"""Intake del canale YouTube Financial Freedom 101 (13/10/2026): conti rifatti sui numeri dichiarati. 0 trial.

Non prova strategie e non sceglie parametri: ricalcola cio' che i due video affermano, con le stesse convenzioni
della fonte, e misura sui nostri dati l'argomento dei "giorni migliori persi".

Cosa stampa:
1. COMMISSIONI (video HBCGczqLGNY): 300 al mese per 40 anni ai tassi della fonte, poi lo stesso conto col costo
   annuo del nostro PAC (OCF e bollo, fonte: docs/INVESTING_PILLAR_PLAN.md par. 0).
2. GIORNI MIGLIORI (video HBCGczqLGNY): crescita dell'S&P 500 togliendo i giorni migliori, i peggiori, entrambi,
   e quanti dei migliori cadono subito dopo un peggiore. Dati: Dukascopy D1, solo prezzo, senza dividendi.
3. COERENZA (video 9MuAacOIAv4): i versamenti dichiarati, investiti ai rendimenti che la fonte stessa elenca,
   arrivano all'ordine di grandezza del patrimonio dichiarato?

Uso: python analysis/pac_intake/verifiche_ff101.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPX = os.path.join(RADICE, "analysis", "trading-bot-eval", "data", "dukascopy_d1", "SPX500_D1.csv")

RATA, MESI = 300, 480
OCF, BOLLO = 0.14, 0.20          # % annuo, dal par. 0 del piano (factsheet al 31/08/2026; bollo di legge)

# video 9MuAacOIAv4: anno -> (rendimento S&P 500 dichiarato in %, versamento dichiarato in migliaia di dollari)
# Il 2022 non ha un rendimento dichiarato: -18 e' il rendimento totale noto dell'anno. Il 2012 e' ambiguo nella
# trascrizione ("25% additional contribution"): letto come 25 mila.
DICHIARATI = {2010: (15, 2), 2011: (2, 8), 2012: (16, 25), 2013: (32, 18), 2014: (14, 18), 2015: (1, 20),
              2016: (12, 23), 2017: (22, 27), 2018: (-4, 33), 2019: (29, 44), 2020: (18, 45), 2021: (28, 46),
              2022: (-18, 34), 2023: (24, 54), 2024: (23, 57), 2025: (16, 59)}
VENDITE = {2013: 25, 2022: 200}  # azioni vendute per comprare casa, migliaia di dollari
# inizio 2026, migliaia: 401k, azioni, IRA (investiti) | pensione a saldo di cassa | liquidita' | casa (stima bassa)
INVESTITI, PENSIONE, LIQUIDITA, CASA = 665 + 128 + 99, 65, 94, 240


def montante(tasso_annuo_pct: float) -> float:
    """Rata mensile a fine mese, capitalizzazione mensile al tasso annuo / 12 (convenzione della fonte)."""
    i = tasso_annuo_pct / 100 / 12
    return RATA * ((1 + i) ** MESI - 1) / i


def commissioni() -> None:
    print("1. COMMISSIONI - 300 al mese per 40 anni")
    for nome, t in (("nominale 10,5%", 10.5), ("reale 8%", 8.0), ("fondo indice 7,9%", 7.9),
                    ("gestito -1%", 7.0), ("gestito -2%", 6.0)):
        print(f"   {nome:<20} {montante(t):>12,.0f}   {montante(t) / montante(8.0) - 1:+7.1%} sul reale 8%")
    print("   nostro PAC, perdita sul capitale finale rispetto a costo zero:")
    for base in (8.0, 5.0):
        riga = "   ".join(f"{nome} {montante(base - c) / montante(base) - 1:+.1%}"
                          for nome, c in (("OCF", OCF), ("bollo", BOLLO), ("OCF+bollo", OCF + BOLLO), ("1%", 1.0)))
        print(f"   rendimento reale {base:.0f}%:  {riga}")


def giorni_migliori() -> None:
    df = pd.read_csv(SPX, parse_dates=["time"])
    df = df[df["time"].dt.weekday < 5].reset_index(drop=True)      # le barre della domenica entrano nel lunedi'
    r = df["close"].pct_change().dropna().reset_index(drop=True)
    anni = (df["time"].iloc[-1] - df["time"].iloc[0]).days / 365.25
    tot = float((1 + r).prod())
    print(f"\n2. GIORNI MIGLIORI - S&P 500 {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}, "
          f"{len(r)} giorni, {anni:.1f} anni, solo prezzo")
    print(f"   sempre investito: x{tot:.2f} ({tot ** (1 / anni) - 1:+.1%} annuo)")
    ordine = r.sort_values()
    for n in (10, 20, 60):
        senza_m = float((1 + r.drop(ordine.index[-n:])).prod())
        senza_p = float((1 + r.drop(ordine.index[:n])).prod())
        senza_e = float((1 + r.drop(ordine.index[-n:].union(ordine.index[:n]))).prod())
        peggiori = np.array(sorted(ordine.index[:n]))
        vicini = sum(((peggiori < i) & (peggiori >= i - 10)).any() for i in ordine.index[-n:])
        print(f"   {n:>2} giorni: senza i migliori x{senza_m:.2f} ({senza_m ** (1 / anni) - 1:+.1%})   "
              f"senza i peggiori x{senza_p:.2f} ({senza_p ** (1 / anni) - 1:+.1%})   "
              f"senza entrambi x{senza_e:.2f} ({senza_e ** (1 / anni) - 1:+.1%})   "
              f"migliori entro 10 sedute da un peggiore: {vicini}/{n}")


def simula(rendimento_fisso: float | None = None) -> float:
    """Versamenti a meta' anno, vendite a inizio anno. Con `rendimento_fisso` (in %) ignora i rendimenti dichiarati."""
    v = 0.0
    for anno, (rend, vers) in DICHIARATI.items():
        rend = rend if rendimento_fisso is None else rendimento_fisso
        v = (v - VENDITE.get(anno, 0)) * (1 + rend / 100) + vers * (1 + rend / 200)
    return v


def coerenza() -> None:
    v = simula()
    versato = sum(c for _, c in DICHIARATI.values())
    patrimonio = INVESTITI + PENSIONE + LIQUIDITA + CASA
    print("\n3. COERENZA - versamenti dichiarati investiti ai rendimenti dichiarati (migliaia di dollari)")
    print(f"   versato 2010-2025: {versato}   vendite per le case: {sum(VENDITE.values())}")
    print(f"   simulato a inizio 2026: {v:,.0f}   dichiarato investito: {INVESTITI}"
          f"   investito + pensione + liquidita': {INVESTITI + PENSIONE + LIQUIDITA}")
    print(f"   patrimonio dichiarato: {patrimonio}   quota dei versamenti: {versato / patrimonio:.0%}")
    rend = [r for r, _ in DICHIARATI.values()]
    print(f"   rendimento annuo composto dei 16 anni dichiarati: "
          f"{np.prod([1 + x / 100 for x in rend]) ** (1 / len(rend)) - 1:+.1%}")
    print("   stessi versamenti e vendite a rendimento costante: "
          + "   ".join(f"{t}% -> {simula(t):,.0f}" for t in (0, 5, 7, 10)))
    # rendimenti dichiarati contro i nostri dati: solo prezzo, quindi sotto il dichiarato di circa i dividendi (1-2 punti)
    df = pd.read_csv(SPX, parse_dates=["time"])
    fine = df.groupby(df["time"].dt.year)["close"].last()
    nostri = (fine / fine.shift(1) - 1).dropna() * 100
    scarti = [DICHIARATI[a][0] - nostri[a] for a in nostri.index if a in DICHIARATI and a != 2022]
    print(f"   rendimenti dichiarati meno i nostri (solo prezzo), {len(scarti)} anni dal {nostri.index[0]}: "
          f"medio {np.mean(scarti):+.1f} punti, da {min(scarti):+.1f} a {max(scarti):+.1f}")


if __name__ == "__main__":
    commissioni()
    giorni_migliori()
    coerenza()
