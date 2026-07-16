"""Esporta US100 e US500 a M5 da MT5 (per l'Opening-Range Breakout).

Scarica quante più barre M5 possibile e le scrive in analysis/trading-bot-eval/data/{SYM}_M5.csv
(OHLC + tick_volume), con un report di copertura (barre, span, anni, ora del giorno più volatile
= sanity per l'apertura USA). I timestamp restano in ora server (naive), come gli altri dati; la
conversione all'apertura USA 09:30 ET è gestita e verificata nel backtester.

Uso: python analysis/opening_range/export_m5.py   (terminale MT5 connesso)
"""
from __future__ import annotations

import os

import pandas as pd

OUT = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
SYMBOLS = [("US100", "US100"), ("US500", "US500")]
COUNT = 500_000   # M5: ~500k barre ≈ diversi anni; il broker può darne meno


def main() -> int:
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        print("MetaTrader5 non installato (serve il PC con MT5)."); return 1
    if not mt5.initialize():
        print("MT5 initialize() fallito:", mt5.last_error()); return 1
    os.makedirs(OUT, exist_ok=True)
    try:
        for sym, prefix in SYMBOLS:
            if not mt5.symbol_select(sym, True):
                print(f"[SKIP] symbol_select({sym}) fallito: {mt5.last_error()} "
                      f"-> aggiusta il nome per il tuo broker"); continue
            rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, COUNT)
            if rates is None or len(rates) == 0:
                print(f"  {sym} M5: nessun dato ({mt5.last_error()})"); continue
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_localize(None)
            df = df.set_index("time")
            df["volume"] = df["tick_volume"]
            df = df[["open", "high", "low", "close", "volume"]]
            path = os.path.join(OUT, f"{prefix}_M5.csv")
            df.to_csv(path)
            span_years = (df.index[-1] - df.index[0]).days / 365.25
            # ora del giorno con range medio massimo (sanity apertura USA)
            rng = (df["high"] - df["low"]).groupby(df.index.hour).mean()
            top = rng.sort_values(ascending=False).head(3)
            print(f"  {sym}: {len(df):7} barre M5  {df.index[0].date()} -> {df.index[-1].date()} "
                  f"({span_years:.1f}y)")
            print(f"       ore (server) più volatili: " +
                  ", ".join(f"{h:02d}:00 ({v:.1f})" for h, v in top.items()))
    finally:
        mt5.shutdown()
    print("\nCSV in analysis/trading-bot-eval/data/ (gitignored). "
          "L'ora server più volatile dovrebbe corrispondere all'apertura USA (~16:30 se server EET).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
