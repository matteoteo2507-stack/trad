"""B1 — chiusura: il ritorno alla media esiste NELLE CODE, contro baseline random matched?

Perche' questo script esiste
----------------------------
La passata descrittiva del 2026-09-17 misurava una **pendenza lineare** su tutto l'intervallo di z.
Ma la fonte (Kichev) dice *"price deviates **significantly far** from mean"*: parla delle **code**.
E in quella passata pendenza complessiva e comportamento nelle code avevano **segni opposti** su
alcuni gruppi, il che rende la pendenza un riassunto sbagliato per questa domanda.

Quindi la passata precedente **non basta a chiudere B1**, e questo script chiude il lavoro invece di
lasciarlo al 90%.

CRITERIO DICHIARATO PRIMA DI ESEGUIRE
-------------------------------------
Statistica, per gruppo: effetto di coda **aggregato** su tutti gli strumenti, periodi di media
(3/5/10/20) e orizzonti (1-4 giorni)

    eff = media di  [ -sign(z) * (rendimento a h giorni / ATR) ]   sul decile alto di |z|

con eff **positivo** = ritorno alla media (uno scostamento alto e' seguito da un movimento contrario).

Baseline random **matched**: si ri-allinea la serie di z a quella dei rendimenti futuri con uno
**spostamento circolare** di offset casuale (>= 250 giorni). Cosi' restano identici: le due serie,
la loro autocorrelazione, il raggruppamento della volatilita', il calendario e la numerosita'.
Si rompe **solo** l'accoppiamento fra scostamento ed esito — che e' esattamente l'ipotesi nulla.
N_PERM = 300 ri-allineamenti per gruppo.

Un gruppo **conferma** se: eff osservato > 0 **e** eff osservato > 95esimo percentile del suo nullo.

VERDETTO, deciso ora:
  - **>= 5 gruppi su 8 confermano**  -> B1 resta aperta: si passa a una pre-registrazione vera.
  - **< 5 gruppi su 8**              -> **B1 CHIUSA**, con la condizione di riapertura gia' scritta.

Non consuma trial: e' una misura descrittiva con baseline, non una regola (niente soglie di
ingresso, niente stop, niente dimensionamento).

    python analysis/meanrev/tails.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")

PERIODI = (3, 5, 10, 20)
ORIZZONTI = (1, 2, 3, 4)
SD_WIN = 100
ATR_N = 14
QUANTILE_CODA = 0.90
N_PERM = 300
OFFSET_MIN = 250
SEED = 42
SOGLIA_GRUPPI = 5


def carica(sym):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_D1.csv"), parse_dates=["time"])
    return d.drop_duplicates(subset="time").sort_values("time").reset_index(drop=True)


def atr(d, n=ATR_N):
    h, l, c = d["high"].values, d["low"].values, d["close"].values
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).rolling(n).mean().values


def serie(sym):
    """Ritorna una lista di (z, fwd_atr) allineate, una per ogni (periodo, orizzonte)."""
    d = carica(sym)
    if len(d) < 600:
        return []
    c = d["close"].values
    a = atr(d)
    fuori = []
    for n in PERIODI:
        sma = pd.Series(c).rolling(n).mean().values
        dev = c - sma
        sd = pd.Series(dev).rolling(SD_WIN).std().values
        with np.errstate(invalid="ignore", divide="ignore"):
            z = dev / sd
        for h in ORIZZONTI:
            fwd = np.full(len(c), np.nan)
            fwd[:-h] = c[h:] - c[:-h]
            with np.errstate(invalid="ignore", divide="ignore"):
                f = fwd / a
            m = np.isfinite(z) & np.isfinite(f)
            if m.sum() < 500:
                continue
            fuori.append((z[m], f[m]))
    return fuori


def eff_coda(z, f):
    """Effetto di coda: positivo = ritorno alla media."""
    q = np.quantile(np.abs(z), QUANTILE_CODA)
    sel = np.abs(z) >= q
    if sel.sum() < 30:
        return np.nan, 0
    return float(np.mean(-np.sign(z[sel]) * f[sel])), int(sel.sum())


def main() -> int:
    cov = pd.read_csv(os.path.join(DATA, "_coverage.csv"))
    rng = np.random.default_rng(SEED)

    per_gruppo = {}
    for _, r in cov.iterrows():
        sym, grp = r["sym"], r["group"]
        try:
            ss = serie(sym)
        except FileNotFoundError:
            continue
        if ss:
            per_gruppo.setdefault(grp, []).extend(ss)

    print("B1 - EFFETTO NELLE CODE contro baseline random matched (0 trial)")
    print("=" * 78)
    print("eff > 0 = ritorno alla media. Nullo: ri-allineamento circolare, %d permutazioni."
          % N_PERM)
    print("Un gruppo CONFERMA se eff osservato > 0 e supera il 95esimo percentile del nullo.\n")
    print("%-10s %9s %9s %9s %7s  %s" %
          ("gruppo", "eff oss.", "nullo p50", "nullo p95", "perc.", "conferma?"))
    print("-" * 78)

    conferme = 0
    righe = []
    for grp in sorted(per_gruppo):
        coppie = per_gruppo[grp]
        # osservato: media degli effetti su tutte le serie del gruppo
        oss = np.nanmean([eff_coda(z, f)[0] for z, f in coppie])

        # nullo: stesso calcolo con z ri-allineato circolarmente
        nulli = np.empty(N_PERM)
        for k in range(N_PERM):
            vals = []
            for z, f in coppie:
                n = len(z)
                if n <= 2 * OFFSET_MIN:
                    continue
                off = int(rng.integers(OFFSET_MIN, n - OFFSET_MIN))
                e, _ = eff_coda(np.roll(z, off), f)
                vals.append(e)
            nulli[k] = np.nanmean(vals) if vals else np.nan

        p50 = float(np.nanpercentile(nulli, 50))
        p95 = float(np.nanpercentile(nulli, 95))
        perc = float(np.nanmean(nulli < oss)) * 100.0
        ok = (oss > 0) and (oss > p95)
        conferme += int(ok)
        righe.append({"gruppo": grp, "eff": oss, "p50": p50, "p95": p95,
                      "perc": perc, "conferma": ok})
        print("%-10s %+9.4f %+9.4f %+9.4f %6.1f%%  %s" %
              (grp, oss, p50, p95, perc, "SI" if ok else "no"))

    n_grp = len(righe)
    print("-" * 78)
    print("\nGruppi che confermano: **%d su %d** (soglia dichiarata: %d)"
          % (conferme, n_grp, SOGLIA_GRUPPI))
    if conferme >= SOGLIA_GRUPPI:
        print("\nVERDETTO: B1 RESTA APERTA -> serve una pre-registrazione vera (1 trial).")
    else:
        print("\nVERDETTO: **B1 CHIUSA**. Nemmeno sulle code, che sono la forma in cui la")
        print("fonte pone la domanda, il ritorno alla media batte un nullo che conserva")
        print("autocorrelazione, volatilita' e calendario.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
