# Quant Review — London Breakout (GBPUSD M15) — 2026-05-29

Reviewer: Quant Reviewer ([agents/quant_reviewer.md](../../agents/quant_reviewer.md)) ·
Protocollo: [docs/QUANT_REVIEW_PROTOCOL.md](../QUANT_REVIEW_PROTOCOL.md) ·
Motore metriche: [core/quant_metrics.py](../../core/quant_metrics.py) ·
Codice: [mql5/london_breakout.mq5](../../mql5/london_breakout.mq5)

> **Stance:** adversariale. L'onere della prova è sulla strategia. In ogni ambiguità ho scelto il verdict più conservativo.

---

## ⚠️ Avviso sui dati (precede ogni conclusione)

Il task chiedeva 3 varianti (A=`FIXED_RR`, B=`PARTIAL_TRAIL`, C=`FULL_TRAIL`) identiche tranne `InpExitMode`. **I dati per B e C non esistono.** Verificato a livello di deal:

| File | Periodo | `InpExitMode` (settings) | Trade | Net | Identità |
|---|---|---|---|---|---|
| [ReportTester-129-05.xlsx](../../backtest_results/london_breakout/ReportTester-129-05.xlsx) | 2020.01.01–2026.05.09 | **0** | 686 | −551.68 | Variante **A** full period |
| ~~ReportTester-partial trail.xlsx~~ (rimosso) | 2020.01.01–2026.05.09 | **0** | 686 | −551.68 | **Duplicato deal-per-deal di A** (max \|ΔP&L\|=0.000000 su 686 trade, 686/686 open-time identici) — non è una run PARTIAL_TRAIL |
| [ReportTester-FixedRR.xlsx](../../backtest_results/london_breakout/ReportTester-FixedRR.xlsx) | 2025.01.01–2026.05.09 | 0 (build EA precedente) | 139 | +413.13 | Variante **A**, sotto-finestra recente |

Conseguenze metodologiche (vincolanti):
- **Nessun confronto di famiglia A/B/C.** La PBO sulle 3 colonne di exit-mode e il White's Reality Check sul multiple-testing exit-mode **non sono calcolabili** → `INSUFFICIENT DATA` (protocollo Step 3: «senza varianti non puoi calcolare PBO»).
- Tutto ciò che segue valuta **solo la variante A (FIXED_RR)**. Dove servivano ≥2 configurazioni per PBO/WRC ho usato una **decomposizione long/short/both** della stessa strategia come *sostituto dichiarato*, non come surrogato dell'esperimento exit-mode.
- Le run B e C vanno prodotte su MT5 prima di qualunque verdict sulla famiglia.

---

## Sommario in 5 righe

Breakout meccanico del range della sessione asiatica (00:00–07:00 UTC): alle 07:00 piazza due stop OCO a `high±buffer·ATR_D1` / `low∓buffer·ATR_D1`, SL al lato opposto del range, TP fisso a 1.5R (variante A). Finestra di entry fino alle 10:00 UTC, time-stop forzato alle 16:00 UTC (strategia **intraday pura**, nessun overnight). Filtri: skip se range Asia ≥ 1.5·ATR_D1, skip primo venerdì del mese (NFP) e date FOMC. Sizing fixed-fractional 1% equity sul rischio di range. Famiglia di edge nota: Osler (AER 2003), Kathy Lien (2016) → soggetta a decadimento post-pubblicazione (McLean-Pontiff JF 2016).

## Gradi di libertà (Step 2)

| Gruppo | Parametri | Tipo |
|---|---|---|
| Soglie edge | `InpBreakoutBufferAtr`, `InpTpRMultiple`, `InpMaxRangeToAtrRatio`, `InpAtrPeriod` | 4 tunable |
| Exit family | `InpExitMode`, `InpPartialAtR`, `InpPartialFraction`, `InpTrailAtrPeriod`, `InpTrailAtrMult` | 5 tunable (inattivi in A, ma parte dello spazio di ricerca) |
| Sessioni | Asia start/end, entry-cutoff, time-stop | 4 finestre, **a priori** (00/07/10/16 UTC) |
| Filtri eventi | `InpSkipNfp`, `InpFomcBlackoutDatesCsv` | 2, a priori macro |
| Sizing | `InpRiskPerTradePct` | 1, rischio (non edge) |

- **N_params (tunable)** ≈ **16**; di cui **~0 calibrati su questo dataset** (le note dichiarano «tutti default, nessuna ottimizzazione»), **4 a priori** (sessioni).
- **N_trial DSR** = 100 × N_params = **1600** (raccomandazione Bailey-LdP 2014 in assenza di documentazione). Sensibilità riportata anche a 10⁴ e 10¹⁰ (persona: >10 DoF → N=10¹⁰).
- Nessun look-ahead nella *price action* (ordini stop su barre Asia chiuse). **Ma** vedi §Top rischi #1 per il look-ahead nel *filtro di regime* proposto.

---

## Verdict

| Oggetto | Verdict | Motivazione |
|---|---|---|
| **A `FIXED_RR`, incondizionata (always-on)** | **NO-GO** | 6.3 anni / 686 trade: Net **−551.68**, PF **0.979**, Sharpe daily **−0.096**, MC permutation **p=0.51** (il null non è nemmeno rifiutabile). Sistema senza edge come strumento sempre-attivo. |
| **A regime-gated (tesi "accendi su Volatile")** | **NO-GO / tesi respinta come formulata** | L'edge per-regime è in larga parte **artefatto di look-ahead**: con label di regime ritardata di 1 giorno (l'unica disponibile alle 07:00) Volatile crolla da +1828 a **+349 (PF 1.04)** e Sideways-Volatile da +909 a **−155 (PF 0.97)**. Netto del costo −1 pip, anche il Volatile onesto va in negativo. |
| **B `PARTIAL_TRAIL`, C `FULL_TRAIL`** | **INSUFFICIENT DATA** | Backtest inesistenti. Da produrre. |
| **Famiglia A/B/C** | **INSUFFICIENT DATA** | Niente confronto, niente PBO exit-mode, niente WRC. |

**Cap massimo possibile = RAFFINA** (protocollo: nessun trade live → live evidence insufficiente). Il cap non viene raggiunto: la variante A *as-is* è **NO-GO**, e il percorso verso RAFFINA è subordinato a correzioni metodologiche pesanti (vedi §Test mancanti).

---

## Edge probability (variante A, full period 2020-01-07 → 2026-05-08, 686 trade)

Returns: P&L per-trade aggregati in **rendimenti giornalieri** (Σ P&L del giorno / equity iniziale 10 000), allineati su 1654 business-day (685 giorni con trade). `periods_per_year=252`.

- **PBO exit-mode (A/B/C)** = **N/A — INSUFFICIENT DATA** (B, C assenti).
  - *Sostituto dichiarato* — PBO su decomposizione long/short/both (s=16, 12 870 combinazioni): **PBO = 0.470** → ~50%, **indistinguibile dal random** (Bailey-Borwein-LdP-Zhu 2017: >0.50 = random, 0.30–0.50 = forte overfitting). Nessuna sotto-configurazione direzionale sopravvive OOS.
- **DSR** = **0.0001** (n_trials=1600) — **NON** significativo al 95%. Robusto al variare di N: 0.0000 a 10⁴ e 10¹⁰. Sharpe osservato (−0.096) sotto la soglia di molteplicità (sr_thr=1.32). Skew +0.54, excess-kurt 1.33.
- **Walk-forward** (rolling 126/63, 24 fold): IS_mean **−0.158**, OOS_mean **−0.193**. IS già negativo → il «degrado» non è interpretabile (non c'è edge IS da degradare). Anchored identico (OOS −0.193). 9 fold OOS su 24 positivi.
- **MC permutation** (2000 perm, block=5): Sharpe_obs −0.096, **p=0.51**. La performance è esattamente a metà della distribuzione null.
- **Risk metrics**: Sortino **−0.067** · Max DD (daily) **−20.2%** · Calmar **−0.060** · CVaR95 **−1.01%/giorno** · CVaR99 **−1.09%**.
- *Riferimento MT5 (per-trade)*: Sharpe MT5 −0.304, PF 0.9786 — coerente coi miei numeri (segno e ordine di grandezza).

### Sotto-finestra recente 2025–2026 (139 trade, variante A)
Net +413.13, PF 1.0824, Sharpe daily **+0.33**, MaxDD −9.7%, **MC p=0.37**, **DSR=0.001**. Positiva ma **non significativa** e **non OOS indipendente** (è la coda del campione 2020–2026, non un hold-out). Coerente con un edge marginale che vive solo in certi sotto-periodi.

---

## Robustezza per-regime (il cuore della tesi — e dove cade)

Join dei 686 trade col regime ([data/regime_timeline_gbpusd.csv](../../data/regime_timeline_gbpusd.csv)) per data di apertura (650 match; 36 trade Gen–Mar 2020 precedono l'inizio della timeline).

**Con label same-day (look-ahead — NON disponibile live alle 07:00):**

| Bucket | n | Net | PF | Win% | Sharpe daily |
|---|---|---|---|---|---|
| Volatile | 263 | +1828.27 | 1.210 | 53.6 | +0.53 |
| Quiet | 387 | −2432.67 | 0.841 | 44.2 | −0.59 |
| Bull Volatile | 47 | +938.99 | 1.795 | 66.0 | — |
| Sideways Volatile | 149 | +909.37 | 1.177 | 52.3 | — |
| Bull Quiet | 51 | −1062.82 | 0.549 | 35.3 | — |
| Sideways Quiet | 292 | −1061.26 | 0.905 | 45.9 | — |
| Bear Quiet / Bear Volatile | 44 / 67 | −308.59 / −20.09 | 0.83 / 0.99 | — | — |

Questo riproduce il finding accertato (Volatile profittevole, Quiet in perdita) **ma è viziato da look-ahead**: il regime del giorno D è calcolato su close/ATR/ADX di D, ignoti alle 07:00 UTC quando si piazzano gli ordini.

**Con label prior-day (ritardo 1 giorno — onesta, no look-ahead):**

| Bucket | n | Net | PF | Δ vs same-day |
|---|---|---|---|---|
| Volatile | 266 | **+349.50** | **1.038** | −1479 |
| Quiet | 384 | −953.90 | 0.936 | +1479 |
| Sideways Volatile | 151 | **−155.24** | **0.972** | −1065 (cambia segno) |

**Conclusione regime:** ~80% del "+1828" su Volatile e l'intero "+909" su Sideways-Volatile sono **peeking sul classificatore di regime**, non edge della strategia. Tolto il peek, il Volatile è breakeven (+349, PF 1.04) e — applicando il costo −1 pip a 266 trade (≈ −$657) — diventa **netto negativo (~−310)**. La tesi «riattiva Sideways Volatile perché è in attivo» **si fonda su numeri look-ahead** e va respinta finché non rivalidata con label ritardata.

### Regola di `activation` attuale
Buckets per colonna `activation` (label same-day): `active` 406 → −142 (PF 0.99); `disabled` 149 → +909 (PF 1.18, = Sideways Volatile); `half` 95 → −1371 (PF 0.67). Sì, **la regola disabilita il bucket apparentemente migliore e dimezza un bucket peggiore** — *ma solo nei numeri look-ahead*. Con label onesta il "disabled" è −155: la regola non è palesemente sbagliata. **Non modificare l'activation rule sulla base di questi dati.**

---

## Costi reali (Step 5)

Report MT5: **Commissioni = 0**, **Swap = 0** su tutti i deal.
- **Swap = 0 è corretto**: strategia intraday, time-stop 16:00 UTC, hold max 8h56m → nessuna posizione overnight.
- **Spread**: incluso implicitamente nei fill (99% real ticks, entry/exit a bid/ask).
- **Commissioni / slippage su stop-order**: **non modellati**. Su breakout violenti gli stop subiscono 2–5× spread di slippage (persona §3). Haircut conservativo applicato: **−1 pip/trade** (≈ $10·lots; lot medio 0.247 → $2.47/trade, totale **−$1693** su 686 trade):

| | Net | PF | Sharpe daily | MaxDD |
|---|---|---|---|---|
| Pre-costo | −551.68 | 0.979 | −0.096 | −20.2% |
| **Post-costo (−1 pip)** | **−2244.88** | **0.916** | **−0.389** | −30.8% |
| Post-costo, Volatile (same-day) | +1227.97 | 1.137 | — | — |
| Post-costo, Sideways-Vol (same-day) | +548.07 | 1.103 | — | — |

Anche i bucket "vincenti" same-day si erodono; combinati col no-look-ahead (sopra) spariscono. −1 pip è l'estremo *ottimistico*: 2× spread su stop sarebbe più realistico.

---

## Top 3 rischi

1. **Look-ahead nel filtro di regime** — il driver #1 del falso edge. Il label di regime di D usa dati di chiusura di D non disponibili alle 07:00 UTC; ritardandolo di 1 barra l'edge Volatile cala dell'~80% e Sideways-Volatile cambia segno. *Citazione:* López de Prado, *Advances in Financial ML* (2018) cap. 7 (purging/embargo) e cap. 14 (backtest statistics) — qualunque feature di labelling dev'essere point-in-time.
2. **Assenza di edge incondizionato + decadimento post-pubblicazione** — PF 0.979, Sharpe −0.10, MC p=0.51 su 686 trade: ORB/London-breakout è strategia pubblicata da 20+ anni. *Citazione:* McLean-Pontiff (JF 2016, alpha decay); Osler (AER 2003) documenta l'edge degli ordini stop in un regime di liquidità diverso da quello retail 2020–2026.
3. **Costi di esecuzione non modellati su ordini stop** — il sistema è già sotto 1.0 di PF; −1 pip lo porta a PF 0.916 e Sharpe −0.39, e gli stop in breakout slippano più di 1 pip. *Citazione:* Quant Reviewer §3 (slippage 2–5× spread su stop in breakout violento).

---

## Test mancanti prima del live

- [ ] **Produrre i backtest B (`PARTIAL_TRAIL`) e C (`FULL_TRAIL`)** su MT5, stesso periodo/ticks → solo allora PBO exit-mode (s=16, T×3) + White's Reality Check ([core/quant_metrics.py](../../core/quant_metrics.py)).
- [ ] **Ricostruire il filtro di regime point-in-time** (label di D−1) e ri-misurare Sharpe/DSR/PBO sulla serie *gated*. Senza questo, ogni numero per-regime è inutilizzabile.
- [ ] **Hold-out OOS reale** (non la coda 2025–2026): walk-forward con riottimizzazione dei parametri per fold, OOS ≥ 20%.
- [ ] **Costi realistici**: spread variabile da tick + commissione prop (~$7/lot round-turn) + slippage 2× su stop. Ri-misurare PF/Sharpe.
- [ ] **Stazionarietà del regime** (ADF/KPSS) e test di persistenza prima di costruire qualunque switch di regime.

## Note operative

Non promuovibile a live in nessuna forma con i dati attuali.
- **NON** riattivare "Sideways Volatile" né toccare la `activation` rule: la giustificazione si basa su numeri look-ahead.
- Se si insiste su una versione regime-gated, trattarla come **nuova strategia da validare da zero** (point-in-time + costi + OOS), non come tuning di questa.
- Eventuale demo di sola osservazione (no size) ammessa solo per validare runtime (gap weekend, skip NFP/FOMC, slippage reale sugli stop), **non** come prova di edge.
- Sample 686 trade è sopra la soglia (≥200) → il problema non è la numerosità, è l'assenza di edge.

---

### Appendice — riproducibilità
Script di estrazione/analisi in [backtest_results/london_breakout/](../../backtest_results/london_breakout/): `_extract.py` (pairing in→out + diff duplicati), `_analysis.py` (battery completa), `_regime_lag.py` (look-ahead vs point-in-time). Metriche da [core/quant_metrics.py](../../core/quant_metrics.py). Dati: i due xlsx variante A + [data/regime_timeline_gbpusd.csv](../../data/regime_timeline_gbpusd.csv).
