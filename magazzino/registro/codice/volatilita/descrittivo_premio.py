"""Forma del premio giornaliero di sviluppo (asimmetria e curtosi in eccesso). 0 trial.

Riproduce in codice versionato il descrittivo calcolato a mano il 13/11 (pre-registrazione §11, "Passo 2, dimensione
del premio"): fino al 27/11 viveva solo in un transcript di sessione. Debito segnalato dal gatekeeper sul passo 1 del
ridisegno (referto grandezze_volatilita_ridisegno_2026-11-24.md) e deciso in DECISIONS 2026-11-27 (2).

GUARDIA: la media e il segno del premio NON si calcolano e NON si stampano (la forma e' gia' vista; la media no).
Lo script riporta solo n, asimmetria e curtosi in eccesso, calcolate sulla serie riportata a media zero, e scrive
esiti/descrittivo_premio.json con il commit. Holdout chiuso (`premio_giornaliero(apri_holdout=False)`).

Uso: python magazzino/registro/codice/volatilita/descrittivo_premio.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path[:0] = [str(QUI)]

import controlli as C  # noqa: E402

CHIAVI_AMMESSE = {"descrittivo", "commit", "n", "asimmetria", "curtosi_eccesso", "nota"}


def forma(p: np.ndarray) -> dict:
    """Asimmetria e curtosi in eccesso (momenti di popolazione) di p riportata a media zero."""
    z = p - p.mean()                      # la media si toglie e non esce dalla funzione
    m2 = float(np.mean(z ** 2))
    return {"n": int(len(z)),
            "asimmetria": round(float(np.mean(z ** 3) / m2 ** 1.5), 2),
            "curtosi_eccesso": round(float(np.mean(z ** 4) / m2 ** 2 - 3.0), 1)}


def main() -> None:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=QUI).stdout.strip()
    esito = {"descrittivo": "forma_premio_sviluppo", "commit": commit,
             **forma(C.premio_giornaliero(apri_holdout=False).to_numpy()),
             "nota": "media e segno non calcolati per guardia; numeri gia' visti il 13/11"}
    assert set(esito) <= CHIAVI_AMMESSE, set(esito) - CHIAVI_AMMESSE
    (QUI / "esiti" / "descrittivo_premio.json").write_text(json.dumps(esito, indent=1), encoding="utf-8")
    print(json.dumps(esito, indent=1))


if __name__ == "__main__":
    main()
