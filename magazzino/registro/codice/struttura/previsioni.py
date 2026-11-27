"""Previsioni di correlazione, bersagli e differenziali di Stein di I3 (referto §4-§6, §10). 0 trial.

Tutto in memoria. Le serie dei differenziali non si stampano ne' si salvano (guardia "nessun canale"): chi chiama le
riduce alla grandezza ammessa (deviazione HAC per la potenza, δ per N2).

- EWMA (benchmark): Q_t = 0,94·Q_{t−1} + 0,06·Σ_t sulle sedute comuni pronte, avvio dalla media delle prime 50 Σ (non
  usate per altro); H = Q normalizzata.
- costante: media delle correlazioni (Σ normalizzate, che non dipendono dalla scala) sulle 500 sedute comuni valide
  che finiscono all'origine.
- persistenza: 0,9·R_t + 0,1·I, R_t la Σ normalizzata dell'origine.
- bersaglio: Σ_{t+1} (h = 1), media delle Σ_{t+1..t+5} (h = 5); un'origine entra solo se tutte le sedute del bersaglio
  sono pronte e tutte le previsioni esistono (nessuna finestra incompleta).
"""
from __future__ import annotations

import numpy as np

import misura as M

AVVIO_Q = 50
FINESTRA_COSTANTE = 500
ORIZZONTI = (1, 5)


def ewma_q(Sigma: np.ndarray, pronto: np.ndarray, avvio: int = AVVIO_Q, lam: float = M.LAMBDA) -> np.ndarray:
    """H_ewma[t] (previsione fatta alla fine di t), NaN finche' l'avvio non e' finito."""
    T, N, _ = Sigma.shape
    H = np.full((T, N, N), np.nan)
    idx = np.flatnonzero(pronto)
    if len(idx) <= avvio:
        return H
    Q = Sigma[idx[:avvio]].mean(axis=0)
    H[idx[avvio - 1]] = M.normalizza(Q)
    for t in range(idx[avvio - 1] + 1, T):
        if pronto[t]:
            Q = lam * Q + (1.0 - lam) * Sigma[t]
        H[t] = M.normalizza(Q)
    return H


def costante(R: np.ndarray, comune: np.ndarray, finestra: int = FINESTRA_COSTANTE) -> np.ndarray:
    T, N, _ = R.shape
    H = np.full((T, N, N), np.nan)
    pos = np.flatnonzero(comune)
    cs = np.concatenate([np.zeros((1, N, N)), np.cumsum(R[pos], axis=0)])
    for j in range(finestra - 1, len(pos)):
        fine = pos[j + 1] if j + 1 < len(pos) else T
        H[pos[j]:fine] = (cs[j + 1] - cs[j + 1 - finestra]) / finestra
    return H


def persistenza(R: np.ndarray, pronto: np.ndarray) -> np.ndarray:
    T, N, _ = R.shape
    H = np.full((T, N, N), np.nan)
    H[pronto] = 0.9 * R[pronto] + 0.1 * np.eye(N)
    return H


def bersagli(Sigma: np.ndarray, pronto: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray]:
    """(B, ok): B[t] = media di Σ_{t+1..t+h}; ok[t] se tutte le h sedute successive sono pronte."""
    T = len(Sigma)
    B = np.full_like(Sigma, np.nan)
    ok = np.zeros(T, bool)
    for t in range(T - h):
        if pronto[t + 1:t + 1 + h].all():
            ok[t] = True
            B[t] = Sigma[t + 1:t + 1 + h].mean(axis=0)
    return B, ok


def differenziale_stein(H1: np.ndarray, H2: np.ndarray, S: np.ndarray) -> np.ndarray:
    """L(H1, S) − L(H2, S) = tr((H1⁻¹ − H2⁻¹)S) + log det H1 − log det H2, per pila di matrici."""
    i1, i2 = np.linalg.inv(H1), np.linalg.inv(H2)
    tr = np.einsum("tij,tji->t", i1 - i2, S)
    return tr + np.linalg.slogdet(H1)[1] - np.linalg.slogdet(H2)[1]


def perdita_stein(H: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Perdita piena (solo per i test: richiede S invertibile)."""
    A = np.linalg.solve(H, S)
    return np.einsum("tii->t", A) - np.linalg.slogdet(A)[1] - S.shape[-1]


def tutte(m: dict) -> dict:
    """Previsioni dalla misura `m` di `misura.matrici`."""
    Sigma, pronto, comune = m["Sigma"], m["pronto"], m["comune"]
    R = m["correl_grezza"]
    return {"ewma": ewma_q(Sigma, pronto), "costante": costante(R, comune), "persistenza": persistenza(R, pronto)}


def differenziali(m: dict, prev: dict | None = None) -> dict:
    """{(alternativa, h): (origini, d)} con d = L(alternativa) − L(EWMA) sulle origini complete. Solo in memoria."""
    prev = tutte(m) if prev is None else prev
    out = {}
    for h in ORIZZONTI:
        B, ok = bersagli(m["Sigma"], m["pronto"], h)
        pronte = ok & m["pronto"]
        for nome in ("costante", "persistenza"):
            valide = pronte & np.isfinite(prev[nome]).all(axis=(1, 2)) & np.isfinite(prev["ewma"]).all(axis=(1, 2))
            orig = np.flatnonzero(valide)
            d = differenziale_stein(prev[nome][orig], prev["ewma"][orig], B[orig])
            out[(nome, h)] = (orig, d)
    return out


def ritardi_hac(h: int) -> int:
    return max(h - 1, 4)


def sd_hac(x: np.ndarray, ritardi: int) -> float:
    """Deviazione di Newey-West centrata (identica a `volatilita/potenza.py:sd_newey_west`, verificato nei test)."""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    s = np.sum(x * x) / n
    for k in range(1, ritardi + 1):
        s += 2 * (1 - k / (ritardi + 1)) * np.sum(x[k:] * x[:-k]) / n
    return float(np.sqrt(s))


def origini_da_maschere(valido_i: np.ndarray) -> dict:
    """Origini valide per orizzonte (EWMA contro costante) dalle sole maschere di validita' per strumento, senza
    rendimenti (riserva R7 della nona passata: un orizzonte decade sui conteggi veri prima della potenza).

    Ripercorre la stessa catena di `misura.matrici` e di `differenziali` con matrici fittizie (identita', varianze 1):
    quali sedute sono pronte, quando EWMA e costante esistono, quali origini hanno 1 + h sedute valide. Un test la
    confronta con la pipeline intera. Restituisce {h: indici delle origini}."""
    v = np.asarray(valido_i, bool)
    T, N = v.shape
    uno = np.ones(T)
    s2 = np.column_stack([M.ewma_rv(uno, v[:, i]) for i in range(N)])
    s = np.column_stack([M.fattore_scala(uno, s2[:, i], v[:, i]) for i in range(N)])
    scala = np.full((T, N), np.nan)
    scala[1:] = s2[:-1] * s[:-1]
    comune = v.all(axis=1)
    pronto = comune & np.isfinite(scala).all(axis=1)
    I = np.eye(N)
    Sigma = np.full((T, N, N), np.nan)
    Sigma[pronto] = I
    R = np.full((T, N, N), np.nan)
    R[comune] = I
    m = {"Sigma": Sigma, "pronto": pronto, "comune": comune, "correl_grezza": R}
    prev = {"ewma": ewma_q(Sigma, pronto), "costante": costante(R, comune)}
    out = {}
    for h in ORIZZONTI:
        _, ok = bersagli(Sigma, pronto, h)
        valide = ok & pronto & np.isfinite(prev["costante"]).all(axis=(1, 2)) & np.isfinite(prev["ewma"]).all(axis=(1, 2))
        out[h] = np.flatnonzero(valide)
    return out
