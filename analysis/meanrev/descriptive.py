"""B1 — Esiste ritorno alla media su D1, e dove? MISURA DESCRITTIVA, non una regola.

Dichiarato PRIMA di eseguire
----------------------------
Questo script **non e' un test di strategia** e **non consuma trial**: non ha soglie di
ingresso, non ha stop, non produce un GO/NO-GO. Misura una relazione condizionata e
riporta **l'intera mappa**, non il suo massimo. Stessa natura del lavoro sulle escursioni
in R (backlog B3): una misura descrittiva non elegge un vincitore.

Se da qui nascera' una regola, quella regola richiedera' una **pre-registrazione a parte**
con i parametri fissati prima, e quella si' consumera' un trial.

Cosa dice davvero la fonte (Kichev, sez. 6 della trascrizione)
--------------------------------------------------------------
    | Mean Reversion | Price deviates significantly far from mean |
    | Exit after reversion or fixed period (1-4 days) | Days |

**Tutto qui.** Nessun periodo della media, nessuna soglia, nessuno stop. Il backlog
attribuiva a B1 una spec molto piu' precisa (`|close - SMA5|` oltre una soglia normalizzata):
quei dettagli **non sono nella fonte**, sono nostri. Quindi la fonte fornisce una
**famiglia** e un **orizzonte**, non una regola pronta: ogni parametro in piu' lo scegliamo
noi, ed e' li' che entra la molteplicita'.

Cosa misura
-----------
Per ogni strumento e per ogni periodo di media n:
    z_t   = (close_t - SMA_n(close)_t) / sd(close - SMA_n)   [sd su finestra mobile]
    fwd_h = (close_{t+h} - close_t) / ATR_t                   [h = 1..4 giorni]
e riporta la **pendenza** di fwd_h su z_t. Pendenza **negativa** = ritorno alla media;
positiva = continuazione. Il segno e' il risultato; la dimensione va letta con i costi.

Tutto e' calcolato solo su informazione passata al tempo t (SMA, sd e ATR fino a t).

    python analysis/meanrev/descriptive.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")

PERIODI = (3, 5, 10, 20)        # la mappa, non una scelta
ORIZZONTI = (1, 2, 3, 4)        # l'unico numero che la fonte da' davvero
SD_WIN = 100                    # finestra per normalizzare lo scostamento
ATR_N = 14


def carica(sym):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_D1.csv"), parse_dates=["time"])
    return d.drop_duplicates(subset="time").sort_values("time").reset_index(drop=True)


def atr(d, n=ATR_N):
    h, l, c = d["high"].values, d["low"].values, d["close"].values
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).rolling(n).mean().values


def misura(sym):
    d = carica(sym)
    if len(d) < 400:
        return []
    c = d["close"].values
    a = atr(d)
    out = []
    for n in PERIODI:
        sma = pd.Series(c).rolling(n).mean().values
        dev = c - sma
        sd = pd.Series(dev).rolling(SD_WIN).std().values
        with np.errstate(invalid="ignore", divide="ignore"):
            z = dev / sd
        for h in ORIZZONTI:
            fwd = np.full(len(c), np.nan)
            fwd[:-h] = (c[h:] - c[:-h])
            with np.errstate(invalid="ignore", divide="ignore"):
                fwd_atr = fwd / a
            m = np.isfinite(z) & np.isfinite(fwd_atr)
            if m.sum() < 300:
                continue
            zz, ff = z[m], fwd_atr[m]
            # pendenza OLS di fwd su z, e correlazione
            slope = np.polyfit(zz, ff, 1)[0]
            corr = np.corrcoef(zz, ff)[0, 1]
            # effetto nelle code: media di fwd quando |z| e' alto, col segno girato
            # (se c'e' ritorno alla media, uno z alto -> fwd negativo, e viceversa)
            q = np.quantile(np.abs(zz), 0.90)
            est = np.abs(zz) >= q
            eff = float(np.mean(-np.sign(zz[est]) * ff[est]))
            out.append({"sym": sym, "n": n, "h": h, "slope": slope,
                        "corr": corr, "eff_code": eff, "oss": int(m.sum())})
    return out


def main() -> int:
    cov = pd.read_csv(os.path.join(DATA, "_coverage.csv"))
    righe = []
    for sym in cov["sym"]:
        try:
            righe += misura(sym)
        except FileNotFoundError:
            pass
    df = pd.DataFrame(righe).merge(cov[["sym", "group"]], on="sym", how="left")
    if df.empty:
        print("nessun dato")
        return 1

    print("B1 - RITORNO ALLA MEDIA SU D1: misura descrittiva (0 trial)")
    print("=" * 78)
    print("Universo: %d strumenti, %d gruppi, 2012-2026.\n"
          % (df["sym"].nunique(), df["group"].nunique()))
    print("Pendenza di (rendimento a h giorni / ATR) su z = scostamento normalizzato.")
    print("NEGATIVA = ritorno alla media.  POSITIVA = continuazione.\n")

    print("--- La mappa intera: pendenza media per periodo x orizzonte ---")
    piv = df.pivot_table(index="n", columns="h", values="slope", aggfunc="mean")
    print(piv.round(4).to_string())
    print()

    print("--- Per gruppo (media su tutti i periodi e orizzonti) ---")
    g = df.groupby("group").agg(slope=("slope", "mean"),
                                corr=("corr", "mean"),
                                eff_code=("eff_code", "mean"),
                                n_str=("sym", "nunique")).sort_values("slope")
    print(g.round(4).to_string())
    print()

    neg = int((df.groupby("sym")["slope"].mean() < 0).sum())
    tot = df["sym"].nunique()
    print("Strumenti con pendenza media negativa (ritorno alla media): %d su %d"
          % (neg, tot))
    print("Gruppi con pendenza media negativa: %d su %d"
          % (int((g["slope"] < 0).sum()), len(g)))
    print()
    print("NOTA sui costi: 'eff_code' e' in unita' di ATR giornaliero. Lo spread su D1")
    print("vale una frazione molto piccola dell'ATR, ma NON e' zero e qui non e' sottratto.")
    print("Nessuna riga di questa tabella e' un risultato: e' la mappa da cui, semmai,")
    print("si sceglie UNA configurazione da pre-registrare.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
