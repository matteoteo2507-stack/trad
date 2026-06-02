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
        self._fail = set(fail_tickets or ())
        self.price = price

    def get_price(self, symbol):
        return self.price

    def place_order(self, order):  # noqa: ANN001 - firma minima per il test
        self._next += 1
        self.placed.append(self._next)
        return str(self._next)

    def modify_position_by_ticket(self, ticket, new_sl=None, new_tp=None):
        if ticket in self._fail:
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


def test_dispatch_trigger_ignorato_se_trade_attivo(tmp_path):
    """Policy v1: un nuovo trigger mentre un trade è attivo viene ignorato."""
    from signal_copier.__main__ import _dispatch

    broker = _FakeBroker(price=4530.0)
    ex = Executor(mode="live", broker=broker, config={"manage": {"move_sl_to_be_on_tp": 1}})
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD SELL NOW", broker=broker)
    assert len(broker.placed) == 3
    _dispatch(_parser(), ex, COPIER_CFG, 10000, "XAUUSD BUY NOW", broker=broker)
    assert len(broker.placed) == 3  # nessuna nuova gamba: ignorato


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
