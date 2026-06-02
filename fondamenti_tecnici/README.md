# fondamenti_tecnici/ — Knowledge base

Fondamenti matematici, tecnici e di funzionamento del mercato: il materiale da cui si
costruiscono strategie, skill, agenti e infrastrutture. Distillato dai documenti sorgente
(in [`_sorgenti/`](_sorgenti/)) in `.md` strutturati e uniformi.

## Come è organizzata (3 nature distinte)

1. **Concetti / reference** (`01_…` → `07_…`) — teoria e fondamenti **stabili**, riferimento.
2. **[blueprints/](blueprints/)** — sistemi *buildabili* (agenti/skill/infra). Sono **idee NON
   committate**: materiale di riferimento, **non** un mandato a costruire. Vedi [DECISIONS.md](../DECISIONS.md).
3. **[strategie_candidate/](strategie_candidate/)** — spec di strategie tradabili pronte a essere
   promosse a `strategies/` o `mql5/` **se** prioritizzate.

> **Regola anti-allucinazione.** Questa cartella raccoglie *materiale*, non *decisioni*. Prima di
> proporre "costruiamo X" da un blueprint o una candidata, controlla [DECISIONS.md](../DECISIONS.md):
> la priorità 2026-05-30 mette le strategie/agenti custom **per ultime** (OctoBot prima).

## Indice

### Concetti / reference
| # | Argomento | Alimenta |
|---|---|---|
| 01 | [Price Action & Market Structure](01_price_action/principles.md) | confluence_levels, candidate |
| 02 | [Liquidità & Order Flow (SMC)](02_liquidita_orderflow/principles.md) | confluence_levels, confluence_auto |
| 03 | [Regimi di mercato & Macro timing](03_regimi_macro/principles.md) | core/regime.py, regime gating |
| 04 | [Metodologia Quant & Bias del backtest](04_quant_metodologia/principles.md) | quant-review, core/quant_metrics.py |
| 05 | [Portfolio & Decomposizione del rischio](05_portfolio_rischio/principles.md) | stock_selector |
| 06 | [Stock Selection](06_stock_selection/principles.md) | stock_selector, consensus |
| 07 | [Data Sources (reference)](07_data_sources/reference.md) | stock_selector/data_sources.py |

### Blueprints (idee non committate)
- [Markov regime skill](blueprints/markov_regime_skill.md) — alternativa probabilistica a `core/regime.py`
- [Hermes optimizer](blueprints/hermes_optimizer.md) — agente auto-migliorante di strategie
- [Insider constellation](blueprints/insider_constellation.md) — 7 agenti SEC/13F/Fed/on-chain
- [Catalogo skill Claude](blueprints/claude_skills_catalog.md) — 40+ skill (repo `claude-trading-skills`)
- [Claude Code for Trading](blueprints/claude_code_for_trading.md) — guida meta/onboarding

### Strategie candidate
- [NYSE Scalping (VWAP + TPO + OTF)](strategie_candidate/nyse_scalping.md)

## Convenzione dei file

Ogni file ha frontmatter (`titolo`, `fonti`, `tipo`) e sezioni: blockquote di sintesi → `## Concetti`
→ `## Regole operative` (se applicabili) → `## Collegamenti` → `## Fonti`. I link interni usano
`[[nome]]` (wikilink) e i path relativi al repo (`../../`).

## Collegamenti chiave nel repo

- Costituzione operativa: [TRADING_PRINCIPLES.md](../TRADING_PRINCIPLES.md) (regole già attive su regimi, S/R, S/D, Fib, POC)
- Decisioni già prese: [DECISIONS.md](../DECISIONS.md)
- Strategie (indice): [strategies/README.md](../strategies/README.md)
- Quant: [core/quant_metrics.py](../core/quant_metrics.py), [docs/QUANT_REVIEW_PROTOCOL.md](../docs/QUANT_REVIEW_PROTOCOL.md)
- Regime engine: [core/regime.py](../core/regime.py)
