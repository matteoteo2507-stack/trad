---
titolo: Riferimenti fondativi — da dove vengono le idee che usiamo
tipo: reference
aggiornato: 2026-10-02
nota: "Buco Quant Guild 44. Elenco, non riassunti: le idee applicate stanno nei moduli 0X e in core/."
---

# Riferimenti fondativi

Nessun documento del repo diceva **da dove vengono** le idee che usiamo. `agents/quant_reviewer.md` cita la
letteratura della **validazione** e del **dimensionamento**; mancava quella dei **fondamenti**. Le due liste
sono complementari. Ogni voce dice **dove la usiamo** nel repo.

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

## Dimensionamento

| Opera | Nel repo |
|---|---|
| Kelly, *A New Interpretation of Information Rate* (Bell System Technical Journal, 1956) | `kelly_*` (buco 16), `05` |
| Thorp, scritti sul criterio di Kelly applicato a giochi e mercati | Kelly frazionario, `05` |
