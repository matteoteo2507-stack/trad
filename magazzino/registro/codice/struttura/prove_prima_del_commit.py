"""Le due prove di N2 prima del commit di congelamento (referto §9), su soli dati sintetici. 0 trial.

1. Verifica del processo (seme 20261125): con 1.450 sedute e la pipeline intera, il gemello sincrono deve avere al
   massimo 25 repliche su 500 che rifiutano nella guardia, in entrambi gli orizzonti. Se no, (a, b) passa al tentativo
   successivo, in ordine fisso: (0,06; 0,93) -> (0,06; 0,90) -> (0,04; 0,94); al massimo tre.
2. Controllo positivo (seme 20261126): 5% fisso di prezzi fermi su tutti i 17 strumenti, durata della catena 3
   mezz'ore; la regola deve scattare (mediana di δ per la costante sotto −0,5 in almeno un orizzonte).

Uscita: `esiti/prove_prima_del_commit.json` (quantili di δ, rifiuti della guardia, esiti). Si rifiuta di partire se
la cartella non e' committata e di riscrivere un esito esistente.

python magazzino/registro/codice/struttura/prove_prima_del_commit.py
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
T = 1450
TENTATIVI = ((0.06, 0.93), (0.06, 0.90), (0.04, 0.94))
MARGINE = 25


def commit_pulito() -> str:
    sporco = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", str(QUI)], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout
    sporco = "\n".join(r for r in sporco.splitlines() if "__pycache__" not in r)
    if sporco:
        raise SystemExit("cartella di I3 non committata:\n" + sporco)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    dest = QUI / "esiti" / "prove_prima_del_commit.json"
    if dest.exists():
        raise SystemExit("%s esiste: non si riscrive" % dest.name)
    out = {"commit": commit_pulito(), "T": T, "repliche": S.REPLICHE, "verifica": [], "positivo": None}
    scelto = None
    for a, b in TENTATIVI:
        r = S.esegui(T, S.nessun_difetto(T, len(S.UNIVERSO)), S.SEME_VERIFICA, a=a, b=b, processi=os.cpu_count())
        ok = all(r["guardia_rifiuti_h%d" % h] <= MARGINE for h in (1, 5)) and r["esito"] != "GUASTO"
        out["verifica"].append({"a": a, "b": b, "guardia_rifiuti_h1": r["guardia_rifiuti_h1"],
                                "guardia_rifiuti_h5": r["guardia_rifiuti_h5"], "non_valide": r["non_valide"],
                                "campione_insufficiente": r["campione_insufficiente"], "passa": ok})
        print("verifica", a, b, "passa" if ok else "non passa", flush=True)
        if ok:
            scelto = (a, b)
            break
    out["processo_scelto"] = scelto
    if scelto is not None:
        r = S.esegui(T, S.difetto_positivo(T), S.SEME_POSITIVO, a=scelto[0], b=scelto[1], processi=os.cpu_count())
        scatta = r["esito"] == "RIFIUTA per misura"
        out["positivo"] = {**r, "scatta": scatta}
        print("positivo", r["esito"], flush=True)
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, dest)
    print("scritto", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
