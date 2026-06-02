"""Registry dei parser per-canale.

Importare i moduli concreti qui registra automaticamente i parser nel registry
(`base.register_parser` viene chiamato a import-time).
"""

from __future__ import annotations

from .base import ChannelParser, get_parser, register_parser, registered_channels

# Import dei parser concreti → side-effect di registrazione.
from . import xau_analysis_lab  # noqa: F401

__all__ = [
    "ChannelParser",
    "get_parser",
    "register_parser",
    "registered_channels",
]
