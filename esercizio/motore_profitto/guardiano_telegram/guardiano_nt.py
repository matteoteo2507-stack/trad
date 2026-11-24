"""GUARDIANO NinjaTrader - Motore Profitto (12/11/2026). Solo lettura: non tocca NinjaTrader ne' i bot.
Ogni 20 s controlla:
 1) Documenti\\NinjaTrader 8\\eventi_bot.txt (scritto dai bot): entrate, uscite, risultati, aggiunte, blocchi, ordini rifiutati -> Telegram
 2) il registro di NinjaTrader (log\\log.*.txt): connessione persa > 60 s, strategia disattivata e non riattivata entro 2 min -> Telegram
 3) che NinjaTrader sia acceso (processo NinjaTrader.exe): se no avviso ogni 30 min
 + riepilogo serale alle 22:05 (ora del PC).
Avvio: AVVIA_GUARDIANO_NT.bat (resta aperto in una finestra; chiudendola si ferma). Prova senza Telegram: python guardiano_nt.py --prova"""
import glob, os, re, subprocess, sys, time, datetime as dt

NT = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8")
EVENTI = os.path.join(NT, "eventi_bot.txt")
PROVA = "--prova" in sys.argv
sys.path.insert(0, "D:/motore_profitto/notifiche")
try:
    from telegram import manda as _manda
except Exception:
    _manda = None


def manda(testo):
    testo = testo.replace("&", "e").replace("<", "sotto ").replace(">", "sopra ")
    print(dt.datetime.now().strftime("%H:%M:%S"), "|", testo.replace("\n", " / "), flush=True)
    if not PROVA and _manda:
        try:
            _manda(testo)
        except Exception as e:
            print("invio Telegram fallito:", e)


def nt_acceso():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq NinjaTrader.exe"], capture_output=True, text=True, timeout=20).stdout
        return "NinjaTrader.exe" in out
    except Exception:
        return True          # nel dubbio non allarmare


def ultimo_log():
    fs = [f for f in glob.glob(os.path.join(NT, "log", "log.*.txt")) if ".it." not in f]
    return max(fs, key=os.path.getmtime) if fs else None


def leggi_nuovo(path, pos):
    try:
        size = os.path.getsize(path)
        if size < pos: pos = 0
        if size == pos: return [], pos
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(pos); dati = f.read(); pos = f.tell()
        return [r for r in dati.splitlines() if r.strip()], pos
    except FileNotFoundError:
        return [], 0


def descrivi_evento(r, oggi):
    """riga 'data ora|bot|testo' -> testo per Telegram (None = non mandare)"""
    m = _descrivi(r, oggi)
    if m and "|OroSpintaNT|" in r: m = m.replace("ORO ", "ORO SPINTA ", 1).replace("Oro:", "Oro SPINTA:", 1).replace("/2", "")
    return m


def _descrivi(r, oggi):
    p = r.split("|", 2)
    if len(p) < 3: return None
    quando, bot, t = p[0][11:16], p[1], p[2]
    if "ORDINE" in t and "OroOrderFlowNT" in t:
        c = t.split(";")
        if len(c) >= 7: return f"ORO {c[2]} {c[3]}: ordine inviato ({quando}) entrata ~{c[4]} stop {c[5]}" + (f" target {c[6]}" if c[6] else "") + f" | {c[-1].split(',')[0].replace('ORDINE ', '')}"
    if "RITARDO" in t: return f"ATTENZIONE ({quando}) {bot}: segnale saltato perche' arrivato in ritardo - " + t.split(": ", 1)[-1]
    m = re.search(r"(OF\w+): entrato (\d+) contratti a (\d+(?:[.,]\d+)?), stop (\d+(?:[.,]\d+)?)(?:, target (\d+(?:[.,]\d+)?))?", t)
    if m:
        r_ = re.search(r"eseguito ([\d.,]+) s", t)
        return f"ORO ENTRATO ({quando}): {m.group(2)} MGC a {m.group(3)}, stop {m.group(4)}" + (f", target {m.group(5)}" if m.group(5) else "") + (f" | ritardo {r_.group(1)} s" if r_ else "")
    m = re.search(r"(OF\w+): risultato (-?\d+(?:[.,]\d+)?) punti x contratti -> perdite di fila (\d+), perdite oggi (\d+)", t)
    if m:
        usd = float(m.group(2).replace(",", ".")) * 10
        oggi["usd"] += usd; oggi["chiusi"] += 1
        return f"ORO CHIUSO ({quando}): {'+' if usd >= 0 else ''}{usd:.0f} $ (prima delle commissioni) | perdite di fila {m.group(3)}, oggi {m.group(4)}/2"
    m = re.search(r"(OF\w+): chiuso a ([\d.,]+) \((\w+)\)", t)
    if m: return None                                   # il risultato arriva gia' nella riga sopra
    if "AGGIUNTA" in t: return f"ORO AGGIUNTA ({quando}): " + t.split(": ", 1)[-1]
    if "GUARDIANO" in t: return f"BLOCCO GIORNALIERO ({quando}) {bot}: " + t.split("GUARDIANO: ", 1)[-1]
    if "filtro POC" in t: return f"Oro: segnale GROSSI saltato dal filtro POC ({quando})"
    if "salto fino a domani" in t: return f"Oro: segnale saltato, gia' 2 perdite oggi ({quando})"
    if "rischio ridotto" in t: return f"Oro ({quando}): " + t.split(": ", 1)[-1]
    if "fine tempo" in t: return None
    if "RIFIUTATO" in t: return f"ATTENZIONE ({quando}) {bot}: ORDINE RIFIUTATO - {t}"
    if "News oro: coppia stop" in t:
        if oggi.get("news_avvisata"): return None
        oggi["news_avvisata"] = True; return f"NEWS ORO ({quando}): stop piazzati, il bot lavora la news"
    if t.startswith("ESEGUITO"):
        oggi["esec_news"] = oggi.get("esec_news", 0) + 1
        return None                                     # troppe righe: vanno nel riepilogo
    if bot == "OroSpintaNT" and "SPINTA;" in t and "ORDINE" in t:
        c = t.split(";")
        if len(c) >= 7: return f"ORO {c[3]}: ordine inviato ({quando}) entrata ~{c[4]} stop {c[5]} target {c[6]}"
    if bot == "OroSpintaNT" and ("salto" in t or "minuti passati" in t): return f"Oro SPINTA ({quando}): " + t.replace("OroSpintaNT", "").strip(" :")
    if "Regola" in t and "contratti, stop" in t: return f"REGOLA INTRADAY ({quando}): " + t.split(" ", 2)[-1]
    return None


def main():
    manda("GUARDIANO NinjaTrader avviato: ti avviso su trade, blocchi, connessione e strategie.")
    pos_ev = os.path.getsize(EVENTI) if os.path.exists(EVENTI) else 0
    log = ultimo_log(); pos_log = os.path.getsize(log) if log else 0
    persa_da = None; disattivate = {}; ultimo_allarme_nt = 0; nt_era_spento = False
    oggi = {"giorno": dt.date.today(), "usd": 0.0, "chiusi": 0, "connessioni": 0}; riepilogo_fatto = False
    while True:
        adesso = time.time(); ora = dt.datetime.now()
        if ora.date() != oggi["giorno"]:
            oggi = {"giorno": ora.date(), "usd": 0.0, "chiusi": 0, "connessioni": 0}; riepilogo_fatto = False
        # 1) eventi dei bot
        righe, pos_ev = leggi_nuovo(EVENTI, pos_ev)
        msg = [m for m in (descrivi_evento(r, oggi) for r in righe) if m]
        if msg: manda("\n".join(msg))
        # 2) registro NinjaTrader
        nuovo = ultimo_log()
        if nuovo != log: log, pos_log = nuovo, 0
        righe, pos_log = leggi_nuovo(log, pos_log) if log else ([], 0)
        for r in righe:
            if "connection=Connection lost" in r or "Price feed=Connection lost" in r:
                if persa_da is None: persa_da = adesso
            elif "Primary connection=Connected, Price feed=Connected" in r:
                if persa_da is not None and adesso - persa_da > 60:
                    manda(f"Connessione RIPRISTINATA dopo {int((adesso - persa_da) / 60)} min.")
                persa_da = None
            m = re.search(r"Disabling NinjaScript strategy '([^/']+)", r)
            if m: disattivate[m.group(1)] = adesso
            m = re.search(r"Enabling NinjaScript strategy '([^/']+)", r)
            if m:
                if disattivate.get(m.group(1), 0) < 0: manda(f"Strategia {m.group(1)} di nuovo ATTIVA.")
                disattivate.pop(m.group(1), None)
        if persa_da is not None and adesso - persa_da > 60 and not oggi.get("avvisata_conn"):
            manda("ATTENZIONE: NinjaTrader ha PERSO LA CONNESSIONE da piu' di 1 minuto. Controlla internet / NinjaTrader.")
            oggi["avvisata_conn"] = True; oggi["connessioni"] += 1
        if persa_da is None: oggi["avvisata_conn"] = False
        for nome, t0 in list(disattivate.items()):
            if t0 > 0 and adesso - t0 > 120:
                manda(f"ATTENZIONE: la strategia {nome} e' DISATTIVATA da piu' di 2 minuti. Riattivala (Strategie -> Abilitato).")
                disattivate[nome] = -1
        # 3) NinjaTrader acceso?
        if int(adesso) % 60 < 20:
            acceso = nt_acceso()
            if not acceso and adesso - ultimo_allarme_nt > 1800:
                manda("ATTENZIONE: NinjaTrader NON e' acceso. I bot non stanno lavorando."); ultimo_allarme_nt = adesso; nt_era_spento = True
            if acceso and nt_era_spento:
                manda("NinjaTrader di nuovo acceso. Controlla che le strategie siano abilitate."); nt_era_spento = False; ultimo_allarme_nt = 0
        # riepilogo serale
        if not riepilogo_fatto and ora.hour == 22 and ora.minute >= 5:
            stato = ""
            try:
                p = open(os.path.join(NT, "of_stato.txt")).read().strip().split(";"); stato = f" | perdite di fila {p[0]}"
            except Exception:
                pass
            manda(f"RIEPILOGO {ora:%d/%m}: oro chiusi {oggi['chiusi']} trade, risultato {oggi['usd']:+.0f} $ (prima delle commissioni){stato}"
                  f" | esecuzioni news/regole {oggi.get('esec_news', 0)} | NinjaTrader {'acceso' if nt_acceso() else 'SPENTO'}")
            riepilogo_fatto = True
        time.sleep(20)


if __name__ == "__main__":
    main()
