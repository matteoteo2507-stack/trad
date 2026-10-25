---
tipo: ricerca
stato: "fotografia del 25/10/2026; nessun acquisto fatto, decide Matteo"
aggiornato: 2026-10-25
fonte: "pagine dei fornitori e repo GitHub lette il 25/10/2026 (link per riga); prezzi del 29/09 da ricerca_X_dati_oro_2026-09-29.md dove indicato"
---
# Dati per chiudere cio' che e' in sospeso e per l'azionario (ricerca del 25/10)

> Richiesta di Matteo (25/10): quali dati servono alle cose in sospeso, se si ricavano gratis, e se no quanto costa
> comprarli **una volta** e tenerli. Seguito di [ricerca_github_2026-09-29](ricerca_github_2026-09-29.md) (GH3, dati
> gratuiti) e [ricerca_X_dati_oro_2026-09-29](ricerca_X_dati_oro_2026-09-29.md) (X1, prezzi): qui solo cio' che
> mancava. Cercato su GitHub (repo di Matteo con stella e fork compresi: `awesome-quant` ha una sezione dati) e sul web.
> **0 trial**: nessun dato scaricato, nessun esito guardato.

## 1. Cosa serve, voce per voce

| In sospeso | Dato che manca | Si chiude anche senza? |
|---|---|---|
| `trend_momentum`, A1 punto 3 | futures su commodity minori con storia lunga **fino a oggi** (strumenti indipendenti ad alta volatilita', BACKLOG G9) | si': dichiararla chiusa per potenza. E i dati da soli non bastano: vedi §5 |
| `mentor_signals` (IN REVISIONE) | nessuno | e' una decisione, non un dato |
| Debito E7, scheda dell'hub, PAC | nessuno | — |
| Azionario (perimetro dal 25/10): D2, D3, D9, G6, G8 | prezzi con i **titoli delistati** (USA e resto del mondo), fondamentali **point-in-time**, sorprese sugli utili, Form 4, per le small cap anche short interest e locate | — |

## 2. Gratis, verificato il 25/10

| Fonte | Cosa da' | Limiti | Serve a |
|---|---|---|---|
| [SEC Financial Statement Data Sets](https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets) | bilanci XBRL di tutte le societa' USA, trimestrali, **dal 2009 Q1** al 2026 Q3; ogni deposito ha `filed` e `accepted` (data e ora di accettazione, dal PDF di documentazione) → **uso point-in-time possibile**; `prevrpt` segna i depositi poi corretti | solo USA; solo i prospetti principali; dato pubblico, nessuna licenza restrittiva | G6 (fondamentali), D3: la **sorpresa sugli utili calcolata dalla serie storica degli utili** (la forma della letteratura originale sul PEAD) non richiede le stime degli analisti |
| [SEC Insider Transactions Data Sets](https://www.sec.gov/dera/data/form-345) | Form 3, 4 e 5 in tabelle, trimestrali, **dal 2006 Q1** | solo USA | D9 |
| [`edgartools`](https://github.com/dgunning/edgartools) (da `awesome-quant`) | libreria Python per XBRL, Form 4 e depositi SEC | — | lettura dei due archivi sopra |
| [`Johnbrick123/sp500-data`](https://github.com/Johnbrick123/sp500-data) | prezzi giornalieri di **tutti i membri dell'S&P 500 dal 1970**, delistati compresi (1.742 societa', 503 oggi), appartenenze giornaliere, aggiornato ogni notte; 235 MB in Parquet; controllato contro CRSP (99,990% dei giorni-membro entro 0,5 punti, dal suo README) | **nessuna licenza dichiarata**; 5 stelle; fonti miste (yfinance, che e' uno scraper non ufficiale, Tiingo, Quandl WIKI, CRSP per il pre-1996); prima del 1996 solo chiusure; il README stesso avverte sui ticker riciclati | azionario USA large cap senza survivorship. Da verificare con `core.data_checks` prima di qualsiasi uso |
| Global Factor Data, Jensen-Kelly-Pedersen ([codice](https://github.com/bkelly-lab/jkp-data), MIT) | rendimenti di **153 fattori in 93 paesi** (README del pacchetto, letto via motore di ricerca) | dati sotto licenza **CC BY-NC 4.0 (non commerciale)**: da chiarire se una societa' di trading fra soci e' uso commerciale | test di **classe** sull'azionario globale senza comprare prezzi di singoli titoli |
| Open Source Asset Pricing, Chen-Zimmermann ([sito](https://www.openassetpricing.com/), [codice](https://github.com/OpenSourceAP/CrossSection) GPL-2.0, 1.070 stelle) | segnali e portafogli di centinaia di anomalie USA replicate; ultimo aggiornamento dei dati ottobre 2025, portafogli fino a fine 2023 | USA; alcuni segnali a livello di titolo si ricostruiscono solo con CRSP/Compustat | come sopra, per gli USA |
| pysystemtrade (gia' in GH3) | 252 futures continui | **fermi al 2024-03-28** (ultima riga di CORN e GOLD, letta il 25/10; i commit successivi non hanno allungato i prezzi) | A1, vedi §5 |

**Scartati:** TurtleTrader (32 mercati maggiori, file "non aggiornati", ridistribuzione solo con permesso); Stooq
(nessuna conferma che i file in blocco contengano i delistati); Tiingo come fonte unica (copertura dei delistati
sul piano gratuito non documentata; e' una delle fonti di `sp500-data`).

## 3. A pagamento: cosa resta tuo dopo l'acquisto

| Fornitore | Cosa | Prezzo | Resta dopo? | Gruppo di soci |
|---|---|---|---|---|
| [Pinnacle CLC](https://pinnacledata2.com/clc.html) | **98 commodity** continue, le piu' vecchie dal 1969, fino all'ultima chiusura; OHLC, settlement, open interest, volume | **99 $** (letto il 25/10); aggiornamenti facoltativi 20 $/mese con minimo 3 mesi, o 18 $/mese per un anno | probabile: lo storico e' nel prezzo, gli aggiornamenti sono un servizio a parte. La pagina non lo dice in modo esplicito: **chiedere prima di pagare** | licenza da verificare |
| [FirstRate Data, Stocks Complete](https://firstratedata.com/b/22/stock-complete-historical-intraday) | **9.329 azioni USA + oltre 7.000 delistate**, gen 2000 → ott 2026, da 1 minuto a 1 giorno, rettificate e non | **non mostrato** sulla pagina (solo al pagamento); un sito di confronto dice ~500 $ una tantum, **non verificato**; aggiornamenti 59,95 $/mese dopo il primo mese | **si'**: *"once downloaded, the data is yours to use forever"* ([licenza](https://firstratedata.com/about/license)) | licenze multiutente per uso interno; i dati grezzi non si ridistribuiscono, i lavori derivati si' |
| [EODHD](https://eodhd.com/pricing) | EOD di tutte le borse del mondo, 30+ anni; elenca i delistati per borsa (60.191 USA, 9.587 Francoforte, 4.077 Londra a settembre 2026: dalla documentazione citata da un motore di ricerca, pagina originale non raggiungibile) | Historian **19,99 €/mese** o 199,90 €/anno (piano personale, letto il 25/10) | **non detto** nelle condizioni | **no** col piano personale: *"On behalf of a group, organization"* rende l'utente commerciale ([condizioni](https://eodhd.com/financial-apis/terms-conditions)); piano commerciale a prezzo non pubblico |
| Norgate (gia' in X1) | azioni USA senza survivorship, futures | 270-787,50 $/anno (29/09) | **no**: alla scadenza *"all rights and capabilities to access and use the associated data shall immediately cease"* ([termini via motore di ricerca](https://norgatedata.com/faq.php)) | — |
| Sharadar, Databento, Kibot, Tick Data | gia' in X1 (29/09) | — | — | — |

## 4. Due vincoli che valgono per tutti

1. **Il repo e' pubblico.** Nessun dato comprato entra in git: ogni licenza letta vieta la ridistribuzione. Resta
   sul disco in una cartella esclusa da git (come `data/cache/` e `analysis/trading-bot-eval/data/`). In git vanno
   solo codice, risultati e i dati pubblici della SEC.
2. **Quattro soci non sono un uso personale.** EODHD lo dice esplicitamente; FirstRate prevede licenze multiutente;
   per Pinnacle e' da chiedere. Comprare con un piano personale e condividere viola le condizioni.

## 5. Cosa dicono questi dati sulle cose in sospeso

- **A1 (`trend_momentum`).** Il conteggio del 03/10 ([referto A1](../TREND_A1_HELDOUT_POWER.md) §8): con futures,
  crypto e azioni il braccio ad alta volatilita' arriva a 7,8-10,9 strumenti indipendenti. Basta per lo scenario
  ottimistico (7,3), non per quello di pianificazione onesta (29,3). **Pinnacle a 99 $ porta i futures a oggi, ma non
  cambia quel conto**; le azioni aggiungono poco perche' si muovono insieme (tetto 3,1). In piu', dei futures contati
  sul broker attuale ci sono solo mais e grano: un risultato positivo direbbe che il gradiente esiste, non che lo
  possiamo operare. **Strada gratuita da valutare prima di pagare:** i futures di pysystemtrade arrivano al 28/03/2024;
  la finestra di A1 parte dal 2017-12-26, quindi avrebbe circa 6,3 anni invece di 8,8. La potenza dipende
  soprattutto dal numero di strumenti, non dagli anni: se il calcolo regge sulla finestra corta, i 99 $ non servono.
  Va rifatto (0 trial) prima di decidere.
  ✅ **Fatto la sera stessa** ([referto A1 §9](../TREND_A1_HELDOUT_POWER.md)): con i futures gratuiti in una finestra
  lunga lo scenario ottimistico e' finanziabile, quello onesto no con nessun dato. **Per A1 non si compra.**
- **Azionario.** Per cominciare non serve comprare nulla: fondamentali USA point-in-time (dal 2009), Form 4 (dal
  2006), S&P 500 senza survivorship (dal 1970) e fattori globali sono gratis. Si paga solo per **small cap USA**
  (FirstRate, una tantum) o per **singoli titoli fuori dagli USA con i delistati** (trovato solo EODHD, in
  abbonamento, con la questione della licenza di gruppo aperta).

## 6. Da decidere (Matteo)

1. **A1:** ✅ calcolo fatto (referto A1 §9): Pinnacle non serve. Resta la decisione del
   03/10: pre-registrare sullo scenario ottimistico, dichiarando prima che un nullo vale "non dimostrato".
2. **Azionario:** partire con le fonti gratuite del §2, e comprare (FirstRate o EODHD) solo quando un test
   pre-registrabile lo chiede (BACKLOG §G, regola per comprare), oppure comprare subito un archivio ampio? La seconda
   strada cambia la regola: va scritta come tale.
3. **Licenze:** chi compra, a nome di chi, e con quale licenza per quattro persone.
4. **Universita':** ✅ esclusa da Matteo (25/10): le licenze accademiche scadono, e serve un dato **di proprieta'** su
   cui lavorare negli anni.
5. **Chi compra dipende da chi usera' i dati** (Matteo, 25/10): le strategie le sviluppa soprattutto il socio
   principale, quindi l'acquisto (e la licenza) si decide con lui.

**Non verificato:** prezzo di FirstRate al pagamento; tenuta dello storico Pinnacle senza aggiornamenti; licenza di
`sp500-data`; licenza dei dati Chen-Zimmermann; se un uso fra soci e' "commerciale" per la licenza CC BY-NC di JKP.

## 7. Per l'hub (registro delle previsioni)

[`Jon-Becker/prediction-market-analysis`](https://github.com/Jon-Becker/prediction-market-analysis) (fra le stelle di
Matteo; MIT, 3.903 stelle): dichiara il piu' grande dataset pubblico di mercati Polymarket e Kalshi. Candidato, con
World Monitor, per il "riferimento" del registro.
