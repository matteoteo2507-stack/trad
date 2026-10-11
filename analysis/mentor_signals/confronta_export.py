"""Confronto fra due export Telegram dello stesso canale, PRIMA di sostituire il vecchio col nuovo.

Regola (feedback "verifica i dati prima", 18/09): un export nuovo SOSTITUISCE il vecchio nella cartella
stabile, ma solo dopo aver dimostrato che ne e' un **sovrainsieme**. E il §6.1 della pre-registrazione OOS
del mentore chiede di **rimisurare a ogni export** il tasso di cancellazione (0,2% all'08/07→07/08).

Confronta per id del messaggio:
- id del vecchio ASSENTI nel nuovo, dentro la finestra comune  -> CANCELLATI dal canale;
- stesso id, testo diverso                                       -> MODIFICATI dopo la pubblicazione;
- stesso id, orario o etichetta di fuso diversi                  -> export fatto con un altro orologio:
  il loader (`backtest.TS_OFFSET_H`) andrebbe riverificato con `coverage.verifica()` prima di qualunque
  metrica;
- id nuovi con data DENTRO la finestra del vecchio               -> inseriti a posteriori (sospetti).

I cancellati e i modificati si salvano in `deleted_signals/` (jsonl), come il 07/07.
Dall'11/10 quei file restano fuori da git (testo e orari dei messaggi, repo pubblico): i conteggi stanno nei referti.

Uso: python analysis/mentor_signals/confronta_export.py <cartella_vecchia> <cartella_nuova> [--salva]
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MSG_SPLIT = re.compile(r'<div class="message ')
ID_RE = re.compile(r'id="message(-?\d+)"')
TS_RE = re.compile(r'title="(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2}) (UTC[+-]\d{2}:\d{2})"')
TEXT_RE = re.compile(r'<div class="text">(.*?)</div>', re.DOTALL)
SEGNALE = re.compile(r"\b(BUY|SELL)\b", re.IGNORECASE)


def _testo(frag: str) -> str:
    t = frag.replace("<br>", "\n").replace("<br/>", "\n")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def leggi(cartella: str) -> dict:
    """id -> {ts, tz, text}. Solo messaggi con data (i separatori di servizio non hanno id utile)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(cartella, "messages*.html"))):
        with open(f, encoding="utf-8") as fh:
            for blk in MSG_SPLIT.split(fh.read())[1:]:
                mid, ts = ID_RE.search(blk), TS_RE.search(blk)
                if not (mid and ts):
                    continue
                d, mo, y, h, mi, s, tz = ts.groups()
                tx = TEXT_RE.search(blk)
                out[int(mid.group(1))] = {"ts": f"{y}-{mo}-{d}T{h}:{mi}:{s}", "tz": tz,
                                          "text": _testo(tx.group(1)) if tx else ""}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vecchio")
    ap.add_argument("nuovo")
    ap.add_argument("--salva", action="store_true", help="scrive cancellati/modificati in deleted_signals/")
    a = ap.parse_args()
    V, N = leggi(a.vecchio), leggi(a.nuovo)
    if not V or not N:
        print("export vuoto o non leggibile"); return 2
    v_ts = sorted(m["ts"] for m in V.values())
    n_ts = sorted(m["ts"] for m in N.values())
    print(f"vecchio: {len(V):5d} messaggi  {v_ts[0]} -> {v_ts[-1]}  fusi {sorted({m['tz'] for m in V.values()})}")
    print(f"nuovo:   {len(N):5d} messaggi  {n_ts[0]} -> {n_ts[-1]}  fusi {sorted({m['tz'] for m in N.values()})}")

    inizio_n = n_ts[0]
    comuni = V.keys() & N.keys()
    cancellati = sorted(i for i in V.keys() - N.keys() if V[i]["ts"] >= inizio_n)
    fuori_finestra = sorted(i for i in V.keys() - N.keys() if V[i]["ts"] < inizio_n)
    modificati = sorted(i for i in comuni if V[i]["text"] != N[i]["text"])
    orario_diverso = sorted(i for i in comuni if (V[i]["ts"], V[i]["tz"]) != (N[i]["ts"], N[i]["tz"]))
    inseriti = sorted(i for i in N.keys() - V.keys() if N[i]["ts"] <= v_ts[-1])
    nuovi = sorted(i for i in N.keys() - V.keys() if N[i]["ts"] > v_ts[-1])

    def segn(ids, src):
        return sum(bool(SEGNALE.search(src[i]["text"])) for i in ids)

    print(f"\nin comune: {len(comuni)}   nuovi dopo la fine del vecchio: {len(nuovi)}")
    print(f"CANCELLATI dal canale (nella finestra comune): {len(cancellati)} "
          f"({len(cancellati) / max(1, len(V)):.2%} del vecchio), di cui con BUY/SELL: {segn(cancellati, V)}")
    print(f"MODIFICATI dopo la pubblicazione: {len(modificati)}, di cui con BUY/SELL: {segn(modificati, V)}")
    print(f"ORARIO o FUSO diverso sullo stesso id: {len(orario_diverso)}")
    print(f"INSERITI a posteriori (nuovi id dentro la finestra vecchia): {len(inseriti)}")
    print(f"vecchi prima dell'inizio del nuovo (export piu' corto, NON cancellati): {len(fuori_finestra)}")
    for nome, ids, src in (("cancellato", cancellati, V), ("modificato", modificati, V),
                           ("orario diverso", orario_diverso, V), ("inserito", inseriti, N)):
        for i in ids[:5]:
            extra = f"  ->  {N[i]['ts']} {N[i]['tz']}" if nome == "orario diverso" else ""
            print(f"  [{nome}] id {i} {src[i]['ts']} {src[i]['tz']}{extra} | {src[i]['text'][:90]!r}")

    sovrainsieme = not cancellati and not fuori_finestra
    print("\nIl nuovo e' un SOVRAINSIEME del vecchio (testo):", "SI" if sovrainsieme else "NO")
    if orario_diverso:
        print("⚠️ orari diversi: riverificare il fuso con coverage.verifica() PRIMA di qualunque metrica")

    if a.salva and (cancellati or modificati):
        os.makedirs(os.path.join(HERE, "deleted_signals"), exist_ok=True)
        dest = os.path.join(HERE, "deleted_signals", f"export_{n_ts[-1][:10]}.jsonl")
        with open(dest, "w", encoding="utf-8") as fh:
            for i in cancellati:
                fh.write(json.dumps({**V[i], "id": i, "note": "presente nel vecchio export, ASSENTE nel nuovo -> cancellato"},
                                    ensure_ascii=False) + "\n")
            for i in modificati:
                fh.write(json.dumps({**V[i], "id": i, "text_nuovo": N[i]["text"], "note": "testo modificato fra i due export"},
                                    ensure_ascii=False) + "\n")
        print("salvato:", dest)
    return 0 if sovrainsieme else 1


if __name__ == "__main__":
    sys.exit(main())
