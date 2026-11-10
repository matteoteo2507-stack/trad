# Blocco H — attribuzione degli appunti orfani (3 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Perché questo blocco esiste.** Il file `fondamenti_tecnici/_sorgenti/Nuove nozioni teoriche 2026-07-16.txt` contiene,
alle **righe 331–491**, un blocco intitolato *"Comprehensive Guide to Investing: Risk, Return, and Portfolio
Management"* **senza attribuzione al video di origine**. Tutti gli altri blocchi dello stesso file sono attribuiti
(vedi la tabella "già distillati" in [`PIANO.md`](PIANO.md)). Questo blocco legge i tre candidati residui del canale per
stabilire **quale video ha prodotto quegli appunti**, e per registrare ciò che i tre video aggiungono.

**Marcatori di riconoscimento cercati** (dagli appunti orfani):
1. *"distills **15 years** of academic and industrial investing experience"*;
2. **quattro verità dure** (nessuno prevede il singolo esito; nessun pasto gratis; nessuna pallottola d'argento;
   la ricchezza richiede tempo);
3. **tabella titoli vs non-titoli** (azioni/obbligazioni/ETF/fondi/opzioni/futures/REIT contro immobili, materie prime
   fisiche, arte, collezionismo, aziende private, crypto, liquidità, prodotti assicurativi);
4. **startup di IA contro Microsoft** come esempio di "più volatilità ≠ più rendimento";
5. **tabella delle tre forme dell'EMH** con un verdetto per ciascuna;
6. **controfattuali e causalità** (impossibilità di testare scenari alternativi);
7. **arte, materie prime fisiche, orologi** come mercati **ortogonali** che reggono quando le correlazioni saltano;
8. tabella delle **metriche** (Sharpe, Sortino, drawdown massimo, CAGR) con la chiusa *"strumenti di posizionamento, non
   sfere di cristallo"*.

**Contesto del repo per questo blocco** (verificato il 2026-09-16): l'intero contenuto degli appunti orfani è **già
assorbito** — `08_asset_allocation_passiva` (EMH nelle tre forme, pilastro passivo), `05_portfolio_rischio` (rischio
diversificabile e non, CAGR, drag di volatilità, correlazioni che saltano), `04_quant_metodologia` §8 (CAGR) e §2b
(metriche necessarie non sufficienti). **L'attribuzione non cambia nulla nel merito**: serve a chiudere la tracciabilità
della fonte, che è un requisito del registro `_INTAKE.md`.

---

## H1 — Quant Explains Investing at 5 Different Levels

`tmkkddOeAsM` · #24 · 18 min · 2.652 parole

### Verdetto sull'attribuzione: **NON è la fonte degli appunti orfani**
Nessuno degli otto marcatori è presente. Il video è costruito su una **narrazione a livelli crescenti** (asilo → banco
della limonata → borsa → diversificazione → rischio non diversificabile), non su una struttura a sezioni numerate; non
nomina i 15 anni di esperienza, non ha la tabella titoli/non-titoli, non ha le tre forme dell'EMH, non parla di
controfattuali né di orologi. **Escluso.**

### Cosa contiene comunque
- **Livelli 1-2 (aneddoti)**: l'investimento come **costo anticipato per un premio non garantito** (studiare a casa per
  arrivare primo ai giocattoli — e il premio viene comunque sottratto); il banco della limonata come **rischio
  d'impresa** (se piove, i limoni e il banco sono distrutti e l'investitore, non il gestore, resta con il conto).
  Zero contenuto tecnico, buona formulazione: *"senza rischio non c'è possibilità di premio, ma non tutti i rischi sono
  uguali"*.
- **Livello 3 — EMH come esito di domanda e offerta**: il prezzo di equilibrio è *"la migliore stima collettiva oggi,
  data l'informazione disponibile"*. Aggiunge una precisazione utile: **il vantaggio informativo non deve essere
  privilegiato** — conoscere Sam da anni (informazione pubblica ma **non raccolta da altri**) è già un differenziale.
  *"Il mercato a volte fa un ottimo lavoro, altre volte pessimo."* Nessuna novità rispetto a G4 e a `08`.
- 🔧 **Livello 4 — il fallimento della diversificazione azionaria, con la meccanica giusta.** L'errore non è tenere
  pochi titoli: è credere che titoli *diversi* siano in *cesti* diversi. *"Se prendi i rendimenti come pannello e fai
  una PCA, vedrai che probabilmente la **seconda componente principale** ha carichi su tutte queste società: sono nello
  stesso cesto tecnologico."* Esempio: Google, Apple, Nvidia in **un solo** cesto; Cigna (sanità) in un altro.
  → Coincide **esattamente** con la regola di lettura dei carichi già registrata in E1 (PC1 = mercato se i segni sono
  tutti concordi; PC2 = settoriale se si raggruppano per settore). **Seconda fonte, stessa regola.**
- 🔧 **Livello 5 — dove esistono i cesti.** Anche cesti settoriali diversi (Apple, Goldman Sachs, Cigna) stanno **nello
  stesso ambiente**: il mercato azionario americano. *"In un ciclo rialzista è una bella giornata di sole; in uno
  ribassista piove su tutti i cesti insieme."* Rimedio proposto: cercare un **mercato ortogonale** — e, esplicitamente,
  *"non deve nemmeno essere un mercato diverso: può essere una strategia di trading completamente diversa"*.
  → **Aggancio diretto al nostro caso**: i segnali del mentore su XAUUSD non sono un titolo in più, sono
  potenzialmente **l'ambiente diverso**. È la stessa idea del buco 42 (pesi fra attività) vista dal lato del rischio
  invece che da quello del capitale.

### Domanda a cui risponde
"Sono davvero diversificato?" — con la risposta: dipende dal **numero di direzioni principali di rischio** a cui sei
esposto, non dal numero di titoli.

### Assunzioni
La PCA identifica cesti interpretabili (vero nel suo esempio, non garantito in generale: cfr. E5, la struttura
fattoriale **si muove**).

### Modi di fallire
- Contare i titoli invece delle direzioni di rischio.
- Cercare l'ortogonalità e trovarla solo **in tempi normali**: E1/`05` registrano che nello stress le correlazioni
  saltano insieme. L'ortogonalità va misurata **condizionata allo stress**, cosa che il video non dice.

### Stato nel repo
`05_portfolio_rischio` ha già la tassonomia del rischio, la PCA e il salto delle correlazioni in crisi; il **PAC è un
solo ETF globale**, quindi il problema dei cesti non si pone oggi nel pilastro investing. **Nulla di nuovo da
installare.** L'unico elemento che il repo non scrive è la lettura di una **strategia** (non un mercato) come direzione
di rischio ortogonale — già coperto dal buco 42.

### Rilevanza
**Reference**; conferma di E1 e di `05`.

### Claim registrati senza uso
Nessun numero in tutto il video.

---

## H2 — Quant Investing for Beginners

`aBfkf_0YsCY` · #162 · 24 min · 4.084 parole

### Verdetto sull'attribuzione: **NON è la fonte degli appunti orfani**
Nessuno degli otto marcatori. Il video è monotematico (diversificazione azionaria e correlazione), non copre EMH,
controfattuali, metriche, titoli vs non-titoli, né dichiara i 15 anni di esperienza. **Escluso.**

### Definizione e strategia proposta
Distinzione d'apertura: **trading quantitativo** (dati alternativi, bassa latenza, molti strumenti, sezione trasversale)
vs **investimento quantitativo**, che è tutt'altro. La strategia del video, in una riga: **diversificare via il rischio
idiosincratico e quello settoriale, tenendo solo il rischio di mercato**.
- Tre secchi di rischio azionario: **idiosincratico** (specifico dell'impresa), **di settore**, **di mercato** (guidato
  da fattori macro: PIL, inflazione, tassi).
- *"Devi assumere del rischio per ottenere un rendimento, ma non devi assumere rischio **non necessario**."*
  Azzerando tutto si ottiene il tasso privo di rischio, cioè i titoli di Stato: non è l'obiettivo.
- Simulazione: 30 percorsi azionari con **deriva 7%** e **volatilità annualizzata 20%**, correlati fra loro.
  Il portafoglio **equipesato** converge alla deriva di mercato (7%): il titolo peggiore non affossa, il migliore non
  traina. ⚠️ E subito la controprova onesta: ripete la simulazione con **deriva negativa** e ottiene **−7%**.
  *"Diversificare via idiosincratico e settoriale **non garantisce di guadagnare**: lascia solo l'esposizione al
  mercato."*
  → Coincide con `05` (portafoglio equipesato di 9 titoli che traccia SPY) e con il pilastro passivo. **Nessuna novità
  di contenuto**, ma la controprova a deriva negativa è la formulazione più pulita del punto.

### 🔧 Il contributo vero: la correlazione è una statistica, e **la finestra la decide**
Misura su Portfolio Visualizer la correlazione fra **Johnson & Johnson e Chipotle**, due titoli apparentemente
scorrelati:

| finestra di calcolo | correlazione |
|---|---|
| rendimenti **annuali** | **0,01** |
| rendimenti mensili, mobile a 12 mesi | **~0,13** di media |
| rendimenti giornalieri, mobile a 60 giorni | **~0,17** di media, con punte a **0,70-0,735** |

*"Devi riconoscere la finestra in cui la stai calcolando, perché cambieranno nel tempo: la media giornaliera è 0,17,
quella mensile 0,13, quella annuale 0,01."* E, su Apple-Amazon: **0,52** annuale, **0,31** mensile.
- 🔧 **Regola**: una correlazione **senza la finestra dichiarata non è un numero**. Due titoli "scorrelati" a
  frequenza annuale possono stare a **0,73 su 60 giorni** — ed è in quei 60 giorni che si subisce il drawdown.
- Distingue inoltre due casi nelle sue simulazioni: correlazione **variabile ma stazionaria** (oscilla attorno a ~0,7) e
  correlazione **non stazionaria** (deriva, con gli attivi che si allontanano mentre il coefficiente sale).
  *"Non c'è nulla che imponga alla correlazione di essere stazionaria… non c'è alcuna tendenza naturale a restare
  attorno a un valore."*
- Corollario sul ribilanciamento, con numeri: 100 $ in Cigna e 100 $ in Nvidia; Nvidia raddoppia; **il portafoglio non è
  più equipesato** e il profilo di rischio non è quello di partenza. *"Non è metti-e-dimentica: è proprio questo a
  renderlo una strategia di investimento **quantitativa** invece che un semplice compra-e-tieni."*
- Due misure proposte per "quanto sono diversificato": **correlazione media a coppie** e **beta di portafoglio**.

### Domanda a cui risponde
"Che cosa sto misurando quando dico che due attivi sono scorrelati?"

### Assunzioni
Rischio azionario scomponibile in tre secchi; correlazione a coppie come proxy della diversificazione (ignora la
struttura di ordine superiore — la PCA di E1/H1 fa meglio).

### Modi di fallire
- Selezionare sulla correlazione **a bassa frequenza** e subire quella **ad alta frequenza** durante lo stress.
- Trattare una correlazione mobile non stazionaria come se avesse una media a cui tornare.
- Scambiare "solo rischio di mercato" per "rischio basso": la controprova a deriva negativa lo esclude.

### Stato nel repo
- **Il caveat sulla finestra non è scritto da nessuna parte.** Il repo usa correlazioni in più punti —
  `docs/TSMOM_PREREGISTRATION.md` ("limite dichiarato: correlazioni alte, molte gambe USD"),
  `docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md` (correlazione sui singoli strumenti come misura secondaria),
  `docs/INVESTMENT_ALGO_DESIGN.md` (universo multi-mercato, matrice di correlazione), `docs/INVESTING_PILLAR_PLAN.md`
  (i bond lunghi che falliscono la diversificazione nel 2022) — e **in nessuno di questi è dichiarata la frequenza dei
  rendimenti né la finestra**. → **buco 46**.
- Il resto (tassonomia del rischio, equipesato che traccia l'indice, ribilanciamento) è **già nel repo**; il
  ribilanciamento è già il buco 18 e per il PAC è già deciso (fase 1 senza ribilanciamento, con versamenti nuovi).

### Rilevanza
**Applicabile ora** limitatamente al buco 46, che tocca documenti già scritti; **reference** per il resto.

### Claim registrati senza uso
7% di deriva e 20% di volatilità sono **parametri di simulazione**, non misure. Le correlazioni di Portfolio Visualizer
(JNJ/CMG, AAPL/AMZN) sono **verificabili in linea di principio** ma dipendono dal campione, che non dichiara.

---

## H3 — Quant on Trading and Investing

`CKXp_sMwPuY` · #131 · 60 min · 9.839 parole — il più lungo dei tre candidati, e quello che **sembrava** più probabile

### Verdetto sull'attribuzione: **NON è la fonte degli appunti orfani**
Nessuno degli otto marcatori. Copre temi **adiacenti** (EMH no, ma rischio/rendimento, diversificazione, metriche,
stabilità), e proprio per questo va detto con precisione cosa manca: niente "15 anni di esperienza", nessuna delle
**quattro verità dure**, nessuna **tabella titoli / non-titoli**, nessuna **tabella delle tre forme dell'EMH con
verdetto**, nessuna sezione sui **controfattuali**, nessun accenno ad **arte e orologi**, nessuna tabella
portafoglio coperto vs non coperto. La struttura è a flusso (rischio e rendimento → esposizioni → mercato →
probabilità implicita → come faccio trading → come investo → metriche), non a **nove sezioni numerate**. **Escluso.**

### Contenuto — quasi tutto già catalogato altrove, con tre aggiunte
Il video è dichiaratamente una **sintesi** di mesi di altri video, quindi ripete blocchi già letti: rischio e
rendimento come variabili aleatorie stimate all'indietro; i tre secchi di esposizione (idiosincratica, settoriale, di
mercato) con la precisazione corretta *"diversificando via un rischio diversifichi via anche il suo rendimento
atteso"*; segnale per decili che regge in campione e **degrada in vivo** (identico a G2); gioco d'azzardo vs gioco a
informazione incompleta (identico a G2, con l'aggiunta: *"un algoritmo di apprendimento per rinforzo sulla roulette
non imparerebbe nulla oltre alla funzione di massa di probabilità"*).

**Le tre cose che aggiunge:**

1. 🔧 **Probabilità implicita ≠ probabilità, e il paradosso di San Pietroburgo come controesempio.**
   Mette a confronto due simulazioni: la media di lanci di moneta **converge** a 0,5 (legge dei grandi numeri); la media
   del gioco di San Pietroburgo **non converge** — *"la rieseguo e la linea si sposta, e continuerà a spostarsi"*.
   Le probabilità implicite appartengono alla seconda famiglia: *"un 90% implicito ti dice dove sono i soldi, non che
   su mille repliche l'esito si verificherebbe 900 volte."*
   - 🔧 **Uso operativo che ne deriva, e che è il pezzo migliore del video**: la probabilità implicita non predice
     l'esito, **misura l'impatto che avrà la sua realizzazione**. Un taglio dei tassi prezzato al **90%** che poi
     avviene muove pochissimo; lo stesso taglio prezzato al **60%** produce un salto. *"Stiamo correggendo o
     confermando una convinzione."* → dove c'è più incertezza c'è più spazio di movimento.
     **Traducibile subito**: prima di un evento macro, ciò che conta per il rischio in portafoglio non è quanto è
     probabile l'esito, ma **quanto è già prezzato**. Il repo non ha nulla su questo (nessun modulo eventi/calendario).
   - Analogia esplicita con la **volatilità implicita**: invertendo Black-Scholes si ottiene *"ciò che i trader stanno
     prezzando ora"*, non la volatilità futura.
2. **Paura e ritorno alla media della volatilità, con un numero citato.** Cita Shiller: la probabilità **percepita** di
   un crollo tipo 1929/1987 nei sei mesi successivi risulta sovrastimata di **6-19 volte** rispetto alla frequenza
   storica. Metafora del lago di vetro: una barca accende il motore, gli altri lo imitano, l'acqua diventa agitata — e
   poi **torna liscia**. È la spiegazione narrativa di **raggruppamento della volatilità + effetto leva** (già in
   `blocco-D.md`). Conclusione sua: *"quando c'è sangue nell'acqua non dovresti vendere in perdita, dovresti comprare
   di più e abbassare il prezzo medio di carico"*.
   ⚠️ Registrato come **claim con conflitto di ruolo**: è anche esattamente ciò che ogni operatore dice dopo un
   recupero. Il numero 6-19× è attribuito a Shiller ma **non verificato**; la conclusione operativa **non segue** dal
   numero (sovrastimare la probabilità di un crollo non implica che comprare nel crollo sia positivo in attesa).
3. 🔧 **Metriche di performance: la lista di cosa considera, che include due cose che noi non contiamo.**
   - Rifiuta *"batte il mercato?"* come criterio (*"uno dei commenti più ridicoli sulla performance"*), e rifiuta anche
     Sharpe/Sortino **presi da soli**: *"mi chiedi se metterei leva su un sistema con Sharpe 2+? No. Non so nulla di
     quel sistema: quanto è difficile da operare, che classe di strategia è, a cosa mi sto esponendo, qual è il
     drawdown massimo."*
   - **Le due voci che nel repo non esistono**: *"in che proporzione di tempo sono stato **in contante**"* e *"quando
     ho avuto **accesso al capitale**"* — non liquidità dell'attivo, ma disponibilità del denaro per altri usi.
     Il suo esempio: *"se uno fa 20% e io 15%, ma io ero in contante metà del tempo, sono cose fondamentalmente
     diverse — io devo pagare l'affitto"*.
     → **Rilevante per noi in modo diretto**: il PAC è a **serbatoio** ([[project_pac_inputs_2026_08_04]]: stipendi
     estivi vincolati per 10 mesi), quindi la quota di tempo in contante **è** una variabile del piano, e oggi non è
     misurata da nessuna parte. → **buco 47**.
   - Chiusa: *"la stabilità di strategie, misure di rischio e misure di performance non è mai garantita ed è anzi
     rara"*.

### Domanda a cui risponde
"Come leggo l'affermazione di chiunque dica di avere un segnale che funziona?" — e la risposta è il telaio
rischio/esposizione/stabilità, non un test.

### Assunzioni
Che la volatilità torni a un livello medio (raggruppamento + effetto leva); che la paura sia sistematicamente
sovrastimata. Entrambe **storiche**, e il video stesso ricorda che il passato non è indicativo.

### Modi di fallire
- Trattare una probabilità implicita come una frequenza (l'errore che il video corregge).
- Usare *"la volatilità torna alla media"* come licenza per mediare al ribasso senza un limite di perdita: la fonte
  non nomina mai la dimensione della posizione, che è esattamente ciò che rende quella mossa sopravvivibile o fatale
  (cfr. `blocco-C.md`, rovina del giocatore).
- Confondere "il sistema è algoritmico" con "il fattore comportamentale è neutralizzato": *"qualcuno sta comunque al
  timone… guadagnare non fa sentire bene quanto perdere fa sentire male"*.

### Stato nel repo
- **Probabilità implicita e impatto già prezzato**: assente (nessun modulo eventi/macro). → parte del **buco 47**
  come nota, ma fuori perimetro operativo finché non si opera su eventi.
- **Tempo in contante / accesso al capitale**: assente da `analysis/ops/weekly_healthcheck.py` e da ogni metrica.
  → **buco 47**.
- Tutto il resto (esposizioni, degrado del segnale, metriche non sufficienti, gioco a informazione incompleta) è già
  coperto da `04` §2b, `05` e dai blocchi B, D, G.

### Rilevanza
**Applicabile ora** per il buco 47; **reference** per il resto. È il video che **meno aggiunge in rapporto alla sua
lunghezza** di tutto il distillamento: 60 minuti, tre voci nuove.

### Claim registrati senza uso
6-19× di sovrastima della probabilità di crollo (attribuito a Shiller, non verificato); "sono corretto in media, ed è
per questo che continuo a guadagnare" (autodichiarato, nessun dato); l'esempio del premio per il rischio di volatilità
dopo gli utili (rimanda a un proprio video con codice, non esaminato qui).

---

## Attribuzione risolta — ma **l'ipotesi del PIANO era sbagliata**

I tre candidati indicati in [`PIANO.md`](PIANO.md) (#24, #131, #162) sono stati letti per intero: **nessuno dei tre** è
la fonte. Il PIANO li aveva scelti per somiglianza del **titolo**; nessuno dei tre ha un solo marcatore.

Ho quindi cercato altrove nell'elenco del canale e scaricato i due candidati residui plausibili
(`quantguild_attribuzione_h.txt`). Risultato del controllo automatico sui marcatori:

| candidato | 15 years | non-securities | hard truths / silver bullet | EMH weak/strong form | counterfactual | watches |
|---|---|---|---|---|---|---|
| #24 `tmkkddOeAsM` | — | — | — | — | — | — |
| #131 `CKXp_sMwPuY` | — | — | — | — | — | — |
| #162 `aBfkf_0YsCY` | — | — | — | — | — | — |
| #35 `37wRzGdC9w4` | — | — | — | — | — | — |
| **#29 `LX4Ugaxx9n0`** | **✅ 1** | **✅ 4** | **✅ 3** | **✅ 2 + 3** | **✅ 6** | **✅ 2** |

> **Fonte: #29 — "The Ultimate Guide to Quant Portfolio Management"** (`LX4Ugaxx9n0`, 57 min, 9.052 parole).
> Incipit testuale: *"I'm about to compress about **15 years of academic and industrial experience** into a single video
> that is going to be the only video that you need to understand the investing space."*

**Perché l'errore era quasi inevitabile, e cosa insegna.** #29 risultava **già distillato**: i suoi appunti erano
attribuiti a `quantportfolio managernotes.txt` righe 1-249 (PCA, CAPM, beta). Nessuno aveva considerato che **lo stesso
video avesse prodotto due serie di appunti, in due file diversi, in due momenti diversi** — la seconda (righe 331-491 di
`Nuove nozioni teoriche`) copre la prima metà del video (verità dure, titoli/non-titoli, EMH, controfattuali,
metriche), la prima copre la seconda metà (decomposizione del rischio). Le due si **incastrano**, non si sovrappongono.
Il titolo del riassunto ("Comprehensive Guide to Investing") è stato prodotto dal sintetizzatore e **non coincide** con
il titolo del video, che è la ragione per cui la ricerca per titolo ha fallito.
→ **Regola da registrare**: negli appunti senza ID, un blocco orfano va cercato **per contenuto sull'intero canale**,
non fra i video "che non risultano ancora distillati" — un video già distillato può aver prodotto più blocchi.

### Il video letto per intero: cosa c'è oltre agli appunti
Gli appunti (righe 331-491) sono **fedeli e completi** su struttura e contenuto. Ciò che il riassunto **comprime via**,
e che vale la pena tenere:

- 🔧 **Il problema in due strati, non uno.** Il riassunto dice "le statistiche sono retrospettive". Il video dice due
  cose distinte: (a) le stime storiche **saranno diverse in avanti**; (b) **anche se fossero corrette**, resta la
  casualità fondamentale — *"cammineremo comunque uno dei percorsi a caso"*. Sono due fonti d'errore indipendenti e
  vanno tenute separate: la prima si combatte con la robustezza, la seconda **non si combatte affatto**, si dimensiona.
- 🔧 **"Rischio non diversificabile" è un termine improprio, ed è la tesi centrale del video.** *"Non diversificabile"
  vale **dentro quel mercato** (azionario USA); non vuol dire che non si possa diversificare **con altri mercati o con
  strategie**. La sua parola è **decorrelazione fisica**: due dadi non hanno nulla in comune per costruzione, non per
  stima. Semiconduttori e sanità hanno correlazione mobile a 40 giorni ~0 **finché non arriva il vento macro**, e
  allora vanno a ~1; un portafoglio di **orologi** non partecipa, perché è un altro mercato.
  → ⚠️ Da tenere con due cautele che il video non pone: (1) l'ortogonalità va misurata **condizionata alla crisi**,
  ed è un'affermazione empirica, non una proprietà; (2) l'illiquidità di quei mercati significa anche che **il prezzo
  non è osservato**, non che non si muove — un orologio invenduto non è un orologio stabile.
- 🔧 **"Non mi serve un backtest per dirti cosa succede."** Se la regressione CAPM mostra beta > 1 e non ci sono gambe
  di copertura, l'esito in un crollo è **noto per costruzione**. Il backtest serve a un'altra cosa: *"dirti come il tuo
  portafoglio si sarebbe comportato nei diversi regimi"* — posizionamento, non predizione. È la stessa distinzione di
  `04` §2b, formulata meglio.
- 🔧 **Il criterio personale dichiarato**, che è la parte più onesta: *"se resto indietro rispetto all'S&P 500 del
  5-10% ogni anno e ho drawdown molto migliori — l'S&P è a −40% e io a −10% — sto molto meglio così, perché so che
  potrò sempre vendere a 90 centesimi sul dollaro se mi serve."* E l'analogia: dire "voglio massimizzare la ricchezza"
  è come dire "voglio massimizzare la panca" — **implica** lavorare su spalle e tricipiti (drawdown massimo,
  rendimento corretto per il rischio, **accessibilità del capitale**).
  → Aggancio diretto al PAC: la domanda *"e se fra sei anni ti servissero i soldi e ci fosse un −30%?"* è esattamente
  la ragione del **secchio cuscinetto** in `docs/INVESTING_PILLAR_PLAN.md`. **Conferma esterna della struttura a due
  secchi**, indipendente.
- ⚠️ **Il conflitto d'interesse è nel corpo del video, non solo in coda**: la "gamba di copertura / fondo hedge
  personale" è citata **tre volte** come suo corso a pagamento, ed è l'unico punto in cui il video afferma un
  risultato (il portafoglio coperto che **supera** quello non coperto sui 10 anni) **senza dati**. Terza occorrenza
  dopo E2 e G6 → vedi conflitto 3 del blocco G: **stato invariato**.
- **Non aggiunge nulla** su: verità dure, titoli/non-titoli, EMH nelle tre forme, controfattuali, metriche — il
  riassunto negli appunti è adeguato e già assorbito in `08` e `05`.

### Conseguenze per il repo
1. **Traccia da correggere**: gli appunti righe 331-491 di `Nuove nozioni teoriche 2026-07-16.txt` vanno attribuiti a
   **#29 `LX4Ugaxx9n0`**, insieme a `quantportfolio managernotes.txt` righe 1-249. Da riportare in `_INTAKE.md` e nella
   tabella "già distillati" di `PIANO.md`. **Il conteggio dei video già distillati resta 9**: non se ne aggiunge uno,
   se ne chiude uno.
2. **Nessuna revisione di contenuto**: tutto ciò che il blocco orfano contiene era già in `08` e `05`.

---

## H4 (fuori blocco) — How a Quant would Invest $1,000,000

`37wRzGdC9w4` · #35 · 7 min · 1.055 parole — scaricato per il controllo di attribuzione (**escluso**: nessun
marcatore), letto e catalogato per completezza

Quattro allocazioni di un milione su 30 anni, con numeri suoi: **titoli di Stato USA** → 3,5 M (4,5 M aggiungendo
20.000 $/anno); **mercato azionario** al 7,5% reale → ~9 M, *"ma guarda questo drawdown del 40% intorno al decimo
anno"*; **private equity / avviare un'impresa** al 18% (*"quartile alto dei gestori"*) → ~150 M, con la nota sulla
**convessità**: *"raddoppiare il tasso non raddoppia il capitale finale"*; **"pensionamento inverso"** (Ferrari, Rolex,
spese) → 24 mesi. Registrato come **intrattenimento con numeri corretti di matematica finanziaria**, non come consiglio.

L'unico contenuto sostanziale: *"e se il premio per il rischio azionario morisse? Guarda il Giappone: dal 1989 al 2024
per recuperare il picco. Non c'è ragione perché le azioni USA non possano comportarsi allo stesso modo."*
→ **Già nel repo, e meglio**: `08_asset_allocation_passiva` §Decenni persi ha i numeri (USA reale ~0% nel 1929-54,
1966-82, 2000-13; Italia e Giappone peggio e più spesso) **e** la risposta strutturale (i decenni persi di Italia e
Giappone furono **locali** → l'All-World annega il rischio-paese; rifiutato il template "70-80% S&P 500"). La fonte
pone il problema e vende un corso; il repo lo ha già risolto con la diversificazione globale. **Nessuna azione.**

---

## Sintesi del blocco H

| # | video | esito attribuzione | cosa aggiunge |
|---|---|---|---|
| H1 | Investing at 5 Different Levels (#24) | **escluso** | i carichi PCA come "cesti" (conferma E1); una **strategia** può essere il mercato ortogonale |
| H2 | Quant Investing for Beginners (#162) | **escluso** | 🔧 **la correlazione dipende dalla finestra**: JNJ/CMG 0,01 annuale, 0,13 mensile, 0,17 giornaliera con punte a 0,73 |
| H3 | Quant on Trading and Investing (#131) | **escluso** | 🔧 probabilità implicita = **impatto già prezzato**, non frequenza (San Pietroburgo come controesempio); **tempo in contante** come metrica |
| — | **The Ultimate Guide to Quant Portfolio Management (#29)** | ✅ **è la fonte** | decorrelazione fisica; "non diversificabile" è un termine improprio; due strati d'errore; conferma esterna dei due secchi del PAC |
| H4 | How a Quant would Invest $1.000.000 (#35) | escluso | nulla (i decenni persi sono già nel repo, con numeri migliori) |

### Buchi aperti dal blocco H
- **Buco 46** — **nessuna correlazione nel repo dichiara la frequenza dei rendimenti e la finestra** con cui è
  calcolata (`TSMOM_PREREGISTRATION`, `TREND_EXIT_PLAYGROUND_PREREGISTRATION`, `INVESTMENT_ALGO_DESIGN`,
  `INVESTING_PILLAR_PLAN`). Due attivi "scorrelati" su base annuale possono stare a 0,73 su 60 giorni — ed è lì che si
  subisce il drawdown. *Costo: una riga per documento. Priorità alta.*
- **Buco 47** — **quota di tempo in contante / accessibilità del capitale** non è misurata da nessuna parte
  (`analysis/ops/weekly_healthcheck.py` non la calcola). Rilevante perché il PAC è **a serbatoio**
  ([[project_pac_inputs_2026_08_04]]) e perché confrontare rendimenti fra chi è sempre investito e chi è metà del
  tempo liquido è un confronto fra cose diverse.
- **Buco 48** — **l'ortogonalità fra gambe non è mai misurata condizionatamente allo stress**. Il repo sa che "le
  correlazioni saltano in crisi" (`05`, E1) ma nessuna analisi calcola la correlazione **dentro** le finestre di
  drawdown. Si aggancia ai buchi 45 (decile peggiore) e 46 (finestra).

### Conflitti per la mappa dei modelli
Nessuno nuovo. La terza occorrenza della **gamba di copertura** (in #29, oltre a E2 e G6) **non** cambia lo stato:
tre video della stessa fonte con lo stesso conflitto d'interesse e nessun fuori campione restano **una** affermazione
non verificata, non tre conferme.

---
