# tests/

Test automatici. Framework: `pytest` (in `pyproject.toml`).

## Convenzioni

- File con prefisso `test_`. Esempio: `test_stock_selector.py`.
- Una funzione `test_<cosa>` per ogni caso d'uso.
- Test minimo per ogni strategia: caso con dati sintetici dove l'output atteso è noto.
- Test minimo per ogni broker: smoke test della connessione (skippato se le credenziali mancano).

## Esecuzione

```bash
pytest                          # tutti i test
pytest tests/test_stock_selector.py    # solo un file
pytest -k "selector"            # solo test che matchano "selector"
pytest --cov=.                  # con coverage
```

## Test strategici (Stage 1+)

Per ogni strategia, almeno:
- Un caso di entrata pulita (i dati sintetici soddisfano tutte le condizioni).
- Un caso di non-entrata (manca una condizione).
- Un caso di uscita anticipata (se la strategia la prevede).
- Un caso di SL/TP triggered.
