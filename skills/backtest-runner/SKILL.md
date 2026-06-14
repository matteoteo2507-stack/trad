---
name: backtest-runner
description: Testare una strategia su uno o più backtester e produrre un report comparativo normalizzato. Usare quando l'utente vuole validare una strategia, confrontare risultati su backtester diversi, o ottenere metriche di performance standard.
---

# Skill — Backtest Runner

Esegue una strategia su uno o più backtester (vectorbt, backtrader, backtester di `ai-hedge-fund`,
custom) e produce un report **normalizzato** per confronto.

## Filosofia

**A cosa serve (e a cosa NON serve) un backtest.** Il backtest serve a **falsificare** una
strategia e a misurarne le proprietà **distributive/strutturali** (varianza, code, drawdown,
correlazione con altri stream). **Non** serve a *scoprire* una regola di timing ottimizzando
parametri sui dati passati: quella è la via maestra dell'overfitting. Prima viene il **meccanismo**
("qual è il gioco?" — microstruttura, comportamento istituzionale, premio di rischio), poi il
backtest lo corrobora o lo falsifica. Una strategia il cui unico argomento è "i numeri storici sono
buoni" è un *giocatore fortunato*, non un edge. (Stessa epistemica del
[Quant Reviewer](../../agents/quant_reviewer.md) §0 e di
[05_portfolio_rischio](../../fondamenti_tecnici/05_portfolio_rischio/principles.md).)

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
| `arithmetic_mean_R` | Media aritmetica dei rendimenti per periodo/trade ($\bar R$, ≈ "EV") |
| `geometric_growth` | Crescita geometrica $R_G \approx \bar R - \sigma^2/2$ — **ciò che compounda davvero il conto** |
| `volatility_drag` | $\sigma^2/2$: quanto la varianza erode il geometrico vs l'aritmetico |
| `sharpe` | Sharpe ratio |
| `sortino` | Sortino ratio |
| `max_drawdown` | Drawdown massimo % |
| `win_rate` | % trade in profitto |
| `profit_factor` | Profitti totali / perdite totali |
| `n_trades` | Numero totale di trade |
| `n_eff` | $N$ effettivo **indipendente** (dopo block-bootstrap; può essere ≪ `n_trades` se clusterati) |
| `avg_trade` | P&L medio per trade |
| `max_consecutive_losses` | Massimo numero di trade in perdita consecutivi |

**Reporting geometric-aware (obbligatorio).** Non riportare solo media/`win_rate`/`avg_trade`: una
strategia con EV positivo ma alta varianza può avere `geometric_growth` ≈ 0 e **non far crescere il
conto**. Riporta sempre `geometric_growth` e `volatility_drag` accanto alle metriche aritmetiche.
Se una variante alza lo Sharpe ma peggiora `geometric_growth` o `max_drawdown`, **non è un
miglioramento** per chi compounda (Sharpe-ottimo ≠ growth-ottimo).

**Trade non indipendenti.** CI ed `n_eff` vanno calcolati con **block-bootstrap**, non assumendo
trade iid: trade nella stessa sessione/regime sono correlati e gonfiano la confidenza apparente.
Riporta `n_eff` insieme a `n_trades`.

**Correlazione al book esistente.** Una strategia non si valuta solo standalone: riporta la sua
correlazione / $R^2$ (regressione CAPM cross-stream) verso gli stream già attivi (segnali mentori,
Level Analyzer, investing). $R^2 \approx 0$ = stream **ortogonale**, prezioso anche con Sharpe
modesto perché abbassa il drawdown del combinato (→ meno volatility drag → più crescita geometrica).
Misura su dati **forward reali** dove disponibili, non sul backtest curve-fit.

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
- **Conta i gradi di libertà** (parametri tunabili) e dichiarali nel report: tanti parametri su
  pochi trade = overfitting probabile → richiedi al [Quant Reviewer](../../agents/quant_reviewer.md)
  DSR/PBO prima di qualsiasi conclusione GO.
- **Lead with the mechanism**: il report deve aprire con *perché* la strategia dovrebbe funzionare
  (il "gioco"), non con la equity curve. Una equity curve bella senza meccanismo = NO-GO di default.
- **Mai concludere "edge" su `geometric_growth`/CI calcolati come iid** se i trade sono clusterati:
  usa block-bootstrap e riporta `n_eff`.

## Riferimenti

- `backtesters/base.py` — interfaccia astratta.
- `backtesters/vectorbt_runner.py`, `backtesters/backtrader_runner.py`, `backtesters/custom.py` — implementazioni (Stage 3).
- Stage 3 della roadmap.
