"""Dati per il Level Analyzer: offline (CSV esportati) e live (MT5 spot)."""
from __future__ import annotations

import csv
from datetime import datetime, timezone


def _row(r):
    t = datetime.fromisoformat(r["time"][:19])
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return {"t": t, "open": float(r["open"]), "high": float(r["high"]),
            "low": float(r["low"]), "close": float(r["close"])}


def _load_csv(path):
    with open(path, encoding="utf-8") as f:
        out = [_row(r) for r in csv.DictReader(r for r in f)]
    out.sort(key=lambda x: x["t"])
    return out


def load_offline(d1_path: str, h1_path: str, h1_window: int = 120):
    """Ritorna (prev_daily, h1_window_bars, price) dagli ultimi dati nei CSV."""
    d1 = _load_csv(d1_path)
    h1 = _load_csv(h1_path)
    prev_daily = d1[-2] if len(d1) >= 2 else d1[-1]      # daily chiuso precedente
    win = h1[-h1_window:]
    price = h1[-1]["close"]
    return prev_daily, win, price


def fetch_mt5(symbol: str, h1_window: int = 120):
    """Live da MT5: (prev_daily, h1_window_bars, price). Richiede terminale connesso."""
    import MetaTrader5 as mt5  # type: ignore
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize fallito: {mt5.last_error()}")
    try:
        mt5.symbol_select(symbol, True)
        h = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, h1_window + 5)
        d = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 5)
        tick = mt5.symbol_info_tick(symbol)
        price = (tick.bid + tick.ask) / 2 if tick else float(h[-1]["close"])
    finally:
        mt5.shutdown()
    if h is None or d is None or len(h) < 30 or len(d) < 2:
        raise RuntimeError("MT5: dati insufficienti")

    def conv(rec):
        return {"open": float(rec["open"]), "high": float(rec["high"]),
                "low": float(rec["low"]), "close": float(rec["close"])}
    h1 = [conv(x) for x in h]
    # daily chiuso precedente = penultimo (l'ultimo e' la candela di oggi in formazione)
    prev_daily = conv(d[-2])
    return prev_daily, h1[-h1_window:], price


def fetch_h1_ts(ticker: str, days: int = 14):
    """H1 CON timestamp (per la riconciliazione forward): lista di {t,open,high,low,close} UTC."""
    import pandas as pd
    import yfinance as yf
    h = yf.download(ticker, period=f"{days}d", interval="1h", auto_adjust=False, progress=False)
    if h is None or len(h) < 2:
        raise RuntimeError(f"yfinance: dati insufficienti per {ticker}")
    if isinstance(h.columns, pd.MultiIndex):
        h.columns = [c[0] for c in h.columns]
    h.columns = [c.lower() for c in h.columns]
    out = []
    for ts, r in h[["open", "high", "low", "close"]].dropna().iterrows():
        t = ts.to_pydatetime()
        t = t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)
        out.append({"t": t, "open": float(r.open), "high": float(r.high),
                    "low": float(r.low), "close": float(r.close)})
    out.sort(key=lambda x: x["t"])
    return out


def fetch_yfinance(ticker: str, h1_window: int = 120):
    """Live da Yahoo (per host Linux/cloud senza MT5): (prev_daily, h1_window_bars, price).
    NB: per l'oro il ticker e' GC=F (futures), ~spot con offset; per BTC e' BTC-USD (~spot)."""
    import pandas as pd
    import yfinance as yf
    h = yf.download(ticker, period="60d", interval="1h", auto_adjust=False, progress=False)
    d = yf.download(ticker, period="200d", interval="1d", auto_adjust=False, progress=False)
    if h is None or len(h) < 30 or d is None or len(d) < 2:
        raise RuntimeError(f"yfinance: dati insufficienti per {ticker}")
    for df in (h, d):
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df.columns = [c.lower() for c in df.columns]

    def rows(df):
        return [{"open": float(r.open), "high": float(r.high),
                 "low": float(r.low), "close": float(r.close)}
                for r in df[["open", "high", "low", "close"]].dropna().itertuples()]
    h1 = rows(h)
    drows = rows(d)
    prev_daily = drows[-2]      # ultimo daily e' quello in formazione di oggi
    price = h1[-1]["close"]
    return prev_daily, h1[-h1_window:], price
