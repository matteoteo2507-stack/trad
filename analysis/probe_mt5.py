"""Sonda MT5: verifica connessione, offset tempo-server e allineamento barre.

Non assume il fuso del broker: lo ricava confrontando l'ultima barra M5 con
l'ora reale, poi controlla che un ingresso noto (dal journal, in UTC reale)
cada davvero dentro la barra M5 corrispondente. Solo dopo questo check ha senso
mappare gli ingressi sui detector.

Uso (terminale MT5 aperto e loggato su DEMO3):
    python -m analysis.probe_mt5
"""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

from brokers.mt5 import MT5Broker


def _broker() -> MT5Broker:
    load_dotenv()
    login = os.getenv("MT5_DEMO3_LOGIN")
    password = os.getenv("MT5_DEMO3_PASSWORD")
    server = os.getenv("MT5_DEMO3_SERVER")
    if not (login and password and server):
        raise SystemExit("Credenziali MT5_DEMO3_* mancanti in .env")
    b = MT5Broker(login=int(login), password=password, server=server)
    b.connect()
    return b


def main() -> int:
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    b = _broker()

    # Ancora nota dal journal: 2026-06-05T12:26:00Z, entry ~4465.795 (NOW eseguito).
    # Mercato chiuso (sabato) => non si puo' usare "ultima barra vs ora". Ricavo
    # l'offset server cercando quale barra M5 contiene il prezzo noto a quell'ora.
    entry_utc = datetime(2026, 6, 5, 12, 26, tzinfo=timezone.utc)
    entry_px = 4465.795

    # Fetch ampio attorno al 05-06 (end in tempo-server ipotizzato; prendo molte barre).
    end_guess = datetime(2026, 6, 5, 20, 0)  # naive, interpretato come server time
    bars = b.get_bars_until("XAUUSD", "M5", end_guess, 400)
    hit = bars[(bars["low"] <= entry_px) & (bars["high"] >= entry_px)]
    print(f"Ancora: entry {entry_px} @ {entry_utc:%Y-%m-%d %H:%M} UTC reale")
    print(f"Barre M5 (label codice) che contengono {entry_px}:")
    for ts, row in hit.iterrows():
        delta = round((ts.to_pydatetime() - entry_utc).total_seconds() / 3600.0)
        print(f"  {ts:%Y-%m-%d %H:%M}  [{row['low']}, {row['high']}]  "
              f"=> offset label-UTC = {delta:+d}h")
    if hit.empty:
        print("  NESSUNA barra contiene il prezzo: ampliare la finestra/giorno.")
    print("\nRange barre scaricate:", bars.index[0], "->", bars.index[-1])

    b.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
