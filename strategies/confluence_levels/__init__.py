"""Confluence Levels Trader — strategia semiautomatica MT5/Telegram.

Vedi `strategies/confluence_levels/README.md` e `skills/strategy-designer/SKILL.md`.

Le re-export sono pigre: importare il pacchetto non trascina dipendenze pesanti
come MetaTrader5/requests (utile per i moduli puri come `levels_loader`).
"""

__all__ = ["ConfluenceLevelsStrategy"]


def __getattr__(name):
    if name == "ConfluenceLevelsStrategy":
        from .strategy import ConfluenceLevelsStrategy

        return ConfluenceLevelsStrategy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
