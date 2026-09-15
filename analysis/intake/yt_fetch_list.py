"""Scarica le trascrizioni da una LISTA di video, in ordine di priorita'.

Nato il 2026-09-15 per il distillamento Quant Guild. Differenze da `yt_fetch.py`:

- legge una lista `id|num|minuti|titolo` (righe che iniziano con # = commenti/blocchi) invece di
  elencare un canale, quindi l'ordine di scaricamento e' quello di lettura;
- NON fa richieste di metadati per video: una sola richiesta a YouTube per trascrizione, meta'
  del rischio di blocco IP rispetto a lanciare `yt_fetch.py` su ogni URL;
- scrive lo stato sotto una chiave ESPLICITA (`--canale`). Serve perche' `yt_fetch.py` lanciato
  su un singolo video salva sotto il nome dell'uploader ("Roman Paolucci"), mentre il giro sul
  canale usa "Roman Paolucci - Videos": con chiavi diverse il giro sul canale riscaricherebbe tutto;
- produce una COPIA DI LETTURA a righe corte in `_raw/_lettura/`. Le trascrizioni grezze sono su
  una riga sola da decine di migliaia di caratteri: il Read le tronca e l'output di una shell si
  ferma a 30.000 caratteri, cioe' si perdono pezzi senza accorgersene. La grezza resta intatta.

Uso:
  python analysis/intake/yt_fetch_list.py analysis/intake/lists/quantguild_gruppo1.txt
  python analysis/intake/yt_fetch_list.py <lista> --solo-lettura   # rigenera solo le copie di lettura

Prima di lanciarlo controllare che non ne giri gia' uno: due fetch insieme raddoppiano il ritmo
delle richieste. Tell: l'ultimo `fetched` in `_state.json` sotto la chiave del canale e' di pochi
minuti fa.
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import textwrap
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yt_fetch as yf  # noqa: E402

LETTURA = os.path.join(yf.RAW, "_lettura")
CANALE_DEFAULT = "Roman Paolucci - Videos"


def leggi_lista(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            vid, num, minuti, titolo = ln.split("|", 3)
            out.append({"id": vid, "num": num, "title": titolo,
                        "duration": int(float(minuti or 0) * 60)})
    return out


def copia_lettura(nome_file):
    """Copia a righe da 160 caratteri, spezzate agli spazi. Contenuto identico alla grezza."""
    src = os.path.join(yf.RAW, nome_file)
    if not os.path.exists(src):
        return None
    os.makedirs(LETTURA, exist_ok=True)
    with open(src, encoding="utf-8") as f:
        testo = f.read()
    righe = []
    for par in testo.split("\n"):
        righe.extend(textwrap.wrap(par, width=160, break_long_words=False,
                                   break_on_hyphens=False) or [""])
    dst = os.path.join(LETTURA, nome_file)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    return dst


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("lista")
    ap.add_argument("--canale", default=CANALE_DEFAULT, help="chiave di stato in _state.json")
    ap.add_argument("--delay", type=float, default=yf.DELAY_DEFAULT)
    ap.add_argument("--solo-lettura", action="store_true",
                    help="non scarica: rigenera le copie di lettura dei video gia' presi")
    a = ap.parse_args()

    lista = leggi_lista(a.lista)
    st = yf.load_state()
    seen = st.setdefault(a.canale, {})

    if a.solo_lettura:
        n = sum(1 for v in lista if v["id"] in seen and copia_lettura(seen[v["id"]]["file"]))
        print(f"copie di lettura rigenerate: {n}/{len(lista)} in {os.path.relpath(LETTURA, yf.ROOT)}")
        return

    todo = [v for v in lista if v["id"] not in seen]
    print(f"lista: {len(lista)}  gia' presi: {len(lista) - len(todo)}  da fare: {len(todo)}"
          f"  ETA ~{len(todo) * a.delay / 60:.0f} min", flush=True)

    strikes, i = 0, 0
    while i < len(todo):
        v = todo[i]
        try:
            txt = yf.fetch_transcript(v["id"])
            _, name = yf.write_raw(v, a.canale, txt)
            seen[v["id"]] = {"title": v["title"], "file": name, "words": len(txt.split()),
                             "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            yf.save_state(st)
            copia_lettura(name)
            strikes = 0
            print(f"[{i + 1}/{len(todo)}] OK  #{v['num']:>3} {len(txt.split()):6} parole  "
                  f"{v['title'][:60]}", flush=True)
            i += 1
        except KeyboardInterrupt:
            print("\ninterrotto: stato salvato, rilancia per riprendere.")
            break
        except Exception as ex:
            n = type(ex).__name__
            blocked = n in ("IpBlocked", "RequestBlocked") or "429" in str(ex)
            if blocked and strikes < len(yf.BACKOFF):
                w = yf.BACKOFF[strikes]
                strikes += 1
                print(f"[{i + 1}/{len(todo)}] BLOCCO IP -> attendo {w // 60} min "
                      f"(tentativo {strikes}/{len(yf.BACKOFF)})", flush=True)
                time.sleep(w)
                continue
            if blocked:
                print("BLOCCO IP persistente: stato salvato, riprendere piu' tardi.", flush=True)
                break
            print(f"[{i + 1}/{len(todo)}] FAIL #{v['num']} {n}: {str(ex)[:90]}", flush=True)
            i += 1
        time.sleep(a.delay * random.uniform(0.8, 1.2))

    yf.save_state(st)
    print("fine lista.", flush=True)


if __name__ == "__main__":
    main()
