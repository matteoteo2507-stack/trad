"""Diagnostica live: esito ORB di OGGI su NAS100 con le regole v2. Fetch live da Dukascopy.

Cosa fa: scarica gli ultimi 4 giorni di M5 NAS100, isola la sessione odierna (ET),
costruisce l'opening range 09:30-10:00, cerca il break + conferma sul 2° livello (L),
applica il filtro ADX>=25, e simula ENTRY(retest)/SL/TP 1:3/BE@2R fino all'esito.
Stampa a video il piano e lo stato del trade del giorno. Nessun output persistito.

STATO: strumento DIAGNOSTICO/manuale, NON di produzione. Appartiene all'indagine
Opening-Range Breakout che è chiusa **NO-GO** (v1 e v2 su 14.5y, entrambi gli indici;
vedi commit `bc7aead` e i predecessori). L'holdout ha smascherato il "miglioramento"
v2 come non-stazionario (positivo solo post-2020). Tenuto come utility per ispezionare
a mano una giornata; non fa parte di alcuna strategia attiva. Condivide le regole/ADX
con `backtest_v2.py`.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from datetime import timezone

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from backtest import adx_series  # noqa: E402

import dukascopy_python as dk  # noqa: E402
import dukascopy_python.instruments as ins  # noqa: E402

BUFFER, RR, BE_AT = 10.0, 3.0, 2.0
OR_S, OR_E, EXP = 570, 600, 720   # 9:30, 10:00, 12:00 ET (minuti)


def main():
    end = dt.datetime.now(timezone.utc)
    start = end - dt.timedelta(days=4)
    df = dk.fetch(ins.INSTRUMENT_IDX_AMERICA_E_NQ_100, dk.INTERVAL_MIN_5, dk.OFFER_SIDE_BID, start, end)
    et = df.index.tz_convert("America/New_York")
    df = df.copy()
    df["etdate"] = et.strftime("%Y-%m-%d")
    df["etmin"] = et.hour * 60 + et.minute
    O, H, L, C = df["open"].values, df["high"].values, df["low"].values, df["close"].values
    ADX = adx_series(H, L, C)
    day = df["etdate"].iloc[-1]
    rows = [i for i in range(len(df)) if df["etdate"].iloc[i] == day]
    orr = [i for i in rows if OR_S <= df["etmin"].iloc[i] < OR_E]
    sess = [i for i in rows if OR_E <= df["etmin"].iloc[i] < EXP]
    print(f"=== NAS100 — {day} (ET) — ultimo prezzo {C[-1]:.1f} @ {et[-1].strftime('%H:%M ET')} ===")
    if len(orr) < 3:
        print("Opening range non ancora formato (sessione USA non aperta)."); return
    ORH = max(H[i] for i in orr); ORL = min(L[i] for i in orr)
    print(f"Opening range 09:30-10:00 ET:  ORH={ORH:.1f}  ORL={ORL:.1f}  (ampiezza {ORH-ORL:.1f} pt)")
    if not sess:
        print("Sessione post-10:00 non ancora iniziata."); return

    side = None
    for k, i in enumerate(sess):
        if C[i] < ORL:
            side, c0k = "SELL", k; break
        if C[i] > ORH:
            side, c0k = "BUY", k; break
    if side is None:
        print("Nessun break di ORH/ORL entro le 12:00 ET -> nessun trade."); return
    level = L[sess[c0k]] if side == "SELL" else H[sess[c0k]]
    jbk = None
    for k in range(c0k + 1, len(sess)):
        i = sess[k]
        if side == "SELL":
            if C[i] < level:
                jbk = k; break
            if L[i] < level:
                level = L[i]
        else:
            if C[i] > level:
                jbk = k; break
            if H[i] > level:
                level = H[i]
    print(f"Break {side} del range. Livello L (2° break) = {level:.1f}")
    if jbk is None:
        print("L non ancora rotto (nessuna conferma) -> in attesa / nessun trade."); return
    adxv = float(ADX[sess[jbk]])
    entry = level
    if side == "SELL":
        sl = ORL + BUFFER; risk = sl - entry; tp = entry - RR * risk; be = entry - BE_AT * risk
    else:
        sl = ORH - BUFFER; risk = entry - sl; tp = entry + RR * risk; be = entry + BE_AT * risk
    print(f"Conferma. ADX@conferma={adxv:.0f}  ({'PASSA' if adxv >= 25 else 'SOTTO soglia 25 -> filtro scarta'})")
    print(f"Piano: ENTRY(retest)={entry:.1f}  SL={sl:.1f}  TP(1:3)={tp:.1f}  BE@2R={be:.1f}  rischio={risk:.1f}pt")

    f = None
    for k in range(jbk + 1, len(sess)):
        i = sess[k]
        if (side == "SELL" and H[i] >= entry) or (side == "BUY" and L[i] <= entry):
            f = i; break
    if f is None:
        print("Pending NON riempito entro le 12:00 ET (nessun retest) -> nessun trade.")
        return
    print(f"Pending RIEMPITO al retest ({entry:.1f}).")
    be_on = False
    for j in range(f + 1, len(H)):
        if side == "SELL":
            if not be_on and L[j] <= be:
                be_on = True
            if H[j] >= (entry if be_on else sl):
                print(f"ESITO: {'BE (0R)' if be_on else 'STOP LOSS (-1R)'} colpito."); return
            if L[j] <= tp:
                print("ESITO: TAKE PROFIT (+3R) colpito."); return
        else:
            if not be_on and H[j] >= be:
                be_on = True
            if L[j] <= (entry if be_on else sl):
                print(f"ESITO: {'BE (0R)' if be_on else 'STOP LOSS (-1R)'} colpito."); return
            if H[j] >= tp:
                print("ESITO: TAKE PROFIT (+3R) colpito."); return
    print(f"ESITO: TRADE ANCORA APERTO {'(dopo BE)' if be_on else ''} — né TP né SL toccati finora.")


if __name__ == "__main__":
    main()
