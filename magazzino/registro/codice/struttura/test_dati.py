"""Test della parte sui dati di I3 (commit (1)), solo su dati sintetici: nessun file di prezzi vero si apre. 0 trial.

python -m pytest magazzino/registro/codice/struttura/test_dati.py -q
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))

import controllo_struttura as CS  # noqa: E402
import dati as D  # noqa: E402
import difetti as DF  # noqa: E402
import guardie as G  # noqa: E402
import misura as M  # noqa: E402
import n2 as N2  # noqa: E402
import potenza as PO  # noqa: E402
import previsioni as V  # noqa: E402
import simula_n2 as S  # noqa: E402
import verifica_generatore as VG  # noqa: E402


# ---------------------------------------------------------------- dati sintetici

def _barre_utc(giorni_ny, seme=0, togli=()):
    """Barre M5 sintetiche (UTC senza fuso) che coprono 9:00-16:30 di New York in ogni giorno; `togli` = tempi NY."""
    rng = np.random.default_rng(seme)
    righe = []
    for g in giorni_ny:
        loc = pd.date_range(pd.Timestamp(g) + pd.Timedelta("9h"), pd.Timestamp(g) + pd.Timedelta("16h25min"),
                            freq="5min")
        for t in loc:
            if t in togli:
                continue
            utc = t.tz_localize(D.NY).tz_convert("UTC").tz_localize(None)
            o = 100 + rng.standard_normal()
            righe.append((utc, o, o + 0.1))
    return pd.DataFrame(righe, columns=["time", "open", "close"])


def _scrivi_csv(tmp_path, df, nome="X"):
    p = tmp_path / ("%s_M5.csv" % nome)
    d = df.copy()
    d["high"] = d[["open", "close"]].max(axis=1)
    d["low"] = d[["open", "close"]].min(axis=1)
    d["volume"] = 0.0
    d[["time", "open", "high", "low", "close", "volume"]].to_csv(p, index=False)
    return p


# ---------------------------------------------------------------- loader, fuso, sedute, griglia

def test_lettura_si_ferma_al_taglio(tmp_path):
    g = pd.DatetimeIndex(["2026-11-09", "2026-11-10", "2026-11-11"])
    p = _scrivi_csv(tmp_path, _barre_utc(g))
    b = D.leggi_barre("X", percorso=p)
    assert b["time"].max() < D.TAGLIO_UTC
    b2 = D.leggi_barre("X", fino_a=D.TAGLIO_SVILUPPO_UTC, percorso=p)
    assert len(b2) == 0
    with pytest.raises(PermissionError):
        D.leggi_barre("X", fino_a="2026-11-12", percorso=p)


def test_fuso_una_volta_sola():
    b = D.a_new_york(_barre_utc(pd.DatetimeIndex(["2024-06-03"])))
    with pytest.raises(D.FusoGiaApplicato):
        D.a_new_york(b)


@pytest.mark.parametrize("giorno", ["2024-03-08", "2024-03-11", "2024-03-29", "2024-04-01",
                                    "2024-10-25", "2024-10-28", "2024-11-01", "2024-11-04"])
def test_griglia_ai_cambi_d_ora(giorno):
    """Cambi d'ora americani (10/03, 03/11) ed europei (31/03, 27/10): l'open delle 9:30 di New York e' sempre la
    barra che inizia alle 9:30 locali, qualunque sia lo scarto da UTC."""
    g = pd.DatetimeIndex([giorno])
    b = _barre_utc(g, seme=1)
    bny = D.a_new_york(b)
    P, pres = D.griglia(bny, g)
    atteso = bny.set_index("ny")
    t930 = pd.Timestamp(giorno) + pd.Timedelta("9h30min")
    t940 = pd.Timestamp(giorno) + pd.Timedelta("9h40min")
    t1555 = pd.Timestamp(giorno) + pd.Timedelta("15h55min")
    assert P[0, 0] == np.log(atteso.loc[t930, "open"])
    assert P[0, 1] == np.log(atteso.loc[t940, "close"])
    assert P[0, 26] == np.log(atteso.loc[t1555, "close"])
    assert pres.all()


def test_sedute_piene_senza_chiusure_anticipate():
    g, n = D.sedute("2024-11-25", "2024-12-31")
    assert pd.Timestamp("2024-11-29") not in g and pd.Timestamp("2024-12-24") not in g
    assert pd.Timestamp("2024-11-27") in g and n == 2
    uno, _ = D.sedute("2024-11-11", "2025-11-10")
    assert len(uno) == S.N_H == 247


def test_griglia_mancanti_e_file_senza_prezzi():
    g = pd.DatetimeIndex(["2024-06-03", "2024-06-04"])
    t = pd.Timestamp("2024-06-03") + pd.Timedelta("9h40min")
    P, pres = D.griglia(D.a_new_york(_barre_utc(g[:1], togli=[t])), g)
    assert np.isnan(P[0, 1]) and np.isfinite(P[0, 2])
    assert not pres[0, 2] and pres[0, 1]
    assert np.isnan(P[1]).all() and not pres[1].any()               # seduta senza barre
    vuoto = pd.DataFrame({"time": pd.to_datetime([]), "open": [], "close": []})
    P0, pres0 = D.griglia(D.a_new_york(vuoto), g)                    # strumento senza prezzi
    assert np.isnan(P0).all() and not pres0.any()


def test_pause_e_rollover_tolti_una_volta():
    g = pd.DatetimeIndex(pd.bdate_range("2024-06-03", periods=6))
    pausa_ny = [d + pd.Timedelta("11h05min") for d in g[:4]]       # barra interna dell'intervallo 10 (11:00-11:15)
    b = D.a_new_york(_barre_utc(g, togli=pausa_ny))
    P, pres = D.griglia(b, g)
    pausa = D.orari_di_pausa(pres, np.asarray(g.year))
    m = (11 * 60 + 5 - 570) // 5
    assert pausa[:, m].all() and pausa.sum(axis=1).tolist() == [1] * 6     # 4 su 6 sedute: pausa dell'anno
    roll = [g[5] + pd.Timedelta("14h07min"), g[5] + pd.Timedelta("20h")]   # dentro e fuori dalla seduta
    it = D.interrotti(pres, pausa, g, rollover=roll)
    assert it[:4, 6].all() and not it[4:, 6].any()
    assert it[5, (14 * 60 + 7 - 570) // 15] and it.sum() == 5
    r15, o15 = M.rendimenti(P[:, :, None], 1, it[:, :, None])
    assert not o15[0, 6, 0] and np.isfinite(P[0, 6]) and np.isfinite(P[0, 7])
    r30, o30 = M.rendimenti(P[:, :, None], 2, it[:, :, None])
    assert not o30[0, 3, 0] and o30[0, 2, 0]                          # 6 e 7 a 15 minuti stanno nel 3 a 30


# ---------------------------------------------------------------- controllo di struttura

def test_cella_solo_conteggi_e_chiavi():
    T = 40
    X = np.cumsum(np.random.default_rng(2).standard_normal((T, 27, 1)), axis=1)
    d = S.nessun_difetto(T, 1)
    d["p0"][:] = 0.1
    d["L"][:] = 2.0
    d["p_giorno"][:] = 0.1
    Y = S.applica_difetti(X, np.random.default_rng(3), d)[:, :, 0]
    it = np.zeros((T, 26), bool)
    r, oss = M.rendimenti(Y[:, :, None], 1)
    v = M.validi_strumento(r, oss)[:, 0]
    c = CS.cella(Y, it, v, np.zeros((T, 78), bool))
    assert set(c) == CS.CELLA
    assert c["sedute"] == T and c["sedute_presenti"] + c["sedute_senza_prezzi"] == T
    assert sum(c["istogramma_nulli"]) == c["sedute_presenti"]
    assert c["rendimenti_nulli"] == int((oss & (r == 0)).sum())
    with pytest.raises(G.GuardiaFallita):
        G.controlla_chiavi({**c, "media": 0.0}, CS.CELLA)


def test_origini_da_maschere_come_la_pipeline():
    T = 800
    X = S.rendimenti_veri(T, np.random.default_rng(4), S.r_bar())["X"]
    d = S.nessun_difetto(T, 17)
    d["p_giorno"][:, 3] = 0.03
    d["p0"][:, 5] = 0.08
    d["L"][:, 5] = 2.0
    Y = S.applica_difetti(X, np.random.default_rng(5), d)
    m = M.matrici(Y)
    diff = V.differenziali(m)
    da_maschere = V.origini_da_maschere(m["valido_i"])
    for h in (1, 5):
        assert np.array_equal(diff[("costante", h)][0], da_maschere[h])
        assert len(da_maschere[h]) > 50


# ---------------------------------------------------------------- generatore e conteggi

def _conteggi_sintetici(universo, inizio="2019-01-02", fine="2021-12-31", seme=6, p0=0.05, p_giorno=0.02):
    """Conteggi in formato controllo di struttura, prodotti dal generatore stesso (per i test)."""
    giorni, _ = D.sedute(inizio, fine)
    anni = np.asarray(giorni.year)
    T, N = len(giorni), len(universo)
    X = np.cumsum(np.random.default_rng(seme).standard_normal((T, 27, N)), axis=1)
    d = S.nessun_difetto(T, N)
    d["p0"][:] = p0
    d["L"][:] = 2.0
    d["p_giorno"][:] = p_giorno
    Y = S.applica_difetti(X, np.random.default_rng(seme + 1), d)
    it = np.zeros((T, 26, N), bool)
    r, oss = M.rendimenti(Y, 1)
    v = M.validi_strumento(r, oss)
    st = {n: {"sviluppo": {}, "blocco": {}} for n in universo}
    an = {"sviluppo": {}, "blocco": {}}
    for a in np.unique(anni):
        k = anni == a
        for i, n in enumerate(universo):
            st[n]["sviluppo"][str(a)] = CS.cella(Y[k, :, i], it[k, :, i], v[k, i], np.zeros((k.sum(), 78), bool))
        ass = ~np.isfinite(Y[k]).any(axis=1)
        an["sviluppo"][str(a)] = {"sedute": int(k.sum()), "escluse_unione": int((~v[k].all(axis=1)).sum()),
                                  "senza_prezzi_tutti": int(ass.all(axis=1).sum()),
                                  "dax_bund_insieme": int((ass[:, 0] & ass[:, 1]).sum())}
    return {"universo": list(universo), "strumenti": st, "anni": an, "inizio_comune": str(giorni[0].date()),
            "fine_sviluppo": str(giorni[-1].date()), "orizzonti_decaduti": []}


def test_correzioni_in_ordine_e_condizionate():
    c = _conteggi_sintetici(["DAX", "BUND", "SPX500"])
    with pytest.raises(ValueError):
        DF.controlla_correzioni((2,))
    a = c["anni"]["sviluppo"]["2020"]
    a.update(senza_prezzi_tutti=3, dax_bund_insieme=8)
    x = c["strumenti"]["DAX"]["sviluppo"]["2020"]
    x["sedute_senza_prezzi"] = 12
    anni = np.array(["2020"] * 5)
    d = DF.da_conteggi(c, c["universo"], anni, (1, 2, 3))
    n = a["sedute"]
    assert np.isclose(d["p_tutti"][0], 3 / n)
    assert np.isclose(d["p_insieme"][0], 5 / (n - 3))
    assert np.isclose(d["p_giorno"][0, 0], (12 - 3 - 5) / (n - 3 - 5))     # un proprietario per seduta mancante
    assert d["coppia"] == (0, 1) and "L_mancanti" in d and "quote" not in d


def test_correzione_quattro_esclude_sopra_il_quarto():
    T, N = 400, 1
    d = S.nessun_difetto(T, N)
    d["L"][:] = 1.0
    valori = np.broadcast_to(np.arange(27) / 26.0, (1, N, 27)).copy()
    cdf = np.zeros((1, N, 27))
    cdf[0, 0, 13:] = 1.0                                               # quota 0,5 sempre: sempre escluso
    d["quote"] = (valori, cdf, np.zeros(T, int))
    X = np.cumsum(np.random.default_rng(8).standard_normal((T, 27, N)), axis=1)
    Y = S.applica_difetti(X, np.random.default_rng(9), d)
    assert np.isnan(Y).all()


def test_generatore_base_invariato():
    """Senza correzioni il flusso dei numeri e' quello del 24/11 (stessa estrazione per seduta)."""
    T, N, K = 50, 3, 27
    X = np.cumsum(np.random.default_rng(10).standard_normal((T, K, N)), axis=1)
    d = S.nessun_difetto(T, N)
    d["p0"][:] = 0.1
    d["L"][:] = 2.0
    d["p_giorno"][:] = 0.05
    d["p_ora"][:, 4, :] = 0.2
    Y = S.applica_difetti(X, np.random.default_rng(11), d)
    rng = np.random.default_rng(11)
    pu = S.prob_fermo(d["p0"], d["L"])
    resta = 1.0 - 1.0 / d["L"]
    Z = np.empty_like(X)
    for t in range(T):
        ug, uf, uo = rng.random(N), rng.random((K, N)), rng.random((K, N))
        y = X[t].copy()
        f = uf[0] < d["p0"][t]
        for k in range(1, K):
            f = np.where(f, uf[k] < resta[t], uf[k] < pu[t])
            y[k] = np.where(f, y[k - 1], X[t, k])
        y[uo < d["p_ora"][t]] = np.nan
        y[:, ug < d["p_giorno"][t]] = np.nan
        Z[t] = y
    assert np.array_equal(np.isnan(Y), np.isnan(Z)) and np.array_equal(Y[np.isfinite(Y)], Z[np.isfinite(Z)])


def test_gruppi_di_anni_e_p_bilaterale():
    assert VG.gruppi_di_anni({"2019": 40, "2020": 250, "2021": 250, "2024": 30}) == \
        [["2019", "2020"], ["2021", "2024"]]
    assert VG.p_bilaterale(0, 100, 0.0) == 1.0 and VG.p_bilaterale(1, 100, 0.0) == 0.0
    assert VG.p_bilaterale(50, 100, 0.5) > 0.9


def test_verifica_generatore_passa_e_si_guasta():
    c = _conteggi_sintetici(["SPX500", "BUND"], p0=0.08, p_giorno=0.03)
    ok = VG.verifica(c, anni_simulati=20, seme=1)
    assert ok["esito"] == "PASSA" and len(ok["celle"]) == 3 * 3
    for a, x in c["strumenti"]["BUND"]["sviluppo"].items():
        x["sedute_escluse"] = x["sedute"] // 2                        # conteggio vero lontano dal generatore
    assert VG.verifica(c, anni_simulati=20, seme=1)["esito"] == "GUASTO"


# ---------------------------------------------------------------- N2 e potenza

def _repo_finto(tmp_path, monkeypatch, conteggi, esito_verifica):
    monkeypatch.setattr(G, "ESITI", tmp_path)
    (tmp_path / "controllo_struttura.json").write_text(json.dumps(conteggi), encoding="utf-8")
    (tmp_path / "verifica_generatore_c0.json").write_text(json.dumps({"esito": esito_verifica}), encoding="utf-8")
    monkeypatch.setattr(G, "verifica", lambda **k: {"commit": "x", "versioni": {}, "sha256": {}})
    monkeypatch.setattr(G, "_sporchi", lambda p: [])
    monkeypatch.setattr(G, "HASH_I3", tmp_path / "controllo_struttura.json")
    monkeypatch.setattr(D, "leggi_barre", lambda *a, **k: (_ for _ in ()).throw(AssertionError("CSV aperto")))


def test_n2_non_parte_con_verifica_guasta(tmp_path, monkeypatch):
    c = _conteggi_sintetici(["SPX500", "BUND"])
    _repo_finto(tmp_path, monkeypatch, c, "GUASTO")
    monkeypatch.setattr(S, "esegui", lambda *a, **k: (_ for _ in ()).throw(AssertionError("replica simulata")))
    monkeypatch.setattr(sys, "argv", ["n2.py"])
    with pytest.raises(G.GuardiaFallita):
        N2.main()


def test_n2_legge_solo_i_conteggi_e_chiavi(tmp_path, monkeypatch):
    c = _conteggi_sintetici(["SPX500", "BUND", "EURUSD"])
    _repo_finto(tmp_path, monkeypatch, c, "PASSA")
    out = N2.esegui(c, repliche=2)
    assert set(out) == N2.CHIAVI - {"commit", "versioni"}
    assert set(out["risultato"]) == N2.CHIAVI_RIASSUNTO
    assert out["sedute"] == len(D.sedute(c["inizio_comune"], c["fine_sviluppo"])[0])


def test_n2_orizzonte_decaduto_sui_conteggi_non_decide():
    nan = float("nan")
    righe = [{"non_valide": 0, ("guardia", 1): False, ("guardia", 5): False,
              ("delta", "costante", 1): 0.1, ("delta", "costante", 5): -3.0,
              ("delta", "persistenza", 1): 0.0, ("delta", "persistenza", 5): 0.0} for _ in range(10)]
    assert S.riassumi(righe)["esito"] == "RIFIUTA per misura"
    assert S.riassumi(righe, esclusi=(5,))["esito"] == "PASSA"
    assert S.riassumi(righe, esclusi=(1, 5))["esito"] == "GUASTO"
    del nan


def test_potenza_data_limite_e_chiavi():
    PO.controlla_data(pd.DatetimeIndex(["2024-11-07", "2024-11-08"]))
    with pytest.raises(PO.OltreLaDataLimite):
        PO.controlla_data(pd.DatetimeIndex(["2024-11-08", "2024-11-11"]))
    with pytest.raises(G.GuardiaFallita):
        G.controlla_chiavi({"n_origini": 1, "ritardi_hac": 4, "sd_hac_centrata": 1.0, "media": 0.0},
                           PO.CHIAVI_ORIZZONTE)
    assert PO.sedute_holdout()["1"] == 247


def test_potenza_restituisce_solo_la_deviazione():
    T = 800
    X = S.rendimenti_veri(T, np.random.default_rng(12), S.r_bar())["X"][:, :, :4]
    out = PO.deviazioni(X, np.zeros((T, 26, 4), bool), (1, 5))
    for h, v in out.items():
        assert len(v) == 3 and isinstance(v[2], float) and v[2] > 0 and v[1] == V.ritardi_hac(h)


def test_potenza_legge_con_la_data_limite(monkeypatch):
    letti = []

    def finto(nome, fino_a=None, percorso=None):
        letti.append(fino_a)
        return pd.DataFrame({"time": pd.to_datetime([]), "open": [], "close": []})

    monkeypatch.setattr(D, "leggi_barre", finto)
    c = {"universo": ["SPX500"], "inizio_comune": "2024-10-01", "fine_sviluppo": "2024-11-08",
         "strumenti": {"SPX500": {"sviluppo": {"2024": {"orari_pausa": []}}}}}
    with pytest.raises(G.GuardiaFallita):
        PO.calcola(c, (1,))                                            # nessun dato: si ferma, niente NaN
    assert letti == [D.TAGLIO_SVILUPPO_UTC]


# ---------------------------------------------------------------- guardie

def test_esito_scritto_una_volta(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "ESITI", tmp_path)
    G.scrivi_esito("x.json", {"a": 1})
    with pytest.raises(G.GuardiaFallita):
        G.scrivi_esito("x.json", {"a": 2})
    assert json.loads((tmp_path / "x.json").read_text(encoding="utf-8")) == {"a": 1}


def test_errore_senza_valori():
    def rompe():
        raise ValueError("valore segreto 1,234")
    with pytest.raises(SystemExit) as e:
        G.protetto(rompe)
    assert "1,234" not in str(e.value) and "ValueError" in str(e.value)


def test_guardie_senza_git_e_versioni():
    out = G.verifica(git=False, dati=False)
    assert out["commit"] is None and out["versioni"]["exchange_calendars"] == "4.13.2"
