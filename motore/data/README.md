# motore/data/

Sorgenti dati e cache locale.

## Sorgenti previste

| Sorgente | Tipo dati | Costo |
|---|---|---|
| `yfinance` | Equities (SP500), ETF, indici | Gratis (rate limited) |
| `ccxt` | Crypto OHLCV via exchange | Gratis |
| `MT5 export` | Forex/CFD | Gratis (richiede terminale MT5) |
| `worldmonitor` (Stage 5) | News + 7-signal radar + macro. **Mai costruito** (25/10): non ha uno storico datato, quindi non regge un backtest; vedi `magazzino/registro/referti/idee_matteo_hub_intake_2026-10-25.md`, voce 6 | Locale |
| `financialdatasets.ai` | Fondamentali equities (alternativa a yfinance) | A pagamento |
| SEC Financial Statement Data Sets e Insider Transactions Data Sets | fondamentali USA point-in-time dal 2009 (non ancora scaricati); **Form 3/4/5 dal 2006: scaricati il 05/11** con `python motore/data/scarica_sec_form345.py` (serve il contatto in `motore/data/cache/sec/user_agent.txt`, fuori da git), tabella `motore/data/cache/sec/form345_mercato.parquet` | Gratis — `magazzino/registro/referti/ricerca_dati_2026-10-25.md` |
| `Johnbrick123/sp500-data` (release congelata `snapshot-2026-11`) | S&P 500 dal 1970 **con i delistati**: prezzi giornalieri rettificati, appartenenza per intervalli (`membership_intervals.parquet`; `members.parquet` ha solo 3.041 date, non usarlo per l'appartenenza giornaliera), giorni senza scambi, uscite in gap | Gratis, **licenza non dichiarata: solo uso locale** — `python motore/data/scarica_sp500_data.py`, output in `motore/data/cache/sp500data/<snapshot>/` con `MANIFEST.json` (sha256). Controlli del 05/11 nella nota `magazzino/registro/referti/azionario_insider_polymarket_2026-11-05.md` §5 |
| CBOE `VIX_History.csv` | VIX giornaliero dal 1990 (backlog G4) | Gratis — `python motore/data/scarica_serie_libere.py` |
| CFTC Commitments of Traders | posizionamento settimanale sui futures: Legacy dal 1986, Disaggregated dal 2006 (backlog G5) | Gratis — stesso script, output in `motore/data/cache/free/` |

## Prezzi (`prezzi/`)

Il feed di prezzo usato dagli studi: CSV per simbolo e timeframe (`XAU_spot_M5.csv`, `NAS100_M5.csv`...) e le
sottocartelle `dukascopy_d1/`, `mt5_fp_d1/`, `pysystemtrade/`, `_duka_xau_m1_mesi/`, `_duka_xau_tick_ore/`.
Era `analysis/trading-bot-eval/data/`, spostato qui il 10/11: per tipo sono dati, non codice di uno studio.
**Fuori da git** (licenze personali, DECISIONS 2026-11-05): si rigenera con gli script di export degli studi
(`magazzino/registro/codice/trading-bot-eval/export_mt5_spot.py`, `fetch_ohlc.py`, gli export Dukascopy). Prima di
usarne uno: `python -m motore.core.data_checks <file>`.

**Fusi verificati** (allineamento a scarto minimo del rapporto con un future, 11/11): `SPX500_M5.csv` e
`NAS100_M5.csv` sono in **UTC**; `XAU_duka_M1_*.parquet` e' gia' in UTC con fuso dichiarato.

### `prezzi/volatilita_m5/` — Dukascopy M5 della famiglia volatilita' (11/11/2026)

Nove strumenti, bid, UTC senza fuso: SPX500, NAS100, DOW, RUSSELL, DAX, XAUUSD, XAGUSD, WTI, EURUSD, fino al
2026-11-11. Script: `magazzino/registro/codice/volatilita/scarica_dukascopy.py` (stampa solo conteggi: dentro c'e'
l'holdout). Controlli dell'11/11 (solo struttura, nessuna statistica sui rendimenti):
- nessun duplicato, tempi ordinati; 34 barre OHLC incoerenti in NAS100, 0 negli altri;
- **sovrainsieme esatto** dei vecchi `SPX500_M5`, `NAS100_M5`, `DAX_M5`: tutte le barre vecchie ci sono, chiusure
  identiche;
- inizio: RUSSELL **2018-08** (prima 0 barre), XAGUSD **2014-07**, gli altri 2012;
- **il feed degli indici cambia natura**: 2012-2014 dal 50 all'81% di barre ferme (massimo = minimo) sulle 24 ore e
  ~93k barre l'anno, 2015-2017 ~42-50k, dal 2018-2019 ~68k. Nella **seduta cash** (9:30-16:00 New York; DAX 9:00-17:30
  Francoforte) i giorni pieni sono il 95-100% e le barre ferme lo 0% **dal 2015**; nel 2012-2014 fino al 10% di barre
  ferme anche in seduta. EURUSD: 28-29% di barre ferme nel 2012-2013, 0% dal 2015. Per una varianza realizzata
  confrontabile nel tempo: **dal 2015**, e sulla giornata intera (notte compresa) solo dal 2019.
- **Oro, argento, petrolio** (barre ferme sulle 24 ore, % per anno, stesso controllo dell'11/11): XAUUSD **0%** ogni
  anno 2012-2026; XAGUSD 0% nel 2014-2016, **1%** nel 2017-2019, 0% dal 2020; WTI 4% (2012), 3% (2013), **19% (2014)**,
  1% (2015), 0% (2016), 1% (2017), 0% (2018), 1% (2019), 0% dal 2020. Barre per anno 61-76 mila (2026 fino all'11/11).

### `prezzi/volatilita_mt5/` — secondo feed dal terminale MT5 (FP Markets, 11/11/2026)

US500, US100, US30, GER40, XAUUSD, XAGUSD, XTIUSD, EURUSD a M5, da giugno-luglio 2025 all'11/11/2026, colonna
`ora_server` = **New York + 7 ore** tutto l'anno (non convertita). Script `esporta_mt5.py` nella stessa cartella del
codice. Il terminale da' al massimo **100.000 barre** per simbolo (`maxbars`): per avere di piu' va alzato "Max bars in
chart" nelle opzioni di MT5. Serve al confronto con Dukascopy e i futures, non come serie di lavoro.

### `prezzi/futures_1m/` — futures CME a 1 minuto con il flusso degli ordini (dai soci, 11/11/2026)

Otto file `<Nome>_<SIMBOLO>_1min.csv`: oro GC, S&P ES, Nasdaq NQ, Dow YM, Russell RTY, petrolio CL, argento SI,
euro 6E. Colonne: `ora_new_york` (ora di New York, senza fuso nel testo), OHLC, `volume`, `vol_acquisti_aggressivi`,
`vol_vendite_aggressive`, `grandi_ordini_acquisto`, `grandi_ordini_vendita`, `delta`. Fonte e licenza: **da chiarire
con i soci**; nessun file passa in git o ad altri.

Controlli dell'11/11 (script di controllo nella sessione, numeri sotto):
- **Copertura: un anno solo**, 2025-11-13/14 → 2026-11-09 (GC, ES, NQ) o 2026-11-11 (gli altri); 338-349 mila barre
  per file, 309-311 date. Nessun NaN, nessun duplicato (anche ai cambi d'ora), OHLC coerenti; `volume` = acquisti +
  vendite aggressive e `delta` = acquisti - vendite nel 100% delle barre.
- **6E: prezzi inutilizzabili**, arrotondati a 2 decimali (11 valori di chiusura distinti, 99,2% di rendimenti a 1
  minuto nulli). Volume e flusso non sono toccati dall'arrotondamento.
- **Serie continue NON aggiustate**: il rapporto con il CFD fa uno scalino a ogni cambio di contratto. ES e NQ: +0,74%
  ... +0,99% il 14/12/2025, 15/03/2026, 12/06/2026 (contro 0,01% di scarto mediano giornaliero); GC: +0,70% ... +1,42% il
  23/11, 23/01, 27/03, 27/05, 24/07. Settembre (indici) e CL, SI, YM, RTY: **non verificati** (manca un CFD
  intraday sovrapposto). Il rendimento a cavallo del cambio va tolto **nel loader**, una volta sola.
- Precisione: SI e CL a 0,01, ES a 0,25, NQ a 0,2 (il passo ufficiale e' 0,25), GC e RTY a 0,1, YM a 1.
- Significato di `grandi_ordini_*` (soglia, unita'): **da chiarire con i soci**.

## Cache

`motore/data/cache/` contiene i dati storici scaricati per evitare di rifare fetch ad ogni backtest.
Convenzione di naming:

```
motore/data/cache/<source>/<symbol>_<timeframe>_<start>_<end>.parquet
```

Esempio: `motore/data/cache/yfinance/AAPL_1d_2020-01-01_2026-04-29.parquet`.

La cache è ignorata da git (vedi `.gitignore`).

## Stage 1+

Stage 1: fetcher SP500 list + dati storici via yfinance (per il porting del notebook V6.0).
Stage 5: bridge con worldmonitor (lettura dei signal correnti per filtrare strategie).
