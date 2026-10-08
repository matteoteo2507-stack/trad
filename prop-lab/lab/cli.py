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

from . import gate
from . import pipeline as P
from .metrics import expand_grid
from .strategies.base import REGISTRY
from .strategies import load_all


def main():
    ap = argparse.ArgumentParser(prog="lab")
    ap.add_argument("cmd", choices=["list", "new", "stage1", "stage2", "stage3", "confirm", "all", "report"])
    ap.add_argument("--family"); ap.add_argument("--symbol"); ap.add_argument("--data"); ap.add_argument("--run")
    ap.add_argument("--famiglia", help="id della famiglia nel contatore di trad (obbligatorio su dati reali)")
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
        try:
            run = P.new_run(a.family, a.symbol.upper(), a.data, ledger_id=a.famiglia)
        except gate.GateError as e:
            raise SystemExit(f"[cancello] {e}")
        print(f"[run] {run}")
        if a.cmd == "new":
            return
        P.stage1(run); P.stage2(run); P.stage3(run)
        tag = P.Run(run).meta.get("ledger_id")
        if tag in (gate.TAG_SINTETICO, gate.TAG_CONTROLLO, gate.TAG_FUORI):
            P.confirm(run)
        else:
            # 08/10 (trad): su una famiglia vera la conferma apre il fuori campione, che si apre una volta sola.
            # Non parte da sola: la si lancia a mano, dopo aver guardato le fasi 1-3.
            print(f"[all] fasi 1-3 fatte. La conferma APRE il fuori campione di '{tag}' (una volta sola).")
            print(f"      python -m lab.cli confirm --run {run}")
        return
    run = a.run if os.path.isabs(a.run) else os.path.join(os.getcwd(), a.run)
    try:
        {"stage1": P.stage1, "stage2": P.stage2, "stage3": P.stage3, "confirm": P.confirm,
         "report": lambda r: P.write_report(P.Run(r))}[a.cmd](run)
    except gate.GateError as e:
        raise SystemExit(f"[cancello] {e}")


if __name__ == "__main__":
    main()
