"""Backtest point-in-time del segnale momentum/RRG dello Stock Selector su ~12 anni
di SP500, con attribuzione condizionata al regime dell'indice (core.regime).

Obiettivo (Step 2): cercare con evidenza multi-regime se i segnali price-based del
selettore hanno edge cross-sezionale e SE quell'edge e' regime-conditional — la
domanda che i 4 snapshot live non potevano risolvere.

NON include lo score fondamentale (non backtestabile point-in-time senza DB PIT).
Survivorship: costituenti SP500 attuali (bias noto, flaggato).

Uso: python -m strategies.stock_selector.analysis.backtest
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import spearmanr

from core.regime import regime_timeline

CACHE = Path(__file__).resolve().parent / "_cache"

# Parametri segnale (allineati a config.yaml dove possibile)
RS_MEAN_WINDOW = 50      # rrg.rs_window
RS_STD_WINDOW = 252      # trailing (PIT) al posto di rs.std() globale del tool live
MOM_LOOKBACK = 10        # rrg.momentum_lookback
FWD_DAYS = 21            # forward return ~1 mese
MOM_12_1_LONG = 252      # momentum 12-1 classico
MOM_12_1_SKIP = 21


def load_prices() -> pd.DataFrame:
    return pd.read_parquet(CACHE / "hist_prices.parquet")


def gspc_regime() -> pd.DataFrame:
    """Timeline regime dell'indice ^GSPC (serve OHLC -> download dedicato)."""
    df = yf.download("^GSPC", start="2012-06-01", end="2026-06-02",
                     auto_adjust=False, progress=False)
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    bars = df[["high", "low", "close"]].dropna()
    return regime_timeline(bars)


def compute_signals(prices: pd.DataFrame, bench: str = "^GSPC") -> dict[str, pd.DataFrame]:
    """Calcola, per ogni titolo e ogni giorno (PIT), i segnali RRG continui.

    Restituisce dict di DataFrame (date x ticker): rs_ratio, rs_momentum, mom_12_1.
    """
    b = prices[bench]
    stocks = [c for c in prices.columns if c not in ("^GSPC", "RSP")]
    px = prices[stocks]

    rs = px.div(b, axis=0)
    rs_mean = rs.rolling(RS_MEAN_WINDOW, min_periods=RS_MEAN_WINDOW).mean()
    rs_std = rs.rolling(RS_STD_WINDOW, min_periods=RS_STD_WINDOW).std()
    rs_ratio = 100 + ((rs - rs_mean) / rs_std) * 10
    rs_momentum = 100 + (rs_ratio - rs_ratio.shift(MOM_LOOKBACK))

    mom_12_1 = px.shift(MOM_12_1_SKIP) / px.shift(MOM_12_1_LONG) - 1.0

    return {"rs_ratio": rs_ratio, "rs_momentum": rs_momentum, "mom_12_1": mom_12_1}


def quadrant(rs_ratio: float, rs_mom: float) -> str:
    if pd.isna(rs_ratio) or pd.isna(rs_mom):
        return "NA"
    if rs_ratio > 100 and rs_mom > 100:
        return "LEADING"
    if rs_ratio > 100 and rs_mom < 100:
        return "WEAKENING"
    if rs_ratio < 100 and rs_mom < 100:
        return "LAGGING"
    return "IMPROVING"


def rebalance_dates(index: pd.DatetimeIndex, start="2014-01-01") -> list[pd.Timestamp]:
    """Month-end trading days da `start`."""
    idx = index[index >= pd.Timestamp(start)]
    s = pd.Series(idx, index=idx)
    return list(s.groupby([idx.year, idx.month]).last().values)


def fwd_returns(prices: pd.DataFrame, dates, stocks) -> pd.DataFrame:
    """Forward FWD_DAYS return per (date, ticker)."""
    px = prices[stocks]
    pos = {d: prices.index.get_loc(d) for d in dates}
    out = {}
    for d in dates:
        i = pos[d]
        j = i + FWD_DAYS
        if j >= len(prices.index):
            continue
        p0 = px.iloc[i]
        p1 = px.iloc[j]
        out[prices.index[i]] = (p1 / p0 - 1.0)
    return pd.DataFrame(out).T  # date x ticker


def main() -> None:
    prices = load_prices()
    stocks = [c for c in prices.columns if c not in ("^GSPC", "RSP")]
    print(f"Universo: {len(stocks)} titoli | {prices.index.min().date()} -> {prices.index.max().date()}")
    print("** SURVIVORSHIP: costituenti SP500 ATTUALI applicati al passato (bias noto) **\n")

    sig = compute_signals(prices)
    reg = gspc_regime()
    dates = [pd.Timestamp(d) for d in rebalance_dates(prices.index)]
    dates = [d for d in dates if d in prices.index]
    fwd = fwd_returns(prices, dates, stocks)
    dates = [d for d in dates if d in fwd.index]
    print(f"Rebalance mensili: {len(dates)} ({dates[0].date()} -> {dates[-1].date()})\n")

    # regime per data di rebalance (asof = ultimo regime noto <= data)
    reg_on_date = reg.reindex(reg.index.union(dates)).ffill().loc[dates]["regime"]

    # ---- 1. IC time series per segnale ----
    signals = ["rs_ratio", "rs_momentum", "mom_12_1"]
    ic_ts = {s: {} for s in signals}
    quad_fwd = {q: [] for q in ["LEADING", "IMPROVING", "WEAKENING", "LAGGING"]}
    quad_fwd_byreg: dict = {}

    for d in dates:
        fr = fwd.loc[d]
        for s in signals:
            sv = sig[s].loc[d] if d in sig[s].index else None
            if sv is None:
                continue
            df = pd.DataFrame({"sig": sv, "fr": fr}).dropna()
            if len(df) > 30:
                ic, _ = spearmanr(df["sig"], df["fr"])
                ic_ts[s][d] = ic
        # quadrante forward
        rr = sig["rs_ratio"].loc[d] if d in sig["rs_ratio"].index else None
        rm = sig["rs_momentum"].loc[d] if d in sig["rs_momentum"].index else None
        if rr is not None and rm is not None:
            quads = pd.Series({t: quadrant(rr.get(t, np.nan), rm.get(t, np.nan)) for t in stocks})
            regime_d = reg_on_date.loc[d]
            for q in quad_fwd:
                m = fr[quads[quads == q].index].dropna().mean()
                if not pd.isna(m):
                    quad_fwd[q].append(m)
                    quad_fwd_byreg.setdefault(regime_d, {q: [] for q in quad_fwd})
                    quad_fwd_byreg[regime_d][q].append(m)

    def ic_stats(d: dict):
        s = pd.Series(d)
        n = len(s)
        mean, std = s.mean(), s.std()
        ir = mean / std if std else np.nan
        t = ir * np.sqrt(n) if not np.isnan(ir) else np.nan
        return mean, std, ir, t, (s > 0).mean(), n

    print("=" * 78)
    print("1. INFORMATION COEFFICIENT — segnale vs forward 1M (12 anni, mensile)")
    print("=" * 78)
    print(f"{'segnale':<12} {'mean IC':>8} {'std':>7} {'IC_IR':>7} {'t-stat':>7} {'%>0':>6} {'N':>4}")
    for s in signals:
        mean, std, ir, t, pos, n = ic_stats(ic_ts[s])
        print(f"{s:<12} {mean:>+8.4f} {std:>7.4f} {ir:>+7.3f} {t:>+7.2f} {pos:>6.0%} {n:>4d}")
    print("  (IC_IR annualizzato ~ IC_IR*sqrt(12); t>2 ~ significativo a 12y)")

    # ---- 2. IC condizionato al regime ----
    print("\n" + "=" * 78)
    print("2. IC del momentum (rs_ratio) CONDIZIONATO al regime ^GSPC")
    print("=" * 78)
    reg_groups: dict = {}
    for d, ic in ic_ts["rs_ratio"].items():
        r = reg_on_date.loc[d]
        reg_groups.setdefault(r, []).append(ic)
    print(f"{'regime':<20} {'mean IC':>8} {'%>0':>6} {'N mesi':>7}")
    for r, lst in sorted(reg_groups.items(), key=lambda x: -len(x[1])):
        s = pd.Series(lst)
        print(f"{r:<20} {s.mean():>+8.4f} {(s>0).mean():>6.0%} {len(s):>7d}")

    # ---- 3. Quadrante RRG: forward return medio ----
    print("\n" + "=" * 78)
    print("3. RRG QUADRANT — forward 1M medio per quadrante (tutti i regimi)")
    print("=" * 78)
    for q in ["LEADING", "IMPROVING", "WEAKENING", "LAGGING"]:
        arr = pd.Series(quad_fwd[q])
        print(f"  {q:<10} mean fwd 1M = {arr.mean():>+.3%}  (su {len(arr)} mesi)")
    lead = pd.Series(quad_fwd["LEADING"]); lag = pd.Series(quad_fwd["LAGGING"])
    n = min(len(lead), len(lag))
    spread = lead.values[:n] - lag.values[:n]
    print(f"  LEADING-LAGGING spread: {spread.mean():>+.3%}/mese  t={spread.mean()/spread.std()*np.sqrt(n):+.2f}")

    # ---- 4. Quadrante x regime ----
    print("\n" + "=" * 78)
    print("4. RRG QUADRANT x REGIME — forward 1M medio (la domanda chiave per H1+H2)")
    print("=" * 78)
    print(f"{'regime':<18} {'LEADING':>9} {'IMPROV':>9} {'WEAKEN':>9} {'LAGGING':>9} {'L-Lag':>8} {'N':>4}")
    for r, qd in sorted(quad_fwd_byreg.items(), key=lambda x: -sum(len(v) for v in x[1].values())):
        means = {q: (np.mean(qd[q]) if qd[q] else np.nan) for q in qd}
        ll = means["LEADING"] - means["LAGGING"]
        nmonths = max(len(v) for v in qd.values())
        print(f"{r:<18} {means['LEADING']:>+9.2%} {means['IMPROVING']:>+9.2%} "
              f"{means['WEAKENING']:>+9.2%} {means['LAGGING']:>+9.2%} {ll:>+8.2%} {nmonths:>4d}")

    # ---- 5. Portafogli a livello aggregato (la prova tangibile) ----
    print("\n" + "=" * 78)
    print("5. PORTAFOGLI mensili equal-weight per quintile di mom_12_1 (vs RSP)")
    print("=" * 78)
    q_rets: dict = {q: [] for q in range(1, 6)}
    topN_rets, rsp_rets = [], []
    rsp = prices["RSP"]
    rpos = {d: prices.index.get_loc(d) for d in dates}
    for d in dates:
        fr = fwd.loc[d]
        sv = sig["mom_12_1"].loc[d] if d in sig["mom_12_1"].index else None
        if sv is None:
            continue
        df = pd.DataFrame({"sig": sv, "fr": fr}).dropna()
        if len(df) < 50:
            continue
        df["q"] = pd.qcut(df["sig"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        for q in range(1, 6):
            q_rets[q].append(df.loc[df["q"] == q, "fr"].mean())
        top = df.nlargest(50, "sig")["fr"].mean()
        topN_rets.append(top)
        i = rpos[d]; j = i + FWD_DAYS
        rsp_rets.append(rsp.iloc[j] / rsp.iloc[i] - 1.0 if j < len(rsp) else np.nan)

    def perf(rets):
        s = pd.Series(rets).dropna()
        ann = (1 + s).prod() ** (12 / len(s)) - 1
        vol = s.std() * np.sqrt(12)
        sharpe = (s.mean() * 12) / vol if vol else np.nan
        cum = (1 + s).cumprod()
        dd = (cum / cum.cummax() - 1).min()
        return ann, vol, sharpe, dd

    print(f"{'portafoglio':<16} {'CAGR':>8} {'vol':>7} {'Sharpe':>7} {'maxDD':>8}")
    for q in range(1, 6):
        a, v, sh, dd = perf(q_rets[q])
        print(f"Q{q} (mom {'basso' if q==1 else 'alto' if q==5 else '  '}){'':<4} {a:>+8.1%} {v:>7.1%} {sh:>+7.2f} {dd:>+8.1%}")
    ls = pd.Series(q_rets[5]).values - pd.Series(q_rets[1]).values
    a, v, sh, dd = perf(ls)
    print(f"{'Q5-Q1 (LS)':<16} {a:>+8.1%} {v:>7.1%} {sh:>+7.2f} {dd:>+8.1%}")
    a, v, sh, dd = perf(topN_rets)
    print(f"{'Top-50 mom':<16} {a:>+8.1%} {v:>7.1%} {sh:>+7.2f} {dd:>+8.1%}")
    a, v, sh, dd = perf(rsp_rets)
    print(f"{'RSP (EW bench)':<16} {a:>+8.1%} {v:>7.1%} {sh:>+7.2f} {dd:>+8.1%}")
    print("  NB survivorship gonfia TUTTE le CAGR long-only; conta il DIFFERENZIALE vs RSP.")

    # ---- 6. DIFENSIVO (low-vol proxy): l'obiettivo asimmetrico dell'utente ----
    # Proxy price-based del tilt 'difensivo/quality+beta<1': quintile a vol piu' bassa.
    # Domanda: partecipa ai rally? resta positivo nei cali dell'indice?
    print("\n" + "=" * 78)
    print("6. DIFENSIVO low-vol vs indice — UP/DOWN capture (obiettivo asimmetrico)")
    print("=" * 78)
    stk = prices[stocks]
    realized_vol = stk.pct_change().rolling(252, min_periods=200).std()  # PIT
    lowvol_rets, highvol_rets = [], []
    for d in dates:
        fr = fwd.loc[d]
        vv = realized_vol.loc[d] if d in realized_vol.index else None
        if vv is None:
            continue
        df = pd.DataFrame({"vol": vv, "fr": fr}).dropna()
        if len(df) < 50:
            continue
        lowvol_rets.append(df.nsmallest(int(len(df)*0.2), "vol")["fr"].mean())
        highvol_rets.append(df.nlargest(int(len(df)*0.2), "vol")["fr"].mean())
    lv = pd.Series(lowvol_rets, index=[d for d in dates if d in realized_vol.index][:len(lowvol_rets)])
    rs = pd.Series(rsp_rets, index=dates[:len(rsp_rets)]).reindex(lv.index)
    up = rs > 0; dn = rs <= 0
    print(f"Mesi indice SU ({up.sum()}): RSP {rs[up].mean():+.2%} | low-vol {lv[up].mean():+.2%} "
          f"-> up-capture {lv[up].mean()/rs[up].mean():.0%}")
    print(f"Mesi indice GIU ({dn.sum()}): RSP {rs[dn].mean():+.2%} | low-vol {lv[dn].mean():+.2%} "
          f"-> down-capture {lv[dn].mean()/rs[dn].mean():.0%}")
    print(f"  Mesi GIU in cui low-vol resta POSITIVO: {(lv[dn] > 0).mean():.0%} "
          f"(obiettivo 'netto positivo mentre indice cala')")
    a, v, sh, dd = perf(lowvol_rets)
    print(f"  Low-vol full: CAGR {a:+.1%} vol {v:.1%} Sharpe {sh:+.2f} maxDD {dd:+.1%}")
    # comportamento nei regimi Bear
    bear = reg_on_date.reindex(lv.index).str.startswith("Bear")
    if bear.sum():
        print(f"  Regime BEAR ({bear.sum()} mesi): RSP {rs[bear].mean():+.2%} | "
              f"low-vol {lv[bear].mean():+.2%} | low-vol positivo {(lv[bear]>0).mean():.0%}")


if __name__ == "__main__":
    main()
