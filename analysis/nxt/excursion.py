"""NXT — soffitto dell'uscita: misura di escursione (MFE/MAE) sui setup gia' pre-registrati.

Rianalisi descrittiva del backtest NXT (NO-GO 2026-07-17). NON cambia nessuna regola:
riusa zigzag/build_legs/fill di backtest.py e misura una quantita' che quel motore non
registrava — quanto lontano e' andato il prezzo a favore PRIMA di tornare allo stop.

Serve a rispondere: esiste UNA QUALUNQUE uscita a coda aperta (niente TP, niente BE) che
riporti E[R] sopra zero? La MFE e' il limite superiore invalicabile di qualsiasi exit rule.

Soglie DICHIARATE PRIMA dell'esecuzione in docs/NXT_EXIT_CEILING_ADDENDUM.md:
  S1  E[R]_oracolo = media di max(MFE, -1) - costi   -> se <= 0: kill immediato
  S2  E[MFE | MFE >= 3R] > 6.5R                      -> se no: tesi "lascia correre" morta
  S3  breadth: maggioranza di asset E di anni sopra soglia

Uso: python analysis/nxt/excursion.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import backtest as nxt  # noqa: E402  (motore pre-registrato, immutato)
from core import quant_metrics as qm  # noqa: E402

W_THRESHOLD = 6.5   # S2: rendimento medio richiesto ai vincenti (vedi addendum)
TP_LEVEL = 3.0      # soglia "vincente" del backtest originale (RR 1:3)
M_BASELINE = 3      # S4: controlli random risk-matched per setup reale


def excursion(leg, H, L, C, sym, entry_fib=nxt.ENTRY_FIB):
    """Un setup -> dict con MFE/MAE in R, R terminale, senza TP e senza break-even.

    Fill identico a backtest.simulate() (look-ahead-safe, solo da conf_idx in poi).
    Poi cammina fino a SL grezzo o MAX_HOLD.
    Bound pessimistico: nella barra che tocca lo stop, l'escursione favorevole non si conta.
    """
    side, hi, lo, rng = leg["side"], leg["hi"], leg["lo"], leg["rng"]
    b, cb = leg["end_idx"], leg["conf"]

    if side == "BUY":
        entry = hi - entry_fib * rng
        sl = hi - nxt.SL_FIB * rng
        risk = entry - sl
    else:
        entry = lo + entry_fib * rng
        sl = lo + nxt.SL_FIB * rng
        risk = sl - entry
    if risk <= 0:
        return None

    # ---- fill del limite (copia fedele di backtest.simulate) ----
    f = None
    for j in range(max(cb, b + 1), min(b + 1 + nxt.FILL_WINDOW, len(H))):
        if side == "BUY":
            if L[j] <= sl:
                if L[j] <= entry:
                    f = j
                    break
                return None
            if L[j] <= entry:
                f = j
                break
        else:
            if H[j] >= sl:
                if H[j] >= entry:
                    f = j
                    break
                return None
            if H[j] >= entry:
                f = j
                break
    if f is None:
        return None

    # ---- cammino senza TP e senza BE ----
    mfe_pess, mfe_opt, mae = -np.inf, -np.inf, 0.0
    reason, hold, terminal = "MAXHOLD", 0, np.nan
    last = min(f + nxt.MAX_HOLD, len(H)) - 1
    for j in range(f, last + 1):
        if side == "BUY":
            fav = (H[j] - entry) / risk
            adv = (entry - L[j]) / risk
            hit_sl = L[j] <= sl
        else:
            fav = (entry - L[j]) / risk
            adv = (H[j] - entry) / risk
            hit_sl = H[j] >= sl
        mfe_opt = max(mfe_opt, fav)
        mae = max(mae, min(adv, 1.0))
        if hit_sl:
            reason, hold, terminal = "SL", j - f, -1.0
            break
        mfe_pess = max(mfe_pess, fav)
        if j == last:
            reason, hold = "MAXHOLD", j - f
            terminal = (C[j] - entry) / risk if side == "BUY" else (entry - C[j]) / risk

    if not np.isfinite(mfe_pess):
        mfe_pess = -1.0
    cost_R = nxt.SPREAD.get(sym, 0.0) / risk
    return {
        "asset": sym, "side": side, "entry_idx": f, "risk": risk, "cost_R": cost_R,
        "mfe_pess": mfe_pess - cost_R, "mfe_opt": mfe_opt - cost_R,
        "mae": mae, "reason": reason, "hold": hold,
        "R_term": terminal - cost_R,
        "R_oracle": max(mfe_pess, -1.0) - cost_R,
    }


def walk_from(entry_idx, entry, sl, side, H, L, C, sym):
    """Cammino identico a excursion() ma a partire da un fill IMPOSTO (baseline random)."""
    risk = (entry - sl) if side == "BUY" else (sl - entry)
    if risk <= 0:
        return None
    mfe_pess, mae = -np.inf, 0.0
    reason, hold, terminal = "MAXHOLD", 0, np.nan
    last = min(entry_idx + nxt.MAX_HOLD, len(H)) - 1
    if last <= entry_idx:
        return None
    for j in range(entry_idx, last + 1):
        if side == "BUY":
            fav, adv = (H[j] - entry) / risk, (entry - L[j]) / risk
            hit_sl = L[j] <= sl
        else:
            fav, adv = (entry - L[j]) / risk, (H[j] - entry) / risk
            hit_sl = H[j] >= sl
        mae = max(mae, min(adv, 1.0))
        if hit_sl:
            reason, hold, terminal = "SL", j - entry_idx, -1.0
            break
        mfe_pess = max(mfe_pess, fav)
        if j == last:
            reason, hold = "MAXHOLD", j - entry_idx
            terminal = (C[j] - entry) / risk if side == "BUY" else (entry - C[j]) / risk
    if not np.isfinite(mfe_pess):
        mfe_pess = -1.0
    cost_R = nxt.SPREAD.get(sym, 0.0) / risk
    return {"asset": sym, "side": side, "entry_idx": entry_idx, "risk": risk,
            "mfe_pess": mfe_pess - cost_R, "mae": mae, "reason": reason, "hold": hold,
            "R_term": terminal - cost_R, "R_oracle": max(mfe_pess, -1.0) - cost_R}


def run_asset(sym, rng=None, m_random=0):
    """Setup reali; se m_random>0 genera anche il baseline random risk-matched.

    Baseline: STESSO asset, STESSO lato, STESSO rischio in unita' di prezzo, ma entrata
    a un istante CASUALE dello stesso anno. Isola cio' che la struttura (pivot + gamba +
    ritracciamento) aggiunge rispetto a "stop stretto tenuto per 20 giorni".
    """
    d = nxt.load_h1(sym)
    H, L, C = d["high"].values, d["low"].values, d["close"].values
    yrs = d["time"].dt.year.values
    A = nxt.atr(H, L, C)
    legs = nxt.build_legs(nxt.zigzag(H, L), A)
    by_year = {y: np.flatnonzero(yrs == y) for y in np.unique(yrs)}
    real, rand = [], []
    for lg in legs:
        r = excursion(lg, H, L, C, sym)
        if r is None:
            continue
        y = int(yrs[r["entry_idx"]])
        legid = f"{sym}:{lg['end_idx']}"
        r["year"], r["legid"] = y, legid
        real.append(r)
        for _ in range(m_random):
            pool = by_year[y]
            k = int(rng.choice(pool))
            if k + 2 >= len(H):
                continue
            e = C[k]
            sl = e - r["risk"] if r["side"] == "BUY" else e + r["risk"]
            rr = walk_from(k + 1, e, sl, r["side"], H, L, C, sym)
            if rr is not None:
                rr["year"], rr["legid"] = y, legid
                rand.append(rr)
    return pd.DataFrame(real), pd.DataFrame(rand)


def cluster_ci(df, col, n_boot=3000, seed=nxt.SEED):
    """CI 95% sulla media di `col`, ricampionando i legid (cluster)."""
    rng = np.random.default_rng(seed)
    g = df.groupby("legid")[col].apply(list)
    keys = list(g.index)
    vals = [g[k] for k in keys]
    idx = np.arange(len(keys))
    boots = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        pool = [v for k in s for v in vals[k]]
        if pool:
            boots.append(float(np.mean(pool)))
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def main():
    print("=" * 78)
    print("NXT — SOFFITTO DELL'USCITA (MFE/MAE, niente TP, niente BE)")
    print("Soglie dichiarate prima: docs/NXT_EXIT_CEILING_ADDENDUM.md")
    print("=" * 78)

    rng = np.random.default_rng(nxt.SEED)
    parts = [run_asset(s, rng, M_BASELINE) for s in nxt.ASSETS]
    df = pd.concat([p[0] for p in parts], ignore_index=True)
    dfr = pd.concat([p[1] for p in parts], ignore_index=True)
    n = len(df)
    print(f"\nSetup riempiti (entry_fib={nxt.ENTRY_FIB}): n={n}  "
          f"asset={df['asset'].nunique()}  anni={df['year'].nunique()}"
          f"  [{df['year'].min()}-{df['year'].max()}]")

    stopped = (df["reason"] == "SL").mean()
    print(f"Stop-out senza TP: {100*stopped:.1f}%   MAE mediana: {df['mae'].median():.2f}R"
          f"   holding mediano: {df['hold'].median():.0f} barre H1")

    # ---- distribuzione MFE ----
    q = [10, 25, 50, 75, 90, 95, 99]
    print("\nDistribuzione MFE (pessimistica, dopo costi), in R:")
    print("  " + "  ".join(f"p{p}={np.percentile(df['mfe_pess'], p):+.2f}" for p in q))
    print(f"  media={df['mfe_pess'].mean():+.3f}   max={df['mfe_pess'].max():+.2f}")
    for thr in (1, 2, 3, 5, 6.5, 10):
        print(f"  P(MFE >= {thr:>4}R) = {100*(df['mfe_pess'] >= thr).mean():5.2f}%"
              f"   (n={int((df['mfe_pess'] >= thr).sum())})")

    # ---- S1: soffitto dell'oracolo ----
    print("\n" + "-" * 78)
    orc = df["R_oracle"].to_numpy()
    lo, hi = cluster_ci(df, "R_oracle")
    verdict1 = "PASSA" if lo > 0 else ("fallisce" if np.mean(orc) <= 0 else "punto>0 ma CI include 0")
    print(f"S1  E[R] ORACOLO (esce sempre al massimo) = {orc.mean():+.3f}R"
          f"   CI95 cluster [{lo:+.3f}, {hi:+.3f}]   -> {verdict1}")
    print(f"    confronto: E[R] del backtest originale (TP 1:3, BE 2R) = -0.44R")
    print(f"    R terminale senza TP ne' BE (tenere fino a stop/MAX_HOLD) = {df['R_term'].mean():+.3f}R")

    # ---- S2: soglia della tesi ----
    win = df[df["mfe_pess"] >= TP_LEVEL]
    p_win = len(win) / n
    if len(win):
        w_mean = win["mfe_pess"].mean()
        need = (1 - p_win) / p_win
        verdict2 = "PASSA" if w_mean > W_THRESHOLD else "FALLISCE"
        print(f"\nS2  Vincenti (MFE >= {TP_LEVEL}R): {100*p_win:.1f}% (n={len(win)})")
        print(f"    E[MFE | MFE >= 3R] = {w_mean:+.2f}R   soglia dichiarata > {W_THRESHOLD}R"
              f"   -> {verdict2}")
        print(f"    (soglia ricalcolata sul tasso osservato: servirebbe W > {need:.2f}R)")
        print(f"    mediana={win['mfe_pess'].median():.2f}R   p90={np.percentile(win['mfe_pess'],90):.2f}R")

    # ---- S3: breadth ----
    print("\n" + "-" * 78)
    print("S3  BREADTH — per asset:")
    print(f"    {'asset':10} {'n':>5} {'stop%':>7} {'E[R]orac':>10} {'P(MFE>=3R)':>11} {'E[MFE|>=3R]':>12}")
    ok_a = 0
    for a, g in df.groupby("asset"):
        w = g[g["mfe_pess"] >= TP_LEVEL]
        wm = w["mfe_pess"].mean() if len(w) else np.nan
        ok = np.isfinite(wm) and wm > W_THRESHOLD and g["R_oracle"].mean() > 0
        ok_a += bool(ok)
        print(f"    {a:10} {len(g):5} {100*(g['reason']=='SL').mean():6.1f}% "
              f"{g['R_oracle'].mean():+10.3f} {100*len(w)/len(g):10.1f}% {wm:+12.2f}"
              f"{'  <--' if ok else ''}")
    print(f"    asset che superano S1+S2: {ok_a}/{df['asset'].nunique()}")

    print("\n    per anno:")
    ok_y = 0
    yrs_n = 0
    for y, g in df.groupby("year"):
        if len(g) < 20:
            continue
        yrs_n += 1
        w = g[g["mfe_pess"] >= TP_LEVEL]
        wm = w["mfe_pess"].mean() if len(w) else np.nan
        ok = np.isfinite(wm) and wm > W_THRESHOLD and g["R_oracle"].mean() > 0
        ok_y += bool(ok)
        print(f"    {y}  n={len(g):4}  E[R]orac={g['R_oracle'].mean():+.3f}"
              f"  E[MFE|>=3R]={wm:+.2f}{'  <--' if ok else ''}")
    print(f"    anni (n>=20) che superano S1+S2: {ok_y}/{yrs_n}")

    # ---- S4: baseline random risk-matched (aggiunto DOPO S1-S3, alza l'asticella) ----
    print("\n" + "=" * 78)
    print("S4  BASELINE RANDOM risk-matched (stesso asset/lato/rischio, istante casuale)")
    print("    Domanda: la STRUTTURA (pivot+gamba+ritracciamento) alza il soffitto,")
    print("    o e' solo l'effetto 'stop stretto tenuto 20 giorni'?")
    print(f"    n_random={len(dfr)} ({M_BASELINE} controlli per setup reale)")
    for col, lab in (("R_oracle", "E[R] oracolo"), ("mfe_pess", "MFE media"),
                     ("R_term", "R terminale (hold)")):
        rv, cv = df[col].mean(), dfr[col].mean()
        lo_, hi_, pt = nxt.cluster_diff_ci(df, dfr, col=col, n_boot=2000)
        flag = "  <-- reale > random" if lo_ > 0 else ("  <-- reale < random" if hi_ < 0 else "  <-- indistinguibile")
        print(f"    {lab:22} reale={rv:+7.3f}  random={cv:+7.3f}  diff={pt:+6.3f}"
              f"  CI95[{lo_:+.3f},{hi_:+.3f}]{flag}")
    pr = 100 * (df["mfe_pess"] >= TP_LEVEL).mean()
    pc = 100 * (dfr["mfe_pess"] >= TP_LEVEL).mean()
    wr_ = df.loc[df["mfe_pess"] >= TP_LEVEL, "mfe_pess"].mean()
    wc_ = dfr.loc[dfr["mfe_pess"] >= TP_LEVEL, "mfe_pess"].mean()
    print(f"    {'P(MFE>=3R)':22} reale={pr:+7.2f}% random={pc:+7.2f}%")
    print(f"    {'E[MFE|>=3R]':22} reale={wr_:+7.2f}  random={wc_:+7.2f}")
    print(f"    {'stop-out %':22} reale={100*(df['reason']=='SL').mean():+7.2f}% "
          f"random={100*(dfr['reason']=='SL').mean():+7.2f}%")

    print("\n    BREADTH del confronto (kill duro n.2 = non batte il random matched):")
    print(f"    {'asset':10} {'orac reale':>11} {'orac random':>12} {'diff':>8} {'CI95':>20}")
    won = 0
    for a in sorted(df["asset"].unique()):
        ga, gb = df[df["asset"] == a], dfr[dfr["asset"] == a]
        lo_, hi_, pt = nxt.cluster_diff_ci(ga, gb, col="R_oracle", n_boot=2000)
        won += int(lo_ > 0)
        print(f"    {a:10} {ga['R_oracle'].mean():+11.3f} {gb['R_oracle'].mean():+12.3f}"
              f" {pt:+8.3f} [{lo_:+.3f},{hi_:+.3f}]")
    print(f"    asset in cui il reale BATTE il random: {won}/{df['asset'].nunique()}")

    print("\n    per anno (diff oracolo reale - random):")
    wy, ny = 0, 0
    for y in sorted(df["year"].unique()):
        ga, gb = df[df["year"] == y], dfr[dfr["year"] == y]
        if len(ga) < 20:
            continue
        ny += 1
        d_ = ga["R_oracle"].mean() - gb["R_oracle"].mean()
        wy += int(d_ > 0)
        print(f"    {y}  diff={d_:+.3f}", end="   " if y % 3 else "\n")
    print(f"\n    anni in cui il reale batte il random: {wy}/{ny}")

    # ---- descrittivo (NON leva di rescue, vedi addendum §Cosa NON si fa) ----
    print("\n" + "-" * 78)
    print("DESCRITTIVO — MFE per quintile di rischio (entry->SL in ATR-equivalenti).")
    print("  NB: usare questo per selezionare il sottoinsieme che funziona = p-hacking (§4).")
    df["risk_q"] = df.groupby("asset")["risk"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]))
    for qi, g in df.groupby("risk_q", observed=True):
        w = g[g["mfe_pess"] >= TP_LEVEL]
        print(f"    Q{qi}  n={len(g):5}  E[R]orac={g['R_oracle'].mean():+.3f}"
              f"  P(MFE>=3R)={100*len(w)/len(g):5.1f}%"
              f"  E[MFE|>=3R]={w['mfe_pess'].mean() if len(w) else np.nan:+.2f}")

    out = os.path.join(HERE, "excursion_trades.csv")
    df.to_csv(out, index=False)
    print(f"\nTrade log -> {out}")


if __name__ == "__main__":
    main()
