"""Selezione per CONFLUENZA: l'edge del livello si concentra dove piu' nature
coincidono? (XAU spot, 13 anni).

Per ogni giorno aggrega le nature di livello (PDH/PDL + swing S/R + order block +
FVG), le clusterizza in ZONE (levels_engine.cluster_confluence) e fada al primo
touch (long supporti / short resistenze, SL=0.5*ATR). Bucketizza per grado di
confluenza (1 / 2 / >=3 nature) e confronta con livello casuale (drift control).

Ipotesi: E[R] cresce col grado di confluenza. Se conf>=2 porta +0.10R verso
+0.30/0.40R mantenendo l'edge vs random -> e' l'amplificazione tradabile.

Uso: python analysis/trading-bot-eval/expectancy_confluence.py
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

import os  # noqa: E402

ASSET = sys.argv[1] if len(sys.argv) > 1 else "XAU"


def _datapath(tf):
    base = "analysis/trading-bot-eval/data"
    for name in (f"{ASSET}_spot_{tf}.csv", f"{ASSET}_{tf}.csv"):
        if os.path.exists(f"{base}/{name}"):
            return f"{base}/{name}"
    return f"{base}/{ASSET}_spot_{tf}.csv"


D1P = _datapath("D1")
H1P = _datapath("H1")
COST_PRICE = float(os.environ.get("COST_PRICE", "0"))   # spread+slippage in unita' di prezzo
SESSION = (6, 21)
K_SL = 0.5
K_TOL = 0.10
K_RAND = 6.0
RRS = [1.5, 2.0, 3.0]
MAX_HOLD = 24
H1_WINDOW = 120
ATR_N = 14
START_YEAR = 2013
CLUSTER_TOL_PCT = 0.25


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
    atr, trs = [None] * len(h1), []
    for i in range(len(h1)):
        tr = (h1[i]["high"] - h1[i]["low"]) if i == 0 else max(
            h1[i]["high"] - h1[i]["low"], abs(h1[i]["high"] - h1[i - 1]["close"]),
            abs(h1[i]["low"] - h1[i - 1]["close"]))
        trs.append(tr)
        if i >= n:
            atr[i] = sum(trs[i - n + 1:i + 1]) / n
    return atr


def resolve(h1, i0, entry, side, sl, tp, sl_dist):
    last, rr = h1[i0]["close"], abs(tp - entry) / sl_dist
    for j in range(i0, min(i0 + MAX_HOLD, len(h1))):
        b = h1[j]; last = b["close"]
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


def first_touch(h1, s_i, e_i, price, tol):
    for j in range(s_i, e_i):
        if h1[j]["low"] <= price + tol and h1[j]["high"] >= price - tol:
            return j
    return None


def sim(h1, s_i, e_i, price, side, rr, atr, rng=None, randomize=False):
    p = price + rng.uniform(-K_RAND * atr, K_RAND * atr) if randomize else price
    j = first_touch(h1, s_i, e_i, p, K_TOL * atr)
    if j is None:
        return None
    sl_dist = K_SL * atr
    if side == "S":
        sl, tp = p - sl_dist, p + rr * sl_dist
    else:
        sl, tp = p + sl_dist, p - rr * sl_dist
    r = resolve(h1, j, p, side, sl, tp, sl_dist)
    return r - COST_PRICE / sl_dist   # netto costi (spread+slippage in prezzo)


def build_entries(prev, hwin):
    e = [{"price": prev["high"], "type": "RESISTANCE", "label": "PDH"},
         {"price": prev["low"], "type": "SUPPORT", "label": "PDL"}]
    kl = le.get_key_levels(hwin)
    for p in kl["supports"]:
        e.append({"price": p, "type": "SUPPORT", "label": "Swing_S"})
    for p in kl["resistances"]:
        e.append({"price": p, "type": "RESISTANCE", "label": "Swing_R"})
    for ob in le.detect_order_blocks(hwin):
        e.append({"price": (ob["high"] + ob["low"]) / 2, "label": "OB",
                  "type": "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE"})
    for f in le.detect_fvg(hwin):
        e.append({"price": (f["high"] + f["low"]) / 2, "label": "FVG",
                  "type": "SUPPORT" if f["type"] == "BULLISH_FVG" else "RESISTANCE"})
    return e


def explin(label, rs):
    n = len(rs)
    if n == 0:
        return f"    {label:12} n=   0"
    return f"    {label:12} n={n:5}  E[R]={st.mean(rs):+5.2f}  win={100*sum(1 for r in rs if r>0)/n:4.0f}%"


def boot_ci(rs, B=1500, seed=1):
    if not rs:
        return (0.0, 0.0)
    rg, n, means = random.Random(seed), len(rs), []
    for _ in range(B):
        means.append(sum(rs[rg.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return (means[int(0.025 * B)], means[int(0.975 * B)])


def boot_diff_ci(a, b, B=1500, seed=2):
    if not a or not b:
        return (0.0, 0.0)
    rg, na, nb, d = random.Random(seed), len(a), len(b), []
    for _ in range(B):
        ma = sum(a[rg.randrange(na)] for _ in range(na)) / na
        mb = sum(b[rg.randrange(nb)] for _ in range(nb)) / nb
        d.append(ma - mb)
    d.sort()
    return (d[int(0.025 * B)], d[int(0.975 * B)])


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (100 * (c - h) / den, 100 * (c + h) / den)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1, h1 = load(D1P), load(H1P)
    if not h1:
        print("Manca XAU_spot_H1.csv."); return 1
    atr = atr_series(h1)
    d1_by_date = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by_date)
    h1_t = [b["t"] for b in h1]
    rng = random.Random(7)
    # bucket per confluenza: 1, 2, "3+"
    real = {rr: {"1": [], "2": [], "3+": []} for rr in RRS}
    ctrl = {rr: [] for rr in RRS}
    era_c2 = {rr: {} for rr in RRS}   # conf>=2 per epoca

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
        ci = bisect.bisect_right(h1_t, ss - timedelta(hours=1))
        hwin = h1[max(0, ci - H1_WINDOW):ci]
        if len(hwin) < 10:
            continue
        zones = le.cluster_confluence(build_entries(prev, hwin), tol_pct=CLUSTER_TOL_PCT)
        era = era_of(day.year)
        for z in zones:
            if z["side"] not in ("SUPPORT", "RESISTANCE"):
                continue
            side = "S" if z["side"] == "SUPPORT" else "R"
            bucket = "1" if z["confluence"] == 1 else "2" if z["confluence"] == 2 else "3+"
            for rr in RRS:
                r = sim(h1, s_i, e_i, z["price"], side, rr, a)
                if r is not None:
                    real[rr][bucket].append(r)
                    if z["confluence"] == 2:
                        era_c2[rr].setdefault(era, []).append(r)
                rc = sim(h1, s_i, e_i, z["price"], side, rr, a, rng=rng, randomize=True)
                if rc is not None:
                    ctrl[rr].append(rc)

    print("=" * 70)
    print(f"SELEZIONE PER CONFLUENZA — {ASSET}  ({H1P})")
    print(f"  giorni valutati={len(days)}  (fade zone clusterizzate, SL=ATR)")
    print("=" * 70)
    for rr in RRS:
        print(f"\n--- RR 1:{rr} ---")
        for b in ("1", "2", "3+"):
            print(explin(f"confluenza {b}", real[rr][b]))
        print(explin("random", ctrl[rr]))
        two, rnd = real[rr]["2"], ctrl[rr]
        if two and rnd:
            lo, hi = boot_ci(two)
            k = sum(1 for r in two if r > 0)
            wlo, whi = wilson(k, len(two))
            rlo, rhi = boot_ci(rnd)
            dlo, dhi = boot_diff_ci(two, rnd)
            sig = "SIGNIFICATIVO (CI esclude 0)" if dlo > 0 else "non significativo (CI include 0)"
            print(f"  >> CONF=2 ISOLATO: E[R]={st.mean(two):+.2f} [CI {lo:+.2f},{hi:+.2f}]  "
                  f"win={100*k/len(two):.0f}% [CI {wlo:.0f},{whi:.0f}]  n={len(two)}")
            print(f"     random          : E[R]={st.mean(rnd):+.2f} [CI {rlo:+.2f},{rhi:+.2f}]")
            print(f"     conf2 - random  = {st.mean(two)-st.mean(rnd):+.2f} [CI {dlo:+.2f},{dhi:+.2f}]  -> {sig}")
            eras = [e for e in ("2013-2018", "2019-2022", "2023-2026") if era_c2[rr].get(e)]
            if len(eras) > 1:
                print("     conf=2 per epoca:", "  ".join(
                    f"{e}:{st.mean(era_c2[rr][e]):+.2f}(n={len(era_c2[rr][e])})" for e in eras))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
