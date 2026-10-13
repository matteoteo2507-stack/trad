"""Collante tra dati, indicatore e simulatore: calendario in ora italiana, uscite forzate, tabelle dei trade."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import dati
from .indicatore import Indicatore, ParInd
from .simulatore import COLONNE, ESITI, simula


class Serie:
    """Barre di un timeframe con il calendario in ora italiana (ora server - 1 h, come da specifica)."""

    def __init__(self, tf: str, df: pd.DataFrame | None = None):
        self.tf = tf
        self.df = df if df is not None else dati.carica(tf)
        it = dati.ora_italiana(self.df.index)
        self.t = self.df.index.values
        self.ora = (it.hour + it.minute / 60.0).values.astype(np.float64)
        self.wday = it.weekday.values.astype(np.int64)
        self.spr = self.df["spread"].values.astype(np.float64)
        # venerdì sera: l'uscita è decisa alla chiusura della candela segnata ed eseguita all'open della successiva.
        # Segnate: le candele di venerdì aperte dalle 21:00 italiane in poi, e la penultima candela prima della pausa
        # del fine settimana (serve per H4/D1: così l'uscita avviene all'open dell'ultima candela della settimana)
        ultima = np.r_[np.diff(self.t) > np.timedelta64(36, "h"), False]
        penultima = np.r_[ultima[1:], False]
        self.venerdi = ((self.wday == 4) & (self.ora >= 21.0)) | penultima
        self._xs: dict = {}

    def fine_sessione(self, h0: float, h1: float) -> np.ndarray:
        """True sull'ultima candela dentro la sessione [h0, h1) (e il venerdì sera): l'uscita avviene all'open
        della candela successiva, cioè la prima fuori sessione."""
        k = (h0, h1)
        if k not in self._xs:
            ins = (self.ora >= h0) & (self.ora < h1)
            if h0 <= 0 and h1 >= 24:
                x = self.venerdi.copy()
            else:
                x = (ins & ~np.r_[ins[1:], False]) | self.venerdi
            self._xs[k] = x
        return self._xs[k]

    def split(self, frazione_is: float = 0.65) -> np.datetime64:
        """Inizio dell'OOS: il primo 65% delle candele è in-sample."""
        return self.t[int(len(self.t) * frazione_is)]


def esegui(S: Serie, ind: Indicatore, cfg: np.ndarray, xflag: np.ndarray | None = None,
           filtro: np.ndarray | None = None) -> np.ndarray:
    ob = ind.ob
    if xflag is None:
        xflag = S.venerdi
    return simula(ind.o, ind.h, ind.l, ind.c, S.spr, ind.atr, ind.trend, ind.tstop, ind.swlo, ind.swhi,
                  S.ora, S.wday, xflag, np.full(len(ind.c), 3, np.int64) if filtro is None else filtro.astype(np.int64),
                  ind.act_id, ind.act_dir, ind.act_top, ind.act_bot, ind.sig_l, ind.sig_s,
                  ob["conf"].values, ob["pivot"].values, ob["top"].values, ob["bottom"].values, cfg)


def tabella(S: Serie, T: np.ndarray) -> pd.DataFrame:
    """Trade leggibili: orari, prezzi, R, esito."""
    df = pd.DataFrame(T, columns=COLONNE)
    for k in ("i_in", "i_out", "dir", "esito", "ob", "n_parz", "i_rf"):
        df[k] = df[k].astype(int)
    df.insert(0, "t_in", S.df.index[df["i_in"].values])
    df.insert(1, "t_out", S.df.index[df["i_out"].values])
    df["esito"] = [ESITI[x] for x in df["esito"].values]
    df["candele"] = df["i_out"] - df["i_in"]
    return df


__all__ = ["Serie", "Indicatore", "ParInd", "esegui", "tabella"]
