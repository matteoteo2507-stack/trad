"""Test dell'auto-riconciliatore (level_analyzer/reconcile.py).

Run:  python tests/test_reconcile.py   (oppure pytest). Deterministico, nessuna rete.
Verifica forward_resolve (win/loss/no_fill/timestop + netto costi) e il round-trip su CSV.
"""
import csv
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from level_analyzer import reconcile, record  # noqa: E402

# segnale LONG di riferimento: zona 100, SL 98 (sl_dist=2), TP 103 (rr=1.5), costo 0.1
ZONE, SL, TP, SLD, COST = 100.0, 98.0, 103.0, 2.0, 0.1


def _bar(lo, hi, cl=None):
    return {"low": lo, "high": hi, "close": cl if cl is not None else (lo + hi) / 2}


def test_win_long():
    bars = [_bar(99, 101), _bar(100, 103.5, 103.2)]   # tocca la zona, poi colpisce il TP
    res = reconcile.forward_resolve(bars, "long", ZONE, SL, TP, SLD, COST)
    assert res["outcome"] == "win"
    assert abs(res["R"] - (1.5 - COST / SLD)) < 1e-9   # rr netto costo = 1.45


def test_loss_long():
    bars = [_bar(99, 101), _bar(97.5, 100)]            # tocca la zona, poi colpisce lo SL
    res = reconcile.forward_resolve(bars, "long", ZONE, SL, TP, SLD, COST)
    assert res["outcome"] == "loss"
    assert abs(res["R"] - (-1.0 - COST / SLD)) < 1e-9  # -1.05


def test_no_fill():
    bars = [_bar(102, 104), _bar(103, 105)]            # la zona 100 non viene mai toccata
    res = reconcile.forward_resolve(bars, "long", ZONE, SL, TP, SLD, COST)
    assert res["outcome"] == "no_fill" and res["R"] == ""


def test_timestop_long():
    bars = [_bar(99, 101)] + [_bar(99.5, 100.5, 100.5)] * 3   # tocca, poi nessun SL/TP
    res = reconcile.forward_resolve(bars, "long", ZONE, SL, TP, SLD, COST, max_hold=4)
    assert res["outcome"] == "timestop"
    assert abs(res["R"] - ((100.5 - 100) / SLD - COST / SLD)) < 1e-9   # 0.20


def test_short_win():
    bars = [_bar(99, 101), _bar(96, 100)]              # short: tocca zona, poi TP a 97
    res = reconcile.forward_resolve(bars, "short", ZONE, 102.0, 97.0, SLD, COST)
    assert res["outcome"] == "win"


def test_reconcile_log_roundtrip():
    ts = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    sig = {"side": "long", "zone": ZONE, "sl": SL, "tp": TP, "rr": 1.5, "confluence": 2,
           "types": ["PDL", "Swing_S"], "dist": 1.0, "dist_atr": 0.1, "atr": 2.0}
    asset = {"name": "XAUUSD", "yf_ticker": "GC=F", "spread_assumed": COST}
    win = [{"open": 100, "high": 100.2, "low": 99.8, "close": 100} for _ in range(120)]
    rec = record.build_record(asset, sig, ZONE, win, data_backend="yfinance",
                              risk_pct=0.5, param_version="v1", ts=ts)
    bars = [{"t": ts + timedelta(hours=1), **_bar(99, 101)},
            {"t": ts + timedelta(hours=2), **_bar(100, 103.5, 103.2)}]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "rec.csv")
        record.append_record(p, rec)
        n = reconcile.reconcile_log(
            p, {"XAUUSD": "GC=F"}, {"XAUUSD": COST}, lambda t: bars,
            now=ts + timedelta(hours=48))
        assert n == 1
        with open(p, encoding="utf-8") as f:
            row = next(csv.DictReader(f))
        assert row["outcome"] == "win"
        assert row["real_R"] != "" and float(row["real_R"]) > 0
        assert row["reconciled_at"] != ""


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("OK — reconcile: tutti i test passati")
