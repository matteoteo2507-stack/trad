# Backlog di ricerca — stato al 2026-08-27 (sera)

> Inventario di tutto ciò che è sul tavolo dopo la chiusura del funnel YouTube, diviso per **cosa
> si può effettivamente farci oggi**. Non è un piano: è la base per decidere quali binari aprire.
>
> Ordine dei bucket: **A** ha un numero da confermare · **B** ha una specifica meccanica completa e
> dati per testarla · **C** migliora qualcosa che già gira · **D** non ha un percorso di test oggi.
> **H** (dal 2026-10-08): le strade uscite dalla ricerca sugli indicatori tecnici, classificate negli stessi bucket.
>
> **Vincoli di budget in vigore** — da tenere presenti in ogni decisione:
> pre-registrazioni da fonte esterna **2-3 per trimestre** (quante ne restano: `python -m core.trial_ledger`) · max **3 round di rifinitura**
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

> ~~Tutte e sei si eseguono sul feed Dukascopy D1, 27 strumenti; nessuna richiede dati che non abbiamo.~~
> ⚠️ **Corretto il 2026-09-29** (quant-gatekeeper): il feed D1 ha **30** strumenti (`_coverage.csv`), e
> **B5 richiede un profilo di volume intraday** che non abbiamo in forma utile.
>
> **Classificazione del 2026-09-29** (quant-gatekeeper, parere di contabilita', 0 trial): decisione
> dell'utente = *"le voci B non si parcheggiano: si affrontano gli ultimi trial di cui dispongono"*. Il
> parere dice **quali trial esistono davvero**: B2 = 1 (esclusivo con A1), B5 = 0, B6 = 0 sull'universo
> gia' testato. Decisioni aperte in fondo alla sezione.

| # | spec | fonte | perché è pronta | costo |
|---|---|---|---|---|
| **B1** | **Mean reversion Kichev** — ✅ **CHIUSA 2026-09-17**. La fonte dice solo *"price deviates significantly far from mean, exit 1-4 days"*: `SMA5` e la soglia **erano nostri**. Misura sulle **code** contro nullo matched (ri-allineamento circolare, 300 perm.): **3 gruppi su 8** confermano, soglia dichiarata prima era **5**. Il nullo non e' piatto ma **bimodale**: energy/index/fx_cross ritornano alla media, **crypto (−0,25) e agri continuano**. ⚠️ Inseguire i 3 che confermano = eleggere un vincitore dalla mappa dopo averla vista. Vedi [DECISIONS 17/09 (6)](../DECISIONS.md) | **0 trial spesi** |
| **B2** | ✅ **CHIUSA 2026-10-03 a 0 trial (strada A)** — non testabile a potenza utile nell'universo della fonte, **non** falsificata; round 3 conservato alla famiglia, riapertura scritta in [DECISIONS 03/10](../DECISIONS.md). _(storico:)_ 🔜 **ROUND 3 ASSEGNATO 2026-09-30** (DECISIONS 30/09). ⚠️ **Potenza (30/09, 0 trial): con X = 5 sotto potenza in ogni universo; potenza sufficiente solo con X = 2 su tutti e 27 gli strumenti, che includono FX e indici esclusi dalla fonte** → [referto](B2_KICHEV_POTENZA.md), decisione dell'utente fra A (chiudere a 0 trial, raccomandata), B, C. **Breakout Kichev** — range della barra ≥ ~2× media range ultime 5 → entra in direzione; uscita **a tempo (2-5 giorni)** o quando il momentum svanisce | Kichev (D.1) | stessa cosa: completa e senza giudizio. ⚠️ Famiglia trend/momentum: **round 2 di 3 già speso** | ~~1 pre-reg + 1 round~~ → **29/09: round 3 di 3 di `trend_momentum`, ESCLUSIVO con A1 punto 3** (stessa fonte, stessi dati: una famiglia nuova ricaricherebbe il budget). Se B2 fallisce la famiglia chiude per budget e con lei **A1 (LEAD → CLOSED) e D4**. 1 slot esterno. ⚠️ **Non e' "completa e senza giudizio"**: la trascrizione dice *"your sixth candle will move by 2%"* (esempio, non soglia) e *"you have to do your research"* sull'uscita → range/movimento, soglia, direzione, X e universo sono **scelte nostre** da dichiarare, una sola primaria. ⚠️ Con i CSV grezzi i trigger sono **7.825**, col loader che fonde il weekend **4.000**: obbligatorio `analysis/trend/backtest.py`. **Passo 0 a 0 trial: MDE** (stima estrapolata da B3: ~0,07 ATR a h=2 sull'aggregato, ~0,10 sull'universo della fonte) contro l'effetto minimo economico. Esito massimo LEAD (dati gia' visti da B1/B3) |
| **B3** | **Condizione di struttura sull'estensione estrema** — ✅ **CHIUSA 2026-09-21, 0 trial spesi**. Protocollo scritto prima ([B3_EXTENSION_STRUCTURE_PROTOCOL.md](B3_EXTENSION_STRUCTURE_PROTOCOL.md) · [motore](../analysis/extension/structure.py)): 1.733 eventi a `E>=3 ATR`, baseline random matched su strumento/direzione/anno/orizzonte. **H1 NO** (cella attesa **+0,007** [−0,145;+0,168], MDE 0,221), **H2 non valutabile**. ⚠️ Il risultato non e' un nullo debole: **le celle non esistono**. Normalizzando sull'ATR, a L=2-3 il **97,0%** e **93,6%** degli eventi ha gia' il range in espansione — e' **aritmetica** (3 ATR in 2 barre impongono barre da 1,5 ATR). La distinzione delle fonti vive di soglie in **percentuale** su strumenti a volatilita' eterogenea: normalizzata, **svanisce**. Il gate volume esclude 10 strumenti su 27 (corr volume/|rendimento| fra −0,03 e 0,14) e sono proprio **agri, bond, crypto, energy, metal**. Breadth **4/8**, e il segno piu' forte e' **crypto +0,248 = continuazione**, opposto all'ipotesi (coerente con B1). Non falsifica le fonti sul **loro** universo: dice che la condizione **non e' trasferibile** | **0 trial** |
| **B4** | **Variante di esecuzione del FADE: conferma sì / conferma no** — ⏸️ **DECADUTA 2026-09-19**: la famiglia FADE e' **KILL dal 17/09** (§A2), quindi non esiste piu' un lead su cui fare una variante di esecuzione. Misurata coi fill ottenibili la famiglia vale **−0,250R**, e l'audit A5 ha mostrato che **anche il lato opposto perde** (−0,118R): il livello non contiene informazione, non e' l'entrata a essere sbagliata. Si riaprirebbe solo alle condizioni di §A2 | **0 — decaduta** |
| **B5** | ➡️ **SPOSTATA IN D8 il 2026-09-30** (DECISIONS 30/09). **Casella vuota: low volume node** — detector LVN accanto a POC/VAH/VAL | Carmine, Fabio, Yush (3 fonti) | verificato nel codice: `analysis/level_research/detectors.py` testa i nodi ad **alto** volume, mai quelli a **basso**. È l'ipotesi **complementare, meccanismo opposto**. ⚠️ Costa poco tecnicamente **ed è proprio questo il rischio**: cella aggiunta a una griglia con **384 trial di NULL**, molteplicità pagata dove non l'abbiamo contata. E tutte e tre le fonti la usano **con conferma di flusso**, che non possiamo replicare → testeremmo una versione amputata | ~~1 pre-reg esterna~~ → **29/09: 0 trial, 0 slot.** E' una cella della famiglia `livelli` (CLOSED, 384 trial, 3 round su 3); tre trader senza campione non sono evidenza §7. Test **amputato** (le fonti entrano solo con conferma di flusso), volume tick-proxy, e Carmine dice che *"il FVG e' un LVN"*: il FVG e' gia' nullo (0/16). Stato onesto proposto: **"non falsificabile coi nostri dati" → bucket D**, non "falsificata". Riapertura: volume vero intraday da borsa (fonte dati nuova §7), o risultato pubblicato con campione |
| **B6** | ✅ **CHIUSA 2026-09-30, 0 trial** (decisione dell'utente: la via §7 sulle commodities non si prende; riapertura solo con evidenza §7). **Casella vuota: trend line inclinate** | Crooks, Silfrain, Tori (3 pro) — **Ariel contro** | i 384 trial erano **solo orizzontali**. Buco reale. ⚠️ Prior basso: 1 fonte su 4 le rifiuta **con la nostra stessa motivazione** (ambiguità del tracciamento) | ~~1 pre-reg esterna~~ → **29/09: 0 trial sull'universo gia' testato.** Va divisa: **B6a rimbalzo sulla retta** = `livelli`; **B6b rottura come cancello** = breakout, `trend_momentum` (in concorrenza per lo stesso round 3), adiacente al FADE (KILL). **Unica via legittima: §7 punto 2, classe di strumenti nuova** — l'universo livelli non conteneva commodities industriali, energia e agri, che Dukascopy ha (XPT, COPPER, WTI, BRENT, NATGAS, agri) e che Tori opera. Sarebbe una **riapertura di `livelli`** su quella classe, con **holdout vero sigillabile**, 1 slot, DSR sul cumulato ≥385, tracciamento in **due convenzioni** (stoppini/chiusure) con concordanza richiesta (l'obiezione di Ariel, misurata). MDE prima, a 0 trial |
| **B7** | **Copier mentore: uscita a 1R invece che a TP1** — ✅ **CHIUSA 2026-09-18, 0 trial spesi**. L'ipotesi era **gia' misurata e non me n'ero accorto**: la "win-rate simmetrica (+1R prima di −1R)", metrica **primaria** della pre-reg di agosto, **e'** l'uscita a 1R. Confronto appaiato su n=627: TP1 **+0,1247** [+0,0737; +0,1712] contro 1R **+0,1246** [+0,0480; +0,2011], differenza **−0,0001** BCa95 **[−0,0633; +0,0596]** — identiche, e 1R porta **+58% di sd** a parita' di rendimento, quindi **peggiore**. ⚠️ Cadeva anche la premessa: "+0,294 di vantaggio contro +0,127 incassato" confrontava **punti di win-rate con R**. In R il vantaggio e' **+0,597** a TP1 e **+0,588** a 1R: lo stesso. Vedi [§10](MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md) | **0 trial** |

---

**Decisioni sul bucket B — ✅ prese il 30/09** (DECISIONS 2026-09-30): 1 → B2; 2 → nel ledger; 3 → da fissare nella pre-registrazione di B2; 4 → si' (D8); 5 → B6 chiusa; 6 → resta debito di protocollo. Testo originale delle domande:
1. Il **round 3 di `trend_momentum`** va a **B2** o resta riservato ad **A1 punto 3**? Sono esclusivi; se B2 fallisce chiude anche A1 e D4.
2. B2 dentro `trend_momentum` (parere del gatekeeper), o un razionale **indipendente** scritto che ne faccia una famiglia a se'.
3. **Universo primario di B2**: quello della fonte (commodities + crypto, con regola sulla crypto) o tutti e 30.
4. **B5 nel bucket D** con le condizioni di riapertura.
5. **B6**: chiudere, o **riaprire `livelli` via §7 sulla classe commodities** (Q1-2027 nella sequenza proposta).
6. Il §7 non dice se una riapertura **rinnova i round** della famiglia: va deciso prima di usarlo (debito di protocollo).

Sequenza proposta dal gatekeeper: nessuna approvazione nel Q3 (nessuna bozza pronta; usare lo slot per non perderlo sarebbe pressione); Q4 slot 1 = Gump se passa la G1 #2; passo di potenza di B2 a 0 trial; Q4 slot 2 = B2 se la potenza regge e il round gli viene assegnato; Q1-2027 = B6 via §7, se scelta.

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
| **D7** | **Riflessività / affollamento come misura** | servono open interest, positioning, short interest | dati non disponibili sul nostro perimetro. ➡️ **03/10**: col COT in casa (G5) e' arrivata un'ipotesi con fonte, il **premio di copertura** sulle commodity → passo di potenza a 0 trial: [COT_PRESSIONE_POTENZA.md](COT_PRESSIONE_POTENZA.md) → ✅ **chiusa a 0 trial** (DECISIONS 2026-10-03 (3)): non testabile a potenza utile, non operabile alla nostra scala |
| **D8** | **Low volume node (ex B5)** | classificata il 2026-09-30 "non falsificabile coi nostri dati": cella della famiglia `livelli` (CLOSED), test amputato senza flusso, volume tick-proxy; per la fonte "il FVG e' un LVN" e il FVG e' gia' nullo | volume vero intraday da borsa (fonte dati nuova, §7), oppure un risultato pubblicato con campione |
| **D9** | **Acquisti degli insider** (SEC Form 4; idea di Matteo, 24/10; con il contesto geopolitico e' il primo caso del ponte con l'hub) | i Form 4 sono gratuiti, ma servono i prezzi delle **azioni singole USA senza survivorship** (G6) e le azioni singole sono fuori perimetro (§H, chiuse in partenza); classe 3 (reazione lenta a un deposito pubblico), letteratura nota a Claude non letta (quarantena). La componente geopolitica e' rimandata all'hub: il registro delle previsioni non ha ancora una misura (scheda d'ingresso, [LIFECYCLE](STRATEGY_LIFECYCLE.md) §8). [Intake del 25/10](reviews/idee_matteo_hub_intake_2026-10-25.md) | universo azionario USA nel perimetro (decisione di Matteo) + dati G6 + uno strumento per eseguire su azioni singole |

---

## H — STRADE DALLA RICERCA SUGLI INDICATORI TECNICI (2026-10-08)

> Fonte: [10_indicatori_tecnici](../fondamenti_tecnici/10_indicatori_tecnici/principles.md) (ricerca di Claude e di
> Comet, 08/10). Ogni strada e' passata per la griglia del [09_fonti_di_vantaggio](../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md)
> §4 (classe → chi paga → limite all'arbitraggio → dove si vede → accessibilita' → potenza → dove muore → provenienza)
> e per la regola **stessa grandezza = stessa famiglia** (DECISIONS 2026-10-08 (3)). **Un trial speso** (H1, 12/10).
>
> **Esito onesto:** la ricerca produce **una strada vera** (H1), tre bloccate dalle nostre stesse regole (H2 dopo la
> chiusura del candidato A, H3, H4), una nota di metodo (H5) e uno strumento di preparazione (H6). Tutto il resto e'
> chiuso in partenza, con il motivo, in fondo alla sezione.
>
> **Aggiornamento 12/10:** H1 e' stata testata ed e' **CLOSED** (DECISIONS 2026-10-12 (2)). La sezione non ha piu'
> strade vive; restano le due voci senza costo (H5, divergenza Hudson-Urquhart) e H6.

| # | strada | grandezza → famiglia | classe e chi paga | bucket | primo passo | costo |
|---|---|---|---|---|---|---|
| **H1** | **Momentum dell'ultima mezz'ora** (coperture di gamma) | rendimento intraday gia' fatto, parente dell'ORB: **famiglia nuova `momentum_ultima_mezzora`** (Matteo, 09/10: meccanismo indipendente), con parentela dichiarata e senza holdout sui dati dell'ORB | **2**: chi e' corto di gamma (market maker di opzioni, ETF a leva) deve comprare quando sale e vendere quando scende, a ridosso della chiusura | ❌ **CLOSED il 12/10** al train, holdout mai aperto ([pre-registrazione](ULTIMA_MEZZORA_PREREGISTRATION.md) §10, DECISIONS 2026-10-12 (2)) | nessuno: riapre solo per §7 | 1 trial speso, terzo slot esterno del 2026-Q4 |
| **H2** | **Inversione di breve condizionata alla turbolenza** (VIX) | spostamento dalla media → **`mr_indici_rsi2`** (candidato A), non famiglia nuova | **2-3**: chi chiede immediatezza paga chi fornisce liquidita'; il compenso sale col VIX (Nagel 2012) | **D**: A e' **CLOSED per potenza** (DECISIONS 2026-10-08 (4)), nessun round residuo | nessuno | — |
| **H3** | **Accelerazione dopo l'attraversamento di un numero tondo** (stop appena oltre, Osler 2003) | livelli → `livelli` e `round_grid`, **CLOSED** | **5**: chi ha lo stop appena oltre il tondo; vince chi arriva prima | **D** | nessuno | — |
| **H4** | **Pitchfork / median line** (e ogni livello disegnato a mano) | livelli inclinati → `livelli` e **B6**, **CLOSED** | nessuna: e' un pattern | **D** | misurare il socio, non lo strumento (proposta B) | — |
| **H5** | **Tendenza: baseline "media storica"** (Huang et al. 2020) e pista *Boundaries of TSMOM* | tendenza → `trend_momentum` (LEAD, round 3 disponibile) | 3 / 1 (da confermare) | nota per **A1** + **D** | acquisire il paper *Boundaries* | 0 |
| **H6** | **Analizzatori del codice Pine** (ridisegno, look-ahead) | — (preparazione) | — | **C** (quando arriva il codice del socio) | valutare licenza e cosa eseguono | 0 |

### H1 — Momentum dell'ultima mezz'ora: la scheda

**Fonte, letta sul testo** (Baltussen, Da, Lammers, Martens, *Journal of Financial Economics* 142, 377-403, 2021,
PDF dal sito di uno degli autori; livello T del modulo 10). Su oltre 60 futures (azioni, obbligazioni, materie prime, valute),
dicembre 1974 - maggio 2020, il rendimento dalla chiusura di ieri a mezz'ora dalla chiusura di oggi predice quello
dell'ultima mezz'ora. Sui futures azionari (Tab. 6, portafoglio 1/N) la strategia "lungo se il giorno e' positivo, corto se
negativo, solo nell'ultima mezz'ora" rende **+6,86% annuo**, deviazione **3,96%**, Sharpe **1,73**, giorni giusti **55%**;
il confronto "sempre lungo nell'ultima mezz'ora" fa **+0,44%**, Sharpe 0,11. Effetto simile nei sottocampioni 1974-1999 e
2000-2020 (Tab. 5). **Senza costi**: gli autori scrivono che con un tick di costo sui futures S&P lo Sharpe netto resta
positivo (p. 386). Conferma indipendente sull'ETF S&P 500 1993-2013: Gao, Han, Li, Zhou 2018 (livello S).

**Perche' e' l'unica strada vera.** E' l'unico risultato della ricerca con un **"chi paga" misurato** (Tab. 9 e Fig. 4
legano l'effetto alla quota di mercato degli ETF a leva; §4 alla posizione in gamma dei market maker), su **molti mercati**,
in una **classe che non abbiamo mai guardato** (flussi forzati, [09](../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md) §3).

**Le domande aperte, in ordine** (ci si ferma alla prima che chiude):

1. **Famiglia.** Con la regola di oggi il segnale (rendimento intraday gia' fatto) ha la grandezza dell'ORB, CLOSED con
   holdout aperto. Due letture: (a) **riapertura di `opening_range` via §7**, punto 3 (risultato pubblicato), con i trial
   che si sommano a quelli dell'ORB; (b) famiglia nuova con razionale indipendente (flusso di chiusura contro asta
   d'apertura), che pero' ricarica il budget. **Raccomandata (a)**; decide Matteo col parere di contabilita' del gatekeeper.
   ✅ **Deciso il 09/10: (b), famiglia nuova** (DECISIONS 2026-10-09), con due condizioni: parentela dichiarata e niente
   holdout sui dati gia' attraversati dall'ORB.
2. **Accessibilita'** (va fatta per prima: e' quella che ha chiuso COT e carry). Effetto lordo a spanne: 6,86% / ~252
   giorni ≈ **2,7 punti base per operazione**, cioe' circa **2 punti di US500** e **8 di NAS100** ai prezzi di luglio 2026
   dei nostri dati. Va confrontato con lo **spread di US500 e US100 nelle barre 15:30 e 16:00 ET**, dall'export MT5
   (`<SPREAD>`, come fa `prop-lab`). Se lo spread si mangia la meta' del lordo, la strada chiude qui. ⚠️ L'ORB e il London
   breakout sono morti proprio sui costi dell'intraday sugli indici.
   ✅ **Fatto il 09/10, sotto la soglia**: misurato dai tick (non dalle barre) sul demo FP Markets, 159 giorni; il costo
   e' una frazione piccola del lordo su entrambi gli indici. Numeri e limiti (conto demo, slittamento e commissione non
   misurati) nel [referto](ULTIMA_MEZZORA_FATTIBILITA.md).
3. **Dati puliti.** Il campione del paper finisce a maggio 2020: da giugno 2020 e' fuori campione per la fonte. Ma i nostri
   NAS100 e SPX500 M5 2012-2026 sono gia' stati visti dall'ORB. Finestra davvero pulita: **strumenti mai usati dall'ORB**
   (altri indici o futures da Dukascopy, oro M1 gia' in casa, con la chiusura del future di riferimento) oppure un
   **forward**. Controlli obbligatori: fuso e **ora legale** (la chiusura delle 16:00 ET cambia ora in UTC due volte
   l'anno), copertura delle barre nella finestra, `core/data_checks.py` ([[feedback_verifica_i_dati_prima]]).
   ✅ **Fatto il 09/10**: i dati reggono, con quattro condizioni per la G1 (fuso MT5 verificato giorno per giorno perche'
   il server FP Markets non ha uno scarto fisso; calendario con chiusure anticipate; l'oro M1 e' l'unico strumento in casa
   pulito rispetto sia alla fonte sia all'ORB; CFD contro futures). Dettaglio nel [referto](ULTIMA_MEZZORA_FATTIBILITA.md).
4. **Potenza** (stima a spanne di Claude, 08/10, da rifare in un referto come [MR_INDICI_POTENZA](MR_INDICI_POTENZA.md)).
   Dalla Tab. 6: media ~2,7 pb e deviazione ~25 pb al giorno (3,96% / √252). Con il fattore 2,80 (alfa 5%, potenza 80%)
   servono **~660 giorni** a effetto pieno e **~2.600** a effetto dimezzato; da giugno 2020 a luglio 2026 ce ne sono
   **~1.500**. ⚠️ I numeri del paper sono un portafoglio di piu' indici: su un indice solo la deviazione e' piu' alta e i
   giorni necessari di piu'. Probabile esito: **potenza sufficiente solo se l'effetto non si e' dimezzato**.
   ✅ **Fatto il 09/10** ([referto](ULTIMA_MEZZORA_FATTIBILITA.md), passo 4): confermato per gli indici USA con la metrica
   di solo segno (SPX e NAS valgono **un solo strumento**); l'oro **non** puo' fare da holdout (il suo effetto pubblicato e'
   ~15 volte piu' debole); un **indice europeo** da 06/2020 darebbe un holdout con potenza, ma va scaricato.
5. **Slot.** Sarebbe la **terza** pre-registrazione esterna del 2026-Q4, con la soglia di allarme gia' raggiunta
   (`python -m core.trial_ledger`): Q1-2027 oppure una decisione esplicita di Matteo.
   ✅ **Deciso l'11/10 da Matteo: adesso**, terzo slot del 2026-Q4. Con questo il trimestre e' pieno.

**Dove muore — il meccanismo, non il pattern.** Tre predizioni che il flusso fa e il rumore no:
- l'effetto **si inverte nei giorni successivi** (lo dice l'abstract): se non si inverte, non e' un flusso di copertura;
- e' **piu' forte nei giorni con rendimento grande**, perche' il ribilanciamento degli ETF a leva cresce col rendimento del
  giorno (da verificare nel §4.2 del paper);
- **dopo il 2021 puo' essere cambiato di segno**: con le opzioni a scadenza giornaliera (0DTE) i market maker possono essere
  **lunghi** di gamma, e allora il prezzo viene trattenuto invece che spinto. E' il meccanismo di Siento gia' discusso nel
  caso ORB (§F). La finestra pulita **e'** l'era 0DTE: il test distingue le due storie.

**Disegno minimo, da fissare alla G1:** segnale = segno del rendimento fino alle 15:30 ET; posizione solo 15:30-16:00 ET;
baseline primaria **"sempre lungo nell'ultima mezz'ora"** (Tab. 6) piu' segno casuale; esecuzione a prezzo ottenibile
(apertura della barra delle 15:30, mai la chiusura della barra del segnale: Step 3bis).

### H2-H6 — le altre, in breve

- **H2.** Il condizionamento al VIX ha una fonte (Nagel 2012, rendimenti attesi e Sharpe dell'inversione di breve che salgono
  con la turbolenza) e il dato gratis gia' in casa (G4). Ma e' la stessa grandezza del candidato A, quindi **non e' una
  famiglia**: poteva essere solo un round di rifinitura di `mr_indici_rsi2`. ✅ **Aggiornata la sera dell'08/10**: A e'
  **CLOSED per potenza**, NON DIMOSTRATO, 1 trial su 1 e nessun round previsto (DECISIONS 2026-10-08 (4)), quindi H2 resta
  possibile **solo come riapertura §7**. Nagel non basta come chiave: misura le **azioni singole**, non contraddice il nostro
  null sugli indici. **Si sblocca se** esce un risultato pubblicato contro un ingresso casuale a durata copiata, su indici e
  dati indipendenti (le condizioni di riapertura di A). Collegata a D5.
- **H3.** Il nostro null sui numeri tondi misura la **reazione**; Osler predice anche l'**accelerazione** dopo
  l'attraversamento, che non abbiamo misurato. Ma Osler documenta **ordini**, non un rendimento: per §7 non "contraddice il
  nostro null", quindi **non riapre** `livelli` ne' `round_grid`. In piu' e' classe 5 (velocita'), quasi sempre persa per un
  retail su CFD. **Si sblocca se** arriva un risultato pubblicato con un rendimento misurato dopo il 2010.
- **H4.** Nessuno studio, nessun repository e nessun post confronta la pitchfork con linee casuali (ricerca 08/10). Senza
  evidenza esterna, §7 non permette di riaprire `livelli` ne' B6 (linee inclinate, chiusa il 30/09): **non e' testabile come
  regola per i nostri criteri**. La strada aperta e' misurare **la persona**: il track record prospettico del socio
  (proposta B, parcheggiata finche' non torna a operare).
- **H5.** Huang et al. 2020: la strategia di tendenza guadagna quasi quanto una che usa solo la **media storica** di ogni
  asset. E' coerente col diagnostico A1 (il vantaggio era il tempo in mercato, DECISIONS 2026-09-21). **Regola per il round 3
  di `trend_momentum`**, se mai si apre: oltre all'ingresso casuale a parita' di tempo in mercato, la baseline "media
  storica". Pista da acquisire (oggi solo da X): *Boundaries of Time Series Momentum* (Suominen, Hjalmarsson), secondo cui la
  tendenza si rompe agli estremi di valutazione; servirebbero dati di valutazione mensili che non abbiamo → D.
- **H6.** `edgeless-ai/pinescript-mcp`, `MoDarK-MK/PineScript-Skill` (controllo statico di ridisegno e look-ahead) e
  `PyneSys/pynecore` (Pine → Python). **Catalogati, non installati**: si valutano (licenza, cosa eseguono, se leggono
  credenziali) solo quando arriva uno script del socio, al passo 2 dello smistamento ([10](../fondamenti_tecnici/10_indicatori_tecnici/principles.md) §10).

### Chiuse in partenza (nessun lavoro previsto)

| cosa | perche' | si riapre se |
|---|---|---|
| oscillatori classici (RSI 14, Stocastico, CCI, Williams %R, MACD) come famiglie a se' | stessa grandezza di famiglie esistenti (regola del 08/10) | mai come famiglia nuova |
| Fibonacci | refutato fuori (Tsinaslanidis et al. 2022: non batte livelli casuali) e dentro (NXT, livelli) | — |
| Elliott, Gann, armonici | non falsificabili | — |
| pattern a candela | nessuna capacita' predittiva al bootstrap (Marshall, Young, Rose 2006) | — |
| Volume Profile, POC, VWAP come zone | 0 celle su 48 (DECISIONS 2026-07-07) | volume vero intraday (vedi D8) |
| regole tecniche sul forex | vantaggi a tratti, non consistenti (Zarrabi 2017, Neely 2009) | — |
| regole tecniche sulle criptovalute | fuori perimetro; divergenza aperta su Bitcoin fuori campione (modulo 10 §3) | se la traccia crypto si riattiva |
| massimo a 52 settimane, media mobile su azioni ad alta volatilita', OBV per il premio mensile | azioni singole o orizzonte mensile: fuori perimetro | universo azionario (D2, D3, G6) |
| gestione per volatilita' come segnale | e' rischio, non direzione; non batte sistematicamente fuori campione (Cederburg 2020); libreria O1-O4 fissa | decisione esplicita di allargare la libreria degli overlay |

### Sequenza proposta (dall'obiettivo all'indietro)

Obiettivo: un vantaggio con un "chi paga" **dentro il nostro perimetro**. L'unico candidato e' H1, e il suo collo di
bottiglia sono **i passi 1 e 2**: famiglia e spread. Costano poco e decidono se H1 vive. Tutto il resto o aspetta
(H6 aspetta il codice del socio) o non ha lavoro (H2, H3, H4, H5).

1. ✅ **H1 passo 2 — spread MT5 nella finestra**: fatto il 09/10, sotto la soglia, H1 resta aperta.
2. ✅ **H1 passo 1 — famiglia**: nuova, decisione di Matteo del 09/10.
3. ✅ **H1 passi 3-4 — dati e potenza** (09/10).
4. **Prima della G1**: ✅ indici europei per l'holdout scaricati e verificati l'11/10 (DAX, Euro Stoxx 50, FTSE 100:
   [referto](ULTIMA_MEZZORA_FATTIBILITA.md)), sigillati; resta da fissare la metrica primaria (regressione o posizione
   proporzionale, contro solo segno): ✅ proporzionale con tetto (Matteo, 11/10).
5. ✅ **H1 passo 5 — slot**: adesso, terzo slot del 2026-Q4 (Matteo, 11/10).
6. ✅ **H1 — pre-registrazione, due passate G1, approvazione, train** (11-12/10): **CLOSED**, holdout mai aperto
   (DECISIONS 2026-10-12 (2)). H1 non ha altro lavoro.
7. In parallelo, senza costo: acquisire *Boundaries of TSMOM* (H5) e chiudere la divergenza su Hudson-Urquhart (modulo 10 §3).

---

## E — DEBITO DI PROTOCOLLO — ✅ E1-E6 **estinte il 2026-09-19**; ⚠️ **E7 aperta** (debito emerso dai test di ottobre)

> **E7 — debito emerso dopo il 19/09, aperto.** Non e' copiato qui: l'elenco sta nei due referti.
> - Candidato A, 08/10 ([referto](reviews/rsi2_indici_esito_2026-10-08.md) §8): controllo dei trade sovrapposti
>   nell'overlay, unita' del runs test, NON DIMOSTRATO assente dalla tassonomia di LIFECYCLE §5.
> - H1, 12/10 ([G2](reviews/ultima_mezzora_G2_2026-10-12.md) §6 e §8): nessun percorso per un'ipotesi nata dai
>   descrittivi di un test chiuso; il §7 non dice come si contabilizza una riapertura ne' se un holdout mai aperto si
>   eredita; nessuna regola sul forward di una famiglia CLOSED; descrittivi stampati senza incertezza e senza
>   correzione per il numero di celle; ripetizione sui semi sul limite che non decide; `core/` e `tests/` fuori dai
>   percorsi congelati; nessun controllo positivo sui dati reali quando l'esito possibile e' un CLOSED; bozza e
>   passate G1 fuori da git fino all'approvazione.
>
> **Sono decisioni di Matteo**, non correzioni tecniche: cambiano cosa il protocollo permette. Due proposte in
> discussione dal 12/10: (1) pre-registrare come varianti dichiarate prima le condizioni che la fonte stessa prevede;
> (2) una sola prova di conferma su dati mai aperti per un'ipotesi nata da un descrittivo.

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
| **E6** | ✅ **FATTO 2026-09-19** — la regola del **fill ottenibile** ora esiste in quattro posti che la fanno rispettare: [`QUANT_REVIEW_PROTOCOL.md` **Step 3bis**](QUANT_REVIEW_PROTOCOL.md) (gate bloccante *prima* delle metriche, con le 3 domande, le 4 varianti SKIP/LIMIT/RECENTER/LIVE e i **5 campanelli**), il guardiano [`quant-gatekeeper.md` **Checklist 3.0**](../.claude/agents/quant-gatekeeper.md) (+ requisito **G1.9**, riga obbligatoria `ESECUZIONE` nell'output, e nella `description` del routing), [`STRATEGY_LIFECYCLE.md §6a.1`](STRATEGY_LIFECYCLE.md) (look-ahead **di prezzo** accanto a quello di informazione) e i red flag di `quant_reviewer.md` (ritirato il 2026-10-13: la regola resta negli altri tre posti). ⚠️ Scritto anche il lato che si dimentica: il fantasma **non ha un segno** — mancando la misura non c'e' verdetto **ne' GO ne' NO-GO** | **fatto** |
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
| **G1** | **Tick XAU/USD BID/ASK** (e M1) | (a) Gump: esecuzione e uscite senza pareggi ([pre-reg](FOREXGUMP_LATENCY_PREREGISTRATION.md) §4). (b) ⚠️ **Mentore XAU: la forbice di 0,82R** fra convenzione pessimistica e ottimistica del baseline casuale, che per DECISIONS 2026-09-18 (2) *"si stringe solo con dati M1/tick"* — cioe' la parte d'ignoranza piu' grande del nostro unico edge | Dukascopy (`dukascopy_python`, gia' installato) | **gratis** | 🟡 M1 BID/ASK 2020-09 → 2026-09 **scaricato** il 28/09 (`XAU_duka_M1_{bid,ask}.parquet`); tick nelle finestre dei segnali **scaricati** il 02/10 (2.573 ore); (a) **usato** nel test unico di Gump (02/10, CLOSED il 05/10). (b) non ancora rifatto |
| **G2** | **Spread e fill reali del broker** dei conti copiati | Gump: bias dello spread (§8.7 pre-reg: Dukascopy 0,58-0,69 $ nel 2025-26 = ~0,3R su SL 2 $); copier XAU: taratura del gate su fill veri (C5) | storico MT5 dei conti demo del socio (Report) | gratis | ⏳ in raccolta: la demo live continua (DECISIONS 2026-09-28) |
| **G3** | **Export Telegram di Gump piu' vecchio** + accesso alla repo `gold-desk-trading-suite` | cancellazioni e messaggi modificati (D3 della pre-reg): unico modo di misurarli dal passato; codice del copier e della webapp del socio | socio | gratis | ⏳ da chiedere |
| **G4** | **Serie VIX** | D5 (regime da VIX) | CBOE `VIX_History.csv` (dal 1990) / FRED `VIXCLS`; dollaro: FRED `DTWEXBGS` (dal 2006) | gratis, download diretto ([ricerca GitHub 29/09](reviews/ricerca_github_2026-09-29.md)) | ✅ **scaricata il 2026-10-03** (`python data/scarica_serie_libere.py` → `data/cache/free/VIX_D1.csv`, 1990-01-02 → 2026-10-02, unico buco anomalo = chiusura post 11/09/2001). FRED non risponde da questa macchina: per il dollaro c'e' `USDX` sul broker MT5. Nessuna ipotesi pre-registrata: e' un dato, non un test |
| **G5** | **Posizionamento sui futures** | D7 (riflessivita' / affollamento) | CFTC Commitments of Traders (settimanale) | **gratis**: Legacy dal 1986, Disaggregated dal 2009 ([ricerca 29/09](reviews/ricerca_X_dati_oro_2026-09-29.md)) | ✅ **scaricato il 2026-10-03** (stesso script → `data/cache/free/cot_{legacy,disagg}_fut.parquet`: Legacy 1986-01-15 → 2026-09-29, 957 mercati; Disaggregated 2006-06-13 → 2026-09-29, 657 mercati). Ipotesi con fonte arrivata il 03/10 (premio di copertura): vedi riga D7. Open interest intraday e short interest: a pagamento, costo da verificare |
| **G6** | **Fondamentali point-in-time senza survivorship** + **sorprese sugli utili** | D3 (PEAD / episodic pivot); selezione titoli (Stock Selector, archiviato) | Sharadar SF1 / Norgate (DECISIONS 2026-06-02); `financialdatasets.ai` ([data/README](../data/README.md)) | Sharadar SF1 uso personale **$39/mese** (tutta la storia, dal 1998); Norgate azioni senza survivorship **$630/anno** (letti 29/09, [ricerca 29/09](reviews/ricerca_X_dati_oro_2026-09-29.md)) | ⛔ **il socio non li ha** (03/10); a pagamento non deciso. rimandato per decisione del 2026-06-02; l'unico setup del funnel con supporto accademico indipendente e' PEAD (D3) |
| **G7** | **Tick + book (order flow)** | D1 (assorbimento, delta, big trade) | feed di borsa a livello di book (es. Databento: CME dal 2010, da $0,50/GB, $125 di crediti gratis; il book L2/L3 solo 1 mese sui piani base — [ricerca 29/09](reviews/ricerca_X_dati_oro_2026-09-29.md)) | a consumo; la tariffa per schema **non e' pubblica** (Comet, 30/09: serve l'estimatore del portale, dopo registrazione) | ⛔ il backlog dice *"mai, realisticamente"*: il vantaggio e' di latenza, non di dato |
| **G8** | **Small cap USA**: float, short interest, halt, locate | D2 | provider dedicati + broker con locate | a pagamento, da verificare | ⛔ fuori perimetro |
| **G9** | **Feed con piu' classi ad alta volatilita' e storia lunga**: futures su commodity minori, singole azioni ad alta volatilita', volatilita' implicita | riapertura di A1: e' la **prima condizione** scritta nel [referto](TREND_A1_HELDOUT_POWER.md) §7 (servono 7,3-29,3 strumenti **indipendenti** per braccio, oggi 3,4) | Pinnacle CLC (98 commodity, dal 1969) · Norgate futures (~100 mercati, dal 1980) | **Pinnacle $99** una tantum (+$20/mese aggiornamenti) · **Norgate $270/anno** (letti 29/09, [ricerca 29/09](reviews/ricerca_X_dati_oro_2026-09-29.md)) | 🟡 **contato gratis il 2026-10-03** → [referto A1 §8](TREND_A1_HELDOUT_POWER.md): il broker FP Markets non ha storia (solo operabilita'); con futures pysystemtrade + crypto (+ azioni) il braccio ALTA passa da 3,4 a **7,8-10,9** strumenti indipendenti: basta per lo scenario ottimistico, **non** per quello onesto (×2,7-3,8). ⏸️ **Non acquistato** (DECISIONS 03/10). _(storico:)_ da valutare: **costa poco**, quindi il vincolo non e' il prezzo ma la condizione sotto. Comet (30/09): CSI Data cita un piano da **$99/anno** senza listino per pacchetto; FirstRate mostra il prezzo solo al checkout; Tick Data solo su preventivo. **Il conteggio si puo' fare gratis prima di comprare**: 252 futures continui di pysystemtrade (fermi al 2024-03) + censimento Dukascopy da dukascopy-node ([ricerca GitHub 29/09](reviews/ricerca_github_2026-09-29.md)). ⚠️ Non basta **piu' ticker dello stesso tipo**: le 19 crypto libere valgono 1,4 strumenti (ρ +0,698). Prima di comprare: contare quanti strumenti **indipendenti** ad alta vol aggiunge il feed. *(Corretta il 29/09: la prima versione diceva "non si compra", in contrasto col §7)* |

**Il piu' conveniente adesso:** ⚠️ *Superato.* Era G1 (b), ma lo storico del mentore e' selezionato dalle
cancellazioni del canale (DECISIONS 2026-10-02, notte) e il forward su cui rimisurarlo non parte (DECISIONS
2026-10-13 (2)): stringere la forbice su quello storico non darebbe un numero citabile.

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
