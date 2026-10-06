> ⚠️ Report generato su dati SINTETICI (data/DEMO_XAUUSD_H1.csv): mostra il formato dell output, i numeri non hanno valore di trading.

# Report mean_reversion_XAUUSD_H1_20261004_184509

Simbolo **XAUUSD** H1 · dati 2022-01-03 00:00:00 → 2025-01-01 23:00:00 · IS fino a 2024-02-08 02:00:00

## Fase 1 · Famiglia (qualitativo, senza costi)

| strategy         |   varianti |   pct_positive |   best_exp |   median_exp |   passano |
|:-----------------|-----------:|---------------:|-----------:|-------------:|----------:|
| bb_fade          |         36 |          0.583 |      0.339 |        0.02  |         3 |
| keltner_reversal |         24 |          0.5   |      0.373 |        0.004 |         5 |
| zscore_revert    |         36 |          0.25  |      0.148 |       -0.022 |         4 |
| consecutive_bars |         16 |          0     |     -0.001 |       -0.025 |         0 |
| rsi_extreme      |         36 |          0     |     -0.008 |       -0.055 |         0 |
| asia_range_fade  |         24 |          0     |     -0.054 |       -0.13  |         0 |
| pdh_pdl_sweep    |         32 |          0     |     -0.064 |       -0.137 |         0 |

## Fase 2 · Con costi reali

| strategy         | params                                             |   n |   exp_gross |   expectancy |   cost_share |    pf |   max_dd_r | pass   |
|:-----------------|:---------------------------------------------------|----:|------------:|-------------:|-------------:|------:|-----------:|:-------|
| zscore_revert    | {"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} | 135 |       0.117 |        0.075 |        0.357 | 1.188 |      9.111 | True   |
| keltner_reversal | {"buf": 0.5, "mult": 2.5, "n": 50, "trend": 0}     | 267 |       0.123 |        0.056 |        0.543 | 1.106 |     21.753 | True   |
| zscore_revert    | {"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.5} | 137 |       0.091 |        0.052 |        0.426 | 1.15  |     10.878 | True   |
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}     | 333 |       0.086 |        0.038 |        0.557 | 1.078 |     11.585 | True   |
| bb_fade          | {"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}     | 213 |       0.094 |        0.047 |        0.501 | 1.094 |      9.071 | True   |
| keltner_reversal | {"buf": 0.2, "mult": 2.5, "n": 50, "trend": 0}     | 288 |       0.104 |        0.043 |        0.585 | 1.071 |     31.164 | True   |
| zscore_revert    | {"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | 163 |       0.081 |        0.047 |        0.418 | 1.081 |     18.346 | True   |
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 0}     | 425 |       0.085 |        0.031 |        0.639 | 1.072 |     12.279 | False  |
| keltner_reversal | {"buf": 0.5, "mult": 2.0, "n": 20, "trend": 0}     | 219 |       0.084 |        0.023 |        0.731 | 1.047 |     10.765 | False  |
| zscore_revert    | {"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} | 212 |       0.057 |        0.018 |        0.689 | 1.041 |     14.859 | False  |
| keltner_reversal | {"buf": 0.5, "mult": 2.5, "n": 20, "trend": 0}     |  82 |       0.063 |        0     |        0.993 | 1.001 |      7.963 | False  |
| keltner_reversal | {"buf": 0.2, "mult": 2.0, "n": 20, "trend": 0}     | 221 |       0.053 |       -0.002 |        1.03  | 0.997 |     17.874 | False  |

## Fase 3 · Pass rate per modello di rischio (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.038 |  0.141 |  0.141 |  0.109 |  0.057 |
| dd_lineare               |  0.01  |  0.109 |  0.191 |  0.206 |  0.145 |
| dd_lineare+guardia+coast |  0.007 |  0.103 |  0.207 |  0.256 |  0.286 |
| dd_scaglioni             |  0.011 |  0.099 |  0.165 |  0.18  |  0.133 |
| guardia_giornaliera      |  0.014 |  0.16  |  0.257 |  0.292 |  0.301 |
| statico                  |  0.014 |  0.155 |  0.231 |  0.222 |  0.148 |
| streak_perdite           |  0.006 |  0.103 |  0.193 |  0.202 |  0.15  |

## Fase 3 · Fallimento per DAILY loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |      0 |  0.013 |  0.281 |  0.554 |  0.816 |
| dd_lineare               |      0 |  0     |  0.026 |  0.18  |  0.575 |
| dd_lineare+guardia+coast |      0 |  0     |  0     |  0     |  0.02  |
| dd_scaglioni             |      0 |  0     |  0.085 |  0.172 |  0.511 |
| guardia_giornaliera      |      0 |  0     |  0     |  0     |  0.043 |
| statico                  |      0 |  0.022 |  0.184 |  0.367 |  0.673 |
| streak_perdite           |      0 |  0     |  0.117 |  0.294 |  0.63  |

## Fase 3 · Fallimento per MAX loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.055 |  0.3   |  0.322 |  0.253 |  0.125 |
| dd_lineare               |  0     |  0.051 |  0.194 |  0.293 |  0.211 |
| dd_lineare+guardia+coast |  0     |  0.026 |  0.121 |  0.235 |  0.393 |
| dd_scaglioni             |  0.015 |  0.134 |  0.203 |  0.246 |  0.183 |
| guardia_giornaliera      |  0.029 |  0.199 |  0.343 |  0.429 |  0.467 |
| statico                  |  0.056 |  0.284 |  0.347 |  0.324 |  0.172 |
| streak_perdite           |  0.041 |  0.281 |  0.385 |  0.378 |  0.206 |

## Fase 3 · EV per tentativo (media, valuta conto)

| risk_family              |     0.5% |     1.0% |    1.5% |     2.0% |     3.0% |
|:-------------------------|---------:|---------:|--------:|---------:|---------:|
| anti_martingala          | -438.183 |   -0.607 |  58.675 | -163.156 | -473.901 |
| dd_lineare               | -511.231 | -136.963 | 343.401 |  441.752 |  119.365 |
| dd_lineare+guardia+coast | -518.234 | -142.473 | 428.744 |  800.602 | 1384.22  |
| dd_scaglioni             | -507.352 | -178.621 | 152.673 |  229.033 |   67.702 |
| guardia_giornaliera      | -496.365 |  208.852 | 956.452 | 1371.38  | 1802.52  |
| statico                  | -496.365 |  175.186 | 759.537 |  708.856 |  183.088 |
| streak_perdite           | -524.547 | -178.408 | 387.713 |  508.622 |  176.926 |

## Fase 3 · Migliori combinazioni prop

| candidate                                                        | rules            | risk_profile                  |   pass_rate |   fail_daily |   fail_max |   median_days |   ev_attempt |
|:-----------------------------------------------------------------|:-----------------|:------------------------------|------------:|-------------:|-----------:|--------------:|-------------:|
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |       0.453 |        0     |      0.423 |          47   |      5694.82 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |       0.45  |        0     |      0.103 |          84   |      4013.6  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|3.0%      |       0.41  |        0     |      0.48  |          36   |      3659.5  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|3.0%      |       0.42  |        0     |      0.157 |          72.5 |      3470.76 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|3.0%      |       0.34  |        0     |      0.447 |          44   |      3321.03 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.35  |        0     |      0.267 |          48   |      3134.44 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|2.0%      |       0.397 |        0     |      0.487 |          62   |      2935.82 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|2.0%      |       0.367 |        0     |      0.44  |          67   |      2783.05 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | dd_lineare+guardia+coast|3.0% |       0.36  |        0     |      0.38  |          39.5 |      2669.16 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|3.0%      |       0.373 |        0     |      0.603 |          35.5 |      2629.71 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | statico|2.0%                  |       0.37  |        0.073 |      0.5   |          58   |      2620.86 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.357 |        0     |      0.223 |          55   |      2567.75 |
| keltner_reversal|{"buf": 0.5, "mult": 2.5, "n": 50, "trend": 0}  | two_step_classic | guardia_giornaliera|2.0%      |       0.31  |        0     |      0.57  |          57   |      2495.35 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|2.0%      |       0.36  |        0     |      0.33  |          78.5 |      2473.91 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | statico|2.0%                  |       0.35  |        0     |      0.54  |          78   |      2456.79 |

## Fase 4 · Conferma OOS

| candidate                                                        |   n_is |   exp_is |   n_oos |   exp_oos |   pf_oos |   dd_oos_r |   dsr_is |   trials | verdetto     |
|:-----------------------------------------------------------------|-------:|---------:|--------:|----------:|---------:|-----------:|---------:|---------:|:-------------|
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} |    135 |    0.075 |      55 |     0.216 |    1.609 |      3.376 |    0.001 |      408 | DA_OSSERVARE |
| keltner_reversal|{"buf": 0.5, "mult": 2.5, "n": 50, "trend": 0}  |    267 |    0.056 |     102 |     0.078 |    1.145 |     10.815 |    0     |      408 | DA_OSSERVARE |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.5} |    137 |    0.052 |      55 |     0.201 |    1.742 |      3.376 |    0     |      408 | DA_OSSERVARE |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           |    333 |    0.038 |     140 |     0.267 |    1.764 |      2.513 |    0     |      408 | DA_OSSERVARE |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           |    213 |    0.047 |      86 |     0.342 |    2.008 |      3.023 |    0     |      408 | DA_OSSERVARE |
| keltner_reversal|{"buf": 0.2, "mult": 2.5, "n": 50, "trend": 0}  |    288 |    0.043 |     110 |     0.091 |    1.151 |     10.932 |    0     |      408 | DA_OSSERVARE |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} |    163 |    0.047 |      60 |     0.148 |    1.272 |      6.106 |    0     |      408 | DA_OSSERVARE |

## Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)

| candidate                                                        | rules            | risk_profile                  |   pass_rate_is |   pass_rate |   fail_daily |   fail_max |   ev_is |   ev_attempt |
|:-----------------------------------------------------------------|:-----------------|:------------------------------|---------------:|------------:|-------------:|-----------:|--------:|-------------:|
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |          0.453 |       0.273 |            0 |      0.523 | 5694.82 |      2013.86 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |          0.45  |       0.553 |            0 |      0.01  | 4013.6  |      6483.26 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|3.0%      |          0.41  |       0.267 |            0 |      0.617 | 3659.5  |      1668.07 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|3.0%      |          0.42  |       0.507 |            0 |      0.007 | 3470.76 |      4938.68 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|3.0%      |          0.34  |       0.83  |            0 |      0.07  | 3321.03 |     23265.9  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.35  |       0.33  |            0 |      0.17  | 3134.44 |      2337.57 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|2.0%      |          0.397 |       0.953 |            0 |      0.027 | 2935.82 |     28929    |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | guardia_giornaliera|2.0%      |          0.367 |       0.32  |            0 |      0.417 | 2783.05 |      1629.5  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.5, "z_exit": 0.0} | two_step_tight   | dd_lineare+guardia+coast|3.0% |          0.36  |       0.317 |            0 |      0.32  | 2669.16 |      1897.22 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|3.0%      |          0.373 |       0.813 |            0 |      0.16  | 2629.71 |     32146.5  |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | statico|2.0%                  |          0.37  |       0.95  |            0 |      0.043 | 2620.86 |     28543.7  |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.357 |       0.893 |            0 |      0.013 | 2567.75 |     24222.3  |
| keltner_reversal|{"buf": 0.5, "mult": 2.5, "n": 50, "trend": 0}  | two_step_classic | guardia_giornaliera|2.0%      |          0.31  |       0.407 |            0 |      0.42  | 2495.35 |      2890.87 |
| bb_fade|{"atr_sl": 2.5, "k": 2.5, "n": 50, "trend": 0}           | two_step_classic | guardia_giornaliera|2.0%      |          0.36  |       0.927 |            0 |      0.017 | 2473.91 |     22291.9  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.5, "z_exit": 0.5} | two_step_tight   | guardia_giornaliera|3.0%      |          0.38  |       0.657 |            0 |      0     | 2408.16 |      8865.36 |
