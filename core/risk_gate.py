"""Risk gate: filtro centralizzato che valida ogni Signal contro `config/risk.yaml`.

Il gate non conosce broker o notifier: riceve uno snapshot del portafoglio
(`PortfolioState`) e una `Signal`, restituisce ok/not-ok con motivazione.

Il `PortfolioState` lo costruisce il runner aggregando i broker attivi via
`PortfolioState.from_brokers([...])`. Questo evita che un broker debba sapere
dell'esistenza di altri broker.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from brokers.base import BrokerBase, BrokerPosition
from strategies._base import Signal

logger = logging.getLogger(__name__)

DEFAULT_RISK_CONFIG_PATH = Path(__file__).parent.parent / "config" / "risk.yaml"


# ---------------------------------------------------------------------------
# Stato portafoglio
# ---------------------------------------------------------------------------


@dataclass
class PortfolioState:
    """Snapshot aggregato dello stato di trading per il risk gate."""

    open_positions: list[BrokerPosition] = field(default_factory=list)
    equity: float = 0.0
    initial_equity: float = 0.0
    daily_pnl: float = 0.0
    consecutive_losses: int = 0
    last_loss_time: Optional[datetime] = None

    @property
    def drawdown_pct(self) -> float:
        """Drawdown corrente in frazione (es. 0.07 = 7%)."""
        if self.initial_equity <= 0:
            return 0.0
        if self.equity >= self.initial_equity:
            return 0.0
        return (self.initial_equity - self.equity) / self.initial_equity

    @property
    def daily_drawdown_pct(self) -> float:
        """Drawdown giornaliero (frazione di equity corrente)."""
        if self.equity <= 0 or self.daily_pnl >= 0:
            return 0.0
        return abs(self.daily_pnl) / self.equity

    @property
    def total_exposure_pct(self) -> float:
        """Somma del valore nozionale aperto / equity."""
        if self.equity <= 0:
            return 0.0
        notional = sum(abs(p.size * p.current_price) for p in self.open_positions)
        return notional / self.equity

    @classmethod
    def from_brokers(
        cls,
        brokers: list[BrokerBase],
        symbols: list[str],
        initial_equity: Optional[float] = None,
    ) -> "PortfolioState":
        """Costruisce lo stato aggregando i broker attivi.

        `symbols` è la lista da interrogare via `get_position` (broker non
        espongono "tutte le posizioni" in modo uniforme).
        """
        positions: list[BrokerPosition] = []
        equity = 0.0
        for broker in brokers:
            try:
                info = broker.get_info()
                equity += info.equity
            except Exception as exc:
                logger.warning("Broker %s get_info fallito: %s", broker.name, exc)
                continue
            for sym in symbols:
                try:
                    pos = broker.get_position(sym)
                    if pos is not None:
                        positions.append(pos)
                except Exception as exc:
                    logger.debug("get_position %s fallito su %s: %s", sym, broker.name, exc)

        return cls(
            open_positions=positions,
            equity=equity,
            initial_equity=initial_equity if initial_equity is not None else equity,
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def load_risk_config(path: Path | str = DEFAULT_RISK_CONFIG_PATH) -> dict[str, Any]:
    """Carica `config/risk.yaml`."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_signal(
    signal: Signal,
    symbol: str,
    entry_price: float,
    state: PortfolioState,
    risk_config: dict[str, Any],
    now: Optional[datetime] = None,
) -> tuple[bool, str]:
    """Valida un Signal contro lo stato corrente e i limiti di rischio.

    Restituisce `(ok, reason)`. Se `ok=False`, `reason` è una stringa diagnostica
    pronta per il logging o la notifica all'utente.
    """
    now = now or datetime.now(timezone.utc)

    # 1. Drawdown totale
    max_dd = risk_config.get("max_drawdown_pct", 1.0)
    if state.drawdown_pct >= max_dd:
        return False, (
            f"max_drawdown_pct superato: {state.drawdown_pct:.2%} >= {max_dd:.2%}"
        )

    # 2. Drawdown giornaliero
    max_daily_dd = risk_config.get("max_daily_drawdown_pct", 1.0)
    if state.daily_drawdown_pct >= max_daily_dd:
        return False, (
            f"max_daily_drawdown_pct superato: "
            f"{state.daily_drawdown_pct:.2%} >= {max_daily_dd:.2%}"
        )

    # 3. Cooldown post-perdite consecutive
    max_losses = risk_config.get("max_consecutive_losses", 999)
    cooldown_min = risk_config.get("cooldown_minutes_after_max_losses", 0)
    if (
        state.consecutive_losses >= max_losses
        and state.last_loss_time is not None
        and now - state.last_loss_time < timedelta(minutes=cooldown_min)
    ):
        remaining = timedelta(minutes=cooldown_min) - (now - state.last_loss_time)
        return False, (
            f"cooldown attivo dopo {state.consecutive_losses} perdite consecutive: "
            f"{remaining} rimanenti"
        )

    # 4. Numero posizioni aperte
    max_open = risk_config.get("max_open_positions", 999)
    if len(state.open_positions) >= max_open:
        return False, f"max_open_positions raggiunto ({max_open})"

    # 5. Posizioni per simbolo
    max_per_sym = risk_config.get("max_positions_per_symbol", 999)
    same_sym = sum(1 for p in state.open_positions if p.symbol == symbol)
    if same_sym >= max_per_sym:
        return False, (
            f"max_positions_per_symbol raggiunto su {symbol} ({max_per_sym})"
        )

    # 6. RR minimo
    min_rr = risk_config.get("min_reward_to_risk", 0.0)
    rr = signal.reward_to_risk(entry_price)
    if rr < min_rr:
        return False, f"reward_to_risk insufficiente: {rr:.2f} < {min_rr}"

    # 7. Size massima per trade (sizing notional / equity)
    max_size_pct = risk_config.get("max_size_per_trade_pct", 1.0)
    if state.equity > 0:
        signal_notional = abs(signal.size * entry_price)
        signal_pct = signal_notional / state.equity
        if signal_pct > max_size_pct:
            return False, (
                f"size eccede max_size_per_trade_pct: "
                f"{signal_pct:.2%} > {max_size_pct:.2%}"
            )

    # 8. Esposizione totale (somma posizioni esistenti + nuova)
    max_total = risk_config.get("max_total_exposure_pct", 1.0)
    if state.equity > 0:
        new_notional = abs(signal.size * entry_price)
        projected = state.total_exposure_pct + (new_notional / state.equity)
        if projected > max_total:
            return False, (
                f"max_total_exposure_pct superato: "
                f"{projected:.2%} > {max_total:.2%}"
            )

    return True, "ok"
