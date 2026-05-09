"""Template per una nuova strategia meccanica.

Copia questa cartella in `strategies/<nome_strategia>/` e adatta:
1. Il nome della classe (es. `MiaStrategia`).
2. La logica di `should_enter` e `should_exit`.
3. `get_required_data` per dichiarare cosa serve dal data layer.

Il trading è MECCANICO: niente chiamate LLM dentro le decisioni.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from brokers.base import BrokerPosition
from strategies._base import DataRequirement, Signal, StrategyBase


class TemplateStrategy(StrategyBase):
    """Strategia di esempio. Sostituire la docstring con 2-3 righe sulla logica reale."""

    name = "template"

    def get_required_data(self) -> DataRequirement:
        return DataRequirement(
            symbols=self.config["symbols"],
            timeframe=self.config["timeframe"],
            lookback_bars=self.config["lookback_bars"],
            indicators=self.config["indicators"],
        )

    def should_enter(self, market_data: pd.DataFrame) -> Optional[Signal]:
        # TODO: implementare la logica di entrata.
        return None

    def should_exit(self, market_data: pd.DataFrame, position: BrokerPosition) -> bool:
        # Default: nessuna uscita anticipata. Solo SL/TP statici.
        return False
