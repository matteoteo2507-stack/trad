"""Parser dei segnali del mentore (export Telegram HTML) -> CSV strutturato.

Estrae da 'Dati su segnali mentore/messages*.html' i segnali XAUUSD, gestendo l'evoluzione
del formato:
  - recente (strutturato): "XAUUSD BUY/SELL ... Entry: X ... TP1: .. TP2: .. TP3: .. Stop Loss: Y"
  - vecchio: "BUY/SELL NOW", "BUY/SELL ZONE ON X", "TP 1 ... ON Z" (spesso SENZA SL)
Le righe di ESITO ("TP1 HIT", "Running loss", "Sl hit") NON sono nuovi segnali -> scartate.

Output: analysis/mentor_signals/signals.csv (ts, side, entry, tp1, tp2, tp3, sl, complete, src).
Uso: python analysis/mentor_signals/parse.py
"""
from __future__ import annotations

import csv
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT, "Dati su segnali mentore")
OUT = os.path.join(os.path.dirname(__file__), "signals.csv")

TS_RE = re.compile(r'title="(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})')
MSG_SPLIT = re.compile(r'<div class="message ')
TEXT_RE = re.compile(r'<div class="text">(.*?)</div>', re.DOTALL)
NUM = r'(\d{3,5}(?:\.\d+)?)'


def _clean(html: str) -> str:
    t = html.replace("<br>", "\n").replace("<br/>", "\n")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[ \t]+", " ", t).strip()


def _iso(m) -> str:
    d, mo, y, h, mi, s = m.groups()
    return f"{y}-{mo}-{d}T{h}:{mi}:{s}"


def parse_text(txt: str):
    """Ritorna dict segnale o None se non e' un nuovo segnale."""
    up = txt.upper()
    # scarta esiti/commenti
    if any(k in up for k in ("TP1 HIT", "TP 1 HIT", "TP2 HIT", "TP3 HIT", "HIT",
                             "RUNNING LOSS", "SL HIT", "PROFIT DONE", "PIPS PROFIT")):
        # ma se contiene anche un Entry esplicito lo teniamo (raro) -> altrimenti scarta
        if "ENTRY" not in up and "ZONE ON" not in up:
            return None
    side = None
    if re.search(r"\bBUY\b", up):
        side = "BUY"
    elif re.search(r"\bSELL\b", up):
        side = "SELL"
    if side is None:
        return None

    entry = None
    m = re.search(r"ENTRY[:\s]*" + NUM, up)
    if m:
        entry = float(m.group(1))
    else:
        m = re.search(r"ZONE\s*ON\s*" + NUM, up)
        if m:
            entry = float(m.group(1))
        else:
            m = re.search(r"\b(?:BUY|SELL)\s*(?:NOW\s*)?(?:@|AT)?\s*" + NUM, up)
            if m:
                entry = float(m.group(1))
    if entry is None:
        return None

    def find(*pats):
        for p in pats:
            mm = re.search(p, up)
            if mm:
                return float(mm.group(1))
        return None

    tp1 = find(r"TP\s*1[:\s]*" + NUM, r"TP1[:\s]*" + NUM, r"TP\s*1\s*(?:TAKE\s*PROFIT)?\s*ON\s*" + NUM)
    tp2 = find(r"TP\s*2[:\s]*" + NUM, r"TP2[:\s]*" + NUM, r"TP\s*2\s*(?:TAKE\s*PROFIT)?\s*ON\s*" + NUM)
    tp3 = find(r"TP\s*3[:\s]*" + NUM, r"TP3[:\s]*" + NUM, r"TP\s*3\s*(?:TAKE\s*PROFIT)?\s*ON\s*" + NUM)
    sl = find(r"STOP\s*LOSS[:\s]*" + NUM, r"\bSL[:\s]*" + NUM)

    return {"side": side, "entry": entry, "tp1": tp1, "tp2": tp2, "tp3": tp3, "sl": sl}


def main():
    rows = []
    for fn in ("messages.html", "messages2.html", "messages3.html"):
        path = os.path.join(SRC_DIR, fn)
        if not os.path.exists(path):
            print(f"[skip] {fn} mancante"); continue
        html = open(path, encoding="utf-8").read()
        blocks = MSG_SPLIT.split(html)
        last_ts = None
        for b in blocks:
            mts = TS_RE.search(b)
            if mts:
                last_ts = _iso(mts)
            mtx = TEXT_RE.search(b)
            if not mtx:
                continue
            txt = _clean(mtx.group(1))
            if not txt:
                continue
            sig = parse_text(txt)
            if sig is None:
                continue
            sig["ts"] = last_ts
            sig["src"] = fn
            sig["complete"] = sig["sl"] is not None and sig["tp1"] is not None
            rows.append(sig)

    rows = [r for r in rows if r["ts"]]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "side", "entry", "tp1", "tp2", "tp3", "sl",
                                          "complete", "src"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # sommario
    n = len(rows)
    comp = [r for r in rows if r["complete"]]
    buys = sum(1 for r in rows if r["side"] == "BUY")
    entries = [r["entry"] for r in rows if r["entry"]]
    print(f"Segnali estratti: {n}  (completi con SL+TP: {len(comp)})")
    if rows:
        print(f"  BUY={buys}  SELL={n-buys}")
        print(f"  range date: {min(r['ts'] for r in rows)} -> {max(r['ts'] for r in rows)}")
        print(f"  entry range: {min(entries):.0f} .. {max(entries):.0f}")
        per_src = {}
        for r in rows:
            per_src.setdefault(r["src"], [0, 0])
            per_src[r["src"]][0] += 1
            per_src[r["src"]][1] += 1 if r["complete"] else 0
        for s, (tot, c) in per_src.items():
            print(f"  {s}: {tot} segnali ({c} completi)")
        print("\n  primi 3 completi:")
        for r in comp[:3]:
            print(f"   {r['ts']} {r['side']} entry={r['entry']} tp1={r['tp1']} sl={r['sl']}")
        print("  ultimi 3 completi:")
        for r in comp[-3:]:
            print(f"   {r['ts']} {r['side']} entry={r['entry']} tp1={r['tp1']} sl={r['sl']}")
    print(f"\nCSV: {OUT}")


if __name__ == "__main__":
    main()
