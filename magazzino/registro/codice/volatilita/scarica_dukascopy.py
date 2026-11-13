"""Scarica da Dukascopy le serie a 5 minuti della famiglia `volatilita` (strumenti, LIFECYCLE §8ter). 0 trial.

Stesso paniere dei futures a 1 minuto dei soci (`motore/data/prezzi/futures_1m/`), da gennaio 2012 a oggi, lato bid,
timestamp UTC senza fuso (come gli altri file Dukascopy). Una sola fonte per tutta la storia: l'holdout di due anni
(LIFECYCLE §8ter H1) non deve contenere un cambio di feed.

Scrive `motore/data/prezzi/volatilita_m5/<NOME>_M5.csv` (fuori da git). Non tocca i file usati dagli studi chiusi.
Una parte di questi dati e' HOLDOUT: lo script stampa solo conteggi di barre, nessuna statistica sui prezzi.

Uso: python magazzino/registro/codice/volatilita/scarica_dukascopy.py [NOME ...]   (senza nomi: tutti)
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from datetime import timezone
from pathlib import Path

import dukascopy_python as dk
import dukascopy_python.instruments as ins
import pandas as pd

ROOT = next(str(p) for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())
OUT = os.path.join(ROOT, "motore/data/prezzi/volatilita_m5")
STRUMENTI = {
    "SPX500": ins.INSTRUMENT_IDX_AMERICA_E_SANDP_500,
    "NAS100": ins.INSTRUMENT_IDX_AMERICA_E_NQ_100,
    "DOW": ins.INSTRUMENT_IDX_AMERICA_E_D_J_IND,
    "RUSSELL": ins.INSTRUMENT_IDX_AMERICA_USSC2000_IDX_USD,
    "DAX": ins.INSTRUMENT_IDX_EUROPE_E_DAAX,
    "XAUUSD": ins.INSTRUMENT_FX_METALS_XAU_USD,
    "XAGUSD": ins.INSTRUMENT_FX_METALS_XAG_USD,
    "WTI": ins.INSTRUMENT_CMD_ENERGY_E_LIGHT,
    "EURUSD": ins.INSTRUMENT_FX_MAJORS_EUR_USD,
}
ANNO_INIZIO = 2012


def scarica(nome: str, codice: str) -> None:
    """Anno per anno (piu' robusto di una richiesta sola); scrive su file temporaneo, poi lo rinomina."""
    adesso = dt.datetime.now(timezone.utc)
    pezzi = []
    for anno in range(ANNO_INIZIO, adesso.year + 1):
        da = dt.datetime(anno, 1, 1, tzinfo=timezone.utc)
        a = min(dt.datetime(anno + 1, 1, 1, tzinfo=timezone.utc), adesso)
        try:
            df = dk.fetch(codice, dk.INTERVAL_MIN_5, dk.OFFER_SIDE_BID, da, a)
        except Exception as ex:  # noqa: BLE001 - un anno fallito non deve fermare gli altri
            print(f"  {nome} {anno}: errore {ex}", flush=True)
            continue
        n = 0 if df is None else len(df)
        print(f"  {nome} {anno}: {n} barre", flush=True)
        if n:
            pezzi.append(df)
    if not pezzi:
        print(f"{nome}: nessun dato", flush=True)
        return
    tutto = pd.concat(pezzi)
    tutto = tutto[~tutto.index.duplicated(keep="last")].sort_index()
    tutto = tutto.rename_axis("time").reset_index()
    tutto["time"] = pd.to_datetime(tutto["time"], utc=True).dt.tz_localize(None)  # UTC senza fuso
    tutto = tutto[["time", "open", "high", "low", "close", "volume"]]
    percorso = os.path.join(OUT, f"{nome}_M5.csv")
    tmp = percorso + ".tmp"
    tutto.to_csv(tmp, index=False)
    os.replace(tmp, percorso)
    print(f"{nome}: {len(tutto)} barre, {tutto['time'].iloc[0]} -> {tutto['time'].iloc[-1]}", flush=True)


def main(argv: list[str]) -> int:
    os.makedirs(OUT, exist_ok=True)
    nomi = argv or list(STRUMENTI)
    for nome in nomi:
        scarica(nome, STRUMENTI[nome])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
