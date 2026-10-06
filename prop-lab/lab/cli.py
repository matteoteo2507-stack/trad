"""Uso:
  python -m lab.cli list                                   # famiglie e strategie disponibili
  python -m lab.cli all   --family mean_reversion --symbol XAUUSD --data data/XAUUSD_H1.csv
  python -m lab.cli new   --family mean_reversion --symbol XAUUSD --data data/XAUUSD_H1.csv
  python -m lab.cli stage1  --run results/<run_id>
  python -m lab.cli stage2  --run results/<run_id>
  python -m lab.cli stage3  --run results/<run_id>        # prop x profili di rischio (in-sample)
  python -m lab.cli confirm --run results/<run_id>        # conferma OOS + report
"""
from __future__ import annotations

import argparse
import os

from . import pipeline as P
from .metrics import expand_grid
from .strategies.base import REGISTRY
from .strategies import load_all


def main():
    ap = argparse.ArgumentParser(prog="lab")
    ap.add_argument("cmd", choices=["list", "new", "stage1", "stage2", "stage3", "confirm", "all", "report"])
    ap.add_argument("--family"); ap.add_argument("--symbol"); ap.add_argument("--data"); ap.add_argument("--run")
    a = ap.parse_args()

    if a.cmd == "list":
        load_all()
        for fam, strats in REGISTRY.items():
            tot = sum(len(expand_grid(c.grid)) for c in strats.values())
            print(f"\n{fam}  ({len(strats)} strategie, {tot} varianti)")
            for n, c in strats.items():
                print(f"  - {n:20s} {len(expand_grid(c.grid)):4d} var  {c.description}")
        return
    if a.cmd in ("new", "all"):
        run = P.new_run(a.family, a.symbol.upper(), a.data)
        print(f"[run] {run}")
        if a.cmd == "new":
            return
        P.stage1(run); P.stage2(run); P.stage3(run); P.confirm(run)
        return
    run = a.run if os.path.isabs(a.run) else os.path.join(os.getcwd(), a.run)
    {"stage1": P.stage1, "stage2": P.stage2, "stage3": P.stage3, "confirm": P.confirm,
     "report": lambda r: P.write_report(P.Run(r))}[a.cmd](run)


if __name__ == "__main__":
    main()
