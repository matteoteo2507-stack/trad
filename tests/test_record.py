"""Smoke test della spina dati contestualizzata (level_analyzer/record.py).

Run:  python tests/test_record.py   (oppure pytest)
Verifica: schema completo, contesto popolato alla cattura, campi umano/esito vuoti,
round-trip append→update by record_id. Nessuna rete, deterministico.
"""
import csv
import os
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from level_analyzer import record  # noqa: E402

SIG = {"side": "long", "zone": 2010.0, "sl": 2008.0, "tp": 2013.0, "rr": 1.5,
       "confluence": 2, "types": ["PDL", "Swing_S"], "dist": 1.0, "dist_atr": 0.1, "atr": 2.0}
ASSET = {"name": "XAUUSD", "yf_ticker": "GC=F", "spread_assumed": 0.10}


def _synthetic_window(n=120):
    h1, px = [], 2000.0
    for i in range(n):
        px *= 1.001 if i % 7 else 0.997
        h1.append({"open": px, "high": px * 1.002, "low": px * 0.998, "close": px})
    return h1


def test_session():
    f = lambda h: record.session_of(datetime(2026, 6, 18, h, tzinfo=timezone.utc))
    assert f(13) == "London/NY overlap"
    assert f(8) == "London"
    assert f(18) == "NY"
    assert f(3) == "Tokyo"
    assert f(22) == "Off"


def test_context_helpers():
    h1 = _synthetic_window()
    adx = record.adx_last(h1)
    assert adx is None or adx >= 0
    vol = record.realized_vol(h1)
    assert vol is not None and vol > 0
    assert record.instrument_basis("GC=F", "yfinance") == "futures"
    assert record.instrument_basis("BTC-USD", "yfinance") == "spot~"
    assert record.instrument_basis("XAUUSD", "mt5") == "spot"
    assert record.regime_from_adx(None) == "n/d"
    assert record.regime_from_adx(10) == "range"
    assert record.regime_from_adx(30) == "trend"


def test_build_record_schema_and_context():
    rec = record.build_record(ASSET, SIG, 2010.0, _synthetic_window(),
                              data_backend="yfinance", risk_pct=0.5,
                              param_version="ksl0.5-rr1.5-tol0.25-prox0.25")
    assert set(rec.keys()) == set(record.HEADER), "schema diverso da HEADER"
    # contesto popolato ALLA CATTURA
    for k in ("session", "regime", "atr_h1", "vol_h1", "spread_assumed",
              "instrument_basis", "param_version", "data_source", "record_id"):
        assert rec[k] != "", f"campo contesto vuoto: {k}"
    assert rec["instrument_basis"] == "futures"   # GC=F
    # campi esito VUOTI alla cattura (li riempie l'auto-riconciliazione dal price path)
    for k in ("real_entry", "real_exit", "real_cost", "real_R", "outcome", "reconciled_at"):
        assert rec[k] == "", f"campo {k} non vuoto alla cattura"


def test_append_update_roundtrip():
    rec = record.build_record(ASSET, SIG, 2010.0, _synthetic_window(),
                              data_backend="yfinance", risk_pct=0.5, param_version="v1")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "rec.csv")
        record.append_record(p, rec)
        record.append_record(p, rec)   # secondo append: niente doppio header
        ok = record.update_record(p, rec["record_id"],
                                   real_R="1.5", outcome="win", reconciled_at="2026-06-19T00:00:00")
        assert ok, "update_record non ha trovato il record_id"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2, f"attese 2 righe dati, trovate {len(rows)}"
        assert rows[0]["real_R"] == "1.5" and rows[0]["outcome"] == "win"


if __name__ == "__main__":
    test_session()
    test_context_helpers()
    test_build_record_schema_and_context()
    test_append_update_roundtrip()
    print("OK — spina dati: tutti i test passati")
