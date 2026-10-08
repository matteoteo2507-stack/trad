"""Candidato A (08/10/2026): mean reversion giornaliera sugli indici USA. PRIMO PASSO, 0 trial: quanti segnali e
quanta potenza, PRIMA di qualunque pre-registrazione.

Regola di questo script, verificabile leggendolo: NON calcola nessun rendimento successivo a un segnale. Conta i
segnali delle regole della fonte esterna e usa solo informazione nota AL segnale (ATR, prezzo) per stimare la
variabilita' di un trade. Quindi non guarda l'esito e non spende tentativi (STRATEGY_LIFECYCLE §3; precedenti:
regola dell'1% sul VIX e COT, 03/10, contati a 0 trial).

Regole contate, dalla fonte esterna (video 2 della sessione col socio, e Connors-Alvarez 2008 come riferimento
classico da confermare all'acquisizione), non tarate da noi:
  R1  RSI(2) < 10 -> long, > 90 -> short
  R2  RSI(2) < 10 -> long solo con chiusura sopra la media a 200 giorni (forma "canonica", solo long)
  R3  chiusura sotto la banda di Bollinger(20, 2) -> long, sopra -> short

Un "episodio" e' una sequenza di giorni consecutivi con segnale nella stessa direzione: con una posizione alla volta
si avvicina al numero di trade. SPX500 e NAS100 sono molto correlati: gli episodi nello stesso giorno su entrambi si
contano anche una volta sola (stima degli eventi indipendenti).

    python analysis/meanrev_indici/potenza.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core.verifiche import fattore_potenza  # noqa: E402

DATI = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")
STRUMENTI = ("SPX500", "NAS100")
K = fattore_potenza(0.05, 0.80)       # 2,80
HOLD = 3                              # giorni di tenuta tipici di un'uscita "al ritorno" (ipotesi dichiarata)


def carica(sym):
    d = pd.read_csv(os.path.join(DATI, f"{sym}_D1.csv"), parse_dates=["time"]).set_index("time").sort_index()
    d = d[d.index.dayofweek < 5]          # Dukascopy D1 ha anche barre di domenica: fuori
    return d[~d.index.duplicated()]


def rsi(c, n=2):
    x = c.diff()
    up = x.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-x.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def atr_pct(d, n=14):
    pc = d["close"].shift(1)
    tr = pd.concat([d.high - d.low, (d.high - pc).abs(), (d.low - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / d["close"] * 100


def segnali(d):
    c = d["close"]; r = rsi(c); sma200 = c.rolling(200).mean()
    m, sd = c.rolling(20).mean(), c.rolling(20).std()
    out = {}
    out["R1 RSI(2) 10/90"] = np.where(r < 10, 1, np.where(r > 90, -1, 0))
    out["R2 RSI(2)<10 sopra SMA200 (solo long)"] = np.where((r < 10) & (c > sma200), 1, 0)
    out["R3 Bollinger(20,2)"] = np.where(c < m - 2 * sd, 1, np.where(c > m + 2 * sd, -1, 0))
    return {k: pd.Series(v, index=d.index) for k, v in out.items()}


def episodi(s):
    """Primo giorno di ogni sequenza di segnali nella stessa direzione."""
    return s[(s != 0) & (s != s.shift(1))]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    dati = {s: carica(s) for s in STRUMENTI}
    anni = {s: (d.index[-1] - d.index[0]).days / 365.25 for s, d in dati.items()}
    sig = {s: segnali(d) for s, d in dati.items()}
    atr = {s: atr_pct(d) for s, d in dati.items()}
    print("Candidato A, conteggio a 0 trial. Dati Dukascopy D1, nessun rendimento dopo il segnale calcolato.")
    for s, d in dati.items():
        print(f"  {s}: {d.index[0].date()} -> {d.index[-1].date()} ({anni[s]:.1f} anni, {len(d)} giorni)")
    print()
    righe = []
    for regola in sig[STRUMENTI[0]]:
        ep = {s: episodi(sig[s][regola]) for s in STRUMENTI}
        n_tot = sum(len(e) for e in ep.values())
        anni_m = np.mean(list(anni.values()))
        giorni_insieme = len(set(ep["SPX500"].index) & set(ep["NAS100"].index))
        n_indip = n_tot - giorni_insieme                       # stesso giorno su entrambi = un evento
        # variabilita' di un trade in % del prezzo, solo da informazione ex ante: ATR al segnale -> sigma giornaliera
        # (ATR ~ 1,4 sigma per un moto browniano su barre giornaliere) -> sqrt(HOLD) giorni
        atr_sig = pd.concat([atr[s].reindex(ep[s].index) for s in STRUMENTI]).dropna()
        sigma_trade = float(atr_sig.median() / 1.4 * np.sqrt(HOLD))
        mde_pct = K * sigma_trade / np.sqrt(n_indip)
        righe.append({"regola": regola, "episodi SPX": len(ep["SPX500"]), "episodi NAS": len(ep["NAS100"]),
                      "stesso giorno": giorni_insieme, "eventi indip.": n_indip, "per anno": n_indip / anni_m,
                      "ATR% al segnale": float(atr_sig.median()), "sigma trade %": sigma_trade,
                      "MDE % (storia intera)": mde_pct})
    t = pd.DataFrame(righe)
    pd.set_option("display.width", 220)
    print(t.round(3).to_string(index=False))
    print()
    print(f"MDE = {K:.2f} * sigma_trade / sqrt(eventi indipendenti); sigma_trade = ATR%/1,4 * sqrt({HOLD}).")
    print("Anni di FORWARD per vedere un effetto E (% per trade), al ritmo di eventi indipendenti di ogni regola:")
    for _, r in t.iterrows():
        cella = []
        for e in (0.10, 0.20, 0.30, 0.50):
            n = (K * r["sigma trade %"] / e) ** 2
            cella.append(f"E={e:.2f}%: {n / r['per anno']:5.1f} anni")
        print(f"  {r['regola']:38s} " + " | ".join(cella))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
