# Stock Selector V6.0 (headless)

> **Sistema:** investing (dinamico — **non etichettato per regime**: oggi semiauto, automatizzabile) · **Stato:** active · **Habitat:** PC
> **Quant review:** — · **Fondamenti:** [stock selection](../../fondamenti_tecnici/06_stock_selection/), [portfolio/rischio](../../fondamenti_tecnici/05_portfolio_rischio/), [data sources](../../fondamenti_tecnici/07_data_sources/)
> Indice: [strategies/README.md](../README.md) · Decisioni: [DECISIONS.md](../../DECISIONS.md) · Parallelo a PAC + worldmonitor (pilastro investing conclusivo)

Versione modulare e callable del notebook `algoritmo selezione azioni.ipynb`.
Replica fedelmente la logica V6.0: scenario macro → scoring fondamentale (0-6) +
quadrante RRG vs benchmark + filtro di scenario.

## Uso programmatico

```python
from strategies.stock_selector import run_selection

result = run_selection(
    risk_free_rate=4.2,
    is_liquidity_increasing=False,
    benchmark="^GSPC",
    save_excel=True,
    output_dir="output/",
)

print(result.scenario)         # MacroScenario.DEFENSIVE
print(len(result.top_picks))   # numero titoli con score ≥ 5
for p in result.top_picks[:5]:
    print(p.ticker, p.score, p.rrg.value, p.target_match)
```

## Uso CLI

```bash
python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing
python -m strategies.stock_selector -r 3.5 -l increasing -b "^NDX" --no-excel
python -m strategies.stock_selector -r 4.2 -l decreasing --tickers AAPL,MSFT,JNJ
```

## Struttura

| File | Ruolo |
|---|---|
| `strategy.py` | Orchestratore `StockSelector` + funzione pubblica `run_selection`. |
| `scoring.py` | Modelli Pydantic + funzioni di scoring/RRG/scenario, pure. |
| `data_sources.py` | Wrapper su `requests` (lista SP500) e `yfinance` (storici/info). |
| `config.yaml` | Tutte le soglie e i parametri. Nessun valore magico nel codice. |
| `__main__.py` | CLI Typer. |

## Output

- `Top_Picks.xlsx` — titoli con **score ≥ 4 e TARGET MATCH == "SI"**, formattazione condizionale (RRG + Macro Match). Soglia e filtro controllati da `top_picks_min_score` e `top_picks_require_macro_match` in `config.yaml`.
- `Analisi_Completa.xlsx` — tutti i titoli analizzati ordinati per score.
- `Sell_Signals.xlsx` — ticker presenti nelle top picks della run **precedente** ma non più in quella corrente. Generato solo se esiste lo stato precedente e ci sono effettive uscite.
- `last_top_picks.json` — stato persistente: lista ticker dell'ultima run, usata per il diff sell. Vive in `output_dir` insieme agli Excel. **Non cancellare** tra una run e l'altra.
- `SelectionResult` Pydantic — disponibile sempre, anche con `save_excel=False`.

### Workflow operativo implicito

Il modulo assume che l'utente compri **tutte le top picks** di ogni run. La "vendita" è triggerata quando un ticker esce dalle top picks correnti (per qualsiasi motivo: score sceso, scenario macro cambiato, RRG, ecc.). Il motivo della sell è esplicitato nella colonna `Motivo Sell` dell'Excel.

> Per supportare un portafoglio non coincidente con le top picks (es. comprare solo un sottoinsieme), servirà un `portfolio.yaml` separato — non implementato.

## Vincoli rispettati

- La logica è la stessa del notebook V6.0 (autorevole). Soglie e formule replicate 1:1.
- Nessun `input()` interattivo — invocazione totalmente headless.
- Pure function-style: l'unico side effect è il salvataggio degli Excel (opzionale).
- Robustezza ai `None` di yfinance come nel notebook originale.

## Test

`tests/test_stock_selector_scoring.py` verifica lo scoring su dati sintetici noti.

## Stage successivi

- Stage 4 → `skills/stock-selector-consensus` invocherà 4 personas (Damodaran, Buffett,
  Burry, Taleb) sulle top picks restituite da questo modulo.
