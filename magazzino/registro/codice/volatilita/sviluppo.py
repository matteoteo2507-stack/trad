"""Corsa di sviluppo (pre-registrazione §7 passo 3): previsioni di tutte le serie sui dati di sviluppo. 0 trial.

Solo descrittiva: **dopo averla vista non si cambia nulla di §2-§6** (una modifica e' una variante post-esito).
Parte solo se i passi 1 (invarianza) e 2 (negativi GARCH e HMM) sono PASSA in `esiti/`.

Il lavoro si divide in compiti (strumento, modello, gruppo di blocchi) eseguiti in parallelo; ogni compito si salva in
`motore/data/cache/volatilita/sviluppo/` appena finisce, e una corsa interrotta riprende dai mancanti. Alla fine
`riassumi()` scrive `esiti/sviluppo.json`: perdite medie per modello, strumento e orizzonte, conteggi, c_t, e la
diagnostica (non convergenze, HAR corrette).

Uso: python magazzino/registro/codice/volatilita/sviluppo.py [--processi 8]
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

CACHE = G.ROOT / "motore/data/cache/volatilita/sviluppo"
ESITI = QUI / "esiti"
MODELLI_STIMATI = ("ewma", "garch", "gjr", "egarch", "hmm2", "hmm3")
GRUPPO = {"hmm3": 10, "hmm2": 40}                 # blocchi per compito (l'HMM a 3 regimi e' il piu' lento)


def _prerequisiti():
    for nome in ("invarianza", "neg_garch", "neg_hmm"):
        f = ESITI / ("%s.json" % nome)
        if not f.exists() or json.loads(f.read_text(encoding="utf-8")).get("esito") != "PASSA":
            raise SystemExit("prerequisito mancante o non superato: %s" % f.name)


def _compiti():
    out = []
    for nome in G.STRUMENTI:
        n = len(G.carica(nome))
        t0s = list(range(M.W - 1, n, M.PASSO))
        for m in MODELLI_STIMATI:
            g = GRUPPO.get(m, len(t0s))
            for i in range(0, len(t0s), g):
                out.append((nome, m, i // g, t0s[i:i + g]))
    return out


def _file(nome, m, j):
    return CACHE / ("%s_%s_%03d.npz" % (nome, m, j))


def _esegui(args):
    nome, m, j, t0s = args
    if _file(nome, m, j).exists():
        return nome, m, j, 0.0
    t = time.time()
    d = G.carica(nome)
    r = d["r"].to_numpy()
    if m.startswith("hmm"):
        out = M.prevedi_hmm(r, int(m[-1]), origini=t0s)
    else:
        out = M.prevedi_arch(r, m, origini=t0s)
    par = {"t0_%d" % t0: p for t0, p in out["parametri"]}
    tmp = _file(nome, m, j).with_suffix(".tmp.npz")
    np.savez(tmp, F=out["F"], non_convergenze=out["non_convergenze"],
             ripartenze=out.get("ripartenze_primo_blocco", 0), **par)
    os.replace(tmp, _file(nome, m, j))
    return nome, m, j, time.time() - t


def unisci(nome: str) -> dict:
    """Previsioni finali dello strumento dai compiti salvati (stessa combinazione di `pipeline.previsioni`)."""
    d = G.carica(nome)
    r, v = d["r"].to_numpy(), d["v"].to_numpy()
    n = len(r)
    grezze, nc, rp = {}, {}, {}
    for m in MODELLI_STIMATI:
        F = np.full((n, M.H), np.nan)
        nc[m], rp[m] = 0, 0
        for f in sorted(CACHE.glob("%s_%s_*.npz" % (nome, m))):
            z = np.load(f)
            ok = np.isfinite(z["F"][:, 0])
            F[ok] = z["F"][ok]
            nc[m] += int(z["non_convergenze"])
            rp[m] += int(z["ripartenze"])
        grezze[m] = F
    c = M.riscala(r, v)
    due = {m: np.column_stack([M.somma_orizzonte(F, 1), M.somma_orizzonte(F, 5)]) for m, F in grezze.items()}
    due["comb2"] = 0.5 * due["gjr"] + 0.5 * due["hmm2"]
    due["comb3"] = 0.5 * due["gjr"] + 0.5 * due["hmm3"]
    due["media_garch"] = (due["garch"] + due["gjr"] + due["egarch"]) / 3
    finali = {m: x * c[:, None] for m, x in due.items()}
    har = M.prevedi_har(v)
    finali["har"] = np.column_stack([har["F"][:, 0], har["F"][:, M.H - 1]])
    finali["persistenza"] = np.column_stack([M.somma_orizzonte(M.prevedi_persistenza(v), h) for h in P.ORIZZONTI])
    finali["media"] = np.column_stack([M.somma_orizzonte(M.prevedi_media(v), h) for h in P.ORIZZONTI])
    senza_c = {m: due[m] for m in P.SCALA_RENDIMENTI}
    return {"dati": d, "previsioni": finali, "senza_c": senza_c, "c": c, "non_convergenze": nc, "ripartenze_primo_blocco": rp,
            "har_corrette": har["corrette"]}


def origini_valutazione(n: int) -> np.ndarray:
    return np.arange(M.W - 1, n - 5)                 # bersaglio a 5 giorni dentro lo sviluppo


def main():
    import guardie

    _prerequisiti()
    controllo = guardie.verifica()
    print("guardie OK, commit", controllo["commit"], flush=True)
    processi = int(sys.argv[sys.argv.index("--processi") + 1]) if "--processi" in sys.argv else os.cpu_count()
    CACHE.mkdir(parents=True, exist_ok=True)
    compiti = sorted(_compiti(), key=lambda x: x[1] != "hmm3")          # i lenti per primi
    mancanti = [c for c in compiti if not _file(c[0], c[1], c[2]).exists()]
    print("compiti %d, mancanti %d" % (len(compiti), len(mancanti)), flush=True)
    with Pool(processi) as pool:
        for k, (nome, m, j, sec) in enumerate(pool.imap_unordered(_esegui, mancanti), 1):
            print("%d/%d %s %s %d (%.0fs)" % (k, len(mancanti), nome, m, j, sec), flush=True)
    (CACHE / "commit.txt").write_text(controllo["commit"] + "\n", encoding="utf-8")
    print("previsioni di sviluppo complete", flush=True)


if __name__ == "__main__":
    main()
