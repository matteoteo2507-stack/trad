"""Intake del pacchetto VTOB del socio (order block su XAUUSD, 11/10/2026). 0 trial.

Legge SOLO cio' che il socio ha consegnato (barre, trade, griglie) e il suo codice. Non prova varianti, non simula
ingressi, non calcola un baseline casuale: quello e' il test, e si fa solo con una pre-registrazione.

Cosa stampa:
1. RIPRODUCIBILITA: i trade rigenerati col codice del socio coincidono con quelli consegnati?
2. DATI: barre e spread per anno, e il giorno in cui la colonna `spread` cambia unita' (da millesimi a centesimi).
3. TRADE: lato, esito, anno, concentrazione, notti in posizione, successioni, MDE, soglia di futilita'.
4. COSTI: quanto pesa l'errore di unita' dello spread sui R consegnati (gli ingressi non cambiano).
5. DERIVA: quanto rende la SOLA salita dell'oro con la stessa uscita. Formula chiusa del moto browniano con deriva
   costante: e' un ordine di grandezza, non un baseline (non copia lo stato del filtro di tendenza).
6. GRIGLIE: quante varianti sono positive per periodo, lato e ampiezza dello stop; posto delle quattro scelte.

Uso: python analysis/vtob_intake/descrittivi.py [--sorgente DIR] [--materiale DIR] [--hub DIR]
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, RADICE)
from core.trial_ledger import futility_sharpe  # noqa: E402
from core.verifiche import mde, n_richiesto, runs_test  # noqa: E402

SORGENTE = os.path.join(RADICE, "fondamenti_tecnici", "_sorgenti", "vtob_socio_2026-10-11")
MATERIALE = os.path.join(RADICE, "materiale_socio", "vtob_dati_risultati_2022-07_2026-10")
HUB = os.path.join(RADICE, "analysis", "trading-bot-eval", "data")
VARIANTI_DICHIARATE = 46_080
# riga scelta in ogni griglia: pivot, TF della media, eta' del trend, lato, stop (x vol), target (R)
SCELTE = {"M15": ("7/3", "60min", 20, "long", 6, 3.0), "H1": ("10/3", "1440min", 10, "both", 3, 4.0),
          "M30": ("5/2", "240min", 20, "both", 8, 3.0), "M5": ("10/5", "60min", 20, "long", 6, 4.0)}
PARAMETRI = ("piv", "htf", "age", "k", "rr")


def atteso_sola_deriva(theta: np.ndarray, rr: float, be: float = 1.0, off: float = 0.1):
    """E[R] e quote TP/BE/SL di un browniano con deriva sotto la stessa uscita (stop 1R, target rr, pareggio a be).

    theta = 2 * mu * D / sigma^2, con mu e sigma del rendimento log giornaliero, D lo stop come frazione del prezzo,
    e il segno della posizione gia' dentro mu. Senza deriva (theta -> 0) E[R] = 0.
    """
    theta = np.where(np.abs(theta) < 1e-9, 1e-9, theta)

    def tocca_prima_sopra(su: float, giu: float) -> np.ndarray:
        return (1 - np.exp(-theta * giu)) / (1 - np.exp(-theta * (su + giu)))

    p1 = tocca_prima_sopra(be, 1.0)            # arriva a +be prima dello stop
    p2 = tocca_prima_sopra(rr - be, be - off)  # da +be: target prima dello stop a pareggio
    return p1 * (p2 * rr + (1 - p2) * off) - (1 - p1), p1 * p2, p1 * (1 - p2), 1 - p1


def lato(d: int) -> str:
    return "long" if d == 1 else "short"


def per_lato(T: pd.DataFrame) -> dict:
    return {lato(d): (len(X), round(float(X.R.sum()), 1), round(float(X.R.mean()), 3)) for d, X in T.groupby("d")}


def prove_massime(sharpe: float, n: int) -> int:
    """Quante prove indipendenti di rumore bastano perche' la soglia di futilita' superi lo Sharpe osservato."""
    return next((N for N in range(1, 100_001) if futility_sharpe(N, n, 1) > sharpe), 100_001)


def riproducibilita(strategie, ris: str) -> dict[str, pd.DataFrame]:
    print("== 1. RIPRODUCIBILITA (trade rigenerati col codice del socio contro quelli consegnati)")
    out = {}
    for nome in strategie.STRATEGIE:
        nuovo, _ = strategie.trades(nome)
        dato = pd.read_csv(os.path.join(ris, f"trade_{nome}.csv"), parse_dates=["t", "tx"])
        uguali = len(nuovo) == len(dato) and (nuovo.t.values == dato.t.values).all() and np.allclose(nuovo.R, dato.R)
        print(f"  {nome}: consegnati {len(dato)}, rigenerati {len(nuovo)}, identici = {uguali}")
        out[nome] = dato
    return out


def dati_e_spread(m15: pd.DataFrame) -> pd.Timestamp:
    print("\n== 2. DATI (XAUUSD M15 del socio)")
    punti = m15.spread / 0.01
    anno = m15.index.year
    tab = pd.DataFrame({"barre": m15.close.groupby(anno).size(), "chiusura_iniziale": m15.close.groupby(anno).first(),
                        "chiusura_finale": m15.close.groupby(anno).last(), "spread_mediano_punti": punti.groupby(anno).median(),
                        "ampiezza_mediana_$": (m15.high - m15.low).groupby(anno).median()})
    print(tab.round(2).to_string())
    giorno = punti.groupby(m15.index.date).median()
    finestra = giorno[[g for g in giorno.index if pd.Timestamp("2025-10-13") <= pd.Timestamp(g) <= pd.Timestamp("2025-10-24")]]
    print("  spread mediano del giorno (punti) attorno al cambio:", {str(g): float(v) for g, v in finestra.items()})
    cambio = pd.Timestamp(next(g for g in finestra.index if finestra[g] < 40))
    prima, dopo = punti[punti.index < cambio], punti[punti.index >= cambio]
    print(f"  primo giorno a due cifre: {cambio.date()} | multipli di 10: {100 * (prima % 10 == 0).mean():.1f}% prima, "
          f"{100 * (dopo % 10 == 0).mean():.1f}% dopo | mediana {prima.median():.0f} -> {dopo.median():.0f} punti")
    return cambio


def confronto_dukascopy(m15: pd.DataFrame, hub: str) -> None:
    """I prezzi del socio sono quelli del mercato? Chiusure M15 contro il nostro Dukascopy bid, e spread vero per anno."""
    f_bid, f_ask = (os.path.join(hub, f"XAU_duka_M1_{x}.parquet") for x in ("bid", "ask"))
    if not (os.path.exists(f_bid) and os.path.exists(f_ask)):
        print("  Dukascopy M1 non presente nel data hub: confronto saltato")
        return
    bid, ask = pd.read_parquet(f_bid), pd.read_parquet(f_ask)
    spread = (ask.close - bid.close).dropna()
    print(f"  spread Dukascopy (ask - bid alla chiusura M1, $), mediana per anno, file fino al {bid.index[-1].date()}:",
          {int(a): round(float(v), 2) for a, v in spread.groupby(spread.index.year).median().items()})
    duka = bid.close.resample("15min", label="left", closed="left").last().dropna()
    duka.index = duka.index.tz_localize(None)
    scarti = {}
    for ore in (2, 3):  # il server del socio e' a UTC+2 o UTC+3 secondo la stagione: per ogni mese vale lo scarto migliore
        socio = m15.close.copy()
        socio.index = socio.index - pd.Timedelta(hours=ore)
        j = pd.concat([socio.rename("socio"), duka.rename("duka")], axis=1, join="inner")
        scarti[ore] = (j.socio - j.duka).abs().groupby(j.index.to_period("M")).median()
    migliore = pd.DataFrame(scarti).min(axis=1)
    print(f"  |chiusura socio - chiusura Dukascopy|: mediana delle mediane mensili {migliore.median():.3f} $ su {len(migliore)} mesi, "
          f"mese peggiore {migliore.max():.3f} $ ({migliore.idxmax()})")
    prima = bid.close[:str(m15.index[0].date())]
    print(f"  oro Dukascopy prima dell'inizio del file del socio: {prima.iloc[0]:.0f} ({prima.index[0].date()}) -> {prima.iloc[-1]:.0f} "
          f"({prima.index[-1].date()}), {(prima.index[-1] - prima.index[0]).days / 7:.0f} settimane")


def trade_per_strategia(strategie, core, trade: dict[str, pd.DataFrame], m15: pd.DataFrame, cambio: pd.Timestamp) -> None:
    giornaliero = np.log(m15.close.resample("1D").last().dropna()).diff().dropna()
    mu, sd = giornaliero.mean(), giornaliero.std()
    mu_a, sd_a = giornaliero.groupby(giornaliero.index.year).mean(), giornaliero.groupby(giornaliero.index.year).std()
    print(f"\n== 3-5. TRADE, COSTI, DERIVA | oro nel file: {m15.close.iloc[0]:.0f} -> {m15.close.iloc[-1]:.0f}, rendimento log "
          f"giornaliero medio {mu:.5f}, sd {sd:.5f}")
    print("  media giornaliera per anno:", {int(a): round(float(v), 5) for a, v in mu_a.items()})
    somma = {"n": 0, "consegnato": 0.0, "lordo": 0.0, "spread_corretto": 0.0, "deriva": 0.0, "deriva_per_anno": 0.0}
    for nome, (tf, par_ind, par_trade) in strategie.STRATEGIE.items():
        df = strategie.dati(tf)
        K = core(df, **par_ind)
        T = trade[nome].copy()
        i = df.index.get_indexer(T.t)
        assert (i > 0).all(), "un ingresso non trovato fra le barre"
        stop = par_trade["k"] * K["atr"][i - 1]      # distanza dello stop in $, sulla barra del segnale
        spread = np.nan_to_num(K["spr"][i], nan=0.4)  # $ addebitati dal motore del socio (punti * 0,01)
        vero = np.where(T.t < cambio, spread / 10, spread)
        T["lordo"] = T.R + spread / stop
        T["corretto"] = T.lordo - vero / stop
        frazione = stop / K["o"][i]
        a = T.t.dt.year.values
        T["deriva"], q_tp, q_be, q_sl = atteso_sola_deriva(2 * mu * frazione / sd**2 * T.d.values, par_trade["rr"])
        T["deriva_anno"] = atteso_sola_deriva(2 * mu_a.reindex(a).values * frazione / sd_a.reindex(a).values ** 2 * T.d.values,
                                              par_trade["rr"])[0]
        notti = (T.tx.dt.normalize() - T.t.dt.normalize()).dt.days
        vecchi = T.t < cambio
        nullo = atteso_sola_deriva(np.zeros(1), par_trade["rr"])
        print(f"\n  {nome}: n = {len(T)} | R consegnato {T.R.sum():.1f}, media {T.R.mean():.3f}, sd {T.R.std():.3f} | "
              f"stop mediano {np.median(stop):.1f} $ = {100 * np.median(frazione):.2f}% del prezzo | notti in posizione: media {notti.mean():.1f}")
        print("   per lato (n, somma R, media):", per_lato(T))
        print("   somma R per anno:", T.groupby(T.tx.dt.year).R.sum().round(1).to_dict(),
              f"| i 10 trade migliori: {T.R.nlargest(10).sum():.1f} R")
        print(f"   spread addebitato prima del {cambio.date()}: {(spread / stop)[vecchi].mean():.3f} R/trade su {int(vecchi.sum())} trade, "
              f"a unita' corretta {(vero / stop)[vecchi].mean():.3f} | R lordo {T.lordo.sum():.1f}, a unita' corretta {T.corretto.sum():.1f}")
        osservate = (T.R > 1.0).mean(), ((T.R <= 1.0) & (T.R > -0.5)).mean(), (T.R <= -0.5).mean()
        print(f"   quote TP/BE/SL: osservate {osservate[0]:.2f}/{osservate[1]:.2f}/{osservate[2]:.2f} | sola deriva "
              f"{q_tp.mean():.2f}/{q_be.mean():.2f}/{q_sl.mean():.2f} | senza deriva {nullo[1][0]:.2f}/{nullo[2][0]:.2f}/{nullo[3][0]:.2f}")
        print(f"   media lorda {T.lordo.mean():.3f} R | sola deriva {T.deriva.mean():.3f} (media dell'intero file), "
              f"{T.deriva_anno.mean():.3f} (media dell'anno) | scarto {(T.lordo - T.deriva).mean():.3f} e {(T.lordo - T.deriva_anno).mean():.3f} "
              f"| MDE a un test {mde(T.lordo.std(), len(T)):.3f}")
        for d, X in T.groupby("d"):
            print(f"     {lato(d)}: n = {len(X)}, lordo {X.lordo.mean():.3f}, sola deriva {X.deriva.mean():.3f} / {X.deriva_anno.mean():.3f}")
        # una posizione alla volta per strategia: i trade non si sovrappongono, il test delle successioni e' lecito
        s = runs_test((T.sort_values("t").R > 0).values)
        print(f"   successioni vinto/perso: z = {s['z']:.2f} (p = {s['p']:.3f}) | Sharpe per trade {T.R.mean() / T.R.std():.3f} | "
              "soglia di futilita' a N prove: " + ", ".join(f"{N} -> {futility_sharpe(N, len(T), 1):.3f}" for N in (1, 100, 1000, 11_520, VARIANTI_DICHIARATE))
              + f" | sotto soglia da N = {prove_massime(T.R.mean() / T.R.std(), len(T))}")
        if nome != "D_M5":
            somma["n"] += len(T)
            for chiave, col in (("consegnato", "R"), ("lordo", "lordo"), ("spread_corretto", "corretto"), ("deriva", "deriva"),
                                ("deriva_per_anno", "deriva_anno")):
                somma[chiave] += T[col].sum()
    print("\n  A+B+C:", {k: round(float(v), 1) for k, v in somma.items()})


def portafoglio(ris: str) -> None:
    P = pd.read_csv(os.path.join(ris, "portafoglio_trade.csv"), parse_dates=["t", "tx"])
    print(f"\n== PORTAFOGLIO A+B+C (trade sovrapposti: n = {len(P)} non sono {len(P)} osservazioni indipendenti)")
    print("  per lato (n, somma R, media):", per_lato(P))
    print("  somma R per anno e lato:")
    print(P.groupby([P.tx.dt.year, "d"]).R.sum().unstack().rename(columns={-1: "short", 1: "long"}).round(1).to_string())
    mesi = P.pivot_table(index=P.tx.dt.to_period("M"), columns="strategia", values="R", aggfunc="sum").fillna(0)
    c = mesi.corr()
    print(f"  correlazione fra le tre, R mensile, {len(mesi)} mesi: A-B {c.loc['A_M15', 'B_H1']:.2f}, A-C {c.loc['A_M15', 'C_M30']:.2f}, "
          f"B-C {c.loc['B_H1', 'C_M30']:.2f}")
    for da in ("2026-02-01", "2026-06-01"):
        X = P[P.t >= da]
        print(f"  ingressi dal {da}: n = {len(X)}, R {X.R.sum():.1f} (long {X[X.d == 1].R.sum():.1f}, short {X[X.d == -1].R.sum():.1f}), "
              f"MDE {mde(X.R.std(), len(X)):.2f}")
    sd = P.R.std()
    print(f"  media {P.R.mean():.3f}, sd {sd:.3f}, Sharpe per trade {P.R.mean() / sd:.3f} | soglia di futilita': "
          + ", ".join(f"{N} -> {futility_sharpe(N, len(P), 1):.3f}" for N in (100, 1000, 11_520, VARIANTI_DICHIARATE)))
    print("  trade indipendenti per vedere un effetto (alfa 5%, potenza 80%):",
          {e: n_richiesto(sd, e) for e in (round(float(P.R.mean()), 3), round(float(P.R.mean()) / 2, 3), 0.10)},
          f"| MDE a 16 trade: {mde(sd, 16):.2f}, a 85 trade: {mde(sd, 85):.2f}")


def griglie(ris: str) -> None:
    print(f"\n== 6. GRIGLIE ({VARIANTI_DICHIARATE} varianti dichiarate)")
    totale = 0
    for tf, (piv, htf, age, dr, k, rr) in SCELTE.items():
        # 'None' nella colonna trail e' un valore, non un dato mancante
        G = pd.read_csv(os.path.join(ris, f"griglia_{tf}.csv"), keep_default_na=False, na_values=[""])
        totale += len(G)
        print(f"\n  {tf}: {len(G)} righe, trade mediani {G.n.median():.0f}")
        for nome, X in (("tutte", G), ("long", G[G.dir == "long"]), ("both", G[G.dir == "both"])):
            print(f"   {nome:5s}: positive nel 1o periodo {100 * (X.R_IS > 0).mean():.0f}%, nel 2o {100 * (X.R_OOS > 0).mean():.0f}%, in entrambi "
                  f"{100 * ((X.R_IS > 0) & (X.R_OOS > 0)).mean():.0f}% | PF mediano {X.PF.median():.2f}, R mediano {X.R.median():.1f}")
        chiave = [*PARAMETRI, "be", "trail", "part"]
        diff = (G[G.dir == "both"].set_index(chiave).R - G[G.dir == "long"].set_index(chiave).R).dropna()
        print(f"   aggiungere gli short (stessi parametri, {len(diff)} coppie): mediana {diff.median():.1f} R, peggiora nel {100 * (diff < 0).mean():.0f}% dei casi")
        print("   positive nel 1o periodo per stop:", {int(v): f"{100 * (X.R_IS > 0).mean():.0f}%" for v, X in G.groupby("k")},
              "| nel 2o:", {int(v): f"{100 * (X.R_OOS > 0).mean():.0f}%" for v, X in G.groupby("k")})
        V = G[G.n >= 100]
        alto = V.nlargest(max(1, len(V) // 100), "R_IS")
        print(f"   Spearman fra PF del 1o e del 2o periodo (n >= 100, {len(V)} righe): {V.PF_IS.corr(V.PF_OOS, method='spearman'):.2f} | "
              f"R del 2o periodo, mediana: migliore 1% del 1o periodo {alto.R_OOS.median():.1f}, tutte {V.R_OOS.median():.1f}")
        uscita = (G.dir == dr) & (G.be == 1.0) & (G.trail == "None") & G.part.isna()
        valori = dict(zip(PARAMETRI, (piv, htf, age, k, rr)))
        scelta = G[uscita & np.logical_and.reduce([G[p] == v for p, v in valori.items()])]
        assert len(scelta) == 1, f"riga scelta non trovata in {tf}"
        r = scelta.iloc[0]
        vicini = pd.concat([G[uscita & (G[p] != valori[p]) & np.logical_and.reduce([G[q] == v for q, v in valori.items() if q != p])]
                            for p in PARAMETRI])
        print(f"   SCELTA: n = {r.n}, PF {r.PF}, R {r.R} ({r.R_IS} + {r.R_OOS}) | posto su {len(G)}: per R {(G.R > r.R).sum() + 1}, per R del 1o periodo "
              f"{(G.R_IS > r.R_IS).sum() + 1}, del 2o {(G.R_OOS > r.R_OOS).sum() + 1} | {len(vicini)} vicini a un parametro: positivi "
              f"{int((vicini.R > 0).sum())}, R mediano {vicini.R.median():.1f}, minimo {vicini.R.min():.1f}")
    print(f"\n  righe totali nelle quattro griglie: {totale}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sorgente", default=SORGENTE, help="cartella con python/ del socio")
    ap.add_argument("--materiale", default=MATERIALE, help="cartella con data/ e risultati/ del socio")
    ap.add_argument("--hub", default=HUB, help="data hub con XAU_duka_M1_{bid,ask}.parquet (confronto dei prezzi)")
    a = ap.parse_args()
    pd.set_option("display.width", 220)
    # codice del socio, letto riga per riga l'11/10: si importa com'e', cambia solo dove cerca le barre
    sys.path.insert(0, os.path.join(a.sorgente, "python"))
    sys.dont_write_bytecode = True  # niente __pycache__ dentro la cartella delle sorgenti
    import strategie
    from vtob_bt import core
    strategie.DATA = os.path.join(a.materiale, "data")
    ris = os.path.join(a.materiale, "risultati")

    trade = riproducibilita(strategie, ris)
    m15 = strategie.dati("M15")
    cambio = dati_e_spread(m15)
    confronto_dukascopy(m15, a.hub)
    trade_per_strategia(strategie, core, trade, m15, cambio)
    portafoglio(ris)
    griglie(ris)


if __name__ == "__main__":
    main()
