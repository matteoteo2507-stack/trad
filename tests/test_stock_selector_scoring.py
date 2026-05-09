"""Test sintetici per le funzioni pure dello Stock Selector.

Coprono il criterio di Stage 1: una società con D/E=0.3 e ROE=0.20 deve avere
score >= 4 nello scenario corrente.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from strategies.stock_selector.scoring import (
    MacroScenario,
    RRGStatus,
    check_scenario_match,
    compute_fundamental_score,
    compute_rrg_status,
    derive_scenario,
    normalize_debt_to_equity,
)


CONFIG_PATH = Path(__file__).parent.parent / "strategies" / "stock_selector" / "config.yaml"


@pytest.fixture(scope="module")
def cfg() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Scenario macro
# ---------------------------------------------------------------------------


def test_scenario_defensive_quando_tassi_alti_e_liquidita_in_calo(cfg):
    s = derive_scenario(4.5, False, cfg["high_rate_threshold"])
    assert s == MacroScenario.DEFENSIVE


def test_scenario_aggressive_quando_tassi_bassi_e_liquidita_in_aumento(cfg):
    s = derive_scenario(2.0, True, cfg["high_rate_threshold"])
    assert s == MacroScenario.AGGRESSIVE


def test_scenario_quality_negli_altri_casi(cfg):
    assert derive_scenario(4.5, True, cfg["high_rate_threshold"]) == MacroScenario.QUALITY
    assert derive_scenario(2.0, False, cfg["high_rate_threshold"]) == MacroScenario.QUALITY


# ---------------------------------------------------------------------------
# Scoring fondamentale — criterio di Stage 1
# ---------------------------------------------------------------------------


def test_score_minimo_4_per_societa_solida(cfg):
    """Criterio di completamento Stage 1 (skill stock-selector):
    società con D/E=0.3 e ROE=0.20 → score >= 4.
    """
    score, _ = compute_fundamental_score(
        de=0.3,
        pe=18.0,
        eps=5.0,
        ebitda_margin=0.25,
        profit_margin=0.12,
        roe=0.20,
        risk_free_decimal=0.042,  # 4.2%
        scoring_cfg=cfg["scoring"],
    )
    assert score >= 4


def test_score_max_6_per_societa_eccellente(cfg):
    score, note = compute_fundamental_score(
        de=0.2,
        pe=15.0,
        eps=8.0,
        ebitda_margin=0.30,
        profit_margin=0.20,
        roe=0.25,
        risk_free_decimal=0.042,
        scoring_cfg=cfg["scoring"],
    )
    assert score == 6
    assert "Debito Alto" not in note


def test_nota_debito_alto_se_de_oltre_soglia(cfg):
    _, note = compute_fundamental_score(
        de=2.5,
        pe=20.0,
        eps=3.0,
        ebitda_margin=0.15,
        profit_margin=0.05,
        roe=0.10,
        risk_free_decimal=0.042,
        scoring_cfg=cfg["scoring"],
    )
    assert "Debito Alto" in note


def test_score_zero_se_dati_tutti_negativi_o_mancanti(cfg):
    score, _ = compute_fundamental_score(
        de=None,
        pe=None,
        eps=-1.0,
        ebitda_margin=0.0,
        profit_margin=0.0,
        roe=0.0,
        risk_free_decimal=0.042,
        scoring_cfg=cfg["scoring"],
    )
    assert score == 0


# ---------------------------------------------------------------------------
# Match scenario
# ---------------------------------------------------------------------------


def test_match_defensive_richiede_de_basso_e_beta_basso(cfg):
    f = cfg["scenario_filters"]
    assert check_scenario_match(0.3, 0.8, 0.18, MacroScenario.DEFENSIVE, f).startswith("SI")
    assert check_scenario_match(0.3, 1.5, 0.18, MacroScenario.DEFENSIVE, f) == "NO"
    assert check_scenario_match(1.5, 0.5, 0.18, MacroScenario.DEFENSIVE, f) == "NO"


def test_match_aggressive_richiede_beta_alto(cfg):
    f = cfg["scenario_filters"]
    assert check_scenario_match(2.0, 1.5, 0.05, MacroScenario.AGGRESSIVE, f).startswith("SI")
    assert check_scenario_match(0.3, 0.9, 0.20, MacroScenario.AGGRESSIVE, f) == "NO"


def test_match_quality_richiede_roe_alto_e_de_contenuto(cfg):
    f = cfg["scenario_filters"]
    assert check_scenario_match(0.5, 1.0, 0.20, MacroScenario.QUALITY, f).startswith("SI")
    assert check_scenario_match(0.5, 1.0, 0.10, MacroScenario.QUALITY, f) == "NO"
    assert check_scenario_match(1.5, 1.0, 0.20, MacroScenario.QUALITY, f) == "NO"


# ---------------------------------------------------------------------------
# Normalizzazione D/E
# ---------------------------------------------------------------------------


def test_normalize_de_riconverte_percentuale_in_frazione():
    assert normalize_debt_to_equity(80.0) == 0.8
    assert normalize_debt_to_equity(0.5) == 0.5
    assert normalize_debt_to_equity(None) is None


# ---------------------------------------------------------------------------
# RRG su serie sintetiche
# ---------------------------------------------------------------------------


def test_rrg_na_se_storico_troppo_corto(cfg):
    short = pd.Series([1.0, 2.0, 3.0])
    assert compute_rrg_status(short, short, cfg["rrg"]) == RRGStatus.NA


def test_rrg_classifica_uno_dei_quattro_quadranti_su_serie_realistica(cfg):
    """Il quadrante deve essere uno dei 4 enum (non N/A) se lo storico è sufficiente."""
    n = 200
    # Serie con accelerazione recente per uscire dalla zona neutra dell'RS.
    bench = pd.Series([100 + i * 0.1 for i in range(n)])
    stock = pd.Series([100 + i * 0.1 + (i ** 1.5) * 0.01 for i in range(n)])
    status = compute_rrg_status(stock, bench, cfg["rrg"])
    assert status in {
        RRGStatus.LEADING,
        RRGStatus.WEAKENING,
        RRGStatus.LAGGING,
        RRGStatus.IMPROVING,
    }
