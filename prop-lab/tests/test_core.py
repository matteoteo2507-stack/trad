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


# ---------------------------------------------------------------- aggiunte trad (2026-10-06)
def _giorni(r_list, mae_loss=1.0):
    return [[(r, mae_loss if r < 0 else 0.0)] for r in r_list]


def test_zero_edge_media_zero_e_mae_coerente():
    from lab.prop import zero_edge
    rng = np.random.default_rng(3)
    days = [[(float(x), 1.0 if x < 0 else 0.3)] for x in rng.choice([2.0, -1.0], 300)] + [[]] * 20
    z = zero_edge(days)
    rs = [r for d in z for r, _ in d]
    assert abs(np.mean(rs)) < 1e-12
    assert all(m >= -r - 1e-12 for d in z for r, m in d)    # una perdita di xR ha escursione >= xR
    assert sum(len(d) for d in z) == sum(len(d) for d in days)


def test_vantaggio_zero_due_barriere_come_la_rovina_del_giocatore():
    """+10% / -10% statico, 1% a trade, niente limite giornaliero ne' timeout: a vantaggio zero si passa
    nel 50% dei casi (rovina del giocatore). Se questo numero si sposta, il simulatore ha un difetto."""
    from lab.prop import evaluate, zero_edge
    rules = {"account": 100000, "daily_loss_pct": 100, "daily_basis": "day_start", "max_loss_pct": 10, "max_loss_type": "static",
             "phases": [{"target_pct": 10, "min_days": 0}], "max_days_default": 5000}
    rng = np.random.default_rng(11)
    days = zero_edge(_giorni(rng.choice([1.0, -1.0], 400)))
    prof = {"name": "s", "base": {"type": "fixed_pct", "pct": 1.0, "of": "initial"}}
    p = evaluate(days, rules, prof, n_paths=2000, block=1, seed=5)["pass_rate"]
    assert abs(p - 0.5) < 0.04, p


def test_evaluate_ci_separa_vantaggio_da_valore_opzione():
    from lab.prop import evaluate_ci
    rules = {"account": 100000, "fee": 500, "daily_loss_pct": 5, "daily_basis": "day_start", "max_loss_pct": 10, "max_loss_type": "static",
             "phases": [{"target_pct": 8, "min_days": 0}], "max_days_default": 120,
             "funded": {"days": 60, "split_pct": 80, "payout_every": 20, "refund_fee": True}}
    prof = {"name": "s", "base": {"type": "fixed_pct", "pct": 1.0, "of": "initial"}}
    rng = np.random.default_rng(2)
    buono = _giorni(np.where(rng.random(300) < 0.62, 1.0, -1.0))        # E ~ +0,24R
    o = evaluate_ci(buono, rules, prof, n_paths=80, n_outer=15, seed=1)
    assert o["ev_vs_zero"] > 0 and o["p_ev_vs_zero_pos"] >= 0.8
    assert o["pass_rate"] > o["pass_zero"]
    lo, hi = o["pass_ci"]
    assert lo <= hi and 0.0 <= lo and hi <= 1.0


def test_map_ricade_in_serie():
    import os
    from lab import pipeline as P
    os.environ["PROPLAB_WORKERS"] = "1"
    try:
        assert P._map(abs, [-1, -2, 3]) == [1, 2, 3]
    finally:
        del os.environ["PROPLAB_WORKERS"]


def test_verdetto_oos_non_promuove_senza_intervallo_e_dsr():
    from lab.metrics import mean_ci, verdetto_oos
    rng = np.random.default_rng(0)
    rumore = rng.choice([1.0, -1.0], 120) + 0.0
    lo, hi, mde = mean_ci(rumore, 0.05, m=8)
    assert lo < 0 < hi and mde > 0
    assert verdetto_oos(lo, hi, dsr=0.99) == "NON_DIMOSTRATA"          # intervallo contiene lo zero
    assert verdetto_oos(0.05, 0.40, dsr=0.10) == "PROMOSSA"             # default: decide l'OOS, il DSR e' diagnostica
    assert verdetto_oos(0.05, 0.40, dsr=0.50, min_dsr=0.95) == "NON_DIMOSTRATA"   # se si chiede il DSR, conta
    assert verdetto_oos(0.05, 0.40, dsr=0.96, min_dsr=0.95) == "PROMOSSA"
    assert verdetto_oos(-0.40, -0.05, dsr=0.99) == "SCARTATA"
    # Bonferroni: piu' candidati, intervallo piu' largo
    assert mean_ci(rumore, 0.05, m=8)[0] < mean_ci(rumore, 0.05, m=1)[0]


def test_regolamento_incompleto_rifiutato_con_elenco():
    import pytest
    from lab.prop import evaluate, regole_mancanti
    r = {"account": 100000, "fee": None, "daily_loss_pct": 5, "daily_basis": None, "max_loss_pct": 10,
         "max_loss_type": "static", "phases": [{"target_pct": None, "min_days": 5}]}
    miss = regole_mancanti(r)
    assert "daily_basis" in miss and "phases[0].target_pct" in miss
    with pytest.raises(ValueError):
        evaluate(_giorni([1.0, -1.0] * 20), r, {"name": "s", "base": {"type": "fixed_pct", "pct": 1.0}})
    r.update(daily_basis="day_start", phases=[{"target_pct": 8, "min_days": 0}])
    o = evaluate(_giorni([1.0, -1.0] * 20), r, {"name": "s", "base": {"type": "fixed_pct", "pct": 1.0}}, n_paths=20)
    assert np.isnan(o["ev_attempt"]) and 0.0 <= o["pass_rate"] <= 1.0   # costo ignoto: niente EV inventato


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok", k)
