"""Caricamento dati OHLC esportati da MetaTrader 5.

Formati supportati:
  1) MT5 "Esporta barre" (tab-separated):
     <DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>
  2) CSV generico con colonne Date,Time,Open,High,Low,Close[,Volume,Spread]
  3) CSV con un'unica colonna datetime (time/datetime/date) + OHLC

Gli orari sono quelli del SERVER del broker (come in MT5): il "giorno di trading"
per le regole prop dipende da questo, quindi non convertiamo il fuso.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def _norm(c: str) -> str:
    return c.strip().strip("<>").lower()


def load_mt5_csv(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        head = f.readline()
    sep = "\t" if "\t" in head else ("," if head.count(",") >= head.count(";") else ";")
    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
    df.columns = [_norm(c) for c in df.columns]

    if "date" in df.columns and "time" in df.columns:
        ts = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str),
                            format="mixed", dayfirst=False)
    else:
        tcol = next((c for c in ("datetime", "time", "date", "timestamp") if c in df.columns), None)
        if tcol is None:
            raise ValueError(f"Colonna data/ora non trovata in {path}: {list(df.columns)}")
        ts = pd.to_datetime(df[tcol], format="mixed")

    out = pd.DataFrame(index=pd.DatetimeIndex(ts, name="time"))
    for c in ("open", "high", "low", "close"):
        if c not in df.columns:
            raise ValueError(f"Colonna '{c}' mancante in {path}")
        out[c] = df[c].astype(float).values
    vol = "tickvol" if "tickvol" in df.columns else ("volume" if "volume" in df.columns else None)
    out["volume"] = df[vol].astype(float).values if vol else np.nan
    # MT5 esporta lo spread in POINTS per barra: lo usiamo se presente
    out["spread_points"] = df["spread"].astype(float).values if "spread" in df.columns else np.nan

    out = out[~out.index.duplicated(keep="first")].sort_index()
    out = out.dropna(subset=["open", "high", "low", "close"])
    return out


def split_is_oos(df: pd.DataFrame, holdout_frac: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """In-sample / out-of-sample cronologico. L'OOS non va MAI guardato prima della fase di conferma."""
    cut = int(len(df) * (1 - holdout_frac))
    return df.iloc[:cut], df.iloc[cut:]


def timeframe_label(df: pd.DataFrame) -> str:
    step = df.index.to_series().diff().median()
    minutes = int(step.total_seconds() // 60)
    return {1: "M1", 5: "M5", 15: "M15", 30: "M30", 60: "H1", 240: "H4", 1440: "D1"}.get(minutes, f"{minutes}m")
