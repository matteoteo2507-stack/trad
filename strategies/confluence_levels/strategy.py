"""Strategia Confluence Levels — semiautomatica MT5/Telegram.

Logica meccanica:
1. L'utente compila `levels.yaml` ogni weekend con i livelli identificati a mano
   (S/R + S/D + Fibonacci in confluenza).
2. La strategia legge i livelli, applica filtri (sessione di Roma, news, RR, SL
   max) e per ogni livello vicino al prezzo corrente produce un `Signal`.
3. Il runner decide se mandare solo notifica (Fase A), piazzare un pending
   (Fase B), chiedere conferma Telegram (Fase C) o gestire BE post-fill (Fase D).

Tutti i flag e le soglie sono in `config.yaml`. Niente hardcoding.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time as dtime, timezone
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pandas as pd

from brokers.base import BrokerPosition
from notifiers._pip_table import get_pip_spec, price_delta_pips
from strategies._base import DataRequirement, Signal, StrategyBase

from .levels_loader import Level, load_levels

logger = logging.getLogger(__name__)


@dataclass
class LevelEvaluation:
    """Risultato della valutazione di un livello rispetto al prezzo corrente.

    `signal` è valorizzato solo se TUTTI i filtri passano. `reason` documenta
    sempre la decisione (utile per logging e dry-run CLI).
    """

    level: Level
    distance_pips: float
    passed: bool
    reason: str
    signal: Optional[Signal] = None


class ConfluenceLevelsStrategy(StrategyBase):
    """Strategia che monitora la prossimità a livelli weekly compilati a mano."""

    name = "confluence_levels"

    def __init__(self, config_path: Path | str):
        super().__init__(config_path=str(config_path))
        self._config_dir = Path(config_path).parent
        self._levels_path = self._config_dir / self.config["levels_file"]
        self._levels_cache: Optional[dict[str, list[Level]]] = None
        self._rome_tz = ZoneInfo("Europe/Rome")

    # ---- API pubblica StrategyBase --------------------------------------

    def get_required_data(self) -> DataRequirement:
        return DataRequirement(
            symbols=list(self.config["symbols"]),
            timeframe=self.config["timeframe"],
            lookback_bars=int(self.config["lookback_bars"]),
            indicators=[],
        )

    def should_enter(self, market_data: pd.DataFrame) -> Optional[Signal]:
        """Per uniformità con `StrategyBase`: restituisce il primo signal valido.

        Il workflow vero della Confluence è multi-livello multi-simbolo: usa
        `evaluate_all` dal runner. Questo metodo è un comodity per integrazione
        con i test e per orchestrator generici.
        """
        if market_data.empty:
            return None
        symbol = self._infer_symbol_from_market_data(market_data)
        if symbol is None:
            return None
        current_price = float(market_data["close"].iloc[-1])
        evaluations = self.evaluate_symbol(symbol, current_price)
        for ev in evaluations:
            if ev.passed and ev.signal is not None:
                return ev.signal
        return None

    def should_exit(self, market_data: pd.DataFrame, position: BrokerPosition) -> bool:
        # Confluence è solo notifica: nessuna gestione exit interna.
        return False

    # `manage_position` non è override: usa il default no-op di StrategyBase.
    # Confluence non gestisce posizioni perché non ne piazza.

    # ---- Logica multi-livello (usata dal runner) ------------------------

    def load_levels_now(self, force_reload: bool = False) -> dict[str, list[Level]]:
        if self._levels_cache is None or force_reload:
            self._levels_cache = load_levels(self._levels_path)
        return self._levels_cache

    def evaluate_symbol(
        self,
        symbol: str,
        current_price: float,
        now: Optional[datetime] = None,
        news_blocked: bool = False,
        already_notified_ids: Optional[set[str]] = None,
    ) -> list[LevelEvaluation]:
        """Valuta tutti i livelli del simbolo rispetto al prezzo corrente."""
        levels = self.load_levels_now().get(symbol, [])
        if not levels:
            return []

        now = now or datetime.now(timezone.utc)
        already = already_notified_ids or set()
        results: list[LevelEvaluation] = []

        for level in levels:
            ev = self._evaluate_level(
                level=level,
                current_price=current_price,
                now=now,
                news_blocked=news_blocked,
                already=already,
            )
            results.append(ev)
        return results

    # ---- Valutazione singolo livello ------------------------------------

    def _evaluate_level(
        self,
        level: Level,
        current_price: float,
        now: datetime,
        news_blocked: bool,
        already: set[str],
    ) -> LevelEvaluation:
        distance = price_delta_pips(level.symbol, level.price, current_price)

        # Dedup: già notificato oggi.
        notif_key = self._notif_key(level, now)
        if notif_key in already:
            return LevelEvaluation(level, distance, False, "già notificato oggi")

        # Sessione operativa (orario Roma).
        if not self._in_session(now):
            return LevelEvaluation(level, distance, False, "fuori sessione operativa")

        # News.
        if news_blocked:
            return LevelEvaluation(level, distance, False, "news high entro finestra")

        # Prossimità.
        threshold = float(self.config["proximity_alert_pips"])
        if distance > threshold:
            return LevelEvaluation(
                level, distance, False, f"distanza {distance:.1f} pip > {threshold}"
            )

        # TP esplicito necessario.
        if level.tp_target_price is None:
            return LevelEvaluation(level, distance, False, "tp_target_price mancante")

        # Calcola SL/TP coerenti col bias.
        sl_buffer = self._sl_buffer_pips(level)
        sl_price = self._compute_sl_price(level, sl_buffer)

        sl_distance = price_delta_pips(level.symbol, level.price, sl_price)
        max_sl = self._max_sl_pips(level.symbol)
        if max_sl is not None and sl_distance > max_sl:
            return LevelEvaluation(
                level,
                distance,
                False,
                f"SL {sl_distance:.1f} pip > max {max_sl} per {level.symbol}",
            )

        # RR vs TP esplicito.
        rr = abs(level.tp_target_price - level.price) / abs(level.price - sl_price)
        min_rr = float(self.config["min_rr"])
        if rr < min_rr:
            return LevelEvaluation(
                level, distance, False, f"RR {rr:.2f} < min_rr {min_rr}"
            )

        # Size è solo cosmetica nel payload Telegram (Confluence non piazza ordini).
        size = 0.1
        signal = Signal(
            direction=level.bias,
            size=size,
            sl=sl_price,
            tp=level.tp_target_price,
            confidence=self._confidence_from_confluence(level),
            note=(
                f"Livello {level.id} ({level.type}): {', '.join(level.confluence)}"
            ),
        )
        return LevelEvaluation(
            level=level,
            distance_pips=distance,
            passed=True,
            reason=f"prossimità {distance:.1f} pip, RR {rr:.2f}",
            signal=signal,
        )

    # ---- Utility --------------------------------------------------------

    def _max_sl_pips(self, symbol: str) -> Optional[float]:
        table = self.config.get("max_sl_pips") or {}
        # Match grezzo: prefisso (es. "EURUSD" copre "EURUSD.r")
        norm = symbol.upper().split(".")[0]
        for key, val in table.items():
            if norm.startswith(str(key).upper()):
                return float(val)
        return None

    def _sl_buffer_pips(self, level: Level) -> float:
        if level.sl_buffer_pips is not None:
            return level.sl_buffer_pips
        defaults = self.config.get("default_sl_buffer_pips") or {}
        norm = level.symbol.upper().split(".")[0]
        for key, val in defaults.items():
            if norm.startswith(str(key).upper()):
                return float(val)
        return 5.0  # fallback minimo, evita SL=livello

    def _compute_sl_price(self, level: Level, buffer_pips: float) -> float:
        spec = get_pip_spec(level.symbol)
        offset = buffer_pips * spec.pip_size
        # Long: SL sotto al livello. Short: SL sopra.
        return level.price - offset if level.bias == "long" else level.price + offset

    def _in_session(self, now: datetime) -> bool:
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        local = now.astimezone(self._rome_tz)
        sess = self.config["session_rome"]
        start = self._parse_hhmm(sess["start"])
        end = self._parse_hhmm(sess["end"])
        return start <= local.time() <= end

    @staticmethod
    def _parse_hhmm(value: str) -> dtime:
        h, m = value.split(":")
        return dtime(int(h), int(m))

    @staticmethod
    def _confidence_from_confluence(level: Level) -> int:
        """Confidence proporzionale al numero di confluenze (capped a 90)."""
        base = 50
        bonus = min(len(level.confluence) * 10, 40)
        return min(base + bonus, 90)

    def _notif_key(self, level: Level, now: datetime) -> str:
        """Chiave di dedup per le notifiche: levelId + giorno (UTC)."""
        d: date = now.astimezone(timezone.utc).date()
        return f"{level.id}|{d.isoformat()}"

    @staticmethod
    def _infer_symbol_from_market_data(market_data: pd.DataFrame) -> Optional[str]:
        """Helper per `should_enter`: legge il simbolo da attribute o colonna."""
        sym = getattr(market_data, "attrs", {}).get("symbol")
        if sym:
            return str(sym)
        if "symbol" in market_data.columns:
            return str(market_data["symbol"].iloc[-1])
        return None

    # ---- API helper per il runner ---------------------------------------

    def notif_key(self, level: Level, now: Optional[datetime] = None) -> str:
        """Pubblica per il runner: dedup persistence."""
        return self._notif_key(level, now or datetime.now(timezone.utc))

    def get_pending_order_payload(self, ev: LevelEvaluation) -> dict[str, Any]:
        """Costruisce il payload per `notifier.send_pending_order_alert`."""
        if ev.signal is None:
            raise ValueError("Evaluation senza signal — non chiamabile.")
        return {
            "level": {
                "id": ev.level.id,
                "price": ev.level.price,
                "type": ev.level.type,
                "confluence": ev.level.confluence,
            },
            "direction": "BUY" if ev.level.bias == "long" else "SELL",
            "symbol": ev.level.symbol,
            "sl": ev.signal.sl,
            "tp": ev.signal.tp,
            "rationale": ev.reason,
        }
