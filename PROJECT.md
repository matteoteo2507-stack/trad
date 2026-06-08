# PROJECT.md — Specifica funzionale

> **Aggiornato 2026-05-31.** Sostituisce il vecchio framing "7-stage / 5.000€ / Stage 0".
> Le decisioni operative già prese sono in [DECISIONS.md](DECISIONS.md) — consultalo prima di
> riproporre cose. La storia degli stage di build resta in [ROADMAP.md](ROADMAP.md).

## Mission

Portare alla **profittabilità** un piccolo portafoglio di sistemi di trading e investing che
operano **senza supervisione costante**, partendo da capitale ~0 e usando le **prop firm** come
leva di accesso al capitale. Il sistema fa scouting al posto dell'utente (niente tempo a grafico).

---

## Milestone di profittabilità (il path)

L'ordine degli step **non cambia**; cambiano gli strumenti con cui li raggiungiamo.

1. **Profittabilità ≥ 1 mese su demo** — un sistema dimostra mese positivo su conto demo.
2. **Prop firm** — superare una challenge low-cost (es. da 1k$) col sistema validato.
3. **Scalare con le prop** — reinvestire i guadagni in **nuove challenge** per account
   **multipli** e **più grandi**, fino a gestire un **account prop da 100k**.
4. **Allocazione delle entrate prop** → due destinazioni:
   - **(a) Stock Selector** (capitale per l'investing azionario).
   - **(b) PAC** — piano di accumulo capitale (lungo termine).

---

## I sistemi da portare a profittabilità

Le modalità **semiautomatico → automatico** sono uno **spettro di maturità esecutiva**, non
etichette fisse: un sistema nasce semiauto (l'utente piazza) e **gradua** ad auto (eseguito dal
bot) man mano che parsing, risk gate e affidabilità lo permettono.

### 1. Semiautomatico — *l'analisi arriva, tu piazzi l'ordine*
- **Confluence Levels** (Python, VPS): notifica setup via Telegram, l'utente piazza a mano.
- **Analisi canali Telegram mentori**: oggi l'utente riceve l'analisi e piazza. **In test
  semiauto → target: piena automazione** (vedi sotto).

### 2. Automatico — *segnali eseguiti direttamente*
- **Telegram Signal Copier**: segnali dei 2 canali mentori → MT5, **demo full-auto**
  (è il percorso di automazione dei segnali semiauto). Prop rimandata; caveat compliance.
- **Strategie quant / EA MQL5**: London Breakout (archiviata NO-GO), TSMOM (NO-GO), Confluence
  Auto (shadow), future EA. Regole codificate, niente LLM nel loop esecutivo.
- **OctoBot**: layer esecutivo crypto — **priorità #1 corrente** ([DECISIONS.md](DECISIONS.md)).

### 3. Manuale / Investing (lungo termine, alimentato dalle entrate prop)
Traccia di **accumulo e crescita capitale**, parallela al trading e **parte conclusiva** del progetto.
**Riformulata 2026-06-02** (vedi [DECISIONS.md](DECISIONS.md) e [docs/INVESTING_PILLAR_PLAN.md](docs/INVESTING_PILLAR_PLAN.md)):
- **Pilastro investing = due secchi passivi**, non un algoritmo:
  - **Secchio A — buffer di sicurezza** (cash/bond brevi, riempito prima dallo stipendio).
  - **Secchio B — PAC**: DCA su ETF azionario **globale All-World** + glide-path per età.
- **Stock Selector** — **ARCHIVIATO come edge-seeker**: dati live + backtest 12y + MVP TAA hanno
  mostrato nessun edge di selezione/timing che batta l'indice. I materiali tecnici (regime, Fed,
  archetipi) restano utili alla traccia trading, non al PAC. Vedi [reviews](docs/reviews/).
- **worldmonitor** — dashboard macro/geopolitica ([worldmonitor.app](https://worldmonitor.app)):
  sensore macro, eventuale supporto al contesto, **non** un selettore di titoli.

PAC passivo ∥ buffer ∥ worldmonitor compongono il pilastro investing di lungo periodo.

---

## Vincoli operativi

- **Tempo**: nessuna possibilità di stare a grafico — il sistema fa scouting al posto dell'utente.
- **Capitale di partenza**: ~0 €. Path-to-prop come strategia di accesso al capitale.
- **Trading meccanico**: entrata/gestione/uscita per **regole codificate**, non per analisi LLM
  nel loop. Gli agent intervengono in selezione/design/review, non nell'esecuzione latency-critical.
- **Sicurezza**: mai live senza risk gate; `paper_mode` default; drawdown cap in `config/risk.yaml`
  (vedi [CONVENTIONS.md](CONVENTIONS.md)).

---

## Architettura

Post-pivot **2026-05-05**: 3 componenti indipendenti, 3 habitat, **zero bridge** — dettaglio in
[docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md), runbook in [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md).

| Componente | Tipo | Habitat |
|---|---|---|
| Confluence Levels (Python) | solo notifica | VPS Linux Hetzner |
| Expert Advisor MQL5 | esecuzione automatica | MetaQuotes VPS |
| Stock Selector (Python) | tool offline | PC di casa |

Linguaggio principale **Python 3.11+**; TS solo se imposto da repo esterni (es. `worldmonitor`).

---

## Mappa del workspace

| Cartella / file | Cosa contiene |
|---|---|
| [fondamenti_tecnici/](fondamenti_tecnici/) | **Knowledge base**: teoria/concetti (price action, liquidità, regimi/macro, quant, portfolio, stock selection, data sources), `blueprints/` (idee non committate), `strategie_candidate/`, `_sorgenti/` (PDF/txt originali) |
| [strategies/](strategies/) | Strategie Python + **indice master** di tutte le strategie/componenti per sistema |
| [mql5/](mql5/) | Expert Advisor MQL5 (London Breakout archiviata, futuri EA) |
| [signal_copier/](signal_copier/) | Copia-segnali Telegram → MT5 (demo full-auto) |
| [agents/](agents/) | Prompt subagent (quant_reviewer, stock_selector, 4 personas consensus) |
| [skills/](skills/) | Skill `SKILL.md` per Claude Code |
| [core/](core/) | Componenti trasversali (regime, quant_metrics, risk_gate, runner, registry) |
| [brokers/](brokers/) · [notifiers/](notifiers/) | Astrazione broker · canali notifica (Telegram) |
| [config/](config/) · [data/](data/) | YAML config (rischio, mercati) · dati locali e stato |
| [journals/](journals/) | Schema journaling (markdown weekend + Notion) |
| [docs/](docs/) | Architettura, guida operativa, protocollo quant, [reviews/](docs/reviews/) |
| [DECISIONS.md](DECISIONS.md) | **Decisioni già prese** (consultare prima di proporre) |
| [TRADING_PRINCIPLES.md](TRADING_PRINCIPLES.md) | Costituzione operativa (regimi, S/R, S/D, Fib, entry) |
| [ROADMAP.md](ROADMAP.md) · [CONVENTIONS.md](CONVENTIONS.md) | Storia stage di build · convenzioni codice |

---

## Asset esterni (repo GitHub `matteoteo2507-stack`, audit 2026-05-31)

29 repo sul profilo. Ruolo assegnato a quelli rilevanti per il progetto:

| Repo | Ruolo |
|---|---|
| `OctoBot` | Layer esecutivo crypto — **priorità #1** |
| `worldmonitor` | Fonte sensoriale macro/geopolitica (pilastro investing conclusivo) |
| `claude-trading-skills` | Catalogo 40+ skill trading — fonte di `blueprints/claude_skills_catalog.md` + `claude_code_for_trading.md` |
| `ai-hedge-fund` | Substrato multi-agent (LangGraph) + personas per il Consensus |
| `dexter` | Pattern Skill + SOUL.md (identità agent) / deep financial research |
| `TradingAgents` | Riferimento alternativo pattern multi-agent (consultivo) |
| `paperclip-zero-human-trading-firm` | Blueprint funzionale (riferimento concettuale) |
| `AI_Stock_Trading` | Design pattern AI trading bot (didattico) |
| `pybroker` | Algo trading Python + ML — candidato backtester pluralistico |
| `Q-Fin` | Libreria utility (option pricing, stochastics) |
| `Kronos` | Foundation model OHLCV (post-MVP, richiede GPU) |
| `QuantDinger` / `FinceptTerminal` / `Vibe-Trading` | Piattaforme/agent trading di riferimento (studio) |
| `tradingview-mcp` | MCP TradingView — **valutato e rimandato** (legge solo Pine, non drawings) |
| `second-brain` / `claudian` | Knowledge base Obsidian + Claude (collegabile al vault) |
| `deep-research` / `GenericAgent` / `ml-intern` / `skills` / `andrej-karpathy-skills` / `context-mode` / `GitNexus` | Tooling AI/agent generico (riferimento) |

Repo non pertinenti al trading: `uBlock`, `awesome`, `actual-backend-app`, `app1`, `Fix-Your-Errors`.

> Nota: la maggior parte dei repo trading sono **fork/riferimenti** di studio, non scaffold da
> integrare ora. L'integrazione effettiva resta condizionata alle priorità in [DECISIONS.md](DECISIONS.md).
