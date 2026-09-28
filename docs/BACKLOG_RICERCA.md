# Backlog di ricerca — stato al 2026-08-27 (sera)

> Inventario di tutto ciò che è sul tavolo dopo la chiusura del funnel YouTube, diviso per **cosa
> si può effettivamente farci oggi**. Non è un piano: è la base per decidere quali binari aprire.
>
> Ordine dei bucket: **A** ha un numero da confermare · **B** ha una specifica meccanica completa e
> dati per testarla · **C** migliora qualcosa che già gira · **D** non ha un percorso di test oggi.
>
> **Vincoli di budget in vigore** — da tenere presenti in ogni decisione:
> pre-registrazioni da fonte esterna **2 di 2-3 usate nel trimestre** · max **3 round di rifinitura**
> per famiglia · **holdout: una apertura per famiglia**, non per variante.
>
> ✅ Dal 2026-09-19 questi numeri **non si copiano piu' a mano**: `python -m core.trial_ledger`
> li stampa dalla fonte ([`trial_ledger.json`](trial_ledger.json)) e `--check` esce **1** se uno
> e' sforato. Se questa riga diverge dal comando, ha ragione il comando.

---

## A — DA CONVALIDARE (esiste un numero, non è confermato)

| # | oggetto | il numero | cosa manca | costo |
|---|---|---|---|---|
| **A1** | **Playground / gradiente di volatilità** | ρ **+0,857** fra volatilità di gruppo ed E[R]. ✅ **Punto 1 — diagnostico di durata (21/09, 0 trial)**: il gradiente **sopravvive** (ρ +0,929 appaiata, +0,881 a durata fissa; il canale meccanico del random crolla da +0,619 a **+0,048**), **ma il livello si ribalta** — a parità di tempo in mercato la regola **perde dal random**: **−0,238** [−0,363;−0,098] e **−0,451** a durata fissa, positiva **1/8 gruppi**. [referto](TREND_DURATION_DIAGNOSTIC.md) | ⛔ **Punto 2 — POTENZA: condizione NON rispettata (21/09, 0 trial)**. Servono **7,3** strumenti indipendenti per braccio nello scenario più ottimistico e **29,3** in quello onesto (effetto dimezzato); il braccio ad **alta volatilità** ne ha **3,4**. Fuori scala **2,1×** nel caso migliore, **19,6×** nel caso pulito. Non è il numero di ticker (Dukascopy ne ha 58+41 liberi): le **19 crypto libere valgono 1,4 strumenti** (ρ misurato **+0,698**) e **nessun cross FX arriva al 20%** di volatilità → il test sarebbe **"crypto contro cross FX"**, circolare per costruzione. [referto](TREND_A1_HELDOUT_POWER.md) | **il punto 3 non si apre**: condizioni di riapertura scritte in §7 del referto. Round trend fermo a **2 di 3** |
| **A2** | **FADE** — ✅ **FAMIGLIA CHIUSA 2026-09-17: KILL**. Misurata coi soli fill ottenibili vale **E[R] = −0,250** BCa95 [−0,287; −0,210] su 5.506 trade; il +0,409 veniva per intero dal fill fantasma (46,1% dei setup). EA spento. Trial **2 di 3**, il terzo **non speso**. Vedi [DECISIONS 17/09 (4)](../DECISIONS.md) — nulla da convalidare. _(storico: test azzerato il 27/08)_ |
| **A3** | **ORB v2** — ✅ **CHIUSA 2026-08-27** | **NO-GO su 14,5 anni**, holdout gia' aperto | ⚠️ **niente**: l'utente ha **spento l'EA**. Verificato: zero posizioni, zero pendenti, ultimo ordine 25/08. La scelta §F si risolve in **F1**. I 10 trade chiusi **non vengono letti** — n=10 non ha potere contro 14,5 anni, e un P&L positivo creerebbe solo pressione a riaprire una famiglia con l'holdout esaurito. Riapertura solo alle condizioni gia' scritte in §F | **0 — fatto** |
| **A4** | **Segnali mentore XAUUSD** — ✅ **CHIUSA, voce corretta 2026-08-24, verdetto RICONFERMATO 2026-09-18** | OOS originale (131 segnali): differenza appaiata **+0,277** BCa95 [+0,193; +0,353] · **E[R] +0,194** [+0,079; +0,289]. **Rifatto sulla finestra estesa a oggi (218 segnali): +0,274** [+0,209; +0,333] · **E[R] +0,173** [+0,083; +0,244]. 🔧 Il fix del fuso del 18/09 **non toccava questo test**: `to_engine` era gia' allineato da agosto, quindi il verdetto pre-registrato non e' mai stato contaminato | ⚠️ **niente**: il test e' **gia' stato eseguito e superato** il 2026-08-07 (131 segnali, 15/06→07/08, motore `analysis/mentor_signals/oos_validation.py`). E' il **primo verdetto positivo su un test pre-registrato** del workspace. La mia voce precedente (*"da verificare se e' partito"*) era sbagliata | **0 — fatto** |
| **A5** | **Audit dei risultati early-stage** — ✅ **FATTA 2026-09-18, 0 trial**. Protocollo scritto **prima** di aprire i motori ([protocollo](EARLY_STAGE_AUDIT_PROTOCOL.md) · [referto](EARLY_STAGE_AUDIT_REPORT.md)) | **Nessun verdetto era sbagliato**, ma due dicevano **meno** di quanto gli abbiamo fatto dire. **Livelli** ✅ confermato e piu' solido del dichiarato (CI < 1 punto su base 30%). **NXT continuazione** ✅ confermato ma il numero era sbagliato: **−0,118R**, non −0,44 — il fill fantasma valeva **+0,326R**. **ORB** 🟡 SPX500 refutato, **NAS100 mai misurato** (ogni CI contiene lo zero, MDE 0,135R). **TSMOM** ⚠️ **NON MISURATO**: MDE Sharpe **0,59** contro un atteso a priori di **0,3-0,5** | **0 — fatto** |
| **A6** | **Sensibilita' del verdetto Stage-2 del FADE** — ✅ **DECADUTA 2026-08-27** | — | non c'e' piu' un margine di cui misurare la sensibilita': il numero di partenza era un artefatto di fill. Assorbita da A2 | **0** |

---

## B — DA BACKTESTARE (spec meccanica completa + dati disponibili)

> Tutte e sei si eseguono sul feed **Dukascopy D1, 2012-2026, 27 strumenti su 8 gruppi**, già in
> repo. Nessuna richiede dati che non abbiamo.

| # | spec | fonte | perché è pronta | costo |
|---|---|---|---|---|
| **B1** | **Mean reversion Kichev** — ✅ **CHIUSA 2026-09-17**. La fonte dice solo *"price deviates significantly far from mean, exit 1-4 days"*: `SMA5` e la soglia **erano nostri**. Misura sulle **code** contro nullo matched (ri-allineamento circolare, 300 perm.): **3 gruppi su 8** confermano, soglia dichiarata prima era **5**. Il nullo non e' piatto ma **bimodale**: energy/index/fx_cross ritornano alla media, **crypto (−0,25) e agri continuano**. ⚠️ Inseguire i 3 che confermano = eleggere un vincitore dalla mappa dopo averla vista. Vedi [DECISIONS 17/09 (6)](../DECISIONS.md) | **0 trial spesi** |
| **B2** | **Breakout Kichev** — range della barra ≥ ~2× media range ultime 5 → entra in direzione; uscita **a tempo (2-5 giorni)** o quando il momentum svanisce | Kichev (D.1) | stessa cosa: completa e senza giudizio. ⚠️ Famiglia trend/momentum: **round 2 di 3 già speso** | 1 pre-reg + 1 round |
| **B3** | **Condizione di struttura sull'estensione estrema** — ✅ **CHIUSA 2026-09-21, 0 trial spesi**. Protocollo scritto prima ([B3_EXTENSION_STRUCTURE_PROTOCOL.md](B3_EXTENSION_STRUCTURE_PROTOCOL.md) · [motore](../analysis/extension/structure.py)): 1.733 eventi a `E>=3 ATR`, baseline random matched su strumento/direzione/anno/orizzonte. **H1 NO** (cella attesa **+0,007** [−0,145;+0,168], MDE 0,221), **H2 non valutabile**. ⚠️ Il risultato non e' un nullo debole: **le celle non esistono**. Normalizzando sull'ATR, a L=2-3 il **97,0%** e **93,6%** degli eventi ha gia' il range in espansione — e' **aritmetica** (3 ATR in 2 barre impongono barre da 1,5 ATR). La distinzione delle fonti vive di soglie in **percentuale** su strumenti a volatilita' eterogenea: normalizzata, **svanisce**. Il gate volume esclude 10 strumenti su 27 (corr volume/|rendimento| fra −0,03 e 0,14) e sono proprio **agri, bond, crypto, energy, metal**. Breadth **4/8**, e il segno piu' forte e' **crypto +0,248 = continuazione**, opposto all'ipotesi (coerente con B1). Non falsifica le fonti sul **loro** universo: dice che la condizione **non e' trasferibile** | **0 trial** |
| **B4** | **Variante di esecuzione del FADE: conferma sì / conferma no** — ⏸️ **DECADUTA 2026-09-19**: la famiglia FADE e' **KILL dal 17/09** (§A2), quindi non esiste piu' un lead su cui fare una variante di esecuzione. Misurata coi fill ottenibili la famiglia vale **−0,250R**, e l'audit A5 ha mostrato che **anche il lato opposto perde** (−0,118R): il livello non contiene informazione, non e' l'entrata a essere sbagliata. Si riaprirebbe solo alle condizioni di §A2 | **0 — decaduta** |
| **B5** | **Casella vuota: low volume node** — detector LVN accanto a POC/VAH/VAL | Carmine, Fabio, Yush (3 fonti) | verificato nel codice: `analysis/level_research/detectors.py` testa i nodi ad **alto** volume, mai quelli a **basso**. È l'ipotesi **complementare, meccanismo opposto**. ⚠️ Costa poco tecnicamente **ed è proprio questo il rischio**: cella aggiunta a una griglia con **384 trial di NULL**, molteplicità pagata dove non l'abbiamo contata. E tutte e tre le fonti la usano **con conferma di flusso**, che non possiamo replicare → testeremmo una versione amputata | 1 pre-reg **esterna** (budget 2/2-3) |
| **B6** | **Casella vuota: trend line inclinate** | Crooks, Silfrain, Tori (3 pro) — **Ariel contro** | i 384 trial erano **solo orizzontali**. Buco reale. ⚠️ Prior basso: 1 fonte su 4 le rifiuta **con la nostra stessa motivazione** (ambiguità del tracciamento) | 1 pre-reg **esterna** |
| **B7** | **Copier mentore: uscita a 1R invece che a TP1** — ✅ **CHIUSA 2026-09-18, 0 trial spesi**. L'ipotesi era **gia' misurata e non me n'ero accorto**: la "win-rate simmetrica (+1R prima di −1R)", metrica **primaria** della pre-reg di agosto, **e'** l'uscita a 1R. Confronto appaiato su n=627: TP1 **+0,1247** [+0,0737; +0,1712] contro 1R **+0,1246** [+0,0480; +0,2011], differenza **−0,0001** BCa95 **[−0,0633; +0,0596]** — identiche, e 1R porta **+58% di sd** a parita' di rendimento, quindi **peggiore**. ⚠️ Cadeva anche la premessa: "+0,294 di vantaggio contro +0,127 incassato" confrontava **punti di win-rate con R**. In R il vantaggio e' **+0,597** a TP1 e **+0,588** a 1R: lo stesso. Vedi [§10](MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md) | **0 trial** |

---

## C — DA IMPLEMENTARE IN COSE CHE GIÀ GIRANO

| # | intervento | dove | nota |
|---|---|---|---|
| **C1** | ~~Allegare il razionale al forward ORB~~ ✅ **DECADUTA 2026-08-27** | — | il forward **esisteva** ed e' stato **spento**. Non c'e' piu' un binario a cui allegare un razionale: vedi §A3 |
| **C2** | ~~Decidere su BTCUSD nel FADE live~~ ✅ **RISOLTA** | prereg FADE | BTCUSD **staccato**: 0 ordini post-fix. Resta 1 solo ordine residuo EURGBP.r (0 trade chiusi, nessun effetto sul campione) |
| **C3** | ✅ **FATTA 2026-09-18**, poi **riscritta quattro volte lo stesso giorno** — ogni volta per i **dati**, mai per il metodo. Valori validi = [§9](MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md) su **629 trade**: DD **11,7R**, serie negativa **5**, finestra minima **199 trade (~54 giorni)**. 🔧 Esiti non indipendenti ma **poco** (z=−1,81): il MC a blocchi da' **+1,09R / +10%** di drawdown rispetto al rimescolamento. ⚠️ §8 e precedenti sono **nulli** | copier | **0 trial** |
| **C4** | ✅ **VERIFICATA 2026-09-18: era gia' corretto.** `notifiers/_pip_table.suggested_lots` calcola `lots = (equity × risk%) / (distanza_SL_in_pip × valore_pip)` — rischio fisso in valuta, size derivata dalla distanza dello stop, esattamente come raccomandano le 3 fonti. Usa **equity** (non balance): `__main__.py:214`. Il rischio totale per segnale (1%) e' diviso fra le gambe, quindi non cresce coi TP. Nessuna modifica necessaria | motore di rischio | **0 trial** |
| **C5** | ✅ **FATTA e IMPLEMENTATA 2026-09-18 (sera)** — ha portato a galla sia il fix del fuso sia la sua doppia applicazione. Rimisurata sui dati corretti (696 segnali): senza gate l'esecuzione a mercato da' **E[R] −0,184** [−0,241; −0,125] contro il **+0,124** del replay; lo scostamento e' **sfavorevole nel 72%** dei casi e i due lati hanno segno opposto (**favorevole +0,209**, **sfavorevole −0,337**). Con **lo stesso 20 pip gia' in config applicato solo allo sfavorevole**: **293 segnali su 696 (42%), E[R] +0,159** [+0,076; +0,239] — meglio del replay stesso. ✅ `planner.py` reso asimmetrico + test di regressione sul lato favorevole. ⚠️ La soglia **non e' stata ricercata**: e' quella che c'era gia' | copier | **0 trial** |
| **C6** | ⏸️ **DECADUTA 2026-09-18, con condizione scritta.** Richiede ≥ 2 strategie vive e poco correlate: col KILL del FADE (17/09) ne resta **una** (copier mentore), quindi non c'e' nulla da ribilanciare. **Si riapre quando esistono 2 binari con capitale contemporaneamente**, e allora si parte dal numero di Kichev (due strategie anticorrelate: 20k senza ribilanciamento, 31,25k con) — che resta **non verificato** | — | **0 trial** |

---

## D — CONCETTO ISOLATO (nessun percorso di test oggi)

| # | concetto | perché è bloccato | si sblocca se… |
|---|---|---|---|
| **D1** | **Order flow** (assorbimento, delta cumulato, big trades, book) | servono **tick + book**; 12 video del funnel ci poggiano sopra | mai, realisticamente: il dato costa e il vantaggio è di latenza |
| **D2** | **Universo small cap USA** (first red day, parabolic short) | servono market cap, float, short interest, halt, e un broker con locate | non nel nostro perimetro |
| **D3** | **PEAD / episodic pivot** | serve la **sorpresa su utili e fatturato** | è l'unico setup del funnel con supporto accademico indipendente: da ricordare se l'universo si allargasse |
| **D4** | **Momentum cross-sectional di gruppo** (Ariel) | il feed 8 gruppi **c'è** — quindi non è bloccato dai dati, è bloccato dal **budget**: famiglia trend following con round 2/3 speso | se il playground (A1) chiude e libera il ramo |
| **D5** | **Regime da VIX** | il VIX non è nel feed D1 attuale | aggiungendo la serie — ma vale la pena solo se A1 dà un segnale |
| **D6** | **Livelli condizionati al calendario macro** | **porta chiusa per decisione** (2026-08-22): moltiplica la ricerca su 384 trial di NULL, e il calendario è il posto più pubblico del mercato | solo con evidenza esterna **quantitativa** nuova |
| **D7** | **Riflessività / affollamento come misura** | servono open interest, positioning, short interest | dati non disponibili sul nostro perimetro |

---

## E — DEBITO DI PROTOCOLLO — ✅ **ESTINTO il 2026-09-19** (E1-E6 tutte chiuse)

Non sono ricerca: sono le cose che rendono la ricerca affidabile. Fino al 2026-09-19
erano **prosa**, cioe' regole che si applicavano solo se qualcuno si ricordava di
applicarle — e ogni errore che dovevano prevenire e' accaduto **dopo** che la regola
era stata scritta. Ora sono **codice eseguibile e gate bloccanti**.

| cosa esiste adesso | dove | cosa impedisce |
|---|---|---|
| `core/resolve_trade.py` | E5 | 5 convenzioni d'uscita implicite in 4 copie (una valeva **0 contro +3R**) |
| `core/random_baseline.py` | E1 | baseline riscritto a mano, matching mai verificato, CI i.i.d. su controlli non indipendenti |
| `core/data_checks.py` | E3 | monotonia, duplicati, barre/anno, partenze scaglionate, file corto, **% di fill fantasma**, gap oltre lo stop |
| `core/trial_ledger.py` + `trial_ledger.json` | E2, E4 | contatore trial a memoria, budget sforati in silenzio, **provenienza dell'ipotesi** non dichiarata |
| `QUANT_REVIEW_PROTOCOL.md` **Step 3bis** | E6 | un verdetto (in **entrambi** i segni) su fill non ottenibili |

⚠️ **Quello che i nuovi controlli hanno trovato appena accesi** — nessuno era noto:
il playground (A1) confronta il reale col random a **holding 7 giorni contro 2**; il CI
i.i.d. sui controlli e' **28% piu' stretto** di quello corretto; **tre famiglie** hanno
il contatore trial non ricostruibile e **due** la provenienza dell'ipotesi non dichiarata.

| # | debito | perché conta |
|---|---|---|
| **E1** | ✅ **FATTO 2026-09-19** — [`core/random_baseline.py`](../core/random_baseline.py): `BarSampler` (istante casuale stratificato), `PoolSampler` (attributo campionato dal pool reale, es. la distanza di un livello), **`check_matching`** (la verifica, prima fatta a mano) e **`gap_ci`** (divario con bootstrap **a cluster sull'evento**). Equivalenza **bit-identica** con le 4 implementazioni storiche dimostrata in `core/tests/test_random_baseline.py` (stops / excursion / trend / level_research). [`analysis/trend/backtest.py`](../analysis/trend/backtest.py) migrato: **output identico**. ⚠️ Il test ha fatto emergere tre cose mai scritte: (a) i due bracci devono usare **lo stesso simulatore**, (b) la **durata di holding non e' matchabile** — e' un esito, si verifica e si dichiara (vedi A1), (c) il CI i.i.d. sui controlli e' **28% piu' stretto** di quello a cluster, cioe' finto. I motori storici **non** sono stati migrati: sono il registro di verdetti gia' emessi | **fatto** |
| **E2** | ✅ **FATTO 2026-09-19** — dato in [`docs/trial_ledger.json`](trial_ledger.json), letto e verificato da [`core/trial_ledger.py`](../core/trial_ledger.py) (`python -m core.trial_ledger`, `--check` esce **1** se un budget e' sforato o se una voce non cita le sue fonti). 11 famiglie ricostruite dalle pre-registrazioni e da DECISIONS. La **regola di futilita' e' diventata un numero**: a 250 osservazioni servono Sharpe **1,65** con 1 trial, **3,12** con 8, **4,64** con i 384 dei livelli. ⚠️ Tre famiglie (`opening_range`, `trend_momentum`, `london_breakout`) hanno il conteggio a **`null`**: non e' ricostruibile perche' all'epoca non era scritto, e **non ci si mette un numero plausibile** | **fatto** |
| **E3** | ✅ **FATTO 2026-09-19** — [`core/data_checks.py`](../core/data_checks.py): monotonia, duplicati, barre/anno, copertura comune + **partenze scaglionate**, **file piu' completo** (il nome cablato che ignora l'export nuovo), **% di fill non ottenibili** (aggancia E6 al codice) e **% di gap oltre lo stop**. `checklist_dati(...)` / `checklist_esecuzione(...)` ritornano un `Esito` stampabile; `python -m core.data_checks <csv>` da riga di comando. ⚙️ Gli 8 test in `core/tests/test_data_checks.py` **non testano funzioni, riproducono gli incidenti**: cumsum invertito, `XAU_spot_M5.csv` accanto a `_ext.csv`, **46,1%** di fill fantasma, **12,7%** di gap, bond dal 2016 accanto a FX dal 2012 — e uno verifica che su dati puliti **non gridi** | **fatto** |
| **E5** | ✅ **FATTO 2026-09-17** — `core/resolve_trade.py` con le **5 convenzioni come parametri** (`fill_bar_can_resolve`, `tie`, `gap_beyond_stop`, `be_priority`, `on_timeout`) e **equivalenza dimostrata** con le 4 implementazioni storiche in `core/tests/test_resolve_trade.py`. Il test ha scoperto da solo l'asse `be_priority` (ORB valutava il BE **dopo** SL/TP). Gia' usata da `fade_obtainable.py`, `latency_gate.py`, `continuation_obtainable.py` | — |
| **E6** | ✅ **FATTO 2026-09-19** — la regola del **fill ottenibile** ora esiste in quattro posti che la fanno rispettare: [`QUANT_REVIEW_PROTOCOL.md` **Step 3bis**](QUANT_REVIEW_PROTOCOL.md) (gate bloccante *prima* delle metriche, con le 3 domande, le 4 varianti SKIP/LIMIT/RECENTER/LIVE e i **5 campanelli**), il guardiano [`quant-gatekeeper.md` **Checklist 3.0**](../.claude/agents/quant-gatekeeper.md) (+ requisito **G1.9**, riga obbligatoria `ESECUZIONE` nell'output, e nella `description` del routing), [`STRATEGY_LIFECYCLE.md §6a.1`](STRATEGY_LIFECYCLE.md) (look-ahead **di prezzo** accanto a quello di informazione) e i red flag di [`quant_reviewer.md`](../agents/quant_reviewer.md). ⚠️ Scritto anche il lato che si dimentica: il fantasma **non ha un segno** — mancando la misura non c'e' verdetto **ne' GO ne' NO-GO** | **fatto** |
| **E4** | ✅ **CHIUSO 2026-09-19** — era scritto **in un posto solo** (guardiano, checklist 5), e una regola che si applica solo se passi di li' non e' una regola. Ora sta anche in [`STRATEGY_LIFECYCLE.md §8`](STRATEGY_LIFECYCLE.md) e in [`QUANT_REVIEW_PROTOCOL.md` Step 2](QUANT_REVIEW_PROTOCOL.md) (tabella: quali provenienze valgono come predizione indipendente), ed e' diventato un **campo verificabile**: `provenienza_ipotesi` in [`trial_ledger.json`](trial_ledger.json), controllato da `python -m core.trial_ledger`. ⚠️ Il controllo ha subito trovato **due famiglie senza provenienza dichiarata** (`meanrev_vol`, `london_breakout`): annotazione finche' restano chiuse, **bloccante** se qualcuno propone di riaprirle. Cutoff in vigore: **2026-05-31** |

---

## G — DATI MANCANTI (da aggiungere al repo, anche a pagamento)

> **Ricostruita il 2026-09-28 dal repo.** Matteo ci stava lavorando in sessioni poi chiuse, e quella
> lista non era stata salvata su file: **aggiungere qui cio' che si ricorda**.
>
> **Regola per comprare** (estesa da DECISIONS 2026-06-02, *"acquisto dati rimandato finche' il livello
> gratis non supera il gate"*): un dato a pagamento si compra solo se sblocca un test **pre-registrabile**
> con **MDE calcolato prima** che stia sotto l'effetto atteso
> ([[feedback_potenza_prima_di_raccogliere]]). Prima si esaurisce la versione gratuita dello stesso dato.
> Costi: nessuna cifra senza fonte e data — dove manca, "da verificare".

| # | dato | cosa sblocca | fonte candidata | costo | stato |
|---|---|---|---|---|---|
| **G1** | **Tick XAU/USD BID/ASK** (e M1) | (a) Gump: esecuzione e uscite senza pareggi ([pre-reg](FOREXGUMP_LATENCY_PREREGISTRATION.md) §4). (b) ⚠️ **Mentore XAU: la forbice di 0,82R** fra convenzione pessimistica e ottimistica del baseline casuale, che per DECISIONS 2026-09-18 (2) *"si stringe solo con dati M1/tick"* — cioe' la parte d'ignoranza piu' grande del nostro unico edge | Dukascopy (`dukascopy_python`, gia' installato) | **gratis** | 🟡 M1 BID/ASK 2020-09 → 2026-09 **scaricato** il 28/09 (`XAU_duka_M1_{bid,ask}.parquet`); tick da scaricare nelle finestre dei segnali. (b) non ancora rifatto |
| **G2** | **Spread e fill reali del broker** dei conti copiati | Gump: bias dello spread (§8.7 pre-reg: Dukascopy 0,58-0,69 $ nel 2025-26 = ~0,3R su SL 2 $); copier XAU: taratura del gate su fill veri (C5) | storico MT5 dei conti demo del socio (Report) | gratis | ⏳ in raccolta: la demo live continua (DECISIONS 2026-09-28) |
| **G3** | **Export Telegram di Gump piu' vecchio** + accesso alla repo `gold-desk-trading-suite` | cancellazioni e messaggi modificati (D3 della pre-reg): unico modo di misurarli dal passato; codice del copier e della webapp del socio | socio | gratis | ⏳ da chiedere |
| **G4** | **Serie VIX** | D5 (regime da VIX) | FRED `VIXCLS` / CBOE | gratis | non scaricata: vale solo se A1 si riapre |
| **G5** | **Posizionamento sui futures** | D7 (riflessivita' / affollamento) | CFTC Commitments of Traders (settimanale) | gratis | non valutato. Open interest intraday e short interest: a pagamento, costo da verificare |
| **G6** | **Fondamentali point-in-time senza survivorship** + **sorprese sugli utili** | D3 (PEAD / episodic pivot); selezione titoli (Stock Selector, archiviato) | Sharadar SF1 / Norgate (DECISIONS 2026-06-02); `financialdatasets.ai` ([data/README](../data/README.md)) | a pagamento, da verificare | rimandato per decisione del 2026-06-02; l'unico setup del funnel con supporto accademico indipendente e' PEAD (D3) |
| **G7** | **Tick + book (order flow)** | D1 (assorbimento, delta, big trade) | feed di borsa a livello di book | a pagamento, da verificare | ⛔ il backlog dice *"mai, realisticamente"*: il vantaggio e' di latenza, non di dato |
| **G8** | **Small cap USA**: float, short interest, halt, locate | D2 | provider dedicati + broker con locate | a pagamento, da verificare | ⛔ fuori perimetro |
| **G9** | **Strumenti indipendenti ad alta volatilita'** per A1 punto 2 | riapertura di A1 ([referto](TREND_A1_HELDOUT_POWER.md) §7) | — | **non si compra** | ⚠️ in lista per non comprarlo: il limite e' l'**universo** (19 crypto valgono 1,4 strumenti), non il fornitore |

**Il piu' conveniente adesso:** G1 (b). E' gratis, i dati sono gia' in casa, e restringe l'incertezza
proprio sull'unico binario con un verdetto positivo.

---

## Collegamenti

- [`STRATEGY_LIFECYCLE.md`](STRATEGY_LIFECYCLE.md) — gate, budget, verdetti
- [`QUANT_REVIEW_PROTOCOL.md`](QUANT_REVIEW_PROTOCOL.md) — gli 8 step della review
- [`../.claude/agents/quant-gatekeeper.md`](../.claude/agents/quant-gatekeeper.md) — il guardiano del protocollo
- [`../fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/SINTESI.md`](../fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/SINTESI.md) — da dove vengono B1-B6

---

## F — Il caso ORB: **CHIUSO 2026-08-27 in F1** (aperto 2026-08-23)

> ✅ **Esito.** L'utente ha **spento l'EA** il 2026-08-27 (verificato: zero posizioni, zero
> pendenti, ultimo ordine 25/08). Quanto segue resta come **motivazione registrata** della scelta e,
> soprattutto, come **condizioni di riapertura** — l'unica porta d'ingresso se un giorno si
> riproponesse.

**I fatti, verificati.**

| | |
|---|---|
| verdetto | **NO-GO** (2026-07-16): 14,5 anni Dukascopy M5, NAS100 **−0,056** [−0,11; 0,00] e SPX500 **−0,137** [−0,19; −0,08]. Entrambi i lati negativi, quasi tutti gli anni rossi |
| iterazioni v2 | filtro news, ADX: **stesso verdetto** |
| holdout | **gia' aperto** — e ha smascherato il "miglioramento" v2 come non-stazionario |
| forward | ⚠️ **esisteva** (EA `orb_nasdaq`, magic 26052, 22 ordini, 10 chiusi dal 31/07) — la mia affermazione del 23/08 era sbagliata: avevo cercato le prove nel repo invece che in **MT5**. **Spento dall'utente il 2026-08-27** |

**Come si e' creata la contraddizione.** La voce DECISIONS del 2026-08-14 concludeva: *"sposta il
prior e rafforza la scelta di lasciar correre il forward ORB, unico modo di risolverlo"*. Era una
**decisione**, non una descrizione — ma non e' mai stata implementata, e da allora e' stata citata
come se lo fosse (in questo backlog e nella discussione del 22-23/08). **L'errore e' mio**, ed e'
la ragione per cui il debito **E2** (contatore/stato persistente) non e' un dettaglio: non esiste
un posto dove lo stato reale di un binario sia registrato e verificabile.

**Cosa dice il 14/08 che spesso viene letto male.** Il test trend/playground ha trovato lo stesso
salto "pre/post-2020" **col segno opposto** su una strategia scorrelata. La conclusione fu che due
breakout della stessa famiglia che si spezzano in direzioni opposte alla stessa data sono piu'
coerenti con **due estrazioni di rumore** che con una rottura di microstruttura. ⚠️ **Quella e'
gia' una risposta alla domanda che il forward avrebbe dovuto risolvere**, ottenuta a costo zero.

**Le due ipotesi economiche arrivate dal funnel** (Cimbali, C4.6 · Siento, E.1) sono **aneddoti
senza campione**, quindi per `STRATEGY_LIFECYCLE §7` **non sono evidenza esterna nuova** e non
autorizzano a riaprire.

### La scelta, che e' dell'utente

| opzione | cosa comporta | costo |
|---|---|---|
| **F1 — lasciare chiuso** (raccomandata) | si registra che il forward non serviva: il 14/08 aveva gia' risposto. Le due ipotesi si archiviano come **condizioni di riapertura** gia' scritte, cosi' la prossima volta che qualcuno dice *"l'ORB funziona per via del gamma"* la risposta e' pronta | zero |
| **F2 — implementare il forward davvero** | rendere `today.py` persistente e farlo girare. ⚠️ E' un forward su una famiglia **NO-GO con holdout gia' bruciato**: raccoglie dati su qualcosa che abbiamo deciso non funziona, e la domanda che doveva risolvere ha gia' una risposta piu' economica | lavoro reale + un binario in piu' da presidiare |

### Se un giorno si riaprisse: le condizioni, scritte ORA

Le due ipotesi fanno **predizioni diverse**, ed e' questo che le rende utili — non la narrativa.
Vanno valutate su dati **mai visti**, non sul campione 2012-2026 gia' esaurito.

| | **Cimbali** — flusso strutturale d'acquisto + market maker che forniscono liquidita' | **Siento** — copertura gamma obbligata delle 0DTE |
|---|---|---|
| lato | **bias long** (il flusso strutturale e' di acquisto) | **simmetrico** (dipende dal posizionamento in opzioni) |
| epoca | effetto **stabile da ~20 anni**, quindi anche **pre-2020** | effetto **assente prima del 2021** (le 0DTE nascono li') |
| ora | nessuna preferenza dichiarata | **concentrato nelle prime ore** (opera solo le prime due) |
| calendario | nessuna dipendenza | **degrada dove non ci sono 0DTE**: triple witching (terzo venerdi' di mar/giu/set/dic), dove lui **non opera** |

⚠️ **Due avvertenze che vanno lette insieme alla tabella.**
1. Il nostro dato storico dice che l'ORB era **negativo pre-2020** — il che e' incompatibile con
   Cimbali e superficialmente compatibile con Siento. **Non conta come conferma**: e' un dato
   gia' visto, e il 14/08 ha mostrato che quello stesso split appare col segno opposto altrove.
2. Il meccanismo di Siento, preso alla lettera, **non predice che l'ORB funzioni**: predice che il
   prezzo venga attirato ai muri di gamma e li' **si inverta**. L'ORB e' una strategia di
   **continuazione**. Il suo meccanismo semmai spiegherebbe perche' l'ORB **fallisce** quando un
   muro sta davanti al target — cioe' e' piu' un argomento contro che a favore.
