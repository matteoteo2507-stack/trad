"""Validazione dei LIVELLI del bot AlphaAnalist (XAUUSD).

Due test indipendenti, look-ahead-safe (si guarda solo cosa succede DOPO che il
livello è stato pubblicato):

A) ACCURATEZZA MECCANICA — i livelli "deterministici" (PDH/PDL/PDC = max/min/close
   di ieri) riportati dal bot coincidono col vero valore calcolato dalle barre?
   Testa se la pipeline-dati del bot è corretta.

B) POTERE REATTIVO — quando il prezzo raggiunge un livello del bot, reagisce nel
   verso atteso (rimbalzo ai supporti / rigetto alle resistenze) PIÙ di un livello
   di prezzo casuale nello stesso contesto? Controllo anti-caso (come per il
   mentore: senza baseline un livello "vicino al prezzo" sembra sempre buono).

Dati: estrae i livelli XAUUSD dai messaggi (signals.jsonl ha i livelli, ma qui
ri-parso dal raw per classificare bene il TIPO) e usa analysis/data/bars_M15.csv
+ bars_D1.csv (già esportate).

Uso: python -m analysis.veltrix.validate_levels
"""

from __future__ import annotations

import glob
import json
import random
import re
import statistics as st
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

TOL = 1.0           # tolleranza "touch" in $ (XAU)
K = 16              # barre M15 di reazione dopo il primo touch (~4h)
TOUCH_WINDOW_D = 3  # giorni entro cui il livello deve essere toccato per contare


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _classify(line: str) -> str | None:
    t = line.lower()
    if "pdh" in t or "max ieri" in t:
        return "PDH"
    if "pdl" in t or "min ieri" in t:
        return "PDL"
    if "pdc" in t or "close ieri" in t:
        return "PDC"
    if "ob" in t and "bull" in t:
        return "OB_bull"
    if "ob" in t and "bear" in t:
        return "OB_bear"
    if "fvg" in t and "bull" in t:
        return "FVG_bull"
    if "fvg" in t and "bear" in t:
        return "FVG_bear"
    if "swing" in t:
        return "Swing"
    if any(k in t for k in ("resistenz", "supporto", "r:", "s:")):
        return "SR_generic"
    return None


def extract_levels(asset="XAUUSD"):
    """Ritorna lista di dict: ts_pub, price, side (R/S/N), type."""
    src = sorted(glob.glob("alphanalist_chat_*.jsonl"))[0]
    out = []
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        if r.get("sender") != "AlphaAnalist":
            continue
        txt = r.get("text") or ""
        if asset not in txt.upper():
            continue
        ts = _ts(r["date"])
        for ln in txt.split("\n"):
            typ = _classify(ln)
            if not typ:
                continue
            m = re.search(r"([🟢🔴🟥⚪🟦⬜])", ln)
            mp = re.search(r"(\d[\d,]*(?:\.\d+)?)", ln)
            if not mp:
                continue
            try:
                price = float(mp.group(1).replace(",", ""))
            except ValueError:
                continue
            if not (1000 < price < 9000):   # sanity XAU
                continue
            emo = m.group(1) if m else ""
            side = "R" if emo in "🔴🟥" else ("S" if emo == "🟢" else "N")
            out.append({"ts": ts, "price": price, "side": side, "type": typ})
    return out


def test_mechanical(levels, d1):
    """A) PDH/PDL/PDC riportati vs veri max/min/close del giorno prima."""
    print("===== A) ACCURATEZZA MECCANICA (PDH/PDL/PDC vs barre) =====")
    d1 = d1.copy()
    d1["d"] = d1.index.date
    by_day = {row.d: row for row in d1.itertuples()}
    days = sorted(by_day)
    prev = {days[i]: days[i - 1] for i in range(1, len(days))}
    for typ, col in (("PDH", "high"), ("PDL", "low"), ("PDC", "close")):
        errs = []
        for lv in levels:
            if lv["type"] != typ:
                continue
            d = lv["ts"].date()
            pd_ = prev.get(d)
            if pd_ is None:
                continue
            true_v = getattr(by_day[pd_], col)
            errs.append(abs(lv["price"] - true_v))
        if errs:
            within = 100 * sum(e <= 1.0 for e in errs) / len(errs)
            print(f"  {typ}: n={len(errs):4}  err mediano=${st.median(errs):6.2f}  "
                  f"entro $1={within:4.0f}%")
        else:
            print(f"  {typ}: n=0")


def _reaction(bars, idx, price, side):
    """Reazione netta ($) nelle K barre dopo il touch: + = ha tenuto/respinto."""
    win = bars.iloc[idx + 1: idx + 1 + K]
    if len(win) < 3:
        return None
    up = float(win["high"].max()) - price       # escursione sopra
    dn = price - float(win["low"].min())          # escursione sotto
    if side == "S":
        return up - dn                            # support: bene se rimbalza su
    if side == "R":
        return dn - up                            # resistance: bene se respinge giù
    return None


def test_reactive(levels, m15):
    """B) reazione al primo touch vs livelli casuali (controllo)."""
    print("\n===== B) POTERE REATTIVO (reazione al primo touch vs random) =====")
    times = m15.index.to_pydatetime()
    highs = m15["high"].to_numpy(); lows = m15["low"].to_numpy()

    def first_touch(price, ts_pub):
        # primo indice con barra che tocca [price-TOL, price+TOL] dopo ts_pub
        start = ts_pub
        end = ts_pub + timedelta(days=TOUCH_WINDOW_D)
        for i, t in enumerate(times):
            if t <= start:
                continue
            if t > end:
                return None
            if lows[i] <= price + TOL and highs[i] >= price - TOL:
                return i
        return None

    real, ctrl = [], []
    rng = random.Random(42)
    daily_lo, daily_hi = float(m15["low"].min()), float(m15["high"].max())
    for lv in levels:
        if lv["side"] not in ("R", "S"):
            continue
        i = first_touch(lv["price"], lv["ts"])
        if i is None:
            continue
        rxn = _reaction(m15, i, lv["price"], lv["side"])
        if rxn is not None:
            real.append((lv["type"], rxn))
        # controllo: prezzo casuale +/-$40 dal livello, stesso side, stesso metodo
        cp = lv["price"] + rng.uniform(-40, 40)
        ci = first_touch(cp, lv["ts"])
        if ci is not None:
            crx = _reaction(m15, ci, cp, lv["side"])
            if crx is not None:
                ctrl.append(crx)

    def summ(vals):
        if not vals:
            return "n=0"
        return (f"n={len(vals):4}  reazione mediana=${st.median(vals):+5.2f}  "
                f"%positiva={100*sum(v>0 for v in vals)/len(vals):4.0f}%")
    allreal = [r for _, r in real]
    print("  LIVELLI BOT   ", summ(allreal))
    print("  RANDOM (ctrl) ", summ(ctrl))
    if allreal and ctrl:
        verdict = ("REAGISCONO più del caso" if st.median(allreal) > st.median(ctrl) + 0.3
                   else "non distinguibili dal caso")
        print(f"  -> {verdict}")
    print("  --- per tipo di livello ---")
    types = sorted(set(t for t, _ in real))
    for ty in types:
        vv = [r for t, r in real if t == ty]
        print(f"  {ty:12}", summ(vv))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    m15 = pd.read_csv("analysis/data/bars_M15.csv", parse_dates=["time"], index_col="time")
    d1 = pd.read_csv("analysis/data/bars_D1.csv", parse_dates=["time"], index_col="time")
    levels = extract_levels("XAUUSD")
    from collections import Counter
    print(f"Livelli XAUUSD estratti: {len(levels)}  per tipo:",
          dict(Counter(l["type"] for l in levels)))
    print(f"Barre M15: {m15.index[0]} -> {m15.index[-1]}\n")
    test_mechanical(levels, d1)
    test_reactive(levels, m15)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
