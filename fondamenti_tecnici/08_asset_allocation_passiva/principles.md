---
titolo: Asset Allocation Passiva — ETF, bond, fiscalita e contesto valutario
fonti:
  - _sorgenti/Petrodollar ed ETF.txt
tipo: concetti
---

# Asset Allocation Passiva — ETF, bond, fiscalita e contesto valutario

> La scelta del prodotto ETF pesa meno del piano: quanto investire, con che cadenza, con che buffer di liquidita e con quale glide-path verso l'obiettivo.
> Per un residente italiano, la struttura piu lineare e un core UCITS ad accumulazione con domicilio Ireland, parte difensiva in governativi euro, regime amministrato e liquidita separata dal portafoglio.
> Il petrodollaro come "motore del dollaro" e in larga misura un mito geopolitico: la dominanza USD era gia solida grazie agli Eurodollari prima del 1974, e oggi gli USA sono esportatori netti di petrolio.

## Concetti

### Tipi di ETF: forma e funzione

**Accumulazione vs distribuzione**

Un ETF ad accumulazione reinveste automaticamente dividendi e coupon nel fondo; uno a distribuzione li versa periodicamente al possessore. L'accumulazione e piu efficiente nella fase di costruzione del capitale (niente attrito fiscale immediato sui dividendi, compounding integro); la distribuzione e utile se si vuole un flusso di reddito periodico o si e gia in fase di decumulo.

**Fisico vs sintetico**

- Fisico (full replication o sampling): l'ETF detiene i titoli sottostanti. Il sampling — un sottoinsieme rappresentativo — introduce un minimo tracking error ma riduce i costi operativi su indici molto ampi.
- Sintetico (swap-based): l'ETF non detiene i titoli direttamente ma stipula contratti swap con una controparte che fornisce il rendimento dell'indice; la controparte posta collaterale a garanzia. Introduce rischio controparte, struttura meno trasparente, ma puo essere efficiente su mercati difficilmente accessibili.
- Ibrido: combina fisico e sintetico.

Per il retail italiano il fisico e generalmente preferito per semplicita e trasparenza.

**TER (Total Expense Ratio)**

Costo annuo dichiarato del fondo. Su UCITS ETF passivi europei, ~0,20% e tipico e ragionevole. Sopra 0,50% su un passivo e alto; attorno all'1% segnala gestione attiva. Su orizzonti lunghi, pochi decimi di punto fanno differenza reale per via del compounding. Il TER non racconta tutto (costi di transazione interni, securities lending), ma e il primo filtro da applicare.

**UCITS vs ETF USA-domiciled**

Per un residente fiscale italiano gli ETF UCITS sono la scelta piu lineare:
- Armonizzati, gestione fiscale semplificata in Italia.
- Tassazione sostitutiva ordinaria al 26% sui redditi finanziari (vedi sezione fiscalita).
- Gli ETF USA-domiciled (non UCITS) possono sembrare piu "puri" o economici, ma:
  - Non armonizzati: trattamento fiscale piu complesso.
  - **US estate tax**: i non residenti USA con asset USA-domiciled oltre la soglia prevista dalla normativa statunitense (storicamente molto bassa per non residenti) sono esposti all'imposta di successione americana. Questo e il rischio principale, non i costi.
  - Il modulo W-8BEN dichiara lo status di non residente e consente ritenute ridotte da trattato, ma non elimina il tema strutturale dell'estate tax.

**Domicilio: Irlanda**

L'Irlanda e il domicilio piu vantaggioso per gli ETF UCITS europei grazie al trattato fiscale con gli USA: la ritenuta alla fonte sui dividendi USA e ridotta al 15% (vs 30% standard). Il Lussemburgo sta recuperando ma resta meno conveniente. Preferire ETF Ireland-domiciled quando si acquistano prodotti con esposizione USA significativa.

**Currency hedging su equity**

Il currency hedging protegge dall'oscillazione del cambio tra la valuta del fondo e quella dell'investitore, usando derivati forward. Costa denaro (premio) e aggiunge complessita. Su equity globale il hedging tipicamente **non ha senso finanziario**: le grandi multinazionali sono gia naturalmente diversificate valutariamente, e nel lungo termine il motore dei rendimenti e la crescita degli utili, non il cambio. Il hedging puo avere senso in situazioni specifiche (prossimo acquisto immobiliare, necessita di liquidita in valuta a breve termine). Sul comparto bond il tema e dibattuto e meno netto.

**Scelta dell'issuer**

Issuer principali: Amundi, iShares, Vanguard, Xtrackers. I criteri rilevanti sono la reputazione/dimensione dell'issuer (issuer piccoli rischiano di chiudere l'ETF), le caratteristiche del prodotto specifico (TER, AUM, liquidita, domicilio), non l'issuer di per se. Preferire prodotti con AUM nell'ordine di miliardi e volumi scambiati su exchange accessibili.

---

### All-World vs USA vs Emergenti

**All-World**

Include migliaia di societa di mercati sviluppati piu una quota emergenti (tipicamente 10-12% del peso totale). Gli USA pesano solitamente il 55-65% del totale. E il compromesso piu pulito per un singolo ETF azionario: ampio, gia include gli emergenti, riduce la necessita di market timing tra aree geografiche. Comportamento piu equilibrato: puo fare leggermente meno dell'USA puro nei periodi in cui Wall Street domina, ma regge meglio nei periodi di sottoperformance USA prolungata.

**ETF USA**

100% allocato negli USA, forte concentrazione su mega-cap (tecnologia, finanza, salute). Storico di crescita e resilienza eccellente nel lungo periodo. Ha senso come scelta core per chi accetta piu concentrazione o come satellite per sovrappesare il motore piu forte del capitalismo. Porta con se massima esposizione al dollaro USA.

**ETF Emergenti**

Pesi molto variabili nel tempo e tra provider; solitamente Cina, Taiwan, India tra le prime posizioni. Offre potenziale di crescita superiore ma con: volatilita maggiore, rischio politico, valute piu deboli e volatili, maggiore sensibilita a dollaro, tassi e materie prime. Da trattare come integrazione di portafoglio, non come base.

**Rischio cambio per investitore euro**

ETF USA = esposizione quasi totale al dollaro. All-World = ancora molto legato al dollaro per il peso USA. Emergenti = aggiunge valute spesso piu deboli e volatili. Il cambio amplifica o attenua i rendimenti nel breve/medio, ma nel lungo il motore e la crescita degli utili aziendali.

**Regola pratica**

All-World come base, USA come sovrappeso opzionale, Emergenti solo in quota aggiuntiva se si tolera la volatilita extra.

---

### Bond: governativi, duration e lezione 2022

**Governativi**

Blocco piu difensivo del portafoglio. Per l'investitore italiano, i titoli di Stato dell'area euro e quelli eleggibili (vedi fiscalita) hanno anche trattamento fiscale piu favorevole. Funzione: stabilizzatori, non motore di rendimento.

**Corporate**

Piu rendimento atteso, piu rischio di credito, maggiore correlazione con l'azionario nei momenti di stress. Utili per carry aggiuntivo, ma non sostituiscono la funzione difensiva dei governativi di qualita.

**Duration**

Sensibilita del prezzo del bond alle variazioni dei tassi. Duration lunga = il titolo reagisce piu violentemente ai rialzi dei rendimenti. Nel 2022 questa e stata la trappola principale dei portafogli obbligazionari: anni di rendimenti artificialmente bassi, poi rialzo aggressivo dei tassi; i Treasury lunghi hanno subito perdite eccezionali, anche l'investment grade ampio ha chiuso in forte ribasso. La duration va calibrata sull'orizzonte temporale del piano.

**Ruolo difensivo nel portafoglio**

I bond non servono a battere l'azionario. Servono a garantire che il capitale sia disponibile quando serve: meno volatilita, meno drawdown, meno probabilita di dover liquidare azioni nel momento peggiore.

---

### Fiscalita italiana (linee generali — consultare un commercialista per la propria situazione)

**Aliquote**

- 26%: aliquota standard su ETF armonizzati (UCITS) e su redditi finanziari ordinari (plusvalenze, dividendi).
- 12,5%: aliquota ridotta sulla quota di rendimento attribuibile a titoli di Stato eleggibili (Italia e altri governi in whitelist). Su un ETF obbligazionario misto la quota al 12,5% viene calcolata proporzionalmente.

**Regime amministrato**

Il broker italiano calcola, trattiene e versa le imposte in automatico; gestisce anche il conto delle minusvalenze laddove compensabile. E il regime piu pratico per il retail: meno errori, meno attriti. Adottarlo se possibile.

**Regime dichiarativo**

L'investitore riporta tutto in dichiarazione dei redditi. Piu controllo, piu complessita e rischio di errore. Ha senso con intermediari esteri o se si vuole gestione diretta.

**Compensazione minusvalenze**

Le minusvalenze hanno regole proprie di compensazione e non si usano liberamente contro tutte le categorie di reddito finanziario. Per gli ETF armonizzati (UCITS) il tema e particolarmente critico: i guadagni su ETF sono tipicamente "redditi di capitale", non compensabili con minusvalenze da "redditi diversi" (come azioni, ETC/ETN, certi certificati). Questo e un punto di attenzione rilevante nella costruzione del portafoglio: il tipo di strumento impatta la compensabilita. Verificare con un professionista.

---

### Petrodollaro e dominio USD: il debunk

La narrativa popolare sostiene che il 1974 accordo USA-Arabia Saudita (Kissinger/Nixon - Re Faisal) abbia ancorato il prezzo del petrolio al dollaro, creando una domanda strutturale di USD che ne garantisce il ruolo di valuta di riserva mondiale. Questa tesi e in larga misura un **mito geopolitico**.

**Cosa dicono i documenti desecretati (FOIA 2016, riportati da Bloomberg)**

L'accordo del 1974 si concentrava su: cooperazione economica, sviluppo industriale saudita, stabilizzazione dei prezzi del petrolio (a livelli bassi), e flusso di beni/tecnologia USA verso il Golfo. I documenti **non contengono alcun impegno saudita a vendere petrolio esclusivamente in dollari**. Ricerche citate (Yaw Asamoah) mostrano che l'Arabia Saudita continuava ad accettare sterline britanniche per il petrolio ben dopo il 1974.

**Eurodollari e preesistenza del dominio USD**

Gia nel 1974 il dollaro dominava le riserve delle banche centrali globali, costruito sulla base del mercato degli **Eurodollari** (depositi in USD tenuti offshore), che preesiste e supera per importanza il "petrodollaro". Il dominio del dollaro poggia su liquidita, profondita dei mercati finanziari USA e fiducia globale, non sul pricing petrolifero.

**Ruolo reale del Golfo nei mercati USA**

Negli anni '80 i paesi del Golfo hanno acquistato Treasury USA, ma detenendone una **frazione molto piccola** del totale. Oggi:
- Arabia Saudita occupa una posizione bassa tra i detentori di debito USA, dietro molte economie piu piccole.
- I SWF del Golfo combinati rappresentano circa **1% del mercato azionario USA** (stimato $72 trilioni).
- I paesi del Golfo investono in USA perche i mercati americani sono i piu grandi e liquidi al mondo — non perche gli USA "dipendano" da loro.

**Scala relativa dei mercati** (CAVEAT: i numeri specifici qui sotto sono citati dalla fonte senza riferimento a dati primari verificabili — usare come ordine di grandezza, non come dato certificato)

Il mercato petrolifero globale vale circa $3 trilioni/anno (2025). Il mercato valutario (FX) ha un turnover giornaliero di circa $9,6 trilioni, ovvero circa $2.500 trilioni su base annua. Il petrolio e quindi irrilevante come driver del FX globale in termini di volumi assoluti.

**Perche il petrodollaro conta ancora meno oggi**

1. Quota petrolio sul PIL USA: era 13-15% durante la crisi 1979, oggi 5-7% per l'aumento di efficienza energetica.
2. Dal 2020 gli USA sono **esportatori netti di petrolio** — la dinamica che rendeva rilevante il riciclo dei petrodollari non esiste piu nella stessa forma.
3. Le eccedenze delle partite correnti dei paesi asiatici manifatturieri (Cina, Giappone, Corea) superano di gran lunga quelle dei paesi petroliferi come driver della domanda di dollari.

**Implicazione per l'investitore**

I tentativi di dedollarizzazione basati sul prezzo del petrolio in yuan o altre valute non intaccano strutturalmente il ruolo del dollaro. La dominanza USD dipende da fattori piu profondi (profondita mercati, rule of law, liquidita) che da accordi bilaterali sul pricing dell'energia.

---

### Glide-path e disciplina DCA

**Glide-path**

Riduzione progressiva (non brusca) del rischio di portafoglio man mano che si avvicina l'orizzonte di spesa. La quota difensiva (bond + liquidita) cresce nel tempo, non per generare rendimento ma per garantire che il capitale sia disponibile senza dover liquidare equity in un momento sfavorevole.

**DCA (Dollar-Cost Averaging)**

La cadenza giusta del DCA non e "quanto si vorrebbe investire" ma "quanto si puo investire con regolarita senza intaccare il buffer di liquidita". Il piano migliore e quello che si riesce a mantenere anche in un anno pessimo, quando il mercato scende e la tentazione di fermare i versamenti e massima. La continuita batte la precisione di timing.

**Buffer di liquidita**

Va tenuto separato dal portafoglio investito. Deve coprire spese vive e imprevisti senza forzare vendite in perdita. Se il reddito e variabile o se si e vicini alla fase di decumulo, il buffer deve essere piu ampio. Non e una quota del portafoglio: e una riserva pre-investimento.

**Struttura pratica per residente italiano**

- Core azionario: ETF UCITS globale ad accumulazione, domicilio Irlanda.
- Satelliti (opzionali): sovrappeso USA o EM, ma senza complicare.
- Parte difensiva: governativi euro di qualita, duration coerente con l'orizzonte.
- Fiscalita: regime amministrato se possibile.
- Liquidita: buffer separato.

---

### Nota sul blocco "portfolio engineering con hedge leg" (speculativo/promozionale, da verificare)

La fonte include una sezione che propone l'uso di un ETF alternativo (KMLM, trend following) come "hedge leg" su un portafoglio SPY, con leva per mantenere l'esposizione beta. I numeri citati (Sharpe ~0,79 vs 0,77, max drawdown -22% vs -25%, backtest 5 anni) provengono da un singolo backtest in-sample su un periodo specifico, senza walk-forward ne out-of-sample validation. La conclusione — che l'active risk allocation superi sistematicamente il passive investing — e una tesi commerciale tipica delle societa di gestione quantitativa, non un risultato peer-reviewed. Il concetto di volatility drag e reale e ben fondato; la soluzione proposta (leva + hedge leg su 5y backtest) non costituisce evidenza robusta. Non riprodurre i numeri come fatto; considerare il concetto di diversificazione con asset a bassa correlazione come principio valido ma non come ricetta operativa validata.

---

## Regole operative

- Scegli il domicilio Irlanda per ETF UCITS con esposizione USA: WHT al 15% invece del 30%.
- Evita ETF USA-domiciled come residente italiano: rischio estate tax USA per non residenti oltre soglia.
- Usa accumulazione nella fase di costruzione del capitale; passa a distribuzione solo se hai necessita di reddito periodico.
- TER e primo filtro; sopra 0,50% su un passivo verifica il perche. AUM nell'ordine di miliardi e liquidita adeguata sugli exchange accessibili.
- Non fare currency hedging su equity globale: costo certo, beneficio incerto nel lungo termine.
- Tieni la duration dei bond coerente con l'orizzonte: bond lunghi in un contesto di rialzo tassi sono rischiosi quanto l'equity.
- Adotta il regime amministrato (broker italiano) se possibile: delega il calcolo e la gestione delle imposte, riduci errori.
- Attenzione alla compensazione minus su ETF UCITS: i guadagni sono "redditi di capitale" e non compensabili con minus da "redditi diversi" (azioni, ETC). Consulta un commercialista.
- Il petrodollaro non e un rischio operativo per l'investitore passivo: la dominanza USD dipende da fattori strutturali profondi, non dal pricing del petrolio.
- DCA: investi solo quello che puoi mantenere anche in un anno di perdite. Il buffer non si tocca.
- Riduci il rischio progressivamente con il glide-path, non bruscamente a ridosso dell'obiettivo.

## Collegamenti

- [[05_portfolio_rischio]] — decomposizione del rischio (idiosincratico, settoriale, sistematico), CAPM, beta: base teorica per capire perche la diversificazione tramite ETF funziona e dove si ferma.
- [[06_stock_selection]] — selezione titoli come satellite opzionale rispetto al core ETF passivo.
- [[07_data_sources]] — fonti dati per monitorare composizione e TER degli ETF nel tempo.
- [../../docs/INVESTING_PILLAR_PLAN.md](../../docs/INVESTING_PILLAR_PLAN.md) — piano dei due secchi (accumulo vs liquidita): il contesto operativo in cui applicare questi principi.
- [../../docs/INVESTMENT_ALGO_DESIGN.md](../../docs/INVESTMENT_ALGO_DESIGN.md) — design del sistema di investimento algoritmico che automatizza DCA e ribilanciamento.

## Fonti

- `_sorgenti/Petrodollar ed ETF.txt` — trascrizione di piu video su ETF (scelta issuer, replicazione, UCITS, domicilio, fiscalita IT, All-World vs USA vs EM, bond, glide-path), sezione portfolio engineering con hedge leg (KMLM/SPY), e debunk del petrodollaro (accordi 1974 FOIA, Eurodollari, scala mercati FX vs petrolio).
