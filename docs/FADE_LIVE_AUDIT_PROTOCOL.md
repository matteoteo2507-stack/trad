# Protocollo di audit del FADE live — scritto **prima** di guardare gli esiti

> **Documento vincolante.** Fissato il **2026-09-17**. Al momento della scrittura **nessuno ha
> guardato equity, P&L o R** dei trade live (utente: dichiarato il 2026-09-15; da parte mia: nessun
> esito mai calcolato, e in questa sessione ho deliberatamente **non** interrogato lo storico MT5).
> La finestra pulita e' ancora aperta ed e' l'unica cosa che rende questo documento utile.
>
> **Questo non e' il trial #3.** Non consuma trial. Non puo' produrre un GO ne' un KILL sulla
> strategia. Il perche' e' il contenuto di questo documento.
>
> Riferimenti: [`NXT_FADE_FORWARD_PREREGISTRATION.md`](NXT_FADE_FORWARD_PREREGISTRATION.md) §11
> (test azzerato) · [`STRATEGY_LIFECYCLE.md`](STRATEGY_LIFECYCLE.md) §3, §4 · [`DECISIONS.md`](../DECISIONS.md)
> voci 2026-08-27 (2) e 2026-09-15.

---

## 0. Fatti verificati, senza toccare gli esiti

| fatto | fonte | verificato |
|---|---|---|
| L'EA **entra ancora a mercato** quando il prezzo ha gia' superato l'entry pre-registrata | [`mql5/nxt_fade.mq5`](../mql5/nxt_fade.mq5) righe **432-451**: `else ok = g_trade.Sell(...)` / `g_trade.Buy(...)` | ✅ letto nel codice il 2026-09-17 |
| Il volume e' dimensionato sulla distanza **teorica** `entry - sl`, non su quella reale | stessa funzione, riga 427: `ComputeVolume(MathAbs(entry - sl))` | ✅ letto nel codice |
| Al 2026-09-15: **80 trade chiusi**, di cui **19 su 39 (49%) entrati a mercato** dopo il 27/08 | [`docs/health/2026-09-15.md`](health/2026-09-15.md), DECISIONS 2026-09-15 | ✅ gia' noto, nessun esito |
| Ritmo di raccolta | 80 trade in 53 giorni = **1,51/giorno**, di cui ramo onesto ≈ **0,77/giorno** | calcolato da date e conteggi |

⚠️ Il difetto del 27/08 **non e' stato riparato**. La patch di allora sistemo' i pendenti orfani, non
il ramo a mercato. Sono andato a leggerlo nel sorgente invece di fidarmi del resoconto.

---

## 1. La domanda che questo documento risolve

Il 2026-09-15 si e' deciso di **lasciare acceso** l'EA con due motivazioni:

1. i trade live sono **gli unici dati fuori campione** che il fade avra' mai (holdout bruciato);
2. il ramo rotto fornisce un **secondo test**: confrontando pendente contro mercato si verifica
   **il nostro modello del fill**, qualunque sia l'esito del primo.

Entrambe le motivazioni sono ragionevoli **se il campione puo' rispondere**. Nessuno aveva calcolato
se potesse. Questo documento lo calcola, **prima** di guardare i risultati — che e' l'unico momento
in cui il calcolo e' onesto.

---

## 2. Potenza: cosa questo campione puo' e non puo' vedere

Deviazione standard per trade **SD = 1,8R**, dal backtest (gia' dichiarata nella pre-registrazione
del 2026-08-04, §3). Test bilaterale, α = 0,05, potenza 80%.

### 2.1 Effetto minimo rilevabile

| n | errore standard | effetto minimo rilevabile |
|---|---|---|
| 36 (ramo a mercato) | 0,300R | **0,840R** |
| 46 (ramo onesto) | 0,265R | **0,744R** |
| 82 (tutto) | 0,199R | 0,557R |
| 200 | 0,127R | 0,357R |

Un E[R] di **+0,74R** su una strategia 1:3 corrisponde a un win rate del **43,5%** (il break-even e'
al 25%, il backtest fantasma sosteneva ~33%). **Non e' un'ipotesi che qualcuno abbia mai avanzato.**
Tradotto: con 46 trade non possiamo rilevare nessun effetto che qualcuno abbia mai proposto per
questa strategia.

### 2.2 Quanti trade servirebbero davvero

| effetto da rilevare | n necessario |
|---|---|
| +0,31R (il numero fantasma) | **265** |
| \|E\| = 0,25R | **407** |
| confermare che e' negativo, E = −0,14R (unilaterale) | **1.021** |
| +0,15R | 1.130 |

### 2.3 Il confronto fra i due rami — **qui la motivazione n. 2 cade**

La previsione del 27/08 e': ramo onesto ≈ −0,139R (punto medio), ramo a mercato ≈ −0,262R.
Differenza attesa ≈ **0,123R**.

| differenza da rilevare | trade necessari **per ramo** |
|---|---|
| **0,123R (quella prevista)** | **3.362** |
| 0,30R | 565 |
| 0,50R | 203 |

Al ritmo attuale, 3.362 trade per ramo sono **circa dodici anni**. Il "secondo test" che giustificava
di lasciare l'EA rotto **non e' sottodimensionato: e' fuori scala di un fattore ~40**.

> 🔧 **Conseguenza operativa**: la motivazione n. 2 del 2026-09-15 **non sopravvive al calcolo di
> potenza**. Non era sbagliata come ragionamento, era **non verificata come numero** — ed e'
> esattamente il buco 2 del distillamento Quant Guild, applicato per la prima volta contro una nostra
> decisione invece che contro una fonte esterna.

### 2.4 L'unico uso statistico legittimo, e quanto vale

Si puo' testare **in un solo senso**: falsificare il numero fantasma.
H0: E[R] = +0,310 · H1: E[R] < +0,310 · unilaterale, α = 0,05, **solo sul ramo onesto**.

| n | si rifiuta se la media osservata e' sotto | potenza se il vero E[R] e' −0,139 | se e' −0,25 | se e' 0,00 |
|---|---|---|---|---|
| 46 | −0,127R | **51,9%** | 67,9% | 31,7% |

> ⚠️ **Dichiarato ora, prima di vedere il dato**: con potenza ~52%, **il mancato rifiuto non e'
> informazione**. Se il test non rifiuta, la conclusione e' *"campione insufficiente"*, **mai**
> *"il fade potrebbe funzionare"*. Chiunque, fra sei mesi, usera' un mancato rifiuto come argomento
> per riaprire la famiglia, stara' violando questo paragrafo.

Per riferimento, l'intervallo di confidenza al 95% che otterremmo a n=46 e' largo **1,04R**: una media
osservata di −0,10R darebbe [−0,62 ; +0,42], che contiene sia il fantasma sia il disastro.

---

## 3. Il campione onesto non e' solo piccolo: e' **selezionato**

Questo non dipende dalla potenza ed e' il problema piu' grave.

Il vincolo **una sola posizione per strumento** (§2 della pre-registrazione) interagisce col ramo
rotto: quando l'EA entra a mercato, **occupa lo slot** e i setup successivi su quello strumento
**non vengono presi**. I trade "puliti" non sono quindi un sottoinsieme casuale dei setup: sono
quelli che capitano **quando nessun ingresso a mercato sta occupando lo strumento**.

E l'ingresso a mercato avviene per una ragione **non casuale**: il prezzo ha gia' superato l'entry,
cioe' il mercato si e' mosso in fretta contro il ritracciamento atteso. Quindi il ramo a mercato
cattura sistematicamente un **tipo di movimento** diverso, e il ramo onesto eredita il complemento.

> 🔧 **Il campione onesto raccolto finora e' contaminato da una selezione, non solo indebolito dalla
> numerosita'.** Nessuna quantita' di trade aggiuntivi raccolti **con l'EA in questo stato** risolve
> il problema: aumentarne il numero rende la stima piu' precisa **attorno al valore sbagliato**.

---

## 4. Cosa si fa, allora — audit deterministico (0 trial)

Le verifiche qui sotto sono **per-trade e binarie**: n=46 e' abbondante, perche' non si stima un
effetto, si controlla una conformita'. Nessuna consuma trial
([`STRATEGY_LIFECYCLE`](STRATEGY_LIFECYCLE.md) §3: l'integrita' di esecuzione non e' un tentativo di
ricerca).

| # | verifica | criterio di conformita' | cosa si guarda |
|---|---|---|---|
| **V1** | tipo di ordine di ogni ingresso | 100% `BUY_STOP`/`SELL_STOP` | `DEAL_TYPE` / `ORDER_TYPE` nello storico |
| **V2** | prezzo di riempimento | pari all'entry pre-registrata entro lo slippage del broker | prezzo ordine vs prezzo deal |
| **V3** | rischio effettivo per trade | \|entry reale − SL\| × volume = **1R** dell'equity, ±10% | prezzi e volume |
| **V4** | rapporto SL/TP effettivo | **1:3** su ogni trade conforme | prezzi SL e TP |
| **V5** | un solo trade per gamba per strumento | nessun doppione sulla stessa gamba | magic + tempi |
| **V6** | quota di setup **persi** per slot occupato | conteggio (non e' un pass/fail: e' la misura della selezione del §3) | log dell'EA vs ordini |

**Nessuna di queste richiede di guardare il P&L.** L'audit produce conteggi e conformita', non esiti.
Lo script che lo esegue deve stampare **solo** queste colonne: se stampa profitti, e' scritto male.

---

## 5. Tabella di decisione, dichiarata ora

| esito dell'audit | conseguenza, gia' decisa |
|---|---|
| **V1 fallisce** (esistono ancora ingressi a mercato) | i trade raccolti **non sono la strategia pre-registrata**. Il campione onesto resta **selezionato** (§3) e non e' utilizzabile per stimare E[R], ne' ora ne' mai. → si passa al §6 |
| **V1 passa ma V2/V3/V4 falliscono** | stesso esito: l'esecuzione non e' conforme, il campione non e' la strategia |
| **tutto passa** | i trade raccolti **dopo** l'ultimo ingresso a mercato costituiscono un campione pulito. Si applica §2.4 (falsificazione del fantasma) **e nient'altro**, con la clausola sul mancato rifiuto |

In **nessuno** di questi rami si dichiara un GO. Un GO sul FADE richiede il §6.

---

## 6. Cosa serve perche' il trial #3 possa esistere — con i numeri, stavolta

La pre-registrazione §11 elencava quattro condizioni. **Tre su quattro sono tuttora non soddisfatte**,
e ora ne aggiungiamo una quinta che prima mancava.

| # | condizione (§11) | stato al 2026-09-17 |
|---|---|---|
| 1 | primitiva unica `resolve_trade()` in `core/` | ❌ non esiste |
| 2 | backtest a **soli fill ottenibili** con E[R] positivo | ❌ oggi e' negativo per **ogni** variante (−0,32 ÷ −0,03) |
| 3 | EA che **rifiuta** il setup quando non puo' ottenere l'entrata | ❌ verificato nel codice: entra a mercato |
| 4 | pre-registrazione nuova con N nuovo | — dipende dalle precedenti |
| **5** | **N dichiarato sulla base della potenza**, non scelto a occhio | 🆕 aggiunta da questo documento |

### 6.1 Il costo in tempo, che nessuno aveva mai calcolato

Al ritmo del ramo onesto (**0,77 trade/giorno**):

| obiettivo | n | tempo di raccolta |
|---|---|---|
| rilevare +0,31R | 265 | **~11 mesi** |
| rilevare \|E\| = 0,25R | 407 | **~1,4 anni** |
| confermare che e' negativo (E = −0,14R) | 1.021 | **~3,6 anni** |

> 🔧 **Il risultato piu' importante di questo documento.** Il FADE non e' soltanto non dimostrato:
> con la nostra frequenza di trade **non e' risolvibile in meno di circa un anno**, e per un KILL
> statistico onesto servirebbero **tre anni e mezzo**. Questo va saputo **prima** di spendere il
> trial #3, non dopo: e' la differenza fra decidere di aspettare e scoprire di aver aspettato.

---

## 7. Impegni vincolanti

1. **Nessun verdetto su E[R] da questo campione.** Ne' GO ne' KILL. Il §2 dice perche'.
2. **Il mancato rifiuto del fantasma non e' evidenza a favore** (§2.4). Dichiarato prima di vedere il dato.
3. **L'audit non guarda il P&L.** Se una verifica richiede il profitto per essere eseguita, e' fuori
   perimetro di questo documento.
4. **Il trial #3 non si apre** finche' le condizioni 1, 2, 3 e 5 del §6 non sono tutte soddisfatte.
   In particolare: **non si apre un forward su una strategia il cui backtest a fill ottenibili e'
   negativo.** Sarebbe raccogliere dati per anni su qualcosa che il nostro stesso backtest dice non
   funzionare.
5. **Se l'EA viene riparato, il campione raccolto finora non si somma a quello nuovo.** Vale il §4.3
   della pre-registrazione, e vale contro di noi come gia' il 27/08.
6. **Questo documento non si modifica dopo aver visto gli esiti dell'audit.** Modifiche datate e
   motivate, come sempre.

---

## 8. Registro

| data | evento |
|---|---|
| 2026-09-17 | documento creato, prima di qualunque lettura degli esiti. Calcoli di potenza in DECISIONS 2026-09-17 (3) |

---

## 9. Esito dell'audit — eseguito il 2026-09-17

Motore: [`analysis/nxt/execution_audit.py`](../analysis/nxt/execution_audit.py).
Report: [`health/fade_execution_audit_2026-09-17.md`](health/fade_execution_audit_2026-09-17.md).
**Nessun P&L letto**: lo script ha un guard (`_assert_no_pnl`) che solleva un'eccezione se un record
contiene un campo di risultato.

| # | verifica | conformi | non conformi | esito |
|---|---|---|---|---|
| V1 | tipo di ordine e' pendente | 50 | **40** | ❌ **FALLITA** |
| V2 | fill al prezzo pre-registrato | 50 | 0 | ✅ passata (sui 50 pendenti) |
| V3 | rischio reale = rischio inteso | 51 | **39** | ❌ **FALLITA** |
| V4 | rapporto SL/TP = 1:3 | 51 | **39** | ❌ **FALLITA** |
| V5 | un solo setup attivo per strumento | 89 | **1** | ❌ fallita (1 caso) |
| V6 | setup che la spec non avrebbe preso | — | **40 su 90 (44%)** | misura della selezione |

**Il danno, in concreto.** I 39 trade non conformi hanno rischiato fino a **4,01×** l'1% previsto, con
il rapporto rischio/rendimento degradato fino a **1:0,00** — cioe' posizioni che rischiavano il 4%
dell'equity con premio atteso nullo. I peggiori:

| simbolo | data | rischio reale / inteso | RR reale |
|---|---|---|---|
| XAUUSD.cyr | 2026-08-13 12:32 | **4,01×** | 1:0,00 |
| US100 | 2026-07-31 04:00 | **3,95×** | 1:0,01 |
| US100 | 2026-08-31 05:00 | **3,84×** | 1:0,04 |

**La buona notizia, isolata**: **V2 passa su tutti e 50 i pendenti**. Quando l'EA riesce a piazzare
l'ordine pre-registrato, il fill avviene al prezzo giusto. Il meccanismo non e' rotto: era rotto il
**ripiego** quando il prezzo era gia' oltre.

### Verdetto, secondo la tabella del §5 dichiarata prima di guardare

> **V1 fallisce** → i trade raccolti **non sono la strategia pre-registrata**. Il campione onesto
> resta **selezionato** (§3) e **non e' utilizzabile per stimare E[R], ne' ora ne' mai.**

Quindi: **nessun verdetto su E[R]**, come previsto. I 90 ingressi raccolti dal 2026-07-24 al
2026-09-17 valgono **zero** per qualunque conclusione sulla strategia, esattamente come i 36 del
27/08. Il loro valore e' diagnostico e si esaurisce qui.

⚠️ **Il 44% e' peggiore del 40% misurato il 27/08.** Non e' un peggioramento del codice — il ramo a
mercato non e' mai stato toccato fino a oggi — ma la conferma che il difetto era **stabile e
continuo**: ha prodotto 23 ingressi non conformi su 45 solo dopo il fix del 27/08.

### Cosa cambia da qui

1. L'EA e' stato portato a **v1.10** lo stesso giorno: il ramo a mercato **non esiste piu'**, il
   setup si salta (commit `bbea38e`). Non consuma trial ([`STRATEGY_LIFECYCLE`](STRATEGY_LIFECYCLE.md)
   §3: correzione di bug + esecuzione piu' realistica).
2. Serve **ricompilare e ridistribuire** l'EA sulla VPS perche' il fix abbia effetto.
3. Il campione raccolto finora **non si somma** a quello nuovo (§4.3 della pre-registrazione, che
   vale contro di noi come il 27/08).
4. **V6 diventa misurabile in avanti**: da v1.10 ogni skip e' loggato e notificato. Il conteggio dei
   setup saltati sostituisce il conteggio degli ingressi a mercato come misura della selezione.
