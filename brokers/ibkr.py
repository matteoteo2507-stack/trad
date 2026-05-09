"""
Broker Interactive Brokers — STUB.

Implementazione completa in Stage 1 (Stock Selector → paper trading IBKR).

Libreria di riferimento: `ib_insync` (vedi pyproject.toml).

IBKR richiede TWS o IB Gateway in esecuzione localmente; la libreria si connette via socket
sulla porta configurata (default paper: 7497, live: 7496).
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from .base import BrokerBase, BrokerInfo, BrokerPosition, Order


class IBKRBroker(BrokerBase):
    name = "ibkr"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,
        client_id: int = 1,
        paper_mode: bool = True,
    ):
        super().__init__(paper_mode=paper_mode)
        self.host = host
        self.port = port
        self.client_id = client_id
        # TODO Stage 1: self.ib = IB()

    def connect(self) -> None:
        # TODO Stage 1: self.ib.connect(self.host, self.port, clientId=self.client_id)
        raise NotImplementedError("Implementazione in Stage 1")

    def disconnect(self) -> None:
        raise NotImplementedError("Implementazione in Stage 1")

    def get_info(self) -> BrokerInfo:
        raise NotImplementedError("Implementazione in Stage 1")

    def get_market_data(self, symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        raise NotImplementedError("Implementazione in Stage 1")

    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        raise NotImplementedError("Implementazione in Stage 1")

    def place_order(self, order: Order) -> str:
        raise NotImplementedError("Implementazione in Stage 1")

    def close_position(self, position: BrokerPosition) -> None:
        raise NotImplementedError("Implementazione in Stage 1")
