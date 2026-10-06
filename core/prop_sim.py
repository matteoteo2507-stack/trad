"""Ponte unico verso il simulatore di challenge prop di `prop-lab` (DECISIONS 2026-10-06).

La logica delle challenge (fasi, perdita giornaliera, max loss statico o trailing, consistency, giorni
minimi, fase funded con payout, profili di rischio) ha **un solo proprietario**: `prop-lab/lab/prop.py` e
`prop-lab/lab/risk.py`, condivisi col repo del socio VELTRIX e tenuti allineati come se fossero un repo solo.
`trad` non ne tiene una copia: li importa da qui. Questo e' l'**unico** punto del repo che tocca `sys.path`
per farlo, e aggiunge `prop-lab` **in coda**, cosi' non puo' oscurare moduli di `trad` con lo stesso nome.

Cosa si usa, e la regola che vale per ognuno:

| funzione | cosa da' | regola |
|---|---|---|
| `evaluate` | pass rate, cause di fallimento, EV per tentativo (stima "plug-in" su un campione) | mai citata da sola |
| `zero_edge` | gli stessi trade con attesa zero | il benchmark di ogni EV |
| `evaluate_ci` | pass rate ed EV con l'incertezza di stima, e `ev_vs_zero` (la parte dovuta al vantaggio) | la forma da citare |
| `RiskModel`, `build_profiles` | i modificatori di rischio | la libreria dichiarata sta in `core/sizing.py` |

Perche' il benchmark e' obbligatorio: il 05/10 una strategia a vantaggio **zero** passava ~30% delle challenge
con EV ~+1.900 per tentativo (profilo guardia giornaliera al 3%). La challenge e' un'opzione: un EV positivo
non e' prova di vantaggio. Vedi anche `docs/PROP_FIRM_CRITERIA.md` §1.9.

Le regole in `prop-lab/config/prop_rules.yaml` sono **modelli parametrici**, non i regolamenti delle firm:
prima di un numero operativo vanno allineate al regolamento primario (PROP_FIRM_CRITERIA §3).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROP_LAB = Path(__file__).resolve().parents[1] / "prop-lab"
if not (PROP_LAB / "lab" / "prop.py").exists():
    raise ImportError(f"prop-lab non trovato in {PROP_LAB}: il simulatore prop vive li'")
if str(PROP_LAB) not in sys.path:
    sys.path.append(str(PROP_LAB))

from lab.prop import (  # noqa: E402
    evaluate, evaluate_ci, make_paths, simulate_path, trades_by_day, zero_edge,
)
from lab.risk import AccountState, RiskModel, build_profiles  # noqa: E402

__all__ = ["PROP_LAB", "AccountState", "RiskModel", "build_profiles", "evaluate", "evaluate_ci",
           "make_paths", "simulate_path", "trades_by_day", "zero_edge"]
