"""Run della matrice concetto x asset (reazione-vs-random) con holdout + breadth + DSR.

Esegue il protocollo PRE-REGISTRATO (docs/LEVEL_RESEARCH_PREREGISTRATION.md):
  - detection walk-forward look-ahead-safe per asset (una passata),
  - split temporale TRAIN 70% / TEST 30% dei giorni,
  - misura reale vs random distance-matched, CI block-bootstrap sui giorni,
  - verdetto per BREADTH (frazione di asset che battono il random) + effetto POOLATO,
  - correzione molteplicita' (falsi attesi = 0.05*T) + verifica out-of-sample dei sopravvissuti.

Uso: python analysis/level_research/__main__.py    (dalla root; i path usano __file__, cwd-agnostici)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np  # noqa: E402

from engine import (CONCEPTS, build_decisions, measure_core, split_days,  # noqa: E402
                    summarize_cell)

ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF",
          "EURJPY.r", "GBPJPY.r", "EURGBP.r", "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD",
          "US500", "US100"]
MIN_TOUCH = 30      # soglia di evidenza per-cella (come il gate del Level Analyzer)
MIN_DAYS = 10


def empty_acc():
    return {c: {"real": [], "rand": [], "net_real": [], "net_rand": [],
                "n_levels": 0, "n_touch": 0} for c in CONCEPTS}


def merge(pool, asset, acc):
    for c in CONCEPTS:
        A, P = acc[c], pool[c]
        for k in ("real", "rand", "net_real", "net_rand"):
            P[k] += [(f"{asset}:{d}", v) for d, v in A[k]]
        P["n_levels"] += A["n_levels"]
        P["n_touch"] += A["n_touch"]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    train_pool, test_pool = empty_acc(), empty_acc()
    per_asset = {}                         # asset -> {concept -> cell(train)}
    breadth = {c: 0 for c in CONCEPTS}     # asset che battono (train)
    tested = {c: 0 for c in CONCEPTS}      # asset con evidenza sufficiente (train)

    print("=" * 92)
    print("MATRICE REAZIONE-vs-RANDOM (distance-matched) — TRAIN 70%  [* = batte il random, CI>0]")
    print("=" * 92)
    for asset in ASSETS:
        h1, decisions = build_decisions(asset)
        if not decisions:
            print(f"{asset:9}  (dati mancanti/insufficienti)"); continue
        tr, te = split_days(decisions)
        acc_tr = measure_core(h1, [d for d in decisions if d["day"] in tr])
        acc_te = measure_core(h1, [d for d in decisions if d["day"] in te])
        if acc_tr is None:
            print(f"{asset:9}  (train vuoto)"); continue
        merge(train_pool, asset, acc_tr)
        if acc_te:
            merge(test_pool, asset, acc_te)
        cells = {}
        row = [f"{asset:9}"]
        for c in CONCEPTS:
            cell = summarize_cell(acc_tr[c])
            cells[c] = cell
            enough = cell["n_touch"] >= MIN_TOUCH and cell["n_days"] >= MIN_DAYS
            if enough:
                tested[c] += 1
                if cell["beats"]:
                    breadth[c] += 1
            if not enough:
                row.append(f"{c[:5]}:  n/a ")
            else:
                mark = "*" if cell["beats"] else " "
                row.append(f"{c[:5]}:{cell['diff']:+5.1f}{mark}")
        per_asset[asset] = cells
        print("  ".join(row))

    # ---- verdetto per concetto: breadth + pooled ----------------------------
    print("\n" + "=" * 92)
    print("VERDETTO PER CONCETTO  (breadth = asset che battono / asset con evidenza)")
    print("=" * 92)
    print(f"{'concetto':10} {'breadth':>10} {'pooled %REACT reale vs rand':>34} "
          f"{'CI95 diff':>18}  esito")
    survivors = []
    total_beats = sum(breadth.values())
    total_tested = sum(tested.values())
    for c in CONCEPTS:
        pc = summarize_cell(train_pool[c], boot_rate=4000, boot_med=1500)
        br = f"{breadth[c]}/{tested[c]}"
        frac = breadth[c] / tested[c] if tested[c] else 0.0
        pooled_beats = (not np.isnan(pc["ci_lo"])) and pc["ci_lo"] > 0
        surv = (frac >= 0.50) and pooled_beats
        if surv:
            survivors.append(c)
        verdict = "SOPRAVVIVE" if surv else ("(pool>0 ma breadth<50%)" if pooled_beats
                                             else "no")
        print(f"{c:10} {br:>10} {pc['rr_real']:>12.1f}% vs {pc['rr_rand']:>7.1f}%"
              f"{'':7}[{pc['ci_lo']:+.1f},{pc['ci_hi']:+.1f}]{'':4}  {verdict}")

    # ---- molteplicita' (DSR/PBO) --------------------------------------------
    T = len([1 for c in CONCEPTS for _ in ASSETS])
    print("\n--- Molteplicita' (DSR/PBO) ---")
    print(f"  trial totali T = {len(CONCEPTS)} concetti x {len(ASSETS)} asset = {T}")
    print(f"  'batte' falsi attesi a CI95 (per puro caso): ~{0.05*T:.0f}")
    print(f"  'batte' osservati (train, celle con evidenza): {total_beats} su {total_tested} testate")
    if total_beats <= 0.05 * T:
        print("  -> osservati <= attesi per caso: nessun segnale robusto alla molteplicita'.")

    # ---- out-of-sample (TEST) per i sopravvissuti ---------------------------
    print("\n" + "=" * 92)
    print("HOLDOUT — verifica out-of-sample (TEST 30%) dei sopravvissuti su TRAIN")
    print("=" * 92)
    if not survivors:
        print("  Nessun concetto sopravvive su TRAIN (breadth>=50% + pool CI>0).")
        print("  => Regola di decisione pre-registrata: nessun criterio batte il random con")
        print("     breadth. Mercato efficiente a questa risoluzione -> pivot (niente edge forzato).")
    else:
        for c in survivors:
            pc = summarize_cell(test_pool[c], boot_rate=4000, boot_med=1500)
            hold = (not np.isnan(pc["ci_lo"])) and pc["ci_lo"] > 0
            print(f"  {c:10} TEST: reale={pc['rr_real']:.1f}% vs rand={pc['rr_rand']:.1f}%  "
                  f"diff={pc['diff']:+.1f} [{pc['ci_lo']:+.1f},{pc['ci_hi']:+.1f}]  "
                  f"-> {'TIENE (out-of-sample)' if hold else 'NON tiene'}")

    print("\nNOTE: soglia evidenza per-cella n_touch>=%d, giorni>=%d. Random distance-matched." %
          (MIN_TOUCH, MIN_DAYS))
    print("Volume/tick-proxy escluso (v1 OHLC-puri). Definizioni/soglie = pre-registrazione.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
