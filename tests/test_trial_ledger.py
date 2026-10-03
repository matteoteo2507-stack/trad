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
