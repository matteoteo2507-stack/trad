# Forex Gump — esito del test pre-registrato (2026-10-02)

Pre-registrazione: `docs/FOREXGUMP_LATENCY_PREREGISTRATION.md`. Esecuzione unica; holdout = 100% del campione.

## 1. Kill sui dati

- senza prezzi: 0.0% (kill > 10%)
- SKIP per spread reale >= SL: 0.9% (kill > 10%)
- non eseguiti (fill oltre 60 s da t+L): 0.1%
- fill da tick: 100.0%, da M1: 0.0%

## 2. Primario (L = 10 s)

| misura | n | media | CI 95% a cluster per giornata | MDE osservato |
|---|---|---|---|---|
| d (pessimistica) | 1774 | -0.007 | [-0.082; +0.069] | 0.109 |
| E[R] lato mentore (pessimistica) | 1774 | -0.342 | [-0.431; -0.248] | 0.132 |
| E[R] lato mentore (STRESS) | 1774 | -0.636 | [-0.713; -0.555] | 0.114 |
| d (ottimistica, solo accanto) | 1774 | -0.006 | [-0.080; +0.069] | 0.108 |

SKIP sotto stress: 0.9% (deciso sullo spread reale: stesso campione)
Quota di trade che attraversano il rollover delle 22 UTC: 3.8%

## 3. Diagnostica Step 3bis

- prezzo postato gia' superato in senso sfavorevole a t+L (sui trade eseguiti): 99.6%
- E[R] al prezzo postato (**NON OTTENIBILE**, solo per il costo del ritardo), sugli stessi 1774 segnali: +0.896
- costo del ritardo = E[R] postato - E[R] ottenibile, stessi segnali: +1.238R

## 4. Verdetto meccanico (§6)

**NON DIMOSTRATO (MDE 0.130R)**

MDE pre-registrato (vale per l'etichetta): 0.130R; MDE dall'errore osservato: 0.109R

## 5. Controlli

| lato | n | E[R] mentore | d |
|---|---|---|---|
| buy | 802 | -0.338 | +0.015 |
| sell | 972 | -0.345 | -0.025 |

| misura | n | media | CI 95% a cluster | MDE |
|---|---|---|---|---|
| E[R] lato mentore rifatto su sole M1 | 1774 | -0.298 | [-0.388; -0.202] | 0.133 |
| E[R] stesso lato a istante casuale (3 controlli, M1) | 5352 | -0.264 | [-0.328; -0.196] | 0.095 |
| divario mentore - controlli (M1 contro M1) | 1774 | -0.040 | [-0.148; +0.075] | 0.158 |
| E[R] lato mentore su tick (solo accanto) | 1774 | -0.342 | [-0.431; -0.248] | 0.132 |

```
MATCHING DEL BASELINE: a posto, CON RISERVA su hold
  [ok] n_events     1774 eventi, 5308 controlli, mediana 3.0 per evento
  [ok] side         coincide su tutte le coppie
  [ok] risk         scarto relativo max 0.00e+00 (tol 2%)
  [riserva] hold         ESITO, non matchabile: mediana reale 0.17 vs random 0.23 (+40%) <-- CONFONDATO, va dichiarato
```

Holding mediano (h), M1: mentore 0.17, lato opposto 0.15, controlli 0.23

## 6. Descrittive (0 trial, nessun verdetto)

**Latenza**

| L (s) | n | E[R] | d |
|---|---|---|---|
| 0 | 1769 | -0.290 | +0.026 |
| 5 | 1770 | -0.303 | +0.018 |
| 10 | 1774 | -0.342 | -0.007 |
| 30 | 1772 | -0.342 | -0.015 |
| 60 | 1772 | -0.386 | -0.025 |
| 300 | 1783 | -0.378 | -0.011 |

**Esecuzioni alternative (solo lato del mentore)**

| variante | eseguiti | E[R] |
|---|---|---|
| live | 1791 di 1792 | -0.156 |
| limit | 984 di 1792 | -0.368 |
| skip1 | 411 di 1792 | -0.279 |
| meta' spread | 1774 | -0.193 |

**Per anno, categoria, finestra post-cutoff**

| gruppo | n | E[R] | d |
|---|---|---|---|
| anno 2020 | 1 | -1.006 | -0.917 |
| anno 2021 | 234 | -0.230 | -0.043 |
| anno 2022 | 279 | -0.580 | -0.246 |
| anno 2023 | 254 | -0.225 | -0.050 |
| anno 2024 | 339 | -0.195 | +0.161 |
| anno 2025 | 459 | -0.494 | -0.006 |
| anno 2026 | 208 | -0.192 | +0.137 |
| hedging | 939 | -0.408 | -0.022 |
| just_for_fun | 840 | -0.328 | -0.007 |
| appesantimento | 58 | -0.064 | +0.009 |
| last | 118 | -0.621 | -0.180 |
| didattica | 384 | -0.338 | +0.083 |
| bonus | 13 | -0.412 | +0.161 |
| 06-09/2026 (post-cutoff) | 78 | -0.041 | +0.122 |

**Spiegazione noiosa** (momentum a 15 minuti): d medio -0.033 su 1693 (esclusi: movimento nullo 0, barre vecchie dopo una pausa 81); d_mentore - d_momentum +0.017 [-0.121; +0.154] — il mentore aggiunge informazione al momentum solo se il limite inferiore e' > 0

