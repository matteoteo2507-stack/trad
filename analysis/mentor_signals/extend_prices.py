"""Estende il feed M5 dell'oro da MT5, con riconciliazione sulla sovrapposizione.

Ripete il procedimento gia' usato per costruire `XAU_spot_M5_ext.csv`
(pre-registrazione OOS §2: serie originale dell'audit estesa col feed MT5
`XAUUSD.cyr`, First Prudential Markets), invece di rifarlo a mano ogni volta.

**Perche' conta la riconciliazione.** Le due fonti sono broker diversi: prima di
incollarle si misura la differenza sulle barre in comune. L'ultima volta era
mediana **+$0,060** con correlazione 1,000000 su 8.063 barre. Se questa volta la
differenza fosse molto piu' grande, incollare sarebbe sbagliato e lo script lo dice.

    python analysis/mentor_signals/extend_prices.py            # solo diagnosi
    python analysis/mentor_signals/extend_prices.py --scrivi   # aggiorna il csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data")
EXT = os.path.join(DATA, "XAU_spot_M5_ext.csv")
SYM = "XAUUSD.cyr"
SOGLIA_DIFF = 1.0     # dollari: oltre, le due fonti non sono incollabili in silenzio
MIN_BARRE_GIORNO = 250  # su 276 di una giornata piena: sotto, la serie e' bucata (vedi completezza)


def da_mt5(dal: dt.datetime, al: dt.datetime):
    import MetaTrader5 as mt5
    if not mt5.initialize():
        print("MT5 non inizializzato: %s" % (mt5.last_error(),), file=sys.stderr)
        return None
    try:
        info = mt5.symbol_info(SYM)
        if info is None:
            print("simbolo %s assente" % SYM, file=sys.stderr)
            return None
        if not info.visible:
            mt5.symbol_select(SYM, True)
        r = mt5.copy_rates_range(SYM, mt5.TIMEFRAME_M5, dal, al)
    finally:
        mt5.shutdown()
    if r is None or not len(r):
        return None
    d = pd.DataFrame(r)
    d["time"] = pd.to_datetime(d["time"], unit="s")
    return d[["time", "open", "high", "low", "close"]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scrivi", action="store_true",
                    help="scrive davvero il csv esteso (default: solo diagnosi)")
    a = ap.parse_args()

    vecchio = pd.read_csv(EXT, parse_dates=["time"])
    fine = vecchio["time"].max()
    print("feed attuale : %s -> %s  (%d barre)"
          % (str(vecchio['time'].min())[:16], str(fine)[:16], len(vecchio)))

    # si riparte 7 giorni prima della fine, per avere sovrapposizione da riconciliare
    nuovo = da_mt5(fine.to_pydatetime() - dt.timedelta(days=7),
                   dt.datetime.now() + dt.timedelta(days=1))
    if nuovo is None:
        print("nessun dato nuovo da MT5.", file=sys.stderr)
        return 2
    print("da MT5       : %s -> %s  (%d barre)"
          % (str(nuovo['time'].min())[:16], str(nuovo['time'].max())[:16], len(nuovo)))

    # --- riconciliazione sulla sovrapposizione ---------------------------------
    m = vecchio.merge(nuovo, on="time", suffixes=("_v", "_n"))
    if len(m) < 100:
        print("sovrapposizione troppo corta (%d barre): non riconciliabile" % len(m),
              file=sys.stderr)
        return 2
    diff = (m["close_n"] - m["close_v"]).values
    corr = float(np.corrcoef(m["close_v"], m["close_n"])[0, 1])
    print("\nRICONCILIAZIONE su %d barre in comune" % len(m))
    print("  differenza mediana %+.3f $   media %+.3f   max |%.3f|"
          % (np.median(diff), diff.mean(), np.abs(diff).max()))
    print("  correlazione %.6f   (riferimento storico: +$0,060 e 1,000000)" % corr)
    if abs(np.median(diff)) > SOGLIA_DIFF or corr < 0.999:
        print("  -> le due fonti NON sono incollabili in silenzio: fermati e guarda.",
              file=sys.stderr)
        return 3
    print("  -> compatibili, si puo' estendere")

    coda = nuovo[nuovo["time"] > fine]
    print("\nbarre nuove da aggiungere: %d  (%s -> %s)"
          % (len(coda), str(coda['time'].min())[:16] if len(coda) else "-",
             str(coda['time'].max())[:16] if len(coda) else "-"))

    # --- completezza per giorno (2026-10-02) --------------------------------------
    # Alla prima chiamata, se il terminale sta ancora sincronizzando lo storico, MT5 restituisce
    # una serie PARZIALE senza errore: il 02/10 la stessa richiesta ha dato 1.538 barre e un minuto
    # dopo 4.085. Scrivere la prima avrebbe lasciato un buco di 13 giorni nel feed, in silenzio.
    # Ogni giorno feriale INTERO della coda (escluso il primo e l'ultimo, parziali per costruzione)
    # deve avere almeno MIN_BARRE_GIORNO barre M5 (una giornata piena dell'oro ne ha 276).
    if len(coda):
        per_giorno = coda["time"].dt.normalize().value_counts().sort_index()
        interni = per_giorno.iloc[1:-1]
        interni = interni[interni.index.dayofweek < 5]
        corti = interni[interni < MIN_BARRE_GIORNO]
        if len(corti):
            print("  -> giorni INCOMPLETI (storico MT5 non ancora sincronizzato?): "
                  + ", ".join(f"{d.date()}={n}" for d, n in corti.items())
                  + "\n     NON si scrive. Rilancia fra un minuto.", file=sys.stderr)
            return 4
        print("  completezza: %d giorni feriali interi, minimo %d barre/giorno"
              % (len(interni), int(interni.min()) if len(interni) else 0))
    if not a.scrivi:
        print("\n(diagnosi soltanto: rilancia con --scrivi per aggiornare il csv)")
        return 0
    if not len(coda):
        print("niente da aggiungere.")
        return 0

    out = pd.concat([vecchio, coda], ignore_index=True)
    out = out.drop_duplicates(subset="time").sort_values("time")
    backup = EXT + ".bak"
    if not os.path.exists(backup):
        vecchio.to_csv(backup, index=False)
        print("backup del precedente in %s" % os.path.basename(backup))
    out.to_csv(EXT, index=False)
    print("scritto %s: %d barre, fino a %s"
          % (os.path.basename(EXT), len(out), str(out['time'].max())[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
