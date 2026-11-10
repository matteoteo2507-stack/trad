"""Data source per Confluence Auto.

Due backend:
- **MT5** (produzione VPS): `MetaTrader5` Python package, fornisce barre + volume
  reali del broker. Richiede `pip install MetaTrader5` e MT5 terminal in esecuzione.
- **yfinance** (dev locale): scarica D1/H4/H1 via Yahoo. `tick_volume` NON
  disponibile su yfinance per forex — POC su yfinance usa `Volume` se >0
  altrimenti tick-count costante (=1) come degenerate fallback.

Restituisce `pd.DataFrame` con colonne `open, high, low, close, volume`
indicizzato per timestamp UTC.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import pandas as pd

logger = logging.getLogger(__name__)

Timeframe = Literal["M15", "H1", "H4", "D1"]


# ---------------------------------------------------------------------------
# yfinance backend
# ---------------------------------------------------------------------------

_YF_INTERVAL = {"M15": "15m", "H1": "1h", "H4": "1h", "D1": "1d"}
# yfinance non offre H4 nativo → useremo H1 e ricampioneremo a H4.


def fetch_yfinance(ticker: str, timeframe: Timeframe, bars: int) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance non installato: pip install yfinance")

    interval = _YF_INTERVAL[timeframe]
    # yfinance ha vincoli sul `period` rispetto all'interval.
    # M15: max 60 giorni; H1: max 730 giorni; D1: nessun limite pratico.
    days_needed = {
        "M15": min(int(bars * 0.011) + 5, 59),
        "H1": min(int(bars / 24 * 1.5) + 5, 700),
        "H4": min(int(bars / 6 * 1.5) + 5, 700),
        "D1": int(bars * 1.6) + 10,
    }[timeframe]

    end = pd.Timestamp.now("UTC").tz_localize(None)
    start = end - pd.Timedelta(days=days_needed)
    df = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    if df.empty:
        raise RuntimeError(f"yfinance: nessun dato per {ticker} {timeframe}")

    # Flatten MultiIndex columns se presenti (multi-ticker download).
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df.columns = [c.lower() for c in df.columns]

    needed = ["open", "high", "low", "close"]
    df = df[needed + (["volume"] if "volume" in df.columns else [])].dropna()
    if "volume" not in df.columns:
        df["volume"] = 1.0
    # Forex yfinance ha volume=0 sempre → maschera come tick=1 (degenerate)
    if (df["volume"] == 0).all():
        df["volume"] = 1.0

    # Resample H1 → H4 se richiesto.
    if timeframe == "H4":
        df = (
            df.resample("4h", origin="start_day")
            .agg({"open": "first", "high": "max", "low": "min",
                  "close": "last", "volume": "sum"})
            .dropna()
        )

    # Tronca alle ultime `bars` righe.
    df = df.tail(bars).copy()
    # Forza index naive UTC.
    if df.index.tz is not None:
        df.index = df.index.tz_convert("UTC").tz_localize(None)
    return df


# ---------------------------------------------------------------------------
# MT5 backend
# ---------------------------------------------------------------------------

_MT5_TIMEFRAME_CONST: dict[Timeframe, int] = {}


def _init_mt5_constants() -> bool:
    """Importa lazy MetaTrader5. Restituisce True se disponibile."""
    global _MT5_TIMEFRAME_CONST
    if _MT5_TIMEFRAME_CONST:
        return True
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        return False
    _MT5_TIMEFRAME_CONST = {
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }
    return True


def fetch_mt5(symbol: str, timeframe: Timeframe, bars: int) -> pd.DataFrame:
    if not _init_mt5_constants():
        raise RuntimeError("MetaTrader5 Python package non installato")
    import MetaTrader5 as mt5  # type: ignore

    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() fallito: {mt5.last_error()}")

    try:
        utc_now = datetime.now(tz=timezone.utc)
        rates = mt5.copy_rates_from(symbol, _MT5_TIMEFRAME_CONST[timeframe], utc_now, bars)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"MT5: nessun dato per {symbol} {timeframe} ({mt5.last_error()})")
    finally:
        mt5.shutdown()

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_localize(None)
    df = df.set_index("time")
    # MT5 espone: open, high, low, close, tick_volume, real_volume, spread.
    # Per il forex usiamo tick_volume (proxy del volume vero, vedi
    # TRADING_PRINCIPLES.md §7).
    df["volume"] = df["tick_volume"]
    return df[["open", "high", "low", "close", "volume"]]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def fetch_ohlc(
    symbol_config: dict,
    timeframe: Timeframe,
    bars: int,
    *,
    prefer: str = "mt5",
) -> pd.DataFrame:
    """Fetch unificato: tenta `prefer`, cade in fallback sull'altro.

    Args:
        symbol_config: dict con keys `yfinance_ticker` e `mt5_symbol`.
        timeframe, bars: vedi backend specifico.
        prefer: "mt5" o "yfinance".

    Returns:
        DataFrame OHLC + volume indicizzato per timestamp UTC naive.
    """
    backends = ["mt5", "yfinance"] if prefer == "mt5" else ["yfinance", "mt5"]
    last_exc: Optional[Exception] = None
    for backend in backends:
        try:
            if backend == "mt5":
                if not _init_mt5_constants():
                    logger.info("MT5 non disponibile, salto a yfinance.")
                    continue
                return fetch_mt5(symbol_config["mt5_symbol"], timeframe, bars)
            else:
                return fetch_yfinance(symbol_config["yfinance_ticker"], timeframe, bars)
        except Exception as exc:
            logger.warning("Backend %s fallito per %s %s: %s",
                           backend, symbol_config, timeframe, exc)
            last_exc = exc
            continue
    raise RuntimeError(f"Tutti i backend hanno fallito: {last_exc}")
