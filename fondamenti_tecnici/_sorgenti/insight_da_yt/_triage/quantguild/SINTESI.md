# Quant Guild — sintesi consolidata del distillamento

> **STATO: CHIUSO il 2026-09-17.** Gruppo 1 completo: **81 video letti per intero** dalle copie in `_raw/_lettura/`,
> blocchi A-H chiusi, più 2 video di controllo scaricati per l'attribuzione. Risultato: **48 buchi** identificati e
> **14 conflitti** per la mappa dei modelli. Questo file è l'**uscita finale**; [`PIANO.md`](PIANO.md) resta il diario
> di lavoro con lo stato per blocco.
>
> ⚠️ ~~I buchi sono identificati, non approvati~~ → **2026-09-30: l'utente approva i buchi di PRIORITA' 1, poi gli
> altri in ordine** (DECISIONS 2026-09-30). **Priorita' 1 IMPLEMENTATA il 2026-09-30**: primitive in
> [`core/verifiche.py`](../../../../../core/verifiche.py) (buchi 2, 5, 22, 27, 28, 29, 37, 46) con 21 test in
> `core/tests/test_verifiche.py`; campi dell'errore del p in `mc_permutation_test` e `whites_reality_check` (37);
> regole in `STRATEGY_LIFECYCLE` §8bis (5, 22, 27, 28, 29, **41**), `QUANT_REVIEW_PROTOCOL` Step 4 (2, 29, 37, 46),
> `04_quant_metodologia` §1 (**20**), G2 del gatekeeper; buco 46 annotato nei 4 documenti indicati. **Prossimo:
> priorita' 2.**

## Che cosa è questo file

Il **catalogo consolidato per dominio** di ciò che il canale Quant Guild (Roman Paolucci) ha da offrire, con:

- lo **stato nel repo** di ogni strumento (implementato in `core/` · documentato in `fondamenti_tecnici/` · assente);
- la **rilevanza** (in uso · applicabile ora · futuro · reference) — che **classifica, non esclude**
  ([[feedback_distillazione_cattura_ampia]]);
- la **destinazione** proposta per ogni voce (`04_quant_metodologia`, `05_portfolio_rischio`, `03_regimi_macro`,
  protocollo, core, o una sezione nuova);
- i **conflitti** da registrare nella mappa dei modelli di `DECISIONS.md`, con le condizioni di validità e **senza
  eleggere un vincitore**.

I file per blocco restano la fonte dettagliata: [`blocco-A.md`](blocco-A.md) (statistica e inferenza),
[`blocco-B.md`](blocco-B.md) (edge, fortuna vs abilità, validità del backtest), [`blocco-C.md`](blocco-C.md) (sizing,
rovina, ergodicità), [`blocco-D.md`](blocco-D.md) (serie storiche, regimi, filtri, processi di punto),
[`blocco-E.md`](blocco-E.md) (portafoglio), [`blocco-F.md`](blocco-F.md) (Monte Carlo),
[`blocco-G.md`](blocco-G.md) (struttura di mercato e cornice), [`blocco-H.md`](blocco-H.md) (attribuzione degli
appunti orfani).

## Regole di lettura applicate in tutto il distillamento

1. **Si raccolgono le regole, si scartano i claim numerici non verificabili.** Dove un numero era ricalcolabile è stato
   **ricalcolato** e il risultato è scritto accanto (diverse volte la fonte sbaglia: vedi la rovina del giocatore in C2,
   il milione a 30 anni in C7, il MSE fuori campione in B18).
2. **Le affermazioni di performance personali non fanno stato** (track record dichiarati, "assomiglia alla mia
   performance live", fondi propri).
3. **Le parti promozionali sono segnate** (corsi, piattaforma, fondo Long Tail, broker in affiliazione) quando toccano
   la sostanza dell'argomento.
4. **Gli errori della fonte sono registrati** come parte del catalogo: servono a non ripeterli.

---

## Catalogo per dominio

> Da compilare a lettura finita, fondendo le tabelle di sintesi dei singoli blocchi.

### 1. Fondamenti statistici e inferenza — da [`blocco-A.md`](blocco-A.md)

**Già nostri** (in uso): valore atteso e sua lettura corretta, varianza sotto scala, covarianza e correlazione, stimatori
e $\sigma^2/n$, test z/t e p-value, valori critici, intervalli di confidenza frequentisti, LGN e TLC con le loro
condizioni, OLS in forma matriciale, statistiche empiriche come variabili aleatorie.

**Da aggiungere, in ordine di utilità**:
1. **Potenza e dimensione campionaria** — $n\approx(z\sigma/E)^2$ (A2, B22). Oggi le pre-registrazioni usano soglie fisse
   ("50 trade"): un NO-GO senza potenza non è un verdetto, è assenza di prova. → *04 + STRATEGY_LIFECYCLE*.
2. **Direzione dell'errore per ogni assunzione violata** (A3, B14): normalità, indipendenza fra trade, fra asset,
   stazionarietà — per ciascuna, se la violazione rende la stima del rischio ottimista o pessimista. → *template di
   pre-registrazione*.
3. **Code pesanti e momenti che non esistono** (A8): con $\alpha\le2$ Sharpe, z-test e bootstrap classici perdono senso;
   serve almeno un controllo di stabilità della media corrente. → *04 + core*.
4. **Aspettativa totale come diagnosi**: scomporre E[R] nelle quattro gambe **nel tempo** per vedere quale si muove
   (A7, B12). → *healthcheck settimanale*.
5. **Incorrelato ≠ indipendente** (A1); **mediana vs media** secondo la funzione di perdita (B11); **multicollinearità e
   VIF** (A14). → *05 / reference*.

### 2. Validità del backtest e protocollo — da [`blocco-B.md`](blocco-B.md)

**Già nostri**: i tre bias, DSR/PBO/CPCV/White, walk-forward, finestre sovrapposte, baseline random, contatore trial,
holdout sigillato, §8bis.

**Da aggiungere**:
1. **Stabilità per gamba e distanza fra distribuzioni** (B2): confrontare forward e backtest su $p$, vincita media,
   perdita media **e forma** (KS/Wasserstein), non solo su drawdown e serie negative.
2. **Deriva con soglie pre-registrate** (B13): CUSUM/SPRT tarati sui parametri del backtest, non finestre mobili
   ri-stimate (C4: le bande mobili assorbono il degrado).
3. **Ablazione pre-registrata** per giudicare una componente aggiunta a una regola (B19, B21) — è anche la risposta
   operativa a *"l'analisi tecnica non si può smentire"*.
4. **Esiti censurati** (B11): il controfattuale dei trade chiusi da uno stop non è osservabile.
5. **Serie rare in campioni lunghi** (B11, verificato: 10 teste di fila entro 1.421 lanci con probabilità > 50%) e
   **dispersione prodotta da un edge dato** (B7, verificato: 11 su 100 in perdita dopo 1.000 trade con E=+0,04R).
6. **$R^2$ fuori campione contro previsore ingenuo** (B18) e **regressione spuria su livelli** (D2).

### 3. Esecuzione e microstruttura

1. **Vantaggio × P(esecuzione)** e **selezione avversa** (B20), con la forma analitica $\lambda(\text{spread})$ (D11):
   un ordine limite più favorevole si esegue **meno** e **peggio**. → *02 / 04*, si aggancia a
   [[feedback_fill_ottenibile]].
2. **L'OHLC non definisce l'esecuzione** (B23, D1): fra due osservazioni il percorso è ignoto; in una barra oraria di un
   titolo liquido ci sono ~$n^2/2$ coppie ingresso-uscita.
3. **Market making con modello sbagliato ma corretto in media** (D1): serve un livello non distorto più uno spread che
   copra l'errore. → *reference*.

### 4. Sizing, rovina, crescita geometrica — da [`blocco-C.md`](blocco-C.md)

**Già nostri**: volatility drag, leva che amplifica il drag come $L^2$, "Kelly frazionario", full Kelly = red flag.

**Da aggiungere**:
1. **Kelly esplicito** $f^*=p-q/b$ (in R: $p-q/W$; continuo: $\mu/\sigma^2$) e la **parabola** $g(f)=f\mu-\frac12f^2\sigma^2$
   che unifica drag e Kelly (C1, C5).
2. **Proprietà del Kelly pieno**: $P(\text{scendere a }x\text{ del capitale})=x$; crescita $k(2-k)$ e varianza $k^2$ con
   frazione $k$; **asimmetria dell'errore di stima** → prudenza razionale (C1, C3).
3. **Capitale a rischio per trade** ≠ esposizione nozionale: il risk gate oggi limita solo il nozionale (C1).
4. **Probabilità di toccare un obiettivo prima di un limite** (C2): discreta (rovina del giocatore) e continua
   ($\theta=2\mu/\sigma^2$). Con edge zero una challenge +8%/−10% si supera nel ~56% dei casi.
5. **Attesa di una serie di $k$ perdite** $\sum_i q^{-i}$ (D6): a win rate 50% una serie di 5 arriva entro ~62 trade.
6. **Rendimento da diversificazione a pesi costanti** (C6) e **Sharpe che si sommano in quadratura** per flussi
   ortogonali (E2).

### 5. Serie storiche, regimi e filtri — da [`blocco-D.md`](blocco-D.md)

1. **Filtraggio vs lisciamento vs previsione** (D1): criterio generale contro il look-ahead, di cui la nostra regime
   timeline è solo un caso particolare. **Corollario forte**: l'inferenza HMM su tutto il campione è lisciamento (D5).
2. **Backtest per eccedenze** di qualunque soglia dichiarata (D3) e **controllo di frequenza implicita** dei parametri
   (D8, D10).
3. **Transizioni impossibili** come falsificazione senza dati (D4); **errore standard** delle probabilità di transizione
   e indipendenza fra unità (D4); **omogeneità temporale** come assunzione esplicita (D4, D7).
4. **Modelli di volatilità condizionata** (ARCH/GARCH, D3): etichetta di regime **assoluta** invece che relativa e
   volatilità prevista per il sizing.
5. **Filtro di Kalman** (D8): guadagno, innovazione, compromesso modello/dati; **innovazioni standardizzate** come
   diagnostica di rottura.
6. **Indipendenza degli esiti da testare** (D10, processi auto-eccitanti): se cade, tutte le soglie i.i.d. vanno
   abbassate.

### 6. Costruzione di portafoglio — da [`blocco-E.md`](blocco-E.md)

**Già nostri**: tassonomia del rischio, PCA come decomposizione, CAPM ed estensioni, alpha ortogonale, orthogonal return
streams, correlazioni che saltano in crisi, volatility drag, pilastro passivo con buffer e glide-path.

**Da aggiungere**:
1. **Test di perturbazione dei parametri** (E4): perturbare gli **input** e misurare lo spostamento delle uscite; con
   0,2% di rumore i pesi ottimi passano da 60% a 37%. Generalizza la regola "instabilità parametrica = NO-GO" a
   qualunque stima (pesi, soglie, matrici). → *04 §2*.
2. **Sharpe che si sommano in quadratura** per flussi ortogonali (E2): dà il valore numerico dell'ortogonalità e dice
   **quando non vale la pena** aggiungere una gamba. → *05*.
3. **Ribilanciamento a pesi costanti** come meccanismo del rendimento da diversificazione (C6, buco 18) — il blocco E ha
   un video dedicato (#220).
4. **MVO è un massimizzatore dell'errore di stima** (E3) e i rimedi che la fonte non cita: shrinkage, resampling, minima
   varianza / risk parity (niente $\mu$), **1/N** come benchmark. Default sensato per noi: **pesi dichiarati prima**,
   ottimizzazione al massimo come controllo. → *05*.
5. **Black-Litterman** (E4) come **forma corretta** in cui un giudizio soggettivo entra in un modello: vista dichiarata
   prima, con fiducia numerica, ancorata a un prior indipendente (l'equilibrio implicito di mercato). Condizione da
   tenere accanto a `04` §9 ("il qualitativo genera ipotesi, non valida").
6. **Stabilità della struttura fattoriale** (E5): PCA mobile su finestra: varianza spiegata e carichi **cambiano**; chi
   ci costruisce sopra deve monitorarla. → *05*.
7. **Annidamento delle frontiere e critica di Roll** (E4): il "mercato" è sempre una proxy scelta, e ogni beta eredita
   quella scelta. → *05, reference*.
### 7. Simulazione Monte Carlo — da [`blocco-F.md`](blocco-F.md)

**Già nostri**: `mc_permutation_test` (permutazione dei rendimenti, block bootstrap se autocorrelati), `bca_bootstrap_ci`,
bootstrap stazionario, `pbo_cscv`, `cpcv_splits`; la distinzione di `04` §2b fra il Monte Carlo che **rimescola i trade**
(dipendenza dal percorso) e ciò che valida un edge; le soglie di ritiro da percentili alti (§8bis).

**Da aggiungere**:
1. **L'errore standard della stima Monte Carlo** (F2, F4): ogni numero che esce da una simulazione ha la propria
   incertezza $\propto 1/\sqrt{N}$ e oggi non la riportiamo mai. Con 1.000 permutazioni un p-value vicino a 0,05 ha
   SE ≈ 0,7 punti: **"0,048" e "0,062" non sono distinguibili**. → *04, core* (buco 37, **priorità 1**).
2. **Ricetta della variabile indicatrice** (F1): per stimare una probabilità si registra 1/0 e si fa la media. Permette
   di esprimere le soglie di §8bis come **probabilità di violazione** invece che come percentili. → *§8bis* (buco 39).
3. **Robustezza al seme** (F3): tutto il repo gira con seme fisso 42, per contratto nelle pre-registrazioni. Corretto
   per la riproducibilità; da affiancare a una **ripetizione su più semi** in fase di verifica. Le due cose non sono in
   conflitto: il seme si dichiara prima, la robustezza si misura dopo. → *pre-registrazione + verifica* (buco 38).
4. **Riduzione della varianza** (F2, variate di controllo): **catalogata, non applicabile** — manca l'ingrediente (una
   quantità ad attesa nota in forma chiusa) e il costo per replicazione è trascurabile. → *reference* (buco 36).
5. **Trasformata inversa e integrazione MC** (F3, F4): fuori perimetro perché ricampioniamo dallo storico invece di
   generare da distribuzioni parametriche — scelta **giusta** e ora anche motivata (le distribuzioni si muovono).

**Il limite che la fonte dichiara da sé** e che vale per tutto il dominio: il Monte Carlo converge **al valore del
modello**, non al vero. La riduzione della varianza accelera la convergenza al numero sbagliato se il modello è
sbagliato (F2, G1). Distinzione fra **rumore di simulazione** ed **errore di modello** da tenere ferma.

### 8. Cornice di mercato — da [`blocco-G.md`](blocco-G.md)

**Già nostri**: EMH nelle tre forme e il suo rifiuto letterale (`08`), alpha come rendimento ortogonale (`05`), retail
vs istituzionale come vincolo pratico, pilastro investing passivo con Stock Selector archiviato, "le metriche sono
necessarie non sufficienti" (`04` §2b).

**Da aggiungere**:
1. 🔧 **La finestra di misura è un grado di libertà** (G3): la fonte mostra **sullo stesso conto e sullo stesso anno**
   Sharpe **0,88** (da inizio anno) e **6,28** (partendo dal minimo). È il *look-elsewhere* applicato alla **data di
   inizio**. Per le strategie il periodo è pre-registrato; **per il conto live non lo è**. → *protocollo, healthcheck*
   (buco 41, **priorità 1**).
2. 🔧 **Confronto sul decile peggiore dei percorsi** (G6): confrontando due strategie sulle medie si ottiene una
   risposta, confrontandole sul 10% di percorsi peggiori se ne ottiene un'altra — nel suo esempio il **segno del CAGR
   cambia**. → *core, 04* (buco 45).
3. 🔧 **Criterio di scelta "positivo ovunque" invece di "ottimo da qualche parte"** (G2): la politica ottima di un
   regime ha EV **negativo** in un altro; si cerca il parametro che è positivo in tutti. Il repo verifica la robustezza
   *dopo* il walk-forward, non la usa come criterio *di selezione*. → *STRATEGY_LIFECYCLE, pre-registrazione* (buco 40).
4. **Problema dell'ipotesi congiunta** (G4, G5): un alpha misurato su un solo fattore è indistinguibile da
   un'esposizione a un fattore non modellato; **due portafogli con lo stesso Sharpe** possono essere uno beta con leva
   e l'altro alpha puro. → *04, 05, docstring di `benchmark_metrics`* (buco 43).
5. **Pesi fra attività** (G3): PAC, segnali del mentore e prove sono una **combinazione lineare** di un unico capitale;
   la sua stessa ottimizzazione a varianza minima la scarta lui (*"i pesi sono sbagliati, sono stimati da dati"*). Serve
   che i pesi siano **dichiarati**, non ottimizzati. → *INVESTING_PILLAR_PLAN o documento di allocazione* (buco 42).
6. **Elenco dei riferimenti fondativi** (G5: Bachelier 1900, Sharpe 1964, Black-Scholes 1973, Dupire 1994, Carr-Madan
   1999): il repo cita solo la letteratura della validazione (López de Prado, Bailey, Harvey, White, Kelly, Thorp).
   → *`_INTAKE.md` o RIFERIMENTI.md* (buco 44).
7. **Selezione avversa** (G3) e **vantaggio × P(esecuzione)** (G1): il market making è fuori perimetro, ma la formula è
   il nostro buco 12 visto dal lato di chi quota — allargare lo spread alza il vantaggio e **abbassa** la probabilità di
   esecuzione. È la forma pulita di [[feedback_fill_ottenibile]].
8. **Casuale vs incerto** (G2): risposta compatta a "il trading è gioco d'azzardo" — nella roulette il vantaggio è
   **−5,26% fisso e nessuna azione lo cambia**; nei sistemi incerti le azioni determinano l'EV. Vale la pena scriverlo
   una volta. → *04, reference*.

**Due affermazioni della fonte che NON adottiamo** (dettaglio e condizioni in `blocco-G.md`): *"l'analisi tecnica non si
può confutare"* (vero per l'abilità discrezionale, falso in generale: si misura con il track record prospettico
pre-registrato) e *"non è la domanda se l'alpha sia statisticamente significativo"* (coerente per un allocatore con
mandato, incompatibile con chi deve **decidere se accendere** una strategia).

### 9. Attribuzione degli appunti orfani — da [`blocco-H.md`](blocco-H.md)

Il blocco *"Comprehensive Guide to Investing"* (`Nuove nozioni teoriche 2026-07-16.txt`, righe **331-491**) è di
**#29 `LX4Ugaxx9n0` — The Ultimate Guide to Quant Portfolio Management**, cioè dello **stesso video** già attribuito per
`quantportfolio managernotes.txt` righe 1-249. L'ipotesi del PIANO (*"uno fra #24, #131, #162"*) era **sbagliata**: i
tre candidati sono stati letti per intero, **zero marcatori**; la fonte è stata trovata cercando per contenuto
sull'intero canale. I già distillati restano **9**.

🔧 **Regola che ne esce**: un blocco di appunti orfano va cercato **per contenuto su tutto il canale**, non fra i video
"non ancora distillati" — un video già distillato può aver prodotto **più blocchi in file diversi**, e il titolo del
riassunto è generato dal sintetizzatore, quindi **non coincide** con quello del video.

**Da aggiungere dal blocco H** (oltre all'attribuzione):
1. 🔧 **La correlazione senza finestra non è un numero** (H2): JNJ/CMG stanno a **0,01** su rendimenti annuali, **0,13**
   su mobile mensile a 12 mesi, **0,17** su mobile giornaliera a 60 giorni **con punte a 0,73**. Nessuna correlazione
   nei nostri documenti dichiara frequenza e finestra. → *tutte le pre-registrazioni che citano correlazioni*
   (buco 46, **priorità 1**, costo una riga).
2. **Ortogonalità misurata condizionatamente allo stress** (#29, H1): il repo sa che le correlazioni saltano in crisi,
   ma nessuna analisi calcola la correlazione **dentro** le finestre di drawdown. → *core* (buco 48).
3. **Quota di tempo in contante / accessibilità del capitale** (H3): non misurata da nessuna parte, e il PAC è
   **a serbatoio**. Confrontare il rendimento di chi è sempre investito con quello di chi è metà del tempo liquido è un
   confronto fra cose diverse. → *healthcheck settimanale* (buco 47).
4. **Probabilità implicita = impatto già prezzato, non frequenza** (H3): un esito prezzato al 90% che si realizza muove
   poco; lo stesso al 60% produce un salto. Fuori perimetro finché non si opera su eventi macro, ma la distinzione
   frequentista vs implicita vale in generale. → *reference*.
5. **"Non diversificabile" è un termine improprio** (#29): vale **dentro** un mercato; la **decorrelazione fisica**
   (mercati o strategie separati per costruzione, non per stima) è il modo di aggirarlo. ⚠️ Con due cautele nostre che
   la fonte non pone: l'ortogonalità è **empirica e condizionata**, e l'illiquidità significa **prezzo non osservato**,
   non prezzo stabile.
6. **Conferma esterna dei due secchi del PAC** (#29): *"e se fra sei anni ti servissero i soldi e ci fosse un −30%?"* è
   esattamente la ragione del secchio cuscinetto di `docs/INVESTING_PILLAR_PLAN.md`. Il suo criterio dichiarato —
   *"resto indietro del 5-10% ogni anno ma con drawdown molto migliori, e sto meglio così"* — è la stessa scelta, fatta
   da un altro. **Conferma, non proposta.**

⚠️ **Terza occorrenza della "gamba di copertura"** (dopo E2 e G6, ora anche in #29, citata tre volte come corso a
pagamento e mai con dati): **stato invariato**. Tre video della stessa fonte con lo stesso conflitto d'interesse
restano **una** affermazione non verificata.

---

## Buchi nel repo

> Numerazione progressiva assegnata durante la lettura: **A 1–4, B 5–13, C 14–19, D 20–29, E 30–35, F 36–39, G 40–45,
> H 46–48** — **48 buchi in tutto**, su 81 video letti per intero.
> **Restano buchi identificati, non lavoro approvato**: la decisione su cosa implementare si prende con l'utente a
> distillazione finita.

### Priorità 1 — cambiano il verdetto di un test (economici, subito)

| # | buco | perché primo | dove |
|---|---|---|---|
| 37 | **errore standard della stima Monte Carlo** mai riportato | con 1.000 permutazioni il SE di un p-value vicino a 0,05 vale ~0,7 punti: "p = 0,048" e "p = 0,062" **non sono distinguibili** (F2). Tocca ogni verdetto vicino alla soglia e la futilità DSR | `core/quant_metrics.py`, `04` |
| 41 | **finestra di misura del conto live** non pre-registrata | la fonte mostra Sharpe **0,88 vs 6,28 sullo stesso conto** cambiando la data d'inizio (G3). Per le strategie il periodo è pre-registrato, per il conto no | `docs/QUANT_REVIEW_PROTOCOL.md`, healthcheck |
| 46 | **correlazioni senza frequenza né finestra dichiarate** | JNJ/CMG: 0,01 annuale, 0,13 mensile, **0,17 giornaliera con punte a 0,73** (H2). Due attivi "scorrelati" possono essere quasi identici proprio nella finestra in cui si subisce il drawdown | tutte le pre-registrazioni che citano correlazioni |
| 2 | **potenza e dimensione campionaria** $n\approx(z\sigma/E)^2$ | senza potenza un NO-GO non distingue "non c'è edge" da "non potevo vederlo": con E=+0,04R servono ~36.000 trade (B22) | pre-registrazione, `04` |
| 20 | **filtraggio vs lisciamento** | criterio generale contro il look-ahead; oggi il repo copre solo il caso della regime timeline | `04` §1 |
| 5 + 28 | **monitoraggio forward per gamba** e **deriva con soglie pre-registrate** (CUSUM/SPRT, innovazioni) | oggi §8bis guarda solo drawdown e serie negative: il degrado di win rate o payoff passa inosservato | §8bis, core |
| 22 | **backtest per eccedenze** delle soglie dichiarate | verifica se una soglia "peggior 5%" lo è davvero; si applica a §8bis, risk gate, percentili MC | core, §8bis |
| 27 | **attesa analitica di una serie di $k$ perdite** $\sum q^{-i}$ | dà un riferimento al `max_consecutive_losses: 4` che oggi non è motivato da nulla | `config/risk.yaml`, §8bis |
| 29 | **test di indipendenza degli esiti** (runs test) | tutte le soglie i.i.d. dipendono da un'ipotesi mai verificata | `04`, core |

### Priorità 2 — rendono dimensionabile ciò che oggi è a soglia fissa

| # | buco | dove |
|---|---|---|
| 14 | **capitale a rischio per trade** (il gate limita solo il nozionale) | `core/risk_gate.py`, `config/risk.yaml` |
| 16 | **proprietà del Kelly frazionario** ($f^*$, parabola $g(f)$, $P(x)=x$, $k(2-k)$, asimmetria) | `05` |
| 15 | **probabilità di toccare un obiettivo prima di un limite** | `docs/PROP_FIRM_CRITERIA.md`, §8bis |
| 13 | **simulazioni con incertezza sui parametri** (non plug-in) | §8bis |
| 39 | **soglie di §8bis come probabilità di violazione** invece che come percentili (ricetta a variabile indicatrice, F1) | §8bis, core |
| 45 | **confronto fra alternative sul decile peggiore dei percorsi**, non sulla media (G6: il segno del CAGR cambia) | `core/quant_metrics.py`, `04` |

### Priorità 3 — disciplina di metodo già quasi nostra, da scrivere

| # | buco | dove |
|---|---|---|
| 11 | **ablazione pre-registrata** per una componente aggiunta a una regola | STRATEGY_LIFECYCLE |
| 33 | **test di perturbazione** generalizzato agli input, con soglia dichiarata | `04` §2 |
| 8 | **checklist assunzioni → direzione dell'errore** | template di pre-registrazione, `04` §9 |
| 24 + 25 | **transizioni impossibili**; **errore standard** delle probabilità stimate | `04`, `03` |
| 10 | **esiti censurati** dalle regole di uscita | `04` |
| 12 | **vantaggio × P(esecuzione)** e selezione avversa, con $\lambda(\text{spread})$ | `02`, `04` |
| 9 | terminologia **stazionarietà** (W3, riga ADF del reviewer) | pre-registrazioni, `agents/quant_reviewer.md` |
| 21 | regressioni su **livelli** e cointegrazione | `04` |
| 38 | **ripetizione su più semi** in verifica (il seme resta dichiarato e fisso nella pre-registrazione) | pre-registrazione + verifica |
| 40 | criterio di **scelta** "positivo ovunque" invece di "ottimo da qualche parte" (G2) | STRATEGY_LIFECYCLE, pre-registrazione |
| 43 | **problema dell'ipotesi congiunta**: un alpha a un fattore è indistinguibile da un'esposizione non modellata | `04`, `05`, docstring di `benchmark_metrics` |
| 47 | **quota di tempo in contante / accessibilità del capitale** (H3; il PAC è a serbatoio) | `analysis/ops/weekly_healthcheck.py` |
| 48 | **ortogonalità misurata dentro le finestre di drawdown**, non su tutto il campione | core, `05` |
| 44 | **elenco dei riferimenti fondativi** (Bachelier, Sharpe, Black-Scholes, Dupire, Carr-Madan) | `_INTAKE.md` o `RIFERIMENTI.md` |

### Priorità 4 — utili quando il perimetro si allargherà

| # | buco | quando serve |
|---|---|---|
| 23 | modello di **volatilità condizionata** (GARCH) per regime assoluto e sizing | quando il gate di regime o il vol targeting diventano operativi |
| 26 | **HMM filtrato, non lisciato** | se si implementa il blueprint Markov |
| 18 | **ribilanciamento** (regola, banda, versamenti nuovi) | quando il glide-path introduce la gamba difensiva |
| 30 | **beta e alpha mobili con intervallo** | quando ci sarà più di una gamba |
| 31 | **Sharpe in quadratura** per decidere se una gamba vale | prima di aggiungere un flusso |
| 32 | rimedi all'**errore di stima** in ottimizzazione (shrinkage, 1/N, min-varianza) | se mai si ottimizzasse |
| 34 | **stabilità della struttura fattoriale** (PCA mobile) | multi-asset |
| 1 | **autocorrelazione nell'annualizzazione** dello Sharpe | quando si annualizza su serie autocorrelate |
| 3 | **coda pesante**: indice di coda, stabilità della media | lead trend/playground |
| 4 | **scomposizione E[R] nel tempo** | healthcheck |
| 6 | regime di volatilità **relativo** dichiarato come tale | `03`, docstring di `core/regime.py` |
| 7 | **beta condizionato** (payoff convessi letti da un modello lineare) | se si valuta una copertura |
| 17 | vincolo contro il **monitoraggio a finestre mobili** | insieme al buco 5 |
| 19 | **stress test per scenari** sulle posizioni | risk gate |
| 35 | **regola di ribilanciamento** (cadenza o banda) + ribilanciamento via **versamenti nuovi** per non realizzare plusvalenze al 26% — specifica il buco 18 | quando il glide-path introdurrà la gamba difensiva |
| 36 | **riduzione della varianza** nel Monte Carlo (variate di controllo) — *catalogato, manca l'ingrediente* | se mai si simularà un processo costoso |
| 42 | **pesi dichiarati fra attività** (PAC, segnali mentore, prove) | quando più di una gamba avrà capitale |

---

## Conflitti per la mappa dei modelli

> Da riportare in `DECISIONS.md` §Mappa dei modelli con la model card minima
> (`claim · fonte · condizioni · contraddice · stato`). **La dottrina della mappa dei modelli è: registrare le
> condizioni di validità, non arbitrare** ([[project_knowledge_intake_modelmap_2026_06]]). Nessuno dei conflitti qui
> sotto riapre una decisione presa.

**14 conflitti in tutto**: 5 in B, 4 in C, 1 in D, 2 in E, 3 in G (F e H non ne producono). I dettagli e le citazioni
stanno nei rispettivi file di blocco; qui c'è l'elenco con lo **stato**.

| # | affermazione della fonte | condizioni di validità | contraddice | stato |
|---|---|---|---|---|
| B1-B5 | 5 conflitti del blocco B, fra cui *"condizionare finché le distribuzioni si separano"* e *"l'analisi tecnica non si può confutare"* | vedi [`blocco-B.md`](blocco-B.md) | budget dei trial; NULL a 384 trial | **nessuna revisione** |
| C1-C4 | 4 conflitti del blocco C, fra cui *"la rovina è certa anche con un vantaggio"* (**falso**, ricalcolato: 88,4%) e C7 vs pilastro PAC | vedi [`blocco-C.md`](blocco-C.md) | — | **numeri corretti da noi** |
| D1 | conflitto del blocco D (lisciamento usato come segnale) | vedi [`blocco-D.md`](blocco-D.md) | `04` §1 | **nessuna revisione** |
| E1 | **Black-Litterman** (una vista soggettiva entra nel modello) vs *"il qualitativo genera ipotesi, non valida"* (`04` §9) | vista **dichiarata prima**, **quantificata** con fiducia esplicita, **ancorata** a un prior indipendente, **verificabile** dopo | `04` §9 | **non è un conflitto** se si tengono le condizioni |
| E2 | *"diversificare è protezione dall'ignoranza; concentra se sai quello che fai"* (Buffett, via E4) | capacità di selezione **dimostrata** + sopravvivenza al drag | `08` (pilastro passivo) | **nessuna riapertura** |
| G1 | *"l'analisi tecnica non si può confutare"* (G2, **fonte primaria** del conflitto già visto in B) | vero per l'**abilità discrezionale** di chi sceglie quando applicare una regola; falso come affermazione generale | la lettura ingenua secondo cui il NULL sui livelli chiuderebbe anche il discrezionale | **il NULL resta**; si aggiunge la precisazione che falsifica **regole meccaniche** e che il discrezionale si misura col **track record prospettico pre-registrato** — strada già percorsa per il mentore |
| G2 | *"non è la domanda se l'alpha sia consistente e statisticamente significativo"* (G4, analogia del fuoricampo) | coerente per un **allocatore con mandato**, che opera comunque | `docs/STRATEGY_LIFECYCLE.md` e [[feedback_mass_search_vs_preregistration]] per chi deve **decidere se accendere** | **la nostra posizione resta**; si registra la distinzione fra problema di **selezione** (nostro) e di **esecuzione** (suo) |
| G3 | **gamba di copertura con monetizzazione** (E2, G6 e #29: **tre occorrenze**) | nessuna: mai un fuori campione, mai i costi, mai i parametri; conflitto d'interesse dichiarato (corso a pagamento) | — | **invariato**: resta la nota "speculativo/promozionale, da verificare" in `08`. Tre video della stessa fonte **non** fanno tre conferme |

**Una tensione interna alla fonte**, registrata perché utile a noi: F1 e G2 dicono che in finanza nulla converge e
nulla è garantito in avanti; F2 e la gamba di copertura presentano risultati con la certezza che quegli stessi video
negano. La distinzione che tiene insieme le due cose — e che la fonte non enuncia mai — è fra **rumore di simulazione**
(riducibile) ed **errore di modello** (non riducibile simulando di più).

---

## Dopo la sintesi (checklist di chiusura)

- [x] `fondamenti_tecnici/_INTAKE.md`: riga per il gruppo 1 con esito, buchi, conflitti e attribuzione risolta.
- [x] `DECISIONS.md`: voce **2026-09-17** di chiusura + **3 conflitti nuovi** nella Mappa dei modelli.
- [x] Memoria: [[project_quantguild_distill_2026_09_15]] portata a **CHIUSO**, riga di MEMORY.md riscritta.
- [x] Commit (`5f6513f`, ramo `docs/metodo-pac-2026-08-07`).
- [x] **Avviso all'utente** (richiesta esplicita).
