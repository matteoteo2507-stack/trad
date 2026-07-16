# Opening-Range Breakout (US indici, M5) — Verdetto: NO-GO — 2026-07-16

> Primo test del filone **scalping single-asset intraday** (idea utente + socio). Pre-registrato
> ([docs/OPENING_RANGE_PREREGISTRATION.md](../OPENING_RANGE_PREREGISTRATION.md)), motore
> [analysis/opening_range/backtest.py](../../analysis/opening_range/backtest.py). Dati M5:
> broker (1.4y) + **Dukascopy 14.5y** (2012-2026, [export_dukascopy.py](../../analysis/opening_range/export_dukascopy.py)).

## La lezione del campione
- **Broker US100, 1.4 anni (2025-26)**: E[R] **+0.073R**, win 36.8%, entrambi i lati positivi → sembrava
  un debole edge (ma BCa CI includeva già lo 0, e US500 OOS era negativo).
- **Dukascopy, 14.5 anni (2012-2026)** — il vero test multi-regime:

| | NAS100 | SPX500 |
|---|---|---|
| trade | 2629 | 2637 |
| E[R] | **−0.056R** | **−0.137R** |
| win% (BE ~34%) | 33.9% | 33.3% |
| BCa CI95 E[R] | [−0.112, 0.000] | [−0.191, −0.083] |
| PF | 0.92 | 0.82 |

Per-anno NAS100: 2012-2020 quasi tutti **negativi**; positivi solo **2021 (+0.35)** e **2026-parziale
(+0.31)** = outlier di regime. Il +0.073 recente era **fortuna di regime** (bull low-vol 2025-26 + coda
2026). Esteso ai regimi 2018/2020/2022 e a SPX500 → **perde**. Entrambi i lati negativi (nessun rescue).

## Verdetto: NO-GO
La strategia opening-range breakout + retest, 1:2, come specificata, **non ha edge** su 14.5 anni e su
entrambi gli indici USA. Estendere lo storico (richiesta utente) ha **corretto un falso positivo** — è la
prova del valore del multi-regime. Feed-consistency: il segno si ribalta tra broker e Dukascopy su un anno
marginale (2025) = firma di edge **inesistente** (E[R]≈0 → domina il rumore di feed).

## Filtro news (v2) — TESTATO: non aiuta, peggiora
Escludendo NFP (primo venerdì, esatto) + giorni con gap di apertura >0.6% (proxy shock/CPI/FOMC,
look-ahead-safe): NAS100 −0.056 → −0.065 → **−0.070**; SPX500 −0.137 → −0.139 → **−0.154**. Togliere i
giorni-news/shock **peggiora** l'E[R] (i breakout hanno bisogno di volatilità; i giorni calmi = chop =
più falsi break). **Le news non stavano sporcando nulla** — la strategia perde anche nei giorni tranquilli.
Ipotesi "filtro news lo salva" **refutata**. (RR/expiry: cambiarli ora = parameter-mining su una base
negativa; farlo solo con grid pre-registrata + DSR/White's RC + holdout train/test + cross-index NAS↔SPX.)

## Bilancio filone scalping single-asset (1° test)
L'idea "meccaniche nascoste di un singolo asset" era ben posta (evento reale = apertura USA, poca
superficie di overfitting), ma **anch'essa null** una volta testata su tutti i regimi. Coerente col resto:
niente edge meccanico *own* robusto. Motore/dati riusabili (Dukascopy M5 14.5y di NAS100/SPX500 in
`data/`) per eventuali varianti pre-registrate future. Reddito = mentore manuale; ricchezza = passivo.

### Riproducibilità
`python analysis/opening_range/backtest.py NAS100` (e `SPX500`). Spec: [OPENING_RANGE_PREREGISTRATION.md](../OPENING_RANGE_PREREGISTRATION.md).
