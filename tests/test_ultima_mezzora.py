"""Test della lettura delle barre per H1 (`analysis/ultima_mezzora/esegui_test.py`, `sedute_da_barre`).

E' la parte che il sintetico del test non attraversa (riserva 3 della revisione G1 dell'11/10): fuso, barre e
calendario. Le barre sono finte, con un prezzo che dipende solo dall'istante, quindi il valore atteso di ogni
rendimento si calcola a mano dagli orari di chiusura.
"""
from __future__ import annotations

import os
import sys

import exchange_calendars as xc
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis", "ultima_mezzora"))
import esegui_test as t  # noqa: E402

ET = "America/New_York"


def prezzo(istante: pd.Timestamp) -> float:
    """Prezzo finto: cresce di 0,01 al minuto da un'origine fissa. Dipende solo dall'istante (in UTC)."""
    origine = pd.Timestamp("2025-01-01", tz="UTC")
    return 5000.0 + 0.01 * (istante.tz_convert("UTC") - origine).total_seconds() / 60.0


def barre_utc(da: str, a: str, salta: list[str] | None = None) -> pd.DataFrame:
    """Barre M5 continue con timestamp UTC senza fuso (come i file Dukascopy), poi convertite come fa `carica`."""
    inizi = pd.date_range(da, a, freq="5min", tz="UTC")
    inizi = inizi[~inizi.isin(pd.DatetimeIndex(salta or [], tz="UTC"))]
    df = pd.DataFrame({"open": [prezzo(x) for x in inizi],
                       "close": [prezzo(x + pd.Timedelta(minutes=5)) for x in inizi]},
                      index=inizi.tz_convert(ET))
    return df


def chiusure(da: str, a: str) -> pd.Series:
    return xc.get_calendar("XNYS", start=da, end=a).schedule["close"]


def atteso(c_oggi: str, c_ieri: str) -> tuple[float, float]:
    """r_ROD e r_LH attesi, in punti base, dati gli istanti di chiusura (ora di New York)."""
    c, p = pd.Timestamp(c_oggi, tz=ET), pd.Timestamp(c_ieri, tz=ET)
    a30 = c - pd.Timedelta(minutes=30)
    return (1e4 * np.log(prezzo(a30) / prezzo(p)), 1e4 * np.log(prezzo(c) / prezzo(a30)))


def test_seduta_normale():
    sed = t.sedute_da_barre(barre_utc("2025-06-02", "2025-06-06"), chiusure("2025-06-02", "2025-06-05"), 5)
    riga = sed.loc[pd.Timestamp("2025-06-04")]
    rod, lh = atteso("2025-06-04 16:00", "2025-06-03 16:00")
    assert riga["valida"]
    assert riga["r_rod"] == pytest.approx(rod, abs=1e-9)
    assert riga["r_lh"] == pytest.approx(lh, abs=1e-9)
    assert riga["scarto"] == pytest.approx(0.0, abs=1e-9)   # il segnale chiude dove l'entrata apre
    assert not sed.loc[pd.Timestamp("2025-06-02"), "valida"]  # prima seduta: manca la chiusura precedente


def test_chiusura_anticipata():
    # 28/11/2025, venerdi' dopo il Ringraziamento: New York chiude alle 13:00; il 27 e' festa.
    sed = t.sedute_da_barre(barre_utc("2025-11-25", "2025-12-02"), chiusure("2025-11-25", "2025-12-01"), 5)
    assert pd.Timestamp("2025-11-27") not in sed.index
    rod, lh = atteso("2025-11-28 13:00", "2025-11-26 16:00")
    riga = sed.loc[pd.Timestamp("2025-11-28")]
    assert riga["r_rod"] == pytest.approx(rod, abs=1e-9)
    assert riga["r_lh"] == pytest.approx(lh, abs=1e-9)
    # la seduta dopo usa come "chiusura di ieri" le 13:00 del venerdi', non le 16:00
    rod_lun, _ = atteso("2025-12-01 16:00", "2025-11-28 13:00")
    assert sed.loc[pd.Timestamp("2025-12-01"), "r_rod"] == pytest.approx(rod_lun, abs=1e-9)


def test_settimana_del_cambio_d_ora():
    # 9/3/2025: New York passa all'ora legale. Le 16:00 sono le 21:00 UTC venerdi' 7 e le 20:00 UTC lunedi' 10.
    barre = barre_utc("2025-03-05", "2025-03-12")
    sed = t.sedute_da_barre(barre, chiusure("2025-03-05", "2025-03-11"), 5)
    rod, lh = atteso("2025-03-10 16:00", "2025-03-07 16:00")
    riga = sed.loc[pd.Timestamp("2025-03-10")]
    assert riga["r_rod"] == pytest.approx(rod, abs=1e-9)
    assert riga["r_lh"] == pytest.approx(lh, abs=1e-9)
    # controllo indipendente sugli orari UTC: l'entrata di lunedi' e' l'apertura della barra delle 19:30 UTC
    p_in = prezzo(pd.Timestamp("2025-03-10 19:30", tz="UTC"))
    p_out = prezzo(pd.Timestamp("2025-03-10 20:00", tz="UTC"))
    assert riga["r_lh"] == pytest.approx(1e4 * np.log(p_out / p_in), abs=1e-9)


@pytest.mark.parametrize("manca, finestra_ok", [
    ("2025-06-04 19:30", False),   # barra d'entrata (15:30 ET): la finestra non c'e'
    ("2025-06-04 19:25", True),    # barra del segnale (15:25 ET): la finestra c'e', la seduta non e' valida
    ("2025-06-03 19:55", True),    # ultima barra di ieri: manca la chiusura precedente
])
def test_barra_mancante(manca, finestra_ok):
    sed = t.sedute_da_barre(barre_utc("2025-06-02", "2025-06-06", salta=[manca]),
                            chiusure("2025-06-02", "2025-06-05"), 5)
    riga = sed.loc[pd.Timestamp("2025-06-04")]
    assert not riga["valida"]
    assert bool(riga["finestra_ok"]) is finestra_ok


def test_scala_nota_prima():
    # la scala del giorno t usa solo le 60 sedute precedenti: cambiare il giorno t non la sposta
    rng = np.random.default_rng(0)
    giorni = pd.bdate_range("2020-03-02", periods=200)
    sed = pd.DataFrame({"r_rod": rng.standard_normal(200) * 100, "r_lh": rng.standard_normal(200) * 28},
                       index=giorni)
    base = t.prepara(sed)
    mosso = sed.copy()
    ultimo = base.index[-1]
    mosso.loc[ultimo, ["r_rod", "r_lh"]] = [5000.0, 900.0]
    dopo = t.prepara(mosso)
    assert dopo.loc[ultimo, "sigma"] == pytest.approx(base.loc[ultimo, "sigma"])
    assert dopo.loc[ultimo, "sigma_lh"] == pytest.approx(base.loc[ultimo, "sigma_lh"])
    assert dopo.loc[ultimo, "w"] == pytest.approx(t.TETTO)   # il tetto limita la posizione
