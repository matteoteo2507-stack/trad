---
tipo: analisi
stato: "quarantena (proposta: NON DIMOSTRATO, chiuso all'intake a 0 trial; decide Matteo)"
aggiornato: 2026-10-11
fonte_dati: "pacchetto del socio dell'11/10/2026: testi in fondamenti_tecnici/_sorgenti/vtob_socio_2026-10-11/, barre e risultati in materiale_socio/vtob_dati_risultati_2022-07_2026-10/ (fuori da git)"
misure: "analysis/vtob_intake/descrittivi.py, lanciato l'11/10/2026; ogni numero 'misurato' di questa nota viene da li'"
---
# Pacchetto "VTOB" del socio (order block su XAUUSD): intake

> Seguito di [indicatore_ob_bigbeluga_intake_2026-10-09](indicatore_ob_bigbeluga_intake_2026-10-09.md). Il 09/10
> l'indicatore non aveva stop ne' uscite e la nota diceva: *se il socio torna con regole e operazioni registrate si
> riparte dal §4*. L'11/10 e' tornato con le **regole complete** e con un **backtest**, non con operazioni registrate.
> Letto tutto il pacchetto, codice compreso. **0 trial**: nessuna variante provata, nessun ingresso simulato, nessun
> baseline casuale. I numeri "dichiarati" sono del socio; i numeri "misurati" escono da
> [`analysis/vtob_intake/descrittivi.py`](../../analysis/vtob_intake/descrittivi.py) sui suoi file.

## 1. Cosa e' arrivato

Quattro strategie con la **stessa regola** e parametri diversi, tutte su XAUUSD:

1. Filtro di tendenza: il Supertrend modificato dell'indicatore (banda a 3,5 volte l'ampiezza media di 50 barre).
2. Zona ("order block"): a un minimo di swing confermato, in tendenza rialzista, la zona parte dal corpo della barra e
   scende di un'ampiezza media. Vale solo se la tendenza dura da almeno N barre, se la zona sta sopra la linea di
   tendenza e se il prezzo e' sopra la media esponenziale a 200 di un timeframe superiore.
3. Segnale: a barra chiusa, il minimo torna sopra il bordo alto della zona. Ingresso **a mercato all'apertura della
   barra dopo**. Un solo trade per zona, una posizione alla volta.
4. Uscita: stop a k volte l'ampiezza media, obiettivo a 3 o 4 R, stop a pareggio (+0,1 R) dopo +1 R.

| | TF | lato | stop | obiettivo | dichiarato dal socio (lug 2022 – ott 2026; D da mag 2025) |
|---|---|---|---|---|---|
| A | M15 | solo long | 6× | 3 R | 199 trade, +83 R |
| B | H1 | long e short | 3× | 4 R | 109 trade, +70 R |
| C | M30 | long e short | 8× | 3 R | 116 trade, +44 R |
| D | M5 | solo long | 6× | 4 R | 117 trade, +42 R |

Parametri completi e risultati dichiarati: `_sorgenti/vtob_socio_2026-10-11/docs/PORTAFOGLIO_VTOB.md`. Il socio dichiara
di aver scelto queste quattro fra **46.080 varianti** (`LEGGIMI.md`, Avvertenze), e avverte lui stesso che dal vivo si
aspetta meno.

Nel pacchetto ci sono anche due prompt e una specifica scritti **per un assistente AI** ("rendila operativa", "trova la
strategia piu' profittevole, itera finche'..."). Li abbiamo letti come materiale, non eseguiti: il secondo chiede una
ricerca di massa, che il nostro protocollo rifiuta (DECISIONS 2026-08-17).

## 2. Cosa regge (verificato l'11/10)

- **I numeri si riproducono.** Rilanciando il codice del socio sui suoi dati, i trade delle quattro strategie sono
  identici a quelli consegnati (199, 109, 116, 117).
- **I dati sono veri.** `core/data_checks.py` a posto (monotonia, duplicati). Le chiusure M15 coincidono con il nostro
  Dukascopy: scarto mediano 0,105 $ su 52 mesi, mese peggiore 0,315 $.
- **Nessun look-ahead trovato** leggendo `vtob_bt.py` e `vtob_v2.py` riga per riga: il pivot si usa dalla barra di
  conferma, il segnale e' a barra chiusa, la media del timeframe superiore e' quella dell'ultima barra chiusa, lo stop
  si controlla prima dell'obiettivo, una barra che apre oltre lo stop esce all'apertura, il pareggio vale dalla barra
  dopo.
- **I fill sono ottenibili per costruzione** (QUANT_REVIEW_PROTOCOL Step 3bis): l'ingresso e' a mercato all'apertura
  successiva, non c'e' un livello da raggiungere. E' la differenza dal FADE.
- **I vicini reggono dentro la griglia**: per ognuna delle quattro scelte, le 11 varianti a un parametro di distanza
  sono tutte positive. Non e' una conferma indipendente: condividono quasi tutti i segnali.

## 3. Cosa non regge

### 3.1 La colonna dello spread cambia unita' a meta' file (errore nei costi)

Misurato: lo spread mediano e' 130 punti fino a venerdi' 17/10/2025 e **13 punti da lunedi' 20/10/2025**. Prima di quel
giorno il 99,5% dei valori e' un multiplo di 10, dopo il 9,5%; i prezzi hanno sempre due decimali. Lettura: fino al
17/10/2025 il simbolo era quotato in millesimi (130 punti = 0,13 $), dopo in centesimi (13 punti = 0,13 $). Il motore
del socio moltiplica sempre per 0,01 (`vtob_bt.py:32`), quindi **prima del 20/10/2025 addebita uno spread dieci volte
piu' alto del vero** (1,2–1,6 $ contro 0,12–0,16 $). Il nostro Dukascopy, che e' piu' largo di un conto raw, ha
0,33–0,58 $ negli stessi anni: 1,5 $ non e' plausibile. ⚠️ E' un'inferenza dai file: la conferma e' la specifica del
simbolo (campo Digits) sul terminale del socio.

Due conseguenze, di segno opposto:

- **I R consegnati sono un po' sottostimati.** Gli ingressi non dipendono dallo spread, quindi la correzione e'
  esatta: A da 82,9 a 96,1 R; A+B+C da 197,1 a 221,9 R. Un numero peggiore non e' per forza onesto.
- **La ricerca e' stata fatta con i costi sbagliati per il 77% del campione** (dal 12/07/2022 al 17/10/2025). Su M15, nel primo periodo le varianti
  positive sono il 3% con stop 3×, il 12% con 4×, il 43% con 6× e il 51% con 8×; nel secondo periodo, dove l'errore
  quasi non c'e', sono il **92% a ogni stop**. La lezione del socio *"con stop stretti lo spread mangia tutto"* e'
  coerente con l'errore di unita', non per forza con il mercato. La graduatoria delle 46.080 varianti andrebbe
  rifatta, e sarebbe un'altra ricerca.

### 3.2 Costi che mancano

Niente swap, commissioni e slippage nel motore Python. Lo swap pesa perche' le posizioni restano aperte: notti medie in
posizione 2,4 (A), 3,3 (B), **9,3 (C)**, 1,2 (D). ⚠️ Stima d'ordine di grandezza, con un finanziamento **ipotetico** del
6% annuo sul long: circa 0,05 R a trade per A, 0,07 per B, 0,10 per C (su medie di 0,42, 0,64 e 0,38 R). Il numero vero
e' lo swap long del conto del socio: da chiedere.

### 3.3 Il "periodo di verifica" non e' un fuori campione

Il socio ha scelto le configurazioni *"buone in entrambi i periodi"* (`LEGGIMI.md`, riga 83): il secondo periodo e'
stato usato per scegliere, quindi e' diventato train (STRATEGY_LIFECYCLE §2). E non discrimina: nel secondo periodo
(da luglio 2025) e' positivo il **92%** delle varianti M15, il 93% delle H1, l'83% delle M30. Su M5 scegliere sul primo
periodo va peggio che non scegliere: correlazione fra i due periodi −0,45, e il migliore 1% del primo periodo ha una
mediana di −0,8 R nel secondo contro +1,7 R di tutte.

### 3.4 Quasi tutto il guadagno e' long, in un mercato salito del 142%

- A+B+C: **187,0 R su 197,1 vengono dai long** (380 trade). Gli short sono 44 e fanno +10,2 R: 8 trade di B (+13,5) e
  36 di C (−3,3).
- Nelle griglie, aggiungere gli short a parita' di parametri peggiora nel **96%** dei casi su M15 (mediana −21 R) e nel
  92% su M30. Se la zona fosse un livello a cui il prezzo reagisce, dovrebbe reggere anche da sopra.
- Quando l'oro ha smesso di salire: sugli ingressi dal 01/02/2026 (oro da 4.741 a 4.195 nel file del socio) i long
  fanno **−6,8 R** e il totale −0,3 R su 51 trade. Campione piccolo (MDE 0,56 R): e' coerente con la lettura, non la
  dimostra.

### 3.5 Quanto spiega la sola salita dell'oro

Stima in forma chiusa: un prezzo che sale con la deriva media dell'oro nel file, senza nessun segnale, sotto la stessa
uscita (stop, obiettivo, pareggio).

| | media lorda osservata | sola deriva (media del file / dell'anno) | scarto | MDE a un test |
|---|---|---|---|---|
| A | 0,491 R | 0,100 / 0,147 | 0,39 / 0,34 | 0,32 |
| B | 0,716 R | 0,109 / 0,152 | 0,61 / 0,56 | 0,55 |
| C | 0,423 R | 0,088 / 0,165 | 0,34 / 0,26 | 0,42 |
| D | 0,408 R | 0,085 / 0,098 | 0,32 / 0,31 | 0,50 |

La deriva spiega fra 42 e 65 R dei 225 lordi di A+B+C: **una parte, non tutto**. Lo scarto che resta sta attorno
all'effetto minimo che questi campioni sanno vedere **con un solo test**; ma i test sono stati decine di migliaia
(§3.6). ⚠️ Non e' un baseline: la formula usa una deriva costante e non copia lo stato in cui la regola entra (tendenza
rialzista avviata, prezzo sopra la media a 200). Se in quello stato l'oro sale piu' della media, la parte spiegata
cresce. Quel confronto e' il test vero (§6, strada B).

### 3.6 La selezione

Lo Sharpe per trade delle quattro scelte contro la soglia di futilita' di `core/trial_ledger.py` (il minimo sotto cui
un risultato non si distingue dal migliore di N prove di rumore; e' un pavimento):

| | Sharpe per trade | soglia a 100 prove | a 46.080 | resta sopra solo se le prove indipendenti sono meno di |
|---|---|---|---|---|
| A | 0,257 | 0,296 | 0,416 | 24 |
| B | 0,316 | 0,401 | 0,562 | 12 |
| C | 0,237 | 0,388 | 0,545 | 4 |
| D | 0,186 | 0,387 | 0,543 | 2 |
| A+B+C | 0,268 | 0,203 | 0,285 | n = 424 trade sovrapposti: non confrontabile |

Le 46.080 varianti sono molto correlate fra loro, quindi le prove davvero indipendenti sono meno; quante, dalle griglie
non si ricava. Ma 46.080 e' un minimo: prima della griglia ci sono stati altri giri non contati (conferma del pivot da
7 a 3 barre, stop da 4× a 6×, obiettivo da 2 a 3 R, cinque filtri provati e due scartati, varianti d'ingresso;
`PROMPT_ClaudeCode_StrategiaMigliore.md`, "cosa ha funzionato / non ha funzionato"). Il "DD Monte Carlo al 95%" del
socio rimescola i trade: misura il percorso, non la selezione (04_quant_metodologia §2b).

### 3.7 Tre strategie, un'idea

A, B e C sono la stessa regola sullo stesso strumento: correlazione dei R mensili 0,42–0,51 su 52 mesi, fino a 3
posizioni aperte insieme. Il portafoglio non e' diversificazione: e' la stessa scommessa con fino a 3 R di rischio.

### 3.8 Provenienza e stato operativo

- La ricerca e' stata condotta con un assistente AI su dati quasi tutti precedenti al suo cutoff, e "long sull'oro nel
  2024-25" e' un regime famoso (gatekeeper, checklist 5): vale solo il forward.
- L'EA e le strategy Pine **non sono mai stati compilati** (`LEGGIMI.md`, riga 106). L'EA ricalcola tutto sulle ultime
  3.000 barre a ogni barra nuova: che dia gli stessi segnali del Python e' dichiarato, non verificato.
- Licenza dell'indicatore di partenza: CC BY-NC-SA 4.0, uso non commerciale (nota del 09/10, §6).

## 4. I claim del socio, con stato

| claim | stato | perche' |
|---|---|---|
| "senza lookahead" | verificato | lettura del codice, §2 |
| "spread reale del broker" | falsificato fino al 17/10/2025 | unita' sbagliata di 10 volte, §3.1 |
| 199 trade, +83 R (A) e gli altri totali | verificato come conto, quarantena come vantaggio | si riproducono; non dicono se la regola batte il caso |
| "positiva nel periodo di scelta e in quello di verifica" | vero, non informativo | lo e' il 92% delle varianti M15, §3.3 |
| "resta buona cambiando i parametri vicini" | verificato dentro la griglia | 11 su 11, ma stessi segnali |
| "tutti gli anni positivi" | vero sul campione | long su un mercato salito in 4 anni su 5; e' anche uno dei campanelli del gatekeeper |
| rendimenti mensili in % | quarantena | sono il binario composto, non il binario 1R su cui si da' il verdetto (§4quater) |
| "dal vivo aspettati PF intorno a 1,5" | non falsificabile oggi | nessuna base nel pacchetto |

## 5. Famiglia

Stessa grandezza gia' vista il 09/10: ritorno su una zona da pivot nella direzione della tendenza. E' la grandezza di
`livelli` (CLOSED, 384 trial, nessun livello batte il caso) e di `nxt` (KILL); il filtro di tendenza la apparenta a
`trend_momentum`. Per la regola dell'08/10 **non e' una famiglia nuova**. Un backtest del socio, scelto fra 46.080
varianti, non e' l'evidenza esterna che §7 chiede per riaprire: e' una statistica dichiarata (§8). Nessun "chi paga".
Le pre-registrazioni esterne del 2026-Q4 sono 3 su 2-3 (`python -m core.trial_ledger`, 11/10).

## 6. Verdetto proposto: NON DIMOSTRATO, chiuso all'intake a 0 trial (decide Matteo)

**Non e' refutato.** Il codice e' pulito e i numeri sono veri come conto; quello che manca e' una misura che separi la
regola dalla salita dell'oro e dalla selezione. Con questi dati non si puo' fare: sono stati attraversati almeno 46.080
volte.

Due strade, da scegliere:

- **A (consigliata): chiudere all'intake.** Si restituiscono al socio i rilievi del §7. Se vuole usare l'EA in demo,
  la soglia si scrive **prima**: per vedere l'effetto dichiarato per intero (0,465 R a trade) servono 109 trade
  indipendenti, circa 57 settimane al suo ritmo di 1,9 a settimana; per vederne la meta', 438. Gli "1-2 mesi in demo"
  del pacchetto sono 8-16 trade, MDE 1,21 R: non possono dire niente, ne' a favore ne' contro.
- **B: un solo test pre-registrato.** Specifiche congelate come consegnate, contro ingressi casuali con stessa uscita,
  stesso lato, stesso anno e **stesso stato dei filtri** (`core/random_baseline.py`): e' l'ablazione della zona
  (§4bis), cioe' "la zona aggiunge qualcosa al solo stare long in tendenza?". Costa 1 trial della famiglia `livelli`,
  che e' CLOSED (serve una decisione esplicita su §7), e uno slot esterno che nel 2026-Q4 non c'e'. Dati che il socio
  non ha toccato: oro prima del 12/07/2022 (Dukascopy M1 dal 01/09/2020: 97 settimane, oro da 1.968 a 1.725, quindi
  senza deriva a favore). ⚠️ Potenza al limite: circa 85 trade attesi per A, MDE circa 0,5 R contro 0,42-0,49
  dichiarati. Da dichiarare prima cosa significherebbe un mancato rifiuto.

**Cosa lo riaprirebbe dopo una chiusura**: un registro forward del socio (demo o reale) con il numero di trade
dichiarato prima; oppure la strada B decisa da Matteo.

## 7. Cosa dire al socio

1. **Unita' dello spread**: controllare Digits di XAUUSD sul terminale e la data del cambio. Finche' non e' corretta,
   ogni confronto fra stop stretti e larghi nelle sue griglie e' falsato.
2. **Swap**: quanto paga il long per notte sul suo conto. C tiene la posizione 9 notti in media.
3. **Compilare e provare l'EA** nel tester MT5 prima di qualunque demo, e confrontare i segnali con i 199 del Python.
4. **Rifare la griglia non risolve**: dopo la correzione sarebbero altre 46.080 prove sugli stessi dati.
5. Restano aperte le domande del 09/10 (§5): quante altre prove ci sono state prima della griglia.
6. La licenza non permette l'uso commerciale (canale di segnali a pagamento, vendita dell'EA).

## Collegamenti

- [indicatore_ob_bigbeluga_intake_2026-10-09](indicatore_ob_bigbeluga_intake_2026-10-09.md): l'indicatore di partenza.
- [STRATEGY_LIFECYCLE](../STRATEGY_LIFECYCLE.md) §2, §3, §4bis, §7, §8; [QUANT_REVIEW_PROTOCOL](../QUANT_REVIEW_PROTOCOL.md) Step 3bis.
- [_INTAKE](../../fondamenti_tecnici/_INTAKE.md), [materiale_socio](../../materiale_socio/README.md).
