"""Scarica l'universo ETF multi-asset + serie macro FRED per il backtest TAA (Layer 1 v2).

Universo rischioso (rotazione): SPY (US eq), EFA (dev ex-US), EEM (EM), TLT (long treasury),
GLD (oro). Safe/bond: AGG. Cash leg: T-bill 3m (FRED DTB3).
Overlay macro: HY credit spread (BAMLH0A0HYM2), yield curve 10y-3m (T10Y3M).

Output: _cache/taa_prices.parquet (adj close mensile), _cache/taa_macro.parquet (serie FRED mensili).
Uso: python -m strategies.stock_selector.analysis.tactical_data
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE = Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)

ETFS = ["SPY", "EFA", "EEM", "TLT", "GLD", "AGG"]
FRED_SERIES = {
    "hy_oas": "BAMLH0A0HYM2",   # ICE BofA US High Yield OAS (credit spread)
    "curve": "T10Y3M",          # 10y - 3m treasury (yield curve)
    "tbill3m": "DTB3",          # 3-month T-bill secondary market rate
}
START = "2002-06-01"
END = "2026-06-02"


def fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    df = pd.read_csv(url, parse_dates=[0])
    df.columns = ["date", series_id]
    df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
    return df.set_index("date")[series_id].dropna()


def main() -> None:
    px = yf.download(ETFS, start=START, end=END, auto_adjust=True, progress=False)["Close"]
    px_m = px.resample("ME").last()
    px_m.to_parquet(CACHE / "taa_prices.parquet")
    print("taa_prices.parquet:", px_m.shape)
    for c in px_m.columns:
        fv = px_m[c].first_valid_index()
        print(f"  {c}: da {fv.date() if fv is not None else 'n/a'}")

    macro = {}
    for name, sid in FRED_SERIES.items():
        s = fred(sid)
        macro[name] = s.resample("ME").last() if name != "tbill3m" else s.resample("ME").mean()
    mac = pd.DataFrame(macro)
    mac.to_parquet(CACHE / "taa_macro.parquet")
    print("taa_macro.parquet:", mac.shape, "|", mac.index.min().date(), "->", mac.index.max().date())
    print(mac.tail(2).round(2).to_string())


if __name__ == "__main__":
    main()
