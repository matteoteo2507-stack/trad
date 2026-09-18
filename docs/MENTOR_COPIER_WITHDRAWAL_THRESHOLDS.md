# Copier mentore — soglie di ritiro e gate di esecuzione, dichiarate **prima** del capitale

> **Documento vincolante.** Creato il **2026-09-18**, **riscritto lo stesso giorno** dopo aver
> trovato un disallineamento di un'ora fra i timestamp dei segnali e il feed dei prezzi. I numeri
> della prima stesura sono **nulli e non vanno citati**: §6a n.1 del
> [ciclo di vita](STRATEGY_LIFECYCLE.md) — un difetto conclamato non si corregge, si rifa' da zero.
>
> Copre le voci **C3** (soglie di ritiro, §8bis) e **C5** (gate anti-ritardo) del
> [backlog](BACKLOG_RICERCA.md). Motori:
> [`withdrawal_thresholds.py`](../analysis/mentor_signals/withdrawal_thresholds.py) ·
> [`latency_gate.py`](../analysis/mentor_signals/latency_gate.py).

---

## 0. Il difetto trovato per primo: **i timestamp erano indietro di un'ora**

Cercando la soglia anti-ritardo e' emerso che lo scostamento mediano fra il prezzo di mercato al
momento del segnale e l'`entry` dichiarato valeva **$12,92 — cioe' 1,27R**, piu' dell'intero TP1 nel
**79,5%** dei casi. Troppo per essere latenza.

Test dell'offset costante (se e' un fuso orario, uno shift deve **minimizzare** lo scostamento):

| shift | mediana \|mercato − entry\| |
|---|---|
| −1h | $18,15 |
| **0h (come stava)** | **$12,69** |
| **+1h** | **$4,23** ← minimo netto |
| +2h | $10,60 |

Minimo **netto** e **stabile su tutti e sei i mesi** (gen→giu), senza salti a marzo: e' un offset
**fisso**, non stagionale, quindi non DST ma un disallineamento di orologio fra l'export dei segnali
e il feed M5.

⚠️ **Perche' e' grave.** `replay()` cercava il fill partendo da `searchsorted(T, ts)`, cioe'
**un'ora prima che il segnale esistesse**. Il riempimento poteva avvenire su prezzi **precedenti alla
pubblicazione**: e' look-ahead di prezzo, la stessa famiglia del fill fantasma che e' costata due mesi
sul FADE ([[feedback_fill_ottenibile]]).

**Quanto valeva**, misurato:

| | fill eseguiti | win-rate simmetrica | E[R] a TP1 |
|---|---|---|---|
| ts grezzo (come tutto e' stato validato finora) | 88% | **67,3%** | **+0,2025** |
| **ts corretto (+1h)** | 78% | **56,1%** | **+0,1015** [+0,037 ; +0,159] |

**L'E[R] si dimezza e il win-rate perde 11 punti.** Il "67-72%" citato ovunque nel repo era misurato
col difetto.

### Ma l'edge sopravvive, e il motivo e' il disegno appaiato

La metrica primaria del verdetto OOS non era il win-rate assoluto: era la **differenza appaiata**
contro lo stesso segnale con lato casuale. Il difetto gonfiava **entrambi i lati**, e la differenza
lo assorbe quasi tutto:

| | mentore | random | differenza appaiata |
|---|---|---|---|
| ts grezzo | 67,4% | 35,3% | **+0,3214** [+0,2794 ; +0,3613] |
| **ts corretto** | 56,2% | 30,8% | **+0,2541** [+0,2118 ; +0,2941] |

> 🔧 **Il verdetto OOS non si ribalta: l'edge era sovrastimato del ~21%, non inventato.** E il motivo
> per cui non si ribalta e' che era misurato **contro un baseline appaiato** invece che contro una
> soglia assoluta — la stessa lezione di [[feedback_r_multiple_ceiling_baseline]], qui a nostro
> favore.

**Correzione applicata** in `analysis/mentor_signals/backtest.py` come `TS_OFFSET`, cosi' vale per
tutti gli script a valle. E' un **bug fix**: non consuma trial (§3).

---

## 1. Il binario e il suo profilo (numeri corretti)

Copia-segnali del mentore su **XAUUSD**, uscita a **TP1**, scenario pessimistico, costi inclusi.

| | |
|---|---|
| E[R] | **+0,1015** BCa95 [+0,037 ; +0,159] |
| deviazione standard | 0,60 |
| vincenti | ~72% |
| trade / giorno | 4,2 |

⚠️ Profilo ad **alto win-rate e payoff piccolo**: l'equity sale quasi sempre e scende di colpo. E'
il profilo in cui la tentazione di spegnere nel mezzo di un drawdown e' massima proprio quando
statisticamente non andrebbe fatto — cioe' il motivo per cui §8bis esiste.

---

## 2. Gli esiti **non sono indipendenti**, e questo cambia le soglie

| diagnostica | valore |
|---|---|
| runs test vinta/persa | **z = −2,55** |
| autocorrelazione dei rendimenti, lag 1 | **+0,128** |
| segnali al giorno | 4,2 (max 9), stesso strumento |

Quando la lettura del mentore e' sbagliata, **sbaglia per tutta la sessione**: le perdite arrivano in
grappoli. Il Monte Carlo che rimescola i trade distrugge proprio quel raggruppamento.

| simulazione (95° percentile, 20.000 percorsi) | maxDD | serie negativa |
|---|---|---|
| i.i.d. — rimescola i singoli trade | 10,94 ± 0,13 R | 5,88 ± 0,35 |
| **a blocchi — ricampiona giorni interi** | **13,72 ± 0,23 R** | **5,00 ± 0,00** |

**L'ipotesi di indipendenza vale 2,78R, il 25% di drawdown in meno** (buco 29 del distillamento).
Gli errori standard sono riportati perche' un percentile e' una stima (buco 37).

---

## 3. Le soglie di ritiro — **§8bis**

| soglia | valore |
|---|---|
| **DD di ritiro** | **13,7 R** (95° pct, ricampionamento a blocchi) |
| **Serie negativa di ritiro** | **5 perdite consecutive** |
| **Finestra minima di valutazione** | **310 trade** (~73 giorni) |

⚠️ **La finestra minima e' quintuplicata rispetto alla prima stesura** (era 62 trade): serve
$n \approx (2{,}80\,\sigma/E)^2$, e con E[R] dimezzato il fabbisogno **quadruplica**. E' il prezzo
del difetto, ed e' bene saperlo prima e non dopo: **sotto i 310 trade non si valuta affatto**,
nemmeno per dire "sta andando bene".

**Macchina a stati** (§8bis):

```
   LIVE ──(DD > 13,7R  oppure  5 perdite consecutive)──► INCUBAZIONE
     │                                                        │
     │                                              (criterio di rientro)
     │                                                        ▼
     │                                                      LIVE
     │                                        (seconda uscita) │
     └──(razionale falsificato / difetto)──────────────► RITIRATA
```

- **Criterio di rientro, dichiarato ora**: in simulazione la curva **recupera il picco precedente**
  all'ingresso in incubazione **e** sono passati almeno **310 trade**. Entrambe le condizioni.
- **Seconda uscita dopo un rientro → RITIRATA definitiva.**
- **Ritiro immediato senza incubazione** se cade il razionale: il mentore smette, cambia stile o
  strumento (key-man risk), oppure emerge un difetto metodologico nel replay — **come e' appena
  successo**.

---

## 4. Il gate di esecuzione — **C5**, e non e' un dettaglio

Il replay riempie **a `entry`**, aspettando fino a 6h che il prezzo ci torni. Il copier vero piazza
`order_type="market"` sul trigger "NOW" del canale (`signal_copier/executor.py`). **Sono due
esecuzioni diverse**, e la differenza e' enorme:

| modello di esecuzione | E[R] |
|---|---|
| replay (fill a `entry`, attesa fino a 6h) | **+0,101** [+0,037 ; +0,159] |
| copier senza gate (fill a mercato, +5 min) | **−0,256** [−0,332 ; −0,185] |

**Senza gate, l'esecuzione a mercato trasforma l'edge in una perdita.** Il gate non e' una
raffinatezza: e' cio' che rende il binario praticabile.

### Lo scostamento favorevole e quello sfavorevole non sono la stessa cosa

| | n | E[R] |
|---|---|---|
| **favorevole** (entriamo meglio del mentore) | 132 | **+0,183** [+0,043 ; +0,310] |
| **sfavorevole** (entriamo peggio) | 347 | **−0,423** [−0,510 ; −0,348] |

Il meccanismo e' aritmetico: entrando peggio, il rischio reale supera l'1% su cui `suggested_lots`
ha dimensionato **e** il TP1 si allontana. Il gate di oggi (`max_slippage_pips: 20`) li tratta
**uguali**, quindi butta via proprio i trade migliori.

### La regola, con il numero gia' dichiarato

| configurazione | trade tenuti | E[R] |
|---|---|---|
| simmetrico a 20 pip (oggi) | 103 (22%) | +0,085 [**−0,045** ; +0,192] |
| **asimmetrico: nessun limite sul favorevole, 20 pip sullo sfavorevole** | **197 (41%)** | **+0,130** [**+0,037** ; +0,236] |

> **Quasi il doppio dei trade e un intervallo che non tocca lo zero, con lo stesso numero.** Non e'
> una taratura: **20 pip era gia' il valore dichiarato**, si toglie solo una restrizione che i dati
> mostrano dannosa. Modifica di **modellazione dell'esecuzione**, non ricerca di parametri (§3).

**Da implementare** in `signal_copier/planner.py`: il gate `anti_late` deve misurare lo scostamento
**con segno** rispetto alla direzione del segnale e applicare `max_slippage_pips` **solo** quando il
prezzo si e' mosso **contro** di noi.

---

## 5. Limiti dichiarati

1. **Campione in larga parte in campione** (gen→giu 2026, il periodo da cui l'edge e' stato
   identificato). La validazione OOS e' successiva, su export diverso, **e va rifatta col
   `TS_OFFSET` corretto**: finche' non e' rifatta, il verdetto OOS va considerato **sovrastimato di
   circa il 21%**, non annullato.
2. **Il gate va implementato prima del capitale.** Oggi il codice e' ancora simmetrico: i numeri del
   §4 descrivono una configurazione che **non e' quella in esecuzione**.
3. Un solo strumento, un solo mentore, cinque mesi. Nulla di questo e' trasferibile a un'altra fonte.
4. Il rischio per trade resta **1% del capitale** (`risk_per_signal_pct`), diviso fra le gambe:
   13,7R di drawdown valgono circa il **13,7%** del capitale.

---

## 6. Registro

| data | evento |
|---|---|
| 2026-09-18 | prima stesura: DD 12R, serie 6, finestra 62. **Nulla** — costruita su timestamp disallineati |
| 2026-09-18 | **seconda riscrittura**: usavo i file corti. Su tutto il campione E[R] scende a **+0,0375**, DD **25R**, e il binario risulta **non governabile su E[R]**. Il mentore e' bravo sulla direzione, la geometria TP1/SL la spreca |
| 2026-09-18 | trovato l'offset di +1h, corretto in `backtest.py` come `TS_OFFSET`. Riscrittura: DD **13,7R**, serie **5**, finestra **310 trade**. Aggiunto il §4 (gate asimmetrico, C5) |

---

## 7. Seconda riscrittura (stesso giorno): **stavo usando i file corti**

Domanda dell'utente: *fino a che mese arrivano i dati?* La risposta ha invalidato di nuovo i numeri.

| file | copertura | l'avevo usato? |
|---|---|---|
| `XAU_spot_M5.csv` | → **12/06** | si' |
| **`XAU_spot_M5_ext.csv`** | → **07/08** | **no** |
| `signals.csv` | → **08/07** | si' |
| **export Telegram** `Messaggi tg aggiornati 07-08` | → **07/08**, 617 segnali | **no** |

**I due mesi in piu' erano gia' nel repo**, usati da `oos_validation.py` che fa `bt.M5 = M5_EXT`.
Io ho importato `bt.load_m5()` col default corto. Errore mio, non un limite dei dati.

### Rifatto su tutto (443 trade, 2026-01-22 → 2026-08-07)

| | campione corto | **completo** |
|---|---|---|
| E[R] | +0,1015 | **+0,0375** |
| serie negativa osservata | 4 | **7** |
| maxDD 95° (a blocchi) | 13,7R | **25,0R** |
| finestra minima | 310 trade | **2.522 trade (~2 anni)** |

### Ma non e' decadimento: e' un numero piccolo, misurato male

| mese | n | E[R] | win% | random% | **differenza appaiata** |
|---|---|---|---|---|---|
| 2026-01 | 29 | −0,034 | 58,6% | 27,6% | **+0,310** |
| 2026-02 | 84 | −0,072 | 47,6% | 22,6% | **+0,250** |
| 2026-03 | 81 | +0,093 | 59,3% | 22,2% | **+0,370** |
| 2026-04 | 65 | +0,104 | 58,5% | 29,2% | **+0,292** |
| 2026-05 | 57 | −0,057 | 47,4% | 28,1% | **+0,193** |
| 2026-06 | 62 | +0,119 | 55,0% | 31,7% | **+0,233** |
| 2026-07 | 55 | +0,120 | 52,7% | 21,8% | **+0,309** |
| 2026-08 | 10 | −0,130 | 40,0% | 10,0% | **+0,300** |

E[R] oscilla attorno a zero senza tendenza (prima meta' +0,014, seconda +0,061, entrambe con
intervallo che attraversa lo zero). **La differenza appaiata invece e' positiva in tutti e otto i
mesi**, fra +0,19 e +0,37.

> 🔧 **La lettura che ne esce, ed e' il risultato piu' importante del lavoro sul copier.**
> **Il mentore e' bravo a chiamare la direzione; la geometria TP1/SL che pubblica converte quella
> bravura in circa niente.** Con TP1 a **+0,46R** e stop a **−1,03R** il pareggio e' al **69,1%** di
> vincite: lui sta al **71,8%**, cioe' **2,7 punti di margine**. L'edge direzionale (~55% contro
> ~26% del lato casuale) e' grande e stabile; il modo in cui viene monetizzato no.

### Conseguenza operativa

**Con E[R] = +0,0375 e sd = 0,67 il binario non e' governabile su E[R]**: servirebbero ~2.500 trade
(due anni) per distinguerlo da zero. Una soglia di ritiro su E[R] non scattera' mai in tempo utile.

**La grandezza governabile e' la differenza appaiata**, che ha un rapporto segnale/rumore molto
migliore (positiva 8 mesi su 8, deviazione fra i mesi ~0,05). Per ogni segnale copiato si registra
anche l'esito del **lato casuale sullo stesso segnale** — costa nulla, e' gia' quello che fa
`oos_validation.py` — e si sorveglia quella.

⚠️ **Ipotesi generata dai dati, NON approvata**: uscire a **1R invece che a TP1 (0,5R)** userebbe
l'edge direzionale invece di sprecarlo. Con 55% contro 45% a 1:1 darebbe E[R] ≈ +0,10 invece di
+0,04. **E' un cambio di parametro dopo aver visto l'esito: costa un trial** (§3) e va
pre-registrato, non fatto adesso.

### Soglie aggiornate

| soglia | valore |
|---|---|
| **DD di ritiro** | **25 R** (95° pct, blocchi) |
| **Serie negativa** | **9** (osservata 7) |
| **Finestra minima su E[R]** | **non applicabile** — servirebbero ~2 anni |
| **Sorveglianza primaria** | **differenza appaiata contro il lato casuale**, soglia da fissare quando il copier accumula i primi mesi live |
