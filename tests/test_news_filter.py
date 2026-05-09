"""Test del filtro news (CSV stub)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from strategies.confluence_levels.news_filter import is_blocked


def _write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "news.csv"
    p.write_text(content, encoding="utf-8")
    return p


def test_csv_inesistente_non_blocca(tmp_path):
    blocked, _ = is_blocked("EURUSD", csv_path=tmp_path / "missing.csv")
    assert blocked is False


def test_csv_solo_header_non_blocca(tmp_path):
    p = _write_csv(tmp_path, "datetime_utc,symbol,impact\n")
    blocked, _ = is_blocked("EURUSD", csv_path=p)
    assert blocked is False


def test_evento_high_entro_finestra_blocca(tmp_path):
    now = datetime(2026, 5, 9, 12, 0, tzinfo=timezone.utc)
    event_time = now + timedelta(minutes=15)
    p = _write_csv(
        tmp_path,
        f"datetime_utc,symbol,impact\n{event_time.strftime('%Y-%m-%d %H:%M')},USD,high\n",
    )
    blocked, reason = is_blocked("EURUSD", now=now, csv_path=p, block_minutes=30)
    assert blocked is True
    assert "USD" in reason


def test_evento_low_non_blocca_anche_se_vicino(tmp_path):
    now = datetime(2026, 5, 9, 12, 0, tzinfo=timezone.utc)
    event_time = now + timedelta(minutes=5)
    p = _write_csv(
        tmp_path,
        f"datetime_utc,symbol,impact\n{event_time.strftime('%Y-%m-%d %H:%M')},USD,low\n",
    )
    blocked, _ = is_blocked("EURUSD", now=now, csv_path=p, block_minutes=30)
    assert blocked is False


def test_evento_su_currency_non_correlata_non_blocca(tmp_path):
    now = datetime(2026, 5, 9, 12, 0, tzinfo=timezone.utc)
    event_time = now + timedelta(minutes=15)
    p = _write_csv(
        tmp_path,
        f"datetime_utc,symbol,impact\n{event_time.strftime('%Y-%m-%d %H:%M')},JPY,high\n",
    )
    blocked, _ = is_blocked("EURUSD", now=now, csv_path=p, block_minutes=30)
    assert blocked is False


def test_evento_passato_oltre_finestra_non_blocca(tmp_path):
    now = datetime(2026, 5, 9, 12, 0, tzinfo=timezone.utc)
    event_time = now - timedelta(minutes=60)
    p = _write_csv(
        tmp_path,
        f"datetime_utc,symbol,impact\n{event_time.strftime('%Y-%m-%d %H:%M')},USD,high\n",
    )
    blocked, _ = is_blocked("EURUSD", now=now, csv_path=p, block_minutes=30)
    assert blocked is False
