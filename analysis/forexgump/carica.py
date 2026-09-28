"""Loader UNICO dei segnali di Forex Gump: qui, e solo qui, si converte l'orario in UTC.

Il fuso, misurato il 2026-09-28 con `fuso.py` (solo entrata postata contro prezzo, nessun esito):
l'export etichetta tutto `UTC+01:00`, ma l'orologio e' **l'ora italiana con l'ora legale**
(Europe/Rome). Con quella conversione l'entrata postata sta nel range dei 5 minuti prima del
messaggio nel 99,1% dei casi d'inverno e nel 98,8% d'estate; con qualunque altro offset sotto il 23%.
Credere all'etichetta avrebbe spostato di un'ora ogni segnale estivo.

Controprova indipendente: il messaggio del 28/09/2026 10:48:40 (export) = 08:48:40 UTC, e il log del
copier del socio apre il conto FTMO alle 08:48:46 UTC.

⚠️ Chi usa i segnali passa da `carica_segnali()`. **Non** riapplicare il fuso altrove: una correzione
applicata due volte produce numeri plausibili e sbagliati (fuso del mentore XAU, 18/09).
`verifica()` fallisce se l'allineamento si rompe (export nuovo con orologio diverso, feed diverso).
"""
from __future__ import annotations

import os

import pandas as pd

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "trading-bot-eval", "data")
FUSO_EXPORT = "Europe/Rome"
SOGLIA_DENTRO = 0.95        # sotto questa quota l'allineamento e' rotto: fermarsi


def carica_segnali(universo: bool = True) -> pd.DataFrame:
    """Segnali con `t_utc` (tz-naive, UTC). `universo=True`: solo bracket con SL, a mercato."""
    s = pd.read_csv(os.path.join(HERE, "signals.csv"))
    loc = pd.to_datetime(s.ts_export).dt.tz_localize(FUSO_EXPORT, ambiguous="NaT",
                                                      nonexistent="NaT")
    s["t_utc"] = loc.dt.tz_convert("UTC").dt.tz_localize(None)
    s = s.dropna(subset=["t_utc"])           # l'ora doppia del cambio d'ottobre: contata in verifica
    if universo:
        s = s[(~s.sl_missing) & (s.order_type == "market")]
    return s.reset_index(drop=True)


def carica_m1() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Barre M1 Dukascopy BID e ASK, indice UTC tz-naive (inizio barra)."""
    out = []
    for lato in ("bid", "ask"):
        d = pd.read_parquet(os.path.join(DATA, f"XAU_duka_M1_{lato}.parquet"))
        d.index = d.index.tz_convert("UTC").tz_localize(None)
        out.append(d)
    return out[0], out[1]


def verifica(s: pd.DataFrame | None = None) -> float:
    """Quota di entrate postate dentro il range eseguibile dei 5 minuti prima del messaggio."""
    s = carica_segnali() if s is None else s
    bid, ask = carica_m1()
    lo5 = bid["low"].rolling(5, min_periods=1).min()
    hi5 = ask["high"].rolling(5, min_periods=1).max()
    t = s.t_utc.dt.floor("min").values
    p = bid.index.searchsorted(t, side="right") - 1
    dentro = ((s.entry.values >= lo5.values[p] - 0.05) & (s.entry.values <= hi5.values[p] + 0.05)).mean()
    persi = len(carica_segnali(universo=False)) - len(pd.read_csv(os.path.join(HERE, "signals.csv")))
    print(f"allineamento: {dentro:.3f} delle entrate dentro il range dei 5 min "
          f"(soglia {SOGLIA_DENTRO}); segnali persi al cambio d'ora: {-persi}")
    assert dentro >= SOGLIA_DENTRO, "fuso o feed disallineati: non leggere nessuna metrica"
    return float(dentro)


if __name__ == "__main__":
    verifica()
