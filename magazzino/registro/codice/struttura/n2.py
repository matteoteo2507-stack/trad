"""N2 sui conteggi veri (referto §9; requisiti del commit (1), punto 6). 0 trial.

Parte solo se sono committati il controllo di struttura, gli hash degli 8 nuovi e una verifica del generatore con
esito PASSA (`--correzioni` sceglie quale; senza, quella base). Legge **solo** il file dei conteggi: nessun CSV di
prezzi si apre (un test lo verifica). Simula 500 repliche sulle **date XNYS reali dello sviluppo comune** (chiusure
anticipate escluse), con l'universo deciso dal controllo di struttura (la regola del 10% non si riapplica), seme
20261123 per la configurazione base e un seme proprio per ogni configurazione corretta (`simula_n2.SEMI_N2`). Un
solo N2: si rifiuta se ne esiste gia' uno, e una configurazione corretta parte solo se le precedenti sono GUASTO.
Un orizzonte gia' decaduto sui conteggi veri resta fuori (riserva R7). Uscita a chiavi ammesse.

python magazzino/registro/codice/struttura/n2.py [--correzioni 1,2]   -> esiti/n2_c<correzioni>.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import dati as D  # noqa: E402
import difetti as DF  # noqa: E402
import guardie as G  # noqa: E402
import simula_n2 as S  # noqa: E402
import verifica_generatore as VG  # noqa: E402

CHIAVI_RIASSUNTO = ({"repliche", "non_valide", "campione_insufficiente_h1", "campione_insufficiente_h5",
                     "orizzonti_decaduti", "esito", "guardia_rifiuti_h1", "guardia_rifiuti_h5"}
                    | {"delta_%s_h%d" % (n, h) for n in ("costante", "persistenza") for h in (1, 5)})
CHIAVI = {"commit", "versioni", "seme", "correzioni", "sedute", "n_h", "tau", "soglia_guardia", "universo",
          "orizzonti_decaduti_conteggi", "risultato", "esito"}


def _nessun_csv(*a, **k):
    raise G.GuardiaFallita("N2 ha tentato di leggere un file di prezzi")


def nome_esito(correzioni) -> str:
    return "n2_c%s.json" % ("".join(map(str, correzioni)) or "0")


def esegui(conteggi: dict, correzioni=(), repliche: int = S.REPLICHE, processi: int = 1) -> dict:
    universo = tuple(conteggi["universo"])
    giorni, _ = D.sedute(conteggi["inizio_comune"], conteggi["fine_sviluppo"])
    anni = np.asarray(giorni.year).astype(str)
    d = DF.da_conteggi(conteggi, universo, anni, correzioni)
    gia = list(conteggi["orizzonti_decaduti"])
    seme = S.SEMI_N2[tuple(correzioni)]
    r = S.esegui(len(giorni), d, seme, repliche, universo=universo, processi=processi, esclusi=gia)
    G.controlla_chiavi(r, CHIAVI_RIASSUNTO, " (riassunto)")
    esito = r["esito"]
    return {"seme": seme, "correzioni": list(correzioni), "sedute": int(len(giorni)), "n_h": S.N_H, "tau": S.TAU,
            "soglia_guardia": S.soglia_guardia(repliche), "universo": list(universo),
            "orizzonti_decaduti_conteggi": gia, "risultato": r, "esito": esito}


def main() -> None:
    corr = ()
    if "--correzioni" in sys.argv:
        corr = tuple(int(x) for x in sys.argv[sys.argv.index("--correzioni") + 1].split(","))
    D.leggi_barre = _nessun_csv                        # requisito 6: N2 non apre file di prezzi (guardia a runtime)
    g = G.verifica(dati=False)
    nome_ver = VG.nome_esito(corr)
    G.richiedi("controllo_struttura.json", nome_ver)
    G.catena_guasta([corr[:k] for k in range(len(corr))], VG.nome_esito)
    gia = sorted(p.name for p in G.ESITI.glob("n2_c*.json"))
    if gia:
        raise G.GuardiaFallita("esiste gia' un N2 (%s): non se ne fa un altro" % gia)
    if not G.HASH_I3.exists() or G._sporchi([str(G.HASH_I3)]):
        raise G.GuardiaFallita("hash degli 8 nuovi mancanti o non committati")
    ver = json.loads((G.ESITI / nome_ver).read_text(encoding="utf-8"))
    if ver["esito"] != "PASSA":
        raise G.GuardiaFallita("verifica del generatore %s: %s, N2 non parte" % (nome_ver, ver["esito"]))
    G.storia_pulita("controllo_struttura.json", nome_ver)
    G.codice_invariato_da(ver["commit"])
    conteggi = json.loads((G.ESITI / "controllo_struttura.json").read_text(encoding="utf-8"))
    out = {"commit": g["commit"], "versioni": g["versioni"], **esegui(conteggi, corr, processi=os.cpu_count())}
    G.controlla_chiavi(out, CHIAVI)
    dest = G.scrivi_esito(nome_esito(corr), out)
    print("scritto", dest.name, "|", out["esito"])


if __name__ == "__main__":
    G.protetto(main)
