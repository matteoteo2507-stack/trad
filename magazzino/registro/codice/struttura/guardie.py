"""Guardie di I3 (requisiti del commit (1), punto 2, del referto del passo 2). 0 trial.

In testa a ogni script che legge dati, ferme al primo errore:
1. i percorsi protetti esistono e non hanno modifiche non committate; hash del commit in ogni esito;
2. versioni di Python e librerie fissate;
3. sha256 **e byte** dei 9 M5 della volatilita' contro `volatilita/hash_dati.json` (letto, mai riscritto) e degli 8
   nuovi contro `struttura/hash_dati.json` (scritto una volta sola dallo scaricatore, `--registra`);
4. per gli 8 nuovi, l'ultima barra non oltre il 2026-11-10 (i 9 vecchi arrivano all'11/11 e li taglia il loader alla
   lettura, `dati.TAGLIO_UTC`);
5. `python -m motore.core.trial_ledger --check` esce a 0;
6. l'ordine dei passi: ogni script dichiara quali esiti committati gli servono (`richiedi`).

`verifica(git=False)` salta i controlli di git: **solo nei test**, mai in una corsa che produce numeri (gli script la
chiamano senza argomenti).
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
HASH_VOL = ROOT / "magazzino/registro/codice/volatilita/hash_dati.json"
HASH_I3 = QUI / "hash_dati.json"
ESITI = QUI / "esiti"

VECCHI = ("SPX500", "NAS100", "DOW", "RUSSELL", "DAX", "XAUUSD", "XAGUSD", "WTI", "EURUSD")
NUOVI = ("BUND", "USTBOND", "USDJPY", "GBPUSD", "AUDUSD", "COPPER", "NATGAS", "BTCUSD")
CARTELLA_VECCHI = "motore/data/prezzi/volatilita_m5"
CARTELLA_NUOVI = "motore/data/prezzi/struttura_m5"
DATI = {**{n: "%s/%s_M5.csv" % (CARTELLA_VECCHI, n) for n in VECCHI},
        **{n: "%s/%s_M5.csv" % (CARTELLA_NUOVI, n) for n in NUOVI}}
ULTIMO_GIORNO_NUOVI = "2026-11-10"

PROTETTI = (
    "magazzino/registro/referti/proprieta_I3_struttura_2026-11-21.md",
    "motore/metodo/STRATEGY_LIFECYCLE.md",
    "decisioni/trial_ledger.json",
    "magazzino/registro/codice/struttura",
    "motore/core",
    "motore/tests",
    "magazzino/registro/codice/volatilita/hash_dati.json",
    "uscita/volatilita_ewma/v1",
)
VERSIONI = {"numpy": "2.4.4", "pandas": "3.0.2", "scipy": "1.17.1", "exchange_calendars": "4.13.2"}
PYTHON = (3, 12)


class GuardiaFallita(RuntimeError):
    """Errore di una guardia: il messaggio non contiene mai valori di prezzi, rendimenti o perdite."""


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


def _sporchi(percorsi) -> list:
    righe = _git("status", "--porcelain", "--untracked-files=all", "--", *percorsi).splitlines()
    return [r for r in righe if "__pycache__" not in r]


def controlla_git() -> str:
    sporchi = _sporchi(PROTETTI)
    if sporchi:
        raise GuardiaFallita("modifiche non committate nei percorsi protetti:\n" + "\n".join(sporchi))
    return _git("rev-parse", "HEAD").strip()


def versioni() -> dict:
    import importlib

    out = {"python": "%d.%d.%d" % sys.version_info[:3]}
    for nome in VERSIONI:
        out[nome] = importlib.import_module(nome).__version__
    return out


def controlla_versioni() -> dict:
    v = versioni()
    diverse = [n for n, att in VERSIONI.items() if v[n] != att]
    if diverse or sys.version_info[:2] != PYTHON:
        raise GuardiaFallita("versioni diverse da quelle fissate: %s" % (diverse or "python"))
    return v


def _registro(percorso: Path) -> dict:
    if not percorso.exists():
        raise GuardiaFallita("manca %s" % percorso.name)
    return json.loads(percorso.read_text(encoding="utf-8"))


def controlla_dati(nomi=None) -> dict:
    """sha256 e byte di ogni file contro il suo registro; per gli 8 nuovi anche l'ultima data."""
    nomi = tuple(nomi or DATI)
    vol, i3 = _registro(HASH_VOL), _registro(HASH_I3)
    out = {}
    for n in nomi:
        reg = vol if n in VECCHI else i3
        p = ROOT / DATI[n]
        if not p.exists():
            raise GuardiaFallita("%s: file mancante" % n)
        if os.path.getsize(p) != reg["byte"].get(n) or sha256(p) != reg["sha256"].get(n):
            raise GuardiaFallita("%s: byte o sha256 diversi dal registro" % n)
        if n in NUOVI and ultima_data(p) > ULTIMO_GIORNO_NUOVI:
            raise GuardiaFallita("%s: barre oltre il %s" % (n, ULTIMO_GIORNO_NUOVI))
        out[n] = reg["sha256"][n]
    return out


def ultima_data(percorso: Path) -> str:
    """Data (AAAA-MM-GG) dell'ultima riga: legge solo la coda del file, nessun prezzo."""
    with open(percorso, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - 4096))
        coda = f.read().decode("utf-8").strip().splitlines()
    return coda[-1].split(",")[0][:10]


def controlla_contatore() -> None:
    r = subprocess.run([sys.executable, "-m", "motore.core.trial_ledger", "--check"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise GuardiaFallita("trial_ledger --check non e' a zero")


def richiedi(*esiti: str) -> None:
    """Ordine dei passi: ogni file in `esiti` (relativo a `esiti/`) deve esistere ed essere committato."""
    mancanti = [e for e in esiti if not (ESITI / e).exists()]
    if mancanti:
        raise GuardiaFallita("passi precedenti mancanti: %s" % mancanti)
    sporchi = _sporchi([str(ESITI / e) for e in esiti])
    if sporchi:
        raise GuardiaFallita("esiti precedenti non committati: %s" % sporchi)


def verifica(nomi=None, git: bool = True, dati: bool = True) -> dict:
    """Tutte le guardie. `git=False` solo nei test."""
    controlla_percorsi()
    commit = controlla_git() if git else None
    v = controlla_versioni()
    sha = controlla_dati(nomi) if dati else {}
    if git:
        controlla_contatore()
    return {"commit": commit, "versioni": v, "sha256": sha}


def protetto(funzione):
    """Lancia `funzione` e, se fallisce, riporta solo il tipo dell'errore (e il messaggio delle guardie, che non
    contiene valori): nessun numero esce da un messaggio d'errore (requisito 4, "nessun canale")."""
    try:
        return funzione()
    except GuardiaFallita as e:
        raise SystemExit("GUARDIA: %s" % e) from None
    except Exception as e:  # noqa: BLE001
        raise SystemExit("ERRORE: %s (messaggio non riportato)" % type(e).__name__) from None


def controlla_chiavi(uscita: dict, ammesse: set, percorso: str = "") -> None:
    """Ferma lo script se l'uscita ha una chiave non ammessa **a questo livello**: ogni script controlla i suoi
    sottodizionari con il loro insieme di chiavi (riserva R9 dell'undicesima)."""
    extra = set(uscita) - ammesse
    if extra:
        raise GuardiaFallita("chiavi non ammesse in uscita%s: %s" % (percorso, sorted(map(str, extra))))


def leggi_esito(nome: str) -> dict:
    return json.loads((ESITI / nome).read_text(encoding="utf-8"))


def catena_guasta(prefissi, nome_esito) -> None:
    """Bloccante B1 dell'undicesima: una configurazione corretta del generatore si usa solo se **ogni** configurazione
    precedente della catena ha una verifica committata con esito GUASTO."""
    for p in prefissi:
        nome = nome_esito(p)
        richiedi(nome)
        if leggi_esito(nome).get("esito") != "GUASTO":
            raise GuardiaFallita("%s non e' GUASTO: la correzione successiva non si applica" % nome)


def scrivi_esito(nome: str, uscita: dict) -> Path:
    """Scrive `esiti/<nome>` una volta sola (file temporaneo e sostituzione); rifiuta se esiste."""
    dest = ESITI / nome
    if dest.exists():
        raise GuardiaFallita("%s esiste: non si riscrive" % nome)
    ESITI.mkdir(exist_ok=True)
    testo = json.dumps(uscita, indent=1, ensure_ascii=False) + "\n"
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(testo, encoding="utf-8", newline="\n")
    os.replace(tmp, dest)
    return dest
