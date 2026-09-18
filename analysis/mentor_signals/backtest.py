"""Replay dei segnali del mentore su prezzo XAUUSD REALE (M5) — hit-rate/R veri, de-biasati.

Legge signals.csv (parse.py) e li replaya sul feed reale M5 (analysis/trading-bot-eval/data/
XAU_spot_M5.csv), che copre ~2026-01-21 -> 2026-06-12 (grosso del periodo). Per ogni segnale:
  - fill all'`entry` se il prezzo lo tocca entro ENTRY_WINDOW; altrimenti non eseguito;
  - dall'entry, primo tocco tra SL e i vari TP entro MAX_HOLD;
  - ambiguita' intrabar (barra che tocca sia SL sia TP) gestita con DUE scenari:
    pessimistico (SL prima) e ottimistico (TP prima) -> bound onesti.
Metriche: win-rate simmetrica (+1R prima di -1R), expectancy uscendo a TP1 e a TP3 (R, dopo
costo), il tutto vs una **baseline a side casuale** (stessa geometria/tempi) per capire se la
DIREZIONE del mentore aggiunge valore o se l'oro ha solo trendato.

Uso: python analysis/mentor_signals/backtest.py
"""
from __future__ import annotations

import csv
import datetime as dt
import os
from datetime import datetime

import numpy as np

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# Feed ESTESO (fino a oggi). Il vecchio XAU_spot_M5.csv si ferma al 2026-06-12 e
# tagliava in silenzio gli ultimi mesi di segnali: era il default fino al 18/09.
M5 = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "XAU_spot_M5_ext.csv")
SIG = os.path.join(HERE, "signals.csv")

ENTRY_WINDOW = 72     # barre M5 (~6h) per il fill all'entry
MAX_HOLD = 576        # barre M5 (~48h) di holding max
COST_USD = 0.30       # costo round-trip (spread/slippage) in $ oro
SEED = 42

# Disallineamento fra l'orologio dell'export dei segnali (UTC+01:00, dichiarato
# dall'export stesso) e quello del feed M5 (ora server del broker, ~UTC+2).
#
# DOVE SI APPLICA (regola, 2026-09-18 sera): **una volta sola, al CARICAMENTO**.
# I segnali escono dai loader (`load_signals` qui, `to_engine` in oos_validation)
# gia' allineati al feed; `replay` e `market_replay` NON toccano piu' il timestamp.
#
# Perche' la regola esiste: fino a poche ore fa la correzione stava in `replay`,
# ma `to_engine` ne applicava gia' una propria -> ogni analisi che passava di li'
# (soglie di ritiro, OOS, report al socio) girava a **+2h**, un'ora troppo TARDI.
# Due posti che applicano la stessa correzione sono un difetto strutturale, non
# una svista: la correzione ha **un solo proprietario**, ed e' il loader.
# Verifica automatica in coverage.verifica(): lo scarto mediano
# |entry dichiarato - prezzo al ts| deve essere **minimo a shift aggiuntivo 0**.
TS_OFFSET_H = 1
TS_OFFSET = dt.timedelta(hours=TS_OFFSET_H)


def load_m5():
    t, hi, lo, cl = [], [], [], []
    with open(M5, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t.append(np.datetime64(r["time"][:19]))
                hi.append(float(r["high"])); lo.append(float(r["low"])); cl.append(float(r["close"]))
            except (ValueError, KeyError):
                continue
    return np.array(t), np.array(hi), np.array(lo), np.array(cl)


def market_replay(sig, T, HI, LO, CL, delay_bars):
    """Copia MANUALE: entra a mercato (close) delay_bars dopo il segnale, mantiene SL/TP
    ASSOLUTI del mentore -> mostra l'erosione da ritardo. Ritorna R (exit TP1, pess)."""
    i = int(np.searchsorted(T, sig["ts"])) + delay_bars
    if i >= len(T):
        return None
    entry = CL[i]
    sl, tp = sig["sl"], sig["tp1"]
    risk = abs(entry - sl)
    if risk <= 0:
        return None
    is_buy = sig["side"] == "BUY"
    # sanity: SL dal lato giusto
    if (is_buy and sl >= entry) or (not is_buy and sl <= entry):
        return None
    c = COST_USD / risk
    tpR = abs(tp - entry) / risk
    if is_buy:
        res, _ = _first_touch(HI, LO, i, tp, sl, "dn")     # pess: SL prima nei tie
        return (tpR - c) if res == "up" else (-1.0 - c if res == "dn" else 0.0)
    res, _ = _first_touch(HI, LO, i, sl, tp, "up")
    return (tpR - c) if res == "dn" else (-1.0 - c if res == "up" else 0.0)


def load_signals():
    out = []
    with open(SIG, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["complete"] != "True":
                continue
            try:
                out.append({
                    # allineato al feed QUI, una volta sola (vedi TS_OFFSET_H)
                    "ts": np.datetime64(r["ts"][:19])
                          + np.timedelta64(TS_OFFSET_H, "h"),
                    "side": r["side"],
                    "entry": float(r["entry"]), "sl": float(r["sl"]),
                    "tp1": float(r["tp1"]), "tp2": float(r["tp2"]) if r["tp2"] else None,
                    "tp3": float(r["tp3"]) if r["tp3"] else None})
            except (ValueError, KeyError):
                continue
    return out


def _first_touch(hi, lo, i0, up, dn, tie):
    """Primo indice in cui il prezzo tocca 'up' (>=) o 'dn' (<=). Ritorna ('up'|'dn'|None, idx).
    tie: se una barra tocca entrambi -> 'up' (ottimistico) o 'dn' (pessimistico)."""
    end = min(i0 + MAX_HOLD, len(hi))
    for j in range(i0, end):
        hu = hi[j] >= up
        hd = lo[j] <= dn
        if hu and hd:
            return (tie, j)
        if hu:
            return ("up", j)
        if hd:
            return ("dn", j)
    return (None, end - 1)


def replay(sig, T, HI, LO, side_override=None):
    """Ritorna dict esiti (pess/opt) o None se non eseguito / fuori copertura."""
    side = side_override or sig["side"]
    entry, sl = sig["entry"], sig["sl"]
    risk = abs(entry - sl)
    if risk <= 0:
        return None
    # Il timestamp arriva GIA' allineato dal loader (vedi TS_OFFSET_H): qui non si
    # tocca. Applicarlo di nuovo sposterebbe il fill un'ora piu' avanti del vero.
    i = int(np.searchsorted(T, sig["ts"]))
    if i >= len(T):
        return None
    # fill all'entry entro ENTRY_WINDOW
    fill = None
    for j in range(i, min(i + ENTRY_WINDOW, len(T))):
        if LO[j] <= entry <= HI[j]:
            fill = j; break
    if fill is None:
        return None

    c = COST_USD / risk  # costo in unita' di R
    is_buy = side == "BUY"
    out = {}
    # (a) simmetrica: +1R prima di -1R
    up = entry + risk if is_buy else entry  # per BUY il target = entry+risk (up), sl = entry-risk (dn)
    dn = entry - risk if is_buy else entry
    if is_buy:
        up_s, dn_s = entry + risk, sl
    else:
        up_s, dn_s = sl, entry - risk   # per SELL: profit se scende a entry-risk (dn), sl sopra (up)
    for tie, tag in ((("dn" if is_buy else "up"), "pess"), (("up" if is_buy else "dn"), "opt")):
        res, _ = _first_touch(HI, LO, fill, up_s, dn_s, tie)
        if res is None:
            win = None
        else:
            profit_side = "up" if is_buy else "dn"
            win = (res == profit_side)
        out[f"sym_{tag}"] = win

    # (b) expectancy uscendo a TP1 e TP3 (R netto), con SL
    for tpname in ("tp1", "tp3"):
        tp = sig[tpname]
        if tp is None:
            continue
        tpR = abs(tp - entry) / risk
        for tie_pess in (True, False):
            tie = ("dn" if is_buy else "up") if tie_pess else ("up" if is_buy else "dn")
            if is_buy:
                res, _ = _first_touch(HI, LO, fill, tp, sl, tie)
                profit = res == "up"
            else:
                res, _ = _first_touch(HI, LO, fill, sl, tp, tie)
                profit = res == "dn"
            if res is None:
                R = 0.0
            elif profit:
                R = tpR - c
            else:
                R = -1.0 - c
            out[f"{tpname}_{'pess' if tie_pess else 'opt'}"] = R
    return out


def _agg(vals):
    v = [x for x in vals if x is not None]
    return (np.mean(v), len(v)) if v else (float("nan"), 0)


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    T, HI, LO, CL = load_m5()
    sigs = load_signals()
    cov = [s for s in sigs if T[0] <= s["ts"] <= T[-1]]
    print(f"Segnali completi: {len(sigs)}  | dentro copertura M5 ({str(T[0])[:10]}..{str(T[-1])[:10]}): {len(cov)}")

    real = [replay(s, T, HI, LO) for s in cov]
    real = [r for r in real if r is not None]
    print(f"Eseguiti (fill entro {ENTRY_WINDOW*5//60}h): {len(real)}/{len(cov)}")

    def report(results, label):
        print(f"\n--- {label} (n eseguiti={len(results)}) ---")
        for tag in ("pess", "opt"):
            wr = _agg([r.get(f"sym_{tag}") for r in results])
            print(f"  [{tag}] win-rate simmetrica (+1R prima di -1R): {wr[0]*100:5.1f}%  (n={wr[1]})")
        for tpname in ("tp1", "tp3"):
            for tag in ("pess", "opt"):
                e = _agg([r.get(f"{tpname}_{tag}") for r in results])
                wins = _agg([1.0 if r.get(f"{tpname}_{tag}", -9) > 0 else 0.0 for r in results
                             if f"{tpname}_{tag}" in r])
                print(f"  [{tag}] exit {tpname.upper()}: E[R]={e[0]:+.3f}  hit%={wins[0]*100:4.0f}%  (n={e[1]})")

    report(real, "MENTORE (side reale)")

    # baseline: side casuale, stessa geometria/tempi
    rng = np.random.default_rng(SEED)
    base = []
    for s in cov:
        so = "BUY" if rng.random() < 0.5 else "SELL"
        r = replay(s, T, HI, LO, side_override=so)
        if r is not None:
            base.append(r)
    report(base, "BASELINE side casuale")

    # ---- sensibilita' al RITARDO di copia manuale (entra a mercato dopo N minuti) ----
    print("\n--- ROBUSTEZZA: ritardo di copia manuale (entry a mercato, SL/TP assoluti, exit TP1) ---")
    for dmin, db in ((0, 0), (5, 1), (15, 3), (30, 6), (60, 12)):
        rs = [market_replay(s, T, HI, LO, CL, db) for s in cov]
        rs = [x for x in rs if x is not None]
        e = np.mean(rs) if rs else float("nan")
        wr = np.mean([1.0 if x > 0 else 0.0 for x in rs]) * 100 if rs else float("nan")
        print(f"  ritardo {dmin:3d} min: E[R]={e:+.3f}  hit%={wr:4.0f}%  (n={len(rs)})")

    # ---- stabilita' mese per mese (win-rate simmetrica pess) ----
    print("\n--- STABILITA' mensile (win-rate simmetrica, pess) ---")
    by_month = {}
    for s, r in zip(cov, [replay(x, T, HI, LO) for x in cov]):
        if r is None or r.get("sym_pess") is None:
            continue
        m = str(s["ts"])[:7]
        by_month.setdefault(m, []).append(1.0 if r["sym_pess"] else 0.0)
    for m in sorted(by_month):
        v = by_month[m]
        print(f"  {m}: {np.mean(v)*100:5.1f}%  (n={len(v)})")

    print("\nNOTE: TP del mentore asimmetrici (TP1~+0.5R vs SL -1R) -> break-even richiede ~67% win.")
    print("Bound pess/opt = ordine intrabar SL-vs-TP non risolvibile su alcune barre M5.")
    print("Copertura M5 fino a 2026-06-12: gli ultimi ~4 mesi di segnali non sono replayati.")


if __name__ == "__main__":
    main()
