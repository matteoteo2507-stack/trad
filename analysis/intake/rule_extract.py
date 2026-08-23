"""Compressore di regole - riduce una trascrizione ai soli passaggi con REGOLE specificate.

Perche' non un filtro percentuale. Il primo prototipo (2026-08-17) classificava i video per
densita' di concetti gia' falsificati e SCARTAVA quelli sotto soglia. Sbagliato: avrebbe buttato
Kichev, che era in stragrande maggioranza discorso generico ma conteneva DUE paragrafi utili (la
spec Donchian e il claim sul playground) - gli unici che hanno prodotto un lead. Un criterio di
densita' misura il rumore, non il segnale.

Questo NON decide se leggere. COMPRIME: tiene le finestre di testo in cui compare una regola
meccanicamente specificata (numeri con unita', timeframe, condizioni di entrata/uscita, ordini,
indicatori, gestione del rischio) e butta il resto. Le famiglie gia' falsificate diventano
un'ETICHETTA accanto al passaggio, non un verdetto sul video.

Le trascrizioni automatiche non hanno punteggiatura: si lavora a finestre scorrevoli di parole,
non a frasi.

Uso:
  python analysis/intake/rule_extract.py --all
  python analysis/intake/rule_extract.py <file.md> [...]
"""
from __future__ import annotations

import argparse
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(ROOT, "fondamenti_tecnici", "_sorgenti", "insight_da_yt", "_raw")
OUT = os.path.join(RAW, "_digest")

WIN, STRIDE = 45, 22        # finestra e passo, in parole

# --- segnali di REGOLA: cio' che rende un passaggio potenzialmente codificabile ---
SIGNALS = {
    # [\s-]? e non \s?: "100-day high" e "10-day MA" erano PERSI per via del trattino.
    # Bug trovato il 2026-08-17 calibrando sul solo caso di cui conosciamo la risposta giusta
    # (la spec Donchian di Kichev, l'unico passaggio che abbia mai prodotto un lead).
    "numero+unita": [r"\b\d+(\.\d+)?[\s-]?(pip|point|tick|percent|%|r\b|atr|period|bar|candle|"
                     r"minute|min|hour|day|week|month|sma|ema|ma\b)"],
    "timeframe": [r"\b(1|2|3|5|10|15|30)\s?(m|min|minute)\b", r"\b(1|4)\s?(h|hour)\b",
                  r"\b(daily|weekly|monthly|intraday)\b", r"\b(m1|m5|m15|m30|h1|h4|d1|w1)\b"],
    # lista di verbi larga: "falls below" era PERSO (stesso bug di calibrazione)
    "condizione": [r"\b(clos|break|cross|trad|fall|mov|go|goes|drop|ris|push|hold|stay|dip|"
                   r"reclaim|reject)\w*\s+(above|below|through|under|over|back)\b",
                   r"\bif\s+(the\s+)?price\b", r"\bwait(s|ing)? for\b", r"\bonly (if|when)\b",
                   r"\bconfirm(ed|ation)\b"],
    "entrata_uscita": [r"\b(entry|enter|entries)\b", r"\b(exit|exits|close the (trade|position))\b",
                       r"\b(take profit|tp\b|target)\b", r"\b(stop ?loss|sl\b|stop out)\b",
                       r"\b(trail(ing)?|break ?even)\b"],
    "ordine": [r"\b(limit|market|stop) order\b", r"\bpending order\b", r"\bfill(ed)?\b"],
    "indicatore": [r"\b(rsi|macd|adx|atr|stochastic|bollinger|vwap|ichimoku)\b",
                   r"\b(moving average|ema|sma|ma\d+|\d+ ?(day|period) (ma|moving average))\b"],
    "rischio": [r"\brisk(:| to | )reward\b", r"\b1\s?:\s?\d\b", r"\br\s?:\s?r\b",
                r"\bposition siz", r"\brisk per trade\b", r"\b\d+(\.\d+)?%\s+(of|per)\b"],
    # CLAIM STRUTTURALE: non e' una regola, e' un'affermazione su DOVE vive l'edge.
    # Aggiunta il 2026-08-17 perche' senza di essa il compressore perdeva il claim sul
    # "playground" di Kichev - l'unica cosa in tutto il funnel che abbia prodotto un lead.
    # Le regole si possono ricavare da mille fonti; le affermazioni falsificabili su dove
    # cercare sono rare, e sono quelle che spostano davvero il lavoro.
    "claim_strutturale": [
        r"\bedge\b.{0,40}\b(decay|decays|decreas|erod|disappear|shrink|gone|lower|higher)",
        r"\b(more|less|most|least)\s+(liquid|volatile|competitive|efficient|crowded)",
        r"\b(higher|lower|larger|smaller)\s+(time ?frame|timeframe)",
        r"\b(competition|arbitrage[d]?|crowded|efficien\w+)\b.{0,40}\b(market|asset|edge)",
        r"\b(retail|institution\w+)\b.{0,40}\b(advantage|edge|compete|disadvantage)",
        r"\b(liquidity|volatility)\b.{0,30}\b(inverse|relate|correlat|proportional)",
        r"\b(asset class|instrument)\w*\b.{0,40}\b(better|worse|higher|lower|more|less)\b",
    ],
}

# --- famiglie GIA' FALSIFICATE nel repo: etichetta, non verdetto ---
CLOSED = {
    "livelli-zone-reazione (384 trial, CLOSED)": [
        r"order ?block", r"\bfvg\b", r"fair value gap", r"imbalance",
        r"liquidity (sweep|grab|pool|void)", r"stop ?hunt", r"previous day (high|low)",
        r"\bpdh\b", r"\bpdl\b", r"equal (high|low)", r"supply (and|&) demand",
        r"(supply|demand) zone", r"support (and|&) resistance", r"break of structure",
        r"\bbos\b", r"choch", r"market structure", r"premium (and )?discount", r"\bict\b", r"\bsmc\b"],
    "volume-profilo (v2, 0/48 celle)": [
        r"volume profile", r"point of control", r"\bpoc\b", r"value area", r"\bvwap\b"],
    "fibonacci-ritracciamento (NXT NO-GO)": [
        r"fibonacci", r"golden pocket", r"0\.?618", r"0\.?786", r"retracement"],
    "numeri-tondi (NULL, CLOSED)": [r"round number", r"psychological level", r"big figure"],
    "opening-range (NO-GO 14.5y)": [r"opening range", r"\borb\b"],
    "stagionalita-calendario (TOM NO-GO)": [
        r"turn of (the )?month", r"seasonal", r"day of (the )?week"],
    "trend-following (round 2/3 speso)": [r"donchian", r"\d+ ?day (high|low)", r"trend follow"],
}

# --- non testabile con i nostri dati: etichetta ---
UNTESTABLE = {
    "order flow (serve tick/book, non l'abbiamo)": [
        r"order ?flow", r"footprint", r"\bdelta\b", r"absorption", r"\bdom\b", r"time and sales"],
}


def tags(text, table):
    out = []
    for name, pats in table.items():
        n = sum(len(re.findall(p, text, re.I)) for p in pats)
        if n:
            out.append((name, n))
    return sorted(out, key=lambda x: -x[1])


def score(text):
    hits = {k: sum(len(re.findall(p, text, re.I)) for p in v) for k, v in SIGNALS.items()}
    cats = sum(1 for v in hits.values() if v)
    strong = (hits["numero+unita"] + hits["condizione"] + hits["rischio"]
              + 2 * hits["claim_strutturale"])   # il claim vale doppio: e' raro
    return cats, strong, hits


def body(path):
    """Salta l'intestazione scritta da yt_fetch.py, ma solo se e' davvero un'intestazione.

    Senza il controllo di posizione, un file con un '---' a meta' testo verrebbe troncato
    in silenzio e meta' del contenuto sparirebbe senza errore.
    """
    t = open(path, encoding="utf-8").read()
    i = t.find("\n---\n")
    return t[i + 5:] if 0 <= i < 700 else t


def process(path, min_cats=2, min_strong=1):
    txt = body(path)
    words = txt.split()
    keep = []
    for i in range(0, max(len(words) - WIN, 0) + 1, STRIDE):
        w = " ".join(words[i:i + WIN])
        cats, strong, hits = score(w)
        # Un claim strutturale BASTA da solo: e' prosa pura, senza numeri ne' timeframe, quindi
        # non raggiungerebbe mai min_cats. Era il motivo per cui il claim sul "playground"
        # continuava a sfuggire anche dopo aver aggiunto il suo lessico (2026-08-17).
        if hits["claim_strutturale"] > 0 or (cats >= min_cats and strong >= min_strong):
            keep.append((i, i + WIN))
    merged = []
    for a, b in keep:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    passages = [" ".join(words[a:b]) for a, b in merged]
    return txt, words, passages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--min-cats", type=int, default=2)
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(RAW, "*.md"))) if a.all else a.files
    if not files:
        print("nessun file. Prima: python analysis/intake/yt_fetch.py <url canale>")
        return
    os.makedirs(OUT, exist_ok=True)
    print("{:50}{:>8}{:>8}{:>8}  etichette".format("file", "parole", "tenute", "compr."))
    tot_in = tot_out = 0
    for p in files:
        txt, words, pas = process(p, a.min_cats)
        kept = sum(len(x.split()) for x in pas)
        tot_in += len(words)
        tot_out += kept
        cl = tags(txt, CLOSED)
        un = tags(txt, UNTESTABLE)
        lab = ", ".join("{}({})".format(n.split(" (")[0], c) for n, c in (cl + un)[:2]) or "-"
        ratio = "{:.0f}%".format(100 * kept / max(len(words), 1))
        name = os.path.basename(p)
        print("{:50}{:8}{:8}{:>8}  {}".format(name[:48], len(words), kept, ratio, lab))
        out_path = os.path.join(OUT, name.replace(".md", ".digest.md"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# DIGEST - {}\n\n".format(name))
            f.write("Compressione: {} -> {} parole ({}). {} passaggi con regole specificate.\n\n"
                    .format(len(words), kept, ratio, len(pas)))
            if cl:
                f.write("## Famiglie GIA' FALSIFICATE presenti (etichetta, non verdetto)\n\n")
                for n, c in cl:
                    f.write("- {} - {} riscontri\n".format(n, c))
                f.write("\n")
            if un:
                f.write("## Non testabile con i nostri dati\n\n")
                for n, c in un:
                    f.write("- {} - {} riscontri\n".format(n, c))
                f.write("\n")
            f.write("## Passaggi con regole specificate\n\n")
            for i, x in enumerate(pas, 1):
                f.write("### {}\n\n{}\n\n".format(i, x))
    print("\nTOTALE {} -> {} parole ({:.1f}%). Digest in {}"
          .format(tot_in, tot_out, 100 * tot_out / max(tot_in, 1), os.path.relpath(OUT, ROOT)))
    print("Il digest NON e' un verdetto: e' cio' che vale la pena leggere.")


if __name__ == "__main__":
    main()
