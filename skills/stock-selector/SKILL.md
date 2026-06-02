---
name: stock-selector
description: Eseguire o modificare la selezione azionaria SP500 basata sul sistema V6.0. Usare quando l'utente chiede top picks SP500, screening fondamentale, valutazione scenario macro, o vuole rigenerare i due file Excel "Top_Picks" e "Analisi_Completa".
---

# Skill — Stock Selector

Questa skill agentizza il sistema di selezione azionaria V6.0 (file originale:
`algoritmo selezione azioni.ipynb` al top level del workspace).

## Cosa fa il sistema V6.0

1. Riceve in input: tasso risk-free USA, trend liquidità banche centrali (Aumento/Diminuzione),
   benchmark di riferimento (default `^GSPC`).
2. Categorizza lo scenario macro in **DEFENSIVE / AGGRESSIVE / NEUTRAL/QUALITY**.
3. Scarica la lista SP500 (fonte: dataset GitHub, fallback hardcoded).
4. Per ogni ticker:
   - calcola il **RRG status** (Relative Rotation Graph) → LEADING/WEAKENING/LAGGING/IMPROVING
     contro il benchmark.
   - calcola lo **score fondamentale 0-6** su P/E, D/E, EPS, EBITDA margin, profit margin, ROE.
   - verifica il **macro match** in base allo scenario.
5. Output:
   - `Top_Picks.xlsx` — score ≥ **4** **e** `TARGET MATCH == "SI"` (filtro coerenza macro).
   - `Analisi_Completa.xlsx` — tutti i titoli analizzati, formattati condizionalmente.
   - `Sell_Signals.xlsx` — ticker che erano top picks nella run **precedente** ma non lo sono più. Generato per diff vs `last_top_picks.json` salvato in `output_dir`. **Assunzione operativa**: l'utente compra tutte le top picks; quando un ticker esce, va venduto.

## Cosa va costruito (Stage 1 della roadmap)

Trasformare il notebook in un modulo Python callable senza `input()`:

```python
from stock_selector import run_selection, SelectionResult

result: SelectionResult = run_selection(
    risk_free_rate=4.2,
    is_liquidity_increasing=False,
    benchmark="^GSPC",
    save_excel=True,
)
```

## Istruzioni per Claude Code

Quando si attiva questa skill:

1. **Leggere il notebook originale** `algoritmo selezione azioni.ipynb` per capire la logica esatta.
   Il notebook è autorevole — la sua logica è già validata da Matteo.
2. **Estrarre la logica in un modulo Python** sotto `strategies/stock_selector/`:
   - `strategy.py` — classe `StockSelector` con metodi pubblici.
   - `data_sources.py` — fetch SP500 list + dati storici via `yfinance`.
   - `scoring.py` — funzioni di calcolo score fondamentale + RRG + macro match.
   - `config.yaml` — parametri (soglie, weight degli score).
3. **Output strutturato**: oltre a salvare gli Excel, restituire un `SelectionResult` Pydantic con
   tipo strutturato (lista di `StockPick` con tutti i campi rilevanti).
4. **CLI**: aggiungere un comando Typer per invocare lo Stock Selector da terminale:
   `python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing`.
5. **Test**: scrivere almeno un test che verifichi la coerenza dello scoring su dati sintetici noti
   (es. una società con D/E=0.3, ROE=0.20 → score >= 4).

## Vincoli

- Non rompere la logica originale: il notebook è la specifica autorevole.
- Yfinance può fallire: gestire i `None` nei `info.get(...)` come già fa il notebook.
- Il modulo deve essere **pure function-style**: input → output, niente side effect oltre il salvataggio file.

## Riferimenti

- Notebook originale: `algoritmo selezione azioni.ipynb` al top level.
- Output di esempio già esistenti: `Top_Picks sp500 30-12-25.ods`, `Analisi_Completa sp500 30-12-25.ods`.
- Stage successivo (Stage 4) → `skills/stock-selector-consensus/` invocherà 4 personas su queste top picks.
