# Blocco D — Serie storiche, regimi, filtri, processi di punto (11 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Contesto del repo per questo blocco** (verificato il 2026-09-15, prima della lettura):
- **Codice**: nessun file in `core/`, `analysis/`, `strategies/`, `backtesters/` usa GARCH/ARCH, HMM (`hmmlearn`,
  `GaussianHMM`), filtro di Kalman, processi di Hawkes o di Poisson, test ADF o `statsmodels.tsa` (ricerca per nome, nessun
  risultato). Tutti **assenti** come implementazione.
- **`core/regime.py`**: classificatore **deterministico** a 6 stati (direzione da Wilder DMI/ADX con soglia 25; volatilità
  "Volatile" se ATR14 > media a 50 dell'ATR, etichetta **relativa** — vedi blocco B, B2 e buco 6).
- **`03_regimi_macro`**: catena di Markov **osservabile** a 3 stati (Bull/Bear/Sideways da rendimento mobile a 20 giorni con
  soglia ±2%), matrice di transizione per conteggio (MLE), distribuzione stazionaria, previsione a $n$ passi con
  Chapman-Kolmogorov, walk-forward senza look-ahead. **Documentata, non implementata.**
- **Blueprint `markov_regime_skill.md`**: **idea non adottata**. Estensione HMM con `GaussianHMM` (covarianza diagonale,
  Baum-Welch, avvertenza sui **massimi locali** → più inizializzazioni). Tre fix "Markov 2.0": FIX 1 conteggio delle
  transizioni su finestre **non sovrapposte** (unica parte assorbita, in `04` §7); FIX 2 verifica delle etichette su periodi
  noti; FIX 3 modalità *filtro* (gate di una strategia esistente) vs *standalone*.
- **`05_portfolio_rischio` §Tail risk**: GARCH(1,1) citato per la coda condizionata al regime (da #31, già distillato).
- **Radici unitarie / ADF**: solo la riga 174 di `agents/quant_reviewer.md`, con l'uso improprio segnato in B16 (buco 9).
- **Filtro di Kalman, processi di Hawkes e di Poisson**: nessuna menzione nei `principles.md`.

---

## D1 — Time Series Analysis for Quant Finance

`JwqjuUnR8OY` · #129 · 44 min · 7.091 parole — **il video più denso del blocco**

### Che cosa è una serie storica
- Osservazioni a intervalli **regolari** (chiusure giornaliere) o **irregolari** (strumento illiquido che scambia di rado).
- ⚠️ **Interpolazione lineare a tratti**: il grafico "unisce i puntini" e **nasconde tutto ciò che accade fra due
  osservazioni**. Vale anche per le barre: fra due chiusure non si sa il percorso. È la stessa lezione del fill
  ottenibile e dei "6 milioni di ingressi dentro una barra" (B23): **l'OHLC non definisce l'esecuzione**.
- **Stato**: lezione in memoria ([[feedback_fill_ottenibile]]), non scritta in `04`. **Rilevanza**: in uso.

### Decomposizione: tendenza, stagionalità, shock
- Una serie si scompone in **tendenza** (direzione di lungo periodo), **stagionalità** (schema a intervalli fissi) e
  **shock/residui** (fluttuazioni non spiegate, con una distribuzione **assunta**).
- **Condizione d'uso**: informativa solo se le componenti sono **stabili**; un cambio strutturale (nuovo prodotto,
  infortunio, cambio di regime) le azzera. Su dati intraday di prezzo *"non si vedrà alcuna stabilità"*.
- **Stato**: assente come voce. **Rilevanza**: reference.

### Filtraggio, lisciamento, previsione — la distinzione che conta
| compito | informazione usata | domanda |
|---|---|---|
| **filtraggio** (filtering) | passato + presente | qual è lo **stato attuale** senza rumore? |
| **lisciamento** (smoothing) | passato + **futuro** (percorso globale) | qual **era** lo stato in un istante passato? |
| **previsione** (forecasting) | passato + presente | qual è l'**aspettativa** dello stato futuro? |
- Una media mobile su un grafico è **filtraggio**: *"non dice nulla sullo stato futuro"*. Il lisciamento esponenziale che
  usa anche i punti successivi è **lisciamento**: richiede la conoscenza del percorso globale.
- ⚠️ **Conseguenza diretta per noi**: qualunque quantità calcolata con una **finestra centrata**, o ri-stimata su tutto lo
  storico e poi applicata all'indietro, è **lisciamento travestito da filtraggio** = look-ahead. È esattamente il difetto
  già documentato per la regime timeline del repo (label sul close dello stesso giorno, usabile solo con lag 1:
  [[reference_regime_timeline_lookahead]]), ma qui diventa un **criterio generale** da applicare a ogni indicatore,
  etichetta di regime o stima di parametro usata in backtest.
- **Stato**: il caso specifico è doc (`04` §1, `03`); la distinzione generale **non è scritta** → **buco 20**.
- **Rilevanza**: **applicabile ora** (controllo da fare su ogni feature di qualunque pre-registrazione).

### "Non esistono previsioni, esistono aspettative"
- Un modello produce l'**aspettativa** condizionata a *status quo*; il machine learning è un'**aspettativa condizionata
  non lineare** (B18). Senza sfera di cristallo non c'è previsione: è la stessa tesi di B17 e B15.
- **Gerarchia delle assunzioni**: alcune sono miti (non-arbitraggio), altre violente ma **utili lo stesso** (volatilità
  costante in Black-Scholes: falsa, ma permette di estrarre la **volatilità implicita**, cioè il prezzo che il mercato
  dà all'incertezza). Criterio utile: non "l'assunzione è vera?" ma "cosa mi permette di misurare, e in che direzione
  sbaglia?" (checklist di A3/B14).
- **Stato**: doc. **Rilevanza**: in uso.

### Evento di utili: la previsione giusta viene dal mercato delle opzioni
- Una previsione da serie storica su un salto da utili è **piatta e violentemente sbagliata**. Meglio modellare **due
  stati del mondo** usando lo **straddle**: l'ampiezza del movimento che il mercato sta prezzando. ⚠️ Non dà la
  **direzione**, solo la dimensione attesa del salto.
- **Domanda che risponde**: quanto si aspetta il mercato che si muova questo strumento su questo evento — utile come
  **filtro di event-risk** (allargare gli stop attesi, non tradare mean-reversion in quella finestra), coerente con `03`
  §6 (canali di trasmissione come calendario di rischio, non come segnale).
- **Stato**: **assente** (opzioni fuori perimetro; gruppo 2). **Rilevanza**: futuro.

### Rotture strutturali e dati alternativi
- Esempi: la sua panca da 350 lb che crolla a 45 lb dopo uno strappo al pettorale; i CDS nel 2008. In entrambi i casi il
  modello di serie storica **non poteva saperlo**, ma **qualcuno aveva l'informazione prima** (il medico; chi controllò i
  tassi di insolvenza reali dei mutui).
- **Strumento**: **dati alternativi** = informazione esterna alla serie che anticipa il salto (foto dei parcheggi, tassi di
  insolvenza, sentiment). È la forma onesta di "edge informativo": non insider, ma dati che il prezzo non ha ancora
  incorporato.
- **Per noi**: è la categoria a cui appartengono i **segnali mentore** ([[project_mentor_signals_edge_2026_07_08]]) — un
  flusso informativo esterno al prezzo. Registrato come inquadramento, non come nuova ipotesi.
- **Stato**: implicito. **Rilevanza**: reference.

### Market making con modello sbagliato ma corretto in media
- Dado a probabilità fisse: si quota attorno a 3,5 e si incassa lo spread (arrivi alla Poisson). Se il "peso del dado"
  **cambia nel tempo**, basta una **media mobile** (filtraggio) per inseguire il livello: il P&L resta positivo perché la
  stima è **corretta in media**, pur essendo sempre sbagliata puntualmente.
- **Lezione**: in market making non serve prevedere, serve un livello non sistematicamente distorto più uno spread che
  copra l'errore. Collega la formula vantaggio × P(esecuzione) di B20.
- **Stato**: reference (non facciamo market making). **Rilevanza**: reference.

### Prezzare uno strumento illiquido con proxy liquidi (filtro di Kalman)
- Strumento che scambia a intervalli irregolari: si stima il suo valore fra un trade e l'altro usando strumenti liquidi
  correlati come **proxy**, con un **filtro di Kalman** (stato latente osservato con rumore attraverso più misure).
- **Assunzioni**: relazione lineare fra proxy e stato, rumore gaussiano, parametri stabili nella finestra.
- **Stato**: **assente** in tutto il repo (verificato: nessun Kalman nel codice). **Rilevanza**: futuro (D8, D9 lo
  approfondiscono).

### Claim ripetuto da mappare
- *"Non esistono test affidabili di stazionarietà"*: già registrato in B16 come **conflitto per domini** (radice unitaria
  in senso tecnico vs non-stazionarietà strutturale). Qui aggiunge la parte corretta e utile: **i prezzi hanno radice
  unitaria, quindi si lavora sui rendimenti** — che è il contenuto di D2.

---

## D2 — Time Series Analysis: Why are Unit Roots Important?

`lCwg599tCm4` · #222 · 13 min · 2.013 parole

### L'esperimento (il più istruttivo del canale)
- Dati Apple dal 2018, due regressioni OLS **entrambe oneste** (il target è `shift(-1)`, cioè il giorno dopo, spiegato
  con il dato di oggi):

  | regressione | $R^2$ |
  |---|---|
  | chiusura di domani su chiusura di oggi | **0,998** |
  | rendimento di domani su rendimento di oggi | **0,015** |

- **Interpretazione**: il primo $R^2$ non misura alcuna capacità predittiva. Due serie con **radice unitaria** (quasi
  passeggiate aleatorie) producono **regressioni spurie**: il modello "spiega" soltanto che il prezzo di domani è vicino a
  quello di oggi. Il secondo numero è la capacità esplicativa vera, circa 1,5%.
- **Rimedio**: **differenziare** (prezzi → rendimenti) finché la serie è ragionevolmente stazionaria, e modellare quella.
- **Tell operativo**: un $R^2$ altissimo su una serie di **livelli** (prezzi, equity, capitale) è un segnale d'allarme, non
  un risultato. Vale anche per le correlazioni fra livelli.

### Stato e rilevanza
- **Stato**: `core/quant_metrics.py` regredisce **rendimenti su rendimenti** (`benchmark_metrics`), quindi la pratica
  corrente è corretta, ma **nulla nel repo lo scrive**; e la riga 174 di `agents/quant_reviewer.md` usa l'ADF per una
  domanda a cui non risponde (buco 9). Manca il complemento: per lavorare **sui livelli** (spread fra due strumenti,
  pairs trading) servirebbe la **cointegrazione**, cioè residuo stazionario — mai nominata nel repo → **buco 21**.
- **Rilevanza**: **applicabile ora** come regola di lettura; futuro per la cointegrazione.
- ⚠️ Il video ripete *"non esistono test affidabili di stazionarietà"* ma **usa** correttamente la radice unitaria:
  conferma che il conflitto di B16 va letto per domini, non come rifiuto dei test.

---

## D3 — Master Volatility with ARCH & GARCH Models

`iImtlBRcczA` · #126 · 48 min · 7.339 parole — **il video più ricco del blocco**

### Volatilità realizzata vs implicita
- **Realizzata (storica)**: deviazione dei rendimenti da una media di riferimento, calcolata **all'indietro** su una
  finestra (es. 30 giorni mobili). ⚠️ **Dipende dalla finestra**: finestre corte danno una misura più nervosa perché anche
  il riferimento si muove più in fretta (stesso compromesso di B16).
- **Implicita**: si ricava **invertendo Black-Scholes** dai prezzi di mercato delle opzioni; è la volatilità
  **prospettica** che i trader stanno prezzando, per una data scadenza e moneyness.
- **Premio per la varianza, misurato**: regredendo la volatilità realizzata **futura** su quella implicita la pendenza è
  **< 1** → l'implicita **sovrastima** sistematicamente la realizzata; separando i regimi l'effetto è **più forte in alta
  volatilità** (pendenza ancora più bassa). Aggiunge un dettaglio a `05` §VRP (da #41): il premio **si concentra quando la
  paura è alta**.
- **Stato**: doc (`05` §VRP). **Rilevanza**: reference (opzioni fuori perimetro).

### Fatti stilizzati che un modello di volatilità deve catturare
1. **Curtosi in eccesso** (distribuzione leptocurtica): code più spesse della normale su **entrambi** i lati → un VaR
   parametrico normale sottostima il rischio (nel suo esempio ~20% di differenza contro il VaR empirico).
2. **Raggruppamento della volatilità**: periodi agitati seguono periodi agitati → persistenza e autocorrelazione **nella
   varianza**, non nei rendimenti.
3. **Ritorno alla media** della volatilità: i livelli estremi non persistono (il VIX non sale "in su e a destra").
4. **Effetto leva**: la volatilità sale **di più** dopo rendimenti negativi che dopo positivi di pari ampiezza.
5. **Memoria lunga**: dipendenza a ritardi molto lontani; motiva i modelli a volatilità *rough* (moto browniano
   frazionario, processi di Volterra) — evidenza **contestata**, lo dice lui stesso.
- **Collegamento ad A8/B15**: gli "eventi a 6, 10, 30 sigma" citati dai media sono quasi sempre il segno di un
  **riferimento mal costruito**, non di un evento impossibile.
- **Stato**: 1 e 3 doc (`05` §Tail risk, da #31); **2, 4, 5 assenti**. **Rilevanza**: applicabile ora.

### ARCH e GARCH
- **ARCH(q)** (Engle, 1982): $y_t=\mu+\varepsilon_t$ con $\varepsilon_t=\sigma_t z_t$, $z_t$ i.i.d. a media 0 e varianza 1;
  $\sigma_t^2=\alpha_0+\sum_{i=1}^{q}\alpha_i\varepsilon_{t-i}^2$. "Autoregressivo" = usa i propri valori passati;
  "condizionatamente eteroschedastico" = la varianza **non è costante** e dipende dall'informazione passata.
- **GARCH(p,q)** (Bollerslev, 1986): aggiunge le varianze condizionate ritardate,
  $\sigma_t^2=\alpha_0+\sum_i\alpha_i\varepsilon_{t-i}^2+\sum_j\beta_j\sigma_{t-j}^2$.
  **Risultato chiave**: un ARCH di ordine **infinito** equivale a un **GARCH(1,1)** → stessa dinamica con due parametri
  invece che infiniti. È il motivo per cui GARCH(1,1) è lo standard pratico.
- **Proprietà**: la distribuzione **non condizionata** è una **mescolanza di gaussiane a varianza variabile**, quindi
  leptocurtica **per costruzione** — è il meccanismo "code grasse da mescolanza di regimi" di B16, qui derivato dal modello.
- **Limiti**: innovazioni i.i.d. (di solito normali: per gli estremi servono code pesanti, es. t di Student); il GARCH base
  **non** cattura l'effetto leva (servono varianti asimmetriche, non nominate); parametri stimati e instabili (B13, B22).

### Le misure di performance dichiarate
| modello | RMSE | $R^2$ |
|---|---|---|
| media mobile esponenziale | ~42% | 5,12% |
| ARCH(1) | ~25% | ~5% |
| GARCH(1,1) | comparabile ad ARCH(1) | ~8% |

- ⚠️ Confronto **non ricalcolabile** (nessun dato, ricerca a griglia su entrambi, un solo titolo); lui stesso lo definisce
  *"lontano dall'essere una gara perfetta"*.
- **Dato utile**: su **titolo singolo giornaliero** un $R^2$ sotto il 10% è atteso; costruendo la volatilità realizzata da
  **dati intragiornalieri** (es. 5 minuti) la varianza spiegata sale al **40–60%**, perché la misura intraday è una
  **proxy molto migliore** del processo latente. Lezione generale: prima di cambiare modello, **migliorare la misura della
  variabile obiettivo**.

### Il backtest del VaR per eccedenze — lo strumento che mancava
- **Procedura**: fissata una soglia al livello $\alpha$ (es. 5%), si conta la frazione di giorni in cui la perdita la
  **supera**; se il modello è corretto le eccedenze devono essere circa $\alpha$.
- **Risultati del video**: VaR parametrico a varianza costante → **40%** di eccedenze contro il 5% atteso (modello
  inservibile); VaR con GARCH → **9,74%**.
- ⚠️ **Lettura onesta**: 9,74% è quasi **il doppio** del 5% nominale, quindi il GARCH con innovazioni normali è ancora mal
  specificato. Il video lo presenta come successo: il confronto corretto è "da inservibile a insufficiente".
- **Per noi**: è il **test di taratura** segnalato come mancante in B14, e si applica **senza opzioni e senza GARCH** —
  qualunque soglia dichiarata come "il x% peggiore" (soglie di ritiro §8bis, limite di drawdown giornaliero del risk gate,
  percentili del Monte Carlo) si verifica contando le eccedenze realizzate contro quelle attese. **Stato: assente** →
  **buco 22**. **Rilevanza**: **applicabile ora**.

### Dove un modello di volatilità servirebbe a noi
- **Etichetta di regime assoluta invece che relativa**: oggi `classify_volatility` dice "Volatile" se ATR14 supera la
  propria media a 50 — etichetta **relativa** che in un periodo lungo ad alta volatilità chiama "Quiet" metà dei giorni
  (buco 6). Una varianza condizionata stimata darebbe un **livello** e una **previsione**, non un confronto con la propria
  media mobile.
- **Dimensionamento**: la frazione di Kelly e le soglie di rischio dipendono da $\sigma$ (C1, C5); con volatilità variabile
  nel tempo una size che ignora la volatilità prevista è sistematicamente sbagliata in entrambe le direzioni (il
  *vol targeting* è già citato nel reviewer come alternativa al fixed fractional).
- **Stato**: **assente** in tutto il repo (verificato). **Rilevanza**: **applicabile ora** → **buco 23**.

---

## D4 — Markov Chains for Quant Finance

`k8oQfd6M5sA` · #124 · 49 min · 7.499 parole

Il repo documenta già lo stesso modello (`03_regimi_macro` §1: 3 stati, matrice di transizione per conteggio,
distribuzione stazionaria, Chapman-Kolmogorov, walk-forward). Qui si registra **ciò che lì manca**.

### L'esempio che vale il video: transizioni impossibili come test di falsificazione
- **Caso**: portafoglio di prestiti con quattro stati (in regola, 30–59 giorni di ritardo, 60–89, 90+). Simulando ogni
  mese **estrazioni indipendenti** dalle distribuzioni marginali, al mese 1 compaiono prestiti a **90+ giorni** partendo da
  un portafoglio tutto in regola: **impossibile** (uno stato a 90 giorni richiede tre mesi).
- **Strumento generale**: se un modello genera **percorsi che non possono esistere**, è falsificato **senza bisogno di
  dati di test**. È un controllo gratuito e fortissimo, complementare ai gate statistici.
- **Per noi**: applicabile a qualunque simulatore o modello di stato — un backtest che produce sequenze impossibili (fill
  a prezzi mai scambiati, due posizioni sullo stesso simbolo quando il gate ne consente una, transizioni di regime che
  saltano stati intermedi) è sbagliato **prima** di qualunque misura di performance. Si aggancia al FIX 2 del blueprint
  (verificare la mappa degli stati su periodi noti) e al fill fantasma.
- **Stato**: **assente** come controllo scritto. **Rilevanza**: **applicabile ora** → **buco 24**.

### Struttura e proprietà (ciò che `03` non esplicita)
- **Dipendenza condizionata locale**: la catena vieta per costruzione le transizioni impossibili (zeri nella matrice).
- **Tre assunzioni dichiarate**: spazio degli stati **finito**; **omogeneità temporale** (le probabilità di transizione
  sono **costanti nel tempo**); **assenza di memoria** (conta solo lo stato attuale, non il percorso).
  - ⚠️ `03_regimi_macro` descrive la catena a 3 stati **senza nominare l'omogeneità temporale**, che è l'assunzione più
    fragile in finanza — lo dice lui stesso subito dopo aver mostrato la distribuzione che cambia nel tempo. Il
    walk-forward del nostro blueprint (ri-stimare `P` solo sul passato a ogni `t`) è una **risposta parziale**: rilassa
    l'omogeneità al prezzo di più rumore di stima.
  - ⚠️ L'assenza di memoria si compra con lo **spazio degli stati**: per ricordare "sono già stato in ritardo grave" serve
    aggiungere stati, e la complessità esplode (stesso avvertimento di B1).
- **Chapman-Kolmogorov**: la matrice a $n$ passi è $P^n$. Esempio: da "in regola" a "90+ giorni" in 12 mesi ≈ **18,26%**
  (illustrativo: dipende dalla sua matrice, non ricalcolabile).
- **Vettore di distribuzione degli stati**: converge alla stazionaria **indipendentemente dallo stato iniziale**; nel suo
  esempio la quota di prestiti a 90+ passa da 7% a 27% a 12 mesi a seconda della partenza, ma a orizzonte lungo converge a
  ~3,8% in entrambi i casi. **Lezione**: la distribuzione iniziale conta **nel breve**, la matrice conta **nel lungo**.

### Stima delle probabilità e sua incertezza
- La stima di massima verosimiglianza della probabilità di transizione è semplicemente la **proporzione di transizioni
  osservate** da uno stato all'altro. Proprietà: consistenza, normalità asintotica; ⚠️ **stime molto volatili con pochi
  dati**, come mostra lui stesso.
- **Ciò che manca ovunque (video e repo)**: l'**errore standard** di ogni cella,
  $\mathrm{SE}(\hat p)=\sqrt{\hat p(1-\hat p)/n_i}$ con $n_i$ transizioni osservate **dallo stato $i$**. Senza quello, una
  matrice stimata su pochi episodi di regime sembra precisa quanto una stimata su migliaia. → **buco 25**.
- **Assunzioni per la stima**, elencate dal video: proprietà di Markov, omogeneità temporale, ergodicità, dati
  sufficienti, **indipendenza fra le unità** (i singoli prestiti). Indica come più critiche l'omogeneità temporale e
  l'indipendenza fra unità (nelle crisi i prestiti falliscono **insieme**).
  - **Traduzione per noi**: contare transizioni di regime su **più strumenti** come se fossero campioni indipendenti
    sovrastima il numero effettivo di osservazioni — gli strumenti cambiano regime insieme. È lo stesso problema del
    `n_eff` e del block bootstrap (`04` §7, reviewer), applicato alla stima della matrice.
- **Stato**: `03` documenta la stima per conteggio; **né l'incertezza né l'indipendenza fra unità sono scritte**.
  **Rilevanza**: applicabile ora, se mai si implementasse il modello a regimi (oggi idea non adottata).

### Nota di completezza
- Il video **non** menziona il difetto delle **finestre sovrapposte** nell'etichettatura dei regimi (qui gli stati sono
  discreti e osservati, non calcolati da rendimenti mobili): il nostro FIX 1 in `04` §7 resta un'aggiunta del repo, non
  una lezione di questa fonte.
- Cita come sviluppi: stati assorbenti (default), irriducibilità, ricorrenza, classi di comunicazione, periodicità —
  materiale del blocco D successivo e del gruppo 2.

---

## D5 — Hidden Markov Models for Quant Finance

`Bru4Mkr601Q` · #122 · 56 min · 8.822 parole

### Variabile latente e proxy
- **Idea**: la distribuzione che genera i rendimenti cambia nel tempo perché è guidata da processi **latenti**
  (volatilità, tendenza, momentum) che **non si osservano**. Si può solo **approssimarli**.
- **Proxy della volatilità**: deviazione standard su **finestra mobile** (20, 60, 80, 150 giorni…) — ⚠️ *"quale finestra
  uso?"* è una domanda aperta e la scelta cambia il proxy (stesso compromesso di B16 e D3). Alternativa citata:
  **compressione con PCA** di molte misure di volatilità in un'unica feature aggregata.
- **Quantificazione dell'errore del modello normale**: su NVIDIA, ogni rendimento oltre 4 deviazioni standard
  richiederebbe in media **125,3 anni** per essere visto una volta, sotto l'ipotesi di normalità — e se ne osservano
  molti. È la stessa famiglia di numeri del "1 ogni 7.000 anni" già in `05` §Tail risk (da #31).
- **Stato**: doc (05). **Rilevanza**: in uso.

### Catena di Markov sui regimi di volatilità → distribuzioni condizionate
- Tre stati (bassa, media, alta volatilità) definiti con i **percentili 33 e 66** della volatilità storica; una gaussiana
  **per regime**. Risultato: la **mescolanza** delle tre gaussiane riproduce la curtosi in eccesso (**0,687**, cioè
  curtosi 3,687) → il meccanismo "code grasse da mescolanza di regimi" (B16, D3) è verificato sui dati.
- ⚠️ **Incoerenza interna della fonte**: qui usa **percentili mobili** per definire i regimi, esattamente la costruzione
  che **lui stesso** aveva mostrato instabile per costruzione in B2 (i terzili estremi si contaminano quando cambia il
  livello assoluto). Vale la stessa condizione: un'etichetta relativa non è un livello.
- **Onestà della fonte**: dice che 3,687 è *"un passo nella direzione giusta"*, non la soluzione — la curtosi empirica di
  NVIDIA è molto più alta. Tre stati e tre gaussiane restano **lontani dalla realtà**.
- **Esplosione dello spazio degli stati**: aggiungendo la tendenza si passa da 3 a **9** stati; ogni fattore latente
  moltiplica. È il costo della memoria esplicita (D4).

### Hidden Markov Model
- **Che cosa fa**: invece di **definire** i regimi, li **apprende dai dati**, comprimendo *tutti* i fattori latenti in un
  numero di stati **scelto da chi modella**. Stima con **forward-backward** e **Baum-Welch** (massima verosimiglianza).
- **Prezzo da pagare**: si perde l'**interpretabilità** — come le componenti principali, uno stato latente non "è" la
  volatilità; lo si interpreta a posteriori dalle statistiche della sua distribuzione condizionata (nel suo esempio:
  deviazioni standard 1,48 / 1,74 / **6,46** → il terzo stato cattura la volatilità alta).
- **Avvertenze che dà**: si può **sovradattare**; il numero di stati è una **scelta** (e il costo computazionale esplode);
  *"un modello più semplice può spiegare altrettanto restando interpretabile"*.
- ⚠️ **Il difetto che né il video né il nostro blueprint segnalano — e che è decisivo per un backtest**:
  forward-backward e Baum-Welch usano **tutto il campione**, passato **e futuro**, per inferire gli stati. Nel vocabolario
  di D1 è **lisciamento**, non filtraggio: la sequenza di stati "più probabile" a posteriori (e i parametri stessi)
  incorpora informazione non disponibile al momento della decisione. Usare quegli stati come segnale in backtest è
  **look-ahead garantito**, ed è la stessa forma del difetto già documentato per la regime timeline del repo. Per un uso
  onesto servono: parametri stimati **solo sul passato** (walk-forward) e probabilità di stato **filtrate** (passo in
  avanti soltanto), mai la decodifica su tutto il campione.
  - Il blueprint `markov_regime_skill.md` descrive `fit_hmm` con `.fit()` + `.predict()` su **tutta** la serie: come
    diagnostica storica va bene, **come segnale no**. → **buco 26**.
- **Stato**: HMM assente nel codice; blueprint non adottato. **Rilevanza**: **applicabile ora** come vincolo di metodo (se
  mai si implementasse), futuro come modello.

### Sintesi per noi
- La catena a stati **espliciti** resta preferibile alla HMM finché conta l'interpretabilità (e per noi conta: un gate di
  regime va spiegato, non solo misurato).
- Il valore vero del video non è l'HMM: è la **catena** latente → distribuzione condizionata → verosimiglianze migliori,
  cioè l'idea che le probabilità di coda vanno stimate **per regime** e non sull'intero campione (già in `05`, qui
  con la procedura).

---

## D6 — Markovian Modeling using First Step Analysis

`oo4Ish9TW7U` · #179 · 29 min · 3.807 parole — secondo video di una serie di tre su domande da colloquio

### Analisi del primo passo (first step analysis)
- **Domanda**: quanti lanci servono **in media** per vedere la prima serie di 3 teste?
- **Metodo**: si condiziona sul **primo passo** e si usa l'aspettativa totale (A7). Detto $H_k$ il numero di lanci per una
  serie di $k$ teste e $p$ la probabilità di testa:
  - $E[H_1]=p\cdot1+(1-p)(1+E[H_1])\;\Rightarrow\;E[H_1]=1/p$ (la geometrica di A10);
  - passo generale: $E[H_{k}]=\dfrac{1}{p}+\dfrac{E[H_{k-1}]}{p}$, da cui
    $$E[H_k]=\frac1p+\frac1{p^2}+\dots+\frac1{p^k}$$
- **Verifica**: con $p=1/2$ e $k=3$ → $2+4+8=\mathbf{14}$; la sua simulazione su 10.000 prove dà **13,87**. ✅ Coerente.
- **Perché funziona**: l'albero degli esiti è infinito (ogni croce fa ripartire la serie); condizionare sul primo passo
  **collassa** l'albero in una ricorsione risolvibile in forma chiusa.
- **Assunzioni**: prove **indipendenti** e identicamente distribuite.

### L'uso che ne facciamo noi: quanto è "normale" una serie di perdite
- Con probabilità di perdita $q$, il numero atteso di operazioni prima di vedere una serie di **$k$ perdite consecutive**
  è $\sum_{i=1}^{k}q^{-i}$.
  | win rate | $k=3$ | $k=4$ | $k=5$ |
  |---|---|---|---|
  | 50% ($q=0{,}5$) | 14 | 30 | **62** |
  | 40% ($q=0{,}6$) | ~9,3 | ~17 | **~30** |
  | 60% ($q=0{,}4$) | ~39 | ~102 | **~258** |
- **Lettura**: con win rate 50%, una serie di **5 perdite è attesa entro ~62 operazioni** — non è un'anomalia e non è un
  segnale di rottura. Il `max_consecutive_losses: 4` di `config/risk.yaml` (con pausa di 60 minuti) scatta quindi su un
  evento che, a win rate 50%, capita in media ogni **30 operazioni**: è una regola di raffreddamento comportamentale,
  **non** un segnale statistico di degrado. Utile saperlo: oggi il numero non è motivato da nulla di scritto.
- ⚠️ **Caveat**: la formula assume operazioni indipendenti. Nella realtà le perdite si **raggruppano** (stesso regime,
  stessa sessione), quindi le serie lunghe arrivano **prima** di così: il numero i.i.d. è un riferimento **ottimista**,
  cioè un pavimento.
- **Collegamento**: è il pezzo mancante della soglia "serie negativa di ritiro" di STRATEGY_LIFECYCLE §8bis (buco 5) —
  dà il **valore atteso** contro cui confrontare la serie osservata, senza dover simulare.
- **Stato**: **assente**. **Rilevanza**: **applicabile ora** → **buco 27**.

### Nota
- Il video è il secondo di una serie: il primo calcola la **probabilità** di una serie di 3 teste in $n$ lanci, il terzo
  (non nel gruppo 1) tratta la convergenza alla distribuzione stazionaria. La tecnica del primo passo serve anche per le
  **probabilità di assorbimento** (rovina del giocatore, C2): stessa impostazione, incognite diverse.

---

## D7 — Chapman-Kolmogorov Equations (catene discrete omogenee)

`L3FqYBDw9fE` · #181 · 37 min · 5.129 parole — video didattico: definizione, dimostrazione, esempio

### Contenuto
- **Esempio**: due monete (testa con probabilità 0,7 e 0,6); se esce testa domani si usa la moneta 1, se esce croce la
  moneta 2 → catena a due stati con $P=\begin{pmatrix}0{,}7&0{,}3\\0{,}6&0{,}4\end{pmatrix}$. Con scelta iniziale equa, la
  probabilità di usare la moneta 1 il secondo giorno è $0{,}5\cdot0{,}7+0{,}5\cdot0{,}6=\mathbf{0{,}65}$ (verificato).
- **Il punto della dimostrazione**: la matrice a $n$ passi $P^{(n)}$ si **definisce** come l'oggetto che contiene le
  probabilità a $n$ passi; che essa sia **uguale alla potenza $n$-esima** $P^n$ **non è una definizione**, è una
  **conseguenza** delle equazioni di Chapman-Kolmogorov
  ($P^{(n+m)}=P^{(n)}P^{(m)}$, dalla probabilità totale + proprietà di Markov) più un'**induzione**.
- **Assunzione usata ovunque**: **omogeneità temporale** (la transizione da 1 a 2 è uguale a quella da 20 a 21) — la stessa
  che D4 segnala come la più fragile in finanza.
- **Avvertenza tecnica utile**: $P^n$ è il **prodotto matriciale** ripetuto, non l'elevamento a potenza elemento per
  elemento. Errore facile da fare implementando.

### Stato e rilevanza
- **Stato**: `03_regimi_macro` usa già $P^n$ per la previsione a $n$ passi e il blueprint lo implementa con
  `np.linalg.matrix_power`. Nessuna voce nuova, solo la **giustificazione** del passaggio.
- **Rilevanza**: reference.

---

## D8 — Kalman Filters for Quant Finance

`zVJY_oaVh-0` · #81 · 48 min · 6.849 parole

### Specificazione vs parametrizzazione (la cornice, utile da sola)
- Ogni modello ha due problemi distinti: **quale modello** (specificazione $M$) e **con quali parametri** ($\theta$).
  Esempi dati: regressione lineare, AR(1), GARCH, Ornstein-Uhlenbeck.
- **Specificazione radicata nella teoria**: per il VIX si sa che la volatilità **torna alla media**; un modello lineare
  estrapola verso $\pm\infty$ (previsioni assurde), un modello a ritorno alla media resta in valori possibili. *"Se il tuo
  modello propone estremi che non possono accadere, la specificazione è sbagliata."*
- **Parametrizzazione**: anche con il modello giusto, parametri sbagliati producono probabilità assurde. Il suo esempio:
  una parametrizzazione implica che il VIX sopra 60 si veda **una volta ogni 65 miliardi di anni**; una migliore dà **una
  volta ogni ~4,2 anni**.
- 🔧 **Strumento che ne ricavo (cheap, e non è nel repo)**: **controllo di sanità per frequenza implicita** — dopo aver
  stimato i parametri, chiedersi *"che frequenza implica questo modello per eventi che ho già osservato?"*. Se il modello
  dice "una volta ogni 65 miliardi di anni" per qualcosa accaduto due volte l'anno scorso, è falsificato senza test
  statistici. È la versione parametrica del **backtest per eccedenze** (D3, buco 22) e parente del controllo sulle
  transizioni impossibili (D4, buco 24).
- **Stato**: assente. **Rilevanza**: **applicabile ora** (vale per qualunque soglia o distribuzione stimata: soglie di
  ritiro, VaR, percentili del Monte Carlo).

### Il filtro di Kalman
- **Cosa fa**: combina **la previsione del modello** con **una misura rumorosa** per stimare lo **stato vero**.
  Ricorsione a due passi: *previsione* (proietta stato e covarianza dell'errore) e *correzione* (incorpora
  l'osservazione).
- **Guadagno di Kalman**: rapporto fra incertezza della previsione e (incertezza della previsione + incertezza della
  misura). $R$ grande (misura rumorosa) → si **crede al modello**; $R$ piccolo → si **crede ai dati**. È l'unica
  manopola che conta.
- **Componenti nel suo esempio** (OU discretizzato ad AR(1) sul VIX): $F$ velocità di ritorno, $B$ media di lungo
  periodo, $Q$ varianza del rumore di processo, $R$ errore di misura. ⚠️ Notazione non standard: di solito $B$ è la
  matrice di controllo; qui è la media.
- **Innovazione**: differenza fra dato osservato e previsione del modello — *"quanto il mercato ha sorpreso il mio
  modello"*.
- **Compromesso mostrato bene**: guadagno alto = adattamento rapido a un nuovo regime ma **contraccolpo** sugli
  outlier; guadagno basso = stabilità ma ritardo nel riconoscere un regime nuovo. Non esiste il pasto gratis.
- **Procedura in tre passi**: (1) calibrazione **offline** del modello (regressione AR(1) per ricavare velocità e media
  di lungo periodo) — ⚠️ con la solita domanda irrisolta *"quanti dati uso?"*; (2) inizializzazione di stato e
  covarianza, con un **periodo di rodaggio** dopo il quale il guadagno converge; (3) ricorsione in linea.
- ⚠️ **Limite dichiarato**: il filtro di Kalman **non aggiorna i parametri del modello** — è *"un cerotto, non una
  cura"*. Per adattare anche i parametri servono estensioni (**dual filter**: i parametri diventano essi stessi stati).

### Perché questo è rilevante per noi (e dove)
- **È un filtro, non un lisciatore**: usa solo passato e presente, quindi è **utilizzabile in tempo reale** senza
  look-ahead — l'opposto della decodifica HMM su tutto il campione (D5, buco 26). Se mai servisse una stima di stato
  adattiva per un gate di regime, questa è la forma onesta.
- 🔧 **Le innovazioni come diagnostica di rottura**: se il modello è ben specificato, le innovazioni **standardizzate**
  sono approssimativamente a media zero e varianza uno e non autocorrelate. Una deriva sistematica (media diversa da
  zero, varianza fuori scala) segnala che **il modello si è rotto**, con un test che si calcola a ogni passo. È il
  complemento naturale del CUSUM di B13 e della regola §8bis: un monitor che misura **quanto il forward sorprende il
  backtest**, invece di aspettare che il drawdown esca dalla distribuzione. → **buco 28**.
- **Applicazione citata dall'industria**: prezzo di obbligazioni illiquide combinando il modello di attualizzazione con
  i pochi scambi osservati e con emissioni simili (dice di averlo fatto a Bloomberg, funzione `BVAL`). Stesso schema di
  D1 (proxy liquidi).
- **Stato**: **assente** in tutto il repo (verificato). **Rilevanza**: futuro come modello; **applicabile ora** come
  criterio (innovazioni, filtro vs lisciatore, controllo di frequenza implicita).

---

## D9 — Trading Mean Reversion with Kalman Filters

`BuPil7nXvMU` · #78 · 13 min · 2.070 parole — applicazione di D8; **nessun numero di performance dichiarato**, e un
avvertimento esplicito a non operare con quel sistema senza capirlo

### In teoria
- Processo di **Ornstein-Uhlenbeck**: si stima una media, si va lunghi ben sotto e corti ben sopra. Nella simulazione la
  media è **stimata dai dati**, non la vera: *"non serve la media teorica esatta, serve essere corretti in media e
  dimensionare bene"* — asintoticamente la legge dei grandi numeri porta alla media di lungo periodo.
- **Assunzione**: che il processo **sia** a ritorno alla media e che la parametrizzazione resti valida.

### In pratica
- ⚠️ I prezzi **non seguono** un OU: non esiste una media di lungo periodo verso cui convergere, e la
  parametrizzazione cambia (ritorna alla media per un periodo, poi smette). *"Questo distrugge quella bella equity
  curve."*
- Restano due domande aperte, entrambe **parametri** (quindi trial da contare): su quale **frequenza** si stima la media
  (5 minuti, 30, giornaliera…) e **quando** la si aggiorna.
- **Il filtro di Kalman come risposta**: combina la media del modello (OU calibrato su una finestra — nel suo sistema
  **60 barre da 1 minuto**) con i dati che arrivano; la media filtrata si sposta verso il trend. La manopola è sempre
  la stessa: fidarsi del modello (media stabile, rischio di restare su un livello stantìo) o dei dati (adattamento
  rapido, rischio di essere sbattuti dal rumore).
- **Onestà della fonte**: nessuna equity curve reale, nessuna metrica; dice che backtest e walk-forward possono aiutare a
  scegliere finestra e rumore, ma *"non c'è garanzia asintotica: puoi passare tutti i test e poi crollare in live"*.

### Come lo classifico per noi
- È la **famiglia** "ritorno a un livello **adattivo stimato**", da distinguere con cura dalla famiglia **CLOSED** dei
  livelli strutturali (order block, FVG, supporti/resistenze: 384 trial, NULL —
  [[project_level_research_v1_null_2026_07_06]]). Non è la stessa cosa: lì il livello è **disegnato** da una regola di
  struttura, qui è la **media stimata di un processo**. Registrarlo come famiglia distinta **non** significa proporlo:
  richiederebbe comunque pre-registrazione, conteggio dei trial (finestra, rumore, soglia di ingresso) e soprattutto
  **esecuzione ottenibile** — una strategia di ritorno alla media su barre da un minuto è esattamente il terreno in cui
  il fill fantasma ha già ingannato questo repo ([[feedback_fill_ottenibile]]).
- **Stato**: assente. **Rilevanza**: futuro (famiglia candidata, non proposta).

---

## D10 — Hawkes Processes for Quant Finance

`BotPHbWFRUA` · #79 · 28 min · 3.983 parole

### La scala dei modelli di arrivo
1. **Variabile di Poisson**: numero di eventi rari in un intervallo, parametro $\lambda$ = frequenza media (stimata per
   massima verosimiglianza). Esempi: scambi in 30 minuti, gap in un anno.
2. **Processo di Poisson**: la stessa cosa **vissuta nel tempo** — si osservano gli arrivi uno a uno e al tempo finale si
   ritrova la distribuzione di partenza.
3. **Poisson non omogeneo**: $\lambda$ diventa **funzione del tempo** $\lambda(t)$ (apertura vs primo pomeriggio); il
   numero di eventi in un intervallo è governato dall'**integrale** dell'intensità.
4. **Processo di Hawkes**: l'intensità diventa **funzione di sé stessa** —
   $$\lambda(t)=\mu+\sum_{t_i<t}\phi(t-t_i)$$
   con $\mu$ intensità di base e $\phi$ **nucleo di attivazione** che decade: ogni evento **aumenta** la probabilità di
   altri eventi (auto-eccitazione, contagio), poi si torna alla base.
- **Conseguenze**: è **non markoviano** e **dipendente dal percorso** → stima dei parametri difficile e costosa (si può
  renderlo markoviano espandendo lo spazio degli stati, come accennato in D4/D5).

### Perché conta: raggruppamento, non solo code grasse
- Un **jump diffusion** standard produce **curtosi in eccesso** ma **non** il raggruppamento: i salti non si chiamano
  l'un l'altro. Con intensità di Hawkes si ottengono **entrambi**.
- **Numeri dichiarati (ordine di grandezza, utili)**: adattando una normale ai rendimenti simulati, l'attesa di un evento
  a 3 sigma risulta ~**370 giorni**; l'attesa implicata dal modello con salti è ~**36–37 giorni**. Un **ordine di
  grandezza** di differenza — è esattamente il controllo di **frequenza implicita** di D8, applicato alle code.
- **Metafora delle barche sul lago** (già usata in D3): la volatilità sale perché qualcuno esce, e l'uscita di uno
  provoca quella di altri; poi il lago torna calmo. Il raggruppamento **e** il ritorno alla media nascono dallo stesso
  meccanismo.

### Uso per noi
- **Non è un modello da implementare** (fuori perimetro: serve a prezzare salti e a modellare flussi di ordini). Conta
  come **giustificazione formale** di due cose che usiamo:
  1. **le perdite si raggruppano**: quindi la formula i.i.d. per l'attesa di una serie di $k$ perdite (D6) è un
     **pavimento ottimista**, e il numero effettivo di osservazioni indipendenti è minore del conteggio grezzo (n_eff,
     `04` §7);
  2. **gli eventi avversi sono contagiosi**: un drawdown aumenta la probabilità del prossimo, il che rende ancora meno
     difendibile un Monte Carlo che rimescola i trade come se fossero indipendenti (`04` §2b, buco 13).
- 🔧 **Test economico che ne deriva (non nel video)**: verificare se gli **esiti delle nostre operazioni** sono davvero
  indipendenti — test delle successioni (runs test) sulla sequenza vinta/persa, o autocorrelazione dei conteggi di
  perdite per finestra. Se l'indipendenza è respinta, le soglie i.i.d. (serie negative, drawdown attesi) vanno riviste
  **al ribasso**. → **buco 29**.
- **Stato**: assente. **Rilevanza**: **applicabile ora** (il test), futuro/reference (il modello).

---

## D11 — Poisson Processes for Quant Finance

`oug0vzbwISQ` · #91 · 42 min · 6.058 parole — è il video **base** di D10 (esce prima nella logica, dopo nel canale)

### Variabile di Poisson: assunzioni esplicite
- Modella il **numero di eventi rari** in un intervallo; $\lambda$ = frequenza media, stimata per massima verosimiglianza
  come **media campionaria** (A3).
- **Quattro assunzioni dichiarate**: **indipendenza** (un evento non rende più probabile il successivo),
  **stazionarietà** ($\lambda$ costante), **non simultaneità**, **conteggi interi**. Supporto: numerabile e illimitato,
  con massa che decade rapidamente.
- **Applicazione**: numero di **gap/salti** di un titolo in una finestra (5 giorni nel suo esempio), numero di insolvenze
  in un portafoglio, numero di scambi in 100 ms.

### Tempi di attesa: esponenziale e assenza di memoria
- Fra un arrivo e l'altro il tempo di attesa è **esponenziale**; la proprietà di **assenza di memoria** dice che aver già
  atteso 5 minuti non cambia la distribuzione dell'attesa residua.
- ⚠️ **Distinzione utile che fa**: la Poisson **non** è senza memoria (osservare 3 scambi cambia la probabilità di
  vederne altri 3 nello stesso intervallo), l'esponenziale sì. Confonderle è un errore comune.
- **Processo di Poisson**: incrementi **indipendenti e stazionari**; conteggi e tempi di attesa convergono alle
  distribuzioni teoriche per la legge dei grandi numeri.

### Non-stazionarietà: lo stesso avvertimento, con un numero
- Calibrando $\lambda$ sui salti storici e usandola nel periodo successivo, il modello attribuisce probabilità
  **< 0,01%** a frequenze che poi si osservano **regolarmente**. È la stessa diagnosi di D8 (frequenza implicita
  assurda) e di A6 (TLC su processo che cambia).

### 🔧 Il pezzo che chiude un anello: $\lambda$ come funzione dello spread
- Nel suo gioco di market making, il tasso di arrivo delle controparti è una **funzione dello spread quotato**: spread
  largo → quasi nessuno transa (oltre il 40% di probabilità di **zero** arrivi), spread stretto → massa che si sposta
  verso più arrivi.
- **Perché conta per noi**: è la formalizzazione della relazione intuita in B20 —
  $$E[\text{guadagno per unità di tempo}]=\underbrace{\text{vantaggio}(\text{spread})}_{\text{cresce}}\times\underbrace{\lambda(\text{spread})}_{\text{decresce}}$$
  con un massimo interno. Vale identica per un **ordine limite**: più lontano metti il limite, meglio entri ma **meno
  spesso** vieni eseguito (e con selezione avversa). Dà la forma matematica al buco 12.
- **Stato**: assente. **Rilevanza**: applicabile ora (qualunque strategia a ordini limite); reference per il market
  making.

### Estensione
- Rendendo $\lambda$ funzione del tempo si ottiene il processo **non omogeneo**; rendendola funzione degli **eventi
  passati** si ottiene il processo di **Hawkes** (D10). Il video è il gradino inferiore della stessa scala.

---

## Sintesi del blocco

> Bozza su D1–D9; le righe di D10 (Hawkes) e D11 (Poisson) si aggiungono a lettura finita.

| strumento | video | stato | rilevanza | destinazione proposta |
|---|---|---|---|---|
| interpolazione a tratti: fra due osservazioni il percorso è ignoto | D1 | memoria, non in 04 | in uso | 04 |
| decomposizione tendenza / stagionalità / shock e sua instabilità | D1 | assente | reference | — |
| **filtraggio vs lisciamento vs previsione** (finestra centrata = look-ahead) | D1 | caso specifico doc, regola generale **assente** | applicabile ora | 04 §1 |
| gerarchia delle assunzioni: cosa permette di misurare un'ipotesi falsa | D1 | doc parziale | in uso | 04 |
| distribuzione dell'evento dal mercato opzioni (straddle) come event-risk | D1 | assente | futuro | 03 §6 / gruppo 2 |
| dati alternativi come informazione che precede il salto | D1 | implicito | reference | 05 |
| **regressione spuria su livelli** ($R^2$ 0,998 vs 0,015) e differenziazione | D2 | pratica corretta ma non scritta | applicabile ora | 04 |
| cointegrazione per lavorare sui livelli | D2 | **assente** | futuro | 04 / 05 |
| volatilità realizzata vs implicita; premio per la varianza per regime | D3 | doc (05 §VRP) | reference | 05 |
| fatti stilizzati: raggruppamento, ritorno alla media, effetto leva, memoria lunga | D3 | 2 su 5 doc | applicabile ora | 05 |
| **ARCH / GARCH**; ARCH(∞) ≡ GARCH(1,1); mescolanza → code grasse | D3 | **assente** | applicabile ora | 05 / core |
| migliorare la **misura** della variabile obiettivo prima del modello (vol realizzata intraday: $R^2$ 5% → 40-60%) | D3 | assente | applicabile ora | 04 |
| **backtest per eccedenze** di una soglia (VaR, soglie di ritiro) | D3 | **assente** | applicabile ora | core + §8bis |
| verifica delle **transizioni impossibili** come falsificazione senza dati | D4 | assente | applicabile ora | 04 |
| errore standard delle probabilità di transizione; indipendenza fra unità | D4 | assente | applicabile ora | 03 |
| omogeneità temporale come assunzione esplicita | D4, D7 | **non nominata** in 03 | applicabile ora | 03 |
| Chapman-Kolmogorov: $P^{(n)}=P^n$ è conseguenza, non definizione | D7 | usato in 03 | reference | — |
| HMM: stati latenti appresi; perdita di interpretabilità; sovradattamento | D5 | blueprint non adottato | futuro | blueprint |
| **inferenza HMM = lisciamento** → look-ahead se usata come segnale | D5 | **assente** (il blueprint fa `fit`+`predict` su tutta la serie) | applicabile ora | blueprint + 04 |
| **analisi del primo passo**: attesa di una serie di $k$ esiti, $\sum_i q^{-i}$ | D6 | **assente** | applicabile ora | §8bis |
| specificazione vs parametrizzazione; **controllo di frequenza implicita** | D8 | assente | applicabile ora | 04 |
| **filtro di Kalman**: guadagno, innovazione, compromesso modello/dati | D8 | **assente** | futuro | 03 / core |
| **innovazioni standardizzate** come diagnostica di rottura del modello | D8 | assente | applicabile ora | §8bis |
| ritorno a un livello **adattivo stimato** (OU + Kalman) come famiglia | D9 | assente | futuro | strategie candidate |
| scala Poisson → non omogeneo → **Hawkes** (auto-eccitazione, contagio) | D10, D11 | assente | reference | 05 |
| jump diffusion: code grasse **senza** raggruppamento; Hawkes le dà entrambe | D10 | assente | reference | 05 |
| test di **indipendenza degli esiti** (successioni, autocorrelazione dei conteggi) | D10 | assente | applicabile ora | 04 / core |
| assunzioni della Poisson; esponenziale e **assenza di memoria** (la Poisson non ce l'ha) | D11 | assente | reference | — |
| **$\lambda$ funzione dello spread**: forma analitica di vantaggio × P(esecuzione) | D11 | assente | applicabile ora | 02 / 04 |

## Buchi emersi nel repo

> Lettura completa D1–D11; numerazione in continuità con A (1–4), B (5–13) e C (14–19). Buchi, non lavoro approvato.

20. **La distinzione filtraggio / lisciamento / previsione non è scritta.** Il repo documenta il caso specifico della
    regime timeline (label same-day), ma non il criterio generale: ogni feature calcolata con finestra centrata o
    ri-stimata sull'intero storico è **lisciamento**, quindi look-ahead. Fonte: D1.
21. **Nessuna regola sulle regressioni su livelli né sulla cointegrazione.** Fonte: D2.
22. **Nessun backtest per eccedenze** delle soglie dichiarate (VaR, soglie di ritiro §8bis, percentili del Monte Carlo).
    Fonte: D3; già segnalato da B14.
23. **Nessun modello di volatilità condizionata.** L'etichetta di regime resta relativa (ATR contro la sua media) e il
    sizing non usa una volatilità prevista. Fonte: D3.
24. **Nessun controllo sulle transizioni impossibili** nei simulatori e nei modelli di stato. Fonte: D4.
25. **La matrice di transizione non ha incertezza**: nessun errore standard per cella, nessun avvertimento
    sull'indipendenza fra strumenti. Fonte: D4.
26. **L'uso dell'HMM come segnale sarebbe look-ahead** così com'è descritto nel blueprint (`fit` + `predict` su tutta la
    serie): servono parametri stimati solo sul passato e probabilità **filtrate**. Fonte: D5.
27. **Manca il riferimento analitico per le serie di perdite**: numero atteso di operazioni prima di una serie di $k$
    perdite, $\sum_{i=1}^{k}q^{-i}$. Il `max_consecutive_losses: 4` del risk gate non è motivato da nulla. Fonte: D6.
28. **Nessuna diagnostica di rottura basata sulle innovazioni** (quanto il forward sorprende il modello), complementare
    al CUSUM del buco 5. Fonte: D8.
29. **L'indipendenza degli esiti non e' mai stata testata.** Tutte le soglie i.i.d. (serie negative, drawdown attesi,
    Monte Carlo che rimescola i trade) assumono indipendenza; i processi auto-eccitanti dicono che gli eventi avversi si
    chiamano l'un l'altro. Test economici: successioni (runs test) sulla sequenza vinta/persa, autocorrelazione dei
    conteggi di perdite per finestra. Se l'indipendenza cade, le soglie vanno abbassate. Fonte: D10.
