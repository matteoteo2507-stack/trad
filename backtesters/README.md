# backtesters/

Wrapper sui backtester pluralistici. Permettono di testare la stessa strategia su più motori
e produrre un report comparativo normalizzato.

## Filosofia

NON fissare un solo backtester. Più backtester = riduzione del rischio di artefatti del singolo
framework + materiale di backtest più ricco.

## Backtester pianificati (Stage 3)

| Backtester | Tipo | Pro | Contro |
|---|---|---|---|
| `vectorbt` | Vettoriale, NumPy/Pandas | Velocissimo per grid search di parametri | API meno familiare |
| `backtrader` | Event-driven | Standard de facto, molta letteratura | Più lento di vectorbt |
| `ai-hedge-fund` | Custom (LangGraph based) | Coerente con il consensus layer | Solo equities, slow |
| `custom` | Implementazione minimale tutto-in-Python | Controllo totale, debug facile | Da scrivere |

## Pattern

Tutte le implementazioni ereditano da `BacktesterBase` (`base.py`). Il wrapper accetta una
strategia generica (eredita da `StrategyBase`) e un dataset, e produce `BacktestReport`
con metriche standard.

Le strategie restano **broker-agnostic**: il backtester traduce le chiamate `should_enter`/
`should_exit` nel proprio linguaggio interno.

## Output normalizzato

Vedi `skills/backtest-runner/SKILL.md` per la lista delle metriche standard prodotte
da tutti i backtester (total_return, Sharpe, max_drawdown, win_rate, profit_factor, ecc.).
