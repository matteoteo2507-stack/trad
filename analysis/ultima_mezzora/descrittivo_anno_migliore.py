"""DESCRITTIVO A POSTERIORI: non decide, non e' un trial, non riapre nulla.

Famiglia `momentum_ultima_mezzora`, CLOSED al train il 12/10/2026 (docs/reviews/esiti/ultima_mezzora_train.txt,
DECISIONS 2026-10-12 (2)). Scritto per la revisione G2 dopo il verdetto
(docs/reviews/ultima_mezzora_G2_2026-10-12.md). Il verdetto resta quello dell'esito: qui non si calcola nessuna
etichetta, non si scrive in docs/reviews/esiti/ e non si tocca l'holdout.

Domanda. Nell'esito il 2022 e' l'unico anno con un divario grande e positivo (+4,89 pb; 2 anni positivi su 7).
Guardare sette anni e commentare il migliore e' una selezione. Quanto spesso il caso, da solo, produce un anno
migliore cosi'?

Nullo: quello del test (§5 della pre-registrazione). La taglia |w| di ogni giorno resta al suo posto, la direzione
viene da un altro giorno: spostamento circolare dei segni, lo stesso per i due strumenti, di almeno 20 sedute. Qui
si usano TUTTI gli spostamenti ammessi (da 20 a n-21), non un campione: non c'e' errore Monte Carlo. Volatilita'
e taglia di ogni anno restano dove sono, quindi sotto il nullo il 2022 resta l'anno turbolento che era.

Due statistiche, calcolate allo stesso modo sul reale e su ogni spostamento:
  - anno migliore in punti base: il massimo fra i sette divari medi annui;
  - anno migliore in errori standard: il massimo fra i sette rapporti (divario medio dell'anno) / (deviazione
    standard dei divari giornalieri di quell'anno / radice delle sedute dell'anno). L'errore standard e' quello
    semplice: serve solo a mettere gli anni sulla stessa scala, il confronto e' con la stessa statistica sotto il nullo.
In piu' (sezione 4) la stessa domanda su tutte le 12 celle di sottocampione che l'esito stampa: 7 anni, 3 terzili
di movimento, 2 strumenti.

Seme: 42 (`esegui_test.SEME`), usato solo per ricostruire il braccio casuale identico a quello dell'esito.
Prima di ogni numero nuovo lo script riproduce i numeri noti dell'esito (impronta dei file, divario per anno,
intervallo del divario, terzili): se non tornano si ferma.

Dati: solo il train (SPX500, NAS100), aperto. Le funzioni di `esegui_test.py` sono importate, non modificate.

Uso: python analysis/ultima_mezzora/descrittivo_anno_migliore.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esegui_test as t  # noqa: E402 - funzioni congelate al commit 2b66e65
from core.verifiche import pvalue_mc  # noqa: E402 - esegui_test ha gia' messo la radice del repo nel percorso

TRAIN = ("SPX500", "NAS100")
# Numeri noti: docs/reviews/esiti/ultima_mezzora_train.txt (12/10/2026, commit 2b66e65).
IMPRONTE = {"SPX500": "de2fe88843cf98a2", "NAS100": "a0631ad091f820c6"}
DIVARIO_ESITO = (-0.51, -2.01, 0.99)
ANNI_ESITO = {2020: -2.36, 2021: -2.33, 2022: 4.89, 2023: 0.14, 2024: -1.69, 2025: -2.17, 2026: -1.07}
TERZILI_ESITO = (1.02, 0.01, -1.23)          # movimento piccolo, medio, grande: solo segno lordo
STRUMENTI_ESITO = (-0.75, -0.27)             # divario per strumento


def carica_train() -> dict:
    """Matrici giorno x strumento del train, con le funzioni del test. Rifiuta ogni altro strumento."""
    primari = list(t.GRUPPI["train"]["primari"])
    if tuple(primari) != TRAIN:
        raise SystemExit("Il gruppo train non e' piu' SPX500 + NAS100: lo script non parte.")
    dati = {}
    for nome in primari:
        sed, info = t.sedute_reali(nome)
        imp = t.impronta(info["percorso"])
        if imp != IMPRONTE[nome]:
            raise SystemExit(f"{nome}: impronta {imp}, nell'esito {IMPRONTE[nome]}. I dati non sono quelli del test.")
        dati[nome] = t.prepara(sed[sed["valida"]][["r_rod", "r_lh"]])
    return t.allinea(dati, primari)


def bracci(M: dict, seme: int = t.SEME):
    """Taglia, segni, r_LH centrato e braccio casuale, nello stesso ordine e con lo stesso flusso di `analizza`."""
    w, s, r = M["w"], M["s"], M["r_lh"]
    r_c = r - np.nanmean(r, axis=0)
    rng = np.random.default_rng(seme)
    cas, _ = t.braccio_casuale(np.abs(w), s, r_c, rng, t.N_SPOSTAMENTI)
    return w, s, r_c, cas, rng


def maschere_terzili(M: dict) -> list[np.ndarray]:
    """Terzili di |r_ROD/sigma| su giorno x strumento, con gli stessi tagli dell'esito."""
    ass, resa = np.abs(M["z"]), M["s"] * M["r_lh"]
    ok = np.isfinite(ass) & np.isfinite(resa)
    q = np.quantile(ass[ok], [1 / 3, 2 / 3])
    return [ok & (ass <= q[0]), ok & (ass > q[0]) & (ass <= q[1]), ok & (ass > q[1])]


def per_anno(d: np.ndarray, anni: np.ndarray, elenco: list[int]):
    """Per ogni anno: media, e media in errori standard semplici. `d` ha i giorni sull'ultimo asse."""
    medie, rapporti = [], []
    for a in elenco:
        x = d[..., anni == a]
        m = x.mean(axis=-1)
        es = x.std(axis=-1, ddof=1) / np.sqrt(x.shape[-1])
        medie.append(m)
        rapporti.append(m / es)
    return np.stack(medie, axis=-1), np.stack(rapporti, axis=-1)


def cella_per_giorno(v: np.ndarray, maschera: np.ndarray):
    """Media di una cella giorno x strumento e suo errore standard a grappoli sul giorno (i due indici dello stesso
    giorno valgono una osservazione). `v` ha forma (..., giorni, strumenti)."""
    somma, conta = np.where(maschera, v, 0.0).sum(axis=-1), maschera.sum(axis=-1)
    m = somma.sum(axis=-1) / conta.sum()
    resto = somma - m[..., None] * conta
    g = int((conta > 0).sum())
    es = np.sqrt((resto ** 2).sum(axis=-1) * g / (g - 1)) / conta.sum()
    return m, m / es


def quota(nulle: np.ndarray, reale: float) -> str:
    """Quota di spostamenti con la statistica almeno pari al reale: (b+1)/(B+1) come `core.verifiche.pvalue_mc`.
    Gli spostamenti sono tutti quelli ammessi, quindi la quota e' esatta; l'intervallo fra parentesi vale solo se
    li si legge come estrazioni indipendenti dal nullo."""
    p = pvalue_mc(int(np.sum(nulle >= reale - 1e-12)), int(nulle.size))
    return f"{p['p']:.3f} ({int(round(p['p_grezzo'] * p['repliche']))} su {p['repliche']}; [{p['low']:.3f}; {p['high']:.3f}])"


def main() -> int:
    print("DESCRITTIVO A POSTERIORI: non decide, non e' un trial, non riapre nulla.")
    M = carica_train()
    w, s, r_c, cas, _ = bracci(M)
    giorni = M["giorni"]
    anni = giorni.year.to_numpy()
    elenco = sorted(set(anni.tolist()))
    n = w.shape[0]
    terzili = maschere_terzili(M)
    tutto = np.isfinite(w)

    # --- 1. riproduzione dei numeri noti dell'esito -------------------------------------------------------------
    d0 = t.portafoglio((w - cas) * r_c)
    ic = t.ic_blocchi(d0, t.N_BOOT, t.SEME)
    m0, t0 = per_anno(d0, anni, elenco)
    ter0 = [cella_per_giorno(s * M["r_lh"], c) for c in terzili]
    str0 = [cella_per_giorno((w - cas) * r_c, tutto & (np.arange(w.shape[1]) == j)) for j in range(w.shape[1])]
    torna = (abs(ic["media"] - DIVARIO_ESITO[0]) < 0.006 and abs(ic["low"] - DIVARIO_ESITO[1]) < 0.006
             and abs(ic["high"] - DIVARIO_ESITO[2]) < 0.006
             and elenco == sorted(ANNI_ESITO) and all(abs(m0[i] - ANNI_ESITO[a]) < 0.006 for i, a in enumerate(elenco))
             and all(abs(float(ter0[i][0]) - TERZILI_ESITO[i]) < 0.006 for i in range(3))
             and all(abs(float(str0[j][0]) - STRUMENTI_ESITO[j]) < 0.006 for j in range(2)))
    print(f"\n--- 1. Riproduzione dell'esito (seme {t.SEME}, {n} sedute {giorni.min().date()} -> {giorni.max().date()})")
    print(f"divario {ic['media']:+.2f} [{ic['low']:+.2f}; {ic['high']:+.2f}] pb, MDE {ic['mde']:.2f} "
          f"(esito: {DIVARIO_ESITO[0]:+.2f} [{DIVARIO_ESITO[1]:+.2f}; {DIVARIO_ESITO[2]:+.2f}]) -> "
          f"{'torna' if torna else 'NON TORNA'}")
    print("anno | divario esito | ricalcolato | sedute | dev. std. giornaliera | errore standard | rapporto")
    for i, a in enumerate(elenco):
        x = d0[anni == a]
        print(f"{a} | {ANNI_ESITO.get(a, float('nan')):+.2f} | {m0[i]:+.2f} | {x.size} | {x.std(ddof=1):.1f} | "
              f"{x.std(ddof=1) / np.sqrt(x.size):.2f} | {t0[i]:+.2f}")
    print("terzili di movimento (solo segno lordo; esito | ricalcolato | in errori standard a grappoli sul giorno): "
          + " ; ".join(f"{nome}: {TERZILI_ESITO[i]:+.2f} | {float(ter0[i][0]):+.2f} | {float(ter0[i][1]):+.2f}"
                       for i, nome in enumerate(("piccolo", "medio", "grande"))))
    print("strumenti (divario; esito | ricalcolato | in errori standard): "
          + " ; ".join(f"{nome}: {STRUMENTI_ESITO[j]:+.2f} | {float(str0[j][0]):+.2f} | {float(str0[j][1]):+.2f}"
                       for j, nome in enumerate(M["nomi"])))
    if not torna:
        print("I numeri noti non tornano: nessun descrittivo.")
        return 3

    # --- 2. il nullo: tutti gli spostamenti circolari ammessi ----------------------------------------------------
    taglia = np.abs(w)
    spost = np.arange(t.LAG_MIN, n - t.LAG_MIN)
    segni = np.stack([np.roll(s, int(k), axis=0) for k in spost])          # (spostamenti, giorni, strumenti)
    Dj = (taglia * segni - cas) * r_c                                       # divario per strumento
    D = np.nanmean(Dj, axis=-1)                                             # portafoglio 1/N, come `portafoglio`
    mN, tN = per_anno(D, anni, elenco)

    i_pb, i_es = int(np.argmax(m0)), int(np.argmax(t0))
    print(f"\n--- 2. Anno migliore dei {len(elenco)}, contro {spost.size} spostamenti (tutti quelli ammessi)")
    print(f"reale, in punti base: {elenco[i_pb]} con {m0[i_pb]:+.2f} pb | reale, in errori standard: "
          f"{elenco[i_es]} con {t0[i_es]:+.2f}")
    print(f"(a) l'anno migliore ha un divario >= {m0[i_pb]:+.2f} pb:        quota {quota(mN.max(axis=1), m0[i_pb])}")
    print(f"(b) l'anno migliore, in errori standard, e' >= {t0[i_es]:+.2f}:  quota {quota(tN.max(axis=1), t0[i_es])}")
    j = elenco.index(2022)
    print("per confronto, il 2022 guardato DA SOLO (come se fosse stato scelto prima):")
    print(f"    divario 2022 >= {m0[j]:+.2f} pb: quota {quota(mN[:, j], m0[j])}")
    print(f"    in errori standard >= {t0[j]:+.2f}: quota {quota(tN[:, j], t0[j])}")
    q = np.percentile(mN.max(axis=1), [50, 95])
    qt = np.percentile(tN.max(axis=1), [50, 95])
    print(f"sotto il nullo l'anno migliore vale in mediana {q[0]:+.2f} pb (95esimo percentile {q[1]:+.2f}); "
          f"in errori standard {qt[0]:+.2f} (95esimo {qt[1]:+.2f})")
    chi_pb = np.bincount(mN.argmax(axis=1), minlength=len(elenco)) / spost.size
    chi_es = np.bincount(tN.argmax(axis=1), minlength=len(elenco)) / spost.size
    print("quale anno e' il migliore sotto il nullo (in pb | in errori standard): " + " ; ".join(
        f"{a}: {chi_pb[i]:.0%} | {chi_es[i]:.0%}" for i, a in enumerate(elenco)))

    # --- 3. lo stesso taglio letto dagli altri due lati ----------------------------------------------------------
    print("\n--- 3. Lo stesso taglio per anno, dagli altri lati (per non leggerlo all'incontrario)")
    print(f"anno piu' estremo in valore assoluto, in errori standard (reale {np.abs(t0).max():.2f}): "
          f"quota {quota(np.abs(tN).max(axis=1), float(np.abs(t0).max()))}")
    print(f"anno peggiore, in errori standard (reale {t0.min():+.2f}): quota con un anno peggiore almeno cosi' "
          f"{quota(-tN.min(axis=1), float(-t0.min()))}")
    pos0, posN = int((m0 > 0).sum()), (mN > 0).sum(axis=1)
    print(f"anni positivi: reale {pos0} su {len(elenco)}; sotto il nullo in media {posN.mean():.1f}; "
          f"quota con {pos0} o meno anni positivi {(int(np.sum(posN <= pos0)) + 1) / (spost.size + 1):.3f}")

    # --- 4. tutte le celle di sottocampione dell'esito: 7 anni + 3 terzili + 2 strumenti ------------------------
    terN = [cella_per_giorno(segni * M["r_lh"], c)[1] for c in terzili]
    strN = [cella_per_giorno(Dj, tutto & (np.arange(w.shape[1]) == jj))[1] for jj in range(w.shape[1])]
    celle0 = np.concatenate([t0, [float(x[1]) for x in ter0], [float(x[1]) for x in str0]])
    celleN = np.column_stack([tN] + terN + strN)
    nomi_celle = [str(a) for a in elenco] + ["mov. piccolo", "mov. medio", "mov. grande"] + list(M["nomi"])
    print(f"\n--- 4. Tutte le {celle0.size} celle di sottocampione dell'esito (anni, terzili di movimento, strumenti)")
    print("in errori standard: " + " ; ".join(f"{nm} {v:+.2f}" for nm, v in zip(nomi_celle, celle0)))
    print(f"cella migliore: {nomi_celle[int(celle0.argmax())]} con {celle0.max():+.2f}. Sotto il nullo la cella "
          f"migliore delle {celle0.size} e' almeno cosi' grande: quota {quota(celleN.max(axis=1), float(celle0.max()))}")
    print(f"cella piu' estrema in valore assoluto ({np.abs(celle0).max():.2f}): quota "
          f"{quota(np.abs(celleN).max(axis=1), float(np.abs(celle0).max()))}")
    print("\nLettura: se le quote non sono piccole, un anno migliore come il 2022 e' quello che il caso produce "
          "guardando sette anni. Non e' un test, non cambia il verdetto e non apre nessuna strada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
