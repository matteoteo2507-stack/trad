---
titolo: Data Sources — Endpoint macro/market, fonti primarie e provider API
fonti:
  - _sorgenti/Data sources.txt
  - _sorgenti/Appunti estratti da pdf key concept.txt (provider API citati)
tipo: reference
---

# Data Sources — Endpoint macro/market, fonti primarie e provider API

> Reference delle fonti dati che alimentano lo screening e lo scoring macro/fondamentale. Organizzato per **categoria** (occupazione, inflazione, attività economica, supply chain, flussi di lavoro, prezzi) con le **fonti primarie ufficiali** (BLS, Fed/regional Fed, Census, NAR, ISM, Conference Board, FRED, EIA, BEA, ADP, UMich), gli **aggregatori non ufficiali** (QuiverQuantitative, Quantaste) e i **provider API** usati lato codice (FMP, FINVIZ Elite, Alpaca). Gli URL nel sorgente sono in molti casi troncati: qui sono ricondotti alla fonte/serie corretta in modo fedele.

## Fonti primarie per categoria

### Occupazione / mercato del lavoro

| Indicatore | Fonte | Riferimento | Frequenza |
|-----------|-------|-------------|-----------|
| Non-farm Payrolls, Employment Situation | BLS (Bureau of Labor Statistics) | bls.gov/news.release (emps…) | Mensile |
| Initial Jobless Claims (ICSA) | FRED / BLS | fred.stlouisfed.org/series/ICSA | Settimanale |
| JOLTS (Job Openings & Labor Turnover) | BLS | bls.gov/news.release/jolts ; bls.gov/jlt | Mensile |
| Employment Cost Index (ECI) | BLS | bls.gov/news.release/eci | Trimestrale |
| Private payrolls (stima privata) | ADP | adpemploymentreport.com | Mensile |

### Inflazione / prezzi

| Indicatore | Fonte | Riferimento | Frequenza |
|-----------|-------|-------------|-----------|
| CPI / Core CPI | BLS | bls.gov/news.release (CPI PDF) | Mensile |
| PPI (Producer Price Index) | BLS | bls.gov/news.release (PPI PDF) | Mensile |
| PCE / Personal Income & Outlays (Core PCE, preferito dalla Fed) | BEA (Bureau of Economic Analysis) | bea.gov/news/2026/personal-income… | Mensile |
| Sticky/Underlying inflation (es. Sticky-Price CPI) | Atlanta Fed | atlantafed.org/research | Mensile |
| Inflation expectations (Survey of Consumer Expectations) | NY Fed | newyorkfed.org/microeconomics | Mensile |

### Attività economica

| Indicatore | Fonte | Riferimento | Frequenza |
|-----------|-------|-------------|-----------|
| GDP (Advance / Third estimate) | BEA | bea.gov/news/2026/gdp-adv… ; gdp-thi… | Trimestrale |
| ISM Manufacturing / Non-Manufacturing PMI | ISM (Institute for Supply Management) | ismworld.org/supply-management | Mensile |
| GDPNow (nowcast PIL) | Atlanta Fed | atlantafed.org/research | Continuo (intra-trimestre) |
| Consumer Confidence Index | Conference Board | conference-board.org | Mensile |
| Consumer Sentiment | University of Michigan (Survey of Consumers) | sca.isr.umich.edu | Mensile |
| Retail Sales (Advance Monthly) | Census Bureau | census.gov/retail/marts | Mensile |
| Existing/Home sales, housing | NAR (National Association of Realtors) | nar.realtor | Mensile |

### Supply chain / flussi di lavoro / consumi

| Indicatore | Fonte | Riferimento | Frequenza |
|-----------|-------|-------------|-----------|
| Global Supply Chain Pressure Index (GSCPI) | NY Fed | newyorkfed.org/research | Mensile |
| Household debt & credit, microdata sui consumatori | NY Fed (Center for Microeconomic Data) | newyorkfed.org/microeconomics | Trimestrale / vario |
| Food / agricultural prices | USDA-ERS ; Farm Bureau (AFBF) | ers.usda.gov/data-products ; fb.org | Vario |

### Prezzi energia / commodity

| Indicatore | Fonte | Riferimento | Frequenza |
|-----------|-------|-------------|-----------|
| Gas prices (benzina USA) | AAA | gasprices.aaa.com | Giornaliero |
| Oil / WTI price charts | OilPrice.com ; EIA | oilprice.com ; eia.gov/international/analysis | Giornaliero / vario |
| Monetary policy / balance sheet (H.4.1) | Federal Reserve | federalreserve.gov/monetarypolicy | Settimanale / per riunione |

## Aggregatori non ufficiali

| Fonte | Uso |
|-------|-----|
| **QuiverQuantitative** | Dati alternativi/aggregati (es. trading dei congressisti, sentiment, flussi) — non ufficiale |
| **Quantaste** | Aggregatore dati quant — non ufficiale |

> Caveat: gli aggregatori non ufficiali vanno triangolati con la fonte primaria prima dell'uso decisionale.

## Provider API (lato codice / screening)

Citati negli Appunti come dipendenze delle skill di screening (vedi [[06_stock_selection]]):

| Provider | Ruolo | Note |
|----------|-------|------|
| **FMP** (Financial Modeling Prep) | OHLCV, fondamentali, calendari (earnings/economic), 13F | *Required* per FTD Detector, Distribution Day Monitor, VCP/CANSLIM screener, screener dividend, ecc. Free tier sufficiente per ~35 titoli |
| **FINVIZ Elite** | Screening azionario, dati istituzionali | *Optional* — riduce i tempi di esecuzione del 70–80%; auto-rilevato via `$FINVIZ_API_KEY`; screener pubblico gratuito disponibile |
| **Alpaca** | Holdings live, barre intraday, order templates | *Required* per Portfolio Manager (via Alpaca MCP) e per le fasi intraday (paper feed OK) |
| **yfinance** | OHLCV / ratio cross-asset gratuiti | Fallback gratuito per Macro Regime Detector e Theme Detector |
| **Glassnode** | On-chain crypto metrics | Per le varianti crypto degli analyzer (sostituisce i settori tradizionali con BTC/ETH/DeFi/L2/AI) |

## Note operative

- La Fed basa le decisioni soprattutto sui **rilasci ufficiali**: prioritizzare le fonti primarie sopra le versioni alternative.
- Indicatori *leading* (Initial Jobless Claims, PPI, Chicago/ISM PMI) anticipano CPI e condizioni economiche — utili per il posizionamento proattivo.
- Abilitare alert sui rilasci (es. Yahoo Finance, Investing.com) per il monitoraggio in tempo reale.

## Collegamenti

- **Implementazione nel repo**: `../../strategies/stock_selector/data_sources.py` — modulo che codifica le fonti/provider qui descritti per lo Stock Selector.
- [[06_stock_selection]] — metodologie di screening che consumano questi dati (CANSLIM, VCP, FTD/Distribution Days, edge pipeline) e relative dipendenze API.
- [[03_regimi_macro]] — interpretazione macro degli indicatori (occupazione, inflazione, attività) e quadranti Fed.
- Contesto progetto: `../../DECISIONS.md`, `../../PROJECT.md`.

## Fonti

- `_sorgenti/Data sources.txt` — elenco endpoint macro/market (BLS, Fed/regional Fed, Census, NAR, ISM, Conference Board, FRED, BEA, EIA, ADP, UMich, USDA, AAA, OilPrice; aggregatori QuiverQuantitative e Quantaste).
- `_sorgenti/Appunti estratti da pdf key concept.txt` — provider API citati come dipendenze delle skill (FMP, FINVIZ Elite, Alpaca, yfinance, Glassnode).
