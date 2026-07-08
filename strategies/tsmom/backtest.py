"""TSMOM multi-asset — backtester di PORTAFOGLIO (serie di rendimenti, non sintesi MT5).

Implementa la spec PRE-REGISTRATA (docs/TSMOM_PREREGISTRATION.md): segnale = sign del ritorno
trailing L giorni; sizing vol-target (60g) per asset a pari rischio; media di portafoglio;
ribilanciamento mensile/giornaliero; costi per turnover; look-ahead-safe (segnale/vol <= t-1,
posizione applicata al ritorno t+1). Validazione con core/quant_metrics.py.

Uso: python strategies/tsmom/backtest.py            (dalla root)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import quant_metrics as qm  # noqa: E402

DATA = os.path.join(ROOT, "analysis", "trading-bot-eval", "data")
ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF",
          "EURJPY.r", "GBPJPY.r", "EURGBP.r", "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD",
          "US500", "US100"]
COST_BPS = {a: 2.0 for a in ASSETS}
COST_BPS.update({"XAUUSD": 4.0, "XAGUSD": 4.0, "US500": 3.0, "US100": 3.0,
                 "BTCUSD": 8.0, "ETHUSD": 8.0})
LOOKBACKS = [21, 63, 126, 252]
REBALS = ["M", "D"]
TARGET_VOL = 0.10          # vol target per-asset (annualizzata)
VOL_WIN = 60
PPY = 252
SEED = 42


def load_closes() -> pd.DataFrame:
    cols = {}
    for a in ASSETS:
        p = os.path.join(DATA, f"{a}_D1.csv")
        if not os.path.exists(p):
            print(f"  [skip] {a}: file mancante"); continue
        df = pd.read_csv(p, parse_dates=["time"]).set_index("time")
        cols[a] = df["close"].astype(float)
    closes = pd.DataFrame(cols).sort_index()
    closes = closes[~closes.index.duplicated(keep="last")]
    return closes


def strategy_returns(closes: pd.DataFrame, lookback: int, rebal: str):
    """Ritorna (portret Series, weights_eff DataFrame, contrib DataFrame lordo)."""
    rets = closes.pct_change()
    mom = closes.pct_change(lookback)                 # ritorno trailing L (<= t)
    vol = rets.rolling(VOL_WIN).std() * np.sqrt(PPY)  # vol ann. (<= t)
    raw_w = np.sign(mom) * (TARGET_VOL / vol)
    raw_w = raw_w.replace([np.inf, -np.inf], np.nan)

    if rebal == "M":
        # ribilanciamento al primo giorno di trading di ogni mese, poi hold
        month = closes.index.to_period("M")
        is_reb = pd.Series(month, index=closes.index)
        is_reb = is_reb != is_reb.shift(1)
        w_eff = raw_w.copy()
        w_eff[~is_reb.values] = np.nan
        w_eff = w_eff.ffill()
    else:
        w_eff = raw_w

    # costi sul turnover (quando la posizione cambia)
    cost_frac = pd.Series({a: COST_BPS[a] / 1e4 for a in closes.columns})
    turnover = w_eff.diff().abs()
    cost = (turnover * cost_frac).mean(axis=1)

    contrib = w_eff.shift(1) * rets                   # posizione da t-1 sul ritorno t
    portret = contrib.mean(axis=1) - cost
    portret = portret.dropna()
    return portret, w_eff, contrib


def per_asset_sharpe(closes: pd.DataFrame, lookback: int) -> dict:
    """Sharpe standalone per asset (stessa regola su un solo strumento) = breadth."""
    rets = closes.pct_change()
    mom = closes.pct_change(lookback)
    vol = rets.rolling(VOL_WIN).std() * np.sqrt(PPY)
    w = (np.sign(mom) * (TARGET_VOL / vol)).replace([np.inf, -np.inf], np.nan)
    out = {}
    for a in closes.columns:
        r = (w[a].shift(1) * rets[a]).dropna()
        if r.size > 60:
            out[a] = qm.sharpe_ratio(r.values, periods_per_year=PPY)
    return out


def per_year(portret: pd.Series) -> pd.Series:
    return portret.groupby(portret.index.year).apply(lambda x: (1 + x).prod() - 1)


def variant_matrix(closes: pd.DataFrame):
    """Matrice T×8 dei rendimenti di portafoglio (lookback×rebal) su date comuni."""
    series = {}
    for lb in LOOKBACKS:
        for rb in REBALS:
            pr, _, _ = strategy_returns(closes, lb, rb)
            series[f"L{lb}_{rb}"] = pr
    M = pd.DataFrame(series).dropna()
    return M


def _line(name, r):
    md = qm.max_drawdown(r.values)["max_dd"]
    return (f"  {name:16} n={r.size:5} Sharpe={qm.sharpe_ratio(r.values, periods_per_year=PPY):+.2f} "
            f"Sortino={qm.sortino_ratio(r.values, periods_per_year=PPY):+.2f} "
            f"CAGR={((1+r).prod()**(PPY/r.size)-1)*100:+.1f}% maxDD={md*100:+.1f}%")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    closes = load_closes()
    print(f"Asset caricati: {list(closes.columns)}")
    print(f"Date: {closes.index[0].date()} -> {closes.index[-1].date()} ({len(closes)} righe)\n")

    print("===== VARIANTI (lookback × ribilanciamento) =====")
    for lb in LOOKBACKS:
        for rb in REBALS:
            pr, _, _ = strategy_returns(closes, lb, rb)
            print(_line(f"L{lb} {rb}", pr))

    # ---- PRIMARIO: 252, mensile ----
    print("\n===== PRIMARIO: lookback 252, ribilanciamento mensile =====")
    pr, w_eff, contrib = strategy_returns(closes, 252, "M")
    print(_line("PRIMARIO", pr))

    # per-anno (mono-anno?)
    yr = per_year(pr)
    pos_years = (yr > 0).sum()
    print(f"\n  anni positivi: {pos_years}/{yr.size}")
    print("  " + "  ".join(f"{y}:{v*100:+.0f}%" for y, v in yr.items()))

    # breadth + concentrazione (mono-asset?)
    sasset = per_asset_sharpe(closes, 252)
    pos_assets = sum(1 for v in sasset.values() if v > 0)
    tot_contrib = contrib.sum()
    tot_contrib = tot_contrib[tot_contrib.index.isin(closes.columns)]
    pnl_share = (tot_contrib / tot_contrib[tot_contrib > 0].sum()).sort_values(ascending=False)
    top_asset, top_share = pnl_share.index[0], pnl_share.iloc[0]
    print(f"\n  breadth: {pos_assets}/{len(sasset)} asset con Sharpe standalone > 0")
    print(f"  Sharpe standalone per asset: " +
          "  ".join(f"{a}:{s:+.2f}" for a, s in sorted(sasset.items(), key=lambda x: -x[1])))
    print(f"  top asset per PnL: {top_asset} = {top_share*100:.0f}% del PnL positivo (mono-asset se >50%)")

    # ---- validazione ----
    r = pr.values
    print("\n===== VALIDAZIONE (core/quant_metrics) =====")
    bca = qm.bca_bootstrap_ci(r, conf=0.95, n_boot=3000, seed=SEED, periods_per_year=PPY)
    print(f"  BCa Sharpe: point={bca['point']:+.2f}  CI95=[{bca['low']:+.2f}, {bca['high']:+.2f}]  "
          f"(lower>0? {'SI' if bca['low'] > 0 else 'NO'})")
    dsr = qm.deflated_sharpe_ratio(r, n_trials=8, periods_per_year=PPY)
    print(f"  DSR: SR={dsr['sr_observed']:+.2f} thr={dsr['sr_threshold']:+.2f} dsr={dsr['dsr']:.3f} "
          f"significant_95={dsr['significant_95']} (skew={dsr['skew']:+.2f} kurt={dsr['kurt_excess']:+.1f})")
    mc = qm.mc_permutation_test(r, n_perm=2000, block_size=5, seed=SEED, periods_per_year=PPY)
    print(f"  MC-permutation: p-value={mc['p_value']:.3f}")

    M = variant_matrix(closes)
    pbo = qm.pbo_cscv(M.values, s=16)
    print(f"  PBO/CSCV (8 varianti): pbo={pbo['pbo']:.3f}  (combos={pbo['n_combos']})")
    wrc = qm.whites_reality_check(M.values, n_boot=1000, block_size=5, seed=SEED)
    print(f"  White's RC (8 varianti): best='{M.columns[wrc['best_strategy_idx']]}' "
          f"p-value={wrc['p_value']:.3f}")

    if r.size > 6 * 252:
        wf = qm.walk_forward(r, train_size=5 * 252, test_size=252, anchored=True, periods_per_year=PPY)
        print(f"  Walk-forward (train 5y / test 1y, anchored): IS Sharpe={wf.is_mean:+.2f} "
              f"OOS Sharpe={wf.oos_mean:+.2f} (degrado={wf.degradation*100:+.0f}%)")

    # ---- overlay prop-like (scala a 10% vol, scaler espanso) ----
    print("\n===== OVERLAY PROP-LIKE (portafoglio scalato a 10% vol annuo) =====")
    exp_vol = pr.expanding(min_periods=60).std() * np.sqrt(PPY)
    scaler = (0.10 / exp_vol).shift(1).clip(upper=10).fillna(0)
    scaled = (pr * scaler).dropna()
    if scaled.size:
        eq = (1 + scaled).cumprod()
        dd = (eq / eq.cummax() - 1)
        worst_day = scaled.min()
        mo = scaled.groupby([scaled.index.year, scaled.index.month]).apply(lambda x: (1 + x).prod() - 1)
        print(f"  vol realizzata={scaled.std()*np.sqrt(PPY)*100:.1f}%  maxDD={dd.min()*100:+.1f}%  "
              f"peggior giorno={worst_day*100:+.2f}%  mesi positivi={(mo>0).mean()*100:.0f}%")

    # ---- verdetto a priori ----
    print("\n===== VERDETTO (criteri PRE-REGISTRATI) =====")
    c1 = bca["low"] > 0
    c2 = bool(dsr["significant_95"])
    c3 = (pos_assets / max(len(sasset), 1) > 0.50) and (top_share < 0.50)
    c4 = pos_years / max(yr.size, 1) > 0.50
    c5 = wrc["p_value"] < 0.05
    print(f"  1) BCa Sharpe lower>0 ............ {c1}")
    print(f"  2) DSR significant_95 ........... {c2}")
    print(f"  3) breadth>50% e top<50% PnL .... {c3}")
    print(f"  4) maggioranza anni positivi .... {c4}")
    print(f"  5) White's RC p<0.05 ............ {c5}")
    go = c1 and c2 and c3 and c4 and c5
    print(f"\n  --> {'GO (edge reale, procedi a forward)' if go else 'NO-GO / kill-switch: archivia TSMOM, passa a mean-reversion vol'}")


if __name__ == "__main__":
    main()
