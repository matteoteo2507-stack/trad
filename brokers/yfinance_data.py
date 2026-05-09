"""Broker read-only basato su yfinance per dati di mercato (no esecuzione).

Pattern Null Object: implementa l'interfaccia `BrokerBase` ma fa raise su tutti
i metodi di esecuzione (`place_order`, `close_position`, `get_position`,
`get_info`). È pensato per strategie SOLO-NOTIFICA come Confluence Levels,
che hanno bisogno solo di prezzi correnti per calcolare la prossimità a
livelli compilati a mano.

Uso:
    from brokers.yfinance_data import YFinanceBroker

    broker = YFinanceBroker()
    broker.connect()
    df = broker.get_market_data("EURUSD", timeframe="M15", bars=200)
    # df["close"].iloc[-1] è il prezzo più recente

Mapping simboli (yfinance ticker convention):
    EURUSD → EURUSD=X
    GBPUSD → GBPUSD=X
    USDJPY → USDJPY=X
    XAUUSD → GC=F (Gold front-month future; XAUUSD=X non è disponibile su Yahoo)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from .base import BrokerBase, BrokerInfo, BrokerPosition, Order

logger = logging.getLogger(__name__)


# Mapping simbolo "trading" → ticker yfinance.
# Override possibile via costruttore per simboli aggiuntivi.
_DEFAULT_SYMBOL_MAP: dict[str, str] = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "AUDUSD": "AUDUSD=X",
    # Gold: useremo il future Comex perché lo spot XAUUSD=X non è disponibile.
    "XAUUSD": "GC=F",
    # Argento spot non disponibile, future Comex alternativo
    "XAGUSD": "SI=F",
}


# Mapping timeframe stringa → intervallo yfinance.
# yfinance accetta: 1m, 2m, 5m, 15m, 30m, 60m/1h, 90m, 1d, 5d, 1wk.
# Per timeframe sopra D1 yfinance limita molto la storia gratis.
_TIMEFRAME_MAP: dict[str, str] = {
    "M1": "1m",
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "H4": None,  # yfinance non supporta H4 nativo: ricampionamento da H1
    "D1": "1d",
    "W1": "1wk",
}


# Mapping timeframe → period (range) richiesto.
# yfinance richiede period più ampio per timeframe più alti.
_PERIOD_FOR_BARS: dict[str, str] = {
    "M1": "5d",
    "M5": "5d",
    "M15": "60d",
    "M30": "60d",
    "H1": "60d",
    "H4": "60d",
    "D1": "1y",
    "W1": "5y",
}


class YFinanceBroker(BrokerBase):
    """Read-only data source. Non esegue ordini, non gestisce posizioni."""

    name = "yfinance"

    def __init__(self, symbol_overrides: Optional[dict[str, str]] = None):
        super().__init__(paper_mode=True)  # è di fatto "paper" in senso stretto
        self.symbol_map = dict(_DEFAULT_SYMBOL_MAP)
        if symbol_overrides:
            self.symbol_map.update(symbol_overrides)

    # ---- Connessione ----------------------------------------------------

    def connect(self) -> None:
        """Idempotente. Verifica solo che yfinance sia importabile."""
        if self._connected:
            return
        try:
            import yfinance as yf  # noqa: F401  # import-time check
        except ImportError as exc:
            raise RuntimeError(
                "Pacchetto `yfinance` non installato. "
                "Eseguire `pip install yfinance`."
            ) from exc
        self._connected = True
        logger.info("yfinance broker connesso (read-only)")

    def disconnect(self) -> None:
        self._connected = False

    # ---- Dati di mercato -----------------------------------------------

    def get_market_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int,
    ) -> pd.DataFrame:
        """Scarica OHLCV da yfinance per il simbolo + timeframe richiesti.

        Restituisce DataFrame con colonne `["open", "high", "low", "close", "volume"]`
        indicizzato per datetime UTC (allineato col contratto BrokerBase).
        """
        self._ensure_connected()
        import yfinance as yf

        yf_ticker = self._resolve_symbol(symbol)
        period, interval = self._resolve_period_interval(timeframe)

        if interval is None:
            # Timeframe non supportato direttamente: ricampiono da H1.
            base_df = self._fetch_raw(yf_ticker, period, "1h")
            df = self._resample(base_df, target=timeframe)
        else:
            df = self._fetch_raw(yf_ticker, period, interval)

        if len(df) > bars:
            df = df.tail(bars)
        return df

    def _fetch_raw(self, yf_ticker: str, period: str, interval: str) -> pd.DataFrame:
        import yfinance as yf

        df = yf.Ticker(yf_ticker).history(period=period, interval=interval)
        if df.empty:
            raise RuntimeError(
                f"yfinance: nessun dato per {yf_ticker} period={period} interval={interval}"
            )
        # Standardizza nomi colonne (lowercase) e indice tz UTC.
        df = df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        # Volume su forex spot di yfinance è sempre 0; lasciamo per uniformità.
        df = df[["open", "high", "low", "close", "volume"]]
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        return df

    @staticmethod
    def _resample(df: pd.DataFrame, target: str) -> pd.DataFrame:
        """Ricampiona a un timeframe non nativo (es. H4)."""
        rule = {"H4": "4h"}.get(target)
        if rule is None:
            raise ValueError(f"Resampling non supportato per timeframe {target}")
        agg = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
        return df.resample(rule, label="right", closed="right").agg(agg).dropna()

    # ---- Account info / Posizioni / Ordini (Null Object) ----------------

    def get_info(self) -> BrokerInfo:
        # yfinance non ha account: ritorniamo info "vuote" per compatibilità con
        # `PortfolioState.from_brokers` se mai venisse chiamato.
        return BrokerInfo(
            name="yfinance",
            account_id="N/A",
            currency="USD",
            balance=0.0,
            equity=0.0,
            is_paper=True,
        )

    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        """yfinance non gestisce posizioni: sempre None."""
        return None

    def place_order(self, order: Order) -> str:
        raise NotImplementedError(
            "YFinanceBroker è read-only: non piazza ordini. "
            "La Confluence è solo notifica per design."
        )

    def close_position(self, position: BrokerPosition) -> None:
        raise NotImplementedError("YFinanceBroker è read-only: non chiude posizioni.")

    # ---- Helper interni -------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("YFinanceBroker non connesso. Chiamare connect() prima.")

    def _resolve_symbol(self, symbol: str) -> str:
        """Map simbolo trading → ticker yfinance (es. EURUSD → EURUSD=X)."""
        norm = symbol.upper().split(".")[0]
        if norm in self.symbol_map:
            return self.symbol_map[norm]
        # Fallback: se l'utente passa già un ticker yfinance valido lo accetta.
        return symbol

    def _resolve_period_interval(self, timeframe: str) -> tuple[str, Optional[str]]:
        if timeframe not in _TIMEFRAME_MAP:
            raise ValueError(
                f"Timeframe '{timeframe}' non supportato. Validi: {sorted(_TIMEFRAME_MAP.keys())}"
            )
        period = _PERIOD_FOR_BARS[timeframe]
        interval = _TIMEFRAME_MAP[timeframe]
        return period, interval
