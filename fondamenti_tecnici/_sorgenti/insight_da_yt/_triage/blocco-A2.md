# Blocco A2 — triage per video

Stessa procedura del blocco A1: lettura integrale, un video alla volta.

---

## A2.1 — "12 Years of Trading Knowledge in 2 Hours" (Umar Ashraf) · 119 min · 25.063 parole

`IUo5AwmsE9A` · fondatore di TradeZella. **Non e' una strategia**: e' un percorso di sviluppo del
trader in 5 stadi (novizio → sviluppo → intermedio → avanzato → pro).

### Verdetto: **REFERENCE / layer operativo**

Nessuna regola testabile. L'unico playbook concreto e' il **"morning top"** (gap down, prima ora,
movimento al rialzo **senza follow-through di volume**, poi rallentamento del tape o pressione in
vendita su un livello → short): e' **order flow intraday su ES/NQ**, quindi fuori dai nostri dati,
e il criterio centrale ("no follow-through") e' una lettura del tape, non una regola.

### Cosa vale la pena trattenere

**1. Metriche di diagnosi che non tracciamo.** Oltre all'R multiple, propone di misurare
**l'efficacia dello stop**: *quante volte il prezzo tocca il tuo stop e poi torna indietro?* Se
capita spesso, lo stop e' troppo stretto. E' una diagnosi che possiamo calcolare sui **nostri**
sistemi, ed e' complementare alla misura del gap-attraverso-lo-stop gia' fatta sul fade
(2026-08-14). Altre proposte: drawdown per trade, entrata troppo presto/tardi, uscita troppo
presto/tardi, aderenza alle regole.

**2. Regole di scala del rischio, numeriche.** Aumento della size **del 20-30% per volta**, mai di
piu'; **1-2 trade al mese** con rischio maggiorato ("una carta speciale"); si scala solo **fuori
dal drawdown**; dopo una serie molto positiva si riduce o ci si ferma (*"dopo tre settimane buone
ho restituito tutto in due giorni"*).

**3. Un'inversione utile sul ruolo della psicologia.** Sostiene che *"le emozioni sono
sopravvalutate"* negli stadi iniziali: se le emozioni ti dominano quando stai imparando, **la size
e' semplicemente troppo grande**. Le emozioni sono un problema **reale solo quando si scala**.
Riformula un problema psicologico come un problema di dimensionamento — utile e falsificabile in
linea di principio.

### Terza convergenza indipendente sul sizing graduato

Holden (A1.3) grada i setup A+/A/B/C in frazioni dello stop giornaliero; Breunigstein (A1.5) tiene
una "pagella" 0-10 su piu' variabili e ne ricava una classe di rischio; Ashraf parla di **rischio
dinamico** riservato agli stadi avanzati. **Tre fonti indipendenti convergono sul dimensionamento
scalato per convinzione** — ma **nessuna delle tre fornisce un metodo validato per assegnare il
grado**. Il "come si assegna A+ invece di B" resta, in tutte e tre, esperienza non misurata.
Registrato come convergenza sul *principio*, non come metodo importabile.

### Statistiche dichiarate

"Eight figure verified trader" (fondatore di TradeZella, quindi con conflitto d'interesse
sull'argomento journaling/dati). Nessun win rate, nessuna espettanza, nessun claim numerico di
strategia. Come Zhang: **niente da sottoporre al BS-test**.

---

## A2.2 — "STEAL This $100M Trading Strategy" (Pradeep Bonde / Stockbee) · 57 min · 10.535 parole

`mDNcx2Dhhms` · **Episodic Pivots (EP)**: azione **trascurata** da mesi + **catalizzatore** →
entrata in apertura del giorno 1, stop stretto, si cavalca il movimento.

Varianti dichiarate: EP classico (crescita di **fatturato**, la chiave: *"il fatturato conta piu'
degli utili"*, >= 39%, meglio a tripla cifra) · **turnaround** (durano piu' a lungo dei growth) ·
**story/theme** (AI, quantum, crypto-treasury) · **delayed reaction** · **EP 9 milioni** ·
"sugar babies" (25 titoli che ripetono mosse del 50%). Frequenza: 5-10/anno il classico,
**100-300/anno** con tutte le varianti.

### Verdetto: **SCARTATO** come strategia

Azioni USA singole; servono **dati fondamentali** (utili, crescita del fatturato, float, quote dei
fondi) che non abbiamo; e soprattutto **lo dichiara lui**: *"non e' meccanico, devi leggere la
notizia e capire quanto il titolo si muovera'"*, *"servono ottime capacita' analitiche"*,
*"servono quattro o cinque stagioni di earnings per prenderci la mano"*.

### Ma c'e' un primitivo che si stacca dal resto: **il volume anomalo come segnale**

La variante **EP 9 milioni** non usa fondamentali, notizie o interpretazione. Usa **solo il
volume**: un titolo che scambia un volume che **non ha mai scambiato in vita sua**. Testuale:

> *"Il volume anomalo e' esso stesso un'informazione."*
> *"Se un titolo ha un float di 5 milioni e ne scambia 50, un catalizzatore c'e'."*
> *"Non discuto col mercato."*

Racconta di aver comprato SPCE **senza sapere perche'**, solo per il volume mai visto (+134%), e di
averlo rifatto dopo un secondo picco di volume (+100-200%). L'ipotesi generalizzata e':

> **un picco di volume anomalo rispetto alla storia dello strumento stesso anticipa un movimento
> direzionale.**

**Secondo pezzo trasferibile — la reazione ritardata.** Sostiene che la reazione del **primo
giorno** al catalizzatore e' spesso sbagliata o rumorosa (gap, poi restituzione), e che il
movimento vero arriva **giorni dopo**; sugli short dichiara di entrare **sempre** in ritardo,
perche' il primo impulso viene comprato da chi pensa "il peggio e' prezzato". E' un claim
falsificabile sul **timing del drift post-evento**.

**Insieme diventano un test che usa solo prezzo e volume**: picco di volume come *proxy
dell'evento* + entrata immediata **contro** entrata ritardata.

### Perche' questo e' interessante dal punto di vista del budget

Sarebbe una **famiglia nuova**. Il nostro registro copre: livelli (CLOSED), trend (round 2/3),
mean reversion (NO-GO + LEAD), breakout intraday (NO-GO), stagionalita' (NO-GO), griglia di prezzo
(CLOSED). **Il volume come segnale direzionale non e' mai stato testato.** La ricerca livelli v2
aveva testato il volume come **profilo/livello** (POC, VWAP, AVWAP → 0/48 celle), che e'
un'ipotesi diversa: li' il volume definiva *dove*, qui definirebbe *quando*.

### Caveat sui dati, da mettere subito

Il volume che abbiamo e' **problematico e va dichiarato**: sui cambi Dukascopy e' un **proxy di
conteggio tick**, non volume scambiato (limite gia' segnalato nella v2); sui CFD e' volume del
broker, non di borsa. Un test sul volume anomalo su FX misurerebbe l'attivita' di quotazione, non
gli scambi. Utilizzabile con piu' fiducia su indici, metalli, energia e crypto.

---

## A2.3 — "Trading Made SIMPLE · 3 Steps" (Alistair Crooks) · 66 min · 13.946 parole

`9D9ck-ZI6V0` · gestore UK, **swing trading su FOREX**. **I nostri strumenti, il nostro
timeframe.** E' la fonte piu' vicina a noi che il canale abbia prodotto.

### La struttura

Tre strumenti d'analisi (supporti/resistenze, trend line, medie 21 e 50) per classificare ogni
mercato in **una di tre condizioni**: *contro-trend*, ***rottura di trend line*** ("la tasca"),
*con il trend*. Poi, per la condizione scelta, un set di criteri d'ingresso fissi.

**Definizione dei livelli — "frequenza e prossimita'"**: quante volte il prezzo ha raggiunto quel
livello (frequenza) **e** cosa e' successo piu' di recente (prossimita'). Due o tre tocchi senza
nulla dopo = livello chiave; un tocco solo con una rottura alle spalle = "procedi con cautela".

### Il setup completo (rottura di trend line) — quasi interamente aritmetico

**Cancelli obbligatori** (se mancano, non si guarda nemmeno):
1. il prezzo deve **toccare il livello** (non avvicinarsi: toccarlo)
2. deve **rompere la trend line**, tracciata dal massimo decrescente piu' recente che ha creato il
   minimo decrescente (e **ri-ancorata** al pivot piu' recente se il movimento accelera dopo una pausa)
3. deve **rompere l'ultimo massimo decrescente** del movimento

**Ingresso**: si attende il ritorno del prezzo sulla **media a 21** → si entra li'.
**Target**: il **massimo/minimo precedente**.
**Stop**: **meta' della distanza** fra ingresso e target → **rapporto fisso 2:1**.
**Ingresso alternativo**: se il prezzo consolida senza raggiungere la media (2 massimi + 2 minimi,
consolidamento neutro o ascendente), si entra sulla rottura, stop sotto il minimo piu' recente.
**Timeframe**: analisi su settimanale/giornaliero, **innesco sul giornaliero** (variante 4 ore).
**Filtri decisi PRIMA del setup** (servono solo a decidere se *allungare* il trade, non se farlo):
divergenza MACD, e **sentiment retail contrarian** (se il 60-75% del retail e' dalla parte opposta
gia' presto nel movimento, si valuta di tenere oltre il 2:1).

### Verdetto: **CANDIDATO** — il piu' vicino a noi finora

| criterio | esito |
|---|---|
| strumenti che tradiamo | **SI** — FX major e cross, piu' petrolio; li abbiamo tutti |
| timeframe coperti | **SI** — giornaliero (e 4 ore) |
| regole codificabili | **IN GRAN PARTE**: media 21, target sul massimo precedente, stop a meta' distanza (2:1 fisso), rottura dell'ultimo massimo decrescente = tutta aritmetica |

**Le due parti dure**, da dichiarare: il **livello chiave** (frequenza+prossimita') e la **trend
line** restano semi-visivi — lui stesso chiama il tutto *"processo di analisi discrezionale"*.
Entrambi pero' sono meccanizzabili: il conteggio dei tocchi con tolleranza e ponderazione per
recency lo fa gia' il motore `analysis/level_research/`, e la trend line ha una regola di
ancoraggio esplicita (pivot piu' recente) che lo `zigzag()` di `analysis/nxt/` sa produrre.

### Perche' NON ricade nella famiglia livelli CLOSED

Qui il livello **non e' l'ingresso**: e' un **cancello**. L'ingresso arriva tre condizioni dopo
(rottura di trend line + rottura dell'ultimo massimo decrescente + ritorno sulla media 21). E'
esattamente l'unico angolo che la ricerca livelli aveva dichiarato **non falsificato**:
*"livelli come filtro condizionale dentro un contesto direzionale — NON e' reazione al livello, e'
un'altra ipotesi"* (DECISIONS 2026-07-06 e 07-07).

E' invece **adiacente al nostro LEAD**: e' un ingresso **contro-trend confermato** (rally dentro la
resistenza → rottura della trend line → pullback → short verso il minimo precedente), cioe' la
stessa famiglia del **fade NXT**.

### Il claim, misurato contro la NOSTRA scala

Dichiara: **dal 2018, a 2:1, win rate 58%**. → **E[R] = +0,74R per trade**.

| riferimento | E[R] misurato |
|---|---|
| fade NXT (il nostro LEAD) | **+0,31R** |
| Donchian, uscita migliore (E3) | +0,14R |
| NXT continuazione | −0,44R |
| **claim di Crooks** | **+0,74R** = **2,4x il nostro miglior lead** |

A 30 trade/anno sarebbero +22% annuo a rischio 1%; a 150 trade/anno **+111%**. La frequenza non e'
dichiarata con precisione (dice che la sola rottura di trend line puo' stare 2-3 settimane senza
segnali, ma anche che un multi-condizione arriva a 150-200 trade/anno), quindi il BS-test **non e'
concludente**: non implica un rendimento impossibile a bassa frequenza, ma **implica un E[R] piu'
del doppio di qualunque cosa abbiamo mai misurato**. E' quello il metro di scetticismo giusto.

**Nota a suo favore**, rara su questo canale: dice esplicitamente *"quando qualcuno ti dice che e'
ad alta probabilita', non credergli — vai a dimostrartelo da solo"*, e racconta di aver testato la
regola della media 21 invece di adottarla. E ammette apertamente i modi di fallire: periodi lunghi
senza segnali, poi quattro setup insieme su **coppie correlate**.

---

## A2.4 — "How The Markets Really Move" (Rajan D, DND Capital) · 80 min · 17.478 parole

`yZpzG8R3Ayk` · prop tradizionale UK. Day trading su azioni/futures con **market profile e teoria
dell'asta**: candela giornaliera come ancora di sentiment, esecuzione a 5 minuti, entrambi i
timeframe devono essere allineati **e assomigliarsi** (stessa pendenza). Ingresso su pattern di
candela bearish/bullish al ritest dell'**area di valore**; stop sulla struttura della candela;
**2:1 fisso**; **un trade al giorno**, durata 4-9 minuti.

### Verdetto: **SCARTATO** come strategia

Richiede accesso diretto al mercato, book, tape e dati pre/post market. **Lo dice lui**: *"un
trader retail non puo' farlo, non ha senso"*. Fuori dai nostri dati e dalla nostra infrastruttura.

### Ma e' la fonte piu' ricca di osservazioni MISURATE

**1. L'aritmetica dello spread, quantificata.** Con 2 pip di spread: puntare a 200 punti costa
l'**1%** del movimento, puntare a 20 punti ne costa il **10%**. Conclusione sua: il retail deve
fare **swing**, non intraday. Converge con Kichev (l'edge decade prima sui timeframe bassi perche'
i costi lo mangiano) e con il nostro NO-GO sull'ORB.

**2. Dati interni del suo desk sull'overtrading.** Rivede i report di tutti i trader ogni venerdi':
**chi fa 3+ trade al giorno rende meno di chi ne fa meno di 3**. Dichiara di non saperne il motivo.

**3. Lo stop a break-even e' CONDIZIONALE al regime.** Misurato dal suo desk: a 1,75:1 e'
statisticamente valido per alcuni trader, **non** per chi opera vicino all'apertura (whipsaw). E
nei regimi ad alta volatilita' spostare a break-even **peggiora**: ti fa uscire prima del
movimento. Converge col nostro risultato sul Donchian, dove lo stop in trailing (che e' uno stop
che si muove) e' risultato **la peggiore delle quattro uscite**.

### CONFLITTO — quarta fonte sul sizing per convinzione, e dice l'opposto

Holden, Breunigstein e Ashraf convergono sul **dimensionare per convinzione**. Rajan ha
**misurato la propria** convinzione: scrive un punteggio di fiducia su ogni trade, e ha trovato che
**circa il 75% delle volte vincono i trade su cui era MENO fiducioso**. Conclusione: rifiuta il
rischio dinamico, usa **rischio fisso** e compone solo meccanicamente (quando 20 unita' diventano
40, ridimensiona a 20 unita' piu' grandi).

Da mappare, senza eleggere un vincitore: tre fonti raccomandano di scalare per convinzione, una
**ha misurato che la propria convinzione era anti-correlata all'esito**. Nessuna delle quattro
fornisce un metodo validato per assegnare il grado — e questa quarta suggerisce che il grado
soggettivo possa essere **rumore, o peggio**.

### Il miglior razionale ECONOMICO che il funnel abbia prodotto — e la sua complicazione

Spiega **perche'** valute e materie prime dovrebbero tornare alla media e le azioni no:

> Se una valuta si rafforza troppo, danneggia gli esportatori. Se il petrolio sale troppo, non si
> riesce a fare benzina e i produttori aumentano l'offerta. **Se un'azione sale, non danneggia
> nessuno.** Nelle valute ci sono inoltre *quattro variabili* (si puo' comprare o vendere ciascuna
> delle due valute), nelle azioni due.

E' un **meccanismo di retroazione economica** che limita i movimenti — cioe' un vero *perche'*, non
solo un *cosa*, ed e' il tipo di razionale che
[STRATEGY_LIFECYCLE §6a.6](../../../docs/STRATEGY_LIFECYCLE.md) richiede.

⚠️ **Ma complica la sintesi del blocco A1**, e va detto invece di appiattirlo. La sintesi A1 era
"trend sugli asset volatili/illiquidi, mean reversion su quelli tranquilli". Rajan propone un asse
diverso: **presenza o assenza di retroazione economica**. Le materie prime sono volatili **e**
hanno retroazione: i due assi dicono cose opposte. E la nostra misura sta con la volatilita', non
con la retroazione — sul test Donchian **energia +0,40 e agricoli +0,24**, cioe' **pro-trend**,
esattamente dove la storia della retroazione predirebbe reversione. Una convergenza in meno, una
domanda in piu'.

**Conferma sul playground da un quarto angolo**: racconta che nell'estate 2019 le escursioni
giornaliere di EURUSD e GBPUSD sono crollate da 120-150 pip a **30 pip**, e che i quant lasciavano
il forex. E' l'osservazione di prima mano della compressione di volatilita' sul mercato piu'
efficiente — lo stesso campo dove abbiamo misurato **−0,47R peggio del random**.

---

## A2.5 — "The ONLY Break And Retest Strategy" (Vincent Desano) · 88 min · 17.750 parole

`SMSqQTBxjc0` · opzioni e futures su NQ/ES/QQQ, grafico a **2 minuti**. Rottura del **massimo del
giorno precedente** → pullback sul livello ("battle zone") → lettura delle candele → long.
Target 1 = il massimo della rottura, si scala, si tengono i runner. Speculare al ribasso sul minimo
del giorno precedente.

### Verdetto: **SCARTATO**

Tre ragioni, in ordine di gravita':
1. **La decisione d'ingresso e' la lettura visiva delle candele** nella battle zone (wick, candela
   che ingloba, "manipolazione"). E' la stessa ragione per cui Okala fu dichiarato non testabile.
2. **2 minuti, opzioni, velocita' d'esecuzione**: fuori dai nostri dati e dalla nostra infrastruttura.
3. Il livello e' **PDH/PDL**, cioe' il concetto **piu' direttamente falsificato** del nostro
   registro: breadth 0/16, reazione 28,8% contro 30,5% del random, CI [−2,4; −1,2] — rotti **piu'**
   del caso.

*Precisazione onesta sul punto 3*: il suo setup e' **rottura + ritest** (inversione di polarita'),
non "il prezzo reagisce al livello". La nostra v1 misurava la reazione **al tocco**, pooled. Sono
ipotesi diverse. Ma il punto 1 rende la questione accademica: qualunque sia il livello, l'ingresso
non e' codificabile.

### Due primitivi meccanici che invece si staccano

**1. La "No Trade Zone" — e la QUARTA formulazione indipendente della stessa idea.** Definisce un
intervallo (massimo del giorno prima ↔ minimo pre-market) e **vieta di operare dentro**; si opera
solo su rotture e ritest **fuori** da li'. Nelle sue parole: *"in mezzo e' dove i trader
distruggono i conti"*.

Confronta:
- **Zhang** (A1.4): gli stage 1 e 3 sono "le fasi da evitare", si opera solo in 2 e 4
- **Breunigstein** (A1.5): si opera solo quando lo strumento e' **esteso**, mai nel grinding
- **Crooks** (A2.3): contro-trend **solo** se il mercato e' esteso rispetto al range
- **Desano**: non si opera dentro la NTZ

**Quattro fonti indipendenti, quattro vocabolari, la stessa regola: non operare in mezzo al
range.** Ed e' meccanicamente testabile senza alcuna discrezionalita': *condizionare all'essere
fuori dal range recente migliora l'espettanza?*

**2. Divergenza fra strumenti correlati come filtro.** La sua "big four correlation" (NQ, ES, SPY,
QQQ guardati insieme): se il Nasdaq rompe un massimo ma l'S&P no, **non si compra**. Racconta una
perdita reale del 25 aprile causata proprio dall'aver ignorato questa divergenza.

E' un **filtro di conferma incrociata**, definibile in aritmetica pura, e **noi abbiamo le coppie
correlate**: NAS100/SPX500, XAUUSD/XAGUSD, BRENT/WTI, BTCUSD/ETHUSD, piu' i cross FX.
**Mai testato da noi.**

---

# CONSUNTIVO DEL BLOCCO A2 (5 video, 84.822 parole, ~7 ore)

| # | fonte | classe | verdetto |
|---|---|---|---|
| A2.1 | Umar Ashraf | sviluppo del trader | **REFERENCE** |
| A2.2 | Pradeep Bonde | Episodic Pivots, azioni USA | **SCARTATO** (servono fondamentali + interpretazione notizie) |
| A2.3 | Alistair Crooks | **swing FOREX** | **CANDIDATO** |
| A2.4 | Rajan D | intraday azioni, market profile | **SCARTATO** (serve accesso diretto e book) |
| A2.5 | Vincent Desano | break & retest, opzioni 2 min | **SCARTATO** (ingresso visivo) |

**Un candidato su cinque** (tre in totale sui dieci video letti). La regola di sospensione non
scatta.

## Cosa e' emerso oltre i singoli video

**1. "Non operare in mezzo" — quattro formulazioni indipendenti.** E' la convergenza piu' forte di
tutto il funnel finora, piu' forte del gradiente di liquidita' perche' arriva da quattro trader con
strumenti, timeframe e vocabolari completamente diversi. Ed e' testabile senza discrezionalita'.

**2. Un razionale economico vero** (A2.4), che pero' **complica** invece di confermare: valute e
materie prime avrebbero retroazione economica che limita i movimenti, le azioni no → FX e commodity
dovrebbero tornare alla media. **Ma la nostra misura dice il contrario sulle commodity** (energia
+0,40 e agricoli +0,24 pro-trend nel test Donchian). Due assi in conflitto: volatilita' contro
retroazione. Da tenere aperto, non da appianare.

**3. Il sizing per convinzione si e' rotto** (A2.4). Dopo tre fonti convergenti (Holden,
Breunigstein, Ashraf), la quarta ha **misurato** la propria convinzione e l'ha trovata
**anti-correlata** all'esito (~75% delle volte vincevano i trade meno convinti) → rischio fisso.
Nessuna delle quattro fornisce un metodo validato per assegnare il grado.

**4. Due primitivi nuovi e mai testati da noi**: il **volume anomalo come segnale** (A2.2, famiglia
nuova, budget intatto) e la **conferma incrociata fra strumenti correlati** (A2.5).

## Statistiche dichiarate raccolte nel blocco

| fonte | claim | esito del BS-test |
|---|---|---|
| Ashraf | "eight figure verified" | nessun claim di strategia |
| Bonde | 5-10 → 100-300 trade/anno; mosse 50-1000% | non quantifica win rate o E[R] |
| **Crooks** | **58% win a 2:1 dal 2018 → E[R] +0,74R** | **non concludente**: dipende dalla frequenza, ma e' **2,4x** il nostro miglior lead misurato |
| Rajan D | ~50% win a 2:1; 3+ trade/giorno rendono meno (dati interni) | E[R] +0,50R implicito; l'osservazione sull'overtrading e' misurata |
| Desano | 400k$ nell'anno, ~1M in 24 mesi; esempio +130% su un contratto | claim di conto, non di strategia |
