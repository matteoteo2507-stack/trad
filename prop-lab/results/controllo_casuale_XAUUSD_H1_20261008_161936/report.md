# Report controllo_casuale_XAUUSD_H1_20261008_161936

Simbolo **XAUUSD** H1 · dati 2020-05-19 08:00:00 → 2026-07-06 11:00:00 · IS fino a 2024-08-30 04:00:00

## Fase 1 · Famiglia (qualitativo, senza costi)

| strategy         |   varianti |   pct_positive |   best_exp |   median_exp |   passano |
|:-----------------|-----------:|---------------:|-----------:|-------------:|----------:|
| ingresso_casuale |         36 |          0.639 |      0.205 |        0.021 |         6 |

## Fase 2 · Con costi reali

| strategy         | params                                                |   n |   exp_gross |   expectancy |   cost_share |    pf |   max_dd_r | pass   |
|:-----------------|:------------------------------------------------------|----:|------------:|-------------:|-------------:|------:|-----------:|:-------|
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | 209 |       0.205 |        0.113 |        0.45  | 1.161 |     20.856 | True   |
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | 217 |       0.142 |        0.06  |        0.575 | 1.094 |     18.477 | True   |
| ingresso_casuale | {"atr_sl": 2.5, "freq": 0.01, "seed": 1, "tp_r": 3.0} | 202 |       0.114 |        0.035 |        0.691 | 1.056 |     25.377 | False  |
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 1, "tp_r": 1.0} | 237 |       0.051 |       -0.016 |        1.309 | 0.969 |     19.467 | False  |
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | 225 |       0.057 |       -0.043 |        1.747 | 0.918 |     23.266 | False  |

## Fase 3 · Pass rate per modello di rischio (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.029 |  0.128 |  0.136 |  0.124 |  0.11  |
| dd_lineare               |  0.004 |  0.103 |  0.182 |  0.214 |  0.179 |
| dd_lineare+guardia+coast |  0.002 |  0.107 |  0.197 |  0.23  |  0.254 |
| dd_scaglioni             |  0.006 |  0.098 |  0.163 |  0.186 |  0.149 |
| guardia_giornaliera      |  0.007 |  0.143 |  0.252 |  0.278 |  0.267 |
| statico                  |  0.007 |  0.143 |  0.244 |  0.262 |  0.206 |
| streak_perdite           |  0.004 |  0.081 |  0.188 |  0.23  |  0.193 |

## Fase 3 · Fallimento per DAILY loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |      0 |  0.004 |  0.158 |  0.356 |  0.598 |
| dd_lineare               |      0 |  0     |  0.002 |  0.024 |  0.351 |
| dd_lineare+guardia+coast |      0 |  0     |  0     |  0     |  0.035 |
| dd_scaglioni             |      0 |  0     |  0.013 |  0.028 |  0.347 |
| guardia_giornaliera      |      0 |  0     |  0     |  0     |  0.058 |
| statico                  |      0 |  0     |  0.023 |  0.047 |  0.357 |
| streak_perdite           |      0 |  0     |  0.031 |  0.047 |  0.361 |

## Fase 3 · Fallimento per MAX loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.004 |  0.215 |  0.348 |  0.364 |  0.283 |
| dd_lineare               |  0     |  0.026 |  0.153 |  0.341 |  0.357 |
| dd_lineare+guardia+coast |  0     |  0.004 |  0.04  |  0.108 |  0.262 |
| dd_scaglioni             |  0.003 |  0.123 |  0.261 |  0.357 |  0.291 |
| guardia_giornaliera      |  0.008 |  0.106 |  0.249 |  0.357 |  0.421 |
| statico                  |  0.031 |  0.311 |  0.519 |  0.616 |  0.431 |
| streak_perdite           |  0.001 |  0.157 |  0.381 |  0.546 |  0.428 |

## Fase 3 · EV per tentativo (media, valuta conto)

| risk_family              |     0.5% |     1.0% |    1.5% |     2.0% |     3.0% |
|:-------------------------|---------:|---------:|--------:|---------:|---------:|
| anti_martingala          | -492.901 |  -64.501 |  28.674 |   20.49  | -345.531 |
| dd_lineare               | -539.672 | -262.326 | 174.037 |  503.065 |  486.79  |
| dd_lineare+guardia+coast | -541.375 | -235.441 | 261.381 |  650.193 | 1069.27  |
| dd_scaglioni             | -536.808 | -264.594 | 131.563 |  404.452 |  331.329 |
| guardia_giornaliera      | -536.835 |  -34.744 | 788.152 | 1227.52  | 1346.43  |
| statico                  | -536.835 |  -22.379 | 704.338 |  968.911 |  767.501 |
| streak_perdite           | -541.433 | -309.764 | 226.686 |  658.616 |  674.664 |

## Fase 3 · EV dovuto al VANTAGGIO (EV meno lo stesso EV a vantaggio zero)

| risk_family              |   0.5% |    1.0% |    1.5% |    2.0% |    3.0% |
|:-------------------------|-------:|--------:|--------:|--------:|--------:|
| anti_martingala          | 31.16  | 208.694 | 239.464 | 256.969 | 104.124 |
| dd_lineare               |  6.369 | 170.675 | 356.705 | 465.949 | 383.877 |
| dd_lineare+guardia+coast |  1.895 | 187.24  | 412.759 | 531.394 | 785.78  |
| dd_scaglioni             |  9.203 | 157.795 | 327.968 | 409.13  | 332.586 |
| guardia_giornaliera      |  9.176 | 279.41  | 656.005 | 811.931 | 839.727 |
| statico                  |  9.176 | 291.634 | 648.453 | 681.809 | 473.655 |
| streak_perdite           |  2.18  | 116.309 | 359.562 | 525.755 | 442.572 |

## Fase 3 · Migliori combinazioni prop (ordinate per ev_vs_zero)

| candidate                                                              | rules             | risk_profile                  |   pass_rate |   pass_zero |   fail_daily |   fail_max |   median_days |   ev_attempt |   ev_zero |   ev_vs_zero |
|:-----------------------------------------------------------------------|:------------------|:------------------------------|------------:|------------:|-------------:|-----------:|--------------:|-------------:|----------:|-------------:|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | guardia_giornaliera|2.0%      |       0.31  |       0.227 |        0     |      0.347 |          69   |     2371.47  |   753.284 |     1618.18  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | statico|2.0%                  |       0.3   |       0.23  |        0     |      0.597 |          67   |     2265.96  |   826.471 |     1439.49  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | guardia_giornaliera|1.5%      |       0.297 |       0.197 |        0     |      0.323 |          84   |     1489.69  |   275.505 |     1214.19  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | guardia_giornaliera|3.0%      |       0.323 |       0.247 |        0     |      0.467 |          40   |     2203.36  |   990.815 |     1212.54  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | statico|1.5%                  |       0.297 |       0.197 |        0     |      0.58  |          84   |     1501.9   |   330.47  |     1171.43  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | guardia_giornaliera|2.0%      |       0.323 |       0.243 |        0     |      0.417 |          52   |     1749.7   |   660.523 |     1089.18  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | dd_lineare+guardia+coast|3.0% |       0.267 |       0.193 |        0     |      0.227 |          47   |     1769.9   |   695.553 |     1074.34  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | guardia_giornaliera|3.0%      |       0.283 |       0.233 |        0     |      0.523 |          24   |     2045.61  |   975.586 |     1070.02  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | streak_perdite|3.0%           |       0.273 |       0.207 |        0.07  |      0.603 |          39   |     1730.31  |   684.436 |     1045.87  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | one_step_trailing | dd_lineare+guardia+coast|3.0% |       0.213 |       0.06  |        0.12  |      0.333 |          45.5 |      440.832 |  -532.528 |      973.361 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | statico|1.5%                  |       0.26  |       0.173 |        0     |      0.433 |          88.5 |     1156.69  |   266.311 |      890.382 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | guardia_giornaliera|1.5%      |       0.26  |       0.173 |        0     |      0.213 |          88.5 |     1141.42  |   255.349 |      886.074 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | statico|2.0%                  |       0.293 |       0.223 |        0.083 |      0.587 |          49.5 |     1272.28  |   391.692 |      880.59  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | statico|3.0%                  |       0.317 |       0.24  |        0.053 |      0.63  |          40   |     1706.88  |   830.389 |      876.488 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_tight    | dd_lineare+guardia+coast|3.0% |       0.28  |       0.207 |        0     |      0.373 |          33   |     1635.59  |   769.029 |      866.558 |

> Come si legge: decide il **verdetto** della conferma (intervallo OOS corretto per i candidati; il DSR e' diagnostica).
> `ev_vs_zero` toglie il valore d'opzione della challenge ma **non il caso**: su un candidato
> NON_DIMOSTRATA non dice niente. Per un candidato vero: `lab.prop.evaluate_ci`.

## Fase 4 · Conferma OOS

| candidate                                                              |   n_is |   exp_is |   n_oos |   exp_oos |   exp_oos_lo |   exp_oos_hi |   mde_oos |   pf_oos |   dd_oos_r |   dsr_is |   trials |   n_candidati | verdetto       |
|:-----------------------------------------------------------------------|-------:|---------:|--------:|----------:|-------------:|-------------:|----------:|---------:|-----------:|---------:|---------:|--------------:|:---------------|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} |    209 |    0.113 |      82 |    -0.335 |       -0.697 |        0.026 |     0.488 |    0.585 |     35.288 |    0.307 |       36 |             2 | NON_DIMOSTRATA |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} |    217 |    0.06  |      86 |    -0.197 |       -0.521 |        0.127 |     0.438 |    0.727 |     28.542 |    0.198 |       36 |             2 | NON_DIMOSTRATA |

## Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)

| candidate                                                              | verdetto       | rules             | risk_profile                  |   pass_rate_is |   pass_rate |   pass_zero |   fail_daily |   fail_max |    ev_is |   ev_attempt |   ev_vs_zero_is |   ev_vs_zero |
|:-----------------------------------------------------------------------|:---------------|:------------------|:------------------------------|---------------:|------------:|------------:|-------------:|-----------:|---------:|-------------:|----------------:|-------------:|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|2.0%      |          0.31  |       0.043 |       0.213 |        0     |      0.367 | 2371.47  |     -369.465 |        1618.18  |    -1029.3   |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_classic  | statico|2.0%                  |          0.3   |       0.04  |       0.213 |        0     |      0.853 | 2265.96  |     -369.465 |        1439.49  |     -990.9   |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|1.5%      |          0.297 |       0.037 |       0.16  |        0     |      0.34  | 1489.69  |     -405.367 |        1214.19  |     -574.033 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.323 |       0.073 |       0.217 |        0     |      0.5   | 2203.36  |     -278.111 |        1212.54  |     -899.659 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_tight    | statico|1.5%                  |          0.297 |       0.033 |       0.16  |        0     |      0.837 | 1501.9   |     -405.367 |        1171.43  |     -612.715 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|2.0%      |          0.323 |       0.053 |       0.22  |        0     |      0.45  | 1749.7   |     -349.389 |        1089.18  |     -831.913 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.213 |       0.047 |       0.123 |        0.033 |      0.48  |  440.832 |     -514.136 |         973.361 |     -363.594 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | one_step_trailing | statico|1.5%                  |          0.29  |       0.06  |       0.23  |        0.07  |      0.85  |  744.261 |     -479.028 |         789.28  |     -731.82  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|3.0%      |          0.293 |       0.12  |       0.21  |        0     |      0.477 | 1527.42  |     -228.218 |         764.186 |     -594.606 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | one_step_trailing | guardia_giornaliera|3.0%      |          0.173 |       0.043 |       0.147 |        0.063 |      0.573 |  271.767 |     -492.297 |         763.979 |     -512.911 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.313 |       0.117 |       0.213 |        0     |      0.407 | 1654.28  |     -275.882 |         733.127 |     -930.831 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_classic  | statico|2.0%                  |          0.267 |       0.057 |       0.183 |        0     |      0.757 | 1123.59  |     -395.96  |         692.501 |     -676.081 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.23  |       0.1   |       0.19  |        0.04  |      0.41  |  607.699 |     -410.802 |         660.861 |     -547.318 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_classic  | statico|3.0%                  |          0.287 |       0.127 |       0.22  |        0.087 |      0.77  | 1362.25  |     -193.732 |         603.504 |     -898.314 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_tight    | statico|3.0%                  |          0.287 |       0.123 |       0.197 |        0.053 |      0.82  | 1233.37  |     -206.884 |         559.211 |     -723.904 |
