"""TASK 3 - Check macro decisivo per la direzione dell'oro (XAU).

Ipotesi a regola FISSA e segno NOTO dalla letteratura (niente fitting):
  oro rialzista quando il DOLLARO (DXY) scende E i RENDIMENTI (10Y) scendono.
Feature = momentum a 5 giorni di DXY e ^TNX, prese SOLO al giorno chiuso precedente
(no look-ahead). Segnale -> long/short/neutral.

Due orizzonti:
  (A) DAILY  : predice la direzione close-to-close dell'oro (10 anni, dove la macro
               dovrebbe essere piu' forte).
  (B) SESSIONE: predice la finestra London 06-13 / NY 13-21 UTC (KPI del bot, dal 2024).

Split train/test. Confronto con baseline (sempre-long, random). Robustezza su lookback 1/5/20.
Uso: python analysis/trading-bot-eval/macro_xau.py
"""
from __future__ import annotations

import bisect
import csv
import math
import random
import sys
from datetime import datetime, timedelta, timezone

DATA = "analysis/trading-bot-eval/data"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def load_daily(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                day = datetime.fromisoformat(r["time"][:19]).date()
                out.append((day, float(r["close"])))
            except (ValueError, KeyError):
                continue
    out.sort()
    return out


def load_h1(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t = datetime.fromisoformat(r["time"])
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                out.append((t, float(r["close"])))
            except (ValueError, KeyError):
                continue
    out.sort()
    return out


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def macro_signal(dxy, tnx, dates_idx, ref_day, lb=5):
    """Segnale come da giorno chiuso < ref_day. Ritorna (score, agree_call)."""
    def val_before(series, sidx, day, back):
        i = bisect.bisect_left(sidx, day)  # primo >= day -> i-1 e' l'ultimo < day
        if i - 1 - back < 0:
            return None, None
        return series[i - 1][1], series[i - 1 - back][1]
    d_now, d_prev = val_before(dxy, dates_idx["dxy"], ref_day, lb)
    t_now, t_prev = val_before(tnx, dates_idx["tnx"], ref_day, lb)
    if d_now is None or t_now is None or d_prev in (None, 0):
        return None, None
    dxy_ret = d_now / d_prev - 1
    tnx_chg = t_now - t_prev
    s = -sign(dxy_ret) - sign(tnx_chg)           # +2 = entrambi giu' (bull oro)
    score_call = sign(s)                          # long/short/neutral
    agree_call = 1 if s >= 2 else -1 if s <= -2 else 0
    return score_call, agree_call


def acc(preds, reals):
    k = n = 0
    for p, r in zip(preds, reals):
        if p == 0:
            continue
        n += 1
        k += (p == r)
    return k, n


def line(label, preds, reals, total):
    k, n = acc(preds, reals)
    if n == 0:
        print(f"    {label:16} n=   0"); return
    lo, hi = wilson(k, n)
    print(f"    {label:16} n={n:4}  hit={100*k/n:5.1f}%  CI95=[{lo:4.1f},{hi:4.1f}]  cov={100*n/total:3.0f}%")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    dxy = load_daily(f"{DATA}/DXY_D1.csv")
    tnx = load_daily(f"{DATA}/TNX_D1.csv")
    xaud = load_daily(f"{DATA}/XAU_D1.csv")
    xauh = load_h1(f"{DATA}/XAU_H1.csv")
    idx = {"dxy": [d for d, _ in dxy], "tnx": [d for d, _ in tnx]}
    rng = random.Random(42)
    ht = [t for t, _ in xauh]

    # ---------- (A) DAILY ----------
    recs = []
    for i in range(1, len(xaud)):
        day, c = xaud[i]
        prev = xaud[i - 1][1]
        real = sign(c - prev)
        if real == 0:
            continue
        sc, ag = macro_signal(dxy, tnx, idx, day, lb=5)
        if sc is None:
            continue
        recs.append({"day": day, "real": real, "score": sc, "agree": ag})
    recs.sort(key=lambda r: r["day"])
    split = recs[int(len(recs) * 0.70)]["day"]
    tr = [r for r in recs if r["day"] < split]
    te = [r for r in recs if r["day"] >= split]
    print("=" * 60)
    print(f"(A) MACRO -> DIREZIONE DAILY ORO   {recs[0]['day']} -> {recs[-1]['day']}")
    print(f"    split test da {split}")
    print("=" * 60)
    for name, rs in (("TRAIN", tr), ("TEST (holdout)", te)):
        print(f"\n  {name}  (n giorni={len(rs)})")
        reals = [r["real"] for r in rs]
        line("MACRO-score", [r["score"] for r in rs], reals, len(rs))
        line("MACRO-agree", [r["agree"] for r in rs], reals, len(rs))
        line("sempre-long", [1] * len(rs), reals, len(rs))
        line("random", [rng.choice([1, -1]) for _ in rs], reals, len(rs))

    print("\n  Robustezza lookback (MACRO-score, TRAIN daily):")
    for lb in (1, 5, 20):
        rs2 = []
        for i in range(1, len(xaud)):
            day, c = xaud[i]
            if day >= split:
                continue
            real = sign(c - xaud[i - 1][1])
            if real == 0:
                continue
            sc, _ = macro_signal(dxy, tnx, idx, day, lb=lb)
            if sc is not None:
                rs2.append((sc, real))
        line(f"lookback {lb:2}g", [p for p, _ in rs2], [r for _, r in rs2], len(rs2))

    # ---------- (B) SESSIONE ----------
    def outcome(start, end):
        i0 = bisect.bisect_left(ht, start)
        if i0 >= len(xauh) or xauh[i0][0] - start > timedelta(hours=3):
            return None
        i1 = bisect.bisect_right(ht, end) - 1
        if i1 <= i0 or xauh[i1][0] < end - timedelta(hours=3):
            return None
        e0, e1 = xauh[i0][1], xauh[i1][1]
        return sign(e1 - e0) if e0 else None

    srecs = []
    days = sorted(set(t.date() for t, _ in xauh))
    for day in days:
        for sh, eh in ((6, 13), (13, 21)):
            start = datetime(day.year, day.month, day.day, sh, tzinfo=timezone.utc)
            end = datetime(day.year, day.month, day.day, eh, tzinfo=timezone.utc)
            real = outcome(start, end)
            if not real:
                continue
            sc, ag = macro_signal(dxy, tnx, idx, day, lb=5)
            if sc is None:
                continue
            srecs.append({"day": day, "real": real, "score": sc, "agree": ag})
    srecs.sort(key=lambda r: r["day"])
    ssplit = srecs[int(len(srecs) * 0.70)]["day"]
    str_, ste = [r for r in srecs if r["day"] < ssplit], [r for r in srecs if r["day"] >= ssplit]
    print("\n" + "=" * 60)
    print(f"(B) MACRO -> DIREZIONE SESSIONE ORO (London+NY)   {srecs[0]['day']} -> {srecs[-1]['day']}")
    print("=" * 60)
    for name, rs in (("TRAIN", str_), ("TEST (holdout)", ste)):
        print(f"\n  {name}  (n sessioni={len(rs)})")
        reals = [r["real"] for r in rs]
        line("MACRO-score", [r["score"] for r in rs], reals, len(rs))
        line("MACRO-agree", [r["agree"] for r in rs], reals, len(rs))
        line("sempre-long", [1] * len(rs), reals, len(rs))
        line("random", [rng.choice([1, -1]) for _ in rs], reals, len(rs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
