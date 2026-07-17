"""NXT — Fibonacci trend-pullback: backtest ridotto PRE-REGISTRATO.

Spec immutabile: fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md.
Riduce la sequenza 0/A/B/C ambigua al primitivo tradabile inequivocabile (step 6-8 del video):
  - trend via struttura swing H1 (ZigZag da fractali k=5), long solo se HH & HL (short simmetrico);
  - impulse leg swingLow->swingHigh (long) di ampiezza >= 1*ATR(14);
  - ENTRY limit al 50% di ritracciamento della gamba, valido <=48 barre dallo swing di fine;
  - SL oltre il 78.6% (rischio = 0.286*ampiezza), TP 1:3, BE a +2R;
  - look-ahead-safe: si opera solo su swing CONFERMATI (k barre dopo).

Tre ipotesi: H1 edge assoluto (BCa lower-bound E[R] TEST > 0); H2 il Fib e' speciale
(0.5 vs random-depth in [0.3,0.7], cluster-bootstrap diff > 0); H3 stazionarieta' (train/test + per-anno).
Verdetto sul bound PESSIMISTICO (SL prima di TP intrabar), dopo costi.

Uso: python analysis/nxt/backtest.py
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402

DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data")

# ---- parametri PRE-REGISTRATI (immutabili) ---------------------------------
ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "US100", "US500"]
K = 5                     # semi-finestra fractale per gli swing
ATR_N = 14
MIN_LEG_ATR = 1.0         # ampiezza minima gamba impulsiva (in ATR)
ENTRY_FIB = 0.5           # ritracciamento di ingresso (primaria)
SL_FIB = 0.786            # oltre questo = invalidazione / stop
RR = 3.0                  # take-profit 1:3
BE_AT = 2.0               # break-even a +2R
FILL_WINDOW = 48          # barre H1 max per il fill del pending dallo swing di fine
MAX_HOLD = 24 * 20        # ~20 giorni H1 di holding max
TRAIN_FRAC = 0.70
M_RANDOM = 5              # random-depth per gamba
SEED = 42

# spread round-trip realistico in unita' di prezzo (round-trip = costo pieno)
SPREAD = {"EURUSD": 0.00008, "GBPUSD": 0.00012, "USDJPY": 0.012,
          "XAUUSD": 0.30, "US100": 1.5, "US500": 0.7}


# ---- IO --------------------------------------------------------------------
def load_h1(sym):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_H1.csv"), parse_dates=["time"])
    d = d.drop_duplicates(subset="time", keep="last").sort_values("time").reset_index(drop=True)
    return d


def atr(H, L, C, n=ATR_N):
    H, L, C = np.asarray(H, float), np.asarray(L, float), np.asarray(C, float)
    pc = np.concatenate([[C[0]], C[:-1]])
    tr = np.maximum(H - L, np.maximum(np.abs(H - pc), np.abs(L - pc)))
    return pd.Series(tr).rolling(n).mean().values


# ---- swing detection (ZigZag da fractali, look-ahead-safe) -----------------
def zigzag(H, L, k=K):
    """Ritorna lista di pivot alternati [(idx, price, 'H'|'L', conf_idx)], conf_idx=idx+k.

    Fractale: barra i e' high se H[i] = max(H[i-k..i+k]); low se L[i]=min(L[i-k..i+k]).
    Alterna H/L: due pivot dello stesso tipo consecutivi -> tiene il piu' estremo.
    Il pivot e' 'noto' solo a conf_idx = i+k (k barre dopo)."""
    n = len(H)
    piv = []  # (idx, price, type)
    for i in range(k, n - k):
        if H[i] == max(H[i - k:i + k + 1]) and H[i] > H[i - 1]:
            piv.append((i, H[i], "H"))
        elif L[i] == min(L[i - k:i + k + 1]) and L[i] < L[i - 1]:
            piv.append((i, L[i], "L"))
    # alternanza
    zz = []
    for idx, pr, t in piv:
        if not zz:
            zz.append([idx, pr, t]); continue
        if t == zz[-1][2]:
            if (t == "H" and pr >= zz[-1][1]) or (t == "L" and pr <= zz[-1][1]):
                zz[-1] = [idx, pr, t]
        else:
            zz.append([idx, pr, t])
    return [(idx, pr, t, idx + k) for idx, pr, t in zz]


# ---- costruzione dei setup (gambe impulsive con filtro trend) --------------
def build_legs(zz, A):
    """Da zigzag a lista di setup long/short con filtro HH&HL. A = ATR series.

    Long: sequenza ...L(prev)->H(prev)->L(a)->H(b), con H_b>H_prev (HH) e L_a>L_prev (HL),
    ampiezza (H_b-L_a) >= MIN_LEG_ATR*ATR[a]. Short simmetrico. conf a b_conf=b+K."""
    legs = []
    for i in range(3, len(zz)):
        p0, p1, p2, p3 = zz[i - 3], zz[i - 2], zz[i - 1], zz[i]
        # long: p0=H_prev, p1=L_prev, p2=L? no -> serve H,L,H,L pattern terminante in H
        # allineo per tipo dell'ultimo pivot
        types = (p0[2], p1[2], p2[2], p3[2])
        a_idx = A  # placeholder (non usato)
        if types == ("H", "L", "H", "L"):
            # short: impulso H(p2)->L(p3), retrace verso l'alto; HH&HL invertito -> LH&LL
            H_prev, L_a, H_b0 = None, None, None
            prevH, prevL, startH, endL = p0, p1, p2, p3
            hi_start, lo_end = startH[1], endL[1]
            rng = hi_start - lo_end
            if rng <= 0:
                continue
            a0 = A[startH[0]] if startH[0] < len(A) else np.nan
            if not np.isfinite(a0) or a0 <= 0 or rng < MIN_LEG_ATR * a0:
                continue
            # LH & LL: startH < prevH (lower high) e endL < prevL (lower low)
            if not (startH[1] < prevH[1] and endL[1] < prevL[1]):
                continue
            legs.append({"side": "SELL", "hi": hi_start, "lo": lo_end, "rng": rng,
                         "end_idx": endL[0], "conf": endL[3]})
        elif types == ("L", "H", "L", "H"):
            prevL, prevH, startL, endH = p0, p1, p2, p3
            hi_end, lo_start = endH[1], startL[1]
            rng = hi_end - lo_start
            if rng <= 0:
                continue
            a0 = A[startL[0]] if startL[0] < len(A) else np.nan
            if not np.isfinite(a0) or a0 <= 0 or rng < MIN_LEG_ATR * a0:
                continue
            # HH & HL
            if not (endH[1] > prevH[1] and startL[1] > prevL[1]):
                continue
            legs.append({"side": "BUY", "hi": hi_end, "lo": lo_start, "rng": rng,
                         "end_idx": endH[0], "conf": endH[3]})
    return legs


# ---- simulazione di un singolo trade ---------------------------------------
def simulate(leg, H, L, entry_fib, sym):
    """Ritorna dict trade risolto o None. entry_fib = ritracciamento d'ingresso.

    Long: entry = lo + (1-entry_fib)*rng?  No: retrace dal top. entry = hi - entry_fib*rng.
    SL = hi - SL_FIB*rng (sotto entry). risk = entry-SL = (SL_FIB-entry_fib)*rng.
    """
    side, hi, lo, rng, b, cb = (leg["side"], leg["hi"], leg["lo"], leg["rng"],
                                leg["end_idx"], leg["conf"])
    if side == "BUY":
        entry = hi - entry_fib * rng
        sl = hi - SL_FIB * rng
        risk = entry - sl
    else:
        entry = lo + entry_fib * rng
        sl = lo + SL_FIB * rng
        risk = sl - entry
    if risk <= 0:
        return None
    tp = entry + RR * risk if side == "BUY" else entry - RR * risk
    be = entry + BE_AT * risk if side == "BUY" else entry - BE_AT * risk

    # fill del limit: solo da cb in poi (look-ahead-safe), entro FILL_WINDOW dallo swing b
    f = None
    for j in range(max(cb, b + 1), min(b + 1 + FILL_WINDOW, len(H))):
        # invalidazione se rompe SL prima di toccare l'entry
        if side == "BUY":
            if L[j] <= sl:   # sfondato lo stop-zone senza fill utile
                if L[j] <= entry:  # nella stessa barra tocca entry: fill poi gestione
                    f = j; break
                return None
            if L[j] <= entry:
                f = j; break
        else:
            if H[j] >= sl:
                if H[j] >= entry:
                    f = j; break
                return None
            if H[j] >= entry:
                f = j; break
    if f is None:
        return None

    # risoluzione TP/SL con BE@2R, bound pess/opt
    def resolve(pess):
        be_on = False
        sl_cur = sl
        for j in range(f, min(f + MAX_HOLD, len(H))):
            if side == "BUY":
                if not be_on and H[j] >= be:
                    be_on = True; sl_cur = entry
                hit_sl = L[j] <= sl_cur
                hit_tp = H[j] >= tp
            else:
                if not be_on and L[j] <= be:
                    be_on = True; sl_cur = entry
                hit_sl = H[j] >= sl_cur
                hit_tp = L[j] <= tp
            if hit_sl and hit_tp:
                return ("SL" if pess else "TP"), be_on, j - f
            if hit_sl:
                return "SL", be_on, j - f
            if hit_tp:
                return "TP", be_on, j - f
        return None, be_on, MAX_HOLD

    cost_R = SPREAD.get(sym, 0.0) / risk
    out = {}
    for tag, pess in (("pess", True), ("opt", False)):
        o, be_on, hold = resolve(pess)
        if o is None:
            return None
        if o == "TP":
            r = RR - cost_R
        elif be_on:      # stoppato a break-even
            r = 0.0 - cost_R
        else:
            r = -1.0 - cost_R
        out[f"R_{tag}"] = r
        out[f"tp_{tag}"] = (o == "TP")
        out[f"hold_{tag}"] = hold
    out.update({"side": side, "risk": risk, "entry_idx": f})
    return out


# ---- run per asset ---------------------------------------------------------
def run_asset(sym, rng):
    d = load_h1(sym)
    H, L, C = d["high"].values, d["low"].values, d["close"].values
    yrs = d["time"].dt.year.values
    A = atr(H, L, C)
    zz = zigzag(H, L)
    legs = build_legs(zz, A)
    rows = []
    for lg in legs:
        # trade reale (0.5)
        t = simulate(lg, H, L, ENTRY_FIB, sym)
        if t is None:
            continue
        yr = int(yrs[t["entry_idx"]])
        legid = f"{sym}:{lg['end_idx']}"
        rec = {"asset": sym, "legid": legid, "year": yr, "kind": "real", **t}
        rows.append(rec)
        # naive 0.382 / 0.618
        for nf, nm in ((0.382, "naive382"), (0.618, "naive618")):
            tn = simulate(lg, H, L, nf, sym)
            if tn is not None:
                rows.append({"asset": sym, "legid": legid, "year": int(yrs[tn["entry_idx"]]),
                             "kind": nm, **tn})
        # random-depth in [0.3,0.7]
        for _ in range(M_RANDOM):
            rf = float(rng.uniform(0.3, 0.7))
            tr_ = simulate(lg, H, L, rf, sym)
            if tr_ is not None:
                rows.append({"asset": sym, "legid": legid, "year": int(yrs[tr_["entry_idx"]]),
                             "kind": "rand", **tr_})
    return pd.DataFrame(rows)


# ---- cluster bootstrap diff (per legid) ------------------------------------
def cluster_diff_ci(df_real, df_rand, col="R_pess", n_boot=3000, seed=SEED):
    """CI 95% di E[R]_real - E[R]_rand, ricampionando i legid (cluster)."""
    rng = np.random.default_rng(seed)
    real_by = defaultdict(list)
    rand_by = defaultdict(list)
    for lid, v in zip(df_real["legid"], df_real[col]):
        real_by[lid].append(v)
    for lid, v in zip(df_rand["legid"], df_rand[col]):
        rand_by[lid].append(v)
    legids = sorted(set(real_by) | set(rand_by))
    if len(legids) < 5:
        return (np.nan, np.nan, np.nan)
    rv_all = [v for lid in legids for v in real_by.get(lid, [])]
    cv_all = [v for lid in legids for v in rand_by.get(lid, [])]
    point = (np.mean(rv_all) - np.mean(cv_all)) if rv_all and cv_all else np.nan
    idx = np.arange(len(legids))
    diffs = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        rv = [v for k in s for v in real_by.get(legids[k], [])]
        cv = [v for k in s for v in rand_by.get(legids[k], [])]
        if rv and cv:
            diffs.append(np.mean(rv) - np.mean(cv))
    if not diffs:
        return (np.nan, np.nan, point)
    return (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)), float(point))


def _er_line(tag, R, tp_bool):
    R = np.asarray(R, float)
    if len(R) < 5:
        return f"{tag:20} n={len(R):4} (pochi)"
    bca = qm.bca_bootstrap_ci(R, metric=lambda x: float(np.mean(x)), conf=0.95, n_boot=3000, seed=SEED)
    wr = 100 * np.mean(tp_bool)
    flag = "  <-- lower>0" if bca["low"] > 0 else ""
    return (f"{tag:20} n={len(R):4}  win%={wr:4.1f}  E[R]={R.mean():+.3f}  "
            f"BCa=[{bca['low']:+.3f},{bca['high']:+.3f}]{flag}")


def split_train_test(df):
    """Split temporale 70/30 per asset sull'indice di ingresso."""
    train, test = [], []
    for sym, g in df.groupby("asset"):
        g = g.sort_values("entry_idx")
        cut = g["entry_idx"].quantile(TRAIN_FRAC)
        train.append(g[g["entry_idx"] <= cut])
        test.append(g[g["entry_idx"] > cut])
    return pd.concat(train), pd.concat(test)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rng = np.random.default_rng(SEED)
    frames = []
    print("Caricamento + backtest per asset...")
    for sym in ASSETS:
        try:
            df = run_asset(sym, rng)
        except FileNotFoundError:
            print(f"  {sym}: dati mancanti, skip"); continue
        n_real = int((df["kind"] == "real").sum()) if len(df) else 0
        print(f"  {sym:8} setup(real)={n_real}")
        frames.append(df)
    if not frames:
        print("Nessun dato."); return
    allr = pd.concat(frames, ignore_index=True)
    real = allr[allr["kind"] == "real"]
    rand = allr[allr["kind"] == "rand"]
    n382 = allr[allr["kind"] == "naive382"]
    n618 = allr[allr["kind"] == "naive618"]

    print("\n" + "=" * 78)
    print("NXT Fib trend-pullback — POOL multi-asset (H1, ~14y)")
    print("=" * 78)
    print(f"break-even win-rate teorico a 1:3 (dopo costi ~0) = 25.0%")
    print(f"claim del video = 60-70% win rate @ 1:3\n")

    print("--- H1: EDGE ASSOLUTO (reale 0.5, tutto il campione) ---")
    for tag in ("pess", "opt"):
        print("  " + _er_line(f"real 0.5 [{tag}]", real[f"R_{tag}"], real[f"tp_{tag}"]))

    print("\n--- H3: HOLDOUT 70/30 temporale (reale 0.5, PESSIMISTICO) ---")
    tr, te = split_train_test(real)
    print("  " + _er_line("TRAIN", tr["R_pess"], tr["tp_pess"]))
    print("  " + _er_line("TEST (holdout)", te["R_pess"], te["tp_pess"]))

    print("\n--- H3: E[R] pess per ANNO (reale 0.5) — caccia al miraggio post-2020 ---")
    for y, g in real.groupby("year"):
        print(f"    {y}: n={len(g):4}  win%={100*g['tp_pess'].mean():4.1f}  E[R]={g['R_pess'].mean():+.3f}")

    print("\n--- H2: IL FIB E' SPECIALE? (reale 0.5 vs baseline, PESSIMISTICO) ---")
    print("  " + _er_line("real 0.5", real["R_pess"], real["tp_pess"]))
    print("  " + _er_line("naive 0.382", n382["R_pess"], n382["tp_pess"]))
    print("  " + _er_line("naive 0.618", n618["R_pess"], n618["tp_pess"]))
    print("  " + _er_line("random depth", rand["R_pess"], rand["tp_pess"]))
    lo, hi, pt = cluster_diff_ci(real, rand, "R_pess")
    print(f"\n  diff E[R] (real0.5 - random) = {pt:+.3f}  CI95=[{lo:+.3f},{hi:+.3f}]  "
          f"{'FIB BATTE random' if lo > 0 else 'Fib NON batte random'}")

    print("\n--- per asset (reale 0.5, pess) ---")
    for sym, g in real.groupby("asset"):
        b = qm.bca_bootstrap_ci(g["R_pess"].values, metric=lambda x: float(np.mean(x)),
                                conf=0.95, n_boot=2000, seed=SEED) if len(g) >= 5 else None
        ci = f"[{b['low']:+.3f},{b['high']:+.3f}]" if b else "n/d"
        print(f"    {sym:8} n={len(g):4}  win%={100*g['tp_pess'].mean():4.1f}  "
              f"E[R]={g['R_pess'].mean():+.3f}  BCa={ci}")


if __name__ == "__main__":
    main()
