"""TSMOM — Time Series Momentum strategy (Moskowitz-Ooi-Pedersen 2012).

Logica di signal su barra D1:

    s_long  = sign(close[t] - close[t - L])
    s_fast  = sign(EWMA(close, fast)[t] - EWMA(close, slow)[t])
    pos[t]  = s_long  if  s_long == s_fast  else 0

Stop loss: entry ± m × ATR(N). Exit naturale: pos[t] cambia segno → close.

Sizing vol-target: size = vol_target_ann / realized_vol_60d_ann, capped.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class TSMOMSignalConfig:
    lookback_long_bars: int
    ewma_fast: int
    ewma_slow: int


@dataclass
class TSMOMSizingConfig:
    vol_target_annual: float
    realized_vol_window: int
    account_risk_pct: float
    size_cap_mult: float


@dataclass
class TSMOMStopConfig:
    atr_period: int
    atr_mult: float


@dataclass
class TSMOMCosts:
    spread_pips: float = 0.0
    slippage_pips: float = 0.0
    commission_per_lot: float = 0.0
    swap_long_per_day: float = 0.0
    swap_short_per_day: float = 0.0


class TSMOMStrategy:
    """Time Series Momentum su singolo asset, barre D1.

    Pure-function style: tutto deriva da `bars: pd.DataFrame` con colonne
    `open, high, low, close`. Nessun side effect.
    """

    name = "tsmom"

    def __init__(
        self,
        signal_cfg: TSMOMSignalConfig,
        sizing_cfg: TSMOMSizingConfig,
        stop_cfg: TSMOMStopConfig,
        costs: TSMOMCosts | None = None,
    ) -> None:
        self.signal_cfg = signal_cfg
        self.sizing_cfg = sizing_cfg
        self.stop_cfg = stop_cfg
        self.costs = costs or TSMOMCosts()

    # ------------------------------------------------------------------
    # Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def _atr(bars: pd.DataFrame, period: int) -> pd.Series:
        high, low, close = bars["high"], bars["low"], bars["close"]
        prev_close = close.shift(1)
        tr = pd.concat([
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(period, min_periods=period).mean()

    @staticmethod
    def _realized_vol_annual(returns: pd.Series, window: int) -> pd.Series:
        return returns.rolling(window).std(ddof=1) * np.sqrt(252)

    # ------------------------------------------------------------------
    # Signal
    # ------------------------------------------------------------------

    def compute_signal(self, bars: pd.DataFrame) -> pd.Series:
        """Restituisce la serie di posizioni desiderate (-1, 0, +1) per barra."""
        close = bars["close"]
        L = self.signal_cfg.lookback_long_bars

        long_change = close - close.shift(L)
        s_long = np.sign(long_change)

        ema_fast = close.ewm(span=self.signal_cfg.ewma_fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.signal_cfg.ewma_slow, adjust=False).mean()
        s_fast = np.sign(ema_fast - ema_slow)

        pos = np.where(s_long == s_fast, s_long, 0)
        return pd.Series(pos, index=bars.index, dtype=float)

    # ------------------------------------------------------------------
    # Sizing
    # ------------------------------------------------------------------

    def compute_size_factor(self, bars: pd.DataFrame) -> pd.Series:
        """Multiplier vol-target: vol_target / realized_vol, capped.

        Restituisce un fattore moltiplicativo che il caller applica al
        sizing baseline (es. lotti calcolati su account_risk_pct).
        """
        returns = bars["close"].pct_change()
        rv = self._realized_vol_annual(returns, self.sizing_cfg.realized_vol_window)
        factor = self.sizing_cfg.vol_target_annual / rv.replace(0, np.nan)
        factor = factor.clip(upper=self.sizing_cfg.size_cap_mult)
        return factor.fillna(0.0)

    # ------------------------------------------------------------------
    # Stop loss
    # ------------------------------------------------------------------

    def compute_stop_distance(self, bars: pd.DataFrame) -> pd.Series:
        """Distanza assoluta entry → SL al momento del fill (ATR · mult)."""
        atr = self._atr(bars, self.stop_cfg.atr_period)
        return atr * self.stop_cfg.atr_mult

    # ------------------------------------------------------------------
    # Backtest (event-driven semplice, no slippage modeling avanzato)
    # ------------------------------------------------------------------

    def backtest(
        self,
        bars: pd.DataFrame,
        initial_equity: float = 10_000.0,
    ) -> pd.DataFrame:
        """Backtest event-driven su barre D1. Returns DataFrame con:

            equity, position, pnl, daily_return, signal, sl_dist
        """
        sig = self.compute_signal(bars)
        size_factor = self.compute_size_factor(bars)
        sl_dist = self.compute_stop_distance(bars)

        close = bars["close"].to_numpy()
        sig_arr = sig.to_numpy()
        sf_arr = size_factor.to_numpy()
        sld_arr = sl_dist.to_numpy()

        n = len(bars)
        equity = np.full(n, initial_equity, dtype=float)
        pnl = np.zeros(n, dtype=float)
        position = np.zeros(n, dtype=float)
        cur_pos = 0.0
        cur_qty = 0.0      # units of underlying (price-quoted)
        cur_entry = 0.0
        cur_sl = 0.0

        spread = self.costs.spread_pips
        # Per USDJPY 1 pip = 0.01; per EURUSD = 0.0001. Approssimazione:
        # se prezzo >= 50 → 0.01, altrimenti 0.0001.
        pip_size = 0.01 if (close[~np.isnan(close)][:1].mean() if (~np.isnan(close)).any() else 0) >= 50 else 0.0001

        for i in range(1, n):
            # 1. Check SL su candela corrente (high/low).
            if cur_pos != 0:
                hi = bars["high"].iat[i]
                lo = bars["low"].iat[i]
                hit = False
                exit_price = close[i]
                if cur_pos > 0 and lo <= cur_sl:
                    exit_price = cur_sl
                    hit = True
                elif cur_pos < 0 and hi >= cur_sl:
                    exit_price = cur_sl
                    hit = True
                if hit:
                    pnl[i] += cur_qty * cur_pos * (exit_price - cur_entry)
                    pnl[i] -= cur_qty * spread * pip_size  # spread di chiusura
                    cur_pos = 0.0
                    cur_qty = 0.0

            # 2. Signal flip → flatten + (eventuale) open inverso.
            desired = sig_arr[i - 1]   # signal su barra t-1, eseguito a open di t
            if desired != cur_pos:
                if cur_pos != 0:
                    pnl[i] += cur_qty * cur_pos * (close[i] - cur_entry)
                    pnl[i] -= cur_qty * spread * pip_size
                    cur_pos = 0.0
                    cur_qty = 0.0
                if desired != 0 and np.isfinite(sld_arr[i - 1]) and sld_arr[i - 1] > 0:
                    # Sizing: account_risk_pct * size_factor diviso stop distance.
                    risk_money = (
                        equity[i - 1]
                        * self.sizing_cfg.account_risk_pct
                        * (sf_arr[i - 1] if np.isfinite(sf_arr[i - 1]) else 0.0)
                    )
                    if risk_money > 0:
                        cur_qty = risk_money / sld_arr[i - 1]
                        cur_pos = desired
                        cur_entry = close[i]
                        cur_sl = (
                            cur_entry - desired * sld_arr[i - 1]
                        )
                        pnl[i] -= cur_qty * spread * pip_size  # spread di apertura

            # 3. Mark-to-market unrealized (incluso per equity continua).
            mtm = cur_qty * cur_pos * (close[i] - cur_entry) if cur_pos != 0 else 0.0
            equity[i] = equity[i - 1] + pnl[i] + (mtm - (equity[i - 1] - initial_equity if i == 1 else 0))
            # Più semplice: equity = equity_realizzata + mtm_unrealized.
            # Ricalcolo cumulativo realizzato:
            equity[i] = initial_equity + np.cumsum(pnl)[i] + mtm
            position[i] = cur_pos

        out = pd.DataFrame({
            "equity": equity,
            "position": position,
            "pnl_realized": pnl,
            "signal": sig.values,
            "size_factor": size_factor.values,
            "sl_dist": sl_dist.values,
        }, index=bars.index)
        out["daily_return"] = out["equity"].pct_change().fillna(0.0)
        return out
