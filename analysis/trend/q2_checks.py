"""Q2 — controlli avversariali sul risultato positivo del playground.

Il primario ha dato Spearman(vol, E[R]) = +0.857 p=0.006 sugli 8 gruppi. Prima di crederci,
tre spiegazioni alternative MECCANICHE che produrrebbero lo stesso ordinamento senza alcun edge:

  C1  CANALE MECCANICO. E[R] e' in unita' di ATR(20) all'entrata. Se gli asset ad alta vol
      hanno piu' vol-of-vol, l'ATR d'ingresso sottostima di piu' la volatilita' successiva;
      combinato con un'uscita ASIMMETRICA (il trail lascia correre e taglia), questo gonfia
      la coda destra in unita' di R senza alcun edge. Controllo: rifare la correlazione sulla
      DIFFERENZA reale - random, che ha stessa normalizzazione e stessa uscita.

  C2  BETA. Crypto ed energia hanno avuto rialzi enormi nel 2018-2026. Se il risultato viene
      tutto dal lato LONG, non e' "edge da illiquidita'": e' raccolta di beta. Controllo:
      E[R] separato per lato.

  C3  RUMORE. n per gruppo e' piccolo (crypto 99, bond 70) e gli strumenti dentro un gruppo
      sono correlati (BTC/ETH insieme). Controllo: CI per gruppo, e bootstrap dell'intera
      correlazione ricampionando gli STRUMENTI dentro i gruppi.

Uso: python analysis/trend/q2_checks.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from backtest import (LOOKBACK, SEED, realized_vol, run_all, spearman_perm,  # noqa: E402
                      universe_from_coverage, _mean_ci)


def main():
    cov = universe_from_coverage()
    t0 = cov["start"].max()
    real, rand = run_all(cov, LOOKBACK, t0=t0)
    print("=" * 78)
    print(f"Q2 CONTROLLI AVVERSARIALI — W2 {t0.date()}+  n_reali={len(real)}  n_random={len(rand)}")
    print("=" * 78)

    per = []
    for sym, gg in real.groupby("sym"):
        g = gg["group"].iloc[0]
        rr = rand[rand["sym"] == sym]
        per.append({
            "sym": sym, "group": g, "vol": realized_vol(sym, g, t0, None),
            "er": gg["E1"].mean(), "er_rand": rr["E1"].mean() if len(rr) else np.nan,
            "n": len(gg),
            "er_buy": gg.loc[gg.side == "BUY", "E1"].mean(),
            "er_sell": gg.loc[gg.side == "SELL", "E1"].mean(),
            "n_buy": int((gg.side == "BUY").sum()), "n_sell": int((gg.side == "SELL").sum()),
        })
    per = pd.DataFrame(per)
    per["er_net"] = per["er"] - per["er_rand"]

    # ---------- C1: correlazione sulla differenza vs random ----------
    print("\n--- C1  canale meccanico: correlazione su (reale - random) ---")
    grp = per.groupby("group").agg(vol=("vol", "mean"), er=("er", "mean"),
                                   er_rand=("er_rand", "mean"), n=("n", "sum")).reset_index()
    grp["er_net"] = grp["er"] - grp["er_rand"]
    grp = grp.sort_values("vol")
    print(f"  {'gruppo':10}{'vol':>8}{'E[R] reale':>12}{'E[R] random':>13}{'differenza':>12}")
    for _, r in grp.iterrows():
        print(f"  {r['group']:10}{100*r['vol']:7.1f}%{r['er']:+12.3f}{r['er_rand']:+13.3f}"
              f"{r['er_net']:+12.3f}")
    rho_raw, p_raw = spearman_perm(grp["vol"], grp["er"])
    rho_net, p_net = spearman_perm(grp["vol"], grp["er_net"])
    rho_rnd, p_rnd = spearman_perm(grp["vol"], grp["er_rand"])
    print(f"\n  Spearman(vol, E[R] reale)   rho={rho_raw:+.3f}  p={p_raw:.4f}   <- il primario")
    print(f"  Spearman(vol, E[R] random)  rho={rho_rnd:+.3f}  p={p_rnd:.4f}   <- se alto, e' MECCANICO")
    print(f"  Spearman(vol, differenza)   rho={rho_net:+.3f}  p={p_net:.4f}   <- il test controllato")

    # ---------- C2: beta / lato ----------
    print("\n--- C2  beta: E[R] per lato ---")
    print(f"  {'gruppo':10}{'n_buy':>7}{'E[R] BUY':>10}{'n_sell':>8}{'E[R] SELL':>11}")
    for g, gg in real.groupby("group"):
        b, s = gg[gg.side == "BUY"], gg[gg.side == "SELL"]
        print(f"  {g:10}{len(b):7}{b['E1'].mean():+10.3f}{len(s):8}{s['E1'].mean():+11.3f}")
    both = real.groupby("group").apply(
        lambda x: (x.loc[x.side == "BUY", "E1"].mean() > 0) and
                  (x.loc[x.side == "SELL", "E1"].mean() > 0), include_groups=False)
    print(f"  gruppi positivi su ENTRAMBI i lati: {int(both.sum())}/{len(both)}")

    # ---------- C3: rumore ----------
    print("\n--- C3  rumore: CI 95% per gruppo (E[R] reale) ---")
    for g, gg in real.groupby("group"):
        ci = _mean_ci(gg["E1"].to_numpy())
        star = "  <-- esclude 0" if (ci["low"] > 0 or ci["high"] < 0) else ""
        print(f"  {g:10} n={len(gg):4}  E[R]={gg['E1'].mean():+.3f} "
              f"BCa95[{ci['low']:+.3f},{ci['high']:+.3f}]{star}")

    print("\n  bootstrap della correlazione ricampionando gli STRUMENTI dentro i gruppi:")
    rng = np.random.default_rng(SEED)
    boots = []
    by_g = {g: gg for g, gg in per.groupby("group")}
    for _ in range(4000):
        vv, ee = [], []
        for g, gg in by_g.items():
            s = gg.sample(len(gg), replace=True, random_state=int(rng.integers(1 << 31)))
            vv.append(s["vol"].mean())
            ee.append(s["er"].mean())
        r, _ = spearman_perm(np.array(vv), np.array(ee), n_perm=1)
        boots.append(r)
    boots = np.array(boots)
    print(f"    rho mediano={np.median(boots):+.3f}  CI95=[{np.percentile(boots,2.5):+.3f},"
          f"{np.percentile(boots,97.5):+.3f}]  P(rho>0)={100*np.mean(boots>0):.1f}%")

    # ---------- controllo extra: senza crypto (il gruppo che traina) ----------
    g2 = grp[grp["group"] != "crypto"]
    r2, p2 = spearman_perm(g2["vol"], g2["er"])
    print(f"\n--- extra: togliendo la crypto (n={len(g2)}): rho={r2:+.3f} p={p2:.4f}")
    g3 = grp[~grp["group"].isin(["crypto", "energy"])]
    r3, p3 = spearman_perm(g3["vol"], g3["er"])
    print(f"    togliendo crypto+energy (n={len(g3)}): rho={r3:+.3f} p={p3:.4f}")


if __name__ == "__main__":
    main()
