"""Modello dati e funzioni di scoring per lo Stock Selector V6.0.

Le soglie e i pesi replicano fedelmente la logica del notebook originale
`algoritmo selezione azioni.ipynb`. Tutti i parametri arrivano dal `config.yaml`
caricato da `strategy.py` — qui dentro non c'è nessun valore hardcodato.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Tipi pubblici
# ---------------------------------------------------------------------------


class MacroScenario(str, Enum):
    """Scenario macro derivato da tassi + trend liquidità."""

    DEFENSIVE = "DEFENSIVE (Stock A)"
    AGGRESSIVE = "AGGRESSIVE (Stock D)"
    QUALITY = "NEUTRAL/QUALITY (Stock B/C)"


class RRGStatus(str, Enum):
    """Quadrante RRG (Relative Rotation Graph) del titolo vs benchmark."""

    LEADING = "LEADING"
    WEAKENING = "WEAKENING"
    LAGGING = "LAGGING"
    IMPROVING = "IMPROVING"
    NA = "N/A"


class StockPick(BaseModel):
    """Riga risultato per un singolo ticker analizzato."""

    ticker: str
    sector: str = "N/A"
    target_match: str = "NO"
    score: float = Field(ge=0, le=6)
    rrg: RRGStatus = RRGStatus.NA
    price: Optional[float] = None
    pe: Optional[float] = None
    de_ratio: Optional[float] = None
    ebitda_margin: Optional[float] = None
    profit_margin: Optional[float] = None
    roe: Optional[float] = None
    beta: Optional[float] = None
    note: str = ""


class SelectionResult(BaseModel):
    """Output strutturato di una selezione completa."""

    scenario: MacroScenario
    benchmark: str
    risk_free_rate: float
    is_liquidity_increasing: bool
    generated_at: datetime
    top_picks: list[StockPick]
    full_analysis: list[StockPick]
    excel_top_picks_path: Optional[str] = None
    excel_full_analysis_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Logica di scenario
# ---------------------------------------------------------------------------


def derive_scenario(
    risk_free_rate: float,
    is_liquidity_increasing: bool,
    high_rate_threshold: float,
) -> MacroScenario:
    """Determina lo scenario macro dai due input chiave.

    Replica esattamente il blocco `--- 3. LOGICA MACRO ---` del notebook V6.0.
    """
    high_rates = risk_free_rate > high_rate_threshold

    if not high_rates and is_liquidity_increasing:
        return MacroScenario.AGGRESSIVE
    if high_rates and not is_liquidity_increasing:
        return MacroScenario.DEFENSIVE
    return MacroScenario.QUALITY


def check_scenario_match(
    de: Optional[float],
    beta: Optional[float],
    roe: Optional[float],
    scenario: MacroScenario,
    filters: dict[str, Any],
) -> str:
    """Restituisce la stringa "SI (...)" / "NO" come nel notebook."""
    if scenario == MacroScenario.DEFENSIVE:
        f = filters["defensive"]
        if de is not None and de < f["de_max"]:
            if beta is not None and beta < f["beta_max"]:
                return "SI (Difensivo)"
        return "NO"

    if scenario == MacroScenario.AGGRESSIVE:
        f = filters["aggressive"]
        if beta is not None and beta > f["beta_min"]:
            return "SI (Aggressivo)"
        return "NO"

    # Quality
    f = filters["quality"]
    if roe is not None and roe > f["roe_min"]:
        if de is not None and de < f["de_max"]:
            return "SI (Quality)"
    return "NO"


# ---------------------------------------------------------------------------
# Scoring fondamentale
# ---------------------------------------------------------------------------


def compute_fundamental_score(
    de: Optional[float],
    pe: Optional[float],
    eps: Optional[float],
    ebitda_margin: Optional[float],
    profit_margin: Optional[float],
    roe: Optional[float],
    risk_free_decimal: float,
    scoring_cfg: dict[str, Any],
) -> tuple[float, str]:
    """Calcola lo score 0-6 e una nota testuale.

    Replica il blocco di calcolo punteggio del notebook V6.0. La nota viene
    appesa come nel notebook (es. "Debito Alto; ").
    """
    score: float = 0
    note: str = ""

    de_cfg = scoring_cfg["debt_to_equity"]
    if de is not None and de < de_cfg["full_point_below"]:
        score += 1
    elif de is not None and de <= de_cfg["half_point_below"]:
        score += 0.5
    else:
        # Sia D/E None sia D/E alto → annotiamo come nel notebook originale.
        note += "Debito Alto; "

    if pe is not None and pe > 0:
        score += 1

    if eps is not None and eps > 0:
        score += 1

    mol_cfg = scoring_cfg["ebitda_margin"]
    if ebitda_margin is not None and ebitda_margin > mol_cfg["full_point_above"]:
        score += 1
    elif ebitda_margin is not None and ebitda_margin > mol_cfg["half_point_above"]:
        score += 0.5

    if profit_margin is not None and profit_margin > scoring_cfg["profit_margin_above"]:
        score += 1

    if roe is not None and roe > risk_free_decimal:
        score += 1

    return score, note


# ---------------------------------------------------------------------------
# RRG
# ---------------------------------------------------------------------------


def compute_rrg_status(
    stock_close: pd.Series,
    bench_close: pd.Series,
    rrg_cfg: dict[str, Any],
) -> RRGStatus:
    """Quadrante RRG del titolo rispetto al benchmark.

    Logica identica a `get_rrg_status` del notebook: RS normalizzato su finestra
    mobile, momentum come differenza shiftata, soglia 100 sui due assi.
    """
    min_bars = rrg_cfg["min_history_bars"]
    if len(stock_close) < min_bars or len(bench_close) < min_bars:
        return RRGStatus.NA

    rs = stock_close / bench_close
    window = rrg_cfg["rs_window"]
    rs_ratio = 100 + ((rs - rs.rolling(window=window).mean()) / rs.std()) * 10
    rs_momentum = 100 + (rs_ratio - rs_ratio.shift(rrg_cfg["momentum_lookback"]))

    curr_r = rs_ratio.iloc[-1]
    curr_m = rs_momentum.iloc[-1]

    if pd.isna(curr_r) or pd.isna(curr_m):
        return RRGStatus.NA

    if curr_r > 100 and curr_m > 100:
        return RRGStatus.LEADING
    if curr_r > 100 and curr_m < 100:
        return RRGStatus.WEAKENING
    if curr_r < 100 and curr_m < 100:
        return RRGStatus.LAGGING
    return RRGStatus.IMPROVING


# ---------------------------------------------------------------------------
# Helper: yfinance.info → valori numerici sicuri
# ---------------------------------------------------------------------------


def normalize_debt_to_equity(de_raw: Optional[float]) -> Optional[float]:
    """yfinance a volte restituisce D/E in percentuale (>10): lo riporta a frazione."""
    if de_raw is None:
        return None
    if de_raw > 10:
        return de_raw / 100
    return de_raw
