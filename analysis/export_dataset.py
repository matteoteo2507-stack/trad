"""Esporta il dataset grezzo per la replica indipendente (5 agenti, offline).

Tira da MT5 una volta sola le barre continue del periodo + i 32 trade, e le
salva in CSV in analysis/data/. Gli agenti analizzano questi file senza toccare
MT5 (niente conflitti di terminale) e senza guardare i miei script.

Uso (terminale MT5 aperto su DEMO3):
    python -m analysis.export_dataset
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from analysis.mentor_entries import LOCAL_OFFSET_H, parse_trades, _broker

OUT = Path("analysis/data")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    OUT.mkdir(parents=True, exist_ok=True)
    b = _broker()
    end = datetime(2026, 6, 6, 2, 0)  # ora-macchina (CEST); ultima barra disponibile

    specs = {"D1": 400, "H1": 1300, "M15": 4200, "M5": 12000}
    for tf, count in specs.items():
        df = b.get_bars_until("XAUUSD", tf, end, count)
        path = OUT / f"bars_{tf}.csv"
        df.to_csv(path)
        print(f"{tf}: {len(df)} barre  {df.index[0]} -> {df.index[-1]}  -> {path}")

    # Trades con timestamp UTC esplicito.
    trades = parse_trades("messaggitg.txt")
    rows = ["n,ts_utc,side,entry,sl,tp1,tp2,tp3,outcome"]
    for t in trades:
        utc = (t.local_dt - timedelta(hours=LOCAL_OFFSET_H))
        tps = (t.tps + [None, None, None])[:3]
        tps_s = ",".join("" if x is None else f"{x}" for x in tps)
        rows.append(f"{t.n},{utc.isoformat()}Z,{t.side},{t.entry},{t.sl},{tps_s},{t.outcome}")
    (OUT / "trades.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"trades: {len(trades)} -> {OUT / 'trades.csv'}")

    b.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
