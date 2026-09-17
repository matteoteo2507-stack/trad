"""Audit di ESECUZIONE del forward FADE — verifica di conformita', non di risultato.

Esegue le verifiche V1-V6 di docs/FADE_LIVE_AUDIT_PROTOCOL.md sullo storico MT5.

PERCHE' ESISTE
--------------
Il forward e' stato azzerato il 2026-08-27 perche' l'EA non eseguiva la strategia
congelata sul 40% dei trade (ingressi a mercato con SL/TP sull'entry teorica).
Questo script misura *quanto* e *dove* l'esecuzione si discosta dalla spec. Non
misura se la strategia guadagna: quella domanda, con ~46 trade utili, non ha
risposta (sez. 2 del protocollo: effetto minimo rilevabile 0,744R).

REGOLA VINCOLANTE: QUESTO SCRIPT NON GUARDA IL P&L
--------------------------------------------------
Nessun campo di profitto viene letto, aggregato o stampato. Non e' pudore: la
finestra di valutazione del campione live e' ancora pulita (nessuno ha visto gli
esiti) e va tenuta tale finche' la regola di valutazione non e' scritta. Un audit
di conformita' non ha bisogno del profitto, quindi non lo tocca. La funzione
_assert_no_pnl() lo impone sul dizionario di ogni trade prima di stamparlo.

USO
---
    python analysis/nxt/execution_audit.py            # report a schermo
    python analysis/nxt/execution_audit.py --md FILE  # anche su file markdown

Richiede il terminale MT5 aperto e loggato sul conto del forward.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections import defaultdict

MAGIC = 26071  # nxt_fade
UNIVERSE = {"EURUSD.r", "GBPUSD.r", "USDJPY.r", "XAUUSD.cyr", "US100", "US500"}

START = dt.datetime(2026, 7, 1)
END = dt.datetime(2030, 1, 1)

# Il conteggio va SEMPRE spezzato ai fix noti, altrimenti si rilegge un problema
# gia' risolto come se fosse in corso (feedback: binario / fonte autorevole).
FIXES = [
    (dt.date(2026, 8, 13), "riaggancio simboli .r + stacco BTCUSD (prereg sez.9)"),
    (dt.date(2026, 8, 27), "fix pendenti orfani / strumento congelato (prereg sez.10)"),
    (dt.date(2026, 9, 17), "v1.10: rimosso l'ingresso a mercato, setup saltato (SKIP)"),
]

RR_ATTESO = 3.0          # TP = 3R (prereg sez.2)
TOL_RR = 0.05            # 5% di tolleranza sul rapporto
TOL_RISCHIO = 0.10       # 10% sul multiplo di rischio reale/inteso

# Campi che non devono MAI comparire in un record di questo script.
VIETATI = ("profit", "pnl", "swap", "commission", "equity", "balance")


def _assert_no_pnl(rec: dict) -> None:
    """Fallisce rumorosamente se un record contiene un campo di risultato."""
    for k in rec:
        low = k.lower()
        for v in VIETATI:
            if v in low:
                raise AssertionError(
                    "Questo script non puo' esporre '%s': vedi docstring e "
                    "docs/FADE_LIVE_AUDIT_PROTOCOL.md sez.4" % k
                )


def _mt5():
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("MetaTrader5 non installato: pip install MetaTrader5", file=sys.stderr)
        return None
    if not mt5.initialize():
        print("initialize() fallito: %s" % (mt5.last_error(),), file=sys.stderr)
        print("Serve il terminale MT5 aperto e loggato sul conto del forward.",
              file=sys.stderr)
        return None
    return mt5


def _fase(t: dt.datetime) -> int:
    """Indice della fase: 0 = prima del primo fix, len(FIXES) = dopo l'ultimo."""
    for i, (d, _) in enumerate(FIXES):
        if t.date() < d:
            return i
    return len(FIXES)


def raccogli(mt5):
    """Costruisce un record per ogni INGRESSO, senza mai leggere il profitto."""
    orders = {o.ticket: o for o in (mt5.history_orders_get(START, END) or [])
              if o.magic == MAGIC}
    deals = [d for d in (mt5.history_deals_get(START, END) or []) if d.magic == MAGIC]

    pendenti = {mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP}
    a_mercato = {mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL}

    trades = []
    for d in deals:
        if d.entry != mt5.DEAL_ENTRY_IN:
            continue                      # solo gli ingressi: le uscite parlano di esito
        o = orders.get(d.order)
        t = dt.datetime.fromtimestamp(d.time)

        rec = {
            "ticket": d.order,
            "symbol": d.symbol,
            "time": t,
            "fase": _fase(t),
            "volume": d.volume,
            "prezzo_reale": d.price,
            # dall'ordine: il prezzo pre-registrato e i livelli congelati
            "tipo_ordine": int(o.type) if o else None,
            "prezzo_ordine": float(o.price_open) if o else None,
            "sl": float(o.sl) if o else None,
            "tp": float(o.tp) if o else None,
        }
        rec["pendente"] = rec["tipo_ordine"] in pendenti if o else None
        rec["mercato"] = rec["tipo_ordine"] in a_mercato if o else None
        _assert_no_pnl(rec)
        trades.append(rec)

    trades.sort(key=lambda r: r["time"])
    return trades


# --- le verifiche ----------------------------------------------------------
def v1_tipo_ordine(t):
    """100% pendenti. Un ingresso a mercato NON e' la strategia pre-registrata."""
    if t["tipo_ordine"] is None:
        return None
    return bool(t["pendente"])


def v2_prezzo_fill(t, tol_punti=None):
    """Il fill deve avvenire al prezzo pre-registrato (slippage del broker a parte).

    Per un ordine a mercato il confronto non ha senso: e' gia' V1 a bocciarlo.
    """
    if not t["pendente"] or not t["prezzo_ordine"]:
        return None
    scarto = abs(t["prezzo_reale"] - t["prezzo_ordine"])
    rel = scarto / t["prezzo_ordine"] if t["prezzo_ordine"] else 0.0
    t["scarto_fill_rel"] = rel
    return rel <= (tol_punti if tol_punti is not None else 1e-4)


def v3_rischio(t):
    """Multiplo di rischio reale / inteso — valutabile anche sugli ordini a mercato.

    Per un ordine a mercato MT5 non conserva l'entry teorica (price_open = 0), ma la
    si ricostruisce esattamente da SL e TP, che l'EA calcola entrambi su di essa:
        |tp - sl| = R + RR*R = (1 + RR) * R   ->   R_inteso = |tp - sl| / (1 + RR)
        entry_teorica = sl + R  (long)  |  sl - R  (short)
    Il volume e' stato dimensionato su R_inteso; il conto rischia invece
    |prezzo_reale - sl|. Conforme se il rapporto e' 1, entro tolleranza.
    Misurato il 27/08 sul ramo a mercato: 1,3x - 4,0x.
    """
    if not t["sl"] or not t["tp"]:
        return None
    inteso = abs(t["tp"] - t["sl"]) / (1.0 + RR_ATTESO)
    if inteso <= 0:
        return None
    t["risk_inteso"] = inteso
    t["entry_teorica"] = t["sl"] + inteso if t["tp"] > t["sl"] else t["sl"] - inteso
    t["mult_rischio"] = abs(t["prezzo_reale"] - t["sl"]) / inteso
    return abs(t["mult_rischio"] - 1.0) <= TOL_RISCHIO


def v4_rr(t):
    """SL/TP effettivi in rapporto 1:3 rispetto al prezzo di ingresso reale."""
    if not t["sl"] or not t["tp"]:
        return None
    rischio = abs(t["prezzo_reale"] - t["sl"])
    premio = abs(t["tp"] - t["prezzo_reale"])
    if rischio <= 0:
        return None
    t["rr_reale"] = premio / rischio
    return abs(t["rr_reale"] - RR_ATTESO) <= RR_ATTESO * TOL_RR


def v5_sovrapposizioni(trades, mt5):
    """Un solo setup attivo per strumento: due ingressi sullo stesso simbolo senza
    un'uscita in mezzo sono una violazione. Usa solo i TEMPI, non gli esiti."""
    uscite = defaultdict(list)
    for d in (mt5.history_deals_get(START, END) or []):
        if d.magic == MAGIC and d.entry == mt5.DEAL_ENTRY_OUT:
            uscite[d.symbol].append(dt.datetime.fromtimestamp(d.time))
    for v in uscite.values():
        v.sort()

    viol = []
    per_sym = defaultdict(list)
    for t in trades:
        per_sym[t["symbol"]].append(t["time"])
    for sym, ingressi in per_sym.items():
        ingressi.sort()
        for a, b in zip(ingressi, ingressi[1:]):
            if not any(a < u <= b for u in uscite.get(sym, [])):
                viol.append((sym, a, b))
    return viol


def v6_setup_saltati(trades):
    """Quanti setup la v1.10 avrebbe saltato.

    Prima del fix un setup 'gia' oltrepassato' diventava un ingresso a mercato:
    il loro numero E' la misura di quanti setup la regola pre-registrata non
    avrebbe mai preso, e quindi di quanto il ramo pendente sia SELEZIONATO
    (protocollo sez.3). Dopo il fix il conteggio arriva dai log [SKIP] dell'EA,
    non dallo storico: qui si puo' misurare solo il periodo pre-fix.
    """
    return sum(1 for t in trades if t.get("mercato"))


# --- report ----------------------------------------------------------------
def esegui(mt5):
    trades = raccogli(mt5)
    L = []
    A = L.append
    A("# Audit di esecuzione FADE (magic %d)" % MAGIC)
    A("")
    A("Generato il %s. Protocollo: docs/FADE_LIVE_AUDIT_PROTOCOL.md"
      % dt.date.today().isoformat())
    A("")
    A("**Questo report non contiene P&L, per costruzione.** Misura la conformita'")
    A("dell'esecuzione alla spec congelata, non il risultato della strategia.")
    A("")

    if not trades:
        A("_Nessun ingresso trovato nella finestra._")
        return "\n".join(L), trades

    fuori = sorted({t["symbol"] for t in trades} - UNIVERSE)
    if fuori:
        A("> ATTENZIONE: simboli fuori dall'universo pre-registrato: %s"
          % ", ".join(fuori))
        A("")

    fasi = ["prima del %s" % FIXES[0][0]] + \
           ["dopo %s (%s)" % (d.isoformat(), nome) for d, nome in FIXES]

    A("## Conteggi per fase")
    A("")
    A("| fase | ingressi | pendenti | a mercato |")
    A("|---|---|---|---|")
    for i, nome in enumerate(fasi):
        sel = [t for t in trades if t["fase"] == i]
        if not sel:
            continue
        pend = sum(1 for t in sel if t.get("pendente"))
        merc = sum(1 for t in sel if t.get("mercato"))
        A("| %s | %d | %d | **%d** |" % (nome, len(sel), pend, merc))
    A("")

    A("## Verifiche")
    A("")
    A("| # | verifica | conformi | non conformi | non valutabili |")
    A("|---|---|---|---|---|")
    for nome, fn in (("V1", v1_tipo_ordine), ("V2", v2_prezzo_fill),
                     ("V3", v3_rischio), ("V4", v4_rr)):
        ok = ko = na = 0
        for t in trades:
            r = fn(t)
            if r is None:
                na += 1
            elif r:
                ok += 1
            else:
                ko += 1
        etichetta = {"V1": "tipo di ordine e' pendente",
                     "V2": "fill al prezzo pre-registrato",
                     "V3": "rischio reale = rischio inteso",
                     "V4": "rapporto SL/TP = 1:3"}[nome]
        segno = "" if ko == 0 else " **FALLITA**"
        A("| %s | %s%s | %d | %d | %d |" % (nome, etichetta, segno, ok, ko, na))

    viol = v5_sovrapposizioni(trades, mt5)
    A("| V5 | un solo setup attivo per strumento%s | %d | %d | - |"
      % ("" if not viol else " **FALLITA**", len(trades) - len(viol), len(viol)))
    A("")

    saltati = v6_setup_saltati(trades)
    A("## V6 - selezione del campione")
    A("")
    A("Setup entrati a mercato, cioe' che la regola pre-registrata **non avrebbe")
    A("preso**: **%d su %d** (%.0f%%)." % (saltati, len(trades),
                                           100.0 * saltati / len(trades)))
    A("")
    A("Ognuno ha occupato lo slot dello strumento (un solo setup attivo), quindi")
    A("ha impedito i setup successivi. Il ramo pendente non e' un sottoinsieme")
    A("casuale: e' il complemento di questa selezione (protocollo sez.3).")
    A("")

    peggiori = sorted((t for t in trades if t.get("mult_rischio")),
                      key=lambda t: -t["mult_rischio"])[:8]
    if peggiori:
        A("## Multipli di rischio piu' alti osservati")
        A("")
        A("Il rischio inteso e' ricostruito da |tp - sl| / 4, cioe' la distanza su cui")
        A("l'EA ha dimensionato il volume. Un multiplo di 2,00x significa che il conto")
        A("ha rischiato il doppio dell'1% previsto su quel trade.")
        A("")
        A("| simbolo | data | ingresso | rischio reale / inteso | RR reale |")
        A("|---|---|---|---|---|")
        for t in peggiori:
            A("| %s | %s | %s | **%.2fx** | 1:%.2f |"
              % (t["symbol"], t["time"].strftime("%Y-%m-%d %H:%M"),
                 "mercato" if t.get("mercato") else "pendente",
                 t["mult_rischio"], t.get("rr_reale", float("nan"))))
        A("")
        esposti = [t for t in trades if t.get("mult_rischio", 0) > 1 + TOL_RISCHIO]
        if esposti:
            mm = max(t["mult_rischio"] for t in esposti)
            A("Trade che hanno rischiato piu' del previsto: **%d su %d**, "
              "fino a **%.2fx**." % (len(esposti), len(trades), mm))
            A("")

    A("## Come si legge questo report")
    A("")
    A("Se V1 non e' 100% conforme, i trade raccolti **non sono la strategia**")
    A("pre-registrata e il campione non serve a stimare E[R], ne' ora ne' mai")
    A("(protocollo sez.5). Nessun ramo di questo audit puo' produrre un GO.")
    return "\n".join(L), trades


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md", help="scrive il report anche su questo file markdown")
    a = ap.parse_args()

    mt5 = _mt5()
    if mt5 is None:
        return 2
    try:
        report, trades = esegui(mt5)
    finally:
        mt5.shutdown()

    # ASCII-only: la console Windows e' cp1252 e ci ha gia' fatto fallire uno
    # script il 2026-09-15.
    sys.stdout.write(report.encode("ascii", "replace").decode("ascii") + "\n")
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print("\n[scritto] %s" % a.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
