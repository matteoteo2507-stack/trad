"""Potenza della famiglia insider (BACKLOG D9), PRIMA di qualunque rendimento dei titoli comprati. 0 trial.

Cosa misura, per ogni variante provvisoria:
1. quanti eventi cadono su membri dell'S&P 500 alla data del deposito, e in quanti blocchi indipendenti;
2. il ritardo fra operazione e deposito (sole date);
3. l'MDE: il rendimento anomalo medio che il test vedrebbe con l'80% di probabilita' (alfa 5% a due code,
   fattore 2,80). Il rumore del test si misura con un nullo **casuale**: stessi giorni d'ingresso, stesso numero di
   titoli, ma titoli estratti a caso fra i membri dell'indice. Nessun rendimento dei titoli degli insider viene letto.

Le definizioni delle varianti sono PROVVISORIE, servono solo a contare: si fissano alla G1 (pre-registrazione).
Limite noto: i titoli comprati dagli insider possono essere piu' volatili della media dell'indice; in quel caso l'MDE
vero e' piu' alto di quello stimato qui.

Dati: data/cache/sp500data/<snapshot>/ (data/scarica_sp500_data.py) e data/cache/sec/form345_mercato.parquet
(data/scarica_sec_form345.py). Uso:
    python -m analysis.insider.potenza
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SNAP = os.path.join(ROOT, "data", "cache", "sp500data", "snapshot-2026-11")
F345 = os.path.join(ROOT, "data", "cache", "sec", "form345_mercato.parquet")
ORIZZONTI = (21, 63)        # giorni di borsa di detenzione
FATTORE = 2.80              # z(0,975) + z(0,80): MDE all'80% di potenza, alfa 5% a due code
N_SORTEGGI = 300
SEME = 42
RUOLI_TOP = re.compile(r"\b(?:CEO|CFO|CHIEF EXECUTIVE|CHIEF FINANCIAL|PRESIDENT)\b", re.I)


def carica_prezzi():
    p = pd.read_parquet(os.path.join(SNAP, "prices.parquet"), columns=["date", "ticker", "adj_close"])
    p = p[p.date >= "2005-01-01"]
    px = p.pivot(index="date", columns="ticker", values="adj_close").sort_index()
    giorni = px.index[px["SPY"].notna()]
    px = px.loc[giorni]
    iv = pd.read_parquet(os.path.join(SNAP, "membership_intervals.parquet"))
    ultimo = giorni.max() + pd.Timedelta(days=1)
    membro = pd.DataFrame(False, index=giorni, columns=px.columns)
    for t, s, e in iv.itertuples(index=False):
        if t in membro.columns:
            membro.loc[(giorni >= s) & (giorni < (ultimo if pd.isna(e) else e)), t] = True
    # niente scambi in quei giorni: non si entra (README del dataset)
    nt = pd.read_csv(os.path.join(SNAP, "no_trade_days.csv"), parse_dates=["date"])
    for t, d in zip(nt.ticker, nt.date):
        if t in membro.columns and d in membro.index:
            membro.loc[d, t] = False
    return px, membro, iv


def mappa_simboli(ev: pd.DataFrame, iv: pd.DataFrame) -> pd.Series:
    """Etichetta del dataset per (simbolo, data del deposito): base dell'etichetta uguale al simbolo e data dentro
    l'intervallo di appartenenza. Restituisce l'etichetta o NaN."""
    iv = iv.assign(base=iv.ticker.str.split("-").str[0].str.upper())
    per_base = {b: g for b, g in iv.groupby("base")}
    out = []
    for sym, d in zip(ev.SYM, ev.FILING_DATE):
        g = per_base.get(sym)
        lab = np.nan
        if g is not None:
            ok = g[(g.start <= d) & (g.end.isna() | (g.end > d))]
            if len(ok):
                lab = ok.ticker.iloc[0]
        out.append(lab)
    return pd.Series(out, index=ev.index)


def varianti(f: pd.DataFrame) -> dict:
    """Eventi (emittente, data del deposito) per variante. Definizioni provvisorie."""
    p = f[(f.TRANS_CODE == "P") & (f.DOCUMENT_TYPE == "4") & (f.TRANS_SHARES > 0) & (f.TRANS_PRICEPERSHARE > 0)]
    out = {"tutti": p}
    out["I-c ruolo (CEO/CFO/President)"] = p[p.RPTOWNER_TITLE.fillna("").str.contains(RUOLI_TOP)]
    # I-b: almeno 3 insider diversi in 30 giorni di calendario; un evento per emittente ogni 90 giorni
    righe = []
    for cik, g in p.sort_values("FILING_DATE").groupby("ISSUERCIK"):
        ultimo = None
        date, own = g.FILING_DATE.to_numpy(), g.RPTOWNERCIK.to_numpy()
        for i in range(len(g)):
            fin = (date >= date[i] - np.timedelta64(30, "D")) & (date <= date[i])
            if len(set(own[fin])) >= 3 and (ultimo is None or date[i] - ultimo > np.timedelta64(90, "D")):
                righe.append(g.index[i])
                ultimo = date[i]
    out["I-b gruppo (>=3 in 30 g)"] = p.loc[righe]
    # I-a (Cohen-Malloy-Pomorski, provvisoria): insider che ha operato (P o S) in ciascuno dei 3 anni precedenti;
    # "di routine" se in quei 3 anni ha operato sempre nello stesso mese di calendario; gli altri sono opportunistici
    tutte = f[f.TRANS_CODE.isin(["P", "S"])].dropna(subset=["TRANS_DATE"])
    storia = tutte.assign(anno=tutte.TRANS_DATE.dt.year, mese=tutte.TRANS_DATE.dt.month)
    mesi = storia.groupby(["RPTOWNERCIK", "anno"]).mese.agg(lambda s: set(s)).to_dict()
    opp = []
    for i, (own, d) in enumerate(zip(p.RPTOWNERCIK, p.TRANS_DATE)):
        if pd.isna(d):
            continue
        prec = [mesi.get((own, d.year - k)) for k in (1, 2, 3)]
        if any(m is None for m in prec):
            continue
        if not (d.month in prec[0] and d.month in prec[1] and d.month in prec[2]):
            opp.append(p.index[i])
    out["I-a opportunistici"] = p.loc[opp]
    return out


def eventi_unici(p: pd.DataFrame) -> pd.DataFrame:
    return p.sort_values("FILING_DATE").drop_duplicates(["ISSUERCIK", "FILING_DATE"])


def mde(ev: pd.DataFrame, px, membro, H: int, rng) -> dict:
    """Nullo casuale: per ogni evento, un titolo a caso fra i membri dello stesso giorno d'ingresso. Statistica: media
    sui blocchi di H giorni della media del rendimento anomalo (titolo meno media equipesata dei membri)."""
    giorni = px.index
    pos = giorni.searchsorted(ev.FILING_DATE.to_numpy(), side="right")      # ingresso: giorno dopo il deposito
    pos = pos[(pos + H) < len(giorni)]
    r = px.shift(-H).to_numpy() / px.to_numpy() - 1.0
    m = membro.to_numpy() & np.isfinite(r)
    blocco = pos // H
    valide = [i for i in range(len(pos)) if m[pos[i]].any()]
    pos, blocco = pos[valide], blocco[valide]
    if len(pos) == 0:
        return {}
    cand = {d: np.flatnonzero(m[d]) for d in np.unique(pos)}
    mkt = {d: np.nanmean(r[d, cand[d]]) for d in cand}
    ub, inv = np.unique(blocco, return_inverse=True)
    T = []
    for _ in range(N_SORTEGGI):
        ab = np.array([r[d, rng.choice(cand[d])] - mkt[d] for d in pos])
        T.append(np.bincount(inv, ab).__truediv__(np.bincount(inv)).mean())
    se = float(np.std(T, ddof=1))
    return {"eventi": len(pos), "blocchi": len(ub), "se": se, "mde": FATTORE * se}


def main() -> int:
    if not os.path.exists(F345):
        sys.exit("manca %s: lancia data/scarica_sec_form345.py" % F345)
    px, membro, iv = carica_prezzi()
    f = pd.read_parquet(F345)
    f = f[f.FILING_DATE >= "2006-01-01"]
    f["SYM"] = f.ISSUERTRADINGSYMBOL.fillna("").str.upper().str.strip().str.replace(".", "-", regex=False)
    rng = np.random.default_rng(SEME)
    print("Potenza insider — %s — snapshot %s — 0 trial" % (pd.Timestamp.today().date(), os.path.basename(SNAP)))
    for nome, p in varianti(f).items():
        ev = eventi_unici(p).copy()
        ev["LAB"] = mappa_simboli(ev, iv)
        tot = len(ev)
        ev = ev.dropna(subset=["LAB"])
        rit = (ev.FILING_DATE - ev.TRANS_DATE).dt.days
        print("\n== %s: %d eventi, %d su membri S&P 500 alla data (%.0f%%)"
              % (nome, tot, len(ev), 100 * len(ev) / max(tot, 1)))
        print("   ritardo operazione -> deposito, giorni: mediana %.0f, 90° perc. %.0f, oltre 30: %.1f%%"
              % (rit.median(), rit.quantile(0.9), 100 * (rit > 30).mean()))
        print("   eventi per anno: %s" % ev.FILING_DATE.dt.year.value_counts().sort_index().to_dict())
        for H in ORIZZONTI:
            x = mde(ev, px, membro, H, rng)
            if x:
                print("   H=%d g: %d eventi in %d blocchi indipendenti; errore standard %.3f%%, MDE %.2f%%"
                      % (H, x["eventi"], x["blocchi"], 100 * x["se"], 100 * x["mde"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
