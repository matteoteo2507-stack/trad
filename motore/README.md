# motore — cio' che serve per lavorare

Seconda macro del repo in ordine di processo (DECISIONS 2026-11-09): il codice condiviso, i test, la configurazione, i
dati e il metodo. Migrata il 10/11. Gli studi che usano il motore stanno in `magazzino/registro/codice/`, cio' che gira
con soldi veri o in demo in `esercizio/`.

| Cartella | Cosa contiene |
|---|---|
| [`core/`](core/) | le primitive di misura e i gate: `quant_metrics`, `random_baseline`, `data_checks`, `resolve_trade`, `verifiche`, `sizing`, il contatore dei trial (`trial_ledger`), il risk gate (`risk_gate`), il ponte verso prop-lab (`prop_sim`), `regime`, `strategia_base` (il `Signal` e la classe base delle strategie, era `strategies/_base.py`). Test in `core/tests/` |
| `brokers/`, `notifiers/` | accesso ai broker (MT5, yfinance, IBKR, Binance, Coinbase) e notifiche Telegram |
| [`tests/`](tests/README.md) | i test del resto del repo, anche quelli del codice dormiente: se quel codice smette di funzionare, si vede qui |
| [`config/`](config/README.md) | `risk.yaml` (tetti di rischio letti dal risk gate), `markets.yaml` |
| [`data/`](data/README.md) | gli script che scaricano i dati e la cache (fuori da git); **i dati di prezzo in `data/prezzi/`** (barre e tick, ~1 GB, fuori da git: licenze personali, DECISIONS 2026-11-05) |
| [`prop-lab/`](prop-lab/README.md) | il simulatore di challenge prop progettato coi soci (DECISIONS 2026-10-06). Ha cartelle sue (`config/`, `data/`, `tests/`) e legge il contatore da `../../decisioni/trial_ledger.json` |
| [`metodo/`](metodo/) | [STRATEGY_LIFECYCLE](metodo/STRATEGY_LIFECYCLE.md) (il loop e i criteri di bocciatura) e [QUANT_REVIEW_PROTOCOL](metodo/QUANT_REVIEW_PROTOCOL.md) (come si misura) |
| [`CONVENTIONS.md`](CONVENTIONS.md) | convenzioni del codice |
| `riordino/` | `sposta.py`, lo strumento con cui si e' fatta la migrazione: sposta file e riscrive link, menzioni e import |

## Comandi

```bash
python -m motore.core.trial_ledger            # famiglie, trial e budget; --check esce 1 se qualcosa non torna
python -m pytest motore/tests motore/core/tests
cd motore/prop-lab && python -m pytest tests
```

## Regole del codice

- **La radice di trad si cerca, non si conta**: `next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())`.
  Un percorso dalla radice si scrive come stringa unica (`"motore/data/prezzi"`), cosi' `riordino/sposta.py` lo
  riscrive se la cartella si sposta.
- **Gli import partono dalla radice**: `from motore.core import quant_metrics`, `from magazzino.registro.codice.nxt
  import ...`. Si lancia dalla radice di trad (`python -m ...` o `python <percorso>.py`).
