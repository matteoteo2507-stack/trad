---
titolo: "Candidato A — mean reversion giornaliera sugli indici USA: potenza prima della pre-registrazione"
tipo: referto
creato: 2026-10-08
stato: quarantena
trial: 0
---

# Candidato A — mean reversion giornaliera sugli indici: potenza (0 trial)

**Scelto da Matteo il 08/10** come primo candidato di ricerca dopo il collaudo. Questo e' il **primo passo**: contare
i segnali e calcolare quanta potenza c'e', **prima** di pre-registrare. Script:
[`analysis/meanrev_indici/potenza.py`](../analysis/meanrev_indici/potenza.py). Non calcola **nessun rendimento
successivo a un segnale**: conta i segnali e usa solo l'ATR al segnale (informazione nota prima). 0 trial.

## 1. Il candidato col metodo della fase RICERCA ([09_fonti_di_vantaggio](../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md) §4)

| domanda | risposta | stato |
|---|---|---|
| classe | reazione eccessiva (3) o fornitura di liquidita' (2): chi deve vendere in fretta nei giorni di stress paga chi compra | da confermare con le fonti del §6 |
| chi paga, limite all'arbitraggio | chi si de-rischia per vincolo (margini, mandati); serve capitale proprio proprio quando il rischio e' massimo, con coda sinistra nei crolli | idem |
| dove si vede | indici azionari, barre giornaliere, tenuta di pochi giorni | — |
| accessibilita' | CFD US100/US500 su MT5. Prop: FTMO **Swing** (overnight e weekend consentiti, leva 1:30); FundedNext da 100k vieta gli EA. **Swap long** da misurare in MT5 | da misurare |
| provenienza | fonte umana esterna (video 2 della sessione col socio; Connors-Alvarez 2008 come riferimento classico) → consumerebbe il **secondo slot** di pre-registrazione esterna del 2026-Q4 | — |
| **contaminazione** | questi dati li abbiamo **gia' visti due volte**: mean reversion vol (08/07, positiva da sola sugli indici) e B1 (17/09, gruppo index +0,047 al 99,7° percentile, D1 2012-2026). Sulla storia il massimo ottenibile e' un **LEAD** | — |

## 2. Potenza (08/10)

Dati Dukascopy D1, SPX500 16/01/2012 → 13/08/2026 e NAS100 19/01/2012 → 13/08/2026 (14,6 anni, domeniche escluse).
Un episodio = primo giorno di una sequenza di segnali nella stessa direzione; lo stesso giorno su entrambi gli indici
conta una volta. Variabilita' di un trade: ATR(14) al segnale / 1,4 × √3 giorni (ipotesi dichiarata), mediana ~1,5%.
MDE = 2,80 × sigma / √eventi.

| regola | eventi indipendenti | all'anno | MDE sulla storia intera |
|---|---|---|---|
| R1 RSI(2) < 10 long / > 90 short | 784 | 53,8 | **0,16%** a trade |
| R2 RSI(2) < 10 sopra la media a 200, solo long (forma di Connors) | 202 | 13,9 | 0,30% |
| R3 chiusura fuori dalla Bollinger(20, 2) | 328 | 22,5 | 0,25% |

**Anni di forward** per vedere un effetto E (lordo, % per trade):

| regola | E = 0,10% | E = 0,20% | E = 0,30% | E = 0,50% |
|---|---|---|---|---|
| R1 | 36 | 9 | 4 | 1,4 |
| R2 | 128 | 32 | 14 | 5,1 |
| R3 | 89 | 22 | 10 | 3,6 |

Costi da sottrarre (stime, **da misurare**): spread trascurabile su D1; lo **swap long** su un CFD indice costa
dell'ordine dello 0,02% a notte, cioe' ~0,05-0,07% su una tenuta di 3 notti. Un effetto lordo di 0,30% diventa ~0,23%
netto: R1 in forward ~7 anni, R2 ~26.

## 3. Lettura

1. **Sulla storia** si vedrebbe un effetto di 0,16% (R1), ma il test e' **contaminato**: sappiamo gia' che sugli indici
   il ritorno alla media era visibile (B1). Un esito positivo era quasi scontato e varrebbe al massimo un LEAD; un esito
   negativo sarebbe informativo, ma e' il meno probabile.
2. **In forward** il test e' pulito ma lento: con due indici molto correlati gli eventi indipendenti sono ~54 l'anno
   (R1) o ~14 (R2). Serve un effetto netto vicino allo 0,5% per stare sotto i due anni.
3. Quale effetto aspettarsi **non lo diciamo noi**: va preso da una fonte pubblicata, sul numero originale e sulla sua
   meta' (09 §4.7; il decadimento dopo la pubblicazione e' documentato da McLean-Pontiff, da confermare). Oggi non ce
   l'abbiamo: i numeri di Connors-Alvarez sono nella mia memoria, non verificati.

## 4. Cosa serve per decidere (a Matteo)

- **L'effetto pubblicato** di RSI(2) sugli indici, originale e in una replica dopo il 2008, con campione e costi: lavoro
  da Comet (prompt nella risposta del 08/10).
- **Lo swap long** di US100/US500 sul conto che useremmo (specifiche del simbolo in MT5).
- **Piu' indici, meno correlati** (Europa, Asia) per moltiplicare gli eventi indipendenti in forward: oggi nel feed
  libero Dukascopy D1 ci sono solo SPX500 e NAS100 (G9 per gli altri).

Con questi tre dati si sceglie fra: (a) test sulla storia pre-registrato sapendo che vale al massimo un LEAD; (b) solo
forward, piu' indici, regola R1; (c) chiudere A a 0 trial per potenza, come COT e carry il 03/10.

## 5. Effetto pubblicato (Comet, 08/10) e potenza ricalcolata

Fonte integrale: [rsi2_fonti_comet_2026-10-08](reviews/rsi2_fonti_comet_2026-10-08.md) (statistiche di terzi, usate solo
come effetto atteso). Effetto per trade sulla regola **R2** (sopra SMA 200, RSI(2) < 10), SPY:

| fonte | campione | effetto per trade | come |
|---|---|---|---|
| QuantifiedStrategies | 1993-2026 | 0,90-0,95% | dichiarato |
| BacktestEverything | 2000-2024, 387 trade | **0,75%** | ricavato: 0,73 × 1,8 − 0,27 × 2,1 |
| Quantitativo | 1999-2024 | 0,60%, **sotto l'S&P dal 2014** | dichiarato |
| Murtazin (GuruFinanceInsights) | 2000-2026, 181 trade | **0,51%** | ricavato: $1 → $2,49 in 181 trade |
| Quant4Free | singole azioni S&P 1500, 2015-2026, netto 10 bps | PF 0,99: **zero** | universo diverso (azioni, non indice) |

Controllo della mia stima: da BacktestEverything la dispersione per trade e' **1,73%** contro l'1,50% stimato con l'ATR:
la stima era leggermente ottimista (anni × ~1,33).

**Anni di forward per R2 su SPX500 + NAS100** (13,9 eventi indipendenti l'anno, sigma 1,50%, swap ~0,06% sottratto):
0,90% → 1,8 anni · 0,75% → 2,7 · 0,60% → 4,4 · 0,51% → 6,4 · **meta' di 0,60% (decadimento dal 2014) → 22 anni**.
Con sigma 1,73% un terzo in piu'. **Sulla storia 2012-2026** l'MDE di R2 e' 0,30%: sotto l'effetto pubblicato, attorno
alla sua meta'.

**Tre fatti che pesano piu' dei numeri:**
1. **Tutte le fonti testano la regola SENZA stop-loss** (o con un time stop a 10 giorni): il vantaggio dichiarato vive
   in un win rate alto con perdite piu' grandi delle vincite (payoff ~0,5-0,9). Una versione da prop, con uno stop che
   rispetti la perdita giornaliera, e' una **regola diversa** che nessuna fonte ha misurato.
2. **E' lenta**: 7-16 trade l'anno su un indice. A rischio 1% per trade, per fare +10% servono decine di trade, cioe'
   anni; FTMO non ha limite di tempo, ma la challenge diventa un investimento pluriennale.
3. **Il decadimento** dal 2014 (Quantitativo, QuantifiedStrategies) e lo zero di Quant4Free sulle singole azioni
   indicano che l'effetto vero oggi e' piu' vicino alla meta' che al numero pubblicato: allora il forward e' fuori scala.
