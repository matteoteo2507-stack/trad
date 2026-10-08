"""Test unico pre-registrato: RSI(2) di Connors sugli indici USA (candidato A).

Pre-registrazione: docs/MR_INDICI_RSI2_PREREGISTRATION.md. Su dati REALI lo script non parte finche' il frontmatter
della pre-registrazione non dice `stato: APPROVATA` e la soglia di chiusura non e' fissata. Con `--sintetico` gira su
due serie giornaliere seminate, con deriva e correlazione regolabili come quelle degli indici veri: serve a controllare
il codice senza guardare il mercato.

    python analysis/meanrev_indici/esegui_test.py --sintetico                       # nullo con deriva e rho 0,9
    python analysis/meanrev_indici/esegui_test.py --sintetico --forza 0.3           # controllo positivo
    python analysis/meanrev_indici/esegui_test.py                                   # IL test (una volta, dopo l'approvazione)

Regola (§2), stessa esecuzione per i due bracci (funzione `chiudi`):
  segnale alla chiusura del giorno t: chiusura > SMA200 e RSI(2) < 10  -> long all'APERTURA di t+1
  uscita: alla prima chiusura con RSI(2) > 70, oppure alla chiusura del 10o giorno in posizione -> esce
          all'APERTURA del giorno dopo. Nessuno stop. Una posizione alla volta per indice (solo braccio reale).
Revisione G1 del 08/10 (gatekeeper): cluster per EPISODIO sovrapposto fra indici, niente trim_tail per anno, ATR al
segnale nel matching, controlli dati sul grezzo, precedenza dei verdetti dichiarata, PSR e futilita'.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from core import data_checks as dc                      # noqa: E402
from core import quant_metrics as qm                    # noqa: E402
from core.random_baseline import BarSampler, check_matching   # noqa: E402
from core.verifiche import runs_test                    # noqa: E402

PREREG = os.path.join(ROOT, "docs", "MR_INDICI_RSI2_PREREGISTRATION.md")
DATI = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")
# Costi FP Markets letti in MT5 il 08/10/2026 (FPMarkets-Demo): spread in punti indice, swap long per notte in % del
# prezzo (US500 −1,14 $/lotto su ~7.500 = 0,0152%; US100 −4,24 $/lotto su ~29.700 = 0,0143%), tripla il venerdi'.
COSTI = {"SPX500": {"spread_pt": 0.25, "swap_notte_pct": 0.0152},
         "NAS100": {"spread_pt": 0.60, "swap_notte_pct": 0.0143}}
RSI_IN, RSI_OUT, MAX_GIORNI, SMA_N = 10, 70, 10, 200
M_CONTROLLI, SEME, N_BOOT = 20, 42, 5000
SOGLIA_CHIUSURA = None     # la fissa Matteo prima dell'approvazione (bloccante 1 della revisione G1, §6)
K = 2.80                   # alpha 0,05 bilaterale, potenza 80%


# ---------------------------------------------------------------- dati
def carica(sym):
    grezzo = pd.read_csv(os.path.join(DATI, f"{sym}_D1.csv"), parse_dates=["time"])
    d = grezzo.set_index("time").sort_index()
    weekend = int((d.index.dayofweek >= 5).sum())
    d = d[d.index.dayofweek < 5]
    dup = int(d.index.duplicated().sum())
    d = d[~d.index.duplicated()][["open", "high", "low", "close"]]
    return d, grezzo, {"righe_grezze": len(grezzo), "barre_weekend_scartate": weekend, "duplicati_scartati": dup}


def sintetico_coppia(seme, forza=0.0, rho=0.9, deriva=0.0005):
    """Due serie giornaliere con shock correlati (rho) e deriva per giorno, barre dal percorso a passi di un'ora.
    `forza` > 0: richiamo verso una media mobile di ~5 giorni (ritorno alla media iniettato, controllo positivo)."""
    rng = np.random.default_rng(seme)
    idx = pd.bdate_range("2012-01-16", "2026-08-13")
    n, k = len(idx), 24
    z1 = rng.standard_t(5, (n, k)) / np.sqrt(5 / 3)
    z2 = rho * z1 + np.sqrt(1 - rho ** 2) * rng.standard_t(5, (n, k)) / np.sqrt(5 / 3)
    out = {}
    for sym, z, p0 in (("SPX500", z1, 1300.0), ("NAS100", z2, 2400.0)):
        passi = (z * (0.011 / np.sqrt(k)) + deriva / k).ravel()
        if forza <= 0:
            lp = (np.log(p0) + np.cumsum(passi)).reshape(n, k)
        else:
            lp = np.empty(passi.size); x = anc = np.log(p0)
            lam, kap = np.exp(-1 / (5 * k)), forza / k
            for j in range(passi.size):
                anc = lam * anc + (1 - lam) * x
                x = x - kap * (x - anc) + passi[j]
                lp[j] = x
            lp = lp.reshape(n, k)
        o = np.r_[np.log(p0), lp[:-1, -1]]
        d = pd.DataFrame({"open": np.exp(o), "high": np.exp(np.maximum(o, lp.max(1))),
                          "low": np.exp(np.minimum(o, lp.min(1))), "close": np.exp(lp[:, -1])}, index=idx)
        out[sym] = (d, d.reset_index().rename(columns={"index": "time"}),
                    {"righe_grezze": n, "barre_weekend_scartate": 0, "duplicati_scartati": 0})
    return out


def indicatori(d):
    c = d["close"]
    x = c.diff()
    up = x.clip(lower=0).ewm(alpha=0.5, adjust=False, min_periods=2).mean()
    dn = (-x.clip(upper=0)).ewm(alpha=0.5, adjust=False, min_periods=2).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    pc = c.shift(1)
    tr = pd.concat([d.high - d.low, (d.high - pc).abs(), (d.low - pc).abs()], axis=1).max(axis=1)
    atr_pct = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean() / c * 100
    return rsi.to_numpy(), c.rolling(SMA_N, min_periods=SMA_N).mean().to_numpy(), atr_pct.to_numpy()


# ---------------------------------------------------------------- un trade (STESSA esecuzione per i due bracci)
def notti(entrata: pd.Timestamp, uscita: pd.Timestamp) -> int:
    """Rollover fra l'apertura di `entrata` e quella di `uscita` (giorni feriali); il venerdi' vale 3."""
    g = pd.bdate_range(entrata, uscita)[:-1]
    return int(sum(3 if x.dayofweek == 4 else 1 for x in g))


def chiudi(d, t, e, x, sym, mult_costi=1.0):
    """Esecuzione comune ai due bracci: ingresso all'apertura di e, uscita all'apertura di x, costi FP Markets."""
    o, l = d["open"].to_numpy(), d["low"].to_numpy()
    entrata, uscita = o[e], o[x]
    lordo = (uscita - entrata) / entrata * 100
    c = COSTI[sym]
    nt = notti(d.index[e], d.index[x])
    costo = (c["spread_pt"] / entrata * 100 + nt * c["swap_notte_pct"]) * mult_costi
    mae = max(0.0, (entrata - l[e:x].min()) / entrata * 100)
    return {"sym": sym, "t": t, "segnale": d.index[t], "entrata": d.index[e], "uscita": d.index[x], "giorni": x - e,
            "notti": nt, "lordo": lordo, "netto": lordo - costo, "mae_pct": mae, "x": x}


def cammina(d, rsi, t, sym, mult_costi=1.0):
    """Regola d'uscita del §2. None se i dati finiscono prima dell'uscita."""
    e = t + 1
    if e >= len(d) - 1:
        return None
    k = e
    while True:
        if rsi[k] > RSI_OUT or (k - e + 1) >= MAX_GIORNI:
            x = k + 1
            break
        k += 1
        if k >= len(d) - 1:
            return None
    if x >= len(d):
        return None
    return chiudi(d, t, e, x, sym, mult_costi)


def cammina_durata(d, t, sym, giorni, mult_costi=1.0):
    """Braccio casuale PRIMARIO: stessa esecuzione, tiene esattamente i giorni del trade reale appaiato."""
    e, x = t + 1, t + 1 + giorni
    if x >= len(d):
        return None
    return chiudi(d, t, e, x, sym, mult_costi)


def braccio_reale(d, rsi, sma, sym):
    out = []
    t = int(np.argmax(np.isfinite(sma)))          # primo giorno con la SMA200 valida
    while t < len(d) - 1:
        if np.isfinite(sma[t]) and d["close"].iloc[t] > sma[t] and rsi[t] < RSI_IN:
            tr = cammina(d, rsi, t, sym)
            if tr is None:
                break
            out.append(tr)
            t = tr["x"]
        else:
            t += 1
    return out


def braccio_casuale(d, rsi, sma, atr, sym, reali, rng, durata_copiata=True):
    """Solo l'istante e' casuale: stesso indice, stesso anno, stesso regime (sopra SMA200). Uscita: con
    `durata_copiata` (PRIMARIO) i giorni del trade reale appaiato; altrimenti la regola d'uscita (descrittivo).
    Niente trim_tail per anno: la fine serie la gestiscono `cammina*` (None)."""
    sopra = np.isfinite(sma) & (d["close"].to_numpy() > np.nan_to_num(sma, nan=np.inf))
    strata = np.array([f"{sym}-{y}" for y in d.index.year])
    bs = BarSampler(strata, rng, usable=sopra, trim_tail=0, min_pool=MAX_GIORNI + 3)
    out, senza = [], 0
    for r in reali:
        n0 = len(out)
        for t in bs.draw(f"{sym}-{r['segnale'].year}", M_CONTROLLI):
            tr = cammina_durata(d, t, sym, r["giorni"]) if durata_copiata else cammina(d, rsi, t, sym)
            if tr is not None:
                tr["evento"] = r["evento"]
                tr["atr_pct"] = float(atr[t])
                out.append(tr)
        senza += len(out) == n0
    return out, senza


# ---------------------------------------------------------------- statistica a cluster per episodio
def episodi(R: pd.DataFrame) -> np.ndarray:
    """Componenti connesse degli intervalli [entrata, uscita) sovrapposti, su entrambi gli indici: trade che si
    sovrappongono nel tempo (anche entrati in giorni diversi) sono un episodio solo."""
    ordine = R.sort_values("entrata")
    lab, cur, fine = {}, -1, pd.Timestamp.min
    for i, row in ordine.iterrows():
        if row.entrata >= fine:
            cur += 1
            fine = row.uscita
        else:
            fine = max(fine, row.uscita)
        lab[i] = cur
    return R.index.map(lab).to_numpy()


def ci_episodi(valori, ep, conf=0.95, seme=SEME):
    """Media PER TRADE, IC percentile con bootstrap degli episodi (si ricampionano episodi, si fa la media dei trade
    contenuti). MDE = 2,80 x errore standard del bootstrap."""
    v = np.asarray(valori, float)
    ep = np.asarray(ep)
    gruppi = [v[ep == g] for g in np.unique(ep)]
    s = np.array([g.sum() for g in gruppi]); n = np.array([len(g) for g in gruppi])
    rng = np.random.default_rng(seme)
    idx = rng.integers(0, len(gruppi), (N_BOOT, len(gruppi)))
    medie = s[idx].sum(1) / n[idx].sum(1)
    a = (1 - conf) / 2
    return {"media": float(v.mean()), "low": float(np.quantile(medie, a)), "high": float(np.quantile(medie, 1 - a)),
            "se": float(medie.std(ddof=1)), "mde": float(K * medie.std(ddof=1)), "n_episodi": len(gruppi)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sintetico", action="store_true")
    ap.add_argument("--forza", type=float, default=0.0)
    ap.add_argument("--rho", type=float, default=0.9)
    ap.add_argument("--deriva", type=float, default=0.0005, help="deriva giornaliera (0,0005 = 0,05%% al giorno)")
    ap.add_argument("--seme", type=int, default=7)
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not a.sintetico:
        import yaml
        testo = open(PREREG, encoding="utf-8").read()
        fm = yaml.safe_load(testo[3:testo.find("\n---", 3)]) if testo.startswith("---") else {}
        if str((fm or {}).get("stato", "")).upper() != "APPROVATA":
            print(f"La pre-registrazione e' in stato '{(fm or {}).get('stato')}': il test sui dati reali parte solo se APPROVATA.")
            return 2
        if SOGLIA_CHIUSURA is None:
            print("SOGLIA_CHIUSURA non fissata: va scritta prima dell'esecuzione (§6).")
            return 2
    soglia = SOGLIA_CHIUSURA if SOGLIA_CHIUSURA is not None else 0.50
    etichetta = (f"SINTETICO (forza {a.forza}, rho {a.rho}, deriva {a.deriva}, seme {a.seme})" if a.sintetico
                 else "DATI REALI")
    sorgenti = sintetico_coppia(a.seme, a.forza, a.rho, a.deriva) if a.sintetico else {s: carica(s) for s in COSTI}
    print(f"=== RSI(2) indici USA — {etichetta} ===")
    print(dc.checklist_dati({s: g for s, (_, g, _) in sorgenti.items()}))
    for s, (_, _, info) in sorgenti.items():
        print(f"  {s} grezzo: {info}")
    rng = np.random.default_rng(SEME)
    rng2 = np.random.default_rng(SEME + 1)
    reali, casuali, casuali_regola, stress, senza = [], [], [], {}, 0
    for s, (d, _, _) in sorgenti.items():
        rsi, sma, atr = indicatori(d)
        r = braccio_reale(d, rsi, sma, s)
        for i, x in enumerate(r):
            x["evento"] = f"{s}-{i}"
            x["atr_pct"] = float(atr[x["t"]])
            stress[x["evento"]] = cammina(d, rsi, x["t"], s, mult_costi=3.0)["netto"]
        reali += r
        c1, n1 = braccio_casuale(d, rsi, sma, atr, s, r, rng, durata_copiata=True)
        c2, _ = braccio_casuale(d, rsi, sma, atr, s, r, rng2, durata_copiata=False)
        casuali += c1; casuali_regola += c2; senza += n1
    R, C, C2 = pd.DataFrame(reali), pd.DataFrame(casuali), pd.DataFrame(casuali_regola)
    for X in (R, C):
        X["side"] = "long"; X["asset"] = X["sym"]; X["hold"] = X["giorni"]; X["atr"] = X["atr_pct"]
    print()
    print(check_matching(R, C, link="evento", exact=("asset", "side"), numeric=(), observed=("hold", "atr")))
    print(f"\nTrade reali: {len(R)} (SPX {int((R.sym == 'SPX500').sum())}, NAS {int((R.sym == 'NAS100').sum())}); "
          f"controlli: {len(C)}; eventi SENZA controlli (esclusi dal divario): {senza}")
    print(f"Fill non ottenibili: 0 su {len(R)} (per costruzione: ingresso e uscita a mercato all'apertura successiva)")
    print(f"Tenuta mediana: reale {R.giorni.median():.0f} giorni, casuale {C.giorni.median():.0f}; "
          f"notti medie {R.notti.mean():.1f} contro {C.notti.mean():.1f}")

    ep = episodi(R)
    R["episodio"] = ep
    print(f"Episodi (trade sovrapposti fra indici = un episodio): {len(np.unique(ep))} su {len(R)} trade")
    netto = ci_episodi(R.netto, ep)
    lordo = ci_episodi(R.lordo, ep)
    netto3 = float(np.mean([stress[e] for e in R.evento]))
    med_c = C.groupby("evento")["netto"].mean()
    con = R[R.evento.isin(med_c.index)]
    gap_v = con.netto.to_numpy() - med_c.loc[con.evento].to_numpy()
    gap = ci_episodi(gap_v, con.episodio.to_numpy())
    print(f"\n[1] Attesa NETTA reale: {netto['media']:+.3f}% a trade  IC95 [{netto['low']:+.3f}; {netto['high']:+.3f}]"
          f"  (episodi {netto['n_episodi']}, MDE {netto['mde']:.3f}%)")
    print(f"    con costi 3x: {netto3:+.3f}%   |   LORDA: {lordo['media']:+.3f}% IC95 [{lordo['low']:+.3f}; {lordo['high']:+.3f}]")
    print(f"[2] Divario reale − casuale a durata copiata (netto): {gap['media']:+.3f}%  IC95 [{gap['low']:+.3f}; "
          f"{gap['high']:+.3f}]  (MDE {gap['mde']:.3f}%)")
    print(f"    media casuale {C.netto.mean():+.3f}% a trade")
    per_ind = {s: float(np.mean(gap_v[con.sym.to_numpy() == s])) for s in COSTI}
    print("    divario puntuale per indice: " + ", ".join(f"{s} {v:+.3f}%" for s, v in per_ind.items()))
    c_atr = C.assign(r=C.netto / C.atr_pct).groupby("evento").r.mean()
    g_atr = con.netto.to_numpy() / con.atr_pct.to_numpy() - c_atr.loc[con.evento].to_numpy()
    print(f"    descrittivo, divario in unita' di ATR al segnale: {np.mean(g_atr):+.3f}")
    med_c2 = C2.groupby("evento")["netto"].mean()
    d2 = (R.set_index("evento")["netto"] - med_c2).dropna()
    print(f"    descrittivo, baseline con la STESSA regola d'uscita (confuso dalla durata): divario {d2.mean():+.3f}%, "
          f"tenuta mediana casuale {C2.giorni.median():.0f} giorni contro {R.giorni.median():.0f}")

    # verdetto (§6): LEAD ha la precedenza; poi CLOSED; il resto e' NON DIMOSTRATO
    lead = (netto["low"] > 0 and gap["low"] > 0 and netto3 > 0 and all(v > 0 for v in per_ind.values()))
    if lead:
        v = "LEAD (gate finale: forward)"
    elif gap["high"] < soglia:
        v = f"CLOSED: escluso un divario di {soglia:.2f}%"
    else:
        v = f"NON DIMOSTRATO (MDE del divario {gap['mde']:.3f}%)"
    print(f"\nVERDETTO DA REGOLA: {v}")

    sr = netto["media"] / R.netto.std(ddof=1)
    psr = qm.probabilistic_sharpe_ratio(sr, 0.0, len(R), float(R.netto.skew()), float(R.netto.kurt()))
    print(f"\nDescrittivi (non decidono): Sharpe per trade {sr:.3f} (pavimento 1,65/sqrt(n) = {1.65 / np.sqrt(len(R)):.3f}), "
          f"PSR {psr:.3f} (1 trial: DSR = PSR)")
    for s in COSTI:
        x = R[R.sym == s]
        print(f"  {s}: n {len(x)}, netto medio {x.netto.mean():+.3f}%, win {100 * (x.netto > 0).mean():.0f}%")
    anni = R.groupby(R.entrata.dt.year)["netto"].sum()
    print(f"  anni con somma netta positiva: {int((anni > 0).sum())} su {len(anni)}")
    rt = runs_test((R.sort_values("entrata").netto > 0).to_numpy())
    print(f"  runs test vinto/perso: z {rt['z']:+.2f}, p {rt['p']:.3f} ({rt['lettura']})")
    print(f"  per giorno in mercato (somma/somma): reale {R.netto.sum() / R.giorni.sum():+.4f}%, "
          f"casuale a durata copiata {C.netto.sum() / C.giorni.sum():+.4f}%")

    from core.sizing import confronta_overlay, confronta_overlay_prop
    from core.prop_sim import PROP_LAB
    import yaml
    Rs = R.sort_values("uscita")
    tab, _ = confronta_overlay((Rs.netto / Rs.atr_pct).to_numpy(), n_perm=500, seed=SEME)
    print("\nDoppio binario, capitale proprio (unita' = ATR% al segnale):")
    print(tab[["binario", "e_per_unita", "e_lo", "e_hi", "valore_dipendenza", "max_dd_r", "lettura"]].round(3).to_string(index=False))
    regole = yaml.safe_load(open(PROP_LAB / "config" / "prop_rules.yaml", encoding="utf-8"))["ftmo_2step"]
    per = {}
    for _, x in Rs.iterrows():
        per.setdefault(x.uscita.normalize(), []).append((float(x.netto / x.atr_pct), float(x.mae_pct / x.atr_pct)))
    day_trades = [per.get(g, []) for g in pd.bdate_range(Rs.entrata.min(), Rs.uscita.max())]
    tp = confronta_overlay_prop(day_trades, regole, base_pct=1.0, n_paths=300, n_outer=60, seed=SEME)
    print("\nDoppio binario, prop FTMO 2 fasi: ILLUSTRATIVO, non se ne trae nulla (regola senza stop, ~14 trade l'anno):")
    print(tp[["binario", "pass_rate", "pass_lo", "pass_hi", "pass_zero"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
