"""Ogni check prende l'errore VERO da cui nasce, o non serve a niente.

Non sono test di funzioni: sono **riproduzioni degli incidenti**. Ogni fixture qui
ricostruisce un difetto realmente accaduto in questo workspace, con la sua magnitudo
documentata, e verifica che `core.data_checks` lo fermi. Un check che passa su dati
puliti ma non riconosce il proprio incidente e' decorazione.

    python core/tests/test_data_checks.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.data_checks import (  # noqa: E402
    barre_per_anno, checklist_dati, checklist_esecuzione, copertura_comune,
    duplicati, file_piu_completo, fill_ottenibili, gap_oltre_stop, monotonia,
)


def feed(inizio="2012-01-02", n=3500, freq="D"):
    return pd.DataFrame({"time": pd.date_range(inizio, periods=n, freq=freq),
                         "close": np.linspace(100, 140, n)})


# --- 1: 2026-08-14, cumsum invertito -> serie decrescente nel tempo ---------
def prova_monotonia():
    d = feed()
    assert monotonia(d).ok, "una serie pulita e' stata segnalata"
    # l'incidente: la chiave di raggruppamento invertiva l'ordine
    rotto = d.iloc[::-1].reset_index(drop=True)
    e = monotonia(rotto)
    assert not e.ok and "monotonia" in e.rotte, str(e)
    # e anche il caso subdolo: un solo blocco fuori posto dopo un merge
    quasi = pd.concat([d.iloc[:100], d.iloc[50:60], d.iloc[100:]]).reset_index(drop=True)
    assert not monotonia(quasi).ok, "10 righe fuori ordine non rilevate"
    return "3 forme di disordine temporale rilevate"


# --- 2: timestamp ripetuti dopo una fusione di sessioni ---------------------
def prova_duplicati():
    d = feed()
    assert duplicati(d).ok
    doppio = pd.concat([d, d.iloc[500:520]]).sort_values("time").reset_index(drop=True)
    e = duplicati(doppio)
    assert not e.ok and "20 timestamp ripetuti" in str(e), str(e)
    return "20 barre contate due volte rilevate"


# --- 3: barre/anno implausibili --------------------------------------------
def prova_barre_anno():
    giorn = feed(n=3500)                      # ~365 barre/anno di calendario
    assert barre_per_anno(giorn, attese=(300, 400)).ok
    e = barre_per_anno(giorn, attese=(200, 300))
    assert not e.ok, "barre/anno fuori dall'atteso non rilevate"
    # senza atteso dichiarato: riserva, non ok silenzioso
    e2 = barre_per_anno(giorn)
    assert e2.ok and "barre/anno" in e2.riserve, str(e2)
    return "fuori range rilevato; assenza di atteso dichiarata come riserva"


# --- 4: il feed del playground (A1), partenze scaglionate -------------------
def prova_copertura():
    allineati = {"EURUSD": feed(), "XAUUSD": feed("2012-01-05")}
    assert not copertura_comune(allineati).riserve, "partenze allineate segnalate"
    # l'incidente vivo: i bond partono nel 2016-17, il resto nel 2012
    sfasati = {"EURUSD": feed(), "US500": feed(), "BUND": feed("2016-06-01", n=2500),
               "UST10": feed("2017-02-01", n=2300)}
    e = copertura_comune(sfasati)
    assert "partenze" in e.riserve, str(e)
    assert "EPOCHE" in str(e) and "BUND" in str(e), str(e)
    assert "2017-02-01" in str(e), "la finestra comune non parte dal piu' tardivo"
    return "partenze scaglionate di ~5 anni segnalate, con finestra comune stampata"


# --- 5: 2026-09-18, il file corto accanto a quello lungo --------------------
def prova_file(tmp=None):
    import tempfile
    d = tempfile.mkdtemp()
    corto = os.path.join(d, "XAU_spot_M5.csv")
    lungo = os.path.join(d, "XAU_spot_M5_ext.csv")
    feed(n=500).to_csv(corto, index=False)
    feed(n=4000).to_csv(lungo, index=False)
    e = file_piu_completo(corto)
    assert not e.ok and "XAU_spot_M5_ext.csv" in str(e), str(e)
    assert file_piu_completo(lungo).ok, "il file piu' lungo e' stato segnalato"
    return "file corto rilevato con accanto quello lungo (+%d%%)" % 700


# --- 6: il fill fantasma del FADE, 46,1% dei setup -------------------------
def prova_fill():
    rng = np.random.default_rng(11)
    n = 10218                                   # i setup veri del FADE
    entry = np.full(n, 100.0)
    long = rng.random(n) < 0.5
    # 46,1% dei setup ha l'apertura gia' oltre il livello
    gia = rng.random(n) < 0.461
    apertura = np.where(long, np.where(gia, 100.5, 99.5), np.where(gia, 99.5, 100.5))
    e = fill_ottenibili(apertura, entry, long)
    assert not e.ok, "il 46%% di fill fantasma non e' stato bloccato:\n%s" % e
    assert "46." in str(e) or "45." in str(e), str(e)

    # un 2% e' un dettaglio, ma va comunque dichiarato: passa, non tace
    gia2 = rng.random(n) < 0.02
    ap2 = np.where(long, np.where(gia2, 100.5, 99.5), np.where(gia2, 99.5, 100.5))
    e2 = fill_ottenibili(ap2, entry, long)
    assert e2.ok and "dichiarato" in str(e2), str(e2)

    # e il caso che nessuno sospetta: il backtest riempie SEMPRE
    ap3 = np.where(long, 99.5, 100.5)
    e3 = fill_ottenibili(ap3, entry, long)
    assert "non e' un ordine" in str(e3), str(e3)

    # senza misura, non c'e' verdetto: il gate deve BLOCCARE, non avvisare
    e4 = checklist_esecuzione()
    assert not e4.ok and "ne' GO ne' NO-GO" in str(e4), str(e4)
    return "46,1% bloccato; 2% dichiarato; 'riempie sempre' segnalato; assenza = BLOCCA"


# --- 7: gap oltre lo stop, 12,7% degli stop del FADE -----------------------
def prova_gap():
    rng = np.random.default_rng(3)
    n = 2000
    long = rng.random(n) < 0.5
    sl = np.where(long, 99.0, 101.0)
    oltre = np.zeros(n, dtype=bool)          # esattamente 12,7%, non "circa"
    oltre[rng.permutation(n)[:int(round(0.127 * n))]] = True
    apertura = np.where(long, np.where(oltre, 98.5, 99.5), np.where(oltre, 101.5, 100.5))
    e = gap_oltre_stop(apertura, sl, long)
    assert "gap oltre stop" in e.riserve, str(e)
    assert "12.7%" in str(e), str(e)
    return "12,7% di stop con gap segnalato (vale +0,046R sul FADE)"


# --- 8: la checklist intera su dati puliti non deve gridare ----------------
def prova_composizione():
    puliti = {"EURUSD": feed(), "XAUUSD": feed("2012-01-03")}
    e = checklist_dati(puliti, barre_attese=(300, 400))
    assert e.ok, "dati puliti segnalati come rotti:\n%s" % e
    assert not e.riserve, "riserve inventate su dati puliti:\n%s" % e
    return "nessun falso allarme su dati puliti"



# --- wrapper per pytest: le prove qui sopra ritornano una riga di referto,
#     che pytest non vuole. La sostanza sta li', questi sono solo adattatori.
def test_monotonia():
    assert prova_monotonia()

def test_duplicati():
    assert prova_duplicati()

def test_barre_anno():
    assert prova_barre_anno()

def test_copertura():
    assert prova_copertura()

def test_file():
    assert prova_file()

def test_fill():
    assert prova_fill()

def test_gap():
    assert prova_gap()

def test_composizione():
    assert prova_composizione()


def main() -> int:
    prove = [("monotonia temporale", prova_monotonia),
             ("duplicati di timestamp", prova_duplicati),
             ("barre per anno", prova_barre_anno),
             ("copertura / partenze", prova_copertura),
             ("file piu' completo", prova_file),
             ("fill ottenibili", prova_fill),
             ("gap oltre lo stop", prova_gap),
             ("nessun falso allarme", prova_composizione)]
    print("core/data_checks.py - ogni check contro l'incidente da cui nasce")
    print("=" * 78)
    for nome, fn in prove:
        print("  %-24s OK   %s" % (nome, fn()))
    print()
    print("TUTTI I TEST PASSATI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
