"""Tabella pip-size e decimali per simbolo.

Centralizzata qui per non hardcodare valori dentro il notifier o le strategie.
Le voci coprono i simboli usati in Stage 2 (forex maggiori, oro, BTC).
Espandibile aggiungendo righe.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipSpec:
    """Specifica formattazione, pip-size e tick-value per un simbolo."""

    decimals: int  # decimali per la stampa del prezzo
    pip_size: float  # frazione di prezzo che corrisponde a 1 pip
    # Valore in USD di 1 pip per 1 LOTTO STANDARD (100k unità per forex, 100 oz
    # per XAU, ecc.). Convenzione broker forex.
    # Forex maggiori XXX/USD: pip 0.0001 = $10/lot.
    # XAU: pip 0.10 = $10/lot (tick 0.01 = $1, quindi 1 pip = 10 tick = $10).
    # USDJPY: pip 0.01 = $9.09/lot circa al cambio attuale — approssimazione $10.
    pip_value_per_lot: float = 10.0


# Pattern → spec. Match per prefisso (case-insensitive). Più specifico vince.
_PIP_TABLE: dict[str, PipSpec] = {
    # Forex maggiori — 1 pip = $10/lot per coppie XXX/USD
    "EURUSD": PipSpec(decimals=5, pip_size=0.0001, pip_value_per_lot=10.0),
    "GBPUSD": PipSpec(decimals=5, pip_size=0.0001, pip_value_per_lot=10.0),
    "AUDUSD": PipSpec(decimals=5, pip_size=0.0001, pip_value_per_lot=10.0),
    "USDCAD": PipSpec(decimals=5, pip_size=0.0001, pip_value_per_lot=10.0),
    "USDCHF": PipSpec(decimals=5, pip_size=0.0001, pip_value_per_lot=10.0),
    # USDJPY: pip value varia col cambio, ~$9/lot al cambio attuale.
    # Per il sizing è approssimato a $10 — l'errore è < 10%.
    "USDJPY": PipSpec(decimals=3, pip_size=0.01, pip_value_per_lot=10.0),
    # Metalli — XAU: tick 0.01 = $1/lot → 1 pip (0.10) = $10/lot.
    "XAUUSD": PipSpec(decimals=2, pip_size=0.10, pip_value_per_lot=10.0),
    "XAGUSD": PipSpec(decimals=3, pip_size=0.001, pip_value_per_lot=5.0),
    # Indici (CFD AvaTrade) — pip value indicativo, da verificare col broker
    "US500": PipSpec(decimals=1, pip_size=0.1, pip_value_per_lot=1.0),
    "NAS100": PipSpec(decimals=1, pip_size=0.1, pip_value_per_lot=1.0),
    "GER40": PipSpec(decimals=1, pip_size=0.1, pip_value_per_lot=1.0),
    # Crypto (Stage 6)
    "BTCUSDT": PipSpec(decimals=2, pip_size=1.0, pip_value_per_lot=1.0),
    "BTC/USDT": PipSpec(decimals=2, pip_size=1.0, pip_value_per_lot=1.0),
    "ETHUSDT": PipSpec(decimals=2, pip_size=0.1, pip_value_per_lot=1.0),
    "ETH/USDT": PipSpec(decimals=2, pip_size=0.1, pip_value_per_lot=1.0),
}

_DEFAULT_SPEC = PipSpec(decimals=4, pip_size=0.0001, pip_value_per_lot=10.0)


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


def suggested_lots(
    symbol: str,
    account_balance: float,
    risk_pct: float,
    entry_price: float,
    sl_price: float,
) -> float:
    """Lottaggio per rischiare risk_pct del balance se SL viene colpito.

    Formula: lots = (balance * risk_pct) / (sl_distance_pips * pip_value_per_lot)

    Restituisce un float con 2 decimali (es. 0.05, 0.12, 1.00). Caller decide
    arrotondamento finale al lot-step del broker.
    """
    spec = get_pip_spec(symbol)
    sl_pips = price_delta_pips(symbol, entry_price, sl_price)
    if sl_pips <= 0:
        return 0.0
    risk_usd = account_balance * risk_pct
    lots = risk_usd / (sl_pips * spec.pip_value_per_lot)
    return round(lots, 2)
