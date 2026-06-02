---
name: quant-review
description: Eseguire una review quantitativa adversariale di una strategia di trading automatica (MQL5 EA o modulo Python). Usare quando l'utente chiede "valuta questa strategia", "ha edge?", "passa la review quant?", "/quant-review <strategia>", o vuole un giudizio rigoroso (PBO, DSR, walk-forward) prima di promuovere una strategia da demo a live.
---

# Skill — Quant Review

Questa skill orchestra il subagent **Quant Reviewer** ([agents/quant_reviewer.md](../../agents/quant_reviewer.md))
per produrre una review quantitativa di una strategia. Il giudizio è **adversariale per
default**: l'obiettivo è cercare attivamente perché la strategia *non* funziona, non
confermare bias dell'utente.

## Quando usarla

Trigger espliciti:
- `/quant-review mql5/london_breakout.mq5`
- `/quant-review strategies/tsmom/`
- "valuta la strategia X con il quant reviewer"
- "ha senso promuovere London Breakout a live?"
- "questa configurazione è overfitted?"

## Cosa fa la skill

1. **Identifica la strategia target**: file MQL5 (`mql5/*.mq5`) o modulo Python
   (`strategies/<name>/`). Se ambiguo, chiedi all'utente.
2. **Raccoglie i dati**:
   - Codice sorgente (entry/exit/filters/sizing).
   - Backtest report disponibili (CSV trade log o `.htm` di MT5).
   - Trade log live/demo se presenti (Notion `Trading Journal` export + `journals/`).
   - Configurazione (`config.yaml`, parametri input EA).
3. **Conta i gradi di libertà**: parametri tunabili totali, varianti testate.
4. **Esegue le metriche statistiche** via [core/quant_metrics.py](../../core/quant_metrics.py):
   - PBO via CSCV (López de Prado-Bailey 2017).
   - Deflated Sharpe Ratio (Bailey-LdP 2014).
   - Walk-forward analysis (anchored + rolling).
   - Monte Carlo permutation test.
   - Se ≥ 2 varianti: White's Reality Check.
5. **Produce il report** nel formato definito da
   [agents/quant_reviewer.md](../../agents/quant_reviewer.md) §Output, salvato in
   `docs/reviews/<strategia>-<YYYY-MM-DD>.md`.

## Istruzioni per Claude Code

Quando si attiva questa skill:

1. **Carica il prompt** di [agents/quant_reviewer.md](../../agents/quant_reviewer.md)
   come system prompt aggiuntivo per il task.
2. **Leggi il codice della strategia** target. Riassumi in 5 righe (entry, exit,
   filtri, sizing, frequenza attesa). Se non ci riesci, **lo segnali come red flag**
   nel report (complessità eccessiva).
3. **Cerca trade log disponibili**:
   - MT5: `<terminal>/MQL5/Files/<strategia>.csv` o report HTM.
   - Python: `strategies/<name>/output/trades.csv` o equivalente.
   - Notion: se l'utente lo richiede, esporta via API (vedi
     [`journals/NOTION_JOURNAL_SCHEMA.md`](../../journals/NOTION_JOURNAL_SCHEMA.md)).
4. **Esegui [core/quant_metrics.py](../../core/quant_metrics.py)** con il trade log:

   ```python
   from core.quant_metrics import (
       deflated_sharpe_ratio,
       pbo_cscv,
       walk_forward,
       mc_permutation_test,
   )

   import pandas as pd
   returns = pd.read_csv("trades.csv")["pnl_pct"]
   print(deflated_sharpe_ratio(returns, n_trials=100))
   print(pbo_cscv(returns_matrix, s=16))
   ```

5. **Se mancano dati per i test statistici**: invece di stimare a occhio, **chiedi
   esplicitamente** all'utente di:
   - Esportare il trade log mancante.
   - Eseguire un backtest aggiuntivo (su quale periodo, quali parametri).
   - O dichiarare il verdict come "INSUFFICIENT DATA" senza pronunciarsi.

6. **Output** in `docs/reviews/<strategia>-<YYYY-MM-DD>.md` con il formato del
   §Output di quant_reviewer.md. Include link relativi a codice e dati usati.

## Vincoli

- **Mai promuovere a live** una strategia con PBO > 30% o senza walk-forward OOS.
- **Mai inventare numeri**. Una metrica non calcolata è una metrica mancante,
  non una stima.
- **Cita paper/sezione** per ogni affermazione tecnica (vedi libreria canonica
  in [agents/quant_reviewer.md](../../agents/quant_reviewer.md) §Riferimenti).
- **Sharpe retail > 2 senza giustificazione = automatic red flag** nel report.
- **Adversariale**: il default è "questa strategia non ha edge dimostrato"; va
  ribaltato solo se i test lo provano.

## Riferimenti

- Persona: [agents/quant_reviewer.md](../../agents/quant_reviewer.md).
- Metriche: [core/quant_metrics.py](../../core/quant_metrics.py).
- Protocollo operativo: [docs/QUANT_REVIEW_PROTOCOL.md](../../docs/QUANT_REVIEW_PROTOCOL.md).
- Output esempio: `docs/reviews/london_breakout-*.md` (primo run da generare).
