# brokers/

Astrazione **broker-agnostic**. Lo stesso signal può essere ruotato sul broker giusto a seconda
della strategia.

## Stato

Stub al momento. Le implementazioni concrete vengono riempite stage per stage:
- `mt5.py` → Stage 2.
- `ibkr.py` → Stage 1 (paper trading per Stock Selector).
- `coinbase.py` / `binance.py` → Stage 6.

## Pattern

Tutte le implementazioni ereditano da `BrokerBase` (`base.py`). L'interfaccia minima:

| Metodo | Cosa fa |
|---|---|
| `connect()` | Apre la connessione al broker |
| `disconnect()` | Chiude |
| `get_market_data(symbol, timeframe, bars)` | Restituisce DataFrame OHLCV |
| `get_position(symbol)` | Restituisce posizione corrente o None |
| `place_order(signal)` | Piazza ordine (rispettando paper_mode flag) |
| `close_position(position)` | Chiude posizione |
| `is_paper()` | Restituisce True se in paper/demo mode |

## Sicurezza

Ogni broker concreto deve avere il flag `paper_mode` settato a **True per default**.
Passare a live mode richiede:
1. Modifica esplicita del file `.env` (es. `IBKR_PAPER_MODE=false`).
2. Commit dedicato sul repo che documenta il passaggio.
3. Verifica che il risk gate (`config/risk.yaml`) sia configurato.
