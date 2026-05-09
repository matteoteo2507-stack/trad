"""Broker MetaTrader 5 — implementazione operativa per Stage 2.

Libreria: `MetaTrader5` (pacchetto MetaQuotes ufficiale, solo Windows).
Richiede il terminale MT5 installato e in esecuzione, autenticato sul demo
indicato (vedi `.env`, `MT5_DEMO1_*`).

Note:
- L'import di `MetaTrader5` è pigro nei metodi: il file resta importabile
  anche su sistemi non-Windows (utile per i test CI). Sollevare un errore
  esplicito se si prova davvero a operare senza la libreria.
- Symbol mapping: AvaTrade usa nomi standard ("EURUSD", "XAUUSD"). Eventuali
  suffissi sono passati dal config (`mt5.symbol_suffix`).
- Server time MT5 è broker-dependent (AvaTrade = EET). I caller che fanno
  filtri di sessione devono convertire in `Europe/Rome` esplicitamente.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from .base import BrokerBase, BrokerInfo, BrokerPosition, Order

logger = logging.getLogger(__name__)


# Mapping timeframe stringa → costante MetaTrader5. Costruito on-demand
# perché richiede l'import della libreria.
_TIMEFRAME_KEYS = ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1")


def _import_mt5() -> Any:
    """Import pigro di MetaTrader5 con messaggio diagnostico se mancante."""
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Pacchetto `MetaTrader5` non installato. "
            "Eseguire `pip install MetaTrader5` (richiede Windows + terminale MT5)."
        ) from exc
    return mt5


def _build_timeframe_map(mt5: Any) -> dict[str, int]:
    return {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
    }


class MT5Broker(BrokerBase):
    """Broker MetaTrader 5 (paper-by-nature: account demo)."""

    name = "mt5"

    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        terminal_path: Optional[str] = None,
        symbol_suffix: str = "",
        symbol_overrides: Optional[dict[str, str]] = None,
        deviation: int = 20,
        magic: int = 26000,
    ):
        super().__init__(paper_mode=True)  # demo MT5 sono già paper
        self.login = int(login)
        self.password = password
        self.server = server
        self.terminal_path = terminal_path
        self.symbol_suffix = symbol_suffix
        self.symbol_overrides = symbol_overrides or {}
        self.deviation = deviation
        self.magic = magic
        self._mt5: Any = None

    # ---- Connessione ----------------------------------------------------

    def connect(self) -> None:
        if self._connected:
            return
        mt5 = _import_mt5()
        init_kwargs: dict[str, Any] = {
            "login": self.login,
            "password": self.password,
            "server": self.server,
        }
        if self.terminal_path:
            init_kwargs["path"] = self.terminal_path
        if not mt5.initialize(**init_kwargs):
            err = mt5.last_error()
            raise RuntimeError(f"MT5 initialize fallito: {err}")
        self._mt5 = mt5
        self._connected = True
        logger.info(
            "MT5 connesso: login=%s server=%s path=%s",
            self.login,
            self.server,
            self.terminal_path or "default",
        )

    def disconnect(self) -> None:
        if not self._connected:
            return
        try:
            self._mt5.shutdown()
        finally:
            self._mt5 = None
            self._connected = False
            logger.info("MT5 disconnesso.")

    # ---- Lookup info ----------------------------------------------------

    def _resolve_symbol(self, symbol: str) -> str:
        """Applica overrides → suffix per ottenere il simbolo broker-specifico."""
        if symbol in self.symbol_overrides:
            return self.symbol_overrides[symbol]
        return f"{symbol}{self.symbol_suffix}"

    def get_info(self) -> BrokerInfo:
        self._ensure_connected()
        acc = self._mt5.account_info()
        if acc is None:
            raise RuntimeError(f"MT5 account_info None: {self._mt5.last_error()}")
        return BrokerInfo(
            name=self.name,
            account_id=str(acc.login),
            currency=acc.currency,
            balance=float(acc.balance),
            equity=float(acc.equity),
            is_paper=True,
        )

    def get_market_data(
        self, symbol: str, timeframe: str, bars: int
    ) -> pd.DataFrame:
        self._ensure_connected()
        tf_map = _build_timeframe_map(self._mt5)
        if timeframe not in tf_map:
            raise ValueError(
                f"Timeframe '{timeframe}' non supportato. Validi: {_TIMEFRAME_KEYS}"
            )
        sym = self._resolve_symbol(symbol)
        rates = self._mt5.copy_rates_from_pos(sym, tf_map[timeframe], 0, bars)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"MT5 nessun dato per {sym} {timeframe}: {self._mt5.last_error()}"
            )
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")
        # Normalizza colonne al contratto BrokerBase
        df = df.rename(columns={"tick_volume": "volume"})
        return df[["open", "high", "low", "close", "volume"]]

    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        self._ensure_connected()
        sym = self._resolve_symbol(symbol)
        positions = self._mt5.positions_get(symbol=sym)
        if not positions:
            return None
        # Una sola posizione per simbolo per convenzione (vedi risk.yaml).
        p = positions[0]
        direction = "long" if p.type == self._mt5.POSITION_TYPE_BUY else "short"
        return BrokerPosition(
            symbol=symbol,
            direction=direction,
            size=float(p.volume),
            entry_price=float(p.price_open),
            entry_time=datetime.fromtimestamp(p.time),
            current_price=float(p.price_current),
            unrealized_pnl=float(p.profit),
            sl=float(p.sl) if p.sl else None,
            tp=float(p.tp) if p.tp else None,
        )

    # ---- Ordini ---------------------------------------------------------

    def place_order(self, order: Order) -> str:
        self._ensure_connected()
        sym = self._resolve_symbol(order.symbol)
        info = self._mt5.symbol_info(sym)
        if info is None:
            raise RuntimeError(f"Simbolo MT5 sconosciuto: {sym}")
        if not info.visible:
            self._mt5.symbol_select(sym, True)

        action_const, order_type_const = self._order_constants(order)
        price = self._order_price(order, info)

        request = {
            "action": action_const,
            "symbol": sym,
            "volume": float(order.size),
            "type": order_type_const,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": (order.note or "")[:31],  # MT5 limita comment a 31 char
            "type_time": self._mt5.ORDER_TIME_GTC,
            "type_filling": self._mt5.ORDER_FILLING_IOC,
        }
        if price is not None:
            request["price"] = price
        if order.stop_loss is not None:
            request["sl"] = float(order.stop_loss)
        if order.take_profit is not None:
            request["tp"] = float(order.take_profit)

        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"MT5 order_send fallito retcode={getattr(result, 'retcode', '?')} "
                f"comment={getattr(result, 'comment', '?')}"
            )
        order_id = str(result.order or result.deal)
        logger.info(
            "MT5 ordine eseguito: %s %s %s vol=%s id=%s",
            order.order_type,
            order.direction,
            sym,
            order.size,
            order_id,
        )
        return order_id

    def close_position(self, position: BrokerPosition) -> None:
        self._ensure_connected()
        sym = self._resolve_symbol(position.symbol)
        opposite = "short" if position.direction == "long" else "long"
        close_order = Order(
            symbol=position.symbol,
            direction=opposite,
            size=position.size,
            order_type="market",
            note="close_position",
        )
        # Per chiusure usiamo direttamente il deal rovesciato.
        self.place_order(close_order)
        logger.info("MT5 chiusura posizione %s direzione=%s", sym, position.direction)

    def modify_position(
        self,
        position: BrokerPosition,
        new_sl: Optional[float] = None,
        new_tp: Optional[float] = None,
    ) -> None:
        """Modifica SL/TP di una posizione esistente. Usato dal BE management."""
        self._ensure_connected()
        sym = self._resolve_symbol(position.symbol)
        positions = self._mt5.positions_get(symbol=sym)
        if not positions:
            raise RuntimeError(f"Nessuna posizione su {sym} da modificare")
        ticket = positions[0].ticket

        request = {
            "action": self._mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": sym,
            "sl": float(new_sl) if new_sl is not None else float(position.sl or 0),
            "tp": float(new_tp) if new_tp is not None else float(position.tp or 0),
        }
        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"MT5 modify SL/TP fallito retcode={getattr(result, 'retcode', '?')}"
            )
        logger.info(
            "MT5 SL/TP modificati su %s: sl=%s tp=%s", sym, new_sl, new_tp
        )

    # ---- Helper interni -------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MT5 non connesso. Chiamare connect() prima.")

    def _order_constants(self, order: Order) -> tuple[int, int]:
        """Restituisce `(action, order_type)` per `order_send`."""
        mt5 = self._mt5
        ot = order.order_type
        if ot == "market":
            action = mt5.TRADE_ACTION_DEAL
            otype = (
                mt5.ORDER_TYPE_BUY if order.direction == "long"
                else mt5.ORDER_TYPE_SELL
            )
            return action, otype
        if ot == "limit":
            action = mt5.TRADE_ACTION_PENDING
            otype = (
                mt5.ORDER_TYPE_BUY_LIMIT if order.direction == "long"
                else mt5.ORDER_TYPE_SELL_LIMIT
            )
            return action, otype
        if ot == "stop":
            action = mt5.TRADE_ACTION_PENDING
            otype = (
                mt5.ORDER_TYPE_BUY_STOP if order.direction == "long"
                else mt5.ORDER_TYPE_SELL_STOP
            )
            return action, otype
        raise ValueError(f"order_type non supportato: {ot}")

    def _order_price(self, order: Order, info: Any) -> Optional[float]:
        """Prezzo da inserire in `request['price']`."""
        if order.order_type == "market":
            tick = self._mt5.symbol_info_tick(info.name)
            if tick is None:
                return None
            return float(tick.ask if order.direction == "long" else tick.bid)
        return float(order.limit_price) if order.limit_price is not None else None
