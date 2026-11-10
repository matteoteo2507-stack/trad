"""Interfaccia astratta per i notifier (canali di notifica verso l'utente)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TradingSignal:
    """Signal di trading da notificare."""

    symbol: str
    direction: str  # "BUY" | "SELL"
    strategy_name: str
    timeframe: str
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float
    confidence: int  # 0-100
    rr_ratio: float
    note: str = ""
    valid_minutes: int = 60


class NotifierBase(ABC):
    """Classe base per tutti i notifier."""

    name: str = "unnamed_notifier"

    @abstractmethod
    def send_signal(self, signal: TradingSignal) -> None:
        """Invia un signal di trading formattato."""
        ...

    @abstractmethod
    def send_message(self, text: str) -> None:
        """Invia un messaggio testuale arbitrario."""
        ...

    @abstractmethod
    def send_exit_alert(self, symbol: str, reason: str) -> None:
        """Invia alert di uscita anticipata su una posizione."""
        ...

    # Default no-op: i notifier futuri possono ignorarli senza rompere nulla.
    # Le strategie che li chiamano hanno comunque il fallback più verboso via send_signal.

    def send_pending_order_alert(
        self,
        level: dict[str, Any],
        direction: str,
        symbol: str,
        sl: float,
        tp: float,
        rationale: str,
        suggested_lots: float | None = None,
    ) -> None:
        """Notifica di prossimità a un livello (Confluence)."""
        return None

    def send_execution_log(
        self,
        symbol: str,
        direction: str,
        fill_price: float,
        strategy_name: str,
    ) -> None:
        """Log post-esecuzione (strategie automatiche)."""
        return None
