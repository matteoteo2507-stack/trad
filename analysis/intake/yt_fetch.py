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

CONTROLLO DI COMPLETEZZA (dal 2026-10-25). Il 09/10 i sottotitoli manuali di un video erano
tronchi (138 parole su 11 minuti) e lo script li aveva presi in silenzio, perche' YouTube da'
prima la traccia manuale. Ora, dopo il fetch, si misurano le parole al minuto contro la durata
del video: sotto SOGLIA_PAROLE_MIN si riprova con l'altra traccia (manuale <-> generata) e si
tiene la piu' lunga; se resta sotto, il file si scrive lo stesso ma con "completezza: SOTTO
SOGLIA" nell'intestazione, in _state.json e a schermo. Durata ignota: si segnala, non si blocca.

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
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(ROOT, "fondamenti_tecnici", "_sorgenti", "insight_da_yt", "_raw")
STATE = os.path.join(HERE, "_state.json")

DELAY_DEFAULT = 90          # secondi fra una trascrizione e l'altra (prudente: la soglia di YouTube non e' nota)
BACKOFF = [300, 900, 1800, 3600, 3600]  # 5, 15, 30, 60, 60 min: ~2,7 ore di pazienza totale

LINGUE = ["en", "en-US", "en-GB"]

# Soglia di completezza, in parole al minuto di video.
# Il parlato normale sta fra 130 e 160 parole/min. La soglia NON e' quel valore: la durata conta
# anche intro, musica, grafici mostrati in silenzio e pause, e chi parla piano scende verso 110.
# 90 e' circa il 70% del minimo del parlato normale: lascia un terzo del video senza voce prima di
# dare un falso allarme, e a ritmo normale scatta quando manca piu' di un terzo del testo.
# L'errore piu' caro e' il falso negativo (leggere una trascrizione tronca credendola intera),
# mentre un falso allarme costa una richiesta in piu' e una riga d'avviso: per questo la soglia sta
# piu' in alto di quanto basterebbe per il caso del 09/10 (12,5 parole/min, sette volte sotto).
# Un video con poco parlato vero resta sotto soglia con entrambe le tracce: lo si capisce aprendolo.
SOGLIA_PAROLE_MIN = 90

OK = "ok"
SOTTO = "SOTTO SOGLIA"
IGNOTA = "durata ignota"


@dataclass
class Trascrizione:
    """Testo scaricato e misura della sua completezza.

    Attributes:
        text: testo della traccia, su una riga.
        traccia: "manuale" o "generata".
        lingua: codice della lingua della traccia (es. "en").
        parole: numero di parole del testo.
        parole_min: parole al minuto di video; None se la durata e' ignota.
        completezza: OK, SOTTO o IGNOTA.
        provate: tracce scaricate, nell'ordine (es. ["manuale", "generata"]).
    """

    text: str
    traccia: str
    lingua: str
    parole: int
    parole_min: float | None
    completezza: str
    provate: list[str] = field(default_factory=list)


def words_per_minute(n_words: int, duration_s: float | None) -> float | None:
    """Parole al minuto di video; None se la durata manca o non e' positiva."""
    if not duration_s or duration_s <= 0:
        return None
    return n_words / (duration_s / 60)


def completeness(wpm: float | None) -> str:
    """Classifica le parole al minuto: OK, SOTTO (sotto SOGLIA_PAROLE_MIN) o IGNOTA."""
    if wpm is None:
        return IGNOTA
    return SOTTO if wpm < SOGLIA_PAROLE_MIN else OK


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _write_atomic(path: str, content: str) -> None:
    """Scrive su un file temporaneo e poi lo sostituisce: un errore non lascia il file vuoto."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)


def save_state(st):
    # Prima si serializza, poi si scrive: json.dump direttamente sul file lo svuoterebbe se
    # fallisse a meta' (memoria feedback_scrittura_file_condivisi).
    content = json.dumps(st, indent=2, ensure_ascii=False)
    _write_atomic(STATE, content)


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


def _download(transcript: Any, duration_s: float | None) -> Trascrizione:
    """Scarica UNA traccia (una richiesta a YouTube) e ne misura la completezza."""
    text = " ".join(seg.text.replace("\n", " ") for seg in transcript.fetch())
    n = len(text.split())
    wpm = words_per_minute(n, duration_s)
    return Trascrizione(text=text, traccia="generata" if transcript.is_generated else "manuale",
                        lingua=transcript.language_code, parole=n, parole_min=wpm,
                        completezza=completeness(wpm))


def fetch_transcript(vid: str, duration_s: float | None = None, api: Any = None) -> Trascrizione:
    """Scarica la trascrizione inglese di un video e ne controlla la completezza.

    Prima scelta come prima del 25/10: la traccia manuale se c'e', altrimenti la generata (e' la
    regola di `find_transcript`). Se le parole al minuto stanno sotto SOGLIA_PAROLE_MIN si scarica
    anche l'altra traccia e si tiene quella con piu' parole. Nel caso normale le richieste sono le
    stesse di prima; la seconda traccia costa una richiesta in piu' solo sotto soglia.

    Args:
        vid: id del video.
        duration_s: durata in secondi dai metadati; None o 0 = ignota (si segnala, non si blocca).
        api: istanza di YouTubeTranscriptApi; nei test un oggetto finto con lo stesso `list()`.

    Returns:
        La Trascrizione tenuta, con `provate` = tracce scaricate.
    """
    from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi
    api = api or YouTubeTranscriptApi()
    tlist = api.list(vid)
    best = _download(tlist.find_transcript(LINGUE), duration_s)
    provate = [best.traccia]
    if best.completezza == SOTTO:
        find_other = (tlist.find_manually_created_transcript if best.traccia == "generata"
                      else tlist.find_generated_transcript)
        try:
            other = find_other(LINGUE)
        except NoTranscriptFound:
            other = None
        if other is not None:
            alt = _download(other, duration_s)
            provate.append(alt.traccia)
            if alt.parole > best.parole:
                best = alt
    best.provate = provate
    return best


def completeness_line(tr: Trascrizione) -> str:
    """Riga `- completezza: ...` dell'intestazione del file grezzo."""
    if tr.completezza == SOTTO:
        return (f"- completezza: SOTTO SOGLIA ({tr.parole_min:.1f} parole/min) - soglia "
                f"{SOGLIA_PAROLE_MIN}, provate: {', '.join(tr.provate)}")
    if tr.completezza == IGNOTA:
        return "- completezza: durata ignota, parole al minuto non verificabili"
    return f"- completezza: ok (soglia {SOGLIA_PAROLE_MIN} parole/min)"


def raw_header(meta: dict, channel: str, tr: Trascrizione) -> str:
    """Intestazione del file grezzo. Resta sotto i 700 caratteri che `rule_extract.body()` salta."""
    dur = meta.get("duration") or 0
    wpm = "durata ignota" if tr.parole_min is None else f"{tr.parole_min:.1f}"
    return (
        f"# {meta['title']}\n\n"
        f"- canale: {channel}\n"
        f"- video: https://www.youtube.com/watch?v={meta['id']}\n"
        f"- durata: {f'{dur // 60} min' if dur > 0 else 'ignota'}\n"
        f"- scaricato: {datetime.now(timezone.utc).date()} (non rivista)\n"
        f"- traccia: {tr.traccia} ({tr.lingua})\n"
        f"- parole: {tr.parole} (al minuto: {wpm})\n"
        f"{completeness_line(tr)}\n\n"
        f"> Trascrizione GREZZA. Non e' una sintesi: la sintesi di terzi e' stata eliminata\n"
        f"> di proposito perche' comprime via i dettagli meccanici delle regole.\n\n---\n\n"
    )


def write_raw(meta: dict, channel: str, tr: Trascrizione) -> tuple[str, str]:
    """Scrive la trascrizione grezza in RAW; ritorna (percorso, nome del file)."""
    os.makedirs(RAW, exist_ok=True)
    name = f"{slug(meta['title'])}__{meta['id']}.md"
    path = os.path.join(RAW, name)
    content = raw_header(meta, channel, tr) + tr.text + "\n"
    _write_atomic(path, content)
    return path, name


def state_entry(meta: dict, name: str, tr: Trascrizione) -> dict:
    """Voce di _state.json per un video scaricato."""
    return {"title": meta["title"], "file": name, "words": tr.parole,
            "traccia": tr.traccia,
            "parole_min": None if tr.parole_min is None else round(tr.parole_min, 1),
            "completezza": tr.completezza,
            "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def outcome_label(tr: Trascrizione) -> str:
    """Etichetta a schermo: OK, o l'avviso di completezza."""
    if tr.completezza == SOTTO:
        return f"SOTTO SOGLIA ({tr.parole_min:.1f} parole/min, provate: {', '.join(tr.provate)})"
    if tr.completezza == IGNOTA:
        return "OK (durata ignota)"
    return f"OK ({tr.parole_min:.0f} parole/min)"


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
            prev = seen.get(v["id"])
            mark = "   " if prev is None else ("!! " if prev.get("completezza") == SOTTO else "ok ")
            print(f"  {mark}{v['id']}  {v['duration'] // 60:>3}m  {v['title'][:70]}")
        return

    eta = len(todo) * a.delay / 60
    print(f"attesa fra richieste: {a.delay:.0f}s  ->  ETA ~{eta:.0f} min. Ctrl-C e' sicuro (stato salvato).\n")

    done = fail = 0
    strikes = 0
    sotto = []
    for i, v in enumerate(todo, 1):
        try:
            tr = fetch_transcript(v["id"], v.get("duration"))
            path, name = write_raw(v, channel, tr)
            seen[v["id"]] = state_entry(v, name, tr)
            save_state(st)
            done += 1
            strikes = 0
            if tr.completezza == SOTTO:
                sotto.append(name)
            print(f"[{i}/{len(todo)}] {tr.parole:6} parole  {outcome_label(tr)}  {v['title'][:56]}",
                  flush=True)
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
    if sotto:
        print(f"\nATTENZIONE: {len(sotto)} trascrizioni SOTTO SOGLIA ({SOGLIA_PAROLE_MIN} parole/min), "
              f"forse tronche: confrontarle col video prima di leggerle come intere.")
        for n in sotto:
            print(f"  !! {n}")
    print("prossimo passo: python analysis/intake/rule_extract.py --all")


if __name__ == "__main__":
    main()
