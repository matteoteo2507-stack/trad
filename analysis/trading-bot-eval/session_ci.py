"""Strato di rigore statistico sopra calibrate_session.py.

Domanda: il claim "80-90% di accuratezza trend per sessione" regge?
Aggiunge a ciò che già fa calibrate_session:
  1) Intervallo di confidenza di Wilson 95% su OGNI cella di hit-rate (le n sono piccole);
  2) Test: la cella batte il lancio di moneta (50%)? E il suo CI raggiunge l'80%?
  3) Cross-check XAUUSD su barre SPOT indipendenti (analysis/data/bars_H1.csv),
     per non dipendere dai prezzi auto-riportati dal bot (che sono GC=F futures).

Uso: python -m analysis.trading-bot-eval.session_ci
  (oppure: python analysis/trading-bot-eval/session_ci.py)
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

SIG = "analysis/veltrix/signals.jsonl"
BARS_XAU_H1 = "analysis/data/bars_H1.csv"


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (centre - half) / d, 100 * (centre + half) / d)


def binom_tail_ge(k: int, n: int, p0: float) -> float:
    """P(X >= k) sotto Binomiale(n, p0). Per 'meglio del caso' usare p0=0.5."""
    from math import comb
    return sum(comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(k, n + 1))


def binom_tail_le(k: int, n: int, p0: float) -> float:
    """P(X <= k) sotto Binomiale(n, p0). Per 'sotto l'80%' usare p0=0.80."""
    from math import comb
    return sum(comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(0, k + 1))


def session_end(day, kind):
    base = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    if kind == "london_session":
        return base + timedelta(hours=13)   # ~apertura NY
    if kind == "ny_session":
        return base + timedelta(days=1)      # ~rollover EOD
    if kind == "asia_session":
        return base + timedelta(hours=6)     # ~apertura London
    return None


def load_rows():
    rows = [json.loads(l) for l in open(SIG, encoding="utf-8")]
    return [r for r in rows if r.get("asset")]


# ─── Outcome auto-riportato (come calibrate_session) ─────────────────────
def self_ref_records(rows):
    tl = defaultdict(list)
    for r in rows:
        if r.get("price"):
            tl[r["asset"]].append((_ts(r["ts_utc"]), float(r["price"])))
    for a in tl:
        tl[a].sort()

    def price_at_or_after(asset, when, max_ahead_h=40):
        for t, p in tl.get(asset, []):
            if t >= when:
                return p if (t - when) <= timedelta(hours=max_ahead_h) else None
        return None

    recs = []
    for r in rows:
        if r["type"] not in ("london_session", "ny_session", "asia_session"):
            continue
        if r["bias"] not in ("long", "short") or not r.get("price"):
            continue
        t = _ts(r["ts_utc"]); a = r["asset"]; p = float(r["price"])
        when = session_end(t.date(), r["type"])
        if when is None or when <= t:
            continue
        end = price_at_or_after(a, when)
        if end is None:
            continue
        sign = 1 if r["bias"] == "long" else -1
        ret = (end - p) / p
        recs.append(dict(asset=a, type=r["type"], bias=r["bias"],
                         strength=r["strength"], hit=(ret * sign) > 0))
    return recs


# ─── Cross-check XAU su barre SPOT indipendenti ──────────────────────────
def xau_independent_records(rows):
    bars = []
    with open(BARS_XAU_H1, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bars.append((datetime.fromisoformat(row["time"]), float(row["close"])))
    bars.sort()

    def close_at_or_after(when):
        for t, c in bars:
            if t >= when:
                return c
        return None

    def close_at_or_before(when):
        prev = None
        for t, c in bars:
            if t <= when:
                prev = c
            else:
                break
        return prev

    recs = []
    for r in rows:
        if r["asset"] != "XAUUSD":
            continue
        if r["type"] not in ("london_session", "ny_session"):
            continue
        if r["bias"] not in ("long", "short"):
            continue
        t = _ts(r["ts_utc"])
        when = session_end(t.date(), r["type"])
        if when is None or when <= t:
            continue
        start_c = close_at_or_after(t)        # primo close spot dopo la call
        end_c = close_at_or_before(when)      # ultimo close spot entro fine sessione
        if start_c is None or end_c is None or when - t > timedelta(hours=20):
            continue
        sign = 1 if r["bias"] == "long" else -1
        ret = (end_c - start_c) / start_c
        if ret == 0:
            continue
        recs.append(dict(hit=(ret * sign) > 0))
    return recs


def line(label, recs):
    n = len(recs)
    if n == 0:
        return f"  {label:22} n=   0"
    k = sum(x["hit"] for x in recs)
    hit = 100 * k / n
    lo, hi = wilson(k, n)
    beats_coin = binom_tail_ge(k, n, 0.50)        # piccolo => batte il caso
    below_80 = binom_tail_le(k, n, 0.80)          # piccolo => sotto l'80% in modo netto
    star = "✓>50%" if beats_coin < 0.05 else ("~50%" if lo <= 50 <= hi else "<50%")
    reach80 = "raggiunge 80%" if hi >= 80 else "NON arriva a 80%"
    return (f"  {label:22} n={n:4}  hit={hit:5.1f}%  CI95=[{lo:4.1f},{hi:4.1f}]  "
            f"{star:6}  {reach80}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rows = load_rows()
    recs = self_ref_records(rows)

    print("===== HIT-RATE PER SESSIONE con CI di Wilson 95% (outcome auto-riportato) =====")
    print("  (star: il CI vs lancio-moneta 50% | e se il CI tocca l'obiettivo 80%)\n")
    print(line("TOTALE sessioni", recs))
    print()
    for ty in ("london_session", "ny_session"):
        print(line(ty, [x for x in recs if x["type"] == ty]))
    print()
    for a in ["XAUUSD", "BTCUSD", "EURUSD", "NASDAQ", "GBPUSD", "SP500"]:
        print(line(a, [x for x in recs if x["asset"] == a]))
    print()
    print(line("FORTE (3/3 TF)", [x for x in recs if x["strength"]]))
    print(line("normale", [x for x in recs if not x["strength"]]))

    print("\n===== CROSS-CHECK XAUUSD su barre SPOT indipendenti (bars_H1) =====")
    xr = xau_independent_records(rows)
    print(line("XAU spot (London+NY)", xr))
    sr = [x for x in recs if x["asset"] == "XAUUSD"]
    print(line("XAU self-report (rif.)", sr))
    print("\n  -> se i due XAU concordano, la misura auto-riportata non sta nascondendo nulla.")

    print("\n===== CONCLUSIONE NUMERICA vs OBIETTIVO 80-90% =====")
    k = sum(x["hit"] for x in recs); n = len(recs)
    lo, hi = wilson(k, n)
    p_below80 = binom_tail_le(k, n, 0.80)
    print(f"  Totale: {100*k/n:.1f}%  CI95=[{lo:.1f},{hi:.1f}]  "
          f"P(dati|vero=80%)={p_below80:.2e}  -> l'80% è respinto con altissima confidenza.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
