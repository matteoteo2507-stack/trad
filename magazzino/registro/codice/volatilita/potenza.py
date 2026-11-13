"""Passi 4-6 del §7: MDE per coppia, rapporto effetto/MDE dei positivi simulati, controllo positivo sui dati veri. 0 trial.

- `mde_coppie(sviluppo)`: per (nodo, strumento, h) MDE = mde(sd_HAC, n_eff, alpha = quota/18, code = 1), sd = deviazione
  di Newey-West (max(h − 1, 4) ritardi) del differenziale di QLIKE benchmark − migliore variante nello sviluppo,
  n_eff = origini dell'holdout dal calendario (nessun dato dell'holdout).
- `sigma_rumore(sviluppo)`: sd di log(v_t / (c_t·f_t^GJR)) per strumento (h = 1), il rumore dei positivi simulati.
- `rapporto_effetto_mde(...)`: per i positivi simulati, effetto atteso (differenza di QLIKE con i parametri del
  processo, da una simulazione lunga) diviso l'MDE simulato (stessa formula, sd dalla stessa simulazione, n = 496);
  si scrive **prima** di far girare i positivi.
- `iniettata(...)`: controllo sui dati veri (§7.6).
"""
from __future__ import annotations

import numpy as np

import modelli as M
import pipeline as P

QUOTE = {"garch": 0.025, "hmm": 0.0125}
N_COPPIE = 18


def sd_newey_west(x: np.ndarray, ritardi: int) -> float:
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    s = np.sum(x * x) / n
    for k in range(1, ritardi + 1):
        s += 2 * (1 - k / (ritardi + 1)) * np.sum(x[k:] * x[:-k]) / n
    return float(np.sqrt(s))


def giorni_holdout(nome: str) -> int:
    """Origini dell'holdout dal solo calendario: giorni di borsa dal 2024-11-11 al 2026-11-10, meno i 5 finali."""
    import exchange_calendars as xc
    import pandas as pd

    import giorni as G

    if nome in G.CALENDARI:
        n = len(xc.get_calendar(G.CALENDARI[nome]).sessions_in_range("2024-11-11", "2026-11-10"))
    else:
        n = len(pd.bdate_range("2024-11-11", "2026-11-10"))
    return n - 5


def mde_coppie(perdite: dict) -> dict:
    """`perdite[(nodo, strumento, h)] = (perdita del benchmark, matrice delle varianti)` sulle origini di sviluppo valide."""
    from motore.core.verifiche import mde

    out = {}
    for (nodo, nome, h), (lb, lm) in perdite.items():
        d = lb[:, None] - lm                                     # positivo = la variante perde meno
        migliore = int(np.argmax(d.mean(axis=0)))
        sd = sd_newey_west(d[:, migliore], max(h - 1, 4))
        n = giorni_holdout(nome)
        out["%s|%s|h%d" % (nodo, nome, h)] = {
            "variante_migliore": P.VARIANTI[nodo][migliore], "sd_hac": sd, "n_eff": n,
            "alfa_prima_soglia": QUOTE[nodo] / N_COPPIE,
            "mde": mde(sd, n, alpha=QUOTE[nodo] / N_COPPIE, code=1)}
    return out


def sigma_rumore(v: np.ndarray, f_gjr_scalato: np.ndarray, validi: np.ndarray) -> float:
    """sd di log(v_t / (c_t·f_t^GJR)) sui giorni t con previsione valida (h = 1, f all'origine t − 1)."""
    x = np.log(v[validi] / f_gjr_scalato[validi])
    return float(np.std(x, ddof=1))


def effetto_simulato(nodo: str, sigma: float, n_lungo: int = 400_000, seme: int = 20261124) -> dict:
    """Effetto atteso e sd del differenziale di QLIKE per i positivi simulati, con i parametri del processo.

    GARCH: processo GJR (0,02; 0,03; 0,10; 0,90); EWMA contro la varianza vera del GJR (oracolo: limite superiore
    dell'effetto, perche' nel controllo il GJR e' stimato). HMM: processo a 2 regimi (0,5 e 2,0; resta 0,98 e 0,95);
    GJR con i parametri pseudo-veri (stimato sulla meta' iniziale della serie lunga) contro il filtro vero a 2 regimi."""
    import controlli as C
    from arch import arch_model

    rng = np.random.default_rng([seme, int(sigma * 1e6), 1 if nodo == "garch" else 2])
    if nodo == "garch":
        r, s2 = C.simula("gjr", n_lungo, rng)
        f_buono = s2
        f_bench = np.empty(n_lungo)
        s = s2[:250].mean()
        for t in range(n_lungo):
            f_bench[t] = s
            s = M.LAMBDA * s + (1 - M.LAMBDA) * r[t] ** 2
    else:
        r, s2 = C.simula("regimi", n_lungo, rng)
        meta = n_lungo // 2
        am = arch_model(r[:meta], mean="Zero", vol="GARCH", p=1, o=1, q=1, rescale=False)
        par = am.fit(disp="off").params.to_numpy()
        f_bench = arch_model(r, mean="Zero", vol="GARCH", p=1, o=1, q=1, rescale=False).fix(par).conditional_volatility ** 2
        var = np.array([0.5, 2.0])
        P_ = np.array([[0.98, 0.05], [0.02, 0.95]])                # P[i, j] = P(s_{t+1} = i | s_t = j)
        p = np.array([0.5, 0.5])
        f_buono = np.empty(n_lungo)
        dens = lambda x: np.exp(-0.5 * x ** 2 / var) / np.sqrt(var)
        for t in range(n_lungo):
            q = P_ @ p                                              # previsione per t con i dati fino a t − 1
            f_buono[t] = var @ q
            p = q * dens(r[t])
            p = p / p.sum()
        r, s2, f_buono, f_bench = r[meta:], s2[meta:], f_buono[meta:], f_bench[meta:]
    v = C.bersaglio_simulato(s2, sigma, rng)
    d = P.qlike(f_bench, v) - P.qlike(f_buono, v)
    return {"effetto": float(d.mean()), "sd_hac": sd_newey_west(d, 4)}


def rapporto_effetto_mde(nodo: str, sigmi: list, n_valutazione: int = 496) -> dict:
    from motore.core.verifiche import mde

    righe = []
    for s in sigmi:
        e = effetto_simulato(nodo, s)
        m = mde(e["sd_hac"], n_valutazione, alpha=QUOTE[nodo] / N_COPPIE, code=1)
        righe.append({"sigma": s, "effetto": e["effetto"], "sd_hac": e["sd_hac"], "mde_simulato": m,
                      "rapporto": e["effetto"] / m})
    return {"nodo": nodo, "per_serie": righe, "rapporto_minimo": min(x["rapporto"] for x in righe)}


def tara_w(f_base: np.ndarray, v: np.ndarray, guadagno: float) -> float:
    """w in [0, 1] tale che QLIKE(f_base) − QLIKE(f_base^(1−w)·v^w) medio = guadagno (bisezione)."""
    def g(w):
        f = f_base ** (1 - w) * v ** w
        return float(np.mean(P.qlike(f_base, v) - P.qlike(f, v)))
    lo, hi = 0.0, 1.0
    if g(hi) < guadagno:
        return float("nan")
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if g(mid) < guadagno else (lo, mid)
    return (lo + hi) / 2
