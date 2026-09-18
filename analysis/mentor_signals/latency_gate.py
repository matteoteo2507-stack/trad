"""C5 — la soglia anti-ritardo del copier, scelta dai dati invece che a numero tondo.

Usa `bt.TS_OFFSET` (fix 2026-09-18: i timestamp dei segnali erano indietro di 1h).

Il problema, che e' piu' grande di una soglia
---------------------------------------------
Tutti i numeri del binario mentore (win-rate OOS 63%, E[R] +0,194, e le soglie di
ritiro fissate il 2026-09-18) vengono dal **replay**, che riempie **esattamente a
`entry`** aspettando fino a 6 ore che il prezzo ci torni.

Il copier vero non fa questo. `signal_copier/executor.py` piazza `order_type="market"`
sul trigger "NOW" del canale, e i livelli arrivano ~1 minuto dopo. Quindi:

    replay  : ordine pendente a `entry`, fill al prezzo dichiarato
    copier  : ordine a mercato, fill al prezzo che c'e' in quel momento

**Sono due esecuzioni diverse**, ed e' la stessa domanda che sul FADE e' costata due mesi:
*il fill modellato e' ottenibile?* Qui la risposta non e' ovvia come li' — il mentore entra
a mercato anche lui e pubblica il suo prezzo, quindi `entry` dovrebbe essere vicino al
mercato del suo istante. Il divario e' la **latenza fra il suo ingresso e il nostro**, ed
e' esattamente cio' che `max_slippage_pips` dovrebbe governare.

Oggi quel parametro vale **20 pip**, che e' un numero tondo mai misurato.

Cosa misura questo script
-------------------------
Per ogni segnale, invece del fill a `entry`:
  - fill al **prezzo di mercato** dopo un ritardo di k barre M5 (k = 0, 1, 2, 3),
  - rischio normalizzato su `|entry - sl|`, che e' cio' su cui il copier **dimensiona**
    (`suggested_lots`): se riempiamo peggio, il rischio reale supera l'1% previsto e il
    rendimento in R peggiora. E' la distinzione r_unit / risk di `core.resolve_trade`.
  - esito risolto con la primitiva unica, convenzione di riferimento.

Poi taglia il campione a varie soglie di scostamento e riporta E[R] e trade superstiti,
separando lo scostamento **sfavorevole** da quello **favorevole**: non e' detto che vadano
trattati allo stesso modo, e il gate attuale li tratta uguali.

    python analysis/mentor_signals/latency_gate.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.mentor_signals import backtest as bt        # noqa: E402
from core import quant_metrics as qm                      # noqa: E402
from core.resolve_trade import FillConvention, resolve_trade  # noqa: E402
from notifiers._pip_table import price_delta_pips         # noqa: E402

SYM = "XAUUSD"
RITARDI = (0, 1, 2, 3)            # barre M5 di ritardo (0 = chiusura della barra del segnale)
SOGLIE = (5, 10, 15, 20, 30, 50, 10_000)
MAX_HOLD = 288                    # 24h in barre M5
CONV = FillConvention(fill_bar_can_resolve=True, tie="pess",
                      gap_beyond_stop=True, on_timeout="mark")


def costruisci(ritardo):
    """Per ogni segnale: fill a mercato dopo `ritardo` barre, R risolto dalla primitiva."""
    T, HI, LO, CL = bt.load_m5()
    OP = CL  # il feed non espone l'open: la chiusura della barra e' il prezzo agibile
    out = []
    for s in bt.load_signals():
        entry, sl = s["entry"], s["sl"]
        tp1 = s.get("tp1")
        if not tp1 or entry == sl:
            continue
        r_unit = abs(entry - sl)
        # ts gia' allineato da bt.load_signals() (vedi bt.TS_OFFSET_H)
        i = int(np.searchsorted(T, s["ts"])) + ritardo
        if i >= len(T):
            continue
        fill = float(CL[i])
        long = s["side"] == "BUY"
        # scostamento con segno: positivo = siamo entrati PEGGIO del mentore
        sfav = (fill - entry) if long else (entry - fill)
        slip_pips = price_delta_pips(SYM, entry, fill)
        cost_R = bt.COST_USD / r_unit
        res = resolve_trade(OP, HI, LO, CL, i, fill=fill, sl=sl, tp=tp1, long=long,
                            r_unit=r_unit, max_hold=MAX_HOLD, cost_R=cost_R, conv=CONV)
        if res is None:
            continue
        out.append({"R": res.r, "slip": slip_pips,
                    "sfav_pips": slip_pips * (1 if sfav > 0 else -1),
                    "esito": res.outcome})
    return out


def sintesi(R):
    R = np.asarray(R, dtype=float)
    if len(R) < 30:
        return "n=%-4d  campione troppo piccolo" % len(R)
    ci = qm.bca_bootstrap_ci(R, np.mean, conf=0.95, n_boot=2000, seed=42)
    return ("n=%-4d  E[R]=%+.3f  BCa95 [%+.3f ; %+.3f]"
            % (len(R), R.mean(), ci["low"], ci["high"]))


def main() -> int:
    print("C5 - SOGLIA ANTI-RITARDO DEL COPIER, misurata")
    print("=" * 78)
    print("Fill a MERCATO (come fa il copier), non a `entry` (come fa il replay).")
    print("R normalizzato su |entry-sl|, cioe' su cui il copier dimensiona i lotti.\n")

    base = None
    for k in RITARDI:
        dati = costruisci(k)
        R = np.array([d["R"] for d in dati])
        slip = np.array([d["slip"] for d in dati])
        sf = np.array([d["sfav_pips"] for d in dati])
        if base is None:
            base = dati
        print("--- ritardo %d barre M5 (~%d min) ---" % (k, k * 5))
        print("   tutti i segnali:            %s" % sintesi(R))
        print("   scostamento: mediana %.1f pip, 90esimo pct %.1f, max %.0f"
              % (np.median(slip), np.percentile(slip, 90), slip.max()))
        print("   sfavorevole nel %.0f%% dei casi" % (100 * (sf > 0).mean()))
        print()

    print("=" * 78)
    print("EFFETTO DELLA SOGLIA (ritardo 1 barra ~5 min, lo scenario realistico)")
    print("=" * 78)
    dati = costruisci(1)
    R = np.array([d["R"] for d in dati])
    slip = np.array([d["slip"] for d in dati])
    sf = np.array([d["sfav_pips"] for d in dati])
    tot = len(R)
    print("%-12s %7s %9s  %s" % ("soglia", "tenuti", "% tenuti", "E[R] dei tenuti"))
    for s in SOGLIE:
        m = slip <= s
        et = "nessuna" if s > 1000 else "%d pip" % s
        print("%-12s %7d %8.0f%%  %s" % (et, m.sum(), 100 * m.mean(), sintesi(R[m])))
    print()

    print("SCOSTAMENTO SFAVOREVOLE contro FAVOREVOLE (il gate oggi li tratta uguali)")
    for et, m in (("favorevole (entriamo meglio)", sf <= 0),
                  ("sfavorevole (entriamo peggio)", sf > 0)):
        print("   %-32s %s" % (et, sintesi(R[m])))
    print()
    for s in (10, 20, 30):
        m = sf > s
        if m.sum() >= 30:
            print("   solo sfavorevole oltre %2d pip:   %s" % (s, sintesi(R[m])))
    print()

    print("=" * 78)
    print("GATE ASIMMETRICO: soglia SOLO sullo scostamento sfavorevole")
    print("=" * 78)
    print("Il gate di oggi (`max_slippage_pips`) guarda il valore ASSOLUTO e quindi")
    print("scarta anche i segnali in cui il mercato si e' mosso A NOSTRO FAVORE, che")
    print("sono quelli che rendono di piu'. Qui la stessa soglia si applica solo al")
    print("lato sfavorevole: il favorevole si tiene sempre.\n")
    print("%-14s %7s %9s  %s" % ("soglia sfav.", "tenuti", "% tenuti", "E[R] dei tenuti"))
    for s in SOGLIE:
        if s > 1000:
            continue
        m = (sf <= 0) | (sf <= s)
        print("%-14s %7d %8.0f%%  %s" % ("%d pip" % s, m.sum(), 100 * m.mean(),
                                         sintesi(R[m])))
    print()

    print("CONFRONTO col modello del replay (fill a `entry`, attesa fino a 6h)")
    T, HI, LO, CL = bt.load_m5()
    Rrep = []
    for s in bt.load_signals():
        r = bt.replay(s, T, HI, LO)
        if r is not None and r.get("tp1_pess") is not None:
            Rrep.append(r["tp1_pess"])
    print("   replay (fill a entry):       %s" % sintesi(Rrep))
    print("   copier (fill a mercato +5m): %s" % sintesi(R))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
