"""Fondazione condivisa per tutte le strategie meccaniche.

Centralizza i tipi `Signal`, `DataRequirement`, `PositionUpdate` e la classe
astratta `StrategyBase`. Le sottoclassi importano da qui invece di ridefinire
le dataclass localmente.

Adapter espliciti `Signal.to_trading_signal` e `Signal.to_order` traducono il
linguaggio interno della strategia ("long"/"short") verso quello del notifier
("BUY"/"SELL") e del broker (`Order` con `direction`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import yaml

from brokers.base import BrokerPosition, Order
from notifiers.base import TradingSignal


# ---------------------------------------------------------------------------
# Tipi condivisi
# ---------------------------------------------------------------------------


@dataclass
class Signal:
    """Segnale prodotto dalla strategia. È *intent*, non esecuzione."""

    direction: str  # "long" | "short"
    size: float
    sl: float
    tp: float
    confidence: int = 50  # 0-100
    note: str = ""

    def reward_to_risk(self, entry_price: float) -> float:
        """Calcola il rapporto reward/risk dato il prezzo di entrata."""
        risk = abs(entry_price - self.sl)
        if risk == 0:
            return 0.0
        reward = abs(self.tp - entry_price)
        return reward / risk

    def to_trading_signal(
        self,
        symbol: str,
        strategy_name: str,
        timeframe: str,
        current_price: float,
        valid_minutes: int = 60,
    ) -> TradingSignal:
        """Converte il signal interno nel formato del notifier (BUY/SELL)."""
        direction_ext = "BUY" if self.direction == "long" else "SELL"
        return TradingSignal(
            symbol=symbol,
            direction=direction_ext,
            strategy_name=strategy_name,
            timeframe=timeframe,
            entry_price=current_price,
            stop_loss=self.sl,
            take_profit=self.tp,
            size=self.size,
            confidence=self.confidence,
            rr_ratio=self.reward_to_risk(current_price),
            note=self.note,
            valid_minutes=valid_minutes,
        )

    def to_order(
        self,
        symbol: str,
        order_type: str = "market",
        limit_price: Optional[float] = None,
    ) -> Order:
        """Converte il signal in un Order broker-agnostico."""
        return Order(
            symbol=symbol,
            direction=self.direction,
            size=self.size,
            order_type=order_type,
            limit_price=limit_price,
            stop_loss=self.sl,
            take_profit=self.tp,
            note=self.note,
        )


@dataclass
class DataRequirement:
    """Cosa serve alla strategia dal data layer."""

    symbols: list[str]
    timeframe: str
    lookback_bars: int
    indicators: list[str] = field(default_factory=list)


@dataclass
class PositionUpdate:
    """Modifica di una posizione esistente (es. SL→BE).

    `manage_position` restituisce questo o `None`. Spostare lo SL non è uscita,
    è modifica della posizione: per questo non passa da `should_exit`.
    """

    new_sl: Optional[float] = None
    new_tp: Optional[float] = None


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class StrategyBase(ABC):
    """Interfaccia comune per tutte le strategie meccaniche."""

    name: str = "unnamed_strategy"

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: dict = yaml.safe_load(f)

    @abstractmethod
    def get_required_data(self) -> DataRequirement:
        """Dichiara cosa serve dal data layer."""
        ...

    @abstractmethod
    def should_enter(self, market_data: pd.DataFrame) -> Optional[Signal]:
        """Valuta condizioni di entrata. Restituisce Signal o None."""
        ...

    @abstractmethod
    def should_exit(self, market_data: pd.DataFrame, position: BrokerPosition) -> bool:
        """Valuta condizioni di uscita anticipata oltre SL/TP."""
        ...

    def manage_position(
        self,
        market_data: pd.DataFrame,
        position: BrokerPosition,
    ) -> Optional[PositionUpdate]:
        """Eventuale modifica della posizione (SL/TP). Default: nessuna modifica."""
        return None
