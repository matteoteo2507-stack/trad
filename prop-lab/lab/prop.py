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
            payout += rules.get("fee") or 0.0
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


_BASI = ("day_start", "initial")
_TIPI_MAX = ("static", "trailing", "trailing_eod")


def regole_mancanti(rules: dict) -> list:
    """Campi necessari alla simulazione che mancano o hanno un valore che il simulatore non modella.
    Aggiunta trad (07/10): i regolamenti veri delle firm arrivano con buchi (dato non pubblicato o non
    trovato) e un default inventato al loro posto produrrebbe un pass rate plausibile e sbagliato."""
    miss = [k for k in ("account", "daily_loss_pct", "daily_basis", "max_loss_pct", "max_loss_type", "phases")
            if rules.get(k) is None]
    if rules.get("daily_basis") is not None and rules["daily_basis"] not in _BASI:
        miss.append(f"daily_basis={rules['daily_basis']!r} non modellato (ammessi: {_BASI})")
    if rules.get("max_loss_type") is not None and rules["max_loss_type"] not in _TIPI_MAX:
        miss.append(f"max_loss_type={rules['max_loss_type']!r} non modellato (ammessi: {_TIPI_MAX})")
    for i, ph in enumerate(rules.get("phases") or []):
        for k in ("target_pct", "min_days"):
            if ph.get(k) is None:
                miss.append(f"phases[{i}].{k}")
    f = rules.get("funded")
    if f:
        for k in ("days", "split_pct", "payout_every"):
            if not isinstance(f.get(k), (int, float)):
                miss.append(f"funded.{k}")
    return miss


def evaluate(day_trades, rules: dict, profile: dict, mode="bootstrap", n_paths=300, block=5, seed=7, stride=5) -> dict:
    miss = regole_mancanti(rules)
    if miss:
        raise ValueError(f"regolamento non simulabile, mancano: {miss}")
    model = RiskModel(profile)
    horizon = sum((p.get("max_days") or rules.get("max_days_default", 120)) for p in rules["phases"])
    horizon += (rules.get("funded") or {}).get("days", 0) + 30
    rng = np.random.default_rng(seed)
    paths = make_paths(len(day_trades), mode, n_paths, horizon, block, rng, stride)
    out = [simulate_path([day_trades[i] for i in p], rules, model) for p in paths]
    n = len(out)
    passed = [o for o in out if o["passed"]]
    fee = rules.get("fee", 0.0)
    if fee is None:            # costo ignoto: il pass rate si calcola, l'EV no (non si inventa un costo)
        fee = float("nan")
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


# ---------------------------------------------------------------- aggiunte trad (2026-10-06)
# Perche': il 05/10 una strategia a vantaggio ZERO ha passato ~30% delle challenge con EV ~+1.900 per
# tentativo (profilo guardia_giornaliera 3%). La challenge e' un'opzione: la firm assorbe le perdite,
# il trader incassa i rialzi. Quindi un EV positivo non e' prova di vantaggio, e un pass rate da un solo
# campione storico non dice quanto e' incerto. Le due funzioni sotto rispondono a queste due domande.

def zero_edge(day_trades):
    """Gli stessi trade, negli stessi giorni, con la stessa forma della distribuzione, ma attesa ZERO:
    a ogni R si sottrae la media del campione. La MAE si riallinea dove la perdita diventa piu' grande
    dell'escursione avversa registrata (una perdita di 1,2R ha per forza un'escursione di almeno 1,2R)."""
    rs = [r for d in day_trades for r, _ in d]
    if not rs:
        return [list(d) for d in day_trades]
    mu = float(np.mean(rs))
    return [[(r - mu, max(m, mu - r)) for r, m in d] for d in day_trades]


def _resample_days(day_trades, block: int, rng: np.random.Generator):
    """Bootstrap a blocchi circolari dei GIORNI (conserva i trade dello stesso giorno e la dipendenza
    fino a `block` giorni), stessa lunghezza del campione."""
    n = len(day_trades)
    nb = math.ceil(n / block)
    st = rng.integers(0, n, nb)
    idx = np.concatenate([np.arange(s, s + block) % n for s in st])[:n]
    return [day_trades[i] for i in idx]


def evaluate_ci(day_trades, rules: dict, profile: dict, mode="bootstrap", n_paths=200, block=5, seed=7,
                n_outer=100, conf=0.90) -> dict:
    """Pass rate ed EV con l'incertezza di STIMA, e il confronto col vantaggio zero.

    `evaluate` da' la stima "plug-in": come andrebbe una strategia le cui statistiche vere fossero
    esattamente quelle del campione. Ma il campione e' uno solo: su 336 trade l'attesa ha un errore
    standard di ~0,055R, e fra -0,10R e +0,10R il pass rate passa dall'1,5% al 46% (misura del 05/10).
    Qui il campione stesso si ricampiona `n_outer` volte e per ognuno si rifa' `evaluate`: la dispersione
    e' quanto non sappiamo. Per ogni ricampionamento si calcola anche lo stesso campione a vantaggio zero,
    con gli STESSI percorsi (numeri casuali comuni): `ev_vs_zero` e' la parte di EV dovuta al vantaggio,
    il resto e' valore d'opzione della challenge, che avrebbe anche chi non ha nessun vantaggio."""
    point = evaluate(day_trades, rules, profile, mode, n_paths, block, seed)
    zero = evaluate(zero_edge(day_trades), rules, profile, mode, n_paths, block, seed)
    rng = np.random.default_rng(seed + 1)
    pr, ev, dpr, dev = [], [], [], []
    for k in range(n_outer):
        s = _resample_days(day_trades, block, rng)
        a = evaluate(s, rules, profile, mode, n_paths, block, seed + 2 + k)
        z = evaluate(zero_edge(s), rules, profile, mode, n_paths, block, seed + 2 + k)
        pr.append(a["pass_rate"]); ev.append(a["ev_attempt"])
        dpr.append(a["pass_rate"] - z["pass_rate"]); dev.append(a["ev_attempt"] - z["ev_attempt"])
    q = [(1 - conf) / 2 * 100, (1 + conf) / 2 * 100]
    pct = lambda x: [float(v) for v in np.percentile(x, q)]
    return {
        "pass_rate": point["pass_rate"], "pass_ci": pct(pr),
        "ev_attempt": point["ev_attempt"], "ev_ci": pct(ev),
        "pass_zero": zero["pass_rate"], "ev_zero": zero["ev_attempt"],
        "pass_vs_zero": point["pass_rate"] - zero["pass_rate"], "pass_vs_zero_ci": pct(dpr),
        "ev_vs_zero": point["ev_attempt"] - zero["ev_attempt"], "ev_vs_zero_ci": pct(dev),
        "p_ev_vs_zero_pos": float(np.mean(np.asarray(dev) > 0)),
        "conf": conf, "n_outer": n_outer, "n_paths": n_paths,
    }
