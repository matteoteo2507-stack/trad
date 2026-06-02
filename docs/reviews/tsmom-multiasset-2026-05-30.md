# TSMOM — Valutazione multi-asset e cosa farne — 2026-05-30

> **DECISIONE (2026-05-30): TSMOM single-asset ARCHIVIATA** (come London, dati conservati). Sviluppo nuove strategie in pausa: focus su consolidamento dell'avviabile (signal copier demo, Confluence). Il progetto portafoglio (§4 opzione 2) resta come possibile ripresa futura, non attivo ora.

> Estende la review single-asset [docs/reviews/tsmom_jpy-2026-05-29.md](tsmom_jpy-2026-05-29.md) con i dati multi-pair raccolti dall'utente.
> Codice [mql5/tsmom_jpy.mq5](../../mql5/tsmom_jpy.mq5) · [strategies/tsmom/](../../strategies/tsmom/) · dati [backtest_results/TSMOM/](../../backtest_results/TSMOM/).

## 1. Dati disponibili (e cosa permettono / non permettono)

| Tipo | Contenuto | Uso valido |
|---|---|---|
| `ReportTester-106852151.xlsx` (USDJPY), `ReportTester-gbpusd.xlsx` | **Trade list** completa | Analisi trade-level (concentrazione, costi) |
| `ReportOptimizer-*.xml` (×3, identici) | **Sweep su 14 simboli**, parametri **default** (nessuna ottimizzazione: 1 pass/simbolo) | Solo **breadth** (stat di sintesi per simbolo) |

> ⚠️ Gli optimizer XML danno **solo metriche di sintesi per simbolo**, non serie di rendimenti giornalieri. Quindi **non** è costruibile la vera equity di portafoglio né lo Sharpe di portafoglio né le correlazioni. Tutto ciò che segue sul "portafoglio" è messo **da parte come non fondato** e affrontato con la letteratura (§4). Nota positiva: **nessun data-snooping sui parametri** (tutti default da paper).

## 2. Breadth — TSMOM default su 14 simboli, 2020–2026

| Symbol | Profit | PF | Sharpe (MT5) | DD% | Trades |
|---|---|---|---|---|---|
| USDJPY | +4498 | 3.45 | 0.88 | 10.0 | 38 |
| USDCNH | +3269 | 2.30 | 0.54 | 17.0 | 24 |
| EURUSD | +1065 | 1.42 | 0.20 | 21.1 | 35 |
| NVDA | +829 | 7.22 | **24.5** | 3.2 | 20 |
| GBPUSD | +707 | 1.35 | 0.19 | 17.1 | 32 |
| AMD | +493 | 4.50 | **22.6** | 3.7 | 22 |
| INTC | +210 | 1.25 | **10.5** | 5.0 | 49 |
| MSFT | +75 | 1.13 | **3.6** | 4.6 | 25 |
| USDSEK | +31 | 1.02 | 0.01 | 10.1 | 32 |
| AUDUSD | −615 | 0.67 | −0.28 | 17.7 | 37 |
| USDCHF | −1074 | 0.61 | −0.30 | 20.1 | 43 |
| NZDUSD | −1666 | 0.25 | −0.93 | 17.3 | 45 |
| USDCAD | −2105 | 0.40 | −0.66 | 24.2 | 52 |
| SP500m | −6919 | 0.15 | −0.09 | **87.8** | 6 |

**Letto onestamente, "9/14 profittevoli" non regge:**

1. **Tutto il profitto FX è USDJPY.** Le 9 coppie FX sommano ≈ +4110; USDJPY da solo è +4498 → **FX-basket senza USDJPY ≈ −388 (negativo)**. Mediana Sharpe FX = **0.01**.
2. **USDJPY e GBPUSD sono mono-trade.** Tolto il trade migliore: USDJPY net +4498 → **−6** (PF 1.00); GBPUSD net → **−500** (PF 0.75). L'edge per-asset è 1 trade (il trend USDJPY 2021–22 = l'annata trend 2022 che *tutti* i CTA hanno preso).
3. **Gli Sharpe azionari (24, 22, 10) non sono credibili.** Sharpe > 3 retail = quasi sempre artefatto metodologico (persona §2). Sono 20–25 trade su titoli in bull secolare (NVDA ~10× nel periodo): è **beta di un trend monodirezionale**, non il premio TSMOM, e il momentum su singolo titolo è un'altra letteratura (cross-sectional).
4. **SP500m: −88% di drawdown su 6 trade** → il sizing vol-target dell'EA **non è robusto** ai contract spec degli indici. Bug di portabilità, non edge.
5. **N < 53 su ogni simbolo** → il problema di campione piccolo è **universale**, la breadth non lo risolve a livello di singolo asset.

## 3. Valutazione dei principi

Il *concetto* TSMOM è solido in letteratura (Moskowitz-Ooi-Pedersen, JFE 2012). Ma **questa implementazione e questo universo non possono esprimerlo**, per ragioni fondate:

- **Universo sbagliato.** L'edge TSMOM è di **portafoglio diversificato a bassa correlazione** (commodities + bond + indici + FX globali). Qui ci sono 9 USD-pair (tutte correlate dalla gamba USD) + 4 tech-stock USA (correlate tra loro e a SP500) + 1 indice che è esploso. È un paniere **stretto e ad alta correlazione** — il caso peggiore per la diversificazione che genera lo Sharpe TSMOM.
- **Epoca sbagliata.** La letteratura documenta che TSMOM era profittevole **1985–2009 e "svanisce dopo il 2009"** per via delle correlazioni cross-asset salite post-GFC (Baltas-Kosowski). Il 2020–2026 è in piena era decaduta; il 2022 è stato l'unico grande anno trend (ed è l'unico trade vincente nei dati).
- **Spec parzialmente non canonica.** EMA(20/60) come conferma + SL 3×ATR + exit su flip è una variante; la robustezza MOP nasce su 12-mesi, vol-scaled, **molti** mercati.

## 4. Cosa possiamo fare — opzioni fondate

1. **Archiviare TSMOM come EA single-asset** (come London). Fondato: single-asset = mono-trade, non validabile; universo retail MT5 inadatto.
2. **Trasformarla in un progetto di ricerca di portafoglio** *serio*, con aspettative realistiche e modeste:
   - Universo **largo e a bassa correlazione**: aggiungere commodities (oro, petrolio), bond/rate futures, indici regionali — non solo USD-pair. *Ma*: l'infra retail MT5 ha già mostrato di rompersi sugli indici (SP500m −88%) → serve un motore Python ([strategies/tsmom/](../../strategies/tsmom/)) con dati daily e vol-targeting **a livello di portafoglio**, validato sulle **serie di rendimenti** (non sulle sintesi).
   - Aspettativa onesta post-2010: Sharpe di programma **~0.3–0.5**, con anni negativi (2023, 2025 YTD −9% per SG Trend Index). Non è un quick win.
3. **Lasciar perdere TSMOM** e prendere la prossima candidata dalla [[project_strategies_pipeline]].

## 5. Raccomandazione (adversariale)

Allo stato, **TSMOM non è avviabile** più di London. Il segnale dei dati + la letteratura convergono: niente edge esprimibile in questo universo/epoca/infra. La trasformazione in portafoglio diversificato (opzione 2) è l'**unico** percorso con fondamento teorico, ma è un **progetto di infrastruttura** a ritorno atteso modesto e ritardato, non la soluzione al "non ho niente di avviabile".

**Proposta:** archiviare TSMOM single-asset con queste lezioni; **non** avviare ora il progetto portafoglio se l'obiettivo è qualcosa di operabile a breve; rivalutare la pipeline strategie per una candidata con edge meno dipendente da diversificazione massiva.

## 6. Lezioni apprese (TSMOM)

1. **Trend-following single-asset è mono-trade** (top trade = 100%+ del net su USDJPY *e* GBPUSD). Non valutabile a N≈35.
2. **L'edge TSMOM vive nel portafoglio diversificato a bassa correlazione**, non nel singolo strumento (MOP 2012; Baltas-Kosowski).
3. **Decay post-2009 documentato** → su 2020–2026 aspettarsi poco; il "vincente" è l'annata-trend 2022.
4. **Diffidare dello Sharpe MT5 su < 50 trade** (NVDA 24 = artefatto small-sample / beta di bull secolare).
5. **Il vol-target dell'EA non è portabile ai contract spec degli indici** (SP500m −88% DD) → da sistemare prima di qualunque uso multi-asset.

---
### Riproducibilità
[backtest_results/TSMOM/_multi.py](../../backtest_results/TSMOM/_multi.py) (breadth dai 3 XML), [_analysis.py](../../backtest_results/TSMOM/_analysis.py) (USDJPY trade-level), [_gbp_conc.py](../../backtest_results/TSMOM/_gbp_conc.py) (GBPUSD concentrazione). Metriche: [core/quant_metrics.py](../../core/quant_metrics.py).

### Fonti (ricerca)
- Moskowitz, Ooi, Pedersen (2012) — *Time Series Momentum*, JFE 104(2). [PDF](http://docs.lhpedersen.com/TimeSeriesMomentum.pdf)
- Baltas, Kosowski (2020) — *Demystifying Time-Series Momentum Strategies*. [ResearchGate](https://www.researchgate.net/publication/350741628_Demystifying_Time-Series_Momentum_Strategies_Volatility_Estimators_Trading_Rules_and_Pairwise_Correlations) · [CME](https://www.cmegroup.com/education/files/demystifiing-time-series-momentum-strategies.pdf)
- SG Trend / TTU Trend Following Report 2025. [Top Traders Unplugged](https://www.toptradersunplugged.com/trend-following-performance-report-april-2025/)
- Quantpedia — Time Series Momentum Effect. [link](https://quantpedia.com/strategies/time-series-momentum-effect)
