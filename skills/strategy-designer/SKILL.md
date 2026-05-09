---
name: strategy-designer
description: Progettare una nuova strategia di trading meccanica partendo da un PDF di analisi tecnica, da un'idea di Matteo, o da un pattern osservato. Usare quando si vuole creare una nuova cartella in strategies/ e codificare le regole di entrata/uscita.
---

# Skill — Strategy Designer

Trasforma un pattern di trading (descritto a parole, in un PDF, o in un grafico) in una **strategia
meccanica** pronta per backtest e per paper trading.

Ricorda: **il trading è meccanico**, non agent-driven. Le regole devono essere completamente
codificabili.

## Workflow di design di una strategia

### 1. Comprensione

Prima di scrivere codice, riassumi a parole (e mostra a Matteo per approvazione):
- **Mercato target**: forex/CFD su MT5? equities? crypto?
- **Timeframe**: scalping (M1-M5), intraday (M15-H1), swing (H4-D1), position (D1-W1)?
- **Direzione**: long-only, short-only, bidirezionale?
- **Setup di entrata**: condizione precisa (es. "RSI < 30 AND prezzo > EMA200 AND candle = bullish engulfing").
- **Setup di uscita**: stop loss + take profit (in pip / %, in ATR, in struttura)?
- **Filtro temporale**: solo certe sessioni? evitare news?
- **Position sizing**: % del capitale, fisso, ATR-based, Kelly?
- **Riferimenti**: quale PDF/libro/articolo descrive la strategia.

### 2. Scaffold

Copia `strategies/_template/` in `strategies/<nome_strategia>/` e popola:
- `strategy.py` — classe che eredita da `StrategyBase`.
- `config.yaml` — tutti i parametri numerici (mai hardcoded nel codice).
- `README.md` — riassunto della strategia + ipotesi + assunzioni.

### 3. Implementazione

Nel `strategy.py`:
- Metodo `should_enter(market_data) -> Optional[Signal]`: restituisce un `Signal` con
  `{direction, size, sl, tp}` o `None` se nessuna entrata.
- Metodo `should_exit(market_data, position) -> bool`: restituisce True se va chiusa la posizione.
- Metodo `get_required_data() -> DataRequirement`: dichiara cosa serve (timeframe, lookback, indicatori).

### 4. Validazione minima

Prima di passare al backtest:
- Test unitari su dati sintetici dove l'output atteso è noto.
- Smoke test su 1 mese di dati reali — controlla che siano stati generati segnali plausibili.

### 5. Backtest e iterazione

Invoca la skill `backtest-runner` per testare. Se i risultati sono coerenti con l'ipotesi
(es. la strategia di trend-following ha drawdown elevati ma profitto positivo nel lungo periodo)
→ procedere a paper trading. Altrimenti → torna al punto 1.

## Pattern teorici di riferimento (PDF in cartella)

- `NYSE Scalping Strategy_251011_114145.pdf` — scalping su sessione US.
- `Candle Structures.pdf` — pattern di candele (engulfing, pin bar, inside bar, ecc.).
- `Art of Confluence Trading.pdf` — multi-timeframe confluence.

Quando si attiva questa skill **e** Matteo cita uno di questi PDF, leggere quello specifico
prima di proporre lo scaffold.

## Output atteso

Una nuova strategia in `strategies/<nome>/` con:
- `strategy.py` funzionante (passa i test unitari).
- `config.yaml` completo.
- `README.md` con ipotesi, regole, fonte teorica.

## Riferimenti

- Template: `strategies/_template/`.
- Pattern broker-agnostic: `brokers/base.py`.
- Pattern signal: `notifiers/base.py` (vedi `Signal` dataclass).
