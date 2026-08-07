"""Validazione OOS dei segnali mentore — esegue la pre-registrazione del 2026-08-07.

Vedi docs/MENTOR_SIGNALS_OOS_PREREGISTRATION.md. Regole: motore di replay INVARIATO
(backtest.replay), parametri congelati, finestra = segnali MAI replayati dall'audit
(ts > fine copertura prezzi originale). Nessuna ritaratura.

Uso: python analysis/mentor_signals/oos_validation.py
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from core import quant_metrics as qm  # noqa: E402
import backtest as bt  # noqa: E402
import parse as pr  # noqa: E402

EXPORT = os.path.join(ROOT, "Messaggi tg aggiornati 07-08")
M5_EXT = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "XAU_spot_M5_ext.csv")
# fine della copertura prezzi usata dall'audit -> tutto cio' che segue e' OOS
OOS_FROM = np.datetime64("2026-06-12T22:55:00")

# --- CORREZIONE DI ALLINEAMENTO ORARIO (bug fix, non ritaratura) -----------------
# I timestamp dell'export Telegram sono UTC+01:00; la serie prezzi e' in ora server
# del broker (~UTC+2). Il confronto naive di backtest.py li tratta come lo stesso
# fuso. Offset determinato con un criterio INDIPENDENTE DAGLI ESITI: quello che
# minimizza lo scarto mediano |entry dichiarato - prezzo al timestamp|.
#     -1h: $16.34   0h: $10.53   +1h: $3.16 (min)   +2h: $7.15   +3h: $9.95
TZ_SHIFT_H = 1


def parse_export():
    """Riusa parse.parse_text (INVARIATO) sull'export nuovo."""
    rows = []
    for fn in sorted(os.listdir(EXPORT)):
        if not re.fullmatch(r"messages\d*\.html", fn):
            continue
        html = open(os.path.join(EXPORT, fn), encoding="utf-8", errors="ignore").read()
        last_ts = None
        for b in pr.MSG_SPLIT.split(html):
            mts = pr.TS_RE.search(b)
            if mts:
                last_ts = pr._iso(mts)
            mtx = pr.TEXT_RE.search(b)
            if not mtx:
                continue
            txt = pr._clean(mtx.group(1))
            if not txt:
                continue
            sig = pr.parse_text(txt)
            if sig is None or last_ts is None:
                continue
            sig["ts"] = last_ts
            sig["complete"] = sig["sl"] is not None and sig["tp1"] is not None
            rows.append(sig)
    return rows


def to_engine(rows):
    out = []
    for r in rows:
        if not r["complete"]:
            continue
        out.append({"ts": np.datetime64(r["ts"][:19]) + np.timedelta64(TZ_SHIFT_H, "h"),
                    "side": r["side"],
                    "entry": float(r["entry"]), "sl": float(r["sl"]),
                    "tp1": float(r["tp1"]),
                    "tp2": r["tp2"], "tp3": r["tp3"]})
    return out


def ci(vals, label, conf=0.95):
    v = np.asarray([x for x in vals if x is not None], float)
    if len(v) < 10:
        return None
    b = qm.bca_bootstrap_ci(v, metric=lambda x: float(np.mean(x)), conf=conf,
                            n_boot=5000, seed=bt.SEED)
    print(f"  {label:44} {v.mean():+7.3f}   BCa95=[{b['low']:+.3f}, {b['high']:+.3f}]  n={len(v)}")
    return b


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    bt.M5 = M5_EXT                       # serie estesa e validata (vedi prereg §2)
    T, HI, LO, CL = bt.load_m5()

    allrows = parse_export()
    sigs = to_engine(allrows)
    oos = [s for s in sigs if s["ts"] > OOS_FROM and T[0] <= s["ts"] <= T[-1]]

    print("=" * 88)
    print("VALIDAZIONE OOS — segnali mentore XAUUSD  (pre-registrazione 2026-08-07)")
    print("=" * 88)
    print(f"Prezzi M5    : {str(T[0])[:16]} -> {str(T[-1])[:16]}  ({len(T)} barre)")
    print(f"Segnali export: {len(allrows)} parsati, {len(sigs)} completi (SL+TP1)")
    print(f"FINESTRA OOS (ts > {str(OOS_FROM)[:16]}): {len(oos)} segnali completi")
    if oos:
        print(f"  periodo: {str(oos[0]['ts'])[:16]} -> {str(oos[-1]['ts'])[:16]}")
        nb = sum(1 for s in oos if s["side"] == "BUY")
        print(f"  BUY={nb}  SELL={len(oos)-nb}")

    # --- sanity check di riconciliazione (prereg §3: fuso orario) ---
    ent = np.array([s["entry"] for s in oos], float)
    w = (T > OOS_FROM)
    print(f"\nRICONCILIAZIONE  entry dichiarati: {ent.min():.0f}..{ent.max():.0f}   "
          f"prezzo reale nella finestra: {LO[w].min():.0f}..{HI[w].max():.0f}")
    if ent.min() < LO[w].min() - 50 or ent.max() > HI[w].max() + 50:
        print("  *** ATTENZIONE: entry fuori dal range reale -> possibile disallineamento di fuso")
    else:
        print("  OK: gli entry cadono dentro il range reale del periodo")

    if len(oos) < 50:
        print(f"\n>>> VERDETTO: INSUFFICIENT DATA ({len(oos)} < 50 segnali)")
        return

    # --- replay: mentore vs baseline side casuale (appaiati sugli stessi segnali) ---
    rng = np.random.default_rng(bt.SEED)
    pairs = []
    for s in oos:
        rm = bt.replay(s, T, HI, LO)
        so = "BUY" if rng.random() < 0.5 else "SELL"
        rb = bt.replay(s, T, HI, LO, side_override=so)
        if rm is not None and rb is not None:
            pairs.append((rm, rb))
    print(f"\nEseguiti (fill entro {bt.ENTRY_WINDOW*5//60}h dall'entry): {len(pairs)}/{len(oos)}")
    if len(pairs) < 50:
        print(f"\n>>> VERDETTO: INSUFFICIENT DATA ({len(pairs)} eseguiti < 50)")
        return

    print("\n" + "-" * 88)
    print("METRICA PRIMARIA — win-rate simmetrica (+1R prima di -1R), scenario PESSIMISTICO")
    print("-" * 88)
    wm = [1.0 if a["sym_pess"] else 0.0 for a, b in pairs if a["sym_pess"] is not None]
    wb = [1.0 if b["sym_pess"] else 0.0 for a, b in pairs if b["sym_pess"] is not None]
    diff = [(1.0 if a["sym_pess"] else 0.0) - (1.0 if b["sym_pess"] else 0.0)
            for a, b in pairs if a["sym_pess"] is not None and b["sym_pess"] is not None]
    print(f"  MENTORE  win-rate : {100*np.mean(wm):5.1f}%   (n={len(wm)})   [audit: 67-72%]")
    print(f"  RANDOM   win-rate : {100*np.mean(wb):5.1f}%   (n={len(wb)})   [audit: 32%]")
    print()
    d = ci(diff, "DIFFERENZA (mentore - random), appaiata")

    print("\n" + "-" * 88)
    print("METRICA SECONDARIA — E[R] uscendo a TP1, dopo costi ($0.30)")
    print("-" * 88)
    e_p = ci([a.get("tp1_pess") for a, _ in pairs], "E[R] TP1 mentore  (pessimistico)")
    ci([a.get("tp1_opt") for a, _ in pairs], "E[R] TP1 mentore  (ottimistico)")
    ci([b.get("tp1_pess") for _, b in pairs], "E[R] TP1 random   (pessimistico)")
    hit = [1.0 if a.get("tp1_pess", -9) > 0 else 0.0 for a, _ in pairs if "tp1_pess" in a]
    print(f"  {'TP1 hit% (pessimistico)':44} {100*np.mean(hit):6.1f}%              [audit: ~85%]")

    print("\n" + "-" * 88)
    print("STABILITA' mensile (win-rate simmetrica pess)")
    print("-" * 88)
    bym = {}
    for s in oos:
        r = bt.replay(s, T, HI, LO)
        if r is None or r.get("sym_pess") is None:
            continue
        bym.setdefault(str(s["ts"])[:7], []).append(1.0 if r["sym_pess"] else 0.0)
    for m in sorted(bym):
        print(f"  {m}: {100*np.mean(bym[m]):5.1f}%   (n={len(bym[m])})")

    # --- VERDETTO secondo le soglie PRE-REGISTRATE ---
    print("\n" + "=" * 88)
    print("VERDETTO (soglie fissate nella pre-registrazione, prima di vedere i dati)")
    print("=" * 88)
    batte = d is not None and d["low"] > 0
    er_pos = e_p is not None and e_p["point"] > 0
    print(f"  lower bound BCa 95% della differenza > 0 ?  {'SI' if batte else 'NO'}"
          f"   ({d['low']:+.3f})" if d else "  differenza: n/d")
    print(f"  E[R] TP1 puntuale > 0 (dopo costi)      ?  {'SI' if er_pos else 'NO'}"
          f"   ({e_p['point']:+.3f})" if e_p else "  E[R]: n/d")
    print()
    if batte and er_pos:
        print("  >>> CONFERMATO — l'edge regge fuori campione.")
    elif batte:
        print("  >>> DEGRADATO — direzione reale ma E[R] <= 0: non tradabile con questa geometria.")
    else:
        print("  >>> FALSIFICATO — non distinguibile dal random. Traccia da archiviare.")


if __name__ == "__main__":
    main()
