---
titolo: "Hermes — Feedback Loop Optimizer per strategie"
fonti:
  - "_sorgenti/hermes feedback loop optimizer for strategies.txt"
tipo: blueprint
---

# Hermes — Feedback Loop Optimizer per strategie

> **STATO: idea — NON committata.** Vedi ../../DECISIONS.md (priorità 2026-05-30: OctoBot prima, dati Confluence+Telegram, prop; agenti/strategie custom PER ULTIME). Questo è materiale di riferimento, non un mandato a costruire.

## Cosa è

Agente di trading **auto-migliorante** che fa girare una strategia 24/7 in paper mode su un servizio cloud e raffina **una sola variabile per ciclo** seguendo il metodo scientifico. L'architettura separa due pezzi:

- **Worker** (il pezzo "stupido"): tira dati di mercato, esegue paper trade secondo la strategia corrente, logga ogni esito.
- **Hermes** (il "cervello"): l'agente open-source di **NousResearch** che osserva gli esiti del worker, scrive ipotesi, edita il file di strategia — un parametro alla volta — e ridistribuisce.

L'obiettivo dichiarato NON è automatizzare la decisione di trading in sé, ma dimostrare un loop di ottimizzazione disciplinato: ogni ciclo cambia esattamente una variabile, conserva la versione precedente, e misura se lo score migliora. Pensato come setup paper-only su crypto (ccxt: `BTC/USDT`, `ETH/USDT`, ecc.).

## Architettura

**Goal state** (`state/goal.yaml`) — definito una volta in fase di intake, fissa cosa è successo/fallimento:

```yaml
asset: "BTC/USDT"
target_return_30d: 0.05     # success
max_drawdown:      0.08     # failure
min_sharpe:        1.2      # quality bar
failure_below:     -0.04    # score floor — sotto questo, score steeply negative
reflection_every:  5        # cadenza ciclo (default 5 trade chiusi)
one_variable_only: true     # guardrail metodo scientifico
```

**Strategia v01** (`state/strategy.yaml`) — punto di partenza, poi evolve di versione in versione:

```yaml
version: "01"
entry:
  indicator: rsi
  threshold: 30          # entry quando RSI < 30
  direction: long
stop_loss_pct: 2.0       # stop 2%
position_size_r: 0.5     # size 0.5R
```

**Worker** (Python, deploy su **Railway**, container Docker):
- `run.py` — entrypoint, legge `--asset` da `goal.yaml`.
- `loop.py` — loop async, ogni minuto: pull dati via adapter, valuta `strategy.yaml`, eventuale paper trade, logga su `trades.jsonl`, scrive heartbeat. Retry per-adapter (3, esponenziale), circuit-break dopo 5 fallimenti consecutivi.
- `score.py` — `score(trades, goal) -> float in [-1, +1]`: composito di (return realizzato vs target), (drawdown vs max), (Sharpe vs min).
- `reflect.py` — ciclo di riflessione con due modalità:
  - `--fallback` **deterministico** (usato prima che Hermes prenda il controllo): se return < target → allenta `entry.threshold` di 2; se drawdown > max → stringe `stop_loss_pct` di 0.2. Cambia sempre **una sola** variabile, bumpa versione, salva la precedente in `state/history/v{NNNN}.yaml`, appende a `hypotheses.jsonl`.
  - `--hermes` **produzione**: legge gli ultimi ~25 trade + strategia corrente, formatta come prompt, chiama `hermes` come subprocess, parsa l'ipotesi e la applica.
- `adapters/{price,onchain,news,macro}.py` — ognuno espone `async def fetch() -> dict` con `schema_version`; mismatch di schema → `SchemaError` che ferma il loop. Endpoint pubblici gratuiti di default, chiavi premium via `.env`.

**Volume persistente su Railway** (i container sono altrimenti ephemeral) montato su `/app/state`, contiene: `goal.yaml`, `strategy.yaml`, `trades.jsonl`, `hypotheses.jsonl`, `history/`, `heartbeat.json`.

**Hand-off a Hermes**: dopo l'install locale di Hermes (NousResearch, `install.sh` su Mac/Linux, `install.ps1` su Windows), l'agente entra in standby-loop: ogni 30 min controlla i log Railway; ogni `reflection_every` trade chiusi, scarica gli ultimi 25 esiti + strategia, li scora contro `goal.yaml`, tagga il regime di mercato, genera 1-3 ipotesi (ognuna nomina UNA variabile e predice la direzione dello score), applica quella a confidenza più alta, bumpa versione, ridistribuisce con `railway up --detach`. Vincolo hard: **mai più di una variabile per ciclo**.

**Fasi di deploy** (one-shot guidato in una sola sessione terminale):
1. Environment check (Git, Node.js per la Railway CLI).
2. Definizione strategia (le 5 domande di intake → `goal.yaml`).
3. Scaffold del worker in locale (`uv init` + deps: ccxt, yfinance, pyyaml, httpx, aiofiles, numpy, pandas, rich).
4. Deploy worker su Railway (volume persistente + `railway up`).
5. Primo ciclo di riflessione con il fallback deterministico (prova il meccanismo).
6. Install di Hermes in locale (per ultimo, per non rompere la sessione).
7. Hand-off a Hermes (briefing + standby loop).

## Cosa servirebbe per costruirlo

- **Account Railway** (free tier per iniziare) + Railway CLI (richiede Node.js).
- **Git** e ambiente Python con `uv`.
- **Hermes** installato in locale (agente open-source NousResearch) — fa da cervello e chiama il modello.
- **Chiave Claude API** per il ragionamento di Hermes (il loop di riflessione gira via API).
- Adapter dati: endpoint pubblici gratuiti bastano per partire; chiavi premium opzionali (`EXCHANGE_API_KEY`, `GLASSNODE_API_KEY`, `NEWS_API_KEY`) via `.env`.
- Per il passaggio a live (sconsigliato all'inizio): flippare `HERMES_TRADING_MODE=live` e `HERMES_TRADING_I_ACCEPT_RISK=true`, poi ridistribuire.

## Perché è rimandato

Le priorità del workspace al 2026-05-30 (vedi ../../DECISIONS.md) mettono **OctoBot per primo**, poi la raccolta dati Confluence+Telegram, poi la prop; **agenti/strategie custom in fondo**. Hermes è esattamente "agente + strategia custom": un loop di ottimizzazione self-improving che richiede infrastruttura cloud dedicata (Railway), un secondo agente locale (Hermes) e budget Claude API ricorrente. Costruirlo ora significherebbe scavalcare l'ordine deciso. Inoltre il suo valore è di processo (disciplina one-variable-at-a-time), non di edge dimostrato: andrebbe comunque triangolato con razionale + walk-forward prima di prenderlo sul serio. Materiale di riferimento, da ripescare quando le strategie automatiche custom risaliranno in cima alla coda.

## Collegamenti

- ../../DECISIONS.md — ordine priorità workspace 2026-05-30.
- `claude_code_for_trading.md` (questa cartella) — concetto di "headless mode" e self-improvement loop, parente concettuale.
- `insider_constellation.md` (questa cartella) — altro sistema multi-agente paper/informational, stessa logica di guardrail "non fa trade da solo / un passo per volta".
- Concetto di score [-1,+1] e reflection: imparenta con il quant-review interno (walk-forward, niente look-ahead).

## Fonti

- `_sorgenti/hermes feedback loop optimizer for strategies.txt` — prompt one-shot di onboarding (framework agente NousResearch / Hermes; deploy worker su Railway; goal.yaml, strategy.yaml v01, reflect fallback/hermes, score, fasi 1-7).
