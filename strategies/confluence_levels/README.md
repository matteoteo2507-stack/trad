# Strategia — Confluence Levels Trader

Strategia **semiautomatica** che monitora la prossimità del prezzo a livelli operativi
identificati a mano dall'utente nel weekend (S/R + S/D + Fibonacci in confluenza).

Asset target Stage 2: **EURUSD**, **XAUUSD** su MT5 demo AvaTrade.

## Fasi progressive (testing graduale)

Tutte controllate da flag in `config.yaml` → sezione `mode`:

| Fase | Flag | Cosa fa |
|---|---|---|
| **A** (default ON) | `notify_on_proximity` | Quando il prezzo entra entro `proximity_alert_pips` da un livello, manda notifica Telegram. L'utente decide se piazzare. |
| **B** | `auto_place_pending` | Il sistema piazza buy_limit/sell_limit su MT5 secondo le regole. Si attiva DOPO che la Fase A ha mostrato segnali plausibili. |
| **C** | `require_telegram_confirm` | Conferma da Telegram (bottoni inline) prima di piazzare. Richiede polling Telegram → Stage 5. |
| **D** | `auto_be_management` | Sposta SL→BE quando il trade raggiunge +1R. Si attiva DOPO la Fase B. |

**Default conservativo**: solo Fase A. I flag B/C/D sono `false` finché Matteo non li attiva esplicitamente.

## Workflow settimanale

1. **Weekend** (45-60min): analisi top-down (Monthly → Weekly → H4/H1) per identificare 2-4 livelli per pair.
2. Compila `levels.yaml` (vedi `levels.example.yaml` come template). **Il file è gitignored.**
3. Avvia il runner: `python -m strategies.confluence_levels run --account DEMO1`.
4. Durante la settimana, ricevi notifiche Telegram quando un livello viene avvicinato.
5. Decidi se piazzare manualmente (Fase A) o lascia fare al sistema (Fase B/C/D).

## Filtri operativi

Tutti configurabili in `config.yaml`:

- **Sessione operativa Roma**: 09:00–18:00 (modificabile).
- **News block**: skip se evento `high impact` entro `news_block_minutes` (default 30min). Stub Stage 2 — file `data/news_calendar.csv` editato a mano. Stage 5 → integrazione worldmonitor.
- **RR minimo**: 1:3 (oltre al risk gate globale `config/risk.yaml`).
- **SL massimo per simbolo**: 30 pip EURUSD, 200 pip XAUUSD.
- **Dedup**: una notifica per livello per giorno UTC.

## CLI

```bash
# Valida levels.yaml (mostra warning su scaduti, RR insufficiente, ecc.)
python -m strategies.confluence_levels validate-levels

# Simula a un prezzo dato (niente broker, niente Telegram)
python -m strategies.confluence_levels dry-run --symbol EURUSD --price 1.08600

# Avvia polling loop (richiede MT5 demo aperto + .env compilato)
python -m strategies.confluence_levels run --account DEMO1

# Una sola passata (utile per cron)
python -m strategies.confluence_levels run --once
```

## Struttura

| File | Ruolo |
|---|---|
| `strategy.py` | `ConfluenceLevelsStrategy` — `evaluate_symbol`, filtri, signal building, BE management. |
| `runner.py` | Polling loop, gestione notifiche/pending/BE, persistenza stato. |
| `levels_loader.py` | Parse + validazione `levels.yaml`. |
| `news_filter.py` | Stub news calendar (CSV → True/False). |
| `config.yaml` | Tutti i parametri. Niente valori magici nel codice. |
| `levels.example.yaml` | Template per `levels.yaml`. |
| `__main__.py` | CLI Typer. |

## Test

`tests/test_confluence_strategy.py`, `tests/test_levels_loader.py`, `tests/test_news_filter.py`.
Tutti **offline**: niente MT5/Telegram reali.

## Criterio di completamento Fase A (Stage 2)

- 1 settimana di run sul demo AvaTrade.
- Almeno **5 segnali plausibili** recapitati via Telegram.
- Zero crash del runner.
- Zero falsi positivi di filtro (skip ingiustificati).

Solo dopo si attiva la Fase B (`auto_place_pending: true`).

## Riferimenti

- Skill: `skills/strategy-designer/SKILL.md` (workflow di design).
- Skill: `skills/telegram-notifier/SKILL.md` (template messaggio).
- Risk gate condiviso: `core/risk_gate.py`.
- Stage 2 della roadmap: `ROADMAP.md`.
