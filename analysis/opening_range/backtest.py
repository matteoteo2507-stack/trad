"""Opening-Range Breakout + retest (US100 M5) — backtester GREZZO (v1). Spec PRE-REGISTRATA
(docs/OPENING_RANGE_PREREGISTRATION.md). Scopo: capire il POTENZIALE (no filtro news).

OR = 09:30-10:00 ET (apertura cash USA, fuso convertito Europe/Bucharest->America/New_York,
DST-safe e verificato dal profilo di volatilità). Break = candela che CHIUDE oltre ORH/ORL;
primo break decide il lato. Poi si attende il break (chiusura) del low/high della candela di
rottura, aggiornando il livello sui wick-senza-chiusura. Entry = SELL/BUY LIMIT sul retest del
livello; SL = estremo opposto della candela di rottura ± BUFFER; TP 1:2; niente BE; hold a TP/SL.
Un solo trade/giorno; pending valido fino alle 16:00 ET. Costi + bound intrabar pess/opt.

Uso: python analysis/opening_range/backtest.py [US100|US500]
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402

DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data")
BUFFER = 6.0          # punti indice sopra/sotto la candela di rottura
RR = 2.0              # TP = RR * rischio (1:2)
SPREAD = 1.5          # costo round-trip in punti (assunzione v1)
OR_START, OR_END = 9 * 60 + 30, 10 * 60      # 09:30-10:00 ET (minuti)
SESS_END = 16 * 60                            # 16:00 ET
MAX_HOLD = 288 * 5    # barre M5 di holding max (~5 giorni)
GAP_THRESH = 0.6      # % gap di apertura oltre cui = giorno "shock" (proxy news)


def _is_nfp(dstr):
    """NFP = primo venerdì del mese (release 8:30 ET, gappa l'apertura). Deterministico."""
    import datetime as _dt
    d = _dt.date.fromisoformat(dstr)
    return d.weekday() == 4 and d.day <= 7


def adx_series(H, L, C, n=14):
    """ADX(14) di Wilder, allineato alle barre (NaN nei primi ~2n). Vettoriale."""
    H, L, C = np.asarray(H, float), np.asarray(L, float), np.asarray(C, float)
    up = H[1:] - H[:-1]
    dn = L[:-1] - L[1:]
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = np.maximum(H[1:] - L[1:], np.maximum(np.abs(H[1:] - C[:-1]), np.abs(L[1:] - C[:-1])))

    def wilder(x):
        s = pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().values
        return s
    atr = wilder(tr)
    pdi = 100.0 * wilder(plus_dm) / np.where(atr == 0, np.nan, atr)
    mdi = 100.0 * wilder(minus_dm) / np.where(atr == 0, np.nan, atr)
    dx = 100.0 * np.abs(pdi - mdi) / np.where((pdi + mdi) == 0, np.nan, pdi + mdi)
    adx = wilder(np.nan_to_num(dx))
    return np.concatenate([[np.nan], adx])   # riallinea (perso 1 bar sul diff)


# fuso del file: broker MT5 = ora server (EET); Dukascopy = UTC
TZMAP = {"US100": "Europe/Bucharest", "US500": "Europe/Bucharest",
         "NAS100": "UTC", "SPX500": "UTC"}


def load(sym):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_M5.csv"), parse_dates=["time"]).set_index("time")
    d = d[~d.index.duplicated(keep="last")].sort_index()
    et = d.index.tz_localize(TZMAP.get(sym, "UTC"), ambiguous="NaT",
                             nonexistent="NaT").tz_convert("America/New_York")
    keep = et.notna()
    d = d[keep]; et = et[keep]
    d["etdate"] = et.strftime("%Y-%m-%d")
    d["etmin"] = et.hour * 60 + et.minute
    d["year"] = et.year
    return d


def run(sym):
    d = load(sym)
    O, H, L, C = d["open"].values, d["high"].values, d["low"].values, d["close"].values
    ADX = adx_series(H, L, C)
    etmin, etdate, year = d["etmin"].values, d["etdate"].values, d["year"].values
    dayrows = defaultdict(list)
    for i, dd in enumerate(etdate):
        dayrows[dd].append(i)

    trades = []
    stats = defaultdict(int)
    prev_close = None
    for dd in sorted(dayrows):
        rows = dayrows[dd]
        orr = [i for i in rows if OR_START <= etmin[i] < OR_END]
        sess = [i for i in rows if OR_END <= etmin[i] < SESS_END]
        # gap di apertura vs chiusura giorno prec (proxy shock/news, look-ahead-safe)
        gap_pct = 0.0
        if orr and prev_close:
            gap_pct = (O[orr[0]] - prev_close) / prev_close * 100
        if rows:
            prev_close = C[rows[-1]]
        nfp = _is_nfp(dd)
        if len(orr) < 3 or len(sess) < 3:
            continue
        stats["days"] += 1
        ORH = max(H[i] for i in orr); ORL = min(L[i] for i in orr)

        side = None
        for k, i in enumerate(sess):
            if C[i] < ORL:
                side, c0k = "SELL", k; break
            if C[i] > ORH:
                side, c0k = "BUY", k; break
        if side is None:
            continue
        stats["break"] += 1
        c0 = sess[c0k]
        level = L[c0] if side == "SELL" else H[c0]
        slref = H[c0] if side == "SELL" else L[c0]

        jbk = None
        for k in range(c0k + 1, len(sess)):
            i = sess[k]
            if side == "SELL":
                if C[i] < level:
                    jbk = k; break
                if L[i] < level:
                    level = L[i]
            else:
                if C[i] > level:
                    jbk = k; break
                if H[i] > level:
                    level = H[i]
        if jbk is None:
            continue
        stats["confirm"] += 1
        entry = level
        if side == "SELL":
            sl = slref + BUFFER; risk = sl - entry; tp = entry - RR * risk
        else:
            sl = slref - BUFFER; risk = entry - sl; tp = entry + RR * risk
        if risk <= 0:
            continue

        # fill sul retest entro la sessione
        f = None
        for k in range(jbk + 1, len(sess)):
            i = sess[k]
            if (side == "SELL" and H[i] >= entry) or (side == "BUY" and L[i] <= entry):
                f = i; break
        if f is None:
            continue
        stats["filled"] += 1

        # risoluzione TP/SL in avanti (anche oltre la sessione), bound intrabar
        o_p = o_o = None; hold = 0
        for j in range(f + 1, min(f + 1 + MAX_HOLD, len(H))):
            hold = j - f
            if side == "SELL":
                hit_sl, hit_tp = H[j] >= sl, L[j] <= tp
            else:
                hit_sl, hit_tp = L[j] <= sl, H[j] >= tp
            if hit_sl and hit_tp:
                o_p, o_o = "SL", "TP"; break
            if hit_sl:
                o_p = o_o = "SL"; break
            if hit_tp:
                o_p = o_o = "TP"; break
        if o_p is None:
            continue  # non risolto entro l'orizzonte
        cR = SPREAD / risk

        def toR(o):
            return (RR - cR) if o == "TP" else (-1.0 - cR)
        trades.append({"date": dd, "year": int(year[f]), "side": side, "risk": risk,
                       "hold": hold, "R_pess": toR(o_p), "R_opt": toR(o_o),
                       "tp_pess": o_p == "TP", "tp_opt": o_o == "TP",
                       "nfp": nfp, "gap_pct": abs(gap_pct),
                       "adx": float(ADX[sess[jbk]]) if np.isfinite(ADX[sess[jbk]]) else 0.0})
    return trades, stats


def report(sym, trades, stats):
    print(f"\n===== {sym} — Opening-Range Breakout (v1 grezza, no news) =====")
    print(f"  giorni validi={stats['days']}  con break={stats['break']}  "
          f"confermati={stats['confirm']}  eseguiti={stats['filled']}  risolti={len(trades)}")
    if not trades:
        print("  nessun trade risolto."); return
    df = pd.DataFrame(trades)
    for tag in ("pess", "opt"):
        R = df[f"R_{tag}"].values
        wr = 100 * df[f"tp_{tag}"].mean()
        pf_num = R[R > 0].sum(); pf_den = -R[R < 0].sum()
        pf = pf_num / pf_den if pf_den else float("inf")
        bca = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95,
                                  n_boot=3000, seed=42)
        print(f"  [{tag}] n={len(df)}  win(TP)%={wr:4.1f}  E[R]={R.mean():+.3f}  "
              f"PF={pf:.2f}  BCa E[R] CI95=[{bca['low']:+.3f},{bca['high']:+.3f}]  "
              f"(lower>0? {'SI' if bca['low']>0 else 'NO'})")
    print(f"  break-even win-rate per 1:2 (dopo costi) ≈ 34%")
    print("  --- FILTRO NEWS (E[R] pess) ---")
    for label, mask in (("tutti", pd.Series(True, index=df.index)),
                        ("no NFP", ~df["nfp"]),
                        (f"no NFP & no gap>{GAP_THRESH}%", ~df["nfp"] & (df["gap_pct"] <= GAP_THRESH))):
        g = df[mask]
        if len(g) < 30:
            print(f"    {label:26} n={len(g)} (troppo pochi)"); continue
        R = g["R_pess"].values
        bca = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95, n_boot=2000, seed=42)
        print(f"    {label:26} n={len(g):4}  win%={100*g['tp_pess'].mean():4.1f}  "
              f"E[R]={R.mean():+.3f}  BCa CI=[{bca['low']:+.3f},{bca['high']:+.3f}]"
              f"{'  <-- lower>0' if bca['low']>0 else ''}")
    print("  --- FILTRO VOLATILITA' ADX(14)@conferma (E[R] pess) ---")

    def _stat(g):
        if len(g) < 30:
            return f"n={len(g):4} (pochi)"
        R = g["R_pess"].values
        b = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95, n_boot=1500, seed=42)
        flag = " *" if b["low"] > 0 else ""
        return f"n={len(g):4} win%={100*g['tp_pess'].mean():4.1f} E[R]={R.mean():+.3f} CI=[{b['low']:+.3f},{b['high']:+.3f}]{flag}"
    news_ok = ~df["nfp"] & (df["gap_pct"] <= GAP_THRESH)
    for thr in (0, 20, 25, 30, 35):
        sub = df[df["adx"] >= thr]
        print(f"    ADX>={thr:2d}  | tutti:  {_stat(sub)}")
        print(f"             | no-news:{_stat(sub[news_ok.loc[sub.index]])}")
    print(f"  distribuzione ADX@conferma: mediana={df['adx'].median():.0f} "
          f"q25={df['adx'].quantile(.25):.0f} q75={df['adx'].quantile(.75):.0f}")
    print(f"  hold mediano={int(df['hold'].median())} barre M5 ({int(df['hold'].median())*5} min)  "
          f"| side: BUY={int((df.side=='BUY').sum())} SELL={int((df.side=='SELL').sum())}")
    print("  E[R] pess per anno:")
    for y, g in df.groupby("year"):
        print(f"    {y}: n={len(g):3}  win%={100*g['tp_pess'].mean():4.1f}  E[R]={g['R_pess'].mean():+.3f}")
    print("  E[R] pess per LATO (alpha vs beta del bull?):")
    for s, g in df.groupby("side"):
        print(f"    {s:4}: n={len(g):3}  win%={100*g['tp_pess'].mean():4.1f}  E[R]={g['R_pess'].mean():+.3f}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    sym = sys.argv[1] if len(sys.argv) > 1 else "US100"
    trades, stats = run(sym)
    report(sym, trades, stats)


if __name__ == "__main__":
    main()
