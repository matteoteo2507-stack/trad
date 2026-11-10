"""Scarica da Dukascopy gli indici europei per l'holdout di H1 (backlog §H, referto passo 4). 0 trial.

DAX, Euro Stoxx 50 e FTSE 100 a M5, dal 2020 a oggi, lato bid, timestamp UTC senza fuso (come gli altri
file Dukascopy). Scrive analysis/trading-bot-eval/data/{DAX,EUSTX50,FTSE100}_M5.csv (fuori da git).

Questi dati sono destinati all'HOLDOUT SIGILLATO della famiglia `momentum_ultima_mezzora`: lo script
stampa solo conteggi di barre. Nessuna statistica sui prezzi; i controlli meccanici li fa
verifica_dati.py, che non calcola rendimenti.

Uso: python analysis/ultima_mezzora/scarica_dukascopy.py
"""
from __future__ import annotations

import datetime as dt
import os
from datetime import timezone

import dukascopy_python as dk
import dukascopy_python.instruments as ins
import pandas as pd

OUT = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
STRUMENTI = [("DAX", ins.INSTRUMENT_IDX_EUROPE_E_DAAX),
             ("EUSTX50", ins.INSTRUMENT_IDX_EUROPE_E_DJE50XX),
             ("FTSE100", ins.INSTRUMENT_IDX_EUROPE_E_FUTSEE_100)]
ANNO_INIZIO = 2020  # il campione della fonte finisce a maggio 2020: l'holdout parte da giugno


def scarica(nome: str, codice: str) -> None:
    """Scarica anno per anno (piu' robusto di una richiesta sola) e scrive il CSV."""
    adesso = dt.datetime.now(timezone.utc)
    pezzi = []
    for anno in range(ANNO_INIZIO, adesso.year + 1):
        da = dt.datetime(anno, 1, 1, tzinfo=timezone.utc)
        a = min(dt.datetime(anno + 1, 1, 1, tzinfo=timezone.utc), adesso)
        try:
            df = dk.fetch(codice, dk.INTERVAL_MIN_5, dk.OFFER_SIDE_BID, da, a)
        except Exception as ex:  # noqa: BLE001 - un anno fallito non deve fermare gli altri
            print(f"  {nome} {anno}: errore {ex}")
            continue
        if df is not None and len(df):
            pezzi.append(df)
            print(f"  {nome} {anno}: {len(df)} barre", flush=True)
    if not pezzi:
        print(f"{nome}: nessun dato")
        return
    tutto = pd.concat(pezzi)
    tutto = tutto[~tutto.index.duplicated(keep="last")].sort_index()
    tutto = tutto.rename_axis("time").reset_index()
    tutto["time"] = pd.to_datetime(tutto["time"], utc=True).dt.tz_localize(None)  # UTC senza fuso
    tutto = tutto[["time", "open", "high", "low", "close", "volume"]]
    percorso = os.path.join(OUT, f"{nome}_M5.csv")
    tutto.to_csv(percorso, index=False)
    print(f"{nome}: {len(tutto)} barre, {tutto['time'].iloc[0].date()} -> "
          f"{tutto['time'].iloc[-1].date()} -> {os.path.normpath(percorso)}", flush=True)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for nome, codice in STRUMENTI:
        scarica(nome, codice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
