# Financial Freedom 101 — scheda del canale e dei video letti

> **Stato: quarantena.** Primo blocco di 5 video letto il 2026-10-25 (§10, regola di arresto in §11). Due video letti per intero il 2026-10-13, uno alla volta, dalle copie in `_raw/_lettura/`;
> `rule_extract.py` passato dopo la lettura, nessun passaggio sfuggito. Canale elencato (solo titoli), nessuna
> trascrizione scaricata in blocco. **Zero strategie, zero pre-registrazioni, 0 trial. Il PAC non cambia.**
> Conti rifatti con [`analysis/pac_intake/verifiche_ff101.py`](../../../../analysis/pac_intake/verifiche_ff101.py)
> (eseguito il 2026-10-13): ogni numero "nostro" di questa scheda viene da lì.

## 1. Che fonte è

Canale YouTube `@financial_freedom101`: 253 video, 40,8 ore (elenco del 2026-10-13). Un ingegnere dipendente
statunitense racconta come è passato da un debito di studio a un patrimonio sopra il milione di dollari in circa
quindici anni, e pubblica ogni una o due settimane un aggiornamento sull'economia USA.

- **Di cosa vive il canale** (dichiarato nel video 1): pubblicità di YouTube e affiliazione Amazon. Nei due video letti
  non vende corsi, segnali o prodotti. Da ricontrollare sul resto del canale.
- **Cosa lo distingue**: mostra i propri numeri anno per anno, comprese le perdite e gli errori (la vendita del 2022,
  l'azienda agricola in perdita, il canale a zero entrate per anni).
- **Cosa non è**: non è una fonte di rendimenti. Il patrimonio è autodichiarato, è un caso solo, è un sopravvissuto
  (non vediamo chi ha fatto lo stesso senza riuscirci) e copre il 2009-2025, uno dei periodi migliori della storia
  dell'azionario USA (§4).

## 2. Era già nel repo, senza nome

Il blocco 4 di `_sorgenti/Appunti misti 2026-08-04.txt` ("Economic and Financial Outlook Update - August 4, 2026",
registrato come "video divulgativo") è il video **`2YqkjSxXA7U`** di questo canale, *Economic Update 04 Aug 2026*.
Attribuito il 13/10 per contenuto e durata:

- gli appunti arrivano al minuto 15:38, il video dura 15 minuti;
- coincidono alla lettera con il video 2: fondo d'emergenza di 6 mesi giustificato dal quarto di disoccupati oltre i
  6 mesi, denaro che serve entro 5 anni in conti garantiti, 70-80% S&P 500 + 10-20% internazionale + 0-10% obbligazioni
  secondo l'attesa sui tassi, metalli (oro, argento, alluminio, acciaio) che nel video 1 dichiara di possedere.

**Conseguenze.**
- L'allocazione 70-80% S&P 500, rifiutata il 04/08 e ritrovata oggi, è **una occorrenza di una fonte sola**, non due
  conferme ([[feedback_conferme_per_fonte]]).
- Gli altri tre blocchi di quel file (decenni persi, valutazione del rischio, MMT) sono video diversi e nessun titolo
  del canale li richiama: restano senza autore. La frase "la fonte si auto-contraddice" scritta il 04/08 dava per
  scontato un autore unico: corretta in `08_asset_allocation_passiva` e in `_INTAKE.md`. Il rifiuto dell'allocazione
  regge da solo (concentrazione su un paese).
- Il titolo del riassunto era del riassuntore, non del video: è la regola già scritta per Quant Guild (un blocco
  orfano si cerca per contenuto su tutto il canale).

## 3. Video 1 — *Living Paycheck to Paycheck to Millionaire*

`9MuAacOIAv4` · 27 min · 4.369 parole · il più recente di almeno quattro versioni della stessa storia sul canale
(#48, #103, #134 dell'elenco: non lette).

**Cosa contiene.** Una tabella anno per anno, 2009-2026: rendimento dell'S&P 500, versamenti dell'anno, patrimonio,
scelte di vita. Poi dieci lezioni.

**Il percorso, in breve (tutto dichiarato dalla fonte).** Parte nel 2009 con un patrimonio negativo e tre lavori.
Primo impiego stabile nel 2010. Estingue prima i debiti a tasso alto, poi il prestito di studio (2012). Versa nel
piano pensionistico aziendale la quota minima che fa scattare il contributo del datore, poi la alza: 4% → 6% → 10% →
12% → 14% → 16% in sette anni. Il datore aggiunge l'11%. Compra una casa sotto il prezzo di zona e la ristruttura da
sé; la rivende nel 2017. Nel 2022 vende azioni per 200 mila dollari, all'inizio del ribasso, per comprarne un'altra.
Supera il milione a giugno 2024.

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 1.1 | Patrimonio da −45 mila (2009) a 1,29 milioni (inizio 2026) | non falsificabile | Autodichiarato. **Coerente al suo interno**: i versamenti dichiarati, investiti ai rendimenti che lui stesso elenca e tolte le due vendite, danno 834 mila contro 892 mila dichiarati fra piano aziendale, azioni e conti pensione (§4). Non è una verifica dei dati |
| 1.2 | Rendimenti annui dell'S&P 500 elencati | verificato (ordine di grandezza) | Sui nostri dati di solo prezzo, 12 anni dal 2013: il dichiarato sta in media 1,3 punti sopra (da −0,5 a +3,1), cioè circa i dividendi. Lui stesso avverte che le fonti differiscono sui dividendi |
| 1.3 | In vent'anni l'S&P 500 ha battuto oltre il 90% dei fondi a gestione attiva | verificabile | Vedi 2.1 |
| 1.4 | A ogni aumento di stipendio, una parte dell'aumento va nei versamenti prima di abituarsi a spenderla | verificabile | È il meccanismo "Save More Tomorrow" (Thaler e Benartzi 2004): chi aderì passò dal 3,5% al 13,6% del reddito al quarto aumento. Evidenza causale giudicata **bassa** dal registro del Dipartimento del Lavoro USA: chi aderisce si è scelto da solo. Conflitto con il nostro piano in §6 |
| 1.5 | Prima il contributo del datore, poi tutto il resto ("non volevo perdere il 4%") | verificabile | Vale per il sistema USA. Domanda italiana in §7 |
| 1.6 | Vendere 200 mila di azioni a inizio 2022 per la casa è costato circa 30 mila ("non potevo aspettare") | non falsificabile | Autodichiarato. È il caso concreto dei **due secchi**: denaro con una data d'uso non sta in azioni. Lo conferma lui stesso nel video 2 (regola dei 5 anni) |
| 1.7 | Circa metà delle attività chiude entro 5 anni: parti sapendo che fallirà e spendi poco all'inizio (forno avviato con 4 mila dollari affittando ore in forni altrui) | verificabile | La statistica non è stata controllata. La regola è la nostra "potenza prima di raccogliere" applicata a un'impresa: comprare la risposta al prezzo più basso |
| 1.8 | "Le notizie vendono paura: guarda la Fed, non le notizie" | non falsificabile | Per il PAC non serve né l'una né l'altra: il §0 non rivede le prospettive di mercato |
| 1.9 | "Non chiedere consigli finanziari a chi è al verde: trova chi ha fatto ciò che vuoi fare" | non falsificabile | Regola di selezione delle fonti che **seleziona sopravvissuti**: chi ha ottenuto il risultato non distingue il metodo dalla fortuna del periodo |
| 1.10 | Impara le norme fiscali: casa venduta senza imposte, conti a esenzione futura, conto del coniuge, conversione | verificabile | Norme USA. Mappa in §7 |

**Che cosa ha prodotto il risultato** (nostra lettura dei suoi numeri, §4): reddito salito di circa quattro volte in
quindici anni, contributo del datore dell'11%, risparmio complessivo intorno a un quarto del reddito negli anni in
cui entrambi i dati sono dichiarati (12% nel 2011, 26% nel 2016, 27% nel 2018, contributo del datore compreso), e un
mercato che ha reso il 13,6% l'anno. La scelta dei titoli non c'entra: quasi tutto è indice.

## 4. Conti rifatti (2026-10-13)

**Coerenza del video 1.** Versamenti dichiarati 2010-2025: 513 mila dollari, contributo del datore compreso; il 2012
è ambiguo nella trascrizione ed è letto come 25 mila. Vendite per le due case: 225 mila. I versamenti sono il **40%**
del patrimonio dichiarato.

**Quanto pesa il periodo.** Gli stessi versamenti e le stesse vendite, a rendimento costante:

| Rendimento annuo | Investito a inizio 2026 (migliaia di dollari) |
|---|---|
| quello dichiarato (13,6% composto) | 834 |
| 10% | 578 |
| 7% | 463 |
| 5% | 402 |
| 0% | 288 |

Con un rendimento "normale" del 7% avrebbe poco più della metà. **La storia insegna l'ordine delle operazioni e la
costanza, non quanto ci si può aspettare.** Per le attese resta la regola del modulo 08: rendimento reale del 3-4%.

**Commissioni (video 2).** I suoi numeri tornano tutti: 300 dollari al mese per 40 anni danno 1.047 mila all'8%
reale, 787 mila con l'1% di costo (−24,8%), 597 mila con il 2% (−43,0%). L'8% reale è un'ipotesi alta e vale per i
soli USA, ma **la quota persa dipende poco dal rendimento ipotizzato**. Lo stesso conto con i costi del nostro PAC
(OCF 0,14% e bollo 0,20%, da [INVESTING_PILLAR_PLAN §0](../../../../docs/INVESTING_PILLAR_PLAN.md)):

| Rendimento reale | OCF | bollo | OCF + bollo | per confronto: 1% |
|---|---|---|---|---|
| 8% | −4,0% | −5,6% | −9,3% | −24,8% |
| 5% | −3,6% | −5,1% | −8,4% | −22,5% |

Su 40 anni i nostri costi tolgono circa l'8-9% del capitale finale; più di metà è il bollo, che è una tassa.

**Giorni migliori (video 2).** S&P 500, solo prezzo, 16/01/2012 → 13/08/2026 (3.781 sedute, 14,6 anni, dati
Dukascopy). Sempre investito: ×6,02.

| Giorni tolti | senza i migliori | senza i peggiori | senza entrambi | migliori entro 10 sedute da un peggiore |
|---|---|---|---|---|
| 10 | ×3,19 | ×11,05 | ×5,85 | 5 su 10 |
| 20 | ×2,26 | ×16,45 | ×6,17 | 12 su 20 |
| 60 | ×0,83 | ×53,70 | ×7,42 | 35 su 60 |

I suoi numeri reggono nell'ordine di grandezza (senza i 10 migliori si perde il 56% dei guadagni, senza i 20 il 75%),
e regge la sua premessa: i giorni migliori seguono i peggiori. Proprio per questo **la statistica non dice nulla sul
tempismo in generale**: non si possono saltare gli uni senza saltare gli altri, e togliendoli entrambi il risultato
non cambia. Misura un'altra cosa, che è quella che lui intende: **chi vende dopo il crollo ha già preso i giorni
peggiori e perde i migliori**. È il costo di vendere per paura.

## 5. Video 2 — *The Secret To Beating The Majority Of Investors*

`HBCGczqLGNY` · 16 min · 2.976 parole.

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 2.1 | Meno del 10% dei fondi gestiti batte l'indice in vent'anni | verificabile | SPIVA USA, fine 2025: il **79%** dei fondi attivi a grande capitalizzazione è rimasto sotto l'S&P 500 nell'anno (dato ufficiale). A 20 anni due fonti secondarie concordano sul **92-93%**. Il PDF ufficiale risponde 403: va letto con Comet. Per noi conta di più SPIVA Europa: nel 2025 il **71%** dei fondi azionari globali in euro è rimasto sotto l'S&P World; il dato a 10 anni di quella categoria non è stato trovato |
| 2.2 | L'1% di costo toglie un quarto del capitale in 40 anni, il 2% il 43% | verificato | §4 |
| 2.3 | Senza i 10 giorni migliori si perde oltre metà dei guadagni; senza 20 il 75%; senza 60 si è in perdita del 60% | verificato (ordine di grandezza), **argomento unilaterale** | §4. L'ultimo numero dipende dalla finestra: sui nostri dati senza 60 giorni si resta a ×0,83 |
| 2.4 | Versamento fisso a ogni stipendio, automatico, dividendi reinvestiti | — | È il nostro §0 |
| 2.5 | Ordine: debito a tasso alto → 1.000 dollari d'emergenza, poi 6 mesi → denaro che serve entro 5 anni in conti garantiti → il resto investito | verificabile | I 6 mesi poggiano sullo stesso dato del 04/08 (un quarto dei disoccupati oltre i 6 mesi): una fonte sola, dato USA, già segnato in `08` come da riverificare su Istat. Sui 5 anni vedi §6 |
| 2.6 | 70-80% S&P 500, 10-20% internazionale, 0-10% obbligazioni lunghe; fuori dalle obbligazioni quando i tassi salgono | **rifiutato** (04/08) | Concentrazione su un paese per un investitore italiano. La regola sulle obbligazioni è una previsione sui tassi: stesso motivo del no al tempismo |
| 2.7 | Limiti USA 2026: piano aziendale 24.500 dollari, conto pensione individuale 7.500 | verificato | ⚠️ La trascrizione dice "75,000": è 7.500 (errore di trascrizione; nel video 1 dice 7.000 per il 2025). Verificata anche la soglia di reddito del conto a esenzione futura per i coniugi (242-252 mila), coerente con il video 1 |
| 2.8 | Plusvalenze oltre l'anno tassate 0-20%, zero sotto 49.450 dollari di reddito (singolo) o 98.900 (coniugi) | verificabile | Non controllato sulla fonte ufficiale |
| 2.9 | Prelievi minimi obbligatori dai 72 anni | verificabile | Probabilmente superato (la norma del 2022 ha alzato l'età): non controllato |
| 2.10 | Evita le quotazioni in borsa appena uscite: il primo giorno circola circa il 20% delle azioni, alla fine del vincolo di vendita (6-12 mesi) arriva il resto e il prezzo scende | verificabile | Fuori perimetro (azioni USA singole). È un'**esclusione**, cioè una scommessa attiva da misurare contro l'indice intero, come nell'idea delle esclusioni settoriali del 03/10. Catalogato, non usato |
| 2.11 | "Buffett e Peter Lynch tengono molto S&P 500" | retorica | Lynch era un gestore attivo. Non usata |

## 6. Conflitti, con la condizione (nessun arbitrato)

1. **Alzare la rata a ogni aumento** (fonte) **contro "la laurea non è un trigger: si aspetta 6-12 mesi"** (nostro §0).
   Non si escludono: la fonte parla di un aumento **a struttura di spesa ferma** (stesso lavoro, stessa vita), dove
   l'aumento è tutto avanzo e impegnarlo subito evita che diventi spesa. Il §0 parla di un **cambio di struttura**
   (primo stipendio e vita da solo), dove l'avanzo non è noto. Il rischio che il §0 non copre è quello che la fonte
   nomina: nei 6-12 mesi di attesa la spesa si adatta al nuovo reddito. **Da decidere alla revisione di settembre
   2027**, non ora.
2. **"Azioni solo per il denaro che non serve da almeno 5 anni"** (fonte) **contro i decenni persi** (modulo 08: 13-25
   anni a rendimento reale nullo per un versamento unico). Cinque anni sono un minimo, non una garanzia. Per noi la
   regola resta: una data d'uso sposta quel denaro nel secchio A, qualunque sia la distanza.
3. **Lettura dell'economia contro pilastro passivo.** La fonte pubblica aggiornamenti economici ogni una o due
   settimane, ma nei due video letti il suo comportamento dichiarato è versare sempre, in ogni anno della tabella.
   Stessa separazione già scritta il 04/08: la lettura macro non entra nel PAC.

## 7. Leve fiscali USA e domanda italiana corrispondente

Le norme USA non si trasferiscono. Si trasferisce la domanda. **Nessuna delle risposte italiane è stata verificata:**
sono domande per una ricerca futura su fonti ufficiali (COVIP, Agenzia delle Entrate), utile dal primo contratto di
lavoro.

| Leva USA (dai due video) | Domanda per l'Italia |
|---|---|
| Contributo del datore al piano aziendale, solo se il lavoratore versa | Il contratto collettivo prevede un contributo del datore al fondo pensione di categoria? A quale versamento minimo del lavoratore scatta? Che cosa succede al TFR? |
| Contributi dedotti dal reddito oggi, tassati all'uscita | Qual è oggi il limite annuo di deduzione per la previdenza complementare, e come è tassata la prestazione finale? |
| Conto tassato oggi ed esente all'uscita | Esiste un equivalente? (Probabilmente no) |
| Crescita non tassata dentro il conto | Come sono tassati i rendimenti annui di un fondo pensione rispetto al 26% di un ETF? Il fondo pensione paga il bollo? |
| Conto intestato al coniuge che non lavora | I versamenti per un familiare a carico sono deducibili? |
| Prelievo anticipato per la prima casa | Quali anticipazioni ammette un fondo pensione, dopo quanti anni e con quale tassazione? |
| Plusvalenze a zero sotto una soglia di reddito, se tenute oltre l'anno | In Italia l'aliquota non dipende dal reddito né dalla durata. L'unica leva nota è il rinvio: un ETF ad accumulo (già scelto) |
| Casa principale venduta senza imposta sul guadagno | Quando è tassata in Italia la plusvalenza sulla vendita di un immobile? |
| Conti per le spese sanitarie | Fondi sanitari integrativi e welfare aziendale: che cosa è deducibile? |
| Compravendite a breve **dentro** il conto previdenziale: nessuna imposta sui guadagni (video 5, 2023) | In Italia un fondo pensione non si usa per comprare e vendere titoli: nessun equivalente noto |
| Perdite di anni precedenti dedotte dal reddito ordinario, 3.000 dollari l'anno (video 5) | Le minusvalenze si compensano con il reddito da lavoro o solo con plusvalenze, ed entro quanti anni? (Da verificare: risposta non controllata) |
| Spese d'impresa dedotte (computer, telefono, arredi: video 5 e 6) | Con partita IVA, regime forfettario contro ordinario: che cosa si deduce davvero? |
| — | Solo italiana: i piani individuali di risparmio (PIR). Obbligano a investire in Italia, quindi confliggono con la scelta All-World |

## 8. Il canale: cosa c'è e cosa leggere dopo

Classificazione per parole chiave dei titoli, quindi approssimata (elenco del 2026-10-13):

| Tema | Video | Ore |
|---|---|---|
| Aggiornamenti economici (lavoro, inflazione, Fed, recessione) | ~78 | ~17,7 |
| Storia personale, lezioni, carriera | ~42 | ~7,0 |
| Regole di base per investire | ~36 | ~4,6 |
| Tasse e conti agevolati USA | ~31 | ~2,4 |
| Casa e debito | ~21 | ~1,8 |
| Attività e secondi lavori | ~11 | ~1,8 |
| Altro (assicurazioni, matrimonio, brevi) | ~34 | ~3,3 |

**Un'osservazione dai soli titoli, non un verdetto.** 22 titoli contengono "recession", dalla metà del 2024 a oggi
("We Are Going Into A Recession", "High probability of Recession in 2025", "We Are Entering a Recession" del
01/10/2025). Nello stesso periodo la sua tabella riporta l'S&P 500 a +23% (2024) e +16% (2025). I titoli sono fatti
per attirare e il contenuto può essere più prudente: per sapere quanto vale la sua lettura servono le previsioni
datate **dentro** i video e un criterio scritto prima (per esempio la datazione ufficiale delle recessioni). È il
metodo già previsto per le [previsioni geopolitiche](../../../../../projects/geopolitica.md): un registro
misurato contro un riferimento.

**Primo blocco (5 video, circa 57 minuti): letto il 25/10/2026 (§10-11), su indicazione di Matteo.** Si legge un video alla volta, per intero, con
un consuntivo alla fine; nessuna trascrizione in blocco prima.

| # elenco | Video | Minuti | Domanda a cui risponde |
|---|---|---|---|
| 47 | *2026 Investment Plan* (`5hUfIbNmAXc`) | 11 | La sua lettura dell'economia cambia ciò che fa coi soldi? |
| 214 | *How I Make Over $250K and Pay Less Than 10% in Tax* (`hkJzagub6Wg`) | 6 | Elenco completo delle leve fiscali che usa (per completare §7) |
| 124 | *How I Would Become a Millionaire Again if I Had to Start Over with Nothing* (`iGcmG1awgrE`) | 12 | Ordine delle operazioni per chi parte da zero: il caso più vicino al nostro |
| 4 | *Economic Update 11 Oct 2026* (`wTMy5tm7oGM`) | 22 | Quali indicatori guarda e con quale regola li legge |
| 128 | *We Are Going Into A Recession, Predictions And What To Do Now* (`sMF2WNpxNVQ`) | 6 | Previsioni datate di due anni fa, misurabili oggi |

**Regola di arresto.** Se dal blocco non esce né un metodo di lettura replicabile né previsioni datate misurabili, gli
aggiornamenti economici restano non letti e il canale si usa solo per i temi dei §3, §5 e §7.

## 10. Primo blocco (25/10/2026): cinque video letti per intero

Trascrizioni scaricate il 25/10 una alla volta (complete: 170-193 parole al minuto contro le 130-160 del parlato
normale), lette per intero una alla volta, poi `rule_extract.py`: nessun passaggio sfuggito. Date di pubblicazione dei
due video con previsioni lette dai metadati (yt-dlp, 25/10). Numerazione dei video in continuita' con §3 e §5.

### Video 3 — *2026 Investment Plan* (`5hUfIbNmAXc`, 05/01/2026, 11 min)

**Risposta alla domanda del blocco** ("la sua lettura dell'economia cambia cio' che fa coi soldi?"): **quasi no**, lo
dice lui: *"It doesn't really change that much year to year."* Il macro tocca solo la quota obbligazionaria (0-10%,
vendute quando i tassi sono scesi molto) e due opzioni da circa lo 0,1% del portafoglio (put sull'S&P 500 comprate a
volatilita' bassa, call su TLT).

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 3.1 | **Previsioni datate (05/01/2026):** disoccupazione in salita ogni mese; la Fed abbassa i tassi per tutto il 2026; gli acquisti di titoli a breve iniziati il 12/12/2025 "non si fermano ad aprile, accelerano" | verificabile | Misura parziale in §11 |
| 3.2 | Fine del quantitative tightening il 01/12/2025; acquisti di T-bill "per liquidita'" dal 12/12/2025 | verificabile | Coerente con quanto noto a Claude fino a meta' 2026; non controllato sulla fonte Fed |
| 3.3 | Ogni anno in media 4-5 cali di almeno il 5% e 1-2 oltre il 10% | verificabile | Statistica storica non controllata; si puo' misurare sui nostri dati dell'S&P 500 |
| 3.4 | Mercati rialzisti: 63 mesi e +182% in media; ribassisti: 14 mesi e −36% | statistica dichiarata | Numeri diffusi nella divulgazione, fonte non citata |
| 3.5 | Il 10% piu' ricco fa circa meta' dei consumi; i consumi sono circa 2/3 del PIL USA | verificabile | Non controllato |
| 3.6 | Metalli (oro, argento, rame, alluminio) tenuti, non comprati, perche' banche centrali e BRICS comprano e la Cina limita l'export d'argento dal 01/01 | opinione | In passato rialzi del 700-1.000% seguiti da cali dell'85% e del 70% (lo dice lui) |
| 3.7 | Allocazione: 75% S&P 500, 15% internazionale, ~10% obbligazioni | **rifiutata** (04/08) | Come 2.6 |

### Video 4 — *Economic Update 11 Oct 2026*, ora intitolato *Bonds Signaling Trouble Ahead For Housing* (`wTMy5tm7oGM`, 22 min)

**Risposta alla domanda del blocco** ("quali indicatori guarda e con quale regola li legge"): **molti indicatori,
nessuna regola che li traduca in azioni.** Elenca lavoro (ADP, BLS con revisioni, partecipazione, disoccupazione
allargata calcolata da lui al 7,6% e al 10,3%, durata oltre 27 settimane, JOLTS), prezzi (PPI, CPI, PCE, totali e core),
PIL, Fed e "dot plot", fiducia dei consumatori, ISM, rendimento del decennale, mutui e una decina di numeri sulla casa,
petrolio e riserve strategiche. L'unico legame con il portafoglio resta il **tempismo sui tassi**: compra obbligazioni
"quando i tassi smettono di salire", put su TLT a scadenza gennaio 2027 (strike 70), put sull'S&P 500 da ricomprare
"ai nuovi massimi".

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 4.1 | Fatti al 11/10/2026: Fed alzata di un quarto a settembre (3,75-4%), decennale al 5,22%, mutuo trentennale al 7,4% (6% a febbraio), disoccupazione 4,2%, CPI 3,4%, scorte strategiche di petrolio ai minimi dagli anni '80, scorte di petroliere in Hormuz | dichiarati, **non verificati** | Oltre la conoscenza di Claude: sono suoi |
| 4.2 | **Previsioni datate (11/10/2026):** una o due strette in piu' fra 2026 e 2027; inflazione sopra il 2% almeno fino al 2028; case giu' di circa il 5% se i tassi restano cosi'; repubblicani che perdono seggi alle elezioni di meta' mandato; prezzi del cibo in salita | verificabile | Materiale per un registro (§11) |
| 4.3 | Mutuo = titoli di Stato + 1-3 punti; +1 punto di mutuo ≈ −10% sul prezzo che una famiglia puo' pagare | verificabile | Regola pratica di accessibilita', non controllata |
| 4.4 | Fondo d'emergenza di 6 mesi perche' il 27% dei disoccupati lo e' da oltre 27 settimane | — | Stesso argomento del 04/08 e di 2.5 |
| 4.5 | Investe in attivita' che possono rendere 10 volte: "anche se meta' fallisce, e' 5 volte" | non falsificabile | Conto che presuppone il 10× sulle sopravvissute: e' la selezione dei vincitori in una frase |
| 4.6 | Metalli per "un paio di centinaia di migliaia di dollari" | dichiarato | Circa il 15% del patrimonio dichiarato: molto piu' di quanto lasci intendere il video 3 |

### Video 5 — *How I Make Over $250K and Pay Less Than 10% in Tax* (`hkJzagub6Wg`, 6 min, anno fiscale 2023)

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 5.1 | Senza pianificazione 39.832 dollari d'imposta su 260 mila (15,3%), con pianificazione 14.311 (5,5%) | **verificato** (conti) | Rifatti con gli scaglioni 2023 per coniugi: tornano, salvo cifre storpiate dalla trascrizione. Il "meno del 10%" del titolo vale solo contando come reddito gli 80 mila di guadagni rimasti nel conto previdenziale |
| 5.2 | Leve: compravendite dentro il conto previdenziale, spese d'impresa, deduzione standard dei coniugi, perdite pregresse, versamento al piano aziendale, credito per figli | — | Norme USA; domande italiane aggiunte al §7 |
| 5.3 | 80 mila di guadagni **a breve** da vendite di azioni nel 2023 | dichiarato | Non e' l'immagine del "compra e tieni" degli altri video; dentro un conto agevolato non pesa sulle imposte |

### Video 6 — *How I Would Become a Millionaire Again if I Had to Start Over* (`iGcmG1awgrE`, 12 min)

**Risposta alla domanda del blocco** (l'ordine delle operazioni per chi parte da zero): competenza richiesta →
sganciare le ore dal guadagno (pagato per risultato, sistemi, macchine) → vivere sotto il reddito → 1.000 dollari
d'emergenza → debiti a tasso alto → investire presto, versamento automatico a ogni stipendio → conti agevolati →
imparare le norme fiscali. Rimpianto dichiarato: una casa plurifamiliare dove abitare affittando le altre unita'.

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 6.1 | 1 dollaro al 7% reale per 45 anni diventa 23 volte | **falsificato** (conti) | Fa **×21,0** |
| 6.2 | 25 dollari a settimana al 10% per 40 anni fanno circa un milione | **falsificato** (conti) | Circa **0,58-0,60 milioni**; 100 $ per 31 anni (0,95-0,99 milioni) e 500 $ per 17 anni (1,05-1,11 milioni) invece tornano |
| 6.3 | Il versamento automatico serve contro l'indecisione, non per un vantaggio di prezzo | — | E' il nostro §0 |
| 6.4 | La grande maggioranza dei milionari USA non ha ricevuto eredita' | statistica dichiarata | Fonte non citata; e' un campione di sopravvissuti |
| 6.5 | Norme USA: casa principale esente fino a 250/500 mila di guadagno dopo 2 anni su 5; plusvalenze a lungo termine 0-20%; crediti d'imposta del 30% su pannelli solari | verificabile | Norme che cambiano: valgono alla data del video |

### Video 7 — *We Are Going Into A Recession, Predictions And What To Do Now* (`sMF2WNpxNVQ`, 29/08/2024, 6 min)

| # | Affermazione | Stato | Nota |
|---|---|---|---|
| 7.1 | **Previsione (29/08/2024):** recessione "ora o entro fine 2024 o nel 2025, probabilmente nel 2025", con la sua definizione: due trimestri di PIL negativo | **mancata** (da verificare) | Vedi §11 |
| 7.2 | **Previsione (29/08/2024):** primo taglio a settembre, da 5,25-5,5% a circa 5-5,25%; a dicembre 4,25-4,75% | **in parte giusta** (da verificare) | Vedi §11 |
| 7.3 | Curva dei rendimenti invertita: 9 volte su 10 segue una recessione entro 6-12 mesi | statistica dichiarata | L'inversione del 2022-2024 di cui parla e' proprio un caso senza recessione nei 12 mesi successivi |
| 7.4 | Recessione media dopo la guerra 10 mesi; la piu' lunga 18 (2007-2009), la piu' corta 2 (2020); picco della disoccupazione ~7-8% in media, 15% nel 2020 | verificabile | Coerente con i dati NBER e BLS noti a Claude; non controllato |
| 7.5 | Bloccare ora i tassi dei certificati di deposito, perche' scenderanno | opinione | E' una previsione sui tassi |

## 11. Previsioni misurate e regola di arresto

**Misura parziale delle previsioni datate.** Fonti: i suoi video successivi e la conoscenza di Claude fino a meta' 2026,
**da verificare** su BEA (PIL) e FRED (`FEDFUNDS`, `MORTGAGE30US`, `UNRATE`), che da questa macchina non rispondono.
Nessun criterio era scritto prima: e' un descrittivo, non un test.

| Data | Previsione | Esito noto | Lettura |
|---|---|---|---|
| 29/08/2024 | recessione probabilmente nel 2025, con due trimestri di PIL negativo | nel 2025 un solo trimestre negativo (il primo), poi crescita; il suo video del 11/10/2026 riporta +2,5% e +2,2% nei primi due trimestri del 2026 | **mancata** |
| 29/08/2024 | Fed a dicembre 2024 fra 4,25% e 4,75% | 4,25-4,50% a dicembre 2024 (taglio di mezzo punto a settembre, non di un quarto) | **giusta sulla direzione e sull'intervallo di fine anno**, sbagliata sull'entita' del primo taglio |
| 05/01/2026 | la Fed abbassa i tassi per tutto il 2026 | secondo il suo stesso video del 11/10/2026, la Fed ha **alzato** a settembre | **contraddetta dai suoi dati**, esito finale a fine 2026 |
| 05/01/2026 | disoccupazione in salita ogni mese | il 11/10/2026 dice 4,2%, "fra il 4 e il 4,3 nell'ultimo anno" | **non confermata dai suoi dati** |

**Regola di arresto (§8).** Si fermava la lettura degli aggiornamenti economici se non usciva **ne'** un metodo di lettura
replicabile **ne'** previsioni datate misurabili.
- Metodo di lettura replicabile: **no.** Gli indicatori non hanno una regola che li traduca in azioni, e l'unica azione
  legata al macro (il tempismo sui tassi) e' gia' rifiutata nel pilastro (2.6).
- Previsioni datate misurabili: **si'**, e le prime misurate danno un esito misto (§11, tabella).

Quindi la regola **non** chiude il canale da sola. Esito proposto, **da decidere (Matteo):** gli aggiornamenti economici
non si leggono come metodo (non ce n'e' uno); le sue previsioni datate (22 titoli con "recession" dal 2024, piu' gli
aggiornamenti) sono materiale per il **registro delle previsioni dell'hub**, misurate contro un riferimento con un
criterio scritto prima. Per il PAC **non cambia nulla**: lui stesso dichiara che il suo comportamento non cambia da un
anno all'altro.

## 9. Prompt per Comet (SPIVA, pagine bloccate)

> Apri i due PDF ufficiali di S&P Dow Jones Indices: "SPIVA U.S. Scorecard Year-End 2025" e "SPIVA Europe Scorecard
> Year-End 2025". Trascrivi alla lettera, con numero di pagina e nome della tabella: (1) nel rapporto USA, la
> percentuale di fondi "All Large-Cap" rimasti sotto l'S&P 500 a 1, 3, 5, 10, 15 e 20 anni; (2) nel rapporto Europa,
> la riga dei fondi "Global Equity" denominati in euro: indice di confronto e percentuale di fondi rimasti sotto a 1,
> 3, 5 e 10 anni. Se un numero non c'è, scrivi "non presente": non stimarlo e non prenderlo da altri siti.
