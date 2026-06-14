"""Test per le metriche aggiunte a core.quant_metrics (omega, tail ratio,
benchmark-relative). Sanity check su casi a valore noto."""

import numpy as np

from core import quant_metrics as q


def test_omega_ratio_symmetric_is_one():
    # Distribuzione simmetrica attorno a 0 → guadagni == perdite → Omega ≈ 1.
    r = np.array([-0.02, -0.01, 0.01, 0.02])
    assert abs(q.omega_ratio(r, threshold=0.0) - 1.0) < 1e-9


def test_omega_ratio_no_losses_is_inf():
    r = np.array([0.01, 0.02, 0.03])
    assert q.omega_ratio(r, threshold=0.0) == float("inf")


def test_omega_threshold_shifts_ratio():
    r = np.array([-0.01, 0.0, 0.01, 0.02])
    # Alzando la soglia il ratio non puo aumentare (piu massa diventa "perdita").
    assert q.omega_ratio(r, threshold=0.02) <= q.omega_ratio(r, threshold=0.0)


def test_tail_ratio_left_skew_below_one():
    # Coda sinistra piu pesante → tail ratio < 1.
    r = np.concatenate([np.full(95, 0.01), np.array([-0.5] * 5)])
    assert q.tail_ratio(r) < 1.0


def test_benchmark_metrics_identity():
    rng = np.random.default_rng(42)
    b = rng.normal(0.0005, 0.01, 500)
    # Strategia == benchmark → beta≈1, R²≈1, tracking error≈0, alpha≈0.
    m = q.benchmark_metrics(b, b, rf=0.0)
    assert abs(m["beta"] - 1.0) < 1e-6
    assert abs(m["r_squared"] - 1.0) < 1e-6
    assert m["tracking_error"] < 1e-9
    assert abs(m["alpha"]) < 1e-6


def test_benchmark_metrics_leveraged_beta():
    rng = np.random.default_rng(7)
    b = rng.normal(0.0005, 0.01, 500)
    # Strategia = 2x il benchmark → beta≈2.
    m = q.benchmark_metrics(2.0 * b, b, rf=0.0)
    assert abs(m["beta"] - 2.0) < 1e-6
    assert abs(m["r_squared"] - 1.0) < 1e-6


def test_bca_ci_brackets_point_and_ordered():
    rng = np.random.default_rng(0)
    r = rng.normal(0.0008, 0.01, 600)  # Sharpe positivo
    ci = q.bca_bootstrap_ci(r, conf=0.95, n_boot=800, seed=1)
    assert ci["low"] < ci["point"] < ci["high"]
    assert np.isfinite(ci["bias_correction"])


def test_bca_ci_reproducible_with_seed():
    rng = np.random.default_rng(2)
    r = rng.normal(0.0005, 0.012, 400)
    a = q.bca_bootstrap_ci(r, n_boot=500, seed=42)
    b = q.bca_bootstrap_ci(r, n_boot=500, seed=42)
    assert a["low"] == b["low"] and a["high"] == b["high"]


def test_bca_ci_wider_conf_is_wider():
    rng = np.random.default_rng(3)
    r = rng.normal(0.0006, 0.011, 500)
    c90 = q.bca_bootstrap_ci(r, conf=0.90, n_boot=800, seed=5)
    c99 = q.bca_bootstrap_ci(r, conf=0.99, n_boot=800, seed=5)
    # CI 99% contiene CI 90%.
    assert c99["low"] <= c90["low"]
    assert c99["high"] >= c90["high"]


def test_bca_ci_custom_metric_sortino():
    rng = np.random.default_rng(4)
    r = rng.normal(0.0007, 0.01, 300)
    ci = q.bca_bootstrap_ci(r, metric=lambda x: q.sortino_ratio(x), n_boot=400, seed=7)
    assert ci["low"] <= ci["point"] <= ci["high"]


def test_bca_ci_insufficient_sample():
    ci = q.bca_bootstrap_ci(np.array([0.01, 0.02]), n_boot=100, seed=1)
    assert np.isnan(ci["low"]) and np.isnan(ci["high"])
