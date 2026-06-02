---
titolo: "Insider Constellation — 7 agenti di segnale equity-US / on-chain"
fonti:
  - "_sorgenti/isider trading.txt"
tipo: blueprint
---

# Insider Constellation — 7 agenti di segnale equity-US / on-chain

> **STATO: idea — NON committata.** Vedi ../../DECISIONS.md (priorità 2026-05-30: OctoBot prima, dati Confluence+Telegram, prop; agenti/strategie custom PER ULTIME). Questo è materiale di riferimento, non un mandato a costruire.

## Cosa è

Costellazione di **7 agenti** che leggono segnali pubblici (filing governativi US, discorsi Fed, movimenti on-chain, drift del proprio portfolio) e recapitano un alert via Gmail/Telegram **solo quando almeno 3 scout concordano** su stesso ticker + direzione. Tre dipartimenti: 5 scout, 1 consensus, 1 dispatcher. Ogni agente è un piccolo script Python; gli scout chiamano Claude via Anthropic SDK e scrivono segnali strutturati in SQLite; consensus e dispatcher sono pura logica locale. **Nessun agente piazza trade**: l'output è informativo, la decisione resta umana.

Nota: è materiale **equity-US / on-chain** (SEC Form 4, 13F, discorsi Fed, whale crypto, allocazione portfolio), quindi **ortogonale** alle priorità attuali (forex/Confluence/prop).

## Architettura

**Gli scout (5)** — ognuno emette un record segnale `{scout, ticker, direction, confidence 1-5, reason, ts}`:

| Agente | Legge | Filtro / cadenza |
|--------|-------|------------------|
| **Eddie**  | SEC Form 4 (insider buy) | acquisti open-market ≥ $100k da CEO/CFO/President/Chairman/Director; daily 06:00 |
| **Maggie** | 13F-HR di 5 mega-fund (Berkshire, Bridgewater, Renaissance, Citadel, Two Sigma) | nuove posizioni / incrementi / uscite ≥ $50M vs trimestre prima; weekly Dom 19:00 |
| **Frank**  | Discorsi Fed + commenti FOMC | net tilt hawkish/dovish (dovish→BULLISH, hawkish→BEARISH per risk asset); weekly Lun 08:00 |
| **Maya**   | Whale on-chain (WBTC/WETH/USDC/USDT) | transfer ≥ $5M (CEX→privato = accumulo BULLISH; privato→CEX = distribuzione BEARISH); ogni 6h; usa **Haiku** (gira spesso, cost-sensitive) |
| **Janet**  | Drift del portfolio dell'utente vs target | flagga posizioni con drift > 5pp (overweight→BEARISH/trim, underweight→BULLISH/add); daily 17:00; legge `portfolio_target.json` + `portfolio_current.json` |

**Il consensus (1) — Sophie**: legge la finestra mobile a 7 giorni dei segnali scout (scarta i NEUTRAL, dedup per scout). Emette un evento **CONSENSUS** quando ≥ 3 scout concordano su stesso (ticker, direzione). Gira ogni 30 min. Soglia/finestra configurabili (`SOPHIE_MIN_AGREE=3`, `SOPHIE_WINDOW_DAYS=7`).

**Il dispatcher (1) — Ross**: quando Sophie spara, invia una Gmail (sempre, SMTP via app password) + Telegram (se configurato). **Mai piazza trade.** Gira ogni 30 min, idempotente: ri-eseguito senza eventi pendenti è un no-op; non marca dispatched se l'email fallisce (retry al run successivo).

**Store** — SQLite a `~/insider-routines/.state/state.db`, due tabelle:
- `signals` — `(id, scout, ticker, direction, confidence, reason, raw, ts)`, indice su `ts`.
- `consensus` — `(id, ticker, direction, scouts, reasons, ts, dispatched)`.

I prompt scout chiudono con un blocco JSON stretto `{"ticker", "direction": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-5>, "reason"}`; `common.py` parsa l'**ultimo** oggetto JSON nella risposta. Se nessun segnale qualificante → placeholder NEUTRAL su `MACRO`.

**Scheduling** — job OS reali: **launchd** su Mac, **crontab** su Linux, **Task Scheduler** su Windows. Installer idempotenti (re-run = pulizia + reinstall), log in `~/insider-routines/.state/logs/`. Modelli configurabili (Sonnet scout di default, Haiku per Maya). Delivery Gmail richiede app password (2-Step Verification attiva); Telegram opzionale via @BotFather.

## Cosa servirebbe per costruirlo

- **Python 3.10+** + `pip install anthropic python-dotenv`.
- **Chiave Anthropic API** (`ANTHROPIC_API_KEY`) — gli scout chiamano Claude (Sonnet/Haiku).
- **Gmail con app password** (richiede 2-Step Verification) per il dispatch via SMTP; **Telegram bot** opzionale.
- Scheduler OS abilitato (launchd/cron/Task Scheduler) — su macchine corporate bloccate, fallback a run manuale.
- Per Janet: due file di config (`portfolio_target.json`, `portfolio_current.json`); se mancano, Janet si auto-skippa.
- Capacità di web research/parsing degli scout (EDGAR, federalreserve.gov, explorer on-chain).

## Perché è rimandato

Doppio motivo. Primo: l'**ordine di priorità** (../../DECISIONS.md) tiene agenti custom in fondo, dopo OctoBot, dati e prop. Secondo, più dirimente: è materiale **equity-US/on-chain**, completamente fuori asse rispetto al focus forex/Confluence/Telegram-copier attuale — non alimenta nessuna delle priorità in cima. È un sistema "informational, non esecutivo" interessante come pattern (consensus ≥3, dispatcher che non fa trade, store SQLite), ma il suo dominio di dati non serve oggi. Ripescabile solo se/quando il workspace si estende all'equity US (cfr. roadmap Stock Selector globale) — e anche lì andrebbe ripensato.

## Collegamenti

- ../../DECISIONS.md — ordine priorità workspace 2026-05-30.
- `hermes_optimizer.md` (questa cartella) — stesso DNA multi-agente paper/informational con guardrail forti.
- `claude_skills_catalog.md` (questa cartella) — l'**Institutional Flow Tracker** (13F) e gli scout sentiment/macro coprono terreno simile a Maggie/Frank.
- Stock Selector globale (memoria progetto) — eventuale aggancio futuro se il workspace andasse verso equity US.

## Fonti

- `_sorgenti/isider trading.txt` — prompt one-shot di onboarding "Insider Routines" (canale Lewis Jackson): 7 agenti, codice `common.py` + i 5 scout + Sophie + Ross, schema SQLite, installer launchd/cron/Task Scheduler, fasi 1-5.
