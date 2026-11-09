"""Sposta file e cartelle di trad e riscrive i riferimenti (riordino in cinque macro, DECISIONS 2026-11-09).

Uso, dalla radice di trad:
    python motore/riordino/sposta.py mappa.json            # prova a secco: elenca cosa cambierebbe
    python motore/riordino/sposta.py mappa.json --applica  # git mv + riscrittura

`mappa.json`:
    {"spostamenti": [["vecchio/percorso", "nuovo/percorso"], ...],
     "moduli":      [["vecchio.modulo", "nuovo.modulo"], ...]}       # pacchetti Python spostati

Cosa riscrive:
1. **Link markdown relativi** `[..](percorso)` in tutti i file di testo: si ricalcolano se si sposta il file che li
   contiene o il file a cui puntano. Vale anche nei registri storici, perche' un link deve continuare a funzionare.
2. **Menzioni di percorso** dalla radice (`mql5/README.md`, `` `analysis/ops/` ``) e, nei file dell'hub, `trad/<percorso>`:
   solo nei documenti vivi e nel codice. Nei registri storici (vedi STORICI) restano come scritte allora.
3. **Import Python** dei moduli spostati (`from X`, `import X`, `python -m X`) nei file `.py` e nei documenti vivi.

Prima calcola tutto, poi sposta, poi scrive ogni file con file temporaneo + sostituzione: un errore a meta' calcolo
non tocca niente (regola "calcola prima, scrivi dopo").
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

TRAD = Path(__file__).resolve().parents[2]
HUB = TRAD.parent

TESTO = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".base", ".txt", ".mq5", ".mqh", ".cfg", ".ini"}
# Fonti grezze e dati: non si toccano mai.
INTOCCABILI = ("fondamenti_tecnici/_sorgenti/", "materiale_socio/", "Da distillare/", "prop-lab/data/",
               "prop-lab/results/", "signal_copier/samples/", "esercizio/signal_copier/samples/")
# Registri storici: si aggiornano i link, non il testo.
STORICI = ("DECISIONS.md", "mappa/_modifiche.md", "docs/reviews/", "docs/health/", "fondamenti_tecnici/_INTAKE.md",
           "esercizio/sorveglianza/report/", "decisioni/DECISIONS.md", "decisioni/mappa/_modifiche.md",
           "decisioni/_INTAKE.md")
# Codice congelato di uno studio chiuso: si sposta ma non si riscrive (si riproduce dal commit del verdetto).
CONGELATI = ("analysis/ultima_mezzora/", "motore/riordino/")  # anche questo strumento: le sue costanti sono percorsi
# File dell'hub che citano trad (solo documenti vivi; i registri dell'hub restano come sono).
HUB_VIVI = ("CLAUDE.md", "README.md", "MEMORY.md", "mappa", "projects", "laboratorio", "global", "memoria/trad",
            ".claude")
HUB_STORICI = ("mappa/_modifiche.md", "global/registro-epistemico/")
VIETATE = re.compile(r"personal|personale|personali", re.I)

LINK = re.compile(r"(\]\()([^)\s]+)(\))")


def git(*args: str, cwd: Path = TRAD) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


def file_tracciati(root: Path) -> list[str]:
    return [p for p in git("ls-files", cwd=root).splitlines() if p]


def nuovo_percorso(rel: str, spost: list[tuple[str, str]]) -> str | None:
    """Percorso nuovo di un file (relativo a trad), o None se non si sposta."""
    for vecchio, nuovo in spost:
        if rel == vecchio:
            return nuovo
        if rel.startswith(vecchio.rstrip("/") + "/"):
            return nuovo.rstrip("/") + rel[len(vecchio.rstrip("/")):]
    return None


def norm(p: PurePosixPath) -> str:
    parti: list[str] = []
    for x in p.parts:
        if x == "..":
            if parti:
                parti.pop()
            else:
                return ""
        elif x not in (".", ""):
            parti.append(x)
    return "/".join(parti)


def relativo(da_dir: str, a: str) -> str:
    return os.path.relpath(a, da_dir or ".").replace(os.sep, "/")


def riscrivi_link(testo: str, src_vecchio: str, src_nuovo: str, base: str, spost, esistenti: set[str]) -> str:
    """Ricalcola i link relativi. `base` = prefisso del repo del file ('' per trad, 'trad/' visto dall'hub)."""
    dir_v = str(PurePosixPath(src_vecchio).parent) if "/" in src_vecchio else ""
    dir_n = str(PurePosixPath(src_nuovo).parent) if "/" in src_nuovo else ""

    def sost(m: re.Match) -> str:
        dest = m.group(2)
        if re.match(r"^[a-z]+:", dest) or dest.startswith("#"):
            return m.group(0)
        percorso, _, anc = dest.partition("#")
        assoluto = norm(PurePosixPath(dir_v) / unquote(percorso))
        if not assoluto:
            return m.group(0)
        if base:  # file dell'hub: interessano solo i bersagli dentro trad
            if not assoluto.startswith(base):
                return m.group(0)
            dentro = assoluto[len(base):]
        else:
            dentro = assoluto
        cartella = dentro.rstrip("/")
        if dentro not in esistenti and not any(e.startswith(cartella + "/") for e in esistenti):
            return m.group(0)  # link gia' rotto o fuori dal repo: non lo tocco
        dest_nuovo = nuovo_percorso(dentro, spost) or dentro
        if dest_nuovo == dentro and src_nuovo == src_vecchio:
            return m.group(0)
        nuovo = relativo(dir_n, base + dest_nuovo if base else dest_nuovo)
        if percorso.endswith("/") and not nuovo.endswith("/"):
            nuovo += "/"
        if " " in nuovo and "%20" in percorso:
            nuovo = nuovo.replace(" ", "%20")
        return m.group(1) + nuovo + ("#" + anc if anc else "") + m.group(3)

    return LINK.sub(sost, testo)


def riscrivi_menzioni(testo: str, spost, prefisso: str = "") -> str:
    """Solo menzioni che sono chiaramente percorsi: un file con estensione, o una cartella seguita da '/'.
    La parola nuda (es. il nome del componente `signal_copier`, o "mql5" in una frase) non si tocca."""
    # I wikilink si risolvono per nome in Obsidian: non si toccano (e possono puntare all'hub, non a trad).
    pezzi = re.split(r"(\[\[[^\]]*\]\])", testo)
    if len(pezzi) > 1:
        return "".join(x if x.startswith("[[") else riscrivi_menzioni(x, spost, prefisso) for x in pezzi)
    for vecchio, nuovo in spost:
        v = re.escape(prefisso + vecchio)
        e_file = bool(PurePosixPath(vecchio).suffix)
        if e_file and "/" not in vecchio and not prefisso:
            continue  # file della radice citato per nome (es. "DECISIONS.md"): e' un nome, non un percorso
        dopo = r"(?=[\s`'\")\],;:|#]|\.(?!\w)|$)" if e_file else r"(?=/)"
        testo = re.sub(rf"(?<![\w/.\-]){v}{dopo}", lambda m: prefisso + nuovo, testo, flags=re.M)
    return testo


def riscrivi_moduli(testo: str, moduli) -> str:
    for vecchio, nuovo in moduli:
        v = re.escape(vecchio)
        testo = re.sub(rf"(\bfrom\s+){v}(?=[\s.])", rf"\g<1>{nuovo}", testo)
        testo = re.sub(rf"(^\s*import\s+){v}(?=[\s.]|$)", rf"\g<1>{nuovo}", testo, flags=re.M)
        testo = re.sub(rf"(-m\s+){v}(?=[\s.`]|$)", rf"\g<1>{nuovo}", testo, flags=re.M)
    return testo


def e_storico(rel: str, storici) -> bool:
    return any(rel == s or rel.startswith(s) for s in storici)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mappa")
    ap.add_argument("--applica", action="store_true")
    ap.add_argument("--diff", action="store_true", help="mostra le righe che cambiano")
    a = ap.parse_args()
    conf = json.loads(Path(a.mappa).read_text(encoding="utf-8"))
    spost = [tuple(x) for x in conf.get("spostamenti", [])]
    moduli = [tuple(x) for x in conf.get("moduli", [])]

    tracciati = file_tracciati(TRAD)
    esistenti = set(tracciati)
    for v, _ in spost:
        if v not in esistenti and not any(e.startswith(v.rstrip("/") + "/") for e in esistenti):
            print(f"ERRORE: {v} non e' tracciato da git", file=sys.stderr)
            return 1
    mosse = {f: nuovo_percorso(f, spost) for f in tracciati if nuovo_percorso(f, spost)}
    for f, n in mosse.items():
        if (TRAD / n).exists():
            print(f"ERRORE: la destinazione esiste gia': {n}", file=sys.stderr)
            return 1

    # 1. calcolo di tutte le riscritture (niente si tocca)
    scritture: dict[Path, str] = {}
    riepilogo: list[str] = []
    for f in tracciati:
        if Path(f).suffix.lower() not in TESTO or e_storico(f, CONGELATI):
            continue
        if e_storico(f, INTOCCABILI) and Path(f).name != "README.md":
            continue
        p = TRAD / f
        try:
            prima = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        dopo = prima
        if f.endswith(".md"):
            dopo = riscrivi_link(dopo, f, mosse.get(f, f), "", spost, esistenti)
        if not e_storico(f, STORICI):
            dopo = riscrivi_menzioni(dopo, spost)
            dopo = riscrivi_moduli(dopo, moduli)
        if dopo != prima:
            scritture[TRAD / mosse.get(f, f)] = dopo
            riepilogo.append(f"trad/{f}" + (f" -> {mosse[f]}" if f in mosse else ""))

    hub = [x for x in file_tracciati(HUB) if any(x == d or x.startswith(d + "/") for d in HUB_VIVI)
           and x.endswith(".md") and not VIETATE.search(x)]
    for f in hub:
        p = HUB / f
        prima = p.read_text(encoding="utf-8")
        dopo = riscrivi_link(prima, f, f, "trad/", spost, esistenti)
        if not e_storico(f, HUB_STORICI):
            dopo = riscrivi_menzioni(dopo, spost, prefisso="trad/")
            if f.startswith("memoria/trad/"):  # la memoria di trad cita i percorsi dalla radice di trad
                dopo = riscrivi_menzioni(dopo, spost)
                dopo = riscrivi_moduli(dopo, moduli)
        if dopo != prima:
            scritture[p] = dopo
            riepilogo.append(f"hub/{f}")

    print(f"file da spostare: {len(mosse)}")
    for f, n in list(mosse.items())[:400]:
        print(f"  mv {f} -> {n}")
    print(f"file da riscrivere: {len(riepilogo)}")
    for r in riepilogo:
        print(f"  {r}")
    if a.diff:
        import difflib
        for p_, testo in scritture.items():
            orig = None
            for f, n in mosse.items():
                if TRAD / n == p_:
                    orig = TRAD / f
            orig = orig or p_
            vecchio = orig.read_text(encoding="utf-8").splitlines()
            for riga in difflib.unified_diff(vecchio, testo.splitlines(), str(orig), str(p_), n=0, lineterm=""):
                if not riga.startswith(("---", "+++", "@@")):
                    print("   ", riga[:200])
    if not a.applica:
        print("\nprova a secco: niente e' stato toccato (aggiungi --applica)")
        return 0

    # 2. spostamenti, 3. scritture
    for v, n in spost:
        (TRAD / n).parent.mkdir(parents=True, exist_ok=True)
        git("mv", v, n)
    for p, testo in scritture.items():
        tmp = p.with_name(p.name + ".tmp-riordino")
        tmp.write_text(testo, encoding="utf-8", newline="")
        os.replace(tmp, p)
    print("\napplicato")
    return 0


if __name__ == "__main__":
    sys.exit(main())
