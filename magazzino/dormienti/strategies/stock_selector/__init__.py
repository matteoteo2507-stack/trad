"""Stock Selector — sistema V6.0 di selezione azionaria SP500.

Versione headless del notebook `algoritmo selezione azioni.ipynb`.

Le re-export sono pigre: importare il pacchetto non trascina yfinance/requests
(utile in test offline che usano solo `scoring`).
"""

from .scoring import MacroScenario, RRGStatus, SelectionResult, StockPick

__all__ = [
    "StockSelector",
    "run_selection",
    "SelectionResult",
    "StockPick",
    "MacroScenario",
    "RRGStatus",
]


def __getattr__(name):
    if name in {"StockSelector", "run_selection"}:
        from . import strategy

        return getattr(strategy, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
