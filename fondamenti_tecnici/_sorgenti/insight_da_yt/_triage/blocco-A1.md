# Blocco A1 — triage per video (fascia A: claim strutturali)

Lettura integrale, un video alla volta, secondo il piano approvato il 2026-08-17
([`_INTAKE.md`](../../_INTAKE.md)). Il digest di `rule_extract.py` è consultato **dopo** la
lettura, come rete di sicurezza. Statistiche dichiarate registrate ma **non** entrate nel prior.

---

## A1.1 — "If You Only Watch ONE Market Cycle Trading Video" (Clement Ang) · 48 min · 9.227 parole

`0_NSmOWVbpA` · US Investing Championship, divisione da $1M denaro reale.

### Contenuto meccanico estratto

**Classe di asset**: **azioni USA singole**. Filtri di selezione dichiarati:
- volume medio giornaliero in dollari **≥ 50 M$**
- **ADR > 3%** (esclude esplicitamente i bancari: "vuole i nomi growthy")
- **forza del gruppo** (altri titoli dello stesso settore che si preparano)
- **forza relativa** contro l'indice durante il consolidamento

**Setup long** (dichiaratamente il "price cycle" di Oliver Kell):
1. titolo in uptrend, SMA 200 inclinata al rialzo
2. pullback → **wedge pop** sopra le EMA 10/20 con **volume alto** = primo segno di domanda
3. ritorno a testare EMA 10 e 20 → **base**, volume che si assottiglia, volatilità in contrazione
4. forza relativa mantenuta durante la base
5. **entrata A (su forza)**: rottura del livello orizzontale, **stop = minimo del giorno** (o del giorno prima) − ~10 cent
6. **entrata B (su debolezza)**: acquisto del pullback sulla EMA 10 mentre gira, stop = minimo del giorno
7. temporizzazione dell'ingresso sul grafico a **5 minuti**

**Gestione del trade (long)** — la parte che ci interessa davvero:
- a **+2 × ADR(20)** di utile non realizzato → chiude **1/3**, sposta lo stop a **break-even**
- quando il prezzo è **> 10 estensioni ATR dalla SMA 50** → chiude un altro **1/3**
- l'ultimo **1/3 va in trailing** fino alla chiusura sotto la **EMA 10** (o la 20, secondo quale il
  titolo abbia storicamente rispettato)

**Setup short** ("late stage failed base" di Gil Morales):
1. uptrend → base → **breakout fallito**
2. violazione della **EMA 20 su volume elevato** → il titolo passa nella watchlist di rottura
3. **wedging**: recupero debole su volume minimo
4. il prezzo "uppercutta" la media e fallisce → si shorta la girata (a 5 min: perdita del **VWAP
   intraday**), **stop sopra il massimo del giorno** +10/20 cent
5. **invalidazione**: chiusura daily sopra la EMA
6. conferma di mercato: il QQQ deve fare la stessa cosa

**Gestione (short)**: copre **metà** all'*undercut and rally* di un minimo precedente; il resto se
riconquista la EMA 10; **ri-shorta** sui rimbalzi contro-trend nelle medie; **massimo 3 rientri per
ticker**, poi abbandona il titolo (regola anti-tilt).

**Altro**: basi settimanali di **almeno 6 settimane** per i movimenti prolungati; niente posizioni
in earnings (rischio binario); un solo schermo, niente indicatori multipli.

### Statistiche dichiarate (registrate, NON nel prior)

| dichiarato | dove |
|---|---|
| "500%+ Champion" | titolo/hook del video |
| **"oltre 80% nel 2024" e "oltre 140% nel 2025"** | detto dal conduttore nello stesso video |
| **win rate storico 30%** | dichiarato dal trader |
| esempi: rischio 4% → +20% in 3 giorni; rischio ~1% → +28% (1:10) | esempi a schermo |

⚠️ **Incoerenza interna alla fonte**: l'hook dice "500%+" ma i numeri enunciati nello stesso video
sono 80% e 140%, che composti fanno ~332%, non 500%. Primo caso in cui il claim del titolo
contraddice il claim del contenuto.

✅ **Nota in direzione opposta**: un **win rate dichiarato del 30%** è un valore *basso*, coerente
con un approccio a payoff asimmetrico, e stona vistosamente col 90-98% del resto del canale. Va
registrato come tale: la distribuzione dei claim di questo ecosistema **non è uniformemente gonfiata**.

### Verdetto contro il filtro d'ingresso

| criterio | esito |
|---|---|
| strumenti che tradiamo | **NO** — azioni USA singole, non le tradiamo e non abbiamo i dati |
| regole codificabili senza discrezionalità | **PARZIALE** — scheletro sì (ADR, ADV, EMA, volume, stop al minimo del giorno, uscite numeriche); ma *wedge pop*, *wedging*, "dove tracci la linea della base" sono **descrizioni visive**, la stessa ragione per cui Okala fu dichiarato non testabile |
| timeframe coperti | daily sì, la temporizzazione a 5 min no |

→ **REFERENCE, non candidato.** Nessuna pre-registrazione.

### L'unica cosa che vale la pena portarsi dietro

La sua **gestione del trade è una terza classe di uscita che non abbiamo mai testato**, ed è
costruita esattamente contro il modo di fallire che il nostro test ha misurato il 2026-08-14:

- noi abbiamo testato **E1 trail puro** (peggiore in tutti e 3 i lookback) ed **E2 target fisso 3R**
  (mediocre); ha vinto **E3, l'uscita a tempo**;
- lui non fa né l'uno né l'altro: **incassa 1/3 a un target scalato sulla volatilità** (2×ADR),
  **1/3 a una soglia di estensione** (10 ATR dalla SMA 50), e **manda in trailing solo l'ultimo
  terzo**.

È una **uscita ibrida a tre stadi**: tronca la maggior parte della posizione presto e lascia correre
solo una coda ridotta. Se la domanda sul trail si riaprirà con un veicolo adatto, questa è la
variante da mettere in gara accanto a E1/E2/E3 — **non** su azioni USA, ma sullo stesso banco di
prova Donchian dove abbiamo già i dati e il motore.

Vincolo da ricordare: la famiglia trend è a **round 2 di 3** e resta **1 pre-registrazione esterna**
nel trimestre. Questo non la merita da solo.

### Rete di sicurezza sul video A1.1: il compressore ha fallito

`rule_extract.py` ha tenuto il 32% del testo e ha **mancato 4 delle 5 regole numeriche** sopra:
2×ADR, 10 ATR di estensione, i filtri 50M$/3% ADR e la base di 6 settimane. Ha trovato solo il "30%".

**Terzo fallimento consecutivo dello stesso strumento**, ognuno su un tipo diverso di omissione. La
conclusione onesta è che un filtro a lessico **non fa questo lavoro in modo affidabile**: dà
sicurezza falsa. Va trattato come curiosità, non come controllo. È la lettura integrale che produce
il risultato — la decisione dell'utente di procedere un video alla volta è ora **misurata**, non
solo ragionevole.

---

## A1.2 — "If You Only Watch One Trading Strategy Video" (Steven Dux) · 67 min · 11.284 parole

`52ZsDmFHqyY` · short selling su **small cap USA**. Tre modelli, tutti sul lato corto.

### Filtri comuni (dichiarati, numerici)

- **capitalizzazione iniziale 1-100 M$** (il *first red day* arriva a 200 M$)
- **float 1-50 M azioni**, con fasce: 1-2 M "very low", 2-5 M "mid", 5-10 M "large"
- **prezzo > 3 $** (sotto, "rovina le statistiche")
- **settori esclusi**: biotech (il win rate cala di 20-30 punti), energia, titoli cinesi
  (rischio *halt*: dichiara perdite del ~100% perche' non si riusciva a uscire)
- volume: se il **pre-market supera 50 M** azioni, il titolo **non e' tradabile** col gap up short
- stima del volume di giornata = **pre-market x 5-10**; il 30-35% del volume passa prima delle 11:00

### I tre modelli

**1. Gap up short** — gap >= 100%; dopo l'apertura spinta del 20-35%; consolidamento di ~1 ora;
alla prima rottura fra le 10 e le 11 si entra a piena size, **stop sopra il massimo del
consolidamento**. Rischio medio dichiarato **7%**, discesa media **26%** dal massimo intraday
→ R:R ~1:3,5-1:4. **Frequenza 50-70/anno, win ~75%.**

**2. Bounce short** — sul grafico a 1 anno si cerca **una candela singola ad altissimo volume** che
ha creato resistenza; si calcola il **"blocco di dollari"** intrappolato (azioni scambiate a quel
prezzo x prezzo, ideale **>= 150 M$**); il titolo e' poi crollato e piatto ~2 mesi; quando riappare
un gap >= 100% verso quel livello, si stima il volume odierno (pre-market x 10, poi **ridotto del
50-80%** perche' il tuffo in apertura scoraggia i compratori) e si confronta col volume
intrappolato: **rapporto >= 2:1 → si aumenta la size** (dichiara un 10:1 su GME). Si shorta in
apertura cavalcando la vendita degli intrappolati. **Frequenza ~30/anno, win 80-85%.**

**3. First red day** — >= **3 giorni verdi consecutivi**, ciascuno con **volume in dollari >= al
precedente**, **nessun giorno rosso o piatto in mezzo** (un rosso azzera il conteggio); ampiezza
**>= 300% su 3 giorni** oppure **>= 1000% su 2**; soglie di "blocco di dollari" per fascia di
capitalizzazione iniziale (50 M → si ferma intorno a 1 G$ scambiati; 100 M → 3 G$; 200 M → 5-10 G$;
IPO da ~500 M → ~30 G$). Il primo giorno si entra solo con **1/4 di size**; si attende il **secondo
giorno**, quando il pre-market collassa e il rapporto di volume diventa 3:1 o 4:1, per la size piena.
**Frequenza 5-10/anno, win fino al 90%.**

**Sizing**: mai oltre il **10% del float** ne' l'**1% del volume**; euristica "un fondo non spinge
oltre il 30% del float, altrimenti si pompa da solo".

### Verdetto contro il filtro d'ingresso: SCARTATO

| criterio | esito |
|---|---|
| strumenti che tradiamo | **NO** — small cap USA, lato **corto** |
| regole codificabili | **ALTA** (piu' di A1.1): quasi tutto e' numerico. Restano discrezionali "consolidamento", "prima debolezza", "azione parabolica" |
| dati | **NO, e in modo dirimente** — servono float, capitalizzazione, volume pre-market, minuti intraday **e soprattutto disponibilita' e costo del prestito titoli** |

**La barriera dirimente non e' il dato di prezzo, e' il prestito titoli.** Shortare small cap
richiede il *locate*: i titoli piu' difficili da prendere a prestito sono **esattamente** quelli che
sfaldano di piu'. Un backtest senza dati di disponibilita' e costo del borrow sarebbe
**sistematicamente ottimista**, e in questa nicchia il bias e' enorme, non marginale. Si aggiunge il
rischio di **halt**, che lui stesso descrive come perdita totale non gestibile. Nessuna
pre-registrazione possibile: non e' una questione di budget, e' che **non e' misurabile da noi**.

### Statistiche dichiarate — e perche' questa volta il BS-test NON boccia

Percorso dichiarato: **27.000 $ → oltre 50 M$** (~1.852x in ~10 anni = **112%/anno composto**);
trade da 7 M$ e ~10 M$ nel 2025; 1,5 M$ in 15 minuti su GME.

Applicando il BS-test di [[04_quant_metodologia]] §8 ai suoi stessi numeri del gap up short
(win 75%, reward medio 26%, rischio medio 7%): **E[R] = +2,54R per trade**, ~60 trade/anno
→ **+152R/anno**. Cioe' i numeri dichiarati sono **internamente coerenti** con il risultato
dichiarato.

⚠️ Questa e' una **categoria diversa** dai claim che abbiamo bocciato finora. NXT, VELTRIX, Okala
fallivano il BS-test perche' implicavano rendimenti impossibili: qui il conto **torna**, e per di
piu' la fonte fornisce spontaneamente il **vincolo di capacita'** che rende la storia coerente
(mai oltre il 10% del float; "se sizo troppo rompo il pattern"; a 7 M$ di trade il suo stesso
ordine muove il titolo). Un edge vero in una nicchia illiquida **deve** essere capacity-constrained:
e' esattamente la firma che ci si aspetta.

**Cio' non lo rende vero.** Non possiamo verificare nulla: sentiamo il vincitore (survivorship
totale), non abbiamo i suoi trade, e la strategia e' per noi **infalsificabile**. Ma va registrato
onestamente come **claim non-rigettato**, non nella stessa casella dei precedenti.

### Il vero valore: due tasselli

**1. Il punto dati piu' forte finora sul "playground".** Opera nell'angolo **piu' illiquido e piu'
affollato di retail** dell'intero mercato — float 1-50 M azioni, capitalizzazione sotto 100 M$ — che
e' precisamente dove Kichev colloca l'edge e dove il nostro **rho +0,857** puntava. Due fonti
indipendenti piu' una nostra misura convergono. **Corroborazione, non prova**: nessuna delle tre e'
un test controllato, e la convergenza fra due fonti dello stesso ecosistema vale meno di due fonti
davvero indipendenti.

**2. Il suo metodo e' il nostro metodo.** Traccia a mano dal 2015: frequenza annua, win rate,
reward medio, e da li' calcola l'**attesa annua prima di operare** — dichiarando che serve a
eliminare la FOMO, perche' sai gia' cosa aspettarti. E aggiunge due regole che sono nostre:
*"testa la strategia da solo prima"* e *"se il criterio non e' legato a un meccanismo logico o
psicologico, la strategia non funzionera'"* — che e' il requisito di **razionale economico** di
[STRATEGY_LIFECYCLE §6a.6](../../../docs/STRATEGY_LIFECYCLE.md). Da un discrezionale, e' la
disciplina piu' vicina alla pre-registrazione che questo canale abbia prodotto.

---

## A1.3 — "If You Only Watch One Trading Process Video" (Jeff Holden, SMB Capital) · 84 min · 17.048 parole

`WDdvnd9vLbM` · **non e' una strategia**: e' il modello di sviluppo del trader usato sul desk SMB.
Ricade nell'**uso primario approvato** per questo ecosistema (layer operativo e di rischio).

### Il "momentum model"

`obiettivo → attrito → registro degli errori → 5 perche' → soluzione → attrito → piccola vittoria`,
e poi si impila. La tesi: azzerare e ripartire da capo (nuovo obiettivo, nuovo account) **non
costruisce nulla**; le curve di equity buone nascono da piccole vittorie accumulate, non da un
momento di svolta.

Meccanica dichiarata: per **una settimana** si annotano gli errori nel *daily report card* senza
giudicarli ne' risolverli; a fine settimana emergono due o tre temi ricorrenti; si sceglie **il
primo**, e lo si diagnostica con i **5 perche'** di Toyota. Regola esplicita: **un obiettivo alla
volta** ("la ricerca dice che lavorando su due non ne concludi nessuno"), e si parte **sempre dal
rischio**.

### I due tasselli concreti

**1. Allocazione del rischio per grado del setup, in frazioni dello STOP GIORNALIERO:**

| grado | quota dello stop giornaliero |
|---|---|
| **A+** | fino a **80%** |
| **A** | **30%** |
| **B** | **15%** |
| **C** | **5%** |

Non e' il sizing come lo scriviamo noi (percentuale dell'equity): l'unita' e' la **perdita massima
giornaliera**. Ed e' l'unita' giusta quando il vincolo che morde e' il **daily drawdown**, che e'
esattamente cio' che [PROP_FIRM_CRITERIA](../../../docs/PROP_FIRM_CRITERIA.md) ha identificato come
primo killer silenzioso. Noi non abbiamo nulla di equivalente: e' una formalizzazione del
"dimensiona per convinzione" espressa nella valuta del vincolo reale. *(Nota: nella trascrizione i
gradi A e B sono enunciati due volte in modo leggermente incoerente; sopra e' riportata la lettura
piu' coerente.)*

**2. I 5 perche' come POST-mortem.** Il nostro [[04_quant_metodologia]] §9 ha un **pre-mortem**
(le direzioni di rischio scritte prima del capitale) ma **niente di sistematico per diagnosticare
gli errori dopo**. Serve ora: il copier va verso il live e il forward del fade e' in corso, e gli
errori che arriveranno sono di **esecuzione** (segnali saltati, fill in ritardo, stop spostati) —
proprio la categoria che il pre-mortem non copre. L'esempio svolto nel video e' istruttivo: partendo
da "non ho rispettato lo stop" si arriva, cinque perche' dopo, a *"quella volta funziono' perche'
stavo tradando il mercato, non il singolo titolo"* — cioe' a una **condizione di validita'**, non a
un buon proposito.

**Altro trattenuto**: un playbook alla volta finche' non e' solido, poi si scala a ~4 (i veterani ne
hanno 18-25); struttura "baseline + A+ = carriera" (i setup A+ sono rari e vanno studiati a parte,
ma si vive di baseline); orizzonte dichiarato di 10 anni con ~2 anni eccezionali.

### Verdetto

**REFERENCE / layer operativo.** Nessuna regola testabile, nessuna pre-registrazione. L'unico
"trade" mostrato (continuazione sulla EMA 9 su Microsoft) e' **un singolo esempio vincente**.

### CONFLITTO da mappare — e questa volta abbiamo il numero

Holden afferma: *"la ragione per uscire e' la prima chiusura sotto la EMA 9; vendere prima e'
l'errore"*, ed e' la **tesi della coda aperta**. La sostiene con **un esempio scelto a posteriori**
piu' l'esperienza del desk.

Noi l'abbiamo **misurata**: sul banco Donchian, l'uscita in trailing su media mobile e' risultata
**la peggiore delle quattro** su tutti e tre i lookback, e ha vinto **l'uscita a tempo**
([reviews/trend-exit-playground-2026-08-14.md](../../../docs/reviews/trend-exit-playground-2026-08-14.md)).

**Non si elegge un vincitore**, si separa per dominio: lui parla di **momentum intraday su singolo
titolo** con un trader che conosce quel playbook; noi abbiamo misurato **swing multi-asset su D1 in
14 anni**. Ma l'asimmetria **epistemica** va registrata: la sua evidenza e' un **aneddoto
selezionato**, la nostra e' una **distribuzione**. E' la stessa asimmetria per cui il nostro
protocollo esiste — e vale la pena notare che il video mostra proprio il caso in cui l'aneddoto
avrebbe portato alla conclusione opposta a quella che i dati sostengono nel nostro dominio.

---

## A1.4 — "Trading $50M At 25 · Market Cycle 4 Stages" (Ted Zhang) · 100 min · 18.814 parole

`VDK200OHNSo` · **stage analysis di Stan Weinstein** (dal libro del 1988), applicata come gauge di
trend di lungo periodo. Ted Zhang gestisce presso Ritholtz/Revere; ha collaborato alla costruzione
del corso di Weinstein presso TraderLion.

### Specifica — interamente aritmetica

Grafico **settimanale**, medie mobili **SEMPLICI a 10, 20, 30, 40 settimane** (lo dichiara
esplicitamente: "I use simple").

| stage | definizione meccanica | operativita' dichiarata |
|---|---|---|
| **4** discesa | prezzo **sotto tutte**, impilate al ribasso (10<20<30<40), pendenze giu' | si shorta |
| **1** base | pendenze piatte, le medie **convergono e attraversano** il prezzo, che oscilla intorno | **si evita** |
| **2** salita | prezzo **sopra tutte**, impilate al rialzo (10>20>30>40) | si compra |
| **3** distribuzione | speculare allo stage 1 | **si evita** |

Soglia d'ingresso dichiarata: prezzo sopra tutte le medie **con almeno 10 > 20 > 30**.

**Il claim centrale e' falsificabile**: *gli stage 1 e 3 sono "le fasi da evitare", dove ci si fa
tritare; gli stage 2 e 4 sono dove si prende posizione.* Cioe': **condizionare allo stage deve
migliorare l'espettanza** rispetto all'incondizionato.

**Il claim di universalita' e' esplicito e ripetuto**, e nel video lo percorre uno per uno:
azioni ed ETF, **crypto** (BTC, ETH), **metalli** (oro, argento), **agricoli** (cacao, succo
d'arancia, caffe'), **energia/uranio**, **obbligazionario** (note decennale USA), **valute** (DXY).
E' anche dichiarato **frattale**: stesso schema su daily con periodi piu' corti.

### Verdetto: **CANDIDATO** — il primo del funnel che supera il filtro d'ingresso

| criterio | esito |
|---|---|
| strumenti che tradiamo | **SI** — rivendica tutte le classi, e noi ora abbiamo **27 strumenti su 8 gruppi** (inclusi bond, energia, agricoli, valute, crypto) |
| regole codificabili senza discrezionalita' | **SI** per gli stage 2 e 4: impilamento di medie e posizione del prezzo sono **aritmetica pura**, zero giudizio visivo. Gli stage 1 e 3 si definiscono come complemento |
| timeframe coperti | **SI** — il settimanale si ricava dal nostro D1 |

E' anche un **filtro di regime**, non una strategia: il primitivo da testare e' pulito e isolabile
("condizionare allo stage migliora l'espettanza?"), esattamente il tipo di test che sappiamo fare.
Aggancia due fili aperti: il **banco Donchian** (motore e baseline gia' pronti) e il **lead sul
playground** (il gradiente sopravvive al condizionamento di regime?).

### I contro, che vanno detti prima e non dopo

1. **E' ancora la famiglia trend.** Stage 2 = prezzo sopra medie crescenti = trend. La famiglia e' a
   **round 2 di 3**: un test sul filtro di stage sarebbe **l'ultimo round disponibile**.
2. **Aggiungere un filtro e' la modifica piu' pericolosa** che conosciamo
   ([STRATEGY_LIFECYCLE §4](../../../docs/STRATEGY_LIFECYCLE.md): *"il piu' seducente e il piu'
   fatale"*). La distinzione che lo rende legittimo: questo filtro e' **specificato a priori da una
   fonte esterna**, non scelto guardando quali nostri trade hanno perso. Resta legittimo **solo se
   pre-registrato prima di eseguirlo**.
3. **Il metodo ha 38 anni** (Weinstein, 1988) ed e' notissimo. L'alpha decay post-pubblicazione
   (McLean-Pontiff, citato dal nostro `QUANT_REVIEW_PROTOCOL`) morde con forza.
4. **L'evidenza nel video e' interamente col senno di poi.** Ogni grafico e' mostrato a posteriori
   con gli stage gia' etichettati. Lui stesso ammette che *"in tempo reale puo' essere difficile
   identificare lo stage"*, e mostra un fallimento (Moderna) inquadrandolo come "per questo si usano
   gli stop".

### Statistiche dichiarate: **nessuna**

Da segnalare in positivo, ed e' un'anomalia in questo canale: **il video non offre un solo numero di
performance** per il metodo. Nessun win rate, nessuna espettanza, nessun backtest. I claim sono
**strutturali** ("e' universale", "evita gli stage 1 e 3"), non numerici. Non c'e' nulla da
sottoporre al BS-test — il che lo rende epistemicamente piu' rispettabile del resto del canale, e
al tempo stesso significa che **tutto il lavoro di verifica e' nostro**.
Gli unici numeri citati sono **masse gestite** ($50M a 25 anni, $400M+ di studio), che non sono
claim di rendimento.

### Nota sulla regola di arresto

Il piano prevedeva la sospensione del funnel se dopo due blocchi nulla avesse superato il filtro
d'ingresso. **Qualcosa lo ha superato al quarto video**: la condizione di sospensione non scatta.

---

## A1.5 — "$100+ Million Trader: His BEST Trading Strategy" (Lance Breunigstein) · 91 min · 15.617 parole

`_qeFh1ADss8` · **mean reversion / capitulation**. E' la famiglia del nostro fade.

### Il framework, costruito esplicitamente sull'expected value

Parte dall'assunto che il mercato sia efficiente e chiede: *cosa puo' portarlo fuori equilibrio?*
Poi elenca le variabili che spostano `EV = p*win - (1-p)*loss`:

| variabile | direzione |
|---|---|
| **ampiezza** del movimento | piu' grande → meglio |
| **velocita' / rate of change** | piu' rapido → meglio (dichiarata "la piu' importante") |
| **giorni consecutivi** nella stessa direzione | piu' sono → meglio |
| **assenza di notizie** | se il fondamentale e' cambiato, l'equilibrio si e' spostato → si evita |
| **"boringness"** dello strumento | piu' e' normalmente tranquillo → meglio |
| liquidazioni forzate, sentiment, capitalizzazione, quantificabilita' | contorno |
| **long vs short** | il long ha un **limite inferiore a zero**, lo short no → asimmetria strutturale |

**Esecuzione — "il lato destro della V"**: non si compra mentre scende; si aspetta la girata e si
compra la **rottura del massimo della barra precedente**, **stop al minimo del movimento**, si
**trascina lo stop sui minimi delle barre precedenti**, e il **target e' la media a 20 periodi**
(banda centrale di Bollinger), usata come "equilibrio". Win rate dichiarato con tutte le variabili
allineate: **70-80%**; senza: **~40%**.

Universalita' dichiarata: *"si applica a ogni prodotto e ogni timeframe, funziona come un
frattale"*. Esempi su azioni, oro-correlate, **Bitcoin**.

### Verdetto: **CANDIDATO** (il secondo)

Il sistema **completo non e' codificabile** — ammette lui stesso di tenere "una pagella mentale" su
un numero indefinito di variabili pesate a occhio. Ma i **primitivi lo sono**, e lui stesso dichiara
di scansionarli a macchina: giorni consecutivi, posizione rispetto alle bande di Bollinger,
distanza dalla media a 20, ampiezza della barra rispetto all'ATR abituale, picco di volume.

**Il claim piu' pulito e piu' facilmente falsificabile**, che non richiede alcuna discrezionalita':

> *"Se l'S&P scende del 3% per otto giorni di fila, la probabilita' che salga il nono non e'
> affatto ancora 50/50."*

Cioe': **P(inversione | N giorni consecutivi nella stessa direzione) cresce con N — e cresce di piu'
sugli strumenti normalmente tranquilli.** E' una misura di probabilita' condizionata su dati che
**abbiamo gia'**, 27 strumenti e 8 gruppi. Nessuna strategia, nessun parametro da tarare oltre N.

### Perche' il nostro NO-GO sulla mean reversion NON copre questo claim

Il test del 2026-07-08 usava **z-score N=10, Z=1**: deviazione **lieve**. Lui parla esplicitamente
della **coda estrema** — multi-sigma, waterfall, capitolazione di volume — e dichiara che **la
selettivita' e' l'intera strategia** (*"applicati in modo estremamente selettivo"*). Abbiamo
testato la mean reversion **mite**, non quella **estrema**. Sono due ipotesi diverse.

### La convergenza che chiude il blocco

Il suo setup ideale e' *"uno strumento eccezionalmente noioso che fa un movimento eccezionalmente
grande"*. Il nostro NO-GO sulla mean reversion aveva trovato, come residuo, MR **positiva sui
RANGER** (EURGBP +0.56, USDCAD +0.32) e **negativa sui TRENDER** (XAU −0.76, BTC −0.38).
"Noioso" = ranger. **Stessa affermazione, da due direzioni indipendenti.**

E si incastra con A1.4 e con Kichev: **il trend vive sugli strumenti volatili/illiquidi, la mean
reversion su quelli tranquilli/liquidi.** Non sono due claim: e' **un solo claim strutturale visto
da due lati**, e il nostro rho +0,857 ne misura una faccia.

---

# CONSUNTIVO DEL BLOCCO A1 (5 video, 72.190 parole, ~6,3 ore)

| # | fonte | classe | verdetto |
|---|---|---|---|
| A1.1 | Clement Ang | azioni USA, trend-pullback | **REFERENCE** — strumenti che non abbiamo, entrate in parte visive |
| A1.2 | Steven Dux | small cap USA, short | **SCARTATO** — barriera dirimente: prestito titoli e halt, non misurabile |
| A1.3 | Jeff Holden (SMB) | processo/psicologia | **REFERENCE** — layer operativo |
| A1.4 | Ted Zhang | stage analysis (Weinstein) | **CANDIDATO** |
| A1.5 | Lance Breunigstein | mean reversion estrema | **CANDIDATO** |

**Due candidati su cinque**, entrambi al quarto e quinto video. La regola di sospensione del funnel
**non scatta**.

## Cosa e' emerso che vale piu' dei singoli video

**1. Una tesi strutturale unica, sostenuta da tre fonti indipendenti e da una nostra misura.**
Trend e mean reversion **non competono**: si dividono il campo secondo la volatilita'/liquidita'
dello strumento. Kichev (A0) e Zhang lo dicono dal lato trend, Breunigstein dal lato reversione,
Dux lo pratica nell'angolo piu' illiquido esistente. La nostra unica misura controllata
(rho +0,857 fra volatilita' di gruppo ed E[R] della regola di trend) ne conferma **una faccia**.
La faccia opposta — *la mean reversion e' ordinata all'inverso* — **non l'abbiamo mai misurata**,
ed e' testabile sugli stessi dati e con lo stesso motore.

**2. Due primitivi puliti, entrambi senza discrezionalita' e sui nostri strumenti:**
- **stage analysis** (A1.4): condizionare allo stage 2/4 migliora l'espettanza? Aritmetica pura su
  medie settimanali a 10/20/30/40.
- **persistenza condizionata** (A1.5): P(inversione | N giorni consecutivi) cresce con N, e cresce
  di piu' sugli strumenti tranquilli? Probabilita' condizionata, zero parametri da tarare.

**3. Un vincolo che pero' morde.** Entrambi i candidati stanno in famiglie con budget quasi
esaurito: il **trend e' a round 2 di 3**, la **mean reversion** ha gia' un NO-GO piu' un LEAD in
forward. E resta **1 sola pre-registrazione esterna** nel trimestre. Non si possono fare entrambi.

## Statistiche dichiarate raccolte nel blocco

| fonte | claim | note |
|---|---|---|
| Clement Ang | "500%+" nel titolo vs **80% (2024) e 140% (2025)** nel video | titolo contraddice il contenuto |
| Clement Ang | **win rate 30%** | basso e coerente col payoff asimmetrico |
| Steven Dux | win 75% / 80-85% / 90%; 27k$ → 50M$ | **BS-test superato**: internamente coerente + vincolo di capacita' dichiarato |
| Ted Zhang | **nessun numero di performance** | anomalia positiva del canale |
| Lance Breunigstein | 70-80% con variabili allineate, ~40% senza; 100M$ verificati | il differenziale e' un claim, non una misura |

Prima osservazione sulla distribuzione: **non e' uniformemente gonfiata**. Due fonti su cinque non
fanno claim numerici o ne fanno di bassi; una supera il BS-test. Molto diverso dal 90-98% che
domina i titoli del canale.
