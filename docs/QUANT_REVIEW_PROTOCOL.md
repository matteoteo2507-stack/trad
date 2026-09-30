# Quant Review — Protocollo operativo

Procedura passo-passo che il **Quant Reviewer** ([agents/quant_reviewer.md](../agents/quant_reviewer.md))
esegue quando viene invocato via skill [quant-review](../skills/quant-review/SKILL.md)
su una strategia (`mql5/*.mq5` o `strategies/*/`).

Output finale: report in `docs/reviews/<strategia>-<YYYY-MM-DD>.md` nel formato del
§Output di `quant_reviewer.md`.

---

## Step 1 — Comprensione della strategia (10 min)

1. Leggi il codice sorgente. Identifica:
   - **Entry rules** (timing, condizioni, ordini market vs limit vs stop).
   - **Exit rules** (TP, SL, time stop, trailing).
   - **Filters** (regime, news, blackout, sessioni).
   - **Sizing** (fixed fractional, vol target, fissato).
2. Scrivi un **sommario in 5 righe** in linguaggio quant.
3. Se non riesci in 5 righe → segnala **complessità eccessiva** come red flag e
   continua.

## Step 2 — Conta i gradi di libertà (5 min)

| Parametro | Origine | Tipo | Note |
|---|---|---|---|
| `InpAtrPeriod` | EA input | int | tunable |
| `InpTpRMultiple` | EA input | float | tunable |
| ... | ... | ... | ... |

- **N_params**: somma totale.
- **N_calibrati**: quanti sono stati scelti guardando i dati storici.
- **N_a_priori**: quanti sono "ovvi" (es. fine sessione = 16:00 UTC).
- **N_trial_stimati**: **non stimarlo a occhio** — leggilo:
  `python -m core.trial_ledger` dà il cumulato della famiglia e la soglia di
  futilità. Solo se la famiglia ha il contatore a `null` (non ricostruibile)
  assumi **100 × N_params** (Bailey-LdP 2014) e **dichiara che l'hai assunto**.

### Provenienza dell'ipotesi — da scrivere, non da ricordare

Chi ha proposto questa specifica, e su quali dati?

| provenienza | vale come predizione indipendente? |
|---|---|
| **fonte esterna umana** datata e citabile | sì |
| **razionale economico** che non richiede di conoscere l'esito | sì |
| **forward oltre il cutoff** del modello | sì — l'unica non contaminabile |
| **proposta dall'LLM** su dati **pre-cutoff** (maggio 2026) | **no**: può essere memorizzazione, va etichettata |
| **non dichiarata** | da trattare come il caso peggiore |

Evidenza esterna: *Profit Mirage* (arXiv 2510.07920) — spostando la finestra di test
oltre il cutoff, **quasi tutti** gli agenti LLM pubblicati **non battono un baseline
random**; in un test controfattuale il peggiore mantiene **82% di predizioni invariate**
anche perturbando gli input, cioè **recita**, non analizza.

⚠️ Segnala esplicitamente se il test "conferma" qualcosa di **famoso e molto
discusso** (crolli noti, regimi noti, titoli noti): è esattamente lo scenario in cui la
memorizzazione somiglia a competenza. Il campo si registra in
[`docs/trial_ledger.json`](trial_ledger.json) (`provenienza_ipotesi`).

## Step 3 — Raccogli i dati (15 min)

1. **Trade log** (necessario per metriche statistiche):
   - MT5 Strategy Tester → export CSV/HTM dei trade.
   - Python: `strategies/<name>/output/trades.csv`.
   - Live demo: export Notion `Trading Journal` filtrato per strategia.
2. **Matrice returns per CSCV** (necessaria per PBO):
   - T × N_varianti — almeno 2-3 varianti di parametri vicini per costruire
     la matrice. Senza varianti **non puoi calcolare PBO**: marca "insufficient
     data".
3. **Returns minimi**: ≥ 50 trade IS per qualunque conclusione. ≥ 200 per
   significatività robusta.

## Step 3bis — I fill erano **ottenibili**? (gate bloccante, prima di qualunque metrica)

> Questo gate esiste perche' la sua assenza e' costata **due mesi di lavoro su un edge
> inesistente**. Fino al 2026-08-27 la parola *ottenibile* non compariva in questo
> protocollo. Non si salta, e non si rimanda a valle delle metriche: una metrica
> calcolata su trade non ottenibili non misura la regola, misura l'artefatto.

**La definizione.** Un fill e' *ottenibile* se il prezzo a cui il backtest ci fa transare
era **ancora disponibile nel momento in cui avremmo potuto agire**. Non e' look-ahead di
**informazione** (il segnale puo' essere perfettamente confermato): e' look-ahead di
**prezzo**. Si transa a un livello che il mercato offriva solo *prima* che potessimo
mandare l'ordine.

### Le tre domande, in quest'ordine

1. **Quando potevamo agire davvero?** Il segnale e' noto alla **chiusura** della barra che
   lo conferma (`cb`) → la prima barra azionabile e' `cb+1`. Ogni ritardo di conferma —
   un frattale a K barre per lato, una media che serve N barre, un pivot — e' un periodo
   di **cecita'** durante il quale il prezzo si muove e noi guardiamo. *Precedente: il
   FADE usava un frattale K=5 su H1 = **~6 ore** di cecita', ed e' esattamente la finestra
   in cui avviene il ritracciamento che volevamo tradare.*
2. **Il livello era gia' oltrepassato all'apertura della prima barra azionabile?**
   E' un controllo di due righe e va **riportato come percentuale**, sempre:

   ```python
   fa = cb + 1                                    # prima barra azionabile
   gia_oltrepassato = (O[fa] > entry) if pos_long else (O[fa] < entry)
   ```

   Sotto il 5% e' un dettaglio da dichiarare. Sul FADE era il **46,1%**, e conteneva
   l'intero risultato. *Implementazione di riferimento:
   [`analysis/nxt/fade_obtainable.py`](../analysis/nxt/fade_obtainable.py) ·
   [`analysis/nxt/entry_fill_audit.py`](../analysis/nxt/entry_fill_audit.py).*
3. **Anche l'uscita usa un prezzo offerto?** Se la barra apre **oltre** lo stop, il fill e'
   `Open`, non lo stop: altrimenti si regala allo stop un prezzo che il mercato non
   offriva — lo stesso difetto, sul lato uscita. Gestito come parametro esplicito
   (`gap_beyond_stop`) in [`core/resolve_trade.py`](../core/resolve_trade.py).

### Cosa si fa quando il fill non e' ottenibile

Non si sceglie la variante col numero migliore: si **riportano tutte**, e la scelta e'
una regola nuova che costa un trial.

| variante | cosa fa | come leggerla |
|---|---|---|
| **SKIP** | se il livello e' gia' oltrepassato, **non si entra** | la piu' fedele alla spec: e' la strategia che si poteva davvero eseguire |
| **LIMIT** | piazza un limit e aspetta che il prezzo **torni** al livello | **maggiorante** della famiglia ottenibile: fill esatto, geometria intatta. Se e' negativo lui, lo e' tutta la famiglia |
| **RECENTER** | entra a mercato alla prima barra azionabile, SL/TP **ricentrati** sul fill reale | rischio controllato, ma e' una geometria diversa da quella pre-registrata |
| **LIVE** | entra a mercato con SL/TP **teorici** (quello che spesso fa l'EA) | da misurare sempre se l'EA ha questo ramo: sul FADE dava rischio **1,3-4,0x** e RR fino a **1:0,00** |

### I cinque campanelli — quando sospettare senza aver ancora misurato

1. **L'edge e' positivo in TUTTI gli anni e TUTTI gli asset.** E' sospetto, non
   rassicurante: nessuna anomalia di mercato rende lo stesso ammontare nel 2013 e nel
   2020, su FX e su indici. Un difetto **meccanico** si'. *Il FADE era +15/15 anni e
   +6/6 asset col fantasma; **0/15 e 0/6** senza.*
2. **Invertire la posizione inverte il segno dell'edge.** Il fade vende dove la
   continuazione compra: il fill non ottenibile che penalizza l'una avvantaggia l'altra
   **per costruzione**. Due risultati simmetrici non sono due conferme indipendenti, sono
   **un artefatto visto dai due lati**.
3. **Attesa fra piazzamento e riempimento ≈ 0.** E' il sintomo **live**: su 72 ordini
   riempiti in universo l'attesa mediana era **0,0h**. Un limit riempito subito e' un
   limit piazzato oltre il prezzo.
4. **L'entrata dipende da un pivot/frattale confermato con ritardo** di K barre.
5. **Il backtest riempie sempre**, cioe' non esiste nessun setup scartato per mancato
   riempimento. Un ordine che non manca mai non e' un ordine.

### Cosa blocca, e cosa no

- **Blocca il verdetto**: senza la percentuale di fill non ottenibili riportata, nessuna
  metrica di questo report e' pubblicabile. Il numero non misura la regola.
- **Non consuma trial**: rimisurare a fill ottenibili e' *modellazione piu' realistica
  dell'esecuzione* ([`STRATEGY_LIFECYCLE.md §3`](STRATEGY_LIFECYCLE.md)) — puo' solo
  peggiorare il risultato. ⚠️ Ma **scegliere** una delle varianti qui sopra per proseguire
  e' un cambio di regola dopo aver visto l'esito: **quello si', un trial**.
- **E' un kill duro se non riparabile**: un edge che esiste solo con fill fantasma ricade
  in `STRATEGY_LIFECYCLE §6a.1` (difetto metodologico conclamato). I numeri vecchi
  **non si citano piu'**.

### Precedenti registrati — il costo effettivo

| caso | col fill fantasma | coi soli fill ottenibili | delta |
|---|---|---|---|
| **FADE NXT** (5.506 / 10.218 setup) | **+0,409** [+0,370; +0,443] | **−0,250** [−0,287; −0,210] | **0,659R** — e ha ucciso la famiglia |
| **Continuazione NXT** | −0,444 | **−0,118** [−0,161; −0,076] | **+0,326R** — un NO-GO troppo severo |
| **Escursioni** (riesame 14/08) | −0,410 [−0,484; −0,332] | **−0,006** [−0,137; +0,130] | l'*"entrata peggiore del random"* era il fantasma |

> La lettura d'insieme, che e' la parte che conta: continuazione **−0,44R** e fade
> **+0,31R** sembravano *due misure indipendenti*. Erano **lo stesso fantasma con due
> segni opposti**. Sotto, con fill ottenibili, ci sono **zero e zero** — cioe' un livello
> **senza informazione**, in nessuna delle due direzioni.

## Step 4 — Esegui le metriche (20 min)

```python
import pandas as pd
import numpy as np
from core.quant_metrics import (
    sharpe_ratio,
    deflated_sharpe_ratio,
    pbo_cscv,
    walk_forward,
    mc_permutation_test,
    sortino_ratio,
    max_drawdown,
    calmar_ratio,
    tail_metrics,
    whites_reality_check,
)

# 1. Trade log → returns
trades = pd.read_csv("trades.csv")
r = trades["pnl_pct"].to_numpy()

# 2. Sharpe + DSR
sr = sharpe_ratio(r, periods_per_year=252)
dsr = deflated_sharpe_ratio(r, n_trials=100, periods_per_year=252)
# Stampa dsr["dsr"], dsr["significant_95"]

# 3. PBO (richiede matrice varianti)
variants_returns = ...  # T × N matrix
pbo = pbo_cscv(variants_returns, s=16)
# Stampa pbo["pbo"]; soglia accettabile < 0.15

# 4. Walk-forward
wf = walk_forward(r, train_size=126, test_size=63, anchored=False)
# Stampa wf.is_mean, wf.oos_mean, wf.degradation

# 5. Monte Carlo permutation
mc = mc_permutation_test(r, n_perm=2000, block_size=5)
# Stampa mc["p_value"]; soglia < 0.05

# 6. Risk metrics aggiuntivi
sortino = sortino_ratio(r)
mdd = max_drawdown(r)
calmar = calmar_ratio(r)
tails = tail_metrics(r)

# 7. White's Reality Check (se confronti varianti)
wrc = whites_reality_check(variants_returns, n_boot=1000, block_size=5)
```

### Come si riportano i numeri (buchi Quant Guild 2, 29, 37, 46 — dal 2026-09-30)

Con le primitive di [`core/verifiche.py`](../core/verifiche.py):

- **Ogni p-value Monte Carlo si riporta con il suo intervallo** (buco 37): `mc_permutation_test` e
  `whites_reality_check` restituiscono ora anche `p_corretto` = (b+1)/(B+1), `p_se`, `p_low`, `p_high`.
  Con 1.000 repliche, "p = 0,048" e "p = 0,062" **non sono distinguibili**: un verdetto che cambia fra i
  due non e' un verdetto. Se la soglia sta dentro l'intervallo, si aumentano le repliche
  (`repliche_per_distinguere`), non si legge il decimale.
- **Ogni verdetto negativo si scrive con l'MDE accanto** (buco 2): `mde(sd, n)` con n **indipendenti**.
  Senza, "non dimostrato" diventa "refutato" nel passaggio a DECISIONS (audit A5).
- **Indipendenza degli esiti** (buco 29): `runs_test` sulla sequenza vinto/perso prima di qualunque CI
  i.i.d. o Monte Carlo che rimescola i trade.
- **Due alternative si confrontano anche sulla coda** (buco 45, priorita' 2): `confronto_decile_peggiore`
  riporta media **e** media del 10% peggiore dei percorsi, e segnala se il segno del confronto cambia
  (Quant Guild, G6). Per un capitale che non puo' ricominciare, la coda decide quanto la media.
- **Nessuna correlazione senza frequenza e finestra** (buco 46): `correlazione_dichiarata(x, y,
  frequenza, finestra)` riporta intero campione **e** minimo/mediana/massimo della mobile. Due attivi
  "scorrelati" su base annuale possono stare a 0,73 su 60 giorni, proprio nella finestra del drawdown.

## Step 5 — Costi reali (10 min)

Verifica che il trade log includa:
- [ ] **Fill ottenibili** (Step 3bis) — e la percentuale di quelli scartati.
- [ ] Spread reale (variabile, non costante).
- [ ] Slippage modellato (stop orders → 2× spread minimo).
- [ ] Commissioni broker (anche se zero, documentarlo).
- [ ] Swap overnight se posizioni multi-day.
- [ ] Lot rounding a step minimo.

Se uno qualsiasi manca, **ricalcola le metriche** dopo aver applicato una
correzione conservativa (es. -1 pip / trade) e confronta degrado.

## Step 6 — Pre-mortem (10 min)

Rispondi per iscritto alle 3 domande del §6 di `quant_reviewer.md`:

1. **Quale cambiamento di regime la rompe?**
   (es. "London Breakout fallisce in Sideways Quiet quando range Asia >
   media e prezzo torna dentro").
2. **Quale assunzione metodologica nascosta?**
   (es. "il backtest assume liquidità infinita anche su NFP friday").
3. **Quale costo reale non modellato la affossa?**
   (es. "swap negativo su XAU short può divorare 1.5R / mese").

## Step 7 — Verdict

| PBO | DSR sig. 95% | OOS degrado | Verdict |
|---|---|---|---|
| < 15% | Sì | < 30% | **GO** (live con sizing standard) |
| 15-30% | Sì | 30-50% | **RAFFINA** (test aggiuntivi, ridurre params) |
| > 30% | No | > 50% | **NO-GO** |
| qualsiasi | qualsiasi | n_trades < 50 IS | **INSUFFICIENT DATA** |
| qualsiasi | qualsiasi | fill non ottenibili **non misurati** (Step 3bis) | **NESSUN VERDETTO** — il numero non misura la regola |

In caso di verdict ambiguo, **default verso NO-GO**. L'onere della prova è
sulla strategia, non sul reviewer.

⚠️ L'ultima riga non e' un verdetto piu' severo: e' l'**assenza** di verdetto. Un
NO-GO dichiarato su fill fantasma e' sbagliato quanto un GO — la continuazione NXT
e' stata bocciata a **−0,44R** quando il numero onesto era **−0,118R**.

## Step 8 — Output report

Salva in `docs/reviews/<strategia>-<YYYY-MM-DD>.md` con il formato del
§Output di `quant_reviewer.md`. Link relativi a:
- Codice strategia.
- Trade log usati.
- Eventuali notebook di analisi.

---

## Casi speciali

### Strategia con < 50 trade live ma backtest lungo

- Usa il backtest per PBO/DSR/walk-forward, ma **dichiara nel report**:
  "Live evidence insufficiente; metriche da backtest, soggette ai bias di
  costi/slippage". Verdict massimo possibile = **RAFFINA**.

### Strategia in stato di sperimentazione A/B/C (es. London Breakout 3 varianti)

- Calcola PBO con S=16 sulla matrice T × 3.
- Applica White's Reality Check per il multiple-testing.
- Verdict per ciascuna variante separato + verdict sulla famiglia.

### Strategia con assunzioni macro forti (es. carry trade, TSMOM)

- Verifica regime in cui il paper di riferimento documenta l'edge.
- Cita McLean-Pontiff JF 2016 per alpha decay post-publication.
- Verdict GO solo se l'edge è confermato anche nel sub-sample più recente
  (es. ultimi 5 anni).
