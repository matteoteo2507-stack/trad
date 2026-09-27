# docs/ — indice

Documentazione tecnica che vive col codice. Aggiornato **2026-09-19**.

> Per le **decisioni già prese** (GO/NO-GO, priorità, cose da non riproporre) il posto è
> [`../DECISIONS.md`](../DECISIONS.md), non qui. Per i **concetti** distillati:
> [`../fondamenti_tecnici/`](../fondamenti_tecnici/).

## Metodo — come si fa ricerca qui

| Documento | Cosa contiene |
|---|---|
| [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md) | **Il loop di ricerca**: gate, disciplina dei dati (train / holdout sigillato / forward), contabilità dei trial, rifinitura legittima vs p-hacking, **criteri di bocciatura**, riapertura di una famiglia CLOSED |
| [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md) | Come si **misura** una strategia: dati richiesti, **Step 3bis = gate bloccante sull'ottenibilità dei fill**, DSR/PBO/walk-forward, tabella dei verdetti. È il *gate*, non la regola di stop |
| [trial_ledger.json](trial_ledger.json) | **Contatore trial persistente** (LIFECYCLE §3): trial cumulati, round spesi, holdout, quota di pre-registrazioni esterne, **provenienza dell'ipotesi**. Si legge con `python -m core.trial_ledger`; `--check` esce **1** se un budget è sforato o se una voce non cita le sue fonti |

**Le regole di metodo sono anche codice** (debito E1-E6 estinto il 2026-09-19 — [DECISIONS 19/09](../DECISIONS.md)):

| Modulo | Cosa fa rispettare |
|---|---|
| [`../core/random_baseline.py`](../core/random_baseline.py) | il baseline random risk-matched: campionamento, **verifica del matching**, divario con cluster sull'evento |
| [`../core/data_checks.py`](../core/data_checks.py) | la checklist dati/esecuzione come assert: monotonia, duplicati, barre/anno, partenze scaglionate, file più completo, **% di fill non ottenibili**, gap oltre lo stop |
| [`../core/trial_ledger.py`](../core/trial_ledger.py) | contatore trial, budget, **regola di futilità come numero** |
| [`../core/resolve_trade.py`](../core/resolve_trade.py) | le 5 convenzioni d'uscita come parametri espliciti |
| [TRADING_WORKFLOW_DESIGN.md](TRADING_WORKFLOW_DESIGN.md) | Design del workflow operativo |
| [OPERATIONAL_GUIDE.md](OPERATIONAL_GUIDE.md) | Guida operativa |
| [VPS_COPIER_SETUP.md](VPS_COPIER_SETUP.md) | **Setup VPS del signal copier** passo passo: scelta macchina, blindatura sistema, MT5, Python, sessione Telethon, avvio automatico, sequenza di go-live, modi di rottura noti |

## Pre-registrazioni

Ipotesi, metriche e soglie fissate **prima** di guardare i dati. Nessun test è informativo senza.

> **Lo stato di ogni pre-registrazione vive in un solo posto: il frontmatter del documento**
> (`stato`, `aggiornato`, `decisione`, `metrica_corrente`). Questa tabella **non ripete** stati né
> numeri — è il motivo per cui il 27/09 diceva ancora "FADE ATTIVO" dieci giorni dopo il KILL.
> Vista d'insieme: [`../mappa/_cruscotto.base`](../mappa/_cruscotto.base) (Obsidian).

| Documento | Cosa testa |
|---|---|
| [NXT_FADE_FORWARD_PREREGISTRATION.md](NXT_FADE_FORWARD_PREREGISTRATION.md) | forward del FADE mean-reversion (NXT A1), due stadi |
| [COPIER_EXECUTION_PREREGISTRATION.md](COPIER_EXECUTION_PREREGISTRATION.md) | quanto dell'edge dei segnali mentore sopravvive all'esecuzione del copier |
| [MENTOR_SIGNALS_OOS_PREREGISTRATION.md](MENTOR_SIGNALS_OOS_PREREGISTRATION.md) | segnali mentore XAUUSD fuori campione, contro lato casuale appaiato |
| [TREND_EXIT_PLAYGROUND_PREREGISTRATION.md](TREND_EXIT_PLAYGROUND_PREREGISTRATION.md) | trend following: uscita a coda aperta × gradiente di liquidità (playground, A1) |
| [ROUND_NUMBER_GRID_PREREGISTRATION.md](ROUND_NUMBER_GRID_PREREGISTRATION.md) | livelli a numero tondo .80/.20 sul Nasdaq |
| [TSMOM_PREREGISTRATION.md](TSMOM_PREREGISTRATION.md) | time-series momentum multi-asset |
| [OPENING_RANGE_PREREGISTRATION.md](OPENING_RANGE_PREREGISTRATION.md) | opening-range breakout + retest, US100 M5 |
| [MEANREV_PREREGISTRATION.md](MEANREV_PREREGISTRATION.md) | mean-reversion di volatilità (non su livelli) |
| [SEASONALITY_PREREGISTRATION.md](SEASONALITY_PREREGISTRATION.md) | stagionalità turn-of-month |
| [LEVEL_RESEARCH_PREREGISTRATION.md](LEVEL_RESEARCH_PREREGISTRATION.md) + [LEVEL_RESEARCH_PLAN.md](LEVEL_RESEARCH_PLAN.md) | livelli come zone di reazione (famiglia dei 384 trial) |

## Pilastro investing (passivo)

| Documento | Cosa contiene |
|---|---|
| [INVESTING_PILLAR_PLAN.md](INVESTING_PILLAR_PLAN.md) | **Documento vivo** del PAC: due secchi, glide-path, guardrail, candidati broker/ETF, input personali mancanti |
| [INVESTMENT_ALGO_DESIGN.md](INVESTMENT_ALGO_DESIGN.md) | Perché niente algoritmo custom sul pilastro investing |

## Sistema e architettura

| Documento | Cosa contiene |
|---|---|
| [ARCHITECTURE_v2.md](ARCHITECTURE_v2.md) | Architettura del sistema |
| [PYTHON_FILES_MAP.md](PYTHON_FILES_MAP.md) | Mappa dei file Python del repo |
| [STAGE2_TESTING_PLAN.md](STAGE2_TESTING_PLAN.md) | Piano di test Stage 2 |
| [reviews/](reviews/) | Quant review effettive, una per strategia testata |

## Backlog documentale

- `PROP_FIRM_CRITERIA.md` — matrice dei criteri pesati + shortlist verificata sui **rulebook
  primari**. **Rimandato**: la scelta della prop è a valle di un GO, e oggi non abbiamo nulla di
  finanziabile ([DECISIONS.md](../DECISIONS.md), 2026-08-04).
- `FISCAL_SUPERVISOR_SPEC.md` — subagent di allerta fiscale (checklist datata, non consulenza).
  **Da costruire per ultimo**, quando entrambi i pilastri hanno numeri veri.
