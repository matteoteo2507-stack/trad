"""Detector S/R via swing pivots + clustering.

Algoritmo (deterministico):

1. **ZigZag pivots**: scorre le barre, identifica swing high/low che differiscono
   dall'ultimo pivot di almeno `threshold` (espresso in multipli di ATR). Ogni
   pivot è un punto (timestamp, price, kind).
2. **Cluster orizzontale**: i pivot vengono fusi se distanti meno di
   `cluster_width_pips`. Ogni cluster diventa un livello S/R con prezzo = media
   pesata e `touch_count` = numero di pivot fusi.
3. **Touch count storico**: dopo il clustering, ricontiamo quante volte il
   prezzo (close delle barre successive al cluster) è tornato entro
   `cluster_width_pips / 2` dal livello, senza romperlo. Questo dà la stima
   reale di "quante volte è stato testato" — soglia di freshness.

Output: lista di `SRLevel(price, kind, touch_count, last_touch, tf_label)`.

Riferimenti: nessun paper specifico — è la formulazione standard "swing pivots
+ horizontal cluster" usata in vari libri di TA classica (Murphy 1999,
Schabacker 1932). Non è una scoperta accademica, è un metodo descrittivo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

PivotKind = Literal["high", "low"]


@dataclass
class Pivot:
    timestamp: pd.Timestamp
    price: float
    kind: PivotKind


@dataclass
class SRLevel:
    price: float
    kind: PivotKind                  # "high" → resistance, "low" → support
    touch_count: int
    last_touch: pd.Timestamp
    tf_label: str                    # "D1" o "H4"


# ---------------------------------------------------------------------------
# ZigZag pivots
# ---------------------------------------------------------------------------

def _atr(bars: pd.DataFrame, period: int = 14) -> float:
    """ATR Wilder, restituisce solo l'ultimo valore."""
    high, low, close = bars["high"], bars["low"], bars["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean().iloc[-1])


def zigzag_pivots(
    bars: pd.DataFrame,
    threshold: float,
) -> list[Pivot]:
    """ZigZag classico. `threshold` in unità di prezzo (non %).

    Algoritmo: traccia il candidato pivot corrente; quando la barra successiva
    si discosta dal candidato di >= threshold nella direzione opposta, conferma
    il pivot e inverte direzione.
    """
    if len(bars) < 3:
        return []

    pivots: list[Pivot] = []
    # Stato: direzione corrente ("up" cerca high, "down" cerca low) e candidato.
    direction = "up"
    cand_idx = 0
    cand_price = bars["high"].iat[0]

    for i in range(1, len(bars)):
        hi = bars["high"].iat[i]
        lo = bars["low"].iat[i]
        if direction == "up":
            if hi > cand_price:
                cand_idx = i
                cand_price = hi
            elif cand_price - lo >= threshold:
                # confirmed high
                pivots.append(Pivot(
                    timestamp=bars.index[cand_idx],
                    price=float(cand_price),
                    kind="high",
                ))
                direction = "down"
                cand_idx = i
                cand_price = lo
        else:  # direction == "down"
            if lo < cand_price:
                cand_idx = i
                cand_price = lo
            elif hi - cand_price >= threshold:
                # confirmed low
                pivots.append(Pivot(
                    timestamp=bars.index[cand_idx],
                    price=float(cand_price),
                    kind="low",
                ))
                direction = "up"
                cand_idx = i
                cand_price = hi

    return pivots


# ---------------------------------------------------------------------------
# Cluster orizzontale
# ---------------------------------------------------------------------------

def _cluster_pivots(
    pivots: list[Pivot],
    cluster_width: float,
    kind: PivotKind,
) -> list[SRLevel]:
    """Fonde pivot dello stesso kind che cadono entro `cluster_width` l'uno
    dall'altro.

    Sliding-window orizzontale: ordina per prezzo, raggruppa quando la distanza
    dal pivot precedente è < cluster_width.
    """
    same = [p for p in pivots if p.kind == kind]
    if not same:
        return []
    same.sort(key=lambda p: p.price)

    clusters: list[list[Pivot]] = [[same[0]]]
    for p in same[1:]:
        if p.price - clusters[-1][-1].price <= cluster_width:
            clusters[-1].append(p)
        else:
            clusters.append([p])

    levels: list[SRLevel] = []
    for cluster in clusters:
        avg_price = float(np.mean([p.price for p in cluster]))
        last_touch = max(p.timestamp for p in cluster)
        levels.append(SRLevel(
            price=avg_price,
            kind=kind,
            touch_count=len(cluster),
            last_touch=last_touch,
            tf_label="",  # popolato dal chiamante
        ))
    return levels


# ---------------------------------------------------------------------------
# Touch counter storico
# ---------------------------------------------------------------------------

def _recount_touches(
    bars: pd.DataFrame,
    level: SRLevel,
    tolerance: float,
) -> int:
    """Conta quante volte il prezzo (high/low della barra) ha "toccato" il livello.

    Definizione di touch: la candela include il livello entro `tolerance` ma
    non lo rompe in modo decisivo (close oltre il livello).

    Per resistance (kind=high): touch se high >= level - tol AND close <= level + tol.
    Per support (kind=low):    touch se low  <= level + tol AND close >= level - tol.
    """
    high = bars["high"].to_numpy()
    low = bars["low"].to_numpy()
    close = bars["close"].to_numpy()
    if level.kind == "high":
        hit = (high >= level.price - tolerance) & (close <= level.price + tolerance)
    else:
        hit = (low <= level.price + tolerance) & (close >= level.price - tolerance)
    return int(hit.sum())


# ---------------------------------------------------------------------------
# API pubblica
# ---------------------------------------------------------------------------

def detect_sr_levels(
    bars: pd.DataFrame,
    *,
    threshold_atr_mult: float,
    cluster_width_pips: float,
    pip_size: float,
    min_touches: int = 1,
    max_levels: int = 6,
    tf_label: str = "",
    atr_period: int = 14,
) -> list[SRLevel]:
    """Detect support & resistance da barre OHLC.

    Args:
        bars: DataFrame con `open, high, low, close`.
        threshold_atr_mult: moltiplicatore ATR per soglia ZigZag.
        cluster_width_pips: ampiezza in pip del cluster orizzontale.
        pip_size: dimensione del pip (0.0001 EURUSD, 0.10 XAU).
        min_touches: minimo touch storici per qualificare il livello.
        max_levels: cap sul numero di livelli restituiti (top per touch_count).
        tf_label: etichetta del timeframe ("D1", "H4") da scrivere su ogni level.

    Returns:
        Lista SRLevel ordinati per touch_count desc + recency.
    """
    if len(bars) < atr_period + 5:
        return []

    atr_val = _atr(bars, atr_period)
    if not np.isfinite(atr_val) or atr_val <= 0:
        return []

    threshold = threshold_atr_mult * atr_val
    cluster_width = cluster_width_pips * pip_size
    tolerance = cluster_width / 2.0

    pivots = zigzag_pivots(bars, threshold=threshold)
    levels: list[SRLevel] = []
    for kind in ("high", "low"):
        clustered = _cluster_pivots(pivots, cluster_width, kind)  # type: ignore[arg-type]
        for lvl in clustered:
            lvl.tf_label = tf_label
            lvl.touch_count = _recount_touches(bars, lvl, tolerance)
        levels.extend(clustered)

    # Filtra per touch minimi + sort + cap.
    levels = [lvl for lvl in levels if lvl.touch_count >= min_touches]
    levels.sort(key=lambda L: (-L.touch_count, -L.last_touch.value))
    return levels[:max_levels]
