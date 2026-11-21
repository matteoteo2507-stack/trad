---
titolo: "I3 Struttura fra asset: proprieta', bersaglio, perdita, benchmark e piano della potenza (passo 2)"
data: 2026-11-21
tipo: controllo
stato: quarantena
---

# I3 — passo 2: cosa si misura, contro cosa, con quale potenza

Passo 2 della procedura per le famiglie di strumenti ([STRATEGY_LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md),
"Procedura"), dopo il [controllo delle grandezze](grandezze_I3_struttura_2026-11-21.md) e l'apertura di I3 (DECISIONS
2026-11-21 (2)). Le scelte marcate **(Matteo)** sono sue, del 21/11, fra opzioni proposte da Claude. **Nessun dato letto**
(solo le date di copertura di `motore/data/prezzi/dukascopy_d1/_coverage.csv` e del README dei dati): 0 trial.

## 1. Classe

**Nessuna: la correlazione e' una misura di rischio** (Matteo, D3 del 21/11), come la volatilita' nel modulo 10 §2. Un
"chi paga" si cerca solo per un'eventuale sottofamiglia di premio (per esempio la correlazione implicita contro la
realizzata), che oggi non e' nel perimetro.

## 2. Lo strumento e la proprieta'

**Lo strumento.** Una previsione, fatta con i soli dati fino alla chiusura di oggi, della matrice di dipendenza fra i
rendimenti di N strumenti nei prossimi **1 e 5 giorni** di borsa (Matteo: come la volatilita').

**Il bersaglio, scritto in modo che la misura sia corretta.** Per ogni strumento i il rendimento intraday r_i si divide
per la volatilita' dell'**ingresso fisso** (EWMA λ = 0,94, decisione D2 del 21/11) calcolata con i dati fino a ieri:
z_i = r_i / σ̂_i. Il bersaglio e' la **matrice di covarianza dei rendimenti standardizzati z** nel periodo previsto.
Se l'ingresso fisso fosse esatto sarebbe la matrice di correlazione; scritto cosi', la misura realizzata (somma dei
prodotti incrociati di z) e' **senza distorsione per costruzione**, che e' la condizione perche' la perdita ordini i
modelli come il bersaglio vero (sezione 3). Tutte le previsioni confrontate usano lo stesso σ̂, quindi differiscono solo
nella dipendenza: e' la regola delle grandezze composte (LIFECYCLE §3).

**La proprieta'.** La previsione ha una perdita di Stein piu' bassa del benchmark, fuori campione.

**Cosa NON si misura.** Nessun rendimento, nessuna regola di allocazione o di copertura: il passaggio a un portafoglio o
a un hedge lo testano i soci. La volatilita' di ogni strumento non si valuta (e' l'ingresso fisso).

## 3. Misura realizzata (Matteo: intraday)

Correlazione realizzata da barre intraday **nelle ore comuni**, sugli M5 Dukascopy. Proposte di Claude, da fissare
prima di ogni dato (passo 3):
- **finestra comune**: la seduta cash USA, 9:30-16:00 New York, in cui sono aperti tutti gli strumenti dell'universo (da
  verificare sulla struttura dei file, solo conteggi di barre, per ogni strumento; il DAX solo se il CFD e' quotato in
  quelle ore);
- **frequenza**: rendimenti a **15 minuti** (26 per seduta), con la correzione per un ritardo (somma dei prodotti
  incrociati a ritardo 0 e ±1) contro l'effetto Epps delle quotazioni non sincrone. Fissata ora, non scelta guardando i
  dati: una scelta fatta su un grafico della correlazione per frequenza sarebbe una variante (C3);
- **giorni**: le stesse regole della volatilita' per i giorni incompleti (meno del 90% delle barre: escluso, e si conta);
- **dal 2015** (dal 2012 al 2014 il feed degli indici ha barre ferme anche in seduta, motore/data/README).

## 4. Perdita (Matteo: Stein)

Perdita primaria **di Stein**, la QLIKE multivariata: L(H, Σ) = tr(H⁻¹Σ) − log det(H⁻¹Σ) − N, con H la previsione e Σ
la misura realizzata. Secondaria la **Frobenius** (errore quadratico su ogni elemento), solo come lettura. Fonti, **in
quarantena** (lette solo nelle sintesi del motore di ricerca il 21/11, testi da leggere prima della bozza):
- Laurent, Rombouts, Violante (2013), *Journal of Econometrics* 173, 1-10: condizioni sulla forma di una perdita
  multivariata perche' l'ordinamento dei modelli resti quello vero quando il bersaglio e' misurato con rumore
  ([EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:173:y:2013:i:1:p:1-10));
- Patton, Sheppard (2009), "Evaluating Volatility and Correlation Forecasts": generalizzazione multivariata delle
  perdite robuste; nelle loro simulazioni la QLIKE ha la potenza maggiore
  ([ORA Oxford](https://ora.ox.ac.uk/objects/uuid:474e796d-5656-4e6b-94d3-b10125785fc5/files/mba0ba07178c0b21e3528d52e99430bd0)).

Da verificare sul testo: che Stein e Frobenius siano nella classe che conserva l'ordinamento con un proxy non distorto;
le condizioni su H (definita positiva) e su Σ (con 26 rendimenti per seduta e N strumenti, Σ di un giorno e' singolare
se N > 26: la perdita di Stein richiede H invertibile, non Σ, ma va controllato).

## 5. Benchmark (Matteo: EWMA 0,94)

- **Benchmark del verdetto**: correlazione **EWMA con λ = 0,94** sui rendimenti standardizzati (RiskMetrics): nessun
  parametro stimato, stesso ingresso fisso.
- **Riferimenti di skill** (G3): correlazione **costante** di lungo periodo (finestra mobile di lunghezza fissa) e
  **persistenza** (la matrice realizzata di ieri, regolarizzata se singolare).
- **Benchmark forte**: **DCC(1,1)** sui rendimenti standardizzati, con lo stesso primo stadio fisso.
- **Combinazione semplice** fra i candidati (G3), da elencare con le varianti al passo 3.

I candidati (PCA a k fattori con k da una regola fissata prima, contrazione verso la correlazione costante,
raggruppamenti, regimi) si elencano al passo 3, con le sottofamiglie e le quote d'errore.

## 6. Universo e dati

**In casa**: 9 strumenti M5 Dukascopy fino al 2026-11-11 (SPX500, NAS100, DOW, RUSSELL, DAX, XAUUSD, XAGUSD, WTI,
EURUSD). Sono **5 classi** (azioni USA, azioni Europa, metalli preziosi, energia, cambi), e le quattro azioni USA si
muovono quasi insieme (A1 §4: ρ medio degli indici +0,791 sul pool D1): per la dipendenza fra classi e' poco.

**Da aggiungere, gratis** (regola d'acquisto, backlog §G: prima si esaurisce il gratuito), scelti **per classe, prima
di ogni dato**: dallo stesso fornitore Dukascopy M5, con lo stesso script della volatilita':
- obbligazioni: BUND, USTBOND (dal 2016 e dal 2018 nel D1; sotto i due anni di sviluppo dal 2015, da verificare);
- cambi: USDJPY, GBPUSD, AUDUSD (le majors meno legate a EURUSD);
- metalli industriali ed energia: COPPER, NATGAS;
- crypto: BTCUSD (24 ore, dal 2017).
Gli agricoli restano fuori: le loro ore di contrattazione non coprono la finestra comune per intero. **L'elenco e' una
proposta**: lo fissa Matteo al passo 3, e ogni strumento si conta nel contatore come serie (C1).

**Acquistabili** (non servono finche' il gratuito non e' esaurito): futures intraday sincroni (Databento, FirstRate),
che toglierebbero il problema delle quotazioni non sincrone dei CFD; i futures a 1 minuto dei soci coprono un anno solo
(2025-11 → 2026-11) e possono servire come conferma su dati veri di borsa, non come storia.

## 7. Dati gia' visti e blocchi sigillati

- **Blocco 2024-11-11 → 2026-11-10 degli M5** (holdout sigillato della volatilita', mai piu' usabile dal suo ridisegno):
  **I3 lo legge, dichiarandolo** (Matteo). Dichiarazione: da questo referto in poi il blocco e' "toccato dalla pipeline"
  per i nove strumenti; una fonte comprata in futuro che lo copra non conta piu' come mai toccata (nota N3, DECISIONS
  2026-11-20 (2)). I3 non calcola e non riporta nessuna statistica di volatilita' su quel blocco (LIFECYCLE §8ter,
  "Ingresso fisso da un'altra famiglia").
- **Strumenti nuovi** (sezione 6): sono anche candidati "mai visti" per il ridisegno della volatilita'. I3 li usa solo
  standardizzati e non calcola statistiche di volatilita'; se contino ancora come mai visti lo decide la
  pre-registrazione del ridisegno, e questo referto lo dichiara.
- **Correlazioni medie per classe** gia' calcolate (A1 §4, §8, §9; elenco nel controllo delle grandezze): sono su dati
  D1, non sulla misura intraday di I3, ma la loro conoscenza si dichiara.

## 8. Piano della potenza (prima di raccogliere)

L'MDE (G6) e' il differenziale di perdita di Stein che il test puo' vedere all'80%. Proposta, da far giudicare al
gatekeeper prima di calcolare:
- **dati**: solo lo sviluppo **prima del 2024-11-11** (il blocco dopo resta disponibile come holdout di I3, che si fissa
  al passo 3);
- **cosa si calcola**: la serie giornaliera del differenziale di perdita fra il **benchmark EWMA e il riferimento
  costante**, cioe' fra due serie che non sono candidati del test, come stima della dispersione di un differenziale
  realistico; da questa la deviazione HAC e l'MDE per orizzonte, col fattore della procedura (test a una coda, quota
  d'errore del nodo, Holm se piu' universi);
- **cosa non si calcola**: nessuna previsione dei candidati, quindi nessun trial (C1). Se il gatekeeper ritiene che
  anche il riferimento costante conti, lo si conta;
- **prima della corsa**: commit del codice e delle guardie (sha256 dei file, nessuna data oltre il 2024-11-08 letta
  per l'MDE), come per la volatilita'.

## Decisioni di Matteo del 21/11 (passo 2)

Misura intraday con orizzonte 1 e 5 giorni; perdita di Stein; benchmark EWMA 0,94; il blocco sigillato degli M5 si
legge, dichiarandolo. Restano da fissare al passo 3: finestra, frequenza, universo, sottofamiglie, varianti, quote,
holdout.

## Revisione del gatekeeper

*(da compilare)*
