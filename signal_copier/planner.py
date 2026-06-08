"""Planner: traduce un `ParsedSignal` in un `TradePlan` eseguibile.

Responsabilità:
- gate copia-segnali (whitelist, coerenza SL/TP, anti-ritardo),
- sizing: rischio totale del segnale splittato sulle N gambe (una per TP),
- arrotondamento al lot-step del broker.

Nota sul rischio: a differenza delle strategie meccaniche, qui NON applichiamo
`min_reward_to_risk` di `config/risk.yaml` — il R/R lo decide il mentore, noi
copiamo. Il R/R blended viene comunque calcolato e loggato per trasparenza.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Optional

from notifiers._pip_table import price_delta_pips, suggested_lots

from .models import EntryTrigger, ParsedSignal, TradeLeg, TradePlan

logger = logging.getLogger(__name__)


def _round_lot(lots: float, step: float, min_lot: float) -> float:
    """Arrotonda i lotti per difetto al lot-step, con floor a `min_lot`."""
    if step <= 0:
        return round(max(lots, min_lot), 2)
    rounded = math.floor(lots / step) * step
    if rounded < min_lot:
        return round(min_lot, 2)
    return round(rounded, 2)


def _valid_tps(signal: ParsedSignal) -> list[float]:
    """Filtra i TP coerenti con la direzione (oltre l'entry, lato giusto)."""
    if signal.side == "SELL":
        return [tp for tp in signal.tps if tp < signal.entry]
    return [tp for tp in signal.tps if tp > signal.entry]


def _sl_is_coherent(signal: ParsedSignal) -> bool:
    """Lo SL deve stare dal lato opposto ai TP rispetto all'entry."""
    if signal.side == "SELL":
        return signal.sl > signal.entry
    return signal.sl < signal.entry


def _reject(signal: ParsedSignal, reason: str) -> TradePlan:
    logger.warning("Segnale scartato [%s]: %s", signal.channel, reason)
    return TradePlan(signal=signal, legs=[], accepted=False, reason=reason)


def build_plan(
    signal: ParsedSignal,
    balance: float,
    config: dict[str, Any],
    current_price: Optional[float] = None,
) -> TradePlan:
    """Costruisce il piano di trade da un segnale parsato.

    Args:
        signal: segnale parsato dal canale.
        balance: equity dell'account (da broker in live, da hint in dry-run).
        config: sezione `copier` del config.yaml.
        current_price: prezzo corrente del simbolo, per il gate anti-ritardo.
            Se None, il gate anti-ritardo viene saltato (dry-run senza feed).
    """
    risk_cfg = config.get("risk", {})
    min_lot = float(config.get("min_lot", 0.01))
    lot_step = float(config.get("lot_step", 0.01))
    max_total_lots = float(config.get("max_total_lots", 1e9))

    # 1. Whitelist simboli.
    whitelist = config.get("symbols_whitelist") or []
    if whitelist and signal.symbol not in whitelist:
        return _reject(signal, f"simbolo {signal.symbol} non in whitelist")

    # 2. Coerenza SL.
    if not _sl_is_coherent(signal):
        return _reject(
            signal,
            f"SL incoerente con direzione {signal.side} "
            f"(entry={signal.entry}, sl={signal.sl})",
        )

    # 3. TP coerenti.
    tps = _valid_tps(signal)
    if not tps:
        return _reject(signal, "nessun TP coerente con la direzione")

    # 4. Gate anti-ritardo: se il prezzo si è già mosso troppo, non rincorriamo.
    anti = config.get("anti_late", {})
    if anti.get("enabled", True) and current_price is not None:
        max_slip = float(anti.get("max_slippage_pips", 20))
        slip = price_delta_pips(signal.symbol, signal.entry, current_price)
        if slip > max_slip:
            return _reject(
                signal,
                f"prezzo mosso {slip:.1f} pip dall'entry > {max_slip} (segnale tardivo)",
            )
        # Prezzo già oltre il primo TP → trade di fatto già concluso.
        first_tp = tps[0]
        already_done = (
            current_price <= first_tp if signal.side == "SELL" else current_price >= first_tp
        )
        if already_done:
            return _reject(signal, "prezzo già oltre TP1: segnale concluso")

    # 5. Sizing: rischio totale splittato sulle N gambe.
    risk_total_pct = float(risk_cfg.get("risk_per_signal_pct", 0.01))
    n = len(tps)
    risk_per_leg_pct = risk_total_pct / n

    legs: list[TradeLeg] = []
    for i, tp in enumerate(tps, start=1):
        raw_lots = suggested_lots(
            signal.symbol, balance, risk_per_leg_pct, signal.entry, signal.sl
        )
        lots = _round_lot(raw_lots, lot_step, min_lot)
        legs.append(
            TradeLeg(
                symbol=signal.symbol,
                direction=signal.direction,
                size=lots,
                stop_loss=signal.sl,
                take_profit=tp,
                tp_index=i,
                note=f"{signal.channel} TP{i}",
            )
        )

    total = sum(leg.size for leg in legs)
    if total > max_total_lots:
        return _reject(signal, f"lotti totali {total:.2f} > max_total_lots {max_total_lots}")

    # R/R blended (solo informativo): media reward gambe / rischio.
    risk_dist = abs(signal.entry - signal.sl)
    if risk_dist > 0:
        blended_rr = sum(abs(tp - signal.entry) for tp in tps) / n / risk_dist
        logger.info(
            "Piano %s %s: %d gambe, %.2f lotti tot, R/R blended %.2f",
            signal.symbol,
            signal.side,
            n,
            total,
            blended_rr,
        )

    return TradePlan(signal=signal, legs=legs, accepted=True, reason="ok")


def build_market_plan(
    trigger: EntryTrigger,
    current_price: float,
    balance: float,
    config: dict[str, Any],
) -> TradePlan:
    """Costruisce un piano a mercato da un trigger "NOW" (niente livelli nel messaggio).

    Il mentore entra a mercato adesso; noi facciamo lo stesso al `current_price`.
    Lo SL del canale è fisso (offset noto da config), i TP sono **provvisori** e
    verranno sovrascritti dai livelli esatti del messaggio successivo (riconciliazione).
    Sizing esatto perché la distanza SL è nota.
    """
    entry_cfg = config.get("entry", {})
    sl_distance = float(entry_cfg.get("sl_distance", 10.0))
    tp_offsets = [float(o) for o in entry_cfg.get("tp_offsets", [5.0, 10.0, 15.0])]

    entry = float(current_price)
    if trigger.side == "SELL":
        sl = entry + sl_distance
        tps = [entry - o for o in tp_offsets]
    else:
        sl = entry - sl_distance
        tps = [entry + o for o in tp_offsets]

    # Sintetizziamo un ParsedSignal e riusiamo build_plan (whitelist, sizing, gambe).
    # current_price=None → gate anti-ritardo OFF: siamo a mercato per definizione.
    synth = ParsedSignal(
        symbol=trigger.symbol,
        side=trigger.side,
        entry=entry,
        sl=sl,
        tps=tps,
        channel=trigger.channel,
        raw=trigger.raw,
    )
    plan = build_plan(synth, balance, config, current_price=None)
    if plan.accepted:
        for leg in plan.legs:
            leg.note = f"{trigger.channel}_TP{leg.tp_index}_NOW"
    return plan
