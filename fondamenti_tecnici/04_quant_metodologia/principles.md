---
titolo: Metodologia Quant & Bias del Backtest
fonti:
  - "_sorgenti/Quant backtest notes.txt"
tipo: concetti
---

# Metodologia Quant & Bias del Backtest

> Un backtest bello non prova nulla: è una "scena del crimine" da interrogare, non un trofeo. Un'equity curve in salita con Sharpe 1.5-1.7 fallisce live se le fondamenta statistiche sono marce. I tre bias che distruggono una strategia sono **look-ahead**, **overfitting / data snooping** e **survivorship**; i costi di transazione vengono dopo. Questo file è **la teoria dietro la nostra quant-review** — i rimedi qui descritti sono già implementati in [`core/quant_metrics.py`](../../core/quant_metrics.py) e operativi nel protocollo [`QUANT_REVIEW_PROTOCOL.md`](../../docs/QUANT_REVIEW_PROTOCOL.md).

## Concetti

### 1. Look-ahead bias

**Definizione**: incorporare nella decisione di trading informazione che **non era disponibile** al momento in cui il trade è stato aperto.

Analogia delle due buste:
- **Envelope 1** — informazione accessibile *al o prima* del momento della decisione (filtration legittima).
- **Envelope 2** — informazione disponibile *solo dopo* il punto di decisione.

Usare dati dell'Envelope 2 per decidere significa "sbirciare nel futuro": gonfia artificialmente la performance. Nell'esempio della fonte, una strategia long-short market-neutral su basket di equity (segnale ranked per quantili) mostrava uno Sharpe iniziale ~3 con relazione monotona tra bucket di segnale e forward return. **Corretto il look-ahead, lo Sharpe crolla** da ~3 a un valore molto più basso.

Insidia chiave: il look-ahead non produce sempre un backtest "troppo perfetto". A volte lascia un segnale **modestamente promettente ma falso** (Sharpe 0.9-1.2), che inganna anche quant esperti. Forme tipiche:
- usare informazione di una settimana avanti per decidere oggi;
- normalizzare il segnale con i **forward return**;
- disallineamento dei timestamp / errori di timing su quando il dato arriva davvero.

**Rimedio**: ogni modello, parametro e dataset deve essere strettamente adattato alla **filtration** dei dati disponibili al momento della decisione — nessun dato futuro deve filtrare nel segnale. Nel repo il rischio è formalizzato dal **purging + embargo** della CPCV ([`cpcv_splits`](../../core/quant_metrics.py)) e dal caveat operativo sulla regime timeline (`data/regime_timeline_gbpusd.csv`): la label calcolata sul close del giorno stesso è look-ahead e va usata **solo con lag di 1 giorno** per strategie intraday.

### 2. Overfitting / data snooping / p-hacking

**Definizione**: testare ripetutamente molte combinazioni di parametri o modelli sugli **stessi dati storici** e scegliere quella che appare migliore per puro rumore statistico, senza contenuto predittivo reale e senza out-of-sample.

Esempio della fonte (MA crossover): le coppie (3,5) o (7,12). La (7,12) ha lo Sharpe IS più alto e tenta il trader a portarla live. Ma se sono state provate **molte** coppie, scegliere la "migliore" è overfitting della parametrizzazione al passato. **Out-of-sample la (7,12) performa male, Sharpe ~ -1.8.**

Red flag di overfitting: **instabilità parametrica** — se un piccolo cambio (es. da (7,12) a (8,12)) fa crollare la performance, il modello è probabilmente overfit e instabile. Una strategia robusta resta stabile su variazioni ragionevoli dei parametri.

| Problema | Descrizione | Mitigazione |
|---|---|---|
| Overfitting parametri | Set che fittano lo storico ma generalizzano male | Walk-forward validation |
| Selection bias (molti modelli) | Provare molti modelli e scegliere il migliore per caso | Criteri di selezione rigorosi |
| Instabilità parametrica | Piccoli cambi → grandi cali di performance | Preferire modelli stabili/robusti |
| Mancanza di razionale economico | Modelli senza giustificazione di mercato | Statistica + domain knowledge |

**Rimedi nel repo** (tutti in [`core/quant_metrics.py`](../../core/quant_metrics.py)): il numero di trial provati va penalizzato col **Deflated Sharpe Ratio** ([`deflated_sharpe_ratio`](../../core/quant_metrics.py)); la probabilità che il best IS sia sotto la mediana OOS è il **PBO via CSCV** ([`pbo_cscv`](../../core/quant_metrics.py)); il multiple-testing tra varianti si controlla col **White's Reality Check** ([`whites_reality_check`](../../core/quant_metrics.py)); la robustezza vs rumore col **Monte Carlo permutation test** ([`mc_permutation_test`](../../core/quant_metrics.py)).

### 3. Survivorship bias

**Analogia degli aerei WWII**: gli analisti studiavano i fori di proiettile sugli aerei *tornati* per decidere dove blindare, ignorando gli aerei *non tornati* (colpiti dove non si vedevano fori). L'errore è guardare solo i sopravvissuti.

Nel trading: un backtest che esclude le aziende fallite o delistate ("cimitero") gonfia artificialmente la performance. Includendo correttamente le delisted, il rendimento **degrada drasticamente, talvolta diventa negativo**.

**Rimedio**: definire l'universo **dinamicamente** — a ogni timestep T della decisione, l'universo deve includere **tutte** le società esistenti in quel momento, comprese quelle che poi falliscono/delistano. L'universo può basarsi su indici storici con delisted, market cap o altri criteri, purché rifletta il mercato reale al tempo T. Rilevante per [`06_stock_selection`](../06_stock_selection) e lo Stock Selector del repo.

### 4. Walk-forward come mitigazione

Procedura raccomandata contro l'overfitting:
1. spezza i dati in slice sequenziali (es. alcuni mesi IS, alcuni OOS);
2. ottimizza i parametri su ogni slice in-sample;
3. testa sul successivo blocco out-of-sample;
4. fai rotolare il processo in avanti nel tempo.

Riduce la probabilità di overfitting e produce set di parametri più robusti. Implementato in [`walk_forward`](../../core/quant_metrics.py) (anchored e rolling); il protocollo richiede OOS **mai sotto il 20%** del sample e misura il **degrado** IS→OOS come metrica di verdict.

**Dominio di validità (mappa dei modelli).** Il walk-forward valida la **persistenza di un edge** su regimi già visti; **non** predice il **timing di un evento di coda inedito** (il 2008 non era nel walk-forward del 2007). Sono due domande diverse e non vanno confuse:
- *"Questa strategia regge fuori campione / cambia regime?"* → sì, è il lavoro del walk-forward (e dell'holdout: vedi [[feedback_backtest_long_history_falsification|storico=laboratorio di falsificazione]]).
- *"Sopravvivrò al prossimo crash?"* → **no backtest lo certifica**; è una questione di **posizionamento per la sopravvivenza** (hedge/optionality), non di predizione (vedi [[05_portfolio_rischio]] §Tail risk).

Non è "il walk-forward è inutile" (falso, ci ha appena salvati sull'ORB): è che lo storico serve a **falsificare** un edge, non a promettere immunità dai tail. Domìni separati, entrambi necessari.

### 5. Costi di transazione, spread, slippage (secondari)

Considerazioni reali ma **non bias core**: costi di transazione, impatto bid-ask spread, slippage di mercato. Erodono l'equity curve. Ma sono **secondari**: se una strategia non è viabile dopo aver corretto i 3 bias, aggiungere i costi non fa che peggiorare il quadro. Vanno comunque modellati (lo Step 5 del protocollo verifica spread variabile, slippage 2× su stop, commissioni, swap, lot rounding).

### 6. Strumenti di backtest (librerie Python) — riferimento

Il nostro harness è custom (`core/runner.py` + `backtesters/`), pensato per integrarsi con la quant-review. Se in futuro servisse un **motore pronto** per esplorare grandi griglie di parametri, walk-forward o portafogli multi-asset più velocemente, le librerie Python serie sono:

- **pybroker** (`pip install lib-pybroker`) — **la più allineata alla nostra filosofia**. Engine NumPy/Numba veloce, ML-native, **walk-forward** integrato, e soprattutto **prevenzione del look-ahead by-design** (gli indicatori vedono solo il passato) + **bootstrap metrics**: `pybroker.eval` calcola CI bootstrap **BCa** (bias-corrected & accelerated) su Sharpe/profit-factor e upper-bound CI sul max drawdown (99.9/99/95/90%). È l'opposto dei "scoring engine" commerciali che premiano il backtest grezzo.
- **vectorbt** — backtest vettorizzati molto rapidi, ideale per sweep di parametri.
- **bt** — portfolio/allocation con ribilanciamento. **backtesting.py** — single-asset, API semplice. **zipline** — event-driven, pipeline universo.

Caveat: un motore veloce rende facilissimo il look-ahead e l'overfitting su griglie enormi — vanno comunque passati i gate di §1-§4 (DSR, PBO, walk-forward). Un pattern d'integrazione pulito (review FinceptTerminal) è "**Python single source of truth**": ogni engine dietro un'interfaccia provider comune.

**Complemento metodologico (review pybroker → implementato).** Il nostro `core/quant_metrics.py` copre la *distribuzione null* (MC permutation, White's RC) e la penalizzazione multiple-testing (DSR, PBO). Il tassello complementare — l'**intervallo di confidenza sul metric osservato** (es. lower bound dello Sharpe reale) — è ora implementato dependency-free in [`bca_bootstrap_ci`](../../core/quant_metrics.py) (bootstrap **BCa**, bias-corrected & accelerated, Efron 1987): dato un array di returns e una metrica, restituisce `point`/`low`/`high`. **Regola d'oro**: decidi sul **lower bound**, non sul valore centrale (uno Sharpe 2.2 su 40 trade può avere CI 95% con estremo inferiore < 0 → edge non affidabile). Resta valida l'opzione di adottare l'engine completo `pip install lib-pybroker` per backtest+eval. Dettagli nel catalogo review esterno (`github_repo_reviews/pybroker.md`).

### 7. Finestre sovrapposte → persistenza/IC fasulla (stride / disjoint sampling)

**Definizione**: stimare statistiche di **persistenza, autocorrelazione, matrici di transizione o
Information Coefficient (IC)** da **finestre/return sovrapposti** gonfia artificialmente il segnale.
Due finestre rolling consecutive da N barre condividono N−1 barre: la sovrapposizione **fabbrica
persistenza** (diagonale della transizione, autocorrelazione, significatività dell'IC) che nei dati
non c'è. È il cugino del look-ahead/overfitting per le serie autocorrelate.

Esempi:
- **Matrice di transizione di regime (Markov)**: etichettare i regimi da rolling return a 20 giorni
  e contare le transizioni giorno-su-giorno conta quasi sempre "stesso stato" perché le finestre si
  sovrappongono → **stickiness illusoria sulla diagonale**. Va contata tra finestre **non
  sovrapposte** (stride = lunghezza finestra). [Materiale "Markov 2.0", FIX 1; il blueprint
  [markov_regime_skill](../blueprints/markov_regime_skill.md) segnala che la v1.0 ha questo bug.]
- **IC di un alpha** misurato su return sovrapposti (forward 30g campionati ogni giorno): il CI è
  troppo stretto, la significatività gonfiata. Misurare su **barre disgiunte** (ogni h barre, return
  a h) — il consiglio "disjoint bars" ricorrente nella prassi quant.

**Rimedio**: per qualunque statistica di persistenza/transizione/IC, **calcola anche la versione
stride-sampled (non sovrapposta)** e confrontala con quella overlapping; tratta come onesta solo la
non-sovrapposta. Si lega al nostro **`n_eff` via block-bootstrap** (skill backtest): N osservazioni
clusterate ≠ N indipendenti.

### 8. CAGR come test di plausibilità (BS-test) + Rule of 72

Il **CAGR** (crescita composta annua: il tasso costante che replica il valore finale da quello iniziale) non predice il futuro, ma è un potente **test di plausibilità** su claim di performance. Comprimendo la crescita composta su decadi, smaschera i numeri impossibili: molti claim di day-trading ("+X% al mese"), composti per anni, producono ricchezze terminali che **superano la ricchezza globale** — quindi sono esagerati o fabbricati. È il cugino long-horizon del nostro "Sharpe retail > 3 = quasi certo errore".

- Benchmark di realtà: l'**S&P 500** ha un CAGR reale (inflation-adjusted) storico di **~7.5%/anno**. Un edge che implica CAGR molto sopra questo, sostenuto per anni, richiede prove straordinarie.
- **Rule of 72**: anni per raddoppiare $\approx 72/\text{CAGR}\%$. A 7.5% → ~9.6 anni per il ×2, ~19 per il ×4, ~29 per il ×8. Modello mentale rapido per sentire se un claim di raddoppio è realistico.
- Caveat: il CAGR **liscia la volatilità** e assume reinvestimento allo stesso tasso → misura crescita passata, non rischio né garanzia futura. Da leggere sempre col volatility drag e il drawdown accanto (vedi [[05_portfolio_rischio]]).

### 9. Pre-mortem: le direzioni principali di rischio (il complemento qualitativo)

Tutto ciò che precede è **ex-post e statistico**: misura un edge su un campione. Ma i modi in cui una
strategia muore live sono spesso **fuori dal campione per costruzione** — non perché siano tail rari,
ma perché **non sono grandezze di mercato**. Nessun DSR, PBO o walk-forward vede il mentore che
smette di postare.

**Direzioni principali di rischio** = l'elenco, scritto **prima** di impegnare capitale, dei fattori
che possono uccidere la tesi. È un **pre-mortem**: si assume che fra un anno il sistema sia morto e si
enumerano le cause plausibili, ordinandole per (probabilità × danno). Serve a rendere esplicito ciò
che il backtest non può nemmeno interrogare.

**Esempio svolto — segnali mentore XAUUSD** (l'unico edge positivo misurato, vedi
[`DECISIONS.md`](../../DECISIONS.md)). L'edge statistico è robusto (direzione ~2/3, stabile 6 mesi,
tollerante al ritardo fino a 60'), ma le direzioni principali di rischio sono **quasi tutte
non-statistiche**:

| Direzione di rischio | Natura | Il backtest la vede? |
|---|---|---|
| **Key-man**: il mentore smette, cambia stile o inizia a sbagliare | strutturale | no — la serie storica assume che continui |
| **Compliance**: le prop vietano copy-trading | regolamentare | no |
| **Rottura del canale/parser**: formato messaggi cambia, account chiuso | tecnica | no |
| **Degrado dell'esecuzione**: slippage/latenza erodono la tolleranza al ritardo | operativa | parzialmente (solo se modellata) |
| **Cambio di regime sull'oro** | di mercato | **sì** — questa è l'unica che il walk-forward interroga |

Il valore dell'esercizio è proprio la sproporzione: **una riga su cinque è misurabile dal backtest**.
Un sistema validato solo statisticamente è validato su un quinto delle sue cause di morte.

**Dominio di validità (mappa dei modelli).** La fonte da cui viene questo concetto sostiene la tesi
più forte — *"i modelli quantitativi e i dati storici non misurano il rischio forward; vince la
profondità qualitativa/esperienza"*. Presa alla lettera è una **licenza a scavalcare un NO-GO
pre-registrato con l'intuito**, cioè esattamente il fallimento contro cui è costruito questo repo
(NXT, ricerca livelli, ORB). Il conflitto si risolve per **domini**, non eleggendo un vincitore
(dettaglio in [`DECISIONS.md`](../../DECISIONS.md) §Mappa dei modelli):

- Dominio della fonte: **scommessa discrezionale concentrata** su una singola entità analizzabile
  fondamentalmente. $n=1$, non esiste campione da backtestare, e l'edge **è** la profondità informativa.
- Dominio nostro: **regole sistematiche ripetibili** su strumenti liquidi. Il campione esiste e il
  fallimento dominante è l'**overfitting**, non la superficialità.

Regola che ne deriva: **il qualitativo genera ipotesi ed enumera rischi; non valida mai.** Un
pre-mortem non promuove una strategia bocciata dai gate §1-§4, e un'ipotesi nata dalla profondità
qualitativa passa comunque dalla pre-registrazione.

Corollario sul **Bayesian updating** (pure dalla fonte): "itera e aggiorna le credenze" è sano in
fase di generazione, ma applicato ingenuamente **a valle di un test** diventa razionalizzazione
post-hoc di un risultato negativo. L'aggiornamento su un edge pre-registrato si fa con **nuovi dati
forward**, non rileggendo gli stessi.

> ⚠️ **Nota sulla fonte**: il materiale si chiude con un lead magnet (corso/research note gratuita).
> "I modelli non funzionano, l'esperienza sì" è anche l'argomento di vendita di un corso di
> esperienza. Non è un motivo per scartare il concetto — è un motivo per non concedergli autorità
> **contro** risultati misurati.

## Regole operative

- **Scrivi il pre-mortem prima del capitale.** Per ogni sistema, elenca le direzioni principali di
  rischio ordinate per (probabilità × danno) e marca quali il backtest può interrogare. Se la
  maggioranza è non-statistica, la validazione quant **non basta** come gate d'accensione.
- **Il qualitativo genera ipotesi, non valida.** Nessuna profondità di ragionamento promuove una
  strategia bocciata dai gate statistici; nessun aggiornamento bayesiano su dati già usati.
- **Sharpe primario, max drawdown secondario.** Lo Sharpe è la metrica di test principale; il max DD è di contorno. Ma lo Sharpe assume return normali — affianca sempre Sortino/Calmar/CVaR/Ulcer e, per leggere code e asimmetria senza assumere normalità, **Omega** ([`omega_ratio`](../../core/quant_metrics.py)) e **Tail ratio** ([`tail_ratio`](../../core/quant_metrics.py)). Quando esiste un benchmark di riferimento (es. buy&hold dell'asset), usa le metriche relative — alpha, beta, information ratio, tracking error, R² ([`benchmark_metrics`](../../core/quant_metrics.py)) — per distinguere edge reale da semplice esposizione direzionale.
- **Prima i 3 bias, poi i costi.** Non perdere tempo a raffinare spread/slippage su una strategia che non sopravvive a look-ahead/overfitting/survivorship.
- **Filtration sempre**: nessun dato futuro nella decisione. Regime timeline solo con lag ≥1 giorno per intraday.
- **Mai persistenza/transizioni/IC da finestre sovrapposte.** Usa stride/disjoint sampling (stride = lunghezza finestra), riporta `n_eff`; l'overlapping va mostrato solo come confronto, mai come prova.
- **Conta i trial.** Se non documentati, assumi ≥100 e applica DSR (Bailey-LdP 2014). Sharpe retail > 2 = red flag; > 3 = quasi certo errore metodologico.
- **Instabilità parametrica = NO-GO.** Se piccole variazioni dei parametri ribaltano la performance, il modello è overfit.
- **Universo dinamico per equity**: includi delisted/falliti al timestep T.
- **Onere della prova sulla strategia**: in caso di verdict ambiguo, default a NO-GO.
- **CAGR come BS-test**: prima di credere a un claim, componilo su anni con la Rule of 72; se implica CAGR ≫ ~7.5% reale sostenuto a lungo, pretendi prove straordinarie. Il walk-forward valida la persistenza dell'edge, **non** immunizza dai tail (posizionati per sopravvivere, non predici).
- **Soglie operative** (vedi protocollo): PBO < 15% accettabile, > 30% sospetto, > 50% random; DSR significativo al 95%; degrado OOS < 30% per GO; < 50 trade IS = INSUFFICIENT DATA.

## Collegamenti

- [[03_regimi_macro]] — l'edge è condizionato al regime; un backtest "tutto in regime favorevole" è una forma di selection bias.
- [`06_stock_selection`](../06_stock_selection) — dove il survivorship bias morde di più (universo equity).
- [`core/quant_metrics.py`](../../core/quant_metrics.py) — implementazione dei rimedi: DSR, PBO via CSCV, CPCV (purging+embargo), walk-forward, Monte Carlo permutation, White's Reality Check, BCa bootstrap CI sul metric osservato (`bca_bootstrap_ci`).
- [`docs/QUANT_REVIEW_PROTOCOL.md`](../../docs/QUANT_REVIEW_PROTOCOL.md) — protocollo passo-passo che applica questa teoria.
- [`agents/quant_reviewer.md`](../../agents/quant_reviewer.md) — la persona reviewer (rigore López de Prado / Bailey / Harvey), adversariale per default.
- Casi reali (entrambi **NO-GO**): [`docs/reviews/london_breakout-2026-05-29.md`](../../docs/reviews/london_breakout-2026-05-29.md) e [`docs/reviews/tsmom_jpy-2026-05-29.md`](../../docs/reviews/tsmom_jpy-2026-05-29.md). Per il London Breakout il cap era proprio il **look-ahead della regime timeline** (label same-day).
- [`DECISIONS.md`](../../DECISIONS.md) — log delle decisioni GO/NO-GO derivanti dalle review.

## Fonti

- `_sorgenti/Quant backtest notes.txt` (~95 righe) — distillato fedele: i 3 bias cardinali, esempi (Sharpe ~3→crollo per look-ahead; MA (7,12) IS positivo / OOS ~ -1.8; aerei WWII per survivorship), walk-forward, costi secondari, metafora "scena del crimine".
- `_sorgenti/Nuove nozioni teoriche 2026-07-16.txt` (Quant Guild) — tasselli distillati qui: **CAGR come BS-test + Rule of 72** (§8) e il **caveat sul dominio del walk-forward** (valida persistenza edge, non predice tail; §4). Il grosso del file (portfolio/rischio/tail) è distillato in [[05_portfolio_rischio]]. Tracciato in [`_INTAKE.md`](../_INTAKE.md).
- `_sorgenti/Appunti misti 2026-08-04.txt` — blocco 2 ("Understanding and Evaluating Risk in Financial Markets"). Distillato in §9: **direzioni principali di rischio / pre-mortem**, con esempio svolto sui segnali mentore. La tesi forte della fonte ("i modelli quantitativi non misurano il rischio forward") è **mappata come conflitto per domìni**, non assorbita: vedi [`DECISIONS.md`](../../DECISIONS.md) §Mappa dei modelli. Blocchi 1/3/4 dello stesso file: vedi [[08_asset_allocation_passiva]], [[03_regimi_macro]] e [`_INTAKE.md`](../_INTAKE.md).
