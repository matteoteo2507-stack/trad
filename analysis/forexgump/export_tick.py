"""Scarica i tick Dukascopy XAU/USD (BID e ASK) nelle finestre dei segnali di Forex Gump.

Pre-registrazione `docs/FOREXGUMP_LATENCY_PREREGISTRATION.md` §3-§4: tick in [messaggio − 10 min,
messaggio + 85 min] per ogni segnale dell'universo, per riempire all'istante giusto (messaggio + L) e
risolvere la prima ora d'uscita senza pareggi intrabar. Oltre l'ora si passa alle barre M1.

Solo dati: nessun esito viene calcolato qui. Gli istanti dei segnali vengono dal loader unico
(`carica.py`, fuso Europe/Rome), mai riconvertiti qui.

Cache: un file parquet per ORA UTC in `analysis/trading-bot-eval/data/_duka_xau_tick_ore/`, cosi' lo
scarico riprende da dove si era fermato. Un'ora senza tick (mercato chiuso) si salva vuota.

Uso: python analysis/forexgump/export_tick.py            # tutte le ore mancanti
     python analysis/forexgump/export_tick.py --conta    # solo quante ore servono / mancano
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time
from datetime import timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from analysis.forexgump.carica import DATA, carica_segnali  # noqa: E402

CACHE = os.path.join(DATA, "_duka_xau_tick_ore")
PRIMA, DOPO = pd.Timedelta(minutes=10), pd.Timedelta(minutes=85)   # 85: latenza max 300 s + limite (15 min) + uscite su tick (60 min) + margine (G1 #3)


def ore_necessarie() -> list[pd.Timestamp]:
    s = carica_segnali()
    ore = set()
    for t in s.t_utc:
        h = (t - PRIMA).floor("h")
        while h <= t + DOPO:
            ore.add(h)
            h += pd.Timedelta(hours=1)
    return sorted(ore)


def _file(h: pd.Timestamp) -> str:
    return os.path.join(CACHE, h.strftime("%Y%m%d_%H") + ".parquet")


def scarica(h: pd.Timestamp) -> int:
    import dukascopy_python as dk
    import dukascopy_python.instruments as ins
    s = h.to_pydatetime().replace(tzinfo=timezone.utc)
    for tentativo in range(4):
        try:
            df = dk.fetch(ins.INSTRUMENT_FX_METALS_XAU_USD, dk.INTERVAL_TICK, dk.OFFER_SIDE_BID,
                          s, s + dt.timedelta(hours=1))
            break
        except Exception as ex:  # noqa: BLE001 - rete: si riprova, poi si segnala
            print(f"  {h}: errore {ex} (tentativo {tentativo + 1})", flush=True)
            time.sleep(3 * (tentativo + 1))
    else:
        return -1
    if df is None or not len(df):
        df = pd.DataFrame({"bidPrice": [], "askPrice": []})
    else:
        df = df[["bidPrice", "askPrice"]]
    df.to_parquet(_file(h))
    return len(df)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conta", action="store_true")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    ore = ore_necessarie()
    mancanti = [h for h in ore if not os.path.exists(_file(h))]
    print(f"ore necessarie: {len(ore)}   gia' in cache: {len(ore) - len(mancanti)}   da scaricare: {len(mancanti)}", flush=True)
    if a.conta:
        return 0
    falliti = 0
    for i, h in enumerate(mancanti, 1):
        n = scarica(h)
        falliti += n < 0
        if i % 100 == 0 or n < 0:
            print(f"  {i}/{len(mancanti)}  {h}  tick={n}", flush=True)
    print(f"FINE: scaricate {len(mancanti) - falliti}, fallite {falliti}", flush=True)
    return 0 if falliti == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
