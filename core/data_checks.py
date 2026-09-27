"""La checklist dati/esecuzione come **codice eseguibile**, non come prosa.

Perche' esiste
--------------
Le checklist 2 e 3 di [`quant-gatekeeper.md`](../.claude/agents/quant-gatekeeper.md)
erano scritte bene e non servivano a niente: erano **prosa**. Ogni voce nasce da un
errore realmente accaduto qui, e ogni errore e' accaduto **dopo** che la voce era stata
scritta. Una regola che dipende dal fatto che qualcuno si ricordi di applicarla non e'
una regola, e' un auspicio.

I tre errori del 2026-09-18 — fuso di 1h, file corti mentre nel repo c'erano quelli
lunghi, nomi di file cablati che ignoravano l'ultimo export — sarebbero stati presi da
**tre assert**. Questi.

Come si usa
-----------
Ogni funzione ritorna un `Esito` stampabile; `Esito.ok` e' `False` se qualcosa e'
**rotto** (non se e' solo sospetto). Si compongono, e si stampa il risultato **prima**
di guardare qualunque numero:

    from core.data_checks import checklist_dati
    print(checklist_dati({"EURUSD": df1, "XAUUSD": df2}, barre_attese=(5000, 7000)))

Oppure da riga di comando, su un CSV OHLC qualunque:

    python -m core.data_checks data/mio_feed.csv

Cosa NON fa
-----------
Non sa cosa stai testando. Non puo' vedere un look-ahead logico, una selezione di asset
fatta dopo l'esito, o due bracci di un confronto che usano simulatori diversi. Prende la
classe di difetti **meccanici e verificabili dal dato**, che sono quelli che ci hanno
fatto perdere piu' tempo proprio perche' sembravano troppo banali per meritare un
controllo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

__all__ = [
    "Esito", "monotonia", "duplicati", "barre_per_anno", "copertura_comune",
    "file_piu_completo", "fill_ottenibili", "gap_oltre_stop",
    "checklist_dati", "checklist_esecuzione",
]


@dataclass
class Esito:
    """Report componibile. `ok=False` solo per i ROTTI: le riserve non bloccano."""

    titolo: str = ""
    ok: bool = True
    righe: list = field(default_factory=list)
    rotte: list = field(default_factory=list)
    riserve: list = field(default_factory=list)

    def add(self, stato: str, voce: str, testo: str) -> "Esito":
        self.righe.append("  [%s] %-18s %s" % (stato, voce, testo))
        if stato == "ROTTO":
            self.ok = False
            self.rotte.append(voce)
        elif stato == "riserva":
            self.riserve.append(voce)
        return self

    def unisci(self, altro: "Esito") -> "Esito":
        self.righe += altro.righe
        self.rotte += altro.rotte
        self.riserve += altro.riserve
        self.ok = self.ok and altro.ok
        return self

    def __str__(self) -> str:
        if not self.ok:
            stato = "ROTTO su " + ", ".join(sorted(set(self.rotte)))
        elif self.riserve:
            stato = "a posto, CON RISERVA su " + ", ".join(sorted(set(self.riserve)))
        else:
            stato = "a posto"
        return "\n".join([(self.titolo or "CHECKLIST DATI") + ": " + stato] + self.righe)

    def solleva_se_rotto(self) -> "Esito":
        """Per chi vuole che il difetto **fermi** lo script invece di stampare."""
        if not self.ok:
            raise AssertionError(str(self))
        return self


def _tempi(df, col):
    import pandas as pd
    return pd.DatetimeIndex(df[col])


# ---------------------------------------------------------------------------
# Checklist 2 — integrita' dei dati
# ---------------------------------------------------------------------------
def monotonia(df, col: str = "time", nome: str = "") -> Esito:
    """Il tempo cresce? Da rieseguire **dopo ogni** groupby/merge/resample.

    ⚠️ Precedente: il 2026-08-14 una chiave di raggruppamento costruita da un `cumsum`
    **invertito** ha prodotto una serie decrescente nel tempo. L'ha presa solo un sanity
    check che mostrava barre/anno negative — cioe' per fortuna.
    """
    e = Esito("MONOTONIA %s" % nome)
    t = _tempi(df, col)
    if t.is_monotonic_increasing:
        return e.add("ok", "monotonia", "%d righe, tempo crescente" % len(t))
    fuori = int((np.diff(t.values.astype("int64")) < 0).sum())
    return e.add("ROTTO", "monotonia",
                 "%d salti ALL'INDIETRO su %d: la serie non e' ordinata nel tempo"
                 % (fuori, len(t) - 1))


def duplicati(df, col: str = "time", nome: str = "") -> Esito:
    """Timestamp ripetuti: una barra contata due volte e' un trade contato due volte."""
    e = Esito("DUPLICATI %s" % nome)
    t = _tempi(df, col)
    n = int(t.duplicated().sum())
    if n == 0:
        return e.add("ok", "duplicati", "nessun timestamp ripetuto")
    return e.add("ROTTO", "duplicati", "%d timestamp ripetuti (%.2f%%)"
                 % (n, 100.0 * n / max(len(t), 1)))


def barre_per_anno(df, attese: Optional[tuple] = None, col: str = "time",
                   nome: str = "") -> Esito:
    """Il controllo piu' economico che esista, e ne prende molti.

    `attese` = (min, max) plausibili per strumento e timeframe. Senza, riporta e basta:
    un numero stampato e' gia' meglio di un numero mai guardato.
    """
    e = Esito("BARRE/ANNO %s" % nome)
    t = _tempi(df, col)
    if len(t) == 0:
        return e.add("ROTTO", "barre/anno", "dataframe vuoto")
    conte = {int(y): int((t.year == y).sum()) for y in sorted(set(t.year))}
    interi = {y: c for y, c in conte.items()
              if y not in (min(conte), max(conte))} or conte
    lo, hi = min(interi.values()), max(interi.values())
    testo = "%d anni, da %d a %d barre/anno (esclusi primo e ultimo)" % (len(conte), lo, hi)
    if attese is None:
        return e.add("riserva", "barre/anno", testo + " - nessun atteso dichiarato")
    a_lo, a_hi = attese
    if lo < a_lo or hi > a_hi:
        return e.add("ROTTO", "barre/anno",
                     "%s - fuori dall'atteso [%d, %d]" % (testo, a_lo, a_hi))
    return e.add("ok", "barre/anno", testo)


def copertura_comune(frames: dict, col: str = "time", tolleranza_giorni: int = 60) -> Esito:
    """Partenze scaglionate = confronto fra gruppi **confondato col periodo**.

    ⚠️ Precedente vivo: il feed del playground (A1) ha i bond dal 2016-17 e il resto dal
    2012. Un confronto fra gruppi su quel feed confronta anche epoche diverse. Questo
    controllo non lo ripara: lo rende **impossibile da non vedere**, e stampa la finestra
    comune da dichiarare.
    """
    import pandas as pd
    e = Esito("COPERTURA")
    if not frames:
        return e.add("ROTTO", "copertura", "nessun dataframe")
    inizi, fini = {}, {}
    for k, df in frames.items():
        t = _tempi(df, col)
        if len(t) == 0:
            e.add("ROTTO", "copertura", "%s: vuoto" % k)
            continue
        inizi[k], fini[k] = t.min(), t.max()
    if not inizi:
        return e
    t0, t1 = max(inizi.values()), min(fini.values())
    spread = (max(inizi.values()) - min(inizi.values())).days
    e.add("ok", "finestra comune", "%s -> %s" % (str(t0)[:10], str(t1)[:10]))
    if spread > tolleranza_giorni:
        tardivi = sorted(inizi.items(), key=lambda kv: kv[1])[-3:]
        e.add("riserva", "partenze",
              "scaglionate di %d giorni: i confronti fra serie sono in parte "
              "confronti fra EPOCHE. I piu' tardivi: %s"
              % (spread, ", ".join("%s dal %s" % (k, str(v)[:10]) for k, v in tardivi)))
    else:
        e.add("ok", "partenze", "allineate entro %d giorni" % spread)
    return e


def file_piu_completo(usato: str, pattern: Optional[str] = None) -> Esito:
    """Stai davvero usando il file piu' lungo che hai in repo?

    ⚠️ Precedente: il 2026-09-18 due analisi sono state invalidate perche' giravano su
    `XAU_spot_M5.csv` (fino al 12/06) mentre accanto c'era `XAU_spot_M5_ext.csv` (fino al
    07/08), e su un export Telegram vecchio di due mesi. Nessuno dei due difetti era
    invisibile: **era solo un nome di file cablato**.

    Args:
        usato: il percorso che lo script sta per leggere.
        pattern: glob dei candidati. Default: stessa cartella, stessa estensione.
    """
    import glob
    e = Esito("FILE")
    if not os.path.exists(usato):
        return e.add("ROTTO", "file", "non esiste: %s" % usato)
    base = os.path.basename(usato)
    if pattern is None:
        radice = os.path.splitext(base)[0].split("_")[0]
        pattern = os.path.join(os.path.dirname(usato) or ".",
                               radice + "*" + os.path.splitext(base)[1])
    cand = [p for p in glob.glob(pattern) if os.path.isfile(p)]
    mio = os.path.getsize(usato)
    piu_grandi = [(p, os.path.getsize(p)) for p in cand
                  if os.path.abspath(p) != os.path.abspath(usato)
                  and os.path.getsize(p) > mio * 1.02]
    if not piu_grandi:
        return e.add("ok", "file", "%s (%.1f MB) e' il piu' completo dei %d candidati"
                     % (base, mio / 1e6, len(cand)))
    p, sz = max(piu_grandi, key=lambda x: x[1])
    return e.add("ROTTO", "file",
                 "stai usando %s (%.1f MB) ma accanto c'e' %s (%.1f MB, +%.0f%%)"
                 % (base, mio / 1e6, os.path.basename(p), sz / 1e6,
                    100.0 * (sz / max(mio, 1) - 1)))


# ---------------------------------------------------------------------------
# Checklist 3 — onesta' dell'esecuzione
# ---------------------------------------------------------------------------
def fill_ottenibili(apertura_prima_barra: Sequence[float], entry: Sequence[float],
                    long: Sequence[bool], soglia_riserva: float = 0.05) -> Esito:
    """Quanti fill erano **ottenibili**? Il gate di `QUANT_REVIEW_PROTOCOL.md` Step 3bis.

    Un fill non e' ottenibile se, all'apertura della **prima barra azionabile**, il prezzo
    aveva gia' oltrepassato il livello: si transerebbe a un prezzo disponibile solo
    *prima* di poter agire. Non e' look-ahead di informazione, e' look-ahead di **prezzo**.

    ⚠️ Precedente: sul FADE era il **46,1%** dei setup, e conteneva l'intero risultato
    (+0,409 col fantasma, **−0,250** senza). Il difetto **non ha un segno**: lo stesso
    fantasma rendeva il NO-GO della continuazione troppo severo (−0,44R invece di −0,118R).

    Args:
        apertura_prima_barra: `O[cb+1]` per ogni setup.
        entry: il livello a cui il backtest fa entrare.
        long: True se la posizione desiderata e' long.
    """
    e = Esito("FILL")
    O = np.asarray(apertura_prima_barra, dtype=float)
    E = np.asarray(entry, dtype=float)
    L = np.asarray(long, dtype=bool)
    if not (len(O) == len(E) == len(L)) or len(O) == 0:
        return e.add("ROTTO", "ottenibilita'", "lunghezze incoerenti o campione vuoto")
    gia = np.where(L, O > E, O < E)
    q = float(gia.mean())
    testo = "%d setup su %d gia' oltrepassati (%.1f%%)" % (gia.sum(), len(O), 100 * q)
    if q == 0:
        return e.add("riserva", "ottenibilita'",
                     "NESSUN setup scartato: un ordine che non manca mai non e' un "
                     "ordine. Verifica che il controllo stia guardando la barra giusta")
    if q <= soglia_riserva:
        return e.add("ok", "ottenibilita'", testo + " - dettaglio, ma va dichiarato")
    return e.add("ROTTO", "ottenibilita'",
                 testo + " - il risultato NON misura la regola finche' non si riporta "
                 "anche la variante a soli fill ottenibili (SKIP/LIMIT/RECENTER/LIVE)")


def gap_oltre_stop(apertura: Sequence[float], sl: Sequence[float],
                   long: Sequence[bool]) -> Esito:
    """Quante barre aprono **oltre** lo stop? La' il fill e' `Open`, non lo stop.

    Ignorarlo regala allo stop un prezzo che il mercato non offriva: e' il fill fantasma
    sul lato uscita. ⚠️ Sul FADE NXT vale il **12,7% degli stop** e ha spostato l'E[R]
    pre-registrato da **+0,354 a +0,308**.
    """
    e = Esito("USCITA")
    A = np.asarray(apertura, dtype=float)
    S = np.asarray(sl, dtype=float)
    L = np.asarray(long, dtype=bool)
    if len(A) == 0:
        return e.add("riserva", "gap oltre stop", "nessuno stop nel campione")
    oltre = np.where(L, A < S, A > S)
    q = float(oltre.mean())
    testo = "%d stop su %d aprono oltre il livello (%.1f%%)" % (oltre.sum(), len(A), 100 * q)
    if q == 0:
        return e.add("ok", "gap oltre stop", "nessuno")
    return e.add("riserva", "gap oltre stop",
                 testo + " - il fill deve essere Open, non lo stop "
                 "(core.resolve_trade: gap_beyond_stop=True)")


# ---------------------------------------------------------------------------
def checklist_dati(frames: dict, col: str = "time",
                   barre_attese: Optional[tuple] = None,
                   file_usati: Optional[dict] = None) -> Esito:
    """Tutta la checklist 2 in una chiamata. Si stampa **prima** di calcolare."""
    tot = Esito("CHECKLIST DATI")
    for nome, df in frames.items():
        tot.unisci(monotonia(df, col, nome))
        tot.unisci(duplicati(df, col, nome))
        tot.unisci(barre_per_anno(df, barre_attese, col, nome))
    tot.unisci(copertura_comune(frames, col))
    for nome, path in (file_usati or {}).items():
        tot.unisci(file_piu_completo(path))
    return tot


def checklist_esecuzione(apertura_prima_barra=None, entry=None, long=None,
                         apertura_stop=None, sl=None, long_stop=None) -> Esito:
    """La parte della checklist 3 che si puo' misurare dai dati."""
    tot = Esito("CHECKLIST ESECUZIONE")
    if apertura_prima_barra is not None:
        tot.unisci(fill_ottenibili(apertura_prima_barra, entry, long))
    else:
        tot.add("ROTTO", "ottenibilita'",
                "NON MISURATA - Step 3bis e' un gate: senza questa percentuale non c'e' "
                "verdetto, ne' GO ne' NO-GO")
    if apertura_stop is not None:
        tot.unisci(gap_oltre_stop(apertura_stop, sl, long_stop))
    return tot


def main(argv=None) -> int:
    import sys
    import pandas as pd
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 0
    frames, usati = {}, {}
    for path in argv:
        nome = os.path.basename(path)
        frames[nome] = pd.read_csv(path, parse_dates=["time"])
        usati[nome] = path
    r = checklist_dati(frames, file_usati=usati)
    print(r)
    return 0 if r.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
