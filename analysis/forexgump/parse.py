"""Parser dei segnali di Forex Gump GOLD VIP (export Telegram HTML) -> CSV strutturato.

Fonte: export del canale in `materiale_socio/dati socio1/messages*.html` (09/09/2020 ->
28/09/2026), fornito dal socio il 2026-09-28. Fonte in `quarantena`.

Cosa estrae
-----------
Ogni messaggio che contiene un **bracket** su XAU: lato, entrata, TP, SL. Il formato cambia
nel tempo e il parser li copre tutti con una regola sola (lato -> prezzo -> TP -> SL):

    2020     "Xauusd sell 1928 tp 1918 sl 1940"              (SL a volte assente)
    2020-21  "XAUUSD buy stop Entry 1938.00 TP 1942.00"      (ordine PENDENTE, senza SL)
    2021+    "NEW SIGNAL XAUUSD sell 1796.05 TP 1786.00 SL 1798.00"
    2025+    "NUOVA INFORMAZIONE DIDATTICA Ho venduto XAU a 4373.80 TP 4363.80 SL 4376.80"

Le **categorie** (hedging, just for fun, appesantimento, last, didattica, bonus) sono solo
etichette: il parser non scarta nulla per categoria. Quale universo si misura lo decide la
pre-registrazione, non il parser — cosi' la scelta resta visibile e fatta prima degli esiti.

Cosa NON fa
-----------
- **Non tocca l'orario.** L'export etichetta *ogni* messaggio `UTC+01:00`, estate e inverno:
  e' un offset fisso dell'esportatore, non l'ora vera. `ts_export` resta com'e' scritto;
  l'allineamento al feed si fa **una volta sola**, nel loader, dopo averlo misurato sui
  prezzi (vedi [[feedback_una_correzione_un_proprietario]]).
- Non legge i messaggi di gestione (BE, "scarico", "TP RAGGIUNTO"): il copier esegue il
  bracket, e l'esito si risolve sul prezzo, non sulla dichiarazione del mentore.

Output: analysis/forexgump/signals.csv (dato derivato da chat privata: ignorato da git).
Uso:    python analysis/forexgump/parse.py
"""
from __future__ import annotations

import csv
import glob
import html
import os
import re
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT, "materiale_socio", "dati socio1")
OUT = os.path.join(os.path.dirname(__file__), "signals.csv")

MSG_SPLIT = re.compile(r'<div class="message ')
TS_RE = re.compile(r'title="(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2}) (UTC[+-]\d{2}:\d{2})"')
TEXT_RE = re.compile(r'<div class="text">(.*?)</div>', re.DOTALL)
ID_RE = re.compile(r'id="message(\d+)"')

PRICE = r"(\d{3,5}(?:\s?\.\s?\d+)?)"
# lato: inglese (buy/sell), italiano al passato (comprato/venduto) o "in long/short su"
SIDE = r"(buy|sell|comprato|venduto|in long|in short)"
# lato ... prezzo (con "stop"/"entry"/"a"/"su XAU a" in mezzo) ... TP prezzo ... [SL [on] prezzo]
BRACKET = re.compile(
    SIDE + r"(?P<stop>\s+stop)?[^\d]{0,40}?" + PRICE +
    r"[^\d]{0,15}?\btp\b[^\d]{0,5}" + PRICE +
    r"(?:[^\d]{0,15}?\bsl\b(?:\s*on)?[^\d]{0,5}" + PRICE + r")?",
    re.IGNORECASE)

# stessa cosa con lo SL scritto PRIMA del TP (3 messaggi del 24/01/2022)
BRACKET_SL_FIRST = re.compile(
    SIDE + r"(?P<stop>\s+stop)?[^\d]{0,40}?" + PRICE +
    r"[^\d]{0,15}?\bsl\b(?:\s*on)?[^\d]{0,5}" + PRICE +
    r"[^\d]{0,15}?\btp\b[^\d]{0,5}" + PRICE,
    re.IGNORECASE)

CATEGORIE = {
    "hedging": r"hedg",
    "just_for_fun": r"just for fun",
    "appesantimento": r"appesant",
    "last": r"\blast signal\b|\bultima informazione\b",
    "didattica": r"didattic",
    "bonus": r"\bbonus\b",
}
BUY_WORDS = ("buy", "comprato", "in long")


def _num(s: str | None) -> float | None:
    return float(re.sub(r"\s", "", s)) if s else None


def _clean(frag: str) -> str:
    t = frag.replace("<br>", " ").replace("<br/>", " ")
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return " ".join(t.split())


SCARTI: Counter = Counter()   # motivo -> quanti messaggi con XAU e TP non diventano bracket


def parse_text(txt: str) -> dict | None:
    """Ritorna il bracket del messaggio, o None se non contiene un segnale su XAU.

    I refusi del mentore (SL dalla parte sbagliata, TP oltre l'entrata, SL = entrata) **non
    si correggono**: un broker li rifiuterebbe, quindi il copier non li avrebbe eseguiti.
    Si contano in `SCARTI`, cosi' la differenza col conteggio della webapp resta spiegata.
    """
    if not re.search(r"xau", txt, re.IGNORECASE):
        return None
    has_tp = bool(re.search(r"\btp\b", txt, re.IGNORECASE))
    m = BRACKET.search(txt)
    if m:
        side_w, entry, tp, sl = m.group(1).lower(), _num(m.group(3)), _num(m.group(4)), _num(m.group(5))
    else:
        m = BRACKET_SL_FIRST.search(txt)
        if not m:
            if has_tp and re.search(r"\d{4}", txt):
                SCARTI["senza prezzo d'entrata (es. 'buy now TP X')"] += 1
            return None
        side_w, entry, sl, tp = m.group(1).lower(), _num(m.group(3)), _num(m.group(4)), _num(m.group(5))
    side = "buy" if side_w in BUY_WORDS else "sell"
    if (side == "buy" and tp <= entry) or (side == "sell" and tp >= entry):
        SCARTI["TP dalla parte sbagliata (refuso)"] += 1
        return None
    if sl is not None and ((side == "buy" and sl >= entry) or (side == "sell" and sl <= entry)):
        SCARTI["SL dalla parte sbagliata o uguale all'entrata"] += 1
        return None
    low = txt.lower()
    rec = {
        "side": side, "entry": entry, "tp": tp, "sl": sl,
        "order_type": "stop" if m.group("stop") else "market",
        "sl_missing": sl is None,
    }
    for k, pat in CATEGORIE.items():
        rec[k] = bool(re.search(pat, low))
    return rec


def main() -> None:
    files = glob.glob(os.path.join(SRC_DIR, "messages*.html"))
    rows, seen, n_msg = [], set(), 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            blocks = MSG_SPLIT.split(fh.read())[1:]
        for blk in blocks:
            ts, tx = TS_RE.search(blk), TEXT_RE.search(blk)
            if not (ts and tx):
                continue
            n_msg += 1
            txt = _clean(tx.group(1))
            rec = parse_text(txt)
            if rec is None:
                continue
            d, mo, y, h, mi, s, lab = ts.groups()
            mid = ID_RE.search(blk)
            key = mid.group(1) if mid else f"{y}{mo}{d}{h}{mi}{s}{txt[:40]}"
            if key in seen:            # un export ripetuto non deve contare doppio
                continue
            seen.add(key)
            rows.append({"msg_id": key, "ts_export": f"{y}-{mo}-{d}T{h}:{mi}:{s}",
                         "tz_label": lab, **rec, "src": os.path.basename(f), "text": txt[:300]})
    rows.sort(key=lambda r: r["ts_export"])
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"messaggi con testo: {n_msg}   bracket estratti: {len(rows)}   -> {OUT}")
    print("per anno:", dict(sorted(Counter(r["ts_export"][:4] for r in rows).items())))
    print("senza SL:", sum(r["sl_missing"] for r in rows),
          "  ordini stop (pendenti):", sum(r["order_type"] == "stop" for r in rows))
    for k in CATEGORIE:
        print(f"  {k:15s} {sum(r[k] for r in rows)}")
    print("messaggi con XAU e TP NON diventati bracket:", dict(SCARTI))
    dist_sl = Counter(round(abs(r["entry"] - r["sl"]), 0) for r in rows if r["sl"] is not None)
    dist_tp = Counter(round(abs(r["tp"] - r["entry"]), 0) for r in rows)
    print("distanza SL ($, arrotondata):", dict(dist_sl.most_common(6)))
    print("distanza TP ($, arrotondata):", dict(dist_tp.most_common(6)))


if __name__ == "__main__":
    main()
