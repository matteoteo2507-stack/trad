"""Esporta l'universo ricerca-livelli da MT5 (broker FP Markets demo4) + REPORT DI QUALITA'.

Per ogni simbolo esporta D1 e H1 (OHLC + tick_volume) in
analysis/trading-bot-eval/data/{PREFIX}_{TF}.csv e stampa un report di qualita'
(n. barre, span, storia in anni, gap piu' grande, gap "sospetti" > 3 giorni) cosi'
verifichiamo la validita' dei dati PRIMA di fidarci. I nomi simbolo sono quelli del
broker dell'utente (metalli con suffisso .cyr); adattali se il tuo broker differisce.

Uso: python analysis/trading-bot-eval/export_mt5_universe.py   (terminale MT5 connesso)
"""
from __future__ import annotations

import os
import sys

import pandas as pd

OUT = "analysis/trading-bot-eval/data"

# (simbolo_broker, prefisso_file, classe)  — classe solo informativa nel report
SYMBOLS = [
    ("EURUSD", "EURUSD", "fx"), ("GBPUSD", "GBPUSD", "fx"), ("USDJPY", "USDJPY", "fx"),
    ("AUDUSD", "AUDUSD", "fx"), ("USDCAD", "USDCAD", "fx"), ("NZDUSD", "NZDUSD", "fx"),
    ("USDCHF", "USDCHF", "fx"), ("EURJPY.r", "EURJPY.r", "fx"), ("GBPJPY.r", "GBPJPY.r", "fx"),
    ("EURGBP.r", "EURGBP.r", "fx"),
    ("XAUUSD.cyr", "XAUUSD", "metal-cfd"), ("XAGUSD.cyr", "XAGUSD", "metal-cfd"),
    ("BTCUSD", "BTCUSD", "crypto"), ("ETHUSD", "ETHUSD", "crypto"),
    ("US500", "US500", "index-cfd"), ("US100", "US100", "index-cfd"),
]
WANT = [("D1", "TIMEFRAME_D1", 6000), ("H1", "TIMEFRAME_H1", 90000)]


def _quality(df):
    """(anni, gap_max_ore, n_gap_sospetti>3g) sull'indice temporale."""
    if len(df) < 3:
        return (0.0, 0.0, 0)
    span_days = (df.index[-1] - df.index[0]).total_seconds() / 86400
    diffs = df.index.to_series().diff().dropna()
    gap_max_h = diffs.max().total_seconds() / 3600
    susp = int((diffs > pd.Timedelta(days=3)).sum())   # buchi che NON sono weekend
    return (span_days / 365.25, gap_max_h, susp)


def main() -> int:
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        print("MetaTrader5 non installato (serve il PC con MT5)."); return 1
    if not mt5.initialize():
        print("MT5 initialize() fallito:", mt5.last_error()); return 1
    os.makedirs(OUT, exist_ok=True)
    report = []
    try:
        for sym, prefix, cls in SYMBOLS:
            if not mt5.symbol_select(sym, True):
                print(f"[SKIP] symbol_select({sym}) fallito: {mt5.last_error()} "
                      f"-> aggiusta il nome per il tuo broker")
                report.append((prefix, cls, "SIMBOLO NON TROVATO", "", "", ""))
                continue
            row_h1 = None
            for suf, tfname, count in WANT:
                rates = mt5.copy_rates_from_pos(sym, getattr(mt5, tfname), 0, count)
                if rates is None or len(rates) == 0:
                    print(f"  {sym} {suf}: nessun dato ({mt5.last_error()})"); continue
                df = pd.DataFrame(rates)
                df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_localize(None)
                df = df.set_index("time")
                df["volume"] = df["tick_volume"]
                df = df[["open", "high", "low", "close", "volume"]]
                df.to_csv(f"{OUT}/{prefix}_{suf}.csv")
                if suf == "H1":
                    yrs, gaph, susp = _quality(df)
                    row_h1 = (prefix, cls, f"{len(df)}", f"{yrs:.1f}y",
                              f"gapmax {gaph:.0f}h", f"buchi>3g: {susp}")
                    flag = " ⚠️" if (yrs < 3 or susp > 5) else ""
                    print(f"  {sym:14} H1: {len(df):6} barre  {df.index[0].date()}->"
                          f"{df.index[-1].date()}  {yrs:.1f}y  gapmax={gaph:.0f}h  buchi>3g={susp}{flag}")
            if row_h1:
                report.append(row_h1)
    finally:
        mt5.shutdown()

    print("\n===== REPORT QUALITA' (H1) =====")
    print(f"{'symbol':10} {'classe':10} {'barre':>8} {'storia':>7} {'gapmax':>10} {'buchi':>10}")
    for r in report:
        print(f"{r[0]:10} {r[1]:10} {r[2]:>8} {r[3]:>7} {r[4]:>10} {r[5]:>10}")
    print("\nNOTE: ⚠️ = storia <3 anni o >5 buchi (>3 giorni) = dati insufficienti/bucati.")
    print("CFD (index-cfd/metal-cfd) = prezzo-broker sintetico; volume = tick-volume (proxy).")
    print("Prossimo: incrocio i close recenti vs riferimento pubblico per validare il feed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
