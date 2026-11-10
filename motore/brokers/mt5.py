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
import re
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

    def get_bars_until(
        self, symbol: str, timeframe: str, end: datetime, count: int
    ) -> pd.DataFrame:
        """`count` barre che TERMINANO a `end` (incluso), andando indietro.

        Look-ahead-safe: per analizzare un ingresso passato si guardano solo le
        barre disponibili fino a quel momento. `end` va passato in tempo server
        del broker (vedi nota TZ in cima al file); il chiamante è responsabile
        dell'allineamento. Le colonne sono normalizzate come in `get_market_data`.
        """
        self._ensure_connected()
        tf_map = _build_timeframe_map(self._mt5)
        if timeframe not in tf_map:
            raise ValueError(
                f"Timeframe '{timeframe}' non supportato. Validi: {_TIMEFRAME_KEYS}"
            )
        sym = self._resolve_symbol(symbol)
        rates = self._mt5.copy_rates_from(sym, tf_map[timeframe], end, count)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"MT5 nessun dato per {sym} {timeframe} fino a {end}: {self._mt5.last_error()}"
            )
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")
        df = df.rename(columns={"tick_volume": "volume"})
        return df[["open", "high", "low", "close", "volume"]]

    def get_price(self, symbol: str) -> float:
        """Prezzo corrente (mid bid/ask) del simbolo. Usato dal gate anti-ritardo."""
        self._ensure_connected()
        sym = self._resolve_symbol(symbol)
        tick = self._mt5.symbol_info_tick(sym)
        if tick is None:
            raise RuntimeError(f"MT5 nessun tick per {sym}: {self._mt5.last_error()}")
        return float((tick.bid + tick.ask) / 2)

    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        self._ensure_connected()
        sym = self._resolve_symbol(symbol)
        positions = self._mt5.positions_get(symbol=sym)
        if not positions:
            return None
        # Su account netting c'è una sola posizione per simbolo; su hedging
        # restituiamo la prima (per la gestione multi-gamba usa get_positions()).
        return self._to_position(positions[0], symbol)

    def get_positions(self, symbol: str) -> list[BrokerPosition]:
        """Tutte le posizioni aperte sul simbolo, ognuna col proprio ticket.

        Su account HEDGING ogni gamba di un segnale è una posizione distinta:
        serve al signal copier per gestire (BE / close) le singole gambe.
        """
        self._ensure_connected()
        sym = self._resolve_symbol(symbol)
        positions = self._mt5.positions_get(symbol=sym)
        if not positions:
            return []
        return [self._to_position(p, symbol) for p in positions]

    def _to_position(self, p: Any, symbol: str) -> BrokerPosition:
        """Converte una posizione MT5 grezza in BrokerPosition (con ticket)."""
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
            ticket=int(p.ticket),
            magic=int(getattr(p, "magic", 0)),
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
        }
        if price is not None:
            request["price"] = price
        if order.stop_loss is not None:
            request["sl"] = float(order.stop_loss)
        if order.take_profit is not None:
            request["tp"] = float(order.take_profit)

        self._normalize_request(request, info)
        result = self._send_with_filling(request, info)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"MT5 order_send fallito retcode={getattr(result, 'retcode', None)} "
                f"comment={getattr(result, 'comment', None)} "
                f"last_error={self._mt5.last_error()} "
                f"(filling={request.get('type_filling')}, symbol={sym})"
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

    def modify_position_by_ticket(
        self,
        ticket: int,
        new_sl: Optional[float] = None,
        new_tp: Optional[float] = None,
    ) -> None:
        """Modifica SL/TP della posizione col ticket dato (account hedging).

        A differenza di `modify_position` (che opera sulla prima posizione del
        simbolo), agisce sulla posizione specifica: indispensabile quando più
        gambe insistono sullo stesso simbolo.
        """
        self._ensure_connected()
        positions = self._mt5.positions_get(ticket=int(ticket))
        if not positions:
            raise RuntimeError(f"Nessuna posizione MT5 col ticket {ticket}")
        p = positions[0]
        request = {
            "action": self._mt5.TRADE_ACTION_SLTP,
            "position": int(ticket),
            "symbol": p.symbol,
            "sl": float(new_sl) if new_sl is not None else float(p.sl or 0),
            "tp": float(new_tp) if new_tp is not None else float(p.tp or 0),
        }
        self._normalize_request(request, self._mt5.symbol_info(p.symbol))
        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"MT5 modify per-ticket {ticket} fallito "
                f"retcode={getattr(result, 'retcode', '?')}"
            )
        logger.info("MT5 SL/TP modificati ticket=%s sl=%s tp=%s", ticket, new_sl, new_tp)

    def close_position_by_ticket(self, ticket: int) -> None:
        """Chiude la singola posizione col ticket dato (account hedging).

        Invia un deal opposto con `position=ticket`, così MT5 chiude proprio
        quella gamba e non un'altra posizione dello stesso simbolo.
        """
        self._ensure_connected()
        positions = self._mt5.positions_get(ticket=int(ticket))
        if not positions:
            logger.info("close per-ticket: ticket %s già chiuso/assente", ticket)
            return
        p = positions[0]
        is_long = p.type == self._mt5.POSITION_TYPE_BUY
        otype = self._mt5.ORDER_TYPE_SELL if is_long else self._mt5.ORDER_TYPE_BUY
        tick = self._mt5.symbol_info_tick(p.symbol)
        info = self._mt5.symbol_info(p.symbol)
        request = {
            "action": self._mt5.TRADE_ACTION_DEAL,
            "symbol": p.symbol,
            "volume": float(p.volume),
            "type": otype,
            "position": int(ticket),
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "close_leg",
            "type_time": self._mt5.ORDER_TIME_GTC,
        }
        if tick is not None:
            request["price"] = float(tick.bid if is_long else tick.ask)
        self._normalize_request(request, info)
        result = self._send_with_filling(request, info)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(
                f"MT5 close per-ticket {ticket} fallito "
                f"retcode={getattr(result, 'retcode', None)} last_error={self._mt5.last_error()}"
            )
        logger.info("MT5 posizione chiusa ticket=%s vol=%s", ticket, p.volume)

    # ---- Helper interni -------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MT5 non connesso. Chiamare connect() prima.")

    def _filling_candidates(self, info: Any) -> list[int]:
        """Ordine di `type_filling` da provare: prima quelli dichiarati dal simbolo, poi tutti.

        Alcune build del pacchetto `MetaTrader5` NON espongono le costanti
        `SYMBOL_FILLING_*`: usiamo i valori del bitmask (FOK=1, IOC=2). Il broker
        a volte rifiuta un filling con `result=None` o retcode 10030
        (INVALID_FILL): in quei casi proviamo il successivo.
        """
        mt5 = self._mt5
        fm = getattr(info, "filling_mode", 0) if info is not None else 0
        order: list[int] = []
        if fm & 1:  # SYMBOL_FILLING_FOK
            order.append(mt5.ORDER_FILLING_FOK)
        if fm & 2:  # SYMBOL_FILLING_IOC
            order.append(mt5.ORDER_FILLING_IOC)
        # Fallback: includi comunque tutti i modi, senza duplicati.
        for f in (mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC):
            if f not in order:
                order.append(f)
        return order

    def _send_with_filling(self, request: dict, info: Any) -> Any:
        """`order_send` provando i filling supportati finché uno non viene accettato."""
        result = None
        for filling in self._filling_candidates(info):
            request["type_filling"] = filling
            result = self._mt5.order_send(request)
            rc = getattr(result, "retcode", None)
            if result is not None and rc == self._mt5.TRADE_RETCODE_DONE:
                return result
            # Riprova con un altro filling SOLO se è (probabile) errore di filling.
            if not (result is None or rc == 10030):  # 10030 = TRADE_RETCODE_INVALID_FILL
                return result
        return result

    @staticmethod
    def _safe_comment(text: str) -> str:
        """Comment MT5-safe: solo `[A-Za-z0-9_-]`, max 31 char.

        MT5 rifiuta i comment con spazi/parentesi/virgole ecc.
        (`-2 'Invalid comment argument'`): i run di caratteri non ammessi
        diventano `_`.
        """
        cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", text or "")
        return cleaned.strip("_")[:31]

    def _norm_volume(self, volume: float, info: Any) -> float:
        """Allinea il volume al passo del simbolo e lo clampa a [min, max]."""
        step = float(getattr(info, "volume_step", 0.01) or 0.01)
        vmin = float(getattr(info, "volume_min", step) or step)
        vmax = float(getattr(info, "volume_max", 1e9) or 1e9)
        v = round(round(volume / step) * step, 8)
        return max(vmin, min(v, vmax))

    def _normalize_request(self, request: dict, info: Any) -> dict:
        """Rende il request MT5-safe e previene i rifiuti più comuni di order_send:
        comment ripulito, prezzi ai `digits` del simbolo, volume al passo (min/max).
        """
        if "comment" in request:
            request["comment"] = self._safe_comment(request.get("comment", ""))
        if info is None:
            return request
        digits = int(getattr(info, "digits", 2) or 2)
        for k in ("price", "sl", "tp"):
            if request.get(k) is not None:
                request[k] = round(float(request[k]), digits)
        if "volume" in request:
            request["volume"] = self._norm_volume(float(request["volume"]), info)
        return request

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
