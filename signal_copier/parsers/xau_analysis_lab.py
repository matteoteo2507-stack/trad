"""Parser per il canale "XAU/USD ANALYSIS TEAM" (t.me/XAUUSD_AnalysisLab).

Formato del segnale di ingresso (un messaggio):

    📉 XAUUSD SELL Signal (Gold)
    ✅ Entry: 4536
    🎯 Target
    - TP1: 4531
    - TP2: 4526
    - TP3: 4521
    🛑 Stop Loss: 4546

Messaggi di gestione (separati, e non sempre tutti inviati):
- "TP1 SUCCESSFUL ... 50 PIPS PROFIT RUNNING"  → tp_hit(1)  [sempre inviato]
- "TP2 SUCCESSFUL ..."                          → tp_hit(2)  [spesso omesso]
- "All TP SUCCESSFUL ..."                       → all_tp     [solo se tutti hit]
- "Close your trades and book profit 🚫"        → close_all  [non sempre]

Strategia di robustezza: TP/SL vengono armati sul broker all'apertura, quindi
gli update mancanti (es. TP2) NON compromettono la gestione. L'unico update che
ci serve davvero è tp_hit(1) → sposta SL a break-even, e close_all → flatten.

Canale mono-simbolo: gli update non contengono il simbolo, lo ereditano dal
`DEFAULT_SYMBOL`.
"""

from __future__ import annotations

import re

from ..models import EntryTrigger, ParsedSignal, SignalUpdate
from .base import ChannelParser, ParseResult, register_parser

DEFAULT_SYMBOL = "XAUUSD"

# Numero decimale generico (interi o con virgola decimale "."): 4536, 4531.5
_NUM = r"([0-9]+(?:\.[0-9]+)?)"

_RE_SIDE = re.compile(r"\b(BUY|SELL)\b", re.IGNORECASE)
_RE_SYMBOL = re.compile(r"\b(XAU\s*/?\s*USD|GOLD)\b", re.IGNORECASE)
_RE_ENTRY = re.compile(r"Entry\s*[:=]?\s*" + _NUM, re.IGNORECASE)
_RE_SL = re.compile(r"Stop\s*Loss\s*[:=]?\s*" + _NUM, re.IGNORECASE)
_RE_TP = re.compile(r"TP\s*\d+\s*[:=]?\s*" + _NUM, re.IGNORECASE)

# Trigger di ingresso a mercato: "XAUUSD SELL NOW" / "BUY NOW" (niente livelli).
_RE_NOW = re.compile(r"\b(BUY|SELL)\s+NOW\b", re.IGNORECASE)

_RE_ALL_TP = re.compile(r"\bALL\s+TP\b", re.IGNORECASE)
_RE_TP_HIT = re.compile(r"\bTP\s*(\d)\b[^\n]*\bSUCCESS", re.IGNORECASE)
_RE_CLOSE = re.compile(r"close\s+your\s+trade|book\s+profit", re.IGNORECASE)


class XauAnalysisLabParser(ChannelParser):
    """Parser deterministico per XAU/USD ANALYSIS TEAM."""

    channel_id = "xauusd_analysislab"
    entry_mode = "trigger"  # "NOW" apre, messaggio coi livelli riconcilia

    def parse(self, text: str) -> ParseResult:
        if not text:
            return None

        # 1. Nuovo segnale: deve avere Entry + Stop Loss + almeno un TP.
        entry_m = _RE_ENTRY.search(text)
        sl_m = _RE_SL.search(text)
        tps = [float(x) for x in _RE_TP.findall(text)]
        if entry_m and sl_m and tps:
            side_m = _RE_SIDE.search(text)
            if side_m is None:
                # senza direzione esplicita non eseguiamo: troppo rischioso.
                return None
            return ParsedSignal(
                symbol=DEFAULT_SYMBOL,
                side=side_m.group(1).upper(),
                entry=float(entry_m.group(1)),
                sl=float(sl_m.group(1)),
                tps=tps,
                channel=self.channel_id,
                raw=text,
            )

        # 2. Trigger di ingresso a mercato ("SELL NOW"/"BUY NOW"): direzione, no livelli.
        #    Deve venire DOPO il blocco segnale-con-livelli (che non contiene "NOW").
        now_m = _RE_NOW.search(text)
        if now_m:
            return EntryTrigger(
                symbol=DEFAULT_SYMBOL,
                side=now_m.group(1).upper(),
                channel=self.channel_id,
                raw=text,
            )

        # 3. Update di gestione.
        if _RE_ALL_TP.search(text):
            return SignalUpdate(
                kind="all_tp", channel=self.channel_id, symbol=DEFAULT_SYMBOL, raw=text
            )
        hit = _RE_TP_HIT.search(text)
        if hit:
            return SignalUpdate(
                kind="tp_hit",
                channel=self.channel_id,
                tp_index=int(hit.group(1)),
                symbol=DEFAULT_SYMBOL,
                raw=text,
            )
        if _RE_CLOSE.search(text):
            return SignalUpdate(
                kind="close_all", channel=self.channel_id, symbol=DEFAULT_SYMBOL, raw=text
            )

        # 4. Tutto il resto (promo, sticker, saluti) → ignorato.
        return None


register_parser(XauAnalysisLabParser())
