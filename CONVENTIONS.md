# CONVENTIONS — Convenzioni di codice e progetto

Documento da leggere prima di scrivere codice in questo workspace.

## Linguaggio principale

- **Python 3.11+** per tutti i moduli core (strategie, broker, notifier, backtester, agent).
- **TypeScript** ammesso solo se imposto da un repo esistente (es. `dexter`, `worldmonitor`).
  Il bridge tra TS e Python passa per file (JSON/CSV) o HTTP.

## Stile codice Python

- **PEP 8** + **black** come formatter (line length 100).
- **Type hints obbligatori** su funzioni pubbliche e metodi di classe.
- **Docstring in italiano** stile Google su funzioni e classi pubbliche.
- **Commenti in italiano** per logica non ovvia. Per blocchi di logica matematica/finanziaria,
  spiegare il *perché* prima del *come*.
- **No logging "decorativo"**: log solo dove serve davvero (errori, decisioni di trading, esecuzione ordini).
- **Niente `print` in produzione**: usare `logging` configurato.

## Naming

- File: `snake_case.py`.
- Funzioni: `snake_case`.
- Classi: `PascalCase`.
- Costanti: `UPPER_SNAKE_CASE`.
- Variabili private: prefisso `_`.

## Pattern di estensione

### Nuova strategia

Una strategia = una cartella sotto `strategies/`:

```
strategies/<nome_strategia>/
├── strategy.py       # Classe che eredita da StrategyBase
├── config.yaml       # Parametri della strategia (size, soglie, timeframe)
└── README.md         # Cosa fa, ipotesi, riferimenti teorici
```

Vedi `strategies/_template/` per lo scaffold.

### Nuovo broker

Sottoclasse di `BrokerBase` in `brokers/<nome_broker>.py`. Implementa l'interfaccia minima
documentata in `brokers/base.py`.

### Nuovo notifier

Sottoclasse di `NotifierBase` in `notifiers/<canale>.py`. Vedi `notifiers/base.py`.

### Nuova skill (per Antigravity / Claude Code)

Cartella sotto `skills/<nome-skill>/` con un file `SKILL.md` che ha frontmatter standard:

```yaml
---
name: nome-skill
description: Descrizione di quando attivare la skill (per il dispatcher di Claude Code).
---

# Istruzioni in markdown
```

### Nuovo subagent / persona

File markdown in `agents/<categoria>/<nome>.md`. Il file è il system prompt dell'agente.
Convenzione: la prima sezione descrive l'identità (chi sei), la seconda il framework di analisi
(come pensi), la terza l'output atteso (formato risposta).

## Configurazione

- File `.env` per **chiavi API e segreti**. Mai committare. `.env.example` è committato come template.
- File `config/*.yaml` per **parametri non sensibili** (rischio, mercati abilitati, soglie).
- Niente valori magici nel codice — tutto referenziato dal config.

## Test

- `pytest` come framework.
- File in `tests/` con prefisso `test_`.
- Test minimo per ogni strategia: un caso con dati sintetici dove l'output atteso è noto.

## Git

- Commit message in italiano, breve descrizione + opzionale spiegazione del *perché*.
- Branch principale: `main`.
- Branch feature: `feat/<descrizione-breve>`.
- `.gitignore` esclude: `.env`, cache, output backtest, virtualenv, `__pycache__`, `.ipynb_checkpoints`.

## Sicurezza operativa (trading)

- **Mai** scrivere chiavi API hardcoded.
- **Mai** lanciare trade live senza un risk gate attivo.
- Ogni broker concrete deve avere un flag `paper_mode` che è il default; passare a `live_mode`
  richiede modifica esplicita del config + commit dedicato.
- Limite di drawdown massimo configurato in `config/risk.yaml` — la strategia si auto-disabilita
  se viene superato.

## Lingua dei deliverable

- Codice e docstring: italiano.
- Nomi di funzioni/classi/variabili: inglese (convenzione tecnica universale).
- README di cartella: italiano.
- Output utente (notifiche Telegram, log critici): italiano.
