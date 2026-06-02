"""Consolida i pick storici dello Stock Selector + scarica i prezzi forward.

Output (in analysis/_cache/):
  picks_long.csv  -- un record per (date, ticker): score, target_match, si, rrg, settore
  prices.csv      -- adj close giornaliero per l'unione dei ticker + benchmark

Uso:
  python -m strategies.stock_selector.analysis.build_dataset
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[3]
PICKS_DIR = ROOT / "stoxs picks"
CACHE = Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)

# file -> (analysis_date, is_full_universe). Entry = primo trading day >= lunedì successivo.
FILES = {
    "Analisi_Completa sp500 30-12-25.ods": ("2025-12-30", True),
    "Analisi_Completa stocks10-05-26.ods": ("2026-05-10", True),
    "Analisi_Completa 17-05-26.xlsx":       ("2026-05-17", True),
    "Top_Picks sp500 30-12-25.ods":         ("2025-12-30", False),
    "Top_Picks 17-05-26.xlsx":              ("2026-05-17", False),
    "Top_Picks 24-5-2026.xlsx":             ("2026-05-24", False),
    "Top_Picks 31-05-26.xlsx":              ("2026-05-31", False),
}


def _engine(fname: str) -> str:
    return "odf" if fname.endswith(".ods") else "openpyxl"


def load_picks() -> pd.DataFrame:
    """Costruisce il long dataset. Per ogni data preferisce il file full-universe;
    se assente usa il Top_Picks (solo score>=5)."""
    frames = []
    # raggruppa per data, preferendo full universe
    by_date: dict[str, tuple[str, bool]] = {}
    for fname, (date, full) in FILES.items():
        if date not in by_date or (full and not by_date[date][1]):
            by_date[date] = (fname, full)

    for date, (fname, full) in sorted(by_date.items()):
        df = pd.read_excel(PICKS_DIR / fname, engine=_engine(fname))
        df = df.rename(columns={
            "Ticker": "ticker",
            "Settore": "sector",
            "TARGET MATCH": "target_match_raw",
            "SCORE (Max 6)": "score",
            "RRG Trend": "rrg",
        })
        df["date"] = date
        df["universe"] = "full" if full else "score_ge_5"
        df["si"] = df["target_match_raw"].astype(str).str.startswith("SI")
        df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
        frames.append(df[["date", "ticker", "sector", "score", "rrg",
                          "target_match_raw", "si", "universe"]])
    out = pd.concat(frames, ignore_index=True)
    return out


def yf_symbol(t: str) -> str:
    # yfinance usa '-' per le classi di azioni (BRK.B -> BRK-B)
    return t.replace(".", "-")


def main() -> None:
    picks = load_picks()
    picks.to_csv(CACHE / "picks_long.csv", index=False)
    print(f"picks_long.csv: {len(picks)} righe, "
          f"{picks['date'].nunique()} date, {picks['ticker'].nunique()} ticker unici")
    for d, g in picks.groupby("date"):
        print(f"  {d}: {len(g)} righe ({g['universe'].iloc[0]}), "
              f"SI={int(g['si'].sum())}, score>=4&SI={int(((g.score>=4)&g.si).sum())}")

    tickers = sorted({yf_symbol(t) for t in picks["ticker"].unique()})
    benches = ["^GSPC", "RSP"]  # RSP = SP500 equal-weight ETF
    all_syms = tickers + benches
    print(f"\nScarico {len(all_syms)} simboli da yfinance...")
    data = yf.download(all_syms, start="2025-12-26", end="2026-06-02",
                       auto_adjust=True, progress=False)
    close = data["Close"]
    close.to_csv(CACHE / "prices.csv")
    miss = [t for t in tickers if t not in close.columns or close[t].dropna().empty]
    print(f"prices.csv: {close.shape[0]} giorni x {close.shape[1]} simboli. "
          f"Mancanti: {len(miss)}")
    if miss:
        print("  ticker senza prezzi:", miss[:20])


if __name__ == "__main__":
    main()
