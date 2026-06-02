"""Prototipo Layer 1 — motore di esposizione (regime -> % azionario vs cash).

Testa se un layer di market-timing dell'esposizione produce il profilo ASIMMETRICO
voluto (partecipa ai rally, protegge nei cali) meglio del buy&hold, su ~20+ anni con
piu' regimi (2003-2026 include 2008, 2020, 2022). Dati gratuiti: SPY (yfinance, total
return via auto_adjust) + FRED (WALCL bilancio Fed, DFF tasso).

Regole confrontate:
  1. Buy&Hold SPY
  2. Faber 10-month SMA timing (in SPY se close>SMA10m, else cash al risk-free)
  3. Fed-quadrant exposure (trend tassi x trend bilancio -> peso azionario)
  4. Combined: trend Faber AND backdrop Fed

Metriche: CAGR, vol, Sharpe, maxDD, up/down-capture, % mesi-giu positivi, alpha CAPM.

Uso: python -m strategies.stock_selector.analysis.layer1_prototype
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf


def fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    df = pd.read_csv(url, parse_dates=[0])
    df.columns = ["date", series_id]
    df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
    return df.set_index("date")[series_id].dropna()


def load_monthly():
    spy = yf.download("SPY", start="1995-01-01", end="2026-06-02",
                      auto_adjust=True, progress=False)["Close"]
    if isinstance(spy, pd.DataFrame):
        spy = spy.iloc[:, 0]
    spy_m = spy.resample("ME").last()
    walcl = fred("WALCL").resample("ME").last()       # bilancio Fed (settimanale->mensile)
    dff = fred("DFF").resample("ME").mean()            # tasso effettivo (giornaliero->mensile)
    df = pd.DataFrame({"spy": spy_m}).dropna()
    df["walcl"] = walcl.reindex(df.index, method="ffill")
    df["rf_m"] = (dff.reindex(df.index, method="ffill") / 100.0) / 12.0  # mensile
    df["ret"] = df["spy"].pct_change()
    df["sma10"] = df["spy"].rolling(10).mean()
    return df.dropna(subset=["ret"])


def exposure_faber(df: pd.DataFrame) -> pd.Series:
    # segnale al mese t-1 (no look-ahead): in mercato se close_{t-1} > sma10_{t-1}
    sig = (df["spy"] > df["sma10"]).astype(float).shift(1)
    return sig.fillna(1.0)


def exposure_fed(df: pd.DataFrame) -> pd.Series:
    # trend 6 mesi (segno) di tassi e bilancio, shiftati (no look-ahead)
    rate_chg = df["rf_m"].diff(6)
    bs_chg = df["walcl"].pct_change(6)
    qe = bs_chg > 0          # bilancio in espansione
    rates_down = rate_chg <= 0
    # quadranti -> peso azionario
    w = pd.Series(0.5, index=df.index)
    w[qe & rates_down] = 1.0      # Q1 max liquidita
    w[qe & ~rates_down] = 0.5     # Q2
    w[~qe & rates_down] = 0.5     # Q3
    w[~qe & ~rates_down] = 0.2    # Q4 min liquidita
    return w.shift(1).fillna(0.5)


def strat_returns(df, exposure):
    eq = df["ret"] * exposure
    cash = df["rf_m"] * (1 - exposure)
    return eq + cash


def perf(rets, mkt, rf):
    s = rets.dropna()
    n = len(s)
    cagr = (1 + s).prod() ** (12 / n) - 1
    vol = s.std() * np.sqrt(12)
    sharpe = ((s - rf.reindex(s.index)).mean() * 12) / vol if vol else np.nan
    cum = (1 + s).cumprod()
    maxdd = (cum / cum.cummax() - 1).min()
    m = mkt.reindex(s.index)
    up = m > 0; dn = m <= 0
    up_cap = s[up].mean() / m[up].mean() if m[up].mean() else np.nan
    dn_cap = s[dn].mean() / m[dn].mean() if m[dn].mean() else np.nan
    pos_dn = (s[dn] > 0).mean()
    # alpha CAPM: regress excess strat on excess market
    y = (s - rf.reindex(s.index)).dropna()
    x = (m - rf.reindex(s.index)).reindex(y.index)
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit()
    alpha_ann = res.params.iloc[0] * 12
    alpha_t = res.tvalues.iloc[0]
    beta = res.params.iloc[1]
    return dict(cagr=cagr, vol=vol, sharpe=sharpe, maxdd=maxdd, up=up_cap,
                dn=dn_cap, pos_dn=pos_dn, alpha=alpha_ann, alpha_t=alpha_t, beta=beta, n=n)


def main():
    df = load_monthly()
    # finestra comune dove WALCL esiste (2003+)
    df = df[df.index >= "2003-01-01"]
    rf = df["rf_m"]
    mkt = df["ret"]

    strategies = {
        "Buy&Hold SPY": pd.Series(1.0, index=df.index),
        "Faber 10m-SMA": exposure_faber(df),
        "Fed-quadrant": exposure_fed(df),
        "Faber AND Fed": (exposure_faber(df) * exposure_fed(df)),
    }
    print(f"Periodo: {df.index[0].date()} -> {df.index[-1].date()} ({len(df)} mesi)\n")
    print(f"{'strategia':<16}{'CAGR':>7}{'vol':>7}{'Sharpe':>7}{'maxDD':>8}"
          f"{'up-cap':>8}{'dn-cap':>8}{'+giu%':>7}{'alpha':>8}{'a_t':>6}{'beta':>6}")
    for name, exp in strategies.items():
        r = strat_returns(df, exp.clip(0, 1)) if name != "Buy&Hold SPY" else mkt
        p = perf(r, mkt, rf)
        print(f"{name:<16}{p['cagr']:>+7.1%}{p['vol']:>7.1%}{p['sharpe']:>+7.2f}"
              f"{p['maxdd']:>+8.1%}{p['up']:>8.0%}{p['dn']:>8.0%}{p['pos_dn']:>7.0%}"
              f"{p['alpha']:>+8.1%}{p['alpha_t']:>+6.2f}{p['beta']:>6.2f}")
    print("\nLettura: obiettivo = up-cap alto + dn-cap basso + alpha_t>2 (alpha CAPM significativo).")
    print("dn-cap basso e maxDD ridotto = protezione; up-cap<100% = costo nei rally (whipsaw).")


if __name__ == "__main__":
    main()
