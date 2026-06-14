"""GATE DI REGIME: l'edge conf=2 dipende dal regime trend/range? (XAU/BTC spot).

Ipotesi a priori (mechanistica, non data-mined): il FADE ai livelli rende di piu' in
RANGE (ADX basso) e peggio nei TREND forti (ADX alto, i livelli si rompono).
Test: tag di ogni trade conf=2 con l'ADX(14) del daily chiuso a inizio sessione,
bucket per TERCILE di ADX (soglie dal TRAIN), E[R] + CI bootstrap, su TRAIN e TEST.

Uso: python analysis/trading-bot-eval/regime_gate.py [XAU|BTC]
"""
from __future__ import annotations

import bisect
import csv
import os
import random
import statistics as st
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

ASSET = sys.argv[1] if len(sys.argv) > 1 else "XAU"
SESSION = (6, 21)
K_SL, K_TOL, K_RAND = 0.5, 0.10, 6.0
RR = 1.5
MAX_HOLD, H1_WINDOW, ATR_N = 24, 120, 14
START_YEAR, CLUSTER_TOL_PCT, ADX_N = 2013, 0.25, 14


def _p(tf):
    base = "analysis/trading-bot-eval/data"
    for n in (f"{ASSET}_spot_{tf}.csv", f"{ASSET}_{tf}.csv"):
        if os.path.exists(f"{base}/{n}"):
            return f"{base}/{n}"
    return f"{base}/{ASSET}_spot_{tf}.csv"


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t = datetime.fromisoformat(r["time"][:19])
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


def adx_series(d1, n=ADX_N):
    L = len(d1)
    adx = [None] * L
    if L < 2 * n + 2:
        return adx
    tr, pdm, ndm = [0.0] * L, [0.0] * L, [0.0] * L
    for i in range(1, L):
        h, l, pc = d1[i]["high"], d1[i]["low"], d1[i - 1]["close"]
        up, dn = h - d1[i - 1]["high"], d1[i - 1]["low"] - l
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
        pdm[i] = up if (up > dn and up > 0) else 0.0
        ndm[i] = dn if (dn > up and dn > 0) else 0.0

    def wilder(x):
        s = [None] * L
        s[n] = sum(x[1:n + 1])
        for i in range(n + 1, L):
            s[i] = s[i - 1] - s[i - 1] / n + x[i]
        return s
    str_, spdm, sndm = wilder(tr), wilder(pdm), wilder(ndm)
    dx = [None] * L
    for i in range(n, L):
        if str_[i] and str_[i] > 0:
            pdi, ndi = 100 * spdm[i] / str_[i], 100 * sndm[i] / str_[i]
            den = pdi + ndi
            dx[i] = 100 * abs(pdi - ndi) / den if den > 0 else 0.0
    vals = [dx[i] for i in range(n + 1, 2 * n + 1)]
    adx[2 * n] = sum(vals) / n
    for i in range(2 * n + 1, L):
        if dx[i] is not None:
            adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return adx


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


def resolve(h1, i0, entry, side, sl, tp, sl_dist):
    last = h1[i0]["close"]
    for j in range(i0, min(i0 + MAX_HOLD, len(h1))):
        b = h1[j]; last = b["close"]
        if side == "S":
            if b["low"] <= sl:
                return -1.0
            if b["high"] >= tp:
                return RR
        else:
            if b["high"] >= sl:
                return -1.0
            if b["low"] <= tp:
                return RR
    return (last - entry) / sl_dist if side == "S" else (entry - last) / sl_dist


def sim(h1, s_i, e_i, price, side, atr):
    tol = K_TOL * atr
    j = None
    for k in range(s_i, e_i):
        if h1[k]["low"] <= price + tol and h1[k]["high"] >= price - tol:
            j = k; break
    if j is None:
        return None
    sld = K_SL * atr
    if side == "S":
        return resolve(h1, j, price, "S", price - sld, price + RR * sld, sld)
    return resolve(h1, j, price, "R", price + sld, price - RR * sld, sld)


def boot_ci(rs, B=1500, seed=1):
    if not rs:
        return (0.0, 0.0)
    rg, n, m = random.Random(seed), len(rs), []
    for _ in range(B):
        m.append(sum(rs[rg.randrange(n)] for _ in range(n)) / n)
    m.sort()
    return (m[int(0.025 * B)], m[int(0.975 * B)])


def line(label, rs):
    if not rs:
        print(f"    {label:22} n=   0"); return
    lo, hi = boot_ci(rs)
    print(f"    {label:22} n={len(rs):4}  E[R]={st.mean(rs):+5.2f} [CI {lo:+.2f},{hi:+.2f}]  "
          f"win={100*sum(1 for r in rs if r>0)/len(rs):3.0f}%")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1, h1 = load(_p("D1")), load(_p("H1"))
    atr = atr_series(h1)
    adx = adx_series(d1)
    d1_dates = [b["t"].date() for b in d1]
    adx_by_date = {d1_dates[i]: adx[i] for i in range(len(d1)) if adx[i] is not None}
    h1_t = [b["t"] for b in h1]

    recs = []  # (ts, R, adx)
    days = sorted({b["t"].date() for b in h1 if b["t"].year >= START_YEAR})
    for day in days:
        di = bisect.bisect_left(d1_dates, day)
        if di == 0:
            continue
        prev = d1[di - 1]
        a_adx = adx_by_date.get(d1_dates[di - 1])
        if a_adx is None:
            continue
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
        for z in le.cluster_confluence(build_entries(prev, hwin), tol_pct=CLUSTER_TOL_PCT):
            if z["confluence"] != 2 or z["side"] not in ("SUPPORT", "RESISTANCE"):
                continue
            r = sim(h1, s_i, e_i, z["price"], "S" if z["side"] == "SUPPORT" else "R", a)
            if r is not None:
                recs.append((ss, r, a_adx))
    recs.sort()
    if len(recs) < 60:
        print(f"{ASSET}: troppi pochi trade ({len(recs)})"); return 1

    split = recs[int(len(recs) * 0.70)][0]
    tr = [x for x in recs if x[0] < split]
    te = [x for x in recs if x[0] >= split]
    adx_tr = sorted(x[2] for x in tr)
    q1, q2 = adx_tr[len(adx_tr) // 3], adx_tr[2 * len(adx_tr) // 3]

    def bucket(a):
        return "ADX basso (range)" if a <= q1 else "ADX medio" if a <= q2 else "ADX alto (trend)"

    print("=" * 64)
    print(f"GATE DI REGIME {ASSET} — conf=2 fade per ADX(14) daily  (RR 1:{RR})")
    print(f"trade={len(recs)}  soglie ADX (da TRAIN): basso<= {q1:.1f} < medio <= {q2:.1f} < alto")
    print("=" * 64)
    for name, data in (("TRAIN", tr), ("TEST (holdout)", te)):
        print(f"\n  {name}:")
        for b in ("ADX basso (range)", "ADX medio", "ADX alto (trend)"):
            line(b, [r for _, r, a in data if bucket(a) == b])
        line("TUTTI (no gate)", [r for _, r, a in data])
    print("\n  >>> Ipotesi: ADX basso (range) > ADX alto (trend). Se confermata su TEST,")
    print("      il gate = opera lo strumento solo quando ADX <= soglia (range/transizione).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
