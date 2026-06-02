---
titolo: "Catalogo claude-trading-skills — 40+ skill Claude Code per trading"
fonti:
  - "_sorgenti/Appunti estratti da pdf key concept.txt"
  - "_sorgenti/Claude_Code_for_Trading_SoulzBTC docx (2)_260522_110338.pdf"
tipo: blueprint
---

# Catalogo claude-trading-skills — 40+ skill Claude Code per trading

> **STATO: idea — NON committata.** Vedi ../../DECISIONS.md (priorità 2026-05-30: OctoBot prima, dati Confluence+Telegram, prop; agenti/strategie custom PER ULTIME). Questo è materiale di riferimento, non un mandato a costruire.

## Cosa è

Catalogo di **40+ skill Claude Code** per il trading, organizzate per layer/area di workflow. Corrisponde al repo GitHub **`claude-trading-skills`** dell'utente (vedi ../../PROJECT.md → "Asset esterni") e si collega alla guida `claude_code_for_trading.md`. Filosofia dichiarata del toolkit: **non** outsourcing della decisione buy/sell all'AI, ma strutturare market review, risk management, trade planning, journaling e miglioramento continuo. È decision-support / process-improvement, non un signal service. Pensato per equity US (più estensioni crypto/forex su alcune skill).

## Architettura

Sei aree skill + satellite + meta tooling. Sintesi per layer:

**Layer 1 — Market Regime (so prima di tradare):** Market Breadth Analyzer, Uptrend Analyzer, Breadth Chart Analyst, Sector Analyst, Market Top Detector, Downtrend Duration Analyzer, Exposure Coach, **FTD Detector** (Follow-Through Day, O'Neil, conferma minimo di mercato), **IBD Distribution Day Monitor** (conta Distribution Days su QQQ/SPY: 0-3 NORMAL, 4-5 CAUTION, 6+ HIGH→SEVERE; scadono dopo 25 sessioni o rally +5%), **Macro Regime Detector** (transizioni macro 1-2 anni via ratio cross-asset: azioni/bond, growth/value, credit spread, curva, momentum commodity), Market Environment Analysis, Market News Analyst, **US Market Bubble Detector** (framework Minsky/Kindleberger v2.1, score 0-100).

**Layer 2 — Core Portfolio (so cosa possiedo):** Portfolio Manager (live via Alpaca MCP, flag HOLD/ADD/TRIM/SELL), Value Dividend Screener, Dividend Growth Pullback Screener, Kanchi Dividend SOP, Kanchi Dividend Review Monitor (5 trigger T1-T5), Kanchi Dividend US Tax Accounting.

**Layer 3 — Swing Opportunity (trova i setup, solo a regime verde):** **VCP Screener** (Volatility Contraction Pattern, Minervini, Stage 2), **CANSLIM Screener** (O'Neil 7-fattori + Relative Strength multi-periodo), Breakout Trade Planner, FINVIZ Screener, Theme Detector.

**Layer 4 — Trade Planning:** Position Sizer (zero dipendenze), Technical Analyst (su chart image), US Stock Analysis.

**Layer 5 — Trade Memory:** Trader Memory Core (YAML locale), Signal Postmortem (4 domande), Trade Hypothesis Ideator.

**Layer 6 — Edge Discovery / Strategy Research:** Backtest Expert, Edge Candidate Agent, Edge Hint Extractor, Edge Concept Synthesizer, Edge Strategy Designer, Edge Strategy Reviewer (quality gate anti-overfit/survivorship), Edge Signal Aggregator, Edge Pipeline Orchestrator, Stanley Druckenmiller Investment Advisor (8 input → conviction 0-100), Strategy Pivot Designer, Scenario Analyzer.

**Satellite (high-value):** Earnings Trade Analyzer (5-fattori), **PEAD Screener** (Post-Earnings Announcement Drift), **Institutional Flow Tracker** (13F), **Pair Trade Screener** (arbitraggio statistico / cointegrazione), Options Strategy Advisor (Black-Scholes), Parabolic Short Trade Planner (3 fasi).

**Meta tooling:** Earnings Calendar, Economic Calendar Fetcher, Data Quality Checker, Skill Designer, Skill Idea Miner, Dual-Axis Skill Reviewer + il loop di self-improvement / auto-generazione skill (round-robin scoring, gate a 90/100, PR automatiche).

**Matrice dipendenze API** (Required / Optional / Not used):
- **FMP API** (free tier 250 req/giorno): *Required* per FTD Detector, IBD Distribution Day Monitor, Macro Regime Detector, VCP Screener, CANSLIM Screener, dividend screeners, Earnings Trade Analyzer, PEAD Screener, Institutional Flow Tracker, Pair Trade Screener, Earnings/Economic Calendar, Parabolic (Ph1). *Optional* per Exposure Coach, Theme Detector, Trader Memory Core, Signal Postmortem, Options Strategy Advisor, Edge Candidate Agent.
- **FINVIZ Elite** ($39.50/mese): *Optional* — velocizza i dividend screener del 70-80% e FINVIZ Screener; mai *Required*.
- **Alpaca** (paper gratuito): *Required* per Portfolio Manager; richiesto in Ph3 di Parabolic Short.
- **Not used / free**: tutto il layer Market Breadth/Uptrend (CSV pubblici GitHub), Position Sizer, Technical Analyst, US Stock Analysis, US Market Bubble Detector, l'intero Edge pipeline, Backtest Expert, Data Quality Checker e quasi tutto il meta tooling (locale/offline o web search).

## Cosa servirebbe per costruirlo / usarlo

- **Claude Code** (incluso nella subscription Claude) + il repo `claude-trading-skills` clonato.
- **Stack gratuito**: una market review + journaling completi girano a costo zero (CSV pubblici + skill locali).
- **FMP free tier** (250 req/giorno) per sbloccare screener e detector regime — `export FMP_API_KEY=...`.
- **Alpaca paper** (gratis, via MCP server) per Portfolio Manager — `ALPACA_PAPER=true` finché non si è confidenti.
- **FINVIZ Elite** opzionale, solo se il tempo di esecuzione dei dividend screener dà fastidio.

## Perché è rimandato

Doppio caveat. Primo: è un **toolkit equity-US**, ortogonale al focus forex/Confluence/prop attuale — la maggior parte delle skill (VCP, CANSLIM, dividend, 13F, breadth S&P) non tocca il dominio operativo di oggi. Secondo: anche la parte trasversale (regime detection, edge pipeline, journaling) ricade sotto "tooling/agenti custom", che ../../DECISIONS.md mette **in fondo** dopo OctoBot, dati e prop. È prezioso come **riferimento di design** (come strutturare un sistema di skill: layer regime→portfolio→swing→planning→memory→edge, matrice dipendenze, quality gate anti-overfit) più che come cosa da adottare ora. Aggancio naturale: se/quando lo Stock Selector si estende oltre SP500 o si vuole un workflow di review più sistematico.

## Collegamenti

- ../../PROJECT.md → "Asset esterni" — il repo `claude-trading-skills` è già censito tra gli asset esterni dell'utente.
- `claude_code_for_trading.md` (questa cartella) — la guida meta che presenta e contestualizza questo stesso catalogo (Part 4-5-8).
- `insider_constellation.md` (questa cartella) — Institutional Flow Tracker (13F) ⇄ scout Maggie; skill sentiment/macro ⇄ Frank.
- ../../DECISIONS.md — ordine priorità workspace 2026-05-30.

## Fonti

- `_sorgenti/Appunti estratti da pdf key concept.txt` — descrizioni skill per area + matrice dipendenze API completa (FMP/FINVIZ/Alpaca) dal README e skills-index.yaml del repo.
- `_sorgenti/Claude_Code_for_Trading_SoulzBTC docx (2)_260522_110338.pdf` — Part 4 (overview toolkit), Part 5 (ogni skill), Part 8 (tabella API), Part 10 (meta tooling + self-improvement loop).
