"""Motore reazione-vs-random multi-asset, walk-forward, look-ahead-safe.

Per ogni asset e ogni giorno (punto di decisione = ora fissa DECISION_HOUR):
  1. rileva i livelli dei 6 concetti dalle ultime H1_WINDOW barre CHIUSE (+ PDH/PDL da D1);
  2. filtra geometria (sup<=prezzo, res>=prezzo), dedup entro 0.10*ATR per concetto;
  3. misura la reazione FORWARD con classify() (barre successive al punto di decisione);
  4. genera M random DISTANCE-MATCHED (distanza campionata dal pool reale del concetto/side)
     e li misura allo stesso modo.
Aggrega per (concetto x asset): %REACTION|touch reale vs random con CI block-bootstrap sui
giorni, + escursione netta mediana. Tutto secondo docs/LEVEL_RESEARCH_PREREGISTRATION.md.

Uso: vedi __main__.py.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict

import numpy as np

from detectors import detect_all
from reaction import (INSUFF, REACTION, TESTED, boot_rate_diff_ci,
                      bootstrap_diff_by_day, classify, TOUCH_WINDOW, N_REACT)

DATA = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
DECISION_HOUR = 8          # punto di decisione giornaliero (UTC), sessione Londra
H1_WINDOW = 120            # barre H1 chiuse per la detection (~1 settimana)
ATR_N = 14
M_RANDOM = 5
MAX_FWD = TOUCH_WINDOW + N_REACT + 2
DEDUP_ATR = 0.10
TRAIN_FRAC = 0.70
SEED = 42

CONCEPTS = ["swing", "pdh_pdl", "ob", "fvg", "round", "eqh_eql"]


# ---- IO --------------------------------------------------------------------
def load_bars(prefix, tf):
    path = os.path.join(DATA, f"{prefix}_{tf}.csv")
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                out.append({"t": r["time"][:19],
                            "open": float(r["open"]), "high": float(r["high"]),
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


# ---- decisioni (una passata di detection) ----------------------------------
def _dedup(levels, atr):
    """levels: [(price, side, concept)]. Dedup entro DEDUP_ATR*atr per (concept, side)."""
    tol = DEDUP_ATR * atr
    kept = []
    for pr, side, con in sorted(levels, key=lambda x: (x[2], x[1], x[0])):
        if any(k[2] == con and k[1] == side and abs(k[0] - pr) <= tol for k in kept):
            continue
        kept.append((pr, side, con))
    return kept


def build_decisions(asset):
    """Ritorna (h1, lista di decisioni). Ogni decisione:
    {day, di, P0, atr, levels=[(price, side, concept, dist_atr)]}."""
    h1 = load_bars(asset, "H1")
    d1 = load_bars(asset, "D1")
    if not h1 or not d1:
        return h1, []
    atr = atr_series(h1)
    d1_by_date = {b["t"][:10]: b for b in d1}
    d1_dates = sorted(d1_by_date)

    # primo indice H1 con ora >= DECISION_HOUR per ogni giorno
    by_day = defaultdict(list)
    for i, b in enumerate(h1):
        by_day[b["t"][:10]].append(i)
    decisions = []
    import bisect
    for day in sorted(by_day):
        di = next((i for i in by_day[day] if int(h1[i]["t"][11:13]) >= DECISION_HOUR), None)
        if di is None or di < H1_WINDOW or di < 1:
            continue
        a = atr[di - 1]
        if not a or a <= 0:
            continue
        P0 = h1[di - 1]["close"]
        window = h1[di - H1_WINDOW:di]
        pos = bisect.bisect_left(d1_dates, day)
        prev_d1 = d1_by_date[d1_dates[pos - 1]] if pos > 0 else None
        raw = detect_all(window, prev_d1, P0, a, asset)
        # geometria valida
        geo = []
        for pr, side, con in raw:
            if pr <= 0:
                continue
            if side == "SUPPORT" and pr > P0:
                continue
            if side == "RESISTANCE" and pr < P0:
                continue
            geo.append((pr, side, con))
        levels = [(pr, side, con, abs(pr - P0) / a) for pr, side, con in _dedup(geo, a)
                  if abs(pr - P0) / a > 1e-9]
        if levels:
            decisions.append({"day": day, "di": di, "P0": P0, "atr": a, "levels": levels})
    return h1, decisions


# ---- misura reale + random distance-matched --------------------------------
def measure_core(h1, decisions):
    """Cuore della misura: dato h1 + lista decisioni gia' filtrate, ritorna per concetto gli
    item (day,val) per rate-diff e per net-median, reale/random distance-matched."""
    if not decisions:
        return None
    rng = np.random.default_rng(SEED)

    # pool distanze reali per (concetto, side) -> per il random distance-matched
    pool = defaultdict(list)
    for dec in decisions:
        for pr, side, con, dist in dec["levels"]:
            pool[(con, side)].append(dist)
    pool = {k: np.array(v) for k, v in pool.items()}

    acc = {c: {"real": [], "rand": [], "net_real": [], "net_rand": [],
               "n_levels": 0, "n_touch": 0} for c in CONCEPTS}

    for dec in decisions:
        di, P0, a, day = dec["di"], dec["P0"], dec["atr"], dec["day"]
        fwd = h1[di:di + MAX_FWD]
        if len(fwd) < 3:
            continue
        for pr, side, con, dist in dec["levels"]:
            A = acc[con]
            A["n_levels"] += 1
            real = classify(fwd, pr, side, a)
            if real["cls"] != INSUFF:
                if real["cls"] in TESTED:
                    A["n_touch"] += 1
                    A["real"].append((day, 1.0 if real["cls"] == REACTION else 0.0))
                if real["net_atr"] is not None:
                    A["net_real"].append((day, real["net_atr"]))
            # random distance-matched
            dpool = pool.get((con, side))
            if dpool is None or len(dpool) == 0:
                continue
            for _ in range(M_RANDOM):
                dprime = float(rng.choice(dpool))
                rp = P0 - dprime * a if side == "SUPPORT" else P0 + dprime * a
                if rp <= 0:
                    continue
                rc = classify(fwd, rp, side, a)
                if rc["cls"] == INSUFF:
                    continue
                if rc["cls"] in TESTED:
                    A["rand"].append((day, 1.0 if rc["cls"] == REACTION else 0.0))
                if rc["net_atr"] is not None:
                    A["net_rand"].append((day, rc["net_atr"]))
    return acc


def split_days(decisions):
    """Divide i giorni-decisione in (train, test) 70/30 temporale."""
    days = sorted({d["day"] for d in decisions})
    if len(days) < 10:
        return set(days), set()
    cut = int(TRAIN_FRAC * len(days))
    return set(days[:cut]), set(days[cut:])


def measure_asset(asset, days_keep=None):
    """Comodita' standalone: build + (filtro giorni) + measure_core."""
    h1, decisions = build_decisions(asset)
    if days_keep is not None:
        decisions = [d for d in decisions if d["day"] in days_keep]
    return measure_core(h1, decisions)


# ---- sommario per cella (concetto x asset) ---------------------------------
def summarize_cell(A, boot_rate=2000, boot_med=800):
    """Da un accumulatore-concetto a un dizionario di statistiche + verdetto."""
    from reaction import rate
    real, rand = A["real"], A["rand"]
    rr_real = rate([v for _, v in real]) * 1 if real else float("nan")
    rr_rand = rate([v for _, v in rand]) * 1 if rand else float("nan")
    lo, hi, dpoint, n_days = boot_rate_diff_ci(real, rand, n_boot=boot_rate, seed=SEED)
    beats = (not np.isnan(lo)) and lo > 0
    # escursione netta mediana
    med_real = float(np.median([v for _, v in A["net_real"]])) if A["net_real"] else float("nan")
    med_rand = float(np.median([v for _, v in A["net_rand"]])) if A["net_rand"] else float("nan")
    mlo = mhi = float("nan")
    # CI mediana (secondaria) solo su campioni gestibili: il pool multi-asset e' enorme e il
    # verdetto poggia comunque sul CI del TASSO (primaria). n_days>6000 -> solo punto.
    if 20 <= len(A["net_real"]) and 20 <= len(A["net_rand"]) and n_days <= 6000:
        mlo, mhi, _, _ = bootstrap_diff_by_day(
            A["net_real"], A["net_rand"], lambda v: float(np.median(v)),
            n_boot=boot_med, seed=SEED)
    return {"n_levels": A["n_levels"], "n_touch": A["n_touch"], "n_days": n_days,
            "rr_real": rr_real, "rr_rand": rr_rand, "diff": dpoint,
            "ci_lo": lo, "ci_hi": hi, "beats": beats,
            "net_real": med_real, "net_rand": med_rand, "net_lo": mlo, "net_hi": mhi}
