"""VERIFICHE DELLA REVISIONE G2 (12/10/2026): non decidono, non sono un trial, non riaprono nulla.

Famiglia `momentum_ultima_mezzora`, CLOSED al train il 12/10/2026 (docs/reviews/esiti/ultima_mezzora_train.txt).
Referto: docs/reviews/ultima_mezzora_G2_2026-10-12.md. Il verdetto resta quello dell'esito, con i parametri
pre-registrati (blocco medio 10, seme 42). Qui si misura quanto regge, e si mette un'incertezza accanto ai
descrittivi che l'esito stampa senza. Niente etichette, niente scritture in docs/reviews/esiti/, niente holdout.

0. Lettura dei dati reali contro un secondo feed: r_ROD e r_LH dei file Dukascopy del test, confrontati seduta per
   seduta con gli stessi rendimenti dai file MT5 FP Markets (US500, US100: aperti, 2025-2026). Nessun rendimento
   della strategia. Un verdetto negativo non ha controllo positivo sui dati reali: questo e' il sostituto.
1. Limite ALTO del divario su 10 semi: e' quello che decide il CLOSED; l'esito ripete sui semi solo il limite basso.
2. Intervallo del divario al variare della lunghezza media del blocco (1 = giorni indipendenti; 10 = pre-registrata).
3. Dipendenza nel tempo: runs test dell'esito riprodotto, runs test e autocorrelazione del divario giornaliero.
4. Costi: costo medio pagato per seduta, attesa netta a costi 1x e 3x con intervallo.
5. La soglia di CLOSED tradotta in unita' di taglia fissa (NON pre-registrata): cosa cambia fra proporzionale e segno.
6. I due controlli del meccanismo (§7 della pre-registrazione) con la loro incertezza: terzili e inversione.

Ogni blocco riproduce prima il numero noto dell'esito; se non torna lo dice. Dati: solo il train (SPX500, NAS100).
Le funzioni di `esegui_test.py` sono importate, non modificate; il bootstrap con blocco variabile e' una copia
locale, verificata identica a quella congelata quando il blocco e' 10.

Uso: python analysis/ultima_mezzora/verifiche_g2.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esegui_test as t  # noqa: E402 - funzioni congelate al commit 2b66e65
from core.verifiche import runs_test  # noqa: E402
from descrittivo_anno_migliore import bracci, carica_train, maschere_terzili  # noqa: E402

SEMI = range(10)                       # gli stessi di `core.verifiche.ripeti_su_semi`
BLOCCHI = (1, 5, 10, 20, 40, 60, 120)
MU_SEGNO_FONTE = 2.72                  # pb a seduta, strategia di solo segno, Tab. 6 (ULTIMA_MEZZORA_FATTIBILITA, 09/10)
SECONDO_FEED = {"SPX500": "US500", "NAS100": "US100"}     # Dukascopy del test -> MT5 FP Markets, entrambi aperti
# Dal 10 al 13 marzo 2025 il server MT5 era a New York + 6 ore e la regola fissa del loader (+7) sbaglia di un'ora
# (ULTIMA_MEZZORA_FATTIBILITA, passo 3, condizione 1): sono giorni sbagliati nel secondo feed, non in quello del test.
SCARTO_SERVER = ("2025-03-10", "2025-03-13")


def secondo_feed() -> None:
    """r_ROD e r_LH delle stesse sedute da due fornitori diversi, con la stessa lettura delle barre."""
    for duka, mt5 in SECONDO_FEED.items():
        a, _ = t.sedute_reali(duka)
        b, _ = t.sedute_reali(mt5)
        j = a[a["valida"]].join(b[b["valida"]], lsuffix="_d", rsuffix="_m", how="inner")
        j = j[j.index >= t.INIZIO]
        noti = (j.index >= SCARTO_SERVER[0]) & (j.index <= SCARTO_SERVER[1])
        print(f"{duka} (Dukascopy) contro {mt5} (MT5): {len(j)} sedute comuni, {j.index.min().date()} -> "
              f"{j.index.max().date()}")
        for c in ("r_rod", "r_lh"):
            for nome, sel in (("tutte", np.ones(len(j), bool)), ("senza 10-13/03/2025", ~noti)):
                x, y = j.loc[sel, c + "_d"], j.loc[sel, c + "_m"]
                print(f"  {c}, {nome}: correlazione {x.corr(y):.4f}, stesso segno {(np.sign(x) == np.sign(y)).mean():.1%}, "
                      f"differenza assoluta mediana {(x - y).abs().median():.2f} pb, massima {(x - y).abs().max():.1f}")


def indici(n: int, rng: np.random.Generator, blocco: float) -> np.ndarray:
    """Copia di `esegui_test._indici_bootstrap` con la lunghezza media del blocco come argomento."""
    nuovo = rng.random(n) < 1.0 / blocco
    nuovo[0] = True
    inizi = rng.integers(0, n, n)[nuovo]
    gruppo = np.cumsum(nuovo) - 1
    primo = np.flatnonzero(nuovo)[gruppo]
    return (inizi[gruppo] + np.arange(n) - primo) % n


def ic(x: np.ndarray, blocco: float, n_boot: int = t.N_BOOT, seme: int = t.SEME) -> dict:
    """Come `esegui_test.ic_blocchi`, con il blocco come argomento."""
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seme)
    medie = np.array([x[indici(len(x), rng, blocco)].mean() for _ in range(n_boot)])
    es = float(medie.std(ddof=1))
    return {"media": float(x.mean()), "low": float(np.percentile(medie, 2.5)),
            "high": float(np.percentile(medie, 97.5)), "es": es, "mde": t.K * es, "n": int(len(x))}


def acf(x: np.ndarray, ritardo: int) -> float:
    x = x - x.mean()
    return float((x[ritardo:] * x[:-ritardo]).sum() / (x * x).sum())


def _f(d: dict) -> str:
    return f"{d['media']:+.2f} [{d['low']:+.2f}; {d['high']:+.2f}] (errore standard {d['es']:.2f})"


def main() -> int:
    print("VERIFICHE G2 A POSTERIORI: non decidono, non sono un trial, non riaprono nulla.")
    print("\n--- 0. Lettura dei dati reali contro un secondo feed (nessun rendimento della strategia)")
    secondo_feed()
    M = carica_train()
    w, s, r_c, cas, rng = bracci(M)
    r, n = M["r_lh"], w.shape[0]
    costi = np.array([t.COSTI_PB[nome] for nome in M["nomi"]])
    d0 = t.portafoglio((w - cas) * r_c)
    base = t.ic_blocchi(d0, t.N_BOOT, t.SEME)
    atteso = t.RHO_RIF["train"] * float(np.mean(np.nanmean(np.abs(w) * np.abs(M["z"]) * M["sigma_lh"], axis=0)))
    meta = atteso / 2
    copia = ic(d0, t.BLOCCO_MEDIO)
    print(f"\ndivario {_f(base)} pb; effetto atteso {atteso:.2f}, meta' {meta:.2f} (esito: -0.51 [-2.01; +0.99]; 4.56; 2.28)")
    print(f"copia locale del bootstrap a blocco {t.BLOCCO_MEDIO}: "
          f"{'identica' if copia == base else 'DIVERSA da quella congelata'}")
    print(f"distanza fra limite alto e soglia di CLOSED: {meta - base['high']:.2f} pb = "
          f"{(meta - base['high']) / base['es']:.1f} errori standard; il limite alto supera la soglia solo se la "
          f"semi-ampiezza alta cresce di {((meta - base['media']) / (base['high'] - base['media']) - 1):.0%}")

    print(f"\n--- 1. Limiti del divario su {len(SEMI)} semi (spostamenti e bootstrap)")
    bassi, alti = [], []
    for sm in SEMI:
        ws, _, rcs, cs, _ = bracci(M, sm)
        x = t.ic_blocchi(t.portafoglio((ws - cs) * rcs), t.N_BOOT, sm)
        bassi.append(x["low"])
        alti.append(x["high"])
    print(f"limite basso: da {min(bassi):+.2f} a {max(bassi):+.2f} (esito: da -2.06 a -1.96)")
    print(f"limite ALTO:  da {min(alti):+.2f} a {max(alti):+.2f} (soglia di CLOSED {meta:.2f})")

    print("\n--- 2. Intervallo del divario al variare del blocco medio (seme 42, 5.000 repliche)")
    for b in BLOCCHI:
        x = ic(d0, b)
        nota = " <- pre-registrato" if b == t.BLOCCO_MEDIO else (" (giorni indipendenti)" if b == 1 else "")
        print(f"blocco {b:>3}: [{x['low']:+.2f}; {x['high']:+.2f}], errore standard {x['es']:.2f}, MDE {x['mde']:.2f} "
              f"-> limite alto {'sotto' if x['high'] < meta else 'SOPRA'} la soglia {meta:.2f}{nota}")
    print(f"errore standard semplice (dev. std. / radice di n): {d0.std(ddof=1) / np.sqrt(n):.2f}")

    print("\n--- 3. Dipendenza nel tempo")
    g_fisso = t.portafoglio(t.netto(s, r, costi))
    g_prop = t.portafoglio(t.netto(w, r, costi))
    r_unita = g_fisso / np.nanmean(M["sigma_lh"], axis=1)
    for nome, serie in (("esiti a taglia fissa (come nell'esito: z -1.94, p 0.052)", r_unita > 0),
                        ("segno del divario giornaliero (primaria)", d0 > 0),
                        ("segno del netto proporzionale", g_prop > 0)):
        rt = runs_test(serie)
        print(f"runs test, {nome}: sequenze {rt['sequenze']} contro {rt['attese']:.1f} attese, z {rt['z']:+.2f}, "
              f"p {rt['p']:.3f}")
    banda = 1.96 / np.sqrt(n)
    for nome, serie in (("divario giornaliero", d0), ("divario giornaliero al quadrato", d0 ** 2),
                        ("esito a taglia fissa (vinto/perso)", (r_unita > 0).astype(float))):
        print(f"autocorrelazione, {nome}: " + " ".join(f"r{k} {acf(serie, k):+.3f}" for k in (1, 2, 3, 5, 10))
              + f" (banda del caso +/-{banda:.3f})")

    print("\n--- 4. Costi")
    costo = float(np.nanmean(t.portafoglio(costi * np.abs(w))))
    n1 = t.ic_blocchi(g_prop, t.N_BOOT, t.SEME)
    n3 = t.ic_blocchi(t.portafoglio(t.netto(w, r, costi, 3.0)), t.N_BOOT, t.SEME)
    print(f"costo medio pagato per seduta: {costo:.2f} pb a costi 1x, {3 * costo:.2f} a costi 3x")
    print(f"attesa netta 1x: {_f(n1)} (esito: -0.97 [-2.43; +0.50])")
    print(f"attesa netta 3x: {_f(n3)} (esito: -1.71, senza intervallo)")
    print(f"limite alto del divario {base['high']:+.2f} pb contro il costo medio: {base['high'] / costo:.1f} volte "
          f"il costo 1x, {base['high'] / (3 * costo):.2f} volte il costo 3x")

    print("\n--- 5. Taglia fissa: stessa formula dell'effetto atteso, in unita' di solo segno (NON pre-registrata)")
    cas_f, _ = t.braccio_casuale(np.abs(s), s, r_c, rng, t.N_SPOSTAMENTI)   # stesso flusso di `analizza`
    fisso = t.ic_blocchi(t.portafoglio((s - cas_f) * r_c), t.N_BOOT, t.SEME)
    att_f = t.RHO_RIF["train"] * float(np.mean(np.nanmean(np.abs(s) * np.abs(M["z"]) * M["sigma_lh"], axis=0)))
    print(f"divario a taglia fissa {_f(fisso)} (esito: -0.07 [-1.38; +1.28])")
    print(f"effetto atteso in unita' di solo segno: {att_f:.2f} pb, meta' {att_f / 2:.2f} -> limite alto "
          f"{'sotto' if fisso['high'] < att_f / 2 else 'SOPRA'} la meta'")
    print(f"contro la strategia di solo segno pubblicata (Tab. 6, {MU_SEGNO_FONTE} pb, meta' {MU_SEGNO_FONTE / 2:.2f}): "
          f"limite alto {'sotto' if fisso['high'] < MU_SEGNO_FONTE / 2 else 'SOPRA'} la meta', di "
          f"{abs(MU_SEGNO_FONTE / 2 - fisso['high']):.2f} pb")

    print("\n--- 6. I due controlli del meccanismo, con la loro incertezza (bootstrap a blocchi sui giorni)")
    celle = maschere_terzili(M)
    v = s * r
    somme = np.column_stack([np.where(c, v, 0.0).sum(axis=1) for c in celle])
    conte = np.column_stack([c.sum(axis=1) for c in celle])
    rb = np.random.default_rng(t.SEME)
    rip = np.empty((t.N_BOOT, 3))
    for i in range(t.N_BOOT):
        ix = indici(n, rb, t.BLOCCO_MEDIO)
        rip[i] = somme[ix].sum(axis=0) / conte[ix].sum(axis=0)
    reali = somme.sum(axis=0) / conte.sum(axis=0)
    for j, nome in enumerate(("piccolo", "medio", "grande")):
        print(f"movimento {nome}: solo segno lordo {reali[j]:+.2f} [{np.percentile(rip[:, j], 2.5):+.2f}; "
              f"{np.percentile(rip[:, j], 97.5):+.2f}] pb")
    diff = rip[:, 2] - rip[:, 0]
    print(f"grande meno piccolo (il meccanismo lo vuole positivo): {reali[2] - reali[0]:+.2f} "
          f"[{np.percentile(diff, 2.5):+.2f}; {np.percentile(diff, 97.5):+.2f}] pb")
    dopo = t.ic_blocchi(t.portafoglio(w[:-1] * M["r_rod"][1:]), t.N_BOOT, t.SEME)
    print(f"inversione il giorno dopo (il meccanismo la vuole negativa): {_f(dopo)} pb (esito: -3.59, senza intervallo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
