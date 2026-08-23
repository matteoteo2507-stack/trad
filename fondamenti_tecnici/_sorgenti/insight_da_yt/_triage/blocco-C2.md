# Blocco C2 — ICT applicato / mentale (5 video, 80.738 parole)

---

## C2.1 — "If you only watch one ICT video" (Desi Trades) · 15.747 parole

`UIGZtoGGPH4` · ~2 M di payout da prop firm, di cui **900.000 $ in un solo payout** su Apex in
25 giorni. Opera solo **NQ ed ES**.

### Il modello: cascata di inversioni su timeframe annidati

1. **daily**: sweep di un massimo/minimo di riferimento (preferisce massimi/minimi **mensili**);
2. **4 ore**: il gap creato nella spinta viene **attraversato senza essere rispettato** ->
   inversione. Vincolo temporale: deve invertirsi **entro 2-3 candele**, con velocita'.
   *"Se il prezzo resta troppo a lungo nello stesso gap, il setup perde probabilita'"*;
3. **15 min**: si aspetta il ritracciamento dentro il gap ribassista creato nella discesa;
4. **1-5 min**: si aspetta che il gap rialzista formato nel ritracciamento venga a sua volta
   invertito -> **quella e' l'entrata**;
5. **stop** sopra il massimo di 15 min; **TP1** su un gap non riempito, **meta' posizione**, stop a
   BE, il resto come runner. R iniziale 1:1,5-1:2, i runner portano a 1:5-1:10.

**Regole dure**: due perdite e la giornata e' finita (se vince-perde, si concede un terzo tentativo);
non media mai al rialzo; non insegue se salta l'entrata, aspetta la candela 4h successiva.

### Verdetto: **SCARTATO** — famiglia CLOSED, in forma piu' annidata

E' la stessa famiglia dei 384 trial (gap/FVG, order block, sweep, market structure), qui impilata su
quattro timeframe. L'annidamento **non aggiunge una famiglia nuova**: aggiunge condizioni. E dichiara
lui stesso il costo: *"chiedi a 10 trader ICT nella stessa stanza e prendono 10 entrate diverse — ed
e' la parte bella di ICT"*. Dal nostro punto di vista **e' l'esatto contrario di una parte bella**:
significa che il modello non ha una specificazione unica, quindi non e' pre-registrabile e
qualunque esito puo' essere attribuito alla variante.

### Ma qui c'e' la convergenza piu' forte di tutto il funnel con un NOSTRO dato

Alla domanda "quanto spesso si presenta", risponde:

> *"Solo pochi mesi l'anno sono davvero ad alta probabilita', e sono quelli in cui il **VIX e'
> alto**. Ricordi com'e' stata brutta l'estate? Il VIX era piatto, non ci siamo mossi per tutta
> l'estate. Quando la volatilita' e' su, **funzionano tutte le sessioni** — Asia, Londra, New York.
> Se sta succedendo tutto questo e il mercato si muove di 10 punti, non e' alta probabilita'."*

E il suo payout record e' esplicitamente attribuito a un periodo di volatilita' elevata al ribasso
(novembre, poi le notizie sui dazi).

⚠️ **Questo e' la terza gamba di una convergenza che include un nostro numero misurato:**

| fonte | forma dell'affermazione |
|---|---|
| **noi**, test trend/playground 14/08 | **rho = +0,857 (p=0,006)** fra volatilita' di gruppo ed E[R] su 8 gruppi di strumenti |
| Tanya Trades (C1.2) | il regime tradabile e' prevedibile **dal calendario** (eventi = distribuzione, niente eventi = accumulazione) |
| Desi Trades (C2.1) | il regime tradabile e' identificato **dal VIX**: pochi mesi l'anno, e in quei mesi **tutte le sessioni** funzionano |

Le tre affermazioni non sono la stessa cosa, ma puntano tutte nella stessa direzione: **la
volatilita' non e' un fastidio da filtrare, e' la variabile che decide se esiste qualcosa da
prendere.** La differenza cruciale e' che **noi l'abbiamo misurata** e loro la raccontano.

Questo **rafforza il lead del playground** invece di aprirne uno nuovo: la nostra correlazione fra
volatilita' di gruppo ed E[R] riceve due conferme esterne qualitative, indipendenti fra loro e da
noi, su mercati diversi. Non e' evidenza statistica aggiuntiva — sono aneddoti — ma sposta il
**prior** su quale sia la domanda giusta da porre al prossimo test.

### Altre due annotazioni

**Stop largo, quarta occorrenza.** *"Le persone hanno stop troppo stretti, si fanno prendere per 20
punti e poi il prezzo va nella loro direzione. **Lascia che sia il grafico a invalidare, non il tuo
P&L** — e per farlo riduci la size, non lo stop."* E' la stessa cosa detta da Verma (B2.3), Brando
(B2.5) e implicitamente da Ariel (B2.4), qui con la formulazione operativa migliore: **lo stop lo
detta la struttura, la size assorbe la differenza.**

**Win rate dichiarato con le perdite.** *"Circa 65%. Perdere 5-6 trade di fila non e' affatto raro,
mi succede piu' volte l'anno."* Terza fonte del funnel a dichiarare un numero **con** la sua
varianza invece che un claim liscio all'80-90%.

---

## C2.2 — "Real fair value gaps" (Carmine Rosato) · 15.795 parole

`jHsD2-2K_Kk` · fondatore di Investor Trade, order flow su ES. La strategia si chiama
**LVN — low volume node**, e ha dichiarato oltre 300.000 $ in 3 mesi con questa sola.

### Il modello

Volume **per prezzo**, non per tempo (*"non m'importa se qualcuno ha comprato a marzo o a giugno:
m'importa a QUALE PREZZO la gente e' disposta a comprare, e quanto"*). Cinque passi:

1. identificare una zona di **domanda/offerta** = consolidamento che precede un movimento impulsivo;
2. aspettare che il prezzo **torni** su quella zona e la **rifiuti** con forza — serve a dimostrare
   che i compratori/venditori sono davvero li'. **Non entra qui**;
3. su quel movimento impulsivo di rifiuto, cercare nel profilo di volume le fasce in cui **si e'
   scambiato pochissimo** (**LVN**): sono nate proprio perche' il movimento e' stato cosi' violento
   che molti ordini non si sono riempiti;
4. aspettare il **ritorno** su quella fascia a basso volume;
5. entrare **solo con conferma** dal flusso (venditori/compratori aggressivi visibili).

Stop stretto sotto/sopra l'estremo, target su minimo/massimo di giornata. R:R dichiarati 4,5-5,5:1,
con **rischio in dollari fisso** (3.500-4.500 $) e **size variabile**: entrata migliore -> stop piu'
vicino -> piu' contratti a parita' di rischio.

### La sua affermazione piu' interessante: **"il fair value gap E' un LVN"**

> *"Nel mondo ICT mi dicono che sto solo facendo trading su un fair value gap. Il punto e' che
> QUESTO e' il motivo per cui i fair value gap si formano. Il gap e' un pattern sul grafico a
> candele; questo e' la meccanica d'asta sottostante."*

E lo mostra: sovrappone il proprio LVN al grafico a candele e il FVG che un trader ICT
disegnerebbe **coincide con la fascia a basso volume**. Se ha ragione — ed e' plausibile,
perche' entrambi nascono dallo stesso evento (movimento troppo veloce perche' tutti si riempiano) —
allora **due delle nostre famiglie chiuse sono la stessa famiglia vista da due lati**.

### Verdetto: **SCARTATO come strategia** (serve order flow) — ma isola **un buco verificato**

Non e' replicabile: i passi 2 e 5 richiedono heat map, footprint, delta cumulativo, bolle di volume
aggressivo. Stessa etichetta di Perez (C1.3).

⚠️ **Ma il passo 3 non richiede il book — richiede solo un profilo di volume. E l'ho verificato:**

`analysis/level_research/detectors.py:107-148` costruisce il volume profile e ne estrae **POC, VAH,
VAL**; `VOLUME_CONCEPTS = ["poc", "vwap", "avwap"]`. Cioe' la ricerca v2 (48 celle, esito NULL) ha
testato i **nodi ad ALTO volume** e i **confini della value area**. **I nodi a BASSO volume non
sono mai stati testati.**

E non e' una variante della stessa ipotesi: e' **l'ipotesi complementare, con un meccanismo
opposto**.

- **HVN / POC** (testato, NULL): *"il prezzo reagisce dove si e' scambiato molto"*.
- **LVN** (mai testato): *"il prezzo attraversa velocemente dove si e' scambiato poco, e ci torna
  perche' li' e' rimasto ordine non eseguito"*.

Nella nostra griglia, quindi, **non e' coperto dal NULL dei livelli**: e' una casella vuota
accanto a caselle piene. Come le trend line inclinate (B2.2).

**Cio' che va scritto subito, prima che sembri una proposta:**

- il detector esiste gia' ed e' a **poche righe di distanza** da quello del POC — il costo tecnico
  di misurarlo e' quasi nullo, ed e' esattamente questo che rende la cosa **pericolosa**: e' il
  classico "gia' che ci siamo" che il ciclo di vita chiama *"ritocchiamo e riproviamo"*;
- la famiglia madre ha **384 trial di NULL**. Aggiungere una cella a una griglia gia' esplorata
  paga la molteplicita' **dove non l'abbiamo contata**;
- il razionale economico di Carmine e' **il migliore del blocco C** (asta, ordini non riempiti,
  non psicologia), ma il suo funzionamento **dipende per sua stessa ammissione dalla conferma di
  flusso**, che noi non possiamo replicare. Testare il solo passo 3 significa testare una versione
  **amputata** della sua strategia: un NULL non lo falsificherebbe, e un positivo non sarebbe suo.

**Registrato come casella vuota identificata e verificata nel codice, insieme alle trend line
inclinate. Non e' una proposta: e' materiale per la discussione sui binari.**

### Nota di onesta' statistica, quarta occorrenza

*"Il mio win rate certi mesi e' il 30-40%. Non ho bisogno di un win rate alto perche' ho il
rapporto rischio/rendimento."* Piu' la regola di sizing corretta (**rischio fisso in valuta, size
derivata dalla distanza dello stop**), che e' la stessa cosa che dice Desi (C2.1) al contrario:
**lo stop lo detta la struttura, la size assorbe.** Quinta fonte convergente su questo punto.

---

## C2.3 — "Easy ICT strategy for prop firms" (Omar / MBB Trader) · 15.853 parole

`IB-fyWI5j8w` · oltre 30 M di funding fra i trader che ha formato, 1,1 M di payout propri.
Divide esplicitamente **framework** (dove aspettarsi il setup) da **entry model** (come entrare).

### Il framework: market maker model / power of three

Si aspetta la sequenza **accumulazione -> manipolazione -> distribuzione** e opera **solo la
distribuzione**. Ancorata a livelli di timeframe alto (massimi/minimi del giorno o della settimana
precedente, PDA su 4h minimo — *"sotto le 4 ore c'e' solo varianza"*). Conferma: **breaker block**
con displacement e chiusura di corpo su 15 min. Bias giornaliero **predeterminato**: senza bias non
si sa quale lato sia manipolazione e quale distribuzione.

### L'entry model: **optimal trade entry = ritracciamento di Fibonacci**

E lo dice apertamente: *"e' letteralmente il golden fib, non c'e' differenza"*. Livelli **0,62 /
0,705 / 0,79**, stop a 1,0, TP a 0,0.

L'unica osservazione originale e' aritmetica e **corretta**: poiche' entrata, stop e target sono
tutti frazioni fisse dello stesso range, **il rapporto R:R e' costante indipendentemente
dall'ampiezza del range** — 1,63R dal 62, ~2,38R dal 705, ~3,7R dal 79. Piu' una raffinatura: usare
**0,9** invece di 1,0 come stop, sostenendo che la probabilita' che il prezzo tocchi il 90% del
ritracciamento **senza** toccare il 100% e' *"meno del 10%, tipo 1 su 15"*.

### Verdetto: **SCARTATO — e' letteralmente la strategia che abbiamo gia' ucciso**

Questo non e' "famiglia chiusa in senso lato". E' **la stessa specifica** del NO-GO NXT del
2026-07-17:

| elemento | Omar (questo video) | NXT (nostro test pre-registrato) |
|---|---|---|
| direzione | bias di timeframe alto | trend/continuazione su timeframe alto |
| entrata | ritracciamento Fib **0,62 / 0,705 / 0,79** | ritracciamento Fib, stessi livelli |
| stop | oltre l'estremo dello swing (1,0, o 0,9 raffinato) | oltre l'estremo dello swing; **testato anche wide** |
| target | estremo opposto del range | estremo opposto |

Il nostro esito, su **6 asset H1 per ~14 anni, pre-registrato**: win rate **13,3%** contro il
60-70% dichiarato dalla fonte originale, **E[R] = −0,44R**, negativo in **14 anni su 14** e in
**6 asset su 6**, e **lo stop largo non lo salva**.

E c'e' di piu': il **sottoprodotto** di quel test — il **FADE**, cioe' prendere il lato **opposto**
del ritracciamento — e' l'unica cosa che sia venuta fuori positiva (**+0,31R**, robusta a holdout e
3x costi). Cioe' abbiamo misurato che, su quei dati, **la direzione giusta e' il contrario di
quella che Omar insegna**.

⚠️ **Il claim aritmetico sul R:R fisso e' vero e irrilevante.** Un R:R costante non dice nulla sul
valore atteso: se il win rate e' 13%, un 2,38R fisso resta un E[R] negativo. E' esattamente la
confusione che il repo ha gia' isolato: **payoff garantito != edge**. Omar arriva a costruirci
sopra un piano di superamento delle challenge (*"1,5% di rischio, tre di questi setup di fila e
hai passato la fase 1"*) che dipende interamente da un win rate **mai misurato**.

**Valore di questo video per noi**: e' la **conferma piu' netta che il nostro lavoro serve**. Una
fonte con 30 M di funding dichiarato insegna, come cosa piu' facile del mondo, una strategia che
abbiamo falsificato su 14 anni con un protocollo pre-registrato — e nel farlo ne descrive
esattamente i livelli. Il registro va lasciato dov'e'.

---

## C2.4 — "Liquidity trap strategy" (Marco Ascetoni) · 21.420 parole (il piu' lungo del canale)

`DAnXM7C16h0` · centinaia di migliaia in payout, milioni in funding. Include una sessione di
**trading in diretta** con esecuzione reale su quattro conti.

### Il modello

Riduce tutto a una sola regola di lettura: **massimo che rispetta massimi precedenti + allontanamento
= liquidita' sopra quel massimo** (e simmetricamente per i minimi). Da li':

- si compra **solo sotto i minimi**, si vende **solo sopra i massimi**, mai al centro;
- i concetti retail (order block, FVG, BOS, Fibonacci, supporti/resistenze) **non vengono negati**:
  vengono usati come **mappa di dove stanno gli stop altrui**. *"Perche' non li opero se in
  qualche modo funzionano? Funzionano temporaneamente, e funzionano apposta: servono a costruire
  liquidita'."*
- **regola di invalidazione dura** (l'unica pulita di tutto il blocco C): *"se sto cercando un
  acquisto e il prezzo sale prendendo dei massimi, **non compro quell'asset finche' quel minimo non
  viene preso**. Non importa cosa succede in mezzo. Se il mercato scende e riparte senza di me, non
  era un movimento in cui dovevo essere."*

### Verdetto: **SCARTATO** — stessa cella di C1.4, con la stessa risposta

E' il modello DaVinci di Marco Asselin (C1.4) con un nome diverso: livello a contatti multipli ->
sweep -> entrata dal lato opposto. E' **una delle celle dei 384 trial** (zone + multi-touch, EQH/EQL)
e la parte potenzialmente valida — il rientro dopo l'estensione — **e' gia' il nostro lead FADE a
+0,31R**, misurato con costi e holdout.

### Le due cose che merita di essere annotate

**1) La sua tesi sui concetti retail e' esattamente la nostra conclusione, capovolta.**

Noi abbiamo misurato che i livelli **non sono zone di reazione** (384 trial, NULL). Lui dice che i
livelli **sono reali ma nel senso opposto**: non sono dove il prezzo reagisce, sono **dove stanno
gli stop**, quindi dove il prezzo va a prenderli. E' l'unica riformulazione, in tutto il funnel,
che sia **compatibile** con il nostro NULL invece di contraddirlo.

⚠️ E anche questo, pero', ha gia' la sua misura nel repo: se i livelli fossero davvero magneti per
gli stop, il **fade** (prendere il lato opposto dopo l'estensione) dovrebbe funzionare — **e in
effetti funziona, +0,31R**, ma **debolmente**, ed e' data-derived, quindi in forward test.
Cioe' abbiamo gia' misurato la sua tesi, e il risultato e' *"si', un po'"*, non *"si', enormemente"*.

**2) La regola di invalidazione e' l'unica pre-registrabile del blocco C.**

*"Non compro finche' quel minimo non e' preso, punto"* e' una condizione binaria, verificabile su
dati storici, senza spazio interpretativo. Confrontala con Asselin (C1.4: *"aspetto che si
ripeta"*), Mayne (C1.1: *"non tutti funzionano"*) e Z (C1.5: *"la storia era un'altra"*).
**Una fonte su dieci del blocco C ha scritto una regola che potrebbe essere falsificata.**
Non basta a renderla interessante — la cella e' gia' testata — ma vale come promemoria di cosa
distingue una regola da una narrazione.

---

## C2.5 — "Master the mental game" (Jared Tendler) · 11.923 parole

`8HxT9WQ-uD0` · psicologo della performance, autore di *The Mental Game of Trading*. Primo e unico
ospite del canale che **non sia un trader**.

### Il contenuto

Legge di **Yerkes-Dodson** (1908): la performance in funzione dell'attivazione emotiva e' una U
rovesciata. Zero emozione = nessuna energia per il lobo frontale = prestazione scadente; troppa
emozione = spegnimento progressivo delle funzioni superiori. Il punto non ovvio: **la parte del
cervello che controlla le emozioni e' la stessa che si spegne quando le emozioni salgono** — per
questo il degrado si autoalimenta.

Il livello ~80 e' il peggiore: resta abbastanza consapevolezza per sapere che si sta sbagliando, ma
non abbastanza controllo per fermarsi. *"E' come essere in un'auto che va giu' da un dirupo e non
riuscire a frenare."*

**Memoria di lavoro**: 5-9 elementi. In stato ottimale si espande (8-9) e li' vive l'intuizione; in
stato compromesso si restringe **e una parte viene consumata dalla difesa** — cioe' dal tentativo di
controllarsi. Da qui la funzione del journaling: **non e' introspezione, e' scaricare il carico
dalla memoria di lavoro**, come posare i pezzi del puzzle sul tavolo invece di tenerli in mano.

Protocollo: definire per iscritto com'e' la propria "zona"; mappare **trigger, pensieri, emozioni,
comportamenti fisici, percezioni** a ogni livello di intensita'; riconoscerli in tempo reale.
Avvertenza esplicita: **non confondere correlazione e causa** (*"porto a spasso il cane e vado in
zona — e' il cane o e' l'aria aperta?"*).

### Verdetto: **REFERENCE** — e, per noi, un argomento a favore dell'architettura, non del metodo

Non e' materiale da testare e non entra in nessuna famiglia. Ma vale la pena registrare **perche'
riguarda un problema che il nostro impianto ha gia' aggirato per costruzione**:

Tutto cio' che Tendler descrive — tilt, revenge trading, FOMO, uscite premature, la percezione
distorta che *"ti fa vedere cose che non ci sono"* — e' il costo di **decidere in tempo reale sotto
carico emotivo**. Le nostre decisioni stanno **fuori dal mercato aperto**: le regole sono
pre-registrate prima di vedere i dati, il backtest e' codice, l'esecuzione e' un EA o un copier.
Il tilt non ha una superficie su cui agire.

⚠️ **Con una eccezione importante, ed e' l'unico punto operativo di questo video per noi.**
Il tilt trova comunque una superficie in due posti del nostro processo:

1. **nella decisione di riaprire una famiglia chiusa dopo un NO-GO** — che e' revenge trading
   applicato alla ricerca invece che all'esecuzione. Il ciclo di vita (max 3 round di rifinitura,
   futilita' DSR, holdout sigillato) e' letteralmente un protocollo anti-tilt scritto a freddo;
2. **nella gestione manuale dei segnali del mentore**, che e' copia **a mano** e quindi esposta a
   tutto quanto sopra.

Il resto — la sezione "come stare nella zona" — non ci riguarda: e' un problema che abbiamo
scelto di non avere.

---

# Consuntivo blocco C2 (5 video, 80.738 parole)

| # | fonte | esito |
|---|---|---|
| C2.1 | Desi Trades — cascata di inversioni | SCARTATO — ma **conferma esterna del lead volatilita'** |
| C2.2 | Carmine Rosato — low volume node | SCARTATO (serve order flow) — **casella vuota verificata nel codice** |
| C2.3 | Omar / MBB — market maker + Fib OTE | SCARTATO — **e' letteralmente il NO-GO NXT** |
| C2.4 | Marco Ascetoni — liquidity trap | SCARTATO — stessa cella di C1.4 |
| C2.5 | Jared Tendler — psicologia | REFERENCE — argomento a favore dell'automazione |

**Zero candidati.** Ma il blocco C2 e' il piu' utile dei due blocchi ICT, per tre motivi:

1. **C2.3 e' la validazione piu' netta del nostro lavoro finora incontrata.** Una fonte con 30 M di
   funding dichiarato insegna, livello per livello (0,62 / 0,705 / 0,79), **la strategia che
   abbiamo pre-registrato e ucciso su 6 asset e 14 anni**, con win rate misurato **13,3%** contro
   il 60-70% dichiarato. E il nostro sottoprodotto dice che la direzione giusta e' **l'opposta**.
2. **C2.1 porta una conferma esterna al lead che abbiamo gia' in mano.** La sua regola "opero solo
   nei pochi mesi in cui il VIX e' alto" e' la versione aneddotica del nostro **rho +0,857 fra
   volatilita' di gruppo ed E[R]**. Terza gamba con Tanya (C1.2, calendario).
3. **C2.2 identifica una casella vuota reale e verificata**: `detectors.py` testa POC/VAH/VAL —
   **nodi ad ALTO volume** — e mai i **nodi a BASSO volume**, che sono l'ipotesi complementare con
   meccanismo opposto. Insieme alle trend line inclinate (B2.2), sono le due caselle vuote emerse
   dall'intero funnel.

**Convergenza trasversale confermata (quinta e sesta occorrenza): lo stop stretto e' un'ipotesi
sbagliata quando il rumore a breve e' grande.** Desi: *"lascia che sia il grafico a invalidare, non
il tuo P&L; riduci la size, non lo stop"*. Carmine: **rischio fisso in valuta, size derivata dalla
distanza dello stop**. Con Verma (B2.3), Brando (B2.5) e Ariel (B2.4) fanno **cinque fonti
indipendenti su cinque mercati diversi** che dicono la stessa cosa — ed e' coerente con il nostro
dato che il **12,7% degli stop NXT apre oltre il livello**.
