"""Scarica gli archivi SEC dei Form 3, 4 e 5 (Insider Transactions Data Sets) ed estrae gli acquisti e le vendite sul
mercato aperto (strato azionario USA, 05/11/2026; famiglia insider, BACKLOG D9).

Fonte: https://www.sec.gov/dera/data/form-345, un file zip per trimestre dal 2006 Q1. Dati pubblici della SEC.

La SEC rifiuta le richieste senza un contatto nel User-Agent (403, verificato il 05/11). Il contatto **non sta nel
codice** (il repo e' pubblico): si legge da `motore/data/cache/sec/user_agent.txt` (fuori da git) o dalla variabile
d'ambiente SEC_USER_AGENT. Una richiesta al secondo, sotto il limite di 10 della SEC.

Output (fuori da git):
- `motore/data/cache/sec/form345/<AAAA>q<N>_form345.zip`: gli archivi originali, riscaricati solo se mancano;
- `motore/data/cache/sec/form345_mercato.parquet`: una riga per operazione con codice P (acquisto sul mercato aperto) o
  S (vendita sul mercato aperto), con data dell'operazione e data del deposito, emittente, insider e ruolo.

Il file del deposito non dice l'ora di accettazione: la data del segnale, in un test, e' il giorno dopo FILING_DATE
(prudente: un deposito accettato dopo la chiusura e' noto solo il giorno dopo).

Uso:
    python motore/data/scarica_sec_form345.py                  # dal 2006q1 all'ultimo trimestre pubblicato
    python motore/data/scarica_sec_form345.py --fino 2026q3
"""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import zipfile

import pandas as pd

ROOT = next(str(p) for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())
OUT = os.path.join(ROOT, "motore/data/cache/sec")
URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/%s_form345.zip"
COL_SUB = ["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL"]
COL_OWN = ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE"]
COL_TR = ["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_SHARES", "TRANS_PRICEPERSHARE",
          "TRANS_ACQUIRED_DISP_CD", "SHRS_OWND_FOLWNG_TRANS", "DIRECT_INDIRECT_OWNERSHIP"]


def user_agent() -> str:
    ua = os.environ.get("SEC_USER_AGENT")
    p = os.path.join(OUT, "user_agent.txt")
    if not ua and os.path.exists(p):
        ua = open(p, encoding="utf-8").read().strip()
    if not ua or "@" not in ua:
        sys.exit("manca il contatto per la SEC: scrivi 'nome email' in motore/data/cache/sec/user_agent.txt")
    return ua


def trimestri(dal: str, al: str) -> list:
    a, qa = int(dal[:4]), int(dal[-1])
    b, qb = int(al[:4]), int(al[-1])
    out = []
    while (a, qa) <= (b, qb):
        out.append("%dq%d" % (a, qa))
        a, qa = (a + 1, 1) if qa == 4 else (a, qa + 1)
    return out


def scarica(q: str, ua: str) -> str | None:
    dest = os.path.join(OUT, "form345", "%s_form345.zip" % q)
    if os.path.exists(dest):
        return dest
    req = urllib.request.Request(URL % q, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            dati = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None                     # trimestre non ancora pubblicato
        raise
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        f.write(dati)
    os.replace(tmp, dest)
    time.sleep(1.0)
    return dest


def _tabella(z: zipfile.ZipFile, nome: str, colonne: list) -> pd.DataFrame:
    with z.open(nome) as f:
        return pd.read_csv(io.TextIOWrapper(f, encoding="latin1"), sep="\t", usecols=colonne, dtype=str,
                           quoting=3, on_bad_lines="warn")


def estrai(path: str, q: str) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        tr = _tabella(z, "NONDERIV_TRANS.tsv", COL_TR)
        tr = tr[tr.TRANS_CODE.isin(["P", "S"])]
        sub = _tabella(z, "SUBMISSION.tsv", COL_SUB)
        own = _tabella(z, "REPORTINGOWNER.tsv", COL_OWN)
    # un deposito puo' avere piu' insider (depositi congiunti): si tiene il primo e si conta quanti sono
    n_own = own.groupby("ACCESSION_NUMBER").size().rename("N_OWNERS")
    own = own.drop_duplicates("ACCESSION_NUMBER").join(n_own, on="ACCESSION_NUMBER")
    df = tr.merge(sub, on="ACCESSION_NUMBER", how="left").merge(own, on="ACCESSION_NUMBER", how="left")
    for c in ("TRANS_DATE", "FILING_DATE"):
        df[c] = pd.to_datetime(df[c], format="%d-%b-%Y", errors="coerce")
    for c in ("TRANS_SHARES", "TRANS_PRICEPERSHARE", "SHRS_OWND_FOLWNG_TRANS"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["TRIMESTRE"] = q
    return df


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dal", default="2006q1")
    ap.add_argument("--fino", default="2026q3")
    a = ap.parse_args(argv)
    os.makedirs(os.path.join(OUT, "form345"), exist_ok=True)
    ua = user_agent()
    parti, mancanti = [], []
    for q in trimestri(a.dal, a.fino):
        p = scarica(q, ua)
        if p is None:
            mancanti.append(q)
            continue
        parti.append(estrai(p, q))
        print("%s: %d operazioni P/S" % (q, len(parti[-1])), flush=True)
    df = pd.concat(parti, ignore_index=True)
    dest = os.path.join(OUT, "form345_mercato.parquet")
    df.to_parquet(dest + ".tmp", index=False)
    os.replace(dest + ".tmp", dest)
    print("fatto: %d righe, %s -> %s; trimestri non pubblicati: %s"
          % (len(df), df.FILING_DATE.min().date(), df.FILING_DATE.max().date(), ", ".join(mancanti) or "nessuno"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
