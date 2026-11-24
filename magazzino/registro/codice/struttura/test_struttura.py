"""Test di I3 su soli dati sintetici (misura, previsioni, N2). 0 trial.

python -m pytest magazzino/registro/codice/struttura/test_struttura.py -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))

import misura as M  # noqa: E402
import previsioni as V  # noqa: E402
import simula_n2 as S  # noqa: E402

ROOT = next(p for p in QUI.parents if (p / "pyproject.toml").exists())


def _griglia(T=3, N=3, seme=0):
    rng = np.random.default_rng(seme)
    r = rng.standard_normal((T, 26, N)) * 0.01
    P = np.zeros((T, 27, N))
    P[:, 1:] = np.cumsum(r, axis=1)
    return P, r


# ---------------------------------------------------------------- misura

def test_rendimenti_e_mancanti():
    P, r = _griglia()
    P[0, 5, 1] = np.nan
    rr, oss = M.rendimenti(P)
    assert rr.shape == (3, 26, 3)
    assert np.allclose(rr[1], r[1])
    assert not oss[0, 4, 1] and not oss[0, 5, 1] and oss[0, 6, 1]      # un prezzo mancante -> due rendimenti


def test_trenta_minuti():
    P, r = _griglia()
    rr, _ = M.rendimenti(P, passo=2)
    assert rr.shape[1] == 13
    assert np.allclose(rr[0, 0], r[0, 0] + r[0, 1])


def test_validita_nulli_sui_soli_osservati():
    P, _ = _griglia(T=1, N=1)
    # 3 prezzi mancanti (non adiacenti) -> 6 rendimenti mancanti: 20 osservati su 26 < 90% -> non valido
    P2 = P.copy()
    P2[0, [3, 10, 20], 0] = np.nan
    r, oss = M.rendimenti(P2)
    assert not M.validi_strumento(r, oss)[0, 0]
    # 1 prezzo mancante -> 24 osservati (>= 23,4); 6 nulli su 24 = 25% -> valido; 7 nulli -> no
    P3 = P.copy()
    P3[0, 25, 0] = np.nan
    for k in (2, 4, 6, 8, 10, 12):
        P3[0, k, 0] = P3[0, k - 1, 0]
    r, oss = M.rendimenti(P3)
    assert oss.sum() == 24 and M.validi_strumento(r, oss)[0, 0]
    P3[0, 14, 0] = P3[0, 13, 0]
    r, oss = M.rendimenti(P3)
    assert not M.validi_strumento(r, oss)[0, 0]


def test_bartlett_semidefinita_con_zeri():
    rng = np.random.default_rng(1)
    for _ in range(50):
        x = rng.standard_normal((26, 17))
        x[rng.random((26, 17)) < 0.2] = 0.0
        for q in (1, 2):
            assert np.linalg.eigvalsh(M.bartlett(x, q))[0] > -1e-10


def test_bartlett_uno_e_due_ritardi_a_mano():
    rng = np.random.default_rng(2)
    x = rng.standard_normal((26, 3))
    G0 = x.T @ x
    G1 = x[1:].T @ x[:-1]
    G2 = x[2:].T @ x[:-2]
    assert np.allclose(M.bartlett(x, 1), G0 + 0.5 * (G1 + G1.T))
    assert np.allclose(M.bartlett(x, 2), G0 + 2 / 3 * (G1 + G1.T) + 1 / 3 * (G2 + G2.T))
    assert M.RITARDI == 2 and M.PASSO_MISURA == 2 and M.N_PREZZI == 27


def test_ewma_ricorsione_del_pacchetto():
    """La ricorsione e' quella del pacchetto volatilita_ewma v1 (stessa operazione, bit per bit a parita' di avvio)."""
    sys.path.insert(0, str(ROOT / "uscita/volatilita_ewma/v1"))
    import volatilita_ewma as P  # noqa: E402

    rng = np.random.default_rng(3)
    r = rng.standard_normal(400)
    pacchetto = P._ewma_grezzo(r, 0.94, 0)
    x = r ** 2
    prec = P._avvio(r)
    nostro = []
    for t in range(len(r)):
        prec = M.LAMBDA * prec + (1.0 - M.LAMBDA) * x[t]
        nostro.append(prec)
    assert np.array_equal(np.array(nostro), pacchetto)
    # ewma_rv applica la stessa riga sulle sedute valide, avvio dalla media delle prime 50
    v = np.ones(400, bool)
    s = M.ewma_rv(x, v)
    atteso = np.mean(x[:50])
    for t in range(50, 400):
        atteso = 0.94 * atteso + (1.0 - 0.94) * x[t]
    assert s[-1] == atteso
    assert np.isnan(s[48]) and np.isfinite(s[49])


def test_ewma_tiene_il_valore_nelle_sedute_non_valide():
    x = np.arange(1.0, 101.0)
    v = np.ones(100, bool)
    v[70] = False
    s = M.ewma_rv(x, v)
    assert s[70] == s[69]


def test_fattore_scala_su_processo_esatto():
    """Volatilita' costante: la diagonale media dei z vale circa 1 dopo il riscaldamento."""
    rng = np.random.default_rng(4)
    X = S.rendimenti_veri(900, rng, S.r_bar())["X"]
    m = M.matrici(X)
    diag = np.einsum("tii->ti", m["Sigma"][m["pronto"]])
    assert abs(diag.mean() - 1.0) < 0.05


def test_riscaldamento():
    rng = np.random.default_rng(5)
    X = S.rendimenti_veri(700, rng, S.r_bar())["X"]
    m = M.matrici(X)
    assert np.flatnonzero(m["pronto"])[0] == 550             # 50 di avvio + 500 del fattore di scala
    prev = V.tutte(m)
    assert np.flatnonzero(np.isfinite(prev["ewma"]).all(axis=(1, 2)))[0] == 599
    assert np.flatnonzero(np.isfinite(prev["costante"]).all(axis=(1, 2)))[0] == 499


def test_esclusione_per_unione():
    P, _ = _griglia(T=4, N=3)
    P[2, 1:10, 1] = np.nan
    m = M.matrici(P)
    assert m["valido_i"][2].tolist() == [True, False, True]
    assert not m["comune"][2] and m["comune"][[0, 1, 3]].all()


# ---------------------------------------------------------------- previsioni

def test_stein_differenziale_uguale_alla_differenza_delle_perdite():
    rng = np.random.default_rng(6)
    N = 5
    A = rng.standard_normal((40, N, N))
    S_ = A @ np.swapaxes(A, 1, 2) / N + np.eye(N)
    R = M.normalizza(S_)
    H1, H2 = 0.7 * R + 0.3 * np.eye(N), np.broadcast_to(np.eye(N), R.shape).copy()
    d = V.differenziale_stein(H1, H2, S_)
    assert np.allclose(d, V.perdita_stein(H1, S_) - V.perdita_stein(H2, S_))


def test_previsioni_definite_a_diagonale_uno():
    rng = np.random.default_rng(7)
    X = S.rendimenti_veri(1200, rng, S.r_bar())["X"]
    m = M.matrici(X)
    for nome, H in V.tutte(m).items():
        ok = np.isfinite(H).all(axis=(1, 2))
        assert ok.any()
        assert np.allclose(np.einsum("tii->ti", H[ok]), 1.0), nome
        assert np.linalg.eigvalsh(H[ok])[:, 0].min() > 0, nome


def test_orizzonte_cinque_nessuna_finestra_incompleta():
    T, N = 20, 2
    Sig = np.broadcast_to(np.eye(N), (T, N, N)).copy()
    pronto = np.ones(T, bool)
    pronto[10] = False
    _, ok = V.bersagli(Sig, pronto, 5)
    assert not ok[5:10].any() and ok[4] and ok[10]
    assert not ok[T - 5:].any()


def test_sd_hac_identica_alla_volatilita():
    sys.path.insert(0, str(QUI.parent / "volatilita"))
    import importlib.util

    spec = importlib.util.spec_from_file_location("pot", QUI.parent / "volatilita" / "potenza.py")
    testo = (QUI.parent / "volatilita" / "potenza.py").read_text(encoding="utf-8")
    inizio = testo.index("def sd_newey_west")
    fine = testo.index("\ndef ", inizio + 1)
    ns = {"np": np}
    exec(testo[inizio:fine], ns)          # solo la funzione: il modulo importa arch, non richiesto qui
    x = np.random.default_rng(8).standard_normal(300)
    for L in (4, 5):
        assert V.sd_hac(x, L) == ns["sd_newey_west"](x, L)


# ---------------------------------------------------------------- N2

def test_r_bar_blocchi():
    R = S.r_bar()
    u = S.UNIVERSO
    assert R[u.index("SPX500"), u.index("DAX")] == 0.791
    assert R[u.index("WTI"), u.index("NATGAS")] == 0.443
    assert R[u.index("EURUSD"), u.index("AUDUSD")] == 0.050
    assert R[u.index("XAUUSD"), u.index("XAGUSD")] == 0.112
    assert R[u.index("SPX500"), u.index("BTCUSD")] == 0.112
    assert abs(np.linalg.eigvalsh(R)[0] - 0.209) < 0.001
    senza_dax = tuple(x for x in u if x != "DAX")
    assert S.r_bar(senza_dax).shape == (16, 16)


def test_processo_diagonale_e_limite():
    rng = np.random.default_rng(9)
    Rb = S.r_bar()
    out = S.rendimenti_veri(1500, rng, Rb)
    assert out["eig_min"].min() >= 0.143 * np.linalg.eigvalsh(Rb)[0] * (1 - 1e-9)


def test_gemelli_senza_difetti_coincidono_e_delta_zero():
    T = 700
    X = S.rendimenti_veri(T, np.random.default_rng(10), S.r_bar())["X"]
    Y = S.applica_difetti(X, np.random.default_rng(11), S.nessun_difetto(T, 17))
    assert np.array_equal(X, Y)
    _, _, ds = S.misura_e_differenziali(X)
    _, _, dd = S.misura_e_differenziali(Y)
    for k in ds:
        assert S.delta(dd[k], ds[k], k[1]) == 0.0


def test_catena_dei_fermi_riproduce_quota_e_durata():
    T, N = 4000, 1
    d = S.nessun_difetto(T, N)
    d["p0"][:] = 0.10
    d["L"][:] = S.durata_catena(3.0)                             # durata della catena che da' 3 come durata contata
    X = np.cumsum(np.random.default_rng(12).standard_normal((T, 27, N)), axis=1)
    X[:, 0] = 0.0
    Y = S.applica_difetti(X, np.random.default_rng(13), d)
    r, _ = M.rendimenti(Y)
    nulli = (r == 0.0)[:, :, 0]
    assert abs(nulli.mean() - 0.10) < 0.01
    corse = []
    for riga in nulli:
        n = 0
        for v in riga:
            if v:
                n += 1
            elif n:
                corse.append(n)
                n = 0
        if n:
            corse.append(n)
    assert 2.85 < np.mean(corse) < 3.15
    assert not np.any(Y[:, 0] != X[:, 0])                        # l'open non e' mai fermo


def test_catena_riparte_ogni_seduta_e_pu_incoerente():
    with pytest.raises(ValueError):
        S.prob_fermo(np.array([0.9]), np.array([1.0]))


def test_mancanti_per_ora_e_seduta():
    T, N = 3000, 2
    d = S.nessun_difetto(T, N)
    d["p_giorno"][:, 0] = 0.05
    d["p_ora"][:, 26, 1] = 1.0
    X = np.zeros((T, 27, N))
    Y = S.applica_difetti(X, np.random.default_rng(14), d)
    manca_giorno = np.isnan(Y[:, :, 0]).all(axis=1)
    assert abs(manca_giorno.mean() - 0.05) < 0.015
    assert np.isnan(Y[:, 26, 1]).all() and not np.isnan(Y[:, :26, 1]).any()


def test_stesso_seme_stesso_risultato():
    T = 720
    a = S.esegui(T, S.difetto_positivo(T), 123, repliche=2)
    b = S.esegui(T, S.difetto_positivo(T), 123, repliche=2)
    assert a == b


def test_uscita_solo_chiavi_ammesse():
    T = 720
    out = S.esegui(T, S.nessun_difetto(T, 17), 7, repliche=2)
    ammesse = {"repliche", "non_valide", "campione_insufficiente_h1", "campione_insufficiente_h5", "orizzonti_decaduti",
               "esito", "guardia_rifiuti_h1", "guardia_rifiuti_h5"}
    ammesse |= {"delta_%s_h%d" % (n, h) for n in ("costante", "persistenza") for h in (1, 5)}
    assert set(out) == ammesse


def test_soglia_guardia_dipende_dalle_repliche():
    assert S.soglia_guardia(500) == S.SOGLIA_GUARDIA == 35
    assert S.soglia_guardia(60) == 7
    assert S.riassumi(_righe(60, lambda i: 0.0, lambda i: 0.0, guardia1=12))["esito"] == "GUASTO"


def test_controllo_positivo_dichiarato():
    d = S.difetto_positivo(100)
    assert (d["p0"] == 0.05).all() and (d["L"] == 3.0).all()
    assert not d["p_giorno"].any() and not d["p_ora"].any() and d["p_ora"].shape[1] == 27


def test_validita_sui_quindici_minuti_misura_sui_trenta():
    """Un prezzo mancante a un quarto d'ora dispari toglie 2 rendimenti su 26 (resta valido, 24 >= 23,4) e nessun
    rendimento a 30 minuti; uno a un orario pari toglie 2 rendimenti a 30 minuti ma la seduta resta valida."""
    P, _ = _griglia(T=2, N=2)
    P[0, 5, 0] = np.nan
    P[1, 6, 0] = np.nan
    m = M.matrici(P, passo=2)
    assert m["valido_i"].all()
    r30, oss30 = M.rendimenti(P, 2)
    assert oss30[0].all()
    assert not oss30[1, 2, 0] and not oss30[1, 3, 0] and oss30[1, 4, 0]


def _righe(n, d1, d5, guardia1=0):
    return [{"non_valide": 0, ("guardia", 1): i < guardia1, ("guardia", 5): False,
             ("delta", "costante", 1): d1(i), ("delta", "costante", 5): d5(i),
             ("delta", "persistenza", 1): 0.0, ("delta", "persistenza", 5): 0.0} for i in range(n)]


def test_orizzonte_senza_campione_decade():
    nan = float("nan")
    out = S.riassumi(_righe(10, lambda i: -2.0, lambda i: nan))          # h5 vuoto ovunque: decade, decide h1
    assert out["orizzonti_decaduti"] == [5] and out["esito"] == "RIFIUTA per misura"
    out = S.riassumi(_righe(10, lambda i: 0.1, lambda i: nan if i < 6 else -3.0))
    assert out["orizzonti_decaduti"] == [5] and out["esito"] == "PASSA"
    out = S.riassumi(_righe(10, lambda i: 0.1, lambda i: nan if i < 5 else -3.0))   # meta' esatta: resta
    assert out["orizzonti_decaduti"] == [] and out["esito"] == "RIFIUTA per misura"
    out = S.riassumi(_righe(10, lambda i: nan, lambda i: nan))
    assert out["orizzonti_decaduti"] == [1, 5] and out["esito"] == "GUASTO"
