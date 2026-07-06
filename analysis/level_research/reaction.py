"""Nucleo di misura: tassonomia reazione + bootstrap clusterizzato sui giorni.

`classify()` e' copiato *fedele* da analysis/trading-bot-eval/level_reaction_analysis.py
(la versione vagliata dall'Agent C): look-ahead-safe, tolleranze ATR-relative, nessuna
ottimizzazione. Qui il side e' "SUPPORT"/"RESISTANCE" (piu' leggibile) invece di long/short.
Le soglie sono quelle PRE-REGISTRATE (docs/LEVEL_RESEARCH_PREREGISTRATION.md): NON toccarle
dopo aver visto i risultati.

Aggiunta rispetto all'originale: `bootstrap_diff_by_day` ricampiona i GIORNI (cluster reale
del walk-forward, dove lo stesso livello strutturale viene ri-rilevato per giorni consecutivi),
non i singoli record — CI onesti a fronte del clustering.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

# ---- soglie PRE-REGISTRATE (immutabili) ------------------------------------
TOL_ATR = 0.10        # tolleranza touch in ATR H1
N_REACT = 4           # barre H1 di reazione dopo il primo touch
TOUCH_WINDOW = 24     # barre H1 entro cui il livello deve essere toccato
REACT_FAV_ATR = 1.0   # escursione favorevole minima (ATR) per dichiarare REACTION

REACTION = "REACTION"
BREAK = "BREAK"
SWEEP = "SWEEP_THEN_BREAK"
WEAK = "TOUCH_NO_REACTION"
NO_TEST = "NO_TEST"
INSUFF = "INSUFFICIENT"
TESTED = frozenset({REACTION, WEAK, BREAK, SWEEP})   # classi "toccato"


def classify(bars: list[dict], zone: float, side: str, atr: float) -> dict:
    """Classifica l'esito del livello sul price path post-segnale (barre gia' filtrate a
    open-time > punto di decisione). side in {'SUPPORT','RESISTANCE'}."""
    tol = TOL_ATR * atr
    sup = side == "SUPPORT"
    res = {"cls": None, "touch_idx": None, "net_atr": None, "fav_atr": None,
           "rejection_wick": False, "displacement": False}

    touch_idx = None
    immediate_break = False
    for i, b in enumerate(bars[:TOUCH_WINDOW]):
        touched = (b["low"] <= zone + tol) if sup else (b["high"] >= zone - tol)
        if not touched:
            continue
        touch_idx = i
        immediate_break = (b["close"] < zone - tol) if sup else (b["close"] > zone + tol)
        break

    if touch_idx is None:
        res["cls"] = NO_TEST if len(bars) >= TOUCH_WINDOW else INSUFF
        return res
    res["touch_idx"] = touch_idx

    tb = bars[touch_idx]
    rng_tb = tb["high"] - tb["low"]
    if rng_tb > 0:
        pos = (tb["close"] - tb["low"]) / rng_tb
        res["rejection_wick"] = (pos >= 2 / 3) if sup else (pos <= 1 / 3)

    win = bars[touch_idx + 1: touch_idx + 1 + N_REACT]
    if len(win) == N_REACT:
        hi = max(b["high"] for b in win)
        lo = min(b["low"] for b in win)
        fav = (hi - zone) if sup else (zone - lo)
        adv = (zone - lo) if sup else (hi - zone)
        res["net_atr"] = (fav - adv) / atr
        res["fav_atr"] = fav / atr

    if immediate_break:
        res["cls"] = BREAK
        return res

    def is_sweep(b):
        return (b["low"] < zone - tol and b["close"] >= zone - tol) if sup else \
               (b["high"] > zone + tol and b["close"] <= zone + tol)

    swept = is_sweep(tb)
    for b in win:
        broke = (b["close"] < zone - tol) if sup else (b["close"] > zone + tol)
        if broke:
            res["cls"] = SWEEP if swept else BREAK
            return res
        swept = swept or is_sweep(b)

    if len(win) < N_REACT:
        res["cls"] = INSUFF
        return res

    for b in win:
        rng = b["high"] - b["low"]
        body = b["close"] - b["open"]
        if rng >= 1.5 * atr and abs(body) >= 0.5 * rng and (body > 0) == sup:
            res["displacement"] = True
            break

    res["cls"] = REACTION if (res["net_atr"] > 0 and res["fav_atr"] >= REACT_FAV_ATR) else WEAK
    return res


# ---------------------------------------------------------------------------
def rate(vals) -> float:
    return 100.0 * sum(vals) / len(vals) if vals else float("nan")


def boot_rate_diff_ci(real_items, rand_items, n_boot=2000, seed=42):
    """CI 95% della differenza di TASSO (%) reale-random, clusterizzato sui giorni, vettoriale.

    real_items/rand_items: liste di (day, 0/1). Aggrega per giorno in (somma, conteggio), poi
    ricampiona i giorni B volte con numpy. Ritorna (lo, hi, diff_puntuale, n_days).
    """
    r_sum, r_cnt = defaultdict(float), defaultdict(int)
    c_sum, c_cnt = defaultdict(float), defaultdict(int)
    for d, v in real_items:
        r_sum[d] += v; r_cnt[d] += 1
    for d, v in rand_items:
        c_sum[d] += v; c_cnt[d] += 1
    days = sorted(set(r_cnt) | set(c_cnt))
    if len(days) < 3:
        return (float("nan"), float("nan"), float("nan"), len(days))
    rs = np.array([r_sum.get(d, 0.0) for d in days])
    rc = np.array([r_cnt.get(d, 0) for d in days], dtype=float)
    cs = np.array([c_sum.get(d, 0.0) for d in days])
    cc = np.array([c_cnt.get(d, 0) for d in days], dtype=float)
    point = (float("nan") if rc.sum() == 0 or cc.sum() == 0
             else 100.0 * (rs.sum() / rc.sum() - cs.sum() / cc.sum()))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(days), size=(n_boot, len(days)))
    rsum, rcnt = rs[idx].sum(1), rc[idx].sum(1)
    csum, ccnt = cs[idx].sum(1), cc[idx].sum(1)
    ok = (rcnt > 0) & (ccnt > 0)
    diff = 100.0 * (rsum[ok] / rcnt[ok] - csum[ok] / ccnt[ok])
    if diff.size < 10:
        return (float("nan"), float("nan"), point, len(days))
    return (float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)),
            point, len(days))


def bootstrap_diff_by_day(real_items, rand_items, stat, n_boot=5000, seed=42):
    """CI 95% della differenza stat(real) - stat(random), ricampionando i GIORNI.

    real_items: lista di (day, value). rand_items: lista di (day, value) del pool random.
    Cluster bootstrap: si ricampionano i giorni distinti; ogni giorno porta con se' TUTTI i
    suoi valori reali e random. Ritorna (lo, hi, diff_puntuale, n_days).
    """
    real_by_day = defaultdict(list)
    rand_by_day = defaultdict(list)
    for d, v in real_items:
        real_by_day[d].append(v)
    for d, v in rand_items:
        rand_by_day[d].append(v)
    days = sorted(set(real_by_day) | set(rand_by_day))
    if len(days) < 3:
        return (float("nan"), float("nan"), float("nan"), len(days))

    rv_all = [v for d in days for v in real_by_day.get(d, [])]
    cv_all = [v for d in days for v in rand_by_day.get(d, [])]
    point = (stat(rv_all) - stat(cv_all)) if (rv_all and cv_all) else float("nan")

    rng = np.random.default_rng(seed)
    idx = np.arange(len(days))
    diffs = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        rv = [v for k in s for v in real_by_day.get(days[k], [])]
        cv = [v for k in s for v in rand_by_day.get(days[k], [])]
        if rv and cv:
            diffs.append(stat(rv) - stat(cv))
    if not diffs:
        return (float("nan"), float("nan"), point, len(days))
    return (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)),
            point, len(days))
