"""Motore di backtest bar-by-bar, espresso in multipli di R (R = distanza dello stop).

Lavorare in R separa la QUALITÀ del segnale dalla GESTIONE DEL RISCHIO:
la stessa lista di trade in R viene poi ridimensionata dal simulatore prop con
modelli di rischio diversi (fisso, decrescente col drawdown, ecc.).

Convenzioni (conservative):
- segnale letto alla chiusura della barra i, ingresso all'apertura della barra i+1
- se nella stessa barra vengono toccati sia SL che TP -> conta lo SL
- gap oltre lo stop -> uscita al prezzo di apertura (perdita > 1R possibile)
- una posizione alla volta per variante

Due modalità:
- costs=None  -> backtest "ideale/qualitativo": niente spread, commissioni, swap, slippage
- costs=dict  -> backtest realistico: spread bid/ask (dai dati MT5 se presente), commissione,
                 slippage, swap per notte (tripla nel giorno configurato)
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class Signals:
    entry: np.ndarray                    # +1 long, -1 short, 0 nulla (letto a chiusura barra)
    sl_dist: np.ndarray                  # distanza stop in prezzo, calcolata alla barra del segnale
    tp_level: np.ndarray | None = None   # target assoluto (es. media) fissato al segnale
    tp_r: float | None = None            # oppure target in multipli di R
    exit_long: np.ndarray | None = None  # condizione di uscita a chiusura (esecuzione open successiva)
    exit_short: np.ndarray | None = None
    max_bars: int = 48                   # time stop
    meta: dict = field(default_factory=dict)


def _swap_nights(t0: pd.Timestamp, t1: pd.Timestamp, triple_dow: int | None) -> int:
    days = pd.date_range(t0.normalize() + pd.Timedelta(days=1), t1.normalize(), freq="D")
    n = 0
    for d in days:
        rollover_dow = (d - pd.Timedelta(days=1)).dayofweek  # notte tra d-1 e d
        if rollover_dow >= 5:   # weekend: il broker carica la tripla a metà settimana
            continue
        n += 3 if (triple_dow is not None and rollover_dow == triple_dow) else 1
    return n


def run_backtest(df: pd.DataFrame, sig: Signals, costs: dict | None = None) -> pd.DataFrame:
    o = df["open"].to_numpy(); h = df["high"].to_numpy()
    l = df["low"].to_numpy(); c = df["close"].to_numpy()
    idx = df.index
    n = len(df)
    entry = sig.entry; sld = sig.sl_dist
    exl = sig.exit_long if sig.exit_long is not None else np.zeros(n, bool)
    exs = sig.exit_short if sig.exit_short is not None else np.zeros(n, bool)

    point = costs["point"] if costs else 0.0
    if costs:
        sp_series = df["spread_points"].to_numpy() if "spread_points" in df else np.full(n, np.nan)
        sp_default = costs.get("spread_points", 0.0)
        spread = np.where(np.isfinite(sp_series), np.maximum(sp_series, sp_default * costs.get("min_spread_frac", 0.0)), sp_default) * point
        spread = spread * costs.get("spread_mult", 1.0)
        comm_px = costs.get("commission_per_lot_rt", 0.0) / costs["contract_size"]
        slip_px = 2 * costs.get("slippage_points", 0.0) * point
    else:
        spread = np.zeros(n); comm_px = 0.0; slip_px = 0.0

    trades = []
    i = 0
    while i < n - 1:
        d = int(entry[i])
        if d == 0 or not np.isfinite(sld[i]) or sld[i] <= 0:
            i += 1
            continue
        j = i + 1
        sp = spread[j]
        # prezzi chart = BID. Long compra ad ASK, chiude a BID. Short vende a BID, chiude ad ASK.
        ent = o[j] + (sp if d == 1 else 0.0)
        dist = sld[i]
        sl = ent - d * dist
        if sig.tp_level is not None:
            tp = sig.tp_level[i]
            if not np.isfinite(tp) or d * (tp - ent) <= 0:
                i += 1
                continue
        elif sig.tp_r is not None:
            tp = ent + d * sig.tp_r * dist
        else:
            tp = np.nan

        worst = ent
        exit_px = None; reason = None; k = j
        while k < n:
            # serie su cui controllare SL/TP: long esce a BID, short esce ad ASK
            adj = 0.0 if d == 1 else spread[k]
            bo, bh, bl, bc = o[k] + adj, h[k] + adj, l[k] + adj, c[k] + adj
            if d == 1:
                worst = min(worst, bl)
                hit_sl = bl <= sl
                hit_tp = np.isfinite(tp) and bh >= tp
                if hit_sl:
                    exit_px = min(sl, bo) if k > j else sl; reason = "sl"
                elif hit_tp:
                    exit_px = max(tp, bo) if k > j else tp; reason = "tp"
            else:
                worst = max(worst, bh)
                hit_sl = bh >= sl
                hit_tp = np.isfinite(tp) and bl <= tp
                if hit_sl:
                    exit_px = max(sl, bo) if k > j else sl; reason = "sl"
                elif hit_tp:
                    exit_px = min(tp, bo) if k > j else tp; reason = "tp"
            if exit_px is not None:
                break
            if (d == 1 and exl[k]) or (d == -1 and exs[k]):
                if k + 1 < n:
                    k += 1
                    exit_px = o[k] + (0.0 if d == 1 else spread[k]); reason = "exit"
                else:
                    exit_px = bc; reason = "end"
                break
            if k - j + 1 >= sig.max_bars:
                exit_px = bc; reason = "time"
                break
            k += 1
        if exit_px is None:
            k = n - 1; exit_px = c[k] + (0.0 if d == 1 else spread[k]); reason = "end"

        r_gross = d * (exit_px - ent) / dist
        mae = max(0.0, d * (ent - worst) / dist)
        cost_r = (comm_px + slip_px) / dist
        swap_r = 0.0; nights = 0
        if costs:
            nights = _swap_nights(idx[j], idx[k], costs.get("triple_swap_dow", 2))
            sw_pts = costs.get("swap_long_points", 0.0) if d == 1 else costs.get("swap_short_points", 0.0)
            swap_r = nights * sw_pts * point / dist   # segno: negativo = costo
        r = r_gross - cost_r + swap_r
        mae_r = min(mae, max(1.0, -r_gross)) + cost_r   # escursione avversa massima (per il DD intraday prop)
        trades.append((idx[j], idx[k], d, ent, exit_px, dist, r, mae_r, nights, reason, k - j + 1))
        i = max(k, j)   # un nuovo segnale può arrivare dalla barra di uscita in poi
    cols = ["entry_time", "exit_time", "dir", "entry", "exit", "sl_dist", "r", "mae_r", "swap_nights", "exit_reason", "bars"]
    return pd.DataFrame(trades, columns=cols)
