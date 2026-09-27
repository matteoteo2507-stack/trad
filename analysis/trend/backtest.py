"""Trend following: uscita a coda aperta x gradiente di liquidita' — motore PRE-REGISTRATO.

Spec immutabile: docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md.

Q1: tenendo FISSA l'entrata (Donchian 100g), un'uscita a coda aperta (trailing SMA10, niente
    target) batte le uscite che troncano (stop1R/target3R, uscita a tempo)?
Q2: l'espettanza della stessa regola e' ordinata secondo la volatilita' realizzata dell'asset
    (claim Kichev: forex = liquidita' massima/edge minimo -> agri/crypto = opposto)?

Tutto look-ahead-safe: segnale/ATR/SMA su dati <= t-1, esecuzione all'apertura di t+1.
Unita' di rischio R = ATR(20) all'entrata (NON e' uno stop: serve a rendere confrontabili
uscite e asset). Baseline obbligatori: oracolo (soffitto) e random risk-matched.

Uso: python analysis/trend/backtest.py [lookback]
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402
from core.random_baseline import BarSampler, check_matching  # noqa: E402

DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")

# ---- parametri PRE-REGISTRATI (immutabili) ---------------------------------
LOOKBACK = 100          # primario (robustezza: 50, 200)
SMA_EXIT = 10           # trailing MA della fonte
ATR_N = 20              # unita' di rischio
STOP_R = 1.0            # E1b / E2
TARGET_R = 3.0          # E2
TIME_EXIT = 20          # E3, giorni di borsa
MAX_HOLD = 250          # cap per E1/E1b/oracolo (~1 anno)
M_RANDOM = 3            # controlli random per segnale reale
SEED = 42

COST_BPS = {"fx_major": 2, "fx_cross": 3, "index": 3, "bond": 3,
            "metal": 4, "metal_ind": 8, "energy": 8, "agri": 12, "crypto": 8}
METAL_IND = {"COPPER", "XPT", "XPD"}     # costo 8 bps, non 4


def load(sym, group=None):
    """D1 pulito. Le barre di sabato/domenica dei CFD NON-crypto sono sessioni PARZIALI
    (1-2 ore: EURUSD domenica ha range mediano 0.137% contro 0.65% dei feriali) e vanno
    FUSE nella barra feriale successiva, non tenute come giornate.

    Perche' e' obbligatorio: tenerle diluisce l'ATR(20) verso il basso -> R troppo piccolo ->
    ogni multiplo di R gonfiato; e trasforma il Donchian "100 giorni" in ~83 giorni reali.
    La crypto tratta davvero 7 giorni su 7: li' non si fonde nulla.
    """
    d = pd.read_csv(os.path.join(DATA, f"{sym}_D1.csv"), parse_dates=["time"])
    d = d.drop_duplicates(subset="time", keep="last").sort_values("time").reset_index(drop=True)
    d = d[d[["open", "high", "low", "close"]].gt(0).all(axis=1)].reset_index(drop=True)
    if group == "crypto" or len(d) == 0:
        return d.reset_index(drop=True)
    is_we = d["time"].dt.dayofweek >= 5
    if not is_we.any():
        return d.reset_index(drop=True)
    # ogni barra di weekend prende la chiave della PROSSIMA barra feriale
    key = (~is_we).iloc[::-1].cumsum().iloc[::-1]
    d = d[key > 0].copy()
    key = key[key > 0]
    g = d.groupby(key.values, sort=True)
    out = pd.DataFrame({
        "time": g["time"].last(), "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(), "volume": g["volume"].sum(),
    })
    # la chiave nasce da un cumsum INVERTITO -> decresce nel tempo: si riordina per tempo
    return out.sort_values("time").reset_index(drop=True)


def atr(H, L, C, n=ATR_N):
    pc = np.concatenate([[C[0]], C[:-1]])
    tr = np.maximum(H - L, np.maximum(np.abs(H - pc), np.abs(L - pc)))
    return pd.Series(tr).rolling(n).mean().values


def cost_bps_for(sym, grp):
    if sym in METAL_IND:
        return COST_BPS["metal_ind"]
    return COST_BPS[grp]


def simulate(O, H, L, C, sma, f, side, R, cost_R):
    """Dalle stesse entrate (fill all'apertura di f), risolve le 4 uscite + l'oracolo.

    Ritorna dict di R-multipli. Convenzione pessimistica intrabar: se nella stessa barra
    toccano stop e target, vince lo stop.
    """
    entry = O[f]
    sgn = 1.0 if side == "BUY" else -1.0
    last = min(f + MAX_HOLD, len(C)) - 1
    out = {}

    # ---- E1 trailing SMA10, nessuno stop ----  ---- E1b: + stop iniziale 1R ----
    stop_px = entry - sgn * STOP_R * R
    e1 = e1b = None
    exit_idx = last
    mfe = -np.inf
    for j in range(f, last + 1):
        fav = (H[j] - entry) if side == "BUY" else (entry - L[j])
        mfe = max(mfe, fav / R)
        if e1b is None:
            hit = (L[j] <= stop_px) if side == "BUY" else (H[j] >= stop_px)
            if hit:
                e1b = -STOP_R - cost_R
        # segnale di uscita sul close di j -> esce all'apertura di j+1
        if np.isfinite(sma[j]):
            cross = (C[j] < sma[j]) if side == "BUY" else (C[j] > sma[j])
            if cross and j + 1 <= len(O) - 1:
                r = sgn * (O[j + 1] - entry) / R - cost_R
                e1 = r
                if e1b is None:
                    e1b = r
                exit_idx = j + 1
                break
        if j == last:
            r = sgn * (C[j] - entry) / R - cost_R
            e1 = r
            if e1b is None:
                e1b = r
            exit_idx = j
    out["E1"], out["E1b"] = e1, e1b
    out["oracle"] = max(mfe, -1.0) - cost_R
    out["mfe"] = mfe - cost_R
    out["hold_e1"] = exit_idx - f
    out["exit_idx"] = exit_idx

    # ---- E2 stop 1R / target 3R ----
    tgt = entry + sgn * TARGET_R * R
    e2 = None
    for j in range(f, min(f + MAX_HOLD, len(C))):
        if side == "BUY":
            hs, ht = L[j] <= stop_px, H[j] >= tgt
        else:
            hs, ht = H[j] >= stop_px, L[j] <= tgt
        if hs:
            e2 = -STOP_R - cost_R
            break
        if ht:
            e2 = TARGET_R - cost_R
            break
    if e2 is None:
        j = min(f + MAX_HOLD, len(C)) - 1
        e2 = sgn * (C[j] - entry) / R - cost_R
    out["E2"] = e2

    # ---- E3 uscita a tempo ----
    j = min(f + TIME_EXIT, len(C) - 1)
    out["E3"] = sgn * (C[j] - entry) / R - cost_R
    return out


def run_asset(sym, grp, lookback, rng, t0=None, t1=None):
    d = load(sym, grp)
    if t0 is not None:
        d = d[d["time"] >= t0]
    if t1 is not None:
        d = d[d["time"] <= t1]
    d = d.reset_index(drop=True)
    if len(d) < lookback + ATR_N + 60:
        return pd.DataFrame(), pd.DataFrame()
    O, H, L, C = (d[c].values.astype(float) for c in ("open", "high", "low", "close"))
    t = d["time"].values
    A = atr(H, L, C)
    sma = pd.Series(C).rolling(SMA_EXIT).mean().values
    hh = pd.Series(H).rolling(lookback).max().shift(1).values   # max di high[t-lb .. t-1]
    ll = pd.Series(L).rolling(lookback).min().shift(1).values
    bps = cost_bps_for(sym, grp)

    real, rand = [], []
    in_pos_until = -1
    years = pd.DatetimeIndex(t).year.values
    valid = np.flatnonzero(np.isfinite(A) & (A > 0))
    lo_v, hi_v = (valid[0], valid[-1]) if len(valid) else (0, 0)
    usable = (np.arange(len(C)) >= lo_v) & (np.arange(len(C)) <= hi_v - 2)
    sampler = BarSampler(years, rng, usable=usable)

    for i in range(lookback + ATR_N, len(C) - 2):
        if i <= in_pos_until:
            continue
        if not np.isfinite(hh[i]) or not np.isfinite(A[i]) or A[i] <= 0:
            continue
        side = None
        if C[i] > hh[i]:
            side = "BUY"
        elif C[i] < ll[i]:
            side = "SELL"
        if side is None:
            continue
        f = i + 1                      # esecuzione all'apertura successiva
        R = A[i]                       # ATR <= t-1 (A[i] usa dati fino a i)
        cost_R = (bps / 1e4) * C[i] / R
        res = simulate(O, H, L, C, sma, f, side, R, cost_R)
        rec = {"sym": sym, "group": grp, "side": side, "year": int(years[f]),
               "entry_idx": f, "R_price": R, "cost_R": cost_R,
               "sigid": f"{sym}:{f}", **res}
        real.append(rec)
        # una posizione per strumento alla volta: si blocca fino all'uscita della regola PRIMARIA
        in_pos_until = int(res["exit_idx"])

        # ---- baseline random risk-matched: stesso anno, stesso lato, istante casuale ----
        # Campionamento da core.random_baseline: estrazioni identiche a quelle del
        # ciclo scritto a mano che stava qui (core/tests/test_random_baseline.py, caso 3).
        for k in sampler.draw(years[f], M_RANDOM):
            if not np.isfinite(A[k]) or A[k] <= 0 or k + 1 >= len(C) - 1:
                continue
            Rk = A[k]
            ck = (bps / 1e4) * C[k] / Rk
            rr = simulate(O, H, L, C, sma, k + 1, side, Rk, ck)
            rand.append({"sym": sym, "group": grp, "side": side, "year": int(years[k]),
                         "entry_idx": k + 1, "R_price": Rk, "cost_R": ck,
                         "sigid": f"{sym}:{f}", **rr})
    return pd.DataFrame(real), pd.DataFrame(rand)


def paired_ci(df, a, b, n_boot=3000, seed=SEED):
    """CI 95% della differenza appaiata media (a - b), cluster sul segnale."""
    x = (df[a] - df[b]).to_numpy(float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return (np.nan, np.nan, np.nan)
    r = qm.bca_bootstrap_ci(x, metric=lambda v: float(np.mean(v)), conf=0.95,
                            n_boot=n_boot, seed=seed)
    return (r["low"], r["high"], float(np.mean(x)))


def spearman_perm(x, y, n_perm=20000, seed=SEED):
    """Spearman + p-value per permutazione (esatto-ish su n piccolo)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 4:
        return np.nan, np.nan
    rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()

    def rho(a, b):
        a, b = a - a.mean(), b - b.mean()
        d = np.sqrt((a * a).sum() * (b * b).sum())
        return float((a * b).sum() / d) if d > 0 else 0.0

    obs = rho(rx, ry)
    rng = np.random.default_rng(seed)
    cnt = sum(1 for _ in range(n_perm) if rho(rng.permutation(rx), ry) >= obs)
    return obs, (cnt + 1) / (n_perm + 1)


def realized_vol(sym, group=None, t0=None, t1=None):
    d = load(sym, group)
    if t0 is not None:
        d = d[d["time"] >= t0]
    if t1 is not None:
        d = d[d["time"] <= t1]
    r = np.diff(np.log(d["close"].values.astype(float)))
    return float(np.std(r, ddof=1) * np.sqrt(252)) if len(r) > 50 else np.nan


def cluster_diff(dfa, dfb, col, n_boot=2000, seed=SEED):
    """CI 95% di media(dfa[col]) - media(dfb[col]), ricampionando i sigid."""
    rng = np.random.default_rng(seed)
    A_, B_ = defaultdict(list), defaultdict(list)
    for s, v in zip(dfa["sigid"], dfa[col]):
        A_[s].append(v)
    for s, v in zip(dfb["sigid"], dfb[col]):
        B_[s].append(v)
    keys = sorted(set(A_) | set(B_))
    if len(keys) < 10:
        return (np.nan, np.nan, np.nan)
    idx = np.arange(len(keys))
    pt = float(np.mean(dfa[col])) - float(np.mean(dfb[col]))
    out = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        av = [v for k in s for v in A_.get(keys[k], [])]
        bv = [v for k in s for v in B_.get(keys[k], [])]
        if av and bv:
            out.append(np.mean(av) - np.mean(bv))
    if not out:
        return (np.nan, np.nan, pt)
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)), pt)


# ---- reporting ------------------------------------------------------------
EXITS = ["E1", "E1b", "E2", "E3"]
EXIT_LAB = {"E1": "E1 trail SMA10 (tesi)", "E1b": "E1b trail + stop 1R",
            "E2": "E2 stop1R/target3R", "E3": "E3 uscita a tempo"}


def _mean_ci(v, n_boot=3000):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return qm.bca_bootstrap_ci(v, metric=lambda x: float(np.mean(x)), conf=0.95,
                               n_boot=n_boot, seed=SEED)


def universe_from_coverage():
    cov = pd.read_csv(os.path.join(DATA, "_coverage.csv"))
    cov = cov[cov["n"] > 0].copy()
    cov["start"] = pd.to_datetime(cov["start"])
    cov["end"] = pd.to_datetime(cov["end"])
    # REGOLA DI COPERTURA, decisa su DISPONIBILITA' e mai su risultato: si escludono gli
    # strumenti che iniziano dopo il 2018-01-01, altrimenti XPT (2021-12) e XPD (2022-02)
    # comprimerebbero la finestra comune W2 a 4.5 anni. Cosi' W2 resta >= 8 anni e tutti
    # gli 8 gruppi restano rappresentati.
    cut = pd.Timestamp("2018-01-01")
    dropped = cov[cov["start"] > cut]
    if len(dropped):
        print("Esclusi per copertura (start > 2018-01-01): "
              + ", ".join(f"{r['sym']}({r['start'].date()})" for _, r in dropped.iterrows()))
    return cov[cov["start"] <= cut].reset_index(drop=True)


def run_all(cov, lookback, t0=None, t1=None, seed=SEED):
    rng = np.random.default_rng(seed)
    R_, D_ = [], []
    for _, row in cov.iterrows():
        a, b = run_asset(row["sym"], row["group"], lookback, rng, t0, t1)
        if len(a):
            R_.append(a)
        if len(b):
            D_.append(b)
    real = pd.concat(R_, ignore_index=True) if R_ else pd.DataFrame()
    rand = pd.concat(D_, ignore_index=True) if D_ else pd.DataFrame()
    return real, rand


def q1_report(real, rand, tag):
    print("\n" + "=" * 78)
    print(f"Q1 - LA CODA APERTA  [{tag}]  n_segnali={len(real)}"
          f"  strumenti={real['sym'].nunique()}  anni={real['year'].nunique()}")
    print("=" * 78)
    print(f"{'uscita':26} {'n':>6} {'E[R]':>9} {'BCa95':>20} {'win%':>7}")
    for e in EXITS:
        v = real[e].dropna().to_numpy()
        ci = _mean_ci(v)
        print(f"{EXIT_LAB[e]:26} {len(v):6} {v.mean():+9.3f} "
              f"[{ci['low']:+.3f},{ci['high']:+.3f}] {100*np.mean(v > 0):6.1f}%")
    orc = real["oracle"].dropna().to_numpy()
    print(f"{'B-oracolo (soffitto)':26} {len(orc):6} {orc.mean():+9.3f}")
    print(f"holding mediano E1 = {real['hold_e1'].median():.0f} giorni")

    print("\n--- confronti appaiati (stesse entrate) ---")
    for a, b in (("E1", "E2"), ("E1", "E3"), ("E1b", "E2"), ("E1", "E1b")):
        lo, hi, pt = paired_ci(real, a, b)
        flag = "  <-- A>B" if lo > 0 else ("  <-- A<B" if hi < 0 else "  <-- nullo")
        print(f"  {a:4} - {b:4}  diff={pt:+.3f}  BCa95[{lo:+.3f},{hi:+.3f}]{flag}")

    print("\n--- vs BASELINE RANDOM risk-matched (stessa uscita) ---")
    if len(rand):
        # Il matching si VERIFICA, non si dichiara. Nota sulla convenzione, che qui
        # non era mai stata scritta: il rischio e' matchato **in unita' di ATR locale**
        # (1 ATR per entrambi i bracci), NON in unita' di prezzo. E' coerente con la
        # regola — l'R della strategia e' 1 ATR all'ingresso — ma significa che le due
        # gambe rischiano importi diversi in valuta, e per questo `R_price` sta fra gli
        # ESITI osservati e non fra le dimensioni matchate.
        print(check_matching(real, rand, link="sigid",
                             exact=("sym", "side", "year"), numeric=(),
                             observed=("R_price", "hold_e1")))
        for col in ("E1", "oracle"):
            lo, hi, pt = cluster_diff(real, rand, col)
            flag = ("  <-- reale > random" if lo > 0 else
                    "  <-- reale < random" if hi < 0 else "  <-- indistinguibile")
            print(f"  {col:8} reale={real[col].mean():+.3f}  random={rand[col].mean():+.3f}"
                  f"  diff={pt:+.3f}  CI95[{lo:+.3f},{hi:+.3f}]{flag}")

    print("\n--- breadth per GRUPPO ---")
    print(f"  {'gruppo':10} {'n':>6} {'E1':>8} {'E2':>8} {'E3':>8} {'vs random':>11}")
    ok_g = 0
    for g, gg in real.groupby("group"):
        gr = rand[rand["group"] == g] if len(rand) else pd.DataFrame()
        d = (gg["E1"].mean() - gr["E1"].mean()) if len(gr) else np.nan
        ok_g += int(gg["E1"].mean() > 0)
        print(f"  {g:10} {len(gg):6} {gg['E1'].mean():+8.3f} {gg['E2'].mean():+8.3f} "
              f"{gg['E3'].mean():+8.3f} {d:+11.3f}")
    print(f"  gruppi con E1 > 0: {ok_g}/{real['group'].nunique()}")

    print("\n--- breadth per ANNO (E[R] di E1) ---")
    yl, pos, tot = [], 0, 0
    for y, gg in real.groupby("year"):
        if len(gg) < 10:
            continue
        tot += 1
        pos += int(gg["E1"].mean() > 0)
        yl.append(f"{y}:{gg['E1'].mean():+.2f}")
    print("  " + "  ".join(yl))
    print(f"  anni positivi: {pos}/{tot}")

    v3 = (real["E1"] - 2 * real["cost_R"]).dropna().to_numpy()
    ci3 = _mean_ci(v3)
    print(f"\n--- stress 3x costi (E1): E[R]={v3.mean():+.3f} "
          f"BCa95[{ci3['low']:+.3f},{ci3['high']:+.3f}]")


def q2_report(real, t0, t1):
    print("\n" + "=" * 78)
    print("Q2 - IL PLAYGROUND (claim: piu' volatile/illiquido = piu' edge)")
    print("=" * 78)
    rows = []
    for sym, gg in real.groupby("sym"):
        rows.append({"sym": sym, "group": gg["group"].iloc[0],
                     "vol": realized_vol(sym, gg["group"].iloc[0], t0, t1), "er": gg["E1"].mean(), "n": len(gg)})
    per = pd.DataFrame(rows).dropna()
    print(f"\n  {'strumento':10} {'gruppo':9} {'vol ann.':>9} {'n':>5} {'E[R] E1':>9}")
    for _, r in per.sort_values("vol").iterrows():
        print(f"  {r['sym']:10} {r['group']:9} {100*r['vol']:8.1f}% "
              f"{int(r['n']):5} {r['er']:+9.3f}")

    grp = per.groupby("group").agg(vol=("vol", "mean"), er=("er", "mean"),
                                   n=("n", "sum")).reset_index().sort_values("vol")
    print(f"\n  --- PRIMARIO: n={len(grp)} gruppi ---")
    print(f"  {'gruppo':10} {'vol media':>10} {'E[R] medio':>11} {'n segnali':>10}")
    for _, r in grp.iterrows():
        print(f"  {r['group']:10} {100*r['vol']:9.1f}% {r['er']:+11.3f} {int(r['n']):10}")
    rho_g, p_g = spearman_perm(grp["vol"].to_numpy(), grp["er"].to_numpy())
    ok = "SUPPORTATO" if (rho_g > 0 and p_g < 0.05) else "ordinamento forte NON rilevato"
    print(f"\n  Spearman(vol, E[R]) sui GRUPPI: rho={rho_g:+.3f}  p(perm)={p_g:.4f}  -> {ok}")
    rho_s, p_s = spearman_perm(per["vol"].to_numpy(), per["er"].to_numpy())
    print(f"  (secondario, pseudo-replicato, NON decisivo): rho={rho_s:+.3f}  p={p_s:.4f}")
    print(f"  NB potenza: con n={len(grp)} serve rho ~0.74 per p<0.05. Un null = "
          f"'ordinamento forte non rilevato', NON 'claim falso'.")


def main():
    lookback = int(sys.argv[1]) if len(sys.argv) > 1 else LOOKBACK
    cov = universe_from_coverage()
    t_start = cov["start"].max()
    print("=" * 78)
    print("TREND - uscita a coda aperta x gradiente di liquidita'")
    print("Pre-registrazione: docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md")
    print("=" * 78)
    print(f"\nUniverso: {len(cov)} strumenti, {cov['group'].nunique()} gruppi. "
          f"Lookback entrata = {lookback}g")
    for g, gg in cov.groupby("group"):
        print(f"  {g:10} {len(gg)} | {', '.join(gg['sym'])} | start max {gg['start'].max().date()}")
    print(f"\nW2 comune = {t_start.date()} -> fine (TUTTI gli strumenti)")

    w1 = cov[cov["start"] <= pd.Timestamp("2012-06-30")]
    print(f"W1 lunga  = 2012+ ({len(w1)} strumenti: {', '.join(sorted(w1['group'].unique()))})")

    real1, rand1 = run_all(w1, lookback)
    if len(real1):
        q1_report(real1, rand1, f"W1 2012+ | lookback {lookback}")

    real2, rand2 = run_all(cov, lookback, t0=t_start)
    if len(real2):
        q1_report(real2, rand2, f"W2 comune {t_start.date()}+ | lookback {lookback}")
        q2_report(real2, t_start, None)

    print("\n" + "=" * 78)
    print("W3 - STAZIONARIETA' (regola: se esiste SOLO post-2020, non e' un edge)")
    print("=" * 78)
    for lab, a, b in (("pre-2020 ", None, pd.Timestamp("2019-12-31")),
                      ("post-2020", pd.Timestamp("2020-01-01"), None)):
        r_, d_ = run_all(w1, lookback, t0=a, t1=b)
        if not len(r_):
            continue
        v = r_["E1"].dropna().to_numpy()
        ci = _mean_ci(v)
        lo, hi, pt = cluster_diff(r_, d_, "E1") if len(d_) else (np.nan, np.nan, np.nan)
        print(f"  {lab}  n={len(v):5}  E[R] E1={v.mean():+.3f} "
              f"BCa95[{ci['low']:+.3f},{ci['high']:+.3f}]   vs random diff={pt:+.3f} "
              f"CI[{lo:+.3f},{hi:+.3f}]")

    if len(real2):
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trades_w2.csv")
        real2.to_csv(out, index=False)
        print(f"\nTrade log -> {out}")


if __name__ == "__main__":
    main()
