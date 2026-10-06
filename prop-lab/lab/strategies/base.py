"""Interfaccia comune delle strategie.

Ogni strategia di una famiglia è una sottoclasse di Strategy con:
  name        identificativo unico (snake_case)
  family      nome della famiglia (es. "mean_reversion")
  description regola in linguaggio naturale + fonte/ispirazione
  grid        dict {parametro: [valori ordinati]}  -> testati TUTTI (si registra ogni tentativo)
  signals(df, **params) -> Signals

REGOLE (le controlla l'agente quant-reviewer):
  - usare solo dati fino alla barra i (rolling/shift, mai shift(-1) / centered)
  - lo stop deve essere SEMPRE definito (sl_dist > 0): serve per esprimere tutto in R
  - il target va fissato al momento del segnale (tp_level/tp_r) o tramite exit_long/exit_short
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..backtest import Signals

REGISTRY: dict[str, dict[str, type]] = {}


def register(cls):
    REGISTRY.setdefault(cls.family, {})[cls.name] = cls
    return cls


class Strategy:
    name: str = "base"
    family: str = "base"
    description: str = ""
    grid: dict = {}

    def signals(self, df: pd.DataFrame, **p) -> Signals:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def arr(x) -> np.ndarray:
        return np.asarray(x, dtype=float)


def get_family(family: str) -> dict[str, type]:
    from . import load_all  # noqa: F401  (import side effect: registra le famiglie)
    load_all()
    if family not in REGISTRY:
        raise KeyError(f"Famiglia '{family}' non trovata. Disponibili: {list(REGISTRY)}")
    return REGISTRY[family]
