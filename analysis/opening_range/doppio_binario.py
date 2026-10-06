"""Doppio binario sui trade ORB v2 (famiglia CLOSED): misura DESCRITTIVA, 0 trial, nessuna riapertura.

Dichiarata in docs/reviews/doppio_binario_closed_2026-10-06.md §2, nel commit PRECEDENTE all'esecuzione.
Domanda di Matteo (06/10): fra le famiglie CLOSED ce n'e' una per cui il doppio binario darebbe un risultato
diverso? L'aritmetica (§1 del referto) lascia in piedi solo NAS100; SPX500 e' il controllo.

Primario dichiarato: NAS100, R_pess (la convenzione del verdetto), blocco 1, O1 e O3 -> 2 confronti,
falso allarme ~10% sulla coppia. Tutto il resto e' descrittivo.

    python analysis/opening_range/doppio_binario.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_v2 import ADX_MIN_DEFAULT, run   # noqa: E402
from core.prop_sim import PROP_LAB             # noqa: E402
from core.sizing import confronta_overlay, confronta_overlay_prop   # noqa: E402

N_PERM = 1000
BLOCCHI = (1, 20)
BASI_PROP = (1.0, 2.0)
REGOLE = "two_step_classic"


def giorni(prim: pd.DataFrame, col: str):
    """Un elenco per giorno lavorativo dal primo all'ultimo trade. MAE = 1R per tutti: limite superiore
    (nessun trade puo' andare oltre lo stop prima del suo esito, salvo gap), quindi conservativo sul DD."""
    per = {}
    for d, r in zip(pd.to_datetime(prim["date"]), prim[col]):
        if np.isfinite(r):
            per.setdefault(d.normalize(), []).append((float(r), 1.0))
    cal = pd.bdate_range(min(per), max(per))
    return [per.get(d, []) for d in cal]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    with open(os.path.join(PROP_LAB, "config", "prop_rules.yaml"), encoding="utf-8") as f:
        rules = yaml.safe_load(f)[REGOLE]
    pd.set_option("display.width", 200)
    cols = ["binario", "e_per_unita", "e_lo", "e_hi", "valore_dipendenza", "percentile_reale", "max_dd_r",
            "max_dd_mediano_rimescolato", "lettura"]
    for sym in ("NAS100", "SPX500"):
        df = run(sym)
        prim = df[df["adx"] >= ADX_MIN_DEFAULT].reset_index(drop=True)
        print(f"\n===== {sym}: {len(prim)} trade primari (ADX >= {ADX_MIN_DEFAULT}), "
              f"{prim['date'].iloc[0]} -> {prim['date'].iloc[-1]} =====")
        for col in ("R_pess", "R_opt"):
            r = prim[col].to_numpy(dtype=float)
            r = r[np.isfinite(r)]
            for b in BLOCCHI:
                tab, runs = confronta_overlay(r, n_perm=N_PERM, blocco=b, seed=42)
                tag = "PRIMARIO" if (sym, col, b) == ("NAS100", "R_pess", 1) else "descrittivo"
                print(f"\n--- {col}, blocco {b} [{tag}]  n={len(r)}  E[R] 1R={r.mean():+.4f}  "
                      f"runs z={runs['z']:+.2f} p={runs['p']:.3f} ({runs['lettura']})")
                print(tab[cols].round(4).to_string(index=False))
        dt = giorni(prim, "R_pess")
        for base in BASI_PROP:
            tp = confronta_overlay_prop(dt, rules, base, n_paths=200, n_outer=60, seed=7)
            print(f"\n--- prop {REGOLE}, R_pess, rischio base {base}% [descrittivo]")
            print(tp.round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
