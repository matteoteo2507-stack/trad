"""Simulatore di challenge prop su liste di trade in R.

Per ogni combinazione (strategia x profilo di rischio x regole prop) simula molte
challenge complete: fase 1 -> fase 2 -> funded (con payout), e misura:
  pass_rate, cause di fallimento (daily / max loss / tempo), giorni per passare,
  payout attesi, EV per tentativo (payout attesi - fee).

Percorsi simulati:
  - storico:   finestre contigue che partono da ogni giorno (stride configurabile)
  - bootstrap: blocchi di giorni ricampionati (mantiene il raggruppamento dei trade)

Approssimazioni dichiarate:
  - il DD intraday di un trade è stimato con la MAE (escursione avversa) del trade
  - un trade conta nel giorno in cui chiude; una posizione alla volta per strategia
  - le regole sono parametriche: VERIFICA SEMPRE il regolamento attuale della tua firm
"""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from .risk import AccountState, RiskModel

INF = float("inf")


def trades_by_day(trades: pd.DataFrame, days: pd.DatetimeIndex) -> list[list[tuple[float, float]]]:
    g = {}
    if not trades.empty:
        t = trades.sort_values("exit_time")
        for d, r, m in zip(t["exit_time"].dt.normalize(), t["r"], t["mae_r"]):
            g.setdefault(d, []).append((float(r), float(m)))
    return [g.get(d, []) for d in days]


def _floors(rules, initial, day_start, peak):
    daily_amt = rules["daily_loss_pct"] / 100 * initial
    max_amt = rules["max_loss_pct"] / 100 * initial
    if rules.get("daily_basis", "day_start") == "day_start":
        f_daily = day_start - daily_amt
    else:
        f_daily = initial - daily_amt
    typ = rules.get("max_loss_type", "static")
    if typ == "static":
        f_max = initial - max_amt
    else:
        f_max = peak - max_amt
        if rules.get("trailing_lock", True):
            f_max = min(f_max, initial)
    return f_daily, f_max, daily_amt, max_amt


def simulate_path(day_seq, rules: dict, model: RiskModel) -> dict:
    initial = float(rules.get("account", 100_000))
    phases = list(rules["phases"])
    funded = rules.get("funded") or {}
    max_days_default = rules.get("max_days_default", 120)
    trailing_eod = rules.get("max_loss_type") == "trailing_eod"

    di = 0; total_days = 0
    res = {"passed": False, "fail": None, "phase_reached": 0, "days_to_pass": None, "payout": 0.0}

    def run_stage(target_pct, min_days, max_days, consistency, funded_cfg=None):
        nonlocal di, total_days
        bal = initial; peak = initial
        tgt = round(initial * (1 + target_pct / 100), 2) if target_pct is not None else INF
        trading_days = 0; day_profits = []; loss_streak = 0; win_streak = 0
        payout = 0.0; days_in = 0
        limit = max_days or (funded_cfg.get("days") if funded_cfg else max_days_default)
        while days_in < limit:
            if di >= len(day_seq):
                return "data_end", days_in, payout
            trades = day_seq[di]; di += 1; days_in += 1; total_days += 1
            day_start = bal
            f_daily, f_max, d_amt, m_amt = _floors(rules, initial, day_start, peak)
            day_pnl = 0.0; n_day = 0
            for r, mae in trades:
                st = AccountState(initial, bal, peak, day_start, day_pnl, n_day, loss_streak, win_streak,
                                  tgt, f_daily, f_max, d_amt, m_amt)
                risk = model.risk_amount(st)
                if risk <= 0:
                    continue
                n_day += 1
                worst = bal - risk * mae
                if worst <= f_daily:
                    return "daily", days_in, payout
                if worst <= f_max:
                    return "max", days_in, payout
                pnl = risk * r
                bal += pnl; day_pnl += pnl
                if bal <= f_daily:
                    return "daily", days_in, payout
                if bal <= f_max:
                    return "max", days_in, payout
                if pnl > 0:
                    win_streak += 1; loss_streak = 0
                else:
                    loss_streak += 1; win_streak = 0
                if not trailing_eod:
                    peak = max(peak, bal)
                    f_daily, f_max, d_amt, m_amt = _floors(rules, initial, day_start, peak)
                if bal >= tgt:
                    break   # target raggiunto: stop rischio
            if trailing_eod:
                peak = max(peak, bal)
            if n_day:
                trading_days += 1
                day_profits.append(day_pnl)
            if bal >= tgt:
                ok_cons = True
                if consistency:
                    tot = bal - initial
                    ok_cons = tot > 0 and max(day_profits) <= consistency / 100 * tot
                if ok_cons:
                    # giorni minimi: si completano con micro-trade a rischio ~0
                    extra = max(0, min_days - trading_days)
                    di += extra; total_days += extra
                    return "pass", days_in + extra, payout
            if funded_cfg and days_in % funded_cfg.get("payout_every", 20) == 0 and bal > initial:
                payout += (bal - initial) * funded_cfg.get("split_pct", 80) / 100
                bal = initial; peak = initial
        return ("timeout" if not funded_cfg else "funded_end"), days_in, payout

    for pi, ph in enumerate(phases):
        status, days, _ = run_stage(ph["target_pct"], ph.get("min_days", 0), ph.get("max_days"),
                                    ph.get("consistency_pct", rules.get("consistency_pct")))
        res["phase_reached"] = pi + 1
        if status != "pass":
            res["fail"] = status
            return res
    res["passed"] = True
    res["days_to_pass"] = total_days
    if funded:
        status, days, payout = run_stage(None, 0, None, None, funded_cfg=funded)
        if payout > 0 and funded.get("refund_fee"):
            payout += rules.get("fee", 0.0)
        res["payout"] = payout
        res["funded_status"] = status
    return res


def make_paths(n_days: int, mode: str, n_paths: int, horizon: int, block: int, rng: np.random.Generator,
               stride: int = 5) -> list[np.ndarray]:
    if mode == "storico":
        starts = range(0, n_days, stride)
        return [np.arange(s, s + horizon) % n_days for s in starts]
    paths = []
    nb = math.ceil(horizon / block)
    for _ in range(n_paths):
        st = rng.integers(0, max(1, n_days - block), nb)
        paths.append(np.concatenate([np.arange(s, s + block) for s in st])[:horizon])
    return paths


def evaluate(day_trades, rules: dict, profile: dict, mode="bootstrap", n_paths=300, block=5, seed=7, stride=5) -> dict:
    model = RiskModel(profile)
    horizon = sum((p.get("max_days") or rules.get("max_days_default", 120)) for p in rules["phases"])
    horizon += (rules.get("funded") or {}).get("days", 0) + 30
    rng = np.random.default_rng(seed)
    paths = make_paths(len(day_trades), mode, n_paths, horizon, block, rng, stride)
    out = [simulate_path([day_trades[i] for i in p], rules, model) for p in paths]
    n = len(out)
    passed = [o for o in out if o["passed"]]
    fee = rules.get("fee", 0.0)
    payouts = np.array([o["payout"] for o in out])
    dtp = [o["days_to_pass"] for o in passed]
    p_pass = len(passed) / n
    return {
        "pass_rate": p_pass,
        "fail_daily": sum(o["fail"] == "daily" for o in out) / n,
        "fail_max": sum(o["fail"] == "max" for o in out) / n,
        "timeout": sum(o["fail"] in ("timeout", "data_end") for o in out) / n,
        "p1_pass": sum(o["phase_reached"] >= 2 or o["passed"] for o in out) / n,
        "median_days": float(np.median(dtp)) if dtp else np.nan,
        "exp_payout": float(payouts.mean()),
        "ev_attempt": float(payouts.mean() - fee),
        "attempts_needed": (1 / p_pass) if p_pass > 0 else np.inf,
        "cost_to_pass": (fee / p_pass) if p_pass > 0 else np.inf,
        "n_paths": n,
    }
