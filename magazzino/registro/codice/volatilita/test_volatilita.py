"""Test veloci della pipeline della famiglia `volatilita`, solo su dati sintetici. 0 trial.

python -m pytest magazzino/registro/codice/volatilita/test_volatilita.py -q
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import giorni as G  # noqa: E402
import invarianza as I  # noqa: E402
import modelli as M  # noqa: E402
import pipeline as P  # noqa: E402

W, PASSO = 200, 5


def _barre_indice():
    """Due sedute XNYS normali (2024-11-04, 05) con una barra mancante e la prima barra assente il secondo giorno."""
    import exchange_calendars as xc

    sched = xc.get_calendar("XNYS").schedule.loc["2024-11-01":"2024-11-05"]
    rng = np.random.default_rng(0)
    righe = []
    prezzo = 100.0
    for k, (ap, ch) in enumerate(zip(sched["open"], sched["close"])):
        t = pd.date_range(ap.tz_convert("UTC").tz_localize(None), ch.tz_convert("UTC").tz_localize(None),
                          freq="5min", inclusive="left")
        if k == 2:
            t = t[1:]                                   # manca la barra d'apertura
        if k == 1:
            t = t.delete(10)                            # manca una barra in mezzo
        for x in t:
            o = prezzo * np.exp(rng.normal(0, 0.001))
            prezzo = o * np.exp(rng.normal(0, 0.001))
            righe.append((x, o, prezzo))
        prezzo *= np.exp(rng.normal(0, 0.005))         # notte
        righe.append((t[-1] + pd.Timedelta(hours=2), prezzo, prezzo))   # barra fuori seduta: si ignora
    return pd.DataFrame(righe, columns=["time", "open", "close"]), sched


def test_somme_esatte_indice():
    barre, sched = _barre_indice()
    d = G.giorni_indice(barre, "XNYS", inizio=pd.Timestamp("2024-11-04"), fine=pd.Timestamp("2024-11-05"))
    assert list(d.index.date.astype(str)) == ["2024-11-04", "2024-11-05"]
    ch = {}
    for data, (ap, c) in zip(sched.index, zip(sched["open"], sched["close"])):
        a, b = ap.tz_convert("UTC").tz_localize(None), c.tz_convert("UTC").tz_localize(None)
        s = barre[(barre.time >= a) & (barre.time < b)]
        ch[data] = s.close.iloc[-1]
    assert abs(d.loc["2024-11-04", "r"] - 100 * np.log(ch[pd.Timestamp("2024-11-04")] / ch[pd.Timestamp("2024-11-01")])) < 1e-9
    assert abs(d.loc["2024-11-05", "r"] - 100 * np.log(ch[pd.Timestamp("2024-11-05")] / ch[pd.Timestamp("2024-11-04")])) < 1e-9
    assert bool(d.loc["2024-11-05", "apertura_mancante"]) and not bool(d.loc["2024-11-04", "apertura_mancante"])
    assert d.loc["2024-11-04", "barre"] == 77 and d.loc["2024-11-04", "attese"] == 78
    assert (d["v"] >= d["notte"] ** 2).all()


def test_giorno_24h_e_pausa():
    t = pd.date_range("2024-11-03 22:00", "2024-11-05 22:00", freq="5min", inclusive="left")   # dom 17:00 NY -> mar
    rng = np.random.default_rng(1)
    o = 100 * np.exp(np.cumsum(rng.normal(0, 0.001, len(t))))
    c = o * np.exp(rng.normal(0, 0.001, len(t)))
    barre = pd.DataFrame({"time": t, "open": o, "close": c})
    d = G.giorni_24h(barre, inizio=pd.Timestamp("2024-11-01"))
    assert list(d.index.date.astype(str)) == ["2024-11-04", "2024-11-05"]
    lun = barre[(barre.time >= "2024-11-03 22:00") & (barre.time < "2024-11-04 22:00")]
    assert abs(d.loc["2024-11-04", "r"] - 100 * np.log(lun.close.iloc[-1] / lun.open.iloc[0])) < 1e-9
    assert d.loc["2024-11-04", "barre"] == 288 and not d.loc["2024-11-04", "escluso"]


def test_holdout_sigillato():
    with pytest.raises(PermissionError):
        G.leggi_barre("SPX500", fino_a=pd.Timestamp("2024-11-12"))
    with pytest.raises(PermissionError):
        G.carica_vix(fino_a=pd.Timestamp("2025-01-01"))
    assert G.HOLDOUT_APERTO is False


def test_egarch_multi_contro_simulazione():
    from arch import arch_model

    rng = np.random.default_rng(2)
    y = rng.standard_normal(600)
    am = arch_model(y, mean="Zero", vol="EGARCH", p=1, o=1, q=1, rescale=False)
    par = np.array([0.02, 0.15, -0.10, 0.95])
    res = am.fix(par)
    s1 = res.forecast(horizon=1, start=590, reindex=False).variance.to_numpy()[:, 0]
    an = M.egarch_multi(s1, *par)
    sim = res.forecast(horizon=5, start=590, reindex=False, method="simulation", simulations=100_000,
                       random_state=np.random.RandomState(0)).variance.to_numpy()
    assert np.max(np.abs(an / sim - 1)) < 0.01


def test_bersagli_esclusi():
    v = np.arange(1.0, 11.0)
    esc = np.zeros(10, bool)
    esc[6] = True
    b = P.bersagli(v, esc)
    assert b[0, 0] == 2.0 and b[0, 1] == 2 + 3 + 4 + 5 + 6
    assert np.isnan(b[5, 0]) and np.isnan(b[1, 1]) and b[6, 0] == 8.0
    assert np.isnan(b[9, 0]) and np.isnan(b[5, 1])


def test_riscala_solo_passato():
    rng = np.random.default_rng(3)
    r = rng.standard_normal(300)
    v = r ** 2 * 1.3
    c = M.riscala(r, v, 100)
    assert np.isnan(c[98]) and abs(c[99] - 1.3) < 1e-12 and abs(c[-1] - 1.3) < 1e-12


def test_invarianza_piccola_tutti_i_modelli():
    r, v = I.sintetica(W + 40, 5)
    for t in (W - 1, W + 3, W + 4, W + 5, W + 17):
        a = P.previsioni(r, v, origini=[t], partenze_hmm=2, w=W, passo=PASSO)["previsioni"]
        r2, v2 = I.con_rumore(r, v, t, 9)
        b = P.previsioni(r2, v2, origini=[t], partenze_hmm=2, w=W, passo=PASSO)["previsioni"]
        assert set(a) == set(P.SCALA_RENDIMENTI + P.SCALA_V)
        for m in a:
            assert np.all(np.isfinite(a[m][t])) and np.all(a[m][t] > 0), (m, t)
            assert np.max(np.abs(a[m][t] - b[m][t])) <= 1e-10, (m, t)


def test_ristretta_uguale_alla_completa():
    r, v = I.sintetica(W + 30, 6)
    piena = P.previsioni(r, v, modelli=["ewma", "gjr", "hmm2", "har"], partenze_hmm=2, w=W, passo=PASSO)
    for t in (W + 2, W + 11):
        rist = P.previsioni(r, v, modelli=["ewma", "gjr", "hmm2", "har"], origini=[t], partenze_hmm=2, w=W,
                            passo=PASSO)
        for m in rist["previsioni"]:
            assert np.allclose(rist["previsioni"][m][t], piena["previsioni"][m][t], rtol=0, atol=1e-12)
    assert np.all(np.isnan(piena["previsioni"]["ewma"][: W - 1]))


def test_hmm_regimi_previsione_sensata():
    """Su un processo a due regimi ben separati la previsione segue il regime (controllo grossolano)."""
    rng = np.random.default_rng(4)
    s = np.repeat([0.5, 3.0, 0.5, 3.0], 75)
    r = rng.standard_normal(300) * s
    out = M.prevedi_hmm(r, 2, w=W, passo=PASSO, partenze=3)
    F = out["F"][:, 0]
    assert np.nanmean(F[225:300]) > 3 * np.nanmean(F[200:220])


def _variante(funzione, sostituzioni):
    """Copia di una funzione di `modelli` con una fuga iniettata (solo per il controllo positivo)."""
    import inspect

    src = inspect.getsource(funzione)
    for a, b in sostituzioni:
        assert a in src, a
        src = src.replace(a, b)
    ns = dict(vars(M))
    exec(src, ns)
    return ns[funzione.__name__]


def _diff_invarianza(r, v, modelli, origini, partenze_hmm=2):
    d = 0.0
    for t in origini:
        a = P.previsioni(r, v, modelli=modelli, origini=[t], partenze_hmm=partenze_hmm, w=W, passo=PASSO)["previsioni"]
        r2, v2 = I.con_rumore(r, v, t, 9)
        b = P.previsioni(r2, v2, modelli=modelli, origini=[t], partenze_hmm=partenze_hmm, w=W, passo=PASSO)["previsioni"]
        d = max(d, max(float(np.max(np.abs(a[m][t] - b[m][t]))) for m in modelli))
    return d


def test_invarianza_rileva_le_fughe(monkeypatch):
    """Controllo positivo del passo 1: quattro fughe di un giorno iniettate devono superare la tolleranza."""
    import controlli as C

    r, v = I.sintetica(W + 40, 5)
    origini = (W - 1, W + 4)                                              # inizi di blocco
    fughe = [
        ("prevedi_arch", _variante(M.prevedi_arch, [("r[t0 - w + 1:t0 + 1], tipo)\n        with",
                                                     "r[t0 - w + 2:t0 + 2], tipo)\n        with")]), ["gjr"]),
        ("prevedi_har", _variante(M.prevedi_har, [("(0, y1, t0 - 1)", "(0, y1, t0)")]), ["har"]),
        ("riscala", lambda r_, v_, w=M.W, _c=M.riscala: np.r_[_c(r_, v_, w)[1:], np.nan], ["ewma"]),
    ]
    for nome, f, modelli in fughe:
        assert _diff_invarianza(r, v, modelli, origini) <= I.TOLLERANZA, nome
        with monkeypatch.context() as mp:
            mp.setattr(M, nome, f)
            assert _diff_invarianza(r, v, modelli, origini) > 1e3 * I.TOLLERANZA, nome
    rr, _ = C.simula("regimi", W + 40, np.random.default_rng(1))
    vv = rr ** 2 + 1e-4
    smussate = _variante(M._previsione_hmm, [("f = m.filter(params)", "f = m.smooth(params)"),
                                             ("filtered_marginal_probabilities", "smoothed_marginal_probabilities")])
    assert _diff_invarianza(rr, vv, ["hmm2"], (W - 1, W), 3) <= I.TOLLERANZA
    with monkeypatch.context() as mp:
        mp.setattr(M, "_previsione_hmm", smussate)
        assert _diff_invarianza(rr, vv, ["hmm2"], (W - 1, W), 3) > 1e3 * I.TOLLERANZA
