"""Famiglia di CONTROLLO: ingressi casuali (aggiunta trad, 08/10/2026).

Non e' un'ipotesi: nessuna informazione di mercato entra nella decisione d'ingresso ne' nella direzione.
Serve a collaudare la pipeline su DATI REALI (loader, costi, giornate, simulatore prop, contatore) senza aprire il
fuori campione di nessuna famiglia vera: su questa famiglia la pipeline non deve promuovere niente, se non per caso
(5% sull'insieme dei candidati, per la correzione di Bonferroni). Il cancello (`lab/gate.py`) la riconosce da
`controllo = True` e non chiede ne' contatore ne' pre-registrazione.

Le forme di stop, target e durata sono le stesse delle strategie della famiglia mean_reversion (ATR 14, 1,5-2,5 ATR,
target in R, time stop), cosi' il controllo ha la stessa geometria dei test veri. Il seme e' nella griglia: varianti
con semi diversi sono campioni indipendenti dello stesso nulla. La sequenza casuale dipende solo dal seme e dalla
posizione della barra, quindi i segnali fino alla barra t non cambiano se si taglia il futuro (test anti look-ahead).
"""
from __future__ import annotations

import numpy as np

from .base import Strategy, register
from ..backtest import Signals
from .. import indicators as ind


@register
class IngressoCasuale(Strategy):
    name = "ingresso_casuale"
    family = "controllo_casuale"
    controllo = True
    description = ("CONTROLLO: entra in barre scelte a caso con direzione a caso. SL = m*ATR, TP = r*SL, "
                   "time stop. Nessun vantaggio possibile se non la deriva del prezzo, che a direzione casuale si annulla.")
    grid = {"atr_sl": [1.5, 2.5], "tp_r": [1.0, 2.0, 3.0], "freq": [0.01, 0.03], "seed": [1, 2, 3]}

    def signals(self, df, atr_sl, tp_r, freq, seed):
        n = len(df)
        rng = np.random.default_rng(seed)
        # una coppia (ingresso, lato) per barra, estratta in ordine di barra: la barra t usa le estrazioni 2t e 2t+1,
        # quindi il prefisso e' identico per qualunque lunghezza dei dati (due estrazioni separate non lo sarebbero)
        u, lato = rng.random((n, 2)).T
        e = np.zeros(n, int)
        on = u < freq
        e[on & (lato < 0.5)] = 1
        e[on & (lato >= 0.5)] = -1
        a = ind.atr(df, 14).to_numpy()
        return Signals(entry=e, sl_dist=atr_sl * a, tp_r=float(tp_r), max_bars=48)
