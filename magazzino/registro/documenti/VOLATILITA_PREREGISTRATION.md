---
tipo: preregistrazione
stato: APPROVATA
approvata: "2026-11-13, Matteo in sessione, sul testo del commit 7dea1e3"
aggiornato: 2026-11-19
decisione: "Matteo: gate degli strumenti e strada A (10-11/11); errore di famiglia 5% = 2,5% GARCH + 1,25% HMM + 1,25% premio di volatilita', holdout di due anni (11/11); orizzonte massimo 5 giorni, strumenti dei test piu' completi (11/11); varianti GARCH approvate, benchmark dell'HMM delegato a Claude secondo S4, premio di volatilita' a 30 giorni come definizione (13/11); dopo la prima G1: combinazione fissa nell'HMM, holdout non aperto se il controllo positivo fallisce, affermazioni per strumento, commit su branch nuovo (13/11). DECISIONS 2026-11-10, 2026-11-11, 2026-11-13"
metrica_corrente: "previsioni di sviluppo calcolate (commit 86fcdae, 19/11), solo descrittive; nessun calcolo sull'holdout"
nota: "Famiglia di STRUMENTI (binario `strumenti`, STRATEGY_LIFECYCLE §8ter): niente trade, niente R, niente DSR. Verdetto sul blocco di holdout 2024-11-11 -> 2026-11-10, aperto una volta. Cinque passate G1 il 13/11: quattro BLOCCA corrette, la quinta PASSA CON RISERVE (riserva chiusa). APPROVATA da Matteo il 13/11: da qui ogni modifica di §1-§6 e' una deviazione (§10); i passi del §7 si registrano in aggiunte datate (§11)."
---

# Pre-registrazione — Previsione della volatilita' (famiglia `volatilita`, binario `strumenti`)

Regole che questa pre-registrazione applica: [STRATEGY_LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md)
(sigle G, H, C, P, S). Fonti della letteratura: [referto del 10/11](../referti/gate_strumenti_volatilita_2026-11-10.md),
claim in quarantena. Dati e controlli: [motore/data/README](../../../motore/data/README.md), sezioni `volatilita_m5`,
`volatilita_mt5`, `futures_1m`. Famiglia nel contatore: `volatilita`. Il testo della prima bozza (quello rivisto dalla
prima passata G1) e' nel commit `a62f622`.

## 1. Cosa si misura, e cosa no

**Lo strumento.** Una previsione della varianza dei prossimi 1 e 5 giorni di borsa (e, per il premio di volatilita',
dei prossimi 30 giorni di calendario), fatta con i soli dati fino alla chiusura di oggi.

**La proprieta'.** La previsione ha una perdita **QLIKE** piu' bassa di quella di un benchmark semplice nominato qui,
fuori campione. Per il premio di volatilita': la varianza implicita nel VIX supera in media la varianza realizzata dei
30 giorni successivi.

**Cosa NON si misura.** Nessun rendimento, nessuna regola di trade. Un esito positivo dice "previsione piu' accurata",
non "piu' profitto" (§8ter, ultimo capoverso): il passaggio a una strategia (sizing, stop, filtri) lo testano i soci.

**Stessa grandezza = stessa famiglia (Checklist 10, punto 8).** Nessuna famiglia del contatore ha misurato
l'accuratezza di una previsione di varianza. `meanrev_vol` (rendimento di uno z-score di prezzo), il gradiente di
volatilita' di `trend_momentum` e la "gestione per volatilita' come segnale" (backlog §H) misurano **rendimenti**: un'altra
grandezza (verificato dalla prima G1). L'asse calmo/volatile di `motore/core/regime.py` (ATR) misura la stessa grandezza
dell'HMM ma non e' una famiglia: un esito dell'HMM **non** lo convalida.

## 2. Dati

| Strumento | File (fuori da git) | Usato da |
|---|---|---|
| SPX500, NAS100, DOW, RUSSELL, DAX | `motore/data/prezzi/volatilita_m5/<NOME>_M5.csv` (Dukascopy, bid, UTC) | 2015-01-02; RUSSELL dal 2018-08-08 (prima non ci sono dati) |
| XAUUSD, XAGUSD, WTI, EURUSD | stessa cartella | 2015-01-02 |
| VIX | `motore/data/cache/free/VIX_D1.csv` (CBOE, aggiornato al 2026-11-12) | solo premio di volatilita' |

**Perche' dal 2015.** Nel 2012-2014 il feed degli indici ha fino al 10% di barre ferme anche in seduta, EURUSD il 28-29%
sulle 24 ore, WTI il 19% nel 2014; dal 2015 lo 0-1% per tutti e nove (controlli dell'11/11, solo struttura, README dei
dati). Prima della corsa di sviluppo si rifa' `checklist_dati` (solo struttura) su tutti i file, con i conteggi per
strumento in un'aggiunta datata (riserva 3 della G1).

**Perche' M5 Dukascopy anche per oro ed euro** (§8ter G1 chiedeva l'oro da M1 e l'FX da H1, che erano i dati in casa
il 10/11): una sola fonte e una sola frequenza per tutti e nove riducono le differenze di rumore fra strumenti; M5 e' la
frequenza standard della RV (Liu-Patton-Sheppard 2015). La stagionalita' oraria di G3 non si applica: tutti i modelli
sono giornalieri.

**Versioni** (13/11): `arch` 8.0.0, `statsmodels` 0.14.6, `numpy` 2.4.4, `scipy` 1.17.1, `pandas` 3.0.2,
`exchange_calendars` 4.13.2, Python 3.12. Il codice controlla le versioni all'avvio e si ferma se cambiano.

## 3. Giorno, rendimenti e bersaglio (G1) — le somme tornano esatte

Rendimenti logaritmici **in percento**, prezzi bid. Barre Dukascopy con l'ora d'**inizio** della barra (UTC).

**Indici.** Calendario di borsa `exchange_calendars`: **XNYS** per SPX500, NAS100, DOW, RUSSELL; **XETR** per il DAX
(sedute, chiusure anticipate e festivi dal calendario, nei fusi America/New_York ed Europe/Berlin).
- *Apertura di seduta* P_ap = `open` della barra che inizia all'apertura del calendario (9:30 New York; 9:00
  Francoforte). *Chiusura di seduta* P_ch = `close` dell'ultima barra che inizia prima della chiusura del calendario
  (15:55 nei giorni normali, prima nei giorni a seduta ridotta).
- Rendimenti di seduta: il primo e' log(close/open) della prima barra, poi log(close_i/close_{i-1}) fra barre
  consecutive della seduta, anche se fra le due manca qualche barra. La loro somma e' esattamente log(P_ch/P_ap).
- Notte: n_t = log(P_ap,t / P_ch,t-1). **Rendimento del modello** r_t = n_t + somma di seduta = log(P_ch,t/P_ch,t-1).
- **Bersaglio giornaliero** v_t = n_t² + somma dei quadrati dei rendimenti di seduta (proxy della varianza da chiusura
  a chiusura).

**Strumenti a 24 ore** (oro, argento, petrolio, euro). Il giorno di borsa t comincia con la prima barra che inizia
alle 17:00 New York o dopo, e finisce con l'ultima barra che inizia prima delle 17:00 del giorno dopo (il giorno del
venerdi' comincia la domenica). Rendimenti: log(close/open) della prima barra, poi close su close. r_t = somma = log
(close dell'ultima barra / open della prima). v_t = somma dei quadrati. **Il rendimento a cavallo della pausa e del fine
settimana non entra ne' in r_t ne' in v_t**: nel petrolio Dukascopy, CFD su futures, li' cadono i salti di rollover
(nel 2015-2024 16 salti alla riapertura il giorno 19 del mese e il +29% del 19/04/2020; controllo del 13/11, solo
prezzi). La grandezza e' la varianza della giornata di contrattazione.

**Giorni esclusi** (con meno del 90% delle barre attese dal calendario o dalla griglia a 24 ore): restano nella stima
(il loro r_t e' esatto per costruzione), ma un'**origine di previsione e' esclusa** per un orizzonte se **un qualunque
giorno** della sua finestra di bersaglio e' escluso. Nessuna somma parziale. Si riportano i conteggi per strumento.

**Orizzonti.** h = 1: bersaglio v_{t+1}. h = 5: somma di v_{t+1..t+5}. Previsione a h = 5: somma delle previsioni a
1..5 passi del modello.

**Premio di volatilita'**, in %² come tutto il resto: IV_t = VIX_t² × 30/365 (VIX in punti percentuali annui alla
chiusura di t); RV_t = somma di v dell'SPX500 nei giorni di borsa in (t, t + 30 giorni di calendario]; premio
p_t = IV_t − RV_t. Esempio di ordine di grandezza: VIX 20 → IV ≈ 32,9 %²; con una volatilita' giornaliera dell'1,25%
per 21 giorni, RV ≈ 32,8 %².

**Scala del bersaglio** (bloccante 1 della G1). Per Patton (2011) la QLIKE ordina bene solo con una proxy non distorta;
se E[v] = c·E[r²] con c ≠ 1, premia chi prevede piu' alto. Regola fissata ora: c_t = (somma di v)/(somma di r²) sui
1.000 giorni di borsa che finiscono all'origine t (solo passato, la stessa finestra della stima). **c_t si applica solo
alle previsioni sulla scala dei rendimenti**, cioe' a tutte le varianti e a tutti i benchmark del verdetto (EWMA, GARCH,
GJR, EGARCH, HMM, combinazioni) e alla parte EWMA della variante iniettata del §7.5. **Non** si applica a cio' che e'
gia' sulla scala di v: HAR, persistenza (v di ieri), media di lungo periodo (media di v sulla finestra). Si riportano
c di sviluppo per strumento e, come descrittivo, le perdite senza riscalamento. Non si sceglie altro dopo la corsa di
sviluppo.

**Premio e scala.** Il premio usa v senza riscalamento (e' il confronto con un'implicita esterna): una distorsione di
livello della proxy sposta direttamente la media del premio, e con c < 1 la sposta verso il rifiuto. Si riporta quindi
il c dell'SPX500 nello sviluppo **con la direzione dell'effetto**, e come descrittivo il premio calcolato con la somma
dei r² (rendimenti chiusura su chiusura) al posto di v.

**Selezione delle origini.** Per i giorni esclusi si riporta |r_t| contro la mediana dello strumento: se i giorni
incompleti coincidono con quelli estremi, la regola seleziona il campione rispetto alla volatilita', e va detto.

## 4. Divisione dei dati (H1-H3)

- **Holdout**: dal **2024-11-11 al 2026-11-10** (due anni, comune a tutti; congelato nel commit `a62f622` del 13/11).
  Ultima origine: quella il cui bersaglio finisce entro il 2026-11-10 (h = 5: 2026-11-03; premio: 2026-10-09).
- **Sviluppo**: dal 2015-01-02. Nessun bersaglio di sviluppo cade nell'holdout: le origini di sviluppo si fermano
  5 giorni di borsa (30 di calendario per il premio) prima del 2024-11-11.
- **Stima**: finestra mobile di **1.000 giorni di borsa**, lunghezza fissa (H3); prima previsione quando la finestra e'
  piena (fine 2018 per quasi tutti; meta' 2022 per RUSSELL). **Ristima ogni 5 giorni di borsa**; fra una ristima e
  l'altra il filtro va avanti coi parametri congelati. Media zero, gaussiana (QMLE).
- **Solo filtraggio** (bloccante 2): con `arch`, stima con `last_obs` = giorno dopo l'origine e previsione dall'origine;
  con `statsmodels` solo `filtered_marginal_probabilities`, **mai** `predict` coi valori di default (che usa i
  lisciati) ne' `smoothed_marginal_probabilities`. Lo garantisce il test d'invarianza del §7.
- **Regimi nel blocco di holdout** (H6, dichiarati dalla cronologia pubblica, senza calcoli sui file): elezioni USA
  (novembre 2024), shock dei dazi USA (aprile 2025), conflitto USA-Iran nel 2026 (nota di geopolitica dell'hub). Il
  blocco non e' "calmo" per costruzione.
- **Contaminazione** (Checklist 5): circa l'80% dell'holdout (2024-11 → 2026-05) precede il cutoff del modello
  (2026-05-31), e il benchmark dell'HMM l'ha scelto un LLM. Rischio basso (il GJR e' la scelta di default della
  letteratura), dichiarato; il sottoblocco 2026-06-01 → 2026-11-10 si riporta a parte, descrittivo. Il premio positivo
  e' un risultato famoso (Carr-Wu 2009): confermarlo porta poca informazione nuova.

## 5. Sottofamiglie, varianti, benchmark (S1-S5, C1-C2)

| Nodo | Varianti (tutte nello SPA, C2) | Benchmark (S4) | Ipotesi elementari |
|---|---|---|---|
| **GARCH** | GARCH(1,1), GJR-GARCH(1,1,1), EGARCH(1,1,1) — `arch` | **EWMA, λ = 0,94** (RiskMetrics, zero parametri) | 18: una per (strumento, orizzonte): "almeno una variante ha QLIKE media piu' bassa di EWMA" |
| **HMM** | varianza a regimi di Markov sui rendimenti giornalieri con **2** e **3** regimi (`statsmodels` `MarkovRegression`, `switching_variance=True`, senza costante; previsione = probabilita' filtrata propagata con la matrice di transizione × varianza del regime); **combinazioni fisse 0,5·GJR + 0,5·HMM** con 2 e con 3 regimi | **GJR-GARCH(1,1,1)** sugli stessi rendimenti | 18: "almeno una variante ha QLIKE media piu' bassa del GJR" |
| **Premio di volatilita'** | uno (§3) | premio nullo | 1: "media del premio > 0" |

- **Perche' GJR e perche' la combinazione** (S4, "contenuto in piu' della probabilita' filtrata"): l'HMM usa i
  rendimenti giornalieri come il GJR, quindi il confronto e' a parita' d'informazione (contro HAR perderebbe per
  l'informazione intraday che non ha). Un HMM a varianza costante per regime puo' pero' contenere informazione utile e
  perdere lo stesso la gara; la combinazione a peso fisso 0,5 misura il contenuto in piu' nel senso di Giacomini-White
  (Matteo, 13/11, bloccante 5). Un mancato rifiuto vale per entrambe le domande, con l'MDE.
- **HMM (S5)**: regimi ordinati per varianza crescente a ogni stima, 20 partenze casuali con seme fisso, si tiene la
  verosimiglianza migliore; una stima che non converge usa i parametri della precedente, e si conta.
- **Premio a 30 giorni** (Matteo, 13/11): e' la definizione del VIX, non un orizzonte di trading. Solo SPX500.
- **Fuori dal contatore** (S1): Black-Scholes, Heston, SABR (solo teoria).
- **Riferimenti, non varianti** (riserva 5): HAR-RV di Corsi sulla RV, GARCH(1,1) come riferimento forte (G3), la media
  delle tre varianti GARCH, la media di lungo periodo (varianza della finestra), la persistenza (varianza di ieri).
  Entrano solo nei descrittivi (MCS, skill). **Nessuno di loro puo' diventare lo strumento consegnato a partire da
  questo holdout**: se HAR vince l'MCS, e' un risultato esplorativo (P1), da confermare su dati forward.

**Contabilita' (C1).** Serie = modello × strumento × orizzonte: GARCH 3 × 9 × 2 = **54**, HMM 4 × 9 × 2 = **72**,
premio **1**. Totale **127**, contati nel contatore quando le previsioni vengono calcolate.

## 6. Gate statistico e verdetto (G2, G4, G8)

- **Perdita primaria**: QLIKE = log(f) + v/f (f previsione riscalata, v bersaglio, entrambi in %²); secondaria MSE
  sulla varianza (descrittiva).
- **Test per coppia** (nodi GARCH e HMM): SPA di Hansen **studentizzato** (p-value `consistent`) delle varianti del
  nodo contro il benchmark, con `spa_studentizzato` di `motore/core/verifiche.py` (commit `7170515`); **non** con il
  parametro `studentize` di `arch`, che nella versione 8.0.0 non cambia la statistica (quarta G1: con arch un modello
  buono passa da p = 0,000 a 0,301 se gli si affianca un modello rumoroso; studentizzato resta a 0,000). Ogni StepM
  (descrittivi e §7.6) passa da `stepm_studentizzato`, sullo stesso ingresso: e' la versione a passi dello SPA
  (Hsu, Hsu e Kuan 2010), studentizzata, non il Romano-Wolf originale (quinta G1). Bootstrap stazionario, blocco √T, **100.000 ripetizioni** (`repliche_per_distinguere`: ne servono 44.193
  alla prima soglia del GARCH e 88.446 a quella dell'HMM perche' l'intervallo del p-value sia largo un quarto della
  soglia), seme 20261113. p-value = (b+1)/(B+1) con `pvalue_spa` (che passa da `pvalue_mc`), riportato con `low`/`high`. Ogni SPA del
  verdetto gira su **4 semi dichiarati** (20261113-20261116) e si sommano superamenti e ripetizioni (400.000 in tutto);
  p-value e intervallo entrano in `procedura_grafica_nodi` con l'argomento `intervalli` (commit `bcc7b4b`): un'ipotesi si
  rifiuta solo se **tutto l'intervallo** sta sotto la soglia **corrente**, a ogni passo, anche dopo che il riciclo l'ha
  alzata. Un nodo uscito prima dell'apertura si toglie dalla procedura (passarlo vuoto e' un errore).
- **Test del premio** (bloccante 4): **t a una coda su osservazioni mensili non sovrapposte** (l'ultimo giorno di borsa
  di ogni mese dell'holdout come origine, circa 23 osservazioni), n − 1 gradi di liberta'. Le osservazioni giornaliere
  sovrapposte con Newey-West restano descrittive.
- **Affermazioni per strumento** (Matteo, 13/11, riserva 4): procedura grafica (Bretz et al. 2009) sulle **37 ipotesi
  elementari**, con la primitiva `procedura_grafica_nodi` di `motore/core/verifiche.py` (commit `987b007`, testata
  contro Holm e contro il riciclo). Quote iniziali dei nodi: GARCH 2,5%, HMM 1,25%, premio 1,25%. Dentro un nodo la
  quota si divide in parti uguali fra le ipotesi non ancora rifiutate (Holm: prima soglia 2,5%/18 e 1,25%/18). Quando
  tutte le ipotesi di un nodo sono rifiutate, la sua quota passa **in parti uguali ai nodi non esauriti** (S2,
  DECISIONS 2026-11-11), e dentro ciascuno alle ipotesi non rifiutate. Si itera finche' non si rifiuta piu' nulla. E' il
  limite con archi epsilon della procedura di Bretz et al. (2009); l'errore e' controllato su ogni affermazione per
  strumento e orizzonte.
- **Verdetto per coppia**: *confermato* (rifiutata), oppure *non dimostrato, MDE = ...*; mai "refutato" senza MDE.
- **Descrittivi** (non decidono): StepM (quali varianti), MCS al 10% con statistica di range (l'MCS di `arch` non e'
  stato riesaminato sulla studentizzazione: va controllato prima che un MCS serva a una scelta) su tutti i modelli e i
  riferimenti, skill rispetto a media di lungo periodo e persistenza, Mincer-Zarnowitz in livelli con errori HAC (G5),
  sensibilita' al blocco (√T/2 e 2√T), perdite senza riscalamento, premio giornaliero con Newey-West (21 ritardi),
  sottoblocco dopo il cutoff.
- **G7 (code)**: non si applica: lo strumento non promette quantili.
- **Confronti complementari nell'holdout** (non decidono, H1): RV dei futures CME a 1 minuto (`futures_1m`, dal
  2025-11; salti di rollover tolti nel loader) e del feed MT5 (`volatilita_mt5`, dal 2025-06) contro la RV Dukascopy.

## 7. Prima dell'apertura — nell'ordine, ogni passo in un'aggiunta datata e in un commit

0. **Guardie** (bloccante 6 della prima G1): prima di ogni corsa lo script verifica che questa pre-registrazione, il
   contatore, il codice della famiglia (`magazzino/registro/codice/volatilita/`), `motore/core/` e `motore/tests/`
   **esistano** e non abbiano modifiche non committate, e registra l'hash del commit. Un percorso inesistente ferma la
   corsa (la guardia dello studio H1 punta a percorsi di prima del riordino e passerebbe a vuoto: non si copia). **Dati**:
   all'approvazione si registra lo sha256 dei nove file M5 e del VIX in un file versionato accanto al codice; ogni corsa
   lo ricalcola e si ferma se cambia (i CSV sono fuori da git: un nuovo scarico cambierebbe i dati senza traccia).
1. **Test d'invarianza al futuro**, in `motore/tests` o accanto al codice, **bloccante**: per ogni modello (EWMA,
   GARCH, GJR, EGARCH, HMM 2 e 3, combinazioni, HAR, persistenza, media di lungo periodo) la previsione **finale**
   (riscalata con c_t dove si applica) all'origine t, calcolata sulla serie vera e sulla stessa serie con i dati dopo t
   sostituiti da rumore, deve essere identica (tolleranza 1e-10). Origini: 20 a caso nello sviluppo, piu' i casi
   speciali: giorni di ristima, il giorno prima e quello dopo, e le posizioni delle prime origini dell'holdout, queste
   su una serie **sintetica** con lo stesso calendario (l'holdout resta chiuso).
2. **Controlli negativi** (dati simulati, prima della corsa di sviluppo). Bersaglio simulato = varianza vera ×
   exp(σε − σ²/2), ε gaussiano, **σ = 0,6** (rumore a media 1; il valore dei dati veri si riporta dopo, descrittivo).
   Varianza iniziale 1 %². La pipeline simulata e' quella vera, c_t compreso.
   - **GARCH**: processo IGARCH con λ = 0,94 e **ω = 0**, per il quale l'EWMA e' il previsore esatto; ogni serie si
     **riscala per una costante** in modo che la varianza vera media della valutazione sia 1 %² (l'EWMA e' equivariante
     alla scala e resta ottimo; correzione del bloccante 1 della seconda G1, che invalidava l'ω = 0,0005 della bozza).
     9 serie da 1.500 giorni (1.000 di stima + 500 di valutazione), **h = 1 e h = 5**, **1.000 repliche**; disegno
     ridotto dichiarato: ristima ogni 20 giorni, 10.000 ripetizioni dello SPA. Criterio: il nodo (procedura grafica
     sulle 18 coppie con le soglie vere) rifiuta in **non piu' del 5%** delle repliche (il doppio della quota). Con
     1.000 repliche il controllo passa nel 54% dei casi se la dimensione vera e' il 5%, e distingue il 2,5% da circa il
     6,5% (con quella dimensione passa nel 2,8% dei casi; calcolo del gatekeeper, terza G1).
   - **HMM**: processo GJR (ω = 0,02, α = 0,03, γ = 0,10, β = 0,90), riscalato come sopra, per il quale il GJR e' il
     previsore esatto; le quattro varianti dell'HMM contro il GJR. Disegno ridotto dichiarato: **200 repliche, 3 serie,
     h = 1, 3 partenze, ristima ogni 60 giorni**. Criterio: il nodo, con la procedura grafica sulle 3 coppie del disegno
     ridotto alla quota del nodo, rifiuta in non piu' del 2,5% delle repliche (il doppio di 1,25%). E' un controllo
     **diverso** da quello vero, non piu' severo: mantiene l'errore del nodo all'1,25%, ma prova la dimensione per
     coppia a 1,25%/3, non nella coda vera (1,25%/18 = 0,069%). Limite dichiarato: con 200 repliche distingue male una dimensione del 2,5% da una del 5%; serve
     a trovare guasti grossi (per esempio la studentizzazione su differenziali piccoli e correlati delle combinazioni).
   - **Premio**: dimensione del **test primario**. Bootstrap a blocchi della serie giornaliera del premio di sviluppo
     riportata a media zero, blocchi di **21** e di **63** giorni, 2.000 repliche ciascuno. Ogni serie ricampionata e'
     lunga quanto le origini del premio nell'holdout (giorni di borsa XNYS dal 2024-11-11 al 2026-10-09) e si mette su
     quelle date del calendario, **senza i loro valori**; le origini mensili sono gli ultimi giorni di borsa del mese di
     quel calendario (circa 23), e si applica la t a una coda.
     Criterio: rifiuto in non piu' del 2,5% delle repliche, con entrambi i blocchi (il premio ha una coda sinistra
     lunga: con 23 osservazioni la t puo' rifiutare troppo nella direzione della conferma).
3. **Corsa di sviluppo**: perdite di tutte le serie, solo descrittive. **Dopo averla vista non si cambia nulla** di
   §2-§6: una modifica e' una variante post-esito (P1-P3), esplorativa.
4. **MDE per coppia** (G6): MDE = `mde(sd, n_eff, alpha=..., code=1)` con l'α della **prima soglia** della coppia
   (2,5%/18: fattore 3,83; 1,25%/18: fattore 4,04), sd = deviazione HAC del differenziale di QLIKE (migliore variante
   contro benchmark) dai dati di sviluppo, Newey-West con max(h − 1, 4) ritardi, n_eff = giorni di holdout. Premio:
   `mde(sd_mensile, n, alpha=0,0125, code=1, gl=n − 1)`, n = mesi di holdout.
5. **Controlli positivi simulati**. Rumore del bersaglio: σ = deviazione standard di log(v_t / (c_t·f_t^GJR)) nei dati di
   sviluppo, **per strumento** (limite alto del rumore della proxy, perche' contiene anche l'errore del modello: scelta
   prudente, che fa uscire piu' nodi). **Prima di far girare** questi controlli si scrive, per ogni nodo, il rapporto
   fra l'effetto del processo simulato (differenza di QLIKE attesa, parametri fissati qui) e l'MDE simulato: se
   l'effetto sta sotto l'MDE, il nodo esce **per la scelta dei parametri**, non per un guasto della pipeline, e lo si dice.
   - **GARCH**: processo GJR come sopra, stesso disegno del negativo, **200 repliche**. Si dichiara prima la differenza
     di QLIKE attesa con questi parametri, accanto all'MDE del passo 4.
   - **HMM**: processo a 2 regimi di varianza (0,5 e 2,0 %², probabilita' di restare 0,98 e 0,95), contro GJR; disegno
     ridotto: 50 repliche, 3 serie, 3 partenze, ristima ogni 60 giorni.
   - **Criterio** (bloccante 2 della seconda G1): la **frequenza media di rifiuto per coppia**, con le **soglie vere
     iniziali** (2,5%/18 e 1,25%/18) anche nel disegno ridotto, e' **almeno l'80%**. Accanto si riporta la frequenza a
     livello di nodo.
6. **Controllo positivo sui dati veri** (bloccante 3 della seconda G1). Variante iniettata
   f_t = (c_t · EWMA_t)^(1 − w) · v_bersaglio^w (conosce il bersaglio). **w si tara sui 500 giorni di sviluppo che
   precedono gli ultimi 500**, perche' il guadagno di QLIKE sia pari all'MDE del passo 4, e **si prova sugli ultimi 500**
   (dati diversi dalla taratura). La variante entra nello SPA **insieme** alle tre varianti vere (diluizione realistica),
   contro EWMA, h = 1, ma il criterio guarda **lei sola** (bloccante 1 della terza G1: uno SPA puo' rifiutare per merito
   delle varianti vere): lo **StepM** alla soglia vera della coppia (2,5%/18) deve **identificare la variante iniettata**.
   **RUSSELL e' escluso** (bloccante 2 della terza G1: ha circa 570 giorni di sviluppo con previsioni, non 1.000).
   Criterio: la variante iniettata e' identificata su **almeno 5 strumenti su 8** (con potenza vera dell'80% per
   strumento succede con probabilita' 0,94, con il 50% con probabilita' 0,36, **se gli strumenti fossero
   indipendenti**: quattro indici USA e il DAX sono correlati, quindi il conteggio e' piu' disperso e il criterio
   distingue meno di quanto dicono questi numeri). StepM con **100.000 ripetizioni**, seme 20261117. Stesso schema per
   l'HMM: variante iniettata sul GJR, nello SPA con le quattro varianti, StepM a 1,25%/18, almeno 5 su 8. Nei controlli
   simulati (§7.2, §7.5) lo SPA usa 10.000 ripetizioni: alla soglia di 0,139% il quantile e' stimato da circa 14
   valori, quindi la decisione della singola replica e' rumorosa; la frequenza su 200-1.000 repliche lo media, ed e'
   un limite dichiarato.
7. **Conseguenze, scritte ora** (riserva 5 della seconda G1):

   | Controllo che fallisce | Cosa succede |
   |---|---|
   | invarianza (1) o un negativo (2, GARCH o HMM) | la pipeline ha un guasto: si cerca e si corregge (correzione gratuita, C5) e si rifanno i passi 1-2, ogni iterazione in un'aggiunta datata; un cambio di disegno che non e' un guasto (blocco, ripetizioni) va nelle deviazioni del §10, anche se gratuito; la corsa di sviluppo non parte prima |
   | dimensione del premio (2) | il nodo del premio **esce prima dell'apertura** |
   | positivo simulato (5) o sui dati veri (6) | il nodo **esce prima dell'apertura** (Matteo, 13/11) |

   **Un nodo uscito tiene la sua quota, riservata** (Matteo, 13/11, conforme a H4: "con l'errore rimasto"): non va agli
   altri nodi. All'apertura la procedura grafica gira solo sui nodi rimasti, con le loro quote iniziali e il riciclo
   fra loro (S2: il riciclo e' dopo un rifiuto, non dopo un'uscita). Il nodo uscito si puo' testare dopo, una volta
   sola, su **dati forward successivi all'apertura**, con la sua quota iniziale (2,5% o 1,25%), in un'aggiunta datata
   scritta prima di raccogliere quei dati e dopo aver corretto la causa dell'uscita, che fissa **prima** la lunghezza
   della finestra forward, l'MDE e i controlli (senza lunghezza fissata il test si fermerebbe quando conviene); l'errore della famiglia resta al
   5%. Un ridisegno dopo il passo 3 conta trial (C1) ed e' post-esito. Se esce ogni nodo, l'holdout resta sigillato.
8. Revisione G1 del gatekeeper sulle aggiunte, poi **apertura unica** dell'holdout (H4) per i nodi rimasti.

## 8. Rifiniture previste per i round 2-3 (P4) e quota d'errore

Tutto l'errore di famiglia (5%) e' assegnato al round 1. Le rifiniture qui sotto sono quindi **esplorative**, salvo una
pre-registrazione nuova su **dati forward** successivi all'apertura con una quota fissata allora (P3, per esempio
α·6/(π²k²) alla k-esima). Quella quota puo' venire **solo** dalla quota riservata di un nodo uscito (§7.7) e non
ancora spesa: cosi' l'errore della famiglia resta al 5%. Andare oltre il 5% richiede una decisione di Matteo in
`DECISIONS.md`. Le rifiniture: (a) distribuzione t di Student (nodo GARCH); (b) finestra di 1.500 giorni (GARCH e HMM);
(c) GARCH a regimi di Markov (Ardia et al. 2018), nel **nodo HMM**, se esiste un'implementazione Python verificata.
Mai sull'holdout. Qualunque altra modifica e' post-esito ed esplorativa (P1).

## 9. Revisione G1

**Prima passata (13/11): BLOCCA**, 6 bloccanti e 7 riserve (DECISIONS 2026-11-13). Come sono stati trattati:

| Rilievo | Correzione |
|---|---|
| B1 scala, giorni esclusi, unita' | §3: apertura e chiusura dal calendario, somme esatte, regola delle origini escluse, unita' in %², riscalamento con c solo passato fissato ora |
| B2 look-ahead nel codice | §4 (solo filtrati, `last_obs`) e §7.1 test d'invarianza bloccante |
| B3 MDE e ripetizioni | §6 (100.000 ripetizioni, (b+1)/(B+1), regola sulla soglia dentro l'intervallo), §7.6 (MDE per coppia a una coda); `verifiche.py` accetta `code=1` (commit `761481f`) |
| B4 controlli | §7.2-7.3: soglia dell'80%, ω > 0, 1.000 repliche nel negativo, disegni ridotti dichiarati, controllo di dimensione del premio; test primario del premio mensile non sovrapposto |
| B5 HMM e S4 | §5: combinazioni fisse 0,5·GJR + 0,5·HMM (Matteo), 127 serie |
| B6 congelamento e storia | commit `889204f`, `b026899`, `db354ec`, `a62f622` sul branch `strumenti/volatilita`; guardie §7.0; versioni §2; controllo positivo sui dati veri §7.5 |
| R1 regimi dell'holdout | §4, dalla cronologia pubblica |
| R2 M5 per oro ed euro | §2, scelta motivata; stagionalita' oraria non applicabile |
| R3 qualita' di XAU, XAG, WTI | §2: numeri dal 2015 e `checklist_dati` prima della corsa |
| R4 livello delle affermazioni | §6: grafo su 37 ipotesi elementari (Matteo: per strumento) |
| R5 riferimenti | §5: non varianti, non consegnabili da questo holdout |
| R6 quota per i round 2-3 | §8: esplorativi salvo pre-registrazione forward con quota nuova; MS-GARCH nel nodo HMM |
| R7 decisioni del 13/11 e contaminazione | voce DECISIONS 2026-11-13; §4 contaminazione |

**Seconda passata (13/11): BLOCCA**, 5 bloccanti e 8 riserve, quasi tutti nei controlli della pipeline. Come sono stati
trattati:

| Rilievo | Correzione |
|---|---|
| B1 negativo IGARCH con ω > 0 non nullo | §7.2: ω = 0 e riscalamento costante della serie |
| B2 soglia dell'80% sul nodo | §7.5: frequenza media di rifiuto per coppia con le soglie vere |
| B3 controllo sui dati veri superabile per costruzione | §7.6: taratura su 500 giorni diversi, variante dentro lo SPA, forma esatta, dopo l'MDE |
| B4 controlli mancanti | §7.2: negativo dell'HMM ripristinato, dimensione del test mensile del premio (blocchi 21 e 63); §7.7 conseguenze |
| B5 riciclo diverso da S2 | §6: quota del nodo esaurito ai **nodi** in parti uguali; primitiva `procedura_grafica_nodi` testata |
| R1 c_t su previsioni gia' sulla scala di v | §3: c_t solo per i modelli sui rendimenti; invarianza sulla previsione finale (§7.1) |
| R2 scala del premio | §3: c dell'SPX500 con la direzione dell'effetto; premio con la somma dei r² come descrittivo |
| R3 specifiche delle simulazioni | §7.2 e §7.5: rumore a media 1, σ, bersaglio, varianza iniziale, c_t nella pipeline |
| R4 h = 5 nei controlli | §7.2: negativo del GARCH a h = 1 e h = 5 |
| R5 nodo uscito | §7.7 |
| R6 dati fuori da git | §7.0: sha256 dei file registrato e verificato |
| R7 numeri di XAU, XAG, WTI | README dei dati, dall'11/11 |
| R8 selezione delle origini | §3: abs(r) dei giorni esclusi contro la mediana |
| Debito: procedura grafica, p-value dello SPA, MDE con t | `motore/core/verifiche.py`: `procedura_grafica_nodi`, `pvalue_spa`, `gl` in `mde` (con test) |

**Terza passata (13/11): BLOCCA**, 3 bloccanti e 5 riserve (procedura grafica giudicata valida). Come sono stati
trattati:

| Rilievo | Correzione |
|---|---|
| B1 lo SPA del controllo sui dati veri puo' rifiutare per le varianti vere | §7.6: criterio sulla variante iniettata identificata dallo StepM alla soglia vera |
| B2 RUSSELL senza i 1.000 giorni | §7.6: RUSSELL escluso, almeno 5 su 8 (0,94 / 0,36) |
| B3 quota del nodo uscito contro H4 | §7.7: quota **riservata** per un test forward (Matteo, 13/11; DECISIONS 2026-11-13) |
| R1 intervallo del p-value a ogni passo, nodi vuoti | §6: 4 semi sommati, `intervalli` nella primitiva (commit `bcc7b4b`, test) |
| R2 frase sul controllo negativo | §7.2 corretta (54% di passaggio al 5%, distingue 2,5% da 6,5%) |
| R3 σ e rapporto effetto/MDE | §7.5: σ per strumento, rapporto scritto prima di far girare i controlli |
| R4 soglie del negativo dell'HMM, serie del premio | §7.2: procedura grafica sulle 3 coppie (piu' severa); serie lunghe quanto l'holdout sul suo calendario, senza valori |
| R5 iterazioni dei controlli | §7.7: aggiunte datate; cambi di disegno nelle deviazioni |

**Quarta passata (13/11): BLOCCA**, 1 bloccante e 5 riserve; "riparato questo, non trovo altri bloccanti" (gatekeeper).

| Rilievo | Correzione |
|---|---|
| B1 lo SPA di `arch` 8.0.0 non studentizza | §6: `spa_studentizzato` e `stepm_studentizzato` (commit `7170515`, verificato sul sorgente e con un caso di prova) |
| R1 5 su 8 assume indipendenza | §7.6: dichiarato accanto ai numeri |
| R2 ripetizioni dello StepM | §7.6: 100.000 e seme 20261117 sui dati veri; limite dichiarato nei controlli simulati |
| R3 errore oltre il 5% nei round 2-3 | §8: quota solo dalla riserva di un nodo uscito, oltre il 5% decide Matteo |
| R4 test forward del nodo uscito | §7.7: lunghezza, MDE e controlli fissati prima |
| R5 "piu' severo" | §7.2: "un controllo diverso", con la ragione |

**Quinta passata (13/11): PASSA CON RISERVE**, 0 bloccanti, 1 riserva di forma (l'etichetta dello StepM: e' la versione
a passi dello SPA di Hsu, Hsu e Kuan 2010), corretta in `verifiche.py` e nel §6. Primitiva verificata dal gatekeeper:
stesso nucleo di arch (scarto 0,0), ricentratura `consistent` valida sull'ingresso riscalato, statistica di Hansen 2005.
**Il testo attende l'approvazione di Matteo.**

## 10. Deviazioni (P5)

| Data | Cosa cambia | Perche' | Esplorativo? |
|---|---|---|---|
| 2026-11-13 | §3, strumenti a 24 ore: il blocco che apre la domenica sera e' il giorno del **lunedi'** (la parentesi "il giorno del venerdi' comincia la domenica" era scritta male) | chiarimento del testo, prima di ogni corsa sui dati veri: con l'altra lettura il blocco del 10/11/2024 sera, che e' gia' il lunedi' dell'holdout, cadrebbe nello sviluppo | no |
| 2026-11-19 | §6, QLIKE: una previsione 0 <= f < 1e-100 vale 1e-100 e si conta per modello, strumento e orizzonte (`pipeline.sotto_soglia`); una previsione negativa o non finita e' un errore (GUASTO). Il filtro delle origini con previsione <= 0 o non finita di `riassumi.py` si toglie (sullo sviluppo ha scartato 0 origini) | le previsioni EGARCH dei blocchi di ripiego S5 arrivano a 1,1e-46 (XAUUSD, XAGUSD, EURUSD; §11 del 19/11): con f = 0 la perdita e' infinita e lo SPA si ferma, come il 14/11; con 1e-100 e v dell'ordine di 1e4 il quadrato della perdita resta sotto ~1e208. **Contrasta con la lettera del §7.3** (modifica del §6 dopo la corsa di sviluppo): Matteo la accetta come deviazione non esplorativa (DECISIONS 2026-11-19 (2)) perche' (i) l'avrebbe fatta con qualunque esito, il motivo e' il campo numerico e non quale modello vince; (ii) e' l'identita' su ogni numero gia' calcolato (sviluppo: minimo 1,1e-46, 216 medie identiche; negativi: argomento sui diari nel §11; l'invarianza non usa la QLIKE); (iii) non puo' favorire un rifiuto: i benchmark non si avvicinano alla soglia e una variante portata alla soglia perde di ~1e97 o piu' al giorno | no |

## 11. Aggiunte datate (passi del §7)

Ogni passo del §7 aggiunge qui una voce, nello stesso commit del codice che lo esegue. Le aggiunte non cambiano §1-§6:
se un passo richiede di cambiarli, la modifica va nel §10.

### 2026-11-13 — Approvazione e passo 0 (guardie)

- **Approvata** da Matteo in sessione, sul testo del commit `7dea1e3` (DECISIONS 2026-11-13 (2)).
- Guardie in [`codice/volatilita/guardie.py`](../codice/volatilita/guardie.py): percorsi protetti esistenti
  (pre-registrazione, contatore, `codice/volatilita/`, `motore/core/`, `motore/tests/`), nessuna modifica non
  committata, hash del commit registrato, versioni del §2 (e Python 3.12), sha256 dei dati.
- sha256 dei nove file M5 e del VIX registrati in [`hash_dati.json`](../codice/volatilita/hash_dati.json), con la
  dimensione in byte; il file non si riscrive (`--registra` si rifiuta se esiste). Calcolati sui byte, holdout
  compreso: nessuna statistica sui prezzi.

### 2026-11-13 — Scelte d'implementazione, dichiarate prima della corsa di sviluppo

Dettagli che §3-§5 non fissavano. Nessuna perdita e nessuna previsione sui dati veri e' stata guardata quando sono
stati scritti (i soli numeri visti sono conteggi di barre e di giorni).

1. **Caricatore** ([`giorni.py`](../codice/volatilita/giorni.py)): legge le righe in ordine e si ferma alla prima con
   ora >= domenica 2024-11-10 00:00 UTC; leggere oltre richiede `HOLDOUT_APERTO = True`, che cambia solo nel commit
   del passo 8. Ultimo giorno di sviluppo: venerdi' 2024-11-08 per tutti.
2. **Indici, barra d'apertura mancante**: P_ap e' l'open della prima barra della seduta. r_t resta esatto (la somma
   telescopica non dipende da P_ap); cambia solo la divisione di v_t fra notte e seduta. Si conta (`apertura_mancante`).
3. **Strumenti a 24 ore**: il giorno D va dalle 17:00 New York di D−1 alle 17:00 di D, e il blocco che apre la
   domenica sera e' il **lunedi'**. La parentesi del §3 ("il giorno del venerdi' comincia la domenica") e' scritta
   male: il chiarimento e' nel §10. Le barre fuori dalla settimana (fra venerdi' e domenica alle 17:00) si scartano:
   dal 2015 sono 3 per XAUUSD, 2 per XAGUSD, 0 per WTI, 27 per EURUSD.
4. **RUSSELL**: il primo giorno con dati (2018-08-08) non ha la chiusura precedente; la serie parte il 2018-08-09.
5. **Struttura dei giorni di sviluppo** (§3, riserva 3 della G1; solo conteggi):

   | Strumento | Giorni | Dal | Esclusi (< 90% delle barre) | Apertura mancante |
   |---|---|---|---|---|
   | SPX500, NAS100, DOW | 2.481 | 2015-01-02 | 8 | 6 |
   | RUSSELL | 1.574 | 2018-08-09 | 8 | 6 |
   | DAX | 2.504 | 2015-01-02 | 3 | 2 |
   | XAUUSD | 2.545 | 2015-01-02 | 77 | — |
   | XAGUSD | 2.544 | 2015-01-02 | 80 | — |
   | WTI | 2.547 | 2015-01-02 | 173 | — |
   | EURUSD | 2.566 | 2015-01-02 | 7 | — |

   Negli strumenti a 24 ore gli esclusi cadono soprattutto di lunedi' (festivi USA con chiusura anticipata del CME); nel
   WTI sono di piu' nel 2015-2019 (19-38 l'anno, poi 6-10). La giornata tipica ha 276 barre su 288 (pausa di un'ora).
6. **Modelli** ([`modelli.py`](../codice/volatilita/modelli.py)): `arch` stima sulla sola finestra di 1.000 giorni
   (equivale a `last_obs`) e prevede con i parametri fissati sul blocco esteso fino all'ultima origine; EWMA con
   `EWMAVariance(0,94)` di `arch` (stessa inizializzazione dei GARCH). **EGARCH a 5 passi**: `arch` 8.0.0 non ha la
   previsione analitica oltre il primo passo; si usa l'attesa esatta sotto la normale (`egarch_multi`, entro l'1% da
   100.000 simulazioni di `arch` nel test). **Non convergenza**: il blocco usa i parametri del precedente, e si conta
   (la regola S5 dell'HMM estesa ai GARCH). **HMM**: 20 stime complete da punti casuali attorno al punto di partenza
   di `statsmodels` (spazio non vincolato, N(0, 1)), seme dipendente solo da (20261113, k, t0); si tiene la
   verosimiglianza migliore fra le stime che convergono. **HAR**: h = 5 diretto (bersaglio la somma dei 5 giorni), una
   previsione <= 0 diventa la media della finestra, e si conta.
7. **Origini**: le stesse per h = 1 e h = 5 (t + 5 entro l'ultimo giorno disponibile), come chiede il §4.
8. **Semi**: invarianza 20261118; negativo GARCH 20261119; negativo HMM 20261120; dimensione del premio 20261121; i
   semi dello SPA di ogni replica derivano da `SeedSequence([seme del controllo, replica, serie, h])`.
9. **Dimensione del premio**: bootstrap circolare a blocchi di lunghezza fissa (Politis e Romano 1992); 479 giorni di
   borsa XNYS dal 2024-11-11 al 2026-10-09, 23 origini di fine mese (dal 2024-11-29 al 2026-09-30); 2.358 osservazioni
   giornaliere del premio di sviluppo (origini con la finestra di 30 giorni prima del 2024-11-11 e senza giorni esclusi).
10. **Controlli positivi simulati (§7.5), serie**: nel GARCH le 9 serie usano ciascuna il σ di uno strumento (tutti e
    nove); nell'HMM, che ha 3 serie, si usano i σ dei **3 strumenti col σ piu' alto** (la scelta prudente del §7.5).
    Fissato ora, prima che la corsa di sviluppo dia i σ.

Codice: commit `5fad489` (caricatore, modelli, pipeline, invarianza, test veloci: 9 test verdi su dati sintetici) e
`c82683d` (controlli simulati).

### 2026-11-13 — Passo 2, dimensione del premio: FALLISCE, il nodo del premio esce

Corsa del commit `c82683d` ([`esiti/dim_premio.json`](../codice/volatilita/esiti/dim_premio.json)): la t a una coda
all'1,25% sulle 23 origini mensili rifiuta nel **14,55%** delle repliche con blocchi di 21 giorni e nel **15,95%** con
blocchi di 63 (criterio: <= 2,5% con entrambi). Il codice e' stato provato sostituendo il premio con rumore gaussiano:
rifiuta nell'1,45% e nell'1,2% dei casi, cioe' l'1,25% atteso. La causa e' la forma della serie, non il codice: il
premio giornaliero di sviluppo ha asimmetria −8,7 e curtosi in eccesso 92 (descrittivi di forma, non della media), e con
23 osservazioni la t rifiuta troppo nella direzione della conferma, il rischio gia' scritto nel §7.2.

**Conseguenza scritta prima** (§7.7): il nodo del premio **esce prima dell'apertura**; la sua quota (1,25%) resta
**riservata** a un test su dati forward, con lunghezza, MDE, test e controllo di dimensione fissati prima di
raccogliere i dati. Non e' un verdetto sul premio: dice solo che questo test, con questa coda, non controlla l'errore.
All'apertura la procedura grafica gira sui nodi GARCH e HMM, con le quote 2,5% e 1,25%.

### 2026-11-13 — Passo 1, invarianza al futuro: PASSA

Corsa del commit `5fad489` ([`esiti/invarianza.json`](../codice/volatilita/esiti/invarianza.json), seme 20261118):
9 strumenti × 12 serie (9 modelli e 3 riferimenti), 26-29 origini per coppia (23 di sviluppo e fino a 6 posizioni
dell'holdout sulla serie sintetica), 2.976 confronti. **Differenza massima 0,0** contro la tolleranza di 1e-10: le
previsioni con r e v dopo t sostituiti da rumore sono identiche bit per bit.

**Controllo positivo del test** (aggiunto dopo l'esito, perche' uno zero esatto e' credibile solo se il test sa
fallire; 0 trial, non cambia nulla di §2-§6): quattro fughe di un giorno iniettate in copie delle funzioni, sulla serie
sintetica, devono superare la tolleranza. Stima GARCH su una finestra spostata in avanti di un giorno: differenza fino a
1,6. Regressione HAR che include il bersaglio di t0 (cioe' v di t0 + 1): fino a 0,11. c_t con la finestra che finisce
in t + 1: 0,36-0,46 a ogni origine. HMM con le probabilita' smussate al posto delle filtrate: 2,9e-10 su una serie GJR,
dove i due regimi stimati quasi non si distinguono, e 0,045-4,6 su un processo a regimi veri (3 semi); senza fuga
0,0. Tutte rilevate; le origini a meta' blocco non le vedono, com'e' giusto, perche' li' la finestra spostata arriva
al piu' a t. Il controllo e' ora il test `test_invarianza_rileva_le_fughe` (10 test verdi).

### 2026-11-14 — Passo 2, negativo GARCH: guasto della pipeline (falsa convergenza dell'EGARCH), corretto; si rifanno i passi 1-2

- **Prima corsa** (commit `a14d10c`): ferma all'avvio, i processi figli non trovavano `motore` (lanciando lo script sul
  percorso c'e' solo la sua cartella; i test passavano perche' pytest aggiunge la radice). Corretto nel commit
  `3bb26de`; nessuna replica calcolata.
- **Seconda corsa** (commit `3bb26de`): ferma dopo 16 repliche su 1.000 (0 rifiuti del nodo), perche' lo SPA
  studentizzato ha rifiutato un differenziale con varianza di lungo periodo non finita. Causa: replica 17, serie 7,
  blocco 1279: `arch` dichiara convergente la stima EGARCH (flag 0, parametri finiti) con α = −15,05 e γ = −65,25 e
  log-verosimiglianza −8.327, **6.390 sotto il punto da cui parte l'ottimizzatore** (coi parametri del blocco precedente
  −3.052; ripartendo da quelli, −1.918,6). Previsione a un passo 1,3·10⁶; a 5 passi `egarch_multi` calcolava
  inf·0 = NaN. La regola di non convergenza (scelta 6) leggeva solo il flag, e i due blocchi successivi, non
  convergenti, ereditavano quei parametri.
- **Correzioni** (guasto, C5, 0 trial; non cambiano §1-§6): (a) una stima con verosimiglianza **minore di quella del
  suo punto di partenza** (`volatility.starting_values`, da cui parte `arch` con media zero e errori normali) conta come
  non convergenza: parametri del blocco precedente, e si conta, come nella scelta 6; (b) `egarch_multi` in logaritmi
  (`norm.logcdf`, `logaddexp`): stesso valore dove prima era finito (scarto relativo < 1e-12 nel test), mai NaN (con
  a + b molto negativo il valore vero e' finito e prima veniva NaN). Sulla serie della replica 17 il criterio scatta
  solo al blocco 1279: tutte le altre stime GARCH, GJR ed EGARCH migliorano la partenza di almeno 4,9.
- **Osservazione** (non e' un guasto e non si cambia): coi parametri di ripiego (β = 0,9998, α < 0) il filtro EGARCH
  dipende molto dall'inizio della finestra: in 1279 prevede 0,80 partendo dal giorno 260 e circa 1.300 partendo dal
  280, perche' con varianza alta |z| e' piccolo e −α·c la spinge ancora in alto. E' il modello sotto la regola S5; in un
  controllo negativo puo' solo far perdere l'EGARCH.
- Test: 12 verdi (nuovi `test_egarch_multi_finito_con_parametri_estremi` e
  `test_falsa_convergenza_conta_come_non_convergenza`; il controllo delle fughe punta alla nuova riga di `prevedi_arch`).
- Per il §7.7 si rifanno i passi 1 e 2 (negativi GARCH e HMM) sul commit di questa voce; le 16 repliche gia' fatte si
  scartano. La dimensione del premio non usa i modelli e non si rifa'.

### 2026-11-14 — Passo 1 rifatto dopo la correzione: PASSA

Corsa del commit `c8a31b0` ([`esiti/invarianza.json`](../codice/volatilita/esiti/invarianza.json), seme 20261118, stesse
origini del 13/11): 108 coppie strumento × modello, 2.976 confronti, **differenza massima 0,0** contro la tolleranza di
1e-10, nessuna origine fallita.

### 2026-11-14 — Passo 2, negativo GARCH: seconda fermata (primo blocco senza precedente), corretto; si rifanno i passi 1-2

- **Terza corsa** (commit `305eed7`): ferma dopo 64 repliche su 1.000 (0 rifiuti del nodo) con `prima stima non
  convergente in t0=999`. Due casi: replica 76, serie 5, GARCH (flag 4 di SLSQP, "Inequality constraints
  incompatible", verosimiglianza +11,9 sulla partenza) e replica 66, serie 7, EGARCH (flag 4, −1,07·10⁸). La regola S5
  estesa ai GARCH (scelta 6) usa i parametri del blocco precedente, che il **primo blocco** non ha: un caso senza
  regola, che fermava la corsa.
- **Regola** (Matteo, 14/11: si corregge il caso osservato e nient'altro; guasto, C5, 0 trial; non cambia §1-§6): solo
  quando fallisce la **prima** stima di una serie, 20 ripartenze di riserva attorno alla partenza di `arch`
  (sv·exp(0,2·N(0,1)), seme fisso legato solo a t0; GARCH e GJR positivi e con persistenza < 0,999, EGARCH con
  β <= 0,995); si tiene la stima con verosimiglianza piu' alta fra quelle che convergono e battono la partenza di
  `arch`; se nessuna, la corsa si ferma con un errore visibile. Gli altri blocchi restano col ripiego sul precedente.
  Le ripartenze si contano (`ripartenze_primo_blocco`, anche nella corsa di sviluppo). Sui due casi: GARCH 20 buone su
  20, la migliore +27,8 sulla partenza (0,0015; 0,039; 0,961); EGARCH 10 su 20, 4 falsi successi scartati dal
  criterio della voce precedente, la migliore +25,7.
- **Processo** (Matteo, 14/11: il ciclo d'errore si accorcia, non si anticipano gli scenari): (a) una replica che va
  in errore non ferma piu' la corsa, diventa una riga con l'errore, e alla fine il controllo e' **GUASTO** (mai letto
  come "non rifiuta", uscita 1); (b) ogni riga del diario porta il commit e la ripresa usa solo le righe dello stesso
  commit (un diario di un altro commit si sposta da parte). Per (b) le 64 repliche del `305eed7` si rifanno.
- Test: 16 verdi (nuovi: ripartenze al primo blocco sui due casi, replica in errore → GUASTO, diario di un altro
  commit non riusato).
- Per il §7.7 si rifanno i passi 1 e 2 (negativi GARCH e HMM) sul commit di questa voce.

### 2026-11-15 — Passo 1 rifatto sul commit della voce precedente: PASSA

Corsa del commit `2fea870` ([`esiti/invarianza.json`](../codice/volatilita/esiti/invarianza.json), seme 20261118, stesse
origini): 108 coppie strumento × modello, 2.976 confronti, **differenza massima 0,0** contro la tolleranza di 1e-10,
nessuna origine fallita. Le ripartenze al primo blocco non cambiano l'invarianza al futuro. Segue il passo 2 da zero
(il diario del `305eed7` si sposta da parte, regola (b) della voce precedente).

### 2026-11-15 — Passo 2, negativo GARCH: GUASTO (2 repliche su 1.000, EGARCH a varianza enorme), corretto; si rifanno i passi 1-2

- **Quarta corsa** (commit `c351ba8`, prima col processo nuovo): arrivata in fondo, esito **GUASTO**. 998 repliche
  calcolate, 7 rifiuti del nodo (0,7%, soglia 5%), che non si leggono come esito: 2 repliche in errore, la 281 (serie 7)
  e la 838 (serie 2), entrambe `prima stima non convergente in t0=999` sull'EGARCH, ripartenze di riserva comprese.
- **Causa**: `arch` 8.0.0 limita omega dell'EGARCH a ln(media y²) ± ln(10.000). Nelle due finestre la media di y² e'
  oltre 10.000 (deviazione standard 249 e 168 al giorno, una serie IGARCH con omega = 0 che deriva), il limite
  inferiore diventa positivo (1,83 e 1,04) ed esclude la stima, che ha omega ~ 0 e beta ~ 1 (Nelder-Mead senza limiti:
  +291,5 e +300,2 di verosimiglianza sulla partenza di `arch`). Fuori dal limite e' anche la partenza di `arch`
  ((1 − beta)·ln v): tutte le stime finivano sul bordo, 131,9 e 7,2 sotto la partenza, e il criterio di falsa
  convergenza del 14/11 le scartava giustamente. Sui dati reali (rendimenti in %) servirebbe una deviazione standard
  giornaliera sopra il 100%.
- **Regola** (caso osservato, guasto, C5, 0 trial; non cambia §1-§6): se la media di y² della finestra supera 10.000,
  l'EGARCH si stima su y/s con s = √(media y²) della stessa finestra e omega si riporta sulla scala di y
  (omega_y = omega_x + 2(1 − beta)·ln s, esatta: la verosimiglianza differisce di n·ln s). Le due repliche rifatte col
  codice nuovo arrivano in fondo, nessun rifiuto del nodo.
- Test: 18 verdi (nuovo: le due finestre si stimano in scala, la stima batte la partenza di oltre 100 con beta > 0,95,
  conversione esatta entro 1e-6).
- Per il §7.7 si rifanno i passi 1 e 2 sul commit di questa voce; il diario del `c351ba8` si sposta da parte.

### 2026-11-15 — Passo 1 rifatto sul commit della voce precedente: PASSA

Corsa del commit `242e1a6` ([`esiti/invarianza.json`](../codice/volatilita/esiti/invarianza.json), seme 20261118, stesse
origini): 108 coppie strumento × modello, 2.976 confronti, **differenza massima 0,0** contro la tolleranza di 1e-10,
nessuna origine fallita. La stima in scala dell'EGARCH non cambia l'invarianza al futuro. Il passo 2 (`neg_garch` da
zero, poi `neg_hmm`) parte nella sessione successiva, sul commit di questa voce.

### 2026-11-16 — Passo 2, negativo GARCH: PASSA

Corsa del commit `ad2e529` ([`esiti/neg_garch.json`](../codice/volatilita/esiti/neg_garch.json); processo IGARCH con
omega = 0, 9 serie × 1.500 giorni, h = 1 e 5, 1.000 repliche, ristima ogni 20 giorni, SPA studentizzato a 10.000
ripetizioni, quota del nodo 2,5%): **il nodo rifiuta in 8 repliche su 1.000 (0,8%)**, contro la soglia del 5%;
frequenza media di rifiuto di una coppia alla soglia vera 0,07%; **nessuna replica in errore**. Il controllo e' molto
conservativo, come atteso sotto un nullo in cui il benchmark e' il modello vero. Segue il negativo HMM sullo stesso commit.

### 2026-11-16 — Passo 2, negativo HMM: GUASTO (12 repliche su 200, HMM a 3 regimi al primo blocco), corretto; si rifanno i passi 1-2

- **Corsa** (commit `ded188e`; processo GJR, 3 serie, h = 1, 200 repliche, 3 partenze, ristima ogni 60 giorni, quota del
  nodo 1,25%): arrivata in fondo, esito **GUASTO**. 188 repliche calcolate, 0 rifiuti del nodo (che non si leggono come
  esito); 12 repliche in errore (5, 15, 50, 66, 68, 99, 173, 176, 179, 181, 185, 186), tutte `prima stima non
  convergente in t0=999`.
- **Causa** (diagnosi sulle repliche 5, 15, 50): l'HMM a 3 regimi al primo blocco; con le 3 partenze del disegno del
  negativo (lo sviluppo ne usa 20) tutte finiscono al limite di iterazioni di statsmodels senza convergere, e il primo
  blocco non ha un precedente su cui ripiegare (lo stesso buco di regola dei GARCH del 14/11). Con 20 partenze le tre
  convergono.
- **Regola** (caso osservato, guasto, C5, 0 trial; non cambia §1-§6): come per i GARCH, solo quando nessuna partenza
  converge alla **prima** stima di una serie, 20 partenze di riserva con un seme a parte ([seme, k, t0, 1]); se nessuna
  converge la corsa registra l'errore. Le ripartenze si contano (`ripartenze_primo_blocco`, ora anche per l'HMM nella
  corsa di sviluppo).
- Le 12 repliche rifatte col codice nuovo arrivano tutte in fondo, nessun rifiuto del nodo. Test: 19 verdi (nuovo:
  replica 5, serie 2, hmm3 riparte al primo blocco).
- Per il §7.7 si rifanno i passi 1 e 2 (negativi GARCH e HMM) sul commit di questa voce; i diari del `ded188e` si
  spostano da parte da soli.

### 2026-11-17 — Passo 1 rifatto sul commit della voce precedente: PASSA

Corsa del commit `04212d2` ([`esiti/invarianza.json`](../codice/volatilita/esiti/invarianza.json), seme 20261118, stesse
origini): 108 coppie strumento × modello, 2.976 confronti, **differenza massima 0,0** contro la tolleranza di 1e-10,
nessuna origine fallita. Le partenze di riserva dell'HMM al primo blocco non cambiano l'invarianza al futuro. Segue il
passo 2 da zero (negativo GARCH, poi HMM) sul commit di questa voce.

### 2026-11-17 — Passo 2, negativo GARCH rifatto: PASSA

Corsa del commit `864f4a8` ([`esiti/neg_garch.json`](../codice/volatilita/esiti/neg_garch.json), stesso disegno della
voce del 16/11): **il nodo rifiuta in 8 repliche su 1.000 (0,8%)** contro la soglia del 5%; frequenza media di rifiuto
di una coppia alla soglia vera 0,07%; **nessuna replica in errore**. Identico alla corsa del `ad2e529`, come atteso: la
correzione del 16/11 tocca solo l'HMM, che il nodo GARCH non usa. Segue il negativo HMM sullo stesso commit.

### 2026-11-17 — Passo 2, negativo HMM rifatto: PASSA

Corsa del commit `6d55776` ([`esiti/neg_hmm.json`](../codice/volatilita/esiti/neg_hmm.json), stesso disegno della voce
del 16/11: processo GJR, 3 serie, h = 1, 200 repliche, 3 partenze, ristima ogni 60 giorni, quota del nodo 1,25%): **il
nodo rifiuta in 0 repliche su 200 (0,0%)** contro la soglia del 2,5%; nessuna coppia rifiuta alla soglia vera;
**nessuna replica in errore** (le 12 del 16/11 comprese). Con il passo 1 (`864f4a8`) e il negativo GARCH (`6d55776`)
i passi 1-2 del §7 sono chiusi sul codice corrente: segue la corsa di sviluppo (passo 3).

### 2026-11-19 — Passi 3-4: corsa di sviluppo (0 errori) e MDE per coppia; 126 trial contati

- **Corsa di sviluppo** (passo 3, [`sviluppo.py`](../codice/volatilita/sviluppo.py), commit `86fcdae`, partita sui tre
  esiti PASSA del 17/11): 361 compiti (strumento × modello × gruppo di blocchi), **0 errori**. Interrotta il 18/11 a
  250 compiti salvati per la chiusura della sessione e ripresa il 19/11 **sullo stesso commit** (la ripresa salta i
  compiti gia' salvati; con un altro commit la cache andava rifatta). Riepilogo (passo 4,
  [`riassumi.py`](../codice/volatilita/riassumi.py), stesso commit) in
  [`esiti/sviluppo.json`](../codice/volatilita/esiti/sviluppo.json).
- **Contatore**: 126 trial (54 GARCH, 72 HMM), contati ora per scelta di Matteo (19/11, DECISIONS 2026-11-19); il
  premio, uscito il 13/11, non ha previsioni e non si conta.
- **Diagnostica.** Non convergenze (regola S5, parametri del blocco precedente): EGARCH 9 su XAUUSD, 20 su XAGUSD, 18 su
  EURUSD; GJR 2 su EURUSD; nessuna altrove, nessuna negli HMM. Ripartenze al primo blocco: 1 (EGARCH, XAGUSD). HAR
  corrette: 12 SPX500, 12 NAS100, 16 DOW, 1 DAX, 5 WTI. c_t medio fra 0,955 (NAS100) e 1,265 (WTI). Previsioni del test
  d'invarianza (blocchi ristretti) contro la corsa completa: differenza massima **0,0**.
- **Osservazione sull'EGARCH** (non e' un guasto e non si cambia, §7.3): su XAUUSD, XAGUSD ed EURUSD la QLIKE media
  dell'EGARCH esplode (h = 1: 5,8·10¹⁷, 6,0·10³², 2,9·10⁴¹; mediane 0,073, 0,071, 0,081). **Tutte** le origini con
  QLIKE > 100 (13, 11, 15) cadono in blocchi di ripiego, con parametri a α < 0 e β fra 0,989 e 0,9995: un rendimento
  grande abbassa la varianza e la previsione crolla (minimi 1,7·10⁻²¹, 9,3·10⁻³⁷, 1,1·10⁻⁴⁶). E' il meccanismo gia'
  visto il 14/11 nel negativo GARCH: il modello sotto la regola S5, che puo' solo far perdere l'EGARCH. Sporca anche
  la media delle tre varianti GARCH, che e' un riferimento descrittivo e non entra nel test. **Punto aperto per
  Matteo**, non una regola nuova (il caso osservato e' finito): se nell'holdout una previsione scendesse a 0 in
  virgola mobile, la QLIKE sarebbe infinita e lo SPA del nodo GARCH si fermerebbe come il 14/11.
- **Descrittivi** (QLIKE, dati di sviluppo; nessuna conseguenza sul disegno). Nodo GARCH: la variante migliore batte
  l'EWMA sugli indici (h = 1: 0,054-0,081 su SPX500, NAS100, DOW, DAX; 0,008 sul RUSSELL) e perde su XAUUSD, XAGUSD,
  EURUSD (0,025-0,053) e sul WTI a h = 5. Nodo HMM: la variante migliore (quasi sempre la combinazione con 3 regimi)
  non batte il GJR di piu' di 0,011 in nessuna coppia. L'HAR, riferimento, e' il migliore su XAUUSD e XAGUSD ai due orizzonti e su EURUSD a h = 1.
- **MDE per coppia** (passo 4, α della prima soglia, n_eff = giorni di holdout 496-517): GARCH fra 0,064 (RUSSELL) e
  0,168 (XAGUSD h = 5), HMM fra 0,027 (RUSSELL) e 0,139. Il guadagno di sviluppo della variante migliore sta sotto
  l'MDE in **tutte le 36 coppie**: rapporto massimo 0,64 nel GARCH (NAS100 h = 1), 0,10 nell'HMM. E' un descrittivo
  sullo sviluppo, non una previsione dell'holdout, ma dice che con questi MDE il test vede solo un vantaggio
  piu' grande di quello osservato finora. σ del rumore per i positivi simulati (§7.5): fra 0,54 (XAGUSD) e 0,77 (SPX500).
- Segue il **passo 5** (controlli positivi simulati), da fare con Matteo: prima delle corse si scrive, per nodo, il
  rapporto fra l'effetto del processo simulato e l'MDE.

### 2026-11-19 — Passo 5, prima delle corse: soglia della QLIKE, regola di rifiuto dei positivi, lettura scritta ora

Revisione del gatekeeper sul codice dei positivi e sulla soglia (19/11): **BLOCCA** con 4 bloccanti, tutti chiusi qui
(conteggio della soglia ed errore su previsioni negative; classificazione come deviazione; regola di rifiuto dei
positivi; h = 5 nel rapporto effetto/MDE del GARCH).

1. **Soglia della QLIKE**: deviazione del §10 (Matteo, 19/11), non una correzione di guasto, quindi i passi 1-2 **non
   si rifanno** (la regola del §7.7 vale per i guasti). Il riepilogo dello sviluppo si rifa' sul commit di questa voce e
   deve uscire identico salvo `commit` e il nuovo conteggio `sotto_soglia`. Negativi invariati per costruzione: nei
   diari validi il guadagno medio piu' negativo e' −5,3·10²⁴ (`neg_garch`, commit `864f4a8`) e −0,57 (`neg_hmm`,
   `6d55776`), mentre una previsione sotto 1e-100 (con bersagli simulati >= ~1e-3) darebbe una perdita > ~1e97 in un
   giorno e una media sotto ~−1e94; i due esiti restano legati a quei commit. Lo script dell'apertura riportera' le
   previsioni portate alla soglia.
2. **Regola di rifiuto per coppia nei positivi** (Matteo, 19/11): decide il **p puntuale** (b+1)/(B+1) <= soglia vera, a
   10.000 ripetizioni dello SPA. Rifiuta per b <= 12 (GARCH, soglia effettiva 13/10.001 = 0,130% contro 0,139%) e
   b <= 5 (HMM, 6/10.001 = 0,060% contro 0,069%): riproduce quasi la soglia effettiva del test vero a 400.000 ripetizioni
   con l'intervallo (~0,127% e ~0,061%, calcolo del gatekeeper). La regola precedente (tutto l'intervallo sotto la
   soglia) provava una soglia 2 volte piu' severa nel GARCH e 4-7 volte nell'HMM; la sua lettura si riporta accanto,
   senza decidere. I negativi passano con entrambe (col p puntuale 1,4% e 0%, ricalcolati dal gatekeeper dai diari).
3. **Rapporto effetto/MDE**: `potenza.py` (seme 20261124, serie lunga 400.000 giorni, n = 495 origini come nelle
   repliche, Newey-West max(h − 1, 4) ritardi, soglia effettiva del punto 2), per ogni coppia σ × h (GARCH h = 1 e 5,
   HMM h = 1): effetto, MDE simulato, rapporto e potenza attesa Φ(√n·e/sd − z_α), con la media. Il GARCH e' un limite
   superiore in media (oracolo contro un GJR stimato); l'HMM un'approssimazione di segno indeterminato. I numeri vanno
   nella voce successiva, prima delle corse.
4. **Lettura, scritta ora**: i positivi girano qualunque sia il rapporto. Se un positivo fallisce con potenza attesa
   media sotto l'80%, il nodo esce **per la scelta dei parametri**; se fallisce con potenza attesa >= 80% esce lo stesso
   (§7.7) e prima di ogni test forward si cerca un guasto; se il GARCH passa con potenza attesa dell'oracolo sotto
   l'80%, e' un campanello: si indaga prima di leggerlo come PASSA. I parametri dei processi simulati **non si cambiano**
   dopo aver visto il rapporto (ridisegno post-esito, conta trial, §7.7). Con 50 repliche × 3 coppie l'HMM ha un errore
   standard di ~3 punti: 0,78 e 0,82 non si distinguono, ma il criterio resta quello pre-registrato.
5. **Esito riportato** (`esiti/pos_garch.json`, `esiti/pos_hmm.json`): frequenza media per coppia col p puntuale e
   intervallo al 95% a cluster sulla replica, la stessa con l'intervallo, frequenze per coppia, frequenza del nodo (per
   l'HMM e' la procedura sulle 3 coppie del controllo a 1,25%, non il nodo vero di 18), previsioni portate alla soglia.
   Semi: positivo GARCH 20261122, positivo HMM 20261123, rapporto effetto/MDE 20261124.
