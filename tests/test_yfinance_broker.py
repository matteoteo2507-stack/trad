"""Test di `brokers/yfinance_data.py`.

I test "live" (con rete) sono marcati e si saltano se yfinance non risponde.
I test "offline" (errori, mapping, null object) girano sempre.
"""

from __future__ import annotations

import pytest

from brokers.yfinance_data import YFinanceBroker
from brokers.base import Order


# ---------------------------------------------------------------------------
# Test offline
# ---------------------------------------------------------------------------


def test_resolve_symbol_eurusd():
    b = YFinanceBroker()
    assert b._resolve_symbol("EURUSD") == "EURUSD=X"


def test_resolve_symbol_xauusd_usa_gold_future():
    b = YFinanceBroker()
    assert b._resolve_symbol("XAUUSD") == "GC=F"


def test_resolve_symbol_override():
    b = YFinanceBroker(symbol_overrides={"XAUUSD": "XAUUSD=X"})
    assert b._resolve_symbol("XAUUSD") == "XAUUSD=X"


def test_resolve_symbol_passthrough_se_sconosciuto():
    """Se l'utente passa un ticker yfinance custom, lo accetta."""
    b = YFinanceBroker()
    assert b._resolve_symbol("MSFT") == "MSFT"


def test_timeframe_supportati():
    b = YFinanceBroker()
    period, interval = b._resolve_period_interval("M15")
    assert period == "60d"
    assert interval == "15m"


def test_timeframe_h4_richiede_resample():
    b = YFinanceBroker()
    period, interval = b._resolve_period_interval("H4")
    # H4 non è nativo yfinance: l'interval ritornato è None per indicare resample
    assert interval is None


def test_timeframe_invalido_solleva():
    b = YFinanceBroker()
    with pytest.raises(ValueError, match="Timeframe"):
        b._resolve_period_interval("M2")


def test_place_order_solleva_not_implemented():
    b = YFinanceBroker()
    order = Order(symbol="EURUSD", direction="long", size=0.1)
    with pytest.raises(NotImplementedError, match="read-only"):
        b.place_order(order)


def test_get_position_sempre_none():
    b = YFinanceBroker()
    assert b.get_position("EURUSD") is None


def test_get_info_ritorna_dummy():
    b = YFinanceBroker()
    info = b.get_info()
    assert info.name == "yfinance"
    assert info.is_paper is True
    assert info.balance == 0.0


def test_connect_non_idempotente_break():
    """connect() deve essere idempotente."""
    b = YFinanceBroker()
    b.connect()
    b.connect()  # non deve sollevare
    assert b.connected is True


# ---------------------------------------------------------------------------
# Test live (con rete) — si saltano se yfinance non disponibile/lento
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    "not config.getoption('--run-live', default=False)",
    reason="Richiede --run-live (flag custom)",
)
def test_get_market_data_eurusd_15m_live():
    b = YFinanceBroker()
    b.connect()
    df = b.get_market_data("EURUSD", timeframe="M15", bars=20)
    assert len(df) <= 20
    assert "close" in df.columns
    assert df["close"].iloc[-1] > 0


@pytest.mark.skipif(
    "not config.getoption('--run-live', default=False)",
    reason="Richiede --run-live (flag custom)",
)
def test_get_market_data_xauusd_usa_gc_live():
    b = YFinanceBroker()
    b.connect()
    df = b.get_market_data("XAUUSD", timeframe="M15", bars=20)
    assert len(df) > 0
    # Gold future: prezzo intorno a migliaia
    assert df["close"].iloc[-1] > 1000
