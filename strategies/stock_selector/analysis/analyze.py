"""Analisi attribuzione dei pick storici dello Stock Selector.

Legge _cache/picks_long.csv + _cache/prices.csv (prodotti da build_dataset.py) e
calcola forward returns a orizzonti fissi, attribuzione a strati (score/SI/RRG),
long-short SI-NO, Information Coefficient cross-sezionale e simulazione portafoglio
equal-weight buy&hold vs benchmark equal-weight (RSP).

Uso:
  python -m strategies.stock_selector.analysis.analyze
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

CACHE = Path(__file__).resolve().parent / "_cache"
HORIZONS = {"1w": 5, "2w": 10, "4w": 20}  # giorni di trading
RRG_ORDER = {"LAGGING": 0, "IMPROVING": 1, "LEADING": 2, "WEAKENING": 1.5}


def yf_symbol(t: str) -> str:
    return t.replace(".", "-")


def load():
    picks = pd.read_csv(CACHE / "picks_long.csv")
    prices = pd.read_csv(CACHE / "prices.csv", index_col=0, parse_dates=True)
    return picks, prices


def entry_index(prices: pd.DataFrame, date: str) -> int | None:
    """Primo indice di trading strettamente dopo la data di analisi (buy lunedì)."""
    d = pd.Timestamp(date)
    after = prices.index[prices.index > d]
    if len(after) == 0:
        return None
    return prices.index.get_loc(after[0])


def fwd_return(prices: pd.DataFrame, sym: str, e_idx: int, horizon_days: int | None):
    """Return da entry a entry+horizon (o all'ultimo disponibile se horizon None)."""
    if sym not in prices.columns:
        return np.nan
    s = prices[sym]
    if e_idx >= len(s) or pd.isna(s.iloc[e_idx]):
        return np.nan
    p0 = s.iloc[e_idx]
    if horizon_days is None:
        last = s.dropna()
        last = last[last.index >= s.index[e_idx]]
        if len(last) < 2:
            return np.nan
        p1 = last.iloc[-1]
    else:
        j = e_idx + horizon_days
        if j >= len(s) or pd.isna(s.iloc[j]):
            # fallback: ultimo disponibile entro la finestra
            window = s.iloc[e_idx:j + 1].dropna()
            if len(window) < 2:
                return np.nan
            p1 = window.iloc[-1]
        else:
            p1 = s.iloc[j]
    return float(p1 / p0 - 1.0)


def build_returns(picks: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    e_idx_by_date = {d: entry_index(prices, d) for d in picks["date"].unique()}
    for _, r in picks.iterrows():
        e = e_idx_by_date[r["date"]]
        if e is None:
            continue
        sym = yf_symbol(r["ticker"])
        rec = {**r.to_dict()}
        for name, h in HORIZONS.items():
            rec[f"ret_{name}"] = fwd_return(prices, sym, e, h)
        rec["ret_now"] = fwd_return(prices, sym, e, None)
        rows.append(rec)
    df = pd.DataFrame(rows)
    df["rrg_ord"] = df["rrg"].map(RRG_ORDER)
    df["buy"] = (df["score"] >= 4) & df["si"]  # buy-list config attuale
    return df


def bench_return(prices: pd.DataFrame, sym: str, date: str, horizon_days):
    e = entry_index(prices, date)
    return fwd_return(prices, sym, e, horizon_days)


def fmt_pct(x):
    return "n/a" if pd.isna(x) else f"{x*100:+.2f}%"


def main():
    picks, prices = load()
    df = build_returns(picks, prices)
    df.to_csv(CACHE / "returns_long.csv", index=False)

    full_dates = ["2025-12-30", "2026-05-10", "2026-05-17"]  # universo completo

    print("=" * 78)
    print("1. BENCHMARK forward returns (RSP=equal-weight, ^GSPC=cap-weight)")
    print("=" * 78)
    for d in sorted(df["date"].unique()):
        parts = []
        for name, h in {**HORIZONS, "now": None}.items():
            rsp = bench_return(prices, "RSP", d, h)
            gspc = bench_return(prices, "^GSPC", d, h)
            parts.append(f"{name}: RSP {fmt_pct(rsp)} / GSPC {fmt_pct(gspc)}")
        print(f"  {d} | " + " | ".join(parts))

    print("\n" + "=" * 78)
    print("2. ATTRIBUZIONE A STRATI — mean forward return per gruppo (vs RSP)")
    print("=" * 78)
    for d in sorted(df["date"].unique()):
        g = df[df["date"] == d]
        is_full = d in full_dates
        print(f"\n--- {d} ({'full universe' if is_full else 'score>=5 only'}) ---")
        rsp_now = bench_return(prices, "RSP", d, None)
        print(f"  Benchmark RSP (to-now): {fmt_pct(rsp_now)}")
        # buy-list vs resto
        for label, mask in [
            ("BUY-LIST (score>=4 & SI)", g["buy"]),
            ("SI (macro match)",          g["si"]),
            ("NO (macro mismatch)",       ~g["si"]),
        ]:
            sub = g[mask]
            print(f"  {label:30s} n={len(sub):3d}  "
                  f"now={fmt_pct(sub['ret_now'].mean())}  "
                  f"1w={fmt_pct(sub['ret_1w'].mean())}  "
                  f"2w={fmt_pct(sub['ret_2w'].mean())}  "
                  f"4w={fmt_pct(sub['ret_4w'].mean())}")
        # per score bucket
        print("  -- per SCORE bucket (to-now) --")
        for sc in sorted(g["score"].unique()):
            sub = g[g["score"] == sc]
            print(f"     score {sc:<4} n={len(sub):3d}  now={fmt_pct(sub['ret_now'].mean())}")
        # per RRG
        print("  -- per RRG (to-now) --")
        for rrg in ["LEADING", "IMPROVING", "WEAKENING", "LAGGING"]:
            sub = g[g["rrg"] == rrg]
            if len(sub):
                print(f"     {rrg:<10} n={len(sub):3d}  now={fmt_pct(sub['ret_now'].mean())}")

    print("\n" + "=" * 78)
    print("3. LONG-SHORT  SI - NO  (spread medio forward return, per data)")
    print("=" * 78)
    for d in sorted(df["date"].unique()):
        g = df[df["date"] == d]
        si = g[g["si"]]
        no = g[~g["si"]]
        parts = []
        for name in ["1w", "2w", "4w", "now"]:
            col = f"ret_{name}"
            spread = si[col].mean() - no[col].mean()
            parts.append(f"{name}: {fmt_pct(spread)}")
        print(f"  {d} | " + " | ".join(parts))

    print("\n" + "=" * 78)
    print("4. INFORMATION COEFFICIENT (Spearman rank corr, segnale vs fwd return)")
    print("=" * 78)
    for sig in ["score", "rrg_ord"]:
        print(f"\n  Segnale: {sig}")
        for d in sorted(df["date"].unique()):
            g = df[df["date"] == d].dropna(subset=[sig, "ret_now"])
            parts = []
            for name in ["1w", "2w", "4w", "now"]:
                gg = g.dropna(subset=[f"ret_{name}"])
                if len(gg) > 10:
                    ic, p = spearmanr(gg[sig], gg[f"ret_{name}"])
                    parts.append(f"{name}: IC={ic:+.3f}(p={p:.2f})")
                else:
                    parts.append(f"{name}: n/a")
            print(f"    {d} | " + " | ".join(parts))

    print("\n" + "=" * 78)
    print("5. SIMULAZIONE PORTAFOGLIO — equal-$ buy&hold buy-list, to-now")
    print("=" * 78)
    print("   (return medio equal-weight della buy-list vs RSP equal-weight)")
    for d in sorted(df["date"].unique()):
        g = df[df["date"] == d]
        bl = g[g["buy"]].dropna(subset=["ret_now"])
        port = bl["ret_now"].mean()
        rsp = bench_return(prices, "RSP", d, None)
        alpha = port - rsp if not pd.isna(rsp) else np.nan
        print(f"  {d} | buy-list n={len(bl):3d}  ret={fmt_pct(port)}  "
              f"RSP={fmt_pct(rsp)}  alpha={fmt_pct(alpha)}")


if __name__ == "__main__":
    main()
