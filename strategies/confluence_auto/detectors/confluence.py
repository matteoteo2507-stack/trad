"""Orchestrator: combina output dei detector S/R, S/D, POC in livelli
"confluence-marked" pronti per il file `levels_auto.yaml`.

Logica di confluenza:

1. Raccoglie tutti i candidati di tipo {S/R, S/D, POC} per il simbolo.
2. Per ogni candidato S/R o S/D, cerca altri candidati di **natura diversa**
   entro `match_window_pips`. Es. un S/R cluster vicino a un POC weekly →
   confluenza S/R + POC.
3. Solo i livelli con **≥ min_detectors marker di natura diversa** vengono
   emessi (gli altri vengono scartati come "rumore singolo-detector").
4. Per ogni livello sopravvissuto: price = quello del detector "ancora"
   (di norma S/R che è il più strutturale), confluence list = unione dei
   marker, tipo = quello dell'ancora.

Marker confluence usati (coerenti con il vocabolario di
`confluence_levels/levels.yaml`):

- S/R: `SR_D1`, `SR_H4` (a seconda del TF).
- S/D: `SD_D1`, `SD_H4`.
- POC: `POC_weekly`, `POC_monthly`, `VAH_weekly`, `VAL_weekly`,
  `HVN`, `LVN`.

Tutti i livelli auto-generati hanno `id` con suffisso `-AUTO` per
distinguibilità nel runner e nelle notifiche Telegram.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import pandas as pd

from .poc import POCLevel
from .sd import SDZone
from .sr import SRLevel


@dataclass
class AutoLevel:
    """Livello auto-generato pronto per la serializzazione YAML."""

    id: str
    symbol: str
    price: float
    type: str                    # support|resistance|demand_zone|supply_zone|key_level
    confluence: list[str] = field(default_factory=list)
    bias: str = "long"           # long|short
    valid_until: date = field(default_factory=date.today)
    tp_target_price: float | None = None
    distal_price: float | None = None  # per S/D zones (commento ## nel yaml)


# ---------------------------------------------------------------------------
# Helpers di tipo conversion
# ---------------------------------------------------------------------------

def _sr_marker(tf_label: str) -> str:
    return f"SR_{tf_label}" if tf_label else "SR"


def _sd_marker(tf_label: str) -> str:
    return f"SD_{tf_label}" if tf_label else "SD"


def _poc_marker(level: POCLevel) -> str:
    if level.kind in ("POC", "VAH", "VAL"):
        return f"{level.kind}_{level.window_label}"
    return level.kind   # HVN / LVN


# ---------------------------------------------------------------------------
# Confluence matching
# ---------------------------------------------------------------------------

def _find_matches(
    anchor_price: float,
    others: list[tuple[float, str]],
    window: float,
) -> list[str]:
    """Ritorna i marker degli altri detector entro `window` da anchor."""
    return [marker for price, marker in others if abs(price - anchor_price) <= window]


# ---------------------------------------------------------------------------
# Pipeline pubblica
# ---------------------------------------------------------------------------

def merge_to_auto_levels(
    *,
    symbol: str,
    sr_d1: list[SRLevel],
    sr_h4: list[SRLevel],
    sd_d1: list[SDZone],
    sd_h4: list[SDZone],
    poc_weekly: list[POCLevel],
    poc_monthly: list[POCLevel],
    match_window_pips: float,
    pip_size: float,
    min_detectors: int,
    valid_for_days: int,
    tp_search_radius_atr: float = 3.0,
    atr_d1: float | None = None,
) -> list[AutoLevel]:
    """Combina i detector e produce la lista di livelli auto.

    Args:
        symbol: nome simbolo per gli ID.
        sr_*, sd_*, poc_*: output dei detector.
        match_window_pips: tolleranza in pip per match cross-detector.
        pip_size: dimensione del pip del simbolo.
        min_detectors: minimo numero di "nature diverse" per emettere il livello.
        valid_for_days: TTL del livello (giorni da oggi).
        tp_search_radius_atr: per il `tp_target_price`, cerca il prossimo
            livello strutturale entro N × ATR_D1 nella direzione del bias.
        atr_d1: ATR D1 corrente del simbolo (usato per tp search).

    Returns:
        Lista di AutoLevel ordinata per: tipo (S/D fresh > S/R > POC standalone),
        e all'interno per touch_count / freshness.
    """
    window = match_window_pips * pip_size
    today = date.today()
    valid_until = today + timedelta(days=valid_for_days)

    # Liste (price, marker) usate per il matching cross-detector.
    sr_d1_marks = [(L.price, _sr_marker("D1")) for L in sr_d1]
    sr_h4_marks = [(L.price, _sr_marker("H4")) for L in sr_h4]
    sd_d1_marks = [(z.proximal, _sd_marker("D1")) for z in sd_d1]
    sd_h4_marks = [(z.proximal, _sd_marker("H4")) for z in sd_h4]
    poc_marks = [(p.price, _poc_marker(p)) for p in (poc_weekly + poc_monthly)]

    all_marks_by_nature = {
        "SR_D1": sr_d1_marks,
        "SR_H4": sr_h4_marks,
        "SD_D1": sd_d1_marks,
        "SD_H4": sd_h4_marks,
        "POC": poc_marks,
    }

    # Per ogni candidato "ancora" (S/R o S/D), trova match in OGNI nature diversa.
    out: list[AutoLevel] = []

    def _build_level_from_anchor(
        *,
        anchor_id_prefix: str,
        anchor_idx: int,
        anchor_price: float,
        anchor_nature: str,
        anchor_marker: str,
        anchor_type: str,
        anchor_bias: str,
        distal: float | None,
    ) -> AutoLevel | None:
        markers = {anchor_marker}
        natures = {anchor_nature}
        for nat, marks in all_marks_by_nature.items():
            if nat == anchor_nature:
                continue
            matched = _find_matches(anchor_price, marks, window)
            if matched:
                markers.update(matched)
                natures.add(nat)
        if len(natures) < min_detectors:
            return None

        # TP target: cerca il prossimo livello "ancora" nella direzione del bias.
        tp = _find_tp_target(
            anchor_price=anchor_price,
            anchor_bias=anchor_bias,
            sr_levels=sr_d1 + sr_h4,
            sd_zones=sd_d1 + sd_h4,
            atr=atr_d1 if atr_d1 and atr_d1 > 0 else None,
            search_radius_atr=tp_search_radius_atr,
        )

        return AutoLevel(
            id=f"{symbol}-{today.strftime('%YW%V')}-{anchor_id_prefix}{anchor_idx}-AUTO",
            symbol=symbol,
            price=anchor_price,
            type=anchor_type,
            confluence=sorted(markers),
            bias=anchor_bias,
            valid_until=valid_until,
            tp_target_price=tp,
            distal_price=distal,
        )

    # --- Ancore S/R D1 ---
    for i, lvl in enumerate(sr_d1):
        is_resistance = lvl.kind == "high"
        out.append(_build_level_from_anchor(
            anchor_id_prefix="R" if is_resistance else "S",
            anchor_idx=i + 1,
            anchor_price=lvl.price,
            anchor_nature="SR_D1",
            anchor_marker="SR_D1",
            anchor_type="resistance" if is_resistance else "support",
            anchor_bias="short" if is_resistance else "long",
            distal=None,
        ))

    # --- Ancore S/R H4 ---
    for i, lvl in enumerate(sr_h4):
        is_resistance = lvl.kind == "high"
        out.append(_build_level_from_anchor(
            anchor_id_prefix="RH4-" if is_resistance else "SH4-",
            anchor_idx=i + 1,
            anchor_price=lvl.price,
            anchor_nature="SR_H4",
            anchor_marker="SR_H4",
            anchor_type="resistance" if is_resistance else "support",
            anchor_bias="short" if is_resistance else "long",
            distal=None,
        ))

    # --- Ancore S/D D1 ---
    for i, zone in enumerate(sd_d1):
        is_supply = zone.kind == "supply"
        out.append(_build_level_from_anchor(
            anchor_id_prefix="SP" if is_supply else "D",
            anchor_idx=i + 1,
            anchor_price=zone.proximal,
            anchor_nature="SD_D1",
            anchor_marker="SD_D1",
            anchor_type="supply_zone" if is_supply else "demand_zone",
            anchor_bias="short" if is_supply else "long",
            distal=zone.distal,
        ))

    # --- Ancore S/D H4 ---
    for i, zone in enumerate(sd_h4):
        is_supply = zone.kind == "supply"
        out.append(_build_level_from_anchor(
            anchor_id_prefix="SPH4-" if is_supply else "DH4-",
            anchor_idx=i + 1,
            anchor_price=zone.proximal,
            anchor_nature="SD_H4",
            anchor_marker="SD_H4",
            anchor_type="supply_zone" if is_supply else "demand_zone",
            anchor_bias="short" if is_supply else "long",
            distal=zone.distal,
        ))

    # Filtra None (ancore senza confluenza sufficiente).
    return [L for L in out if L is not None]


# ---------------------------------------------------------------------------
# TP target search
# ---------------------------------------------------------------------------

def _find_tp_target(
    *,
    anchor_price: float,
    anchor_bias: str,
    sr_levels: list[SRLevel],
    sd_zones: list[SDZone],
    atr: float | None,
    search_radius_atr: float,
) -> float | None:
    """Cerca il prossimo livello strutturale nella direzione del bias.

    - bias long: TP = prossimo S/R alto o S/D supply sopra `anchor_price`.
    - bias short: TP = prossimo S/R basso o S/D demand sotto `anchor_price`.

    Restituisce None se non trova nulla entro `search_radius_atr × ATR`.
    Senza TP, il loader scarta il livello → meglio None che valore inventato.
    """
    candidates: list[float] = []
    for L in sr_levels:
        candidates.append(L.price)
    for z in sd_zones:
        candidates.append(z.proximal)

    if not candidates:
        return None

    radius = atr * search_radius_atr if atr else float("inf")

    if anchor_bias == "long":
        higher = [c for c in candidates if c > anchor_price and c <= anchor_price + radius]
        if not higher:
            return None
        return min(higher)  # primo target
    else:
        lower = [c for c in candidates if c < anchor_price and c >= anchor_price - radius]
        if not lower:
            return None
        return max(lower)
