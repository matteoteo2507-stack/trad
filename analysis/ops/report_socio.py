"""Resoconto per il socio — testo semplice, copiabile in WhatsApp.

Niente tabelle markdown (WhatsApp non le rende). Tre strategie, con la granularita'
che ha senso per ciascuna:
  - nxt_fade  : backtest 14 anni -> PER ANNO (175 mesi sarebbero illeggibili in chat)
  - orb_nasdaq: backtest 14.5 anni -> PER ANNO
  - mentore   : audit + validazione OOS su 2026 -> PER MESE (il periodo e' corto)

Uso: python analysis/ops/report_socio.py > report_socio.txt
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)

# Tre moduli distinti si chiamano tutti `backtest.py` (nxt, opening_range,
# mentor_signals): senza isolamento il primo importato vince e gli altri esplodono.
_DIRS = {"nxt": os.path.join(ROOT, "analysis", "nxt"),
         "orb": os.path.join(ROOT, "analysis", "opening_range"),
         "mentor": os.path.join(ROOT, "analysis", "mentor_signals")}
_COLLIDE = ("backtest", "backtest_v2", "closure", "consistency", "parse",
            "oos_validation", "reaction")


def _use(which):
    """Rende importabile SOLO il pacchetto richiesto, ripulendo i moduli in collisione."""
    for m in _COLLIDE:
        sys.modules.pop(m, None)
    for d in _DIRS.values():
        while d in sys.path:
            sys.path.remove(d)
    sys.path.insert(0, _DIRS[which])


def sez(t):
    print("\n" + "-" * 34)
    print(t)
    print("-" * 34)


def nxt_fade():
    _use('nxt')
    import consistency as cs
    df = cs.collect()
    df["anno"] = pd.to_datetime(df["exit_time"]).dt.year
    print("\n*NXT FADE (mean-reversion contro-trend)*")
    print("Backtest: 6 strumenti, H1, 2012-2026")
    print(f"Trade: {len(df)}  |  Win: {100*(df['outcome']=='TP').mean():.1f}%  "
          f"(pareggio a 1:3 = 25%)")
    print(f"Media per trade: {df['R'].mean():+.3f}R dopo costi")
    print("Regge anche a 3x i costi: +0.24R")
    print("\nPer anno (media R per trade / n. trade):")
    ok = 0
    for a, g in df.groupby("anno"):
        seg = "+" if g["R"].mean() > 0 else "-"
        ok += g["R"].mean() > 0
        print(f"  {a}  {seg}{abs(g['R'].mean()):.2f}R   n={len(g)}")
    print(f"\nAnni in positivo: {ok}/{df['anno'].nunique()}")
    print("Per strumento (tutti positivi):")
    for s, g in df.groupby("asset"):
        print(f"  {s:11} {g['R'].mean():+.2f}R   n={len(g)}")


def orb():
    _use('orb')
    import backtest_v2 as b2
    print("\n*ORB NASDAQ (breakout apertura USA)*")
    print("Backtest: NAS100 e SPX500, M5, 2012-2026 (dati Dukascopy)")
    for sym in ("NAS100", "SPX500"):
        try:
            tr = b2.run(sym)
        except Exception as e:
            print(f"  {sym}: dati non disponibili ({e})")
            continue
        d = pd.DataFrame(tr)
        d = d[d["adx"] >= 25] if "adx" in d.columns else d
        col = "R_pess" if "R_pess" in d.columns else "R"
        print(f"\n{sym}: {len(d)} trade  |  Win: {100*(d[col]>0).mean():.1f}%  "
              f"|  Media: {d[col].mean():+.3f}R")
        print("Per anno:")
        ok = 0
        for a, g in d.groupby("year"):
            seg = "+" if g[col].mean() > 0 else "-"
            ok += g[col].mean() > 0
            print(f"  {a}  {seg}{abs(g[col].mean()):.2f}R   n={len(g)}")
        print(f"Anni in positivo: {ok}/{d['year'].nunique()}")


def mentore():
    _use('mentor')
    import numpy as _np
    import backtest as mb
    import oos_validation as ov
    mb.M5 = ov.M5_EXT
    T, HI, LO, CL = mb.load_m5()
    sig = ov.to_engine(ov.parse_export())
    sig = [s for s in sig if T[0] <= s["ts"] <= T[-1]]
    print("\n*SEGNALI MENTORE XAUUSD (il copier)*")
    print("Non e' un backtest nostro: e' l'audit dei suoi segnali reali")
    print("rigiocati sul prezzo vero dell'oro (M5).")
    bym = defaultdict(list)
    byr = defaultdict(list)
    for s in sig:
        r = mb.replay(s, T, HI, LO)
        if r is None or r.get("sym_pess") is None:
            continue
        m = str(s["ts"])[:7]
        bym[m].append(1.0 if r["sym_pess"] else 0.0)
        if r.get("tp1_pess") is not None:
            byr[m].append(r["tp1_pess"])
    tot = [v for m in bym for v in bym[m]]
    allr = [v for m in byr for v in byr[m]]
    print(f"\nSegnali rigiocati: {len(tot)}")
    print(f"Direzione giusta: {100*_np.mean(tot):.1f}%  (un lato a caso: ~35%)")
    print(f"Media per trade: {_np.mean(allr):+.3f}R dopo costi")
    print("\nPer mese (direzione giusta / n. segnali):")
    for m in sorted(bym):
        print(f"  {m}  {100*_np.mean(bym[m]):.0f}%   n={len(bym[m])}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    nxt_fade()
    orb()
    mentore()


if __name__ == "__main__":
    main()
