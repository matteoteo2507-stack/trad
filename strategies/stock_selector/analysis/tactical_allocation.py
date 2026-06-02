"""MVP Layer 1 v2 — TAA cross-asset (dual-momentum ensemble + vol-targeting + overlay macro).

Implementa il design v2 mergiato dalla review a 5 agent:
- timer: dual-momentum (absolute vs cash) cross-asset, ENSEMBLE di lookback {3,6,12m} VOTATO
- sizing: vol-targeting continuo (no on/off, no pesi quadrante)
- overlay macro: risk-scaler continuo da credit spread (HY OAS) + yield curve, normalizzati
  su finestra ESPANSIVA (no look-ahead), laggati 1 mese (lag di pubblicazione)
- costi di turnover espliciti
Tutti i segnali shiftati di 1 mese (decisione a t-1, hold mese t).

Confronto vs baseline (Buy&Hold SPY, 60/40, Faber single-SPY, GEM semplice) con pannello di
metriche incluso ALPHA TIMING-AWARE (Treynor-Mazuy + Henriksson-Merton), come richiesto dalla
review (l'OLS a beta costante gonfia l'intercetta su strategie a beta tempo-variante).

Uso: python -m strategies.stock_selector.analysis.tactical_allocation
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

CACHE = Path(__file__).resolve().parent / "_cache"
RISKY = ["SPY", "EFA", "EEM", "TLT", "GLD"]   # universo di rotazione
SAFE = "AGG"                                   # bond aggregato (fallback risk-off)
LOOKBACKS = [3, 6, 12]                          # mesi (fissati a priori, non tunati)
VOL_TARGET = 0.10                               # 10% annuo
COST_PER_TURN = 0.0010                          # 10 bps per unita' di turnover
VOL_WIN = 6                                     # finestra realized vol per vol-targeting
MACRO_FLOOR = 0.5                               # lo scaler macro riduce, non veta


def load():
    px = pd.read_parquet(CACHE / "taa_prices.parquet")
    mac = pd.read_parquet(CACHE / "taa_macro.parquet")
    df = px.dropna()                            # da quando tutti gli ETF esistono (2004-12)
    mac = mac.reindex(px.index).ffill()
    rets = px.pct_change()
    tbill_m = (mac["tbill3m"] / 100.0) / 12.0   # rendimento cash mensile
    return df, px, rets, mac, tbill_m


def momentum_score(px: pd.Series, t_idx: int, tbill_cum: dict) -> float:
    """Voto ensemble: frazione di lookback in cui l'asset batte il cash (absolute momentum)."""
    votes = []
    for L in LOOKBACKS:
        if t_idx - L < 0:
            continue
        asset_ret = px.iloc[t_idx] / px.iloc[t_idx - L] - 1.0
        votes.append(1.0 if asset_ret > tbill_cum[L] else 0.0)
    return float(np.mean(votes)) if votes else 0.0


def macro_scaler(mac: pd.DataFrame, dates) -> pd.Series:
    """Scaler continuo in [MACRO_FLOOR, 1] da credit spread + curva, percentili ESPANSIVI."""
    oas = mac["hy_oas"]
    curve = mac["curve"]
    # percentile espansivo (solo passato) dell'OAS: alto = stress -> riduci
    oas_pct = oas.expanding(min_periods=24).apply(lambda x: (x.iloc[-1] >= x).mean(), raw=False)
    credit_factor = 1.0 - oas_pct.clip(0, 1)                       # OAS alto -> ~0
    curve_factor = (curve > 0).astype(float).rolling(1).mean()      # curva invertita -> 0
    # combinazione: media, poi rimappata in [floor,1]
    raw = 0.5 * credit_factor + 0.5 * curve_factor
    scaler = MACRO_FLOOR + (1 - MACRO_FLOOR) * raw
    return scaler.reindex(dates).fillna(1.0)


def run_v2(df, px, rets, mac, tbill_m, use_macro=True, use_voltarget=True):
    dates = df.index
    macro_s = macro_scaler(mac, dates).shift(1).fillna(1.0)
    weights = pd.DataFrame(0.0, index=dates, columns=RISKY + [SAFE, "CASH"])
    for i in range(len(dates)):
        if i < max(LOOKBACKS) + 1:
            weights.iloc[i, weights.columns.get_loc("CASH")] = 1.0
            continue
        tdec = i - 1  # decisione a t-1 (no look-ahead)
        tbill_cum = {L: (1 + tbill_m.iloc[tdec - L + 1: tdec + 1]).prod() - 1
                     for L in LOOKBACKS if tdec - L >= 0}
        scores = {a: momentum_score(px[a], tdec, tbill_cum) for a in RISKY}
        tot = sum(scores.values())
        if tot <= 0:
            # nessun asset batte il cash -> tutto safe bond
            weights.iloc[i, weights.columns.get_loc(SAFE)] = 1.0
            continue
        w_raw = {a: scores[a] / tot for a in RISKY}
        # vol-targeting: realized vol del basket (pesi correnti su returns trailing)
        if use_voltarget:
            basket = sum(w_raw[a] * rets[a] for a in RISKY)
            rv = basket.iloc[tdec - VOL_WIN + 1: tdec + 1].std() * np.sqrt(12)
            s_vol = min(1.0, VOL_TARGET / rv) if rv and rv > 0 else 1.0
        else:
            s_vol = 1.0
        gross = s_vol * (macro_s.iloc[i] if use_macro else 1.0)
        gross = float(np.clip(gross, 0, 1))
        for a in RISKY:
            weights.iloc[i, weights.columns.get_loc(a)] = w_raw[a] * gross
        weights.iloc[i, weights.columns.get_loc("CASH")] = 1.0 - gross
    return weights


def weights_to_returns(weights, rets, tbill_m):
    asset_rets = rets.reindex(index=weights.index, columns=RISKY + [SAFE]).fillna(0.0)
    cash = tbill_m.reindex(weights.index).fillna(0.0)
    port = (weights[RISKY + [SAFE]] * asset_rets).sum(axis=1) + weights["CASH"] * cash
    turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
    return (port - turnover * COST_PER_TURN).reindex(weights.index), turnover


# ---- baseline ----
def faber_spy(px, rets, tbill_m):
    sma = px["SPY"].rolling(10).mean()
    sig = (px["SPY"] > sma).astype(float).shift(1).fillna(1.0)
    return rets["SPY"].fillna(0) * sig + tbill_m * (1 - sig)


def sixty_forty(rets, tbill_m):
    return 0.6 * rets["SPY"].fillna(0) + 0.4 * rets[SAFE].fillna(0)


def gem_simple(px, rets, tbill_m):
    """GEM 12m: tra SPY/EFA il migliore se batte cash, else AGG."""
    out = pd.Series(0.0, index=px.index)
    for i in range(13, len(px.index)):
        td = i - 1
        cash12 = (1 + tbill_m.iloc[td - 11: td + 1]).prod() - 1
        m = {a: px[a].iloc[td] / px[a].iloc[td - 12] - 1 for a in ["SPY", "EFA"]}
        best = max(m, key=m.get)
        held = best if m[best] > cash12 else SAFE
        out.iloc[i] = rets[held].iloc[i] if not np.isnan(rets[held].iloc[i]) else 0.0
    return out


# ---- metriche ----
def metrics(r, mkt, rf, turnover=None):
    s = r.dropna()
    n = len(s)
    cagr = (1 + s).prod() ** (12 / n) - 1
    vol = s.std() * np.sqrt(12)
    excess = s - rf.reindex(s.index)
    sharpe = (excess.mean() * 12) / vol if vol else np.nan
    cum = (1 + s).cumprod()
    maxdd = (cum / cum.cummax() - 1).min()
    m = mkt.reindex(s.index); up = m > 0; dn = m <= 0
    up_cap = s[up].mean() / m[up].mean() if m[up].mean() else np.nan
    dn_cap = s[dn].mean() / m[dn].mean() if m[dn].mean() else np.nan
    pos_dn = (s[dn] > 0).mean()
    # Treynor-Mazuy: excess_s = a + b*xm + g*xm^2 ; g>0 = timing
    xm = (m - rf.reindex(s.index)).reindex(excess.index)
    tm = sm.OLS(excess, sm.add_constant(pd.DataFrame({"xm": xm, "xm2": xm**2})), missing="drop").fit()
    a_tm, a_tm_t, gamma = tm.params["const"]*12, tm.tvalues["const"], tm.params["xm2"]
    # Henriksson-Merton: excess_s = a + b*xm + c*max(0,xm)
    hm = sm.OLS(excess, sm.add_constant(pd.DataFrame({"xm": xm, "down": np.maximum(0, xm)})), missing="drop").fit()
    a_hm_t = hm.tvalues["const"]
    turn = turnover.mean()*12 if turnover is not None else np.nan
    return dict(cagr=cagr, vol=vol, sharpe=sharpe, maxdd=maxdd, up=up_cap, dn=dn_cap,
                pos_dn=pos_dn, a_tm=a_tm, a_tm_t=a_tm_t, gamma=gamma, a_hm_t=a_hm_t, turn=turn)


def main():
    df, px, rets, mac, tbill_m = load()
    start = df.index[0]
    print(f"Universo: {RISKY} + {SAFE} | {start.date()} -> {df.index[-1].date()} ({len(df)} mesi)")
    mkt = rets["SPY"].reindex(df.index)
    rf = tbill_m.reindex(df.index)

    w_v2 = run_v2(df, px, rets, mac, tbill_m, use_macro=True, use_voltarget=True)
    r_v2, turn_v2 = weights_to_returns(w_v2, rets, tbill_m)
    w_nomac = run_v2(df, px, rets, mac, tbill_m, use_macro=False, use_voltarget=True)
    r_nomac, turn_nm = weights_to_returns(w_nomac, rets, tbill_m)

    series = {
        "Buy&Hold SPY": mkt,
        "60/40": sixty_forty(rets, tbill_m),
        "Faber SPY": faber_spy(px, rets, tbill_m),
        "GEM 12m": gem_simple(px, rets, tbill_m),
        "v2 noMacro": r_nomac,
        "v2 FULL": r_v2,
    }
    turns = {"v2 noMacro": turn_nm, "v2 FULL": turn_v2}

    print(f"\n{'strategia':<14}{'CAGR':>7}{'vol':>6}{'Shrp':>6}{'maxDD':>8}{'upC':>6}{'dnC':>6}"
          f"{'+gu%':>6}{'aTM':>7}{'aTM_t':>6}{'gamma':>7}{'aHM_t':>6}{'turn':>6}")
    for name, r in series.items():
        p = metrics(r.reindex(df.index), mkt, rf, turns.get(name))
        turn_s = f"{p['turn']:>5.1f}" if not np.isnan(p['turn']) else "   - "
        print(f"{name:<14}{p['cagr']:>+7.1%}{p['vol']:>6.1%}{p['sharpe']:>+6.2f}{p['maxdd']:>+8.1%}"
              f"{p['up']:>6.0%}{p['dn']:>6.0%}{p['pos_dn']:>6.0%}{p['a_tm']:>+7.1%}{p['a_tm_t']:>+6.2f}"
              f"{p['gamma']:>+7.2f}{p['a_hm_t']:>+6.2f}{turn_s:>6}")
    print("\naTM/aHM_t = alpha timing-aware (Treynor-Mazuy/Henriksson-Merton); t>2 significativo.")
    print("gamma>0 = market-timing skill. upC alto + dnC basso = asimmetria. turn = turnover annuo.")

    # split OOS (prima meta' / seconda meta') per stabilita'
    mid = df.index[len(df)//2]
    print(f"\n-- Stabilita' v2 FULL: 1a meta' (<{mid.date()}) vs 2a meta' --")
    for lbl, sl in [("1a", df.index < mid), ("2a", df.index >= mid)]:
        p = metrics(r_v2[sl], mkt[sl], rf[sl])
        print(f"  {lbl}: CAGR {p['cagr']:+.1%}  Sharpe {p['sharpe']:+.2f}  maxDD {p['maxdd']:+.1%}  "
              f"upC {p['up']:.0%}  dnC {p['dn']:.0%}  aTM_t {p['a_tm_t']:+.2f}")


if __name__ == "__main__":
    main()
