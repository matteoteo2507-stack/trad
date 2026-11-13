"""Test di motore/core/verifiche.py.

Come in test_data_checks: i test non verificano solo che le funzioni girino, **riproducono i numeri della
fonte** (distillamento Quant Guild, SINTESI §8) e dimostrano l'equivalenza col codice gia' in uso.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from motore.core import verifiche as v


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
    from motore.core.quant_metrics import mc_permutation_test
    r = mc_permutation_test(np.random.default_rng(0).normal(0.001, 0.01, 500), n_perm=200, seed=1)
    for campo in ("p_value", "p_corretto", "p_se", "p_low", "p_high"):
        assert campo in r
    assert r["p_corretto"] > 0


# ---- buco 29 ------------------------------------------------------------------------------------

def _runs_a_mano(w):
    """Copia letterale della formula di magazzino/registro/codice/mentor_signals/withdrawal_thresholds.py (C3, 18/09)."""
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


# =================================================================================================
# Priorita' 2
# =================================================================================================

# ---- buco 15 ------------------------------------------------------------------------------------

def test_challenge_senza_edge_passa_nel_56_per_cento():
    # blocco C, C2: +8% / -10% con edge zero -> 10/18
    assert v.prob_obiettivo_prima_del_limite(0.0, 1.0, 8, 10) == pytest.approx(10 / 18)


def test_continuo_e_discreto_concordano():
    # passi di 1% con p = 0,52: deriva 0,04 e varianza ~1 per passo
    p = 0.52
    disc = v.rovina_del_giocatore(p, 8, 10)
    cont = v.prob_obiettivo_prima_del_limite(2 * p - 1, math.sqrt(1 - (2 * p - 1) ** 2), 8, 10)
    assert cont == pytest.approx(disc, abs=0.02)
    assert disc > 10 / 18


def test_rovina_simmetrica():
    assert v.rovina_del_giocatore(0.5, 3, 7) == pytest.approx(0.7)


# ---- buco 16 ------------------------------------------------------------------------------------

def test_kelly_parabola_e_frazione():
    mu, sigma = 0.1, 0.5
    fstar = v.kelly_ottimo(mu, sigma)
    assert fstar == pytest.approx(0.4)
    gmax = v.kelly_crescita(fstar, mu, sigma)
    assert v.kelly_crescita(0.5 * fstar, mu, sigma) / gmax == pytest.approx(0.75)
    assert v.kelly_crescita(2 * fstar, mu, sigma) == pytest.approx(0.0, abs=1e-12)  # oltre 2f* si perde
    k = v.kelly_frazionario(0.5)
    assert k["crescita_relativa"] == 0.75 and k["varianza_relativa"] == 0.25
    assert v.kelly_frazionario(1.0)["prob_meta_capitale"] == pytest.approx(0.5)
    assert k["prob_meta_capitale"] == pytest.approx(0.125)


# ---- buchi 13 + 39 -------------------------------------------------------------------------------

def test_incertezza_sui_parametri_allarga_la_coda():
    r = np.random.default_rng(9).normal(0.1, 1.0, 150)
    senza = v.rischio_percorsi(r, 200, n_sim=3000, incertezza_parametri=False, seed=1)
    con = v.rischio_percorsi(r, 200, n_sim=3000, incertezza_parametri=True, seed=1)
    assert np.percentile(con["max_drawdown"], 95) > np.percentile(senza["max_drawdown"], 95)


def test_probabilita_violazione_del_95esimo_percentile_vale_5_per_cento():
    r = np.random.default_rng(4).normal(0.1, 1.0, 300)
    sim = v.rischio_percorsi(r, 200, n_sim=4000, seed=2)
    soglia = float(np.percentile(sim["max_drawdown"], 95))
    pv = v.probabilita_violazione(sim["max_drawdown"], soglia)
    assert pv["prob"] == pytest.approx(0.05, abs=0.005) and pv["low"] < 0.05 < pv["high"] + 0.005


# ---- buco 45 ------------------------------------------------------------------------------------

def test_confronto_decile_peggiore_cambia_segno():
    rng = np.random.default_rng(6)
    a = rng.normal(0.12, 0.40, 5000)     # media piu' alta, coda piu' brutta
    b = rng.normal(0.08, 0.10, 5000)
    r = v.confronto_decile_peggiore(a, b)
    assert r["diff_media"] > 0 and r["diff_coda"] < 0 and r["segno_cambia"]


# =================================================================================================
# Priorita' 3
# =================================================================================================

def test_matrice_transizione_con_errore_e_zeri():
    seq = [0, 0, 1, 0, 0, 1, 1, 0, 0, 0] * 30
    m = v.matrice_transizione(seq, n_stati=3)
    assert np.allclose(np.nansum(m["p"][:2], axis=1), 1)
    assert m["se"][0, 1] > 0
    assert (0, 2, int(m["n_riga"][0])) in m["zero_osservati"]          # mai visto, non impossibile
    assert m["limite_superiore_zero"][(0, 2)] == pytest.approx(3 / m["n_riga"][0])


def test_transizioni_vietate():
    ammesse = {("flat", "long"), ("long", "flat"), ("flat", "flat"), ("long", "long")}
    seq = ["flat", "long", "long", "short", "flat"]
    assert [(a, b) for _, a, b in v.transizioni_vietate(seq, ammesse)] == [("long", "short"), ("short", "flat")]


def test_perturbazione_distingue_stabile_da_fragile():
    stabile = v.test_perturbazione(lambda a, b: a + b, {"a": 10.0, "b": 5}, frazione=0.1, soglia=0.2)
    fragile = v.test_perturbazione(lambda a: 1.0 if 9.95 < a < 10.05 else -1.0, {"a": 10.0})
    assert stabile["stabile"] and not fragile["stabile"]


def test_ripeti_su_semi_misura_la_dispersione():
    r = v.ripeti_su_semi(lambda s: np.random.default_rng(s).normal(0, 1, 50).mean(), range(30))
    assert r["n_semi"] == 30 and 0.05 < r["sd"] < 0.3


def test_correlazione_in_drawdown_vede_il_contagio():
    # gambe indipendenti, tranne un crollo comune di ~20% (60 giorni) seguito da una ripresa
    rng = np.random.default_rng(8)
    idx = pd.bdate_range("2015-01-01", periods=2000)
    x = pd.Series(rng.normal(0.0004, 0.01, len(idx)), idx)
    y = pd.Series(rng.normal(0.0004, 0.01, len(idx)), idx)
    shock = rng.normal(-0.004, 0.01, 60)
    x.iloc[900:960] = shock + rng.normal(0, 0.002, 60)
    y.iloc[900:960] = shock + rng.normal(0, 0.002, 60)
    x.iloc[960:1020] = rng.normal(0.004, 0.01, 60)
    y.iloc[960:1020] = rng.normal(0.004, 0.01, 60)
    r = v.correlazione_in_drawdown(x, y, soglia_dd=0.10)
    assert 20 < r["periodi_stress"] < 400
    assert r["intero_campione"] < 0.2 and r["in_drawdown"] > r["intero_campione"] + 0.15


def test_fattore_potenza_una_coda_con_holm():
    """G1 della volatilita' (13/11/2026): a una coda con Holm su 18 coppie il fattore non e' 2,80."""
    from motore.core.verifiche import fattore_potenza, mde
    assert abs(fattore_potenza() - 2.80) < 0.01                      # default invariato: due code al 5%
    assert abs(fattore_potenza(0.025 / 18, code=1) - 3.83) < 0.01    # nodo GARCH, prima soglia di Holm
    assert abs(fattore_potenza(0.0125 / 18, code=1) - 4.04) < 0.01   # nodo HMM
    assert abs(fattore_potenza(0.0125, code=1) - 3.08) < 0.01        # premio di volatilita'
    assert mde(1.0, 100, alpha=0.05, code=1) < mde(1.0, 100)         # una coda: MDE piu' stretto a pari alpha


def test_procedura_grafica_un_nodo_e_holm():
    from motore.core.verifiche import procedura_grafica_nodi
    p = {"a": 0.01, "b": 0.02, "c": 0.04, "d": 0.30}
    r = procedura_grafica_nodi({"N": p}, {"N": 0.05})["rifiutate"]["N"]
    # Holm a 0,05 su 4: 0,01 <= 0,0125 si'; 0,02 <= 0,0167 no -> si ferma
    assert r == ["a"]


def test_procedura_grafica_ricicla_ai_nodi_alla_pari():
    from motore.core.verifiche import procedura_grafica_nodi
    pv = {"G": {"g1": 1e-6, "g2": 1e-6}, "H": {"h1": 0.03, "h2": 0.9}, "P": {"p": 0.024}}
    out = procedura_grafica_nodi(pv, {"G": 0.025, "H": 0.0125, "P": 0.0125})["rifiutate"]
    # G esaurito: 0,025 va 0,0125 a H e 0,0125 a P -> H 0,025 (soglia 0,0125 su 2), P 0,025: p si';
    # P esaurito: H 0,05, soglia 0,025 su 2 -> h1 = 0,03 no
    assert out["G"] == ["g1", "g2"] and out["P"] == ["p"] and out["H"] == []
    # P esaurito: la sua quota (0,025) va a H, unico vivo -> H 0,05, soglia 0,025 su 2: h1 = 0,016 si'
    pv["H"]["h1"] = 0.016
    out = procedura_grafica_nodi(pv, {"G": 0.025, "H": 0.0125, "P": 0.0125})["rifiutate"]
    assert out["H"] == ["h1"]


def test_mde_con_t_di_student():
    from motore.core.verifiche import fattore_potenza
    assert fattore_potenza(0.0125, code=1, gl=22) > fattore_potenza(0.0125, code=1)   # 23 mesi: soglia piu' alta


def test_procedura_grafica_intervallo_a_ogni_passo():
    """Un p puntuale sotto la soglia ma con l'intervallo che la contiene non si rifiuta (G1 volatilita', 13/11)."""
    import pytest
    from motore.core.verifiche import procedura_grafica_nodi
    pv = {"N": {"a": 0.024, "b": 0.040}}
    # senza intervalli: soglia 0,025 -> a si'; poi 0,05 -> b si'
    assert procedura_grafica_nodi(pv, {"N": 0.05})["rifiutate"]["N"] == ["a", "b"]
    # a ha l'intervallo (0,020; 0,028) che contiene la soglia 0,025: non si rifiuta, e b resta alla soglia 0,025
    out = procedura_grafica_nodi(pv, {"N": 0.05}, intervalli={"N": {"a": (0.020, 0.028), "b": (0.038, 0.042)}})
    assert out["rifiutate"]["N"] == []
    with pytest.raises(ValueError):
        procedura_grafica_nodi({"N": {}, "M": {"x": 0.001}}, {"N": 0.01, "M": 0.01})


def _perdite_sintetiche(seed=0, n=500):
    rng = np.random.default_rng(seed)
    bench = rng.normal(1.0, 0.2, n)
    buono = bench - 0.06 + rng.normal(0, 0.2, n)        # vantaggio netto, rumore moderato
    rumoroso = bench + rng.normal(0, 3.0, n)            # nessun vantaggio, rumore enorme
    return bench, buono, rumoroso


def test_spa_studentizzato_con_un_modello_coincide_con_arch():
    from arch.bootstrap import SPA
    from motore.core.verifiche import spa_studentizzato
    bench, buono, _ = _perdite_sintetiche()
    a = SPA(bench, buono[:, None], reps=2000, seed=7); a.compute()
    s = spa_studentizzato(bench, buono[:, None], reps=2000, seed=7)
    assert abs(a.pvalues["consistent"] - s.pvalues["consistent"]) < 1e-12


def test_spa_studentizzato_non_perde_il_modello_buono_accanto_a_uno_rumoroso():
    """G1 della volatilita' (13/11/2026): con arch il modello rumoroso fa salire il p; studentizzato no."""
    from arch.bootstrap import SPA
    from motore.core.verifiche import spa_studentizzato
    bench, buono, rumoroso = _perdite_sintetiche()
    modelli = np.column_stack([buono, rumoroso])
    grezzo = SPA(bench, modelli, reps=2000, seed=7); grezzo.compute()
    stud = spa_studentizzato(bench, modelli, reps=2000, seed=7)
    assert stud.pvalues["consistent"] < 0.01
    assert grezzo.pvalues["consistent"] > stud.pvalues["consistent"]


def test_stepm_studentizzato_trova_il_modello_buono():
    from motore.core.verifiche import stepm_studentizzato
    bench, buono, rumoroso = _perdite_sintetiche()
    assert stepm_studentizzato(bench, np.column_stack([buono, rumoroso]), size=0.05, reps=2000, seed=7) == [0]
