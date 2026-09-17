# Blocco G — Struttura di mercato e cornice (6 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Contesto del repo per questo blocco** (verificato il 2026-09-16, prima della lettura):
- **Efficienza dei mercati**: `08_asset_allocation_passiva` tratta l'EMH nelle tre forme (dagli appunti del blocco H
  ancora da attribuire) e la rifiuta come descrizione letterale, tenendola come esperimento mentale; `05` definisce
  l'alpha come rendimento **ortogonale** e non come sovraperformance.
- **Retail vs istituzionale**: nel repo esiste come vincolo pratico (spread, commissioni, esecuzione MT5, tick volume in
  `agents/quant_reviewer.md` §5, `02_liquidita_orderflow` per gli strumenti di order flow), non come cornice teorica.
- **Market making**: nessuna trattazione; la formula vantaggio × P(esecuzione) è emersa in questo distillamento (B20,
  D11, buco 12).
- **Stock picking**: `06_stock_selection` esiste, ma il pilastro investing è stato **deciso passivo**
  ([[project_stock_selector_eval_2026_06]]: Stock Selector archiviato, nessun edge dimostrato) → i video su selezione e
  "battere il mercato" vanno letti come **conferme o smentite di una decisione già presa**, non come proposte.
- **Letteratura fondativa**: nessun elenco di riferimenti canonici nel repo; `agents/quant_reviewer.md` cita López de
  Prado, Bailey, Harvey, White, Kelly, Thorp, MacLean-Ziemba, Fernholz.

---


## G1 — Quant Explains Algorithmic Market-Making

`aVzFKwyzwM0` · #104 · ~21 min · 3.866 parole

### Definizione e formule
Il market maker è un **fornitore di liquidità**: quota bid e ask e prende l'altro lato di ogni operazione. Il video
costruisce tutto su un "mercato del dado" e poi lo estende alle opzioni.

- 🔧 **Il prezzo medio è la media, e non per convenzione**: si pone $\theta$ = migliore stima dell'esito e si minimizza
  l'errore quadratico medio $\mathbb{E}[(X-\theta)^2]$. Derivata a zero → $\theta^{*} = \mathbb{E}[X]$. Sul dado: 3,5,
  che il dado non può realizzare. **La stima ottima in senso MSE non appartiene al supporto** — vale per ogni "prezzo
  giusto".
- 🔧 **Profitto atteso per operazione = spread / 2**, sotto l'ipotesi di **volume uguale sui due lati**. Deriva dalla
  legge dell'attesa totale: vendendo all'ask si guadagna $\text{ask} - X$, comprando al bid $X - \text{bid}$; in media
  $\frac{\text{ask}-\text{bid}}{2}$.
- 🔧 **Perché non si allarga lo spread all'infinito**: la formula è lineare nello spread, il **problema no**. Nella sua
  simulazione, con spread larghissimo si eseguono **due sole operazioni**. Il profitto è
  $\frac{\text{spread}}{2} \times (\text{numero di esecuzioni})$, e il secondo fattore **decresce con lo spread** → esiste
  un massimo interno. *"In mercati illiquidi lo spread sarà più largo; in mercati molto liquidi sarà strettissimo."*
  → **È la stessa struttura di B20/D11: vantaggio × P(esecuzione)**, qui derivata dal lato di chi quota anziché di chi
  subisce lo spread. Le due letture sono la stessa equazione vista dai due lati del book.
- **Estensione alle opzioni**: cambia una cosa sola, il payoff si realizza a $T$ e non all'istante. Prezzo medio =
  attesa risk-neutral scontata (teorema fondamentale del pricing) → serve **scegliere un modello** (Heston, ecc.) e
  **calibrarlo** alla superficie di volatilità di mercato; poi si simula (LGN, come F1). Aggiustamenti ulteriori per
  rischio di controparte e liquidità.
- ⚠️ **I due "catch" che il video dichiara da sé**:
  1. *"Abbiamo convergenza garantita solo al prezzo **del modello**. Non vuol dire che il modello sia corretto."* Con un
     modello sbagliato si accumulano **perdite** pur avendo quotato uno spread positivo. È esattamente la distinzione
     rumore-di-simulazione vs errore-di-modello del blocco F.
  2. La **copertura imperfetta mangia lo spread**: tra quotazione e scadenza bisogna coprirsi; frizioni e costi di
     transazione erodono il profitto teorico. *"Quanto efficacemente riesci a coprirti detta quanto dello spread
     incassi."*

### Domanda a cui risponde
"Da dove viene il profitto di chi sta dall'altro lato dei miei ordini, e a quali condizioni esiste?"

### Assunzioni
Volume simmetrico sui due lati (mai vero nella pratica: è l'ipotesi che **cancella la selezione avversa**, tema che il
video **non tocca**); distribuzione fissa nel mercato-dado; modello calibrato valido in avanti nel caso opzioni.

### Modi di fallire
- **Flusso sbilanciato / selezione avversa**: se chi transa con noi sa qualcosa, il volume non è simmetrico e
  $\text{spread}/2$ non è più il profitto atteso. Il video lo elude ipotizzandolo via. ⚠️ Registrato come **omissione
  della fonte**, non come regola.
- Modello errato → convergenza sicura al prezzo sbagliato.
- Spread ottimizzato ignorando la probabilità di esecuzione.

### Stato nel repo — **assente, e resta fuori perimetro**
Nessuna trattazione del market making (già verificato nel contesto del blocco). Noi siamo strutturalmente **price
taker**: paghiamo lo spread, non lo incassiamo.
**Ma il pezzo trasferibile esiste ed è già emerso due volte**: il prodotto **vantaggio × P(esecuzione)** e il fatto che
ottimizzare il primo fattore da solo è un errore. È il cuore di [[feedback_fill_ottenibile]]: un livello di entrata più
favorevole alza il vantaggio teorico e **abbassa la probabilità di essere eseguiti**; se il backtest concede il fill
comunque, ottimizza un prodotto in cui il secondo fattore è stato posto a 1 per costruzione. Il buco 12 resta quello.

### Rilevanza
**Reference** come mestiere; **applicabile ora** come formalizzazione del compromesso prezzo-esecuzione — è la versione
pulita del difetto che ci è costato due mesi.

### Claim registrati senza uso
Il rimando a Bühler-Horvath sul reinforcement learning per la copertura: citazione senza numeri, fuori perimetro.

---

## G2 — Quant vs. Discretionary Trading

`3gblERSSHXI` · #119 · 61 min · 10.231 parole — **il video più denso del blocco G** e la **fonte primaria** del conflitto
già registrato in `blocco-B.md`

### Definizione centrale: sistema **casuale** vs sistema **incerto**
| | sistema casuale | sistema incerto |
|---|---|---|
| esempi | roulette, craps, slot, lotteria | poker, scommesse su eventi, **trading** |
| probabilità | fisse, ben definite, **convergono** (LGN) | non fisse, riflettono una **credenza**, **nessuna convergenza** |
| l'esito del singolo evento | sconosciuto | sconosciuto |
| le nostre azioni sull'EV | **nessun effetto** | **lo determinano** |
| decisione ottima | non giocare | trovare $\pi^{*}$ |

Numeri di controllo: roulette americana, vantaggio del giocatore **−5,26%** per giro, fisso, **nessuna azione lo cambia**.
*"L'unica decisione ottima è non giocare."* → risposta a "il trading è gioco d'azzardo": **no, ma solo perché le azioni
spostano l'EV**; nulla garantisce che le tue lo spostino in positivo.

### 🔧 La funzione di politica $\pi^{*}$ e la sua variabilità nel tempo
L'oggetto ottimizzato **non è una strategia** ma un **insieme di azioni**: $\pi^{*} = \arg\max$ del rendimento
corretto per il rischio (esplicitamente Sharpe, non EV puro — *"non vogliamo solo massimizzare l'EV, vogliamo anche
minimizzare il rischio"*, mostrato con percorsi a bassa vs alta varianza attorno alla stessa media).

- **Dimostrazione per assurdo, con numeri suoi**: prova a imparare $\pi^{*}$ con machine learning su NVDA, split
  train/validation/test. **Sharpe 3,01 in addestramento**, validation e test *"lontanissimi"*. Conclusione sua:
  *"ho sovradattato al rumore"*, e quindi **la politica ottima condizionata ≠ politica ottima non condizionata**.
- **Il grafico chiave** (astrazione, non dati): EV sul verticale, $\pi$ sull'orizzontale, **una curva per ogni periodo**.
  Il $\pi^{*}$ del periodo arancione, applicato al periodo blu, dà **EV negativo**, e viceversa. Ciò che si cerca è la
  curva verde: un $\pi$ **globale**, non ottimo in nessun regime ma **positivo in tutti**.
  → 🔧 **Regola riusabile**: preferire il parametro che è positivo ovunque a quello che è ottimo da qualche parte. È
  esattamente ciò che nel repo chiamiamo robustezza al walk-forward, qui detto come criterio di **scelta**, non di
  verifica.
- *"L'unica funzione di politica fissa ragionevole è comprare e tenere. E la maggior parte delle persone non dovrebbe
  fare trading."* — coerente con il pilastro investing già deciso ([[project_stock_selector_eval_2026_06]]).

### ⚠️ "L'analisi tecnica non si può confutare" — la fonte primaria del conflitto
Argomento del video, per intero: *"non possiamo rigiocare lo stesso evento tecnico 10.000 volte. Se con quello hanno
fatto soldi, li hanno fatti… Non puoi fare un backtest su un tecnico e dire che lo hai confutato: non sono obbligato a
usarlo sempre, posso usarlo quando voglio."* E: *"assenza di prova non è prova di assenza"*. Esempio di supporto: poker
con coppia d'assi contro 5 giocatori — probabilità **non condizionata** di vincere 46%, quindi in teoria si dovrebbe
foldare, ma con bluff e dimensionamento efficaci la frequenza realizzata diventa **60/40**.

**Come lo registriamo** — e qui serve precisione, perché l'argomento è **per metà corretto**:
- ✅ **Corretto**: un backtest meccanico di una regola tecnica falsifica **quella regola meccanica**, non l'abilità
  discrezionale di chi la usa selettivamente. Sono ipotesi diverse.
- ❌ **Insufficiente**: da ciò non segue che l'abilità discrezionale sia **inosservabile**. È osservabile — con il
  track record **pre-registrato e prospettico** di quel trader. Il video non lo dice mai; è la strada che il repo ha già
  percorso con successo per i segnali del mentore ([[project_mentor_signals_edge_2026_07_08]]: direzione giusta 67-72%
  vs 32% casuale, stabile su 6 mesi, robusta al ritardo). **Quella misura è precisamente la confutabilità che la fonte
  dichiara impossibile.**
- **Conseguenza per noi**: la nostra ricerca sui livelli ([[project_level_research_v1_null_2026_07_06]], 384 trial
  pre-registrati, NULL su ogni TF) **non è toccata** da questo argomento e non va riaperta: falsificava regole
  meccaniche, che era esattamente ciò che si voleva falsificare. Ma il video ricorda che **il NULL non copre il
  discrezionale** — cosa che il repo non aveva mai affermato. Nessuna revisione necessaria, **una precisazione sì**.
  → **conflitto 1 del blocco G** (mappa dei modelli).

### Le due giustificazioni di stabilità, messe a confronto
| | discrezionale | quantitativo |
|---|---|---|
| fonte del vantaggio | esperienza, scelta **di quando accendere** | disallineamento **statistico/strutturale** |
| perché dovrebbe reggere in avanti | *"se ho ragione in media"* — nessuna garanzia esterna | il disallineamento **esiste nei dati storici e nessuno può toglierlo da lì**; ma *"nessuna garanzia che persista"* |
| rischi propri | comportamentali, fatica, posizione, liquidità; **il drawdown va letto come segnale di spegnere**, non come conferma | decadimento dell'alpha, affollamento, capacità/scalabilità, cambio di regime, qualità dati, rischio tecnologico e regolamentare |
| barriera d'ingresso | bassa → **è facilissimo operare con EV negativo** | alta → *"è più difficile agire del tutto, ma più facile agire con EV positivo"* |

⚠️ **L'asimmetria della barriera d'ingresso è l'osservazione più utile del video** ed è anche un giudizio su di noi: la
barriera alta non produce vantaggio, produce **selezione** — chi non sa fare, non agisce. Per un operatore individuale
che *può* agire, il filtro va ricostruito a mano, ed è esattamente ciò che fa
[[project_strategy_lifecycle_2026_08_04]] (pre-registrazione, contatore dei trial, futilità DSR).

### Il suo esempio di sistema discrezionale, con il conflitto d'interesse annesso
Calibra un modello di Heston alla superficie di volatilità (motore C++ proprio, *"600 righe"*, FFT, pesi strutturati) e
scambia le dislocazioni contro la superficie calibrata; **accende il sistema a propria discrezione** quando ritiene che
la percezione di volatilità del mercato sia alta. Ammette che *"se lo lasciassi acceso 24/7 accumulerei perdite"* e che
la soglia (*"VIX 15 basso, 25 medio, 30+ alto"*) sarebbe **arbitraria**.
⚠️ Due letture da tenere ferme: (a) **"non temo di condividere il mio vantaggio perché nessun retail scrive 600 righe di
C++"** è un argomento di barriera, **non** una misura di vantaggio: nessun numero di performance viene mostrato per
questo sistema; (b) *"posso attaccarci una misura quantitativa di cosa sia volatilità alta, ma resta discrezionale"* —
autoconsapevole e onesto, ma equivale a dire che **il criterio di accensione non è pre-registrato**, cioè il difetto che
il nostro ciclo di vita vieta esplicitamente.

### Il suo esempio di sistema quantitativo
Dati alternativi testuali (sentiment) → segnale in **sezione trasversale**, decili, portafoglio **neutrale al mercato**
(lungo il decile alto, corto il basso), relazione monotona decile→rendimento, **Sharpe ~2,72** *"in linea con
l'istituzionale"*. Letteratura citata e verificabile: **Loughran-McDonald, Tetlock, Antweiler-Frank**.
⚠️ Lo Sharpe 2,72 è **in campione, senza fuori campione né costi di turnover dichiarati** (li nomina come "da
considerare", non li applica) → **non-evidenza**, registrato per completezza. La **letteratura** citata, invece, è
reale ed è l'unico riferimento bibliografico verificabile del blocco.

### Stato nel repo
- La distinzione **casuale vs incerto** non è scritta da nessuna parte, ma è il presupposto implicito di tutto il
  workspace. Vale la pena scriverla: è la risposta compatta a "il trading è gioco d'azzardo".
- **$\pi^{*}$ variabile nel tempo**: il repo ha `docs/STRATEGY_LIFECYCLE.md` (ritiro, max 3 round di rifinitura) e
  [[feedback_strategy_conditional_edge]] (nessuna fase di mercato tradabile in assoluto), che sono la stessa idea; manca
  la formulazione come **scelta del parametro positivo ovunque invece che ottimo da qualche parte**. → **buco 40**.
- **Neutralità al mercato / sezione trasversale**: assente (operiamo su singoli strumenti, [[blocco-E]] E4). Fuori
  portata operativa oggi.

### Rilevanza
**Applicabile ora** per la regola del "positivo ovunque"; **reference** per il resto; **conferma** (non proposta) della
scelta passiva per il pilastro investing.

### Claim registrati senza uso
Sharpe 3,01 in addestramento (dichiarato lui stesso come sovradattamento), Sharpe 2,72 del long-short (in campione),
−5,26% della roulette (**verificato**: $-2/38 = -5{,}26\%$, corretto), 46% della coppia d'assi contro 5 giocatori
(plausibile, non verificato), 60/40 realizzato (aneddotico).

---

## G3 — Quant Trader on Retail vs. Institutional Trading

`j1XAcdEHzbU` · #133 · 29 min · 5.263 parole — **contiene la dimostrazione più onesta del canale**, e su di sé

### La confessione metodologica: due Sharpe dallo stesso conto
Mostra il proprio P&L da inizio anno, ribasato a 100.000 $, trading algoritmico + discrezionale (esclusi crypto e
previdenza), su Interactive Brokers:

| fase | valore | cosa è successo |
|---|---|---|
| inizio anno | 100.000 | sistema algoritmico giornaliero |
| picco iniziale | ~120.000 | poi perdite consistenti |
| minimo | ~80.000 | cambio strategia → **vendita di volatilità** |
| picco | ~130.000 | |
| crollo | **~70.000** | **liquidato**: *"ero in palestra, mi è arrivata la notifica che mi stavano liquidando"* |
| oggi (fine agosto) | ~130.000 | **+30% circa da inizio anno** |

🔧 **Il pezzo da conservare**, parole sue: *"se fossi un tipo diverso ti mostrerei solo questo: sono partito da 70.000 e
sono salito a 130.000, **Sharpe 6,28, Sortino 14,8**. Ma non ti mento: il mio Sharpe da inizio anno è **0,88**, il
Sortino **0,97**."*
→ **Lo stesso conto, lo stesso periodo di trading, due Sharpe che differiscono di un fattore 7 in base a dove si mette
l'inizio della finestra.** È la dimostrazione numerica, fatta dalla fonte su se stessa, del *look-elsewhere* applicato
alla **data di partenza** invece che ai parametri. Vale come esempio canonico, ed è di gran lunga il contributo più
utile del blocco G.

- 🔧 Corollario che enuncia subito dopo: *"queste metriche di performance sono **esse stesse variabili aleatorie**… la
  loro media non converge a un valore fisso. L'intero spazio è variabile nel tempo."* E l'osservazione al vetriolo sui
  guru: *"citano il teorema del limite centrale senza conoscere la differenza fra convergenza in probabilità e
  convergenza quasi certa"*.
- Aggiunge che Sharpe/Sortino sono appropriati *"per un backtest con una strategia fissa"*, **non** per un conto in cui
  si accendono e spengono sistemi diversi. ⚠️ Vale per noi: il nostro conto live mescola segnali del mentore e prove;
  uno Sharpe di conto aggregato non è la metrica giusta di nessuna delle due cose.

### Tassonomia: retail, sell side, buy side
- **Retail**: distribuzione **fortemente asimmetrica** (moltissimi disinformati, pochi informati). Due affermazioni
  controcorrente e, a nostro parere, corrette:
  1. *"Il mercato non sa che esisti"* — con capitale piccolo su strumenti liquidi **non ci sono problemi di scalabilità
     e nessuno ti prende di mira**; il P&L dipende solo dalle tue decisioni. Smonta il vittimismo ("gli istituzionali mi
     cacciano gli stop") senza smontare i costi reali (spread, commissioni).
  2. *"Le istituzioni saltano in continuazione"* — differenza fra Citadel e un fondo quant nuovo = differenza fra
     Microsoft e una startup. *"Non sanno nulla che tu non sappia; hanno gli stessi problemi di ogni altro trader."*
- **Sell side** = market making, quota due lati e incassa lo spread (→ G1). Rischi propri, elencati: **rischio di
  inventario** (essere colpiti solo sul bid senza che l'ask venga preso), **selezione avversa** (*"quello che sembra
  P&L facile è solo un trader con informazione migliore"* — l'esempio: qualcuno che carica call molto out of the money e
  poi il prezzo esplode), errori tecnici, volatilità, controparte.
  → ⚠️ **Qui la selezione avversa c'è**, mentre G1 l'aveva evitata con l'ipotesi di volume simmetrico. I due video vanno
  letti insieme: G1 dà la formula, G3 dice cosa la rompe.
- **Buy side** (parte quant): segnale da dati alternativi → grafico per quantili → portafoglio long-short. Ammette che
  il grafico *"non è una bella salita verso destra"*, ma che un po' di alpha c'è. Poi i vincoli: **capacità** (*"al
  crescere del capitale allocato il segnale si dissipa"*), relazioni, competizione per il capitale.
- 🔧 **Affermazione strutturale da tenere**: *"i disallineamenti di prezzo guidano il P&L, la volatilità guida i
  disallineamenti, e i mercati toro sono noiosi"*. Dichiarata come **aneddoto** (performance degli hedge fund in quel
  momento), non come misura — ma è coerente con quanto abbiamo misurato noi in
  [[project_trend_playground_lead_2026_08_14]] (ρ +0,857 fra volatilità di gruppo ed E[R]). **Due fonti indipendenti che
  puntano nella stessa direzione**, una misurata e una aneddotica: la nostra vale di più, ma la convergenza si registra.

### 🔧 L'allocazione fra strategie come combinazione lineare — e perché non la ottimizza
Presenta tre "sistemi" (discrezionale, algoritmico, mercato) come pesi di un portafoglio; calcola il portafoglio a
**varianza minima** e ottiene *"15% discrezionale, 75% algoritmico, il resto al mercato"*. Poi lo **butta via** lui
stesso: *"questi valori non sono stabili, sono stimati da dati, non convergono a niente. L'ottimizzazione mi dà dei pesi,
**ma sono sbagliati**… non è un problema di ottimizzazione globale."*
→ È la stessa conclusione del blocco E (MVO come massimizzatore dell'errore di stima), qui applicata al livello **meta**:
non i pesi fra titoli, ma i pesi fra **attività**. Conclusione operativa sua: *"faccio trading discrezionale quando mi
conviene, accendo i sistemi quando mi conviene, e **tengo la liquidità nell'S&P 500 quando mi conviene**"*.
⚠️ Con il caveat di G2: "quando mi conviene" **non è pre-registrato**. La struttura a combinazione lineare è però esatta
ed è esattamente la forma della nostra questione aperta (quanto capitale ai segnali del mentore vs PAC).

### Cosa dice di guardarsi — allineato col repo
*"L'informazione in questo spazio è **un'arma**"*: piattaforme che automatizzano il backtest e vendono abbonamenti per
"tick data migliori" o "schemi di ottimizzazione" (*"perché diavolo stai ottimizzando i backtest? Stai sovradattando
rumore"*), notizie (*"vogliono la tua attenzione, non sanno niente"*), broker che rendono il trading troppo facile
(*"su Coinbase puoi operare prima che il deposito sia liquidato"* — incassano commissioni). Rimedio proposto: padroneggia
gli strumenti quantitativi **per decidere da solo**.
→ Coerente con [[feedback_mass_search_vs_preregistration]] e con tutto l'impianto del nostro ciclo di vita. Nessuna
azione nuova.

### Stato nel repo
- **Sharpe su finestra scelta a posteriori**: `core/quant_metrics.py` calcola Sharpe/Sortino sul campione che riceve;
  il protocollo pre-registra il periodo (`docs/QUANT_REVIEW_PROTOCOL.md`, `STRATEGY_LIFECYCLE`), quindi la difesa
  **esiste per le strategie**. **Non esiste per il conto live**: nessuna regola dice su quale finestra si misura la
  performance del conto, e il conto oggi mescola attività diverse. → **buco 41**.
- **Allocazione fra attività**: `docs/INVESTING_PILLAR_PLAN.md` copre il pilastro passivo; nessun documento tratta la
  ripartizione del capitale **fra** PAC, segnali del mentore e prove. Era già implicito in
  [[project_mentor_signals_edge_2026_07_08]] ("l'edge del mentore va su capitale proprio"), mai scritto come pesi.
  → **buco 42**.
- **Selezione avversa**: mai nominata nel repo. Per noi, price taker, si manifesta come **riempimento quando il prezzo
  ci passa oltre** — cioè, di nuovo, [[feedback_fill_ottenibile]]. Il nome corretto del fenomeno è utile in sé.

### Rilevanza
**Applicabile ora** (i due Sharpe dello stesso conto; la finestra di misura del conto live; i pesi fra attività);
**reference** per sell side / buy side.

### Claim registrati senza uso
Il P&L personale è **autodichiarato e non verificabile** (grafico ribasato, nessun estratto conto): registrato come
**non-evidenza**, con una nota di merito — è l'unico caso in tutto il distillamento in cui la fonte mostra il **proprio
drawdown da liquidazione** invece di nasconderlo. Il valore del segmento sta nel metodo esibito, non nei numeri.

---

## G4 — "Academia is wrong. Markets aren't efficient. Alpha is a homerun."

`EwRlKEjJcr0` · #25 · 17 min · 2.671 parole — **è uno sfogo ("rant", parola sua), non una lezione**: zero formule, zero
dati. Va letto per le distinzioni concettuali, che sono buone, e maneggiato con cautela per le conclusioni, che in un
punto contraddicono frontalmente il nostro impianto.

### 1. EMH — la formulazione corretta (e coincide con quella già nel repo)
*"L'ipotesi dei mercati efficienti **non** significa che tutto sia prezzato correttamente e subito."* È un **modello**:
il prezzo di equilibrio è **l'aspettativa del mercato** sul valore equo **oggi, adesso**, dato l'insieme informativo —
non il valore equo. La reazione rapida a una notizia *"non deve essere razionale: è uno shock effimero di domanda e
offerta"*, e spesso viene ritrattata il giorno o la settimana dopo. *"È questo che crea l'opportunità."*
Formulazione compatta che offre: *"si costruisce ricchezza su **aspettative e aspettative infrante**"*.
- **Stato**: `08_asset_allocation_passiva` tratta già le tre forme e rifiuta l'EMH come descrizione letterale tenendola
  come esperimento mentale. **Questo video conferma, non aggiunge.** Il titolo ("l'accademia sbaglia, i mercati non sono
  efficienti") è più forte del contenuto: il contenuto dice che l'EMH è *mal insegnata*, non che sia falsa.

### 2. Alpha — definizione ortogonale, già nel repo, qui con il problema dell'ipotesi congiunta
*"Alpha non è il rendimento in eccesso su un riferimento."* Esempio suo: allocatori passivi che gestiscono ~1 miliardo e
dicono *"il mio alpha è stato il 5% perché ho battuto il mercato inclinando sul tech"* — sbagliato: quella è
**esposizione a un fattore**, e se bastasse *"si inclinerebbe brutalmente sul tech e si incasserebbe una commissione
mostruosa"*. Alpha = rendimento **ortogonale a un rischio sistematico, non diversificabile e remunerato**.
- 🔧 **Problema dell'ipotesi congiunta**, enunciato correttamente: un alpha misurato è sempre *"o vero alpha, o un
  fattore che non hai nel modello"*. Numero dichiarato: il **CAPM spiega il 50-70%** della variazione del profilo di
  rendimento (ordine di grandezza plausibile, non verificato; dipende interamente dal campione).
- **Stato**: `05` definisce già l'alpha come rendimento ortogonale; `benchmark_metrics` calcola alpha e beta su un solo
  fattore (mercato). Il **problema dell'ipotesi congiunta non è scritto da nessuna parte**: ogni nostro "alpha" a un
  fattore è, formalmente, indistinguibile da un'esposizione a un fattore che non stiamo modellando. → **buco 43**.

### 3. ⚠️ L'analogia del fuoricampo — dove la fonte esce dal nostro impianto
*"Allocare rischio è come presentarsi in battuta. Hai una media battuta: è ciò che ci si aspetta da te. Se la mandi
fuori dal campo, generi alpha… L'accademico direbbe: quel giocatore non può battere fuoricampo in modo consistente. Ma
**non era quella la domanda**. Deve essere nella posizione di poterlo fare."* E, esplicito:
> *"Non si tratta di stabilire se io possa continuare a generare alpha in modo consistente e statisticamente
> significativo. **Non è affatto quella la domanda.**"*

**Questa è una contraddizione diretta con il nostro protocollo**, e va registrata come tale:
- Per noi la domanda *è* esattamente quella. `docs/STRATEGY_LIFECYCLE.md` esiste per impedire di chiamare vantaggio il
  risultato di una coda destra: pre-registrazione, contatore dei trial persistente, futilità DSR, holdout sigillato.
  [[feedback_mass_search_vs_preregistration]] quantifica il punto: con ~0,25% di falsi passaggi, 10.000 candidati ne
  producono ~25 **dal solo rumore** — tutti "fuoricampo", nessuno ripetibile.
- **Cosa c'è di valido nell'analogia**: la parte sulla **media battuta**. *"Se hai una media battuta schifosa, come
  diavolo farai mai a battere un fuoricampo?"* Tradotto: si presidia il processo (esposizione al rischio ragionevole,
  costi bassi, sopravvivenza), non il singolo esito eccezionale. Questo è compatibile con noi.
- **Cosa non è valido**: che il fuoricampo conti come prova di abilità. In una distribuzione a coda destra il singolo
  esito estremo è **esattamente** ciò che il rumore produce. La differenza fra la sua posizione e la nostra è che lui
  parla da **allocatore professionale già dentro il gioco** (ha un mandato, opera comunque) e noi da **operatore che
  deve decidere se accendere una strategia**: il nostro problema è la selezione, il suo è l'esecuzione. Le due domande
  non sono la stessa, e la sua risposta non trasferisce.
  → **conflitto 2 del blocco G** (mappa dei modelli).

### 4. Rischio di modello — enunciato nella sua forma più netta
*"Non esiste una distribuzione generatrice dei dati n-dimensionale. Costruiamo modelli per approssimare la verosimiglianza
di stati del mondo… **tutte le probabilità che generiamo sono sbagliate. Garantito. Il 100% delle volte.** Se potessi
scommettere la casa su una cosa sola, scommetterei che il tuo modello è sbagliato."*
Elenca esattamente gli strumenti dei blocchi A-F (stimatori, medie, varianze, modelli di Markov nascosti, catene di
Markov, moto browniano aritmetico e geometrico, superfici di volatilità) e dice che in aula non si fa mai il passo
indietro.
- 🔧 **La domanda che dice di porre a ogni backtest**, e che è la cosa migliore del video:
  > *"Se questo è già successo, perché pensi che succederà di nuovo in futuro?"*
  > *"E nessuno sa rispondere. Nessuno."*
  È, parola per parola, il requisito di **razionale ex ante** che il nostro ciclo di vita impone prima della
  pre-registrazione, e la stessa cosa che [[feedback_backtest_long_history_falsification]] chiede quando un edge
  "funziona solo post-COVID". **Convergenza piena, nessuna azione nuova** — ma la formulazione è più efficace della
  nostra e vale come frase di controllo da usare davvero.
- Corollario metodologico esplicito: *"non banalizzare"*, *"preferisco fare la domanda banale ed essere meno in errore
  che avere troppo ego per sembrare stupido"*.

### 5. "L'alpha decade e le strategie vanno tenute segrete" — rigettato
*"Non è così. Sui siti di molti fondi quantitativi trovi le loro strategie principali; non è un segreto. Vai a fare
reverse engineering, costruisci le tue varianti e alloca rischio."* Analogia della palestra: chiedere *"dimmi cosa è
meglio per il mio capitale"* è come chiedere *"dimmi cosa è meglio per il mio allenamento"* — la risposta dipende
dall'obiettivo (più muscolo o meno grasso; rendimento potenziale alto con percorso accidentato **e drag di volatilità**,
oppure crescita geometrica ottimale nel lungo periodo). *"Non esiste una taglia unica."*
- Nota: cita esplicitamente **drag di volatilità** e **crescita geometrica ottimale** come dimensioni della scelta →
  aggancio diretto al blocco C (Kelly, $R_G \approx \bar{R} - \sigma^2/2$).
- ⚠️ La chiusa (*"esistono stili di allocazione tattica che evitano quei drawdown"*) è **affermata e mai mostrata**, ed
  è in tensione con tutto il resto del canale (G2: nessuna garanzia in avanti). Non-evidenza.

### Stato nel repo (riepilogo)
EMH ✅ già trattata; alpha ortogonale ✅ già in `05`; **ipotesi congiunta ✗ assente** (buco 43); domanda del "perché
dovrebbe ripetersi" ✅ già nel ciclo di vita, in forma meno memorabile; segretezza delle strategie: non pertinente
(non abbiamo nulla da tenere segreto).

### Rilevanza
**Reference** con due eccezioni applicabili ora: il buco 43 e la frase di controllo sul backtest.

### Claim registrati senza uso
CAPM 50-70% della varianza (ordine di grandezza, campione ignoto); "gli allocatori passivi che gestiscono un miliardo
sbagliano la definizione di alpha" (aneddoto); "si possono evitare i drawdown con l'allocazione tattica" (non mostrato,
in tensione con G2).

---

## G5 — The 5 Papers that Built Modern Quant Finance

`ZwS1gMGegrM` · #93 · 24 min · 3.599 parole — **è il riferimento bibliografico che nel repo mancava**

### I cinque lavori, con ciò che ciascuno stabilisce
| anno | lavoro | risultato | cosa ne resta per noi |
|---|---|---|---|
| **1900** | **Bachelier**, *Théorie de la spéculation* | moto browniano **aritmetico** applicato ai prezzi, cinque anni prima di Einstein; già una formula di prezzo | l'incertezza **si allarga con il tempo**: la varianza cresce, non il livello. Ammette prezzi negativi — difetto che nel **2020, con il petrolio negativo, è tornato un pregio** (alcuni desk sono tornati a Bachelier) |
| **1964** | **Sharpe**, CAPM (su Markowitz anni '50) | **solo il rischio sistematico è remunerato**; l'idiosincratico si diversifica via → nascono beta e alpha | è la base di `05` e di `benchmark_metrics` |
| **1973** | **Black-Scholes**, *The Pricing of Options and Corporate Liabilities* | **argomento di replica**: non si prevede il sottostante, si replica; sotto non arbitraggio, scambio continuo e assenza di frizioni, il prezzo dell'opzione = costo di costruire e mantenere la copertura. Passaggio dalla misura P alla misura Q. Dà la **volatilità implicita** | fuori perimetro operativo; la lezione trasferibile è l'inversione: **si può leggere un'aspettativa del mercato invertendo un modello** |
| **1994** | **Dupire**, *Pricing with a Smile* | volatilità **locale**: funzione deterministica di strike e scadenza, calibrata agli strumenti liquidi | la ragione per cui esiste: la superficie **non è piatta** |
| **1999** | **Carr-Madan**, valutazione con **trasformata di Fourier veloce** | se la funzione caratteristica del processo è nota, si trasforma il problema in un dominio dove la soluzione è analitica, si risolve, si antitrasforma: **elimina la simulazione** | *"il mio lavoro preferito"*, dice. Fuori perimetro; è il seguito naturale del blocco F (efficienza della simulazione) |

- Nota di trasparenza: dichiara che **Dupire è capo della ricerca quant in Bloomberg**, dove lui ha ottenuto il primo
  incarico, e che si conoscono. Conflitto d'interesse dichiarato dalla fonte stessa; non altera i fatti storici.

### 🔧 Il pezzo davvero operativo: due Sharpe uguali, due cose diverse
Animazione con **due portafogli che battono il mercato, entrambi con Sharpe ≈ 2,5**:
- quello di sinistra è **solo esposizione al mercato con leva** — rendimenti fortemente correlati; se il mercato crolla,
  crolla con lui;
- quello di destra **non ha nulla a che vedere col mercato**: se il mercato crolla, continua a sovraperformare. Quello è
  **alpha**.

→ **Regola**: lo Sharpe **non distingue** fra le due cose. Serve la scomposizione rispetto ai fattori remunerati.
Si somma esattamente al buco 43 (ipotesi congiunta) e al buco 41 (finestra di misura): **una metrica aggregata non dice
di che natura sia il rendimento**, che è la stessa tesi di `04_quant_metodologia` ("le metriche sono necessarie, non
sufficienti").

### 🔧 Perché le code sono sottostimate — catena causale esplicita
Log-normalità ⇒ curtosi in eccesso ignorata ⇒ **rischio di coda gravemente sottostimato**. E la causa che indica: *"le
code grasse ci sono perché **le distribuzioni non sono fisse: cambiano nel tempo**"*. Il 1987 è l'evento che ha reso
visibile l'errore e ha prodotto lo smile.
→ Stessa tesi del blocco A (code pesanti, CLT inservibile con momenti infiniti) e del blocco D (non stazionarietà), qui
con una **spiegazione generativa** delle code grasse: non un'altra distribuzione fissa più larga, ma **una distribuzione
che si muove**. Distinzione che conta: nel primo caso si cambia la distribuzione del modello, nel secondo si smette di
credere a qualunque distribuzione fissa. **La seconda lettura è quella che il repo ha già adottato di fatto**
(ricampionamento dallo storico invece di modelli parametrici) senza averla mai motivata così.

### Compromesso efficienza-efficacia
Enunciato esplicito: *"si può sempre aggiungere complessità al modello, ma si sacrifica efficienza; i modelli migliori
ottimizzano entrambe."* Vale fuori dal pricing: è la ragione per cui `core/regime.py` usa ADX/ATR deterministici invece
di un GARCH.

### Stato nel repo
- **Nessun elenco di riferimenti canonici** esisteva (verificato prima della lettura): `agents/quant_reviewer.md` cita
  López de Prado, Bailey, Harvey, White, Kelly, Thorp, MacLean-Ziemba, Fernholz — cioè la letteratura della
  **validazione e del dimensionamento**, non quella dei **fondamenti**. Le due liste sono complementari e la seconda
  mancava. → **buco 44**: nessun documento del repo dice da dove vengono le idee che usiamo.
- Bachelier / Black-Scholes / Dupire / Carr-Madan: **fuori perimetro operativo** (non trattiamo opzioni). Sharpe/CAPM:
  già dentro.

### Rilevanza
**Reference**, con un'eccezione **applicabile ora**: la coppia "stesso Sharpe, natura diversa" e la catena
log-normalità → code sottostimate.

### Claim registrati senza uso
Sharpe ≈ 2,5 dei due portafogli (animazione costruita, non dati); "alcuni desk sono tornati a Bachelier per il petrolio
negativo nel 2020" (plausibile e documentato in letteratura, non verificato qui).

---

## G6 — "Stock Picking is Worse than Gambling at a Casino (I Can Prove It)"

`E2PuxT_SucA` · #38 · 17 min · 2.506 parole — ⚠️ **chiude con la vendita di un corso**: la seconda metà è l'argomento
commerciale della "gamba di copertura", già visto in E2 e già marcato con cautela in `08`

### 🔧 L'argomento tecnico, che è valido e utile
Non è "lo stock picking rende meno": è **che il rendimento di un titolo scelto non è idiosincratico**.
1. **Il beta non si elimina scegliendo bene.** Esempio: VRT, +3.000% in pochi anni. *"Supponiamo tu sia il miglior
   selezionatore di titoli del mondo e l'avessi visto arrivare da mille miglia."* **Beta 2,22**, drawdown massimo
   **61%** contro il **20%** del mercato nello stesso periodo. Su 100.000 $ significa una perdita non realizzata di
   60.000 $. *"Ma è tornato su." — "Sì. E quando non torna?"* → **bias di sopravvivenza**, nominato correttamente.
2. **La media aritmetica alta è prodotta da pochi valori estremi iniziali** che trascinano su la media ma non la
   crescita composta. CAGR mercato **13,9%** vs selezione **27,3%** *nel percorso medio* — e qui arriva il punto vero.
3. 🔧 **La tecnica da rubare: condizionare sul decile peggiore dei percorsi.** Invece di confrontare le medie, confronta
   le due strategie **sul 10% di percorsi peggiori**:

   | | drawdown massimo medio (peggior 10%) | CAGR medio (peggior 10%) |
   |---|---|---|
   | esposizione al mercato | **50%** | **+10%** |
   | selezione di titoli | **80%** | **−1,9%** |

   *"Non scegli tu quale percorso cammini."* Sul decile peggiore il segno del CAGR **cambia**: la selezione di titoli
   passa da "più redditizia" a **distruttiva**, mentre il mercato resta positivo. **Il confronto fra medie e il
   confronto fra code danno risposte opposte, sugli stessi due portafogli.**
   → Questo è il contributo riusabile del video ed è **un metodo, non un'opinione**: si applica a qualunque coppia di
   strategie.

### Domanda a cui risponde
"Quanto di ciò che credo di aver guadagnato scegliendo bene è in realtà beta con la leva, e cosa succede se il percorso
che cammino è uno di quelli brutti?"

### Assunzioni
Simulazioni sue, parametri non dichiarati, orizzonte 10 anni; nessun costo, nessuna tassazione. I numeri sono
**illustrativi**, non misure.

### Modi di fallire (della tesi, non dello strumento)
- L'argomento vale contro la **selezione arbitraria**, non contro strategie **neutrali al mercato** — lo dice
  esplicitamente lui (*"non stiamo parlando di strategie che neutralizzano il beta"*). Non è una confutazione dello
  stock picking istituzionale.
- Il decile peggiore è calcolato **su una simulazione parametrizzata da lui**: cambiando la volatilità assunta per la
  gamba "selezione", il risultato si muove a piacere. Il **metodo** è solido, i **numeri** no.

### Stato nel repo — **conferma di una decisione già presa**
Il pilastro investing è già passivo e lo **Stock Selector è archiviato** con motivazione propria
([[project_stock_selector_eval_2026_06]]: nessun edge, dimostrato su dati, backtest e MVP). Il video **non riapre
nulla**: aggiunge, a posteriori, la ragione strutturale (beta non eliminabile + drag di volatilità) a una decisione
presa su base empirica. **Due strade indipendenti, stessa conclusione.**
- **Assente invece la tecnica**: nessuna analisi del repo condiziona sul **decile peggiore dei percorsi**. `STRATEGY_LIFECYCLE`
  §8bis usa percentili alti del Monte Carlo per fissare le soglie di ritiro, ma nessun confronto **fra alternative** è
  mai stato fatto sulla coda invece che sulla media. → **buco 45** (e si aggancia al buco 39: percentile vs probabilità).

### ⚠️ La parte commerciale, registrata e scartata
Chiusa del video: si introduce una **gamba di copertura con monetizzazione** sopra l'esposizione al mercato; numero
esibito: il **percentile 1%** del portafoglio coperto dà *"+50% del capitale iniziale su 10 anni"* contro **−70%** della
selezione di titoli. Poi: *"è esattamente la strategia che insegno nel mio corso dal vivo di quattro settimane… candidati
per la prossima coorte"*.
→ **Stessa ricetta di E2, stessa fonte, stesso conflitto d'interesse**, e ancora una volta **nessun backtest fuori
campione, nessun costo della copertura, nessun parametro dichiarato**. `08_asset_allocation_passiva` la porta già con la
nota "speculativo/promozionale, da verificare": **la nota resta, e questo video ne è la seconda conferma indipendente**.
Registrato come **non-evidenza**. Da notare che è in tensione con il suo stesso G2 (*"nessuna garanzia che una cosa
persista in avanti"*): la gamba di copertura viene presentata con la certezza che il resto del canale nega.

### Rilevanza
**Applicabile ora** per la tecnica del decile peggiore; **conferma** per il pilastro passivo; la gamba di copertura
resta **non approvata**.

### Claim registrati senza uso
Tutti i numeri: 13,9% / 27,3% CAGR, 50%/80% drawdown sul decile peggiore, +10%/−1,9% CAGR sul decile peggiore, 1%
percentile +50% vs −70%. Simulazioni proprie, parametri non dichiarati. Il beta 2,22 e il drawdown 61% di VRT sono
invece **verificabili in linea di principio** (dati pubblici) e plausibili.

---

## Sintesi del blocco G

| # | video | cosa aggiunge | stato nel repo | rilevanza |
|---|---|---|---|---|
| G1 | Algorithmic Market-Making | prezzo medio = attesa (minimo MSE); **profitto = spread/2**; il massimo è interno perché **P(esecuzione) decresce con lo spread**; convergenza garantita solo **al prezzo del modello** | market making assente (fuori perimetro); il prodotto vantaggio × P(esecuzione) è il buco 12 | reference + **ora** |
| G2 | Quant vs. Discretionary | **casuale vs incerto**; $\pi^{*}$ variabile nel tempo (Sharpe 3,01 in addestramento → crollo fuori); **scegliere il parametro positivo ovunque, non ottimo da qualche parte**; barriera d'ingresso asimmetrica | ciclo di vita copre il concetto, non la regola di scelta | **ora** (buco 40) |
| G3 | Retail vs. Institutional | **Sharpe 0,88 vs 6,28 sullo stesso conto** cambiando l'inizio della finestra; metriche come variabili aleatorie; selezione avversa; allocazione fra attività come combinazione lineare non ottimizzabile | finestra pre-registrata per le strategie, **non per il conto**; pesi fra attività mai scritti | **ora** (buchi 41, 42) |
| G4 | "Academia is wrong" | EMH come modello di **aspettative**; alpha ortogonale; **problema dell'ipotesi congiunta**; *"se è già successo, perché dovrebbe succedere di nuovo?"* | EMH e alpha già nel repo; ipotesi congiunta assente | reference + **ora** (buco 43) |
| G5 | The 5 Papers | bibliografia fondativa (Bachelier, Sharpe, Black-Scholes, Dupire, Carr-Madan); **stesso Sharpe, natura diversa**; code grasse perché **le distribuzioni si muovono** | nessun elenco di riferimenti fondativi | reference (buco 44) |
| G6 | "Stock Picking is Worse than Gambling" | **condizionare sul decile peggiore dei percorsi** ribalta il confronto fra strategie; il beta non si elimina scegliendo bene | conferma l'archiviazione dello Stock Selector; tecnica assente | **ora** (buco 45) |

**Valutazione onesta del blocco**: è il blocco più **discorsivo** (nessuna formula nuova oltre a spread/2) ma non il
meno utile: contiene la **migliore dimostrazione di metodo di tutto il distillamento** (G3, i due Sharpe dallo stesso
conto) e due tecniche riusabili subito (decile peggiore in G6, criterio "positivo ovunque" in G2). Contiene anche il
**secondo spot commerciale** della gamba di copertura (G6 dopo E2), che non cambia stato.

### Buchi aperti dal blocco G
- **Buco 40** — manca la regola di **scelta** del parametro: preferire il valore **positivo in tutti i regimi** a quello
  **ottimo in uno**. Il repo verifica la robustezza *dopo* (walk-forward); non la usa come criterio *di selezione*.
  → `STRATEGY_LIFECYCLE`, template di pre-registrazione.
- **Buco 41** — nessuna regola sulla **finestra di misura del conto live**. Le strategie hanno il periodo
  pre-registrato; il conto no, e oggi mescola attività diverse (segnali del mentore, prove). Uno Sharpe di conto non
  misura nessuna delle due. → `docs/QUANT_REVIEW_PROTOCOL.md`, healthcheck settimanale.
- **Buco 42** — nessun documento scrive i **pesi fra attività** (PAC, segnali del mentore, prove) né dice chi li
  decide e quando si rivedono. Implicito in [[project_mentor_signals_edge_2026_07_08]], mai esplicito.
  → `docs/INVESTING_PILLAR_PLAN.md` o un documento di allocazione.
- **Buco 43** — **problema dell'ipotesi congiunta** mai enunciato: ogni alpha a un fattore è indistinguibile da
  un'esposizione a un fattore non modellato. → `04`, `05`, docstring di `benchmark_metrics`.
- **Buco 44** — nessun **elenco di riferimenti fondativi** nel repo (quelli in `agents/quant_reviewer.md` riguardano
  validazione e sizing, non i fondamenti). → `fondamenti_tecnici/_INTAKE.md` o un `RIFERIMENTI.md`.
- **Buco 45** — i confronti **fra alternative** si fanno sulla media; mai **condizionati sul decile peggiore dei
  percorsi**, dove il segno può cambiare. → `core/quant_metrics.py`, `04`.

### Conflitti per la mappa dei modelli
1. **"L'analisi tecnica non si può confutare"** (G2, fonte primaria del conflitto già registrato in `blocco-B.md`).
   *Condizioni di validità*: vero per l'**abilità discrezionale di un operatore che sceglie quando applicare una
   regola**; falso come affermazione generale. *Contraddice*: la lettura ingenua secondo cui il NULL sui livelli
   ([[project_level_research_v1_null_2026_07_06]], 384 trial) chiuderebbe anche il discrezionale. *Stato*: **nessuna
   revisione del NULL**; si aggiunge la precisazione che quel NULL falsifica **regole meccaniche**, e che l'abilità
   discrezionale si misura con il **track record prospettico pre-registrato**, strada già percorsa con successo per il
   mentore.
2. **"Non è la domanda se l'alpha sia consistente e statisticamente significativo"** (G4, analogia del fuoricampo).
   *Condizioni di validità*: coerente per un **allocatore con mandato**, che opera comunque e deve solo restare in
   posizione. *Contraddice* frontalmente `docs/STRATEGY_LIFECYCLE.md` e
   [[feedback_mass_search_vs_preregistration]] per chi deve **decidere se accendere** una strategia: lì la
   significatività corretta per molteplicità è esattamente la domanda. *Stato*: **la nostra posizione resta**; si
   registra la distinzione fra il problema di **selezione** (nostro) e quello di **esecuzione** (suo).
3. **Gamba di copertura con monetizzazione** (G6, seconda occorrenza dopo E2). *Stato*: **invariato** — resta la nota
   "speculativo/promozionale, da verificare" in `08_asset_allocation_passiva`. Due video della stessa fonte, entrambi
   con conflitto d'interesse dichiarato, nessun fuori campione: **due occorrenze non fanno una conferma**.

---
