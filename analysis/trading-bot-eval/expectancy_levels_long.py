"""Expectancy-in-R dei livelli XAU spot su 13 ANNI (2012-2026), multi-regime.

Come expectancy_levels.py ma:
  - dati spot lunghi da MT5 (XAU_spot_D1.csv 2004+, XAU_spot_H1.csv 2012+);
  - SL/TP dimensionati ad ATR(H1,14) -> era-invariante (oro $1200 vs $5000);
  - path risolto su H1 (la risoluzione coarse e' simmetrica reale/random -> si
    annulla nel CONFRONTO, che e' la metrica che conta);
  - split per EPOCA per vedere se l'eventuale edge regge tra regimi.

Modello: fade al primo touch (long supporti / short resistenze), SL = K_SL*ATR
oltre il livello, TP = RR*SL. Controllo: livello casuale a distanza ~ATR, stesso lato.

Uso: python analysis/trading-bot-eval/expectancy_levels_long.py
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

SESSION = (6, 21)         # UTC (server-time del broker, offset costante: ininfluente sul confronto)
K_SL = 0.5                # SL = 0.5 * ATR(H1,14) oltre il livello
K_TOL = 0.10             # touch tolerance = 0.10 * ATR
K_RAND = 6.0             # livello casuale entro +/- 6*ATR
RRS = [1.5, 2.0, 3.0]
MAX_HOLD = 24            # barre H1 (~1 giorno)
H1_WINDOW = 60
ATR_N = 14
START_YEAR = 2013        # primo anno valutato (serve storia pregressa)


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
        if i == 0:
            tr = h1[i]["high"] - h1[i]["low"]
        else:
            pc = h1[i - 1]["close"]
            tr = max(h1[i]["high"] - h1[i]["low"], abs(h1[i]["high"] - pc), abs(h1[i]["low"] - pc))
        trs.append(tr)
        if i >= n:
            atr[i] = sum(trs[i - n + 1:i + 1]) / n
    return atr


def resolve(h1, i0, entry, side, sl, tp, sl_dist):
    last = h1[i0]["close"]
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


def first_touch(h1, s_i, e_i, price, tol):
    for j in range(s_i, e_i):
        if h1[j]["low"] <= price + tol and h1[j]["high"] >= price - tol:
            return j
    return None


def sim(h1, s_i, e_i, price, side, rr, atr, rng=None, randomize=False):
    p = price + rng.uniform(-K_RAND * atr, K_RAND * atr) if randomize else price
    tol = K_TOL * atr
    j = first_touch(h1, s_i, e_i, p, tol)
    if j is None:
        return None
    sl_dist = K_SL * atr
    if side == "S":
        sl, tp = p - sl_dist, p + rr * sl_dist
    else:
        sl, tp = p + sl_dist, p - rr * sl_dist
    return resolve(h1, j, p, side, sl, tp, sl_dist)


def explin(label, rs):
    n = len(rs)
    if n == 0:
        return f"    {label:12} n=   0"
    ev, win = st.mean(rs), 100 * sum(1 for r in rs if r > 0) / n
    return f"    {label:12} n={n:5}  E[R]={ev:+5.2f}  win={win:4.0f}%"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1, h1 = load(D1P), load(H1P)
    if not h1:
        print("Nessuna barra H1 spot. Esegui prima export_mt5_spot.py."); return 1
    atr = atr_series(h1)
    d1_by_date = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by_date)
    h1_t = [b["t"] for b in h1]

    real = {rr: {} for rr in RRS}
    ctrl = {rr: {} for rr in RRS}
    era_real = {rr: {} for rr in RRS}   # delta per epoca
    era_ctrl = {rr: {} for rr in RRS}
    rng = random.Random(7)

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
                r = sim(h1, s_i, e_i, price, side, rr, a)
                if r is not None:
                    real[rr].setdefault(typ, []).append(r)
                    era_real[rr].setdefault(era, []).append(r)
                rc = sim(h1, s_i, e_i, price, side, rr, a, rng=rng, randomize=True)
                if rc is not None:
                    ctrl[rr].setdefault(typ, []).append(rc)
                    era_ctrl[rr].setdefault(era, []).append(rc)

    print("=" * 68)
    print("EXPECTANCY-IN-R LIVELLI XAU SPOT — 13 ANNI (fade al primo touch, ATR-sized)")
    print(f"giorni valutati={len(days)}  SL={K_SL}*ATR  hold={MAX_HOLD}h")
    print("=" * 68)
    for rr in RRS:
        all_real = [r for v in real[rr].values() for r in v]
        all_ctrl = [r for v in ctrl[rr].values() for r in v]
        print(f"\n--- RR 1:{rr} ---")
        print("  REALE:", )
        print(explin("TOTALE", all_real))
        for typ in ("PDH", "PDL", "Swing_S", "Swing_R"):
            print(explin(typ, real[rr].get(typ, [])))
        print("  CONTROLLO random:")
        print(explin("TOTALE", all_ctrl))
        if all_real and all_ctrl:
            d = st.mean(all_real) - st.mean(all_ctrl)
            print(f"  -> E[R] reale - random = {d:+.3f}  "
                  f"({'EDGE' if d > 0.03 else 'no edge vs random'})")
            print("  per epoca (reale - random):")
            for era in ("2013-2018", "2019-2022", "2023-2026"):
                er, ec = era_real[rr].get(era, []), era_ctrl[rr].get(era, [])
                if er and ec:
                    print(f"      {era}:  {st.mean(er) - st.mean(ec):+.3f}  "
                          f"(reale E[R]={st.mean(er):+.2f}, n={len(er)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
