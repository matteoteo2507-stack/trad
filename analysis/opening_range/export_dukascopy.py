"""Scarica M5 storico lungo di NAS100 e SPX500 da Dukascopy (multi-regime 2011+).

Timestamp UTC (puliti). Scrive analysis/trading-bot-eval/data/{NAS100,SPX500}_M5.csv
(time,open,high,low,close,volume). Fetch anno-per-anno (robusto). Il livello CFD può differire
dal broker per un offset (irrilevante per una strategia di breakout, che è relativa); la struttura
intraday è quella dell'indice. Validazione vs broker sull'overlap fatta a parte.

Uso: python analysis/opening_range/export_dukascopy.py
"""
from __future__ import annotations

import datetime as dt
import os
from datetime import timezone

import pandas as pd

import dukascopy_python as dk
import dukascopy_python.instruments as ins

OUT = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
SYMS = [("NAS100", ins.INSTRUMENT_IDX_AMERICA_E_NQ_100),
        ("SPX500", ins.INSTRUMENT_IDX_AMERICA_E_SANDP_500)]
Y0, Y1 = 2011, 2027


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, code in SYMS:
        frames = []
        for y in range(Y0, Y1):
            s = dt.datetime(y, 1, 1, tzinfo=timezone.utc)
            e = dt.datetime(y + 1, 1, 1, tzinfo=timezone.utc)
            if s > dt.datetime.now(timezone.utc):
                break
            try:
                df = dk.fetch(code, dk.INTERVAL_MIN_5, dk.OFFER_SIDE_BID, s, e)
            except Exception as ex:  # noqa: BLE001
                print(f"  {name} {y}: errore {ex}"); continue
            if df is not None and len(df):
                frames.append(df)
                print(f"  {name} {y}: {len(df)} barre", flush=True)
        if not frames:
            print(f"{name}: nessun dato"); continue
        full = pd.concat(frames)
        full = full[~full.index.duplicated(keep="last")].sort_index()
        full = full.rename_axis("time").reset_index()
        full["time"] = pd.to_datetime(full["time"], utc=True).dt.tz_localize(None)  # naive UTC
        full = full[["time", "open", "high", "low", "close", "volume"]]
        path = os.path.join(OUT, f"{name}_M5.csv")
        full.to_csv(path, index=False)
        yrs = (full["time"].iloc[-1] - full["time"].iloc[0]).days / 365.25
        print(f"{name}: {len(full)} barre  {full['time'].iloc[0].date()} -> "
              f"{full['time'].iloc[-1].date()} ({yrs:.1f}y) -> {path}", flush=True)


if __name__ == "__main__":
    main()
