"""NXT/FADE — diagnostica del rischio WEEKEND (mai misurato finora).

NON e' una variante di strategia: e' una misura di (a) quanto il backtest esistente sia
ottimista sui fill e (b) come si comportano davvero i gap del fine settimana. Per
STRATEGY_LIFECYCLE §3 la modellazione piu' realistica dell'esecuzione non consuma trial.

Tre domande:
  D1  Quanti trade attraversano un weekend, e quanto ci sta dentro?
  D2  I gap del weekend sono AVVERSI o simmetrici? (misurati in R, con il segno della posizione)
  D3  Quanti stop vengono saltati dal gap? Il backtest registra esattamente -1R, ma se il
      lunedi' apre gia' oltre lo stop il fill vero e' PEGGIO. Quanto costa davvero?

E, in forma puramente DESCRITTIVA (non e' una regola, non e' un test): quanto contributo
di gap va alle posizioni che il venerdi' erano in PROFITTO contro quelle in PERDITA.
Serve a valutare la regola manuale dell'utente "venerdi' chiudo i profit e lascio i loss".

Uso: python analysis/nxt/weekend.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import backtest as bt  # noqa: E402

BE_AT = 2.0
RR = 3.0


def fade_trades(sym):
    """Riproduce la config A1 (FADE) e strumenta il cammino per il weekend."""
    d = bt.load_h1(sym)
    O, H, L, C = (d[c].values.astype(float) for c in ("open", "high", "low", "close"))
    t = pd.DatetimeIndex(d["time"])
    dow = t.dayofweek.values
    A = bt.atr(H, L, C)
    legs = bt.build_legs(bt.zigzag(H, L), A)
    spread = bt.SPREAD.get(sym, 0.0)

    rows, gaps = [], []
    for lg in legs:
        side, hi, lo, rng = lg["side"], lg["hi"], lg["lo"], lg["rng"]
        b, cb = lg["end_idx"], lg["conf"]
        buy_leg = (side == "BUY")
        entry = (hi - 0.5 * rng) if buy_leg else (lo + 0.5 * rng)
        pos_long = not buy_leg                      # FADE = posizione invertita
        risk = 0.286 * rng
        if risk <= 0:
            continue
        sl = entry - risk if pos_long else entry + risk
        tp = entry + RR * risk if pos_long else entry - RR * risk
        be = entry + BE_AT * risk if pos_long else entry - BE_AT * risk

        # fill del limite (look-ahead-safe, da cb in poi).
        # ATTENZIONE: la condizione va sul verso della GAMBA (dove deve arrivare il prezzo
        # per ritracciare fino all'entry), NON sul verso della posizione. Cfr closure.py:82.
        f = None
        for j in range(max(cb, b + 1), min(b + 1 + bt.FILL_WINDOW, len(H))):
            touched = (L[j] <= entry) if buy_leg else (H[j] >= entry)
            if touched:
                f = j
                break
        if f is None:
            continue

        sgn = 1.0 if pos_long else -1.0
        cost_R = spread / risk
        sl_cur, be_on = sl, False
        n_we, we_after_gap_stop = 0, False
        outcome, R, hold = None, None, 0

        for j in range(f, min(f + bt.MAX_HOLD, len(H))):
            # --- confine di weekend fra j e j+1 ---
            if j + 1 < len(H) and dow[j] == 4 and dow[j + 1] != 4:
                n_we += 1
                unreal = sgn * (C[j] - entry) / risk           # R non realizzato al venerdi'
                gap_R = sgn * (O[j + 1] - C[j]) / risk         # gap col segno della posizione
                gaps.append({"sym": sym, "in_profit": bool(unreal > 0), "unreal_R": unreal,
                             "gap_R": gap_R, "be_on": be_on})

            # ordine identico a closure.py: prima il break-even, poi il test di stop/target
            if not be_on and ((H[j] >= be) if pos_long else (L[j] <= be)):
                be_on = True
                sl_cur = entry
            hit_sl = (L[j] <= sl_cur) if pos_long else (H[j] >= sl_cur)
            hit_tp = (H[j] >= tp) if pos_long else (L[j] <= tp)
            if hit_sl:
                # fill VERO: se l'apertura della barra e' gia' oltre lo stop, si riempie li'
                jumped = (O[j] < sl_cur) if pos_long else (O[j] > sl_cur)
                fill = O[j] if jumped else sl_cur
                R_assumed = (0.0 if be_on else -1.0) - cost_R    # convenzione closure.py
                R = sgn * (fill - entry) / risk - cost_R
                prev_we = (j > 0 and dow[j - 1] == 4 and dow[j] != 4)
                we_after_gap_stop = bool(jumped and prev_we)
                outcome = "SL"
                rows.append({"sym": sym, "outcome": outcome, "R": R, "R_assumed": R_assumed,
                             "jumped": bool(jumped), "gap_stop_weekend": we_after_gap_stop,
                             "n_weekend": n_we, "hold": j - f, "be_on": be_on})
                break
            if hit_tp:
                R = RR - cost_R
                rows.append({"sym": sym, "outcome": "TP", "R": R, "R_assumed": R,
                             "jumped": False, "gap_stop_weekend": False,
                             "n_weekend": n_we, "hold": j - f, "be_on": be_on})
                break
        else:
            j = min(f + bt.MAX_HOLD, len(H)) - 1
            R = sgn * (C[j] - entry) / risk - cost_R
            rows.append({"sym": sym, "outcome": "TIME", "R": R, "R_assumed": R,
                         "jumped": False, "gap_stop_weekend": False,
                         "n_weekend": n_we, "hold": j - f, "be_on": be_on})
    return pd.DataFrame(rows), pd.DataFrame(gaps)


def main():
    print("=" * 78)
    print("FADE (NXT A1) — DIAGNOSTICA WEEKEND. Descrittiva: non consuma trial.")
    print("=" * 78)
    T, G = [], []
    for s in bt.ASSETS:
        a, b = fade_trades(s)
        T.append(a)
        G.append(b)
    tr = pd.concat(T, ignore_index=True)
    gp = pd.concat(G, ignore_index=True)

    print(f"\nTrade: n={len(tr)}  E[R]={tr['R'].mean():+.3f}  "
          f"(con i fill assunti dal backtest: {tr['R_assumed'].mean():+.3f})")

    # ---- D1 ----
    print(f"\n--- D1  esposizione al weekend ---")
    print(f"  trade che attraversano >=1 weekend: {100*(tr['n_weekend'] > 0).mean():.1f}%"
          f"   weekend medi per trade: {tr['n_weekend'].mean():.2f}"
          f"   holding mediano: {tr['hold'].median():.0f} barre H1")
    print(f"  weekend attraversati in totale: {len(gp)}")

    # ---- D2 ----
    print(f"\n--- D2  i gap del weekend sono avversi o simmetrici? (R col segno della posizione) ---")
    g = gp["gap_R"].to_numpy()
    ci = bt.qm.bca_bootstrap_ci(g, metric=lambda x: float(np.mean(x)), conf=0.95,
                                n_boot=3000, seed=bt.SEED)
    print(f"  TUTTI      n={len(g):5}  media={g.mean():+.4f}R  mediana={np.median(g):+.4f}R"
          f"  BCa95[{ci['low']:+.4f},{ci['high']:+.4f}]  P(gap<0)={100*np.mean(g < 0):.1f}%")
    for lab, sub in (("in PROFITTO", gp[gp["in_profit"]]), ("in PERDITA ", gp[~gp["in_profit"]])):
        v = sub["gap_R"].to_numpy()
        if len(v) < 10:
            continue
        c2 = bt.qm.bca_bootstrap_ci(v, metric=lambda x: float(np.mean(x)), conf=0.95,
                                    n_boot=3000, seed=bt.SEED)
        print(f"  {lab} n={len(v):5}  media={v.mean():+.4f}R  mediana={np.median(v):+.4f}R"
              f"  BCa95[{c2['low']:+.4f},{c2['high']:+.4f}]  P(gap<0)={100*np.mean(v < 0):.1f}%")
    print(f"  coda: |gap| > 0.5R nel {100*np.mean(np.abs(g) > 0.5):.2f}% dei weekend;"
          f"  > 1R nel {100*np.mean(np.abs(g) > 1.0):.2f}%")

    # ---- D3 ----
    print(f"\n--- D3  stop SALTATI dal gap (il backtest li registra a -1R esatto) ---")
    sl = tr[tr["outcome"] == "SL"]
    jm = sl[sl["jumped"]]
    print(f"  stop totali: {len(sl)}   di cui con apertura gia' oltre lo stop: {len(jm)}"
          f"  ({100*len(jm)/max(len(sl),1):.1f}%)")
    if len(jm):
        print(f"  su questi: R vero medio={jm['R'].mean():+.3f} contro "
              f"{jm['R_assumed'].mean():+.3f} assunto  -> scarto {(jm['R']-jm['R_assumed']).mean():+.3f}R")
        wk = jm[jm["gap_stop_weekend"]]
        print(f"  di cui il salto avviene sulla barra DOPO un weekend: {len(wk)}"
              f"  ({100*len(wk)/max(len(jm),1):.1f}% dei salti)")
    delta = tr["R"].mean() - tr["R_assumed"].mean()
    print(f"  IMPATTO COMPLESSIVO sull'E[R] del fade: {delta:+.4f}R "
          f"({tr['R_assumed'].mean():+.3f} -> {tr['R'].mean():+.3f})")

    # ---- descrittivo sulla regola manuale ----
    print(f"\n--- DESCRITTIVO  la regola 'venerdi' chiudo i profit, lascio i loss' ---")
    prof = gp[gp["in_profit"]]["gap_R"]
    loss = gp[~gp["in_profit"]]["gap_R"]
    print(f"  R di gap che si RINUNCEREBBE chiudendo i vincenti: media {prof.mean():+.4f}R"
          f"  x {len(prof)} occorrenze = {prof.sum():+.1f}R complessivi")
    print(f"  R di gap che si TERREBBE tenendo i perdenti:        media {loss.mean():+.4f}R"
          f"  x {len(loss)} occorrenze = {loss.sum():+.1f}R complessivi")
    print(f"  NB: chiudere e riaprire costa spread; qui NON e' conteggiato (favorisce la regola).")
    print(f"  NB: e' una scomposizione descrittiva, NON un backtest della regola.")

    print(f"\n--- per strumento (gap medio in R) ---")
    for s, gg in gp.groupby("sym"):
        print(f"  {s:8} n={len(gg):5}  gap medio={gg['gap_R'].mean():+.4f}R  "
              f"P(<0)={100*np.mean(gg['gap_R'] < 0):.1f}%")


if __name__ == "__main__":
    main()
