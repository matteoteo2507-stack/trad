# `_template/` — Scaffold per una nuova strategia

Copia questa cartella in `strategies/<nome_strategia>/` e personalizza i 3 file.

## Documenta la tua strategia qui

### Mercato target
(es. forex EURUSD su MT5 demo)

### Timeframe
(es. H1)

### Direzione
(long-only / short-only / bidirezionale)

### Ipotesi di mercato
Una o due frasi: *perché* dovrebbe funzionare? Cosa stai cercando di catturare?
(es. "i pullback contro trend su mercati a forte momentum vengono comprati nel medio periodo")

### Setup di entrata
Condizioni precise. Esempio:
- prezzo > EMA200 (filtro di trend);
- RSI(14) attraversa dal basso il livello 30;
- la candela di segnale ha range > ATR(14) * 0.8;
- tutti e 3 i punti contemporaneamente.

### Setup di uscita
- SL: 1.5 × ATR sotto il minimo della candela di segnale.
- TP: 3 × ATR (R/R 2:1).
- Uscita anticipata: prezzo chiude sotto EMA200.

### Filtri
- Solo sessione London + NY overlap (UTC 12:00–16:00).
- Evita 30 min prima/dopo news ad alto impatto.

### Riferimento teorico
Citare il PDF/libro/articolo da cui viene la strategia.

## Validazione minima

Prima di passare al backtest:
1. Implementa `strategy.py` e completa `config.yaml`.
2. Esegui i test unitari (`pytest tests/test_<nome>.py`).
3. Smoke test su 1 mese di dati reali — controllare manualmente i segnali sui grafici.

## Backtest

Invoca la skill `backtest-runner` con la strategia come argomento.
