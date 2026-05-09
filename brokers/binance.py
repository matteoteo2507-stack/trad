"""
Broker Binance — STUB.

Implementazione completa in Stage 6 (crypto live integration).

Libreria di riferimento: `ccxt` (compatibile con Binance spot e futures).

Binance ha anche endpoint **testnet** per fare paper trading reale prima di passare al live.
In Stage 6, di default usare il testnet via `paper_mode=True`.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from .base import BrokerBase, BrokerInfo, BrokerPosition, Order


class BinanceBroker(BrokerBase):
    name = "binance"

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
        # TODO Stage 6: ccxt.binance({'apiKey': ..., 'secret': ..., 'options': {'defaultType': 'spot'}})
        # Se paper_mode -> usare testnet endpoint (sandbox)
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
