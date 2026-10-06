"""Genera dati SINTETICI in formato MT5 per provare la pipeline senza dati reali.
⚠️ I risultati su questi dati NON hanno alcun valore di trading: servono solo a verificare che tutto giri.
Sostituiscili con i CSV esportati dal tuo MT5 (Strumenti -> Centro Storico / Simboli -> Barre -> Esporta).

python tools/make_demo_data.py --symbol XAUUSD --years 3 --out data/DEMO_XAUUSD_H1.csv
"""
import argparse
import numpy as np
import pandas as pd

P = {"XAUUSD": (2000.0, 0.0022, 0.01, 25), "EURUSD": (1.08, 0.0011, 0.00001, 3), "NAS100": (17000.0, 0.0028, 0.01, 150)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="XAUUSD"); ap.add_argument("--years", type=float, default=3)
    ap.add_argument("--out", default="data/DEMO_XAUUSD_H1.csv"); ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    p0, vol_h, point, spread = P[a.symbol]
    rng = np.random.default_rng(a.seed)
    idx = pd.date_range("2022-01-03", periods=int(a.years * 365 * 24), freq="h")
    idx = idx[(idx.dayofweek < 5) & ~((idx.dayofweek == 4) & (idx.hour >= 23))]
    n = len(idx)
    hrs = np.asarray(idx.hour)
    season = 0.6 + 0.9 * np.exp(-((hrs - 15) ** 2) / 8) + 0.4 * np.exp(-((hrs - 10) ** 2) / 6)
    # volatilità GARCH-like
    v = np.empty(n); v[0] = 1.0; eps = rng.standard_t(5, n) / np.sqrt(5 / 3)
    for i in range(1, n):
        v[i] = 0.05 + 0.90 * v[i - 1] + 0.05 * eps[i - 1] ** 2
    sig = vol_h * np.sqrt(v) * season
    # rendimento = drift di regime + componente mean-reverting (OU sul log prezzo vs media mobile lenta)
    regime = np.repeat(rng.normal(0, vol_h * 0.04, n // 500 + 1), 500)[:n]
    logp = np.empty(n); logp[0] = np.log(p0); anchor = logp[0]
    for i in range(1, n):
        anchor = 0.995 * anchor + 0.005 * logp[i - 1]
        mr = -0.006 * (logp[i - 1] - anchor)
        logp[i] = logp[i - 1] + regime[i] + mr + sig[i] * eps[i]
    close = np.exp(logp)
    open_ = np.r_[close[0], close[:-1]] * np.exp(rng.normal(0, vol_h * 0.05, n))
    rng_hl = np.abs(rng.normal(0, 1, (n, 2))) * sig[:, None] * close[:, None] * 0.8
    high = np.maximum(open_, close) + rng_hl[:, 0]
    low = np.minimum(open_, close) - rng_hl[:, 1]
    sp = np.maximum(1, spread * (1 + 0.5 * (hrs < 2) + rng.exponential(0.2, n))).astype(int)
    dig = int(round(-np.log10(point)))
    out = pd.DataFrame({"<DATE>": idx.strftime("%Y.%m.%d"), "<TIME>": idx.strftime("%H:%M:%S"),
                        "<OPEN>": open_.round(dig), "<HIGH>": high.round(dig), "<LOW>": low.round(dig),
                        "<CLOSE>": close.round(dig), "<TICKVOL>": rng.integers(500, 5000, n), "<VOL>": 0, "<SPREAD>": sp})
    out.to_csv(a.out, sep="\t", index=False)
    print(f"{a.out}: {n} barre {idx[0]} -> {idx[-1]}")


if __name__ == "__main__":
    main()
