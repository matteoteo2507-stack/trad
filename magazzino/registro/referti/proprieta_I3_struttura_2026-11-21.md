---
titolo: "I3 Struttura fra asset: proprieta', bersaglio, perdita, benchmark e piano della potenza (passo 2)"
data: 2026-11-21
tipo: controllo
stato: quarantena
---

# I3 — passo 2: cosa si misura, contro cosa, con quale potenza

Passo 2 della procedura per le famiglie di strumenti ([STRATEGY_LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md),
"Procedura"), dopo il [controllo delle grandezze](grandezze_I3_struttura_2026-11-21.md) e l'apertura di I3 (DECISIONS
2026-11-21 (2)). Le scelte marcate **(Matteo)** sono sue, del 21/11 (DECISIONS 2026-11-21 (5)). **Nessun dato di prezzo
letto** (solo le date di copertura di `motore/data/prezzi/dukascopy_d1/_coverage.csv` e il README dei dati): 0 trial.
Prima bozza (commit `5ad5b98`) bloccata dal gatekeeper (4 bloccanti, 8 riserve): questa versione le applica; elenco in
fondo.

## 1. Classe

**Nessuna: la correlazione e' una misura di rischio** (Matteo, DECISIONS 2026-11-21 (2)). Un "chi paga" si cerca solo
per un'eventuale sottofamiglia di premio (correlazione implicita contro realizzata), oggi fuori perimetro.

## 2. Lo strumento e la proprieta'

**Lo strumento.** Una previsione, fatta con i soli dati fino alla chiusura della seduta di oggi, della **matrice di
correlazione** dei rendimenti di N strumenti nella seduta USA dei prossimi **1 e 5 giorni** di borsa (Matteo).

**La proprieta'.** La previsione ha una perdita di Stein piu' bassa del benchmark EWMA, fuori campione.

**Cosa NON si misura.** Nessun rendimento, nessuna regola di allocazione o di copertura (i soci). La volatilita' di
ogni strumento non si valuta: e' l'ingresso fisso.

**Cosa potra' dire il pacchetto ai soci.** "Previsione piu' accurata della correlazione **nella seduta USA**", non della
correlazione fra rendimenti di un giorno o di cinque giorni interi: mancano la notte e i ritardi fra un giorno e
l'altro.

## 3. Misura realizzata (Matteo: intraday)

Tutte le scelte qui sotto sono **fissate ora**, prima di ogni dato; il costo di un cambio segue **P6** (LIFECYCLE §8ter).
- **Finestra comune W**: seduta USA, 9:30-16:00 New York, secondo il calendario di borsa di New York (XNYS). Le barre
  Dukascopy (bid, ora d'inizio in UTC) si convertono all'ora di New York col fuso, quindi i cambi d'ora europei e
  americani non spostano la finestra; DAX e BUND, quotati su orari europei, si leggono comunque in ora di New York.
- **Due griglie** (DECISIONS 2026-11-23 (4) e 2026-11-24, prese insieme prima di ogni dato dopo le prove sintetiche,
  sezioni in fondo). **Griglia a 15 minuti**, per validita', conteggi e generatore dei difetti: il primo prezzo e'
  l'**open della barra M5 delle 9:30**, poi la **chiusura della barra M5 che finisce a ogni quarto d'ora** (quella che
  inizia alle :10, :25, :40, :55), fino alla chiusura della barra delle 15:55: 27 prezzi, 26 rendimenti. **Misura** (RV,
  D, s, Σ): **rendimenti a 30 minuti**, un prezzo su due della stessa griglia (14 prezzi: le barre che iniziano alle
  :25 e alle :55), 13 rendimenti per seduta piena. Un prezzo mancante rende mancanti i due rendimenti adiacenti della
  sua griglia (un prezzo a un quarto d'ora dispari non tocca i rendimenti a 30 minuti). *Fino al 23/11 la misura era a
  15 minuti; il 23/11 tutto era passato a 30 minuti, ma con 13 rendimenti la soglia del 90% (un solo prezzo mancante
  basta a superarla) e quella del 25% di nulli svuotavano il campione: controllo positivo GUASTO in 500 repliche su
  500.* **Un rendimento mancante vale zero in tutti i prodotti** (decisione del 21/11,
  DECISIONS (7)): la matrice di Bartlett resta semidefinita positiva per costruzione anche con buchi; la diagonale un po'
  piu' bassa la assorbe il fattore di scala, uguale per tutte le previsioni.
- **Correzione per due ritardi** con **pesi di Bartlett** (2/3 sui prodotti incrociati a ritardo ±1, 1/3 a ritardo
  ±2; *fino al 23/11 un ritardo, ½*) **su tutta la matrice, diagonale compresa**: toglie parte dell'effetto Epps delle quotazioni non sincrone e garantisce una matrice
  semidefinita positiva. Dopo la correzione resta un Epps residuo, uguale per tutte le previsioni: il bersaglio e'
  l'attesa di **questo** stimatore, non la correlazione vera, e va detto.
- **Giorni**: le sedute piene del calendario XNYS. Le **chiusure anticipate** (13:00) sono escluse e si contano. Un
  giorno entra solo se **tutti** gli N strumenti hanno almeno il 90% dei 26 rendimenti a 15 minuti attesi: si esclude l'unione dei
  giorni mancanti, e si riporta per anno e per strumento quanti giorni esclude (controllo di selezione, come la
  volatilita': per ogni giorno escluso si riporta il rendimento assoluto della seduta contro la mediana, per vedere se le
  esclusioni coincidono con i giorni estremi).
- **Quotazioni ferme**: un rendimento a 15 minuti **osservato** ed esattamente nullo si conta; uno strumento-giorno con
  piu' del 25% di rendimenti nulli **fra quelli osservati** conta come mancante (un rendimento mancante, che vale zero
  solo nei prodotti, non e' un rendimento nullo: la quota si conta prima di mettere gli zeri, cosi' un buco non pesa due
  volte) (un prezzo fermo spinge la correlazione verso zero). La quota per strumento e per
  anno si misura nel controllo di struttura, prima di ogni statistica.
- **Rollover** dei CFD su futures (BUND, USTBOND, COPPER, NATGAS, WTI): il rendimento a 30 minuti che attraversa
  l'ora di un cambio di contratto si toglie **nel loader**, una volta sola, con le date del calendario del fornitore.
  Se il calendario non si trova si assume che il cambio avvenga **alla riapertura serale**, fuori dalla seduta USA,
  come verificato per il WTI di Dukascopy (DECISIONS 2026-11-13, salti alla riapertura del giorno 19): lo strumento
  resta, l'ipotesi e' dichiarata, e il controllo di struttura riporta per ogni strumento dove cadono le pause di
  quotazione (solo orari, nessun rendimento). **Se una pausa o una riapertura cade dentro W**, ogni giorno si toglie il
  rendimento a 30 minuti che la attraversa (vale come mancante); lo strumento resta se rispetta le soglie (DECISIONS (7)).
- **DAX**: entra solo se il controllo di struttura mostra barre nel 90% delle sedute per tutta la finestra (dopo le
  11:30 di New York e' fuori dalla seduta cash di Francoforte); altrimenti resta fuori.
- **Strumento fuori**: se nello sviluppo i suoi giorni mancanti (meno del 90% dei rendimenti, o oltre il 25% di
  rendimenti nulli) superano il 10% delle sedute XNYS, lo strumento esce dall'universo, deciso una volta sul controllo
  di struttura e prima di ogni perdita (con l'esclusione per unione, uno strumento spesso fermo cancellerebbe giorni a
  tutti).
- **Calendario**: XNYS di `exchange_calendars`, versione registrata nelle guardie (come la volatilita').
- **Controllo di struttura**: conteggi su sviluppo e blocco. Per il G9 (§9, N2) si prendono **solo dallo sviluppo**,
  per strumento e per anno: sedute mancanti per intero, prezzi mancanti per ciascuno dei 27 orari della seduta, quota
  di rendimenti nulli **fra quelli osservati** e lunghezza media delle serie di rendimenti nulli consecutivi. Nessuna
  RV, nessuna media di rendimenti, nessun livello di prezzo. Il controllo di selezione (rendimento assoluto dei giorni
  esclusi contro la mediana) si fa **solo sullo sviluppo**, con la data limite 2024-11-08 applicata alla lettura come
  per la potenza.
- **Orizzonte 5**: un'origine si esclude se uno dei 5 giorni e' escluso (come la volatilita').

## 4. Ingresso fisso e scala del bersaglio

**Ingresso fisso** (Matteo, D2 e decisioni del 21/11 in DECISIONS (5)): per ogni strumento i e ogni seduta t,
RV_{i,t} = somma dei quadrati dei 13 rendimenti a 30 minuti nella finestra W; σ̂²_{i,t} = **EWMA con λ = 0,94 di
RV_i fino alla seduta t** (la formula del pacchetto, applicata alla stessa finestra del bersaglio, Matteo).
**Distribuzione marginale: gaussiana** (quasi-verosimiglianza), dove serve una verosimiglianza (DCC) (Matteo).

L'EWMA e s si aggiornano sulle sedute valide **dello strumento** (non solo su quelle comuni); in una seduta non valida
lo strumento tiene il valore del giorno prima. **Avvio**: σ̂² parte dalla media di RV delle prime 50 sedute valide dello
strumento, che non si usano per altro. Le matrici Σ, le correlazioni, la costante, il DCC e le perdite usano invece le
**sedute valide comuni**.

**Fattore di scala** (rimedio del bloccante B1). Senza, la diagonale del bersaglio non vale 1 e la perdita di Stein
premia correlazioni gonfiate o sgonfiate (calcolo sintetico del gatekeeper: con diagonale 0,5 e correlazione vera 0,5 la
Stein premia 0,725; con 0,95 premia 0,516). Come c_t della volatilita' (VOLATILITA_PREREGISTRATION §3), **col bersaglio
al numeratore**: sia D_{i,τ} l'elemento diagonale della matrice di Bartlett dei rendimenti **grezzi** della seduta τ
(RV piu' i termini a ritardo 1 e 2 coi pesi di Bartlett); s_{i,t} = **media semplice** dei rapporti D_{i,τ} / σ̂²_{i,τ−1} sulle **500 sedute**
valide che finiscono a t (solo passato). La media semplice, non il rapporto di somme di c_t, perche' la perdita di Stein
e' lineare nel bersaglio e conta la media sui giorni (il rapporto di somme sarebbe una media pesata per la
volatilita'); la differenza si misura nel G9, non sui dati. I rendimenti standardizzati sono
z_{i,k} = r_{i,k} / (σ̂_{i,t−1} · √s_{i,t−1}) per le mezz'ore k della seduta t.

**Limite dichiarato: la scala vale in media, non giorno per giorno.** Nei giorni in cui l'EWMA sbaglia la volatilita',
la diagonale del bersaglio si allontana da 1 e la Stein premia in parte le previsioni di correlazione che si muovono
insieme a quell'errore (calcolo sintetico: con diagonale 1,25 l'ottimo scende da 0,5 a 0,441, con 0,8 sale a 0,572;
una previsione costante non ne e' toccata). Le fonti definiscono la proxy non distorta condizionatamente al passato.
Rimedio deciso (preso insieme, 21/11): **si misura nel G9** (§9, configurazione N1) con volatilita' marginali che
l'EWMA sbaglia; se N1 rifiuta oltre la soglia, **prima di ogni trial** il bersaglio passa alla correlazione realizzata
definita sotto, con la sua giustificazione sul testo delle fonti. E' un cambio **elencato prima** come condizionato a
quell'uscita (P6, punto 3).

**Bersaglio alternativo, definito ora** (si applica solo con la regola sopra): R_t = la matrice di Bartlett dei
rendimenti **grezzi** della seduta t normalizzata a diagonale 1 (correlazione realizzata, diagonale 1 ogni giorno, senza
ingresso fisso ne' fattore di scala). Orizzonte 5: **media delle cinque R** giornaliere. Le previsioni usano le R passate
al posto delle Σ: EWMA = Q delle R normalizzata; costante = media delle R; DCC con Q̄ = media delle R della finestra;
persistenza = 0,9·R_t + 0,1·I. La potenza (§10) si ricalcola sul bersaglio nuovo prima di ogni trial. La perdita di Stein
su R e' distorta per la disuguaglianza di Jensen: la giustificazione va trovata sul testo prima del G9, altrimenti il
passaggio non si fa e si torna al passo 2.

**Bersaglio.** Σ_t = matrice realizzata dei z della seduta t, con la correzione di Bartlett. Per l'orizzonte 5:
media delle Σ delle sedute t+1 ... t+5, ognuna standardizzata col suo σ̂ del giorno prima (informazione successiva
all'origine: si puo' per un bersaglio, ed e' dichiarato).

**Insieme d'informazione** di ogni previsione (R3), uguale per benchmark e candidati: le **matrici realizzate Σ delle
sedute passate** (non i rendimenti giornalieri: con N fino a 17 una correlazione EWMA su rendimenti giornalieri avrebbe
circa 32 osservazioni efficaci e sarebbe mal condizionata). Ogni previsione H e' una **matrice di correlazione**
(diagonale 1), definita positiva.

**Cosa I3 riporta e cosa no** (rimedio del bloccante B4). La diagonale di Σ e' la calibrazione dell'EWMA, ed entra
per forza nella perdita di Stein: I3 la **calcola** ma **non la riporta** (ne' media di z², ne' c, ne' s per strumento)
come risultato sull'EWMA. Si riportano solo i differenziali di perdita fra previsioni di correlazione.

## 5. Perdita (Matteo: Stein)

L(H, Σ) = tr(H⁻¹Σ) − log det(H⁻¹Σ) − N. Si calcolano **solo i differenziali** fra due previsioni,
L(H₁, Σ) − L(H₂, Σ) = tr((H₁⁻¹ − H₂⁻¹)Σ) + log det H₁ − log det H₂, che richiedono H invertibile e non Σ (il livello
sarebbe infinito se Σ e' singolare). Con 13 rendimenti per seduta e N fino a 17 la Σ di un giorno puo' essere singolare (rango al piu' 13 a ritardo 0; la
correzione di Bartlett lo alza ma non lo garantisce): il differenziale non ne ha bisogno, perche' inverte solo le
previsioni H, che sono definite positive; la perdita piena non si calcola mai.
Secondaria la **Frobenius**, solo come lettura. Errori HAC con max(h − 1, 4) ritardi per le origini sovrapposte, come la
volatilita'.

**Fonti, in quarantena** (lette solo nelle sintesi del motore di ricerca il 21/11): Laurent, Rombouts, Violante (2013),
*Journal of Econometrics* 173, 1-10 ([EconPapers](https://econpapers.repec.org/RePEc:eee:econom:v:173:y:2013:i:1:p:1-10));
Patton, Sheppard (2009), "Evaluating Volatility and Correlation Forecasts"
([ORA Oxford](https://ora.ox.ac.uk/objects/uuid:474e796d-5656-4e6b-94d3-b10125785fc5/files/mba0ba07178c0b21e3528d52e99430bd0)).
**Prima della corsa della potenza** si verificano sul testo: (a) che Stein e Frobenius stiano nella classe che conserva
l'ordinamento; (b) quale non distorsione chiede il teorema (la non distorsione **condizionata** per la grandezza che H
prevede: qui la correlazione, resa vera in media dal fattore di scala, non giorno per giorno: se il teorema la chiede
giorno per giorno va detto e deciso); (c) se il "QLIKE piu' potente" di Patton-Sheppard vale nel caso multivariato.
Una perdita non si cambia dopo un esito (G2).

## 6. Benchmark (Matteo: EWMA 0,94)

- **Benchmark del verdetto**: Q_t = 0,94·Q_{t−1} + 0,06·Σ_t (EWMA delle matrici realizzate), H = Q normalizzata a
  diagonale 1. Nessun parametro stimato. Avvio: Q parte dalla media delle prime 50 Σ comuni, non usate per altro.
- **Riferimenti di skill** (G3): correlazione **costante** = media delle matrici di correlazione (ogni Σ normalizzata a
  diagonale 1, poi la media) sulle **500 sedute** precedenti (finestra fissa, H3); **persistenza** = la matrice di ieri
  normalizzata, regolarizzata come 0,9·R_t + 0,1·I (regola fissata ora, copre anche il caso non definito positivo).
- **Benchmark forte**: **DCC(1,1) su matrici realizzate**, Q_t = (1 − a − b)·Q̄ + a·Σ_{t−1} + b·Q_{t−1}, con Q̄ la
  media delle Σ della finestra e H = Q normalizzata; (a, b) stimati per **quasi-verosimiglianza gaussiana dei
  rendimenti a 30 minuti standardizzati** (covarianza di una mezz'ora = H_t / 13, ritardo 0), sulla finestra mobile
  di **500 sedute**, ristima settimanale (H3). Previsione a 5 passi: E_t[Q_{t+k}] = Q̄ + (a + b)^{k−1}·(Q_{t+1} − Q̄),
  poi normalizzata (approssimazione di Engle e Sheppard 2001, dalla memoria: **in quarantena**, da verificare prima del
  passo 3).
- **Come si legge "batte l'EWMA ma non la costante"** (R3, scritto prima): un candidato che batte l'EWMA ma non la
  costante dice che la contrazione verso la media batte un filtro rumoroso, un risultato noto (Checklist 5), non che il
  candidato prevede la dinamica. Il pacchetto lo riporterebbe cosi'.
- I candidati (PCA a k fattori con k da una regola fissata prima, contrazione verso la costante, raggruppamenti,
  regimi), la combinazione semplice, le sottofamiglie e le quote sono scelte rinviate (statuto).

## 7. Universo e dati (Matteo: gli 8 strumenti nuovi si spendono per I3)

**17 strumenti, 8 classi**: azioni USA (SPX500, NAS100, DOW, RUSSELL), azioni Europa (DAX, se passa il controllo del
§3), metalli preziosi (XAUUSD, XAGUSD), energia (WTI, NATGAS), cambi (EURUSD, USDJPY, GBPUSD, AUDUSD), obbligazioni
(BUND, USTBOND), metalli industriali (COPPER), crypto (BTCUSD). I 9 in casa (M5 fino al 2026-11-11) piu' 8 da scaricare
gratis da Dukascopy M5 con lo stesso script della volatilita' (regola d'acquisto, backlog §G: prima il gratuito).
- **Scelta delle tre majors** (USDJPY, GBPUSD, AUDUSD): proposta da Claude con l'argomento "le meno legate a EURUSD",
  cioe' usando la memoria del modello sulla grandezza da misurare: **contaminazione dichiarata** (Checklist 5).
- **Inizio della matrice comune**: il piu' tardi fra gli inizi M5 (da verificare sui file: nel D1 USTBOND parte il
  2018-12-18, BUND il 2016-05-02, BTCUSD il 2017-05-07; RUSSELL M5 2018-08), quindi **intorno al 2019**, non dal 2015.
  Lo sviluppo va dal primo giorno comune al 2024-11-08.
- Il +0,791 di A1 (TREND_A1_HELDOUT_POWER §4) e' la correlazione media dei rendimenti D1 di **cinque indici** (SPX500,
  NAS100, DAX, N225, DJIND, dal 2017-12-26; `magazzino/registro/codice/trend/heldout_pool.py`, insieme "index"),
  applicata poi ai 20 indici liberi, non delle quattro azioni USA. *Corretto il 23/11: la versione precedente diceva "la
  media dei 20 indici del pool libero", ma il codice la misura sui cinque.*
- **Unita' di conto** (C1, G8): proposta, una serie = **modello × orizzonte** sull'intera matrice (un universo unico);
  scelta rinviata (statuto).
- **Acquistabili**, non necessari finche' il gratuito basta: futures intraday sincroni (Databento, FirstRate); i
  futures a 1 minuto dei soci coprono un anno (2025-11 → 2026-11), utili come conferma su prezzi di borsa.

## 8. Dati gia' visti, blocchi, contaminazione

- **Blocco 2024-11-11 → 2026-11-10 degli M5** (holdout sigillato della volatilita', mai piu' usabile dal ridisegno):
  **I3 lo legge, dichiarandolo** (Matteo). Da qui il blocco e' toccato dalla pipeline per i nove strumenti; una fonte
  comprata in futuro che lo copra non conta piu' come mai toccata (impegno registrato in DECISIONS 2026-11-21 (5)).
  I3 non riporta statistiche di volatilita' su quel blocco (§4): sul blocco il controllo di struttura riporta solo
  conteggi, e il controllo di selezione con i rendimenti assoluti si fa solo sullo sviluppo (§3).
- **Gli 8 strumenti nuovi** (Matteo): letti da I3, **perdono in modo irreversibile** lo stato di "mai visti" per la
  calibrazione dell'EWMA del ridisegno della volatilita'. Restano a quel ridisegno gli altri strumenti Dukascopy mai
  toccati (A1 §8 ne censiva circa 280 fra le azioni USA; bond e commodity sono pochi).
- **Dopo la pre-registrazione del ridisegno della volatilita'**, sui dati del suo test I3 non riporta nulla della
  diagonale (LIFECYCLE §8ter, "Ingresso fisso da un'altra famiglia"); come si riportano le perdite in quel periodo e'
  una scelta rinviata (statuto).
- **Correlazioni medie per classe** gia' calcolate su dati D1 (A1 §4, §8, §9): non sulla misura di I3, ma note.
- **Contaminazione** (H6, Checklist 5): quasi tutto il periodo dei dati (dal 2019 al 2026-05) precede il knowledge
  cutoff del modello (2026-05-31), compreso lo shock dei dazi di aprile 2025 nel blocco; universo, benchmark e misura li
  ha proposti Claude.
  Fatti famosi sulla grandezza ("le correlazioni salgono nelle crisi"; azioni-obbligazioni positive nel 2022) confermati
  dal test porterebbero poca informazione nuova.

## 9. Controllo della pipeline (G9, rimedio del bloccante B3)

Processi simulati **attraverso la misura vera** (13 rendimenti a 30 minuti, standardizzazione con l'ingresso fisso,
fattore di scala, correzione di Bartlett, rendimento mancante = zero), con due ingredienti dichiarati:
- **volatilita' marginali che l'EWMA sbaglia**: un **GJR per strumento con parametri stimati sui rendimenti di
  sviluppo**, solo dopo il commit di candidati e quote e **senza riportarli** (DECISIONS (7)): senza, l'errore
  condizionato dell'EWMA e' zero e il controllo non vede il limite del §4;
- **quotazioni non sincrone e buchi**: generati dai conteggi del controllo di struttura (sedute mancanti, prezzi
  mancanti per ora del giorno, prezzi fermi con la loro durata; nessuna statistica sui rendimenti), col generatore
  descritto in N2 qui sotto.

**N2, fissato ora per intero e prima della potenza** (decisione del 21/11, DECISIONS (9)). Gira dopo il controllo di
struttura (§10 (3)) e prima del calcolo della potenza (§10 (4)), quindi dopo i **soli conteggi**: se rifiuta, il ritorno
al passo 2 e' davvero il punto 2 di P6 del §8ter (deviazione, 0 trial).
*Processo riscritto il 23/11 (riserva R1 della sesta passata, scelta presa insieme, opzione A fra tre; DECISIONS
2026-11-23 (2)).* Il processo precedente (ricorsione EWMA sulla matrice intera, partenza dall'identita') muoveva la
diagonale e degenerava: su numeri inventati, 200 repliche di 1.450 sedute senza difetti di misura, diagonale spostata
fino a 2,4, condizionamento mediano ~3.700, e costante e persistenza battevano l'EWMA in 180 e 150 repliche su 200,
quindi il negativo non valeva (script di Claude nello scratchpad della sessione, non nel repo, pipeline semplificata
senza buchi ne' Bartlett). Riserva del gatekeeper: "un negativo con un processo che degenera non vale".
- **Processo vero, sulla correlazione** (volatilita' **costante e unitaria** per ogni strumento: ogni rendimento a 15
  minuti ha varianza 1/26, e l'EWMA la prevede senza errore sistematico dopo l'avvio). La correlazione vera dei 26
  rendimenti della seduta t e' Q_t, con
  Q_t = (1 − a − b)·R̄ + a·S_{t−1} + b·Q_{t−1}, **a = 0,06, b = 0,93**, Q_0 = R̄,
  dove S_{t−1} e' la matrice dei prodotti (non centrati) dei 26 rendimenti **veri** della seduta t − 1 normalizzata a
  diagonale 1, e i rendimenti sono gaussiani. a e' il peso dell'EWMA 0,94; a + b = 0,99 (emivita di circa 69 sedute)
  rende il processo persistente ma stazionario. Valori dichiarati, nessuno stimato sui dati.
- **Perche' non degenera, per costruzione**: R̄ e S hanno diagonale 1, quindi Q_t ha diagonale **esattamente 1** in ogni
  seduta (nessuna normalizzazione); Q_t e' una combinazione convessa di matrici semidefinite, e il suo autovalore minimo
  non scende mai sotto (1 − a − b)/(1 − b) = 0,143 volte quello di R̄. Prova su numeri inventati (stesso script, 200
  repliche di 1.450 sedute): condizionamento massimo mediano 35, |ρ| massimo mediano 0,80, nessun rifiuto di costante o
  persistenza senza difetti di misura; su 10.000 sedute nessun cambiamento.
- **Matrice di ritorno R̄, a blocchi, dalle correlazioni D1 gia' note di A1** (non dalla memoria del modello, Checklist
  5): **azioni** (SPX500, NAS100, DOW, RUSSELL, DAX) **0,791**, la media dell'insieme "indici" di A1 (SPX500, NAS100,
  DAX, N225, DJIND, rendimenti D1 dal 2017-12-26; `magazzino/registro/codice/trend/heldout_pool.py`,
  TREND_A1_HELDOUT_POWER §4); **energia** (WTI, NATGAS) **0,443** (insieme "energia" di A1: BRENT, WTI, NATGAS,
  DIESEL); **cambi** (EURUSD, USDJPY, GBPUSD, AUDUSD) **0,050** (cross FX di A1, non le majors: dichiarato); **ogni
  altra coppia**, dentro una classe senza numero di A1 (XAUUSD-XAGUSD, BUND-USTBOND) e fra classi, **0,112**, la media
  su **tutte** le coppie dei 20 futures pysystemtrade di A1 in 5 classi, dentro e fra classi (§8 dello stesso
  referto), usata come livello di fondo (riserva R2 della settima passata: non e' una misura "fra classi"). Le
  correlazioni vere di metalli e obbligazioni sono quasi certamente piu' alte: il processo non deve somigliare al
  mercato, deve partire da una struttura non banale. Con 17 strumenti l'autovalore minimo di R̄ e' 0,209 (calcolato il
  23/11, nessun dato); se il DAX esce dall'universo si toglie la sua riga e colonna. Il codice verifica che R̄ sia
  definita positiva e si ferma se non lo e' (nessuna correzione automatica).
- **Lettura, scritta ora**: con questo processo l'EWMA **non** e' il previsore esatto (il processo torna verso R̄) ma ci
  si avvicina molto (pesi 0,94^k contro 0,93^k piu' il ritorno), quindi senza difetti costante e persistenza sono molto
  peggiori dell'EWMA. Per questo N2 **non** decide su quante repliche rifiutano un test di significativita' (un difetto
  dovrebbe ribaltare tutto il distacco, e N2 passerebbe per costruzione: bloccante B1 della settima passata), ma su
  **quanto i difetti spostano il differenziale**, in unita' di effetto, confrontando ogni replica col suo gemello
  sincrono (regola sotto). La mappa fra correlazione vera e misurata non serve piu' (il processo e' definito sulla
  correlazione vera e la misura gli si applica sopra) e non si calcola.
- **Quotazioni non sincrone e buchi** (riserva R2 della sesta passata, precisata con R3, R4 e R8 della settima), tutti
  dai **soli conteggi dello sviluppo**, per strumento e per anno, presi **prima delle esclusioni**, generati sui
  **prezzi della griglia a 15 minuti** (27 per seduta, come il processo vero; la misura ne prende poi uno su due) e
  passati alla misura vera (prezzo
  mancante → due rendimenti mancanti, mancante = zero, soglie del 90% e del 25%, esclusione per unione), in quest'ordine:
  1. **seduta mancante per intero**: probabilita' che la seduta non abbia alcun prezzo in W (per esempio i festivi
     europei di DAX e BUND); estratta indipendente per strumento;
  2. **prezzi fermi**, nelle sedute presenti: una catena a due stati che **riparte ogni seduta dalla sua distribuzione
     stazionaria** (lo stato dell'open si estrae con probabilita' p0, ma il prezzo dell'open e' sempre quello vero;
     *corretto il 23/11: con l'open sempre "aggiornato" e soli 13 rendimenti la quota di nulli riprodotta scendeva dal
     10% all'8,8%, test sintetico*); dallo stato "aggiornato" si passa a "fermo" con probabilita' p_u = p0 / (L·(1 − p0)), da "fermo"
     si resta fermi con probabilita' 1 − 1/L, dove p0 e' la quota di rendimenti nulli fra quelli osservati e L la
     lunghezza media delle serie di rendimenti nulli consecutivi. Se p_u > 1 il codice si ferma (conteggi incoerenti).
     Un prezzo fermo ripete l'ultimo prezzo: il rendimento accumulato compare all'aggiornamento successivo (e' il
     meccanismo dell'Epps);
  3. **prezzo mancante per ora del giorno**, nelle sedute presenti: per ciascuno dei 27 orari, la probabilita' che il
     prezzo manchi, contata **sulle sole sedute presenti** (una seduta mancante per intero non conta due volte, come gli
     zeri nella quarta passata); riproduce le pause a ora fissa e il DAX dopo le 11:30 di New York. Un mancante cancella
     il prezzo anche se la catena lo dava fermo.
  **Come si contano nei dati veri**: una serie di rendimenti nulli consecutivi si interrompe a un rendimento mancante e
  si tronca a inizio e a fine seduta; il troncamento accorcia la durata contata L̃. Per riprodurla, la catena usa
  L = (n − 1)/(n/L̃ − 1), con n = 26 rendimenti a 15 minuti (con catena stazionaria la durata contata e'
  n/(1 + (n − 1)/L); per L = 3 vale circa 2,8, e il test sintetico la ritrova); se L̃ >= 26 il codice si ferma. *Aggiunto il 23/11: prima la catena usava
  la durata contata come se fosse la sua, e i fermi simulati risultavano piu' corti di quelli veri.* Le estrazioni per ora sono
  indipendenti fra loro, quindi i buchi di piu' ore consecutive non si riproducono: per questo il generatore si
  **verifica** sui soli conteggi prima di N2 (bloccante B1 dell'ottava passata): per strumento e per anno, la quota
  q̂ di sedute che il generatore fa escludere (meno del 90% dei rendimenti o oltre il 25% di nulli) su 200 anni
  simulati deve stare entro max(2 punti; 25% di q; 3·√(q(1 − q)/n_anno)) dalla quota vera q del controllo di
  struttura, con n_anno le sedute di quell'anno (il terzo termine assorbe il rumore di campionamento della quota vera:
  con ~245 sedute un generatore perfetto usciva per caso dalla tolleranza in una cella su 10-19). La verifica gira in
  uno script a se', **prima** di simulare qualunque replica: se e' GUASTO lo script si ferma e l'unica uscita e' la
  verifica (un test lo controlla), quindi nessun δ e' visto prima di correggere il generatore. **Correzioni ammesse
  del generatore, in quest'ordine**, ognuna una deviazione P5 (P6 punto 2) e seguita da una nuova verifica: (1) i
  prezzi mancanti per ora estratti a blocchi, con la durata media delle serie di prezzi mancanti consecutivi contata
  come quella dei nulli; (2) la seduta mancante per intero estratta insieme per gli strumenti con lo stesso calendario
  europeo (DAX, BUND). Se dopo le due la verifica fallisce ancora, N2 e' GUASTO e si torna al passo 2. Resta gratis
  solo la correzione di un errore di codice (il generatore non fa cio' che il testo dice). Il rollover dentro W non si simula: per la regola del §3 cade alla
  riapertura serale; se il controllo trova pause dentro W, il punto 3 le contiene gia'.
- **Universo e sedute simulate** (riserva R5 della settima): l'universo e' quello fissato dal controllo di struttura
  vero (DAX e regola del 10% decisi li'); **nelle repliche la regola del 10% non si riapplica**, cosi' i due gemelli
  hanno lo stesso universo. Le sedute simulate sono le **date XNYS reali dello sviluppo comune**, con le chiusure
  anticipate escluse (servono per le probabilita' per anno); le origini sono le stesse della potenza (§10).
- **Gemello sincrono**: ogni replica gira due volte con **gli stessi rendimenti veri**, una con i difetti di misura e
  una senza (probabilita' zero di buchi e di prezzi fermi), attraverso la stessa pipeline.
- **Seme e flussi** (riserva R6 della settima): seme **20261123**; `SeedSequence(20261123).spawn(500)` da' una
  sottosequenza per replica, in ordine; ognuna fa `spawn(2)`: il primo flusso genera i rendimenti veri, il secondo i
  difetti. Dentro un flusso le estrazioni seguono le sedute in ordine di data e, in ogni seduta, gli strumenti
  nell'ordine del §7. Un seme diverso per ognuna delle due prove prima del commit (sotto): **20261128** per la verifica
  del processo, **20261129** per il controllo positivo (*20261125 e 20261126 sono stati usati il 23/11 con la griglia
  a 30 minuti: un seme gia' usato non si riusa*).
- **Previsioni confrontate**: EWMA (benchmark) contro **costante**, che **decide**, e contro **persistenza**, che si
  calcola e si riporta ma **non decide** (Matteo, 23/11: con t ≈ 95 nella prova del gatekeeper nessun difetto plausibile
  vi si vede), con le regole e le finestre del §6.
- **Regola di N2: spostamento appaiato in unita' di effetto** (rimedio del bloccante B1 della settima passata, scelta
  presa insieme il 23/11, τ = 0,5 fra 0,25, 0,5 e 1). Per ogni replica, confronto e orizzonte h ∈ {1, 5}:
  d_t = L(alternativa) − L(EWMA) (Stein; positivo = l'EWMA e' migliore), e
  δ = (media di d nel gemello con difetti − media di d nel gemello sincrono) / (deviazione HAC di d nel gemello
  sincrono / √n_h),
  con medie e deviazione calcolate sull'**intersezione delle origini valide** dei due gemelli (il gemello con difetti
  perde sedute per l'esclusione per unione: riserva R6 dell'ottava passata); una replica con meno di 50 origini comuni
  a un orizzonte ha a quell'orizzonte un **campione insufficiente**,
  con deviazione HAC centrata a max(h − 1, 4) ritardi e **n_h = 247**, le sedute piene XNYS dal 2024-11-11 al 2025-11-10
  (un anno, dal solo calendario: 250 sedute meno 3 chiusure anticipate; unita' di misura, non una scelta dell'holdout).
  δ e' in unita' di **errore standard** di un anno (sd/√247): l'MDE vale 2,486 di queste unita' (riserva R1
  dell'ottava passata; la versione precedente diceva per errore "unita' di MDE"). La sd e' quella del gemello
  sincrono simulato, non quella reale: se la reale e' piu' grande, la regola e' piu' severa del dichiarato. **N2 RIFIUTA per misura** se, per la
  costante, la **mediana di δ sulle 500 repliche e' sotto −0,5** in almeno uno dei due orizzonti (circa un quinto del
  fattore MDE 2,486): i difetti favoriscono l'alternativa abbastanza da poter creare un falso positivo. Uno spostamento
  a favore dell'EWMA (δ > 0) toglie potenza ma non crea falsi positivi: si riporta e non ferma il test; in quel
  caso, accanto a un mancato rifiuto, l'MDE si riporta anche come (fattore + mediana di δ)·errore standard (riserva
  R5 dell'ottava passata). Con probabilita'
  di difetto zero δ vale esattamente 0. Bonferroni non serve piu': la regola e' una soglia su una grandezza, non un test.
- **Guardia sul processo** (gemello sincrono): in ogni replica e orizzonte si fa anche il Diebold-Mariano a una coda
  "la costante batte l'EWMA" (HLN, HAC con max(h − 1, 4) ritardi, al 5%) **sul solo gemello sincrono**; se piu' di **35
  repliche su 500** rifiutano in un orizzonte (35 e' il quantile al 97,5% di una binomiale (500; 0,05): falso allarme
  1,96% per orizzonte, al massimo 3,9% sui due), il processo non e' un negativo valido alla lunghezza vera e N2 e'
  **GUASTO**. *Correzione del 23/11 (riserva R1 della settima): la soglia della versione del 22/11 era il limite alto
  dell'intervallo binomiale al 95%, 34,55 repliche, cioe' almeno 35, con falso allarme del 3,03% per confronto e circa
  l'11,6% sui quattro, come scritto nella sesta passata; il "17%" della prima stesura di oggi era sbagliato.*
- **Matrici non valide**: si contano, per replica, le matrici (Q_t, previsioni H, bersagli) con un valore non finito o,
  per Q_t e le H, autovalore minimo ≤ 10⁻¹⁰. Per costruzione dovrebbero essere zero: se ce n'e' anche una, N2 e'
  **GUASTO** (non "passa") e si cerca l'errore.
- **Due prove prima del commit di congelamento** (test sintetici, nessun dato, P6 punto 1), con 1.450 sedute (circa lo
  sviluppo comune atteso dal 2019), la pipeline intera e 500 repliche:
  - **verifica del processo** (seme 20261128): il gemello sincrono deve avere **al massimo 25 repliche su 500** (5%)
    che rifiutano nella guardia sopra, in entrambi gli orizzonti (margine sotto la soglia di 35). Se non ci sta, (a, b)
    si cambia **una volta per tentativo, in quest'ordine fisso**: (0,06; 0,93) → (0,06; 0,90) → (0,04; 0,94); al
    massimo questi tre; se nessuno passa si torna al testo. Un cambio e' gratis (P6 punto 1: dati sintetici, prima del
    commit) solo a queste condizioni, e si registra in DECISIONS;
  - **controllo positivo di N2** (seme 20261129): con un difetto dichiarato ora, **quota di prezzi fermi fissa del 5%
    su tutti i 17 strumenti, catena di durata L = 3 quarti d'ora sulla griglia a 15 minuti, nessun altro difetto**
    (*la rampa fino al 30% su 7 strumenti e, il 23/11, lo stesso 5% sulla griglia a 30 minuti svuotavano il campione:
    sezioni "Prove sintetiche" e "Prove prima del commit"*), la regola deve scattare (mediana di δ sotto −0,5 per la costante in almeno un orizzonte); con probabilita' di difetto zero δ deve
    valere esattamente 0. Se il difetto non fa scattare la regola, la regola non va e si torna al testo.
- **Conseguenze, scritte ora**:
  - **RIFIUTA per misura** (regola di δ): la misura e' distorta (Epps residuo, buchi o la loro variazione negli anni);
    il test non va avanti e si torna al passo 2 (punto 2 di P6, deviazione, 0 trial). **Rimedi ammessi, elencati ora**
    (riserve R8 della settima e R3 dell'ottava): i rimedi (i) Bartlett a due ritardi e (ii) 30 minuti sono gia' la
    misura di base dal 23/11; resta (iii) l'**uscita dello strumento** con la quota di prezzi fermi piu' alta nello
    sviluppo, **ripetibile fino a tre strumenti**, uno alla volta, ciascuna seguita da un nuovo N2 (le uscite si
    sommano: lo strumento uscito non rientra). L'universo minimo resta di 14 strumenti; R̄ perde le righe degli
    strumenti usciti. Ogni uscita e' una deviazione nella tabella P5 (punto 2 di P6); un rimedio non elencato qui e'
    una scelta nuova dopo un'uscita (punto 3). **Finiti i rimedi** (tre strumenti fuori e N2 che rifiuta ancora): la
    misura intraday sui CFD Dukascopy non basta, I3 si ferma al passo 2 e si torna a Matteo (dati di borsa sincroni,
    backlog §G, o famiglia chiusa per misura). Piu' ritardi di Bartlett non sono un rimedio: a 30 minuti con 3 o 4
    ritardi la guardia del gemello sincrono si rompe (sezione "Prove sintetiche");
  - **GUASTO** (guardia sul processo, generatore fuori tolleranza, matrici non valide, o tutti e due gli orizzonti
    decaduti): N2 non passa; si cerca l'errore o si torna al passo 2 per il processo (punto 2 di P6);
  - **orizzonte senza campione** (decisione presa insieme il 24/11, DECISIONS 2026-11-24 (2)): un orizzonte con
    campione insufficiente in **piu' della meta'** delle repliche **decade**: esce da I3 (la misura manca, la pipeline
    non e' guasta), e regola di δ e guardia valgono sugli orizzonti rimasti, con la mediana sulle repliche che hanno
    campione. Vale anche sui dati veri: un orizzonte con meno di 50 origini comuni nello sviluppo, dopo il controllo di
    struttura (soli conteggi), esce da I3 prima della potenza. Il pacchetto dira' allora solo cio' che resta (per
    esempio "previsione a una seduta");
  - nessuno dei tre: si calcola la potenza sugli orizzonti rimasti.
- Dopo il passo 3, N2 si **ripete** sui candidati insieme a N1 e al positivo; le conseguenze di quelle uscite sono fra
  le scelte rinviate (statuto) e si scrivono nel commit del passo 3, prima che giri qualunque configurazione del G9.
  Nella ripetizione la guardia sul gemello sincrono **non si trasferisce cosi' com'e'**: il processo torna verso R̄,
  quindi un candidato di contrazione o un DCC e' davvero migliore dell'EWMA e il gemello sincrono rifiutera' per merito;
  la lettura sara' appaiata (riserva R7 della settima, nell'elenco dello statuto).

**Ordine di N1 e del positivo**: solo dopo il commit di candidati, sottofamiglie, quote e conseguenze (passo 3) si
stimano GJR e DCC e girano N1, il positivo e la ripetizione di N2; i parametri stimati non si riportano prima. Lo script
del G9 si rifiuta di partire senza quel commit (percorso protetto pulito, hash registrato).
- **negativo, in due configurazioni** (ogni rifiuto ha una sola causa e una conseguenza scritta ora):
  - **N1**: marginali GJR (l'EWMA sbaglia la scala) e quotazioni **sincrone**. Se rifiuta oltre la soglia, si passa al
    bersaglio alternativo del §4;
  - **N2**: volatilita' costante (l'EWMA non sbaglia la scala) e quotazioni **non sincrone** come nello sviluppo;
    fissato per intero sopra, gira prima della potenza;
  - il processo di correlazione, le repliche e le soglie di **N1** sono scelte rinviate (statuto); quelli di N2 sono
    fissati sopra. Le rifiniture P4 dei round 2-3 entrano anche nel negativo (un candidato che legge le diagonali
    passate puo' prevedere l'errore dell'EWMA e vincere per bravura sulla volatilita');
- **positivo**: un **DCC(1,1) con i parametri stimati sulle ultime 500 sedute comuni dello sviluppo** (H3), a scelte
  congelate: e' il benchmark forte, non un candidato, quindi 0 trial. In ogni replica il DCC **si ristima** con la stessa
  verosimiglianza della pipeline (cosi' si mette alla prova anche la differenza fra verosimiglianza a ritardo 0 e
  bersaglio con Bartlett). Il test deve trovare il DCC contro l'EWMA almeno nell'80% delle repliche.
- Il **rapporto effetto/MDE** del positivo si scrive **prima di contare qualunque trial**: se il disegno non vede
  l'effetto di un DCC realistico, lo si dice prima, non dopo 100 trial (lezione del 2026-11-20).
- Numero di repliche e soglie di N1 e del positivo: scelte rinviate (statuto), con il precedente della volatilita' (p
  puntuale dello SPA, DECISIONS 2026-11-19 (2)).

## 10. Piano della potenza (prima di raccogliere)

**Ordine** (rimedio del bloccante B2): (1) commit di tutte le scelte dei §3-§9, del codice e delle guardie (sha256 dei
file, nessuna seduta oltre il 2024-11-08 letta per l'MDE, e una guardia che impedisce allo script di stampare la media o
il segno del differenziale, su nessun canale: vedi "Requisiti del commit (1)"); (2) verifica delle fonti sul testo
(§5); (3) download degli 8 strumenti **con fine fissa al 2026-11-10** (anche nel loader: I3 non legge nulla dopo la fine
del blocco, che e' il periodo del possibile test del ridisegno della volatilita') e controllo di struttura (solo
conteggi); (3b) **N2** (§9); (4) calcolo della potenza.

**Riscaldamento e prima origine** (le finestre stanno una dentro l'altra): la storia comune parte intorno al 2019 (il
piu' tardi fra gli inizi M5, da leggere sui file). In sedute dall'inizio comune, circa:
- 50 di avvio dell'EWMA di σ̂², poi 500 per il fattore di scala s: le Σ esistono da circa la seduta 550;
- 50 di avvio della Q dell'EWMA: il benchmark ha la prima previsione intorno alla seduta 600;
- la costante usa correlazioni normalizzate, che non dipendono da s: 500 sedute, ma il confronto parte con l'EWMA;
- il DCC richiede 500 Σ: prima previsione intorno alla seduta 1.050, cioe' intorno al 2023.
La potenza EWMA contro costante usa quindi le origini dalla seduta ~600 (meta' 2021 circa) al 2024-11-08, circa 850
sedute; il DCC nello sviluppo ne ha circa 450. Nessuna finestra incompleta: un'origine senza tutte le sue finestre non
entra.

**Cosa riporta** (Matteo): **solo la deviazione HAC** del differenziale di perdita fra EWMA e correlazione costante,
per orizzonte, **senza media ne' segno**: cosi' nessun numero dice quale modello vince, e i candidati si possono ancora
scegliere al passo 3. E' un ordine di grandezza (un differenziale fra due previsioni lontane puo' essere piu' disperso
di quello fra un candidato e l'EWMA); la prova vera e' il rapporto effetto/MDE del positivo (§9).

**MDE** = fattore × deviazione HAC / √n, con n = sedute dell'holdout (inizio e lunghezza: scelta rinviata, statuto; si
riporta per 1 e 2 anni). Fattori a una coda all'80% (`fattore_potenza`, calcolati dal gatekeeper il 21/11): **2,486**
(α 5%), **2,802** (2,5%), **3,083** (1,25%), **3,339** (0,625%); quello giusto e' la prima soglia di Holm
dell'ipotesi elementare, quando le quote (scelta rinviata) saranno fissate.

**Trial**: 0. EWMA e costante sono benchmark e riferimento, non varianti (precedente: la volatilita' non li ha contati,
VOLATILITA_PREREGISTRATION §5); condizioni: la finestra della costante e' fissata ora (500 sedute), e la costante non
puo' diventare lo strumento consegnato a partire da questi dati.

## Requisiti del commit (1) (dalla quinta passata del gatekeeper, 21/11, e dalla sesta, riserva R6, 23/11)

Il gatekeeper rivede il diff del commit prima di ogni corsa. Il commit contiene:
1. **contenuto**: questo referto, la voce DECISIONS, il codice in una cartella nuova sotto `magazzino/registro/codice/`
   con i test; nessun dato degli 8 strumenti (non ancora scaricati); lo scaricatore (importato da
   `volatilita/scarica_dukascopy.py`) con date d'inizio e di fine fisse, fine al 2026-11-10;
2. **guardie** sul modello di `volatilita/guardie.py`, in testa a ogni script, ferme al primo errore: percorsi protetti
   puliti in git (referto, LIFECYCLE, contatore, cartella di I3, `motore/core`, `motore/tests`, i moduli della
   volatilita' importati e `volatilita/hash_dati.json`), hash del commit in ogni uscita; il controllo di git si salta
   (`git=False`) **solo nei test**, mai in una corsa che produce numeri; versioni fissate (Python 3.12, numpy, pandas,
   scipy, `exchange_calendars` 4.13.2, statsmodels se usato; `arch` solo dal passo 3), lo script si ferma se non
   coincidono; sha256 **e numero di byte** dei 9 M5 contro `volatilita/hash_dati.json` (letto, mai riscritto) e degli 8
   nuovi registrati una volta sola subito dopo il download (file temporaneo e sostituzione, rifiuto se esiste); data
   massima di ogni file ≤ 2026-11-10; `trial_ledger --check` a 0; ordine: la potenza parte solo se esistono,
   committati, l'esito della verifica delle fonti, il controllo di struttura, gli hash degli 8 e l'esito di N2;
3. **data della potenza e del controllo di selezione**: fine al 2024-11-08 scritta nel codice, applicata **alla
   lettura** prima di ogni rendimento, controllata su ogni oggetto derivato; un test con una seduta successiva deve
   fermare lo script (per la potenza e per il controllo di selezione);
4. **uscita della potenza, nessun canale aperto**: un dizionario con chiavi ammesse (commit, versioni, sha256; per
   h ∈ {1, 5} numero di origini, ritardi HAC, deviazione HAC **centrata** del differenziale; sedute dell'holdout a 1 e 2
   anni dal solo calendario; fattori e MDE); una chiave in piu' ferma lo script (un test aggiunge `media`). Su nessun
   canale (schermo, log, file, cache, grafici, messaggi d'errore, oggetti restituiti): media, segno, t, p, quota di
   giorni vinti, perdite per modello, Frobenius, serie dei differenziali, matrici o livelli di correlazione, σ̂², RV, s,
   rapporti D/σ̂², media di z². La serie dei differenziali vive solo in memoria e passa a una funzione che restituisce la
   sola deviazione; gli errori riportano data e tipo, non valori. Non si ripete l'abitudine della volatilita' di salvare
   le perdite in cache;
5. **uscita del controllo di struttura**: solo conteggi per strumento e per anno (sviluppo e blocco separati), le
   quantita' per il G9 del §3 dal solo sviluppo, orari delle pause, copertura del DAX, regola del 10%; **nessuna RV,
   nessuna media di rendimenti, nessun livello di prezzo**; il controllo di selezione solo sullo sviluppo, con la data
   limite del punto 3; chiavi d'uscita ammesse come al punto 4;
6. **N2** (riserva R6): parte solo se il controllo di struttura e gli hash degli 8 sono committati; legge **solo** il
   file dei conteggi del controllo di struttura (guardia sui percorsi: nessun CSV di prezzi aperto, un test lo
   verifica); chiavi d'uscita ammesse: commit, versioni, seme, numero di repliche e di sedute, n_h, esito della verifica
   del generatore per strumento e anno, per confronto e orizzonte i **quantili di δ** (5, 25, 50, 75, 95%) e il numero
   di repliche che rifiutano nella guardia sul gemello sincrono, per orizzonte le repliche con campione insufficiente,
   gli orizzonti decaduti, soglie, esito (PASSA, RIFIUTA per misura, GUASTO), numero di matrici non valide; una chiave in piu' ferma lo script. Su nessun canale: differenziali, perdite, t, p
   delle singole repliche, matrici. I quantili di δ sono differenziali **simulati** su un processo inventato: lo statuto
   non cambia;
7. **test su dati sintetici**, verdi: prezzi e griglia; fuso applicato una volta nel loader e protetto dal doppio, anche
   **ai cambi d'ora** (marzo e novembre, europei e americani); rollover tolto una volta; **file senza prezzi** in una
   seduta e in un intero strumento; Bartlett semidefinita con zeri; nulli sui soli osservati; esclusione per unione,
   chiusure anticipate, orizzonte 5, **nessuna finestra incompleta**; fattore di scala con diagonale media vicina a 1 su
   un processo EWMA esatto; differenziale di Stein uguale alla differenza delle perdite piene; EWMA, costante e
   persistenza definite positive a diagonale 1; riscaldamento (indici 50, 550, 600); ingresso fisso identico bit per
   bit alla formula del pacchetto (importata); deviazione di Newey-West identica a `volatilita/potenza.py:sd_newey_west`;
   le guardie di data e di campi; **per N2**: con probabilita' di difetto zero i due gemelli coincidono bit per bit, δ
   vale 0 e la diagonale media del bersaglio e' vicina a 1; la catena dei prezzi fermi riparte a ogni seduta, l'open non
   e' mai fermo nel prezzo (lo stato parte dalla distribuzione stazionaria), p_u > 1 ferma il codice; la durata della
   catena riproduce quella contata; i mancanti per ora contati sulle sole sedute presenti; validita' sui 26 rendimenti
   a 15 minuti e misura sui 13 a 30 minuti; le due prove prima del commit del §9 (verifica del processo, seme
   20261128; controllo positivo, seme 20261129); Q_t ha diagonale 1 e autovalore minimo ≥ 0,143·λ_min(R̄) in ogni
   seduta; R̄ a blocchi coi valori del §9; il generatore riproduce in media le probabilita' in ingresso (sedute
   mancanti, prezzi mancanti per ora, quota e durata dei fermi); stesso seme, stesso risultato.

La **mappa inversa** fra correlazione vera e misurata, chiesta dalla sesta passata, non serve piu' col processo del
23/11 (§9) e non si scrive.

## Statuto delle decisioni (Matteo, 21/11; corretto dalla terza e dalla quarta passata)

Le scelte di **misura e di disegno** di questo referto sono **prese insieme da Matteo e Claude**, con un margine d'errore
dichiarato: sono rivedibili, e il costo di un cambio segue **P6 del §8ter** (LIFECYCLE): gratis prima del commit di
congelamento se nessun dato gia' visto le riguarda (qui pesano gia' le correlazioni di A1 e i risultati della
volatilita' sugli stessi M5, §8); deviazione P5 dopo il commit o dopo soli conteggi (compreso N2, §9); dopo perdite o
differenziali (la deviazione HAC del §10, il rapporto effetto/MDE e N1 del §9) solo i cambi elencati prima, cioe' il
passaggio al bersaglio alternativo (§4) e la lunghezza dell'holdout; dopo l'holdout nessuno.

**Scelte rinviate in modo esplicito** (decisione del 21/11, DECISIONS (5); **unico elenco**, le sezioni rimandano qui):
si fanno al passo 3 **dopo la sola dispersione HAC** del §10: candidati (con la regola per k della PCA) e combinazione;
sottofamiglie, quote e riciclo; unita' di conto (C1, G8); holdout (inizio e lunghezza); repliche, soglie e processi
esatti di N1 e del positivo; conseguenze di tutte le uscite del G9 (positivo sotto l'80%, N1 e N2 insieme con N2 che
prevale, G9 da rifare dopo il passaggio al bersaglio alternativo, ripetizione di N2 sui candidati); verosimiglianza del
DCC sul bersaglio alternativo; probabilita' per anno in N1; come si riportano le perdite durante il test del ridisegno
della volatilita' (§8); P4; la frase del §2 sul vantaggio che coincide con gli anni di dati peggiori; la lettura
**appaiata** della guardia sul gemello sincrono nella ripetizione di N2 sui candidati (§9). Restano confermative
solo se, oltre a quella dispersione e ai conteggi, **nessun'altra informazione su perdite o differenziali sui dati
reali** e' stata vista; altrimenti vale il punto 3 di P6. Le quote di rifiuto di N2 sono differenziali **simulati**, su
un processo inventato e tarato sui soli conteggi (nessun rendimento reale entra nella simulazione): non portano
informazione sulle perdite reali e non tolgono lo stato confermativo (decisione del 21/11, DECISIONS (9)).

**Regole di protezione** (non sono scelte e non stanno sotto lo statuto; cambiano solo col §7 o con una decisione di
metodo di Matteo che dichiari cosa ha visto): l'holdout e il blocco sigillato; i dati futuri della volatilita'; la
guardia che impedisce di stampare **media e segno** del differenziale e quella **"nessuna seduta oltre il 2024-11-08"**
per la potenza (§10); il **non riportare la diagonale** (§4); gli impegni del §8 (una fonte comprata che copra il blocco
non conta come mai toccata; gli 8 strumenti non sono piu' "mai visti" per la volatilita'); il vincolo che **la costante
non diventa lo strumento consegnato** a partire da questi dati (§10). I verdetti, quando ci saranno, idem.

## Decisioni del 21/11 (passo 2), prese insieme

Misura intraday, orizzonte 1 e 5 giorni; perdita di Stein; benchmark EWMA 0,94; il blocco sigillato degli M5 si legge,
dichiarandolo; **fattore di scala** come c_t; gli **8 strumenti nuovi si spendono per I3**; la potenza riporta **solo la
dispersione**; positivo del G9 con parametri **stimati sullo sviluppo**; EWMA calcolata **sulla stessa seduta** del
bersaglio; marginale **gaussiana**. Dopo la seconda passata del gatekeeper: il limite della scala giorno per giorno
**si misura nel G9**, con il passaggio alla correlazione realizzata se il negativo rifiuta oltre la quota; finestre
fisse di **500 sedute**; rollover senza calendario **alla riapertura serale**; le regole di misura del §3 proposte da
Claude (Bartlett su tutta la matrice, 90% dei rendimenti, chiusure anticipate escluse, 25% di rendimenti nulli, soglia
del 10% per lo strumento, DAX, prezzi) adottate insieme. Le scelte che restano sono nell'**unico elenco** dello statuto
(sopra). Le probabilita' di N2 per strumento e per anno, coi mancanti generati, sono fissate nel §9 (con mancante =
zero e prezzi fermi la correlazione misurata si attenua di circa √((1−p_i)(1−p_j)); se le quote cambiano negli anni
EWMA e DCC seguono l'attenuazione e la costante no: un vantaggio sulla qualita' dei dati, non sulla dinamica, che N2
deve vedere). ⚠️ *Smentita in direzione dalle prove sintetiche del 23/11 (sezione in fondo, numeri inventati): i
prezzi fermi favoriscono la costante, anche a quota fissa.*

**23/11 (riserve della sesta passata), prese insieme:** processo di N2 sulla correlazione con ritorno verso una matrice
a blocchi dalle correlazioni D1 di A1, a = 0,06 e b = 0,93, con gemello sincrono (opzione A fra tre, raccomandata da
Claude); generatore dei buchi in tre componenti dai conteggi (§9). Dopo la settima passata: N2 decide sullo
**spostamento appaiato δ** in unita' di effetto, con **τ = 0,5** (fra 0,25, 0,5 e 1), e la persistenza resta **solo
lettura** (scelte prese insieme, raccomandate da Claude sulla proposta del gatekeeper). La soglia con Bonferroni della
prima stesura di oggi (36 repliche su 500) e' superata.

## Revisione del gatekeeper

**Prima passata (commit `5ad5b98`): BLOCCA**, 4 bloccanti, 8 riserve. B1 scala del bersaglio → §4 (fattore di scala,
Matteo); B2 ordine e C3 → §10 (scelte congelate prima, solo dispersione, Matteo); B3 G9 mancante → §9 (Matteo per i
parametri); B4 dichiarazione falsa sull'ingresso fisso → §4 e §8 ("calcola ma non riporta"; strumenti nuovi spesi per
I3, Matteo). Riserve: R1 dichiarazioni di misura → §3; R2 singolarita' → §5; R3 insieme d'informazione e lettura di
"batte l'EWMA" → §4, §6; R4 orizzonte 5 e pacchetto → §2, §4, §5, §6; R5 potenza → §10; R6 universo, citazione A1,
majors, inizio, unita' → §7; R7 blocco, impegno N3 in DECISIONS, contaminazione → §8; R8 fonti prima della corsa → §5.

**Seconda passata (commit `0721a6a`): BLOCCA**, 1 bloccante, 9 riserve. Bloccante: Bartlett e fattore di scala
stimavano due diagonali diverse (la diagonale media sarebbe stata circa 1 + ρ1) → §4, s col bersaglio al numeratore
(diagonale di Bartlett dei rendimenti grezzi). Riserve: scala condizionata → §4 (limite dichiarato, misurato nel G9,
regola di passaggio); G9 senza volatilita' marginali e quotazioni non sincrone → §9; ordine del G9 dopo il commit dei
candidati → §9; riscaldamento e prima origine → §10 e finestre di 500 sedute; regole di misura da fissare → §3 (prezzi,
quarti mancanti, aggiornamento di EWMA e s, orizzonte 5, costante, soglia dello strumento, rollover, periodo del
controllo, calendario); chi decide la misura → "Statuto" e decisioni; frase falsa sul blocco → §8; media pesata → §4
(media semplice); contaminazione e Epps residuo → §3, §8.

**Terza passata (commit `c84fa77`): BLOCCA**, 1 bloccante, 5 riserve. Bloccante: lo statuto rendeva rivedibili gratis
regole di protezione e verdetti, e non diceva P1 e H5 → P6 nel LIFECYCLE, statuto ristretto (DECISIONS (7)). Riserve:
R1 matrice semidefinita con buchi → §3 (mancante = zero); R2 regola di passaggio → §4 e §9 (N1 e N2, soglia binomiale,
bersaglio alternativo definito, P4 nel negativo); R3 parametri GJR e ristima del DCC → §9; R4 riscaldamento → §4, §6,
§10; R5 pause dentro W → §3.

**Quarta passata (commit `2885c53`): BLOCCA**, 1 bloccante, 5 riserve. Bloccante: le scelte del passo 3 fatte dopo la
dispersione HAC non erano regolate da P6, e la guardia su media e segno non era una protezione (via: togliere la guardia
come deviazione, leggere il segno, scegliere i candidati) → P6 del §8ter precisato (prime scelte dopo un'uscita, guardie
fra le protezioni), statuto con scelte rinviate e protezioni elencate (DECISIONS (8)). Riserve: R-a zeri contati due
volte → §3; R-b N2 per primo e da solo → §9 (le altre conseguenze al passo 3); R-c DCC sul bersaglio alternativo e R-d
mancanti che cambiano negli anni → passo 3, prima del G9; R-e nome P6 → citato come "P6 del §8ter".

**Quinta passata (commit `980a839`): BLOCCA**, 1 bloccante, 4 riserve. Bloccante: N2, configurato al passo 3, girava
dopo la dispersione HAC, quindi il ritorno al passo 2 non era una deviazione gratuita → N2 fissato ora per intero e prima
della potenza (§9, DECISIONS (9)). Riserve: un solo elenco delle scelte rinviate → statuto; conseguenze del G9 prima di
qualunque configurazione → §9; guardia "nessun canale" → requisiti del commit (1); fine dei dati al 2026-11-10 → §10.

**Sesta passata (commit `7259c62`, chiusa il 22/11): PASSA CON RISERVE**. Il passo 2 e' chiuso fino al commit (1): N2
gira davvero dopo i soli conteggi e non porta informazione sulle perdite reali. Il gatekeeper **non approva il commit (1)**
senza queste correzioni, tutte prima di ogni dato (0 trial). **Da fare all'inizio della prossima sessione:**
- **R1, processo di N2 incoerente e degenere**: la ricorsione EWMA sulla matrice intera muove la diagonale e, usata come
  processo vero, degenera (simulazione su numeri inventati: diagonale 0,14-3,9, condizionamento mediano ~1.260, |ρ| max
  mediano 0,86; script del gatekeeper `scratchpad/m_walk.py`, non nel repo). Serve: un processo con diagonale ferma che
  non degenera (per esempio una ricorsione sulla correlazione che ritorna verso una matrice fissa dichiarata; allora un
  rifiuto si legge come contrazione verso la media, non come Epps, e la lettura va scritta prima); una matrice di
  partenza non identita' (struttura a blocchi con livelli dalle correlazioni D1 di A1, gia' note); metodo e numero di
  simulazioni della mappa inversa, regola e conteggio delle matrici non valide; il seme. **Scelta da fare insieme.**
- **R2, generatore dei buchi**: componente giornaliera (sedute mancanti intere, festivi europei) e componente per ora
  del giorno (pause a ora fissa, prezzi fermi lunghi, DAX dopo le 11:30 NY), dai conteggi.
- **R3, rinvii ancora sparsi**: togliere o riscrivere le frasi che rinviano N2 al passo 3 (§9, "in entrambe" e
  "repliche al passo 3"; soglie del G9), il secondo elenco "Restano al passo 3" nelle decisioni, e far rimandare allo
  statuto §6, §7, §8 e §10.
- **R4, statuto**: "nessun'altra informazione su perdite o differenziali **sui dati reali**" (le quote di N2 sono
  differenziali simulati).
- **R5, soglia di N2 su quattro confronti**: falso allarme ~3,0% per confronto, fino a ~11,6% sui quattro: dichiararlo
  o usare Bonferroni.
- **R6, requisiti del commit (1)**: aggiungere `git=False` solo nei test; statsmodels se usato; byte con gli sha256;
  **data limite 2024-11-08 anche per il controllo di selezione**; "nessuna RV, nessuna media di rendimenti" nel controllo
  di struttura; test sul fuso ai cambi d'ora, test senza prezzi, nessuna finestra incompleta; **requisiti di N2**
  (parte dopo struttura e hash committati, legge solo il file dei conteggi con guardia sui percorsi, chiavi d'uscita
  ammesse: quote di rifiuto, esito, matrici non valide; test: con probabilita' zero diagonale ~1, la mappa inversa
  ritrova la correlazione vera, stesso seme stesso risultato).
Debito: primitiva comune in `motore/core` per campi d'uscita ammessi e data limite; riga nella Checklist 10 "un negativo
con un processo che degenera non vale".

**Riserve applicate il 23/11** (prima del commit di congelamento, 0 trial, P6 punto 1): R1 → §9, processo sulla
correlazione con ritorno verso la matrice a blocchi di A1 e gemello sincrono (opzione A, scelta presa insieme; DECISIONS
2026-11-23 (2)); R2 → §9 e §3, generatore in tre componenti dai conteggi; R3 → §6, §7, §8, §9, §10 e decisioni del
21/11, che rimandano all'unico elenco dello statuto; R4 → statuto ("sui dati reali"); R5 → §9, Bonferroni, 36 repliche
su 500 (⚠️ superata dalla settima passata: la regola di N2 ora e' δ); R6 → requisiti del commit (1), punti 2, 3, 5, 6 e 7. Correzione di citazione nel §7 (il +0,791 di A1 viene da
cinque indici, non da venti). I due debiti restano a Matteo.

**Settima passata (commit `f8654d0`, 23/11): BLOCCA**, 1 bloccante, 8 riserve. Il gatekeeper attribuisce il bloccante
anche alla propria sesta passata, che aveva accettato la soglia sulle repliche senza controllare che N2 potesse
rifiutare. **B1**: con il processo del 23/11 l'EWMA e' quasi il previsore ottimo, quindi la statistica DM "costante meno
EWMA" vale circa +34 senza difetti e +26 con prezzi fermi fino al 30%: uno spostamento di circa 8 deviazioni, cioe'
circa 4,4 unita' su un anno di holdout, quasi due volte il fattore MDE. Eppure rifiutava 0 repliche su 6, e N2 passava
per costruzione (prova del gatekeeper su numeri inventati, 6 repliche, script nello scratchpad della sessione, non nel
repo) → §9: regola sullo spostamento appaiato δ con τ = 0,5, controllo positivo sintetico prima del commit, gemello
sincrono come guardia sul processo, persistenza solo lettura (scelte prese insieme, DECISIONS 2026-11-23 (3)).
Riserve: R1 numero sbagliato sulla soglia di prima (era almeno 35 repliche, 3,03% per confronto, ~11,6% sui quattro, non
"17%") → §9; R2 descrizione dello 0,112 (media su tutte le coppie dei futures, non fra classi) → §9; R3 catena dei
prezzi fermi (ripartenza, fattibilita', ordine, conteggio delle serie) → §9; R4 mancanti per ora sulle sole sedute
presenti → §9; R5 universo fisso nelle repliche, date XNYS reali, stesse origini → §9; R6 flussi, ordine, semi diversi
per le prove, tentativi ammessi su (a, b) → §9; R7 lettura appaiata nella ripetizione sui candidati → §9 e statuto; R8
verifica del generatore e rimedi ammessi elencati prima → §9. Debito nuovo per Matteo: nella Checklist 10 la riga "un
negativo deve poter rifiutare, con il suo controllo positivo"; primitiva comune per la soglia appaiata in `motore/core`.

**Ottava passata (commit `dba01af`, 23/11): BLOCCA**, 1 bloccante, 6 riserve; B1 e R1-R8 della settima risultano chiusi
(la regola su δ scatta col difetto dichiarato, δ ≈ −5,4, e vale 0 esatto senza difetti: prova del gatekeeper su numeri
inventati). **Da fare prima del commit (1), tutto gratis (P6 punto 1):**
- **B1, verifica del generatore**: (a) se e' GUASTO lo script si ferma **prima** di simulare le repliche e l'unica
  uscita e' la verifica (test); (b) tolleranza col rumore di campionamento, per esempio max(2 punti; 25%;
  3·√(q(1−q)/n_anno)), perche' con ~245 sedute l'anno un generatore perfetto esce dalla tolleranza del 23/11 per caso
  nel 10-19% delle celle; (c) elenco ordinato e limitato delle correzioni ammesse del generatore (per esempio una
  componente a blocchi per i buchi di piu' ore), ognuna una deviazione P5; gratis solo un errore di codice.
- **R1** δ e' in unita' di **errore standard** di un anno (sd/√247), non di MDE; denominatore dalla sd sintetica (se la
  reale e' maggiore la regola e' piu' severa); test di unita' su δ nel punto 7.
- **R2** controllo positivo scritto per intero: EURUSD, USDJPY, GBPUSD, AUDUSD, XAUUSD, XAGUSD, BUND; quota di prezzi
  fermi in rampa lineare per seduta da 0 a 0,30 sulle 1.450 sedute, L = 3, nessun altro difetto.
- **R3** rimedi: si sommano o si sostituiscono; cosa succede quando finiscono; cosa cambia coi 30 minuti (13 rendimenti,
  soglie, Bartlett, Σ singolare con N > 13 nel §5, HAC del §10).
- **R4** su numeri inventati i prezzi fermi favoriscono la costante **anche a quota costante** (mediana di δ: −1,53 col
  5% su 7 strumenti, −4,33 col 15%, −5,86 col 5% su tutti; −0,66 con rampa 0→3%): con conteggi realistici N2
  probabilmente rifiutera'. La frase delle decisioni del 21/11 (EWMA e DCC seguono l'attenuazione, la costante no) va
  corretta come misura sintetica; i tre rimedi vanno provati sul difetto del controllo positivo prima del commit.
- **R5** se la mediana di δ e' sopra 0, accanto a un mancato rifiuto l'MDE si riporta anche come (fattore + δ)·errore
  standard.
- **R6** origini delle due medie e della sd: l'intersezione delle origini valide dei due gemelli.
Debito nuovo: Checklist 10, "una verifica di calibrazione si ferma prima di produrre la grandezza che decide".

## Prove sintetiche dei rimedi di N2 (23/11, prima del commit di congelamento)

Riserva R4 dell'ottava passata: prima di scegliere la misura, i rimedi si provano su difetti **inventati** (nessun dato,
P6 punto 1). Codice: `magazzino/registro/codice/struttura/` (`misura.py`, `previsioni.py`, `simula_n2.py`, 23 test
sintetici); esiti in `esiti/prove_rimedi_2026-11-23.json` (commit `fb2e388`) e `esiti/prove_ritardi_2026-11-23.json`
(commit `4fa85c4`): processo del §9, 1.450 sedute, 60 repliche per riga, seme 20261127, pipeline intera (esclusioni
comprese). Prezzi fermi con durata media 3 quarti d'ora; nessun altro difetto. In tabella: **mediana di δ per la
costante** (h = 1 / h = 5) ed esito; τ = 0,5.

| difetto | 15 min, Bartlett 1 (oggi) | 15 min, B2 | 30 min, B1 | **30 min, B2** | 30 min, B3 / B4 |
|---|---|---|---|---|---|
| rampa 0 → 10% su 7 | −1,59 / −1,95, campione corto in 3 repliche | −1,04 / −1,30 | −0,73 / −0,77 | **−0,41 / −0,41 PASSA** | guardia rotta |
| 5% fisso su 7 | −1,51 / −1,94 | −1,10 / −1,18 | −0,67 / −0,76 | **−0,36 / −0,46 PASSA** | guardia rotta |
| 15% fisso su 7 | campione insufficiente | idem | idem a h = 5 | idem a h = 5 | — |
| 5% fisso su tutti i 17 | −6,34 / campione insufficiente | −4,35 / idem | −2,86 / −3,52 | **−1,63 / −1,91 RIFIUTA** | guardia rotta |
| BUND 15%, altri 6 al 5% | −2,15 / −3,11, campione corto in 40 | — | — | — | — |
| idem, BUND fuori (rimedio iii) | −1,28 / −1,47 | — | — | — | — |

(15 min con B3 e B4: −0,83 / −0,91 e −0,62 / −0,66 sul 5% su 7, sempre oltre τ.) La guardia sul gemello sincrono
(costante che batte l'EWMA senza difetti) resta a 0 rifiuti su 60 con B1 e B2; a 30 minuti con B3 rifiuta in 3 e 12
repliche su 60, con B4 in 46 e 59: con 13 rendimenti per seduta e tre o quattro ritardi la Σ di ogni giorno e' cosi'
rumorosa che la costante batte l'EWMA anche senza difetti, e il negativo non vale.

**Errore di codice trovato nella prova e corretto**: la soglia della guardia era fissa a 35 (giusta per 500 repliche)
anche con 60 repliche, dove il quantile al 97,5% e' 7; il file `prove_ritardi` riporta quindi "PASSA" per 30 minuti
con B3, che e' **GUASTO** (12 su 60 a h = 5). Ora la soglia dipende dal numero di repliche (`soglia_guardia`, test). I
file degli esiti non si riscrivono: questa e' la lettura corretta.

**Lettura (numeri inventati, da non confondere con i dati veri).**
1. I prezzi fermi favoriscono la costante sempre, anche a quota costante (conferma la R4 dell'ottava passata, ora con
   le esclusioni): la frase delle decisioni del 21/11 sull'attenuazione aveva la direzione sbagliata.
2. A 15 minuti nessun numero di ritardi porta δ sotto τ gia' col 5% di prezzi fermi su 7 strumenti; con lo stesso 5%
   su tutti i 17, o col 15% su 7, la regola del 25% di nulli e l'esclusione per unione **svuotano il campione**
   (all'orizzonte 5 restano meno di 50 origini).
3. **30 minuti con Bartlett a 2 ritardi** e' l'unica misura provata che passa col 5% su 7 e con la rampa al 10%,
   con la guardia pulita; col 5% su tutti i 17 rifiuta comunque (−1,6 / −1,9).
4. Il controllo positivo dichiarato nel §9 (rampa fino al 30%) svuota il campione: va ridefinito.
5. Se N2 passi davvero dipende dalle quote vere di prezzi fermi per strumento, che si sapranno solo dai conteggi.

## Prove prima del commit di congelamento (23/11, misura a 30 minuti con Bartlett a 2 ritardi)

Script `magazzino/registro/codice/struttura/prove_prima_del_commit.py`, esito in `esiti/prove_prima_del_commit.json`
(commit `083db54`), 1.450 sedute, 500 repliche, soli dati sintetici.
- **Verifica del processo** (seme 20261125): **passa al primo tentativo**, (a, b) = (0,06; 0,93): il gemello sincrono
  rifiuta nella guardia **0 volte su 500** a h = 1 e a h = 5; matrici non valide 0; nessun campione insufficiente.
- **Controllo positivo** (seme 20261126; 5% fisso di prezzi fermi su tutti i 17, durata della catena 3 mezz'ore sulla
  griglia della misura): **GUASTO, non scatta**. In **500 repliche su 500** il campione e' insufficiente (meno di 50
  origini comuni ai due gemelli): con 13 rendimenti per seduta bastano 4 nulli per superare la soglia del 25%, e con
  l'esclusione per unione su 17 strumenti quasi ogni seduta cade. Il difetto l'aveva definito Claude prendendo il
  numero dalle prove precedenti, dove i fermi erano generati sui quarti d'ora e poi sottocampionati (molto piu'
  leggeri sulla griglia a 30 minuti): errore di Claude.

**Cosa dice, oltre al controllo positivo.** Con la misura a 30 minuti la regola dei nulli (25% di 13) e l'esclusione per
unione sono **fragili**: una quota di prezzi fermi diffusa svuota il campione prima che δ possa dire qualcosa. Lo
stesso potrebbe succedere sui dati veri. **Aperto, da decidere con Matteo prima del commit (1)** (gratis, P6 punto 1):
il controllo positivo (un difetto che lasci campione) e se la regola dei nulli e l'esclusione per unione vadano
riviste per la misura a 30 minuti.

## Prove prima del commit, seconda volta (24/11, due griglie)

Stesso script, esito in `esiti/prove_prima_del_commit_2026-11-24.json` (commit `bffefae`), 1.450 sedute, 500 repliche,
semi 20261128 e 20261129, soli dati sintetici.
- **Verifica del processo**: **passa al primo tentativo**, (a, b) = (0,06; 0,93): 0 rifiuti su 500 a h = 1 e a h = 5;
  matrici non valide 0.
- **Controllo positivo** (5% fisso di prezzi fermi su tutti i 17, catena di 3 quarti d'ora): a **h = 1 la regola
  scatta** (mediana di δ per la costante −2,44; quantili 5% e 95%: −5,26 e −0,02); a **h = 5 il campione e'
  insufficiente in 500 repliche su 500**: con l'esclusione per unione cade una quota di sedute tale che quasi nessuna
  finestra di cinque sedute consecutive resta intera. Per la regola scritta l'esito e' **GUASTO**.

**Lettura.** La regola su δ puo' rifiutare (h = 1). Il limite e' il bersaglio a 5 sedute con l'esclusione per unione:
con prezzi fermi diffusi l'orizzonte 5 non si misura, e lo stesso puo' succedere sui dati veri. Il controllo positivo
non si ridefinisce di nuovo finche' Matteo non decide come trattare un orizzonte senza campione (scelta di disegno,
gratis prima del commit): ridefinirlo fino a che passa adatterebbe il controllo al suo esito.

**Dopo la regola dell'orizzonte senza campione** (DECISIONS 2026-11-24 (2); stesso script e stessi semi, esito in
`esiti/prove_prima_del_commit_2026-11-24b.json`, commit `cced8e9`): **verifica del processo passata** (0 rifiuti su 500,
nessun orizzonte decaduto); **controllo positivo: scatta** ("RIFIUTA per misura"): l'orizzonte 5 decade (campione
insufficiente in 500 repliche su 500), a h = 1 mediana di δ −2,44 (11 repliche su 500 senza campione). Le due prove
prima del commit di congelamento sono **chiuse**; prossimo: revisione del gatekeeper su testo e codice sintetico, poi
la parte del commit (1) sui dati (scaricatore, loader, guardie, controllo di struttura, verifica del generatore, potenza).

## Nona passata del gatekeeper (2026-11-24, commit `f916dcc`): BLOCCA per la parte sui dati

Revisione con `git diff dba01af f916dcc`, codice estratto dal commit: **26 test verdi**; nessun dato letto, 0 trial.
Testo e codice sintetico **reggono**: processo, generatore, due griglie, Bartlett, fattore di scala, riscaldamento, δ
sull'intersezione delle origini, guardia, differenziale di Stein, `sd_hac` e uscite ammesse fanno cio' che il testo dice.
Le scelte prese dopo gli esiti sintetici sono coerenti col punto 1 di P6 del §8ter (gratis, prima del commit, su numeri
inventati, nessuna tocca τ o δ), **salvo il controllo positivo** (R1, B2). Il commit (1) sui dati **non si scrive** prima
di chiudere:

**Bloccanti**
- **B1, tolleranza della verifica del generatore** (§9): la regola per cella (strumento × anno, circa 102 celle) non e'
  corretta per il numero di celle: con un generatore perfetto almeno una cella esce per caso nel 27-35% delle corse
  (calcolo binomiale esatto del gatekeeper; anche con Bonferroni sulla normale 6-51% con q piccolo e anni parziali).
  Errore della tolleranza proposta dal gatekeeper all'ottava passata. Proposta: una cella fallisce se il p bilaterale
  binomiale del conteggio vero sotto Bin(n_anno; q̂), con q̂ dai 200 anni simulati, scende sotto 0,05 / numero di celle;
  regola per le celle sotto ~60 sedute (unite all'anno vicino o escluse).
- **B2, nessun controllo positivo a h = 5** (§9): nella configurazione congelata il positivo scatta solo a h = 1
  (mediana di δ −2,44); a h = 5 il campione e' insufficiente in 500 repliche su 500. I δ a h = 5 sotto soglia della
  tabella del 23/11 venivano da un'altra configurazione (validita' sui 30 minuti). Opzioni: (a) un positivo a h = 5 con
  lo stesso difetto (5% su 17, L = 3), lunghezza T fissata ora (per esempio 10 × 1.450), un tentativo, seme nuovo; se non
  scatta h = 5 esce da I3; (b) senza prova: h = 5 entra in N2 solo con un positivo che scatta, altrimenti esce.

**Riserve**
- R1: il positivo "5% su 17" e' stato scelto fra righe di cui si sapeva che scattavano: dimostra solo un difetto pesante
  (col 5% su 7 δ ≈ −0,4); va scritto nel §9.
- R2: DECISIONS 2026-11-24 dice che le prove sintetiche passavano con la misura a 30 minuti nella configurazione
  congelata: falso (la validita' era sui 30 minuti); correzione in una voce nuova; la giustificazione della misura e'
  **non riverificata** nella configurazione congelata.
- R3: `previsioni.py:105` esclude anche le origini col giorno t escluso (servono 1 + h sedute valide): va scritto nel §3
  e nel §10, o tolto per costante ed EWMA.
- R4: chiusure anticipate: riga tolta dall'indice delle sedute o giorno escluso che rompe la finestra? Va scritto.
- R5: la verifica del generatore guarda solo le quote per strumento; il campione dipende dall'esclusione per unione
  (difetti comuni fra strumenti) e da come i nulli si concentrano nei giorni. Proposte: quota di unione per anno nella
  verifica; correzione (3) "seduta mancante per tutti"; correzione (4) quota giornaliera di nulli dall'istogramma dei
  conteggi (chiave ammessa nel requisito 5).
- R6: rollover e pause sulla griglia a 15 minuti (oggi scritto solo per i 30).
- R7: "meno di 50 origini comuni nello sviluppo" sui dati veri: definizione di origine (R3), intervallo (quello della
  potenza), e un orizzonte esce se decade in N2 **o** sui conteggi veri.
- R8: regola dei semi: "seme fisso per configurazione; una rilettura dopo un cambio di regola riusa il seme".
- R9: test mancanti al punto 7: δ su un caso noto; "verifica GUASTO, nessuna replica"; `p_ora` frazionario con
  `p_giorno`; ingresso fisso confrontato con `ewma_rv` del pacchetto su tutta la serie (oggi per transitivita' e solo
  l'ultimo elemento).
- R10: pulizia: commento vecchio a `simula_n2.py:160`; `durata_catena` NaN con p0 > 0 deve fermarsi nel commit (1); riga
  del 23/11 in `_modifiche.md` con file cancellati e "23 test"; due griglie e decadenza senza riga propria in
  `_modifiche.md`; versioni di numpy e scipy negli esiti.

**Per il codice del commit (1)**, dopo B1-B2 e R3-R7: scaricatore e loader con fine al 2026-11-10; fuso una volta sola
col controllo contro il doppio; griglia di 27 prezzi; chiusure anticipate (R4); rollover e pause su entrambe le griglie
(R6); controllo di struttura con chiavi ammesse (q per cella, quota di unione, istogramma dei nulli se si adotta R5,
p_giorno, p_ora, p0, L̃); verifica del generatore come script a se' che si ferma prima delle repliche (regola B1);
wrapper di N2 (date XNYS reali, `durata_catena` che si ferma su NaN, universo dal controllo, seme 20261123, guardia sulle
chiavi a runtime, positivo a h = 5 secondo B2); potenza con data limite 2024-11-08 alla lettura e decadenza (R7);
`trial_ledger --check` come guardia.

Debito (decide Matteo): primitive comuni in `motore/core` per tolleranza per cella con correzione, chiavi d'uscita a
runtime e data limite; due righe per la Checklist 10 ("ogni orizzonte che decide ha il suo positivo nella configurazione
congelata"; "una tolleranza per cella si corregge per il numero di celle").
