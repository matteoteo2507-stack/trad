"""Controllo positivo di N2 all'orizzonte di 5 sedute (bloccante B2 della nona passata; DECISIONS 2026-11-24 (5)). 0 trial.

Un solo tentativo, regola scritta prima nel referto (§9): stesso difetto del controllo positivo (5% fisso di prezzi
fermi su tutti i 17 strumenti, catena di 3 quarti d'ora), serie di **14.500 sedute** (10 × 1.450), 500 repliche,
**seme 20261130**, mai usato. Scatta se a h = 5 l'orizzonte **non decade** e la mediana di δ per la costante e' sotto
−0,5. Se non scatta, h = 5 esce da I3. Soli dati sintetici.

Uscita: `esiti/prova_positivo_h5_2026-11-24.json` (chiavi di `simula_n2.riassumi`, versioni, esito della prova). Si
rifiuta di partire se la cartella non e' committata e di riscrivere un esito esistente.

python magazzino/registro/codice/struttura/prova_positivo_h5.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import simula_n2 as S  # noqa: E402

ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
T = 14_500
SEME = 20261130


def commit_pulito() -> str:
    sporco = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", str(QUI)], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout
    sporco = "\n".join(r for r in sporco.splitlines() if "__pycache__" not in r)
    if sporco:
        raise SystemExit("cartella di I3 non committata:\n" + sporco)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def versioni() -> dict:
    import numpy
    import scipy

    return {"python": sys.version.split()[0], "numpy": numpy.__version__, "scipy": scipy.__version__}


def main():
    dest = QUI / "esiti" / "prova_positivo_h5_2026-11-24.json"
    if dest.exists():
        raise SystemExit("%s esiste: non si riscrive" % dest.name)
    out = {"commit": commit_pulito(), "versioni": versioni(), "T": T, "seme": SEME, "repliche": S.REPLICHE}
    r = S.esegui(T, S.difetto_positivo(T), SEME, processi=os.cpu_count())
    mediana = r["delta_costante_h5"][2] if r["delta_costante_h5"] else None
    scatta = (5 not in r["orizzonti_decaduti"]) and mediana is not None and mediana < -S.TAU
    out["risultato"] = r
    out["h5_scatta"] = bool(scatta)
    out["conseguenza"] = "h = 5 resta in I3" if scatta else "h = 5 esce da I3"
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, dest)
    print(out["conseguenza"], "| scritto", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
