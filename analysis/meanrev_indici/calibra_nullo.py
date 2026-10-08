"""Distorsione del baseline a durata copiata sotto il nullo (revisione G1, seconda passata, 08/10/2026).

Il gatekeeper ha misurato che, senza nessun ritorno alla media, il divario reale − casuale a durata copiata esce in
media POSITIVO (~+0,05% a trade): la durata e' un esito del cammino del trade reale, e il pool dello stesso anno contiene
finestre sovrapposte a quel cammino, selezionato dal segnale. Questo script la misura con le STESSE funzioni del test
(`esegui_test.py`), su serie sintetiche senza vantaggio, PRIMA del test sui dati reali. Il valore entra nel §6 della
pre-registrazione come `B_NULL`: il LEAD richiede limite basso del divario > B_NULL.

    python analysis/meanrev_indici/calibra_nullo.py
"""
from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esegui_test as T   # noqa: E402

N_SEMI = 200
CONDIZIONI = (("deriva 0,05%/g, rho 0,9", 0.0005, 0.9), ("deriva 0, rho 0,9", 0.0, 0.9))


def divario(args):
    seme, deriva, rho = args
    sorgenti = T.sintetico_coppia(10_000 + seme, 0.0, rho, deriva)
    rng = np.random.default_rng(T.SEME + seme)
    reali, casuali = [], []
    for s, (d, _, _) in sorgenti.items():
        rsi, sma, atr = T.indicatori(d)
        r = T.braccio_reale(d, rsi, sma, s)
        for i, x in enumerate(r):
            x["evento"] = f"{s}-{i}"
        reali += r
        c, _ = T.braccio_casuale(d, rsi, sma, atr, s, r, rng, durata_copiata=True)
        casuali += c
    R, C = pd.DataFrame(reali), pd.DataFrame(casuali)
    med = C.groupby("evento")["netto"].mean()
    con = R[R.evento.isin(med.index)]
    return float(np.mean(con.netto.to_numpy() - med.loc[con.evento].to_numpy()))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"Distorsione del divario a durata copiata sotto il nullo, {N_SEMI} serie per condizione")
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        for nome, deriva, rho in CONDIZIONI:
            v = np.array(list(ex.map(divario, [(s, deriva, rho) for s in range(N_SEMI)], chunksize=4)))
            se = v.std(ddof=1) / np.sqrt(len(v))
            print(f"  {nome:26s}: divario medio {v.mean():+.4f}%  (errore standard {se:.4f}, "
                  f"IC95 [{v.mean() - 1.96 * se:+.4f}; {v.mean() + 1.96 * se:+.4f}])")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
