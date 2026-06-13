"""Core: zone di confluenza conf=2 con lato/SL/TP/RR. Logica pura, offline-testabile.

Riusa analysis/veltrix/levels_engine.py (port fedele dei detector: swing S/R, OB, FVG,
PD levels, cluster_confluence). La spec (validata) e':
  - aggrega nature -> cluster in zone -> tieni SOLO confluence == 2;
  - fade: long su SUPPORT, short su RESISTANCE;
  - SL = k_sl * ATR(H1);  TP = RR * SL.
"""
from __future__ import annotations

import os
import sys

_VELTRIX = os.path.join(os.path.dirname(__file__), "..", "analysis", "veltrix")
if _VELTRIX not in sys.path:
    sys.path.insert(0, _VELTRIX)
import levels_engine as le  # noqa: E402


def atr(h1: list, n: int = 14) -> float:
    """ATR semplice sugli ultimi n+1 bar H1 (dict open/high/low/close)."""
    if len(h1) < n + 1:
        return 0.0
    trs = []
    for i in range(len(h1) - n, len(h1)):
        pc = h1[i - 1]["close"]
        trs.append(max(h1[i]["high"] - h1[i]["low"],
                       abs(h1[i]["high"] - pc), abs(h1[i]["low"] - pc)))
    return sum(trs) / len(trs)


def build_entries(prev_daily: dict, h1_window: list) -> list:
    e = [{"price": prev_daily["high"], "type": "RESISTANCE", "label": "PDH"},
         {"price": prev_daily["low"], "type": "SUPPORT", "label": "PDL"}]
    kl = le.get_key_levels(h1_window)
    for p in kl["supports"]:
        e.append({"price": p, "type": "SUPPORT", "label": "Swing_S"})
    for p in kl["resistances"]:
        e.append({"price": p, "type": "RESISTANCE", "label": "Swing_R"})
    for ob in le.detect_order_blocks(h1_window):
        e.append({"price": (ob["high"] + ob["low"]) / 2, "label": "OB",
                  "type": "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE"})
    for f in le.detect_fvg(h1_window):
        e.append({"price": (f["high"] + f["low"]) / 2, "label": "FVG",
                  "type": "SUPPORT" if f["type"] == "BULLISH_FVG" else "RESISTANCE"})
    return e


def conf2_signals(prev_daily: dict, h1_window: list, price: float, *,
                  k_sl: float, rr: float, cluster_tol_pct: float,
                  max_dist_atr: float, atr_val: float | None = None) -> list:
    """Ritorna le zone conf=2 vicine al prezzo, con lato/entry/SL/TP/RR/distanza."""
    a = atr_val if atr_val is not None else atr(h1_window)
    if a <= 0:
        return []
    zones = le.cluster_confluence(build_entries(prev_daily, h1_window), tol_pct=cluster_tol_pct)
    out = []
    sl_dist = k_sl * a
    for z in zones:
        if z["confluence"] != 2 or z["side"] not in ("SUPPORT", "RESISTANCE"):
            continue
        dist = abs(z["price"] - price)
        if dist > max_dist_atr * a:
            continue
        entry = z["price"]
        if z["side"] == "SUPPORT":
            side, sl, tp = "long", entry - sl_dist, entry + rr * sl_dist
        else:
            side, sl, tp = "short", entry + sl_dist, entry - rr * sl_dist
        out.append({
            "side": side, "zone": round(entry, 2), "sl": round(sl, 2), "tp": round(tp, 2),
            "rr": rr, "sl_dist": round(sl_dist, 2), "confluence": z["confluence"],
            "types": z["types"], "dist": round(dist, 2), "dist_atr": round(dist / a, 2),
            "atr": round(a, 2),
        })
    out.sort(key=lambda s: s["dist"])
    return out
