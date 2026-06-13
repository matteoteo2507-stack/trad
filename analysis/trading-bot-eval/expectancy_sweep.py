"""Test sweep+reclaim sui livelli XAU spot (13 anni) — il "contesto" che dovrebbe
amplificare l'edge sottile del livello-nudo (+0.10R) in expectancy tradabile.

Setup (su H1):
  - Supporto: barra che FORA sotto il livello (low < liv - tol) ma CHIUDE sopra
    (close > liv)  -> sweep della liquidita' sell-side + reclaim  -> LONG.
    Entry = close della barra di reclaim;  SL = wick_low - buf (oltre il wick);
    TP = RR * (entry - SL).
  - Resistenza: speculare -> SHORT.
Confronto con lo stesso setup su un livello CASUALE (drift control) e con il
baseline naive (fade cieco, ~+0.10R). Split per epoca.

Uso: python analysis/trading-bot-eval/expectancy_sweep.py
"""
from __future__ import annotations

import bisect
import csv
import random
import statistics as st
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

D1P = "analysis/trading-bot-eval/data/XAU_spot_D1.csv"
H1P = "analysis/trading-bot-eval/data/XAU_spot_H1.csv"
SESSION = (6, 21)
K_TOL = 0.10
K_BUF = 0.10
K_RAND = 6.0
RRS = [1.5, 2.0, 3.0]
MAX_HOLD = 24
H1_WINDOW = 60
ATR_N = 14
START_YEAR = 2013
MIN_SL = 0.10   # sl_dist minimo in unita' di ATR


def load(path):
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


def atr_series(h1, n=ATR_N):
    atr = [None] * len(h1)
    trs = []
    for i in range(len(h1)):
        tr = (h1[i]["high"] - h1[i]["low"]) if i == 0 else max(
            h1[i]["high"] - h1[i]["low"], abs(h1[i]["high"] - h1[i - 1]["close"]),
            abs(h1[i]["low"] - h1[i - 1]["close"]))
        trs.append(tr)
        if i >= n:
            atr[i] = sum(trs[i - n + 1:i + 1]) / n
    return atr


def find_setup(h1, s_i, e_i, level, side, tol):
    for j in range(s_i, e_i):
        b = h1[j]
        if side == "S" and b["low"] < level - tol and b["close"] > level:
            return j, b["low"]
        if side == "R" and b["high"] > level + tol and b["close"] < level:
            return j, b["high"]
    return None, None


def resolve(h1, i0, entry, side, sl, tp, sl_dist):
    last = h1[i0]["close"] if i0 < len(h1) else entry
    rr = abs(tp - entry) / sl_dist
    for j in range(i0, min(i0 + MAX_HOLD, len(h1))):
        b = h1[j]
        last = b["close"]
        if side == "S":
            if b["low"] <= sl:
                return -1.0
            if b["high"] >= tp:
                return rr
        else:
            if b["high"] >= sl:
                return -1.0
            if b["low"] <= tp:
                return rr
    return (last - entry) / sl_dist if side == "S" else (entry - last) / sl_dist


def sim(h1, s_i, e_i, price, side, rr, atr, buf, rng=None, randomize=False):
    p = price + rng.uniform(-K_RAND * atr, K_RAND * atr) if randomize else price
    j, wick = find_setup(h1, s_i, e_i, p, side, K_TOL * atr)
    if j is None:
        return None
    entry = h1[j]["close"]
    if side == "S":
        sl = wick - buf
        sl_dist = entry - sl
        if sl_dist < MIN_SL * atr:
            return None
        tp = entry + rr * sl_dist
    else:
        sl = wick + buf
        sl_dist = sl - entry
        if sl_dist < MIN_SL * atr:
            return None
        tp = entry - rr * sl_dist
    return resolve(h1, j + 1, entry, side, sl, tp, sl_dist)


def explin(label, rs):
    n = len(rs)
    if n == 0:
        return f"    {label:12} n=   0"
    return f"    {label:12} n={n:5}  E[R]={st.mean(rs):+5.2f}  win={100*sum(1 for r in rs if r>0)/n:4.0f}%"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1, h1 = load(D1P), load(H1P)
    if not h1:
        print("Manca XAU_spot_H1.csv (export_mt5_spot.py)."); return 1
    atr = atr_series(h1)
    d1_by_date = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by_date)
    h1_t = [b["t"] for b in h1]
    rng = random.Random(7)
    real = {rr: {} for rr in RRS}
    ctrl = {rr: {} for rr in RRS}
    era_real = {rr: {} for rr in RRS}
    era_ctrl = {rr: {} for rr in RRS}

    def era_of(y):
        return "2013-2018" if y <= 2018 else "2019-2022" if y <= 2022 else "2023-2026"

    days = sorted({b["t"].date() for b in h1 if b["t"].year >= START_YEAR})
    for day in days:
        di = bisect.bisect_left(d1_dates, day)
        if di == 0:
            continue
        prev = d1_by_date[d1_dates[di - 1]]
        ss = datetime(day.year, day.month, day.day, SESSION[0], tzinfo=timezone.utc)
        se = datetime(day.year, day.month, day.day, SESSION[1], tzinfo=timezone.utc)
        s_i, e_i = bisect.bisect_left(h1_t, ss), bisect.bisect_left(h1_t, se)
        if e_i - s_i < 6 or s_i == 0:
            continue
        a = atr[s_i - 1]
        if not a or a <= 0:
            continue
        buf = K_BUF * a
        levels = [("PDH", prev["high"], "R"), ("PDL", prev["low"], "S")]
        ci = bisect.bisect_right(h1_t, ss - timedelta(hours=1))
        hwin = h1[max(0, ci - H1_WINDOW):ci]
        if len(hwin) >= 5:
            kl = le.get_key_levels(hwin)
            for p in kl["supports"][:3]:
                levels.append(("Swing_S", p, "S"))
            for p in kl["resistances"][:3]:
                levels.append(("Swing_R", p, "R"))
        era = era_of(day.year)
        for typ, price, side in levels:
            for rr in RRS:
                r = sim(h1, s_i, e_i, price, side, rr, a, buf)
                if r is not None:
                    real[rr].setdefault(typ, []).append(r)
                    era_real[rr].setdefault(era, []).append(r)
                rc = sim(h1, s_i, e_i, price, side, rr, a, buf, rng=rng, randomize=True)
                if rc is not None:
                    era_ctrl[rr].setdefault(era, []).append(rc)
                    ctrl[rr].setdefault("_all", []).append(rc)

    print("=" * 68)
    print("SWEEP+RECLAIM sui livelli XAU spot — 13 anni (baseline naive ~ +0.10R)")
    print("=" * 68)
    for rr in RRS:
        all_real = [r for k, v in real[rr].items() for r in v]
        all_ctrl = ctrl[rr].get("_all", [])
        print(f"\n--- RR 1:{rr} ---")
        print("  SWEEP+RECLAIM reale:")
        print(explin("TOTALE", all_real))
        for typ in ("PDH", "PDL", "Swing_S", "Swing_R"):
            print(explin(typ, real[rr].get(typ, [])))
        print("  controllo random (sweep+reclaim su livello casuale):")
        print(explin("TOTALE", all_ctrl))
        if all_real and all_ctrl:
            d = st.mean(all_real) - st.mean(all_ctrl)
            print(f"  -> E[R] reale - random = {d:+.3f}  ({'EDGE' if d > 0.03 else 'no edge'})")
            print("  per epoca (reale E[R], n):")
            for era in ("2013-2018", "2019-2022", "2023-2026"):
                er = era_real[rr].get(era, [])
                if er:
                    print(f"      {era}: E[R]={st.mean(er):+.2f}  win={100*sum(1 for r in er if r>0)/len(er):.0f}%  n={len(er)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
