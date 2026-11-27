"""Controllo di struttura di I3 (referto §3, §9, §10 passo (3); requisito 5): **solo conteggi**. 0 trial.

Legge i 17 M5 (fino al 2026-11-10; i 9 vecchi tagliati alla lettura), costruisce griglia e presenze delle barre, e
riporta per strumento e per anno, con **sviluppo** (fino al 2024-11-08) e **blocco** (2024-11-11 → 2026-11-10) separati:
sedute, sedute senza prezzi, prezzi mancanti per orario, rendimenti osservati e nulli (a 15 minuti), durata media delle
serie di nulli e di prezzi mancanti, istogramma dei nulli per seduta, sedute escluse, orari di pausa; per anno le
sedute escluse per unione, senza prezzi per tutti, con DAX e BUND mancanti insieme; le chiusure anticipate; la
copertura del DAX e la regola del 10% (universo); il controllo di selezione (**solo sviluppo, letto con la data limite
2024-11-08**: quante sedute escluse hanno un rendimento assoluto sopra la mediana delle incluse); le origini per
orizzonte dalle sole maschere (decadenza, riserva R7). Nessuna RV, nessuna media di rendimenti, nessun livello di prezzo.

Inizio comune: la prima seduta in cui **tutti i 17** hanno almeno un prezzo nella seduta, calcolata una volta (se poi
uno strumento esce non si ricalcola).

python magazzino/registro/codice/struttura/controllo_struttura.py   -> esiti/controllo_struttura.json
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import dati as D  # noqa: E402
import guardie as G  # noqa: E402
import misura as M  # noqa: E402
import previsioni as V  # noqa: E402
import simula_n2 as S  # noqa: E402

ESITO = "controllo_struttura.json"
SOGLIA_DAX = 0.90
SOGLIA_STRUMENTO = 0.10
MIN_ORIGINI = S.MIN_ORIGINI

CHIAVI = {"commit", "versioni", "sha256", "inizio_comune", "fine_sviluppo", "inizio_blocco", "fine",
          "chiusure_anticipate", "strumenti", "anni", "dax", "regola_10", "universo", "selezione", "origini",
          "orizzonti_decaduti"}
CELLA = {"sedute", "sedute_senza_prezzi", "sedute_presenti", "prezzi_mancanti_per_orario", "rendimenti_osservati",
         "rendimenti_nulli", "durata_media_nulli", "durata_media_mancanti", "istogramma_nulli", "sedute_escluse",
         "orari_pausa", "intervalli_interrotti_per_orario"}
ANNO = {"sedute", "escluse_unione", "senza_prezzi_tutti", "dax_bund_insieme"}


def _serie(mask_righe) -> list:
    """Lunghezze delle serie di True consecutivi, riga per riga (troncate ai bordi della riga)."""
    out = []
    for riga in mask_righe:
        n = 0
        for v in riga:
            if v:
                n += 1
            elif n:
                out.append(n)
                n = 0
        if n:
            out.append(n)
    return out


def cella(P: np.ndarray, it: np.ndarray, valido: np.ndarray, pausa: np.ndarray) -> dict:
    """Conteggi di una cella strumento × anno: P (T, 27), it (T, 26), valido (T,), pausa (T, 78). Solo conteggi."""
    presente = np.isfinite(P).any(axis=1)
    r, oss = M.rendimenti(P[:, :, None], 1, it[:, :, None])
    r, oss = r[:, :, 0], oss[:, :, 0]
    nulli = oss & (r == 0.0)
    Pp, op, np_ = P[presente], oss[presente], nulli[presente]
    serie_nulli = _serie(np.where(op, np_, False))
    serie_manc = _serie(~np.isfinite(Pp))
    quota = np.divide(np_.sum(axis=1), op.sum(axis=1), out=np.zeros(len(op)), where=op.sum(axis=1) > 0)
    ist = np.bincount(np.rint(26 * quota[op.sum(axis=1) > 0]).astype(int), minlength=27)[:27]
    return {"sedute": int(len(P)), "sedute_senza_prezzi": int((~presente).sum()),
            "sedute_presenti": int(presente.sum()),
            "prezzi_mancanti_per_orario": [int(x) for x in (~np.isfinite(Pp)).sum(axis=0)],
            "rendimenti_osservati": int(oss.sum()), "rendimenti_nulli": int(nulli.sum()),
            "durata_media_nulli": float(np.mean(serie_nulli)) if serie_nulli else None,
            "durata_media_mancanti": float(np.mean(serie_manc)) if serie_manc else None,
            "istogramma_nulli": [int(x) for x in ist],
            "sedute_escluse": int((~valido).sum()),
            "orari_pausa": [int(m) for m in np.flatnonzero(pausa[0])] if len(pausa) else [],
            "intervalli_interrotti_per_orario": [int(x) for x in it[presente].sum(axis=0)]}


def costruisci(nomi, fino_a=None, giorni=None) -> dict:
    """Griglia, presenze, pause, interruzioni e validita' per strumento (solo in memoria)."""
    out = {}
    for n in nomi:
        b = D.a_new_york(D.leggi_barre(n, fino_a=fino_a))
        out[n] = {"barre": b}
    if giorni is None:
        giorni, _ = D.sedute("2012-01-01", D.FINE)
    anni = np.asarray(giorni.year)
    for n in nomi:
        P, pres = D.griglia(out[n].pop("barre"), giorni)
        pausa = D.orari_di_pausa(pres, anni)
        it = D.interrotti(pres, pausa, giorni)
        r, oss = M.rendimenti(P[:, :, None], 1, it[:, :, None])
        out[n].update(P=P, presenti=pres, pausa=pausa, it=it, valido=M.validi_strumento(r, oss)[:, 0])
    return {"giorni": giorni, "anni": anni, "strumenti": out}


def selezione(nomi, giorni_sviluppo) -> dict:
    """Controllo di selezione, solo sviluppo, con la data limite applicata alla lettura: per ogni strumento, quante
    sedute escluse hanno un rendimento della seduta e quante lo hanno sopra la mediana (in valore assoluto) delle
    sedute incluse. Solo conteggi."""
    if giorni_sviluppo.max() > D.FINE_SVILUPPO:
        raise G.GuardiaFallita("controllo di selezione oltre il 2024-11-08")
    c = costruisci(nomi, fino_a=D.TAGLIO_SVILUPPO_UTC, giorni=giorni_sviluppo)
    out = {}
    for n in nomi:
        x = c["strumenti"][n]
        P = x["P"]
        primo = np.array([row[np.isfinite(row)][0] if np.isfinite(row).any() else np.nan for row in P])
        ultimo = np.array([row[np.isfinite(row)][-1] if np.isfinite(row).any() else np.nan for row in P])
        ra = np.abs(ultimo - primo)
        incl = x["valido"] & np.isfinite(ra)
        escl = (~x["valido"]) & np.isfinite(ra)
        med = np.median(ra[incl]) if incl.any() else np.nan
        out[n] = {"escluse_con_rendimento": int(escl.sum()),
                  "sopra_mediana": int((ra[escl] > med).sum()) if np.isfinite(med) else 0}
    return out


def main() -> None:
    g = G.verifica()
    nomi = G.VECCHI + G.NUOVI
    c = costruisci(nomi)
    giorni, anni = c["giorni"], c["anni"]
    st = c["strumenti"]
    primi = [np.flatnonzero(np.isfinite(st[n]["P"]).any(axis=1))[0] for n in nomi]
    t0 = max(primi)
    sv = (np.arange(len(giorni)) >= t0) & (giorni <= D.FINE_SVILUPPO)
    bl = giorni >= D.INIZIO_BLOCCO
    periodi = {"sviluppo": sv, "blocco": bl}

    _, anticipate = None, {}
    for nome_p, sel in periodi.items():
        anticipate[nome_p] = {}
        for a in np.unique(anni[sel]):
            gg = giorni[sel & (anni == a)]
            _, n_ant = D.sedute(gg.min(), gg.max())
            anticipate[nome_p][str(a)] = n_ant

    strumenti = {}
    for n in nomi:
        x = st[n]
        strumenti[n] = {}
        for nome_p, sel in periodi.items():
            strumenti[n][nome_p] = {}
            for a in np.unique(anni[sel]):
                k = sel & (anni == a)
                cel = cella(x["P"][k], x["it"][k], x["valido"][k], x["pausa"][k])
                G.controlla_chiavi(cel, CELLA, " (cella)")
                strumenti[n][nome_p][str(a)] = cel

    pres_dax = st["DAX"]["presenti"][sv]
    cop = float(pres_dax.mean(axis=0).min())
    dax_entra = cop >= SOGLIA_DAX
    candidati = [n for n in nomi if n != "DAX" or dax_entra]
    regola = {}
    for n in candidati:
        q = float((~st[n]["valido"][sv]).mean())
        regola[n] = {"quota_escluse": round(q, 4), "esce": bool(q > SOGLIA_STRUMENTO)}
    universo = [n for n in candidati if not regola[n]["esce"]]

    anni_out = {}
    for nome_p, sel in periodi.items():
        anni_out[nome_p] = {}
        for a in np.unique(anni[sel]):
            k = sel & (anni == a)
            v = np.column_stack([st[n]["valido"][k] for n in universo])
            assenti = np.column_stack([~np.isfinite(st[n]["P"][k]).any(axis=1) for n in nomi])
            rec = {"sedute": int(k.sum()), "escluse_unione": int((~v.all(axis=1)).sum()),
                   "senza_prezzi_tutti": int(assenti.all(axis=1).sum()),
                   "dax_bund_insieme": int((assenti[:, nomi.index("DAX")] & assenti[:, nomi.index("BUND")]).sum())}
            G.controlla_chiavi(rec, ANNO, " (anno)")
            anni_out[nome_p][str(a)] = rec

    v_sv = np.column_stack([st[n]["valido"][sv] for n in universo])
    origini = {"h%d" % h: int(len(o)) for h, o in V.origini_da_maschere(v_sv).items()}
    decaduti = [h for h in V.ORIZZONTI if origini["h%d" % h] < MIN_ORIGINI]
    del c, st

    out = {"commit": g["commit"], "versioni": g["versioni"], "sha256": g["sha256"],
           "inizio_comune": str(giorni[t0].date()), "fine_sviluppo": str(D.FINE_SVILUPPO.date()),
           "inizio_blocco": str(D.INIZIO_BLOCCO.date()), "fine": str(D.FINE.date()),
           "chiusure_anticipate": anticipate, "strumenti": strumenti, "anni": anni_out,
           "dax": {"copertura_minima": round(cop, 4), "entra": bool(dax_entra)},
           "regola_10": regola, "universo": universo,
           "selezione": selezione(universo, giorni[sv]),
           "origini": origini, "orizzonti_decaduti": decaduti}
    G.controlla_chiavi(out, CHIAVI)
    dest = G.scrivi_esito(ESITO, out)
    print("scritto", dest.relative_to(G.ROOT), "| universo", len(universo), "| decaduti", decaduti)


if __name__ == "__main__":
    G.protetto(main)
