# TSMOM multi-asset (canonico, di portafoglio) — Verdetto: NO-GO — 2026-07-08

> Primo edge del pivot post-livelli. Test **pre-registrato** ([docs/TSMOM_PREREGISTRATION.md](../TSMOM_PREREGISTRATION.md)),
> motore [strategies/tsmom/backtest.py](../../strategies/tsmom/backtest.py), metriche [core/quant_metrics.py](../../core/quant_metrics.py).
> Universo 16 asset D1 (2003-2026), spec canonica MOP (sign ritorno 252g, vol-target 60g, media di
> portafoglio, ribilanciamento mensile, costi per turnover, look-ahead-safe).

## Esito primario (lookback 252, mensile), dopo costi
| metrica | valore | criterio a priori | pass |
|---|---|---|---|
| Sharpe | +0.21 | — | — |
| **BCa CI Sharpe 95%** | **[−0.18, +0.59]** | lower > 0 | ❌ |
| **DSR** (n_trials=8) | dsr=0.33, SR 0.21 < thr 0.30 | significant_95 | ❌ |
| MC-permutation | p=0.51 | — | ❌ (rumore) |
| PBO/CSCV (8 varianti) | 0.58 | <0.5 | ❌ |
| White's RC (8 varianti) | best L126_D, p=0.53 | <0.05 | ❌ |
| Walk-forward (5y/1y anchored) | IS +0.23 → OOS +0.12 | — | degrado 51% |
| breadth | 12/16 asset Sharpe>0 | >50% | ✅ |
| concentrazione | top asset (USDJPY) 16% PnL | <50% | ✅ |
| anni positivi | 13/23 | maggioranza | ✅ |

**Verdetto (regola pre-registrata): NO-GO.** 3/5 criteri chiave falliti (i 5 test statistici concordano:
l'edge **non è distinguibile dal caso**). Overlay prop (scala 10% vol): maxDD −40%, peggior giorno −4.7%,
mesi positivi 52% → non prop-viable com'è.

## Lettura onesta
- **Il multi-asset ha corretto i difetti del NO-GO 2026-05-29** (mono-asset/mono-anno): qui breadth 12/16,
  top asset 16%, 13/23 anni positivi. Il problema **non** è più il campione o la concentrazione.
- Il problema è che **l'edge è semplicemente troppo debole** (Sharpe ~0.2) in questo universo/epoca —
  **esattamente l'aspettativa a priori** (decay post-2009, Baltas-Kosowski; universo USD-pesante senza
  bond/commodities). Coerente con SG Trend ~0.3-0.5 e anni negativi.

## Ipotesi (NON risultato — richiede nuova pre-registrazione)
Gli Sharpe standalone mostrano il trend **concentrato negli asset che trendano** (XAUUSD +1.44, US100
+1.19, US500 +1.13, BTCUSD +0.63) e **diluito dai cross FX** (USDCHF −0.27, EURGBP.r −0.69). Un TSMOM
su **indici+metalli+crypto** (niente cross FX) *potrebbe* essere più forte — **ma selezionare i vincitori
ora è post-hoc/p-hacking**. Va pre-registrato come **nuovo trial** e validato OOS, con la consapevolezza
che è un'ipotesi derivata dai dati (evidenza più debole di una fresca).

## Azione
Per il kill-switch pre-registrato: **archiviare TSMOM canonico** e passare al prossimo edge del backlog
ortogonale (**mean-reversion vol non-level**), **oppure** (scelta utente) pre-registrare la variante
"trending-universe" come nuovo trial prima di procedere. Dati/codice conservati e riproducibili.

### Riproducibilità
`python strategies/tsmom/backtest.py` (dalla root). Spec e criteri: [TSMOM_PREREGISTRATION.md](../TSMOM_PREREGISTRATION.md).
