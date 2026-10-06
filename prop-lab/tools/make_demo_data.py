"""Genera dati SINTETICI in formato MT5 per verificare la pipeline: un controllo NEGATIVO e uno POSITIVO.
⚠️ Nessun valore di trading: servono a sapere se la pipeline distingue il niente da qualcosa.
Sostituiscili con i CSV esportati dal tuo MT5 (Simboli -> Barre -> Esporta).

  python tools/make_demo_data.py --mode null   # data/DEMO_NULL_XAUUSD_H1.csv: random walk, NESSUN vantaggio
  python tools/make_demo_data.py --mode mr     # data/DEMO_MR_XAUUSD_H1.csv: mean reversion INIETTATA

Cosa ci si aspetta:
- su DEMO_NULL la pipeline non deve PROMUOVERE niente. Se lo fa, e' rotta;
- su DEMO_MR deve trovare la mean reversion, se i dati bastano: con 3 anni e 204 varianti il DSR richiede
  Sharpe > 3 (soglia di futilita'), quindi puo' non riuscirci. Allora il limite e' la potenza, non il motore.

Correzione del 07/10 (trad). Prima c'era una sola serie, DEMO_XAUUSD_H1, con due vantaggi nascosti:
(1) una componente mean-reverting nel prezzo, non dichiarata nel nome del file; (2) massimi e minimi aggiunti
come "baffi" casuali staccati dal percorso, che danno attesa positiva a chi ha il target piu' vicino dello stop
(cioe' proprio al fade verso la media). Ora massimi e minimi sono gli estremi veri di un percorso a passi di un
minuto. Con passi da 5 minuti resta una distorsione misurabile (+0,018R su RSI(2), 05/10: lo stop viene riempito
al livello esatto anche quando il prezzo lo salta); a 1 minuto sparisce (-0,0004R).
"""
import argparse

import numpy as np
import pandas as pd

P = {"XAUUSD": (2000.0, 0.0022, 0.01, 25), "EURUSD": (1.08, 0.0011, 0.00001, 3), "NAS100": (17000.0, 0.0028, 0.01, 150)}
PASSI_ORA = 60          # passi da un minuto per barra H1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["null", "mr"], default="null")
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--years", type=float, default=3)
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--forza", type=float, default=1.0, help="moltiplicatore del richiamo verso la media (solo --mode mr)")
    a = ap.parse_args()
    out = a.out or f"data/DEMO_{a.mode.upper()}{'' if a.forza == 1 else f'_x{a.forza:g}'}_{a.symbol}_H1.csv"
    p0, vol_h, point, spread = P[a.symbol]
    rng = np.random.default_rng(a.seed)
    idx = pd.date_range("2022-01-03", periods=int(a.years * 365 * 24), freq="h")
    idx = idx[(idx.dayofweek < 5) & ~((idx.dayofweek == 4) & (idx.hour >= 23))]
    n, k = len(idx), PASSI_ORA
    hrs = np.asarray(idx.hour)
    season = 0.6 + 0.9 * np.exp(-((hrs - 15) ** 2) / 8) + 0.4 * np.exp(-((hrs - 10) ** 2) / 6)
    # volatilita' GARCH-like per ora
    v = np.empty(n); v[0] = 1.0; eps = rng.standard_t(5, n) / np.sqrt(5 / 3)
    for i in range(1, n):
        v[i] = 0.05 + 0.90 * v[i - 1] + 0.05 * eps[i - 1] ** 2
    sig = vol_h * np.sqrt(v) * season
    passi = rng.standard_t(5, (n, k)) / np.sqrt(5 / 3) * (sig[:, None] / np.sqrt(k))
    if a.mode == "null":
        logp = np.log(p0) + np.cumsum(passi.ravel()).reshape(n, k)
    else:
        # mean reversion DICHIARATA: richiamo verso una media mobile lenta del log-prezzo, piu' un drift di regime
        # a blocchi di 500 ore. Stessa forza per ora della versione originale (0,006 e 0,995 per ora).
        regime = np.repeat(rng.normal(0, vol_h * 0.04, n // 500 + 1), 500)[:n]
        kappa, lam = 0.006 * a.forza / k, 0.995 ** (1 / k)
        flat = passi.ravel(); lp = np.empty(flat.size); x = anchor = np.log(p0)
        drift = np.repeat(regime / k, k)
        for j in range(flat.size):
            anchor = lam * anchor + (1 - lam) * x
            x = x + drift[j] - kappa * (x - anchor) + flat[j]
            lp[j] = x
        logp = lp.reshape(n, k)
    prev = np.r_[np.log(p0), logp[:-1, -1]]
    o, c = prev, logp[:, -1]
    h = np.maximum(o, logp.max(axis=1)); l = np.minimum(o, logp.min(axis=1))
    dig = int(round(-np.log10(point)))
    sp = np.maximum(1, spread * (1 + 0.5 * (hrs < 2) + rng.exponential(0.2, n))).astype(int)
    df = pd.DataFrame({"<DATE>": idx.strftime("%Y.%m.%d"), "<TIME>": idx.strftime("%H:%M:%S"),
                       "<OPEN>": np.exp(o).round(dig), "<HIGH>": np.exp(h).round(dig), "<LOW>": np.exp(l).round(dig),
                       "<CLOSE>": np.exp(c).round(dig), "<TICKVOL>": rng.integers(500, 5000, n), "<VOL>": 0, "<SPREAD>": sp})
    df.to_csv(out, sep="\t", index=False)
    print(f"{out}: {n} barre {idx[0]} -> {idx[-1]} (modo {a.mode})")


if __name__ == "__main__":
    main()
