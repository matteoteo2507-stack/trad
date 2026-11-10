# Sintesi del funnel Chart Fanatics — 45 video, ~608.000 parole

**Chiuso il 2026-08-22.** Tutti i 45 video del canale sono stati **letti per intero**, uno alla
volta, senza compressione automatica. Le schede per video stanno in `blocco-A1/A2/B1/B2/C1/C2/C3/C4/D.md`.
Questo documento e' il **consuntivo**: cosa ne esce, cosa NON ne esce, e cosa resta da decidere.

**Regola di lettura di questo file**: qui non c'e' nessuna proposta approvata. Ci sono **oggetti
identificati**, ordinati per quanto sono vicini a essere testabili, con i loro rischi scritti
accanto. Le decisioni si prendono nella discussione, non qui.

---

## 1. Il risultato in una riga

> **Su 45 video e 68 ore di materiale, zero strategie importabili. Cinque caselle vuote
> identificate nella nostra griglia, quattro conferme esterne indipendenti del lead che avevamo
> gia', e una lunga serie di riscontri che il nostro registro era gia' nel posto giusto.**

E' un esito **atteso e coerente col mandato**: `_INTAKE.md` dichiarava in anticipo che il canale
serve come *"segnalazione di punti da verificare"*, non come fonte di conoscenza — e che
l'uso primario e' il **layer operativo e di rischio**, non le strategie.

---

## 2. Dove sono finiti i 45 video

| esito | n. | nota |
|---|---|---|
| **famiglie gia' falsificate** (livelli/zone, FVG, order block, sweep, Fibonacci, numeri tondi, VWAP/POC, ORB, stagionalita') | **19** | la grande maggioranza del canale e' ICT/SMC in varianti |
| **non testabili coi nostri dati** (order flow: tick + book; oppure universo small cap USA) | **12** | 5 dei 6 video in diretta piu' Perez, Carmine ×2, Yush, Verma, Kyle |
| **reference** — utili sul metodo, sul rischio o come contesto, non come strategia | **11** | inclusi psicologia, corso opzioni, primi principi |
| **gia' testati dal repo** (pre-registrati -> NULL) | **1** | Okala 80/20 -> round grid, NULL |
| **gia' distillati in precedenza** | **2** | Kichev (parziale), Noel T. |

**Nessun video ha prodotto un CANDIDATO nuovo.** I 5 candidati che avevamo dai blocchi A/B restano
5; nessuno se ne aggiunge, e uno (Breunigstein, "estensione estrema -> inversione") **esce dal
funnel molto meglio specificato di come ci era entrato**.

---

## 3. La raccolta promessa: claim dichiarati contro misurati

`_INTAKE.md` prevedeva di raccogliere **ogni statistica dichiarata** lungo la strada, per avere a
fine funnel la distribuzione dei claim dell'ecosistema. Eccola.

### 3a. I claim alti (scartati per protocollo)

| fonte | claim | verificabilita' |
|---|---|---|
| Brando (B2.5) | *">80%"* sui livelli maggiori | nessun campione, esempi scelti a posteriori su 7 anni |
| Marius (C3.4) | **85-90%** sul parabolic short | ~20 occasioni/anno selezionate a mano, nessun baseline |
| Tanya (C1.2) | **70-80%** nelle giornate CPI | *"guarda il mio canale"* |
| Yush (D.2) | **74%** (nel titolo) | screenshot Discord |
| Okala (D.3) | **65-70%** (nel titolo) | nessuno |
| Fabio (C4.3) | **+20-30 punti** di win rate dal filtro di bilancio | nessun campione ne' metodo |

### 3b. I claim bassi — e sono i piu' interessanti

| fonte | claim | forma |
|---|---|---|
| Trader Mayne (C1.1) | *"sono fortunato se ne vinco meta'"*, min **2:1** | win rate basso + payoff, **vincolo d'ingresso** |
| Z (C1.5) | *"i trader d'elite stanno fra **50 e 55%**"* | esplicito, contro il proprio marketing |
| Desi (C2.1) | **~65%**, con **5-6 perdite di fila piu' volte l'anno** | numero **con la sua varianza** |
| Carmine (C2.2, C4.5) | **30-40%** certi mesi; **30-33%** con R:R 7-8:1 e rischio fisso | **i tre numeri insieme**: unico caso in cui il conto e' verificabile |
| Marius (C3.4) | **25-30%** sui suoi setup long — *"opero nel fallimento"* | coerente col payoff asimmetrico |
| Kyle (C3.5) | short **50-70%** a 1-2:1; long **20-40%** a 5-15:1 | descrive **due regimi di payoff distinti** |

### 3c. Il confronto con cio' che abbiamo misurato noi

| claim esterno | nostro misurato |
|---|---|
| NXT continuazione **60-70%** | **13,3%**, E[R] −0,44R, 14/14 anni e 6/6 asset negativi |
| VELTRIX **80-90%** | **~53%** per sessione (80% respinto, p=2e-26) |
| playbook Chart Fanatics **90%** | **~20%** (test di terzi) |
| Okala **65-70%** su griglia .80/.20 | **NULL** su 28.745 touch, diff +0,08 pt, CI [−0,56, +0,74] |
| Yush, confluenza *"almeno 2 strumenti"* | **conf=2 = NO-GO forward** (2026-07-05) |

⚠️ **La lettura corretta di questa tabella non e' "mentono tutti".** E':

1. **I claim alti non sono mai accompagnati dai numeri che servono per verificarli** (campione,
   periodo, baseline, taglia del rischio). I claim bassi spesso lo sono.
2. **Nei quattro casi in cui abbiamo potuto misurare, il claim alto e' collassato.** Quattro su
   quattro. Questo e' ora un **argomento riutilizzabile a ogni fonte nuova**, e vale piu' di
   qualunque singola strategia del canale.
3. **Le fonti che dichiarano win rate basso sono le stesse che descrivono meccanismi economici
   concreti** (Verma: diluizione e bag holder; Marius: riflessivita' e affollamento; Kichev:
   liquidita' e decadimento dell'edge). La correlazione fra *onesta' statistica* e *qualita' del
   razionale* e' la cosa piu' netta del funnel.

---

## 4. Cosa esce di NUOVO — cinque oggetti, in ordine di vicinanza al test

### 4.1 — Condizione di STRUTTURA sull'estensione estrema ⭐ *il piu' maturo*

**Due fonti indipendenti**, mercati e stili diversi, che si sono specificate a vicenda senza
essersi mai parlate:

| | Marius (C3.4, US Investing Championships +291%) | Kyle (C3.5, 7 M $ verificati) |
|---|---|---|
| forma richiesta | **2-4 candele enormi con ATR ampio**; scarta le "formiche" (tante candeline) | le candele devono **espandersi** salendo; se si contraggono e' negativo |
| volume | **volume piu' alto dell'anno** sul climax | volume **in espansione**; se cala, **non opera** |
| mai | **mai il primo giorno** | **mai un solo giorno verde** |
| invalidazione | finestra **2 giorni** | massimo **3 tentativi** |

**Perche' conta**: il nostro candidato "estensione estrema -> inversione" (Breunigstein) diceva
*quanto*; queste due fonti dicono **come**, e il "come" e' **misurabile sui nostri dati** —
servono solo range delle candele e volume. Nessun market cap, nessun order flow.

⚠️ **Vincoli non negoziabili se mai lo testassimo**: (a) le soglie assolute (200%, 100%, 80%) **non
sono trasferibili** e vanno normalizzate sulla volatilita' dello strumento; (b) serve un **baseline
random risk-matched** — e' esattamente il caso in cui il KILL delle escursioni del 14/08 e' nato
(soglie assolute passate 6/6 e 15/15, ribaltate dal random).

### 4.2 — Le due spec mancanti di Kichev ⭐ *la piu' economica*

Dalla lettura **integrale** di D.1 (prima ne avevamo estratte solo due parti) escono le altre due
specifiche complete, mai entrate nel registro:

- **breakout = espansione di volatilita'**: la candela corrente si muove ~2x la media delle ultime
  5. Uscita **a tempo** (il momentum breve su daily dura **2-5 giorni**) o quando il momentum svanisce.
- **mean reversion = scostamento dalla media a 5 giorni**: se lo scostamento giornaliero e' molto
  superiore alla media, tende a rientrare. Uscita **a tempo** (1-4 giorni) o al ritorno sulla media.

**Perche' conta**: la seconda e' **la forma canonica del nostro lead FADE** (+0,31R), scritta da
una fonte esterna, **prima** che noi la trovassimo, e senza aver visto i nostri dati. E' il tipo
di specifica che rende una regola data-derived **ri-pre-registrabile** — che e' esattamente il
problema aperto del FADE.

E l'uscita **a tempo** in entrambe converge col nostro test del 14/08: **l'uscita a tempo batte o
appaia il trailing** su 3 lookback.

### 4.3 — La domanda "conferma si' / conferma no" sul FADE ⭐ *decisione, non ricerca*

Kichev e' **l'unica voce del funnel** a dire di **non** aspettare la conferma su una mean
reversion (*"piu' il mercato scende, piu' alta e' la probabilita' che entrando finisca in
profitto"*) — contro **sette** formulazioni indipendenti del contrario.

Non e' una famiglia nuova: e' una **variante di esecuzione** di una regola che abbiamo gia', in
forward test, sui dati che abbiamo gia'. E' la differenza fra entrare al tocco del livello ed
entrare dopo un segnale di rientro.

⚠️ **Ed e' anche il conflitto gia' mappato in `_INTAKE.md`**: il claim di Kichev su *"entrare nel
ritracciamento"* e' gia' registrato come **falsificato dai nostri dati** il 14/08 (0/6 asset,
peggio del random) — ma su **continuazione**, non su fade. La condizione va tenuta: sono due cose
diverse e vanno separate per dominio, non arbitrate.

### 4.4 — Casella vuota verificata: i LOW VOLUME NODE

**Verificato nel codice**: `analysis/level_research/detectors.py:107-148` costruisce il volume
profile ed estrae **POC / VAH / VAL**; `VOLUME_CONCEPTS = ["poc", "vwap", "avwap"]`. La ricerca v2
(48 celle, NULL) ha testato i **nodi ad ALTO volume**. **I nodi a BASSO volume non sono mai stati
testati** — e non sono una variante, sono **l'ipotesi complementare con meccanismo opposto**:

- **HVN/POC** (testato, NULL): *"il prezzo reagisce dove si e' scambiato molto"*;
- **LVN** (mai testato): *"il prezzo attraversa in fretta dove si e' scambiato poco, e ci torna
  perche' li' e' rimasto ordine non eseguito"*.

**Tre fonti indipendenti** ci costruiscono sopra: Carmine (C2.2, e' la sua strategia principale,
300k$ in 3 mesi), Fabio (C4.3), Yush (D.2).

⚠️ **E qui il rischio e' esattamente il contrario di quanto sembra.** Il detector e' a **poche
righe** da quello del POC: il costo tecnico e' quasi nullo, ed **e' proprio questo che lo rende
pericoloso** — e' il "gia' che ci siamo" che il ciclo di vita chiama *"ritocchiamo e riproviamo"*.
La famiglia madre ha **384 trial di NULL**. Aggiungere una cella a una griglia gia' esplorata paga
la molteplicita' **dove non l'abbiamo contata**. Inoltre tutte e tre le fonti dicono che funziona
**solo con la conferma di flusso**, che non possiamo replicare: testeremmo una versione **amputata**,
dove un NULL non falsifica e un positivo non e' loro.

### 4.5 — Casella vuota: le trend line INCLINATE

I 384 trial hanno testato **solo livelli orizzontali** (swing S/R, PDH/PDL, numeri tondi, order
block, FVG, EQH/EQL, POC/VWAP). **Le rette inclinate non sono mai state testate**, e tre fonti ci
costruiscono sopra l'intero metodo: Crooks (A2.3, la rottura come cancello), Silfrain (B2.1,
l'ancoraggio della proiezione), Tori (B2.2, con criteri numerici espliciti — contatti, ampiezza
minima, fascia di tolleranza).

⚠️ **Ma il funnel non e' concorde**: Ariel (B2.4) le **rifiuta esplicitamente** e con la nostra
stessa motivazione — *"sono troppo soggettive: c'e' chi le disegna sui massimi degli stoppini, chi
sulle chiusure. Preferisco le orizzontali, dove posso dire: sopra e' buono, sotto e' cattivo."*
3 a favore, 1 contro **argomentato sulla falsificabilita'**. Il buco e' reale, il prior e' basso.

---

## 5. Cosa NON esce — due porte che restano chiuse, e va scritto adesso

### 5.1 — I livelli condizionati (al calendario macro, al regime, alla struttura)

Tre fonti sostengono che i livelli funzionano **a condizione che**: Brando (B2.5, serve un evento
macro in calendario), Tanya (C1.2, giorni con red folder si', senza no), Trader Mayne + Asselin
+ Ascetoni (C1.1/C1.4/C2.4, serve l'allineamento di timeframe alto e la meta' giusta del range).

⚠️ **Registrato come buco noto, NON come proposta.** Condizionare i livelli **moltiplica lo spazio
di ricerca** su una famiglia gia' falsificata con 384 trial, e il calendario macro e' il posto
**piu' affollato e piu' pubblico** del mercato — l'opposto esatto del playground. Riaprire richiede
**evidenza esterna nuova e quantitativa**; questi video sono aneddoti selezionati a posteriori.

### 5.2 — L'ORB

Andrea Cimbali (C4.6) afferma che l'ORB *"funziona da 20 anni"* sugli indici USA, con un razionale
economico **migliore del nostro** (flusso strutturale di acquisto + market maker che devono fornire
liquidita'). E' **esattamente** il nostro filone: `analysis/opening_range/`, apertura cash USA
09:30 ET, M5, 14,5 anni, NAS100 e SPX500 -> **NO-GO**.

⚠️ **Non riapre nulla**, per due motivi: (a) e' un'affermazione senza campione, periodo o baseline;
(b) lui opera l'ORB **con l'order flow sopra**, e lo dice (*"non ho bisogno di aspettare il breakout
per capire che i compratori hanno il controllo"*) — cioe' **sta operando qualcos'altro**.

**Ma il suo razionale merita di essere allegato al forward ORB gia' in corso**, come ipotesi
economica dichiarata: se il forward risulta positivo sappiamo gia' *perche'* potrebbe esserlo; se
risulta negativo abbiamo falsificato anche il meccanismo, non solo il pattern. **Costo zero,
nessuna decisione da prendere.**

---

## 6. Le conferme esterne del lavoro gia' fatto

Questa e' la sezione che il funnel ha prodotto in modo piu' abbondante, e la piu' facile da
sottovalutare.

### 6.1 — Il lead del playground riceve QUATTRO gambe indipendenti

| fonte | formulazione | credenziale |
|---|---|---|
| **noi (misurato 14/08)** | **rho = +0,857, p=0,006** fra volatilita' di gruppo ed E[R] su 8 gruppi | il **nostro** dato |
| Kichev (D.1) | forex -> commodities -> small cap -> crypto, per liquidita' decrescente | gestore algoritmico istituzionale, 20 anni |
| Desi (C2.1) | *"funziona solo nei pochi mesi in cui il VIX e' alto — e allora funzionano tutte le sessioni"* | 900k$ in un payout |
| Carmine (C4.2) | *"opero dove non c'e' molta liquidita', e' li' che sta l'edge"* | 7 figure verificate |
| Fabio (C4.3) | *"il breakout fallisce **dentro** la balance area e funziona **fuori**"* | **top 3 Robbins Cup, +500%/12 mesi** |

Quattro vocabolari diversi (classe di attivi / mese / strumento / stato d'asta), **una sola forma**:
dove c'e' meno partecipazione efficiente, c'e' piu' da prendere. **Nessuna delle quattro e'
evidenza statistica.** Ma spostano il **prior** su quale sia la domanda giusta, e la nostra e'
l'unica con un numero.

### 6.2 — Le fonti convergono sul FADE, mai sulla continuazione

Quattro fonti del blocco C (Asselin C1.4, Ascetoni C2.4, Kane C3.2, Jadecap C3.3) descrivono
meccanismi che coincidono con la direzione che **abbiamo misurato positiva** (+0,31R). L'unica che
descrive la continuazione — Omar (C2.3) — descrive, **livello per livello (0,62 / 0,705 / 0,79)**,
la strategia che abbiamo misurato a **−0,44R** su 6 asset e 14 anni.

Non e' evidenza. Ma e' una coincidenza sistematica fra cio' che il mercato racconta e cio' che
abbiamo misurato, ed e' il pattern piu' netto dell'intero funnel.

### 6.3 — Altri riscontri diretti

- **Uscita a tempo > trailing**: Fabio (C4.3) — *"piu' cerchi di andare oltre l'ATR giornaliero,
  piu' la probabilita' si abbassa"*. Converge col nostro test del 14/08 e col KILL delle escursioni.
- **Costi vs timeframe**: Kichev quantifica perche' **i nostri NO-GO intraday su FX erano
  prevedibili** — forex = massima liquidita', ORB/London Breakout = timeframe minimo = la cella
  peggiore della sua griglia. Abbiamo trovato NULL dopo NULL esattamente li'.
- **Larghezza dello stop**: Verma (B2.3, small cap: gli stop stretti **sono** la liquidita' cercata)
  e Desi (C2.1, futures: *"lascia che sia il grafico a invalidare, non il tuo P&L — riduci la size,
  non lo stop"*). Converge col nostro **12,7% di stop NXT che aprono oltre il livello**.
  ⚠️ **Correzione al conteggio**: sono **2-3 fonti indipendenti, non 5-6** — tre delle occorrenze
  erano trader di opzioni che descrivevano la **stessa** causa (la non-linearita' del premio,
  spiegata in C3.1), non tre osservazioni distinte.
- **Il regime di payoff e' vincolato dalla struttura di finanziamento**: i trader che vivono su prop
  firm tendono **tutti** verso alto win rate / basso R, perche' e' l'unico compatibile con le
  consistency rule. Conferma dall'esterno cio' che `PROP_FIRM_CRITERIA.md` aveva gia' isolato
  (payoff 1:3 + payout bi-settimanale + consistency 40% = incompatibili).
- **La psicologia (C2.5) e' un argomento a favore della nostra architettura**, non del metodo: tilt,
  revenge trading e FOMO sono il costo di **decidere in tempo reale**. Le nostre decisioni stanno
  fuori dal mercato aperto. ⚠️ Con **due eccezioni**: la tentazione di riaprire una famiglia chiusa
  (revenge trading applicato alla ricerca — ed e' precisamente cio' che il ciclo di vita impedisce)
  e la copia **manuale** dei segnali mentore.

### 6.4 — Il ribilanciamento di portafoglio

Kichev (D.1) porta un esempio numerico completo: due strategie anticorrelate, senza ribilanciamento
finiscono a 20k dopo due anni; **con** ribilanciamento annuale a 31,25k. Stesse strategie, stessi
rendimenti, **+56% dal solo ribilanciamento**. *"E' l'unico vero sacro graal che abbiamo."*

E la conseguenza che chiude il cerchio con il resto: **non serve un timeframe basso per avere
stabilita'** — si puo' stare dove l'edge e' piu' spesso e recuperare lo Sharpe **a livello di
portafoglio**. E' gia' coperto in `[[05_portfolio_rischio]]`, ma **come teoria, non come pratica**:
oggi non abbiamo un livello di portafoglio.

---

## 7. Il quadro per la discussione: binari attivi e binari candidati

### 7a. Cosa e' gia' in moto

| binario | stato | il funnel lo tocca? |
|---|---|---|
| **FADE NXT** — forward test pre-registrato | in corso | si': §4.2 (spec canonica esterna), §4.3 (variante di esecuzione), §6.2 (4 conferme di direzione) |
| **ORB v2** — forward test | in corso | si': §5.2 (razionale economico da allegare, costo zero) |
| **Copier segnali mentore** — demo verso live | pre-registrazione esecuzione fatta, guida VPS fatta | marginalmente: §6.3 (la copia manuale e' l'unico punto dove il tilt ha superficie) |
| **PAC / pilastro investing** — parte fine settembre 2026 | 1.200 EUR da vincolare a settembre | si': §6.4 (ribilanciamento) e Z (C1.5) — conferma esterna della separazione dei pilastri |
| **Audit risultati early-stage** | in coda, richiesto dall'utente | indirettamente: il funnel ha gia' verificato nel codice due coperture (LVN, tolleranze) |

### 7b. Cosa il funnel mette sul tavolo — **da discutere, non deciso**

Ordinati per **rapporto valore/rischio**, non per attrattiva:

| # | oggetto | natura | costo trial | rischio principale |
|---|---|---|---|---|
| **1** | Allegare il razionale Cimbali al forward ORB | annotazione | **zero** | nessuno |
| **2** | Misura descrittiva: condizione di struttura (espansione range + volume) sull'estensione estrema | **misura**, non regola | **zero** (come le escursioni) | trasformarla in regola senza accorgersene |
| **3** | Variante di esecuzione del FADE: conferma si' / conferma no | variante su lead esistente | **basso** (stessa famiglia) | e' comunque un round di rifinitura: contarlo |
| **4** | Pre-registrazione seria del **playground** con holdout | il lead che abbiamo | **1 pre-reg** | 3/8 gruppi, n=8, nessun holdout: e' il punto debole noto |
| **5** | Casella **LVN** | famiglia chiusa + 1 cella | **1 pre-reg** | molteplicita' non contata; versione amputata; il "gia' che ci siamo" |
| **6** | Casella **trend line inclinate** | famiglia chiusa + 1 cella | **1 pre-reg** | prior basso, 1 fonte su 4 le rifiuta con la nostra motivazione |
| **7** | Livello di **portafoglio + ribilanciamento** | architettura, non edge | **zero** | serve piu' di una strategia viva per avere senso |

⚠️ **Vincoli di budget da tenere presenti nella discussione**: il budget di pre-registrazioni da
fonte esterna e' **2 su 2-3 gia' speso nel trimestre** (round grid .80/.20, trend/playground).
Gli oggetti #5 e #6 sono **entrambi** pre-registrazioni esterne. Gli oggetti #1, #2 e #7 non lo sono.

### 7c. Le tre domande a cui la discussione deve rispondere

1. **Quanti binari in parallelo regge davvero il lavoro?** Ce ne sono gia' 4 attivi piu' l'audit in
   coda. Aggiungerne non e' gratis: ogni ipotesi in piu' **alza la soglia DSR per tutte**.
2. **Il playground si pre-registra adesso o dopo l'audit?** E' il lead migliore che abbiamo e il
   funnel gli ha appena dato quattro conferme esterne — ma il suo punto debole (n=8, niente
   holdout) e' esattamente il tipo di cosa che l'audit sui risultati early-stage dovrebbe
   insegnarci a non ripetere.
3. **Le due caselle vuote (LVN, trend line) si aprono, si chiudono, o si parcheggiano?** Sono reali,
   sono a costo tecnico quasi nullo, e **proprio per questo** sono il caso da manuale che il ciclo
   di vita esiste per fermare. La domanda non e' *"si puo' fare"* — e' *"cosa ci compra e cosa ci
   costa in molteplicita'"*.

---

## 8. Cosa NON fare, deciso adesso

- **Non** riaprire livelli, numeri tondi, Fibonacci, ORB, stagionalita' sulla base di questo funnel.
  Nessuno dei 45 video porta evidenza esterna nuova nel senso richiesto dal ciclo di vita.
- **Non** importare nessuna statistica dichiarata nel prior. Quattro su quattro sono collassate
  quando le abbiamo misurate.
- **Non** trattare le quattro conferme del playground come evidenza statistica: spostano il prior,
  non i dati.
- **Non** far ripartire il funnel su altri canali prima che i binari attuali abbiano prodotto un
  verdetto. Il tetto era **1 pre-registrazione** dal funnel; ne abbiamo speso 1 (playground) e ne
  abbiamo prodotta 1 in precedenza (round grid). **Il funnel e' chiuso.**

---

## 9. Appendice — video usciti DOPO la chiusura (aggiornata 2026-08-23)

Il funnel e' chiuso, ma il canale continua a pubblicare. I video successivi al 22/08 stanno in
[`blocco-E-postfunnel.md`](blocco-E-postfunnel.md).

⚠️ **Questione di processo, aperta.** "Funnel chiuso" significava *non rileggiamo l'arretrato di
altri canali*: non era stata scritta una regola per i **video nuovi dello stesso canale**. Vanno
decise due cose — (a) li leggiamo tutti, a campione, o solo su segnalazione? (b) contano contro il
tetto di **1 pre-registrazione** del funnel, gia' speso? Finche' non e' deciso, ogni video nuovo e'
**segnalazione**, non intake corrente.

**E.1 — Freddy Siento, market maker (23/08, 26.718 parole, il piu' lungo del canale).**
**NON TESTABILE** (serve catena opzioni + superficie di volatilita' implicita intraday, piu' un
abbonamento vendor), **zero pre-registrazioni aperte**, ma:

- porta **il razionale economico piu' forte dei 46 video**: la copertura delta/gamma del market
  maker e' un **obbligo**, non una scelta, ed e' meccanica verificabile indipendentemente. E'
  l'unico caso del funnel che avrebbe passato a pieni voti il gate del razionale (§6a);
- **seconda voce con esperienza di market making** (dopo Cimbali) a smentire lo *stop-hunting* —
  coerente col nostro NULL sui livelli;
- **fornisce il meccanismo mancante ai low volume node** (§4.4 / backlog B5): i picchi di
  volatilita' implicita sono i nodi ad alto volume, le tasche quelli a basso. Non cambia il
  verdetto su B5, ma spiega *perche'* tre fonti ci costruiscono sopra;
- ⚠️ **le sue statistiche sono internamente incoerenti**, e si smonta senza avere alcun dato:
  dichiara **75% di win rate** e insieme *"uno stop ogni due o tre settimane"* con **1-2 occasioni
  al giorno** — che implica un win rate del **90-97%**. I due numeri differiscono di un fattore
  3-10. Track record dei claim del funnel: **5 su 5** privi di campione, periodo, baseline e
  taglia del rischio;
- **conflitto dichiarato**: sconto 65% sulla piattaforma vendor indispensabile al metodo;
- **effetto operativo, a costo zero**: e' il **secondo meccanismo in due giorni** proposto per
  l'intraday sugli indici USA, cioe' il perimetro del nostro NO-GO ORB — e piu' preciso di quello
  di Cimbali. ⚠️ **Non riapre nulla** (la coincidenza fra 0DTE dal 2021 e ORB "meno negativo"
  post-2020 e' esattamente il tipo di lettura che
  [[feedback_backtest_long_history_falsification]] vieta di fare sul backtest che l'ha generata).
  Va **allegato al forward ORB gia' in corso** insieme a quello di Cimbali: due ipotesi dichiarate
  prima dell'esito invece di una.
