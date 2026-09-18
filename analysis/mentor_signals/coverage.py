"""Controllo di copertura dei dati — da chiamare PRIMA di qualunque calcolo.

Perche' esiste
--------------
Il 2026-09-18 abbiamo prodotto tre versioni successive delle soglie di ritiro del
copier, e due sono state invalidate non da un errore di metodo ma dai **dati in
ingresso**:

  1. i timestamp dei segnali erano indietro di **1h** rispetto al feed prezzi
     (look-ahead: il fill veniva cercato prima che il segnale esistesse);
  2. si usavano `XAU_spot_M5.csv` (fino al 12/06) e `signals.csv` (fino al 08/07)
     mentre nel **repo** c'erano gia' `XAU_spot_M5_ext.csv` (fino al 07/08) e un
     export Telegram con due mesi in piu'.

Nessuno dei due difetti era invisibile: bastava **stampare la finestra dei dati
prima di calcolare**. Non lo facevamo, quindi non lo vedevamo.

Questo modulo lo rende obbligatorio e rumoroso.

    from coverage import verifica
    T, HI, LO, CL, segnali = verifica()   # stampa la copertura, solleva se non torna
"""
from __future__ import annotations

import datetime as dt
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data")

# Quanti giorni di ritardo sono tollerabili fra la fine dei dati e oggi prima di
# considerarli stantii. Oltre, si avvisa: non e' un errore, ma va visto.
GIORNI_STANTII = 21


class CoperturaInsufficiente(RuntimeError):
    """I dati non coprono quello che l'analisi sta per assumere."""


def _finestra(ts):
    return str(min(ts))[:16], str(max(ts))[:16]


def verifica(prezzi="XAU_spot_M5_ext.csv", silenzioso=False):
    """Carica prezzi e segnali, stampa la copertura di entrambi, solleva se non torna.

    Ritorna (T, HI, LO, CL, segnali). Usa SEMPRE il feed esteso e l'export
    Telegram: i file corti (`XAU_spot_M5.csv`, `signals.csv`) restano solo per
    compatibilita' storica e **non vanno usati per analisi nuove**.
    """
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.dirname(__file__))
    from analysis.mentor_signals import backtest as bt
    import oos_validation as ov

    percorso = os.path.join(DATA, prezzi)
    if not os.path.exists(percorso):
        raise CoperturaInsufficiente("feed prezzi assente: %s" % percorso)
    bt.M5 = percorso
    T, HI, LO, CL = bt.load_m5()

    righe = ov.parse_export()
    if not righe:
        raise CoperturaInsufficiente(
            "ZERO segnali letti da %s.\n"
            "  Metti l'export Telegram (i file messages*.html) dentro quella "
            "cartella, oppure controlla che il parser li riconosca." % ov.EXPORT)
    segnali = ov.to_engine(righe)

    p0, p1 = _finestra(T)
    s0, s1 = _finestra([r["ts"] for r in righe])
    oggi = dt.date.today()
    fine_prezzi = dt.datetime.fromisoformat(p1).date()
    fine_segnali = dt.datetime.fromisoformat(s1).date()
    ritardo_p = (oggi - fine_prezzi).days
    ritardo_s = (oggi - fine_segnali).days

    if not silenzioso:
        print("COPERTURA DEI DATI (controllata prima di calcolare)")
        print("-" * 68)
        print("  prezzi  %-28s %s -> %s  (%d barre)"
              % (os.path.basename(percorso), p0, p1, len(T)))
        print("  segnali %-28s %s -> %s  (%d messaggi)"
              % (os.path.basename(ov.EXPORT) + "/", s0, s1, len(righe)))
        print("  ritardo rispetto a oggi: prezzi %d giorni, segnali %d giorni"
              % (ritardo_p, ritardo_s))

    # I segnali senza prezzi che li coprano NON sono replayabili: e' esattamente
    # la situazione che ci ha fatto buttare via un mese (segnali al 08/07,
    # prezzi al 12/06).
    scoperti = (fine_segnali - fine_prezzi).days
    if scoperti > 1:
        print("  ATTENZIONE: %d giorni di segnali NON hanno prezzi per essere "
              "replayati (%s -> %s). Estendi il feed prima di fidarti dei numeri."
              % (scoperti, p1[:10], s1[:10]), file=sys.stderr)
    if max(ritardo_p, ritardo_s) > GIORNI_STANTII:
        print("  ATTENZIONE: dati fermi da piu' di %d giorni. Aggiorna export e "
              "feed prima di prendere decisioni operative." % GIORNI_STANTII,
              file=sys.stderr)
    if not silenzioso:
        print()
    return T, HI, LO, CL, segnali
