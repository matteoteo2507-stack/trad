"""ESECUZIONE UNICA del test pre-registrato Forex Gump (`docs/FOREXGUMP_LATENCY_PREREGISTRATION.md`).

⚠️ Si lancia UNA volta sola, dopo l'approvazione. La GUARDIA si rifiuta di partire se:
- il frontmatter della pre-registrazione non ha `stato: APPROVATA`;
- la famiglia `forexgump_signals` non e' nel ledger, oppure il suo `holdout_aperto` NON e' vuoto
  (una seconda esecuzione e' vietata da D1), oppure il referto di oggi esiste gia';
- mancano ore di tick o ci sono scarichi falliti (`export_tick.py --conta` deve dire 0 da scaricare);
- l'allineamento del fuso (`carica.verifica`) e' sotto il 95%.
Superata la guardia, l'holdout si registra come APERTO nel ledger PRIMA di calcolare, e il referto si
scrive un pezzo alla volta in `docs/reviews/forexgump_esito_<data>.md` (G1 #2, B1: un errore a meta' non
deve lasciare l'holdout aperto senza referto).

`--ripresa AAAA-MM-GG`: SOLO se l'esecuzione unica si e' interrotta dopo l'apertura dell'holdout (procedura
§0bis, da confermare da Matteo). Ammessa solo se `holdout_aperto` e' GIA' pieno e in DECISIONS.md esiste una
voce `## AAAA-MM-GG ...` che contiene "ripresa" e "Gump", scritta prima del rilancio. Non cancella nulla:
il referto parziale resta, il nuovo va in `forexgump_esito_<data>_ripresa.md`. Una ripresa sola.

`--prova-a-secco`: nessuna guardia, nessun segnale toccato. Gira lo STESSO codice su istanti SPOSTATI
(giornate spostate in blocco come in `potenza.py`), su un sottoinsieme, e scrive nella scratchpad. Serve a
dimostrare che l'esecuzione unica arriva in fondo (richiesto dalla G1 #2).

Cosa calcola, nell'ordine della pre-registrazione: kill sui dati; primario (d ed E[R], L = 10 s,
pessimistica, base e stress, CI a cluster per giornata, ottimistica accanto); diagnostica Step 3bis; verdetto
meccanico §6 con l'MDE pre-registrato (0,130R) e quello osservato; controlli (per lato, stesso lato a istante
casuale con `check_matching`, holding dei tre bracci, quota oltre il rollover); descrittive (latenza, LIVE,
LIMIT, SKIP1, meta' spread, anno, categoria, finestra post-cutoff, spiegazione noiosa).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
from analysis.forexgump import replay as rp  # noqa: E402
from analysis.forexgump.carica import DATA, carica_m1, carica_segnali, verifica  # noqa: E402
from core.random_baseline import check_matching  # noqa: E402
from core.resolve_trade import OTTIMISTA, PESSIMISTA  # noqa: E402
from core.verifiche import fattore_potenza  # noqa: E402

PREREG = os.path.join(ROOT, "docs", "FOREXGUMP_LATENCY_PREREGISTRATION.md")
LEDGER = os.path.join(ROOT, "docs", "trial_ledger.json")
TICK_DIR = os.path.join(DATA, "_duka_xau_tick_ore")
FAMIGLIA = "forexgump_signals"
SEED = 42
KILL = 0.10
LATENZE = (0, 5, 10, 30, 60, 300)
MDE_PREREGISTRATO = 0.130          # §6, potenza.py del 02/10: e' quello che va accanto al verdetto
CATEGORIE = ("hedging", "just_for_fun", "appesantimento", "last", "didattica", "bonus")
SPOSTAMENTI = [k for k in range(-20, 21) if k != 0]


# ---- guardia --------------------------------------------------------------------------------

def guardia_ripresa(referto: str, data_voce: str) -> None:
    """Rilancio dopo un'interruzione: l'apertura resta registrata, la ripresa deve essere gia' in DECISIONS."""
    fam = {f["id"]: f for f in json.load(open(LEDGER, encoding="utf-8"))["famiglie"]}
    if FAMIGLIA not in fam or not fam[FAMIGLIA].get("holdout_aperto"):
        sys.exit("GUARDIA RIPRESA: l'holdout non risulta aperto: non c'e' nulla da riprendere, usa l'esecuzione normale.")
    dec = open(os.path.join(ROOT, "DECISIONS.md"), encoding="utf-8").read().split("\n")
    voci = [r for r in dec if r.startswith(f"## {data_voce}") and "ripresa" in r.lower() and "gump" in r.lower()]
    if not voci:
        sys.exit(f"GUARDIA RIPRESA: nessuna voce '## {data_voce} ...' con 'ripresa' e 'Gump' in DECISIONS.md. Scrivila prima.")
    if os.path.exists(referto):
        sys.exit(f"GUARDIA RIPRESA: {referto} esiste gia': la ripresa si fa una volta sola.")
    verifica()


def guardia(referto: str) -> None:
    fm = open(PREREG, encoding="utf-8").read().split("---")[1]
    stato = re.search(r"^stato:\s*(\S+)", fm, re.M)
    if not stato or stato.group(1) != "APPROVATA":
        sys.exit(f"GUARDIA: la pre-registrazione e' '{stato.group(1) if stato else '?'}', non APPROVATA. Non si esegue.")
    fam = {f["id"]: f for f in json.load(open(LEDGER, encoding="utf-8"))["famiglie"]}
    if FAMIGLIA not in fam:
        sys.exit(f"GUARDIA: la famiglia {FAMIGLIA} non e' nel ledger. Non si esegue.")
    if fam[FAMIGLIA].get("holdout_aperto"):
        sys.exit(f"GUARDIA: holdout gia' aperto il {fam[FAMIGLIA]['holdout_aperto']}. Una seconda esecuzione e' vietata (D1).")
    if os.path.exists(referto):
        sys.exit(f"GUARDIA: il referto {referto} esiste gia'. Non si esegue.")
    from analysis.forexgump.export_tick import _file, ore_necessarie
    mancanti = [h for h in ore_necessarie() if not os.path.exists(_file(h))]
    if mancanti:
        sys.exit(f"GUARDIA: mancano {len(mancanti)} ore di tick (prima: {mancanti[0]}). Completa export_tick.py.")
    bid, _ = carica_m1()
    for h in ore_necessarie():
        if len(pd.read_parquet(_file(h))) == 0:
            i0, i1 = bid.index.searchsorted(h), bid.index.searchsorted(h + pd.Timedelta(hours=1))
            if i1 > i0:
                sys.exit(f"GUARDIA: l'ora {h} non ha tick ma ha {i1 - i0} barre M1: scarico incompleto, non chiusura.")
    verifica()


def apri_holdout() -> None:
    led = json.load(open(LEDGER, encoding="utf-8"))
    for f in led["famiglie"]:
        if f["id"] == FAMIGLIA:
            f["holdout_aperto"] = str(dt.date.today())
    with open(LEDGER, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(led, ensure_ascii=False, indent=2) + "\n")


# ---- dati -----------------------------------------------------------------------------------

def tick_da_cache(t0, t1):
    """Tick di [t0, t1) solo se TUTTE le ore sono in cache; altrimenti None -> il trade va su M1 (B2)."""
    parti = []
    for h in pd.date_range(pd.Timestamp(t0).floor("h"), pd.Timestamp(t1).floor("h"), freq="h"):
        f = os.path.join(TICK_DIR, h.strftime("%Y%m%d_%H") + ".parquet")
        if not os.path.exists(f):
            return None
        parti.append(pd.read_parquet(f))
    df = pd.concat(parti)
    if not len(df):
        return None
    df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    df = df[~df.index.duplicated()].sort_index()
    df = df.loc[(df.index >= t0) & (df.index < t1)]
    return df if len(df) else None


def tick_sintetici(bid: pd.DataFrame, ask: pd.DataFrame):
    """Solo per la PROVA A SECCO (G1 #3, N1): tick ricavati dalle M1, 4 per barra (apertura, minimo,
    massimo, chiusura a +0/+15/+30/+45 s), cosi' la prova esercita lo stesso percorso tick dell'esecuzione
    vera (fill su tick, giunzione al minuto intero, variante LIMIT). Mai usati per un risultato."""
    def f(t0, t1):
        i0, i1 = bid.index.searchsorted(t0), bid.index.searchsorted(t1)
        if i1 <= i0:
            return None
        b, a = bid.iloc[i0:i1], ask.iloc[i0:i1]
        righe = []
        for k, (cb, ca) in enumerate((("open", "open"), ("low", "low"), ("high", "high"), ("close", "close"))):
            righe.append(pd.DataFrame({"bidPrice": b[cb].values, "askPrice": a[ca].values},
                                      index=b.index + pd.Timedelta(seconds=15 * k)))
        df = pd.concat(righe).sort_index()
        df = df.loc[(df.index >= t0) & (df.index < t1)]
        return df if len(df) else None
    return f


def sposta_giornate(s: pd.DataFrame, idx: pd.DatetimeIndex, rng, n_volte: int = 1) -> pd.DataFrame:
    """Copie della tabella dei segnali con le giornate spostate in blocco di +/-1..20 giorni (come potenza.py)."""
    righe = []
    for _, blocco in s.groupby(s.t_utc.map(rp.giorno_trading)):
        trovati = 0
        for k in rng.permutation(SPOSTAMENTI):          # spostamenti DISTINTI per giornata (G1 #3)
            nuovi = blocco.t_utc + pd.Timedelta(days=int(k))
            pos = idx.searchsorted(nuovi.values)
            if all(p < len(idx) and abs((idx[p] - t).total_seconds()) < 180 for p, t in zip(pos, nuovi)):
                righe.append(blocco.assign(t_utc=nuovi))
                trovati += 1
                if trovati == n_volte:
                    break
    return pd.concat(righe, ignore_index=True)


# ---- calcolo --------------------------------------------------------------------------------

def corsa(pz, s, appaiato=True, **kw) -> pd.DataFrame:
    righe = []
    for r in s.itertuples():
        if appaiato:
            x = rp.esegui_appaiato(pz, r.t_utc, r.long, r.dsl, r.dtp, entry_post=r.entry, **kw)
            m, o, d = x["mentore"], x["opposto"], x["d"]
        else:                                         # varianti descrittive: solo il lato del mentore (B1)
            m, o, d = rp.esegui(pz, r.t_utc, r.long, r.dsl, r.dtp, entry_post=r.entry, **kw), {}, None
        hold = lambda z: ((z["t_uscita"] - z["t_fill"]).total_seconds() / 3600
                          if z.get("t_uscita") is not None else None)
        righe.append({"msg_id": r.msg_id, "t": r.t_utc, "anno": r.t_utc.year, "long": r.long, "dsl": r.dsl,
                      "esito": m["esito"], "r_m": m["r"], "r_o": o.get("r"), "d": d,
                      "scarto": m.get("scarto_postato"), "fonte": m.get("sorgente_fill"),
                      "giorno": rp.giorno_trading(m.get("t_fill", r.t_utc)),
                      "hold_m": hold(m), "hold_o": hold(o) if o else None, "rollover": m.get("rollover"),
                      **{c: getattr(r, c) for c in CATEGORIE}})
    return pd.DataFrame(righe)


class Referto:
    """Scrive il referto un pezzo alla volta: un errore a meta' lascia comunque tutto cio' che e' calcolato."""

    def __init__(self, dest):
        self.dest = dest
        open(dest, "w", encoding="utf-8").close()

    def __call__(self, *righe):
        with open(self.dest, "a", encoding="utf-8") as fh:
            fh.write("\n".join(righe) + "\n")
        print("\n".join(righe), flush=True)


def _riga(nome, valori, giorni, f):
    ci = rp.ci_cluster_giorno(valori, giorni)
    return (f"| {nome} | {ci['n']} | {ci['media']:+.3f} | [{ci['low']:+.3f}; {ci['high']:+.3f}] | "
            f"{f * ci['se']:.3f} |"), ci


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prova-a-secco", action="store_true", help="istanti spostati, nessuna guardia, scratchpad")
    ap.add_argument("--n", type=int, default=150, help="segnali nella prova a secco")
    ap.add_argument("--ripresa", metavar="AAAA-MM-GG", help="data della voce DECISIONS che autorizza la ripresa")
    a = ap.parse_args()
    f = fattore_potenza()
    rng = np.random.default_rng(SEED)
    bid, ask = carica_m1()
    s = carica_segnali()
    s["long"] = s.side == "buy"
    s["dsl"], s["dtp"] = (s.entry - s.sl).abs(), (s.tp - s.entry).abs()

    if a.prova_a_secco:
        s = sposta_giornate(s, bid.index, rng).head(a.n)          # NESSUN istante dei segnali
        dest = os.path.join(os.environ.get("TEMP", "."), f"forexgump_prova_a_secco_{dt.date.today()}.md")
        pz = rp.Prezzi(m1_bid=bid, m1_ask=ask, tick=tick_sintetici(bid, ask))   # stesso percorso tick (N1)
    elif a.ripresa:
        dest = os.path.join(ROOT, "docs", "reviews", f"forexgump_esito_{dt.date.today()}_ripresa.md")
        guardia_ripresa(dest, a.ripresa)                       # l'apertura NON si tocca
        pz = rp.Prezzi(m1_bid=bid, m1_ask=ask, tick=tick_da_cache)
    else:
        dest = os.path.join(ROOT, "docs", "reviews", f"forexgump_esito_{dt.date.today()}.md")
        guardia(dest)
        apri_holdout()
        pz = rp.Prezzi(m1_bid=bid, m1_ask=ask, tick=tick_da_cache)
    out = Referto(dest)
    out(f"# Forex Gump — esito del test pre-registrato ({dt.date.today()}){' — PROVA A SECCO, istanti spostati' if a.prova_a_secco else ''}",
        "", "Pre-registrazione: `docs/FOREXGUMP_LATENCY_PREREGISTRATION.md`. Esecuzione unica; holdout = 100% del campione.", "")

    # 1. kill sui dati -------------------------------------------------------------------------
    base = corsa(pz, s, L=10, conv=PESSIMISTA)
    q = lambda e: (base.esito == e).mean()
    out("## 1. Kill sui dati", "", f"- senza prezzi: {q('SENZA_PREZZI'):.1%} (kill > 10%)",
        f"- SKIP per spread reale >= SL: {q('SKIP_SPREAD'):.1%} (kill > 10%)",
        f"- non eseguiti (fill oltre 60 s da t+L): {q('NON_ESEGUITO'):.1%}",
        f"- fill da tick: {(base.fonte == 'tick').mean():.1%}, da M1: {(base.fonte == 'm1').mean():.1%}", "")
    if q("SENZA_PREZZI") + q("NON_ESEGUITO") > KILL or q("SKIP_SPREAD") > KILL:   # §6: senza prezzi o non eseguiti
        out("**KILL sui dati**: il test si ferma qui, come da §6."); return 0

    # 2. primario ----------------------------------------------------------------------------
    stress = corsa(pz, s, L=10, conv=PESSIMISTA, stress=True)
    ottim = corsa(pz, s, L=10, conv=OTTIMISTA)
    ok, oks, oko = base.d.notna(), stress.d.notna(), ottim.d.notna()
    r_d, ci_d = _riga("d (pessimistica)", base.d[ok], base.giorno[ok], f)
    r_e, ci_e = _riga("E[R] lato mentore (pessimistica)", base.r_m[ok], base.giorno[ok], f)
    r_es, ci_es = _riga("E[R] lato mentore (STRESS)", stress.r_m[oks], stress.giorno[oks], f)
    r_do, _ = _riga("d (ottimistica, solo accanto)", ottim.d[oko], ottim.giorno[oko], f)
    out("## 2. Primario (L = 10 s)", "", "| misura | n | media | CI 95% a cluster per giornata | MDE osservato |",
        "|---|---|---|---|---|", r_d, r_e, r_es, r_do,
        f"\nSKIP sotto stress: {(stress.esito == 'SKIP_SPREAD').mean():.1%} (deciso sullo spread reale: stesso campione)",
        f"Quota di trade che attraversano il rollover delle 22 UTC: {(base.rollover.dropna() > 0).mean():.1%}", "")

    # 3. Step 3bis -----------------------------------------------------------------------------
    postato = corsa(pz, s, appaiato=False, L=10, conv=PESSIMISTA, variante="postato")
    stessi = base.msg_id[base.r_m.notna()]                     # costo del ritardo sugli STESSI segnali (G1 #3)
    e_ott, e_post = base.r_m[base.msg_id.isin(stessi)].mean(), postato.r_m[postato.msg_id.isin(stessi)].mean()
    sc = base.scarto[base.esito.isin(["SL", "TP", "TIMEOUT", "BE"])].dropna()
    out("## 3. Diagnostica Step 3bis", "",
        f"- prezzo postato gia' superato in senso sfavorevole a t+L (sui trade eseguiti): {(sc > 0).mean():.1%}",
        f"- E[R] al prezzo postato (**NON OTTENIBILE**, solo per il costo del ritardo), sugli stessi {len(stessi)} segnali: {e_post:+.3f}",
        f"- costo del ritardo = E[R] postato - E[R] ottenibile, stessi segnali: {e_post - e_ott:+.3f}R", "")

    # 4. verdetto ------------------------------------------------------------------------------
    lb = ci_d["low"]
    if lb > 0 and ci_e["media"] > 0 and ci_es["media"] > 0:
        verdetto = "LEAD"
    elif lb > 0 and ci_e["media"] > 0:
        verdetto = "LEAD FRAGILE"
    elif lb > 0:
        verdetto = "DEGRADATO"
    else:
        verdetto = f"NON DIMOSTRATO (MDE {MDE_PREREGISTRATO:.3f}R)"
    out("## 4. Verdetto meccanico (§6)", "", f"**{verdetto}**", "",
        f"MDE pre-registrato (vale per l'etichetta): {MDE_PREREGISTRATO:.3f}R; MDE dall'errore osservato: {f * ci_d['se']:.3f}R", "")

    # 5. controlli -----------------------------------------------------------------------------
    out("## 5. Controlli", "", "| lato | n | E[R] mentore | d |", "|---|---|---|---|")
    for lab, m in (("buy", base.long), ("sell", ~base.long)):
        sel = base[m & ok]
        out(f"| {lab} | {len(sel)} | {sel.r_m.mean():+.3f} | {sel.d.mean():+.3f} |")
    # N2 (G1 #3): i controlli girano su sole M1 (fuori dalle finestre dei segnali non ci sono tick), quindi
    # il braccio reale si RIFA su sole M1 e il confronto e' M1 contro M1. La versione su tick resta accanto.
    pz_m1 = rp.Prezzi(m1_bid=bid, m1_ask=ask)
    base_m1 = corsa(pz_m1, s, L=10, conv=PESSIMISTA)
    spost = sposta_giornate(s, bid.index, np.random.default_rng(SEED + 1), n_volte=3)
    ctrl = corsa(pz_m1, spost, L=10, conv=PESSIMISTA)
    ctrl = ctrl[ctrl.r_m.notna()]
    reale = base_m1[base_m1.r_m.notna()].assign(side=lambda x: x.long.map({True: "buy", False: "sell"}), risk=lambda x: x.dsl, hold=lambda x: x.hold_m)
    contr = ctrl.assign(side=lambda x: x.long.map({True: "buy", False: "sell"}), risk=lambda x: x.dsl, hold=lambda x: x.hold_m)
    contr = contr[contr.msg_id.isin(reale.msg_id)]
    rep = check_matching(reale.rename(columns={"side": "side"}), contr, link="msg_id",
                         exact=("side",), numeric=("risk",), observed=("hold",))
    r_c, ci_c = _riga("E[R] stesso lato a istante casuale (3 controlli, M1)", ctrl.r_m, ctrl.giorno, f)
    okm = base_m1.r_m.notna()
    r_em, _ = _riga("E[R] lato mentore rifatto su sole M1", base_m1.r_m[okm], base_m1.giorno[okm], f)
    media_ctrl = ctrl.groupby("msg_id").r_m.mean()
    div = base_m1[okm].assign(c=lambda x: x.msg_id.map(media_ctrl)).dropna(subset=["c"])
    r_div, _ = _riga("divario mentore - controlli (M1 contro M1)", div.r_m - div.c, div.giorno, f)
    out("", "| misura | n | media | CI 95% a cluster | MDE |", "|---|---|---|---|---|", r_em, r_c, r_div,
        r_e.replace("E[R] lato mentore (pessimistica)", "E[R] lato mentore su tick (solo accanto)"), "",
        "```", str(rep), "```", "",
        f"Holding mediano (h), M1: mentore {base_m1.hold_m.median():.2f}, lato opposto {base_m1.hold_o.median():.2f}, "
        f"controlli {ctrl.hold_m.median():.2f}", "")

    # 6. descrittive (0 trial) -----------------------------------------------------------------
    out("## 6. Descrittive (0 trial, nessun verdetto)", "", "**Latenza**", "", "| L (s) | n | E[R] | d |", "|---|---|---|---|")
    for L in LATENZE:
        x = base if L == 10 else corsa(pz, s, L=L, conv=PESSIMISTA)
        xo = x.d.notna()
        out(f"| {L} | {xo.sum()} | {x.r_m[xo].mean():+.3f} | {x.d[xo].mean():+.3f} |")
    out("", "**Esecuzioni alternative (solo lato del mentore)**", "", "| variante | eseguiti | E[R] |", "|---|---|---|")
    for var in ("live", "limit", "skip1"):
        x = corsa(pz, s, appaiato=False, L=10, conv=PESSIMISTA, variante=var)
        out(f"| {var} | {x.r_m.notna().sum()} di {len(s)} | {x.r_m.mean():+.3f} |")
    meta = corsa(pz, s, appaiato=False, L=10, conv=PESSIMISTA, k_spread=0.5)
    out(f"| meta' spread | {meta.r_m.notna().sum()} | {meta.r_m.mean():+.3f} |",
        "", "**Per anno, categoria, finestra post-cutoff**", "", "| gruppo | n | E[R] | d |", "|---|---|---|---|")
    gruppi = [(f"anno {y}", base.anno == y) for y in sorted(base.anno.unique())]
    gruppi += [(c, base[c].astype(bool)) for c in CATEGORIE]
    gruppi += [("06-09/2026 (post-cutoff)", base.t >= pd.Timestamp("2026-06-01"))]
    for lab, m in gruppi:
        sel = base[m & ok]
        if len(sel):
            out(f"| {lab} | {len(sel)} | {sel.r_m.mean():+.3f} | {sel.d.mean():+.3f} |")

    # spiegazione noiosa: lato = segno del movimento nei 15 minuti prima, SOLO barre chiuse entro il
    # messaggio (B3). Movimento nullo -> nessun lato, escluso e contato. Criterio dichiarato: il mentore
    # aggiunge informazione al momentum se il CI a cluster della differenza appaiata (d_mentore - d_mom),
    # sugli stessi istanti, ha limite inferiore > 0.
    mid_c = ((bid.close + ask.close) / 2)
    ix = mid_c.index
    mom_d, ment_d, giorni, nulli, stantii = [], [], [], 0, 0
    for r, dm, g in zip(s.itertuples(), base.d, base.giorno):
        p1 = ix.searchsorted(r.t_utc - pd.Timedelta(minutes=1), side="right") - 1    # barra chiusa entro t
        p0 = ix.searchsorted(r.t_utc - pd.Timedelta(minutes=16), side="right") - 1   # chiusa entro t-15
        if p0 < 0 or p1 < 0 or pd.isna(dm):
            continue
        if ix[p1] < r.t_utc - pd.Timedelta(minutes=2) or ix[p0] < r.t_utc - pd.Timedelta(minutes=17):
            stantii += 1; continue                            # dopo una pausa le barre sono vecchie (G1 #3)
        if mid_c.iloc[p1] == mid_c.iloc[p0]:
            nulli += 1; continue
        lato = bool(mid_c.iloc[p1] > mid_c.iloc[p0])
        dmom = dm if lato == r.long else -dm                  # stesso istante: d del lato opposto = -d
        mom_d.append(dmom); ment_d.append(dm); giorni.append(g)
    diff = np.array(ment_d) - np.array(mom_d)
    ci_mom = rp.ci_cluster_giorno(diff, giorni)
    out("", f"**Spiegazione noiosa** (momentum a 15 minuti): d medio {np.mean(mom_d):+.3f} su {len(mom_d)} "
        f"(esclusi: movimento nullo {nulli}, barre vecchie dopo una pausa {stantii}); d_mentore - d_momentum {ci_mom['media']:+.3f} "
        f"[{ci_mom['low']:+.3f}; {ci_mom['high']:+.3f}] — il mentore aggiunge informazione al momentum solo se il "
        f"limite inferiore e' > 0", "")
    print("\nscritto:", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
