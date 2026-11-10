---
titolo: "Estratto — Roan (@RohOnChain) Quant Series + ecosistema jackson-video-resources"
fonti:
  - "X/@RohOnChain (articoli gated, presi via mirror: rattibha/youmind/reddit)"
  - "github.com/jackson-video-resources (18 repo companion)"
tipo: blueprint
---

# Estratto — Roan (@RohOnChain) Quant Series + ecosistema

> **STATO: reference/catalogo — NON un mandato a costruire** (regola anti-allucinazione, vedi
> [README](../README.md) e [DECISIONS.md](../../../decisioni/DECISIONS.md): custom in fondo). Cattura **lossless**
> di materiale utile, distillato **on-demand**. I 3 repo taggati ⭐WORKFLOW sono **INPUT del piano
> di architettura del workflow** (il piano successivo), non roba da installare ora.
> Tracciato in [`_INTAKE.md`](../../../decisioni/_INTAKE.md).

> ⚠️ **Framing onesto.** I titoli "…To Win Every Single Trade" sono **marketing**; le tecniche
> sotto sono **standard accademici reali** (Grinold-Kahn, ADF, IC/IR, PPO). Tutto va comunque
> **dietro il nostro gate** (DSR/PBO/costi, [[04_quant_metodologia]]), mai preso sulla fiducia del
> demo — stessa regola della Markov 2.0.

## Chi è (e limiti d'accesso)
**Roan = @RohOnChain** (≠ Quant Guild / Paolucci, che è l'altra fonte — volatility drag/VRP).
Backend dev: system design, **HFT-style execution**, sistemi quant, focus **prediction markets +
crypto on-chain**. ~50.7K follower. **Niente GitHub pubblico** sotto quel nome: il **codice dei suoi
framework vive nei repo di Lewis Jackson** (`jackson-video-resources`, "the guy installing it on
camera"). Gli "Article" long-form su X sono **gated senza login** → substance recuperata dai mirror.

## La "Quant Series" (articoli + cuore tecnico)

| # | Articolo | Cuore tecnico | Nostro stato |
|---|---|---|---|
| 1 | **Hedge Fund Method / Markov** | regime → matrice transizione → stickiness → segnale `P(bull)−P(bear)` | già nostro ([[markov_regime_skill]] + FIX 1 in [[04_quant_metodologia]]) |
| 2 | **Time Series Model** | lag/differencing, **lookback scelto per correlazione** con holding period, OLS vs WLS, **stazionarietà (ADF)** | da assorbire on-demand |
| 3 | **Linear Regression → Alpha Signals** | isolare **alpha da beta**, p-value, **OOS testing**, single→multi-factor | da assorbire on-demand |
| 4 | **50 Weak Signals → 1 Trade** | **Fundamental Law of Active Management** (Grinold): `IR = IC·√breadth` — combinare molti segnali deboli batte cercarne 1 forte; procedura 11-step | rilevante (ensemble/ortogonalità) |
| 5 | **How Quant Firms Use AI (Roadmap)** | pipeline agentica research→signal→execution | input workflow |
| 6 | **RL/POMDP trading system** | stato `{OHLCV, posizione, regime, σ}`, **PPO** (ε=0.2, GAE), **vol-targeting 15%**, 50 alpha `~N(0,1)`, **regime filter `𝟙(MA20>MA100)`** | avanzato, reference |
| 7 | "$650k/yr quant career from zero" | career/roadmap | skip |

## Insight trasversali da assorbire (quando serve)
- **Fundamental Law**: `IR = IC·√breadth`. Molti segnali deboli quasi-indipendenti > un segnale
  forte. Si lega alla nostra ortogonalità ([[05_portfolio_rischio]], quant §7).
- **Disjoint bars**: misurare IC/persistenza su barre **non sovrapposte** → già assorbito come
  metodologia ([[04_quant_metodologia]] §7); cross-confermato anche dal thread r/quant.
- **Autocorrelazione del segnale = proxy del turnover**: matcha la velocità di decadimento dell'IC
  col turnover per massimizzare il profitto netto.
- **Vol-targeting** (scala la size per tenere σ annua ~15%) e **regime filter** (`MA20>MA100`,
  flat longs in down-regime): pattern standard, coerenti col nostro sizing/regime.

## Ecosistema-tool: i 18 repo `jackson-video-resources`
Link: `https://github.com/jackson-video-resources/<nome>`

**⭐WORKFLOW — input diretti per il piano di architettura successivo:**
- **`paperclip-zero-human-trading-firm`** (106★) — **firm a 6 agenti**: CEO · Research (scanna
  YouTube/arXiv/TradingView/Reddit) · **Backtest (memoria istituzionale: logga ogni risultato)** ·
  **Risk (gatekeeper: niente va live senza firma + tua approvazione)** · Execution (paper default) ·
  Cost Optimizer. ← è la catena research→gate→sizing→execution che vogliamo.
- **`ai-quant-workbench`** (5★) — skill modulare: probability primitives (Bayes/EV), statistics
  (t-test, OLS signal-vs-noise, **ADF**, residui), portfolio math (covarianza, eigendecomposition).
- **`skills`** (11★) — toolkit Claude Code: `autoresearch`, `capital-allocator`, `risk-manager`,
  `strategy-audit`, `backtest`, `pine-script`, `trade-journal`, `commit-push-pr`, `security-audit`.
  (`npx skills add jackson-video-resources/skills -s <nome>`)

**Esecuzione / bridge:** `claude-tradingview-mcp-trading` (484★, Claude↔TradingView↔BitGet,
safety-check, VPS 24/7, `trades.csv` tax-ready, MACD da candele grezze) · `claude-mt5` ·
`claude-code-stocks-futures`.
**Research-automation:** `yt-strategy-agent` (19★, ultimi 5 video di un canale → `strategy.md` +
`rules.json` + changelog) · `markov-hedge-fund-method` (292★, video 1).
**Crypto/DeFi (meno rilevanti per noi):** `bittensor-investing-agent` · `vibe-staking` ·
`defi-yield-optimizer-agent` · `Jackson-airdrop-farmer`.
**Off-topic:** `ai-accountant` (UK tax) · `claude-plus-codex` · `codex-claude-bridge` ·
`daily-personal-feed-agent` · `dreams-use-case-template` · `codex-goal-directive`.

## Conflitti annotati (mappa dei modelli)
- "Backtest inutile/overfitting" (taglio di Roan/Quant Guild) **vs** la nostra disciplina
  DSR/PBO/walk-forward: risolto in [DECISIONS.md → Mappa dei modelli](../../../decisioni/DECISIONS.md) (falsificare
  ≠ scoprire una regola curve-fit). Le sue tecniche (IC, ADF, Fundamental Law) **presuppongono** la
  misurazione → la sua "critica al backtest" è retorica, la prassi è quantitativa.

## Collegamenti
- [[markov_regime_skill]] — video 1 della serie, già nel workspace (con i 3 fix della 2.0).
- [[04_quant_metodologia]] §7 — disjoint/stride sampling (assorbito da qui).
- [[05_portfolio_rischio]] — ortogonalità / Fundamental Law / vol-targeting.
- [`_INTAKE.md`](../../../decisioni/_INTAKE.md) — stato di questa fonte (`parcheggiato/reference`).

## Fonti
- X/@RohOnChain — "Quant Series" (articoli long-form **gated**: titoli, metriche e substance presi
  via mirror rattibha/youmind + thread r/quant). I corpi completi con codice restano gated.
- `github.com/jackson-video-resources` — 18 repo companion (README letti via API GitHub, giugno 2026).
