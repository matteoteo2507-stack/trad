---
titolo: NXT — Fibonacci + Elliott trend-pullback (strategia ex-soci)
fonti:
  - "_sorgenti/NXT strategy Fibonacci Elliott (video ex-socio).txt"
tipo: strategia_candidata
---

# NXT — Fibonacci + Elliott trend-pullback

> **STATO: in valutazione — esperimento ridotto pre-registrato.** Strategia usata da alcuni ex-soci dell'utente, spiegata in un video da uno di loro. Questo file contiene (1) il triage onesto, (2) la **pre-registrazione** dell'esperimento ridotto — regole fissate *prima* di vedere i risultati — e (3) il verdetto a valle. Motore: [`analysis/nxt/backtest.py`](../../analysis/nxt/backtest.py). Metodologia allineata a [[04_quant_metodologia]] e alla ricerca livelli [[project_level_research_v1_null_2026_07_06]].

## 1. Triage: cos'è, tolto il marketing

Sotto Fibonacci + Elliott, la sostanza è **trend-continuation su pullback**: in un trend stabilito, si attende un ritracciamento e si entra in direzione del trend con rischio definito, target 1:3, stop a break-even dopo 2R. Il resto (livelli 0.5/0.618/0.786, onde, punti 0/A/B/C) è **decorazione geometrica** attorno a quel nucleo.

**Tre red flag pregiudiziali** (motivano il rigore, non un pre-verdetto):

1. **Le statistiche dichiarate falliscono il BS-test** ([[04_quant_metodologia]] §8). A 1:3 il break-even è 25% di win rate; loro dichiarano 60-70%. Aspettativa implicita: `0.65×3 − 0.35×1 = +1.6R/trade` (a 60% → +1.4R). Un'aspettativa simile composta possiederebbe il mondo. Win-rate alto **e** RR alto non convivono nel retail: il claim è quasi certamente in-sample/cherry-picked (10 trade non sono un campione).
2. **"Meccanico" ma di fatto discrezionale** → look-ahead da manuale. "Swing significativo" per quale regola? Il conteggio Elliott "giusto" si trova col senno di poi. I caveat del video ("serve disciplina", "non tutte le sequenze sono valide") sono la scappatoia infalsificabile.
3. **Il meccanismo l'abbiamo già falsificato**: NXT è una strategia **level-reaction** (entri perché il prezzo "reagisce" a una zona Fib). La ricerca livelli v1+v2+v3 (384 trial pre-registrati) ha concluso NULL — i livelli, incluse le zone tipo-Fib, non battono il random su nessun TF. Vedi [[project_level_research_v1_null_2026_07_06]].

**L'unico kernel potenzialmente reale non è Fib: è il momentum/trend-continuation** (edge strutturalmente ancorato, evidenza ~200y — vedi [[05_portfolio_rischio]]). L'esperimento serve a separare la sostanza (momentum) dalla decorazione (Fib).

## 2. Pre-registrazione dell'esperimento ridotto

> **Le regole sotto sono immutabili una volta visti i risultati** (disciplina anti data-snooping, come per ORB e livelli). Se un parametro va cambiato dopo aver guardato l'output, è overfitting e va dichiarato.

### 2.1 Dati e universo
- **TF operativo**: H1 (default del presentatore). **Contesto trend**: struttura swing su H1 (no look-ahead).
- **Strumenti** (pool multi-asset, anti-fortuna-di-singolo-mercato): `EURUSD, GBPUSD, USDJPY, XAUUSD, US100, US500`. Fonte Dukascopy/MT5 già in `analysis/trading-bot-eval/data/*_H1.csv` (H1 dal 2012, ~14y).
- **Holdout temporale 70/30** per strumento: parametri e lettura si "decidono" sul train; il **verdetto vive sul TEST**. In più, **E[R] per anno** (caccia al miraggio "solo post-2020" che ha smascherato ORB v2).

### 2.2 Regole meccaniche (il primitivo tradabile)
Riduco la sequenza 0/A/B/C ambigua al **primitivo Fib-pullback** inequivocabile e coerente con gli step 6-8 del video:

1. **Swing detection**: pivot fractale con半-finestra `k=5` barre H1 (una barra è swing-high se è il massimo di 5 barre per lato; simmetrico per swing-low). Look-ahead-safe: uno swing è "confermato" solo `k` barre dopo, e si opera solo su swing confermati.
2. **Impulse leg**: ultima gamba impulsiva confermata `swingLow→swingHigh` (long) / `swingHigh→swingLow` (short). **Significatività**: ampiezza gamba `≥ 1.0×ATR(14, H1)` al momento dello swing di partenza.
3. **Filtro trend** (allineamento, mechanical): long solo se l'ultima struttura è **higher-high & higher-low** (lo swing-high della gamba supera il precedente swing-high, e il minimo di partenza supera il precedente swing-low); simmetrico short. Niente contro-trend.
4. **Entry** (variante primaria): **limit al 50%** di ritracciamento della gamba impulsiva. Il pending è valido finché il prezzo non rompe lo 0.786 (invalidazione) o non parte verso il target; finestra massima `48` barre H1 dallo swing-high.
5. **Stop-loss**: oltre il **78.6%** di ritracciamento della gamba (step 6 del video). Rischio `= |entry − SL| = (0.786−0.5)=0.286` dell'ampiezza gamba.
6. **Take-profit**: **1:3** R fisso dall'entry (step 7).
7. **Break-even**: SL portato a entry al raggiungimento di **+2R** (step 8 bonus).
8. **Un solo trade attivo per strumento per gamba**. No trade con apertura pending il venerdì (step del video: gap del lunedì).

### 2.3 Le tre ipotesi (falsificabili)
- **H1 — edge assoluto**: il Fib-pullback batte una **baseline random structure-free**? Baseline: stesso contesto trend + stesso management 1:3/BE@2R, ma **entry a un livello di ritracciamento casuale** in `[0.3, 0.7]` della gamba (SL/TP scalati di conseguenza). Confronto `E[R]` reale vs random, **cluster-bootstrap CI per (asset, gamba)**. *Edge assoluto solo se lower-bound CI della differenza > 0.*
- **H2 — il Fib è speciale?**: il 50% batte una **baseline naive** = entry a profondità di pullback fissa non-Fib (mediamente `0.5` ma testata anche `0.382`/`0.618` come robustezza) o casuale-in-zona? Isola se i *numeri di Fibonacci* contano vs "compra un dip qualunque in trend".
- **H3 — stazionarietà/OOS**: le stat reggono sul **test set** e non solo su un sotto-periodo? Break per anno.

### 2.4 Metriche e gate (pre-registrati)
- **Primaria**: `E[R]/trade` con **BCa 95% CI** ([`bca_bootstrap_ci`](../../core/quant_metrics.py)). **Decidi sul lower-bound**, non sul valore centrale (regola d'oro [[04_quant_metodologia]]).
- **Win rate** riportato esplicitamente per confrontarlo col claim 60-70%.
- **Differenza reale-vs-random / reale-vs-naive** con CI cluster-bootstrap (lower-bound > 0 per rivendicare edge del Fib).
- **Risoluzione intrabar**: bound **pessimistico** (SL prima di TP nella stessa barra) e ottimistico; il verdetto usa il pessimistico.
- **Costi**: spread round-trip per-strumento realistico (FX ~0.6-1.2 pip, XAU ~0.30, indici ~1-1.5 pt).
- **Trial**: config primaria UNICA pre-registrata → multiple-testing minimo; le varianti (0.618, no-BE, TP 1:2) sono **robustezza**, non selezione.
- **Gate GO** (tutti necessari): (a) E[R] pess TEST con **BCa lower-bound > 0**; (b) batte random con lower-bound diff > 0; (c) nessun collasso OOS (test coerente col train); (d) non "solo post-2020". Onere della prova sulla strategia: verdetto ambiguo ⇒ **NO-GO**.

## 3. Verdetto — **NO-GO schiacciante** (run 2026-07-17)

Config primaria pre-registrata (§2), pool 6 asset H1 ~14y, **10.290 setup reali**. Bound pessimistico, dopo costi.

| Test | Risultato | Esito |
|---|---|---|
| **Win rate** | **13.3%** (claim video: 60-70%; break-even 1:3 = 25%) | claim falsificato ~5×; sotto metà del break-even |
| **H1 — edge assoluto** | `E[R]=−0.439R`, BCa CI `[−0.464,−0.413]` | **FALSO** (fortemente negativo) |
| **H3 — holdout 70/30** | TRAIN −0.460 / TEST −0.392 | **FALSO** (nessun overfit: è proprio negativo) |
| **H3 — per anno** | **tutti 14/14 anni negativi** (2012→2026), nessun "solo post-2020" | **FALSO** |
| **Per asset** | 6/6 negativi (EURUSD −0.49 … USDJPY −0.38) | robusto |
| **H2 — Fib speciale?** | 0.5 (−0.439) *batte* random-depth (−0.523), diff +0.084 CI `[+0.070,+0.098]` | "meno negativo" ≠ profittevole; artefatto di costo, **non** edge |

**Meccanismo del fallimento** (più utile del solo numero): geometria auto-lesionista. Entry 0.5 + SL 0.786 mette lo stop a `0.286×ampiezza`, **dentro** la banda di rumore del ritracciamento → i pullback toccano spesso 0.618-0.786 prima di rimbalzare → stop preso e prezzo che riparte senza il trade. Stop stretto nel rumore + target lontano (1:3) ⇒ win rate strutturalmente sotto il 25% del random. Nessun tweak di **uscita** (BE, 1:2) lo salva: il 13% di TP-hit è qualità dell'**ingresso**, non gestione.

**Sul "Fib batte il random"**: reale ma economicamente irrilevante (entrambi perdono ~0.4-0.5R) e in gran parte artefatto (il random include ingressi a 0.7 con rischio minuscolo → costo per-R enorme). Nessun edge tradabile nei livelli di Fibonacci — coerente con [[project_level_research_v1_null_2026_07_06]].

**Chiusura.** NXT ridotta al suo primitivo tradabile è NO-GO su 14 anni e 6 mercati. Il kernel momentum non emerge in questa forma (entrata contro-ritracciamento con stop stretto). "Gli ex-soci lo usano" non implica profitto (cfr. [[project_veltrix_bot_eval_2026_06_12]]). Motore riproducibile in [`analysis/nxt/backtest.py`](../../analysis/nxt/backtest.py).

## 4. Chiusura definitiva — test dell'ipotesi "stop dentro il rumore" (run 2026-07-17b)

Diagnosi del §3: lo stop a 0.786 vive dentro il rumore del ritracciamento. Due implicazioni testabili, pre-registrate in [`analysis/nxt/closure.py`](../../analysis/nxt/closure.py) (4 config, verdetto su holdout+anno+asset, **multiple-testing esplicito**). Pool 6 asset H1 ~14y, bound pessimistico.

| Config | Descrizione | E[R] pess | Esito |
|---|---|---|---|
| **B1** | continuazione, entry 0.5, **SL oltre l'origine**, TP 1:1 | −0.286 | negativo (6/6 asset) |
| **B2** | continuazione, entry 0.5, SL oltre origine, TP 1:2 | −0.294 | negativo (6/6 asset) |
| **B3** | continuazione, entry 0.786 deep, SL oltre origine, TP 1:2 | −0.314 | negativo (6/6 asset) |
| **A1** | **FADE** (lato opposto), entry 0.5, mirror 1:3 | **+0.354** | positivo, robusto |

**Esito 1 — la mia ipotesi "wide-stop salva la continuazione" è FALSA.** B1/B2/B3 restano tutte negative su tutti gli asset: allargare lo stop non aiuta. **La continuazione non ha edge, con qualunque stop.** NXT (comprare il ritracciamento in trend) è definitivamente morta.

**Esito 2 — il FADE (A1) è positivo e robusto, MA è un lead, non un GO.**
- +0.354R, win 31.3% @ 1:3 (break-even 25%), BCa CI `[+0.320,+0.389]`.
- Holdout 70/30: TRAIN +0.379 / TEST +0.296 (regge); **14/14 anni positivi** (+0.14…+0.50); **6/6 asset positivi** (+0.28…+0.52).
- Net **mean-reversion** bilanciata long/short (fade delle gambe up *e* down) → non è beta del bull (EURUSD +0.36 lo conferma).
- Sotto bound **pessimistico** (SL prima di TP) e **sopravvive a 3× i costi/slippage** (+0.238R, lower-bound > 0; cost_R medio ~0.058).

⚠️ **Perché A1 NON è un GO** (disciplina anti data-snooping): A1 è un'**ipotesi derivata dai dati** — trovata *invertendo* la continuazione dopo averla vista fallire sull'intero campione. L'holdout 70/30 **non è indipendente** (tutti i 14 anni sono serviti a scoprire l'inversione). Per la dottrina [[feedback_backtest_long_history_falsification]] (*nessuna ipotesi si conferma sul backtest che l'ha generata*), A1 va trattata come **nuova candidata da ri-pre-registrare da zero** + **forward paper OOS**, non da rifinire su questi dati (sarebbe p-hacking). Angoli ancora aperti: fill tick-level reali, sensibilità a K (swing), scelta del target 3R, spread nei regimi di stress.

**Bottom line NXT.** La strategia degli ex-soci (continuazione Fib) è **NO-GO chiuso**. Il sottoprodotto — *fadare* il ritracciamento delle gambe mature (short-horizon mean-reversion) — è **il lead più forte mai prodotto in questo repo** e apre un thread NUOVO, separato da NXT, da validare con rigore indipendente. Vedi [[project_nxt_fib_nogo_2026_07_17]] (NEXT).

## Collegamenti
- [`analysis/nxt/backtest.py`](../../analysis/nxt/backtest.py) — motore.
- [[04_quant_metodologia]] — bias, BS-test, gate; [[05_portfolio_rischio]] — momentum come edge ancorato.
- [[project_level_research_v1_null_2026_07_06]] — precedente NULL sul meccanismo level-reaction.
- [[project_veltrix_bot_eval_2026_06_12]] — nello stesso giro, claim gonfiati (53% vs 80-90%): "gli ex-soci lo usano" ≠ evidenza di profitto.
- [`../_INTAKE.md`](../_INTAKE.md) — registro intake.
