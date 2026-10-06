"""Doppio binario della gestione del rischio: libreria dichiarata, overlay, i tre casi del 06/10."""
import numpy as np
import pytest

from core import prop_sim, sizing


def _iid(n, e, rng):
    return np.where(rng.random(n) < (1 + e) / 2, 1.0, -1.0)


def _regimi(n, pg, pb, stay, rng):
    s, out = 0, []
    for _ in range(n):
        if rng.random() > stay:
            s = 1 - s
        out.append(1.0 if rng.random() < (pg if s == 0 else pb) else -1.0)
    return np.array(out)


def _alternati(n, e, rho, rng):
    out, p = [1.0], (1 + e) / 2
    for _ in range(n - 1):
        q = p - rho if out[-1] > 0 else p + rho
        out.append(1.0 if rng.random() < q else -1.0)
    return np.array(out)


def test_libreria_dichiarata_non_cambia_di_nascosto():
    assert set(sizing.LIBRERIA) == {"O1_cuscinetto", "O2_guardia_giornaliera", "O3_serie_perdite",
                                    "O4_avvicinamento_target"}
    assert sizing.LIBRERIA["O1_cuscinetto"]["modifiers"] == [{"type": "dd_linear", "min_mult": 0.25}]
    assert sizing.LIBRERIA["O2_guardia_giornaliera"]["modifiers"] == [
        {"type": "daily_guard", "stop_at": 0.5, "max_trades": 3}, {"type": "floor_cap", "frac": 0.9}]
    assert sizing.LIBRERIA["O3_serie_perdite"]["modifiers"] == [
        {"type": "loss_streak", "after": 2, "factor": 0.5, "min_mult": 0.25}]
    assert sizing.LIBRERIA["O4_avvicinamento_target"]["modifiers"] == [
        {"type": "target_coast", "near": 0.8, "mult": 0.5}]
    assert sizing.LIBRERIA["O2_guardia_giornaliera"]["obiettivi"] == ("prop",)


def test_un_overlay_fuori_libreria_e_un_tentativo():
    with pytest.raises(KeyError):
        sizing.confronta_overlay(np.ones(10), overlay=("anti_martingala",))
    with pytest.raises(ValueError):
        sizing.confronta_overlay(np.ones(10), overlay=("O2_guardia_giornaliera",))   # solo prop


def test_moltiplicatori_serie_e_cuscinetto():
    m = sizing.moltiplicatori([-1, -1, -1, 1, -1], "O3_serie_perdite")
    assert list(m) == [1.0, 1.0, 0.5, 0.25, 1.0]
    m = sizing.moltiplicatori([-1.0] * 5 + [0.0], "O1_cuscinetto", limite_r=10)
    # dopo 1R di DD la size e' 0,9, ma ogni perdita e' grande quanto la size del suo trade
    assert m[0] == 1.0 and abs(m[1] - 0.9) < 1e-12 and m[-1] < m[1]
    assert list(sizing.moltiplicatori([1, -1], "1R")) == [1.0, 1.0]


def test_ponte_unico_verso_prop_lab():
    import lab.prop
    import lab.risk
    assert prop_sim.evaluate is lab.prop.evaluate and prop_sim.zero_edge is lab.prop.zero_edge
    assert prop_sim.RiskModel is lab.risk.RiskModel


def test_esiti_indipendenti_falsi_allarmi_al_tasso_nominale():
    """Con esiti indipendenti la lettura AGGIUNGE/TOGLIE deve scattare solo per caso, al tasso 1 - conf.
    Un singolo seme non prova niente (il 10% delle volte esce fuori banda): si misura il tasso."""
    fuori = {"O1_cuscinetto": 0, "O3_serie_perdite": 0}
    for s in range(30):
        r = _iid(300, 0.10, np.random.default_rng(500 + s))
        t = sizing.confronta_overlay(r, n_perm=60, seed=s)[0].set_index("binario")
        for k in fuori:
            fuori[k] += t.loc[k, "lettura"] != "nessun valore di dipendenza"
    assert all(v <= 6 for v in fuori.values()), fuori      # atteso ~1,5 su 30; 6 ha probabilita' < 0,5%


def test_regimi_il_cuscinetto_aggiunge():
    r = _regimi(2000, 0.65, 0.45, 0.97, np.random.default_rng(1))
    tab, _ = sizing.confronta_overlay(r, n_perm=200, seed=3)
    riga = tab.set_index("binario").loc["O1_cuscinetto"]
    assert riga["lettura"].startswith("AGGIUNGE") and riga["valore_dipendenza"] > 0.02


def test_esiti_alternati_la_serie_toglie():
    r = _alternati(2000, 0.10, 0.10, np.random.default_rng(1))
    tab, runs = sizing.confronta_overlay(r, n_perm=200, seed=3)
    assert tab.set_index("binario").loc["O3_serie_perdite", "lettura"] == "TOGLIE per dipendenza"
    assert runs["z"] > 2


def test_confronta_overlay_prop_riporta_il_benchmark_zero():
    rng = np.random.default_rng(4)
    days = [[(1.0, 0.0)] if rng.random() < 0.6 else [(-1.0, 1.0)] for _ in range(250)]
    rules = {"account": 100000, "fee": 500, "daily_loss_pct": 5, "max_loss_pct": 10, "max_loss_type": "static",
             "phases": [{"target_pct": 8, "min_days": 0}], "max_days_default": 120}
    tab = sizing.confronta_overlay_prop(days, rules, 1.0, overlay=("O1_cuscinetto",), n_paths=60, n_outer=8)
    assert list(tab["binario"]) == ["1R", "O1_cuscinetto"]
    assert (tab["pass_rate"] >= tab["pass_zero"]).all()
    assert {"ev_vs_zero", "ev_vs_zero_lo", "ev_vs_zero_hi", "p_ev_vs_zero_pos"} <= set(tab.columns)
