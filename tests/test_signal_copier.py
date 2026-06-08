"""Test del signal copier: parser XAU, planner (sizing + gate), reader offline."""

from __future__ import annotations

import json
from pathlib import Path

from signal_copier.executor import Executor
from signal_copier.journal import TradeJournal
from signal_copier.models import EntryTrigger, ParsedSignal, SignalUpdate
from signal_copier.parsers import get_parser
from signal_copier.parsers.xau_analysis_lab import XauAnalysisLabParser
from signal_copier.planner import build_plan
from signal_copier.reader import iter_offline_messages

SAMPLES = Path(__file__).parent.parent / "signal_copier" / "samples" / "xau_analysis_lab.txt"

COPIER_CFG = {
    "symbols_whitelist": ["XAUUSD"],
    "risk": {"risk_per_signal_pct": 0.01},
    "min_lot": 0.01,
    "lot_step": 0.01,
    "max_total_lots": 5.0,
    "anti_late": {"enabled": True, "max_slippage_pips": 20},
    "manage": {"move_sl_to_be_on_tp": 1},
    "account_balance_hint": 10000,
}

SIGNAL_TXT = (
    "📉 XAUUSD SELL Signal (Gold)\n"
    "✅ Entry: 4536\n"
    "🎯 Target\n"
    "- TP1: 4531\n- TP2: 4526\n- TP3: 4521\n"
    "🛑 Stop Loss: 4546"
)


def _parser() -> XauAnalysisLabParser:
    return XauAnalysisLabParser()


# ---- Parser ---------------------------------------------------------------


def test_parse_new_signal():
    res = _parser().parse(SIGNAL_TXT)
    assert isinstance(res, ParsedSignal)
    assert res.symbol == "XAUUSD"
    assert res.side == "SELL"
    assert res.direction == "short"
    assert res.entry == 4536
    assert res.sl == 4546
    assert res.tps == [4531, 4526, 4521]


def test_parse_tp1_hit():
    res = _parser().parse("TP1 SUCCESSFUL 🔥\nENJOY YOUR PROFIT ✅🔥\n50 PIPS")
    assert isinstance(res, SignalUpdate)
    assert res.kind == "tp_hit"
    assert res.tp_index == 1


def test_parse_all_tp():
    res = _parser().parse("All TP SUCCESSFUL 🔥\n150 PIPS PROFIT RUNNING")
    assert isinstance(res, SignalUpdate)
    assert res.kind == "all_tp"


def test_parse_close():
    res = _parser().parse("Close your trades and book profit 🚫🚫🚫")
    assert isinstance(res, SignalUpdate)
    assert res.kind == "close_all"


def test_parse_promo_ignored():
    assert _parser().parse("🎁 PROMO: unisciti al canale VIP! Link in bio 🚀") is None


def test_parser_registered():
    assert get_parser("xauusd_analysislab") is not None


# ---- Reader offline -------------------------------------------------------


def test_offline_messages_count():
    msgs = list(iter_offline_messages(SAMPLES))
    # 8 blocchi: get-ready, NOW, segnale-livelli, TP1, TP2, all-tp, close, promo
    assert len(msgs) == 8
    assert any("NOW" in m for m in msgs)
    assert any("SELL Signal" in m for m in msgs)


def test_parse_now_trigger():
    res = _parser().parse("XAUUSD SELL NOW 🔥")
    assert isinstance(res, EntryTrigger)
    assert res.side == "SELL"
    assert res.direction == "short"


# ---- Canale GOLD 5 TP (entry_mode=signal, tutto-in-uno) --------------------

from signal_copier.parsers.gold_5tp import Gold5TpParser

GOLD5_SIGNAL = (
    "GOLD BUY 4470//4466\n\n"
    "✔️TP¹ 4474\n✔️TP² 4478\n✔️TP³ 4482\n✔️TP⁴ 4486\n✔️TP⁵ 4490\n\n"
    "🚫SL 4456"
)


def test_gold5tp_parse_signal():
    res = Gold5TpParser().parse(GOLD5_SIGNAL)
    assert isinstance(res, ParsedSignal)
    assert res.side == "BUY" and res.symbol == "XAUUSD"
    assert res.entry == 4470.0 and res.sl == 4456.0
    assert res.tps == [4474.0, 4478.0, 4482.0, 4486.0, 4490.0]  # 5 TP, apici Unicode


def test_gold5tp_headsup_ignorato():
    assert Gold5TpParser().parse("READY FOR GOLD SIGNAL") is None
    assert Gold5TpParser().entry_mode == "signal"


def test_dispatch_signal_mode_apre_5_gambe(tmp_path):
    """Canale signal-mode: il messaggio completo apre 5 gambe a mercato (no trigger)."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4470.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}},
                  journal=TradeJournal(tmp_path / "j.jsonl"))
    _dispatch(Gold5TpParser(), ex, COPIER_CFG, 10000, GOLD5_SIGNAL, broker=broker)
    assert len(broker.placed) == 5  # una gamba per TP


def test_gold5tp_parse_tp_hit():
    res = Gold5TpParser().parse("GOLD SELL tp 1 hit 40 pips running profit✌️✌️💪🔥🔥")
    assert isinstance(res, SignalUpdate)
    assert res.kind == "tp_hit" and res.tp_index == 1


def test_executor_libera_canale_quando_flat(tmp_path):
    """Canale senza 'close': quando il broker non ha più gambe aperte, il canale si libera."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4470.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(Gold5TpParser(), ex, COPIER_CFG, 10000, GOLD5_SIGNAL, broker=broker)
    assert ex.has_active("gold_5tp")
    broker.closed = list(broker.placed)  # tutte le gambe risultano chiuse sul broker
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=5))
    assert not ex.has_active("gold_5tp")


# ---- Trailing a gradino (BE → SL a TP1 a TP3) -----------------------------

TRAIL_CFG = {"manage": {"move_sl_to_be_on_tp": 1,
                        "trail": {"enabled": True, "on_tp": 3, "to_tp": 1}}}


def _gold5_live(tmp_path):
    """Apre le 5 gambe del canale gold_5tp con trailing attivo. Ritorna (broker, ex)."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4470.0)
    ex = Executor(mode="live", broker=broker, config=TRAIL_CFG)
    _dispatch(Gold5TpParser(), ex, COPIER_CFG, 10000, GOLD5_SIGNAL, broker=broker)
    assert len(broker.placed) == 5
    return broker, ex


def test_trailing_be_su_tp1_poi_sl_a_tp1_su_tp3(tmp_path):
    broker, ex = _gold5_live(tmp_path)
    # TP1 → break-even (entry BUY = 4470) su tutte le gambe.
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=1))
    assert broker.modified and all(m["sl"] == 4470.0 for m in broker.modified)
    broker.modified.clear()
    # TP3 → SL a TP1 (4474) sulle gambe residue, una sola volta.
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=3))
    assert broker.modified and all(m["sl"] == 4474.0 for m in broker.modified)


def test_trailing_non_torna_a_be_dopo_il_gradino(tmp_path):
    broker, ex = _gold5_live(tmp_path)
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=3))  # trailing a TP1
    broker.modified.clear()
    # tp_hit successivi non devono riabbassare lo SL a BE né rispostarlo.
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=4))
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=5))
    assert broker.modified == []


def test_trailing_scatta_anche_se_tp3_perso(tmp_path):
    # Se il messaggio di TP3 si perde e arriva TP4, il trailing scatta comunque.
    broker, ex = _gold5_live(tmp_path)
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=4))
    assert broker.modified and all(m["sl"] == 4474.0 for m in broker.modified)


def test_trailing_disattivo_resta_be(tmp_path):
    # Senza config trail (comportamento storico): a TP3 lo SL resta a break-even.
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4470.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(Gold5TpParser(), ex, COPIER_CFG, 10000, GOLD5_SIGNAL, broker=broker)
    ex.on_update(SignalUpdate(kind="tp_hit", channel="gold_5tp", tp_index=3))
    assert broker.modified and all(m["sl"] == 4470.0 for m in broker.modified)  # BE, non TP1


# ---- Gestione guidata dal broker (BE/trailing senza messaggi del canale) ----


def test_poll_arma_be_quando_tp1_chiude_sul_broker():
    """Il poll arma il BE vedendo la gamba TP1 chiusa sul broker, SENZA messaggio."""
    sig, plan, broker, ex = _live_plan_and_broker()  # canale 1, 3 gambe, BE@TP1
    # La gamba TP1 (primo ticket) risulta chiusa sul broker: nessun 'tp_hit' inviato.
    broker.closed.append(plan.legs[0].ticket)
    ex.poll_broker_management()
    # BE applicato alle 2 gambe ancora aperte (entry = sig.entry), senza alcun on_update.
    assert {m["ticket"] for m in broker.modified} == {plan.legs[1].ticket, plan.legs[2].ticket}
    assert all(m["sl"] == sig.entry for m in broker.modified)
    assert plan.be_armed


def test_poll_non_riapplica_be_se_gia_armato():
    sig, plan, broker, ex = _live_plan_and_broker()
    broker.closed.append(plan.legs[0].ticket)
    ex.poll_broker_management()
    broker.modified.clear()
    ex.poll_broker_management()  # secondo giro: nulla di nuovo
    assert broker.modified == []


def test_poll_trailing_quando_3_gambe_chiuse():
    """Canale gold_5tp: con 3 gambe chiuse il poll porta lo SL a TP1 (trailing)."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4470.0)
    ex = Executor(mode="live", broker=broker, config=TRAIL_CFG)
    _dispatch(Gold5TpParser(), ex, COPIER_CFG, 10000, GOLD5_SIGNAL, broker=broker)
    # Le prime 3 gambe (TP1..TP3) si chiudono sul broker: nessun messaggio inviato.
    broker.closed.extend(broker.placed[:3])
    ex.poll_broker_management()
    # SL portato a TP1 (4474) sulle 2 gambe residue.
    assert broker.modified and all(m["sl"] == 4474.0 for m in broker.modified)


def test_poll_libera_canale_quando_flat():
    sig, plan, broker, ex = _live_plan_and_broker()
    broker.closed = list(broker.placed)  # tutte chiuse
    ex.poll_broker_management()
    assert not ex.has_active(sig.channel)


def test_poll_no_op_in_dry_run():
    sig = _parser().parse(SIGNAL_TXT)
    plan = build_plan(sig, 10000, COPIER_CFG)
    ex = Executor(mode="dry_run", config={"manage": {"move_sl_to_be_on_tp": 1}})
    ex.on_signal(plan)
    ex.poll_broker_management()  # non deve sollevare né fare nulla
    assert not plan.be_armed


# ---- Planner --------------------------------------------------------------


def test_plan_three_legs_sized():
    sig = _parser().parse(SIGNAL_TXT)
    plan = build_plan(sig, balance=10000, config=COPIER_CFG, current_price=None)
    assert plan.accepted
    assert len(plan.legs) == 3
    # SL = 10 prezzo = 100 pip (pip XAU 0.10). Rischio 1% = $100, /3 ≈ $33/gamba.
    # lots = 33 / (100 * 10) ≈ 0.033 → 0.03 dopo arrotondamento.
    assert all(leg.size >= 0.01 for leg in plan.legs)
    assert [leg.take_profit for leg in plan.legs] == [4531, 4526, 4521]
    assert all(leg.stop_loss == 4546 for leg in plan.legs)
    assert all(leg.direction == "short" for leg in plan.legs)


def test_plan_rejects_incoherent_sl():
    # SELL ma SL sotto l'entry → incoerente.
    sig = ParsedSignal(symbol="XAUUSD", side="SELL", entry=4536, sl=4530,
                       tps=[4531], channel="x")
    plan = build_plan(sig, 10000, COPIER_CFG)
    assert not plan.accepted
    assert "SL incoerente" in plan.reason


def test_plan_rejects_late_signal():
    sig = _parser().parse(SIGNAL_TXT)
    # prezzo a 4533 = 30 pip dall'entry (>20) → tardivo.
    plan = build_plan(sig, 10000, COPIER_CFG, current_price=4533.0)
    assert not plan.accepted
    assert "tardivo" in plan.reason


def test_plan_rejects_price_past_tp1():
    sig = _parser().parse(SIGNAL_TXT)
    # SELL, prezzo già sotto TP1 (4531) ma entro slippage → segnale concluso.
    plan = build_plan(sig, 10000, COPIER_CFG, current_price=4530.5)
    assert not plan.accepted


def test_plan_rejects_non_whitelisted_symbol():
    sig = ParsedSignal(symbol="EURUSD", side="BUY", entry=1.10, sl=1.09,
                       tps=[1.11], channel="x")
    plan = build_plan(sig, 10000, COPIER_CFG)
    assert not plan.accepted
    assert "whitelist" in plan.reason


# ---- Executor: gestione per-ticket multi-gamba ----------------------------


class _FakeBroker:
    """Broker finto per testare la gestione per-ticket dell'executor.

    Apre gambe restituendo ticket incrementali; registra le modifiche SL→BE e
    le chiusure. I ticket in `fail_tickets` simulano una gamba già chiusa sul
    broker (il metodo solleva, come farebbe MT5 su posizione inesistente).
    """

    def __init__(self, fail_tickets=None, price=4530.0):
        self._next = 1000
        self.placed: list[int] = []
        self.modified: list[dict] = []
        self.closed: list[int] = []
        self._dir: dict[int, str] = {}  # ticket -> "long"/"short"
        self._fail = set(fail_tickets or ())
        self.price = price
        self.magic = 27050

    def get_price(self, symbol):
        return self.price

    def get_positions(self, symbol):
        from types import SimpleNamespace
        return [SimpleNamespace(ticket=t, direction=self._dir.get(t), magic=self.magic)
                for t in self.placed if t not in self.closed]

    def place_order(self, order):  # noqa: ANN001 - firma minima per il test
        self._next += 1
        self.placed.append(self._next)
        self._dir[self._next] = order.direction
        return str(self._next)

    def modify_position_by_ticket(self, ticket, new_sl=None, new_tp=None):
        # Come MT5: una posizione già chiusa (per TP/SL/flip) non è modificabile.
        if ticket in self._fail or ticket in self.closed:
            raise RuntimeError(f"posizione {ticket} inesistente")
        self.modified.append({"ticket": ticket, "sl": new_sl, "tp": new_tp})

    def close_position_by_ticket(self, ticket):
        if ticket in self._fail:
            raise RuntimeError(f"posizione {ticket} inesistente")
        self.closed.append(ticket)


def _live_executor(broker: _FakeBroker) -> Executor:
    return Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})


def _live_plan_and_broker(fail_tickets=None):
    sig = _parser().parse(SIGNAL_TXT)
    plan = build_plan(sig, 10000, COPIER_CFG)
    broker = _FakeBroker(fail_tickets=fail_tickets)
    ex = _live_executor(broker)
    ex.on_signal(plan)
    return sig, plan, broker, ex


def test_executor_live_apre_gambe_e_traccia_ticket():
    sig, plan, broker, _ = _live_plan_and_broker()
    assert len(broker.placed) == 3
    assert [leg.ticket for leg in plan.legs] == broker.placed


def test_executor_tp1_sposta_be_su_tutte_le_gambe():
    sig, plan, broker, ex = _live_plan_and_broker()
    ex.on_update(SignalUpdate(kind="tp_hit", channel=sig.channel, tp_index=1))
    assert {m["ticket"] for m in broker.modified} == set(broker.placed)
    assert all(m["sl"] == sig.entry for m in broker.modified)


def test_executor_close_all_chiude_tutte_le_gambe():
    sig, plan, broker, ex = _live_plan_and_broker()
    ex.on_update(SignalUpdate(kind="close_all", channel=sig.channel))
    assert set(broker.closed) == set(broker.placed)
    # Piano rimosso dagli attivi: un secondo close non riapre nulla.
    ex.on_update(SignalUpdate(kind="close_all", channel=sig.channel))
    assert len(broker.closed) == 3


def test_executor_be_ignora_gamba_gia_chiusa():
    sig, plan, broker, ex = _live_plan_and_broker()
    closed_leg = plan.legs[0].ticket
    broker._fail.add(closed_leg)  # la gamba 1 ha già colpito il suo TP sul broker
    ex.on_update(SignalUpdate(kind="tp_hit", channel=sig.channel, tp_index=1))
    assert closed_leg not in {m["ticket"] for m in broker.modified}
    assert len({m["ticket"] for m in broker.modified}) == 2  # le altre 2 gambe ricevono il BE


# ---- Trade journal (auto-log, sostituisce Notion) -------------------------


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_journal_logs_signal_with_rr(tmp_path):
    sig = _parser().parse(SIGNAL_TXT)
    plan = build_plan(sig, 10000, COPIER_CFG)
    jpath = tmp_path / "j.jsonl"
    TradeJournal(jpath).log_signal(plan, mode="live")
    rec = _read_jsonl(jpath)[0]
    assert rec["event"] == "signal_accepted"
    assert rec["symbol"] == "XAUUSD" and rec["side"] == "SELL"
    assert len(rec["legs"]) == 3
    # R/R pianificato gamba1: |4531-4536| / |4536-4546| = 5/10 = 0.5
    assert rec["legs"][0]["rr"] == 0.5


def test_journal_logs_rejection(tmp_path):
    sig = ParsedSignal(symbol="EURUSD", side="BUY", entry=1.10, sl=1.09, tps=[1.11], channel="x")
    plan = build_plan(sig, 10000, COPIER_CFG)
    jpath = tmp_path / "j.jsonl"
    TradeJournal(jpath).log_signal(plan, mode="dry_run")
    rec = _read_jsonl(jpath)[0]
    assert rec["event"] == "signal_rejected"
    assert "whitelist" in rec["reason"]


def test_dispatch_trigger_apre_a_mercato(tmp_path):
    """Il trigger 'NOW' apre a mercato col prezzo del broker (SL fisso, TP provvisori)."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4530.0)
    jpath = tmp_path / "j.jsonl"
    ex = Executor(mode="live", broker=broker,
                  config={"manage": {"move_sl_to_be_on_tp": 1}}, journal=TradeJournal(jpath))
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW 🔥", broker=broker)
    assert len(broker.placed) == 3
    rec = _read_jsonl(jpath)[0]
    assert rec["event"] == "signal_accepted"
    assert rec["entry"] == 4530.0 and rec["sl"] == 4540.0  # SELL: SL = entry + sl_distance(10)


def test_dispatch_riconcilia_livelli_dopo_trigger(tmp_path):
    """Dopo il trigger, il messaggio coi livelli sovrascrive SL/TP esatti sulle gambe."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4530.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW", broker=broker)
    _dispatch(_parser(), ex, COPIER_CFG, 10000, SIGNAL_TXT, broker=broker)  # entry 4536, SL 4546, TP 4531/4526/4521
    assert len(broker.modified) == 3
    assert all(m["sl"] == 4546.0 for m in broker.modified)
    assert sorted(m["tp"] for m in broker.modified) == [4521.0, 4526.0, 4531.0]


def test_dispatch_reentry_stesso_bias_ignorato(tmp_path):
    """Re-entry con STESSO bias mentre un trade è aperto → ignorato (uno per simbolo)."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4530.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW", broker=broker)
    assert len(broker.placed) == 3
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW", broker=broker)  # stesso bias
    assert len(broker.placed) == 3  # nessuna nuova gamba
    assert not broker.closed         # niente flip


def test_dispatch_flip_su_bias_opposto(tmp_path):
    """Nuovo segnale con bias OPPOSTO → chiude il vecchio trade e apre il nuovo."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4530.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW", broker=broker)  # apre SELL
    first = list(broker.placed)
    assert len(first) == 3
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD BUY NOW", broker=broker)   # bias opposto
    assert set(first).issubset(set(broker.closed))  # le 3 vecchie chiuse (flip)
    assert len(broker.placed) == 6                   # + 3 nuove (BUY)


def test_executor_journals_signal_and_update(tmp_path):
    sig = _parser().parse(SIGNAL_TXT)
    plan = build_plan(sig, 10000, COPIER_CFG)
    broker = _FakeBroker()
    jpath = tmp_path / "j.jsonl"
    ex = Executor(mode="live", broker=broker,
                  config={"manage": {"move_sl_to_be_on_tp": 1}}, journal=TradeJournal(jpath))
    ex.on_signal(plan)
    ex.on_update(SignalUpdate(kind="tp_hit", channel=sig.channel, tp_index=1))
    recs = _read_jsonl(jpath)
    assert [r["event"] for r in recs] == ["signal_accepted", "update_tp_hit"]
    # il ticket della gamba aperta finisce nel record del segnale
    assert recs[0]["legs"][0]["ticket"] == broker.placed[0]
