"""B3 - la condizione di STRUTTURA sull'estensione estrema porta informazione?

Protocollo scritto prima: docs/B3_EXTENSION_STRUCTURE_PROTOCOL.md. Soglie, celle, direzione
attesa e significato di un mancato rifiuto sono fissati li'.

Due fonti indipendenti (Marius C3.4, Kyle C3.5) convergono non su "l'estensione estrema si
inverte" - lo dicono in cinque - ma su QUALE estensione: quella fatta di **poche candele grandi**
con **volume in espansione**. Qui si misura se quella distinzione esiste sui nostri dati.

Costo: 0 trial. Misura descrittiva con predizione pre-dichiarata; nessun parametro scelto
guardando l'esito, nessuna cella promossa a regola.

    python analysis/extension/structure.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analysis", "trend"))

from backtest import ATR_N, atr, load, universe_from_coverage  # noqa: E402
from core import quant_metrics as qm                           # noqa: E402
from core.random_baseline import BarSampler, check_matching, gap_ci  # noqa: E402

# --- parametri PRE-DICHIARATI (docs/B3_..._PROTOCOL.md sez.3) ---------------
L_MIN, L_MAX = 2, 5          # mai il primo giorno; non piu' di 5 = accumulazione ordinata
E_PRIM = 3.0                 # soglia primaria di estensione, in ATR pre-corsa
E_ROBUST = (2.0, 4.0)        # robustezza riportata, NON decisionale
BASE_WIN = 10                # barre di riferimento prima della corsa
F_SU, F_GIU = 1.2, 1.0       # forma: espansione / contrazione
V_SU, V_GIU = 1.2, 1.0       # volume: espansione / contrazione
ORIZZONTI = (1, 2, 3, 5)     # barre; h=2 e' l'orizzonte PRIMARIO
H_PRIM = 2
M_RANDOM = 3
SEED = 42

# --- gate di usabilita' del volume (sez.2), dichiarato prima ---------------
VOL_ZERI_MAX = 0.05
VOL_CORR_MIN = 0.15
VOL_MEDIANA_MIN = 10.0


def volume_usabile(d):
    """La colonna `volume` si comporta come un volume? Tre criteri dichiarati prima."""
    v = d["volume"].to_numpy(float)
    c = d["close"].to_numpy(float)
    if len(v) < 200:
        return False, "campione corto", {}
    zeri = float(np.mean(v == 0))
    med = float(np.median(v))
    r = np.abs(np.diff(np.log(c)))
    ok = np.isfinite(v[1:]) & np.isfinite(r)
    corr = float(np.corrcoef(v[1:][ok], r[ok])[0, 1]) if ok.sum() > 50 else np.nan
    m = {"zeri": zeri, "corr": corr, "mediana": med}
    motivi = []
    if zeri >= VOL_ZERI_MAX:
        motivi.append("zeri %.1f%%" % (100 * zeri))
    if not np.isfinite(corr) or corr < VOL_CORR_MIN:
        motivi.append("corr %.2f" % corr)
    if med < VOL_MEDIANA_MIN:
        motivi.append("mediana %.1f" % med)
    return (not motivi), (", ".join(motivi) or "ok"), m


def eventi_asset(sym, grp, t0, rng):
    """Eventi di estensione estrema + controlli random appaiati per orizzonte."""
    d = load(sym, grp)
    d = d[d["time"] >= t0].reset_index(drop=True)
    if len(d) < 300:
        return pd.DataFrame(), pd.DataFrame(), None
    O, H, L, C = (d[c].values.astype(float) for c in ("open", "high", "low", "close"))
    V = d["volume"].values.astype(float)
    A = atr(H, L, C)
    rng_bar = H - L
    anni = pd.DatetimeIndex(d["time"]).year.values
    n = len(C)
    vol_ok, vol_motivo, vol_m = volume_usabile(d)

    valid = np.flatnonzero(np.isfinite(A) & (A > 0))
    lo_v, hi_v = (valid[0], valid[-1]) if len(valid) else (0, 0)
    usable = (np.arange(n) >= lo_v + BASE_WIN) & (np.arange(n) <= hi_v - max(ORIZZONTI) - 2)
    sampler = BarSampler(anni, rng, usable=usable)

    # lunghezza della corsa di chiusure nella stessa direzione che finisce in t
    su = np.zeros(n, dtype=int)
    giu = np.zeros(n, dtype=int)
    for t in range(1, n):
        su[t] = su[t - 1] + 1 if C[t] > C[t - 1] else 0
        giu[t] = giu[t - 1] + 1 if C[t] < C[t - 1] else 0

    reali, ctrl = [], []
    for t in range(ATR_N + BASE_WIN + L_MAX + 1, n - max(ORIZZONTI) - 2):
        lung, direz = (su[t], +1) if su[t] >= L_MIN else (
            (giu[t], -1) if giu[t] >= L_MIN else (0, 0))
        if lung < L_MIN or lung > L_MAX:
            continue
        i0 = t - lung                      # ultima barra PRIMA della corsa
        a0 = A[i0 - 1]                     # ATR noto prima che la corsa inizi
        if not np.isfinite(a0) or a0 <= 0:
            continue
        E = abs(C[t] - C[i0]) / a0
        if E < min(E_ROBUST[0], E_PRIM):
            continue
        base = slice(i0 - BASE_WIN, i0)
        mr = float(np.nanmean(rng_bar[base]))
        mv = float(np.nanmean(V[base]))
        F = float(np.nanmean(rng_bar[i0 + 1:t + 1])) / mr if mr > 0 else np.nan
        Vr = (float(np.nanmean(V[i0 + 1:t + 1])) / mv) if (vol_ok and mv > 0) else np.nan

        rec = {"sym": sym, "group": grp, "anno": int(anni[t]), "t": t, "L": lung,
               "dir": direz, "E": E, "F": F, "Vr": Vr, "atr0": a0,
               "evid": "%s:%d" % (sym, t), "vol_ok": vol_ok}
        # rendimento orientato alla corsa: positivo = CONTINUAZIONE
        for h in ORIZZONTI:
            f, u = t + 1, t + 1 + h
            rec["R%d" % h] = (direz * (O[u] - O[f]) / a0) if u <= n - 1 else np.nan
        reali.append(rec)

        for k in sampler.draw(anni[t], M_RANDOM):
            a1 = A[k - 1] if k - 1 >= 0 else np.nan
            if not np.isfinite(a1) or a1 <= 0:
                continue
            c = {"sym": sym, "group": grp, "anno": int(anni[k]), "dir": direz,
                 "evid": rec["evid"]}
            for h in ORIZZONTI:
                f, u = k + 1, k + 1 + h
                c["R%d" % h] = (direz * (O[u] - O[f]) / a1) if u <= n - 1 else np.nan
            ctrl.append(c)
    return pd.DataFrame(reali), pd.DataFrame(ctrl), (vol_ok, vol_motivo, vol_m)


def cella(row):
    """Le quattro celle del protocollo sez.5. NaN se il volume non e' usabile."""
    if not np.isfinite(row["F"]):
        return None
    f = "range+" if row["F"] >= F_SU else ("range-" if row["F"] <= F_GIU else None)
    if f is None:
        return None
    if not np.isfinite(row["Vr"]):
        return f + " / vol n.d."
    v = "vol+" if row["Vr"] >= V_SU else ("vol-" if row["Vr"] <= V_GIU else None)
    if v is None:
        return None
    return f + " / " + v


def mde(sd, n):
    """Effetto minimo rilevabile: 2,80 * SE, alpha 0,05 bilaterale e potenza 80%."""
    if n < 3 or not np.isfinite(sd):
        return float("nan")
    return 2.801 * sd / np.sqrt(n)


def riga_gap(eti, reali, ctrl, h):
    col = "R%d" % h
    g = gap_ci(reali.assign(val=reali[col]), ctrl.assign(val=ctrl[col]),
               value="val", link="evid", n_boot=2000, seed=SEED)
    n = g["n_eventi"]
    med = ctrl.groupby("evid")[col].mean()
    dif = (reali.set_index("evid")[col] - med.reindex(reali["evid"]).to_numpy()).dropna()
    m = mde(float(dif.std(ddof=1)), len(dif)) if len(dif) > 2 else float("nan")
    stella = ""
    if np.isfinite(g["low"]) and (g["low"] > 0 or g["high"] < 0):
        stella = "  <-- esclude 0"
    print("  %-26s n=%-5d reale=%+.3f random=%+.3f  diff=%+.3f [%+.3f;%+.3f]  MDE=%.3f%s"
          % (eti, n, g["media_reale"], g["media_random"], g["gap"], g["low"], g["high"],
             m, stella))
    return g, m


def main() -> int:
    cov = universe_from_coverage()
    t0 = cov["start"].max()
    rng = np.random.default_rng(SEED)
    R, D, volinfo = [], [], {}
    for _, r in cov.iterrows():
        a, b, vi = eventi_asset(r["sym"], r["group"], t0, rng)
        if vi is not None:
            volinfo[r["sym"]] = vi
        if len(a):
            R.append(a)
        if len(b):
            D.append(b)
    reali = pd.concat(R, ignore_index=True)
    ctrl = pd.concat(D, ignore_index=True)

    print("=" * 92)
    print("B3 - CONDIZIONE DI STRUTTURA SULL'ESTENSIONE ESTREMA")
    print("protocollo: docs/B3_EXTENSION_STRUCTURE_PROTOCOL.md   (0 trial)")
    print("finestra %s+   %d strumenti   soglia primaria E>=%.1f ATR   L in [%d,%d]"
          % (t0.date(), len(volinfo), E_PRIM, L_MIN, L_MAX))
    print("=" * 92)

    print("\n--- GATE VOLUME (sez.2): la colonna si comporta come un volume?")
    ok = [s for s, v in volinfo.items() if v[0]]
    ko = [s for s, v in volinfo.items() if not v[0]]
    print("  passano %d su %d: %s" % (len(ok), len(volinfo), ", ".join(sorted(ok))))
    print("\n  NON passano (la gamba VOLUME non viene misurata li'):")
    for s in sorted(ko):
        print("    %-9s %s" % (s, volinfo[s][1]))
    gruppi_ko = sorted({cov.set_index("sym").loc[s, "group"] for s in ko})
    print("  gruppi coinvolti: %s" % ", ".join(gruppi_ko))

    # --- filtro alla soglia primaria ---
    ev = reali[reali["E"] >= E_PRIM].copy()
    ev["cella"] = ev.apply(cella, axis=1)
    cc = ctrl[ctrl["evid"].isin(set(ev["evid"]))]

    print("\n--- EVENTI alla soglia primaria E>=%.1f" % E_PRIM)
    print("  %d eventi su %d strumenti, %d controlli (m=%d)"
          % (len(ev), ev["sym"].nunique(), len(cc), M_RANDOM))
    print("  per direzione: su %d, giu %d" % (int((ev["dir"] > 0).sum()),
                                              int((ev["dir"] < 0).sum())))
    print("  lunghezza corsa: " + "  ".join(
        "L=%d:%d" % (k, v) for k, v in sorted(ev["L"].value_counts().items())))

    print()
    print(check_matching(ev, cc, link="evid", exact=("sym", "dir", "anno"),
                         numeric=(), observed=()))

    print("\n--- TUTTI gli eventi, per orizzonte (positivo = CONTINUAZIONE)")
    for h in ORIZZONTI:
        riga_gap("h=%d%s" % (h, "  PRIMARIO" if h == H_PRIM else ""), ev, cc, h)

    print()
    print("--- LE CELLE ESISTONO? forma per lunghezza della corsa")
    print("  Se normalizzare sull'ATR rende 'estensione estrema' e 'candele grandi' la STESSA")
    print("  cosa, la distinzione delle fonti non e' testabile: sparisce per costruzione.")
    print("  %-6s %7s %9s %9s %9s" % ("L", "n", "range+", "range-", "in mezzo"))
    for LL in range(L_MIN, L_MAX + 1):
        sub = ev[ev["L"] == LL]
        if not len(sub):
            continue
        su_ = int((sub["F"] >= F_SU).sum())
        gi_ = int((sub["F"] <= F_GIU).sum())
        print("  %-6d %7d %8.1f%% %8.1f%% %8.1f%%"
              % (LL, len(sub), 100 * su_ / len(sub), 100 * gi_ / len(sub),
                 100 * (len(sub) - su_ - gi_) / len(sub)))
    print("  correlazione di rango fra estensione E e forma F: %.3f"
          % float(ev[["E", "F"]].corr(method="spearman").iloc[0, 1]))

    print()
    print("--- BREADTH per gruppo (tutti gli eventi, h=%d)" % H_PRIM)
    print("  %-9s %7s %10s %10s %10s" % ("gruppo", "n", "reale", "random", "diff"))
    neg = 0
    ngr = 0
    for g, gg in ev.groupby("group"):
        cg = cc[cc["evid"].isin(set(gg["evid"]))]
        col = "R%d" % H_PRIM
        med = cg.groupby("evid")[col].mean()
        dd = (gg.set_index("evid")[col] - med.reindex(gg["evid"]).to_numpy()).dropna()
        if len(dd) < 20:
            continue
        ngr += 1
        neg += int(dd.mean() < 0)
        print("  %-9s %7d %+10.3f %+10.3f %+10.3f"
              % (g, len(gg), gg[col].mean(), cg[col].mean(), dd.mean()))
    print("  gruppi con differenza NEGATIVA (= inversione, la direzione attesa): %d/%d"
          % (neg, ngr))

    print()
    print("--- LE QUATTRO CELLE, orizzonte primario h=%d" % H_PRIM)
    print("  predizione dichiarata: 'range+ / vol+' e' la PIU' NEGATIVA e il suo CI esclude 0")
    risultati = {}
    for c in ("range+ / vol+", "range+ / vol-", "range- / vol+", "range- / vol-"):
        sub = ev[ev["cella"] == c]
        if len(sub) < 30:
            print("  %-26s n=%-5d campione troppo piccolo" % (c, len(sub)))
            continue
        g, m = riga_gap(c, sub, cc[cc["evid"].isin(set(sub["evid"]))], H_PRIM)
        risultati[c] = g

    nd = ev[ev["cella"].astype(str).str.contains("vol n.d.", na=False)]
    if len(nd) >= 30:
        print("\n  (strumenti senza volume usabile, solo gamba FORMA)")
        for c in ("range+ / vol n.d.", "range- / vol n.d."):
            sub = ev[ev["cella"] == c]
            if len(sub) >= 30:
                riga_gap(c, sub, cc[cc["evid"].isin(set(sub["evid"]))], H_PRIM)

    print("\n--- ROBUSTEZZA sulla soglia di estensione (riportata, NON decisionale)")
    for e in sorted(set(E_ROBUST) | {E_PRIM}):
        sub = reali[reali["E"] >= e].copy()
        sub["cella"] = sub.apply(cella, axis=1)
        s2 = sub[sub["cella"] == "range+ / vol+"]
        if len(s2) < 30:
            print("  E>=%.1f  cella attesa n=%d: troppo piccolo" % (e, len(s2)))
            continue
        riga_gap("E>=%.1f  range+ / vol+" % e, s2,
                 ctrl[ctrl["evid"].isin(set(s2["evid"]))], H_PRIM)

    # --- verdetto secondo H1/H2 dichiarate prima ---
    print("\n" + "=" * 92)
    print("ESITO secondo docs/B3_EXTENSION_STRUCTURE_PROTOCOL.md sez.5 (scritta prima)")
    print("=" * 92)
    att = risultati.get("range+ / vol+")
    if att is None:
        print("  NON VALUTABILE: la cella attesa non ha campione sufficiente.")
        return 0
    h1 = np.isfinite(att["high"]) and att["high"] < 0
    altri = [v["gap"] for k, v in risultati.items() if k != "range+ / vol+"]
    h2 = bool(altri) and att["gap"] < min(altri)
    print("  H1  la cella attesa e' negativa e il CI esclude 0: %s  (gap %+.3f [%+.3f;%+.3f])"
          % ("SI" if h1 else "NO", att["gap"], att["low"], att["high"]))
    if len(risultati) < 4:
        print("  H2  NON VALUTABILE: solo %d celle su 4 hanno campione sufficiente."
              % len(risultati))
        print("      Le celle a range in contrazione sono quasi vuote, e non per caso: vedi la")
        print("      tabella 'LE CELLE ESISTONO?'. Dichiarare H2 vera confrontando due celle su")
        print("      quattro sarebbe un risultato costruito.")
        h2 = False
    else:
        print("  H2  la cella attesa e' la piu' negativa delle quattro: %s"
              % ("SI" if h2 else "NO"))
    if h1 and h2:
        print("\n  La condizione di struttura PORTA INFORMAZIONE sul nostro universo.")
        print("  -> non e' una regola: e' una casella descrittiva confermata. Trasformarla in")
        print("     regola sarebbe un trial e una pre-registrazione nuova.")
    else:
        print("\n  La condizione di struttura NON porta informazione misurabile qui.")
        print("  Leggere l'MDE accanto a ogni riga: un'assenza senza MDE non e' un risultato.")
        print("  Non significa che le fonti sbaglino sul LORO universo (small/mid cap USA con")
        print("  float ristretto, squeeze, halt): significa che la condizione non e' trasferibile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
