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
- **Rendimenti a 15 minuti** (26 per seduta piena), log del prezzo bid: il primo prezzo e' l'**open della barra M5
  delle 9:30**, poi la **chiusura della barra M5 che finisce a ogni quarto d'ora** (quella che inizia alle :10, :25,
  :40, :55), fino alla chiusura della barra delle 15:55. Un prezzo mancante rende mancanti i due rendimenti adiacenti
  (nessun rendimento su 30 minuti). **Un rendimento mancante vale zero in tutti i prodotti** (decisione del 21/11,
  DECISIONS (7)): la matrice di Bartlett resta semidefinita positiva per costruzione anche con buchi; la diagonale un po'
  piu' bassa la assorbe il fattore di scala, uguale per tutte le previsioni.
- **Correzione per un ritardo** con **pesi di Bartlett** (½ sui prodotti incrociati a ritardo ±1) **su tutta la
  matrice, diagonale compresa**: toglie parte dell'effetto Epps delle quotazioni non sincrone e garantisce una matrice
  semidefinita positiva. Dopo la correzione resta un Epps residuo, uguale per tutte le previsioni: il bersaglio e'
  l'attesa di **questo** stimatore, non la correlazione vera, e va detto.
- **Giorni**: le sedute piene del calendario XNYS. Le **chiusure anticipate** (13:00) sono escluse e si contano. Un
  giorno entra solo se **tutti** gli N strumenti hanno almeno il 90% dei 26 rendimenti attesi: si esclude l'unione dei
  giorni mancanti, e si riporta per anno e per strumento quanti giorni esclude (controllo di selezione, come la
  volatilita': per ogni giorno escluso si riporta il rendimento assoluto della seduta contro la mediana, per vedere se le
  esclusioni coincidono con i giorni estremi).
- **Quotazioni ferme**: un rendimento a 15 minuti **osservato** ed esattamente nullo si conta; uno strumento-giorno con
  piu' del 25% di rendimenti nulli **fra quelli osservati** conta come mancante (un rendimento mancante, che vale zero
  solo nei prodotti, non e' un rendimento nullo: la quota si conta prima di mettere gli zeri, cosi' un buco non pesa due
  volte) (un prezzo fermo spinge la correlazione verso zero). La quota per strumento e per
  anno si misura nel controllo di struttura, prima di ogni statistica.
- **Rollover** dei CFD su futures (BUND, USTBOND, COPPER, NATGAS, WTI): il rendimento a 15 minuti che attraversa
  l'ora di un cambio di contratto si toglie **nel loader**, una volta sola, con le date del calendario del fornitore.
  Se il calendario non si trova si assume che il cambio avvenga **alla riapertura serale**, fuori dalla seduta USA,
  come verificato per il WTI di Dukascopy (DECISIONS 2026-11-13, salti alla riapertura del giorno 19): lo strumento
  resta, l'ipotesi e' dichiarata, e il controllo di struttura riporta per ogni strumento dove cadono le pause di
  quotazione (solo orari, nessun rendimento). **Se una pausa o una riapertura cade dentro W**, ogni giorno si toglie il
  rendimento a 15 minuti che la attraversa (vale come mancante); lo strumento resta se rispetta le soglie (DECISIONS (7)).
- **DAX**: entra solo se il controllo di struttura mostra barre nel 90% delle sedute per tutta la finestra (dopo le
  11:30 di New York e' fuori dalla seduta cash di Francoforte); altrimenti resta fuori.
- **Strumento fuori**: se nello sviluppo i suoi giorni mancanti (meno del 90% dei rendimenti, o oltre il 25% di
  rendimenti nulli) superano il 10% delle sedute XNYS, lo strumento esce dall'universo, deciso una volta sul controllo
  di struttura e prima di ogni perdita (con l'esclusione per unione, uno strumento spesso fermo cancellerebbe giorni a
  tutti).
- **Calendario**: XNYS di `exchange_calendars`, versione registrata nelle guardie (come la volatilita').
- **Controllo di struttura**: conteggi su sviluppo e blocco (le probabilita' di prezzo fermo per il G9 si prendono
  **solo dallo sviluppo**, sui soli rendimenti osservati, separate dalle probabilita' di rendimento mancante); il controllo di selezione (rendimento assoluto dei giorni
  esclusi contro la mediana) **solo sullo sviluppo**.
- **Orizzonte 5**: un'origine si esclude se uno dei 5 giorni e' escluso (come la volatilita').

## 4. Ingresso fisso e scala del bersaglio

**Ingresso fisso** (Matteo, D2 e decisioni del 21/11 in DECISIONS (5)): per ogni strumento i e ogni seduta t,
RV_{i,t} = somma dei quadrati dei 26 rendimenti a 15 minuti nella finestra W; σ̂²_{i,t} = **EWMA con λ = 0,94 di
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
(RV piu' il termine a ritardo 1); s_{i,t} = **media semplice** dei rapporti D_{i,τ} / σ̂²_{i,τ−1} sulle **500 sedute**
valide che finiscono a t (solo passato). La media semplice, non il rapporto di somme di c_t, perche' la perdita di Stein
e' lineare nel bersaglio e conta la media sui giorni (il rapporto di somme sarebbe una media pesata per la
volatilita'); la differenza si misura nel G9, non sui dati. I rendimenti standardizzati sono
z_{i,k} = r_{i,k} / (σ̂_{i,t−1} · √s_{i,t−1}) per i quarti d'ora k della seduta t.

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
sarebbe infinito se Σ e' singolare). Con N ≤ 17 < 26 rendimenti per seduta il rango a ritardo 0 non e' un vincolo.
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
  rendimenti a 15 minuti standardizzati** (covarianza di un quarto d'ora = H_t / 26, ritardo 0), sulla finestra mobile
  di **500 sedute**, ristima settimanale (H3). Previsione a 5 passi: E_t[Q_{t+k}] = Q̄ + (a + b)^{k−1}·(Q_{t+1} − Q̄),
  poi normalizzata (approssimazione di Engle e Sheppard 2001, dalla memoria: **in quarantena**, da verificare prima del
  passo 3).
- **Come si legge "batte l'EWMA ma non la costante"** (R3, scritto prima): un candidato che batte l'EWMA ma non la
  costante dice che la contrazione verso la media batte un filtro rumoroso, un risultato noto (Checklist 5), non che il
  candidato prevede la dinamica. Il pacchetto lo riporterebbe cosi'.
- I candidati (PCA a k fattori con k da una regola fissata prima, contrazione verso la costante, raggruppamenti,
  regimi) e la combinazione semplice si elencano al passo 3, con sottofamiglie e quote.

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
- Il +0,791 del controllo delle grandezze e' la media dei **20 indici del pool libero** di A1 (TREND_A1_HELDOUT_POWER
  §4), non delle quattro azioni USA (citazione corretta).
- **Unita' di conto** (C1, G8): proposta, una serie = **modello × orizzonte** sull'intera matrice (un universo unico);
  si fissa al passo 3.
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
  diagonale (LIFECYCLE §8ter, "Ingresso fisso da un'altra famiglia"); al passo 3 si scrive come si riportano le
  perdite in quel periodo.
- **Correlazioni medie per classe** gia' calcolate su dati D1 (A1 §4, §8, §9): non sulla misura di I3, ma note.
- **Contaminazione** (H6, Checklist 5): quasi tutto il periodo dei dati (dal 2019 al 2026-05) precede il knowledge
  cutoff del modello (2026-05-31), compreso lo shock dei dazi di aprile 2025 nel blocco; universo, benchmark e misura li
  ha proposti Claude.
  Fatti famosi sulla grandezza ("le correlazioni salgono nelle crisi"; azioni-obbligazioni positive nel 2022) confermati
  dal test porterebbero poca informazione nuova.

## 9. Controllo della pipeline (G9, rimedio del bloccante B3)

Processi simulati **attraverso la misura vera** (26 rendimenti a 15 minuti, standardizzazione con l'ingresso fisso,
fattore di scala, correzione di Bartlett, rendimento mancante = zero), con due ingredienti dichiarati:
- **volatilita' marginali che l'EWMA sbaglia**: un **GJR per strumento con parametri stimati sui rendimenti di
  sviluppo**, solo dopo il commit di candidati e quote e **senza riportarli** (DECISIONS (7)): senza, l'errore
  condizionato dell'EWMA e' zero e il controllo non vede il limite del §4;
- **quotazioni non sincrone**: per ogni strumento una probabilita' di prezzo fermo per quarto d'ora presa dal controllo
  di struttura (solo conteggi di rendimenti nulli, nessuna statistica sui rendimenti). La frase "il benchmark e' il
  previsore esatto" vale solo se la misura simulata non ha Epps residuo: se ne ha, un rifiuto del negativo misura la
  distorsione della misura, e va letto cosi'.

**N2, fissato ora per intero e prima della potenza** (decisione del 21/11, DECISIONS (9)). Gira dopo il controllo di
struttura (§10 (3)) e prima del calcolo della potenza (§10 (4)), quindi dopo i **soli conteggi**: se rifiuta, il ritorno
al passo 2 e' davvero il punto 2 di P6 del §8ter (deviazione, 0 trial).
- **Processo**: volatilita' **costante e unitaria** per ogni strumento (l'EWMA la prevede esattamente dopo l'avvio);
  l'attesa della matrice **misurata** segue la ricorsione M_t = 0,94·M_{t−1} + 0,06·Σ_{t−1} (l'EWMA e' il previsore
  esatto del bersaglio misurato, non della correlazione vera); la correlazione vera dei 26 rendimenti di ogni seduta e'
  quella che, attraverso la misura, da' in attesa M_t (la mappa fra correlazione vera e misurata si calcola per
  simulazione prima della corsa, con le sole probabilita' in ingresso); M parte dalla matrice identita'.
- **Quotazioni non sincrone e buchi**: per ogni strumento e per anno, la probabilita' di prezzo fermo (sui rendimenti
  osservati) e quella di rendimento mancante, dai conteggi dello sviluppo; si generano sia i prezzi fermi sia i
  mancanti, con le regole della misura vera (mancante = zero, soglie del 90% e del 25%).
- **Previsioni confrontate**: EWMA (benchmark) contro **costante** e contro **persistenza** (i candidati non esistono
  ancora), con le regole e le finestre del §6.
- **Test**: per ogni confronto e orizzonte, Diebold-Mariano a una coda sul differenziale di Stein ("l'alternativa batte
  l'EWMA"), correzione HLN, errori HAC con max(h − 1, 4) ritardi, al **5%**; **500 repliche**, ognuna lunga quanto lo
  sviluppo comune (sedute contate dal controllo di struttura), seme fisso.
- **Soglia**: rifiuta se la quota di repliche che rifiutano supera il limite alto dell'intervallo binomiale al 95%
  attorno al 5% (con 500 repliche circa 6,9%), in almeno un confronto.
- **Conseguenza, scritta ora**: se N2 rifiuta, la misura e' distorta dall'Epps residuo: il test non va avanti e si torna
  al passo 2 (punto 2 di P6). Se non rifiuta, si calcola la potenza.
- Dopo il passo 3, N2 si **ripete** sui candidati insieme a N1 e al positivo; le conseguenze di quelle uscite si
  scrivono nel commit del passo 3, prima che giri qualunque configurazione del G9.

**Ordine di N1 e del positivo**: solo dopo il commit di candidati, sottofamiglie, quote e conseguenze (passo 3) si
stimano GJR e DCC e girano N1, il positivo e la ripetizione di N2; i parametri stimati non si riportano prima. Lo script
del G9 si rifiuta di partire senza quel commit (percorso protetto pulito, hash registrato).
- **negativo, in due configurazioni** (ogni rifiuto ha una sola causa e una conseguenza scritta ora):
  - **N1**: marginali GJR (l'EWMA sbaglia la scala) e quotazioni **sincrone**. Se rifiuta oltre la soglia, si passa al
    bersaglio alternativo del §4;
  - **N2**: volatilita' che l'EWMA prevede esattamente e quotazioni **non sincrone** come nello sviluppo; fissato per
    intero sotto, gira prima della potenza;
  - in entrambe la correlazione segue la ricorsione EWMA 0,94 **del bersaglio misurato** (il processo esatto per lo
    stimatore, non per la correlazione vera: si scrive al passo 3); **soglia**: il limite alto dell'intervallo binomiale
    al 95% attorno alla quota, con le repliche fissate al passo 3. Le rifiniture P4 dei round 2-3 entrano anche nel
    negativo (un candidato che legge le diagonali passate puo' prevedere l'errore dell'EWMA e vincere per bravura sulla
    volatilita');
- **positivo**: un **DCC(1,1) con i parametri stimati sulle ultime 500 sedute comuni dello sviluppo** (H3), a scelte
  congelate: e' il benchmark forte, non un candidato, quindi 0 trial. In ogni replica il DCC **si ristima** con la stessa
  verosimiglianza della pipeline (cosi' si mette alla prova anche la differenza fra verosimiglianza a ritardo 0 e
  bersaglio con Bartlett). Il test deve trovare il DCC contro l'EWMA almeno nell'80% delle repliche.
- Il **rapporto effetto/MDE** del positivo si scrive **prima di contare qualunque trial**: se il disegno non vede
  l'effetto di un DCC realistico, lo si dice prima, non dopo 100 trial (lezione del 2026-11-20).
- Numero di repliche e soglie come la volatilita' (p puntuale dello SPA, DECISIONS 2026-11-19 (2)), da fissare al
  passo 3.

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

**MDE** = fattore × deviazione HAC / √n, con n = sedute dell'holdout (da fissare al passo 3: si riporta per 1 e 2 anni).
Fattori a una coda all'80% (`fattore_potenza`, calcolati dal gatekeeper il 21/11): **2,486** (α 5%), **2,802** (2,5%),
**3,083** (1,25%), **3,339** (0,625%); quello giusto e' la prima soglia di Holm dell'ipotesi elementare, quando le quote
saranno fissate.

**Trial**: 0. EWMA e costante sono benchmark e riferimento, non varianti (precedente: la volatilita' non li ha contati,
VOLATILITA_PREREGISTRATION §5); condizioni: la finestra della costante e' fissata ora (500 sedute), e la costante non
puo' diventare lo strumento consegnato a partire da questi dati.

## Requisiti del commit (1) (dalla quinta passata del gatekeeper, 21/11)

Il gatekeeper rivede il diff del commit prima di ogni corsa. Il commit contiene:
1. **contenuto**: questo referto, la voce DECISIONS, il codice in una cartella nuova sotto `magazzino/registro/codice/`
   con i test; nessun dato degli 8 strumenti (non ancora scaricati); lo scaricatore (importato da
   `volatilita/scarica_dukascopy.py`) con date d'inizio e di fine fisse, fine al 2026-11-10;
2. **guardie** sul modello di `volatilita/guardie.py`, in testa a ogni script, ferme al primo errore: percorsi protetti
   puliti in git (referto, LIFECYCLE, contatore, cartella di I3, `motore/core`, `motore/tests`, i moduli della
   volatilita' importati e `volatilita/hash_dati.json`), hash del commit in ogni uscita; versioni fissate (Python 3.12,
   numpy, pandas, scipy, `exchange_calendars` 4.13.2; `arch` solo dal passo 3), lo script si ferma se non coincidono;
   sha256 dei 9 M5 contro `volatilita/hash_dati.json` (letto, mai riscritto) e degli 8 nuovi registrati una volta sola
   subito dopo il download (file temporaneo e sostituzione, rifiuto se esiste); data massima di ogni file ≤ 2026-11-10;
   `trial_ledger --check` a 0; ordine: la potenza parte solo se esistono, committati, l'esito della verifica delle
   fonti, il controllo di struttura, gli hash degli 8 e l'esito di N2;
3. **data della potenza**: fine al 2024-11-08 scritta nel codice, applicata **alla lettura** prima di ogni rendimento,
   controllata su ogni oggetto derivato; un test con una seduta successiva deve fermare lo script;
4. **uscita della potenza, nessun canale aperto**: un dizionario con chiavi ammesse (commit, versioni, sha256; per
   h ∈ {1, 5} numero di origini, ritardi HAC, deviazione HAC **centrata** del differenziale; sedute dell'holdout a 1 e 2
   anni dal solo calendario; fattori e MDE); una chiave in piu' ferma lo script (un test aggiunge `media`). Su nessun
   canale (schermo, log, file, cache, grafici, messaggi d'errore, oggetti restituiti): media, segno, t, p, quota di
   giorni vinti, perdite per modello, Frobenius, serie dei differenziali, matrici o livelli di correlazione, σ̂², RV, s,
   rapporti D/σ̂², media di z². La serie dei differenziali vive solo in memoria e passa a una funzione che restituisce la
   sola deviazione; gli errori riportano data e tipo, non valori. Non si ripete l'abitudine della volatilita' di salvare
   le perdite in cache;
5. **uscita del controllo di struttura e di N2**: solo conteggi per strumento e per anno (sviluppo e blocco separati),
   probabilita' per il G9 dal solo sviluppo, orari delle pause, copertura del DAX, regola del 10%; il controllo di
   selezione solo sullo sviluppo; per N2 le quote di rifiuto per confronto e orizzonte e l'esito rispetto alla soglia;
6. **test su dati sintetici**, verdi: prezzi e griglia; fuso applicato una volta nel loader e protetto dal doppio;
   rollover tolto una volta; Bartlett semidefinita con zeri; nulli sui soli osservati; esclusione per unione, chiusure
   anticipate, orizzonte 5; fattore di scala con diagonale media vicina a 1 su un processo EWMA esatto; differenziale di
   Stein uguale alla differenza delle perdite piene; EWMA, costante e persistenza definite positive a diagonale 1;
   riscaldamento (indici 50, 550, 600); ingresso fisso identico bit per bit alla formula del pacchetto (importata);
   deviazione di Newey-West identica a `volatilita/potenza.py:sd_newey_west`; le guardie di data e di campi.

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
della volatilita' (§8); P4; la frase del §2 sul vantaggio che coincide con gli anni di dati peggiori. Restano confermative
solo se, oltre a quella dispersione e ai conteggi, **nessun'altra informazione** su perdite o differenziali e' stata
vista; altrimenti vale il punto 3 di P6.

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
del 10% per lo strumento, DAX, prezzi) adottate insieme. Restano al passo 3: candidati, sottofamiglie, quote, unita' di conto, holdout,
repliche del G9, P4; inoltre, prima che N1 e il positivo girino: la verosimiglianza del DCC sul bersaglio alternativo
(oggi usa i rendimenti standardizzati, che quel bersaglio toglie); in N2 le probabilita' di mancante e di prezzo fermo
**per strumento e per anno**, generando anche i mancanti (con mancante = zero e prezzi fermi la correlazione misurata si
attenua di circa √((1−p_i)(1−p_j)), e se le quote cambiano negli anni EWMA e DCC seguono l'attenuazione e la costante no:
un vantaggio sulla qualita' dei dati, non sulla dinamica); nel §2 una frase su cosa dira' il pacchetto se il vantaggio
coincide con quegli anni.

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

*(sesta passata: da compilare)*
