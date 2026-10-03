"""MDE della pre-registrazione Forex Gump, su ISTANTI CASUALI (§6, richiesto dalla G1 #1). 0 trial.

Non tocca gli istanti dei segnali. Ogni giornata di trading con segnali viene spostata IN BLOCCO di un
numero casuale di giorni (±1-20, stessa ora del giorno; l'anno puo' cambiare a cavallo di capodanno),
cosi' restano identici:
- la geometria di ogni bracket (distanze SL e TP postate),
- il numero di eventi e il loro RAGGRUPPAMENTO per giorno (che entra nel CI a cluster),
- la distribuzione delle ore del giorno.
Su ogni istante spostato si esegue lo stesso motore (`replay.esegui_appaiato`, barre M1: niente tick
fuori dalle finestre dei segnali) e si misura l'errore standard, iid e a cluster per giornata, di
d = (R_lato - R_opposto) / 2 e di R del lato. MDE = 2,80 x SE.

Uso: python analysis/forexgump/potenza.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from analysis.forexgump import replay as rp  # noqa: E402
from analysis.forexgump.carica import carica_m1, carica_segnali  # noqa: E402
from core.verifiche import fattore_potenza  # noqa: E402

SEED = 42
SPOSTAMENTI = [k for k in range(-20, 21) if k != 0]


def main() -> int:
    rng = np.random.default_rng(SEED)
    s = carica_segnali()
    bid, ask = carica_m1()
    pz = rp.Prezzi(m1_bid=bid, m1_ask=ask)
    idx = bid.index
    s["giorno"] = s.t_utc.map(rp.giorno_trading)

    d, rl, giorni, esiti = [], [], [], {}
    for g, blocco in s.groupby("giorno"):
        for _ in range(10):                       # trova uno spostamento con prezzi per tutto il blocco
            k = pd.Timedelta(days=int(rng.choice(SPOSTAMENTI)))
            nuovi = blocco.t_utc + k
            pos = idx.searchsorted(nuovi.values)
            ok = all(p < len(idx) and abs((idx[p] - t).total_seconds()) < 180 for p, t in zip(pos, nuovi))
            if ok:
                break
        else:
            continue
        for (_, r), t in zip(blocco.iterrows(), nuovi):
            x = rp.esegui_appaiato(pz, t, r.side == "buy", abs(r.entry - r.sl), abs(r.tp - r.entry))
            esiti[x["mentore"]["esito"]] = esiti.get(x["mentore"]["esito"], 0) + 1
            if x["d"] is None:
                continue
            d.append(x["d"]); rl.append(x["mentore"]["r"]); giorni.append(rp.giorno_trading(t))

    f = fattore_potenza()
    ci_d = rp.ci_cluster_giorno(d, giorni, n_boot=10_000)
    ci_r = rp.ci_cluster_giorno(rl, giorni, n_boot=10_000)
    sd_d, sd_r, n = float(np.std(d, ddof=1)), float(np.std(rl, ddof=1)), len(d)
    print("=" * 92)
    print("Forex Gump — MDE su istanti casuali (0 trial; nessun istante dei segnali simulato)")
    print("=" * 92)
    print(f"istanti eseguiti: {n} su {len(s)} segnali spostati   esiti del lato: {esiti}")
    print(f"giornate: {ci_d['giorni']}")
    print(f"\n  d = (R_lato - R_opposto)/2 : sd {sd_d:.3f}R   MDE iid {f * sd_d / np.sqrt(n):.3f}R   "
          f"MDE a cluster per giornata {f * ci_d['se']:.3f}R")
    print(f"  R del lato (per E[R])      : sd {sd_r:.3f}R   MDE iid {f * sd_r / np.sqrt(n):.3f}R   "
          f"MDE a cluster per giornata {f * ci_r['se']:.3f}R")
    print("\nDa scrivere nel §6 della pre-registrazione PRIMA dell'approvazione. Riferimento grezzo (su R,")
    print("esiti +5R/-1R): ~0,17-0,18R. La differenza fra MDE iid e a cluster e' il costo del raggruppamento.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
