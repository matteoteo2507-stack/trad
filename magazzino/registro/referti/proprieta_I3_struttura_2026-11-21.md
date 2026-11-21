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

Tutte le scelte qui sotto sono **fissate ora**, prima di ogni dato; cambiarle dopo e' una variante (C3).
- **Finestra comune W**: seduta USA, 9:30-16:00 New York, secondo il calendario di borsa di New York (XNYS). Le barre
  Dukascopy (bid, ora d'inizio in UTC) si convertono all'ora di New York col fuso, quindi i cambi d'ora europei e
  americani non spostano la finestra; DAX e BUND, quotati su orari europei, si leggono comunque in ora di New York.
- **Rendimenti a 15 minuti** (26 per seduta piena), log del prezzo bid all'ultima barra M5 di ogni quarto d'ora, griglia
  allineata alle 9:30 New York.
- **Correzione per un ritardo** con **pesi di Bartlett** (½ sui prodotti incrociati a ritardo ±1): toglie parte
  dell'effetto Epps delle quotazioni non sincrone e garantisce una matrice semidefinita positiva (con peso 1 potrebbe
  non esserlo). Scelta di Claude per correttezza, dichiarata.
- **Giorni**: le sedute piene del calendario XNYS. Le **chiusure anticipate** (13:00) sono escluse e si contano. Un
  giorno entra solo se **tutti** gli N strumenti hanno almeno il 90% dei 26 rendimenti attesi: si esclude l'unione dei
  giorni mancanti, e si riporta per anno e per strumento quanti giorni esclude (controllo di selezione, come la
  volatilita': per ogni giorno escluso si riporta il rendimento assoluto della seduta contro la mediana, per vedere se le
  esclusioni coincidono con i giorni estremi).
- **Quotazioni ferme**: un rendimento a 15 minuti esattamente nullo si conta; uno strumento-giorno con piu' del 25% di
  rendimenti nulli conta come mancante (un prezzo fermo spinge la correlazione verso zero). La quota per strumento e per
  anno si misura nel controllo di struttura, prima di ogni statistica.
- **Rollover** dei CFD su futures (BUND, USTBOND, COPPER, NATGAS, WTI): il rendimento a 15 minuti che attraversa
  l'ora di un cambio di contratto si toglie **nel loader**, una volta sola; le date si prendono dal calendario del
  fornitore. Se il calendario non si trova, lo strumento resta fuori (regola fissata ora, non dopo aver visto i salti).
- **DAX**: entra solo se il controllo di struttura mostra barre nel 90% delle sedute per tutta la finestra (dopo le
  11:30 di New York e' fuori dalla seduta cash di Francoforte); altrimenti resta fuori.

## 4. Ingresso fisso e scala del bersaglio

**Ingresso fisso** (Matteo, D2 e decisioni del 21/11 in DECISIONS (5)): per ogni strumento i e ogni seduta t,
RV_{i,t} = somma dei quadrati dei 26 rendimenti a 15 minuti nella finestra W; σ̂²_{i,t} = **EWMA con λ = 0,94 di
RV_i fino alla seduta t** (la formula del pacchetto, applicata alla stessa finestra del bersaglio, Matteo).
**Distribuzione marginale: gaussiana** (quasi-verosimiglianza), dove serve una verosimiglianza (DCC) (Matteo).

**Fattore di scala** (Matteo, rimedio del bloccante B1). Senza, la diagonale del bersaglio non vale 1 e la perdita di
Stein premia correlazioni gonfiate o sgonfiate (calcolo sintetico del gatekeeper: con diagonale 0,5 e correlazione vera
0,5 la Stein premia 0,725). Come c_t della volatilita' (VOLATILITA_PREREGISTRATION §3, "Scala del bersaglio"):
s_{i,t} = (somma di RV_i) / (somma di σ̂²_i) sulle **1.000 sedute** che finiscono a t, solo passato. I rendimenti
standardizzati sono z_{i,k} = r_{i,k} / (σ̂_{i,t−1} · √s_{i,t−1}) per i quarti d'ora k della seduta t. Resta l'errore
**condizionato** dell'EWMA (la diagonale vale 1 in media, non giorno per giorno), dichiarato.

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
  diagonale 1. Nessun parametro stimato.
- **Riferimenti di skill** (G3): correlazione **costante** = media delle matrici realizzate (normalizzate) sulle 1.000
  sedute precedenti (finestra fissa, H3); **persistenza** = la matrice di ieri normalizzata, regolarizzata come
  0,9·R_t + 0,1·I (regola fissata ora, copre anche il caso non definito positivo).
- **Benchmark forte**: **DCC(1,1)** sulle stesse matrici, gaussiano, stimato sulla finestra mobile di 1.000 sedute con
  ristima settimanale (H3); previsione a 5 passi con l'approssimazione della matrice Q a piu' passi (da citare con la
  fonte alla bozza).
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
  I3 non riporta statistiche di volatilita' su quel blocco (§4).
- **Gli 8 strumenti nuovi** (Matteo): letti da I3, **perdono in modo irreversibile** lo stato di "mai visti" per la
  calibrazione dell'EWMA del ridisegno della volatilita'. Restano a quel ridisegno gli altri strumenti Dukascopy mai
  toccati (A1 §8 ne censiva circa 280 fra le azioni USA; bond e commodity sono pochi).
- **Dopo la pre-registrazione del ridisegno della volatilita'**, sui dati del suo test I3 non riporta nulla della
  diagonale (LIFECYCLE §8ter, "Ingresso fisso da un'altra famiglia"); al passo 3 si scrive come si riportano le
  perdite in quel periodo.
- **Correlazioni medie per classe** gia' calcolate su dati D1 (A1 §4, §8, §9): non sulla misura di I3, ma note.
- **Contaminazione** (H6, Checklist 5): il periodo 2024-11 → 2026-05 precede il knowledge cutoff del modello
  (2026-05-31) e contiene lo shock dei dazi di aprile 2025; universo, benchmark e misura li ha proposti Claude.
  Fatti famosi sulla grandezza ("le correlazioni salgono nelle crisi"; azioni-obbligazioni positive nel 2022) confermati
  dal test porterebbero poca informazione nuova.

## 9. Controllo della pipeline (G9, rimedio del bloccante B3)

Due processi simulati **attraverso la misura vera** (26 rendimenti a 15 minuti, ritardi di quotazione come nei dati,
standardizzazione con l'ingresso fisso, fattore di scala, correzione di Bartlett):
- **negativo**: la correlazione segue esattamente la ricorsione EWMA 0,94 (il benchmark e' il previsore esatto,
  l'analogo dell'IGARCH della volatilita'): il test deve rifiutare al massimo alla sua quota;
- **positivo**: un **DCC(1,1) con i parametri stimati sullo sviluppo** (Matteo), a scelte congelate: e' il benchmark
  forte, non un candidato, quindi 0 trial. Il test deve trovare il DCC contro l'EWMA almeno nell'80% delle repliche.
- Il **rapporto effetto/MDE** del positivo si scrive **prima di contare qualunque trial**: se il disegno non vede
  l'effetto di un DCC realistico, lo si dice prima, non dopo 100 trial (lezione del 2026-11-20).
- Numero di repliche e soglie come la volatilita' (p puntuale dello SPA, DECISIONS 2026-11-19 (2)), da fissare al
  passo 3.

## 10. Piano della potenza (prima di raccogliere)

**Ordine** (rimedio del bloccante B2): (1) commit di tutte le scelte dei §3-§9, del codice e delle guardie (sha256 dei
file, nessuna seduta oltre il 2024-11-08 letta per l'MDE); (2) verifica delle fonti sul testo (§5); (3) controllo di
struttura (solo conteggi: barre, giorni, quote di rendimenti nulli, DAX, rollover); (4) calcolo.

**Cosa riporta** (Matteo): **solo la deviazione HAC** del differenziale di perdita fra EWMA e correlazione costante,
per orizzonte, **senza media ne' segno**: cosi' nessun numero dice quale modello vince, e i candidati si possono ancora
scegliere al passo 3. E' un ordine di grandezza (un differenziale fra due previsioni lontane puo' essere piu' disperso
di quello fra un candidato e l'EWMA); la prova vera e' il rapporto effetto/MDE del positivo (§9).

**MDE** = fattore × deviazione HAC / √n, con n = sedute dell'holdout (da fissare al passo 3: si riporta per 1 e 2 anni).
Fattori a una coda all'80% (`fattore_potenza`, calcolati dal gatekeeper il 21/11): **2,486** (α 5%), **2,802** (2,5%),
**3,083** (1,25%), **3,339** (0,625%); quello giusto e' la prima soglia di Holm dell'ipotesi elementare, quando le quote
saranno fissate.

**Trial**: 0. EWMA e costante sono benchmark e riferimento, non varianti (precedente: la volatilita' non li ha contati,
VOLATILITA_PREREGISTRATION §5); condizioni: la finestra della costante e' fissata ora (1.000 sedute), e la costante non
puo' diventare lo strumento consegnato a partire da questi dati.

## Decisioni di Matteo del 21/11 (passo 2)

Misura intraday, orizzonte 1 e 5 giorni; perdita di Stein; benchmark EWMA 0,94; il blocco sigillato degli M5 si legge,
dichiarandolo; **fattore di scala** come c_t; gli **8 strumenti nuovi si spendono per I3**; la potenza riporta **solo la
dispersione**; positivo del G9 con parametri **stimati sullo sviluppo**; EWMA calcolata **sulla stessa seduta** del
bersaglio; marginale **gaussiana**. Restano al passo 3: candidati, sottofamiglie, quote, unita' di conto, holdout,
repliche del G9, P4.

## Revisione del gatekeeper

**Prima passata (commit `5ad5b98`): BLOCCA**, 4 bloccanti, 8 riserve. B1 scala del bersaglio → §4 (fattore di scala,
Matteo); B2 ordine e C3 → §10 (scelte congelate prima, solo dispersione, Matteo); B3 G9 mancante → §9 (Matteo per i
parametri); B4 dichiarazione falsa sull'ingresso fisso → §4 e §8 ("calcola ma non riporta"; strumenti nuovi spesi per
I3, Matteo). Riserve: R1 dichiarazioni di misura → §3; R2 singolarita' → §5; R3 insieme d'informazione e lettura di
"batte l'EWMA" → §4, §6; R4 orizzonte 5 e pacchetto → §2, §4, §5, §6; R5 potenza → §10; R6 universo, citazione A1,
majors, inizio, unita' → §7; R7 blocco, impegno N3 in DECISIONS, contaminazione → §8; R8 fonti prima della corsa → §5.

*(seconda passata: da compilare)*
