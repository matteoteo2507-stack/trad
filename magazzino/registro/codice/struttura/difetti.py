"""Parametri del generatore dei difetti di N2 dai soli conteggi dello sviluppo (referto §9). 0 trial.

`da_conteggi(conteggi, universo, anni, correzioni)` legge l'esito del controllo di struttura (solo la parte
`sviluppo`) e restituisce il dizionario per `simula_n2.applica_difetti`, una riga per seduta (l'anno della seduta
sceglie la cella):
- `p_giorno` = sedute senza prezzi / sedute; `p_ora[k]` = prezzi mancanti all'orario k / sedute presenti;
- `p0` = nulli / osservati; `L` = `durata_catena(L̃, p0)` (la durata della catena che riproduce quella contata);
- `p_interrotti[j]` = intervalli interrotti con gli estremi presenti / sedute con gli estremi presenti (probabilita'
  **condizionata**: un intervallo con un estremo mancante e' gia' mancante; riserva R1 dell'undicesima), solo se ce
  n'e' almeno uno;
- (1) `L_mancanti` = durata della catena che riproduce la durata **contata** delle serie di prezzi mancanti, corretta
  per il troncamento su 27 prezzi come per i nulli (bloccante B2 dell'undicesima);
- correzioni (1)-(4), solo se elencate in `correzioni` e **in quest'ordine** (un prefisso di 1, 2, 3, 4): (1)
  `L_mancanti`; (2) DAX e BUND mancanti insieme; (3) seduta mancante per tutti; (4) quota giornaliera di nulli
  dall'istogramma. Con (2) e (3) `p_giorno` diventa **condizionata** (una seduta mancante si conta una volta).
"""
from __future__ import annotations

import numpy as np

import simula_n2 as S

ORDINE = (1, 2, 3, 4)
SOGLIA_QUOTA = 0.25


def controlla_correzioni(correzioni) -> tuple:
    c = tuple(correzioni)
    if c != ORDINE[:len(c)]:
        raise ValueError("le correzioni si applicano in ordine: %s, non %s" % (ORDINE, c))
    return c


def _num(x, default):
    return default if x is None else float(x)


def da_conteggi(conteggi: dict, universo, anni: np.ndarray, correzioni=()) -> dict:
    c = controlla_correzioni(correzioni)
    universo = list(universo)
    T, N = len(anni), len(universo)
    sv = {n: conteggi["strumenti"][n]["sviluppo"] for n in universo}
    an = conteggi["anni"]["sviluppo"]
    chiavi_anno = sorted({str(a) for a in anni})
    mancanti = [a for a in chiavi_anno if a not in an or any(a not in sv[n] for n in universo)]
    if mancanti:
        raise ValueError("anni senza conteggi: %s" % mancanti)
    d = {"p_giorno": np.zeros((T, N)), "p0": np.zeros((T, N)), "L": np.ones((T, N)),
         "p_ora": np.zeros((T, S.N_PREZZI, N))}
    interr = np.zeros((T, S.N_PREZZI - 1, N))
    Lm = np.ones((T, N))
    p_tutti = np.zeros(T)
    p_ins = np.zeros(T)
    for a in chiavi_anno:
        righe = np.array([str(x) == a for x in anni])
        ya = an[a]
        m_tutti = ya["senza_prezzi_tutti"] if 3 in c else 0
        coppia = 2 in c and "DAX" in universo and "BUND" in universo
        m_ins = (ya["dax_bund_insieme"] - (ya["senza_prezzi_tutti"] if 3 in c else 0)) if coppia else 0
        if 3 in c:
            p_tutti[righe] = m_tutti / ya["sedute"]
        if coppia:
            p_ins[righe] = m_ins / (ya["sedute"] - m_tutti)
        for i, n in enumerate(universo):
            x = sv[n][a]
            pres = max(x["sedute_presenti"], 1)
            togli = m_tutti + (m_ins if coppia and n in ("DAX", "BUND") else 0)
            d["p_giorno"][righe, i] = max(x["sedute_senza_prezzi"] - togli, 0) / (x["sedute"] - togli)
            d["p_ora"][righe, :, i] = np.asarray(x["prezzi_mancanti_per_orario"], float) / pres
            p0 = x["rendimenti_nulli"] / x["rendimenti_osservati"] if x["rendimenti_osservati"] else 0.0
            d["p0"][righe, i] = p0
            d["L"][righe, i] = S.durata_catena(np.array([_num(x["durata_media_nulli"], np.nan)]),
                                               p0=np.array([p0]))[0]
            den = np.maximum(np.asarray(x["intervalli_con_estremi_presenti_per_orario"], float), 1.0)
            interr[righe, :, i] = np.asarray(x["intervalli_interrotti_per_orario"], float) / den
            q_manc = sum(x["prezzi_mancanti_per_orario"]) / (S.N_PREZZI * pres)
            Lm[righe, i] = S.durata_catena(np.array([_num(x["durata_media_mancanti"], np.nan)]),
                                           p0=np.array([q_manc]), n=S.N_PREZZI)[0]
    if interr.any():
        d["p_interrotti"] = interr
    if 1 in c:
        d["L_mancanti"] = Lm
    if 2 in c and "DAX" in universo and "BUND" in universo:
        d["coppia"] = (universo.index("DAX"), universo.index("BUND"))
        d["p_insieme"] = p_ins
    if 3 in c:
        d["p_tutti"] = p_tutti
    if 4 in c:
        idx = {a: k for k, a in enumerate(chiavi_anno)}
        valori = np.broadcast_to(np.arange(27) / 26.0, (len(chiavi_anno), N, 27)).copy()
        cdf = np.zeros((len(chiavi_anno), N, 27))
        for a, k in idx.items():
            for i, n in enumerate(universo):
                h = np.asarray(sv[n][a]["istogramma_nulli"], float)
                cdf[k, i] = np.cumsum(h) / h.sum() if h.sum() else 1.0
        d["quote"] = (valori, cdf, np.array([idx[str(x)] for x in anni]))
    return d
