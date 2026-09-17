"""FADE con soli fill OTTENIBILI, risolto dalla primitiva unica.

Risponde alla condizione 2 della sez. 11 della pre-registrazione: *"un backtest che
modelli solo fill ottenibili, e il cui E[R] risultante sia positivo"*. Usa
`core.resolve_trade`, la cui equivalenza con le quattro implementazioni storiche e'
verificata in `core/tests/test_resolve_trade.py`.

Misura due cose separate:

1. **E[R] della variante SKIP** (si entra solo se il livello non e' gia' stato
   oltrepassato all'apertura della prima barra azionabile), sotto la convenzione di
   riferimento e sotto quella ottimista: la distanza fra le due e' l'ambiguita' residua.
2. **Quanto costa la convenzione `on_timeout`**. Tre delle quattro implementazioni
   storiche SCARTAVANO i trade che a max-hold non avevano toccato ne' SL ne' TP.
   Non e' prudenza: e' un filtro sull'esito. Qui si misura quanti trade sparivano e
   quanto spostavano la media.

Non consuma trial: LIFECYCLE sez.3, "modellazione piu' realistica dell'esecuzione".

    python analysis/nxt/fade_obtainable.py
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

RISK_FRAC = 0.286      # config A1, CONGELATO
RR = 3.0
BE_AT = 2.0

# La convenzione di riferimento: sfavorevole dove il dato e' ambiguo, ma senza
# scartare i trade in timeout (scartarli e' selezione, non prudenza).
RIFERIMENTO = FillConvention(fill_bar_can_resolve=True, tie="pess",
                             gap_beyond_stop=True, on_timeout="mark")
OTTIMISTA = FillConvention(fill_bar_can_resolve=True, tie="opt",
                           gap_beyond_stop=False, on_timeout="mark")
# Quella che produceva i numeri storici del fade (closure.py).
STORICA = FillConvention(fill_bar_can_resolve=True, tie="pess",
                         gap_beyond_stop=False, on_timeout="drop")


def trades_per_asset(sym):
    d = bt.load_h1(sym)
    O = d["open"].values
    H = d["high"].values
    L = d["low"].values
    C = d["close"].values
    A = bt.atr(H, L, C)
    legs = bt.build_legs(bt.zigzag(H, L), A)

    righe = []
    for leg in legs:
        side, hi, lo, rng = leg["side"], leg["hi"], leg["lo"], leg["rng"]
        b, cb = leg["end_idx"], leg["conf"]
        buy_leg = (side == "BUY")

        entry = (hi - 0.5 * rng) if buy_leg else (lo + 0.5 * rng)
        pos_long = not buy_leg                    # FADE: posizione invertita
        r_int = RISK_FRAC * rng
        if r_int <= 0:
            continue
        sl = entry - r_int if pos_long else entry + r_int
        tp = entry + RR * r_int if pos_long else entry - RR * r_int
        cost_R = bt.SPREAD.get(sym, 0.0) / r_int

        fa = cb + 1
        if fa >= len(H):
            continue
        # OTTENIBILE? il livello non deve essere gia' oltrepassato all'apertura
        # della prima barra azionabile (stessa definizione di entry_fill_audit.py)
        already = (O[fa] > entry) if pos_long else (O[fa] < entry)

        f = None
        for j in range(fa, min(b + 1 + bt.FILL_WINDOW, len(H))):
            if (L[j] <= entry) if buy_leg else (H[j] >= entry):
                f = j
                break
        if f is None:
            continue

        rec = {"asset": sym, "entry_idx": f, "already": bool(already)}
        for tag, conv in (("rif", RIFERIMENTO), ("opt", OTTIMISTA),
                          ("storica", STORICA)):
            res = resolve_trade(O, H, L, C, f, fill=entry, sl=sl, tp=tp,
                                long=pos_long, r_unit=r_int, max_hold=bt.MAX_HOLD,
                                be_at=BE_AT, cost_R=cost_R, conv=conv)
            rec["R_" + tag] = np.nan if res is None else res.r
            rec["esito_" + tag] = None if res is None else res.outcome
        righe.append(rec)
    return righe


def riga(nome, R):
    R = np.asarray([x for x in R if np.isfinite(x)], dtype=float)
    if len(R) < 30:
        return "  %-34s n=%-5d campione troppo piccolo" % (nome, len(R))
    ci = qm.bca_bootstrap_ci(R, np.mean, conf=0.95, n_boot=2000, seed=42)
    lo, hi = ci["low"], ci["high"]
    se = R.std(ddof=1) / np.sqrt(len(R))
    return ("  %-34s n=%-5d E[R]=%+.3f  BCa95 [%+.3f ; %+.3f]  SE=%.3f"
            % (nome, len(R), R.mean(), lo, hi, se))


def main() -> int:
    righe = []
    for sym in bt.SYMS if hasattr(bt, "SYMS") else \
            ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "US100", "US500"]:
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
    print("FADE config A1 - risolto con core.resolve_trade")
    print("=" * 74)
    print("Setup totali: %d   di cui con livello GIA' OLTREPASSATO: %d (%.1f%%)"
          % (tot, n_alr, 100.0 * n_alr / tot))
    print("Quelli sono i setup che la spec (e ora l'EA v1.10) NON prende.\n")

    ott = df[~df["already"]]
    print("1) VARIANTE SKIP - solo fill ottenibili")
    print(riga("convenzione di riferimento", ott["R_rif"]))
    print(riga("convenzione ottimista", ott["R_opt"]))
    print("   La distanza fra le due e' l'ambiguita' che il dato OHLC non risolve.\n")

    print("2) TUTTI i setup, come se il fill fantasma fosse valido (per confronto)")
    print(riga("convenzione di riferimento", df["R_rif"]))
    print("   Include i %d setup non ottenibili: e' il numero che gonfiava il lead.\n"
          % n_alr)

    print("3) QUANTO COSTA SCARTARE I TRADE IN TIMEOUT")
    persi = int(df["R_storica"].isna().sum())
    print("   Trade che la convenzione storica SCARTAVA: %d su %d (%.1f%%)"
          % (persi, tot, 100.0 * persi / tot))
    if persi:
        tmo = df[df["esito_rif"] == "TIMEOUT"]["R_rif"]
        print(riga("   i soli trade scartati, valutati", tmo))
        print(riga("   tutti, scartando (storica)", df["R_storica"]))
        print(riga("   tutti, senza scartare (rif.)", df["R_rif"]))
        print("   La differenza fra le ultime due righe e' il costo del filtro.")
    print()

    print("4) COMPOSIZIONE DEGLI ESITI (convenzione di riferimento)")
    print(df["esito_rif"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
