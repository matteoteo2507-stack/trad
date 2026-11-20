"""Previsione della varianza giornaliera con EWMA (lambda = 0,94), e GJR-GARCH come opzione esplorativa.

Pacchetto `volatilita_ewma` v1 di `trad` (report: `report.md` nella stessa cartella). Autonomo: numpy e pandas;
`arch` solo per il GJR. Provato con Python 3.12, numpy 2.4.4, pandas 3.0.2, arch 8.0.0. Unita': rendimenti logaritmici in percento, varianze in %² (una varianza di 1,0 =
deviazione standard giornaliera dell'1%).

Convenzione dei tempi: la riga t contiene la previsione fatta **alla chiusura del giorno t**, con i soli dati fino a t,
per la varianza del giorno t+1 (`h1`) e per la somma delle varianze dei giorni t+1..t+5 (`h5`). Nessun dato
successivo a t entra nella riga t (lo verificano i test).

Uso da riga di comando:
    python volatilita_ewma.py prezzi.csv --data time --prezzo close [--gjr] [--uscita previsioni.csv]
Il file deve avere una riga per giorno di borsa, in ordine di data, con il prezzo di chiusura.
"""
from __future__ import annotations

import argparse
import warnings

import numpy as np
import pandas as pd

LAMBDA = 0.94          # RiskMetrics (1996), il valore usato in trad
RISCALDAMENTO = 100    # giorni prima della prima previsione EWMA: il peso dell'avvio scende sotto 0,94^100 = 0,2%
W = 1000               # finestra mobile del GJR e di c_t, in giorni di borsa (come in trad)
PASSO = 5              # il GJR si ristima ogni 5 giorni di borsa (come in trad)
SEME = 20261113        # seme delle partenze di riserva del primo blocco GJR (come in trad)
RIPARTENZE = 20


def rendimenti(prezzi: pd.Series) -> pd.Series:
    """Rendimenti logaritmici in percento: 100 * log(P_t / P_{t-1}). Il primo giorno non ha rendimento."""
    p = pd.Series(prezzi, dtype=float)
    if (p <= 0).any() or p.isna().any():
        raise ValueError("prezzi mancanti, nulli o negativi")
    return (100.0 * np.log(p / p.shift(1))).iloc[1:]


AVVIO = 75             # giorni usati per la varianza iniziale (come `arch`)


def _avvio(r: np.ndarray) -> float:
    """Varianza iniziale: media pesata dei primi 75 quadrati (pesi 0,94^k), come `arch`. Usa i giorni 0..74, quindi
    nessuna previsione pubblica esce prima del giorno 75 (vedi `ewma`)."""
    tau = min(AVVIO, len(r))
    w = 0.94 ** np.arange(tau)
    return float(np.sum(w / w.sum() * r[:tau] ** 2))


def ewma(r: pd.Series | np.ndarray, lam: float = LAMBDA, riscaldamento: int = RISCALDAMENTO) -> np.ndarray:
    """Varianza prevista per t+1 alla chiusura di t: s_{t+1} = lam * s_t + (1 - lam) * r_t².

    Restituisce un array lungo come `r`; NaN nei primi `riscaldamento` giorni, dove pesa ancora l'avvio. Il
    riscaldamento non puo' scendere sotto 75: l'avvio usa i giorni 0..74, e una previsione prima del giorno 75
    userebbe dati successivi alla sua origine."""
    if riscaldamento < AVVIO:
        raise ValueError("riscaldamento minimo %d giorni (l'avvio usa i giorni 0..%d)" % (AVVIO, AVVIO - 1))
    return _ewma_grezzo(r, lam, riscaldamento)


def _ewma_grezzo(r, lam: float, riscaldamento: int) -> np.ndarray:
    """La ricorsione senza il controllo del riscaldamento (solo per i test di uguaglianza con `arch`)."""
    r = np.asarray(r, float)
    if not np.all(np.isfinite(r)):
        raise ValueError("rendimenti mancanti o non finiti")
    s = np.empty(len(r))
    prec = _avvio(r)                       # varianza attesa per il giorno 0
    for t in range(len(r)):
        prec = lam * prec + (1.0 - lam) * r[t] ** 2
        s[t] = prec
    s[:riscaldamento] = np.nan
    return s


def previsioni_ewma(r: pd.Series, lam: float = LAMBDA, riscaldamento: int = RISCALDAMENTO) -> pd.DataFrame:
    """Colonne `h1` (varianza di domani) e `h5` (somma dei prossimi 5 giorni). L'EWMA prevede una varianza piatta:
    h5 = 5 * h1."""
    s = ewma(r, lam, riscaldamento)
    idx = r.index if isinstance(r, pd.Series) else None
    return pd.DataFrame({"h1": s, "h5": 5.0 * s}, index=idx)


def riscala(r: np.ndarray, v: np.ndarray, w: int = W) -> np.ndarray:
    """c_t = somma di v / somma di r² sui w giorni che finiscono in t (solo passato); NaN prima della finestra piena.

    Serve solo se si confronta la previsione con una varianza realizzata intraday `v` (somma dei quadrati dei
    rendimenti a 5 minuti, piu' la notte per gli indici): la previsione da rendimenti giornalieri va moltiplicata per
    c_t, altrimenti la scala non torna (report, "Come si usa")."""
    r, v = np.asarray(r, float), np.asarray(v, float)
    cv = np.cumsum(np.r_[0.0, v])
    cr = np.cumsum(np.r_[0.0, r ** 2])
    c = np.full(len(r), np.nan)
    t = np.arange(w - 1, len(r))
    if not (np.all(np.isfinite(r)) and np.all(np.isfinite(v)) and np.all(v >= 0)):
        raise ValueError("r o v mancanti, non finiti, o v negativa")
    den = cr[t + 1] - cr[t + 1 - w]
    c[t] = np.where(den > 0, (cv[t + 1] - cv[t + 1 - w]) / np.where(den > 0, den, 1.0), np.nan)
    return c


def bersaglio(v: np.ndarray, h: int) -> np.ndarray:
    """Il bersaglio della riga t: somma di v[t+1 .. t+h]. NaN dove la finestra esce dai dati o contiene un v mancante
    (solo le righe la cui finestra tocca quel giorno, nessuna somma parziale). La previsione della riga t si confronta
    con questo, mai con v[t]: senza lo spostamento il confronto premia chi copia oggi."""
    s = pd.Series(np.asarray(v, float)).rolling(h, min_periods=h).sum().shift(-h)
    return s.to_numpy()


def qlike(f: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Perdita QLIKE = log f + v / f (piu' bassa = previsione migliore). f e v nella stessa unita' e sullo stesso
    orizzonte: la previsione della riga t va con `bersaglio(v, h)[t]`, cioe' con i giorni t+1..t+h. Una previsione
    <= 0 o non finita, o un bersaglio negativo o non finito, e' un errore."""
    f, v = np.asarray(f, float), np.asarray(v, float)
    if not np.all(np.isfinite(f)) or np.any(f <= 0):
        raise ValueError("previsione nulla, negativa o non finita")
    if not np.all(np.isfinite(v)) or np.any(v < 0):
        raise ValueError("bersaglio negativo o non finito")
    return np.log(f) + v / f


# --------------------------------------------------------------------------------------------- GJR (esplorativo)
def _modello_gjr(y: np.ndarray):
    from arch import arch_model

    return arch_model(y, mean="Zero", vol="GARCH", p=1, o=1, q=1, dist="normal", rescale=False)


def _partenze_riserva(sv: np.ndarray, t0: int):
    rng = np.random.default_rng([SEME, t0, 1])
    for _ in range(RIPARTENZE):
        s = np.clip(sv * np.exp(0.2 * rng.standard_normal(len(sv))), 1e-6, None)
        pers = s[1] + s[2] / 2 + s[-1]
        if pers >= 0.999:
            s[1:] *= 0.99 / pers
        yield s


def _stima_gjr(y: np.ndarray, t0: int, primo: bool):
    """Parametri (omega, alpha, gamma, beta) o None. Una stima conta solo se converge e ha una verosimiglianza non
    peggiore della partenza; nel primo blocco si riprova da partenze perturbate (seme fisso)."""
    am = _modello_gjr(y)
    sv = am.volatility.starting_values(y)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ll0 = _modello_gjr(y).fix(sv).loglikelihood
        buona = lambda res: (res.convergence_flag == 0 and np.all(np.isfinite(res.params))
                             and res.loglikelihood >= ll0)
        res = am.fit(disp="off")
        if buona(res):
            return np.asarray(res.params)
        if not primo:
            return None
        ok = [x for x in (am.fit(disp="off", starting_values=s) for s in _partenze_riserva(sv, t0)) if buona(x)]
    return np.asarray(max(ok, key=lambda x: x.loglikelihood).params) if ok else None


def previsioni_gjr(r: pd.Series, w: int = W, passo: int = PASSO) -> pd.DataFrame:
    """GJR-GARCH(1,1) a media zero, gaussiano, finestra mobile di `w` giorni, ristima ogni `passo` giorni; fra una
    ristima e l'altra il filtro avanza coi parametri congelati. Una stima che non converge riusa i parametri del
    blocco precedente (colonna `ripiego` = True). Colonne `h1` e `h5` (somma delle previsioni a 1..5 passi).

    Nota: `arch` fissa i limiti numerici della varianza dalle statistiche del blocco filtrato, che arriva fino a 4
    giorni dopo l'origine. E' un canale teorico verso il futuro che non scatta nei test (le previsioni non cambiano
    se si cambiano i dati dopo l'origine) ed e' identico al codice di `trad`."""
    y_tutto = np.asarray(r, float)
    n = len(y_tutto)
    if n < w:
        raise ValueError("servono almeno %d giorni di rendimenti, ce ne sono %d" % (w, n))
    h1, h5 = np.full(n, np.nan), np.full(n, np.nan)
    ripiego = np.zeros(n, bool)
    par = None
    for t0 in range(w - 1, n, passo):
        t1 = min(t0 + passo - 1, n - 1)
        nuovi = _stima_gjr(y_tutto[t0 - w + 1:t0 + 1], t0, primo=par is None)
        if nuovi is None and par is None:
            raise RuntimeError("prima stima del GJR non convergente (t0 = %d)" % t0)
        if nuovi is None:
            ripiego[t0:t1 + 1] = True
        else:
            par = nuovi
        res = _modello_gjr(y_tutto[t0 - w + 1:t1 + 1]).fix(par)
        F = res.forecast(horizon=5, start=w - 1, reindex=False).variance.to_numpy()
        h1[t0:t1 + 1], h5[t0:t1 + 1] = F[:, 0], F.sum(axis=1)
    idx = r.index if isinstance(r, pd.Series) else None
    return pd.DataFrame({"h1": h1, "h5": h5, "ripiego": ripiego}, index=idx)


# ---------------------------------------------------------------------------------------------- riga di comando
def _principale(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv", help="file con una riga per giorno di borsa")
    ap.add_argument("--data", default="time", help="colonna della data (default: time)")
    ap.add_argument("--prezzo", default="close", help="colonna del prezzo di chiusura (default: close)")
    ap.add_argument("--gjr", action="store_true", help="aggiunge il GJR esplorativo (serve arch; lento)")
    ap.add_argument("--uscita", help="CSV di uscita con tutte le previsioni")
    a = ap.parse_args(argv)

    df = pd.read_csv(a.csv, parse_dates=[a.data]).set_index(a.data).sort_index()
    if df.index.duplicated().any():
        raise SystemExit("date duplicate nel file: una riga per giorno di borsa")
    r = rendimenti(df[a.prezzo])
    if len(r) <= RISCALDAMENTO:
        raise SystemExit("servono piu' di %d rendimenti giornalieri, ce ne sono %d" % (RISCALDAMENTO, len(r)))
    out = previsioni_ewma(r).add_prefix("ewma_")
    out.insert(0, "r", r)
    if a.gjr:
        out = out.join(previsioni_gjr(r).add_prefix("gjr_"))
    out["ewma_vol_giorno_pct"] = np.sqrt(out["ewma_h1"])
    out["ewma_vol_annua_pct"] = np.sqrt(252.0 * out["ewma_h1"])
    if a.uscita:
        out.to_csv(a.uscita)
    ultimo = out.iloc[-1]
    print("ultima chiusura: %s" % out.index[-1].date())
    print("EWMA  varianza domani %.4f %%^2  (vol. giornaliera %.3f%%, annua %.2f%%); prossimi 5 giorni %.4f %%^2"
          % (ultimo["ewma_h1"], ultimo["ewma_vol_giorno_pct"], ultimo["ewma_vol_annua_pct"], ultimo["ewma_h5"]))
    if a.gjr:
        print("GJR   varianza domani %.4f %%^2; prossimi 5 giorni %.4f %%^2 (esplorativo)"
              % (ultimo["gjr_h1"], ultimo["gjr_h5"]))


if __name__ == "__main__":
    _principale()
