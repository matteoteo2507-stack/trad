# Blocco C — Sizing, rovina, ergodicità, dipendenza dal percorso (11 video)

Letto per intero dalle copie in `_raw/_lettura/`. Legenda come in [`blocco-A.md`](blocco-A.md).

**Contesto del repo per questo blocco** (verificato il 2026-09-15):
- `05_portfolio_rischio`: volatility drag $R_G\approx\bar R-\sigma^2/2$, leva che amplifica il drag come $L^2$,
  "Kelly frazionario", trade raggruppati → frazione ottimale **sotto** il Kelly calcolato come i.i.d.
- `agents/quant_reviewer.md` §4: *"sizing full Kelly o oltre = red flag di ruin risk"*; riportare l'$N$ effettivo
  indipendente.
- `config/risk.yaml`: size massima per trade 2% del capitale, drawdown massimo 15%, drawdown giornaliero 5%, pausa
  dopo 4 perdite consecutive. **Nessun calcolo di sizing ottimo** in `core/`: i limiti sono soglie, non una
  frazione derivata dall'edge.
- Rovina del giocatore ed ergodicità in forma esplicita: **assenti**.

---

## C1 — How to Trade with the Kelly Criterion

`7tvW3NvRnPk` · #137 · 16 min · 2.773 parole

### Puntata fissa vs puntata proporzionale
- **Puntata fissa** (additiva): con E positivo la ricchezza deriva linearmente; puntata più grande = più upside e
  **più probabilità di rovina prima** di accumulare.
- **Puntata proporzionale al capitale** (moltiplicativa): il sistema diventa **non ergodico** — pochi percorsi
  accumulano moltissimo e trascinano in alto la media, **la maggioranza** chiude sotto il capitale iniziale.
  Esempio del video (frazione non ottimale): ricchezza **media** finale 1.757 su 1.000 iniziali, ma probabilità di
  chiudere sopra 1.000 solo **47%**. *"Il difetto delle medie"*: il fiume profondo in media 7 piedi.
- **Obiettivo corretto** con puntata proporzionale: massimizzare la **media geometrica** (il log della ricchezza),
  non quella aritmetica.
- **Stato**: doc (05 volatility drag; B17 ergodicità verificata). **Rilevanza**: in uso.

### Criterio di Kelly
- **Formula** (il video la nomina come "funzione di $p$, $q$ e profitto netto per unità rischiata" senza scriverla):
  $$f^*=\arg\max_f E[\ln(1+fX)]\;\Rightarrow\;f^*=p-\frac{q}{b}$$
  con $p$ probabilità di vincita, $q=1-p$, $b$ = vincita netta per unità persa. In **multipli di R** (perdita = 1R,
  vincita media = $W$ R): $f^*=p-q/W$. Per rendimenti continui approssimativamente normali: $f^*\approx\mu/\sigma^2$.
- **Domanda**: quale frazione del capitale rischiare per trade per massimizzare la crescita di lungo periodo del
  **singolo percorso** (media temporale), non della media d'insieme.
- **Assunzioni**: trade indipendenti; $p$ e $b$ **noti e costanti**; nessun vincolo di drawdown; orizzonte lungo.
- **Risultati del video** (illustrativi, parametri non dati, **non coerenti fra loro**): con Kelly la probabilità di
  chiudere sopra il capitale sale al 76% (poi citata come 71% per lo stesso caso; orizzonte che passa da 1.000 a
  10.000 trade), mediana finale 1.018 contro 836 della frazione non ottimale. **Con parametri stimati male**, la
  stessa politica Kelly scende al **41%**. Il punto qualitativo è corretto; i numeri non si usano.

### Ciò che il video non dice e che conta (proprietà note di Kelly)
- **Drawdown del Kelly pieno**: nel limite continuo (Thorp) la probabilità che la ricchezza scenda **prima o poi** a
  una frazione $x$ del **capitale iniziale** è $x$ — scendere alla metà del capitale di partenza almeno una volta ha
  probabilità **50%**, a un terzo il 33%. Su orizzonte lungo, drawdown profondi **dal massimo** sono praticamente
  certi. Incompatibile con un drawdown massimo del 15% (`config/risk.yaml`) e con qualunque regola da prop firm.
- **Oltre Kelly**: la crescita è una parabola in $f$; a $2f^*$ la crescita attesa è **zero**, oltre è negativa, pur con
  edge positivo.
- **Kelly frazionario**: con $f=k\,f^*$ la crescita è $\approx k(2-k)$ volte quella piena e la varianza $\approx k^2$
  volte. **Mezzo Kelly: ~75% della crescita con ~25% della varianza** (metà della volatilità).
- **Asimmetria dell'errore di stima**: la curva di crescita scende molto più in fretta a destra dell'ottimo che a
  sinistra. **Sovrastimare l'edge costa molto più che sottostimarlo** → con $p$ e $b$ stimati da un backtest (dove
  l'edge è sistematicamente gonfiato dalla selezione) la scelta razionale è una frazione di Kelly, spesso 1/4–1/2.
- **Trade dipendenti**: raggruppamenti per sessione o regime aumentano la varianza effettiva → $f^*$ reale **sotto**
  quello i.i.d. (già in 05).
- **Parametri variabili nel tempo**: il video mostra $p$ e payoff che oscillano per regime e suggerisce stime
  **per regime** e un bot che ri-stima Kelly iterativamente. ⚠️ Ri-stimare $f^*$ su finestre mobili importa tutto il
  rumore di stima di B13/B22 dentro la size; senza una penalità per l'incertezza (Kelly con parametri incerti, o
  frazione ridotta) amplifica gli errori.

### Stato e rilevanza
- **Stato**: doc (05 "Kelly frazionario", reviewer "full Kelly = red flag"); **nessun calcolo di $f^*$** né in core né
  nelle pre-registrazioni; le formule sopra (drawdown del Kelly pieno, $k(2-k)$, asimmetria) **non sono scritte**.
- **Rilevanza**: **applicabile ora** — dimensionamento del capitale proprio sui segnali mentore (unico edge
  misurato): con $p$, vincita media in R ed E[R] del backtest si calcola $f^*$ e si sceglie una frazione (1/4–1/2),
  ricordando che l'edge del backtest è una stima gonfiata per selezione.
- ⚠️ **Verifica sul codice — i due numeri non sono confrontabili.** Il controllo n. 7 di `core/risk_gate.py` calcola
  `abs(size × entry_price) / equity`: il `max_size_per_trade_pct: 0.02` di `config/risk.yaml` è un limite
  sull'**esposizione nozionale**, non sul **capitale a rischio fino allo stop**. Kelly in multipli di R è invece la
  frazione di capitale **persa se scatta lo stop** = nozionale × distanza percentuale dello stop. Su strumenti a leva
  (FX, oro) il 2% nozionale corrisponde a un rischio per trade molto più piccolo; su uno stop largo il rapporto cambia
  ancora. **Il risk gate non ha alcun limite sul capitale a rischio per trade**: senza quel numero non si può né
  dimensionare con Kelly né verificare di stare sotto una sua frazione. → **buco 14** (vedi fondo del blocco).

---

## C2 — Gambler's Ruin Problem in Quant Trading

`YNvhjSr_nz0` · #145 · 30 min · 4.575 parole

### Rovina del giocatore (versione classica)
- **Setup**: +1 con probabilità $p$, −1 con $q=1-p$, capitale iniziale $i$, ci si ferma a $0$ (rovina) o a $N$
  (obiettivo). Processo **markoviano**: conta solo il capitale attuale.
- **Formula** (il video la mostra, non la deriva):
  $$P(\text{obiettivo}\mid i)=\frac{1-(q/p)^i}{1-(q/p)^N}\quad(p\neq q),\qquad P(\text{obiettivo}\mid i)=\frac{i}{N}\quad(p=q)$$
- **Verifica dei numeri del video**:
  | caso | video (simulazione) | valore esatto |
  |---|---|---|
  | $p=0{,}6$, da 5 a 10 | "circa 80%" | **88,4%** |
  | $p=0{,}6$, da 7 a 10 | "circa 97%" | **95,8%** |
  | $p=0{,}5$, da 7 a 10 | "circa 75%" | **70%** |
  | $p=0{,}5$, da 10 a 100 | 10% | **10%** |
  Gli scarti sono rumore di simulazione; il primo è il più largo.
- **Lezioni corrette**: più capitale iniziale → meno rovina; l'edge **sposta molto** la probabilità di arrivare
  all'obiettivo; la simulazione (media degli indicatori di successo, LGN) approssima la formula.
- ⚠️ **Errore della fonte**: *"anche con un edge, se si gioca all'infinito la rovina è certa"*. **Falso.** Senza
  obiettivo, con $p>q$ la probabilità di rovina partendo da $i$ è $(q/p)^i<1$ — con $p=0{,}6$ e $i=5$ è
  $(2/3)^5\approx13\%$. La rovina è certa solo con $p\le q$. (Con puntate **proporzionali** al capitale la rovina in
  senso stretto non avviene mai, ma può avvenire quella pratica: vedi C1.)
- **Stato**: assente. **Rilevanza**: applicabile ora.

### Estensione ai trade: payoff asimmetrici e parametri stimati
- **Tesi**: un sistema di trading **è** una rovina del giocatore con payoff asimmetrici (vincita media ≠ perdita
  media) e probabilità **non costanti**. Si stimano $p$, vincita e perdita medie dai trade e si calcola la
  probabilità di raggiungere un capitale obiettivo.
- **Sensibilità ai parametri**: ricampionando lo stesso sistema, o dopo un cambio di regime ($p=0{,}53$, vincita 157,
  perdita 149), la probabilità di arrivare all'obiettivo passa da ~80% a ~60%. Unità e capitali non specificati: non
  ricalcolabile, ma è la stessa fragilità di B22 (parametri stimati usati come noti).
- **Consiglio della fonte**: stime con medie mobili esponenziali o filtri; *"sarà sbagliata, ma meglio di niente;
  meglio una stima del 90% che del 10%"*.
- **Leve**: le quattro gambe dell'aspettativa totale (B12); proposta di "coprirsi prima" quando la probabilità di
  perdere sale e "lasciar correre" quando c'è margine — ⚠️ regola adattiva non specificata, da trattare come trial.

### Strumento da aggiungere (non nel video): probabilità di toccare un obiettivo prima di un limite
- **Versione continua** (rendimenti con deriva $\mu$ e varianza $\sigma^2$ per unità di tempo o per trade), con
  $\theta=2\mu/\sigma^2$:
  $$P(\text{toccare }+a\text{ prima di }-b)=\frac{1-e^{\theta b}}{e^{-\theta a}-e^{\theta b}}\;\xrightarrow{\;\mu\to0\;}\;\frac{b}{a+b}$$
- **Senza obiettivo** (rovina vicina a Cramér-Lundberg): $P(\text{perdere }c)\approx e^{-2\mu c/\sigma^2}$.
- **Esempio verificabile, ipotesi dichiarate**: challenge con obiettivo **+8%** e drawdown massimo **−10%**, **edge
  zero**, limite continuo, niente limite giornaliero né di tempo → $P(\text{superarla})=10/18\approx$ **56%**. Più di
  metà delle challenge si superano **per caso** con una strategia a E nullo. È il meccanismo di sopravvivenza di B7
  applicato alle prop: un passaggio non è evidenza di edge. Trade discreti, limite giornaliero e scadenza abbassano la
  percentuale, ma non ne cambiano la lezione.
- **Domanda che risponde**: con E[R] e dispersione **per trade** stimati, qual è la probabilità di raggiungere un
  obiettivo prima di un limite di perdita — la domanda esatta di una challenge prop e di una soglia di ritiro.
- **Assunzioni**: incrementi indipendenti e parametri costanti (entrambe violate, B13); approssimazione normale degli
  incrementi (sottostima il rischio con code grasse, B14).
- **Stato**: **assente** — `docs/PROP_FIRM_CRITERIA.md` misura la consistency rule sui dati ma **non** calcola
  probabilità di superamento o di rovina (verificato). **Rilevanza**: **applicabile ora**
  ([[project_prop_criteria_2026_08_07]]).

---

## C3 — Why Most Traders Lose: Ergodicity for Quant Trading

`dryV1qJYUw8` · #92 · 13 min · 2.150 parole — **sintesi breve di C1 e B17**

### Contenuto già catalogato
- Aspettativa totale e quattro leve (B12); gioco d'azzardo a distribuzione fissa vs gioco a informazione incompleta
  con edge variabile (B20); puntata **additiva** = sistema ergodico, puntata **proporzionale** = non ergodico, *"l'esperienza
  dei molti non è l'esperienza dei pochi"* (B17); Kelly come massimizzazione della **media temporale** (C1).
- Precisazione corretta che vale la pena tenere: *"Kelly non rende ergodico un sistema non ergodico; migliora
  l'esperienza del singolo percorso"*.
- **Statistica d'apertura non usata**: *"il 90 e rotti per cento dei trader perde"* — non verificata, nessuna fonte.

### Kelly pieno vs mezzo Kelly con edge variabile nel tempo
- **Esempio simulato**: edge che oscilla fra periodi più e meno favorevoli. Con **Kelly pieno** la media d'insieme
  finale resta **sotto** il capitale iniziale; con **mezzo Kelly** no. Parametri non dati: illustrativo.
- **Lettura**: il Kelly pieno è ottimo solo con edge **noto e costante**. Quando l'edge reale in un periodo è più basso
  di quello usato per dimensionare, si sta puntando **oltre** il Kelly di quel periodo, dove la crescita crolla
  (asimmetria descritta in C1). Il Kelly frazionario è quindi anche un'**assicurazione contro la variabilità
  dell'edge**, non solo contro l'errore di stima.
- *"Punta di più quando l'edge è alto, meno o nulla quando è basso"*: ⚠️ presuppone di **stimare l'edge corrente**, che
  arriva sempre in ritardo (*"saremo sempre reattivi"*, lo dice lui) e con il rumore di B13/B22. Senza soglie e finestre
  pre-registrate diventa ottimizzazione a posteriori della size.
- **Stato**: doc (05, reviewer: full Kelly = red flag); la motivazione "edge variabile" per il Kelly frazionario non è
  scritta. **Rilevanza**: applicabile ora (stesso uso di C1).

---

## C4 — Math Proves the Journey Matters More than the Destination

`hYNxlEKy5Hg` · #61 · 17 min · 2.662 parole — ⚠️ **classificazione per titolo errata**: è un video di sviluppo
personale (adattamento alle aspettative, stoicismo, "il viaggio conta più della meta"), non di sizing. Letto per intero
comunque; un solo strumento.

### Banda adattiva di aspettativa ("finestra di varianza")
- **Modello**: ogni giorno si forma un'**aspettativa** e, implicitamente, una **finestra** di deviazioni tollerate (la
  varianza attesa). Un esito dentro la finestra non sorprende; uscirne sopra o sotto è uno **shock**. Dopo un cambio di
  regime (un infortunio, lasciare il lavoro) aspettativa e finestra **si riadattano** al nuovo livello; un obiettivo
  lontano, raggiunto, cade dentro la finestra e "non pesa più".
- **Forma quantitativa equivalente**: media mobile (o esponenziale) ± $k$ deviazioni standard mobili — un control
  chart / z-score adattivo.
- **La lezione che conta per noi (non detta nel video)**: una banda adattiva **si ricentra dopo una rottura**, quindi un
  monitoraggio basato su statistiche **mobili** **normalizza il degrado**: dopo qualche settimana il nuovo livello peggiore
  diventa "atteso" e smette di generare allarmi. Per questo il forward di una strategia va giudicato contro la
  **distribuzione fissa dichiarata nella pre-registrazione** (regola di STRATEGY_LIFECYCLE §8bis: *"si giudica contro la
  distribuzione, non contro l'umore"*), e un eventuale CUSUM (buco 5) va tarato sui parametri del backtest, non ristimato
  in corsa.
- **Stato**: la regola §8bis esiste; il motivo "le bande mobili assorbono il degrado" non è scritto. **Rilevanza**:
  applicabile ora (disegno del monitoraggio forward); il resto del video: fuori perimetro.

---

## C5 — How Volatility Drag Destroys (and Creates) Wealth

`pNRkxItN0qM` · #18 · 18 min · 2.691 parole — parte promozionale (corso "personal hedge fund", nota di ricerca)

### Volatility drag (già distillato) e verifica dei numeri
- $R_G\approx\bar R-\sigma^2/2$ è già in `05_portfolio_rischio` (da #44). Aggiunge animazioni: la **media aritmetica** dei
  percorsi è trascinata in alto da pochi outlier (solo ~40% dei percorsi le sta sopra); la **geometrica** divide i percorsi
  circa a metà, cioè si comporta come la **mediana**.
- **Numeri ricalcolati**:
  - aritmetica 10%, volatilità 30% → $0{,}10-0{,}30^2/2=5{,}5\%$ (video: "circa 6%"); ✓
  - aritmetica 10%, drag 3% → volatilità ≈ 24,5%, geometrica ≈ 7% (video: 6,88%, formula esatta); ✓
  - aritmetica 18% e geometrica ≈ 0 su 30 anni → volatilità ≈ 60%; stessa volatilità implicita del caso "40% con 18% di
    drag". Coerenti fra loro.
- **Stato**: doc (05). **Rilevanza**: in uso.

### ⚠️ "Drag buono" e "drag cattivo": errore di impostazione
- **Claim**: *"un grande trade vincente crea molto volatility drag, ma è drag buono"*; il drag cattivo viene dalla
  diversificazione azionaria e dall'inseguire rendimenti effimeri.
- **Si rompe**: il drag è $\sigma^2/2$, una proprietà della **varianza dei rendimenti**, non di un singolo esito. Un
  singolo guadagno del 40% in un periodo non ha drag (aritmetica = geometrica su un periodo). Quello che la fonte intende
  è: **una media aritmetica abbastanza alta e ripetibile può più che compensare il drag** (40% di media con 60% di
  volatilità dà comunque ~22% geometrico, contro l'8% del portafoglio prudente).
- *"Il drag cattivo viene dal tenere un portafoglio diversificato"*: formulazione fuorviante; la diversificazione **riduce**
  la varianza e quindi il drag (05, B5). Il suo punto, detto meglio: la diversificazione **fra titoli correlati** smette di
  ridurla nelle crisi.

### Il conflitto "drag vs ricchezza nella coda destra" ha una soluzione esatta
- **Il video**: *"hanno ragione entrambi"* (ridurre il drag e concentrare sulle grandi vincite), poi consiglia il prudente a
  quasi tutti.
- **Risoluzione (non nel video)**: con esposizione $f$ a un'opportunità di media $\mu$ e varianza $\sigma^2$, la crescita
  geometrica è $g(f)=f\mu-\tfrac12 f^2\sigma^2$, massima a $f^*=\mu/\sigma^2$ — **il criterio di Kelly** (C1).
  Concentrare aumenta la crescita **finché** $f<f^*$; oltre la riduce, e a $2f^*$ la annulla. "Coda destra" e "drag" sono
  i due termini della stessa parabola.
- **Condizione di validità**: vale solo con $\mu$ **vero e ripetibile**. Con $\mu$ stimato (e gonfiato dalla selezione)
  l'ottimo reale è a sinistra di quello calcolato → la prudenza non è un gusto, è la risposta all'incertezza su $\mu$.
  È il motivo per cui i professionisti concentrati sono pochi e il resto sopravvive meglio con il prudente.
- **Per noi**: il lead del playground trend ha E[R] migliore dove la volatilità di gruppo è più alta (crypto, metalli,
  [[project_trend_playground_lead_2026_08_14]]). La domanda giusta non è "più volatilità = meglio", ma dove sta
  $\mu/\sigma^2$ per gruppo, al netto dell'incertezza su $\mu$.
- **Stato**: la parabola $g(f)$ e il legame esplicito drag ↔ Kelly **non sono scritti** (05 cita "Kelly frazionario" come
  conseguenza della leva). **Rilevanza**: applicabile ora.

### Copertura monetizzata → CAGR più alto
- Portafoglio coperto che perde meno nel crollo e compra a sconto → geometrico più alto. Ripete B10, B24 e 05 §Tail risk;
  numeri illustrativi da simulazione promozionale. **Nessuna voce nuova.**
- Strumento interattivo (media aritmetica, volatilità, geometrica sulla frontiera efficiente): reference.

---

## C6 — Quant Portfolio Management and Volatility Drag

`YDjOBWb5iG8` · #45 · 16 min · 2.520 parole — "fireside chat" su una sua nota di ricerca interna non pubblicata

### Sharpe massimo ≠ crescita geometrica massima
- Il portafoglio di tangenza (Sharpe massimo sulla frontiera efficiente) **non** è quello che massimizza la crescita
  geometrica. *"Il quant dirà che è banale, obiettivi diversi; ma le conseguenze pratiche sono nella costruzione."*
- **Stato**: doc (05, volatility drag punto 4; reviewer). **Rilevanza**: in uso.

### Il combinato a crescita positiva da due gambe a crescita nulla o negativa
- **Esempio del video**: strategia A con crescita geometrica **0%** (media aritmetica 15%) + sleeve di copertura con
  crescita geometrica **−2,5%** → il combinato ha crescita geometrica **positiva**.
- ⚠️ **Numeri incoerenti**: con media 15%, crescita zero richiede volatilità ≈ **55%** ($0{,}15-\sigma^2/2=0$); con il "30% o
  40%" che dice a voce la crescita sarebbe 10,5% o 7%.
- **Il meccanismo è corretto e ha un nome**: **rendimento da diversificazione** (Booth e Fama, 1992). Per un portafoglio a
  pesi $w_i$:
  $$g_p-\sum_i w_i g_i\;\approx\;\tfrac12\Big(\sum_i w_i\sigma_i^2-\sigma_p^2\Big)\;\ge 0$$
  tanto più grande quanto più la varianza del portafoglio è sotto la media pesata delle varianze — cioè con correlazioni
  basse o negative.
- **Esempio ricalcolabile, parametri ipotetici dichiarati**: A con $\mu=15\%$, $\sigma=54{,}8\%$ ($g_A\approx0$); B con
  $\sigma=20\%$, $g_B=-2{,}5\%$ (quindi $\mu_B=-0{,}5\%$); $\rho=-0{,}5$; pesi 70/30.
  $\mu_p=10{,}35\%$, $\sigma_p^2=0{,}49\cdot0{,}300+0{,}09\cdot0{,}04+2\cdot0{,}21\cdot(-0{,}5)\cdot0{,}548\cdot0{,}20\approx0{,}128$,
  $g_p\approx10{,}35\%-6{,}39\%\approx$ **+4,0%**. Il risultato del video è riproducibile.
- ⚠️ **Condizione che il video non dice**: il beneficio esiste con **ribilanciamento periodico a pesi costanti**. Senza
  ribilanciare, i pesi derivano verso la gamba che cresce, la varianza del portafoglio non resta bassa e il rendimento da
  diversificazione svanisce. Il ribilanciamento **è** il meccanismo (vende ciò che è salito, compra ciò che è sceso).
- **Stato**: 05 afferma che una sleeve a crescita negativa può alzare la crescita del combinato, ma **nessun file di
  `fondamenti_tecnici/` menziona ribilanciamento, pesi costanti o rendimento da diversificazione** (verificato) →
  **buco 18**. Il blocco E ha un video dedicato (#220, *Why is Portfolio Rebalancing Important?*).
- **Rilevanza**: applicabile ora (qualunque combinazione di stream; il PAC in fase 1 è un solo ETF e non ne è toccato).

### "Triplo long": il capitale umano è correlato al mercato
- *"Sei long la casa, il lavoro e il portafoglio"*: in recessione si perdono insieme lavoro, valore della casa e
  portafoglio, e **serve liquidità quando tutti ne hanno bisogno**.
- **Per noi**: è la ragione del **buffer** separato in `08_asset_allocation_passiva` (dimensionato sulla durata della
  disoccupazione) e dell'idea di stream fisicamente indipendenti. Il capitale umano va trattato come un'esposizione del
  portafoglio, non come qualcosa di esterno.
- **Stato**: doc implicito (08 buffer). **Rilevanza**: reference (pilastro investing).

### Leva più copertura "batte il buy-and-hold"
- **Claim**: con sleeve di copertura e leva appropriata si batte il buy-and-hold di azioni diversificate; la leva senza
  copertura invece fa esplodere i drawdown (non linearità). Ricerca **interna, non pubblicata**.
- **Registrato senza uso**: stessa cautela già scritta in `08` §"portfolio engineering con hedge leg" (singolo backtest,
  nessun fuori campione). Il principio (meno drawdown → meno drag) è in 05.
- **Esempi di gambe indipendenti**: market making su prediction market (risoluzione fisicamente indipendente; ammette che il
  **volume** è correlato al ciclo), sleeve sul premio per la varianza condizionata alla struttura della volatilità
  implicita. Già in B5 (con l'annotazione sul vincolo di finanziamento comune) e nel conflitto VRP/convexity di
  `DECISIONS.md`. **Nessuna voce nuova.**

---

## C7 — The Mathematical Trap of "Just Buy SPY"

`sgbEkAYAdwk` · #46 · 6 min · 1.064 parole — video promozionale ("assumi un allocatore di rischio")

### I numeri del "retail" di paglia
- **Claim messo in bocca al retail**: 57.000 $ al 10% annuo per 30 anni → *"ben sopra il milione"*.
- **Verifica**: $57.000\times1{,}10^{30}\approx995.000$ $ — **appena sotto** il milione. E il 10% è una media **aritmetica**:
  con una crescita geometrica realistica di ~8,5% il capitale finale è ~660.000 $ (volatility drag, C5). L'errore
  aritmetica/geometrica che il video attribuisce al retail è reale; i numeri sono sbagliati anche nella versione che critica.

### "Triplo long" e liquidità (ripetuto da C6)
- In recessione servono soldi quando lavoro, casa e portafoglio calano insieme → si vende a sconto. **Punto valido**, già
  coperto in `08` dal **buffer separato** dimensionato sulla durata della disoccupazione.

### Entrare nel 2022 o nel 2023
- **Esempio**: stesso S&P 500, un portafoglio entra a gennaio 2022, l'altro a gennaio 2023 → il secondo ha drawdown minore
  e "metriche migliori". ⚠️ Un **singolo percorso scelto col senno di poi**: il 2022 è noto come anno negativo. La fonte
  stessa dice *"non è timing, è un esperimento mentale"*, e la frase sulle metriche si contraddice ("rendimento totale
  minore" ma "meglio aspettare"). **Scartato come evidenza.**
- **Il "6 milioni di ingressi in una barra oraria"** ripetuto da B23 e applicato al prezzo di carico: irrilevante per un
  versamento mensile.

### Overlay di convexity "che emula il timing"
- **Claim**: un portafoglio con una gamba di copertura (long convexity) "rivaleggia" con quello entrato col senno di poi nel
  2023: meno drag, prezzo di carico più basso comprando nella svendita. Stessa simulazione su **un** periodo (2022–2023).
- **Registrato senza uso**: stesso claim di B10, B24, C5, C6; stessa cautela di `08` §"portfolio engineering con hedge leg".

### ⚠️ Conflitto con una decisione del repo — mappa dei modelli
- **"Comprare solo l'indice è una trappola; serve un allocatore con overlay di copertura"** (C7, e in forma più generale
  C5–C6) **vs** **PAC passivo All-World, buffer separato, nessun timing, nessuna ricetta levered-hedge da singolo
  backtest** (`08_asset_allocation_passiva`, `DECISIONS.md`, [[project_pac_inputs_2026_08_04]]).
- **Non si riapre la decisione.** Condizioni che separano i due domini:
  1. il problema reale che il video solleva — **liquidità nel momento sbagliato** — nel nostro pilastro è risolto dal
     **buffer**, non da un overlay;
  2. in **fase di accumulo** (portafoglio piccolo rispetto ai versamenti) un ribasso è un vantaggio per il PAC, non una
     minaccia (`08` §Decenni persi, punto 1); il sequence risk morde in decumulo ed è gestito dal glide-path;
  3. la copertura ha un **costo certo** (l'assicurazione è in media sovraprezzata: premio per la varianza, `05`) e un
     **beneficio che dipende dal campione**; l'evidenza offerta è un solo percorso col senno di poi più ricerca interna non
     pubblicata, da una fonte che vende il corso sull'argomento.
- **Condizione sotto cui il claim varrebbe**: portafoglio **grande** rispetto al reddito, **vicino al decumulo** o con
  leva, e un overlay il cui costo netto sia misurato **fuori campione** su più crisi. Nessuna di queste vale oggi.
- **Stato**: decisione doc (08, DECISIONS). **Rilevanza**: reference per il pilastro investing; da registrare nella mappa a
  distillazione finita.

---

## C8 — The Math of "Burn the Boats": Why Hedging Ruins Everything

`20PEEtXrqUI` · #65 · 12 min · 1.697 parole — ⚠️ **classificazione per titolo errata**: "hedging" qui è il **piano B
nella vita** (battaglia, startup, relazioni, la sua scelta di non tornare a un lavoro da quant), non la copertura di
portafoglio. Video motivazionale. Letto per intero; lo strumento dichiarato è sbagliato, e l'errore è la parte utile.

### L'argomento
- Vittoria/sconfitta partiziona lo spazio; anche "ho le navi / le ho bruciate" lo partiziona. Condizionando ad "avere le
  navi", nella varianza negativa si ritira → $P(\text{vittoria}\mid\text{navi})\ll P(\text{vittoria}\mid\text{navi bruciate})$.
  Stessa struttura per startup con lavoro di riserva e relazioni. *"Se lo copri, non lo vuoi abbastanza."*
- Nessun dato: *"la massa di probabilità parla da sé"*; i diagrammi di Venn sono disegnati per ipotesi.

### ⚠️ Perché non regge (tre errori, tutti già catalogati altrove nel distillamento)
1. **Associazione ≠ causa.** Anche se nei dati $P(\text{successo}\mid\text{nessun piano B})>P(\text{successo}\mid\text{piano
   B})$, il confronto è **confuso**: chi brucia le navi è diverso da chi non lo fa (motivazione, abilità, assenza di
   alternative), e il condizionamento non isola l'effetto di togliere il piano B. Per quello servirebbe un confronto a
   parità di tutto il resto.
2. **Sopravvivenza.** I casi raccontati sono i vichinghi che hanno vinto e i fondatori che ce l'hanno fatta; chi ha bruciato
   le navi e ha perso non racconta (B7, B11).
3. **Ignora la dimensione della perdita.** Bruciare le navi può alzare $P(\text{vittoria})$ ma trasforma la sconfitta in
   **rovina**, uno stato assorbente. Massimizzare la probabilità di successo di un singolo tentativo **non** è massimizzare
   la crescita attesa su tentativi ripetuti: C1 (Kelly) e C2 (rovina del giocatore) dicono l'opposto per i giochi
   ripetuti — prima si sopravvive, poi si accumula edge.

### Cosa si salva
- **Dispositivo di impegno** (economia comportamentale): togliersi un'opzione può cambiare il comportamento futuro in modo
  favorevole quando il problema è la **propria incoerenza nel tempo** (cedere nella varianza negativa). È un fenomeno reale;
  il video lo presenta come legge matematica.
- **Lezione statistica ricavata dall'errore**: una probabilità condizionata calcolata su gruppi che **si sono
  autoselezionati** non misura l'effetto della scelta. Vale identica per "i trader che usano lo stop perdono di più" o "le
  strategie con filtro di regime rendono di più": prima di leggere un condizionamento come effetto, chiedersi chi è finito
  in quel gruppo e perché.
- **Stato**: assente come voce; il vincolo "partizione = trial, calcolabile all'ingresso" (B1) copre il caso operativo.
  **Rilevanza**: reference.

### Conflitto per la mappa dei modelli
- **"La copertura rovina tutto"** (C8) **vs** **sopravvivenza prima dell'edge: Kelly frazionario, rovina del giocatore,
  buffer, sleeve di copertura** (C1, C2, `05` §Tail risk, `08` buffer — e lo stesso autore in B10, B24, C5–C7). Condizione di
  validità: il claim può valere per un **impegno singolo e non ripetuto**, con posta non finanziaria e dove il rischio
  principale è la propria incoerenza nel tempo; **non** vale per **scommesse finanziarie ripetute** con rovina assorbente,
  dove togliersi la ritirata è l'errore di sizing che C1 e C2 misurano. Nota: la fonte dichiara di avere il 100% del
  capitale nelle proprie strategie e di vendere i propri corsi — la tesi è anche la sua scelta di vita.

---

## C9 — Life's Downside Variance: Math vs. Drugs, Edge, Judgement

`Ok08aBwfeDY` · #66 · 8 min · 1.156 parole — ⚠️ **classificazione per titolo errata**: video motivazionale sulle scelte di
vita dopo un periodo negativo (palestra, studio, corsa contro droghe, feste, gioco d'azzardo come azioni a EV positivo o
negativo). Letto per intero.

### Cosa non regge
- *"La vita è un gioco a somma zero e la controparte sei tu"*: **metafora, non matematica**. Un gioco a somma zero richiede
  due parti i cui guadagni si annullano; "sé stessi come controparte" contraddice la definizione. Scartato.
- La classificazione delle azioni in EV positivo e negativo è **dichiarata**, non stimata; gli "asintoti" (a 50 anni sano e
  sposato contro rovinato) sono esempi costruiti. Nessun numero.

### Cosa si salva (già nel repo)
- **La politica non cambia per l'esito appena realizzato.** Il casinò che subisce una grossa vincita di un giocatore
  **non** inizia a fare scommesse a EV negativo per recuperare: l'edge delle puntate future non dipende dall'esito
  passato. Per noi è la regola anti-*tilt* e anti-*resulting*: dopo un drawdown si decide in base all'edge stimato e alla
  distribuzione attesa, non al dolore dell'esito (STRATEGY_LIFECYCLE §8bis *"contro la distribuzione, non contro
  l'umore"*; B23).
- **"Guarda gli asintoti"**: valutare una politica **ripetuta** dal suo esito di lungo periodo, cioè dalla media temporale
  (B17, C1). Euristica corretta, qui applicata a scelte non misurate.
- **Aspettativa e finestra di varianza nel tempo**: ripete C4.
- **Stato**: doc (§8bis, B17). **Rilevanza**: reference. **Nessuna voce nuova.**

---

## C10 — How to Think About Stock Market Bubbles and Drawdowns

`A6QWWrhDJTc` · #33 · 20 min · 3.208 parole — "fireside chat" sulla presunta bolla dell'IA; parte promozionale (corso
"personal hedge fund")

### "Bolla" riformulata come aspettative
- **Tesi**: "bolla" è un'etichetta che si applica **col senno di poi** (conferma, sopravvivenza). Più utile: il prezzo di
  equilibrio incorpora **aspettative**; un crollo è una **revisione violenta** delle aspettative dopo un catalizzatore
  **imprevedibile**; il rischio è la deviazione dalle aspettative. La revisione può essere rapida (crollo) o lenta
  (sanguinamento pluriennale).
- **Lettura**: coerente con "prevedere il timing è impossibile, posizionarsi per sopravvivere" (`05` §Tail risk). Non aggiunge
  uno strumento, ma chiarisce perché un segnale "c'è una bolla" non è tradabile: dice che le aspettative *potrebbero* essere
  riviste, non **quando**.
- **Opinioni registrate senza uso**: *"se il crollo è violento il prezzo scende sotto il giusto, se è lento è più
  corretto"*; *"nessuno scrive più codice"*; uno studio del MIT sull'impatto dell'IA liquidato senza riferimento.
- **Stato**: doc (05). **Rilevanza**: reference.

### Affermazioni storiche controllabili
- **"Circa una crisi ogni 10 anni, drawdown fra il 20% e l'80%"** negli ultimi 100 anni: ordine di grandezza **coerente**
  con la storia azionaria USA (1929–32, 1937, 1973–74, 1987, 2000–02, 2008, 2020, 2022). Non verificato caso per caso;
  l'80% è la Grande Depressione.
- **"Il Giappone ha impiegato dal 1989 al 2024 per recuperare"**: **corretto per il Nikkei 225 come indice di prezzo**
  (massimo di fine dicembre 1989 superato a febbraio 2024). ⚠️ In **rendimento totale** (dividendi reinvestiti) il recupero è
  arrivato diversi anni prima: la statistica da indice di prezzo esagera la durata. Il concetto è già in `08` §Decenni
  persi (Italia e Giappone), con la precisazione che è una statistica da investimento in un'unica soluzione al massimo.

### Stress test per scenari
- **Strumento**: *"cosa succede al mio portafoglio se questo asset scende dell'80% e quello del 40%?"* — shock
  **deterministici** applicati alle posizioni, senza ipotesi sulla distribuzione. Per l'autore è l'unica misura in avanti
  davvero utile, proprio perché le misure statistiche dipendono da un passato non stazionario (B14, B15).
- **Domanda che risponde**: sopravvivo a uno scenario che non so prevedere? Non "quanto è probabile", ma "cosa succede se".
- **Limiti**: la scelta degli scenari è arbitraria; non dà probabilità; gli shock simultanei vanno scelti tenendo conto che
  in crisi le correlazioni salgono (05).
- **Stato**: in forma **mentale** in `08` (*"scegli una quota azionaria che reggi attraverso un −50% / 10 anni piatti"*);
  **assente** come strumento per le posizioni di trading (gap simultaneo su posizioni correlate, es. oro e NASDAQ nei
  canali di trasmissione di `03` §6). **Rilevanza**: applicabile ora (pilastro PAC già coperto; trading da valutare).

---

## C11 — How to Protect your Stock Portfolio from Market Crashes

`Z3w8TpH7kYw` · #16 · 14 min · 2.190 parole — parte promozionale (corso "personal hedge fund", nota di ricerca)

### La diversificazione fra titoli fallisce quando serve (già distillato)
- Caterpillar e NVIDIA quasi scorrelati a inizio 2025, poi nel crollo dei dazi seguono entrambi l'S&P 500; regressione
  NVIDIA su Caterpillar da piatta a inclinata. PCA sulle due serie: prima componente al **74%** della varianza con carichi
  entrambi positivi = fattore di mercato non diversificabile.
- Coincide con `05` (non-stazionarietà delle correlazioni, tassonomia del rischio, PCA) e con B14. **Nessuna voce nuova.**

### Assicurazione di portafoglio con put
- **Strumento**: una **put** lunga sull'indice dà **convexity** nel crollo; il pagamento, **monetizzato**, finanzia acquisti
  a prezzi di svendita → recupero più rapido dal drawdown. I rendimenti del portafoglio coperto nel crollo diventano quasi
  scorrelati dal mercato.
- **Collegamento non detto**: monetizzare la copertura nel drawdown e comprare ciò che è sceso **è un ribilanciamento**:
  è lo stesso meccanismo del rendimento da diversificazione di C6, con una gamba a payoff convesso.
- **Obiezione del premio per la varianza** (*"l'assicurazione è in media sovraprezzata, sanguini theta"*): risposta del video
  = *"non tutte le assicurazioni hanno lo stesso prezzo, si confrontano i preventivi"*. ⚠️ Stessa analogia debole di B10:
  preventivi diversi non provano una mispricing sfruttabile. Il conflitto "vendi il premio vs compra convexity" è già
  mappato in `DECISIONS.md` e resta condizionato al regime.

### Skew delle put e scelta dello strike
- **Tesi**: la protezione al ribasso costa di più in volatilità implicita (**skew**), ma le put **molto fuori dal denaro**
  possono dare nel crollo una convexity **simile o maggiore** di quelle più vicine al denaro, con un costo di mantenimento
  (sanguinamento) minore. *"Stessa copertura a metà prezzo."* Cita le presentazioni di un ETF di copertura dalle code
  (nella trascrizione "KO ETF": **non identificato**).
- **Lettura**: è un'osservazione nota fra chi gestisce programmi di copertura delle code, ma **dipende** da velocità e
  profondità del crollo e da quanto si riprezza la volatilità implicita (le put lontane guadagnano soprattutto
  dall'espansione di volatilità). Nessun parametro nel video: non ricalcolabile.
- **Implementazione minima citata**: comprare ogni mese una put a **20 delta**; *"sanguini molto più in fretta di una
  strategia dedicata"* (quella del corso).
- **Claim non verificabile**: *"assomiglia molto alla mia performance live del 2025"* — autodichiarata, un solo episodio.
- **Stato**: opzioni fuori perimetro operativo (`05` §VRP come reference; conflitto VRP/convexity in `DECISIONS.md`); skew,
  greche e prezzo delle opzioni sono nel **gruppo 2** (non distillato ora). **Rilevanza**: futuro / reference.

---

## Sintesi del blocco

> Lettura completa C1–C11. Tre video (C4, C8, C9) sono classificati male per titolo: sviluppo personale e motivazione, non
> sizing. Le righe di C10–C11 sono in fondo alla tabella.

| strumento | video | stato | rilevanza | destinazione proposta |
|---|---|---|---|---|
| puntata fissa vs proporzionale; media d'insieme vs media temporale | C1, C3 | doc (05, B17) | in uso | 05 |
| criterio di Kelly: $f^*=p-q/b$, in R $p-q/W$, continuo $\mu/\sigma^2$ | C1 | **assente** come calcolo | applicabile ora | 05 + core |
| proprietà del Kelly pieno e frazionario: $P(\text{scendere a }x)=x$, crescita $k(2-k)$, varianza $k^2$, asimmetria dell'errore, edge variabile | C1, C3 | **assente** | applicabile ora | 05 |
| capitale a rischio per trade (nozionale × distanza dello stop) vs esposizione nozionale | C1 | **assente** nel risk gate | applicabile ora | `core/risk_gate.py`, `config/risk.yaml` |
| rovina del giocatore discreta (verificata); "rovina certa anche con edge" è falso | C2 | assente | applicabile ora | 05 |
| probabilità di toccare $+a$ prima di $-b$ ($\theta=2\mu/\sigma^2$); Cramér-Lundberg; challenge +8/−10 a edge zero ≈ 56% | C2 | **assente** | applicabile ora | `docs/PROP_FIRM_CRITERIA.md`, §8bis |
| banda adattiva che si ricentra e assorbe il degrado | C4 | assente come vincolo | applicabile ora | STRATEGY_LIFECYCLE §8bis |
| parabola $g(f)=f\mu-\tfrac12 f^2\sigma^2$: drag e Kelly sono la stessa curva | C5 | **assente** | applicabile ora | 05 |
| "volatility drag buono" di un singolo trade: errore di impostazione | C5 | — | reference | — |
| rendimento da diversificazione a pesi costanti (Booth-Fama), esempio ricalcolato +4,0% | C6 | **assente** (nessuna menzione del ribilanciamento) | applicabile ora | 05 / blocco E |
| capitale umano correlato al mercato ("triplo long") | C6, C7 | doc implicito (08 buffer) | reference | 08 |
| "comprare solo l'indice è una trappola" vs PAC passivo: conflitto per domini | C7 | decisione doc | reference | mappa dei modelli |
| dispositivo di impegno (togliersi un'opzione contro la propria incoerenza nel tempo) | C8 | assente | reference | — |
| probabilità condizionate su gruppi **autoselezionati**: associazione ≠ effetto della scelta | C8 | parziale (B1: partizione = trial) | applicabile ora | 04 |
| "la copertura rovina tutto" vs sopravvivenza prima dell'edge: conflitto per domini | C8 | — | reference | mappa dei modelli |
| la politica non cambia per l'esito appena realizzato (anti-tilt, anti-resulting) | C9 | doc (§8bis, B23) | in uso | — |
| "bolla" riformulata come revisione delle aspettative dopo un catalizzatore imprevedibile | C10 | doc (05 §Tail risk) | reference | — |
| verifica di affermazioni storiche: ~1 crisi ogni 10 anni (coerente); Giappone 1989–2024 vero solo come indice di prezzo | C10 | doc parziale (08 §Decenni persi) | reference | 08 |
| **stress test per scenari** (shock deterministici sulle posizioni, nessuna ipotesi distributiva) | C10 | mentale in 08; **assente** per il trading | applicabile ora | 05 / risk gate |
| put lunga come copertura convessa; monetizzazione nel drawdown = ribilanciamento | C11 | reference (05 §VRP) | futuro | gruppo 2 / blocco E |
| skew delle put e scelta dello strike (costo di mantenimento vs convexity) | C11 | assente | futuro | gruppo 2 |

## Buchi emersi nel repo

> Bozza su C1–C3; numerazione in continuità con i blocchi A (1–4) e B (5–13). Buchi, non lavoro approvato.

14. **Il risk gate non limita il capitale a rischio per trade.** `max_size_per_trade_pct` è esposizione nozionale
    (`abs(size × entry_price) / equity`, verificato in `core/risk_gate.py`); non esiste un limite su nozionale ×
    distanza dello stop. Senza quel numero non si può dimensionare con Kelly né verificare di stare sotto una sua
    frazione. Fonte: C1.
15. **Nessuno strumento per la probabilità di toccare un obiettivo prima di un limite.** Né per le challenge prop
    (`docs/PROP_FIRM_CRITERIA.md` non la calcola) né per le soglie di ritiro. La formula continua con
    $\theta=2\mu/\sigma^2$ e la versione discreta della rovina del giocatore rispondono direttamente; con edge zero
    una challenge +8% / −10% si supera per caso nel ~56% dei casi. Fonte: C2.
16. **Le proprietà del Kelly frazionario non sono scritte.** 05 e il reviewer dicono "Kelly frazionario" e "full
    Kelly = red flag" senza le ragioni quantitative: rovina pratica del Kelly pieno ($P(\text{scendere a }x)=x$),
    crescita $k(2-k)$ con varianza $k^2$, asimmetria dell'errore di stima, edge variabile nel tempo. Manca anche la
    **parabola** $g(f)=f\mu-\tfrac12 f^2\sigma^2$ con massimo in $f^*=\mu/\sigma^2$, che unifica volatility drag e Kelly e
    chiude il conflitto "ridurre il drag vs concentrare sulla coda destra". Fonti: C1, C3, C5.
17. **Nessun vincolo scritto contro il monitoraggio con statistiche mobili ristimate.** Una banda adattiva (media e
    deviazione mobili) si ricentra dopo una rottura e **assorbe il degrado**: dopo qualche settimana il livello peggiore
    diventa "atteso". §8bis giudica già contro la distribuzione del backtest, ma il motivo non è esplicitato e nulla
    impedisce a un futuro controllo di deriva (buco 5) di essere implementato con finestre mobili. Fonte: C4.
18. **La condizione del ribilanciamento non è scritta.** 05 afferma che una sleeve a crescita geometrica negativa può
    alzare la crescita del combinato, ma nessun file di `fondamenti_tecnici/` menziona ribilanciamento, pesi costanti o
    rendimento da diversificazione (verificato con ricerca). Senza ribilanciare, i pesi derivano verso la gamba vincente
    e il beneficio svanisce: la formula $g_p-\sum w_ig_i\approx\tfrac12(\sum w_i\sigma_i^2-\sigma_p^2)$ vale **a pesi
    costanti**. Fonte: C6 (da completare con #220 nel blocco E).
19. **Nessuno stress test per scenari sulle posizioni di trading.** Il pilastro PAC ne ha una versione mentale (`08`: la
    quota azionaria che si regge attraverso un −50%); per il trading non esiste un controllo "cosa succede al conto se le
    posizioni aperte subiscono insieme uno shock dato" (gap simultaneo su oro e NASDAQ nei canali di `03` §6), che non
    richiede ipotesi distributive. Fonte: C10.

## Conflitti per la mappa dei modelli

- **"Ridurre il volatility drag"** **vs** **"la ricchezza si crea nella coda destra, concentrando"** (C5, che li lascia
  "entrambi veri"). **Non è un conflitto ma una curva**: con esposizione $f$ la crescita geometrica è
  $g(f)=f\mu-\tfrac12 f^2\sigma^2$, massima a $f^*=\mu/\sigma^2$ (Kelly, C1). Condizione di validità della concentrazione:
  $f$ sotto $f^*$ **e** $\mu$ vero e ripetibile; con $\mu$ stimato l'ottimo reale sta a sinistra di quello calcolato, da cui
  la prudenza.
- **"Comprare solo l'indice è una trappola; serve un allocatore con overlay di copertura"** (C7, con C5, C6, C10, C11)
  **vs** **PAC passivo All-World, buffer separato, nessun timing, nessuna ricetta levered-hedge da singolo backtest** (`08`,
  `DECISIONS.md`, [[project_pac_inputs_2026_08_04]]). **La decisione non si riapre.** Condizioni: il problema reale che la fonte
  solleva (liquidità nel momento sbagliato, "triplo long") è coperto dal **buffer**; in accumulo un ribasso favorisce il PAC;
  la copertura ha costo certo (premio per la varianza) e beneficio dipendente dal campione, e l'evidenza offerta è un solo
  percorso col senno di poi più ricerca non pubblicata da chi vende il corso. Il claim varrebbe per un portafoglio grande
  rispetto al reddito, vicino al decumulo o con leva, con costo netto dell'overlay misurato fuori campione su più crisi.
- **"La copertura rovina tutto: brucia le navi"** (C8) **vs** **sopravvivenza prima dell'edge** (C1, C2, `05` §Tail risk, `08`
  buffer; e lo stesso autore in C5–C7, C11). Condizione: il claim può valere per un **impegno singolo non ripetuto**, con posta
  non finanziaria e dove il rischio dominante è la propria incoerenza nel tempo (dispositivo di impegno); **non** vale per
  **scommesse finanziarie ripetute** con rovina assorbente, dove togliersi la ritirata è l'errore di sizing che Kelly e la rovina
  del giocatore misurano.
- **Premio per la varianza: "l'assicurazione è sovraprezzata"** (`05`) **vs** **"compra put, meglio se molto fuori dal
  denaro"** (C11). Già mappato in `DECISIONS.md` (vendi il premio vs compra convexity, condizionato al regime); C11 aggiunge
  solo l'argomento dello skew (costo/convexity per strike), non verificabile senza parametri.
