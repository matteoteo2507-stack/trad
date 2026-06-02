# ROADMAP — I 7 stage di build

> ## Stato reale 2026-05-31 (riconciliazione)
>
> Questo file è la **storia degli stage di build**. Il framing operativo corrente è in
> [PROJECT.md](PROJECT.md) (milestone di profittabilità + 3 sistemi) e le scelte chiuse sono in
> [DECISIONS.md](DECISIONS.md). In sintesi, rispetto agli stage sotto:
>
> - **Pivot 2026-05-05**: architettura a 3 componenti ibridi → [docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md).
> - **Priorità 2026-05-30**: **OctoBot** (#1) → dati Confluence + Telegram → prop → strategie custom *per ultime*.
> - **London Breakout** (Stage 2.5/2.6): **NO-GO**, archiviata. **TSMOM** (Stage 2.6): **NO-GO** single-asset.
> - **Telegram Signal Copier**: demo full-auto (non previsto negli stage originali).
> - Gli stage sotto restano come riferimento storico/tecnico, non come ordine di lavoro vincolante.

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

## Stage 2.5 — Quant Reviewer subagent

**Cosa**: subagent Claude Code locale specializzato in valutazione quantitativa adversariale
delle strategie. Invocabile via skill `/quant-review <strategia>`. Output: report markdown
con verdict GO/NO-GO/RAFFINA basato su metriche statistiche formali (PBO, DSR, walk-forward,
MC permutation).

**Motivazione**: dopo 2 settimane di trading live (London Breakout: 2 trade, RR fisso 1.5
percepito basso; Confluence: 0 trade per attrito operativo), le decisioni su quali strategie
promuovere/scartare devono passare da analisi quantitative, non da impressioni.

**Deliverable**:
- [agents/quant_reviewer.md](agents/quant_reviewer.md) — persona prompt con rigore accademico
  (López de Prado, Bailey, Harvey).
- [skills/quant-review/SKILL.md](skills/quant-review/SKILL.md) — invocazione `/quant-review`.
- [core/quant_metrics.py](core/quant_metrics.py) — DSR, PBO via CSCV, CPCV, walk-forward,
  Monte Carlo permutation, White's Reality Check, risk metrics oltre lo Sharpe.
- [docs/QUANT_REVIEW_PROTOCOL.md](docs/QUANT_REVIEW_PROTOCOL.md) — protocollo operativo
  passo-passo.

**Criterio di completamento**: `/quant-review mql5/london_breakout.mq5` produce un report
DSR+PBO leggibile in `docs/reviews/london_breakout-<data>.md`.

---

## Stage 2.6 — Strategy fleet expansion (parallel data collection)

**Cosa**: aumentare in parallelo il numero di trade/settimana per generare campione
statisticamente significativo entro 4 settimane.

**Componenti**:

1. **London Breakout 3 varianti A/B/C** (refactor `InpExitMode`):
   - A: `FIXED_RR` (1.5R) — baseline attuale.
   - B: `PARTIAL_TRAIL` — partial 50% a 1R, trailing ATR(M15)·1.5 sul resto + BE shift.
   - C: `FULL_TRAIL` — no TP fisso, trailing ATR(M15)·1.5 dal fill.

   Deploy su 3 account demo MT5 distinti, stesso simbolo/entry → 3× dati in parallelo
   sulla stessa price action.

2. **TSMOM USDJPY D1** ([strategies/tsmom/](strategies/tsmom/)):
   - Moskowitz-Ooi-Pedersen JFE 2012, sizing vol-target.
   - Modalità `notify_only` su VPS Hetzner, segnali via Telegram.
   - 4-8 trade/mese attesi → bassa attenzione operativa, ortogonale a London Breakout.

3. **Confluence manuale**: derubricata a opportunistica
   ([WEEKEND_CHECKLIST.md](WEEKEND_CHECKLIST.md) aggiornato), nessun obbligo settimanale.

4. **Confluence Auto (shadow run)** — nuovo modulo `strategies/confluence_auto/`:
   ricava i livelli **algoritmicamente** (S/R da swing pivot ZigZag/fractals,
   S/D da impulse-base-impulse detection, POC/VAH/VAL da volume profile, opzionale
   Fib su swing dominante) e li alimenta come `levels.yaml` virtuale al runner
   Confluence esistente. Gira **in parallelo** alla versione manuale per:
   - garantire copertura settimanale anche quando l'utente non ha tempo per
     l'analisi weekend;
   - costruire dataset di confronto manuale vs algoritmico → nel lungo periodo
     identifica quali concetti la mente umana cattura meglio dell'algoritmo
     e viceversa, per **rifinire la lettura dei livelli**;
   - moltiplicare i dati per il Quant Reviewer (Stage 2.7).

   I livelli Fib restano (per ora) **manuali** — lo swing dominante è scelta
   contestuale difficile da automatizzare in modo robusto; il modulo li
   marca come `[MANUAL_ONLY]` e li importa dall'analisi weekend se presente.

**Criterio di completamento**: ≥3 trade/settimana aggregati, mantenuto per ≥4 settimane
consecutive.

---

## Stage 2.6.5 — Regime gating automatico

**Cosa**: meccanismo che mappa regime corrente → quali strategie devono essere attive,
in `half_size` o `disabled`. Estensione di [`core/regime.py`](core/regime.py) che oggi
si limita a calcolare il regime senza pilotare le strategie.

**Motivazione**: ogni strategia funziona in regimi specifici (vedi
[TRADING_PRINCIPLES.md §1](TRADING_PRINCIPLES.md)), ma oggi è solo una regola scritta —
sta all'utente ricordarsene. Automatizzando si elimina un punto di disciplina umana.

**Architettura proposta**:
- `core/regime.py` scrive `data/current_regime.yaml` ad ogni esecuzione (cron daily 21 UTC).
- Ogni `strategies/*/config.yaml` dichiara `enabled_regimes` con la mappa regime → azione.
- All'avvio giornata ogni strategia legge il file e decide. Logga su Telegram quando
  passa in `disabled` / `half_size` / torna `active`.

**Quando implementarlo**: **dopo Stage 2.6** (London×3 + TSMOM attive). Senza un
campione di trade non possiamo validare che il mapping regime→strategia sia corretto.

**Deliverable**:
- Estensione `core/regime.py` → output `data/current_regime.yaml`.
- Nuovo campo `enabled_regimes` nei config delle strategie Python.
- Per gli EA MQL5: lettura del file via `FileOpen` al primo tick di ogni giornata.

**Criterio di completamento**: log Telegram mostra almeno 1 transizione di regime
che disabilita o riduce size di una strategia in modo osservabile.

---

## Stage 2.7 — Decision gate quant

**Cosa**: il Quant Reviewer ispeziona i dati raccolti in Stage 2.6 e decide quali strategie/
varianti promuovere a Stage 3 (backtester pluralistico) e quali deprecare.

**Deliverable**:
- Report `/quant-review` per ciascuna delle 4 strategie attive (London×3 + TSMOM).
- Confronto White's Reality Check sulle 3 varianti London (multiple-testing penalty).
- Decisione documentata in `docs/reviews/decision-gate-<data>.md`.

**Criterio di completamento**: almeno 1 strategia con verdict **GO** (PBO < 15%, DSR
significativo al 95%, walk-forward OOS degrado < 30%), pronta per Stage 3.

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
