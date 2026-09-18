"""ORB v2 (US indici, M5) — nuove meccaniche (idea utente+socio), TESTATO CON PALETTI.

Rispetto alla v1: SL ancorato all'OR (SELL=ORL+10, BUY=ORH-10), RR 1:3 dallo SL, BE a +2R,
pending expiry 12:00 ET (18:00 Roma), filtro volatilità ADX, niente parziali. Entry = retest del
L trailato (invariato). Rischio 1% = neutro in R (ogni trade +3R/-1R/BE). Validazione: curva ADX +
news + HOLDOUT temporale (train 2012-2019 / test 2020-2026) + DSR, su NAS100 E SPX500.

Uso: python analysis/opening_range/backtest_v2.py [ADX_MIN]
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
from backtest import (GAP_THRESH, OR_END, OR_START, _is_nfp,  # noqa: E402
                      adx_series, load)

BUFFER2 = 10.0        # punti: SL = ORL+10 (sell) / ORH-10 (buy)
RR2 = 3.0             # TP = 3*rischio (1:3 dallo SL)
BE_AT = 2.0           # a +2R sposta SL a breakeven
EXPIRY_ET = 12 * 60   # 12:00 ET (18:00 Roma): scadenza del pending
SPREAD = 1.5
MAX_HOLD = 288 * 5
ADX_MIN_DEFAULT = 25


def _resolve(H, L, f, side, entry, sl0, tp, be_trig, tie):
    """R (prima dei costi) o None. tie='pess'|'opt' per l'ordine intrabar."""
    be = False
    sl = sl0
    for j in range(f + 1, min(f + 1 + MAX_HOLD, len(H))):
        hi, lo = H[j], L[j]
        if side == "SELL":
            hit_tp = lo <= tp
            hit_sl = hi >= sl
            if not be:
                hit_be = lo <= be_trig
                if hit_sl and hit_tp:
                    return RR2 if tie == "opt" else -1.0
                if hit_sl:
                    if hit_be and tie == "opt":
                        be = True; sl = entry; continue
                    return -1.0
                if hit_tp:
                    return RR2
                if hit_be:
                    be = True; sl = entry; continue
            else:
                if hit_sl and hit_tp:
                    return RR2 if tie == "opt" else 0.0
                if hit_sl:
                    return 0.0
                if hit_tp:
                    return RR2
        else:  # BUY
            hit_tp = hi >= tp
            hit_sl = lo <= sl
            if not be:
                hit_be = hi >= be_trig
                if hit_sl and hit_tp:
                    return RR2 if tie == "opt" else -1.0
                if hit_sl:
                    if hit_be and tie == "opt":
                        be = True; sl = entry; continue
                    return -1.0
                if hit_tp:
                    return RR2
                if hit_be:
                    be = True; sl = entry; continue
            else:
                if hit_sl and hit_tp:
                    return RR2 if tie == "opt" else 0.0
                if hit_sl:
                    return 0.0
                if hit_tp:
                    return RR2
    return None


def run(sym):
    d = load(sym)
    O, H, L, C = (d["open"].values, d["high"].values, d["low"].values, d["close"].values)
    ADX = adx_series(H, L, C)
    etmin, etdate, year = d["etmin"].values, d["etdate"].values, d["year"].values
    dayrows = defaultdict(list)
    for i, dd in enumerate(etdate):
        dayrows[dd].append(i)

    trades = []
    prev_close = None
    for dd in sorted(dayrows):
        rows = dayrows[dd]
        orr = [i for i in rows if OR_START <= etmin[i] < OR_END]
        sess = [i for i in rows if OR_END <= etmin[i] < EXPIRY_ET]   # finestra 10:00-12:00 ET
        gap_pct = (O[orr[0]] - prev_close) / prev_close * 100 if (orr and prev_close) else 0.0
        if rows:
            prev_close = C[rows[-1]]
        nfp = _is_nfp(dd)
        if len(orr) < 3 or len(sess) < 3:
            continue
        ORH = max(H[i] for i in orr); ORL = min(L[i] for i in orr)

        side = None
        for k, i in enumerate(sess):
            if C[i] < ORL:
                side, c0k = "SELL", k; break
            if C[i] > ORH:
                side, c0k = "BUY", k; break
        if side is None:
            continue
        level = L[sess[c0k]] if side == "SELL" else H[sess[c0k]]
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
        entry = level
        if side == "SELL":
            sl0 = ORL + BUFFER2; risk = sl0 - entry
            tp = entry - RR2 * risk; be_trig = entry - BE_AT * risk
        else:
            sl0 = ORH - BUFFER2; risk = entry - sl0
            tp = entry + RR2 * risk; be_trig = entry + BE_AT * risk
        if risk <= 0:
            continue

        f = None
        for k in range(jbk + 1, len(sess)):
            i = sess[k]
            if (side == "SELL" and H[i] >= entry) or (side == "BUY" and L[i] <= entry):
                f = i; break
        if f is None:
            continue
        cR = SPREAD / risk
        rp = _resolve(H, L, f, side, entry, sl0, tp, be_trig, "pess")
        ro = _resolve(H, L, f, side, entry, sl0, tp, be_trig, "opt")
        if rp is None:
            continue
        adxv = float(ADX[sess[jbk]]) if np.isfinite(ADX[sess[jbk]]) else 0.0
        trades.append({"year": int(year[f]), "side": side, "risk": risk,
                       "R_pess": rp - cR,
                       # A5 (2026-09-18): era `else 0.0`, cioe' un timeout sotto la
                       # convenzione ottimistica veniva contato come pareggio invece che
                       # scartato. Colonna mai usata nel verdetto, quindi il NO-GO non ne
                       # risente -- ma ora la usiamo, e va pulita.
                       "R_opt": (ro - cR) if ro is not None else float("nan"),
                       "win": rp > 0, "nfp": nfp, "gap": abs(gap_pct), "adx": adxv})
    return pd.DataFrame(trades)


def _stat(g):
    if len(g) < 25:
        return f"n={len(g):4} (pochi)"
    R = g["R_pess"].values
    b = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95, n_boot=1500, seed=42)
    return (f"n={len(g):4} win%={100*g['win'].mean():4.1f} E[R]={R.mean():+.3f} "
            f"CI=[{b['low']:+.3f},{b['high']:+.3f}]{'  *' if b['low']>0 else ''}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    adx_min = float(sys.argv[1]) if len(sys.argv) > 1 else ADX_MIN_DEFAULT
    print(f"ORB v2 (SL su OR+10, RR 1:3, BE a 2R, expiry 12:00 ET). ADX primario ≥ {adx_min:.0f}\n")
    for sym in ("NAS100", "SPX500"):
        df = run(sym)
        print(f"===== {sym} (n totale eseguiti={len(df)}) =====")
        print("  curva ADX (E[R] pess, tutto il periodo):")
        for thr in (0, 20, 25, 30):
            print(f"    ADX>={thr:2d}  {_stat(df[df['adx'] >= thr])}")
        prim = df[df["adx"] >= adx_min]
        news_ok = ~prim["nfp"] & (prim["gap"] <= GAP_THRESH)
        print(f"  PRIMARIO ADX>={adx_min:.0f}:")
        print(f"    tutti     {_stat(prim)}")
        print(f"    no-news   {_stat(prim[news_ok])}")
        print(f"    TRAIN '12-'19  {_stat(prim[prim['year'] <= 2019])}")
        print(f"    TEST  '20-'26  {_stat(prim[prim['year'] >= 2020])}")
        R = prim["R_pess"].values
        if len(R) >= 25:
            dsr = qm.deflated_sharpe_ratio(R, n_trials=4, periods_per_year=252)
            print(f"    DSR(trial=4 soglie): dsr={dsr['dsr']:.3f} sig95={dsr['significant_95']}")
        print()


if __name__ == "__main__":
    main()
