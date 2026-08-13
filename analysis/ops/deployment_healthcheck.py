"""Health-check settimanale del deployment EA su MT5.

Nasce dal bug del 2026-08-12: per TRE SETTIMANE l'EA e' rimasto agganciato a simboli
forex non negoziabili (`[Trade disabled]`) senza che nulla lo dichiarasse. Grafici attivi,
EA in esecuzione, log che scorreva — e zero trade. Il segnale stava in cio' che MANCAVA.

Questo script risponde a quattro domande in dieci secondi:
  1. Ogni strumento dell'universo pre-registrato ha almeno un ordine nello storico?
  2. Quanti ordini vengono RIFIUTATI, e per quale motivo?
  3. Ci sono strumenti FUORI universo che stanno operando?
  4. Il rischio effettivo per trade e' quello atteso?

Uso: python analysis/ops/deployment_healthcheck.py [giorni]   (default 30)
"""
from __future__ import annotations

import collections
import datetime as dt
import sys

try:
    import MetaTrader5 as mt5
except ImportError:
    print("MetaTrader5 non installato: pip install MetaTrader5")
    sys.exit(1)

# universo PRE-REGISTRATO (docs/NXT_FADE_FORWARD_PREREGISTRATION.md §2), coi suffissi del broker
UNIVERSE = {"EURUSD.r", "GBPUSD.r", "USDJPY.r", "XAUUSD.cyr", "US100", "US500"}
MAGIC = {26071: "nxt_fade", 26052: "orb_nasdaq"}
RISK_ATTESO_PCT = 0.25          # frazione*100 attesa da InpRiskPerTradePct
N_TARGET = 50                   # Stadio 1 della pre-registrazione

ORDER_STATE = {0: "STARTED", 1: "PLACED", 2: "CANCELED", 3: "PARTIAL",
               4: "FILLED", 5: "REJECTED", 6: "EXPIRED"}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    if not mt5.initialize():
        print(f"initialize() fallita: {mt5.last_error()}")
        return
    ai = mt5.account_info()
    frm = dt.datetime.now() - dt.timedelta(days=days)
    orders = mt5.history_orders_get(frm, dt.datetime.now()) or []
    deals = mt5.history_deals_get(frm, dt.datetime.now()) or []

    print("=" * 84)
    print(f"HEALTH-CHECK DEPLOYMENT — {ai.login} @ {ai.server} — ultimi {days} giorni")
    print(f"equity {ai.equity:,.2f} {ai.currency}")
    print("=" * 84)

    # ---- 1. copertura dell'universo -------------------------------------------------
    # NB: history_orders_get() NON contiene i pendenti ancora attivi -> vanno sommati,
    # altrimenti uno strumento agganciato e funzionante ma senza fill risulta "scoperto".
    live = mt5.orders_get() or []
    seen = collections.Counter(o.symbol for o in orders)
    seen_live = collections.Counter(o.symbol for o in live)
    print("\n[1] COPERTURA UNIVERSO PRE-REGISTRATO")
    missing = []
    for s in sorted(UNIVERSE):
        n, nl = seen.get(s, 0), seen_live.get(s, 0)
        flag = "OK " if (n + nl) > 0 else "!! "
        if n + nl == 0:
            missing.append(s)
        extra = f"  (+{nl} pendenti attivi)" if nl else ""
        print(f"  {flag} {s:14} ordini storici: {n}{extra}")
    if missing:
        print(f"\n  *** ALLARME: nessun ordine su {', '.join(missing)}")
        print("      Cause tipiche: EA non agganciato, simbolo sbagliato (suffisso!),")
        print("      simbolo disabilitato alla negoziazione. Controlla il log Experts.")

    # ---- 2. rifiuti -----------------------------------------------------------------
    print("\n[2] ORDINI NON ESEGUITI")
    bad = [o for o in orders if o.state != 4]
    if not bad:
        print("  nessuno")
    else:
        c = collections.Counter((o.symbol, ORDER_STATE.get(o.state, o.state),
                                 (o.comment or "").strip()) for o in bad)
        for (sym, st, cm), n in sorted(c.items(), key=lambda x: -x[1]):
            print(f"  {sym:14} {st:9} x{n:<4} {cm}")
        print(f"\n  totale non eseguiti: {len(bad)} su {len(orders)} "
              f"({100*len(bad)/max(len(orders),1):.1f}%)")
        print("  NB: un dropout per margine NON e' casuale — colpisce i setup con lo stop")
        print("      piu' stretto (volume maggiore) e distorce il campione del forward.")

    # ---- 3. strumenti fuori universo -------------------------------------------------
    print("\n[3] STRUMENTI FUORI UNIVERSO")
    extra = {s: n for s, n in seen.items() if s not in UNIVERSE}
    if not extra:
        print("  nessuno")
    else:
        for s, n in sorted(extra.items(), key=lambda x: -x[1]):
            print(f"  !! {s:14} ordini: {n}   <-- NON pre-registrato: staccare l'EA")

    # ---- 4. rischio effettivo --------------------------------------------------------
    print("\n[4] RISCHIO EFFETTIVO PER TRADE (posizioni aperte)")
    pos = mt5.positions_get() or []
    if not pos:
        print("  nessuna posizione aperta")
    for p in pos:
        si = mt5.symbol_info(p.symbol)
        if si is None or not p.sl or si.trade_tick_size <= 0:
            continue
        risk = abs(p.price_open - p.sl)
        money = (risk / si.trade_tick_size) * si.trade_tick_value * p.volume
        pct = 100 * money / ai.equity if ai.equity else 0
        note = "" if abs(pct - RISK_ATTESO_PCT) < 0.15 or risk == 0 else "  <-- fuori atteso"
        print(f"  {p.symbol:14} vol={p.volume:<8} rischio={money:9.2f} "
              f"= {pct:5.2f}% equity (atteso ~{RISK_ATTESO_PCT}%){note}")

    # ---- 5. conteggio verso N ---------------------------------------------------------
    print(f"\n[5] CONTEGGIO FORWARD (Stadio 1: N={N_TARGET})")
    closed = collections.Counter(d.symbol for d in deals
                                 if d.entry == 1 and d.magic == 26071)
    n_in = sum(v for k, v in closed.items() if k in UNIVERSE)
    n_out = sum(v for k, v in closed.items() if k not in UNIVERSE)
    for s, n in sorted(closed.items()):
        tag = "" if s in UNIVERSE else "  (ESCLUSO: fuori universo)"
        print(f"  {s:14} chiusi: {n}{tag}")
    print(f"\n  N valido = {n_in}/{N_TARGET}" + (f"   (esclusi {n_out} fuori universo)" if n_out else ""))
    print(f"  breadth: {sum(1 for s in UNIVERSE if closed.get(s,0)>0)}/{len(UNIVERSE)} strumenti con trade chiusi")

    mt5.shutdown()


if __name__ == "__main__":
    main()
