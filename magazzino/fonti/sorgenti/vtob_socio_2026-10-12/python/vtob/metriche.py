"""Statistiche dei trade: risultati in R e in $, ripartizione degli esiti, IS/OOS, periodi, Monte Carlo.

Il drawdown si misura sulla curva cumulata in R che parte da 0 (il motore di riferimento la fa partire dal primo
trade: se la serie inizia con perdite, quel calcolo sottostima il drawdown).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numba import njit

from .simulatore import X_BE, X_PARZ, X_SL, X_TP, X_TRAIL


@njit(cache=True)
def max_dd(r: np.ndarray) -> float:
    eq = 0.0; peak = 0.0; dd = 0.0
    for x in r:
        eq += x
        if eq > peak:
            peak = eq
        if peak - eq > dd:
            dd = peak - eq
    return dd


SOGLIA_PERDITA = -0.1      # un trade "perde" se perde più di 0,1R (le uscite a break-even non contano come perdite)


@njit(cache=True)
def serie_perdente(r: np.ndarray) -> int:
    best = 0; cur = 0
    for x in r:
        if x < SOGLIA_PERDITA:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


@njit(cache=True)
def monte_carlo(r: np.ndarray, n_iter: int = 1000, seed: int = 7):
    """Rimescola l'ordine dei trade n_iter volte: drawdown al 95° percentile e serie perdente al 95° percentile."""
    np.random.seed(seed)
    x = r.copy()
    dd = np.empty(n_iter); st = np.empty(n_iter)
    for k in range(n_iter):
        np.random.shuffle(x)
        dd[k] = max_dd(x)
        st[k] = serie_perdente(x)
    return np.percentile(dd, 95.0), np.percentile(st, 95.0)


def pf(r: np.ndarray) -> float:
    g = r[r > 0].sum(); p = -r[r < 0].sum()
    if p <= 0:
        return np.inf if g > 0 else np.nan
    return g / p


def _blocco(r: np.ndarray) -> dict:
    if len(r) == 0:
        return dict(n=0, pf=np.nan, R=0.0, dd=0.0, rdd=np.nan, avg=np.nan)
    dd = max_dd(r); R = float(r.sum())
    return dict(n=len(r), pf=pf(r), R=R, dd=dd, rdd=(R / dd) if dd > 0 else (np.inf if R > 0 else np.nan),
                avg=float(r.mean()))


def statistiche(T: np.ndarray, t_in: np.ndarray, t_split: np.datetime64, t0: np.datetime64, t1: np.datetime64,
                periodo: str = "Y", mc: bool = True) -> dict:
    """T: matrice dei trade del simulatore; t_in: datetime64 d'ingresso dei trade; t_split: inizio dell'OOS;
    t0/t1: inizio e fine dei dati (per i trade a settimana); periodo: 'Y' anni, 'Q' trimestri, 'M' mesi."""
    n = len(T)
    sett = max((t1 - t0) / np.timedelta64(7, "D"), 1e-9)
    if n == 0:
        return dict(trade=0, trade_sett=0.0)
    R = T[:, 5]; es = T[:, 7].astype(int); d = T[:, 2]
    tot = _blocco(R)
    m_is = t_in < t_split
    bi = _blocco(R[m_is]); bo = _blocco(R[~m_is])
    per = pd.Series(R, index=pd.DatetimeIndex(t_in)).groupby(pd.DatetimeIndex(t_in).to_period(periodo)).sum()
    out = dict(
        trade=n, trade_sett=n / sett,
        win=100.0 * (R > 0).mean(), tp=100.0 * (es == X_TP).mean(), be=100.0 * (es == X_BE).mean(),
        sl=100.0 * (es == X_SL).mean(), parz=100.0 * (es == X_PARZ).mean(), trail=100.0 * (es == X_TRAIL).mean(),
        altro=100.0 * (es > X_TRAIL).mean(),
        PF=tot["pf"], R_tot=tot["R"], R_medio=tot["avg"], maxDD=tot["dd"], R_DD=tot["rdd"],
        pnl_usd=float(T[:, 6].sum()), costo_medio_R=float((T[:, 12] / T[:, 9]).mean()),
        rischio_medio_usd=float(T[:, 9].mean()),
        trade_IS=bi["n"], PF_IS=bi["pf"], R_IS=bi["R"], DD_IS=bi["dd"], R_DD_IS=bi["rdd"],
        trade_OOS=bo["n"], PF_OOS=bo["pf"], R_OOS=bo["R"], DD_OOS=bo["dd"], R_DD_OOS=bo["rdd"],
        R_long=float(R[d == 1].sum()), R_short=float(R[d == -1].sum()),
        n_long=int((d == 1).sum()), n_short=int((d == -1).sum()),
        periodi=len(per), periodi_pos=int((per > 0).sum()), periodi_neg=int((per < 0).sum()),
        periodo_peggiore=float(per.min()), serie_perdente=int(serie_perdente(R)),
    )
    if mc and n >= 5:
        dd95, st95 = monte_carlo(R.astype(np.float64))
        out["DD_MC95"] = float(dd95); out["serie_perdente_MC95"] = float(st95)
    return out


def per_periodo(T: np.ndarray, t_in: np.ndarray, periodo: str = "Y") -> pd.DataFrame:
    """Risultati per anno (o trimestre / mese): trade, R, PF, win%."""
    if len(T) == 0:
        return pd.DataFrame()
    df = pd.DataFrame({"R": T[:, 5], "dir": T[:, 2]}, index=pd.DatetimeIndex(t_in))
    g = df.groupby(df.index.to_period(periodo))["R"]
    return pd.DataFrame({"trade": g.size(), "R": g.sum(), "PF": g.apply(lambda x: pf(x.values)),
                         "win": g.apply(lambda x: 100.0 * (x > 0).mean())})


# ---------------------------------------------------------------- statistiche veloci (griglie da decine di migliaia)
STAT_NOMI = ["trade", "win", "pct_tp", "pct_be", "pct_sl", "pct_parz", "pct_trail", "pct_altro", "PF", "R_tot", "R_medio", "maxDD", "R_DD",
             "trade_IS", "PF_IS", "R_IS", "DD_IS", "R_DD_IS", "R_medio_IS",
             "trade_OOS", "PF_OOS", "R_OOS", "DD_OOS", "R_DD_OOS", "R_medio_OOS",
             "periodi", "periodi_pos", "periodi_neg", "periodo_peggiore", "serie_perdente", "DD_MC95", "serie_MC95",
             "R_long", "R_short", "n_long", "n_short", "costo_medio_R", "trade_sett", "pnl_usd", "rischio_medio_usd"]
_NS = len(STAT_NOMI)


@njit(cache=True)
def _pf(gp, gl):
    if gl > 0:
        return gp / gl
    return 999.0 if gp > 0 else np.nan


@njit(cache=True)
def _rdd(R, dd):
    if dd > 0:
        return R / dd
    return 999.0 if R > 0 else np.nan


@njit(cache=True)
def stat_veloci(T, per_bar, n_per, i_split, settimane, n_mc, seed):
    """Vettore STAT_NOMI da una matrice di trade del simulatore. per_bar: indice del periodo (anno/trimestre/mese) di
    ogni candela; i_split: prima candela dell'OOS; n_mc: rimescolamenti Monte Carlo (0 = niente)."""
    out = np.full(_NS, np.nan)
    n = T.shape[0]
    out[0] = n
    out[37] = n / settimane
    if n == 0:
        return out
    R = T[:, 5].copy()
    gp = 0.0; gl = 0.0; gpi = 0.0; gli = 0.0; gpo = 0.0; glo = 0.0
    ni = 0; no = 0; Ri = 0.0; Ro = 0.0
    eq = 0.0; pk = 0.0; dd = 0.0; eqi = 0.0; pki = 0.0; ddi = 0.0; eqo = 0.0; pko = 0.0; ddo = 0.0
    cnt = np.zeros(8)
    per = np.zeros(n_per)
    Rl = 0.0; Rs = 0.0; nl = 0; ns = 0; cR = 0.0; pnl = 0.0
    for k in range(n):
        x = R[k]
        es = int(T[k, 7])
        if es > 7:
            es = 7
        cnt[es] += 1
        if x > 0:
            gp += x
        else:
            gl -= x
        eq += x
        if eq > pk:
            pk = eq
        if pk - eq > dd:
            dd = pk - eq
        i_in = int(T[k, 0])
        if i_in < i_split:
            ni += 1; Ri += x
            if x > 0:
                gpi += x
            else:
                gli -= x
            eqi += x
            if eqi > pki:
                pki = eqi
            if pki - eqi > ddi:
                ddi = pki - eqi
        else:
            no += 1; Ro += x
            if x > 0:
                gpo += x
            else:
                glo -= x
            eqo += x
            if eqo > pko:
                pko = eqo
            if pko - eqo > ddo:
                ddo = pko - eqo
        per[per_bar[i_in]] += x
        if T[k, 2] > 0:
            Rl += x; nl += 1
        else:
            Rs += x; ns += 1
        cR += T[k, 12] / T[k, 9]
        pnl += T[k, 6]
    out[1] = 100.0 * (R > 0).sum() / n
    out[2] = 100.0 * cnt[1] / n; out[3] = 100.0 * cnt[2] / n; out[4] = 100.0 * cnt[0] / n
    out[5] = 100.0 * cnt[3] / n; out[6] = 100.0 * cnt[4] / n; out[7] = 100.0 * (cnt[5] + cnt[6] + cnt[7]) / n
    Rt = gp - gl
    out[8] = _pf(gp, gl); out[9] = Rt; out[10] = Rt / n; out[11] = dd; out[12] = _rdd(Rt, dd)
    out[13] = ni; out[14] = _pf(gpi, gli); out[15] = Ri; out[16] = ddi; out[17] = _rdd(Ri, ddi)
    out[18] = Ri / ni if ni > 0 else np.nan
    out[19] = no; out[20] = _pf(gpo, glo); out[21] = Ro; out[22] = ddo; out[23] = _rdd(Ro, ddo)
    out[24] = Ro / no if no > 0 else np.nan
    out[25] = n_per; out[26] = (per > 1e-12).sum(); out[27] = (per < -1e-12).sum(); out[28] = per.min()
    out[29] = serie_perdente(R)
    if n_mc > 0 and n >= 5:
        a, b = monte_carlo(R, n_mc, seed)
        out[30] = a; out[31] = b
    out[32] = Rl; out[33] = Rs; out[34] = nl; out[35] = ns; out[36] = cR / n; out[38] = pnl
    out[39] = T[:, 9].mean()
    return out


@njit(cache=True)
def mensili(T, mese_bar, n_mesi):
    """Somma di R e numero di trade per mese d'ingresso (per il walk-forward)."""
    r = np.zeros(n_mesi, np.float32); c = np.zeros(n_mesi, np.int16)
    for k in range(T.shape[0]):
        m = mese_bar[int(T[k, 0])]
        r[m] += T[k, 5]; c[m] += 1
    return r, c
