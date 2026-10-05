---
tipo: revisione
data: 2026-10-03
trial: 0
esito: "nessun candidato testabile a potenza utile; due voci chiuse all'intake (regola dell'1% sul VIX, carry FX); una voce del backlog superata da una decisione piu' recente"
---

# Ricerca nel repo dopo la chiusura di oro notturno e COT (03/10)

> Richiesta di Matteo (03/10): *"fai una ricerca approfondita nel repo se trovi qualcos'altro"*.
> Lette per intero o per le parti di stato: [BACKLOG_RICERCA](../BACKLOG_RICERCA.md), le sintesi dei
> due funnel (Chart Fanatics e Quant Guild) e i blocchi A1, A2, B1, la pipeline di strategie del
> 02/05 (memoria), i blueprint, le strategie candidate, l'intake, l'audit A5. **0 trial**: nessun
> esito di strategia e' stato calcolato; l'unico calcolo e' un **conteggio di eventi** (§1).

## 1. Regola dell'1% sul VIX (funnel B1.4) — **CHIUSA all'intake, 0 trial**

**Cosa dice la fonte** ([blocco-B1 §B1.4](../../fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/blocco-B1.md),
Dylan O'Neal, un solo trader, nessun campione). Se in un giorno l'S&P sale di almeno l'1% **e** il VIX sale di
almeno l'1%, l'S&P difficilmente tiene i massimi. Speculare: entrambi giu' di almeno l'1% → rimbalzo
probabile. Nel funnel era *"il test piu' economico"*, famiglia nuova (volatilita' implicita come segnale).
Aveva un argomento vero a favore: e' l'unica regola del catalogo che usa **informazione esterna al prezzo**
(il mercato delle opzioni), mentre tutte quelle cadute usavano il prezzo dello strumento stesso.

**Perche' si chiude:**
- **Potenza.** VIX CBOE (`data/cache/free/VIX_D1.csv`) incrociato con SPX500 D1 Dukascopy, 2012-01-18 →
  2026-08-13 (14,6 anni, 3.695 giorni comuni). Eventi: **19 al rialzo e 16 al ribasso**. ⚠️ Il conteggio e'
  approssimato: la chiusura del CFD e quella del VIX non coincidono. Con la deviazione standard giornaliera
  di tutti i giorni (1,03%, che **sottostima** quella dei giorni di evento), l'MDE sul rendimento medio del
  giorno dopo e' **0,49%** sui 35 eventi insieme (0,66% e 0,72% per lato), e **1,09%** a 5 giorni. Anche con
  la storia dell'S&P dal 1990 gli eventi resterebbero nell'ordine di qualche decina.
- **Una misura esterna gia' fatta, su un insieme piu' largo.** [Macroption](https://www.macroption.com/vix-spx-same-direction)
  (1990-2013): sui 20 e sui 100 giorni con il rialzo dell'S&P piu' grande **e** VIX in salita, il giorno dopo
  l'S&P fa in media **+0,01%** e **−0,07%**: *"nessun vantaggio direzionale"*. Un effetto 7 volte piu' piccolo
  del nostro MDE.
- **Il modo di fallire dichiarato dalla fonte e' il regime di oggi.** La fonte stessa dice che sui massimi
  storici il VIX risale perche' le coperture costano poco (falso segnale). Cboe descrive esattamente questo
  meccanismo per il 2026 (*"spot up, VIX up as investors hedge record highs"*).

**Riapertura:** una misura pubblicata con campione che mostri un effetto **condizionato al filtro dell'1%** di
almeno qualche decimo di punto al giorno.

## 2. Carry FX (pipeline del 02/05, voce 7) — **CHIUSO all'intake, 0 trial**

E' il premio per il rischio che avevo **dimenticato** nella voce DECISIONS 2026-10-03 (3), dove ho scritto che
i premi alla portata del retail sono "gia' presi o fuori perimetro". Il carry e' alla portata: il broker lo
passa, almeno in parte (sotto). Si chiude per un altro motivo.

- **Il premio e' sparito dopo il 2008, secondo due fonti indipendenti.**
  - Fan et al. 2022, *J. Int. Financial Markets, Institutions & Money* 76: declino del carry dopo la crisi
    del 2008, attribuito alla sparizione del rischio di ribasso
    ([abstract](https://ideas.repec.org/a/eee/intfin/v76y2022ics1042443121001670.html)).
  - Citi, via [Reuters del 15/05/2026](https://www.reuters.com/markets/wealth/carry-trading-rate-based-g10-currency-bets-make-comeback-2026-05-15):
    *"dalla crisi finanziaria il carry sui paesi sviluppati non ha fatto soldi"*. Il +4% del 2026 fino a maggio
    e' un anno solo.

  I nostri dati FX (Dukascopy D1) partono dal **2012**: tutta la finestra e' dopo la crisi, cioe' dove le fonti
  vedono un premio vicino allo zero. Con 14,6 anni l'MDE sullo Sharpe e' 2,80/√14,6 = **0,73**, contro un premio
  atteso vicino a 0.
- **Cosa passa il broker, letto in MT5 il 03/10.** E' una fotografia di un giorno, non una storia: lo storico
  degli swap non esiste.
  - **USDJPY:** swap long +9,37 punti a notte, short −14,84. Su 1 lotto sono circa **+2,3% l'anno** di
    nozionale in incasso, contro circa **−3,7%** a pagamento. La forbice di ~1,4 punti e' il ricarico del broker.
  - **AUDJPY:** long circa +2,8% l'anno.
  - **Emergenti:** il carry **non passa**. Short USDMXN incassa circa 0,6% l'anno e il long paga circa 4,9%;
    USDZAR e USDTRY hanno la stessa forma.

  Questi numeri sono **stime mie**, convertite a mano dai punti, con i cambi a valori approssimati.

**Riapertura:** evidenza pubblicata di un premio G10 dopo il 2008 con Sharpe vicino a 0,5 su piu' anni,
non uno solo.

## 3. Le altre voci trovate, e perche' non si aprono

| voce | dove | stato | perche' non si apre |
|---|---|---|---|
| **Faccia speculare di A1**: la mean reversion ordinata all'inverso per volatilita'/liquidita' | blocco-A1 §cosa emerge | segnata *"mai misurata"* | **gia' vista due volte nel campione**: meanrev_vol (07/08: positiva sui *ranger*, negativa sui *trender*) e B1 (17/09: energy/index/fx_cross ritornano, crypto/agri continuano). Un test avrebbe la stessa barriera di A1: **pochi strumenti indipendenti** ([referto A1 §8](../TREND_A1_HELDOUT_POWER.md)) |
| Stage analysis (A1.4), persistenza condizionata (A1.5), uscita ibrida a tre stadi (A1.1) | blocco-A1 | candidati del funnel | famiglia `trend_momentum`: l'unico round rimasto (il 3) e' conteso fra B2 e A1 punto 3 (DECISIONS 2026-10-03) |
| Volume anomalo come segnale (A2.2) | blocco-A2 | *"mai testato"* | dato inadatto: volume di tick, scorrelato da \|rendimento\| su 10 strumenti su 27 ([B3](../B3_EXTENSION_STRUCTURE_PROTOCOL.md)) |
| TSMOM e ORB NAS100 *"non misurati"* | audit A5 | caselle vuote, non chiuse | famiglie con holdout gia' aperto: si riaprono solo con evidenza esterna nuova (§7) |
| Buchi Quant Guild di priorita' 4 | SINTESI Quant Guild | prossimi in ordine | sono **metodo**, non strategie: servono quando il perimetro si allarga |
| NYSE scalping, Insider Constellation, Hermes, Markov | strategie candidate, blueprint | idee non committate | order flow/TPO intraday (D1), equity USA + segnali da agenti, ottimizzatore auto-migliorante (ricerca di massa senza conto dei trial), regola di tempismo su indici |

## 4. Una voce del backlog superata da una decisione piu' recente (segnalata, non corretta)

Il [backlog](../BACKLOG_RICERCA.md) §G dice: *"Il piu' conveniente adesso: G1 (b)"*, cioe' stringere con i dati M1
la forbice di 0,82R fra le convenzioni del baseline del mentore XAT. Ma **DECISIONS 2026-10-02 (notte)** ha messo
XAT **in revisione**: lo storico e' selezionato (il canale cancella i perdenti), e la misura e' il **forward**. Un
replay piu' preciso di uno storico selezionato non misura piu' l'edge. Per la regola di `CLAUDE.md` vale la voce
piu' recente; la riga del backlog e' **vecchia**. La correzione la decide Matteo: o si declassa G1 (b), o si dice
a cosa serve ancora (per esempio a tarare il baseline del forward).

## 5. Lettura d'insieme

Dopo tre giorni di candidati (oro notturno, COT, VIX, carry) il quadro e' coerente: **nel perimetro attuale**
(CFD retail, capitale piccolo, dati liberi) **non c'e' un'ipotesi testabile a potenza utile che non sia gia'
chiusa**. Le cause si ripetono:
- **pochi strumenti indipendenti:** A1, la faccia speculare di A1, COT;
- **pochi eventi:** VIX;
- **premio sparito o non operabile:** carry, COT;
- **meccanismo non trasferibile:** oro notturno.

E' un esito sul **perimetro**, non sul metodo. Le leve che lo sposterebbero sono gia' scritte e costano:
- piu' strumenti indipendenti con storia (G9, ma lo scenario onesto resta fuori scala di ~3×);
- un conto futures con capitale adeguato;
- il tempo, cioe' i forward: XAT dal 05/10 e Gump.
