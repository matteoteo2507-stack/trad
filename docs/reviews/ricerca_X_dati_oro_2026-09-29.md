---
tipo: ricerca
stato: quarantena
aggiornato: 2026-09-29
nota: "Tutto e' dichiarazione di terzi, verificata il 2026-09-29. Prezzi dei fornitori letti sulle pagine ufficiali: cambiano, ricontrollare prima di comprare."
---
# Ricerca X (e fonti collegate) — prezzi dei dati, microstruttura dell'oro, risultati pubblicati

Specifica confermata da Matteo il 2026-09-29 (voci X1-X3). Eseguita da un subagente in sola lettura;
regola di arresto a blocchi da 5. **X in se' ha reso pochissimo**: per l'oro restituisce quasi solo
venditori di segnali. Il materiale utile viene da pagine ufficiali dei fornitori, CME e paper.
Le conferme si contano **per fonte**, non per occorrenza.

## X1 — Prezzi dei dati (letti il 2026-09-29)

| Fornitore | Cosa | Prezzo e condizioni | Fonte |
|---|---|---|---|
| **CFTC** | COT storico: Legacy dal **1986**, futures+opzioni dal 1995, Disaggregated dal 2009, TFF dal 2010 | **gratis** | [cftc.gov](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm) |
| **Pinnacle Data** | CLC: **98 commodity** in serie continue, le piu' vecchie dal **1969**; roll a scelta; esiste anche un DB COT | **$99** + aggiornamenti $20/mese | [pinnacledata2.com](https://pinnacledata2.com/clc.html) |
| **Norgate** | Futures: ~**100 mercati** su 11 borse, dal **1980** circa; close = settlement; continue non aggiustate e back-adjusted | **USD 148,50 / 6 mesi, 270 / 12 mesi** | [norgatedata.com](https://norgatedata.com/futurespackage.php) |
| **Norgate** | Azioni USA senza survivorship (delistati, costituenti storici dal 1990: piano Platinum) | Silver 270, Gold 360, **Platinum 630**, Diamond 787,50 USD/anno | [norgatedata.com](https://norgatedata.com/stockmarketpackages.php) |
| **Sharadar** | Fondamentali SF1 point-in-time, storia da **gennaio 1998** (fonte primaria; un rivenditore dice 1990: vale 1998) | uso personale: 19 / 29 / **39 $/mese** per 5 / 10 anni / tutta la storia | [sharadar.com](https://sharadar.com/pricing) |
| **Databento** | CME Globex (incluso COMEX): **dal 2010**; storico **da $0,50/GB** (tariffa minima, quella per schema non pubblica) | a consumo; **$125 di crediti gratis** per 6 mesi; piani da **$199/mese** | [databento.com](https://databento.com/pricing) |
| **Tick Data** | Futures, indici, FX dal 2008; **XAUUSD non confermato** | minimo **$1.000** per ordine storico; API da $250/mese con impegno annuale | [tickdata.com](https://www.tickdata.com/fee-estimate) |
| **Kibot** | FX tick + bid/ask dal 2009 (XAUUSD non indicato); futures continui | FX primi 10 cambi **$440**; futures $520 a 1 minuto, $1.950 tick | [kibot.com](https://www.kibot.com/buy.aspx) |
| **FirstRate Data** | GC continuo da 31-01-2008, 1 min → 1 giorno | prezzo del dataset **non mostrato**; aggiornamenti $99,95/anno | [firstratedata.com](https://firstratedata.com/i/futures/GC) |

Giudizi d'uso (opinione): un utente X ([@Solidrock85](https://x.com/Solidrock85/status/2080212544677990416),
2026-07-23) dice di aver ottenuto con **~100 $ di Databento** i futures che non riusciva a ricostruire da
Dukascopy. Due fonti su X indicano Norgate per i costituenti storici e Sharadar per i fondamentali.
Una recensione di un rivenditore di VPS contraddice la pagina ufficiale di Databento sulla profondita'
dello storico: vale la pagina ufficiale.

**Mancano** (prompt per Comet in fondo): tariffe per schema di Databento, prezzi di FirstRate, di CSI
Data, e se Tick Data vende XAUUSD spot.

## X2 — Microstruttura dell'oro

- **Spread per ora, due fonti indipendenti**: whitepaper CME (GC futures: ~1,39 tick = ~0,14 $ di media,
  **massimo alle 22:00 UTC**, conflitto: CME promuove il proprio contratto) e **Batten et al., PLoS ONE
  2017** (5 minuti, 2000-2015: spread "piuttosto costante lungo la giornata", piccolo aumento **attorno alle
  22 GMT**, in calo nel tempo). Contraddicono i blog dei broker ("Asia piu' larga del 30-50%"), che non
  hanno campione.
- **Lo spread spot/CFD di Dukascopy** (mediane annue 0,33-0,69 $, nostra misura del 28/09) sta ~2,4-5 volte
  sopra il futures: plausibile per un CFD, non prova da solo una distorsione.
- **Ipotesi verificabile gratis** (da un blog di broker, numeri scartati): *lo spread e' costante in punti
  base e sale col prezzo*. Si controlla sul nostro feed Dukascopy.
- **Costo della latenza per chi copia segnali**: **nessuno studio pubblicato**. Unico dato reale e'
  la metrica di slippage dei segnali MQL5 ([guida MetaTrader 5](https://www.metatrader5.com/en/terminal/help/signals/signal_monitoring)),
  che pero' riguarda la copia MT→MT.
- **Myfxbook "Real Spread XAUUSD"** per broker: fonte gratuita per confrontare Dukascopy col broker vero
  (unita' non dichiarata; sito con affiliazioni).

## X3 — Risultati pubblicati sull'oro (intraday-settimanale)

| Fonte | Cosa dice | Stato per noi |
|---|---|---|
| [Blose, Gondhalekar, Kort, *J. Econ. Finance* 2018](https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html) | rendimenti **notturni positivi, diurni negativi**, in mercati al rialzo e al ribasso, "economicamente importanti anche dopo i costi" (grandezze non nell'abstract) | da leggere per intero; **risultato pubblicato con razionale**, replicabile con dati gratuiti. Candidato a ipotesi nuova (costa una pre-registrazione esterna) |
| [Torul, working paper 2026-07-08](https://web.bogazici.edu.tr/torul/reflex.pdf) | la risposta dell'oro agli shock azionari 2024-26 in USD (−0,92, t −2,0) **sparisce in EUR** (−0,15, t −0,4): e' in gran parte l'effetto dollaro | non referato; utile come avvertenza su qualunque "l'oro sale nei risk-off" |
| [Chicago Fed Letter 464, 2021](https://www.chicagofed.org/publications/chicago-fed-letter/2021/464) | tassi reali: segno negativo ma **R² = 0,012** su dati giornalieri | nell'orizzonte breve il legame spiega pochissimo: raffredda il lead "intermarket" |
| Sobti et al. 2021; Hauptfleisch et al. 2016 | il **futures di New York** guida la scoperta del prezzo | contesto |
| Awartani et al. 2024; Elder et al. 2012; Cai et al. 2001 | reazioni a FOMC e dati macro; aggiustamento oltre i 5 minuti dopo il FOMC | contesto; richiedono intraday attorno agli annunci |
| WGC mid-year 2026 (via FXStreet) | H1 2026: Asia +12,9%, Nord America −15% | **n = 1 semestre**, conflitto WGC: solo descrittivo |
| evtradelabs (stagionalita' XAUUSD) | ~20 test senza correzione | scartato: ricerca di massa |

## Prompt per Comet (dati bloccati o mancanti)

1. «Apri https://databento.com/pricing e la pagina del dataset GLBX.MDP3 (catalog/cme/GLBX.MDP3). Riporta, con la data di lettura, il prezzo in $/GB per gli schemi trades, tbbo, mbp-1, bbo-1s, ohlcv-1m, ohlcv-1d e statistics. Poi, se possibile con il cost estimator del portale, stima il costo di GC (serie continua front-month) dal 2010-06-06 al 2026-09-26 per tbbo e per ohlcv-1m. Copia i numeri esatti, non riassumere.»
2. «Su https://www.tickdata.com (store o fee estimate) e su https://firstratedata.com/i/futures/GC: 1) Tick Data vende XAUUSD spot? Da che data e a che prezzo per symbol-year? Qual è il prezzo per symbol-year del futures GC (quotes+trades)? 2) Quanto costa su FirstRate il dataset GC e il bundle "Most Active Futures"? Riporta i prezzi esatti in USD con la data di lettura.»
3. «Su Myfxbook (registrati se serve), pagina "Real Spread XAUUSD" per Dukascopy e per [broker del copier]: esporta o copia lo spread medio per ora (UTC) e per sessione degli ultimi 3 mesi, indicando l'unità di misura dichiarata, e in particolare le 21:00–23:00 UTC e la domenica sera. Copia i numeri, non riassumere.»
4. «Apri https://www.csidata.com e trova il listino di Unfair Advantage per i futures mondiali (storia completa) e per i dati COT: prezzo mensile e annuale, con la data di lettura.»

## Risultati promt comet
1. Ho letto le pagine il 30 settembre 2026. La pagina HTML consultabile senza JavaScript non espone i valori numerici del listino né il risultato interattivo del cost estimator; quindi non posso copiare quei numeri esatti senza inventarli.

Prezzi per schema
Schema	Prezzo esatto in $/GB
trades	Non esposto nella pagina statica consultata
tbbo	Non esposto nella pagina statica consultata
mbp-1	Non esposto nella pagina statica consultata
bbo-1s	Non esposto nella pagina statica consultata
ohlcv-1m	Non esposto nella pagina statica consultata
ohlcv-1d	Non esposto nella pagina statica consultata
statistics	Non esposto nella pagina statica consultata
La pagina generale conferma che Databento misura e fattura i dati sulla loro dimensione non compressa in formato binario, con prezzi espressi in $/GB; CSV e JSON non aggiungono un sovrapprezzo.

Il dataset GLBX.MDP3 include gli schemi richiesti, tra cui Trades, TBBO, MBP-1, BBO-1s, OHLCV-1m, OHLCV-1d e Statistics.

Stima GC
Richiesta	Intervallo	Risultato esatto
Richiesta	Intervallo	Risultato esatto
GC front-month continuo, tbbo	2010-06-06 — 2026-09-26	Non ottenibile dalla pagina statica consultata
GC front-month continuo, ohlcv-1m	2010-06-06 — 2026-09-26	Non ottenibile dalla pagina statica consultata
La pagina dedicata a GC conferma che la serie è disponibile dal 2010-06-06 UTC e che il catalogo supporta i contratti continui; la documentazione Databento indica la sintassi GC.v.0 per il front month basato sul volume.

Non ho riportato valori approssimativi perché hai chiesto esplicitamente i numeri esatti. Il cost estimator interattivo richiede il caricamento dell’applicazione JavaScript e, per una stima precisa, la selezione di dataset, schema, simbolo continuo e intervallo; la pagina statica restituisce soltanto il messaggio che JavaScript deve essere abilitato.

2. Ho letto le pagine il 30 settembre 2026. La conclusione più importante è questa: i prezzi Tick Data non sono pubblicati direttamente nelle pagine consultabili; Tick Data descrive il prodotto e indica di contattare un esperto per il pricing. FirstRate, invece, mostra il dataset e il bundle, ma nei contenuti accessibili non espone il prezzo d’acquisto.

1. Tick Data
Prodotto	Disponibilità	Inizio dati	Prezzo pubblicato
Spot Forex, incluso XAUUSD se presente nella lista dei cross disponibili	Sì, Tick Data dichiara oltre 2.000 coppie spot Forex	1 maggio 2008	Non pubblicato; preventivo su richiesta
Futures GC – Gold Futures COMEX	Sì	Trades: gennaio 1984; Quotes: gennaio 2010	Non pubblicato; preventivo su richiesta
Tick Data dichiara che i dati spot Forex comprendono quotazioni tick-by-tick bid/ask e dati provenienti da oltre 95 contributori; tuttavia la pagina non conferma esplicitamente, nel testo accessibile, che il simbolo specifico sia “XAUUSD”. La disponibilità va quindi verificata nella lista dei simboli o direttamente con Tick Data.

Per GC, la tabella ufficiale riporta:

Trade Data Start: Jan-84.

Quote Data Start: Jan-10.

End Date: Present.

Exchange: COMEX.

Il prodotto futures include sia tick-by-tick Level I quotes, con bid/ask e size, sia trades, con prezzo dell’ultima esecuzione e volume.

Pertanto, il prezzo richiesto per symbol-year — sia per XAUUSD spot sia per GC quotes + trades — non è disponibile come tariffario pubblico. Tick Data pubblicizza il servizio, ma rinvia al contatto commerciale per il prezzo. La pagina futures conferma inoltre che il pricing è una sezione separata (“Data Pricing”), senza esporre nel contenuto estratto una cifra.

2. FirstRate Data
Dataset	Periodo indicato	Prezzo d’acquisto
GC – Gold Futures (CME), intraday bars	31 gennaio 2008 – 28 settembre 2026	Non visibile nella pagina consultata
Futures – Most Active, 130 futures	gennaio 2007 – settembre 2026	Non visibile nella pagina consultata
Per GC, FirstRate specifica che il dataset contiene frequenze 1 minuto, 5 minuti, 30 minuti, 1 ora e 1 giorno, con serie continue e singoli contratti. La pagina indica inoltre un mese di aggiornamenti gratuiti e, successivamente, un abbonamento annuale agli aggiornamenti di USD 99,95.

Il bundle Futures – Most Active, composto da 130 futures, contiene le stesse cinque frequenze intraday e include sia serie continue sia dati dei singoli contratti. Per gli aggiornamenti successivi al primo mese gratuito, la pagina indica USD 59,95 al mese.

La pagina del bundle conferma per GC:

Serie continua dal 31 gennaio 2008.

Contratti individuali da GCZ08 a GCZ29.

Dati aggiornati al 25 settembre 2026.

Prezzi esatti richiesti
Con la lettura effettuata il 30/09/2026, i soli prezzi numerici pubblicamente visibili nelle pagine accessibili sono:

FirstRate, aggiornamenti dataset GC dopo il primo mese: USD 99.95/anno.

FirstRate, aggiornamenti del bundle Most Active dopo il primo mese: USD 59.95/mese.

Non sono invece riuscito a verificare un prezzo numerico pubblico per:

acquisto iniziale del dataset GC su FirstRate;

acquisto iniziale del bundle “Most Active Futures” su FirstRate;

dati Tick Data XAUUSD spot, quotati per symbol-year;

dati Tick Data GC quotes + trades, quotati per symbol-year.

In altre parole, sarebbe scorretto inventare quei quattro importi: le pagine mostrano “Buy Now”, ma il prezzo non è restituito nel contenuto pubblico consultabile. Per un confronto economico serio, FirstRate richiede quindi il prezzo visualizzato nel checkout, mentre Tick Data richiede un preventivo commerciale.

3. Mi dispiace, ma non posso accedere a Myfxbook né esportare dati in tempo reale da quel sito.

Le mie capacità si limitano a:

Cercare informazioni pubbliche sul web (ma Myfxbook richiede login e i dati che chiedi sono dentro un’area riservata, quindi non sono accessibili via ricerca).

Leggere file che hai caricato qui nel progetto (attualmente vedo solo le lettere agli azionisti di Berkshire Hathaway, niente CSV o screenshot di spread).

Eseguire calcoli o analisi su dati che mi fornisci tu.

Per ottenere esattamente quello che chiedi (spread medio orario UTC e per sessione, ultimi 3 mesi, per Dukascopy e per il broker del copier, con focus su 21:00–23:00 UTC e domenica sera, copiando i numeri e non riassumendo), devi:

Accedere tu a Myfxbook.

Andare sulla pagina “Real Spread XAUUSD”.

Selezionare:

Broker: Dukascopy

Broker: il broker del tuo copier

Periodo: ultimi 3 mesi

Granularità: media per ora (UTC) e per sessione.

Esportare in CSV (se disponibile) oppure copiare le tabelle.

Incollare qui i dati (o caricare i CSV).

Una volta che avrò i numeri, potrò:

Riorganizzarli per ora UTC e per sessione.

Evidenziare 21:00–23:00 UTC e la domenica sera.

Mantenere l’unità di misura dichiarata (di solito pips o punti, a seconda di come Myfxbook la riporta per XAUUSD).


4. Ho visitato il sito csidata.com e ho cercato le pagine con i listini prezzi per Unfair Advantage, in particolare per i futures mondiali (storici) e per i dati COT (Commitment of Traders), con prezzi mensili e annuali e relative date di lettura.

Cosa ho trovato sul listino Unfair Advantage
Dalle pagine ufficiali di CSI e dalla documentazione di Unfair Advantage emergono questi punti chiave:

Copertura dati: CSI offre dati EOD (end-of-day) su futures, azioni, indici, opzioni e serie economiche/governative, con storia che in molti casi risale agli anni ’50 o oltre.

Futures mondiali: il database include 110+ exchange e migliaia di contratti futures; i dati possono essere trasformati in contratti continui “back-adjusted” e aggregati su base giornaliera, settimanale, mensile, trimestrale e annuale.

Dati COT: la documentazione recente menziona che i dati COT (Commitment of Traders) sono inclusi e aggiornati, con campi come volume medio e open interest totale.

Piani e prezzi indicati pubblicamente: sul sito compare un’offerta trial a $20 per 21 giorni e un piano a $99/anno per l’accesso ai dati; esiste anche un modulo di analisi tecnica a partire da $25/mese.

Tuttavia, non ho trovato una pagina pubblica con un listino dettagliato e aggiornato che specifichi:

il prezzo mensile e annuale distinto per il pacchetto “futures mondiali (storia completa)” in Unfair Advantage;

il prezzo mensile e annuale distinto per il modulo dati COT;

le date di lettura (es. “prezzi aggiornati al …”) associate a ciascun listino.

La struttura dei prezzi di CSI per Unfair Advantage è tradizionalmente basata su pacchetti per categoria di mercato (es. “North American Futures”, “World Futures”, ecc.) e su sottoscrizioni annuali, ma i dettagli precisi (importi esatti per ciascun pacchetto, opzioni mensili, e data di validità del listino) non sono riportati in forma tabellare nelle pagine pubbliche che ho estratto.

Come ottenere il listino esatto (futures mondiali + COT, mensile/annuale)
Per avere il listino preciso con:

pacchetto “futures mondiali (storia completa)” in Unfair Advantage;

modulo dati COT;

prezzi mensili e annuali;

data di lettura del listino;

ti consiglio di:

Controllare la pagina “Ordering / Pricing” di Unfair Advantage sul sito CSI (spesso raggiungibile dal menu principale di csidata.com → Unfair Advantage → Ordering/Pricing).

Usare il form di contatto / richiesta preventivo su csidata.com: CSI fornisce spesso listini personalizzati in base ai pacchetti scelti (es. “World Futures”, “COT data”) e alla frequenza (mensile/annuale).

Richiedere esplicitamente:

“Unfair Advantage – pacchetto futures mondiali con storia completa”

“Dati COT (Commitment of Traders) – opzione mensile e annuale”

“Listino aggiornato con data di validità”.