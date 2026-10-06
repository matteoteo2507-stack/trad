> ⚠️ **Controllo NEGATIVO** su dati sintetici (`tools/make_demo_data.py --mode null`, random walk, nessun vantaggio). Generato il 07/10/2026 col codice corretto. Esito atteso e ottenuto: nessuna PROMOSSA. I numeri non hanno valore di trading.
> Nota: in fase 3 `ev_vs_zero` e' positivo anche qui, perche' lavora sui trade in-sample dei candidati scelti come migliori, e fuori campione sui due candidati usciti positivi per caso. Toglie il valore d'opzione, non il caso: decide il verdetto della fase 4.

# Report mean_reversion_XAUUSD_H1_20261006_220901

Simbolo **XAUUSD** H1 · dati 2022-01-03 00:00:00 → 2025-01-01 23:00:00 · IS fino a 2024-02-08 02:00:00

## Fase 1 · Famiglia (qualitativo, senza costi)

| strategy         |   varianti |   pct_positive |   best_exp |   median_exp |   passano |
|:-----------------|-----------:|---------------:|-----------:|-------------:|----------:|
| rsi_extreme      |         36 |          0.806 |      0.739 |        0.024 |         4 |
| consecutive_bars |         16 |          0.75  |      0.064 |        0.008 |         1 |
| keltner_reversal |         24 |          0.5   |      0.125 |        0.002 |         2 |
| pdh_pdl_sweep    |         32 |          0.406 |      0.108 |       -0.008 |         4 |
| zscore_revert    |         36 |          0.389 |      0.054 |       -0.018 |         0 |
| bb_fade          |         36 |          0.444 |      0.258 |       -0.024 |         3 |
| asia_range_fade  |         24 |          0.083 |      0.023 |       -0.028 |         0 |

## Fase 2 · Con costi reali

| strategy         | params                                               |   n |   exp_gross |   expectancy |   cost_share |    pf |   max_dd_r | pass   |
|:-----------------|:-----------------------------------------------------|----:|------------:|-------------:|-------------:|------:|-----------:|:-------|
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1}       | 133 |       0.176 |        0.086 |        0.508 | 1.195 |     11     | True   |
| bb_fade          | {"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1}       | 166 |       0.215 |        0.102 |        0.524 | 1.17  |     19.237 | True   |
| rsi_extreme      | {"atr_sl": 1.5, "lo": 20, "n": 5, "trend": 1}        | 232 |       0.085 |        0.013 |        0.844 | 1.029 |     11.814 | False  |
| keltner_reversal | {"buf": 0.2, "mult": 2.5, "n": 50, "trend": 0}       | 542 |       0.09  |        0.007 |        0.918 | 1.013 |     36.403 | False  |
| consecutive_bars | {"atr_sl": 1.5, "n_bars": 5, "trend": 1}             | 156 |       0.064 |        0.002 |        0.963 | 1.011 |      6.919 | False  |
| pdh_pdl_sweep    | {"buf": 0.1, "end_h": 18, "start_h": 8, "tp": "mid"} | 485 |       0.108 |       -0.011 |        1.1   | 0.984 |     34.439 | False  |
| bb_fade          | {"atr_sl": 2.5, "k": 2.5, "n": 20, "trend": 1}       |  92 |       0.059 |       -0.02  |        1.335 | 0.958 |     12.093 | False  |
| pdh_pdl_sweep    | {"buf": 0.1, "end_h": 18, "start_h": 10, "tp": 3.0}  | 393 |       0.071 |       -0.022 |        1.315 | 0.968 |     51.941 | False  |
| pdh_pdl_sweep    | {"buf": 0.1, "end_h": 18, "start_h": 8, "tp": 3.0}   | 452 |       0.068 |       -0.027 |        1.397 | 0.962 |     71.767 | False  |
| pdh_pdl_sweep    | {"buf": 0.1, "end_h": 22, "start_h": 8, "tp": "mid"} | 545 |       0.088 |       -0.03  |        1.339 | 0.956 |     41.459 | False  |
| rsi_extreme      | {"atr_sl": 1.5, "lo": 20, "n": 3, "trend": 1}        | 697 |       0.052 |       -0.016 |        1.314 | 0.957 |     19.061 | False  |
| keltner_reversal | {"buf": 0.2, "mult": 2.0, "n": 20, "trend": 1}       | 140 |       0.125 |       -0.057 |        1.453 | 0.898 |     16.312 | False  |
| rsi_extreme      | {"atr_sl": 1.5, "lo": 10, "n": 3, "trend": 1}        | 238 |       0.05  |       -0.033 |        1.657 | 0.921 |     22.784 | False  |
| rsi_extreme      | {"atr_sl": 1.5, "lo": 10, "n": 2, "trend": 1}        | 724 |       0.051 |       -0.021 |        1.403 | 0.934 |     29.134 | False  |

## Fase 3 · Pass rate per modello di rischio (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.056 |  0.219 |  0.197 |  0.151 |  0.101 |
| dd_lineare               |  0.01  |  0.133 |  0.219 |  0.235 |  0.191 |
| dd_lineare+guardia+coast |  0.007 |  0.128 |  0.263 |  0.337 |  0.397 |
| dd_scaglioni             |  0.009 |  0.127 |  0.184 |  0.226 |  0.177 |
| guardia_giornaliera      |  0.012 |  0.179 |  0.327 |  0.391 |  0.399 |
| statico                  |  0.011 |  0.159 |  0.241 |  0.251 |  0.203 |
| streak_perdite           |  0.009 |  0.123 |  0.219 |  0.24  |  0.209 |

## Fase 3 · Fallimento per DAILY loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |      0 |  0.045 |  0.338 |  0.573 |  0.792 |
| dd_lineare               |      0 |  0.049 |  0.1   |  0.252 |  0.569 |
| dd_lineare+guardia+coast |      0 |  0     |  0     |  0     |  0.009 |
| dd_scaglioni             |      0 |  0.036 |  0.168 |  0.209 |  0.519 |
| guardia_giornaliera      |      0 |  0     |  0     |  0     |  0.027 |
| statico                  |      0 |  0.117 |  0.271 |  0.398 |  0.607 |
| streak_perdite           |      0 |  0.02  |  0.18  |  0.352 |  0.582 |

## Fase 3 · Fallimento per MAX loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.009 |  0.159 |  0.18  |  0.176 |  0.104 |
| dd_lineare               |  0     |  0.017 |  0.093 |  0.167 |  0.151 |
| dd_lineare+guardia+coast |  0     |  0.006 |  0.038 |  0.083 |  0.188 |
| dd_scaglioni             |  0.005 |  0.071 |  0.121 |  0.178 |  0.124 |
| guardia_giornaliera      |  0.007 |  0.083 |  0.166 |  0.233 |  0.278 |
| statico                  |  0.028 |  0.162 |  0.234 |  0.258 |  0.182 |
| streak_perdite           |  0.005 |  0.127 |  0.223 |  0.263 |  0.193 |

## Fase 3 · EV per tentativo (media, valuta conto)

| risk_family              |     0.5% |    1.0% |     1.5% |     2.0% |     3.0% |
|:-------------------------|---------:|--------:|---------:|---------:|---------:|
| anti_martingala          | -328.827 | 596.905 |  527.325 |  196.841 | -357.655 |
| dd_lineare               | -507.428 |  -1.918 |  650.823 |  707.077 |  412.135 |
| dd_lineare+guardia+coast | -521.333 |  28.93  |  961.402 | 1950.59  | 3174.7   |
| dd_scaglioni             | -508.509 |   0.398 |  415.455 |  693.701 |  248.573 |
| guardia_giornaliera      | -493.098 | 418.765 | 1853.2   | 2926.09  | 3621.91  |
| statico                  | -499.573 | 213.546 |  950.261 | 1008.04  |  693.939 |
| streak_perdite           | -516.09  | -26.495 |  657.276 |  810.686 |  715.165 |

## Fase 3 · EV dovuto al VANTAGGIO (EV meno lo stesso EV a vantaggio zero)

| risk_family              |    0.5% |    1.0% |     1.5% |     2.0% |     3.0% |
|:-------------------------|--------:|--------:|---------:|---------:|---------:|
| anti_martingala          | 144.806 | 748.294 |  628.28  |  395.182 |  104.729 |
| dd_lineare               |  28.555 | 355.31  |  768.03  |  725.05  |  459.956 |
| dd_lineare+guardia+coast |  18.149 | 361.429 |  867.651 | 1402.78  | 2263.75  |
| dd_scaglioni             |  23.821 | 342.727 |  578.344 |  665.886 |  409.03  |
| guardia_giornaliera      |  37.541 | 592.825 | 1314.87  | 1787.63  | 2240.23  |
| statico                  |  32.463 | 466.321 |  891.569 |  799.127 |  609.157 |
| streak_perdite           |  20.225 | 306.236 |  738.504 |  706.541 |  655.544 |

## Fase 3 · Migliori combinazioni prop (ordinate per ev_vs_zero)

| candidate                                              | rules             | risk_profile                  |   pass_rate |   pass_zero |   fail_daily |   fail_max |   median_days |   ev_attempt |   ev_zero |   ev_vs_zero |
|:-------------------------------------------------------|:------------------|:------------------------------|------------:|------------:|-------------:|-----------:|--------------:|-------------:|----------:|-------------:|
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | guardia_giornaliera|3.0%      |       0.467 |       0.317 |        0     |      0.413 |          39   |      6253.55 |  3170.29  |      3083.26 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | dd_lineare+guardia+coast|3.0% |       0.42  |       0.27  |        0     |      0.223 |          46.5 |      5059.3  |  2007     |      3052.3  |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | dd_lineare+guardia+coast|3.0% |       0.437 |       0.287 |        0     |      0.34  |          39   |      4437.77 |  1537.88  |      2899.89 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | guardia_giornaliera|3.0%      |       0.433 |       0.307 |        0     |      0.077 |          71.5 |      4558.84 |  1863.18  |      2695.66 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | guardia_giornaliera|3.0%      |       0.453 |       0.287 |        0     |      0.11  |          62   |      4331.81 |  1819.5   |      2512.31 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | guardia_giornaliera|2.0%      |       0.4   |       0.277 |        0     |      0.357 |          66   |      4108.66 |  1681.36  |      2427.3  |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | dd_lineare+guardia+coast|3.0% |       0.42  |       0.243 |        0     |      0.03  |          82.5 |      3551.87 |  1244.8   |      2307.07 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | guardia_giornaliera|2.0%      |       0.437 |       0.23  |        0     |      0.047 |          98   |      3130.56 |   908.156 |      2222.41 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | guardia_giornaliera|3.0%      |       0.407 |       0.317 |        0     |      0.473 |          28   |      4231.05 |  2055.61  |      2175.44 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | guardia_giornaliera|2.0%      |       0.477 |       0.333 |        0     |      0.37  |          60   |      4653.52 |  2511.18  |      2142.34 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | dd_lineare+guardia+coast|2.0% |       0.403 |       0.273 |        0     |      0.123 |          61   |      3339.18 |  1313.8   |      2025.38 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | one_step_trailing | dd_lineare+guardia+coast|3.0% |       0.357 |       0.117 |        0.047 |      0.4   |          35   |      1365.73 |  -600     |      1965.73 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | guardia_giornaliera|1.5%      |       0.39  |       0.27  |        0     |      0.323 |          75   |      2858.99 |   971.236 |      1887.75 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | two_step_classic  | guardia_giornaliera|1.5%      |       0.357 |       0.23  |        0     |      0.173 |          87   |      2804.7  |   990.052 |      1814.65 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | two_step_tight    | dd_lineare+guardia+coast|3.0% |       0.417 |       0.247 |        0     |      0.057 |          71   |      3043.28 |  1229.38  |      1813.9  |

> Come si legge: decide il **verdetto** della conferma (intervallo OOS corretto per i candidati; il DSR e' diagnostica).
> `ev_vs_zero` toglie il valore d'opzione della challenge ma **non il caso**: su un candidato
> NON_DIMOSTRATA non dice niente. Per un candidato vero: `lab.prop.evaluate_ci`.

## Fase 4 · Conferma OOS

| candidate                                              |   n_is |   exp_is |   n_oos |   exp_oos |   exp_oos_lo |   exp_oos_hi |   mde_oos |   pf_oos |   dd_oos_r |   dsr_is |   trials |   n_candidati | verdetto       |
|:-------------------------------------------------------|-------:|---------:|--------:|----------:|-------------:|-------------:|----------:|---------:|-----------:|---------:|---------:|--------------:|:---------------|
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} |    133 |    0.086 |      58 |     0.241 |       -0.057 |        0.538 |     0.398 |    1.656 |      4.271 |    0.089 |      204 |             2 | NON_DIMOSTRATA |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} |    166 |    0.102 |      70 |     0.211 |       -0.163 |        0.586 |     0.504 |    1.391 |      8.036 |    0.075 |      204 |             2 | NON_DIMOSTRATA |

## Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)

| candidate                                              | verdetto       | rules             | risk_profile                  |   pass_rate_is |   pass_rate |   pass_zero |   fail_daily |   fail_max |    ev_is |   ev_attempt |   ev_vs_zero_is |   ev_vs_zero |
|:-------------------------------------------------------|:---------------|:------------------|:------------------------------|---------------:|------------:|------------:|-------------:|-----------:|---------:|-------------:|----------------:|-------------:|
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.467 |       0.763 |       0.373 |            0 |      0.093 | 6253.55  |     14412.2  |         3083.26 |     12436.1  |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | dd_lineare+guardia+coast|3.0% |          0.42  |       0.65  |       0.32  |            0 |      0.04  | 5059.3   |     10816.2  |         3052.3  |      9333.22 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | dd_lineare+guardia+coast|3.0% |          0.437 |       0.633 |       0.283 |            0 |      0.067 | 4437.77  |      9187.95 |         2899.89 |      8582.2  |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.433 |       0.737 |       0.197 |            0 |      0.01  | 4558.84  |     11074.2  |         2695.66 |     10809.6  |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|3.0%      |          0.453 |       0.687 |       0.22  |            0 |      0.01  | 4331.81  |      9416.1  |         2512.31 |      9046.37 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|2.0%      |          0.4   |       0.637 |       0.27  |            0 |      0.05  | 4108.66  |      7552.32 |         2427.3  |      6507.02 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | dd_lineare+guardia+coast|3.0% |          0.42  |       0.677 |       0.14  |            0 |      0     | 3551.87  |      8550.34 |         2307.07 |      8650.74 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|2.0%      |          0.437 |       0.7   |       0.13  |            0 |      0.003 | 3130.56  |      7552.46 |         2222.41 |      7528.62 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|3.0%      |          0.407 |       0.613 |       0.337 |            0 |      0.173 | 4231.05  |      9941.76 |         2175.44 |      8867.8  |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|2.0%      |          0.477 |       0.817 |       0.403 |            0 |      0.05  | 4653.52  |     13138.9  |         2142.34 |     10663.1  |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.357 |       0.557 |       0.133 |            0 |      0.117 | 1365.73  |      5214.89 |         1965.73 |      5713.98 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_tight    | dd_lineare+guardia+coast|3.0% |          0.417 |       0.657 |       0.153 |            0 |      0.003 | 3043.28  |      8007.45 |         1813.9  |      7996.01 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.333 |       0.6   |       0.097 |            0 |      0     | 1590.25  |      4936.34 |         1543.63 |      5481.72 |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | one_step_trailing | guardia_giornaliera|3.0%      |          0.3   |       0.463 |       0.11  |            0 |      0.24  |  938.095 |      4943.58 |         1538.1  |      5442.68 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 1} | NON_DIMOSTRATA | two_step_classic  | statico|3.0%                  |          0.29  |       0.713 |       0.193 |            0 |      0.237 | 2151.26  |     10669.6  |         1489.34 |     10420    |
