"""CLI per TSMOM: scarica dati storici, esegui backtest, stampa metriche.

Uso:
    python -m strategies.tsmom backtest --symbol USDJPY=X --years 5
    python -m strategies.tsmom backtest --csv path/to/bars.csv

Le metriche statistiche (DSR, MC permutation) vengono delegate a
core.quant_metrics. Per la review completa con PBO, usare la skill
/quant-review su questa strategia (richiede matrice varianti).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

from core.quant_metrics import (
    calmar_ratio,
    deflated_sharpe_ratio,
    max_drawdown,
    mc_permutation_test,
    sharpe_ratio,
    sortino_ratio,
    tail_metrics,
)
from strategies.tsmom.strategy import (
    TSMOMCosts,
    TSMOMSignalConfig,
    TSMOMSizingConfig,
    TSMOMStopConfig,
    TSMOMStrategy,
)


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_strategy(cfg: dict) -> TSMOMStrategy:
    return TSMOMStrategy(
        signal_cfg=TSMOMSignalConfig(**cfg["signal"]),
        sizing_cfg=TSMOMSizingConfig(**cfg["sizing"]),
        stop_cfg=TSMOMStopConfig(
            atr_period=cfg["stop_loss"]["atr_period"],
            atr_mult=cfg["stop_loss"]["atr_mult"],
        ),
        costs=TSMOMCosts(**cfg.get("costs", {})),
    )


def _fetch_yfinance(symbol: str, years: int) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance non installato: pip install yfinance")
    end = pd.Timestamp.utcnow().normalize()
    start = end - pd.Timedelta(days=int(365.25 * years))
    df = yf.download(symbol, start=start, end=end, interval="1d", auto_adjust=False, progress=False)
    if df.empty:
        sys.exit(f"yfinance non ha restituito dati per {symbol}")
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    df = df[["open", "high", "low", "close"]].dropna()
    return df


def _load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close"]].dropna()


def cmd_backtest(args: argparse.Namespace) -> int:
    cfg = _load_config()
    strat = _build_strategy(cfg)

    if args.csv:
        bars = _load_csv(args.csv)
    else:
        bars = _fetch_yfinance(args.symbol, args.years)

    if len(bars) < cfg["filters"]["min_history_bars"]:
        sys.exit(f"history insufficiente: {len(bars)} < min {cfg['filters']['min_history_bars']}")

    out = strat.backtest(bars, initial_equity=args.equity)
    returns = out["daily_return"].dropna().to_numpy()

    # Metriche
    sr = sharpe_ratio(returns)
    sortino = sortino_ratio(returns)
    mdd = max_drawdown(returns)
    calmar = calmar_ratio(returns)
    tails = tail_metrics(returns)
    dsr = deflated_sharpe_ratio(returns, n_trials=args.n_trials)
    mc = mc_permutation_test(returns, n_perm=args.n_perm, block_size=5, seed=42)

    print(f"=== TSMOM backtest — {args.symbol or args.csv} — {len(bars)} bars ===")
    print(f"Final equity      : {out['equity'].iloc[-1]:.2f}")
    print(f"Sharpe (ann.)     : {sr:.3f}")
    print(f"Sortino           : {sortino:.3f}")
    print(f"Max drawdown      : {mdd['max_dd']*100:.2f}%")
    print(f"Calmar            : {calmar:.3f}")
    print(f"Skew / Kurt(ex.)  : {tails['skew']:.3f} / {tails['kurt_excess']:.3f}")
    print(f"CVaR 95 / 99      : {tails['cvar_95']*100:.2f}% / {tails['cvar_99']*100:.2f}%")
    print(f"DSR (N_trials={dsr['n_trials']}) : {dsr['dsr']:.4f}  (sig95={dsr['significant_95']})")
    print(f"  SR threshold    : {dsr['sr_threshold']:.3f}")
    print(f"MC perm p-value   : {mc['p_value']:.4f} (n_perm={args.n_perm})")

    if args.save_trades:
        out.to_csv(args.save_trades)
        print(f"Equity curve salvata in {args.save_trades}")

    # Sanity vs paper
    if sr < 0.4 or sr > 1.5:
        print(f"⚠ Sharpe fuori range Moskowitz et al. (0.7-1.0 atteso); red flag per quant review.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m strategies.tsmom")
    sub = parser.add_subparsers(dest="cmd", required=True)

    bt = sub.add_parser("backtest", help="Esegui il backtest TSMOM")
    bt.add_argument("--symbol", default="USDJPY=X", help="Ticker yfinance (default USDJPY=X)")
    bt.add_argument("--csv", default=None, help="Path a CSV OHLC alternativo a yfinance")
    bt.add_argument("--years", type=int, default=5)
    bt.add_argument("--equity", type=float, default=10_000.0)
    bt.add_argument("--n-trials", type=int, default=100,
                    help="Numero di trial stimato per DSR (default 100)")
    bt.add_argument("--n-perm", type=int, default=2000)
    bt.add_argument("--save-trades", default=None, help="Path CSV per equity curve")
    bt.set_defaults(func=cmd_backtest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
