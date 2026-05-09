# Architettura del workspace — v2 (post-pivot 2026-05-05)

> Questo documento sostituisce `STAGE2_TESTING_PLAN.md` come riferimento operativo.
> Il file vecchio resta come archivio storico.

## Visione d'insieme

Tre componenti, tre habitat, **deployment indipendenti**:

```
┌────────────────────────┐  ┌──────────────────────────┐  ┌────────────────────┐
│ COMPONENTE 1           │  │ COMPONENTE 2             │  │ COMPONENTE 3       │
│ Confluence Levels      │  │ London Open Breakout     │  │ Stock Selector     │
│ (Python)               │  │ (Expert Advisor MQL5)    │  │ + Consensus LLM    │
│                        │  │                          │  │ (Python)           │
│ SOLO NOTIFICA          │  │ AUTOMATICA (esegue)      │  │ TOOL OFFLINE       │
│                        │  │                          │  │                    │
│ Habitat:               │  │ Habitat:                 │  │ Habitat:           │
│ VPS Linux 0-5€/mese    │  │ MetaQuotes VPS 9€/mese   │  │ PC di casa         │
│                        │  │                          │  │ (lanciato a mano)  │
│                        │  │                          │  │                    │
│ Datasource: yfinance   │  │ Datasource: tick reali   │  │ Datasource:        │
│ Output: Telegram       │  │ Output: ordini broker +  │  │   yfinance, LLM    │
│                        │  │         Telegram         │  │ Output: Excel      │
└────────────────────────┘  └──────────────────────────┘  └────────────────────┘
            │                            │                          │
            └────────────────────────────┴──────────────────────────┘
                            Tutti notificano lo stesso bot Telegram
                              (token+chat_id condivisi via .env)
```

**Niente bridge** tra i tre componenti. Ognuno ha il suo Telegram outbound, il suo
deployment, il suo log. Zero accoppiamento, zero failure mode condivise.

---

## Componente 1 — Confluence Levels (Python)

### Cosa fa

L'utente compila a mano `strategies/confluence_levels/levels.yaml` ogni weekend con la mappa
dei livelli (S/R + S/D + Fibonacci in confluenza) per EURUSD e XAUUSD.

Il runner Python:
- Polling ogni 60s del prezzo da yfinance.
- Per ogni livello: verifica prossimità (≤ 15 pip default), filtri (sessione 9-18 Roma,
  news, RR ≥ 3, SL strutturale ≤ 30 pip EUR / 200 pip XAU, dedup giornaliero).
- Invia notifica Telegram con i dettagli del setup.

L'utente decide se piazzare l'ordine a mano dall'app del broker (telefono o PC).

### Deployment

**Locale (sviluppo, primo test)**:

```bash
cd c:/Users/mmbus/Desktop/lavoro/trad
python -m strategies.confluence_levels validate-levels
python -m strategies.confluence_levels run                  # default yfinance
python -m strategies.confluence_levels run --datasource mt5 --account DEMO1   # legacy
```

**Cloud (produzione)**: VPS Linux economico, sempre online.

Opzioni di hosting:
- **Hetzner CX11** ~3.5€/mese (1 vCPU, 2GB RAM, Linux Ubuntu).
- **Oracle Cloud Always Free** gratis a vita (4 ARM cores, 24GB RAM, sempre disponibile).
- **fly.io free tier** (3 VM piccole gratis).

Setup tipico VPS Linux:
```bash
git clone <repo> trad
cd trad
python -m venv venv
source venv/bin/activate
pip install -e .   # o pip install -r requirements.txt
cp .env.example .env  # poi compila TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

Per girare in background, usa `systemd` user service o `tmux`/`screen`.

### Configurazione

- `strategies/confluence_levels/config.yaml`: parametri della strategia.
- `strategies/confluence_levels/levels.yaml`: input umano weekly (gitignored).
- `.env`: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.

### Test

```bash
python -m pytest tests/
```

Atteso: 81/81 verdi (offline) + 2 skipped (live yfinance).

---

## Componente 2 — London Open Breakout (Expert Advisor MQL5)

### Cosa fa

EA scritto in MQL5 nativo che gira dentro il terminale MetaTrader 5. Replica la logica della
strategia Python originale che era in `strategies/london_breakout/` (eliminata nel pivot).

Operazioni:
- 00:00–07:00 UTC: costruzione range Asia (high/low M15) per il simbolo configurato.
- 07:00 UTC: piazzamento di due stop orders (buy_stop / sell_stop) con SL al lato opposto del
  range e TP a 1.5R.
- 10:00 UTC: cancellazione degli ordini non scattati.
- 16:00 UTC: time stop, chiude posizioni residue.
- Filtri: skip range esaurito (>1.5×ATR_D1), NFP (primo venerdì), FOMC (lista date in input).

### Deployment

**Test locale (1-2 settimane)**:

1. MT5 desktop loggato sul demo MetaQuotes (DEMO2 nel `.env`).
2. Copia `mql5/london_breakout.mq5` + `mql5/include/*.mqh` in `<MT5 Data Folder>/MQL5/Experts/...`.
3. Compile in MetaEditor (F7).
4. Aggancia EA a grafico GBPUSD M15.
5. Verifica notifiche Telegram + ordini piazzati.

**Produzione (MetaQuotes VPS, dopo validazione)**:

1. Da app mobile MT5: tab "VPS" → Subscribe (10$/mese, regione vicino al broker).
2. Migrate to virtual server. EA + chart trasferiti automaticamente.
3. PC di casa libero. Monitor da app mobile.

Vedi `mql5/README.md` per istruzioni dettagliate.

### Backtesting

Strategy Tester MT5: tick reali, modello spread variabile, 6 mesi GBPUSD M15.
Atteso: trade frequency 15-20/mese, win rate 45-55%, max DD < 10%.

### Configurazione

Tutti i parametri sono `input` dell'EA (settabili dal dialog MT5 quando agganci l'EA al grafico):
finestre temporali, ATR period, TP multiplier, NFP/FOMC blacklist, sizing, Telegram token+chat_id.

---

## Componente 3 — Stock Selector + Consensus LLM (Python offline)

### Cosa fa

- `strategies/stock_selector/`: screening SP500 (V6.0, scoring fundamentale + RRG + scenario macro).
- `agents/consensus/`: 4 personas LLM (Damodaran, Buffett, Burry, Taleb) — Stage 4, da implementare.

### Deployment

PC di casa, lanciato a mano nei weekend. Niente always-on, niente VPS.

```bash
python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing
```

Output: `Top_Picks.xlsx` + `Analisi_Completa.xlsx`.

### Configurazione

- `strategies/stock_selector/config.yaml`: soglie scoring, parametri RRG, lista fallback.

---

## Workflow operativo settimanale

### Domenica sera

1. **Analisi top-down EURUSD/XAUUSD** su TradingView → segna livelli.
2. **Compila** `strategies/confluence_levels/levels.yaml`.
3. `python -m strategies.confluence_levels validate-levels` → verifica.
4. (Se ti serve weekend update) `python -m strategies.stock_selector ...` → top picks.

### Durante la settimana

5. **Componente 1** gira sul VPS Linux 24/7. Niente da fare lato tuo.
6. **Componente 2** gira sul MetaQuotes VPS 24/7. Niente da fare lato tuo.
7. Ricevi notifiche Telegram da entrambi.
8. Quando arriva una notifica Confluence: decidi se piazzare a mano dall'app broker.
9. Quando arriva una notifica London Breakout: è già stato piazzato, è solo info.

### Venerdì sera

10. Compila `notes/week_<data>.md` (template in `STAGE2_TESTING_PLAN.md`):
    - Quante notifiche Confluence, quante avresti piazzato.
    - Trade London Breakout: quanti, win rate, DD.
    - Bug/comportamenti strani.

---

## Costi mensili

| Voce | Costo | Note |
|---|---|---|
| VPS Linux Confluence | 0–5€ | Free tier (Oracle) o Hetzner CX11 |
| MetaQuotes VPS London Breakout | ~9€ | 10 USD/mese, include MT5 |
| Telegram bot | 0€ | Gratuito |
| Yahoo Finance (yfinance) | 0€ | Gratuito |
| **Totale** | **9–14€/mese** | |

---

## Cosa non c'è (esplicito)

- ~~`brokers/mt5.py` non più richiesto~~ Resta come fallback per `--datasource mt5` ma non
  necessario per uso normale.
- ~~`strategies/london_breakout/` Python~~ ELIMINATA. Sostituita da `mql5/london_breakout.mq5`.
- Niente VPS Windows, niente RDP da gestire.
- Niente bridge Python ↔ MQL5 (no file sync, no socket, no HTTP).
- Niente ordini automatici dalla Confluence (decisione utente: solo notifica per design).
- Stage 5 (worldmonitor news), Stage 6 (crypto), Stage 7 (prop firm) sono cycle futuri,
  costruibili sotto questa stessa architettura ibrida.

## Backlog strategie automatiche

In memoria persistente, vedi `~/.claude/projects/.../memory/project_strategies_pipeline.md`:

1. Time Series Momentum (USDJPY D1) — prossima EA MQL5
2. Volatility Targeting overlay — applicabile a tutte le EA
3. Donchian/Turtle classico
4. DXY → EURUSD z-score
5. Mean Reversion intraday
6. KAMA + ATR breakout
7. Carry Trade (deprioritized 2026)

Ogni nuova strategia automatica → nuovo `.mq5` in `mql5/`. Ogni nuova strategia analitica
(ranking, screening, ML) → nuovo `strategies/<nome>/` Python.
