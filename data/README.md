# data/

Sorgenti dati e cache locale.

## Sorgenti previste

| Sorgente | Tipo dati | Costo |
|---|---|---|
| `yfinance` | Equities (SP500), ETF, indici | Gratis (rate limited) |
| `ccxt` | Crypto OHLCV via exchange | Gratis |
| `MT5 export` | Forex/CFD | Gratis (richiede terminale MT5) |
| `worldmonitor` (Stage 5) | News + 7-signal radar + macro. **Mai costruito** (25/10): non ha uno storico datato, quindi non regge un backtest; vedi `magazzino/registro/referti/idee_matteo_hub_intake_2026-10-25.md`, voce 6 | Locale |
| `financialdatasets.ai` | Fondamentali equities (alternativa a yfinance) | A pagamento |
| SEC Financial Statement Data Sets e Insider Transactions Data Sets | fondamentali USA point-in-time dal 2009 (non ancora scaricati); **Form 3/4/5 dal 2006: scaricati il 05/11** con `python data/scarica_sec_form345.py` (serve il contatto in `data/cache/sec/user_agent.txt`, fuori da git), tabella `data/cache/sec/form345_mercato.parquet` | Gratis — `magazzino/registro/referti/ricerca_dati_2026-10-25.md` |
| `Johnbrick123/sp500-data` (release congelata `snapshot-2026-11`) | S&P 500 dal 1970 **con i delistati**: prezzi giornalieri rettificati, appartenenza per intervalli (`membership_intervals.parquet`; `members.parquet` ha solo 3.041 date, non usarlo per l'appartenenza giornaliera), giorni senza scambi, uscite in gap | Gratis, **licenza non dichiarata: solo uso locale** — `python data/scarica_sp500_data.py`, output in `data/cache/sp500data/<snapshot>/` con `MANIFEST.json` (sha256). Controlli del 05/11 nella nota `magazzino/registro/referti/azionario_insider_polymarket_2026-11-05.md` §5 |
| CBOE `VIX_History.csv` | VIX giornaliero dal 1990 (backlog G4) | Gratis — `python data/scarica_serie_libere.py` |
| CFTC Commitments of Traders | posizionamento settimanale sui futures: Legacy dal 1986, Disaggregated dal 2006 (backlog G5) | Gratis — stesso script, output in `data/cache/free/` |

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
