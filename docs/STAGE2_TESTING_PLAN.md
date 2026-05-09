# Stage 2 + 2.5 — Piano di testing operativo (ARCHIVIATO 2026-05-05)

> ⚠️ **Documento superato dal pivot 2026-05-05**.
> Riferimento operativo corrente: [ARCHITECTURE_v2.md](ARCHITECTURE_v2.md).
> Questo file resta come storico delle decisioni pre-pivot (architettura monolite Python+MT5 desktop).
> Le sezioni "criteri Fase A → Fase B" non sono più rilevanti perché la Confluence è stata
> definitivamente classificata come solo-notifica.

# Stage 2 + 2.5 — Piano di testing operativo

> **Per chi torna qui dopo qualche giorno**: questo documento è la fonte di verità per ricostruire il contesto. Non riassume il codice (lo trovi in `*/README.md`), ma elenca **cosa testare**, **come testarlo**, e **cosa registrare** per il perfezionamento. Aggiornato: 2026-05-03.

---

## 1. Inventario di ciò che è stato costruito

### 1.1 Componenti trasversali

| Componente | Path | Stato |
|---|---|---|
| Tipi base strategie | [strategies/_base.py](../strategies/_base.py) | Pronto. `Signal`, `DataRequirement`, `PositionUpdate`, `StrategyBase`, adapter `to_trading_signal` / `to_order`. |
| Risk gate | [core/risk_gate.py](../core/risk_gate.py) | Pronto. `PortfolioState`, `validate_signal`, 8 regole da `config/risk.yaml`. |
| Orchestrator generico | [core/runner.py](../core/runner.py), [core/registry.py](../core/registry.py) | Pronto. CLI `python -m core.runner run --strategy <name>`. Registra entrambe le strategie. |
| Notifier Telegram | [notifiers/telegram.py](../notifiers/telegram.py) | Pronto. Outbound only via `requests`. Retry 1/3/9s. Log su `logs/telegram.log`. |
| Tabella pip | [notifiers/_pip_table.py](../notifiers/_pip_table.py) | Pronto. EUR/GBP/USDJPY/XAU/indici/BTC/ETH. |
| Broker MT5 | [brokers/mt5.py](../brokers/mt5.py) | Pronto. `connect/disconnect/get_market_data/get_position/place_order/close_position/modify_position`. **Mai testato live, solo unit test importabilità**. |

### 1.2 Strategie

| Strategia | Cartella | Tipo | Asset | Demo MT5 | Stato test offline |
|---|---|---|---|---|---|
| **Stock Selector V6.0** | [strategies/stock_selector/](../strategies/stock_selector/) | Headless screening | SP500 | n/a (yfinance) | 13/13 verdi |
| **Confluence Levels** | [strategies/confluence_levels/](../strategies/confluence_levels/) | Semiautomatica (notifica) | EURUSD, XAUUSD | DEMO1 (AvaTrade) | 24/24 verdi |
| **London Open Breakout** | [strategies/london_breakout/](../strategies/london_breakout/) | Automatica | GBPUSD | DEMO2 (MetaQuotes) | 16/16 verdi |

**Totale test offline: 88/88 verdi.**

### 1.3 Configurazione operativa

| Path | Cosa contiene | Da modificare quando |
|---|---|---|
| [.env](../.env) | Token Telegram, login MT5 DEMO1+DEMO2, API Alpaca, Binance/Bybit testnet | Se cambi broker o token |
| [config/risk.yaml](../config/risk.yaml) | Limiti rischio globali (DD, max position, RR min, cooldown) | Se vuoi essere più/meno aggressivo |
| [config/markets.yaml](../config/markets.yaml) | Mercati abilitati per scopo | Se cambi simboli di default |
| [strategies/confluence_levels/config.yaml](../strategies/confluence_levels/config.yaml) | Flag mode (notify/auto/BE), soglie pip, sessione, news block | Quando attivi Fase B/C/D |
| [strategies/confluence_levels/levels.yaml](../strategies/confluence_levels/levels.yaml) | **Input umano settimanale**: livelli S/R + S/D + Fib | **Ogni weekend** |
| [strategies/london_breakout/config.yaml](../strategies/london_breakout/config.yaml) | Range Asia, finestre, ATR multiplier, FOMC blacklist | Quando aggiorni date FOMC o cambi simboli |
| [data/news_calendar.csv](../data/news_calendar.csv) | Stub vuoto (header only) | A mano se vuoi testare il filtro news prima di Stage 5 |

---

## 2. Cosa va testato (in ordine di priorità)

### Priorità 1 — Confluence Levels (DEMO1 AvaTrade)

#### Setup pre-run (una tantum)

- [ ] MetaTrader 5 desktop installato e loggato sul demo AvaTrade (login 107054945, server `Ava-Demo 1-MT5`).
- [ ] Verifica visivamente che EURUSD e XAUUSD siano nel Market Watch del terminale MT5.
- [ ] Compila [strategies/confluence_levels/levels.yaml](../strategies/confluence_levels/levels.yaml) con la mappa dei livelli reali della settimana corrente. Vedi il formato in [levels.example.yaml](../strategies/confluence_levels/levels.example.yaml).
- [ ] Esegui `python -m strategies.confluence_levels validate-levels` → tabella deve mostrare livelli accettati senza errori.
- [ ] Esegui `python -m strategies.confluence_levels dry-run --symbol EURUSD --price <prezzo_attuale>` → verifica che la decisione mostrata sia coerente con quello che ti aspetti.

#### Run live (settimana di test)

- [ ] Comando: `python -m strategies.confluence_levels run --account DEMO1`
- [ ] Lascia girare almeno 5 giorni di trading (lun-ven), terminale MT5 sempre aperto.
- [ ] Tieni d'occhio Telegram per le notifiche di prossimità.

#### Cose da osservare e annotare

| Variabile | Cosa annotare | Dove cercare |
|---|---|---|
| **Numero notifiche totali** | Quante notifiche di prossimità sono arrivate | `logs/telegram.log`, `data/notifications_sent.json` |
| **Livelli attivati** | Quali ID livello hanno triggerato (e quante volte ognuno) | `data/notifications_sent.json` |
| **Falsi positivi di filtro** | Notifica arrivata per un livello già invalidato dal prezzo | log + memoria visiva del grafico |
| **Falsi negativi di filtro** | Prezzo è entrato nella zona ma niente notifica | confronto manuale TradingView vs `logs/runner_confluence_levels.log` |
| **Crash del runner** | Eccezioni non gestite | log Python + status del processo |
| **Latenza notifica → reazione prezzo** | Quanti minuti dopo la notifica il prezzo si è effettivamente girato? | timestamp Telegram + grafico |
| **Quanti dei segnali avresti piazzato manualmente** | Soggettiva ma fondamentale | tieni un foglio di carta o file `notes/confluence_week1.md` |

#### Criteri di passaggio Fase A → Fase B (auto_place_pending)

Definiti in [strategies/confluence_levels/README.md](../strategies/confluence_levels/README.md):

- [ ] Almeno **5 notifiche di prossimità** arrivate correttamente.
- [ ] Almeno **3 setup** che avresti piazzato a mano (giudizio tuo).
- [ ] **Zero falsi positivi di filtro** (skip ingiustificati).
- [ ] **Zero crash** del runner.

Se tutti soddisfatti → si può attivare `auto_place_pending: true` in `config.yaml`. **NON attivare prima**.

---

### Priorità 2 — London Open Breakout (DEMO2 MetaQuotes)

#### Setup pre-run (una tantum)

- [ ] Apri **un secondo terminale MetaTrader 5** sul demo MetaQuotes (login 5050007154, server `MetaQuotes-Demo`).
- [ ] Aggiungi GBPUSD al Market Watch.
- [ ] Verifica spread M15 su GBPUSD: dovrebbe essere ≤ 1.5 pip in sessione London. Se è > 5 pip costantemente, MetaQuotes-Demo non va bene → apri un secondo demo Ava.
- [ ] Esegui `python -m strategies.london_breakout dry-run` → mostra finestra entry, blackout day, simboli.

#### Run live (settimana di test)

- [ ] Comando: `python -m strategies.london_breakout run --account DEMO2`
- [ ] Lascia girare per 5 giorni di trading (lun-ven).
- [ ] **Importante**: il primo evento utile è alle 07:00 UTC = **09:00 ora italiana**. Avvia il runner prima di quell'orario.

#### Cose da osservare e annotare

| Variabile | Cosa annotare | Dove cercare |
|---|---|---|
| **Range Asia rilevato** | High e low calcolati dal runner ogni giorno alle 07:00 UTC | log + screen MT5 |
| **Stop orders piazzati** | Confermare che i due ordini compaiono sulla piattaforma alle 07:00 | tab "Trade" del terminale MT5 |
| **Quale dei due si filla** | Long, short o nessuno (range troppo stretto / troppo largo) | log + tab "History" |
| **L'altro viene cancellato** | Quando uno fila, l'altro deve sparire entro il polling successivo | tab "Trade" |
| **Cancellazione alle 10:00 UTC** | Se nessuno fila, entrambi vengono cancellati alle 12:00 ora italiana | tab "Trade" |
| **Time stop alle 16:00 UTC** | Posizione aperta chiusa automaticamente alle 18:00 ora italiana | tab "History" |
| **Skip per blackout NFP/FOMC** | Verifica venerdì 2026-05-01 (NFP) e mercoledì 2026-05-13 (FOMC) | log + Telegram |
| **Skip per range esaurito** | Notifica `⏭ skip` quando range Asia > 1.5·ATR | Telegram |
| **Esito di ogni trade** | TP raggiunto / SL toccato / time stop / partial | log + History MT5 |

#### Criteri di completamento Stage 2.5

Definiti in [strategies/london_breakout/README.md](../strategies/london_breakout/README.md):

- [ ] Almeno **3-5 trade eseguiti** in 1 settimana (frequenza attesa ~15-20/mese).
- [ ] Win rate 45-55% (3-5 trade non basta per statistica robusta, ma orientativo).
- [ ] **Zero stop orders rimasti orfani** dopo le 10:00 UTC.
- [ ] **Zero crash** del runner.

---

### Priorità 3 — Stress test infrastrutturale

Da fare in parallelo durante la settimana, non bloccante:

- [ ] **Telegram retry**: stacca temporaneamente il wifi mentre il runner sta per inviare. Verifica che dopo 3 tentativi non blocchi il loop.
- [ ] **Riavvio runner**: ferma con Ctrl-C, riavvia. Verifica che `data/notifications_sent.json` e `data/london_breakout_state.json` vengano riletti e non si rimandino notifiche già inviate.
- [ ] **MT5 disconnesso**: chiudi il terminale MT5 mentre il runner gira. Verifica messaggio di errore pulito (no traceback infinito).
- [ ] **`levels.yaml` modificato a metà settimana**: aggiungi un livello, verifica che venga preso al ciclo successivo (~60s).
- [ ] **Risk gate**: forza una violazione (es. metti `max_open_positions: 0` in `risk.yaml`) e verifica che il sistema mandi messaggio di skip senza piazzare.

---

## 3. Workflow operativo settimanale

### Domenica sera o lunedì mattina presto

1. **Analisi top-down EURUSD/XAUUSD** → segna livelli su TradingView.
2. **Compila** [strategies/confluence_levels/levels.yaml](../strategies/confluence_levels/levels.yaml) (vedi formato in `levels.example.yaml`).
3. `python -m strategies.confluence_levels validate-levels` → controlla che sia tutto verde.
4. **Aggiorna FOMC dates** in [strategies/london_breakout/config.yaml](../strategies/london_breakout/config.yaml) se ci sono nuove date confermate per il mese.
5. Apri **due terminali MT5** (DEMO1 Ava + DEMO2 MetaQuotes), entrambi loggati e con simboli nel Market Watch.

### Lunedì 08:55 ora italiana

6. Apri due shell PowerShell:
   ```
   # Shell 1
   python -m strategies.confluence_levels run --account DEMO1

   # Shell 2
   python -m strategies.london_breakout run --account DEMO2
   ```
7. Verifica messaggio Telegram di avvio in entrambi.

### Durante la settimana

8. Annota osservazioni in un file `notes/week_<N>.md` (vedi template sezione 5).
9. Se aggiungi/modifichi livelli weekly: salva e basta, il runner ricarica entro 60s.

### Venerdì sera

10. `Ctrl-C` su entrambi i runner.
11. Compila il **report settimanale** (template sezione 5) con i numeri raccolti.
12. Decidi:
    - Confluence: criteri Fase A → B soddisfatti? Se sì, programma l'attivazione di `auto_place_pending`.
    - London Breakout: trade plausibili? Win rate orientativo?
    - Bug/comportamenti strani: lista issues per la sessione di lavoro successiva.

---

## 4. Matrice delle decisioni (cosa attivare quando)

| Flag | File | Default | Quando attivare |
|---|---|---|---|
| `notify_on_proximity` | confluence_levels/config.yaml | `true` | Sempre (è la Fase A). |
| `auto_place_pending` | confluence_levels/config.yaml | `false` | Dopo Fase A validata: 5+ notifiche, 3+ setup giusti, zero falsi positivi. |
| `require_telegram_confirm` | confluence_levels/config.yaml | `false` | Stage 5+ (richiede polling Telegram per i bottoni inline). |
| `auto_be_management` | confluence_levels/config.yaml | `false` | Dopo Fase B validata: posizioni piazzate automaticamente vanno a +1R con regolarità. |
| `skip_nfp` | london_breakout/config.yaml | `true` | Sempre on a meno di test specifici sul comportamento NFP. |

---

## 5. Template note settimanali

Crea `notes/week_YYYY-MM-DD.md` ogni venerdì sera. Suggerimento:

```markdown
# Settimana <data>

## Confluence Levels (DEMO1)

### Numeri grezzi
- Notifiche totali: <N>
- Livelli attivati: <id1>, <id2>, ...
- Setup che avrei piazzato a mano: <N>
- Falsi positivi di filtro: <N>
- Crash runner: <N>

### Osservazioni qualitative
- ...

## London Breakout (DEMO2)

### Numeri grezzi
- Giorni operativi: <N>
- Trade aperti: <N>
- Win rate: <N>/<tot>
- Trade chiusi via SL / TP / time stop: <a>/<b>/<c>
- Skip per blackout: <N>
- Skip per range esaurito: <N>

### Osservazioni qualitative
- ...

## Issues / bug riscontrati
- ...

## Decisioni per la settimana prossima
- [ ] Attivare flag X?
- [ ] Modificare config Y?
- [ ] Aggiungere/rimuovere livelli?
```

---

## 6. Comandi cheatsheet

```bash
# Verifica setup
python -m pytest tests/                                    # 88/88 dovrebbero passare
python -m core.runner list                                 # mostra strategie disponibili

# Confluence Levels
python -m strategies.confluence_levels validate-levels
python -m strategies.confluence_levels dry-run --symbol EURUSD --price 1.08600
python -m strategies.confluence_levels run --account DEMO1
python -m strategies.confluence_levels run --account DEMO1 --once    # singola passata

# London Breakout
python -m strategies.london_breakout dry-run               # check finestre + blackout day
python -m strategies.london_breakout run --account DEMO2
python -m strategies.london_breakout run --account DEMO2 --once

# Equivalenti via orchestrator generico
python -m core.runner run --strategy confluence_levels --account DEMO1
python -m core.runner run --strategy london_breakout --account DEMO2

# Logs
type logs\telegram.log                                     # ultime righe Telegram
type logs\runner_confluence_levels.log                     # se creato dal logger
```

---

## 7. Punti aperti (non bloccanti, da affrontare al ritorno)

### Bug noti / minori
- `_template/strategy.py` ha hint "unused parameter" sui metodi non implementati. Voluto, è un template — ignorabile.
- `tests/test_risk_gate.py` usa `datetime.utcnow()` deprecated in Python 3.12 (warning, non error). Da sistemare in passaggio successivo.
- Il `CronCreate` schedulato per il 9 maggio 19:23 ora italiana è **session-only**: se chiudi Claude Code prima, il job muore. Per renderlo durable serve `durable: true` (modifica `.claude/scheduled_tasks.json`).

### Feature pending
- **News calendar dinamico**: `data/news_calendar.csv` è stub vuoto. Stage 5 → integrazione worldmonitor.
- **Comandi bot Telegram inline** (`/status`, `/disable`, conferma pending): Stage 5+ con `python-telegram-bot` polling.
- **Portfolio aggregato cross-broker**: `PortfolioState.from_brokers` esiste ma il runner Confluence interroga solo `[broker]` singolo. Stage 6 quando entreranno ccxt + MT5 in parallelo.
- **Backtest delle due strategie**: Stage 3. Per ora abbiamo solo test unitari.
- **Modifica SL→BE Confluence**: `manage_position` è cablata ma il runner Confluence chiama `broker.modify_position` solo se `auto_be_management=true`. Da testare quando si attiva la Fase D.

### Configurazione da rivedere periodicamente
- `fomc_blackout_dates` in `london_breakout/config.yaml`: le date 2026 sono manuali, vanno aggiornate ogni mese in base ai comunicati FED ufficiali.
- `risk.yaml` `max_size_per_trade_pct: 0.02`: per i due demo è prudente. Per prop firm Stage 7 andrà ridotto a 0.005 o 0.01.

### Backlog strategie (vedi memoria `project_strategies_pipeline.md`)
1. Time Series Momentum su USDJPY D1 (Moskowitz-Ooi-Pedersen 2012)
2. Volatility Targeting overlay (Harvey et al. 2018) — applicabile a tutte
3. Donchian/Turtle (Faith 2007)
4. Cross-asset DXY → EURUSD z-score
5. Mean Reversion intraday EURUSD
6. KAMA + ATR breakout filter
7. Carry Trade sistematico (deprioritized 2026)

Plus Donchian BTC su Binance testnet (Stage 6).

---

## 8. Quando tornerai qui

Apri questo file e in ordine:

1. Leggi sezione 2 → vedi cosa hai testato e cosa no.
2. Apri `notes/week_<ultima data>.md` se l'hai compilato → ti dà i numeri grezzi.
3. Sezione 4 → decidi se attivare il prossimo flag.
4. Se ti ricordi di un comportamento strano: Sezione 7 punti aperti, oppure aggiungi alla lista.
5. Per il prossimo cycle di sviluppo: pesca dalla memoria `project_strategies_pipeline.md` la prossima strategia in lista.

Niente di fondamentale è "in testa": tutto è in file che sopravvivono alla chiusura della sessione.
