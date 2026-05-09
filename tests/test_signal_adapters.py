"""Test sugli adapter centralizzati di `strategies/_base.py`."""

from __future__ import annotations

import pytest

from brokers.base import Order
from notifiers.base import TradingSignal
from strategies._base import Signal


def test_long_signal_diventa_buy_in_trading_signal():
    s = Signal(direction="long", size=0.1, sl=1.0800, tp=1.0950, confidence=80, note="test")
    ts = s.to_trading_signal(
        symbol="EURUSD",
        strategy_name="confluence_levels",
        timeframe="H1",
        current_price=1.0850,
    )
    assert isinstance(ts, TradingSignal)
    assert ts.direction == "BUY"
    assert ts.symbol == "EURUSD"
    assert ts.entry_price == 1.0850
    assert ts.stop_loss == 1.0800
    assert ts.take_profit == 1.0950
    assert ts.confidence == 80
    # RR = (1.0950-1.0850)/(1.0850-1.0800) = 0.01/0.005 = 2.0
    assert ts.rr_ratio == pytest.approx(2.0)


def test_short_signal_diventa_sell_in_trading_signal():
    s = Signal(direction="short", size=0.1, sl=2400, tp=2350, confidence=70)
    ts = s.to_trading_signal(
        symbol="XAUUSD",
        strategy_name="confluence_levels",
        timeframe="H4",
        current_price=2380,
    )
    assert ts.direction == "SELL"
    # RR = (2380-2350)/(2400-2380) = 30/20 = 1.5
    assert ts.rr_ratio == pytest.approx(1.5)


def test_reward_to_risk_zero_quando_sl_uguale_entry():
    s = Signal(direction="long", size=0.1, sl=1.0850, tp=1.0900)
    assert s.reward_to_risk(entry_price=1.0850) == 0.0


def test_to_order_market_default():
    s = Signal(direction="long", size=0.5, sl=1.0800, tp=1.0950, note="break")
    order = s.to_order(symbol="EURUSD")
    assert isinstance(order, Order)
    assert order.symbol == "EURUSD"
    assert order.direction == "long"
    assert order.size == 0.5
    assert order.order_type == "market"
    assert order.stop_loss == 1.0800
    assert order.take_profit == 1.0950
    assert order.limit_price is None


def test_to_order_limit_con_prezzo():
    s = Signal(direction="short", size=0.2, sl=2410, tp=2350)
    order = s.to_order(symbol="XAUUSD", order_type="limit", limit_price=2400)
    assert order.order_type == "limit"
    assert order.limit_price == 2400
    assert order.direction == "short"
