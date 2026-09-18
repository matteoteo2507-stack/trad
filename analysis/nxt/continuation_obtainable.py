"""A5 - NXT CONTINUAZIONE rimisurata con i soli fill OTTENIBILI.

Perche' esiste
--------------
Il 2026-07-17 la continuazione NXT (entry al ritracciamento 0,5, SL 0,786, TP 1:3)
e' stata bocciata con **E[R] = -0,44R**, win-rate 13,3%, negativa in 14/14 anni e
6/6 strumenti. Verdetto: NO-GO per fallimento di breadth.

Il 2026-08-27 abbiamo scoperto che il motore concedeva il fill a `entry` **anche
quando il mercato aveva gia' oltrepassato il livello** prima che potessimo agire
(frattale K=5 -> ~6h di cecita', il 46,1% dei setup). E' look-ahead di PREZZO.

⚠️ **Il punto che rende questa misura necessaria.** Sul FADE quel difetto
**regalava** rendimento (+0,409 fantasma contro -0,250 reale): si vende a un
livello piu' alto di quello disponibile. Sulla CONTINUAZIONE, che **compra** lo
stesso livello, il regalo ha il segno opposto: **si compra piu' caro del mercato
disponibile**. Lo stesso artefatto che gonfiava il fade **deprimeva** la
continuazione -- ed e' proprio la direzione che puo' aver **prodotto** il NO-GO.

Un NO-GO nato da un difetto che peggiora i numeri e' l'errore piu' pericoloso del
workspace: e' invisibile e definitivo, perche' la strategia non esiste piu' e non
genera dati che lo contraddicano (docs/EARLY_STAGE_AUDIT_PROTOCOL.md).

Cosa fa
-------
Stessa geometria della pre-registrazione originale (CONGELATA: 0,5 / 0,786 / 1:3 /
BE a 2R), stessi asset, stessa finestra di fill. Cambia **solo** il modello di
esecuzione, esattamente come `fade_obtainable.py` ha fatto per il lato opposto:

  - prima barra azionabile = `cb + 1` (non `cb`: la barra di conferma porta
    l'informazione alla sua chiusura, non prima);
  - variante **SKIP**: si entra solo se all'apertura di quella barra il livello
    non e' gia' stato oltrepassato;
  - risoluzione affidata a `core.resolve_trade`, la primitiva unica la cui
    equivalenza con le quattro implementazioni storiche e' dimostrata da un test.

Non consuma trial: LIFECYCLE sez.3, "modellazione piu' realistica dell'esecuzione".

    python analysis/nxt/continuation_obtainable.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.nxt import backtest as bt            # noqa: E402
from core import quant_metrics as qm               # noqa: E402
from core.resolve_trade import (                   # noqa: E402
    FillConvention, resolve_trade,
)

ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "US100", "US500"]

RIFERIMENTO = FillConvention(fill_bar_can_resolve=True, tie="pess",
                             gap_beyond_stop=True, on_timeout="mark")
OTTIMISTA = FillConvention(fill_bar_can_resolve=True, tie="opt",
                           gap_beyond_stop=False, on_timeout="mark")
STORICA = FillConvention(fill_bar_can_resolve=True, tie="pess",
                         gap_beyond_stop=False, on_timeout="drop")


def trades_per_asset(sym):
    d = bt.load_h1(sym)
    O, H, L, C = (d["open"].values, d["high"].values,
                  d["low"].values, d["close"].values)
    A = bt.atr(H, L, C)
    legs = bt.build_legs(bt.zigzag(H, L), A)
    tempi = d["time"].values

    righe = []
    for leg in legs:
        side, hi, lo, rng = leg["side"], leg["hi"], leg["lo"], leg["rng"]
        b, cb = leg["end_idx"], leg["conf"]
        buy_leg = (side == "BUY")

        # geometria CONGELATA della pre-registrazione
        if buy_leg:
            entry = hi - bt.ENTRY_FIB * rng
            sl = hi - bt.SL_FIB * rng
        else:
            entry = lo + bt.ENTRY_FIB * rng
            sl = lo + bt.SL_FIB * rng
        pos_long = buy_leg                       # CONTINUAZIONE: nel verso del trend
        r_int = abs(entry - sl)
        if r_int <= 0:
            continue
        tp = entry + bt.RR * r_int if pos_long else entry - bt.RR * r_int
        cost_R = bt.SPREAD.get(sym, 0.0) / r_int

        fa = cb + 1
        if fa >= len(H):
            continue
        # il livello e' gia' stato oltrepassato all'apertura della prima barra
        # azionabile? Condizione identica a fade_obtainable.py: dipende dal verso
        # del ritracciamento, non da quale posizione prendiamo noi.
        already = (O[fa] < entry) if buy_leg else (O[fa] > entry)

        f = None
        for j in range(fa, min(b + 1 + bt.FILL_WINDOW, len(H))):
            if (L[j] <= entry) if buy_leg else (H[j] >= entry):
                f = j
                break
        if f is None:
            continue

        rec = {"asset": sym, "entry_idx": f, "already": bool(already),
               "anno": int(str(tempi[f])[:4])}
        for tag, conv in (("rif", RIFERIMENTO), ("opt", OTTIMISTA),
                          ("storica", STORICA)):
            res = resolve_trade(O, H, L, C, f, fill=entry, sl=sl, tp=tp,
                                long=pos_long, r_unit=r_int, max_hold=bt.MAX_HOLD,
                                be_at=bt.BE_AT, cost_R=cost_R, conv=conv)
            rec["R_" + tag] = np.nan if res is None else res.r
        righe.append(rec)
    return righe


def riga(nome, R):
    R = np.asarray([x for x in R if np.isfinite(x)], dtype=float)
    if len(R) < 30:
        return "  %-36s n=%-5d campione troppo piccolo" % (nome, len(R))
    ci = qm.bca_bootstrap_ci(R, np.mean, conf=0.95, n_boot=2000, seed=42)
    return ("  %-36s n=%-5d E[R]=%+.3f  BCa95 [%+.3f ; %+.3f]"
            % (nome, len(R), R.mean(), ci["low"], ci["high"]))


def _media(serie):
    v = np.asarray([x for x in serie if np.isfinite(x)], dtype=float)
    return v


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    righe = []
    for sym in ASSETS:
        try:
            righe += trades_per_asset(sym)
        except FileNotFoundError:
            print("  (dati mancanti per %s, saltato)" % sym)
    df = pd.DataFrame(righe)
    if df.empty:
        print("nessun trade")
        return 1

    tot = len(df)
    n_alr = int(df["already"].sum())
    print("A5 - NXT CONTINUAZIONE con fill ottenibili  (geometria CONGELATA 0,5/0,786/1:3)")
    print("=" * 78)
    print("Setup totali: %d   di cui livello GIA' OLTREPASSATO: %d (%.1f%%)"
          % (tot, n_alr, 100.0 * n_alr / tot))
    print("Sul FADE quel difetto regalava rendimento. Qui fa comprare piu' caro")
    print("del prezzo che il mercato rendeva davvero disponibile.\n")

    ott = df[~df["already"]]
    print("1) VARIANTE SKIP - solo fill OTTENIBILI   <- il numero onesto")
    print(riga("convenzione di riferimento", ott["R_rif"]))
    print(riga("convenzione ottimista", ott["R_opt"]))
    print()
    print("2) TUTTI i setup, col fill fantasma (come il verdetto del 17/07)")
    print(riga("convenzione di riferimento", df["R_rif"]))
    print(riga("convenzione storica (scarta i timeout)", df["R_storica"]))
    print()

    a = _media(ott["R_rif"])
    b_ = _media(df["R_rif"])
    if len(a) > 30 and len(b_) > 30:
        print("   DIFFERENZA fantasma -> ottenibile: %+.3f R" % (a.mean() - b_.mean()))
        print("   (sul FADE la stessa differenza valeva -0,659 R: +0,409 -> -0,250)\n")

    print("3) BREADTH - il verdetto del 17/07 diceva 'negativa in 6/6 strumenti'")
    pos = 0
    val = 0
    for sym in ASSETS:
        v = _media(ott[ott["asset"] == sym]["R_rif"])
        if len(v) < 30:
            print("   %-8s n=%-4d (campione troppo piccolo)" % (sym, len(v)))
            continue
        val += 1
        pos += v.mean() > 0
        print("   %-8s n=%-4d E[R]=%+.3f" % (sym, len(v), v.mean()))
    print("   strumenti positivi: %d su %d valutabili" % (pos, val))
    print()

    print("4) PER ANNO - il verdetto diceva 'negativa in 14/14 anni'")
    pos_a = val_a = 0
    for y in sorted(set(ott["anno"])):
        v = _media(ott[ott["anno"] == y]["R_rif"])
        if len(v) < 30:
            continue
        val_a += 1
        pos_a += v.mean() > 0
        print("   %d  n=%-4d E[R]=%+.3f" % (y, len(v), v.mean()))
    print("   anni positivi: %d su %d valutabili" % (pos_a, val_a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
