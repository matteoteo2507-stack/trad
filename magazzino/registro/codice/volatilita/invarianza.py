"""Test d'invarianza al futuro (pre-registrazione §7 passo 1, bloccante). 0 trial.

Per ogni strumento e ogni modello o riferimento, la previsione **finale** (h = 1 e h = 5, riscalata con c_t dove si
applica) all'origine t, calcolata sulla serie vera e sulla stessa serie con r e v dopo t sostituiti da rumore, deve
essere identica entro 1e-10.

Origini: 20 a caso fra quelle di sviluppo (seme 20261118), piu' un giorno di ristima scelto a caso, il giorno prima e
quello dopo. Le prime origini dell'holdout (le prime tre e la prima ristima dell'holdout con i suoi vicini) si provano su
una serie **sintetica** lunga quanto lo sviluppo piu' 12 giorni: l'holdout resta chiuso, contano solo le posizioni.
Si calcolano solo i blocchi che contengono l'origine (`origini=`), con 20 partenze per l'HMM come nella corsa vera.

Uso: python magazzino/registro/codice/volatilita/invarianza.py [--processi 8]
Scrive il riepilogo in `esiti/invarianza.json` (nessun prezzo, solo le differenze massime) e le previsioni alle origini
in `motore/data/cache/volatilita/invarianza_previsioni.npz` (fuori da git: per il confronto con la corsa di sviluppo).
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))

import giorni as G  # noqa: E402
import modelli as M  # noqa: E402
import pipeline as P  # noqa: E402

TOLLERANZA = 1e-10
SEME = 20261118
CACHE = G.ROOT / "motore/data/cache/volatilita"


def origini_sviluppo(n: int, rng) -> list:
    ultima = n - 1 - 5                                       # il bersaglio a 5 giorni sta nello sviluppo
    casuali = sorted(int(t) for t in rng.choice(np.arange(M.W - 1, ultima + 1), 20, replace=False))
    ristime = np.arange(M.W - 1 + M.PASSO, ultima, M.PASSO)
    t0 = int(rng.choice(ristime))
    return casuali + [t0 - 1, t0, t0 + 1]


def origini_holdout(n_dev: int) -> list:
    prima_ristima = M.W - 1 + -(-(n_dev - (M.W - 1)) // M.PASSO) * M.PASSO
    return sorted({n_dev, n_dev + 1, n_dev + 2, prima_ristima - 1, prima_ristima, prima_ristima + 1})


def sintetica(n: int, seme: int):
    """GJR gaussiano (omega 0,02, alpha 0,03, gamma 0,10, beta 0,90) e v = r² con rumore lognormale: solo posizioni."""
    rng = np.random.default_rng(seme)
    r = np.empty(n)
    s2 = 1.0
    for t in range(n):
        r[t] = np.sqrt(s2) * rng.standard_normal()
        s2 = 0.02 + (0.03 + 0.10 * (r[t] < 0)) * r[t] ** 2 + 0.90 * s2
    v = r ** 2 * np.exp(0.6 * rng.standard_normal(n) - 0.18) + 1e-4
    return r, v


def con_rumore(r, v, t, seme):
    rng = np.random.default_rng(seme)
    r2, v2 = r.copy(), v.copy()
    k = len(r) - t - 1
    r2[t + 1:] = rng.standard_normal(k) * 5.0
    v2[t + 1:] = np.exp(rng.standard_normal(k) * 2.0)
    return r2, v2


def _compito(args):
    nome, tipo, t, r, v = args
    t_inizio = time.time()
    out = P.previsioni(r, v, origini=[t])["previsioni"]
    return nome, tipo, t, {m: out[m][t].tolist() for m in out}, time.time() - t_inizio


def main():
    import guardie
    controllo = guardie.verifica()
    print("guardie OK, commit", controllo["commit"], flush=True)
    processi = int(sys.argv[sys.argv.index("--processi") + 1]) if "--processi" in sys.argv else os.cpu_count()
    rng = np.random.default_rng(SEME)
    compiti = []
    for i, nome in enumerate(G.STRUMENTI):
        d = G.carica(nome)
        r, v = d["r"].to_numpy(), d["v"].to_numpy()
        for t in origini_sviluppo(len(r), rng):
            r2, v2 = con_rumore(r, v, t, SEME + 1000 * i + t)
            compiti += [(nome, "vera", t, r, v), (nome, "rumore", t, r2, v2)]
        rs, vs = sintetica(len(r) + 12, SEME + i)
        for t in origini_holdout(len(r)):
            r2, v2 = con_rumore(rs, vs, t, SEME + 1000 * i + t + 7)
            compiti += [(nome, "sint_vera", t, rs, vs), (nome, "sint_rumore", t, r2, v2)]
    print("compiti", len(compiti), "processi", processi, flush=True)
    risultati = {}
    with Pool(processi) as pool:
        for j, (nome, tipo, t, prev, sec) in enumerate(pool.imap_unordered(_compito, compiti), 1):
            risultati[(nome, tipo, t)] = prev
            if j % 20 == 0:
                print("%d/%d (ultimo %.0fs)" % (j, len(compiti), sec), flush=True)

    riepilogo, peggiore = {}, 0.0
    salva = {}
    for (nome, tipo, t), prev in risultati.items():
        if tipo not in ("vera", "sint_vera"):
            continue
        altra = risultati[(nome, tipo.replace("vera", "rumore"), t)]
        for m, val in prev.items():
            a, b = np.array(val), np.array(altra[m])
            diff = float(np.max(np.abs(a - b))) if np.all(np.isfinite(a)) and np.all(np.isfinite(b)) else float("inf")
            chiave = "%s/%s" % (nome, m)
            riepilogo.setdefault(chiave, {"origini": 0, "diff_max": 0.0, "fallite": []})
            riepilogo[chiave]["origini"] += 1
            riepilogo[chiave]["diff_max"] = max(riepilogo[chiave]["diff_max"], diff)
            if not diff <= TOLLERANZA:
                riepilogo[chiave]["fallite"].append([tipo, t])
            peggiore = max(peggiore, diff)
            if tipo == "vera":
                salva["%s|%s|%d" % (nome, m, t)] = a
    esito = all(not x["fallite"] for x in riepilogo.values())
    (QUI / "esiti").mkdir(exist_ok=True)
    out = {"esito": "PASSA" if esito else "FALLISCE", "commit": controllo["commit"], "tolleranza": TOLLERANZA, "diff_max_complessiva": peggiore,
           "seme": SEME, "per_strumento_e_modello": riepilogo}
    tmp = QUI / "esiti" / "invarianza.json.tmp"
    tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, QUI / "esiti" / "invarianza.json")
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE / "invarianza_previsioni.npz", **salva)
    print(out["esito"], "diff max", peggiore)
    return 0 if esito else 1


if __name__ == "__main__":
    sys.exit(main())
