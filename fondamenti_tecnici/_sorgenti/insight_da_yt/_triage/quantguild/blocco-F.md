# Blocco F — Simulazione Monte Carlo (4 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Contesto del repo per questo blocco** (verificato il 2026-09-16, prima della lettura):
- **`core/quant_metrics.py`**: `mc_permutation_test` (permutazione dei rendimenti / block bootstrap se autocorrelati),
  `bca_bootstrap_ci` (intervallo BCa), bootstrap stazionario, `pbo_cscv`, `cpcv_splits`.
- **`04_quant_metodologia` §2b**: distinzione netta fra il **Monte Carlo che rimescola i trade** (misura la dipendenza dal
  percorso: maxDD e serie negative) e ciò che serve per validare un edge (DSR, PBO, permutazione della **serie dei
  prezzi**). Regola: *"rimescolare i trade risponde a quanto può andare male il percorso, mai a se il segnale è reale"*.
- **`STRATEGY_LIFECYCLE` §8bis**: le soglie di ritiro (DD, serie negative) si fissano da **percentili alti del Monte
  Carlo del backtest**.
- **Limiti già registrati in questo distillamento**: il Monte Carlo che ricampiona dallo storico assume la stazionarietà
  (B15, buco 13: nessuna incertezza sui parametri; D10, buco 29: nessun test di indipendenza degli esiti).
- **Assenti**: tecniche di **riduzione della varianza** (variate di controllo, antitetiche, campionamento per
  importanza), metodo della **trasformata inversa**, integrazione Monte Carlo, criteri sul **numero di simulazioni**
  necessarie (errore standard $\propto 1/\sqrt{N}$).

---


## F1 — Why Monte Carlo Simulation Works

`-4sf43SLL3A` · #140 · 22 min · 4.018 parole

### Definizione e fondamento
Il Monte Carlo non è una tecnica a sé: è la **legge dei grandi numeri applicata al rovescio**. Se so estrarre dalla
distribuzione ma non so calcolare analiticamente una sua quantità, estraggo $N$ volte e calcolo la statistica empirica:
per la LGN converge alla quantità teorica. *"Quello è esattamente ciò che è la simulazione Monte Carlo, e quello è
esattamente il motivo per cui funziona."*

- 🔧 **Ricetta per le medie**: media campionaria di $N$ estrazioni $\to \mathbb{E}[X]$. Verificata sul dado (media e
  varianza teoriche note) e poi su un gioco composto (dado dispari → moneta truccata, dado pari → moneta equa) di cui la
  media analitica esiste ma è scomoda.
- 🔧 **Ricetta per le probabilità** — la parte davvero riusabile: per stimare $P(A)$ si registra **1 se $A$ accade, 0
  altrimenti**, e si fa la media. Funziona perché per una Bernoulli l'attesa *è* la probabilità. *"Quella è precisamente
  la ricetta."* Con questa si ottengono cose che nessuna formula chiusa dà comodamente: probabilità di rovina,
  probabilità di toccare una soglia, probabilità che un'opzione scada in-the-money.
  - Suo esempio numerico: partendo da 10.000 $, pagando il prezzo equo 325 $ a partita, $P(\text{arrivare a }15.000) = 42{,}8\%$
    → *"non giocherei a questo gioco a 325"*. Il prezzo **equo** non è un prezzo **accettabile**: con un obiettivo di
    ricchezza e un capitale finito, l'EV nullo produce un esito sfavorevole. È la stessa asimmetria di C1 (rovina del
    giocatore) e C5 (drag della volatilità), vista qui come regola di prezzo.
- **Vantaggio (edge) definito di nuovo**: *"accumulazione di valore atteso positivo nel tempo"*. Nei giochi d'azzardo
  l'EV non è sotto controllo; nei giochi a informazione incompleta (poker, trading) **le azioni contribuiscono
  direttamente all'EV**. Il banco prezza **sopra** il valore equo: se prezzi a 325 o meno, il caso migliore è il pareggio.
- ⚠️ **Il limite, dichiarato dalla fonte stessa**: tutto quanto sopra vale perché la distribuzione è **fissa** (il dado
  non cambia; il moto browniano geometrico, una volta parametrizzato, non cambia). In finanza le distribuzioni sono
  **variabili nel tempo** e ciò che si osserva è solo l'empirica, per di più marginale di una gigantesca congiunta
  (i rendimenti non sono indipendenti da inflazione, mercato del lavoro, politica). *"Se la distribuzione non è fissa e
  usiamo il Monte Carlo, il valore che otteniamo sarà allettante da usare, ma può non essere corretto."*

### Domanda a cui risponde
"Perché ho il diritto di credere ai numeri che escono da una simulazione?" — e, di rimbalzo, "quando **non** ho quel
diritto".

### Assunzioni
Estrazioni **indipendenti** dalla **stessa** distribuzione, e distribuzione **fissa nel tempo**. Cadute queste, la LGN
non garantisce nulla: non c'è una linea rossa a cui convergere.

### Modi di fallire
- Usare il MC su una distribuzione che deriva (data drift) e leggere il risultato come se fosse un valore teorico.
- Confondere la convergenza in distribuzione (l'istogramma si sovrappone alla densità) con la convergenza della statistica.
- Applicarlo a quantità che non esistono: la fonte rimanda qui al proprio video *"i rendimenti attesi non esistono"* e
  dice che il VaR fallisce proprio perché *"approssima un livello che non esiste e non ha garanzie di convergenza"*.

### Stato nel repo
La ricetta della media è implicita ovunque; la **ricetta con la variabile indicatrice per le probabilità** non è
esplicitata da nessuna parte, benché sia lo strumento naturale per domande che il repo si pone davvero (probabilità di
toccare il drawdown di ritiro, probabilità di una serie di $k$ perdite — cfr. buco 25 in `blocco-D.md`). L'assunzione di
stazionarietà è già registrata come limite (`04_quant_metodologia` §2b, buco 13).

### Rilevanza
**Applicabile ora**: la soglia di ritiro di `STRATEGY_LIFECYCLE` §8bis si fissa su percentili del Monte Carlo del
backtest; la variabile indicatrice permette di esprimerla come *probabilità di violazione* invece che come percentile,
che è la forma in cui la domanda viene effettivamente posta.

### Claim registrati senza uso
Nessuna statistica dichiarata sui mercati: il video è interamente su esempi costruiti, quindi i numeri (325 $, 42,8 %,
0,55) sono **riproducibili per costruzione**, non affermazioni empiriche.

---

## F2 — Control Variates for Variance Reduction

`Iu_gCD74Y70` · #175 · 20 min · 3.239 parole

### Definizione e formula
Il problema: l'errore standard di una stima Monte Carlo scala come $1/\sqrt{N}$, quindi **dimezzarlo costa quattro volte
il calcolo**. Quando ogni percorso è caro, alzare $N$ non è praticabile. Le variate di controllo riducono la varianza
**a parità di $N$**, usando informazione ausiliaria che la simulazione produce comunque.

$$C_{CV} = Y - c\,(X - \mathbb{E}[X]), \qquad c^{*} = \frac{\mathrm{Cov}(Y,X)}{\mathrm{Var}(X)}$$

- $Y$ = quantità d'interesse; $X$ = variabile ausiliaria **di cui si conosce l'attesa in forma chiusa**.
- Per linearità dell'attesa i due termini in $X$ si cancellano: $\mathbb{E}[C_{CV}] = \mathbb{E}[Y]$. **La variata di
  controllo non è la quantità: ha la stessa attesa.** Corollario che il video corregge esplicitamente: la sua
  *distribuzione* non è quella dei payoff, solo la media coincide.
- $c^{*}$ è **il coefficiente di una regressione lineare** di $Y$ su $X$, stimato con covarianza e varianza
  **campionarie** dopo la simulazione (le vere non si conoscono: se si conoscessero, si conoscerebbe anche $\mathbb{E}[Y]$).
- Varianza risultante: $\mathrm{Var}(C_{CV}) = \mathrm{Var}(Y)\,(1-\rho^{2}_{XY})$ → **la riduzione dipende solo dalla
  correlazione**; massima per $|\rho| \to 1$, nulla per $\rho = 0$. Si estende a più variabili ausiliarie (regressione
  multipla).
- Esempio numerico (call europea sotto moto browniano **aritmetico**, $S_0=K=100$, $\mu=10\%$, $\sigma=30\%$, 252 passi,
  10.000 simulazioni; variata = media aritmetica dei prezzi simulati, la cui attesa è $S_0 + \mu T/2$): errore standard
  da **0,05 a 0,02**, ~**75% di riduzione della varianza**, intervallo di confidenza più stretto **a parità di calcolo**.
  Lui stesso dichiara l'esempio ridondante (se conosci $\mathbb{E}[S_T]$ non ti serve simulare).

### Domanda a cui risponde
"Come ottengo la stessa precisione con meno simulazioni, quando ogni simulazione costa?"

### Assunzioni
1. Esiste una $X$ **correlata** con $Y$ e con **attesa nota analiticamente**. Senza il secondo requisito la tecnica non
   esiste: è quello che fa cancellare i termini.
2. La stima di $c$ dal campione introduce un piccolo bias, che la fonte non discute.

### Modi di fallire
- Usare come variata qualcosa la cui attesa è a sua volta stimata → si sposta il problema, non lo si risolve.
- Leggere la distribuzione della variata come se fosse quella della quantità.
- Credere di aver ridotto l'**incertezza sul modello**: si riduce solo il rumore Monte Carlo. Se il modello è sbagliato,
  la variata di controllo fa convergere più in fretta **al numero sbagliato**.

### Stato nel repo — **assente**
Nessuna tecnica di riduzione della varianza in `core/quant_metrics.py`: `mc_permutation_test` gira 1.000 permutazioni,
`bca_bootstrap_ci` 2.000 ricampionamenti, il bootstrap stazionario 500, tutti a forza bruta. → **buco 36**.

### Rilevanza — **futuro, con una riserva esplicita**
La tecnica richiede un'attesa nota in forma chiusa: nei nostri Monte Carlo (permutazione dei rendimenti, bootstrap dei
trade) **non esiste una quantità con attesa analitica** da usare come ancora, e il costo per replicazione è
trascurabile. Quindi **catalogata, non applicabile al lavoro attuale**; diventa rilevante solo se si arriverà a prezzare
strumenti con simulazione di percorsi costosa (volatilità rough, esotici path-dependent).

Il pezzo **riusabile subito** non è la tecnica ma la sua premessa: **l'errore standard di una stima Monte Carlo è
$\propto 1/\sqrt{N}$ e va dichiarato**. Oggi il repo riporta p-value di permutazione e soglie da percentile **senza
l'incertezza Monte Carlo che li accompagna**: con 1.000 permutazioni, l'errore standard su un p-value vicino a 0,05 è
$\sqrt{0{,}05 \cdot 0{,}95/1000} \approx 0{,}7$ punti percentuali, cioè un "p = 0,048" e un "p = 0,062" **non sono
distinguibili** dal numero di permutazioni scelto. → **buco 37**.

### Claim registrati senza uso
Il collegamento alla letteratura su volatilità rough e approssimazione dei funzionali di prezzo con reti neurali: fuori
perimetro, nessun numero, nessuna fonte verificabile citata.

---

## F3 — Inverse Transform Method for Generating Random Variables

`1WB8PtKnaqU` · #176 · 48 min · 7.351 parole

### Definizione e procedura
Come si **genera** una variabile aleatoria con una distribuzione voluta, partendo dall'unica cosa che un calcolatore sa
produrre: un numero uniforme in $[0,1]$.

> Intuizione: il **codominio** di *ogni* funzione di ripartizione è $[0,1]$ (limite $0$ a $-\infty$, limite $1$ a
> $+\infty$). Quindi se so **invertire** la CDF, un numero uniforme in $[0,1]$ diventa un'estrazione con la corretta
> massa di probabilità. *"Pescare 0,5 dal cappello"* e leggere sulla CDF a quale esito corrisponde.

🔧 **Procedura (4 passi)**: 1) trova la CDF $F$; 2) invertila, $G = F^{-1}$; 3) estrai $U \sim \mathcal{U}(0,1)$;
4) restituisci $G(U)$.

- **Caso continuo** — immediato. Esempio esponenziale: $F(x) = 1 - e^{-\lambda x}$ → $G(u) = -\frac{\ln(1-u)}{\lambda}$.
  Tre righe di codice; la densità generata si sovrappone alla teorica.
- **Caso discreto** — serve un ciclo che **accumula** massa da sinistra a destra finché supera $U$. Due implementazioni
  mostrate: `np.searchsorted` sulla somma cumulata (vettoriale, richiede la CDF **tabulata per intero**) e un `while` che
  accumula $F \mathrel{+}= p(a)$, $a \mathrel{+}= 1$ (dinamico). La seconda è quella generale: serve quando il supporto è
  **infinito** e la CDF non si può tabulare — il suo esempio è la **geometrica**.
- ⚠️ **Condizione di validità dichiarata dalla fonte**: la CDF deve essere **invertibile analiticamente**. Per la
  normale non lo è ($\int e^{-s^2/2}ds$ non ha primitiva elementare) → serve un'altra tecnica (cita
  **accettazione-rifiuto**, non trattata).
- **Da dove viene $U$**: generatori pseudo-casuali. Mostra il **generatore lineare congruenziale**
  $x_{n+1} = (a x_n + c) \bmod m$, normalizzato per $m$. Tre proprietà: **periodicità**, uniformità, **riproducibilità da
  seme**.
- ⚠️ **Osservazione che vale oltre il video**: *"sono algoritmi deterministici… se ho il seme e la funzione, posso
  predire con accuratezza del 100% ogni esito"*. La sequenza rispetta le frequenze giuste, ma **non è casuale**: è una
  sequenza fissa. Riproducibilità e casualità sono la stessa proprietà letta da due lati.

### Domanda a cui risponde
"Come costruisco estrazioni da una distribuzione che non sia quella che il generatore mi dà già?"

### Assunzioni
CDF nota **e invertibile in forma chiusa**; nel caso discreto, la massa dev'essere accumulabile (finita, o funzionale
come nella geometrica).

### Modi di fallire
- Applicarlo a una CDF non invertibile e ripiegare su un'inversione numerica senza dichiarare l'errore introdotto.
- Nel caso discreto, sbagliare il verso della disuguaglianza nel ciclo — errore che la fonte commette **in diretta** e
  poi corregge (`while U > F`), il che è anche la prova che l'implementazione va **testata sulle frequenze**, non letta.
- Trattare un flusso pseudo-casuale con seme fisso come se fosse una fonte di casualità indipendente.

### Stato nel repo — **assente come tecnica, ma la premessa è ovunque**
Il repo non genera mai variabili da una distribuzione parametrica: **ricampiona sempre dallo storico** (permutazione,
bootstrap stazionario, baseline random a entrata casuale). È una scelta coerente con
[[feedback_mass_search_vs_preregistration]] e con il rifiuto della normalità, quindi la trasformata inversa resta
**catalogata, non un buco operativo**. → **buco 38** (sotto) riguarda invece il seme.

**Il seme, verificato**: tutto il repo usa `np.random.default_rng` con **seme fisso** — `SEED` in
`analysis/level_research/engine.py`, `htf.py`, `analysis/mentor_signals/backtest.py`, `seed=42` in `reaction.py`, e la
pre-registrazione `docs/ROUND_NUMBER_GRID_PREREGISTRATION.md` lo fissa a **42** per contratto. Giusto per la
riproducibilità (è esattamente il punto della fonte); ma **nessun risultato è stato ripetuto con semi diversi**, quindi
non sappiamo quanta parte della differenza fra "reale" e "random" sia il particolare flusso pseudo-casuale numero 42.
→ **buco 38**.

### Rilevanza
**Reference** per la tecnica; **applicabile ora** per la lettura sul seme, che tocca ogni baseline random già prodotto.

### Claim registrati senza uso
Nessuno: il video non fa affermazioni empiriche sui mercati.

---

## F4 — Monte Carlo Integration in Python

`EnsWVUjpqDE` · #216 · 8 min · 1.419 parole

### Definizione e formula
Il caso più semplice di Monte Carlo: approssimare un integrale definito quando non esiste primitiva.

$$\int_a^b f(x)\,dx \;\approx\; \frac{1}{N}\sum_{i=1}^{N} (b-a)\, f(X_i), \qquad X_i \sim \mathcal{U}(a,b)$$

🔧 **Lettura geometrica che la rende memorizzabile**: ogni campione definisce un rettangolo di **larghezza fissa $b-a$** e
**altezza $f(X_i)$**; l'integrale è la **media delle aree** di quei rettangoli. La somma di Riemann fa variare la
larghezza ($\Delta x$) tenendo fissi i punti; il Monte Carlo fa il contrario — **tiene fissa la larghezza e rende
casuali i punti**.

- Verifica numerica: $\int_0^2 4x^3\,dx = 16$ analiticamente; con 10.000 punti uniformi ottiene **15,985**.
- È di nuovo solo la legge dei grandi numeri (F1): $\frac{1}{N}\sum f(X_i) \to \mathbb{E}[f(X)]$, e
  $\mathbb{E}[f(X)] = \frac{1}{b-a}\int_a^b f$ per $X$ uniforme.

### Domanda a cui risponde
"Come calcolo un'area/attesa quando l'integrale non si risolve?"

### Assunzioni
$f$ valutabile puntualmente; dominio limitato $[a,b]$; campionamento **uniforme** (per domini illimitati o integrandi
molto concentrati serve il campionamento per importanza, che il canale non tratta).

### Modi di fallire
- Dominio illimitato o integrando a coda pesante: l'errore standard esplode e nessun $N$ ragionevole basta (è lo stesso
  problema che in A rendeva inutile la CLT con momenti infiniti).
- Riportare **15,985 senza il suo errore standard**: il video non lo calcola, e infatti non si può dire se
  l'approssimazione sia buona o fortunata. Stesso vuoto del buco 37.

### Stato nel repo — **assente e non necessario**
Nel repo non ci sono integrali da valutare: le quantità sono medie campionarie su trade osservati. Il video è il
gradino didattico più basso della famiglia F.

### Rilevanza — **reference**
L'unico pezzo che vale operativamente è la lettura "Monte Carlo = media, Riemann = griglia": è ciò che spiega perché il
Monte Carlo **non peggiora** con il numero di dimensioni (l'errore resta $1/\sqrt{N}$ in qualunque dimensione, mentre
una griglia costa $N^d$). Il video non lo dice; è la ragione per cui la tecnica esiste in finanza.

### Claim registrati senza uso
Nessuno.

---

## Sintesi del blocco F

| # | video | cosa aggiunge | stato nel repo | rilevanza |
|---|---|---|---|---|
| F1 | Why Monte Carlo Simulation Works | LGN come fondamento; **ricetta a variabile indicatrice per le probabilità**; limite della distribuzione non fissa | fondamento implicito; indicatrice **non esplicitata** | **applicabile ora** |
| F2 | Control Variates | riduzione della varianza via regressione su ausiliaria a attesa nota; $\mathrm{Var}(1-\rho^2)$; **SE $\propto 1/\sqrt{N}$** | riduzione varianza **assente**; SE del MC **mai dichiarato** | futuro (tecnica) / **ora** (la premessa) |
| F3 | Inverse Transform | generazione di variabili da CDF invertibile; PRNG, LCG, determinismo del seme | generazione parametrica assente **per scelta**; seme fisso 42 ovunque | reference / **ora** (seme) |
| F4 | MC Integration | integrale come media di rettangoli a larghezza fissa | assente e non necessario | reference |

**Valutazione onesta del blocco**: è il blocco **meno denso** del distillamento. Tre dei quattro video sono materiale
didattico su tecniche che il repo non usa e, per come è impostata la ricerca (ricampionamento dallo storico invece di
modelli parametrici), **non dovrebbe usare**. Il valore non sta nelle tecniche ma in due cose trasversali: la **ricetta
dell'indicatrice** (F1) e il fatto che **ogni stima Monte Carlo ha un proprio errore standard che finora non abbiamo mai
riportato** (F2, F3, F4).

### Buchi aperti dal blocco F
- **Buco 36** — nessuna tecnica di riduzione della varianza in `core/quant_metrics.py`. *Classificato futuro*: manca
  l'ingrediente (una quantità ad attesa nota) e il costo per replicazione è trascurabile. Catalogato, non da installare.
- **Buco 37** — **l'incertezza Monte Carlo delle nostre stime non viene mai riportata**. I p-value di permutazione
  (1.000 repliche), gli intervalli BCa (2.000), il bootstrap stazionario (500) escono come numeri puntuali. Con 1.000
  permutazioni, il SE di un p-value vicino a 0,05 vale ~0,7 punti percentuali: **"p = 0,048" e "p = 0,062" non sono
  distinguibili** dal numero di repliche. Rilevante per la regola di futilità DSR di `STRATEGY_LIFECYCLE` e per ogni
  verdetto vicino alla soglia. *Priorità alta: è un costo di una riga di codice.*
- **Buco 38** — **tutti i baseline random girano con seme fisso** (42, per contratto nelle pre-registrazioni). Corretto
  per la riproducibilità, ma nessun risultato è stato ripetuto con semi diversi: non sappiamo quanto della differenza
  reale-vs-random dipenda da quel particolare flusso. Da distinguere: il seme **va dichiarato e fissato** nella
  pre-registrazione (contratto), e **l'analisi va ripetuta su più semi** in fase di verifica (robustezza). Le due cose
  non sono in conflitto.
- **Buco 39** — **la ricetta dell'indicatrice non è usata**: le soglie di ritiro di `STRATEGY_LIFECYCLE` §8bis sono
  espresse come *percentili* del Monte Carlo, mentre la domanda operativa è una *probabilità* ("qual è la probabilità di
  toccare questo drawdown / questa serie di $k$ perdite se la strategia è viva?"). Si aggancia al buco 25 (`blocco-D.md`).

### Conflitti per la mappa dei modelli
Nessuno. Il blocco F non contraddice nulla di ciò che il repo afferma; ne misura solo un'omissione (l'errore Monte
Carlo). L'unico attrito è **interno alla fonte**: F1 dichiara che in finanza le distribuzioni non sono fisse e che
quindi il Monte Carlo *"può non essere corretto"*, mentre F2 investe venti minuti nel rendere più precisa una stima
**condizionata a un modello scelto**. Le due cose convivono solo se si tiene fermo che la riduzione della varianza
riduce il **rumore di simulazione**, mai l'**errore di modello** — distinzione che la fonte non enuncia e che va tenuta
noi.

---
