"""NXT/FADE — AUTOPSIA DEGLI STOP: come e perche' muoiono i trade.

NON e' una variante di strategia e NON propone regole: e' una scomposizione descrittiva
del trade log gia' pre-registrato (config A1 FADE, entry_fib=0.5). Per STRATEGY_LIFECYCLE
§3 la rianalisi descrittiva di un test chiuso non consuma trial.

Convenzioni identiche a weekend.py (che corregge closure.py sul fill vero dello stop:
se la barra APRE gia' oltre lo stop, il fill e' l'apertura, non il livello).

Sette domande:
  A  ESITI      quanto pesa ogni modo di morte sull'E[R]?
  B  QUANDO     dopo quante barre muore un trade? quanti muoiono sulla barra di ingresso?
  C  FAVORE     quanto era andato a favore PRIMA di morire? (stop stretto vs. restituzione)
  D  RUMORE     quanto e' largo lo stop in unita' di ATR orario? vive dentro il rumore?
  E  ORE        gli stop si concentrano in certe ore? (normalizzato per ESPOSIZIONE)
  F  SALTI      il gap-attraverso-lo-stop: quando avviene davvero?
  G  RANDOM     un'entrata casuale con lo STESSO stop muore allo stesso modo?

Uso: python analysis/nxt/stops.py
"""
from __future__ import annotations

import collections
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import backtest as bt  # noqa: E402

BE_AT = 2.0
RR = 3.0
M_RANDOM = 3        # controlli random risk-matched per trade reale
SEED = bt.SEED


# ---------------------------------------------------------------------------
def walk(f, entry, sl, tp, be, pos_long, O, H, L, C, cost_R, max_hold=None):
    """Cammino di un trade dal fill alla risoluzione, strumentato.

    Regole IDENTICHE a weekend.py/closure.py: prima il BE, poi stop/target, bound
    pessimistico (se una barra tocca entrambi vince lo stop). Ritorna un dict o None.
    """
    max_hold = bt.MAX_HOLD if max_hold is None else max_hold
    sgn = 1.0 if pos_long else -1.0
    sl_cur, be_on, be_bar = sl, False, -1
    mfe = mae = 0.0                      # escursioni in R, correnti
    mfe_pre = 0.0                        # MFE raggiunta PRIMA della barra fatale
    risk = abs(entry - sl)

    for j in range(f, min(f + max_hold, len(H))):
        # escursioni della barra in R, col segno della posizione (prima di BE/stop:
        # misuro il CAMMINO, non l'esito)
        if pos_long:
            hi_R, lo_R = (H[j] - entry) / risk, (L[j] - entry) / risk
        else:
            hi_R, lo_R = (entry - L[j]) / risk, (entry - H[j]) / risk
        mfe_pre = mfe
        mfe = max(mfe, hi_R)
        mae = min(mae, lo_R)

        if not be_on and ((H[j] >= be) if pos_long else (L[j] <= be)):
            be_on = True
            be_bar = j - f
            sl_cur = entry
        hit_sl = (L[j] <= sl_cur) if pos_long else (H[j] >= sl_cur)
        hit_tp = (H[j] >= tp) if pos_long else (L[j] <= tp)

        if hit_sl:
            jumped = (O[j] < sl_cur) if pos_long else (O[j] > sl_cur)
            fill = O[j] if jumped else sl_cur
            return {"outcome": "BE" if be_on else "SL",
                    "R": sgn * (fill - entry) / risk - cost_R,
                    "R_assumed": (0.0 if be_on else -1.0) - cost_R,
                    "jumped": bool(jumped),
                    "ambiguous": bool(hit_tp),      # la barra fatale toccava ANCHE il TP
                    "hold": j - f, "exit_idx": j, "be_on": be_on, "be_bar": be_bar,
                    "mfe": mfe, "mfe_pre": mfe_pre, "mae": mae}
        if hit_tp:
            return {"outcome": "TP", "R": RR - cost_R, "R_assumed": RR - cost_R,
                    "jumped": False, "ambiguous": False,
                    "hold": j - f, "exit_idx": j, "be_on": be_on, "be_bar": be_bar,
                    "mfe": mfe, "mfe_pre": mfe_pre, "mae": mae}

    j = min(f + max_hold, len(H)) - 1
    return {"outcome": "TIME", "R": sgn * (C[j] - entry) / risk - cost_R,
            "R_assumed": sgn * (C[j] - entry) / risk - cost_R,
            "jumped": False, "ambiguous": False,
            "hold": j - f, "exit_idx": j, "be_on": be_on, "be_bar": be_bar,
            "mfe": mfe, "mfe_pre": mfe_pre, "mae": mae}


def fade_trades(sym, rng=None, m_random=0):
    """Config A1 (FADE) strumentata + baseline random risk-matched."""
    d = bt.load_h1(sym)
    O, H, L, C = (d[c].values.astype(float) for c in ("open", "high", "low", "close"))
    t = pd.DatetimeIndex(d["time"])
    hour, dow = t.hour.values, t.dayofweek.values
    A = bt.atr(H, L, C)
    legs = bt.build_legs(bt.zigzag(H, L), A)
    spread = bt.SPREAD.get(sym, 0.0)
    n = len(H)

    rows, rnd, expo = [], [], collections.Counter()
    for lg in legs:
        side, hi, lo, rng_ = lg["side"], lg["hi"], lg["lo"], lg["rng"]
        b, cb = lg["end_idx"], lg["conf"]
        buy_leg = (side == "BUY")
        entry = (hi - 0.5 * rng_) if buy_leg else (lo + 0.5 * rng_)
        pos_long = not buy_leg                       # FADE = posizione invertita
        risk = 0.286 * rng_
        if risk <= 0:
            continue
        sl = entry - risk if pos_long else entry + risk
        tp = entry + RR * risk if pos_long else entry - RR * risk
        be = entry + BE_AT * risk if pos_long else entry - BE_AT * risk

        f = None
        for j in range(max(cb, b + 1), min(b + 1 + bt.FILL_WINDOW, n)):
            if (L[j] <= entry) if buy_leg else (H[j] >= entry):
                f = j
                break
        if f is None:
            continue

        cost_R = spread / risk
        w = walk(f, entry, sl, tp, be, pos_long, O, H, L, C, cost_R)
        if w is None:
            continue
        for j in range(f, w["exit_idx"] + 1):        # esposizione oraria
            expo[hour[j]] += 1
        atr_f = A[f] if np.isfinite(A[f]) and A[f] > 0 else np.nan
        tid = f"{sym}:{len(rows)}"
        rows.append({"tid": tid, "sym": sym, "pos_long": pos_long, "entry_idx": f,
                     "year": int(t[f].year), "hour_in": int(hour[f]), "dow_in": int(dow[f]),
                     "hour_out": int(hour[w["exit_idx"]]), "dow_out": int(dow[w["exit_idx"]]),
                     "risk_atr": risk / atr_f if atr_f == atr_f else np.nan,
                     "leg_atr": rng_ / atr_f if atr_f == atr_f else np.nan,
                     "cost_R": cost_R, **w})

        # ---- baseline random risk-matched: stesso rischio in PREZZO, stesso lato,
        #      entrata a istante casuale nello stesso anno.
        if m_random and rng is not None:
            same_year = np.where(t.year.values == t[f].year)[0]
            if len(same_year) > bt.MAX_HOLD + 2:
                pool = same_year[:-(bt.MAX_HOLD + 1)] if len(same_year) > bt.MAX_HOLD + 1 else same_year
                for _ in range(m_random):
                    k = int(rng.choice(pool))
                    e2 = C[k]
                    sl2 = e2 - risk if pos_long else e2 + risk
                    tp2 = e2 + RR * risk if pos_long else e2 - RR * risk
                    be2 = e2 + BE_AT * risk if pos_long else e2 - BE_AT * risk
                    w2 = walk(k + 1, e2, sl2, tp2, be2, pos_long, O, H, L, C, cost_R)
                    if w2 is not None:
                        a2 = A[k + 1] if np.isfinite(A[k + 1]) and A[k + 1] > 0 else np.nan
                        rnd.append({"sym": sym, "pos_long": pos_long, "parent": tid,
                                    "risk_atr": risk / a2 if a2 == a2 else np.nan,
                                    "hour_out": int(hour[w2["exit_idx"]]), **w2})
    return (pd.DataFrame(rows), pd.DataFrame(rnd), expo,
            pd.DataFrame({"hour": hour, "vol": d["volume"].values.astype(float),
                          "rng": (H - L) / np.where(np.isfinite(A) & (A > 0), A, np.nan)}))


# ---------------------------------------------------------------------------
def pct(x, n):
    return f"{100.0 * x / n:.1f}%" if n else "n/a"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    rng = np.random.default_rng(SEED)
    T, RND, EXPO, PROF = [], [], collections.Counter(), []
    for s in bt.ASSETS:
        a, r, e, p = fade_trades(s, rng=rng, m_random=M_RANDOM)
        T.append(a); RND.append(r); EXPO.update(e); PROF.append(p)
    tr = pd.concat(T, ignore_index=True)
    rd = pd.concat(RND, ignore_index=True)
    prof = pd.concat(PROF, ignore_index=True)

    print("=" * 78)
    print("FADE (NXT A1) — AUTOPSIA DEGLI STOP. Descrittiva: non consuma trial.")
    print("=" * 78)
    n = len(tr)
    print(f"\nRIPRODUZIONE: n={n}  E[R]={tr['R'].mean():+.3f}  "
          f"(fill assunti dal backtest: {tr['R_assumed'].mean():+.3f})")
    print(f"  atteso da weekend.py: n=10290  E[R]=+0.308  (assunto +0.355)")

    # ---------------- A. esiti ----------------
    print("\n" + "-" * 78)
    print("A  MODI DI MORTE — quanto pesa ognuno sull'E[R]")
    print(f"  {'esito':8} {'n':>6} {'quota':>7} {'R medio':>9} {'contributo E[R]':>16}")
    for o in ("TP", "SL", "BE", "TIME"):
        s = tr[tr["outcome"] == o]
        if not len(s):
            continue
        print(f"  {o:8} {len(s):6} {pct(len(s), n):>7} {s['R'].mean():+9.3f} "
              f"{s['R'].sum() / n:+16.3f}")
    print(f"  {'TOTALE':8} {n:6} {'100.0%':>7} {'':9} {tr['R'].sum() / n:+16.3f}")
    print(f"\n  win rate (TP) = {pct((tr['outcome'] == 'TP').sum(), n)}   "
          f"break-even a 1:3 = 25.0%")
    print(f"  perdite piene (-1R): {pct((tr['outcome'] == 'SL').sum(), n)}   "
          f"salvate dal BE (0R): {pct((tr['outcome'] == 'BE').sum(), n)}")
    amb = tr[(tr["outcome"].isin(("SL", "BE"))) & (tr["ambiguous"])]
    print(f"  stop su barra AMBIGUA (tocca anche il TP, bound pessimistico): {len(amb)}"
          f"  = {pct(len(amb), (tr['outcome'].isin(('SL', 'BE'))).sum())} degli stop")
    print(f"     se quelle barre fossero TP invece che SL, E[R] passerebbe a "
          f"{(tr['R'].sum() + len(amb) * (RR + 1)) / n:+.3f} (tetto ottimistico, NON il verdetto)")

    # ---------------- B. quando ----------------
    print("\n" + "-" * 78)
    print("B  QUANDO muoiono — barre H1 dal fill alla risoluzione")
    for lab, s in (("TUTTI", tr), ("stop -1R", tr[tr["outcome"] == "SL"]),
                   ("stop a BE", tr[tr["outcome"] == "BE"]), ("TP", tr[tr["outcome"] == "TP"])):
        if not len(s):
            continue
        h = s["hold"].to_numpy()
        print(f"  {lab:10} n={len(s):5}  p25={np.percentile(h, 25):5.0f}  "
              f"mediana={np.median(h):5.0f}  p75={np.percentile(h, 75):5.0f}  "
              f"p95={np.percentile(h, 95):6.0f}  max={h.max():5.0f}")
    sl = tr[tr["outcome"] == "SL"]
    print(f"\n  stop sulla BARRA DI INGRESSO (hold=0): {(sl['hold'] == 0).sum()}"
          f"  = {pct((sl['hold'] == 0).sum(), len(sl))} degli stop pieni")
    print(f"     -> entry e stop toccati nella STESSA ora: il livello di ingresso e lo stop"
          f" distano meno dell'escursione di una singola barra")
    for k in (1, 2, 3, 6, 12, 24):
        print(f"  stop entro {k:2} barre: {pct((sl['hold'] < k).sum(), len(sl)):>6}")

    # ---------------- C. favore prima di morire ----------------
    print("\n" + "-" * 78)
    print("C  QUANTO FAVORE prima di morire — MFE dei perdenti (in R, netto costi esclusi)")
    los = tr[tr["outcome"].isin(("SL", "BE"))]
    m = los["mfe"].to_numpy()
    print(f"  perdenti n={len(los)}   MFE mediana={np.median(m):+.2f}R   media={m.mean():+.2f}R")
    bins = [(-99, 0.0, "mai a favore  (MFE<=0)"), (0.0, 0.25, "0 - 0.25R"),
            (0.25, 0.5, "0.25 - 0.5R"), (0.5, 1.0, "0.5 - 1R"),
            (1.0, 2.0, "1R - 2R"), (2.0, 99, ">= 2R (BE armato)")]
    for a, b, lab in bins:
        k = ((m > a) & (m <= b)).sum()
        print(f"    {lab:24} {k:6}  {pct(k, len(los)):>7}")
    print(f"\n  LETTURA: 'mai a favore' + '0-0.25R' = "
          f"{pct(((m <= 0.25)).sum(), len(los))} dei perdenti muore senza che il prezzo"
          f" si sia mai mosso a favore in modo apprezzabile.")
    win = tr[tr["outcome"] == "TP"]
    if len(win):
        wm = win["mae"].to_numpy()
        print(f"\n  specularmente, MAE dei VINCENTI: mediana={np.median(wm):+.2f}R  "
              f"p10={np.percentile(wm, 10):+.2f}R  "
              f"quota di vincenti che ha sfiorato lo stop (MAE<=-0.75R): "
              f"{pct((wm <= -0.75).sum(), len(win))}")

    # ---------------- D. rumore ----------------
    print("\n" + "-" * 78)
    print("D  LO STOP VIVE DENTRO IL RUMORE? — ampiezza dello stop in ATR(14) H1")
    ra = tr["risk_atr"].dropna().to_numpy()
    la = tr["leg_atr"].dropna().to_numpy()
    print(f"  R (entry->SL) in ATR orari:  p10={np.percentile(ra, 10):.2f}  "
          f"p25={np.percentile(ra, 25):.2f}  mediana={np.median(ra):.2f}  "
          f"p75={np.percentile(ra, 75):.2f}  p90={np.percentile(ra, 90):.2f}")
    print(f"  ampiezza GAMBA in ATR orari: mediana={np.median(la):.2f}  (filtro: >= 1.0)")
    print(f"  quota di trade con stop piu' STRETTO di 1 ATR orario: "
          f"{pct((ra < 1.0).sum(), len(ra))}")
    print("\n  P(esito) per quintile di R/ATR  [DESCRITTIVO: selezionare qui = p-hacking, §4]")
    q = pd.qcut(tr["risk_atr"], 5, labels=False, duplicates="drop")
    print(f"    {'quintile':9} {'n':>6} {'R/ATR med':>10} {'SL%':>7} {'BE%':>7} {'TP%':>7} {'E[R]':>8}")
    for i in sorted(pd.Series(q).dropna().unique()):
        s = tr[q == i]
        print(f"    Q{int(i) + 1:<8} {len(s):6} {s['risk_atr'].median():10.2f} "
              f"{100 * (s['outcome'] == 'SL').mean():6.1f}% {100 * (s['outcome'] == 'BE').mean():6.1f}% "
              f"{100 * (s['outcome'] == 'TP').mean():6.1f}% {s['R'].mean():+8.3f}")

    # ---------------- E. ore ----------------
    print("\n" + "-" * 78)
    print("E  ORE DEL GIORNO — stop normalizzati per ESPOSIZIONE (barre-posizione aperte)")
    print("   NB: fuso del FEED (broker legacy), non necessariamente = fuso del conto live.")
    pf = prof.groupby("hour").agg(vol=("vol", "mean"), rng=("rng", "mean"))
    so = collections.Counter(tr[tr["outcome"].isin(("SL", "BE"))]["hour_out"])
    to = collections.Counter(tr[tr["outcome"] == "TP"]["hour_out"])
    base = sum(so.values()) / max(sum(EXPO.values()), 1)
    print(f"    {'ora':>3} {'esposiz.':>9} {'stop':>6} {'stop/esp':>9} {'indice':>7} "
          f"{'TP':>5} {'vol.med':>8} {'range/ATR':>10}")
    for h in range(24):
        e = EXPO.get(h, 0)
        r = so.get(h, 0) / e if e else float("nan")
        idx = r / base if base and e else float("nan")
        v = pf["vol"].get(h, float("nan"))
        rr = pf["rng"].get(h, float("nan"))
        flag = ""
        if e and idx == idx:
            flag = "  <<<" if idx >= 1.25 else ("  <" if idx >= 1.10 else "")
        print(f"    {h:3} {e:9} {so.get(h, 0):6} {r:9.4f} {idx:7.2f} {to.get(h, 0):5} "
              f"{v:8.0f} {rr:10.2f}{flag}")
    hmin = pf["vol"].idxmin()
    print(f"\n  ora a volume MINIMO del feed: h{hmin} (vol medio {pf['vol'].min():.0f}"
          f" contro {pf['vol'].max():.0f} del massimo, h{pf['vol'].idxmax()})")
    print(f"  indice stop/esposizione a h{hmin}: "
          f"{(so.get(hmin, 0) / EXPO[hmin]) / base:.2f}" if EXPO.get(hmin) else "")

    # ---------------- F. salti ----------------
    print("\n" + "-" * 78)
    print("F  IL SALTO ATTRAVERSO LO STOP — quando la barra APRE gia' oltre")
    stops = tr[tr["outcome"].isin(("SL", "BE"))]
    jm = stops[stops["jumped"]]
    print(f"  stop totali={len(stops)}  con salto={len(jm)} ({pct(len(jm), len(stops))})")
    print(f"  su quelli col salto: R vero medio={jm['R'].mean():+.3f} contro "
          f"{jm['R_assumed'].mean():+.3f} assunto -> scarto {(jm['R'] - jm['R_assumed']).mean():+.3f}R")
    print(f"  costo sull'E[R] complessivo: {(tr['R'].mean() - tr['R_assumed'].mean()):+.4f}R")
    print(f"\n  distribuzione dei salti per ORA di apertura barra:")
    jh = collections.Counter(jm["hour_out"])
    sh = collections.Counter(stops["hour_out"])
    for h in range(24):
        if sh.get(h, 0) < 20:
            continue
        print(f"    h{h:02}  stop={sh[h]:5}  saltati={jh.get(h, 0):5}  "
              f"quota={100 * jh.get(h, 0) / sh[h]:5.1f}%")
    print(f"\n  per giorno della settimana (0=lun):")
    for d_ in range(7):
        s_ = stops[stops["dow_out"] == d_]
        if len(s_) < 20:
            continue
        print(f"    dow{d_}  stop={len(s_):5}  saltati={s_['jumped'].sum():5}  "
              f"quota={100 * s_['jumped'].mean():5.1f}%  scarto medio sul totale="
              f"{(s_['R'] - s_['R_assumed']).mean():+.4f}R")

    # ---------------- G. random ----------------
    print("\n" + "-" * 78)
    print("G  CONTROLLO — un'entrata CASUALE con lo STESSO stop muore allo stesso modo?")
    print(f"  (stesso asset, stesso lato, stesso rischio in prezzo, istante casuale, "
          f"stesse regole. n_random={len(rd)})")
    print(f"    {'metrica':26} {'FADE reale':>12} {'random matched':>15}")
    rows_cmp = [
        ("E[R]", tr["R"].mean(), rd["R"].mean()),
        ("quota TP", 100 * (tr["outcome"] == "TP").mean(), 100 * (rd["outcome"] == "TP").mean()),
        ("quota SL piena", 100 * (tr["outcome"] == "SL").mean(), 100 * (rd["outcome"] == "SL").mean()),
        ("quota BE (0R)", 100 * (tr["outcome"] == "BE").mean(), 100 * (rd["outcome"] == "BE").mean()),
        ("holding mediano (barre)", tr["hold"].median(), rd["hold"].median()),
        ("MFE mediana dei perdenti",
         np.median(tr[tr["outcome"].isin(("SL", "BE"))]["mfe"]),
         np.median(rd[rd["outcome"].isin(("SL", "BE"))]["mfe"])),
        ("stop su barra d'ingresso %",
         100 * (tr[tr["outcome"] == "SL"]["hold"] == 0).mean(),
         100 * (rd[rd["outcome"] == "SL"]["hold"] == 0).mean()),
        ("stop col salto %",
         100 * tr[tr["outcome"].isin(("SL", "BE"))]["jumped"].mean(),
         100 * rd[rd["outcome"].isin(("SL", "BE"))]["jumped"].mean()),
    ]
    for lab, a, b in rows_cmp:
        print(f"    {lab:26} {a:12.3f} {b:15.3f}")

    # differenza APPAIATA: ogni trade reale contro la media dei suoi controlli
    rmean = rd.groupby("parent")["R"].mean()
    pair = tr.set_index("tid")["R"].reindex(rmean.index) - rmean
    pair = pair.dropna().to_numpy()
    ci = bt.qm.bca_bootstrap_ci(pair, metric=lambda x: float(np.mean(x)), conf=0.95,
                                n_boot=3000, seed=SEED)
    print(f"\n  differenza APPAIATA (reale - media dei suoi {M_RANDOM} controlli), n={len(pair)}:")
    print(f"    {pair.mean():+.3f}R   BCa95 [{ci['low']:+.3f}, {ci['high']:+.3f}]   "
          f"P(diff>0) empirica = {100 * np.mean(pair > 0):.1f}%")

    # il gradiente R/ATR e' una proprieta' del FADE o della sola geometria a barriere?
    print(f"\n  Il gradiente R/ATR della sezione D vale anche per il RANDOM?")
    edges = np.quantile(tr["risk_atr"].dropna(), [0, .2, .4, .6, .8, 1.0])
    edges[0], edges[-1] = -np.inf, np.inf
    qr = pd.cut(tr["risk_atr"], edges, labels=False)
    qc = pd.cut(rd["risk_atr"], edges, labels=False)
    print(f"    {'quintile':9} {'E[R] fade':>10} {'E[R] random':>12} {'diff':>8} "
          f"{'TP% fade':>9} {'TP% random':>11}")
    for i in range(5):
        a_, b_ = tr[qr == i], rd[qc == i]
        if not len(a_) or not len(b_):
            continue
        print(f"    Q{i + 1:<8} {a_['R'].mean():+10.3f} {b_['R'].mean():+12.3f} "
              f"{a_['R'].mean() - b_['R'].mean():+8.3f} "
              f"{100 * (a_['outcome'] == 'TP').mean():8.1f}% {100 * (b_['outcome'] == 'TP').mean():10.1f}%")

    # ---------------- H. per asset ----------------
    print("\n" + "-" * 78)
    print("H  PER STRUMENTO")
    print(f"  {'asset':8} {'n':>6} {'SL%':>7} {'BE%':>7} {'TP%':>7} {'hold med':>9} "
          f"{'R/ATR med':>10} {'salti%':>8} {'E[R]':>8}")
    for s_, g in tr.groupby("sym"):
        st = g[g["outcome"].isin(("SL", "BE"))]
        print(f"  {s_:8} {len(g):6} {100 * (g['outcome'] == 'SL').mean():6.1f}% "
              f"{100 * (g['outcome'] == 'BE').mean():6.1f}% {100 * (g['outcome'] == 'TP').mean():6.1f}% "
              f"{g['hold'].median():9.0f} {g['risk_atr'].median():10.2f} "
              f"{100 * st['jumped'].mean():7.1f}% {g['R'].mean():+8.3f}")

    out = os.path.join(HERE, "stops_trades.csv")
    tr.to_csv(out, index=False)
    print(f"\nTrade log -> {out}")


if __name__ == "__main__":
    main()
