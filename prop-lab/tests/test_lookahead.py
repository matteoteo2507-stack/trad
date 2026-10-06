"""Test anti look-ahead per TUTTE le strategie registrate:
i segnali fino alla barra t non devono cambiare se tagliamo via il futuro dopo t.
python tests/test_lookahead.py data/DEMO_XAUUSD_H1.csv"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from lab.data import load_mt5_csv
from lab.metrics import expand_grid
from lab.strategies import load_all
from lab.strategies.base import REGISTRY


def check(path, n_bars=3000, cuts=(1500, 2200)):
    df = load_mt5_csv(path).iloc[:n_bars]
    load_all(); bad = []
    for fam, strats in REGISTRY.items():
        for name, cls in strats.items():
            for p in expand_grid(cls.grid)[:: max(1, len(expand_grid(cls.grid)) // 4)]:
                full = cls().signals(df, **p)
                for c in cuts:
                    part = cls().signals(df.iloc[:c], **p)
                    a, b = full.entry[:c], part.entry
                    sa, sb = np.nan_to_num(full.sl_dist[:c]), np.nan_to_num(part.sl_dist)
                    if not (np.array_equal(a, b) and np.allclose(sa, sb, equal_nan=True)):
                        bad.append((fam, name, p, c))
    return bad


if __name__ == "__main__":
    bad = check(sys.argv[1] if len(sys.argv) > 1 else "data/DEMO_XAUUSD_H1.csv")
    print("OK: nessun look-ahead rilevato" if not bad else f"LOOK-AHEAD in: {bad}")
    sys.exit(1 if bad else 0)
