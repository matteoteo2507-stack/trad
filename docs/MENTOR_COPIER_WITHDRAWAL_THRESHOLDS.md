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

---

## 8. Versione definitiva — dati completi e verificati (2026-09-18, sera)

Export unico e aggiornato a oggi, prezzi estesi da MT5 a oggi, copertura controllata prima di
calcolare. **Campione: 509 trade, 168 giorni, 2026-01-22 → 2026-09-18.**

### Il terzo difetto nei dati, trovato rigenerando `signals.csv`
`parse.py` aveva **tre nomi di file cablati** (`messages.html`, `2`, `3`) e ignorava
**`messages4.html`**, cioe' i messaggi piu' recenti di ogni export. Corretto con `glob` e
ordinamento **numerico**. Terzo difetto della stessa famiglia in un giorno, tutti nei **dati**.

### I numeri definitivi

| | valore |
|---|---|
| **E[R] a TP1** | **+0,026** — indistinguibile da zero |
| trade per distinguerlo da zero | **~5.300 (~5 anni)** |
| maxDD 95° (a blocchi) | **29,1 ± 0,6 R** |
| maxDD 95° (i.i.d., per confronto) | 20,0 ± 0,1 R — **l'indipendenza vale 9,1R, +46%** |
| serie negativa 95° | **9** (osservata 7) |

### La stabilita' mensile dice la cosa importante

| mese | n | E[R] | **diff. appaiata** |
|---|---|---|---|
| gen | 29 | −0,034 | **+0,310** |
| feb | 84 | −0,072 | **+0,250** |
| mar | 81 | +0,093 | **+0,370** |
| apr | 65 | +0,104 | **+0,292** |
| mag | 57 | −0,057 | **+0,193** |
| giu | 62 | +0,119 | **+0,233** |
| lug | 55 | +0,120 | **+0,309** |
| ago | 49 | −0,077 | **+0,245** |
| set | 27 | −0,030 | **+0,370** |

**Differenza appaiata complessiva: +0,2821 BCa95 [+0,2406 ; +0,3215]** su n=507, **positiva in tutti
e nove i mesi**.

> 🔧 **Conclusione del lavoro sul copier.** Il mentore **e' bravo a chiamare la direzione** — 9 mesi
> su 9, differenza fra +0,19 e +0,37 contro il lato casuale, con un intervallo stretto. **La
> geometria TP1/SL che pubblica converte quella bravura in circa niente**: TP1 rende +0,46R e lo stop
> costa −1,03R, quindi il pareggio e' al **69,1%** di vincite e lui sta al ~72%. **2,7 punti di
> margine.**
>
> **Copiarlo alla lettera non e' un'allocazione di capitale difendibile.** L'edge esiste, ma non in
> quello che si incassa uscendo a TP1.

### Cosa si puo' sorvegliare, e cosa no

| grandezza | governabile? |
|---|---|
| **E[R]** | **no** — ~5 anni per distinguerlo da zero. Una soglia su E[R] non scattera' mai in tempo |
| **differenza appaiata** | **si'** — positiva 9/9 mesi, deviazione fra i mesi ~0,06 |

Per ogni segnale copiato si registra anche l'esito del **lato casuale sullo stesso segnale** (costa
nulla, `oos_validation.py` lo fa gia') e si sorveglia **quella**.

### Soglie finali

| soglia | valore |
|---|---|
| **DD di ritiro** | **29 R** |
| **Serie negativa** | **9 consecutive** |
| **Finestra minima su E[R]** | **non applicabile** |
| **Sorveglianza primaria** | differenza appaiata; soglia da fissare sui primi mesi live |

⚠️ **Ipotesi generata dai dati, NON approvata**: uscire a **1R invece che a TP1** userebbe l'edge
direzionale invece di sprecarlo. **Costa un trial** (§3) e va pre-registrata prima, non provata ora.

### Igiene dei dati, sistemata
- Export **unico** in `_export_telegram/` (nome fisso, 704 segnali a oggi). I **tre** export datati
  che convivevano sono stati eliminati dopo aver verificato insiemisticamente che il nuovo li
  contiene tutti. L'unico segnale presente solo nel piu' vecchio era gia' registrato in
  `deleted_signals/` — **cancellato dal mentore dal canale**.
- Prezzi estesi a oggi con [`extend_prices.py`](../analysis/mentor_signals/extend_prices.py):
  riconciliazione sulla sovrapposizione **+$0,060 / correlazione 1,000000**, identica al riferimento.
- [`coverage.py`](../analysis/mentor_signals/coverage.py) stampa e verifica la finestra dei dati
  **prima** di ogni calcolo, e si ferma se l'export e' vuoto.

---

## 9. Quarta riscrittura — **la correzione dell'ora era applicata due volte** (2026-09-18, tarda sera)

> ⚠️ **Tutto il §8 e' NULLO e non va citato.** I numeri li' dentro sono stati prodotti con i
> segnali spostati di **+2h** invece che di +1h.

### Il difetto, e di chi e'

Il difetto e' **mio**, introdotto oggi stesso mentre correggevo il fuso orario (§0).

La correzione di +1h **esisteva gia'** da agosto dentro `oos_validation.to_engine()`
(`TZ_SHIFT_H = 1`, commit `a845a32`), dove era stata determinata con lo stesso criterio
indipendente dagli esiti. Non l'ho cercata: ne ho aggiunta una seconda dentro
`backtest.replay()`. Ogni analisi che passa dal primo loader e poi dal motore di replay
— **soglie di ritiro, validazione OOS, report al socio** — ha quindi applicato la
correzione **due volte**.

Effetto: non look-ahead (quello era il difetto di stamattina) ma l'opposto, **ingressi
cercati un'ora piu' tardi del vero**. Il fill sistematicamente peggiore ha prodotto
numeri **plausibili e sbagliati** — che e' la ragione per cui non si e' visto subito.

Misura dello scarto mediano |entry dichiarato − prezzo al timestamp|, criterio
indipendente dagli esiti, 699 segnali:

| shift aggiuntivo | −2h | −1h | **0h** | +1h | +2h |
|---|---|---|---|---|---|
| scarto mediano | $17,42 | $12,10 | **$3,98** | $9,39 | $13,30 |

Il minimo e' a **0**: i segnali usciti da `to_engine` erano **gia' allineati**, e il
`+TS_OFFSET` dentro `replay` era di troppo.

### La correzione, e perche' e' strutturale

**La correzione di fuso ha UN SOLO proprietario: il loader.** `load_signals()` e
`to_engine()` restituiscono timestamp gia' allineati; `replay()` e `market_replay()` non
toccano piu' l'orologio; il valore vive in un solo posto (`backtest.TS_OFFSET_H`) e
`oos_validation` lo importa invece di ridichiararlo.

Come effetto collaterale si chiude un secondo buco: `market_replay()` **non applicava
nessuna correzione**, quindi la tabella "robustezza al ritardo di copia" girava un'ora in
anticipo — look-ahead residuo mai notato.

`coverage.verifica()` adesso **calcola quella tabella a ogni esecuzione e solleva** se il
minimo non cade a 0. Una convenzione applicata in due posti non e' una svista che si
corregge guardando meglio: e' una proprieta' del codice, e va resa impossibile.

### I numeri veri — 629 trade, 170 giorni, 2026-01-22 -> 2026-09-18

| | §8 (sbagliato, +2h) | **§9 (corretto, +1h)** |
|---|---|---|
| trade replayati | 509 | **629** |
| **E[R] a TP1** | +0,026 | **+0,1265** BCa95 **[+0,0756 ; +0,1736]**, t = **+5,06** |
| vincenti (TP1 hit) | ~72% | **77,4%** |
| **differenza appaiata** | +0,2821 [+0,2406 ; +0,3215] | **+0,2939** BCa95 **[+0,2572 ; +0,3291]** |
| mesi con differenza positiva | 9/9 | **9/9** |
| maxDD 95esimo (a blocchi) | 29,1 R | **11,7 ± 0,2 R** |
| maxDD 95esimo (i.i.d.) | 20,0 R | 10,6 ± 0,1 R |
| costo dell'indipendenza | +9,1R (+46%) | **+1,09R (+10%)** |
| serie negativa 95esimo | 9 | **5** (osservata 4) |
| runs test | z = −3,37 | z = **−1,81** |
| **finestra minima su E[R]** | ~5.300 trade (~5 anni) | **199 trade (~54 giorni)** |

### Cosa cambia nella conclusione

**Si ribalta la conclusione del §8.** Non era vero che E[R] fosse indistinguibile da zero:
e' **+0,1265 con l'intervallo tutto positivo e t oltre 5**. Non era vero che servissero
cinque anni per sorvegliarlo: ne bastano **~54 giorni** di segnali. Non era vero che il
drawdown atteso fosse di 29R: e' **11,7R**.

Resta vero, e anzi si vede meglio, che **la geometria pubblicata non sfrutta tutta la
bravura direzionale**: il mentore chiama la direzione con un vantaggio appaiato di
**+0,294** contro il lato casuale, e uscendo a TP1 ne incassa **+0,127**. Il pareggio
richiede **69,1%** di vincite (TP1 +0,46R contro SL −1,03R) e lui sta a **77,4%**: il
margine c'e' — **8,3 punti**, non 2,7 — ma meno della meta' del vantaggio direzionale
arriva al conto.

### Stabilita' mensile della differenza appaiata (n=626)

| mese | gen | feb | mar | apr | mag | giu | lug | ago | set |
|---|---|---|---|---|---|---|---|---|---|
| n | 35 | 106 | 112 | 75 | 67 | 65 | 69 | 61 | 36 |
| **diff.** | +0,229 | +0,208 | +0,295 | +0,347 | +0,328 | +0,323 | +0,261 | +0,311 | +0,417 |

### Validazione OOS rifatta (finestra allungata a oggi)

La pre-registrazione del 2026-08-07 era gia' allineata correttamente, quindi **il verdetto
di allora non era contaminato**. Rifatta sulla finestra estesa (218 segnali, 15/06 -> 18/09,
contro i 131 originali) conferma con margine:

| | valore | soglia pre-registrata |
|---|---|---|
| differenza appaiata | **+0,274** BCa95 [+0,209 ; +0,333] | lower bound > 0 |
| E[R] a TP1 (pess) | **+0,173** BCa95 [+0,083 ; +0,244] | puntuale > 0 |
| win-rate mentore vs random | 61,2% contro 33,7% | — |

### Soglie finali (sostituiscono quelle del §8)

| soglia | valore |
|---|---|
| **DD di ritiro** | **11,7 R** (percentile 95, ricampionamento a blocchi) |
| **Serie negativa** | **5 perdite consecutive** |
| **Finestra minima** | **199 trade** (~54 giorni) — sotto non si valuta affatto |
| **Sensibilita'** | con E[R] al limite inferiore OOS (+0,079): DD **15,4 R**, serie 5 |
| **Sorveglianza** | E[R] **e** differenza appaiata: ora sono governabili entrambe |

### Il gate di esecuzione, rimisurato (C5)

Il divario fra il modello e la realta' operativa **resta il fatto piu' grande di tutti**:

| modello | n | E[R] |
|---|---|---|
| replay, fill a `entry` entro 6h | 629 | **+0,124** [+0,077 ; +0,172] |
| copier, fill **a mercato** +5 min, nessun gate | 696 | **−0,184** [−0,241 ; −0,125] |

Lo scostamento e' **sfavorevole nel 72% dei casi**. Separando i due lati:

| | n | E[R] |
|---|---|---|
| scostamento **favorevole** (entriamo meglio) | 195 | **+0,209** [+0,099 ; +0,311] |
| scostamento **sfavorevole** (entriamo peggio) | 501 | **−0,337** [−0,409 ; −0,276] |

Il gate di oggi guarda il **valore assoluto** e quindi butta via anche i segnali del primo
gruppo. Applicando **la soglia gia' in `config.yaml` (20 pip)** al **solo lato sfavorevole**:

| | n | % tenuti | E[R] |
|---|---|---|---|
| gate asimmetrico 20 pip | **293** | 42% | **+0,159** [+0,076 ; +0,239] |

Cioe' **meglio del replay stesso, su quasi la meta' dei segnali, con esecuzione a mercato
realistica**.

> ⚠️ **La soglia non si sceglie dalla tabella.** A 5 pip si legge +0,195 e a 30 pip +0,157:
> prendere il massimo sarebbe **eleggere un vincitore dopo aver visto gli esiti**, e
> costerebbe un trial. Si tiene il **20 gia' scritto in `config.yaml`**; l'unica modifica e'
> **simmetrico -> asimmetrico**, che e' una correzione di esecuzione, non una ricerca di
> parametro.
