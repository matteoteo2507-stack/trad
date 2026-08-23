# Blocco B1 — triage per video (fascia B: strategie meccanicamente specificate)

---

## B1.1 — "90% Win Rate (1:20+ RR)" (TG Capital / Tyler) · 48 min · 10.478 parole

`ADnslyKOwFE` · ICT-derivato. **London kill zone 3:00-6:30 ora di New York**, grafico a 30 minuti,
EMA 5/9/13/21 impilate, sopra la EMA 200 = bias long. Sequenza: **fair value gap** stampato sulla
candela delle 2:30-3:00 → **candela doji** che perfora il 50% del FVG ("consequent encroachment")
→ la candela successiva **chiude sotto** il massimo della doji → long. Stop sotto il minimo della
doji (~10 pip). Target: si cavalca il trend sul daily. Su USDCAD, NZDUSD, EURUSD, GBPUSD, USDJPY e
**oro**. Dichiara 6-8 ingressi l'anno per coppia, 10-15 sull'oro.

### Verdetto: **SCARTATO** — e il fallimento del BS-test piu' netto del funnel

**Il claim: 90% di win rate a 1:20 minimo.**

$$E[R] = 0{,}90 \times 20 - 0{,}10 \times 1 = \mathbf{+17{,}9R \text{ per trade}}$$

| riferimento nostro (misurato) | E[R] | il claim e' |
|---|---|---|
| fade NXT (LEAD) | +0,31R | **58×** |
| Donchian, uscita migliore | +0,14R | **128×** |
| claim Crooks (A2.3) | +0,74R | **24×** |

A 40-50 trade l'anno sarebbero **+716R / +895R annui**. A un rischio dello 0,5% per trade fanno
**+447% l'anno semplice**, prima di composizione. Non esiste nulla nella storia dei mercati che
sostenga questo.

**Ma c'e' di peggio: il claim non e' nemmeno BEN FORMATO.** Dichiara che **sull'oro non usa uno
stop fisso** (*"aspetto la chiusura della candela"*). Senza stop fisso **il denominatore di R non
esiste**: "1:20" non e' una quantita' definita. E mostra un esempio che *"e' corso per 175R"*
aggiungendo *"so che e' impossibile tenerlo cosi' a lungo"* — cioe' l'R realizzato non e' l'R
dichiarato.

**Concetti**: fair value gap e kill zone ICT. Il FVG e' nella nostra **famiglia CLOSED**: v1,
breadth **0/16**, pooled 29,6% contro 29,8% del random, esito **nullo**.

### L'unica cosa utile, e non e' la strategia

Spiega con precisione **perche' un trader swing deve pretendere un drawdown calcolato sul BALANCE
e non sull'equity**: le firm con drawdown *equity-based* o *ibrido* prendono alle 17:00 il valore
**piu' alto fra equity e balance**; quindi se sei dentro un trade in profitto del 10%, la soglia si
**alza** su quel 10% flottante, e una normale ritracciata il giorno dopo **brucia il conto**.

E' esattamente il **primo killer silenzioso** che avevamo identificato in
[PROP_FIRM_CRITERIA §1](../../../docs/PROP_FIRM_CRITERIA.md) — *"daily drawdown su balance, NON su
equity flottante"* — qui **confermato da un praticante con il meccanismo esplicitato**. Conferma
indipendente di una nostra analisi, dall'unica fonte che ha davvero interesse a saperlo.

**Nota di provenienza**: dichiara spontaneamente di essere **bandito da oltre 25 prop firm**, e lo
interpreta come firm che non vogliono pagare i vincenti. Lettura alternativa altrettanto coerente:
il *payout review*, cioe' **il meccanismo di enforcement che avevamo documentato**
(DECISIONS 2026-08-07: l'enforcement scatta alla richiesta di prelievo, non all'apertura).
Non decidiamo quale delle due sia vera — registriamo che il dato e' compatibile con entrambe.

---

## B1.2 — "98% Win Rate" — first red day (Alex Temiz) · 72 min · 13.809 parole

`Jx5cJ_qb31U` · **stessa identica strategia del terzo modello di Dux (A1.2)**: dopo una corsa
**parabolica multi-giorno** (minimo **3 giorni** di estensione vera, non consolidamenti), si shorta
il **primo giorno in cui il prezzo scende sotto la chiusura del giorno precedente**. Stop: la
riconquista della linea "rosso-verde" (= chiusura precedente); se la riconquista, **la tesi e'
morta e si esce**. Dichiara ~4 occorrenze l'anno, ~2 M$ verificati su questo pattern.

### Verdetto: **SCARTATO** — stessa barriera di A1.2

Azioni USA, lato **corto**: servono prestito titoli, gestione degli halt e (nel suo caso) opzioni.
Non misurabile da noi con onesta'.

### Il BS-test qui si comporta diversamente, e va detto

A differenza di B1.1, questo claim **non implica un rendimento impossibile**: 4 trade l'anno, anche
a E[R] molto alto, danno un totale gestibile — il suo 1,2 M$ annuo viene dalla **size**, non dalla
frequenza. L'implausibilita' e' altrove: **il 98% su ~4 campioni l'anno**. Su 8 anni sarebbero
31 vittorie su 32. Straordinario, non impossibile, e **non verificabile**.
Categoria: *claim non-rigettato ma invalidabile*, come Dux.

### LA CONVERGENZA PIU' FORTE DEL FUNNEL — terza fonte indipendente sullo stesso fenomeno

| fonte | formulazione | frequenza | win dichiarato |
|---|---|---|---|
| **Dux** (A1.2) | "first red day" dopo >=3 giorni verdi con volume crescente | 5-10/anno | fino al 90% |
| **Temiz** (B1.2) | "first red day" dopo corsa parabolica multi-giorno | ~4/anno | 98% |
| **Breunigstein** (A1.5) | movimento estremo + capitolazione → reversione; **piu' gambe = piu' probabile** | selettiva | 70-80% |

E danno **tutti lo stesso meccanismo economico**, che non e' un pattern grafico:
**i compratori in ritardo restano intrappolati e diventano venditori forzati**. Temiz aggiunge il
passaggio successivo: a quel punto le societa' fanno un aumento di capitale diluitivo, immettendo
altra offerta a prezzo piu' basso.

### Il primitivo generico, indipendente dallo strumento — e testabile SENZA shortare

> Dopo **N giorni consecutivi di estensione parabolica**, il **primo giorno che chiude sotto la
> chiusura precedente** segna un cambio di momentum con **rendimenti attesi negativi**.

Non c'e' nulla di specifico alle small cap USA: serve solo un asset capace di estensione
parabolica, e **ne abbiamo** — crypto, energia (NatGas), agricoli (cacao, caffe'), argento.

**E soprattutto: si puo' misurare senza alcuna ipotesi di esecuzione.** Non serve shortare, non
serve il prestito titoli: basta misurare la **distribuzione dei rendimenti futuri** dopo il segnale
contro l'incondizionata. E' esattamente la forma di test che sappiamo fare e che non richiede
nessuna assunzione su fill, borrow o halt.

**Perche' il nostro NO-GO sulla mean reversion non lo copre**: quel test usava z-score **Z=1**,
deviazione lieve. Qui si parla della **coda estrema** — tre giorni o piu' di estensione parabolica.
Ipotesi diversa, mai testata.

**Stato**: e' oggi il **filo piu' forte del funnel** — tre fonti indipendenti, un meccanismo
economico dichiarato, e misurabilita' senza assunzioni di esecuzione. Piu' solido dello stage
analysis (una fonte) e della conferma incrociata (una fonte).

---

## B1.3 — "3 Simple Steps To Master The TREND" (Anthony Crudele) · 46 min · 9.892 parole

`EZ_L7zovyrw` · veterano ventennale, futures su indici (ES, NQ, Russell), **swing 1-5 giorni**.
Classifica ogni mercato in **tre ambienti** e poi opera **una sola direzione**.

### Specifica — INTERAMENTE ARITMETICA, zero giudizio visivo

Strumento unico: **bande di Bollinger a 20 periodi e 3 deviazioni standard, sul giornaliero**
(usa 3 e non 2 perche' sugli indici la 2 e' troppo stretta).

| ambiente | definizione meccanica | operativita' |
|---|---|---|
| **consolidamento** | bande **contratte e piatte** | due direzioni, **si opera sui bordi del range, MAI in mezzo**; si scende di timeframe |
| **espansione** | bande che **puntano verso l'esterno** + il prezzo rompe i massimi precedenti | **solo long** (speculare short). Target: **il picco precedente della banda** = *"lavoro non finito"* |
| **ritorno alla media** | bande che **ricominciano a contrarsi** dopo il trend | **Fibonacci sui PICCHI DELLE BANDE**, non sul prezzo: chiusura giornaliera sotto il **30%** → target **50%**; si esce quando una chiusura torna sopra |

Sizing dichiarato: **rischio in dollari fisso, size aggiustata alla distanza dello stop** — mai la
stessa size (*"se oggi il rischio e' 20 punti e domani 200, non posso avere lo stesso numero di
contratti"*). L'RSI serve solo a confermare ipercomprato/ipervenduto nella fase di reversione.
Il suo indicatore "Beacon" (il fib automatico sui picchi delle bande) e' **open source** su
NinjaTrader e TradingView: **lo regala**.

### Verdetto: **CANDIDATO** — il meglio specificato di tutto il funnel

| criterio | esito |
|---|---|
| strumenti che tradiamo | **SI** — indici (NAS100, SPX500), e la regola e' generalizzabile ai 27 |
| timeframe | **SI** — giornaliero |
| codificabilita' | **TOTALE**: larghezza e pendenza delle bande, rottura dei massimi, livelli fib sui picchi delle bande. **Non c'e' una sola decisione visiva** |

E' **piu' semplice** dello stage analysis di Zhang (A1.4): un indicatore invece di quattro medie
piu' il giudizio sulle pendenze, e in piu' **definisce meccanicamente anche la fase di reversione**,
dove Zhang si limita a dire "evita".

### Onesta' della fonte, da segnalare

- **Dichiara dove perde**: *"le zone di transizione sono dove mi ammazzo, storicamente e
  attualmente"*. Indica il proprio punto debole invece di nasconderlo.
- **Nessun claim numerico**: nessun win rate, nessun R:R, nessuna cifra di profitto. Terza fonte del
  funnel (con Zhang e Ashraf) a non offrire **niente da sottoporre al BS-test**.
- Ammette che i **target sono il problema irrisolto** della strategia e che si appoggia a livelli
  altrui, VWAP ancorata e medie mobili.
- Sul giorno della pausa tariffaria del 90% (+10% in una seduta): *"non so cosa avrebbe potuto fare
  chiunque altro"*. Non pretende che il metodo copra gli shock da titolo di giornale.

### Quinta formulazione indipendente di "non operare in mezzo"

> *"Opera sui bordi del range. Stai fuori dal mezzo."*

Dopo Zhang (evita gli stage 1 e 3), Breunigstein (solo se esteso), Crooks (contro-trend solo se
esteso) e Desano (no trade zone). **Cinque fonti, cinque vocabolari, un'unica regola** — ed e'
la seconda che fornisce anche un **classificatore di regime a tre stati** meccanico.

**Nota di parentela con noi**: le bande di Bollinger a 20 periodi sono la stessa "media a 20 =
equilibrio" che Breunigstein usa come **target** della reversione (A1.5). Due fonti indipendenti,
stesso oggetto matematico, ruoli diversi: per Crudele definisce **il regime**, per Breunigstein
**il bersaglio**.

---

## B1.4 — "Wall Street's Formula To Measure FEAR" (Dylan O'Neal) · 98 min · 16.137 parole

`4BgkLlwgpvo` · trader di una prop tradizionale di Wall Street. Usa il **VIX come filtro di
conferma** per i futures su S&P e Nasdaq.

### La meccanica

Il VIX misura la volatilita' implicita a 30 giorni ricavata dal posizionamento sulle opzioni SPX.
Domanda di put su S&P che sale → VIX su → **pressione sull'S&P**; e viceversa. Su questa base:

**1. Setup di divergenza.** L'S&P rompe il **minimo del giorno prima** con momentum → si guarda il
VIX. Se il VIX e' **al di sopra del proprio massimo del giorno prima**, la discesa e' confermata e
prosegue. Se invece il VIX fa un **massimo decrescente** (debolezza relativa), la rottura e' un
**bear trap**: si aspetta che l'S&P riconquisti il minimo e si va **long**, preferibilmente sul
Nasdaq se e' lui a mostrare forza relativa. Tripla conferma = S&P rompe + VIX debole + Nasdaq fa un
minimo crescente.

**2. La "regola dell'1%" — la piu' testabile di tutto il funnel.** Se in una giornata **l'S&P e' su
di >= 1% E il VIX e' su di >= 1%**, e' un'anomalia: il VIX dovrebbe essere piatto o giu'. Implica
troppa pressione, e l'S&P difficilmente tiene quei massimi → si cerca una resistenza. Speculare:
**entrambi giu' di >= 1%** → rimbalzo probabile, si cerca un supporto.

**3. La "regola del 16"**: VIX / 16 = movimento giornaliero atteso in % sull'S&P.
Dichiara: *"la uso da anni e sinceramente non so perche' sia 16"*. **La ragione e' esatta e
banale**: √252 = **15,87**. E' semplicemente la **de-annualizzazione** della volatilita' implicita
(il VIX e' espresso annualizzato). Nulla di misterioso, e vale per qualunque volatilita' annua.

### Verdetto: **CANDIDATO**, e la regola dell'1% e' il test piu' economico che abbiamo

| criterio | esito |
|---|---|
| strumenti | **SI** — abbiamo SPX500 e NAS100 su D1. **Il VIX non ce l'abbiamo**, ma e' fra i dati storici piu' liberamente disponibili (dal 1990) |
| timeframe | **SI** — la regola dell'1% e' definita su **chiusure giornaliere** |
| codificabilita' | **TOTALE** per la regola dell'1%: due serie, una condizione aritmetica. Zero discrezionalita', zero lettura visiva |

**Perche' e' il candidato piu' economico**: due serie giornaliere, una condizione, e si misura la
**distribuzione dei rendimenti futuri** contro l'incondizionata. Nessuna ipotesi di esecuzione,
nessun fill, nessun costo da modellare per rispondere alla domanda *"il segnale contiene
informazione?"*. Si puo' eseguire in un pomeriggio.

**Ed e' una FAMIGLIA NUOVA**: la volatilita' implicita come segnale non e' mai stata testata da noi.
Il nostro registro copre livelli, trend, mean reversion, breakout intraday, stagionalita', griglie
di prezzo. **Budget di famiglia intatto**, come per il volume anomalo di A2.2.

### Onesta' della fonte

Dichiara spontaneamente **il modo di fallire**: sui massimi storici il VIX tocca un **pavimento
naturale** e puo' persino risalire, perche' le coperture costano poco e i gestori le comprano — il
che produce un **falso segnale** di pressione. In quella condizione dice di stare fermo. E' la
descrizione precisa di un limite del proprio strumento, e va registrata insieme al segnale: un test
serio deve **condizionare sui massimi storici**.

Nessun claim di win rate. Un solo trade mostrato (6:1 sul VIX del 20 febbraio). Claim di contesto,
non verificato: *"il 90% del volume sui futures S&P e' algoritmico e legato al prezzo del VIX"*.

### Terza fonte sulla conferma incrociata

Dopo Desano (A2.5, "big four": NQ/ES/SPY/QQQ) e Crooks (A2.3, sentiment retail contrarian), questa
e' la terza formulazione del **filtro di conferma fra strumenti**, e la prima che aggiunge una
classe davvero diversa: **la volatilita' implicita** invece di un altro strumento direzionale.

---

## B1.5 — "The ONE Indicator" — volume profile (Forest Knight) · 83 min · 16.183 parole

`q_MdVlZ1SH4` · profilo di volume su NQ. Nodi ad alto volume = prezzi "appiccicosi"; nodi a basso
volume = il prezzo li attraversa di corsa. Si opera sui **bordi** di uno scaffale ad alto volume con
una **candela-segnale ad alto volume**, e i livelli chiave sono **massimo/minimo della notte** e
**massimo/minimo del giorno prima**. Profilo su settimanale/giornaliero, esecuzione da 4 ore a 2
minuti.

### Verdetto: **SCARTATO** — combina DUE famiglie gia' chiuse

1. **Profilo di volume**: la nostra v2 ha testato POC, VAH, VAL, VWAP e VWAP ancorata su 16 asset →
   **0 celle su 48** battono il random, breadth **0/16** per ciascun concetto.
2. **Massimo/minimo del giorno precedente**: v1, breadth **0/16**, reazione **28,8% contro 30,5%**
   del random, CI [−2,4; −1,2] — rotti **piu'** del caso.
3. L'ingresso richiede comunque di **leggere una candela-segnale**: visivo.

E' il contenuto piu' direttamente gia'-falsificato dell'intero funnel.

### Tre cose che valgono comunque

**1. Conferma indipendente del nostro caveat sul volume in FX.** Dice, spontaneamente:
*"il forex non ha una borsa centralizzata, quindi qui fallisce miseramente — non lo trado per
questo"*. E' esattamente il limite che il nostro repo dichiara dalla v2 (volume = proxy di conteggio
tick sui cambi). **Conseguenza operativa per A2.2**: se testeremo il volume anomalo come segnale, va
ristretto a strumenti con volume significativo (indici, metalli, energia, crypto) ed **escluso il
forex**, non per prudenza generica ma perche' due fonti indipendenti dicono che li' il dato non
misura ciò che sembra.

**2. Il look-ahead descritto dalla sedia del trader.** Insiste: *"se cerchi informazione nella
candela, devi aspettare che CHIUDA"*, e descrive il modo di fallire — a 3 ore e 58 di una candela a
4 ore sembra un segnale, e negli ultimi minuti diventa il contrario. Aggiunge il trucco operativo di
**nascondere la candela in formazione** per non poterla vedere.

E' il nostro **kill duro n. 1** (look-ahead) espresso in forma operativa, e la versione
discrezionale della nostra regola "segnale su dati ≤ t-1". Un praticante che arriva per esperienza
alla stessa regola che noi imponiamo per metodo.

**3. Quarta formulazione del meccanismo degli intrappolati.** Il suo *"ultimo uomo"*: chi ha comprato
sul massimo resta bloccato e diventa **venditore forzato** quando il prezzo torna li'. E' lo stesso
meccanismo di Dux (A1.2), Temiz (B1.2) e Breunigstein (A1.5). **Quattro fonti, stessa spiegazione
economica.**

E **sesta formulazione di "non operare in mezzo"**: *"dove non c'e' nessuno ti fai tritare — si
opera da bordo a bordo"*.

---

# CONSUNTIVO DEL BLOCCO B1 (5 video, 66.499 parole, ~5,8 ore)

| # | fonte | verdetto |
|---|---|---|
| B1.1 | TG Capital — kill zone ICT + FVG | **SCARTATO** (BS-test: +17,9R per trade; e senza stop fisso R non e' definito) |
| B1.2 | Alex Temiz — first red day | **SCARTATO** (small cap USA short) ma **terza fonte** sul primitivo estensione→inversione |
| B1.3 | Anthony Crudele — regimi con bande di Bollinger | **CANDIDATO** — il meglio specificato del funnel |
| B1.4 | Dylan O'Neal — VIX come filtro | **CANDIDATO** — il test piu' economico del funnel |
| B1.5 | Forest Knight — profilo di volume | **SCARTATO** (due famiglie gia' chiuse) |

**Due candidati su cinque. Cinque candidati su quindici video letti.**

## Le due cose piu' importanti uscite da questo blocco

**1. Il filo "estensione estrema → inversione" e' ora a tre fonti + un meccanismo economico a
quattro.** Dux, Temiz e Breunigstein descrivono lo stesso segnale; Dux, Temiz, Breunigstein e Knight
danno **la stessa causa**: i compratori in ritardo restano intrappolati e diventano venditori
forzati. E il primitivo si misura **senza shortare e senza ipotesi di esecuzione**: basta
confrontare la distribuzione dei rendimenti futuri dopo il segnale con l'incondizionata.

**2. Due candidati testabili con costo quasi nullo e in famiglie NUOVE.**
- **Regola dell'1% sul VIX** (B1.4): due serie giornaliere, una condizione aritmetica. Famiglia
  "volatilita' implicita come segnale": **mai testata**, budget intatto.
- **Regimi con bande di Bollinger** (B1.3): un solo indicatore, zero giudizio visivo, sui nostri
  strumenti e sul nostro timeframe.

## "Non operare in mezzo": sei formulazioni indipendenti

Zhang (evita gli stage 1 e 3) · Breunigstein (solo se esteso) · Crooks (contro-trend solo se esteso)
· Desano (no trade zone) · **Crudele** (*"opera sui bordi, stai fuori dal mezzo"*) · **Knight**
(*"da bordo a bordo, in mezzo non c'e' nessuno"*).

Sei trader, sei vocabolari, strumenti e timeframe diversi, **una sola regola**. E' la convergenza
piu' robusta del funnel, ed e' testabile senza discrezionalita'.

## Statistiche dichiarate del blocco

| fonte | claim | BS-test |
|---|---|---|
| TG Capital | 90% win a 1:20 | **+17,9R/trade = 58× il nostro miglior lead**. E senza stop fisso il claim **non e' ben formato** |
| Temiz | 98% win, ~4 volte l'anno | non implica rendimenti impossibili (bassa frequenza); implausibile per **precisione su campione piccolo** |
| Crudele | **nessun numero** | niente da testare — terza fonte "onesta" con Zhang e Ashraf |
| O'Neal | nessun win rate; un trade 6:1 | claim di contesto non verificato (90% del volume algoritmico) |
| Knight | "sette figure" | nessun claim di strategia |
