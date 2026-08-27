"""RIESAME del verdetto 2026-08-14 — "l'entrata e' peggio del random" (gap -0,399R).

Perche' esiste. L'audit del fill d'ingresso del 2026-08-27 (`entry_fill_audit.py`) ha
mostrato che il motore FADE concede il fill al prezzo `entry` anche quando il mercato
lo ha gia' oltrepassato, cioe' a un prezzo non ottenibile. `excursion.py` — il motore
che ha prodotto il verdetto del 14/08 — usa **lo stesso identico fill**, ma il suo
controllo random entra a `e = C[k]`, la chiusura di una barra: un prezzo sempre
disponibile. Il fantasma sta da UN SOLO LATO del confronto.

E il segno si rovescia rispetto al fade. La continuazione COMPRA il ritracciamento:
se il prezzo e' gia' sceso sotto `entry`, riempire a `entry` significa **pagare piu'
del mercato** -> il braccio reale e' PENALIZZATO. (Il fade vende allo stesso livello e
ne e' invece avvantaggiato.) Stesso artefatto, due segni opposti: e' il motivo per cui
il 14/08 sembrava "convergere" col +0,35R del fade.

Seconda asimmetria, indipendente e nella stessa direzione. Il braccio reale cammina da
`j = f` (`excursion.py:87`), quindi la barra di fill puo' stopparlo con il proprio range
**precedente all'ingresso**; il random parte da `k+1` (`excursion.py:180`), quindi la sua
barra d'ingresso non puo' mai stopparlo. Con SL a 0,286 di ampiezza e' un vantaggio
sistematico per il random.

Cosa misura questo file: il gap reale-vs-random dopo aver tolto UNA per volta le due
asimmetrie, per capire quanta parte dei -0,399R sia artefatto e quanta sopravviva.

  BASE      : com'e' oggi (fill fantasma + cammino da f)
  SYM       : cammino da f+1, come il random -> toglie l'asimmetria 2
  SKIP      : non entra se il livello e' gia' oltrepassato alla prima barra azionabile
  SKIP+SYM  : entrambe le correzioni
  random    : invariato (baseline registrato)
  random@k  : random che cammina dalla barra d'ingresso, simmetrico a BASE

Classificazione: rianalisi descrittiva di un test gia' chiuso, nessuna regola toccata,
holdout non aperto -> **nessun trial consumato** (STRATEGY_LIFECYCLE §3), stessa
classificazione che il 14/08 si era gia' dato.

Uso:  python analysis/nxt/excursion_recheck.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.nxt import backtest as nxt          # noqa: E402
from analysis.nxt import excursion as ex          # noqa: E402

M_RANDOM = 3


def real_terminal(leg, O, H, L, C, sym, honest, sym_walk):
    """R terminale del braccio reale. `honest`: se True salta i fill non ottenibili.

    `sym_walk`: se True il cammino parte da f+1 (come il random), togliendo alla barra
    di fill il potere di stoppare col range pre-ingresso.
    """
    side, hi, lo, rng = leg["side"], leg["hi"], leg["lo"], leg["rng"]
    b, cb = leg["end_idx"], leg["conf"]
    if side == "BUY":
        entry = hi - nxt.ENTRY_FIB * rng
        sl = hi - nxt.SL_FIB * rng
        risk = entry - sl
    else:
        entry = lo + nxt.ENTRY_FIB * rng
        sl = lo + nxt.SL_FIB * rng
        risk = sl - entry
    if risk <= 0:
        return None

    fa = cb + 1                       # frattale noto alla CHIUSURA di cb
    if fa >= len(H):
        return None
    # gia' oltrepassato? la continuazione COMPRA scendendo (BUY-leg) / VENDE salendo
    already = (O[fa] < entry) if side == "BUY" else (O[fa] > entry)
    if honest and already:
        return None

    f = None                          # fill identico a excursion.py
    for j in range(fa, min(b + 1 + nxt.FILL_WINDOW, len(H))):
        if side == "BUY":
            if L[j] <= sl:
                if L[j] <= entry:
                    f = j
                break
            if L[j] <= entry:
                f = j
                break
        else:
            if H[j] >= sl:
                if H[j] >= entry:
                    f = j
                break
            if H[j] >= entry:
                f = j
                break
    if f is None:
        return None

    start = f + 1 if sym_walk else f
    last = min(f + nxt.MAX_HOLD, len(H)) - 1
    if last <= start:
        return None
    terminal = np.nan
    for j in range(start, last + 1):
        hit_sl = (L[j] <= sl) if side == "BUY" else (H[j] >= sl)
        if hit_sl:
            terminal = -1.0
            break
        if j == last:
            terminal = ((C[j] - entry) / risk if side == "BUY" else (entry - C[j]) / risk)
    if not np.isfinite(terminal):
        return None
    cost_R = nxt.SPREAD.get(sym, 0.0) / risk
    return {"asset": sym, "side": side, "risk": risk, "entry_idx": f,
            "already": bool(already), "R_term": terminal - cost_R}


def run():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:
        pass
    variants = {"BASE": (False, False), "SYM": (False, True),
                "SKIP": (True, False), "SKIP+SYM": (True, True)}
    real = {k: [] for k in variants}
    rnd, rnd_k = [], []
    gen = np.random.default_rng(nxt.SEED)

    for sym in nxt.ASSETS:
        d = nxt.load_h1(sym)
        O = d["open"].values
        H, L, C = d["high"].values, d["low"].values, d["close"].values
        yrs = d["time"].dt.year.values
        A = nxt.atr(H, L, C)
        legs = nxt.build_legs(nxt.zigzag(H, L), A)
        by_year = {y: np.flatnonzero(yrs == y) for y in np.unique(yrs)}
        for lg in legs:
            base = None
            for name, (honest, sw) in variants.items():
                r = real_terminal(lg, O, H, L, C, sym, honest, sw)
                if r is None:
                    continue
                r["legid"] = "%s:%d" % (sym, lg["end_idx"])
                r["year"] = int(yrs[r["entry_idx"]])
                real[name].append(r)
                if name == "BASE":
                    base = r
            if base is None:
                continue
            for _ in range(M_RANDOM):           # baseline risk-matched, come il 14/08
                pool = by_year[base["year"]]
                k = int(gen.choice(pool))
                if k + 2 >= len(H):
                    continue
                e = C[k]
                s = e - base["risk"] if base["side"] == "BUY" else e + base["risk"]
                a = ex.walk_from(k + 1, e, s, base["side"], H, L, C, sym)
                if a is not None:
                    a["legid"], a["year"] = base["legid"], base["year"]
                    rnd.append(a)
                bk = ex.walk_from(k, e, s, base["side"], H, L, C, sym)
                if bk is not None:
                    bk["legid"], bk["year"] = base["legid"], base["year"]
                    rnd_k.append(bk)

    dfs = {k: pd.DataFrame(v) for k, v in real.items()}
    dr, drk = pd.DataFrame(rnd), pd.DataFrame(rnd_k)

    print("=" * 84)
    print("RIESAME 2026-08-14 — \"l'entrata e' peggio del random\"")
    print("=" * 84)
    print("\nvalore registrato il 14/08:  reale -0,405  ·  random -0,005  ·  gap -0,399")
    print("                             [CI cluster -0,493; -0,308]\n")
    lo, hi = ex.cluster_ci(dr, "R_term")
    print("  %-10s n=%6d  R_term = %+.3f   [%+.3f; %+.3f]" % ("random", len(dr),
                                                              dr["R_term"].mean(), lo, hi))
    lo, hi = ex.cluster_ci(drk, "R_term")
    print("  %-10s n=%6d  R_term = %+.3f   [%+.3f; %+.3f]  (cammina dalla barra d'ingresso)"
          % ("random@k", len(drk), drk["R_term"].mean(), lo, hi))
    print()
    for name in ("BASE", "SYM", "SKIP", "SKIP+SYM"):
        df = dfs[name]
        if df.empty:
            continue
        lo, hi = ex.cluster_ci(df, "R_term")
        ref = drk if "SYM" not in name else dr    # confronto a convenzione OMOGENEA
        refn = "random@k" if "SYM" not in name else "random"
        gap = df["R_term"].mean() - ref["R_term"].mean()
        print("  %-10s n=%6d  R_term = %+.3f   [%+.3f; %+.3f]   gap vs %-9s = %+.3f"
              % (name, len(df), df["R_term"].mean(), lo, hi, refn, gap))

    b = dfs["BASE"]
    print("\n  fill non ottenibili nel braccio reale: %d / %d = %.1f%%"
          % (int(b["already"].sum()), len(b), 100 * b["already"].mean()))
    print("  R_term dei soli fill NON ottenibili : %+.3f" % b[b["already"]]["R_term"].mean())
    print("  R_term dei soli fill ottenibili     : %+.3f" % b[~b["already"]]["R_term"].mean())


if __name__ == "__main__":
    run()
