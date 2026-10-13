"""Controllo con ingressi casuali: stessa gestione del trade, stessa direzione, stessi filtri orari, ma il momento
d'ingresso è estratto a caso (eventualmente solo nelle candele che rispettano le stesse condizioni di regime degli OB).
Serve a capire quanto del risultato viene dal segnale dell'OB e quanto dal mercato (l'oro 2022-2026 sale molto).
"""
from __future__ import annotations

import numpy as np

from .motore import Serie
from .simulatore import C_DIR, simula


def simula_casuale(S: Serie, ind, cfg: np.ndarray, n_segnali: int, n_prove: int = 200, regime: bool = True,
                   seed: int = 11, xflag: np.ndarray | None = None) -> list[np.ndarray]:
    """n_prove simulazioni con n_segnali croci casuali. Ogni croce ha un suo "OB" fittizio (top = bottom = low/high
    della candela) così la regola "un trade per OB" non blocca nulla. regime=True: solo candele con trend del
    Supertrend a favore da almeno 20 candele e prezzo dal lato giusto della EMA del TF superiore (fattori b e c)."""
    n = len(ind.c)
    rng = np.random.default_rng(seed)
    dirf = int(cfg[C_DIR])
    dirs = [1, -1] if dirf == 0 else [dirf]
    if xflag is None:
        xflag = S.venerdi
    cand = {}
    for d in dirs:
        ok = np.ones(n, bool)
        ok[:200] = False
        ok[-2:] = False
        if regime:
            hema = ind.hema
            lato = (ind.c > hema) if d == 1 else (ind.c < hema)
            ok &= (ind.trend == d) & (ind.age >= 20) & np.nan_to_num(lato, nan=False).astype(bool)
        cand[d] = np.where(ok)[0]
    ob_conf = np.arange(n, dtype=np.int64); ob_piv = np.arange(n, dtype=np.int64)   # pivot = candela del segnale
    out = []
    for _ in range(n_prove):
        act_id = np.full(n, -1, np.int64); act_dir = np.zeros(n, np.int64)
        sig_l = np.zeros(n, np.bool_); sig_s = np.zeros(n, np.bool_)
        for d in dirs:
            k = n_segnali if len(dirs) == 1 else n_segnali // 2
            if len(cand[d]) == 0:
                continue
            idx = rng.choice(cand[d], size=min(k, len(cand[d])), replace=False)
            act_id[idx] = idx; act_dir[idx] = d
            if d == 1:
                sig_l[idx] = True
            else:
                sig_s[idx] = True
        lv = np.where(act_dir == -1, ind.h, ind.l).astype(np.float64)        # "OB" fittizio piatto sulla candela
        T = simula(ind.o, ind.h, ind.l, ind.c, S.spr, ind.atr, ind.trend, ind.tstop, ind.swlo, ind.swhi,
                   S.ora, S.wday, xflag, np.full(n, 3, np.int64),
                   act_id, act_dir, lv, lv, sig_l, sig_s, ob_conf, ob_piv, lv, lv, cfg)
        out.append(T)
    return out
