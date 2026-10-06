"""Famiglia: MEAN REVERSION (ritorno verso la media / fade degli eccessi).

Catalogo e fonti: research/families/mean_reversion/catalogo.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, register
from ..backtest import Signals
from .. import indicators as ind


def _trend_ok(df, d, use_filter, n=200):
    """Filtro opzionale: long solo sopra SMA lunga, short solo sotto (reversion 'a favore di trend')."""
    if not use_filter:
        return np.ones(len(df), bool)
    m = ind.sma(df["close"], n).to_numpy()
    c = df["close"].to_numpy()
    return (c > m) if d == 1 else (c < m)


@register
class BollingerFade(Strategy):
    name = "bb_fade"
    family = "mean_reversion"
    description = "Chiusura fuori dalla Bollinger(n,k) -> fade verso la banda centrale. SL = m*ATR."
    grid = {"n": [20, 30, 50], "k": [2.0, 2.5, 3.0], "atr_sl": [1.5, 2.5], "trend": [0, 1]}

    def signals(self, df, n, k, atr_sl, trend):
        c = df["close"]
        mid = ind.sma(c, n); sd = c.rolling(n, min_periods=n).std()
        up, lo = mid + k * sd, mid - k * sd
        a = ind.atr(df, 14).to_numpy()
        e = np.zeros(len(df), int)
        e[(c < lo).to_numpy() & _trend_ok(df, 1, trend)] = 1
        e[(c > up).to_numpy() & _trend_ok(df, -1, trend)] = -1
        return Signals(entry=e, sl_dist=atr_sl * a, tp_level=mid.to_numpy(), max_bars=3 * n)


@register
class RSIExtreme(Strategy):
    name = "rsi_extreme"
    family = "mean_reversion"
    description = "RSI corto (Connors-style) in ipervenduto/ipercomprato -> entra; esce quando RSI torna a 50. SL = m*ATR."
    grid = {"n": [2, 3, 5], "lo": [5, 10, 20], "atr_sl": [1.5, 2.5], "trend": [0, 1]}

    def signals(self, df, n, lo, atr_sl, trend):
        r = ind.rsi(df["close"], n)
        a = ind.atr(df, 14).to_numpy()
        e = np.zeros(len(df), int)
        e[(r < lo).to_numpy() & _trend_ok(df, 1, trend)] = 1
        e[(r > 100 - lo).to_numpy() & _trend_ok(df, -1, trend)] = -1
        return Signals(entry=e, sl_dist=atr_sl * a, exit_long=(r > 50).to_numpy(),
                       exit_short=(r < 50).to_numpy(), max_bars=24)


@register
class ZScoreRevert(Strategy):
    name = "zscore_revert"
    family = "mean_reversion"
    description = "Z-score del prezzo vs media(n) oltre soglia -> entra; esce al ritorno dello z verso 0. SL = m*ATR."
    grid = {"n": [20, 50, 100], "z": [2.0, 2.5, 3.0], "z_exit": [0.0, 0.5], "atr_sl": [2.0, 3.0]}

    def signals(self, df, n, z, z_exit, atr_sl):
        zz = ind.zscore(df["close"], n)
        a = ind.atr(df, 14).to_numpy()
        e = np.zeros(len(df), int)
        e[(zz < -z).to_numpy()] = 1
        e[(zz > z).to_numpy()] = -1
        return Signals(entry=e, sl_dist=atr_sl * a, exit_long=(zz > -z_exit).to_numpy(),
                       exit_short=(zz < z_exit).to_numpy(), max_bars=2 * n)


@register
class KeltnerReversal(Strategy):
    name = "keltner_reversal"
    family = "mean_reversion"
    description = ("Barra precedente chiusa fuori dal Keltner (EMA ± m*ATR), barra attuale con candela di "
                   "inversione che richiude dentro -> fade verso l'EMA. SL oltre l'estremo + buffer ATR.")
    grid = {"n": [20, 50], "mult": [1.5, 2.0, 2.5], "buf": [0.2, 0.5], "trend": [0, 1]}

    def signals(self, df, n, mult, buf, trend):
        c = df["close"]; o = df["open"]
        m = ind.ema(c, n); a = ind.atr(df, 14)
        up, lo = m + mult * a, m - mult * a
        prev_out_lo = (c.shift(1) < lo.shift(1)); prev_out_up = (c.shift(1) > up.shift(1))
        bull = (c > o) & (c > lo); bear = (c < o) & (c < up)
        ext_lo = np.minimum(df["low"], df["low"].shift(1)); ext_hi = np.maximum(df["high"], df["high"].shift(1))
        e = np.zeros(len(df), int)
        L = (prev_out_lo & bull).to_numpy() & _trend_ok(df, 1, trend)
        S = (prev_out_up & bear).to_numpy() & _trend_ok(df, -1, trend)
        e[L] = 1; e[S] = -1
        sl = np.where(e == 1, (c - ext_lo + buf * a).to_numpy(), (ext_hi - c + buf * a).to_numpy())
        return Signals(entry=e, sl_dist=sl, tp_level=m.to_numpy(), max_bars=3 * n)


@register
class PrevDaySweep(Strategy):
    name = "pdh_pdl_sweep"
    family = "mean_reversion"
    description = ("Liquidity sweep: la barra supera il massimo (minimo) del giorno precedente e chiude di nuovo "
                   "dentro -> short (long). SL oltre la wick + buffer ATR. TP = R multiplo oppure metà range di ieri.")
    grid = {"buf": [0.1, 0.3], "tp": ["mid", 1.5, 2.0, 3.0], "start_h": [8, 10], "end_h": [18, 22]}

    def signals(self, df, buf, tp, start_h, end_h):
        pdl = ind.prev_day_levels(df)
        c = df["close"]; h = df["high"]; l = df["low"]
        a = ind.atr(df, 14)
        hr = df.index.hour
        window = (hr >= start_h) & (hr < end_h)
        S = ((h > pdl["h"]) & (c < pdl["h"])).to_numpy() & window
        L = ((l < pdl["l"]) & (c > pdl["l"])).to_numpy() & window
        e = np.zeros(len(df), int); e[L] = 1; e[S] = -1
        sl = np.where(e == 1, (c - l + buf * a).to_numpy(), (h - c + buf * a).to_numpy())
        if tp == "mid":
            return Signals(entry=e, sl_dist=sl, tp_level=pdl["mid"].to_numpy(), max_bars=24)
        return Signals(entry=e, sl_dist=sl, tp_r=float(tp), max_bars=24)


@register
class SessionRangeFade(Strategy):
    name = "asia_range_fade"
    family = "mean_reversion"
    description = ("Falsa rottura del range asiatico: dopo la sessione asiatica il prezzo esce dal range e "
                   "richiude dentro -> fade verso il centro del range. Orari = orario SERVER MT5.")
    grid = {"asia_end": [8, 9], "buf": [0.1, 0.3], "tp": ["mid", "opposite", 1.5], "last_h": [14, 18]}

    def signals(self, df, asia_end, buf, tp, last_h):
        rg = ind.session_range(df, 1, asia_end)
        c = df["close"]; h = df["high"]; l = df["low"]
        a = ind.atr(df, 14)
        hr = df.index.hour
        window = hr < last_h
        S = ((h > rg["h"]) & (c < rg["h"])).to_numpy() & window
        L = ((l < rg["l"]) & (c > rg["l"])).to_numpy() & window
        # un solo trade per giorno per lato: primo segnale della giornata
        day = df.index.normalize()
        S = S & (pd.Series(S, index=df.index).groupby(day).cumsum().to_numpy() == 1)
        L = L & (pd.Series(L, index=df.index).groupby(day).cumsum().to_numpy() == 1)
        e = np.zeros(len(df), int); e[L] = 1; e[S] = -1
        sl = np.where(e == 1, (c - l + buf * a).to_numpy(), (h - c + buf * a).to_numpy())
        mid = ((rg["h"] + rg["l"]) / 2).to_numpy()
        if tp == "mid":
            return Signals(entry=e, sl_dist=sl, tp_level=mid, max_bars=12)
        if tp == "opposite":
            lvl = np.where(e == 1, rg["h"].to_numpy(), rg["l"].to_numpy())
            return Signals(entry=e, sl_dist=sl, tp_level=lvl, max_bars=12)
        return Signals(entry=e, sl_dist=sl, tp_r=float(tp), max_bars=12)


@register
class ConsecutiveBars(Strategy):
    name = "consecutive_bars"
    family = "mean_reversion"
    description = "N chiusure consecutive nella stessa direzione -> fade; esce alla prima chiusura contraria. SL = m*ATR."
    grid = {"n_bars": [3, 4, 5, 6], "atr_sl": [1.5, 2.5], "trend": [0, 1]}

    def signals(self, df, n_bars, atr_sl, trend):
        c = df["close"]
        up = (c > c.shift(1)).astype(int); dn = (c < c.shift(1)).astype(int)
        run_up = up.rolling(n_bars).sum() == n_bars
        run_dn = dn.rolling(n_bars).sum() == n_bars
        a = ind.atr(df, 14).to_numpy()
        e = np.zeros(len(df), int)
        e[run_dn.to_numpy() & _trend_ok(df, 1, trend)] = 1
        e[run_up.to_numpy() & _trend_ok(df, -1, trend)] = -1
        return Signals(entry=e, sl_dist=atr_sl * a, exit_long=(up == 1).to_numpy(),
                       exit_short=(dn == 1).to_numpy(), max_bars=12)
