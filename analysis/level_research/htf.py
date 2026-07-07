"""v3 — livelli HTF (H4/D1/W1) con metodologia CORRETTA (vedi PRE-REGISTRAZIONE addendum v3).

Correzioni rispetto a v1/v2:
  - detection e misura su H4, D1, W1 (H4 ricampionato da H1, W1 da D1);
  - tolleranza scalata all'ATR del TF (banda 0.20*ATR per i livelli-LINEA; sweep 0.10/0.30);
  - livelli-ZONA (Order Block): larghezza intrinseca della zona + break = body-close oltre il 50% MT;
  - random distance-matched E structure-free (rifiutato se cade su qualsiasi struttura vera);
  - freshness: ogni livello reale naked (0 touch pregressi) vs tested.
FVG e volume esclusi (decisione utente). Look-ahead-safe. Reuse: reaction.classify (generalizzata),
levels_engine, detectors.round_number/eqh_eql.

Uso:  python analysis/level_research/htf.py            # tolleranza primaria 0.20
      python analysis/level_research/htf.py 0.10        # sweep di robustezza
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "veltrix"))
import numpy as np  # noqa: E402

import levels_engine as le  # noqa: E402
from detectors import ROUND_STEP, eqh_eql, round_number  # noqa: E402
from engine import atr_series, load_bars  # noqa: E402
from reaction import (INSUFF, REACTION, TESTED, boot_rate_diff_ci,  # noqa: E402
                      classify, rate)

# ---- costanti (PRE-REGISTRATE) --------------------------------------------
TFS = ["H4", "D1", "W1"]
DET_WINDOW = {"H4": 180, "D1": 120, "W1": 52}   # barre chiuse trailing per la detection
FWD = 30                                        # TOUCH_WINDOW(24)+N_REACT(4)+2, in barre del TF
DEDUP_ATR = 0.20
TRAIN_FRAC = 0.70
M_RANDOM = 5
MIN_TOUCH, MIN_DAYS = 30, 10
SEED = 42
CONCEPTS = ["swing", "prevhl", "ob", "round", "eqh_eql"]
ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF",
          "EURJPY.r", "GBPJPY.r", "EURGBP.r", "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD",
          "US500", "US100"]


# ---- ricampionamento -------------------------------------------------------
def _agg(group):
    return {"t": group[0]["t"], "open": group[0]["open"],
            "high": max(b["high"] for b in group), "low": min(b["low"] for b in group),
            "close": group[-1]["close"], "volume": sum(b.get("volume", 0) for b in group)}


def resample_h4(h1):
    """H1 -> H4 su bucket 0/4/8/12/16/20 UTC."""
    out, cur, key = [], [], None
    for b in h1:
        hh = int(b["t"][11:13])
        k = (b["t"][:10], hh // 4)
        if key is None or k == key:
            cur.append(b); key = k
        else:
            out.append(_agg(cur)); cur = [b]; key = k
    if cur:
        out.append(_agg(cur))
    return out


def _isoweek(dstr):
    import datetime as dt
    y, m, d = int(dstr[:4]), int(dstr[5:7]), int(dstr[8:10])
    iy, iw, _ = dt.date(y, m, d).isocalendar()
    return (iy, iw)


def resample_w1(d1):
    """D1 -> W1 per settimana ISO."""
    out, cur, key = [], [], None
    for b in d1:
        k = _isoweek(b["t"][:10])
        if key is None or k == key:
            cur.append(b); key = k
        else:
            out.append(_agg(cur)); cur = [b]; key = k
    if cur:
        out.append(_agg(cur))
    return out


def load_tf(asset, tf):
    if tf == "D1":
        return load_bars(asset, "D1")
    if tf == "H4":
        return resample_h4(load_bars(asset, "H1"))
    if tf == "W1":
        return resample_w1(load_bars(asset, "D1"))
    raise ValueError(tf)


# ---- detection -------------------------------------------------------------
def detect_levels(window, prev_bar, price, atr, asset, tol_atr, concepts):
    """Lista di dict {anchor, side, concept, touch_tol, break_tol}. Non filtrati."""
    lt = tol_atr * atr
    out = []

    def line(p, side, con):
        return {"anchor": p, "side": side, "concept": con, "touch_tol": lt, "break_tol": lt}

    if "swing" in concepts:
        kl = le.get_key_levels(window)
        out += [line(p, "SUPPORT", "swing") for p in kl["supports"]]
        out += [line(p, "RESISTANCE", "swing") for p in kl["resistances"]]
    if "prevhl" in concepts and prev_bar:
        out.append(line(prev_bar["high"], "RESISTANCE", "prevhl"))
        out.append(line(prev_bar["low"], "SUPPORT", "prevhl"))
    if "ob" in concepts:
        for ob in le.detect_order_blocks(window):
            mt = (ob["high"] + ob["low"]) / 2
            half = max((ob["high"] - ob["low"]) / 2, 1e-9)
            side = "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE"
            # zona: touch = ingresso zona (mezza larghezza); break = body-close oltre il 50% MT
            out.append({"anchor": mt, "side": side, "concept": "ob",
                        "touch_tol": half, "break_tol": 0.0})
    if "round" in concepts:
        for p, side, _ in round_number(price, ROUND_STEP.get(asset)):
            out.append(line(p, side, "round"))
    if "eqh_eql" in concepts:
        for p, side, _ in eqh_eql(window, atr, tol_atr):
            out.append(line(p, side, "eqh_eql"))
    return out


def _prior_touches(window, anchor, tt):
    return sum(1 for b in window if b["low"] <= anchor + tt and b["high"] >= anchor - tt)


# ---- misura per TF ---------------------------------------------------------
def measure_tf(bars, asset, tf, tol_atr, concepts, days_keep=None):
    if len(bars) < DET_WINDOW[tf] + FWD + 5:
        return None
    atr = atr_series(bars)
    win = DET_WINDOW[tf]
    lineband = tol_atr

    decisions = []
    pool = defaultdict(list)
    for di in range(win, len(bars) - 3):
        a = atr[di - 1]
        if not a or a <= 0:
            continue
        day = bars[di]["t"][:10]
        if days_keep is not None and day not in days_keep:
            continue
        P0 = bars[di - 1]["close"]
        window = bars[di - win:di]
        raw = detect_levels(window, bars[di - 1], P0, a, asset, tol_atr, concepts)
        lvls, anchors = [], []
        seen = []
        for L in raw:
            pr, side = L["anchor"], L["side"]
            if pr <= 0 or (side == "SUPPORT" and pr > P0) or (side == "RESISTANCE" and pr < P0):
                continue
            dist = abs(pr - P0) / a
            if dist <= 1e-9:
                continue
            if any(c == L["concept"] and s == side and abs(k - pr) <= DEDUP_ATR * a
                   for k, s, c in seen):
                continue
            seen.append((pr, side, L["concept"]))
            naked = _prior_touches(window, pr, L["touch_tol"]) <= 1
            lvls.append((pr, side, L["concept"], L["touch_tol"], L["break_tol"], dist, naked))
            anchors.append(pr)
            pool[(L["concept"], side)].append(dist)
        if lvls:
            decisions.append({"di": di, "P0": P0, "a": a, "day": day,
                              "levels": lvls, "anchors": anchors})
    if not decisions:
        return None
    pool = {k: np.array(v) for k, v in pool.items()}
    rng = np.random.default_rng(SEED)

    acc = {c: {"real": [], "rand": [], "naked": [], "tested": [], "n_touch": 0, "n_lev": 0}
           for c in concepts}
    for dec in decisions:
        di, P0, a, day = dec["di"], dec["P0"], dec["a"], dec["day"]
        fwd = bars[di:di + FWD]
        if len(fwd) < 3:
            continue
        band = lineband * a
        anchors = dec["anchors"]
        for pr, side, con, ttol, btol, dist, naked in dec["levels"]:
            A = acc[con]; A["n_lev"] += 1
            real = classify(fwd, pr, side, a, touch_tol=ttol, break_tol=btol)
            if real["cls"] != INSUFF and real["cls"] in TESTED:
                A["n_touch"] += 1
                r = 1.0 if real["cls"] == REACTION else 0.0
                A["real"].append((day, r))
                (A["naked"] if naked else A["tested"]).append((day, r))
            dpool = pool.get((con, side))
            if dpool is None or len(dpool) == 0:
                continue
            got = 0
            tries = 0
            while got < M_RANDOM and tries < 6 * M_RANDOM:
                tries += 1
                dprime = float(rng.choice(dpool))
                rp = P0 - dprime * a if side == "SUPPORT" else P0 + dprime * a
                if rp <= 0:
                    continue
                if any(abs(rp - x) <= band for x in anchors):   # structure-free
                    continue
                rc = classify(fwd, rp, side, a, touch_tol=ttol, break_tol=btol)
                if rc["cls"] == INSUFF:
                    continue
                got += 1
                if rc["cls"] in TESTED:
                    A["rand"].append((day, 1.0 if rc["cls"] == REACTION else 0.0))
    return acc


def split_days(bars, tf):
    days = sorted({bars[i]["t"][:10] for i in range(DET_WINDOW[tf], len(bars) - 3)})
    if len(days) < 10:
        return set(days), set()
    cut = int(TRAIN_FRAC * len(days))
    return set(days[:cut]), set(days[cut:])


# ---- aggregazione poolata (per-giorno, memoria limitata) -------------------
def _add_items(agg, items):
    for d, v in items:
        s = agg.setdefault(d, [0.0, 0])
        s[0] += v; s[1] += 1


def boot_agg(real_agg, rand_agg, n_boot=4000, seed=SEED):
    """CI 95% diff di tasso da dict giorno->[somma,conteggio], chunked (memoria limitata)."""
    days = sorted(set(real_agg) | set(rand_agg))
    if len(days) < 3:
        return (float("nan"), float("nan"), float("nan"), len(days))
    rs = np.array([real_agg.get(d, [0, 0])[0] for d in days])
    rc = np.array([real_agg.get(d, [0, 0])[1] for d in days], float)
    cs = np.array([rand_agg.get(d, [0, 0])[0] for d in days])
    cc = np.array([rand_agg.get(d, [0, 0])[1] for d in days], float)
    point = (float("nan") if rc.sum() == 0 or cc.sum() == 0
             else 100.0 * (rs.sum() / rc.sum() - cs.sum() / cc.sum()))
    rng = np.random.default_rng(seed)
    nd = len(days); chunk = max(1, 4_000_000 // nd); diffs = []; done = 0
    while done < n_boot:
        bsz = min(chunk, n_boot - done)
        idx = rng.integers(0, nd, size=(bsz, nd))
        rsum, rcnt = rs[idx].sum(1), rc[idx].sum(1)
        csum, ccnt = cs[idx].sum(1), cc[idx].sum(1)
        ok = (rcnt > 0) & (ccnt > 0)
        diffs.append(100.0 * (rsum[ok] / rcnt[ok] - csum[ok] / ccnt[ok]))
        done += bsz
    diff = np.concatenate(diffs)
    if diff.size < 10:
        return (float("nan"), float("nan"), point, len(days))
    return (float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)), point, len(days))


def _agg_rate(agg):
    s = sum(v[0] for v in agg.values()); n = sum(v[1] for v in agg.values())
    return 100.0 * s / n if n else float("nan"), n


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    tol = float(sys.argv[1]) if len(sys.argv) > 1 else 0.20
    print("=" * 96)
    print(f"v3 HTF — reazione-vs-random (distance-matched + STRUCTURE-FREE) — tol linea {tol}·ATR(TF)")
    print(f"   concetti={CONCEPTS}  TF={TFS}  freshness=naked/tested  [* batte random, CI>0]")
    print("=" * 96)
    survivors = []
    tot_beats = tot_cells = 0
    for tf in TFS:
        ptr = {c: {"real": {}, "rand": {}, "naked": {}, "tested": {}, "rnd_all": {}}
               for c in CONCEPTS}
        pte = {c: {"real": {}, "rand": {}} for c in CONCEPTS}
        breadth = {c: 0 for c in CONCEPTS}; tested = {c: 0 for c in CONCEPTS}
        print(f"\n----- {tf} -----")
        for asset in ASSETS:
            bars = load_tf(asset, tf)
            tr, te = split_days(bars, tf)
            acc = measure_tf(bars, asset, tf, tol, CONCEPTS, tr)
            ate = measure_tf(bars, asset, tf, tol, CONCEPTS, te)
            marks = [f"{asset:9}"]
            for c in CONCEPTS:
                if acc is None:
                    marks.append(f"{c[:5]}:  -  "); continue
                A = acc[c]
                _add_items(ptr[c]["real"], [(f"{asset}:{d}", v) for d, v in A["real"]])
                _add_items(ptr[c]["rand"], [(f"{asset}:{d}", v) for d, v in A["rand"]])
                _add_items(ptr[c]["naked"], [(f"{asset}:{d}", v) for d, v in A["naked"]])
                _add_items(ptr[c]["tested"], [(f"{asset}:{d}", v) for d, v in A["tested"]])
                if ate:
                    _add_items(pte[c]["real"], [(f"{asset}:{d}", v) for d, v in ate[c]["real"]])
                    _add_items(pte[c]["rand"], [(f"{asset}:{d}", v) for d, v in ate[c]["rand"]])
                # cella per-asset (train) per la breadth
                lo, hi, dp, nd = boot_rate_diff_ci(A["real"], A["rand"], n_boot=1500)
                enough = A["n_touch"] >= MIN_TOUCH and nd >= MIN_DAYS
                beat = enough and not np.isnan(lo) and lo > 0
                if enough:
                    tested[c] += 1; tot_cells += 1
                    if beat:
                        breadth[c] += 1; tot_beats += 1
                marks.append(f"{c[:5]}:{dp:+5.1f}{'*' if beat else ' '}" if enough
                             else f"{c[:5]}: n/a ")
            print("  ".join(marks))
        # verdetto poolato per concetto su questo TF
        print(f"  --- verdetto {tf} (breadth + pooled + freshness) ---")
        for c in CONCEPTS:
            lo, hi, dp, nd = boot_agg(ptr[c]["real"], ptr[c]["rand"])
            rr, _ = _agg_rate(ptr[c]["real"]); rn, _ = _agg_rate(ptr[c]["rand"])
            nk, nkn = _agg_rate(ptr[c]["naked"]); ts, tsn = _agg_rate(ptr[c]["tested"])
            pooled_beat = not np.isnan(lo) and lo > 0
            surv = (tested[c] and breadth[c] / tested[c] >= 0.50) and pooled_beat
            if surv:
                survivors.append((tf, c))
            v = "SOPRAVVIVE" if surv else ("(pool>0,breadth<50%)" if pooled_beat else "no")
            print(f"  {c:8} breadth {breadth[c]}/{tested[c]:<2} pooled {rr:4.1f}%vs{rn:4.1f}% "
                  f"CI[{lo:+.1f},{hi:+.1f}] | naked {nk:4.1f}%(n{nkn}) tested {ts:4.1f}%(n{tsn})"
                  f"  -> {v}")
        # holdout test per i sopravvissuti di questo TF
        for (stf, c) in [s for s in survivors if s[0] == tf]:
            lo, hi, dp, nd = boot_agg(pte[c]["real"], pte[c]["rand"])
            print(f"  HOLDOUT {c}: TEST diff={dp:+.1f} CI[{lo:+.1f},{hi:+.1f}] "
                  f"-> {'TIENE' if (not np.isnan(lo) and lo>0) else 'NON tiene'}")

    T = len(CONCEPTS) * len(TFS) * len(ASSETS)
    print("\n" + "=" * 96)
    print(f"DSR: trial = {len(CONCEPTS)}x{len(TFS)}x{len(ASSETS)} = {T} (falsi attesi ~{0.05*T:.0f})")
    print(f"     'batte' osservati = {tot_beats} su {tot_cells} celle con evidenza")
    if not survivors:
        print("NESSUN sopravvissuto: nemmeno gli HTF (fatti bene) battono il random -> libro chiuso.")
    print(f"tol linea {tol}·ATR(TF); zone (OB) = larghezza vera + break 50% MT; random structure-free.")


if __name__ == "__main__":
    main()
