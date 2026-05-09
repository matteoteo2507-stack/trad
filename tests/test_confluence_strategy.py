"""Test della strategia Confluence Levels (filtri + proximity + adapter)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from strategies.confluence_levels.strategy import ConfluenceLevelsStrategy


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CONFIG_TEMPLATE = """
symbols: [EURUSD, XAUUSD]
timeframe: M15
lookback_bars: 200

proximity_alert_pips: 15
min_rr: 3.0
max_sl_pips:
  EURUSD: 30
  XAUUSD: 200
default_sl_buffer_pips:
  EURUSD: 5
  XAUUSD: 30

session_rome:
  start: "00:00"
  end: "23:59"

news_block_minutes: 30
levels_file: "levels.yaml"
poll_interval_seconds: 60
default_valid_minutes: 240
state_dir: "data"
"""

LEVELS_TEMPLATE = """
EURUSD:
  - id: "L1"
    price: 1.08500
    type: support
    confluence: [SR_weekly, SD_H4, Fib_618]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.09500
"""


@pytest.fixture
def strategy_dir(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    (tmp_path / "levels.yaml").write_text(LEVELS_TEMPLATE, encoding="utf-8")
    return tmp_path


@pytest.fixture
def strategy(strategy_dir: Path) -> ConfluenceLevelsStrategy:
    return ConfluenceLevelsStrategy(config_path=strategy_dir / "config.yaml")


# ---------------------------------------------------------------------------
# Proximity
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime(2026, 5, 5, 10, 0, tzinfo=timezone.utc)


def test_proximity_passa_a_10_pip(strategy):
    evals = strategy.evaluate_symbol("EURUSD", current_price=1.08600, now=_now())
    assert len(evals) == 1
    ev = evals[0]
    assert ev.passed
    assert ev.signal is not None
    # SL = 1.0850 - 5 pip = 1.08450
    assert ev.signal.sl == pytest.approx(1.08450, abs=1e-4)
    assert ev.signal.tp == 1.09500
    assert ev.signal.direction == "long"


def test_proximity_blocca_a_50_pip(strategy):
    evals = strategy.evaluate_symbol("EURUSD", current_price=1.09000, now=_now())
    assert len(evals) == 1
    assert not evals[0].passed
    assert "distanza" in evals[0].reason


# ---------------------------------------------------------------------------
# Filtri
# ---------------------------------------------------------------------------


def test_news_blocca(strategy):
    evals = strategy.evaluate_symbol(
        "EURUSD", current_price=1.08600, now=_now(), news_blocked=True
    )
    assert not evals[0].passed
    assert "news" in evals[0].reason


def test_dedup_blocca(strategy):
    levels = strategy.load_levels_now()["EURUSD"]
    key = strategy.notif_key(levels[0], _now())
    evals = strategy.evaluate_symbol(
        "EURUSD",
        current_price=1.08600,
        now=_now(),
        already_notified_ids={key},
    )
    assert not evals[0].passed
    assert "notificato" in evals[0].reason


def test_fuori_sessione_blocca(tmp_path):
    cfg_text = CONFIG_TEMPLATE.replace(
        'start: "00:00"\n  end: "23:59"',
        'start: "09:00"\n  end: "18:00"',
    )
    cfg = tmp_path / "config.yaml"
    cfg.write_text(cfg_text, encoding="utf-8")
    (tmp_path / "levels.yaml").write_text(LEVELS_TEMPLATE, encoding="utf-8")
    strategy = ConfluenceLevelsStrategy(config_path=cfg)

    # 03:00 UTC = 05:00 Roma → fuori sessione
    early_morning = datetime(2026, 5, 5, 3, 0, tzinfo=timezone.utc)
    evals = strategy.evaluate_symbol("EURUSD", current_price=1.08600, now=early_morning)
    assert not evals[0].passed
    assert "sessione" in evals[0].reason


def test_rr_insufficiente_blocca(tmp_path):
    """TP troppo vicino al livello → RR < 3 → skip."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    levels_short_tp = """
EURUSD:
  - id: "L1"
    price: 1.08500
    type: support
    confluence: [SR_weekly, SD_H4, Fib_618]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.08600
"""
    (tmp_path / "levels.yaml").write_text(levels_short_tp, encoding="utf-8")
    strategy = ConfluenceLevelsStrategy(config_path=cfg)

    evals = strategy.evaluate_symbol("EURUSD", current_price=1.08600, now=_now())
    assert not evals[0].passed
    assert "RR" in evals[0].reason


def test_sl_eccede_max_blocca(tmp_path):
    """SL buffer enorme → distanza SL > max_sl_pips → skip."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    levels_huge_buffer = """
EURUSD:
  - id: "L1"
    price: 1.08500
    type: support
    confluence: [SR_weekly, SD_H4, Fib_618]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.20000
    sl_buffer_pips: 50
"""
    (tmp_path / "levels.yaml").write_text(levels_huge_buffer, encoding="utf-8")
    strategy = ConfluenceLevelsStrategy(config_path=cfg)

    evals = strategy.evaluate_symbol("EURUSD", current_price=1.08600, now=_now())
    assert not evals[0].passed
    assert "SL" in evals[0].reason


def test_tp_mancante_blocca(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    levels_no_tp = """
EURUSD:
  - id: "L1"
    price: 1.08500
    type: support
    confluence: [SR_weekly, SD_H4, Fib_618]
    bias: long
    valid_until: 2099-12-31
"""
    (tmp_path / "levels.yaml").write_text(levels_no_tp, encoding="utf-8")
    strategy = ConfluenceLevelsStrategy(config_path=cfg)

    evals = strategy.evaluate_symbol("EURUSD", current_price=1.08600, now=_now())
    assert not evals[0].passed
    assert "tp_target_price" in evals[0].reason


# ---------------------------------------------------------------------------
# manage_position (post-pivot 2026-05-05): Confluence è solo notifica.
# `manage_position` resta ereditato da StrategyBase con default no-op.
# ---------------------------------------------------------------------------


def test_manage_position_default_noop(strategy):
    """Confluence non gestisce posizioni: usa il default di StrategyBase."""
    import pandas as pd

    from brokers.base import BrokerPosition

    md = pd.DataFrame({"close": [1.09100]})
    pos = BrokerPosition(
        symbol="EURUSD",
        direction="long",
        size=0.1,
        entry_price=1.08500,
        entry_time=datetime.now(timezone.utc),
        current_price=1.09100,
        unrealized_pnl=60.0,
        sl=1.08400,
        tp=1.09500,
    )
    assert strategy.manage_position(md, pos) is None
