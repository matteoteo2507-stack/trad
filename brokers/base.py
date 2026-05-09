"""
Interfaccia astratta per tutti i broker.

Ogni broker concreto (IBKR, MT5, Coinbase, Binance) eredita da BrokerBase e implementa
i metodi astratti. Il sistema di trading parla solo con questa interfaccia, mai con
le API specifiche del broker.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class Order:
    """Ordine generico da piazzare sul broker."""

    symbol: str
    direction: str  # "long" | "short"
    size: float
    order_type: str = "market"  # "market" | "limit" | "stop"
    limit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    note: str = ""


@dataclass
class BrokerPosition:
    """Posizione corrente sul broker."""

    symbol: str
    direction: str
    size: float
    entry_price: float
    entry_time: datetime
    current_price: float
    unrealized_pnl: float
    sl: Optional[float]
    tp: Optional[float]


@dataclass
class BrokerInfo:
    """Info di base sull'account del broker."""

    name: str
    account_id: str
    currency: str
    balance: float
    equity: float
    is_paper: bool


class BrokerBase(ABC):
    """Classe base per tutti i broker."""

    name: str = "unnamed_broker"

    def __init__(self, paper_mode: bool = True):
        self.paper_mode = paper_mode
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """Apre la connessione al broker. Deve essere idempotente."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Chiude la connessione. Deve essere idempotente."""
        ...

    @abstractmethod
    def get_info(self) -> BrokerInfo:
        """Restituisce info account (balance, equity, currency, paper_mode)."""
        ...

    @abstractmethod
    def get_market_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int,
    ) -> pd.DataFrame:
        """Scarica dati OHLCV. DataFrame con colonne: ['open','high','low','close','volume']."""
        ...

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        """Restituisce la posizione corrente sul simbolo, o None se non esiste."""
        ...

    @abstractmethod
    def place_order(self, order: Order) -> str:
        """
        Piazza l'ordine. Restituisce l'ID univoco del broker.

        Se paper_mode=True, l'implementazione deve simulare l'ordine senza inviarlo davvero
        al mercato (oppure usare l'endpoint paper/demo del broker se disponibile).
        """
        ...

    @abstractmethod
    def close_position(self, position: BrokerPosition) -> None:
        """Chiude la posizione data."""
        ...

    def is_paper(self) -> bool:
        return self.paper_mode

    @property
    def connected(self) -> bool:
        return self._connected
