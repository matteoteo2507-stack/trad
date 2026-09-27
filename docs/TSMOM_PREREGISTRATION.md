---
tipo: preregistrazione
stato: NO-GO
aggiornato: 2026-09-18
decisione: "DECISIONS 2026-09-18 (5) — audit A5"
metrica_corrente: "Sharpe +0,21 [−0,18; +0,59]; MDE Sharpe 0,59"
nota: "Audit A5: NON MISURATO (potenza insufficiente). Resta chiuso ma non vale come prova di assenza di edge."
---
# TSMOM multi-asset — PRE-REGISTRAZIONE (anti-p-hacking)

> **Committata PRIMA di guardare i risultati.** 2026-07-08. Primo edge del pivot post-livelli
> (384 trial null, [DECISIONS.md](../DECISIONS.md)). Contratto: spec, universo, varianti, metrica,
> **criteri di successo e kill-switch** sono fissati qui *a priori*. Dopo i numeri non si cambiano;
> un bug si documenta come *fix*, non come nuova definizione; ogni variante extra = nuovo trial nel DSR.
> Attua il piano `~/.claude/plans/…`. Riusa `core/quant_metrics.py`.

## Domanda (una sola)
Un programma **time-series momentum canonico, multi-asset, vol-targeted** produce un edge
risk-adjusted **reale dopo i costi e out-of-sample** sul nostro universo, **robusto alla molteplicità
dei lookback** — oppure è (come avverte la letteratura per il 2020-2026) troppo debole / mono-asset /
mono-anno per essere avviato? Misuriamo per **falsificare bene**, non per innamorarci.

## Contesto onesto (aspettative a priori)
Letteratura: TSMOM forte 1985-2009, **decade dopo il 2009** (Baltas-Kosowski); l'edge vive in un
**portafoglio ampio a bassa correlazione** (commodities+bond+indici+FX globali). Il nostro universo è
**USD-pesante e senza bond/commodities** → sub-ottimale. Aspettativa realistica: **Sharpe di programma
~0.3-0.5 con anni negativi**. Il precedente NO-GO (2026-05-29) era *dati insufficienti* (38 trade, 1
asset): qui lo rifacciamo **multi-asset sulle serie di rendimenti** (non sulle sintesi MT5).

## Universo (16 asset, D1) — feed demo4 validato
EURUSD GBPUSD USDJPY AUDUSD USDCAD NZDUSD USDCHF EURJPY.r GBPJPY.r EURGBP.r · XAUUSD XAGUSD ·
BTCUSD ETHUSD · US500 US100. Dati: `analysis/trading-bot-eval/data/{PREFIX}_D1.csv`.
**Limite dichiarato**: correlazioni alte (molte gambe USD, 2 indici USA, 2 metalli, 2 crypto);
espansione a bond/commodities/indici regionali solo se il concetto mostra vita.

## Spec canonica (fissa)
- **Rendimenti**: daily close-to-close (aritmetici) per asset.
- **Segnale**: a ogni ribilanciamento t, posizione = **sign del ritorno trailing 252 giorni** (12 mesi)
  usando dati **≤ t-1** (look-ahead-safe). Long se >0, short se <0.
- **Sizing (vol-target)**: peso_i,t = sign_i,t · (σ_target / σ_i,t), con **σ_i,t = vol annualizzata dei
  rendimenti daily su 60g trailing** (≤ t-1); σ_target = 10%/asset. Portafoglio = **media** dei
  contributi per-asset (ogni asset a pari rischio). Per l'overlay prop la serie di portafoglio è scalata
  a **vol target 10% annuo** con scaler **espanso** (no look-ahead). Lo Sharpe è invariante di scala.
- **Ribilanciamento**: **mensile** (primo giorno di trading) = primario; **giornaliero** = robustezza.
- **Costi** (per turnover, sul cambio di posizione, bps di nozionale, a priori):
  FX major/cross **2 bps**, XAU/XAG **4 bps**, US500/US100 **3 bps**, BTC/ETH **8 bps**.
- **Niente SL discrezionale** (il vol-target È il controllo del rischio). Robustezza: variante con
  stop 3·ATR(20) riportata a parte.

## Varianti pre-registrate (per DSR/PBO/White) — il "numero di trial"
Lookback **{21, 63, 126, 252}** × ribilanciamento **{mensile, giornaliero}** = **8 varianti**.
Primario = **(252, mensile)**. Stop on/off riportato come robustezza (non entra nel conteggio primario).
`n_trials = 8` per il DSR.

## Metriche e validazione (a priori, via `core/quant_metrics.py`)
- Portafoglio: **Sharpe** (ann.), Sortino, CAGR, **maxDD**, Calmar, % anni positivi.
- **Breadth**: quanti asset hanno contributo standalone positivo; concentrazione (top asset % del PnL).
- **BCa bootstrap CI** sullo Sharpe (`bca_bootstrap_ci`) → **lower bound**.
- **DSR** (`deflated_sharpe_ratio`, n_trials=8) → `significant_95`.
- **PBO/CSCV** (`pbo_cscv`) sulla matrice T×8 delle varianti.
- **Walk-forward** (`walk_forward`, anchored, train ~5y / test ~1y) → Sharpe OOS.
- **MC-permutation** (`mc_permutation_test`, block bootstrap) → p-value.
- **White's Reality Check** (`whites_reality_check`) sulle 8 varianti → controlla "ho provato 8 lookback".

## Regola di decisione (scritta prima dei numeri)
**GO** se il **primario (252, mensile)**, dopo costi, soddisfa **tutte**:
1. BCa CI Sharpe con **lower bound > 0**;
2. **DSR significant_95** (n_trials=8);
3. **breadth > 50%** asset con contributo positivo **e** top asset **< 50%** del PnL (no mono-asset);
4. **positivo nella maggioranza degli anni** (no mono-anno);
5. White's RC p < 0.05 sulle varianti.
Uno Sharpe modesto (~0.3-0.5) **conta** se supera 1-5.

**KILL-SWITCH (NO-GO)** se: mono-asset o mono-anno, **oppure** DSR n.s., **oppure** BCa lower ≤ 0,
**oppure** breadth < 50%. → si archivia TSMOM (come il precedente) e si passa al **prossimo edge del
backlog ortogonale** (mean-reversion vol → stagionalità → carry), senza forzare.

## Overlay prop-like (risponde a "demo a regole severe")
Con portafoglio a vol 10% annuo: riporta **max perdita giornaliera**, **max DD totale**, DD più lungo,
% mesi positivi, giorni di trading/mese → valuta la sopravvivenza a regole prop tipiche (es. 5%
daily / 10% total DD, min-days, consistency). Non si curve-fitta ai limiti (walk-forward + forward).

## Impegni anti-overfitting (vincolanti)
1. Varianti/costi/lookback fissati qui; nessun tuning per-asset. 2. Serie di **rendimenti** (non sintesi).
3. Look-ahead-safe (segnale/vol ≤ t-1). 4. DSR/PBO/White sul **vero** numero di varianti. 5. Verdetto per
BCa lower-bound + DSR + breadth, mai sul best-asset. 6. Forward per il sopravvissuto prima di demo/prop.
