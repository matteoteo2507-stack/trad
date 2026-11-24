"""Notifiche Telegram delle ricerche. Si accendono solo quando lo decide l'utente, una ricerca alla volta.

py -3.13 telegram.py collega <TOKEN>     collega il bot (prima scrivigli /start su Telegram)
py -3.13 telegram.py prova                manda un messaggio di prova
py -3.13 telegram.py attiva ricerca500    accende le notifiche per quella ricerca (gira in background)
py -3.13 telegram.py disattiva ricerca500 le spegne
py -3.13 telegram.py stato                quali notifiche sono accese

Messaggi: avvio, ogni 25% di avanzamento, fine di ogni fase con il riassunto, ricerca ferma da troppo, disco quasi pieno."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent
ROOT = QUI.parent
CONFIG = QUI / "config.json"
ATTIVE = QUI / "attive"
CONTROLLO_OGNI = 120        # secondi tra un controllo e l'altro
FERMA_DOPO = 45 * 60        # avviso se nessun lavoro finisce per tanto tempo


# ---------- Telegram ----------
def _cfg() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def _api(metodo: str, **param) -> dict:
    tok = _cfg().get("token") or param.pop("_token")
    url = f"https://api.telegram.org/bot{tok}/{metodo}"
    dati = urllib.parse.urlencode(param).encode() if param else None
    with urllib.request.urlopen(url, data=dati, timeout=30) as r:
        return json.loads(r.read().decode())


def manda(testo: str) -> bool:
    c = _cfg()
    if not c.get("chat_id"):
        print("bot non collegato: usa 'collega <TOKEN>'")
        return False
    for _ in range(3):
        try:
            _api("sendMessage", chat_id=c["chat_id"], text=testo, parse_mode="HTML", disable_web_page_preview="true")
            return True
        except Exception as e:  # rete assente: riprova
            print("invio fallito:", e)
            time.sleep(20)
    return False


def collega(token: str):
    r = _api("getUpdates", _token=token)
    chat = next((u["message"]["chat"] for u in reversed(r.get("result", [])) if "message" in u), None)
    if chat is None:
        raise SystemExit("Nessun messaggio trovato: apri il bot su Telegram, premi Avvia (/start) e rilancia.")
    CONFIG.write_text(json.dumps({"token": token, "chat_id": chat["id"]}, indent=1), encoding="utf-8")
    manda("✅ Bot collegato. Le notifiche delle ricerche arrivano qui solo quando le accendi.")
    print("collegato alla chat", chat.get("first_name") or chat.get("title"), chat["id"])


# ---------- ricerche che si possono seguire ----------
def _ricerca500() -> dict:
    """Avanzamento della RICERCA 500 (stessi conti di stato_500.py)."""
    sys.path.insert(0, str(ROOT))
    import stato_500 as S
    out = S.OUT
    f = out / "ordine_pine.json"
    ordine = json.loads(f.read_text()) if f.exists() else []
    lav = [(p, a) for p in ordine[:] for a in S.ASSET]
    tempi, fatti = [], 0
    for p, a in lav:
        s, t = S.stato(S.DEEP / f"{p}_{a}")
        if s:
            fatti += 1
            tempi.append(t)
    log = out / "log_ricerca.txt"
    finito = log.exists() and "FINITO" in log.read_text(encoding="utf-8", errors="ignore")[-2000:]
    return dict(
        nome="RICERCA 500", fatti=fatti, totale=len(lav), ultimo=max(tempi) if tempi else time.time(),
        fasi=[("giro1", "Giro 1 finito (25 strategie migliori)", out / "fase2_portafogli_giro1.csv"),
              ("giro2", "Giro 2 finito: risultati FINALI", out / "fase2_portafogli_giro2.csv")],
        finito=finito)


def _riassunto_portafogli(csv: Path) -> str:
    import pandas as pd
    try:
        d = pd.read_csv(csv)
        d = d[d.get("e_il_rischio_scelto", True) == True]  # noqa: E712
        m = [c for c in d.columns if c.startswith("mc_") and any(k in c for k in ("p500", "pbruc", "gg500"))][:3]
        righe = []
        for _, r in d.iterrows():
            extra = "  ".join(f"{c[3:]} {r[c]:.0%}" if "gg" not in c else f"{c[3:]} {r[c]:.0f}gg" for c in m
                              if pd.notna(r[c]))
            righe.append(f"• <b>{r['portafoglio']}</b> ({r['periodo']}): {int(r['n_strategie'])} strategie, "
                         f"rischio {r['f_scelto']:.0%}  {extra}")
        return "\n".join(righe[:12])
    except Exception as e:
        return f"(riassunto non disponibile: {e})"


RICERCHE = {"ricerca500": _ricerca500}


# ---------- sorveglianza ----------
def segui(nome: str):
    memo_f = ATTIVE / f"{nome}.json"
    memo = json.loads(memo_f.read_text()) if memo_f.exists() else {"quarti": 0, "fasi": [], "ferma": False}
    salva = lambda: memo_f.write_text(json.dumps(memo), encoding="utf-8")  # noqa: E731
    s = RICERCHE[nome]()
    if not memo.get("avviata"):
        manda(f"🔔 Notifiche accese per <b>{s['nome']}</b>\nAvanzamento: {s['fatti']}/{s['totale']} "
              f"({s['fatti'] / max(s['totale'], 1):.0%})")
        memo["avviata"] = True
        memo["quarti"] = int(4 * s["fatti"] / max(s["totale"], 1))
        salva()
    while True:
        try:
            s = RICERCHE[nome]()
            q = int(4 * s["fatti"] / max(s["totale"], 1))
            if q > memo["quarti"] and q < 4:
                manda(f"📈 {s['nome']}: {q * 25}% ({s['fatti']}/{s['totale']})")
                memo["quarti"] = q
            for chiave, testo, csv in s["fasi"]:
                if csv.exists() and chiave not in memo["fasi"]:
                    manda(f"✅ <b>{s['nome']}</b>: {testo}\n\n{_riassunto_portafogli(csv)}\n\nScrivi a Claude per i dettagli.")
                    memo["fasi"].append(chiave)
            fermo = time.time() - s["ultimo"]
            if not s["finito"] and fermo > FERMA_DOPO and not memo["ferma"] and s["fatti"] < s["totale"]:
                manda(f"⚠️ {s['nome']}: nessun lavoro finito da {fermo / 60:.0f} minuti. Controlla che il PC e "
                      f"la finestra della ricerca siano accesi.")
                memo["ferma"] = True
            elif fermo < FERMA_DOPO:
                memo["ferma"] = False
            lib = shutil.disk_usage(ROOT).free / 1e9
            if lib < 1.5 and not memo.get("disco"):
                manda(f"⚠️ Disco quasi pieno: {lib:.1f} GB liberi.")
                memo["disco"] = True
            if s["finito"]:
                manda(f"🏁 <b>{s['nome']}</b> FINITA ({datetime.now():%d/%m %H:%M}). Notifiche spente per questa ricerca.")
                salva()
                (ATTIVE / f"{nome}.pid").unlink(missing_ok=True)
                return
            salva()
        except Exception as e:
            print("errore nel controllo:", e)
        time.sleep(CONTROLLO_OGNI)


def attiva(nome: str):
    if nome not in RICERCHE:
        raise SystemExit(f"ricerca sconosciuta: {nome}. Disponibili: {', '.join(RICERCHE)}")
    ATTIVE.mkdir(exist_ok=True)
    if _vivo(nome):
        print("gia' attive per", nome)
        return
    pyw = Path(sys.executable).with_name("pythonw.exe")
    p = subprocess.Popen([str(pyw if pyw.exists() else sys.executable), str(Path(__file__)), "segui", nome],
                         cwd=QUI, creationflags=0x00000008 | 0x00000200)  # DETACHED_PROCESS | NEW_PROCESS_GROUP
    (ATTIVE / f"{nome}.pid").write_text(str(p.pid))
    print("notifiche accese per", nome, "pid", p.pid)


def _vivo(nome: str) -> bool:
    f = ATTIVE / f"{nome}.pid"
    if not f.exists():
        return False
    pid = f.read_text().strip()
    r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
    return pid in r.stdout


def disattiva(nome: str):
    f = ATTIVE / f"{nome}.pid"
    if f.exists():
        subprocess.run(["taskkill", "/PID", f.read_text().strip(), "/F"], capture_output=True)
        f.unlink()
    (ATTIVE / f"{nome}.json").unlink(missing_ok=True)
    manda(f"🔕 Notifiche spente per {nome}.")
    print("spente per", nome)


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "collega":
        collega(a[1])
    elif a[0] == "prova":
        print("inviato" if manda("👋 Prova: le notifiche funzionano.") else "non inviato")
    elif a[0] == "attiva":
        attiva(a[1])
    elif a[0] == "disattiva":
        disattiva(a[1])
    elif a[0] == "segui":
        segui(a[1])
    elif a[0] == "stato":
        for n in RICERCHE:
            print(n, "ACCESE" if _vivo(n) else "spente")


if __name__ == "__main__":
    main()
