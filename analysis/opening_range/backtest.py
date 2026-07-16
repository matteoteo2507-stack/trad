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


def load(sym):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_M5.csv"), parse_dates=["time"]).set_index("time")
    d = d[~d.index.duplicated(keep="last")].sort_index()
    et = d.index.tz_localize("Europe/Bucharest", ambiguous="NaT", nonexistent="NaT").tz_convert("America/New_York")
    keep = et.notna()
    d = d[keep]; et = et[keep]
    d["etdate"] = et.strftime("%Y-%m-%d")
    d["etmin"] = et.hour * 60 + et.minute
    d["year"] = et.year
    return d


def run(sym):
    d = load(sym)
    H, L, C = d["high"].values, d["low"].values, d["close"].values
    etmin, etdate, year = d["etmin"].values, d["etdate"].values, d["year"].values
    dayrows = defaultdict(list)
    for i, dd in enumerate(etdate):
        dayrows[dd].append(i)

    trades = []
    stats = defaultdict(int)
    for dd, rows in dayrows.items():
        orr = [i for i in rows if OR_START <= etmin[i] < OR_END]
        sess = [i for i in rows if OR_END <= etmin[i] < SESS_END]
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
                       "tp_pess": o_p == "TP", "tp_opt": o_o == "TP"})
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
