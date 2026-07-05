"""CHECK ECONOMICO: il fade conf=2 e' morto forward. Testiamo la direzione OPPOSTA.

Sulle STESSE zone conf=2 e stessa geometria (SL=0.5*ATR, RR1.5), confronta su 13y/6y:
  - FADE      (long supporto / short resistenza)  -> l'edge storico, ora refutato forward
  - REVERSE   (short supporto / long resistenza)  -> "il bias e' l'opposto" dell'utente
  - RANDOM    (fade di una zona casuale +-6*ATR)   -> drift control
Se REVERSE batte RANDOM in modo netto -> quei livelli predicono CONTINUAZIONE (edge inverso).
Se ne' fade ne' reverse battono random -> le zone sono rumore, libro chiuso.

Tolleranze ATR-relative (mercati sporchi: mai pip esatti). Uso: python analysis/trading-bot-eval/breakout_check.py
"""
from __future__ import annotations
import bisect, csv, os, random, statistics as st, sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

SESSION = (6, 21)
K_SL, K_TOL, K_RAND, RR = 0.5, 0.10, 6.0, 1.5
MAX_HOLD, H1_WINDOW, ATR_N = 24, 120, 14
START_YEAR, CLUSTER_TOL_PCT = 2013, 0.25
ASSETS = [("XAU", 0.10), ("BTC", 13.0), ("EUR", 0.00011)]


def _p(asset, tf):
    base = "analysis/trading-bot-eval/data"
    for n in (f"{asset}_spot_{tf}.csv", f"{asset}_{tf}.csv"):
        if os.path.exists(f"{base}/{n}"):
            return f"{base}/{n}"
    return f"{base}/{asset}_spot_{tf}.csv"


def load(path):
    out = []
    if not os.path.exists(path):
        return out
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


def resolve(h1, i0, entry, tside, sl, tp, sl_dist):
    last = h1[i0]["close"]
    for j in range(i0, min(i0 + MAX_HOLD, len(h1))):
        b = h1[j]; last = b["close"]
        if tside == "L":
            if b["low"] <= sl:
                return -1.0
            if b["high"] >= tp:
                return RR
        else:
            if b["high"] >= sl:
                return -1.0
            if b["low"] <= tp:
                return RR
    return (last - entry) / sl_dist if tside == "L" else (entry - last) / sl_dist


def first_touch(h1, s_i, e_i, price, tol):
    for j in range(s_i, e_i):
        if h1[j]["low"] <= price + tol and h1[j]["high"] >= price - tol:
            return j
    return None


def sim(h1, s_i, e_i, z, tside, atr, cost, rng=None):
    p = z + rng.uniform(-K_RAND * atr, K_RAND * atr) if rng else z
    j = first_touch(h1, s_i, e_i, p, K_TOL * atr)
    if j is None:
        return None
    sld = K_SL * atr
    sl, tp = (p - sld, p + RR * sld) if tside == "L" else (p + sld, p - RR * sld)
    return resolve(h1, j, p, tside, sl, tp, sld) - cost / sld


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
        return f"    {label:16} n=   0"
    lo, hi = boot_ci(rs)
    return (f"    {label:16} n={len(rs):5}  E[R]={st.mean(rs):+5.2f} [CI {lo:+.2f},{hi:+.2f}]  "
            f"win={100*sum(1 for r in rs if r>0)/len(rs):3.0f}%")


def run_asset(asset, cost):
    d1, h1 = load(_p(asset, "D1")), load(_p(asset, "H1"))
    if not h1:
        print(f"\n### {asset}: dati mancanti"); return
    atr = atr_series(h1)
    d1_by = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by)
    h1_t = [b["t"] for b in h1]
    rng = random.Random(7)
    fade, rev, rnd = [], [], []
    days = sorted({b["t"].date() for b in h1 if b["t"].year >= START_YEAR})
    for day in days:
        di = bisect.bisect_left(d1_dates, day)
        if di == 0:
            continue
        prev = d1_by[d1_dates[di - 1]]
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
            fside = "L" if z["side"] == "SUPPORT" else "S"
            rside = "S" if fside == "L" else "L"
            rf = sim(h1, s_i, e_i, z["price"], fside, a, cost)
            rr_ = sim(h1, s_i, e_i, z["price"], rside, a, cost)
            rc = sim(h1, s_i, e_i, z["price"], fside, a, cost, rng=rng)
            if rf is not None:
                fade.append(rf)
            if rr_ is not None:
                rev.append(rr_)
            if rc is not None:
                rnd.append(rc)
    print(f"\n### {asset}  (costo {cost}, {len(days)} giorni)")
    print(line("FADE", fade))
    print(line("REVERSE", rev))
    print(line("RANDOM", rnd))
    if fade and rnd:
        d = st.mean(rev) - st.mean(rnd)
        print(f"    -> REVERSE - RANDOM = {d:+.2f}R  ({'batte il random' if d>0 else 'NON batte il random'})")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    print("=" * 64)
    print("CHECK BREAKOUT/REVERSE — conf=2 zone-fade vs reverse vs random")
    print("=" * 64)
    for a, c in ASSETS:
        run_asset(a, c)


if __name__ == "__main__":
    main()
