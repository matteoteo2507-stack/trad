"""Quant metrics for strategy review.

Implementazioni delle metriche statistiche usate dal Quant Reviewer
(agents/quant_reviewer.md). Riferimenti:

- Bailey D., López de Prado M. (2014) — The Deflated Sharpe Ratio. SSRN 2460551.
- Bailey, Borwein, López de Prado, Zhu (2017) — The Probability of Backtest
  Overfitting. J. Computational Finance 20(4).
- López de Prado M. (2018) — Advances in Financial Machine Learning. Wiley.
  (cap. 7 CPCV, cap. 11 PBO, cap. 14 backtest statistics).
- Harvey, Hoyle, Korgaonkar (2018) — The Impact of Volatility Targeting. JPM.
- White H. (2000) — A Reality Check for Data Snooping. Econometrica 68(5).

Le funzioni sono pure su array/Series numerici di returns. Periodo dei returns
e tasso risk-free **annualizzati con lo stesso fattore** (`periods_per_year`).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb, erf, sqrt
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Sharpe family
# ---------------------------------------------------------------------------

def sharpe_ratio(
    returns: np.ndarray | pd.Series,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Annualized Sharpe ratio classico.

    SR_annual = sqrt(P) * (mean(r) - rf/P) / std(r, ddof=1)
    """
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return float("nan")
    rf_per = rf / periods_per_year
    excess = r - rf_per
    sd = excess.std(ddof=1)
    if sd == 0:
        return float("nan")
    return float(np.sqrt(periods_per_year) * excess.mean() / sd)


def probabilistic_sharpe_ratio(
    sr_observed: float,
    sr_benchmark: float,
    n: int,
    skew: float,
    kurt_excess: float,
) -> float:
    """PSR — Bailey & López de Prado (2012, 2014).

    Probabilità che lo Sharpe vero sia > sr_benchmark dato lo Sharpe osservato
    su N osservazioni, corretta per skew/kurtosis.
    """
    if n < 2:
        return float("nan")
    num = (sr_observed - sr_benchmark) * sqrt(n - 1)
    den = sqrt(1 - skew * sr_observed + (kurt_excess / 4.0) * sr_observed ** 2)
    if den <= 0:
        return float("nan")
    return float(_norm_cdf(num / den))


def deflated_sharpe_ratio(
    returns: np.ndarray | pd.Series,
    n_trials: int,
    periods_per_year: int = 252,
) -> dict:
    """Deflated Sharpe Ratio — Bailey & López de Prado (SSRN 2460551, 2014).

    Corregge lo Sharpe osservato per il numero di trial testati N e per le
    proprietà non-gaussiane della distribuzione (skew, excess kurtosis).

    Restituisce dict con:
      - sr_observed: Sharpe osservato (annualizzato).
      - sr_threshold: Sharpe minimo richiesto al livello 95% data la
        molteplicità N.
      - dsr: Probabilistic Sharpe Ratio vs threshold (Bailey-LdP).
      - significant_95: True se dsr > 0.95.

    Note: il "threshold" implementa l'equazione (4) di Bailey-LdP 2014:
        E[max SR | N i.i.d. trial null] ≈
          (1 - γ) * Φ^-1(1 - 1/N) + γ * Φ^-1(1 - 1/N * e^-1)
    dove γ = costante di Eulero-Mascheroni ≈ 0.5772.
    """
    r = np.asarray(returns, dtype=float)
    if r.size < 2 or n_trials < 1:
        return {"sr_observed": float("nan"), "sr_threshold": float("nan"),
                "dsr": float("nan"), "significant_95": False}

    sr_obs = sharpe_ratio(r, rf=0.0, periods_per_year=periods_per_year)
    sr_obs_per = sr_obs / sqrt(periods_per_year)  # SR per-period
    skew = float(stats.skew(r, bias=False))
    kurt_ex = float(stats.kurtosis(r, fisher=True, bias=False))
    n = r.size

    # Threshold E[max SR] sotto null hypothesis di N trial gaussiani indipendenti.
    if n_trials == 1:
        sr_thr_per = 0.0
    else:
        gamma = 0.5772156649  # Eulero-Mascheroni
        z1 = _norm_inv(1.0 - 1.0 / n_trials)
        z2 = _norm_inv(1.0 - 1.0 / (n_trials * np.e))
        sr_thr_per = (1.0 - gamma) * z1 + gamma * z2
        sr_thr_per /= sqrt(n)  # threshold sullo SR osservato (per-period)

    dsr = probabilistic_sharpe_ratio(
        sr_observed=sr_obs_per,
        sr_benchmark=sr_thr_per,
        n=n,
        skew=skew,
        kurt_excess=kurt_ex,
    )

    return {
        "sr_observed": sr_obs,
        "sr_threshold": float(sr_thr_per * sqrt(periods_per_year)),
        "dsr": dsr,
        "significant_95": bool(dsr > 0.95),
        "skew": skew,
        "kurt_excess": kurt_ex,
        "n_obs": n,
        "n_trials": n_trials,
    }


# ---------------------------------------------------------------------------
# PBO via CSCV — Bailey-Borwein-LdP-Zhu (2017)
# ---------------------------------------------------------------------------

def pbo_cscv(
    returns_matrix: np.ndarray | pd.DataFrame,
    s: int = 16,
    metric: Callable[[np.ndarray], float] | None = None,
) -> dict:
    """Probability of Backtest Overfitting via Combinatorially Symmetric CV.

    Args:
        returns_matrix: matrice T × N, dove T = sample length, N = numero di
            configurazioni/strategie testate. Ogni colonna = serie di returns
            di una configurazione.
        s: numero di sotto-periodi in cui spezzare T (deve essere pari).
            Standard: 16. Genera C(s, s/2) combinazioni di partizioni.
        metric: funzione che mappa returns → score (default: Sharpe).

    Returns:
        dict con:
          - pbo: probabilità che il best IS sia sotto la mediana OOS.
          - logits: array di logit(rank_oos / (N+1)) per ogni combinazione.
          - n_combos: numero di partizioni valutate.

    Interpretazione: PBO < 0.15 accettabile; > 0.30 sospetto; > 0.50 random.
    """
    if metric is None:
        metric = lambda r: sharpe_ratio(r, periods_per_year=1)  # noqa: E731

    R = np.asarray(returns_matrix, dtype=float)
    if R.ndim != 2:
        raise ValueError("returns_matrix deve essere 2D (T × N)")
    if s % 2 != 0:
        raise ValueError("s deve essere pari")

    T, N = R.shape
    if T < s or N < 2:
        return {"pbo": float("nan"), "logits": np.array([]), "n_combos": 0}

    # Split T in s sotto-periodi.
    chunk_size = T // s
    chunks = [R[i * chunk_size:(i + 1) * chunk_size] for i in range(s)]

    half = s // 2
    logits = []
    for combo in combinations(range(s), half):
        is_idx = set(combo)
        oos_idx = [i for i in range(s) if i not in is_idx]

        is_data = np.vstack([chunks[i] for i in combo])
        oos_data = np.vstack([chunks[i] for i in oos_idx])

        is_scores = np.array([metric(is_data[:, j]) for j in range(N)])
        oos_scores = np.array([metric(oos_data[:, j]) for j in range(N)])

        # Mask configurazioni con score NaN/inf.
        valid = np.isfinite(is_scores) & np.isfinite(oos_scores)
        if valid.sum() < 2:
            continue

        # Rank OOS della config che era IS-best.
        is_best = np.argmax(np.where(valid, is_scores, -np.inf))
        # Rank percentile della OOS-performance del IS-best.
        oos_valid = oos_scores[valid]
        rank = (oos_valid < oos_scores[is_best]).sum()
        n_valid = valid.sum()
        # Rank normalizzato in (0, 1) — clip per evitare logit infinito.
        w = (rank + 1) / (n_valid + 1)
        w = min(max(w, 1e-9), 1.0 - 1e-9)
        logits.append(np.log(w / (1.0 - w)))

    logits = np.asarray(logits)
    if logits.size == 0:
        return {"pbo": float("nan"), "logits": logits, "n_combos": 0}

    # PBO = P(logit < 0) = frazione di combinazioni in cui IS-best è sotto
    # mediana OOS.
    pbo = float((logits < 0).mean())
    return {"pbo": pbo, "logits": logits, "n_combos": int(logits.size)}


# ---------------------------------------------------------------------------
# CPCV — Combinatorial Purged CV (López de Prado 2018, cap. 7)
# ---------------------------------------------------------------------------

@dataclass
class CPCVSplit:
    """Single train/test split from CPCV."""
    train_idx: np.ndarray
    test_idx: np.ndarray


def cpcv_splits(
    n_samples: int,
    n_groups: int = 6,
    k_test_groups: int = 2,
    embargo_pct: float = 0.01,
    sample_horizons: np.ndarray | None = None,
) -> list[CPCVSplit]:
    """Combinatorial Purged CV — López de Prado (2018) cap. 7.

    Args:
        n_samples: numero di sample T.
        n_groups: numero di gruppi in cui spezzare T (N).
        k_test_groups: gruppi assegnati al test (k). Genera C(N, k) split.
        embargo_pct: frazione di T da escludere dopo ogni test set (embargo).
        sample_horizons: array di lunghezza T con l'orizzonte (in sample) di
            ogni label. Se None, assume horizon=1 (no purging extra).

    Returns:
        Lista di CPCVSplit. Train_idx esclude (i) sample del test set, (ii)
        sample con horizon che si sovrappone al test set (purging),
        (iii) sample in embargo dopo il test set.
    """
    if n_groups < 2 or k_test_groups < 1 or k_test_groups >= n_groups:
        raise ValueError("n_groups >= 2 e 1 <= k_test_groups < n_groups")
    if sample_horizons is None:
        sample_horizons = np.ones(n_samples, dtype=int)
    if len(sample_horizons) != n_samples:
        raise ValueError("sample_horizons deve avere lunghezza n_samples")

    embargo = int(n_samples * embargo_pct)
    group_size = n_samples // n_groups
    group_bounds = [
        (i * group_size, n_samples if i == n_groups - 1 else (i + 1) * group_size)
        for i in range(n_groups)
    ]

    splits = []
    for combo in combinations(range(n_groups), k_test_groups):
        test_mask = np.zeros(n_samples, dtype=bool)
        for g in combo:
            lo, hi = group_bounds[g]
            test_mask[lo:hi] = True

        # Purging: rimuovi train sample il cui horizon entra nel test set.
        train_mask = ~test_mask
        for i in np.where(train_mask)[0]:
            end_i = min(i + int(sample_horizons[i]), n_samples)
            if test_mask[i:end_i].any():
                train_mask[i] = False

        # Embargo: dopo ogni blocco test, escludi `embargo` sample da train.
        if embargo > 0:
            for g in combo:
                _, hi = group_bounds[g]
                emb_end = min(hi + embargo, n_samples)
                train_mask[hi:emb_end] = False

        splits.append(CPCVSplit(
            train_idx=np.where(train_mask)[0],
            test_idx=np.where(test_mask)[0],
        ))
    return splits


# ---------------------------------------------------------------------------
# Walk-forward
# ---------------------------------------------------------------------------

@dataclass
class WalkForwardResult:
    is_sharpes: list[float]
    oos_sharpes: list[float]
    is_mean: float
    oos_mean: float
    degradation: float  # (is_mean - oos_mean) / is_mean


def walk_forward(
    returns: np.ndarray | pd.Series,
    train_size: int,
    test_size: int,
    anchored: bool = False,
    periods_per_year: int = 252,
) -> WalkForwardResult:
    """Walk-forward analysis.

    Args:
        returns: serie storica di returns già generata dalla strategia.
        train_size: lunghezza finestra di training.
        test_size: lunghezza finestra di test (sliding).
        anchored: se True, train cresce; se False, sliding fisso.

    Returns:
        WalkForwardResult con Sharpe IS e OOS per ogni step + degrado medio.

    NB: questa funzione richiede che `returns` sia già stato generato
    out-of-strategy-config. Non riottimizza i parametri per ogni fold — quella
    è responsabilità del caller, che dovrebbe invocare walk_forward su returns
    risultanti da diverse ottimizzazioni IS.
    """
    r = np.asarray(returns, dtype=float)
    n = r.size
    if train_size + test_size > n:
        raise ValueError("train_size + test_size > len(returns)")

    is_sr, oos_sr = [], []
    start = 0
    train_end = train_size
    while train_end + test_size <= n:
        is_slice = r[start:train_end] if anchored else r[train_end - train_size:train_end]
        oos_slice = r[train_end:train_end + test_size]
        is_sr.append(sharpe_ratio(is_slice, periods_per_year=periods_per_year))
        oos_sr.append(sharpe_ratio(oos_slice, periods_per_year=periods_per_year))
        train_end += test_size
        if not anchored:
            start += test_size

    is_arr = np.array(is_sr)
    oos_arr = np.array(oos_sr)
    is_mean = float(np.nanmean(is_arr)) if is_arr.size else float("nan")
    oos_mean = float(np.nanmean(oos_arr)) if oos_arr.size else float("nan")
    deg = (is_mean - oos_mean) / is_mean if is_mean and not np.isnan(is_mean) else float("nan")
    return WalkForwardResult(is_sr, oos_sr, is_mean, oos_mean, deg)


# ---------------------------------------------------------------------------
# Monte Carlo permutation
# ---------------------------------------------------------------------------

def mc_permutation_test(
    returns: np.ndarray | pd.Series,
    n_perm: int = 1000,
    block_size: int = 1,
    seed: int | None = None,
    periods_per_year: int = 252,
) -> dict:
    """Monte Carlo permutation: distribuzione null dello Sharpe shuffling
    i returns (block bootstrap se i returns sono autocorrelati).

    Returns:
        dict con:
          - sr_observed: Sharpe osservato.
          - p_value: P(SR_perm >= SR_obs) sotto null.
          - sr_distribution: array degli Sharpe shufflati.
    """
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return {"sr_observed": float("nan"), "p_value": float("nan"),
                "sr_distribution": np.array([])}
    rng = np.random.default_rng(seed)
    sr_obs = sharpe_ratio(r, periods_per_year=periods_per_year)

    if block_size <= 1:
        sims = np.array([
            sharpe_ratio(rng.permutation(r), periods_per_year=periods_per_year)
            for _ in range(n_perm)
        ])
    else:
        n_blocks = int(np.ceil(r.size / block_size))
        sims = []
        for _ in range(n_perm):
            starts = rng.integers(0, r.size - block_size + 1, size=n_blocks)
            sampled = np.concatenate([r[s:s + block_size] for s in starts])[:r.size]
            sims.append(sharpe_ratio(sampled, periods_per_year=periods_per_year))
        sims = np.array(sims)

    p_value = float((sims >= sr_obs).mean())
    return {
        "sr_observed": sr_obs,
        "p_value": p_value,
        "sr_distribution": sims,
    }


# ---------------------------------------------------------------------------
# Risk metrics oltre lo Sharpe
# ---------------------------------------------------------------------------

def sortino_ratio(
    returns: np.ndarray | pd.Series,
    rf: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return float("nan")
    rf_per = rf / periods_per_year
    excess = r - rf_per
    downside = excess[excess < 0]
    if downside.size == 0:
        return float("inf")
    dd = np.sqrt(np.mean(downside ** 2))
    if dd == 0:
        return float("nan")
    return float(np.sqrt(periods_per_year) * excess.mean() / dd)


def max_drawdown(returns: np.ndarray | pd.Series) -> dict:
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return {"max_dd": float("nan"), "peak_idx": -1, "trough_idx": -1}
    equity = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    trough = int(np.argmin(dd))
    peak_idx = int(np.argmax(equity[:trough + 1])) if trough > 0 else 0
    return {"max_dd": float(dd.min()), "peak_idx": peak_idx, "trough_idx": trough}


def calmar_ratio(
    returns: np.ndarray | pd.Series,
    periods_per_year: int = 252,
) -> float:
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return float("nan")
    ann_return = (1 + r).prod() ** (periods_per_year / r.size) - 1
    mdd = abs(max_drawdown(r)["max_dd"])
    return float(ann_return / mdd) if mdd > 0 else float("nan")


def ulcer_index(returns: np.ndarray | pd.Series) -> float:
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return float("nan")
    equity = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(equity)
    dd_pct = (equity - peak) / peak * 100
    return float(np.sqrt(np.mean(dd_pct ** 2)))


def tail_metrics(returns: np.ndarray | pd.Series) -> dict:
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return {"cvar_95": float("nan"), "cvar_99": float("nan"),
                "skew": float("nan"), "kurt_excess": float("nan")}
    var_95 = np.quantile(r, 0.05)
    var_99 = np.quantile(r, 0.01)
    cvar_95 = r[r <= var_95].mean() if (r <= var_95).any() else float("nan")
    cvar_99 = r[r <= var_99].mean() if (r <= var_99).any() else float("nan")
    return {
        "cvar_95": float(cvar_95),
        "cvar_99": float(cvar_99),
        "skew": float(stats.skew(r, bias=False)),
        "kurt_excess": float(stats.kurtosis(r, fisher=True, bias=False)),
    }


# ---------------------------------------------------------------------------
# White's Reality Check (versione semplice, single-step)
# ---------------------------------------------------------------------------

def whites_reality_check(
    returns_matrix: np.ndarray | pd.DataFrame,
    benchmark: np.ndarray | pd.Series | None = None,
    n_boot: int = 500,
    block_size: int = 5,
    seed: int | None = None,
) -> dict:
    """White's Reality Check (Econometrica 2000), variante stationary
    bootstrap.

    Null: max_k E[f_k - f_bench] <= 0. Stat di test: max_k mean(f_k - f_bench).
    Distribuzione null via bootstrap stazionario.

    Args:
        returns_matrix: T × N matrice di returns delle N strategie/varianti.
        benchmark: serie T del benchmark; se None, usa zeros (test "qualcuno
            ha mean return > 0").
        n_boot: numero di replicazioni bootstrap.
        block_size: lunghezza media dei blocchi nello stationary bootstrap.

    Returns:
        dict con stat osservata, p-value, e indice della strategia migliore.
    """
    R = np.asarray(returns_matrix, dtype=float)
    if R.ndim != 2:
        raise ValueError("returns_matrix deve essere 2D")
    T, N = R.shape
    if benchmark is None:
        bench = np.zeros(T)
    else:
        bench = np.asarray(benchmark, dtype=float)
    diffs = R - bench[:, None]   # T × N
    obs_means = diffs.mean(axis=0)
    obs_stat = obs_means.max()
    best_idx = int(np.argmax(obs_means))

    rng = np.random.default_rng(seed)
    p = 1.0 / block_size  # stationary bootstrap geometric block length
    boot_stats = np.empty(n_boot)
    for b in range(n_boot):
        idx = _stationary_bootstrap_indices(T, p, rng)
        sample = diffs[idx]
        boot_means = sample.mean(axis=0) - obs_means  # centering
        boot_stats[b] = boot_means.max()

    p_value = float((boot_stats >= obs_stat).mean())
    return {
        "obs_stat": float(obs_stat),
        "p_value": p_value,
        "best_strategy_idx": best_idx,
        "best_strategy_mean": float(obs_means[best_idx]),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_inv(p: float) -> float:
    """Quantile della normale standard via scipy."""
    return float(stats.norm.ppf(p))


def _stationary_bootstrap_indices(t: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Politis & Romano (1994) stationary bootstrap."""
    idx = np.empty(t, dtype=int)
    idx[0] = rng.integers(0, t)
    for i in range(1, t):
        if rng.random() < p:
            idx[i] = rng.integers(0, t)
        else:
            idx[i] = (idx[i - 1] + 1) % t
    return idx
