"""La primitiva riproduce i baseline originali, o non serve a niente.

Stessa prova pretesa per `core/resolve_trade.py`: ogni test qui sotto ricopia il
campionamento di una delle implementazioni storiche e verifica che
`core.random_baseline` produca **gli stessi identici indici**, a parita' di generatore
e di ordine delle chiamate. Senza questa prova la primitiva sarebbe un nono baseline,
cioe' il problema che doveva risolvere.

I quattro originali coperti:
  1. analysis/nxt/stops.py            - pool d'anno, trim di MAX_HOLD+1, guard su MAX_HOLD+2
  2. analysis/nxt/excursion.py        - pool d'anno pieno (e excursion_recheck.py, identico)
  3. analysis/trend/backtest.py       - pool d'anno ristretto alla finestra valida lo_v..hi_v-2
  4. analysis/level_research/engine.py - distance-matched dal pool reale (concetto, lato)

Piu' i test di cio' che prima non esisteva affatto: la **verifica** del matching e il
divario con bootstrap a cluster.

    python core/tests/test_random_baseline.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.random_baseline import (  # noqa: E402
    BarSampler, PoolSampler, check_matching, gap_ci,
)

MAX_HOLD = 40
M_RANDOM = 3
SEED = 7


def anni_finti(n=4000, primo=2012):
    """Chiave di strato per barra: anni di lunghezza disuguale, come un feed vero."""
    anni, y, resto = [], primo, n
    rng = np.random.default_rng(0)
    while resto > 0:
        k = min(resto, int(rng.integers(30, 900)))
        anni += [y] * k
        y += 1
        resto -= k
    return np.asarray(anni[:n])


def eventi_finti(anni, n=250, seed=1):
    """Indici di barra su cui si appoggiano gli eventi reali."""
    rng = np.random.default_rng(seed)
    return sorted(int(x) for x in rng.integers(0, len(anni), size=n))


# --- 1: analysis/nxt/stops.py -----------------------------------------------
def originale_stops(anni, eventi, rng, m=M_RANDOM):
    """Copia letterale del blocco 'baseline random risk-matched' di stops.py."""
    fuori = []
    for f in eventi:
        same_year = np.where(anni == anni[f])[0]
        if len(same_year) > MAX_HOLD + 2:
            pool = (same_year[:-(MAX_HOLD + 1)] if len(same_year) > MAX_HOLD + 1
                    else same_year)
            for _ in range(m):
                fuori.append(int(rng.choice(pool)))
    return fuori


def prova_stops():
    anni = anni_finti()
    eventi = eventi_finti(anni)
    atteso = originale_stops(anni, eventi, np.random.default_rng(SEED))
    s = BarSampler(anni, np.random.default_rng(SEED),
                   trim_tail=MAX_HOLD + 1, min_pool=MAX_HOLD + 2)
    ottenuto = []
    for f in eventi:
        ottenuto += s.draw(anni[f], M_RANDOM)
    assert ottenuto == atteso, "stops.py: %d/%d indici diversi" % (
        sum(a != b for a, b in zip(ottenuto, atteso)), len(atteso))
    assert len(atteso) > 300, "il test non sta estraendo abbastanza: %d" % len(atteso)
    return len(atteso)


# --- 2: analysis/nxt/excursion.py (e excursion_recheck.py) ------------------
def originale_excursion(anni, eventi, rng, m=M_RANDOM):
    """Copia letterale: by_year[y] pieno, nessun trim, nessun guard."""
    by_year = {y: np.flatnonzero(anni == y) for y in np.unique(anni)}
    fuori = []
    for f in eventi:
        for _ in range(m):
            fuori.append(int(rng.choice(by_year[anni[f]])))
    return fuori


def prova_excursion():
    anni = anni_finti()
    eventi = eventi_finti(anni)
    atteso = originale_excursion(anni, eventi, np.random.default_rng(SEED))
    s = BarSampler(anni, np.random.default_rng(SEED))
    ottenuto = []
    for f in eventi:
        ottenuto += s.draw(anni[f], M_RANDOM)
    assert ottenuto == atteso, "excursion.py: indici diversi"
    return len(atteso)


# --- 3: analysis/trend/backtest.py ------------------------------------------
def originale_trend(anni, eventi, rng, lo_v, hi_v, m=M_RANDOM):
    """Copia letterale: pool d'anno intersecato con la finestra valida del feed."""
    n = len(anni)
    fuori = []
    for f in eventi:
        same_year = np.flatnonzero((anni == anni[f]) & (np.arange(n) >= lo_v)
                                   & (np.arange(n) <= hi_v - 2))
        for _ in range(m):
            if len(same_year) == 0:
                break
            fuori.append(int(rng.choice(same_year)))
    return fuori


def prova_trend():
    anni = anni_finti()
    eventi = eventi_finti(anni)
    lo_v, hi_v = 200, len(anni) - 50
    atteso = originale_trend(anni, eventi, np.random.default_rng(SEED), lo_v, hi_v)
    usable = (np.arange(len(anni)) >= lo_v) & (np.arange(len(anni)) <= hi_v - 2)
    s = BarSampler(anni, np.random.default_rng(SEED), usable=usable)
    ottenuto = []
    for f in eventi:
        ottenuto += s.draw(anni[f], M_RANDOM)
    assert ottenuto == atteso, "trend/backtest.py: indici diversi"
    # e il warm-up deve essere davvero escluso, non solo "in media"
    assert min(ottenuto) >= lo_v and max(ottenuto) <= hi_v - 2
    return len(atteso)


# --- 4: analysis/level_research/engine.py -----------------------------------
def originale_livelli(livelli, rng, m=M_RANDOM):
    """Copia letterale del random distance-matched: pool per (concetto, lato)."""
    from collections import defaultdict
    pool = defaultdict(list)
    for con, side, dist in livelli:
        pool[(con, side)].append(dist)
    pool = {k: np.array(v) for k, v in pool.items()}
    fuori = []
    for con, side, _ in livelli:
        dpool = pool.get((con, side))
        if dpool is None or len(dpool) == 0:
            continue
        for _ in range(m):
            fuori.append(float(rng.choice(dpool)))
    return fuori


def prova_livelli():
    rng0 = np.random.default_rng(3)
    concetti = ["PDH", "PDL", "POC", "VAH"]
    livelli = [(concetti[int(rng0.integers(0, 4))],
                "SUPPORT" if rng0.random() < 0.5 else "RESISTANCE",
                float(rng0.gamma(2.0, 0.8))) for _ in range(600)]
    atteso = originale_livelli(livelli, np.random.default_rng(SEED))

    p = PoolSampler(np.random.default_rng(SEED))
    for con, side, dist in livelli:
        p.add((con, side), dist)
    p.freeze()
    ottenuto = []
    for con, side, _ in livelli:
        ottenuto += p.draw((con, side), M_RANDOM)
    assert ottenuto == atteso, "level_research: distanze diverse"

    # il pool si congela PRIMA di estrarre: aggiungere dopo deve essere un errore,
    # perche' i primi eventi campionerebbero da un pool piu' povero degli ultimi.
    try:
        p.add(("PDH", "SUPPORT"), 1.0)
    except RuntimeError:
        pass
    else:
        raise AssertionError("add() dopo freeze() doveva sollevare")
    return len(atteso)


# --- 5: la verifica del matching (prima non esisteva) -----------------------
def _coppie(n_eventi=200, m=3, seed=5, rompi=None):
    rng = np.random.default_rng(seed)
    real, rand = [], []
    for i in range(n_eventi):
        ev = {"sigid": "E%03d" % i, "asset": "EURUSD" if i % 2 else "XAUUSD",
              "side": "BUY" if i % 3 else "SELL", "risk": float(1 + rng.random()),
              "hold": float(rng.integers(3, 40)), "R": float(rng.normal(0.0, 1.0))}
        real.append(ev)
        for j in range(m):
            c = {"sigid": ev["sigid"], "asset": ev["asset"], "side": ev["side"],
                 "risk": ev["risk"], "hold": float(rng.integers(3, 40)),
                 "R": float(rng.normal(0.0, 1.0))}
            if rompi == "side" and i == 7 and j == 0:
                c["side"] = "BUY" if c["side"] == "SELL" else "SELL"
            if rompi == "risk" and i == 11 and j == 1:
                c["risk"] = ev["risk"] * 1.5
            rand.append(c)
    return pd.DataFrame(real), pd.DataFrame(rand)


def prova_matching():
    real, rand = _coppie()
    rep = check_matching(real, rand, link="sigid")
    assert rep.ok, "un baseline corretto e' stato segnalato come rotto:\n%s" % rep

    # un solo controllo col lato sbagliato deve bastare a far fallire tutto:
    # e' il "trap piu' frequente del workspace" e non puo' passare per media.
    real, rand = _coppie(rompi="side")
    rep = check_matching(real, rand, link="sigid")
    assert not rep.ok and "side" in rep.rotte, "lato invertito non rilevato:\n%s" % rep

    real, rand = _coppie(rompi="risk")
    rep = check_matching(real, rand, link="sigid")
    assert not rep.ok and "risk" in rep.rotte, "rischio diverso non rilevato:\n%s" % rep

    # meno di 3 controlli per evento: baseline troppo rumoroso
    real, rand = _coppie(m=1)
    rep = check_matching(real, rand, link="sigid")
    assert not rep.ok and "n_events" in rep.rotte, "m=1 doveva essere bloccato:\n%s" % rep

    # eventi senza controlli: non e' un dettaglio, e' un campione selezionato
    real, rand = _coppie()
    rand = rand[rand["sigid"] != "E000"]
    rep = check_matching(real, rand, link="sigid")
    assert "SENZA controlli" in str(rep), "eventi scoperti non riportati:\n%s" % rep
    return str(rep).splitlines()[0]


# --- 6: il divario, con cluster sull'evento ---------------------------------
def prova_gap():
    # (a) nessun edge: il CI deve contenere lo zero
    real, rand = _coppie(n_eventi=400, seed=9)
    g = gap_ci(real, rand, value="R", link="sigid", n_boot=800)
    assert g["low"] < 0 < g["high"], "gap nullo dichiarato significativo: %s" % g

    # (b) edge vero di +0,5R: il CI deve escluderlo
    real2 = real.copy()
    real2["R"] = real2["R"] + 0.5
    g2 = gap_ci(real2, rand, value="R", link="sigid", n_boot=800)
    assert g2["low"] > 0, "edge di +0,5R non rilevato: %s" % g2
    assert abs(g2["gap"] - (g["gap"] + 0.5)) < 1e-9

    # (c) il cluster conta: ignorarlo su controlli non indipendenti
    #     stringe il CI. Qui si misura la differenza invece di affermarla.
    import core.quant_metrics as qm
    piatto = (real.set_index("sigid")["R"].reindex(rand["sigid"]).to_numpy(float)
              - rand["R"].to_numpy(float))
    ci_iid = qm.bca_bootstrap_ci(piatto, metric=lambda v: float(np.mean(v)),
                                 conf=0.95, n_boot=800, seed=42)
    largh_iid = ci_iid["high"] - ci_iid["low"]
    largh_cluster = g["high"] - g["low"]
    assert largh_cluster > largh_iid, (
        "il CI a cluster (%.4f) non e' piu' largo di quello i.i.d. (%.4f): "
        "il test non sta dimostrando nulla" % (largh_cluster, largh_iid))
    return largh_iid, largh_cluster


# ---------------------------------------------------------------------------

# --- wrapper per pytest: le prove qui sopra ritornano una riga di referto,
#     che pytest non vuole. La sostanza sta li', questi sono solo adattatori.
def test_stops():
    assert prova_stops()

def test_excursion():
    assert prova_excursion()

def test_trend():
    assert prova_trend()

def test_livelli():
    assert prova_livelli()

def test_matching():
    assert prova_matching()

def test_gap():
    assert prova_gap()


def main() -> int:
    n1 = prova_stops()
    n2 = prova_excursion()
    n3 = prova_trend()
    n4 = prova_livelli()
    riga = prova_matching()
    iid, clu = prova_gap()
    print("core/random_baseline.py - equivalenza con i baseline storici")
    print("=" * 70)
    print("  1. analysis/nxt/stops.py              OK   %5d estrazioni identiche" % n1)
    print("  2. analysis/nxt/excursion.py          OK   %5d estrazioni identiche" % n2)
    print("     (analysis/nxt/excursion_recheck.py: stesso pool, coperto da (2))")
    print("  3. analysis/trend/backtest.py         OK   %5d estrazioni identiche" % n3)
    print("  4. analysis/level_research/engine.py  OK   %5d distanze identiche" % n4)
    print()
    print("cio' che prima NON esisteva:")
    print("  5. verifica del matching              OK   %s" % riga)
    print("     rileva: lato invertito, rischio diverso, m<3, eventi senza controlli")
    print("  6. divario con cluster sull'evento    OK   CI i.i.d. %.4f -> cluster %.4f"
          % (iid, clu))
    print("     il CI i.i.d. e' piu' stretto del %.0f%%: sarebbe stato falso"
          % (100 * (1 - iid / clu)))
    print()
    print("TUTTI I TEST PASSATI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
