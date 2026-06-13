"""Esporta storia spot XAUUSD da MT5 (broker) — stessa convenzione orario di
strategies/confluence_auto/data_source.py (epoch -> UTC naive).

Prende il massimo disponibile dal terminale per TF. Output in
analysis/trading-bot-eval/data/XAU_spot_{D1,H1,M15,M5}.csv (non tocca analysis/data).

Uso: python analysis/trading-bot-eval/export_mt5_spot.py   (MT5 terminal connesso)
"""
from __future__ import annotations

import os
import sys

import pandas as pd

SYMBOL = "XAUUSD"
OUT = "analysis/trading-bot-eval/data"
# (suffisso, costante TF, n. barre da richiedere a ritroso da ora)
WANT = [("D1", "TIMEFRAME_D1", 6000),
        ("H1", "TIMEFRAME_H1", 80000),
        ("M15", "TIMEFRAME_M15", 250000),
        ("M5", "TIMEFRAME_M5", 250000)]


def main() -> int:
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        print("MetaTrader5 non installato."); return 1
    if not mt5.initialize():
        print("MT5 initialize() fallito:", mt5.last_error()); return 1
    os.makedirs(OUT, exist_ok=True)
    if not mt5.symbol_select(SYMBOL, True):
        print(f"symbol_select({SYMBOL}) fallito:", mt5.last_error())
    try:
        for suf, tfname, count in WANT:
            tf = getattr(mt5, tfname)
            rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, count)
            if rates is None or len(rates) == 0:
                print(f"{suf}: nessun dato ({mt5.last_error()})"); continue
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_localize(None)
            df = df.set_index("time")
            df["volume"] = df["tick_volume"]
            df = df[["open", "high", "low", "close", "volume"]]
            path = f"{OUT}/XAU_spot_{suf}.csv"
            df.to_csv(path)
            print(f"{suf}: {len(df):6} barre  {df.index[0]} -> {df.index[-1]}  -> {path}")
    finally:
        mt5.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
