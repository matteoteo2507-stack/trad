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
