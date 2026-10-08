"""Cancello verso il contatore dei tentativi di trad (aggiunta trad, 08/10/2026).

Perche' esiste: prima di questo modulo `prop-lab` registrava i suoi tentativi solo in `results/registry.sqlite`, che
il contatore ufficiale di trad (`docs/trial_ledger.json`, letto da `core/trial_ledger.py`) non vedeva. Un giro su
dati reali spendeva 204 tentativi e apriva il fuori campione senza che nessun controllo se ne accorgesse, e niente
impediva di riaprirlo. Qui:

- `tag_avvio` decide se un run puo' partire e con quale etichetta finiscono i suoi tentativi nel registro:
  `sintetico` (dati DEMO_*), `controllo` (famiglie di controllo), oppure l'id della famiglia nel contatore;
- `verifica_apertura` rifiuta una seconda apertura del fuori campione della stessa famiglia;
- `core.trial_ledger --check` (lato trad) confronta il registro con il contatore e segnala ogni differenza.

Il registro resta il diario degli eventi, il contatore resta la fonte dei numeri: nessuna copia.
Configurazione: `config/gate.yaml`.
"""
from __future__ import annotations

import json
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG_SINTETICO = "sintetico"
TAG_CONTROLLO = "controllo"
TAG_FUORI = "fuori_gate"      # cancello spento (repo del socio): eventi registrati ma non contano per trad


class GateError(RuntimeError):
    """Il run non puo' partire, o il fuori campione non puo' essere aperto."""


def config() -> dict:
    p = os.path.join(ROOT, "config", "gate.yaml")
    if not os.path.exists(p):
        return {"attivo": False}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"attivo": False}


def is_sintetico(data_path: str) -> bool:
    return os.path.basename(data_path).upper().startswith("DEMO_")


def is_controllo(family: str) -> bool:
    from .strategies.base import get_family
    strats = get_family(family)
    return bool(strats) and all(getattr(c, "controllo", False) for c in strats.values())


def frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        testo = f.read()
    if not testo.startswith("---"):
        return {}
    fine = testo.find("\n---", 3)
    return (yaml.safe_load(testo[3:fine]) or {}) if fine > 0 else {}


def _ledger(cfg: dict) -> tuple[dict, str]:
    p = os.path.normpath(os.path.join(ROOT, cfg["ledger"]))
    if not os.path.exists(p):
        raise GateError(f"contatore non trovato in {p}. In un repo senza trad: `attivo: false` in config/gate.yaml")
    with open(p, encoding="utf-8") as f:
        return json.load(f), os.path.dirname(os.path.dirname(p))   # (dati, radice di trad)


def famiglia_ledger(ledger_id: str, cfg: dict | None = None) -> dict:
    cfg = cfg or config()
    dati, _ = _ledger(cfg)
    for f in dati["famiglie"]:
        if f["id"] == ledger_id:
            return f
    raise GateError(f"la famiglia '{ledger_id}' non esiste nel contatore {cfg['ledger']}: va aggiunta prima del test")


def tag_avvio(family: str, data_path: str, ledger_id: str | None, cfg: dict | None = None) -> str:
    """Etichetta dei tentativi del run, oppure GateError se su dati reali mancano contatore o pre-registrazione."""
    cfg = cfg or config()
    if is_sintetico(data_path):
        return TAG_SINTETICO
    if is_controllo(family):
        return TAG_CONTROLLO
    if not cfg.get("attivo"):
        return TAG_FUORI
    if not ledger_id:
        raise GateError(f"dati reali ({os.path.basename(data_path)}): serve --famiglia <id del contatore>. "
                        f"Un test vero si pre-registra prima (STRATEGY_LIFECYCLE §1, gate G1)")
    fam = famiglia_ledger(ledger_id, cfg)
    if fam.get("stato") in cfg.get("stati_chiusi", []):
        raise GateError(f"la famiglia '{ledger_id}' e' {fam['stato']}: non si riapre con un nuovo giro (§7)")
    if not fam.get("registro_prop_lab"):
        raise GateError(f"la famiglia '{ledger_id}' non ha `registro_prop_lab: true` nel contatore: i suoi tentativi "
                        f"non verrebbero contati")
    pre = fam.get("preregistrazione")
    if not pre:
        raise GateError(f"la famiglia '{ledger_id}' non ha il campo `preregistrazione` nel contatore")
    _, radice = _ledger(cfg)
    pre_path = os.path.join(radice, pre)
    if not os.path.exists(pre_path):
        raise GateError(f"pre-registrazione non trovata: {pre}")
    stato = str(frontmatter(pre_path).get("stato", "")).upper()
    richiesto = cfg.get("stato_preregistrazione_richiesto", "APPROVATA")
    if stato != richiesto:
        raise GateError(f"pre-registrazione {pre} in stato '{stato or 'assente'}': serve '{richiesto}'")
    return ledger_id


def verifica_apertura(tag: str, con, cfg: dict | None = None) -> None:
    """Il fuori campione di una famiglia del contatore si apre UNA volta (STRATEGY_LIFECYCLE §2)."""
    if tag in (TAG_SINTETICO, TAG_CONTROLLO, TAG_FUORI):
        return
    cfg = cfg or config()
    fam = famiglia_ledger(tag, cfg)
    if fam.get("holdout_aperto"):
        raise GateError(f"il fuori campione di '{tag}' risulta gia' aperto nel contatore ({fam['holdout_aperto']})")
    prima = con.execute("SELECT run_id, ts FROM aperture WHERE ledger_id=?", (tag,)).fetchone()
    if prima:
        raise GateError(f"il fuori campione di '{tag}' e' gia' stato aperto dal run {prima[0]}")
