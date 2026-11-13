"""Giorni di borsa, rendimenti e bersaglio della famiglia `volatilita` (pre-registrazione §3). 0 trial.

Da barre M5 Dukascopy (bid, ora d'inizio della barra, UTC) a una tabella giornaliera con:
- `r`  rendimento del modello in %  (indici: log(P_ch,t / P_ch,t-1); 24 ore: log(close ultima / open prima barra));
- `v`  bersaglio in %²              (indici: notte² + somma dei quadrati di seduta; 24 ore: somma dei quadrati);
- `barre`, `attese`, `escluso` (meno del 90% delle barre attese), `apertura_mancante` (indici: manca la barra che
  inizia all'apertura del calendario; P_ap e' allora l'open della prima barra della seduta, e r resta esatto).

**Holdout.** Il caricatore legge le righe in ordine e si ferma alla prima con ora >= `TAGLIO_UTC` (domenica
2024-11-10 00:00 UTC): nessuna barra dell'holdout entra in memoria come dato. L'ultimo giorno di sviluppo e' venerdi'
2024-11-08 per tutti gli strumenti; il primo giorno dell'holdout (lunedi' 2024-11-11) comincia per gli strumenti a 24
ore domenica alle 17:00 New York, dopo il taglio. Leggere oltre richiede `HOLDOUT_APERTO = True`, che cambia solo nel
commit del passo 8 del §7.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
CARTELLA = ROOT / "motore/data/prezzi/volatilita_m5"

HOLDOUT_INIZIO = pd.Timestamp("2024-11-11")
TAGLIO_UTC = pd.Timestamp("2024-11-10 00:00")
HOLDOUT_APERTO = False
INIZIO = pd.Timestamp("2015-01-02")

CALENDARI = {"SPX500": "XNYS", "NAS100": "XNYS", "DOW": "XNYS", "RUSSELL": "XNYS", "DAX": "XETR"}
H24 = ("XAUUSD", "XAGUSD", "WTI", "EURUSD")
STRUMENTI = tuple(CALENDARI) + H24
SOGLIA_COMPLETO = 0.90
BARRA = pd.Timedelta(minutes=5)


def leggi_barre(nome: str, fino_a: pd.Timestamp | None = None, percorso: Path | None = None) -> pd.DataFrame:
    """Barre M5 fino a `fino_a` escluso (default: il taglio dello sviluppo). Si ferma al primo blocco oltre il taglio."""
    fino_a = TAGLIO_UTC if fino_a is None else pd.Timestamp(fino_a)
    if fino_a > TAGLIO_UTC and not HOLDOUT_APERTO:
        raise PermissionError("holdout sigillato: lettura oltre %s rifiutata" % TAGLIO_UTC)
    percorso = CARTELLA / f"{nome}_M5.csv" if percorso is None else percorso
    pezzi = []
    for blocco in pd.read_csv(percorso, usecols=["time", "open", "close"], chunksize=200_000):
        blocco["time"] = pd.to_datetime(blocco["time"])
        dentro = blocco[blocco["time"] < fino_a]
        pezzi.append(dentro)
        if len(dentro) < len(blocco):
            break
    df = pd.concat(pezzi, ignore_index=True)
    if not df["time"].is_monotonic_increasing or df["time"].duplicated().any():
        raise ValueError("%s: tempi non ordinati o duplicati" % nome)
    return df


def _lr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return 100.0 * np.log(a / b)


def giorni_indice(barre: pd.DataFrame, calendario: str, inizio=INIZIO, fine=None) -> pd.DataFrame:
    """Sedute del calendario `exchange_calendars`; barre con inizio in [apertura, chiusura)."""
    import exchange_calendars as xc

    fine = barre["time"].iloc[-1].normalize() if fine is None else pd.Timestamp(fine)
    sched = xc.get_calendar(calendario).schedule.loc[inizio - pd.Timedelta(days=10):fine]
    ap = sched["open"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy()
    ch = sched["close"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy()
    t = barre["time"].to_numpy()
    o = barre["open"].to_numpy(float)
    c = barre["close"].to_numpy(float)
    i0 = np.searchsorted(t, ap, side="left")
    i1 = np.searchsorted(t, ch, side="left")          # barre che iniziano prima della chiusura
    righe = []
    chiusura_prec = np.nan
    for k, data in enumerate(sched.index):
        a, b = i0[k], i1[k]
        attese = int((ch[k] - ap[k]) / np.timedelta64(5, "m"))
        n = b - a
        if n == 0:
            righe.append((data, np.nan, np.nan, np.nan, 0, attese, True, True))
            continue
        p_ap = o[a]
        mancante = t[a] != ap[k]
        seduta = np.concatenate([[_lr(c[a], o[a])], _lr(c[a + 1:b], c[a:b - 1])])
        notte = _lr(p_ap, chiusura_prec) if np.isfinite(chiusura_prec) else np.nan
        r = notte + seduta.sum()
        v = notte ** 2 + np.sum(seduta ** 2)
        righe.append((data, r, v, notte, n, attese, n < SOGLIA_COMPLETO * attese, bool(mancante)))
        chiusura_prec = c[b - 1]
    df = pd.DataFrame(righe, columns=["data", "r", "v", "notte", "barre", "attese", "escluso", "apertura_mancante"])
    return df.set_index("data").loc[inizio:]


def giorni_24h(barre: pd.DataFrame, inizio=INIZIO) -> pd.DataFrame:
    """Giorno D = barre con inizio in [17:00 New York di D-1, 17:00 New York di D); il blocco che apre la domenica e'
    il giorno del lunedi'. Il rendimento a cavallo della pausa e del fine settimana non entra."""
    ny = barre["time"].dt.tz_localize("UTC").dt.tz_convert("America/New_York")
    etichetta = (ny + pd.Timedelta(hours=7)).dt.tz_localize(None).dt.normalize()
    dopo = (etichetta >= inizio).to_numpy()
    weekend = dopo & (etichetta.dt.dayofweek >= 5).to_numpy()   # barre fra venerdi' 17:00 e domenica 17:00 NY
    tieni = dopo & ~weekend
    barre, etichetta = barre[tieni], etichetta[tieni]
    o = barre["open"].to_numpy(float)
    c = barre["close"].to_numpy(float)
    g = etichetta.to_numpy()
    cambi = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    fini = np.r_[cambi[1:], len(g)]
    righe = []
    for a, b in zip(cambi, fini):
        data = pd.Timestamp(g[a])
        ritorni = np.concatenate([[_lr(c[a], o[a])], _lr(c[a + 1:b], c[a:b - 1])])
        n = b - a
        righe.append((data, ritorni.sum(), np.sum(ritorni ** 2), np.nan, n, 288, n < SOGLIA_COMPLETO * 288, False))
    df = pd.DataFrame(righe, columns=["data", "r", "v", "notte", "barre", "attese", "escluso", "apertura_mancante"])
    df = df.set_index("data")
    df.attrs["barre_weekend_scartate"] = int(weekend.sum())
    return df


def carica(nome: str, fino_a: pd.Timestamp | None = None) -> pd.DataFrame:
    barre = leggi_barre(nome, fino_a)
    if nome in CALENDARI:
        fine = (pd.Timestamp(fino_a) if fino_a is not None else TAGLIO_UTC).normalize() - pd.Timedelta(days=1)
        df = giorni_indice(barre, CALENDARI[nome], fine=fine)
    else:
        df = giorni_24h(barre)
    if not HOLDOUT_APERTO and (df.index >= HOLDOUT_INIZIO).any():
        raise AssertionError("un giorno dell'holdout e' entrato nello sviluppo")
    if nome == "RUSSELL":
        df = df.loc[df["barre"].gt(0).idxmax():]        # prima dell'agosto 2018 non ci sono dati
        df = df.iloc[1:]                                # il primo giorno non ha la chiusura precedente
    if df["r"].isna().any() or df["v"].isna().any():
        raise ValueError("%s: r o v mancanti in %s" % (nome, list(df.index[df["r"].isna()].date)))
    return df


def carica_vix(fino_a: pd.Timestamp | None = None) -> pd.Series:
    fino_a = HOLDOUT_INIZIO if fino_a is None else pd.Timestamp(fino_a)
    if fino_a > HOLDOUT_INIZIO and not HOLDOUT_APERTO:
        raise PermissionError("holdout sigillato")
    s = pd.read_csv(ROOT / "motore/data/cache/free/VIX_D1.csv", parse_dates=["time"]).set_index("time")["close"]
    return s.loc[:fino_a - pd.Timedelta(days=1)]
