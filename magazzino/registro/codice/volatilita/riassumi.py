"""Riepilogo della corsa di sviluppo (§7 passo 3, descrittivo) e passo 4 (MDE per coppia). 0 trial.

Legge le previsioni salvate da `sviluppo.py` e scrive `esiti/sviluppo.json`:
- per strumento: giorni, origini valide per h, c_t medio nello sviluppo (con la direzione dell'effetto per l'SPX500),
  non convergenze, previsioni HAR corrette, giorni esclusi con |r| contro la mediana (§3, selezione delle origini);
- perdite QLIKE medie (e MSE, descrittiva) di ogni modello e riferimento, con e senza c_t;
- il sigma del rumore per i positivi simulati (§7.5) e l'MDE di ogni coppia (§7.4);
- il confronto fra le previsioni del test d'invarianza (blocchi ristretti) e quelle della corsa completa.

Uso: python magazzino/registro/codice/volatilita/riassumi.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
sys.path[:0] = [str(QUI), str(ROOT)]          # ROOT: `motore` (verifiche, mde) lanciando lo script direttamente

import giorni as G  # noqa: E402
import pipeline as P  # noqa: E402
import potenza as Q  # noqa: E402
import sviluppo as S  # noqa: E402


def perdite_valide(u: dict):
    d = u["dati"]
    v = d["v"].to_numpy()
    b = P.bersagli(v, d["escluso"].to_numpy())
    t = S.origini_valutazione(len(v))
    out = {}
    for j, h in enumerate(P.ORIZZONTI):
        out[h] = t[np.isfinite(b[t, j])]          # solo il bersaglio sceglie le origini; una previsione non valida e'
                                                  # un errore di `P.qlike` (19/11; prima un filtro, 0 origini scartate)
    return b, out


def main():
    import guardie

    controllo = guardie.verifica()
    rapporto = {"commit": controllo["commit"], "commit_previsioni": (S.CACHE / "commit.txt").read_text().strip(),
                "strumenti": {}, "mde": {}, "sigma_rumore": {}}
    perdite_coppie = {}
    inv = np.load(G.ROOT / "motore/data/cache/volatilita/invarianza_previsioni.npz")
    diff_inv = 0.0
    for nome in G.STRUMENTI:
        u = S.unisci(nome)
        d = u["dati"]
        r, v = d["r"].to_numpy(), d["v"].to_numpy()
        b, valide = perdite_valide(u)
        riga = {"giorni": len(v), "origini_valide": {"h%d" % h: int(len(t)) for h, t in valide.items()},
                "c_medio": float(np.nanmean(u["c"][S.origini_valutazione(len(v))])),
                "non_convergenze": u["non_convergenze"],
                "ripartenze_primo_blocco": u["ripartenze_primo_blocco"], "har_corrette": u["har_corrette"]}
        esc = d["escluso"].to_numpy()
        med = float(np.median(np.abs(r)))
        riga["esclusi_abs_r_su_mediana"] = {"mediana_esclusi": float(np.median(np.abs(r[esc])) / med) if esc.any() else None,
                                            "quota_esclusi_sopra_q90": float(np.mean(np.abs(r[esc]) > np.quantile(np.abs(r), 0.9))) if esc.any() else None}
        riga["qlike"], riga["qlike_senza_c"], riga["mse"], riga["sotto_soglia"] = {}, {}, {}, {}
        for j, h in enumerate(P.ORIZZONTI):
            t = valide[h]
            riga["sotto_soglia"]["h%d" % h] = {m: P.sotto_soglia(F[t, j]) for m, F in u["previsioni"].items()}
            riga["qlike"]["h%d" % h] = {m: float(P.qlike(F[t, j], b[t, j]).mean()) for m, F in u["previsioni"].items()}
            riga["qlike_senza_c"]["h%d" % h] = {m: float(P.qlike(F[t, j], b[t, j]).mean()) for m, F in u["senza_c"].items()}
            riga["mse"]["h%d" % h] = {m: float(np.mean((F[t, j] - b[t, j]) ** 2)) for m, F in u["previsioni"].items()}
            for nodo in ("garch", "hmm"):
                lb = P.qlike(u["previsioni"][P.BENCHMARK[nodo]][t, j], b[t, j])
                lm = np.column_stack([P.qlike(u["previsioni"][m][t, j], b[t, j]) for m in P.VARIANTI[nodo]])
                perdite_coppie[(nodo, nome, h)] = (lb, lm)
        t1 = valide[1]
        f_gjr = u["previsioni"]["gjr"][t1, 0]
        rapporto["sigma_rumore"][nome] = Q.sigma_rumore(b[t1, 0], f_gjr, np.ones(len(t1), bool))
        for chiave in inv.files:
            n_, m_, t_ = chiave.split("|")
            if n_ == nome:
                diff_inv = max(diff_inv, float(np.max(np.abs(inv[chiave] - u["previsioni"][m_][int(t_)]))))
        rapporto["strumenti"][nome] = riga
    rapporto["mde"] = Q.mde_coppie(perdite_coppie)
    rapporto["invarianza_ristretta_contro_completa_diff_max"] = diff_inv
    tmp = QUI / "esiti" / "sviluppo.json.tmp"
    tmp.write_text(json.dumps(rapporto, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, QUI / "esiti" / "sviluppo.json")
    print("scritto esiti/sviluppo.json; ristretta contro completa: diff max", diff_inv)


if __name__ == "__main__":
    main()
