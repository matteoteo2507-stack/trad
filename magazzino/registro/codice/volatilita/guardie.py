"""Guardie della famiglia `volatilita` (pre-registrazione §7 passo 0). 0 trial.

Prima di ogni corsa `verifica()` controlla, e si ferma al primo problema:
1. che i percorsi protetti **esistano** (una guardia su percorsi spariti passerebbe a vuoto);
2. che non abbiano modifiche non committate (`git status --porcelain`), e registra l'hash del commit;
3. che le versioni delle librerie siano quelle del §2;
4. che lo sha256 dei nove file M5 e del VIX sia quello registrato in `hash_dati.json` all'approvazione
   (i CSV sono fuori da git: un nuovo scarico cambierebbe i dati senza traccia).

`python magazzino/registro/codice/volatilita/guardie.py --registra` scrive `hash_dati.json` una volta sola: se il file
esiste si rifiuta. L'hash si calcola sui byte, holdout compreso: non e' una statistica sui prezzi.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
FILE_HASH = QUI / "hash_dati.json"

STRUMENTI = ("SPX500", "NAS100", "DOW", "RUSSELL", "DAX", "XAUUSD", "XAGUSD", "WTI", "EURUSD")
DATI = {n: f"motore/data/prezzi/volatilita_m5/{n}_M5.csv" for n in STRUMENTI}
DATI["VIX"] = "motore/data/cache/free/VIX_D1.csv"

PROTETTI = (
    "magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md",
    "decisioni/trial_ledger.json",
    "magazzino/registro/codice/volatilita",
    "motore/core",
    "motore/tests",
)

VERSIONI = {
    "arch": "8.0.0",
    "statsmodels": "0.14.6",
    "numpy": "2.4.4",
    "scipy": "1.17.1",
    "pandas": "3.0.2",
    "exchange_calendars": "4.13.2",
}
PYTHON = (3, 12)


class GuardiaFallita(RuntimeError):
    pass


def sha256(percorso: Path, blocco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        while True:
            b = f.read(blocco)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def controlla_percorsi() -> None:
    mancanti = [p for p in PROTETTI if not (ROOT / p).exists()]
    if mancanti:
        raise GuardiaFallita("percorsi protetti inesistenti: %s" % mancanti)


def controlla_git() -> str:
    sporchi = _git("status", "--porcelain", "--untracked-files=all", "--", *PROTETTI).strip()
    # i __pycache__ non sono codice: git li ignora gia' se il .gitignore li esclude; se compaiono, si segnalano
    if sporchi:
        raise GuardiaFallita("modifiche non committate nei percorsi protetti:\n" + sporchi)
    return _git("rev-parse", "HEAD").strip()


def controlla_versioni() -> dict:
    import importlib

    trovate = {}
    for nome, attesa in VERSIONI.items():
        v = importlib.import_module(nome).__version__
        trovate[nome] = v
        if v != attesa:
            raise GuardiaFallita("%s %s, la pre-registrazione dice %s" % (nome, v, attesa))
    if sys.version_info[:2] != PYTHON:
        raise GuardiaFallita("Python %d.%d, la pre-registrazione dice %d.%d" % (*sys.version_info[:2], *PYTHON))
    return trovate


def hash_correnti() -> dict:
    return {n: sha256(ROOT / p) for n, p in DATI.items()}


def controlla_dati() -> dict:
    if not FILE_HASH.exists():
        raise GuardiaFallita("manca %s: va registrato all'approvazione (--registra)" % FILE_HASH.name)
    registrati = json.loads(FILE_HASH.read_text(encoding="utf-8"))["sha256"]
    correnti = hash_correnti()
    diversi = [n for n in DATI if registrati.get(n) != correnti[n]]
    if diversi or set(registrati) != set(DATI):
        raise GuardiaFallita("dati cambiati rispetto a hash_dati.json: %s" % (diversi or "insiemi diversi"))
    return correnti


def verifica(git: bool = True) -> dict:
    """Tutte le guardie. `git=False` solo per i test unitari della pipeline, mai per una corsa che produce numeri."""
    controlla_percorsi()
    commit = controlla_git() if git else None
    versioni = controlla_versioni()
    dati = controlla_dati()
    return {"commit": commit, "versioni": versioni, "sha256": dati}


def registra() -> None:
    if FILE_HASH.exists():
        raise GuardiaFallita("%s esiste gia': non si riscrive" % FILE_HASH.name)
    controlla_percorsi()
    righe = {"nota": "sha256 dei dati della famiglia volatilita' all'approvazione della pre-registrazione (13/11/2026), "
                     "§7 passo 0. Si ricalcola a ogni corsa (guardie.py).",
             "percorsi": DATI,
             "byte": {n: os.path.getsize(ROOT / p) for n, p in DATI.items()},
             "sha256": hash_correnti()}
    tmp = FILE_HASH.with_suffix(".tmp")
    tmp.write_text(json.dumps(righe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, FILE_HASH)


if __name__ == "__main__":
    if "--registra" in sys.argv:
        registra()
        print("registrato", FILE_HASH.relative_to(ROOT))
    else:
        esito = verifica()
        print("guardie OK, commit", esito["commit"])
