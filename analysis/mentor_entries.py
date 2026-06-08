"""Reverse-engineering ingressi mentore (canale 1) vs detector in libreria.

Per ogni ingresso storico (da messaggitg.txt) ricostruisce il contesto di prezzo
*disponibile fino a quel momento* (no look-ahead) e misura quanto l'entry e' vicino
ai livelli prodotti dai detector che gia' abbiamo:
  - S/R  (swing pivot + cluster)            strategies/confluence_auto/detectors/sr
  - S/D  (base-impulse-base)                .../sd
  - POC/VAH/VAL/HVN/LVN (volume profile)    .../poc
piu' feature semplici: numeri tondi ($10/$50), PDH/PDL, range asiatico.

Allineamento TZ (verificato con probe_mt5): le label barre sono UTC reale;
`copy_rates_from` interpreta l'input come ora-macchina (CEST=UTC+2), quindi gli
orari locali di messaggitg.txt si passano tali e quali. entry_utc = locale - 2h.

Uso (terminale MT5 aperto su DEMO3):
    python -m analysis.mentor_entries
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from brokers.mt5 import MT5Broker
from strategies.confluence_auto.detectors import (
    detect_poc_levels,
    detect_sd_zones,
    detect_sr_levels,
)

PIP = 0.10
LOCAL_OFFSET_H = 2  # CEST = UTC+2 (date estive: maggio-giugno)


@dataclass
class Trade:
    n: int
    local_dt: datetime  # naive, ora locale CEST (= input MT5)
    side: str
    entry: float
    sl: float
    tps: list[float]
    outcome: str


def parse_trades(path: str) -> list[Trade]:
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"\n(?=\d+-\s)", text)
    out: list[Trade] = []
    for b in blocks:
        m = re.search(r"(\d+)-\s+(\d{1,2}):(\d{2})\s+(\d{1,2})[.\-](\d{2})", b)
        if not m:
            continue
        n = int(m.group(1)); hh = int(m.group(2)); mm = int(m.group(3))
        day = int(m.group(4)); mon = int(m.group(5))
        side = "SELL" if "SELL" in b else ("BUY" if "BUY" in b else "?")
        e = re.search(r"Entry:\s*([\d.]+)", b)
        sl = re.search(r"Stop Loss:\s*([\d.]+)", b)
        tps = [float(x) for x in re.findall(r"TP\d:\s*([\d.]+)", b)]
        if not e or side == "?":
            continue
        body = b.split("Stop Loss")[1] if "Stop Loss" in b else ""
        if "All TP" in b:
            oc = "ALL"
        elif "TP2 SUCCESSFUL" in b:
            oc = "TP2"
        elif "TP1 SUCCESSFUL" in b:
            oc = "TP1"
        elif re.search(r"\bSL\b", body):
            oc = "SL"
        else:
            oc = "?"
        out.append(Trade(n=n, local_dt=datetime(2026, mon, day, hh, mm), side=side,
                         entry=float(e.group(1)), sl=float(sl.group(1)) if sl else 0.0,
                         tps=tps, outcome=oc))
    return out


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


def _nearest(entry: float, prices: list[float]) -> float | None:
    vals = [p for p in prices if p is not None and p == p]  # drop None/NaN
    if not vals:
        return None
    return min(abs(entry - p) for p in vals)


def analyze() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    trades = parse_trades("messaggitg.txt")
    b = _broker()
    rows = []
    for t in trades:
        end = t.local_dt  # naive CEST -> input MT5
        entry_utc = t.local_dt - timedelta(hours=LOCAL_OFFSET_H)
        try:
            d1 = b.get_bars_until("XAUUSD", "D1", end, 300)
            h4 = b.get_bars_until("XAUUSD", "H4", end, 500)
            m15 = b.get_bars_until("XAUUSD", "M15", end, 600)
        except Exception as exc:
            print(f"#{t.n}: fetch fallito ({exc}) - salto")
            continue

        sr_d1 = detect_sr_levels(d1, threshold_atr_mult=1.5, cluster_width_pips=80,
                                 pip_size=PIP, min_touches=1, max_levels=6, tf_label="D1")
        sr_h4 = detect_sr_levels(h4, threshold_atr_mult=1.2, cluster_width_pips=80,
                                 pip_size=PIP, min_touches=1, max_levels=4, tf_label="H4")
        sd_d1 = detect_sd_zones(d1, base_min_bars=2, base_max_bars=6, base_range_atr_mult=0.5,
                                impulse_atr_mult=1.5, max_touches_for_valid=1, max_zones=4,
                                max_age_days=180, tf_label="D1")
        sd_h4 = detect_sd_zones(h4, base_min_bars=2, base_max_bars=6, base_range_atr_mult=0.5,
                                impulse_atr_mult=1.5, max_touches_for_valid=1, max_zones=6,
                                max_age_days=60, tf_label="H4")
        poc = detect_poc_levels(m15.tail(480), window_label="weekly", n_bins=100,
                                value_area_pct=0.70, hvn_threshold_pct=0.7, lvn_threshold_pct=0.2)

        # Livelli per direzione: dove "ci si aspetta" un BUY (support/demand) vs SELL (res/supply).
        supports = [L.price for L in sr_d1 + sr_h4 if L.kind == "low"]
        resist = [L.price for L in sr_d1 + sr_h4 if L.kind == "high"]
        demand = [z.proximal for z in sd_d1 + sd_h4 if z.kind == "demand"]
        supply = [z.proximal for z in sd_d1 + sd_h4 if z.kind == "supply"]
        poc_prices = [L.price for L in poc]

        # Livello "pro-direzione": BUY -> support/demand sotto/al prezzo; SELL -> res/supply.
        if t.side == "BUY":
            pro = supports + demand
        else:
            pro = resist + supply

        # PDH/PDL: high/low del giorno precedente (ultima barra D1 completata < oggi).
        day0 = entry_utc.date()
        prev = d1[d1.index.date < day0]
        pdh = float(prev["high"].iloc[-1]) if len(prev) else None
        pdl = float(prev["low"].iloc[-1]) if len(prev) else None

        # Range asiatico: 00:00-08:00 UTC del giorno dell'ingresso.
        asia = m15[(m15.index.date == day0) & (m15.index.hour < 8)]
        ah = float(asia["high"].max()) if len(asia) else None
        al = float(asia["low"].min()) if len(asia) else None

        # Numeri tondi.
        r10 = abs(t.entry - round(t.entry / 10) * 10)
        r50 = abs(t.entry - round(t.entry / 50) * 50)

        # Controllo: prezzo casuale a +/-$25 dall'entry, stesso contesto/detector.
        # Se l'entry e' davvero "attratto" da un criterio, sara' piu' vicino del random.
        import random
        ctrl = t.entry + random.uniform(-25, 25)

        rows.append(dict(
            n=t.n, side=t.side, oc=t.outcome, entry=t.entry,
            sess=_session(entry_utc),
            sr=_nearest(t.entry, supports + resist),
            sd=_nearest(t.entry, demand + supply),
            pro=_nearest(t.entry, pro),
            poc=_nearest(t.entry, poc_prices),
            pdh_pdl=_nearest(t.entry, [pdh, pdl]),
            asia=_nearest(t.entry, [ah, al]),
            r10=r10, r50=r50,
            # versioni di controllo (prezzo random)
            c_sr=_nearest(ctrl, supports + resist),
            c_pro=_nearest(ctrl, pro),
            c_poc=_nearest(ctrl, poc_prices),
        ))
    b.disconnect()
    _report(rows)
    return 0


def _session(dt_utc: datetime) -> str:
    h = dt_utc.hour
    if h < 7:
        return "ASIA"
    if h < 12:
        return "LONDON"
    return "NY"


def _report(rows: list[dict]) -> None:
    if not rows:
        print("Nessun dato.")
        return
    print(f"\n{'#':>3} {'side':>4} {'oc':>4} {'entry':>8} {'sess':>6}"
          f" {'SR':>6} {'SD':>6} {'PRO':>6} {'POC':>6} {'PDHL':>6} {'ASIA':>6} {'r10':>5} {'r50':>5}")
    def f(x):
        return f"{x:6.2f}" if isinstance(x, (int, float)) and x is not None else "   -- "
    for r in rows:
        print(f"{r['n']:>3} {r['side']:>4} {r['oc']:>4} {r['entry']:>8.2f} {r['sess']:>6}"
              f" {f(r['sr'])} {f(r['sd'])} {f(r['pro'])} {f(r['poc'])} {f(r['pdh_pdl'])}"
              f" {f(r['asia'])} {r['r10']:5.1f} {r['r50']:5.1f}")

    # Riepilogo: mediana distanza e % entro soglie ($1.5 e $3.0) per criterio.
    import statistics as st
    print(f"\n{'criterio':>8} {'n':>3} {'mediana$':>9} {'<=1.5$':>7} {'<=3.0$':>7}")
    for key, label in [("sr", "SR"), ("sd", "SD"), ("pro", "PRO-dir"), ("poc", "POC"),
                       ("pdh_pdl", "PDH/PDL"), ("asia", "ASIA"), ("r10", "round10"),
                       ("r50", "round50")]:
        vals = [r[key] for r in rows if r[key] is not None]
        if not vals:
            print(f"{label:>8}   0      --      --      --")
            continue
        med = st.median(vals)
        p15 = 100 * sum(v <= 1.5 for v in vals) / len(vals)
        p30 = 100 * sum(v <= 3.0 for v in vals) / len(vals)
        print(f"{label:>8} {len(vals):>3} {med:9.2f} {p15:6.0f}% {p30:6.0f}%")
    print(f"\nSessioni: ", {s: sum(r['sess'] == s for r in rows)
                            for s in ('ASIA', 'LONDON', 'NY')})

    # Controllo entry vs prezzo random (stesso contesto): mediana distanza.
    print(f"\nControllo (mediana $ ENTRY vs RANDOM, stesso contesto):")
    for key, ckey, label in [("sr", "c_sr", "SR"), ("pro", "c_pro", "PRO-dir"),
                             ("poc", "c_poc", "POC")]:
        ev = [r[key] for r in rows if r[key] is not None]
        cv = [r[ckey] for r in rows if r[ckey] is not None]
        if ev and cv:
            print(f"  {label:>8}: entry {st.median(ev):6.2f}  vs  random {st.median(cv):6.2f}"
                  f"   ({'ATTRAE' if st.median(ev) < st.median(cv) * 0.7 else 'non distinguibile'})")


if __name__ == "__main__":
    raise SystemExit(analyze())
