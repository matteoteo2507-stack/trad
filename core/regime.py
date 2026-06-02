"""Diagnosi automatica del regime di mercato.

Sostituisce la regola empirica HH/HL della Fase 1 di WEEKEND_CHECKLIST.md
con un albero decisionale deterministico basato su DMI/ADX/ATR (Wilder 1978).

Output: regime ∈ {Bull|Bear|Sideways} × {Quiet|Volatile} + decisione operativa
(proceed / halve_size / stay_out) coerente con TRADING_PRINCIPLES.md §1.

Riferimenti:
- Wilder J.W. (1978) — New Concepts in Technical Trading Systems. Trend Research.
  (Implementazioni canoniche di +DI, -DI, ADX, ATR).
- Faber M. (2007) — A Quantitative Approach to Tactical Asset Allocation.
  Journal of Wealth Management. (SMA(200) come regime filter, non usato in v1).

Uso:
    python -m core.regime --symbols EURUSD=X,XAUUSD=X
    python -m core.regime --csv data/eurusd_d1.csv --label EURUSD
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


Direction = Literal["Bull", "Bear", "Sideways"]
Volatility = Literal["Quiet", "Volatile"]
Action = Literal["proceed", "halve_size", "stay_out"]


@dataclass
class RegimeReport:
    symbol: str
    as_of: pd.Timestamp
    direction: Direction
    volatility: Volatility
    action: Action
    atr14: float
    atr14_sma50: float
    adx14: float
    plus_di14: float
    minus_di14: float

    @property
    def regime(self) -> str:
        return f"{self.direction} {self.volatility}"

    def format_journal_line(self) -> str:
        # ASCII-only per evitare problemi di encoding su console Windows (cp1252).
        return (
            f"- {self.symbol}: {self.regime}"
            f"  | ATR={self.atr14:.5f} (SMA50={self.atr14_sma50:.5f})"
            f"  ADX={self.adx14:.1f}  +DI={self.plus_di14:.1f} -DI={self.minus_di14:.1f}"
            f"  -> {self.action}"
        )


# ---------------------------------------------------------------------------
# Wilder indicators (implementazione da scratch, no dipendenze TA esterne)
# ---------------------------------------------------------------------------

def _wilder_smooth(series: pd.Series, period: int) -> pd.Series:
    """Wilder smoothing (RMA): ewm con alpha = 1/period, adjust=False.

    Equivalente al "Wilder's smoothing" originale: smoothed[t] =
    smoothed[t-1] - smoothed[t-1]/period + value[t].
    """
    return series.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def atr(bars: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range — Wilder 1978."""
    high, low, close = bars["high"], bars["low"], bars["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return _wilder_smooth(tr, period)


def dmi_adx(bars: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Directional Movement Index + ADX — Wilder 1978.

    Returns DataFrame con colonne: plus_di, minus_di, dx, adx.
    """
    high, low, close = bars["high"], bars["low"], bars["close"]
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm = pd.Series(plus_dm, index=bars.index)
    minus_dm = pd.Series(minus_dm, index=bars.index)

    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    atr_w = _wilder_smooth(tr, period)
    plus_di = 100.0 * _wilder_smooth(plus_dm, period) / atr_w.replace(0, np.nan)
    minus_di = 100.0 * _wilder_smooth(minus_dm, period) / atr_w.replace(0, np.nan)

    di_sum = plus_di + minus_di
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum.replace(0, np.nan)
    adx = _wilder_smooth(dx, period)

    return pd.DataFrame({
        "plus_di": plus_di,
        "minus_di": minus_di,
        "dx": dx,
        "adx": adx,
    })


# ---------------------------------------------------------------------------
# Decisione regime
# ---------------------------------------------------------------------------

# Soglie centralizzate — modificabili in config se diventeranno tunable.
ADX_NO_TREND_MAX = 25.0   # < 25 → Sideways (direzione ignorata)
ADX_STRONG_MIN = 40.0     # ≥ 40 → trend forte (uguale tradabile, ma logghiamo il caso)


def classify_direction(adx14: float, plus_di14: float, minus_di14: float) -> Direction:
    """ADX gating + DI comparison. Vedi TRADING_PRINCIPLES.md §1.

    - ADX < 25 → Sideways (a prescindere dai DI).
    - ADX ≥ 25 → +DI vs -DI decide Bull/Bear.
    """
    if not np.isfinite(adx14) or adx14 < ADX_NO_TREND_MAX:
        return "Sideways"
    if plus_di14 > minus_di14:
        return "Bull"
    if minus_di14 > plus_di14:
        return "Bear"
    # Pareggio esatto (raro) → Sideways per cautela.
    return "Sideways"


def classify_volatility(atr14: float, atr_sma50: float) -> Volatility:
    if not np.isfinite(atr14) or not np.isfinite(atr_sma50) or atr_sma50 <= 0:
        return "Quiet"
    return "Volatile" if atr14 > atr_sma50 else "Quiet"


def operational_action(direction: Direction, volatility: Volatility) -> Action:
    """Mappa regime → azione operativa (TRADING_PRINCIPLES.md §1)."""
    if direction == "Sideways" and volatility == "Volatile":
        return "stay_out"
    return "proceed"


def diagnose_regime(
    bars: pd.DataFrame,
    symbol: str,
    *,
    atr_period: int = 14,
    adx_period: int = 14,
    atr_sma_window: int = 50,
) -> RegimeReport:
    """Calcola il regime corrente date barre D1 OHLC.

    Richiede `bars` con colonne `high`, `low`, `close` indicizzate per data.
    Servono almeno ~70 barre (adx_period × 2 + atr_sma_window) per valori stabili.
    """
    required = {"high", "low", "close"}
    if not required.issubset(bars.columns):
        raise ValueError(f"bars deve avere colonne {required}, trovate: {set(bars.columns)}")
    if len(bars) < adx_period * 2 + atr_sma_window:
        raise ValueError(
            f"barre insufficienti: {len(bars)} < min {adx_period * 2 + atr_sma_window}"
        )

    atr_series = atr(bars, atr_period)
    atr_sma = atr_series.rolling(atr_sma_window, min_periods=atr_sma_window).mean()
    dmi = dmi_adx(bars, adx_period)

    last_idx = bars.index[-1]
    atr14 = float(atr_series.iloc[-1])
    atr_sma50 = float(atr_sma.iloc[-1])
    adx14 = float(dmi["adx"].iloc[-1])
    plus_di14 = float(dmi["plus_di"].iloc[-1])
    minus_di14 = float(dmi["minus_di"].iloc[-1])

    direction = classify_direction(adx14, plus_di14, minus_di14)
    volatility = classify_volatility(atr14, atr_sma50)
    action = operational_action(direction, volatility)

    return RegimeReport(
        symbol=symbol,
        as_of=last_idx,
        direction=direction,
        volatility=volatility,
        action=action,
        atr14=atr14,
        atr14_sma50=atr_sma50,
        adx14=adx14,
        plus_di14=plus_di14,
        minus_di14=minus_di14,
    )


# ---------------------------------------------------------------------------
# Timeline storica + attivazione per strategia
# ---------------------------------------------------------------------------

# Mappa regime → stato di attivazione per ciascuna strategia.
# "active" = opera a size pieno, "half" = size dimezzata, "disabled" = stay out.
# Coerente con TRADING_PRINCIPLES.md §1 e con la tabella in ROADMAP Stage 2.6.5.
STRATEGY_REGIME_ACTIVATION: dict[str, dict[str, str]] = {
    "london_breakout": {
        "Bull Quiet": "half",      "Bull Volatile": "active",
        "Bear Quiet": "half",      "Bear Volatile": "active",
        "Sideways Quiet": "active", "Sideways Volatile": "disabled",
    },
    "tsmom": {
        "Bull Quiet": "active",    "Bull Volatile": "active",
        "Bear Quiet": "active",    "Bear Volatile": "active",
        "Sideways Quiet": "disabled", "Sideways Volatile": "disabled",
    },
    "confluence": {
        "Bull Quiet": "active",    "Bull Volatile": "half",
        "Bear Quiet": "active",    "Bear Volatile": "half",
        "Sideways Quiet": "active", "Sideways Volatile": "disabled",
    },
}


def regime_timeline(
    bars: pd.DataFrame,
    *,
    atr_period: int = 14,
    adx_period: int = 14,
    atr_sma_window: int = 50,
) -> pd.DataFrame:
    """Calcola il regime per OGNI barra (non solo l'ultima).

    Restituisce un DataFrame indicizzato per data con colonne:
    close, atr, atr_sma, adx, plus_di, minus_di, direction, volatility,
    regime, action.
    """
    atr_series = atr(bars, atr_period)
    atr_sma = atr_series.rolling(atr_sma_window, min_periods=atr_sma_window).mean()
    dmi = dmi_adx(bars, adx_period)

    df = pd.DataFrame(index=bars.index)
    df["close"] = bars["close"]
    df["atr"] = atr_series
    df["atr_sma"] = atr_sma
    df["adx"] = dmi["adx"]
    df["plus_di"] = dmi["plus_di"]
    df["minus_di"] = dmi["minus_di"]
    df = df.dropna(subset=["atr_sma", "adx", "plus_di", "minus_di"])

    directions, vols, actions = [], [], []
    for _, row in df.iterrows():
        d = classify_direction(row["adx"], row["plus_di"], row["minus_di"])
        v = classify_volatility(row["atr"], row["atr_sma"])
        directions.append(d)
        vols.append(v)
        actions.append(operational_action(d, v))
    df["direction"] = directions
    df["volatility"] = vols
    df["regime"] = [f"{d} {v}" for d, v in zip(directions, vols)]
    df["action"] = actions
    return df


def strategy_activation(timeline_df: pd.DataFrame, strategy: str) -> pd.Series:
    """Mappa la colonna `regime` del timeline → stato attivazione per la strategia.

    Restituisce una Series allineata al timeline con valori in
    {active, half, disabled}.
    """
    if strategy not in STRATEGY_REGIME_ACTIVATION:
        raise ValueError(
            f"strategia '{strategy}' sconosciuta. Note: {list(STRATEGY_REGIME_ACTIVATION)}"
        )
    mapping = STRATEGY_REGIME_ACTIVATION[strategy]
    return timeline_df["regime"].map(mapping).fillna("active")


def contiguous_ranges(flags: pd.Series) -> list[tuple]:
    """Dato un boolean Series indicizzato per data, restituisce la lista di
    intervalli (start_date, end_date) contigui dove flag == True.
    """
    ranges = []
    start = None
    prev_idx = None
    for idx, val in flags.items():
        if val and start is None:
            start = idx
        elif not val and start is not None:
            ranges.append((start, prev_idx))
            start = None
        prev_idx = idx
    if start is not None:
        ranges.append((start, prev_idx))
    return ranges


def summarize_timeline(timeline_df: pd.DataFrame, strategy: str) -> dict:
    """Riepilogo per il filtro 'avrei attivato la strategia?'.

    Restituisce dict con:
      - pct_per_regime: % di tempo in ciascun regime.
      - pct_per_activation: % di tempo active/half/disabled per la strategia.
      - collectable_ranges: intervalli (start, end) in cui la strategia NON è
        disabled (= dati che avrei raccolto).
      - excluded_ranges: intervalli disabled (= da tagliare dal backtest).
    """
    n = len(timeline_df)
    activation = strategy_activation(timeline_df, strategy)

    pct_per_regime = (timeline_df["regime"].value_counts() / n * 100).round(1).to_dict()
    pct_per_activation = (activation.value_counts() / n * 100).round(1).to_dict()

    collectable = activation != "disabled"
    excluded = activation == "disabled"
    return {
        "n_bars": n,
        "pct_per_regime": pct_per_regime,
        "pct_per_activation": pct_per_activation,
        "collectable_ranges": contiguous_ranges(collectable),
        "excluded_ranges": contiguous_ranges(excluded),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _fetch_yfinance_range(symbol: str, start: str, end: str | None) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance non installato: pip install yfinance")
    end_ts = (
        pd.Timestamp(end) if end
        else pd.Timestamp.now("UTC").tz_localize(None).normalize()
    )
    df = yf.download(symbol, start=pd.Timestamp(start), end=end_ts,
                     interval="1d", auto_adjust=False, progress=False)
    if df.empty:
        sys.exit(f"yfinance non ha restituito dati per {symbol} ({start}→{end})")
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    return df[["high", "low", "close"]].dropna()


def _plot_timeline(timeline_df: pd.DataFrame, strategy: str, out_path: str) -> bool:
    """Plot prezzo + shading dei periodi 'disabled'. Restituisce True se salvato."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    activation = strategy_activation(timeline_df, strategy)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(timeline_df.index, timeline_df["close"], color="black", linewidth=0.8)

    disabled = activation == "disabled"
    for start, end in contiguous_ranges(disabled):
        ax.axvspan(start, end, color="red", alpha=0.18)
    half = activation == "half"
    for start, end in contiguous_ranges(half):
        ax.axvspan(start, end, color="orange", alpha=0.10)

    ax.set_title(f"{strategy} — periodi attivi (bianco/arancio) vs disabled (rosso)")
    ax.set_ylabel("close")
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return True

def _fetch_yfinance(symbol: str, years: int) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance non installato: pip install yfinance")
    end = pd.Timestamp.now("UTC").tz_localize(None).normalize()
    start = end - pd.Timedelta(days=int(365.25 * years))
    df = yf.download(symbol, start=start, end=end, interval="1d",
                     auto_adjust=False, progress=False)
    if df.empty:
        sys.exit(f"yfinance non ha restituito dati per {symbol}")
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    return df[["high", "low", "close"]].dropna()


def _load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    df.columns = [c.lower() for c in df.columns]
    return df[["high", "low", "close"]].dropna()


def _print_report(rep: RegimeReport) -> None:
    print(rep.format_journal_line())


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m core.regime")
    parser.add_argument(
        "--symbols",
        default="EURUSD=X,GC=F",
        help="Ticker yfinance comma-separated (default: EURUSD=X,GC=F). "
             "XAU usa GC=F (gold futures CME) perché XAUUSD=X non è esposto.",
    )
    parser.add_argument("--csv", default=None, help="Path CSV alternativo (single symbol)")
    parser.add_argument("--label", default="CUSTOM", help="Label simbolo per --csv")
    parser.add_argument("--years", type=int, default=2,
                        help="Anni di history yfinance (default 2)")
    parser.add_argument("--journal", action="store_true",
                        help="Output in blocco markdown da incollare nel journal")
    # --- Timeline mode ---
    parser.add_argument("--timeline", action="store_true",
                        help="Modalità timeline storica: calcola il regime per ogni "
                             "barra e i periodi in cui una strategia sarebbe attiva.")
    parser.add_argument("--start", default="2020-01-01",
                        help="Data inizio per --timeline (YYYY-MM-DD, default 2020-01-01)")
    parser.add_argument("--end", default=None,
                        help="Data fine per --timeline (default: oggi)")
    parser.add_argument("--strategy", default="london_breakout",
                        choices=list(STRATEGY_REGIME_ACTIVATION),
                        help="Strategia per cui calcolare i periodi attivi (--timeline)")
    parser.add_argument("--out-csv", default=None,
                        help="Salva il timeline come CSV (--timeline)")
    parser.add_argument("--plot", default=None,
                        help="Salva un PNG prezzo+regime (--timeline). Richiede matplotlib.")
    args = parser.parse_args()

    if args.timeline:
        return _run_timeline(args)

    reports: list[RegimeReport] = []
    if args.csv:
        bars = _load_csv(args.csv)
        reports.append(diagnose_regime(bars, args.label))
    else:
        for sym in [s.strip() for s in args.symbols.split(",") if s.strip()]:
            label = sym.replace("=X", "").replace("=F", "")
            if label == "GC":
                label = "XAUUSD"  # alias leggibile per gold futures
            bars = _fetch_yfinance(sym, args.years)
            reports.append(diagnose_regime(bars, label))

    if args.journal:
        as_of = reports[0].as_of.strftime("%Y-%m-%d")
        print(f"## Regime corrente {as_of}")
        for r in reports:
            print(r.format_journal_line())
    else:
        for r in reports:
            _print_report(r)

    # Exit code 0 = ok; 2 se almeno un simbolo è "stay_out".
    return 2 if any(r.action == "stay_out" for r in reports) else 0


def _run_timeline(args) -> int:
    """Modalità --timeline: regime storico + periodi attivi per la strategia."""
    if args.csv:
        bars = _load_csv(args.csv)
        label = args.label
    else:
        sym = args.symbols.split(",")[0].strip()
        label = sym.replace("=X", "").replace("=F", "")
        if label == "GC":
            label = "XAUUSD"
        bars = _fetch_yfinance_range(sym, args.start, args.end)

    tl = regime_timeline(bars)
    if tl.empty:
        sys.exit("Timeline vuota: history insufficiente per gli indicatori.")

    summary = summarize_timeline(tl, args.strategy)

    print(f"=== Regime timeline {label} — strategia '{args.strategy}' ===")
    print(f"Periodo: {tl.index[0].date()} -> {tl.index[-1].date()}  ({summary['n_bars']} barre D1)\n")

    print("% tempo per regime:")
    for regime, pct in sorted(summary["pct_per_regime"].items(), key=lambda x: -x[1]):
        print(f"  {regime:<20} {pct:>5}%")

    print("\n% tempo per stato di attivazione:")
    for state in ("active", "half", "disabled"):
        pct = summary["pct_per_activation"].get(state, 0.0)
        print(f"  {state:<10} {pct:>5}%")

    collectable = summary["collectable_ranges"]
    excluded = summary["excluded_ranges"]
    print(f"\nPeriodi RACCOLTI (active+half, {len(collectable)} intervalli) — "
          f"su questi va valutato il backtest:")
    for start, end in collectable:
        print(f"  {start.date()} -> {end.date()}")
    print(f"\nPeriodi ESCLUSI (Sideways Volatile = disabled, {len(excluded)} intervalli) — "
          f"da tagliare dai trade del backtest:")
    for start, end in excluded:
        print(f"  {start.date()} -> {end.date()}")

    if args.out_csv:
        tl_out = tl.copy()
        tl_out["activation"] = strategy_activation(tl, args.strategy)
        tl_out.to_csv(args.out_csv)
        print(f"\nTimeline salvato in {args.out_csv}")

    if args.plot:
        ok = _plot_timeline(tl, args.strategy, args.plot)
        if ok:
            print(f"Plot salvato in {args.plot}")
        else:
            print("matplotlib non installato: plot saltato (pip install matplotlib)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
