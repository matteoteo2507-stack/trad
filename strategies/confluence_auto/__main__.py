"""CLI Confluence Auto.

Comandi:
    python -m strategies.confluence_auto generate
        → rigenera `levels_auto.yaml` con i detector configurati.

    python -m strategies.confluence_auto preview
        → dry-run: stampa i livelli generati ma non scrive il file.

    python -m strategies.confluence_auto generate --source yfinance
        → forza yfinance (utile in dev locale dove MT5 non c'è).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from .data_source import fetch_ohlc
from .detectors.confluence import AutoLevel, merge_to_auto_levels
from .detectors.poc import detect_poc_levels
from .detectors.sd import detect_sd_zones
from .detectors.sr import detect_sr_levels
from .writer import write_levels_yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("confluence_auto")

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _atr_simple(bars, period=14) -> float:
    """ATR ultimo valore (Wilder smoothing)."""
    import pandas as pd
    high, low, close = bars["high"], bars["low"], bars["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean().iloc[-1])


def _generate_for_symbol(
    symbol: str,
    symbol_cfg: dict[str, Any],
    full_cfg: dict[str, Any],
    source: str,
) -> list[AutoLevel]:
    """Pipeline completa per UN simbolo."""
    ds_cfg = full_cfg["data_source"]
    sr_cfg = full_cfg["sr"]
    sd_cfg = full_cfg["sd"]
    poc_cfg = full_cfg["poc"]
    conf_cfg = full_cfg["confluence"]
    out_cfg = full_cfg["output"]
    pip_size = symbol_cfg["pip_size"]

    logger.info("[%s] fetch barre D1/H4/M15 da %s", symbol, source)
    bars_d1 = fetch_ohlc(symbol_cfg, "D1", ds_cfg["bars_d1"], prefer=source)
    bars_h4 = fetch_ohlc(symbol_cfg, "H4", ds_cfg["bars_h4"], prefer=source)
    bars_m15 = None
    try:
        bars_m15 = fetch_ohlc(symbol_cfg, "M15", ds_cfg["bars_m15_for_poc"], prefer=source)
    except Exception as exc:
        logger.warning("[%s] M15 non disponibile (%s) — POC sarà saltato", symbol, exc)

    logger.info("[%s] D1=%d barre, H4=%d barre, M15=%s", symbol,
                len(bars_d1), len(bars_h4),
                len(bars_m15) if bars_m15 is not None else "n/a")

    # === Detector S/R ===
    sr_d1 = detect_sr_levels(
        bars_d1,
        threshold_atr_mult=sr_cfg["zigzag_threshold_atr_mult"]["d1"],
        cluster_width_pips=sr_cfg["cluster_width_pips"][symbol],
        pip_size=pip_size,
        min_touches=sr_cfg["min_touches"],
        max_levels=sr_cfg["max_levels_per_tf"]["d1"],
        tf_label="D1",
    )
    sr_h4 = detect_sr_levels(
        bars_h4,
        threshold_atr_mult=sr_cfg["zigzag_threshold_atr_mult"]["h4"],
        cluster_width_pips=sr_cfg["cluster_width_pips"][symbol],
        pip_size=pip_size,
        min_touches=sr_cfg["min_touches"],
        max_levels=sr_cfg["max_levels_per_tf"]["h4"],
        tf_label="H4",
    )
    logger.info("[%s] S/R: D1=%d, H4=%d", symbol, len(sr_d1), len(sr_h4))

    # === Detector S/D ===
    sd_d1 = detect_sd_zones(
        bars_d1,
        base_min_bars=sd_cfg["base_min_bars"],
        base_max_bars=sd_cfg["base_max_bars"],
        base_range_atr_mult=sd_cfg["base_range_atr_mult"],
        impulse_atr_mult=sd_cfg["impulse_atr_mult"],
        max_touches_for_valid=sd_cfg["max_touches_for_valid"],
        max_zones=sd_cfg["max_zones_per_tf"]["d1"],
        max_age_days=sd_cfg["max_age_days"]["d1"],
        tf_label="D1",
    )
    sd_h4 = detect_sd_zones(
        bars_h4,
        base_min_bars=sd_cfg["base_min_bars"],
        base_max_bars=sd_cfg["base_max_bars"],
        base_range_atr_mult=sd_cfg["base_range_atr_mult"],
        impulse_atr_mult=sd_cfg["impulse_atr_mult"],
        max_touches_for_valid=sd_cfg["max_touches_for_valid"],
        max_zones=sd_cfg["max_zones_per_tf"]["h4"],
        max_age_days=sd_cfg["max_age_days"]["h4"],
        tf_label="H4",
    )
    logger.info("[%s] S/D: D1=%d, H4=%d", symbol, len(sd_d1), len(sd_h4))

    # === Detector POC ===
    poc_weekly: list = []
    poc_monthly: list = []
    if bars_m15 is not None:
        bars_week = bars_m15.tail(poc_cfg["weekly_window_m15"])
        bars_month = bars_m15.tail(poc_cfg["monthly_window_m15"])
        poc_weekly = detect_poc_levels(
            bars_week,
            window_label="weekly",
            n_bins=poc_cfg["n_bins"],
            value_area_pct=poc_cfg["value_area_pct"],
            hvn_threshold_pct=poc_cfg["hvn_threshold_pct"],
            lvn_threshold_pct=poc_cfg["lvn_threshold_pct"],
        )
        poc_monthly = detect_poc_levels(
            bars_month,
            window_label="monthly",
            n_bins=poc_cfg["n_bins"],
            value_area_pct=poc_cfg["value_area_pct"],
            hvn_threshold_pct=poc_cfg["hvn_threshold_pct"],
            lvn_threshold_pct=poc_cfg["lvn_threshold_pct"],
        )
    logger.info("[%s] POC: weekly=%d, monthly=%d", symbol, len(poc_weekly), len(poc_monthly))

    # === Cross-detector confluence ===
    atr_d1 = _atr_simple(bars_d1)
    levels = merge_to_auto_levels(
        symbol=symbol,
        sr_d1=sr_d1,
        sr_h4=sr_h4,
        sd_d1=sd_d1,
        sd_h4=sd_h4,
        poc_weekly=poc_weekly,
        poc_monthly=poc_monthly,
        match_window_pips=conf_cfg["match_window_pips"][symbol],
        pip_size=pip_size,
        min_detectors=conf_cfg["min_detectors"],
        valid_for_days=out_cfg["valid_for_days"],
        atr_d1=atr_d1,
    )
    logger.info("[%s] livelli AUTO in confluenza: %d", symbol, len(levels))
    return levels


def cmd_generate(args: argparse.Namespace) -> int:
    cfg = _load_config()
    source = args.source or cfg["data_source"]["prefer"]

    levels_by_symbol: dict[str, list[AutoLevel]] = {}
    for symbol, sym_cfg in cfg["symbols"].items():
        try:
            levels = _generate_for_symbol(symbol, sym_cfg, cfg, source)
            levels_by_symbol[symbol] = levels
        except Exception as exc:
            logger.exception("[%s] generazione fallita: %s", symbol, exc)

    if not args.preview:
        out_path = (CONFIG_PATH.parent / cfg["output"]["yaml_path"]).resolve()
        write_levels_yaml(levels_by_symbol, out_path)
        logger.info("Scritto %s", out_path)
    else:
        # Dry-run: stampa solo.
        for symbol, levels in levels_by_symbol.items():
            print(f"\n=== {symbol} ===")
            for L in levels:
                tp = f"TP={L.tp_target_price}" if L.tp_target_price is not None else "TP=None"
                print(f"  {L.id}: {L.price} ({L.type}, bias {L.bias}) "
                      f"conf={L.confluence} {tp}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m strategies.confluence_auto")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Rigenera levels_auto.yaml")
    gen.add_argument("--source", choices=["mt5", "yfinance"], default=None,
                     help="Override del data source dal config.")
    gen.set_defaults(func=cmd_generate, preview=False)

    prev = sub.add_parser("preview", help="Dry-run: stampa i livelli, non scrive")
    prev.add_argument("--source", choices=["mt5", "yfinance"], default=None)
    prev.set_defaults(func=cmd_generate, preview=True)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
