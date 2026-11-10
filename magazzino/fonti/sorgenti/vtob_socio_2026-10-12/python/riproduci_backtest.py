"""Backtest della combinazione VTOB "A+B+C consigliata + US_M30" (ultimi 4 anni): rifà tutti i trade e le statistiche.

Uso (Python 3.11+):
    pip install -r requirements.txt
    python riproduci_backtest.py
Scrive in ../backtest/ i trade e i riepiloghi (CSV) e i grafici, e stampa il riepilogo.

Le quattro strategie:
    A consigliata  XAUUSD M15  solo long
    B consigliata  XAUUSD H1   long e short
    C              XAUUSD M30  long e short
    US_M30         USTEC  M30  solo long (Nasdaq 100)
Ogni strategia rischia la stessa cifra per trade (1R). Le % del conto sono R x 0,5 (rischio 0,5% a trade, senza
interesse composto).

Periodo: trade entrati dal 12/07/2022 al 09/10/2026.
Dati (cartella dati/):
- export MT5 di XAUUSD (M15, M30, H1, H4, D1, W1) e di USTEC M30;
- NAS100 D1 Dukascopy dal 2016, per avere la EMA200 giornaliera vera di US_M30.

Costi:
- oro: spread reale della candela d'ingresso + 0,10 $ per lato;
- Nasdaq: spread reale + 0,5 punti.

Regole del motore (identiche all'EA MT5):
- segnale a candela chiusa, ingresso all'apertura della candela dopo;
- nessun dato del futuro;
- se una candela tocca sia lo stop sia il target, conta lo stop.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from vtob import config as CF                                       # noqa: E402
from vtob import dati as DT                                         # noqa: E402
from vtob import indicatore as IM                                   # noqa: E402
from vtob import metriche as MT                                     # noqa: E402
from vtob.indicatore import Indicatore, ParInd                      # noqa: E402
from vtob.motore import Serie, esegui, tabella                      # noqa: E402
from vtob.simulatore import cfg_vettore                             # noqa: E402

DATI = QUI / "dati"
USCITA = QUI.parent / "backtest"
INIZIO, FINE = pd.Timestamp("2022-07-12"), pd.Timestamp("2026-10-10")
ULTIMI_12 = pd.Timestamp("2025-10-09")
RISCHIO = 0.5
ORO = {"A": ("A consigliata", {**CF.STRATEGIE["A"], "parz": "50@1.5", "pbe": True}),
       "B": ("B consigliata", {**CF.STRATEGIE["B"], "parz": "33x3", "pbe": True}),
       "C": ("C", dict(CF.STRATEGIE["C"]))}


def _trade(S: Serie, T: np.ndarray, chiave: str, simbolo: str, regimi: pd.Series) -> pd.DataFrame:
    D = tabella(S, T)
    D = D[(D["t_in"] >= INIZIO) & (D["t_in"] < FINE)]
    q = pd.DatetimeIndex(D["t_in"]).to_period("Q")
    return pd.DataFrame({"strategia": chiave, "simbolo": simbolo, "ingresso": D["t_in"].values, "uscita": D["t_out"].values,
                         "direzione": np.where(D["dir"] > 0, "BUY", "SELL"), "R": D["R"].round(4).values,
                         "pct_conto": (D["R"] * RISCHIO).round(4).values, "esito": D["esito"].values,
                         "regime_trimestre": regimi.reindex(q).values})


def regimi(close: pd.Series) -> pd.Series:
    """Rialzo / ribasso / laterale del trimestre (rendimento > +5%, < -5%, altrimenti)."""
    q = close.groupby(close.index.to_period("Q")).last()
    r = q / q.shift(1) - 1
    return pd.Series(np.where(r > 0.05, "rialzo", np.where(r < -0.05, "ribasso", "laterale")), index=q.index)


def trade_oro() -> pd.DataFrame:
    IM._HTF.clear()
    for tf in ("H1", "H4", "D1", "W1"):                       # EMA del timeframe superiore: candele HTF già chiuse
        IM._HTF[tf] = DT.carica(tf, cartella=DATI)
    reg = regimi(IM._HTF["D1"]["close"])
    out = []
    for k, (nome, g) in ORO.items():
        g = CF.normalizza(g)
        df = DT.carica(g["tf"], cartella=DATI)
        df = df[df.index >= pd.Timestamp("2022-01-01")]      # 6 mesi per scaldare gli indicatori
        S = Serie(g["tf"], df)
        T = esegui(S, Indicatore(S.df, CF.par_ind(g)), CF.vettore(g, CF.COSTI), CF.xflag(S, g))
        out.append(_trade(S, T, k, "XAUUSD", reg))
    return pd.concat(out, ignore_index=True)


def trade_us30() -> pd.DataFrame:
    d = pd.read_csv(DATI / "USTEC_M30.csv")
    df = pd.DataFrame({"open": d["open"].values, "high": d["high"].values, "low": d["low"].values,
                       "close": d["close"].values, "volume": d["tick_volume"].astype(float).values,
                       "spread": d["spread"].astype(float).values * 0.01 + 0.5},
                      index=pd.DatetimeIndex(pd.to_datetime(d["time"]), name="time"))
    k = pd.read_csv(DATI / "NAS100_D1.csv")
    d1 = pd.DataFrame({"open": k["Open"].values, "high": k["High"].values, "low": k["Low"].values,
                       "close": k["Close"].values},
                      index=pd.to_datetime(k["Date"] + " " + k["Time"], format="%Y.%m.%d %H:%M"))
    IM._HTF.clear()
    IM._HTF["D1"] = d1
    S = Serie("M30", df)
    P = ParInd(st_len=50, st_mult=3.5, pivot_left=7, pivot_right=3, zona_h=1.0, use_imp=False, use_age=True,
               min_age=40, use_htf=True, htf="D1", htf_len=200, use_dist=True, dist_mult=0.0, use_vol=False,
               min_score=5, htf_fonte="file")
    cfg = cfg_vettore(entry="croce", sl="atr", sl_x=4.0, tp="rr", tp_x=4.0, be=(0.0, 0.0), trail="st",
                      trail_start="subito", direzione="long", spread_mult=1.0, slippage=0.0, commissione=0.0)
    T = esegui(S, Indicatore(df, P), cfg)
    return _trade(S, T, "US_M30", "USTEC", regimi(df["close"]))


def statistiche(D: pd.DataFrame) -> dict:
    D = D.sort_values("uscita")
    R = D["R"].values.astype(np.float64)
    mesi = pd.period_range(INIZIO, FINE - pd.Timedelta(days=1), freq="M")
    m = pd.Series(R, index=pd.DatetimeIndex(D["uscita"]).to_period("M")).groupby(level=0).sum().reindex(mesi, fill_value=0.0)
    eq = m.cumsum().values
    picco = np.maximum.accumulate(np.maximum(eq, 0))
    sott, cur = 0, 0
    for x in picco - eq:
        cur = cur + 1 if x > 1e-9 else 0
        sott = max(sott, cur)
    sem = pd.Series(R, index=pd.DatetimeIndex(D["uscita"])).groupby(lambda t: f"{t.year}-{1 if t.month <= 6 else 2}").sum()
    dd95, st95 = MT.monte_carlo(R, 1000, 7)
    ult = D[D["ingresso"] >= ULTIMI_12]["R"].values
    g, p = R[R > 0].sum(), -R[R < 0].sum()
    out = {"trade": len(R), "trade_a_settimana": len(R) / ((FINE - INIZIO) / pd.Timedelta(days=7)),
           "vincenti_%": 100 * (R > 0).mean(), "profit_factor": g / p, "R_totale": R.sum(), "R_medio": R.mean(),
           "%_conto_totale": R.sum() * RISCHIO, "drawdown_max_R": MT.max_dd(R), "drawdown_max_%": MT.max_dd(R) * RISCHIO,
           "drawdown_95%_MonteCarlo_%": dd95 * RISCHIO, "perdite_di_fila_max": MT.serie_perdente(R),
           "perdite_di_fila_95%_MonteCarlo": st95, "mesi_positivi_%": 100 * (m > 0).mean(),
           "mese_medio_%": m.mean() * RISCHIO, "mese_mediano_%": float(np.median(m)) * RISCHIO,
           "mese_peggiore_%": m.min() * RISCHIO, "mese_migliore_%": m.max() * RISCHIO,
           "sharpe_mensile": m.mean() / m.std(ddof=1), "mesi_di_fila_sotto_il_massimo": sott,
           "semestri_positivi": f"{int((sem > 0).sum())}/{len(sem)}", "ultimi_12_mesi_%": ult.sum() * RISCHIO,
           "ultimi_12_mesi_trade": len(ult)}
    for a in range(2022, 2027):
        out[f"anno_{a}_%"] = D.loc[pd.DatetimeIndex(D["uscita"]).year == a, "R"].sum() * RISCHIO
    for r in ("rialzo", "laterale", "ribasso"):
        x = D.loc[D["regime_trimestre"] == r, "R"]
        out[f"R_medio_{r}"] = x.mean() if len(x) else np.nan
        out[f"trade_{r}"] = len(x)
    return out, m


def max_insieme(D: pd.DataFrame) -> int:
    ev = pd.concat([pd.DataFrame({"t": D["ingresso"], "d": 1}), pd.DataFrame({"t": D["uscita"], "d": -1})])
    return int(ev.sort_values(["t", "d"])["d"].cumsum().max())


def calcola() -> dict:
    T = pd.concat([trade_oro(), trade_us30()], ignore_index=True).sort_values("uscita").reset_index(drop=True)
    gruppi = {"A consigliata": ["A"], "B consigliata": ["B"], "C": ["C"], "US_M30": ["US_M30"],
              "TUTTE INSIEME": ["A", "B", "C", "US_M30"], "solo A+B+C (senza US_M30)": ["A", "B", "C"]}
    stats, mensili = {}, {}
    for nome, parti in gruppi.items():
        D = T[T["strategia"].isin(parti)]
        s, m = statistiche(D)
        s["posizioni_aperte_insieme_max"] = max_insieme(D)
        stats[nome], mensili[nome] = s, m
    return {"trade": T, "stats": pd.DataFrame(stats), "mensile_R": pd.DataFrame(mensili)}


def grafici(r: dict, cartella: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    T = r["trade"]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for nome, parti, lw in (("Tutte insieme", ["A", "B", "C", "US_M30"], 2.6), ("Solo A+B+C (oro)", ["A", "B", "C"], 1.4)):
        D = T[T["strategia"].isin(parti)].sort_values("uscita")
        ax.plot(pd.to_datetime(D["uscita"]), (D["R"] * RISCHIO).cumsum(), lw=lw, label=nome)
    ax.set_title("Backtest: % del conto con rischio 0,5% a trade (senza interesse composto)")
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(cartella / "grafico_equity.png", dpi=120); plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for k in ("A", "B", "C", "US_M30"):
        D = T[T["strategia"] == k].sort_values("uscita")
        ax.plot(pd.to_datetime(D["uscita"]), D["R"].cumsum(), lw=1.6, label=k)
    ax.set_title("Ogni strategia da sola: R cumulati (1R = rischio di un trade)")
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(cartella / "grafico_strategie.png", dpi=120); plt.close(fig)
    m = r["mensile_R"]["TUTTE INSIEME"] * RISCHIO
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.bar(m.index.to_timestamp(), m.values, width=20, color=np.where(m.values >= 0, "#2a9d5c", "#d9534f"))
    ax.set_title("Mese per mese, tutte insieme (% del conto)")
    ax.grid(alpha=.3, axis="y"); fig.tight_layout(); fig.savefig(cartella / "grafico_mesi.png", dpi=120); plt.close(fig)


def main():
    USCITA.mkdir(parents=True, exist_ok=True)
    r = calcola()
    r["trade"].to_csv(USCITA / "trade_tutti.csv", index=False, sep=";", decimal=",")
    r["stats"].round(3).to_csv(USCITA / "statistiche.csv", sep=";", decimal=",")
    (r["mensile_R"] * RISCHIO).round(3).rename_axis("mese").to_csv(USCITA / "mensile_pct.csv", sep=";", decimal=",")
    grafici(r, USCITA)
    s = r["stats"]["TUTTE INSIEME"]
    print(f"Tutte insieme: {s['trade']:.0f} trade, PF {s['profit_factor']:.2f}, {s['%_conto_totale']:+.1f}% del conto, "
          f"drawdown {s['drawdown_max_%']:.1f}%, mesi positivi {s['mesi_positivi_%']:.0f}%, "
          f"mese peggiore {s['mese_peggiore_%']:+.1f}%")
    print(f"File scritti in {USCITA}")


if __name__ == "__main__":
    main()
