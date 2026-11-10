# registro — indice degli studi

Il registro di tutto cio' che e' stato studiato: pre-registrazioni e documenti di studio in
[`documenti/`](documenti/), referti e output degli audit in [`referti/`](referti/), il codice degli studi in
[`codice/`](codice/) (dal 10/11, una sottocartella per studio: era `analysis/`). Era l'indice di `docs/`
(aggiornato **2026-09-19**); spostato qui col riordino del 09/11, quando `docs/` si e' svuotata. Lo stato di una
famiglia non sta qui: sta nel frontmatter della sua pre-registrazione e nel contatore.

> Per le **decisioni già prese** (GO/NO-GO, priorità, cose da non riproporre) il posto è
> [`../DECISIONS.md`](../../decisioni/DECISIONS.md), non qui. Per i **concetti** distillati:
> [`../fondamenti_tecnici/`](../fondamenti_tecnici/).

## Metodo — come si fa ricerca qui

| Documento | Cosa contiene |
|---|---|
| [STRATEGY_LIFECYCLE.md](../../motore/metodo/STRATEGY_LIFECYCLE.md) | **Il loop di ricerca**: gate, disciplina dei dati (train / holdout sigillato / forward), contabilità dei trial, rifinitura legittima vs p-hacking, **criteri di bocciatura**, riapertura di una famiglia CLOSED |
| [QUANT_REVIEW_PROTOCOL.md](../../motore/metodo/QUANT_REVIEW_PROTOCOL.md) | Come si **misura** una strategia: dati richiesti, **Step 3bis = gate bloccante sull'ottenibilità dei fill**, DSR/PBO/walk-forward, tabella dei verdetti. È il *gate*, non la regola di stop |
| [trial_ledger.json](../../decisioni/trial_ledger.json) | **Contatore trial persistente** (LIFECYCLE §3): trial cumulati, round spesi, holdout, quota di pre-registrazioni esterne, **provenienza dell'ipotesi**. Si legge con `python -m motore.core.trial_ledger`; `--check` esce **1** se un budget è sforato o se una voce non cita le sue fonti |

**Le regole di metodo sono anche codice** (debito E1-E6 estinto il 2026-09-19 — [DECISIONS 19/09](../../decisioni/DECISIONS.md)):

| Modulo | Cosa fa rispettare |
|---|---|
| [`motore/core/random_baseline.py`](../../motore/core/random_baseline.py) | il baseline random risk-matched: campionamento, **verifica del matching**, divario con cluster sull'evento |
| [`motore/core/data_checks.py`](../../motore/core/data_checks.py) | la checklist dati/esecuzione come assert: monotonia, duplicati, barre/anno, partenze scaglionate, file più completo, **% di fill non ottenibili**, gap oltre lo stop |
| [`motore/core/trial_ledger.py`](../../motore/core/trial_ledger.py) | contatore trial, budget, **regola di futilità come numero** |
| [`motore/core/resolve_trade.py`](../../motore/core/resolve_trade.py) | le 5 convenzioni d'uscita come parametri espliciti |
| [TRADING_WORKFLOW_DESIGN.md](../dormienti/docs/TRADING_WORKFLOW_DESIGN.md) | Design del workflow operativo |
| [OPERATIONAL_GUIDE.md](../dormienti/docs/OPERATIONAL_GUIDE.md) | Guida operativa |
| [VPS_COPIER_SETUP.md](../../docs/VPS_COPIER_SETUP.md) | **Setup VPS del signal copier** passo passo: scelta macchina, blindatura sistema, MT5, Python, sessione Telethon, avvio automatico, sequenza di go-live, modi di rottura noti |

## Pre-registrazioni

Ipotesi, metriche e soglie fissate **prima** di guardare i dati. Nessun test è informativo senza.

> **Lo stato di ogni pre-registrazione vive in un solo posto: il frontmatter del documento**
> (`stato`, `aggiornato`, `decisione`, `metrica_corrente`). Questa tabella **non ripete** stati né
> numeri — è il motivo per cui il 27/09 diceva ancora "FADE ATTIVO" dieci giorni dopo il KILL.
> Vista d'insieme: [`../mappa/_cruscotto.base`](../../decisioni/mappa/_cruscotto.base) (Obsidian).

| Documento | Cosa testa |
|---|---|
| [ULTIMA_MEZZORA_PREREGISTRATION.md](documenti/ULTIMA_MEZZORA_PREREGISTRATION.md) | momentum dell'ultima mezz'ora sugli indici USA (coperture di gamma, backlog H1) |
| [MR_INDICI_RSI2_PREREGISTRATION.md](documenti/MR_INDICI_RSI2_PREREGISTRATION.md) | RSI(2) di Connors sugli indici USA contro un ingresso casuale a durata copiata (candidato A) |
| [FOREXGUMP_LATENCY_PREREGISTRATION.md](documenti/FOREXGUMP_LATENCY_PREREGISTRATION.md) | segnali di Forex Gump GOLD VIP: il segnale copiato in ritardo vale ancora? |
| [NXT_FADE_FORWARD_PREREGISTRATION.md](documenti/NXT_FADE_FORWARD_PREREGISTRATION.md) | forward del FADE mean-reversion (NXT A1), due stadi |
| [COPIER_EXECUTION_PREREGISTRATION.md](documenti/COPIER_EXECUTION_PREREGISTRATION.md) | quanto dell'edge dei segnali mentore sopravvive all'esecuzione del copier |
| [MENTOR_SIGNALS_OOS_PREREGISTRATION.md](documenti/MENTOR_SIGNALS_OOS_PREREGISTRATION.md) | segnali mentore XAUUSD fuori campione, contro lato casuale appaiato |
| [TREND_EXIT_PLAYGROUND_PREREGISTRATION.md](documenti/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md) | trend following: uscita a coda aperta × gradiente di liquidità (playground, A1) |
| [ROUND_NUMBER_GRID_PREREGISTRATION.md](documenti/ROUND_NUMBER_GRID_PREREGISTRATION.md) | livelli a numero tondo .80/.20 sul Nasdaq |
| [TSMOM_PREREGISTRATION.md](documenti/TSMOM_PREREGISTRATION.md) | time-series momentum multi-asset |
| [OPENING_RANGE_PREREGISTRATION.md](documenti/OPENING_RANGE_PREREGISTRATION.md) | opening-range breakout + retest, US100 M5 |
| [MEANREV_PREREGISTRATION.md](documenti/MEANREV_PREREGISTRATION.md) | mean-reversion di volatilità (non su livelli) |
| [SEASONALITY_PREREGISTRATION.md](documenti/SEASONALITY_PREREGISTRATION.md) | stagionalità turn-of-month |
| [LEVEL_RESEARCH_PREREGISTRATION.md](documenti/LEVEL_RESEARCH_PREREGISTRATION.md) + [LEVEL_RESEARCH_PLAN.md](documenti/LEVEL_RESEARCH_PLAN.md) | livelli come zone di reazione (famiglia `livelli`; trial nel contatore, `python -m motore.core.trial_ledger`) |

## Pilastro investing (passivo)

| Documento | Cosa contiene |
|---|---|
| [INVESTING_PILLAR_PLAN.md](../../esercizio/pac/INVESTING_PILLAR_PLAN.md) | **Documento vivo** del PAC: due secchi, glide-path, guardrail, candidati broker/ETF, input personali mancanti |
| [INVESTMENT_ALGO_DESIGN.md](../dormienti/docs/INVESTMENT_ALGO_DESIGN.md) | Perché niente algoritmo custom sul pilastro investing |

## Sistema e architettura

| Documento | Cosa contiene |
|---|---|
| [ARCHITECTURE_v2.md](../dormienti/docs/ARCHITECTURE_v2.md) | Architettura del sistema |
| [PYTHON_FILES_MAP.md](../dormienti/docs/PYTHON_FILES_MAP.md) | Mappa dei file Python del repo |
| [STAGE2_TESTING_PLAN.md](../dormienti/docs/STAGE2_TESTING_PLAN.md) | Piano di test Stage 2 |
| [reviews/](referti/) | Quant review effettive, una per strategia testata |

## Backlog documentale

- `PROP_FIRM_CRITERIA.md` — matrice dei criteri pesati + shortlist verificata sui **rulebook
  primari**. **Rimandato**: la scelta della prop è a valle di un GO, e oggi non abbiamo nulla di
  finanziabile ([DECISIONS.md](../../decisioni/DECISIONS.md), 2026-08-04).
- `FISCAL_SUPERVISOR_SPEC.md` — subagent di allerta fiscale (checklist datata, non consulenza).
  **Da costruire per ultimo**, quando entrambi i pilastri hanno numeri veri.
