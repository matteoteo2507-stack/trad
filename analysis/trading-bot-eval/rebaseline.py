"""TASK 2 - Re-baseline su dati ampi, con split train/test (XAU/BTC/EUR).

Per OGNI giorno nel dataset genera la call di sessione (London 06:00, NY 13:00 UTC)
con la logica pulita del bot (levels_engine: confluenza D/4H/1H), SOLO candele chiuse,
4H reale. Outcome = direzione della finestra di sessione su barre H1.

Confronta la call pulita con baseline (sempre-long, sempre-short, segui-daily, random)
su TRAIN (prime ~70% date) e TEST (ultime ~30% date, holdout).

Uso: python analysis/trading-bot-eval/rebaseline.py
"""
from __future__ import annotations

import bisect
import csv
import math
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

DATA = "analysis/trading-bot-eval/data"
ASSETS = ["XAU", "BTC", "EUR"]
SESSIONS = {"London": (6, 13), "NY": (13, 21)}  # (start_h, end_h) UTC


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


def load_h1(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t = datetime.fromisoformat(r["time"])
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                out.append({"t": t, "open": float(r["open"]), "high": float(r["high"]),
                            "low": float(r["low"]), "close": float(r["close"])})
            except (ValueError, KeyError):
                continue
    out.sort(key=lambda x: x["t"])
    return out


def load_d1(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                day = datetime.fromisoformat(r["time"][:19]).date()
                out.append({"date": day, "open": float(r["open"]), "high": float(r["high"]),
                            "low": float(r["low"]), "close": float(r["close"])})
            except (ValueError, KeyError):
                continue
    out.sort(key=lambda x: x["date"])
    return out


def agg4h_real(h1):
    from collections import defaultdict
    g = defaultdict(list)
    for b in h1:
        a = b["t"].replace(minute=0, second=0, microsecond=0)
        g[a.replace(hour=(a.hour // 4) * 4)].append(b)
    out = []
    for block in sorted(g):
        grp = sorted(g[block], key=lambda x: x["t"])
        if len(grp) < 4:
            continue
        out.append({"open": grp[0]["open"], "high": max(x["high"] for x in grp),
                    "low": min(x["low"] for x in grp), "close": grp[-1]["close"]})
    return out


def build(asset):
    h1 = load_h1(f"{DATA}/{asset}_H1.csv")
    d1 = load_d1(f"{DATA}/{asset}_D1.csv")
    ht = [b["t"] for b in h1]
    dd = [b["date"] for b in d1]

    def call_at(t):
        ci = bisect.bisect_right(ht, t - timedelta(hours=1))   # H1 chiuse (t_bar+1h<=t)
        h = h1[max(0, ci - 80):ci]
        di = bisect.bisect_left(dd, t.date())                  # daily chiusi (date<oggi)
        d = d1[max(0, di - 40):di]
        if len(h) < 24 or len(d) < 5:
            return None, None
        h4 = agg4h_real(h)
        if len(h4) < 5:
            return None, None
        bd = le.analyze_bias([{k: x[k] for k in ("open", "high", "low", "close")} for x in d[-30:]], "D")
        b4 = le.analyze_bias(h4[-30:], "4H")
        b1 = le.analyze_bias(h[-30:], "1H")
        conf = le.calc_confluence(bd, b4, b1)
        call = "long" if conf["score"] > 0 else "short" if conf["score"] < 0 else "neutral"
        strong = conf["bull"] == 3 or conf["bear"] == 3
        return call, strong

    def outcome(start, end):
        i0 = bisect.bisect_left(ht, start)
        if i0 >= len(h1) or h1[i0]["t"] - start > timedelta(hours=3):
            return None
        i1 = bisect.bisect_right(ht, end) - 1
        if i1 <= i0 or h1[i1]["t"] < end - timedelta(hours=3):
            return None
        e0, e1 = h1[i0]["close"], h1[i1]["close"]
        return (e1 - e0) / e0 if e0 else None

    def daily_dir(t):
        di = bisect.bisect_left(dd, t.date())
        if di == 0:
            return 0
        c = d1[di - 1]
        return 1 if c["close"] > c["open"] else -1 if c["close"] < c["open"] else 0

    recs = []
    days = sorted(set(b["t"].date() for b in h1))
    for day in days:
        for sess, (sh, eh) in SESSIONS.items():
            start = datetime(day.year, day.month, day.day, sh, tzinfo=timezone.utc)
            end = datetime(day.year, day.month, day.day, eh, tzinfo=timezone.utc)
            ret = outcome(start, end)
            if ret is None or ret == 0:
                continue
            call, strong = call_at(start)
            if call is None:
                continue
            recs.append({"ts": start, "sess": sess, "ret": ret, "call": call,
                         "strong": strong, "ddir": daily_dir(start)})
    return recs


def metrics(recs, rng):
    """Ritorna dict di (label -> (k,n)) sui vari predittori."""
    real = [1 if r["ret"] > 0 else -1 for r in recs]
    out = {}

    def acc(pred_signs, mask=None):
        k = n = 0
        for i, r in enumerate(recs):
            if mask and not mask(r):
                continue
            ps = pred_signs[i]
            if ps == 0:
                continue
            n += 1
            k += (ps == real[i])
        return k, n

    clean = [1 if r["call"] == "long" else -1 if r["call"] == "short" else 0 for r in recs]
    out["CLEAN"] = acc(clean)
    out["CLEAN-FORTE"] = acc([clean[i] if recs[i]["strong"] else 0 for i in range(len(recs))])
    out["sempre-long"] = acc([1] * len(recs))
    out["sempre-short"] = acc([-1] * len(recs))
    out["segui-daily"] = acc([r["ddir"] for r in recs])
    out["random"] = acc([rng.choice([1, -1]) for _ in recs])
    return out, len(recs)


def show(title, recs, rng):
    m, n = metrics(recs, rng)
    print(f"\n  {title}  (sessioni con outcome: {n})")
    for label in ("CLEAN", "CLEAN-FORTE", "sempre-long", "sempre-short", "segui-daily", "random"):
        k, nn = m[label]
        if nn == 0:
            print(f"    {label:13} n=   0"); continue
        lo, hi = wilson(k, nn)
        cov = 100 * nn / n
        print(f"    {label:13} n={nn:4}  hit={100*k/nn:5.1f}%  CI95=[{lo:4.1f},{hi:4.1f}]  cov={cov:3.0f}%")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rng = random.Random(42)
    for asset in ASSETS:
        recs = build(asset)
        if not recs:
            print(f"\n===== {asset}: nessun record =====")
            continue
        recs.sort(key=lambda r: r["ts"])
        split = recs[int(len(recs) * 0.70)]["ts"]
        train = [r for r in recs if r["ts"] < split]
        test = [r for r in recs if r["ts"] >= split]
        print("\n" + "=" * 66)
        print(f"{asset}   periodo {recs[0]['ts'].date()} -> {recs[-1]['ts'].date()}   "
              f"(split test da {split.date()})")
        print("=" * 66)
        show("TRAIN", train, rng)
        show("TEST (holdout)", test, rng)
        # per sessione, su tutto
        for sess in SESSIONS:
            show(f"TUTTO - {sess}", [r for r in recs if r["sess"] == sess], rng)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
