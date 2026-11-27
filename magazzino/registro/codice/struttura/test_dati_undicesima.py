"""Test chiesti dall'undicesima passata del gatekeeper (27/11), solo su dati sintetici. 0 trial.

python -m pytest magazzino/registro/codice/struttura/test_dati_undicesima.py -q
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
import simula_n2 as S  # noqa: E402
import verifica_generatore as VG  # noqa: E402
from test_dati import _barre_utc, _conteggi_sintetici, _scrivi_csv  # noqa: E402


# ---------------------------------------------------------------- B1: catena delle correzioni

def _esiti(tmp_path, monkeypatch, **file):
    monkeypatch.setattr(G, "ESITI", tmp_path)
    monkeypatch.setattr(G, "_sporchi", lambda p: [])
    monkeypatch.setattr(G, "verifica", lambda **k: {"commit": "x", "versioni": {}, "sha256": {}})
    for nome, esito in file.items():
        (tmp_path / nome).write_text(json.dumps(esito), encoding="utf-8")


def test_correzione_solo_dopo_guasto(tmp_path, monkeypatch):
    _esiti(tmp_path, monkeypatch, **{"controllo_struttura.json": {}})
    with pytest.raises(G.GuardiaFallita):                              # manca la base
        G.catena_guasta([()], VG.nome_esito)
    (tmp_path / "verifica_generatore_c0.json").write_text(json.dumps({"esito": "PASSA"}), encoding="utf-8")
    with pytest.raises(G.GuardiaFallita):                              # la base passa: niente (1)
        G.catena_guasta([()], VG.nome_esito)
    (tmp_path / "verifica_generatore_c0.json").write_text(json.dumps({"esito": "GUASTO"}), encoding="utf-8")
    G.catena_guasta([()], VG.nome_esito)
    with pytest.raises(G.GuardiaFallita):                              # (1, 2) senza (1) GUASTO
        G.catena_guasta([(), (1,)], VG.nome_esito)


def test_verifica_con_correzione_rifiuta_senza_base(tmp_path, monkeypatch):
    _esiti(tmp_path, monkeypatch, **{"controllo_struttura.json": {}})
    monkeypatch.setattr(sys, "argv", ["verifica_generatore.py", "--correzioni", "1"])
    with pytest.raises(G.GuardiaFallita):
        VG.main()


def test_un_solo_n2(tmp_path, monkeypatch):
    c = _conteggi_sintetici(["SPX500", "BUND"])
    _esiti(tmp_path, monkeypatch, **{"controllo_struttura.json": c, "verifica_generatore_c0.json": {"esito": "PASSA"},
                                     "n2_c0.json": {"esito": "PASSA"}})
    monkeypatch.setattr(G, "HASH_I3", tmp_path / "controllo_struttura.json")
    monkeypatch.setattr(S, "esegui", lambda *a, **k: (_ for _ in ()).throw(AssertionError("replica simulata")))
    monkeypatch.setattr(sys, "argv", ["n2.py"])
    with pytest.raises(G.GuardiaFallita):
        N2.main()


def test_n2_blocca_la_lettura_dei_csv(tmp_path, monkeypatch):
    c = _conteggi_sintetici(["SPX500", "BUND"])
    _esiti(tmp_path, monkeypatch, **{"controllo_struttura.json": c, "verifica_generatore_c0.json": {"esito": "GUASTO"}})
    monkeypatch.setattr(G, "HASH_I3", tmp_path / "controllo_struttura.json")
    monkeypatch.setattr(sys, "argv", ["n2.py"])
    originale = D.leggi_barre
    try:
        with pytest.raises(G.GuardiaFallita):
            N2.main()
        with pytest.raises(G.GuardiaFallita):
            D.leggi_barre("SPX500")
    finally:
        D.leggi_barre = originale


def test_potenza_usa_l_unico_n2(tmp_path, monkeypatch):
    _esiti(tmp_path, monkeypatch, **{"n2_c0.json": {}, "n2_c1.json": {}})
    with pytest.raises(G.GuardiaFallita):
        PO.unico_n2()
    (tmp_path / "n2_c1.json").unlink()
    assert PO.unico_n2() == "n2_c0.json"


# ---------------------------------------------------------------- B2 e correzioni del generatore

def test_correzione_uno_riproduce_p_ora_per_orario():
    T, N = 20000, 1
    d = S.nessun_difetto(T, N)
    d["p_ora"][:, :, 0] = 0.02
    d["p_ora"][:, 10:14, 0] = 0.30
    d["p_ora"][:, 20, 0] = 0.90                                      # un orario di pausa
    d["L_mancanti"] = np.full((T, N), 2.0)
    X = np.cumsum(np.random.default_rng(1).standard_normal((T, 27, N)), axis=1)
    Y = S.applica_difetti(X, np.random.default_rng(2), d)
    sim = np.isnan(Y[:, :, 0]).mean(axis=0)
    assert np.allclose(sim, d["p_ora"][0, :, 0], atol=0.012)
    blocchi = []
    for riga in np.isnan(Y[:, 9:15, 0]):
        n = 0
        for v in riga:
            if v:
                n += 1
            elif n:
                blocchi.append(n)
                n = 0
    assert np.mean(blocchi) > 1.5                                     # mancanti a blocchi, non isolati


def test_correzioni_due_e_tre_riproducono_le_marginali():
    T = 30000
    d = S.nessun_difetto(T, 3)
    d["p_tutti"] = np.full(T, 0.02)
    d["coppia"] = (0, 1)
    d["p_insieme"] = np.full(T, 0.05)
    d["p_giorno"][:] = 0.03
    X = np.cumsum(np.random.default_rng(3).standard_normal((T, 27, 3)), axis=1)
    Y = S.applica_difetti(X, np.random.default_rng(4), d)
    vuote = np.isnan(Y).all(axis=1)
    attesa_coppia = 1 - (1 - 0.02) * (1 - 0.05) * (1 - 0.03)
    attesa_terzo = 1 - (1 - 0.02) * (1 - 0.03)
    assert abs(vuote[:, 0].mean() - attesa_coppia) < 0.006
    assert abs(vuote[:, 2].mean() - attesa_terzo) < 0.005
    assert abs((vuote[:, 0] & vuote[:, 1] & vuote[:, 2]).mean() - (0.02 + 0.98 * 0.05 * 0.03 * 0.03)) < 0.004


def test_correzione_quattro_quota_intermedia():
    T, N = 20000, 1
    d = S.nessun_difetto(T, N)
    d["L"][:] = 1.5
    valori = np.broadcast_to(np.arange(27) / 26.0, (1, N, 27)).copy()
    cdf = np.zeros((1, N, 27))
    cdf[0, 0, 0:3] = 0.5                                              # meta' sedute quota 0
    cdf[0, 0, 3:] = 1.0                                               # meta' quota 3/26
    d["quote"] = (valori, cdf, np.zeros(T, int))
    X = np.cumsum(np.random.default_rng(5).standard_normal((T, 27, N)), axis=1)
    Y = S.applica_difetti(X, np.random.default_rng(6), d)
    r, oss = M.rendimenti(Y, 1)
    q = ((r == 0) & oss).sum(axis=1)[:, 0] / oss.sum(axis=1)[:, 0]
    assert not np.isnan(Y).any()
    assert abs(q.mean() - 0.5 * 3 / 26) < 0.01


def test_parametri_correzione_uno_e_interrotti_condizionati():
    c = _conteggi_sintetici(["SPX500", "BUND"])
    x = c["strumenti"]["SPX500"]["sviluppo"]["2020"]
    x["durata_media_mancanti"] = 2.0
    x["prezzi_mancanti_per_orario"] = [5] * 27
    x["intervalli_interrotti_per_orario"] = [0] * 25 + [10]
    x["intervalli_con_estremi_presenti_per_orario"] = [100] * 25 + [20]
    d = DF.da_conteggi(c, c["universo"], np.array(["2020"] * 3), (1,))
    assert d["L_mancanti"][0, 0] > 2.0                                # corretta per il troncamento su 27 prezzi
    assert np.isclose(d["p_interrotti"][0, 25, 0], 10 / 20)


# ---------------------------------------------------------------- R1 e controllo di struttura

def test_interrotto_con_estremo_mancante_non_si_conta():
    T = 4
    P = np.cumsum(np.random.default_rng(7).standard_normal((T, 27)), axis=1)
    P[0, 6] = np.nan
    it = np.zeros((T, 26), bool)
    it[:, 5] = True                                                   # intervallo 5: estremi 5 e 6
    c = CS.cella(P, it, np.ones(T, bool), np.zeros((T, 78), bool), np.ones((T, 78), bool))
    assert c["intervalli_interrotti_per_orario"][5] == 3
    assert c["intervalli_con_estremi_presenti_per_orario"][5] == 3
    assert c["barre_assenti_per_orario"] == [0] * 78


def test_selezione_oltre_la_data_limite_si_ferma():
    with pytest.raises(G.GuardiaFallita):
        CS.selezione(["SPX500"], pd.DatetimeIndex(["2024-11-08", "2024-11-11"]), {})


def test_controllo_struttura_intero_su_csv_sintetici(tmp_path, monkeypatch):
    giorni, _ = D.sedute("2024-01-02", "2024-12-31")
    nomi = G.VECCHI + G.NUOVI
    barre = {n: _barre_utc(giorni, seme=k) for k, n in enumerate(nomi)}
    barre["BTCUSD"] = barre["BTCUSD"][barre["BTCUSD"]["time"] >= pd.Timestamp("2024-02-01")]   # inizio piu' tardo

    def leggi(nome, fino_a=None, percorso=None):
        b = barre[nome]
        return b[b["time"] < (D.TAGLIO_UTC if fino_a is None else fino_a)].reset_index(drop=True)

    monkeypatch.setattr(D, "leggi_barre", leggi)
    monkeypatch.setattr(CS, "INIZIO_SEDUTE", "2024-01-02")
    monkeypatch.setattr(D, "FINE", pd.Timestamp("2024-12-31"))
    monkeypatch.setattr(G, "verifica", lambda **k: {"commit": "x", "versioni": {}, "sha256": {}})
    monkeypatch.setattr(G, "ESITI", tmp_path)
    CS.main()
    out = json.loads((tmp_path / CS.ESITO).read_text(encoding="utf-8"))
    assert set(out) == CS.CHIAVI
    assert out["inizio_comune"] == "2024-02-01"
    assert out["universo"] == list(S.UNIVERSO)                        # ordine del §7, DAX dentro, nessuno escluso
    assert set(out["strumenti"]["SPX500"]) == {"sviluppo", "blocco"}
    assert "2024" in out["strumenti"]["SPX500"]["blocco"]
    assert out["anni"]["sviluppo"]["2024"]["escluse_unione"] == 0
    assert out["orizzonti_decaduti"] == [1, 5]                       # meno di un anno: nessuna origine
    assert set(out["selezione"]["SPX500"]["2024"]) == CS.SELEZIONE


# ---------------------------------------------------------------- guardie dei dati

def test_controlla_dati_byte_sha_e_data(tmp_path, monkeypatch):
    g = pd.DatetimeIndex(["2026-11-10"])
    p_ok = _scrivi_csv(tmp_path, _barre_utc(g), "BUND")
    reg = {"byte": {"BUND": p_ok.stat().st_size}, "sha256": {"BUND": G.sha256(p_ok)}}
    (tmp_path / "h.json").write_text(json.dumps(reg), encoding="utf-8")
    monkeypatch.setattr(G, "HASH_I3", tmp_path / "h.json")
    monkeypatch.setattr(G, "HASH_VOL", tmp_path / "h.json")
    monkeypatch.setattr(G, "ROOT", tmp_path)
    monkeypatch.setitem(G.DATI, "BUND", "BUND_M5.csv")
    assert G.controlla_dati(["BUND"])["BUND"] == reg["sha256"]["BUND"]
    reg["sha256"]["BUND"] = "0" * 64
    (tmp_path / "h.json").write_text(json.dumps(reg), encoding="utf-8")
    with pytest.raises(G.GuardiaFallita):
        G.controlla_dati(["BUND"])
    p2 = _scrivi_csv(tmp_path, _barre_utc(pd.DatetimeIndex(["2026-11-11"])), "BUND")
    reg = {"byte": {"BUND": p2.stat().st_size}, "sha256": {"BUND": G.sha256(p2)}}
    (tmp_path / "h.json").write_text(json.dumps(reg), encoding="utf-8")
    with pytest.raises(G.GuardiaFallita):                             # barre oltre il 2026-11-10
        G.controlla_dati(["BUND"])


def test_scaricatore_e_registro_non_riscrivono(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "ROOT", tmp_path)
    monkeypatch.setitem(G.DATI, "BUND", "BUND_M5.csv")
    (tmp_path / "BUND_M5.csv").write_text("x", encoding="utf-8")
    with pytest.raises(G.GuardiaFallita):
        D.scarica("BUND")
    (tmp_path / "h.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(G, "HASH_I3", tmp_path / "h.json")
    with pytest.raises(G.GuardiaFallita):
        D.registra()
