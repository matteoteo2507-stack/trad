"""Misura realizzata di I3 (referto del passo 2, §3-§4): dalla griglia dei prezzi alle matrici Σ. 0 trial.

Funzioni pure su array, usate dal simulatore di N2 e (dal commit (1)) dal loader dei dati veri. Nessuna stampa: chi
chiama decide cosa esce (guardia "nessun canale", requisiti del commit (1) punto 4).

Convenzioni (referto §3, §4):
- `P[t, k, i]`: log-prezzo della seduta t, orario k della griglia della misura, strumento i; NaN = prezzo mancante.
  Dal 23/11 la misura e' a **30 minuti** (14 prezzi: l'open delle 9:30 e le 13 chiusure delle mezz'ore) con
  **Bartlett a 2 ritardi** (DECISIONS 2026-11-23 (4)); `passo` sottocampiona una griglia piu' fine se serve.
- rendimento = differenza di log-prezzi adiacenti; un prezzo mancante rende mancanti i due rendimenti adiacenti;
  **mancante = zero** nei prodotti.
- strumento-giorno valido: almeno il 90% dei rendimenti attesi osservati e al massimo il 25% di nulli **fra gli
  osservati**; giorno comune valido: tutti gli strumenti validi (esclusione per unione).
- Bartlett con `ritardi` ritardi (2 di base): pesi 1 − l/(ritardi + 1), su tutta la matrice;
  semidefinita positiva per costruzione (Newey-West), anche con gli zeri.
- ingresso fisso: σ̂² = EWMA 0,94 della RV sulle sedute valide **dello strumento**, avvio dalla media delle prime 50 RV
  valide (non usate per altro); in una seduta non valida si tiene il valore di prima.
- fattore di scala s_{i,t}: media semplice di D_{i,τ} / σ̂²_{i,τ−1} sulle 500 sedute valide dello strumento che
  finiscono a t (D = diagonale di Bartlett dei rendimenti grezzi).
- Σ_t = Bartlett dei z_{k,i} = r_{k,i} / (σ̂_{i,t−1}·√s_{i,t−1}), nei giorni comuni validi con tutti gli ingredienti.
"""
from __future__ import annotations

import numpy as np

LAMBDA = 0.94
AVVIO_EWMA = 50
FINESTRA_S = 500
SOGLIA_OSSERVATI = 0.90
SOGLIA_NULLI = 0.25
RITARDI = 2
N_PREZZI = 14


def rendimenti(P: np.ndarray, passo: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """(r, osservato): r[t, j, i] con NaN dove manca; `osservato` booleano."""
    Q = P[:, ::passo, :]
    r = np.diff(Q, axis=1)
    return r, np.isfinite(r)


def validi_strumento(r: np.ndarray, oss: np.ndarray) -> np.ndarray:
    """valido[t, i]: >= 90% di rendimenti osservati e <= 25% di nulli fra gli osservati."""
    attesi = r.shape[1]
    n_oss = oss.sum(axis=1)
    nulli = np.where(oss, r == 0.0, False).sum(axis=1)
    quota_nulli = np.divide(nulli, n_oss, out=np.ones_like(nulli, dtype=float), where=n_oss > 0)
    return (n_oss >= SOGLIA_OSSERVATI * attesi) & (quota_nulli <= SOGLIA_NULLI)


def bartlett(x: np.ndarray, ritardi: int = 1) -> np.ndarray:
    """x[..., k, i] con zeri al posto dei mancanti -> matrice [..., i, j] = Γ0 + Σ_l w_l (Γl + Γl')."""
    C = np.einsum("...ki,...kj->...ij", x, x)
    for l in range(1, ritardi + 1):
        w = 1.0 - l / (ritardi + 1.0)
        G = np.einsum("...ki,...kj->...ij", x[..., l:, :], x[..., :-l, :])
        C = C + w * (G + np.swapaxes(G, -1, -2))
    return C


def ewma_rv(rv: np.ndarray, valido: np.ndarray, avvio: int = AVVIO_EWMA, lam: float = LAMBDA) -> np.ndarray:
    """σ̂²[t] dopo la seduta t (NaN fino alla fine dell'avvio). La ricorsione e' quella del pacchetto
    `uscita/volatilita_ewma/v1` (prec = lam·prec + (1 − lam)·x), sulle sole sedute valide; le prime `avvio` sedute
    valide danno solo la varianza iniziale (media semplice)."""
    out = np.full(len(rv), np.nan)
    idx = np.flatnonzero(valido)
    if len(idx) <= avvio:
        return out
    prec = float(np.mean(rv[idx[:avvio]]))
    out[idx[avvio - 1]] = prec
    for t in range(idx[avvio - 1] + 1, len(rv)):
        if valido[t]:
            prec = lam * prec + (1.0 - lam) * rv[t]
        out[t] = prec
    return out


def fattore_scala(D: np.ndarray, s2: np.ndarray, valido: np.ndarray, finestra: int = FINESTRA_S) -> np.ndarray:
    """s[t] = media di D[τ] / s2[τ−1] sulle ultime `finestra` sedute valide τ <= t con s2[τ−1] definito; NaN prima."""
    n = len(D)
    prec = np.full(n, np.nan)
    prec[1:] = s2[:-1]
    usabile = valido & np.isfinite(prec)
    rapporti = np.where(usabile, D / np.where(usabile, prec, 1.0), 0.0)
    cr = np.concatenate([[0.0], np.cumsum(rapporti)])
    cu = np.concatenate([[0], np.cumsum(usabile.astype(int))])
    out = np.full(n, np.nan)
    pos = np.flatnonzero(usabile)
    for j in range(finestra - 1, len(pos)):
        t0, t1 = pos[j - finestra + 1], pos[j]
        fine = pos[j + 1] if j + 1 < len(pos) else n
        out[t1:fine] = (cr[t1 + 1] - cr[t0]) / finestra
    return out


def matrici(P: np.ndarray, passo: int = 1, ritardi: int = RITARDI) -> dict:
    """Σ per seduta (NaN dove non definita) e maschere. Restituisce solo oggetti in memoria."""
    r, oss = rendimenti(P, passo)
    valido_i = validi_strumento(r, oss)
    r0 = np.where(oss, r, 0.0)
    T, K, N = r0.shape
    rv = np.einsum("tki,tki->ti", r0, r0)
    D = np.einsum("tii->ti", bartlett(r0, ritardi))
    s2 = np.column_stack([ewma_rv(rv[:, i], valido_i[:, i]) for i in range(N)])
    s = np.column_stack([fattore_scala(D[:, i], s2[:, i], valido_i[:, i]) for i in range(N)])
    scala = np.full((T, N), np.nan)
    scala[1:] = np.sqrt(s2[:-1] * s[:-1])
    comune = valido_i.all(axis=1)
    pronto = comune & np.isfinite(scala).all(axis=1)
    z = r0 / np.where(np.isfinite(scala), scala, 1.0)[:, None, :]
    Sigma = np.full((T, N, N), np.nan)
    Sigma[pronto] = bartlett(z[pronto], ritardi)
    grezza = np.full((T, N, N), np.nan)
    grezza[comune] = bartlett(r0[comune], ritardi)
    return {"Sigma": Sigma, "pronto": pronto, "comune": comune, "correl_grezza": normalizza(grezza),
            "valido_i": valido_i}


def normalizza(C: np.ndarray) -> np.ndarray:
    """Matrice (o pila) a diagonale 1; NaN restano NaN."""
    d = np.sqrt(np.einsum("...ii->...i", C))
    return C / (d[..., :, None] * d[..., None, :])
