# Blocco B — Edge, fortuna vs abilità, validità del backtest (24 video)

Il nostro protocollo visto da fuori. Letto per intero dalle copie in `_raw/_lettura/`.

A differenza del blocco A qui ci sono **claim e numeri**: esempi su NVIDIA, percentuali di simulazione,
aneddoti di consulenza. Si applica il filtro sulle statistiche dichiarate: i numeri **ricalcolabili**
si verificano, quelli su un solo esempio o su un solo episodio si registrano come illustrazione e non
come evidenza. Il blocco ha anche parti promozionali (corsi, piattaforma): segnalate dove pesano
sull'argomento.

Legenda come in [`blocco-A.md`](blocco-A.md).

---

## B1 — Why Your Backtests are Wrong

`w-EbZ6Xct_E` · #102 · 31 min · 4.573 parole

### Distribuzione condizionata vs incondizionata
- **Esempio**: somma di due dadi. Incondizionata: $E=7$, $P(11)\approx5{,}6\%$. Condizionata al primo
  dado = 5: $E=8{,}5$, $P(11)\approx16{,}7\%$. La LGN garantisce la convergenza **di ciascuna**, ma verso
  valori diversi.
- **Stato**: doc implicito. **Rilevanza**: in uso.

### Proprietà di Markov
- **Formula**: $P(X_{t+1}\mid X_t,X_{t-1},\dots,X_0)=P(X_{t+1}\mid X_t)$. Tutta l'informazione utile sta
  nello stato corrente.
- **Tesi**: i mercati **non** sono markoviani nel prezzo (cita letteratura, non la dettaglia).
  Espandere lo spazio degli stati è legittimo, ma *"se devi risalire all'inizio del percorso non è più
  una semplificazione"*.
- **Stato**: doc (03, catena di Markov a 3 stati). **Rilevanza**: in uso.

### Il difetto del P&L aggregato
- **Tesi**: raccogliere il P&L di tutti gli ingressi dello stesso segnale in **una** distribuzione mescola
  distribuzioni condizionate diverse (il percorso che precede ogni ingresso è diverso). Un E[R] negativo
  aggregato può nascondere un sottoinsieme a E[R] positivo e uno negativo.
- **Rimedio che propone**: comprimere il percorso in **variabili di stato** (regime di volatilità,
  momentum, sentiment) e separare le distribuzioni per stato; espandere lo spazio degli stati; modelli
  più ricchi (HMM, variabili latenti).
- ⚠️ **Si rompe — e qui sta il punto per noi**: *"condiziona finché le distribuzioni si separano"* è la
  descrizione esatta di una **ricerca di massa non contabilizzata**. Ogni variabile di stato e ogni
  soglia è un trial; con abbastanza partizioni **qualunque** segnale nullo mostra un sottoinsieme
  positivo in campione. Il video non menziona mai molteplicità, holdout o pre-registrazione.
- **Condizione di validità**: la partizione dev'essere (1) **dichiarata prima** di guardare il P&L
  condizionato, (2) **calcolabile al momento dell'ingresso** (niente label same-day), (3) **contata**
  nel budget di trial, (4) confermata **fuori campione**. Senza queste, è il meccanismo che ha prodotto
  il London Breakout.
- **Stato**: la separazione per regime esiste (`core/regime.py`, `strategy_activation`); il vincolo
  "partizione = trial" è nel protocollo (STRATEGY_LIFECYCLE, contatore trial).
- **Rilevanza**: in uso → **conflitto per la mappa dei modelli** (vedi fondo).

---

## B2 — Profitable vs Tradable: Why Most Strategies Fail Live

`fzz22JNg9HE` · #96 · 32 min · 4.657 parole — **il video più utile del blocco finora**

### Profittevole vs tradabile
- **Definizione**: *profittevole* = misura all'indietro (ha guadagnato). *Tradabile* = misura in avanti:
  il meccanismo statistico da cui guadagna è **stabile**. Vale identica per il discrezionale.
- **Edge** = valore atteso positivo; **rischio** = deviazione attesa dal valore atteso.

### Stabilità delle gambe della distribuzione del P&L (aspettativa totale applicata)
- **Strumento**: scomporre $E[PnL]=P(win)E[win]+P(loss)E[loss]$ in campione e fuori campione e
  confrontare **le distribuzioni** dei vincenti e dei perdenti e le probabilità, non solo l'E[R].
- **Esempio**: strategia su NVIDIA 2020–2023 → win rate ~57%, vincita media > perdita media, E>0;
  2024–2025 → win rate simile, **forma delle distribuzioni cambiata**, E<0. Un solo titolo, una sola
  strategia non specificata: illustrazione, non evidenza.
- **Lezione**: un win rate stabile **non** dice che l'edge è stabile; la deriva può stare tutta nella
  forma delle code dei vincenti o dei perdenti.
- **Stato**: §8bis confronta forward e backtest su **drawdown e serie negative**; il confronto per gamba
  e per forma di distribuzione è **assente** (è il buco 3 del blocco A, qui con l'esempio operativo).
- **Rilevanza**: **applicabile ora**.

### Distanza fra distribuzioni come test di stabilità
- **Strumento**: divergenza di **Kullback-Leibler** (o altra distanza fra distribuzioni) fra la
  distribuzione in campione e quella fuori campione, per regime, per feature, per P&L.
- **Assunzioni**: KL richiede densità stimate (istogrammi/kernel) e supporti compatibili; è
  asimmetrica e infinita se una distribuzione ha massa dove l'altra non ne ha. Alternative più robuste
  su campioni piccoli: Kolmogorov-Smirnov a due campioni, Wasserstein, Jensen-Shannon.
- **Stato**: **assente** in core. **Rilevanza**: applicabile ora (forward vs backtest).

### Instabilità costruita dei regimi a percentile mobile
- **Strumento/diagnosi**: regime di volatilità = varianza quadratica a 20 giorni divisa in **terzili
  mobili**. Ipotesi dichiarata **prima** di guardare: i terzili estremi sono instabili **per
  costruzione** — in un periodo molto volatile il 33° percentile mobile etichetta "bassa volatilità"
  giorni che in assoluto non lo sono, e viceversa. Il terzile centrale è il più stabile.
- **Verifica nel video**: fuori campione il regime centrale mantiene l'E[R] (0,66 → 0,53) mentre gli
  estremi cambiano segno; la distanza KL delle volatilità è minima per il centrale. Un esempio, ma
  l'ipotesi era dichiarata in anticipo e il meccanismo è logico, non empirico.
- **Lezione generale**: *"la stabilità del regime sta a monte della stabilità del P&L"*. Un'etichetta
  **relativa** (percentile o rapporto su finestra mobile) cambia significato quando cambia il livello
  assoluto; il P&L condizionato a quell'etichetta eredita l'instabilità.
- **Per il repo**: `classify_volatility` etichetta "Volatile" se ATR14 > media mobile a 50 dell'ATR —
  anch'essa un'etichetta **relativa**. In un periodo prolungato ad alta volatilità circa metà dei
  giorni risulta "Quiet". Non è un errore, ma è una proprietà da dichiarare quando si condiziona su
  quel regime.
- **Stato**: assente come controllo. **Rilevanza**: **applicabile ora**.

### Stabilità delle feature a monte
- **Strumento**: prima del P&L, controllare che le **feature** che generano il segnale abbiano
  distribuzione stabile nel tempo (PCA o distribuzioni per sotto-periodo). È la prima cosa che chiede ai
  fondi da 30–100 milioni che lo consultano (aneddoto non verificabile, la richiesta è sensata).
- **HMM "che non funzionano"**: la sua diagnosi è che, stimato su periodi disgiunti, ogni stato latente
  ha distribuzioni molto diverse → parametri mal specificati per non-stazionarietà, non un difetto del
  modello in sé. Rimanda al blocco D.
- **Stato**: assente. **Rilevanza**: futuro (modelli multi-feature), applicabile ora come controllo su
  regimi.

---

## B3 — Why Trading Metrics are Misleading (Unless This is True)

`K-aUu_M02-Y` · #125 · 35 min · 5.279 parole

### Metriche inutili da sole
- **Rendimento medio**: nessuna misura di rischio, nessuna validità in avanti. Esempio NVIDIA 2025:
  media giornaliera −0,4% nel pieno dei dazi, +0,52% dopo — la media dipende dalla finestra.
- **Win rate**: da solo non dice nulla. Tre strategie simulate: 100% win rate → +2,97%; 99% → +65%;
  40% → +137%. Il 99% con coda sinistra è **vendere assicurazione** (opzioni corte, premio incassato
  finché arriva il terremoto).
- **Cassa generata al mese**: senza la dimensione del conto non dice nulla; 3.000 $/mese su un milione
  sono il rendimento dei Treasury.
- **Stato**: doc (04 regole: Sharpe primario, Omega/Tail ratio; filtro claim del funnel Chart
  Fanatics). **Rilevanza**: in uso.

### Metriche "meno inutili": necessarie, non sufficienti
- Sharpe, Sortino (penalizza solo le deviazioni negative), max drawdown: danno il profilo
  rischio/rendimento **del percorso osservato**. Ma se la media non è indicativa del futuro, non lo è
  nemmeno la deviazione dalla media, né il loro rapporto.
- **Stato**: core (`sharpe_ratio`, `sortino_ratio`, `max_drawdown`, `calmar_ratio`). **Rilevanza**: in uso.

### Stabilità in avanti come unico criterio
- **Tesi**: *"non parlo di spezzare lo storico in train e test: parlo di metterla live adesso"*.
  Esempio: backtest Sharpe 2,12 → live 1,71 = compatibile ("statistiche ragionevoli confermano");
  2,31 → 0,51 = degrado.
- **Cause di degrado elencate**: esposizione a un fattore che ha smesso di pagare, esposizione al
  mercato in fase contrattiva, **affollamento** dell'inefficienza, overfitting. Richiede monitoraggio
  continuo: *"non esiste l'hedge fund da un uomo solo set-and-forget"*.
- ⚠️ **Buco della fonte**: "statistiche ragionevoli" non è mai specificato. Quanto deve scendere uno
  Sharpe perché il degrado sia significativo dipende da quanti periodi live ci sono: con pochi mesi,
  2,12 → 0,51 può essere rumore. Serve un test con la varianza dello Sharpe stimato (PSR usato con lo
  Sharpe del backtest come benchmark, o intervallo sullo Sharpe live).
- **Stato**: doc (forward pre-registrato, §8bis, PSR in core). Il "confronto Sharpe backtest vs Sharpe
  live con la sua incertezza" non è una procedura scritta. **Rilevanza**: in uso.

---

## B4 — Stop Using the Sharpe Ratio Until You Watch This

`NJ5PNfIQHrE` · #72 · 18 min · 2.665 parole

### Lo Sharpe come compressione con perdita
- **Tesi**: media, varianza e Sharpe sono proprietà **del percorso realizzato**, non della distribuzione
  che l'ha generato. Infiniti percorsi producono le stesse statistiche; dalla statistica non si risale
  al percorso né alla sua qualità (overfit o no).
- **Due modi di fallire**: (1) **geometria** — tratta le deviazioni positive come le negative (strategia
  con Sharpe 1,5 ed E=17% contro Sharpe 1,8 ed E=8,7%: il Sortino ribalta l'ordine); (2) **stabilità in
  avanti** — la statistica vale quanto il percorso che la produce.
- **Errore della fonte**: definisce lo Sharpe come *"rapporto fra rendimento atteso e varianza"*; è la
  deviazione standard.
- **Degrado live, due spiegazioni**: rottura strutturale (possibile, va investigata) oppure — *"su cui
  scommetterei la casa"* — overfitting, snooping, survivorship, look-ahead. Coerente con la nostra
  esperienza (NXT, fill fantasma).
- **Underfit / overfit / robusto**: l'errore fuori campione del modello overfit è il peggiore; lo scopo
  del backtest è trovare il modello robusto, *"non unire i puntini"*.
- **Frase da registrare**: *"la performance live con capitale reale, per un periodo esteso, vale
  migliaia di backtest"*. Coincide con il nostro forward pre-registrato.
- **Stato**: doc (04 §2, Sortino/Omega in core). **Rilevanza**: in uso (rinforzo).

---

## B5 — Math to Increase your Sharpe Ratios

`GTVBT1SQKWY` · #27 · 18 min · 2.469 parole — **già distillato**

- $Var(R_P)=W^2\sigma_A^2+Q^2\sigma_B^2+2WQ\rho\sigma_A\sigma_B$; $\rho<1$ riduce $\sigma_P$ e alza lo
  Sharpe "per pura algebra"; l'indipendenza **fisica** implica quella stocastica, non viceversa; esempio
  NVIDIA + market making su scommesse sportive.
- Il contenuto coincide con la sezione *Orthogonal return streams* di `05_portfolio_rischio`: stessa
  derivazione, stessa distinzione, stessi esempi. **Nessuna voce nuova.**
- 🔎 **Attribuzione ricostruita in lettura**: gli appunti di questo video **sono già in `_sorgenti`**,
  `Nuove nozioni teoriche 2026-07-16.txt` righe **495–589** (*"How Physical Decorrelation Mechanically
  Improves Sharpe Ratio"*). Il PIANO li includeva per errore nel blocco "Comprehensive Guide to
  Investing" (che finisce alla riga 491). Gli appunti di #43 (`NOZIONI AGGIUNTIVE.txt`) contengono il
  concetto di indipendenza fisica/stocastica ma **non** la derivazione a tre termini: quella in 05 viene
  da qui. I video già distillati prima di questo lavoro sono quindi **9**, non 8.
- **Annotazione aggiuntiva** (non nel 05): anche due stream "fisicamente" indipendenti condividono il
  **conto**: margine, capitale, leva, controparte/piattaforma. In una crisi di liquidità il vincolo di
  capitale li lega anche se i payoff non si toccano. L'indipendenza fisica è dei payoff, non del
  finanziamento.
- **Errore della fonte**: dice che Apple e NVIDIA hanno correlazione "zero la maggior parte del tempo";
  sono due titoli tech a correlazione tipicamente alta.
- **Stato**: doc (05). **Rilevanza**: in uso.

---

## B6 — How to Trade with an Edge

`NlqpDB2BhxE` · #139 · 30 min · 5.397 parole

### Edge come prezzo contro livello atteso
- **Esempio**: mercato su un dado con bid/ask casuali intorno a 3,5. Comprare sotto 3,5 o vendere sopra =
  edge; transare a caso = deriva a zero; roulette = nessuna azione cambia l'E negativo (unica azione
  ottima: non giocare).
- **Distinzione**: gioco a distribuzione fissa (gambling) vs gioco in cui **le azioni cambiano l'E**.
- **Tesi su previsione**: *"ML e AI sono aspettative condizionate non lineari"*; senza informazione
  privilegiata non si prevede un livello, si stima un'aspettativa attorno a cui decidere.
- **Stato**: doc (04, 05). **Rilevanza**: reference.

### Media d'insieme vs percorso singolo
- Anche con edge alcuni percorsi vanno in rovina **prima** di accumulare; si vive un percorso solo.
  Rimanda a ergodicità e Kelly (blocco C).
- **Contro chi cita il TLC**: *"se la strategia è buona converge all'EV positivo"* è sbagliato — la
  convergenza richiede stabilità e sopravvivenza del percorso.
- **Stato**: doc (volatility drag, 05). **Rilevanza**: in uso.

### Edge quantitativo
- Relazione **monotona** fra quantili del segnale e rendimento medio (long il quantile alto, short il
  basso). **Scalabilità**: l'edge cala con il capitale allocato.
- **Portafoglio di strategie** con E positivo indipendenti > una strategia sola: contro la rovina del
  percorso singolo.
- **Stato**: doc parziale. **Rilevanza**: futuro (cross-section).

### Edge qualitativo
- **Tesi**: esiste (il poker: leggere il tavolo), non è strutturabile in regole.
- **Esempio**: comprare ETF quando il VIX > 30 durante i dazi 2025, in un'unica soluzione (DD 13%, poi
  112k) o a rate del 10% al giorno (DD 2%, poi 115k). **Scartato come evidenza**: un solo episodio,
  scelto a posteriori, soglia 30 non giustificata. Il meccanismo citato (effetto leva: la volatilità
  sale più in fretta di quanto scenda) è un fatto stilizzato documentato; la regola no.
- **Conflitto già mappato**: *"l'edge qualitativo esiste"* vs *"il qualitativo genera ipotesi e non
  valida"* — risolto in 04 §9 per domini ($n=1$ discrezionale vs regole ripetibili). Qui Paolucci stesso
  ammette il limite: *"questo percorso si realizza una volta sola, come un'elezione"*. Nessuna voce
  nuova.
- **Stato**: doc (04 §9). **Rilevanza**: reference.

---

## B7 — Is Trading Luck or Skill? Quant Debunks Trading Gurus with Math

`czEyUZabE2U` · #127 · 29 min · 4.541 parole

### Simulazione di trader a EV nullo e positivo (verificabile)
- **Setup**: 100 trader, 1.000 trade ciascuno, puntate additive.
  - **EV = 0**: 7 su 100 chiudono sopra +50%, con Sharpe 1,06–1,30. Nessuna differenza fra loro.
  - **EV > 0** (win rate 52%, payoff 1:1, E = +0,04R): 32 su 100 sopra +50%; **11 su 100 in perdita dopo
    1.000 trade**.
- **Verifica**: con E = 0,04R e $\sigma\approx1$R per trade, dopo 1.000 trade la somma ha media 40R e
  deviazione $\sqrt{1000}\approx31{,}6$R → $P(\text{perdita})=\Phi(-40/31{,}6)=\Phi(-1{,}26)\approx10{,}4\%$.
  **Il numero 11/100 è corretto.**
- **Il "94 su 100 sotto il capitale iniziale"** che cita è ambiguo (sotto il capitale iniziale in
  qualche momento?) e non ricalcolabile senza la size: registrato senza uso.
- **Lezione**: con 1.000 trade e un edge di 0,04R **un trader su dieci con edge vero perde**; e un
  campione di trader a EV nullo ne produce qualcuno con Sharpe > 1. Il meccanismo delle **scuole di
  trading**: con abbastanza studenti, qualcuno "funziona" per caso e diventa la vetrina
  (survivorship).
- **Collegamento**: è il buco 2 del blocco A (potenza) visto dall'altro lato. Per distinguere 0,04R da
  zero con 1.000 trade la statistica $t\approx1{,}26$: **non significativo**. Serve un campione ~2,5
  volte più grande per $t\approx2$.
- **Stato**: doc (survivorship 04 §3, DSR). La simulazione come **strumento didattico e di calibrazione
  delle aspettative** (quanta dispersione produce un edge dato) è assente. **Rilevanza**: applicabile
  ora.

### Politica ottima e dipendenza sfruttabile
- **Esempio**: roulette modificata in cui dopo un rosso è più probabile il nero; due agenti di
  reinforcement learning imparano la politica e accumulano, gli altri perdono. Edge = **dipendenza
  sfruttabile** nel processo, non distribuzione fissa. Anche con la politica ottima ci sono drawdown.
- **Stato**: reference. **Rilevanza**: reference.

### Cosa distingue un'analisi istituzionale
- Elenca: regressioni in serie storica e **Fama-MacBeth**, distinzione fra **inefficienza statistica**
  e **rischio prezzato**, pipeline dati, *"split temporali in modo casuale"* per verificare che la
  mispricing sia consistente.
- ⚠️ "Split temporali casuali" presi alla lettera introducono leakage fra periodi adiacenti; la versione
  corretta è CPCV con purging ed embargo (`cpcv_splits`, 04 §1).
- **Stato**: core (CPCV); Fama-MacBeth assente. **Rilevanza**: futuro (cross-section).

---

## B8 — Trader Skill or Market Luck? Quant Explains Alpha in 3 Minutes

`Ivz58kZLD2U` · #95 · 4 min · 641 parole

- Due fondi con Sharpe ~2,5: uno a beta alto (rendimento quasi tutto beta), uno a correlazione quasi
  nulla con il mercato (rendimento quasi tutto alpha). In un mercato ribassista il primo crolla. CAPM
  come regressione rendimento-mercato.
- **Già distillato** (05: alpha ortogonale, CAPM, beta). **Stato**: core (`benchmark_metrics`).
  **Rilevanza**: in uso.

---

## B9 — I Bet You've Never Found Alpha (and I Can Prove It)

`UzTJHs3-eT0` · #77 · 9 min · 1.161 parole

### Test "è solo beta?" su una strategia di timing
- **Esempio**: strategia a medie mobili con Sharpe ~1 → beta 1,14 sull'S&P 500; estesa a un periodo di
  forte ribasso, perde ~20% e il **beta aumenta**. Filtro di regime (catena di Markov a 3 stati di
  volatilità, trade solo in bassa volatilità): **alpha nullo e non significativo**.
- **Lezione**: un segnale di timing o un filtro di regime **non producono alpha per il fatto di stare
  fuori mercato**: se i rendimenti restano spiegati dal mercato quando si è esposti, è beta con
  pause.
- **Frase da registrare**: *"c'è una relazione inversa fra quanto è facile sviluppare un segnale e
  quanto funziona"*.
- **Stato**: core (`benchmark_metrics`), regola in 04 (*"distinguere edge reale da semplice esposizione
  direzionale"*). **Rilevanza**: in uso.

---

## B10 — What the F*ck is Alpha? (And How to Actually Find It)

`21SONVlvkDQ` · #39 · 18 min · 2.735 parole — parte promozionale (corso "personal hedge fund")

### Alpha relativo a un modello di prezzo
- **Definizione corretta**: alpha = rendimento **non spiegato da un modello di prezzo scelto**
  (intercetta della regressione), non rendimento sopra un benchmark. Soggetto a **rischio di modello**:
  aggiungendo fattori l'intercetta può sparire (problema dell'ipotesi congiunta).
- **Stato**: doc (05). **Rilevanza**: in uso.

### "La copertura produce alpha"
- **Tesi**: un portafoglio a beta positivo con una sleeve di copertura (opzioni) mostra alpha nella
  regressione CAPM su un campione che contiene un crollo, perché nel crollo non perde al ritmo del
  mercato.
- ⚠️ **Si rompe**: un payoff **non lineare** (convesso) regredito su un modello **lineare** produce
  un'intercetta che è un **artefatto di specificazione**, non abilità. Nei campioni senza crollo la
  stessa copertura produce alpha **negativo** (il premio pagato). Il modo corretto di leggerlo: beta
  condizionati al segno del mercato (downside beta) o regressioni con termine quadratico
  (Treynor-Mazuy) / opzionale (Henriksson-Merton). L'argomento valido del video è l'altro: la copertura
  riduce il drawdown e quindi il volatility drag (già in 05).
- **"Tutto è mal prezzato"**: l'esempio delle quote diverse per la stessa assicurazione auto non prova
  una mispricing (le compagnie hanno costi, modelli di rischio e clientele diverse). Claim retorico,
  non registrato.
- **Stato**: `benchmark_metrics` è lineare, nessun downside beta. **Rilevanza**: applicabile ora quando si
  misura una strategia con payoff asimmetrico (short vol, trend following con uscite convesse) contro un
  benchmark.

---

## B11 — The Math "Day Traders" Don't Want You to See

`cAFocAbUYY4` · #9 · 36 min · 5.607 parole — apre con un terminale di trading **finto** costruito in
pochi secondi, per mostrare quanto è facile fabbricare P&L

### Il valore atteso come miglior stima sotto errore quadratico
- **Formula**: $\arg\min_c E[(X-c)^2]=E[X]$. È il motivo per cui "prezzo equo = aspettativa" e per cui
  l'edge è transare lontano dall'aspettativa (dado: comprare sotto 3,5, vendere sopra).
- **Complemento non detto**: sotto errore **assoluto** la miglior stima è la **mediana**, non la media.
  Con distribuzioni asimmetriche (multipli di R, rendimenti) le due divergono, e la scelta della
  funzione di perdita decide quale "livello" si sta stimando.
- **Stato**: reference. **Rilevanza**: reference.

### Il campione non stazionario
- *"NVIDIA oggi non è la stessa azienda di 20 anni fa"*: la media su 20 anni mescola processi diversi.
  *"Quando ha senso usare quali dati è il problema canonico della finanza quantitativa."*
- ⚠️ **Conflitto con il nostro storico lungo**: vedi mappa in fondo. **Stato**: doc (memoria
  "storico lungo = laboratorio di falsificazione"). **Rilevanza**: in uso.

### Edge "amorfo" e probabilità censurate (poker)
- **Esempio**: coppia d'assi contro 4 mani casuali → win rate "circa 42%" portando sempre la mano allo
  showdown. Ma se l'avversario rilancia forte e tu foldi, **non osservi mai** se avresti vinto: la
  probabilità condizionata è **censurata** dalle tue stesse decisioni.
- ⚠️ **Numero da verificare**: le tabelle di equity comuni danno per AA contro 4 mani casuali circa il
  **56%**; il 42% corrisponde a più avversari. Non cambia l'argomento.
- **Strumento che ne viene (non nominato dalla fonte)**: **censura degli esiti**. Ogni regola di uscita
  anticipata (stop, time exit, chiusura discrezionale) rende inosservabile l'esito controfattuale del
  trade. Un'analisi che confronta "cosa sarebbe successo senza lo stop" usando solo i trade chiusi
  dallo stop è distorta per costruzione. Collegato a [[feedback_fill_ottenibile]] (anche lì il problema
  è ciò che non si poteva osservare al momento).
- **Stato**: assente come voce. **Rilevanza**: applicabile ora (analisi di MFE/MAE e di uscite
  alternative).

### Serie rare in campioni lunghi (verificabile)
- **Claim**: in **1.421** lanci di moneta la probabilità di osservare almeno una serie di 10 teste
  supera il 50%.
- **Verifica**: il tempo d'attesa atteso per 10 teste consecutive è $2^{11}-2=2046$ lanci; con attesa
  approssimativamente esponenziale la mediana è $\approx2046\ln2\approx1418$. **Il numero è corretto.**
- **Lezione**: un evento raro "per singola prova" diventa probabile quando lo si **cerca su molte
  prove** (tempo, strumenti, studenti). È il problema del *look-elsewhere*: una sequenza di trade
  vincenti, un pattern "perfetto" su un grafico lungo, un anno eccezionale di una strategia fra molte.
- **Applicazione di Paolucci**: studenti di una scuola a 50/50 con commissioni: ~27,5% chiude sopra il
  capitale iniziale e qualcuno lo quintuplica (parametri non dati, non ricalcolabile). Le
  testimonianze si scelgono fra loro.
- **Stato**: doc (DSR, molteplicità; [[feedback_mass_search_vs_preregistration]]). La formulazione
  "serie rare in finestre lunghe" non è scritta. **Rilevanza**: in uso.

### Elenco dei segnali di truffa
- "Libertà finanziaria"; concetti statistici usati male per giustificare un edge (nomina Craig Percoco
  e TJR, cioè i due video reaction #10 e #12 della lista esclusi); P&L facilissimo da fabbricare;
  payoff da biglietto della lotteria. Coerente con il filtro del funnel Chart Fanatics.
- **Stato**: doc (memoria funnel YouTube). **Rilevanza**: reference.

---

## B12 — Quant Explains Backtesting with Poker

`xJJ1nWj9Rto` · #98 · 8 min · 1.359 parole

- Stessa tesi di B1 con il poker: "entra con coppia d'assi e punta sempre" ha E>0 contro avversari
  passivi (il backtest), E<0 contro avversari che rilanciano (il live). Leva usata per recuperare:
  **ridurre la perdita media** (foldare davanti a rilanci forti), anche se la probabilità di perdere
  sale.
- **Lettura della scomposizione** $P(win)E[win]+P(loss)E[loss]$ come **quattro leve**: alzare la vincita
  media, alzare la probabilità di vincere, abbassare la probabilità di perdere, abbassare la perdita
  media.
- ⚠️ La regola "folda sui rilanci" è costruita **dopo** aver visto il live negativo: nell'esempio è
  didattica, in una strategia reale sarebbe un round di rifinitura da contare (STRATEGY_LIFECYCLE:
  massimo 3).
- **Nessuno strumento nuovo** rispetto a B1/B2. **Stato**: doc. **Rilevanza**: in uso.

---

## B13 — Analyzing Trading Strategy Performance Over Time

`boh9JkGPG9U` · #173 · 21 min · 3.525 parole

### I parametri dell'edge sono processi stocastici
- **Tesi**: $p(win)$, vincita media e perdita media non sono costanti da stimare una volta: hanno una
  **dinamica** sconosciuta e non stazionaria. Con TP e SL fissi le due medie sono fisse e resta solo
  $p$ — lo spazio si semplifica ma il problema resta.
- **Tre dinamiche simulate** (base: $p=0{,}55$, vincita 10, perdita 8):
  - **deriva lineare** $0{,}55\to0{,}40$ su 1.000 trade → l'equity si appiattisce;
  - **mean reverting** (tipo Ornstein-Uhlenbeck) verso 0,51 → cresce, ma circa la metà;
  - **deriva negativa stocastica**.
- **Diagnosi pratica**: tracciare accanto all'equity la probabilità di vincita **cumulata** nel tempo (e,
  su un altro asse, vincita e perdita medie) per vedere **quale leva** si è mossa.
- **Proposta per il ritiro**: smettere quando $p$ degrada, riprendere se torna verso una media con edge
  positivo; finestre mobili per stimare $p$; oppure stimare un processo OU su $p$ e simularlo in avanti.
- ⚠️ **Si rompe**:
  - la probabilità **cumulata** reagisce tardi (la media di tutto lo storico diluisce il cambiamento
    recente); la **finestra mobile** reagisce ma è rumorosa — con 50 trade l'errore standard di $p$ è
    ~7 punti, più grande della deriva da rilevare;
  - "spegni quando degrada, riaccendi quando torna" senza soglie fissate prima è **optional stopping
    sul capitale**: esattamente il difetto che §8bis di STRATEGY_LIFECYCLE chiude;
  - stimare un processo OU **sul parametro** stimato di un altro processo moltiplica l'errore di stima.
- **Strumento corretto (non nominato dalla fonte)**: rilevamento di cambiamento **sequenziale con
  soglie pre-registrate** — CUSUM o test sequenziale del rapporto di verosimiglianza (SPRT) sulla
  sequenza di esiti 0/1 (o sugli R), tarato perché i falsi allarmi siano rari sotto l'edge del backtest.
  Risponde alla domanda di Paolucci senza l'optional stopping.
- **Stato**: §8bis ritira su **drawdown e serie negative** fuori distribuzione; nessun monitoraggio della
  **deriva del win rate o del payoff**, nessun CUSUM/SPRT. **Rilevanza**: **applicabile ora** (forward
  segnali mentore, forward pre-registrati) → **buco** (vedi fondo).

---

## B14 — Trading with Violated Model Assumptions

`2ezWtM8J_os` · #149 · 27 min · 4.429 parole

**Tesi del video**: il modello è sbagliato per certo; conta sapere **in che direzione** ogni assunzione
violata sposta la stima. È l'estensione a tre assunzioni della "direzione dell'errore" di A3 (MLE).

### Curtosi in eccesso e VaR parametrico
- **Definizioni**: curtosi = quarto momento standardizzato; normale = 3; eccesso = curtosi − 3.
  Esempio AMZN 2021–22: curtosi 6,35 (illustrativo, un titolo e un anno).
- **Errore della fonte**: la chiama "misura di appuntimento"; la curtosi misura soprattutto **il peso
  delle code**, non la forma del picco.
- **Strumento**: **VaR parametrico normale** (media e deviazione standard) contro **VaR empirico**
  (quantile storico).
- **Risultati mostrati**: in campione il normale sbaglia in **entrambe** le direzioni a seconda del livello
  di confidenza; stimato sull'anno precedente e applicato all'anno dopo **sottostima** il VaR reale a
  ogni livello.
- **Precisazione utile**: con code grasse lo schema tipico è che la normale **sovrastima** il rischio ai
  livelli moderati (90–95%) e lo **sottostima** ai livelli estremi (99% e oltre), perché la massa si
  sposta dal centro-spalle alle code. "Sbaglia nei due sensi" è vero, ma non a caso: dipende dal
  quantile.
- **Stato**: core — `tail_metrics` (verificato: CVaR 95% e 99% da quantili **empirici**, più skew e curtosi
  in eccesso); nessun VaR parametrico da confrontare, e il confronto
  "stima su un anno, verifica sull'anno dopo" (backtest del VaR, conteggio delle violazioni) è
  **assente**. **Rilevanza**: futuro (portafoglio); applicabile ora come avvertenza su qualunque soglia
  di rischio calcolata con $\mu\pm z\sigma$.

### Indipendenza violata e PCA come correzione
- **Tesi**: quando va male, gli asset scendono **insieme** (dazi 2025, 2008); assumere indipendenza
  **sottostima** il rischio di perdite congiunte.
- **Strumento**: PCA su MSFT, AMZN, AAPL, GM → PC1 ≈ 60% della varianza (mercato, correlata allo S&P 500),
  PC2 settore, PC3 idiosincratica. Portafoglio pesato sui **loading di PC3** → correlazione mobile con
  lo S&P ≈ 0.
- **Si rompe (e lo mostra lui)**: in campione il portafoglio PC3 batte lo S&P; **fuori campione
  (2022–2025) perde** contro lo S&P, perché i loading cambiano. Inoltre pesi calcolati con la PCA
  sull'**intero** campione e applicati allo stesso campione sono look-ahead.
- **Stato**: doc (PCA in 05). **Rilevanza**: futuro (neutralizzazione fattoriale).

### Non-stazionarietà e stima della media
- **Tesi**: la media di un parametro variabile nel tempo **non ha un valore corretto**: media cumulata,
  mobile a 10 o a 30 giorni danno livelli diversi, e il VaR con finestre 30/60/120/252 giorni dà numeri
  diversi senza che uno sia "giusto".
- **Errori impilati**: media sbagliata → varianza sbagliata (dipende dalla media) → distribuzione
  sbagliata (normale) → dipendenza ignorata (i.i.d.). *"Adesso sei sbagliato due volte."*
- **Rimedio**: nessuna formula; il ciclo modellare → stimare in campione → validare → testare fuori
  campione → confrontare con modelli alternativi.
- **Stato**: doc. La scelta della **finestra di stima** come parametro (quindi come trial) non è scritta
  esplicitamente. **Rilevanza**: in uso.

### Checklist che se ne ricava (da unire ad A3)
| assunzione violata | effetto tipico sulla stima del rischio |
|---|---|
| normalità (code grasse) | sovrastima ai quantili moderati, **sottostima ai quantili estremi** |
| indipendenza fra asset | **sottostima** delle perdite congiunte in crisi |
| indipendenza nel tempo (trade o giorni raggruppati) | **sottostima** di serie negative e drawdown |
| stazionarietà | direzione non nota a priori: dipende da dove va il regime successivo |

- **Stato**: assente come checklist. **Rilevanza**: **applicabile ora** — da allegare alle
  pre-registrazioni (sezione assunzioni) e al pre-mortem di 04 §9.

---

## B15 — Why Quant Models Break (Wall Street's Dirty Secret)

`brdG1TmsPlw` · #115 · 30 min · 5.062 parole

### Sistema casuale vs sistema incerto
- **Definizione**: *casuale* = esiti e probabilità **fissi** (moneta pesata al 70%, binomiale su 10 lanci,
  media campionaria): le frequenze convergono. *Incerto* = esiti e probabilità non fissi, l'esperimento
  **non si può ripetere nelle stesse condizioni**, nessuna convergenza. È la distinzione rischio/incertezza
  di Knight, non citata per nome.
- **Tesi**: i mercati sono incerti, non casuali; per questo *"il trading non è gambling"* (il gambling è
  un sistema casuale con E negativo fisso).
- **Stato**: doc implicito (05 non-stazionarietà). **Rilevanza**: reference.

### Probabilità implicite di mercato
- **Esempio**: partita Giants–Broncos, probabilità di vittoria implicita 99,8% → 3,3% → 93,8% → sconfitta.
  Le probabilità implicite si ricavano dal **prezzo di equilibrio**, e l'equilibrio è "giusto" solo con
  agenti razionali.
- ⚠️ Il "se rigiocassimo l'ultimo quarto 10.000 volte convergerebbe a 70/30" è **inventato**: lo dice lui
  stesso che non si può rigiocare. Illustrazione, non dato.
- **Strumento corretto per la domanda (non nominato)**: la **calibrazione** — raggruppare molti eventi con
  probabilità implicita simile e confrontare con la frequenza realizzata (diagramma di affidabilità, Brier
  score). Una singola partita non dice nulla sulla calibrazione del mercato; migliaia sì.
- **Claim scartato**: *"il mercato è strutturalmente mal prezzato, altrimenti nessuno scambierebbe"*. Si
  scambia anche per copertura, liquidità, vincoli di bilancio: lo scambio non implica una mispricing.
- **Stato**: assente. **Rilevanza**: futuro (prediction market, qualunque segnale espresso come
  probabilità — anche la direzione dei segnali mentore, se un giorno venisse espressa con una confidenza).

### Perché un modello semplice si rompe
- **Esempio**: rendimenti storici di NVIDIA spezzati alla mediana → media sopra ≈ doppio della media sotto
  → "E positivo, scommettiamo la casa" → simulazione in avanti che pesca da **quella distribuzione fissa**
  → drawdown non previsto.
- **Meccanismo**: la distribuzione che genera i dati **si sposta** (media e varianza) guidata da processi
  latenti (volatilità); campionare dallo storico come se fosse fisso assume la stazionarietà.
- **Per noi**: vale per **ogni bootstrap o Monte Carlo** che ricampiona trade o rendimenti storici,
  compreso quello che fissa le soglie di ritiro in §8bis. Il block bootstrap preserva la dipendenza a
  breve, **non** i cambi di regime più lunghi del blocco. Le soglie così ottenute sono un pavimento, non
  un intervallo garantito.
- **Stato**: doc parziale (04 §2b dice cosa misura il Monte Carlo, non questo limite). **Rilevanza**:
  applicabile ora.

### Eventi "a 20 sigma" e fattori esogeni
- **2008**: il modello di rischio segna un salto di ~20 deviazioni standard; chi ha guadagnato (CDS, *The
  Big Short*) aveva modellato un **fattore esogeno** assente nei modelli delle banche.
- **Lettura corretta**: un evento a 20σ sotto normalità ha probabilità praticamente nulla; osservarlo è
  **prova che il modello è sbagliato**, non che è capitato l'impossibile. Si collega a curtosi (B14) e a
  momenti infiniti (A8).
- **Stato**: doc (05 tail risk). **Rilevanza**: reference.

### Perché modellare comunque
- *"Se conoscessimo la dinamica non servirebbe un modello"*; chi ha una funzione di business **deve
  agire**, e un modello sbagliato ma esplicito informa meglio di nessun modello. Obiettivo: accumulare
  valore atteso su molte decisioni piccole e indipendenti, **non prevedere** un evento.
- **Stato**: doc (principio del repo). **Rilevanza**: reference.

---

## B16 — Non-Stationarity and Why Market Timing Fails

`7nvjrgqKjJE` · #80 · 31 min · 4.685 parole

### Tre passi fuori dall'aula (mercato su un dado)
1. **Distribuzione nota**: fair value 3,5, si transa solo attorno → equity che cresce.
2. **Distribuzione stimata dai dati**: con **50 lanci** la media stimata è 3,66 → l'edge sparisce; con molti
   più lanci la stima converge (LGN) e l'edge torna.
3. **Distribuzione che cambia**: dopo un po' il dado diventa a 10 facce; chi continua a quotare sul dado a 6
   perde molto.
- **Il problema di rilevamento**: un 5 può venire da entrambi i dadi; il cambio non si vede in un singolo
  esito. *"Quando aggiornare la stima? Quanti dati usare?"*

### Il compromesso sulla finestra di stima
- **Strumento (implicito nei passi 2 e 3)**: finestra lunga = stima precisa se il processo è fermo, **stantia**
  se è cambiato; finestra corta = reattiva ma rumorosa. Non esiste una lunghezza giusta indipendente dal
  tasso di cambiamento del processo.
- **Per noi**: è lo stesso compromesso di B13 (monitoraggio di $p$) e di B14 (VaR con finestre diverse). La
  lunghezza della finestra è un **parametro**, quindi un trial.
- **Stato**: assente come voce. **Rilevanza**: applicabile ora.

### "Stabilità, non stazionarietà"
- **Tesi**: la stazionarietà è un'assunzione d'aula; nel mondo reale si cerca **stabilità**: la strategia
  regge a **perturbazioni dei parametri** e a **ricampionamenti fra regimi**; se si rompe, si deve poter
  modellare la rottura e ritrovare stabilità.
- **Stato**: doc (04 §2: instabilità parametrica = NO-GO; walk-forward). **Rilevanza**: in uso (rinforzo).

### Code grasse come mescolanza di regimi
- **Esempio**: rendimenti SPY, normale stimata su tutto lo storico → la probabilità di un evento a −3σ è molto
  sotto quella della stima kernel empirica.
- **Meccanismo proposto**: la distribuzione "statica" è la **compressione** di distribuzioni diverse nel
  tempo (bassa, media, alta volatilità). **Fatto matematico corretto**: una mescolanza di normali con
  varianze diverse ha curtosi maggiore di 3 anche se ogni componente è normale. Le code grasse aggregate
  **possono** nascere da regimi, non necessariamente da code grasse dentro ciascun regime.
- **Conseguenza**: condizionare al regime **giusto** può ridurre la curtosi osservata; modelli citati: catene
  di Markov, HMM, mescolanze gaussiane (blocco D).
- **Stato**: doc parziale (05 tail risk "regime-condizionale"). **Rilevanza**: applicabile ora (lettura dei
  multipli di R per regime).

### "Non si può rendere stazionario ciò che non lo è" e "i test di stazionarietà sono senza senso"
- ⚠️ **Confusione di termini nella fonte**. Parla di non-stazionarietà **strutturale** (il processo
  generatore cambia per cause reali) e ha ragione che nessuna trasformazione la elimina e che un test su un
  campione non certifica il futuro. Ma nel senso tecnico — processi con **radice unitaria** — differenziare
  (prezzi → rendimenti) **rende** la serie stazionaria, ed è ciò che il blocco D (#222, *Why are Unit Roots
  Important?*) insegna. Un test ADF/KPSS risponde a una domanda **stretta e utile** (c'è una radice
  unitaria in questo campione? i residui di questa coppia sono stazionari?), non a "la strategia resterà
  stabile".
- **Condizione**: il test di stazionarietà vale **per la proprietà che testa e sul campione su cui è
  fatto**; non vale come garanzia di stabilità futura. Vedi mappa in fondo.
- **Stato nel repo — la parola è usata in due sensi diversi**:
  - il test **W3 "stazionarietà"** della pre-registrazione del playground trend (e H3 in `analysis/nxt`)
    spezza il campione pre/post-2020: è un test di **stabilità** nel senso di Paolucci, non di
    stazionarietà statistica. Il contenuto è giusto, il nome confonde;
  - `agents/quant_reviewer.md` riga 174 propone **ADF/KPSS sui rendimenti** per stimare *"quanto durano i
    regimi"*: i rendimenti passano quasi sempre l'ADF, e il test non dice nulla sulla durata dei regimi.
    È un uso fuori dalla domanda a cui il test risponde.
- **Rilevanza**: applicabile ora (terminologia dei documenti di pre-registrazione; correzione della riga del
  reviewer da valutare in SINTESI).

---

## B17 — Expected Stock Returns Don't Exist

`iXNSBn5xqrA` · #152 · 24 min · 4.295 parole

### Il rendimento atteso come processo stocastico
- **Tesi**: ottimizzazione di portafoglio, CAPM, VaR, drift di Black-Scholes richiedono tutti un rendimento
  atteso; i corsi assumono **stazionarietà debole**, che garantisce che la media esista e sia costante. Nei
  dati non è così.
- **Esempio**: media cumulata dei rendimenti giornalieri di NVIDIA. Su tutta la vita del titolo sembra
  assestarsi (per effetto della volatilità iniziale), ma **dentro** il 2008, il 2016, il 2024 e il 2025 non
  converge: chi avesse fissato la media a inizio anno sarebbe stato smentito a fine anno.
- **Conseguenza dichiarata**: se la media è un processo, lo sono anche i momenti superiori che la usano.
  Nessuna finestra "giusta"; opzioni: **filtro di Kalman** sul livello atteso, modelli a regimi, GARCH
  (blocco D). *"Non prevediamo i rendimenti, stimiamo il livello atteso."*
- **Stato**: doc (05 non-stazionarietà). **Rilevanza**: in uso.

### Media d'insieme vs media temporale (ergodicità) — verificato
- **Gioco additivo**: dado, +1 $ con il 6, −0,20 $ altrimenti → $E=1/6-0{,}2\cdot5/6=0$. Media d'insieme e
  media temporale coincidono: processo **ergodico**.
- **Gioco moltiplicativo**: moneta, ×1,5 con testa, ×0,6 con croce → moltiplicatore atteso **1,05**, ma
  fattore di crescita del singolo percorso $\sqrt{1{,}5\cdot0{,}6}=\sqrt{0{,}9}\approx0{,}949<1$. La media
  d'insieme cresce, **quasi tutti i percorsi vanno a zero**, pochi percorsi concentrano la ricchezza:
  **non ergodico**. (Esempio classico di Ole Peters, non citato.)
- **Per noi**: l'E[R] in multipli di R è una media **d'insieme e additiva**; appena la size è una frazione
  dell'equity la ricchezza è moltiplicativa e conta la **media temporale** ($\approx\bar R-\sigma^2/2$).
  È già in 05 (volatility drag); la formulazione ergodica e il sizing ottimo stanno nel blocco C.
- **Stato**: doc (05). **Rilevanza**: in uso.

### Media che non esiste (San Pietroburgo, di nuovo)
- Stesso contenuto di A8; aggiunge che il prezzo del gioco richiede una **funzione di utilità** (preferenze
  al rischio), *"insoddisfacente ma inevitabile"*. Nessuna voce nuova.

### Conflitto con il nostro uso di E[R]
- *"Il rendimento atteso non esiste"* **vs** ogni pre-registrazione del repo, che stima un E[R] e ne fa la
  soglia di verdetto. **Non si contraddicono** se l'E[R] è letto per quello che è: la **media locale su una
  finestra dichiarata**, e se la verifica decisiva è la sua **stabilità fra finestre disgiunte** (W3
  pre/post-2020, holdout, forward). Diventa un errore quando l'E[R] del backtest è usato come parametro
  fisso del futuro (sizing, soglie di ritiro) senza intervallo né controllo di deriva — vedi B13.
- **Stato**: implicito. **Rilevanza**: in uso → nota per la mappa dei modelli.

---

## B18 — Information and Stock Price Prediction

`df9arrckvL8` · #159 · 19 min · 3.267 parole

### Nessuna informazione, nessun modello
- **Esempio**: S&P 500, rendimento di ieri → rendimento di oggi. Il grafico a dispersione è una **nuvola**
  senza pendenza: condizionando a "ieri = 0" i punti di oggi stanno sopra e sotto lo zero in modo simmetrico.
  Regressione lineare e rete neurale, con split temporale train/test: entrambe falliscono fuori campione.
- **Lezione**: *"nessun modello, per quanto complicato, genera potere predittivo dal nulla"*. Il lavoro vero
  è trovare **informazione rilevante** (dati alternativi, spiegazione economica), non aumentare la
  complessità. La rete neurale **fitta il rumore meglio** in campione e fa **peggio** fuori.
- **Distinzione utile che fa**: relazione **contemporanea** (inflazione sotto le attese → rendimento dello
  stesso giorno) vs **predittiva** (ritardata). Solo la seconda è tradabile; confonderle è look-ahead.
- **Claim registrato senza verifica**: *"non c'è modo che le bande di Bollinger abbiano potere predittivo"*.
  Coerente con il NULL della ricerca livelli del repo, ma nel video non è testato.

### ⚠️ L'errore di lettura dei numeri
- **Numeri mostrati**: MSE in campione 0,99 (regressione) e 0,95 (rete); fuori campione **33,50** e **33,75**.
- **Perché "overfitting" non li spiega**: una regressione con un regressore e previsioni vicine a zero non può
  produrre un errore fuori campione **33 volte** quello in campione per overfitting. Con previsioni ≈ 0,
  $MSE\approx Var(\text{target})$: il salto dice che **la varianza del periodo di test è ~33 volte quella del
  periodo di train**, o che le due parti sono su scale diverse (per esempio target standardizzato con le
  statistiche del solo train, test che contiene un periodo molto volatile). È **cambio di distribuzione o
  di scala**, non apprendimento del rumore. La conclusione del video (nessun potere predittivo) resta
  giusta; la diagnosi no.
- **Strumento corretto (non nominato)**: confrontare il MSE del modello con quello di un **previsore
  ingenuo** sullo **stesso** periodo di test (zero, o media storica) → **$R^2$ fuori campione**
  (Campbell-Thompson): $R^2_{OOS}=1-MSE_{modello}/MSE_{ingenuo}$. Un MSE assoluto confrontato fra periodi
  diversi non dice nulla. È l'equivalente, per le previsioni, del nostro **baseline random risk-matched** per i
  trade ([[feedback_r_multiple_ceiling_baseline]]).
- **Stato**: baseline random nel protocollo (G1/G2); $R^2$ fuori campione contro previsore ingenuo
  **assente** (non abbiamo modelli predittivi di rendimento in uso). **Rilevanza**: futuro (qualunque
  modello di previsione); il principio "confronta sempre con il baseline sullo stesso periodo" è in uso.

---

## B19 — Quant Busts 3 Trading Myths with Math

`wJfIk3VnubE` · #117 · 33 min · 5.228 parole — in gran parte **ripetizione** di B3, B6, B15, B17

### Mito 1: "il trading è gambling, il mercato è casuale"
- Stessa distinzione casuale/incerto di B15 e gioco d'azzardo/gioco a informazione incompleta di B6–B7.
  Roulette americana: E = −5,26% della puntata ($-2/38$), verificato. Evento di utili con probabilità
  implicita 60/40 "simulato 10.000 volte con una macchina del tempo": illustrazione inventata, come B15.
- **Nessuna voce nuova.**

### Mito 2: "basta avere ragione il 50,5% delle volte"
- Win rate da solo irrilevante (B3). Aggiunge il confronto **ergodico vs non ergodico** a E positivo: nel
  sistema ergodico ~56–60% dei trader in profitto e vicini alla retta attesa; nel non ergodico **solo ~20%**,
  perché l'E è dominato da pochi percorsi fortunati → *"il caso medio non è il valore atteso"* (mediana ≠
  media). Percentuali non ricalcolabili (parametri non dati); il meccanismo è quello verificato in B17.
- **Nessuna voce nuova** (blocco C per il sizing).

### Mito 3: "le strategie sono fisse, funzionano sempre, nessuno condivide quelle profittevoli"
- **Funzione di policy** $\pi^*$: l'insieme di azioni che massimizza il rendimento corretto per il rischio,
  condizionato all'ambiente. Non è una strategia fissa; si ritirano le alpha morte e si **riattivano** quando
  tornano stabili.
- **Condividere classi di strategie** (mean reversion, volatilità sopravvalutata, momentum, sentiment) non
  affolla l'alpha a scala retail; l'affollamento è un problema di capitale istituzionale (non-compete,
  garden leave).
- ⚠️ "Riattivare le alpha quando tornano stabili" senza regole fissate prima = optional stopping (B13). §8bis
  di STRATEGY_LIFECYCLE prevede incubazione e riattivazione **pre-dichiarate**: coerente solo in quella forma.

### Il claim che conta: *"l'analisi tecnica non si può smentire con un semplice backtest"*
- **Argomento**: un indicatore non va giudicato da solo ma come **componente** di $\pi^*$; esempio del poker —
  coppia d'assi contro 5 avversari vince incondizionatamente meno del 50%, ma con bluff e lettura del tavolo il
  giocatore porta il risultato a 60/40.
- ⚠️ **Si rompe**: presa alla lettera la frase è **non falsificabile** — nessun test potrebbe mai bocciare
  una componente, perché si può sempre dire che il test non la usava "nella policy giusta". Il modo corretto di
  valutare una componente di una policy esiste ed è standard: **ablazione pre-registrata** — la stessa policy
  **con e senza** la componente, sugli stessi dati, confrontate con il baseline. Se la componente non aggiunge
  valore incrementale, non è una componente utile.
- **Conflitto con il repo** (mappa dei modelli): i 384 trial della ricerca livelli (NULL) hanno testato i
  livelli **incondizionatamente**, e la riapertura richiede **evidenza esterna nuova e quantitativa**
  ([[project_level_research_v1_null_2026_07_06]], STRATEGY_LIFECYCLE). Questo video **non** è evidenza nuova:
  è un argomento di principio senza dati. Condizione di validità del claim: vale come avvertenza metodologica
  ("un test incondizionato non chiude i test condizionati"), **non** come ragione per riaprire una famiglia
  chiusa. È la stessa risposta data a Brando e a Trader Mayne nel funnel Chart Fanatics (blocco C1): buco noto,
  non proposta; se mai si riaprisse, una volta sola e con un'ablazione.
- **Stato**: principio di riapertura doc (STRATEGY_LIFECYCLE); l'ablazione come formato di test di una
  componente **non è scritta**. **Rilevanza**: applicabile ora (qualunque filtro aggiunto a una regola
  esistente).

---

## B20 — Is Trading Gambling? Quant Proves It's Not With Math & Logic

`GvX8Ragl3ZU` · #113 · 36 min · 5.774 parole — in gran parte **ripetizione** di B6, B7, B15, B19

### Definizione formale di gambling
- **Formula**: un sistema è gioco d'azzardo se $E[\text{ricchezza}\mid\pi]=E[\text{ricchezza}]$ **per ogni
  policy** $\pi$, ottima compresa, ed è negativo e fisso: nessuna azione cambia la traiettoria attesa (roulette,
  slot, lotterie, craps). In un gioco a informazione incompleta $E[\cdot\mid\pi^*]\neq E[\cdot]$: le azioni
  cambiano l'aspettativa (poker, scommesse sportive ed elettorali, trading — e, provocatoriamente, fare la spesa:
  prezzo incerto, policy "compro solo ciò che serve al prezzo minimo", scorte quando c'è lo sconto).
- **Utilità**: è un criterio operativo per una domanda che torna spesso — *"questa strategia è d'azzardo?"* —
  riformulata come *"la sua aspettativa dipende dalle regole di decisione o no?"*. Una regola il cui E[R] non
  si distingue dall'ingresso casuale risk-matched è, in questo senso, gambling.
- **Stato**: implicito nel baseline random del protocollo. **Rilevanza**: reference.

### Convergenza delle probabilità come medie di Bernoulli
- Qualunque probabilità di evento è la media di un indicatore 0/1, quindi la LGN sulla media implica la
  convergenza delle probabilità empiriche e della distribuzione: è ciò che giustifica il **Monte Carlo** per
  eventi composti complicati (blocco F).
- **Stato**: doc implicito. **Rilevanza**: reference.

### Market making sul dado e il compromesso spread / esecuzione
- **Esempio**: fair value 3,5, quotazione denaro 2 / lettera 4. ⚠️ Il video dice "edge 0,5 per trade": vale per
  il lato **vendita** (vendo a 4, valore atteso 3,5); sul lato **acquisto** (compro a 2) il vantaggio è **1,5**.
  L'edge medio dipende da come arrivano le controparti.
- **Strumento**: il valore atteso della policy è **concavo** nell'ampiezza dello spread — più largo aumenta il
  guadagno per esecuzione ma **riduce la probabilità di esecuzione**, fino a nessuna controparte:
  $E[\text{quota}]=\text{vantaggio}\times P(\text{esecuzione}\mid\text{vantaggio})$.
- **Collegamento diretto al repo**: è la stessa struttura del **fill fantasma**
  ([[feedback_fill_ottenibile]]). Un edge misurato solo sugli ordini **eseguiti**, senza modellare che i prezzi
  più favorevoli si eseguono meno e peggio (selezione avversa: si viene eseguiti proprio quando il prezzo sta
  andando oltre), è sovrastimato per costruzione.
- **Stato**: la lezione è in memoria e nei verdetti NXT/FADE; la formula
  $\text{vantaggio}\times P(\text{esecuzione})$ e la selezione avversa **non sono scritte** in
  `fondamenti_tecnici/`. **Rilevanza**: **applicabile ora** (qualunque strategia a ordini limite).

### Il resto
- Sistema casuale vs incerto, nessuna convergenza nei mercati, $\pi^*$ variabile nel tempo, *"non esiste la
  strategia gallina dalle uova d'oro"*: già in B6, B13, B15, B19. **Nessuna voce nuova.**

---

## B21 — Is Quant Trading Gambling? Roulette, Poker, and Trading

`fI3UHYD389g` · #147 · 17 min · 2.908 parole — il video più vecchio della serie "gambling"; B6, B7, B19, B20
ne sono le versioni successive

### Equazione di Bellman come criterio di "struttura"
- **Formula** (non scritta nel video, solo descritta): $V(s)=\max_a\,E\left[r(s,a)+\gamma V(s')\mid s,a\right]$ —
  valore di uno stato = migliore azione in termini di ricompensa immediata più valore scontato dello stato
  successivo. Ingredienti: **stato** (mano, flop, avversari, bankroll), **azioni** (call, raise, fold / hedge,
  hold, aumentare la size), **ricompensa** (P&L).
- **Uso che ne fa**: un agente di reinforcement learning messo alla roulette **non impara nulla** (nessuna azione
  cambia la ricompensa attesa); al poker sì. Quindi *"un agente che impara"* è evidenza di **struttura
  sfruttabile**.
- ⚠️ **Condizione**: vale solo se l'agente batte il caso **su dati non usati per addestrarlo**. Un agente di RL è
  il più potente cercatore di overfitting che esista: in campione "impara" sempre qualcosa, anche sul rumore
  (B18: la rete neurale fitta il rumore meglio della regressione).
- **Riferimento**: Hans Buehler et al., *Deep Hedging* e *Deep Bellman Hedging* — il RL per coprire opzioni in
  mercati con attriti (gruppo 2).
- **Stato**: assente. **Rilevanza**: futuro (RL, gruppo 2); reference.

### Discrezionale vs algoritmico: adattività
- **Tesi**: l'algoritmo elimina l'emozione ma segue **regole fisse** che si adattano lentamente all'ambiente; il
  discrezionale si adatta subito ma porta avversione alle perdite ed errori emotivi. *"Il quant non è
  arbitrariamente migliore, è diverso."* Esistono ibridi.
- **Collegamento**: è la tensione della traccia mentore (discrezionale copiato, [[project_mentor_signals_edge_2026_07_08]])
  contro le regole sistematiche. Già risolta nel repo per domini (04 §9). **Nessuna voce nuova.**
- **Uso dello storico**: *"i dati storici servono poco a stimare livelli, molto a imparare comportamenti ottimali
  sotto incertezza"*. Coerente con la memoria sullo storico lungo (falsificare, non stimare parametri fissi).

### La versione forte del claim sull'analisi tecnica
- *"Non si può dimostrare né smentire: può funzionare molto bene **per titoli specifici in momenti specifici**, poi
  smettere quando la usano in tanti, poi tornare."*
- ⚠️ **Si rompe**: "funziona su qualche titolo in qualche periodo" è **esattamente** ciò che produce una ricerca su
  molte coppie (titolo, periodo) **senza** contabilizzare la molteplicità — il look-elsewhere verificato in B11 (in
  1.421 lanci una serie di 10 teste è più probabile che no). Una affermazione che nessun risultato può smentire non
  è una tesi empirica. Si somma al conflitto già registrato in **B19**; stessa condizione: avvertenza metodologica,
  non evidenza per riaprire famiglie chiuse.
- **Stato**: conflitto mappato (B19). **Rilevanza**: in uso.

---

## B22 — How to Make & Lose Money Trading

`WP9fb7AMFsI` · #174 · 23 min · 3.826 parole — versione precedente di B13 (stessi due problemi, stessa scomposizione)

### Problema 1: stima dei parametri su campioni piccoli
- **Esempio**: 10 lanci di una moneta equa → 2 teste → stima $\hat p=0{,}2$. *"Gli ultimi 10 giorni di trading
  accadono una volta sola, non si ripetono."* Strumenti citati e non sviluppati: intervalli di confidenza,
  simulazione, riduzione della varianza.
- **Stato**: core (bootstrap, BCa). **Rilevanza**: in uso.

### Problema 2: il parametro cambia nel tempo
- Stessa tesi di B13: $p$ come funzione aleatoria del tempo; stime sopra e sotto il vero a seconda del momento;
  cita volatilità locale e stocastica come modelli di parametri variabili (gruppo 2).
- **Nessuna voce nuova** rispetto a B13.

### L'esempio numerico — verificato, e più istruttivo di quanto il video dica
- **Dati**: 7 trade, 4 vincenti (+150, +120, +90, +100 → media +115) e 3 perdenti (media −150).
  $E=\tfrac47\cdot115-\tfrac37\cdot150\approx+1{,}43$ (il video dice 1,42). **Corretto.**
- **Cosa fa il video**: simula 252 giorni **usando quei parametri come se fossero veri** → a volte −3.000, a volte
  +750; per "vedere la deriva" deve arrivare a 100.000–1.000.000 di passi.
- ⚠️ **Due lezioni che il video non esplicita**:
  1. **Dimensione campionaria.** Con perdite e vincite dell'ordine di ±150 la deviazione standard per trade è
     circa 135. Per distinguere $E=+1{,}43$ da zero con $t\approx2$ servono
     $n\approx(2\sigma/E)^2=(2\cdot135/1{,}43)^2\approx36.000$ trade. È la formula
     $n\approx(z\,\sigma/E)^2$ che manca alle nostre pre-registrazioni (**buco 2**, blocco A): un edge piccolo
     rispetto alla dispersione **non è misurabile** in nessun orizzonte realistico, e il rapporto $E/\sigma$ per
     trade andrebbe dichiarato prima di scegliere la finestra del test.
  2. **Simulazione plug-in.** Simulare con parametri stimati su 7 osservazioni come se fossero noti **ignora
     l'incertezza di stima**: le curve simulate sono troppo ottimiste. La versione corretta ricampiona anche i
     parametri (bootstrap dei trade, o distribuzione a posteriori) prima di simulare i percorsi.
- **Slider interattivo** (win rate 80%, vincita 115 o 10, perdita 150): i valori di edge mostrati a schermo non
  coincidono con quelli ricalcolabili dai numeri detti a voce (es. $0{,}8\cdot10-0{,}2\cdot150=-22$, il video
  mostra −17). Il punto qualitativo regge: 80% di vincite con vincita piccola e perdita grande = edge negativo.
- **Stato**: la scomposizione è doc implicito; **formula della dimensione campionaria** e **simulazione con
  incertezza sui parametri** assenti. **Rilevanza**: **applicabile ora** (pre-registrazioni; soglie di ritiro
  §8bis, che prendono il percentile del maxDD dal Monte Carlo del backtest: rimescolare **gli stessi trade**
  lascia invariata la media, quindi l'incertezza sull'E[R] stimato non entra nella soglia).

---

## B23 — The Mathematical Delusion of Retail Trading

`RBfc8SkRwwU` · #53 · 13 min · 2.263 parole — apre con un finto trade "da guru" sugli utili Apple; parte
promozionale (discourses.io)

### Nessun controfattuale: l'edge di un singolo trade non esiste
- **Tesi**: dell'evento utili si realizza **un** percorso; se lo si potesse rigiocare mille volte, quel gap al rialzo
  potrebbe essere l'unico caso fortunato. *"Edge in un singolo trade non equivale a edge nel tempo."*
- **Bias nominato senza nome**: dopo un esito favorevole si vuole aver avuto ragione → si conferma la tesi
  (conferma / *resulting*, giudicare la decisione dall'esito). Una regola a E negativo può produrre una
  serie di esiti che la "confermano".
- **Stato**: doc (04 §2, pre-registrazione). **Rilevanza**: in uso.

### Il numero di ingressi e uscite possibili dentro una barra
- **Claim**: in una sola candela oraria di un titolo liquido come Apple ci sono **oltre 6 milioni** di combinazioni
  di ingresso e uscita. *"Quando entri e perché?"*
- **Verifica di ordine di grandezza**: con $n$ prezzi eseguiti distinti nell'ora, le coppie ingresso-prima-di-uscita
  sono $\approx n^2/2$; $n\approx3.500$ dà $\approx6$ milioni. **Plausibile.**
- **Lezione per noi**: un backtest su barre OHLC **non definisce l'esecuzione** dentro la barra; ogni ipotesi su
  dove si entra ed esce nella barra è una scelta (e un trial). È la radice del fill fantasma: il fill a un livello
  che la barra ha toccato non dice che era ottenibile ([[feedback_fill_ottenibile]]).
- **Stato**: lezione in memoria e nei verdetti; la formulazione "l'OHLC lascia l'esecuzione indefinita" non è in
  04. **Rilevanza**: in uso.

### Analisi tecnica, terza volta
- *"Liquidarla del tutto perché suona ridicola è altrettanto ridicolo: può avere merito dentro l'aspettativa amorfa
  del P&L; è una domanda di ricerca."* Formulazione più moderata di B19/B21 — ammette che è **una domanda di
  ricerca**, cioè da testare. Coerente con la condizione già registrata in B19 (ablazione, evidenza nuova).

### ⚠️ Errore della fonte contro la sua stessa lezione (covered call)
- **Claim**: *"la covered call limita l'upside" è una critica arbitraria: se il titolo scende, non l'ha limitato*.
- **Si rompe**: "limita l'upside" è una proprietà della **distribuzione** del payoff (taglia la coda destra), vera per
  costruzione; che un **singolo percorso** realizzato non tocchi il tetto non la smentisce. È la confusione
  percorso/distribuzione che Paolucci stesso corregge in A6 (le statistiche sono variabili aleatorie) e B4 (lo
  Sharpe è una proprietà del percorso, non del processo). Registrato come esempio di come la lezione vada
  applicata anche alle sue conclusioni.

---

## B24 — When Does a Trading Strategy Actually Need to be Secret?

`WsEwKlr_1lA` · #34 · 20 min · 2.951 parole — parte promozionale (corso "personal hedge fund")

### Allocazione vs alpha: cosa ha senso tenere segreto
- **Allocazione** = esporsi a un **premio per il rischio documentato**: mercato, premio per la varianza (vendere
  assicurazione), small-minus-big, high-minus-low, momentum. È "il vento che soffia": nessuno sa da che parte,
  tutti sanno che esiste. **Nulla da tenere segreto** — un'esposizione di beta non diventa alpha perché la si tiene
  nascosta, né perché si fanno molti trade (esempio: strategia che in un mercato rialzista batte l'indice ma
  regredita sul mercato è beta con leva, drawdown 60–80% nel ribasso).
- **Alpha che va tenuto segreto** = un'inefficienza o un premio **non documentato** (dati difficili da raccogliere,
  un segnale che vede solo tu, market making come funzione di servizio). **Si esaurisce quando diventa noto.**
  Metafora: il battitore che vede i segnali del lanciatore al ricevitore.
- **Modelli fattoriali**: *"spiegano i rendimenti, non li prevedono"*.
- **Collegamento non citato**: il decadimento dei premi dopo la pubblicazione è documentato in letteratura
  (McLean e Pontiff, 2016). Per noi: una regola presa da una fonte pubblica parte già da un premio parzialmente
  arbitraggiato — un motivo in più per il baseline e per l'holdout.
- **Stato**: doc (05 alpha, CAPM, estensioni). La distinzione allocazione/alpha come criterio per classificare una
  strategia **non è scritta** in questi termini. **Rilevanza**: applicabile ora (classificare cosa è davvero il
  lead del playground trend: premio di momentum/trend documentato o inefficienza?).

### Claim registrati senza uso
- **"Il fattore sentiment ha correlazione ~0 con il mercato"** e **"con dati sufficienti se ne prevede in parte la
  direzione"**: rimanda alla sua ricerca, non verificabile qui.
- **"Strategia segreta con alpha annuo 10–12% invariato in ogni regime"**: simulazione illustrativa.
- **"La copertura produce alpha nella crisi"**: ripete B10, stesso artefatto di un modello lineare su payoff
  convesso. Il punto valido resta la riduzione del drawdown (maxDD dimezzato nella sua simulazione).

---

## Sintesi del blocco

> Lettura completa B1–B24. Le righe sono in ordine di video; B23 e B24 in fondo alla tabella.

| strumento | video | stato | rilevanza | destinazione proposta |
|---|---|---|---|---|
| P&L aggregato vs condizionato; **ogni partizione è un trial** | B1, B12 | doc (contatore trial) | in uso | 04 + mappa |
| proprietà di Markov, espansione dello spazio degli stati | B1 | doc (03) | in uso | 03 |
| stabilità **per gamba** (distribuzioni di vincenti e perdenti, $p$) fra campione e fuori | B2, B12 | **assente** | applicabile ora | STRATEGY_LIFECYCLE §8bis |
| distanza fra distribuzioni (KL, KS a due campioni, Wasserstein) | B2 | **assente** | applicabile ora | core + §8bis |
| instabilità costruita delle etichette di regime **relative** | B2 | **assente** (`classify_volatility` è relativa) | applicabile ora | 03 + docstring `core/regime.py` |
| stabilità delle feature a monte del P&L | B2 | assente | futuro | 04 |
| win rate, cassa, media: inutili da soli | B3 | doc | in uso | — |
| Sharpe backtest vs live **con la sua incertezza** | B3 | parziale (PSR) | in uso | §8bis |
| Sharpe come compressione con perdita; underfit/overfit/robusto | B4 | doc | in uso | — |
| varianza a tre termini, indipendenza fisica; **vincolo di finanziamento comune** | B5 | doc (05) | in uso | 05 (annotazione) |
| edge = prezzo contro livello atteso; media d'insieme vs percorso | B6, B17 | doc (05) | in uso | 05 / blocco C |
| simulazione della dispersione prodotta da un edge dato | B7 | assente | applicabile ora | 04 |
| Fama-MacBeth; rischio prezzato vs inefficienza | B7 | assente | futuro | 05 |
| test "è solo beta?" su strategie di timing e filtri di regime | B8, B9 | core (`benchmark_metrics`) | in uso | — |
| alpha lineare su payoff convesso = artefatto; downside beta, Treynor-Mazuy, Henriksson-Merton | B10 | **assente** | applicabile ora | 05 + core |
| miglior stima: media (perdita quadratica) vs mediana (assoluta) | B11 | — | reference | 04 |
| **esiti censurati** dalle regole di uscita | B11 | assente | applicabile ora | 04 |
| serie rare in campioni lunghi (look-elsewhere), verificato | B11 | doc parziale | in uso | 04 §2 |
| parametri dell'edge come processi; **CUSUM / SPRT** con soglie pre-registrate | B13 | **assente** | applicabile ora | §8bis + core |
| direzione dell'errore per assunzione violata (checklist, con A3) | B14 | assente | applicabile ora | template pre-registrazione, 04 §9 |
| VaR parametrico vs empirico; backtest del VaR | B14 | parziale (`tail_metrics`) | futuro | 05 |
| PCA per neutralizzare fattori; look-ahead dei loading | B14 | doc (05) | futuro | 05 |
| sistema casuale vs incerto; **calibrazione** di probabilità (Brier, affidabilità) | B15 | assente | futuro | 04 |
| limite di bootstrap e Monte Carlo sotto cambio di regime | B15 | doc parziale (04 §2b) | applicabile ora | 04 §2b, §8bis |
| compromesso sulla lunghezza della finestra di stima | B16 | assente | applicabile ora | 04 |
| code grasse come mescolanza di regimi | B16 | doc parziale (05) | applicabile ora | 05 |
| stazionarietà in senso tecnico vs strutturale | B16 | **incoerenza terminologica** | applicabile ora | pre-registrazioni, `agents/quant_reviewer.md` |
| ergodicità: gioco additivo vs moltiplicativo (verificato) | B17 | doc (05) | in uso | blocco C |
| $R^2$ fuori campione contro previsore ingenuo; contemporaneo vs predittivo | B18 | assente | futuro | 04 |
| **ablazione pre-registrata** per valutare una componente di una policy (con/senza, stessi dati, contro baseline) | B19, B21 | **assente** come formato | applicabile ora | STRATEGY_LIFECYCLE |
| definizione formale di gambling: $E[\cdot\mid\pi]=E[\cdot]$ per ogni policy | B20 | implicito (baseline random) | reference | 04 |
| convergenza delle probabilità come medie di indicatori → giustificazione del Monte Carlo | B20 | doc implicito | reference | blocco F |
| **vantaggio × P(esecuzione)**, concavità nello spread, **selezione avversa** | B20 | lezione in memoria, **non** in `fondamenti_tecnici/` | applicabile ora | 02 / 04 |
| equazione di Bellman come test di struttura (solo fuori campione) | B21 | assente | futuro | gruppo 2 |
| adattività discrezionale vs algoritmico | B21 | doc (04 §9) | reference | — |
| **dimensione campionaria** $n\approx(z\sigma/E)^2$, con esempio ricalcolato (~36.000 trade) | B22 | **assente** (buco 2) | applicabile ora | pre-registrazioni |
| **simulazione con incertezza sui parametri** (non plug-in) | B22 | assente | applicabile ora | §8bis |
| assenza di controfattuale; giudicare la decisione dall'esito | B23 | doc (04 §2) | in uso | — |
| l'OHLC lascia indefinita l'esecuzione dentro la barra (~$n^2/2$ coppie ingresso-uscita) | B23 | lezione in memoria, non in 04 | in uso | 04 |
| distinzione percorso realizzato vs distribuzione applicata alle conclusioni della fonte (covered call) | B23 | — | reference | — |
| **allocazione** (premi per il rischio documentati) vs **alpha** (inefficienza non documentata); decadimento dopo la pubblicazione | B24 | doc parziale (05) | applicabile ora | 05 |

## Buchi emersi nel repo

Numerazione in continuità con [`blocco-A.md`](blocco-A.md) (buchi 1–4). Registrati come **buchi**, non come
lavoro approvato: la decisione si prende in `SINTESI.md`.

5. **Il monitoraggio forward guarda solo drawdown e serie negative.** Mancano: confronto per gamba
   ($p$, vincita media, perdita media) e per forma di distribuzione (KS/Wasserstein) contro il backtest, e un
   **test sequenziale di deriva** (CUSUM o SPRT) con soglie fissate nella pre-registrazione. Fonde il buco 3
   del blocco A. Fonti: B2, B3, B13.
6. **Il regime di volatilità è un'etichetta relativa non dichiarata come tale.** `classify_volatility`
   confronta ATR14 con la sua media a 50: in un periodo lungo ad alta volatilità etichetta "Quiet" circa metà
   dei giorni. Chi condiziona su quel regime deve saperlo. Fonte: B2.
7. **`benchmark_metrics` è lineare.** Una strategia a payoff convesso (copertura, uscite asimmetriche)
   produce un alpha che è artefatto di specificazione. Serve almeno il beta condizionato al segno del
   benchmark. Fonte: B10.
8. **Le pre-registrazioni non hanno una sezione "assunzioni e direzione dell'errore".** Normalità,
   indipendenza fra trade, indipendenza fra asset, stazionarietà: per ciascuna, se la violazione rende la stima
   del rischio ottimista o pessimista. Fonti: A3, B14.
9. **"Stazionarietà" usata in due sensi**: W3 del playground (in realtà un test di stabilità) e la riga 174
   di `agents/quant_reviewer.md` (ADF/KPSS sui rendimenti per stimare la durata dei regimi, domanda a cui il
   test non risponde). Fonte: B16.
10. **Esiti censurati.** Nessuna avvertenza nelle analisi di uscite alternative e MFE/MAE: il controfattuale
    dei trade chiusi da uno stop non è osservabile. Fonte: B11.
11. **Nessun formato di test per una componente aggiunta a una regola.** Filtri, condizioni di regime, uscite
    alternative si valutano oggi come strategie nuove; il formato corretto è l'**ablazione pre-registrata**
    (stessa regola con e senza la componente, stessi dati, contro il baseline), che è anche la risposta
    operativa a *"l'analisi tecnica non si può smentire"*. Fonti: B19, B21.
12. **La meccanica dell'esecuzione limite non è in `fondamenti_tecnici/`.** La lezione del fill fantasma vive
    in memoria e nei verdetti NXT/FADE, ma la formula $\text{vantaggio}\times P(\text{esecuzione})$ e la
    **selezione avversa** (si viene eseguiti quando il prezzo sta andando oltre) non sono scritte come
    principio. Fonte: B20.
13. **Le simulazioni usano parametri stimati come se fossero noti.** Il Monte Carlo delle soglie di ritiro
    (§8bis) rimescola gli stessi trade: l'incertezza sull'E[R] stimato non entra. Si somma al buco 2 (potenza):
    la dimensione campionaria richiesta $n\approx(z\sigma/E)^2$ va dichiarata prima del test. Fonte: B22.

## Conflitti per la mappa dei modelli

- **"Condiziona sulle variabili di stato finché le distribuzioni del P&L si separano"** (B1, B2, B12) **vs**
  **pre-registrazione con budget di trial** (STRATEGY_LIFECYCLE). Non si elegge un vincitore. Condizione di
  validità del condizionamento: la partizione è (1) dichiarata prima di vedere il P&L condizionato, (2)
  calcolabile al momento dell'ingresso, (3) contata come trial, (4) confermata fuori campione. Senza queste
  quattro è ricerca di massa non contabilizzata — il meccanismo del London Breakout.
- **"I test di stazionarietà sono senza senso; non si rende stazionario ciò che non lo è"** (B16) **vs**
  **radici unitarie e differenziazione** (blocco D, #222). Condizione: la fonte parla di non-stazionarietà
  **strutturale** (il processo generatore cambia) e lì ha ragione; nel senso **tecnico** (radice unitaria)
  differenziare rende stazionario e l'ADF risponde a una domanda precisa sul campione. Nessuno dei due test
  garantisce stabilità futura.
- **"Il rendimento atteso non esiste"** (B17) **vs** **E[R] come soglia di verdetto** in ogni
  pre-registrazione. Condizione: l'E[R] è una **media locale su una finestra dichiarata**; diventa un errore
  solo se usato come parametro fisso del futuro senza intervallo e senza controllo di deriva.
- **"NVIDIA oggi non è l'azienda di 20 anni fa: quali dati usare è il problema canonico"** (B11, B17) **vs**
  **"storico lungo = laboratorio di falsificazione"** ([[feedback_backtest_long_history_falsification]]).
  Condizione: lo storico lungo serve a **falsificare** una regola (se funziona solo in un sotto-periodo è
  sospetta); per **stimare un parametro** da usare in avanti serve una finestra rilevante, e la sua lunghezza
  è un trial (B16). Sono due usi diversi dello stesso storico.
- **"L'analisi tecnica non si può dimostrare né smentire: è una componente della policy, funziona su certi titoli
  in certi momenti"** (B19, B21; versione moderata in B23: *"è una domanda di ricerca"*) **vs** **NULL della
  ricerca livelli (384 trial) e famiglie CLOSED riapribili solo con evidenza esterna nuova e quantitativa**
  ([[project_level_research_v1_null_2026_07_06]], STRATEGY_LIFECYCLE). Non si elegge un vincitore. Condizione di
  validità del claim: vale come **avvertenza metodologica** — un test incondizionato non chiude i test condizionati,
  e una componente va giudicata dentro la regola che la usa. Non vale come **ragione per riaprire**: nella forma
  forte non è falsificabile, e "funziona su qualche titolo in qualche periodo" è l'esito atteso di una ricerca non
  contabilizzata (look-elsewhere, B11). La traduzione operativa della parte valida è l'**ablazione
  pre-registrata** (buco 11), da usare una volta sola se mai la famiglia si riaprisse per evidenza nuova.
