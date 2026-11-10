# trad

Laboratorio di ricerca quant. Fornisce ai soci i **fondamenti tecnici** su cui poggia la ricerca di edge:
strumenti di lettura del prezzo, analizzati da quant (limiti, applicazioni, uso combinato) e consegnati come pacchetti.
Tiene il **metodo** con cui un'idea diventa una decisione, e il PAC. Obiettivo e ruoli: [PROJECT.md](PROJECT.md).

## Da leggere per primi

1. [PROJECT.md](PROJECT.md): obiettivo comune ai soci, ruoli, vincoli, macrostruttura.
2. [DECISIONS.md](decisioni/DECISIONS.md): il registro delle decisioni. **La voce piu' recente vince**; controllalo prima di
   proporre qualcosa.
3. [motore/metodo/STRATEGY_LIFECYCLE.md](motore/metodo/STRATEGY_LIFECYCLE.md): come un'idea arriva a un verdetto, e quando muore.
4. [decisioni/mappa/00-panoramica-trad.md](decisioni/mappa/00-panoramica-trad.md): cosa fa ogni parte, come si usa, come si rompe.

## Dove stanno le cose

Cinque macro in ordine di processo (DECISIONS 2026-11-09), migrate fra il 09 e il 10/11. Il catasto file per file e'
nella [mappa](decisioni/mappa/00-panoramica-trad.md).

| Macro | Cosa contiene |
|---|---|
| [`decisioni/`](decisioni/README.md) | `DECISIONS.md`, contatore dei trial, backlog, mappa, ingresso (`Da distillare/`, `_INTAKE.md`) |
| [`motore/`](motore/README.md) | codice condiviso (`core/`, `brokers/`, `notifiers/`), test, `config/`, dati (`data/`, coi prezzi in `data/prezzi/` fuori da git), simulatore prop (`prop-lab/`), metodo (`metodo/`), `CONVENTIONS.md` |
| [`magazzino/`](magazzino/README.md) | teoria (`fondamenti_tecnici/`), fonti grezze (`fonti/`), registro degli studi (`registro/documenti/`, `registro/referti/`, `registro/codice/`), cio' che non gira (`dormienti/`) |
| [`esercizio/`](esercizio/README.md) | EA, copier, sorveglianza, PAC, criteri prop |
| [`uscita/`](uscita/README.md) | pacchetti per i soci, vuota fino al primo |

Ogni script trova la radice del repo cercando `pyproject.toml`, non contando le cartelle: spostarlo non lo rompe.

Restano alla radice: `CLAUDE.md` e `.claude/` (istruzioni e agenti di Claude Code), `pyproject.toml`, `conftest.py`,
`.gitignore`, questo README e PROJECT. Le cartelle locali fuori da git (`logs/`, `backtest_results/`, export e cloni
di terzi) restano dove sono.

## Comandi

```bash
python -m motore.core.trial_ledger          # stato delle famiglie, trial e budget (legge decisioni/trial_ledger.json)
python -m pytest motore/core/tests          # test delle primitive di misura
```

## Regole che valgono ovunque

- **Nessun numero senza nota sorgente e data della misura.** Il contatore e `decisioni/DECISIONS.md` puntano alle note.
- **Ogni test passa dal gatekeeper** (`.claude/agents/quant-gatekeeper.md`): prima di lanciarlo e prima del verdetto.
- **Ogni modifica di architettura** aggiorna la mappa e `decisioni/mappa/_modifiche.md` nella stessa sessione.
- **Repo pubblico**: niente nomi, chat, orari, numeri di conto; credenziali (`.env`, `*.session`) mai lette o
  spostate.
