"""Mean-reversion vol (non-level) — backtester di portafoglio. Spec PRE-REGISTRATA
(docs/MEANREV_PREREGISTRATION.md). Riusa data/sizing/validazione di strategies/tsmom/backtest.py.

Segnale: z-score del prezzo (z = (close - SMA_N)/STD_N, dati <= t). Entry contro-stiramento
(z<=-Z_ENTRY long / z>=+Z_ENTRY short); exit a ritorno alla media (z cambia segno) o time-stop
(MAX_HOLD) o vol-stop (|z|>=Z_STOP). Vol-target per asset; posizione a close t guadagna ret t+1.

Uso: python strategies/meanrev/backtest.py   (dalla root)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402
from strategies.tsmom.backtest import (ASSETS, COST_BPS, PPY, TARGET_VOL,  # noqa: E402
                                       VOL_WIN, load_closes, per_year)

SEED = 42
N_PRIMARY, Z_ENTRY_PRIMARY = 10, 1.0
Z_STOP, MAX_HOLD = 3.0, 10
NS = [5, 10, 20]
ZS = [1.0, 2.0]


def mr_weights(closes: pd.DataFrame, N: int, z_entry: float,
               z_stop: float = Z_STOP, max_hold: int = MAX_HOLD) -> pd.DataFrame:
    sma = closes.rolling(N).mean()
    sd = closes.rolling(N).std()
    z = (closes - sma) / sd
    vol = closes.pct_change().rolling(VOL_WIN).std() * np.sqrt(PPY)
    W = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    for a in closes.columns:
        za, va = z[a].values, vol[a].values
        w = np.full(len(za), np.nan)
        pos, held = 0, 0
        for i in range(len(za)):
            zi = za[i]
            if not np.isfinite(zi):
                pos, held = 0, 0
                continue
            if pos == 0:
                if zi <= -z_entry:
                    pos, held = 1, 0
                elif zi >= z_entry:
                    pos, held = -1, 0
            else:
                held += 1
                if pos == 1 and (zi >= 0 or held >= max_hold or zi <= -z_stop):
                    pos = 0
                elif pos == -1 and (zi <= 0 or held >= max_hold or zi >= z_stop):
                    pos = 0
            if pos != 0 and np.isfinite(va[i]) and va[i] > 0:
                w[i] = pos * (TARGET_VOL / va[i])
        W[a] = w
    return W


def strategy_returns(closes, N, z_entry):
    rets = closes.pct_change()
    W = mr_weights(closes, N, z_entry)
    cost_frac = pd.Series({a: COST_BPS[a] / 1e4 for a in closes.columns})
    turnover = W.fillna(0).diff().abs()
    cost = (turnover * cost_frac).mean(axis=1)
    contrib = W.shift(1) * rets
    portret = contrib.mean(axis=1) - cost
    return portret.dropna(), W, contrib


def per_asset_sharpe(closes, N, z_entry):
    rets = closes.pct_change()
    W = mr_weights(closes, N, z_entry)
    out = {}
    for a in closes.columns:
        r = (W[a].shift(1) * rets[a]).dropna()
        r = r[r != 0]
        if r.size > 60:
            out[a] = qm.sharpe_ratio(r.values, periods_per_year=PPY)
    return out


def variant_matrix(closes):
    s = {}
    for N in NS:
        for z in ZS:
            pr, _, _ = strategy_returns(closes, N, z)
            if pr.size > 250:            # scarta varianti con troppo pochi trade
                s[f"N{N}_Z{z}"] = pr
    return pd.DataFrame(s).dropna()


def _line(name, r):
    md = qm.max_drawdown(r.values)["max_dd"]
    return (f"  {name:14} n={r.size:5} Sharpe={qm.sharpe_ratio(r.values, periods_per_year=PPY):+.2f} "
            f"Sortino={qm.sortino_ratio(r.values, periods_per_year=PPY):+.2f} "
            f"CAGR={((1+r).prod()**(PPY/max(r.size,1))-1)*100:+.1f}% maxDD={md*100:+.1f}%")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    closes = load_closes()
    print(f"Asset: {list(closes.columns)}\nDate: {closes.index[0].date()} -> {closes.index[-1].date()} "
          f"({len(closes)} righe)\n")

    print("===== VARIANTI (N × Z_ENTRY) =====")
    for N in NS:
        for z in ZS:
            pr, _, _ = strategy_returns(closes, N, z)
            print(_line(f"N{N} Z{z}", pr))

    print(f"\n===== PRIMARIO: N={N_PRIMARY}, Z_ENTRY={Z_ENTRY_PRIMARY} =====")
    pr, W, contrib = strategy_returns(closes, N_PRIMARY, Z_ENTRY_PRIMARY)
    print(_line("PRIMARIO", pr))

    yr = per_year(pr)
    pos_years = int((yr > 0).sum())
    print(f"\n  anni positivi: {pos_years}/{yr.size}")
    print("  " + "  ".join(f"{y}:{v*100:+.0f}%" for y, v in yr.items()))

    sasset = per_asset_sharpe(closes, N_PRIMARY, Z_ENTRY_PRIMARY)
    pos_assets = sum(1 for v in sasset.values() if v > 0)
    tot = contrib.sum()
    tot = tot[tot.index.isin(closes.columns)]
    share = (tot / tot[tot > 0].sum()).sort_values(ascending=False)
    top_asset, top_share = share.index[0], float(share.iloc[0])
    print(f"\n  breadth: {pos_assets}/{len(sasset)} asset con Sharpe standalone > 0")
    print("  Sharpe/asset: " + "  ".join(f"{a}:{s:+.2f}" for a, s in sorted(sasset.items(), key=lambda x: -x[1])))
    print(f"  top asset per PnL: {top_asset} = {top_share*100:.0f}%")

    r = pr.values
    print("\n===== VALIDAZIONE =====")
    bca = qm.bca_bootstrap_ci(r, conf=0.95, n_boot=3000, seed=SEED, periods_per_year=PPY)
    print(f"  BCa Sharpe: {bca['point']:+.2f}  CI95=[{bca['low']:+.2f}, {bca['high']:+.2f}]  "
          f"(lower>0? {'SI' if bca['low'] > 0 else 'NO'})")
    dsr = qm.deflated_sharpe_ratio(r, n_trials=6, periods_per_year=PPY)
    print(f"  DSR: SR={dsr['sr_observed']:+.2f} thr={dsr['sr_threshold']:+.2f} dsr={dsr['dsr']:.3f} "
          f"significant_95={dsr['significant_95']}")
    mc = qm.mc_permutation_test(r, n_perm=2000, block_size=5, seed=SEED, periods_per_year=PPY)
    print(f"  MC-permutation: p={mc['p_value']:.3f}")
    M = variant_matrix(closes)
    pbo = qm.pbo_cscv(M.values, s=16)
    print(f"  PBO/CSCV (6 varianti): {pbo['pbo']:.3f}")
    wrc = qm.whites_reality_check(M.values, n_boot=1000, block_size=5, seed=SEED)
    print(f"  White's RC: best='{M.columns[wrc['best_strategy_idx']]}' p={wrc['p_value']:.3f}")
    if r.size > 6 * 252:
        wf = qm.walk_forward(r, train_size=5 * 252, test_size=252, anchored=True, periods_per_year=PPY)
        print(f"  Walk-forward: IS={wf.is_mean:+.2f} OOS={wf.oos_mean:+.2f} (degrado={wf.degradation*100:+.0f}%)")

    print("\n===== OVERLAY PROP-LIKE (scala 10% vol) =====")
    exp_vol = pr.expanding(min_periods=60).std() * np.sqrt(PPY)
    scaled = (pr * (0.10 / exp_vol).shift(1).clip(upper=10).fillna(0)).dropna()
    if scaled.size:
        eq = (1 + scaled).cumprod(); dd = eq / eq.cummax() - 1
        print(f"  vol={scaled.std()*np.sqrt(PPY)*100:.1f}%  maxDD={dd.min()*100:+.1f}%  "
              f"peggior giorno={scaled.min()*100:+.2f}%")

    print("\n===== VERDETTO (criteri PRE-REGISTRATI) =====")
    c1 = bca["low"] > 0
    c2 = bool(dsr["significant_95"])
    c3 = (pos_assets / max(len(sasset), 1) > 0.50) and (top_share < 0.50)
    c4 = pos_years / max(yr.size, 1) > 0.50
    c5 = wrc["p_value"] < 0.05
    for i, (lbl, c) in enumerate([("BCa lower>0", c1), ("DSR sig", c2), ("breadth>50% & top<50%", c3),
                                  ("anni+ maggioranza", c4), ("White RC p<0.05", c5)], 1):
        print(f"  {i}) {lbl:22} {c}")
    go = c1 and c2 and c3 and c4 and c5
    print(f"\n  --> {'GO' if go else 'NO-GO / kill-switch: passa a stagionalita/calendario'}")


if __name__ == "__main__":
    main()
