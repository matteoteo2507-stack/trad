"""Calibrazione del test di H1 su sedute sintetiche, PRIMA di toccare il mercato (controllo negativo e positivo).

Usa il codice del test (`esegui_test.py`: stesse funzioni, stesse soglie) su serie seminate. Scenari:
- nullo, meta' effetto, effetto pieno (correlazione di riferimento del train): falsi positivi e potenza;
- quattro nulli "cattivi" della revisione G1 dell'11/10: effetto che vive solo nella taglia, asimmetria con deriva
  negativa dell'ultima mezz'ora, volatilita' dell'ultima mezz'ora legata al movimento del giorno, segni autocorrelati.
Misura la distorsione del divario sotto il nullo (da cui B_NULL), quante volte il test dice PASSA, quanto pesa la
guardia a taglia fissa, il rapporto fra effetto realizzato e atteso, e l'errore del CLOSED a meta' effetto.
Per velocita' usa meno repliche del test vero (bootstrap 1.000 invece di 5.000, 300 spostamenti invece di 1.000).

Uso: python analysis/ultima_mezzora/calibra_nullo.py [--serie 300] [--processi 6]
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import esegui_test as t

RHO = t.RHO_RIF["train"]
SCENARI = {
    "nullo": dict(forza=0.0),
    "meta' effetto": dict(forza=RHO / 2),
    "effetto pieno": dict(forza=RHO),
    "solo nella taglia": dict(forza=0.0, solo_taglia=0.50, deriva_rod=0.0),
    "asimmetria e deriva negativa": dict(forza=0.0, a_giu=1.45, a_su=0.75, spinta=0.12, deriva_lh=-2.0,
                                         deriva_rod=0.0),
    "volatilita' legata al movimento": dict(forza=0.0, vol_legata=1.0),
    "segni autocorrelati": dict(forza=0.0, p_resta=0.85),
}


def una(arg: tuple) -> dict:
    """Una serie sintetica passata per l'analisi e il verdetto del test."""
    nome, seme, n = arg
    primari = t.GRUPPI["train"]["primari"]
    dati = {k: t.prepara(v) for k, v in t.sedute_sintetiche(seme, n=n, nomi=primari, **SCENARI[nome]).items()}
    M = t.allinea(dati, primari)
    A = t.analizza(M, np.array([t.COSTI_PB[k] for k in primari]), n_spost=300, n_boot=1000, seme=seme)
    etichetta, atteso, _ = t.verdetto(A, "train")
    f = A["divario_fisso"]
    return {"divario": A["divario"]["media"], "low": A["divario"]["low"], "mde": A["divario"]["mde"],
            "atteso": atteso, "guardia": f["media"] > t.Z_GUARDIA * f["es"], "etichetta": etichetta}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serie", type=int, default=300)
    ap.add_argument("--n", type=int, default=1540, help="sedute per serie (come il train)")
    ap.add_argument("--processi", type=int, default=6)
    args = ap.parse_args()
    print(f"B_NULL {t.B_NULL}; guardia a taglia fissa: divario > {t.Z_GUARDIA} errori standard; sedute per serie "
          f"{args.n}; serie per scenario {args.serie}")
    with ProcessPoolExecutor(args.processi) as pool:
        for nome in SCENARI:
            ris = list(pool.map(una, [(nome, 1000 + i, args.n) for i in range(args.serie)], chunksize=10))
            d = np.array([r["divario"] for r in ris])
            es = d.std(ddof=1) / np.sqrt(len(d))
            conta = Counter(r["etichetta"] for r in ris)
            sopra = [r for r in ris if r["low"] > t.B_NULL]
            print(f"\n=== {nome}  {SCENARI[nome]}")
            print(f"divario medio {d.mean():+.3f} pb [{d.mean() - 1.96 * es:+.3f}; {d.mean() + 1.96 * es:+.3f}] | "
                  f"atteso medio a correlazione piena {np.mean([r['atteso'] for r in ris]):.2f} pb | "
                  f"MDE mediano {np.median([r['mde'] for r in ris]):.2f} pb")
            print(f"limite basso > B_NULL in {len(sopra) / len(ris):.1%} delle serie; fra queste la guardia passa in "
                  f"{(np.mean([r['guardia'] for r in sopra]) if sopra else float('nan')):.1%} | guardia da sola: "
                  f"{np.mean([r['guardia'] for r in ris]):.1%}")
            print("verdetti: " + ", ".join(f"{k} {v / len(ris):.1%}" for k, v in sorted(conta.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
