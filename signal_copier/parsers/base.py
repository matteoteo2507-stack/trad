"""Interfaccia dei parser per-canale e registry.

Ogni canale Telegram ha un formato proprio: una sottoclasse di `ChannelParser`
incapsula le regex/regole di quel canale e restituisce `ParsedSignal`,
`SignalUpdate` o `None` (messaggio irrilevante: promo, sticker, saluti).

I parser sono deterministici di proposito: in un percorso che apre ordini reali
non vogliamo un LLM che "interpreta" e ogni tanto allucina un prezzo.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

from ..models import EntryTrigger, ParsedSignal, SignalUpdate

ParseResult = Union[ParsedSignal, EntryTrigger, SignalUpdate, None]


class ChannelParser(ABC):
    """Base per i parser di un singolo canale."""

    channel_id: str = "unnamed_channel"

    @abstractmethod
    def parse(self, text: str) -> ParseResult:
        """Interpreta un messaggio testuale del canale.

        Restituisce `ParsedSignal` (nuovo segnale), `SignalUpdate` (gestione di
        un segnale aperto) oppure `None` se il messaggio non è rilevante.
        """
        ...


# Registry: channel_id → istanza parser. Popolato dai moduli concreti via
# `register_parser`. Il reader sceglie il parser in base al canale sorgente.
_REGISTRY: dict[str, ChannelParser] = {}


def register_parser(parser: ChannelParser) -> ChannelParser:
    """Registra un parser nel registry globale (idempotente per channel_id)."""
    _REGISTRY[parser.channel_id] = parser
    return parser


def get_parser(channel_id: str) -> Optional[ChannelParser]:
    """Restituisce il parser per il canale, o None se non registrato."""
    return _REGISTRY.get(channel_id)


def registered_channels() -> list[str]:
    """Elenco dei canali con un parser registrato."""
    return sorted(_REGISTRY.keys())
