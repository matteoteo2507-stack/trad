"""Indicatori base. Tutti calcolati SOLO con dati fino alla barra corrente (nessun look-ahead):
il segnale si legge alla chiusura della barra i e si esegue all'apertura della barra i+1."""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def zscore(s: pd.Series, n: int) -> pd.Series:
    m = s.rolling(n, min_periods=n).mean()
    sd = s.rolling(n, min_periods=n).std()
    return (s - m) / sd.replace(0, np.nan)


def prev_day_levels(df: pd.DataFrame) -> pd.DataFrame:
    """High/low/mid del giorno PRECEDENTE (orario server), allineati a ogni barra."""
    d = df.index.normalize()
    daily = df.groupby(d).agg(h=("high", "max"), l=("low", "min"))
    prev = daily.shift(1)
    out = prev.reindex(d)
    out.index = df.index
    out["mid"] = (out["h"] + out["l"]) / 2
    return out


def session_range(df: pd.DataFrame, start_hour: int, end_hour: int) -> pd.DataFrame:
    """Range (high/low) della sessione [start_hour, end_hour) del giorno corrente,
    disponibile solo DOPO la chiusura della sessione (valori NaN prima)."""
    hours = df.index.hour
    day = df.index.normalize()
    in_sess = (hours >= start_hour) & (hours < end_hour)
    h = df["high"].where(in_sess)
    l = df["low"].where(in_sess)
    sh = h.groupby(day).cummax()
    sl = l.groupby(day).cummin()
    # congela il valore a fine sessione e rendilo disponibile solo dopo
    sh = sh.groupby(day).ffill()
    sl = sl.groupby(day).ffill()
    after = hours >= end_hour
    return pd.DataFrame({"h": sh.where(after), "l": sl.where(after)}, index=df.index)
