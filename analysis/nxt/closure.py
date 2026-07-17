"""NXT — chiusura definitiva: testa l'ipotesi 'stop dentro il rumore' (2026-07-17b).

La primaria (continuazione, entry 0.5, SL 0.786, 1:3) e' NO-GO (backtest.py: win 13%, E[R]=-0.44).
Diagnosi: lo stop a 0.786 vive DENTRO il rumore del ritracciamento. Due implicazioni testabili,
PRE-REGISTRATE qui (regole immutabili, verdetto su holdout + per-anno + per-asset):

  FAM. A — FADE (lato opposto):
    A1  mirror-fade 1:3       : stessa entrata/fill a 0.5, posizione INVERTITA, risk 0.286, TP 3R.
  FAM. B — CONTINUAZIONE con stop FUORI dal rumore (test diretto della diagnosi):
    B1  entry 0.5 , SL oltre origine (lo-0.10*rng), TP 1:1
    B2  entry 0.5 , SL oltre origine,               TP 1:2
    B3  entry 0.786 (deep), SL oltre origine,       TP 1:2

Multiple-testing: 4 config -> scetticismo esplicito. Una config 'positiva' non e' un GO:
va ri-pre-registrata da zero. Riusa leg-detection look-ahead-safe di backtest.py.

Uso: python analysis/nxt/closure.py
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from core import quant_metrics as qm  # noqa: E402
import backtest as bt  # noqa: E402  (riusa load_h1, atr, zigzag, build_legs, SPREAD, K, FILL_WINDOW, MAX_HOLD)

BE_AT = 2.0
ORIGIN_BUF = 0.10   # buffer oltre l'origine della gamba (in frazione di ampiezza)


def sim(leg, H, L, sym, mode, cost_mult=1.0):
    """Simula una config. mode in {'A1','B1','B2','B3'}. Ritorna dict o None.

    cost_mult: stress su spread+slippage (1=base, 2/3 = frizione crescente). Rischi piccoli
    (~0.286 ATR) rendono la frizione dominante: la sensibilita' e' il test di robustezza chiave.
    Geometria (BUY-leg = uptrend: lo=origine, hi=fine; retrace misurato da hi verso il basso).
    """
    side, hi, lo, rng, b, cb = (leg["side"], leg["hi"], leg["lo"], leg["rng"],
                                leg["end_idx"], leg["conf"])
    buy_leg = (side == "BUY")

    # livello di ingresso (fill quando il prezzo ritraccia fino a qui, da cb in poi)
    if mode in ("A1", "B1", "B2"):
        efib = 0.5
    else:  # B3
        efib = 0.786
    entry = (hi - efib * rng) if buy_leg else (lo + efib * rng)

    # posizione + SL + TP secondo la config
    if mode == "A1":
        # FADE: posizione invertita rispetto al trend, mirror 1:3, risk 0.286*rng
        pos_long = not buy_leg
        risk = 0.286 * rng
        if pos_long:
            sl = entry - risk; tp = entry + 3.0 * risk
        else:
            sl = entry + risk; tp = entry - 3.0 * risk
    else:
        # CONTINUAZIONE con SL oltre l'origine della gamba
        pos_long = buy_leg
        if pos_long:
            sl = lo - ORIGIN_BUF * rng
        else:
            sl = hi + ORIGIN_BUF * rng
        risk = abs(entry - sl)
        rr = 1.0 if mode == "B1" else 2.0
        tp = entry + rr * risk if pos_long else entry - rr * risk
    if risk <= 0:
        return None
    be = entry + BE_AT * risk if pos_long else entry - BE_AT * risk

    # fill del limit da cb in poi, entro FILL_WINDOW dallo swing di fine (look-ahead-safe)
    f = None
    for j in range(max(cb, b + 1), min(b + 1 + bt.FILL_WINDOW, len(H))):
        touched = (L[j] <= entry) if buy_leg else (H[j] >= entry)  # ritraccia fino all'entry
        if touched:
            f = j; break
    if f is None:
        return None

    def resolve(pess):
        be_on = False; sl_cur = sl
        for j in range(f, min(f + bt.MAX_HOLD, len(H))):
            if pos_long:
                if not be_on and H[j] >= be:
                    be_on = True; sl_cur = entry
                hit_sl = L[j] <= sl_cur; hit_tp = H[j] >= tp
            else:
                if not be_on and L[j] <= be:
                    be_on = True; sl_cur = entry
                hit_sl = H[j] >= sl_cur; hit_tp = L[j] <= tp
            if hit_sl and hit_tp:
                return ("SL" if pess else "TP"), be_on, j - f
            if hit_sl:
                return "SL", be_on, j - f
            if hit_tp:
                return "TP", be_on, j - f
        return None, be_on, bt.MAX_HOLD

    rr_win = abs(tp - entry) / risk  # multiplo R del target
    cost_R = bt.SPREAD.get(sym, 0.0) * cost_mult / risk
    out = {"entry_idx": f, "legid": f"{sym}:{b}", "asset": sym}
    for tag, pess in (("pess", True), ("opt", False)):
        o, be_on, _ = resolve(pess)
        if o is None:
            return None
        if o == "TP":
            r = rr_win - cost_R
        elif be_on:
            r = 0.0 - cost_R
        else:
            r = -1.0 - cost_R
        out[f"R_{tag}"] = r
        out[f"tp_{tag}"] = (o == "TP")
    return out


def run():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    modes = ["A1", "B1", "B2", "B3"]
    names = {"A1": "FADE mirror 1:3", "B1": "cont 0.5 SLorigin 1:1",
             "B2": "cont 0.5 SLorigin 1:2", "B3": "cont 0.786 SLorigin 1:2"}
    rec = {m: [] for m in modes}
    for sym in bt.ASSETS:
        try:
            d = bt.load_h1(sym)
        except FileNotFoundError:
            continue
        H, L, C = d["high"].values, d["low"].values, d["close"].values
        yrs = d["time"].dt.year.values
        A = bt.atr(H, L, C)
        legs = bt.build_legs(bt.zigzag(H, L), A)
        for lg in legs:
            for m in modes:
                t = sim(lg, H, L, sym, m)
                if t is not None:
                    t["year"] = int(yrs[t["entry_idx"]])
                    rec[m].append(t)

    print("=" * 82)
    print("NXT — CHIUSURA: test dell'ipotesi 'stop dentro il rumore' (pool 6 asset H1 ~14y)")
    print("  break-even: 1:1 -> 50% | 1:2 -> 33.3% | 1:3 -> 25%   (PESSIMISTICO, dopo costi)")
    print("  ** 4 config = multiple testing: una 'positiva' NON e' un GO (ri-pre-registrare) **")
    print("=" * 82)
    import pandas as pd
    for m in modes:
        df = pd.DataFrame(rec[m])
        if len(df) < 20:
            print(f"\n[{m}] {names[m]:26} n={len(df)} (pochi)"); continue
        R = df["R_pess"].values
        bca = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95,
                                  n_boot=3000, seed=42)
        wr = 100 * df["tp_pess"].mean()
        flag = "  <== lower-bound > 0 !" if bca["low"] > 0 else ""
        print(f"\n[{m}] {names[m]:26} n={len(df):5}  win%={wr:4.1f}  "
              f"E[R]={R.mean():+.3f}  BCa=[{bca['low']:+.3f},{bca['high']:+.3f}]{flag}")
        # holdout + per-anno solo se il punto non e' chiaramente negativo
        if bca["high"] > 0:
            cut = df.groupby("asset")["entry_idx"].transform(lambda s: s.quantile(0.70))
            tr, te = df[df["entry_idx"] <= cut], df[df["entry_idx"] > cut]
            for lbl, gsub in (("TRAIN", tr), ("TEST ", te)):
                if len(gsub) >= 20:
                    b2 = qm.bca_bootstrap_ci(gsub["R_pess"].values,
                                             metric=lambda x: float(np.mean(x)), conf=0.95,
                                             n_boot=2000, seed=42)
                    print(f"        {lbl}: n={len(gsub):5} E[R]={gsub['R_pess'].mean():+.3f} "
                          f"BCa=[{b2['low']:+.3f},{b2['high']:+.3f}]")
            print("        per-anno E[R]: " + "  ".join(
                f"{y}:{gy['R_pess'].mean():+.2f}" for y, gy in df.groupby("year")))
        # per-asset compatto
        pa = " ".join(f"{s}:{gg['R_pess'].mean():+.2f}" for s, gg in df.groupby("asset"))
        print(f"        per-asset E[R]: {pa}")

    # ---- stress su A1: sensibilita' a costi/slippage (rischi minuscoli -> frizione domina) ----
    print("\n" + "=" * 82)
    print("STRESS A1 (fade): sensibilita' a costi/slippage — 1x=base, 2x, 3x spread")
    print("  (rischio ~0.286 ATR: se l'edge muore raddoppiando i costi, e' fragile all'esecuzione)")
    print("=" * 82)
    import pandas as pd
    for cm in (1.0, 2.0, 3.0):
        rows = []
        cr_list = []
        for sym in bt.ASSETS:
            try:
                d = bt.load_h1(sym)
            except FileNotFoundError:
                continue
            H, L = d["high"].values, d["low"].values
            A = bt.atr(H, L, d["close"].values)
            for lg in bt.build_legs(bt.zigzag(H, L), A):
                t = sim(lg, H, L, sym, "A1", cost_mult=cm)
                if t is not None:
                    rows.append(t)
                    cr_list.append(bt.SPREAD.get(sym, 0.0) * cm / (0.286 * lg["rng"]))
        df = pd.DataFrame(rows)
        R = df["R_pess"].values
        bca = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95,
                                  n_boot=3000, seed=42)
        flag = "  <== ancora > 0" if bca["low"] > 0 else "  <== CROLLA sotto/attorno a 0"
        print(f"  costi {cm:.0f}x  n={len(df):5}  win%={100*df['tp_pess'].mean():4.1f}  "
              f"E[R]={R.mean():+.3f}  BCa=[{bca['low']:+.3f},{bca['high']:+.3f}]  "
              f"cost_R medio={np.mean(cr_list):.3f}{flag}")


if __name__ == "__main__":
    run()
