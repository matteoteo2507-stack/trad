"""Metriche di COSTANZA sui rendimenti mensili (mesi senza trade compresi) e metriche per trade.

Rendimento di un mese = somma degli R dei trade USCITI in quel mese (risultato realizzato). In % del conto, con rischio
fisso r per trade e senza interesse composto, è r x R: le metriche in R valgono anche in % (scala lineare).
- pct_pos: % di mesi con risultato > 0;
- sharpe: media / deviazione standard dei risultati mensili (Sharpe mensile, senza tasso privo di rischio);
- peggiore: mese peggiore; media e mediana;
- sottacqua: numero massimo di mesi consecutivi chiusi sotto il massimo precedente dell'equity (da 0);
- ulcer: radice della media dei quadrati del drawdown di fine mese (in R): penalizza drawdown profondi E lunghi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import metriche

SPLIT = pd.Timestamp("2025-07-01")            # primo periodo (scelta) fino a giugno 2025, poi verifica


def mesi(t0, t1) -> pd.PeriodIndex:
    return pd.period_range(pd.Timestamp(t0), pd.Timestamp(t1), freq="M")


def serie_mensile(t_out, R, elenco_mesi: pd.PeriodIndex) -> np.ndarray:
    """Somma degli R per mese d'uscita, con zero nei mesi senza trade."""
    if len(R) == 0:
        return np.zeros(len(elenco_mesi))
    s = pd.Series(np.asarray(R, float), index=pd.DatetimeIndex(t_out).to_period("M")).groupby(level=0).sum()
    return s.reindex(elenco_mesi, fill_value=0.0).values


def metriche_mensili(m: np.ndarray) -> dict:
    m = np.asarray(m, float)
    if len(m) == 0:
        return {}
    eq = np.cumsum(m)
    picco = np.maximum.accumulate(np.maximum(eq, 0.0))
    dd = picco - eq
    sotto, cur = 0, 0
    for x in dd:
        cur = cur + 1 if x > 1e-9 else 0
        sotto = max(sotto, cur)
    sd = m.std(ddof=1) if len(m) > 1 else np.nan
    return dict(mesi=len(m), pct_pos=100.0 * (m > 0).mean(), sharpe=(m.mean() / sd) if sd and sd > 0 else np.nan,
                media=m.mean(), mediana=float(np.median(m)), peggiore=m.min(), migliore=m.max(), sottacqua=sotto,
                ulcer=float(np.sqrt(np.mean(dd ** 2))), dd_mensile=float(dd.max()))


def metriche_trade(R: np.ndarray, settimane: float | None = None, mc: bool = True) -> dict:
    R = np.asarray(R, float)
    if len(R) == 0:
        return dict(trade=0)
    out = dict(trade=len(R), PF=metriche.pf(R), R_tot=float(R.sum()), R_medio=float(R.mean()),
               maxDD=float(metriche.max_dd(R)), serie_perdente=int(metriche.serie_perdente(R)))
    if settimane:
        out["trade_sett"] = len(R) / settimane
    if mc and len(R) >= 5:
        dd95, st95 = metriche.monte_carlo(R, 1000, 7)
        out["DD_MC95"] = float(dd95); out["serie_MC95"] = float(st95)
    return out


def scheda(T: pd.DataFrame, t0, t1, split=SPLIT, mc: bool = True) -> dict:
    """Tutte le metriche (intero, primo periodo, secondo periodo) di una tabella di trade con t_in, t_out, R."""
    T = T.sort_values("t_out")                              # drawdown e serie in ordine di uscita
    el = mesi(t0, t1)
    m = serie_mensile(T["t_out"], T["R"], el)
    is_m = np.asarray(el < pd.Period(split, "M"))
    sett = (pd.Timestamp(t1) - pd.Timestamp(t0)) / pd.Timedelta(days=7)
    out = {**metriche_trade(T["R"].values, sett, mc), **metriche_mensili(m)}
    for nome, sel_m, sel_t in (("_1", is_m, T["t_in"] < split), ("_2", ~is_m, T["t_in"] >= split)):
        mm = metriche_mensili(m[sel_m])
        out.update({k + nome: v for k, v in mm.items() if k in ("pct_pos", "sharpe", "peggiore", "sottacqua", "ulcer", "media")})
        Rt = T.loc[sel_t, "R"].values
        out["PF" + nome] = metriche.pf(Rt) if len(Rt) else np.nan
        out["R" + nome] = float(Rt.sum())
        out["trade" + nome] = len(Rt)
    return out


def in_percentuale(m_R: np.ndarray, rischio: float) -> dict:
    """Rendimenti mensili in % del conto con rischio fisso (in %) per trade, senza interesse composto."""
    p = np.asarray(m_R) * rischio
    eq = np.cumsum(p); picco = np.maximum.accumulate(np.maximum(eq, 0.0))
    return dict(mese_medio=p.mean(), mese_mediano=float(np.median(p)), mese_peggiore=p.min(), mese_migliore=p.max(),
                totale=p.sum(), dd_max_mensile=float((picco - eq).max()))
