---
name: backtest-runner
description: Testare una strategia su uno o più backtester e produrre un report comparativo normalizzato. Usare quando l'utente vuole validare una strategia, confrontare risultati su backtester diversi, o ottenere metriche di performance standard.
---

# Skill — Backtest Runner

Esegue una strategia su uno o più backtester (vectorbt, backtrader, backtester di `ai-hedge-fund`,
custom) e produce un report **normalizzato** per confronto.

## Filosofia

NON fissare un solo backtester. La diversità di motori riduce il rischio di artefatti del singolo
framework e fornisce materiale di backtest più ricco. Vedi `backtesters/README.md`.

## Workflow

### 1. Identificare la strategia

L'utente indica una strategia per nome (cartella sotto `strategies/`). Validare che esista
`strategy.py` + `config.yaml`.

### 2. Identificare i backtester da usare

Default: tutti quelli disponibili. Ammessa selezione esplicita: `--backtester vectorbt,custom`.

### 3. Identificare il dataset

Parametri standard:
- ticker / strumento;
- timeframe;
- periodo storico (start/end o lookback);
- fonte dati (yfinance per equities, ccxt per crypto, MT5 export per forex).

### 4. Esecuzione

Per ogni backtester selezionato:
- caricare la strategia (adapter pattern: la strategia espone `should_enter`/`should_exit`,
  il wrapper la traduce nel linguaggio del backtester);
- eseguire la simulazione;
- estrarre le metriche standard (vedi sotto).

### 5. Report

Output Markdown + CSV con metriche normalizzate per backtester:

| Metrica | Descrizione |
|---|---|
| `total_return` | Rendimento totale % |
| `cagr` | Tasso di crescita annualizzato |
| `sharpe` | Sharpe ratio |
| `sortino` | Sortino ratio |
| `max_drawdown` | Drawdown massimo % |
| `win_rate` | % trade in profitto |
| `profit_factor` | Profitti totali / perdite totali |
| `n_trades` | Numero totale di trade |
| `avg_trade` | P&L medio per trade |
| `max_consecutive_losses` | Massimo numero di trade in perdita consecutivi |

Se i backtester divergono significativamente su una metrica (es. Sharpe 1.2 vs 0.4 sulla stessa
strategia/dati), **segnalare la divergenza** e ipotizzare la causa (gestione fee, slippage,
ordine di esecuzione tick-vs-bar, ecc.).

### 6. Output finale

- File Markdown in `output/backtest_<strategia>_<timestamp>.md`.
- File CSV in `output/backtest_<strategia>_<timestamp>.csv`.
- Aggiornamento del registro `output/backtest_history.csv` con una riga per ogni run.
- (Opzionale) sintesi in chat per Matteo: "La strategia X ha Sharpe 1.4 su vectorbt, 1.1 su custom.
  Drawdown 12%. 47 trade. Sembra promettente per MT5 demo."

## Vincoli

- Le commissioni devono essere realistiche per il broker target (MT5 demo broker reale, IBKR retail,
  Coinbase fee tier 0).
- Lo slippage va modellato (default: 1-2 pip su forex, 0.05% su crypto).
- Il backtest deve essere **walk-forward o out-of-sample** quando possibile, per evitare overfitting.

## Riferimenti

- `backtesters/base.py` — interfaccia astratta.
- `backtesters/vectorbt_runner.py`, `backtesters/backtrader_runner.py`, `backtesters/custom.py` — implementazioni (Stage 3).
- Stage 3 della roadmap.
