"""Prova dei rimedi di N2 su difetti SINTETICI, prima del commit di congelamento (riserva R4 dell'ottava passata). 0 trial.

Nessun dato di prezzo: processo inventato del §9, difetti dichiarati qui. Serve a scegliere la misura prima di ogni
dato (P6 del §8ter, punto 1: gratis) e a sapere se i rimedi elencati abbassano |δ|. Uscita: per ogni difetto e
misura, quantili di δ, rifiuti della guardia, esito; nient'altro.

python magazzino/registro/codice/struttura/prova_rimedi.py [repliche]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import simula_n2 as S  # noqa: E402

ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
T = 1450
SEME = 20261127            # seme proprio di questa prova (diverso da N2, verifica e positivo)
SETTE = S.POSITIVO_STRUMENTI


def difetto(quote: dict, rampa: bool = False, L: float = 3.0) -> dict:
    d = S.nessun_difetto(T, len(S.UNIVERSO))
    for nome, q in quote.items():
        i = S.UNIVERSO.index(nome)
        d["p0"][:, i] = np.linspace(0.0, q, T) if rampa else q
        d["L"][:, i] = L
    return d


DIFETTI = {
    "rampa_0_10_su_7": difetto({x: 0.10 for x in SETTE}, rampa=True),
    "fisso_5_su_7": difetto({x: 0.05 for x in SETTE}),
    "fisso_15_su_7": difetto({x: 0.15 for x in SETTE}),
    "fisso_5_su_17": difetto({x: 0.05 for x in S.UNIVERSO}),
}
MISURE = {"base_15m_B1": (1, 1), "i_15m_B2": (1, 2), "ii_30m_B1": (2, 1), "i+ii_30m_B2": (2, 2)}


def commit_pulito() -> str:
    sporco = subprocess.run(["git", "status", "--porcelain", "--", str(QUI)], cwd=ROOT, capture_output=True,
                            text=True, check=True).stdout.strip()
    if sporco:
        raise SystemExit("cartella di I3 non committata:\n" + sporco)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def main(argv):
    repliche = int(argv[0]) if argv else 60
    commit = commit_pulito()
    out = {"commit": commit, "T": T, "seme": SEME, "repliche": repliche, "prove": {}}
    for nd, d in DIFETTI.items():
        for nm, (passo, ritardi) in MISURE.items():
            out["prove"]["%s | %s" % (nd, nm)] = S.esegui(T, d, SEME, repliche, passo=passo, ritardi=ritardi,
                                                          processi=os.cpu_count())
            print(nd, nm, out["prove"]["%s | %s" % (nd, nm)]["esito"], flush=True)
    # rimedio (iii): difetto concentrato su BUND, poi BUND fuori dalla misura
    d = difetto({**{x: 0.05 for x in SETTE}, "BUND": 0.15})
    senza = [i for i, x in enumerate(S.UNIVERSO) if x != "BUND"]
    out["prove"]["bund_15_altri6_5 | base_15m_B1"] = S.esegui(T, d, SEME, repliche, processi=os.cpu_count())
    out["prove"]["bund_15_altri6_5 | iii_senza_BUND"] = S.esegui(T, d, SEME, repliche, colonne=senza,
                                                                processi=os.cpu_count())
    dest = QUI / "esiti" / "prove_rimedi_2026-11-23.json"
    dest.parent.mkdir(exist_ok=True)
    if dest.exists():
        raise SystemExit("%s esiste: non si riscrive" % dest.name)
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, dest)
    print("scritto", dest.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
