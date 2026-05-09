"""Test offline del risk gate. Niente broker reali."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from brokers.base import BrokerPosition
from core.risk_gate import PortfolioState, validate_signal
from strategies._base import Signal


# Configurazione minima fissa per i test (replica `config/risk.yaml`).
RISK = {
    "max_drawdown_pct": 0.15,
    "max_daily_drawdown_pct": 0.05,
    "max_size_per_trade_pct": 0.02,
    "max_open_positions": 5,
    "max_positions_per_symbol": 1,
    "max_total_exposure_pct": 0.50,
    "min_reward_to_risk": 1.5,
    "max_consecutive_losses": 4,
    "cooldown_minutes_after_max_losses": 60,
}


def _open_position(symbol: str, size: float, current_price: float) -> BrokerPosition:
    return BrokerPosition(
        symbol=symbol,
        direction="long",
        size=size,
        entry_price=current_price,
        entry_time=datetime.utcnow(),
        current_price=current_price,
        unrealized_pnl=0.0,
        sl=None,
        tp=None,
    )


def _state(equity: float = 10_000, **kwargs) -> PortfolioState:
    return PortfolioState(equity=equity, initial_equity=equity, **kwargs)


# ---------------------------------------------------------------------------
# Casi positivi
# ---------------------------------------------------------------------------


def test_signal_valido_passa():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)  # RR=3
    ok, reason = validate_signal(s, "EURUSD", 1.0850, _state(), RISK)
    assert ok, reason
    assert reason == "ok"


# ---------------------------------------------------------------------------
# Drawdown
# ---------------------------------------------------------------------------


def test_drawdown_totale_blocca():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    state = PortfolioState(equity=8_000, initial_equity=10_000)  # 20% DD
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK)
    assert not ok
    assert "max_drawdown_pct" in reason


def test_drawdown_giornaliero_blocca():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    state = PortfolioState(equity=10_000, initial_equity=10_000, daily_pnl=-600)  # 6%
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK)
    assert not ok
    assert "max_daily_drawdown_pct" in reason


# ---------------------------------------------------------------------------
# Posizioni aperte
# ---------------------------------------------------------------------------


def test_max_open_positions_blocca():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    state = _state(open_positions=[_open_position(f"S{i}", 0.01, 100) for i in range(5)])
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK)
    assert not ok
    assert "max_open_positions" in reason


def test_max_per_symbol_blocca():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    state = _state(open_positions=[_open_position("EURUSD", 0.01, 1.085)])
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK)
    assert not ok
    assert "max_positions_per_symbol" in reason


# ---------------------------------------------------------------------------
# RR
# ---------------------------------------------------------------------------


def test_rr_insufficiente_blocca():
    # SL 50 pip, TP 50 pip → RR = 1.0 < 1.5
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0900)
    ok, reason = validate_signal(s, "EURUSD", 1.0850, _state(), RISK)
    assert not ok
    assert "reward_to_risk" in reason


# ---------------------------------------------------------------------------
# Size & esposizione
# ---------------------------------------------------------------------------


def test_size_eccessiva_blocca():
    # equity=10k, size=300 unità * 1.085 = 325$ notional → 3.25% > 2%
    s = Signal(direction="long", size=300, sl=1.0800, tp=1.0950)
    ok, reason = validate_signal(s, "EURUSD", 1.0850, _state(), RISK)
    assert not ok
    assert "max_size_per_trade_pct" in reason


def test_esposizione_totale_blocca():
    # 4 posizioni da 1300$ ciascuna = 5200$ notional su 10k equity → 52%.
    # Aggiungere una nuova posizione anche piccola fa scattare il limite 50%.
    state = _state(
        open_positions=[
            _open_position(f"S{i}", 1300, 1.0) for i in range(4)
        ]
    )
    s = Signal(direction="long", size=10, sl=1.0800, tp=1.0950)
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK)
    assert not ok
    assert "max_total_exposure_pct" in reason


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------


def test_cooldown_blocca_subito_dopo_max_losses():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    now = datetime.utcnow()
    state = _state(consecutive_losses=4, last_loss_time=now)
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK, now=now)
    assert not ok
    assert "cooldown" in reason


def test_cooldown_scaduto_lascia_passare():
    s = Signal(direction="long", size=0.01, sl=1.0800, tp=1.0950)
    now = datetime.utcnow()
    state = _state(
        consecutive_losses=4,
        last_loss_time=now - timedelta(minutes=61),
    )
    ok, reason = validate_signal(s, "EURUSD", 1.0850, state, RISK, now=now)
    assert ok, reason


# ---------------------------------------------------------------------------
# Properties di PortfolioState
# ---------------------------------------------------------------------------


def test_drawdown_zero_se_equity_uguale_o_superiore():
    assert PortfolioState(equity=10_000, initial_equity=10_000).drawdown_pct == 0
    assert PortfolioState(equity=11_000, initial_equity=10_000).drawdown_pct == 0


def test_total_exposure_calcolato_correttamente():
    state = _state(
        equity=10_000,
        open_positions=[_open_position("EURUSD", 1000, 1.0)],
    )
    assert state.total_exposure_pct == pytest.approx(0.10)
