# Blocco C4 — sessioni di trading in diretta (6 video, ~216.000 parole)

**Nota di metodo, dichiarata in apertura.** Questi sei video hanno una struttura diversa da tutti gli
altri: una spiegazione della strategia (~25% del testo) seguita da **esecuzione in diretta a
mercato aperto** (~75%). La parte in diretta e' narrazione di ordini in tempo reale — *"chiudo due
contratti, sposto lo stop, aspetto il VWAP"* — e **non contiene regole**: contiene l'applicazione,
istante per istante, di regole gia' enunciate prima. Ho letto per intero le sezioni di strategia e
percorso le sezioni in diretta cercando enunciati di regola, numeri e invalidazioni. **Dove la
diretta ha aggiunto qualcosa, e' annotato.** Dove non ha aggiunto nulla, e' detto.

Cinque dei sei ospiti sono **scalper in order flow**, cioe' la famiglia gia' etichettata come
**non testabile con i nostri dati** (serve tick + book).

---

## C4.1 — "Verified $5M trader live" (Kamjan / Gala Trades) · 20.817 parole

`70UtrLU6RAg` · oltre 5 M $ di profitti dichiarati, opzioni intraday. Unico del blocco a **non**
usare order flow.

### La strategia

Trend e livelli sulla **candela oraria**; il livello e' tracciato **sull'apertura del corpo** della
candela di pivot, ignorando gli stoppini. Esecuzione su **2 e 5 minuti** (se i due timeframe
discordano, comanda il 5 minuti). Tre setup: **break & retest**, **bounce** (per le call),
**rejection** (per le put). Configurazione ideale: candela con **stoppino sotto il livello e corpo
sopra** — *"li' e' dove il prezzo e' stato comprato in fretta"* — stop appena sotto quello
stoppino.

**Regole dure, tutte quantificate:**

- **massimo 2 tentativi sullo stesso setup**; al terzo *"e' overtrading, e' rottura di regola"*;
- **2-3 trade al giorno**, quattro o piu' = overtrading (*"nel 2023 ne facevo 8-9 e andava bene; il
  mercato era piu' facile"*);
- opera **un'ora al giorno**, piu' un'ora di preparazione e un'ora di journaling. Analizza
  sull'orario **perche' i suoi trade durano meno di un'ora**;
- target standard **2R**, trim del 50%, poi stop spostato sopra l'entrata.

### Verdetto: **SCARTATO** — livelli orizzontali + break & retest, famiglia CLOSED

Nessuna sorpresa: e' la famiglia dei 384 trial. La variante "livello sull'apertura del corpo invece
che sullo stoppino" e' una **tolleranza di tracciamento**, e le tolleranze sono state testate
(NULL robusto a 0,10 e 0,20).

### La cosa che merita di essere estratta, ed e' contro-narrativa

> *"2R o anche 1,5R: i trade piccoli sono quelli che generano la maggior parte del profitto a fine
> anno. **I trade da home run fanno sentire bene, ma a fine anno sommano una parte piu' piccola dei
> profitti** rispetto a quelli regolari."*

E' l'esatto **opposto** di Kyle Williams (C3.5: *"long = win rate 20-30% ma 10:1"*), di Marius
(C3.4: *"opero nel fallimento, il sistema e' basato sull'asimmetria"*) e di Trader Mayne (C1.1:
*"vinci il 40% con 2:1 e sei profittevole"*).

⚠️ **Non e' una contraddizione, ed e' importante capire perche'**: i tre parlano di **distribuzioni
diverse**. Chi opera code (long su momentum, short parabolici) vive di outlier e deve accettare un
win rate basso; chi opera rientri di breve orizzonte vive di frequenza e non ha code. **Sono due
regimi di payoff distinti**, e la scelta fra i due **non e' una preferenza: e' determinata dalla
strategia**.

Per noi questo e' rilevante in un punto preciso e gia' scritto nel registro: `docs/PROP_FIRM_CRITERIA.md`
documenta che **payoff 1:3 + payout bi-settimanale + consistency rule al 40% sono incompatibili
per qualunque strategia di quella forma**. Cioe' avevamo gia' isolato che il **regime di payoff
vincola la struttura di finanziamento**. Questo blocco lo conferma dall'altro lato: **i trader che
vivono su prop firm tendono tutti verso il regime ad alto win rate e basso R** — perche' e'
l'unico compatibile con le regole di consistency. Non e' una scoperta sul mercato: e' una scoperta
su **cosa selezionano le prop firm**.

---

## C4.2 — "Two world-class order flow scalpers" (Fabio Valentini + Carmine Rosato) · 34.440 parole

`xUyqIjCfZzg` · sessione di New York operata **in due**, su NQ (Fabio) e ES (Carmine).

Entrambi order flow, quindi **non testabile**. La diretta e' interessante per una ragione diversa
dal contenuto: **i due sono spesso in disaccordo sullo stesso grafico nello stesso istante**, con
gli stessi strumenti — uno vede continuazione, l'altro vede range. E' la miglior dimostrazione
disponibile che il metodo **non produce una lettura univoca**.

### Le due frasi che valgono

**Carmine**: *"Mi piace operare dove non c'e' molta liquidita', perche' e' li' che secondo me sta
gran parte dell'edge."* E poco dopo, entrambi: *"il NASDAQ e' il driver perche' e' **meno liquido**;
l'ES e' piu' liquido e quindi piu' lento"*.

⚠️ **Questa e' la terza formulazione indipendente del claim del "playground"** — quello di Kichev,
l'unico passaggio dell'intero funnel che ci abbia prodotto **un lead misurato**:

| fonte | formulazione |
|---|---|
| Kichev (blocco A) | l'edge vive dove c'e' **meno concorrenza** — il "playground" |
| Desi Trades (C2.1) | funziona **solo nei mesi in cui il VIX e' alto** |
| Carmine (qui) | *"opero dove **non c'e' molta liquidita'**, e' li' che sta l'edge"* |
| **noi (misurato, 14/08)** | **rho = +0,857 (p=0,006)** fra volatilita' di gruppo ed E[R] su 8 gruppi |

Le quattro affermazioni parlano di scale diverse (classe di attivi / mese / strumento / gruppo) ma
**hanno la stessa forma**: dove c'e' meno partecipazione efficiente, c'e' piu' da prendere. **La
nostra e' l'unica con un numero.**

**Fabio**, di sfuggita: *"l'opening range breakout ha una curva di equity davvero liscia, ma ci
devi aggiungere sopra strumenti di timing."* ⚠️ Annotato perche' l'ORB e' **NO-GO nel nostro
registro** (vedi C4.6, dove il claim e' esplicito e va affrontato).

---

## C4.3 — "The #1 scalper in the world" (Fabio Valentini) · 36.566 parole

`tvERE-Beu2U` · **top 3 mondiale nella divisione futures della Robbins Cup, +500% in 12 mesi**.
E' il curriculum verificabile piu' forte del canale dopo le US Investing Championships di Marius.

### La tesi centrale — e' un **filtro di regime**, non un setup

> *"Lo schema che tutti operano — market structure shift, ritracciamento, order block — **di norma
> non funziona se non lo inquadri nel contesto giusto**. Se quello schema si presenta **dentro la
> campana della distribuzione del volume della giornata**, stai entrando contro il grosso del
> volume: statisticamente **solo il 30% passa**, il resto resta dentro la value area, e continui a
> essere stoppato. Se aspetti che il mercato sia **fuori dalla balance area**, il tuo win rate sale
> **di almeno 20-30 punti**."*

Piu' tre precisazioni:

- la **teoria dell'asta** (auction market theory): il mercato passa da **bilanciato** a
  **sbilanciato** e ritorna, e **sta in bilancio la maggior parte del tempo**;
- **finestra**: il modello trend-following funziona **solo nella sessione di New York**; a Londra
  produce *"fuori bilancio, dentro, fuori, dentro"* — cioe' falsi segnali. A Londra usa invece un
  modello **mean-reverting**, perche' *"statisticamente negli indici la sessione di Londra ha
  comportamento di ritorno alla media"*;
- **il target influenza il win rate**: *"piu' cerchi di andare oltre l'ATR giornaliero, piu' la
  probabilita' si abbassa"*. E su un target dichiara: *"prendiamo tutta la posizione perche' la
  probabilita' che il mercato inverta da li' e' il 70%; non vale la pena tenerla per il 30%
  restante"*.

Chiama il suo metodo **modello, non strategia**, *"perche' una strategia e' un gruppo di regole da
seguire rigidamente, e non puoi ingabbiare un'entita' dinamica"*.

### Verdetto: **NON TESTABILE** (order flow), ma con **due riscontri diretti sul nostro lavoro**

**1) Il target oltre l'ATR abbassa la probabilita'** — e' la stessa cosa che abbiamo **misurato**
il 14/08 nel test sul soffitto delle escursioni, e che ci ha portato al KILL dell'idea "grandi RR,
niente TP": le uscite lontane sembrano ottime finche' non le confronti con un baseline random
risk-matched. Lui ci arriva per esperienza; noi abbiamo il numero e il baseline.

**2) Il filtro "dentro/fuori bilancio" e' vicinissimo al nostro lead del playground.** La sua tesi
operativa — *il breakout funziona quando il mercato e' fuori bilancio, fallisce quando e' dentro* —
e', tradotta, *il trend-following rende quando la volatilita' e' espansa*. Che e' **esattamente la
direzione del nostro rho +0,857**, arrivata da un mercato diverso, su un timeframe diverso, con
strumenti diversi.

⚠️ **Non e' una conferma statistica** — e' un aneddoto quantificato male (*"+20-30 punti di win
rate"* senza campione ne' metodo). Ma e' la **quarta gamba** della stessa convergenza, e questa
volta viene da qualcuno con un piazzamento **verificato in una competizione**, non da screenshot.

**La frase che spiega perche' non lo possiamo importare** e' sua: *"non puoi automatizzarlo, e'
molto sensibile al mercato"*, e *"che probabilita' c'e' che il trade che inquadro io sia lo stesso
che inquadra il mio studente? Molto bassa"*. E' onesto, ed e' il motivo per cui questo resta
REFERENCE.

---

## C4.4 — "$1M order flow trader live" (Jay Ortani) · 36.700 parole

`SQEtBHOJW6I` · da 3.000 $ a sette cifre. Azioni USA (Tesla, Nvidia, ARM). Order flow su
market depth e volume per prezzo.

Racconto d'origine utile: ha iniziato con **incrocio EMA 9/20 sui 5 minuti** come segnale di
inversione, ha perso, e la domanda che dice di essersi posto e' *"perche' dovrebbe funzionare?"*.
Da li' e' passato al volume per prezzo. Sul resto: *"i bull flag funzionano forse il 50-60% delle
volte a seconda delle condizioni"*.

**Verdetto: NON TESTABILE** (order flow su azioni USA). La sezione in diretta e' esecuzione, non
regole. R:R dichiarati 2,5-4:1, rischio dinamico.

Unico elemento riutilizzabile — ed e' metodologico, non operativo: *"il mio edge e' abbassare il
rischio perche' aumento la size"*, cioe' la stessa cosa di Carmine (C2.2) e Desi (C2.1): **rischio
in valuta costante, size derivata dalla distanza dello stop**. Terza formulazione della stessa
regola, questa volta su azioni.

---

## C4.5 — "How he made $40,000 using order flow" (Carmine Rosato, parte 2) · 37.482 parole

`UhkRRqO1gQM` · seguito richiesto di C2.2; qui non c'e' una strategia, c'e' un **corso di order
flow** (heat map, footprint, delta, assorbimento) esplicitamente presentato come **strato da
aggiungere a qualunque strategia**: *"ICT, smart money, Fibonacci, supply demand — qualunque cosa
usi, aggiungerci l'order flow ti da' entrate migliori e R:R migliori"*.

**Verdetto: NON TESTABILE.**

### Ma contiene il dato piu' onesto del blocco, ed e' quello che voglio tenere

> *"Due settimane fa ho avuto un win rate del 30-33% e ho comunque chiuso la settimana in verde.
> **Il rapporto rischio/rendimento e' piu' importante del win rate.** Se ti concentri sull'R:R e
> proteggi le perdite, le vittorie si prendono cura di se stesse."*

E lo mostra con i numeri dei singoli trade: 35.000 $ con **8:1**, 25.000 $ con **7,6:1**,
27.000 $ con **8:1**, rischio standardizzato ~4.500 $. Sono numeri **coerenti fra loro**: un R:R
medio di ~7 con win rate 30% da' un E[R] ampiamente positivo. E' l'unico ospite del canale che
pubblichi **contemporaneamente** win rate basso, R:R alto e taglia di rischio fissa — cioe' i tre
numeri che servono per verificare che il conto torni. Tutti gli altri ne pubblicano uno solo.

⚠️ Resta un campione selezionato e non verificabile. Ma la **forma** e' quella giusta, e va
contrapposta ai claim 80-90% scartati altrove.

---

## C4.6 — "One of the world's best scalpers" (Andrea Cimbali) · 49.951 parole (il piu' lungo)

`TvoQr6ObjnU` · formatosi sul trading floor di campioni di trading, allievo della stessa scuola di
Fabio (C4.3). Sessione di New York in diretta durante il conflitto mediorientale, +7.000 $.

Il contenuto e' **microstruttura**: come si forma davvero una candela, cosa succede nel book, e una
**demolizione dello "stop loss hunting"** — *"non e' caccia agli stop dei retail: gli stop dei
retail non muovono niente; cio' che il mercato cerca e' liquidita' per riempire ordini grandi"*.
Racconta di esserci creduto anche lui quando era un trader SMC.

**Verdetto: NON TESTABILE** (order flow) — con **un'eccezione che va affrontata direttamente.**

### L'unico claim di questo blocco che collide frontalmente con un nostro NO-GO

> *"Ecco perche' **l'opening range breakout e' una strategia cosi' affascinante e potente, che
> funziona da 20 anni**. Il motivo per cui noi retail possiamo avere un edge scalpando long
> sull'S&P 500 e' che **ci saranno sempre investitori che immettono denaro nel mercato azionario**,
> e i market maker devono fornire liquidita' per riempire quegli ordini enormi: e' quello a
> generare movimenti che possono durare l'intera giornata."*

⚠️ **Questo e' esattamente il nostro filone ORB, e il nostro registro dice NO-GO** —
`analysis/opening_range/`, ORB dell'apertura cash USA (09:30 ET) + retest, dati Dukascopy **M5,
14,5 anni, NAS100 e SPX500**. Stesso strumento, stessa sessione, stesso trigger. E il dettaglio
importante e' nel `DECISIONS.md`: **l'ORB era negativo pre-2020**, e il post-2020 (−0,208) non
batte il random (−0,323 [−0,487, −0,157]) in modo conclusivo — che e' precisamente il motivo per cui
il **forward test e' stato lasciato correre** invece di chiudere il libro.

**Come va trattato questo claim:**

- **non e' evidenza esterna nuova**: e' un'affermazione senza campione, senza periodo, senza
  baseline, fatta da qualcuno che opera l'ORB **con l'order flow sopra** — cioe' non l'ORB nudo che
  abbiamo testato. Lui stesso lo dice: *"non ho bisogno di aspettare il breakout per capire che i
  compratori hanno il controllo"*. **Sta operando qualcos'altro** e lo chiama ORB;
- **ma il razionale economico che porta e' migliore del nostro**. Noi abbiamo testato l'ORB come
  pattern; lui offre un **meccanismo**: flusso strutturale di acquisto sugli indici azionari +
  market maker che devono fornire liquidita'. E' falsificabile e non e' assurdo;
- ⚠️ **e non giustifica di riaprire il filone**: il ciclo di vita richiede **evidenza esterna nuova**
  per riaprire un CLOSED, e un aneddoto non lo e'. Il forward test **sta gia' girando** ed e'
  esattamente lo strumento previsto per questa situazione. **La risposta corretta e' aspettare che
  il forward produca il suo verdetto**, non anticiparlo perche' un professionista ha detto che
  funziona.

**Da tenere per la discussione sui binari**: il razionale di Cimbali va **allegato al forward ORB**
come ipotesi economica dichiarata — cosi' che, se il forward dovesse risultare positivo, sappiamo
gia' *perche'* potrebbe esserlo, e se risulta negativo abbiamo falsificato anche il meccanismo, non
solo il pattern.

---

# Consuntivo blocco C4 (6 video, ~216.000 parole)

| # | fonte | esito |
|---|---|---|
| C4.1 | Gala Trades — livelli orari + opzioni | SCARTATO (CLOSED) |
| C4.2 | Fabio + Carmine — sessione a due | NON TESTABILE — **terza gamba del "playground"** |
| C4.3 | Fabio Valentini — filtro dentro/fuori bilancio | NON TESTABILE — **quarta gamba, con curriculum verificato** |
| C4.4 | Jay Ortani — order flow su azioni | NON TESTABILE |
| C4.5 | Carmine Rosato — corso order flow | NON TESTABILE — **il set di numeri piu' onesto del canale** |
| C4.6 | Andrea Cimbali — microstruttura + ORB | NON TESTABILE — **collide con il nostro NO-GO ORB** |

**Zero candidati, come atteso: cinque ospiti su sei operano order flow.** Il blocco produce tre
cose:

1. **Due gambe in piu' sulla convergenza "meno liquidita'/piu' volatilita' -> piu' edge"**
   (C4.2 Carmine, C4.3 Fabio), di cui una da un **top 3 alla Robbins Cup**. Portano il totale a
   **quattro fonti indipendenti** attorno all'unico numero che abbiamo misurato (rho +0,857).
2. **Un riscontro esterno al nostro KILL sulle uscite**: Fabio dichiara che spingere il target
   oltre l'ATR giornaliero abbassa la probabilita' — la stessa cosa che il test sul soffitto delle
   escursioni ha misurato contro un baseline random.
3. **Un claim che collide con il NO-GO ORB** (C4.6) e che va **allegato al forward test in corso**
   come ipotesi economica, non usato per riaprire il filone.

**Nota trasversale sul blocco**: sei sessioni in diretta, ~216.000 parole, e **nessuna regola nuova
che non fosse gia' enunciata prima del mercato aperto**. La diretta mostra **esecuzione e gestione**,
mai la formazione di una regola. Per il nostro processo — dove le regole si scrivono **prima** di
vedere i dati — la parte in diretta e' la meno informativa dell'intero funnel. E' un dato utile in
se': **se un anno di contenuti si distilla in cio' che viene detto sulla lavagna prima
dell'apertura, il resto e' intrattenimento.**
