# Criteri di selezione prop firm — le NOSTRE condizioni

> **Metodo: prima definiamo cosa ci serve, poi cerchiamo chi lo soddisfa.** Non si parte dai
> comparatori — che sono in larga parte contenuto affiliato — e non si adatta la strategia alle
> regole di una firm scelta per lo split. Ogni condizione qui sotto è **derivata da cosa tradiamo
> davvero**, non da preferenze generiche.
>
> Aggiornato **2026-08-07**. Stato: **preparatorio** — nessuna strategia è oggi finanziabile
> (ORB NO-GO, fade LEAD in forward). Questo documento serve a essere pronti al primo GO.

---

## 0. Cosa dobbiamo far girare (il vincolo a monte)

| Strategia | Profilo | Stato |
|---|---|---|
| **nxt_fade** | H1, 6 strumenti simultanei (EURUSD, GBPUSD, USDJPY, XAUUSD, US100, US500), contro-trend, 1:3, BE a +2R, holding **mediano 5 ore**, cap a ~20 giorni (solo il **10,5%** dei trade vede un weekend) | LEAD, forward in corso |
| **orb_nasdaq** | NAS100 intraday, apertura cash USA 09:30 ET, chiusura entro 12:00 ET | NO-GO su backtest, forward per la domanda post-COVID |
| ~~segnali mentore~~ | XAUUSD manuale | ❌ **Fuori perimetro prop** — vedi §4 |

---

## 1. Requisiti ELIMINATORI

Se una firm non soddisfa uno di questi, è fuori. Nessuna compensazione con split o prezzo.

### 1.1 Drawdown giornaliero calcolato sul BALANCE, non sull'equity flottante

**È il criterio più importante e il meno pubblicizzato.** `nxt_fade` tiene posizioni aperte **fino a
20 giorni di borsa**, su **6 strumenti in parallelo**, con stop a 1R e target a 3R. Se il limite di
perdita giornaliera si calcola sull'**equity flottante**, una posizione che va contro **prima** di
girare a TP può far scattare la violazione — e la strategia viene uccisa da una regola contabile,
non da una perdita reale.

Con posizioni correlate aperte insieme (EURUSD/GBPUSD, US100/US500) il flottante negativo si somma:
il rischio non è teorico.

→ **Domanda da fare alla firm:** *"Il daily loss limit è calcolato su balance di inizio giornata o
include il P&L flottante delle posizioni aperte?"*

### 1.2 Drawdown massimo STATICO, non trailing

Il trailing drawdown che segue l'equity di picco è incompatibile con un payoff 1:3: dopo un vincitore
il floor si alza e un normale ritorno alla media diventa una violazione. Statico su balance iniziale
è lo standard di FTMO, The5ers, FXIFY — quindi è ottenibile, non è una pretesa.

### 1.3 Holding overnight e nel weekend consentito

⚠️ **Ridimensionato il 2026-08-14 su misura diretta** (`analysis/nxt/weekend.py`): il fade era classificato come swing per via del cap a 20 giorni, ma la distribuzione reale dice altro — **holding mediano 5 barre H1** e solo il **10,5%** dei trade attraversa un fine settimana. Il criterio resta valido ma **pesa molto meno**: non e' una strategia che vive nel weekend, e una firm che obbliga a chiudere il venerdi' amputerebbe ~1 trade su 10, non la strategia. Nota di rischio opposta e confermata: quando il weekend c'e', la **varianza** e' reale — un gap oltre 0,5R nel **26,9%** dei weekend e oltre 1R nel **10,3%** (rileva per il daily DD, non per l'aspettativa: il gap medio e' **−0,008R, CI [−0,063, +0,046]**, indistinguibile da zero).

`nxt_fade` è di fatto **swing**, non intraday. Le firm che obbligano a chiudere prima del weekend, o
che azzerano i profitti delle posizioni tenute oltre il venerdì, lo rendono ineseguibile. Gli swap
sono accettabili; il divieto no.

### 1.4 EA consentiti su MT5

I nostri EA sono MQL5 compilati. Vietati ovunque HFT, latency arbitrage e tick scalping — non ci
riguardano. Serve la conferma esplicita che breakout e mean-reversion standard siano ammessi.

**Preferenza forte: senza consegna del sorgente `.mq5`.** Alpha Capital richiede l'invio di `.ex5`
**e** `.mq5` per la pre-approvazione. Oggi è irrilevante (non abbiamo nulla di validato), ma è una
condizione da pesare il giorno in cui l'EA avrà edge dimostrato.

### 1.5 Nessuna consistency rule, o dimostrabilmente compatibile

Una regola tipo il **40% best-day** di Alpha Capital limita quanta parte del profitto può venire da
un solo giorno. Con payoff 1:3 il nostro P&L giornaliero è **a code grasse per costruzione**: pochi
giorni fanno la maggior parte del risultato.

→ **MISURATO il 2026-08-07** — motore [`analysis/nxt/consistency.py`](../analysis/nxt/consistency.py)
(rigioca la config A1 pre-registrata catturando la barra di uscita; riproduce esattamente i numeri di
`closure.py`: E[R] +0.354 → **+0.308 dopo il fix sui fill del 2026-08-14**, win 31.3%, n=10.280).

Quota del giorno migliore sul profitto della finestra, **solo finestre in utile** (quelle in cui si
chiede il payout):

| Finestra | Mediana | Media | **Sfora 40%** | Sfora 50% |
|---|---|---|---|---|
| **14 giorni** (payout bi-settimanale) | **57,2%** | 62,9% | **74,7%** | 59,2% |
| 30 giorni | 35,3% | 44,6% | 41,9% | 29,3% |
| 60 giorni | 21,1% | 28,1% | **15,7%** | 10,9% |

**Su ciclo bi-settimanale `nxt_fade` violerebbe una regola del 40% in 3 payout su 4** — e la
*mediana* stessa sfora. **Alpha Capital paga il 14 e il 28 → squalificata per questa strategia**, a
prescindere da split, costo o esecuzione.

**Mitigazione (importante).** La violazione crolla allungando la finestra: 75% → 42% → **16%**. Se la
regola si calcola sul profitto **dall'ultimo payout**, richiedere il payout ogni ~60 giorni invece
che ogni 14 rende il vincolo gestibile. Da cui una domanda che va posta a ogni firm con consistency
rule:

> *Si calcola sul profitto accumulato dall'ultimo payout, dall'apertura del conto, o sull'intera
> storia dell'account? Sono obbligato a richiedere il payout a scadenza o posso lasciar accumulare?*

Calcolo **dall'ultimo payout + accumulo libero** → gestibile. **Intera storia** o **payout
obbligatori a scadenza** → resta eliminatoria.

> **Il risultato è più durevole della strategia.** Il calcolo **non dipende dall'avere edge**:
> dipende dalla *forma* della distribuzione (payoff 1:3, trade sparsi, 64% di giorni con chiusure).
> Quella forma è fissata dal disegno. Quindi **payoff 1:3 + payout bi-settimanale + consistency rule
> 40% = incompatibili** vale per **qualunque strategia di questa forma**, anche futura. È un vincolo
> di progettazione, non un risultato su `nxt_fade`.

### 1.6 Regole news compatibili con posizioni aperte

FTMO vieta di **aprire, modificare o chiudere** su XAUUSD e DXY nei ±2 minuti attorno a FFR, NFP,
CPI, GDP advance e FOMC minutes — e la regola **si applica da funded**, non in challenge. Con
posizioni aperte significa non poter gestire uno stop nel momento di massima volatilità.

FundedNext applica un **taglio del 40% sui profitti** realizzati in finestra news e una regola di
SL a 3 minuti su funded.

→ Serve sapere: cosa è vietato esattamente, se vale solo l'apertura o anche la chiusura, e se
cambia tra challenge e funded.

### 1.7 Strumenti e leva accettabili su XAUUSD e NAS100

FundedNext ha tagliato la leva su XAUUSD da **1:100 a 1:10** (gennaio 2026): cambia margine e
sizing. Serve la tabella per strumento, non la leva "di conto".

### 1.8 Disponibilità per residenti italiani

E postura verso **MiFID II**: ESMA ha dichiarato (settembre 2026) che le prop rivolte all'UE
potrebbero rientrare nel perimetro, con le challenge fee trattate come compenso per servizio
d'investimento. La Czech National Bank è il primo regolatore UE a muoversi — rilevante perché FTMO è
ceca. **CONSOB** aveva già avvertito nel luglio 2024 sulle challenge retail.

---

### 1.9 La challenge si puo' superare per caso: il numero di riferimento (buco Quant Guild 15, 2026-09-30)

Prima di leggere "l'ho passata" come prova di abilita', si calcola quanto spesso la **stessa challenge**
si supera **senza edge**, con `core.verifiche.prob_obiettivo_prima_del_limite(mu, sigma, obiettivo,
limite)` (o `rovina_del_giocatore` per passi discreti). Con edge zero, una challenge **+8% / −10%** si
supera nel 10/18 = **~56%** dei casi. Un superamento vale come evidenza solo se la probabilita' con
l'edge dichiarato e' **molto** piu' alta di quella a edge zero, e ogni regola aggiuntiva (drawdown
giornaliero, consistency) va simulata sopra, non ignorata.

## 2. Criteri di RANKING (a parità di eliminatori)

In ordine di peso. Nota che il **profit split è ultimo**: l'80% o il 90% di zero è zero.

| # | Criterio | Perché |
|---|---|---|
| 1 | **Track record dei payout + anzianità** | **Rischio di controparte = dominante.** 80-100 firm hanno chiuso nel 2024. La firm deve esistere e pagare *quando saremo profittevoli*, cioè tra molti mesi |
| 2 | **Chiarezza e stabilità del rulebook** | Regole cambiate unilateralmente a metà percorso sono il modo tipico in cui si perde un account |
| 3 | **Costo della challenge** e politica di retry | È il capitale a rischio reale finché non si è funded |
| 4 | **Frequenza dei payout** | Bi-settimanale > mensile: riduce l'esposizione temporale alla firm |
| 5 | **Condizioni di esecuzione** (spread, slippage, server) | Erodono l'edge misurato; da verificare in demo prima di pagare |
| 6 | **Profit split** | Ultimo |

---

## 3. Griglia di verifica — da compilare sui RULEBOOK PRIMARI

Non sui comparatori. Se un dato non è pubblicato, si scrive **NON PRESENTE** e si chiede alla firm.

| # | Domanda | FTMO | FundedNext | The5ers | Alpha Capital | Altre |
|---|---|---|---|---|---|---|
| 1.1 | Daily DD su balance o equity flottante? | ❓ | ❓ | ❓ | ❓ | |
| 1.2 | Max DD statico o trailing? | statico | ❓ | statico | ❓ | |
| 1.3 | Weekend/overnight consentito? | ❓ (Swing account) | ❓ | ❓ | ✅ su Pro/Swing/One/Three | |
| 1.4 | EA MT5 senza sorgente? | ✅ senza pre-approvazione | ✅ MT4/MT5 | ✅ | ⚠️ **richiede `.mq5`** | |
| 1.5 | Consistency rule? | ❓ | ❓ | ❓ | ❌ **40% best day → SQUALIFICATA** (payout 14/28 gg: violeremmo il 74,7% delle volte) | |
| 1.5b | Se c'è: si calcola dall'ultimo payout o dall'intera storia? Accumulo libero? | ❓ | ❓ | ❓ | ❓ | |
| 1.6 | News: apertura e chiusura? | ⚠️ ±2min XAUUSD/DXY, **solo funded** | ⚠️ **−40% profitti news** + SL 3min | ⚠️ varia per piano | ❓ "news gambling" vietato (vago) | |
| 1.7 | Leva XAUUSD / NAS100 | ❓ | ⚠️ **XAUUSD 1:10** | ❓ | ❓ (1:30 su Swing) | |
| 1.8 | Italia + postura MiFID II | ❓ | ❓ | ❓ | ❓ | |

**Candidate da aggiungere alla griglia** (emerse come "no consistency rule + static DD + EA su MT5",
tutte da verificare sui rulebook primari, nessuna approvata): Goat Funded Trader, FXIFY, Atlas
Funded, Blueberry Funded.

---

## 4. Esclusione permanente: la traccia segnali-mentore

**Chiuso il 2026-08-07 dopo cinque verifiche indipendenti** (FTMO, FundedNext, The5ers, Alpha
Capital + ricerca trasversale sul settore).

La distinzione universale è **interno vs esterno**: copiare la *propria* strategia su *propri*
account è permesso quasi ovunque; abbonarsi a un signal service, farsi gestire l'account o collegare
un copier a un master esterno è vietato **anche in funded** — anzi, in funded è più severo, perché i
programmi funded richiedono esplicitamente decisioni di trading indipendenti.

**Perché non è aggirabile:** l'edge e il rischio di compliance sono **la stessa variabile**. Più si
segue il mentore meccanicamente, più l'edge funziona e più i trade diventano indistinguibili da
quelli di un copier. Il rilevamento avviene per **pattern identici tra account**, al **payout
review** — cioè si tradano mesi e i profitti vengono negati alla richiesta.

→ **L'edge mentore va operato su capitale proprio, o non va.** Riapertura solo con evidenza esterna
nuova ([STRATEGY_LIFECYCLE §7](STRATEGY_LIFECYCLE.md)).

---

## 5. Sequenza operativa

1. **Test consistency rule** sul trade log del backtest — l'unico lavoro prop eseguibile **ora**,
   senza toccare il forward.
2. **Compilare §3** sui rulebook primari (le caselle ❓). Dove il sito blocca l'accesso → prompt per
   Comet ([[feedback_comet_browser_handoff]]).
3. **Solo a valle di un GO**: shortlist finale, verifica delle condizioni di esecuzione in demo,
   scelta.
4. **Prima di scalare**: inquadramento fiscale (occasionale 26% vs abituale con partita IVA e
   forfettario) — vedi il backlog `FISCAL_SUPERVISOR_SPEC.md`.

> **Nessuna challenge si paga prima di un GO pre-registrato.** Pagare per far girare una strategia
> non validata è comprare biglietti della lotteria con passaggi extra.
