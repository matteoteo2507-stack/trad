# Trading System — Workspace

Piattaforma modulare per costruire, testare e mettere in produzione strategie di trading
**automatiche** ed **semiautomatiche**, con scouting senza supervisione umana costante.

> **Framing corrente** → [PROJECT.md](PROJECT.md) (milestone di profittabilità + 3 sistemi + traccia investing).
> Decisioni già prese → [DECISIONS.md](DECISIONS.md). Storia degli stage di build → [ROADMAP.md](ROADMAP.md).

---

## Indice del workspace

| Cartella | Cosa contiene |
|---|---|
| `fondamenti_tecnici/` | **Knowledge base**: teoria/concetti, `blueprints/`, `strategie_candidate/`, `_sorgenti/` (PDF/txt originali). Vedi il suo [README](fondamenti_tecnici/README.md) |
| `strategies/` | Strategie Python + **indice master** di tutte le strategie per sistema ([README](strategies/README.md)) |
| `mql5/` | Expert Advisor MQL5 (London Breakout archiviata NO-GO, futuri EA) |
| `signal_copier/` | Copia-segnali Telegram → MT5 (demo full-auto) |
| `agents/` | Prompt di sistema per i subagent (quant_reviewer, Stock Selector, 4 personas consensus) |
| `skills/` | Skill in formato `SKILL.md` per Claude Code / Antigravity |
| `brokers/` | Astrazione broker (yfinance read-only, MT5 legacy) |
| `notifiers/` | Canali di notifica (Telegram outbound) |
| `core/` | Componenti trasversali (regime, quant_metrics, risk gate, runner, registry) |
| `data/` | Sorgenti dati locali, news calendar stub, stato persistente |
| `config/` | File YAML di configurazione (rischio, mercati) |
| `journals/` | Schema journaling (markdown weekend + Notion) |
| `tests/` | Test automatici (offline) |
| `docs/` | Documentazione tecnica + [reviews/](docs/reviews/) |

I documenti sorgente densi (PDF, `.txt`, immagini) sono stati **spostati** in
[`fondamenti_tecnici/_sorgenti/`](fondamenti_tecnici/_sorgenti/) e distillati in `principles.md`
strutturati (vedi [fondamenti_tecnici/README.md](fondamenti_tecnici/README.md)). Il notebook
`algoritmo selezione azioni.ipynb` resta al top level (sorgente dello Stock Selector).

## Documenti chiave

- `PROJECT.md` — Mission, milestone di profittabilità, 3 sistemi, traccia investing, asset esterni.
- `DECISIONS.md` — **Decisioni già prese** (pivot, NO-GO, priorità). Leggi prima di proporre.
- `TRADING_PRINCIPLES.md` — Costituzione operativa (regimi, S/R, S/D, Fib, entry, journaling).
- `fondamenti_tecnici/` — Knowledge base teorica (concetti, blueprint, candidate).
- `ROADMAP.md` — Storia degli stage di build (con riconciliazione 2026-05-31 in testa).
- `CONVENTIONS.md` — Convenzioni di codice, naming, lingua commenti, pattern di estensione.

## Quick start (quando passi su Antigravity / Claude Code)

1. Apri la cartella `C:\Users\mmbus\Desktop\lavoro\trad` come progetto.
2. Leggi `PROJECT.md` e `ROADMAP.md` (5 minuti).
3. Stage corrente da implementare → vedi sezione "Stato corrente" qui sotto.
4. Le `skills/` sono già scritte: usale come istruzioni precompilate per Claude Code.

## Stato corrente

> **Quando torni dopo qualche giorno, apri questi due:**
> 1. [docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md) — architettura post-pivot (3 componenti
>    ibridi cloud-native), workflow settimanale, deployment, costi.
> 2. [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md) — **step-by-step** per deploy
>    VPS, EA MQL5, MetaQuotes VPS, e workflow weekend (Stock Selector + levels.yaml).
>
> Documento storico: [docs/STAGE2_TESTING_PLAN.md](docs/STAGE2_TESTING_PLAN.md) (pre-pivot).

- [x] Stage 0 — Workspace setup
- [x] Stage 1 — Stock Selector headless (Python weekend tool)
- [x] Stage 2 — Confluence Levels Python + Telegram bridge (solo notifica, 81/81 test verdi). Cloud-ready via yfinance, niente più MT5 desktop richiesto.
- [x] Stage 2.5 — London Open Breakout migrato a **Expert Advisor MQL5** (`mql5/london_breakout.mq5`). Gira sul terminale MT5 / MetaQuotes VPS. Backtest in Strategy Tester.
- [ ] **Pivot architetturale 2026-05-05**: vedi `docs/ARCHITECTURE_v2.md`. Componenti ibridi su 3 habitat indipendenti.
- [ ] Stage 3 — Backtester pluralistico (per equity/crypto Python; per forex il Strategy Tester MT5 è sufficiente)
- [ ] Stage 4 — Stock Selector Consensus (4 personas opzionali)
- [ ] Stage 5 — Worldmonitor bridge
- [ ] Stage 6 — OctoBot integration crypto live
- [ ] Stage 7 — Prop firm challenge

## Asset esterni di riferimento

- Repo di studio in `C:\Users\mmbus\OneDrive\Desktop\` o online: `paperclip-zero-human-trading-firm`,
  `ai-hedge-fund`, `TradingAgents`, `OctoBot`, `dexter`, `Kronos`, `Q-Fin`, `worldmonitor`,
  `AI_Stock_Trading`. Vedi `PROJECT.md` per il ruolo assegnato a ciascuno.
- Vault Obsidian: `C:\Users\mmbus\Obsidian\` — knowledge base evolutiva (test, decisioni, storico dati).
- Sito proprio di market intelligence: [worldmonitor.app](https://worldmonitor.app).
