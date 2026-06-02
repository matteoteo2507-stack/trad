"""Executor: consuma `TradePlan` e `SignalUpdate` e agisce.

Due modalità:
- "dry_run" (default): logga il piano e gli update senza inviare nulla. È il
  percorso usato per validare il parsing sui messaggi reali prima del live.
- "live": apre le gambe su MT5 via `brokers.mt5.MT5Broker`.

Gestione update:
- tp_hit(1) → sposta SL a break-even sulle gambe residue.
- close_all → chiude ciò che resta a mercato.
- all_tp     → no-op (i TP erano armati sul broker, le gambe si sono chiuse da sé).

NB gestione live multi-gamba: su account HEDGING le N gambe sono posizioni
distinte, ciascuna col proprio ticket. Il ticket viene catturato all'apertura
(`TradeLeg.ticket`) e usato per il management per-ticket: SL→BE e flatten
agiscono sulla singola gamba via `MT5Broker.modify_position_by_ticket` /
`close_position_by_ticket`. Una gamba il cui TP è già scattato sul broker non
esiste più: l'errore relativo viene assorbito e loggato, non è un fallimento.

⚠️ Richiede un account MT5 di tipo HEDGING (vedi README): su netting le gambe
si fondono e i ticket indipendenti saltano.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from brokers.base import Order

from .models import ParsedSignal, SignalUpdate, TradePlan

logger = logging.getLogger(__name__)


class Executor:
    """Esegue piani di trade e applica gli update di gestione."""

    def __init__(
        self,
        mode: str = "dry_run",
        broker: Any = None,
        notifier: Any = None,
        config: Optional[dict[str, Any]] = None,
        journal: Any = None,
    ):
        if mode not in ("dry_run", "live"):
            raise ValueError(f"mode non valido: {mode}")
        if mode == "live" and broker is None:
            raise ValueError("mode=live richiede un broker")
        self.mode = mode
        self.broker = broker
        self.notifier = notifier
        self.config = config or {}
        self.journal = journal  # TradeJournal opzionale: log strutturato degli eventi.
        # Piani attivi per canale (per applicare gli update al segnale giusto).
        self._active: dict[str, TradePlan] = {}

    # ---- Ingresso -------------------------------------------------------

    def on_signal(self, plan: TradePlan) -> None:
        """Gestisce un nuovo piano: lo esegue se accettato, altrimenti logga."""
        sig = plan.signal
        if not plan.accepted:
            self._notify(f"⛔ Segnale {sig.symbol} {sig.side} scartato: {plan.reason}")
            self._journal_signal(plan)
            return

        self._active[sig.channel] = plan
        legs_desc = ", ".join(
            f"TP{leg.tp_index}@{leg.take_profit} ({leg.size} lot)" for leg in plan.legs
        )
        header = (
            f"{'🧪 DRY-RUN' if self.mode == 'dry_run' else '🟢 LIVE'} "
            f"{sig.side} {sig.symbol} entry={sig.entry} SL={sig.sl} "
            f"| {len(plan.legs)} gambe, {plan.total_size} lot tot | {legs_desc}"
        )
        logger.info(header)
        self._notify(header)

        if self.mode == "live":
            self._place_legs(plan)
        # Journaling dopo l'apertura: in live le gambe hanno già il loro ticket.
        self._journal_signal(plan)

    # ---- Gestione -------------------------------------------------------

    def on_update(self, update: SignalUpdate) -> None:
        """Applica un update di gestione al piano attivo del canale."""
        plan = self._active.get(update.channel)
        if plan is None:
            logger.info("Update %s su canale %s senza piano attivo: ignorato",
                        update.kind, update.channel)
            self._journal_update(update, None)
            return

        if update.kind == "tp_hit" and (update.tp_index or 0) >= self._be_trigger():
            msg = f"➡️ {plan.signal.symbol}: TP{update.tp_index} hit → SL a break-even ({plan.signal.entry})"
            logger.info(msg)
            self._notify(msg)
            if self.mode == "live":
                self._move_sl_to_be(plan)
        elif update.kind == "close_all":
            msg = f"🚫 {plan.signal.symbol}: chiusura richiesta dal canale"
            logger.info(msg)
            self._notify(msg)
            if self.mode == "live":
                self._close_all(plan)
            self._active.pop(update.channel, None)
        elif update.kind == "all_tp":
            msg = f"🎯 {plan.signal.symbol}: tutti i TP raggiunti"
            logger.info(msg)
            self._notify(msg)
            self._active.pop(update.channel, None)

        self._journal_update(update, plan)

    # ---- Stato / riconciliazione ---------------------------------------

    def has_active(self, channel: str) -> bool:
        """True se c'è già un trade attivo sul canale (policy: uno per canale)."""
        return channel in self._active

    def on_reconcile(self, signal: ParsedSignal) -> None:
        """Applica i livelli esatti del mentore (messaggio #3) al trade aperto sul 'NOW'.

        Sovrascrive SL/TP provvisori con quelli dichiarati: lo SL su tutte le
        gambe, il TP della gamba i con `signal.tps[i]`. È la fonte di verità per i
        livelli. Se non c'è un trade attivo (trigger 'NOW' non visto), ignora.
        """
        plan = self._active.get(signal.channel)
        if plan is None:
            logger.info("Livelli ricevuti su %s ma nessun trade attivo: ignoro "
                        "(manca il trigger NOW)", signal.channel)
            self._journal_reconcile(signal, None)
            return

        for i, leg in enumerate(plan.legs):
            new_tp = signal.tps[i] if i < len(signal.tps) else leg.take_profit
            leg.stop_loss = signal.sl
            leg.take_profit = new_tp
            if self.mode == "live" and leg.ticket is not None:
                try:
                    self.broker.modify_position_by_ticket(
                        leg.ticket, new_sl=signal.sl, new_tp=new_tp
                    )
                except Exception as exc:
                    logger.info("Riconciliazione ticket %s saltata (gamba chiusa?): %s",
                                leg.ticket, exc)
        if len(signal.tps) != len(plan.legs):
            logger.warning("Riconciliazione %s: %d TP dichiarati vs %d gambe aperte",
                           signal.symbol, len(signal.tps), len(plan.legs))
        msg = (f"🔧 {signal.symbol}: livelli riconciliati → SL {signal.sl}, "
               f"TP {signal.tps}")
        logger.info(msg)
        self._notify(msg)
        self._journal_reconcile(signal, plan)

    # ---- Helper live ----------------------------------------------------

    def _place_legs(self, plan: TradePlan) -> None:
        for leg in plan.legs:
            order = Order(
                symbol=leg.symbol,
                direction=leg.direction,
                size=leg.size,
                order_type="market",
                stop_loss=leg.stop_loss,
                take_profit=leg.take_profit,
                note=leg.note,
            )
            try:
                oid = self.broker.place_order(order)
                try:
                    leg.ticket = int(oid)
                except (TypeError, ValueError):
                    leg.ticket = None
                    logger.warning("Gamba TP%d aperta ma id non numerico=%r: "
                                   "management per-ticket non disponibile", leg.tp_index, oid)
                logger.info("Gamba TP%d aperta ticket=%s", leg.tp_index, leg.ticket)
            except Exception as exc:
                logger.error("Apertura gamba TP%d fallita: %s", leg.tp_index, exc)
                self._notify(f"⚠️ Apertura gamba TP{leg.tp_index} fallita: {exc}")

    def _move_sl_to_be(self, plan: TradePlan) -> None:
        """Sposta lo SL a break-even su tutte le gambe ancora aperte (per-ticket)."""
        be_price = plan.signal.entry
        for leg in plan.legs:
            if leg.ticket is None:
                continue
            try:
                self.broker.modify_position_by_ticket(leg.ticket, new_sl=be_price)
            except Exception as exc:
                # Una gamba può essersi già chiusa (TP colpito sul broker): non è un errore.
                logger.info("BE su ticket %s saltato (probabile gamba già chiusa): %s",
                            leg.ticket, exc)

    def _close_all(self, plan: TradePlan) -> None:
        """Chiude a mercato tutte le gambe ancora aperte (per-ticket)."""
        for leg in plan.legs:
            if leg.ticket is None:
                continue
            try:
                self.broker.close_position_by_ticket(leg.ticket)
            except Exception as exc:
                logger.info("Close su ticket %s saltato (probabile gamba già chiusa): %s",
                            leg.ticket, exc)

    # ---- Util -----------------------------------------------------------

    def _be_trigger(self) -> int:
        return int(self.config.get("manage", {}).get("move_sl_to_be_on_tp", 1))

    def _notify(self, text: str) -> None:
        if self.notifier is not None:
            try:
                self.notifier.send_message(text)
            except Exception as exc:
                logger.warning("Notifica fallita: %s", exc)

    def _journal_signal(self, plan: TradePlan) -> None:
        if self.journal is not None:
            try:
                self.journal.log_signal(plan, self.mode)
            except Exception as exc:
                logger.warning("Journal signal fallito: %s", exc)

    def _journal_update(self, update: SignalUpdate, plan: Optional[TradePlan]) -> None:
        if self.journal is not None:
            try:
                self.journal.log_update(update, plan, self.mode)
            except Exception as exc:
                logger.warning("Journal update fallito: %s", exc)

    def _journal_reconcile(self, signal: ParsedSignal, plan: Optional[TradePlan]) -> None:
        if self.journal is not None:
            try:
                self.journal.log_reconcile(signal, plan, self.mode)
            except Exception as exc:
                logger.warning("Journal reconcile fallito: %s", exc)
