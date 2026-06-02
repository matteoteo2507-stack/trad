"""Notifier Telegram — outbound only.

Usa `requests.Session` direttamente verso `api.telegram.org`. Non importa
`python-telegram-bot` (resta in pyproject per Stage 5 quando servirà polling
per comandi `/status` ecc.; in Stage 2 outbound è single-thread sincrono).

Template messaggio definito in `skills/telegram-notifier/SKILL.md`.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Optional

import requests

from .base import NotifierBase, TradingSignal
from ._pip_table import format_price, price_delta_pct, price_delta_pips

logger = logging.getLogger(__name__)

LOGS_DIR = Path(__file__).parent.parent / "logs"
TELEGRAM_LOG_FILE = LOGS_DIR / "telegram.log"

_BACKOFF_SECONDS = (1, 3, 9)


def _ensure_log_handler() -> None:
    """Aggancia il file handler dedicato al logger del modulo (idempotente)."""
    if any(
        isinstance(h, logging.FileHandler)
        and Path(getattr(h, "baseFilename", "")) == TELEGRAM_LOG_FILE
        for h in logger.handlers
    ):
        return
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(TELEGRAM_LOG_FILE, encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)


class TelegramNotifier(NotifierBase):
    """Invio messaggi Telegram via Bot API REST (HTTP POST sincroni)."""

    name = "telegram"

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
    ):
        self.bot_token = bot_token
        self.chat_id = str(chat_id)
        self.timeout = timeout
        self._session = session or requests.Session()
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
        _ensure_log_handler()

    # ---- API pubblica ABC -----------------------------------------------

    def send_signal(self, signal: TradingSignal) -> None:
        text = self._format_signal(signal)
        self._send(text)

    def send_message(self, text: str) -> None:
        self._send(text)

    def send_exit_alert(self, symbol: str, reason: str) -> None:
        text = (
            f"⚠️ EXIT {symbol}\n"
            f"Motivo: {reason}\n"
            f"Posizione da chiudere su {symbol}."
        )
        self._send(text)

    # ---- API pubblica extra (override default no-op di NotifierBase) ----

    def send_pending_order_alert(
        self,
        level: dict[str, Any],
        direction: str,
        symbol: str,
        sl: float,
        tp: float,
        rationale: str,
        suggested_lots: float | None = None,
    ) -> None:
        text = self._format_pending_alert(
            level, direction, symbol, sl, tp, rationale, suggested_lots
        )
        self._send(text)

    def send_execution_log(
        self,
        symbol: str,
        direction: str,
        fill_price: float,
        strategy_name: str,
    ) -> None:
        text = (
            f"✅ FILL {direction} {symbol}\n"
            f"Strategia: {strategy_name}\n"
            f"Prezzo eseguito: {format_price(symbol, fill_price)}"
        )
        self._send(text)

    # ---- Formatter ------------------------------------------------------

    @staticmethod
    def _format_signal(signal: TradingSignal) -> str:
        sym = signal.symbol
        emoji = "🟢" if signal.direction == "BUY" else "🔴"
        sl_pips = price_delta_pips(sym, signal.entry_price, signal.stop_loss)
        tp_pips = price_delta_pips(sym, signal.entry_price, signal.take_profit)
        sl_pct = price_delta_pct(signal.entry_price, signal.stop_loss)
        tp_pct = price_delta_pct(signal.entry_price, signal.take_profit)

        lines = [
            f"{emoji} {signal.direction} {sym}",
            f"Strategia: {signal.strategy_name}",
            f"Timeframe: {signal.timeframe}",
            "",
            f"📍 Entry: {format_price(sym, signal.entry_price)}",
            f"🛑 SL:    {format_price(sym, signal.stop_loss)}  ({sl_pips:.1f} pip / {sl_pct:+.2f}%)",
            f"🎯 TP:    {format_price(sym, signal.take_profit)}  ({tp_pips:.1f} pip / {tp_pct:+.2f}%)",
            "",
            f"💰 Size: {signal.size}",
            f"⏱  Validità: {signal.valid_minutes} min",
            "",
            f"Ratio R/R: {signal.rr_ratio:.2f}",
            f"Confidence: {signal.confidence}%",
        ]
        if signal.note:
            lines.append("")
            lines.append(signal.note)
        return "\n".join(lines)

    @staticmethod
    def _format_pending_alert(
        level: dict[str, Any],
        direction: str,
        symbol: str,
        sl: float,
        tp: float,
        rationale: str,
        suggested_lots: float | None = None,
    ) -> str:
        emoji = "🟢" if direction.upper() in ("BUY", "LONG") else "🔴"
        confluence = level.get("confluence", [])
        confluence_str = ", ".join(confluence) if confluence else "n/d"
        price = level["price"]

        sl_pips = price_delta_pips(symbol, price, sl)
        tp_pips = price_delta_pips(symbol, price, tp)
        rr = (abs(tp - price) / abs(price - sl)) if price != sl else 0.0

        lines = [
            f"{emoji} LIVELLO IN AVVICINAMENTO {symbol}",
            f"Bias: {direction.upper()}",
            f"Tipo livello: {level.get('type', 'n/d')}",
            f"Confluenza: {confluence_str}",
            "",
            f"📍 Livello: {format_price(symbol, price)}",
            f"🛑 SL:      {format_price(symbol, sl)}  ({sl_pips:.1f} pip)",
            f"🎯 TP:      {format_price(symbol, tp)}  ({tp_pips:.1f} pip)",
            f"Ratio R/R: {rr:.2f}",
        ]
        if suggested_lots is not None:
            lines.append(f"💰 Lotti suggeriti: {suggested_lots:.2f}")
        lines.append("")
        lines.append(rationale)
        return "\n".join(lines)

    # ---- HTTP -----------------------------------------------------------

    def _send(self, text: str) -> None:
        """POST sendMessage con retry esponenziale."""
        for attempt, backoff in enumerate(_BACKOFF_SECONDS, start=1):
            try:
                resp = self._session.post(
                    f"{self._base_url}/sendMessage",
                    data={"chat_id": self.chat_id, "text": text},
                    timeout=self.timeout,
                )
                if resp.status_code == 200 and resp.json().get("ok"):
                    logger.info(
                        "telegram OK chat=%s len=%d", self.chat_id, len(text)
                    )
                    return
                logger.warning(
                    "telegram tentativo %d non-ok: status=%s body=%s",
                    attempt,
                    resp.status_code,
                    resp.text[:200],
                )
            except Exception as exc:
                logger.warning("telegram tentativo %d errore: %s", attempt, exc)

            time.sleep(backoff)

        logger.error(
            "telegram fallimento dopo %d tentativi", len(_BACKOFF_SECONDS)
        )
