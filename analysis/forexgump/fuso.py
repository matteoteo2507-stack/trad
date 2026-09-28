"""Calibrazione del fuso dell'export di Forex Gump (pre-registrazione §3.1).

L'export etichetta ogni messaggio `UTC+01:00`, estate e inverno: e' l'orologio
dell'esportatore, non l'ora vera. Qui si misura quale offset allinea i messaggi al feed
Dukascopy (UTC), usando **solo l'entrata postata**, mai l'esito: non contamina il test.

Per ogni offset candidato h (l'orologio dell'export sta h ore avanti a UTC):
  - `scarto`  : |entrata postata − prezzo medio (bid+ask)/2 alla chiusura del minuto del messaggio|
  - `dentro5` : quota di segnali la cui entrata sta nel range [min, max] dei 5 minuti prima del
                messaggio (il mentore scrive "ho venduto a X": X deve essere un prezzo appena visto)
Separatamente per **ora solare** e **ora legale** (Europa), per vedere se l'esportatore la segue.

Il risultato va scritto **una volta sola** nel loader (feedback: una correzione, un proprietario).

Uso: python analysis/forexgump/fuso.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "trading-bot-eval", "data")
OFFSETS = range(-3, 5)          # ore di anticipo dell'orologio dell'export su UTC


def carica_mid() -> pd.DataFrame:
    b = pd.read_parquet(os.path.join(DATA, "XAU_duka_M1_bid.parquet"))
    a = pd.read_parquet(os.path.join(DATA, "XAU_duka_M1_ask.parquet"))
    m = pd.DataFrame({"lo": b["low"], "hi": a["high"],            # range eseguibile del minuto
                      "mid": (b["close"] + a["close"]) / 2}).dropna()
    m.index = m.index.tz_convert("UTC").tz_localize(None)
    return m


def main() -> None:
    s = pd.read_csv(os.path.join(HERE, "signals.csv"))
    s = s[(~s.sl_missing) & (s.order_type == "market")].copy()
    s["t_exp"] = pd.to_datetime(s.ts_export)
    # ora legale europea sull'istante nominale (etichetta UTC+1 → UTC → Europe/Rome)
    rome = (s.t_exp - pd.Timedelta(hours=1)).dt.tz_localize("UTC").dt.tz_convert("Europe/Rome")
    s["legale"] = rome.map(lambda x: bool(x.dst()))
    m = carica_mid()
    idx = m.index
    lo5 = m["lo"].rolling(5, min_periods=1).min()
    hi5 = m["hi"].rolling(5, min_periods=1).max()

    righe = []
    for h in OFFSETS:
        t = (s.t_exp - pd.Timedelta(hours=h)).dt.floor("min")
        pos = idx.searchsorted(t.values, side="right") - 1          # ultimo minuto <= t
        ok = (pos >= 0) & (np.abs((idx[np.clip(pos, 0, None)] - t.values).total_seconds()) < 600)
        p = np.clip(pos, 0, None)
        scarto = np.abs(s.entry.values - m["mid"].values[p])
        dentro = (s.entry.values >= lo5.values[p] - 0.05) & (s.entry.values <= hi5.values[p] + 0.05)
        for leg in (False, True):
            k = ok & (s.legale.values == leg)
            righe.append({"offset_h": h, "periodo": "legale" if leg else "solare", "n": int(k.sum()),
                          "scarto_mediano_$": round(float(np.median(scarto[k])), 2) if k.any() else None,
                          "dentro_5min": round(float(dentro[k].mean()), 3) if k.any() else None})
    r = pd.DataFrame(righe)
    for per in ("solare", "legale"):
        print(f"\n--- ora {per} ---")
        print(r[r.periodo == per].drop(columns="periodo").to_string(index=False))
    senza = (~((s.t_exp - pd.Timedelta(hours=1)).dt.floor("min").isin(idx))).mean()
    print(f"\nquota di messaggi senza barra esatta all'offset nominale: {senza:.3f} (weekend/buchi del feed)")


if __name__ == "__main__":
    main()
