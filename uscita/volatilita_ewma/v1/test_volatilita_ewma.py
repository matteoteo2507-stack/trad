"""Test del pacchetto volatilita_ewma v1 (9 test). Lancio: python -m pytest test_volatilita_ewma.py (dalla cartella v1)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import volatilita_ewma as V  # noqa: E402


def _serie(n: int, seme: int = 1) -> np.ndarray:
    """Rendimenti GJR simulati (in %), con volatilita' che cambia nel tempo."""
    rng = np.random.default_rng(seme)
    r, s2 = np.empty(n), 1.0
    for t in range(n):
        r[t] = np.sqrt(s2) * rng.standard_normal()
        s2 = 0.02 + 0.03 * r[t] ** 2 + 0.08 * r[t] ** 2 * (r[t] < 0) + 0.92 * s2
    return r


def test_ricorsione_a_mano():
    r = np.array([1.0, -2.0, 0.5])
    s0 = V._avvio(r)
    s1 = 0.94 * s0 + 0.06 * 1.0
    s2 = 0.94 * s1 + 0.06 * 4.0
    s3 = 0.94 * s2 + 0.06 * 0.25
    assert np.allclose(V._ewma_grezzo(r, 0.94, 0), [s1, s2, s3])


def test_h5_piatto_e_riscaldamento():
    r = pd.Series(_serie(300), index=pd.bdate_range("2020-01-01", periods=300))
    p = V.previsioni_ewma(r)
    assert p["h1"].iloc[:V.RISCALDAMENTO].isna().all()
    assert np.allclose(p["h5"].dropna(), 5 * p["h1"].dropna())


def test_nessun_dato_futuro_ewma():
    r = _serie(400)
    r2 = r.copy()
    r2[250:] *= 5.0                                   # cambia il futuro dal giorno 250
    a, b = V.ewma(r), V.ewma(r2)
    assert np.allclose(a[:250], b[:250], equal_nan=True)
    assert not np.allclose(a[250:], b[250:])


def test_uguale_ad_arch_ewma():
    arch = pytest.importorskip("arch")
    from arch.univariate import EWMAVariance, ZeroMean

    r = _serie(500)
    res = ZeroMean(r, volatility=EWMAVariance(0.94), rescale=False).fix(np.zeros(0))
    f = res.forecast(horizon=1, start=0, reindex=False).variance.to_numpy()[:, 0]
    assert np.allclose(V._ewma_grezzo(r, 0.94, 0), f, rtol=1e-10)
    assert arch is not None


def test_riscala_e_qlike():
    r = np.ones(10)
    v = np.full(10, 2.0)
    c = V.riscala(r, v, w=4)
    assert np.isnan(c[:3]).all() and np.allclose(c[3:], 2.0)
    assert np.allclose(V.qlike(np.array([2.0]), np.array([2.0])), np.log(2.0) + 1.0)
    with pytest.raises(ValueError):
        V.qlike(np.array([0.0]), np.array([1.0]))


def test_rendimenti():
    p = pd.Series([100.0, 101.0, 99.0])
    r = V.rendimenti(p)
    assert len(r) == 2 and np.isclose(r.iloc[0], 100 * np.log(1.01))
    with pytest.raises(ValueError):
        V.rendimenti(pd.Series([100.0, 0.0]))


def test_nessun_dato_futuro_gjr():
    pytest.importorskip("arch")
    w, n, taglio = 300, 330, 312                      # blocchi da 299 a passi di 5: il taglio cade dentro 309-313
    r = pd.Series(_serie(n, seme=2))
    r2 = r.copy()
    r2.iloc[taglio:] *= 3.0
    a, b = V.previsioni_gjr(r, w=w), V.previsioni_gjr(r2, w=w)
    # le origini prima del taglio, anche quelle del suo blocco (309-311), non vedono il rendimento cambiato
    assert np.allclose(a["h1"].iloc[:taglio], b["h1"].iloc[:taglio], equal_nan=True)


def test_controlli_degli_input():
    with pytest.raises(ValueError):
        V.ewma(np.ones(200), riscaldamento=10)        # l'avvio userebbe dati futuri
    with pytest.raises(ValueError):
        V.qlike(np.array([1.0]), np.array([np.nan]))
    c = V.riscala(np.zeros(6), np.ones(6), w=3)       # nessun movimento: c non definito, non infinito
    assert np.isnan(c).all()


def test_bersaglio_allineato():
    v = np.array([1.0, 2.0, 3.0, 4.0])
    assert np.allclose(V.bersaglio(v, 1), [2.0, 3.0, 4.0, np.nan], equal_nan=True)
    assert np.allclose(V.bersaglio(v, 2), [5.0, 7.0, np.nan, np.nan], equal_nan=True)
