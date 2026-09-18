"""A5 - ORB v2: il NO-GO regge anche con la convenzione intrabar opposta?

Perche' esiste
--------------
`backtest_v2.py` calcola **due** risultati per ogni trade -- `R_pess` e `R_opt`,
che differiscono per l'ordine assunto degli eventi dentro la stessa barra M5
(stop prima del target, e breakeven prima o dopo lo stop) -- ma il verdetto
stampato usa **solo** `R_pess`. La colonna ottimistica e' calcolata e mai letta.

Su un NO-GO questo e' il verso pericoloso: la convenzione pessimistica **deprime**
il risultato, quindi potrebbe aver prodotto lei il verdetto. Il 2026-09-18 abbiamo
visto la stessa forbice valere **0,82R** sul baseline casuale del copier mentore.

Qui si stampano entrambe, affiancate, sulla stessa scomposizione del verdetto
originale (curva ADX, primario, no-news, TRAIN/TEST). Non si cambia nessuna
soglia e non si cerca nessun parametro: si misura **quanto del verdetto dipende
da una convenzione mai dichiarata**.

    python analysis/opening_range/audit_convenzioni.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import quant_metrics as qm   # noqa: E402
from backtest import GAP_THRESH        # noqa: E402
from backtest_v2 import ADX_MIN_DEFAULT, run   # noqa: E402


K_POTENZA = 2.80   # alpha 0,05 bilaterale, potenza 80%


def stat(g, col):
    v = np.asarray(g[col].values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 25:
        return "n=%-4d (pochi)" % len(v), None
    b = qm.bca_bootstrap_ci(v, metric=lambda x: float(np.mean(x)), conf=0.95,
                            n_boot=1500, seed=42)
    return ("n=%-4d E[R]=%+.3f  CI=[%+.3f,%+.3f]%s"
            % (len(v), v.mean(), b["low"], b["high"], " *" if b["low"] > 0 else ""),
            v.mean())


def potenza(g, col="R_pess"):
    """MDE: il piu' piccolo effetto che questo campione poteva vedere."""
    v = np.asarray(g[col].values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 25:
        return None, None, None
    sd = float(v.std(ddof=1))
    mde = K_POTENZA * sd / np.sqrt(len(v))
    b = qm.bca_bootstrap_ci(v, metric=lambda x: float(np.mean(x)), conf=0.95,
                            n_boot=1500, seed=42)
    return mde, sd, b["high"]


def riga(et, g):
    sp, mp = stat(g, "R_pess")
    so, mo = stat(g, "R_opt")
    delta = ("  forbice %+.3f R" % (mo - mp)) if (mp is not None and mo is not None) else ""
    print("    %-16s pess  %s" % (et, sp))
    print("    %-16s opt   %s%s" % ("", so, delta))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("A5 - ORB v2: il verdetto contro la convenzione intrabar")
    print("=" * 78)
    print("Il NO-GO del 2026-07-16 e' stato dichiarato sulla sola colonna PESSIMISTICA.")
    print("Qui le due convenzioni sono affiancate. La distanza fra loro e' la misura")
    print("di quanto non sappiamo su cosa succede dentro la barra M5.\n")
    for sym in ("NAS100", "SPX500"):
        df = run(sym)
        nan_opt = int((~np.isfinite(df["R_opt"].values.astype(float))).sum())
        print("===== %s  (n=%d eseguiti, di cui %d senza esito sotto 'opt') ====="
              % (sym, len(df), nan_opt))
        prim = df[df["adx"] >= ADX_MIN_DEFAULT]
        news_ok = ~prim["nfp"] & (prim["gap"] <= GAP_THRESH)
        riga("tutti ADX>=25", prim)
        riga("no-news", prim[news_ok])
        riga("TRAIN '12-'19", prim[prim["year"] <= 2019])
        riga("TEST  '20-'26", prim[prim["year"] >= 2020])
        print()
        print("    POTENZA - il piu' piccolo effetto che questo campione poteva vedere")
        for et, g in (("tutti ADX>=25", prim),
                      ("TRAIN '12-'19", prim[prim["year"] <= 2019]),
                      ("TEST  '20-'26", prim[prim["year"] >= 2020])):
            mde, sd, hi = potenza(g)
            if mde is None:
                continue
            print("      %-16s sd=%.3f  MDE=%.3f R   estremo alto del CI=%+.3f R  %s"
                  % (et, sd, mde, hi,
                     "<- il CI arriva in territorio TRADABILE" if hi > 0.05 else ""))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
