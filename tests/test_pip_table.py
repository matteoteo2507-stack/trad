"""Test della tabella pip-size."""

from __future__ import annotations

import pytest

from notifiers._pip_table import (
    format_price,
    get_pip_spec,
    price_delta_pct,
    price_delta_pips,
)


def test_eurusd_decimali_e_pip():
    spec = get_pip_spec("EURUSD")
    assert spec.decimals == 5
    assert spec.pip_size == 0.0001


def test_xauusd_decimali_e_pip():
    spec = get_pip_spec("XAUUSD")
    assert spec.decimals == 2
    assert spec.pip_size == 0.01


def test_usdjpy_pip_size():
    """USDJPY ha pip 0.01 (non 0.0001) per via del prezzo grande."""
    spec = get_pip_spec("USDJPY")
    assert spec.pip_size == 0.01


def test_simbolo_con_suffisso_avaTrade_normalizzato():
    """EURUSD.r → EURUSD."""
    spec = get_pip_spec("EURUSD.r")
    assert spec.decimals == 5


def test_simbolo_sconosciuto_usa_default():
    spec = get_pip_spec("ZZZZZZ")
    assert spec.decimals == 4


def test_format_price_eurusd():
    assert format_price("EURUSD", 1.0850123) == "1.08501"


def test_format_price_xau():
    assert format_price("XAUUSD", 2380.456) == "2380.46"


def test_pip_delta_eurusd():
    """1.0850 → 1.0820 = 30 pip su EURUSD."""
    assert price_delta_pips("EURUSD", 1.0850, 1.0820) == pytest.approx(30, rel=0.01)


def test_pip_delta_xau():
    """2380 → 2378 = 200 pip su XAU (pip = 0.01)."""
    assert price_delta_pips("XAUUSD", 2380.0, 2378.0) == pytest.approx(200, rel=0.01)


def test_pct_delta_segno_corretto():
    # SL sotto entry → delta negativo
    assert price_delta_pct(1.0850, 1.0800) < 0
    # TP sopra entry → delta positivo
    assert price_delta_pct(1.0850, 1.0950) > 0
