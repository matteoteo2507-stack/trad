"""Audit dell'ONESTA' DEL FILL D'INGRESSO sul FADE A1 — non e' un trial nuovo.

Domanda. `closure.py` concede il fill al prezzo `entry` ogni volta che una barra
successiva alla conferma lo *tocca*. Ma lo swing di fine e' un frattale a K=5 barre
per lato: e' noto solo alla CHIUSURA della barra `cb = b+K`, quindi la prima barra
azionabile e' `cb+1` (l'EA infatti legge solo barre chiuse: `nxt_fade.mq5` CopyRates
da shift 1). In quelle ~6 ore il prezzo fa proprio il ritracciamento al 50% che
vogliamo tradare, e puo' aver gia' oltrepassato il livello. Quando succede, il
backtest riempie comunque **a `entry`**: un prezzo che il mercato aveva lasciato
indietro prima che potessimo agire.

Non e' look-ahead di INFORMAZIONE (il pivot e' confermato): e' look-ahead di PREZZO.
Live e' esattamente il ramo in cui `mql5/nxt_fade.mq5` (righe ~436-450) rinuncia al
pending ed entra a mercato tenendo SL/TP del livello teorico -> rischio 1,3-4,0x,
RR fino a 1:0,00.

Varianti misurate sugli stessi dati del backtest originale:
  BASE     : com'e' oggi — fill sempre a `entry`
  SKIP     : se il livello e' gia' oltrepassato alla prima barra azionabile, NON si entra
  RECENTER : entra all'apertura della prima barra azionabile, SL/TP RICENTRATI sul fill
  LIVE     : entra all'apertura della prima barra azionabile con SL/TP TEORICI (= l'EA)
  LIMIT    : piazza un limit e ASPETTA che il prezzo torni al livello. Fill esatto a
             `entry`, geometria 1:3 intatta. E' il maggiorante della famiglia ottenibile.

TRE ASSI DI BRACKETING, non due. Oltre all'ambiguita' intrabar SL-vs-TP (pess/opt)
c'e' una terza convenzione che vale piu' delle altre due messe insieme:

  **la barra di fill puo' stoppare il trade con il proprio range PRE-ingresso?**

`closure.py` dice si' (`range(f, ...)`). Ma con stop a 0,286*ampiezza, una barra che
apre oltre il 78,6% e sfonda il 50% in un'ora e' comune — e questo penalizza in modo
STRUTTURALE proprio le varianti oneste, che si riempiono a meta' barra, risparmiando
il ramo `already` di BASE che apre gia' oltre con lo stop lontano. Misurato: gli stop
sulla barra di fill sono ~20% dei trade `already=False` contro ~2,5% degli `already=True`.
Ignorarlo produce una magnitudo gonfiata. Si riporta quindi un INTERVALLO su 4 combinazioni,
mai un punto.

Convenzione sullo stop: se l'apertura della barra e' gia' oltre lo stop, il fill avviene
LI' (come `weekend.py`), non al livello — tranne sulla barra di fill stessa, dove
l'apertura PRECEDE l'ingresso e non e' un prezzo raggiungibile dopo. I trade non risolti
entro MAX_HOLD sono marcati al mercato (come `weekend.py` e come l'EA), non scartati.

Unita' di misura: **rischio INTESO** (Rint = 0.286*rng), l'unita' su cui il sizing mette
lo 0,25% dell'equity. E' l'unica normalizzazione in cui una perdita con stop 3x piu'
lontano costa davvero 3 volte — cioe' l'unica che dice cosa fa il conto.

Classificazione: verifica di integrita' dell'esecuzione (STRATEGY_LIFECYCLE §3),
**nessun trial consumato**. Non tocca ne' regole ne' parametri. ATTENZIONE: se una di
queste varianti venisse SCELTA per proseguire, quello sarebbe un cambio di regola dopo
aver visto l'esito -> trial #3, l'ultimo del budget della famiglia NXT.

Uso:  python analysis/nxt/entry_fill_audit.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.nxt import backtest as bt          # noqa: E402
from core import quant_metrics as qm             # noqa: E402

RISK_FRAC = 0.286          # R come frazione dell'ampiezza (config A1, CONGELATO)
RR = 3.0
BE_AT = 2.0
COMMON_START = pd.Timestamp("2020-05-19")   # inizio del piu' corto dei 6 feed (XAUUSD)

VARIANTS = ("base", "skip", "recenter", "live", "limit")
CONV = [(p, s) for p in (True, False) for s in (True, False)]   # (pess, fill_bar_stops)


def resolve(O, H, L, C, f, fill, sl, tp, pos_long, r_int, cost_R, pess, fill_bar_stops):
    """Dal fill in poi: BE a +2R sul rischio REALE, poi SL/TP. Ritorna R in unita' Rint.

    - `fill_bar_stops=False`: la barra di fill non puo' risolvere il trade (si parte da f+1).
      E' il terzo asse di bracketing: vedi docstring del modulo.
    - gap oltre lo stop: se l'apertura e' gia' oltre, il fill e' li' (weekend.py), tranne
      sulla barra di fill, la cui apertura precede l'ingresso.
    """
    risk = abs(fill - sl)
    if risk <= 0:
        return None
    sgn = 1.0 if pos_long else -1.0
    be = fill + BE_AT * risk if pos_long else fill - BE_AT * risk
    be_on, sl_cur = False, sl
    start = f if fill_bar_stops else f + 1
    end = min(f + bt.MAX_HOLD, len(H))
    if start >= end:
        return None
    for j in range(start, end):
        if not be_on and ((H[j] >= be) if pos_long else (L[j] <= be)):
            be_on, sl_cur = True, fill
        hit_sl = (L[j] <= sl_cur) if pos_long else (H[j] >= sl_cur)
        hit_tp = (H[j] >= tp) if pos_long else (L[j] <= tp)
        if hit_sl and hit_tp:
            hit_tp, hit_sl = (False, True) if pess else (True, False)
        if hit_sl:
            jumped = (O[j] < sl_cur) if pos_long else (O[j] > sl_cur)
            if j == f:
                jumped = False          # l'apertura precede l'ingresso
            px = O[j] if jumped else sl_cur
            return sgn * (px - fill) / r_int - cost_R
        if hit_tp:
            return sgn * (tp - fill) / r_int - cost_R
    return sgn * (C[end - 1] - fill) / r_int - cost_R      # mark-to-market a max-hold


def sim_variants(leg, O, H, L, C, sym):
    side, hi, lo, rng = leg["side"], leg["hi"], leg["lo"], leg["rng"]
    b, cb = leg["end_idx"], leg["conf"]
    buy_leg = (side == "BUY")

    entry = (hi - 0.5 * rng) if buy_leg else (lo + 0.5 * rng)
    pos_long = not buy_leg                       # FADE: posizione invertita
    r_int = RISK_FRAC * rng
    if r_int <= 0:
        return None
    sl_t = entry - r_int if pos_long else entry + r_int
    tp_t = entry + RR * r_int if pos_long else entry - RR * r_int
    cost_R = bt.SPREAD.get(sym, 0.0) / r_int

    fa = cb + 1                                  # frattale noto alla CHIUSURA di cb
    if fa >= len(H):
        return None

    # gia' oltrepassato all'apertura della prima barra azionabile?
    already = (O[fa] > entry) if pos_long else (O[fa] < entry)

    f = None                                     # fill "com'e' oggi", al livello
    for j in range(fa, min(b + 1 + bt.FILL_WINDOW, len(H))):
        if (L[j] <= entry) if buy_leg else (H[j] >= entry):
            f = j
            break
    if f is None:
        return None

    out = {"asset": sym, "entry_idx": f, "already": bool(already)}

    def acc(tag, f_i, fill, sl, tp):
        for pess, fbs in CONV:
            k = "R_%s_%s%s" % (tag, "p" if pess else "o", "S" if fbs else "N")
            r = resolve(O, H, L, C, f_i, fill, sl, tp, pos_long, r_int, cost_R, pess, fbs)
            out[k] = np.nan if r is None else r

    acc("base", f, entry, sl_t, tp_t)

    if not already:
        for t in ("skip", "recenter", "live", "limit"):
            for pess, fbs in CONV:
                sfx = "%s%s" % ("p" if pess else "o", "S" if fbs else "N")
                out["R_%s_%s" % (t, sfx)] = out["R_base_%s" % sfx]
        return out

    for pess, fbs in CONV:                       # SKIP: trade non preso
        out["R_skip_%s%s" % ("p" if pess else "o", "S" if fbs else "N")] = np.nan
    fill = O[fa]
    sl_r = fill - r_int if pos_long else fill + r_int
    tp_r = fill + RR * r_int if pos_long else fill - RR * r_int
    acc("recenter", fa, fill, sl_r, tp_r)
    acc("live", fa, fill, sl_t, tp_t)
    # LIMIT: finestra contata da `fa` (piu' generosa della spec, A FAVORE della strategia)
    fl = None
    for j in range(fa, min(fa + bt.FILL_WINDOW, len(H))):
        if (L[j] <= entry) if pos_long else (H[j] >= entry):
            fl = j
            break
    if fl is None:
        for pess, fbs in CONV:
            out["R_limit_%s%s" % ("p" if pess else "o", "S" if fbs else "N")] = np.nan
    else:
        acc("limit", fl, entry, sl_t, tp_t)
    return out


def bracket(d, tag):
    """Intervallo di E[R] sulle 4 convenzioni + BCa sul caso peggiore e migliore."""
    vals = {}
    for pess, fbs in CONV:
        col = "R_%s_%s%s" % (tag, "p" if pess else "o", "S" if fbs else "N")
        x = d[col].dropna().values
        if len(x):
            vals[(pess, fbs)] = x
    if not vals:
        return None
    means = {k: float(v.mean()) for k, v in vals.items()}
    kmin = min(means, key=means.get)
    kmax = max(means, key=means.get)
    ci = lambda x: qm.bca_bootstrap_ci(x, metric=lambda v: float(np.mean(v)), conf=0.95,
                                       n_boot=3000, seed=bt.SEED)
    lo_ci, hi_ci = ci(vals[kmin]), ci(vals[kmax])
    n = int(np.mean([len(v) for v in vals.values()]))
    return {"tag": tag, "n": n, "lo": means[kmin], "hi": means[kmax],
            "lo_ci": (lo_ci["low"], lo_ci["high"]), "hi_ci": (hi_ci["low"], hi_ci["high"]),
            "win": float((vals[(True, True)] > 0).mean()) if (True, True) in vals else np.nan,
            "worst": float(min(v.min() for v in vals.values()))}


def show(d, title):
    print("\n" + title)
    print("  %-9s %6s  %-30s %-24s %6s %8s"
          % ("variante", "n", "E[R] intervallo su 4 convenzioni", "BCa95 dei due estremi",
             "win", "peggiore"))
    for t in VARIANTS:
        b = bracket(d, t)
        if b is None:
            print("  %-9s  —" % t)
            continue
        print("  %-9s %6d  [%+.3f ; %+.3f]%13s [%+.3f;%+.3f] [%+.3f;%+.3f] %5.1f%% %+7.2fR"
              % (t, b["n"], b["lo"], b["hi"], "",
                 b["lo_ci"][0], b["lo_ci"][1], b["hi_ci"][0], b["hi_ci"][1],
                 100 * b["win"], b["worst"]))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:
        pass
    rows = []
    for sym in bt.ASSETS:
        d = bt.load_h1(sym)
        O, H = d["open"].to_numpy(float), d["high"].to_numpy(float)
        L, C = d["low"].to_numpy(float), d["close"].to_numpy(float)
        A = bt.atr(H, L, C)
        for lg in bt.build_legs(bt.zigzag(H, L), A):
            r = sim_variants(lg, O, H, L, C, sym)
            if r:
                r["time"] = d["time"].iloc[r["entry_idx"]]
                rows.append(r)
    df = pd.DataFrame(rows)
    df["year"] = df["time"].dt.year
    n, na = len(df), int(df["already"].sum())

    print("=" * 92)
    print("AUDIT DEL FILL D'INGRESSO - FADE A1   (lag corretto: prima barra azionabile = cb+1)")
    print("=" * 92)
    print("\ntrade simulati: %d" % n)
    print("livello GIA' OLTREPASSATO alla prima barra azionabile: **%d (%.1f%%)**" % (na, 100 * na / n))
    print("  [live: 17/43 = 40%%, CI95 ~[26%%;56%%] — COMPATIBILE, non confermativo:")
    print("   n live troppo piccolo, e il ramo market dell'EA scatta anche dentro lo stops level]")

    print("\n⚠️ COPERTURA NON OMOGENEA — le finestre non coincidono:")
    for s, g in df.groupby("asset"):
        print("  %-8s %s -> %s   already %4d/%4d (%4.1f%%)"
              % (s, g["time"].min().date(), g["time"].max().date(),
                 int(g["already"].sum()), len(g), 100 * g["already"].mean()))
    print("  FX dal 2012, indici/oro dal 2020: la tabella per strumento NON e' prova di")
    print("  omogeneita' del fenomeno, e' confondata col periodo. Vedi finestra comune sotto.")

    show(df, "--- TUTTI I DATI ---")
    dc = df[df["time"] >= COMMON_START]
    print("\n  (finestra comune %s -> fine, n=%d, already %.1f%%)"
          % (COMMON_START.date(), len(dc), 100 * dc["already"].mean()))
    show(dc, "--- FINESTRA COMUNE A TUTTI E 6 GLI STRUMENTI ---")
    show(df[df["already"]], "--- SOLO i %d trade con livello gia' oltrepassato ---" % na)

    print("\n--- CORROBORAZIONE: e' meccanico o e' di mercato? ---")
    for t in ("base", "skip"):
        col = "R_%s_pS" % t
        yr = df.groupby("year")[col].mean().dropna()
        asst = df.groupby("asset")[col].mean().dropna()
        print("  %-5s  anni positivi %2d/%2d   asset positivi %d/%d   (convenzione pess+fillbar)"
              % (t, int((yr > 0).sum()), len(yr), int((asst > 0).sum()), len(asst)))
    print("  Un edge presente in TUTTI gli anni e TUTTI gli asset, che sparisce togliendo")
    print("  i fill non ottenibili, e' un artefatto meccanico — non un'anomalia di mercato.")

    print("\ntrade log -> %s"
          % os.path.relpath(os.path.join(ROOT, "analysis", "nxt",
                                         "entry_fill_audit_trades.csv"), ROOT))
    df.to_csv(os.path.join(ROOT, "analysis", "nxt", "entry_fill_audit_trades.csv"), index=False)


if __name__ == "__main__":
    main()
