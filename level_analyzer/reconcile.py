"""Auto-riconciliatore (self-labeling) — Incremento 2 del workflow.

Il sistema calcola da solo l'esito di OGNI segnale dal price path successivo
(entry al tocco della zona → SL/TP/time-stop), netto del costo assunto. Nessun
input umano: sostituisce il lavoro decisionale di "com'e' andato il trade".
Mirror forward della stessa logica del backtest (analysis/trading-bot-eval).

Vedi docs/TRADING_WORKFLOW_DESIGN.md.  Logica pura, testabile offline.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from . import record


def _res(outcome, entry, exit_, r_gross, cost, sl_dist):
    r_net = r_gross - (cost / sl_dist if sl_dist else 0.0)
    return {"outcome": outcome, "entry": round(entry, 4), "exit": round(exit_, 4),
            "R": round(r_net, 3)}


def forward_resolve(bars_after: list, side: str, zone: float, sl: float, tp: float,
                    sl_dist: float, cost: float, *, entry_window: int = 24,
                    max_hold: int = 24):
    """Esito del segnale sul price path successivo (bar H1 con t > ts del segnale).

    entry = primo tocco della zona entro `entry_window` barre; poi risoluzione SL/TP entro
    `max_hold` barre dall'entry (SL prima del TP nello stesso bar, conservativo); altrimenti
    time-stop sul close. R netto del costo (cost/sl_dist). 'no_fill' se la zona non viene toccata.
    """
    if sl_dist <= 0 or not bars_after:
        return None
    rr = abs(tp - zone) / sl_dist
    j = None
    for k in range(min(entry_window, len(bars_after))):
        b = bars_after[k]
        if b["low"] <= zone <= b["high"]:
            j = k
            break
    if j is None:
        return {"outcome": "no_fill", "entry": "", "exit": "", "R": ""}
    last = bars_after[j]["close"]
    for k in range(j, min(j + max_hold, len(bars_after))):
        b = bars_after[k]
        last = b["close"]
        if side == "long":
            if b["low"] <= sl:
                return _res("loss", zone, sl, -1.0, cost, sl_dist)
            if b["high"] >= tp:
                return _res("win", zone, tp, rr, cost, sl_dist)
        else:
            if b["high"] >= sl:
                return _res("loss", zone, sl, -1.0, cost, sl_dist)
            if b["low"] <= tp:
                return _res("win", zone, tp, rr, cost, sl_dist)
    r = (last - zone) / sl_dist if side == "long" else (zone - last) / sl_dist
    return _res("timestop", zone, last, r, cost, sl_dist)


def _parse_ts(s):
    try:
        t = datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t


def reconcile_log(path: str, ticker_of: dict, spread_of: dict, fetch_fn, *,
                  entry_window: int = 24, max_hold: int = 24, min_age_hours: int = 24,
                  now: datetime | None = None) -> int:
    """Riconcilia i record non ancora etichettati e abbastanza vecchi. Ritorna quanti."""
    p = Path(path)
    if not p.exists():
        return 0
    now = now or datetime.now(timezone.utc)
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cache: dict = {}
    done = 0
    for r in rows:
        if (r.get("real_R") or "") != "":
            continue
        ts = _parse_ts(r.get("ts_utc", ""))
        if ts is None or (now - ts).total_seconds() < min_age_hours * 3600:
            continue
        asset = r.get("asset")
        ticker = ticker_of.get(asset)
        if not ticker:
            continue
        if ticker not in cache:
            try:
                cache[ticker] = fetch_fn(ticker)
            except Exception:
                cache[ticker] = []
        bars = [b for b in cache[ticker] if b["t"] > ts]
        if not bars:
            continue
        try:
            zone, sl, tp = float(r["zone"]), float(r["sl"]), float(r["tp"])
        except (ValueError, KeyError):
            continue
        sl_dist = abs(zone - sl)
        cost = float(spread_of.get(asset, 0.0) or 0.0)
        res = forward_resolve(bars, r["side"], zone, sl, tp, sl_dist, cost,
                              entry_window=entry_window, max_hold=max_hold)
        if not res:
            continue
        r["real_entry"] = res["entry"]
        r["real_exit"] = res["exit"]
        r["real_cost"] = cost if res["outcome"] != "no_fill" else ""
        r["real_R"] = res["R"]
        r["outcome"] = res["outcome"]
        r["reconciled_at"] = now.isoformat(timespec="seconds")
        done += 1
    if done:
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=record.HEADER, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return done
