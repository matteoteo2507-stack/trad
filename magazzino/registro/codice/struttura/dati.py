"""Dati di I3: scaricatore degli 8 strumenti nuovi, loader, sedute e griglia di 27 prezzi (referto §3, §7, §10). 0 trial.

- **Scaricatore** (`python dati.py --scarica`): gli 8 strumenti nuovi da Dukascopy M5, lato bid. **Riscritto**, non
  importato, da `volatilita/scarica_dukascopy.py` (stessa libreria e stesso formato; quello usa la data di oggi e salta
  gli anni in errore): **date fisse**, guardie in testa, e un anno che va in errore si riprova 3 volte e poi **ferma lo
  strumento** (nessun buco silenzioso; un anno vuoto prima della quotazione non e' un errore). Date: dal 2012-01-01 al
  2026-11-11 00:00 UTC escluso, quindi l'ultima barra e' del 2026-11-10. Scrive in `motore/data/prezzi/struttura_m5/`
  (fuori da git) e **rifiuta se il file esiste**. Stampa solo il numero di barre per anno. Poi
  `python dati.py --registra` scrive una volta sola `hash_dati.json` (sha256 e byte; rifiuta se esiste).
- **Loader**: legge fino a `TAGLIO_UTC` escluso, fermandosi al primo blocco oltre (i 9 file della volatilita' arrivano
  all'11/11: le barre dell'11 stanno nell'ultimo blocco letto, vengono scartate subito e non entrano in nessun oggetto
  restituito); la potenza e il controllo di selezione passano
  `fino_a = TAGLIO_SVILUPPO_UTC` (sedute fino al 2024-11-08).
- **Fuso**: `a_new_york` aggiunge una colonna con l'ora di New York una volta sola e si ferma se e' gia' stata
  aggiunta (una correzione, un proprietario).
- **Sedute**: le sedute XNYS piene (9:30-16:00); le chiusure anticipate si contano e **non entrano nell'indice**.
- **Griglia**: per ogni seduta 27 log-prezzi (l'open della barra delle 9:30 e la chiusura delle barre che iniziano alle
  :10, :25, :40, :55) e la presenza delle 78 barre M5 della seduta (per le pause).
- **Intervalli interrotti**: un intervallo a 15 minuti e' interrotto se una sua barra interna manca in un **orario di
  pausa** dello strumento per quell'anno (barra assente in piu' della meta' delle sedute presenti dell'anno, regola
  proposta da Claude il 27/11, dal controllo di struttura) o se contiene un **rollover** dentro la seduta. Si applicano
  solo in `misura.rendimenti`.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import guardie as G  # noqa: E402

ROOT = G.ROOT
NY = "America/New_York"
TAGLIO_UTC = pd.Timestamp("2026-11-11 00:00")
TAGLIO_SVILUPPO_UTC = pd.Timestamp("2024-11-09 00:00")
FINE = pd.Timestamp("2026-11-10")
FINE_SVILUPPO = pd.Timestamp("2024-11-08")
INIZIO_BLOCCO = pd.Timestamp("2024-11-11")
INIZIO_SCARICO = dt.datetime(2012, 1, 1, tzinfo=dt.timezone.utc)
FINE_SCARICO = dt.datetime(2026, 11, 11, tzinfo=dt.timezone.utc)
N_PREZZI = 27
N_BARRE = 78
SOGLIA_PAUSA = 0.5


class FusoGiaApplicato(RuntimeError):
    pass


# ---------------------------------------------------------------- scaricatore

def codici() -> dict:
    import dukascopy_python.instruments as ins

    return {"BUND": ins.INSTRUMENT_BND_CFD_BUND_TR_EUR, "USTBOND": ins.INSTRUMENT_BND_CFD_USTBOND_TR_USD,
            "USDJPY": ins.INSTRUMENT_FX_MAJORS_USD_JPY, "GBPUSD": ins.INSTRUMENT_FX_MAJORS_GBP_USD,
            "AUDUSD": ins.INSTRUMENT_FX_MAJORS_AUD_USD, "COPPER": ins.INSTRUMENT_CMD_METALS_COPPER_CMD_USD,
            "NATGAS": ins.INSTRUMENT_CMD_ENERGY_GAS_CMD_USD, "BTCUSD": ins.INSTRUMENT_VCCY_BTC_USD}


def _fetch(dk, codice, da, a, nome, anno, tentativi: int = 3):
    for k in range(tentativi):
        try:
            return dk.fetch(codice, dk.INTERVAL_MIN_5, dk.OFFER_SIDE_BID, da, a)
        except Exception as e:  # noqa: BLE001
            print("  %s %d: tentativo %d fallito (%s)" % (nome, anno, k + 1, type(e).__name__), flush=True)
    raise G.GuardiaFallita("%s %d: scarico fallito dopo %d tentativi, strumento fermo" % (nome, anno, tentativi))


def scarica(nome: str) -> None:
    import dukascopy_python as dk

    dest = ROOT / G.DATI[nome]
    if dest.exists():
        raise G.GuardiaFallita("%s esiste: non si riscarica" % nome)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pezzi = []
    for anno in range(INIZIO_SCARICO.year, FINE_SCARICO.year + 1):
        da = dt.datetime(anno, 1, 1, tzinfo=dt.timezone.utc)
        a = min(dt.datetime(anno + 1, 1, 1, tzinfo=dt.timezone.utc), FINE_SCARICO)
        df = _fetch(dk, codici()[nome], da, a, nome, anno)
        n = 0 if df is None else len(df)
        print("  %s %d: %d barre" % (nome, anno, n), flush=True)
        if n:
            pezzi.append(df)
        elif pezzi:
            raise G.GuardiaFallita("%s %d: anno vuoto dopo l'inizio della quotazione, strumento fermo" % (nome, anno))
    if not pezzi:
        raise G.GuardiaFallita("%s: nessun dato" % nome)
    tutto = pd.concat(pezzi)
    tutto = tutto[~tutto.index.duplicated(keep="last")].sort_index().rename_axis("time").reset_index()
    tutto["time"] = pd.to_datetime(tutto["time"], utc=True).dt.tz_localize(None)
    tutto = tutto[tutto["time"] < pd.Timestamp(FINE_SCARICO.replace(tzinfo=None))]
    tutto = tutto[["time", "open", "high", "low", "close", "volume"]]
    tmp = dest.with_suffix(".tmp")
    tutto.to_csv(tmp, index=False)
    os.replace(tmp, dest)
    print("%s: %d barre" % (nome, len(tutto)), flush=True)


def registra() -> None:
    """Registra sha256 e byte degli 8 nuovi, una volta sola, dopo aver controllato l'ultima data di ogni file."""
    if G.HASH_I3.exists():
        raise G.GuardiaFallita("%s esiste: non si riscrive" % G.HASH_I3.name)
    g = G.verifica(dati=False)
    righe = {"nota": "sha256 e byte degli 8 strumenti nuovi di I3, registrati una volta sola dopo lo scarico "
                     "(referto del passo 2, requisiti del commit (1), punto 2).",
             "commit": g["commit"], "versioni": g["versioni"], "percorsi": {}, "byte": {}, "sha256": {}}
    for n in G.NUOVI:
        p = ROOT / G.DATI[n]
        if G.ultima_data(p) > G.ULTIMO_GIORNO_NUOVI:
            raise G.GuardiaFallita("%s: barre oltre il %s" % (n, G.ULTIMO_GIORNO_NUOVI))
        righe["percorsi"][n] = G.DATI[n]
        righe["byte"][n] = os.path.getsize(p)
        righe["sha256"][n] = G.sha256(p)
    import json

    tmp = G.HASH_I3.with_suffix(".tmp")
    tmp.write_text(json.dumps(righe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, G.HASH_I3)


# ---------------------------------------------------------------- loader

def leggi_barre(nome: str, fino_a: pd.Timestamp | None = None, percorso: Path | None = None) -> pd.DataFrame:
    """Barre M5 (ora d'inizio UTC senza fuso, open, close) fino a `fino_a` escluso; si ferma al primo blocco oltre."""
    fino_a = TAGLIO_UTC if fino_a is None else pd.Timestamp(fino_a)
    if fino_a > TAGLIO_UTC:
        raise PermissionError("lettura oltre %s rifiutata" % TAGLIO_UTC)
    percorso = ROOT / G.DATI[nome] if percorso is None else percorso
    pezzi = []
    for blocco in pd.read_csv(percorso, usecols=["time", "open", "close"], chunksize=200_000):
        blocco["time"] = pd.to_datetime(blocco["time"])
        dentro = blocco[blocco["time"] < fino_a]
        pezzi.append(dentro)
        if len(dentro) < len(blocco):
            break
    df = pd.concat(pezzi, ignore_index=True)
    if df["time"].dt.tz is not None:
        raise ValueError("%s: tempi con fuso nel file (attesi UTC senza fuso)" % nome)
    if not df["time"].is_monotonic_increasing or df["time"].duplicated().any():
        raise ValueError("%s: tempi non ordinati o duplicati" % nome)
    return df


def a_new_york(barre: pd.DataFrame) -> pd.DataFrame:
    """Aggiunge `ny` (ora d'inizio a New York, senza fuso) una volta sola; si ferma se c'e' gia'."""
    if "ny" in barre.columns:
        raise FusoGiaApplicato("fuso di New York gia' applicato")
    out = barre.copy()
    out["ny"] = out["time"].dt.tz_localize("UTC").dt.tz_convert(NY).dt.tz_localize(None)
    return out


def sedute(inizio, fine) -> tuple[pd.DatetimeIndex, int]:
    """Sedute XNYS piene (9:30-16:00 di New York) in [inizio, fine] e numero di chiusure anticipate tolte."""
    import exchange_calendars as xc

    sched = xc.get_calendar("XNYS").schedule.loc[pd.Timestamp(inizio):pd.Timestamp(fine)]
    ap = sched["open"].dt.tz_convert(NY)
    ch = sched["close"].dt.tz_convert(NY)
    piena = (ap.dt.hour == 9) & (ap.dt.minute == 30) & (ch.dt.hour == 16) & (ch.dt.minute == 0)
    return pd.DatetimeIndex(sched.index[piena.to_numpy()]), int((~piena).sum())


def griglia(barre_ny: pd.DataFrame, giorni: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
    """(P, presenti): P[t, k] log-prezzo (NaN se manca), presenti[t, m] barra M5 m della seduta (m = 0..77)."""
    if "ny" not in barre_ny.columns:
        raise ValueError("serve la colonna `ny` (a_new_york)")
    ny = barre_ny["ny"]
    minuti = ny.dt.hour * 60 + ny.dt.minute
    dentro = (minuti >= 570) & (minuti < 960)
    b = barre_ny[dentro.to_numpy()]
    b = b[~b["ny"].duplicated(keep="first")].set_index("ny")
    offs = pd.to_timedelta(570 + 5 * np.arange(N_BARRE), unit="min")
    tempi = pd.DatetimeIndex((np.asarray(giorni, "datetime64[ns]")[:, None] + offs.to_numpy()[None, :]).ravel())
    ap = b["open"].reindex(tempi).to_numpy().reshape(len(giorni), N_BARRE)
    ch = b["close"].reindex(tempi).to_numpy().reshape(len(giorni), N_BARRE)
    presenti = np.isfinite(ch)
    P = np.full((len(giorni), N_PREZZI), np.nan)
    P[:, 0] = ap[:, 0]
    P[:, 1:] = ch[:, 3 * np.arange(1, N_PREZZI) - 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.where(P > 0, np.log(P), np.nan)
    return P, presenti


def orari_di_pausa(presenti: np.ndarray, anni: np.ndarray) -> np.ndarray:
    """pausa[t, m]: la barra m e' un orario di pausa nell'anno della seduta t (assente in piu' della meta' delle sedute
    presenti di quell'anno). Solo presenze di barre: nessun prezzo."""
    pausa = np.zeros_like(presenti, bool)
    seduta_presente = presenti.any(axis=1)
    for a in np.unique(anni):
        sel = (anni == a) & seduta_presente
        if sel.any():
            pausa[anni == a] = (~presenti[sel]).mean(axis=0) > SOGLIA_PAUSA
    return pausa


def interrotti(presenti: np.ndarray, pausa: np.ndarray, giorni: pd.DatetimeIndex, rollover=()) -> np.ndarray:
    """it[t, j] per i 26 intervalli a 15 minuti: una barra interna (le due barre prima di quella che chiude
    l'intervallo) manca in un orario di pausa, o un rollover (ora di New York) cade dentro l'intervallo."""
    T = presenti.shape[0]
    j = np.arange(N_PREZZI - 1)
    interne = np.stack([3 * j, 3 * j + 1], axis=1)                   # barre m interne all'intervallo j
    manca_in_pausa = (~presenti) & pausa
    it = manca_in_pausa[:, interne].any(axis=2)
    pos = {d: t for t, d in enumerate(pd.DatetimeIndex(giorni).normalize())}
    for r in rollover:
        r = pd.Timestamp(r)
        t = pos.get(r.normalize())
        m = (r.hour * 60 + r.minute - 570) // 15
        if t is not None and 0 <= m < N_PREZZI - 1:
            it[t, m] = True
    return it


if __name__ == "__main__":
    if "--scarica" in sys.argv:
        nomi = [a for a in sys.argv[1:] if not a.startswith("--")] or list(G.NUOVI)
        for n in nomi:
            if n not in G.NUOVI:
                raise SystemExit("%s non e' fra gli 8 nuovi" % n)
        G.protetto(lambda: (G.verifica(dati=False), G.richiedi("verifica_fonti.md")))   # §10: fonti prima
        for n in nomi:
            G.protetto(lambda n=n: scarica(n))
    elif "--registra" in sys.argv:
        G.protetto(registra)
        print("registrato", G.HASH_I3.relative_to(ROOT))
    else:
        print(__doc__)
