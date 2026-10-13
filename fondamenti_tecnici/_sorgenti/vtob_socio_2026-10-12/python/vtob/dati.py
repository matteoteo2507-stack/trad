"""Caricamento e controllo degli export barre MT5 di XAUUSD.

Formato: time,open,high,low,close,tick_volume,spread,real_volume
- time = ora del server del broker (UTC+3 d'estate, UTC+2 d'inverno); ora italiana = server - 1 h.
- spread in punti (1 punto = 0,01 $). ATTENZIONE: nelle barre MT5 lo spread è il MINIMO della candela
  (verificato: lo spread M15 coincide al 100% col minimo delle sue 15 M1), quindi sottostima il costo reale.
- prezzi BID.
I file originali non vengono mai modificati.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CARTELLA_DATI = Path(__file__).resolve().parents[2] / "data"      # cartella data/ del pacchetto
TF_MINUTI = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440, "W1": 10080}


SPREAD_SOSTITUTO_PCT = 0.0005     # 0,05% del prezzo: livello tipico dello spread del broker nel 2017 (primo anno valido)


def carica(tf: str, cartella: Path = CARTELLA_DATI, pulisci: bool = True) -> pd.DataFrame:
    """Barre di un timeframe, spread in $. Con pulisci=True (default) gestisce le anomalie trovate negli export:
    - H1/H4: fino al 12/07/2011 il file contiene UNA barra al giorno (sono giornaliere, non intraday) -> tagliate;
    - spread a zero (fino al 2011-2012) e spread fisso a 10 $ (2012-2016, valore finto dello storico) -> sostituiti con
      lo 0,05% del prezzo. Negli anni normali gli spread alti isolati (picchi reali) restano come sono.
    Quello che è stato fatto finisce in df.attrs (per il report)."""
    d = pd.read_csv(Path(cartella) / f"XAUUSD_{tf}.csv")
    idx = pd.DatetimeIndex(pd.to_datetime(d["time"], format="mixed"), name="time")
    df = pd.DataFrame({"open": d["open"].astype(float).values, "high": d["high"].astype(float).values,
                       "low": d["low"].astype(float).values, "close": d["close"].astype(float).values,
                       "volume": d["tick_volume"].astype(float).values,
                       "spread": d["spread"].astype(float).values * 0.01}, index=idx)
    df = df[~df.index.duplicated()].sort_index()
    df.attrs["tf"] = tf
    df.attrs["barre_tagliate_inizio"] = 0
    df.attrs["spread_sostituiti"] = 0
    if not pulisci:
        return df
    # 1) inizio della vera storia intraday: primo giorno con almeno metà delle barre tipiche
    if TF_MINUTI[tf] < 1440:
        cnt = df.index.normalize().value_counts().sort_index()
        tipiche = cnt[cnt.index >= cnt.index[-1] - pd.Timedelta(days=3 * 365)].median()
        primo = cnt[cnt >= 0.5 * tipiche].index[0]
        k = int((df.index < primo).sum())
        if k and (primo - df.index[0]) > pd.Timedelta(days=30):      # solo un vero tratto di barre giornaliere
            df = df[df.index >= primo].copy()
            df.attrs["barre_tagliate_inizio"] = k
            df.attrs["inizio_intraday"] = str(primo.date())
    # 2) spread non validi: zero ovunque; >= 5 $ solo negli anni in cui lo spread mediano è finto (>= 5 $)
    sp = df["spread"]
    med_anno = sp.groupby(df.index.year).transform("median")
    cattivi = (sp <= 0) | ((sp >= 5.0) & (med_anno >= 5.0))
    df.loc[cattivi, "spread"] = df.loc[cattivi, "close"] * SPREAD_SOSTITUTO_PCT
    df.attrs["spread_sostituiti"] = int(cattivi.sum())
    if cattivi.any():
        anni = df.index[cattivi.values].year
        df.attrs["spread_sostituiti_anni"] = f"{anni.min()}-{anni.max()}"
    return df


def ora_italiana(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Ora italiana = ora server - 1 h (come nel motore di riferimento)."""
    return idx - pd.Timedelta(hours=1)


def controllo(df: pd.DataFrame) -> dict:
    """Buchi, candele anomale, duplicati: da riportare nel report."""
    t = df.index.to_series()
    step = t.diff().mode().iloc[0]
    dt = t.diff()
    buchi = dt[(dt > step * 3) & (dt < pd.Timedelta("2D"))]
    rng = df["high"] - df["low"]
    med = rng.rolling(500, min_periods=50).median()
    spike = df.index[(rng > 20 * med).values]
    inval = ((df["high"] < df[["open", "close"]].max(axis=1)) | (df["low"] > df[["open", "close"]].min(axis=1))).sum()
    return {"barre": len(df), "inizio": str(df.index[0]), "fine": str(df.index[-1]), "passo": str(step),
            "candele_invalide": int(inval), "buchi_infrasettimanali": int(len(buchi)),
            "buco_max": str(buchi.max()) if len(buchi) else "-", "candele_anomale_range_20x": [str(x) for x in spike[:20]],
            "barre_tagliate_inizio": df.attrs.get("barre_tagliate_inizio", 0),
            "spread_sostituiti": df.attrs.get("spread_sostituiti", 0),
            "spread_sostituiti_anni": df.attrs.get("spread_sostituiti_anni", "-")}
