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

        if update.kind == "tp_hit":
            self._manage_tp_hit(plan, update.tp_index or 0)
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

        # Canali senza messaggio di chiusura: libera il canale quando sul broker non
        # resta aperta nessuna delle gambe (tutte chiuse da TP o SL). Vale anche da
        # rete di sicurezza per i canali con "close" se quel messaggio si perde.
        if update.channel in self._active and self._all_legs_closed(plan):
            logger.info("%s: gambe tutte chiuse sul broker → canale liberato",
                        plan.signal.symbol)
            self._active.pop(update.channel, None)

        self._journal_update(update, plan)

    def _manage_tp_hit(self, plan: TradePlan, idx: int) -> None:
        """Gestione su 'tp_hit' dal canale: delega alla logica condivisa."""
        self._apply_management(plan, idx)

    def _apply_management(self, plan: TradePlan, reached_tp: int) -> None:
        """Scala lo SL in base al numero di TP raggiunti (`reached_tp`).

        Sorgente unica per i due trigger: il messaggio del canale (`tp_index`) e
        il broker (n. gambe chiuse — vedi `poll_broker_management`). Due gradini,
        in ordine crescente di protezione; flag idempotenti così non si torna mai
        indietro (un trigger tardivo non riporta lo SL a BE dopo il trailing):
        1. `reached_tp >= move_sl_to_be_on_tp` (default 1) → SL a break-even.
        2. trailing opzionale: `reached_tp >= manage.trail.on_tp` → SL al livello di
           `manage.trail.to_tp` (1-based) sulle gambe residue, **una sola volta**.

        Es. gold_5tp (5 TP, spacing fisso): BE dopo TP1, poi a TP3 lo SL va a TP1
        (blocca profitto lasciando correre i runner TP4/TP5). Sui canali con meno
        TP il trailing è inerte (al TP finale le gambe sono già chiuse).
        """
        if reached_tp <= 0:
            return
        trail = (self.config.get("manage", {}) or {}).get("trail", {}) or {}
        trail_on = int(trail.get("on_tp", 0)) if trail.get("enabled") else 0
        if trail_on and reached_tp >= trail_on and not plan.trailed:
            to_tp = int(trail.get("to_tp", 1))
            level = self._tp_level(plan, to_tp)
            if level is None:
                logger.warning("%s: trailing richiesto a TP%d ma livello assente "
                               "(%d TP) → niente trailing", plan.signal.symbol, to_tp,
                               len(plan.signal.tps))
                return
            msg = (f"⏫ {plan.signal.symbol}: TP{reached_tp} raggiunto → SL a TP{to_tp} "
                   f"({level}) sulle gambe residue")
            logger.info(msg)
            self._notify(msg)
            if self.mode == "live":
                self._move_sl_to_price(plan, level)
            plan.trailed = True
            plan.be_armed = True  # il trailing è più protettivo del BE: copre anche quello
            return
        if not plan.be_armed and reached_tp >= self._be_trigger():
            msg = (f"➡️ {plan.signal.symbol}: TP{reached_tp} raggiunto → SL a "
                   f"break-even ({plan.signal.entry})")
            logger.info(msg)
            self._notify(msg)
            if self.mode == "live":
                self._move_sl_to_be(plan)
            plan.be_armed = True

    def poll_broker_management(self) -> None:
        """Gestione guidata dal broker, indipendente dai messaggi del canale.

        Chiamata periodicamente dal loop live: per ogni piano attivo conta le
        gambe **chiuse sul broker** (= TP raggiunti, dato che condividono lo SL) e
        applica BE/trailing di conseguenza. Così il break-even scatta anche quando
        il canale **non manda** (o manda in formato non parsato) il "TP hit" — il
        caso che ieri ha lasciato due gambe sullo SL pieno. I messaggi restano
        come conferma ridondante. Libera il canale quando tutto è chiuso.
        """
        if self.mode != "live" or self.broker is None:
            return
        for channel, plan in list(self._active.items()):
            reached = self._closed_leg_count(plan)
            if reached > 0:
                self._apply_management(plan, reached)
            if self._all_legs_closed(plan):
                logger.info("%s: gambe tutte chiuse sul broker (poll) → canale liberato",
                            plan.signal.symbol)
                self._active.pop(channel, None)

    def _closed_leg_count(self, plan: TradePlan) -> int:
        """Quante gambe del piano non sono più aperte sul broker (proxy dei TP raggiunti)."""
        leg_tickets = [leg.ticket for leg in plan.legs if leg.ticket is not None]
        if not leg_tickets:
            return 0
        try:
            open_tickets = {
                getattr(p, "ticket", None)
                for p in self.broker.get_positions(plan.signal.symbol)
            }
        except Exception as exc:
            logger.debug("poll get_positions fallito: %s", exc)
            return 0
        return sum(1 for t in leg_tickets if t not in open_tickets)

    # ---- Stato / riconciliazione ---------------------------------------

    def has_active(self, channel: str) -> bool:
        """True se c'è un trade davvero attivo sul canale.

        Si riconcilia col broker (fonte di verità): se le gambe risultano tutte
        chiuse — es. **SL colpito senza notifica** del canale — libera il canale
        così il prossimo segnale può entrare. Senza questo, lo stato dedotto dai
        soli messaggi (incompleti) bloccherebbe i segnali successivi.
        """
        plan = self._active.get(channel)
        if plan is None:
            return False
        if self._all_legs_closed(plan):
            logger.info("%s: trade non più aperto sul broker → canale liberato",
                        plan.signal.symbol)
            self._active.pop(channel, None)
            return False
        return True

    def prepare_for_new_trade(self, symbol: str, direction: str) -> bool:
        """Policy "uno per simbolo" + flip su cambio bias. True se si deve aprire.

        - nessun trade nostro aperto sul simbolo → True (apri);
        - trade aperto **stesso bias** → False (re-entry ignorato);
        - trade aperto **bias opposto** → chiude il vecchio e ritorna True (flip).

        Fonte di verità: il broker in live (posizioni nostre, filtrate per magic),
        altrimenti i piani in memoria (dry-run).
        """
        open_dir, tickets = self._open_direction_and_tickets(symbol)
        if open_dir is None:
            return True
        if open_dir == direction:
            logger.info("%s: trade %s già aperto, stesso bias → re-entry ignorato",
                        symbol, direction)
            return False
        logger.info("%s: bias cambiato (%s → %s) → chiudo il vecchio trade e apro il nuovo",
                    symbol, open_dir, direction)
        self._notify(f"🔄 {symbol}: bias invertito → chiudo {open_dir}, apro {direction}")
        self._close_tickets(tickets)
        for ch, plan in list(self._active.items()):
            if plan.signal.symbol == symbol:
                self._active.pop(ch, None)
        return True

    def _open_direction_and_tickets(self, symbol: str):
        """(direzione, [ticket]) del trade NOSTRO aperto sul simbolo, o (None, [])."""
        if self.mode == "live" and self.broker is not None:
            try:
                positions = self.broker.get_positions(symbol)
            except Exception as exc:
                logger.debug("prepare get_positions fallito: %s", exc)
                positions = []
            magic = getattr(self.broker, "magic", None)
            ours = [p for p in positions
                    if magic is None or getattr(p, "magic", None) == magic]
            if ours:
                tickets = [p.ticket for p in ours if getattr(p, "ticket", None) is not None]
                return ours[0].direction, tickets
            return None, []
        # dry-run / no broker: stato in memoria
        for plan in self._active.values():
            if plan.signal.symbol == symbol and not self._all_legs_closed(plan):
                return plan.signal.direction, [l.ticket for l in plan.legs if l.ticket]
        return None, []

    def _close_tickets(self, tickets) -> None:
        """Chiude per-ticket (flip). Best-effort: una gamba già chiusa non è errore."""
        if self.mode != "live" or self.broker is None:
            return
        for t in tickets:
            try:
                self.broker.close_position_by_ticket(t)
            except Exception as exc:
                logger.info("Flip: chiusura ticket %s saltata: %s", t, exc)

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
        if plan.reconciled:
            # I livelli del trade in corso sono già stati applicati: questo è un
            # secondo messaggio di livelli (es. re-entry stesso bias) → non riscrivere.
            logger.info("%s: livelli già applicati, ignoro (probabile re-entry)", signal.symbol)
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
        plan.reconciled = True
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
        self._move_sl_to_price(plan, plan.signal.entry)

    def _move_sl_to_price(self, plan: TradePlan, price: float) -> None:
        """Sposta lo SL al prezzo dato su tutte le gambe ancora aperte (per-ticket)."""
        for leg in plan.legs:
            if leg.ticket is None:
                continue
            try:
                self.broker.modify_position_by_ticket(leg.ticket, new_sl=price)
            except Exception as exc:
                # Una gamba può essersi già chiusa (TP colpito sul broker): non è un errore.
                logger.info("Spostamento SL su ticket %s saltato (probabile gamba già chiusa): %s",
                            leg.ticket, exc)

    @staticmethod
    def _tp_level(plan: TradePlan, tp_index: int) -> Optional[float]:
        """Prezzo del TP `tp_index` (1-based) dichiarato dal segnale, o None se assente."""
        tps = plan.signal.tps
        if 1 <= tp_index <= len(tps):
            return tps[tp_index - 1]
        return None

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

    def _all_legs_closed(self, plan: TradePlan) -> bool:
        """True se nessuna gamba del piano è più aperta sul broker (solo live)."""
        if self.mode != "live" or self.broker is None:
            return False
        leg_tickets = {leg.ticket for leg in plan.legs if leg.ticket is not None}
        if not leg_tickets:
            return False
        try:
            open_tickets = {
                getattr(p, "ticket", None)
                for p in self.broker.get_positions(plan.signal.symbol)
            }
        except Exception as exc:
            logger.debug("flat-check get_positions fallito: %s", exc)
            return False
        return leg_tickets.isdisjoint(open_tickets)

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
