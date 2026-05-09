"""
Interfaccia astratta per i backtester pluralistici.

Implementazioni concrete in Stage 3.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class BacktestConfig:
    """Configurazione di una run di backtest."""

    strategy_name: str
    symbols: list[str]
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10_000.0
    # Costi realistici per il broker target
    commission_pct: float = 0.0  # commissione %
    slippage_pct: float = 0.0  # slippage %


@dataclass
class BacktestReport:
    """Report normalizzato di una run di backtest. Stesse metriche per tutti i backtester."""

    backtester_name: str
    config: BacktestConfig

    # Metriche standard
    total_return: float
    cagr: float
    sharpe: float
    sortino: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    n_trades: int
    avg_trade: float
    max_consecutive_losses: int

    # Equity curve (per plot/diagnostica)
    equity_curve: pd.Series

    # Lista trade (per analisi dettagliata)
    trades: pd.DataFrame


class BacktesterBase(ABC):
    """Classe base per tutti i backtester."""

    name: str = "unnamed_backtester"

    @abstractmethod
    def run(self, strategy_path: str, config: BacktestConfig) -> BacktestReport:
        """
        Esegue la strategia indicata sul dataset definito da config.
        Restituisce un BacktestReport normalizzato.
        """
        ...
