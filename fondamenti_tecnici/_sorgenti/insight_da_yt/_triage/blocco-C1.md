# Blocco C1 — ICT / liquidity (5 video, 67.887 parole)

Blocco monotematico: tutti e cinque i video appartengono alla famiglia **livelli-zone-reazione**,
chiusa nel repo da **384 trial pre-registrati con esito NULL su ogni timeframe** (order block, FVG,
liquidity sweep, market structure, PDH/PDL, EQH/EQL, premium/discount). Il triage qui NON rimette in
discussione quel verdetto: cerca **cio' che non era dentro quei 384 trial**.

---

## C1.1 — "The simple $10M ICT blueprint" (Trader Mayne) · 11.522 parole

`coBMd1vk2Lo` · trader verificato 8 figure, co-fondatore della prop firm crypto Breakout.

### Il framework, per intero

Due timeframe obbligatori. **Alto** = analisi (weekly/daily/H4), **basso** = esecuzione
(rispettivamente daily-H12 / H1 / M15).

1. **Struttura**: swing a **3 candele** (la centrale piu' alta delle due laterali). Rottura di
   struttura = **chiusura** oltre lo swing, non semplice tocco.
2. **Range**: dal minimo di swing al massimo di swing formato **dopo** la rottura di struttura.
3. **POI**: l'**order block** = le candele ribassiste immediatamente precedenti al movimento che ha
   rotto la struttura. Ammette esplicitamente che se sono 2-3 candele si possono unire, *"non serve
   essere precisi, e' l'alto timeframe"*.
4. **Premium/discount**: 50% del range. Si compra solo nella meta' bassa, si vende solo nella alta.
5. **Entrata (basso timeframe)**: setup **breaker** = si aspetta che un minimo si formi, **venga
   spazzato**, e poi che il massimo che l'aveva generato venga **rotto**. Chiama "doppia conferma"
   il caso in cui ci sono due rotture di struttura.
6. **Stop**: sotto il minimo dello sweep (non sotto il breaker: *"in crypto quelli li prendono"*).
7. **Filtro di rischio vincolante**: **R:R minimo 2:1**, altrimenti il trade non si prende **anche
   se tutte le altre caselle sono spuntate**.
8. **Gestione**: a 2R chiude meta' o porta a BE. Sizing dinamico sul numero di confluenze.

### Verdetto: **SCARTATO** (famiglia CLOSED), con due annotazioni

**Perche' scartato**: e' esattamente il contenuto dei 384 trial. Order block, sweep di liquidita',
market structure, premium/discount e fair value gap sono stati testati con tolleranze corrette, a
zone, con multi-touch, contro un random structure-free, su ogni timeframe. Nessuno batte il random.
Il verdetto non si riapre per un aneddoto.

**Annotazione 1 — l'onesta' statistica e' insolita.** A differenza di tutto il resto del canale
**non dichiara un win rate alto**: *"non posso vincere il 90% dei trade, sono fortunato se ne vinco
meta'... se vinci il 40% con 2:1 sei profittevole"*. E' aritmetica corretta e verificabile, e la
usa come **vincolo di ingresso** (niente trade sotto 2:1) invece che come claim di marketing.
E' l'unica fonte del funnel che presenti il proprio edge come **basso win rate + payoff**, cioe'
nella forma che noi riconosceremmo.

**Annotazione 2 — il condizionamento.** Come Brando (B2.5), la sua tesi non e' *"il POI reagisce"*,
e' *"il POI reagisce **se** e' nella meta' giusta del range **e** allineato al trend dell'alto
timeframe"*. I nostri 384 trial hanno testato i livelli **incondizionatamente**.

⚠️ **E qui la risposta e' la stessa data a Brando, e va tenuta ferma**: condizionare i livelli
moltiplica lo spazio di ricerca su una famiglia gia' falsificata con 384 trial. Riaprirla serve
**evidenza esterna nuova e quantitativa**, e questi video non lo sono: sono esempi scelti a
posteriori (qui, tre trade vincenti sul proprio Discord). Registrato come **buco noto**, non come
proposta. Se mai si riaprisse, si riaprirebbe **una volta sola** e per la condizione piu' economica
da testare, non per ogni variante.

**Nota**: dice *"questo si potrebbe codificare al 100% in un algoritmo"* e poi, nei contro, che
*"nessun sistema e' puramente meccanico, c'e' sempre discrezione"*. Le due frasi sono nello stesso
video a 4 minuti di distanza. E' il tell che ricorre in tutto il funnel.

---

## C1.2 — "ICT futures strategy" (Tanya Trades) · 13.307 parole

`PZDWQgtqt2I` · live streamer ICT, futures NQ/ES, opera in diretta ogni giorno.

Struttura del video: **il 70% non parla di entrate, parla di QUANDO NON OPERARE.** E' l'unico
video del funnel il cui contenuto principale e' un **filtro di regime**, non un setto.

### Il modello: accumulazione -> manipolazione -> distribuzione

Opera **solo la distribuzione**. Salta l'accumulazione (range, *"seek and destroy"*) e non prende
la manipolazione (*"a volte non e' manipolazione, e' davvero una rottura"*).

**Giorni a BASSA probabilita' — dichiarati in anticipo, dal calendario:**

| condizione | motivo dichiarato |
|---|---|
| nessun evento "red folder" (solo yellow, o niente) | il prezzo accumula, genera liquidita' per il giorno dopo |
| festivi bancari e giorno successivo | volume assente |
| **giorno PRIMA** di CPI / NFP / FOMC | accumulo pre-evento; *"il giorno dopo vedi lo spike delle 8:30 che spazza tutti prima del movimento vero"* |
| giorno **dopo** una giornata di espansione ampia che ha centrato un obiettivo di timeframe alto | dopo la distribuzione torna l'accumulazione |

**Giorni ad ALTA probabilita'**: giornate con evento red folder — e **non opera il rilascio**,
opera la **sessione di New York successiva**. Dichiara CPI come giornata preferita.

**Checklist mattutina (5 punti)**: (1) calendario economico, red folder si/no; (2) **NQ, ES e YM
sono correlati fra loro?** se divergono strutturalmente, sta fuori; (3) si riesce a nominare un
obiettivo di liquidita'? se no, *"se non riesci a capire il draw on liquidity, il draw sei tu"*;
(4) ci sono displacement (rotture di swing con gap di prezzo) o solo stoppini che rientrano nel
range?; (5) i FVG di timeframe alto vengono rispettati?

**Regola di rischio dura**: **due stop e la giornata e' finita.** Size ridotta il giorno prima di
un evento ad alto impatto.

### Verdetto: **SCARTATO come strategia**, ma isola **una misura che possiamo fare**

Le entrate (FVG, inversioni, order block, silver bullet, macro 9:50-10:10, SMT divergence) sono
integralmente nella famiglia CLOSED. Il claim di win rate *"70-80% su CPI"* e' una statistica
dichiarata: si scarta. E le sue prove sono screenshot di trade vincenti, come tutti.

**Ma la tesi portante non e' una tesi sui livelli.** E':

> **Il mercato alterna regime di range e regime di trend, e il regime e' prevedibile in anticipo
> dal calendario macro: senza catalizzatore in calendario si accumula, con catalizzatore si
> distribuisce.**

E aggiunge un numero: *"il prezzo e' in trend forse il 20-30% del tempo, il resto e' range"*.

⚠️ **Questo e' un claim strutturale, falsificabile, e NON e' nei nostri 384 trial** — che
riguardavano la reazione ai livelli, non la distribuzione del regime. **Ed e' la SECONDA fonte
indipendente del funnel a dirlo**: Brando (B2.5) dice la stessa cosa dal lato opposto
(*"ad agosto non c'era la Fed, quindi il breakout non e' partito"*). Due fonti, due mercati
diversi (SPX opzioni / NQ futures), stessa affermazione.

**Cosa NON e'**: non e' una strategia, e non e' un permesso per riaprire i livelli condizionandoli
al calendario (vedi C1.1 e B2.5 — quella porta resta chiusa).

**Cosa potrebbe essere**: una **misurazione descrittiva** — la persistenza direzionale e
l'ampiezza giornaliera differiscono, su una serie storica lunga, fra giorni con evento macro in
calendario e giorni senza? E' la stessa forma del lavoro sulle escursioni: si misura una proprieta'
del mercato, non si elegge una regola. In quella forma **non consuma un trial**.

⚠️ **Con due avvertenze che vanno scritte adesso, non dopo:**
1. il calendario macro e' **pubblico e affollato** — l'opposto del "playground". Una differenza
   misurata **non implica** un edge estraibile al netto dello spread, che sugli eventi si allarga.
2. la famiglia **stagionalita'-calendario** ha gia' un NO-GO (turn-of-month). Questo e' un oggetto
   diverso (evento, non posizione nel mese), ma il precedente impone di dichiarare in anticipo cosa
   si misura e di fermarsi li'.

---

## C1.3 — "ICT + order flow futures" (Abraham Perez) · 13.415 parole

`KkTTCKr-3Ew` · scalper NQ, oltre 600.000 $ di payout da prop firm. Combina ICT con **order flow
su Bookmap**. Il video include una sessione **in diretta** in cui non prende quasi nulla.

### Il processo in tre passi

1. **Contesto** su 4h/daily: ciclo di liquidita' (esterna -> ritorno all'equilibrio -> esterna).
2. **Conferma strutturale** su 15m/1h: displacement con **volume** attraverso uno swing.
3. **Trigger** su 1m/30s + Bookmap: uno di tre modelli — **IFVG** (fair value gap invertito),
   **change in state of delivery** (reazione -> manipolazione -> displacement -> retest),
   **break & retest** — ma **solo se confermato dall'order flow**: heat map (ordini passivi in
   attesa), volume dots (ordini aggressivi a mercato), order book corrente, POC di sessione, VWAP.

Distinzione che fa esplicitamente e che e' corretta: **la liquidita' passiva attira il prezzo, ma
non lo muove; a muoverlo sono gli aggressori** (ordini a mercato). Avverte che i grandi blocchi
passivi visibili possono essere **spoof**. TP tipico 1:2, allargato solo con piu' confluenze.

### Verdetto: **NON TESTABILE con i nostri dati**

Metà del suo processo (heat map, delta cumulativo, POC in tempo reale, aggressori) richiede
**dati tick + book**, che non abbiamo e che non e' realistico procurarsi. L'altra meta' e' famiglia
CLOSED. Non c'e' un percorso per portarlo a un test.

Etichetta gia' prevista dal registro: *"order flow (serve tick/book, non l'abbiamo)"*.

### Ma va registrata la sua obiezione, perche' e' la nostra tesi al contrario

> *"Non credo nelle strategie meccaniche. Non penso che funzionino bene nel lungo periodo, perche'
> se esistesse una strategia meccanica che funziona sempre, la farebbero tutti — basterebbe
> programmare un algoritmo e sarebbe follemente profittevole."*

E' l'argomento anti-meccanico piu' pulito che il funnel abbia prodotto, ed e' **la stessa premessa
da cui partiamo noi, con la conclusione opposta**:

- **lui** ne deduce che l'edge deve stare nella discrezione, in cio' che non si puo' codificare;
- **noi** ne deduciamo che l'edge deve stare **dove la concorrenza non arriva** — il claim del
  "playground" — e che una regola meccanica va cercata li', non nei mercati piu' guardati.

La sua premessa e' corretta e la nostra risposta e' gia' scritta nel repo. Vale come **conferma
esterna che il problema e' posto bene**, non come argomento contro il metodo. Il difetto della sua
conclusione e' che *"non e' codificabile"* non implica *"funziona"*: rende soltanto impossibile
falsificarlo — e infatti nella sessione live, con l'analisi tutta a posto, chiude dicendo
*"il bias non e' chiaro, sto fuori"*.

**Nota di coerenza interna al funnel**: Trader Mayne (C1.1) dice *"questo si potrebbe codificare
al 100% in un algoritmo"* della **stessa famiglia di concetti** che Perez dichiara non codificabile.
Non e' una divergenza di dettaglio: e' l'intero disaccordo sul perche' la cosa funzionerebbe.

---

## C1.4 — "The one liquidity pattern that actually works" (Marco Asselin) · 14.423 parole

`T_djSNBmV00` · oltre 500.000 $ di payout, opera oro e futures. Chiama il suo schema
**"modello DaVinci"**.

### Il modello

Frattale, dichiarato valido su qualunque asset e qualunque timeframe. In versione rialzista:

1. il prezzo prende **qualcosa a sinistra** (un vecchio minimo) — cio' valida la direzione;
2. sale e forma un massimo che **rispetta massimi precedenti** -> **"liquidita' ingegnerizzata"**:
   e' il mercato che *comunica* dove stanno gli ordini, invece di indovinarlo;
3. il prezzo ritraccia, i compratori precoci entrano e vengono **spazzati** sotto un minimo;
4. **entrata** appena quel minimo viene preso, **stop** sotto il minimo a sinistra,
   **obiettivo** i massimi identificati al punto 2;
5. filtro di rischio: **R:R minimo 1:3**, altrimenti scende di timeframe per un'entrata piu' stretta
   o non prende il trade.

Il punto che rivendica come originale: *"non c'e' liquidita' sopra OGNI massimo"*. Solo un massimo
che **rispetta massimi precedenti** (massimi uguali) conta. Invalidazione: se lo sweep non produce
il movimento, aspetta che si ripeta lo schema; l'idea non e' sbagliata, era solo prematura.

### Verdetto: **SCARTATO** — e' esattamente una cella gia' testata

A differenza degli altri video del blocco, qui non serve nemmeno un'argomentazione generale: la
variante specifica che rivendica come discriminante — **livello con contatti multipli / massimi
uguali, con tolleranza a zona** — e' **una delle celle esplicitamente incluse nei 384 trial**
(v1/v2: zone + multi-touch, EQH/EQL, freshness). Esito NULL, e NULL robusto a tolleranza 0,10 e
0,20.

L'unica differenza rispetto a cio' che abbiamo testato e' che lui entra **dopo lo sweep** invece
che al tocco. Ed e' un dettaglio che **abbiamo gia' misurato altrove**: il nostro lead FADE (NXT)
e' esattamente uno short-horizon mean-reversion dopo un'escursione, e vale **+0,31R** — misurato
con costi, holdout e modellazione onesta del fill. Cioe' la parte potenzialmente valida del modello
DaVinci **non e' la liquidita' ingegnerizzata: e' il rientro dopo l'estensione**, che nel nostro
repo esiste gia' come lead, e' gia' quantificata, ed e' gia' in forward test.

**Nota sull'invalidazione**: *"se lo sweep non funziona, aspetto che accada di nuovo — non
significa che la direzione sia sbagliata"*. Formalmente e' una regola **senza condizione di
falsificazione**: nessuna sequenza di risultati puo' dichiararla sbagliata. E' il difetto
strutturale piu' importante da annotare su tutto il blocco, e vale anche per C1.1 e C1.2.

---

## C1.5 — "Universal playbook" (Z, the traveling trader) · 15.220 parole

`nMhywubR2xc` · 15 anni di attivita', trascorsi a Wall Street. Opera azioni, opzioni, futures e
gestisce investimenti di lungo periodo. **Rifiuta esplicitamente** di portare l'ennesimo derivato
ICT/SMC e propone invece un meta-framework.

### Il "playbook universale"

*"Nessuna storia, nessun trade."* La storia richiede:

1. un **catalizzatore di liquidita'** — vecchi massimi/minimi, livelli chiave, rottura di trend
   line, **movimento ampio**, o **market structure shift**. Se il prezzo si limita a tendere
   tranquillamente, *"non c'e' niente da fare, non e' successo nulla a cui reagire"*;
2. un **ritracciamento** dopo l'evento: rifiuta il breakout trading perche' lo stop diventa 2-3x
   piu' lontano a parita' di obiettivo;
3. **confluenza** tecnica **e fondamentale**.

Piu' una tesi sul metodo: la strategia specifica e' irrilevante (*"trend line, SMC, testa e spalle,
Fibonacci — stanno tutti raccontando la stessa storia"*); cio' che distingue e' avere una storia.

### Verdetto: **REFERENCE**, con **un'unica misura isolabile**

Il framework nel complesso **non e' falsificabile**: "movimento ampio o rottura di struttura o
livello chiave o trend line, piu' un ritracciamento, piu' confluenza" e' abbastanza ampio da
descrivere qualunque grafico a posteriori. Nella nostra griglia sarebbe una regola senza condizione
di rifiuto. E lo dimostra il suo stesso esempio di perdita: entrato su uno sweep di minimi uguali,
stoppato, e la reazione e' *"va bene, adesso la storia e' una bear flag"* — la storia si riscrive
dopo l'esito.

**Le tre affermazioni concrete, valutate una per una:**

| claim | giudizio |
|---|---|
| il ribasso 2025 si e' fermato ai massimi 2021, il 2022 ai massimi 2020, il COVID ai massimi pre-2015 | n=3, **selezionato a posteriori** su tutta la storia disponibile. Non e' evidenza. |
| debolezza stagionale a febbraio del primo anno del ciclo presidenziale | famiglia **stagionalita'-calendario**, che nel registro ha gia' un NO-GO (turn-of-month). n≈20 cicli. |
| **l'S&P tende a fermarsi a cali del -10% e del -20% dal massimo** | ⚠️ **questa e' misurabile a costo quasi nullo** e non e' nei 384 trial: quelli testavano livelli di PREZZO, non **soglie di drawdown percentuale dal massimo**. E' un oggetto diverso. |

Sul terzo: e' una misura descrittiva (la distribuzione dei minimi di drawdown si addensa a -10% e
-20%?) fattibile su un indice con storia lunga. **Ma il prior e' pessimo per il motivo di sempre**:
sono le soglie **piu' guardate e piu' commentate del mercato piu' guardato del mondo** — l'opposto
del playground. E la sua stessa formulazione (*"minus 10 bounce, minus 20 bounce"*) e' una soglia
assoluta, cioe' esattamente la forma che il **KILL delle escursioni del 14/08** ci ha insegnato a
non leggere senza un baseline: soglie assolute passate 6/6 e 15/15 e poi ribaltate dal random.
**Registrato, non proposto.**

### Le due cose che vale davvero la pena portare via

**1) Onesta' sul win rate, seconda occorrenza nel blocco.** *"La maggior parte dei trader d'elite
sta fra il 50 e il 55% di win rate; ci si concentra sul multiplo di R, non sul win rate."* Insieme
a Mayne (C1.1: *"sono fortunato se ne vinco meta'"*), fanno **due fonti su cinque nel blocco piu'
chiacchierato del canale** che presentano l'edge nella forma corretta. Contro i claim di
80-90% che abbiamo scartato dappertutto.

**2) La frase che riguarda il pilastro investing, non il trading:**

> *"Ho guadagnato molto piu' facendo swing e investendo che facendo trading. Il trading per me e'
> reddito, non e' un modo per creare ricchezza. Non puoi battere l'effetto della capitalizzazione."*

Detta da un professionista di 15 anni con background in finanza, in un canale che vive di prop firm
e sponsorizzazioni sul day trading, cioe' **contro il proprio interesse editoriale**. Non e' una
prova di nulla, ma e' la posizione a cui il repo e' gia' arrivato per conto suo con il **PAC
passivo** (`docs/INVESTING_PILLAR_PLAN.md`) dopo aver archiviato lo Stock Selector. Vale come
**conferma esterna della separazione dei due pilastri**.

---

# Consuntivo blocco C1 (5 video, 67.887 parole)

| # | fonte | esito |
|---|---|---|
| C1.1 | Trader Mayne — framework ICT | SCARTATO (CLOSED) — onesta' su win rate |
| C1.2 | Tanya Trades — filtro di regime da calendario | SCARTATO come strategia; **isola una misura** |
| C1.3 | Abraham Perez — ICT + order flow | NON TESTABILE (serve tick/book) |
| C1.4 | Marco Asselin — modello DaVinci | SCARTATO — cella gia' testata nei 384 trial |
| C1.5 | Z — playbook universale | REFERENCE — framework non falsificabile |

**Zero candidati, come previsto.** Il blocco era interamente dentro una famiglia chiusa, e la
lettura integrale l'ha confermato senza sorprese. Cio' che il blocco ha prodotto:

1. **Un oggetto misurabile, non un candidato**: il **regime condizionato al calendario macro**
   (C1.2, confermato da B2.5 e in parte da C1.5). La forma corretta e' una misura descrittiva —
   la persistenza direzionale differisce fra giorni con e senza evento in calendario? — che non
   consuma un trial e non riapre la famiglia livelli. Con il caveat, dichiarato in anticipo, che
   il calendario e' pubblico e affollato.
2. **Due conferme esterne dell'onesta' statistica corretta** (win rate 50-55% + multiplo di R),
   che contrastano tutti i claim 80-90% del resto del canale.
3. **La miglior formulazione dell'obiezione anti-meccanica** (C1.3) — e il fatto che la nostra
   risposta ("cercare dove non c'e' concorrenza") sia gia' scritta nel repo.
4. **Un difetto strutturale comune** a C1.1, C1.2, C1.4: nessuno di questi modelli ha una
   **condizione di falsificazione**. Quando lo sweep non funziona, la risposta e' sempre *"aspetto
   che si ripeta"* o *"la storia era un'altra"*. E' precisamente cio' che il nostro protocollo di
   pre-registrazione esiste per impedire.
