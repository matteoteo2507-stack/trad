# docs/ — indice

Documentazione tecnica che vive col codice. Aggiornato **2026-08-04**.

> Per le **decisioni già prese** (GO/NO-GO, priorità, cose da non riproporre) il posto è
> [`../DECISIONS.md`](../DECISIONS.md), non qui. Per i **concetti** distillati:
> [`../fondamenti_tecnici/`](../fondamenti_tecnici/).

## Metodo — come si fa ricerca qui

| Documento | Cosa contiene |
|---|---|
| [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md) | **Il loop di ricerca**: gate, disciplina dei dati (train / holdout sigillato / forward), contabilità dei trial, rifinitura legittima vs p-hacking, **criteri di bocciatura**, riapertura di una famiglia CLOSED |
| [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md) | Come si **misura** una strategia: dati richiesti, DSR/PBO/walk-forward, tabella dei verdetti. È il *gate*, non la regola di stop |
| [TRADING_WORKFLOW_DESIGN.md](TRADING_WORKFLOW_DESIGN.md) | Design del workflow operativo |
| [OPERATIONAL_GUIDE.md](OPERATIONAL_GUIDE.md) | Guida operativa |
| [VPS_COPIER_SETUP.md](VPS_COPIER_SETUP.md) | **Setup VPS del signal copier** passo passo: scelta macchina, blindatura sistema, MT5, Python, sessione Telethon, avvio automatico, sequenza di go-live, modi di rottura noti |

## Pre-registrazioni

Ipotesi, metriche e soglie fissate **prima** di guardare i dati. Nessun test è informativo senza.

| Documento | Stato |
|---|---|
| [NXT_FADE_FORWARD_PREREGISTRATION.md](NXT_FADE_FORWARD_PREREGISTRATION.md) | **ATTIVO** — forward in corso. Due stadi: N=50 boccia, N=200 conferma |
| [COPIER_EXECUTION_PREREGISTRATION.md](COPIER_EXECUTION_PREREGISTRATION.md) | **IN AVVIO** — quanto dell'edge del segnale (+0,194R) sopravvive all'esecuzione. N=60 boccia, N=120 conferma |
| [MENTOR_SIGNALS_OOS_PREREGISTRATION.md](MENTOR_SIGNALS_OOS_PREREGISTRATION.md) | Chiuso → **CONFERMATO** (63,0% vs 35,0% random; E[R] +0,194) |
| [ROUND_NUMBER_GRID_PREREGISTRATION.md](ROUND_NUMBER_GRID_PREREGISTRATION.md) | Chiuso → **NULL** (griglia .80/.20, famiglia CLOSED) |
| [TSMOM_PREREGISTRATION.md](TSMOM_PREREGISTRATION.md) | Chiuso → NO-GO |
| [OPENING_RANGE_PREREGISTRATION.md](OPENING_RANGE_PREREGISTRATION.md) | Chiuso → NO-GO |
| [MEANREV_PREREGISTRATION.md](MEANREV_PREREGISTRATION.md) | Chiuso → NO-GO |
| [SEASONALITY_PREREGISTRATION.md](SEASONALITY_PREREGISTRATION.md) | Chiuso → NO-GO |
| [LEVEL_RESEARCH_PREREGISTRATION.md](LEVEL_RESEARCH_PREREGISTRATION.md) + [LEVEL_RESEARCH_PLAN.md](LEVEL_RESEARCH_PLAN.md) | Chiuso → **CLOSED** (famiglia morta, 384 trial) |

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
