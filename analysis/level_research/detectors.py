"""Detector dei 6 concetti OHLC-puri (v1), come da PRE-REGISTRAZIONE.

Ogni detector prende barre H1 chiuse (finestra di detection) + contesto e ritorna livelli
grezzi come tuple (price, side, concept) con side in {'SUPPORT','RESISTANCE'}. Il filtro di
geometria (supporti <= prezzo, resistenze >= prezzo), la dedup e la distanza sono applicati
a valle nell'engine. Swing/OB/FVG riusano `analysis/veltrix/levels_engine.py` (nessuna logica
reinventata).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "veltrix"))
import levels_engine as le  # noqa: E402

# passo round-number per asset (PRE-REGISTRATO)
ROUND_STEP = {
    "EURUSD": 0.0050, "GBPUSD": 0.0050, "AUDUSD": 0.0050, "USDCAD": 0.0050,
    "NZDUSD": 0.0050, "USDCHF": 0.0050, "EURGBP.r": 0.0050,
    "USDJPY": 0.50, "EURJPY.r": 0.50, "GBPJPY.r": 0.50,
    "XAUUSD": 25.0, "XAGUSD": 0.50, "BTCUSD": 1000.0, "ETHUSD": 100.0,
    "US500": 25.0, "US100": 100.0,
}


def swing_sr(bars):
    kl = le.get_key_levels(bars)
    out = [(p, "SUPPORT", "swing") for p in kl["supports"]]
    out += [(p, "RESISTANCE", "swing") for p in kl["resistances"]]
    return out


def pdh_pdl(prev_d1):
    if not prev_d1:
        return []
    return [(prev_d1["high"], "RESISTANCE", "pdh_pdl"),
            (prev_d1["low"], "SUPPORT", "pdh_pdl")]


def order_block(bars):
    out = []
    for ob in le.detect_order_blocks(bars):
        mid = (ob["high"] + ob["low"]) / 2
        side = "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE"
        out.append((mid, side, "ob"))
    return out


def fvg(bars):
    out = []
    for f in le.detect_fvg(bars):
        mid = (f["high"] + f["low"]) / 2
        side = "SUPPORT" if f["type"] == "BULLISH_FVG" else "RESISTANCE"
        out.append((mid, side, "fvg"))
    return out


def round_number(price, step, n_each=2):
    if not step or step <= 0:
        return []
    base = price - (price % step)          # round <= price
    out = []
    for k in range(n_each):
        out.append((base - k * step, "SUPPORT", "round"))
        out.append((base + (k + 1) * step, "RESISTANCE", "round"))
    return out


def _pivots(bars):
    """(pivot_highs, pivot_lows) a 3 candele su tutta la finestra."""
    hs, ls = [], []
    for i in range(1, len(bars) - 1):
        if bars[i]["high"] > bars[i - 1]["high"] and bars[i]["high"] > bars[i + 1]["high"]:
            hs.append(bars[i]["high"])
        if bars[i]["low"] < bars[i - 1]["low"] and bars[i]["low"] < bars[i + 1]["low"]:
            ls.append(bars[i]["low"])
    return hs, ls


def eqh_eql(bars, atr, tol_atr=0.10):
    """>=2 pivot high (o low) entro tol_atr = pool di liquidita'; livello = media del cluster."""
    if atr <= 0:
        return []
    tol = tol_atr * atr
    hs, ls = _pivots(bars)
    out = []
    for piv, side, tag in ((hs, "RESISTANCE", "eqh"), (ls, "SUPPORT", "eql")):
        piv = sorted(piv)
        i = 0
        while i < len(piv):
            j = i
            while j + 1 < len(piv) and piv[j + 1] - piv[i] <= tol:
                j += 1
            if j > i:  # almeno 2 nel cluster
                out.append((sum(piv[i:j + 1]) / (j - i + 1), side, "eqh_eql"))
            i = j + 1
    return out


# ─── VOLUME (v2, tick-volume proxy) ──────────────────────────────────────
def _side(pr, price):
    return "SUPPORT" if pr <= price else "RESISTANCE"


def volume_profile(bars, price, atr, va_frac=0.70, bin_atr=0.20):
    """POC/VAH/VAL sul volume profile delle barre. Volume di ogni barra distribuito
    uniformemente sul suo range [low,high]; bin di ampiezza bin_atr*ATR."""
    if atr <= 0 or len(bars) < 5:
        return []
    lo = min(b["low"] for b in bars)
    hi = max(b["high"] for b in bars)
    if hi <= lo:
        return []
    binw = bin_atr * atr
    nb = max(1, int((hi - lo) / binw) + 1)
    vol = [0.0] * nb
    for b in bars:
        v = b.get("volume", 0.0) or 0.0
        if v <= 0:
            continue
        if b["high"] <= b["low"]:
            k = min(nb - 1, max(0, int((b["close"] - lo) / binw)))
            vol[k] += v
            continue
        k0 = max(0, int((b["low"] - lo) / binw))
        k1 = min(nb - 1, int((b["high"] - lo) / binw))
        share = v / (k1 - k0 + 1)
        for k in range(k0, k1 + 1):
            vol[k] += share
    total = sum(vol)
    if total <= 0:
        return []
    poc_k = max(range(nb), key=lambda k: vol[k])
    inc, acc = {poc_k}, vol[poc_k]
    left, right = poc_k - 1, poc_k + 1
    while acc < va_frac * total and (left >= 0 or right < nb):
        lv = vol[left] if left >= 0 else -1.0
        rv = vol[right] if right < nb else -1.0
        if lv >= rv:
            acc += vol[left]; inc.add(left); left -= 1
        else:
            acc += vol[right]; inc.add(right); right += 1
    center = lambda k: lo + (k + 0.5) * binw  # noqa: E731
    poc, vah, val = center(poc_k), center(max(inc)), center(min(inc))
    return [(poc, _side(poc, price), "poc"),
            (vah, _side(vah, price), "poc"),
            (val, _side(val, price), "poc")]


def _typ_vwap(bars):
    num = den = 0.0
    for b in bars:
        v = b.get("volume", 0.0) or 0.0
        num += (b["high"] + b["low"] + b["close"]) / 3 * v
        den += v
    return num / den if den > 0 else None


def vwap_level(bars, price):
    vw = _typ_vwap(bars)
    return [(vw, _side(vw, price), "vwap")] if vw and vw > 0 else []


def avwap_levels(bars, price):
    """2 AVWAP ancorate agli estremi della finestra (max-high e min-low) fino a 'ora'."""
    if len(bars) < 5:
        return []
    hi_i = max(range(len(bars)), key=lambda i: bars[i]["high"])
    lo_i = min(range(len(bars)), key=lambda i: bars[i]["low"])
    out = []
    for anchor in {hi_i, lo_i}:
        vw = _typ_vwap(bars[anchor:])
        if vw and vw > 0:
            out.append((vw, _side(vw, price), "avwap"))
    return out


# ─── dispatch ────────────────────────────────────────────────────────────
DISPATCH = {
    "swing": lambda bars, prev_d1, price, atr, asset: swing_sr(bars),
    "pdh_pdl": lambda bars, prev_d1, price, atr, asset: pdh_pdl(prev_d1),
    "ob": lambda bars, prev_d1, price, atr, asset: order_block(bars),
    "fvg": lambda bars, prev_d1, price, atr, asset: fvg(bars),
    "round": lambda bars, prev_d1, price, atr, asset: round_number(price, ROUND_STEP.get(asset)),
    "eqh_eql": lambda bars, prev_d1, price, atr, asset: eqh_eql(bars, atr),
    "poc": lambda bars, prev_d1, price, atr, asset: volume_profile(bars, price, atr),
    "vwap": lambda bars, prev_d1, price, atr, asset: vwap_level(bars, price),
    "avwap": lambda bars, prev_d1, price, atr, asset: avwap_levels(bars, price),
}
OHLC_CONCEPTS = ["swing", "pdh_pdl", "ob", "fvg", "round", "eqh_eql"]
VOLUME_CONCEPTS = ["poc", "vwap", "avwap"]


def detect_all(bars, prev_d1, price, atr, asset, concepts):
    """Concetti richiesti -> lista di (price, side, concept). Grezzi, non filtrati."""
    lv = []
    for c in concepts:
        lv += DISPATCH[c](bars, prev_d1, price, atr, asset)
    return lv
