---
titolo: "Claude Code for Trading — guida meta (SoulzBTC)"
fonti:
  - "_sorgenti/Claude_Code_for_Trading_SoulzBTC docx (2)_260522_110338.pdf"
tipo: blueprint
---

# Claude Code for Trading — guida meta (SoulzBTC)

> **STATO: idea — NON committata.** Vedi ../../DECISIONS.md (priorità 2026-05-30: OctoBot prima, dati Confluence+Telegram, prop; agenti/strategie custom PER ULTIME). Questo è materiale di riferimento, non un mandato a costruire.

## Cosa è

Guida **meta** su Claude Code come **agente** per workflow di trading — non è una strategia, è un modo di lavorare. Tesi di fondo: per la prima volta un singolo trader può costruire ed eseguire workflow di ricerca che prima richiedevano un team quant intero. Il vantaggio non è "l'AI che decide meglio", ma **avere più tempo e informazione più pulita per decidere meglio da soli**: Claude Code rimuove l'overhead amministrativo, non sostituisce il giudizio. Indice della guida (12 parti): storia dell'AI nel trading, cosa è Claude Code, 15 core concepts, overview del toolkit `claude-trading-skills`, ogni skill in dettaglio, workflow reali, 6 lezioni da 900+ ore, tabella API completa, setup/costi API, meta tools + self-improvement, percorso settimana-per-settimana, parola finale.

## Architettura (concetti chiave)

**Storia (Part 1)** — dal modello Black-Scholes (1973) → program trading anni '80 → Bloomberg terminal anni '90 → Renaissance/Medallion → HFT → API retail (Interactive Brokers/Alpaca) → ML → ChatGPT (2022) → coding assistant (2023) → **Claude Code (2024)** che rompe la barriera per i non-coder → era MCP (2024-25). Tesi: ogni shift apre una "finestra" per gli early mover; quella di Claude Code è aperta ora.

**Agent vs chatbot (Part 2)** — un chatbot genera solo testo (niente file, niente codice, niente API, memoria solo di sessione). Un **agente** agisce: legge/scrive file, esegue script, installa software, chiama API via MCP, concatena task, ha memoria persistente via `CLAUDE.md`. Claude Code è un agente.

**3 tool built-in** — **Read** (legge file/dati), **Write** (crea/aggiorna file), **Bash** (esegue comandi terminale, script Python, eseguibili). L'utente descrive il goal; Claude Code sequenzia i tool da solo.

**15 core concepts (Part 3):** (1) Terminal, (2) Prompt — la specificità è tutto (weak vs strong), (3) Permissions (gate su internet/install), (4) i 3 tool, (5) Context window (una task per sessione, `/compact`, `/clear`), (6) **CLAUDE.md** = memoria permanente (formato dati, exchange, regole di rischio, sizing, librerie, definizioni setup), (7) Memory vs CLAUDE.md, (8) Modelli (Haiku economico/veloce, Sonnet default ~90% del lavoro, Opus reasoning complesso), (9) `/compact` e `/clear`, (10) MCP server, (11) slash command & skill, (12) sub-agent (specialisti in parallelo), (13) **headless mode** (`-p`, schedulabile via cron), (14) worktrees (istanze isolate sullo stesso progetto), (15) voice prompt (più lunghi e completi del testo).

**Toolkit (Part 4-5)** — il repo open-source **`claude-trading-skills`** (`github.com/tradermonty/claude-trading-skills`): 40+ skill in 6 aree (Market Regime, Core Portfolio, Swing Opportunity, Trade Planning, Trade Memory, Strategy Research) + satellite + meta. Dettaglio completo in `claude_skills_catalog.md`. Cinque workflow di partenza consigliati (daily market check, weekly portfolio review, swing opportunity, trade-memory loop, monthly performance review).

**MCP** — Model Context Protocol: layer di connessione tra Claude Code e fonti dati esterne (exchange, data provider, portfolio tracker), tutto orchestrato da una conversazione.

**6 lezioni (Part 7)** — pianifica prima di costruire; modello mentale "junior quant" (capace, veloce, confidentemente sbagliato se vago → istruzioni precise e bounded); una task per sessione; costruisci `CLAUDE.md` nella settimana 1; voice-prompt tutto; chi vince non è il miglior coder ma il miglior "manager" dell'agente.

**Setup/costi API (Part 9)** — stack gratuito copre market review + journaling completi. FMP free tier (250 req/giorno). FINVIZ Elite ($39.50/mese, opzionale). Alpaca paper gratis (con `ALPACA_PAPER=true`). Claude Code incluso nella subscription Claude.

**Meta + self-improvement (Part 10)** — loop automatico che sceglie una skill a rotazione, la scora (Dual-Axis Reviewer, gate 90/100) e apre PR di miglioramento; + pipeline di auto-generazione skill dai log di sessione.

**Percorso settimanale (Part 11)** — Settimana 1: install + `CLAUDE.md` + primo regime check + prima trade review + audit position sizing. Settimana 2: aggiungi FMP. Settimane 3-4: inizia a screenare (senza tradare). Mese 2: workflow integrato. Mese 3+: automazione headless + edge research.

## Cosa servirebbe per costruirlo / applicarlo

- **Claude Code** installato (via subscription Claude) e un progetto con `CLAUDE.md` ben fatto.
- Il repo `claude-trading-skills` clonato (per le skill).
- Opzionali a scaglioni: **FMP free tier** → **Alpaca paper** → **FINVIZ Elite** solo se serve velocità.
- Disciplina operativa: una task per sessione, prompt specifici, planning prima del codice.

## Perché è rimandato

Questa guida non è una "cosa da costruire" ma il **manuale d'uso meta** dietro `claude_skills_catalog.md` — ed è centrata su workflow **equity-US/crypto** (SoulzBTC), fuori asse rispetto al focus forex/Confluence/prop attuale. Diverse pratiche sono già di fatto adottate nel workspace (CLAUDE.md, sub-agent come quant-reviewer, una-task-per-sessione). Adottare il toolkit completo o l'automazione headless ricade sotto "tooling/agenti custom", che ../../DECISIONS.md mette **in fondo** dopo OctoBot, dati e prop. Vale come riferimento concettuale (agent vs chatbot, i 15 concept, il modello "junior quant", il percorso settimanale), da ripescare quando la coda delle priorità arriverà al tooling.

## Collegamenti

- `claude_skills_catalog.md` (questa cartella) — il catalogo dettagliato delle 40+ skill descritte qui (Part 4-5-8).
- ../../PROJECT.md → "Asset esterni" — il repo `claude-trading-skills` tra gli asset esterni dell'utente.
- `hermes_optimizer.md` (questa cartella) — esempio concreto di headless/self-improvement loop applicato a una strategia.
- ../../DECISIONS.md — ordine priorità workspace 2026-05-30.

## Fonti

- `_sorgenti/Claude_Code_for_Trading_SoulzBTC docx (2)_260522_110338.pdf` — guida completa SoulzBTC, 12 parti (storia, agent vs chatbot, 3 tool, 15 core concepts, toolkit + ogni skill, workflow, 6 lezioni, tabella API, setup/costi, meta/self-improvement, percorso settimanale, parola finale).
