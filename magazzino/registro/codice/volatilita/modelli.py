"""Previsioni di varianza della famiglia `volatilita` (pre-registrazione §4-§5). 0 trial.

Schema comune: finestra mobile di `W` = 1.000 giorni, ristima ogni `PASSO` = 5 giorni di borsa. Un **blocco** comincia
all'origine t0 (stima su r[t0-W+1 .. t0]) e copre le origini t0 .. t0+PASSO-1: fra una ristima e l'altra il filtro va
avanti con i parametri congelati. Ogni funzione restituisce `F`, matrice (n, H) con la previsione a 1..H passi
all'origine t (riga t), sulla scala dei rendimenti (%²) e **senza** il riscalamento c_t (lo applica `riscala`), NaN
dove non c'e' previsione. Media zero, gaussiana (QMLE).

Solo filtraggio: `arch` stima con `last_obs` = giorno dopo l'origine del blocco e prevede dall'origine; l'HMM usa solo
`filtered_marginal_probabilities`. Il test d'invarianza al futuro (`test_invarianza.py`) lo verifica.

Scelte d'implementazione dichiarate prima della corsa di sviluppo (pre-registrazione §11, 13/11):
- EGARCH a piu' passi: `arch` 8.0.0 non ha la previsione analitica oltre il primo passo; si usa l'attesa esatta sotto la
  normale (`egarch_multi`, verificata contro la simulazione di arch);
- una stima che non converge usa i parametri del blocco precedente (S5, esteso a GARCH, GJR, EGARCH), e si conta;
- HMM: 20 partenze = 20 stime complete da punti casuali attorno al punto di partenza di statsmodels (spazio non vincolato,
  N(0, 1)), seme dipendente solo da (k, t0), si tiene la verosimiglianza migliore fra quelle che convergono;
- HAR a h = 5 diretto (bersaglio la somma dei 5 giorni); una previsione HAR <= 0 diventa la media della finestra, e si conta.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import norm

W = 1000
PASSO = 5
H = 5
LAMBDA = 0.94
SEME_HMM = 20261113
C = np.sqrt(2.0 / np.pi)


def blocchi(n: int, w: int = W, passo: int = PASSO, origini=None):
    """(t0, t1) con t1 incluso: origini t0..t1 coi parametri stimati su r[t0-w+1..t0]. Con `origini` solo i blocchi che
    le contengono (per il test d'invarianza): la griglia dei blocchi non cambia."""
    scelti = None if origini is None else {w - 1 + ((t - (w - 1)) // passo) * passo for t in origini if t >= w - 1}
    for t0 in range(w - 1, n, passo):
        if scelti is None or t0 in scelti:
            yield t0, min(t0 + passo - 1, n - 1)


class _Parametri:
    """Parametri per blocco, con il ripiego sul blocco precedente se una stima non converge (S5). Il blocco precedente
    si stima a richiesta: con `origini` il risultato e' lo stesso della corsa completa."""

    def __init__(self, stima, w, passo):
        self.stima, self.w, self.passo = stima, w, passo
        self.memo, self.non_conv = {}, 0

    def __call__(self, t0):
        if t0 not in self.memo:
            par = self.stima(t0)
            if par is None:
                self.non_conv += 1
                if t0 - self.passo < self.w - 1:
                    raise RuntimeError("prima stima non convergente in t0=%d" % t0)
                par = self(t0 - self.passo)
            self.memo[t0] = par
        return self.memo[t0]


def riscala(r: np.ndarray, v: np.ndarray, w: int = W) -> np.ndarray:
    """c_t = somma di v / somma di r² sui w giorni che finiscono in t (solo passato); NaN prima della finestra piena."""
    cv = np.cumsum(np.r_[0.0, v])
    cr = np.cumsum(np.r_[0.0, r ** 2])
    c = np.full(len(r), np.nan)
    t = np.arange(w - 1, len(r))
    c[t] = (cv[t + 1] - cv[t + 1 - w]) / (cr[t + 1] - cr[t + 1 - w])
    return c


def egarch_multi(s1: np.ndarray, omega: float, alpha: float, gamma: float, beta: float, h: int = H) -> np.ndarray:
    """E[sigma²_{t+k}] per k = 1..h di un EGARCH(1,1,1) di arch con innovazioni normali, dato sigma²_{t+1} = s1.

    ln s²_{t+k} = omega·sum_j beta^j + beta^(k-1)·ln s²_{t+1} + sum_j beta^j (alpha(|z|-c) + gamma z), j = 0..k-2;
    E[exp(a|z| + b z)] = exp((a+b)²/2)·Phi(a+b) + exp((a-b)²/2)·Phi(a-b), calcolata in logaritmi (con |a ± b| grande
    exp(x²/2)·Phi(x) e' finito, ma i due fattori separati danno inf·0 = NaN)."""
    s1 = np.asarray(s1, float)
    out = np.empty((len(s1), h))
    out[:, 0] = s1
    for k in range(2, h + 1):
        bj = beta ** np.arange(k - 1)
        a, b = bj * alpha, bj * gamma
        log_e = np.logaddexp((a + b) ** 2 / 2 + norm.logcdf(a + b), (a - b) ** 2 / 2 + norm.logcdf(a - b))
        log_cost = omega * bj.sum() - C * a.sum() + log_e.sum()
        out[:, k - 1] = np.exp(log_cost + beta ** (k - 1) * np.log(s1))
    return out


# ---------------------------------------------------------------------------------------------------------- arch
def _modello_arch(y, tipo):
    from arch import arch_model
    from arch.univariate import EWMAVariance, ZeroMean

    if tipo == "ewma":
        return ZeroMean(y, volatility=EWMAVariance(LAMBDA), rescale=False)
    vol, o = {"garch": ("GARCH", 0), "gjr": ("GARCH", 1), "egarch": ("EGARCH", 1)}[tipo]
    return arch_model(y, mean="Zero", vol=vol, p=1, o=o, q=1, dist="normal", rescale=False)


RIPARTENZE_PRIMO_BLOCCO = 20


def _partenze_riserva(sv: np.ndarray, tipo: str, t0: int, n: int):
    """Partenze perturbate attorno a quella di `arch` (sv·exp(0,2·N(0,1))), seme fisso legato solo a t0 (nessun dato):
    positive e con persistenza < 0,999 per GARCH e GJR, beta <= 0,995 per l'EGARCH."""
    rng = np.random.default_rng([SEME_HMM, t0, ("garch", "gjr", "egarch").index(tipo)])
    for _ in range(n):
        s = sv * np.exp(0.2 * rng.standard_normal(len(sv)))
        if tipo == "egarch":
            s[-1] = min(s[-1], 0.995)
        else:
            s = np.clip(s, 1e-6, None)
            pers = s[1] + (s[2] / 2 if tipo == "gjr" else 0) + s[-1]
            if pers >= 0.999:
                s[1:] *= 0.99 / pers
        yield s


def prevedi_arch(r: np.ndarray, tipo: str, w: int = W, passo: int = PASSO, h: int = H, origini=None) -> dict:
    """tipo in {ewma, garch, gjr, egarch}."""
    n = len(r)
    F = np.full((n, h), np.nan)
    ripartenze = [0]

    def stima(t0):
        if tipo == "ewma":
            return np.zeros(0)
        y = r[t0 - w + 1:t0 + 1]
        am = _modello_arch(y, tipo)
        sv = am.volatility.starting_values(y)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # falsa convergenza: l'ottimizzatore dichiara successo in un punto peggiore della sua partenza (EGARCH,
            # neg_garch replica 17: alfa -15, gamma -65, verosimiglianza 6.390 sotto la partenza). Conta come non
            # convergenza (parametri del blocco precedente).
            ll_partenza = _modello_arch(y, tipo).fix(sv).loglikelihood
            buona = lambda res: (res.convergence_flag == 0 and np.all(np.isfinite(res.params))
                                 and res.loglikelihood >= ll_partenza)
            res = am.fit(disp="off")
            if buona(res):
                return np.asarray(res.params)
            if t0 - passo >= w - 1:
                return None                               # ripiego sul blocco precedente (S5)
            # primo blocco, senza un precedente (neg_garch repliche 66 e 76): ripartenze di riserva, si tiene la
            # migliore che converge e batte la partenza di arch; se nessuna, None (errore visibile in _Parametri)
            ripartenze[0] += 1
            ok = [x for x in (am.fit(disp="off", starting_values=s)
                              for s in _partenze_riserva(sv, tipo, t0, RIPARTENZE_PRIMO_BLOCCO)) if buona(x)]
        return np.asarray(max(ok, key=lambda x: x.loglikelihood).params) if ok else None

    par_di = _Parametri(stima, w, passo)
    parametri = []
    for t0, t1 in blocchi(n, w, passo, origini):
        par = par_di(t0)
        parametri.append((t0, par))
        res = _modello_arch(r[t0 - w + 1:t1 + 1], tipo).fix(par)
        if tipo == "egarch":
            s1 = res.forecast(horizon=1, start=w - 1, reindex=False).variance.to_numpy()[:, 0]
            om, al, ga, be = np.asarray(res.params)
            F[t0:t1 + 1] = egarch_multi(s1, om, al, ga, be, h)
        else:
            F[t0:t1 + 1] = res.forecast(horizon=h, start=w - 1, reindex=False).variance.to_numpy()
    return {"F": F, "non_convergenze": par_di.non_conv, "ripartenze_primo_blocco": ripartenze[0],
            "parametri": parametri}


# ----------------------------------------------------------------------------------------------------------- HMM
def _stima_hmm(y, k, partenze, rng):
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    m = MarkovRegression(y, k_regimes=k, trend="n", switching_variance=True)
    base = m.untransform_params(m.start_params)
    migliore = None
    for _ in range(partenze):
        start = m.transform_params(base + rng.standard_normal(len(base)))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                res = m.fit(start_params=start, disp=False)
            except Exception:
                continue
        if not res.mle_retvals.get("converged", False) or not np.isfinite(res.llf):
            continue
        if migliore is None or res.llf > migliore.llf:
            migliore = res
    return None if migliore is None else np.asarray(migliore.params)


def _previsione_hmm(y_ext, params, k, da, h):
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    m = MarkovRegression(y_ext, k_regimes=k, trend="n", switching_variance=True)
    f = m.filter(params)
    p = np.asarray(f.filtered_marginal_probabilities)[da:]          # (origini, k): P(s_t | dati fino a t)
    P = np.asarray(f.regime_transition)[:, :, 0]                      # P[i, j] = P(s_{t+1} = i | s_t = j)
    s2 = params[-k:]
    out = np.empty((len(p), h))
    q = p.T
    for j in range(h):
        q = P @ q
        out[:, j] = s2 @ q
    return out


def prevedi_hmm(r: np.ndarray, k: int, w: int = W, passo: int = PASSO, h: int = H, partenze: int = 20,
                seme: int = SEME_HMM, origini=None) -> dict:
    n = len(r)
    F = np.full((n, h), np.nan)
    par_di = _Parametri(lambda t0: _stima_hmm(r[t0 - w + 1:t0 + 1], k, partenze,
                                              np.random.default_rng([seme, k, t0])), w, passo)
    parametri = []
    for t0, t1 in blocchi(n, w, passo, origini):
        par = par_di(t0)
        parametri.append((t0, par))
        F[t0:t1 + 1] = _previsione_hmm(r[t0 - w + 1:t1 + 1], par, k, w - 1, h)
    return {"F": F, "non_convergenze": par_di.non_conv, "parametri": parametri}


# ------------------------------------------------------------------------------------------------ riferimenti
def prevedi_har(v: np.ndarray, w: int = W, passo: int = PASSO, h: int = H, origini=None) -> dict:
    """HAR-RV di Corsi sulla scala di v. Restituisce F1 (h = 1) e F5 (somma diretta di h giorni) in `F[:, 0]` e
    `F[:, h-1]`; le colonne intermedie restano NaN."""
    n = len(v)
    cs = np.cumsum(np.r_[0.0, v])
    idx = np.arange(n)
    m5 = np.full(n, np.nan)
    m22 = np.full(n, np.nan)
    m5[4:] = (cs[idx[4:] + 1] - cs[idx[4:] - 4]) / 5
    m22[21:] = (cs[idx[21:] + 1] - cs[idx[21:] - 21]) / 22
    X = np.column_stack([np.ones(n), v, m5, m22])
    y1 = np.r_[v[1:], np.nan]
    yh = np.full(n, np.nan)
    yh[:n - h] = cs[idx[:n - h] + 1 + h] - cs[idx[:n - h] + 1]
    F = np.full((n, h), np.nan)
    corretti = 0
    for t0, t1 in blocchi(n, w, passo, origini):
        lo = t0 - w + 1 + 21
        for col, y, ultimo in ((0, y1, t0 - 1), (h - 1, yh, t0 - h)):
            s = np.arange(lo, ultimo + 1)
            beta = np.linalg.lstsq(X[s], y[s], rcond=None)[0]
            f = X[t0:t1 + 1] @ beta
            scala = 1 if col == 0 else h
            media = np.array([v[t - w + 1:t + 1].mean() * scala for t in range(t0, t1 + 1)])
            cattivi = ~(f > 0)
            corretti += int(cattivi.sum())
            F[t0:t1 + 1, col] = np.where(cattivi, media, f)
    return {"F": F, "corrette": corretti}


def prevedi_persistenza(v: np.ndarray, w: int = W, h: int = H) -> np.ndarray:
    F = np.full((len(v), h), np.nan)
    F[w - 1:] = v[w - 1:, None]
    return F


def prevedi_media(v: np.ndarray, w: int = W, h: int = H) -> np.ndarray:
    cs = np.cumsum(np.r_[0.0, v])
    t = np.arange(w - 1, len(v))
    F = np.full((len(v), h), np.nan)
    F[t] = ((cs[t + 1] - cs[t + 1 - w]) / w)[:, None]
    return F


def somma_orizzonte(F: np.ndarray, h: int) -> np.ndarray:
    """Previsione della varianza dei prossimi h giorni = somma dei passi 1..h."""
    return F[:, :h].sum(axis=1)
