"""Verifica del generatore dei difetti (referto §9, bloccante B1 dell'ottava e della nona passata). 0 trial.

Gira **prima** di N2 e non simula nessuna replica di N2: confronta, cella per cella, le sedute escluse vere (dal
controllo di struttura) con quelle che il generatore fa escludere su **200 anni simulati** per anno.
- celle: strumento × anno (sedute escluse dello strumento) e anno (sedute escluse per unione), sull'universo;
- un anno con meno di 60 sedute si unisce all'anno vicino (il primo al successivo, gli altri al precedente): ogni
  sotto-anno si simula coi suoi parametri, i conteggi si sommano, q̂ e' la quota pesata;
- una cella **fallisce** se il p bilaterale binomiale del conteggio vero k sotto Bin(n; q̂) e' sotto 0,05 / celle;
- esito PASSA o GUASTO; N2 parte solo da un esito PASSA committato.
Correzioni (deviazioni P5, in ordine): `--correzioni 1,2` ecc.; ogni configurazione ha il suo seme.

python magazzino/registro/codice/struttura/verifica_generatore.py [--correzioni 1,2,3,4]
    -> esiti/verifica_generatore_c<correzioni>.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import difetti as DF  # noqa: E402
import guardie as G  # noqa: E402
import misura as M  # noqa: E402
import simula_n2 as S  # noqa: E402

ANNI_SIMULATI = 200
MIN_SEDUTE_ANNO = 60
ALFA = 0.05
SEMI = {(): 20261140, (1,): 20261141, (1, 2): 20261142, (1, 2, 3): 20261143, (1, 2, 3, 4): 20261144}
CHIAVI = {"commit", "versioni", "seme", "correzioni", "anni_simulati", "celle", "soglia_p", "fallite", "esito"}


def nome_esito(correzioni) -> str:
    return "verifica_generatore_c%s.json" % ("".join(map(str, correzioni)) or "0")


def gruppi_di_anni(sedute_per_anno: dict) -> list:
    """Anni ordinati, uniti quando hanno meno di MIN_SEDUTE_ANNO sedute: lista di liste di anni."""
    anni = sorted(sedute_per_anno)
    gruppi = [[a] for a in anni]
    k = 0
    while k < len(gruppi):
        n = sum(sedute_per_anno[a] for a in gruppi[k])
        if n < MIN_SEDUTE_ANNO and len(gruppi) > 1:
            j = k + 1 if k == 0 else k - 1
            gruppi[j] = sorted(gruppi[j] + gruppi[k])
            del gruppi[k]
            k = 0
            continue
        k += 1
    return gruppi


def esclusi_simulati(conteggi, universo, anno: str, n_sedute: int, correzioni, rng) -> tuple:
    """(esclusi per strumento, esclusi per unione) su n_sedute sedute simulate con i parametri dell'anno."""
    anni = np.array([anno] * n_sedute)
    d = DF.da_conteggi(conteggi, universo, anni, correzioni)
    X = np.cumsum(rng.standard_normal((n_sedute, S.N_PREZZI, len(universo))), axis=1)
    X[:, 0] = 0.0
    Y = S.applica_difetti(X, rng, d)
    it = S.estrai_interrotti(rng, d)
    r, oss = M.rendimenti(Y, 1, it)
    v = M.validi_strumento(r, oss)
    return (~v).sum(axis=0), int((~v.all(axis=1)).sum())


def p_bilaterale(k: int, n: int, q: float) -> float:
    q = min(max(q, 0.0), 1.0)
    if q == 0.0:
        return 1.0 if k == 0 else 0.0
    if q == 1.0:
        return 1.0 if k == n else 0.0
    return float(stats.binomtest(k, n, q).pvalue)


def verifica(conteggi: dict, correzioni=(), anni_simulati: int = ANNI_SIMULATI, seme: int | None = None) -> dict:
    c = DF.controlla_correzioni(correzioni)
    seme = SEMI[c] if seme is None else seme
    rng = np.random.default_rng(seme)
    universo = list(conteggi["universo"])
    an = conteggi["anni"]["sviluppo"]
    sedute = {a: an[a]["sedute"] for a in an}
    celle = {}
    for gruppo in gruppi_di_anni(sedute):
        nome = "+".join(gruppo)
        n = sum(sedute[a] for a in gruppo)
        k_str = np.zeros(len(universo), int)
        k_uni = 0
        sim_str = np.zeros(len(universo))
        sim_uni = 0.0
        for a in gruppo:
            k_str += np.array([conteggi["strumenti"][u]["sviluppo"][a]["sedute_escluse"] for u in universo])
            k_uni += an[a]["escluse_unione"]
            es, eu = esclusi_simulati(conteggi, universo, a, anni_simulati * sedute[a], c, rng)
            sim_str += es
            sim_uni += eu
        tot = anni_simulati * n
        for i, u in enumerate(universo):
            q = sim_str[i] / tot
            celle["%s|%s" % (u, nome)] = {"k": int(k_str[i]), "n": int(n), "q_sim": round(float(q), 6),
                                          "p": p_bilaterale(int(k_str[i]), n, q)}
        q = sim_uni / tot
        celle["unione|%s" % nome] = {"k": int(k_uni), "n": int(n), "q_sim": round(float(q), 6),
                                     "p": p_bilaterale(int(k_uni), n, q)}
    soglia = ALFA / len(celle)
    fallite = sorted(k for k, v in celle.items() if v["p"] < soglia)
    return {"seme": seme, "correzioni": list(c), "anni_simulati": anni_simulati, "celle": celle,
            "soglia_p": soglia, "fallite": fallite, "esito": "GUASTO" if fallite else "PASSA"}


def main() -> None:
    corr = ()
    if "--correzioni" in sys.argv:
        corr = tuple(int(x) for x in sys.argv[sys.argv.index("--correzioni") + 1].split(","))
    g = G.verifica(dati=False)
    G.richiedi("controllo_struttura.json")
    if not G.HASH_I3.exists() or G._sporchi([str(G.HASH_I3)]):
        raise G.GuardiaFallita("hash degli 8 nuovi mancanti o non committati")
    conteggi = json.loads((G.ESITI / "controllo_struttura.json").read_text(encoding="utf-8"))
    out = {"commit": g["commit"], "versioni": g["versioni"], **verifica(conteggi, corr)}
    G.controlla_chiavi(out, CHIAVI)
    dest = G.scrivi_esito(nome_esito(corr), out)
    print("scritto", dest.relative_to(G.ROOT), "|", out["esito"], "| celle fallite", len(out["fallite"]))


if __name__ == "__main__":
    G.protetto(main)
