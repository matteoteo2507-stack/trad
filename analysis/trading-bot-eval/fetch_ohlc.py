"""Scarica OHLC multi-anno per il re-baseline (Task 2).

Yahoo (come il bot): GC=F (oro futures, lo spot XAUUSD=X e' delisted), BTC-USD, EURUSD=X.
Limiti Yahoo: 1h -> max ~730 giorni; 1d -> anni. Salva in analysis/trading-bot-eval/data/.
"""
from __future__ import annotations

import os

import pandas as pd
import yfinance as yf

OUT = "analysis/trading-bot-eval/data"
SYMS = {"XAU": "GC=F", "BTC": "BTC-USD", "EUR": "EURUSD=X"}
TFS = {"H1": ("1h", "730d"), "D1": ("1d", "10y")}


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for name, sym in SYMS.items():
        for tf, (interval, period) in TFS.items():
            df = yf.download(sym, interval=interval, period=period,
                             progress=False, auto_adjust=True)
            if df is None or len(df) == 0:
                print(f"{name} {tf}: VUOTO ({sym})")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.rename(columns=str.lower)
            keep = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
            df = df[keep]
            df.index.name = "time"
            path = f"{OUT}/{name}_{tf}.csv"
            df.to_csv(path)
            print(f"{name} {tf}: {len(df):5} righe  {df.index[0]} -> {df.index[-1]}  -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
