"""Griglia a numero tondo .80/.20 sul Nasdaq: zone di reazione o no?

Esegue docs/ROUND_NUMBER_GRID_PREREGISTRATION.md. Riusa `classify()` della ricerca livelli
con le costanti PRE-REGISTRATE invariate, cosi' i due studi sono confrontabili.

Null: stessa geometria, FASE diversa (griglia {20+d, 80+d} mod 100). A griglia fissa il
random distance-matched non e' applicabile: la distanza determina la posizione.

Uso: python analysis/round_grid/test_80_20.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis", "level_research"))
from reaction import (REACTION, TESTED, boot_rate_diff_ci, classify,  # noqa: E402
                      N_REACT, TOUCH_WINDOW)

DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "NAS100_M5.csv")
STEP = 12          # un punto di decisione ogni 12 barre M5 (1 ora)
M_RANDOM = 5       # griglie sfasate per punto di decisione
MIN_PHASE = 10     # offset minimo dalla griglia reale (punti)
ATR_N = 14
TRAIN_FRAC = 0.70
SEED = 42
MAX_FWD = TOUCH_WINDOW + N_REACT + 2

REAL_PHASES = (20.0, 80.0)


def atr_series(h, l, c, n=ATR_N):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    out = pd.Series(tr).rolling(n).mean().to_numpy()
    return out


def nearest(price, phases, side):
    """Livello della griglia piu' vicino: sotto (SUPPORT) o sopra (RESISTANCE)."""
    base = np.floor(price / 100.0) * 100.0
    cand = [base + p + k * 100.0 for p in phases for k in (-1, 0, 1)]
    if side == "SUPPORT":
        c = [x for x in cand if x < price]
        return max(c) if c else None
    c = [x for x in cand if x > price]
    return min(c) if c else None


def run(bars, idxs, A, days, phases, rng=None, tag="real"):
    """Classifica i touch della griglia `phases` sui punti di decisione. Ritorna items (day,0/1)."""
    items = {"SUPPORT": [], "RESISTANCE": []}
    dists = []
    for i in idxs:
        atr = A[i]
        if not np.isfinite(atr) or atr <= 0:
            continue
        price = bars[i]["close"]
        ph = phases
        if rng is not None:                       # griglia SFASATA (null)
            d = rng.uniform(MIN_PHASE, 100.0 - MIN_PHASE)
            ph = tuple((p + d) % 100.0 for p in REAL_PHASES)
        fwd = bars[i + 1: i + 1 + MAX_FWD]
        if len(fwd) < MAX_FWD:
            continue
        for side in ("SUPPORT", "RESISTANCE"):
            z = nearest(price, ph, side)
            if z is None:
                continue
            dists.append(abs(price - z) / atr)
            r = classify(fwd, z, side, atr)
            if r["cls"] in TESTED:
                items[side].append((days[i], 1.0 if r["cls"] == REACTION else 0.0))
    return items, np.array(dists)


def report(real, rand, label):
    pooled_r = real["SUPPORT"] + real["RESISTANCE"]
    pooled_c = rand["SUPPORT"] + rand["RESISTANCE"]
    print(f"\n--- {label} ---")
    for side in ("SUPPORT", "RESISTANCE", "POOL"):
        r = pooled_r if side == "POOL" else real[side]
        c = pooled_c if side == "POOL" else rand[side]
        if len(r) < 30 or len(c) < 30:
            print(f"  {side:11} dati insufficienti (n_real={len(r)}, n_rand={len(c)})")
            continue
        lo, hi, pt, nd = boot_rate_diff_ci(r, c, n_boot=2000, seed=SEED)
        rr = 100 * np.mean([v for _, v in r])
        cr = 100 * np.mean([v for _, v in c])
        star = " *" if lo > 0 else ""
        print(f"  {side:11} reale={rr:5.1f}%  random={cr:5.1f}%  diff={pt:+5.2f}pt  "
              f"CI95=[{lo:+.2f},{hi:+.2f}]  n_real={len(r):6} giorni={nd}{star}")
    return pooled_r, pooled_c


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    d = pd.read_csv(DATA, parse_dates=["time"]).drop_duplicates("time").sort_values("time")
    d = d.reset_index(drop=True)
    H, L, C, O = (d["high"].to_numpy(float), d["low"].to_numpy(float),
                  d["close"].to_numpy(float), d["open"].to_numpy(float))
    A = atr_series(H, L, C)
    days = d["time"].dt.strftime("%Y-%m-%d").to_numpy()
    bars = [{"open": O[i], "high": H[i], "low": L[i], "close": C[i]} for i in range(len(d))]

    n = len(d)
    cut = int(n * TRAIN_FRAC)
    print("=" * 92)
    print("GRIGLIA .80/.20 SUL NASDAQ — zone di reazione? (pre-registrazione 2026-08-09)")
    print("=" * 92)
    print(f"Serie: {n} barre M5  {d['time'].iloc[0]} -> {d['time'].iloc[-1]}")
    print(f"Split cronologico: TRAIN {cut} barre (fino a {d['time'].iloc[cut]}) | HOLDOUT {n-cut}")

    idx_tr = [i for i in range(ATR_N + 1, cut - MAX_FWD - 1, STEP)]
    print(f"Punti di decisione TRAIN: {len(idx_tr)} (uno ogni {STEP} barre = 1h)")

    rng = np.random.default_rng(SEED)
    real_tr, dist_tr = run(bars, idx_tr, A, days, REAL_PHASES)
    rand_tr = {"SUPPORT": [], "RESISTANCE": []}
    for _ in range(M_RANDOM):
        r, _ = run(bars, idx_tr, A, days, REAL_PHASES, rng=rng)
        rand_tr["SUPPORT"] += r["SUPPORT"]; rand_tr["RESISTANCE"] += r["RESISTANCE"]

    # metrica descrittiva obbligatoria (prereg §5): quanto e' selettivo il filtro
    print(f"\nSELETTIVITA': distanza |prezzo-livello| in ATR — mediana={np.median(dist_tr):.2f}  "
          f"p10={np.percentile(dist_tr,10):.2f}  p90={np.percentile(dist_tr,90):.2f}")
    print(f"  frazione di punti con livello entro 0.10 ATR (= gia' 'al livello'): "
          f"{100*np.mean(dist_tr <= 0.10):.1f}%")

    pr, pc = report(real_tr, rand_tr, "TRAIN (70%)")
    lo, hi, pt, nd = boot_rate_diff_ci(pr, pc, n_boot=4000, seed=SEED)

    print("\n" + "=" * 92)
    print("VERDETTO PRIMARIO (soglia pre-registrata: lower bound CI 95% del POOL > 0)")
    print("=" * 92)
    print(f"  POOL TRAIN: diff = {pt:+.2f} punti percentuali   CI95 = [{lo:+.2f}, {hi:+.2f}]")
    if lo > 0:
        print("  => TRAIN POSITIVO: apro l'HOLDOUT (unica apertura consentita)")
        idx_ho = [i for i in range(cut, n - MAX_FWD - 1, STEP)]
        rng2 = np.random.default_rng(SEED + 1)
        real_ho, _ = run(bars, idx_ho, A, days, REAL_PHASES)
        rand_ho = {"SUPPORT": [], "RESISTANCE": []}
        for _ in range(M_RANDOM):
            r, _ = run(bars, idx_ho, A, days, REAL_PHASES, rng=rng2)
            rand_ho["SUPPORT"] += r["SUPPORT"]; rand_ho["RESISTANCE"] += r["RESISTANCE"]
        hr, hc = report(real_ho, rand_ho, "HOLDOUT (30%)")
        lo2, hi2, pt2, _ = boot_rate_diff_ci(hr, hc, n_boot=4000, seed=SEED)
        print(f"\n  POOL HOLDOUT: diff = {pt2:+.2f} pt   CI95 = [{lo2:+.2f}, {hi2:+.2f}]")
        print("\n  >>> CONFERMATO" if lo2 > 0 else "\n  >>> NULL sull'holdout — famiglia CLOSED")
    else:
        print("  => NULL: la fase della griglia non conta. Famiglia CLOSED, nessuna rifinitura.")
        print("     L'HOLDOUT NON viene aperto (resta sigillato per eventuali ipotesi future).")


if __name__ == "__main__":
    main()
