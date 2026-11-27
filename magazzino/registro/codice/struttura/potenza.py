"""Potenza di I3 (referto §10, passo (4); requisiti del commit (1), punti 3 e 4). 0 trial.

Parte solo dopo, tutti committati: l'esito della verifica delle fonti (`esiti/verifica_fonti.md`), il controllo di
struttura, gli hash degli 8 nuovi e un N2 con esito PASSA. Legge i prezzi con la **data limite 2024-11-08 alla lettura**
(`dati.TAGLIO_SVILUPPO_UTC`) e controlla che nessun oggetto derivato vada oltre. Sugli orizzonti non decaduti calcola
il differenziale di Stein EWMA − costante e ne riporta **solo la deviazione HAC centrata**, con le origini e i
ritardi: nessuna media, nessun segno, nessuna perdita, nessuna matrice. La serie dei differenziali vive solo dentro
`deviazioni` e non esce. MDE = fattore × deviazione / √n per n = sedute di 1 e 2 anni di holdout dal solo calendario.

python magazzino/registro/codice/struttura/potenza.py   -> esiti/potenza.json (usa l'unico esiti/n2_c*.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import dati as D  # noqa: E402
import guardie as G  # noqa: E402
import misura as M  # noqa: E402
import previsioni as V  # noqa: E402
import verifica_generatore as VG  # noqa: E402

ESITO = "potenza.json"
V_MIN_ORIGINI = 50     # come simula_n2.MIN_ORIGINI e la decadenza sui conteggi
ALFE = (0.05, 0.025, 0.0125, 0.00625)
CHIAVI = {"commit", "versioni", "sha256", "universo", "orizzonti", "sedute_holdout", "fattori", "mde"}
CHIAVI_ORIZZONTE = {"n_origini", "ritardi_hac", "sd_hac_centrata"}


class OltreLaDataLimite(G.GuardiaFallita):
    pass


def controlla_data(giorni) -> None:
    """Ogni oggetto derivato e' indicizzato da queste sedute: nessuna oltre il 2024-11-08."""
    if len(giorni) and np.max(np.asarray(giorni, "datetime64[ns]")) > np.datetime64(D.FINE_SVILUPPO):
        raise OltreLaDataLimite("seduta oltre il 2024-11-08 negli oggetti della potenza")


def pause_dai_conteggi(conteggi: dict, nome: str, giorni) -> np.ndarray:
    """Orari di pausa per seduta presi dal controllo di struttura (un proprietario: non si ricalcolano)."""
    celle = conteggi["strumenti"][nome]["sviluppo"]
    pausa = np.zeros((len(giorni), D.N_BARRE), bool)
    for t, a in enumerate(np.asarray(giorni.year).astype(str)):
        pausa[t, celle[a]["orari_pausa"]] = True
    return pausa


def deviazioni(P: np.ndarray, it: np.ndarray, orizzonti) -> dict:
    """{h: (n_origini, ritardi, sd)}: la serie dei differenziali resta qui dentro."""
    m = M.matrici(P, interrotti=it)
    prev = V.tutte(m)
    out = {}
    for h in orizzonti:
        B, ok = V.bersagli(m["Sigma"], m["pronto"], h)
        valide = ok & m["pronto"] & np.isfinite(prev["costante"]).all(axis=(1, 2)) \
            & np.isfinite(prev["ewma"]).all(axis=(1, 2))
        o = np.flatnonzero(valide)
        if len(o) < V_MIN_ORIGINI:
            raise G.GuardiaFallita("orizzonte %d: meno di %d origini nella potenza" % (h, V_MIN_ORIGINI))
        d = V.differenziale_stein(prev["ewma"][o], prev["costante"][o], B[o])
        out[h] = (int(len(o)), V.ritardi_hac(h), V.sd_hac(d, V.ritardi_hac(h)))
        del d
    return out


def sedute_holdout() -> dict:
    uno, _ = D.sedute("2024-11-11", "2025-11-10")
    due, _ = D.sedute("2024-11-11", "2026-11-10")
    return {"1": int(len(uno)), "2": int(len(due))}


def unico_n2() -> str:
    """Bloccante B1 dell'undicesima: la potenza usa l'unico N2 che esiste, non uno scelto da riga di comando."""
    trovati = sorted(p.name for p in G.ESITI.glob("n2_c*.json"))
    if len(trovati) != 1:
        raise G.GuardiaFallita("serve esattamente un N2, trovati %d" % len(trovati))
    return trovati[0]


def calcola(conteggi: dict, orizzonti, universo=None) -> dict:
    """`universo`: quello dell'N2 che ha passato (riserva R12: dopo un'uscita di strumento non coincide coi
    conteggi)."""
    from motore.core.verifiche import fattore_potenza

    universo = list(conteggi["universo"] if universo is None else universo)
    giorni, _ = D.sedute(conteggi["inizio_comune"], conteggi["fine_sviluppo"])
    controlla_data(giorni)
    P = np.full((len(giorni), D.N_PREZZI, len(universo)), np.nan)
    it = np.zeros((len(giorni), D.N_PREZZI - 1, len(universo)), bool)
    for i, n in enumerate(universo):
        b = D.a_new_york(D.leggi_barre(n, fino_a=D.TAGLIO_SVILUPPO_UTC))
        Pi, pres = D.griglia(b, giorni)
        del b
        P[:, :, i] = Pi
        it[:, :, i] = D.interrotti(pres, pause_dai_conteggi(conteggi, n, giorni), giorni)
    controlla_data(giorni)
    dev = deviazioni(P, it, orizzonti)
    del P
    hold = sedute_holdout()
    fatt = {str(a): round(fattore_potenza(a, code=1), 3) for a in ALFE}
    oriz = {}
    for h, (n, L, sd) in dev.items():
        oriz["h%d" % h] = {"n_origini": n, "ritardi_hac": L, "sd_hac_centrata": sd}
        G.controlla_chiavi(oriz["h%d" % h], CHIAVI_ORIZZONTE, " (orizzonte)")
    mde = {"h%d" % h: {anni: {a: f * dev[h][2] / np.sqrt(n) for a, f in fatt.items()} for anni, n in hold.items()}
           for h in dev}
    return {"universo": universo, "orizzonti": oriz, "sedute_holdout": hold, "fattori": fatt, "mde": mde}


def main() -> None:
    g = G.verifica()
    nome_n2 = unico_n2()
    G.richiedi("verifica_fonti.md", "controllo_struttura.json", nome_n2)
    if G._sporchi([str(G.HASH_I3)]):
        raise G.GuardiaFallita("hash degli 8 nuovi non committati")
    n2 = json.loads((G.ESITI / nome_n2).read_text(encoding="utf-8"))
    if n2["esito"] != "PASSA":
        raise G.GuardiaFallita("N2 %s: %s, la potenza non parte" % (nome_n2, n2["esito"]))
    conteggi = json.loads((G.ESITI / "controllo_struttura.json").read_text(encoding="utf-8"))
    decaduti = set(conteggi["orizzonti_decaduti"]) | set(n2["risultato"]["orizzonti_decaduti"])
    orizzonti = [h for h in V.ORIZZONTI if h not in decaduti]
    corr = tuple(n2["correzioni"])
    G.catena_guasta([corr[:k] for k in range(len(corr))], VG.nome_esito)
    if G.leggi_esito(VG.nome_esito(corr)).get("esito") != "PASSA":
        raise G.GuardiaFallita("la verifica delle correzioni di N2 non e' PASSA")
    out = {"commit": g["commit"], "versioni": g["versioni"], "sha256": g["sha256"],
           **calcola(conteggi, orizzonti, universo=n2["universo"])}
    G.controlla_chiavi(out, CHIAVI)
    dest = G.scrivi_esito(ESITO, out)
    print("scritto", dest.name, "| orizzonti", orizzonti)


if __name__ == "__main__":
    G.protetto(main)
