"""Previsioni finali di tutti i modelli e riferimenti della famiglia `volatilita` per uno strumento. 0 trial.

`previsioni(r, v)` restituisce {nome: matrice (n, 2)} con la previsione finale a h = 1 e h = 5 all'origine t, sulla
scala di v (%²): c_t applicato ai modelli sulla scala dei rendimenti (§3), non a HAR, persistenza e media.
"""
from __future__ import annotations

import numpy as np

import modelli as M

SCALA_RENDIMENTI = ("ewma", "garch", "gjr", "egarch", "hmm2", "hmm3", "comb2", "comb3", "media_garch")
SCALA_V = ("har", "persistenza", "media")
VARIANTI = {"garch": ("garch", "gjr", "egarch"), "hmm": ("hmm2", "hmm3", "comb2", "comb3")}
BENCHMARK = {"garch": "ewma", "hmm": "gjr"}
ORIZZONTI = (1, 5)


def _due_orizzonti(F):
    return np.column_stack([M.somma_orizzonte(F, 1), M.somma_orizzonte(F, 5)])


def previsioni(r: np.ndarray, v: np.ndarray, modelli=None, origini=None, partenze_hmm: int = 20,
               w: int = M.W, passo: int = M.PASSO) -> dict:
    """`modelli`: sottoinsieme dei nomi (default tutti). Le combinazioni e la media GARCH calcolano i loro componenti."""
    tutti = SCALA_RENDIMENTI + SCALA_V
    voluti = set(tutti if modelli is None else modelli)
    serve = set(voluti)
    if voluti & {"comb2", "comb3"}:
        serve |= {"gjr"}
    if "comb2" in voluti:
        serve.add("hmm2")
    if "comb3" in voluti:
        serve.add("hmm3")
    if "media_garch" in voluti:
        serve |= {"garch", "gjr", "egarch"}

    grezze, diagnostica = {}, {}
    for tipo in ("ewma", "garch", "gjr", "egarch"):
        if tipo in serve:
            out = M.prevedi_arch(r, tipo, w=w, passo=passo, origini=origini)
            grezze[tipo], diagnostica[tipo] = out["F"], out["non_convergenze"]
    for k in (2, 3):
        if "hmm%d" % k in serve:
            out = M.prevedi_hmm(r, k, w=w, passo=passo, partenze=partenze_hmm, origini=origini)
            grezze["hmm%d" % k], diagnostica["hmm%d" % k] = out["F"], out["non_convergenze"]
    due = {n: _due_orizzonti(F) for n, F in grezze.items()}
    for k in (2, 3):
        if "comb%d" % k in serve:
            due["comb%d" % k] = 0.5 * due["gjr"] + 0.5 * due["hmm%d" % k]
    if "media_garch" in serve:
        due["media_garch"] = (due["garch"] + due["gjr"] + due["egarch"]) / 3
    c = M.riscala(r, v, w)
    finali = {n: due[n] * c[:, None] for n in due if n in voluti}

    if "har" in voluti:
        out = M.prevedi_har(v, w=w, passo=passo, origini=origini)
        finali["har"] = np.column_stack([out["F"][:, 0], out["F"][:, M.H - 1]])
        diagnostica["har_corrette"] = out["corrette"]
    if "persistenza" in voluti:
        finali["persistenza"] = _due_orizzonti(M.prevedi_persistenza(v, w))
    if "media" in voluti:
        finali["media"] = _due_orizzonti(M.prevedi_media(v, w))
    return {"previsioni": finali, "c": c, "diagnostica": diagnostica}


def bersagli(v: np.ndarray, escluso: np.ndarray) -> np.ndarray:
    """(n, 2): v_{t+1} e somma di v_{t+1..t+5}; NaN se un giorno della finestra e' escluso o manca (§3)."""
    n = len(v)
    out = np.full((n, 2), np.nan)
    cs = np.cumsum(np.r_[0.0, v])
    ce = np.cumsum(np.r_[0, escluso.astype(int)])
    for j, h in enumerate(ORIZZONTI):
        t = np.arange(n - h)
        ok = (ce[t + 1 + h] - ce[t + 1]) == 0
        out[t[ok], j] = cs[t[ok] + 1 + h] - cs[t[ok] + 1]
    return out


def qlike(f: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.log(f) + v / f
