"""Controlli simulati della pipeline (pre-registrazione §7 passi 2 e 5). 0 trial.

Negativi (passo 2), prima della corsa di sviluppo:
- `neg_garch`: IGARCH lambda 0,94 e omega 0 (l'EWMA e' il previsore esatto), 9 serie da 1.500 giorni riscalate perche' la
  varianza vera media della valutazione sia 1 %², h = 1 e 5, 1.000 repliche, ristima ogni 20 giorni, SPA con 10.000
  ripetizioni; procedura grafica sulle 18 coppie con la quota del nodo (2,5%). Passa se rifiuta in <= 5% delle repliche.
- `neg_hmm`: GJR (0,02; 0,03; 0,10; 0,90) riscalato, le quattro varianti dell'HMM contro il GJR, 200 repliche, 3 serie,
  h = 1, 3 partenze, ristima ogni 60 giorni; procedura sulle 3 coppie a 1,25%. Passa se rifiuta in <= 2,5%.
- `dim_premio`: bootstrap circolare a blocchi fissi (21 e 63 giorni, 2.000 repliche ciascuno) del premio giornaliero di
  sviluppo riportato a media zero, messo sulle date di borsa XNYS dal 2024-11-11 al 2026-10-09 senza i loro valori; t a
  una coda sulle origini di fine mese, alfa 1,25%. Passa se rifiuta in <= 2,5% con entrambi i blocchi.

Bersaglio simulato = varianza vera × exp(sigma·eps − sigma²/2), sigma = 0,6 nei negativi. La pipeline e' quella vera
(`pipeline.previsioni`, c_t compreso). Ogni replica ha un seme derivato da (seme del controllo, replica) e si scrive
subito in `motore/data/cache/volatilita/<controllo>.jsonl`: una corsa interrotta riprende dalle repliche mancanti.

Uso: python magazzino/registro/codice/volatilita/controlli.py neg_garch|neg_hmm|dim_premio [--processi 8] [--repliche N]
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())
sys.path[:0] = [str(QUI), str(ROOT)]          # ROOT: `motore` anche nei processi figli (spawn su Windows)

import giorni as G  # noqa: E402
import pipeline as P  # noqa: E402

CACHE = G.ROOT / "motore/data/cache/volatilita"
ESITI = QUI / "esiti"
N_SERIE_GIORNI = 1500
VALUTAZIONE = 500

DISEGNI = {
    "neg_garch": dict(seme=20261119, repliche=1000, processo="igarch", serie=9, orizzonti=(1, 5), passo=20,
                      partenze=None, reps_spa=10_000, nodo="garch", alfa=0.025, soglia_esito=0.05, sigma=0.6),
    "neg_hmm": dict(seme=20261120, repliche=200, processo="gjr", serie=3, orizzonti=(1,), passo=60,
                    partenze=3, reps_spa=10_000, nodo="hmm", alfa=0.0125, soglia_esito=0.025, sigma=0.6),
}
PREMIO = dict(seme=20261121, repliche=2000, blocchi=(21, 63), alfa=0.0125, soglia_esito=0.025,
              holdout=("2024-11-11", "2026-10-09"))


# ------------------------------------------------------------------------------------------------ processi
def simula(processo: str, n: int, rng, **kw):
    """r (rendimenti, %) e s2 (varianza condizionale vera di r_t, %²)."""
    z = rng.standard_normal(n)
    r = np.empty(n)
    s2 = np.empty(n)
    if processo == "igarch":
        s = 1.0
        for t in range(n):
            s2[t] = s
            r[t] = np.sqrt(s) * z[t]
            s = 0.94 * s + 0.06 * r[t] ** 2
    elif processo == "gjr":
        om, al, ga, be = kw.get("parametri", (0.02, 0.03, 0.10, 0.90))
        s = om / (1 - al - ga / 2 - be)
        for t in range(n):
            s2[t] = s
            r[t] = np.sqrt(s) * z[t]
            s = om + (al + ga * (r[t] < 0)) * r[t] ** 2 + be * s
    elif processo == "regimi":
        var = np.asarray(kw.get("varianze", (0.5, 2.0)))
        resta = np.asarray(kw.get("resta", (0.98, 0.95)))
        u = rng.random(n)
        stato = 0
        for t in range(n):
            s2[t] = var[stato]
            r[t] = np.sqrt(var[stato]) * z[t]
            if u[t] > resta[stato]:
                stato = 1 - stato
    else:
        raise ValueError(processo)
    return r, s2


def riscala_valutazione(r, s2, n_val=VALUTAZIONE):
    m = s2[-n_val:].mean()
    return r / np.sqrt(m), s2 / m


def bersaglio_simulato(s2, sigma, rng):
    return s2 * np.exp(sigma * rng.standard_normal(len(s2)) - sigma ** 2 / 2)


# ------------------------------------------------------------------------------------------------ replica
def replica(nome: str, k: int, disegno: dict, sigma_serie=None) -> dict:
    """Una replica: serie simulate, pipeline, SPA studentizzato per coppia, procedura grafica sul nodo."""
    from motore.core.verifiche import procedura_grafica_nodi, pvalue_spa, spa_studentizzato

    ss = np.random.SeedSequence([disegno["seme"], k])
    figli = ss.spawn(disegno["serie"])
    bench = P.BENCHMARK[disegno["nodo"]]
    varianti = list(P.VARIANTI[disegno["nodo"]])
    pv, iv, perdite_medie = {}, {}, {}
    for i, figlio in enumerate(figli):
        rng = np.random.default_rng(figlio)
        r, s2 = simula(disegno["processo"], N_SERIE_GIORNI, rng, **disegno.get("kw", {}))
        if disegno["processo"] in ("igarch", "gjr"):
            r, s2 = riscala_valutazione(r, s2)
        sigma = disegno["sigma"] if sigma_serie is None else sigma_serie[i]
        v = bersaglio_simulato(s2, sigma, rng)
        out = P.previsioni(r, v, modelli=[bench] + varianti, passo=disegno["passo"],
                           partenze_hmm=disegno["partenze"] or 20)["previsioni"]
        b = P.bersagli(v, np.zeros(len(v), bool))
        t = np.arange(len(v) - VALUTAZIONE - 1, len(v) - 1 - 5)          # origini comuni a h = 1 e 5
        for j, h in enumerate(P.ORIZZONTI):
            if h not in disegno["orizzonti"]:
                continue
            lb = P.qlike(out[bench][t, j], b[t, j])
            lm = np.column_stack([P.qlike(out[m][t, j], b[t, j]) for m in varianti])
            seme_spa = int(np.random.SeedSequence([disegno["seme"], k, i, h]).generate_state(1)[0])
            spa = spa_studentizzato(lb, lm, reps=disegno["reps_spa"], seed=seme_spa)
            p = pvalue_spa(spa, disegno["reps_spa"])
            chiave = "s%d_h%d" % (i, h)
            pv[chiave], iv[chiave] = p["p"], (p["low"], p["high"])
            perdite_medie[chiave] = [float(lb.mean() - lm[:, q].mean()) for q in range(lm.shape[1])]
    nodo = disegno["nodo"]
    proc = procedura_grafica_nodi({nodo: pv}, {nodo: disegno["alfa"]}, intervalli={nodo: iv})
    soglia_coppia = disegno["alfa"] / 18                                   # prima soglia vera della coppia
    return {"replica": k, "p": pv, "intervalli": iv, "rifiutate": proc["rifiutate"][nodo],
            "rifiuta_nodo": bool(proc["rifiutate"][nodo]),
            "rifiuti_coppia_soglia_vera": {c: bool(iv[c][1] <= soglia_coppia) for c in pv},
            "guadagno_qlike_medio": perdite_medie}


def _compito(args):
    nome, k, disegno, sigma_serie = args
    t0 = time.time()
    out = replica(nome, k, disegno, sigma_serie)
    out["secondi"] = round(time.time() - t0, 1)
    return out


def esegui(nome: str, disegno: dict, processi: int, repliche: int | None = None, sigma_serie=None,
           commit: str | None = None) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    diario = CACHE / ("%s.jsonl" % nome)
    fatte = {}
    if diario.exists():
        for riga in diario.read_text(encoding="utf-8").splitlines():
            x = json.loads(riga)
            fatte[x["replica"]] = x
    n = disegno["repliche"] if repliche is None else repliche
    mancanti = [k for k in range(n) if k not in fatte]
    print("%s: %d repliche, %d gia' fatte, %d processi" % (nome, n, n - len(mancanti), processi), flush=True)
    with Pool(processi) as pool, open(diario, "a", encoding="utf-8", newline="\n") as f:
        for j, out in enumerate(pool.imap_unordered(_compito, [(nome, k, disegno, sigma_serie) for k in mancanti]), 1):
            f.write(json.dumps(out) + "\n")
            f.flush()
            fatte[out["replica"]] = out
            if j % 10 == 0:
                tot = sum(x["rifiuta_nodo"] for x in fatte.values())
                print("%d/%d  rifiuti del nodo finora %d su %d  (%.0fs)" % (j, len(mancanti), tot, len(fatte),
                                                                           out["secondi"]), flush=True)
    righe = [fatte[k] for k in range(n)]
    freq_nodo = float(np.mean([x["rifiuta_nodo"] for x in righe]))
    freq_coppia = float(np.mean([np.mean(list(x["rifiuti_coppia_soglia_vera"].values())) for x in righe]))
    return {"controllo": nome, "commit": commit, "repliche": n, "frequenza_rifiuto_nodo": freq_nodo,
            "frequenza_media_rifiuto_coppia_soglia_vera": freq_coppia,
            "disegno": {k: v for k, v in disegno.items() if k != "kw"}}


# ------------------------------------------------------------------------------------------------ premio
def premio_giornaliero(apri_holdout: bool = False):
    """Premio p_t = VIX_t²·30/365 − somma di v dell'SPX500 nei giorni di borsa in (t, t + 30 giorni] (§3), in %².
    Origini con tutta la finestra nello sviluppo e nessun giorno escluso."""
    if apri_holdout:
        raise PermissionError("holdout sigillato")
    d = G.carica("SPX500")
    vix = G.carica_vix()
    date = d.index
    cs = np.cumsum(np.r_[0.0, d["v"].to_numpy()])
    ce = np.cumsum(np.r_[0, d["escluso"].to_numpy().astype(int)])
    fine = np.searchsorted(date, date + np.timedelta64(30, "D"), side="right")     # primo indice oltre t+30
    righe = []
    for i, t in enumerate(date):
        if t + np.timedelta64(30, "D") >= G.HOLDOUT_INIZIO:
            continue                                                                 # finestra oltre lo sviluppo
        if t not in vix.index or ce[fine[i]] - ce[i + 1] > 0:
            continue
        rv = cs[fine[i]] - cs[i + 1]
        righe.append((t, vix.loc[t] ** 2 * 30 / 365 - rv))
    import pandas as pd
    return pd.Series([x[1] for x in righe], index=pd.DatetimeIndex([x[0] for x in righe]), name="premio")


def dimensione_premio(commit=None) -> dict:
    import exchange_calendars as xc
    import pandas as pd
    from scipy import stats

    p = premio_giornaliero().to_numpy()
    p = p - p.mean()
    a, b = PREMIO["holdout"]
    date = xc.get_calendar("XNYS").sessions_in_range(a, b)
    L = len(date)
    tutte = xc.get_calendar("XNYS").sessions_in_range(a, pd.Timestamp(b) + pd.Timedelta(days=62))
    fm = pd.Series(tutte, index=tutte).groupby([tutte.year, tutte.month]).max()
    fm = fm[(fm >= pd.Timestamp(a)) & (fm <= pd.Timestamp(b))]          # ultimo giorno di borsa del mese
    mesi_completi = date.get_indexer(pd.DatetimeIndex(fm.to_numpy()))
    n = len(mesi_completi)
    crit = stats.t.ppf(1 - PREMIO["alfa"], n - 1)
    esiti = {}
    for bl in PREMIO["blocchi"]:
        rng = np.random.default_rng([PREMIO["seme"], bl])
        rifiuti = 0
        for _ in range(PREMIO["repliche"]):
            partenze = rng.integers(0, len(p), size=-(-L // bl))
            idx = (partenze[:, None] + np.arange(bl)[None, :]).reshape(-1)[:L] % len(p)
            x = p[idx][mesi_completi]
            tstat = x.mean() / (x.std(ddof=1) / np.sqrt(n))
            rifiuti += tstat > crit
        esiti["blocco_%d" % bl] = rifiuti / PREMIO["repliche"]
    passa = all(f <= PREMIO["soglia_esito"] for f in esiti.values())
    return {"controllo": "dim_premio", "commit": commit, "esito": "PASSA" if passa else "FALLISCE",
            "frequenza_rifiuto": esiti, "origini_mensili": n, "giorni_holdout": L, "osservazioni_sviluppo": len(p),
            "disegno": PREMIO}


def _scrivi(nome, out):
    ESITI.mkdir(exist_ok=True)
    tmp = ESITI / ("%s.json.tmp" % nome)
    tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, ESITI / ("%s.json" % nome))


def main():
    import guardie

    nome = sys.argv[1]
    controllo = guardie.verifica()
    print("guardie OK, commit", controllo["commit"], flush=True)
    processi = int(sys.argv[sys.argv.index("--processi") + 1]) if "--processi" in sys.argv else os.cpu_count()
    repliche = int(sys.argv[sys.argv.index("--repliche") + 1]) if "--repliche" in sys.argv else None
    if nome == "dim_premio":
        out = dimensione_premio(controllo["commit"])
    else:
        d = DISEGNI[nome]
        out = esegui(nome, d, processi, repliche, commit=controllo["commit"])
        out["esito"] = "PASSA" if out["frequenza_rifiuto_nodo"] <= d["soglia_esito"] else "FALLISCE"
    if repliche is None:
        _scrivi(nome, out)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
