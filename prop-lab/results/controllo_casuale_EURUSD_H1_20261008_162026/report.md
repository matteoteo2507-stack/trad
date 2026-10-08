# Report controllo_casuale_EURUSD_H1_20261008_162026

Simbolo **EURUSD** H1 · dati 2012-01-05 17:00:00 → 2026-07-06 11:00:00 · IS fino a 2022-03-02 12:00:00

## Fase 1 · Famiglia (qualitativo, senza costi)

| strategy         |   varianti |   pct_positive |   best_exp |   median_exp |   passano |
|:-----------------|-----------:|---------------:|-----------:|-------------:|----------:|
| ingresso_casuale |         36 |          0.472 |      0.105 |       -0.004 |         6 |

## Fase 2 · Con costi reali

| strategy         | params                                                |   n |   exp_gross |   expectancy |   cost_share |    pf |   max_dd_r | pass   |
|:-----------------|:------------------------------------------------------|----:|------------:|-------------:|-------------:|------:|-----------:|:-------|
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | 564 |       0.105 |        0.043 |        0.591 | 1.089 |     15.717 | True   |
| ingresso_casuale | {"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | 496 |       0.084 |        0.047 |        0.439 | 1.08  |     19.311 | True   |
| ingresso_casuale | {"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | 481 |       0.085 |        0.038 |        0.545 | 1.062 |     22.462 | True   |
| ingresso_casuale | {"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | 536 |       0.059 |        0.019 |        0.676 | 1.04  |     16.527 | False  |
| ingresso_casuale | {"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | 541 |       0.074 |        0.009 |        0.88  | 1.013 |     27.228 | False  |

## Fase 3 · Pass rate per modello di rischio (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.024 |  0.124 |  0.14  |  0.121 |  0.091 |
| dd_lineare               |  0.002 |  0.066 |  0.145 |  0.184 |  0.169 |
| dd_lineare+guardia+coast |  0     |  0.058 |  0.153 |  0.2   |  0.255 |
| dd_scaglioni             |  0.003 |  0.068 |  0.144 |  0.179 |  0.144 |
| guardia_giornaliera      |  0.003 |  0.085 |  0.199 |  0.245 |  0.276 |
| statico                  |  0.003 |  0.085 |  0.194 |  0.231 |  0.19  |
| streak_perdite           |  0.001 |  0.063 |  0.165 |  0.215 |  0.186 |

## Fase 3 · Fallimento per DAILY loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.001 |  0.006 |  0.206 |  0.442 |  0.69  |
| dd_lineare               |  0     |  0.001 |  0.009 |  0.055 |  0.379 |
| dd_lineare+guardia+coast |  0     |  0.001 |  0.006 |  0.013 |  0.023 |
| dd_scaglioni             |  0     |  0.001 |  0.026 |  0.043 |  0.357 |
| guardia_giornaliera      |  0     |  0.003 |  0.013 |  0.015 |  0.033 |
| statico                  |  0     |  0.003 |  0.058 |  0.122 |  0.423 |
| streak_perdite           |  0     |  0.003 |  0.042 |  0.094 |  0.396 |

## Fase 3 · Fallimento per MAX loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.004 |  0.179 |  0.246 |  0.267 |  0.207 |
| dd_lineare               |  0     |  0.01  |  0.102 |  0.237 |  0.277 |
| dd_lineare+guardia+coast |  0     |  0     |  0.012 |  0.039 |  0.129 |
| dd_scaglioni             |  0.002 |  0.084 |  0.198 |  0.274 |  0.223 |
| guardia_giornaliera      |  0.001 |  0.037 |  0.104 |  0.164 |  0.239 |
| statico                  |  0.019 |  0.225 |  0.402 |  0.506 |  0.374 |
| streak_perdite           |  0     |  0.126 |  0.314 |  0.447 |  0.376 |

## Fase 3 · EV per tentativo (media, valuta conto)

| risk_family              |     0.5% |     1.0% |    1.5% |    2.0% |     3.0% |
|:-------------------------|---------:|---------:|--------:|--------:|---------:|
| anti_martingala          | -506.611 |  -43.019 |  98.083 | -24.849 | -379.501 |
| dd_lineare               | -544.871 | -376.905 |  47.266 | 367.448 |  412.235 |
| dd_lineare+guardia+coast | -546.13  | -384.943 |  53.689 | 523.186 | 1106.59  |
| dd_scaglioni             | -543.53  | -344.749 |  57.794 | 354.494 |  296.449 |
| guardia_giornaliera      | -543.417 | -259.376 | 402.571 | 948.238 | 1544.82  |
| statico                  | -543.417 | -260.43  | 387.862 | 779.525 |  654.13  |
| streak_perdite           | -545.838 | -369.765 | 145.444 | 600.618 |  662.083 |

## Fase 3 · EV dovuto al VANTAGGIO (EV meno lo stesso EV a vantaggio zero)

| risk_family              |   0.5% |    1.0% |    1.5% |    2.0% |    3.0% |
|:-------------------------|-------:|--------:|--------:|--------:|--------:|
| anti_martingala          | 15.48  | 182.809 | 177.405 | 123.918 |  31.904 |
| dd_lineare               |  0.862 |  63.484 | 172.112 | 263.649 | 250.063 |
| dd_lineare+guardia+coast |  0.258 |  64.012 | 156.374 | 311.73  | 465.54  |
| dd_scaglioni             |  1.814 |  82.612 | 186.471 | 242.785 | 269.892 |
| guardia_giornaliera      |  1.39  |  99.457 | 279.054 | 345.886 | 586.23  |
| statico                  |  1.39  |  99.681 | 274.038 | 313.145 | 294.803 |
| streak_perdite           |  0.389 |  70.615 | 199.905 | 289.062 | 291.626 |

## Fase 3 · Migliori combinazioni prop (ordinate per ev_vs_zero)

| candidate                                                              | rules             | risk_profile                  |   pass_rate |   pass_zero |   fail_daily |   fail_max |   median_days |   ev_attempt |   ev_zero |   ev_vs_zero |
|:-----------------------------------------------------------------------|:------------------|:------------------------------|------------:|------------:|-------------:|-----------:|--------------:|-------------:|----------:|-------------:|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | one_step_trailing | guardia_giornaliera|3.0%      |       0.29  |       0.147 |        0.09  |      0.247 |          32   |      979.516 |   107.761 |      871.754 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | one_step_trailing | dd_lineare+guardia+coast|3.0% |       0.287 |       0.21  |        0.053 |      0.187 |          40   |      906.853 |   148.999 |      757.855 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_classic  | statico|3.0%                  |       0.26  |       0.2   |        0.29  |      0.393 |          56.5 |     1304.3   |   553.648 |      750.649 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | one_step_trailing | guardia_giornaliera|3.0%      |       0.287 |       0.22  |        0.053 |      0.223 |          32   |     1257.05  |   544.415 |      712.634 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | one_step_trailing | dd_lineare+guardia+coast|3.0% |       0.297 |       0.237 |        0.02  |      0.17  |          35   |     1087.44  |   410.972 |      676.465 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_classic  | guardia_giornaliera|3.0%      |       0.313 |       0.25  |        0.017 |      0.157 |          61.5 |     1672.59  |  1012.77  |      659.813 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_tight    | guardia_giornaliera|3.0%      |       0.3   |       0.253 |        0.013 |      0.21  |          50   |     1476.05  |   860.756 |      615.29  |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_classic  | streak_perdite|3.0%           |       0.25  |       0.213 |        0.18  |      0.45  |          62   |     1275.08  |   687.683 |      587.394 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | guardia_giornaliera|3.0%      |       0.29  |       0.237 |        0.01  |      0.277 |          55   |     2039.46  |  1464.5   |      574.964 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_classic  | dd_lineare+guardia+coast|3.0% |       0.237 |       0.203 |        0.027 |      0.073 |          67   |     1163.85  |   594.603 |      569.247 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | two_step_classic  | guardia_giornaliera|3.0%      |       0.28  |       0.24  |        0.017 |      0.193 |          55.5 |     2359.02  |  1791.93  |      567.088 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_classic  | guardia_giornaliera|2.0%      |       0.177 |       0.11  |        0.033 |      0.073 |         101   |      649.572 |    83.005 |      566.567 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_tight    | dd_lineare|3.0%               |       0.24  |       0.183 |        0.167 |      0.357 |          49.5 |      873.871 |   311.055 |      562.817 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | two_step_classic  | statico|3.0%                  |       0.28  |       0.223 |        0.12  |      0.59  |          53   |     1635.2   |  1092.71  |      542.497 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | two_step_tight    | dd_lineare+guardia+coast|3.0% |       0.297 |       0.233 |        0.02  |      0.09  |          58   |     1211.1   |   680.039 |      531.056 |

> Come si legge: decide il **verdetto** della conferma (intervallo OOS corretto per i candidati; il DSR e' diagnostica).
> `ev_vs_zero` toglie il valore d'opzione della challenge ma **non il caso**: su un candidato
> NON_DIMOSTRATA non dice niente. Per un candidato vero: `lab.prop.evaluate_ci`.

## Fase 4 · Conferma OOS

| candidate                                                              |   n_is |   exp_is |   n_oos |   exp_oos |   exp_oos_lo |   exp_oos_hi |   mde_oos |   pf_oos |   dd_oos_r |   dsr_is |   trials |   n_candidati | verdetto       |
|:-----------------------------------------------------------------------|-------:|---------:|--------:|----------:|-------------:|-------------:|----------:|---------:|-----------:|---------:|---------:|--------------:|:---------------|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} |    564 |    0.043 |     272 |    -0.023 |       -0.169 |        0.124 |     0.197 |    0.956 |     17.966 |    0.166 |       36 |             3 | NON_DIMOSTRATA |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} |    496 |    0.047 |     232 |    -0.009 |       -0.218 |        0.199 |     0.28  |    0.985 |     20.877 |    0.115 |       36 |             3 | NON_DIMOSTRATA |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} |    481 |    0.038 |     228 |     0.017 |       -0.222 |        0.256 |     0.321 |    1.027 |     19.66  |    0.076 |       36 |             3 | NON_DIMOSTRATA |

## Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)

| candidate                                                              | verdetto       | rules             | risk_profile                  |   pass_rate_is |   pass_rate |   pass_zero |   fail_daily |   fail_max |    ev_is |   ev_attempt |   ev_vs_zero_is |   ev_vs_zero |
|:-----------------------------------------------------------------------|:---------------|:------------------|:------------------------------|---------------:|------------:|------------:|-------------:|-----------:|---------:|-------------:|----------------:|-------------:|
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | one_step_trailing | guardia_giornaliera|3.0%      |          0.29  |       0.193 |       0.21  |        0.047 |      0.35  |  979.516 |       21.799 |         871.754 |     -184.935 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.287 |       0.19  |       0.22  |        0.023 |      0.227 |  906.853 |      -26.642 |         757.855 |     -182.065 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_classic  | statico|3.0%                  |          0.26  |       0.167 |       0.18  |        0.267 |      0.507 | 1304.3   |      421.68  |         750.649 |     -133.596 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | one_step_trailing | guardia_giornaliera|3.0%      |          0.287 |       0.22  |       0.233 |        0.02  |      0.307 | 1257.05  |      378.976 |         712.634 |      -23.376 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | one_step_trailing | dd_lineare+guardia+coast|3.0% |          0.297 |       0.247 |       0.253 |        0.01  |      0.203 | 1087.44  |      490.733 |         676.465 |      -42.027 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.313 |       0.21  |       0.233 |        0.043 |      0.163 | 1672.59  |      834.715 |         659.813 |     -139.194 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_tight    | guardia_giornaliera|3.0%      |          0.3   |       0.227 |       0.26  |        0.03  |      0.24  | 1476.05  |      886.054 |         615.29  |     -193.533 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_classic  | streak_perdite|3.0%           |          0.25  |       0.183 |       0.207 |        0.21  |      0.517 | 1275.08  |      678.12  |         587.394 |     -226.295 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.29  |       0.233 |       0.223 |        0.017 |      0.3   | 2039.46  |     1540.66  |         574.964 |       92.504 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_classic  | guardia_giornaliera|3.0%      |          0.28  |       0.25  |       0.253 |        0.023 |      0.213 | 2359.02  |      930.716 |         567.088 |      -89.187 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_tight    | dd_lineare|3.0%               |          0.24  |       0.15  |       0.17  |        0.187 |      0.49  |  873.871 |      232.438 |         562.817 |     -199.215 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_classic  | statico|3.0%                  |          0.28  |       0.233 |       0.23  |        0.107 |      0.657 | 1635.2   |     1270.75  |         542.497 |       85.682 |
| ingresso_casuale|{"atr_sl": 1.5, "freq": 0.01, "seed": 2, "tp_r": 1.0} | NON_DIMOSTRATA | two_step_tight    | dd_lineare+guardia+coast|3.0% |          0.297 |       0.193 |       0.223 |        0.027 |      0.083 | 1211.1   |      498.126 |         531.056 |     -344.713 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 2.0} | NON_DIMOSTRATA | two_step_classic  | dd_lineare+guardia+coast|3.0% |          0.253 |       0.23  |       0.237 |        0.007 |      0.067 | 1394.95  |      706.857 |         506.946 |     -113.729 |
| ingresso_casuale|{"atr_sl": 2.5, "freq": 0.01, "seed": 2, "tp_r": 3.0} | NON_DIMOSTRATA | two_step_tight    | dd_scaglioni|3.0%             |          0.163 |       0.18  |       0.17  |        0.043 |      0.627 |  854.367 |      613.666 |         494.952 |      188.461 |
