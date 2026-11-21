"""Campo `grandezze` del contatore (DECISIONS 2026-11-21 (2), LIFECYCLE §3 "stessa grandezza = stessa famiglia").

Prima del 21/11 il contatore non sapeva quale grandezza misurasse una famiglia: due id sulla stessa grandezza
passavano `--check` in silenzio (debito 1 del controllo di I2). Nessun dato vero: registri sintetici.
"""
from motore.core.trial_ledger import verifica, grandezze_condivise, tabella, load

BUDGET = {"round_rifinitura_per_famiglia": 3, "prereg_esterne_per_trimestre": 3,
          "prereg_esterne_per_trimestre_soglia_allarme": 2, "prereg_hub_per_trimestre": 1,
          "holdout_aperture_per_famiglia": 1, "llm_knowledge_cutoff": "2026-05-31"}


def _fam(fid, grandezze):
    f = {"id": fid, "stato": "CLOSED", "motivo_chiusura": "potenza", "round_rifinitura": 0, "fonti": ["x"],
         "provenienza_ipotesi": "umana_esterna", "finestra_dati_fine": "2026-10-01"}
    if grandezze is not None:
        f["grandezze"] = grandezze
    return f


def _dati(famiglie):
    return {"budget": BUDGET, "trimestre_corrente": "2026-Q4", "aggiornato": "2026-11-21", "famiglie": famiglie}


def test_grandezze_mancanti_sono_un_problema():
    assert any("grandezze non dichiarate" in p for p in verifica(_dati([_fam("a", None)]), registro={}))
    assert any("grandezze non dichiarate" in p for p in verifica(_dati([_fam("a", [])]), registro={}))


def test_grandezza_sconosciuta_e_un_problema():
    assert any("grandezza sconosciuta" in p for p in verifica(_dati([_fam("a", ["fase_lunare"])]), registro={}))


def test_due_famiglie_sulla_stessa_grandezza_non_sono_un_errore_ma_si_vedono():
    dati = _dati([_fam("tsmom", ["tendenza"]), _fam("trend", ["tendenza"]), _fam("lv", ["livelli"])])
    assert verifica(dati, registro={}) == []
    assert grandezze_condivise(dati) == {"tendenza": ["tsmom", "trend"]}
    assert "tendenza" in tabella(dati) and "tsmom, trend" in tabella(dati)


def test_una_grandezza_ripetuta_non_rende_una_famiglia_condivisa_con_se_stessa():
    assert grandezze_condivise(_dati([_fam("x", ["tendenza", "tendenza"])])) == {}


def test_il_contatore_vero_dichiara_le_grandezze_di_ogni_famiglia():
    dati = load()
    assert all(f.get("grandezze") for f in dati["famiglie"])
    assert not [p for p in verifica(dati, registro={}) if "grandezz" in p]


def _nuova(grandezze, binario="strumenti", parentela=None):
    f = _fam("nuova", grandezze)
    f.update(stato="BOZZA", motivo_chiusura=None, binario=binario)
    del f["motivo_chiusura"]
    if binario == "strumenti":
        f.update(alfa_famiglia=0.05, trial_cumulati=0,
                 sottofamiglie=[{"id": "a", "alfa": 0.05, "benchmark": "b", "trial_cumulati": 0}])
    if parentela is not None:
        f["parentela"] = parentela
    return f


def test_famiglia_aperta_sulla_grandezza_di_una_chiusa_senza_parentela_fallisce():
    """§7a (Matteo, 21/11): il binario strumenti non e' una porta laterale per una famiglia chiusa."""
    dati = _dati([_fam("tsmom", ["tendenza"]), _nuova(["tendenza"])])
    assert any("senza parentela dichiarata" in p and "tsmom" in p for p in verifica(dati, registro={}))


def test_parentela_dichiarata_con_fonte_passa():
    par = [{"famiglia": "tsmom", "tipo": "riapertura", "fonte": "DECISIONS 2099-01-01"}]
    dati = _dati([_fam("tsmom", ["tendenza"]), _nuova(["tendenza"], parentela=par)])
    assert verifica(dati, registro={}) == []


def test_parentela_senza_fonte_o_con_tipo_ignoto_fallisce():
    par = [{"famiglia": "tsmom", "tipo": "cugina"}]
    probl = verifica(_dati([_fam("tsmom", ["tendenza"]), _nuova(["tendenza"], parentela=par)]), registro={})
    assert any("senza fonte" in p for p in probl) and any("tipo 'cugina'" in p for p in probl)


def test_segnale_esterno_non_e_una_grandezza_condivisa_ed_e_vietato_agli_strumenti():
    dati = _dati([_fam("mentore", ["segnale_esterno"]), _fam("gump", ["segnale_esterno"])])
    assert grandezze_condivise(dati) == {} and verifica(dati, registro={}) == []
    assert any("riservata ai segnali copiati" in p
               for p in verifica(_dati([_nuova(["segnale_esterno"])]), registro={}))


def test_il_contatore_vero_volatilita_dichiara_la_parentela_con_trend_momentum():
    f = next(f for f in load()["famiglie"] if f["id"] == "volatilita")
    assert {p["famiglia"] for p in f["parentela"]} == {"trend_momentum"}


def test_livelli_ha_misurato_anche_il_volume():
    """La v2 della ricerca livelli ha testato POC/VAH/VAL, VWAP e VWAP ancorato (LEVEL_RESEARCH_PREREGISTRATION,
    addendum v2; modulo 10 §2 riga 4): senza `volume` la tabella direbbe che nessuna famiglia l'ha misurato (B1 della
    revisione del 21/11, prima di I4)."""
    f = next(f for f in load()["famiglie"] if f["id"] == "livelli")
    assert "volume" in f["grandezze"]
