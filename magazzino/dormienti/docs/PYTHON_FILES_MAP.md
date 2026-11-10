# Mappa file Python del workspace

> ## ⚠️ INCOMPLETO — verificato 2026-08-27
>
> Dichiara di coprire **ogni** file `.py`, ma e' fermo al 2026-06-02. Mancano almeno:
> `magazzino/registro/codice/intake/`, `magazzino/registro/codice/trend/`, `magazzino/registro/codice/nxt/{excursion,stops,weekend}.py`,
> `esercizio/sorveglianza/weekly_healthcheck.py`, `magazzino/registro/codice/mentor_signals/oos_validation.py`.
> Usalo per orientarti sul vecchio, **non** come inventario.

> Spiegazione one-liner di OGNI file `.py`. Quando torni qui dopo giorni, parti da questo file per orientarti.

## 🎯 File "ENTRY POINT" (lanciati da CLI)

Sono i comandi che lanci tu. Sotto a ciascuno trovi tutta la catena di import.

| Comando | File | Cosa fa |
|---|---|---|
| `python -m magazzino.dormienti.strategies.confluence_levels run` | `magazzino/dormienti/strategies/confluence_levels/__main__.py` | Avvia il runner Confluence |
| `python -m magazzino.dormienti.strategies.confluence_levels validate-levels` | (idem) | Valida `levels.yaml` |
| `python -m magazzino.dormienti.strategies.confluence_levels dry-run` | (idem) | Simula a un prezzo dato |
| `python -m magazzino.dormienti.strategies.stock_selector --risk-free 4.2 --liquidity decreasing` | `magazzino/dormienti/strategies/stock_selector/__main__.py` | Genera Top_Picks.xlsx + Analisi_Completa.xlsx + Sell_Signals.xlsx (diff vs run precedente) |
| `python -m magazzino.dormienti.orchestratore.runner run --strategy ...` | `magazzino/dormienti/orchestratore/runner.py` | Orchestrator generico (alternative al CLI specifico) |
| `python -m pytest motore/tests/` | `conftest.py` (auto) + `motore/tests/test_*.py` | Esegue tutti i test offline |

Tutto il resto sono **moduli importati** da questi entry point. Non li lanci tu.

---

## 📦 Strategie

### `motore/core/strategia_base.py` — fondazione condivisa
Tipi e classi base che ogni strategia eredita. **Lo importano tutte le strategie.**
- `Signal`: dataclass del segnale di trading (direction, size, sl, tp, confidence, note).
- `DataRequirement`: cosa serve dal data layer.
- `PositionUpdate`: modifica SL/TP (per BE management futuro).
- `StrategyBase` (ABC): interfaccia astratta con `should_enter`, `should_exit`, `manage_position`.
- Adapter: `Signal.to_trading_signal()` (per Telegram), `Signal.to_order()` (per broker).

### `magazzino/dormienti/strategies/_template/strategy.py` — scaffold
Template vuoto da copiare quando crei una nuova strategia. Non eseguito mai a runtime.

### `magazzino/dormienti/strategies/confluence_levels/`
La **strategia operativa** che gira H24 sul VPS. Solo notifica.

| File | Cosa fa |
|---|---|
| `__init__.py` | Lazy export di `ConfluenceLevelsStrategy`. |
| `__main__.py` | **Entry point CLI** (`run`, `validate-levels`, `dry-run`). |
| `strategy.py` | Classe `ConfluenceLevelsStrategy`: valuta i livelli vs prezzo corrente, applica filtri (sessione, news, RR, SL max, dedup), genera `Signal`. |
| `levels_loader.py` | Parsing + validazione di `levels.yaml`. Scarta livelli scaduti, warna su confluenze < 2. |
| `news_filter.py` | Filtro news basato su `motore/data/news_calendar.csv`. Stub vuoto fino a Stage 5. |
| `runner.py` | **Loop di polling** (default 60s): orchestratore che usa il broker per i prezzi, la strategy per la valutazione, il notifier per Telegram, e persiste lo stato in `motore/data/notifications_sent.json`. |

### `magazzino/dormienti/strategies/stock_selector/`
Tool **weekend** per generare top picks SP500. Lanciato a mano (o da cron).

| File | Cosa fa |
|---|---|
| `__init__.py` | Re-export pigro. |
| `__main__.py` | **Entry point CLI**. Tasso risk-free e trend liquidità da CLI. |
| `strategy.py` | Classe `StockSelector`: orchestratore che scarica SP500, calcola scoring, esporta Excel. |
| `scoring.py` | Logica pura: scenario macro, score fundamentale 0-6, RRG, match scenario. Tutti i tipi Pydantic (`StockPick`, `SelectionResult`, `MacroScenario`, `RRGStatus`). |
| `data_sources.py` | Fetch lista SP500 da GitHub Datasets, download storici e info via `yfinance`. |

---

## 🏗 Core (componenti trasversali)

| File | Cosa fa |
|---|---|
| `motore/core/__init__.py` | Marker package. |
| `motore/core/risk_gate.py` | `PortfolioState` + `validate_signal`: regole rischio da `motore/config/risk.yaml`. **Dormiente** post-pivot perché Confluence non piazza ordini. Resta utilizzabile se in futuro arriveranno strategie Python con esecuzione. |
| `magazzino/dormienti/orchestratore/runner.py` | Orchestrator generico (factory broker yfinance/MT5 + delega ai runner specifici). |
| `magazzino/dormienti/orchestratore/registry.py` | Registry strategie disponibili. Attualmente solo `confluence_levels`. |

---

## 📡 Brokers (data source / esecuzione)

Tutti ereditano da `motore/brokers/base.py`.

| File | Cosa fa | Stato |
|---|---|---|
| `motore/brokers/base.py` | `BrokerBase` (ABC) + dataclass `Order`, `BrokerPosition`, `BrokerInfo`. | **In uso** (interfaccia condivisa). |
| `motore/brokers/yfinance_data.py` | **Broker read-only** via yfinance. Usato dalla Confluence sul VPS. `place_order` solleva eccezione (è solo dati). | **In uso** (default Confluence). |
| `motore/brokers/mt5.py` | Broker MT5 desktop (richiede terminale aperto su Windows). | **Legacy** (per `--datasource mt5` opzionale). Non usato in produzione. |
| `motore/brokers/ibkr.py` | Stub Interactive Brokers, non implementato. | **Stub futuro**. |
| `motore/brokers/binance.py` | Stub Binance ccxt. | **Stub Stage 6**. |
| `motore/brokers/coinbase.py` | Stub Coinbase. | **Stub futuro** (decisione 2026-05: deprioritizzato, no sandbox API). |

---

## 🔔 Notifiers (canali in uscita)

| File | Cosa fa | Stato |
|---|---|---|
| `motore/notifiers/base.py` | `NotifierBase` (ABC) + `TradingSignal` dataclass. | **In uso**. |
| `motore/notifiers/telegram.py` | Implementazione Telegram outbound via `requests` (HTTP POST a Bot API). Retry 1/3/9s, log su `logs/telegram.log`. | **In uso**. |
| `motore/notifiers/_pip_table.py` | Tabella pip-size per simbolo (EUR=0.0001, XAU=0.01, BTC=1.0, ecc.). Usato dal formatter Telegram. | **In uso**. |

---

## 📊 Backtesters (Stage 3, futuri)

| File | Cosa fa | Stato |
|---|---|---|
| `magazzino/dormienti/backtesters/base.py` | Interfaccia astratta. | **Stub Stage 3**. Per il forex il Strategy Tester MT5 sostituisce questa cartella. Da implementare quando arriverà una strategia Python da backtestare. |

---

## 🧪 Test (offline)

Tutti girano in 2-3 secondi con `python -m pytest motore/tests/`. **NON** richiedono broker reali, MT5 desktop, Telegram, internet (eccetto i 2 test live yfinance opt-in).

| File | Cosa testa |
|---|---|
| `motore/tests/test_signal_adapters.py` | `Signal.to_trading_signal` e `to_order`. |
| `motore/tests/test_risk_gate.py` | Tutte le regole risk gate (drawdown, max position, RR, cooldown). |
| `motore/tests/test_levels_loader.py` | Parse YAML, validazione livelli scaduti/malformati. |
| `motore/tests/test_news_filter.py` | CSV vuoto, evento high impact in finestra. |
| `motore/tests/test_confluence_strategy.py` | Filtri Confluence (proximity, sessione, news, RR, SL max, dedup, manage_position default). |
| `motore/tests/test_pip_table.py` | Pip calc EUR/XAU/USD/JPY. |
| `motore/tests/test_telegram_format.py` | Format messaggi mock-mockato (no rete). |
| `motore/tests/test_yfinance_broker.py` | Mapping ticker, timeframe, errori. 2 test live opt-in (richiedono rete). |
| `motore/tests/test_stock_selector_scoring.py` | Scoring fondamentale, scenario macro, RRG. |
| `conftest.py` | Aggiunge la root del workspace a `sys.path` (prerequisito per gli import). |

---

## 🗂 Struttura visuale

```
trad/
├── magazzino/dormienti/strategies/
│   ├── _base.py                    ← fondazione (Signal, StrategyBase)
│   ├── _template/                  ← scaffold per nuove strategie
│   ├── confluence_levels/          ← OPERATIVA (gira H24 su VPS)
│   │   ├── __main__.py             ← entry point CLI
│   │   ├── strategy.py             ← logica filtri/proximity
│   │   ├── runner.py               ← polling loop
│   │   ├── levels_loader.py        ← parse levels.yaml
│   │   ├── news_filter.py          ← filtro news
│   │   ├── config.yaml             ← parametri (no codice)
│   │   ├── levels.yaml             ← INPUT UMANO weekly (gitignored)
│   │   └── levels.example.yaml     ← template committato
│   └── stock_selector/             ← TOOL WEEKEND (Stage 1)
│       ├── __main__.py             ← CLI
│       ├── strategy.py             ← orchestratore
│       ├── scoring.py              ← logica scoring/RRG
│       └── data_sources.py         ← yfinance + lista SP500
├── motore/core/                           ← trasversali
│   ├── risk_gate.py                ← regole rischio (dormiente)
│   ├── runner.py                   ← orchestrator generico
│   └── registry.py                 ← registry strategie
├── motore/brokers/                        ← data source/esecuzione
│   ├── base.py                     ← ABC
│   ├── yfinance_data.py            ← USATO (Confluence VPS)
│   ├── mt5.py                      ← legacy
│   └── (ibkr/binance/coinbase)     ← stub futuri
├── motore/notifiers/
│   ├── base.py                     ← ABC
│   ├── telegram.py                 ← USATO
│   └── _pip_table.py               ← lookup pip
├── motore/tests/                          ← 81 test offline + 2 live
├── esercizio/mql5/                           ← EA in MQL5 (NO Python)
│   ├── london_breakout.mq5
│   └── include/
└── docs/                           ← guide operative
```

## Quando un file diventa obsoleto

Tutti i file marcati **stub** o **legacy** restano se non interferiscono con il runtime. La regola: si elimina solo quando il pivot è chiuso e non c'è scenario futuro che li riusa.
