"""Detector Supply/Demand zones via pattern base-impulse-base.

Algoritmo (deterministico):

1. **Base detection**: finestra di K barre (K ∈ [base_min_bars, base_max_bars])
   in cui ogni barra ha range high-low < base_range_atr_mult × ATR.
   Filtro: il range complessivo (max(high) - min(low)) della base anch'esso
   < base_range_atr_mult × ATR. Le candele indecise (small body) qualificano.
2. **Impulse confirmation**: la barra **immediatamente successiva** alla base
   deve avere range >= impulse_atr_mult × ATR e direzione coerente:
   - Impulse rialzista (close > open con body grosso) → la base è una
     **demand zone** (i compratori sono entrati lì).
   - Impulse ribassista (close < open) → la base è una **supply zone**.
3. **Bordi della zona**:
   - Demand: prossimale = high massimo della base; distale = low minimo.
   - Supply: prossimale = low minimo della base; distale = high massimo.
4. **Freshness**: contiamo i touch successivi. Una zona con > max_touches
   viene considerata esaurita (`fresh=False`).

Riferimenti: pattern descritto in Sam Seiden ("Online Trading Academy"
methodology) e variazioni della scuola order-flow. Non c'è paper peer-reviewed
sul S/D retail trading; la giustificazione concettuale è che gli ordini
istituzionali lasciati "non eseguiti" nella base vengono colpiti al ritorno.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

ZoneKind = Literal["demand", "supply"]


@dataclass
class SDZone:
    kind: ZoneKind
    proximal: float          # bordo "interno" (più vicino al lato da cui si entra)
    distal: float            # bordo "esterno" (lo SL si piazza oltre)
    created_at: pd.Timestamp
    base_size: int           # numero di barre della base
    impulse_strength: float  # range della candela impulse in unità di ATR
    touch_count: int
    fresh: bool
    tf_label: str


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

def _atr_series(bars: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = bars["high"], bars["low"], bars["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


# ---------------------------------------------------------------------------
# Base scan
# ---------------------------------------------------------------------------

def _scan_zones(
    bars: pd.DataFrame,
    atr: pd.Series,
    *,
    base_min: int,
    base_max: int,
    base_range_mult: float,
    impulse_mult: float,
    tf_label: str,
) -> list[SDZone]:
    """Single pass O(n × base_max) sui dati. Per ogni candidate base
    (intervallo [i, i+k)), verifica se la barra successiva è un impulse.
    """
    zones: list[SDZone] = []
    n = len(bars)
    highs = bars["high"].to_numpy()
    lows = bars["low"].to_numpy()
    opens = bars["open"].to_numpy()
    closes = bars["close"].to_numpy()

    for i in range(0, n - base_max - 1):
        # Salta finché ATR non è definito.
        if not np.isfinite(atr.iat[i + base_max]):
            continue
        for k in range(base_min, base_max + 1):
            end = i + k
            if end >= n:
                break
            atr_ref = float(atr.iat[end])
            if not np.isfinite(atr_ref) or atr_ref <= 0:
                continue
            # Base: ogni barra ha range < soglia + range totale < soglia.
            base_high = float(np.max(highs[i:end]))
            base_low = float(np.min(lows[i:end]))
            base_range = base_high - base_low
            if base_range >= base_range_mult * atr_ref:
                continue
            # Tutte le singole candele hanno range piccolo?
            max_single = float(np.max(highs[i:end] - lows[i:end]))
            if max_single >= base_range_mult * atr_ref:
                continue
            # Impulse: barra end deve essere grossa.
            imp_range = float(highs[end] - lows[end])
            if imp_range < impulse_mult * atr_ref:
                continue
            imp_body = float(closes[end] - opens[end])
            if abs(imp_body) < 0.5 * imp_range:
                # Body troppo piccolo (doji-like) — non un vero impulse.
                continue

            if imp_body > 0:
                # Bullish impulse → demand zone.
                zones.append(SDZone(
                    kind="demand",
                    proximal=base_high,
                    distal=base_low,
                    created_at=bars.index[end - 1],
                    base_size=k,
                    impulse_strength=imp_range / atr_ref,
                    touch_count=0,
                    fresh=True,
                    tf_label=tf_label,
                ))
            else:
                # Bearish impulse → supply zone.
                zones.append(SDZone(
                    kind="supply",
                    proximal=base_low,
                    distal=base_high,
                    created_at=bars.index[end - 1],
                    base_size=k,
                    impulse_strength=imp_range / atr_ref,
                    touch_count=0,
                    fresh=True,
                    tf_label=tf_label,
                ))
            break  # trovato il pattern partendo da i: skippa altri k

    return zones


# ---------------------------------------------------------------------------
# Touch counter
# ---------------------------------------------------------------------------

def _count_touches(
    bars: pd.DataFrame,
    zone: SDZone,
) -> int:
    """Conta quante volte il prezzo è entrato nella zona dopo la creazione.

    Un touch = una sequenza contigua di barre che entrano nella zona;
    barre consecutive nella zona contano come UN touch.
    """
    mask = bars.index > zone.created_at
    if not mask.any():
        return 0
    sub = bars.loc[mask]
    if zone.kind == "demand":
        lo_b, hi_b = zone.distal, zone.proximal
    else:
        lo_b, hi_b = zone.proximal, zone.distal

    in_zone = ((sub["low"] <= hi_b) & (sub["high"] >= lo_b)).to_numpy()
    # Conta le transizioni False→True.
    touches = 0
    prev = False
    for v in in_zone:
        if v and not prev:
            touches += 1
        prev = v
    return touches


def _is_zone_broken(
    bars: pd.DataFrame,
    zone: SDZone,
) -> bool:
    """Demand è "rotta" se close < distal; Supply se close > distal."""
    mask = bars.index > zone.created_at
    if not mask.any():
        return False
    closes = bars.loc[mask, "close"]
    if zone.kind == "demand":
        return bool((closes < zone.distal).any())
    return bool((closes > zone.distal).any())


# ---------------------------------------------------------------------------
# API pubblica
# ---------------------------------------------------------------------------

def detect_sd_zones(
    bars: pd.DataFrame,
    *,
    base_min_bars: int,
    base_max_bars: int,
    base_range_atr_mult: float,
    impulse_atr_mult: float,
    max_touches_for_valid: int,
    max_zones: int,
    max_age_days: int,
    tf_label: str = "",
    atr_period: int = 14,
) -> list[SDZone]:
    """Detect supply/demand zones.

    Args:
        bars: DataFrame OHLC.
        base_min_bars, base_max_bars: range del numero di barre di base.
        base_range_atr_mult: max ampiezza della base in unità ATR.
        impulse_atr_mult: min ampiezza dell'impulse in unità ATR.
        max_touches_for_valid: zone con più di N touch sono "esaurite".
        max_zones: cap sul numero di zone restituite (più fresh + più recenti).
        max_age_days: zone più vecchie di N giorni scartate.
        tf_label: etichetta TF da assegnare a ogni zona.

    Returns:
        Lista SDZone ordinata per (fresh desc, recency desc).
    """
    if len(bars) < base_max_bars + atr_period + 5:
        return []

    atr = _atr_series(bars, atr_period)
    zones = _scan_zones(
        bars,
        atr,
        base_min=base_min_bars,
        base_max=base_max_bars,
        base_range_mult=base_range_atr_mult,
        impulse_mult=impulse_atr_mult,
        tf_label=tf_label,
    )
    if not zones:
        return []

    # Filtra per età.
    last_bar = bars.index[-1]
    cutoff = last_bar - pd.Timedelta(days=max_age_days)
    zones = [z for z in zones if z.created_at >= cutoff]

    # Touch counting + break filter.
    surviving: list[SDZone] = []
    for z in zones:
        if _is_zone_broken(bars, z):
            continue
        z.touch_count = _count_touches(bars, z)
        z.fresh = z.touch_count <= max_touches_for_valid
        if z.fresh:
            surviving.append(z)

    surviving.sort(key=lambda z: (-int(z.fresh), -z.created_at.value, -z.impulse_strength))
    return surviving[:max_zones]
