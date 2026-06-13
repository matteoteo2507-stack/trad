"""Calibrazione RIALLINEATA per sessione (lo scopo reale del bot).

Il bot predice la direzionalita' DELLA SESSIONE, non del giorno. Quindi una call
di sessione va valutata sul movimento *dalla call alla fine di quella sessione*,
non su orizzonti fissi 4h/24h.

Ancore di fine-sessione (prezzi del bot stesso alle transizioni, stesso giorno/asset):
  - LONDON call  -> fine ~ prezzo della call NY dello stesso giorno (apertura NY);
                    fallback: close_report EOD.
  - NY call      -> fine ~ prezzo del close_report EOD dello stesso giorno;
                    fallback: prima quota del giorno dopo.
  - ASIA call    -> fine ~ prezzo della call LONDON dello stesso giorno.

Verdetto sul prodotto vero del bot = le call di sessione (London/NY/Asia).
Alert Daily / Close Report restano come contesto, non come metro direzionale.

Uso: python -m analysis.veltrix.calibrate_session
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime

SIG = "analysis/veltrix/signals.jsonl"


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rows = [json.loads(l) for l in open(SIG, encoding="utf-8")]
    rows = [r for r in rows if r.get("asset")]

    # Timeline prezzi per asset (ordinata). NB: alert_daily/close_report sono a 00:00
    # UTC (rollover), quindi l'ancora di fine sessione DEVE essere temporale e in
    # AVANTI rispetto alla call, non per tipo di messaggio (bug corretto 2026-06-08).
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td
    tl: dict[str, list] = defaultdict(list)
    for r in rows:
        if r.get("price"):
            tl[r["asset"]].append((_ts(r["ts_utc"]), float(r["price"])))
    for a in tl:
        tl[a].sort()

    def price_at_or_after(asset, when, max_ahead_h=40):
        for t, p in tl.get(asset, []):
            if t >= when:
                return p if (t - when) <= _td(hours=max_ahead_h) else None
        return None

    def session_end(day, kind):
        # orari UTC di fine sessione (estate IT=UTC+2)
        base = _dt(day.year, day.month, day.day, tzinfo=_tz.utc)
        if kind == "london_session":
            return base + _td(hours=13)         # apertura NY ~13:00 UTC
        if kind == "ny_session":
            return base + _td(days=1)           # rollover ~00:00 UTC giorno dopo (~EOD)
        if kind == "asia_session":
            return base + _td(hours=6)           # apertura London ~06:00 UTC
        return None

    recs = []
    for r in rows:
        if r["type"] not in ("london_session", "ny_session", "asia_session"):
            continue
        if r["bias"] not in ("long", "short") or not r.get("price"):
            continue
        t = _ts(r["ts_utc"]); a = r["asset"]; p = float(r["price"])
        when = session_end(t.date(), r["type"])
        if when is None or when <= t:   # call gia' oltre la fine sessione -> scarta
            continue
        end = price_at_or_after(a, when)
        if end is None:
            continue
        sign = 1 if r["bias"] == "long" else -1
        ret = (end - p) / p
        recs.append(dict(asset=a, type=r["type"], bias=r["bias"], strength=r["strength"],
                         ret=ret, signed=ret * sign, hit=(ret * sign) > 0))

    def summ(rs):
        if not rs:
            return "n=0"
        n = len(rs); hit = 100 * sum(x["hit"] for x in rs) / n
        avg = 1e4 * sum(x["signed"] for x in rs) / n
        return f"n={n:4} hit={hit:5.1f}%  following medio={avg:+6.1f}bps"

    print("===== CALIBRAZIONE PER SESSIONE (call -> fine sessione) =====")
    print("TOTALE sessioni ", summ(recs))
    print("  LONG          ", summ([x for x in recs if x["bias"] == "long"]))
    print("  SHORT         ", summ([x for x in recs if x["bias"] == "short"]))
    print("\n  --- per tipo di sessione ---")
    for ty in ("london_session", "ny_session", "asia_session"):
        rs = [x for x in recs if x["type"] == ty]
        print(f"  {ty:15}", summ(rs))
        # split long/short per vedere il drift
        print(f"      LONG  ", summ([x for x in rs if x['bias'] == 'long']))
        print(f"      SHORT ", summ([x for x in rs if x['bias'] == 'short']))
    print("\n  --- per asset (tutte le sessioni) ---")
    for a in ["XAUUSD", "EURUSD", "NASDAQ", "BTCUSD", "GBPUSD", "SP500"]:
        print(f"  {a:8}      ", summ([x for x in recs if x["asset"] == a]))
    print("\n  --- per forza ---")
    print("  FORTE         ", summ([x for x in recs if x["strength"]]))
    print("  normale       ", summ([x for x in recs if not x["strength"]]))

    # NEUTRO: la sessione e' davvero piu' piatta?
    import statistics as st
    neu = []
    for r in rows:
        if r["type"] not in ("london_session", "ny_session", "asia_session"):
            continue
        if r["bias"] != "neutral" or not r.get("price"):
            continue
        t = _ts(r["ts_utc"])
        when = session_end(t.date(), r["type"])
        if when is None or when <= t:
            continue
        end = price_at_or_after(r["asset"], when)
        if end:
            neu.append(abs(end - float(r["price"])) / float(r["price"]))
    dirabs = [abs(x["ret"]) for x in recs]
    if neu and dirabs:
        print("\n===== NEUTRO vs direzionali (|movimento di sessione|) =====")
        print(f"  NEUTRO       : {1e4*st.mean(neu):6.1f}bps (n={len(neu)})")
        print(f"  LONG/SHORT   : {1e4*st.mean(dirabs):6.1f}bps (n={len(dirabs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
