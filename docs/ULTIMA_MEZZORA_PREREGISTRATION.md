---
tipo: preregistrazione
stato: CLOSED
approvata: "2026-10-12, Matteo, dopo la seconda passata G1 (passa con riserve, riserve chiuse)"
aggiornato: 2026-10-12
decisione: "Matteo: famiglia nuova (09/10); metrica primaria proporzionale con tetto, pre-registrazione subito nel terzo slot esterno del 2026-Q4, guardia a taglia fissa al 5% a una coda (strada B) (11/10); testo approvato il 12/10 dopo la seconda passata G1. DECISIONS 2026-10-09, 2026-10-11 e 2026-10-12"
metrica_corrente: "CLOSED al train (12/10): divario dal casuale -0,51 pb [-2,01; +0,99], MDE 2,15; limite alto sotto la meta' dell'effetto atteso (2,28 pb). Holdout DAX mai aperto (esito docs/reviews/esiti/ultima_mezzora_train.txt)"
nota: "Due stadi, una esecuzione ciascuno: train (SPX500 + NAS100) e, solo se PASSA, holdout (DAX). Massimo esito LEAD con gate finale forward. Script: analysis/ultima_mezzora/esegui_test.py"
---

# Pre-registrazione — Momentum dell'ultima mezz'ora (famiglia `momentum_ultima_mezzora`, backlog H1)

Referto dei passi a 0 trial (costi, dati, potenza): [ULTIMA_MEZZORA_FATTIBILITA.md](ULTIMA_MEZZORA_FATTIBILITA.md).
Fonte: Baltussen, Da, Lammers, Martens, *Journal of Financial Economics* 142 (2021) 377-403, letta sul testo
([10_indicatori_tecnici](../fondamenti_tecnici/10_indicatori_tecnici/principles.md), livello T). Famiglia nel contatore:
`momentum_ultima_mezzora`.

## 1. Ipotesi e razionale

**Ipotesi.** Sugli indici azionari, il rendimento dalla chiusura del giorno prima a 30 minuti dalla chiusura (r_ROD)
predice con segno positivo il rendimento dell'ultima mezz'ora (r_LH). Una posizione **proporzionale a r_ROD, con un
tetto**, tenuta solo nell'ultima mezz'ora, rende al netto dei costi CFD **piu' della stessa posizione con la direzione
presa da un altro giorno**.

**Cosa la falsifica.** Un intervallo del divario (reale − casuale) il cui limite alto sta sotto **meta' dell'effetto
atteso dalla fonte** (§6): escluso un effetto pari a meta' di quello pubblicato.

**Razionale (classe, chi paga).** Classe 2 di [09_fonti_di_vantaggio](../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md):
flusso forzato. Chi e' corto di gamma (market maker che hanno venduto opzioni, ETF a leva che ribilanciano a fine
giornata) deve comprare quando il mercato sale e vendere quando scende, in quantita' proporzionale al movimento, a
ridosso della chiusura. Accetta perche' e' un vincolo (copertura, mandato), non un errore. Limite all'arbitraggio:
capacita' piccola, costi di una strategia giornaliera, inversione nei giorni successivi.

**Parentela con `opening_range`** (condizione 1 di DECISIONS 2026-10-09). Il segnale usa il rendimento intraday gia'
fatto, come l'ORB (CLOSED, holdout aperto). E' una famiglia nuova perche' cambia il meccanismo (coperture a fine
giornata contro asta d'apertura) e la finestra (ultima mezz'ora contro prima ora). Conseguenza sui dati: quelli gia'
attraversati dall'ORB **non fanno da holdout** (§3).

**Provenienza.** L'ipotesi e' della fonte, umana, esterna, datata (2021), trovata nella ricerca dell'08/10. **Sono
proposte dell'assistente**, non della fonte: la metrica proporzionale come primaria (il paper la misura come
regressione e riporta la strategia di solo segno), la finestra di scala di 60 sedute e il tetto 2. Sono fissate qui e
non tarate, ma nascono da un modello con knowledge cutoff al 2026-05-31, su un tema molto discusso e su dati in gran
parte precedenti al cutoff: e' una delle ragioni del tetto LEAD con forward (§8). Consuma il **terzo slot** di
pre-registrazione esterna del 2026-Q4, che con questa e' pieno.

## 2. Regola (esatta, uguale per tutti gli strumenti)

Per ogni seduta del calendario di borsa (`exchange_calendars`: XNYS per gli indici USA, XETR per il DAX), con
chiusura C (16:00 a New York, 17:30 a Francoforte; nelle chiusure anticipate la finestra si sposta con C):

- **r_ROD** = ln(chiusura della barra M5 che finisce a C−30' / chiusura dell'ultima barra della seduta precedente).
- **sigma** = deviazione standard di r_ROD sulle 60 sedute valide precedenti (nota prima dell'entrata).
- **Posizione primaria (proporzionale con tetto):** w = r_ROD / sigma, limitata a [−2, +2].
- **Posizione a taglia fissa (binario 1R):** s = segno(r_ROD).
- **Entrata** all'apertura della barra che inizia a C−30'. **Uscita** alla chiusura dell'ultima barra prima di C.
- **r_LH** = ln(uscita / entrata). Rendimento netto = posizione × r_LH − costo × |posizione| (§4).
- Portafoglio = media 1/N degli strumenti primari disponibili quel giorno.

**Fill.** Il segnale usa la chiusura della barra che finisce a C−30', nota a C−30'; l'entrata e' il primo prezzo
successivo (apertura della barra dopo). L'uscita e' un ordine a mercato alla chiusura, e il CFD resta aperto dopo C.
Non c'e' nessun livello: fill non ottenibili 0 per costruzione; lo script lo stampa, insieme allo scarto fra la
chiusura della barra del segnale e l'apertura dell'entrata. Lo slittamento non e' modellato: lo coprono in parte il
margine sui costi e lo stress 3x, e si misura solo in forward.

**Parametri.** 60 sedute e tetto 2: fissati qui, nessuna variante. Sedute senza una delle quattro barre: escluse e contate.

## 3. Dati e divisione

| pezzo | strumenti | periodo | sedute | stato |
|---|---|---|---|---|
| **TRAIN** | SPX500 + NAS100, Dukascopy M5, UTC | 2020-06-01 → 2026-07-16 | ~1.538 | fuori dal campione della fonte; gia' attraversati dall'ORB e dal conteggio di potenza (deviazione di r_LH, correlazione fra i due) |
| **HOLDOUT sigillato** | **DAX**, Dukascopy M5, UTC | 2020-06-01 → 2026-10-09 | 1.622 | l'M5 non e' mai stato usato: solo controlli meccanici (11/10). Si apre **una volta**, solo se il train PASSA |
| repliche descrittive | Euro Stoxx 50, FTSE 100 | come il DAX | 1.622 e 1.608 | si aprono col DAX; **non entrano nel verdetto** |
| **FORWARD** | CFD su demo FP Markets | dopo un eventuale LEAD | — | gate finale, nuova pre-registrazione |

- SPX500 e NAS100 valgono **un solo strumento** (r_LH correlati a 0,96): l'intervallo si calcola sul portafoglio.
- **Perche' il DAX come primario dell'holdout.** Dei tre indici europei scaricati e' il piu' economico su FP Markets
  (0,20 pb misurati; FTSE 0,96; Euro Stoxx 2,58, cioe' quasi tutto il lordo stimato). Scelta fatta sui costi, prima
  di calcolare qualunque rendimento. I tre sono attesi molto correlati: contano come uno.
- "Mai usato" vale per l'M5. Il DAX **giornaliero** e' passato dall'inventario di volatilita' di
  `analysis/trend/heldout_pool.py` (0 trial, nessuna regola).
- Il campione della fonte finisce a maggio 2020: tutto il test e' fuori campione rispetto al paper.
- **Controlli, prima di ogni numero che dipende dal segnale.** `core.data_checks.checklist_dati` completa (monotonia,
  duplicati, file piu' completo; le barre per anno sono solo riportate, senza soglia) sul file grezzo; impronta SHA-256 dei file; sul train la
  **riproduzione dei numeri gia' noti** dal referto del 09/10 (deviazione di r_LH 26,4 e 30,7 pb, 1.538 sedute, con
  tolleranza 0,1 pb e 2 sedute). Se un controllo e' ROTTO, i numeri noti non tornano o piu' del 5% delle sedute dei
  primari e' escluso, lo script esce prima (NESSUN VERDETTO).
- La lettura delle barre (`sedute_da_barre`: fuso, calendario, chiusure anticipate, barre mancanti) e' coperta da
  `tests/test_ultima_mezzora.py` su barre finte con prezzi noti.
- **Differenze dalla fonte, dichiarate:** CFD Dukascopy lato bid, non futures; il fuso e' UTC (nessun dato MT5 nel test,
  quindi il problema dello scarto del server non c'e').

## 4. Costi

Spread misurati dai tick MT5 sul demo FP Markets nella finestra di ogni indice, 02-10/2026
([referto](ULTIMA_MEZZORA_FATTIBILITA.md)). Costo andata e ritorno per unita' di posizione, in punti base:

| strumento | misurato: mediana (p90) | usato nel test |
|---|---|---|
| SPX500 (US500) | 0,34 (0,38) | **0,5** |
| NAS100 (US100) | 0,21 (0,25) | **0,5** |
| DAX (GER40) | 0,20 (0,21) | **0,5** |
| FTSE 100 (UK100) | 0,96 (1,07) | 1,5 |
| Euro Stoxx 50 (EURO50) | 2,58 (2,96) | 3,0 |

Valori arrotondati in su, con margine per slittamento e conto demo. **Stress: costi 3x.** Nessuno swap (posizione
chiusa in giornata). Commissioni non misurate: dichiarato. ⚠️ Gli spread sono del 2026 e si applicano a tutto il
2020-2026: se negli anni precedenti erano piu' larghi, il costo e' **sottostimato** (direzione ottimista, §8).

## 5. Baseline

**Stessa taglia ogni giorno, direzione presa da un altro giorno.** I segni di r_ROD si spostano in blocco di un numero
casuale di sedute (spostamento circolare, almeno 20 sedute, 1.000 spostamenti, seme 42, lo stesso spostamento per tutti
gli strumenti); la taglia |w| di ogni giorno resta al suo posto. Il confronto conserva: la taglia giorno per giorno
(identica nei due bracci), la quota di giorni lunghi e corti, la struttura seriale dei segni, il legame fra taglia e
volatilita' dell'ultima mezz'ora dello stesso giorno, la dipendenza fra strumenti. I due bracci pagano gli stessi
costi.

- **Cosa non conserva, e come si rimedia.** Lo spostamento rompe anche il legame fra taglia e segno dello stesso giorno
  (per esempio giorni di ribasso piu' grandi di quelli di rialzo), quindi i due bracci possono avere un'esposizione
  netta media diversa: con una deriva dell'ultima mezz'ora nascerebbe un divario senza alcun legame di direzione
  (misurato dal gatekeeper: fino a +0,30 pb). Per questo **il divario si calcola su r_LH centrato** (meno la media
  del campione, per strumento): la deriva esce dal confronto per costruzione. Lo script stampa comunque l'esposizione
  netta dei due bracci e la media di r_LH. L'attesa netta, invece, usa r_LH non centrato: e' quello che si incassa.
- Copre il benchmark della fonte ("sempre lungo nell'ultima mezz'ora"): l'esposizione media non conta nel divario.
- Non si usa `core.random_baseline.BarSampler` perche' li' e' casuale l'**istante** d'ingresso; qui l'istante e' fisso
  per costruzione (l'ultima mezz'ora di ogni seduta) e l'unica cosa che si puo' rendere casuale e' la direzione.

## 6. Metriche, soglie e verdetto (scritti prima)

Unita': punti base per seduta, sul portafoglio dei primari. Intervalli: bootstrap stazionario a blocchi sui giorni
(lunghezza media 10 sedute), percentile al 95%, 5.000 repliche, seme 42. MDE = 2,80 × errore standard del bootstrap.

**Primaria:** il **divario** fra la posizione proporzionale con tetto e il braccio casuale.

**Effetto atteso dalla fonte** (corretto dopo la prima passata G1): rho × media nel tempo di |w| × |r_ROD/sigma| ×
deviazione mobile a 60 sedute dell'ultima mezz'ora, per strumento e poi 1/N. rho e' la correlazione pubblicata fra
r_ROD e r_LH (radice dell'R² **fuori campione** della Tab. B1: 0,151 per ES e 0,194 per NQ, riferimento del train
**0,1725**; 0,158 per la media europea, riferimento dell'holdout). Tutti i fattori sono noti prima dell'esito. La
versione precedente usava la deviazione a campione intero, che con volatilita' a grappoli sovrastima l'effetto e
rendeva il CLOSED troppo facile.

| esito | condizione | conseguenza |
|---|---|---|
| **NESSUN VERDETTO** (prima di tutto) | controlli dati ROTTI, numeri noti non riprodotti, o piu' del 5% di sedute escluse | si corregge come esecuzione (0 trial) e si rilancia una volta, con `--ripresa` |
| **PASSA** (train) / **LEAD** (holdout): ha la precedenza sugli altri | limite basso del divario > **B_NULL** **e** limite basso dell'attesa netta > 0 **e** attesa netta con costi 3x > 0 **e** divario puntuale > 0 su **ogni** strumento primario **e** **guardia a taglia fissa**: divario a taglia fissa > 1,645 errori standard | train: si apre l'holdout. Holdout: gate finale forward, nuova pre-registrazione |
| **CLOSED** | limite alto del divario < **meta' dell'effetto atteso** | escluso un effetto pari a meta' di quello pubblicato; famiglia chiusa |
| **NON DIMOSTRATO** | il resto | si scrive con l'MDE accanto; famiglia chiusa per potenza, non refutata |

- **Due stadi.** L'holdout si apre **solo** se il train PASSA. Se il train non passa la famiglia si chiude e l'holdout
  resta sigillato (servirebbe una riapertura §7).
- **La guardia a taglia fissa: eccezione dichiarata a STRATEGY_LIFECYCLE §4quater** (Matteo, 11/10, strada B;
  DECISIONS 2026-10-11). La regola del 06/10 da' il verdetto sul vantaggio solo a taglia fissa e tratta la taglia "per
  convinzione" come un pezzo del segnale. Qui, **solo per questa famiglia**, decide la proporzionale, perche' il
  meccanismo dice che la spinta cresce col movimento. In cambio la taglia fissa deve reggere **da sola**: il suo
  divario dal casuale deve essere positivo al 5% a una coda (sopra 1,645 errori standard). Un eventuale LEAD e'
  quindi "proporzionale, con la taglia fissa significativa a una coda", e l'intervallo e l'MDE della taglia fissa si
  riportano accanto. La prima bozza chiedeva solo un valore puntuale positivo: non proteggeva (§9).
- **Ablazione della taglia** (§4bis): differenza appaiata fra proporzionale e solo segno a pari taglia media, col
  suo intervallo a blocchi. Dice quanto aggiunge la taglia; non decide.
- **Tabella di esclusione** (sempre stampata). Per ogni correlazione pubblicata (in campione e fuori campione), piena
  e dimezzata: ESCLUSO se il limite alto del divario sta sotto l'effetto atteso con quella correlazione; "superato"
  se il limite basso sta sopra; altrimenti "non escluso". Un "superato" non si cita come conferma della fonte.
- Il p-value dagli spostamenti circolari si riporta col suo intervallo (`core.verifiche.pvalue_mc`), non decide.

**B_NULL = 0,2 pb**; falsi positivi, potenza ed errore del CLOSED misurati sul sintetico col codice del test: §9.

## 7. Descrittivi (non decidono) e doppio binario

Per strumento; divario e netto per anno, con il conteggio degli anni positivi; limite basso del divario ripetuto su 10
semi (`core.verifiche.ripeti_su_semi`); Sharpe per seduta con PSR (1 trial: DSR = PSR) e pavimento di futilita'
1,65/√n; proporzionale senza tetto; ablazione della taglia; **due controlli del meccanismo**: solo segno per terzile
di |r_ROD/sigma| (l'effetto deve crescere con il movimento) e posizione di oggi × r_ROD di domani (le coperture si
invertono: atteso negativo). Se i due controlli vanno contro il meccanismo lo si scrive accanto al verdetto, che non
cambia.

**Doppio binario** (§4quater). Binario 1R = solo segno a taglia fissa: entra nel verdetto come guardia (§6). Overlay O1
e O3 con `confronta_overlay` sulla sequenza a taglia fissa (una operazione al giorno, senza sovrapposizioni), in unita'
della deviazione mobile dell'ultima mezz'ora, con banda e runs test. Binario prop omesso: senza stop il rischio per
operazione non e' definito, e una versione con stop sarebbe un'altra regola.

## 8. Contabilita' e kill

- **1 trial**, budget 1, nessun round di rifinitura. La specifica e' una; il train e l'holdout sono due stadi dello
  stesso trial. **Holdout: una apertura.** Qualunque modifica dopo l'esito e' una pre-registrazione nuova.
- **Una sola esecuzione per stadio, e lo fa rispettare lo script.** Prima di ogni stadio: (1) il contatore registra lo
  stadio (train: `trial_cumulati = 1`; holdout: `holdout_aperto` con la data); (2) pre-registrazione, codice e
  contatore sono **committati**; (3) si esegue. Lo script rifiuta di partire se la pre-registrazione non e'
  APPROVATA, se quei file hanno modifiche non committate, se il contatore non ha registrato lo stadio, o se l'esito
  dello stadio esiste gia'. L'holdout chiede anche l'esito del train committato con PASSA. L'esito riporta l'hash del
  commit e l'impronta dei file dati, e va committato subito.
- **Kill:** CLOSED o NON DIMOSTRATO, a uno qualunque dei due stadi, chiudono la famiglia.
- **Massimo esito LEAD**, mai GO, per quattro motivi: l'ipotesi viene da una fonte pubblicata (decadimento dopo la
  pubblicazione); CFD e non futures; costi da conto demo senza slittamento; scelte dell'assistente su dati in gran
  parte precedenti al cutoff (§1). Il GO passa da un forward su demo con la sua pre-registrazione.
- **I due stadi non sono due prove indipendenti di tutto.** Sotto il nullo il rumore dei due stadi e' indipendente,
  ma un difetto comune (stesso fornitore di dati, stessa costruzione del confronto, stessa lettura delle barre)
  colpirebbe entrambi nello stesso verso.
- **Assunzioni e direzione dell'errore.** Costi arrotondati in su (pessimista); spread del 2026 applicati al
  2020-2026 (**ottimista**); slittamento non modellato (ottimista, coperto in parte dallo stress 3x); lato bid per
  entrata e uscita (neutro sul rendimento, lo spread e' nei costi); calendario di borsa per le chiusure anticipate
  (se sbaglia un giorno, la finestra di quel giorno e' fuori posto: rumore, non distorsione); SPX e NAS trattati come
  portafoglio (l'intervallo non conta due volte lo stesso giorno).
- **Procedura di ripresa:** se l'esecuzione si interrompe dopo aver letto i dati, o esce NESSUN VERDETTO, il difetto si
  corregge come esecuzione (0 trial), si scrive una voce in DECISIONS e si rilancia **una** volta con `--ripresa
  "motivo"`, che finisce nell'esito.

## 9. Calibrazione sul sintetico (11/10, prima del mercato) e revisione G1

Codice del test ([`esegui_test.py`](../analysis/ultima_mezzora/esegui_test.py)) su sedute seminate
([`calibra_nullo.py`](../analysis/ultima_mezzora/calibra_nullo.py)): volatilita' a grappoli comune, code grasse (t a 5
gradi), due strumenti correlati a 0,96, 1.540 sedute come il train, **300 serie per scenario**, con B_NULL = 0,2 e la
guardia a 1,645 errori standard. Per velocita' la calibrazione usa 1.000 repliche di bootstrap e 300 spostamenti (il
test vero 5.000 e 1.000). I quattro nulli "cattivi" sono quelli costruiti dal gatekeeper nella prima passata.

| scenario | divario medio | limite basso > B_NULL | guardia da sola | PASSA | CLOSED | NON DIMOSTRATO |
|---|---|---|---|---|---|---|
| nullo | +0,053 pb [−0,067; +0,173] | 2,3% | 6,0% | **1,7%** | 64,3% | 34,0% |
| meta' effetto (correlazione 0,086) | +2,27 pb (atteso 2,36) | 53,0% | 70,3% | **47,0%** | 2,7% | 50,3% |
| effetto pieno (correlazione 0,172) | +4,49 pb (atteso 4,70) | 98,0% | 99,3% | **97,3%** | 0% | 2,7% |
| effetto solo nella taglia | +4,57 pb | 98,0% | 5,0% | **5,0%** | 0% | 95,0% |
| asimmetria e deriva negativa dell'ultima mezz'ora | +0,044 pb [−0,076; +0,163] | 2,3% | 6,0% | **1,7%** | 65,0% | 33,3% |
| volatilita' dell'ultima mezz'ora legata al movimento | +0,044 pb [−0,151; +0,240] | 3,0% | 7,3% | **1,3%** | 37,7% | 61,0% |
| segni autocorrelati | +0,059 pb [−0,067; +0,184] | 3,0% | 4,7% | **2,3%** | 62,7% | 35,0% |

- **B_NULL = 0,2 pb.** Sotto il nullo il divario non ha una distorsione rilevabile (+0,053 [−0,067; +0,173]); scelta
  prudente: il limite alto dell'intervallo, arrotondato in su.
- **Falsi positivi:** PASSA a torto fra l'1,3% e il 2,3% in tutti e cinque i nulli.
- **La guardia fa il suo lavoro:** un effetto che vive solo nella taglia passa nel 5,0% delle serie (con la guardia
  sul valore puntuale della prima bozza passava nel 52,8%). Costa al piu' 6 punti di potenza a meta' effetto (53,0% →
  47,0%) e quasi niente a effetto pieno.
- **Il centramento fa il suo lavoro:** con asimmetria e deriva il divario era +0,30 pb senza alcun legame di
  direzione; ora e' +0,044, come il nullo.
- **La formula dell'effetto atteso regge:** realizzato/atteso 0,96 a meta' effetto e 0,96 a effetto pieno; a meta'
  effetto il CLOSED scatta nel **2,7%** delle serie, in linea col 2,5% nominale (prima: 9,3%).
- **Potenza, con il suo limite.** Su questo sintetico: a effetto pieno il train passa nel 97% dei casi, a **meta'
  effetto una volta su due**, e arrivare al LEAD passando due stadi a meta' effetto e' circa una volta su quattro o
  cinque. **Non e' una previsione**: l'MDE (qui 2,8 pb) dipende da come e' fatta la volatilita' vera, e sul sintetico
  varia da 1,8 pb senza grappoli a 4,6 pb se la volatilita' dell'ultima mezz'ora cresce col movimento del giorno. Un
  NON DIMOSTRATO non smentisce un effetto dimezzato: lo dice l'MDE misurato sul reale, non l'etichetta.
- **Limiti del sintetico, dichiarati:** l'effetto iniettato e' lineare e uguale ogni giorno; sui dati veri puo' essere
  concentrato in pochi giorni o cambiare segno dopo il 2021 (opzioni a scadenza giornaliera). Le code del sintetico
  sono piu' pesanti di quelle misurate sul train (curtosi in eccesso mediana 17 contro 4,5 e 4,3).
- **Guardie e lettura delle barre:** con la pre-registrazione in BOZZA lo script rifiuta i dati reali (codice 2);
  `tests/test_ultima_mezzora.py` passa (7 casi: seduta normale, chiusura anticipata, settimana del cambio d'ora,
  barre mancanti, scala nota prima).

### Revisione G1 del gatekeeper

**Prima passata (11/10): BLOCCA**, due bloccanti e nove riserve; nessun difetto che promuovesse il rumore (PASSA a
torto 1,3-2,0% sui nulli provati), nessun dato reale letto.
1. *Soglia di CLOSED in unita' sbagliate* (deviazione a campione intero invece della volatilita' media incassata):
   **corretto** con la formula del §6; errore del CLOSED a meta' effetto da 9,3% a 2,7%.
2. *Guardia a taglia fissa inefficace* (valore puntuale: non scattava mai sotto i nulli e lasciava passare il 52,8% di
   un effetto solo nella taglia): **corretto** con la strada B scelta da Matteo, guardia al 5% a una coda (5,0%).
   Il gatekeeper ha anche misurato che sul sintetico la taglia fissa ha la stessa potenza della proporzionale: la
   scelta della proporzionale poggia sul meccanismo, non su una potenza dimostrata.

Riserve accolte: divario su r_LH centrato ed esposizioni stampate (1); p-value col suo intervallo, ripetizione su 10
semi, riga sui fill, divario per anno, banda e runs test dell'overlay, `checklist_dati` completa (2); test sulla
lettura delle barre e riproduzione dei numeri noti prima del segnale (3); blocco della seconda esecuzione, contatore e
commit prima di ogni stadio, hash e impronta dei dati nell'esito (4); §9 riallineato (5); limite dei "due falsi
positivi indipendenti" (6); direzione dell'errore sui costi (7); provenienza delle scelte dell'assistente (8);
precedenza di PASSA su CLOSED e precisazione sul DAX giornaliero (9).

**Seconda passata (12/10): PASSA CON RISERVE, 0 bloccanti.** Solo sintetico, nessun dato reale letto. Il gatekeeper
ha rimisurato sul codice corretto: CLOSED a meta' effetto 2,7% (era 10,5%), realizzato/atteso 0,965, effetto solo
nella taglia PASSA 3,5% su 200 serie (era 52,8%), divario con asimmetria e deriva −0,018 [−0,153; +0,117] (era +0,30).
Ha fatto girare il percorso dei dati reali su sedute finte fino alla scrittura dell'esito, e provato i rami delle
guardie. Testo e codice coincidono su regola, baseline, effetto atteso, verdetti, precedenza e guardia.

Cinque riserve, chiuse il 12/10 prima dell'approvazione:
1. *Se git non rispondeva, il train partiva* (stato vuoto letto come "pulito"): **corretto**, lo script rifiuta se git
   da' errore o non restituisce l'hash.
2. *Dopo un NESSUN VERDETTO o un'interruzione il rilancio non chiedeva `--ripresa`*: **corretto**. Lo script scrive
   un segnaposto dell'esito prima di leggere i dati; da li' ogni altro lancio chiede il motivo, la ripresa e' una
   sola, e un esito che ha gia' un verdetto non si riesegue in nessun caso.
3. *"La guardia costa circa 6 punti"*: **corretto** in "al piu' 6 punti" (lo scarto contiene anche le altre condizioni).
4. *Il controllo "barre per anno" non puo' fermare lo script* (senza un intervallo atteso e' solo riportato):
   **testo allineato** al §3.
5. Minori: l'holdout ora verifica che `analysis/ultima_mezzora` non sia cambiato dal commit del train (**corretto**);
   l'etichetta "verdetto sul vantaggio" sulla riga 1R dell'overlay e' sostituita (**corretto**); i test coprono il
   calendario di New York e non `carica` ne' il calendario di Francoforte dell'holdout (**dichiarato**: li' la
   protezione sono i controlli meccanici dell'11/10 e la lettura diretta del codice).

Rami delle guardie riprovati dopo le correzioni (percorsi temporanei, git finto): contatore senza trial speso, tutto a
posto, segnaposto con e senza `--ripresa`, seconda ripresa, verdetto esistente, git in errore, hash vuoto: 8 su 8.

**Approvata da Matteo il 12/10/2026** sul testo uscito dalla seconda passata G1 ("procedi con l'ordine proposto":
stato ad APPROVATA, trial segnato come speso nel contatore, commit, esecuzione del train una volta). Da questo
commit testo, codice e contatore sono congelati: l'esito di ogni stadio sta in `docs/reviews/esiti/`.

## 10. Esito (12/10/2026)

Train eseguito **una volta** sul commit `2b66e65`, dopo l'approvazione: **CLOSED**. Il limite alto del divario dal
casuale sta sotto la meta' dell'effetto atteso dalla fonte (§6), quindi la famiglia e' chiusa e **l'holdout sul DAX non
e' stato aperto**. Numeri e descrittivi: [esito](reviews/esiti/ultima_mezzora_train.txt). Lettura, limiti e condizioni
di riapertura: DECISIONS 2026-10-12 (2). Revisione G2 del gatekeeper (12/10): **PASSA CON RISERVE**, 0 bloccanti sul
verdetto, lettura corretta: [referto](reviews/ultima_mezzora_G2_2026-10-12.md).
