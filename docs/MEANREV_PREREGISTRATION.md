# Mean-reversion vol (non-level) — PRE-REGISTRAZIONE (anti-p-hacking)

> **Committata PRIMA dei risultati.** 2026-07-08. Secondo edge del pivot (dopo TSMOM NO-GO). Contratto:
> spec, universo, varianti, metrica, criteri e kill-switch fissati qui *a priori*; dopo i numeri non si
> cambiano; ogni variante extra = nuovo trial nel DSR. Riusa `core/quant_metrics.py` e la struttura di
> `strategies/tsmom/backtest.py`.

## Domanda (una sola)
Un edge di **mean-reversion di breve termine basato sulla volatilità** (z-score del prezzo, **NON**
livelli) — comprare l'oversold / vendere l'overbought e puntare al ritorno alla media — produce un edge
risk-adjusted **reale dopo costi e out-of-sample** sul nostro universo, robusto alla molteplicità? È
concettualmente **ortogonale** al momentum (orizzonti opposti) e diverso da ciò che abbiamo falsificato
(i livelli): qui lo "stiramento" è misurato in **unità di volatilità**, non su una linea di prezzo.

## Contesto onesto (aspettative a priori)
Letteratura: reversione di breve documentata (Lo-MacKinlay 1999, Conrad-Kaul 1998) ma **decadimento
post-2015** su FX intraday; win-rate storicamente alto (~60%) ma **coda sinistra** (si shorta la forza).
Ipotesi naturale (dal risultato TSMOM): la reversione dovrebbe funzionare **dove il momentum perde** (i
cross FX che nel test TSMOM avevano Sharpe negativo) e **fallire sugli asset che trendano** (oro, indici,
crypto). Lo testiamo su **tutti i 16** (breadth) senza pre-selezionare, e vediamo.

## Universo (16 asset, D1) — feed demo4 validato
Stesso di TSMOM: EURUSD GBPUSD USDJPY AUDUSD USDCAD NZDUSD USDCHF EURJPY.r GBPJPY.r EURGBP.r · XAUUSD
XAGUSD · BTCUSD ETHUSD · US500 US100. Dati `analysis/trading-bot-eval/data/{PREFIX}_D1.csv`.

## Spec canonica (fissa)
- **z-score**: `z_t = (close_t − SMA(close,N)_t) / STD(close,N)_t`, calcolato con dati **≤ t**.
- **Entry** (da flat): `z_t ≤ −Z_ENTRY` → **LONG**; `z_t ≥ +Z_ENTRY` → **SHORT** (contro-stiramento).
- **Exit**: ritorno alla media (`z` torna a 0, cioè cambia segno rispetto all'entry) **oppure**
  **time-stop** a `MAX_HOLD` giorni **oppure** **vol-stop** se lo stiramento peggiora a `|z| ≥ Z_STOP`.
- **Sizing**: quando in posizione, `peso = side · (σ_target / σ_i,t)` (vol-target 60g, σ_target=10%),
  identico a TSMOM. Fuori posizione = flat (0). Media di portafoglio sugli asset attivi.
- **Look-ahead-safe**: `z`/vol da dati ≤ t; la posizione stabilita a close t guadagna il ritorno t+1.
- **Costi**: per turnover (entry/exit), stessi bps a priori di TSMOM (FX 2, XAU/XAG 4, indici 3, crypto 8).
- **Primario**: `N=10, Z_ENTRY=1.0, Z_STOP=3.0, MAX_HOLD=10` giorni.

## Varianti pre-registrate (per DSR/PBO/White) — "numero di trial"
`N ∈ {5, 10, 20}` × `Z_ENTRY ∈ {1.0, 2.0}` = **6 varianti**. Primario = **(N=10, Z_ENTRY=1.0)**.
`n_trials = 6` per il DSR. (Z_STOP e MAX_HOLD fissi; loro sensibilità = robustezza a parte.)

## Metriche, validazione, regola di decisione — IDENTICHE a TSMOM
Via `core/quant_metrics.py`: Sharpe/Sortino/CAGR/maxDD/Calmar, **breadth** (asset con contributo>0) +
concentrazione, **BCa CI** sullo Sharpe, **DSR** (n_trials=6), **PBO/CSCV** sulla matrice T×6,
**walk-forward** (anchored 5y/1y), **MC-permutation**, **White's RC** sulle 6 varianti; overlay prop
(vol 10%, DD giornaliero/totale, giorni). Per-anno (mono-anno?).

**GO** se il primario (N10,Z1) dopo costi soddisfa TUTTE: (1) BCa Sharpe lower>0; (2) DSR significant_95;
(3) breadth>50% e top asset<50% del PnL; (4) maggioranza anni positivi; (5) White's RC p<0.05.
**KILL-SWITCH (NO-GO)** se mono-asset/mono-anno, o DSR n.s., o BCa lower≤0, o breadth<50% → si archivia
e si passa al prossimo edge del backlog (**stagionalità/calendario**, poi carry).

## Impegni anti-overfitting (vincolanti)
Come TSMOM: varianti/costi/spec fissati qui; nessun tuning per-asset; serie di rendimenti; look-ahead-safe;
DSR/PBO/White sul vero numero di varianti; verdetto per BCa+DSR+breadth (mai best-asset); forward per il
sopravvissuto. **Attenzione coda**: la reversione ha rischio-coda (shortare la forza) → il vol-stop e il
time-stop sono il controllo; se l'edge dipende dal togliere lo stop, è fragile.
