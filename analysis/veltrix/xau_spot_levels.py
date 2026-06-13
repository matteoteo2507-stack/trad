"""XAUUSD: livelli SPOT (feed MT5) vs FUTURES (bot/GC=F) — per le notifiche doppie.

Operiamo su XAUUSD spot ma il bot calcola su GC=F (futures): qui ricalcoliamo gli
STESSI livelli (logica portata da marketBias.js) sulle candele SPOT MT5 e li
affianchiamo a quelli futures del bot, così le notifiche possono mostrare entrambi.

Uso: python -m analysis.veltrix.xau_spot_levels
"""

from __future__ import annotations

import glob
import json
import re
import sys
from datetime import datetime, timezone

import pandas as pd

from analysis.veltrix.levels_engine import get_entry_points, analyze_bias, calc_confluence, aggregate_4h


def load_candles(csv_path: str) -> list[dict]:
    df = pd.read_csv(csv_path, parse_dates=["time"], index_col="time").sort_index()
    return [{"open": r.open, "high": r.high, "low": r.low, "close": r.close,
             "volume": getattr(r, "volume", 0), "time": idx} for idx, r in
            zip(df.index, df.itertuples())]


def bot_futures_pd(target_day) -> dict:
    """Estrae PDH/PDL/PDC futures riportati dal bot per il giorno dato (dall'export)."""
    src = sorted(glob.glob("alphanalist_chat_*.jsonl"))
    if not src:
        return {}
    out = {}
    for line in open(src[0], encoding="utf-8"):
        r = json.loads(line)
        if r.get("sender") != "AlphaAnalist":
            continue
        txt = (r.get("text") or "")
        if "XAUUSD" not in txt.upper():
            continue
        d = datetime.fromisoformat(r["date"].replace("Z", "+00:00")).date()
        if d != target_day:
            continue
        for ln in txt.split("\n"):
            up = ln.upper()
            mp = re.search(r"(\d[\d,]*(?:\.\d+)?)", ln)
            if not mp:
                continue
            try:
                price = float(mp.group(1).replace(",", ""))
            except ValueError:
                continue
            if not (1000 < price < 9000):
                continue
            if ("PDH" in up or "MAX IERI" in up) and "pdh" not in out:
                out["pdh"] = price
            elif ("PDL" in up or "MIN IERI" in up) and "pdl" not in out:
                out["pdl"] = price
            elif ("PDC" in up or "CLOSE IERI" in up) and "pdc" not in out:
                out["pdc"] = price
    return out


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    candles = load_candles("analysis/data/bars_D1.csv")
    asof = candles[-1]["time"]
    print(f"XAUUSD SPOT (feed MT5) — livelli as-of candela {asof:%Y-%m-%d}")
    print(f"Prezzo (close): {candles[-1]['close']:.2f}\n")

    entries = get_entry_points(candles)
    print("LIVELLI SPOT (stessa logica del bot, feed spot):")
    for e in entries:
        print(f"  {e['type'][:1]}  {e['label']:18} {e['price']:9.2f}   dist {e['distancePct']:.2f}%")

    # Bias spot (per completezza: dimostra che riproduciamo anche il bias del bot)
    bias_d = analyze_bias(candles, "Daily")
    print(f"\nBias DAILY spot: {bias_d['bias']} (score {bias_d['score']})  -> {bias_d['reasons']}")

    # Confronto PDH/PDL/PDC spot vs futures del bot, stesso giorno.
    spot_prev = candles[-2]
    spot = {"pdh": spot_prev["high"], "pdl": spot_prev["low"], "pdc": spot_prev["close"]}
    fut = bot_futures_pd(asof.date())
    print(f"\n=== PDH/PDL/PDC: SPOT (MT5) vs FUTURES (bot/GC=F), giorno {asof:%Y-%m-%d} ===")
    print(f"{'livello':6} {'SPOT':>10} {'FUTURES':>10} {'delta':>9}")
    for k in ("pdh", "pdl", "pdc"):
        s = spot.get(k); f = fut.get(k)
        if s is not None and f is not None:
            print(f"{k.upper():6} {s:10.2f} {f:10.2f} {f-s:+9.2f}")
        else:
            print(f"{k.upper():6} {('%.2f'%s) if s else '--':>10} {('%.2f'%f) if f else '--':>10}   (manca futures export)")
    print("\n-> il delta NON e' costante (basis futures-spot + rollover): per le notifiche"
          "\n   spot bisogna usare i valori SPOT qui sopra, non un offset sui futures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
