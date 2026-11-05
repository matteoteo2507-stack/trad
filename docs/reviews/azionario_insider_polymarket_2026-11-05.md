---
titolo: "Idee dall'inbox del 04/11: infrastruttura azionaria, ipotesi sugli insider, Polymarket"
data: 2026-11-05
stato: bozza — 0 trial, nessuna pre-registrazione aperta
provenienza: "Matteo, inbox dell'hub del 04/11 (`DISTILLARE TR.md`) e richiesta in sessione del 05/11"
---

# Idee del 04/11: infrastruttura azionaria, insider, Polymarket

Tre domande di Matteo per la sessione del 05/11:
1. come riusare l'infrastruttura di selezione azioni costruita a giugno;
2. quali strategie sugli insider si possono testare;
3. se Polymarket sara' tradabile (anche con una VPN) o se serve solo come fonte di dati.

Nessun dato di rendimento e' stato guardato. Tutto cio' che viene dalla letteratura e' **nota a Claude, non letta:
quarantena**.

---

## 1. L'infrastruttura dello Stock Selector: cosa si riusa

Stato: lo score fondamentale e' **non validato** (DECISIONS 2026-10-25 (7)); il momentum/RRG e' **chiuso** (IC
nullo su 12 anni, [review del 01/06](stock_selector-2026-06-01.md), Risultato 1). L'obiettivo asimmetrico ("batti
l'indice nei rialzi, positivo nei cali") resta non raggiungibile con un portafoglio solo long: e' quello che ha
chiuso il selettore, non lo score.

| Pezzo | Dove | Si riusa? | Perche' |
|---|---|---|---|
| Score 0-6 (D/E, P/E, EPS, margine operativo lordo, margine netto, ROE > tasso privo di rischio) | `strategies/stock_selector/scoring.py`, `compute_fundamental_score` | **si', la funzione** | e' pura: riceve i numeri, non li scarica. Basta darle i numeri **com'erano a ogni data** |
| Dati del selettore (lista S&P 500 di oggi, fondamentali di yfinance) | `data_sources.py` | **no** | sono i membri **di oggi** (survivorship) e i bilanci **di oggi** (non point-in-time): un backtest con questi dati e' falso per costruzione |
| Motore cross-sezionale: IC per data, quintili, long-short, attribuzione per regime | `analysis/backtest.py` | **si', come schema** | la meccanica (rango per data, rendimento successivo, IC di Spearman, regime con `core.regime`) vale per qualsiasi segnale sui titoli. Va collegato ai dati nuovi e alle primitive di `core/` (baseline casuale, errori standard per data, non i p-value nominali) |
| Prezzi in cache | `analysis/_cache/hist_prices.parquet` | **no** | costituenti attuali applicati al passato |
| Filtro macro e scenari | `scoring.py`, `derive_scenario` | **no, per ora** | e' un secondo segnale: un test dello score lo deve escludere (o testarlo per ablazione, LIFECYCLE §4bis) |

**Lo strato di dati che manca, ed e' gratuito** ([ricerca dati del 25/10](ricerca_dati_2026-10-25.md) §2):
- prezzi e appartenenza giornaliera all'S&P 500 dal 1970, delistati compresi (`Johnbrick123/sp500-data`; **nessuna
  licenza dichiarata**: si usa in locale, mai in git; prima va passato da `core.data_checks`);
- bilanci SEC dal 2009 con l'ora di accettazione del deposito (uso point-in-time possibile);
- Form 3, 4 e 5 dal 2006, per gli insider.

**Proposta: uno strato unico "azionario USA point-in-time"** (codice in `data/` o `core/`, dati fuori da git) che
serve a tutte le idee sull'azionario: lo score fondamentale, gli insider (§2), il PEAD (D3). Si costruisce una volta,
con i controlli dei dati, e **non e' un trial**: non si guarda nessun rendimento.

**Lo score come famiglia da testare** (decisione di Matteo, non ancora presa):
- e' un filtro di **qualita'** (redditivita', poco debito): la classe del modulo 09 va scritta alla G1 (premio di
  rischio o errore di prezzo? chi paga?);
- le **14 soglie** sono state scelte a mano in 6 versioni del notebook mai documentate: la review chiedeva di contare
  almeno 100 tentativi nel DSR. In piu' le soglie sono state fissate nel 2025: un test sul 2009-2025 e' un backtest di
  una regola disegnata **dopo** quei dati. La conferma vera puo' venire solo dal forward (LIFECYCLE §7c, per analogia);
- metrica naturale: IC dello score per data e quintili, contro un baseline di titoli casuali con la stessa esposizione
  di settore e di dimensione.

---

## 2. Insider: ipotesi testabili (bozza per la G1)

Stato di partenza: BACKLOG **D9**, parcheggiata il 25/10 per i dati (prezzi senza survivorship) e il perimetro. Il
perimetro si e' allargato all'azionario la sera stessa; i dati del §1 sono gratuiti. Resta da risolvere
l'**esecuzione** su azioni singole USA (broker, costi, frazionamento: domanda 6 della griglia).

**Classe e chi paga** (modulo 09, §4). L'insider ha l'informazione (classe 4), ma noi la leggiamo **dopo** che e'
pubblica: per chi segue i Form 4 la classe e' la **3**, reazione lenta del mercato a un deposito pubblico (correzione
del gatekeeper, 25/10). Chi paga: chi vende in quei giorni senza guardare i depositi. Limite all'arbitraggio
dichiarato dalla letteratura (quarantena): l'effetto sarebbe piu' forte nelle piccole societa', dove arbitrare costa di
piu'. **Conseguenza da scrivere prima:** sull'S&P 500 ci si aspetta un effetto piu' piccolo che nelle small cap, e le
small cap richiedono dati a pagamento (FirstRate).

**Regole comuni a tutte le varianti** (da fissare alla G1):
- **data del segnale = accettazione del deposito su EDGAR**, non la data della transazione (i Form 4 arrivano fino a
  due giorni lavorativi dopo); ingresso alla prima apertura successiva;
- solo **acquisti sul mercato aperto** (codice P); esclusi assegnazioni, esercizi di opzioni, piani 10b5-1 dove
  dichiarati;
- solo lungo: le vendite degli insider hanno molte ragioni non informative (diversificazione, tasse), e lo short su
  azioni singole non e' accessibile;
- universo: membri dell'S&P 500 **alla data**; baseline: titoli casuali dello stesso giorno con lo stesso settore e
  la stessa dimensione, stessa durata (`core.random_baseline`);
- unita' indipendente: il **mese di calendario** (gli eventi dello stesso periodo sono correlati), non il singolo
  acquisto.

**Una famiglia, tre varianti dichiarate prima** (LIFECYCLE §4bis, regola del 04/11: le condizioni che la fonte
prevede sono varianti, un trial ciascuna):

| | Variante | Cosa la distingue | Da dove viene (quarantena) |
|---|---|---|---|
| I-a | **Acquisti "opportunistici"** | l'insider non compra nello stesso mese negli anni precedenti; i "di routine" sono esclusi | Cohen, Malloy, Pomorski 2012 |
| I-b | **Acquisti in gruppo** | almeno k insider diversi della stessa societa' comprano in una finestra breve | letteratura sui "cluster buys", da trovare e leggere |
| I-c | **Ruolo** | solo amministratore delegato e direttore finanziario, contro tutti | Lakonishok-Lee 2001 (effetto per ruolo), da leggere |

Le tre misurano la **stessa grandezza** (l'intensita' di acquisto degli insider): sono **una famiglia**, e ogni
variante e' un trial nel DSR. Prima di qualunque rendimento:
1. **Potenza** (0 trial): contare dagli archivi Form 4 quanti acquisti per variante cadono su membri dell'S&P 500
   dal 2006, e quanti mesi indipendenti li contengono; con l'effetto atteso dichiarato prima, calcolare l'MDE. Se
   l'MDE supera l'effetto plausibile per le large cap, la famiglia si chiude **prima** di spendere un trial (come
   `meanrev_kichev`). Lo schema esiste gia': `analysis/meanrev_indici/potenza.py`.
2. **Holdout**: gli ultimi anni sigillati, oppure solo forward (§7b-7c). Si decide alla G1.
3. **Quota**: l'idea e' di Matteo e arriva dall'hub, quindi binario `hub` (1 a trimestre, 0 usate nel 2026-Q4 secondo
   il contatore del 04/11). Da confermare alla G1.

**Fuori da questa famiglia:**
- **Operazioni dei parlamentari USA** (via Quiver Quantitative o i registri pubblici del Congresso): meccanismo
  diverso (informazione politica, non aziendale), quindi **famiglia diversa**. Ritardo di pubblicazione fino a 45
  giorni; la letteratura che ricordo e' discordante (quarantena). Prima va capito se i dati storici sono gratuiti e
  con quale licenza.
- **Insider pesati con la geopolitica**: resta bloccata dalla domanda 2 (nessuno ha scritto perche' il contesto
  cambierebbe il contenuto di un acquisto) e dal registro delle previsioni dell'hub.
- **Quiver Quantitative** e' una fonte di dati, non un'ipotesi. I backtest che pubblica sono statistiche dichiarate
  da terzi (checklist 7 del gatekeeper): quarantena. I Form 4 grezzi della SEC sono gratuiti e restano la fonte
  primaria; Quiver serve, se serve, per i dati che la SEC non pubblica in tabelle.

---

## 3. Polymarket: tradabile o solo fonte di dati?

**Oggi non e' tradabile dall'Italia, nemmeno con una VPN.** Tre ragioni indipendenti:

1. **E' bloccato.** L'ADM l'ha messo nella lista dei siti non autorizzati una prima volta nel 2025 e una seconda il
   10/07/2026, con oscuramento dal 27/07/2026; il TAR del Lazio non ha sospeso il blocco
   ([Il Sole 24 Ore](https://en.ilsole24ore.com/art/online-game-from-27-july-polymarket-will-no-longer-be-accessible-in-italia-AJdNZLT),
   [Milano Finanza](https://www.milanofinanza.it/news/polymarket-il-tar-del-lazio-respinge-il-ricorso-d-urgenza-il-sito-resta-oscurato-in-italia-202608051324451066),
   [Open](https://www.open.online/2026/07/13/polymarket-lista-nera-agenzia-dogane-perche/)). Anche la Francia l'ha
   bloccato il 16/07/2026.
2. **Il rischio e' anche del giocatore.** Secondo l'ADM, chi partecipa a scommesse di operatori senza concessione e'
   punito con un'ammenda e con l'arresto fino a tre mesi (L. 401/1989, art. 4;
   [comunicato ADM](https://www.adm.gov.it/portale/documents/20182/156031934/comunicato+stampa+siti+non+aams+.pdf/a0b31796-a4d2-d127-528a-40559fadd3bc)).
   La VPN non cambia lo stato legale della piattaforma. Il caso concreto va chiesto a un avvocato: qui non si da' un
   parere legale.
3. **Il conto non sarebbe al sicuro.** Le condizioni di Polymarket vietano di aggirare i blocchi geografici, e dal
   2026 la piattaforma sospende i conti sospetti e chiede il KYC: fondi congelati o conto chiuso
   ([Biometric Update](https://www.biometricupdate.com/202606/polymarkets-vpn-crackdown-puts-prediction-market-id-controls-under-scrutiny),
   [Bitcoin.com](https://news.bitcoin.com/report-polymarket-pushes-kyc-on-crypto-traders-as-geoblocking-gaps-draw-global-scrutiny/)).
   Le condizioni originali non sono state lette direttamente: fonti secondarie.

**Quando potrebbe diventarlo:** con una concessione ADM a Polymarket (o a un'altra piattaforma di previsione), o con
una sentenza che la distingua dalle scommesse. Da ricontrollare quando cambia la notizia, non a calendario.

**Come fonte di dati serve, ed e' lecito:** i prezzi sono pubblici. Due usi:
- **riferimento del registro delle previsioni dell'hub** (scelta aperta in [[geopolitica]]): le previsioni di Matteo o
  di una fonte battono il prezzo di mercato (Brier score)? E' l'unica misura possibile dell'"edge da previsione", a
  costo zero e senza capitale;
- **probabilita' di eventi** (decisioni della Fed, elezioni) come variabile di contesto in un test di `trad`, con
  dati datati: il dataset pubblico Polymarket + Kalshi trovato il 25/10 ([ricerca dati](ricerca_dati_2026-10-25.md),
  riga 95) va prima controllato.

### "Grokbot"
E' **Grok Bot** di SpaceXAI (beta dall'11/08/2026): agenti con un computer nel cloud. Il caso virale e' un post su X
di agosto, *"$50 diventati $5.273 in 48 ore"* su Polymarket
([post](https://x.com/Argona0x/status/2091946932037906774)), con scansione di 500-1000 mercati, sentiment di X,
prezzi sbagliati oltre il 6% e puntate con Kelly. Un riepilogo di X lo contesta (cruscotto fabbricato, portafoglio
piu' vecchio della storia raccontata); un altro filo racconta un bot sceso a 34 $
([post](https://x.com/0xkkai/status/2092661234344603997)). **Statistiche dichiarate da terzi, contestate: quarantena.**
Le idee dentro (prezzi sbagliati contro una stima propria, Kelly) si possono misurare solo come previsione su dati
pubblici; come trading, dall'Italia valgono le tre ragioni sopra.

---

## 4. La domanda piu' larga: trading su singole azioni, anche fuori dagli USA (05/11)

**Una correzione di partenza.** Lo stock picking **non** e' stato bocciato matematicamente: e' stato misurato nullo
solo il **momentum/RRG** fra i titoli dell'S&P 500 (12 anni). Lo score non e' mai stato testato, e "acquista e tieni"
era il formato di quei test, non un limite del metodo.

**Le singole azioni sono una classe di strumenti nuova.** Per il §7 di LIFECYCLE *"una classe di strumenti realmente
diversa"* e' evidenza esterna nuova: le famiglie chiuse sugli indici (ritorno alla media, tendenza, apertura) **possono
riaprire** sulle singole azioni, ma come riapertura della **stessa famiglia** (§7a: trial sommati, quota). Non sono
famiglie nuove: stessa grandezza = stessa famiglia.

**Dove le singole azioni hanno qualcosa che gli indici non hanno:** gli **eventi della societa'**, tutti datati e
pubblici, e tutti a orizzonte breve (trading, non acquista e tieni):

| Evento | Classe (modulo 09) | Chi paga, in una riga | Dati gratuiti | Stato |
|---|---|---|---|---|
| Acquisti degli insider (Form 4) | 3 | chi vende senza leggere i depositi | SEC dal 2006 | §2 |
| Operazioni dei politici | 3 (per chi copia) | come sopra, con un ritardo molto piu' lungo | Quiver; registri del Congresso | sotto |
| Utili trimestrali (PEAD, D3) | 3 | chi reagisce lento alla sorpresa | SEC dal 2009 (sorpresa dalla serie storica degli utili) | BACKLOG D3 |
| Ingresso e uscita dagli indici | **2, flussi forzati** | i fondi indicizzati, che devono comprare a una data nota | appartenenza giornaliera all'S&P 500 (`sp500-data`) | **mai guardato**; il modulo 09 lo indica come classe "da capire" |

**Fuori dagli USA: i dati per le singole azioni non li abbiamo ancora.** La ricerca del 25/10 ha trovato gratis solo
i **fattori** globali (Jensen-Kelly-Pedersen, licenza non commerciale), non i prezzi dei singoli titoli. Prezzi con i
delistati fuori dagli USA: solo EODHD, in abbonamento, e il piano personale non vale per un gruppo di soci. Gli insider
europei sono pubblici (regolamento MAR, art. 19: Consob, BaFin...), ma sparsi per paese; un archivio unico gratuito
non e' noto. **Prima di allargare serve una decisione di spesa e di licenza.**

**Operazioni di Trump e dei politici (commento di Matteo, da verificare).** Cosa dicono le fonti trovate il 05/11:
- i due moduli OGE 278-T del primo trimestre 2026 riportano **3.642 operazioni** fra il 6/01 e il 30/03 (2.346
  acquisti, 1.296 vendite; altre fonti 3.711 o 4.139, non verificate), valori solo **per fasce**, obbligazioni e
  azioni insieme, depositati **in ritardo** rispetto ai 45 giorni di legge; i moduli non dicono chi ha deciso le
  operazioni ([CBS](https://cbsnews.com/news/trump-stock-trades-2026),
  [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/jim-cramer-froze-on-live-tv-after-seeing-trump39s-3700-stock-trades--here39s-what39s-in-the-president39s-portfolio-140000901.html));
- i familiari: quali obblighi di comunicazione abbiano e' **da verificare**.

Il punto che decide se e' copiabile e' il **ritardo**: copiamo quando il deposito e' pubblico, fino a 45 giorni dopo
(o piu', se in ritardo). Un vantaggio informativo a breve termine e' gia' passato; resta solo cio' che dura mesi.
**Un test dal vivo esiste gia':** l'ETF NANC copia le operazioni dei parlamentari democratici dal febbraio 2023. Ha
battuto l'S&P 500 dal lancio, ma gli analisti lo attribuiscono all'esposizione alle grandi tecnologiche, e nel 2026 e'
indietro ([24/7 Wall St](https://247wallst.com/investing/2026/05/16/nanc-traders-beat-the-crowd-by-33-points-and-the-difference-keeps-growing/),
[PortfoliosLab](https://portfolioslab.com/tools/stock-comparison/NANC/SPY)). E' esattamente la terza delle sei domande
(*stessa esposizione?*): il confronto si fa contro un portafoglio con lo stesso settore e la stessa dimensione, non
contro l'indice. Numeri di terzi: quarantena.

**Il collo di bottiglia e' la quota.** Le famiglie candidate sono almeno quattro (score, insider, politici, ingresso
negli indici). Nel 2026-Q4 resta **1** pre-registrazione sul binario hub e **0** sul binario esterno (contatore del
04/11). Per questo si parte dai conteggi di potenza (0 trial) di tutte, e si pre-registra solo quella che puo' vedere
l'effetto.

---

## 5. Lavoro del 05/11: dati, demo dei broker, ritardo

### Strato dati USA, primo pezzo (fatto)
`python data/scarica_sp500_data.py` scarica la release congelata `snapshot-2026-11` di `sp500-data` in
`data/cache/sp500data/` (fuori da git), con le impronte sha256 in `MANIFEST.json`. Il loro rapporto di verifica (03/11)
passa tutti i controlli. I nostri, sullo stesso snapshot:
- 12.294.730 righe, 1.895 ticker, prezzi dal 02/01/1968 al 30/10/2026;
- dal 1996: **498-508 membri** per giorno (dagli intervalli di appartenenza); **145 giorni-membro senza prezzo su
  3.891.816**, quasi tutti negli ultimi giorni di societa' acquisite;
- `members.parquet` ha solo 3.041 date: l'appartenenza giornaliera si prende da `membership_intervals.parquet`;
- due salti giornalieri oltre +100% su giorni-membro (HIG 05/12/2008, MRNA 19/08/2026): da confrontare con una seconda
  fonte se un test li tocca.

**Archivi SEC (Form 4 e bilanci): bloccati.** La SEC risponde 403 a un User-Agent senza contatto (05/11): la sua
politica di accesso chiede nome ed email. Serve un indirizzo da usare, deciso da Matteo.

### Demo dei broker per i dati che mancano
- **Un conto demo da' solo i titoli quotati oggi.** Per i test storici su singole azioni e' survivorship per
  costruzione: i delistati non ci sono. Quindi una demo serve per **esecuzione, costi e forward**, non per un backtest
  storico su singole azioni.
- **MT5:** la profondita' dello storico sulle demo dipende dal broker, e sul forum MQL5 ci sono casi di demo che non
  scaricano lo storico ([MQL5](https://www.mql5.com/en/forum/484936)). Le liste di azioni vanno controllate broker per
  broker.
- **Dukascopy** (gia' usato dal repo per gli indici europei): il datafeed storico e' gratuito per tutti gli strumenti
  del suo mercato ([Dukascopy](https://www.dukascopy.com/swiss/cz/marketwatch/historical)); quali azioni europee copra
  non e' documentato, e anche li' mancano i delistati.
- **Interactive Brokers, conto di prova:** lo storico via API richiede abbonamenti ai dati di un conto reale
  ([documentazione TWS](https://interactivebrokers.github.io/tws-api/historical_data.html)).
- Il resto (liste di titoli per broker, profondita' dello storico) e' nel prompt per Comet.

### Il ritardo dei depositi
- **Quiver ha lo stesso ritardo**: i dati sul Congresso li prende dai depositi previsti dallo STOCK Act (entro 45
  giorni), *"We download those disclosures, parse them for stock trades"*
  ([Quiver, pagina Congress](https://www.quiverquant.com/congresstrading/)). Non puo' toglierlo: e' il ritardo di legge.
  Per i Form 4 il ritardo di legge e' di due giorni lavorativi.
- **Si misura in due tempi.** La distribuzione del ritardo (data dell'operazione → data del deposito) si calcola **senza
  rendimenti**, a 0 trial: la tabella del Congresso su Quiver mostra le colonne "Traded" e "Filed". Quanto il ritardo
  costi richiede i rendimenti, quindi entra nella pre-registrazione come metrica principale: il rendimento anomalo fra
  operazione e deposito (non catturabile) contro quello dopo il deposito (catturabile).
- **Quiver, licenza e costo** (pagine lette il 05/11): piano Hobbyist 30 $/mese (Congresso, Trump, contratti), Trader
  75 $/mese (insider, 13F), entrambi *"for personal, non-commercial use"*; uso commerciale da 250 $/mese (Startup). Una
  societa' di trading fra soci rischia di non essere "personale": stessa questione di EODHD. Nessun download storico
  gratuito trovato. Le pagine dei termini d'uso, `/export/` e i campi dell'API non sono stati letti: Comet.

### Risultati di Comet (05/11)
- **Termini di Quiver** ([termsofservice](https://www.quiverquant.com/termsofservice/), modificati il 25/06/2026): uso
  *"personal, non-commercial"*; *"Commercial purposes do not include personal securities trading activities"*;
  ridistribuzione vietata *"to any third party, whether for commercial purposes or otherwise"*. Con il lavoro separato
  dai soci basta il piano personale (DECISIONS 2026-11-05). Il contratto di licenza dell'API e i campi degli endpoint
  **non sono stati letti**; `/export/` richiede il login.
- **Camera USA, fonte primaria gratuita:** download dei depositi per anno **dal 2008**
  ([Clerk](https://disclosures-clerk.house.gov/FinancialDisclosure/ViewReport)); i PTR sono **PDF** con *"Date of
  Transaction"* e *"Date Notified of Transaction"*: il ritardo si misura anche dalla fonte primaria, ma va estratto dai
  PDF. Senato, House/Senate Stock Watcher e le demo dei broker: **non verificati**.
- **Conseguenza:** per il Congresso e Trump, Quiver Hobbyist (30 $/mese, piano personale) evita di estrarre migliaia di
  PDF; per gli insider la fonte gratuita resta la SEC.

---

## 6. Potenza della famiglia insider, sull'S&P 500 (05/11, 0 trial)

Script: `python -m analysis.insider.potenza` (snapshot `sp500-data` 2026-11; Form 4 SEC dal 2006 Q1 al 2026 Q1,
`data/scarica_sec_form345.py`, 3.469.846 operazioni P/S). Nessun rendimento dei titoli comprati dagli insider e' stato
letto: il rumore viene da titoli **casuali** dell'indice negli stessi giorni (300 sorteggi, seme 42). Un evento =
(emittente, giorno del deposito); ingresso il giorno di borsa dopo il deposito; rendimento anomalo = titolo meno la
media equipesata dei membri; unita' indipendente = blocco di H giorni. MDE all'80% di potenza, alfa 5% a due code.
**Definizioni delle varianti provvisorie**, solo per contare.

| Variante | Eventi totali | Su membri S&P 500 | MDE a 21 giorni | MDE a 63 giorni | Ritardo mediano (90° perc.) |
|---|---|---|---|---|---|
| Tutti gli acquisti sul mercato | 272.862 | 11.090 (4%) | 0,24% | 0,39% | 2 g (4) |
| I-c ruolo (CEO/CFO/President) | 83.709 | 2.581 (3%) | 0,56% | 0,86% | 1 g (5) |
| I-b gruppo (>= 3 insider in 30 g) | 23.917 | 753 (3%) | 1,01% | 1,73% | 1 g (5) |
| I-a opportunistici (dal 2008) | 54.031 | 2.060 (4%) | 0,73% | 1,14% | 2 g (5) |

**Lettura** (numeri del 05/11, script sopra):
1. **Il ritardo dei Form 4 non e' il problema**: mediana 1-2 giorni, 90° percentile 4-5; oltre 30 giorni solo l'1-4%
   (depositi tardivi). Il problema del ritardo vale per i politici (fino a 45 giorni), non per gli insider.
2. **Il 96% degli acquisti degli insider e' fuori dall'S&P 500.** Gli insider delle grandi societa' comprano poco: sono
   le piccole e medie che fanno il campione, ed e' li' che la letteratura (non letta, quarantena) colloca l'effetto.
3. **Sull'S&P 500 le varianti strette sono deboli**: per I-a, I-b e I-c l'MDE va da 0,56% a 1,01% a 21 giorni. Se
   l'effetto nelle grandi societa' e' piu' piccolo di cosi', il test non lo vede. L'effetto atteso va **dichiarato prima**
   alla G1, dalla letteratura letta, e confrontato con queste MDE.
4. **Limite della stima**: i titoli degli insider possono essere piu' volatili della media dell'indice, quindi l'MDE vero
   e' probabilmente piu' alto. E con tre varianti il DSR conta tre trial.

**Decisione che ne esce (per Matteo):** il test che puo' vedere qualcosa e' fuori dall'S&P 500, e richiede prezzi delle
piccole e medie societa' USA con i delistati (FirstRate, una tantum; ricerca dati del 25/10 §3), con il piano personale.
In alternativa: la sola variante "tutti gli acquisti" sull'S&P 500 (MDE 0,24% a 21 giorni), che pero' e' la meno
selettiva.

---

## Decisioni di Matteo (05/11) e passi successivi

Decise (DECISIONS 2026-11-05): Polymarket solo fonte di dati; score fondamentale famiglia da testare; strato dati da
costruire; per insider e politici nessuna esclusione a priori.

Passi, in ordine:
1. **Strato dati USA point-in-time** (0 trial): prezzi e appartenenza S&P 500, bilanci SEC, Form 345, dati di Quiver
   sui politici (licenza e costo da leggere).
2. **Conteggi di potenza** (0 trial) per score, insider (tre varianti), politici, ingresso negli indici.
3. **G1** solo per le famiglie con potenza sufficiente, nei limiti della quota.
4. **Fuori dagli USA**: decisione di spesa e licenza, poi lo stesso percorso.
5. Idea 3 dell'inbox (verdetti collegati ai dati che li riaprirebbero), insieme allo "spazio di ricerca residuo".
