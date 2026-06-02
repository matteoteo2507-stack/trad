"""Trade journal del signal copier: log strutturato append-only (JSONL).

Sostituisce il Notion manuale: ogni evento del copier viene scritto come una
riga JSON in un file `.jsonl`. Zero attrito (il copier è full-auto), e i dati
sono direttamente analizzabili per ottimizzare il risk management e alimentare
`/quant-review`.

Cosa contiene (tutto il lato "segnale + risk management", ricavabile senza
broker):
- `signal_accepted` — segnale + le gambe pianificate (entry/SL/TP, lotti) e il
  R/R pianificato di ogni gamba (reward fino al suo TP / rischio allo SL).
- `signal_rejected` — segnale scartato dal planner + motivo.
- `update_tp_hit` / `update_close_all` / `update_all_tp` — eventi di gestione.

Cosa NON contiene: il PnL realizzato per gamba. I prezzi di fill stanno nello
storico MT5: la riconciliazione per ticket è un follow-up (`reconcile`), non
serve per iniziare a operare e raccogliere il grosso dei dati.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .models import ParsedSignal, SignalUpdate, TradePlan

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TradeJournal:
    """Scrive gli eventi del copier in un file JSONL (una riga per evento)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, record: dict[str, Any]) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            # Il journal non deve mai far cadere l'esecuzione di un trade.
            logger.warning("Scrittura journal fallita (%s): %s", self.path, exc)

    def log_signal(self, plan: TradePlan, mode: str) -> None:
        """Registra un piano: accettato (con gambe + R/R) o scartato (con motivo)."""
        sig = plan.signal
        risk = abs(sig.entry - sig.sl)
        record: dict[str, Any] = {
            "event": "signal_accepted" if plan.accepted else "signal_rejected",
            "ts": _now_iso(),
            "mode": mode,
            "channel": sig.channel,
            "symbol": sig.symbol,
            "side": sig.side,
            "entry": sig.entry,
            "sl": sig.sl,
            "tps": sig.tps,
            "reason": plan.reason,
        }
        if plan.accepted:
            record["total_lots"] = plan.total_size
            record["legs"] = [
                {
                    "tp_index": leg.tp_index,
                    "tp": leg.take_profit,
                    "size": leg.size,
                    "ticket": leg.ticket,
                    # R/R pianificato della gamba: reward al suo TP / rischio allo SL.
                    "rr": round(abs(leg.take_profit - sig.entry) / risk, 2) if risk else None,
                }
                for leg in plan.legs
            ]
        self._write(record)

    def log_reconcile(
        self, signal: ParsedSignal, plan: Optional[TradePlan], mode: str
    ) -> None:
        """Registra la riconciliazione dei livelli esatti (messaggio #3) sul trade aperto."""
        record: dict[str, Any] = {
            "event": "levels_reconciled" if plan is not None else "levels_no_trade",
            "ts": _now_iso(),
            "mode": mode,
            "channel": signal.channel,
            "symbol": signal.symbol,
            "side": signal.side,
            "entry": signal.entry,
            "sl": signal.sl,
            "tps": signal.tps,
            "tickets": [leg.ticket for leg in plan.legs] if plan is not None else None,
        }
        self._write(record)

    def log_update(
        self, update: SignalUpdate, plan: Optional[TradePlan], mode: str
    ) -> None:
        """Registra un evento di gestione (TP hit / close / all TP)."""
        sig = plan.signal if plan is not None else None
        record: dict[str, Any] = {
            "event": f"update_{update.kind}",
            "ts": _now_iso(),
            "mode": mode,
            "channel": update.channel,
            "symbol": sig.symbol if sig is not None else update.symbol,
            "tp_index": update.tp_index,
            "tickets": [leg.ticket for leg in plan.legs] if plan is not None else None,
        }
        self._write(record)
