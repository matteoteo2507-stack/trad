"""Report del gate di evidenza (Incremento 3).

Legge la spina riconciliata (trade_records.csv) e dice SE c'e' abbastanza evidenza e
PER QUALE conclusione — **condizionata** a regime/sessione/asset. NON modifica nulla:
e' un verdetto, non un'azione. Regole (vedi docs/TRADING_WORKFLOW_DESIGN.md):

  - si decide sul LOWER BOUND del CI, mai sul valore centrale (regola d'oro quant);
  - i trade sono CLUSTERATI per giorno -> CI via BLOCK-bootstrap sui giorni (non iid),
    e il conteggio dei giorni distinti e' il proxy di n_eff;
  - sotto le soglie minime: verdetto INSUFFICIENTE (continua a raccogliere), mai forzare.

Logica pura, offline-testabile. Nessuna modifica a strategie.
"""
from __future__ import annotations

import csv
import random
import statistics as st
from pathlib import Path

# --- regola di decisione (a priori) ---
MIN_TRADES = 30          # sotto = rumore
MIN_DAYS = 10            # cluster minimi (n_eff proxy): meno = non concludere
RANDOM_BASELINE = -0.13  # E[R] netto del fade a zona CASUALE (backtest, linea di riferimento)


def load_reconciled(path: str) -> list:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("real_R") or "") != ""]


def _trades(rows: list) -> list:
    """(day, R, regime, session, asset) per i record con posizione presa (no_fill escluso)."""
    out = []
    for r in rows:
        if r.get("outcome") == "no_fill":
            continue
        try:
            R = float(r["real_R"])
        except (ValueError, KeyError):
            continue
        day = (r.get("ts_utc") or "")[:10]
        out.append((day, R, r.get("regime", "?"), r.get("session", "?"), r.get("asset", "?")))
    return out


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (100 * (c - h) / den, 100 * (c + h) / den)


def block_boot_ci(trades: list, B: int = 2000, seed: int = 1):
    """CI bootstrap sull'E[R] ricampionando i GIORNI (block) — onesto sul clustering."""
    if not trades:
        return (0.0, 0.0)
    by_day: dict = {}
    for day, R, *_ in trades:
        by_day.setdefault(day, []).append(R)
    days = list(by_day)
    rng, means = random.Random(seed), []
    for _ in range(B):
        pool = []
        for _ in range(len(days)):
            pool.extend(by_day[days[rng.randrange(len(days))]])
        if pool:
            means.append(sum(pool) / len(pool))
    means.sort()
    return (means[int(0.025 * len(means))], means[int(0.975 * len(means))])


def analyze(trades: list) -> dict:
    n = len(trades)
    rs = [t[1] for t in trades]
    days = {t[0] for t in trades}
    wins = sum(1 for r in rs if r > 0)
    er = st.mean(rs) if rs else 0.0
    lo, hi = block_boot_ci(trades)
    wlo, whi = wilson(wins, n)
    return {"n": n, "n_days": len(days), "ER": er, "ci_lo": lo, "ci_hi": hi,
            "win": 100 * wins / n if n else 0.0, "win_lo": wlo, "win_hi": whi}


def verdict(s: dict, rr: float = 1.5) -> tuple:
    breakeven = 100.0 / (1.0 + rr)   # win-rate di pareggio (RR1.5 -> 40%)
    if s["n"] < MIN_TRADES or s["n_days"] < MIN_DAYS:
        return ("INSUFFICIENTE",
                f"n={s['n']} (<{MIN_TRADES}) o giorni={s['n_days']} (<{MIN_DAYS}) — continua a raccogliere")
    if s["ci_lo"] > 0:
        return ("EDGE FORWARD", f"CI E[R] esclude 0 (lower bound {s['ci_lo']:+.2f}R); "
                f"win {s['win']:.0f}% vs pareggio {breakeven:.0f}%")
    if s["ci_hi"] < 0:
        return ("NEGATIVO", f"CI E[R] sotto 0 (upper {s['ci_hi']:+.2f}R) — edge assente/decaduto forward")
    return ("AMBIGUO", f"CI E[R] include 0 [{s['ci_lo']:+.2f},{s['ci_hi']:+.2f}] — troppo sottile o pochi dati")


def _line(label: str, trades: list) -> str:
    if not trades:
        return f"  {label:22} n=   0"
    s = analyze(trades)
    return (f"  {label:22} n={s['n']:4} g={s['n_days']:3}  E[R]={s['ER']:+5.2f} "
            f"[CI {s['ci_lo']:+.2f},{s['ci_hi']:+.2f}]  win={s['win']:3.0f}%")


def format_report(path: str) -> str:
    rows = load_reconciled(path)
    trades = _trades(rows)
    n_total = len(rows)
    n_fill = len(trades)
    no_fill = sum(1 for r in rows if r.get("outcome") == "no_fill")
    out = ["=" * 64, "GATE DI EVIDENZA — Level Analyzer conf=2 (forward, netto costi)",
           f"record riconciliati={n_total}  presi={n_fill}  no_fill={no_fill}"
           f"  (fill-rate {100*n_fill/n_total:.0f}%)" if n_total else "nessun record riconciliato.",
           "=" * 64]
    if not trades:
        out.append("  Nessun trade preso ancora — lascia girare e riconciliare.")
        return "\n".join(out)
    s = analyze(trades)
    lbl, motivo = verdict(s)
    out.append(f"\n  TOTALE: {_line('tutti', trades).strip()}")
    out.append(f"  baseline random (backtest): E[R]~{RANDOM_BASELINE:+.2f}R")
    out.append(f"\n  >>> VERDETTO: {lbl} — {motivo}")
    out.append("      (decisione sul LOWER BOUND; CI block-bootstrap sui giorni, non iid)")
    for dim, idx in (("REGIME", 2), ("SESSIONE", 3), ("ASSET", 4)):
        groups = sorted({t[idx] for t in trades})
        if len(groups) > 1:
            out.append(f"\n  per {dim}:")
            for g in groups:
                out.append(_line(str(g), [t for t in trades if t[idx] == g]))
    return "\n".join(out)
