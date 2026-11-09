# trad

Laboratorio di ricerca quant. Fornisce ai soci i **fondamenti tecnici** su cui poggia la ricerca di edge:
strumenti di lettura del prezzo, analizzati da quant (limiti, applicazioni, uso combinato) e consegnati come pacchetti.
Tiene il **metodo** con cui un'idea diventa una decisione, e il PAC. Obiettivo e ruoli: [PROJECT.md](PROJECT.md).

## Da leggere per primi

1. [PROJECT.md](PROJECT.md): obiettivo comune ai soci, ruoli, vincoli, macrostruttura.
2. [DECISIONS.md](DECISIONS.md): il registro delle decisioni. **La voce piu' recente vince**; controllalo prima di
   proporre qualcosa.
3. [docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md): come un'idea arriva a un verdetto, e quando muore.
4. [mappa/00-panoramica-trad.md](mappa/00-panoramica-trad.md): cosa fa ogni parte, come si usa, come si rompe.

## Dove stanno le cose oggi

La migrazione verso le cinque macro e' in corso, una macro alla volta (DECISIONS 2026-11-09): questa tabella si
aggiorna a ogni passo.

| Oggi | Cosa contiene | Va in |
|---|---|---|
| `DECISIONS.md`, `docs/trial_ledger.json`, `docs/BACKLOG_RICERCA.md`, `mappa/` | decisioni, contatore dei trial, backlog, mappa | `decisioni/` |
| `Da distillare/`, `fondamenti_tecnici/_INTAKE.md` | ingresso del materiale nuovo e suo smistamento | `decisioni/` |
| `core/`, `brokers/`, `notifiers/`, `tests/`, `config/`, `data/` | codice, test, configurazione, script dei dati | `motore/` |
| `docs/STRATEGY_LIFECYCLE.md`, `docs/QUANT_REVIEW_PROTOCOL.md`, `CONVENTIONS.md` | il metodo e le convenzioni | `motore/` |
| `fondamenti_tecnici/` (moduli `0X_*`), `TRADING_PRINCIPLES.md` | teoria | `magazzino/` |
| `fondamenti_tecnici/_sorgenti/`, `materiale_socio/` | fonti grezze, immutabili | `magazzino/` |
| `docs/*_PREREGISTRATION.md`, `docs/reviews/`, `analysis/<famiglia>/`, `strategies/{tsmom,meanrev,seasonality}/` | registro degli studi | `magazzino/` |
| `mql5/`, `signal_copier/`, `analysis/ops/`, `docs/health/`, `docs/INVESTING_PILLAR_PLAN.md`, `docs/PROP_FIRM_CRITERIA.md` | cio' che gira con soldi veri o in demo, e la sua sorveglianza | `esercizio/` |
| (nasce col primo pacchetto) | pacchetti per i soci | `uscita/` |
| `prop-lab/` | simulatore prop condiviso con un socio, tenuto allineato al suo repo | da decidere al passo dell'uscita |
| `strategies/{confluence_*,stock_selector,_base,_template}/`, `level_analyzer/`, `backtesters/`, `journals/`, `core/{runner,registry}.py`, documenti di architettura di maggio in `docs/` | sistemi dormienti | da decidere caso per caso |

Restano alla radice: `CLAUDE.md` e `.claude/` (istruzioni e agenti di Claude Code), `pyproject.toml`, `conftest.py`,
`.gitignore`, questo README e PROJECT.

## Comandi

```bash
python -m core.trial_ledger          # stato delle famiglie, trial e budget: l'unica fonte di questi numeri
python -m pytest core/tests          # test delle primitive di misura
```

## Regole che valgono ovunque

- **Nessun numero senza nota sorgente e data della misura.** Il contatore e `DECISIONS.md` puntano alle note.
- **Ogni test passa dal gatekeeper** (`.claude/agents/quant-gatekeeper.md`): prima di lanciarlo e prima del verdetto.
- **Ogni modifica di architettura** aggiorna la mappa e `mappa/_modifiche.md` nella stessa sessione.
- **Repo pubblico**: niente nomi, chat, orari, numeri di conto; credenziali (`.env`, `*.session`) mai lette o
  spostate.
