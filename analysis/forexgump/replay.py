"""Motore di replay di Forex Gump: il segnale come lo esegue il copier (pre-registrazione §4-§5).

`docs/FOREXGUMP_LATENCY_PREREGISTRATION.md` e' il contratto: questo file non decide nulla che non sia
scritto li'. Il motore **non si lancia sui segnali** finche' la pre-registrazione non e' approvata e
registrata nel ledger; prima si usa solo per l'MDE su istanti casuali (`mde_istanti_casuali`).

Esecuzione primaria (§4):
- istante azionabile = messaggio + L (10 s);
- fill al primo tick >= istante azionabile: buy all'ASK, sell al BID. Senza tick, ripiego sull'apertura
  della prima barra M1 che inizia >= istante (lo stesso lato), e la sorgente si registra;
- SKIP se lo spread al fill >= distanza dello SL: il broker rifiuterebbe gli stop (invalid stops);
- bracket RICENTRATO sul fill alle distanze postate; bracket puro, nessuna gestione;
- uscita: buy sul BID, sell sull'ASK. Tick per i primi 60 minuti (niente pareggi), poi barre M1 con
  pareggio pessimistico; troncamento a 24 ore di CALENDARIO dal fill, chiusura marcata;
- R = (uscita - fill) / distanza SL postata, meno commissione (0,07 $/oncia andata e ritorno);
- stress: spread x1,5, commissione x3, 0,10 $ di slittamento per lato, swap 0,10 $/oncia per rollover.

Baseline appaiato (§5): a ogni istante si simulano ENTRAMBI i lati; d = (R_mentore - R_opposto) / 2.
CI: bootstrap percentile per GIORNATA DI TRADING (inizia alle 22:00 UTC), 10.000 ricampionamenti.

Varianti descrittive (§5, 0 trial): `variante="live"` (livelli postati assoluti, r_unit = |fill - SL|),
`"limit"` (limite al prezzo postato, attesa 15 minuti), `"postato"` (NON OTTENIBILE: solo per il costo del
ritardo), `"skip1"` (salta se lo scostamento sfavorevole a
t+L supera 1 $), latenza come parametro.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from core.resolve_trade import PESSIMISTA, OTTIMISTA, resolve_trade  # noqa: E402,F401

L_SEC = 10
FINESTRA_TICK = pd.Timedelta(minutes=60)
TIMEOUT = pd.Timedelta(hours=24)
COMMISSIONE = 0.07          # $/oncia andata e ritorno
STRESS = {"spread": 1.5, "commissione": 3.0, "slittamento": 0.10, "swap": 0.10}
ATTESA_LIMIT = pd.Timedelta(minutes=15)
RITARDO_MAX_FILL = pd.Timedelta(seconds=60)   # fill entro 60 s da t+L, per tick e M1 allo stesso modo (G1 #2, B2)
SOGLIA_SKIP1 = 1.0          # $ di scostamento sfavorevole oltre cui la variante skip1 non entra


@dataclass
class Prezzi:
    """Accesso ai prezzi. `m1_bid`/`m1_ask`: barre M1 (indice UTC tz-naive, inizio barra).
    `tick`: funzione (t0, t1) -> DataFrame con colonne bidPrice/askPrice e indice UTC tz-naive,
    oppure None se i tick non ci sono (si ripiega sulle M1)."""

    m1_bid: pd.DataFrame
    m1_ask: pd.DataFrame
    tick: object = None
    _idx: pd.DatetimeIndex = field(init=False, repr=False)

    def __post_init__(self):
        self._idx = self.m1_bid.index

    def ticks(self, t0, t1) -> pd.DataFrame | None:
        if self.tick is None:
            return None
        df = self.tick(t0, t1)
        return df if df is not None and len(df) else None

    def m1(self, t0, t1, lato_prezzo: str) -> pd.DataFrame:
        """Barre con inizio in [t0, t1). Indice ordinato: ricerca binaria, non scansione."""
        src = self.m1_bid if lato_prezzo == "bid" else self.m1_ask
        i0, i1 = src.index.searchsorted(t0, "left"), src.index.searchsorted(t1, "left")
        return src.iloc[i0:i1]


def giorno_trading(t: pd.Timestamp) -> pd.Timestamp:
    """Giornata di trading con rollover alle 22:00 UTC: 22:00 di lunedi' -> martedi'."""
    return (t + pd.Timedelta(hours=2)).normalize()


def _rollover(t0: pd.Timestamp, t1: pd.Timestamp) -> int:
    """Quante volte l'intervallo (t0, t1] attraversa le 22:00 UTC."""
    if t1 <= t0:
        return 0
    return int((giorno_trading(t1) - giorno_trading(t0)).days)


def esegui(prezzi: Prezzi, t_msg: pd.Timestamp, long: bool, dist_sl: float, dist_tp: float, *,
           entry_post: float | None = None, L: float = L_SEC, variante: str = "recenter",
           stress: bool = False, conv=PESSIMISTA, k_spread: float | None = None) -> dict:
    """Esegue UN lato di un segnale. Ritorna sempre un dict con `esito`; `r` e' None se non eseguito."""
    if k_spread is None:
        k_spread = STRESS["spread"] if stress else 1.0   # 0,5 = variante descrittiva a meta' spread
    slip = STRESS["slittamento"] if stress else 0.0
    comm = COMMISSIONE * (STRESS["commissione"] if stress else 1.0)
    t_az = t_msg + pd.Timedelta(seconds=L)

    # --- fill -----------------------------------------------------------------------------
    # I tick arrivano solo se la finestra e' COMPLETA (il fornitore restituisce None se manca un'ora):
    # cosi' un trade e' tutto su tick o tutto su M1, mai con un buco in mezzo (G1 #2, B2).
    tk = prezzi.ticks(t_az - pd.Timedelta(minutes=1), t_az + FINESTRA_TICK + pd.Timedelta(minutes=16))
    sorgente = "tick"
    if tk is not None:
        tk_dopo = tk[(tk.index >= t_az) & (tk.index <= t_az + RITARDO_MAX_FILL)]
        if not len(tk_dopo):
            return {"esito": "NON_ESEGUITO", "r": None, "sorgente_fill": "tick"}
        t_fill, bid0, ask0 = tk_dopo.index[0], float(tk_dopo.bidPrice.iloc[0]), float(tk_dopo.askPrice.iloc[0])
    else:
        sorgente = "m1"
        b = prezzi.m1(t_az, t_az + pd.Timedelta(minutes=30), "bid")
        a = prezzi.m1(t_az, t_az + pd.Timedelta(minutes=30), "ask")
        if not len(b) or not len(a):
            return {"esito": "SENZA_PREZZI", "r": None, "sorgente_fill": "m1"}
        if b.index[0] > t_az + RITARDO_MAX_FILL:
            return {"esito": "NON_ESEGUITO", "r": None, "sorgente_fill": "m1"}
        t_fill, bid0, ask0 = b.index[0], float(b.open.iloc[0]), float(a.open.iloc[0])
    spread_reale = ask0 - bid0
    mid0, spread0 = (bid0 + ask0) / 2, spread_reale * k_spread
    fill = mid0 + spread0 / 2 + slip if long else mid0 - spread0 / 2 - slip
    out = {"t_fill": t_fill, "fill": fill, "spread": spread0, "spread_reale": spread_reale,
           "sorgente_fill": sorgente}
    if entry_post is not None:
        # Step 3bis: il prezzo postato era gia' superato in senso sfavorevole all'istante azionabile?
        out["scarto_postato"] = (fill - entry_post) if long else (entry_post - fill)

    # --- livelli secondo la variante ------------------------------------------------------
    if variante in ("recenter", "skip1"):
        if variante == "skip1" and out.get("scarto_postato", 0.0) > SOGLIA_SKIP1:
            return {**out, "esito": "SKIP_SCARTO", "r": None}
        sl = fill - dist_sl if long else fill + dist_sl
        tp = fill + dist_tp if long else fill - dist_tp
        r_unit = dist_sl
    elif variante == "live":
        if entry_post is None:
            raise ValueError("la variante live richiede entry_post")
        sl = entry_post - dist_sl if long else entry_post + dist_sl
        tp = entry_post + dist_tp if long else entry_post - dist_tp
        r_unit = abs(fill - sl)
        # lo stop si confronta col prezzo d'USCITA (BID per un long, ASK per uno short) (G1 #2, R7)
        if (long and bid0 <= sl) or (not long and ask0 >= sl):
            return {**out, "esito": "SKIP_OLTRE_SL", "r": None}
    elif variante == "postato":
        # NON OTTENIBILE (§5): fill al prezzo postato, come presumibilmente fa la webapp. Serve solo a
        # misurare il costo del ritardo (differenza col primario); non si cita mai come risultato.
        if entry_post is None:
            raise ValueError("la variante postato richiede entry_post")
        fill = float(entry_post)
        out.update(fill=fill)
        sl = entry_post - dist_sl if long else entry_post + dist_sl
        tp = entry_post + dist_tp if long else entry_post - dist_tp
        r_unit = dist_sl
    elif variante == "limit":
        if entry_post is None or tk is None:
            return {**out, "esito": "SENZA_TICK_LIMIT", "r": None}
        attesa = tk[(tk.index >= t_az) & (tk.index <= t_az + ATTESA_LIMIT)]
        prezzo_ingresso = attesa.askPrice if long else attesa.bidPrice
        ok = (prezzo_ingresso <= entry_post) if long else (prezzo_ingresso >= entry_post)
        if not ok.any():
            return {**out, "esito": "LIMIT_NON_ESEGUITO", "r": None}
        t_fill, fill = ok.idxmax(), float(entry_post)
        out.update(t_fill=t_fill, fill=fill)
        sl = entry_post - dist_sl if long else entry_post + dist_sl
        tp = entry_post + dist_tp if long else entry_post - dist_tp
        r_unit = dist_sl
    else:
        raise ValueError(f"variante sconosciuta: {variante}")

    # SKIP deciso sullo spread REALE, non su quello di stress: base e stress sullo stesso campione (R2)
    if variante in ("recenter", "skip1") and spread_reale >= dist_sl:
        return {**out, "esito": "SKIP_SPREAD", "r": None}

    # --- serie d'uscita: tick per un'ora, poi M1, troncata a 24 ore di calendario -----------
    # Prezzo d'uscita = mid -/+ spread*k/2 (long esce sul BID, short sull'ASK). Nel caso base (k = 1)
    # coincide con BID/ASK. Lo slittamento d'uscita NON sposta la serie (spostava anche il trigger del TP):
    # e' un costo esplicito su ogni uscita che non e' TP, sotto (G1 #2, R1).
    def _uscita(bid, ask):
        mid, sp = (bid + ask) / 2, (ask - bid) * k_spread
        return (mid - sp / 2) if long else (mid + sp / 2)

    fine_tick, fine = t_fill + FINESTRA_TICK, t_fill + TIMEOUT
    t_seq, O, H, L_, C = [], [], [], [], []
    inizio_m1 = t_fill
    if tk is not None:
        inizio_m1 = fine_tick.ceil("min")      # i tick arrivano fino all'inizio della prima M1: nessun buco
        tt = tk[(tk.index >= t_fill) & (tk.index < inizio_m1)]
        px = list(_uscita(tt.bidPrice, tt.askPrice))
        t_seq, O, H, L_, C = list(tt.index), px[:], px[:], px[:], px[:]
    b = prezzi.m1(inizio_m1, fine, "bid")
    a = prezzi.m1(inizio_m1, fine, "ask")
    comune = b.index.intersection(a.index)
    b, a = b.loc[comune], a.loc[comune]
    for lista, col in ((O, "open"), (H, "high"), (L_, "low"), (C, "close")):
        lista.extend(list(_uscita(b[col], a[col])))
    t_seq.extend(list(comune))
    if not O:
        return {**out, "esito": "SENZA_PREZZI", "r": None}

    res = resolve_trade(O, H, L_, C, 0, fill=fill, sl=sl, tp=tp, long=long, r_unit=r_unit,
                        max_hold=len(O), cost_R=comm / r_unit, conv=conv)
    if res is None:
        return {**out, "esito": "NON_RISOLTO", "r": None}
    t_uscita = t_seq[min(res.bars_held, len(t_seq) - 1)]
    swap = (STRESS["swap"] if stress else 0.0) * _rollover(t_fill, t_uscita) / r_unit
    slip_uscita = slip / r_unit if res.outcome != "TP" else 0.0     # un TP e' un limite: niente slittamento
    return {**out, "esito": res.outcome, "r": res.r - swap - slip_uscita, "t_uscita": t_uscita,
            "rollover": _rollover(t_fill, t_uscita), "r_unit": r_unit}


def esegui_appaiato(prezzi: Prezzi, t_msg, lato_mentore_long: bool, dist_sl: float, dist_tp: float,
                    **kw) -> dict:
    """Entrambi i lati allo stesso istante (§5). d = (R_mentore - R_opposto) / 2.

    Solo per l'esecuzione PRIMARIA (variante "recenter", anche sotto stress, con latenza o convenzione
    diverse). Le varianti descrittive si simulano solo sul lato del mentore con `esegui`: per il lato
    opposto non esiste un prezzo postato (G1 #2, B1: chiamarla con "postato" o "live" mandava in errore
    lo script d'esecuzione unica a meta' corsa).
    """
    if kw.get("variante", "recenter") != "recenter":
        raise ValueError("esegui_appaiato vale solo per la variante primaria 'recenter'")
    m = esegui(prezzi, t_msg, lato_mentore_long, dist_sl, dist_tp, **kw)
    kw_o = {k: v for k, v in kw.items() if k != "entry_post"}
    o = esegui(prezzi, t_msg, not lato_mentore_long, dist_sl, dist_tp, **kw_o)
    d = (m["r"] - o["r"]) / 2 if m["r"] is not None and o["r"] is not None else None
    return {"mentore": m, "opposto": o, "d": d}


def ci_cluster_giorno(valori, giorni, n_boot: int = 10_000, conf: float = 0.95, seed: int = 42) -> dict:
    """CI percentile della media, ricampionando GIORNATE di trading (§5): metrica = somma / numero."""
    df = pd.DataFrame({"v": np.asarray(valori, float), "g": list(giorni)}).dropna()
    per_g = df.groupby("g")["v"].agg(["sum", "count"])
    s, c = per_g["sum"].to_numpy(), per_g["count"].to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(s), (n_boot, len(s)))
    medie = s[idx].sum(axis=1) / c[idx].sum(axis=1)
    a = (1 - conf) / 2
    return {"media": float(df.v.mean()), "low": float(np.quantile(medie, a)),
            "high": float(np.quantile(medie, 1 - a)), "se": float(medie.std(ddof=1)),
            "n": int(len(df)), "giorni": int(len(s))}
