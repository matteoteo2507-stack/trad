"""Test di core/verifiche.py.

Come in test_data_checks: i test non verificano solo che le funzioni girino, **riproducono i numeri della
fonte** (distillamento Quant Guild, SINTESI §8) e dimostrano l'equivalenza col codice gia' in uso.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from core import verifiche as v


# ---- buco 2 -------------------------------------------------------------------------------------

def test_fattore_potenza_e_280():
    assert v.fattore_potenza() == pytest.approx(2.8016, abs=1e-3)


def test_mde_e_n_richiesto_sono_inversi():
    sd, n = 2.4, 1792
    assert v.n_richiesto(sd, v.mde(sd, n)) == pytest.approx(n, abs=1)


def test_n_richiesto_riproduce_b22():
    # SINTESI B22: con E = +0,04R servono ~36.000 trade (sd ~2,7R)
    assert 35_000 < v.n_richiesto(2.7, 0.04) < 37_000


# ---- buco 37 ------------------------------------------------------------------------------------

def test_pvalue_mc_048_e_062_non_distinguibili():
    # SINTESI F2: con 1.000 permutazioni il SE di un p ~0,05 e' ~0,7 punti
    a, b = v.pvalue_mc(48, 1000), v.pvalue_mc(62, 1000)
    assert a["se"] == pytest.approx(0.0069, abs=5e-4)
    assert not v.pvalue_distinguibile(a, 0.05) and not v.pvalue_distinguibile(b, 0.05)


def test_pvalue_mc_non_vale_mai_zero():
    r = v.pvalue_mc(0, 1000)
    assert r["p_grezzo"] == 0 and r["p"] == pytest.approx(1 / 1001)


def test_repliche_per_distinguere():
    # per stringere l'intervallo a +/-0,005 attorno a 0,05 servono ~7.300 repliche
    assert 7_000 < v.repliche_per_distinguere(0.05, 0.005) < 7_500


def test_mc_permutation_test_riporta_errore_del_p():
    from core.quant_metrics import mc_permutation_test
    r = mc_permutation_test(np.random.default_rng(0).normal(0.001, 0.01, 500), n_perm=200, seed=1)
    for campo in ("p_value", "p_corretto", "p_se", "p_low", "p_high"):
        assert campo in r
    assert r["p_corretto"] > 0


# ---- buco 29 ------------------------------------------------------------------------------------

def _runs_a_mano(w):
    """Copia letterale della formula di analysis/mentor_signals/withdrawal_thresholds.py (C3, 18/09)."""
    n = w.size
    runs = 1 + int((w[1:] != w[:-1]).sum())
    n1, n0 = int(w.sum()), int(n - w.sum())
    mu = 2 * n1 * n0 / n + 1
    sd = np.sqrt(2 * n1 * n0 * (2 * n1 * n0 - n) / (n * n * (n - 1)))
    return (runs - mu) / sd


def test_runs_test_equivalente_alla_formula_in_uso():
    w = np.random.default_rng(3).random(629) < 0.6
    assert v.runs_test(w)["z"] == pytest.approx(_runs_a_mano(w), abs=1e-12)


def test_runs_test_riconosce_esiti_raggruppati():
    w = np.array(([True] * 10 + [False] * 10) * 10)
    r = v.runs_test(w)
    assert r["z"] < -3 and "RAGGRUPPATI" in r["lettura"]


def test_runs_test_senza_perdite_non_calcolabile():
    assert math.isnan(v.runs_test([True] * 20)["z"])


# ---- buco 22 ------------------------------------------------------------------------------------

def test_eccedenze_riproduce_il_var_inservibile():
    # blocco D: VaR a varianza costante, 40% di eccedenze contro 5% attese
    r = v.test_eccedenze(100, 0.05, n=250)
    assert "SOTTOSTIMA" in r["verdetto"] and r["p_lr"] < 1e-10


def test_eccedenze_tarata_e_compatibile():
    r = v.test_eccedenze(13, 0.05, n=250)
    assert r["verdetto"].startswith("compatibile")


def test_eccedenze_da_array():
    viol = np.zeros(200, dtype=bool)
    viol[:2] = True
    r = v.test_eccedenze(viol, 0.05)
    assert r["eccedenze"] == 2 and "prudente" in r["verdetto"]


# ---- buco 27 ------------------------------------------------------------------------------------

@pytest.mark.parametrize("q,k,atteso", [(0.5, 5, 62), (0.5, 4, 30), (0.6, 5, 29.65)])
def test_attesa_serie_perdite_riproduce_la_tabella(q, k, atteso):
    # blocco D, D6: win rate 50% -> 5 perdite di fila attese entro ~62 operazioni; 4 entro 30
    assert v.attesa_trade_prima_di_k_perdite(q, k) == pytest.approx(atteso, abs=0.05)


def test_prob_serie_perdite_coincide_con_la_simulazione():
    rng = np.random.default_rng(7)
    q, k, n = 0.45, 4, 60
    sims = rng.random((20_000, n)) < q
    def ha_serie(riga):
        c = 0
        for x in riga:
            c = c + 1 if x else 0
            if c >= k:
                return True
        return False
    emp = np.mean([ha_serie(r) for r in sims])
    assert v.prob_serie_perdite(q, k, n) == pytest.approx(emp, abs=0.012)


# ---- buchi 5 + 28 -------------------------------------------------------------------------------

def test_sprt_vede_il_degrado_e_non_da_falsi_allarmi_in_linea():
    rng = np.random.default_rng(11)
    degradato = v.SPRTBernoulli(p0=0.6, p1=0.45)
    stati = [degradato.aggiorna(x) for x in rng.random(400) < 0.45]
    assert "degrado" in stati
    in_linea = v.SPRTBernoulli(p0=0.6, p1=0.45)
    falsi = sum(in_linea.aggiorna(x) == "degrado" for x in rng.random(300) < 0.6)
    assert falsi <= 1


def test_sprt_parametri_invalidi():
    with pytest.raises(ValueError):
        v.SPRTBernoulli(p0=0.4, p1=0.5)


def test_cusum_allarme_solo_dopo_la_rottura():
    rng = np.random.default_rng(5)
    c = v.CUSUMInferiore(mu0=0.13, sigma0=1.0)
    prima = [c.aggiorna(r) for r in rng.normal(0.13, 1.0, 300)]
    assert not any(prima)
    dopo = [c.aggiorna(r) for r in rng.normal(-0.87, 1.0, 60)]
    assert any(dopo)
    assert c.riepilogo_innovazioni()["media"] < 0


# ---- buco 46 ------------------------------------------------------------------------------------

def test_correlazione_dichiarata_mostra_le_punte():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2018-01-01", periods=1500)
    x = pd.Series(rng.normal(0, 0.01, len(idx)), idx)
    y = pd.Series(rng.normal(0, 0.01, len(idx)), idx)
    y.iloc[600:660] = x.iloc[600:660] * 0.9 + rng.normal(0, 0.002, 60)   # un episodio di contagio
    r = v.correlazione_dichiarata(x, y, "D", 60)
    assert abs(r["intero_campione"]) < 0.15 and r["mobile_max"] > 0.7
    assert r["frequenza"] == "D" and r["finestra"] == 60
