"""Registry centralizzato delle strategie disponibili.

Aggiungere qui ogni nuova strategia per renderla invocabile via `core.runner`.
Le import sono pigre: il registry stesso non trascina dipendenze pesanti.
"""

from __future__ import annotations

from typing import Callable

# nome → factory che importa e restituisce la classe strategy.
# Pigro per evitare import in cascata di MT5/ccxt.

_REGISTRY: dict[str, Callable[[], type]] = {}


def register(name: str, factory: Callable[[], type]) -> None:
    """Registra una strategia (factory pigra)."""
    _REGISTRY[name] = factory


def get_strategy_class(name: str) -> type:
    """Restituisce la classe strategy data il suo nome."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Strategia sconosciuta: '{name}'. "
            f"Disponibili: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]()


def available() -> list[str]:
    return sorted(_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Registrazioni built-in
# ---------------------------------------------------------------------------


def _confluence_factory() -> type:
    from strategies.confluence_levels.strategy import ConfluenceLevelsStrategy

    return ConfluenceLevelsStrategy


# London Breakout è stata migrata a Expert Advisor MQL5 (vedi `mql5/london_breakout.mq5`)
# nel pivot 2026-05-05. Niente più factory Python per quella strategia.

register("confluence_levels", _confluence_factory)
