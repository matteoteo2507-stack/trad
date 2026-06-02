"""Detector POC / VAH / VAL via Volume Profile rolling.

Volume Profile = istogramma del **volume scambiato per bin di prezzo**, su una
finestra temporale (settimanale o mensile).

- **POC** (Point of Control): bin col volume massimo.
- **VAH/VAL** (Value Area High/Low): estremi dell'intervallo che contiene
  `value_area_pct` (tipicamente 70%) del volume totale, costruito espandendo
  dal POC verso i bin adiacenti col volume più alto fino a raggiungere la
  percentuale target.
- **HVN** (High Volume Node): bin con volume >= hvn_threshold_pct × POC_volume,
  diversi dal POC stesso.
- **LVN** (Low Volume Node): bin con volume <= lvn_threshold_pct × POC_volume —
  zone di "vuoto", tipicamente target di breakout.

Approssimazione: il volume di ogni barra viene attribuito al **mid price**
(`(high+low)/2`). Versione più accurata usa TPO o distribuzione lineare sul
range della barra, ma per le finestre weekly/monthly su forex/XAU questa
approssimazione è già robusta.

Su forex spot MT5 si usa `tick_volume` come proxy del volume reale (vedi
TRADING_PRINCIPLES.md §7). Su yfinance forex il volume è zero → il modulo
ritorna lista vuota.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

LevelKind = Literal["POC", "VAH", "VAL", "HVN", "LVN"]


@dataclass
class POCLevel:
    price: float
    kind: LevelKind
    window_label: str          # "weekly", "monthly"
    volume_fraction: float     # bin_volume / total_volume, per ranking


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_histogram(
    bars: pd.DataFrame,
    n_bins: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Restituisce (bin_centers, bin_volumes).

    Bins lineari fra min(low) e max(high) della finestra. Ogni barra contribuisce
    `volume` interamente al bin del suo mid price.
    """
    lo = float(bars["low"].min())
    hi = float(bars["high"].max())
    if hi <= lo:
        return np.array([]), np.array([])

    edges = np.linspace(lo, hi, n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0

    mids = ((bars["high"] + bars["low"]) / 2.0).to_numpy()
    vols = bars["volume"].to_numpy(dtype=float)

    # np.digitize: bin index per ogni mid. -1 per gestire boundary.
    idx = np.clip(np.digitize(mids, edges) - 1, 0, n_bins - 1)
    volumes = np.zeros(n_bins, dtype=float)
    np.add.at(volumes, idx, vols)
    return centers, volumes


def _value_area(
    centers: np.ndarray,
    volumes: np.ndarray,
    pct: float,
) -> tuple[float, float]:
    """Calcola VAH/VAL espandendo dal POC verso i bin adiacenti col volume
    più alto, finché si raggiunge `pct` del volume totale.
    """
    total = volumes.sum()
    if total <= 0:
        return float("nan"), float("nan")
    target = pct * total
    poc_idx = int(np.argmax(volumes))
    lo_idx = poc_idx
    hi_idx = poc_idx
    accumulated = volumes[poc_idx]

    while accumulated < target:
        left_vol = volumes[lo_idx - 1] if lo_idx > 0 else -np.inf
        right_vol = volumes[hi_idx + 1] if hi_idx < len(volumes) - 1 else -np.inf
        if left_vol < 0 and right_vol < 0:
            break
        if right_vol > left_vol:
            hi_idx += 1
            accumulated += volumes[hi_idx]
        else:
            lo_idx -= 1
            accumulated += volumes[lo_idx]

    return float(centers[lo_idx]), float(centers[hi_idx])


# ---------------------------------------------------------------------------
# API pubblica
# ---------------------------------------------------------------------------

def detect_poc_levels(
    bars: pd.DataFrame,
    *,
    window_label: str,
    n_bins: int,
    value_area_pct: float,
    hvn_threshold_pct: float,
    lvn_threshold_pct: float,
) -> list[POCLevel]:
    """Volume Profile su `bars`. Le barre sono già state ritagliate alla
    finestra (weekly / monthly) prima della chiamata.

    Returns: POC + VAL + VAH + lista di HVN + lista di LVN.
    """
    if len(bars) < 5:
        return []
    if (bars["volume"] <= 0).all():
        # Volume degenerato (yfinance forex) → POC non significativo, skip.
        return []

    centers, volumes = _build_histogram(bars, n_bins)
    if centers.size == 0 or volumes.sum() <= 0:
        return []

    total = volumes.sum()
    poc_idx = int(np.argmax(volumes))
    poc_vol = volumes[poc_idx]
    val, vah = _value_area(centers, volumes, value_area_pct)

    out: list[POCLevel] = [
        POCLevel(
            price=float(centers[poc_idx]),
            kind="POC",
            window_label=window_label,
            volume_fraction=float(poc_vol / total),
        ),
        POCLevel(
            price=val,
            kind="VAL",
            window_label=window_label,
            volume_fraction=value_area_pct,
        ),
        POCLevel(
            price=vah,
            kind="VAH",
            window_label=window_label,
            volume_fraction=value_area_pct,
        ),
    ]

    # HVN: bin con volume >= hvn_threshold_pct × POC_vol, escluso POC stesso.
    hvn_mask = (volumes >= hvn_threshold_pct * poc_vol) & (np.arange(len(volumes)) != poc_idx)
    for i in np.where(hvn_mask)[0]:
        out.append(POCLevel(
            price=float(centers[i]),
            kind="HVN",
            window_label=window_label,
            volume_fraction=float(volumes[i] / total),
        ))

    # LVN: bin con volume <= lvn_threshold_pct × POC_vol, escludendo bin vuoti
    # (i bordi della distribuzione spesso hanno volume 0 e non sono significativi).
    nonzero_mask = volumes > 0
    lvn_mask = (volumes <= lvn_threshold_pct * poc_vol) & nonzero_mask
    for i in np.where(lvn_mask)[0]:
        out.append(POCLevel(
            price=float(centers[i]),
            kind="LVN",
            window_label=window_label,
            volume_fraction=float(volumes[i] / total),
        ))

    return out
