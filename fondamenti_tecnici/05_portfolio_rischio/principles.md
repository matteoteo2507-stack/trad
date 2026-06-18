---
titolo: Portfolio & Decomposizione del Rischio
fonti:
  - "_sorgenti/quantportfolio managernotes.txt"
tipo: concetti
---

# Portfolio & Decomposizione del Rischio

> Battere un benchmark NON equivale a generare alpha. L'alpha è il rendimento ortogonale al rischio di mercato; tutto il resto (incluso un +87% del settore tech contro un +49% dell'indice) può essere solo sovraesposizione a beta. La gestione di portafoglio consiste nel decomporre il rischio (idiosincratico, settoriale, di mercato), misurarlo con modelli quantitativi (CAPM, PCA, fattori) e targettizzare esposizioni fattoriali coerenti con gli obiettivi, monitorando esposizioni che sono per natura non-stazionarie.

## Concetti

### Alpha: rendimento ortogonale al rischio di mercato

Un errore diffuso è credere che sovraperformare un benchmark (S&P 500, NASDAQ) significhi generare alpha. Formalmente, **l'alpha è il rendimento che eccede ciò che ci si aspetterebbe dalla sola esposizione al rischio** — cioè rendimento **indipendente dai movimenti di mercato (ortogonale ai fattori di mercato)**.

Esempio: un portafoglio tech che rende 87% contro il 49% dell'indice NON ha generato alpha se quella sovraperformance deriva da sovraesposizione al beta di mercato (e infatti soffre drawdown più severi nei ribassi). Il vero alpha si genera con rendimenti indipendenti dalla direzione del mercato: trading intraday attivo, raccolta del premio di volatilità, o stock selection con effettiva skill.

### Tassonomia del rischio azionario

Tre componenti gerarchiche, distinte per diversificabilità:

1. **Rischio idiosincratico (firm-specific):** unico della singola azienda (scandali, gestione scadente, eventi straordinari). Esempio: UnitedHealth (UNH) con un -45% nel periodo di detenzione mentre il resto del settore healthcare era positivo. **Diversificabile** tenendo più titoli: un portafoglio di settore equipesato riduce drasticamente questo rischio mantenendo un rendimento medio positivo.
2. **Rischio settoriale/di industria:** eventi avversi che colpiscono un intero settore (es. regolamentazione sul tech) muovono insieme tutti i titoli del comparto. **Diversificabile** incrociando più settori.
3. **Rischio di mercato (sistematico):** ciò che resta dopo aver diversificato firm e settore. Colpisce tutti gli asset, legato a fattori macro. **NON diversificabile.**

Insight chiave: un singolo titolo espone interamente a tutti gli upside e downside idiosincratici — sconsigliato dalla teoria, dato il rendimento idiosincratico atteso mediamente negativo. Un portafoglio equipesato di 9 titoli (3 tech, 3 healthcare, 3 staples), una volta diversificati rischio firm e settore, traccia lo SPY con correlazione quasi perfetta.

### Beneficio e limiti della diversificazione

Covarianza e correlazione misurano le relazioni tra titoli:
- **Entro lo stesso settore:** correlazione positiva (influenze comuni di comparto).
- **Tra settori diversi:** correlazione vicina a zero in tempi normali (indipendenza).
- **In periodi di stress:** le correlazioni di tutti i titoli aumentano rapidamente, anche tra settori normalmente scorrelati — il beneficio della diversificazione collassa proprio quando servirebbe (es. shock tariffe inizio 2025).

### Non-stazionarietà delle correlazioni

Le serie storiche finanziarie sono **non-stazionarie**: le proprietà statistiche classiche (convergenza delle correlazioni empiriche, Legge dei Grandi Numeri, Teorema del Limite Centrale) non valgono sotto cambi di regime. Di conseguenza **le matrici di correlazione sono dinamiche e inaffidabili come predittori durante le crisi**. Stesso problema per i beta e per le esposizioni fattoriali: instabili nel tempo, richiedono monitoraggio e ribilanciamento continui.

### Volatility drag (variance drain)

La crescita di un capitale è **geometrica** (moltiplicativa periodo-su-periodo), non aritmetica. Da $V_n = \prod_{i=1}^n (1+R_i) = (1+R_G)^n$, prendendo i logaritmi e usando l'espansione di Taylor $\ln(1+x)\approx x - x^2/2$ per rendimenti piccoli, si ricava l'approssimazione fondamentale:

$$R_G \approx \bar{R} - \frac{\sigma^2}{2}$$

dove $R_G$ è il rendimento **geometrico** (la crescita composta effettiva del capitale), $\bar R$ la media **aritmetica** dei rendimenti, $\sigma^2$ la varianza. Il termine sottratto $\sigma^2/2$ è il **volatility drag** (variance drain): quanto la volatilità erode la crescita composta anche a fronte di una media positiva.

Conseguenze, in ordine di importanza operativa:

1. **EV positivo è necessario ma NON sufficiente.** Una strategia con media aritmetica positiva ($\bar R>0$, cioè "expectancy positiva") può avere **crescita geometrica nulla o negativa** se $\sigma^2$ è alta. Il conto non cresce. Questo è il buco della metrica "win_rate × RR = EV": misura $\bar R$, non $R_G$.
2. **Il geometrico è sempre ≤ dell'aritmetico**, e il gap cresce col **quadrato** della volatilità.
3. **La leva amplifica il drag in modo non-lineare.** Scalando i rendimenti per una leva $L$: la media cresce come $L$, ma la varianza come $L^2$ → il drag cresce come $L^2$. Esiste una leva oltre la quale aumentare l'esposizione **riduce** la crescita geometrica (oltre a far esplodere il drawdown). È la base matematica del **Kelly frazionario** e del perché "raddoppiare la size" non raddoppia la crescita.
4. **Massimizzare lo Sharpe ≠ massimizzare la crescita geometrica.** Sono funzioni obiettivo diverse; la frontiera efficiente Sharpe-ottima non coincide con quella growth-ottima / min-drawdown. Una variante che alza lo Sharpe ma peggiora il geometrico **non** è un miglioramento per chi compounda.

**Tradotto per il trading a R-multiple** (es. il Level Analyzer): la R per-trade è già normalizzata al rischio, quindi il drag **non si vede nella singola R** — vive nella **varianza della equity curve**, governata da (a) la frazione di capitale rischiata per trade e (b) la **correlazione/clustering tra trade**. Trade simultanei o nello stesso regime/sessione **non sono indipendenti**: la loro varianza combinata è più alta di $n$ trade iid → più drag → la frazione corretta per-trade è **più piccola** del Kelly calcolato come se fossero indipendenti.

### Orthogonal return streams: oltre la diversificazione

Estende l'idea di alpha-come-rendimento-ortogonale e di fattori PCA ortogonali. Metafora del **"gioco contro i giocatori"**: giudicare una strategia dagli esiti passati dei singoli trade/titoli (i "giocatori") è fragile e prono all'overfitting; ciò che conta è il **meccanismo che genera il rendimento** (il "gioco"). Due strategie possono essere "giocatori" diversi dello **stesso gioco** (stesso driver di rischio) → la loro combinazione è diversificazione **illusoria**.

La diversificazione classica (più titoli, più settori) fallisce nelle crisi perché le correlazioni convergono a 1 (vedi sopra). La risposta robusta non è "più asset correlati" ma **return stream fisicamente e stocasticamente indipendenti** — driver che si risolvono per cause strutturalmente diverse:

- **Indipendenza fisica**: il payoff si determina per un meccanismo causale diverso (es. l'esito di un prediction market politico non dipende dal ciclo macro; il trend-following su futures non dipende dalla direzione spot dell'azionario).
- **Indipendenza stocastica**: $R^2 \approx 0$ regredendo uno stream sull'altro (CAPM cross-stream).

Esempio canonico (managed futures): il beta azionario (SPY) e il trend-following su futures gestiti (DBMF/KMLM) hanno $R^2 \approx 0$ tra loro. Da solo il trend-following ha Sharpe e crescita molto inferiori; ma **combinato** abbassa il max drawdown del portafoglio in modo marcato. E qui si chiude il cerchio col volatility drag: **drawdown più basso = meno variance drain = miglior crescita geometrica**, anche a parità (o lieve calo) di media aritmetica. Una "sleeve" perfino a crescita geometrica **negativa**, se anti-correlata nei momenti giusti (convexity/hedge), può **alzare** la crescita geometrica del combinato — risultato controintuitivo ma corretto.

⚠️ **Caveat di evidenza** (coerente con la nota in [[08_asset_allocation_passiva]]): il **concetto** è solido e ben fondato; le **ricette commerciali** che lo accompagnano ("leva + hedge leg che batte SPY con meno drawdown") sono tipicamente supportate da **un singolo backtest in-sample a 5 anni, senza walk-forward né out-of-sample** → trattare l'idea come **principio di costruzione**, non i numeri come evidenza robusta. Il modo corretto di usarla: misurare la correlazione/$R^2$ tra i propri stream **reali** (forward, non backtest curve-fit) e chiedersi se aggiungere uno stream **abbassa il drawdown combinato**.

### Volatility risk premium (VRP) — nota di reference

**Fuori dallo scope operativo** (non tradiamo opzioni), ma chiude il cerchio della convexity sleeve
ed è l'**esempio cardine della mappa dei modelli**. L'**implied vol** (dai prezzi opzioni, invertendo
Black-Scholes) sovrastima **sistematicamente** la **realized vol**: la regressione IV-oggi vs
RV-30g-dopo ha pendenza < 1, l'istogramma IV è shiftato a destra, lo smile rende le put OTM più care
(assicurazione "prezzata cara"). Da qui due claim apparentemente opposti, **entrambi veri secondo
regime/timing**:
- **Vendere** il premio (short straddle/strangle) raccoglie il VRP **in mercato normale**, ma viene
  **devastato nei crash** (tail) se non coperto.
- **Comprare** convexity/long-vol **costa** (negative carry) ma **paga nei tail** e — collegandosi al
  volatility drag sopra — **riduce il drawdown → migliora il geometrico** nonostante il bleed
  aritmetico.

Non è una contraddizione: è la stessa cosa vista in regimi diversi → caso scuola della dottrina
[Mappa dei modelli](../../DECISIONS.md). Per noi: **reference, non operativo**. Fonte in
`_sorgenti/NOZIONI AGGIUNTIVE.txt`.

### PCA / spectral decomposition

L'Analisi delle Componenti Principali (PCA) è una decomposizione spettrale che estrae **fattori ortogonali** dalla variazione dei rendimenti, ciascuno un fattore di rischio indipendente, comprimendo 9 titoli in pochi componenti.

| Componente Principale | Varianza spiegata | Varianza cumulata | Interpretazione |
|-----------------------|-------------------|-------------------|-----------------|
| PC1                   | ~27%              | ~27%              | Fattore di mercato |
| PC2 + PC3             | n.d.              | ~60%              | Rischio settoriale / variazione |
| PC5 o PC6             | n.d.              | ~90%              | Include rischio idiosincratico residuo |

I **loading sulla PC1 hanno segno uniforme** su tutti i titoli, confermandola come fattore di mercato. Le componenti successive differenziano i settori (tech, healthcare, staples) catturando il rischio settoriale. Il rischio idiosincratico resta in larga parte non spiegato da mercato e settore — particolarmente evidente per UNH, i cui rendimenti estremi sono di origine idiosincratica.

### CAPM (Capital Asset Pricing Model)

Metodo basato su regressione per quantificare l'esposizione al rischio di mercato:

$$E(R) = R_f + \beta\,(R_m - R_f)$$

Si regrediscono i rendimenti dell'asset/portafoglio contro l'**excess return di mercato** (rendimento di mercato meno tasso risk-free).

- Se i rendimenti sono interamente spiegati dall'excess return di mercato → **nessun alpha**: la performance è guidata dal mercato.
- Se la regressione ha un'**intercetta (alpha) statisticamente diversa da zero** → rendimento indipendente dall'esposizione al rischio di mercato = **vero alpha**, indicatore di skill nello stock picking o nel timing.

Sui portafogli compositi l'alpha risulta tipicamente non significativo (rendimenti spiegati dall'esposizione di mercato). L'**R²** varia per settore: il tech mostra R² più alto (più rendimento spiegato dal mercato) rispetto a healthcare e staples. Nel dataset il mercato spiega ~27% della varianza; il resto motiva le estensioni multi-fattore.

### Beta per settore e trade-off rischio/rendimento

| Settore           | Beta (esposizione al mercato) | Comportamento |
|-------------------|-------------------------------|---------------|
| Technology        | > 1 (sovraesposto)            | Rendimenti maggiori nei bull, drawdown più severi nei bear |
| Consumer Staples  | ~0.33                         | Minore esposizione, drawdown più contenuti |
| Healthcare        | ~0.25                         | Minore esposizione, drawdown più contenuti |

Trade-off centrale: rendimenti più alti tramite esposizione al beta vs. performance più liscia e drawdown ridotti tramite diversificazione settoriale (beta < 1). Un beta > 1 è "sovraesposto" e performa peggio nei mercati ribassisti nonostante i guadagni superiori nei rialzisti.

### Estensioni del CAPM

Poiché il solo beta di mercato spiega una frazione della varianza, si ricorre a modelli multi-fattore che catturano altri rischi prezzati e possibili fonti di alpha:
- **Fama-French a 3 fattori** e a **5 fattori**.
- **Carhart** (aggiunge il fattore **momentum**).
- Altri fattori citati: sentiment, momentum, size, value.

Tutti soffrono delle stesse sfide statistiche (loading non-stazionari).

### Metriche fondamentali correlate

- **WACC (costo medio ponderato del capitale):** un tasso di sconto `r` più basso → valutazioni più alte.
- **Debt/EBITDA:** misura della leva finanziaria.

### Costruzione di portafoglio goal-driven

L'obiettivo non è "battere il mercato" ma **targettizzare le esposizioni ai fattori di rischio prezzati** (mercato, settori, altri) coerenti con gli obiettivi di investimento, bilanciando crescita desiderata e rischio accettabile.

## Regole operative

- Non confondere sovraperformance con alpha: prima di attribuirti skill, regredisci i rendimenti sul mercato e verifica che l'**intercetta sia significativa**.
- Diversifica su firm e settore per neutralizzare il rischio diversificabile, ma **non aspettarti che la diversificazione tenga nelle crisi** (le correlazioni convergono a 1).
- Tratta beta ed esposizioni fattoriali come **grandezze dinamiche**: monitora e ribilancia, non assumerle stabili.
- Definisci obiettivi chiari di rischio/rendimento e costruisci targettizzando esposizioni fattoriali, non rincorrendo il benchmark.
- Un beta > 1 va messo in conto come drawdown più severi nei ribassi, non come "edge".
- **Riporta sempre il rendimento geometrico accanto all'aritmetico.** Un EV/Sharpe positivo non garantisce crescita se $\sigma$ è alta: la metrica che compounda il conto è $R_G \approx \bar R - \sigma^2/2$, non la media.
- **Dimensiona con consapevolezza del drag**: Kelly frazionario, e ricorda che trade correlati/clusterati (stessa sessione, stesso regime) riducono la frazione ottimale **sotto** il Kelly calcolato come iid.
- **Per abbassare il drawdown (e quindi alzare il geometrico) cerca stream ortogonali** ($R^2\approx 0$), non più asset della stessa famiglia. Valuta una strategia per il suo **contributo marginale** al drawdown/crescita del book combinato, non per lo Sharpe standalone.
- **Non confondere il concetto valido (drag, ortogonalità) con le ricette levered-hedge da singolo backtest**: il primo è principio, le seconde non sono evidenza robusta.

## Collegamenti

- Repo: [`../../strategies/stock_selector/`](../../strategies/stock_selector/) — lo scoring fondamentale + RRG applica questa logica di fattori e decomposizione del rischio.
- [[06_stock_selection]] — selezione titoli a valle della logica fattoriale.
- [[03_regimi_macro]] — il rischio di mercato (sistematico) dipende dal regime; correlazioni e beta cambiano con il regime.
- [[08_asset_allocation_passiva]] — applicazione al pilastro investing (hedge-leg / managed futures) con il caveat di evidenza già calibrato lì.
- `agents/quant_reviewer.md` — l'agente quant porta volatility drag, crescita geometrica e review portfolio-level come bagaglio permanente, citando questo documento.

## Fonti

- `_sorgenti/quantportfolio managernotes.txt` (~righe 1-152) — note da video "Quant Portfolio Manager" (materiali Quant Guild / quantguild.com). La parte successiva del file (gamma exposure / Argo) non è inclusa in questo documento.
- `_sorgenti/NOZIONI AGGIUNTIVE.txt` — trascrizioni Roman Paolucci / Quant Guild su **volatility drag** (derivazione $R_G \approx \bar R - \sigma^2/2$), **orthogonal return streams** (game-vs-players, SPY+DBMF, convexity sleeve) e **volatility risk premium** (IV vs RV, smile, vendi-vs-compra assicurazione). Stessa scuola del file sopra. Tracciato in [`_INTAKE.md`](../_INTAKE.md).
