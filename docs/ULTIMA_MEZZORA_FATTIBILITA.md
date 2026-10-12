---
tipo: referto
stato: chiuso
aggiornato: 2026-10-12
strada: "BACKLOG_RICERCA §H, H1 (momentum dell'ultima mezz'ora)"
nota: "Passi a 0 trial prima della G1. Fatti il 09/10: famiglia (1, nuova), costi (2, sotto la soglia), dati (3, reggono con quattro condizioni), potenza (4: USA solo a effetto pieno, oro no, serve un indice europeo). Restano slot (5), download europei e metrica primaria."
---
# H1, momentum dell'ultima mezz'ora: fattibilita' prima della pre-registrazione

> I passi che si fanno **senza guardare nessun rendimento**, per sapere se H1 merita una pre-registrazione.
> La scheda della strada (fonte, meccanismo, domande aperte) e' nel [backlog, sezione H](BACKLOG_RICERCA.md); qui
> stanno i numeri misurati. Script: [`analysis/ultima_mezzora/spread_mt5.py`](../analysis/ultima_mezzora/spread_mt5.py).

## Passo 2 — Costi (accessibilita'): SOTTO la soglia

**Domanda.** Lo spread dei CFD del nostro broker, entrando alle 15:30 e uscendo alle 16:00 di New York, si mangia il
guadagno lordo pubblicato?

**Soglia dichiarata prima della misura** (backlog H1, 08/10): H1 chiude se il costo per operazione e' almeno **meta'**
del lordo stimato. Lordo stimato: **~2,7 punti base** per operazione (Baltussen et al. 2021, Tab. 6, futures azionari:
6,86% annuo / ~252 giorni; stima a spanne). Soglia: **1,35 pb**.

**Come.** Dai tick di MT5 (denaro e lettera), conto demo **FP Markets**, per ogni giorno feriale: ultima quotazione prima
delle 15:30:00 e prima delle 16:00:00 ET (scartata se piu' vecchia di 60 secondi). Costo andata e ritorno = meta' spread
in entrata + meta' spread in uscita, in punti base del prezzo medio. Nessun rendimento calcolato.

**Esito** (misurato il 2026-10-09, 159 giorni validi dal 2026-02-23 al 2026-10-08):

| | US500 | US100 |
|---|---|---|
| spread alle 15:30 ET, mediana (p90) | 0,25 (0,25) punti | 0,60 (0,60) punti |
| spread alle 16:00 ET, mediana (p90) | 0,25 (0,25) punti | 0,60 (0,60) punti |
| costo per operazione, mediana (p90; max) | **0,34 pb** (0,38; 1,19) | **0,21 pb** (0,25; 0,37) |
| quota del lordo stimato | **12%** | **8%** |
| giorni sopra la soglia | 0% | 0% |

Il passo 2 **non chiude H1**: c'e' un margine di circa 4 volte prima della soglia su US500 e di circa 6 su US100. Il
profilo dalle 15:00 alle 16:30 ET e' **piatto** (spread mediano identico in ogni intervallo di 5 minuti); l'unico giorno
caro e' il 26/06/2026 (1,5 punti alle 16:00 su US500).

**Cosa questo numero NON dice.**
- E' un **conto demo**: lo spread costante (0,25 e 0,60 per tutta la sessione USA) fa pensare a uno spread fisso del
  demo. Va confermato sul conto con cui si opererebbe, compreso il **tipo di conto** e l'eventuale **commissione** (non
  misurata).
- Lo spread non e' tutto il costo: lo **slittamento** di un ordine a mercato alle 15:30 e alle 16:00 non e' misurato.
  Si misura solo eseguendo (demo), e il FADE insegna che l'esecuzione e' dove si nascondono i numeri ([[feedback_fill_ottenibile]]).
- Il lordo di 2,7 pb e' la media 1974-2020 di un portafoglio di futures azionari. Se dopo il 2020 l'effetto si e'
  ridotto, il margine si stringe: e' la domanda della potenza (passo 4).

## Scoperta collaterale: il server FP Markets segue New York + 7 ore (di regola), non l'ora di Bucarest

> ⚠️ **Precisato dal passo 3 lo stesso giorno**: "di regola", non "sempre". Dal 10 al 13 marzo 2025 il server era a +6
> (sezione Passo 3, condizione 1). La conclusione operativa diventa piu' forte: lo scarto si verifica giorno per giorno.

Lo script prova due convenzioni orarie e per ogni giorno tiene quella in cui non ci sono tick durante la pausa dei futures
USA (17:15-17:45 ET). Risultato: **144 giorni** tornano con "Europe/Bucharest", ma **15** solo con "New York + 7 ore", e
sono esattamente i giorni **dal 9 al 27 marzo 2026**, quando gli Stati Uniti erano gia' all'ora legale e l'Europa no. I 5
giorni senza misura sono festivita' USA (3/4, 25/5, 19/6, 3/7, 7/9).

Quindi nel 2026 il server seguiva New York + 7 ore, e la convenzione "Europe/Bucharest" usata per i file MT5 di US100 e
US500 in [`analysis/opening_range/backtest.py`](../analysis/opening_range/backtest.py) (riga 64) **sbaglia di un'ora circa
quattro settimane all'anno** (tre a marzo, una fra fine ottobre e inizio novembre).

- **Impatto sui verdetti: nessuno noto.** Il NO-GO dell'ORB poggia sui dati Dukascopy, che sono in UTC (DECISIONS
  2026-07-16); i file MT5 erano il primo giro esplorativo sul broker. Il codice di una famiglia chiusa non e' stato toccato.
- **Impatto su H1: diretto.** Ogni test sui dati MT5 FP Markets deve ricavare lo scarto **giorno per giorno** dalla pausa,
  in **un solo punto** del loader ([[feedback_una_correzione_un_proprietario]]).

## Passo 1 — Famiglia: NUOVA (decisione di Matteo, 09/10)

`momentum_ultima_mezzora`, con due condizioni: la pre-registrazione dichiara la parentela con `opening_range`, e i dati
gia' attraversati dall'ORB non fanno da holdout. Motivazione e condizioni: DECISIONS 2026-10-09.

## Passo 3 — Dati: reggono, con quattro condizioni per la G1

**Come.** Script [`analysis/ultima_mezzora/verifica_dati.py`](../analysis/ultima_mezzora/verifica_dati.py), lanciato il
2026-10-09. Per ogni file intraday in casa: controlli meccanici di `core/data_checks.py`, coerenza dei prezzi, fuso orario
(barre nella pausa dei futures USA, 17:15-17:45 ET) e copertura della finestra **seduta per seduta** dal calendario di
borsa (`exchange_calendars`: XNYS per gli indici, COMEX per l'oro). La finestra segue la Tab. 1 del paper: indici USA
15:30-16:00 ET (12:30-13:00 nelle chiusure anticipate), oro 13:00-13:30 ET (chiusura COMEX). **Nessun rendimento
calcolato.**

| feed | fonte, fuso | periodo | sedute complete da 06/2020 | attraversato dall'ORB | note |
|---|---|---|---|---|---|
| SPX500 M5 | Dukascopy, UTC | 2012-01 → 2026-07-16 | **99,9%** di 1.539 | si' | barre nella pausa solo 2012-2015 (comportamento del feed); dal 2021 pausa pulita 16:15-18:00 ET |
| NAS100 M5 | Dukascopy, UTC | 2012-01 → 2026-07-16 | **99,9%** di 1.539 | si' | 34 barre incoerenti, tutte nel 2013 (12 nella finestra): fuori dal periodo pulito |
| US500 M5 | MT5 FP Markets | 2025-02 → 2026-07-16 | 97,2% di 355 | si' (primo giro) | buco nelle finestre dal 06/07 al 16/07/2026 (export); storia corta |
| US100 M5 | MT5 FP Markets | 2025-02 → 2026-07-16 | 99,7% di 354 | si' (primo giro) | storia corta |
| XAUUSD M1 | Dukascopy, UTC | 2020-09 → 2026-10-02 | 98,0% di 1.571 | **no** | pausa pulita (0 barre); le sedute "incomplete" sono festivita' USA e il giorno dopo |

Controlli meccanici (monotonia, duplicati, prezzi non positivi) **a posto su tutti e cinque**. Barre ferme nella finestra:
0,00% da 06/2020 sugli indici, 0,03% sull'oro.

**Le quattro condizioni per la G1:**
1. **Fuso MT5 verificato giorno per giorno.** Il server FP Markets non ha uno scarto fisso: New York + 7 ore, ma **+6 dal
   10 al 13 marzo 2025** (il buco della pausa cade alle 17:55-19:00 ET invece che alle 16:55-18:00), poi +7 da venerdi'
   14. Nel 2026 era +7 gia' dal 9 marzo. Una regola fissa, qualunque sia, sbaglia qualche giorno: il loader deve
   ricavare lo scarto dalla pausa di ogni giorno e scartare i giorni che non tornano. Dukascopy e' UTC e non ha il
   problema.
2. **Calendario esplicito.** 32 chiusure anticipate fra il 2012 e il 2026 (la finestra diventa 12:30-13:00 ET; complete
   al 91-94%) e festivita' escluse; "chiusura di ieri" = ultima seduta valida, non il giorno di calendario precedente.
   Per l'oro le festivita' USA vanno escluse anche se il calendario COMEX le conta come sedute.
3. **Divisione dei dati coerente con DECISIONS 2026-10-09.** In casa c'e' un solo strumento sia fuori dal campione della
   fonte sia mai usato dall'ORB: **l'oro M1 dal 2020**. SPX500 e NAS100 da 06/2020 sono fuori dal campione della fonte ma
   gia' attraversati dall'ORB: campione di sviluppo, non holdout. Un holdout multi-strumento richiede di **scaricare**
   (Dukascopy, gratis) altri futures della Tab. 1 mai usati dall'ORB, per esempio DAX, FTSE 100, Euro Stoxx 50, Bund,
   T-note, petrolio, valute: il paper trova l'effetto in tutte e quattro le classi.
4. **CFD contro futures.** Il paper misura futures; noi CFD su indici e oro a pronti. Se il CFD segue il future o
   l'indice a contanti non e' verificato: va dichiarato come differenza dalla fonte.

## Passo 4 — Potenza: gli indici USA bastano solo a effetto pieno; l'oro no; serve un indice europeo

**Come.** Script [`analysis/ultima_mezzora/potenza.py`](../analysis/ultima_mezzora/potenza.py), lanciato il 2026-10-09.
Dai nostri dati prende **solo** cio' che non dipende dal segnale: la deviazione del rendimento dell'ultima mezz'ora
(r_LH), la correlazione fra strumenti e il numero di sedute. **Non calcola il rendimento della giornata (r_ROD) ne'
nessuna media condizionata al segnale.** L'effetto atteso viene dal paper, pieno e dimezzato (09 §4.7), con due metriche:

- **segno**: lungo se la giornata e' salita fino alle 15:30, corto se e' scesa (Tab. 6, media della classe);
- **regressione**: r_LH su r_ROD, correlazione = radice dell'R² del singolo mercato (Tab. B1 e B3), in campione e fuori
  campione. Usa anche l'ampiezza del movimento, cioe' dove il meccanismo mette l'effetto.

Fattore 2,80 (alfa 5% a due code, potenza 80%).

**I dati, da 06/2020** (fuori dal campione della fonte):

| | sedute | deviazione r_LH | curtosi in eccesso |
|---|---|---|---|
| SPX500 | 1.538 | 26,4 pb | 4,5 |
| NAS100 | 1.538 | 30,7 pb | 4,3 |
| XAUUSD | 1.527 | 14,7 pb | **38,6** |

SPX500 e NAS100 hanno r_LH correlati a **0,96**: insieme valgono **1,02 strumenti**, ~1.570 sedute indipendenti, non 3.000.

**Metrica segno** (effetto pubblicato per le azioni: 6,86% annuo = 2,72 pb a seduta):

| | sedute necessarie, effetto pieno | a meta' | MDE con le sedute disponibili |
|---|---|---|---|
| SPX500 | 736 (2,9 anni) | 2.945 (11,7 anni) | 1,88 pb |
| SPX500 + NAS100 | 863 (3,4 anni) | 3.452 (13,7 anni) | 2,02 pb |
| SPX500 al netto dello spread US500 (0,34 pb) | 965 | 5.252 | — |

**Metrica regressione** (sedute per vedere la correlazione pubblicata):

| mercato | in campione: pieno / meta' | fuori campione: pieno / meta' |
|---|---|---|
| ES (S&P 500) | 228 / 917 | 340 / 1.367 |
| NQ (Nasdaq 100) | 189 / 763 | 206 / 832 |
| EU (media europea) | 330 / 1.327 | 311 / 1.252 |
| GC (oro) | 3.134 / 12.542 | 9.798 / 39.198 |

**L'oro.** La metrica segno con la media delle materie prime (1,72 pb) lo farebbe sembrare testabile, ma il paper dice
che l'oro **in particolare** e' molto piu' debole (R² 0,25% contro 3,41% dell'S&P). Convertendo la sua correlazione in un
effetto di solo segno (normale bivariata: rho × sigma × √(2/π), stima di Claude) l'effetto e' ~0,59 pb in campione e ~0,33
fuori: servono **~4.900-15.400 sedute**, contro 1.527. **L'oro non puo' fare da holdout.**

**Lettura.**
1. **Il campione di sviluppo** (SPX500 + NAS100 da 06/2020) vale **un solo strumento** con ~1.570 sedute. Ha potenza per
   l'effetto pubblicato, non per quello dimezzato con la metrica segno (servirebbero 13,7 anni). Con la regressione ha
   potenza anche a meta' dell'effetto fuori campione (1.367 sedute su 1.538), ma di poco.
2. **La regressione e' ottimista.** I numeri di Fisher assumono code normali: con curtosi 4,3-4,5 una parte dell'effetto
   sta in pochi giorni estremi. Un indizio sta nel paper stesso: dalla correlazione di ES la normale prevede ~3,9 pb di
   effetto di solo segno, la strategia vera della Tab. 6 ne fa 2,72 (circa il 70%). Alla G1 la regressione va testata con
   un bootstrap per blocchi di giorni, che ha meno potenza di questi numeri.
3. **Un holdout con potenza c'e', ma va scaricato.** Un indice europeo (DAX, Euro Stoxx 50, FTSE 100) da 06/2020 avrebbe
   ~1.550 sedute, mai usate dall'ORB, con la finestra 17:00-17:30 dell'Europa centrale (Tab. 1; 11:00-11:30 a New York),
cioe' **un'altra ora** rispetto agli USA e
   quindi quasi indipendente dal campione di sviluppo. Con la regressione basta a meta' dell'effetto europeo fuori
   campione (1.252 sedute). Piu' indici europei fra loro saranno correlati come SPX e NAS: contano come uno.
4. **Scelta della metrica primaria** (da fissare alla G1, decide Matteo): la regressione, o una strategia con posizione
   proporzionale al movimento della giornata, e' piu' potente e coerente col meccanismo; il segno e' piu' robusto alle
   code ma chiede piu' anni. Una sola primaria; l'altra si riporta come secondaria.

## Holdout europeo — dati scaricati (11/10), sigillati

Decisione di Matteo (11/10): si scaricano. Script
[`analysis/ultima_mezzora/scarica_dukascopy.py`](../analysis/ultima_mezzora/scarica_dukascopy.py): DAX, Euro Stoxx 50 e
FTSE 100 a M5 dal 2020, Dukascopy, UTC. **Sono l'holdout**: su questi file si lanciano solo i controlli meccanici di
`verifica_dati.py` (nessun rendimento, nemmeno la deviazione) finche' la pre-registrazione non e' approvata.

| feed | calendario, finestra | periodo | sedute complete da 06/2020 | note |
|---|---|---|---|---|
| DAX M5 | XETR, 17:00-17:30 Francoforte | 2020-01 → 2026-10-09 | **99,8%** di 1.622 | controlli meccanici a posto; 0 barre nella pausa notturna; 6 chiusure anticipate, tutte complete |
| EUSTX50 M5 | XETR, 17:00-17:30 Francoforte | 2020-01 → 2026-10-09 | **99,3%** di 1.622 | controlli a posto; feed attivo solo 08:00-21:55 (meno barre del DAX); barre ferme nella finestra 0,35%; 2023 al 97%; calendario di Francoforte usato come approssimazione |
| FTSE100 M5 | XLON, 16:00-16:30 Londra | 2020-01 → 2026-10-09 | **99,3%** di 1.608 | controlli a posto; 12 chiusure anticipate (12:30), complete al 92% |

Tutti e tre: monotonia, duplicati e coerenza dei prezzi a posto, 0 barre nella pausa notturna. Misurato l'11/10/2026.
Fra loro saranno molto correlati (stessa mezz'ora): per la potenza contano come **uno strumento**, non tre; quale sia
lo strumento primario dell'holdout (uno dei tre, o la loro media) si fissa nella pre-registrazione, prima di aprirli.

## Costi sugli indici europei (11/10)

Stesso metodo del passo 2 (`spread_mt5.py`, tick MT5, demo FP Markets, 158 giorni validi dal 2026-02-23 al
2026-10-09), ciascuno nella sua finestra:

| | spread mediano | costo per operazione, mediana (p90) | quota del lordo stimato |
|---|---|---|---|
| GER40 (DAX), 17:00-17:30 Francoforte | 0,50 punti | **0,20 pb** (0,21) | 7% |
| UK100 (FTSE 100), 16:00-16:30 Londra | 1,00 punti | **0,96 pb** (1,07) | 35% |
| EURO50 (Euro Stoxx 50), 17:00-17:30 Francoforte | 1,60 punti | **2,58 pb** (2,96) | **96%** |

L'Euro Stoxx 50 su FP Markets **non e' accessibile**: lo spread si mangia quasi tutto il lordo. Per questo l'holdout
della pre-registrazione e' il DAX, e gli altri due restano repliche descrittive.

## Passi che restano

5. **Slot** — ✅ deciso l'11/10: adesso, terzo slot esterno del 2026-Q4.
- **Metrica primaria** — ✅ Matteo, 11/10: proporzionale con tetto. Bozza della pre-registrazione scritta lo stesso
  giorno ([ULTIMA_MEZZORA_PREREGISTRATION](ULTIMA_MEZZORA_PREREGISTRATION.md)); revisione G1: **BLOCCA**, stato e
  correzioni nel suo §9.
- **Seguito** — approvata e testata il 12/10: **CLOSED** al train, holdout mai aperto (pre-registrazione §10,
  DECISIONS 2026-10-12 (2)). Questo referto resta valido per costi, dati e scarto del server.
