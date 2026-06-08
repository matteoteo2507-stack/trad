"""Parser per canale GOLD a 5 TP (es. t.me/gfetyydh8959).

Sequenza dei messaggi:
1. "READY FOR GOLD SIGNAL" → heads-up, ignorato.
2. Segnale completo in UN messaggio (direzione + entry + 5 TP + SL), es.:

       GOLD BUY 4470//4466
       ✔️TP¹ 4474
       ✔️TP² 4478
       ✔️TP³ 4482
       ✔️TP⁴ 4486
       ✔️TP⁵ 4490
       🚫SL 4456

   → `entry_mode="signal"`: si apre a mercato direttamente (i livelli sono già qui,
   niente messaggio separato → niente trigger/riconciliazione).
3. Notifiche di TP raggiunto (nessun messaggio di chiusura).

Note:
- I TP usano apici Unicode (¹²³⁴⁵), non cifre ASCII → la regex cattura il numero
  che segue, ignorando l'apice.
- L'entry può essere una zona "4470//4466": prendiamo il primo valore come riferimento
  (l'apertura è comunque a mercato).
- SL fisso, sempre 5 TP (come da indicazioni del canale).
- Gestione TP→break-even: **attiva**. L'update "tp N hit" (richiede la parola HIT, non
  confondibile con la lista TP del segnale) sposta lo SL a BE sulle gambe residue.
- **Nessun messaggio di chiusura**: il canale si libera quando tutte le gambe risultano
  chiuse sul broker (`executor._all_legs_closed`), così i segnali successivi non restano bloccati.
"""

from __future__ import annotations

import re

from ..models import ParsedSignal, SignalUpdate
from .base import ChannelParser, ParseResult, register_parser

DEFAULT_SYMBOL = "XAUUSD"

_NUM = r"([0-9]+(?:\.[0-9]+)?)"
_RE_SIDE = re.compile(r"\b(BUY|SELL)\b", re.IGNORECASE)
# entry = primo numero dopo BUY/SELL (zona "4470//4466" → primo valore)
_RE_ENTRY = re.compile(r"\b(?:BUY|SELL)\b[^\d]*" + _NUM, re.IGNORECASE)
_RE_SL = re.compile(r"\bSL\b[^\d]*" + _NUM, re.IGNORECASE)
# "TP¹ 4474" / "TP1 4474": dopo "TP" salta apice/spazi (non-cifre) e cattura il prezzo.
_RE_TP = re.compile(r"TP[^\d\n]*?" + _NUM, re.IGNORECASE)
# Update "tp N hit" (es. "GOLD SELL tp 1 hit 40 pips running profit"): richiede la
# parola HIT → non confondibile con la lista TP del segnale (che non ha "hit").
_RE_TP_HIT = re.compile(r"\bTP\s*(\d+)\s*HIT\b", re.IGNORECASE)


class Gold5TpParser(ChannelParser):
    """Parser deterministico per il canale GOLD a 5 TP (segnale tutto-in-uno)."""

    channel_id = "gold_5tp"
    entry_mode = "signal"  # il messaggio coi livelli apre direttamente a mercato

    def parse(self, text: str) -> ParseResult:
        if not text:
            return None

        side_m = _RE_SIDE.search(text)
        entry_m = _RE_ENTRY.search(text)
        sl_m = _RE_SL.search(text)
        tps = [float(x) for x in _RE_TP.findall(text)]

        # Segnale completo: direzione + entry + SL + almeno un TP nello stesso messaggio.
        if side_m and entry_m and sl_m and tps:
            return ParsedSignal(
                symbol=DEFAULT_SYMBOL,
                side=side_m.group(1).upper(),
                entry=float(entry_m.group(1)),
                sl=float(sl_m.group(1)),
                tps=tps,
                channel=self.channel_id,
                raw=text,
            )

        # Update "tp N hit" (niente messaggio di chiusura su questo canale: il
        # rilascio del canale avviene quando le gambe risultano chiuse sul broker).
        hit = _RE_TP_HIT.search(text)
        if hit:
            return SignalUpdate(
                kind="tp_hit",
                channel=self.channel_id,
                tp_index=int(hit.group(1)),
                symbol=DEFAULT_SYMBOL,
                raw=text,
            )

        # Heads-up "READY FOR GOLD SIGNAL" e tutto il resto → ignorato.
        return None


register_parser(Gold5TpParser())
