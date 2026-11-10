# Blocco A — Statistica e inferenza (14 video, 61.482 parole, ~7 ore)

Le fondamenta dei gate G1/G2. Letto per intero il 2026-09-15 dalle copie in `_raw/_lettura/`.

Il blocco è **didattico**: nessun claim di performance da filtrare, pochissimi numeri dichiarati.
Il valore sta in due posti: (1) le **condizioni** sotto cui ogni strumento vale, che Paolucci
ripete con insistenza per il caso finanziario (non-stazionarietà); (2) i **buchi** che la lettura
fa emergere nel nostro protocollo, elencati in fondo.

**Errori della fonte** trovati in lettura (trascrizioni automatiche, lavagna a mano): segnati nella
voce del video. Nessuno cambia le conclusioni, ma due (A2, A4) riguardano proprio l'interpretazione
di p-value e intervalli di confidenza, cioè il punto su cui si sbaglia di più.

Legenda. **Stato**: `core` = implementato in `core/` · `doc` = documentato in `fondamenti_tecnici/`
o nel protocollo · `analisi` = usato in uno script di `analysis/` ma non in `core/` · `assente`.
**Rilevanza**: in uso · applicabile ora · futuro · reference.

---

## A1 — Expectation, Variance, Independence, Covariance, and Correlation

`2eQLnHiJJ7A` · #190 · 64 min · 8.942 parole

### Valore atteso (definizione e linearità)
- **Formula**: $E[X]=\sum_a a\,P(a)$ (discreto), $\int x f(x)\,dx$ (continuo). $E[rX+t]=rE[X]+t$.
  $E[X+Y]=E[X]+E[Y]$ **anche senza indipendenza**.
- **Domanda**: qual è la media dello spazio degli esiti pesata per le probabilità.
- **Assunzioni**: che il valore atteso esista (vedi A8).
- **Si rompe**: quando lo si legge come "l'esito più probabile" o "quello che mi aspetto di vedere".
  Il dado ha $E=3{,}5$, esito impossibile. Il valore più frequente è la **moda**, quello centrale la
  **mediana**. Rilevante per noi: un E[R] positivo con win rate basso vuol dire che il trade *tipico*
  perde.
- **Stato**: doc implicito (E[R] ovunque nelle review). **Rilevanza**: in uso.

### Varianza sotto trasformazione
- **Formula**: $Var(X)=E[X^2]-E[X]^2$; $Var(rX+t)=r^2 Var(X)$. Lo shift non conta, la scala entra al
  quadrato.
- **Applicazione**: annualizzazione. $Var(\sqrt{252}\,X)=252\,Var(X)$, quindi la volatilità
  giornaliera si moltiplica per $\sqrt{252}$.
- **Assunzioni (non dette nel video, e sono il punto)**: il fattore $\sqrt{T}$ vale **solo se i
  rendimenti sono incorrelati nel tempo**. Con autocorrelazione $\rho$ la varianza su $T$ periodi
  contiene i termini $2\sum Cov$, e $\sqrt{T}$ sbaglia: sottostima il rischio con $\rho>0$
  (trend/momentum), lo sovrastima con $\rho<0$ (mean reversion). Paolucci stesso chiude dicendo che
  l'esempio sull'annualizzazione *"non mi sembra del tutto corretto"*.
- **Stato**: core — `sharpe_ratio` usa $\sqrt{P}$ senza correzione per autocorrelazione (Lo 2002 non
  implementato). Il gatekeeper avverte sui CI i.i.d. su trade sovrapposti, e 04 §7 tratta le finestre
  sovrapposte, ma **l'annualizzazione dello Sharpe non ha un controllo sull'autocorrelazione**.
- **Rilevanza**: in uso → **buco** (vedi fondo).

### Varianza della somma, covarianza, correlazione
- **Formula**: $Var(X+Y)=Var(X)+Var(Y)+2Cov(X,Y)$; $Cov(X,Y)=E[XY]-E[X]E[Y]$;
  $\rho=Cov/\sqrt{Var(X)Var(Y)}\in[-1,1]$, invariante alla scala.
- **Domanda**: quanto rischio aggiunge combinare due flussi; quanto sono *linearmente* legati.
- **Si rompe**: **covarianza zero non implica indipendenza**. $\rho$ misura solo la dipendenza
  lineare: due strategie a $\rho\approx0$ possono perdere insieme nelle code (dipendenza non lineare,
  tail dependence).
- **Stato**: doc (05 diversificazione, non-stazionarietà delle correlazioni). La distinzione
  incorrelato ≠ indipendente **non è scritta**. **Rilevanza**: applicabile ora (orthogonal return
  streams, playground multi-gruppo).

---

## A2 — Applied Statistics and Statistical Inference

`ndou1b8NGQ0` · #191 · 42 min · 6.717 parole

### Stimatore, correttezza, varianza dello stimatore
- **Formula**: $\bar X=\frac1n\sum X_i$; $E[\bar X]=\mu$ (non distorto); $Var(\bar X)=\sigma^2/n$.
- **Domanda**: quanto è affidabile una media campionaria.
- **Assunzioni**: $X_i$ **i.i.d.**
- **Errore della fonte**: sulla lavagna scrive $Var(\bar X)=\frac{n}{12}(\beta-\alpha)^2$; è
  $\frac{(\beta-\alpha)^2}{12\,n}$.
- **Regola pratica che dà** (corretta e utile): *non spezzare un campione in sotto-campioni per poi
  mediare le medie*; usa il campione più grande possibile per la stima. Il ricampionamento serve a
  **vedere** la distribuzione della statistica, non a stimare meglio.
- **Stato**: doc implicito. **Rilevanza**: in uso.

### Test d'ipotesi a una media (z e t)
- **Formula**: $z=(\bar x-\mu_0)/(s/\sqrt n)$. Con $\sigma$ nota o $n$ grande → normale; con $s$ e $n$
  piccolo → $t_{n-1}$ (esatta solo se i dati sono normali).
- **Procedura**: $H_0$, $H_1$ (unilaterale o bilaterale), statistica, p-value, rifiuto a un livello.
- **Si rompe**:
  - dati non i.i.d. (autocorrelazione → $s/\sqrt n$ troppo piccolo → p-value troppo ottimisti);
  - $t$ usata su dati non normali con $n$ piccolo.
- ⚠️ **Errore della fonte, ed è l'errore classico**: a metà spiegazione dice *"la probabilità che il
  vero parametro sia 0,5 è minuscola"*. Il p-value è $P(\text{dati così estremi}\mid H_0)$, **non**
  $P(H_0\mid\text{dati})$. Poco prima l'aveva detto giusto. Da tenere fermo nei verdetti G2.
- **Stato**: core in forma evoluta (`probabilistic_sharpe_ratio` è uno z-test sullo Sharpe corretto
  per skew/curtosi; `mc_permutation_test`, `bca_bootstrap_ci`); analisi (`session_ci.py`, binomiale).
- **Rilevanza**: in uso.

### Errori di tipo I/II e potenza
- **Definizione**: tipo I = rifiutare $H_0$ vera (falso positivo, $\alpha$); tipo II = non rifiutare
  $H_0$ falsa (falso negativo, $\beta$); **potenza** $=1-\beta$. *"La potenza di un test ti dice la
  dimensione campionaria richiesta."*
- **Esempio del video**: con $n=200$ non rifiuta $\mu=0{,}4$ quando il vero è $0{,}375$ → errore di
  tipo II. Solo accennato, *"ne parleremo in un altro video"*.
- **Domanda che risponde**: **quanti trade servono** per avere una probabilità ragionevole di vedere
  un edge di dimensione data, se c'è.
- **Stato**: **assente** come calcolo. Il repo ha soglie fisse (*"< 50 trade IS = INSUFFICIENT
  DATA"*, 04 regole; *"50-100 trade"*, `agents/quant_reviewer.md`) e la pre-registrazione NXT fissa
  la dimensione campionaria contro l'optional stopping, ma **nessuna pre-registrazione calcola la
  potenza**, e non c'è il MinTRL (Minimum Track Record Length, Bailey-López de Prado), che è
  l'equivalente per lo Sharpe.
- **Rilevanza**: **applicabile ora** → **buco** (vedi fondo).

---

## A3 — The Method of Maximum Likelihood Estimation

`fbqNL9ae6yU` · #192 · 35 min · 5.081 parole

### Stima di massima verosimiglianza (MLE)
- **Formula**: $\hat\theta=\arg\max_\theta \prod_i f(x_i\mid\theta)=\arg\max_\theta\sum_i\ln f(x_i\mid\theta)$.
  Per Poisson: $\hat\lambda=\bar x$.
- **Distinzione**: **stimatore** = funzione (derivata sulle variabili aleatorie); **stima** = funzione
  applicata ai dati.
- **Domanda**: quale parametro rende più probabili i dati osservati.
- **Assunzioni**: forma distributiva corretta; **indipendenza**, che trasforma la verosimiglianza
  congiunta in un prodotto. Proprietà asintotiche: distorsione → 0, varianza minima, normalità.
- **Si rompe — ed è la parte migliore del video**: ogni assunzione ha una **direzione di errore sul
  rischio**, e va dichiarata. Nell'esempio (posti letto in ospedale):
  - "entrano ed escono in giornata" → sottostima il rischio;
  - "i giorni sono indipendenti" → sottostima il rischio (i contagi creano cluster).
  Lezione generale: *chiedersi, per ogni assunzione, se rende la stima del rischio conservativa o
  liberale*. Per noi: assumere trade indipendenti **sottostima** la probabilità di serie negative
  quando le perdite si raggruppano per regime.
- **Applicazione**: stima $\hat\lambda$, poi $P(X>100)=1-F(100)$ → probabilità di superare una
  capacità. Stesso schema di "probabilità che il drawdown superi la soglia di ritiro".
- **Stato**: assente in core (le calibrazioni GARCH/HMM del blocco D la useranno). La "direzione
  dell'errore per assunzione" è vicina al pre-mortem di 04 §9 ma non è scritta come checklist.
- **Rilevanza**: futuro (calibrazione modelli); la checklist delle direzioni: applicabile ora.

---

## A4 — Correcting the Interpretation of a Confidence Interval

`7h8MDB029MQ` · #195 · 9 min · 1.526 parole

### Intervallo di confidenza (interpretazione frequentista)
- **Formula**: $\bar x\pm z_{1-\alpha/2}\,\sigma/\sqrt n$ (95%: $z=1{,}96$; esempio $50\pm1{,}96$ →
  48–52).
- **Interpretazione corretta**: la procedura, ripetuta su molti campioni, produce intervalli che
  **contengono il parametro nel 95% dei casi**. **Non** "c'è il 95% di probabilità che $\mu$ stia in
  questo intervallo": una volta calcolato, l'intervallo lo contiene o no.
- **Controintuitivo utile**: più confidenza → intervallo **più largo**.
- **Errore della fonte**: nel grafico dice *"circa 95 su 100 **non** conterranno"*; sono 5 su 100.
- **Conseguenza per il repo**: la regola d'oro di 04 §6 (*"decidi sul lower bound"*) resta giusta, ma
  il lower bound BCa **non** va letto come "95% di probabilità che lo Sharpe vero sia sopra". È un
  limite di una procedura con copertura nominale 95% — e la copertura nominale vale solo se le
  assunzioni del bootstrap reggono (dipendenza, stazionarietà).
- **Stato**: core (`bca_bootstrap_ci`). **Rilevanza**: in uso (formulazione dei verdetti).

---

## A5 — Intuition for Law of Large Numbers and Central Limit Theorem

`tb5gaJzVrlk` · #196 · 16 min · 2.410 parole

### Legge dei grandi numeri (LGN)
- **Formula**: $\lim_{n\to\infty}P(|\bar X_n-\mu|<\varepsilon)=1$ per ogni $\varepsilon>0$ (legge debole).
- **Simulazione**: con $\varepsilon=0{,}01$ la frequenza di "dentro" passa da 0,21 ($n=10$) a ~1
  ($n=100.000$).
- **Assunzioni**: i.i.d., **media finita**.
- **Stato**: doc (05, citata come ciò che *non* vale sotto non-stazionarietà). **Rilevanza**: in uso.

### Teorema del limite centrale (TLC) — versione intuitiva
- **Enunciato**: la distribuzione delle medie campionarie è approssimativamente normale per $n$
  abbastanza grande, *"qualunque sia la distribuzione di partenza"*.
- **Esempio di trading**: segnale di sentiment su un campione casuale di tweet (API limitata) → la
  media del campione è normale → test d'ipotesi sul segno.
- ⚠️ **Conflitto interno alla fonte**: *"qualunque sia la distribuzione"* è **falso senza varianza
  finita**, e Paolucci stesso lo mostra in A8. Vedi mappa dei modelli in fondo.
- **Stato/rilevanza**: come A6.

---

## A6 — Central Limit Theorem for Quant Finance

`q2era-4pnic` · #112 · 52 min · 7.550 parole — **il video più importante del blocco**

### Le statistiche empiriche sono variabili aleatorie
- La distribuzione empirica di un campione è essa stessa aleatoria (un altro seed → altro
  istogramma), quindi lo è ogni statistica calcolata sopra: media, Sharpe, win rate, E[R].
- **Per noi**: ogni metrica di backtest è **una estrazione**, non una proprietà della strategia.
- **Stato**: doc (è il presupposto di DSR/PBO/bootstrap). **Rilevanza**: in uso.

### TLC — dimostrazione con la funzione caratteristica
- **Schema**: media standardizzata $Z_n$; funzione caratteristica della somma di indipendenti =
  prodotto; espansione di Taylor; limite $e^{-t^2/2}$ = caratteristica della normale standard;
  teorema di continuità di Lévy → convergenza in distribuzione.
- **Assunzioni**: indipendenza, identica distribuzione, **varianza finita** (serve all'espansione al
  secondo ordine). La funzione caratteristica esiste sempre (a differenza della MGF, A9).
- **Varianza della media** $\sigma^2/n$ → più campione, più stretta la distribuzione della media.
- **Stato**: reference. **Rilevanza**: reference.

### Modello calibrato vs distribuzione fuori campione (drift)
- **Esempio**: Poisson calibrata a $\lambda=4$ trade per 100 ms; nei 10 s successivi la media empirica
  è 2. Tre domande del modellatore: (1) la famiglia distributiva è ragionevole? (2) la distribuzione è
  stabile o varia nel tempo? (3) se varia, un **regime** la cattura?
- **Strumento**: $P(\text{media osservata}\mid\text{modello calibrato})$ come **test di deriva**:
  se è minuscola, il modello non descrive più il processo.
- **Per noi**: è la logica delle soglie di ritiro sul forward (STRATEGY_LIFECYCLE §8bis) — il forward
  si confronta con la distribuzione attesa dal backtest, non con il suo valore puntuale.
- **Stato**: doc (§8bis). **Rilevanza**: in uso.

### TLC sotto non-stazionarietà: sottostima delle code
- **Esempio NVIDIA**: medie su blocchi disgiunti da 90 giorni; normale calibrata sulle medie di blocco
  → $P(\text{media di blocco}<0)\approx0$. Realtà: **20 blocchi negativi su 74 (27%)**. I "anni di
  attesa" che cita (decine di migliaia) sono illustrativi e non verificati — il dato che conta è
  $\approx0$ previsto vs 27% osservato.
- **Condizione**: il TLC presuppone una distribuzione **fissa**. Con il processo che cambia, la
  normale calibrata su tutto lo storico **sottostima sistematicamente** gli eventi avversi.
- **Uso legittimo che propone**: TLC come **fotografia locale**. Decisione effimera (includere un
  titolo nel paniere in base a 50 documenti di sentiment tra le 8:00 e le 9:20) → la distribuzione è
  plausibilmente stabile *in quella finestra*. Sceglie volutamente una **distribuzione nulla
  conservativa** e integra la coda.
- **Stato**: doc (05, "LGN e TLC non valgono sotto cambi di regime"). La distinzione **"fotografia
  locale sì, previsione di lungo periodo no"** non è scritta. **Rilevanza**: in uso.

---

## A7 — Modeling with the Law of Total Expectation

`-CPUbalMh14` · #49 · 24 min · 3.410 parole

### Legge dell'aspettativa totale
- **Formula**: per una partizione $\{B_i\}$ dello spazio (unione = tutto, intersezioni vuote),
  $E[X]=\sum_i E[X\mid B_i]\,P(B_i)$.
- **Applicazione di trading**:
  $E[PnL]=E[PnL\mid win]\,P(win)+E[PnL\mid loss]\,P(loss)$, ripartibile ulteriormente per regime di
  volatilità, fattori macro, ecc.
- **Uso diagnostico — lo strumento vero del video**: quando l'aspettativa incondizionata cambia fra
  due periodi, **scomporla nelle quattro gambe** e guardare quale si è mossa: il win rate? la vincita
  media? la perdita media? Esempio dell'altezza media 1902 vs 2026.
- **Definizione di edge che ne dà**: le gambe condizionate sono **ragionevolmente stabili nel tempo**,
  media positiva con varianza contenuta. È la prima cosa che chiede ai clienti di consulenza: *"la
  stabilità della distribuzione nel tempo"*.
- **Assunzioni**: la partizione dev'essere **vera** (disgiunta ed esaustiva) e **nota al momento
  della decisione**.
- **Si rompe**:
  - una partizione per regime calcolata con look-ahead (label sul close dello stesso giorno) non è
    una partizione ammissibile, è informazione futura — il caso London Breakout;
  - ogni partizione aggiuntiva è un **trial**: condizionare finché una gamba "diventa stabile" è
    ricerca di massa non contabilizzata.
- **Citazione che registra**: *"tutta la ricerca empirica è data mining"*; se hai trovato qualcosa di
  strutturale continui a sfruttarlo.
- **Stato**: implicito (win rate × payoff nelle review); **la scomposizione nel tempo come diagnosi
  di deriva è assente** (il weekly healthcheck conta i trade, non scompone E[R]).
- **Rilevanza**: **applicabile ora** — forward dei segnali mentore (se il degrado arriva, è la
  direzione o il payoff?) e qualunque forward pre-registrato.

---

## A8 — What Happens when the Expectation is Infinity?

`GF2lJ-G2BYc` · #182 · 27 min · 4.310 parole

### Paradosso di San Pietroburgo / momenti non esistenti
- **Setup**: si lancia una moneta fino alla prima croce; $N$ lanci → vincita $2^N$. $N$ geometrica
  ($p=1/2$, $E[N]=2$). Per aspettativa totale
  $E[G]=\sum_{t\ge1}2^t(1/2)^t=\sum 1=\infty$.
- **Tesi**: *"è una storia di inconsistenza, non di infinito"*. Senza media finita la LGN non ha
  nulla verso cui convergere: la media campionaria corrente **non si stabilizza**, e rilanciando la
  simulazione si stabilizza "intorno" a valori diversi (12–14, poi 15–20). Varianza, skew e curtosi
  non esistono.
- **Conseguenza**: il prezzo "giusto" non è una questione di valore atteso ma di **tolleranza al
  rischio**. Simulare e leggere la media è sbagliato proprio perché usa implicitamente LGN/TLC.
- **Domanda per noi**: una distribuzione di rendimenti o di multipli di R **a coda pesante** (indice
  di coda $\alpha\le2$: varianza infinita; $\alpha\le1$: media infinita) rende inaffidabili Sharpe,
  z-test e bootstrap classici, anche con molti trade. Con $2<\alpha$ piccolo i momenti esistono ma la
  convergenza è **lentissima**.
- **Dove morde**: strategie a coda destra lunga (trend following, uscite senza target), crypto — il
  lead del playground, dove l'E[R] è trainato da pochi trade enormi; e, al contrario, strategie short
  volatilità a coda sinistra.
- **Stato**: `tail_metrics`, `omega_ratio`, `tail_ratio` descrivono le code; PSR/DSR correggono per
  skew/curtosi **assumendo che esistano**. **Nessuna stima dell'indice di coda** (Hill o simili) e
  nessun controllo "la media campionaria si è stabilizzata?" (grafico della media corrente).
- **Rilevanza**: **applicabile ora** sul lead trend/playground → **buco** (vedi fondo).

---

## A9 — Moment Generating Functions and Normal Random Variables

`ZE3Fi4ZH7f8` · #188 · 55 min · 7.247 parole

### Funzione generatrice dei momenti (MGF)
- **Formula**: $M_Z(\theta)=E[e^{\theta Z}]$; espansione di Taylor
  $M(\theta)=\sum_k \theta^k E[Z^k]/k!$ → $E[Z^n]=M^{(n)}(0)$.
- **Normale**: standard $M=e^{\theta^2/2}$ (completando il quadrato); generale
  $M=e^{\theta\mu+\frac12\theta^2\sigma^2}$.
- **Moto browniano**: $B_t\sim N(0,t)$ → $M=e^{\frac12\theta^2 t}$, $E[B_t]=0$, $E[B_t^2]=t$. È
  l'origine della scala $\sqrt t$ della volatilità (con le assunzioni di A1).
- **Limiti**: la MGF **non esiste** per distribuzioni a coda pesante (lognormale, Pareto, t di
  Student): per queste si usa la funzione caratteristica, che esiste sempre (A6).
- **Stato**: assente. **Rilevanza**: reference (serve al gruppo 2, calcolo stocastico).

---

## A10 — Uniform Probability and Binomial Random Variables

`7C72-fuccio` · #161 · 32 min · 4.687 parole — video promozionale della piattaforma di esercizi

### Probabilità da densità, da ripartizione, da rapporto di misure
- Tre vie equivalenti: $\int_a^b f$; $F(b)-F(a)$; esiti favorevoli / esiti totali (lunghezze,
  conteggi). Dadi: $P(7\text{ o }11)=8/36$ (unione di insiemi disgiunti).
- **Stato**: reference.

### Variabile binomiale
- **Formula**: $X\sim Bin(n,p)$, $P(X=k)=\binom nk p^k(1-p)^{n-k}$; somma di Bernoulli **indipendenti**.
- **Domanda per noi**: il **test binomiale sul win rate / hit rate direzionale** ("67–72% contro 32%
  random" dei segnali mentore; "53% contro 80% dichiarato" di VELTRIX).
- **Assunzioni**: prove indipendenti a $p$ costante. **Si rompe**: trade sovrapposti o raggruppati
  nello stesso movimento (non indipendenti) → p-value troppo piccoli; $p$ che cambia nel tempo.
- **Variante citata**: *"qual è l'$n$ che massimizza la probabilità di vedere $k$ successi"* →
  problema di ottimizzazione, non di sostituzione.
- **Stato**: analisi (`analysis/trading-bot-eval/session_ci.py`: code binomiali). Non in core.
- **Rilevanza**: in uso.

### Variabile geometrica (da A8)
- $P(N=t)=(1-p)^{t-1}p$, $E[N]=1/p$: numero di prove fino al primo successo. Per noi: attese su
  eventi rari (primo mese negativo, prima serie di $k$ perdite) — **solo** con prove indipendenti.
- **Stato**: assente. **Rilevanza**: reference.

---

## A11 — Critical Values in 3 Minutes

`YyBG3IESj90` · #189 · 3 min · 474 parole

### Valore critico
- **Formula**: $x_c=\Phi^{-1}(1-\alpha)$; unilaterale 95% → 1,645; bilaterale 95% → 1,96.
- **Stato**: core (`_norm_inv`). **Rilevanza**: in uso.
- ⚠️ Ripete *"regardless of the distribution"* per la media campionaria: stessa riserva di A5.

---

## A12 — Linear Regression Clearly Explained with Matrices

`y7tYH6Io0Y4` · #218 · 26 min · 3.905 parole

### Minimi quadrati in forma matriciale (OLS)
- **Formula**: $\hat y=Xb$, con $X$ $n\times2$ (colonna di 1 per l'intercetta); minimizzare
  $SSE=e^\top e$; derivata rispetto a $b$ uguale a zero → $X^\top Xb=X^\top y$ →
  $b=(X^\top X)^{-1}X^\top y$.
- **Errore della fonte**: scrive $b=(X^\top X)^{-1}y^\top X$ (dimensioni sbagliate: $y^\top X$ è
  $1\times2$). La forma giusta è sopra; nel video in Python (A13) i numeri tornano perché i vettori
  vengono trasposti a mano.
- **Assunzioni per interpretare i coefficienti**: linearità, errori a media zero e varianza costante,
  regressori non collineari (A14); per l'inferenza, errori indipendenti.
- **Si rompe**:
  - **regressione nello spazio dei prezzi**: lo dice lui stesso (radici unitarie → blocco D):
    regressioni su serie non stazionarie producono relazioni spurie;
  - **pochi punti** → la retta cambia molto con nuovi dati (overfitting). Rimedio citato:
    regolarizzazione L1/L2 (lasso, ridge), rimandata.
- **Stato**: core (`benchmark_metrics`: alpha e beta come intercetta e pendenza). **Rilevanza**: in
  uso.

---

## A13 — Linear Regressions in Python

`xh7HgsReYGk` · #206 · 11 min · 1.739 parole

- Stessa OLS di A12 in NumPy (`inv(X.T @ X) @ X.T @ y`) confrontata con `sklearn.LinearRegression`:
  coincidono a 5 decimali, a riprova dell'unicità della soluzione.
- Nulla di nuovo come strumento. **Stato**: core (vedi A12). **Rilevanza**: reference.

---

## A14 — Linear Algebra: Linear Independence

`hJmX1V5JlRs` · #210 · 24 min · 3.484 parole

### Indipendenza lineare, base, ortogonalità
- **Definizioni**: norma $\|x\|=\sqrt{\sum x_i^2}$; prodotto scalare; ortogonali se $x\cdot y=0$;
  **ortonormale** = ortogonali e di norma 1; una base genera lo spazio. $v_1,\dots,v_k$ linearmente
  indipendenti se $\sum q_iv_i=0$ ha solo la soluzione nulla. Vettori ortogonali non nulli sono
  indipendenti.
- **Applicazione — multicollinearità**: se $z=d_1x+d_2y$, la feature $z$ è **ridondante** (non
  aggiunge informazione e rende instabile $(X^\top X)^{-1}$). Misura citata: **VIF**; rimedio: cambio di
  base (**PCA**).
- **Per noi**: due segnali "diversi" costruiti dagli stessi prezzi possono essere quasi collineari; in
  una ricerca con più feature il numero *effettivo* di trial è minore del nominale, ma i coefficienti
  diventano instabili.
- **Stato**: PCA doc (05); VIF assente. **Rilevanza**: futuro (modelli multi-feature); reference.

---

## Sintesi del blocco

| strumento | video | stato | rilevanza | destinazione proposta |
|---|---|---|---|---|
| valore atteso, linearità, moda/mediana | A1 | doc implicito | in uso | 04 (nuova sez. fondamenti statistici) |
| varianza sotto scala, annualizzazione $\sqrt T$ | A1, A9 | core senza correzione autocorr. | in uso | 04 + buco 1 |
| $Var(X+Y)$, covarianza, correlazione; incorrelato ≠ indipendente | A1 | doc parziale (05) | applicabile ora | 05 |
| stimatore, $\sigma^2/n$, "non spezzare il campione" | A2 | doc implicito | in uso | 04 |
| z/t test, p-value e sua lettura corretta | A2, A11 | core (PSR), analisi | in uso | 04 |
| errori tipo I/II, potenza, dimensione campionaria | A2 | **assente** | applicabile ora | 04 + STRATEGY_LIFECYCLE (buco 2) |
| MLE e direzione dell'errore di ogni assunzione | A3 | assente | futuro / checklist ora | 04 §9 (estensione) |
| intervallo di confidenza frequentista | A4 | core (BCa) | in uso | 04 §6 (precisazione) |
| LGN, TLC e loro condizioni | A5, A6 | doc (05) | in uso | 04 |
| statistiche empiriche = variabili aleatorie | A6 | doc | in uso | 04 |
| test di deriva modello calibrato vs forward | A6 | doc (§8bis) | in uso | STRATEGY_LIFECYCLE §8bis (rinforzo) |
| TLC come fotografia locale, non previsione | A6 | doc parziale | in uso | 05 §non-stazionarietà |
| aspettativa totale, scomposizione per gambe nel tempo | A7 | **assente come diagnosi** | applicabile ora | 04 + healthcheck (buco 3) |
| momenti infiniti, coda pesante, convergenza della media | A8 | **assente** | applicabile ora | 04 + core (buco 4) |
| MGF, momenti del moto browniano | A9 | assente | reference | gruppo 2 |
| binomiale, geometrica, uniforme | A10 | analisi | in uso / reference | 04 |
| valore critico | A11 | core | in uso | — |
| OLS matriciale, regressione spuria, regolarizzazione | A12, A13 | core (alpha/beta) | in uso | 04 / 05 |
| indipendenza lineare, multicollinearità, VIF | A14 | PCA doc, VIF assente | futuro | 05 |

## Buchi emersi nel repo

Registrati come **buchi**, non come lavoro approvato: la decisione su cosa implementare si prende a
distillazione finita, in `SINTESI.md`.

1. **Annualizzazione senza controllo di autocorrelazione.** `sharpe_ratio` moltiplica per
   $\sqrt{P}$; con rendimenti autocorrelati lo Sharpe annuo è distorto (Lo 2002). Minimo: riportare
   l'autocorrelazione dei rendimenti accanto allo Sharpe.
2. **Nessun calcolo di potenza nelle pre-registrazioni.** Le soglie "50 trade" sono fisse e
   indipendenti dall'effetto cercato. Serve: dato l'effetto minimo interessante (es. E[R]=+0,10R con
   la dispersione attesa), quanti trade servono per potenza 80%? E il MinTRL per lo Sharpe. Un test
   senza potenza che non rifiuta **non è un NO-GO informativo**: è un'assenza di prova.
3. **Nessuna scomposizione E[R] = P(win)·E[win] + P(loss)·E[loss] nel tempo** nel monitoraggio forward.
4. **Nessuna diagnosi di coda pesante**: né indice di coda né stabilità della media corrente. PSR/DSR
   assumono che skew e curtosi esistano e siano stimabili; con coda pesante non è così.

## Conflitti per la mappa dei modelli

- **"La media campionaria è normale qualunque sia la distribuzione"** (A5, A6, A11) **vs** **"con media
  infinita non converge a nulla"** (A8) — *stessa fonte*. Condizione: il TLC classico richiede
  **i.i.d. e varianza finita**. Con coda pesante ($\alpha\le2$) la somma converge a una legge stabile
  non normale, o non converge. Non c'è vincitore: sono lo stesso teorema con e senza la sua ipotesi.
- **"TLC e LGN non valgono in finanza"** (05, A6, A7) **vs** **"il TLC è utile per decisioni
  locali"** (A6). Condizione: vale come **fotografia** su una finestra in cui il processo è
  plausibilmente stabile e con una **nulla conservativa**; non vale come previsione su orizzonti lunghi
  calibrata su tutto lo storico.
