"""Intake YouTube — scarica SOLO le trascrizioni (mai i video) di un canale.

Sostituisce il ciclo manuale: aprire il canale, scegliere, copiare il link, passare da NoteGPT,
incollare in un file. Il passaggio di sintesi di terzi viene ELIMINATO, non automatizzato: un
riassuntore generico conserva i claim d'effetto e comprime via i dettagli meccanici della regola,
che sono l'unica cosa che ci serve (vedi _INTAKE.md, "si raccolgono le regole, si scartano le
statistiche dichiarate").

NESSUN MEDIA VIENE SCARICATO. Solo la traccia sottotitoli: ~82 KB di testo per video contro
~2 GB di video, misurato. yt-dlp e' usato in modalita' extract_flat (soli metadati).

VINCOLO REALE: YouTube blocca l'IP dopo poche richieste ravvicinate (IpBlocked / HTTP 429).
Verificato il 2026-08-17: ~15 richieste di fila sono bastate. Percio' questo script e'
volutamente LENTO e RIPRENDIBILE - stato su disco, backoff esponenziale, si puo' interrompere
e rilanciare senza perdere lavoro.

Uso:
  python analysis/intake/yt_fetch.py https://www.youtube.com/@chart-fanatics/videos
  python analysis/intake/yt_fetch.py <url> --limit 5 --delay 60
  python analysis/intake/yt_fetch.py --list-only <url>
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(ROOT, "fondamenti_tecnici", "_sorgenti", "insight_da_yt", "_raw")
STATE = os.path.join(HERE, "_state.json")

DELAY_DEFAULT = 90          # secondi fra una trascrizione e l'altra (prudente: la soglia di YouTube non e' nota)
BACKOFF = [300, 900, 1800, 3600, 3600]  # 5, 15, 30, 60, 60 min: ~2,7 ore di pazienza totale


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)


def slug(s, n=60):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    return re.sub(r"[-\s]+", "-", s).strip("-")[:n] or "senza-titolo"


def is_single_video(url):
    return bool(re.search(r"(watch\?v=|youtu\.be/|/shorts/)", url))


def list_channel(url, limit=None):
    """Accetta un canale/playlist OPPURE un singolo video.

    Il flusso normale e' UN VIDEO ALLA VOLTA: una trascrizione sta in ~13.500 parole e si
    legge INTERA, senza comprimere nulla, quindi non si perde alcun insight. La compressione
    serviva solo per leggere 45 video insieme (608.000 parole) - un problema che con questo
    flusso non esiste. Lo scaricamento in blocco resta possibile perche' copiare testo non
    seleziona e non interpreta: il rischio di qualita' sta tutto nella lettura, non nel fetch.
    """
    import yt_dlp
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
    if limit:
        opts["playlistend"] = limit
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(url, download=False)

    if is_single_video(url) or not info.get("entries"):
        vid = {"id": info.get("id"), "title": info.get("title") or "",
               "duration": info.get("duration") or 0}
        chan = info.get("uploader") or info.get("channel") or "singolo-video"
        return chan, ([vid] if vid["id"] else [])

    out = []
    for e in info.get("entries", []) or []:
        if e and e.get("id"):
            out.append({"id": e["id"], "title": e.get("title") or "",
                        "duration": e.get("duration") or 0})
    return info.get("title") or url, out


def fetch_transcript(vid):
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    tr = api.fetch(vid, languages=["en", "en-US", "en-GB"])
    return " ".join(seg.text.replace("\n", " ") for seg in tr)


def write_raw(meta, channel, text):
    os.makedirs(RAW, exist_ok=True)
    name = f"{slug(meta['title'])}__{meta['id']}.md"
    path = os.path.join(RAW, name)
    head = (
        f"# {meta['title']}\n\n"
        f"- canale: {channel}\n"
        f"- video: https://www.youtube.com/watch?v={meta['id']}\n"
        f"- durata: {meta['duration'] // 60} min\n"
        f"- scaricato: {datetime.now(timezone.utc).date()} (trascrizione automatica, non rivista)\n"
        f"- parole: {len(text.split())}\n\n"
        f"> Trascrizione GREZZA. Non e' una sintesi: la sintesi di terzi e' stata eliminata\n"
        f"> di proposito perche' comprime via i dettagli meccanici delle regole.\n\n---\n\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + text + "\n")
    return path, name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--limit", type=int, default=None, help="quanti video considerare")
    ap.add_argument("--delay", type=float, default=DELAY_DEFAULT, help="secondi fra le richieste")
    ap.add_argument("--all", action="store_true", help="riscarica anche quelli gia' presi")
    ap.add_argument("--list-only", action="store_true", help="elenca soltanto, non scarica")
    a = ap.parse_args()

    channel, vids = list_channel(a.url, a.limit)
    st = load_state()
    seen = st.setdefault(channel, {})
    todo = [v for v in vids if a.all or v["id"] not in seen]

    print(f"canale: {channel}")
    print(f"video elencati: {len(vids)}   gia' scaricati: {len(vids) - len(todo)}   da fare: {len(todo)}")
    tot_min = sum(v["duration"] for v in vids) / 60
    print(f"durata totale: {tot_min / 60:.1f} h   stima testo: ~{len(vids) * 82 / 1024:.1f} MB (nessun video)")
    if a.list_only or not todo:
        for v in vids[:30]:
            mark = "ok " if v["id"] in seen else "   "
            print(f"  {mark}{v['id']}  {v['duration'] // 60:>3}m  {v['title'][:70]}")
        return

    eta = len(todo) * a.delay / 60
    print(f"attesa fra richieste: {a.delay:.0f}s  ->  ETA ~{eta:.0f} min. Ctrl-C e' sicuro (stato salvato).\n")

    done = fail = 0
    strikes = 0
    for i, v in enumerate(todo, 1):
        try:
            txt = fetch_transcript(v["id"])
            path, name = write_raw(v, channel, txt)
            seen[v["id"]] = {"title": v["title"], "file": name, "words": len(txt.split()),
                             "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            save_state(st)
            done += 1
            strikes = 0
            print(f"[{i}/{len(todo)}] OK   {len(txt.split()):6} parole  {v['title'][:56]}", flush=True)
        except KeyboardInterrupt:
            print("\ninterrotto: stato salvato, rilancia per riprendere.")
            break
        except Exception as ex:
            name_ex = type(ex).__name__
            blocked = name_ex in ("IpBlocked", "RequestBlocked") or "429" in str(ex)
            if blocked and strikes < len(BACKOFF):
                w = BACKOFF[strikes]
                strikes += 1
                print(f"[{i}/{len(todo)}] BLOCCO IP -> attendo {w // 60} min e riprovo "
                      f"(tentativo {strikes}/{len(BACKOFF)})", flush=True)
                try:
                    time.sleep(w)
                except KeyboardInterrupt:
                    print("\ninterrotto durante l'attesa: stato salvato."); break
                todo.append(v)          # rimesso in coda
                continue
            if blocked:
                print(f"\nBLOCCO IP persistente dopo {len(BACKOFF)} tentativi. Stato salvato: "
                      f"riprova fra qualche ora o da un'altra rete.")
                break
            fail += 1
            print(f"[{i}/{len(todo)}] FAIL {name_ex}: {str(ex)[:90]}", flush=True)
        time.sleep(a.delay * random.uniform(0.8, 1.2))

    save_state(st)
    print(f"\nfatti {done}, falliti {fail}. Trascrizioni in {os.path.relpath(RAW, ROOT)}")
    print("prossimo passo: python analysis/intake/rule_extract.py --all")


if __name__ == "__main__":
    main()
