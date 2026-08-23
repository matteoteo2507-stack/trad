# Blocco C3 — masterclass lunghe (5 video, 109.879 parole)

---

## C3.1 — "Options trading for beginners" (Usman Ashraf) · 20.839 parole

`6Bdv-_YUQ0s` · trader verificato 7 figure, 10+ anni di opzioni, fondatore di Options Hub.
E' un **corso**, non una strategia: circa il 90% e' meccanica delle opzioni.

### Cosa contiene davvero

Strike / premio / scadenza spiegati con l'analogia casa e auto; call e put; in the money vs out of
the money; e poi i **greci**: delta, gamma (accelerazione del delta, esplode vicino alla scadenza),
theta (decadimento temporale, si aggrava avvicinandosi alla scadenza), vega e **implied volatility**
con il meccanismo **IV rush / IV crush**.

Le sole regole operative che dichiara: opera **sempre gli stessi sottostanti** per conoscerne la
"personalita'" di IV; scala fuori a **30/20/20/30%**; in day trading punta a uscire dal 50% quando
lo strike e' in the money; sceglie lo strike guardando la **liquidita'** della catena.

### Verdetto: **REFERENCE tecnico** — utile come manuale, non come fonte di strategia

Non c'e' nulla da testare: lui stesso lo dice, *"non c'e' nessuna strategia segreta su come
operarle"*. Le opzioni sono uno **strumento di esecuzione**, non un edge: la direzione la deve
fornire qualcos'altro.

**Perche' vale comunque la pena averlo registrato**, e' l'unico punto di questo video che tocca il
repo: la meccanica dei greci spiega **perche' le tre fonti del funnel che operano opzioni** (Brando
B2.5, Z C1.5, questo) **rifiutino tutte lo stop stretto**, ognuna a modo suo:

- il premio di un'opzione puo' fare −60% e poi +300% sullo stesso movimento del sottostante, perche'
  dipende da **delta + gamma + IV**, non solo dal prezzo;
- quindi uno stop sul **premio** viene colpito da rumore che non ha nulla a che vedere con la tesi;
- da qui il **"size for zero"** (Brando) e il *"il mio stop lo guardo sul grafico del sottostante,
  non sul prezzo dell'opzione"* (Z).

E' la **spiegazione meccanica** della convergenza sullo stop largo che il funnel ha prodotto cinque
volte. Non e' una prova che valga anche per noi (noi non operiamo opzioni), ma chiarisce che quelle
tre voci **non sono tre conferme indipendenti**: sono **una sola** osservazione sulla non-linearita'
del premio. Le conferme davvero indipendenti restano quelle di Verma (small cap, manipolazione dei
cluster di stop) e Desi (futures, rumore intraday) — **due**, non cinque.

⚠️ Correzione a quanto scritto nei consuntivi B2 e C2: **la convergenza sullo stop largo va contata
2-3, non 5-6.** Il fatto resta rilevante e coerente col nostro 12,7% di gap oltre lo stop, ma non ha
il peso che sembrava avere sommando fonti che condividono la stessa causa.

---

## C3.2 — "World's best NQ scalper" (Trader Kane) · 14.467 parole

`HNuRp9Z1bMs` · **record del payout piu' grande nella storia delle prop firm: 2,3 M $**; a dicembre
ha portato 130.000 $ a oltre 1,4 M in circa un mese. Opera **solo NQ**.

### Il modello, ridotto all'osso

> *"Voglio vedere il prezzo ribilanciare al 50% del range e poi continuare con il trend. Ho
> costruito un modello attorno a quello. Non mi serve un movimento grande: mi serve quel colpo
> singolo, ogni giorno, e poi ho finito."*

Operativamente: allineamento **daily -> H4 -> H1** dello schema accumulazione/manipolazione/
distribuzione. Attende che il prezzo **manipoli** sopra il massimo del periodo precedente (dove
stanno gli stop di chi e' entrato prima), poi entra sulla rottura verso il **50% del range**.
Finestra oraria: **9:15-11:30 EST**, con particolare attenzione alle **10:00** (apertura della
nuova candela H4). Filtro di correlazione: divergenza **NQ vs ES**. Gestione: a **break even il
prima possibile**, sempre — e lo mette nei *contro*, precisando che *"e' proprio questo che lo
rende profittevole"*.

### Verdetto: **SCARTATO come strategia** — ma contiene **il claim piu' vicino a un nostro lead**

Le entrate (inversioni, divergenza SMT, power of three) sono famiglia CLOSED. La finestra oraria e
l'allineamento a tre timeframe sono condizioni, non una famiglia nuova.

**Ma la tesi portante e' una sola frase, ed e' misurabile:**

> **"Il prezzo torna al 50% del range."**

Non e' un pattern grafico: e' un'affermazione sulla **distribuzione del ritorno verso il centro di
un range**, cioe' **mean reversion di breve orizzonte**. Ed e' — leggermente riformulata — la stessa
famiglia del nostro **unico lead positivo misurato**:

| | Kane | noi (FADE, sottoprodotto NXT) |
|---|---|---|
| tesi | il prezzo estende oltre un estremo e **rientra verso il centro** | il prezzo estende e **rientra**: short-horizon mean reversion |
| entrata | dopo lo sweep del massimo/minimo precedente | dopo l'estensione oltre il livello |
| durata | ore, chiude in giornata | mediana **5 ore** |
| esito | aneddotico, non misurato | **+0,31R**, holdout + 3x costi, gia' in forward test |

⚠️ **Attenzione a non farne piu' di quello che e'.** Non e' una conferma indipendente del FADE:
Kane non porta un numero, porta screenshot. Ma e' **la terza fonte del funnel** (con Asselin C1.4 e
Ascetoni C2.4) il cui meccanismo dichiarato coincide con la direzione che **noi abbiamo gia'
misurato positiva** — mentre la direzione opposta (continuazione dopo il ritracciamento, Omar
C2.3 = NXT) e' quella che **abbiamo misurato a −0,44R**.

**Questo e' il pattern piu' importante emerso dal blocco C**: quando le fonti convergono su
qualcosa che abbiamo misurato, convergono sul **fade**, non sulla continuazione.

### La frase che chiude il cerchio con C1.3

Alla domanda "quanto e' meccanico e quanto discrezionale":

> *"Penso che un robot potrebbe prendere il modello e, se mi sedessi a scrivere la logica per bene,
> potrebbe essere abbastanza meccanico. La realta' e' che **la discrezione e' il mio edge**. La
> prima cosa che dico a chiunque insegni e': questa parte fara' schifo, perche' **non posso
> insegnarti la mia intuizione**."*

E' la stessa posizione di Perez (C1.3) e l'opposto di Mayne (C1.1). Detta pero' da chi detiene il
record di payout del settore, e detta **contro il proprio interesse commerciale** (sta vendendo un
modello). Vale la pena registrarla senza addolcirla: **se ha ragione, la parte trasferibile del
suo risultato non e' il modello.** E se ha ragione, il modello venduto ai suoi studenti non e' cio'
che ha prodotto i 2,3 M.

---

## C3.3 — "World's best prop firm trader" (Jadecap / Kyle) · 18.406 parole

`8OX-mcSHWhg` · ha **battuto il record di Kane**: 2,5 M $ in un singolo payout, ~4,5 M totali.
Opera indici, prevalentemente NQ.

### Il modello

Parte da una ricostruzione storica: nel floor trading si **vedeva** dove stavano gli stop; con
l'elettronico non si vede piu', quindi li si **deduce** dai massimi e minimi non ancora presi
(ultimi ~3 giorni, piu' i range di sessione **asiatica** e **londinese**).

Lo "swing failure" che assegna come compito ai suoi studenti e' l'unica regola completamente
specificata del video:

> raid sotto il **minimo del giorno precedente** -> attendere una **chiusura di ritorno sopra** quel
> minimo -> **long**, stop sotto il nuovo minimo creato, target il **massimo del giorno precedente**.

Piu' tre condizioni:

1. **giornata rialzista "classica"**: il minimo del range asiatico o di Londra dovrebbe essere
   preso **prima** che il prezzo salga. *"Se non prendiamo i minimi asiatici, la mia probabilita' di
   successo crolla."* Se **entrambi** i lati del range sono gia' stati presi all'apertura di New
   York, si aspetta **consolidamento**.
2. **finestra oraria**: il minimo/massimo intraday degli indici si forma prevalentemente fra le
   **9:30 e le 10:30 EST**; chi opera fuori da quella finestra si posiziona male per costruzione.
3. **stop larghi**: *"la gente ha stop troppo stretti — in questo scenario userei il minimo del
   giorno precedente, perche' so che li' sotto ci sono un sacco di ordini"*.

Gestione: mai aggiungere se lo stop della prima posizione non e' gia' stato spostato e parte del
rischio tolta. R:R minimo **1:1,5**. E la tesi esplicita: *"la gestione del trade e' cio' che
aggiunge piu' edge di qualunque altra cosa — dai lo stesso segnale a 10 trader e vince chi gestisce
il rischio"*.

### Verdetto: **SCARTATO** — ma e' la quarta fonte che converge sul FADE, non sulla continuazione

Lo swing failure che insegna **e' il nostro fade**: estensione oltre un estremo, rientro,
posizione nella direzione del rientro, target l'estremo opposto. Stessa forma di Kane (C3.2),
Asselin (C1.4), Ascetoni (C2.4).

**Cio' che ha di specifico e che noi NON abbiamo testato** sono le due condizioni di contesto:

- **il raid del range di sessione precedente come prerequisito** (asiatica/Londra prima di New York);
- **la finestra oraria in cui si forma l'estremo di giornata** (9:30-10:30 EST sugli indici).

⚠️ Entrambe cadono sotto lo stesso avvertimento gia' scritto per Tanya (C1.2) e Brando (B2.5): sono
**condizionamenti** che, applicati a una famiglia gia' falsificata, moltiplicano lo spazio di
ricerca. Con un'aggravante specifica: sono **legate agli indici azionari USA**, che non sono nel
nostro universo, e la loro struttura di sessione (apertura di cassa alle 9:30) **non esiste** sul
forex e sulle materie prime che operiamo, dove il mercato e' continuo. **Non sono trasferibili**,
non solo non testate.

### La cosa piu' utile del video non riguarda l'entrata

> *"La gestione del trade e la gestione del rischio sono cio' che aggiunge piu' edge a qualunque
> sistema. Puoi dare lo stesso segnale profittevole a 10 trader: chi sa aggiungere alla posizione e
> gestire il rischio finira' molto avanti rispetto a chi ha una sola entrata, una sola uscita, un
> solo target."*

E la regola concreta che ne deriva: **non si aggiunge mai senza aver prima spostato lo stop della
posizione esistente e tolto rischio dal tavolo** — altrimenti 1R + 1R = una perdita da 2R.

⚠️ **Attenzione: per noi questa affermazione e' vera solo a meta', ed e' importante dire quale.**
Nel nostro impianto la "gestione" e' **parte della regola pre-registrata** e viene misurata insieme
al resto: il nostro test sulle uscite (14/08) ha mostrato che l'**uscita a tempo batte o appaia il
trailing** su 3 lookback, e il test sul **soffitto delle escursioni** ha mostrato che regole di
uscita apparentemente eccellenti **crollano contro un baseline random**. Cioe': la gestione puo'
spostare l'esito, ma **non e' una fonte di edge indipendente** — e crederlo e' il modo piu' rapido
per attribuire a se stessi cio' che sta facendo la volatilita'.

**Registrato come tensione esplicita fra la nostra misura e quattro fonti convergenti.** E' una
delle cose da mettere sul tavolo nella discussione sui binari, non da risolvere qui.

---

## C3.4 — "Parabolic short setup" (Marius Stamatiou) · 26.802 parole

`SInAfwX3X3A` · **+291% in un anno alle US Investing Championships**, 10 anni di attivita'.
Long-only momentum trader; questo e' il suo **unico setup short**, dichiarato come complementare.

### La specifica completa — e' la piu' precisa dell'intero funnel

**Filtro 1 — movimento percentuale rapportato alla capitalizzazione**, misurato **dall'ultima base
evidente** (non dall'inizio arbitrario del movimento):

| market cap | movimento minimo per interessarsi | soglia "estremo" |
|---|---|---|
| < 10 mld | **+200%** | 2-3x la soglia (600-1000%) |
| 10-100 mld | **+100%** | 2-3x |
| > 100 mld | **+50%** | 2-3x |

**Filtro 2 — struttura del prezzo.** Tre forme in cui il fenomeno parabolico si manifesta:

- **"formiche"**: molte candele verdi consecutive ma piccole -> **non opera**;
- **"verde-rosso"**: verdi interrotte da rosse -> **non opera**;
- **"da manuale"**: **2-4 candele verdi enormi**, ATR ampio, eventualmente con gap -> **e' l'unica
  che opera**, e **mai il primo giorno**: ne servono almeno due.

Trade-off che dichiara e risolve esplicitamente: *"il da manuale ha buona accuratezza ma e' raro;
gli altri sono frequenti ma hanno falsi segnali"* -> opera gli **ibridi** (formiche o verde-rosso
che **sfociano** in candele da manuale).

**Bonus 1 — volume**: il **volume piu' alto dell'anno** (sia in azioni sia in controvalore). Il
razionale e' preciso e invertito rispetto al senso comune: **volume enorme all'inizio** di un
movimento = istituzioni che accumulano (rialzista); **volume enorme sul climax** = affollamento
completo, non resta nessuno da comprare.

**Bonus 2 — numeri tondi**: primo tocco di una soglia psicologica (100, 500, 1000).

**Finestra temporale — regola dura**: *"do sempre due giorni. Se non funziona, lo cancello e non lo
guardo mai piu'."*

**Entrata (intraday)**: tre tattiche, tutte ancorate al **VWAP** classico di giornata — rottura
della struttura + perdita del VWAP; oppure rottura del VWAP; oppure fallita riconquista del VWAP.
Stop al massimo di giornata (o al massimo relativo precedente). **Rischio 0,5%** per trade.

**Numeri dichiarati**: win rate **85-90%** su questo setup contro **25-30%** sui suoi setup long
(*"opero nel fallimento, il mio sistema e' basato sull'asimmetria"*). ~10 occasioni molto buone e
~10 mediocri all'anno.

### Verdetto: **REFERENCE di alto valore** — non e' un candidato per noi, ma rafforza quello che
abbiamo gia'

**Perche' non e' un candidato**: universo azionario USA (serve market cap, float, volume in
controvalore, screening su 1.000 titoli al giorno) — dati che non abbiamo. E il **VWAP intraday**,
su cui poggiano tutte e tre le tattiche di entrata, e' **famiglia chiusa nel nostro registro**
(v2, 0/48 celle). Cosi' come i **numeri tondi** (NULL, CLOSED). Cioe' **entrambi i suoi appigli
operativi sono cose che abbiamo gia' misurato come nulle**, sul nostro universo.

⚠️ E il claim **85-90% di win rate** e' una statistica dichiarata, senza campione ne' metodo: si
scarta per protocollo come tutte le altre. Con un'aggravante che vale la pena scrivere: lui stesso
dichiara **~20 occasioni all'anno**, quindi anche prendendole tutte, in 10 anni il campione e' di
poche centinaia di trade **selezionati a mano**, senza baseline. Non e' un numero utilizzabile.

**Perche' vale comunque molto**: e' la formulazione piu' rigorosa mai incontrata del **CANDIDATO
che abbiamo gia' in lista** — *"estensione estrema -> inversione"* (Breunigstein, blocco A). E la
porta avanti su tre punti che noi non avevamo:

1. **la soglia di estensione va normalizzata** — lui la normalizza sulla capitalizzazione; noi
   dovremmo normalizzarla su **volatilita' dello strumento**, che e' l'analogo. E' esattamente la
   lezione del **KILL delle escursioni (14/08)**: una soglia assoluta non significa nulla senza un
   riferimento.
2. **la struttura conta piu' della quantita'**: lo stesso +300% e' operabile o no a seconda che sia
   arrivato in 2-4 candele enormi o in venti candeline. E' una condizione **misurabile** (rapporto
   fra il movimento e l'ATR delle candele che lo compongono) e **non e' nei nostri test**.
3. **la finestra di invalidazione temporale a 2 giorni**, che rende la regola falsificabile.

### Il razionale economico e' il migliore del funnel

Riflessivita' alla Soros: piu' persone condividono la stessa narrativa e agiscono, piu' rafforzano
il trend, finche' l'affollamento e' completo — a quel punto **basta una scintilla**. E porta un
esempio verificabile: dicembre 2024, i titoli quantum in climax top, il CEO di Nvidia dice che il
quantum computing e' *"a 15 anni di distanza"*, tutto crolla. *"Se lo stesso annuncio fosse arrivato
prima, non avrebbe avuto lo stesso effetto."*

E' lo stesso meccanismo di **Verma (B2.3)** — offerta forzata su titoli affollati — arrivato da un
mercato e da un lato completamente diversi.

**Cio' che porto via**: quando riapriremo il candidato "estensione estrema -> inversione", la
specifica va scritta **cosi'**: soglia normalizzata sulla volatilita', **condizione di struttura**
(pochi grandi movimenti, non tanti piccoli), **finestra di invalidazione temporale**, e baseline
random risk-matched. Non con le sue soglie e non con il suo universo.

---

## C3.5 — "One candle strategy" / first red day (Kyle Williams) · 29.365 parole

`2Ug0jyDvoek` · da poche migliaia a oltre **7 M $ di profitti verificati**, top 5 su Kinfo,
~1 M nel solo dicembre 2025. Small cap USA, prevalentemente short.

### Il setup: "first red day"

Criteri minimi (li chiama **la parte scientifica**):

- **almeno 2 giorni verdi consecutivi** (mai uno solo: *"le mosse di un giorno solo hanno probabilita'
  troppo casuali"*);
- **almeno +80/100%** sul movimento complessivo. E chiarisce il trade-off: 10 giorni verdi con +30%
  **non vale** — *"e' accumulazione ordinata, non una bolla"*;
- **espansione**: le candele devono diventare **piu' grandi** salendo, non piu' piccole. Se il range
  si contrae mentre il prezzo sale, e' un **segnale negativo**;
- **volume in espansione**: idealmente il volume del giorno di picco e' enormemente superiore ai
  precedenti. Se il volume **cala** mentre il prezzo sale, *"nessuno se ne interessa, quindi perche'
  dovrei io"* — e dichiara che **quasi mai** opera quel caso.

Il framing: *"tutti sanno cos'e' una bolla, ma pensano che accada una volta ogni 20-30 anni.
Immagina bolle che accadono **una volta a settimana**."*

Gestione: stop al **massimo assoluto della corsa** (*"se il titolo deve scendere, prima deve
smettere di salire"*); massimo **3 tentativi**, poi si ferma (*"tante volte ho dato 5-6 tentativi
e alla fine avevo ragione, ma ero solo in pareggio"*); copertura verso il **VWAP**; sistema di
**grading dei setup (C / B / A / A+)** con size proporzionata al voto.

Numeri che dichiara sulla propria attivita' complessiva — e sono **coerenti e informativi**:

> *"Shortare in generale e' un'idea ad **alto win rate ma basso rapporto rischio/rendimento**:
> vinco il 50-60-70% delle volte, ma i trade sono 1:1, a volte 2:1, raramente 4:1 o 5:1. Andare
> long e' l'opposto: vinco il 20-30-40% delle volte, ma quando vinco e' 5:1, 10:1, 15:1.
> **Entrambe le strade sono profittevoli, cambia come ci arrivi.**"*

### Verdetto: **REFERENCE** — non testabile da noi, ma **conferma una condizione strutturale precisa**

Universo inaccessibile per gli stessi motivi di Verma (B2.3): small cap USA, locate, halt, gap.
Il VWAP e' famiglia chiusa. Non c'e' un percorso di test.

⚠️ **Ma questa e' la SECONDA fonte indipendente, sullo stesso oggetto, a specificare la stessa
condizione di struttura**, e le due non si sono mai parlate (mercati e stili diversi):

| condizione | Marius (C3.4, US Investing Championships) | Kyle (C3.5, small cap) |
|---|---|---|
| estensione minima | 200% / 100% / 50% secondo market cap | 80-100% |
| durata | 2-4 candele, **mai il primo giorno** | **almeno 2 giorni verdi**, mai uno solo |
| **forma** | solo il "da manuale": **candele enormi con ATR ampio**; scarta le "formiche" (tante candeline) | le candele devono **espandersi** salendo; se si contraggono e' negativo |
| **volume** | **volume piu' alto dell'anno** sul climax = affollamento completo | volume **in espansione**; se cala, non opera |
| invalidazione | finestra di **2 giorni** | massimo **3 tentativi** |

**La convergenza non e' su "l'estensione estrema si inverte"** — quello lo dicono in cinque. E' su
**quale estensione**: *non conta quanto e' salito, conta se e' salito in pochi grandi movimenti con
volume crescente*. Due specifiche indipendenti, quasi identiche, con lo stesso razionale economico
(affollamento completo -> non resta nessuno da comprare).

**E questa condizione e' misurabile sui nostri dati.** Non richiede market cap ne' order flow:
richiede **range delle candele** e **volume**, che abbiamo. E' la traduzione operativa del nostro
CANDIDATO "estensione estrema -> inversione".

⚠️ Con l'avvertimento gia' scritto in C3.4 e non negoziabile: le soglie assolute (200%, 100%, 80%)
**non sono trasferibili** e non vanno lette senza baseline. Il KILL delle escursioni del 14/08 e'
nato esattamente da questo: soglie assolute che passavano 6/6 e 15/15 e che il **random
risk-matched** ha ribaltato.

---

# Consuntivo blocco C3 (5 video, 109.879 parole)

| # | fonte | esito |
|---|---|---|
| C3.1 | Usman Ashraf — corso opzioni | REFERENCE tecnico — **corregge il conteggio "stop largo"** |
| C3.2 | Trader Kane — 50% del range | SCARTATO — quarta fonte che converge sul **fade** |
| C3.3 | Jadecap — swing failure + sessioni | SCARTATO — condizioni non trasferibili (indici USA) |
| C3.4 | Marius Stamatiou — parabolic short | **REFERENCE di alto valore** — specifica il candidato |
| C3.5 | Kyle Williams — first red day | REFERENCE — **conferma indipendente della condizione di struttura** |

**Zero candidati nuovi. Ma il blocco C3 e' il piu' produttivo dell'intero funnel**, per due
risultati che non erano nei blocchi precedenti:

**1) La specifica del candidato "estensione estrema -> inversione" e' passata da vaga a scrivibile.**
Due fonti indipendenti (C3.4, C3.5) concordano che **la forma del movimento conta piu' della sua
ampiezza**: pochi grandi movimenti con **range in espansione** e **volume in espansione** -> si
inverte; tanti piccoli movimenti con volume calante -> non si inverte. Entrambe misurabili sui
nostri dati. Piu' una **finestra di invalidazione temporale** esplicita in entrambe.

**2) Le fonti convergono sul FADE, mai sulla continuazione.** Quattro fonti del blocco C
(Asselin C1.4, Ascetoni C2.4, Kane C3.2, Jadecap C3.3) descrivono meccanismi che coincidono con la
direzione che **noi abbiamo misurato positiva** (+0,31R). L'unica che descrive la continuazione
(Omar C2.3) descrive **esattamente** la strategia che abbiamo misurato a **−0,44R**. Non e'
evidenza statistica — sono aneddoti — ma e' una coincidenza sistematica fra cio' che il mercato
racconta e cio' che abbiamo misurato, e vale la pena averla scritta.

**3) Correzione al conteggio precedente**: la convergenza "stop largo" va contata **2-3 fonti
indipendenti**, non 5-6 (vedi C3.1): tre delle occorrenze erano trader di opzioni che descrivevano
la **stessa** causa — la non-linearita' del premio — non tre osservazioni distinte.
