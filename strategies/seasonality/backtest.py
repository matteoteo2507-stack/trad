"""Stagionalità Turn-of-Month — backtester + controllo giorni-casuali. Spec PRE-REGISTRATA
(docs/SEASONALITY_PREREGISTRATION.md). Riusa data/sizing/validazione di TSMOM.

TOM = ultimo giorno del mese (rank-dal-fondo ≤ n_last) o primi n_first del mese (rank ≤ n_first).
Metrica: (media ret TOM − media ret non-TOM) per non confondere l'effetto col drift (beta); la
finestra vera è confrontata con B finestre di GIORNI CASUALI dello stesso numero. Strategia
tradabile: long-in-TOM / flat, vol-target; confronto col buy&hold.

Uso: python strategies/seasonality/backtest.py   (dalla root)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402
from strategies.tsmom.backtest import (COST_BPS, PPY, TARGET_VOL, VOL_WIN,  # noqa: E402
                                       load_closes, per_year)

SEED = 42
WINDOWS = {"[-1,+3]": (1, 3), "[-1,+2]": (1, 2), "[0,+3]": (0, 3), "[-2,+3]": (2, 3)}
PRIMARY = "[-1,+3]"
B_RAND = 2000


def tom_mask(index, n_last, n_first):
    m = index.to_period("M")
    df = pd.DataFrame({"m": m}, index=index)
    df["rs"] = df.groupby("m").cumcount() + 1
    df["n"] = df.groupby("m")["rs"].transform("max")
    df["re"] = df["n"] - df["rs"] + 1
    mask = ((df["rs"] <= n_first) | (df["re"] <= n_last)).values
    return mask.astype(float)


def base_returns(closes):
    """(days×assets) rendimento long vol-targetato: posizione a t-1 guadagna ret t."""
    rets = closes.pct_change()
    vol = rets.rolling(VOL_WIN).std() * np.sqrt(PPY)
    base = (TARGET_VOL / vol).shift(1) * rets
    return base


def strat_portret(base, mask, cost_frac_mean):
    strat = base.values * mask[:, None]           # long solo nei giorni mask
    port = np.nanmean(strat, axis=1)
    turn = np.abs(np.diff(mask, prepend=mask[0]))
    port = port - turn * cost_frac_mean
    s = pd.Series(port, index=base.index).replace([np.inf, -np.inf], np.nan).dropna()
    return s


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    closes = load_closes()
    rets = closes.pct_change()
    base = base_returns(closes)
    cfm = float(np.mean([COST_BPS[a] / 1e4 for a in closes.columns]))
    idx = closes.index
    print(f"Asset: {list(closes.columns)}\nDate: {idx[0].date()} -> {idx[-1].date()} ({len(idx)} righe)\n")

    rng = np.random.default_rng(SEED)

    print("===== VARIANTI (finestra TOM): strategia long-TOM/flat =====")
    for name, (nl, nf) in WINDOWS.items():
        mask = tom_mask(idx, nl, nf)
        s = strat_portret(base, mask, cfm)
        print(f"  {name:8} giorni TOM={int(mask.sum())} ({100*mask.mean():.0f}%)  "
              f"Sharpe={qm.sharpe_ratio(s.values, periods_per_year=PPY):+.2f}  "
              f"CAGR={((1+s).prod()**(PPY/len(s))-1)*100:+.1f}%")

    # ---- PRIMARIO ----
    nl, nf = WINDOWS[PRIMARY]
    mask = tom_mask(idx, nl, nf)
    tomb = mask.astype(bool)
    print(f"\n===== PRIMARIO {PRIMARY} =====")

    # (a) TOM - nonTOM per asset (isola dal beta) + breadth
    diffs = {}
    for a in closes.columns:
        r = rets[a].values
        ok = np.isfinite(r)
        d = np.nanmean(r[tomb & ok]) - np.nanmean(r[~tomb & ok])
        diffs[a] = d * PPY * 100  # % annualizzato
    pos = sum(1 for v in diffs.values() if v > 0)
    print(f"  (TOM−nonTOM) annualizzato %/asset  [breadth positivi: {pos}/{len(diffs)}]:")
    print("   " + "  ".join(f"{a}:{v:+.1f}" for a, v in sorted(diffs.items(), key=lambda x: -x[1])))

    # (b) controllo GIORNI-CASUALI: la finestra TOM batte finestre casuali di pari numero?
    k = int(mask.sum())
    n = len(idx)
    # stat pooled = media su asset del (TOM−nonTOM)
    R = rets.values
    finite = np.isfinite(R)

    def pooled_diff(sel):
        tom = np.where(sel[:, None] & finite, R, np.nan)
        non = np.where((~sel)[:, None] & finite, R, np.nan)
        return np.nanmean(np.nanmean(tom, axis=0) - np.nanmean(non, axis=0))

    obs = pooled_diff(tomb)
    null = np.empty(B_RAND)
    for b in range(B_RAND):
        sel = np.zeros(n, dtype=bool)
        sel[rng.choice(n, size=k, replace=False)] = True
        null[b] = pooled_diff(sel)
    p_rand = float((null >= obs).mean())
    print(f"\n  pooled (TOM−nonTOM) giornaliero = {obs*1e4:+.2f} bps/g  |  "
          f"vs giorni casuali (n={B_RAND}): p={p_rand:.3f}  "
          f"(null medio {null.mean()*1e4:+.2f}, sd {null.std()*1e4:.2f} bps)")

    # (c) strategia long-TOM/flat: validazione + confronto B&H
    s = strat_portret(base, mask, cfm)
    bh = pd.Series(np.nanmean(base.values, axis=1), index=idx).dropna()
    r = s.values
    print(f"\n  strategia long-TOM/flat: Sharpe={qm.sharpe_ratio(r, periods_per_year=PPY):+.2f}  "
          f"maxDD={qm.max_drawdown(r)['max_dd']*100:+.1f}%  time-in-market={100*mask.mean():.0f}%")
    print(f"  buy&hold (long sempre): Sharpe={qm.sharpe_ratio(bh.values, periods_per_year=PPY):+.2f}  "
          f"CAGR={((1+bh).prod()**(PPY/len(bh))-1)*100:+.1f}%")
    cagr_s = (1 + s).prod() ** (PPY / len(s)) - 1
    cagr_b = (1 + bh).prod() ** (PPY / len(bh)) - 1
    print(f"  frazione del CAGR B&H catturata in ~{100*mask.mean():.0f}% del tempo: {100*cagr_s/cagr_b:.0f}%")

    bca = qm.bca_bootstrap_ci(r, conf=0.95, n_boot=3000, seed=SEED, periods_per_year=PPY)
    dsr = qm.deflated_sharpe_ratio(r, n_trials=len(WINDOWS), periods_per_year=PPY)
    mc = qm.mc_permutation_test(r, n_perm=2000, block_size=5, seed=SEED, periods_per_year=PPY)
    print(f"\n  BCa Sharpe: {bca['point']:+.2f} CI95=[{bca['low']:+.2f},{bca['high']:+.2f}] "
          f"(lower>0? {'SI' if bca['low']>0 else 'NO'})")
    print(f"  DSR: dsr={dsr['dsr']:.3f} significant_95={dsr['significant_95']}   MC p={mc['p_value']:.3f}")
    if r.size > 6 * 252:
        wf = qm.walk_forward(r, train_size=5*252, test_size=252, anchored=True, periods_per_year=PPY)
        print(f"  Walk-forward: IS={wf.is_mean:+.2f} OOS={wf.oos_mean:+.2f}")
    yr = per_year(s); posy = int((yr > 0).sum())
    print(f"  anni positivi: {posy}/{yr.size}")

    # focus indici (dove l'effetto è atteso)
    print("\n  --- focus indici (US500, US100) ---")
    for a in ("US500", "US100"):
        if a in closes.columns:
            print(f"   {a}: (TOM−nonTOM)={diffs[a]:+.1f}%/anno")

    # ---- verdetto ----
    print("\n===== VERDETTO (criteri PRE-REGISTRATI) =====")
    c1 = (obs > 0) and (p_rand < 0.05)
    c2 = (pos / len(diffs) > 0.50) or (diffs.get("US500", -1) > 0 and diffs.get("US100", -1) > 0)
    c3 = bca["low"] > 0 and bool(dsr["significant_95"])
    c4 = posy / max(yr.size, 1) > 0.50
    for i, (lbl, c) in enumerate([("TOM batte giorni casuali (p<0.05)", c1),
                                  ("breadth>50% o robusto sui 2 indici", c2),
                                  ("BCa lower>0 & DSR sig", c3),
                                  ("anni+ maggioranza", c4)], 1):
        print(f"  {i}) {lbl:38} {c}")
    go = c1 and c2 and c3 and c4
    print(f"\n  --> {'GO' if go else 'NO-GO: patto -> stop edge-hunting, pivot al pilastro passivo'}")


if __name__ == "__main__":
    main()
