"""Runner della strategia Confluence Levels (post-pivot 2026-05-05).

Polling continuo: per ogni simbolo configurato chiede il prezzo corrente al
data source (yfinance/MT5), valuta tutti i livelli, manda notifiche Telegram
sulla prossimità.

**SOLO NOTIFICA**: la Confluence è umano-centrica per design dell'utente.
Non piazza ordini. Niente risk gate (non ha senso senza esecuzione). Niente
gestione posizioni o BE management.

Stato persistente:
- `data/notifications_sent.json` — chiavi `levelId|YYYY-MM-DD` già notificate
  per evitare duplicati al riavvio.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from brokers.base import BrokerBase
from notifiers.base import NotifierBase

from .news_filter import is_blocked as news_is_blocked
from .strategy import ConfluenceLevelsStrategy, LevelEvaluation


HEARTBEAT_INTERVAL_SECONDS = 15 * 60  # log riassuntivo ogni 15 minuti

logger = logging.getLogger(__name__)


@dataclass
class PersistentState:
    """Stato runtime persistito su disco per sopravvivere ai riavvii."""

    notifications_sent: set[str]


def _load_state(state_dir: Path) -> PersistentState:
    notif_path = state_dir / "notifications_sent.json"
    notif: set[str] = set()
    if notif_path.exists():
        try:
            notif = set(json.loads(notif_path.read_text(encoding="utf-8")))
        except Exception as exc:
            logger.warning("notifications_sent corrotto, reset: %s", exc)
    return PersistentState(notifications_sent=notif)


def _save_state(state: PersistentState, state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "notifications_sent.json").write_text(
        json.dumps(sorted(state.notifications_sent)), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


class ConfluenceRunner:
    """Polling-driven, gestisce un simbolo o più simboli sequenzialmente."""

    def __init__(
        self,
        strategy: ConfluenceLevelsStrategy,
        broker: BrokerBase,
        notifier: NotifierBase,
        risk_config: Optional[dict[str, Any]] = None,
        state_dir: Optional[Path] = None,
    ):
        self.strategy = strategy
        self.broker = broker
        self.notifier = notifier
        # `risk_config` è accettato per compatibilità con eventuali wrapper, ma
        # non viene usato: la Confluence è solo notifica.
        self.risk_config = risk_config or {}
        self.state_dir = (
            state_dir
            if state_dir is not None
            else Path(strategy.config.get("state_dir", "data"))
        )
        self.state = _load_state(self.state_dir)
        # Heartbeat: ultimo timestamp di log riassuntivo per simbolo.
        self._last_heartbeat: dict[str, datetime] = {}

    # ---- Loop principale ------------------------------------------------

    def run_forever(self) -> None:
        """Polling loop. Bloccante. Interrompibile con Ctrl-C."""
        interval = int(self.strategy.config.get("poll_interval_seconds", 60))
        logger.info(
            "Confluence runner avviato. Intervallo=%ss simboli=%s",
            interval,
            self.strategy.config.get("symbols"),
        )
        try:
            while True:
                try:
                    self.run_once()
                except Exception as exc:
                    logger.exception("Errore nel ciclo: %s", exc)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Confluence runner interrotto da utente.")

    def run_once(self, now: Optional[datetime] = None) -> list[LevelEvaluation]:
        """Una passata su tutti i simboli. Restituisce le valutazioni per dry-run/test."""
        now = now or datetime.now(timezone.utc)
        symbols = list(self.strategy.config.get("symbols") or [])
        all_evaluations: list[LevelEvaluation] = []

        for symbol in symbols:
            try:
                price = self._fetch_current_price(symbol)
            except Exception as exc:
                logger.warning("Skip %s: %s", symbol, exc)
                continue
            if price is None:
                continue

            news_blocked, news_reason = news_is_blocked(
                symbol=symbol,
                now=now,
                block_minutes=int(self.strategy.config.get("news_block_minutes", 30)),
            )
            if news_blocked:
                logger.info("News block su %s: %s", symbol, news_reason)

            evaluations = self.strategy.evaluate_symbol(
                symbol=symbol,
                current_price=price,
                now=now,
                news_blocked=news_blocked,
                already_notified_ids=self.state.notifications_sent,
            )
            all_evaluations.extend(evaluations)

            for ev in evaluations:
                if not ev.passed:
                    logger.debug("%s %s skip: %s", symbol, ev.level.id, ev.reason)
                    continue
                self._send_proximity_alert(ev, now=now)

            self._maybe_log_heartbeat(symbol, price, evaluations, now)

        _save_state(self.state, self.state_dir)
        return all_evaluations

    # ---- Handler unico --------------------------------------------------

    def _send_proximity_alert(self, ev: LevelEvaluation, now: datetime) -> None:
        """Notifica Telegram sulla prossimità del prezzo a un livello."""
        if ev.signal is None:
            return
        payload = self.strategy.get_pending_order_payload(ev)
        try:
            self.notifier.send_pending_order_alert(**payload)
        except Exception as exc:
            logger.exception("Errore invio notifica: %s", exc)
            return
        key = self.strategy.notif_key(ev.level, now)
        self.state.notifications_sent.add(key)

    # ---- Heartbeat ------------------------------------------------------

    def _maybe_log_heartbeat(
        self,
        symbol: str,
        price: float,
        evaluations: list[LevelEvaluation],
        now: datetime,
    ) -> None:
        """Log INFO ogni HEARTBEAT_INTERVAL_SECONDS con prezzo + livello più vicino.

        Serve a distinguere "runner sano ma niente entro proximity" da "runner
        bloccato/silenzioso per bug". Senza questo, tra una notifica e l'altra
        non c'è traccia che il runner stia osservando il prezzo.
        """
        last = self._last_heartbeat.get(symbol)
        if last is not None and (now - last).total_seconds() < HEARTBEAT_INTERVAL_SECONDS:
            return
        self._last_heartbeat[symbol] = now

        if not evaluations:
            logger.info("[heartbeat] %s price=%s nessun livello attivo", symbol, price)
            return

        nearest = min(evaluations, key=lambda e: e.distance_pips)
        logger.info(
            "[heartbeat] %s price=%s nearest=%s @%.2f dist=%.1f pip (%s)",
            symbol,
            price,
            nearest.level.id,
            nearest.level.price,
            nearest.distance_pips,
            "PASS" if nearest.passed else nearest.reason,
        )

    # ---- Helper ---------------------------------------------------------

    def _fetch_current_price(self, symbol: str) -> Optional[float]:
        """Ultimo close dalla candela corrente del timeframe configurato."""
        timeframe = self.strategy.config.get("timeframe", "M15")
        df = self.broker.get_market_data(symbol=symbol, timeframe=timeframe, bars=2)
        if df.empty:
            return None
        return float(df["close"].iloc[-1])
