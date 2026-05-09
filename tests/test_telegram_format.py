"""Test del formatting Telegram. Mock di requests, niente chiamate reali."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from notifiers.base import TradingSignal
from notifiers.telegram import TelegramNotifier


@pytest.fixture
def signal_buy_eurusd() -> TradingSignal:
    return TradingSignal(
        symbol="EURUSD",
        direction="BUY",
        strategy_name="confluence_levels",
        timeframe="H1",
        entry_price=1.08500,
        stop_loss=1.08000,
        take_profit=1.09500,
        size=0.10,
        confidence=80,
        rr_ratio=2.0,
        note="break livello 1.085",
        valid_minutes=120,
    )


@pytest.fixture
def signal_sell_xau() -> TradingSignal:
    return TradingSignal(
        symbol="XAUUSD",
        direction="SELL",
        strategy_name="confluence_levels",
        timeframe="H4",
        entry_price=2380.00,
        stop_loss=2400.00,
        take_profit=2350.00,
        size=0.01,
        confidence=65,
        rr_ratio=1.5,
    )


def _mock_notifier() -> tuple[TelegramNotifier, MagicMock]:
    session = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"ok": True, "result": {}}
    session.post.return_value = response
    return TelegramNotifier(bot_token="x", chat_id="123", session=session), session


def test_format_signal_buy_contiene_emoji_e_campi(signal_buy_eurusd):
    text = TelegramNotifier._format_signal(signal_buy_eurusd)
    assert "🟢" in text
    assert "BUY EURUSD" in text
    assert "Strategia: confluence_levels" in text
    assert "Timeframe: H1" in text
    assert "1.08500" in text  # entry con 5 decimali
    assert "1.08000" in text  # SL
    assert "1.09500" in text  # TP
    assert "Ratio R/R: 2.00" in text
    assert "Confidence: 80%" in text
    assert "break livello 1.085" in text


def test_format_signal_sell_emoji_rossa_e_decimali_xau(signal_sell_xau):
    text = TelegramNotifier._format_signal(signal_sell_xau)
    assert "🔴" in text
    assert "SELL XAUUSD" in text
    assert "2380.00" in text
    assert "2400.00" in text


def test_format_signal_pip_delta_calcolato(signal_buy_eurusd):
    text = TelegramNotifier._format_signal(signal_buy_eurusd)
    # SL 50 pip sotto, TP 100 pip sopra
    assert "50.0 pip" in text
    assert "100.0 pip" in text


def test_send_signal_chiama_api_telegram(signal_buy_eurusd):
    notifier, session = _mock_notifier()
    notifier.send_signal(signal_buy_eurusd)
    session.post.assert_called_once()
    args, kwargs = session.post.call_args
    assert "api.telegram.org" in args[0]
    assert "/sendMessage" in args[0]
    body = kwargs["data"]
    assert body["chat_id"] == "123"
    assert "BUY EURUSD" in body["text"]


def test_pending_order_alert_contiene_confluenza():
    notifier, session = _mock_notifier()
    level = {
        "id": "EURUSD-W19-S1",
        "price": 1.0850,
        "type": "support",
        "confluence": ["SR_weekly", "SD_H4", "Fib_618"],
    }
    notifier.send_pending_order_alert(
        level=level,
        direction="BUY",
        symbol="EURUSD",
        sl=1.0820,
        tp=1.0950,
        rationale="Prossimità entro 12 pip",
    )
    body = session.post.call_args.kwargs["data"]
    text = body["text"]
    assert "EURUSD" in text
    assert "SR_weekly" in text
    assert "Fib_618" in text
    assert "Prossimità entro 12 pip" in text


def test_send_message_passa_attraverso():
    notifier, session = _mock_notifier()
    notifier.send_message("ciao")
    body = session.post.call_args.kwargs["data"]
    assert body["text"] == "ciao"


def test_exit_alert_format():
    notifier, session = _mock_notifier()
    notifier.send_exit_alert("EURUSD", "macro radar = CASH")
    body = session.post.call_args.kwargs["data"]
    assert "⚠️" in body["text"]
    assert "EXIT EURUSD" in body["text"]
    assert "macro radar" in body["text"]


def test_retry_dopo_failure(signal_buy_eurusd):
    notifier, session = _mock_notifier()
    bad_resp = MagicMock()
    bad_resp.status_code = 500
    bad_resp.text = "internal"
    bad_resp.json.return_value = {"ok": False}
    good_resp = MagicMock()
    good_resp.status_code = 200
    good_resp.json.return_value = {"ok": True}
    session.post.side_effect = [bad_resp, good_resp]

    # Patch sleep per non bloccare i test
    import notifiers.telegram as tg_mod

    original_sleep = tg_mod.time.sleep
    tg_mod.time.sleep = lambda _: None
    try:
        notifier.send_signal(signal_buy_eurusd)
    finally:
        tg_mod.time.sleep = original_sleep

    assert session.post.call_count == 2
