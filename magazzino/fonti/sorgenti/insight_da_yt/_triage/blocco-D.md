# Blocco D — i quattro rimasti (4 video, 58.082 parole)

Video non coperti dai blocchi A-C. Tre sono nuovi; il primo era gia' stato **parzialmente**
distillato il 14/08 (da li' vengono la spec Donchian e il claim del "playground" che hanno prodotto
il lead del 14/08), ma **non era mai stato letto per intero**. Leggerlo intero cambia il quadro,
quindi ha una scheda completa.

---

## D.1 — "20 years of institutional trading knowledge" (Pavel Kichev) · 9.598 parole

`_wpg45NdMkM` · 20 anni di attivita', **gestisce fondi per istituzionali e patrimoni privati con
strategie algoritmiche**. E' l'unico ospite del canale che non sia un trader retail scalato, e
l'unico che ragioni per **primi principi** invece che per setup.

> ⚠️ **Questo video e' la fonte del nostro lead del 14/08** (`project_trend_playground_lead_2026_08_14`).
> La distillazione precedente ne aveva estratto due passaggi. Il testo completo ne contiene molti
> altri, e alcuni **rispondono a domande che ci siamo posti dopo**.

### 1. Il framework economico — perche' l'edge sta dove sta

Tre relazioni dichiarate, tutte con la stessa causa:

| relazione | direzione | perche' |
|---|---|---|
| **Sharpe ratio vs timeframe** | timeframe alto -> Sharpe **piu' basso** | il capitale gira meno, i drawdown sono piu' lunghi |
| **liquidita' vs volatilita'** | piu' liquido -> **meno volatile** | il denaro intelligente affluisce dove puo' operare in size, e cosi' facendo comprime la volatilita' |
| **edge decay vs timeframe** | timeframe basso -> l'edge **decade piu' in fretta** | serve **meno capitale** per arbitrarlo via |

E la conclusione operativa che ne trae:

> *"Gli istituzionali sono pagati per massimizzare lo Sharpe. Quindi vanno dove lo Sharpe e' piu'
> alto: **timeframe bassi su mercati molto liquidi**. Quello e' il campo di battaglia
> sovraffollato. **Il posto del trader individuale e' dove il rapporto fra professionisti e retail
> e' piu' basso.**"*

Classifica esplicita dell'edge potenziale per il retail, dal peggiore al migliore:
**forex -> materie prime / grandi azioni -> small cap -> crypto**. Il criterio e' liquidita'
decrescente e volatilita' crescente. E il ciclo *immature -> mature*: un mercato nuovo e' illiquido
e volatile; man mano che matura diventa liquido e poco volatile — **ed e' quello il meccanismo
del decadimento dell'edge**.

### 2. L'argomento sui costi — il piu' importante e quello che avevamo perso

E' quantificato, ed e' l'unico calcolo esplicito di tutto il funnel:

> *"L'expectancy per trade cresce **in modo esponenziale** con il timeframe, mentre i costi
> restano costanti. Un breakout su crypto ha expectancy ~**1,5% su daily** e ~**0,4% su H1**. Il
> costo medio (slippage + commissioni) e' ~**0,2%**. Quindi su H1 i costi si mangiano il **50%**
> dell'edge; su daily meno del **15%**. E poiche' **l'edge decade** mentre i costi no, arrivi molto
> in fretta al punto in cui expectancy = costi."*

Da cui la regola che formula come conclusione principale:

> **"Piu' liquida e' la classe di attivi, piu' alto deve essere il timeframe su cui la operi."**

E la variante che ci riguarda direttamente: *"non importa se decidi sui dati a 5 minuti, quello che
conta e' quanto **tieni** la posizione"* — cioe' e' l'**holding time**, non il timeframe di
decisione, a determinare l'expectancy per trade.

### 3. I tre approcci — e la loro riduzione

Quattro famiglie: **arbitraggio**, **market making** (entrambi praticabili dal retail **solo** dove
la liquidita' e' cosi' bassa che gli istituzionali non ci stanno: crypto, small cap), **momentum**,
**mean reversion**. Poi la riduzione:

> *"Il trend e' **momentum di lungo periodo**, e il momentum di lungo periodo non e' altro che una
> catena di **momentum di breve seguito da mean reversion**. Puoi parlare di ICT, di Fibonacci, di
> quello che vuoi: **tutto e' costruito su queste tre cose.**"*

Con le **spec complete** di tutte e tre — e sono spec, non descrizioni:

- **breakout / momentum breve**: misurare l'**espansione di volatilita'** (la candela corrente si
  muove ~2x la media delle ultime 5). Uscita: dopo **X giorni** (il momentum breve su daily dura
  **2-5 giorni**) oppure quando il momentum svanisce;
- **mean reversion**: misurare la **distanza dalla media a 5 giorni**; se lo scostamento giornaliero
  e' molto superiore alla media (es. 6-7% contro 2%), tende a rientrare. Uscita: dopo **1-4 giorni**
  o al ritorno sulla media;
- **trend following**: rottura del **massimo a 100 giorni** (*"piu' lungo il periodo, meglio e';
  il massimo storico da' l'edge piu' forte"*), uscita alla **chiusura sotto la media a 10 giorni**.

⚠️ **Questa e' letteralmente la configurazione del nostro test del 14/08**: `analysis/trend/backtest.py`
usa `LOOKBACK=100, SMA_EXIT=10`. Il fatto che l'avessimo gia' presa da qui e' corretto; il fatto che
**anche le altre due spec fossero nello stesso video** era andato perso.

### 4. Il claim contro-consenso che nessun altro fa — ed e' testabile

> *"Il trader retail tende ad affidarsi alle **conferme**. Ma con la mean reversion, **piu' il
> mercato scende, piu' alta e' la probabilita' che entrando finisca in profitto**. Quindi se vuoi
> operare un rientro nel trend, e' meglio **non** aspettare la conferma: misura la correzione ed
> entra **mentre** avviene."*

⚠️ **Questo contraddice frontalmente il resto del funnel.** *"Aspetta la conferma, non anticipare"*
e' la convergenza piu' ripetuta di tutti i blocchi (sette formulazioni indipendenti fra A, B e C).
Kichev dice l'opposto — e lo dice **con una condizione**: vale per la **mean reversion**, non per il
momentum.

**E questo lo possiamo misurare.** E' esattamente la domanda che il nostro lead **FADE** (+0,31R)
pone senza rispondere: entriamo al tocco del livello o dopo un segnale di rientro? La differenza fra
le due e' misurabile sui dati che abbiamo gia', ed e' una **variante di esecuzione della stessa
regola**, non una famiglia nuova.

### 5. La mappa asset-approccio

| classe | cosa dice di operare |
|---|---|
| **grandi azioni / indici** | **solo** momentum di lungo (trend following) **long** + mean reversion **long**, su **daily o superiore** |
| **small cap** | anche momentum breve e mean reversion **short** — perche' sono inefficienti |
| **materie prime** | **tutti e tre** — *"non sono cosi' efficienti"* |
| **forex** | **solo** trend following o mean reversion, e **solo su timeframe alti** |
| **crypto** | tutti e tre |

E la nota finale: *"il momentum di lungo periodo funziona su tutte le classi — per questo lo
chiamano l'approccio piu' robusto in assoluto. E funziona **perche' il suo Sharpe e' basso**: il
denaro intelligente non e' concentrato li'."*

### 6. Portfolio trading = diversificazione **+ ribilanciamento**

L'ultima parte, mai distillata prima, e' un esempio numerico completo:

Due strategie **anticorrelate**, 10k ciascuna. Anno 1: +100% e −50% -> 20k + 5k = **25k**.
Anno 2: −50% e +100% -> 10k + 10k = **20k**. Risultato netto su due anni: **zero**.

Con **ribilanciamento** a fine anno 1 (25k -> 12,5k + 12,5k), anno 2: 6,25k + 25k = **31,25k**.
Stesse strategie, stessi rendimenti, **+56% di differenza dal solo ribilanciamento**.

> *"Il ribilanciamento e' **l'unico vero sacro graal** che abbiamo nel trading."*

E la conseguenza che rende tutto coerente: *"non devi affidarti a timeframe brevissimi per avere
stabilita'. Puoi uscire dal campo di battaglia affollato e andare dove l'edge e' piu' spesso e
l'expectancy piu' alta, e **recuperare lo Sharpe a livello di portafoglio**, combinando strategie
poco correlate."*

### Verdetto: **la fonte piu' importante dell'intero funnel** — e va trattata di conseguenza

Non e' un CANDIDATO perche' non e' una strategia: e' una **teoria su dove cercare**, e la stiamo
gia' usando. Ma la lettura integrale produce **quattro cose che non avevamo**:

1. **L'argomento sui costi e' quantificato** e spiega, meglio di quanto avessimo scritto noi,
   **perche' i nostri NO-GO intraday su FX erano prevedibili**: forex = massima liquidita', ORB e
   London Breakout = timeframe minimo. Secondo il suo framework e' **la cella peggiore della
   griglia**, e infatti e' dove abbiamo trovato NULL dopo NULL.
2. **Le altre due spec** (breakout come espansione di volatilita'; mean reversion come scostamento
   dalla media a 5 giorni, con uscita a tempo 1-4 giorni) sono **complete e testabili**, e non erano
   nel registro. La seconda in particolare e' **la forma canonica del nostro lead FADE**.
3. **Il claim "non aspettare la conferma sulla mean reversion"** e' falsificabile, contraddice sette
   fonti, e riguarda una scelta che dobbiamo comunque fare sul FADE.
4. **Il ribilanciamento di portafoglio** e' un moltiplicatore che non dipende da trovare un edge
   migliore — e ha un aggancio diretto con il pilastro investing.

⚠️ **Cautela obbligatoria**: e' comunque **una fonte sola**, e i suoi numeri (1,5% / 0,4% / 0,2%,
"2-5 giorni", "1-4 giorni") sono **dichiarati, non dimostrati**. Il fatto che il suo primo claim
abbia prodotto un lead misurato (rho +0,857) alza il prior su di lui, **non trasforma le sue
affermazioni in dati**. Ogni spec che prendiamo da qui va pre-registrata e testata come qualunque
altra, con baseline random.

---

## D.2 — "74% win rate order flow strategy" (Trader Yush) · 18.399 parole

`hvyf6frvCcA` · oltre 2 M $ di payout da prop firm, di cui 196.000 in un mese. **Era un trader ICT
senza un payout**, poi e' passato all'order flow. Opera **solo ES e NQ**, solo sessione di New York,
e chiude *"la maggior parte della giornata entro un'ora"*.

> Anche questo era **parzialmente** distillato il 14/08 (insieme a Kichev). La lettura integrale
> aggiunge la specifica completa.

### I quattro strumenti che compongono una zona di interesse

1. **livelli generati dal mercato**: massimo/minimo del giorno precedente (solo RTH), massimo/minimo
   overnight (21:00-9:29 EST), e un **ORB a 30 secondi** — preso, dice, dai tempi del floor;
2. **volume profile**: **value area** (dove si e' scambiato il 70%) e, soprattutto, i **low volume
   node**;
3. **big trades**: filtro a **75 lotti su NQ**, **200 su ES**, abbassati a 50/100 quando il book e'
   sottile (lo ha fatto ad aprile, durante i dazi);
4. **delta profile**: assorbimento e partecipanti intrappolati.

**Regola di composizione**: servono **almeno 2 dei 4** allineati nella stessa area. Se il prezzo non
ci torna, **non opera**. Target tipico **2R**.

**Due modelli, uno per regime:**

- **mercato in bilancio (chop)**: opera **i bordi** della value area, **mai il centro** — *"e' li'
  che i trader restano intrappolati"*;
- **mercato in trend**: opera i **pullback nei low volume node**.

### Verdetto: **NON TESTABILE** (big trades e delta richiedono tick/book)

Ma tre annotazioni che contano:

**1) Terza fonte indipendente sui LOW VOLUME NODE.** Dopo Carmine (C2.2) e Fabio (C4.3), Yush li
mette **fra i quattro pilastri** del suo metodo. Tre trader diversi, tre percorsi diversi, stesso
oggetto. ⚠️ E resta il fatto verificato in C2.2: `analysis/level_research/detectors.py` testa
**POC / VAH / VAL** — nodi ad **alto** volume — e **mai** i nodi a basso volume. La casella vuota
e' confermata da una terza fonte.

**2) "Non operare in mezzo al range" — ottava formulazione.** Qui in forma esplicitamente
regolamentata: bordi della value area si', centro no.

**3) Il suo percorso e' un dato.** *"Ero un trader ICT e non avevo mai ottenuto un payout."* E' la
seconda voce del funnel (dopo Marco Ascetoni, C2.4) che dichiara di aver **abbandonato** la famiglia
che i nostri 384 trial hanno trovato nulla. Non e' evidenza, ma e' coerente.

---

## D.3 — "Prop firm strategy with 65% win rate" (Okala) · 11.686 parole

`jsUTbjwpFVk` · oltre 5 M $ di payout, 3 M nel solo anno scorso, **operando dal telefono**.

### La strategia 80/20

Sul NASDAQ: opera i livelli che finiscono in **.80** e **.20** (es. 25.680, 25.620). Timeframe
**10 minuti** per la struttura e **200 secondi** per l'entrata (un terzo esatto del 10 minuti).
Ordini **limite** ai livelli, **stop fisso a 10 punti**, **primo TP a 15 punti**, poi stop a
break even e si lascia correre. Finestra: apertura di New York, evita l'ora di pranzo. Nessun
indicatore, nessun order flow.

Alla domanda su come ci sia arrivato: *"tempo davanti allo schermo — 6, 8, 12 ore al giorno, piu'
il market replay la sera"*.

### Verdetto: **GIA' TESTATO E CHIUSO — questa e' la fonte del nostro round grid**

Questo video era gia' distillato (`okala_80-20_nasdaq_ChartFanatics.md`) e ha prodotto **una delle
due sole pre-registrazioni da fonte esterna concesse nel trimestre**: il test sulla **griglia dei
numeri tondi .80/.20**. Esito: **NULL**.

Il fatto che stia qui, in fondo al funnel, e' l'esempio piu' pulito del ciclo che vogliamo:
affermazione da fonte esterna con curriculum forte (5 M $ di payout) -> pre-registrazione ->
test -> **NULL** -> famiglia chiusa. **Non va riaperto**, e il video integrale non aggiunge nulla
che lo giustifichi: la spec era gia' stata estratta correttamente.

⚠️ Vale pero' segnalare un dettaglio che il test copriva e la lettura integrale conferma: lui
stesso dice che **il livello non deve essere toccato esattamente** (*"se si ferma a 19,75 e reagisce,
il mercato non stava aspettando il numero"*). Cioe' la sua e' una regola **a zona con tolleranza
discrezionale**, non a prezzo — e la nostra ricerca sui livelli ha testato **anche** le zone con
tolleranza, trovando NULL robusto a 0,10 e 0,20. La copertura c'era.

---

# Consuntivo blocco D (4 video, 58.082 parole)

| # | fonte | esito |
|---|---|---|
| D.1 | Pavel Kichev — primi principi | **la fonte piu' importante del funnel** — 4 elementi nuovi |
| D.2 | Trader Yush — order flow su ES/NQ | NON TESTABILE — **terza conferma dei low volume node** |
| D.3 | Okala — 80/20 sul NASDAQ | **gia' testato: NULL, famiglia chiusa** |
| D.4 | Noel T — StrategyQuant / algo no-code | gia' distillato il 17/08 (vedi `_INTAKE.md` e DECISIONS 2026-08-17) |

Il blocco D contiene, di fatto, **l'inizio e la fine del funnel**: la fonte che ha prodotto l'unico
lead misurato (D.1) e la fonte che ha prodotto l'unico NULL pre-registrato da materiale esterno
(D.3). Che siano nello stesso canale, a poche settimane di distanza, e con curricula ugualmente
impressionanti, e' il promemoria piu' utile del blocco: **il curriculum non predice l'esito del
test.**
