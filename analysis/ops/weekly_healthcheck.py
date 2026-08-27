"""Health-check SETTIMANALE persistito — scrive un report datato in docs/health/.

Perche' esiste. Il 2026-08-27 e' emerso che il problema non era la mancanza dello
strumento (`deployment_healthcheck.py` esisteva ed era corretto) ma che **nessuno lo
eseguiva**, e che leggendone l'output una tantum si legge un **aggregato cumulato**:
197 errori "fra il 2 e il 21 agosto" sembravano un guasto in corso, mentre 196 su 197
erano precedenti a un fix gia' applicato il 12/08. Un allarme al posto di una verifica.

La differenza fra questo script e `deployment_healthcheck.py`:
  - separa SEMPRE il conteggio **prima/dopo** le date dei fix noti;
  - usa una finestra temporale **senza limite superiore** (il primo tentativo usava
    `now + 1 giorno` e tagliava fuori i trade piu' recenti, producendo un secondo
    errore di lettura);
  - **persiste** un report datato, cosi' che N, breadth e anomalie abbiano una serie
    storica e la domanda "e' nuovo o e' il residuo di un problema vecchio?" si risponda
    confrontando due file invece di rileggere un log cumulato;
  - conta anche i **pendenti VIVI** (`orders_get`), non solo lo storico. La prima versione di
    questo script usava solo `history_orders_get`, che **non vede gli ordini ancora attivi**:
    US500 risultava "senza alcun ordine" mentre aveva un pendente piazzato lo stesso giorno.
    Terza variante dello stesso errore: leggere UNA fonte parziale e chiamarla stato.

Uso:
    python analysis/ops/weekly_healthcheck.py            # scrive docs/health/YYYY-MM-DD.md
    python analysis/ops/weekly_healthcheck.py --stdout   # stampa e basta
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTDIR = os.path.join(ROOT, "docs", "health")

# --- configurazione: cio' che il protocollo considera vincolante -------------------
MAGIC = {26071: "nxt_fade", 26052: "orb_nasdaq"}

# universo PRE-REGISTRATO del fade (docs/NXT_FADE_FORWARD_PREREGISTRATION.md §2),
# coi suffissi effettivi del broker
UNIVERSE_FADE = {"EURUSD.r", "GBPUSD.r", "USDJPY.r", "XAUUSD.cyr", "US100", "US500"}

# soglie di Stadio dalla pre-registrazione
STAGE1_N = 50
STAGE2_N = 200
DEADLINE = dt.date(2027, 3, 31)

# date dei fix noti: il conteggio va SEMPRE spezzato qui, altrimenti si rilegge
# un problema gia' risolto come se fosse in corso
FIXES = [
    (dt.date(2026, 8, 13), "riaggancio ai simboli .r + stacco BTCUSD (prereg §9)"),
]

START = dt.datetime(2026, 7, 1)          # inizio del forward
END = dt.datetime(2030, 1, 1)            # nessun taglio superiore: vedi docstring


def _mt5():
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("MetaTrader5 non installato: pip install MetaTrader5", file=sys.stderr)
        return None
    if not mt5.initialize():
        print(f"initialize() fallito: {mt5.last_error()}", file=sys.stderr)
        return None
    return mt5


# un pendente fermo piu' di questi giorni e' sospetto: il setup che lo ha generato e' scaduto
STALE_DAYS = 3


def collect(mt5, magic: int):
    orders = [o for o in (mt5.history_orders_get(START, END) or []) if o.magic == magic]
    deals = [d for d in (mt5.history_deals_get(START, END) or []) if d.magic == magic]
    cut = dt.datetime.combine(FIXES[-1][0], dt.time())

    o_tab = defaultdict(lambda: [0, 0])
    c_tab = defaultdict(lambda: [0, 0])
    rej = defaultdict(lambda: [0, 0])
    for o in orders:
        t = dt.datetime.fromtimestamp(o.time_setup)
        i = 0 if t < cut else 1
        o_tab[o.symbol][i] += 1
        if o.state in (mt5.ORDER_STATE_REJECTED, mt5.ORDER_STATE_CANCELED,
                       mt5.ORDER_STATE_EXPIRED):
            rej[(o.symbol, (o.comment or "").strip()[:30])][i] += 1
    for d in deals:
        if d.entry == mt5.DEAL_ENTRY_OUT:
            t = dt.datetime.fromtimestamp(d.time)
            c_tab[d.symbol][0 if t < cut else 1] += 1

    live = [o for o in (mt5.orders_get() or []) if o.magic == magic]
    pos = [p for p in (mt5.positions_get() or []) if p.magic == magic]
    return o_tab, c_tab, rej, live, pos


def render(mt5) -> str:
    acc = mt5.account_info()
    today = dt.date.today()
    L = []
    L.append(f"# Health-check deployment — {today:%Y-%m-%d}\n")
    L.append("> Generato da `analysis/ops/weekly_healthcheck.py`. **Il conteggio e' sempre "
             "separato prima/dopo i fix noti**: un aggregato cumulato fa sembrare in corso "
             "un guasto gia' risolto (accaduto il 2026-08-27).\n")
    if acc:
        L.append(f"Conto **{acc.login} @ {acc.server}** · equity **{acc.equity:,.2f} {acc.currency}**\n")
    L.append("Fix noti presi come spartiacque:\n")
    for d, why in FIXES:
        L.append(f"- **{d:%Y-%m-%d}** — {why}")
    L.append("")

    for magic, name in MAGIC.items():
        o_tab, c_tab, rej, live, pos = collect(mt5, magic)
        if not o_tab and not c_tab and not live and not pos:
            L.append(f"## `{name}` (magic {magic})\n\n_nessun ordine nella finestra._\n")
            continue
        uni = UNIVERSE_FADE if name == "nxt_fade" else set()
        L.append(f"## `{name}` (magic {magic})\n")
        L.append("| simbolo | in universo | ordini pre/post | chiusi pre/post |")
        L.append("|---|---|---|---|")
        for s in sorted(set(o_tab) | set(c_tab)):
            a, b = o_tab.get(s, [0, 0])
            c, e = c_tab.get(s, [0, 0])
            mark = "—" if not uni else ("si" if s in uni else "**NO**")
            L.append(f"| {s} | {mark} | {a} / **{b}** | {c} / **{e}** |")
        L.append("")

        if uni:
            n_in = sum(sum(c_tab.get(s, [0, 0])) for s in uni)
            out = {s: sum(v) for s, v in c_tab.items() if s not in uni and sum(v)}
            live_sym = {o.symbol for o in live}
            breadth = sum(1 for s in uni
                          if sum(o_tab.get(s, [0, 0])) > 0 or s in live_sym)
            stage = "Stadio 1" if n_in < STAGE1_N else "Stadio 2"
            target = STAGE1_N if n_in < STAGE1_N else STAGE2_N
            L.append(f"**{stage}: N valido = {n_in} / {target}** · breadth "
                     f"**{breadth}/{len(uni)}** strumenti con ordini")
            if out:
                L.append(f"\n⚠️ Chiusi **fuori universo** (esclusi dal conteggio, per decisione "
                         f"utente 2026-08-27): {out}")
            silent = [s for s in uni if sum(o_tab.get(s, [0, 0])) == 0]
            if silent:
                L.append(f"\n⚠️ In universo ma **senza alcun ordine**: {silent} — "
                         f"da verificare che non sia un problema di simbolo o permessi")
            days = (DEADLINE - dt.date.today()).days
            L.append(f"\nScadenza pre-registrata: **{DEADLINE:%Y-%m-%d}** ({days} giorni).")
            L.append("\n> ⚠️ **Il P&L non e' riportato di proposito.** La regola di stop e' "
                     "**N e data**, mai il cumulato: guardarlo sarebbe optional stopping "
                     "(prereg §5).\n")

        L.append(f"**Pendenti vivi**: {len(live)} · **posizioni aperte**: {len(pos)}")
        now = dt.datetime.now()
        for o in sorted(live, key=lambda x: x.time_setup):
            t = dt.datetime.fromtimestamp(o.time_setup)
            age = (now - t).days
            flag = f" ⚠️ **fermo da {age}g**" if age >= STALE_DAYS else ""
            L.append(f"- pendente `{o.symbol}` dal {t:%Y-%m-%d %H:%M}{flag}")
        for p_ in sorted(pos, key=lambda x: x.time):
            L.append(f"- posizione `{p_.symbol}` vol {p_.volume} dal "
                     f"{dt.datetime.fromtimestamp(p_.time):%Y-%m-%d %H:%M}")
        L.append("")

        post_rej = {k: v[1] for k, v in rej.items() if v[1]}
        pre_rej = sum(v[0] for v in rej.values())
        L.append(f"**Ordini non eseguiti** — pre-fix: {pre_rej} (storici, non azionabili) · "
                 f"post-fix: {sum(post_rej.values())}")
        if post_rej:
            for (s, c), n in sorted(post_rej.items()):
                L.append(f"- ⚠️ `{s}` × {n} — `{c}`")
        L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true", help="stampa senza scrivere il file")
    a = ap.parse_args()
    mt5 = _mt5()
    if mt5 is None:
        return 1
    try:
        txt = render(mt5)
    finally:
        mt5.shutdown()
    if a.stdout:
        print(txt)
        return 0
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{dt.date.today():%Y-%m-%d}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"scritto {os.path.relpath(path, ROOT)}")
    print("confronta col precedente per distinguere un problema NUOVO da un residuo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
