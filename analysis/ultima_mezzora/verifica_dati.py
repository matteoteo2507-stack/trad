"""Verifiche dei dati per H1, momentum dell'ultima mezz'ora (backlog §H, passo 3). 0 trial.

Per ogni file intraday in casa controlla, SENZA calcolare nessun rendimento:

1. integrita' meccanica con `core.data_checks` (monotonia, duplicati, barre per anno);
2. coerenza dei prezzi (niente prezzi <= 0; massimo >= apertura, chiusura >= minimo);
3. fuso orario: conversione dichiarata per fonte + controllo della pausa giornaliera dei futures USA
   (quante barre iniziano fra le 17:15 e le 17:45 ET, quando il mercato di riferimento e' fermo);
4. copertura della finestra, seduta per seduta, dal calendario di borsa (`exchange_calendars`):
   ci sono la barra della chiusura di ieri, quella d'inizio dell'ultima mezz'ora e quella della
   chiusura di oggi? Le chiusure anticipate spostano la finestra e si contano a parte; le barre
   ferme (massimo = minimo) nella finestra si contano perche' un feed fermo non e' un prezzo.

Definizione della finestra (Baltussen et al. 2021, Tab. 1): azioni USA 9:30-16:00 ET (ultima mezz'ora
15:30-16:00, oppure 12:30-13:00 nelle chiusure anticipate); oro COMEX 8:20-13:30 ET (13:00-13:30).

Fusi: Dukascopy = UTC; MT5 FP Markets = New York + 7 ore tutto l'anno (verificato il 09/10 in
docs/ULTIMA_MEZZORA_FATTIBILITA.md: NON Europe/Bucharest).

Uso: python analysis/ultima_mezzora/verifica_dati.py [NOME ...]   (senza nomi: tutti i feed)
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import exchange_calendars as xc
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from core.data_checks import barre_per_anno, duplicati, monotonia  # noqa: E402

DATI = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")
ET = "America/New_York"
PAUSA = (pd.Timedelta(hours=17, minutes=15), pd.Timedelta(hours=17, minutes=45))
FUORI_CAMPIONE_FONTE = pd.Timestamp("2020-06-01")  # il campione del paper finisce a maggio 2020


@dataclass
class Feed:
    """Un file intraday e le regole per leggerlo."""

    nome: str
    file: str
    fonte: str
    fuso: str  # "utc" | "ny_piu_7"
    passo_min: int
    calendario: str
    chiusura_fissa: str | None  # "13:30" per l'oro COMEX; None = chiusura del calendario
    visto_da_orb: bool
    fuso_borsa: str = ET  # per stampare gli orari attivi del feed nell'ora della borsa


FEEDS = [
    Feed("SPX500", "SPX500_M5.csv", "Dukascopy", "utc", 5, "XNYS", None, True),
    Feed("NAS100", "NAS100_M5.csv", "Dukascopy", "utc", 5, "XNYS", None, True),
    Feed("US500", "US500_M5.csv", "MT5 FP Markets", "ny_piu_7", 5, "XNYS", None, True),
    Feed("US100", "US100_M5.csv", "MT5 FP Markets", "ny_piu_7", 5, "XNYS", None, True),
    Feed("XAUUSD", "XAU_duka_M1_bid.parquet", "Dukascopy", "utc", 1, "COMEX", "13:30", False),
    # Indici europei per l'holdout (scarica_dukascopy.py). Tab. 1 del paper: DAX ed Euro Stoxx 50
    # 9:00-17:30 ora di Francoforte, FTSE 100 8:00-16:30 ora di Londra. Per l'Euro Stoxx si usa il
    # calendario di Francoforte (stessi orari; le festivita' possono differire di qualche giorno).
    Feed("DAX", "DAX_M5.csv", "Dukascopy", "utc", 5, "XETR", None, False, "Europe/Berlin"),
    Feed("EUSTX50", "EUSTX50_M5.csv", "Dukascopy", "utc", 5, "XETR", None, False, "Europe/Berlin"),
    Feed("FTSE100", "FTSE100_M5.csv", "Dukascopy", "utc", 5, "XLON", None, False, "Europe/London"),
]


def carica(f: Feed) -> pd.DataFrame:
    """Legge il file e aggiunge `et`, l'ora di New York della barra (inizio barra)."""
    percorso = os.path.join(DATI, f.file)
    if f.file.endswith(".parquet"):
        df = pd.read_parquet(percorso).reset_index()
        df = df.rename(columns={df.columns[0]: "time"})
    else:
        df = pd.read_csv(percorso, parse_dates=["time"])
    t = pd.DatetimeIndex(df["time"])
    if f.fuso == "utc":
        et = (t.tz_localize("UTC") if t.tz is None else t).tz_convert(ET)
    else:  # server = New York + 7 ore
        et = (t.tz_localize(None) - pd.Timedelta(hours=7)).tz_localize(
            ET, ambiguous="NaT", nonexistent="NaT")
    df["et"] = et
    return df


def coerenza_prezzi(df: pd.DataFrame) -> str:
    """Prezzi non positivi e barre con massimo/minimo incoerenti."""
    o, h, lo, c = df["open"], df["high"], df["low"], df["close"]
    nonpos = int(((o <= 0) | (h <= 0) | (lo <= 0) | (c <= 0)).sum())
    incoer = int(((h < np.maximum(o, c) - 1e-9) | (lo > np.minimum(o, c) + 1e-9)).sum())
    return f"prezzi <= 0: {nonpos} | barre con massimo/minimo incoerenti: {incoer}"


def pausa(df: pd.DataFrame) -> str:
    """Barre che iniziano nella pausa dei futures USA, contro quelle dell'ora 16-17 ET."""
    et = df["et"].dropna()
    ora = et - et.dt.normalize()
    feriali = et.dt.dayofweek < 5
    in_pausa = int(((ora >= PAUSA[0]) & (ora < PAUSA[1]) & feriali).sum())
    controllo = int(((ora >= pd.Timedelta(hours=16)) & (ora < pd.Timedelta(hours=17))
                     & feriali).sum())
    return (f"barre nella pausa 17:15-17:45 ET: {in_pausa} | nell'ora 16-17 ET: {controllo} "
            f"(rapporto {in_pausa / max(controllo, 1):.3f})")


def orario_attivo(df: pd.DataFrame, f: Feed) -> str:
    """Prima e ultima barra del giorno (mediana), nell'ora della borsa: la finestra ci sta dentro?"""
    loc = df["et"].dropna().dt.tz_convert(f.fuso_borsa)
    loc = loc[loc.dt.dayofweek < 5]
    minuti = loc.dt.hour * 60 + loc.dt.minute
    per_giorno = minuti.groupby(loc.dt.date).agg(["min", "max"]).median()
    hhmm = lambda m: f"{int(m) // 60:02d}:{int(m) % 60:02d}"  # noqa: E731
    return (f"barre attive (mediana, ora di {f.fuso_borsa}): dalle {hhmm(per_giorno['min'])} "
            f"alle {hhmm(per_giorno['max'])}")


def copertura(df: pd.DataFrame, f: Feed) -> pd.DataFrame:
    """Per ogni seduta: ci sono le tre barre che servono, e quante barre della finestra sono ferme?"""
    inizio, fine = df["et"].min(), df["et"].max()
    cal = xc.get_calendar(f.calendario, start=inizio.tz_convert(None).normalize(),
                          end=fine.tz_convert(None).normalize())
    sched = cal.schedule
    anticipate = set(cal.early_closes)
    barre = df.dropna(subset=["et"]).set_index("et").sort_index()
    indice = barre.index
    passo = pd.Timedelta(minutes=f.passo_min)
    righe = []
    chiusura_prec = None
    for giorno, r in sched.iterrows():
        chiusura_cal = r["close"].tz_convert(ET)
        if f.chiusura_fissa:
            hh, mm = map(int, f.chiusura_fissa.split(":"))
            chiusura = pd.Timestamp(giorno.year, giorno.month, giorno.day, hh, mm, tz=ET)
            anticipata = False
        else:
            chiusura = chiusura_cal
            anticipata = giorno in anticipate
        attese = {
            "inizio": chiusura - pd.Timedelta(minutes=30),
            "ultima": chiusura - passo,
            "prec": None if chiusura_prec is None else chiusura_prec - passo,
        }
        presenti = {k: (v is not None and v in indice) for k, v in attese.items()}
        # ricerca binaria sull'indice ordinato: una maschera per seduta su milioni di barre e' lenta
        finestra = barre.iloc[indice.searchsorted(attese["inizio"]):indice.searchsorted(chiusura)]
        attese_n = int(30 / f.passo_min)
        righe.append({
            "giorno": giorno, "anticipata": anticipata,
            "completa": all(presenti.values()),
            "manca_inizio": not presenti["inizio"], "manca_ultima": not presenti["ultima"],
            "manca_prec": not presenti["prec"],
            "barre_finestra": len(finestra), "attese": attese_n,
            "ferme": int((finestra["high"] == finestra["low"]).sum()),
        })
        chiusura_prec = chiusura
    return pd.DataFrame(righe)


def riassunto_copertura(cop: pd.DataFrame) -> list[str]:
    """Righe di testo: totale, dopo il campione della fonte, per anno, chiusure anticipate."""
    out = []
    for etichetta, sub in (("tutto", cop),
                           ("da 06/2020 (fuori dal campione della fonte)",
                            cop[cop["giorno"] >= FUORI_CAMPIONE_FONTE])):
        if sub.empty:
            continue
        out.append(
            f"  {etichetta}: sedute {len(sub)}, complete {sub['completa'].mean():.1%} | "
            f"mancano inizio {sub['manca_inizio'].sum()}, ultima {sub['manca_ultima'].sum()}, "
            f"chiusura di ieri {sub['manca_prec'].sum()} | barre ferme nella finestra "
            f"{sub['ferme'].sum() / max(sub['barre_finestra'].sum(), 1):.2%} | "
            f"finestre con meno barre dell'atteso {(sub['barre_finestra'] < sub['attese']).mean():.1%}")
    per_anno = cop.groupby(cop["giorno"].dt.year)["completa"].mean()
    out.append("  complete per anno: " + " ".join(f"{a}:{v:.0%}" for a, v in per_anno.items()))
    ant = cop[cop["anticipata"]]
    out.append(f"  chiusure anticipate nel calendario: {len(ant)}, complete {ant['completa'].mean():.0%}"
               if len(ant) else "  chiusure anticipate nel calendario: 0")
    return out


def main() -> int:
    scelti = set(sys.argv[1:])  # senza argomenti: tutti i feed
    for f in FEEDS:
        if scelti and f.nome not in scelti:
            continue
        if not os.path.exists(os.path.join(DATI, f.file)):
            print(f"\n=== {f.nome}: file {f.file} assente")
            continue
        df = carica(f)
        print(f"\n=== {f.nome}  ({f.fonte}, fuso {f.fuso}, M{f.passo_min}, "
              f"{'gia' + chr(39) + ' attraversato dall' + chr(39) + 'ORB' if f.visto_da_orb else 'mai usato dall' + chr(39) + 'ORB'})")
        print(f"  periodo: {df['et'].min()} -> {df['et'].max()} | righe {len(df)} | "
              f"ore non convertibili (cambio d'ora): {int(df['et'].isna().sum())}")
        for esito in (monotonia(df, nome=f.nome), duplicati(df, nome=f.nome),
                      barre_per_anno(df, nome=f.nome)):
            print("  " + str(esito).replace("\n", "\n  "))
        print("  " + coerenza_prezzi(df))
        print("  " + pausa(df))
        print("  " + orario_attivo(df, f))
        cop = copertura(df, f)
        for riga in riassunto_copertura(cop):
            print(riga)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
