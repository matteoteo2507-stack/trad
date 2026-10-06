> ⚠️ **Controllo POSITIVO** su dati sintetici (`tools/make_demo_data.py --mode mr`, mean reversion iniettata alla forza originale, 3 anni). Generato il 07/10/2026 col codice corretto. La pipeline la vede in fase 1 e ne conferma 2 candidati su 8 fuori campione: con 3 anni il vantaggio debole e' al limite della potenza. Con `--forza 5` le promosse sono 8 su 8. I numeri non hanno valore di trading.

# Report mean_reversion_XAUUSD_H1_20261006_221000

Simbolo **XAUUSD** H1 · dati 2022-01-03 00:00:00 → 2025-01-01 23:00:00 · IS fino a 2024-02-08 02:00:00

## Fase 1 · Famiglia (qualitativo, senza costi)

| strategy         |   varianti |   pct_positive |   best_exp |   median_exp |   passano |
|:-----------------|-----------:|---------------:|-----------:|-------------:|----------:|
| pdh_pdl_sweep    |         32 |          1     |      0.13  |        0.081 |        19 |
| zscore_revert    |         36 |          0.833 |      0.267 |        0.054 |        15 |
| keltner_reversal |         24 |          0.708 |      0.084 |        0.021 |         6 |
| consecutive_bars |         16 |          0.812 |      0.039 |        0.02  |         0 |
| rsi_extreme      |         36 |          0.556 |      0.673 |        0.004 |         3 |
| bb_fade          |         36 |          0.444 |      0.265 |       -0.03  |        12 |
| asia_range_fade  |         24 |          0.083 |      0.026 |       -0.035 |         0 |

## Fase 2 · Con costi reali

| strategy         | params                                              |   n |   exp_gross |   expectancy |   cost_share |    pf |   max_dd_r | pass   |
|:-----------------|:----------------------------------------------------|----:|------------:|-------------:|-------------:|------:|-----------:|:-------|
| zscore_revert    | {"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5}  | 256 |       0.212 |        0.173 |        0.186 | 1.413 |      8.86  | True   |
| zscore_revert    | {"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5}  | 325 |       0.259 |        0.18  |        0.303 | 1.318 |     15.15  | True   |
| zscore_revert    | {"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0}  | 249 |       0.21  |        0.165 |        0.212 | 1.339 |      9.234 | True   |
| zscore_revert    | {"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0}  | 320 |       0.267 |        0.192 |        0.28  | 1.307 |     13.541 | True   |
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}      | 355 |       0.192 |        0.138 |        0.282 | 1.254 |     20.165 | True   |
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 0}      | 460 |       0.128 |        0.079 |        0.381 | 1.158 |     14.209 | True   |
| zscore_revert    | {"atr_sl": 2.0, "n": 50, "z": 2.0, "z_exit": 0.5}   | 462 |       0.139 |        0.078 |        0.435 | 1.157 |     13.293 | True   |
| bb_fade          | {"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 0}      | 637 |       0.131 |        0.061 |        0.537 | 1.093 |     21.62  | True   |
| bb_fade          | {"atr_sl": 1.5, "k": 2.0, "n": 20, "trend": 0}      | 815 |       0.112 |        0.036 |        0.682 | 1.059 |     24.9   | False  |
| bb_fade          | {"atr_sl": 2.5, "k": 2.0, "n": 20, "trend": 0}      | 607 |       0.089 |        0.031 |        0.653 | 1.066 |     15.705 | False  |
| rsi_extreme      | {"atr_sl": 2.5, "lo": 10, "n": 5, "trend": 0}       | 146 |       0.09  |        0.033 |        0.636 | 1.113 |      7.748 | False  |
| pdh_pdl_sweep    | {"buf": 0.3, "end_h": 22, "start_h": 10, "tp": 3.0} | 418 |       0.13  |        0.037 |        0.712 | 1.056 |     29.002 | False  |
| pdh_pdl_sweep    | {"buf": 0.3, "end_h": 18, "start_h": 10, "tp": 3.0} | 377 |       0.112 |        0.03  |        0.733 | 1.045 |     33.005 | False  |
| pdh_pdl_sweep    | {"buf": 0.3, "end_h": 22, "start_h": 8, "tp": 3.0}  | 465 |       0.122 |        0.014 |        0.886 | 1.021 |     41.599 | False  |
| keltner_reversal | {"buf": 0.5, "mult": 2.5, "n": 20, "trend": 0}      | 357 |       0.076 |        0.012 |        0.843 | 1.021 |     28.588 | False  |

## Fase 3 · Pass rate per modello di rischio (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.314 |  0.439 |  0.329 |  0.208 |  0.117 |
| dd_lineare               |  0.194 |  0.455 |  0.461 |  0.362 |  0.222 |
| dd_lineare+guardia+coast |  0.172 |  0.492 |  0.568 |  0.568 |  0.51  |
| dd_scaglioni             |  0.191 |  0.42  |  0.396 |  0.367 |  0.235 |
| guardia_giornaliera      |  0.246 |  0.541 |  0.553 |  0.52  |  0.454 |
| statico                  |  0.234 |  0.472 |  0.407 |  0.32  |  0.207 |
| streak_perdite           |  0.151 |  0.476 |  0.448 |  0.327 |  0.213 |

## Fase 3 · Fallimento per DAILY loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |      0 |  0.073 |  0.348 |  0.59  |  0.783 |
| dd_lineare               |      0 |  0.042 |  0.161 |  0.367 |  0.652 |
| dd_lineare+guardia+coast |      0 |  0     |  0     |  0     |  0.031 |
| dd_scaglioni             |      0 |  0.023 |  0.202 |  0.318 |  0.612 |
| guardia_giornaliera      |      0 |  0     |  0     |  0     |  0.052 |
| statico                  |      0 |  0.132 |  0.342 |  0.503 |  0.722 |
| streak_perdite           |      0 |  0     |  0.191 |  0.446 |  0.685 |

## Fase 3 · Fallimento per MAX loss (media)

| risk_family              |   0.5% |   1.0% |   1.5% |   2.0% |   3.0% |
|:-------------------------|-------:|-------:|-------:|-------:|-------:|
| anti_martingala          |  0.091 |  0.275 |  0.262 |  0.191 |  0.1   |
| dd_lineare               |  0.012 |  0.121 |  0.218 |  0.224 |  0.122 |
| dd_lineare+guardia+coast |  0.007 |  0.084 |  0.199 |  0.302 |  0.402 |
| dd_scaglioni             |  0.046 |  0.152 |  0.175 |  0.188 |  0.121 |
| guardia_giornaliera      |  0.088 |  0.283 |  0.389 |  0.447 |  0.466 |
| statico                  |  0.125 |  0.272 |  0.231 |  0.176 |  0.071 |
| streak_perdite           |  0.064 |  0.285 |  0.305 |  0.22  |  0.102 |

## Fase 3 · EV per tentativo (media, valuta conto)

| risk_family              |     0.5% |    1.0% |    1.5% |     2.0% |     3.0% |
|:-------------------------|---------:|--------:|--------:|---------:|---------:|
| anti_martingala          | 1466.29  | 3639.75 | 2508.34 |  601.051 | -501.569 |
| dd_lineare               |  462.222 | 3173.21 | 3700.64 | 2337.47  |  389.175 |
| dd_lineare+guardia+coast |  394.021 | 3859.54 | 6224.42 | 7529.76  | 7909.52  |
| dd_scaglioni             |  466.499 | 2881.23 | 2900.49 | 2545.82  |  720.154 |
| guardia_giornaliera      |  952.608 | 4877.71 | 6569.54 | 7222.65  | 7095.83  |
| statico                  |  819.596 | 3639.07 | 3413.86 | 1941.46  |  272.022 |
| streak_perdite           |  183.713 | 3415.94 | 3965.31 | 2000.81  |  371.465 |

## Fase 3 · EV dovuto al VANTAGGIO (EV meno lo stesso EV a vantaggio zero)

| risk_family              |     0.5% |    1.0% |    1.5% |     2.0% |     3.0% |
|:-------------------------|---------:|--------:|--------:|---------:|---------:|
| anti_martingala          | 1618.46  | 3235.16 | 2317.86 |  862.393 |   35.21  |
| dd_lineare               |  857.15  | 2973.29 | 3339.01 | 2178.01  |  621.897 |
| dd_lineare+guardia+coast |  777.401 | 3388.27 | 5003.03 | 5792.27  | 6263.64  |
| dd_scaglioni             |  863.304 | 2817.31 | 2725.94 | 2356.18  |  861.198 |
| guardia_giornaliera      | 1216.21  | 4023.2  | 4908    | 5029.19  | 5005.15  |
| statico                  | 1130.15  | 3155.64 | 2883.22 | 1650.13  |  454.145 |
| streak_perdite           |  591.482 | 3027.59 | 3405.03 | 1726.04  |  582.316 |

## Fase 3 · Migliori combinazioni prop (ordinate per ev_vs_zero)

| candidate                                                        | rules            | risk_profile                  |   pass_rate |   pass_zero |   fail_daily |   fail_max |   median_days |   ev_attempt |   ev_zero |   ev_vs_zero |
|:-----------------------------------------------------------------|:-----------------|:------------------------------|------------:|------------:|-------------:|-----------:|--------------:|-------------:|----------:|-------------:|
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.61  |       0.337 |            0 |      0.357 |          24   |     16508.7  |  3522.31  |     12986.4  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.653 |       0.33  |            0 |      0.277 |          30   |     15071.5  |  3019.03  |     12052.4  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.713 |       0.267 |            0 |      0.073 |          47   |     13244.2  |  1290.92  |     11953.3  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.683 |       0.303 |            0 |      0.167 |          39   |     12111.2  |  1646.44  |     10464.7  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | guardia_giornaliera|2.0%      |       0.717 |       0.243 |            0 |      0.127 |          67   |     11432.4  |  1168.58  |     10263.9  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | dd_lineare+guardia+coast|2.0% |       0.68  |       0.29  |            0 |      0.143 |          45.5 |     12033    |  1878.64  |     10154.4  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | dd_lineare+guardia+coast|2.0% |       0.677 |       0.33  |            0 |      0.23  |          39   |     12319.7  |  2276.61  |     10043.1  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | guardia_giornaliera|3.0%      |       0.63  |       0.317 |            0 |      0.217 |          37   |     12527.5  |  2517.74  |     10009.8  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |       0.557 |       0.39  |            0 |      0.443 |          19   |     15780.7  |  5871.24  |      9909.51 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | two_step_classic | dd_lineare+guardia+coast|3.0% |       0.653 |       0.357 |            0 |      0.307 |          26   |     11880.9  |  2250.27  |      9630.68 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | guardia_giornaliera|1.5%      |       0.673 |       0.32  |            0 |      0.263 |          56   |     11778.8  |  2259.34  |      9519.5  |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_tight   | dd_lineare+guardia+coast|3.0% |       0.66  |       0.283 |            0 |      0.127 |          40   |     10765.2  |  1324.75  |      9440.41 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|3.0%      |       0.613 |       0.36  |            0 |      0.333 |          30.5 |     12259.3  |  2931.47  |      9327.78 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | two_step_classic | dd_lineare+guardia+coast|2.0% |       0.67  |       0.223 |            0 |      0.013 |          69   |      9588.11 |   452.375 |      9135.73 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | two_step_classic | guardia_giornaliera|1.5%      |       0.643 |       0.347 |            0 |      0.34  |          45   |     11241.8  |  2145.94  |      9095.83 |

> Come si legge: decide il **verdetto** della conferma (intervallo OOS corretto per i candidati; il DSR e' diagnostica).
> `ev_vs_zero` toglie il valore d'opzione della challenge ma **non il caso**: su un candidato
> NON_DIMOSTRATA non dice niente. Per un candidato vero: `lab.prop.evaluate_ci`.

## Fase 4 · Conferma OOS

| candidate                                                        |   n_is |   exp_is |   n_oos |   exp_oos |   exp_oos_lo |   exp_oos_hi |   mde_oos |   pf_oos |   dd_oos_r |   dsr_is |   trials |   n_candidati | verdetto       |
|:-----------------------------------------------------------------|-------:|---------:|--------:|----------:|-------------:|-------------:|----------:|---------:|-----------:|---------:|---------:|--------------:|:---------------|
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} |    256 |    0.173 |     100 |     0.095 |       -0.187 |        0.377 |     0.361 |    1.216 |      8.507 |    0.288 |      204 |             8 | NON_DIMOSTRATA |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} |    325 |    0.18  |     133 |     0.096 |       -0.234 |        0.426 |     0.425 |    1.162 |     13.279 |    0.175 |      204 |             8 | NON_DIMOSTRATA |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} |    249 |    0.165 |      96 |     0.134 |       -0.202 |        0.471 |     0.431 |    1.269 |      7.648 |    0.135 |      204 |             8 | NON_DIMOSTRATA |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} |    320 |    0.192 |     129 |     0.12  |       -0.267 |        0.506 |     0.497 |    1.184 |     15.535 |    0.12  |      204 |             8 | NON_DIMOSTRATA |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           |    355 |    0.138 |     147 |     0.219 |       -0.073 |        0.512 |     0.377 |    1.435 |      7.927 |    0.108 |      204 |             8 | NON_DIMOSTRATA |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 30, "trend": 0}           |    460 |    0.079 |     195 |     0.238 |        0.019 |        0.457 |     0.283 |    1.566 |      6.533 |    0.042 |      204 |             8 | PROMOSSA       |
| zscore_revert|{"atr_sl": 2.0, "n": 50, "z": 2.0, "z_exit": 0.5}  |    462 |    0.078 |     210 |     0.128 |       -0.091 |        0.347 |     0.284 |    1.268 |      9.4   |    0.047 |      204 |             8 | NON_DIMOSTRATA |
| bb_fade|{"atr_sl": 1.5, "k": 2.0, "n": 30, "trend": 0}           |    637 |    0.061 |     265 |     0.281 |        0.018 |        0.544 |     0.341 |    1.492 |     10.574 |    0.013 |      204 |             8 | PROMOSSA       |

## Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)

| candidate                                                        | verdetto       | rules            | risk_profile                  |   pass_rate_is |   pass_rate |   pass_zero |   fail_daily |   fail_max |   ev_is |   ev_attempt |   ev_vs_zero_is |   ev_vs_zero |
|:-----------------------------------------------------------------|:---------------|:-----------------|:------------------------------|---------------:|------------:|------------:|-------------:|-----------:|--------:|-------------:|----------------:|-------------:|
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.61  |       0.413 |       0.257 |            0 |      0.543 | 16508.7 |      5412.77 |        12986.4  |      4054.14 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.653 |       0.367 |       0.233 |            0 |      0.553 | 15071.5 |      3672.47 |        12052.4  |      2929.78 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.713 |       0.503 |       0.263 |            0 |      0.2   | 13244.2 |      5199.52 |        11953.3  |      4284.06 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.683 |       0.547 |       0.227 |            0 |      0.203 | 12111.2 |      6575.06 |        10464.7  |      5675.34 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | guardia_giornaliera|2.0%      |          0.717 |       0.423 |       0.167 |            0 |      0.303 | 11432.4 |      3299.24 |        10263.9  |      3067.36 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|2.0% |          0.68  |       0.383 |       0.203 |            0 |      0.36  | 12033   |      3255.3  |        10154.4  |      2768.15 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|2.0% |          0.677 |       0.407 |       0.223 |            0 |      0.41  | 12319.7 |      3008.26 |        10043.1  |      2701.49 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | guardia_giornaliera|3.0%      |          0.63  |       0.58  |       0.33  |            0 |      0.333 | 12527.5 |      7518.28 |        10009.8  |      5850.23 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_classic | guardia_giornaliera|3.0%      |          0.557 |       0.463 |       0.343 |            0 |      0.537 | 15780.7 |      7210.25 |         9909.51 |      4321.46 |
| bb_fade|{"atr_sl": 2.5, "k": 2.0, "n": 50, "trend": 0}           | NON_DIMOSTRATA | two_step_classic | dd_lineare+guardia+coast|3.0% |          0.653 |       0.767 |       0.28  |            0 |      0.21  | 11880.9 |     22624.4  |         9630.68 |     20595.1  |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_classic | guardia_giornaliera|1.5%      |          0.673 |       0.437 |       0.24  |            0 |      0.443 | 11778.8 |      3604.85 |         9519.5  |      2919.18 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_tight   | dd_lineare+guardia+coast|3.0% |          0.66  |       0.463 |       0.263 |            0 |      0.32  | 10765.2 |      4338.19 |         9440.41 |      3542.81 |
| zscore_revert|{"atr_sl": 3.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_classic | guardia_giornaliera|3.0%      |          0.613 |       0.533 |       0.313 |            0 |      0.393 | 12259.3 |      7935.93 |         9327.78 |      6097.15 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.5} | NON_DIMOSTRATA | two_step_tight   | dd_lineare+guardia+coast|3.0% |          0.557 |       0.35  |       0.247 |            0 |      0.63  | 10906.5 |      2510.1  |         8700.48 |      1955.81 |
| zscore_revert|{"atr_sl": 2.0, "n": 100, "z": 2.0, "z_exit": 0.0} | NON_DIMOSTRATA | two_step_tight   | dd_lineare+guardia+coast|3.0% |          0.5   |       0.363 |       0.22  |            0 |      0.627 | 10978.7 |      4179.61 |         8531.76 |      3540.99 |
