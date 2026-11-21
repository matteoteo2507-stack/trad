"""Binario `strumenti` del contatore (DECISIONS 2026-11-10 e 2026-11-11, STRATEGY_LIFECYCLE §8ter).

Una famiglia di strumenti non consuma quote trimestrali, divide il suo errore fra le sottofamiglie prima di ogni test
e conta anche le varianti esplorative. Nessun dato vero: registri sintetici.
"""
import itertools

from motore.core.trial_ledger import verifica, tabella

# Una grandezza diversa per ogni famiglia sintetica: questi test misurano le quote, non la parentela
# (le famiglie sintetiche non sono fra le esenti del 21/11).
_GR = itertools.cycle(("tendenza", "spostamento_media", "volume", "livelli", "candela", "tempo",
                       "dipendenza_rendimenti"))

BUDGET = {"round_rifinitura_per_famiglia": 3, "prereg_esterne_per_trimestre": 3,
          "prereg_esterne_per_trimestre_soglia_allarme": 2, "prereg_hub_per_trimestre": 1,
          "holdout_aperture_per_famiglia": 1, "llm_knowledge_cutoff": "2026-05-31"}


def _vol(**kw):
    f = {"id": "volatilita", "stato": "BOZZA", "binario": "strumenti", "fonti": ["x"], "round_rifinitura": 0, "grandezze": ["volatilita"],
         "alfa_famiglia": 0.05, "trial_cumulati": 0, "holdout_aperto": None, "holdout_inizio": "2024-11-01",
         "prereg_esterna_trimestre": "2026-Q4", "provenienza_ipotesi": "letteratura",
         "finestra_dati_fine": "2026-11-09",
         "sottofamiglie": [{"id": "garch", "alfa": 0.025, "benchmark": "EWMA 0,94", "trial_cumulati": 0},
                           {"id": "hmm", "alfa": 0.0125, "benchmark": "GJR", "trial_cumulati": 0},
                           {"id": "vrp", "alfa": 0.0125, "benchmark": "VIX2 = RV", "trial_cumulati": 0}]}
    f.update(kw)
    return f


def _dati(famiglie):
    return {"budget": BUDGET, "trimestre_corrente": "2026-Q4", "aggiornato": "2026-11-11", "famiglie": famiglie}


def _strat(fid):
    return {"id": fid, "stato": "CLOSED", "motivo_chiusura": "potenza", "round_rifinitura": 0, "fonti": ["x"], "grandezze": [next(_GR)],
            "prereg_esterna_trimestre": "2026-Q4", "provenienza_ipotesi": "umana_esterna",
            "finestra_dati_fine": "2026-10-01"}


def test_famiglia_valida_senza_problemi():
    assert verifica(_dati([_vol()]), registro={}) == []


def test_strumenti_non_consumano_la_quota_delle_strategie():
    """Quota strategie gia' piena (3 di 3): una famiglia di strumenti nello stesso trimestre non la sfora."""
    fam = [_strat("s1"), _strat("s2"), _strat("s3"), _vol()]
    assert verifica(_dati(fam), registro={}) == []


def test_quote_oltre_l_errore_di_famiglia():
    f = _vol()
    f["sottofamiglie"][0]["alfa"] = 0.04
    assert any("quote delle sottofamiglie" in p for p in verifica(_dati([f]), registro={}))


def test_sottofamiglia_senza_benchmark():
    f = _vol()
    del f["sottofamiglie"][1]["benchmark"]
    assert any("senza benchmark" in p for p in verifica(_dati([f]), registro={}))


def test_esplorative_contano_nei_trial_della_famiglia():
    f = _vol(trial_cumulati=3)
    f["sottofamiglie"][0].update(trial_cumulati=2, varianti_esplorative=1)
    assert verifica(_dati([f]), registro={}) == []
    f["trial_cumulati"] = 2                       # dimenticare l'esplorativa e' un errore
    assert any("sommano 3" in p for p in verifica(_dati([f]), registro={}))


def test_holdout_aperto_senza_data_dichiarata():
    f = _vol(holdout_aperto="2026-12-01", holdout_inizio=None)
    assert any("holdout_inizio" in p for p in verifica(_dati([f]), registro={}))


def test_alfa_famiglia_mancante():
    f = _vol()
    del f["alfa_famiglia"]
    assert any("alfa_famiglia" in p for p in verifica(_dati([f]), registro={}))


def test_tabella_mostra_le_sottofamiglie():
    t = tabella(_dati([_vol()]))
    assert "garch" in t and "nessuna quota trimestrale" in t
