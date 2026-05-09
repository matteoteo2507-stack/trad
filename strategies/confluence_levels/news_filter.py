"""Filtro news basato su `data/news_calendar.csv`.

Stub per Stage 2: il CSV è committato vuoto (solo header) ed è popolato a mano
dall'utente per il testing. In Stage 5 verrà sostituito dall'integrazione con
worldmonitor.

Formato CSV atteso:
    datetime_utc,symbol,impact
    2026-05-09 12:30,USD,high
    2026-05-09 14:00,EUR,medium

Il match symbol→evento è semplice prefisso: per EURUSD bloccano sia eventi
con symbol="USD" sia "EUR".
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = Path(__file__).parent.parent.parent / "data" / "news_calendar.csv"


def is_blocked(
    symbol: str,
    now: Optional[datetime] = None,
    block_minutes: int = 30,
    csv_path: Path | str = DEFAULT_CSV_PATH,
    impact_threshold: str = "high",
) -> tuple[bool, str]:
    """Restituisce (blocked, reason). CSV vuoto/mancante → False (non blocca)."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return False, "no news calendar file"

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        return False, "empty news calendar"
    except Exception as exc:
        logger.warning("Errore lettura news calendar: %s", exc)
        return False, "news calendar unreadable"

    if df.empty:
        return False, "no events"

    required = {"datetime_utc", "symbol", "impact"}
    missing = required - set(df.columns)
    if missing:
        logger.warning("news calendar columns mancanti: %s", missing)
        return False, "schema invalid"

    df = df.copy()
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["datetime_utc"])
    df["impact"] = df["impact"].astype(str).str.lower()

    threshold_severity = _impact_severity(impact_threshold)
    upper_bound = now + timedelta(minutes=block_minutes)
    lower_bound = now - timedelta(minutes=block_minutes)

    sym_upper = symbol.upper()
    for _, row in df.iterrows():
        if _impact_severity(row["impact"]) < threshold_severity:
            continue
        # match grezzo: il currency code deve apparire nel symbol del trader.
        currency = str(row["symbol"]).upper()
        if currency not in sym_upper:
            continue
        ts = row["datetime_utc"].to_pydatetime()
        if lower_bound <= ts <= upper_bound:
            return True, (
                f"news {row['impact']} su {currency} alle {ts.isoformat()} "
                f"(±{block_minutes}min da now)"
            )

    return False, "no relevant news in window"


_SEVERITY = {"low": 1, "medium": 2, "high": 3}


def _impact_severity(impact: str) -> int:
    return _SEVERITY.get(str(impact).lower(), 0)
