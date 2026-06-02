"""Scarica storia lunga SP500 per il backtest del segnale momentum/RRG.

ATTENZIONE survivorship: usa i costituenti SP500 ATTUALI applicati al passato →
i titoli usciti dall'indice (falliti/declassati) sono assenti. Bias noto, da
correggere con costituenti point-in-time in una v2. Flaggato in tutti i report.

Output: _cache/hist_prices.parquet (adj close giornaliero).
Uso: python -m strategies.stock_selector.analysis.backtest_data
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

CACHE = Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)
SP500_CSV = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
START = "2013-01-01"
END = "2026-06-02"


def get_constituents() -> list[str]:
    try:
        r = requests.get(SP500_CSV, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        syms = df["Symbol"].astype(str).str.strip().tolist()
        return [s.replace(".", "-") for s in syms]
    except Exception as e:
        print("constituents fetch fallito, uso cache picks:", e)
        picks = pd.read_csv(CACHE / "picks_long.csv")
        return sorted({t.replace(".", "-") for t in picks["ticker"].unique()})


def main() -> None:
    syms = sorted(set(get_constituents()) | {"RSP", "^GSPC"})
    print(f"Scarico {len(syms)} simboli {START}->{END} (puo' richiedere qualche minuto)...")
    data = yf.download(syms, start=START, end=END, auto_adjust=True,
                       progress=False, threads=True)
    close = data["Close"]
    # tieni solo colonne con almeno 2 anni di storia
    enough = [c for c in close.columns if close[c].dropna().shape[0] > 500]
    close = close[enough]
    close.to_parquet(CACHE / "hist_prices.parquet")
    print(f"hist_prices.parquet: {close.shape[0]} giorni x {close.shape[1]} simboli")
    print(f"range: {close.index.min().date()} -> {close.index.max().date()}")


if __name__ == "__main__":
    main()
