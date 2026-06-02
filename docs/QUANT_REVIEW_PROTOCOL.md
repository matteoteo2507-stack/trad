# Quant Review — Protocollo operativo

Procedura passo-passo che il **Quant Reviewer** ([agents/quant_reviewer.md](../agents/quant_reviewer.md))
esegue quando viene invocato via skill [quant-review](../skills/quant-review/SKILL.md)
su una strategia (`mql5/*.mq5` o `strategies/*/`).

Output finale: report in `docs/reviews/<strategia>-<YYYY-MM-DD>.md` nel formato del
§Output di `quant_reviewer.md`.

---

## Step 1 — Comprensione della strategia (10 min)

1. Leggi il codice sorgente. Identifica:
   - **Entry rules** (timing, condizioni, ordini market vs limit vs stop).
   - **Exit rules** (TP, SL, time stop, trailing).
   - **Filters** (regime, news, blackout, sessioni).
   - **Sizing** (fixed fractional, vol target, fissato).
2. Scrivi un **sommario in 5 righe** in linguaggio quant.
3. Se non riesci in 5 righe → segnala **complessità eccessiva** come red flag e
   continua.

## Step 2 — Conta i gradi di libertà (5 min)

| Parametro | Origine | Tipo | Note |
|---|---|---|---|
| `InpAtrPeriod` | EA input | int | tunable |
| `InpTpRMultiple` | EA input | float | tunable |
| ... | ... | ... | ... |

- **N_params**: somma totale.
- **N_calibrati**: quanti sono stati scelti guardando i dati storici.
- **N_a_priori**: quanti sono "ovvi" (es. fine sessione = 16:00 UTC).
- **N_trial_stimati**: se l'utente non documenta, **assumi 100 × N_params**
  (Bailey-LdP 2014 raccomandazione).

## Step 3 — Raccogli i dati (15 min)

1. **Trade log** (necessario per metriche statistiche):
   - MT5 Strategy Tester → export CSV/HTM dei trade.
   - Python: `strategies/<name>/output/trades.csv`.
   - Live demo: export Notion `Trading Journal` filtrato per strategia.
2. **Matrice returns per CSCV** (necessaria per PBO):
   - T × N_varianti — almeno 2-3 varianti di parametri vicini per costruire
     la matrice. Senza varianti **non puoi calcolare PBO**: marca "insufficient
     data".
3. **Returns minimi**: ≥ 50 trade IS per qualunque conclusione. ≥ 200 per
   significatività robusta.

## Step 4 — Esegui le metriche (20 min)

```python
import pandas as pd
import numpy as np
from core.quant_metrics import (
    sharpe_ratio,
    deflated_sharpe_ratio,
    pbo_cscv,
    walk_forward,
    mc_permutation_test,
    sortino_ratio,
    max_drawdown,
    calmar_ratio,
    tail_metrics,
    whites_reality_check,
)

# 1. Trade log → returns
trades = pd.read_csv("trades.csv")
r = trades["pnl_pct"].to_numpy()

# 2. Sharpe + DSR
sr = sharpe_ratio(r, periods_per_year=252)
dsr = deflated_sharpe_ratio(r, n_trials=100, periods_per_year=252)
# Stampa dsr["dsr"], dsr["significant_95"]

# 3. PBO (richiede matrice varianti)
variants_returns = ...  # T × N matrix
pbo = pbo_cscv(variants_returns, s=16)
# Stampa pbo["pbo"]; soglia accettabile < 0.15

# 4. Walk-forward
wf = walk_forward(r, train_size=126, test_size=63, anchored=False)
# Stampa wf.is_mean, wf.oos_mean, wf.degradation

# 5. Monte Carlo permutation
mc = mc_permutation_test(r, n_perm=2000, block_size=5)
# Stampa mc["p_value"]; soglia < 0.05

# 6. Risk metrics aggiuntivi
sortino = sortino_ratio(r)
mdd = max_drawdown(r)
calmar = calmar_ratio(r)
tails = tail_metrics(r)

# 7. White's Reality Check (se confronti varianti)
wrc = whites_reality_check(variants_returns, n_boot=1000, block_size=5)
```

## Step 5 — Costi reali (10 min)

Verifica che il trade log includa:
- [ ] Spread reale (variabile, non costante).
- [ ] Slippage modellato (stop orders → 2× spread minimo).
- [ ] Commissioni broker (anche se zero, documentarlo).
- [ ] Swap overnight se posizioni multi-day.
- [ ] Lot rounding a step minimo.

Se uno qualsiasi manca, **ricalcola le metriche** dopo aver applicato una
correzione conservativa (es. -1 pip / trade) e confronta degrado.

## Step 6 — Pre-mortem (10 min)

Rispondi per iscritto alle 3 domande del §6 di `quant_reviewer.md`:

1. **Quale cambiamento di regime la rompe?**
   (es. "London Breakout fallisce in Sideways Quiet quando range Asia >
   media e prezzo torna dentro").
2. **Quale assunzione metodologica nascosta?**
   (es. "il backtest assume liquidità infinita anche su NFP friday").
3. **Quale costo reale non modellato la affossa?**
   (es. "swap negativo su XAU short può divorare 1.5R / mese").

## Step 7 — Verdict

| PBO | DSR sig. 95% | OOS degrado | Verdict |
|---|---|---|---|
| < 15% | Sì | < 30% | **GO** (live con sizing standard) |
| 15-30% | Sì | 30-50% | **RAFFINA** (test aggiuntivi, ridurre params) |
| > 30% | No | > 50% | **NO-GO** |
| qualsiasi | qualsiasi | n_trades < 50 IS | **INSUFFICIENT DATA** |

In caso di verdict ambiguo, **default verso NO-GO**. L'onere della prova è
sulla strategia, non sul reviewer.

## Step 8 — Output report

Salva in `docs/reviews/<strategia>-<YYYY-MM-DD>.md` con il formato del
§Output di `quant_reviewer.md`. Link relativi a:
- Codice strategia.
- Trade log usati.
- Eventuali notebook di analisi.

---

## Casi speciali

### Strategia con < 50 trade live ma backtest lungo

- Usa il backtest per PBO/DSR/walk-forward, ma **dichiara nel report**:
  "Live evidence insufficiente; metriche da backtest, soggette ai bias di
  costi/slippage". Verdict massimo possibile = **RAFFINA**.

### Strategia in stato di sperimentazione A/B/C (es. London Breakout 3 varianti)

- Calcola PBO con S=16 sulla matrice T × 3.
- Applica White's Reality Check per il multiple-testing.
- Verdict per ciascuna variante separato + verdict sulla famiglia.

### Strategia con assunzioni macro forti (es. carry trade, TSMOM)

- Verifica regime in cui il paper di riferimento documenta l'edge.
- Cita McLean-Pontiff JF 2016 per alpha decay post-publication.
- Verdict GO solo se l'edge è confermato anche nel sub-sample più recente
  (es. ultimi 5 anni).
