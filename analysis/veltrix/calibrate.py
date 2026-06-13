"""Punto 2: calibrazione dell'hit-rate direzionale del bot AlphaAnalist/VELTRIX.

Domanda: quando il bot dice LONG/SHORT, il prezzo si muove davvero in quella
direzione? E quanto è affidabile per asset / tipo di messaggio / accordo dei
timeframe / forza del segnale?

Outcome senza dipendenze esterne: si usa il **timeline di prezzo del bot stesso**
(ogni messaggio riporta il prezzo dell'asset). Per ogni call direzionale al tempo
t con prezzo p, si prende il prezzo p' alla prima quotazione >= t+H (orizzonti 4h
e 24h) e si calcola ret=(p'-p)/p. Hit = segno(ret) concorde col bias.

Attenzione drift: nel periodo l'oro scende e NASDAQ/BTC salgono, quindi "sempre
short gold"/"sempre long nasdaq" hanno hit-rate alto per drift, non per edge. Per
questo si riportano hit-rate LONG e SHORT separati e il confronto con un baseline
naive (segui sempre il drift dell'asset) + il rendimento medio del following.

Uso:
    python -m analysis.veltrix.calibrate
"""

from __future__ import annotations

import json
import sys
from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timedelta

SIG = "analysis/veltrix/signals.jsonl"
HORIZONS = [("4h", timedelta(hours=4)), ("24h", timedelta(hours=24))]


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rows = [json.loads(l) for l in open(SIG, encoding="utf-8")]
    rows = [r for r in rows if r.get("asset")]  # scarta i 2 frammenti senza asset

    # Timeline prezzi per asset (da QUALSIASI riga con prezzo).
    tl: dict[str, list[tuple[datetime, float]]] = defaultdict(list)
    for r in rows:
        if r.get("price"):
            tl[r["asset"]].append((_ts(r["ts_utc"]), float(r["price"])))
    for a in tl:
        tl[a].sort()

    def fwd_price(asset: str, t: datetime, h: timedelta) -> float | None:
        series = tl.get(asset)
        if not series:
            return None
        times = [x[0] for x in series]
        i = bisect_left(times, t + h)
        if i >= len(series):
            return None
        return series[i][1]

    # Calibrazione per ogni call direzionale.
    records = []
    for r in rows:
        if r["bias"] not in ("long", "short") or not r.get("price"):
            continue
        t = _ts(r["ts_utc"]); p = float(r["price"]); sign = 1 if r["bias"] == "long" else -1
        agree = sum(1 for k in ("tf_d", "tf_4h", "tf_1h")
                    if r.get(k) is not None and (1 if r[k] > 0 else -1 if r[k] < 0 else 0) == sign)
        for hl, hd in HORIZONS:
            pf = fwd_price(r["asset"], t, hd)
            if pf is None:
                continue
            ret = (pf - p) / p
            records.append(dict(asset=r["asset"], type=r["type"], bias=r["bias"],
                                strength=r["strength"], agree=agree, h=hl,
                                ret=ret, signed=ret * sign, hit=(ret * sign) > 0))

    def summ(rs):
        n = len(rs)
        if not n:
            return "n=0"
        hit = 100 * sum(x["hit"] for x in rs) / n
        avg = 1e4 * sum(x["signed"] for x in rs) / n  # rendimento medio del following in bps
        return f"n={n:4} hit={hit:5.1f}%  ritorno-following medio={avg:+6.1f}bps"

    for hl, _ in HORIZONS:
        rs = [x for x in records if x["h"] == hl]
        print(f"\n================ ORIZZONTE {hl} ================")
        print("TOTALE          ", summ(rs))
        print("  LONG          ", summ([x for x in rs if x["bias"] == "long"]))
        print("  SHORT         ", summ([x for x in rs if x["bias"] == "short"]))
        print("  --- per asset ---")
        for a in ["XAUUSD", "EURUSD", "NASDAQ", "BTCUSD", "GBPUSD", "SP500"]:
            print(f"  {a:8}      ", summ([x for x in rs if x["asset"] == a]))
        print("  --- per tipo messaggio ---")
        for ty in ("alert_daily", "ny_session", "london_session", "asia_session", "close_report"):
            print(f"  {ty:14}", summ([x for x in rs if x["type"] == ty]))
        print("  --- per accordo timeframe (quanti dei 3 TF concordano col bias) ---")
        for k in (3, 2, 1, 0):
            print(f"  {k}/3 TF        ", summ([x for x in rs if x["agree"] == k]))
        print("  --- per forza ---")
        print("  FORTE         ", summ([x for x in rs if x["strength"]]))
        print("  normale       ", summ([x for x in rs if not x["strength"]]))

    # Baseline drift: hit-rate di "segui sempre il drift dell'asset" = quota di ret>0.
    print("\n================ BASELINE DRIFT (quota mosse positive, per asset, 24h) ===")
    rs24 = [x for x in records if x["h"] == "24h"]
    for a in ["XAUUSD", "EURUSD", "NASDAQ", "BTCUSD", "GBPUSD", "SP500"]:
        ar = [x for x in rs24 if x["asset"] == a]
        if ar:
            up = 100 * sum(x["ret"] > 0 for x in ar) / len(ar)
            print(f"  {a:8}  mosse-su={up:5.1f}%  (se ~50% niente drift; lontano da 50% = drift forte)")

    # Neutral: il bot quando dice NEUTRO becca davvero le fasi piatte?
    print("\n================ NEUTRO: |ret| medio vs direzionali (24h) ============")
    neu = []
    for r in rows:
        if r["bias"] == "neutral" and r.get("price"):
            pf = fwd_price(r["asset"], _ts(r["ts_utc"]), timedelta(hours=24))
            if pf:
                neu.append(abs(pf - float(r["price"])) / float(r["price"]))
    dirabs = [abs(x["ret"]) for x in rs24]
    import statistics as st
    if neu and dirabs:
        print(f"  |ret| NEUTRO  : {1e4*st.mean(neu):6.1f}bps (n={len(neu)})")
        print(f"  |ret| LONG/SHORT: {1e4*st.mean(dirabs):6.1f}bps (n={len(dirabs)})")
        print("  -> se NEUTRO ha |ret| più basso, il bot identifica davvero le fasi piatte.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
