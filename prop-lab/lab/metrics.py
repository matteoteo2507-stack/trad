"""Metriche sui trade (in R) e controlli anti-overfitting."""
from __future__ import annotations

import itertools
import numpy as np
import pandas as pd
from scipy import stats


def daily_r(trades: pd.DataFrame, days: pd.DatetimeIndex) -> pd.Series:
    if trades.empty:
        return pd.Series(0.0, index=days)
    s = trades.groupby(trades["exit_time"].dt.normalize())["r"].sum()
    return s.reindex(days, fill_value=0.0)


def trade_metrics(trades: pd.DataFrame, days: pd.DatetimeIndex) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0, "win_rate": np.nan, "expectancy": np.nan, "pf": np.nan, "total_r": 0.0,
                "max_dd_r": 0.0, "sharpe_d": np.nan, "sharpe_ann": np.nan, "tstat": np.nan,
                "trades_month": 0.0, "pct_pos_quarters": np.nan, "avg_win": np.nan, "avg_loss": np.nan,
                "skew_d": np.nan, "kurt_d": np.nan, "n_days": len(days)}
    r = trades["r"].to_numpy()
    wins = r[r > 0]; losses = r[r <= 0]
    eq = np.cumsum(r)
    dd = np.max(np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq) if n else 0.0
    dr = daily_r(trades, days)
    sd = dr.std(ddof=1)
    sh_d = dr.mean() / sd if sd > 0 else np.nan
    q = trades.groupby(trades["exit_time"].dt.to_period("Q"))["r"].sum()
    months = max(1e-9, (days[-1] - days[0]).days / 30.44) if len(days) > 1 else 1.0
    return {
        "n": n,
        "win_rate": len(wins) / n,
        "avg_win": wins.mean() if len(wins) else 0.0,
        "avg_loss": losses.mean() if len(losses) else 0.0,
        "expectancy": r.mean(),
        "pf": wins.sum() / -losses.sum() if losses.sum() < 0 else np.inf,
        "total_r": r.sum(),
        "max_dd_r": dd,
        "sharpe_d": sh_d,
        "sharpe_ann": sh_d * np.sqrt(252) if np.isfinite(sh_d) else np.nan,
        "tstat": r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 2 and r.std(ddof=1) > 0 else np.nan,
        "trades_month": n / months,
        "pct_pos_quarters": (q > 0).mean() if len(q) else np.nan,
        "skew_d": stats.skew(dr) if len(dr) > 3 else 0.0,
        "kurt_d": stats.kurtosis(dr, fisher=False) if len(dr) > 3 else 3.0,
        "n_days": len(dr),
    }


def deflated_sharpe(sr: float, sr_trials: np.ndarray, n_obs: int, skew: float, kurt: float) -> float:
    """Deflated Sharpe Ratio (Bailey & López de Prado, 2014).
    Probabilità che lo Sharpe osservato sia > 0 tenendo conto di QUANTE varianti sono state provate.
    sr e sr_trials sono Sharpe per-periodo (giornalieri, non annualizzati)."""
    sr_trials = np.asarray([x for x in sr_trials if np.isfinite(x)])
    N = max(len(sr_trials), 1)
    if not np.isfinite(sr) or n_obs < 10:
        return np.nan
    v = np.var(sr_trials, ddof=1) if N > 1 else 0.0
    g = 0.5772156649
    if N > 1 and v > 0:
        sr0 = np.sqrt(v) * ((1 - g) * stats.norm.ppf(1 - 1 / N) + g * stats.norm.ppf(1 - 1 / (N * np.e)))
    else:
        sr0 = 0.0
    den = np.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr ** 2))
    return float(stats.norm.cdf((sr - sr0) * np.sqrt(n_obs - 1) / den))


def plateau_scores(res: pd.DataFrame, grid: dict, metric: str = "expectancy") -> pd.Series:
    """Media della metrica sulla variante + vicini di griglia (un parametro spostato di un passo).
    Un picco isolato circondato da varianti negative = probabile overfitting."""
    keys = list(grid.keys())
    if not keys:
        return res[metric]
    pos = {k: {v: i for i, v in enumerate(grid[k])} for k in keys}
    table = {tuple(row[k] for k in keys): row[metric] for _, row in res.iterrows()}
    out = []
    for _, row in res.iterrows():
        vals = [row[metric]]
        for ki, k in enumerate(keys):
            i = pos[k].get(row[k])
            if i is None:
                continue
            for di in (-1, 1):
                ni = i + di
                if 0 <= ni < len(grid[k]):
                    key = list(tuple(row[kk] for kk in keys))
                    key[ki] = grid[k][ni]
                    v = table.get(tuple(key))
                    if v is not None and np.isfinite(v):
                        vals.append(v)
        out.append(np.nanmean(vals))
    return pd.Series(out, index=res.index)


def expand_grid(grid: dict) -> list[dict]:
    keys = list(grid.keys())
    return [dict(zip(keys, combo)) for combo in itertools.product(*[grid[k] for k in keys])]


# ---------------------------------------------------------------- aggiunte trad (2026-10-07)
def mean_ci(r, alpha: float = 0.05, m: int = 1) -> tuple[float, float, float]:
    """Intervallo t della media di R con correzione di Bonferroni per `m` candidati, e MDE (potenza 80%).
    Serve alla conferma OOS: fra 8 candidati scelti come migliori, almeno uno esce positivo per caso con
    probabilita' alta (5 random walk su 8 il 05/10). Un numero > 0 senza intervallo non e' un verdetto."""
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    n = r.size
    if n < 3:
        return np.nan, np.nan, np.nan
    se = r.std(ddof=1) / np.sqrt(n)
    a = alpha / (2 * max(1, m))
    t = stats.t.ppf(1 - a, n - 1)
    mde = (stats.norm.ppf(1 - a) + stats.norm.ppf(0.80)) * se
    return float(r.mean() - t * se), float(r.mean() + t * se), float(mde)


def verdetto_oos(lo: float, hi: float, dsr: float, min_exp: float = 0.0, min_dsr: float | None = None) -> str:
    """PROMOSSA solo se il limite basso dell'intervallo OOS (gia' corretto per il numero di candidati) sta
    sopra la soglia; con `min_dsr` impostato, serve anche il DSR in-sample. SCARTATA solo se l'intervallo OOS
    sta tutto sotto. Tutto il resto e' NON_DIMOSTRATA: non va in demo e non si scrive "refutata".

    Perche' il DSR non e' obbligatorio (controlli del 07/10): il test OOS sui candidati scelti PRIMA di guardare
    l'OOS, con Bonferroni, e' gia' il test valido. Con DSR >= 0,95 obbligatorio la pipeline non promuoveva
    nemmeno una mean reversion iniettata fortissima (OOS +0,85R, limite basso +0,68R, DSR 0,90): un gate
    irraggiungibile e' rotto quanto uno che fa passare il rumore. Senza DSR: 0 promosse su 9 random walk,
    8 su 8 sui controlli forti."""
    dsr_ok = min_dsr is None or (np.isfinite(dsr) and dsr >= min_dsr)
    if np.isfinite(lo) and lo > min_exp and dsr_ok:
        return "PROMOSSA"
    if np.isfinite(hi) and hi < min_exp:
        return "SCARTATA"
    return "NON_DIMOSTRATA"
