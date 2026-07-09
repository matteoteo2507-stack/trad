# Stagionalità Turn-of-Month — Verdetto: NO-GO — 2026-07-08

> Terzo e **ultimo** edge sistematico del pivot. Test **pre-registrato**
> ([docs/SEASONALITY_PREREGISTRATION.md](../SEASONALITY_PREREGISTRATION.md)), motore
> [strategies/seasonality/backtest.py](../../strategies/seasonality/backtest.py). 16 asset D1 2003-2026.

## Esito
| test | valore | criterio | pass |
|---|---|---|---|
| strategia long-TOM/flat (tutte le 4 finestre) | Sharpe −0.28 … −0.44 | — | ❌ |
| **(TOM−nonTOM) vs giorni casuali** | +3.47 bps/g, **p=0.238** (null sd 4.76) | p<0.05 | ❌ |
| US500 / US100 (casa attesa) | **−1.0% / −2.6%** annuo | >0 | ❌ |
| BCa Sharpe | −0.28, CI[−0.69,+0.13] | lower>0 | ❌ |
| DSR (n_trials=4) | 0.008 | significant_95 | ❌ |
| MC-permutation | p=0.481 | — | ❌ |
| walk-forward | IS −0.38 → OOS −0.21 | — | ❌ |
| buy&hold (long sempre) | Sharpe **+0.40** > strategia | — | — |

**Verdetto: NO-GO.** La finestra di cambio-mese **non batte finestre di giorni casuali** (p=0.24);
l'effetto TOM classico è **assente/negativo sugli indici** nel 2003-2026 (decaduto, come molte anomalie
di calendario post-2000). I pochi "positivi" (ETH +118%/anno, XAU +16.7) sono **rumore da piccolo
campione** su asset ad alta volatilità, non effetto. Concentrare nel TOM **distrugge** rendimento vs
buy&hold. Nessun curve-fit: verdetto per p-value giorni-casuali + BCa + DSR.

## Conclusione (il patto)
Era l'ultimo colpo sistematico pulito. **È null.** → **Patto attivato con l'utente: si chiude la ricerca
di edge sistematici *own*.** Bilancio del pivot post-livelli:
- Livelli: null (384 trial). TSMOM: NO-GO (= beta, non alpha). Mean-reversion: NO-GO. Router momentum+MR:
  refutato (beta-trap). Stagionalità TOM: NO-GO.
- **Unico edge reale**: il **mentore** (discrezionale, manuale, dipendente da operatività esterna).
- Ciò che è robusto e automatizzabile su questo universo/epoca/accesso è **raccogliere beta** (long
  diversificato gestito a volatilità) → il **pilastro passivo**.

**Prossimo lavoro di più alto valore**: costruire bene il **pilastro passivo** ("strutturato e protetto"),
che era in sospeso in attesa degli input personali dell'utente ([[project_stock_selector_eval_2026_06]] /
[docs/INVESTING_PILLAR_PLAN.md](../INVESTING_PILLAR_PLAN.md)). Il reddito attivo resta il mentore manuale.
La macchina rigorosa (`core/quant_metrics` + backtester) resta pronta per opportunità future.

### Riproducibilità
`python strategies/seasonality/backtest.py`. Spec: [SEASONALITY_PREREGISTRATION.md](../SEASONALITY_PREREGISTRATION.md).
