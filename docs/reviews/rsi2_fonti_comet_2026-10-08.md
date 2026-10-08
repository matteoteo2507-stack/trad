---
titolo: "RSI(2) di Connors sugli indici: fonti pubblicate raccolte da Comet"
tipo: fonte
creato: 2026-10-08
fonte: "Comet (browser AI di Matteo), 08/10/2026, prompt nella sessione del 08/10 (candidato A)"
stato: quarantena
---

# RSI(2) di Connors: fonti pubblicate (Comet, 08/10)

> **Cos'e'.** Il report di Comet portato da Matteo il 08/10 per il candidato A
> ([MR_INDICI_POTENZA](../MR_INDICI_POTENZA.md) §5), riportato sotto **senza modifiche di contenuto**.
>
> **Come leggerlo (08/10).** Sono **statistiche dichiarate da terzi** (regola del 04/08): non entrano come evidenza di
> vantaggio, servono solo come **effetto atteso per il calcolo di potenza** (09_fonti_di_vantaggio §4.7: effetto
> pubblicato e sua meta'). I numeri del libro di Connors-Alvarez sono **di seconda mano** (Comet non ha il libro). Le
> repliche sono blog di educazione quantitativa, alcune con contenuti a pagamento; nessuna con codice verificato da noi.
> Si contano per fonte, non per occorrenza. **Tutte testano la regola senza stop-loss** (o con time stop di 10 giorni).

---

**1) Numeri "originali" (Connors & Alvarez, 2008)** — *Short Term Trading Strategies That Work*, 2008. Secondo fonti
secondarie: test 1995-2007 su SPY e componenti S&P 500, varianti "RSI(2) < 5 o < 10 sopra SMA 200, uscita su RSI(2) >
65-70 o chiusura > SMA 5"; win rate 75-90%; guadagno medio ~0,8-1,0% per trade lordo, tenuta di pochi giorni; costi
realistici non esplicitati; nessuno stop-loss nei test originali. Comet non ha accesso al libro. Sintesi da
QuantifiedStrategies e Alpha Strategic Growth.

**2) Repliche con dati dopo il 2008**

| fonte | URL | campione | regola | numeri | costi |
|---|---|---|---|---|---|
| QuantifiedStrategies, "Complete Guide To Larry Connors' 2-Period RSI Trading Rules", 2026 | https://www.quantifiedstrategies.com/rsi-2-strategy/ | SPY 1993-2026 | RSI(2) < 10, uscita RSI(2) > 80; varianti con SMA 200 e uscita SMA 5 | senza filtro: 0,9% a trade, CAGR 9%, maxDD 34%, 28% in mercato; con SMA 200: 0,95% a trade, CAGR 6,8%, maxDD 31%, 18% in mercato; win 76% in una variante; trade non esplicitati | non chiaro quali curve siano nette; "leggero decadimento" 2015-2025 |
| Ayrat Murtazin (GuruFinanceInsights), "I Backtested the Classic RSI(2)...", 2026 | https://gurufinanceinsights.substack.com/p/i-backtested-the-classic-rsi2-mean | SPY 10/2000-09/2026 | sopra SMA 200, RSI(2) < 10, uscita RSI(2) > 70 o 10 giorni | **181 trade**, win 82%, tenuta media 3,7 giorni, 10,2% in mercato, maxDD −13,8% (B&H −55,2%), $1 → $2,49 (B&H $8,68) | "considered", livello non specificato |
| Quant4Free, "Does Connors' RSI(2) mean-reversion actually work?", 2026 | https://quant4free.com/analysis/rsi2-mean-reversion/ | **S&P 1500 (singole azioni)** 2015-2026 | sopra SMA 200, RSI(2) < 5, uscita chiusura > SMA 5 | 8.261 trade, win 63,1%, **PF 0,99**, CAGR −0,7%, maxDD −57,3% | **10 bps per lato** |
| Quantitativo, "Squeezing more profits with cumulative RSI", 2024 | https://www.quantitativo.com/p/squeezing-more-profits-with-cumulative | S&P 500, 1999-2024 | RSI(2) vanilla (e cumulativa) | vanilla: **0,6% a trade**, win 74%, payoff ~0,50 (+2,5% / −4,9%); batte l'S&P quasi ogni anno 2000-2013, **sotto dal 2014** in diversi anni | non esplicitati |
| BacktestEverything, "RSI Mean Reversion Strategy: A Complete Backtest Guide", 2025 | https://www.backtesteverything.com/blog/rsi-mean-reversion-strategy-complete-backtest | SPY 2000-2024 | RSI(2) < 10, sopra SMA 200, uscita RSI(2) > 70 o 10 giorni | **387 trade**, win 73%, vincita media +1,8%, perdita media −2,1%, PF 1,65, 9,4% annuo, 22% in mercato; walk-forward: efficienza OOS 0,78 | non chiari |
| Backtest.Substack, "The 2-Period RSI: A Simple System That Still Earns Its Keep", 2026 | https://backtest.substack.com/p/the-2-period-rsi-a-simple-system | componenti Nasdaq 100, ~20 anni, 4 slot | RSI(2) basso sopra SMA 200 | win 64,3%, +2,33% / −3,02%, PF 1,45, 17,84% annuo, maxDD 29,15% | non esplicitati |
| Reddit r/algotrading, "Backtest Results for Connors RSI2 Strategy", 2024 | https://www.reddit.com/r/algotrading/comments/1fm5lfj/backtest_results_for_connors_rsi2_strategy/ | non specificato | — | solo qualitativo: win alto, rendimento basso per il poco tempo in mercato, drawdown migliore del B&H | non chiaro |

**3) Indici fuori dagli USA.** Backtrex, "RSI (2) Strategy Backtest on the DAX (10 Years)",
https://backtrex.com/en/backtests/connors-rsi-2-dax : numeri non estratti. Nessun numero verificabile su FTSE o Nikkei.

**4) Sintesi di Comet.** Win rate 75-90% nei test originali, 63-82% nelle repliche. Su SPY/S&P 500 con costi bassi e
filtro di trend, CAGR ancora positivo (6-9%); su universi ampi con costi realistici, PF ~1 e CAGR leggermente negativo.
Decadimento dopo il 2013-2015 segnalato da piu' autori. In molti test recenti non batte il buy-and-hold in rendimento,
ma con drawdown e tempo in mercato minori.

**5) Fonti che vendono.** TopTradingStrategy vende materiale educativo; QuantifiedStrategies, BacktestEverything, Alpha
Strategic Growth, Quant4Free e Quantitativo hanno contenuti premium o membership; nessuna evidenza di segnali in tempo
reale legati a RSI(2). Backtrex e' una piattaforma di backtesting.
