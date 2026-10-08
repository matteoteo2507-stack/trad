"""Regola del contatore: un LEAD con l'holdout aperto passa solo con gate_finale = "forward" (02/10)."""
from core.trial_ledger import verifica


def _dati(**fam):
    f = {"id": "x", "stato": "LEAD", "fonti": ["DECISIONS.md"], "provenienza_ipotesi": "utente"}
    f.update(fam)
    return {"budget": {"round_rifinitura_per_famiglia": 3, "prereg_esterne_per_trimestre": 3},
            "trimestre_corrente": "2026-Q4", "famiglie": [f]}


def test_lead_con_holdout_aperto_senza_gate_finale_e_errore():
    assert any("LEAD con holdout" in p for p in verifica(_dati(holdout_aperto="2026-10-02")))


def test_lead_con_holdout_aperto_e_gate_forward_passa():
    assert verifica(_dati(holdout_aperto="2026-10-02", gate_finale="forward")) == []


def test_gate_finale_sconosciuto_e_errore():
    assert any("gate_finale" in p for p in verifica(_dati(gate_finale="speranza")))


# ---- collegamento col registro di prop-lab (08/10/2026) ----------------------------------------
def _fam_prop(**kw):
    d = _dati()
    base = dict(registro_prop_lab=True, trial_cumulati=36, holdout_aperto=None, stato="IN TEST")
    base.update(kw)
    d["famiglie"][0].update(base)
    return d


def test_registro_prop_lab_coerente_nessun_problema():
    reg = {"x": {"trial": 36, "aperture": []}, "controllo": {"trial": 36, "aperture": [("r1", 0.0)]}}
    assert verifica(_fam_prop(id="x"), registro=reg) == []


def test_trial_diversi_dal_registro_sono_un_problema():
    reg = {"x": {"trial": 72, "aperture": []}}
    assert any("trial_cumulati 36" in p for p in verifica(_fam_prop(id="x"), registro=reg))


def test_holdout_aperto_in_prop_lab_ma_non_nel_contatore():
    reg = {"x": {"trial": 36, "aperture": [("run_1", 0.0)]}}
    assert any("holdout_aperto vuoto" in p for p in verifica(_fam_prop(id="x"), registro=reg))
    assert verifica(_fam_prop(id="x", holdout_aperto="2026-10-08"), registro=reg) == []


def test_famiglia_sconosciuta_nel_registro():
    reg = {"fantasma": {"trial": 10, "aperture": []}}
    assert any("fantasma" in p for p in verifica(_dati(), registro=reg))
