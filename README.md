# trad

Laboratorio di ricerca quant. Fornisce ai soci i **fondamenti tecnici** su cui poggia la ricerca di edge:
strumenti di lettura del prezzo, analizzati da quant (limiti, applicazioni, uso combinato) e consegnati come pacchetti.
Tiene il **metodo** con cui un'idea diventa una decisione, e il PAC. Obiettivo e ruoli: [PROJECT.md](PROJECT.md).

## Da leggere per primi

1. [PROJECT.md](PROJECT.md): obiettivo comune ai soci, ruoli, vincoli, macrostruttura.
2. [DECISIONS.md](decisioni/DECISIONS.md): il registro delle decisioni. **La voce piu' recente vince**; controllalo prima di
   proporre qualcosa.
3. [docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md): come un'idea arriva a un verdetto, e quando muore.
4. [decisioni/mappa/00-panoramica-trad.md](decisioni/mappa/00-panoramica-trad.md): cosa fa ogni parte, come si usa, come si rompe.

## Dove stanno le cose oggi

La migrazione verso le cinque macro e' in corso, una macro alla volta (DECISIONS 2026-11-09): questa tabella si
aggiorna a ogni passo.

| Oggi | Cosa contiene | Va in |
|---|---|---|
| [`decisioni/`](decisioni/README.md) | **migrata il 09/11**: `DECISIONS.md`, contatore dei trial, backlog, mappa, ingresso (`Da distillare/`, `_INTAKE.md`) | fatto |
| [`magazzino/`](magazzino/README.md) | **documenti migrati il 10/11**: teoria (`fondamenti_tecnici/`, con `TRADING_PRINCIPLES.md`), fonti grezze (`fonti/`), registro degli studi (`registro/documenti/`, `registro/referti/`), documenti dormienti (`dormienti/`) | fatto |
| [`esercizio/`](esercizio/README.md) | **migrata il 09/11**: EA, copier, sorveglianza, PAC, criteri prop | fatto |
| [`uscita/`](uscita/README.md) | **creata il 09/11**: pacchetti per i soci, vuota fino al primo | fatto |
| `core/`, `brokers/`, `notifiers/`, `tests/`, `config/`, `data/`, `prop-lab/` | codice, test, configurazione, script dei dati, simulatore prop | `motore/` (gia' li': `motore/riordino/sposta.py`) |
| `docs/STRATEGY_LIFECYCLE.md`, `docs/QUANT_REVIEW_PROTOCOL.md`, `CONVENTIONS.md` | il metodo e le convenzioni | `motore/` |
| `analysis/` (codice degli studi), `strategies/{tsmom,meanrev,seasonality}/` | codice del registro | `magazzino/registro/` col passo del motore |
| `strategies/{confluence_*,stock_selector,_base,_template}/`, `level_analyzer/`, `backtesters/`, `core/{runner,registry}.py` | codice dormiente | `magazzino/dormienti/` col passo del motore |

Il codice si sposta tutto insieme nel passo del motore: prima ogni script trova la radice del repo cercando
`pyproject.toml` invece di contare le cartelle, cosi' spostarlo non lo rompe.

Restano alla radice: `CLAUDE.md` e `.claude/` (istruzioni e agenti di Claude Code), `pyproject.toml`, `conftest.py`,
`.gitignore`, questo README e PROJECT.

## Comandi

```bash
python -m core.trial_ledger          # stato delle famiglie, trial e budget (legge decisioni/trial_ledger.json)
python -m pytest core/tests          # test delle primitive di misura
```

## Regole che valgono ovunque

- **Nessun numero senza nota sorgente e data della misura.** Il contatore e `decisioni/DECISIONS.md` puntano alle note.
- **Ogni test passa dal gatekeeper** (`.claude/agents/quant-gatekeeper.md`): prima di lanciarlo e prima del verdetto.
- **Ogni modifica di architettura** aggiorna la mappa e `decisioni/mappa/_modifiche.md` nella stessa sessione.
- **Repo pubblico**: niente nomi, chat, orari, numeri di conto; credenziali (`.env`, `*.session`) mai lette o
  spostate.
