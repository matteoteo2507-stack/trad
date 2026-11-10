# Blocco E — Costruzione di portafoglio (8 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Contesto del repo per questo blocco** (verificato il 2026-09-16, prima della lettura):
- **`05_portfolio_rischio`**: alpha come rendimento ortogonale, tassonomia del rischio (idiosincratico / settoriale /
  mercato), limiti della diversificazione, **non-stazionarietà delle correlazioni**, volatility drag, orthogonal return
  streams, VRP, tail risk, **PCA**, **CAPM ed estensioni**, beta per settore, costruzione goal-driven. Gran parte viene
  da **#29**, cioè da un video di questo stesso canale (già distillato).
- **`core/quant_metrics.py`**: `benchmark_metrics` (alpha di Jensen, beta, information ratio, tracking error, R²) su
  rendimenti. **Nessun ottimizzatore di portafoglio** in tutto il repo (ricerca per `cvxpy`, `scipy.optimize`,
  `pypfopt`, `efficient_frontier`: nessun risultato).
- **`08_asset_allocation_passiva`**: pilastro PAC (All-World, buffer separato, glide-path, niente timing).
- **Buco 18** (blocco C): ribilanciamento e rendimento da diversificazione non sono scritti da nessuna parte.
- **Assenti**: beta mobile monitorato nel tempo, ottimizzazione media-varianza, Black-Litterman, modelli fattoriali
  (Fama-French, Carhart), market neutral.

---

## E1 — How a Quant Manages a Portfolio

`JjbBAyu0DmI` · #85 · 43 min · 6.044 parole — ⚠️ **ampia sovrapposizione con #29**, già distillato in `05`

### Ciò che coincide con il già distillato
Tassonomia del rischio (idiosincratico, settoriale, di mercato) con l'esempio dei 9 titoli in 3 settori; le correlazioni
che **saltano insieme** durante lo stress (dazi 2025) e annullano il beneficio della diversificazione; PCA come
decomposizione spettrale; CAPM e alpha ≠ sovraperformance del benchmark. Tutto già in `05`.

### Ciò che aggiunge (voci nuove)
- 🔧 **Come si leggono i carichi delle componenti principali** — regola pratica:
  - **PC1**: se **tutti i carichi hanno lo stesso segno**, è il **fattore di mercato**;
  - **PC2**: i segni si raggruppano **per settore** → fattore settoriale (e può spillare su PC3–PC5);
  - le componenti successive raccolgono l'**idiosincratico**.
  Numeri del suo campione: PC1 **27%** della varianza, prime tre **60%**, prime cinque-sei **~90%**. Con 9 titoli: la
  decomposizione non è "il mercato spiega tutto", il mercato spiega **un quarto**.
- 🔧 **Quota di varianza non spiegata come misura di idiosincraticità per titolo**: UNH ha la quota più alta (l'anno del
  suo crollo) → strumento diagnostico per capire **chi** nel portafoglio si muove per ragioni proprie.
- **Beta per settore, misurati**: tech **sovraesposto** (beta > 1), healthcare ~¼ di quell'esposizione, staples ~⅓.
  Conseguenza operativa: nello stress il tech scende quanto il mercato o più, e *"servirà un rendimento molto maggiore
  del drawdown per recuperare"* (asimmetria del recupero, coerente con il volatility drag di C5).
- **Frase operativa da tenere**: *"sviluppare l'allocazione obiettivo è la parte facile; il lavoro vero è osservare la
  **stabilità** di quella selezione nel tempo"* — dice di ri-stimare le esposizioni **su base mobile** e correggere.
  ⚠️ Con il caveat di C4/B13: una ri-stima mobile continua è anche un modo per inseguire il rumore; le soglie di
  correzione andrebbero dichiarate prima.
- **Beta come statistica non convergente**: mostra i beta mobili che **saltano** durante lo stress. È la
  non-stazionarietà applicata al parametro che si usa per costruire il portafoglio.
- **Stato**: `benchmark_metrics` calcola alpha e beta **una volta**, su tutto il campione; **nessun monitoraggio mobile
  del beta** e nessuna lettura dei carichi PCA. → **buco 30**.
- **Rilevanza**: applicabile ora per il pilastro investing (il PAC è un solo ETF: il beta mobile non serve finché non ci
  sono più gambe); **reference** per il trading.

### Claim registrati senza uso
- Cita un proprio paper su fattori di sentiment (SSRN) — non verificato.
- *"Tenere un solo titolo in media non conviene: l'esposizione idiosincratica in sezione trasversale è mediamente
  negativa"* — affermazione di letteratura, non dimostrata nel video; coerente con `05` (rischio idiosincratico
  diversificabile e non remunerato).

---

## E2 — How Quants Engineer Portfolios

`1r39EGSm9fw` · #47 · 10 min · 1.586 parole — ⚠️ **conflitto d'interesse dichiarato**: chiude dicendo che questo è
*"l'obiettivo dichiarato del fondo su cui sto lavorando, Long Tail"*

### È la fonte primaria di un blocco già marcato con cautela nel repo
`08_asset_allocation_passiva` contiene la nota *"portfolio engineering con hedge leg (speculativo/promozionale, da
verificare)"*, costruita su numeri di terza mano. **Questo video è l'originale.** I numeri, tutti su **un singolo
backtest di 5 anni, in campione, senza walk-forward né fuori campione**:

| portafoglio | Sharpe | beta | max drawdown | rendimento totale 5 anni |
|---|---|---|---|---|
| SPY | 0,77 | 1,00 | −25% | ~80% |
| KMLM da solo (trend following gestito) | 0,02 | −0,12 | −36% | −4,33% |
| 70% SPY + 30% KMLM | 0,76 | ~0,5 | **−14%** | ~50% |
| 70/30 **con leva** per pareggiare l'esposizione | **0,79** | — | **−22%** | > 80% |

- **Lettura onesta**: il 70/30 dimezza il drawdown ma **rinuncia a un terzo del rendimento**; è la versione con **leva**
  a battere l'indice "su quasi ogni misura", e la leva è esattamente ciò che richiede che la correlazione negativa
  **tenga** nel momento sbagliato. Un solo campione di 5 anni non può dirlo. La cautela già scritta in `08` resta
  valida, ora con la fonte identificata.

### 🔧 Il risultato pulito: gli Sharpe ortogonali si sommano in quadratura
- Per flussi **non correlati** combinati con pesi ottimali:
  $$SR_{\text{tot}}=\sqrt{SR_1^2+SR_2^2+\dots}$$
- **A cosa serve**: dà il **valore quantitativo dell'ortogonalità**, cioè quanto vale davvero aggiungere una gamba
  scorrelata. Esempio: a uno stream con Sharpe 0,8 se ne aggiunge uno ortogonale con Sharpe 0,3 →
  $\sqrt{0{,}64+0{,}09}\approx0{,}85$. Aggiungere una gamba **debole** rende poco: serve o Sharpe decente o
  **correlazione negativa** (che va oltre la formula ortogonale).
- ⚠️ **Incoerenza interna della fonte**: con Sharpe 0,02, per questa stessa formula KMLM **non aggiunge nulla** allo
  Sharpe. Il beneficio che mostra viene dalla **correlazione negativa** e dalla riduzione del drag (crescita
  geometrica), non dall'additività degli Sharpe che cita.
- **Condizione dimenticata**: il beneficio esiste **ribilanciando** a pesi costanti (C6, buco 18). Senza ribilanciamento
  il 70/30 deriva e il vantaggio svanisce.
- **Stato**: `05` ha orthogonal streams e la varianza a tre termini, **non** la formula quadratica sugli Sharpe.
  **Rilevanza**: **applicabile ora** — è il criterio per decidere se vale la pena aggiungere un secondo flusso (p.es.
  segnali mentore accanto al PAC: quanto Sharpe serve perché sposti qualcosa).
- → **buco 31**.

### Il resto
- Volatility drag spiegato con due percorsi a pari media (~8% di differenza terminale) e l'asimmetria del recupero:
  identico a C5 e a `05`. *"Non si sfugge al drag se si compone geometricamente."* **Nessuna voce nuova.**
- *"Il gestore passivo che tiene solo SPY: per cosa viene pagato?"* — polemica di categoria, non catalogata.

---

## E3 — Why Portfolio Optimization Doesn't Work

`eZIITtd3UfY` · #153 · 21 min · 3.578 parole

### L'effetto voluto, mostrato su un caso in cui funziona davvero
- Tre **giochi d'azzardo correlati** (una struttura di covarianza comune, per costruzione **invariante nel tempo**).
  Sharpe individuali 0,54 · 1,18 · 1,83. La combinazione ottimale (**portafoglio di tangenza**, massimo Sharpe) raggiunge
  **1,92**, cioè **più del gioco migliore da solo**: è il beneficio della diversificazione, misurato.
- **Cosa massimizza davvero**: non il percorso più ricco (quello è casuale), ma il **rendimento atteso corretto per il
  rischio dell'insieme** dei percorsi futuri. Nelle simulazioni la linea dei pesi ottimali sta **sopra in media** alle
  altre combinazioni.
- **Condizione perché funzioni**: media, varianza e **covarianza non cambiano nel tempo**. Nei giochi è vero per
  costruzione.

### Perché si rompe sugli asset
1. **I parametri sono bersagli mobili**: Apple 2005 ≠ Apple oggi; i pesi ottimi del 2005 *"potrebbero non funzionare
   nemmeno nel 2006"*.
2. **Il rendimento atteso è la stima peggiore che abbiamo** (A6, B17, D8): tutta l'ottimizzazione eredita quell'errore.
- **Dimostrazione nel video**: si trovano i pesi ottimi su un campione, si generano **nuovi** rendimenti per gli stessi
  titoli e i vecchi pesi **sottoperformano** sistematicamente il nuovo ottimo. *"Abbiamo sovradattato lo Sharpe nello
  spazio dei rendimenti storici."*
- **Posizione finale, equilibrata**: l'ottimizzazione è una **lente statistica** legittima *se* le stime sono decenti e
  ragionevolmente stabili; è overfitting se si prendono i pesi come verità.

### 🔧 Ciò che il video non dice (e che serve se mai costruiremo un portafoglio multi-gamba)
- Il difetto ha un nome: l'ottimizzazione media-varianza è un **massimizzatore dell'errore di stima** — sovrappesa
  proprio gli asset il cui rendimento atteso è stato **sovrastimato**, perché l'ottimizzatore non distingue segnale da
  errore.
- **Rimedi standard**, nessuno citato nel video:
  - **stimatori ridotti/contratti** della matrice di covarianza (shrinkage, Ledoit-Wolf) e dei rendimenti attesi;
  - **ottimizzazione resampled** (media dei pesi su molte ri-estrazioni dei parametri) — è l'analogo della
    "simulazione con incertezza sui parametri" del buco 13;
  - **minima varianza** o **risk parity**, che **non richiedono** il rendimento atteso: eliminano l'input più
    inaffidabile;
  - **pesi uguali (1/N)** come benchmark serio: in letteratura batte spesso la media-varianza fuori campione.
- **Implicazione per noi**: se un giorno servisse combinare più flussi (PAC + segnali mentore + eventuale terzo
  secchio), la scelta di default non è l'ottimizzatore, è **pesi semplici dichiarati prima**, con l'ottimizzazione al
  massimo come controllo. Coerente con il pilastro passivo già deciso e con il buco 31 (quanto Sharpe serve perché una
  gamba sposti qualcosa).
- **Stato**: nessun ottimizzatore nel repo (verificato); `05` ha la teoria ma non questi rimedi. → **buco 32**.
- **Rilevanza**: **applicabile ora** come criterio di scelta (non ottimizzare), futuro come strumento.

---

## E4 — Black-Litterman vs Mean-Variance Optimization (MVO) in Python

`o1mCFVt79Y8` · #73 · 38 min · 5.613 parole — **il video più utile del blocco E**

### Frontiera efficiente: la parte teorica che vale la pena tenere
- **Annidamento dei sottoinsiemi**: la frontiera di un **sottoinsieme** di asset è sempre **contenuta** in quella di un
  soprainsieme — al peggio si replica (non si usano gli asset in più), al meglio si sposta in fuori. Suo esempio: solo
  azioni max Sharpe **0,59**, multi-asset (azioni + obbligazioni) **0,74**.
- **Critica di Roll**: il **portafoglio di mercato vero non è osservabile**; ogni frontiera è costruita su un
  sottoinsieme scelto. Quindi "il mercato" nel CAPM è sempre una **proxy**, e i beta stimati ereditano quella scelta.
- **Stato**: `05` ha CAPM e i suoi limiti, **non** l'annidamento né Roll. **Rilevanza**: reference (utile a capire perché
  "battere il mercato" dipende da quale mercato).

### 🔧 Il test di perturbazione dei parametri (il pezzo che conta)
- **Criterio generale**, detto bene: *"se hai imparato **struttura**, perturbando leggermente gli input del modello devi
  osservare solo un lieve degrado; se le uscite cambiano moltissimo, hai adattato il rumore."*
- **Dimostrazione su MVO**: iniettando **0,2%** di rumore nei parametri, il peso di un titolo passa dal **60% al 37%**,
  un altro da **0 al 15%**. Le allocazioni "ottime" non sono informazione, sono rumore riorganizzato.
- **Conferma fuori campione**: tangenza stimata su 6 mesi con Sharpe **3,94** → fuori campione **0,83**, contro **1,09**
  del mercato; beta 1,5 e alpha con **p = 0,91** (nessun alpha). Overfitting da manuale.
- **Stato nel repo**: `04` §2 ha già *"instabilità parametrica = NO-GO"* per i parametri di una strategia. **Manca** la
  versione quantitativa e generale: perturbare gli **input** (non solo i parametri della regola) e **misurare** lo
  spostamento delle uscite, con una soglia dichiarata. → **buco 33**. **Rilevanza**: **applicabile ora** (vale per pesi,
  soglie, matrici di transizione, qualunque stima).

### Black-Litterman
- **Idea**: invece di partire dai rendimenti storici, si parte dall'**equilibrio implicito** — si assume che gli
  investitori nel complesso tengano il portafoglio di mercato (pesi per capitalizzazione) e si **inverte**
  l'ottimizzazione usando covarianza e coefficiente di avversione al rischio per ricavare i rendimenti attesi impliciti
  $\pi$. Poi si esprimono **viste soggettive**: $P$ (su quali asset), $Q$ (quanto), $\Omega$ (con quanta **fiducia**),
  più uno scalare $\tau$. Con fiducia nulla si torna esattamente all'equilibrio.
- **Perché è più stabile**: l'ancora non è la stima peggiore che abbiamo (i rendimenti storici) ma l'equilibrio di
  mercato; e la matrice di **covarianza è più stabile** del vettore dei rendimenti attesi. Misurato: perturbando lo
  spazio dei parametri dello **0,5%**, i pesi MVO si spostano del **17%**, quelli Black-Litterman dello **0,5%**.
- **Assunzioni/limiti**: che i pesi di mercato siano davvero il portafoglio ottimo dell'insieme; che si sappia esprimere
  la **fiducia** nelle proprie viste (parametro soggettivo, quindi anche manipolabile); resta necessaria la covarianza
  stimata.
- **Stato**: assente (nessun ottimizzatore nel repo). **Rilevanza**: futuro; **reference** subito come *forma* corretta di
  combinare prior e giudizio.

### ⚠️ Conflitto da mappare: il qualitativo dentro un modello quantitativo
- `04` §9 stabilisce che **il qualitativo genera ipotesi e non valida mai** (conflitto già risolto per domini contro la
  fonte del pre-mortem). Black-Litterman è il caso in cui una **vista soggettiva entra dentro il modello** con un peso
  esplicito.
- **Non è una contraddizione, se si tiene la condizione**: in BL la vista è (1) **dichiarata prima**, (2) **quantificata**
  con una fiducia esplicita, (3) **ancorata** a un prior che non dipende dalla vista, (4) verificabile a posteriori
  confrontando la vista con il realizzato. È l'opposto del ragionamento qualitativo che **scavalca** un verdetto: qui il
  giudizio è un input misurato, non un permesso.
- **Traduzione operativa per noi**: se un giorno un giudizio qualitativo dovesse entrare in una decisione di
  allocazione, deve avere la forma di BL — vista dichiarata prima, con una fiducia numerica, su un'ancora indipendente —
  e non la forma "ci credo, quindi lo attivo".

### Il resto (già catalogato altrove)
- Diversificare o concentrare: la concentrazione paga **solo se si è attivi e si ha ragione**; altrimenti si mangia il
  volatility drag e si esce prima del lungo periodo (C5). *"In selezione e concentrazione, probabilmente non sei bravo."*
- **Non risultare** (*resulting*): l'esito non giudica la qualità della decisione (B23, C9).
- *"Non esiste una distribuzione dei rendimenti: è un processo variabile nel tempo, non un istogramma"* — già in A6, B15,
  D1.

---

## E5 — Analyzing Stock Returns with Principal Component Analysis in Python

`oKJ5Rb3PI-o` · #157 · 29 min · parole n.d. — video tecnico; `05` ha già la PCA, qui contano le **aggiunte**

### Meccanica (reference)
- Due strade equivalenti: **SVD della matrice dei dati** ($X=U\Sigma V^\top$) o **decomposizione agli autovalori della
  matrice di covarianza** ($S=V\Lambda V^\top$). Relazione: $\lambda_i=\sigma_i^2/(n-1)$, e gli autovettori coincidono con
  i vettori singolari destri. Obiettivo comune: **diagonalizzare** la matrice di covarianza, cioè ottenere componenti che
  portano informazione **non ridondante**.
- **Analogia delle telecamere**: dieci telecamere con inquadrature sovrapposte → si combinano le sovrapposizioni e si
  guarda solo l'informazione unica; quella puntata sul frigorifero si butta.

### Perché la collinearità fa male (catena esplicita)
Coefficienti **instabili** (quale dei due titoli correlati "spiega" la risposta?) → interpretazione impossibile → modello
più complesso del necessario → **sovradattamento del rumore**. Vale per regressioni e per reti neurali. Misura citata:
**VIF** (già in A14, assente nel repo).

### 🔧 PCA mobile: la struttura fattoriale **non è stabile**
- Interpretazione dei carichi nel suo esempio (Apple, Amazon, GM, Microsoft): **PC1 = mercato** (~55%, carichi tutti
  dello stesso segno), **PC2 = settore** (i tre tech insieme, GM opposto; cumulata ~82%), **PC3 = idiosincratico**
  (cumulata > 90%).
- **Il test che conta**: rifacendo la PCA su **finestra mobile di 60 giorni**, la varianza spiegata da PC1 passa da
  **oltre il 60% a sotto il 50%** e poi risale, mentre la componente idiosincratica **cresce** fino quasi a superare il
  settore. *"Anche i carichi cambiano, ed è più difficile da visualizzare."*
- **Lettura**: la decomposizione in fattori è **una fotografia**, non una struttura permanente; chi ci costruisce sopra
  (neutralizzazione fattoriale, pesi, gate di regime) deve monitorarne la stabilità, non assumerla. È la stessa lezione
  della non-stazionarietà applicata alla matrice di covarianza (B14, E1).
- **Uso possibile per noi**: sui gruppi di strumenti del playground trend (FX, crypto, metalli, bond, energia…) la
  domanda "i gruppi si muovono ancora insieme come quando li ho definiti?" è esattamente una PCA mobile sui rendimenti di
  gruppo. Registrato come strumento, **non** come proposta.
- **Stato**: `05` documenta la PCA come decomposizione del rischio; **nessun controllo di stabilità** dei carichi o della
  varianza spiegata. → **buco 34**. **Rilevanza**: futuro (multi-asset), reference.

---

## E6 — Why is Portfolio Rebalancing Important?

`ztyh4L6rSR8` · #220 · 18 min — il video che il blocco C rimandava (buco 18)

### L'esperimento
- Portafoglio 50/50 Amazon + Apple dal 2020, due versioni: **ribilanciato** (pesi riportati a 50/50) e **acquisto unico**
  lasciato correre. Dopo ~2 anni i pesi dell'acquisto unico sono **40% Amazon / 60% Apple**.
- **La tesi**: la distanza fra le due curve non è (principalmente) una questione di rendimento — *"queste due linee si
  somigliano"* — è che **il profilo di rischio del portafoglio è cambiato senza che tu lo decidessi**. Con due soli
  asset in due anni la deriva è del 10%; con 30 asset e 30 anni *"è tutto sottosopra"*.
- **Raccomandazione**: mantenere i pesi obiettivo, per esempio con cadenza **mensile**.

### Che cosa aggiunge al repo, e che cosa resta fuori
- **Copre la metà "rischio" del buco 18**: senza ribilanciare, l'esposizione deriva verso ciò che è salito. La metà
  "crescita" — il **rendimento da diversificazione** a pesi costanti (C6) — **non è nel video**: qui il ribilanciamento è
  solo manutenzione del profilo di rischio. Le due giustificazioni sono complementari e vanno scritte insieme.
- ⚠️ **Assente nel video, ma necessario per una regola vera**:
  - **cadenza vs banda**: ribilanciare a calendario (mensile, annuale) oppure quando un peso esce da una **banda**
    (es. ±5 punti assoluti o ±25% relativo). La banda riduce il numero di operazioni;
  - **costi e fiscalità**: ribilanciare **vendendo** costa commissioni e, per un residente italiano, realizza
    plusvalenze tassate al **26%** (`08` §Fiscalità). In **fase di accumulo** la forma efficiente è ribilanciare con i
    **versamenti nuovi** (si compra la gamba sotto peso), non vendendo quella sopra peso;
  - **quanto spesso è troppo**: ribilanciare di continuo insegue il rumore e, con asset a momentum, taglia i vincitori.
- **Per il PAC dell'utente**: in **fase 1** il portafoglio è **un solo ETF azionario** ([[project_pac_inputs_2026_08_04]]:
  100% azionario, nessun ribilancio) → il problema **non esiste oggi**. Diventa vincolante quando il glide-path
  introduce la gamba difensiva: lì serve una **regola dichiarata prima** (banda o cadenza) e la preferenza per il
  ribilanciamento via versamenti.
- **Stato**: `08` documenta il glide-path ma **non** una regola di ribilanciamento; `05` non menziona il ribilanciamento
  (verificato). → **buco 18 confermato e specificato**.
- **Rilevanza**: **applicabile ora** per il pilastro investing (scrivere la regola prima che serva), futuro per il
  trading multi-gamba.

---

## E7 — How to Calculate Portfolio Alpha & Beta (Python + Interactive Brokers)

`A7zJARrdo3U` · #28 · 14 min — video operativo; la parte di codice è legata a Interactive Brokers (fuori perimetro),
la **procedura** no

### Lo strumento
- Si prendono i **rendimenti del portafoglio** (rispettando lato e size di ogni posizione), si prende un **proxy di
  mercato** (SPY) e si fa una **regressione CAPM mobile a 63 giorni** (un trimestre), producendo:
  **beta mobile**, **alpha mobile annualizzato**, e le metriche del portafoglio contro il benchmark nel tempo
  (max drawdown, CAGR, Sharpe, Sortino).
- **A cosa risponde**: *"i miei rendimenti vengono dall'esposizione al mercato o da altro?"* — e soprattutto **come
  cambia nel tempo**, che è la domanda che una stima unica non può porre.

### La lettura corretta (e il limite che il video tratta a occhio)
- Nel suo esempio l'alpha annualizzato oscilla fra **−50% e +50%** e il beta fra **0,5 e 1**. Conclude: *"non riesco a
  immaginare che sia statisticamente diverso da zero"* — ed è giusto, ma **non lo misura**.
- ⚠️ **Aggiunta necessaria**: un alpha stimato su 63 osservazioni ha un errore standard enorme; l'oscillazione ±50%
  **è** il rumore della stima, non un segnale. Se si monitora l'alpha mobile bisogna riportare **intervallo di
  confidenza** (o almeno l'errore standard della regressione), altrimenti si legge rumore come informazione — esattamente
  il difetto che il repo evita con `bca_bootstrap_ci` sulle metriche (`04` §6, "decidi sul lower bound").
- **Osservazione utile che fa**: in crisi il beta **aumenta** (le correlazioni salgono), quindi il beta stimato in
  periodo calmo **sottostima** l'esposizione proprio quando conta.

### Stato e rilevanza
- **Stato**: `core/quant_metrics.py` ha `benchmark_metrics` (alpha, beta, IR, tracking error, R²) ma **su tutto il
  campione**; nessuna versione mobile, nessun intervallo. → conferma **buco 30**, con la specifica: *mobile + intervallo
  di confidenza*.
- **Rilevanza**: **applicabile ora** quando esisterà più di una gamba (oggi: PAC a un solo ETF, beta ≈ 1 per
  costruzione); utile anche per verificare che una strategia di trading non sia beta travestito (B9).

---

## E8 — Live Capital Management: My 2025 Crisis Alpha

`yRDs4atfRB0` · #22 · 24 min — **autoanalisi della propria performance** ("films"): numeri **autodichiarati**, un solo
anno, nessuna verifica possibile → per il nostro filtro **non fanno stato**

### I numeri dichiarati (registrati, non usati)
CAGR **44%** contro **16%** dell'S&P 500; volatility drag **~5%** contro 1,9%; **max drawdown 30%**. Era **corto
volatilità** entrando nel crollo dei dazi, **senza** gamba di convexity.

### Ciò che vale la pena tenere
- **Autocritica esplicita e utile**: *"non c'era alcun motivo per subire un drawdown del 30%"* — il rischio che lo ha
  colpito è **quello che aveva scelto di non coprire**, pur sapendo dove e come avrebbe coperto. È il caso di scuola del
  pre-mortem non applicato (`04` §9): conoscere la copertura non serve se non è in posizione **prima**.
- **Monetizzazione del drawdown senza fare timing**: la tesi è che non serve chiamare il minimo, serve distinguere
  **crollo con recupero rapido** da **ciclo ribassista persistente**, e usare come innesco il **collasso della
  volatilità** (previsione GARCH in calo) o il profit-take sulla convexity. Nel 2025 dice di aver avuto **circa un mese**
  di finestra utile.
  - ⚠️ Tutto ciò è **descritto, non misurato**: quanto duri la finestra in altri crolli, e come si distinguano i due casi
    **in tempo reale**, non è mostrato. Registrato come **ipotesi**, non come regola.
- 🔎 **Conferma di un punto nostro**: dice che *"se allochi durante il drawdown, il **timing si presenta come alpha**"* in
  una regressione contro il mercato. È esattamente l'artefatto segnalato in **B10**: un payoff dipendente dal momento
  (o convesso) letto da un modello **lineare** produce un'intercetta che non è abilità di selezione. Qui lo dice la
  fonte stessa — utile averlo dalla sua voce.
- **Dipendenza dal percorso delle opzioni**: entrare oggi o fra una settimana sulla stessa put dà convexity simile nel
  crollo ma **decadimento molto diverso** sull'equity fino a quel momento. Conferma il caveat di C11 sullo strike e sul
  costo di mantenimento.

### Stato e rilevanza
- **Stato**: nessuno strumento nuovo. **Rilevanza**: reference; il valore è metodologico (pre-mortem applicato,
  monetizzazione come parte dichiarata del piano di copertura, timing che si traveste da alpha).

---

## Sintesi del blocco

| strumento | video | stato | rilevanza | destinazione proposta |
|---|---|---|---|---|
| lettura dei carichi PCA (mercato / settore / idiosincratico) e varianza non spiegata per titolo | E1 | doc parziale (05) | futuro | 05 |
| beta per settore e asimmetria del recupero | E1 | doc (05) | reference | — |
| **beta e alpha mobili**, con intervallo di confidenza | E1, E7 | `benchmark_metrics` è statico | applicabile ora (multi-gamba) | core, 05 |
| **Sharpe che si sommano in quadratura** per flussi ortogonali | E2 | assente | applicabile ora | 05 |
| ricetta "SPY + gamba trend con leva": fonte primaria dei numeri già segnati in `08` | E2 | doc con cautela (08) | reference | 08 |
| **MVO come massimizzatore dell'errore**; rimedi (shrinkage, resampling, min-varianza, 1/N) | E3 | assente | applicabile ora (come criterio: non ottimizzare) | 05 |
| **test di perturbazione dei parametri** con misura dello spostamento | E4 | regola qualitativa in 04 §2 | applicabile ora | 04 |
| **Black-Litterman**: prior di equilibrio + viste con fiducia esplicita | E4 | assente | futuro; reference subito | 05 + mappa (04 §9) |
| annidamento delle frontiere, critica di Roll | E4 | assente | reference | 05 |
| PCA: SVD vs autovalori; collinearità → pesi instabili | E5 | doc parziale | reference | 05 |
| **PCA mobile**: la struttura fattoriale non è stabile | E5 | assente | futuro | 05 |
| **ribilanciamento**: deriva dei pesi = deriva del profilo di rischio | E6 | assente | applicabile ora (pilastro investing) | 08, 05 |
| cadenza vs banda, costi e fiscalità, ribilanciare con i versamenti | E6 (aggiunta) | assente | applicabile ora | 08 |
| monetizzazione del drawdown e finestra di monetizzazione | E8 | doc parziale (05 tail) | reference | 05 |
| il **timing si presenta come alpha** in un modello lineare | E8, B10 | assente | applicabile ora | 05 |

## Buchi emersi nel repo

> Numerazione in continuità con A (1–4), B (5–13), C (14–19), D (20–29).

30. **`benchmark_metrics` è statico**: alpha e beta stimati una volta su tutto il campione, senza versione **mobile** né
    **intervallo di confidenza**. Un alpha su finestra corta è rumore se non se ne misura l'incertezza. Fonti: E1, E7.
31. **Manca il criterio per decidere se una gamba nuova vale**: per flussi ortogonali $SR_{tot}=\sqrt{\sum SR_i^2}$ dice
    quanto serve che una gamba sia buona perché sposti l'insieme. Fonte: E2.
32. **Nessun rimedio all'errore di stima in ottimizzazione** (shrinkage, resampling, minima varianza, 1/N come
    benchmark) — e nessuna regola che dica che il default è **pesi dichiarati prima**. Fonte: E3.
33. **Il test di instabilità parametrica non è quantitativo né esteso agli input**: perturbare gli input di X% e misurare
    lo spostamento delle uscite, con soglia dichiarata. Fonte: E4.
34. **Nessun controllo di stabilità della struttura fattoriale** (PCA mobile su varianza spiegata e carichi). Fonte: E5.
35. **Nessuna regola di ribilanciamento** (né cadenza né banda) per quando il glide-path introdurrà la gamba difensiva,
    e nessuna nota sul ribilanciamento via **versamenti nuovi** per non realizzare plusvalenze al 26%. Fonte: E6
    (specifica il buco 18).

## Conflitti per la mappa dei modelli

- **"Il qualitativo genera ipotesi e non valida mai"** (`04` §9) **vs** **Black-Litterman**, dove una vista soggettiva
  entra nel modello con un peso. **Non è un conflitto** se si tiene la condizione: vista **dichiarata prima**,
  **quantificata** con una fiducia esplicita, **ancorata** a un prior indipendente (l'equilibrio di mercato) e
  **verificabile** a posteriori. È l'opposto del giudizio che scavalca un verdetto.
- **"Diversificare è protezione dall'ignoranza; concentra se sai quello che fai"** (E4, citando Buffett) **vs**
  **pilastro passivo diversificato** (`08`). Condizione: la concentrazione paga solo con capacità di selezione
  **dimostrata** e sopravvivenza al drag; per un PAC in accumulo senza edge di selezione dimostrato, la diversificazione
  resta la scelta. Nessuna riapertura.
