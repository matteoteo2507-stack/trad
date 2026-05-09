"""Sorgenti dati per lo Stock Selector: lista SP500 + storici via yfinance."""

from __future__ import annotations

import io
import logging
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def fetch_sp500_tickers(
    csv_url: str,
    fallback_tickers: list[str],
) -> list[str]:
    """Recupera la lista SP500 da GitHub Datasets, con fallback hardcoded.

    Replica `get_sp500_tickers_robust` del notebook V6.0. La normalizzazione
    `.` → `-` (BRK.B → BRK-B) per yfinance avviene nel chiamante.
    """
    try:
        logger.info("Scaricamento lista SP500 da %s", csv_url)
        resp = requests.get(csv_url, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")))
        tickers = df["Symbol"].tolist()
        logger.info("Lista SP500 ottenuta: %d ticker", len(tickers))
        return tickers
    except Exception as exc:  # rete, parsing, schema diverso → fallback
        logger.warning("Fetch SP500 fallito (%s). Uso lista di emergenza.", exc)
        return list(fallback_tickers)


def normalize_tickers_for_yfinance(tickers: list[str]) -> list[str]:
    """yfinance vuole `BRK-B` non `BRK.B`."""
    return [t.replace(".", "-") for t in tickers]


def download_history(
    tickers: list[str],
    benchmark: str,
    period: str,
    interval: str,
) -> pd.DataFrame:
    """Scarica gli storici OHLC con `yfinance.download` group_by ticker.

    Import pigro per non rendere yfinance una dipendenza hard del modulo
    (utile in test che non scaricano dati).
    """
    import yfinance as yf

    symbols = list(dict.fromkeys(tickers + [benchmark]))  # dedup preservando ordine
    logger.info(
        "Download storico: %d simboli, period=%s interval=%s", len(symbols), period, interval
    )
    return yf.download(
        symbols,
        period=period,
        interval=interval,
        progress=False,
        group_by="ticker",
        auto_adjust=True,
    )


def fetch_ticker_info(ticker: str) -> dict[str, Any]:
    """Wrapper su `yf.Ticker(t).info` con cattura errori. Restituisce {} se fallisce."""
    import yfinance as yf

    try:
        return yf.Ticker(ticker).info or {}
    except Exception as exc:
        logger.debug("Info non disponibili per %s: %s", ticker, exc)
        return {}
