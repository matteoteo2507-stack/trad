"""Seconda prova dei rimedi di N2 su difetti SINTETICI: Bartlett con piu' ritardi (3, 4), a 15 e a 30 minuti. 0 trial.

Stesso processo, stessi difetti e stesso seme di `prova_rimedi.py`; nessun dato di prezzo. Uscita: quantili di δ,
guardia, esito.

python magazzino/registro/codice/struttura/prova_ritardi.py [repliche]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import prova_rimedi as PR  # noqa: E402
import simula_n2 as S  # noqa: E402

MISURE = {"15m_B3": (1, 3), "15m_B4": (1, 4), "30m_B3": (2, 3), "30m_B4": (2, 4)}
DIFETTI = ("fisso_5_su_7", "fisso_5_su_17", "rampa_0_10_su_7")


def main(argv):
    repliche = int(argv[0]) if argv else 60
    commit = PR.commit_pulito()
    out = {"commit": commit, "T": PR.T, "seme": PR.SEME, "repliche": repliche, "prove": {}}
    for nd in DIFETTI:
        for nm, (passo, ritardi) in MISURE.items():
            k = "%s | %s" % (nd, nm)
            out["prove"][k] = S.esegui(PR.T, PR.DIFETTI[nd], PR.SEME, repliche, passo=passo, ritardi=ritardi,
                                       processi=os.cpu_count())
            print(k, out["prove"][k]["esito"], flush=True)
    dest = QUI / "esiti" / "prove_ritardi_2026-11-23.json"
    if dest.exists():
        raise SystemExit("%s esiste: non si riscrive" % dest.name)
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, dest)


if __name__ == "__main__":
    main(sys.argv[1:])
