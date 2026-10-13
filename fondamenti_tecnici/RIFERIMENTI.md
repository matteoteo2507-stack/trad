---
titolo: Riferimenti fondativi — da dove vengono le idee che usiamo
tipo: reference
aggiornato: 2026-10-13
nota: "Buco Quant Guild 44. Elenco, non riassunti: le idee applicate stanno nei moduli 0X e in core/."
---

# Riferimenti fondativi

Nessun documento del repo diceva **da dove vengono** le idee che usiamo. Il primo revisore
(`agents/quant_reviewer.md`, ritirato il 2026-10-13) citava la letteratura della **validazione** e del
**dimensionamento**; mancava quella dei **fondamenti**. Dal 13/10 le due liste stanno qui, in un file solo.
Ogni voce dice **dove la usiamo** nel repo.

## Fondamenti (Quant Guild, G5)

| Opera | Idea | Nel repo |
|---|---|---|
| Bachelier, *Théorie de la spéculation* (1900) | i prezzi come passeggiata casuale | base del baseline casuale: il prezzo senza informazione |
| Sharpe, *Capital Asset Prices* (Journal of Finance, 1964) | CAPM: rendimento atteso e beta | `05`, `benchmark_metrics` |
| Sharpe, *Mutual Fund Performance* (Journal of Business, 1966) | il rapporto rendimento/volatilita' | `sharpe_ratio` |
| Black & Scholes, *The Pricing of Options and Corporate Liabilities* (Journal of Political Economy, 1973) | prezzo delle opzioni, log-normalita' | **fuori perimetro operativo** (niente opzioni); la log-normalita' sottostima le code |
| Dupire, *Pricing with a Smile* (Risk, 1994) | volatilita' locale | fuori perimetro |
| Carr & Madan, *Towards a Theory of Volatility Trading* (1998) | esposizione alla volatilita' | fuori perimetro; nota sul VRP in `05` |

## Validazione e metodo (gia' usati in `core/`)

| Opera | Nel repo |
|---|---|
| Efron, *Better Bootstrap Confidence Intervals* (JASA, 1987) | `bca_bootstrap_ci` |
| Politis & Romano, *The Stationary Bootstrap* (JASA, 1994) | `_stationary_bootstrap_indices`, `whites_reality_check` |
| White, *A Reality Check for Data Snooping* (Econometrica, 2000) | `whites_reality_check` |
| Hansen, *A Test for Superior Predictive Ability* (Journal of Business & Economic Statistics, 2005) | SPA: catalogato, via `arch` ([ricerca GitHub](../docs/reviews/ricerca_github_2026-09-29.md)) |
| Bailey & López de Prado, *The Deflated Sharpe Ratio* (Journal of Portfolio Management, 2014) | `deflated_sharpe_ratio` |
| Bailey, Borwein, López de Prado, Zhu, *The Probability of Backtest Overfitting* (Journal of Computational Finance, 2017) | `pbo_cscv` |
| Harvey, Liu, Zhu, *…and the Cross-Section of Expected Returns* (Review of Financial Studies, 2016) | soglie piu' alte con molti test: contatore trial |
| Phipson & Smyth, *Permutation P-values Should Never Be Zero* (Statistical Applications in Genetics and Molecular Biology, 2010) | `pvalue_mc` (buco 37) |
| Kupiec, *Techniques for Verifying the Accuracy of Risk Measurement Models* (Journal of Derivatives, 1995) | `test_eccedenze` (buco 22) |
| Wald, *Sequential Tests of Statistical Hypotheses* (Annals of Mathematical Statistics, 1945) | `SPRTBernoulli` (buco 5) |
| Page, *Continuous Inspection Schemes* (Biometrika, 1954) | `CUSUMInferiore` (buchi 5, 28) |
| López de Prado, *Advances in Financial Machine Learning* (Wiley, 2018), cap. 7 (CPCV), 11 (PBO), 14 (statistiche di backtest) | `cpcv_splits`, `pbo_cscv`, Step 6 del protocollo (pre-mortem) |
| López de Prado, *Machine Learning for Asset Managers* (Cambridge University Press, 2020) | riferimento generale del primo revisore; nessun uso puntuale nel codice |
| McLean & Pontiff, *Does Academic Research Destroy Stock Return Predictability?* (Journal of Finance, 2016) | decadimento dopo la pubblicazione: `QUANT_REVIEW_PROTOCOL.md`, "Casi speciali" |

## Dimensionamento

| Opera | Nel repo |
|---|---|
| Kelly, *A New Interpretation of Information Rate* (Bell System Technical Journal, 1956) | `kelly_*` (buco 16), `05` |
| Thorp, scritti sul criterio di Kelly applicato a giochi e mercati | Kelly frazionario, `05` |
| MacLean, Thorp, Ziemba, *The Kelly Capital Growth Investment Criterion* (World Scientific, 2011) | crescita ottima contro Sharpe ottimo, rovina con leva eccessiva: `05` |
| Fernholz, *Stochastic Portfolio Theory* (Springer, 2002) | perdita di crescita da varianza (volatility drag): `05` |
| Harvey, Hoyle, Korgaonkar e altri, *The Impact of Volatility Targeting* (Journal of Portfolio Management, 2018) | dimensionamento a volatilita' obiettivo: `strategies/tsmom/` |
| Carver, *Systematic Trading* (Harriman House, 2015) | combinare sistemi poco correlati: `05` |

## Famiglie di strategie (dal primo revisore, 2026-10-13)

| Opera | Nel repo |
|---|---|
| Moskowitz, Ooi, Pedersen, *Time Series Momentum* (Journal of Financial Economics, 2012) | famiglia `tsmom`: `strategies/tsmom/`, `docs/TSMOM_PREREGISTRATION.md` |
| Hurst, Ooi, Pedersen, *A Century of Evidence on Trend-Following Investing* (Journal of Portfolio Management, 2017) | il trend come flusso ortogonale al beta azionario: `05`, `08` |
| Osler, *Currency Orders and Exchange-Rate Dynamics* (American Economic Review, 2003) | termine di confronto nella review di London Breakout |
