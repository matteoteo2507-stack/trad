"""Reverse-engineering ingressi mentore — ipotesi momentum/continuazione + intrabar.

Visto che nessun criterio level-based fissa l'ingresso (vedi mentor_entries.py),
qui si testa il COME entra, non il DOVE:

  A) Continuazione vs reversione: la direzione dell'ingresso concorda col trend
     recente (H1, M15)? baseline = 50% (coin flip).
  B) Dip vs breakout: dentro l'ultima ora, l'entry e' vicino al minimo (BUY) /
     massimo (SELL) -> "compra il ribasso/vende il rialzo" (mean-reversion), o
     vicino all'estremo opposto -> "rompe" (momentum)?
  C) Spinta immediata: nei 15' prima, il prezzo si muove A FAVORE (breakout) o
     CONTRO (pullback poi entry) la direzione?

Tutto look-ahead-safe: si scarta la barra in formazione all'istante d'ingresso.

Uso (terminale MT5 aperto su DEMO3):
    python -m analysis.mentor_momentum
"""

from __future__ import annotations

import statistics as st
import sys
from datetime import timedelta

from analysis.mentor_entries import LOCAL_OFFSET_H, parse_trades, _broker, _session


def _trend_sign(closes, n: int) -> int:
    if len(closes) <= n:
        return 0
    diff = float(closes[-1] - closes[-1 - n])
    return 1 if diff > 0 else (-1 if diff < 0 else 0)


def analyze() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    trades = parse_trades("messaggitg.txt")
    b = _broker()
    rows = []
    for t in trades:
        end = t.local_dt
        entry_utc = t.local_dt - timedelta(hours=LOCAL_OFFSET_H)
        side_sign = 1 if t.side == "BUY" else -1
        try:
            h1 = b.get_bars_until("XAUUSD", "H1", end, 12)
            m15 = b.get_bars_until("XAUUSD", "M15", end, 24)
            m5 = b.get_bars_until("XAUUSD", "M5", end, 36)
            m5d = b.get_bars_until("XAUUSD", "M5", end, 300)  # per VWAP di sessione
        except Exception as exc:
            print(f"#{t.n}: fetch fallito ({exc})")
            continue
        # VWAP intraday dal giorno UTC dell'ingresso fino all'entry (escl. barra in corso).
        day0 = entry_utc.date()
        sess = m5d[m5d.index.date == day0].iloc[:-1]
        if len(sess) >= 3:
            typ = (sess["high"] + sess["low"] + sess["close"]) / 3.0
            vwap = float((typ * sess["volume"]).sum() / max(sess["volume"].sum(), 1))
            day_open = float(sess["open"].iloc[0])
            # extension: quanto l'entry e' "oltre" la media, nel verso del fade.
            # BUY mean-reversion -> entry SOTTO vwap (sconto); SELL -> SOPRA.
            vwap_ext = (vwap - t.entry) if t.side == "BUY" else (t.entry - vwap)
            open_ext = (day_open - t.entry) if t.side == "BUY" else (t.entry - day_open)
        else:
            vwap_ext = open_ext = None
        # Scarta la barra in formazione all'ingresso (evita look-ahead intrabar).
        h1c = h1["close"].to_numpy()[:-1]
        m15c = m15["close"].to_numpy()[:-1]
        m5b = m5.iloc[:-1]

        # A) Continuazione: side concorda col trend?
        align_h1 = (side_sign == _trend_sign(h1c, 4))      # ~4h
        align_m15 = (side_sign == _trend_sign(m15c, 8))     # ~2h

        # B) Dip vs breakout nell'ultima ora (12 barre M5).
        last1h = m5b.tail(12)
        lo = float(last1h["low"].min()); hi = float(last1h["high"].max())
        rng = hi - lo
        if rng <= 0:
            continue
        pos = (t.entry - lo) / rng          # 0=minimo, 1=massimo dell'ora
        # dipscore: 1 = compra sul minimo / vende sul massimo (mean-reversion)
        dipscore = (1 - pos) if t.side == "BUY" else pos

        # C) Spinta immediata: movimento nei 15' prima (3 barre M5) vs direzione.
        last15 = m5b.tail(3)
        push = float(last15["close"].iloc[-1] - last15["open"].iloc[0])
        push_with = (push * side_sign) > 0   # True = spinta a favore (breakout)

        rows.append(dict(n=t.n, side=t.side, oc=t.outcome, sess=_session(entry_utc),
                         align_h1=align_h1, align_m15=align_m15,
                         dipscore=dipscore, range1h=rng, push_with=push_with,
                         vwap_ext=vwap_ext, open_ext=open_ext))
    b.disconnect()
    _report(rows)
    return 0


def _report(rows: list[dict]) -> None:
    if not rows:
        print("Nessun dato.")
        return
    n = len(rows)
    print(f"\n{'#':>3} {'side':>4} {'oc':>4} {'sess':>6} {'alH1':>5} {'alM15':>6}"
          f" {'dip':>5} {'rng1h$':>7} {'push':>6}")
    for r in rows:
        print(f"{r['n']:>3} {r['side']:>4} {r['oc']:>4} {r['sess']:>6}"
              f" {'Y' if r['align_h1'] else 'n':>5} {'Y' if r['align_m15'] else 'n':>6}"
              f" {r['dipscore']:5.2f} {r['range1h']:7.2f} {'with' if r['push_with'] else 'vs':>6}")

    ah1 = 100 * sum(r["align_h1"] for r in rows) / n
    am15 = 100 * sum(r["align_m15"] for r in rows) / n
    dips = [r["dipscore"] for r in rows]
    dip_style = 100 * sum(d >= 0.6 for d in dips) / n
    brk_style = 100 * sum(d <= 0.4 for d in dips) / n
    push_with = 100 * sum(r["push_with"] for r in rows) / n
    print(f"\n=== {n} ingressi ===")
    print(f"A) Continuazione (side = trend), baseline 50%:")
    print(f"   allineato a trend H1(4h):  {ah1:.0f}%")
    print(f"   allineato a trend M15(2h): {am15:.0f}%")
    print(f"B) Dentro l'ultima ora (dipscore: 1=compra minimo/vende massimo):")
    print(f"   mediana dipscore: {st.median(dips):.2f}")
    print(f"   stile DIP/reversione (>=0.6): {dip_style:.0f}%   stile BREAKOUT (<=0.4): {brk_style:.0f}%")
    print(f"C) Spinta nei 15' prima a favore della direzione (breakout): {push_with:.0f}%")
    print(f"\nRange medio dell'ultima ora prima dell'ingresso: ${st.mean([r['range1h'] for r in rows]):.1f}")

    # D) Extension da VWAP / apertura (segno + = entry dal lato 'fade': BUY sotto, SELL sopra).
    vext = [r["vwap_ext"] for r in rows if r["vwap_ext"] is not None]
    oext = [r["open_ext"] for r in rows if r["open_ext"] is not None]
    if vext:
        print(f"D) Mean-reversion vs VWAP/apertura (segno + = entry sul lato dello sconto):")
        print(f"   vs VWAP:     mediana ${st.median(vext):+.2f}   "
              f"% dal lato fade: {100*sum(v>0 for v in vext)/len(vext):.0f}%")
        print(f"   vs apertura: mediana ${st.median(oext):+.2f}   "
              f"% dal lato fade: {100*sum(v>0 for v in oext)/len(oext):.0f}%")


if __name__ == "__main__":
    raise SystemExit(analyze())
