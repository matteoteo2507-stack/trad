"""
Broker Coinbase — STUB.

Implementazione completa in Stage 6 (crypto live integration via OctoBot).

Libreria di riferimento: `ccxt` (uniformata per tutti gli exchange crypto). Vedi pyproject.toml.

In Stage 6 valutare se usare ccxt direttamente o orchestrare OctoBot come executor.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from .base import BrokerBase, BrokerInfo, BrokerPosition, Order


class CoinbaseBroker(BrokerBase):
    name = "coinbase"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        paper_mode: bool = True,
    ):
        super().__init__(paper_mode=paper_mode)
        self.api_key = api_key
        self.api_secret = api_secret

    def connect(self) -> None:
        # TODO Stage 6: ccxt.coinbase({'apiKey': ..., 'secret': ...})
        raise NotImplementedError("Implementazione in Stage 6")

    def disconnect(self) -> None:
        raise NotImplementedError("Implementazione in Stage 6")

    def get_info(self) -> BrokerInfo:
        raise NotImplementedError("Implementazione in Stage 6")

    def get_market_data(self, symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        raise NotImplementedError("Implementazione in Stage 6")

    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        raise NotImplementedError("Implementazione in Stage 6")

    def place_order(self, order: Order) -> str:
        raise NotImplementedError("Implementazione in Stage 6")

    def close_position(self, position: BrokerPosition) -> None:
        raise NotImplementedError("Implementazione in Stage 6")
