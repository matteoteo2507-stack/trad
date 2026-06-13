"""Porting fedele della logica livelli/bias del bot (modules/marketBias.js) in Python.

Symbol-agnostic: prende candele OHLC e produce gli STESSI livelli/bias del bot,
così possiamo (a) ricalcolare i livelli XAU su feed SPOT (il bot usa GC=F futures),
(b) riusare la stessa logica per la strategia BTC, (c) correggere i difetti noti
(es. aggregazione 4H) quando vorremo.

Funzioni 1:1 col bot:
  analyze_bias, calc_confluence, get_key_levels, detect_order_blocks,
  detect_fvg, get_entry_points, aggregate_4h.

Candela = dict {open, high, low, close, volume?} oppure namedtuple con quei campi.
"""

from __future__ import annotations

from typing import Any


def _g(c: Any, k: str) -> float:
    return float(c[k] if isinstance(c, dict) else getattr(c, k))


# ─── BIAS PRICE ACTION (per timeframe) ───────────────────────────────────
def analyze_bias(candles: list, label: str = "") -> dict:
    if not candles or len(candles) < 5:
        return {"bias": "INDECISO", "emoji": "⚪", "score": 0, "bull": 0, "bear": 0,
                "reasons": ["Dati insufficienti"]}
    last, prev, prev2 = candles[-1], candles[-2], candles[-3]
    lo, ho, ho2 = _g(last, "low"), _g(prev, "high"), _g(prev2, "high")
    bull = bear = 0
    reasons = []

    if _g(last, "close") > _g(last, "open"):
        bull += 2; reasons.append(f"Candela {label} bullish")
    else:
        bear += 2; reasons.append(f"Candela {label} bearish")

    rng = _g(last, "high") - _g(last, "low")
    if rng > 0:
        pos = (_g(last, "close") - _g(last, "low")) / rng
        if pos > 0.70:
            bull += 2; reasons.append("Close terzo superiore")
        elif pos < 0.30:
            bear += 2; reasons.append("Close terzo inferiore")

    if _g(last, "close") > _g(prev, "high"):
        bull += 3; reasons.append("BOS bullish")
    elif _g(last, "close") < _g(prev, "low"):
        bear += 3; reasons.append("BOS bearish")

    if (_g(last, "high") > _g(prev, "high") and _g(last, "low") > _g(prev, "low")
            and _g(prev, "high") > _g(prev2, "high") and _g(prev, "low") > _g(prev2, "low")):
        bull += 2; reasons.append("Struttura HH+HL")
    elif (_g(last, "high") < _g(prev, "high") and _g(last, "low") < _g(prev, "low")
          and _g(prev, "high") < _g(prev2, "high") and _g(prev, "low") < _g(prev2, "low")):
        bear += 2; reasons.append("Struttura LH+LL")

    prev_range = _g(prev, "high") - _g(prev, "low")
    if rng > prev_range * 1.3:
        if _g(last, "close") > _g(last, "open"):
            bull += 1; reasons.append("Range espanso bullish")
        else:
            bear += 1; reasons.append("Range espanso bearish")

    total = bull + bear
    score = round((bull - bear) / total * 100) if total > 0 else 0
    bias = "RIALZISTA" if bull > bear + 1 else "RIBASSISTA" if bear > bull + 1 else "INDECISO"
    emoji = "🟢" if bias == "RIALZISTA" else "🔴" if bias == "RIBASSISTA" else "🟡"
    return {"bias": bias, "emoji": emoji, "score": score, "bull": bull, "bear": bear,
            "reasons": reasons}


def calc_confluence(daily: dict, tf4h: dict, tf1h: dict) -> dict:
    votes = [daily["bias"], tf4h["bias"], tf1h["bias"]]
    bull = votes.count("RIALZISTA")
    bear = votes.count("RIBASSISTA")
    if bull == 3:
        sig, emoji, score = "LONG FORTE", "🚀", 100
    elif bull == 2:
        sig, emoji, score = "LONG", "🟢", 66
    elif bear == 3:
        sig, emoji, score = "SHORT FORTE", "💥", -100
    elif bear == 2:
        sig, emoji, score = "SHORT", "🔴", -66
    else:
        sig, emoji, score = "NEUTRO", "⚪", 0
    return {"signal": sig, "emoji": emoji, "score": score, "bull": bull, "bear": bear,
            "neutral": 3 - bull - bear}


# ─── LIVELLI ─────────────────────────────────────────────────────────────
def get_key_levels(candles: list) -> dict:
    if len(candles) < 3:
        return {"supports": [], "resistances": []}
    sup, res = [], []
    for i in range(1, len(candles) - 1):
        if _g(candles[i], "low") < _g(candles[i-1], "low") and _g(candles[i], "low") < _g(candles[i+1], "low"):
            sup.append(_g(candles[i], "low"))
        if _g(candles[i], "high") > _g(candles[i-1], "high") and _g(candles[i], "high") > _g(candles[i+1], "high"):
            res.append(_g(candles[i], "high"))
    return {"supports": list(reversed(sup[-4:])), "resistances": list(reversed(res[-4:]))}


def detect_order_blocks(candles: list) -> list:
    obs = []
    for i in range(1, len(candles) - 2):
        c, n1, n2 = candles[i], candles[i+1], candles[i+2]
        if _g(c, "close") < _g(c, "open") and (_g(n1, "close") > _g(c, "high") or _g(n2, "close") > _g(c, "high")):
            obs.append({"type": "BULLISH_OB", "high": _g(c, "high"), "low": _g(c, "low")})
        if _g(c, "close") > _g(c, "open") and (_g(n1, "close") < _g(c, "low") or _g(n2, "close") < _g(c, "low")):
            obs.append({"type": "BEARISH_OB", "high": _g(c, "high"), "low": _g(c, "low")})
    return obs[-3:]


def detect_fvg(candles: list) -> list:
    fvgs = []
    for i in range(1, len(candles) - 1):
        p, n = candles[i-1], candles[i+1]
        if _g(n, "low") > _g(p, "high"):
            fvgs.append({"type": "BULLISH_FVG", "high": _g(n, "low"), "low": _g(p, "high")})
        if _g(n, "high") < _g(p, "low"):
            fvgs.append({"type": "BEARISH_FVG", "high": _g(p, "low"), "low": _g(n, "high")})
    return fvgs[-3:]


def get_entry_points(candles: list) -> list:
    """PDH/PDL/PDC + swing + OB + FVG, con distanza % dal prezzo corrente, top 7."""
    last, prev = candles[-1], candles[-2]
    price = _g(last, "close")
    entries = [
        {"label": "PDH (Max Ieri)", "price": _g(prev, "high"), "type": "RESISTANCE", "priority": "HIGH"},
        {"label": "PDL (Min Ieri)", "price": _g(prev, "low"), "type": "SUPPORT", "priority": "HIGH"},
        {"label": "PDC (Close Ieri)", "price": _g(prev, "close"), "type": "NEUTRAL", "priority": "MEDIUM"},
    ]
    kl = get_key_levels(candles)
    for p in kl["supports"][:2]:
        entries.append({"label": "Supporto Swing", "price": p, "type": "SUPPORT", "priority": "MEDIUM"})
    for p in kl["resistances"][:2]:
        entries.append({"label": "Resistenza Swing", "price": p, "type": "RESISTANCE", "priority": "MEDIUM"})
    for ob in detect_order_blocks(candles):
        mid = (ob["high"] + ob["low"]) / 2
        entries.append({"label": "OB Bullish" if ob["type"] == "BULLISH_OB" else "OB Bearish",
                        "price": mid, "priceHigh": ob["high"], "priceLow": ob["low"],
                        "type": "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE", "priority": "HIGH"})
    for fvg in detect_fvg(candles):
        mid = (fvg["high"] + fvg["low"]) / 2
        entries.append({"label": "FVG Bullish" if fvg["type"] == "BULLISH_FVG" else "FVG Bearish",
                        "price": mid, "priceHigh": fvg["high"], "priceLow": fvg["low"],
                        "type": "SUPPORT" if fvg["type"] == "BULLISH_FVG" else "RESISTANCE", "priority": "MEDIUM"})
    out = [e for e in entries if e["price"] > 0]
    for e in out:
        e["distancePct"] = abs((e["price"] - price) / price) * 100
    out.sort(key=lambda e: e["distancePct"])
    return out[:7]


def cluster_confluence(entries: list, tol_pct: float = 0.30) -> list:
    """Raggruppa i livelli (output di get_entry_points) entro `tol_pct` in ZONE di
    confluenza. Ogni zona: prezzo medio, n. confluenze, tipi, side dominante.

    Una zona con confluence>=2 e tipi diversi (es. PDL+OB+FVG) è un livello "forte":
    è il trigger della variante manuale e il punto preferito dei pending della
    variante semiauto.
    """
    if not entries:
        return []
    es = sorted(entries, key=lambda e: e["price"])
    zones: list[dict] = []
    for e in es:
        if zones and abs(e["price"] - zones[-1]["anchor"]) / zones[-1]["anchor"] * 100 <= tol_pct:
            zones[-1]["members"].append(e)
            zones[-1]["anchor"] = sum(m["price"] for m in zones[-1]["members"]) / len(zones[-1]["members"])
        else:
            zones.append({"anchor": e["price"], "members": [e]})
    out = []
    for z in zones:
        m = z["members"]
        sides = [x["type"] for x in m]
        n_sup = sides.count("SUPPORT"); n_res = sides.count("RESISTANCE")
        side = "SUPPORT" if n_sup > n_res else "RESISTANCE" if n_res > n_sup else "MIXED"
        out.append({
            "price": round(z["anchor"], 2),
            "confluence": len(m),
            "types": [x["label"] for x in m],
            "side": side,
            "distancePct": min(x.get("distancePct", 0) for x in m),
            "min": min(x.get("priceLow", x["price"]) for x in m),
            "max": max(x.get("priceHigh", x["price"]) for x in m),
        })
    out.sort(key=lambda z: z["distancePct"])
    return out


def aggregate_4h(candles_1h: list) -> list:
    """NB: come il bot — blocchi di 4 dall'inizio array (NON allineato ai veri 4H)."""
    res = []
    for i in range(0, len(candles_1h) - 3, 4):
        g = candles_1h[i:i+4]
        res.append({"open": _g(g[0], "open"), "high": max(_g(c, "high") for c in g),
                    "low": min(_g(c, "low") for c in g), "close": _g(g[3], "close")})
    return res
