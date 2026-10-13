"""Intake del secondo pacchetto VTOB del socio (12/10/2026: uscite parziali su A e B, strategia US_M30 sul Nasdaq). 0 trial.

Come `descrittivi.py`: legge solo cio' che il socio ha consegnato e rilancia il suo codice com'e'. Non prova varianti,
non simula ingressi, e NON tocca le barre precedenti al 12/07/2022 che il pacchetto contiene (H1 dal 2011, M30 dal
2018): lanciare le sue regole li' sarebbe un test.

Cosa stampa:
1. RIPRODUCIBILITA: i 535 trade rigenerati coincidono con quelli consegnati?
2. TRADE per strategia: lato, esiti, anno, Sharpe per trade, MDE, soglia di futilita'.
3. DATI: da quando partono le barre, unita' dello spread, salita di oro e Nasdaq.

Il codice del socio usa numba solo per la velocita': se non e' installato, qui `njit` diventa una funzione che non fa
niente e il risultato e' lo stesso (piu' lento).

Uso: python analysis/vtob_intake/secondo_pacchetto.py [--sorgente DIR] [--materiale DIR]
"""
from __future__ import annotations

import argparse
import os
import sys
import types

import numpy as np
import pandas as pd

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, RADICE)
from core.trial_ledger import futility_sharpe  # noqa: E402
from core.verifiche import mde  # noqa: E402

SORGENTE = os.path.join(RADICE, "fondamenti_tecnici", "_sorgenti", "vtob_socio_2026-10-12")
MATERIALE = os.path.join(RADICE, "materiale_socio", "vtob_dati_risultati_usm30_2000-06_2026-10")
INIZIO_REPORT = pd.Timestamp("2022-07-12")


def numba_o_sostituto() -> None:
    try:
        import numba  # noqa: F401
    except ModuleNotFoundError:
        finto = types.ModuleType("numba")
        finto.njit = lambda *a, **k: a[0] if a and callable(a[0]) else (lambda f: f)
        sys.modules["numba"] = finto


def riproducibilita(sorgente: str, materiale: str) -> pd.DataFrame:
    print("== 1. RIPRODUCIBILITA (trade rigenerati col codice del socio contro quelli consegnati)")
    from pathlib import Path

    sys.dont_write_bytecode = True  # niente __pycache__ dentro la cartella delle sorgenti
    sys.path.insert(0, os.path.join(sorgente, "python"))
    numba_o_sostituto()
    import riproduci_backtest as rb

    rb.DATI = Path(materiale) / "dati"  # cambia solo dove cerca le barre
    nuovo = rb.calcola()["trade"]
    dato = pd.read_csv(os.path.join(materiale, "backtest", "trade_tutti.csv"), sep=";", decimal=",", parse_dates=["ingresso", "uscita"])
    uguali = (len(nuovo) == len(dato) and (pd.to_datetime(nuovo.ingresso).values == dato.ingresso.values).all()
              and np.allclose(nuovo.R, dato.R, atol=1e-4))
    print(f"  consegnati {len(dato)}, rigenerati {len(nuovo)}, identici = {uguali}")
    return dato


def trade(T: pd.DataFrame) -> None:
    print("\n== 2. TRADE CONSEGNATI")
    for nome, X in T.groupby("strategia"):
        lati = {d: (len(Y), round(float(Y.R.sum()), 1), round(float(Y.R.mean()), 3)) for d, Y in X.groupby("direzione")}
        sh = X.R.mean() / X.R.std()
        recenti = X[X.ingresso >= "2026-02-01"]
        print(f"  {nome}: n = {len(X)}, R {X.R.sum():.1f}, media {X.R.mean():.3f}, sd {X.R.std():.3f} | per lato (n, somma, media): {lati}")
        print(f"     esiti: {X.esito.value_counts().to_dict()} | somma R per anno: {X.groupby(X.uscita.dt.year).R.sum().round(1).to_dict()} "
              f"| ingressi dal 2026-02-01: {recenti.R.sum():.1f} R su {len(recenti)}")
        print(f"     Sharpe per trade {sh:.3f} | MDE a un test {mde(X.R.std(), len(X)):.3f} | soglia di futilita' a 100 prove "
              f"{futility_sharpe(100, len(X), 1):.3f}, a 1000 {futility_sharpe(1000, len(X), 1):.3f}")
    print("  tutte insieme, per lato (n, somma R):", {d: (len(Y), round(float(Y.R.sum()), 1)) for d, Y in T.groupby("direzione")})


def dati(materiale: str) -> None:
    print("\n== 3. DATI (solo conteggi e prezzi: nessuna regola lanciata prima del 12/07/2022)")
    for f in ("XAUUSD_M15", "XAUUSD_M30", "XAUUSD_H1", "USTEC_M30"):
        d = pd.read_csv(os.path.join(materiale, "dati", f + ".csv"), parse_dates=["time"]).set_index("time")
        per_giorno = d.index.normalize().value_counts().sort_index()
        intraday = per_giorno[per_giorno >= 12].index[0]
        mese = d.spread.groupby(d.index.to_period("M")).median()
        print(f"  {f}: barre intraday dal {intraday.date()}, {int((d.index < INIZIO_REPORT).sum())} barre prima del 12/07/2022 | "
              f"spread mediano (punti) set-dic 2025: {[float(v) for v in mese['2025-09':'2025-12']]} | chiusura {d.close.iloc[0]:.0f} -> {d.close.iloc[-1]:.0f}")
    oro = pd.read_csv(os.path.join(materiale, "dati", "XAUUSD_D1.csv"), parse_dates=["time"]).set_index("time").close
    ustec = pd.read_csv(os.path.join(materiale, "dati", "USTEC_M30.csv"), parse_dates=["time"]).set_index("time").close
    print(f"  oro D1: {oro['2011-07-13':].iloc[0]:.0f} (13/07/2011), {oro['2018-04-16':].iloc[0]:.0f} (16/04/2018), "
          f"{oro['2022-07-12':].iloc[0]:.0f} (12/07/2022), {oro.iloc[-1]:.0f} (fine) | Nasdaq nel file: {ustec.iloc[0]:.0f} -> {ustec.iloc[-1]:.0f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sorgente", default=SORGENTE, help="cartella con python/ del socio")
    ap.add_argument("--materiale", default=MATERIALE, help="cartella con dati/ e backtest/ del socio")
    a = ap.parse_args()
    T = riproducibilita(a.sorgente, a.materiale)
    trade(T)
    dati(a.materiale)


if __name__ == "__main__":
    main()
