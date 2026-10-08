---
stato: BOZZA
aggiornato: 2026-10-08
decisione: "Matteo (08/10): test sulla storia 'per sicurezza e per avere una misura nostra', a prescindere dall'esito, accettando il costo del trial"
metrica_corrente: null
nota: "Una sola esecuzione. Massimo esito: LEAD con gate finale forward (storia gia' vista). Script: analysis/meanrev_indici/esegui_test.py"
---

# Pre-registrazione — RSI(2) di Connors sugli indici USA (candidato A)

Referto di potenza: [MR_INDICI_POTENZA.md](MR_INDICI_POTENZA.md). Fonti dell'effetto atteso:
[rsi2_fonti_comet_2026-10-08](reviews/rsi2_fonti_comet_2026-10-08.md). Famiglia nel contatore: `mr_indici_rsi2`.

## 1. Ipotesi e razionale

**Ipotesi.** Su SPX500 e NAS100 giornalieri, comprare sopra la media a 200 giorni quando RSI(2) scende sotto 10
rende, al netto dei costi CFD, **piu' di un ingresso casuale nello stesso indice, anno e regime, tenuto gli stessi
giorni**.

**Cosa la falsifica.** Un intervallo del divario (reale − casuale) il cui limite alto sta sotto 0,50% a trade:
escluso un **eccesso sul caso** di almeno 0,50% (§6). Cosa significa per ciascuna fonte pubblicata lo dice la tabella di
esclusione del §6, non questa frase.

**Razionale (classe, chi paga).** Ritorno alla media di breve: chi vende in fretta nei giorni di ribasso (vincoli di
rischio, margini, mandati) paga chi fornisce liquidita'; oppure reazione eccessiva. Limite all'arbitraggio: serve
capitale proprio quando il rischio e' massimo, con coda sinistra nei crolli. Classe 2 o 3 di
[09_fonti_di_vantaggio](../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md), **da confermare** con le fonti del §6.

**Perche' non e' gia' scartata, e perche' non e' una riapertura** (bloccante 3 della revisione G1 del 08/10).
- Il 17/08 (DECISIONS) questa stessa regola, mostrata da StrategyQuant X, fu **scartata senza test** come
  *"long-only su indice in una finestra rialzista, lo stesso beta-trap del router momentum+MR"*. L'obiezione e'
  giusta per un confronto contro zero, ed e' **superata dal disegno**: il baseline primario (§5) e' un ingresso casuale
  long nello stesso regime, tenuto **gli stessi giorni**, quindi il beta e la deriva per giorno stanno in entrambi i
  bracci e il divario misura solo il tempismo del segnale.
- Non e' una riapertura di `meanrev_vol` (CLOSED 08/07, z-score N=10 su 16 asset, provenienza non dichiarata): la
  regola e' diversa (RSI(2), filtro di trend, solo long), la fonte la sceglie **sugli indici USA indipendentemente** dai
  nostri esiti (Connors 2008), e il tetto e' LEAD con forward. Restringersi agli indici dopo aver visto che
  `meanrev_vol` era positiva sugli indici sarebbe un cambio di asset a esito visto: e' il motivo del tetto.

**Provenienza.** Fonte umana esterna: video 2 della sessione col socio VELTRIX (04-05/10) e Connors-Alvarez 2008
(di seconda mano). **Consuma il secondo slot** di pre-registrazione esterna del 2026-Q4. Proposta dal LLM? No: la
regola e' quella delle fonti, non tarata da noi.

## 2. Regola (esatta, uguale per tutto il campione)

- Segnale alla **chiusura** del giorno t: chiusura > SMA(200) **e** RSI(2) < 10 (RSI di Wilder, alpha 1/2).
- **Ingresso** long all'**apertura** di t+1.
- **Uscita**: alla prima chiusura in posizione con RSI(2) > 70, oppure alla chiusura del 10° giorno in posizione;
  si esce all'**apertura** del giorno dopo. **Nessuno stop-loss** (come tutte le fonti).
- Una posizione alla volta per indice; i segnali durante una posizione si ignorano.
- **Fill.** Ingresso e uscita a mercato all'apertura successiva al segnale: sempre ottenibili (nessun livello
  oltrepassato possibile). Fill non ottenibili attesi: 0, riportati comunque.

## 3. Dati

Dukascopy D1, `analysis/trading-bot-eval/data/dukascopy_d1/{SPX500,NAS100}_D1.csv`, 16/01/2012 → 13/08/2026
(barre del sabato e della domenica escluse: i file grezzi hanno 4.453 e 4.463 righe, le barre scartate si
stampano). Controllo `core.data_checks` sul file **grezzo**, stampato prima del calcolo. Le barre
Dukascopy si chiudono alle 00:00 UTC, non alla chiusura della borsa USA: l'RSI e' quello del CFD, non dello SPY delle
fonti (differenza dichiarata, non corretta).

**Split.** Il campione intero e' l'holdout (nessun train, nessun parametro da tarare): una sola esecuzione,
`gate_finale: "forward"` nel contatore (precedente: Gump, 02/10). **Storia gia' vista**: mean reversion vol (08/07,
indici positivi da soli) e B1 (17/09, gruppo index +0,047 al 99,7° percentile, D1 2012-2026). Per questo il massimo
esito e' **LEAD**, mai GO.

## 4. Costi

FP Markets letti in MT5 il 08/10/2026 (FPMarkets-Demo): spread US500 0,25 punti, US100 0,60 punti; swap long per notte
**0,0152%** (US500) e **0,0143%** (US100) del prezzo, tripla il venerdi'. Applicati in percentuale a tutta la storia: con
i tassi del 2012-2021 lo swap vero era piu' basso, quindi il costo e' **conservativo**. Stress: costi **3x**.

## 5. Baseline

`core.random_baseline.BarSampler`, **solo l'istante d'ingresso e' casuale**: stesso indice, strato = indice-anno,
regime = chiusura sopra SMA(200), 20 controlli per trade reale, seme 42, **senza `trim_tail` per anno** (la fine
della serie la gestisce il cammino); si stampano gli eventi rimasti senza controlli.
- **Primario: durata copiata.** Ogni controllo tiene esattamente i giorni del trade reale appaiato, con la stessa
  esecuzione (apertura → apertura, stessi costi). Motivo, trovato sui dati sintetici prima di guardare il mercato: con
  la stessa regola d'uscita un ingresso casuale esce dopo 2 giorni di mediana contro 5 del reale (RSI gia' sopra 70),
  e in un mercato che sale il divario premierebbe la regola per la sola deriva.
- **Descrittivo: stessa regola d'uscita.** Riportato con la sua durata, dichiarato confuso.
- `check_matching` stampato accanto al risultato, con **ATR al segnale** fra le dimensioni osservate (i segnali reali
  arrivano dopo un calo, con volatilita' piu' alta: spiegazione alternativa "premio per la volatilita'"), e un divario
  descrittivo in unita' di ATR.

## 6. Metriche, soglie e verdetto (scritti prima)

Unita': rendimento **netto** per trade in % del prezzo. Intervalli: bootstrap percentile al 95% per **episodio**
(componenti connesse degli intervalli [entrata, uscita) sovrapposti su entrambi gli indici: SPX e NAS in posizione
negli stessi giorni sono un evento solo, anche se entrati in giorni diversi), media per trade dentro ogni replica,
5.000 repliche, seme 42. MDE = 2,80 x errore standard del bootstrap. Motivo (revisione G1): il cluster per data
d'ingresso lasciava fuori il 37% di trade sovrapposti, e con indici correlati a 0,9 il limite basso del divario
superava 0 nel 7,5% dei nulli invece del 2,5%.

| esito | condizione | conseguenza |
|---|---|---|
| **NESSUN VERDETTO** (prima di tutto) | `checklist_dati` o `check_matching` ROTTO, o piu' del 5% di eventi senza controlli | si corregge come esecuzione (0 trial) e si rilancia una volta (§8) |
| **LEAD** (ha la precedenza sugli altri) | limite basso dell'attesa netta > 0 **e** limite basso del divario > **B_NULL** **e** attesa netta con costi 3x > 0 **e** divario puntuale > 0 su **entrambi** gli indici | gate finale forward, nuova pre-registrazione per il forward |
| **CLOSED** | limite alto del divario (netto) < **0,50%**: escluso un **eccesso sul caso** di almeno 0,50% a trade | famiglia chiusa; cosa significa per le fonti lo dice la tabella di esclusione, non l'etichetta |
| **NON DIMOSTRATO** | il resto | si scrive con l'MDE accanto; famiglia chiusa per potenza, non refutata |

**Scelta della soglia (opzione c, 08/10).** Matteo ha chiesto l'opzione con la massima trasparenza sui risultati e mi
ha delegato la scelta. Valutate: (a) soglia 0,50% sul divario; (b) soglia tradotta dalla replica piu' bassa (sotto
l'MDE: quasi sempre NON DIMOSTRATO); (d) rapporto di verosimiglianza (metodo nuovo, non tarato nel repo); (e) test di
equivalenza (coincide con a). Scelta: **(c) = l'etichetta di (a) + una tabella di esclusione obbligatoria**, perche'
le fonti e il test misurano cose diverse: le fonti un rendimento **lordo assoluto**, che contiene la crescita del
mercato nei giorni tenuti; il test un **eccesso sul caso**, che non la contiene. Una soglia sola giudicherebbe una
delle due con il metro dell'altra.

**Tabella di esclusione** (sempre stampata, decisa ora; corretta nella seconda passata G1). Per ogni effetto pubblicato
(Murtazin 0,51%, Quantitativo 0,60%, BacktestEverything 0,75%, QuantifiedStrategies 0,95% nella variante con SMA200 e
uscita RSI > 80):
- **nel loro metro**: ESCLUSO se il limite alto del nostro rendimento **lordo assoluto** e' sotto il valore; "superato"
  se il limite basso e' sopra; altrimenti "non escluso".
- **tradotto nel nostro**, solo dove la fonte da' i numeri per calcolare la crescita del **suo** campione nei giorni
  tenuti: Murtazin (buy & hold da $1 a $8,68 in 26 anni, tenuta 3,7 giorni → ~0,12%, crescita non condizionata, che
  sottostima quella sopra la SMA200). Si confronta il nostro **divario lordo** con 0,51% − 0,12% = 0,39% e, come limite
  prudente, con la crescita doppia: 0,51% − 0,24% = 0,27%. **In questa colonna la direzione e' opposta**: con la crescita
  sottostimata l'eccesso attribuito alla fonte e' gonfiato, quindi un ESCLUSO tradotto e' **ottimista** e si cita solo se
  regge anche con la crescita doppia; un "superato" tradotto e' prudente. Per le altre fonti: "non traducibile". ⚠️ La prima versione traduceva con la **nostra** crescita
  misurata: era un'identita' (la crescita si toglieva da tutti e due i lati) e ripeteva la colonna "nel loro metro".
- **Direzione dell'errore**: il nostro periodo (2012-2026) ha probabilmente piu' crescita di quello delle fonti (che
  comprende il 2000-2012 piatto); se le fonti sono nette di costi, va nello stesso verso. Quindi ESCLUSO nel loro metro e'
  **conservativo**, "superato" e' **ottimista**: un "superato" **non si cita** come effetto pubblicato confermato.
Il referto riporta la tabella intera accanto all'etichetta. Esempio dal controllo sintetico (nullo con sola crescita,
seme 1): lordo assoluto +0,515% [+0,09; +0,90] (sembra Murtazin) ma divario +0,19% [−0,28; +0,61]: NON DIMOSTRATO;
QuantifiedStrategies (0,95%) risulta ESCLUSO nel loro metro, le altre fonti non escluse ne' confermate. Un mercato con
sola crescita riproduce lo 0,51% pubblicato: e' il "beta-trap" del 17/08 in cifre, ed e' il motivo della tabella.

**Distorsione del nullo (B_NULL).** Sotto il nullo il divario a durata copiata esce in media **positivo**: la durata e' un
esito del cammino del trade reale, e il pool dello stesso anno contiene finestre sovrapposte a quel cammino selezionato
dal segnale (seconda passata G1, ~+0,05%). Misurata **prima** del test con il codice del test
(`analysis/meanrev_indici/calibra_nullo.py`, 200 serie per condizione): **B_NULL = 0,09%** (distorsione misurata +0,063% [+0,038; +0,088] con crescita 0,05%/giorno e indici a 0,9; +0,047%
[+0,018; +0,075] senza crescita; scelto il limite alto della condizione piu' vicina ai dati veri, arrotondato in su). Il LEAD richiede il
limite basso del divario sopra B_NULL. CLOSED e NON DIMOSTRATO non la correggono: la distorsione li sposta nella
direzione prudente. **Ipotesi dichiarata:** B_NULL viene da serie con volatilita' costante (t5, 1,1% al giorno) e crescita
costante; sui dati veri (volatilita' a grappoli, crescita variabile, volatilita' piu' bassa sopra la SMA200) la
distorsione puo' essere diversa, in direzione ignota. Misure indipendenti del gatekeeper: +0,052 ± 0,022 e +0,063 ± 0,014.

**Potenza: fonte unica di questo numero.** MDE del divario sui nulli sintetici col codice del test (deriva 0,05%/giorno,
indici correlati a 0,9, cluster per episodio): **0,53-0,66%** (§9). Sostituisce lo 0,30% del referto di potenza (tenuta
di 3 giorni, nessun raggruppamento). Il valore sui dati reali si legge nel referto dell'esito. Gli altri documenti
rimandano qui.

**Potenza del LEAD** (terza passata G1). Errore standard del divario ~0,19-0,24% (MDE / 2,80). Con B_NULL la soglia del
LEAD sale: per vederlo con l'80% di probabilita' serve un **eccesso vero sul caso di circa 0,62-0,75%** a trade. Con
l'eccesso di Murtazin tradotto (0,27-0,39%) la probabilita' di un LEAD e' ~15-30%. Un esito diverso da LEAD **non
smentisce** Murtazin: lo dice la tabella, non l'etichetta.

**Controlli del verdetto** (sintetici, 08/10, prima del mercato, con deriva 0,05%/giorno e indici correlati a 0,9
dopo la revisione G1): riportati nel §9.

## 7. Descrittivi (non decidono) e doppio binario

Per indice; anni con somma netta positiva; runs test; rendimento per giorno in mercato (somma/somma); baseline con la
stessa regola d'uscita; attesa **lorda** assoluta con il suo intervallo; Sharpe per trade col pavimento di futilita'
1,65/sqrt(n) e PSR (1 trial: DSR = PSR). **Doppio binario** (STRATEGY_LIFECYCLE §4quater): binario 1R = posizione fissa; overlay O1 e
O3 con `confronta_overlay` (unita' = ATR% al segnale); prop FTMO 2 fasi con `confronta_overlay_prop` (regole citate
senza URL, costo ignoto: solo pass rate e `pass_zero`). ⚠️ Senza stop il rischio per trade non e' definito: il
binario prop e' illustrativo **e non se ne trae nulla** (con ~14 trade l'anno e un orizzonte di 250 giorni il pass
rate e' vicino a zero per costruzione), e una versione da prop con stop sarebbe una **regola diversa**, non testata qui.
Per un eventuale forward: le barre (Dukascopy alle 00:00 UTC o server FP Markets) vanno fissate nella sua
pre-registrazione, perche' danno RSI diversi; in FTMO serve il conto Swing (la regola tiene nel weekend).

## 8. Contabilita' e kill

- **1 trial**, budget 1. Nessuna variante: soglie, finestre, uscita e costi sono questi. Qualunque modifica dopo
  l'esito e' una pre-registrazione nuova.
- **Descrittivi su episodi:** PSR e pavimento di futilita' 1,65/sqrt(n) con n = episodi, non trade.
- **Assunzioni e direzione dell'errore:** trade non indipendenti fra indici → CI a cluster per episodio; swap attuale
  su tutta la storia → costo sovrastimato in media (pessimista), sottostimato nel 2023-2025; dividendi sul CFD long non
  accreditati (pessimista); spread alle 00:00 UTC piu' largo di quello letto (coperto dal 3x); chiusura Dukascopy alle 00:00 UTC invece della chiusura di
  borsa → segnali diversi da quelli delle fonti (direzione ignota, dichiarata).
- **Kill:** CLOSED o NON DIMOSTRATO chiudono la famiglia; nessun round di rifinitura.
- **Procedura di ripresa:** se l'esecuzione si interrompe dopo aver letto i dati, il difetto si corregge come
  esecuzione (0 trial), si scrive una voce in DECISIONS e si rilancia una volta.

## 9. Revisione G1 (08/10) e controlli del verdetto

**Gatekeeper, prima passata: BLOCCA** con tre bloccanti, nessuno sui dati reali (eseguito solo il sintetico).
1. Soglia di CLOSED in unita' sbagliate (lordo assoluto pubblicato contro divario al netto della deriva): **chiuso con
   l'opzione (c)** (§6), scelta su delega di Matteo.
2. Cluster per data d'ingresso insufficiente con indici sovrapposti: **corretto**, cluster per episodio.
3. Regola scartata il 17/08 senza voce che registri il ripensamento: **corretto**, §1 e DECISIONS 2026-10-08 (2).
Riserve accolte: ATR nel matching, niente `trim_tail` per anno, eventi senza controlli stampati, controlli dati sul
grezzo, precedenza LEAD e ampiezza su entrambi gli indici, PSR e futilita', costi e barre del forward dichiarati.

**Controlli sintetici dopo le correzioni** (deriva 0,05%/giorno, indici correlati a 0,9, regola e codice del test):

| serie | esito |
|---|---|
| nullo, 8 semi | **0 LEAD**; divario puntuale da −0,05% a +0,21%; MDE del divario **0,53-0,66%**; 4 CLOSED e 4 NON DIMOSTRATO con soglia provvisoria 0,50% |
| distorsione del nullo, 200 serie per condizione (`calibra_nullo.py`) | +0,063% [+0,038; +0,088] con crescita; +0,047% [+0,018; +0,075] senza → **B_NULL = 0,09%** |
| ritorno alla media forte | **LEAD**: divario +1,03% [+0,84; +1,23], matching a posto su durata (3 contro 3 giorni) e ATR (1,42 contro 1,41) |

**Gatekeeper, terza passata: PASSA CON RISERVE, 0 bloccanti.** Riserve accolte prima dell'approvazione:
1. Se `checklist_dati` o `check_matching` e' ROTTO, o piu' del 5% di eventi resta senza controlli, lo script esce
   (codice 3) **prima di stampare un solo rendimento**: un NESSUN VERDETTO non deve mostrare l'esito che poi si corregge.
   Controllo negativo con i due controlli forzati ROTTI: uscita 3, nessun rendimento a schermo. Controlli dei dati sul
   grezzo dei file reali gia' eseguiti: a posto, con riserva su barre/anno (257-358: nei file ci sono barre di weekend).
2. Colonna tradotta della tabella con la crescita di Murtazin semplice e **doppia** (0,39% e 0,27%): un ESCLUSO tradotto
   si cita solo se regge con la doppia (§6).
3. Potenza del LEAD dichiarata (§6): eccesso necessario ~0,62-0,75%, probabilita' di LEAD ~15-30% se vale l'eccesso
   tradotto di Murtazin.
4. Ipotesi di B_NULL dichiarata (§6): volatilita' costante; sui dati veri la distorsione puo' differire, direzione ignota.
5. Esempio del seme 1 corretto (§6).
Dopo le correzioni: nullo seme 1 NON DIMOSTRATO (divario +0,19% [−0,28; +0,61]); ritorno alla media iniettato (forza 0,3,
seme 3) **LEAD**, divario +1,11% [+0,85; +1,35].
