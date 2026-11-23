"""Controllo N2 del G9 di I3 (referto §9): processo simulato, generatore dei difetti, gemelli, δ e guardia. 0 trial.

Nessun dato di prezzo: il processo e' inventato (correlazione vera che torna verso una matrice a blocchi dalle
correlazioni D1 di A1) e i difetti vengono da probabilita' passate da chi chiama (per la corsa vera: i soli conteggi
del controllo di struttura; per le prove prima del commit: difetti dichiarati nel referto).

Uscite ammesse (requisiti del commit (1), punto 6): quantili di δ, numero di repliche che rifiutano nella guardia,
matrici non valide. Le serie dei differenziali restano in memoria dentro `replica`.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

import misura as M
import previsioni as V

UNIVERSO = ("SPX500", "NAS100", "DOW", "RUSSELL", "DAX", "XAUUSD", "XAGUSD", "WTI", "NATGAS",
            "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "BUND", "USTBOND", "COPPER", "BTCUSD")   # ordine del §7
BLOCCHI = {("SPX500", "NAS100", "DOW", "RUSSELL", "DAX"): 0.791,     # A1 §4, insieme "index" (heldout_pool.py)
           ("WTI", "NATGAS"): 0.443,                                   # A1 §4, energia
           ("EURUSD", "USDJPY", "GBPUSD", "AUDUSD"): 0.050}             # A1 §4, cross FX
FONDO = 0.112                                                           # A1 §8, tutte le coppie dei futures
A, B = 0.06, 0.93
N_ORARI = 27          # griglia del processo vero: 26 quarti d'ora
N_REND = 26
PASSO_MISURA = 2      # la misura prende un prezzo su due: 14 prezzi, 13 rendimenti a 30 minuti (23/11)
N_PREZZI = 14
N_H = 247              # sedute piene XNYS 2024-11-11 -> 2025-11-10 (referto §9)
TAU = 0.5
SEME = 20261123
SEME_VERIFICA = 20261125
SEME_POSITIVO = 20261126
REPLICHE = 500
SOGLIA_GUARDIA = 35    # quantile al 97,5% di Bin(500; 0,05)


def soglia_guardia(repliche: int) -> int:
    """Quantile al 97,5% di Bin(repliche; 0,05): 35 con 500 repliche. Corretto il 23/11: prima la soglia era 35 per
    qualunque numero di repliche, e le prove con 60 repliche davano PASSA con il 20% di rifiuti."""
    return int(stats.binom.ppf(0.975, repliche, 0.05))
EIG_MIN = 1e-10
MIN_ORIGINI = 50
POSITIVO_STRUMENTI = ("EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "XAUUSD", "XAGUSD", "BUND")   # prove del 23/11
POSITIVO_QUOTA = 0.05     # controllo positivo dal 23/11: 5% fisso su tutti i 17, L = 3 mezz'ore
POSITIVO_L = 3.0


def r_bar(universo=UNIVERSO) -> np.ndarray:
    n = len(universo)
    R = np.full((n, n), FONDO)
    for nomi, rho in BLOCCHI.items():
        idx = [universo.index(x) for x in nomi if x in universo]
        R[np.ix_(idx, idx)] = rho
    np.fill_diagonal(R, 1.0)
    if np.linalg.eigvalsh(R)[0] <= 0:
        raise ValueError("R̄ non definita positiva")
    return R


def rendimenti_veri(T: int, rng: np.random.Generator, Rb: np.ndarray, a: float = A, b: float = B) -> dict:
    """Log-prezzi veri X[t, k, i] (X[t, 0] = 0) e minimo autovalore di Q_t per seduta."""
    N = len(Rb)
    Q = Rb.copy()
    X = np.zeros((T, N_ORARI, N))
    eig_min = np.empty(T)
    for t in range(T):
        e = np.linalg.eigvalsh(Q)
        eig_min[t] = e[0]
        L = np.linalg.cholesky(Q)
        z = rng.standard_normal((N_REND, N)) @ L.T / np.sqrt(N_REND)
        X[t, 1:] = np.cumsum(z, axis=0)
        C = z.T @ z
        S = M.normalizza(C)
        Q = (1.0 - a - b) * Rb + a * S + b * Q
    return {"X": X, "eig_min": eig_min}


def durata_catena(L_contata: np.ndarray, n: int = N_PREZZI - 1) -> np.ndarray:
    """Durata media della catena che riproduce la durata **contata** nei dati (serie di nulli troncate a inizio e fine
    seduta): con catena stazionaria su n rendimenti, L_contata = n / (1 + (n − 1)/L), quindi L = (n − 1)/(n/L_contata − 1).
    Si ferma se L_contata >= n (conteggi incoerenti)."""
    Lc = np.asarray(L_contata, float)
    if np.any(Lc >= n) or np.any(Lc < 1.0):
        raise ValueError("durata contata fuori da [1, %d)" % n)
    return (n - 1) / (n / Lc - 1.0)


def prob_fermo(p0: np.ndarray, L: np.ndarray) -> np.ndarray:
    """p_u = p0 / (L·(1 − p0)): probabilita' di passare da aggiornato a fermo (referto §9)."""
    p0, L = np.asarray(p0, float), np.asarray(L, float)
    pu = np.where(p0 > 0, p0 / (np.maximum(L, 1.0) * (1.0 - p0)), 0.0)
    if np.any(pu > 1.0) or np.any(p0 >= 1.0):
        raise ValueError("conteggi incoerenti: p_u > 1")
    return pu


def applica_difetti(X: np.ndarray, rng: np.random.Generator, difetti: dict) -> np.ndarray:
    """Prezzi osservati. `difetti`: p_giorno[t, i], p0[t, i], L[t, i], p_ora[t, k, i] (k = 0..26).
    Ordine: seduta mancante, prezzi fermi (catena che riparte ogni seduta dalla sua distribuzione stazionaria: lo stato
    dell'open si estrae con probabilita' p0, ma il prezzo dell'open e' sempre quello vero), mancanti per ora. Ogni
    seduta estrae sempre gli stessi tre blocchi di numeri, cosi' il flusso non dipende dai valori."""
    T, K, N = X.shape
    pu = prob_fermo(difetti["p0"], difetti["L"])
    resta = np.where(difetti["p0"] > 0, 1.0 - 1.0 / np.maximum(difetti["L"], 1.0), 0.0)
    Y = np.empty_like(X)
    for t in range(T):
        u_giorno = rng.random(N)
        u_fermo = rng.random((K, N))
        u_ora = rng.random((K, N))
        y = X[t].copy()
        fermo = u_fermo[0] < difetti["p0"][t]          # stato dell'open dalla distribuzione stazionaria
        for k in range(1, K):
            fermo = np.where(fermo, u_fermo[k] < resta[t], u_fermo[k] < pu[t])
            y[k] = np.where(fermo, y[k - 1], X[t, k])
        y[u_ora < difetti["p_ora"][t]] = np.nan
        y[:, u_giorno < difetti["p_giorno"][t]] = np.nan
        Y[t] = y
    return Y


def nessun_difetto(T: int, N: int) -> dict:
    return {"p_giorno": np.zeros((T, N)), "p0": np.zeros((T, N)), "L": np.ones((T, N)),
            "p_ora": np.zeros((T, N_PREZZI, N))}


def difetto_positivo(T: int, universo=UNIVERSO, quota: float = POSITIVO_QUOTA, L: float = POSITIVO_L) -> dict:
    """Controllo positivo del §9 (dal 23/11): quota fissa di prezzi fermi su tutti gli strumenti, durata media L sulla
    griglia della misura, nessun altro difetto."""
    d = nessun_difetto(T, len(universo))
    d["p0"][:] = quota
    d["L"][:] = L
    return d


def matrici_non_valide(m: dict, prev: dict, eig_q: np.ndarray) -> int:
    n = int(np.sum(eig_q <= EIG_MIN))
    for H in prev.values():
        ok = np.isfinite(H).all(axis=(1, 2))
        n += int(np.sum(np.linalg.eigvalsh(H[ok])[:, 0] <= EIG_MIN)) if ok.any() else 0
    S = m["Sigma"][m["pronto"]]
    n += int(np.sum(~np.isfinite(S).all(axis=(1, 2))))
    return n


def misura_e_differenziali(P: np.ndarray, ritardi: int = M.RITARDI, colonne=None):
    """`P` sulla griglia della misura (14 prezzi)."""
    if colonne is not None:
        P = P[:, :, colonne]
    m = M.matrici(P, ritardi=ritardi)
    prev = V.tutte(m)
    return m, prev, V.differenziali(m, prev)


def delta(dd: tuple, ds: tuple, h: int, n_h: int = N_H) -> float:
    """δ sull'intersezione delle origini valide dei due gemelli (riserva R6 dell'ottava passata), in unita' di errore
    standard di un anno: (media d_difetti − media d_sincrono) / (sd_HAC(d_sincrono) / √n_h)."""
    (od, d_d), (os_, d_s) = dd, ds
    comuni, i_d, i_s = np.intersect1d(od, os_, return_indices=True)
    if len(comuni) < MIN_ORIGINI:
        return float("nan")          # campione insufficiente: la replica conta come GUASTO (riassumi)
    x_d, x_s = d_d[i_d], d_s[i_s]
    es = V.sd_hac(x_s, V.ritardi_hac(h)) / np.sqrt(n_h)
    return float((x_d.mean() - x_s.mean()) / es)


def dm_rifiuta(d: np.ndarray, h: int, alfa: float = 0.05) -> bool:
    """Diebold-Mariano a una coda "l'alternativa batte l'EWMA" (media di d < 0), HLN, HAC max(h − 1, 4)."""
    n = len(d)
    sd = V.sd_hac(d, V.ritardi_hac(h))
    t = d.mean() / (sd / np.sqrt(n))
    t *= np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return bool(t < -stats.t.ppf(1 - alfa, n - 1))


def replica(args) -> dict:
    """Una replica: gemello sincrono e gemello con difetti, stessi rendimenti veri. Solo grandezze ammesse in uscita."""
    figlio, T, difetti, a, b, ritardi, colonne, universo = args
    s_veri, s_dif = figlio.spawn(2)
    Rb = r_bar(universo)
    vero = rendimenti_veri(T, np.random.default_rng(s_veri), Rb, a, b)
    X = vero["X"][:, ::PASSO_MISURA]                     # griglia della misura: i difetti si applicano qui
    Y = applica_difetti(X, np.random.default_rng(s_dif), difetti)
    m_s, p_s, d_s = misura_e_differenziali(X, ritardi, colonne)
    m_d, p_d, d_d = misura_e_differenziali(Y, ritardi, colonne)
    out = {"non_valide": matrici_non_valide(m_s, p_s, vero["eig_min"]) + matrici_non_valide(m_d, p_d, vero["eig_min"])}
    for (nome, h) in d_s:
        out[("delta", nome, h)] = delta(d_d[(nome, h)], d_s[(nome, h)], h)
        if nome == "costante":
            out[("guardia", h)] = dm_rifiuta(d_s[(nome, h)][1], h)
    return out


def esegui(T: int, difetti: dict, seme: int, repliche: int = REPLICHE, a: float = A, b: float = B,
           ritardi: int = M.RITARDI, colonne=None, universo=UNIVERSO, processi: int = 1) -> dict:
    figli = np.random.SeedSequence(seme).spawn(repliche)
    compiti = [(f, T, difetti, a, b, ritardi, colonne, universo) for f in figli]
    if processi > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(processi) as ex:
            righe = list(ex.map(replica, compiti, chunksize=4))
    else:
        righe = [replica(c) for c in compiti]
    return riassumi(righe)


QUANTILI = (0.05, 0.25, 0.5, 0.75, 0.95)


def riassumi(righe: list) -> dict:
    """Solo le chiavi ammesse: quantili di δ, rifiuti della guardia, matrici non valide, esito."""
    out = {"repliche": len(righe), "non_valide": int(sum(r["non_valide"] for r in righe))}
    insufficienti = 0
    for nome in ("costante", "persistenza"):
        for h in V.ORIZZONTI:
            x = np.array([r[("delta", nome, h)] for r in righe])
            insufficienti = max(insufficienti, int(np.sum(~np.isfinite(x))))
            x = x[np.isfinite(x)]
            out["delta_%s_h%d" % (nome, h)] = ([round(float(q), 3) for q in np.quantile(x, QUANTILI)]
                                              if len(x) else None)
    out["campione_insufficiente"] = insufficienti
    for h in V.ORIZZONTI:
        out["guardia_rifiuti_h%d" % h] = int(sum(r[("guardia", h)] for r in righe))
    mediane = [out["delta_costante_h%d" % h][2] if out["delta_costante_h%d" % h] else np.nan for h in V.ORIZZONTI]
    if out["non_valide"] > 0 or insufficienti > 0 or any(out["guardia_rifiuti_h%d" % h] > soglia_guardia(len(righe)) for h in V.ORIZZONTI):
        out["esito"] = "GUASTO"
    elif min(mediane) < -TAU:
        out["esito"] = "RIFIUTA per misura"
    else:
        out["esito"] = "PASSA"
    return out
