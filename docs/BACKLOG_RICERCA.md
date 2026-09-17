# Backlog di ricerca — stato al 2026-08-27 (sera)

> Inventario di tutto ciò che è sul tavolo dopo la chiusura del funnel YouTube, diviso per **cosa
> si può effettivamente farci oggi**. Non è un piano: è la base per decidere quali binari aprire.
>
> Ordine dei bucket: **A** ha un numero da confermare · **B** ha una specifica meccanica completa e
> dati per testarla · **C** migliora qualcosa che già gira · **D** non ha un percorso di test oggi.
>
> **Vincoli di budget in vigore** — da tenere presenti in ogni decisione:
> pre-registrazioni da fonte esterna **2 di 2-3 usate nel trimestre** · max **3 round di rifinitura**
> per famiglia · **holdout: una apertura per famiglia**, non per variante.

---

## A — DA CONVALIDARE (esiste un numero, non è confermato)

| # | oggetto | il numero | cosa manca | costo |
|---|---|---|---|---|
| **A1** | **Playground / gradiente di volatilità** | ρ **+0,857**, p=0,006, fra volatilità di gruppo ed E[R] su 8 gruppi | **pre-registrazione seria con holdout**. Oggi: n=8, solo **3/8 gruppi positivi su entrambi i lati**, nessun holdout, feed con **partenze scaglionate** (bond dal 2016-17) → confronto fra gruppi parzialmente confondato col periodo | 1 pre-reg |
| **A2** | **FADE** — ✅ **FAMIGLIA CHIUSA 2026-09-17: KILL**. Misurata coi soli fill ottenibili vale **E[R] = −0,250** BCa95 [−0,287; −0,210] su 5.506 trade; il +0,409 veniva per intero dal fill fantasma (46,1% dei setup). EA spento. Trial **2 di 3**, il terzo **non speso**. Vedi [DECISIONS 17/09 (4)](../DECISIONS.md) — nulla da convalidare. _(storico: test azzerato il 27/08)_ |
| **A3** | **ORB v2** — ✅ **CHIUSA 2026-08-27** | **NO-GO su 14,5 anni**, holdout gia' aperto | ⚠️ **niente**: l'utente ha **spento l'EA**. Verificato: zero posizioni, zero pendenti, ultimo ordine 25/08. La scelta §F si risolve in **F1**. I 10 trade chiusi **non vengono letti** — n=10 non ha potere contro 14,5 anni, e un P&L positivo creerebbe solo pressione a riaprire una famiglia con l'holdout esaurito. Riapertura solo alle condizioni gia' scritte in §F | **0 — fatto** |
| **A4** | **Segnali mentore XAUUSD** — ✅ **CHIUSA, voce corretta 2026-08-24** | OOS: win-rate **63,0%** vs 35,0% del lato casuale · differenza appaiata **+0,277** BCa95 [+0,193; +0,353] · **E[R] +0,194** BCa95 [+0,079; +0,289] | ⚠️ **niente**: il test e' **gia' stato eseguito e superato** il 2026-08-07 (131 segnali, 15/06→07/08, motore `analysis/mentor_signals/oos_validation.py`). E' il **primo verdetto positivo su un test pre-registrato** del workspace. La mia voce precedente (*"da verificare se e' partito"*) era sbagliata | **0 — fatto** |
| **A5** | **Audit dei risultati early-stage** | — | richiesto dall'utente e mai fatto: ricontrollare **come** sono stati ricavati i verdetti di livelli / NXT / ORB / TSMOM (look-ahead, finestre, baseline). È la fondazione su cui poggiano i NO-GO che usiamo per rifiutare cose nuove | 0 trial, tempo sì |
| **A6** | **Sensibilita' del verdetto Stage-2 del FADE** — ✅ **DECADUTA 2026-08-27** | — | non c'e' piu' un margine di cui misurare la sensibilita': il numero di partenza era un artefatto di fill. Assorbita da A2 | **0** |

---

## B — DA BACKTESTARE (spec meccanica completa + dati disponibili)

> Tutte e sei si eseguono sul feed **Dukascopy D1, 2012-2026, 27 strumenti su 8 gruppi**, già in
> repo. Nessuna richiede dati che non abbiamo.

| # | spec | fonte | perché è pronta | costo |
|---|---|---|---|---|
| **B1** | **Mean reversion Kichev** — `\|close − SMA5\|` oltre una soglia normalizzata sullo scostamento storico → entra **contro**; uscita **a tempo (1-4 giorni)** o al ritorno sulla media | Kichev (D.1) | entrata, uscita e invalidazione tutte specificate; **nessuna discrezionalità**. È la **forma canonica del FADE scritta da una fonte esterna prima che lo trovassimo** → è ciò che serve per ri-pre-registrare una regola data-derived | 1 pre-reg |
| **B2** | **Breakout Kichev** — range della barra ≥ ~2× media range ultime 5 → entra in direzione; uscita **a tempo (2-5 giorni)** o quando il momentum svanisce | Kichev (D.1) | stessa cosa: completa e senza giudizio. ⚠️ Famiglia trend/momentum: **round 2 di 3 già speso** | 1 pre-reg + 1 round |
| **B3** | **Condizione di struttura sull'estensione estrema** — N barre con **range in espansione** + **volume in espansione** → misura del comportamento successivo contro baseline random risk-matched | Marius (C3.4) + Kyle (C3.5), **indipendenti** | è una **misura descrittiva, non una regola** → nella forma corretta **non consuma trial** (stessa natura del lavoro sulle escursioni). ⚠️ Le soglie assolute delle fonti (200%/100%/80%) **non sono trasferibili**: vanno normalizzate sulla volatilità | **0 trial** |
| **B4** | **Variante di esecuzione del FADE: conferma sì / conferma no** — entrata al tocco vs entrata dopo un segnale di rientro | Kichev, unico contro sette | non è una famiglia nuova, è una **variante di esecuzione** su un lead esistente, sugli stessi dati. ⚠️ Resta comunque un **round di rifinitura da contare** | basso, ma 1 round |
| **B5** | **Casella vuota: low volume node** — detector LVN accanto a POC/VAH/VAL | Carmine, Fabio, Yush (3 fonti) | verificato nel codice: `analysis/level_research/detectors.py` testa i nodi ad **alto** volume, mai quelli a **basso**. È l'ipotesi **complementare, meccanismo opposto**. ⚠️ Costa poco tecnicamente **ed è proprio questo il rischio**: cella aggiunta a una griglia con **384 trial di NULL**, molteplicità pagata dove non l'abbiamo contata. E tutte e tre le fonti la usano **con conferma di flusso**, che non possiamo replicare → testeremmo una versione amputata | 1 pre-reg **esterna** (budget 2/2-3) |
| **B6** | **Casella vuota: trend line inclinate** | Crooks, Silfrain, Tori (3 pro) — **Ariel contro** | i 384 trial erano **solo orizzontali**. Buco reale. ⚠️ Prior basso: 1 fonte su 4 le rifiuta **con la nostra stessa motivazione** (ambiguità del tracciamento) | 1 pre-reg **esterna** |

---

## C — DA IMPLEMENTARE IN COSE CHE GIÀ GIRANO

| # | intervento | dove | nota |
|---|---|---|---|
| **C1** | ~~Allegare il razionale al forward ORB~~ ✅ **DECADUTA 2026-08-27** | — | il forward **esisteva** ed e' stato **spento**. Non c'e' piu' un binario a cui allegare un razionale: vedi §A3 |
| **C2** | ~~Decidere su BTCUSD nel FADE live~~ ✅ **RISOLTA** | prereg FADE | BTCUSD **staccato**: 0 ordini post-fix. Resta 1 solo ordine residuo EURGBP.r (0 trade chiusi, nessun effetto sul campione) |
| **C3** | **Soglie di ritiro dichiarate prima del capitale** | FADE e copier mentore | `STRATEGY_LIFECYCLE §8bis` le richiede ancorate a un percentile del maxDD Monte Carlo. **Non ancora scritte** per nessuna delle due — e il copier si avvicina al live |
| **C4** | **Sizing: rischio fisso in valuta, size derivata dalla distanza dello stop** | motore di rischio | 3 fonti indipendenti (Carmine, Desi, Ortani). Da verificare se il nostro sizing è già così o se è size fissa |
| **C5** | Soglia anti-ritardo del copier | copier | lo **shadow log dello scarto in pip** già registra il numero; manca la soglia |
| **C6** | **Livello di portafoglio + ribilanciamento** | non esiste | Kichev: due strategie anticorrelate senza ribilanciamento chiudono a 20k, **con** ribilanciamento a 31,25k. **Non richiede un edge nuovo.** ⚠️ Ha senso solo con ≥2 strategie vive: oggi non le abbiamo |

---

## D — CONCETTO ISOLATO (nessun percorso di test oggi)

| # | concetto | perché è bloccato | si sblocca se… |
|---|---|---|---|
| **D1** | **Order flow** (assorbimento, delta cumulato, big trades, book) | servono **tick + book**; 12 video del funnel ci poggiano sopra | mai, realisticamente: il dato costa e il vantaggio è di latenza |
| **D2** | **Universo small cap USA** (first red day, parabolic short) | servono market cap, float, short interest, halt, e un broker con locate | non nel nostro perimetro |
| **D3** | **PEAD / episodic pivot** | serve la **sorpresa su utili e fatturato** | è l'unico setup del funnel con supporto accademico indipendente: da ricordare se l'universo si allargasse |
| **D4** | **Momentum cross-sectional di gruppo** (Ariel) | il feed 8 gruppi **c'è** — quindi non è bloccato dai dati, è bloccato dal **budget**: famiglia trend following con round 2/3 speso | se il playground (A1) chiude e libera il ramo |
| **D5** | **Regime da VIX** | il VIX non è nel feed D1 attuale | aggiungendo la serie — ma vale la pena solo se A1 dà un segnale |
| **D6** | **Livelli condizionati al calendario macro** | **porta chiusa per decisione** (2026-08-22): moltiplica la ricerca su 384 trial di NULL, e il calendario è il posto più pubblico del mercato | solo con evidenza esterna **quantitativa** nuova |
| **D7** | **Riflessività / affollamento come misura** | servono open interest, positioning, short interest | dati non disponibili sul nostro perimetro |

---

## E — DEBITO DI PROTOCOLLO (emerso costruendo il guardiano)

Non sono ricerca: sono le cose che rendono la ricerca affidabile, e oggi mancano.

| # | debito | perché conta |
|---|---|---|
| **E1** | **Primitiva condivisa del baseline random risk-matched** | oggi è **reimplementata ad hoc in ~10 file**. È il singolo controllo che ha ribaltato il verdetto del 14/08 in KILL, e non esiste un posto da cui riusarlo → va ricordato a mano ogni volta |
| **E2** | **Contatore trial persistente** | `STRATEGY_LIFECYCLE §3` lo dichiara necessario perché il DSR funzioni. **Non esiste nel codice**: va ricostruito a mano dai file di pre-registrazione |
| **E3** | **Checklist dati/esecuzione come codice eseguibile** | monotonia temporale, barre/anno, duplicati, gap oltre lo stop, condizione di fill. Sono prosa; i tre errori di questa sessione sarebbero stati presi da tre assert |
| **E5** | **Primitiva unica `resolve_trade()` in `core/`** | la logica di fill/risoluzione e' reimplementata **quattro volte** (`backtest.py`, `closure.py`, `weekend.py`, `entry_fill_audit.py`) con **quattro convenzioni diverse** su gap-oltre-lo-stop e barra di fill. E' il meccanismo che ha prodotto l'ambiguita' +0,354 / +0,308 / +0,347 — e che ha tenuto in piedi per due mesi un edge inesistente. **Prerequisito di qualunque forward nuovo** |
| **E6** | **Ogni backtest deve dichiarare se il suo fill e' OTTENIBILE** | il fill fantasma non e' look-ahead di informazione (che cerchiamo gia') ma di **prezzo**: si transa a un livello disponibile solo *prima* di poter agire. Nessun controllo esistente lo intercettava. Va aggiunto alla checklist del guardiano e a `QUANT_REVIEW_PROTOCOL.md` |
| **E4** | **Contaminazione da knowledge cutoff dell'LLM** | rischio **nuovo**, non previsto dal protocollo, ora scritto nel guardiano (checklist 5). Evidenza esterna: *Profit Mirage* (arXiv 2510.07920) — spostando la finestra oltre il cutoff, **quasi tutti** gli agenti LLM pubblicati **non battono un baseline random** |

---

## Collegamenti

- [`STRATEGY_LIFECYCLE.md`](STRATEGY_LIFECYCLE.md) — gate, budget, verdetti
- [`QUANT_REVIEW_PROTOCOL.md`](QUANT_REVIEW_PROTOCOL.md) — gli 8 step della review
- [`../.claude/agents/quant-gatekeeper.md`](../.claude/agents/quant-gatekeeper.md) — il guardiano del protocollo
- [`../fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/SINTESI.md`](../fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/SINTESI.md) — da dove vengono B1-B6

---

## F — Il caso ORB: **CHIUSO 2026-08-27 in F1** (aperto 2026-08-23)

> ✅ **Esito.** L'utente ha **spento l'EA** il 2026-08-27 (verificato: zero posizioni, zero
> pendenti, ultimo ordine 25/08). Quanto segue resta come **motivazione registrata** della scelta e,
> soprattutto, come **condizioni di riapertura** — l'unica porta d'ingresso se un giorno si
> riproponesse.

**I fatti, verificati.**

| | |
|---|---|
| verdetto | **NO-GO** (2026-07-16): 14,5 anni Dukascopy M5, NAS100 **−0,056** [−0,11; 0,00] e SPX500 **−0,137** [−0,19; −0,08]. Entrambi i lati negativi, quasi tutti gli anni rossi |
| iterazioni v2 | filtro news, ADX: **stesso verdetto** |
| holdout | **gia' aperto** — e ha smascherato il "miglioramento" v2 come non-stazionario |
| forward | ⚠️ **esisteva** (EA `orb_nasdaq`, magic 26052, 22 ordini, 10 chiusi dal 31/07) — la mia affermazione del 23/08 era sbagliata: avevo cercato le prove nel repo invece che in **MT5**. **Spento dall'utente il 2026-08-27** |

**Come si e' creata la contraddizione.** La voce DECISIONS del 2026-08-14 concludeva: *"sposta il
prior e rafforza la scelta di lasciar correre il forward ORB, unico modo di risolverlo"*. Era una
**decisione**, non una descrizione — ma non e' mai stata implementata, e da allora e' stata citata
come se lo fosse (in questo backlog e nella discussione del 22-23/08). **L'errore e' mio**, ed e'
la ragione per cui il debito **E2** (contatore/stato persistente) non e' un dettaglio: non esiste
un posto dove lo stato reale di un binario sia registrato e verificabile.

**Cosa dice il 14/08 che spesso viene letto male.** Il test trend/playground ha trovato lo stesso
salto "pre/post-2020" **col segno opposto** su una strategia scorrelata. La conclusione fu che due
breakout della stessa famiglia che si spezzano in direzioni opposte alla stessa data sono piu'
coerenti con **due estrazioni di rumore** che con una rottura di microstruttura. ⚠️ **Quella e'
gia' una risposta alla domanda che il forward avrebbe dovuto risolvere**, ottenuta a costo zero.

**Le due ipotesi economiche arrivate dal funnel** (Cimbali, C4.6 · Siento, E.1) sono **aneddoti
senza campione**, quindi per `STRATEGY_LIFECYCLE §7` **non sono evidenza esterna nuova** e non
autorizzano a riaprire.

### La scelta, che e' dell'utente

| opzione | cosa comporta | costo |
|---|---|---|
| **F1 — lasciare chiuso** (raccomandata) | si registra che il forward non serviva: il 14/08 aveva gia' risposto. Le due ipotesi si archiviano come **condizioni di riapertura** gia' scritte, cosi' la prossima volta che qualcuno dice *"l'ORB funziona per via del gamma"* la risposta e' pronta | zero |
| **F2 — implementare il forward davvero** | rendere `today.py` persistente e farlo girare. ⚠️ E' un forward su una famiglia **NO-GO con holdout gia' bruciato**: raccoglie dati su qualcosa che abbiamo deciso non funziona, e la domanda che doveva risolvere ha gia' una risposta piu' economica | lavoro reale + un binario in piu' da presidiare |

### Se un giorno si riaprisse: le condizioni, scritte ORA

Le due ipotesi fanno **predizioni diverse**, ed e' questo che le rende utili — non la narrativa.
Vanno valutate su dati **mai visti**, non sul campione 2012-2026 gia' esaurito.

| | **Cimbali** — flusso strutturale d'acquisto + market maker che forniscono liquidita' | **Siento** — copertura gamma obbligata delle 0DTE |
|---|---|---|
| lato | **bias long** (il flusso strutturale e' di acquisto) | **simmetrico** (dipende dal posizionamento in opzioni) |
| epoca | effetto **stabile da ~20 anni**, quindi anche **pre-2020** | effetto **assente prima del 2021** (le 0DTE nascono li') |
| ora | nessuna preferenza dichiarata | **concentrato nelle prime ore** (opera solo le prime due) |
| calendario | nessuna dipendenza | **degrada dove non ci sono 0DTE**: triple witching (terzo venerdi' di mar/giu/set/dic), dove lui **non opera** |

⚠️ **Due avvertenze che vanno lette insieme alla tabella.**
1. Il nostro dato storico dice che l'ORB era **negativo pre-2020** — il che e' incompatibile con
   Cimbali e superficialmente compatibile con Siento. **Non conta come conferma**: e' un dato
   gia' visto, e il 14/08 ha mostrato che quello stesso split appare col segno opposto altrove.
2. Il meccanismo di Siento, preso alla lettera, **non predice che l'ORB funzioni**: predice che il
   prezzo venga attirato ai muri di gamma e li' **si inverta**. L'ORB e' una strategia di
   **continuazione**. Il suo meccanismo semmai spiegherebbe perche' l'ORB **fallisce** quando un
   muro sta davanti al target — cioe' e' piu' un argomento contro che a favore.
