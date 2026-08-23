"""Estrazione D1 storico lungo da Dukascopy — feed OMOGENEO per il test trend/playground.

Perche' un feed unico: i CSV in data/ mescolano finestre diverse (major FX dal 2003, il resto
dal 2020) E broker diversi. Confrontare gruppi di asset su quei dati misura il calendario e il
feed, non l'asset. Qui si scarica TUTTO dalla stessa fonte, stessa granularita', stessa finestra.

Universo scelto A PRIORI per coprire il gradiente liquidita'/volatilita' del claim Kichev
(forex = massima liquidita'/minimo edge -> agricoli/crypto = minima liquidita'/massimo edge),
e per colmare il buco dichiarato dalla pre-registrazione TSMOM (niente bond, niente commodities).

Output: analysis/trading-bot-eval/data/dukascopy_d1/{SYM}_D1.csv  (NON sovrascrive il feed broker)

Uso: python analysis/trend/export_d1.py [anno_inizio]
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from datetime import timezone

import pandas as pd

import dukascopy_python as dk
import dukascopy_python.instruments as ins

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "trading-bot-eval", "data", "dukascopy_d1")

# (nome, codice, gruppo a priori) — il gruppo e' dichiarato QUI, prima di vedere qualunque numero
UNIVERSE = [
    # --- FX majors: liquidita' massima, volatilita' minima (Kichev: edge piu' basso) ---
    ("EURUSD", ins.INSTRUMENT_FX_MAJORS_EUR_USD, "fx_major"),
    ("GBPUSD", ins.INSTRUMENT_FX_MAJORS_GBP_USD, "fx_major"),
    ("USDJPY", ins.INSTRUMENT_FX_MAJORS_USD_JPY, "fx_major"),
    ("AUDUSD", ins.INSTRUMENT_FX_MAJORS_AUD_USD, "fx_major"),
    ("USDCAD", ins.INSTRUMENT_FX_MAJORS_USD_CAD, "fx_major"),
    ("NZDUSD", ins.INSTRUMENT_FX_MAJORS_NZD_USD, "fx_major"),
    ("USDCHF", ins.INSTRUMENT_FX_MAJORS_USD_CHF, "fx_major"),
    # --- FX crosses ---
    ("EURJPY", ins.INSTRUMENT_FX_CROSSES_EUR_JPY, "fx_cross"),
    ("GBPJPY", ins.INSTRUMENT_FX_CROSSES_GBP_JPY, "fx_cross"),
    ("EURGBP", ins.INSTRUMENT_FX_CROSSES_EUR_GBP, "fx_cross"),
    # --- indici azionari ---
    ("NAS100", ins.INSTRUMENT_IDX_AMERICA_E_NQ_100, "index"),
    ("SPX500", ins.INSTRUMENT_IDX_AMERICA_E_SANDP_500, "index"),
    # --- bond (mai avuti prima: buco dichiarato dalla prereg TSMOM) ---
    ("BUND", ins.INSTRUMENT_BND_CFD_BUND_TR_EUR, "bond"),
    ("UKGILT", ins.INSTRUMENT_BND_CFD_UKGILT_TR_GBP, "bond"),
    ("USTBOND", ins.INSTRUMENT_BND_CFD_USTBOND_TR_USD, "bond"),
    # --- metalli preziosi e industriali ---
    ("XAUUSD", ins.INSTRUMENT_FX_METALS_XAU_USD, "metal"),
    ("XAGUSD", ins.INSTRUMENT_FX_METALS_XAG_USD, "metal"),
    ("COPPER", ins.INSTRUMENT_CMD_METALS_COPPER_CMD_USD, "metal"),
    ("XPT", ins.INSTRUMENT_CMD_METALS_XPT_CMD_USD, "metal"),
    ("XPD", ins.INSTRUMENT_CMD_METALS_XPD_CMD_USD, "metal"),
    # --- energia ---
    ("BRENT", ins.INSTRUMENT_CMD_ENERGY_E_BRENT, "energy"),
    ("WTI", ins.INSTRUMENT_CMD_ENERGY_E_LIGHT, "energy"),
    ("NATGAS", ins.INSTRUMENT_CMD_ENERGY_GAS_CMD_USD, "energy"),
    # --- agricoli: liquidita' minima fra i CFD (Kichev: edge piu' alto) ---
    ("COCOA", ins.INSTRUMENT_CMD_AGRICULTURAL_COCOA_CMD_USD, "agri"),
    ("COFFEE", ins.INSTRUMENT_CMD_AGRICULTURAL_COFFEE_CMD_USX, "agri"),
    ("COTTON", ins.INSTRUMENT_CMD_AGRICULTURAL_COTTON_CMD_USX, "agri"),
    ("SOYBEAN", ins.INSTRUMENT_CMD_AGRICULTURAL_SOYBEAN_CMD_USX, "agri"),
    ("SUGAR", ins.INSTRUMENT_CMD_AGRICULTURAL_SUGAR_CMD_USD, "agri"),
    # --- crypto: volatilita' massima ---
    ("BTCUSD", ins.INSTRUMENT_VCCY_BTC_USD, "crypto"),
    ("ETHUSD", ins.INSTRUMENT_VCCY_ETH_USD, "crypto"),
]


def fetch_symbol(name, code, y0, y1):
    frames = []
    for y in range(y0, y1):
        s = dt.datetime(y, 1, 1, tzinfo=timezone.utc)
        e = dt.datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        if s > dt.datetime.now(timezone.utc):
            break
        try:
            df = dk.fetch(code, dk.INTERVAL_DAY_1, dk.OFFER_SIDE_BID, s, e)
        except Exception as ex:  # noqa: BLE001
            print(f"    {name} {y}: {type(ex).__name__} {ex}", flush=True)
            continue
        if df is not None and len(df):
            frames.append(df)
    if not frames:
        return None
    full = pd.concat(frames)
    full = full[~full.index.duplicated(keep="last")].sort_index()
    full = full.rename_axis("time").reset_index()
    full["time"] = pd.to_datetime(full["time"], utc=True).dt.tz_localize(None)
    return full[["time", "open", "high", "low", "close", "volume"]]


def main():
    y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2012
    y1 = 2027
    os.makedirs(OUT, exist_ok=True)
    print(f"Dukascopy D1 {y0}-> | universo {len(UNIVERSE)} strumenti | out={OUT}\n")
    rows = []
    for name, code, grp in UNIVERSE:
        df = fetch_symbol(name, code, y0, y1)
        if df is None or len(df) < 100:
            print(f"  {name:8} [{grp:9}] NESSUN DATO utile", flush=True)
            rows.append({"sym": name, "group": grp, "n": 0, "start": None, "end": None})
            continue
        path = os.path.join(OUT, f"{name}_D1.csv")
        df.to_csv(path, index=False)
        print(f"  {name:8} [{grp:9}] n={len(df):5}  "
              f"{df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}", flush=True)
        rows.append({"sym": name, "group": grp, "n": len(df),
                     "start": df["time"].iloc[0].date(), "end": df["time"].iloc[-1].date()})
    rep = pd.DataFrame(rows)
    rep.to_csv(os.path.join(OUT, "_coverage.csv"), index=False)
    ok = rep[rep["n"] > 0]
    if len(ok):
        print(f"\nStrumenti utili: {len(ok)}/{len(rep)}")
        print(f"Inizio comune (max degli start): {ok['start'].max()}")
        print("Per gruppo:")
        for g, gg in ok.groupby("group"):
            print(f"  {g:9} n_strumenti={len(gg)}  start piu' tardivo={gg['start'].max()}")


if __name__ == "__main__":
    main()
