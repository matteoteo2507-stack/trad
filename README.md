# Trading System — Workspace

Piattaforma modulare per costruire, testare e mettere in produzione strategie di trading
**automatiche** ed **semiautomatiche**, con scouting senza supervisione umana costante.

> Status: **Stage 0 (workspace setup)**. Stage successivi → vedi `ROADMAP.md`.

---

## Indice del workspace

| Cartella | Cosa contiene |
|---|---|
| `agents/` | Prompt di sistema per i subagent (Stock Selector + 4 personas del consensus) |
| `skills/` | Skill in formato `SKILL.md` per Claude Code / Antigravity |
| `strategies/` | Strategie Python (Confluence, Stock Selector). `_template/` come scaffold |
| `mql5/` | Expert Advisor MQL5 nativi per esecuzione automatica (es. London Breakout) |
| `brokers/` | Astrazione broker (yfinance read-only, MT5 legacy) |
| `notifiers/` | Canali di notifica (Telegram outbound) |
| `core/` | Componenti trasversali (risk gate, runner generico, registry strategie) |
| `data/` | Sorgenti dati locali, news calendar stub, stato persistente |
| `config/` | File YAML di configurazione (rischio, mercati) |
| `tests/` | Test automatici (offline) |
| `docs/` | Documentazione tecnica |

I file legacy al top level (`algoritmo selezione azioni.ipynb`, PDF, `.ods`, immagini) restano dove sono;
verranno integrati in `data/` o trasformati in subagent nelle fasi successive (vedi Stage 1).

## Documenti chiave

- `PROJECT.md` — Mission, obiettivi, vincoli, stack, decisioni architetturali.
- `ROADMAP.md` — I 7 stage in dettaglio, deliverable per stage, criterio di completamento.
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
