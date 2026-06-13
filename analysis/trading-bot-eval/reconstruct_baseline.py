"""TASK 1 - Baseline onesto, look-ahead-free, riproducibile (XAUUSD).

Ricostruisce la call di sessione del bot con il port fedele (levels_engine.py) ma:
  - SOLO candele CHIUSE all'istante della call (niente candela viva);
  - 4H allineato ai VERI boundary UTC (00/04/08/12/16/20), non blocchi-di-4;
  - outcome misurato su barre SPOT XAUUSD (analysis/data/bars_H1.csv).

Confronta 4 cose sullo STESSO outcome spot e sulle stesse date:
  A) CLEAN      = logica pulita, candele chiuse, 4H reale     <- il vero baseline
  B) LOOK-AHEAD = stessa logica ma include la candela viva    <- quanto gonfiava il LA
  C) BOT POSTED = le call realmente pubblicate (signals.jsonl)
  D) baseline   = 'sempre short' (drift del periodo) e random

Uso: python analysis/trading-bot-eval/reconstruct_baseline.py
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

D1 = "analysis/data/bars_D1.csv"
H1 = "analysis/data/bars_H1.csv"
SIG = "analysis/veltrix/signals.jsonl"


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_bars(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({"t": datetime.fromisoformat(r["time"]),
                        "open": float(r["open"]), "high": float(r["high"]),
                        "low": float(r["low"]), "close": float(r["close"])})
    out.sort(key=lambda x: x["t"])
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def session_end(day, kind):
    base = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    if kind == "london_session":
        return base + timedelta(hours=13)
    if kind == "ny_session":
        return base + timedelta(days=1)
    return None


def agg4h_real(h1):
    """4H reale: blocchi ancorati a 00/04/08/12/16/20 UTC, solo blocchi completi (4h)."""
    groups = defaultdict(list)
    for b in h1:
        a = b["t"].replace(minute=0, second=0, microsecond=0)
        block = a.replace(hour=(a.hour // 4) * 4)
        groups[block].append(b)
    out = []
    for block in sorted(groups):
        g = sorted(groups[block], key=lambda x: x["t"])
        if len(g) < 4:
            continue
        out.append({"open": g[0]["open"], "high": max(x["high"] for x in g),
                    "low": min(x["low"] for x in g), "close": g[-1]["close"]})
    return out


def make_call(d1, h1all, t, lookahead=False):
    """Genera la call di sessione (long/short/neutral) come confluenza D/4H/1H."""
    if lookahead:
        d = [b for b in d1 if b["t"] <= t]                       # include daily in formazione
        h = [b for b in h1all if b["t"] <= t]                    # include l'ora in formazione
    else:
        d = [b for b in d1 if b["t"].date() < t.date()]          # solo daily chiusi
        h = [b for b in h1all if b["t"] + timedelta(hours=1) <= t]  # solo ore chiuse
    if len(d) < 5 or len(h) < 8:
        return None
    h4 = agg4h_real(h)
    if len(h4) < 5:
        return None
    bd = le.analyze_bias(d[-30:], "D")
    b4 = le.analyze_bias(h4[-30:], "4H")
    b1 = le.analyze_bias(h[-30:], "1H")
    conf = le.calc_confluence(bd, b4, b1)
    if conf["score"] > 0:
        return "long"
    if conf["score"] < 0:
        return "short"
    return "neutral"


def outcome(h1all, t, kind):
    when = session_end(t.date(), kind)
    if when is None or when <= t or (when - t) > timedelta(hours=20):
        return None
    start = next((b["close"] for b in h1all if b["t"] >= t), None)
    end = None
    for b in h1all:
        if b["t"] <= when:
            end = b["close"]
        else:
            break
    if start is None or end is None or start == 0:
        return None
    return (end - start) / start


def hit_line(label, hits):
    n = len(hits)
    if n == 0:
        return f"  {label:24} n=  0"
    k = sum(hits)
    lo, hi = wilson(k, n)
    return f"  {label:24} n={n:3}  hit={100*k/n:5.1f}%  CI95=[{lo:4.1f},{hi:4.1f}]"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1 = load_bars(D1)
    h1 = load_bars(H1)
    rows = [json.loads(l) for l in open(SIG, encoding="utf-8")]
    xs = [r for r in rows if r.get("asset") == "XAUUSD"
          and r["type"] in ("london_session", "ny_session")]

    rng = random.Random(42)
    clean, look, posted, always_short, rand = [], [], [], [], []
    cov_clean = cov_look = n_eval = 0
    per_sess = defaultdict(lambda: {"clean": [], "posted": []})

    for r in xs:
        t = _ts(r["ts_utc"])
        ret = outcome(h1, t, r["type"])
        if ret is None or ret == 0:
            continue
        n_eval += 1
        real_sign = 1 if ret > 0 else -1

        cc = make_call(d1, h1, t, lookahead=False)
        lc = make_call(d1, h1, t, lookahead=True)
        if cc in ("long", "short"):
            cov_clean += 1
            h = (1 if cc == "long" else -1) == real_sign
            clean.append(h); per_sess[r["type"]]["clean"].append(h)
        if lc in ("long", "short"):
            cov_look += 1
            look.append((1 if lc == "long" else -1) == real_sign)

        if r["bias"] in ("long", "short"):
            h = (1 if r["bias"] == "long" else -1) == real_sign
            posted.append(h); per_sess[r["type"]]["posted"].append(h)

        always_short.append(real_sign == -1)
        rand.append((rng.choice([1, -1])) == real_sign)

    print("=" * 64)
    print("TASK 1 - BASELINE ONESTO XAUUSD (call di sessione, outcome SPOT)")
    print(f"Sessioni valutabili: {n_eval}   (London+NY, Apr-Giu 2026)")
    print("=" * 64)
    print("\n--- HIT-RATE (sulle stesse date/outcome) ---")
    print(hit_line("A) CLEAN (no look-ahead)", clean),
          f"  coverage={100*cov_clean/n_eval:.0f}%")
    print(hit_line("B) LOOK-AHEAD (cand. viva)", look),
          f"  coverage={100*cov_look/n_eval:.0f}%")
    print(hit_line("C) BOT POSTED (reale)", posted))
    print(hit_line("D) baseline 'sempre short'", always_short))
    print(hit_line("D) baseline random", rand))

    if clean and look:
        print(f"\n  >>> Inflazione da look-ahead (B - A) = "
              f"{100*sum(look)/len(look) - 100*sum(clean)/len(clean):+.1f} punti")

    print("\n--- CLEAN per sessione ---")
    for ty in ("london_session", "ny_session"):
        print(hit_line(ty, per_sess[ty]["clean"]))
    print("\n--- BOT POSTED per sessione (riferimento) ---")
    for ty in ("london_session", "ny_session"):
        print(hit_line(ty, per_sess[ty]["posted"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
