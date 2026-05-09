# ROADMAP — I 7 stage di build

Filosofia: **complessità crescente**. Ogni stage produce qualcosa di osservabile. Lo stage N+1
inizia solo quando lo stage N è stabile.

---

## Stage 0 — Workspace setup ✅ (corrente)

**Cosa**: struttura cartelle, skill base, prompt di sistema, convenzioni codice, file config,
`.env.example`, `pyproject.toml`.

**Deliverable**: questo workspace pronto per essere aperto in Antigravity/Claude Code.

**Criterio di completamento**: tutti i `README.md` di cartella esistono, le `skills/` sono scritte,
le 4 personas del consensus hanno il loro prompt, c'è un template di strategia in `strategies/_template/`.

---

## Stage 1 — Stock Selector headless

**Cosa**: trasformare il notebook `algoritmo selezione azioni.ipynb` (V6.0) in un subagent callable
senza `input()` interattivi. Output: JSON strutturato + Excel formattato.

**Deliverable**:
- Modulo `stock_selector/` (sotto `strategies/` o equivalente) con funzione pura
  `run_selection(risk_free, liquidity_trend, benchmark="^GSPC") → SelectionResult`.
- CLI per invocarlo da terminale.
- Test su paper trading IBKR (validazione: i top picks tengono il portafoglio simulato per N settimane).

**Criterio di completamento**: invocazione headless che produce gli stessi top picks del notebook
manuale a parità di input.

---

## Stage 2 — Telegram bridge + single strategy meccanica MT5 demo

**Cosa**: una strategia tecnica codificata (presa dai PDF in cartella — confluence, candle
structures, NYSE scalping) che gira su uno dei 3 demo MT5 e manda i segnali via Telegram.

**Trading meccanico**: niente LLM nel loop. Regole codificate, conditional entry/exit.

**Deliverable**:
- `strategies/<nome_strategia>/strategy.py` con classe che eredita da `StrategyBase`.
- `notifiers/telegram.py` funzionante con bot token in `.env`.
- `brokers/mt5.py` operativo per leggere prezzi (esecuzione semiautomatica → notifica, non ordine).

**Criterio di completamento**: la strategia gira 1 settimana sul demo, manda almeno 5 segnali
plausibili via Telegram.

---

## Stage 3 — Backtester pluralistico

**Cosa**: wrapper che fa girare la stessa strategia su 2-3 backtester diversi (vectorbt + il
backtester di `ai-hedge-fund` + uno custom semplice) e produce un report comparativo normalizzato.

**Deliverable**:
- `backtesters/base.py` con interfaccia astratta.
- Almeno 2 implementazioni concrete.
- Report unificato (CSV/Markdown) con metriche standard: total return, Sharpe, max drawdown,
  win rate, profit factor, # trade.

**Criterio di completamento**: stessa strategia testata su 2+ backtester con report comparabile,
divergenze chiare e spiegabili.

---

## Stage 4 — Stock Selector Consensus (opzionale, on-demand)

**Cosa**: 4 personas (Damodaran, Buffett, Burry, Taleb) invocabili dallo Stock Selector come
"second opinion" sulle top picks. Stack: LangGraph + LangChain con multi-provider LLM.

**Output**: tabella con valutazione di ognuno dei 4 (signal, confidence, reasoning), **non un
voto aggregato meccanico**. La decisione finale è dell'utente.

**Deliverable**:
- `agents/consensus/{damodaran,buffett,burry,taleb}.md` (prompt già scritti in Stage 0).
- Modulo Python che orchestra la chiamata in parallelo via LangGraph.
- Skill `skills/stock-selector-consensus/SKILL.md`.

**Criterio di completamento**: invocazione su una top pick produce 4 valutazioni divergenti
(non identiche), in ≤ 60 secondi.

---

## Stage 5 — Worldmonitor bridge

**Cosa**: integrare worldmonitor come fonte sensoriale macro. I 7-signal radar + le news
aggregate entrano come **context** nel prompt dello Stock Selector e come **filtri on/off**
delle strategie meccaniche (es. se 7-radar dice "CASH", le strategie aggressive restano disabilitate).

**Deliverable**:
- API o file di scambio tra worldmonitor e questo workspace.
- Modulo `data/worldmonitor.py` che legge i signal correnti.
- Filtro `config/markets.yaml` esteso con regole condizionate al radar.

**Criterio di completamento**: il radar di worldmonitor controlla almeno 1 strategia in modo
osservabile (log mostra "strategia X disabilitata perché radar = CASH").

---

## Stage 6 — OctoBot integration crypto live

**Cosa**: prima strategia quant live su Binance/Coinbase con capitale minimo (5-10 €) usando
OctoBot come executor. Strategia validata in backtest e in demo deve passare a live con il
nostro layer di rischio sopra.

**Deliverable**:
- Bridge `brokers/coinbase.py` o `brokers/binance.py` che istruisce OctoBot.
- Risk gate (`config/risk.yaml`) che blocca size oltre soglia.
- Logging completo dei trade live.

**Criterio di completamento**: 10+ trade live eseguiti senza intervento manuale, drawdown
sotto la soglia configurata.

---

## Stage 7 — Prop firm challenge

**Cosa**: la strategia migliore validata in MT5 demo (Stage 2-3) viene scelta per il challenge
da 1k$ presso una prop firm low-cost (FTMO, MyForexFunds, FundedNext o simili).

**Deliverable**:
- Decisione documentata della strategia scelta + report di validazione.
- Account prop aperto.
- Sistema di esecuzione che gira sull'account prop.

**Criterio di completamento**: challenge superata. Da qui in poi → Step 2 (scalare con prop più grandi).
