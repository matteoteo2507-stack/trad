---
aliases: [10_indicatori_tecnici]
titolo: "Indicatori tecnici — cosa misurano, cosa dice la letteratura, quali tenere e quali scartare"
fonti:
  - "Ricerca web di Claude, 08/10/2026: ~30 fonti, livello di verifica dichiarato per ciascuna nella sezione Fonti"
  - "Ricerca parallela via Comet, 08/10/2026: abstract trascritti di 14 paper, 25 post su X, 16 repository GitHub (_sorgenti/comet_indicatori_*_2026-10-08.md)"
  - "Evidenza interna: verdetti gia' scritti in DECISIONS.md (linkati, non copiati)"
tipo: concetti
stato: quarantena
creato: 2026-10-08
---

# Indicatori tecnici — cosa misurano, cosa dice la letteratura, quali tenere e quali scartare

> **Un indicatore non e' una fonte di vantaggio: e' un riassunto del prezzo passato.** Le centinaia di
> indicatori di TradingView si riducono a **sei grandezze** (tendenza, spostamento dalla media, volatilita',
> volume, livelli, forma della candela). La domanda utile non e' "quale indicatore funziona" ma **"quale
> grandezza misura, e chi paga se quella grandezza predice qualcosa"** ([[09_fonti_di_vantaggio]]).
> Sessant'anni di studi dicono tre cose. (1) Le regole classiche guadagnavano fino ai primi anni '90 e poi
> sono decadute; corrette per i tentativi multipli e per i costi, su un singolo mercato resta quasi niente.
> (2) Resiste la **tendenza a orizzonte di mesi su molti mercati insieme**, il **ritorno di breve come
> compenso per chi fornisce liquidita'**, e la **volatilita' come misura di rischio** (non di direzione).
> (3) Tutto cio' che si **disegna a mano** (Fibonacci, Elliott, pitchfork, Gann, trendline) non ha evidenza
> a favore e ha gradi di liberta' illimitati: Fibonacci e' stato confrontato con livelli casuali e non li
> batte; per la pitchfork nessuno, ne' in letteratura ne' su GitHub, ha mai fatto il confronto. Quasi tutta
> l'evidenza positiva sta **fuori dal nostro perimetro** (azioni singole, panieri di futures, orizzonte
> mensile, criptovalute).

## 0. Stato di questo modulo — leggere prima

- **Quarantena.** Nato da una ricerca web dell'08/10/2026 (richiesta di Matteo, in attesa dei dettagli
  dell'idea del socio su TradingView), integrata lo stesso giorno con la ricerca parallela via Comet. I due
  report grezzi sono in `_sorgenti/` ([paper e GitHub](../_sorgenti/comet_indicatori_paper_github_2026-10-08.md),
  [X](../_sorgenti/comet_indicatori_X_2026-10-08.md)) e registrati in [`_INTAKE.md`](../_INTAKE.md).
- **Livelli di verifica** (colonna della sezione Fonti):
  - **T** testo letto da Claude;
  - **A** abstract letto da Claude sulla pagina dell'editore o di IDEAS;
  - **A·C** abstract trascritto parola per parola da Comet. Controllo a campione dell'08/10 su tre abstract:
    Fibonacci e Baltussen **coincidono**; Hudson-Urquhart **diverge** (§3, eccezioni);
  - **S** sintesi del motore di ricerca, da confermare sull'abstract;
  - **X** post su X o README di GitHub: testimonianza, non evidenza, e mai fonte di un numero.
  Un claim che poggia solo su **S** o **X** resta in quarantena anche se plausibile.
- **Provenienza** ([STRATEGY_LIFECYCLE §8](../../docs/STRATEGY_LIFECYCLE.md)). Questo modulo **non genera
  ipotesi da testare**: classifica strumenti. Una regola dedotta da qui passa comunque da `_INTAKE.md` con
  una fonte umana datata.
- **Regola approvata da Matteo l'08/10:** due indicatori della stessa grandezza sono una famiglia nel
  contatore ([DECISIONS 2026-10-08 (3)](../../DECISIONS.md), [STRATEGY_LIFECYCLE](../../docs/STRATEGY_LIFECYCLE.md) §3 e §7).
- **Le strade testabili** uscite da questa ricerca sono nel [backlog, sezione H](../../docs/BACKLOG_RICERCA.md): li'
  vive il lavoro da fare, qui la conoscenza.

## Concetti

### 1. Che cos'e' un indicatore, in termini di funzione

Un indicatore e' una funzione **f(prezzi e volumi fino a t) → un numero**. Tre conseguenze:

1. **Non aggiunge informazione al prezzo: la riassume.** Puo' solo filtrare meglio o peggio. Levine e
   Pedersen (2016) mostrano che incrocio di medie mobili, momentum di serie storica, filtro di
   Hodrick-Prescott e filtro di Kalman sono **rappresentazioni equivalenti** dello stesso oggetto: un
   filtro lineare dei rendimenti passati. Cambiare indicatore di tendenza cambia i pesi sul passato, non
   la natura del segnale. Due praticanti lo dicono con parole loro (X, con conflitto d'interesse: gestiscono
   ETF di tendenza): i segnali che funzionano sono "versioni rumorose della media a 200 giorni" (W. Gray);
   un segnale binario sopra/sotto la media "spreca quasi tutti i dati", meglio uno continuo (Robot Wealth).
2. **Il ritardo non e' un difetto da curare: e' il prezzo del filtraggio.** Un indicatore "senza ritardo"
   o usa una finestra centrata (cioe' il futuro: e' lisciamento travestito da filtraggio,
   [[04_quant_metodologia]] §1) o filtra meno (piu' rumore). Non esiste il pasto gratis.
3. **Molti indicatori misurano la stessa grandezza.** RSI, Stocastico, Williams %R, CCI, %B di Bollinger
   e z-score del prezzo sono tutti "quanto si e' allontanato il prezzo dalla sua media recente, in unita'
   di ampiezza recente". Tre "conferme" da tre oscillatori sono **una conferma contata tre volte**: e' la
   stessa regola delle conferme per fonte ([[feedback_conferme_per_fonte]]) applicata agli strumenti.

### 2. Le sei grandezze

| # | grandezza | indicatori che la misurano | cosa dice la letteratura (sintesi; dettaglio sotto) | classe e chi paga ([[09_fonti_di_vantaggio]]) | nel nostro perimetro |
|---|---|---|---|---|---|
| 1 | **Tendenza** (rendimento passato) | medie mobili e loro incroci, MACD, canali di Donchian e breakout, momentum di serie storica, Supertrend, Parabolic SAR, ADX (forza), Ichimoku (in parte) | la piu' documentata, **su panieri di futures a orizzonte 1-12 mesi**; asset per asset e' debole; le regole su singolo indice sono decadute | 3 (reazione in ritardo, poi eccesso) e in parte 1 (rende nelle crisi): da confermare | TSMOM chiuso; famiglia trend ancora LEAD con la coda aperta refutata e A1 fermo per potenza: stato in `python -m core.trial_ledger` |
| 2 | **Spostamento dalla media** (oscillatori) | RSI, Stocastico, Williams %R, CCI, %B di Bollinger, z-score, distanza dalla media | il ritorno di breve sulle **azioni singole** e' il compenso per chi fornisce liquidita', e cresce col VIX; le regole classiche su indici: deboli, non corrette per i tentativi multipli | 2-3: paga chi **chiede immediatezza** (vende in fretta) | B1, mean reversion vol e FADE chiusi; RSI(2) sugli indici: stato nella sua [pre-registrazione](../../docs/MR_INDICI_RSI2_PREREGISTRATION.md) |
| 3 | **Volatilita'** (ampiezza) | ATR, deviazione standard, larghezza delle Bollinger, Keltner, VIX | il fatto stilizzato piu' robusto: la volatilita' si raggruppa nel tempo. Serve a **dimensionare e mettere stop**, non a prevedere la direzione | nessuna: e' una misura di rischio, non una fonte di rendimento | gia' in uso in `core/sizing.py`; attenzione alle soglie normalizzate ([[feedback_soglia_normalizzata_cancella_distinzione]]) |
| 4 | **Volume** (partecipazione) | OBV, VWAP, Volume Profile e POC, MFI, accumulazione/distribuzione, delta | regole OBV fra quelle utili per prevedere il premio azionario **mensile** USA; sulle materie prime non profittevoli | VWAP: e' il riferimento con cui si misurano gli esecutori istituzionali (meccanismo plausibile, fonte da acquisire) | **0 celle su 48** per POC/VAH/VAL, VWAP, VWAP ancorato (DECISIONS 2026-07-07). Su CFD e forex il volume e' **di tick**, non scambiato |
| 5 | **Livelli e struttura** | supporti e resistenze, pivot point, massimi e minimi del giorno prima, numeri tondi, Fibonacci, pitchfork, trendline, Gann, order block, FVG, zigzag, frattali | **unico meccanismo documentato**: prese di profitto ammassate sui numeri tondi, stop appena oltre (forex). Fibonacci: il prezzo rimbalza **altrettanto** su livelli qualsiasi, e la regola non batte livelli casuali. Pitchfork ed Elliott: nessuna evidenza | numeri tondi: 5 (microstruttura degli ordini). Il resto: **nessuna classe**, cioe' un pattern | livelli **384 trial, nessuno batte il casuale** (DECISIONS 2026-07-06/07); griglia a numero tondo NULL (2026-08-09); NXT Fibonacci NO-GO (2026-07-17) |
| 6 | **Forma della candela e figure** | pattern a candela, testa e spalle, triangoli, armonici (Gartley...), Heikin Ashi | candele: nessuna capacita' predittiva al bootstrap; figure riconosciute da algoritmo: qualche informazione in piu', ma "ottimo per la statistica non e' ottimo per il profitto" | nessuna | mai testate come famiglia |

**Fuori dalle sei c'e' il tempo** (sessioni, apertura, ultima mezz'ora, calendario): non e' un indicatore
ma un condizionamento, e la sua classe naturale e' la 2 (flussi ancorati a un orario). E' **l'unico punto
di questa ricerca con un "chi paga" esplicito e misurato su molti mercati**:
- Baltussen, Da, Lammers, Martens (2021, **T**): su oltre 60 futures (azioni, obbligazioni, materie prime,
  valute), dicembre 1974 - maggio 2020, il rendimento della giornata fino a mezz'ora dalla chiusura
  **predice quello dell'ultima mezz'ora**, ovunque; l'effetto si inverte nei giorni successivi. Sui futures
  azionari la strategia di solo segno rende +6,86% annuo con Sharpe 1,73 (Tab. 6), simile nei due
  sottocampioni (Tab. 5), **senza costi**. Il meccanismo: chi e' **corto di gamma** (market maker di
  opzioni, ETF a leva) deve coprirsi **nella direzione del movimento**. Chi paga: chi e' obbligato a
  coprirsi. Perche' accetta: e' un vincolo, non un errore. Scheda completa: [backlog H1](../../docs/BACKLOG_RICERCA.md).
- Gao, Han, Li, Zhou (2018, **S**): la prima mezz'ora predice l'ultima sull'ETF S&P 500, 1993-2013.
- **E' una direzione di lettura, non un'ipotesi** ([[09_fonti_di_vantaggio]] §5): cade vicino al perimetro
  gia' chiuso dell'intraday sugli indici (ORB, London breakout), dove i costi hanno ucciso tutto, quindi la
  domanda di accessibilita' (§4 punto 6 del 09) va fatta **per prima**.

### 3. La storia in quattro tappe: perche' "funzionava" non vuol dire "funziona"

1. **Fino ai primi anni '90 le regole guadagnavano davvero.** Park e Irwin (2007, **A·C**): su 95 studi
   "moderni", 56 positivi, 20 negativi, 19 misti; profitti economici in vari mercati speculativi almeno
   fino ai primi anni '90, ma **la maggior parte** degli studi ha problemi di metodo (data snooping, scelta
   delle regole a posteriori, stima del rischio e dei costi). Neely, Weller e Ulrich (2009, **S**) con test
   fuori campione veri: gli extra rendimenti degli anni '70-'80 nel forex **erano reali** e **sono spariti**
   per filtri e medie mobili entro i primi anni '90. Taylor (2014, **A**), titoli del Dow 1928-2012: profitti
   confinati a episodi, soprattutto **meta' anni '60 - meta' anni '80**.
2. **Corretti per i tentativi multipli, i vincitori spariscono fuori campione.** Sullivan, Timmermann e White
   (1999, **T**): quasi 8.000 regole sul Dow 1897-1996; nel periodo di Brock-Lakonishok-LeBaron (1897-1986)
   alcune battono il benchmark **anche dopo** la correzione, ma nei 10 anni successivi la probabilita' che
   la migliore non batta il benchmark e' quasi del 12%: *"scant evidence that technical trading rules were
   of any economic value during the period 1987-1996"*. Fang, Jacobsen e Qin (2014, **A**): le stesse regole
   di BLL su dati nuovi 1987-2011, **nessuna capacita' predittiva**; attribuiscono il successo originale a
   una distorsione, non a un mercato diventato efficiente.
3. **Anche quando il passato regge, non si sa scegliere prima.** Bajgrowicz e Scaillet (2012, **A·C**), Dow
   1897-2011 con la false discovery rate: un investitore **non avrebbe mai potuto scegliere in anticipo**
   le regole migliori, e anche in campione costi bassi annullano tutto. Rink (2023, **A**): 6.406 regole su
   41 indici azionari fino a 66 anni; in campione molte battono il buy-and-hold (di piu' negli emergenti),
   la prevedibilita' **cala drasticamente nel tempo**, e le regole migliori di recente fanno
   **significativamente peggio** del buy-and-hold dopo. Aronson (libro, Wiley 2006; risultato **S**): 6.402
   regole sull'S&P 500, nessuna significativa dopo la correzione per il data mining. Marshall, Cahan e Cahan
   (2008, **S**): 7.846 regole su 15 futures su materie prime, non profittevoli da sole.
4. **Cio' che si pubblica decade, e resta dove l'arbitraggio costa.** McLean e Pontiff (2016, **A·C**), 97
   predittori dei rendimenti azionari: rendimento **-26% fuori campione** e **-58% dopo la pubblicazione**;
   il calo e' **maggiore per i predittori che rendevano di piu' in campione**, e i rendimenti restano piu'
   alti nelle azioni ad **alto rischio idiosincratico e bassa liquidita'**, cioe' dove arbitrare e' costoso.
   Vale per le anomalie di sezione trasversale, non per gli indicatori in senso stretto, ma e' la risposta
   empirica alla domanda 3 del [[09_fonti_di_vantaggio]] (limite all'arbitraggio).

**Le eccezioni, da leggere con le loro condizioni:**
- **Forex.** Hsu, Taylor, Wang (2016, **S**): 30 valute, 45 anni, oltre 21.000 regole con test a passi,
  prevedibilita' sostanziale, piu' forte negli emergenti. Ma Zarrabi, Snaith, Coakley (2017, **A·C**): 7.650
  regole su 6 valute contro dollaro, 1994-2014, false discovery rate e costi: fuori campione **molte regole
  guadagnano per periodi brevi, nessuna in modo consistente**. La lettura comune e' la stessa: vantaggi che
  compaiono e spariscono (mercati adattivi), non una regola da tenere.
- **Spread di materie prime** (Psaradellis et al. 2023, **T**): 18.410 regole con false discovery rate,
  1990-2016; prevedibilita' molto piu' forte sugli spread di commodity che su quelli azionari e valutari;
  respingono l'idea di un declino uniforme. Fuori perimetro (spread tra futures).
- **Criptovalute.** Hudson e Urquhart (2021, **A·C**): quasi 15.000 regole di cinque classi, due mercati di
  Bitcoin e altre tre criptovalute, procedure per test multipli: prevedibilita' e profitto significativi per
  ogni classe e ogni moneta, costi di pareggio ben sopra quelli tipici. ⚠️ **Divergenza aperta**: due sintesi
  indipendenti del motore di ricerca riportano una frase che l'abstract trascritto da Comet non ha, *nessuna
  prevedibilita' per Bitcoin nel periodo fuori campione*; non verificabile l'08/10 (editore e archivi
  bloccati). Sul lato opposto, un repository GitHub (**X**: 3.669 regole su Bitcoin a 5 minuti,
  walk-forward, costi, Reality Check p = 0,85) dichiara **nessun alpha**. Fuori perimetro in ogni caso.
- **Media mobile su portafogli di azioni ad alta volatilita'** (Han, Yang, Zhou 2013, **S**): rendimenti
  anomali anche dopo i costi, poco correlati col momentum. Azioni singole: fuori perimetro.
- **Indicatori tecnici per il premio azionario mensile** (Neely, Rapach, Tu, Zhou 2014, **S**): medie
  mobili, momentum e OBV prevedono il premio azionario USA almeno quanto le variabili macro, soprattutto
  vicino ai picchi del ciclo. Orizzonte mensile, mercato aggregato.

### 4. La tendenza: la grandezza con piu' evidenza, e i suoi limiti

- **A favore.** Moskowitz, Ooi, Pedersen (2012, **S**): su 58 futures liquidi il rendimento degli ultimi 12
  mesi predice quello del mese dopo; persiste fino a un anno e poi si inverte in parte. Hurst, Ooi, Pedersen
  (2017, **A·C**): mercati globali dal 1880, rendimento medio positivo **in ogni decennio**, bene in **8 delle
  10** peggiori crisi di un portafoglio 60/40, e in tutti i contesti macro (recessioni e espansioni, tassi e
  inflazione alti e bassi).
- **Contro.** Huang, Li, Wang, Zhou (2020, **A·C**): **asset per asset** quasi nessuna evidenza, in e fuori
  campione; la t-statistica grande della regressione congiunta non supera i valori critici del bootstrap; la
  strategia guadagna, ma **quasi quanto una che usa solo la media storica** e non richiede prevedibilita'.
  Tradotto: buona parte del guadagno viene dall'essere esposti, nel tempo, ad asset con rendimento medio
  positivo, non dal prevedere.
- **Piste aperte da X** (da acquisire, oggi solo **X**): *Boundaries of Time Series Momentum* (Suominen,
  Hjalmarsson, segnalato da Quantpedia e Swedroe ad agosto 2026): la tendenza regge nei cicli normali e si
  **rompe e inverte agli estremi di valutazione**; *VIX and Trend Following Revisited* (Alpha Architect,
  "quasi un decennio fuori campione", conflitto d'interesse: vendono ETF).
- **Per noi.** E' esattamente cio' che abbiamo trovato in casa: a parita' di tempo in mercato la regola di
  tendenza A1 **perde da un'entrata casuale**, il vantaggio era il tempo in mercato (DECISIONS 2026-09-21).
  E la tendenza vive su **panieri ampi**: con pochi CFD la potenza manca (A1 fermo al punto 2).

### 5. Lo spostamento dalla media: c'e' un "chi paga", ma su un altro mercato

- **Il meccanismo.** Nagel (2012, **A·C**): il rendimento delle strategie di inversione di breve sulle azioni
  e' un'approssimazione del **compenso per fornire liquidita'**; e' molto prevedibile col VIX, e rendimenti
  attesi e Sharpe condizionali **salgono di colpo** nelle fasi di turbolenza. Classe 2-3 con un pagatore
  preciso: chi vuole uscire **subito**.
- **Coerente con il limite all'arbitraggio** (§3.4): un post su X (**X**, D. Bianchi) riporta che nelle
  criptovalute il rendimento della fornitura di liquidita' sta quasi tutto nelle coppie di "bassa qualita'".
  Un altro (**X**, QuantSeeker) che l'inversione classica si e' indebolita e torna con varianti (residua o
  relativa al settore, finestre piu' corte, lontano dalle notizie): paper non nominato, pista da acquisire.
- **Le regole classiche.** Bollinger: dopo i costi non battono il buy-and-hold, meglio usate al contrario
  (Lento et al. 2007, **S**). MACD e RSI a parametri fissi: rendimenti anomali in alcuni indici OCSE
  (Chong, Ng, Liew 2014, **S**), ma su poche regole scelte, senza correzione per i tentativi multipli:
  evidenza debole.
- **Per noi.** La famiglia piu' vicina, RSI(2) sugli indici USA, e' il candidato A: lo stato vive nella sua
  [pre-registrazione](../../docs/MR_INDICI_RSI2_PREREGISTRATION.md) e nel contatore, non qui.

### 6. La volatilita': robusta, ma e' rischio, non direzione

- Cont (2001, **S**): i rendimenti non hanno autocorrelazione lineare significativa (salvo scale
  intragiornaliere di ~20 minuti), mentre le misure di volatilita' sono **positivamente autocorrelate per
  piu' giorni**. E' il motivo per cui ATR e deviazione standard **prevedono l'ampiezza** dei movimenti futuri
  e non il loro segno.
- Anche usarla per dosare l'esposizione non e' gratis: su 103 strategie azionarie i portafogli gestiti per
  volatilita' **non battono sistematicamente** quelli non gestiti in confronto diretto per un investitore
  in tempo reale (Cederburg et al. 2020, **S**).
- **Uso corretto:** dimensione della posizione, distanza degli stop, filtro di regime. Mai come segnale di
  ingresso direzionale da solo.

### 7. Livelli disegnati a mano: perche' non si possono validare cosi' come sono

- **Numeri tondi: l'unico meccanismo.** Osler (2003, **A·C**), primi dati su ordini individuali di stop e
  presa di profitto nel forex: le **prese di profitto** si ammassano sui numeri tondi (spiegherebbe le
  inversioni ai livelli), gli **stop appena oltre** (spiegherebbe le accelerazioni dopo la rottura). Il
  nostro primo test sul Nasdaq e' nullo ([pre-registrazione](../../docs/ROUND_NUMBER_GRID_PREREGISTRATION.md)).
- **Fibonacci: confrontato con il caso, non lo batte.** Tsinaslanidis, Guijarro, Voukelatos (*Expert Systems
  with Applications* 187, 2022, **A·C** controllato): zone costruite attorno ai livelli 23,6 / 38,2 / 61,8 /
  100% per togliere la soggettivita' del disegno; azioni di Dow Jones, NASDAQ e DAX, 1968-2019. Il prezzo
  **rimbalza altrettanto su livelli non Fibonacci**, e una regola di trading sui livelli Fibonacci **non
  batte una regola su livelli scelti a caso**; zone piu' larghe trovano piu' rimbalzi, ma il risultato di
  trading resta scarso a ogni larghezza. E' lo stesso risultato della nostra ricerca livelli: reazione
  identica fra livello vero e punto arbitrario alla stessa distanza (DECISIONS 2026-07-06). Gli studi "a
  favore" che circolano non hanno il controllo: 4 titoli per un trimestre, nessuna zona di confronto
  (Shaker et al. 2018, **A**). Su GitHub (ricerca Comet) **nessun repository** confronta Fibonacci con
  livelli casuali.
- **Pitchfork (median line di Andrews).** Nessuna validazione con revisione paritaria; su GitHub **nessun
  repository** la testa contro linee casuali; su X solo aneddoti (ricerca Comet 08/10). La regola tramandata
  ("il prezzo torna sulla mediana l'80% delle volte") non e' mai confrontata con una linea casuale, e la
  mediana sta per costruzione in mezzo all'oscillazione recente: tornarci spesso e' atteso anche nel rumore.
  Si costruisce da **tre pivot**, che si confermano solo barre dopo: e' il primo sospettato di look-ahead di
  prezzo ([[feedback_fill_ottenibile]]). Il nostro motore `analysis/level_research/` fa gia' il confronto
  con livelli casuali alla stessa distanza: non ne abbiamo trovato un equivalente pubblico.
- **Onde di Elliott.** Regole abbastanza lasche, e onde annidabili a piacere, da adattarsi a **qualsiasi**
  tratto di storia: per Aronson non e' una teoria ma un racconto (**S**). **Non falsificabile.**
- **Gann, armonici (Gartley e simili).** Nessuna evidenza trovata; i livelli armonici sono gia' esclusi in
  [01_price_action](../01_price_action/principles.md) e in [TRADING_PRINCIPLES](../../TRADING_PRINCIPLES.md) §4.

### 8. Le otto illusioni: come un indicatore sembra utile senza esserlo

1. **Il cervello vede figure anche nel caso.** Roberts (1959, **S**): grafici generati da numeri casuali,
   mostrati ad analisti tecnici, ricevevano consigli di acquisto e vendita come grafici veri.
2. **Ridisegno.** La documentazione di TradingView (**A**) elenca le cause: valori della barra ancora aperta,
   `request.security` su timeframe superiore, `varip`, `barstate.isnew`, `timenow`, strategie con
   `calc_on_every_tick`, **disegno nel passato** (pivot, zigzag, frattali che compaiono su barre precedenti
   quando si confermano) e revisioni dei dati. Sullo storico l'indicatore vede cio' che dal vivo non avrebbe
   visto. E' il look-ahead di prezzo che ha tenuto in piedi il FADE per due mesi. Su X il tema torna in
   molti racconti di backtest crollati dal vivo (**X**, senza campione: non si usano i numeri; il "90% degli
   script ridisegna" viene da chi vende un servizio di conversione TradingView→MT5).
3. **Prezzi sintetici.** Su Heikin Ashi, Renko, Kagi, Point & Figure e Range i backtest di TradingView
   riempiono ai prezzi del grafico sintetico, non a quelli di mercato; TradingView stesso lo scrive (**S**).
4. **Disegno a scelta.** Quale swing, quale ancora, quale timeframe: scelti **guardando il grafico**. Il
   risultato e' in campione per costruzione, e i gradi di liberta' non si contano. Lo studio su Fibonacci
   (§7) ha dovuto costruire zone automatiche proprio per toglierli.
5. **Tasso di base mancante.** "Il prezzo rispetta il livello" senza dire quanto spesso rispetta un livello
   **qualsiasi** alla stessa distanza. Da noi il confronto ha chiuso 384 trial; nello studio su Fibonacci,
   lo stesso.
6. **Conferme ridondanti.** Piu' oscillatori della stessa grandezza = un segnale solo (§1).
7. **Selezione sul tester.** Strategy Tester + parametri ritoccati + libreria pubblica con migliaia di script:
   affiora cio' che e' andato meglio sul passato. Rink (2023): le regole migliori di recente fanno peggio
   dopo. E' il problema della ricerca di massa ([[feedback_mass_search_vs_preregistration]]). Sinclair (**X**):
   il numero di trader che vincono con l'RSI non dice niente senza il numero di quelli che perdono.
8. **Decadimento.** Cio' che era vero negli anni '70-'80 e' nei libri, quindi negli script, quindi
   arbitraggiato (§3.4).

## 9. La lista: cosa tenere, cosa trattare con cautela, cosa scartare

"Scartare" qui vuol dire **come fonte di segnale**, con il motivo dichiarato: refutato con potenza (R),
non falsificabile (NF), artefatto di calcolo (AC), oppure ridondante con un'altra grandezza (RD).
Un indicatore non dimostrato non e' refutato ([[feedback_verdetto_con_la_forza_del_test]]).

| indicatore o strumento | grandezza | verdetto | perche' |
|---|---|---|---|
| **ATR, deviazione standard, range, larghezza Bollinger** | 3 | **tenere** come misura di rischio | volatilita' raggruppata (Cont 2001). Non per la direzione |
| **Medie mobili, breakout di canale, momentum di serie storica** | 1 | **tenere, uno solo**: sono la stessa cosa | evidenza piu' lunga (1880-oggi) ma su panieri ampi a orizzonte di mesi; asset per asset debole (Huang 2020) |
| **Oscillatore corto (RSI 2-3, z-score) come fornitura di liquidita'** | 2 | **tenere come ipotesi sulle azioni singole** (fuori perimetro) | Nagel 2012 sulle azioni; sugli indici il candidato A e' **CLOSED per potenza** (DECISIONS 2026-10-08 (4)) |
| **Numeri tondi** | 5 | **tenere come meccanismo**, non come regola | Osler 2003 sul forex; nostro primo test sul Nasdaq NULL |
| **Momentum dell'ultima mezz'ora** | tempo | **tenere come direzione di lettura** (classe 2) | Baltussen 2021: 60+ futures, chi paga = chi copre la gamma; accessibilita' da verificare per prima → [backlog H1](../../docs/BACKLOG_RICERCA.md). **Nostro test sugli indici USA dal 2020: CLOSED il 12/10** (DECISIONS 2026-10-12 (2)): l'effetto pubblicato non si ritrova sui CFD dopo il campione del paper |
| MACD, RSI 14 a 30/70, Stocastico, Williams %R, CCI | 2 (MACD: 1) | **cautela** (RD) | varianti delle grandezze 1-2; poche prove positive, senza correzione per i tentativi multipli |
| Bollinger come segnale di ingresso | 2 | **cautela** | non battono il buy-and-hold dopo i costi (Lento 2007) |
| Ichimoku | 1 | **cautela** | coi parametri standard funzionava nel primo sottoperiodo e non nel secondo; sul forex nessuna regola profittevole nemmeno variando i parametri (Deng et al. 2021) |
| ADX, Parabolic SAR, Supertrend, Aroon | 1 | **cautela** (RD) | nessuna evidenza specifica trovata; sono filtri di tendenza con altri pesi (Levine-Pedersen) |
| OBV e indicatori di volume | 4 | **cautela** | utili solo per il premio azionario mensile aggregato (Neely 2014); su CFD il volume e' di tick |
| Regole tecniche sul forex | 1-2 | **cautela** | vantaggi che compaiono per periodi brevi e spariscono (Zarrabi 2017, Neely 2009) |
| Regole tecniche sulle criptovalute | 1-2 | **cautela, fuori perimetro** | positive in campione su 15.000 regole (Hudson-Urquhart 2021), Bitcoin fuori campione in dubbio (§3) |
| Massimo a 52 settimane | 1/5 | **cautela, fuori perimetro** | ancoraggio documentato sulle azioni singole (George, Hwang 2004) |
| Figure riconosciute da algoritmo (testa e spalle...) | 6 | **cautela** | qualche informazione in piu' sulle azioni (Lo, Mamaysky, Wang 2000); sul forex 1973-1994 testate contro il random walk (Osler, Chang 1995), esito non letto |
| **Fibonacci (ritracciamenti, estensioni)** | 5 | **scartare** (R) | rimbalzi uguali su livelli qualsiasi, regola peggiore o pari a livelli casuali (Tsinaslanidis et al. 2022); nostro NXT NO-GO e livelli NULL |
| **Onde di Elliott** | 5 | **scartare** (NF) | si adattano a qualunque storia |
| **Pitchfork / median line** | 5 | **scartare come regola nota**, testabile solo come ipotesi nuova (§10) | nessuna evidenza ne' repository con controllo casuale; "80%" senza linea di controllo; costruita da pivot |
| **Gann, armonici** | 5 | **scartare** (NF) | nessuna evidenza; livelli non standard gia' esclusi |
| **Supporti/resistenze, pivot point, massimi/minimi del giorno prima, order block, FVG** | 5 | **scartare come zone di reazione** (R) | 384 trial, nessuno batte il casuale |
| **Volume Profile, POC, VWAP come zone di reazione** | 4/5 | **scartare** (R) | 0 celle su 48 (DECISIONS 2026-07-07) |
| **Pattern a candela singoli** | 6 | **scartare** (R) | nessuna capacita' predittiva al bootstrap (Marshall, Young, Rose 2006) |
| **Heikin Ashi, Renko, Range come base di un backtest** | — | **scartare** (AC) | riempimenti a prezzi sintetici |
| **Zigzag, frattali, pivot non confermati, `request.security` senza offset** | — | **scartare finche' ridisegnano** (AC) | look-ahead |
| **"Confluenza" di piu' oscillatori** | 2 | **scartare** (RD) | un segnale contato piu' volte; la nostra conf=2 e' NO-GO (DECISIONS 2026-07-05) |

**La lettura che conta per noi.** Nel nostro perimetro (CFD su oro, indici e valute, da intraday a
giornaliero, pochi strumenti) gli indicatori sono soprattutto **strumenti di rischio** (grandezza 3), non
di segnale. Le grandezze con evidenza di segnale (1 e 2) l'hanno su panieri ampi o su azioni singole, cioe'
dove noi non siamo; dove siamo, le abbiamo gia' misurate e sono chiuse (l'ultima, RSI(2) sugli indici, l'08/10). L'unica pista
nuova emersa da questa ricerca **con un "chi paga" misurato** e' il tempo (ultima mezz'ora, coperture di
gamma), che e' un flusso, non un indicatore. L'abbiamo misurata il 12/10 su S&P 500 e Nasdaq dal 2020: chiusa anche
questa (DECISIONS 2026-10-12 (2)).

### 10. Come smistare un indicatore di TradingView in cinque minuti

Prima di qualunque test, in quest'ordine. Ci si ferma alla prima risposta che chiude.

1. **Quale grandezza misura?** (§2) Se e' una delle sei gia' coperte, si eredita il loro verdetto.
2. **Ridisegna?** (§8.2) Si chiede il codice Pine: senza codice, la risposta e' "non si sa", e chiude.
   Esistono analizzatori statici del codice Pine che cercano proprio queste cause (catalogati l'08/10 dalla
   ricerca Comet, **non installati**: codice di terzi, da valutare prima per licenza e per cosa esegue):
   `edgeless-ai/pinescript-mcp` (look-ahead, ridisegno, `security`, `timenow`, `barstate`, `varip`),
   `MoDarK-MK/PineScript-Skill` (63 regole), e per tradurre il Pine in Python `PyneSys/pynecore`.
3. **Si calcola e si riempie su prezzi veri?** (§8.3)
4. **Ha parametri o ancore scelti guardando il grafico?** Se si', serve una regola scritta **prima** e
   una baseline di linee o livelli casuali, come nella ricerca livelli.
5. **Chi paga?** ([[09_fonti_di_vantaggio]] §4) Senza risposta e' un pattern: va in `_INTAKE.md` come
   segnalazione, non in pre-registrazione.
6. **Quante varianti sono state provate** prima di arrivare a questa? E' il numero di candidati che alza
   la soglia.

**Esempio svolto:** l'indicatore "Volume-Trend Order Block Engine" portato dal socio il 09/10
([intake](../../docs/reviews/indicatore_ob_bigbeluga_intake_2026-10-09.md)): segnale causale ma zona disegnata
nel passato, filtro sul volume probabilmente vero per costruzione, stessa grandezza di due famiglie chiuse.

## Regole operative

- **Un indicatore si classifica per grandezza prima di discuterne.** Il nome commerciale non conta.
- **Due indicatori della stessa grandezza sono un candidato, non due**, e nel contatore stanno nella
  stessa famiglia (approvata l'08/10: DECISIONS 2026-10-08 (3), STRATEGY_LIFECYCLE §3). Un indicatore nuovo
  della stessa grandezza di una famiglia CLOSED non la riapre (§7).
- **Un backtest di TradingView non e' un risultato**: si legge il codice, si riscrive la regola, si testa
  da zero sui nostri dati, come per il backtest di un venditore ([[project_terzo_socio_2026_09_17]]).
- **Un indicatore che ridisegna e' escluso** finche' non esiste una versione confermata alla chiusura.
- **Gli strumenti disegnati a mano si testano solo come ipotesi nuova**: ancoraggio scritto prima, linee
  di controllo casuali, conteggio dei trial. Altrimenti restano strumenti di lettura, non di segnale.
- **La volatilita' entra nel rischio, non nel segnale.**
- **Un post su X o un README non e' una fonte di numeri**: e' una pista da acquisire o una testimonianza.

## Collegamenti

- [[09_fonti_di_vantaggio]] — la griglia "chi paga" che questo modulo applica agli strumenti.
- [BACKLOG_RICERCA §H](../../docs/BACKLOG_RICERCA.md) — le strade testabili uscite da qui, con il primo passo di ciascuna.
- [[04_quant_metodologia]] — filtraggio contro lisciamento (§1), overfitting e data snooping (§2).
- [01_price_action](../01_price_action/principles.md) e [TRADING_PRINCIPLES](../../TRADING_PRINCIPLES.md) §4 — Fibonacci e livelli armonici.
- [LEVEL_RESEARCH_PREREGISTRATION](../../docs/LEVEL_RESEARCH_PREREGISTRATION.md) — il confronto con livelli casuali.
- [STRATEGY_LIFECYCLE](../../docs/STRATEGY_LIFECYCLE.md), [QUANT_REVIEW_PROTOCOL](../../docs/QUANT_REVIEW_PROTOCOL.md).
- `prop-lab/lab/indicators.py` — gli indicatori gia' implementati (SMA, EMA, ATR, RSI, z-score, livelli del giorno prima, range di sessione).
- [[feedback_fill_ottenibile]], [[feedback_mass_search_vs_preregistration]], [[feedback_conferme_per_fonte]].

## Fonti

Verificate l'08/10/2026. Livelli: **T** testo, **A** abstract letto da Claude, **A·C** abstract trascritto
da Comet (controllato dove indicato), **S** sintesi del motore di ricerca, **X** post o README.

| fonte | cosa ne prendiamo | livello |
|---|---|---|
| Sullivan, Timmermann, White, *Journal of Finance* 54(5), 1999 | ~8.000 regole sul Dow 1897-1996; i vincitori 1897-1986 non hanno valore 1987-1996 | T (working paper LSE FMG DP303, pp. 1-4) |
| Psaradellis, Laws, Pantelous, Sermpinis, *International Journal of Forecasting* 39(1), 2023 | 18.410 regole, FDR, spread 1990-2016: prevedibilita' sugli spread di commodity | T (versione autore, abstract) |
| Fang, Jacobsen, Qin, *Review of Financial Economics* 23(1), 2014 | regole BLL fuori campione 1987-2011: nessuna capacita' predittiva | A |
| Rink, *Financial Markets and Portfolio Management* 37(4), 2023 | 6.406 regole, 41 indici: in campione si', nel tempo cala, non persistente | A |
| Taylor, *Journal of Banking & Finance* 40, 2014 | profitti confinati a episodi, meta' '60 - meta' '80 | A |
| Deng, Yu, Wei, Yang, Tatsuro, *International Journal of Finance & Economics* 26(4), 2021 | Ichimoku: primo sottoperiodo si', secondo no; forex nessuna | A |
| Shaker, Asad, Zulfiqar, *Int. Journal of Economics and Financial Research* 4(6), 2018 | esempio di studio "a favore" di Fibonacci senza controllo | A |
| TradingView, Pine Script docs, *Repainting* | le cause del ridisegno | A (pagina ufficiale) |
| Tsinaslanidis, Guijarro, Voukelatos, *Expert Systems with Applications* 187, 2022 (doi 10.1016/j.eswa.2021.115893) | Fibonacci = livelli qualsiasi; la regola non batte livelli casuali; DJIA, NASDAQ, DAX 1968-2019 | A·C, controllato (autori e conclusione) |
| Baltussen, Da, Lammers, Martens, *Journal of Financial Economics* 142, 377-403, 2021 | momentum dell'ultima mezz'ora su 60+ futures 1974-2020, dalle coperture di gamma; Tab. 5-6, nessun costo | T (PDF dal sito di un autore, letto l'08/10; abstract di Comet coincide) |
| Hudson, Urquhart, *Annals of Operations Research* 297, 191-220, 2021 | ~15.000 regole su criptovalute: positive con test multipli | A·C, ⚠️ diverge: la frase su Bitcoin fuori campione manca nella trascrizione (§3) |
| Park, Irwin, *Journal of Economic Surveys* 21(4), 786-826, 2007 | 95 studi moderni (56 / 20 / 19); profitti fino ai primi '90; problemi di metodo | A·C |
| Bajgrowicz, Scaillet, *Journal of Financial Economics* 106(3), 473-491, 2012 | FDR sul Dow 1897-2011: non selezionabili prima, annullati dai costi | A·C |
| Huang, Li, Wang, Zhou, *Journal of Financial Economics* 135(3), 774-794, 2020 | asset per asset debole; profitto come strategia della media storica | A·C |
| Osler, *Journal of Finance* 58(5), 1791-1819, 2003 | prese di profitto sui numeri tondi, stop appena oltre | A·C |
| Hurst, Ooi, Pedersen, *Journal of Portfolio Management* 44, 15-29, 2017 | tendenza positiva in ogni decennio dal 1880, 8 crisi su 10 | A·C |
| McLean, Pontiff, *Journal of Finance* 71(1), 5-32, 2016 | -26% fuori campione, -58% dopo la pubblicazione; resta dove l'arbitraggio costa | A·C |
| Nagel, *Review of Financial Studies* 25(7), 2005-2039, 2012 | inversione di breve = compenso per la liquidita', prevedibile col VIX | A·C |
| Zarrabi, Snaith, Coakley, *International Review of Financial Analysis* 49, 113-127, 2017 | 7.650 regole forex, FDR: profittevoli a tratti, non consistenti | A·C |
| Osler, Chang, FRBNY Staff Report 4, 1995 | testa e spalle sul forex 1973-1994 contro 10.000 random walk | A·C (esito non nell'abstract) |
| Marshall, Young, Rose, *Journal of Banking & Finance* 30(8), 2303-2323, 2006 | 28 segnali a candela sul Dow 1992-2002: nessuna capacita' predittiva | S (rivista A·C, abstract non disponibile) |
| Aronson, *Evidence-Based Technical Analysis*, Wiley, 2006 | 6.402 regole S&P 500: nessuna significativa; Elliott come racconto | S (anno A·C; risultato non trovato da Comet) |
| Neely, Weller, Ulrich, *JFQA* 44(2), 2009 | forex: profitti reali negli anni '70-'80, spariti nei primi '90 | S |
| Hsu, Taylor, Wang, *Journal of International Economics*, 2016 | forex 30 valute, 21.000+ regole: ancora prevedibile, piu' negli emergenti | S |
| Marshall, Cahan, Cahan, *Journal of Banking & Finance*, 2008 | 7.846 regole su 15 futures su materie prime: non profittevoli da sole | S |
| Levine, Pedersen, *Financial Analysts Journal* 72(3), 2016 | medie mobili e momentum di serie storica equivalenti | S |
| Moskowitz, Ooi, Pedersen, *Journal of Financial Economics*, 2012 | 58 futures, persistenza 1-12 mesi, inversione parziale | S |
| Neely, Rapach, Tu, Zhou, *Management Science*, 2014 | medie mobili, momentum, OBV per il premio azionario mensile | S |
| Han, Yang, Zhou, *JFQA* 48(5), 2013 | media mobile su portafogli ad alta volatilita' | S |
| Lento, Gradojevic, Wright, *Applied Financial Economics Letters* 3(4), 2007 | Bollinger: no dopo i costi, meglio al contrario | S |
| Chong, Ng, Liew, *JRFM* 7(1), 2014 | MACD e RSI positivi in alcuni indici OCSE | S |
| Lo, Mamaysky, Wang, *Journal of Finance*, 2000 | figure da algoritmo: informazione in piu', non profitto | S |
| George, Hwang, *Journal of Finance*, 2004 | massimo a 52 settimane e momentum | S |
| Gao, Han, Li, Zhou, *Journal of Financial Economics* 129(2), 2018 | prima mezz'ora predice l'ultima, SPY 1993-2013 | S |
| Cont, *Quantitative Finance* 1(2), 2001 | nessuna autocorrelazione lineare, volatilita' raggruppata | S |
| Cederburg, O'Doherty, Wang, Yan, *Journal of Financial Economics* 138, 2020 | gestione per volatilita' non batte sistematicamente fuori campione | S |
| Roberts, *Journal of Finance*, 1959 | grafici casuali letti come veri | S |
| TradingView, supporto, *Strategy produces unrealistic results on non-standard chart types* | riempimenti su grafici sintetici | S |
| Ricerca X via Comet ([report](../_sorgenti/comet_indicatori_X_2026-10-08.md)): 25 post, ~40 esclusi come promozionali | nessuna evidenza nuova; piste da acquisire (§4, §5); testimonianze sul ridisegno; i praticanti piu' favorevoli alla tendenza hanno un conflitto d'interesse | X |
| Ricerca GitHub via Comet ([report](../_sorgenti/comet_indicatori_paper_github_2026-10-08.md)): 16 repository | nessuna replica completa di Sullivan et al.; nessun test di Fibonacci o pitchfork contro il caso; Bitcoin 5 minuti senza alpha; analizzatori Pine | X |

**Da acquisire** (sposterebbero il livello verso T): Aronson (il capitolo dei risultati: e' la fonte piu'
vicina a questo modulo); Hudson-Urquhart (abstract pubblicato completo, per chiudere la divergenza su
Bitcoin); Osler-Chang 1995 (l'esito); *Boundaries of Time Series Momentum* (Suominen, Hjalmarsson); il paper
sull'inversione di breve "rianimata" citato da QuantSeeker; Huang et al. 2020 e Baltussen et al. 2021 interi.
