---
titolo: Metodologia Quant & Bias del Backtest
fonti:
  - "_sorgenti/Quant backtest notes.txt"
tipo: concetti
---

# Metodologia Quant & Bias del Backtest

> Un backtest bello non prova nulla: è una "scena del crimine" da interrogare, non un trofeo. Un'equity curve in salita con Sharpe 1.5-1.7 fallisce live se le fondamenta statistiche sono marce. I tre bias che distruggono una strategia sono **look-ahead**, **overfitting / data snooping** e **survivorship**; i costi di transazione vengono dopo. Questo file è **la teoria dietro la nostra quant-review** — i rimedi qui descritti sono già implementati in [`core/quant_metrics.py`](../../core/quant_metrics.py) e operativi nel protocollo [`QUANT_REVIEW_PROTOCOL.md`](../../docs/QUANT_REVIEW_PROTOCOL.md).

## Concetti

### 1. Look-ahead bias

**Definizione**: incorporare nella decisione di trading informazione che **non era disponibile** al momento in cui il trade è stato aperto.

Analogia delle due buste:
- **Envelope 1** — informazione accessibile *al o prima* del momento della decisione (filtration legittima).
- **Envelope 2** — informazione disponibile *solo dopo* il punto di decisione.

Usare dati dell'Envelope 2 per decidere significa "sbirciare nel futuro": gonfia artificialmente la performance. Nell'esempio della fonte, una strategia long-short market-neutral su basket di equity (segnale ranked per quantili) mostrava uno Sharpe iniziale ~3 con relazione monotona tra bucket di segnale e forward return. **Corretto il look-ahead, lo Sharpe crolla** da ~3 a un valore molto più basso.

Insidia chiave: il look-ahead non produce sempre un backtest "troppo perfetto". A volte lascia un segnale **modestamente promettente ma falso** (Sharpe 0.9-1.2), che inganna anche quant esperti. Forme tipiche:
- usare informazione di una settimana avanti per decidere oggi;
- normalizzare il segnale con i **forward return**;
- disallineamento dei timestamp / errori di timing su quando il dato arriva davvero.

**Rimedio**: ogni modello, parametro e dataset deve essere strettamente adattato alla **filtration** dei dati disponibili al momento della decisione — nessun dato futuro deve filtrare nel segnale. Nel repo il rischio è formalizzato dal **purging + embargo** della CPCV ([`cpcv_splits`](../../core/quant_metrics.py)) e dal caveat operativo sulla regime timeline (`data/regime_timeline_gbpusd.csv`): la label calcolata sul close del giorno stesso è look-ahead e va usata **solo con lag di 1 giorno** per strategie intraday.

### 2. Overfitting / data snooping / p-hacking

**Definizione**: testare ripetutamente molte combinazioni di parametri o modelli sugli **stessi dati storici** e scegliere quella che appare migliore per puro rumore statistico, senza contenuto predittivo reale e senza out-of-sample.

Esempio della fonte (MA crossover): le coppie (3,5) o (7,12). La (7,12) ha lo Sharpe IS più alto e tenta il trader a portarla live. Ma se sono state provate **molte** coppie, scegliere la "migliore" è overfitting della parametrizzazione al passato. **Out-of-sample la (7,12) performa male, Sharpe ~ -1.8.**

Red flag di overfitting: **instabilità parametrica** — se un piccolo cambio (es. da (7,12) a (8,12)) fa crollare la performance, il modello è probabilmente overfit e instabile. Una strategia robusta resta stabile su variazioni ragionevoli dei parametri.

| Problema | Descrizione | Mitigazione |
|---|---|---|
| Overfitting parametri | Set che fittano lo storico ma generalizzano male | Walk-forward validation |
| Selection bias (molti modelli) | Provare molti modelli e scegliere il migliore per caso | Criteri di selezione rigorosi |
| Instabilità parametrica | Piccoli cambi → grandi cali di performance | Preferire modelli stabili/robusti |
| Mancanza di razionale economico | Modelli senza giustificazione di mercato | Statistica + domain knowledge |

**Rimedi nel repo** (tutti in [`core/quant_metrics.py`](../../core/quant_metrics.py)): il numero di trial provati va penalizzato col **Deflated Sharpe Ratio** ([`deflated_sharpe_ratio`](../../core/quant_metrics.py)); la probabilità che il best IS sia sotto la mediana OOS è il **PBO via CSCV** ([`pbo_cscv`](../../core/quant_metrics.py)); il multiple-testing tra varianti si controlla col **White's Reality Check** ([`whites_reality_check`](../../core/quant_metrics.py)); la robustezza vs rumore col **Monte Carlo permutation test** ([`mc_permutation_test`](../../core/quant_metrics.py)).

### 3. Survivorship bias

**Analogia degli aerei WWII**: gli analisti studiavano i fori di proiettile sugli aerei *tornati* per decidere dove blindare, ignorando gli aerei *non tornati* (colpiti dove non si vedevano fori). L'errore è guardare solo i sopravvissuti.

Nel trading: un backtest che esclude le aziende fallite o delistate ("cimitero") gonfia artificialmente la performance. Includendo correttamente le delisted, il rendimento **degrada drasticamente, talvolta diventa negativo**.

**Rimedio**: definire l'universo **dinamicamente** — a ogni timestep T della decisione, l'universo deve includere **tutte** le società esistenti in quel momento, comprese quelle che poi falliscono/delistano. L'universo può basarsi su indici storici con delisted, market cap o altri criteri, purché rifletta il mercato reale al tempo T. Rilevante per [`06_stock_selection`](../06_stock_selection) e lo Stock Selector del repo.

### 4. Walk-forward come mitigazione

Procedura raccomandata contro l'overfitting:
1. spezza i dati in slice sequenziali (es. alcuni mesi IS, alcuni OOS);
2. ottimizza i parametri su ogni slice in-sample;
3. testa sul successivo blocco out-of-sample;
4. fai rotolare il processo in avanti nel tempo.

Riduce la probabilità di overfitting e produce set di parametri più robusti. Implementato in [`walk_forward`](../../core/quant_metrics.py) (anchored e rolling); il protocollo richiede OOS **mai sotto il 20%** del sample e misura il **degrado** IS→OOS come metrica di verdict.

### 5. Costi di transazione, spread, slippage (secondari)

Considerazioni reali ma **non bias core**: costi di transazione, impatto bid-ask spread, slippage di mercato. Erodono l'equity curve. Ma sono **secondari**: se una strategia non è viabile dopo aver corretto i 3 bias, aggiungere i costi non fa che peggiorare il quadro. Vanno comunque modellati (lo Step 5 del protocollo verifica spread variabile, slippage 2× su stop, commissioni, swap, lot rounding).

## Regole operative

- **Sharpe primario, max drawdown secondario.** Lo Sharpe è la metrica di test principale; il max DD è di contorno. Ma lo Sharpe assume return normali — affianca sempre Sortino/Calmar/CVaR ([`core/quant_metrics.py`](../../core/quant_metrics.py)).
- **Prima i 3 bias, poi i costi.** Non perdere tempo a raffinare spread/slippage su una strategia che non sopravvive a look-ahead/overfitting/survivorship.
- **Filtration sempre**: nessun dato futuro nella decisione. Regime timeline solo con lag ≥1 giorno per intraday.
- **Conta i trial.** Se non documentati, assumi ≥100 e applica DSR (Bailey-LdP 2014). Sharpe retail > 2 = red flag; > 3 = quasi certo errore metodologico.
- **Instabilità parametrica = NO-GO.** Se piccole variazioni dei parametri ribaltano la performance, il modello è overfit.
- **Universo dinamico per equity**: includi delisted/falliti al timestep T.
- **Onere della prova sulla strategia**: in caso di verdict ambiguo, default a NO-GO.
- **Soglie operative** (vedi protocollo): PBO < 15% accettabile, > 30% sospetto, > 50% random; DSR significativo al 95%; degrado OOS < 30% per GO; < 50 trade IS = INSUFFICIENT DATA.

## Collegamenti

- [[03_regimi_macro]] — l'edge è condizionato al regime; un backtest "tutto in regime favorevole" è una forma di selection bias.
- [`06_stock_selection`](../06_stock_selection) — dove il survivorship bias morde di più (universo equity).
- [`core/quant_metrics.py`](../../core/quant_metrics.py) — implementazione dei rimedi: DSR, PBO via CSCV, CPCV (purging+embargo), walk-forward, Monte Carlo permutation, White's Reality Check.
- [`docs/QUANT_REVIEW_PROTOCOL.md`](../../docs/QUANT_REVIEW_PROTOCOL.md) — protocollo passo-passo che applica questa teoria.
- [`agents/quant_reviewer.md`](../../agents/quant_reviewer.md) — la persona reviewer (rigore López de Prado / Bailey / Harvey), adversariale per default.
- Casi reali (entrambi **NO-GO**): [`docs/reviews/london_breakout-2026-05-29.md`](../../docs/reviews/london_breakout-2026-05-29.md) e [`docs/reviews/tsmom_jpy-2026-05-29.md`](../../docs/reviews/tsmom_jpy-2026-05-29.md). Per il London Breakout il cap era proprio il **look-ahead della regime timeline** (label same-day).
- [`DECISIONS.md`](../../DECISIONS.md) — log delle decisioni GO/NO-GO derivanti dalle review.

## Fonti

- `_sorgenti/Quant backtest notes.txt` (~95 righe) — distillato fedele: i 3 bias cardinali, esempi (Sharpe ~3→crollo per look-ahead; MA (7,12) IS positivo / OOS ~ -1.8; aerei WWII per survivorship), walk-forward, costi secondari, metafora "scena del crimine".
