# Mean-reversion vol (non-level, di portafoglio) — Verdetto: NO-GO — 2026-07-08

> Secondo edge del pivot. Test **pre-registrato** ([docs/MEANREV_PREREGISTRATION.md](../MEANREV_PREREGISTRATION.md)),
> motore [strategies/meanrev/backtest.py](../../strategies/meanrev/backtest.py) (riusa data/sizing/validazione
> di TSMOM). Universo 16 asset D1 2003-2026, z-score N=10 Z_ENTRY=1.0, exit media/time-stop/vol-stop.

## Esito primario (dopo costi)
| metrica | valore | criterio | pass |
|---|---|---|---|
| Sharpe | **−0.21** | — | — |
| BCa CI Sharpe | [−0.63, +0.21] | lower>0 | ❌ |
| DSR (n_trials=6) | dsr=0.011 | significant_95 | ❌ |
| MC-permutation | p=0.498 | — | ❌ |
| PBO/CSCV | 0.796 | <0.5 | ❌ |
| White's RC | best N10_Z1.0, p=0.937 | <0.05 | ❌ |
| walk-forward | IS −0.30 → OOS −0.02 | — | — |
| breadth | 9/16 Sharpe>0 | >50% | ✅ |
| anni positivi | 8/24 | maggioranza | ❌ |

**Verdetto: NO-GO.** La mean-reversion di breve, applicata a **tutto** l'universo, è negativa (tutte le 5
varianti con trade ≤ 0). Coerente col decadimento documentato (Lo-MacKinlay/Conrad-Kaul, decay post-2015).

## La rivelazione: complementarità momentum ⟂ reversione (per natura dell'asset)
Sharpe standalone MR (in-sample): **positivo sui RANGER** — EURGBP.r +0.56, USDCAD +0.32, AUDUSD +0.17,
EURJPY.r/NZDUSD/USDCHF/EURUSD >0, US100/US500 leggermente >0 — **negativo sui TRENDER** — XAUUSD −0.76,
BTCUSD −0.38, GBPUSD −0.37, ETHUSD −0.34, XAGUSD −0.24. È lo **specchio esatto di TSMOM** (XAU +1.44,
US100 +1.19, US500 +1.13, BTC +0.63 positivi; cross FX negativi). I due edge, **deboli da soli**, sono
**anti-correlati per carattere dell'asset**: alcuni asset trendano, altri tornano alla media.

## Ipotesi (da PRE-REGISTRARE, non rivendicare)
Un **sistema combinato momentum+reversione** — o un **router** che, con una misura di "trendiness"
*look-ahead-safe* (es. efficiency ratio / Hurst / autocorrelazione su dati passati), instrada ogni asset
al momentum se trenda e alla reversione se torna alla media — potrebbe unire due edge deboli in uno
positivo. **Rischio p-hacking**: la classificazione NON deve usare gli Sharpe in-sample; va definita a
priori e validata OOS (walk-forward + DSR). È la materializzazione della tesi "portafoglio ortogonale".

## Azione
Kill-switch pre-registrato: **archiviare MR standalone**. Bivio: (a) pre-registrare il **combinato
momentum+reversione / router trendiness** (lead più forte, thesis-aligned) oppure (b) il prossimo edge
del backlog (**stagionalità/calendario**). Scelta utente. Macchina e dati riusabili.

### Riproducibilità
`python strategies/meanrev/backtest.py`. Spec: [MEANREV_PREREGISTRATION.md](../MEANREV_PREREGISTRATION.md).
