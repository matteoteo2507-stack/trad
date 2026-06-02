"""Tipi dati del signal copier.

Tre livelli:
- `ParsedSignal` / `SignalUpdate`: output del parser (cosa ha detto il canale).
- `TradeLeg` / `TradePlan`: output del planner (cosa apriremo, già dimensionato).

Il parser produce *intent grezzo*; il planner lo traduce in un piano eseguibile
rispettando il rischio. L'executor consuma solo `TradePlan` / `SignalUpdate`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Output del parser
# ---------------------------------------------------------------------------


@dataclass
class ParsedSignal:
    """Segnale di ingresso estratto da un messaggio del canale."""

    symbol: str  # normalizzato, es. "XAUUSD"
    side: str  # "BUY" | "SELL"
    entry: float
    sl: float
    tps: list[float]  # in ordine: [TP1, TP2, TP3, ...]
    channel: str  # id del canale sorgente
    raw: str = ""  # messaggio originale (per audit/log)
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def direction(self) -> str:
        """Direzione in linguaggio broker: 'long' | 'short'."""
        return "long" if self.side.upper() == "BUY" else "short"


@dataclass
class EntryTrigger:
    """Trigger di ingresso "a mercato adesso" (es. "XAUUSD SELL NOW").

    Ha la **direzione** ma NON i livelli: il canale manda prima questo (è il
    momento in cui il mentore entra a mercato), poi ~1 min dopo il messaggio con
    entry/SL/TP. Apriamo a mercato su questo e riconciliamo i livelli dopo.
    """

    symbol: str
    side: str  # "BUY" | "SELL"
    channel: str
    raw: str = ""
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def direction(self) -> str:
        return "long" if self.side.upper() == "BUY" else "short"


@dataclass
class SignalUpdate:
    """Messaggio di gestione su un segnale già aperto.

    `kind`:
    - "tp_hit": un TP è stato raggiunto (`tp_index` 1-based, None se ignoto).
    - "all_tp": tutti i TP raggiunti.
    - "close_all": invito esplicito a chiudere ("Close your trades").
    """

    kind: str
    channel: str
    tp_index: Optional[int] = None
    symbol: Optional[str] = None
    raw: str = ""
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Output del planner
# ---------------------------------------------------------------------------


@dataclass
class TradeLeg:
    """Una delle posizioni in cui viene splittato il segnale (una per TP)."""

    symbol: str
    direction: str  # "long" | "short"
    size: float  # lotti
    stop_loss: float
    take_profit: float
    tp_index: int  # 1-based: a quale TP punta questa gamba
    note: str = ""
    ticket: Optional[int] = None  # ticket MT5 della gamba, valorizzato all'apertura live


@dataclass
class TradePlan:
    """Piano eseguibile derivato da un `ParsedSignal`.

    `accepted=False` significa che il risk gate ha scartato il segnale; in quel
    caso `legs` è vuota e `reason` spiega il motivo (pronto per log/notifica).
    """

    signal: ParsedSignal
    legs: list[TradeLeg] = field(default_factory=list)
    accepted: bool = True
    reason: str = "ok"

    @property
    def total_size(self) -> float:
        return round(sum(leg.size for leg in self.legs), 2)
