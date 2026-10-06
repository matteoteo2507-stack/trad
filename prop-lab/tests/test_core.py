"""Test di base del motore: python -m pytest -q   (oppure python tests/test_core.py)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from lab.backtest import Signals, run_backtest
from lab.prop import simulate_path
from lab.risk import RiskModel


def bars(rows):
    idx = pd.date_range("2024-01-02 08:00", periods=len(rows), freq="h")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx).assign(spread_points=np.nan)


def test_long_tp_and_next_open_entry():
    df = bars([(100, 101, 99, 100), (100, 101, 99.5, 100.5), (100.5, 103, 100, 102.5), (102, 102, 101, 101)])
    e = np.array([1, 0, 0, 0]); sl = np.full(4, 2.0)
    tr = run_backtest(df, Signals(entry=e, sl_dist=sl, tp_r=1.0, max_bars=10))
    assert len(tr) == 1
    t = tr.iloc[0]
    assert t.entry == 100 and t.exit == 102 and t.exit_reason == "tp" and abs(t.r - 1.0) < 1e-9


def test_same_bar_sl_and_tp_counts_sl():
    df = bars([(100, 100, 100, 100), (100, 103, 97, 100), (100, 100, 100, 100)])
    tr = run_backtest(df, Signals(entry=np.array([1, 0, 0]), sl_dist=np.full(3, 2.0), tp_r=1.0))
    assert tr.iloc[0].exit_reason == "sl" and abs(tr.iloc[0].r + 1) < 1e-9


def test_gap_through_stop_loses_more_than_1R():
    df = bars([(100, 100, 100, 100), (100, 100.5, 99.5, 100), (95, 96, 94, 95)])
    tr = run_backtest(df, Signals(entry=np.array([1, 0, 0]), sl_dist=np.full(3, 2.0), tp_r=3.0))
    assert tr.iloc[0].exit == 95 and abs(tr.iloc[0].r + 2.5) < 1e-9


def test_costs_reduce_r():
    df = bars([(100, 100, 100, 100), (100, 101, 99.5, 100.5), (100.5, 103, 100, 102.5), (102, 102, 101, 101)])
    sig = Signals(entry=np.array([1, 0, 0, 0]), sl_dist=np.full(4, 2.0), tp_r=1.0)
    c = {"point": 0.01, "contract_size": 100, "spread_points": 20, "commission_per_lot_rt": 7, "slippage_points": 0,
         "swap_long_points": 0, "swap_short_points": 0}
    g = run_backtest(df, sig).iloc[0].r; n = run_backtest(df, sig, c).iloc[0].r
    assert n < g


def test_prop_daily_loss_breach():
    rules = {"account": 100000, "daily_loss_pct": 5, "max_loss_pct": 10, "max_loss_type": "static",
             "phases": [{"target_pct": 10, "min_days": 1}]}
    model = RiskModel({"name": "x", "base": {"type": "fixed_pct", "pct": 2.0, "of": "initial"},
                       "modifiers": [{"type": "floor_cap", "frac": 10.0}]})
    days = [[(-1, 1), (-1, 1), (-1, 1)]] + [[]] * 10
    assert simulate_path(days, rules, model)["fail"] == "daily"


def test_prop_pass():
    rules = {"account": 100000, "daily_loss_pct": 5, "max_loss_pct": 10, "max_loss_type": "static",
             "phases": [{"target_pct": 10, "min_days": 4}]}
    model = RiskModel({"name": "x", "base": {"type": "fixed_pct", "pct": 1.0, "of": "initial"}})
    days = [[(2, 0.3)]] * 10
    r = simulate_path(days, rules, model)
    assert r["passed"] and r["days_to_pass"] == 5


def test_dd_linear_reduces_risk():
    from lab.risk import AccountState
    m = RiskModel({"name": "d", "base": {"type": "fixed_pct", "pct": 1.0, "of": "initial"},
                   "modifiers": [{"type": "dd_linear", "min_mult": 0.25}]})
    full = AccountState(1e5, 1e5, 1e5, 1e5, 0, 0, 0, 0, 1.1e5, 9.5e4, 9e4, 5e3, 1e4)
    down = AccountState(1e5, 9.5e4, 1e5, 9.5e4, 0, 0, 0, 0, 1.1e5, 9.0e4, 9e4, 5e3, 1e4)
    assert m.risk_amount(down) < m.risk_amount(full)


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok", k)
