"""Verifica del pacchetto d'uscita `uscita/volatilita_ewma/v1` contro il codice della famiglia. 0 trial.

Sui dati di sviluppo dei nove strumenti (fino al 2024-11-08, holdout sigillato dal caricatore) confronta le previsioni
EWMA e GJR del pacchetto con quelle di `modelli.prevedi_arch`, prima di c_t, a h = 1 e h = 5. Ricalcola serie gia'
calcolate e contate: nessuna variante nuova. Scrive `esiti/pacchetto_ewma_v1.json` con lo scarto relativo massimo, le
origini confrontate, la prima origine e l'ultimo giorno di sviluppo, legato al commit (le guardie vogliono l'albero
pulito, e lo deve essere anche la cartella del pacchetto).

Uso: python magazzino/registro/codice/volatilita/verifica_pacchetto.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))

import giorni as G  # noqa: E402
import guardie  # noqa: E402
import modelli as M  # noqa: E402

PACCHETTO = G.ROOT / "uscita/volatilita_ewma/v1"
sys.path.insert(0, str(PACCHETTO))

import volatilita_ewma as V  # noqa: E402

USCITA = QUI / "esiti" / "pacchetto_ewma_v1.json"


def _scarto(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a / b - 1.0)))


def confronta(nome: str) -> dict:
    df = G.carica(nome)
    r = df["r"].to_numpy()
    riga = {"giorni": len(df), "prima_origine": str(df.index[M.W - 1].date()), "ultimo_giorno": str(df.index[-1].date())}
    for tipo in ("ewma", "gjr"):
        F = M.prevedi_arch(r, tipo)["F"]
        rif = {"h1": F[:, 0], "h5": F[:, :5].sum(axis=1)}
        p = V.previsioni_ewma(pd.Series(r)) if tipo == "ewma" else V.previsioni_gjr(pd.Series(r))
        ok = np.isfinite(rif["h1"])
        riga[tipo] = {"origini": int(ok.sum()),
                      **{"scarto_max_" + h: _scarto(p[h].to_numpy()[ok], rif[h][ok]) for h in ("h1", "h5")}}
        if tipo == "gjr":
            riga[tipo]["ripieghi_pacchetto"] = int(p["ripiego"].sum())
    return riga


def main() -> None:
    controllo = guardie.verifica()
    sporchi = subprocess.run(["git", "status", "--porcelain", "--", str(PACCHETTO)], cwd=G.ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
    if sporchi:
        raise SystemExit("cartella del pacchetto non committata:\n" + sporchi)
    strumenti = {}
    for nome in G.STRUMENTI:
        strumenti[nome] = confronta(nome)
        print(nome, json.dumps(strumenti[nome]), flush=True)
    peggiore = max(v[t]["scarto_max_" + h] for v in strumenti.values() for t in ("ewma", "gjr") for h in ("h1", "h5"))
    out = {"commit": controllo["commit"], "scarto_max_complessivo": peggiore, "strumenti": strumenti}
    testo = json.dumps(out, indent=1, ensure_ascii=False)      # calcola prima, scrive dopo
    tmp = USCITA.with_suffix(".tmp")
    tmp.write_text(testo, encoding="utf-8")
    os.replace(tmp, USCITA)
    print("scarto massimo complessivo %.3g -> %s" % (peggiore, USCITA.name))


if __name__ == "__main__":
    main()
