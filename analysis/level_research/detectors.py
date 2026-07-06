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


def detect_all(bars, prev_d1, price, atr, asset):
    """Tutti i concetti -> lista di (price, side, concept). Grezzi, non filtrati."""
    step = ROUND_STEP.get(asset)
    lv = []
    lv += swing_sr(bars)
    lv += pdh_pdl(prev_d1)
    lv += order_block(bars)
    lv += fvg(bars)
    lv += round_number(price, step)
    lv += eqh_eql(bars, atr)
    return lv
