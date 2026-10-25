"""Quote di pre-registrazione separate (strategie / hub) ed etichetta di provenienza `utente_llm`.

Decisioni di Matteo del 2026-10-25 (DECISIONS 2026-10-25 (8)): l'hub ha un budget suo di 1 slot a
trimestre, che non tocca quello delle strategie; un'idea scritta con l'LLM su dati prima del cutoff non
e' una predizione indipendente. Nessun dato vero: registri sintetici.
"""
from core.trial_ledger import verifica, _contaminazione

BUDGET = {"round_rifinitura_per_famiglia": 3, "prereg_esterne_per_trimestre": 3,
          "prereg_esterne_per_trimestre_soglia_allarme": 2, "prereg_hub_per_trimestre": 1,
          "holdout_aperture_per_famiglia": 1, "llm_knowledge_cutoff": "2026-05-31"}


def _fam(fid, binario=None, q="2026-Q4"):
    f = {"id": fid, "stato": "CLOSED", "round_rifinitura": 0, "fonti": ["x"],
         "prereg_esterna_trimestre": q, "provenienza_ipotesi": "umana_esterna",
         "finestra_dati_fine": "2026-10-01"}
    if binario:
        f["binario"] = binario
    return f


def _dati(famiglie):
    return {"budget": BUDGET, "trimestre_corrente": "2026-Q4", "famiglie": famiglie}


def test_hub_non_consuma_la_quota_delle_strategie():
    fam = [_fam("s1"), _fam("s2"), _fam("s3"), _fam("h1", "hub")]
    assert verifica(_dati(fam), registro={}) == []


def test_quota_hub_sforata():
    fam = [_fam("h1", "hub"), _fam("h2", "hub")]
    assert any("dall'hub" in p and "SFORATO" in p for p in verifica(_dati(fam), registro={}))


def test_quota_strategie_sforata_anche_con_hub_vuoto():
    fam = [_fam("s%d" % i) for i in range(4)]
    assert any("prereg esterne" in p for p in verifica(_dati(fam), registro={}))


def test_binario_sconosciuto():
    assert any("binario" in p for p in verifica(_dati([_fam("x", "geopolitica")]), registro={}))


def test_utente_llm_prima_del_cutoff_non_e_indipendente():
    f = {"id": "u", "provenienza_ipotesi": "utente_llm", "finestra_dati_fine": "2026-03-01"}
    assert _contaminazione(f, "u", "2026-05-31")


def test_utente_llm_in_avanti_e_valida():
    f = {"id": "u", "provenienza_ipotesi": "utente_llm", "finestra_dati_fine": "2026-12-01"}
    assert _contaminazione(f, "u", "2026-05-31") == []
