"""Replica candela per candela di VTOB_Indicator_Pro.pine (BigBeluga mod), SENZA lookahead.

Tutto è calcolato alla CHIUSURA della candela i con dati fino a i:
- custom_atr = SMA(high-low, st_len); Supertrend ricorsivo come nel Pine (nz(band[1]), prevSuperTrend == prevUpperBand);
- pivot ta.pivotlow/pivothigh(left, right): il pivot è la candela i-right ed è noto solo alla candela i (conferma);
  regola sui pari: stretto a sinistra, non stretto a destra (come il motore di riferimento: vince il primo di due minimi uguali);
- OB long (trend 1 + pivot low): top = min(open, close) della candela pivot, bottom = top - zona_h*atr(i); short speculare;
  ignorato se si sovrappone all'OB attivo; un solo OB attivo; punteggio alla candela di conferma;
- invalidazione: long se high < bottom, short se low > top (dopo la rottura niente segnali);
- croce di retest long: crossover(low, active_top) con OB long attivo, nessun pivot low sulla candela, nessun cambio di trend.

Uscita: Struttura con array per candela (stato DOPO la chiusura della candela) e tabella degli OB.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from numba import njit

from . import dati


@dataclass(frozen=True)
class ParInd:
    st_len: int = 50
    st_mult: float = 3.5
    pivot_left: int = 7
    pivot_right: int = 3
    zona_h: float = 1.0
    use_imp: bool = False
    imp_mult: float = 1.0
    use_age: bool = True
    min_age: int = 20
    use_htf: bool = True
    htf: str = "H1"
    htf_len: int = 200
    use_dist: bool = True
    dist_mult: float = 0.0
    use_vol: bool = False
    vol_mult: float = 1.2
    min_score: int = 3
    htf_fonte: str = "file"     # "file" = barre MT5 del TF superiore (storia completa, come TradingView)
                                # "resample" = ricostruite dalle barre del grafico (come il motore di riferimento)


# ---------------------------------------------------------------- Supertrend custom e pivot
@njit(cache=True)
def _supertrend(h, l, c, atr, mult):
    n = len(c)
    lb = np.full(n, np.nan); ub = np.full(n, np.nan)
    trend = np.zeros(n, np.int64); tstop = np.full(n, np.nan)
    for i in range(n):
        src = (h[i] + l[i]) / 2.0
        lb0 = src - mult * atr[i]; ub0 = src + mult * atr[i]
        plb = 0.0 if (i == 0 or np.isnan(lb[i - 1])) else lb[i - 1]      # nz(lower_band[1])
        pub = 0.0 if (i == 0 or np.isnan(ub[i - 1])) else ub[i - 1]
        pc = c[i - 1] if i > 0 else np.nan
        # lower_band := lower_band > prevLowerBand or close[1] < prevLowerBand ? lower_band : prevLowerBand
        lb[i] = lb0 if (lb0 > plb or (i > 0 and pc < plb)) else plb
        ub[i] = ub0 if (ub0 < pub or (i > 0 and pc > pub)) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            trend[i] = 1
        elif tstop[i - 1] == pub:                                         # prevSuperTrend == prevUpperBand
            trend[i] = 1 if c[i] > ub[i] else -1
        else:
            trend[i] = -1 if c[i] < lb[i] else 1
        tstop[i] = lb[i] if trend[i] == 1 else ub[i]
    return trend, tstop


@njit(cache=True)
def _pivot(h, l, left, right):
    """pl[i]/ph[i] = True se la candela i-right è un pivot confermato alla candela i."""
    n = len(h)
    pl = np.zeros(n, np.bool_); ph = np.zeros(n, np.bool_)
    for i in range(left + right, n):
        p = i - right
        okl = True; okh = True
        for k in range(p - left, p):          # sinistra: stretto
            if l[k] <= l[p]:
                okl = False
            if h[k] >= h[p]:
                okh = False
        for k in range(p + 1, i + 1):         # destra: non stretto
            if l[k] < l[p]:
                okl = False
            if h[k] > h[p]:
                okh = False
        pl[i] = okl; ph[i] = okh
    return pl, ph


# ---------------------------------------------------------------- order block, punteggio, invalidazione, croci
@njit(cache=True)
def _order_block(o, h, l, c, v, atr, trend, tstop, pl, ph, chg, age, hh, ll, vavg, hema, R, zona_h,
                 use_imp, imp_mult, use_age, min_age, use_htf, use_dist, dist_mult, use_vol, vol_mult, need):
    n = len(c)
    act_id = np.full(n, -1, np.int64); act_dir = np.zeros(n, np.int64)
    act_top = np.full(n, np.nan); act_bot = np.full(n, np.nan)
    sig_l = np.zeros(n, np.bool_); sig_s = np.zeros(n, np.bool_)
    cap = n // 2 + 10
    ob_conf = np.zeros(cap, np.int64); ob_piv = np.zeros(cap, np.int64); ob_dir = np.zeros(cap, np.int64)
    ob_top = np.zeros(cap); ob_bot = np.zeros(cap); ob_score = np.zeros(cap, np.int64)
    ob_end = np.full(cap, n, np.int64); ob_rotto = np.zeros(cap, np.bool_)
    ob_f = np.full((cap, 5), np.nan)       # fattori: impulso/atr, età, htf ok, distanza/atr, volume/media
    nob = 0; nrej = 0
    a_id = -1; a_dir = 0; a_top = np.nan; a_bot = np.nan
    prev_top = np.nan; prev_bot = np.nan
    for i in range(n):
        if not np.isnan(atr[i]):
            for d in (1, -1):
                if trend[i] != d:
                    continue
                if d == 1 and not pl[i]:
                    continue
                if d == -1 and not ph[i]:
                    continue
                p = i - R
                if d == 1:
                    top = min(o[p], c[p]); bot = top - zona_h * atr[i]
                else:
                    bot = max(o[p], c[p]); top = bot + zona_h * atr[i]
                if not (np.isnan(a_top) or np.isnan(a_bot)):
                    if not (bot > a_top or top < a_bot):
                        continue                                      # si sovrappone all'OB attivo
                f_imp = ((hh[i] - top) if d == 1 else (bot - ll[i])) / atr[i]
                f_age = age[i]
                he = hema[i]
                f_htf = np.nan if np.isnan(he) else (1.0 if ((c[i] > he) if d == 1 else (c[i] < he)) else 0.0)
                f_dist = ((bot - tstop[i]) if d == 1 else (tstop[i] - top)) / atr[i]
                va = vavg[i - R - 1] if i - R - 1 >= 0 else np.nan
                f_vol = np.nan if (np.isnan(va) or va <= 0) else v[p] / va
                s = 0
                if use_imp and (((hh[i] - top) if d == 1 else (bot - ll[i])) >= imp_mult * atr[i]):
                    s += 1
                if use_age and f_age >= min_age:
                    s += 1
                if use_htf and f_htf == 1.0:
                    s += 1
                if use_dist and (((bot - tstop[i]) if d == 1 else (tstop[i] - top)) >= dist_mult * atr[i]):
                    s += 1
                if use_vol and (not np.isnan(va)) and v[p] >= vol_mult * va:
                    s += 1
                if s < need:
                    nrej += 1
                    continue
                if a_id >= 0:
                    ob_end[a_id] = i                                   # sostituito dal nuovo OB
                a_id = nob; a_dir = d; a_top = top; a_bot = bot
                ob_conf[nob] = i; ob_piv[nob] = p; ob_dir[nob] = d; ob_top[nob] = top; ob_bot[nob] = bot
                ob_score[nob] = s
                ob_f[nob, 0] = f_imp; ob_f[nob, 1] = f_age; ob_f[nob, 2] = f_htf; ob_f[nob, 3] = f_dist; ob_f[nob, 4] = f_vol
                nob += 1
        # invalidazione (dopo la rottura niente più segnali)
        if a_id >= 0:
            if (a_dir == 1 and h[i] < a_bot) or (a_dir == -1 and l[i] > a_top):
                ob_end[a_id] = i; ob_rotto[a_id] = True
                a_id = -1; a_dir = 0; a_top = np.nan; a_bot = np.nan
        act_id[i] = a_id; act_dir[i] = a_dir; act_top[i] = a_top; act_bot[i] = a_bot
        # croci di retest (ta.crossover(low, active_top): low > top and low[1] <= top[1])
        if i > 0 and a_dir == 1 and not pl[i] and not chg[i]:
            if l[i] > a_top and (not np.isnan(prev_top)) and l[i - 1] <= prev_top:
                sig_l[i] = True
        if i > 0 and a_dir == -1 and not ph[i] and not chg[i]:
            if h[i] < a_bot and (not np.isnan(prev_bot)) and h[i - 1] >= prev_bot:
                sig_s[i] = True
        prev_top = a_top; prev_bot = a_bot
    return (act_id, act_dir, act_top, act_bot, sig_l, sig_s, nob, nrej,
            ob_conf[:nob], ob_piv[:nob], ob_dir[:nob], ob_top[:nob], ob_bot[:nob], ob_score[:nob], ob_end[:nob],
            ob_rotto[:nob], ob_f[:nob])


# ---------------------------------------------------------------- EMA del TF superiore (candela HTF già chiusa)
_HTF: dict = {}


def _htf_cache(tf: str) -> pd.DataFrame:
    if tf not in _HTF:
        _HTF[tf] = dati.carica(tf)
    return _HTF[tf]


def pine_ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan); a = 2.0 / (n + 1)
    if len(x) >= n:
        out[n - 1] = x[:n].mean()
        for i in range(n, len(x)):
            out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def ema_htf(df: pd.DataFrame, htf: str, n: int, fonte: str = "file") -> np.ndarray:
    """request.security(htf, ta.ema(close, n)[1], lookahead_on): alla candela t vale la EMA della candela HTF precedente
    a quella che contiene t (quindi già chiusa)."""
    mins = dati.TF_MINUTI[htf]
    if fonte == "resample":                    # come il motore di riferimento (ewm pandas, solo dati del grafico)
        hc = df["close"].resample(f"{mins}min", label="left", closed="left").last().dropna()
        hema = hc.ewm(span=n, adjust=False).mean().shift(1)
        return hema.reindex(df.index.floor(f"{mins}min")).values
    h = _htf_cache(htf)
    e = pd.Series(pine_ema(h["close"].values, n), index=h.index).shift(1)
    pos = np.searchsorted(h.index.values, df.index.values, side="right") - 1     # candela HTF che contiene t
    out = np.full(len(df), np.nan)
    ok = pos >= 0
    out[ok] = e.values[pos[ok]]
    return out


# ---------------------------------------------------------------- interfaccia
class Indicatore:
    """Calcola tutto una volta per (dati, parametri dell'indicatore) e lo tiene in memoria."""

    def __init__(self, df: pd.DataFrame, P: ParInd = ParInd()):
        self.df = df; self.P = P
        o, h, l, c, v = (df[k].values.astype(np.float64) for k in ("open", "high", "low", "close", "volume"))
        n = len(c)
        atr = pd.Series(h - l).rolling(P.st_len).mean().values
        trend, tstop = _supertrend(h, l, c, atr, P.st_mult)
        pl, ph = _pivot(h, l, P.pivot_left, P.pivot_right)
        chg = np.r_[False, trend[1:] != trend[:-1]]
        age = np.empty(n, np.int64); a = 100000
        for i in range(n):
            a = 0 if chg[i] else a + 1
            age[i] = a
        R = P.pivot_right
        hh = pd.Series(h).rolling(R).max().values
        ll = pd.Series(l).rolling(R).min().values
        vavg = pd.Series(v).rolling(20).mean().values
        hema = ema_htf(df, P.htf, P.htf_len, P.htf_fonte) if P.use_htf else np.full(n, np.nan)
        maxs = int(P.use_imp) + int(P.use_age) + int(P.use_htf) + int(P.use_dist) + int(P.use_vol)
        need = min(P.min_score, maxs)
        r = _order_block(o, h, l, c, v, atr, trend, tstop, pl, ph, chg, age, hh, ll, vavg, hema, R, P.zona_h,
                         P.use_imp, P.imp_mult, P.use_age, P.min_age, P.use_htf, P.use_dist, P.dist_mult,
                         P.use_vol, P.vol_mult, need)
        (self.act_id, self.act_dir, self.act_top, self.act_bot, self.sig_l, self.sig_s, self.n_ob, self.n_rej,
         ob_conf, ob_piv, ob_dir, ob_top, ob_bot, ob_score, ob_end, ob_rotto, ob_f) = r
        self.o, self.h, self.l, self.c, self.v = o, h, l, c, v
        self.atr, self.trend, self.tstop, self.pl, self.ph, self.chg, self.age, self.hema = atr, trend, tstop, pl, ph, chg, age, hema
        # ultimo minimo / massimo di pivot confermato (per il trailing sullo swing): noto dalla candela di conferma
        k = np.arange(n) - R
        self.swlo = pd.Series(np.where(pl, l[np.maximum(k, 0)], np.nan)).ffill().values
        self.swhi = pd.Series(np.where(ph, h[np.maximum(k, 0)], np.nan)).ffill().values
        self.ob = pd.DataFrame({"conf": ob_conf, "pivot": ob_piv, "dir": ob_dir, "top": ob_top, "bottom": ob_bot,
                                "score": ob_score, "fine": ob_end, "rotto": ob_rotto, "f_imp": ob_f[:, 0],
                                "f_age": ob_f[:, 1], "f_htf": ob_f[:, 2], "f_dist": ob_f[:, 3], "f_vol": ob_f[:, 4]})
        self.ob["t_pivot"] = df.index[self.ob["pivot"].values]
        self.ob["t_conferma"] = df.index[self.ob["conf"].values]

    def param(self) -> dict:
        return asdict(self.P)
