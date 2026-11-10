---
titolo: Mappa di trad — panoramica e percorso
tipo: mappa
tags: [#public]
creato: 2026-09-30
compreso: spiegato
verificato_il:
metodo: spiegazione
---

# Mappa di trad — panoramica e percorso

`trad` è il progetto di ricerca quant: un **metodo** per decidere se un'idea di trading merita
capitale, gli **strumenti** che lo rendono misurabile, e i pochi **sistemi** che girano davvero. Dal 09/11 il suo ruolo fra i soci e' fornire la teoria e gli strumenti di lettura del prezzo su cui
poggia la ricerca di edge, consegnati come pacchetti ([PROJECT](../../PROJECT.md), DECISIONS 2026-11-09).
Questa nota è la porta d'ingresso. Ogni componente ha la sua nota, scritta leggendo il codice
vero. La mappa dell'hub (Sync, backup, filtri) è a parte: [[mappa/00-panoramica|panoramica dell'hub]].

## Obiettivo e risalita (30/09/2026)

```
"Matteo ha domestichezza completa con trad: sa cosa fa ogni parte, come si usa, come si rompe"
  ← comprensione VERIFICATA componente per componente (campo `compreso` + metodo)
    ← una nota per componente, che cita i file reali
      ← questa panoramica: come i componenti si collegano
        ← un CATASTO COMPLETO: ogni cartella e ogni doc assegnati a un componente
          (senza catasto "tutto" non è misurabile: non sapremmo quando abbiamo finito)
```

## Il sistema in due figure

**1. Il loop di ricerca: come un'idea diventa una decisione.** Metodo:
`motore/metodo/STRATEGY_LIFECYCLE.md` §1.

```mermaid
flowchart LR
  I[Idea o materiale<br/>_INTAKE · socio · video] --> P["[G1] Pre-registrazione<br/>magazzino/registro/documenti/"]
  P --> S[Studio<br/>magazzino/registro/codice/&lt;famiglia&gt;/]
  C[(motore/core/<br/>primitive di misura)] --> S
  S --> V["[G2] Verdetto<br/>magazzino/registro/referti/"]
  QG{{quant-gatekeeper}} -. controlla .-> P
  QG -. controlla .-> V
  V --> D[DECISIONS.md<br/>+ stato nel frontmatter]
  D -->|LEAD| F[Forward su demo<br/>EA esercizio/mql5/ o copier]
  D -->|NO-GO · KILL · CLOSED| X[Famiglia chiusa]
  F --> H[Sorveglianza<br/>esercizio/sorveglianza/]
  H --> D
  T[(trial_ledger)] -. conta i tentativi .-> P
```

**2. La catena che tocca soldi: i segnali del mentore.** Era l'unico edge `CONFERMATO`; dal 02/10 è
stato in revisione perché il canale cancella i segnali perdenti, e dal **25/10 è `CLOSED`, non dimostrato**
(frontmatter di `magazzino/registro/documenti/MENTOR_SIGNALS_OOS_PREREGISTRATION.md`, DECISIONS 2026-10-25 (6)). La catena qui sotto resta
come descrizione di com'era costruita: il **journal** è l'unico registro non selezionato, l'export Telegram no.

```mermaid
flowchart LR
  TG[Canale Telegram<br/>del mentore] --> R[reader<br/>Telethon]
  R --> PA[parser<br/>per canale]
  PA --> PL[planner<br/>sizing + gate]
  CF[(esercizio/signal_copier/<br/>config.yaml)] --> PL
  PL --> EX[executor<br/>+ gate alla riconciliazione]
  EX --> MT[motore/brokers/mt5.py] --> MT5[(MetaTrader 5<br/>demo)]
  EX --> J[journal JSONL]
  TG -. export .-> ET[(_export_telegram/)] --> MS[magazzino/registro/codice/mentor_signals/<br/>misura del track record]
```

**Dove agisce il gate anti-ritardo (dal 30/09).** Il mentore apre sul messaggio "NOW", prima di
postare l'entrata: il copier entra a mercato con un bracket provvisorio e, al messaggio coi livelli,
**riconcilia**. Il gate (20 pip, solo lato sfavorevole: `planner.late_gate`) agisce quindi in due
punti: nel **planner** per i canali che postano tutto in un messaggio, e nell'**executor alla
riconciliazione** per il mentore, dove se scatta **chiude le gambe a mercato**. Prima del 30/09 sul
mentore non agiva mai ([review del 30/09](../../magazzino/registro/referti/analysis_team_live_2026-09-30.md) §4).

## Catasto: dove sta ogni cosa

Censimento del 30/09/2026 con `git ls-files` e l'analisi degli import di tutti i 179 file `.py`
(circa 31.000 righe). **Stato**: *vivo* = usato o modificato nell'ultimo mese; *sorveglianza* =
fermo ma legato a qualcosa che gira; *dormiente* = funziona ma non è usato; *archivio* = storia.

| Cartella / file | Cosa contiene | Componente | Stato |
|---|---|---|---|
| `motore/metodo/STRATEGY_LIFECYCLE.md`, `motore/metodo/QUANT_REVIEW_PROTOCOL.md`, `magazzino/registro/documenti/EARLY_STAGE_AUDIT_*`, `decisioni/BACKLOG_RICERCA.md`, `decisioni/trial_ledger.json` | il metodo | 1 · ciclo di vita e gate | vivo |
| `magazzino/registro/documenti/*_PREREGISTRATION.md`, `decisioni/DECISIONS.md`, `magazzino/registro/referti/`, `magazzino/registro/README.md`, `decisioni/mappa/_cruscotto.base` | stato e storia delle decisioni | 2 · stato canonico | vivo |
| `esercizio/signal_copier/` (configurazione propria in `esercizio/signal_copier/config.yaml`), `magazzino/registro/documenti/COPIER_EXECUTION_PREREGISTRATION.md` | copia dei segnali Telegram → MT5 | 3 · signal copier | vivo (demo dal 21/09) |
| `esercizio/mql5/`, `esercizio/sorveglianza/` (script e `report/`), `magazzino/registro/documenti/FADE_LIVE_AUDIT_PROTOCOL.md`; in `magazzino/registro/referti/audit/` e `magazzino/registro/codice/ops/` restano solo output e script degli audit di famiglia (vanno nel registro) | Expert Advisor e loro sorveglianza | 4 · EA e VPS | sorveglianza |
| `magazzino/registro/codice/mentor_signals/`, `magazzino/registro/codice/{mentor_entries,mentor_momentum,export_dataset,probe_mt5}.py`, `magazzino/registro/documenti/MENTOR_*`, `esercizio/prop/PROP_FIRM_CRITERIA.md`, `_export_telegram/` (dati, fuori da git) | misura del track record del mentore | 5 · segnali mentore | vivo |
| `motore/core/` (tranne regime, prop_sim, sizing), `motore/core/tests/`, `motore/config/risk.yaml` (letto da `motore/core/risk_gate.py`) | primitive di misura e gate di rischio delle strategie meccaniche | 6 · primitive | vivo |
| `magazzino/registro/codice/trend/`, `magazzino/registro/documenti/TREND_*`, `magazzino/registro/documenti/B2_KICHEV_POTENZA.md` | uno studio completo, usato come esempio | 7 · anatomia di uno studio | vivo |
| `magazzino/registro/codice/{level_research,nxt,opening_range,meanrev,meanrev_indici,round_grid,extension,trading-bot-eval,veltrix,forexgump,ultima_mezzora,vtob_intake,pac_intake}/`, `magazzino/registro/codice/{tsmom,seasonality}/` e `meanrev/backtest.py` (erano in `strategies/`), i restanti documenti di famiglia in `magazzino/registro/documenti/` (`LEVEL_RESEARCH_PLAN`, `NXT_EXIT_CEILING_ADDENDUM`, `B3_*`, `ULTIMA_MEZZORA_FATTIBILITA`) | tutte le famiglie studiate | 8 · catalogo delle famiglie | archivio: nessuna famiglia viva (stato di ciascuna: `python -m motore.core.trial_ledger`); `vtob_intake` e' un intake in attesa della decisione di Matteo |
| `decisioni/Da distillare/` (cartella di arrivo, il più possibile vuota), `decisioni/_INTAKE.md`, `magazzino/fondamenti_tecnici/`, `magazzino/registro/codice/intake/`, `magazzino/fonti/materiale_socio/`, `magazzino/fondamenti_tecnici/TRADING_PRINCIPLES.md` | conoscenza distillata e porta del materiale nuovo | 9 · conoscenza e intake | vivo |
| `CLAUDE.md`, `.claude/`, `memoria/trad/` (nell'hub) | come lavora Claude su trad | 10 · Claude in trad | vivo (`agents/` e `skills/` alla radice ritirati il 13/10: nessuno strumento li caricava, nessun codice li leggeva) |
| `pyproject.toml`, `conftest.py`, `motore/tests/`, `motore/config/markets.yaml`, `motore/config/README.md`, `.env.example`, `.gitignore`, `motore/data/` (coi prezzi in `motore/data/prezzi/`, fuori da git), `motore/CONVENTIONS.md` | ambiente, test, configurazione | 11 · ambiente e test | vivo |
| `magazzino/dormienti/orchestratore/` (`runner.py`, `registry.py`, erano in `core/`), `magazzino/dormienti/strategies/{_template,confluence_levels,confluence_auto}/`, `motore/core/strategia_base.py` (il `Signal` letto dal risk gate, era `strategies/_base.py`), `motore/notifiers/`, `motore/brokers/` (tranne mt5), `magazzino/dormienti/backtesters/`, `magazzino/dormienti/level_analyzer/`, `magazzino/dormienti/journals/`, `magazzino/dormienti/docs/{ARCHITECTURE_v2,STAGE2_TESTING_PLAN,OPERATIONAL_GUIDE,TRADING_WORKFLOW_DESIGN,PYTHON_FILES_MAP}.md` | l'architettura di maggio–giugno (pre e post pivot) | 12 · sistemi dormienti | dormiente |
| `magazzino/dormienti/strategies/stock_selector/`, `motore/core/regime.py`, `esercizio/pac/INVESTING_PILLAR_PLAN.md`, `magazzino/dormienti/docs/INVESTMENT_ALGO_DESIGN.md`, `magazzino/dormienti/stoxs picks/` | investimento passivo e il vecchio selettore di azioni | 13 · investing | archivio (selettore), vivo (PAC) |
| `motore/prop-lab/` (repo condiviso col socio VELTRIX, allineato con `motore/prop-lab/CHANGELOG.md`), `motore/core/prop_sim.py`, `motore/core/sizing.py` | simulatore di challenge prop, pipeline di famiglia del socio, doppio binario della gestione del rischio | 14 · prop-lab e doppio binario | vivo (dal 06/10) |
| `decisioni/README.md`, `motore/README.md`, `magazzino/README.md`, `esercizio/README.md`, `uscita/README.md` | le cinque macro (migrate il 09-10/11): `decisioni/` raccoglie in ordine di processo ingresso, smistamento, backlog, registro, contatore e mappa; ogni README dice cosa contiene la macro e le sue regole; `uscita/` resta vuota fino al primo pacchetto | — | vivo |
| `motore/riordino/sposta.py` | lo strumento della migrazione: sposta file e cartelle (anche quelle fuori da git) e riscrive link, menzioni e import | — | vivo: serve a ogni spostamento futuro |
| `README.md`, `PROJECT.md` | i file d'ingresso: obiettivo comune ai soci, ruoli, dove stanno le cose (riscritti il 09/11, DECISIONS 2026-11-09) | — | vivo |
| `decisioni/mappa/` | questa mappa, il cruscotto e il registro modifiche di trad | — | vivo |
| `backtest_results/`, `logs/` | risultati e materiale locale, quasi tutto fuori da git (`output/` e `docs/` tolte il 10/11: il loro ultimo file e' nei dormienti e col copier; `socio-trading-bot/`, doppione del clone in `trading-bot-eval/vendor-trading-bot/`, cancellato da Matteo il 10/11) | — | dati |

**Moduli condivisi tra componenti:** `motore/brokers/mt5.py` (3 e 4), `motore/notifiers/_pip_table.py` (3 e 5),
`motore/core/quant_metrics.py` (usato da 22 file di ricerca), `motore/core/risk_gate.py` (6 e 12: lo usano
`magazzino/dormienti/orchestratore/runner.py` e `confluence_levels`, **non** il copier).

**Da sapere prima di iniziare:** `magazzino/dormienti/docs/PYTHON_FILES_MAP.md` è una mappa vecchia, ferma al 02/06 e
già marcata incompleta dal 27/08. Il suo posto lo prende questo catasto.

## Il percorso

Prima ciò che tocca **soldi e decisioni**, poi gli strumenti, poi la storia. Ritmo del piano:
2 componenti a settimana. Metodi di verifica: **spiegazione** (scrivi *con parole mie*, Claude
confronta con il codice), **quiz**, **guasto simulato** (Claude introduce un guasto realistico su
un branch e tu lo trovi).

| # | Componente | Perché a questo punto | Verifica |
|---|---|---|---|
| 0 | questa panoramica | la cornice di tutto il resto | spiegazione |
| 1 | ciclo di vita e gate | è la regola che decide cosa riceve capitale | spiegazione |
| 2 | stato canonico e DECISIONS | è dove nasceva il "mescola versioni" | guasto simulato |
| 3 | signal copier | gira in demo, domani con soldi veri | guasto simulato |
| 4 | EA e VPS | ciò che gira sul VPS lo si verifica in MT5, non nel repo | guasto simulato |
| 5 | segnali mentore | l'unico edge confermato: come è stato misurato | spiegazione |
| 6 | primitive di misura | le regole diventate codice (fill, baseline, dati, trial) | spiegazione + quiz |
| 7 | anatomia di uno studio | come si legge una qualsiasi cartella di `magazzino/registro/codice/` | spiegazione |
| 8 | catalogo delle famiglie | cosa è già stato provato, e perché non si riapre | quiz |
| 9 | conoscenza e intake | da dove entrano idee e fonti | spiegazione |
| 10 | Claude in trad | istruzioni, agenti, memoria | quiz |
| 11 | ambiente e test | come si lancia e come si controlla che funzioni | quiz |
| 12 | sistemi dormienti | cosa c'è ma non gira, e perché non va toccato a caso | quiz |
| 13 | investing | PAC e selettore archiviato | quiz |
| 14 | prop-lab e doppio binario | il simulatore prop e la regola dei due binari, arrivati il 06/10: [[14-prop-lab-e-doppio-binario]] | spiegazione |

**A che punto sei** non si scrive qui: sta nel campo `compreso` del frontmatter di ogni nota, e il
cruscotto (`decisioni/mappa/_cruscotto.base`, vista *Comprensione*) lo raccoglie da solo.

## Con parole mie

