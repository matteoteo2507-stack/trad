"""Tabella pip-size e decimali per simbolo.

Centralizzata qui per non hardcodare valori dentro il notifier o le strategie.
Le voci coprono i simboli usati in Stage 2 (forex maggiori, oro, BTC).
Espandibile aggiungendo righe.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipSpec:
    """Specifica formattazione e pip-size per un simbolo."""

    decimals: int  # decimali per la stampa del prezzo
    pip_size: float  # frazione di prezzo che corrisponde a 1 pip


# Pattern → spec. Match per prefisso (case-insensitive). Più specifico vince.
_PIP_TABLE: dict[str, PipSpec] = {
    # Forex maggiori
    "EURUSD": PipSpec(decimals=5, pip_size=0.0001),
    "GBPUSD": PipSpec(decimals=5, pip_size=0.0001),
    "AUDUSD": PipSpec(decimals=5, pip_size=0.0001),
    "USDCAD": PipSpec(decimals=5, pip_size=0.0001),
    "USDCHF": PipSpec(decimals=5, pip_size=0.0001),
    "USDJPY": PipSpec(decimals=3, pip_size=0.01),
    # Metalli — convenzione: 1 pip XAU = $0.10 (= 10 tick broker da 0.01)
    "XAUUSD": PipSpec(decimals=2, pip_size=0.10),
    "XAGUSD": PipSpec(decimals=3, pip_size=0.001),
    # Indici (CFD AvaTrade)
    "US500": PipSpec(decimals=1, pip_size=0.1),
    "NAS100": PipSpec(decimals=1, pip_size=0.1),
    "GER40": PipSpec(decimals=1, pip_size=0.1),
    # Crypto (Stage 6)
    "BTCUSDT": PipSpec(decimals=2, pip_size=1.0),
    "BTC/USDT": PipSpec(decimals=2, pip_size=1.0),
    "ETHUSDT": PipSpec(decimals=2, pip_size=0.1),
    "ETH/USDT": PipSpec(decimals=2, pip_size=0.1),
}

_DEFAULT_SPEC = PipSpec(decimals=4, pip_size=0.0001)


def _normalize(symbol: str) -> str:
    """Normalizza varianti del simbolo (es. EURUSD.r → EURUSD)."""
    return symbol.upper().split(".")[0]


def get_pip_spec(symbol: str) -> PipSpec:
    """Restituisce la `PipSpec` per il simbolo, fallback al default."""
    norm = _normalize(symbol)
    if norm in _PIP_TABLE:
        return _PIP_TABLE[norm]
    return _DEFAULT_SPEC


def format_price(symbol: str, price: float) -> str:
    """Formatta il prezzo con i decimali corretti per il simbolo."""
    spec = get_pip_spec(symbol)
    return f"{price:.{spec.decimals}f}"


def price_delta_pips(symbol: str, p1: float, p2: float) -> float:
    """Differenza |p1 - p2| espressa in pip per il simbolo dato."""
    spec = get_pip_spec(symbol)
    return abs(p1 - p2) / spec.pip_size


def price_delta_pct(p_ref: float, p: float) -> float:
    """Variazione percentuale (p - p_ref)/p_ref espressa in % (es. 1.5 per 1.5%)."""
    if p_ref == 0:
        return 0.0
    return (p - p_ref) / p_ref * 100
