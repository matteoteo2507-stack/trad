# PROJECT.md — Specifica funzionale

## Mission

Costruire una piattaforma modulare che faccia **scouting automatico** delle opportunità di trading,
testando in parallelo il maggior numero possibile di strategie, e che operi senza richiedere
supervisione umana costante.

## Obiettivi

### Step 1 — ~5.000 €/anno
Generare ~5.000 €/anno tramite un portafoglio diversificato di strategie automatiche e
semiautomatiche, partendo da capitale **0** e passando per una **prop firm low-cost (challenge da 1k$)**.
Il path è: paper/demo → strategia validata → prop superata → reinvestire profitti → prop più grandi.

### Step 2 — Conti prop da 100k
Gestire conti prop firm da 100k. Le entrate finanzieranno (a) operatività intensiva su conti
di accumulo e (b) trading di lungo termine.

## Vincoli operativi

- **Tempo**: nessuna possibilità di stare a grafico. Il sistema deve fare scouting al posto dell'utente.
- **Capitale di partenza**: 0 €. Path-to-prop come strategia di accesso al capitale.
- **Modalità di esecuzione supportate**:
  - **Automatica** → bot piazza l'ordine direttamente.
  - **Semiautomatica** → segnale via Telegram, l'utente piazza l'ordine (anche pending).

## Stack di sviluppo

- **Antigravity + Claude Code** → ambiente principale di build (codice).
- **Cowork (sessioni)** → organizzazione, roadmap, decisioni architetturali.
- **Claude scheduled tasks** → solo per task che richiedono ragionamento (briefing pre-mercato,
  sintesi notizie, monitoring scenari). **Mai per esecuzione ordini latency-critical**.
- **Telegram** → canale di notifica per segnali semiautomatici.
- **Linguaggio principale**: Python 3.11+. Eventuali moduli TS solo se imposti da repo esistenti
  (es. `dexter`, `worldmonitor`).

## Conti operativi

- IBKR live (vuoto o quasi) — paper trading per equities/futures/SP500 selector.
- Coinbase, Binance (vuoti o quasi) — laboratorio crypto.
- 3 demo MT5 — training ground per la prop firm.

## Stratificazione mercati per scopo (Step 1)

| Conto | Scopo | Cosa ci gira |
|---|---|---|
| **3 demo MT5** | Training ground per la prop. Le prop low-cost da 1k operano su MT4/5. | Strategie tecniche meccaniche (scalping, candle patterns, confluence). |
| **Coinbase + Binance** | Laboratorio sperimentale 24/7. | Strategie quant nuove, OctoBot. |
| **IBKR paper** | Casa dello Stock Selector (notebook V6.0). | Output del Stock Selector → simulazione paper trading. |

## Decisioni architetturali chiave

### 1. Trading è MECCANICO, non agent-driven
Le decisioni operative (entrata, gestione, uscita di un trade) avvengono per **regole codificate**
dentro le strategie, NON tramite analisi parallele di agenti LLM. Gli agent intervengono in altre
parti del workflow (selezione, design, backtest), non nell'esecuzione.

### 2. Stock Selector Consensus opzionale (Stage 4)
Layer multi-agent **stocastico** limitato alla scelta delle azioni. Quattro personas pescate da
`ai-hedge-fund` (Damodaran, Buffett, Burry, Taleb) producono ognuna `{signal, confidence, reasoning}`
sullo stesso ticker. Output: tabella delle 4 lenti, **non un voto aggregato meccanico** — la decisione
finale resta dell'utente. Invocato on-demand dallo Stock Selector.

### 3. Backtester pluralistico (Stage 3)
NON scegliere un solo backtester. Wrapper che permetta di switchare tra più backtester
(vectorbt, quello di ai-hedge-fund, custom) e produca metriche normalizzate per confronto.

### 4. Broker-agnostic dal giorno 1
Astrazione `BrokerBase` con implementazioni separate per IBKR, MT5, Coinbase, Binance.
Lo stesso signal può essere ruotato sul conto giusto a seconda della strategia.

### 5. Build a complessità crescente
Ogni stage poggia sul precedente. Lo stage N+1 inizia solo quando lo stage N è stabile e
osservabile. Non costruire tutto il sistema in parallelo.

### 6. worldmonitor: integrare, non riscrivere
Il dashboard `worldmonitor` (Tauri+TS) è asset esistente. Diventa la fonte sensoriale del
sistema (context macro/news/scenario per Stock Selector e per filtri on/off delle strategie meccaniche).
Bridge di integrazione → Stage 5.

### 7. Vault Obsidian come knowledge base evolutiva
Path: `C:\Users\mmbus\Obsidian\`. Vuoto all'inizio. Contiene risultati test, decisioni progettuali,
storico dati delle strategie. NON è fonte di input iniziale.

## Asset esterni — ruolo assegnato

| Repo | Ruolo |
|---|---|
| paperclip-zero-human-trading-firm | Blueprint funzionale (riferimento concettuale, non scaffold) |
| ai-hedge-fund | Substrato pattern multi-agent (LangGraph) + libreria personas per il Consensus |
| TradingAgents | Riferimento alternativo al pattern multi-agent (consultivo) |
| dexter | Riferimento per pattern Skill + SOUL.md (identità agent) |
| OctoBot | Layer esecutivo crypto (Stage 6) |
| Kronos | Componente predittivo OHLCV (post-MVP, richiede GPU) |
| Q-Fin | Libreria utility (option pricing, stochastics) |
| AI_Stock_Trading | Marginale (didattico) |
| worldmonitor | Fonte sensoriale macro (Stage 5) |
