"""Scarica le serie GRATUITE del backlog G4 (VIX) e G5 (posizionamento CFTC) in data/cache/free/.

Perche' esiste
--------------
Righe G4 e G5 di [`docs/BACKLOG_RICERCA.md`](../docs/BACKLOG_RICERCA.md): due dati gratis,
mai scaricati. Sbloccano D5 (regime da VIX) e D7 (affollamento / posizionamento) **come
dati**, non come ipotesi: nessuna delle due ha ancora una pre-registrazione, e scaricarle
non consuma trial.

Fonti (verificate il 2026-10-03)
--------------------------------
- VIX: CBOE `VIX_History.csv` (giornaliero dal 1990).
- COT Legacy, solo futures: CFTC `deacot1986_2016.zip` + `deacot<anno>.zip` (settimanale, dal 1986).
- COT Disaggregated, solo futures: CFTC `fut_disagg_txt_hist_2006_2016.zip` +
  `fut_disagg_txt_<anno>.zip` (dal 2006).
FRED (`VIXCLS`, `DTWEXBGS`) non risponde da questa macchina (timeout, 03/10): non e' usato.

Output (ignorato da git, come tutta `data/cache/`)
--------------------------------------------------
    data/cache/free/VIX_D1.csv
    data/cache/free/cot_legacy_fut.parquet
    data/cache/free/cot_disagg_fut.parquet
    data/cache/free/_zip/...            copie grezze dei file CFTC

Un nuovo download **sostituisce** il precedente (nomi fissi): non ci sono versioni da scegliere.

    python data/scarica_serie_libere.py            # tutto
    python data/scarica_serie_libere.py --solo vix
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import sys
import urllib.request
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "data", "cache", "free")
ZIP = os.path.join(OUT, "_zip")

URL_VIX = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
CFTC = "https://www.cftc.gov/files/dea/history/"
COT = {
    # nome: (archivio storico, modello del file annuale, primo anno annuale, colonna data)
    "legacy": ("deacot1986_2016.zip", "deacot{y}.zip", 2017,
               "As of Date in Form YYYY-MM-DD"),
    "disagg": ("fut_disagg_txt_hist_2006_2016.zip", "fut_disagg_txt_{y}.zip", 2017,
               "Report_Date_as_YYYY-MM-DD"),
}
COL_MERCATO = "CFTC_Contract_Market_Code"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def vix() -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(_get(URL_VIX)))
    df.columns = [c.strip().lower() for c in df.columns]
    df["time"] = pd.to_datetime(df["date"], format="%m/%d/%Y")
    df = df[["time", "open", "high", "low", "close"]].sort_values("time")
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "VIX_D1.csv"), index=False)
    return df


def _leggi_zip(blob: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".txt"))
        with z.open(nome) as f:
            return pd.read_csv(f, low_memory=False)


def cot(tipo: str) -> pd.DataFrame:
    storico, annuale, primo, col_data = COT[tipo]
    os.makedirs(ZIP, exist_ok=True)
    nomi = [storico] + [annuale.format(y=y) for y in range(primo, dt.date.today().year + 1)]
    parti = []
    for n in nomi:
        blob = _get(CFTC + n)
        with open(os.path.join(ZIP, n), "wb") as f:
            f.write(blob)
        parti.append(_leggi_zip(blob))
    # legacy usa spazi nei nomi di colonna, disaggregated underscore: si normalizza
    for p in parti:
        p.columns = [c.strip().replace(" ", "_") for c in p.columns]
    df = pd.concat(parti, ignore_index=True)
    df["time"] = pd.to_datetime(df[col_data.replace(" ", "_")])
    # l'archivio storico e i file annuali si sovrappongono ai bordi: una riga per mercato e data
    prima = len(df)
    df = df.drop_duplicates(subset=[COL_MERCATO, "time"], keep="last")
    df = df.sort_values([COL_MERCATO, "time"])
    for c in df.columns:                       # parquet non accetta colonne miste
        if df[c].dtype == object:
            df[c] = df[c].astype(str)
    df.to_parquet(os.path.join(OUT, "cot_%s_fut.parquet" % tipo), index=False)
    df.attrs["duplicati_rimossi"] = prima - len(df)
    return df


def _report_vix(df: pd.DataFrame) -> None:
    buchi = df["time"].diff().dt.days
    i = buchi.idxmax()
    print("VIX  %d barre  %s -> %s  buco massimo %d giorni, fino al %s (ponti festivi attesi <= 4)"
          % (len(df), df.time.iloc[0].date(), df.time.iloc[-1].date(), int(buchi.max()),
             df.time[i].date()))
    per_anno = df.groupby(df.time.dt.year).size()
    corti = per_anno[(per_anno < 245) & (per_anno.index < dt.date.today().year)]
    if len(corti):
        print("  anni con meno di 245 barre:", dict(corti))


def _report_cot(tipo: str, df: pd.DataFrame) -> None:
    ultimo = df["time"].max()
    print("COT %-6s %d righe, %d mercati, %s -> %s, duplicati di bordo rimossi: %d"
          % (tipo, len(df), df[COL_MERCATO].nunique(), df.time.min().date(), ultimo.date(),
             df.attrs.get("duplicati_rimossi", 0)))
    ritardo = (pd.Timestamp(dt.date.today()) - ultimo).days
    if ritardo > 14:
        print("  ATTENZIONE: ultimo report vecchio di %d giorni (atteso <= 10)" % ritardo)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["vix", "cot"])
    a = ap.parse_args(argv)
    if a.solo in (None, "vix"):
        _report_vix(vix())
    if a.solo in (None, "cot"):
        for tipo in COT:
            _report_cot(tipo, cot(tipo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
