"""Test del gate di evidenza (level_analyzer/gate.py).

Run:  python tests/test_gate.py   (oppure pytest). Deterministico, nessuna rete.
Verifica la regola di decisione (INSUFFICIENTE/EDGE/NEGATIVO/AMBIGUO) e il report end-to-end.
"""
import csv
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from level_analyzer import gate, record  # noqa: E402


def _write(path, trades):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=record.HEADER, extrasaction="ignore")
        w.writeheader()
        for ts, R, out, reg, ses, asset in trades:
            w.writerow({"real_R": R, "outcome": out, "ts_utc": ts,
                        "regime": reg, "session": ses, "asset": asset})


def test_verdict_insufficient():
    s = {"n": 5, "n_days": 3, "ER": 0.5, "ci_lo": 0.1, "ci_hi": 0.9, "win": 60}
    assert gate.verdict(s)[0] == "INSUFFICIENTE"
    s2 = {"n": 40, "n_days": 4, "ER": 0.5, "ci_lo": 0.1, "ci_hi": 0.9, "win": 60}
    assert gate.verdict(s2)[0] == "INSUFFICIENTE"   # troppi pochi GIORNI (cluster)


def test_verdict_edge_negative_ambiguous():
    base = {"n": 50, "n_days": 15, "win": 50}
    assert gate.verdict({**base, "ER": 0.3, "ci_lo": 0.1, "ci_hi": 0.5})[0] == "EDGE FORWARD"
    assert gate.verdict({**base, "ER": -0.3, "ci_lo": -0.5, "ci_hi": -0.1})[0] == "NEGATIVO"
    assert gate.verdict({**base, "ER": 0.05, "ci_lo": -0.1, "ci_hi": 0.2})[0] == "AMBIGUO"


def test_analyze_and_report():
    rng = random.Random(0)
    trades = []
    for i in range(40):
        day = f"2026-06-{1 + (i % 14):02d}"
        R = 1.5 if rng.random() < 0.5 else -1.0
        trades.append((f"{day}T10:00:00+00:00", R, "win" if R > 0 else "loss",
                       "range" if i % 2 else "trend", "London", "XAUUSD"))
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "rec.csv")
        _write(p, trades)
        tr = gate._trades(gate.load_reconciled(p))
        assert len(tr) == 40
        s = gate.analyze(tr)
        assert s["n"] == 40 and s["n_days"] == 14
        rep = gate.format_report(p)
        assert "GATE DI EVIDENZA" in rep and "VERDETTO" in rep


def test_no_fill_excluded():
    trades = [("2026-06-01T10:00:00+00:00", "", "no_fill", "range", "London", "XAUUSD")]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "rec.csv")
        _write(p, trades)
        assert gate._trades(gate.load_reconciled(p)) == []   # no_fill non e' un trade


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("test_") and callable(v):
            v()
    print("OK — gate: tutti i test passati")
