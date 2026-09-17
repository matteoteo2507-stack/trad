"""La primitiva riproduce le implementazioni originali, o non serve a niente.

Ogni test qui sotto ricopia la logica di uno dei quattro `resolve` storici e verifica
che `core.resolve_trade` dia lo STESSO numero su migliaia di percorsi casuali, scelta
la convenzione giusta. Senza questa prova la primitiva sarebbe solo una quinta
convenzione, cioe' il problema che doveva risolvere.

    python core/tests/test_resolve_trade.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.resolve_trade import FillConvention, resolve_trade  # noqa: E402

MAX_HOLD = 40
RR = 3.0
BE_AT = 2.0


def percorso(rng, n=120, p0=100.0, vol=0.6):
    """OHLC casuale ma coerente (high >= max(open,close), low <= min(open,close))."""
    c = p0 + np.cumsum(rng.normal(0, vol, n))
    o = np.empty(n)
    o[0] = p0
    o[1:] = c[:-1] + rng.normal(0, vol / 3, n - 1)   # gap fra chiusura e apertura
    hi = np.maximum(o, c) + np.abs(rng.normal(0, vol, n))
    lo = np.minimum(o, c) - np.abs(rng.normal(0, vol, n))
    return o, hi, lo, c


# --- 1 e 2: analysis/nxt/backtest.py e analysis/nxt/closure.py -----------------
def originale_nxt(H, L, f, entry, sl, tp, be, long, pess):
    """Copia letterale: barra di fill risolve, niente gap, timeout -> scartato."""
    be_on = False
    sl_cur = sl
    for j in range(f, min(f + MAX_HOLD, len(H))):
        if long:
            if not be_on and H[j] >= be:
                be_on = True
                sl_cur = entry
            hit_sl = L[j] <= sl_cur
            hit_tp = H[j] >= tp
        else:
            if not be_on and L[j] <= be:
                be_on = True
                sl_cur = entry
            hit_sl = H[j] >= sl_cur
            hit_tp = L[j] <= tp
        if hit_sl and hit_tp:
            return ("SL" if pess else "TP"), be_on
        if hit_sl:
            return "SL", be_on
        if hit_tp:
            return "TP", be_on
    return None, be_on


def test_nxt():
    rng = np.random.default_rng(20260917)
    visti = {"TP": 0, "SL": 0, "BE": 0, "drop": 0}
    for _ in range(4000):
        O, H, L, C = percorso(rng)
        long = bool(rng.integers(2))
        f = int(rng.integers(0, 60))
        entry = float(C[f])
        risk = float(abs(rng.normal(0, 0.8))) + 0.3
        sl = entry - risk if long else entry + risk
        tp = entry + RR * risk if long else entry - RR * risk
        be = entry + BE_AT * risk if long else entry - BE_AT * risk
        for pess in (True, False):
            esito, be_on = originale_nxt(H, L, f, entry, sl, tp, be, long, pess)
            atteso = (None if esito is None
                      else (RR if esito == "TP" else (0.0 if be_on else -1.0)))

            got = resolve_trade(
                O, H, L, C, f, fill=entry, sl=sl, tp=tp, long=long,
                r_unit=risk, max_hold=MAX_HOLD, be_at=BE_AT,
                conv=FillConvention(fill_bar_can_resolve=True,
                                    tie="pess" if pess else "opt",
                                    gap_beyond_stop=False,
                                    on_timeout="drop"),
            )
            if atteso is None:
                assert got is None, "originale scarta, primitiva no"
                visti["drop"] += 1
                continue
            assert got is not None, "originale risolve, primitiva scarta"
            assert abs(got.r - atteso) < 1e-9, (
                "R diverso: primitiva %.6f vs originale %.6f (%s)"
                % (got.r, atteso, got.outcome))
            visti[got.outcome] += 1
    print("  nxt/backtest.py + nxt/closure.py  OK   esiti:", visti)


# --- 3: analysis/nxt/entry_fill_audit.py --------------------------------------
def originale_audit(O, H, L, C, f, fill, sl, tp, long, r_int, cost_R,
                    pess, fill_bar_stops):
    risk = abs(fill - sl)
    if risk <= 0:
        return None
    sgn = 1.0 if long else -1.0
    be = fill + BE_AT * risk if long else fill - BE_AT * risk
    be_on, sl_cur = False, sl
    start = f if fill_bar_stops else f + 1
    end = min(f + MAX_HOLD, len(H))
    if start >= end:
        return None
    for j in range(start, end):
        if not be_on and ((H[j] >= be) if long else (L[j] <= be)):
            be_on, sl_cur = True, fill
        hit_sl = (L[j] <= sl_cur) if long else (H[j] >= sl_cur)
        hit_tp = (H[j] >= tp) if long else (L[j] <= tp)
        if hit_sl and hit_tp:
            hit_tp, hit_sl = (False, True) if pess else (True, False)
        if hit_sl:
            jumped = (O[j] < sl_cur) if long else (O[j] > sl_cur)
            if j == f:
                jumped = False
            px = O[j] if jumped else sl_cur
            return sgn * (px - fill) / r_int - cost_R
        if hit_tp:
            return sgn * (tp - fill) / r_int - cost_R
    return sgn * (C[end - 1] - fill) / r_int - cost_R


def test_audit():
    rng = np.random.default_rng(1312)
    visti = {"TP": 0, "SL": 0, "BE": 0, "TIMEOUT": 0}
    for _ in range(4000):
        O, H, L, C = percorso(rng)
        long = bool(rng.integers(2))
        f = int(rng.integers(0, 60))
        # fill DIVERSO dall'entry teorica: e' il caso che le altre non sanno trattare
        r_int = float(abs(rng.normal(0, 0.8))) + 0.3
        entry = float(C[f])
        fill = entry + float(rng.normal(0, 0.3))
        sl = entry - r_int if long else entry + r_int
        tp = entry + RR * r_int if long else entry - RR * r_int
        cost_R = float(abs(rng.normal(0, 0.02)))
        for pess in (True, False):
            for fbs in (True, False):
                atteso = originale_audit(O, H, L, C, f, fill, sl, tp, long,
                                         r_int, cost_R, pess, fbs)
                got = resolve_trade(
                    O, H, L, C, f, fill=fill, sl=sl, tp=tp, long=long,
                    r_unit=r_int, max_hold=MAX_HOLD, be_at=BE_AT, cost_R=cost_R,
                    conv=FillConvention(fill_bar_can_resolve=fbs,
                                        tie="pess" if pess else "opt",
                                        gap_beyond_stop=True,
                                        on_timeout="mark"),
                )
                if atteso is None:
                    assert got is None
                    continue
                assert got is not None
                assert abs(got.r - atteso) < 1e-9, (
                    "R diverso: primitiva %.6f vs originale %.6f" % (got.r, atteso))
                visti[got.outcome] += 1
    print("  nxt/entry_fill_audit.py           OK   esiti:", visti)


# --- 4: analysis/opening_range/backtest_v2.py (solo il ramo pessimista) --------
def originale_orb_pess(H, L, f, long, entry, sl0, tp, be_trig):
    """Ramo tie='pess'. Il ramo 'opt' NON e' riproducibile: vedi test_orb()."""
    be = False
    sl = sl0
    for j in range(f + 1, min(f + 1 + MAX_HOLD, len(H))):
        hi, lo = H[j], L[j]
        if long:
            hit_tp, hit_sl, hit_be = hi >= tp, lo <= sl, hi >= be_trig
        else:
            hit_tp, hit_sl, hit_be = lo <= tp, hi >= sl, lo <= be_trig
        if not be:
            if hit_sl and hit_tp:
                return -1.0
            if hit_sl:
                return -1.0
            if hit_tp:
                return RR
            if hit_be:
                be = True
                sl = entry
                continue
        else:
            if hit_sl and hit_tp:
                return 0.0
            if hit_sl:
                return 0.0
            if hit_tp:
                return RR
    return None


def test_orb():
    rng = np.random.default_rng(777)
    n_ok = 0
    for _ in range(4000):
        O, H, L, C = percorso(rng)
        long = bool(rng.integers(2))
        f = int(rng.integers(0, 60))
        entry = float(C[f])
        risk = float(abs(rng.normal(0, 0.8))) + 0.3
        sl = entry - risk if long else entry + risk
        tp = entry + RR * risk if long else entry - RR * risk
        be_trig = entry + BE_AT * risk if long else entry - BE_AT * risk
        atteso = originale_orb_pess(H, L, f, long, entry, sl, tp, be_trig)
        got = resolve_trade(
            O, H, L, C, f, fill=entry, sl=sl, tp=tp, long=long,
            r_unit=risk, max_hold=MAX_HOLD + 1, be_at=BE_AT,
            conv=FillConvention(fill_bar_can_resolve=False, tie="pess",
                                gap_beyond_stop=False, on_timeout="drop",
                                be_priority="last"),
        )
        if atteso is None:
            assert got is None
            continue
        assert got is not None
        assert abs(got.r - atteso) < 1e-9, (
            "R diverso: primitiva %.6f vs ORB %.6f" % (got.r, atteso))
        n_ok += 1
    print("  opening_range/backtest_v2.py      OK   (ramo pess, %d casi)" % n_ok)
    print("    NOTA: il ramo tie='opt' dell'ORB NON e' riproducibile, ed e' un bene.")
    print("    Li' un trade che nella stessa barra tocca BE *e* stop originale")
    print("    SOPRAVVIVE e prosegue: ma se il BE e' scattato lo stop era gia' a")
    print("    pareggio, quindi l'esito corretto e' 0, non 'continua'.")


if __name__ == "__main__":
    print("Equivalenza con le implementazioni originali:")
    test_nxt()
    test_audit()
    test_orb()
    print("\nTutti i confronti passati.")
