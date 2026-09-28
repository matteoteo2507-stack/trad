"""Scarica da Dukascopy l'oro (XAU/USD) a 1 minuto, lato BID e lato ASK, 2020-09 -> oggi.

Perche' serve un feed nuovo
---------------------------
Il feed M5 usato per il mentore XAU (`XAU_spot_M5_ext.csv`) parte il 2025-08-04, mentre
Forex Gump pubblica dal 2020-09-09. E la geometria e' molto piu' stretta: SL **2 $**
(TP 10 $) contro i 10 $ del mentore. Dentro una barra M5 l'oro si muove spesso piu' di 2 $,
quindi a M5 quasi ogni esito dipenderebbe dalla convenzione di pareggio, non dal mercato.

Perche' due lati
----------------
Con uno stop di 2 $ lo spread non e' un dettaglio: il 23/09/2026 alle 09:00 UTC valeva
0,59 $ = 0,3R. Un buy entra all'ASK ed esce al BID, un sell il contrario. Un replay su un
solo lato regala lo spread a ogni trade.

Timestamp: UTC (Dukascopy), inizio barra. Nessuna correzione di fuso qui.

Output: analysis/trading-bot-eval/data/XAU_duka_M1_{bid,ask}.parquet (data hub, ignorato da git).
Uso:    python analysis/forexgump/export_prices.py            # tutto, riprende da dove era
        python analysis/forexgump/export_prices.py --da 2026-09  # solo dai mesi indicati
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import time
from datetime import timezone

import pandas as pd

import dukascopy_python as dk
import dukascopy_python.instruments as ins

DATA = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
CACHE = os.path.join(DATA, "_duka_xau_m1_mesi")      # un file per mese: si riprende se cade
INIZIO = dt.date(2020, 9, 1)
LATI = {"bid": dk.OFFER_SIDE_BID, "ask": dk.OFFER_SIDE_ASK}
STRUMENTO = ins.INSTRUMENT_FX_METALS_XAU_USD


def _mesi(da: dt.date):
    y, m = da.year, da.month
    oggi = dt.date.today()
    while (y, m) <= (oggi.year, oggi.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _scarica_mese(lato: str, y: int, m: int, forza: bool) -> None:
    out = os.path.join(CACHE, f"{lato}_{y}-{m:02d}.parquet")
    corrente = (y, m) == (dt.date.today().year, dt.date.today().month)
    if os.path.exists(out) and not forza and not corrente:
        return
    s = dt.datetime(y, m, 1, tzinfo=timezone.utc)
    e = dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc)
    for tentativo in range(4):
        try:
            df = dk.fetch(STRUMENTO, dk.INTERVAL_MIN_1, LATI[lato], s, e)
            break
        except Exception as ex:  # noqa: BLE001 - rete: si riprova, poi si segnala
            print(f"  {lato} {y}-{m:02d}: errore {ex} (tentativo {tentativo + 1})", flush=True)
            time.sleep(5 * (tentativo + 1))
    else:
        print(f"  {lato} {y}-{m:02d}: RINUNCIO, mese mancante", flush=True)
        return
    df = df[["open", "high", "low", "close", "volume"]]
    df.to_parquet(out)
    print(f"  {lato} {y}-{m:02d}: {len(df)} barre", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--da", help="AAAA-MM: primo mese da (ri)scaricare")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    da = dt.date(*map(int, a.da.split("-")), 1) if a.da else INIZIO
    for y, m in _mesi(da):
        for lato in LATI:
            _scarica_mese(lato, y, m, forza=bool(a.da))
    for lato in LATI:
        parti = sorted(f for f in os.listdir(CACHE) if f.startswith(lato + "_"))
        full = pd.concat(pd.read_parquet(os.path.join(CACHE, f)) for f in parti)
        full = full[~full.index.duplicated(keep="last")].sort_index()
        out = os.path.join(DATA, f"XAU_duka_M1_{lato}.parquet")
        full.to_parquet(out)
        print(f"{lato}: {len(full)} barre {full.index.min()} -> {full.index.max()}  -> {out}")


if __name__ == "__main__":
    main()
