"""Test pre-registrato della famiglia `momentum_ultima_mezzora` (backlog H1).

Pre-registrazione: docs/ULTIMA_MEZZORA_PREREGISTRATION.md. Sui dati REALI lo script parte solo se:
  - il frontmatter della pre-registrazione dice `stato: APPROVATA`;
  - pre-registrazione, codice e contatore sono committati e senza modifiche (l'hash finisce nell'esito);
  - il contatore ha registrato lo stadio (train: trial speso; holdout: data di apertura);
  - lo stadio non e' gia' stato eseguito (una ripresa richiede `--ripresa "motivo"`, §8);
  - per l'holdout: `--apri-holdout` e un esito del train committato che dice PASSA.
Con `--sintetico` gira su sedute seminate, senza toccare il mercato (controllo negativo e positivo).

    python analysis/ultima_mezzora/esegui_test.py --sintetico                  # nullo
    python analysis/ultima_mezzora/esegui_test.py --sintetico --forza 0.17     # effetto iniettato (correlazione)
    python analysis/ultima_mezzora/esegui_test.py --gruppo train               # IL test, primo stadio (una volta)
    python analysis/ultima_mezzora/esegui_test.py --gruppo holdout --apri-holdout   # secondo stadio (una volta)

Regola (§2 della pre-registrazione), per ogni seduta con chiusura C:
  r_ROD = ln(chiusura della barra che finisce a C-30' / chiusura dell'ultima barra della seduta precedente)
  sigma = deviazione standard di r_ROD sulle 60 sedute valide precedenti (nota prima)
  posizione proporzionale w = r_ROD / sigma, limitata a [-2, +2]; posizione a taglia fissa s = segno(r_ROD)
  entrata all'APERTURA della barra che inizia a C-30', uscita alla CHIUSURA dell'ultima barra prima di C
  r_LH = ln(uscita / entrata); rendimento netto = posizione * r_LH - costo * |posizione|
Confronto casuale (§5): stessa taglia ogni giorno, direzione presa da un altro giorno (spostamento circolare);
il divario si calcola su r_LH centrato, cosi' una deriva dell'ultima mezz'ora non entra nel confronto.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, QUI)
from core import data_checks as dc      # noqa: E402
from core import quant_metrics as qm    # noqa: E402
from core.sizing import confronta_overlay  # noqa: E402
from core.verifiche import pvalue_mc, ripeti_su_semi  # noqa: E402

FAMIGLIA = "momentum_ultima_mezzora"
PREREG = os.path.join(ROOT, "docs", "ULTIMA_MEZZORA_PREREGISTRATION.md")
CONTATORE = os.path.join(ROOT, "docs", "trial_ledger.json")
ESITI = os.path.join(ROOT, "docs", "reviews", "esiti")
CONGELATI = ["docs/ULTIMA_MEZZORA_PREREGISTRATION.md", "analysis/ultima_mezzora", "docs/trial_ledger.json"]
INIZIO = pd.Timestamp("2020-06-01")   # il campione della fonte finisce a maggio 2020
FINESTRA_SCALA, TETTO = 60, 2.0
N_SPOSTAMENTI, LAG_MIN = 1000, 20
N_BOOT, BLOCCO_MEDIO, SEME = 5000, 10, 42
K = 2.80                              # alfa 5% a due code, potenza 80%
Z_GUARDIA = 1.645                     # guardia a taglia fissa: positiva al 5% a una coda (strada B, Matteo 11/10)
# Costo andata e ritorno per unita' di posizione, in punti base. Misurati dai tick MT5 (demo FP Markets, 02-10/2026,
# docs/ULTIMA_MEZZORA_FATTIBILITA.md): mediane 0,34 (US500), 0,21 (US100), 0,20 (GER40), 0,96 (UK100), 2,58 (EURO50).
# Qui arrotondati in su, con margine per slittamento e conto demo.
COSTI_PB = {"SPX500": 0.5, "NAS100": 0.5, "DAX": 0.5, "FTSE100": 1.5, "EUSTX50": 3.0}
GRUPPI = {"train": {"primari": ["SPX500", "NAS100"], "descrittivi": []},
          "holdout": {"primari": ["DAX"], "descrittivi": ["EUSTX50", "FTSE100"]}}
# Correlazione fra r_ROD e r_LH pubblicata (Baltussen et al. 2021, Tab. B1: radice dell'R2 di beta_ROD).
RHO_FONTE = {"train": {"ES in campione": 0.185, "ES fuori campione": 0.151,
                       "NQ in campione": 0.202, "NQ fuori campione": 0.194},
             "holdout": {"EU in campione": 0.154, "EU fuori campione": 0.158}}
RHO_RIF = {"train": (0.151 + 0.194) / 2, "holdout": 0.158}   # riferimento: fuori campione
# Numeri gia' noti dal referto del 09/10 (potenza.py): deviazione di r_LH in pb e sedute da 06/2020 con la finestra
# completa. Il test li riproduce PRIMA di ogni numero che dipende dal segnale: se non tornano, la lettura delle barre
# e' cambiata e non si da' un verdetto.
RIFERIMENTO = {"SPX500": (26.4, 1538), "NAS100": (30.7, 1538)}
# Distorsione del divario sotto il nullo, misurata da calibra_nullo.py PRIMA del test (§9 della pre-registrazione).
B_NULL = 0.2


# ---------------------------------------------------------------------------------------------------------------
# Sedute: dai dati reali o sintetiche
# ---------------------------------------------------------------------------------------------------------------
def sedute_da_barre(barre: pd.DataFrame, chiusure: pd.Series, passo_min: int) -> pd.DataFrame:
    """Da barre intraday a una riga per seduta. Funzione pura, coperta da tests/test_ultima_mezzora.py.

    Args:
        barre: indice = inizio barra con fuso (qualunque), colonne `open` e `close`, ordinate.
        chiusure: per ogni seduta (indice = giorno), l'istante di chiusura con fuso.
        passo_min: durata della barra in minuti.

    Returns:
        Per seduta: `finestra_ok` (ci sono entrata e uscita), `valida` (ci sono anche segnale e chiusura
        precedente), `r_lh` e `r_rod` in punti base, `scarto` fra chiusura del segnale e apertura dell'entrata.
    """
    passo, mezzora = pd.Timedelta(minutes=passo_min), pd.Timedelta(minutes=30)
    idx = barre.index
    righe, prec = [], None
    for giorno, c in chiusure.items():
        c = c.tz_convert(idx.tz)
        t_seg, t_in, t_out = c - mezzora - passo, c - mezzora, c - passo
        t_prec = None if prec is None else prec - passo
        finestra = t_in in idx and t_out in idx
        valida = finestra and t_seg in idx and t_prec is not None and t_prec in idx
        riga = {"giorno": giorno, "finestra_ok": finestra, "valida": valida}
        if finestra:
            riga["r_lh"] = 1e4 * np.log(barre.at[t_out, "close"] / barre.at[t_in, "open"])
        if valida:
            riga["r_rod"] = 1e4 * np.log(barre.at[t_seg, "close"] / barre.at[t_prec, "close"])
            riga["scarto"] = 1e4 * np.log(barre.at[t_in, "open"] / barre.at[t_seg, "close"])
        righe.append(riga)
        prec = c
    return pd.DataFrame(righe).set_index("giorno")


def sedute_reali(nome: str) -> tuple[pd.DataFrame, dict]:
    """Legge il file del feed e restituisce le sedute, piu' il grezzo e il percorso per i controlli."""
    import exchange_calendars as xc
    from verifica_dati import DATI, FEEDS, carica

    f = next(x for x in FEEDS if x.nome == nome)
    grezzo = carica(f)
    barre = grezzo.dropna(subset=["et"]).set_index("et").sort_index()
    da, a = barre.index.min().tz_convert(None).normalize(), barre.index.max().tz_convert(None).normalize()
    sched = xc.get_calendar(f.calendario, start=da, end=a).schedule
    sed = sedute_da_barre(barre, sched["close"], f.passo_min)
    return sed, {"grezzo": grezzo, "percorso": os.path.join(DATI, f.file)}


def sedute_sintetiche(seme: int, forza: float, n: int, nomi: list[str], vol_sd: float = 0.18,
                      deriva_lh: float = 0.2, deriva_rod: float = 5.0, a_giu: float = 1.0, a_su: float = 1.0,
                      spinta: float = 0.0, p_resta: float | None = None, vol_legata: float = 0.0,
                      solo_taglia: float = 0.0) -> dict:
    """Sedute seminate: volatilita' a grappoli comune, code grasse, strumenti correlati a 0,96, piccola deriva.

    `forza` = correlazione vera fra r_ROD e r_LH dello stesso giorno (0 = nullo). Gli altri parametri costruiscono
    i nulli "cattivi" della revisione G1: asimmetria fra giorni di rialzo e di ribasso (`a_giu`, `a_su`, `spinta`),
    segni autocorrelati (`p_resta`), volatilita' dell'ultima mezz'ora che cresce col movimento del giorno
    (`vol_legata`), effetto che vive solo nella taglia (`solo_taglia`: momentum nei giorni grandi, inversione nei
    piccoli, solo segno nullo in attesa).
    """
    rng = np.random.default_rng(seme)
    m = n + FINESTRA_SCALA + 40
    logv = np.zeros(m)
    for i in range(1, m):                       # log-volatilita' AR(1): grappoli come sui dati veri
        logv[i] = 0.97 * logv[i - 1] + vol_sd * rng.standard_normal()
    v = np.exp(logv - logv.var() / 2)
    giorni = pd.bdate_range("2020-02-01", periods=m)
    t5 = lambda: rng.standard_t(5, m) / np.sqrt(5 / 3)   # noqa: E731 - varianza 1
    com_rod, com_lh, out = t5(), t5(), {}
    if p_resta is not None:                     # catena di Markov sui segni del fattore comune
        resta = rng.random(m) < p_resta
        seg = np.ones(m)
        for i in range(1, m):
            seg[i] = seg[i - 1] if resta[i] else -seg[i - 1]
        com_rod = np.abs(com_rod) * seg
    for nome in nomi:
        z = np.sqrt(0.96) * com_rod + np.sqrt(0.04) * t5()
        e = np.sqrt(0.96) * com_lh + np.sqrt(0.04) * t5()
        z = np.where(z < 0, a_giu * z, a_su * z) + spinta
        r_rod = v * 100.0 * z + deriva_rod                                 # ~100 pb di deviazione
        scala = (0.35 + 0.90 * np.abs(com_rod)) / 1.03 if vol_legata else 1.0
        if solo_taglia:
            media = solo_taglia * np.sign(z) * (np.abs(z) - 0.7394)        # 0,7394 = E|z| del fattore composito
            r_lh = v * 28.0 * (media + e) + deriva_lh
        else:
            r_lh = v * 28.0 * scala * (forza * z + np.sqrt(1 - forza ** 2) * e) + deriva_lh
        out[nome] = pd.DataFrame({"r_rod": r_rod, "r_lh": r_lh}, index=giorni)
    return out


def prepara(sed: pd.DataFrame) -> pd.DataFrame:
    """Aggiunge scala, posizione proporzionale e segno; tiene le sedute da INIZIO con la scala disponibile."""
    d = sed.sort_index().copy()
    d["sigma"] = d["r_rod"].rolling(FINESTRA_SCALA, min_periods=FINESTRA_SCALA).std().shift(1)
    d["z"] = d["r_rod"] / d["sigma"]
    d["w"] = d["z"].clip(-TETTO, TETTO)
    d["s"] = np.sign(d["r_rod"])
    d["sigma_lh"] = d["r_lh"].rolling(FINESTRA_SCALA, min_periods=FINESTRA_SCALA).std().shift(1)
    return d[(d.index >= INIZIO) & d["sigma"].notna() & d["sigma_lh"].notna()]


# ---------------------------------------------------------------------------------------------------------------
# Bracci e statistiche
# ---------------------------------------------------------------------------------------------------------------
def allinea(dati: dict, nomi: list[str]) -> dict:
    """Matrici giorno x strumento (NaN dove lo strumento non ha la seduta)."""
    giorni = sorted(set().union(*[set(dati[n].index) for n in nomi]))
    idx = pd.DatetimeIndex(giorni)
    return {c: np.column_stack([dati[n][c].reindex(idx).to_numpy(float) for n in nomi])
            for c in ("w", "s", "z", "r_lh", "r_rod", "sigma_lh")} | {"giorni": idx, "nomi": nomi}


def netto(pos: np.ndarray, r_lh: np.ndarray, costi: np.ndarray, mult: float = 1.0) -> np.ndarray:
    """Rendimento netto per giorno e strumento, in punti base."""
    return pos * r_lh - mult * costi * np.abs(pos)


def portafoglio(x: np.ndarray) -> np.ndarray:
    """Media fra gli strumenti disponibili quel giorno (1/N)."""
    return np.nanmean(x, axis=1)


def braccio_casuale(taglia: np.ndarray, segni: np.ndarray, r_c: np.ndarray, rng: np.random.Generator,
                    n_spost: int) -> tuple[np.ndarray, np.ndarray]:
    """Stessa taglia ogni giorno, direzione presa da un altro giorno: spostamento circolare dei segni.

    Lo stesso spostamento vale per tutti gli strumenti (conserva la dipendenza fra loro). Restituisce la posizione
    media dei controlli per giorno e strumento, e la media di ogni spostamento su r_LH centrato (distribuzione nulla).
    """
    n = taglia.shape[0]
    somma, medie = np.zeros_like(taglia), np.empty(n_spost)
    for k in range(n_spost):
        pos = taglia * np.roll(segni, int(rng.integers(LAG_MIN, n - LAG_MIN)), axis=0)
        somma += np.nan_to_num(pos)
        medie[k] = np.nanmean(portafoglio(pos * r_c))
    media_pos = somma / n_spost
    media_pos[~np.isfinite(taglia)] = np.nan
    return media_pos, medie


def _indici_bootstrap(n: int, rng: np.random.Generator) -> np.ndarray:
    """Bootstrap stazionario (Politis-Romano) a blocchi di lunghezza media BLOCCO_MEDIO, vettoriale."""
    nuovo = rng.random(n) < 1.0 / BLOCCO_MEDIO
    nuovo[0] = True
    inizi = rng.integers(0, n, n)[nuovo]
    gruppo = np.cumsum(nuovo) - 1
    primo = np.flatnonzero(nuovo)[gruppo]
    return (inizi[gruppo] + np.arange(n) - primo) % n


def ic_blocchi(x: np.ndarray, n_boot: int, seme: int = SEME) -> dict:
    """Media con intervallo percentile al 95% da bootstrap a blocchi sui giorni, errore standard e MDE."""
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seme)
    medie = np.array([x[_indici_bootstrap(len(x), rng)].mean() for _ in range(n_boot)])
    es = float(medie.std(ddof=1))
    return {"media": float(x.mean()), "low": float(np.percentile(medie, 2.5)),
            "high": float(np.percentile(medie, 97.5)), "es": es, "mde": K * es, "n": int(len(x))}


def analizza(M: dict, costi: np.ndarray, n_spost: int = N_SPOSTAMENTI, n_boot: int = N_BOOT,
             seme: int = SEME) -> dict:
    """Tutte le statistiche che entrano nel verdetto, per un gruppo di strumenti primari."""
    rng = np.random.default_rng(seme)
    w, s, r = M["w"], M["s"], M["r_lh"]
    r_c = r - np.nanmean(r, axis=0)          # centrato per strumento: la deriva non entra nel divario
    g_prop = portafoglio(netto(w, r, costi))
    g_fisso = portafoglio(netto(s, r, costi))
    cas_prop, nulle = braccio_casuale(np.abs(w), s, r_c, rng, n_spost)
    cas_fisso, _ = braccio_casuale(np.abs(s), s, r_c, rng, n_spost)
    d_prop = (w - cas_prop) * r_c            # i due bracci pagano gli stessi costi: il divario e' lordo
    d_fisso = (s - cas_fisso) * r_c
    reale_c = float(np.nanmean(portafoglio(w * r_c)))
    scala = float(np.nanmean(np.abs(w)))
    return {
        "divario": ic_blocchi(portafoglio(d_prop), n_boot, seme),
        "netto": ic_blocchi(g_prop, n_boot, seme),
        "netto_3x": float(np.nanmean(portafoglio(netto(w, r, costi, 3.0)))),
        "divario_fisso": ic_blocchi(portafoglio(d_fisso), n_boot, seme),
        "netto_fisso": ic_blocchi(g_fisso, n_boot, seme),
        # ablazione appaiata della taglia (§4bis): proporzionale meno solo segno a pari taglia media, lordo
        "ablazione": ic_blocchi(portafoglio(w * r) - portafoglio(scala * s * r), n_boot, seme),
        "p": pvalue_mc(int(np.sum(nulle >= reale_c)), n_spost),
        # effetto atteso per unita' di correlazione (bloccante 1 della G1): media di |w| x |z| x deviazione mobile
        # dell'ultima mezz'ora, per strumento e poi 1/N. Solo grandezze note prima dell'esito.
        "atteso_per_rho": float(np.mean(np.nanmean(np.abs(w) * np.abs(M["z"]) * M["sigma_lh"], axis=0))),
        "g_prop": g_prop, "g_fisso": g_fisso, "d_prop": portafoglio(d_prop), "taglia_media": scala,
        "esposizione": (float(np.nanmean(w)), float(np.nanmean(cas_prop)), float(np.nanmean(r))),
        "per_strumento": {nome: {"divario": float(np.nanmean(d_prop[:, j])),
                                 "netto": float(np.nanmean(netto(w, r, costi)[:, j])),
                                 "sedute": int(np.isfinite(d_prop[:, j]).sum())}
                          for j, nome in enumerate(M["nomi"])},
    }


def verdetto(A: dict, gruppo: str) -> tuple[str, float, float]:
    """Etichetta secondo il §6 della pre-registrazione (PASSA/LEAD ha la precedenza su CLOSED)."""
    atteso = RHO_RIF[gruppo] * A["atteso_per_rho"]
    meta = atteso / 2
    fisso = A["divario_fisso"]
    passa = (A["divario"]["low"] > B_NULL and A["netto"]["low"] > 0 and A["netto_3x"] > 0
             and all(v["divario"] > 0 for v in A["per_strumento"].values())
             and fisso["media"] > Z_GUARDIA * fisso["es"])
    if passa:
        return ("PASSA" if gruppo == "train" else "LEAD"), atteso, meta
    if A["divario"]["high"] < meta:
        return "CLOSED", atteso, meta
    return "NON DIMOSTRATO", atteso, meta


# ---------------------------------------------------------------------------------------------------------------
# Stampa
# ---------------------------------------------------------------------------------------------------------------
def _ic(d: dict) -> str:
    return f"{d['media']:+.2f} [{d['low']:+.2f}; {d['high']:+.2f}] pb (n {d['n']}, MDE {d['mde']:.2f})"


def stampa(A: dict, M: dict, gruppo: str, etichetta: str, atteso: float, meta: float, costi: np.ndarray,
           semi: dict | None) -> None:
    esp_r, esp_c, media_r = A["esposizione"]
    print(f"\n--- Confronto casuale: taglia identica per giorno nei due bracci (media {A['taglia_media']:.2f}); "
          f"esposizione netta media reale {esp_r:+.3f}, casuale {esp_c:+.3f}; media dell'ultima mezz'ora "
          f"{media_r:+.2f} pb (tolta dal divario: r_LH centrato)")
    print(f"effetto atteso dalla fonte: {atteso:.2f} pb (rho {RHO_RIF[gruppo]:.3f} x media di |w| x |z| x deviazione "
          f"mobile dell'ultima mezz'ora = {A['atteso_per_rho']:.1f}), meta' {meta:.2f} pb")
    print("\n=== PRIMARIA: posizione proporzionale con tetto")
    print(f"divario dal casuale (direzione): {_ic(A['divario'])}   soglia B_NULL {B_NULL:+.2f}")
    print(f"attesa netta per seduta:         {_ic(A['netto'])}")
    print(f"attesa netta con costi 3x:       {A['netto_3x']:+.2f} pb")
    p = A["p"]
    print(f"p dagli spostamenti circolari:   {p['p']:.4f} [{p['low']:.4f}; {p['high']:.4f}] su {p['repliche']} (non decide)")
    for nome, v in A["per_strumento"].items():
        print(f"  {nome}: divario {v['divario']:+.2f} pb, netto {v['netto']:+.2f} pb, sedute {v['sedute']}")
    f = A["divario_fisso"]
    print("\n=== GUARDIA A TAGLIA FISSA (binario 1R): solo segno")
    print(f"divario dal casuale: {_ic(f)}   rapporto con l'errore standard {f['media'] / f['es']:+.2f} "
          f"(soglia {Z_GUARDIA}: {'superata' if f['media'] > Z_GUARDIA * f['es'] else 'NON superata'})")
    print(f"attesa netta:        {_ic(A['netto_fisso'])}")
    print("\n=== TABELLA DI ESCLUSIONE (divario contro rho pubblicata x media di |w| x |z| x deviazione mobile)")
    for fonte, rho in RHO_FONTE[gruppo].items():
        for quota, nome_q in ((1.0, "pieno"), (0.5, "meta'")):
            x = rho * quota * A["atteso_per_rho"]
            stato = ("ESCLUSO" if A["divario"]["high"] < x else
                     "superato" if A["divario"]["low"] > x else "non escluso")
            print(f"  {fonte} ({nome_q}, {x:.2f} pb): {stato}")
    print(f"\n*** VERDETTO {gruppo.upper()}: {etichetta} ***")

    print("\n--- DESCRITTIVI (non decidono)")
    if semi is not None:
        print(f"limite basso del divario su {semi['n_semi']} semi (bootstrap e spostamenti): da {semi['min']:+.2f} a "
              f"{semi['max']:+.2f} pb (seme dichiarato {SEME}: {A['divario']['low']:+.2f})")
    giorni = M["giorni"]
    anni = pd.DataFrame({"netto": A["g_prop"], "divario": A["d_prop"]}, index=giorni).groupby(giorni.year)
    tab = anni.agg(["mean", "count"])
    print("per anno (divario medio pb | netto medio pb | sedute): " + " ; ".join(
        f"{a}: {r[('divario', 'mean')]:+.2f} | {r[('netto', 'mean')]:+.2f} | {int(r[('netto', 'count')])}"
        for a, r in tab.iterrows()))
    print(f"anni con divario positivo: {(tab[('divario', 'mean')] > 0).sum()} su {len(tab)}")
    g = A["g_prop"][np.isfinite(A["g_prop"])]
    sr = g.mean() / g.std(ddof=1)
    psr = qm.probabilistic_sharpe_ratio(sr, 0.0, len(g), float(pd.Series(g).skew()), float(pd.Series(g).kurt()))
    print(f"Sharpe per seduta {sr:+.3f} (annuo {sr * np.sqrt(252):+.2f}), PSR {psr:.3f} (1 trial: DSR = PSR), "
          f"pavimento di futilita' {1.65 / np.sqrt(len(g)):.3f}")
    print(f"proporzionale senza tetto, netto: {np.nanmean(portafoglio(netto(M['z'], M['r_lh'], costi))):+.2f} pb")
    print(f"ablazione della taglia (lordo, proporzionale meno solo segno a pari taglia media "
          f"{A['taglia_media']:.2f}): {_ic(A['ablazione'])}")
    # meccanismo: per terzile di |z| (solo segno, lordo) e inversione il giorno dopo
    ass, resa = np.abs(M["z"]).ravel(), (M["s"] * M["r_lh"]).ravel()
    ok = np.isfinite(ass) & np.isfinite(resa)
    q = np.quantile(ass[ok], [1 / 3, 2 / 3])
    for nome_t, sel in (("piccolo", ass <= q[0]), ("medio", (ass > q[0]) & (ass <= q[1])), ("grande", ass > q[1])):
        m = ok & sel
        print(f"  giorni con movimento {nome_t}: solo segno lordo {resa[m].mean():+.2f} pb (n {int(m.sum())})")
    dopo = portafoglio(M["w"][:-1] * M["r_rod"][1:])
    print(f"inversione il giorno dopo (posizione di oggi x r_ROD di domani, lordo): {np.nanmean(dopo):+.2f} pb "
          f"(il meccanismo di copertura la vuole negativa)")
    # doppio binario (STRATEGY_LIFECYCLE §4quater): overlay sulla sequenza a taglia fissa, in unita' di rischio
    r_unita = A["g_fisso"] / np.nanmean(M["sigma_lh"], axis=1)
    tab_o, runs = confronta_overlay(r_unita[np.isfinite(r_unita)])
    tab_o.loc[tab_o["binario"] == "1R", "lettura"] = "binario 1R: qui e' la guardia, non il verdetto (§6)"
    print("doppio binario sulla taglia fissa (unita' = deviazione mobile dell'ultima mezz'ora, 60 sedute):")
    print(tab_o[["binario", "e_per_unita", "e_lo", "e_hi", "valore_dipendenza", "percentile_reale",
                 "lettura"]].to_string(index=False))
    print(f"runs test sugli esiti a taglia fissa: {runs}")


# ---------------------------------------------------------------------------------------------------------------
# Guardie per i dati reali (una sola esecuzione per stadio, codice congelato)
# ---------------------------------------------------------------------------------------------------------------
def stato_prereg() -> str:
    """Legge `stato:` dal frontmatter della pre-registrazione."""
    if not os.path.exists(PREREG):
        return "ASSENTE"
    with open(PREREG, encoding="utf-8") as fh:
        for riga in fh:
            if riga.startswith("stato:"):
                return riga.split(":", 1)[1].strip().strip('"').upper()
    return "SENZA STATO"


class GitNonRisponde(RuntimeError):
    """git ha restituito un errore: le guardie non possono dire che il codice e' congelato."""


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise GitNonRisponde(f"git {' '.join(args)}: {r.stderr.strip() or 'codice ' + str(r.returncode)}")
    return r.stdout.strip()


def guardie_reali(gruppo: str, apri_holdout: bool, ripresa: str | None) -> tuple[str | None, str]:
    """Restituisce (motivo del rifiuto oppure None, hash del commit). Se git non risponde, rifiuta."""
    try:
        return _guardie(gruppo, apri_holdout, ripresa)
    except GitNonRisponde as ex:
        return f"git non risponde, quindi non si puo' verificare che il codice sia congelato: {ex}", ""


def _guardie(gruppo: str, apri_holdout: bool, ripresa: str | None) -> tuple[str | None, str]:
    stato = stato_prereg()
    if stato != "APPROVATA":
        return f"La pre-registrazione e' in stato '{stato}': il test sui dati reali parte solo se APPROVATA.", ""
    sporchi = _git("status", "--porcelain", "--", *CONGELATI)
    if sporchi:
        return "Pre-registrazione, codice o contatore non sono committati o hanno modifiche:\n" + sporchi, ""
    with open(CONTATORE, encoding="utf-8") as fh:
        fam = next((f for f in json.load(fh)["famiglie"] if f.get("id") == FAMIGLIA), None)
    if fam is None:
        return f"La famiglia {FAMIGLIA} non e' nel contatore.", ""
    esito = os.path.join(ESITI, f"ultima_mezzora_{gruppo}.txt")
    if os.path.exists(esito):
        vecchio = open(esito, encoding="utf-8").read()
        if "*** VERDETTO" in vecchio:
            return f"Lo stadio {gruppo} ha gia' un verdetto ({esito}): non si riesegue.", ""
        if "RIPRESA:" in vecchio:
            return f"Lo stadio {gruppo} e' gia' stato ripreso una volta ({esito}): non si rilancia ancora.", ""
        if not ripresa:
            return (f"Lo stadio {gruppo} e' gia' stato lanciato senza arrivare a un verdetto ({esito}). Una ripresa "
                    f"per difetto di esecuzione richiede --ripresa \"motivo\" e una voce in DECISIONS (§8)."), ""
    if gruppo == "train" and fam.get("trial_cumulati") != 1:
        return "Prima del train il contatore deve registrare il trial speso (trial_cumulati = 1) ed essere committato.", ""
    if gruppo == "holdout":
        rel = "docs/reviews/esiti/ultima_mezzora_train.txt"
        tr = os.path.join(ROOT, rel)
        passato = os.path.exists(tr) and "*** VERDETTO TRAIN: PASSA ***" in open(tr, encoding="utf-8").read()
        tracciato = bool(_git("ls-files", "--", rel)) and not _git("status", "--porcelain", "--", rel)
        if not (apri_holdout and passato and tracciato):
            return ("L'holdout si apre solo con --apri-holdout e dopo un train con verdetto PASSA il cui esito e' "
                    "committato senza modifiche."), ""
        riga = next((x for x in open(tr, encoding="utf-8").read().splitlines() if "sul commit " in x), "")
        commit_train = riga.split("sul commit ")[-1].split()[0] if riga else ""
        if not commit_train or _git("diff", "--name-only", commit_train, "HEAD", "--", "analysis/ultima_mezzora"):
            return "Il codice di analysis/ultima_mezzora e' cambiato dal commit del train: l'holdout non parte.", ""
        if not fam.get("holdout_aperto"):
            return "Prima dell'holdout il contatore deve registrare la data di apertura ed essere committato.", ""
    commit = _git("rev-parse", "HEAD")
    if not commit:
        return "git non restituisce l'hash del commit.", ""
    return None, commit


def impronta(percorso: str) -> str:
    """Prime 16 cifre dello SHA-256 del file dati: l'esito dice su quali dati e' stato calcolato."""
    h = hashlib.sha256()
    with open(percorso, "rb") as fh:
        for pezzo in iter(lambda: fh.read(1 << 20), b""):
            h.update(pezzo)
    return h.hexdigest()[:16]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sintetico", action="store_true")
    ap.add_argument("--forza", type=float, default=0.0, help="correlazione iniettata fra r_ROD e r_LH")
    ap.add_argument("--seme", type=int, default=7)
    ap.add_argument("--n", type=int, default=1540, help="sedute sintetiche")
    ap.add_argument("--gruppo", choices=["train", "holdout"], default="train")
    ap.add_argument("--apri-holdout", action="store_true")
    ap.add_argument("--ripresa", default=None, help="motivo di una seconda esecuzione per difetto (§8)")
    args = ap.parse_args(argv)
    primari = GRUPPI[args.gruppo]["primari"]
    descrittivi = GRUPPI[args.gruppo]["descrittivi"]
    testa = []

    if args.sintetico:
        grezzi = sedute_sintetiche(args.seme, args.forza, args.n, primari + descrittivi)
        testa.append(f"SINTETICO seme {args.seme}, correlazione iniettata {args.forza}, gruppo {args.gruppo}")
    else:
        rifiuto, commit = guardie_reali(args.gruppo, args.apri_holdout, args.ripresa)
        if rifiuto:
            print(rifiuto)
            return 2
        testa.append(f"Eseguito il {dt.date.today()} sul commit {commit}"
                     + (f" | RIPRESA: {args.ripresa}" if args.ripresa else ""))
        # segnaposto scritto PRIMA di leggere i dati: da qui in poi ogni altro lancio chiede --ripresa (§8)
        os.makedirs(ESITI, exist_ok=True)
        file_esito = os.path.join(ESITI, f"ultima_mezzora_{args.gruppo}.txt")
        with open(file_esito, "w", encoding="utf-8") as fh:
            print(testa[0], file=fh)
            print("IN CORSO: lo script ha iniziato a leggere i dati e non ha ancora un esito.", file=fh)
        grezzi, frames, file_usati, rotto = {}, {}, {}, False
        escluse = sedute_tot = 0
        for nome in primari + descrittivi:
            sed, info = sedute_reali(nome)
            frames[nome], file_usati[nome] = info["grezzo"], info["percorso"]
            dal = sed[sed.index >= INIZIO]
            lh = dal.loc[dal["finestra_ok"], "r_lh"]
            riga = (f"{nome}: impronta {impronta(info['percorso'])} | sedute dal {INIZIO.date()} {len(dal)}, "
                    f"finestra completa {len(lh)}, escluse per barre mancanti {int((~dal['valida']).sum())} | "
                    f"deviazione di r_LH {lh.std():.1f} pb")
            if nome in RIFERIMENTO:               # riproduzione dei numeri gia' noti, prima di tutto il resto
                sd_rif, n_rif = RIFERIMENTO[nome]
                torna = abs(lh.std() - sd_rif) <= 0.1 and abs(len(lh) - n_rif) <= 2
                riga += f" (referto 09/10: {sd_rif} pb, {n_rif} sedute -> {'torna' if torna else 'NON TORNA'})"
                rotto |= not torna
            if nome in primari:
                escluse, sedute_tot = escluse + int((~dal["valida"]).sum()), sedute_tot + len(dal)
            v = dal[dal["valida"]]
            riga += (f" | fill non ottenibili: 0 su {len(v)} per costruzione (ordine a mercato alla prima barra dopo "
                     f"il segnale); scarto fra chiusura del segnale e apertura dell'entrata: mediana "
                     f"{v['scarto'].abs().median():.2f} pb, massimo {v['scarto'].abs().max():.1f} pb")
            testa.append(riga)
            grezzi[nome] = sed[sed["valida"]][["r_rod", "r_lh"]]
        controlli = dc.checklist_dati(frames, file_usati=file_usati)
        testa.append(str(controlli))
        rotto |= not controlli.ok
        if rotto or escluse > 0.05 * max(sedute_tot, 1):
            # si esce PRIMA di calcolare un solo numero che dipende dal segnale
            print("\n".join(testa))
            nessuno = ("*** NESSUN VERDETTO: controlli dati rotti, numeri noti non riprodotti o piu' del 5% di "
                       "sedute escluse ***")
            print(nessuno)
            with open(file_esito, "w", encoding="utf-8") as fh:   # "NESSUN VERDETTO" non contiene "*** VERDETTO"
                for riga_t in testa + [nessuno]:
                    print(riga_t, file=fh)
            return 3

    dati = {n: prepara(d) for n, d in grezzi.items()}
    M = allinea(dati, primari)
    costi = np.array([COSTI_PB[n] for n in primari])
    A = analizza(M, costi)
    etichetta, atteso, meta = verdetto(A, args.gruppo)
    semi = None if args.sintetico else ripeti_su_semi(lambda sm: analizza(M, costi, seme=sm)["divario"]["low"])
    buf = io.StringIO()
    vecchio, sys.stdout = sys.stdout, buf
    try:
        print("\n".join(testa))
        print(f"Famiglia {FAMIGLIA}, gruppo {args.gruppo}, strumenti primari {primari}, "
              f"sedute {len(M['giorni'])} ({M['giorni'].min().date()} -> {M['giorni'].max().date()})")
        stampa(A, M, args.gruppo, etichetta, atteso, meta, costi, semi)
        for nome in descrittivi:                     # repliche descrittive: non entrano nel verdetto
            Ad = analizza(allinea(dati, [nome]), np.array([COSTI_PB[nome]]))
            print(f"\nreplica descrittiva {nome}: divario {_ic(Ad['divario'])}; netto {_ic(Ad['netto'])} "
                  f"(costo {COSTI_PB[nome]} pb)")
    finally:
        sys.stdout = vecchio
    testo = buf.getvalue()
    print(testo)
    if not args.sintetico:
        with open(file_esito, "w", encoding="utf-8") as fh:
            fh.write(testo)
        print(f"Output salvato in {os.path.relpath(file_esito, ROOT)}: va committato prima di ogni altro passo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
