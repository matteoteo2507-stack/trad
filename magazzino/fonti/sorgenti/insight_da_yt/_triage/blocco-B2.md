# Blocco B2 — triage per video

---

## B2.1 — "World's #2 Futures Trader" (Marci Silfrain) · 83 min · 14.553 parole

`AVVM-FyewLg` · seconda al World Championship of Futures Trading (+320%). Pattern che chiama
**"little rizzy"**: dopo un calo iniziale si attende il rimbalzo, si traccia una trend line
discendente sui massimi; si misura la distanza **verticale dal minimo del pattern fino alla trend
line** e si **proietta quella stessa distanza sotto il minimo** = obiettivo della gamba successiva.
Bande di Bollinger (20, 2 SD) come **"realta'"**: fuori dalle bande = "fuori dalla realta'", deve
rientrare. Trend intatto finche' se ne formano di nuove; rotto quando una candela **chiude oltre**
la trend line.

### Verdetto: **REFERENCE**, con un primitivo testabile isolato

Il nucleo e' una **proiezione di movimento misurato** (measured move). E' aritmetica **una volta che
la trend line esiste** — ma l'ancoraggio della trend line resta visivo, e **lo ammette lei**:
*"potrei non accorgermene fino a tre candele dopo, e magari me la perdo"*.

⚠️ **Tutti gli esempi del video sono col senno di poi**: 1929, 2000, 2008, 2018, 2020, 2022, 2025,
disegnati su grafici gia' completi. E' esattamente il modo di argomentare che il nostro protocollo
non accetta come evidenza.

**Il primitivo isolabile**: *la proiezione del movimento misurato predice l'ampiezza della gamba
successiva meglio di una proiezione ingenua o casuale?* Non riguarda le entrate (i ritracciamenti
di Fibonacci come **ingresso** sono gia' NO-GO con NXT) ma i **bersagli** — cosa mai testata da noi.
Richiede pero' di meccanizzare la trend line.

### Una previsione falsificabile e datata, da verificare

Dichiara pubblicamente, in video e su X: **Bitcoin sotto 60.000, verso 50.000**. E' l'unico claim
prospettico e verificabile che il funnel abbia prodotto. **Da controllare**: abbiamo BTCUSD D1 nel
feed Dukascopy.

### Terza fonte a usare le bande di Bollinger, terzo ruolo diverso

| fonte | ruolo delle bande |
|---|---|
| **Crudele** (B1.3) | **classificatore di regime** (larghezza e pendenza) |
| **Breunigstein** (A1.5) | **bersaglio** della reversione (la media a 20 = equilibrio) |
| **Silfrain** (B2.1) | **misura di estensione** ("dentro/fuori dalla realta'") |

Stesso oggetto matematico, tre funzioni diverse, tre fonti indipendenti. Se testeremo qualcosa sulle
bande, conviene testarne **il ruolo**, non "le bande".

### Euristica non misurabile ma coerente col filo principale

*"Quando la notizia arriva sui telegiornali generalisti — non su CNBC o Bloomberg — e' gia'
prezzata. E quando mi telefonano amici che non tradano, e' finita."* E' un proxy di **estremo di
sentiment**, cioe' la stessa famiglia "estensione estrema → inversione" vista dal lato del
posizionamento. Aneddotico, non misurabile con i nostri dati, ma converge.

---

## B2.2 — "Making $500,000" (Tori Trades) · 71 min · 14.886 parole

`VTEQ2fhGLqE` · **trend line** su futures a 4 ore (soprattutto **platino**, poi rame e petrolio).
Due setup: **rimbalzo** sulla linea e **rottura** della linea (il suo principale).

### La definizione di trend line piu' MECCANIZZABILE del funnel

- **2-3+ punti di contatto**
- **almeno una settimana di dati** dietro la linea (dal primo contatto all'ingresso, su 4 ore)
- **basso rischio** = distanza contenuta fra il punto di rottura e la linea opposta
- **"action line"** = la linea rotta, dice quando entrare · **"safety line"** = la linea opposta,
  definisce lo stop e **lo trascina** man mano che si formano nuovi contatti
- linea disegnata **spessa** (4 pixel), **niente magnete**: e' esplicitamente una **fascia di
  tolleranza**, non una retta
- struttura "a ventaglio": il precedente punto B diventa il nuovo punto A

**Dato misurato da lei**: le rotture a **2 contatti** hanno **win rate piu' alto** ma **perdita
media maggiore** rispetto a quelle a 3. E' un trade-off misurato sui propri dati, non un'opinione.

### Verdetto: **REFERENCE**, ma segnala un buco reale nel nostro registro

La linea resta tracciata a mano e lei lo rivendica (*"niente indicatori, niente magnete, la disegno
io"*). Pero' i criteri che da' — conteggio dei contatti, ampiezza minima, fascia di tolleranza —
sono **sufficienti a meccanizzarla**, piu' di quanto lo fossero Crooks (A2.3) e Silfrain (B2.1).

⚠️ **Il buco**: i nostri **384 trial sui livelli hanno testato solo livelli ORIZZONTALI** — swing
S/R, PDH/PDL, numeri tondi, order block, FVG, EQH/EQL, POC/VWAP. **Le linee INCLINATE non sono mai
state testate.** Economicamente e' la stessa famiglia ("il prezzo reagisce a una retta"), quindi il
prior e' pessimo; ma **letteralmente non e' coperta**, e **tre fonti indipendenti** ci costruiscono
sopra l'intero metodo:

| fonte | uso della trend line |
|---|---|
| **Crooks** (A2.3) | la **rottura** come cancello d'ingresso |
| **Silfrain** (B2.1) | ancoraggio della **proiezione** del movimento misurato |
| **Tori** (B2.2) | **rimbalzo e rottura**, con criteri numerici espliciti |

**Nota che la separa dalle altre fonti**: dice esplicitamente *"lo stesso setup funziona molto
meglio su platino che su petrolio — devi testarlo tu, non credermi sulla parola"*, e racconta di
aver impiegato **un anno intero** a passare da intraday a swing, pubblicamente e male.
E' l'atteggiamento piu' vicino al nostro che il canale abbia mostrato.

---

## B2.3 — "Gap up short" (Chris Verma) · 15.680 parole

`EcTRlLYvhXU` · small cap USA, top-20 su Kinfo (verificato), 3K -> 2,1M con **questa sola
strategia**. E' il **primo trader esplicitamente SISTEMATICO** di tutto il funnel, e l'unico che
parli il nostro linguaggio: back test, expectancy, profit factor, database costruito a mano.

### La strategia nella sua forma pura ("opening print")

| elemento | specifica |
|---|---|
| universo | small cap USA, **market cap < 100 M** (max 200 M), institutional ownership **< 40%** |
| trigger | gap in pre-market **>= +100%** su hype/PR, non su catalyst reale |
| entrata | **short all'apertura** (opening print) |
| stop | **percentuale fissa larga, +75% / +150% dall'entrata** |
| uscita | **cover alla chiusura** della stessa giornata |
| filtro di gestione | **regola delle 10:00** — se alle 10:00 il prezzo e' **sopra il prezzo di apertura**, l'expectancy diventa **negativa**: ridurre, chiudere, o girare long |
| conferma | volume **decrescente** dopo l'apertura |

Il razionale economico e' **strutturale, non tecnico**: societa' fondamentalmente scadenti che si
finanziano diluendo (warrant, ATM, direct offering) + bag holder di lungo periodo che aspettano
liquidita' per uscire. Il picco **e'** l'evento di liquidita' in cui chi deve vendere vende. Non e'
"pattern", e' **flusso di offerta forzata**.

### I due passaggi che valgono per NOI (indipendenti dall'universo)

**1) Lo stop stretto DISTRUGGE l'edge quando i tuoi stop sono la liquidita' che il mercato cerca.**
Dice esplicitamente che usare il **massimo pre-market** come stop e' peggio di uno stop percentuale
largo, perche' il massimo pre-market e' **dove gli stop stanno tutti insieme** e il movimento e'
costruito per raccoglierli, per poi crollare subito dopo. Con stop largo: **win rate alto**, R:R
brutto (perdite > vincite), ma **profit factor > 1,5**. E aggiunge la frase che ci riguarda:
*"va contro la saggezza convenzionale del 3:1, l'ho smontata coi dati"*.

Questo **converge esattamente** con il nostro risultato NXT: lo stop wide non salvava la
continuazione, ma nel **fade** l'entrata larga e' quella che regge — e con il nostro dato che il
**12,7% degli stop apre oltre il livello**. La lezione trasferibile: **la larghezza dello stop non
e' una preferenza di rischio, e' un'ipotesi su chi c'e' dall'altra parte.** Se il prezzo e'
manipolato verso i cluster di stop, lo stop stretto e' un contributo alla controparte.

**2) L'edge decade e lui LO MISURA, non lo racconta.** Il pattern "pop and drop" (short a +20/40%,
mean reversion immediata) era la sua unica strategia nel 2020-2021 ed **e' morto**: stessa mossa
del 20%, ma lo spike medio e' passato da ~10% a ~50%, quindi "indovinare il top" non e' piu'
possibile. Causa dichiarata: **volume 10x** (da 5-10 M a 50-100 M a fine giornata) e
**affollamento del lato short** (broker specializzati, piu' capitale, stessi trader con size 5x).
Adattamento: non anticipa piu' il top, entra sul **backside** dopo che il grafico ha mostrato il
cedimento (candela di topping + volume in calo) — **stessa media di prezzo, ma senza drawdown**.

### Verdetto: **REFERENCE forte** — non trasferibile, ma e' il modello di come si lavora

**Non e' un CANDIDATO** per noi, e i motivi sono duri e non aggirabili:

- **universo inaccessibile**: serve un broker specializzato con locate hard-to-borrow (Schwab e IBKR
  non li hanno), 25k per la PDT rule, e i costi di prestito 1-2% del prezzo del titolo — che lui
  stesso dice **negano l'edge se salgono al 5%**
- **non e' testabile coi nostri dati**: non abbiamo dati equity small cap, ne' float/market cap/
  short interest, ne' lo storico dei false print pre-market che lui **cancella a mano** perche'
  altrimenti falsano il back test
- **rischio di coda non simulabile**: halt, gap oltre lo stop, squeeze del 300% su float da 500k
- **la meta' dei suoi risultati e' discrezionale** e lo dichiara: **70% sistema / 30% discrezione**,
  con il "recycling" (short i pop / cover i drop dentro il range) che e' pura esecuzione manuale a
  1 minuto per ore

Ma **il metodo con cui e' arrivato alle sue regole e' il nostro**, e in un canale di 45 video e'
la prima volta: back test su Polygon per anni di storia, database **ripulito a mano** dai trigger
falsi, expectancy misurata **condizionata** (ora del giorno, volume, estensione %, float, market
cap, institutional %), **profit factor** come metrica primaria sopra win rate e R:R, e la
**consapevolezza esplicita del decadimento dell'edge** con la causa (affollamento) e la misura
(volume 10x).

### Cosa registro come convergenza

- **"non anticipare, aspetta la conferma"** — quarta formulazione indipendente. Qui e' quantificata:
  stessa media di prezzo, ma drawdown quasi nullo invece del 40%.
- **"estensione estrema -> inversione"** — quarta fonte. Qui con il meccanismo economico piu'
  concreto di tutto il funnel: **diluizione + bag holder**, non psicologia.
- ⚠️ **contro-convergenza sullo stop**: tutto il resto del canale predica stop stretti e R:R 1:3.
  Lui li **falsifica coi propri dati** sul suo universo. Va tenuto come **avvertimento sul prior**:
  il R:R "giusto" e' una **conseguenza misurata** della struttura del mercato, non una regola.

---

## B2.4 — "Exact entry system" (Ariel, Real Simple Ariel) · 13.203 parole

`YzYDUEUOZ4k` · 30k (2020) -> oltre 10 M. Swing trader su azioni USA, **solo daily + 5 minuti**,
nient'altro. Sei setup nominati, tutti con entrata e stop specificati.

### I setup, come li dichiara

| setup | trigger | stop |
|---|---|---|
| **EP** (episodic pivot) | gap up su **sorpresa di utili E fatturato**, volume del giorno **3-7x** la media (es. da 4 M a 12-30 M azioni) | minimo del giorno |
| **HVC ritardato** (delayed high volume close) | **non** compra il gap; traccia una linea orizzontale sulla **chiusura del giorno ad alto volume** e compra la **rottura** di quella linea nei giorni successivi | minimo del giorno d'acquisto |
| **flat base breakout** | consolidamento con **top piatto**, rottura sopra il **massimo del giorno precedente**, medie 10/20/50 strette | minimo del giorno prec. se la candela e' stretta, altrimenti minimo del giorno |
| **undercut & rally** | il prezzo **buca** un minimo precedente e **rientra** sopra | sotto il minimo del wash-out |
| **MA undercut & rally** | stesso schema ma contro una **media in salita** | idem |
| **high tight flag** | consolidamento **3-5 settimane** stretto dopo un EP, rottura della meta' superiore | minimo del giorno |

**Uscite** (identiche per tutti): trim su 3-5 giorni di forza, poi **trailing su media in salita**
(10 -> 20 -> 50 a seconda della forza). Regola di trailing esplicita: *"finche' non CHIUDE sotto la
media che ho scelto, puo' ritestarla tre volte, va bene"*, con lo stop mentale che sale a ogni
minimo di pullback confermato.

**Sizing**: posizione dimensionata sull'**ADR** del titolo, non fissa. Titolo lento (3%/giorno) ->
15-20% del portafoglio; titolo veloce (8%/giorno) -> 8-10%. Obiettivo: **rischio di portafoglio
costante ~0,4-2%** per trade. Piu' **progressive exposure**: si aggiunge una nuova posizione solo
se quella precedente sta gia' funzionando.

### Verdetto: **REFERENCE**, con **un ponte verso qualcosa di testabile**

Non e' trasferibile alla lettera: e' azionario USA, richiede **dati sugli utili** (sorpresa su EPS e
fatturato), **volume relativo** affidabile e **classificazione settoriale** (parla dei 177 industry
group e di operare solo nei top 30). Non abbiamo nulla di tutto cio'.

Ma due elementi meritano di essere isolati perche' **non dipendono dall'azionario**:

**1) L'EP e' il PEAD travestito.** Gap su sorpresa di utili + volume anomalo + deriva che continua
"per 6-8 trimestri" e' letteralmente il **post-earnings announcement drift**, una delle anomalie
meglio documentate in letteratura. E' l'**unico setup incontrato in tutto il funnel con un
supporto accademico indipendente dal canale**. Non e' un motivo per costruirlo — non abbiamo il
dato — ma e' un motivo per **non trattarlo come folklore** se un giorno l'universo si allargasse.

**2) La "forza relativa di gruppo" e' momentum cross-sectional, e QUELLO lo possiamo testare.**
La sua regola operativa — *"opera solo nei gruppi che scendono meno quando il mercato scende e
salgono di piu' quando sale"*, e *"non comprare un minatore d'oro se i futures sull'oro sono
deboli quel giorno"* — e' una **selezione cross-sectional per gruppo**, non un pattern grafico.
E il **nuovo feed Dukascopy D1 (27 strumenti, 8 gruppi)** costruito per il playground contiene
esattamente la struttura che serve: piu' strumenti, raggruppati, stessa storia, stesso costo.

⚠️ **Attenzione**: e' un'idea, **non** un candidato. Rientra nella famiglia trend following, per la
quale il registro segna **round 2 di 3 gia' speso**, e va incrociata con il lead del playground
(rho +0,857 fra volatilita' di gruppo ed E[R]) prima di spendere qualunque cosa. Va nel registro
come **collegamento**, non come proposta.

### Contro-convergenza da registrare: le trend line inclinate

Dopo Crooks (A2.3), Silfrain (B2.1) e Tori (B2.2) che ci costruiscono sopra l'intero metodo,
Ariel le **rifiuta esplicitamente** e con la motivazione che avremmo dato noi:

> *"Non mi piacciono le linee discendenti perche' sono troppo soggettive: c'e' chi le disegna sui
> massimi degli stoppini, chi sulle chiusure, chi ci fa passare gli stoppini attraverso. Preferisco
> le linee orizzontali, dove posso dire: sopra e' buono, sotto e' cattivo."*

E aggiunge una posizione **opposta a Tori** sul retest: *"i grafici piu' forti del mondo non fanno
il retest — se lo fa, non e' forte come pensi"*. Quindi il funnel **non e' concorde** sulle linee
inclinate: 3 a favore, 1 contro, e il contrario e' argomentato su **falsificabilita'**, non su
preferenza. Il buco nel nostro registro rimane reale (mai testate), ma il prior si abbassa.

### Convergenze

- **"non anticipare, aspetta la conferma"** — quinta formulazione. Qui: non comprare il gap,
  aspettare la rottura dell'HVC.
- **"non operare in mezzo al range"** — settima formulazione, in forma di FOMO: comprare quando le
  medie sono **larghe** (prezzo esteso) produce chop; comprare quando sono **strette** produce il
  movimento. E' la stessa cosa che dicono gli altri sei, detta come compressione della volatilita'.
- **trailing su media mobile** — ⚠️ da leggere alla luce del nostro test del 14/08: su 3 lookback
  l'**uscita a tempo** batte o appaia il trail. Lui stesso porta **due esempi di trail che gli
  hanno restituito il 75% del guadagno** (Toast, Nvidia). Nessuno di noi due ha un caso a favore.

---

## B2.5 — "6.000 -> 10 M" (Brando, Elite Options Trader) · 12.321 parole

`yLuH8YZXORQ` · opzioni su SPX, weekly e 0DTE. Circa **il 45% del video e' mindset** (tre tratti del
trader di successo, FOMO, pazienza) — materiale gia' coperto e non azionabile.

### Cosa dichiara come metodo

Livelli di supporto/resistenza su **daily/weekly/monthly**, rifiuta esplicitamente i livelli
intraday (*"5 o 10 minuti va bene per quel giorno, ma i setup migliori li vedi solo zoomando
fuori"*), **numeri tondi** come livelli privilegiati (6.000, 5.000), e attende una **conferma** di
2 candele settimanali con minimi crescenti prima di entrare. Esempi: fondo 2018 (2.346) riconquistato
nel 2020; fondo 2022 (3.491) a ~100 punti dal massimo 2020; fondo aprile 2025 (4.835) contro il
massimo 2022 (4.818).

**Sizing "for zero"**: niente stop. La dimensione della posizione **e'** la perdita massima
accettata. Invece di 5.000 con stop al -20%, compra 1.000 e li considera gia' persi. Motivo
dichiarato: un'opzione puo' fare -60% un giorno e +300% il giorno dopo, e uno stop stretto
raccoglie solo il primo movimento.

### Verdetto: **SCARTATO** — famiglie chiuse, tranne un'ipotesi condizionante

Due delle tre gambe cadono direttamente nel registro:

- **livelli come zone di reazione** -> 384 trial pre-registrati, NULL su ogni timeframe
- **numeri tondi** -> NULL, CLOSED (e il round grid .80/.20 e' gia' uno dei 2 budget esterni spesi)

Il *claim* di **">80% di probabilita'"** e' una statistica dichiarata: si scarta per protocollo,
come tutte le altre del canale. E la selezione degli esempi e' **il caso peggiore visto finora**:
quattro fondi di mercato scelti **col senno di poi** su 7 anni, con i numeri che "tornano" perche'
sono stati cercati sapendo gia' dove guardare.

**L'unica cosa che non e' gia' nel registro** e' la sua condizione di attivazione:

> *"Ad agosto 2024 il mercato ha ritestato il massimo di luglio e la maggior parte dei trader ha
> comprato la rottura. Ma ad agosto non c'era riunione Fed — non c'era il catalizzatore. Chi ha
> preso il movimento ha aspettato settembre, la riunione, il taglio dei tassi."*

Cioe': **il livello da solo non basta; serve un evento macro in calendario che lo attivi.**
Aggiunge un numero verificabile: dopo il FOMC il movimento medio dell'S&P e' **~1,7%** con
volatilita' **~25% superiore**.

⚠️ **Come va registrato.** I nostri 384 trial hanno testato i livelli **incondizionatamente**: mai
condizionati alla presenza di un evento macro in calendario. Letteralmente e' un buco, come le
trend line inclinate. **Ma la conclusione operativa e' opposta**, e vale la pena scriverla:

- il calendario macro (FOMC, CPI, NFP) e' **noto in anticipo** e **pubblico**: e' il posto piu'
  affollato del mercato, l'esatto contrario del "playground" che stiamo cercando
- riaprire i livelli condizionandoli a un evento **moltiplica lo spazio di ricerca** su una famiglia
  che ha gia' prodotto 384 trial di NULL: e' il caso da manuale di *"ritocchiamo e riproviamo"* che
  il ciclo di vita vieta senza **evidenza esterna nuova**
- questo video **non e' evidenza esterna nuova**: e' un aneddoto selezionato a posteriori

Quindi: **annotato come buco, NON come proposta.** Se un giorno una fonte indipendente e
quantitativa portasse una misura di reazione ai livelli condizionata al calendario, allora si
riaprirebbe. Non prima.

### L'unica convergenza utile

**"Size for zero" e' la terza fonte in questo blocco a dire che lo stop stretto distrugge l'edge**,
dopo Verma (B2.3, stop percentuale largo perche' gli stop stretti *sono* la liquidita' cercata) e
in tensione con il resto del canale. Qui il meccanismo e' diverso — la gamma delle opzioni, non la
manipolazione — ma la forma e' identica: **quando il rumore a breve e' grande rispetto al segnale,
lo stop stretto converte movimenti favorevoli in perdite certe.** E' esattamente il nostro dato
NXT (12,7% degli stop aperti oltre il livello) visto da un'altra angolazione.

---

# Consuntivo blocco B2 (5 video, 70.643 parole)

| # | fonte | esito |
|---|---|---|
| B2.1 | Marci Silfrain — measured move + Bollinger | REFERENCE |
| B2.2 | Tori Trades — trend line meccanizzabile | REFERENCE (apre il buco "linee inclinate") |
| B2.3 | Chris Verma — gap up short small cap | REFERENCE FORTE (metodo, non strategia) |
| B2.4 | Ariel — EP / HVC / flat base | REFERENCE (ponte: momentum cross-sectional di gruppo) |
| B2.5 | Brando — livelli + catalizzatore macro | SCARTATO (famiglie chiuse) |

**Nessun CANDIDATO nuovo dal blocco B2.** Ma tre acquisizioni che pesano piu' di un candidato:

1. **La larghezza dello stop e' un'ipotesi, non una preferenza.** Tre fonti indipendenti in questo
   blocco (Verma, Brando, e implicitamente Ariel col sizing su ADR) dicono che lo stop stretto
   distrugge l'edge quando il rumore a breve e' grande. Converge col nostro 12,7% di gap oltre lo
   stop su NXT. **Questa e' la cosa piu' azionabile emersa dal funnel finora.**
2. **Il buco delle trend line inclinate esiste ma il funnel non e' concorde** (3 pro, 1 contro
   argomentato su falsificabilita').
3. **Verma e' il primo interlocutore metodologicamente compatibile** in 45 video: back test su anni,
   dati ripuliti a mano, expectancy condizionata, profit factor, decadimento dell'edge misurato con
   la causa. Vale come **conferma esterna del nostro metodo**, non come strategia da importare.
