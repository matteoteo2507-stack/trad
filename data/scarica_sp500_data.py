"""Scarica lo storico S&P 500 senza survivorship di `Johnbrick123/sp500-data` (strato azionario USA, 05/11/2026).

Perche' questa fonte: prezzi giornalieri di tutti i membri dell'indice dal 1970, delistati compresi, con
l'appartenenza giorno per giorno (ricerca dati del 25/10, magazzino/registro/referti/ricerca_dati_2026-10-25.md §2).

Regole:
- si scarica una release **congelata** (`snapshot-AAAA-MM`), mai la release mobile, cosi' un test sa su quale versione
  ha girato; le impronte sha256 finiscono in `MANIFEST.json` accanto ai file;
- i dati restano in `data/cache/sp500data/` (fuori da git): il repo **non dichiara una licenza**, quindi si usano in
  locale e non si ridistribuiscono;
- `no_trade_days.csv` e `exit_gaps.csv` esistono solo nella release mobile `data`: si scaricano da li' e il manifesto
  registra la data. Il README del dataset chiede di usarli in ogni backtest (giorni senza scambi, uscite in gap).

Uso:
    python data/scarica_sp500_data.py                 # snapshot di default
    python data/scarica_sp500_data.py --snapshot snapshot-2026-12
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = "https://github.com/Johnbrick123/sp500-data/releases/download"
SNAPSHOT_DEFAULT = "snapshot-2026-11"
FILE_SNAPSHOT = ["prices.parquet", "members.parquet", "membership_intervals.parquet",
                 "recycled_tickers.csv", "verification_report.txt"]
FILE_MOBILI = ["no_trade_days.csv", "exit_gaps.csv"]


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def _scarica(url: str, dest: str) -> None:
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "trad-research"})
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        while True:
            blocco = r.read(1 << 20)
            if not blocco:
                break
            f.write(blocco)
    os.replace(tmp, dest)          # il file finale esiste solo se il download e' completo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=SNAPSHOT_DEFAULT)
    a = ap.parse_args(argv)
    out = os.path.join(ROOT, "data", "cache", "sp500data", a.snapshot)
    os.makedirs(out, exist_ok=True)
    manifesto = {"fonte": "https://github.com/Johnbrick123/sp500-data", "licenza": "non dichiarata: solo uso locale",
                 "snapshot": a.snapshot, "scaricato": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "file": {}}
    for nome, tag in [(n, a.snapshot) for n in FILE_SNAPSHOT] + [(n, "data") for n in FILE_MOBILI]:
        dest = os.path.join(out, nome)
        if not os.path.exists(dest):
            print("scarico %s (%s)" % (nome, tag), flush=True)
            _scarica("%s/%s/%s" % (BASE, tag, nome), dest)
        manifesto["file"][nome] = {"release": tag, "byte": os.path.getsize(dest), "sha256": _sha256(dest)}
    with open(os.path.join(out, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)
    print("fatto: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
