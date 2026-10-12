"""Potenza per H1, momentum dell'ultima mezz'ora (backlog §H, passo 4). 0 trial.

Dai nostri dati prende SOLO grandezze che non dipendono dal segnale:
- la deviazione standard del rendimento dell'ultima mezz'ora (r_LH) per strumento;
- la correlazione fra strumenti di r_LH (per contare quanti strumenti indipendenti abbiamo);
- quante sedute utili ci sono in ogni pezzo della divisione dei dati.
NON calcola il rendimento della giornata (r_ROD) ne' nessuna media condizionata al segnale.

L'effetto atteso viene dalla fonte (Baltussen et al. 2021), sul numero pubblicato e sulla sua meta'
(09_fonti_di_vantaggio §4.7), con due metriche:
- SEGNO: lungo se r_ROD > 0, corto altrimenti, solo nell'ultima mezz'ora. Media per classe dalla Tab. 6
  (portafoglio 1/N per classe: si assume la stessa media sul singolo strumento).
- REGRESSIONE: r_LH su r_ROD. Correlazione = radice dell'R2 per mercato (Tab. B1, B3), in campione e fuori
  campione. Usa anche l'ampiezza del movimento, che e' dove il meccanismo mette l'effetto.

Formule (alfa 5% a due code, potenza 80%, fattore 2,80 come nel resto del repo):
- segno: n = (2,80 * sigma / mu)^2;   MDE = 2,80 * sigma / sqrt(n)
- regressione: n = (2,80 / atanh(rho))^2 + 3   (Fisher; ottimista con code grasse, vedi curtosi)

Uso: python analysis/ultima_mezzora/potenza.py
"""
from __future__ import annotations

import os
import sys

import exchange_calendars as xc
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from verifica_dati import ET, FEEDS, FUORI_CAMPIONE_FONTE, carica  # noqa: E402

Z = 2.80
SEDUTE_ANNO = 252
# Tab. 6 (strategia di solo segno su r_ROD, portafoglio 1/N per classe, 12/1974-05/2020): rendimento annuo %
MU_ANNUO_PCT = {"azioni": 6.86, "materie_prime": 4.34}
# Tab. B1 e B3, beta_ROD: R2 e R2 fuori campione in % per mercato (EU = pooled europeo, Tab. B1 Panel A)
R2_PCT = {"ES (S&P 500)": (3.41, 2.29), "NQ (Nasdaq 100)": (4.10, 3.76),
          "EU (pooled)": (2.36, 2.50), "GC (oro)": (0.25, 0.08)}


def rendimenti_ultima_mezzora(nome: str) -> pd.Series:
    """r_LH in punti base per seduta valida: apertura della barra a chiusura-30' -> chiusura dell'ultima barra."""
    f = next(x for x in FEEDS if x.nome == nome)
    df = carica(f).dropna(subset=["et"]).set_index("et").sort_index()
    inizio, fine = df.index.min().tz_convert(None).normalize(), df.index.max().tz_convert(None).normalize()
    sched = xc.get_calendar(f.calendario, start=inizio, end=fine).schedule
    # condizione 2 del referto: le festivita' USA si escludono anche per l'oro
    nyse = xc.get_calendar("XNYS", start=inizio, end=fine).schedule.index
    sched = sched[sched.index.isin(nyse)]
    passo = pd.Timedelta(minutes=f.passo_min)
    out = {}
    for giorno, r in sched.iterrows():
        if f.chiusura_fissa:
            hh, mm = map(int, f.chiusura_fissa.split(":"))
            chiusura = pd.Timestamp(giorno.year, giorno.month, giorno.day, hh, mm, tz=ET)
        else:
            chiusura = r["close"].tz_convert(ET)
        t0, t1 = chiusura - pd.Timedelta(minutes=30), chiusura - passo
        if t0 in df.index and t1 in df.index:
            out[giorno] = 1e4 * np.log(df.at[t1, "close"] / df.at[t0, "open"])
    return pd.Series(out, name=nome)


def n_segno(sigma: float, mu: float) -> float:
    return (Z * sigma / mu) ** 2


def n_regressione(rho: float) -> float:
    return (Z / np.arctanh(rho)) ** 2 + 3


def main() -> int:
    serie = {n: rendimenti_ultima_mezzora(n) for n in ("SPX500", "NAS100", "XAUUSD")}
    pulito = {n: s[s.index >= FUORI_CAMPIONE_FONTE] for n, s in serie.items()}

    print("=== Dati (solo da 06/2020: fuori dal campione della fonte)")
    stat = {}
    for n, s in pulito.items():
        sd = s.std()
        stat[n] = (len(s), sd)
        print(f"  {n}: sedute {len(s)} ({s.index.min().date()} -> {s.index.max().date()}) | "
              f"deviazione r_LH {sd:.1f} pb | curtosi in eccesso {s.kurt():.1f}")
    comune = pd.concat([pulito["SPX500"], pulito["NAS100"]], axis=1).dropna()
    rho_x = comune.corr().iloc[0, 1]
    n_eff_dev = len(comune) * 2 / (1 + rho_x)
    print(f"  correlazione r_LH SPX500-NAS100: {rho_x:.2f} -> i due indici valgono "
          f"{2 / (1 + rho_x):.2f} strumenti, cioe' ~{n_eff_dev:.0f} sedute indipendenti")

    print("\n=== Metrica SEGNO (Tab. 6): sedute necessarie e MDE con le sedute disponibili")
    righe = [("SPX500", "azioni", stat["SPX500"][0], stat["SPX500"][1]),
             ("NAS100", "azioni", stat["NAS100"][0], stat["NAS100"][1]),
             ("SPX500+NAS100", "azioni", n_eff_dev, (stat["SPX500"][1] + stat["NAS100"][1]) / 2),
             ("XAUUSD", "materie_prime", stat["XAUUSD"][0], stat["XAUUSD"][1])]
    for nome, classe, n_disp, sd in righe:
        mu = MU_ANNUO_PCT[classe] * 100 / SEDUTE_ANNO  # pb per seduta
        mde = Z * sd / np.sqrt(n_disp)
        print(f"  {nome}: effetto {mu:.2f} pb (meta' {mu / 2:.2f}) | servono {n_segno(sd, mu):.0f} sedute "
              f"({n_segno(sd, mu) / SEDUTE_ANNO:.1f} anni), a meta' {n_segno(sd, mu / 2):.0f} "
              f"({n_segno(sd, mu / 2) / SEDUTE_ANNO:.1f} anni) | disponibili {n_disp:.0f} -> MDE {mde:.2f} pb")

    print("\n=== Metrica REGRESSIONE (Tab. B1, B3): sedute necessarie per vedere la correlazione")
    for mercato, (r2_in, r2_oos) in R2_PCT.items():
        parti = []
        for etichetta, r2 in (("in campione", r2_in), ("fuori campione", r2_oos)):
            rho = np.sqrt(r2 / 100)
            parti.append(f"{etichetta}: rho {rho:.3f} -> {n_regressione(rho):.0f} sedute, "
                         f"a meta' {n_regressione(rho / 2):.0f}")
        print(f"  {mercato}: " + " | ".join(parti))
    print(f"  disponibili da 06/2020: SPX500 {stat['SPX500'][0]}, NAS100 {stat['NAS100'][0]} "
          f"(insieme ~{n_eff_dev:.0f} indipendenti), XAUUSD {stat['XAUUSD'][0]}; "
          f"un indice europeo scaricato da Dukascopy ne avrebbe circa quante SPX500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
