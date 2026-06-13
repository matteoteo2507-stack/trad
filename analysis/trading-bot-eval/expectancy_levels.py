"""Validazione EXPECTANCY-IN-R dei livelli (XAU spot) — drift-controllata.

Domanda: i livelli che il sistema gia' produce (PDH/PDL + swing S/R) danno
expectancy POSITIVA tradando un fade al primo touch? E battono livelli CASUALI
nello stesso contesto (controllo anti-drift, stile Osler/validate_levels)?

Modello di trade (semplice, onesto, baseline):
  - al primo touch del livello nella sessione: fade (long ai supporti, short alle
    resistenze), entry = prezzo del livello;
  - SL = SL_BUF oltre il livello;  TP = RR * SL_BUF (sweep su RR = 1.5/2/3);
  - esito risolto su barre M5; se TP e SL nella stessa barra -> conservativo = SL;
  - se nessuno entro MAX_HOLD_H -> mark-to-close (R parziale).
Controllo: per ogni livello reale, un livello CASUALE a distanza arbitraria
(+/- RAND_$) dallo stesso prezzo, stesso lato e stessa simulazione.

Dati: analysis/data/bars_{D1,H1,M5}.csv (XAU spot, MT5). Periodo ~ primavera 2026.
Uso: python analysis/trading-bot-eval/expectancy_levels.py
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

D1P = "analysis/data/bars_D1.csv"
H1P = "analysis/data/bars_H1.csv"
M5P = "analysis/data/bars_M5.csv"

SESSION = (6, 21)          # UTC: dalla London preview a fine NY
TOUCH_TOL = 0.8            # $ entro cui conta come "touch"
SL_BUF = 3.0              # $ oltre il livello per lo SL (gold)
RRS = [1.5, 2.0, 3.0]
MAX_HOLD_H = 12
RAND_OFFSET = 40.0        # $ per il livello di controllo casuale
H1_WINDOW = 60            # barre H1 chiuse per gli swing S/R


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


def resolve(m5, i0, entry, side, sl, tp):
    """Ritorna R: +RR se TP prima, -1 se SL prima, altrimenti mark-to-close."""
    end_t = m5[i0]["t"] + timedelta(hours=MAX_HOLD_H)
    last = m5[i0]["close"]
    rr = abs(tp - entry) / SL_BUF
    for j in range(i0, len(m5)):
        b = m5[j]
        if b["t"] > end_t:
            break
        last = b["close"]
        if side == "S":  # long
            if b["low"] <= sl:
                return -1.0
            if b["high"] >= tp:
                return rr
        else:            # short
            if b["high"] >= sl:
                return -1.0
            if b["low"] <= tp:
                return rr
    return (last - entry) / SL_BUF if side == "S" else (entry - last) / SL_BUF


def first_touch(m5, start_i, end_i, price):
    for j in range(start_i, end_i):
        if m5[j]["low"] <= price + TOUCH_TOL and m5[j]["high"] >= price - TOUCH_TOL:
            return j
    return None


def sim_level(m5, s_i, e_i, price, side, rr, rng=None, randomize=False):
    p = price + rng.uniform(-RAND_OFFSET, RAND_OFFSET) if randomize else price
    j = first_touch(m5, s_i, e_i, p)
    if j is None:
        return None
    entry = p
    if side == "S":
        sl, tp = p - SL_BUF, p + rr * SL_BUF
    else:
        sl, tp = p + SL_BUF, p - rr * SL_BUF
    return resolve(m5, j, entry, side, sl, tp)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    d1, h1, m5 = load(D1P), load(H1P), load(M5P)
    if not m5:
        print("Nessuna barra M5."); return 1
    d1_by_date = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by_date)
    h1_t = [b["t"] for b in h1]
    m5_t = [b["t"] for b in m5]
    rng = random.Random(7)

    days = sorted({b["t"].date() for b in m5})
    # risultati: {rr: {type: [R...]}} reale e controllo
    real = {rr: {} for rr in RRS}
    ctrl = {rr: {} for rr in RRS}

    def add(d, rr, typ, r):
        d[rr].setdefault(typ, []).append(r)

    for day in days:
        di = bisect.bisect_left(d1_dates, day)
        if di == 0:
            continue
        prev = d1_by_date[d1_dates[di - 1]]
        sess_start = datetime(day.year, day.month, day.day, SESSION[0], tzinfo=timezone.utc)
        sess_end = datetime(day.year, day.month, day.day, SESSION[1], tzinfo=timezone.utc)
        s_i = bisect.bisect_left(m5_t, sess_start)
        e_i = bisect.bisect_left(m5_t, sess_end)
        if e_i - s_i < 12:
            continue

        # livelli del giorno
        levels = [("PDH", prev["high"], "R"), ("PDL", prev["low"], "S")]
        ci = bisect.bisect_right(h1_t, sess_start - timedelta(hours=1))
        hwin = h1[max(0, ci - H1_WINDOW):ci]
        if len(hwin) >= 5:
            kl = le.get_key_levels(hwin)
            for p in kl["supports"][:3]:
                levels.append(("Swing_S", p, "S"))
            for p in kl["resistances"][:3]:
                levels.append(("Swing_R", p, "R"))

        for typ, price, side in levels:
            for rr in RRS:
                r = sim_level(m5, s_i, e_i, price, side, rr)
                if r is not None:
                    add(real, rr, typ, r)
                rc = sim_level(m5, s_i, e_i, price, side, rr, rng=rng, randomize=True)
                if rc is not None:
                    add(ctrl, rr, typ, rc)

    def explin(label, rs):
        n = len(rs)
        if n == 0:
            return f"    {label:12} n=  0"
        ev = st.mean(rs)
        win = 100 * sum(1 for r in rs if r > 0) / n
        return f"    {label:12} n={n:4}  E[R]={ev:+5.2f}  win={win:4.0f}%"

    print("=" * 66)
    print("EXPECTANCY-IN-R DEI LIVELLI XAU SPOT (fade al primo touch)")
    print(f"giorni={len(days)}  SL_BUF=${SL_BUF}  hold={MAX_HOLD_H}h  TOL=${TOUCH_TOL}")
    print("=" * 66)
    for rr in RRS:
        print(f"\n--- RR 1:{rr}  (TP=${rr*SL_BUF:.0f}, SL=${SL_BUF:.0f}) ---")
        all_real = [r for v in real[rr].values() for r in v]
        all_ctrl = [r for v in ctrl[rr].values() for r in v]
        print("  REALE:")
        print(explin("TOTALE", all_real))
        for typ in ("PDH", "PDL", "Swing_S", "Swing_R"):
            print(explin(typ, real[rr].get(typ, [])))
        print("  CONTROLLO random:")
        print(explin("TOTALE", all_ctrl))
        if all_real and all_ctrl:
            delta = st.mean(all_real) - st.mean(all_ctrl)
            verdict = "livelli > random" if delta > 0.03 else "NON distinguibili dal random"
            print(f"  -> E[R] reale - random = {delta:+.2f}  =>  {verdict}")
    print("\nNota: campione corto (~primavera 2026, un regime). Numeri indicativi,")
    print("il controllo random isola l'edge dal drift. Estendere con piu' storia spot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
