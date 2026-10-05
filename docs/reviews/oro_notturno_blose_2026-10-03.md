---
stato: chiuso all'intake
aperta: 2026-10-03
chiusa: 2026-10-03
verdetto: CHIUSO all'intake, 0 trial — condizione (a) del §4 non soddisfatta; (b) e (c) non verificabili
trial: 0
---

# Oro: rendimenti notturni positivi e diurni negativi (Blose et al.) — revisione d'intake

> **Revisione d'intake, non un test.** Costo: **0 trial**. Nessun dato nostro e' stato
> aperto per rispondere a questa domanda. Lo stato canonico della fonte e' la riga in
> [`_INTAKE.md`](../../fondamenti_tecnici/_INTAKE.md); qui stanno il ragionamento e il verdetto.

## 1. Da dove nasce

Ricerca del 29/09 ([§X3](ricerca_X_dati_oro_2026-09-29.md)), poi la sessione di brainstorming del
03/10. In quella sessione l'ho proposto come **primo test di un premio per il rischio**, invece che
di una regola di tempismo. Era una lettura sbagliata: vedi §3, punto 3.

## 2. Cosa dice la fonte (letto il 03/10: solo gli abstract, il testo completo e' a pagamento)

- **Blose, Gondhalekar, Kort, *J. Econ. Finance* 42(3), 2018, pp. 526-549**
  ([abstract](https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html)).
  Notti **positive** e giorni **negativi** su futures COMEX (primo mese), London Fix, azioni minerarie,
  fondi chiusi ed ETF sull'oro. Presente sia nei mercati al rialzo sia in quelli al ribasso.
  Spiegazione degli autori: il prezzo e' **(troppo) alto all'apertura** dei vari mercati.
  *"Economicamente importante anche coi costi di transazione"*, ma le grandezze non sono nell'abstract.
- **Blose, Gondhalekar, *Applied Economics Letters* 21(18), 2014**
  ([abstract](https://ideas.repec.org/a/taf/apeclt/v21y2014i18p1269-1272.html)): COMEX 1985-2012.
  *"L'asimmetria si e' indebolita sostanzialmente negli anni, ma e' ancora presente."*
- Sono gli **stessi autori**: per [[feedback_conferme_per_fonte]] contano come **una fonte**.

## 3. Cosa indebolisce il candidato (prima del testo completo)

1. **Il meccanismo dipende da un'apertura.** "Prezzo troppo alto all'apertura" richiede un mercato
   che **apre**: un'asta o l'inizio della sessione COMEX o dell'ETF. Il CFD sull'oro scambia in continuo
   ~23 ore su 24 e non ha un'asta d'apertura: li' "l'apertura" e' un orario che scegliamo noi. Su
   XAUUSD testeremmo un'**ipotesi diversa** (deriva oraria dello spot continuo). Stessa forma di B3:
   valida sul loro universo, **non trasferibile** al nostro senza un argomento nuovo.
2. **Una parte dell'effetto e' un artefatto d'esecuzione**, da due fonti indipendenti:
   - [QuantPedia](https://quantpedia.com/dangers-of-relying-on-ohlc-prices-the-case-of-overnight-drift-in-gdx-etf)
     su GDX: eseguendo alle 9:31 coi dati a 1 minuto l'effetto si riduce molto rispetto al prezzo
     d'apertura dei dati giornalieri;
   - [Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly)
     su SPY: i costi di transazione cancellano l'anomalia.

   E' il **fill fantasma** ([QUANT_REVIEW_PROTOCOL Step 3bis](../QUANT_REVIEW_PROTOCOL.md)): il
   prezzo d'apertura di un dato OHLC non e' un prezzo a cui si poteva eseguire.
3. **Non e' un premio per il rischio.** "Prezzo troppo alto all'apertura" e' un errore di prezzo
   comportamentale, cioe' un'**anomalia di tempismo**: la categoria che abbiamo falsificato piu' volte.
4. **Decade gia' dentro il campione della fonte** (2014), e i nostri dati (XAU M1 2020-2026) partono
   almeno 8 anni dopo la fine di quel campione.

## 4. Criterio del verdetto — scritto PRIMA di leggere il testo completo

Il testo completo (via Comet) decide fra due esiti. Le condizioni sono queste e **non si toccano dopo**.

**Resta `verificabile` (diventa candidato a pre-registrazione esterna) solo se valgono TUTTE:**
- **(a)** l'effetto c'e' anche su una misura **senza asta d'apertura**, oppure su una con prezzo
  eseguibile: London Fix fix-to-fix, oppure spot o futures misurato a un orario fisso fuori dall'apertura;
- **(b)** l'ultimo sotto-periodo riportato dalla fonte ha l'effetto ancora **diverso da zero**,
  non solo "presente";
- **(c)** la grandezza netta dei costi dichiarata dalla fonte e' almeno dell'ordine di **qualche
  punto base al giorno**. La soglia esatta si fissa poi con l'MDE sui nostri dati, prima di qualunque
  test.

**Altrimenti: CHIUSO all'intake, 0 trial**, come *"meccanismo legato all'apertura, non trasferibile
al CFD continuo; in calo nella fonte; in parte artefatto d'esecuzione"*. La riapertura richiede un
risultato pubblicato su **oro spot continuo** con esecuzione a prezzo ottenibile.

**Se il testo completo resta irraggiungibile**, vale l'esito "chiuso". L'onere della prova sta sulla
fonte ([04_quant_metodologia](../../fondamenti_tecnici/04_quant_metodologia/principles.md): *"in caso di
verdetto ambiguo, default a NO-GO"*). Il motivo va scritto: **non verificabile**, non falsificato.

## 5. Cosa resta in ogni caso (0 trial, non e' una strategia)

**Il rendimento per ora del giorno sull'oro spot** (bid/ask M1 Dukascopy, gia' in casa: riga G1 del
[backlog](../BACKLOG_RICERCA.md)) come **misura descrittiva**. Serve da baseline "noioso" per i
segnali sull'oro. Il random di [`oos_validation.py:151`](../../analysis/mentor_signals/oos_validation.py#L151)
sceglie il lato 50/50: se il mentore compra piu' di quanto vende in un oro al rialzo, una parte del
vantaggio e' deriva, e quel baseline non la toglie. ⚠️ E' una misura, non una regola: non si
trasforma in un filtro orario dopo averla vista (stessa regola di B3).

## 6. Verdetto — **CHIUSO all'intake, 0 trial** (2026-10-03)

**Cosa ha trovato Comet (03/10), tre ricerche:**
1. **Paper 2018: testo completo non raggiungibile.** Springer a pagamento (39,95 USD); nessuna versione
   libera su Scholar, ResearchGate, ScholarWorks GVSU, SSRN. Visibili solo l'abstract e alcune note:
   - il London **PM** fix e' usato in almeno parte dell'analisi;
   - il COMEX ha chiuso la viva voce sull'oro a luglio 2015;
   - fino al 17/03/1992 il portafoglio minerario era **un solo titolo** (ASA, che investe anche in
     argento, platino e diamanti);
   - i costi sono commissioni intervistate presso 9 broker azionari e 9 broker futures retail
     (azioni 4,00-9,99 $; futures 1,00-9,70 $ a contratto). Spread, impatto e ritardo d'esecuzione
     sono citati come **non** inclusi.
2. **Articolo 2014: testo completo non raggiungibile.** Nessun numero sul calo dell'effetto oltre
   all'abstract.
3. **Repliche dopo il 2015 su oro spot continuo: nessuna.** L'unico lavoro pertinente,
   Iwatsubo-Watkins-Xu (RIETI DP 17-E-120, 2017; pubblicato nel 2018), usa bid/ask a 1 minuto di
   TOCOM e COMEX su 128 giorni (09/2014-03/2015). Studia **microstruttura, non rendimenti medi**:
   volatilita' massima alle aperture di Tokyo, Londra e New York; volume COMEX massimo
   all'apertura di New York.

**Applicazione del §4:**
- **(a) NON soddisfatta.** Tutte le misure della fonte sono definite su **aperture, chiusure o
  fixing**, e il fixing di Londra e' a sua volta un'asta. Nessuna e' una misura senza apertura su
  un mercato continuo. Lo dice gia' l'elenco degli asset nell'abstract (futures di sessione, fix,
  azioni, fondi chiusi, ETF): **il verdetto non dipende dal paywall**, e comprare l'articolo non
  lo cambierebbe.
- **(b) non verificabile:** l'unico dato e' l'abstract del 2014, *"si e' indebolita sostanzialmente"*.
- **(c) non verificabile:** i costi della fonte sono solo commissioni retail. Lo spread e il fill
  ottenibile, cioe' il punto in cui altre due fonti vedono l'effetto sparire (§3.2), non sono
  inclusi.

**Formula:** *meccanismo legato all'apertura, non trasferibile al CFD continuo; in calo nella
fonte; in parte artefatto d'esecuzione su altre classi*. **Non falsificato**: nessun nostro dato e'
stato aperto. Non c'e' MDE perche' non c'e' stato test.

**Condizione di riapertura:** un risultato pubblicato su **oro spot continuo (o futures sulla
sessione elettronica 24 ore)**, misurato a orari fissi con prezzi eseguibili (bid per vendere, ask
per comprare) e al netto dello spread.

**Cosa resta:** la misura descrittiva del §5, proposta e **non decisa**. Iwatsubo-Watkins-Xu ne e'
il riferimento di metodo: sessioni Tokyo/Londra/New York esplicite, midquote a 1 minuto, spread per
fascia oraria. Nell'attesa resta aperta una sola osservazione: lo spread dell'oro **cambia per fascia
oraria** (RIETI; e §X2 della [ricerca del 29/09](ricerca_X_dati_oro_2026-09-29.md)). Qualunque deriva
oraria che misurassimo andrebbe letta **al netto dello spread di quella fascia**.
