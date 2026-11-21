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


def test_il_contatore_vero_dichiara_le_grandezze_di_ogni_famiglia():
    dati = load()
    assert all(f.get("grandezze") for f in dati["famiglie"])
    assert not [p for p in verifica(dati, registro={}) if "grandezz" in p]
