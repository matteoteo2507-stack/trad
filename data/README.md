# data/

Sorgenti dati e cache locale.

## Sorgenti previste

| Sorgente | Tipo dati | Costo |
|---|---|---|
| `yfinance` | Equities (SP500), ETF, indici | Gratis (rate limited) |
| `ccxt` | Crypto OHLCV via exchange | Gratis |
| `MT5 export` | Forex/CFD | Gratis (richiede terminale MT5) |
| `worldmonitor` (Stage 5) | News + 7-signal radar + macro | Locale |
| `financialdatasets.ai` | Fondamentali equities (alternativa a yfinance) | A pagamento |

## Cache

`data/cache/` contiene i dati storici scaricati per evitare di rifare fetch ad ogni backtest.
Convenzione di naming:

```
data/cache/<source>/<symbol>_<timeframe>_<start>_<end>.parquet
```

Esempio: `data/cache/yfinance/AAPL_1d_2020-01-01_2026-04-29.parquet`.

La cache è ignorata da git (vedi `.gitignore`).

## Stage 1+

Stage 1: fetcher SP500 list + dati storici via yfinance (per il porting del notebook V6.0).
Stage 5: bridge con worldmonitor (lettura dei signal correnti per filtrare strategie).
