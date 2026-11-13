---
tipo: preregistrazione
stato: BOZZA
approvata: ""
aggiornato: 2026-11-13
decisione: "Matteo: gate degli strumenti e strada A (10-11/11); errore di famiglia 5% = 2,5% GARCH + 1,25% HMM + 1,25% premio di volatilita', holdout di due anni (11/11); orizzonte massimo 5 giorni, strumenti dei test piu' completi (11/11); varianti GARCH approvate, benchmark dell'HMM delegato a Claude secondo S4, premio di volatilita' a 30 giorni come definizione (13/11). DECISIONS 2026-11-10, 2026-11-11"
metrica_corrente: "nessuna: nessuna previsione calcolata"
nota: "Famiglia di STRUMENTI (binario `strumenti`, STRATEGY_LIFECYCLE §8ter): niente trade, niente R, niente DSR. Verdetto sul blocco di holdout 2024-11-11 -> 2026-11-10, aperto una volta."
---

# Pre-registrazione — Previsione della volatilita' (famiglia `volatilita`, binario `strumenti`)

Regole che questa pre-registrazione applica: [STRATEGY_LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md)
(sigle G, H, C, P, S). Fonti della letteratura: [referto del 10/11](../referti/gate_strumenti_volatilita_2026-11-10.md),
claim in quarantena. Dati e controlli: [motore/data/README](../../../motore/data/README.md), sezioni `volatilita_m5`,
`volatilita_mt5`, `futures_1m`. Famiglia nel contatore: `volatilita`.

## 1. Cosa si misura, e cosa no

**Lo strumento.** Una previsione della varianza dei prossimi 1 e 5 giorni di borsa (e, per il premio di volatilita',
dei prossimi 30 giorni di calendario), fatta con i soli dati fino alla chiusura di oggi.

**La proprieta'.** La previsione ha una perdita **QLIKE** piu' bassa di quella di un benchmark semplice nominato qui,
fuori campione. Per il premio di volatilita': la varianza implicita nel VIX supera in media la varianza realizzata dei
30 giorni successivi.

**Cosa NON si misura.** Nessun rendimento, nessuna regola di trade. Un esito positivo dice "previsione piu' accurata",
non "piu' profitto" (§8ter, ultimo capoverso): il passaggio a una strategia (sizing, stop, filtri) lo testano i soci.

**Stessa grandezza = stessa famiglia (Checklist 10, punto 8).** Nessuna famiglia del contatore ha misurato
l'accuratezza di una previsione di varianza. `meanrev_vol`, il gradiente di volatilita' di `trend_momentum` e la
"gestione per volatilita' come segnale" (backlog §H, chiusa in partenza) misurano **rendimenti** condizionati alla
volatilita': un'altra grandezza. Se un esito di questa famiglia venisse usato per rileggere quei verdetti, sarebbe un
trial di quelle famiglie.

## 2. Dati

| Strumento | File (fuori da git) | Usato da |
|---|---|---|
| SPX500, NAS100, DOW, RUSSELL, DAX | `motore/data/prezzi/volatilita_m5/<NOME>_M5.csv` (Dukascopy, UTC) | 2015-01-02; RUSSELL dal 2018-08-08 (prima non ci sono dati) |
| XAUUSD, XAGUSD, WTI, EURUSD | stessa cartella | 2015-01-02 |
| VIX | `motore/data/cache/free/VIX_D1.csv` (CBOE, aggiornato al 2026-11-12) | solo premio di volatilita' |

**Perche' dal 2015.** Nel 2012-2014 il feed Dukascopy degli indici ha fino al 10% di barre ferme anche in seduta, ed
EURUSD il 28-29% sulle 24 ore; dal 2015 lo 0% (controllo dell'11/11, README dei dati). Una varianza realizzata con un
feed che cambia natura non e' confrontabile nel tempo.

**Definizione del giorno e del bersaglio (G1).** Rendimenti logaritmici a 5 minuti, barre bid.
- **Indici** (seduta cash: 9:30-16:00 New York; DAX 9:00-17:30 Francoforte, con l'ora legale dei rispettivi fusi):
  varianza del giorno = **RV di seduta + rendimento notturno al quadrato** (chiusura di seduta di ieri → apertura di
  seduta di oggi). E' la proxy della varianza da chiusura a chiusura; il rendimento giornaliero dei modelli e' da
  chiusura di seduta a chiusura di seduta.
- **Strumenti a 24 ore** (oro, argento, petrolio, euro): il giorno va dalla prima barra dopo la pausa delle 17:00 New
  York alla chiusura delle 17:00. **Il rendimento a cavallo della pausa (e del fine settimana) resta fuori** sia dal
  rendimento giornaliero dei modelli sia dal bersaglio: nel petrolio Dukascopy, che e' un CFD su futures, li' cadono i
  salti di rollover (nel periodo di sviluppo 16 salti alla riapertura il giorno 19 del mese e il +29% del 19/04/2020,
  controllo del 13/11, solo prezzi). La grandezza misurata e' quindi la varianza **della giornata di contrattazione**.
- Dentro la seduta o la giornata, un rendimento a cavallo di un buco di oltre 15 minuti non entra nella RV.
  Un giorno con meno del 90% delle barre attese e' escluso dal bersaglio (non dalla stima); il conteggio si riporta.
- **Orizzonte h = 5**: somma delle varianze dei 5 giorni di borsa successivi. **Premio di volatilita'**: somma delle
  varianze giornaliere dell'SPX500 nei giorni di borsa in (t, t + 30 giorni di calendario].

## 3. Divisione dei dati (H1-H3)

- **Holdout**: dal **2024-11-11 al 2026-11-10** (due anni, comune a tutti gli strumenti; la fine comune dei file
  Dukascopy e' il 2026-11-11). Ultima origine di previsione: quella il cui bersaglio finisce entro il 2026-11-10
  (per h = 5, il 2026-11-03; per il premio, il 2026-10-09).
- **Sviluppo**: dal 2015-01-02 al 2024-11-08. Nessun bersaglio di sviluppo cade nell'holdout: le origini di sviluppo si
  fermano 5 giorni di borsa (30 di calendario per il premio) prima del 2024-11-11.
- **Stima**: finestra mobile di **1.000 giorni di borsa**, lunghezza fissa (H3); prima previsione di sviluppo quando la
  finestra e' piena (fine 2018 per quasi tutti; meta' 2022 per RUSSELL). **Ristima ogni 5 giorni di borsa**; fra una
  ristima e l'altra il filtro va avanti coi parametri congelati. Nell'holdout la finestra scorre su dati di sviluppo e
  di holdout passati: e' filtraggio, non lisciamento.
- Media zero, rendimenti in percento, distribuzione **gaussiana (QMLE)**.

## 4. Sottofamiglie, varianti, benchmark (S1-S5, C1-C2)

| Nodo | Varianti (tutte nello SPA, C2) | Benchmark (S4) | Ipotesi del nodo (S3) |
|---|---|---|---|
| **GARCH** | GARCH(1,1), GJR-GARCH(1,1,1), EGARCH(1,1,1) — libreria `arch` 8.0.0 | **EWMA, λ = 0,94** (RiskMetrics, zero parametri) | almeno una variante ha QLIKE media piu' bassa di EWMA |
| **HMM** | varianza a regimi di Markov sui rendimenti giornalieri, **2** e **3** regimi (`statsmodels` `MarkovRegression`, `switching_variance=True`, senza costante); previsione = somma su regimi della probabilita' **filtrata** propagata × varianza del regime | **GJR-GARCH(1,1,1)** sugli stessi rendimenti | almeno una variante ha QLIKE media piu' bassa del GJR |
| **Premio di volatilita'** | uno: varianza implicita a 30 giorni = (VIX/100)² × 30/365, in unita' di varianza giornaliera, contro la varianza realizzata dei 30 giorni di calendario successivi (§2) | premio nullo | media del premio > 0 |

- **Perche' GJR per l'HMM** (S4: "contenuto in piu' della probabilita' filtrata"): l'HMM usa i rendimenti
  giornalieri, come il GJR. Contro HAR, che usa la RV intraday, perderebbe per l'informazione in meno, non per i regimi.
  Il benchmark e' fissato qui e non dipende dall'esito del nodo GARCH.
- **HMM (S5)**: regimi ordinati per varianza crescente a ogni stima (σ₁ < σ₂ < σ₃), 20 partenze casuali con seme fisso,
  si tiene la verosimiglianza migliore; una stima che non converge usa i parametri della stima precedente, e si conta.
- **Premio di volatilita' a 30 giorni** (Matteo, 13/11): e' la definizione del VIX, non un orizzonte di trading, quindi
  non viola il massimo di 5 giorni. Solo SPX500 (l'unico indice con una volatilita' implicita nei dati).
- **Fuori dal contatore** (S1): Black-Scholes, Heston, SABR (solo teoria).
- **Solo descrittivi** (nessun verdetto): HAR-RV di Corsi sulla RV, GARCH(1,1) come riferimento forte (G3), la media
  delle tre varianti GARCH, la media di lungo periodo (varianza della finestra) e la persistenza (varianza di ieri)
  come riferimenti di skill.

**Contabilita' (C1).** Serie di previsione = modello × strumento × orizzonte: GARCH 3 × 9 × 2 = **54**, HMM 2 × 9 × 2 =
**36**, premio **1**. Totale **91**, contati nel contatore quando le previsioni vengono calcolate (all'approvazione il
contatore resta a 0).

## 5. Gate statistico (G2, G4, G8) e verdetto

- **Perdita primaria**: QLIKE = log(h) + RV/h sulla varianza (h previsione, RV bersaglio); secondaria MSE sulla
  varianza (descrittiva).
- **Test per nodo GARCH e HMM**: per ogni coppia (strumento, orizzonte) uno **SPA di Hansen** (p-value `consistent`)
  delle varianti contro il benchmark, bootstrap stazionario, **5.000** ripetizioni, blocco √T, seme 20261113 (`arch.
  bootstrap.SPA`). Le 18 p-value del nodo si correggono con **Holm** (G8). Il nodo **rifiuta** se almeno una p
  corretta e' sotto la quota d'errore del nodo; si riporta su quali coppie.
- **Test del premio**: t a una coda sulla media del premio giornaliero (osservazioni sovrapposte), errori di
  **Newey-West con 21 ritardi**; robustezza descrittiva su osservazioni mensili non sovrapposte.
- **Errore di famiglia 5% a una coda, grafo con riciclo (S2)**: GARCH 2,5%, HMM 1,25%, premio 1,25%. Se un nodo
  rifiuta, la sua quota si divide in parti uguali fra i nodi non ancora rifiutati, che si ritestano alla quota nuova
  (procedura grafica di Bretz et al. 2009).
- **Verdetto per nodo**: *confermato* (rifiuta), oppure *non dimostrato, MDE = ...* (G6). Mai "refutato" senza MDE.
- **Descrittivi** (non decidono): StepM (quali varianti battono il benchmark), MCS al 10% con statistica di range su
  tutti i modelli del §4 compresi i riferimenti, skill rispetto a media di lungo periodo e persistenza, Mincer-Zarnowitz
  in livelli con errori HAC (G5), sensibilita' al blocco del bootstrap (√T/2 e 2√T).
- **G7 (code)**: non si applica: lo strumento non promette quantili.
- **Confronti complementari nell'holdout** (non decidono, H1): RV dei futures CME a 1 minuto (`futures_1m`, dal
  2025-11) e del feed MT5 (`volatilita_mt5`, dal 2025-06) contro la RV Dukascopy, sugli stessi giorni; i salti di
  rollover dei futures si tolgono nel loader.

## 6. Prima dell'apertura (G6, G9)

Nell'ordine, ognuno scritto in un'aggiunta datata a questo documento **prima** di aprire l'holdout:
1. **Controllo della pipeline (G9)**, su dati simulati: 200 repliche di 9 serie lunghe quanto i dati veri.
   *Negativo*: processo EWMA/IGARCH (λ = 0,94); il nodo GARCH non deve rifiutare piu' del **doppio** della sua quota
   (5% delle repliche), altrimenti la pipeline e' rotta e si blocca. *Positivo*: processo GJR (ω = 0,02, α = 0,03,
   γ = 0,10, β = 0,90) con bersaglio = varianza vera × rumore lognormale tarato sulla RV; si riporta la frequenza di
   rifiuto con 500 giorni di holdout. Stesso schema per l'HMM (processo a regimi contro GJR puro).
2. **Corsa di sviluppo** (2018/2022 → 2024-11-08): perdite di tutte le serie, solo descrittive. **Dopo averla vista
   non si cambia nulla** di §2-§5: una modifica e' una variante post-esito (P1-P3), esplorativa.
3. **MDE (G6)** per ogni nodo, dai dati di sviluppo: MDE = 2,80 × σ_HAC del differenziale di QLIKE (migliore variante
   contro benchmark) / √N, con N = giorni di holdout; per il premio, dalla serie di sviluppo del premio.
4. Revisione G1 del gatekeeper sull'aggiunta, poi **apertura unica** dell'holdout (H4) per i tre nodi insieme.

## 7. Rifiniture previste per i round 2-3 (P4)

Solo se il round 1 lo giustifica, e **mai sull'holdout**: su dati forward successivi all'apertura (H4, P3).
(a) distribuzione t di Student; (b) finestra di 1.500 giorni; (c) GARCH a regimi di Markov (Ardia et al. 2018), se
esiste un'implementazione Python verificata. Qualunque altra modifica e' post-esito ed esplorativa (P1).

## 8. Deviazioni (P5)

| Data | Cosa cambia | Perche' | Esplorativo? |
|---|---|---|---|
| — | — | — | — |
