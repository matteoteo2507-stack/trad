# DECISIONS — Decisioni già prese (decision log)

> **Perché questo file esiste.** Per non riallucinare scelte già chiuse né ricostruire
> analisi già fatte. Prima di proporre "costruiamo X" o "riattiviamo Y", **controlla qui**.
> Le decisioni si cambiano **con dati nuovi**, non con sensazioni — e quando cambiano, si
> aggiorna questo file con una nuova voce (non si riscrive la storia).
>
> Formato: ogni voce = *data · decisione · razionale · link*. Ordine: dal più recente.
> Questo file rispecchia nel repo le decisioni che vivono anche nella memoria di lavoro
> (`~/.claude/projects/.../memory/`), così sono visibili sfogliando il workspace e su GitHub.

---

## 2026-09-21 (3) — **B3 chiusa a 0 trial.** La condizione di struttura non è trasferibile, e il motivo è aritmetico

**Cosa è stato fatto.** Prossimo punto operativo del backlog dopo lo stop di A1: **B3**, l'unica
voce aperta che non costa budget (B2 spenderebbe l'ultimo round del ramo trend, B5 e B6 una
pre-registrazione esterna, e ne resta una sola nel trimestre). Protocollo — soglie, celle,
direzione attesa e significato di un mancato rifiuto — scritto **prima** di misurare:
[docs/B3_EXTENSION_STRUCTURE_PROTOCOL.md](docs/B3_EXTENSION_STRUCTURE_PROTOCOL.md).
Motore: [analysis/extension/structure.py](analysis/extension/structure.py). **Costo: 0 trial.**

**L'oggetto.** Non *"l'estensione estrema si inverte"* — lo dicono in cinque ed è infalsificabile
così. Ma **quale** estensione: Marius (C3.4) e Kyle (C3.5), indipendenti e su mercati diversi,
convergono su *"poche candele grandi con volume in espansione"*, scartando le **"formiche"**
(tante candeline) e il volume calante.

### Esito: H1 NO, H2 non valutabile

1.733 eventi a `E ≥ 3 ATR` su 27 strumenti, baseline random matched su strumento, direzione, anno
**e orizzonte** (durata identica per costruzione: il confonditore trovato su A1 non si presenta).

| | n | differenza vs random | BCa95 | MDE |
|---|---|---|---|---|
| tutti gli eventi, h=2 (primario) | 1.733 | **+0,011** | [−0,061; +0,090] | **0,106** |
| **cella attesa** range+ / vol+ | 517 | **+0,007** | [−0,145; +0,168] | 0,221 |
| range+ / vol− | 126 | +0,011 | [−0,218; +0,224] | 0,323 |

Nessun orizzonte (1, 2, 3, 5) si distingue dal random. Le due celle misurabili danno **lo stesso
numero**: la gamba volume non separa niente. Robustezza sulla soglia: `E≥2,0` +0,041 → `E≥4,0`
+0,001, **monotona verso zero al crescere dell'estensione** — il contrario di quanto prevede
l'ipotesi.

### Il risultato vero: le celle non esistono, e non per mancanza di campione

| L | n | range **+** | range **−** |
|---|---|---|---|
| 2 | 236 | **97,0%** | 1,3% |
| 3 | 450 | **93,6%** | 1,3% |
| 5 | 513 | 59,5% | 9,9% |

**È aritmetica.** Un'estensione di 3 ATR in 2 barre impone barre da ≥1,5 ATR; il range è almeno
quanto il movimento, quindi il range **è già in espansione per costruzione**. Normalizzando la
soglia sulla volatilità, *"estensione estrema"* e *"candele grandi"* diventano **la stessa cosa**,
e le "formiche" scendono all'1,3% degli eventi.

> La distinzione delle fonti vive di soglie in **percentuale** applicate a strumenti con
> volatilità molto diversa: lì un +200% può arrivare in venti candeline. **Non è che non riusciamo
> a misurarla: su un universo normalizzato non è una distinzione.**

### Il gate sul volume esclude proprio gli strumenti che servivano

Dichiarato prima (zeri <5%, `corr(volume, |rendimento|)` ≥0,15, mediana ≥10): **17 strumenti su 27
passano**. Non passano COCOA, COTTON, SUGAR, SOYBEAN (corr da −0,03 a −0,00), BTCUSD (0,02),
ETHUSD (0,05), NATGAS (**20,6% di barre a volume zero**), BRENT, COPPER, UKGILT. Sono **agri,
bond, crypto, energy, metal**: l'estremo ad alta volatilità, dove il fenomeno dovrebbe esserci.
La gamba volume resta testabile solo su un sottoinsieme dominato dall'FX. ⚠️ È la seconda volta in
due giorni che il vincolo mordente è la **composizione dell'universo**, non il metodo.

### Breadth: moneta, e il segno più forte è quello sbagliato

**4 gruppi su 8** vanno nella direzione attesa. Il valore più grande è **crypto +0,248**, cioè
**continuazione** — l'opposto della predizione, sullo strumento dove il fenomeno dovrebbe essere
più forte. Coerente con la misura indipendente di B1 (17/09): crypto **continua**, non ritorna.

### Formulazione del verdetto

Come imponeva §6 del protocollo: le fonti **non sono falsificate sul loro universo**. Operano
small/mid cap USA con float ristretto, squeeze, halt e locate — meccanismi che su CFD e FX non
esistono. Il test dice che la condizione **non è trasferibile**, per una ragione **strutturale**
(normalizzazione) e non statistica.

**Riaprirebbe la casella**: un universo dove volatilità e dimensione della candela si separano
davvero (azionario con normalizzazione su market cap = bucket D2, bloccato per dati) e **volume
vero**, non tick volume di CFD. ⚠️ **Non** è condizione di riapertura inseguire il +0,248 della
crypto: segno opposto all'ipotesi, non pre-registrato, un gruppo su otto visto **dopo** la tabella.

**Contabilità invariata**: 0 trial, round trend 2 di 3, pre-registrazioni esterne 2 di 2-3.
Restano aperte **B2, B5, B6** — tutte e tre costano budget, quindi sono decisioni dell'utente.

---

## 2026-09-21 (2) — **A1 punto 2: il test held-out non è finanziabile con i dati che esistono.** Fuori scala da 2,1× a 19,6×

**Cosa è stato fatto.** Secondo dei tre passi concordati, eseguito perché il punto 1 era passato.
Calcolo di **potenza** + **inventario degli strumenti disponibili**, entrambi *prima* di aprire
qualunque pre-registrazione. Referto: [docs/TREND_A1_HELDOUT_POWER.md](docs/TREND_A1_HELDOUT_POWER.md).
Motori: [power_two_groups.py](analysis/trend/power_two_groups.py) e
[heldout_pool.py](analysis/trend/heldout_pool.py). **Costo: 0 trial.**

**Esito: la condizione NON è rispettata.** Il punto 3 non si apre.

### Quanti strumenti servono

Unità di inferenza = lo **strumento**, non il trade: è lo strumento che si tiene fuori, e i trade
dentro uno strumento condividono la serie. Misurato: ICC 0,011–0,022 con cluster da 43 trade →
design effect **1,5–1,9**, cioè i 1.169 trade raccolti valgono **791** trade indipendenti.
Contarli per trade darebbe 246/588 per braccio: comodo e sbagliato.

| effetto ipotizzato | durata appaiata | durata fissa 20g |
|---|---|---|
| osservato +0,61 / +0,65 R (ottimistico) | **7,3** | **16,7** |
| **dimezzato** (winner's curse) | **29,3** | **66,8** |

### Quanti ce ne sono davvero

Dukascopy espone 1.380 strumenti, quasi tutti azioni. Fuori dall'azionario restano **liberi**:
58 cross FX, 20 indici, 19 crypto, 1 agricolo, 1 energia. Bond, FX major e metalli **esauriti**.
Disponibilità **verificata scaricando** (18 su 19; XMRUSD non ha dati).

Ma i ticker non sono informazione. Con ρ **misurato** sui rendimenti D1:

| insieme | ρ medio | liberi | **valgono** |
|---|---|---|---|
| **crypto** | **+0,698** | 19 | **1,40** |
| indici | **+0,791** | 20 | 1,25 |
| cross FX | +0,050 | 58 | 15,07 |

E la volatilità dice dove finiscono: **nessun cross FX raggiunge il 20%** (il massimo è USDZAR a
13,0%); DAX 17,8%, N225 19,7%, DJIND 16,5% stanno **sotto** la soglia. Capacità effettiva del
braccio ad **alta volatilità: 3,4 strumenti** nuovi indipendenti (crypto 1,40 + agri 1,00 +
energia 1,00), contro 16,3 del braccio basso — e la stima è **generosa**, perché somma categorie
diverse come se fossero indipendenti.

| scenario | servono | ALTA ha | esito |
|---|---|---|---|
| appaiata, effetto osservato | 7,3 | 3,4 | **fuori scala 2,1×** |
| fissa 20g, effetto osservato | 16,7 | 3,4 | 4,9× |
| appaiata, effetto dimezzato | 29,3 | 3,4 | 8,6× |
| fissa 20g, effetto dimezzato | 66,8 | 3,4 | **19,6×** |

### Perché non è un problema di dati, ma di struttura del mercato

**L'estremo alto della volatilità è una sola classe di attivi.** Le 19 crypto libere si muovono
insieme e portano 1,4 strumenti di informazione. Un confronto a due bracci costruito su quel pool
non misurerebbe *"alta contro bassa volatilità"*: misurerebbe **"crypto contro cross FX"** — una
differenza di classe di attivi, e per giunta sulla classe che è **l'unica positiva nel campione di
scoperta**. Sarebbe circolare **per costruzione**.

**Le tre vie d'uscita che sembrano disponibili e non lo sono**: (a) abbassare la soglia fa entrare
strumenti meno volatili → **riduce Δ** e alza il fabbisogno; (b) una regressione continua è più
efficiente di uno split ma resta dominata dai ~3 punti indipendenti sopra il 20%; (c) allungare la
finestra all'indietro non aiuta, la crypto non esiste prima del 2017.

### Decisione

**Il punto 3 non si apre**, e il terzo round del ramo trend **non si spende**. Condizioni di
riapertura scritte ora (§7 del referto): una fonte dati con **più classi ad alta volatilità** e
storia lunga; un effetto più grande misurato da un disegno diverso; oppure il **forward**, che non
consuma holdout — ma a **4,8 trade per strumento-anno** arrivare a ~30 strumenti indipendenti per
braccio è questione di anni.

⚠️ **Non** è condizione di riapertura scegliere la crypto perché è l'unica casella positiva: dopo
aver visto la tabella, è eleggere un vincitore dalla mappa.

**Contabilità invariata**: 0 trial, round trend **2 di 3**, pre-registrazioni esterne 2 di 2-3.
Sottoprodotto riutilizzabile: 18 serie D1 nuove in
`analysis/trading-bot-eval/data/dukascopy_d1/_pool_candidati/`.

---

## 2026-09-21 — **A1, diagnostico di durata**: il gradiente regge, ma a parità di tempo in mercato la regola **perde dal random**

**Cosa è stato fatto.** Primo dei tre passi concordati sul playground (A1). Protocollo e soglie
scritti **prima** di eseguire: [docs/TREND_DURATION_DIAGNOSTIC.md](docs/TREND_DURATION_DIAGNOSTIC.md).
Motore: [analysis/trend/duration_diagnostic.py](analysis/trend/duration_diagnostic.py).
**Costo: 0 trial** — verifica dell'integrità di un confronto già fatto, non una regola nuova.

**Da dove nasce.** Il 19/09 `check_matching` (primitiva nuova, debito E1) ha mostrato che i due
bracci del confronto **non stanno in mercato per lo stesso tempo**: holding mediano **7 giorni
contro 2**. Il controllo C1 di `q2_checks.py`, quello che doveva neutralizzare il canale
meccanico, era costruito proprio su quella differenza.

### Esito 1 — il gradiente SOPRAVVIVE, ed è più netto di prima

| | rho(vol, differenza) | rho(vol, E[R] del random) |
|---|---|---|
| **come oggi** (durata non appaiata) | +0,786 p=0,0135 | **+0,619** p=0,062 |
| **durata appaiata** al trade reale | **+0,929** p=0,0009 | **+0,048** p=0,46 |
| **durata fissa** 20g (E3, già pre-registrata) | **+0,881** p=0,0041 | +0,429 p=0,15 |

Il braccio random mostrava da solo un gradiente di **+0,619**: era la spiegazione meccanica da
battere. A durata controllata **crolla a +0,048**. Il gradiente non è la normalizzazione in unità
di ATR e non è il tempo in mercato. Due controlli indipendenti, stesso segno.

### Esito 2 — ma il livello si ribalta, ed è la cosa più importante

| confronto | reale | random | divario | BCa95 |
|---|---|---|---|---|
| come oggi | +0,037 | +0,118 | −0,081 | [−0,215 ; **+0,071**] — contiene lo zero |
| **durata appaiata** | +0,037 | +0,275 | **−0,238** | [−0,363 ; −0,098] |
| **durata fissa 20g** | +0,135 | +0,587 | **−0,451** | [−0,661 ; −0,219] |

A parità di tempo in mercato, **un'entrata casuale dello stesso lato e dello stesso anno batte il
breakout Donchian**: in aggregato, con CI che escludono lo zero, e con differenza positiva su
**1 gruppo su 8** a durata fissa (solo crypto). Il vantaggio che la regola sembrava avere era
**tempo in mercato**, non scelta del momento: il trail teneva le posizioni aperte quasi il doppio
del controllo, e in un mercato con deriva il tempo paga. Tolto quello, dell'entrata resta un costo.

⚠️ Non è "assenza di prova": è una misura positiva con segno sfavorevole.

### Il dettaglio che cambia la lettura del primario

`rho(holding, E[R])` sui gruppi = **+0,976** (p=0,0001), più forte del primario `rho(vol, E[R])`
= +0,857. Al netto della durata, la parziale `vol → E[R]` scende a **+0,525** (p=0,12, non
rilevato). ⚠️ Ma volatilità e durata sono **collineari** (+0,810): con n=8 **non sono separabili**,
quindi questa riga da sola non decide — è per questo che il protocollo aveva dichiarato *prima* il
confronto controllato come test decisivo, e non la parziale.

### Limiti dichiarati

1. **La durata appaiata condiziona su un esito**: `rho(hold, E1)` sui singoli trade = **+0,836**,
   quindi il controllo riceve un orizzonte più lungo proprio quando il reale ha funzionato. Per
   questo esiste D3b a **durata fissa decisa prima**, che non è esposta all'obiezione e dà lo
   stesso segno, più forte.
2. **n = 8 resta n = 8**: partenze scaglionate (bond dal 2016-17), **nessun holdout sigillato** —
   lacuna dichiarata nella pre-registrazione originale, non scoperta dopo.
3. Il lato è **ereditato** dal trade reale: il confronto misura *quando* entrare, non *se* essere
   long o short. Resta valido il controllo C2: solo **3/8** gruppi positivi su entrambi i lati.

### Conseguenza per la decisione (punto 3, che è dell'utente)

A1 non si chiude qui, ma **cambia oggetto**: non più *"più volatile = più edge"* bensì *"più
volatile = l'entrata danneggia meno"*. Una pre-registrazione su strumenti held-out dovrebbe
misurare la **differenza contro random a durata controllata** (è il grezzo che conteneva il canale
meccanico) e dichiarare come ipotesi un **divario negativo che si attenua**, non un edge positivo.
⚠️ Inseguire l'unica casella positiva (crypto) dopo aver visto questa tabella sarebbe **eleggere un
vincitore dalla mappa**, e costerebbe il terzo e ultimo round del ramo trend.

**Contabilità invariata**: 0 trial spesi, round trend fermo a 2 di 3, pre-registrazioni esterne
ferme a 2 di 2-3 nel trimestre.

---

## 2026-09-19 — **Debito di protocollo ESTINTO** (E1-E6). Le regole erano prosa; ora sono codice che blocca

**Decisione.** Chiuse tutte e sei le voci del bucket E di
[docs/BACKLOG_RICERCA.md](docs/BACKLOG_RICERCA.md). Non e' ricerca e non consuma trial: e' la
differenza fra avere un protocollo e **avere un protocollo che si applica da solo**.

**Il problema, detto una volta sola.** Ogni voce del guardiano nasce da un errore realmente
accaduto qui — e **ogni errore e' accaduto dopo che la voce era stata scritta**. Una regola che
funziona solo se qualcuno si ricorda di applicarla non e' una regola: e' un auspicio. Le sei voci
avevano tutte la stessa forma, non sei forme diverse.

### Cosa esiste adesso

| debito | cosa e' stato costruito | cosa impedisce |
|---|---|---|
| **E6** | [`QUANT_REVIEW_PROTOCOL.md` **Step 3bis**](docs/QUANT_REVIEW_PROTOCOL.md), gate **bloccante prima delle metriche** + Checklist 3.0 del guardiano + `LIFECYCLE §6a.1` + red flag del reviewer | un verdetto su **fill non ottenibili** |
| **E1** | [`core/random_baseline.py`](core/random_baseline.py) (`BarSampler`, `PoolSampler`, `check_matching`, `gap_ci`) | baseline riscritto a mano, matching mai verificato, CI i.i.d. su controlli non indipendenti |
| **E3** | [`core/data_checks.py`](core/data_checks.py) | monotonia, duplicati, barre/anno, partenze scaglionate, **file corto accanto a quello lungo**, % di fill fantasma, gap oltre lo stop |
| **E2** | [`core/trial_ledger.py`](core/trial_ledger.py) + [`docs/trial_ledger.json`](docs/trial_ledger.json) | contatore trial tenuto a memoria, budget sforati in silenzio |
| **E4** | campo `provenienza_ipotesi` nel registro + `LIFECYCLE §8` + `PROTOCOL` Step 2 | contaminazione da knowledge cutoff scritta **in un posto solo** |
| **E5** | `core/resolve_trade.py` (gia' fatto il 17/09) | 5 convenzioni d'uscita implicite in 4 copie |

### La prova che la primitiva non e' una primitiva in piu'

E' la stessa pretesa di E5: **equivalenza bit-identica** con le implementazioni storiche, o non
serve a niente. `core/tests/test_random_baseline.py` ricopia il campionamento di `analysis/nxt/stops.py`,
`analysis/nxt/excursion.py`, `analysis/trend/backtest.py` e `analysis/level_research/engine.py`
e verifica che escano **gli stessi identici indici**. `analysis/trend/backtest.py` e' stato migrato:
**output identico riga per riga**, tranne il nuovo blocco di verifica.

`core/tests/test_data_checks.py` non testa funzioni: **riproduce gli incidenti**. Il `cumsum`
invertito del 14/08, `XAU_spot_M5.csv` accanto a `_ext.csv`, il **46,1%** di fill fantasma del FADE,
il **12,7%** di gap oltre lo stop, i bond dal 2016 accanto a FX dal 2012 — piu' un test che verifica
che su dati puliti **non gridi**, perche' un guardiano che segnala sempre smette di essere letto.

### Quattro cose che i controlli hanno trovato appena accesi

Nessuna era nota. E' il motivo per cui il debito andava pagato adesso e non "quando serve".

1. **Il playground (A1) confronta reale e random a durate diverse**: holding mediano **7 giorni
   contro 2** (−71%). Il divario *reale vs random* e' quindi **in parte un confronto fra durate**.
   Coerente con la regola (un'entrata casuale con trailing SMA10 viene troncata subito), ma **va
   dichiarato nella pre-registrazione**: e' una riserva sul lead vivo, non una sua refutazione.
   Tutti gli altri assi — asset, lato, anno, numerosita' — risultano matchati.
2. **La "stessa durata di holding" della checklist non e' matchabile.** Con le stesse regole
   d'uscita la durata e' un **esito**, non un input. Si matcha la **regola**, si **verifica** la
   durata, e se diverge si dichiara. La riga della tabella del guardiano e' stata corretta.
3. **Il CI i.i.d. sui controlli random e' il 28% piu' stretto** di quello a cluster sull'evento,
   misurato sui dati sintetici del test. Gli `m` controlli di uno stesso evento condividono strato,
   lato e rischio: un CI che li tratta da indipendenti e' **finto**.
4. **Tre famiglie hanno il contatore trial non ricostruibile** (`opening_range`, `trend_momentum`,
   `london_breakout`) e **due la provenienza dell'ipotesi non dichiarata** (`meanrev_vol`,
   `london_breakout`). Nel registro valgono `null`, non un numero plausibile: per il DSR di quelle
   famiglie si applica Bailey-LdP (100 × N_params) **e lo si dichiara**.

### La regola di futilita' e' diventata un numero

`python -m core.trial_ledger --futilita 250`. Su 250 osservazioni servono Sharpe **1,65** con 1
trial, **3,12** con 8, **4,64** con i **384** della ricerca livelli — cioe' arrivati a v3 nessun
risultato raggiungibile avrebbe potuto essere significativo, e il libro andava chiuso a v2. E' un
**pavimento gaussiano**: con skew negativo o code grasse la soglia sale.

### Cosa NON e' stato fatto, e perche'

I motori storici (`analysis/nxt/*`, `analysis/level_research/*`, `analysis/round_grid/*`) **non**
sono stati migrati alla primitiva. Sono il **registro** di verdetti gia' emessi: riscriverli non
cambia un numero e introdurrebbe rischio su risultati che non si possono piu' verificare contro
nulla. La primitiva e' obbligatoria per i test **nuovi**, ed e' il guardiano a farla rispettare.

**Costo: 0 trial.** Nessuna ipotesi aperta, nessuna chiusa, nessun budget toccato. Budget FADE
fermo a 2 di 3, pre-registrazioni esterne ferme a 2 di 2-3 nel trimestre.

---

## 2026-09-18 (5) — **A5: audit dei verdetti early-stage.** Nessuno era sbagliato; due dicevano **meno** di quello che gli abbiamo fatto dire

Protocollo scritto e committato **prima** di aprire i motori
([EARLY_STAGE_AUDIT_PROTOCOL.md](docs/EARLY_STAGE_AUDIT_PROTOCOL.md)), referto completo in
[EARLY_STAGE_AUDIT_REPORT.md](docs/EARLY_STAGE_AUDIT_REPORT.md). **0 trial spesi.**

### L'asimmetria da cui e' partito

Sono quasi tutti **NO-GO**, e questo ribalta quale difetto e' pericoloso. Un difetto che **gonfia**
(look-ahead, fill fantasma) rende il NO-GO piu' difficile: se non passa nonostante il regalo, il
verdetto regge a maggior ragione. Il difetto pericoloso e' quello che **deprime** il risultato o che
**toglie potenza** — ed e' invisibile, perche' un numero peggiore sembra prudenza. Un NO-GO falso
non si autocorregge mai: la strategia non esiste piu' e non genera dati che lo contraddicano.

### Il risultato

**Nessun verdetto era sbagliato. Il difetto sistematico sta nel passaggio dal test al verdetto.**
Le review tecniche sono oneste — scrivono *"non distinguibile dal caso"*, *"INSUFFICIENT DATA"*. In
DECISIONS e in memoria diventano *"NO-GO pulito"*, *"null"*, *"l'edge non esiste"*. **Su quelle
formulazioni compresse abbiamo poi costruito il bilancio del pivot.**

| famiglia | esito | cosa cambia |
|---|---|---|
| **Livelli** (384 trial) | ✅ CONFERMATO, **piu' solido** del dichiarato | niente; CI larghi **meno di 1 punto** su base 30% |
| **NXT continuazione** | ✅ CONFERMATO, **numero sbagliato** | E[R] vero **−0,118**, non −0,444 |
| **ORB** | 🟡 MISTO | SPX500 refutato · **NAS100 mai misurato** |
| **TSMOM** | ⚠️ **NON MISURATO** | MDE Sharpe **0,59** contro un atteso di **0,3-0,5** |

### NXT: il difetto c'era, valeva 0,326R, il verdetto regge lo stesso

Fade e continuazione entrano allo **stesso livello**: il fade **vende**, la continuazione **compra**.
Il fill fantasma **regala** un prezzo migliore a chi vende e **impone** un prezzo peggiore a chi
compra — cioe' poteva **aver prodotto lui** il NO-GO della continuazione.

Rimisurata con i soli fill ottenibili (`analysis/nxt/continuation_obtainable.py`): da **−0,444**
[−0,470 ; −0,417] a **−0,118** [−0,161 ; −0,076]. **Tre quarti dell'effetto erano artefatto.** Ma
l'intervallo esclude lo zero in entrambe le convenzioni, **0/6** strumenti e **2/15** anni positivi.

🔧 **Il fatto che vale piu' del verdetto**: misurate onestamente **entrambe le direzioni dello
stesso ingresso perdono** — fade **−0,250**, continuazione **−0,118**. Non e' un edge col segno
sbagliato: e' **un livello che non contiene informazione**, piu' costi. E' la stessa conclusione dei
384 trial sui livelli, raggiunta da una strada indipendente.

### ORB: una mia ipotesi refutata, e un buco vero

Sospettavo che il verdetto dipendesse dalla convenzione intrabar (il motore calcola `R_pess` e
`R_opt` ma stampa solo la pessimistica). **Misurata: forbice +0,001R.** Ipotesi mia, sbagliata — con
RR 1:3 e stop ampio le barre ambigue sono rare.

Il buco vero e' la **potenza**. NAS100: **ogni** intervallo contiene lo zero e arriva a **+0,078** /
**+0,203**, territorio tradabile; MDE **0,135R**. SPX500 TRAIN '12-'19 e' invece **genuinamente
negativo**: −0,267 [−0,391 ; −0,121]. E il criterio pre-registrato era *"E[R] > 0 con lower bound >
0"*, che puo' produrre solo "dimostrato" / "non dimostrato" — e il "non dimostrato" e' diventato
*"anche il filone scalping single-asset e' null"*, generalizzando da **uno strumento su due**.

### TSMOM: il test non poteva vedere quello che cercava

Sharpe +0,21, BCa95 [−0,18 ; +0,59] → NO-GO per regola. Ma la review **cita nella stessa pagina**
l'atteso a priori: **Sharpe 0,3-0,5**. Con `SE(SR) ≈ sqrt((1+SR²/2)/T)` e T=23 anni, l'**MDE e'
Sharpe 0,59**: per rilevare 0,4 servivano **53 anni**, 2,3× quelli disponibili; per 0,3 ne servivano
91. **L'intervallo osservato contiene per intero la fascia attesa.**

Stessa forma del difetto che il 17/09 ha smontato il "secondo test" del FADE (fuori scala 40×):
una giustificazione plausibile, mai tradotta in un numero. ⚠️ Non autorizza a riaprire — autorizza a
**smettere di citarlo come prova**. E la casella non e' riempibile: 53 anni non esistono.

### Regola nuova

**Un verdetto si scrive con la forza del test che lo produce.** Se il criterio era *"dimostra che
> 0"*, il fallimento si scrive **"non dimostrato"**, non "refutato", e si accompagna con l'**MDE**.
`STRATEGY_LIFECYCLE` chiede gia' di dichiarare prima cosa significhera' un mancato rifiuto:
**non lo stavamo facendo**.

### Contabilita'

0 trial. Nessuna famiglia riaperta, nessun holdout toccato. I due verdetti declassati **non**
ricevono un trial nuovo: tornano allo stato precedente col budget residuo di allora. Restano chiusi,
ma **smettono di valere come prova** nel bilancio *"niente edge meccanico own robusto"* — che e' la
frase su cui poggia il pivot al passivo.

---

## 2026-09-18 (4) — **La correzione dell'ora era applicata due volte.** Il copier non e' piatto: E[R] **+0,127**, sorvegliabile in **54 giorni**

Voce di **correzione**: annulla e sostituisce i numeri del **§8** del documento soglie e del commit
`Copier: dati completi e verificati` (in DECISIONS non erano ancora entrati).

### Il difetto, mio, introdotto oggi stesso

La correzione di fuso di +1h **esisteva gia' da agosto** dentro `oos_validation.to_engine()`
(`TZ_SHIFT_H = 1`, commit `a845a32`). Non l'ho cercata prima di aggiungerne una seconda dentro
`backtest.replay()`. Ogni analisi che passa dal loader **e poi** dal motore — soglie di ritiro,
validazione OOS, report al socio — ha applicato la correzione **due volte**, cioe' **+2h**.

Non e' look-ahead (quello era il difetto del mattino): e' l'opposto, il fill cercato **un'ora piu'
tardi del vero**. Produce numeri **peggiori e plausibili**, che e' il motivo per cui non si e' visto.

Scarto mediano |entry dichiarato − prezzo al timestamp|, criterio indipendente dagli esiti, 699 segnali:

| shift aggiuntivo | −2h | −1h | **0h** | +1h | +2h |
|---|---|---|---|---|---|
| scarto mediano | $17,42 | $12,10 | **$3,98** | $9,39 | $13,30 |

### I numeri veri (629 trade, 2026-01-22 -> 2026-09-18)

| | §8, **nullo** | **corretto** |
|---|---|---|
| **E[R] a TP1** | +0,026 (indistinguibile da zero) | **+0,1265** BCa95 **[+0,0756 ; +0,1736]**, t = **+5,06** |
| differenza appaiata | +0,2821 | **+0,2939** [+0,2572 ; +0,3291], **9/9 mesi positivi** |
| maxDD 95esimo (blocchi) | 29,1 R | **11,7 R** |
| costo dell'indipendenza | +9,1R (+46%) | **+1,09R (+10%)** |
| serie negativa 95esimo | 9 | **5** |
| finestra minima su E[R] | ~5.300 trade (~5 anni) | **199 trade (~54 giorni)** |

**Si ribalta la conclusione del §8.** E[R] **non** e' indistinguibile da zero e **non** e'
ingovernabile: e' positivo con margine e si sorveglia in due mesi. La validazione OOS, che non era
contaminata (era gia' allineata), rifatta sulla finestra estesa a oggi conferma: differenza appaiata
**+0,274** [+0,209 ; +0,333], E[R] **+0,173** [+0,083 ; +0,244] su 218 segnali.

Il pareggio e' al **69,1%** (TP1 +0,46R contro SL −1,03R) e lui sta al **77,4%**: **8,3 punti** di
margine.

> ⚠️ **Correzione, mia, entro la stessa sera.** Avevo scritto che la geometria pubblicata "spreca"
> l'edge perche' il vantaggio appaiato vale **+0,294** e a TP1 se ne incassa **+0,127**. Il confronto e'
> **sbagliato: unita' diverse**. Il +0,294 e' una differenza di **win-rate** (29,4 punti percentuali),
> il +0,127 e' un E[R] **in R**. In R il vantaggio sul lato casuale vale **+0,597** a TP1 e **+0,588**
> a 1R: **la stessa cosa**. Nessuna geometria ne spreca meta'. Vedi §10 del documento.

### Decisione strutturale: la correzione ha **un solo proprietario**

`load_signals()` e `to_engine()` restituiscono timestamp **gia' allineati**; `replay()` e
`market_replay()` non toccano piu' l'orologio; il valore vive solo in `backtest.TS_OFFSET_H`.
Effetto collaterale: si chiude un secondo buco mai notato — `market_replay()` non applicava **nessuna**
correzione, quindi la tabella "robustezza al ritardo di copia" girava un'ora in anticipo.

`coverage.verifica()` adesso ricalcola quella tabella **a ogni esecuzione** e **solleva** se il minimo
non cade a 0. Una convenzione applicata in due posti non e' una svista da correggere guardando meglio:
e' una proprieta' del codice, e va resa impossibile ([[feedback_convenzioni_implicite]]).

Corretto anche il default di `backtest.M5`, che puntava ancora al feed corto (fino al 2026-06-12) e
tagliava in silenzio gli ultimi tre mesi di segnali.

### C5 implementata: il gate anti-ritardo diventa **asimmetrico**

Il divario fra modello e realta' operativa resta **il fatto piu' grande**: replay con fill a `entry`
**+0,124**, copier con fill **a mercato** +5 min e nessun gate **−0,184**. Lo scostamento e'
sfavorevole nel **72%** dei casi e i due lati hanno segno opposto: **favorevole +0,209** (n=195),
**sfavorevole −0,337** (n=501). Il gate sul valore assoluto buttava via proprio i migliori.

Applicando **la soglia gia' scritta in `config.yaml` (20 pip)** al **solo lato sfavorevole**:
**293 segnali su 696 (42%), E[R] +0,159** [+0,076 ; +0,239] — meglio del replay a limite, con
esecuzione realistica. Implementato in `signal_copier/planner.py` con test di regressione.

> ⚠️ **La soglia non e' stata scelta dalla tabella.** A 5 pip si legge +0,195: prenderlo sarebbe
> eleggere un vincitore dopo aver visto gli esiti, e costerebbe un trial. L'unica modifica e'
> **simmetrico -> asimmetrico**, correzione di esecuzione, **0 trial** ([[feedback_correggere_non_e_cercare]]).

### Igiene del repo

`.gitignore` non copriva `_export_telegram/`: il commit delle 17:xx aveva inglobato **4.384 file /
184 MB** di chat privata (foto e video del canale). **Mai pushato**; regole aggiunte, indice ripulito,
commit riscritto. Estratto inoltre in un commit proprio il fix `_build_broker` dell'utente, finito per
sbaglio nel commit del gruppo C per un `git add -A` di troppo.

### B7 (uscita a 1R) chiusa la sera stessa, **0 trial**

L'uscita a 1R **era gia' dentro i numeri**: la "win-rate simmetrica (+1R prima di −1R)", metrica
**primaria** della pre-registrazione di agosto, **e'** l'uscita a 1R — bastava convertirla in R.
Confronto appaiato sullo stesso segnale (n=627): TP1 **+0,1247** [+0,0737 ; +0,1712], 1R **+0,1246**
[+0,0480 ; +0,2011], **differenza −0,0001 BCa95 [−0,0633 ; +0,0596]**. Identiche — e 1R porta
**+58% di deviazione standard** a parita' di rendimento, quindi e' **peggiore**.

Non costa un trial perche' **non si adotta niente**: il contatore si muove quando si adotta una
regola scelta dopo averne visto l'esito, non quando la si rifiuta. Se fosse uscita positiva, allora
sarebbe servita una pre-registrazione.

⚠️ **Limite che resta, e vale piu' di B7**: il lato casuale a TP1 vale **−0,487** in convenzione
pessimistica e **+0,333** in quella ottimistica — forbice di **0,82R**, contro i 0,05R del mentore.
Il "+0,59R contro il caso" e' **condizionato alla convenzione pessimistica**. Si stringe solo con
dati M1/tick, non con altra statistica sugli stessi dati.

Documento: [MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md §9-§10](docs/MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md).

---

## 2026-09-18 (2) — **Gruppo C chiuso**. E cercando una soglia abbiamo trovato **un'ora di look-ahead** sull'unico binario positivo

Il bucket C del [backlog](docs/BACKLOG_RICERCA.md) e' chiuso per intero (C1-C2 gia' decadute, **C3,
C4, C5, C6** oggi). Il risultato che conta non era nella scaletta.

### Il difetto: i timestamp dei segnali erano indietro di un'ora

Cercando la soglia anti-ritardo (C5) e' saltato fuori che lo scostamento mediano fra il prezzo di
mercato al momento del segnale e l'`entry` dichiarato valeva **$12,92 = 1,27R**, piu' dell'intero TP1
nel **79,5%** dei casi. Troppo per essere latenza.

Test dell'offset costante: minimo **netto a +1h** (mediana da $12,69 a **$4,23**) e **stabile su tutti
e sei i mesi**, senza salti DST → disallineamento **fisso** di orologio fra export dei segnali e feed M5.

⚠️ `replay()` cercava il fill da `searchsorted(T, ts)`, cioe' **un'ora prima che il segnale
esistesse**: poteva riempire su prezzi **precedenti alla pubblicazione**. **Look-ahead di prezzo**,
stessa famiglia del fill fantasma del FADE ([[feedback_fill_ottenibile]]).

| | fill eseguiti | win-rate simmetrica | E[R] a TP1 |
|---|---|---|---|
| ts grezzo (come tutto e' stato validato) | 88% | **67,3%** | **+0,2025** |
| **ts corretto (+1h)** | 78% | **56,1%** | **+0,1015** [+0,037 ; +0,159] |

**E[R] dimezzato, win-rate −11 punti.** Il "67-72%" citato ovunque nel repo era misurato col difetto.

### L'edge sopravvive, e il motivo e' il disegno appaiato

La metrica primaria del verdetto OOS era la **differenza appaiata** contro lo stesso segnale con lato
casuale. Il difetto gonfiava **entrambi i lati**:

| | mentore | random | differenza appaiata |
|---|---|---|---|
| ts grezzo | 67,4% | 35,3% | +0,3214 [+0,2794 ; +0,3613] |
| **ts corretto** | 56,2% | 30,8% | **+0,2541** [+0,2118 ; +0,2941] |

> 🔧 **Il verdetto non si ribalta: l'edge era sovrastimato del ~21%, non inventato.** E non si
> ribalta **perche' era misurato contro un baseline appaiato** invece che contro una soglia assoluta
> ([[feedback_r_multiple_ceiling_baseline]], qui a nostro favore). Correzione applicata come
> `TS_OFFSET` in `backtest.py`: **bug fix, 0 trial** (§3).

### C5 — il gate non e' un dettaglio, e non deve essere simmetrico

Il replay riempie a `entry`; il copier piazza `order_type="market"`. **Due esecuzioni diverse**:

| esecuzione | E[R] |
|---|---|
| replay (fill a `entry`, attesa 6h) | +0,101 |
| **copier senza gate (mercato, +5 min)** | **−0,256** |

Senza gate l'esecuzione a mercato **trasforma l'edge in una perdita**. E lo scostamento ha due segni
molto diversi: **favorevole +0,183**, **sfavorevole −0,423**. Il gate di oggi li tratta uguali, quindi
scarta proprio i trade migliori.

| configurazione | tenuti | E[R] |
|---|---|---|
| simmetrico 20 pip (oggi) | 103 (22%) | +0,085 [**−0,045**; +0,192] |
| **asimmetrico, 20 pip solo sullo sfavorevole** | **197 (41%)** | **+0,130** [**+0,037**; +0,236] |

Stesso numero gia' dichiarato, si toglie solo una restrizione dannosa. ⚠️ **Da implementare in
`signal_copier/planner.py`**: oggi il codice e' ancora simmetrico.

### C3 — soglie rifatte coi numeri corretti

**DD 13,7R · serie negativa 5 · finestra minima 310 trade (~73 giorni)**, dal ricampionamento **a
blocchi sui giorni** (gli esiti non sono indipendenti: runs test z=−2,55, +25% di drawdown rispetto
al rimescolamento i.i.d.). La finestra minima **quintuplica** rispetto alla prima stesura: serve
$npprox(2{,}80\sigma/E)^2$ e con E[R] dimezzato il fabbisogno quadruplica.
La prima stesura (DD 12R, serie 6, finestra 62) e' **nulla e non va citata** (§6a n.1).

### C4 — era gia' corretto, verificato

`suggested_lots` calcola `lots = (equity × risk%) / (distanza_SL_pip × valore_pip)`: rischio fisso in
valuta, size derivata dallo stop, come raccomandano le 3 fonti. Usa **equity**, non balance
(`__main__.py:214`), e l'1% per segnale e' **diviso fra le gambe**, quindi non cresce col numero di
TP. **Nessuna modifica.**

### C6 — decaduta, con condizione scritta

Il livello di portafoglio richiede ≥2 strategie vive e poco correlate: col KILL del FADE ne resta
**una**. Si riapre **quando esistono due binari con capitale contemporaneamente**.

### Cosa resta aperto
Rifare la **validazione OOS** col `TS_OFFSET` corretto (finche' non e' rifatta, il verdetto va letto
come **sovrastimato del ~21%**, non annullato) e **implementare il gate asimmetrico** prima del
capitale.

---

## 2026-09-18 — **C3 fatta**: soglie di ritiro del copier mentore. L'ipotesi di indipendenza valeva **5,3R**

Prima voce di §8bis mai compilata, e arriva **prima del capitale**: il copier non e' ancora operativo
(il deploy VPS del 15/09 era fallito). Documento vincolante:
[`MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md`](docs/MENTOR_COPIER_WITHDRAWAL_THRESHOLDS.md), motore
[`analysis/mentor_signals/withdrawal_thresholds.py`](analysis/mentor_signals/withdrawal_thresholds.py).

**Il profilo che rende le soglie necessarie.** 477 trade, 101 giorni: E[R] **+0,2025**, sd 0,571,
**82,6% di vincenti**, payoff **+0,46 / −1,03**. L'equity sale quasi sempre e scende di colpo, e
servono **2,2 vincite per recuperare una perdita**: e' il profilo in cui la tentazione di spegnere nel
mezzo e' massima proprio quando non andrebbe fatto.

### Il risultato che ha cambiato i numeri

Il Monte Carlo standard rimescola i trade, cioe' **assume che siano indipendenti**. Non lo sono:

| diagnostica | valore |
|---|---|
| runs test vinta/persa | **z = −3,37** |
| autocorrelazione lag 1 / lag 10 | **+0,136** / +0,085 |
| segnali al giorno | 4,7 (max 9), stesso strumento |

Quando la lettura del mentore e' sbagliata, **sbaglia per tutta la sessione**: le perdite arrivano in
grappoli, e il rimescolamento distrugge proprio quello.

| simulazione (95° pct, 20.000 percorsi) | maxDD | serie negativa |
|---|---|---|
| i.i.d. (rimescola i trade) | **6,84 ± 0,06 R** | 4,88 ± 0,35 |
| **a blocchi (giorni interi)** | **12,15 ± 0,12 R** | 5,38 ± 0,52 |

> 🔧 **L'ipotesi di indipendenza valeva 5,31R: il 78% di drawdown in meno.** Col metodo standard
> avremmo messo la soglia a 6,8R e ritirato il copier durante un drawdown che gli capita
> **normalmente una volta su venti**. E' il **buco 29** del distillamento Quant Guild applicato, e da
> solo ha quasi raddoppiato la soglia. Gli errori standard sono riportati perche' un percentile e' una
> stima (**buco 37**).

### Le soglie

| | valore |
|---|---|
| **DD di ritiro** | **12 R** |
| **Serie negativa** | **6 consecutive** |
| **Finestra minima** | **62 trade** (~13 giorni) |

**12R e non 20R** (il valore che si otterrebbe con E[R] al limite inferiore OOS +0,079): la soglia
manda in **incubazione**, non in pensione. Un falso allarme costa poco ed e' reversibile; una soglia
larga fa bruciare capitale vero mentre si aspetta. Si accetta che scatti piu' del 5% se il vero E[R]
e' basso.

**Criterio di rientro, dichiarato ora**: si torna LIVE quando in simulazione la curva **recupera il
picco precedente** *e* sono passati almeno **62 trade** dall'ingresso in incubazione. Entrambe.
Seconda uscita dopo un rientro → **ritirata definitiva**.

### Una buona notizia sulla potenza, per contrasto col FADE
Il degrado che conta — **da +0,20 a zero** — si vede in **62 trade (~13 giorni)**. Sul FADE ne
servivano oltre 1.000 anche per la domanda grossa. La differenza e' la deviazione standard:
**0,571R contro 1,8R**. E' questo che rende il binario governabile. (Un degrado *piccolo*, 0,05R,
resta invisibile per ~216 giorni: dichiarato, non nascosto.)

### Limiti dichiarati
Campione **in larga parte in campione** (la OOS e' successiva e su export diverso; la sensibilita' del
§3 compensa solo in parte) · il **replay non e' il copier**: assume fill entro 6h e la **soglia
anti-ritardo (C5) e' ancora aperta** · un solo strumento, un solo mentore, cinque mesi.

**Costo: 0 trial.**

---

## 2026-09-17 (6) — **B1 CHIUSA** sul criterio dichiarato prima. Ma il nullo non e' piatto: e' **bimodale**

Ultimo tassello della giornata, fatto invece di lasciare B1 al 90% con una "condizione di
riapertura" — che sarebbe stato un parcheggio travestito da decisione
([[feedback_un_lavoro_iniziato_si_finisce]]).

**Perche' serviva.** La passata descrittiva misurava una **pendenza lineare**, ma la fonte parla delle
**code** (*"deviates significantly far"*), e pendenza e code avevano segni opposti su alcuni gruppi.
La pendenza era il riassunto sbagliato per la domanda.

**Criterio dichiarato nel commit PRIMA di eseguire** (`analysis/meanrev/tails.py`): effetto di coda
(decile alto di |z|) aggregato per gruppo, contro un nullo **matched** ottenuto ri-allineando z ai
rendimenti futuri con spostamento circolare — conserva autocorrelazione, volatilita', calendario e
numerosita', rompe **solo** l'accoppiamento. 300 permutazioni. Un gruppo conferma se eff > 0 **e**
sopra il 95esimo percentile del nullo. **Soglia: ≥ 5 gruppi su 8.**

| gruppo | eff osservato | percentile nel nullo | |
|---|---|---|---|
| energy | **+0,0527** | 100,0% | ✅ ritorno alla media |
| index | **+0,0466** | 99,7% | ✅ ritorno alla media |
| fx_cross | **+0,0377** | 100,0% | ✅ ritorno alla media |
| bond | −0,0079 | 30,7% | no |
| metal | −0,0508 | 38,3% | no ⚠️ nullo instabile (p95 = +0,77) |
| fx_major | −0,0146 | 3,7% | no |
| agri | −0,0720 | **0,0%** | **continuazione** |
| crypto | **−0,2507** | **0,0%** | **continuazione netta** |

**3 su 8. Sotto la soglia. → B1 CHIUSA.**

### Cosa dice davvero questo risultato

Non e' "non c'e' niente": e' **struttura con segni opposti per gruppo**, che si annulla in aggregato.
Crypto sta allo 0° percentile sul lato continuazione con la stessa forza con cui energy sta al 100°
sul lato ritorno alla media.

> ⚠️ **E questo e' esattamente il motivo per cui la soglia era dichiarata prima.** La tentazione ora
> e' *"tre gruppi confermano, inseguiamo quelli"*. Sarebbe **eleggere un vincitore dalla mappa dopo
> averla vista** — il p-hacking che il criterio esisteva per impedire. Il claim della fonte era
> *"mean reversion"* senza condizioni: quel claim e' **falso sui nostri dati**. Un claim
> **condizionato al gruppo** e' un'ipotesi diversa, che nessuno ha formulato prima di guardare, e che
> costerebbe un trial.

### Terza corroborazione indipendente del lead playground, nella stessa giornata
La continuazione e' netta dove la volatilita' e' alta (**crypto −0,25**, agri −0,07) e assente sui
major FX. Terzo strumento diverso, stesso ordinamento del rho +0,857
([[project_trend_playground_lead_2026_08_14]]). Non e' conferma statistica — e' convergenza di segno,
e vale come prior per quando si aprira' A1.

⚠️ **Nota tecnica**: il nullo del gruppo metal e' instabile (p95 = +0,77 contro p50 = +0,004),
segno che almeno uno strumento del gruppo produce valori estremi. Non cambia il verdetto — metal non
confermava comunque — ma va guardato se si torna su quel gruppo.

**Costo: 0 trial.** Budget della famiglia FADE ancora 2 di 3, budget pre-registrazioni esterne ancora
2 di 2-3 nel trimestre.

---

## 2026-09-17 (5) — B1 (mean reversion Kichev): la fonte dice **molto meno** di quanto le attribuivamo, e la misura descrittiva e' **nulla**

Misura descrittiva, **0 trial**: [`analysis/meanrev/descriptive.py`](analysis/meanrev/descriptive.py),
dichiarata come descrittiva **nel commit precedente all'esecuzione**. Nessuna soglia, nessuno stop,
nessun GO/NO-GO. Output in [`docs/health/b1_meanrev_descriptive_2026-09-17.txt`](docs/health/b1_meanrev_descriptive_2026-09-17.txt).

### 1. La fonte e' molto piu' sottile di come l'avevamo registrata

Il backlog attribuiva a B1 una spec precisa: *"|close − SMA5| oltre una soglia normalizzata sullo
scostamento storico"*. Andando a leggere la trascrizione, Kichev dice **esattamente questo**:

| Mean Reversion | Price deviates significantly far from mean | Exit after reversion or fixed period (1-4 days) | Days |

**Tutto qui.** Nessun periodo della media, nessuna soglia, nessuno stop. **`SMA5` e la
normalizzazione erano nostri**, non suoi. Quindi B1 non era *"la forma canonica del FADE scritta da
una fonte esterna"*: la fonte fornisce una **famiglia** e un **orizzonte**, e ogni parametro in piu'
lo scegliamo noi — cioe' e' li' che entrerebbe la molteplicita' che credevamo di aver evitato.
⚠️ Riga del backlog **corretta**.

### 2. La misura: nessun ritorno alla media su D1

Pendenza di (rendimento a h giorni / ATR) sullo scostamento normalizzato z, su **30 strumenti,
8 gruppi, 2012-2026**, per periodi di media 3/5/10/20 e orizzonti 1-4 giorni (l'unico numero che la
fonte fornisce). Negativa = ritorno alla media.

- L'intera mappa sta fra **−0,02 e +0,008** in unita' di ATR: livello rumore.
- **16 strumenti su 30** e **4 gruppi su 8** hanno pendenza negativa: testa o croce.
- Correlazioni |r| quasi tutte sotto **0,03**.

**Non c'e' niente da pre-registrare.** Raccomandazione: **non spendere il trial su B1** cosi' com'e'.

### 3. Le due cose che valgono, e non erano la domanda

| gruppo | pendenza | lettura |
|---|---|---|
| **crypto** | **+0,0796** (corr +0,069) | **continuazione netta**, il segnale piu' forte della tabella |
| agri, bond, metal | +0,013 / +0,008 / +0,005 | continuazione debole |
| fx_major | −0,007 | ritorno alla media debolissimo |
| index, fx_cross | −0,036 / −0,021 | ritorno alla media, ma **2 e 3 strumenti** |

1. **Il crypto va nella direzione opposta**, e con il segnale piu' forte: contraddice la stessa fonte,
   che al §7 raccomanda *"mean reversion on crypto"*. Registrato come **claim della fonte falsificato
   sui nostri dati**.
2. 🔧 **Corroborazione indipendente del lead playground**: la continuazione e' forte dove la
   volatilita' e' alta (crypto, agri, metalli) e assente o invertita dove la liquidita' e' massima
   (fx_major). E' lo stesso ordinamento di [[project_trend_playground_lead_2026_08_14]] (rho +0,857),
   misurato con **uno strumento completamente diverso** — deviazione da media invece di regola di
   trend. Non e' una conferma statistica, e' una convergenza di segno che vale come prior.

⚠️ **Anomalia da non inseguire stasera**: per alcuni gruppi la pendenza complessiva e il
comportamento **nelle code** (decile alto di |z|) hanno **segni opposti** — possibile non linearita'
(ritorno alla media al centro, continuazione agli estremi). E' un'ipotesi generata dai dati: se si
vuole guardare, si guarda **dichiarandolo prima**.

---

## 2026-09-17 (4) — **FADE: KILL della famiglia.** EA spento. Il +0,31R era per intero fill fantasma

Decisione dell'utente dopo la misura onesta. Chiude la famiglia **NXT/FADE**, aperta a luglio.

**Il numero che chiude la questione.** Con la primitiva unica
[`core/resolve_trade.py`](core/resolve_trade.py) e soli **fill ottenibili**, su 10.218 setup / 14 anni / 6 asset:

| campione | n | E[R] | BCa 95% |
|---|---|---|---|
| **fill ottenibili (SKIP)** | **5.506** | **−0,250** | **[−0,287 ; −0,210]** |
| fill ottenibili, convenzione ottimista | 5.506 | −0,186 | [−0,226 ; −0,146] |
| tutti i setup, col fill fantasma | 10.218 | +0,409 | [+0,370 ; +0,443] |

**Il 46,1%** dei setup aveva il livello gia' oltrepassato. Il segno positivo del lead veniva **per
intero** da quei fill: +0,409 col fantasma, **−0,250** senza. Non un aggiustamento, un ribaltamento —
e misurato **sui dati da cui la strategia era stata derivata**, cioe' nelle condizioni piu'
favorevoli possibili.

**Base regolamentare**: kill duri [`STRATEGY_LIFECYCLE`](docs/STRATEGY_LIFECYCLE.md) §6a **n. 1**
(difetto metodologico conclamato: i vecchi numeri sono **nulli**, rifatti da zero danno −0,25) e
**n. 3** (fallimento di breadth). Nessun ramo di rifinitura disponibile (§4.4 della pre-registrazione).

**Contabilita' finale della famiglia**: trial **2 di 3**. La riparazione dell'EA e la ri-misura con
la primitiva **non hanno consumato trial** (§3: bug fix + esecuzione piu' realistica). **Il trial #3
non e' stato speso e resta disponibile** per un'ipotesi con razionale indipendente.

**Cosa succede all'infrastruttura.**
- **EA spento** dall'utente. Il fix v1.10 (`bbea38e`) resta in repo: e' codice corretto, se un giorno
  servira' quella meccanica e' gia' giusta.
- I **90 ingressi live** valgono **zero**, come i 36 del 27/08: l'audit di esecuzione aveva gia'
  stabilito che non erano la strategia pre-registrata.
- La famiglia e' **CLOSED**: si riapre solo con evidenza esterna nuova (§7), non con un parametro.

**Cosa resta, e vale.** La primitiva `resolve_trade` con le **cinque** convenzioni esplicite e la
prova di equivalenza con le quattro implementazioni storiche. E' il pezzo che sopravvive alla
strategia: qualunque backtest futuro parte da li' invece di reimplementare la logica una quinta volta.

---

## 2026-09-17 (3) — FADE: il motivo per cui l'EA era lasciato rotto **non sopravvive a un calcolo di potenza**

Primo lavoro fatto **applicando** i buchi del distillamento invece di catalogarli. Documento vincolante:
[`FADE_LIVE_AUDIT_PROTOCOL.md`](docs/FADE_LIVE_AUDIT_PROTOCOL.md), scritto **prima di guardare qualunque esito**
(nessun P&L, nessun R, nessuna interrogazione dello storico MT5 in questa sessione).

**Il fatto verificato nel sorgente, non nei resoconti.** `mql5/nxt_fade.mq5` righe **432-451**: l'EA **entra ancora a
mercato** quando il prezzo ha superato l'entry pre-registrata (`else ok = g_trade.Sell(...)`), con volume dimensionato
sulla distanza **teorica** `entry - sl` (riga 427). Il difetto del 27/08 **non e' stato riparato**: la patch di allora
sistemo' i pendenti orfani, non questo ramo.

**Il calcolo che nessuno aveva fatto.** Con SD = 1,8R per trade (numero gia' nostro, dichiarato il 2026-08-04):

| | n | effetto minimo rilevabile (80%) |
|---|---|---|
| ramo onesto | ~46 | **0,744R** — un win rate del **43,5%** su una 1:3, che nessuno ha mai proposto |
| tutto il campione | ~82 | 0,557R |

E per il **confronto fra i due rami** — la seconda motivazione del 2026-09-15, quella per cui l'EA non andava
riparato — la differenza prevista e' **0,123R**, che richiede **3.362 trade per ramo**, cioe' **circa dodici anni**.

> 🔧 **La motivazione n. 2 del 2026-09-15 non era sbagliata come ragionamento: era non verificata come numero.**
> E' fuori scala di un fattore ~40. E' il buco 2 del distillamento Quant Guild applicato per la prima volta **contro
> una nostra decisione**, non contro una fonte esterna.

**Il problema piu' grave non e' la potenza, e' la selezione.** Il vincolo *una posizione per strumento* fa si' che un
ingresso a mercato **occupi lo slot** e blocchi i setup successivi su quello strumento — e l'ingresso a mercato avviene
**quando il prezzo si e' mosso in fretta contro il ritracciamento atteso**, cioe' per una ragione non casuale. Il ramo
onesto non e' un sottoinsieme casuale dei setup: e' il complemento di una selezione sistematica.
**Raccogliere piu' trade con l'EA in questo stato rende la stima piu' precisa attorno al valore sbagliato.**

**Costo in tempo, mai calcolato prima.** Al ritmo del ramo onesto (0,77 trade/giorno): **~11 mesi** per rilevare
+0,31R, **~1,4 anni** per |E| = 0,25R, **~3,6 anni** per un KILL statistico onesto. Il FADE non e' solo non
dimostrato: **non e' risolvibile in meno di circa un anno**, qualunque sia la risposta.

**Decisioni.**
1. **Nessun verdetto su E[R] da questo campione**, ne' GO ne' KILL — e il mancato rifiuto del fantasma +0,31R
   (potenza ~52%) **non conta come evidenza a favore**, dichiarato prima di vedere il dato.
2. **Il trial #3 resta chiuso.** Delle 4 condizioni del §11 della pre-registrazione, **tre sono non soddisfatte**
   (primitiva `resolve_trade`, backtest a fill ottenibili con E[R] positivo, EA che rifiuta il setup). Aggiunta la
   **condizione 5**: N dichiarato sulla base della potenza.
3. **Si esegue un audit deterministico** (0 trial): tipo di ordine, prezzo di fill, rischio reale, RR, doppioni,
   e conteggio dei setup persi per slot occupato. Sono verifiche **binarie per trade**, dove n=46 abbonda perche' non
   si stima un effetto, si controlla una conformita'. **L'audit non guarda il P&L.**
4. **Aperta all'utente**: riparare l'EA (rifiutare il setup invece di entrare a mercato) oppure spegnerlo. La ragione
   per lasciarlo com'e' e' decaduta con il §2.3 del protocollo. Se si ripara, il campione raccolto finora **non si
   somma** a quello nuovo (§4.3, che vale contro di noi come il 27/08).

### Esito dell'audit, eseguito lo stesso giorno

EA portato a **v1.10** (commit `bbea38e`): il ramo a mercato **non esiste piu'**, il setup si salta,
fedele alla definizione della variante SKIP in `entry_fill_audit.py` righe 131-132. **Zero trial**
(§3: bug fix + esecuzione piu' realistica). Poi audit con
[`analysis/nxt/execution_audit.py`](analysis/nxt/execution_audit.py) su **90 ingressi**:

| verifica | non conformi | esito |
|---|---|---|
| V1 ordine pendente | **40 su 90 (44%)** | ❌ |
| V2 fill al prezzo pre-registrato | 0 su 50 pendenti | ✅ |
| V3 rischio reale = inteso | **39**, fino a **4,01×** | ❌ |
| V4 rapporto 1:3 | **39**, fino a **1:0,00** | ❌ |
| V5 un setup per strumento | 1 | ❌ |

**Verdetto per la tabella dichiarata prima di guardare**: V1 fallita → i trade **non sono la
strategia pre-registrata**, il ramo pendente resta **selezionato**, il campione **non e' utilizzabile
per stimare E[R], ne' ora ne' mai**. I 90 ingressi valgono **zero**, come i 36 del 27/08.

Il **44%** e' peggiore del 40% misurato allora: non un peggioramento del codice — quel ramo non era
mai stato toccato — ma la conferma che il difetto era **stabile e continuo** (23 su 45 anche dopo il
fix del 27/08). Unica nota positiva, isolata: **V2 passa su tutti e 50 i pendenti**, quindi il
meccanismo dell'ordine pre-registrato funziona; era rotto solo il **ripiego**.

⚠️ **Correzione a mio carico**: la prima versione di V3 non valutava gli ordini a mercato
(`price_open = 0`) e la tabella degli outlier mostrava solo `1,00×`, leggibile come *"va tutto
bene"*. Il rischio inteso si ricostruisce esattamente da `|tp - sl| / 4`. Corretto prima di
pubblicare il report.

**Serve ricompilare e ridistribuire l'EA sulla VPS** perche' il fix abbia effetto.

---

---

## 2026-09-17 (2) — Passata mirata sulle opzioni: la **gamba di copertura e' CHIUSA**. Il conto torna solo con la leva

Unica coda aperta del distillamento Quant Guild: il claim della "gamba di copertura con monetizzazione del drawdown",
parcheggiato **tre volte** senza mai essere deciso. Letti **7 video** del gruppo 2 scelti perche' toccano il claim
(non e' l'apertura del gruppo 2, che resta chiuso), con i **criteri di qualifica/chiusura dichiarati prima** della
lettura: [`copertura.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/quantguild/copertura.md).

**Esito: CHIUSO.** Il claim forte — *"la copertura migliora il CAGR di lungo periodo"* — cade per tre motivi:
il costo non e' mai prezzato in 10 video; la regola di monetizzazione e' **dichiaratamente non pubblicata**
(*"stavo pensando di pubblicare le note... non so bene cosa farne"*, il resto e' in un corso a pagamento);
l'unica dimostrazione numerica e' **sbagliata** (dichiara crescita geometrica 0% con mu=15% e sigma=30%: ricalcolata
vale **+10,5%**, e per azzerarla servirebbe **sigma=54,8%**).

🔧 **Il risultato riusabile — la condizione di pareggio**, che nessuna delle fonti enuncia e che vale anche per la
variante KMLM gia' nel repo: una gamba che costa `c` all'anno e porta la volatilita' da `sigma` a `k*sigma` si ripaga
con la sola riduzione dell'erosione **solo se `sigma > sqrt(2c / (1 - k^2))`**. Con c=2,5% e k=0,5 serve
**sigma > 25,8%**; un azionario diversificato sta a 15-20%, dove l'erosione totale vale **1,1-2,0%/anno** — cioe'
**meno di quanto costa la gamba**, anche azzerando tutta la volatilita'. **Il conto torna solo a volatilita' alta**, ed
e' esattamente per questo che entrambe le fonti accoppiano la gamba alla **leva** senza trarne la conseguenza: la
proposta reale non e' "aggiungi protezione al tuo ETF", e' un **pacchetto azionario-con-leva piu' copertura**.

**Cosa sopravvive, con condizione dichiarata.** L'argomento della **perdita tripla** (in una crisi lavoro, casa e
portafoglio crollano insieme perche' condividono il fattore macro; *"serve liquidita' quando serve a tutti"*) e'
valido, ma **non e' un argomento sul CAGR**: e' sulla correlazione col **capitale umano**. Condizione operativa:
*la gamba serve quando il capitale finanziario e' grande rispetto al capitale umano residuo*. **Oggi non si applica**
(capitale ~0, decenni di reddito davanti, e il drawdown si ricompra con i versamenti del PAC — la monetizzazione
gratis). Torna seria **a ridosso del decumulo**, e solo con costo dichiarato e regola scritta prima.

**Aggiornati**: la nota in `08_asset_allocation_passiva` (da "da verificare" a **chiusa**, con la disuguaglianza e la
condizione), la Mappa dei modelli, la memoria. **Nessuna azione operativa**: non abbiamo un broker opzioni e non
serve averlo.

**Nota di metodo, a mio carico**: avevo scelto `#65` ("Why Hedging Ruins Everything") aspettandomi la contraddizione
interna della fonte. **Ipotesi sbagliata**: e' un video motivazionale su startup e relazioni, non sulla copertura
finanziaria. Contiene pero' un difetto che vale la pena registrare — presenta come matematica un argomento
**infalsificabile** (due diagrammi di Venn e nessun dato), cioe' lo stesso difetto che il canale rimprovera ai guru.

---

## 2026-09-17 — Distillamento Quant Guild **CHIUSO**: 81 video letti per intero, **48 buchi di metodo**, zero strategie, zero pre-registrazioni

**Cosa è stato fatto.** Secondo distillamento del canale **Quant Guild** (Roman Paolucci), a **cattura ampia**
([[feedback_distillazione_cattura_ampia]]): gruppo 1 = **81 video letti integralmente** dalle copie di lettura, in
otto blocchi tematici, più 2 video scaricati per risolvere un'attribuzione. Output:
[`fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/quantguild/SINTESI.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/quantguild/SINTESI.md)
(catalogo per dominio + buchi + conflitti), schede per video in `quantguild/blocco-A..H.md`, diario di lavoro in
`quantguild/PIANO.md`. Registrato in [`_INTAKE.md`](fondamenti_tecnici/_INTAKE.md).

**Natura della fonte, che cambia cosa ci si può aspettare.** A differenza del funnel Chart Fanatics (che cercava
strategie e ne ha trovate zero), questa è una fonte di **metodo statistico**. Non c'era nulla da importare come
strategia e infatti **nessuna pre-registrazione è stata aperta**: il budget esterno resta intatto. Ciò che ha prodotto
sono **48 buchi** nel nostro impianto e **14 conflitti** da mappare.

### Le sei cose che cambiano un verdetto, e costano poco

1. **Potenza e dimensione campionaria** $n\approx(z\sigma/E)^2$. Senza, un NO-GO non distingue *"non c'è edge"* da
   *"non potevo vederlo"*. Con un effetto di +0,04R servirebbero **~36.000 trade**: la maggior parte dei nostri NO-GO
   non ha mai dichiarato quale effetto era in grado di rilevare.
2. **Filtraggio vs lisciamento** come criterio **generale** contro il look-ahead. Oggi il repo copre un caso singolo
   ([[reference_regime_timeline_lookahead]]); la regola è che **ogni finestra centrata** e ogni stima che usa il futuro
   del campione (Baum-Welch, medie centrate, smoother) è look-ahead se usata come segnale.
3. **L'errore standard delle nostre stime Monte Carlo non viene mai riportato.** Con 1.000 permutazioni il SE di un
   p-value vicino a 0,05 vale ~0,7 punti percentuali: **"p = 0,048" e "p = 0,062" non sono distinguibili** dal numero
   di repliche scelto. Tocca ogni verdetto vicino alla soglia e la regola di futilità DSR.
4. **La finestra di misura del conto live non è pre-registrata.** La fonte esibisce, sullo stesso conto e sullo stesso
   anno, **Sharpe 0,88** (da inizio anno) e **6,28** (partendo dal minimo): è il *look-elsewhere* applicato alla **data
   d'inizio**. Per le strategie il periodo è pre-registrato; per il conto no, e il conto oggi mescola attività diverse.
5. **Nessuna correlazione nei nostri documenti dichiara frequenza e finestra.** Esempio misurato dalla fonte:
   JNJ/CMG stanno a **0,01** su rendimenti annuali, **0,13** su mobile mensile, **0,17** su mobile a 60 giorni
   **con punte a 0,73**. Due attivi "scorrelati" possono essere quasi identici **proprio nella finestra in cui si
   subisce il drawdown**. Riguarda `TSMOM_PREREGISTRATION`, `TREND_EXIT_PLAYGROUND_PREREGISTRATION`,
   `INVESTMENT_ALGO_DESIGN`, `INVESTING_PILLAR_PLAN`. **Costo: una riga per documento.**
6. **Backtest per eccedenze** delle soglie dichiarate e **test di indipendenza degli esiti**: tutte le nostre soglie
   i.i.d. poggiano su un'ipotesi mai verificata.

### Numeri ricalcolati — più volte **contro** la fonte
Dove si poteva ricalcolare, si è ricalcolato. La rovina del giocatore nel suo esempio è **88,4%**, non *"certa anche
con un vantaggio"* come afferma. Il vantaggio della roulette americana (**−5,26%**) è invece corretto. Le statistiche
dichiarate sui mercati sono quasi tutte **in campione e senza costi** (Sharpe 2,72 del long-short; 3,01 in
addestramento, che lui stesso dichiara sovradattamento) → registrate come **non-evidenza**.

### Tre conferme esterne di decisioni già prese — **nessuna riapertura**
- **Stock Selector archiviato** ([[project_stock_selector_eval_2026_06]]): il beta non si elimina scegliendo bene
  (VRT: beta **2,22**, drawdown **61%** contro **20%** del mercato). Arriviamo alla stessa conclusione per due strade
  indipendenti, la nostra empirica e la sua strutturale.
- **I due secchi del PAC**: *"e se fra sei anni ti servissero i soldi e ci fosse un −30%?"* è esattamente la ragione del
  secchio cuscinetto in `docs/INVESTING_PILLAR_PLAN.md`.
- **Decenni persi**: già nel repo (`08`) con numeri migliori e con la risposta strutturale (i decenni persi di Italia e
  Giappone furono **locali** → All-World).

### Conflitti per la mappa dei modelli (i tre che contano)
- **"L'analisi tecnica non si può confutare"**. *Condizioni*: vero per l'**abilità discrezionale** di chi sceglie
  **quando** applicare una regola; falso come affermazione generale. *Stato*: **il NULL a 384 trial sui livelli resta**
  ([[project_level_research_v1_null_2026_07_06]]) — falsificava regole **meccaniche**, che era il bersaglio. Si aggiunge
  la precisazione che quel NULL **non copre il discrezionale**, e che il discrezionale si misura con il **track record
  prospettico pre-registrato**: strada che abbiamo già percorso con successo sui segnali del mentore
  ([[project_mentor_signals_edge_2026_07_08]]). **La confutabilità che la fonte dichiara impossibile, noi l'abbiamo
  già esercitata.**
- **"Non è la domanda se l'alpha sia consistente e statisticamente significativo"** (analogia del fuoricampo).
  *Condizioni*: coerente per un **allocatore con mandato**, che opera comunque e deve solo restare in posizione.
  *Contraddice* frontalmente `docs/STRATEGY_LIFECYCLE.md` e [[feedback_mass_search_vs_preregistration]] per chi deve
  **decidere se accendere**. *Stato*: **la nostra posizione resta**; si registra la distinzione fra problema di
  **selezione** (nostro) e di **esecuzione** (suo).
- **Gamba di copertura con monetizzazione**: ora a **tre occorrenze** (E2, G6, #29), sempre presentata come corso a
  pagamento, **mai** con un fuori campione, i costi o i parametri. *Stato*: **invariato** — resta la nota
  "speculativo/promozionale, da verificare" in `08_asset_allocation_passiva`. **Tre video della stessa fonte con lo
  stesso conflitto d'interesse non fanno tre conferme.**

### Un'attribuzione risolta, e l'errore che l'aveva bloccata
Il blocco di appunti orfano *"Comprehensive Guide to Investing"* (`Nuove nozioni teoriche 2026-07-16.txt`, righe
331-491) è di **#29 `LX4Ugaxx9n0` — The Ultimate Guide to Quant Portfolio Management**, cioè dello **stesso video**
già attribuito per `quantportfolio managernotes.txt` righe 1-249: **un video, due serie di appunti in due file
diversi**, che coprono metà video ciascuna. L'ipotesi registrata nel piano (*"uno fra #24, #131, #162"*) era
**sbagliata**: i tre candidati sono stati letti per intero, **zero marcatori**.
**Regola che ne esce**: un blocco di appunti orfano va cercato **per contenuto sull'intero canale**, non fra i video
"non ancora distillati" — un video già distillato può aver prodotto **più blocchi**, e il titolo del riassunto è
generato dal sintetizzatore, quindi **non coincide** con quello del video. I già distillati restano **9**.

### Cosa NON è stato fatto, di proposito
**Nessuno dei 48 buchi è stato implementato.** Sono identificati e ordinati per priorità in `SINTESI.md`; la decisione
su cosa installare si prende con l'utente. Nessuna strategia importata, nessuna pre-registrazione aperta, nessuna
decisione esistente riaperta.

---

## 2026-09-15 — Ripresa dopo 19 giorni: il fade resta acceso **per scelta**, trade2sync **in prova**, secondo distillamento Quant Guild a **cattura ampia**

**Stato trovato — verificato in MT5, non nel repo.**
- L'EA fade ha continuato a girare: da 36 a **80 trade chiusi in universo**, tutti a valore **zero**
  per la decisione del 27/08. Dopo il 27/08 **19 ingressi su 39 (49%)** sono entrati a mercato
  (rischio fino a 3,84×, RR fino a 1:0,04): la patch del 27/08 aveva sistemato i pendenti orfani,
  **non** il ramo a mercato.
- `analysis/ops/weekly_healthcheck.py` riportava *"Stadio 2: N valido = 80/200"* per un test
  **azzerato**. Corretto, insieme a due difetti: il blocco `silent` che la patch del 27/08 non aveva
  mai toccato (lo `str.replace` senza `assert` era fallito in silenzio) e `--stdout` sulla console
  cp1252. Report in [`docs/health/2026-09-15.md`](docs/health/2026-09-15.md).
- Il copier del mentore (magic 27050) **non ha mai operato** sul conto 7396683: il deploy su VPS non è
  andato a buon fine per problemi tecnici e di tempo. **Resta aperto.**

**Decisione 1 — il fade resta acceso, per una ragione precisa.** Scelta dell'utente: VPS già pagato,
e con l'holdout della famiglia bruciato **i trade live sono gli unici dati fuori campione** che il
fade avrà mai. Il campione è in realtà **due campioni, separabili ex-ante dal tipo di ordine**:

| | trade finora | misura | previsione già scritta il 27/08 |
|---|---|---|---|
| riempiti da pendente | ~46 | il fade onesto (variante SKIP) | E[R] fra −0,250 e −0,027 |
| entrati a mercato | ~36 | il ramo rotto (variante LIVE) | E[R] fra −0,319 e −0,204 |

Il secondo confronto verifica anche **il nostro modello del fill**, qualunque sia l'esito del primo.
Per questo l'EA **non si ripara**: i pendenti arriverebbero allo stesso ritmo e si perderebbe il
secondo test. Limite da dichiarare: una sola posizione per strumento, quindi un trade a mercato
aperto blocca i setup successivi e assottiglia il campione onesto.

⚠️ **Condizione**: la regola di valutazione va scritta **prima** di guardare gli esiti. **Nessuno ha
guardato equity o P&L** (utente, 2026-09-15; da parte mia nessun esito mai calcolato) → la finestra
pulita è ancora aperta. La rivalutazione è il **trial #3, l'ultimo** della famiglia: pre-registrazione
da scrivere.

**Decisione 2 — trade2sync in prova, non adottato.** Copier Telegram→MT5 interamente in cloud (niente
VPS, EA o terminale). Rischi: tiene una **sessione Telegram completa** e la **password master MT5**;
elimina il nostro gate anti-slippage e il registro dello scarto in pip; gestione dei messaggi
successivi non documentata; versione cloud uscita a maggio 2026. Prova: **un mese di Basic mensile**
($39,99) su **conto MT5 demo dedicato** (lo storico MT5 diventa il log autorevole e lo scarto lo
calcoliamo noi) e **account Telegram dedicato**. Criteri fissati prima: quota di segnali copiati su
quelli pubblicati · scarto in pip · gestione dei messaggi successivi · mappatura dei suffissi. Il
nostro `signal_copier` resta il piano B.

**Decisione 3 — Quant Guild: cattura ampia.** Principio dell'utente: nelle distillazioni **non si
cerca solo ciò che serve a quello che abbiamo** — sarebbe superficiale, non sappiamo quali strumenti
serviranno. L'output è un **catalogo** (definizione, domanda, assunzioni, limiti, stato nel repo,
rilevanza), dove la rilevanza **classifica e non esclude**. Perimetro: 248 video + 2 live; **8 già
distillati** (#14, #29, #31, #32, #41, #43, #44, #76); gruppo 1 (81 video, nucleo matematico)
distillato; gruppo 2 (calcolo stocastico e opzioni, ~45) **scaricato, non distillato ora**; gruppo 3
(programmazione) letto per strumenti; video personali e reaction esclusi.

**WIP**: `docs/VPS_COPIER_SETUP.md` tolto dal repo (resta sul disco, aggiunto a `.gitignore`).

---

## 2026-08-27 (2) — **Il fill fantasma**: il +0,31R del FADE e il −0,44R della continuazione sono lo **stesso artefatto con due segni**. Forward **azzerato**, i 36 trade contano **0**

> **La voce più importante del mese.** Non boccia una strategia: **invalida il modo in cui abbiamo
> misurato un'intera famiglia per due mesi**, in entrambe le direzioni.

### 1. Da dove è partito: un'osservazione dell'utente su un ordine live

L'utente ha notato un ordine GBPUSD aperto con **RR rovesciato, 3:1 invece di 1:3**. Verificando
tutti gli ingressi del forward in MT5:

| tipo di ordine | n | rischio reale / inteso | RR reale |
|---|---|---|---|
| `BUY_STOP` / `SELL_STOP` | 26 | **1,00×** | **1:3** — corretto |
| `BUY` / `SELL` a mercato | 17 | **1,3× – 4,0×** | da 1:2,1 fino a **1:0,00** |

**17 su 43 ingressi in universo (40%).** Esposizione aperta misurata **2,00% dell'equity** contro
l'1,00% da specifica. Causa in [`mql5/nxt_fade.mq5`](mql5/nxt_fade.mq5) (~430-450): se al momento
dell'arm il livello è già stato superato, l'EA rinuncia al pending ed entra **a mercato**, ma
mantiene SL/TP calcolati sull'entry **teorica** e il volume da `ComputeVolume(|entry - sl|)`.

Nei casi peggiori il TP risulta **già praticamente toccato** (1:0,00): una vincita quasi certa con
una perdita da 4R attaccata dietro. **Skew negativo che fabbrica un win-rate alto.** L'aritmetica
che l'utente ha messo in chiaro: a 1:3 il break-even è **25%**, a 3:1 rovesciato serve **75%**.

### 2. Perché succede: 6 ore di cecità obbligatoria

Lo swing di fine è un **frattale a K=5 barre per lato**: è noto solo alla **chiusura** della barra
`b+K`, quindi la prima barra azionabile è `b+K+1`. In quelle ~6 ore il prezzo fa **esattamente il
ritracciamento al 50% che vogliamo tradare**. Misurato: **il 46,1% dei setup ha il livello già
oltrepassato** quando abbiamo il diritto di guardarlo.

### 3. Il difetto NON è dell'EA: è del backtest

[`analysis/nxt/closure.py`](analysis/nxt/closure.py) concede il fill al prezzo `entry` ogni volta
che una barra successiva lo **tocca**. Se il prezzo è già oltre, il fill viene concesso
**comunque, al livello** — un prezzo che il mercato aveva lasciato indietro prima che potessimo
agire.

> **Non è look-ahead di INFORMAZIONE** (il pivot è confermato correttamente): **è look-ahead di
> PREZZO.** Si transa a un livello disponibile solo *prima* di poter agire.

Il ramo a mercato dell'EA è il **tentativo goffo di gestire un caso che il backtest cancellava**.
Il backtest si regala il fill migliore esattamente dove il live prende il peggiore.

### 4. La misura — [`analysis/nxt/entry_fill_audit.py`](analysis/nxt/entry_fill_audit.py)

E[R] in unità di rischio **inteso**, **intervallo su 4 convenzioni** (pess/opt × la barra di fill
può stoppare o no). Mai un punto: la terza convenzione vale più delle altre due insieme.

| variante | n | E[R] intervallo | BCa95 agli estremi |
|---|---|---|---|
| **BASE** — com'è oggi | 10.218 | **[+0,409 ; +0,521]** | [+0,373;+0,444] · [+0,484;+0,558] |
| **SKIP** — solo i riempibili | 5.506 | **[−0,250 ; −0,027]** | [−0,287;−0,209] · [−0,073;+0,017] |
| **LIMIT** — aspetta il ritorno al livello | 9.189 | **[−0,191 ; −0,039]** | [−0,222;−0,160] · [−0,075;−0,002] |
| **RECENTER** — a mercato, geometria ricentrata | 10.218 | [−0,241 ; −0,075] | |
| **LIVE** — quello che fa l'EA | 10.218 | **[−0,319 ; −0,204]** | |

Finestra comune 2020→ (i sei feed non partono insieme: FX dal 2012, indici e oro dal 2020):
**identici**. Non è un effetto di periodo.

**LIMIT è il maggiorante della famiglia ottenibile** — costruito apposta per dare alla strategia
la sua occasione: se il livello è già passato, metti un limit e aspetti che il prezzo torni, fill
esatto a `entry`, geometria 1:3 intatta, finestra più generosa della spec. **Negativo in tutte e
quattro le convenzioni.**

**La corroborazione decisiva**: BASE è positivo in **15 anni su 15** e **6 asset su 6**; SKIP è
positivo in **0 su 15** e **0 su 6**. Un edge presente in ogni singolo anno e ogni singolo
strumento, che sparisce togliendo i fill non ottenibili, è **meccanico** — nessuna anomalia di
mercato rende lo stesso ammontare nel 2013 e nel 2020, su FX e su indici.

### 5. Il riesame del 2026-08-14 — [`analysis/nxt/excursion_recheck.py`](analysis/nxt/excursion_recheck.py)

`excursion.py` usa **lo stesso identico fill** nel braccio reale, ma il suo controllo random entra a
`C[k]`, la chiusura di una barra: **un prezzo sempre disponibile**. Il fantasma sta da un solo lato
del confronto. Seconda asimmetria indipendente: il reale cammina da `j = f` (la barra di fill può
stopparlo col range **pre-ingresso**), il random da `k+1`.

| | R terminale | gap vs random a convenzione omogenea |
|---|---|---|
| **BASE** (riproduce il −0,405 registrato) | **−0,410** [−0,484; −0,332] | −0,316 |
| **SKIP** (solo fill ottenibili) | **−0,056** [−0,177; +0,072] | **+0,038** |
| **SKIP+SYM** (entrambe le asimmetrie tolte) | **−0,006** [−0,137; +0,130] | **−0,027** |

R terminale dei fill **non ottenibili**: **−0,824**. Dei fill **ottenibili**: **−0,056**.

> **La lettura (2) del 14/08 è falsificata.** *"L'entrata distrugge ~0,4R rispetto alla moneta, è
> alpha negativo misurato"*: no. Con fill ottenibili l'entrata è **indistinguibile dal random**.

> **La lettura (3) è falsificata, ed è la più grave.** Il 14/08 presentava come *"due misure
> indipendenti"* il −0,4R della continuazione e il +0,35R del fade. **Non sono indipendenti: sono lo
> stesso artefatto visto dai due lati.** Il fade vende al livello dove la continuazione compra, quindi
> il fill non ottenibile che penalizza l'una avvantaggia l'altra **per costruzione**. Invertire la
> posizione inverte il segno del fantasma — non scopre un edge.

### 6. La sintesi

> Continuazione **−0,44R** (NO-GO 2026-07-17) e fade **+0,31R** (LEAD) sono **lo stesso fantasma con
> due segni opposti**. Sotto, con fill ottenibili, ci sono **zero e zero**.

Ne consegue che anche il NO-GO del 17/07 era **troppo pessimista**, per lo stesso motivo per cui il
LEAD era troppo ottimista. Non è che avevamo un edge e l'abbiamo perso: **non abbiamo mai misurato
l'entrata**, in nessuna delle due direzioni.

### 7. Decisioni dell'utente (2026-08-27)

1. **Forward AZZERATO.** Non "fermato per via del backtest": l'EA **non stava eseguendo la strategia
   pre-registrata sul 40% dei trade** — il ramo a mercato viola simultaneamente i tre parametri
   congelati del §2 (SL 1R, TP 3R, R=28,6%). È il caso previsto dal
   [§4.3 della pre-registrazione](docs/NXT_FADE_FORWARD_PREREGISTRATION.md): *"qualunque modifica
   azzera il test e ne apre uno nuovo"*. **Vincolo speculare**: riparare l'EA e proseguire lo stesso
   contatore di Stadio 1 è **vietato dalla stessa clausola**.
2. **I 36 trade contano 0.** Non entrano in nessun verdetto. Lo Stadio 1 non esiste più.
3. **Trial annullato.**
4. **La famiglia si chiama FADE**, non NXT: il forward live era a tutti gli effetti solo fade.
   ⚠️ **Il rinominare non azzera il contatore**: il fade è nato **invertendo** la continuazione sugli
   stessi dati, stesso albero di ricerca. Restano **2 trial su 3** e l'**holdout già aperto**.

### 8. Contabilità e cosa resta aperto

**Trial consumati: 0.** Entrambi gli audit sono verifiche di integrità dell'esecuzione
([`LIFECYCLE §3`](docs/STRATEGY_LIFECYCLE.md), riga *"modellazione più realistica di
costi/slippage/esecuzione → No"*), stessa classificazione che il 14/08 si era già dato.
⚠️ **Clausola sospensiva**: nel momento in cui una variante venisse **scelta** per proseguire
("mettiamo il LIMIT nell'EA"), quello sarebbe un cambio di regola dopo aver visto l'esito →
**trial #3, l'ultimo del budget**.

**Non rimisurato, e va detto**: (a) il confronto **oracolo/MFE** del 14/08 (+1,709 vs +3,149) usa lo
stesso braccio reale contaminato — l'ho falsificato solo sull'R terminale; (b) **né +0,354 né
+0,308 sono verificati sotto una convenzione unica** — quattro motori (`backtest.py`, `closure.py`,
`weekend.py`, `entry_fill_audit.py`) implementano quattro convenzioni diverse sullo stop; (c) l'EA
gira ancora e continua a produrre trade che non contano.

**Debito di protocollo aggiornato** (vedi [`BACKLOG_RICERCA §E`](docs/BACKLOG_RICERCA.md)): serve
**una** primitiva `resolve_trade()` in `core/`, con la convenzione sulla barra di fill e sul gap
oltre lo stop come **parametri espliciti**. La quadrupla reimplementazione è precisamente il
meccanismo che ha generato questa ambiguità.

**Metodo che ha funzionato, e va ripetuto**: la misura è stata sottoposta al
[`quant-gatekeeper`](.claude/agents/quant-gatekeeper.md) **prima** di essere registrata. Ha emesso
**BLOCCA** con 4 bloccanti — fill del gap oltre lo stop non modellato, asimmetria intrabar sulla
barra di fill, look-ahead residuo di una barra, copertura confondata col periodo. Tutti e quattro
fondati, tutti riparati. La **direzione** ha retto; la **magnitudo** no: la prima stesura diceva
−0,246R, il valore onesto è un intervallo che arriva a −0,027.

**Link:** [`analysis/nxt/entry_fill_audit.py`](analysis/nxt/entry_fill_audit.py) ·
[`analysis/nxt/excursion_recheck.py`](analysis/nxt/excursion_recheck.py) ·
[`docs/NXT_FADE_FORWARD_PREREGISTRATION.md`](docs/NXT_FADE_FORWARD_PREREGISTRATION.md) §11

---

## 2026-08-27 — **ORB spento** (A3 chiusa in F1) · e il difetto che teneva **US500 congelato da 27 giorni**

### 1. ORB: spento dall'utente, A3 chiusa

Verificato in MT5: **zero posizioni, zero pendenti** con magic 26052, ultimo ordine 2026-08-25
20:33. Chiusura pulita. La scelta F1/F2 di [`BACKLOG_RICERCA §F`](docs/BACKLOG_RICERCA.md) si
risolve in **F1 — lasciare chiuso**, per una via diversa da quella scritta: non *"non lo avviamo"*
ma **"era acceso a nostra insaputa e lo spegniamo"**. Razionale invariato: famiglia **NO-GO su
14,5 anni** (NAS100 −0,056, SPX500 −0,137), **holdout gia' bruciato**, e la domanda che il forward
doveva risolvere ha ricevuto il 2026-08-14 una risposta piu' economica (lo stesso salto pre/post-2020
compare **col segno opposto** su una strategia scorrelata).

**I 10 trade chiusi non vengono letti, ed e' una scelta.** Il forward non era pre-registrato: non ha
regola di stop, quindi non c'e' optional stopping da violare — ma non c'e' nemmeno nulla da
imparare. **n=10 non ha potere contro un verdetto su 14,5 anni**; se il P&L fosse positivo
produrrebbe solo pressione a riaprire una famiglia con l'holdout esaurito. Il numero non e' stato
calcolato. Le **condizioni di riapertura** (Cimbali vs Siento, con predizioni divergenti su
lato/epoca/ora/calendario) restano in `§F` e sono l'unica porta.

### 2. Il difetto trovato mentre si spegneva l'ORB: **un riavvio dell'EA congela lo strumento**

**Come e' emerso.** L'utente ha cancellato a mano un pendente US500 fermo dal 2026-07-31 per vedere
se lo strumento si sbloccava: **si e' sbloccato**, l'EA ha piazzato un nuovo ordine tre minuti dopo.
Non era una stranezza: era il sintomo.

**Il meccanismo, verificato nel sorgente.** In [`mql5/nxt_fade.mq5`](mql5/nxt_fade.mq5) la scadenza
del pending (**48 barre H1**, parametro CONGELATO della pre-registrazione) si calcola da
`g_pending_swingend`, una variabile che **vive solo in RAM** e che `OnInit()` **non ripristinava**.
Dopo ogni riavvio — ricompilazione, restart del terminale, **spostamento sul VPS Windows** — tornava
a `0`. La catena:

1. `iBarShift(symbol, H1, 1970-01-01)` ritorna **−1**;
2. la condizione `-1 > 48` e' **falsa** -> il pending orfano **non scade mai**;
3. la riga successiva e' `return;  // un solo setup attivo per volta` -> **nessun nuovo setup viene
   mai armato su quel simbolo**.

Un solo ordine non riempito, dopo un riavvio, **spegne lo strumento in modo permanente e silenzioso**.

**Impatto misurato sul forward in corso.**

| strumento | congelato da | a | durata | effetto |
|---|---|---|---|---|
| **US500** | 2026-07-31 20:00 | 2026-08-27 13:57 (sblocco manuale) | **27 giorni** | 0 trade: **non erano segnali mancanti, era lo strumento spento** |
| **XAUUSD.cyr** | 2026-08-21 04:00 | **tuttora** | **6 giorni** | pendente vivo adesso, oro fermo |

**Cosa NON tocca.** I riempimenti avvenuti restano dentro la finestra: su 72 ordini riempiti in
universo, attesa **mediana 0,0h**, solo 3 oltre le 24h di calendario e tutti spiegati dal weekend
(le 48 sono **barre**, non ore). Il difetto **sottrae** trade, non ne aggiunge di spuri: colpisce
**breadth e composizione**, non i valori di R gia' raccolti. **N valido resta 36/50.**

**Aggravante di metodo.** Il difetto si attiva **quando interveniamo** — ogni nostra riparazione
(il riaggancio `.r` del 12-13/08, il trasloco sul VPS) creava un orfano. Il caveat di composizione
gia' in prereg §9 va quindi letto piu' duro: la copertura non e' solo disomogenea, e' **correlata
alle nostre manutenzioni**.

**La correzione** (`mql5/nxt_fade.mq5`, 2026-08-27): `OnInit()` ricostruisce `g_pending_swingend`
dall'ordine vivo usando `ORDER_TIME_SETUP` come proxy dello swing (scarto <= 1-2 barre su 48, mai in
difetto); e il test di scadenza tratta `age < 0` come **scaduto**, mai come *"tienilo per sempre"*.
Richiede **ricompilazione in MetaEditor e riattacco dell'EA**.

**Trial consumati: zero.** Spegnere un forward su famiglia NO-GO non e' una modifica di regole; la
correzione dell'EA e' un **bug fix** che riporta l'esecuzione **dentro** la spec congelata invece di
allontanarla ([`LIFECYCLE §3`](docs/STRATEGY_LIFECYCLE.md)).

### 3. Anche il mio health-check leggeva una fonte parziale

`weekly_healthcheck.py` usava solo `history_orders_get()`, che **non vede i pendenti vivi**: US500
risultava *"in universo ma senza alcun ordine"* mentre ne aveva uno attivo. Ora conta anche
`orders_get()`/`positions_get()`, calcola la breadth includendoli e **segnala i pendenti fermi da
oltre 3 giorni** — che e' esattamente la firma di questo difetto. **Breadth corretta: 6/6.**

**Link:** [`docs/health/2026-08-27.md`](docs/health/2026-08-27.md) ·
[`docs/NXT_FADE_FORWARD_PREREGISTRATION.md`](docs/NXT_FADE_FORWARD_PREREGISTRATION.md) §10 ·
[`docs/BACKLOG_RICERCA.md`](docs/BACKLOG_RICERCA.md) §A2/§A3/§F

---

## 2026-08-24 — Bucket A verificato voce per voce. Il forward FADE **gira ma il campione è contaminato**; il test mentore era **già superato**; il forward ORB **non esiste**

**Origine.** Dopo aver scoperto il 23/08 che il forward ORB era citato come "in corso" senza essere
mai stato implementato, ho verificato **uno per uno** gli altri binari del bucket A invece di
fidarmi del registro. Due voci su sei erano descritte male, in direzioni opposte.

**A4 — segnali mentore: era GIÀ CHIUSA e SUPERATA.** Il mio backlog diceva *"da verificare se il
forward è partito"*. Falso: il test OOS pre-registrato è stato **eseguito e superato il 2026-08-07**
(131 segnali 15/06→07/08, win-rate 63,0% vs 35,0% del lato casuale, differenza appaiata +0,277
BCa95 [+0,193; +0,353], E[R] +0,194 BCa95 [+0,079; +0,289]). È il **primo verdetto positivo su un
test pre-registrato** del workspace.

**A2 — forward FADE: gira davvero, ma il campione non è pulito.** Health-check eseguito
([review](docs/reviews/forward-fade-healthcheck-2026-08-24.md)). **N valido 29/50** allo Stadio 1,
breadth 4/6. Quattro difetti, tutti di **esecuzione**, nessuno di strategia → per
[§3](docs/STRATEGY_LIFECYCLE.md) **non consumano trial**:

1. **197 ordini non inviati** fra il 2 e il 21 agosto — `[nxt_fade] <SIMBOLO> arm fallito, err=4756`,
   su chart a **nome semplice** (`EURUSD`, `USDJPY`, `GBPUSD`) mentre il conto negozia i simboli
   **con suffisso** (`.r`), a cadenza **oraria esatta**. EURUSD ha **1 ordine storico contro 64
   tentativi falliti**. È la **recidiva del bug che ha generato lo script stesso** (tre settimane su
   simboli non negoziabili, agosto). Effetto: il campione perde in modo **sistematico** i segnali dei
   **major FX**, cioè — per il lead del playground — proprio il gruppo con l'aspettativa peggiore →
   il campione superstite è spostato verso gli strumenti **più volatili**, che è la direzione che
   **gonfia** l'E[R].
2. **Strumenti fuori universo**: BTCUSD (7 ordini, 2 chiusi) ed EURGBP.r (2). Esclusi dal conteggio,
   ma continuano a generare ordini e consumare margine.
3. **Dropout per margine non casuale**: 8 su 92 (8,7%), `deleted [no money]`. Colpisce i setup con lo
   **stop più stretto** (a rischio costante = volume maggiore = margine maggiore), che sono anche
   quelli col miglior payoff potenziale.
4. **Rischio fuori specifica**: GBPUSD.r a **0,63% contro 0,25%** atteso. Multipli di R non
   confrontabili fra loro.

**Non guardato di proposito: il P&L.** La regola di stop è **N e data**, mai il cumulato: guardarlo
adesso sarebbe optional stopping.

**Decisione aperta (dell'utente).** Riparare è obbligatorio e gratuito in termini di trial. Resta da
scegliere cosa fare dei **29 trade già raccolti**: tenerli e dichiarare la contaminazione nel report
finale, oppure **azzerare lo Stadio 1** e ripartire pulito (~30 trade e ~un mese di costo).
La seconda è quella coerente col protocollo — il forward è l'**unica fonte rinnovabile di dati
puliti** ([§2](docs/STRATEGY_LIFECYCLE.md)) — ma non la decido io.

**C2 non è più una decisione.** *"Reinserire BTCUSD nel FADE?"* era formulata come scelta aperta:
sta **già operando fuori universo**. Non c'è da decidere, c'è da staccare l'EA.

**Debito confermato, secondo caso in due giorni.** Lo strumento esisteva e ha trovato tutto in dieci
secondi — **ma nessuno lo eseguiva**. Come per l'ORB, il problema non è la mancanza dello strumento:
è che **lo stato reale dei binari non è osservabile senza cercarlo a mano**. Minimo indispensabile:
health-check **settimanale**, con output datato e versionato, così che N e anomalie abbiano una serie
storica invece di una fotografia.

---

## 2026-08-22 — Funnel Chart Fanatics **chiuso**: 45 video letti per intero, **zero strategie importabili**, cinque caselle vuote identificate, quattro conferme esterne del lead playground. Nessuna pre-registrazione nuova.

**Cosa è stato fatto.** Tutti i **45 video** del canale (74,7 h, ~608.000 parole) sono stati letti
**per intero, uno alla volta**, senza compressione automatica — la scelta di metodo presa il
2026-08-17 dopo che il compressore lessicale aveva perso 4 regole numeriche su 5 su una trascrizione
reale. Schede per video in
[`_triage/blocco-A1/A2/B1/B2/C1/C2/C3/C4/D.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/),
consuntivo in [`_triage/SINTESI.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/SINTESI.md),
riga di registro in [`_INTAKE.md`](fondamenti_tecnici/_INTAKE.md).

**Esito complessivo.** **Nessun candidato nuovo.** Ripartizione: **19** video in famiglie già
falsificate (livelli/zone, FVG, order block, sweep, Fibonacci, numeri tondi, VWAP/POC, ORB,
stagionalità), **12** non testabili con i nostri dati (order flow = tick + book; oppure universo
small cap USA), **11** reference (metodo, rischio, contesto), **1** già testato → NULL (Okala
80/20 → round grid), **2** già distillati.

**CINQUE OGGETTI NUOVI — identificati, non proposti.**
1. **Condizione di STRUTTURA sull'estensione estrema.** Due fonti indipendenti — Marius Stamatiou
   (+291% alle US Investing Championships) e Kyle Williams (7 M$ verificati) — concordano, senza
   essersi mai parlate, che **conta la forma più dell'ampiezza**: pochi grandi movimenti con
   **range in espansione** e **volume in espansione** si invertono; tanti piccoli movimenti con
   volume calante no. Entrambe aggiungono una **finestra di invalidazione temporale** (2 giorni /
   3 tentativi). **Misurabile sui nostri dati** — servono solo range e volume — e specifica il
   candidato "estensione estrema → inversione" che avevamo dal blocco A.
2. **Le due spec mancanti di Kichev**, emerse solo dalla lettura integrale: *breakout = espansione
   di volatilità* (~2x la media delle ultime 5) con **uscita a tempo** 2-5 giorni; *mean reversion
   = scostamento dalla media a 5 giorni* con uscita a tempo 1-4 giorni. La seconda è la **forma
   canonica del nostro lead FADE**, scritta da una fonte esterna **prima** che la trovassimo — cioè
   esattamente ciò che serve per ri-pre-registrare una regola data-derived.
3. **La domanda conferma-sì / conferma-no sul FADE.** Kichev è l'unica voce del funnel, contro
   sette, a dire di **non** aspettare la conferma su una mean reversion. Non è una famiglia nuova:
   è una **variante di esecuzione** su un lead già in forward test.
4. **Casella vuota LVN, verificata nel codice.** `analysis/level_research/detectors.py:107-148` +
   `VOLUME_CONCEPTS = ["poc","vwap","avwap"]`: la ricerca v2 (48 celle, NULL) ha testato i nodi ad
   **alto** volume (POC/VAH/VAL). I **low volume node non sono mai stati testati**, e non sono una
   variante ma **l'ipotesi complementare con meccanismo opposto**. Tre fonti indipendenti (Carmine
   Rosato, Fabio Valentini, Yush).
5. **Casella vuota trend line inclinate.** I 384 trial hanno testato **solo livelli orizzontali**.
   3 fonti ci costruiscono sopra il metodo; **1 (Ariel) le rifiuta con la nostra stessa
   motivazione** — l'ambiguità del tracciamento. Buco reale, prior basso.

**DUE PORTE CHE RESTANO CHIUSE — deciso adesso.**
- **Livelli condizionati** (a un evento macro in calendario, al regime, alla struttura di timeframe
  alto): 3 fonti lo sostengono. **Non si riapre**: condizionare moltiplica lo spazio di ricerca su
  una famiglia con **384 trial di NULL**, e il calendario macro è il posto **più pubblico e più
  affollato** del mercato, cioè l'opposto del playground. Serve evidenza esterna **quantitativa**;
  aneddoti scelti a posteriori non lo sono.
- **ORB.** Andrea Cimbali afferma che *"funziona da 20 anni"* sugli indici USA — **esattamente** il
  nostro filone (`analysis/opening_range/`, apertura cash 09:30 ET, M5, 14,5 anni, NAS100/SPX500 →
  NO-GO). Non riapre nulla: nessun campione, nessun baseline, e lui lo opera **con l'order flow
  sopra**, dichiarandolo (*"non ho bisogno di aspettare il breakout"*). **Ma il suo razionale
  economico** — flusso strutturale d'acquisto sugli indici + market maker obbligati a fornire
  liquidità — **va allegato al forward ORB già in corso** come ipotesi dichiarata, a costo zero: se
  il forward risulta positivo sappiamo *perché* potrebbe esserlo; se negativo abbiamo falsificato
  anche il meccanismo, non solo il pattern.

**QUATTRO CONFERME ESTERNE INDIPENDENTI DEL LEAD PLAYGROUND** (nostro ρ = +0,857, p=0,006): Kichev
(classifica per liquidità decrescente: forex → commodities → small cap → crypto), Desi Trades
(*"funziona solo nei pochi mesi in cui il VIX è alto"*), Carmine Rosato (*"opero dove non c'è molta
liquidità, è lì che sta l'edge"*), Fabio Valentini — **top 3 Robbins Cup, +500%/12 mesi** — (*"il
breakout fallisce dentro la balance area e funziona fuori"*). Quattro vocabolari diversi, **una sola
forma**. ⚠️ Nessuna delle quattro è evidenza statistica: **spostano il prior, non i dati**. La
nostra resta l'unica con un numero.

**LE FONTI CONVERGONO SUL FADE, MAI SULLA CONTINUAZIONE.** Quattro fonti descrivono meccanismi che
coincidono con la direzione che abbiamo misurato **+0,31R**. L'unica che descrive la continuazione
(Omar / MBB Trader, 30 M$ di funding dichiarato) descrive **livello per livello — 0,62 / 0,705 /
0,79** — la strategia che abbiamo pre-registrato e misurato a **−0,44R** su 6 asset e 14 anni, con
win rate **13,3%** contro il 60-70% dichiarato dalla fonte originale.

**DISTRIBUZIONE DEI CLAIM** (raccolta prevista dal mandato d'intake, ora completa). I claim alti
(>80%, 85-90%, 74%, 70-80%, 65-70%) **non sono mai accompagnati** da campione, periodo, baseline o
taglia del rischio. I claim bassi spesso lo sono: Trader Mayne *"sono fortunato se ne vinco metà"*
con minimo 2:1 come vincolo d'ingresso; Z *"l'élite sta fra 50 e 55%"*; Desi **65% con 5-6 perdite
di fila più volte l'anno**; Carmine **30-33% con R:R 7-8:1 e rischio fisso** — l'unico caso in cui i
tre numeri necessari a verificare il conto sono pubblicati insieme. **Quattro su quattro dei claim
alti che abbiamo potuto misurare sono collassati** (60-70%→13,3%; 80-90%→~53%; 90%→~20%;
65-70%→NULL). Correlazione netta e riutilizzabile: **onestà statistica e qualità del razionale
economico vanno insieme.**

**CORREZIONE a un conteggio intermedio.** La convergenza "stop largo" registrata nei consuntivi B2
e C2 vale **2-3 fonti indipendenti, non 5-6**: tre delle occorrenze erano trader di **opzioni** che
descrivevano la **stessa** causa — la non-linearità del premio (delta + gamma + IV), spiegata nel
corso di Usman Ashraf — non tre osservazioni distinte. Il fatto resta coerente col nostro **12,7%
di stop NXT che aprono oltre il livello**, ma non ha il peso che sembrava avere sommando fonti con
causa comune.

**Nota trasversale sul formato.** Le 6 sessioni **in diretta** (~216.000 parole, il 36% del corpus)
**non hanno prodotto una sola regola** che non fosse già enunciata sulla lavagna prima
dell'apertura. La diretta mostra esecuzione e gestione, mai la formazione di una regola — che per un
processo dove le regole si scrivono **prima** di vedere i dati è la parte meno informativa in
assoluto.

**BUDGET E CHIUSURA.** Nessuna pre-registrazione nuova aperta. Il tetto di **1** previsto dal piano
di lettura resta speso dal playground; il budget esterno trimestrale resta a **2 di 2-3**.
**Il funnel è chiuso**: non si riparte su altri canali prima che i binari attivi (FADE forward, ORB
forward, copier, PAC) producano un verdetto. La prossima decisione — quali binari paralleli
configurare o avviare — è **da prendere insieme**, non implicita in questa voce.

---

## 2026-08-17 — Fonte "algo senza codice" (StrategyQuant X): **1 tassello distillato, metodo rifiutato**. Colmato il buco post-capitale del ciclo di vita.

**Fonte.** *Noel T.*, portafoglio di ~150 algoritmi costruiti con **StrategyQuant X** senza scrivere
codice — di fatto una **demo del software**. Grezzo in
[`insight_da_yt/noel_t_strategyquant_no-code_algo_2026-08-17.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/),
triage in [`_INTAKE.md`](fondamenti_tecnici/_INTAKE.md). Statistiche dichiarate (≈$1M di profitti)
**non entrate nel prior**, come da mandato.

**DISTILLATO — il buco che colma (l'unico tassello).** Il nostro
[STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md) copriva **solo nascita e morte prima del
capitale**: il loop finiva al verdetto e non diceva nulla su *cosa fare con una strategia già
operativa che peggiora*. Serve **adesso** (fade in forward, copier mentore verso il live) → nuovo
**§8bis: ritiro, incubazione, riattivazione**.

**Adattamento obbligatorio, non copia.** Il trigger della fonte è discrezionale — *"se perde per
qualche mese, riduci o spegni"* — ed è **optional stopping applicato al capitale**: la performance
di qualunque edge reale è rumorosa, quindi un criterio a sensazione spegne **sistematicamente dopo
il drawdown, cioè al minimo**, e riaccende dopo il recupero. Sostituito con una soglia **dichiarata
nella pre-registrazione prima del capitale**, ancorata al **percentile del maxDD della simulazione
Monte Carlo**: si ritira quando la strategia **esce dalla distribuzione attesa**, non quando "va
male". Stati: LIVE → INCUBAZIONE (gira in simulazione, continua a raccogliere dati) → rientro con
criterio dichiarato, oppure RITIRATA definitiva alla **seconda** uscita. Ritiro **immediato senza
incubazione** per razionale falsificato o difetto metodologico. **Vietato ritarare in incubazione**:
sarebbe p-hacking col capitale già in gioco.

**RIFIUTATO — il metodo.** Generare milioni di combinazioni e filtrare da **10.000 candidati a ~25**
è **mass data mining senza deflazione**. Il conto che lo mostra: con una catena di filtri di
stringenza plausibile (~0,25% di falsi passaggi complessivi) **il puro rumore produrrebbe ~25
sopravvissuti su 10.000** — cioè esattamente il numero osservato. Non dimostra che le sue strategie
siano rumore; dimostra che **il numero di superstiti, da solo, non porta informazione** se non si
conosce il tasso di falso positivo. Il flusso descritto ha OOS singolo + reshuffle e **nessun
controllo di molteplicità** (né DSR né PBO).

**CORREZIONE TECNICA** → [04_quant_metodologia §2b](fondamenti_tecnici/04_quant_metodologia/principles.md):
il "**Monte Carlo di robustezza**" che **rimescola l'ordine dei trade** conserva media, varianza e
ogni momento, e cambia solo il **percorso**. Misura la distribuzione del **maxDD** — utile per il
sizing e per le soglie di ritiro — e **non può rilevare l'overfitting**: se i trade sono il prodotto
di una selezione overfittata, riordinarli restituisce le stesse statistiche. Distinzione da tenere
ferma se mai valutassimo uno di questi tool.

**Strategie mostrate: SCARTATE entrambe.** *"Gold Rush"* (compra oro il giovedì) è
**calendario/stagionalità**, famiglia già **NO-GO** (TOM 2026-07-08, anomalia decaduta). La *"S&P
mean reversion"* (sopra SMA200, RSI(2)<20 in entrata, RSI>70 in uscita) è la **RSI(2) di Larry
Connors**, pubblicata intorno al 2008 e fra le più data-minate del retail — presentata come scoperta
del software; è **long-only su indice in una finestra rialzista**, cioè lo stesso **beta-trap** che
ha refutato il router momentum+MR. **Nessuna pre-registrazione**: il budget esterno resta a **2 di
2-3** usate nel trimestre.

**Tool: non adottato.** Il nostro collo di bottiglia non è "non sappiamo programmare" — abbiamo già
lo stack di validazione. SQX darebbe **ricerca di massa**, che è precisamente ciò che la nostra
dottrina evita, e senza le metriche che la renderebbero legittima.

---

## 2026-08-14 (3) — Rischio weekend sul fade: la regola "venerdì chiudo i profit" è **irrilevante**. Ma il fill dello stop era ottimista: E[R] **+0,354 → +0,308**

**Origine.** Domanda dell'utente: la sua regola manuale — *venerdì sera chiudo le posizioni in
profitto e lascio aperte solo quelle in perdita* — era mai stata analizzata sul fade? **No, mai**:
nessuna gestione weekend esiste nei motori, nella spec o nell'EA. Misurata con
[`analysis/nxt/weekend.py`](analysis/nxt/weekend.py). Diagnostica di esecuzione, **non** una variante
di strategia → **non consuma trial** ([STRATEGY_LIFECYCLE §3](docs/STRATEGY_LIFECYCLE.md)).
Riproduzione validata: n=10.290 ed E[R] assunto **+0,355** contro il +0,354 pre-registrato.

**1. Il fade quasi non vive nel weekend.** Holding **mediano 5 barre H1** (cinque ore); solo il
**10,5%** dei trade attraversa un fine settimana. Il `MAX_HOLD` di 20 giorni è un **tetto**, non il
comportamento tipico.

**2. I gap del weekend non sono avversi** (in R, col segno della posizione):

| | n | media | mediana | BCa95 | P(gap<0) |
|---|---|---|---|---|---|
| tutti | 1.123 | **−0,008R** | 0,000 | **[−0,063, +0,046]** | 49,0% |
| in profitto il venerdì | 872 | −0,043R | −0,004 | [−0,102, +0,018] | 51,0% |
| in perdita il venerdì | 251 | +0,113R | +0,005 | [−0,033, +0,254] | 41,8% |

Il gap medio è **indistinguibile da zero**. La separazione profitto/perdita *sembra* dare ragione
alla regola, ma **nessuna delle due CI esclude lo zero** e il pattern è un **artefatto di
condizionamento**: selezionare "le posizioni in profitto adesso" seleziona quelle già mosse a
favore, e qualunque componente di ritorno alla media — o solo rumore — produce restituzione
parziale. **Si vedrebbe identico condizionando su un martedì: non è un effetto del weekend.**

**3. Verdetto sulla regola: irrilevante in aspettativa, controproducente se implementata.**
Beneficio descrittivo: evitare −37,1R sui vincenti + tenere +28,3R sui perdenti su 10.290 trade =
**+0,0036R per trade, ~1% dell'E[R]**, dentro CI che includono zero. Riaprire 872 posizioni allo
spread della strategia (~0,058R a giro, dallo stress 1×/3× già in repo) costerebbe **~50R contro
~37R di beneficio**. Ed è **strutturalmente rovesciata**: col BE a +2R un vincente ha già lo stop a
pareggio (rischio weekend ~nullo) mentre un perdente ha 1R pieno esposto → la regola **chiude ciò
che rischia meno e tiene ciò che rischia di più**, firma della *disposition effect*. Se la
preoccupazione è il gap non copribile, la risposta coerente è "chiudo **tutto** il venerdì", non
"chiudo i vincenti". **Ambito**: vale per QUESTA strategia (H1, mediana 5 ore, BE 2R, 6 strumenti
liquidi); non si trasferisce a una strategia che tiene davvero per settimane.

**4. IL PROBLEMA VERO, trovato altrove — correzione di un numero pre-registrato.** Il backtest
assume che lo stop si riempia **esattamente** al livello. Nella realtà il **12,7% degli stop apre
già oltre**: fill vero **−1,288R** contro **−0,752R** assunto (scarto −0,537R su quelli).
→ **E[R] del fade: +0,355 → +0,308** (−0,047R, **taglio del 13%** sul numero pre-registrato).
Ma solo il **4,8%** di quei salti avviene dopo un weekend: **il gap-attraverso-lo-stop è per il 95%
un fenomeno infrasettimanale.** La preoccupazione era sul posto sbagliato.
È un **fix di modellazione dell'esecuzione**, non una ritaratura: non consuma trial, e può solo
peggiorare. **Il verdetto non cambia** (resta LEAD, resta positivo), ma **stringe il margine dello
Stadio 2**, che richiede lower bound BCa > 0. Il forward va confrontato con **+0,31R, non +0,35R**.

**5. Varianza sì, aspettativa no.** Un gap oltre **0,5R nel 26,9%** dei weekend e oltre **1R nel
10,3%** — un weekend su dieci il salto supera l'intero stop. Rileva per il **daily drawdown** di una
prop, non per l'expectancy.

**6. Corretto un assunto operativo.** [PROP_FIRM_CRITERIA §1.3](docs/PROP_FIRM_CRITERIA.md)
classificava il fade come **swing** per via del cap a 20 giorni: la distribuzione reale dice mediana
5 ore e 10,5% di trade con weekend. Il criterio "holding weekend consentito" **resta valido ma pesa
molto meno** — una firm che obbliga a chiudere il venerdì amputerebbe ~1 trade su 10, non la
strategia. **Il forward in corso non è stato toccato**: nessun cambio di regola in corsa.

---

## 2026-08-14 (2) — Trend Donchian: coda aperta **NO-GO** · **playground = LEAD** (il campo era sbagliato)

**Decisione.** Fonte esterna *Pavel Kichev*, pre-registrata in
[docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md](docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md),
motori [`analysis/trend/`](analysis/trend/), verdetto
[docs/reviews/trend-exit-playground-2026-08-14.md](docs/reviews/trend-exit-playground-2026-08-14.md).
Due domande in un solo esperimento: **Q1** la coda aperta (domanda dell'utente), **Q2** il claim
"l'edge retail vive sugli asset meno liquidi e più volatili".

**Dati nuovi (asset riusabile).** Feed **omogeneo** Dukascopy D1, **27 strumenti su 8 gruppi**:
per la prima volta nel workspace entrano **bond, energia, agricoli e metalli industriali** — il buco
che la pre-registrazione TSMOM aveva dichiarato ("USD-pesante, senza bond né commodities").

**Q1 — coda aperta: NO-GO.** Quattro uscite sulle **identiche** entrate, 3 lookback:

| lookback | **E1 trail SMA10** | E2 stop1R/3R | **E3 uscita a 20g** | E1 vs random |
|---|---|---|---|---|
| 50 | +0,015 | +0,067 | **+0,131** | −0,004 [−0,107, +0,098] |
| **100** | **−0,038** | +0,045 | **+0,110** | −0,076 [−0,202, +0,053] |
| 200 | −0,024 | +0,057 | **+0,137** | −0,125 [−0,269, +0,021] |

**Il trail è l'uscita peggiore o quasi in tutte e tre; l'uscita a tempo — la più stupida possibile —
è la migliore in tutte e tre.** A lookback 100 la differenza appaiata **E1 − E3 = −0,147, BCa95
[−0,285, −0,014]**. E1 non batte il random in nessuna variante → **kill-switch pre-registrato**.
Anni positivi 6/15; a 3× costi −0,100. **La risposta alla domanda sul trail non dipende dall'edge
dell'entrata**: il confronto è appaiato sugli stessi ingressi.

**W3 — il "post-2020" si ripresenta, COL SEGNO OPPOSTO.** pre-2020 E[R] +0,078 (vs random +0,010,
nulla); post-2020 **−0,208**, vs random **−0,323 [−0,487, −0,157]**. L'ORB era *negativo pre-2020 e
positivo post*; questo è *piatto pre-2020 e peggio del random post*. Due breakout della stessa
famiglia che si spezzano in **direzioni opposte alla stessa data** sono più coerenti con **due
estrazioni di rumore** che con una rottura di microstruttura → sposta il prior e **rafforza la
scelta di lasciar correre il forward ORB**, unico modo di risolverlo.

**Q2 — playground: SUPPORTATO → LEAD.** Spearman(vol di gruppo, E[R] di gruppo), n=8:
**ρ = +0,857, p = 0,0060**. Ordinamento: fx_cross −0,52 · fx_major −0,40 · index −0,12 · agri +0,24 ·
energy +0,40 · metal +0,46 · crypto +1,10. Controlli avversariali: il random da solo dà ρ +0,619
(p 0,062) → **una parte è meccanica**, ma il test **controllato** sulla differenza reale−random
tiene (**ρ +0,786, p 0,0135**); bootstrap sugli strumenti dentro i gruppi ρ mediano +0,786 CI
[+0,476, +0,952] **P(ρ>0)=100%**; senza crypto ρ +0,786 p 0,023; senza crypto+energia ρ +0,771
p 0,050 → **non trainato da un gruppo solo**.

**Perché LEAD e non GO**: (1) solo **3/8 gruppi positivi su ENTRAMBI i lati** — è in larga parte
lato lungo in una finestra di rialzo di commodities e crypto; (2) solo 2/8 gruppi individualmente
significativi; (3) n=8 punti; (4) W2 è per ~2/3 post-2020, dove il livello assoluto è cattivo;
(5) **la mia pre-registrazione non ha definito un holdout per Q2** — lacuna dichiarata, nessun gate
G2 superato.

**Cosa cambia davvero.** Non "abbiamo un edge su crypto e commodities": la regola Donchian è NO-GO.
Ma **sui major FX la stessa regola fa −0,47R PEGGIO del random, sui gruppi volatili fa meglio** →
il campo su cui abbiamo cercato per un anno (FX, indici, oro) è plausibilmente **il peggiore
possibile**, e la spiegazione arriva da una fonte che i nostri dati non li ha mai visti. Vale come
**direzione di ricerca**, non come strategia.

**Due difetti dei dati trovati e corretti PRIMA del test.** (a) Il D1 grezzo Dukascopy contiene
sessioni **parziali** di sabato/domenica (EURUSD: 761 barre domenicali a range mediano 0,137% contro
0,65% dei feriali) → diluiscono l'ATR, gonfiano ogni multiplo di R e riducono il "Donchian 100
giorni" a ~83 giorni reali; corretto fondendole nella barra feriale successiva (la crypto tratta
davvero 7 giorni). (b) Un mio bug nel fix restituiva la serie **in ordine temporale inverso**,
intercettato da un controllo di sanità. ⚠️ **Il feed broker legacy è invece PULITO** (258-260
barre/anno, zero domeniche): questo difetto **non contamina** NXT, ricerca livelli e TSMOM.

**Contabilità**: 12 trial dichiarati, famiglia trend **round 2 di 3**, **2ª di 2-3 pre-registrazioni
esterne** del trimestre.

---

## 2026-08-14 — "Grandi RR, niente TP, uscita a medie mobili": **KILL**. L'entrata è peggio del random.

**Decisione.** Idea dell'utente: individuare il minimo/massimo di un periodo (o di una sessione),
piazzare un ordine limite a una distanza fissa dall'estremo, stop sotto l'estremo, **niente TP**,
uscita all'incrocio di medie mobili. **KILL** senza arrivare alla pre-registrazione completa.
Addendum pre-registrato [docs/NXT_EXIT_CEILING_ADDENDUM.md](docs/NXT_EXIT_CEILING_ADDENDUM.md),
motore [`analysis/nxt/excursion.py`](analysis/nxt/excursion.py), verdetto
[docs/reviews/nxt-exit-ceiling-2026-08-14.md](docs/reviews/nxt-exit-ceiling-2026-08-14.md).

**Perché non è servito un test nuovo.** La meccanica d'entrata descritta è **già implementata** in
[`analysis/nxt/backtest.py`](analysis/nxt/backtest.py): `zigzag()` k=5 è il "pivot confermato a N
barre" (noto solo a `i+k`, look-ahead-safe), l'entry limite al 50% della gamba è l'ordine "a tot
distanza dall'estremo", lo SL al 78.6% è lo "stop sotto il minimo". Già testata: **E[R] −0,44R,
6/6 asset e 14/14 anni negativi** (2026-07-17). L'unico elemento nuovo era **l'uscita**.

**Il test: si misura il soffitto, non una regola.** La MFE è il limite superiore invalicabile di
qualunque exit rule — nessuna regola incassa più di quanto il prezzo si sia mosso a favore. Se il
soffitto non basta, non serve costruire l'uscita a medie mobili.

**Aritmetica dichiarata prima**: con win 13,3% a stop invariato, per ribaltare il segno i vincenti
devono rendere in media **> 6,5R** invece di 3R.

**Le soglie sono passate — ed erano sbagliate.** E[R] oracolo +1,709 (CI [+1,610, +1,816]),
E[MFE | ≥3R] +10,10R, breadth 6/6 e 15/15. Ma con rischio = 0,286 × ampiezza gamba (≥1 ATR H1) e
holding fino a 20 giorni, **una MFE a doppia cifra in R è garantita per costruzione** per qualunque
geometria a stop stretto: 10R ≈ 2,9 ATR orari in 20 giorni. Zero potere discriminante. Errore di
progettazione dell'addendum, corretto aggiungendo il baseline che discrimina davvero.

**Il baseline random risk-matched ribalta il verdetto** (stesso asset, lato, rischio in unità di
prezzo e anno; entrata a **istante casuale**; 3 controlli per setup, n=30.869):

| | reale | random matched | diff | CI95 cluster |
|---|---|---|---|---|
| **E[R] oracolo** | +1,709 | **+3,149** | **−1,440** | **[−1,569, −1,314]** |
| **R terminale** (tenere fino a stop/scadenza) | −0,405 | **−0,005** | **−0,399** | **[−0,493, −0,308]** |
| P(MFE ≥ 3R) | 16,24% | 24,72% | −8,5 pt | — |
| stop-out | 95,4% | 92,7% | +2,7 pt | — |

**Breadth: 0/6 asset, 0/15 anni.** Ogni CI per asset esclude lo zero dal lato sbagliato.
→ **kill duro n. 2** (non batte il random matched) **e n. 3** (breadth).

**Le tre letture che contano.** (1) Il **soffitto** della struttura è più basso di quello del caso:
nessuna uscita può invertire l'ordine, si ottimizzerebbe dentro uno spazio più povero di quello di
partenza. (2) Il random terminale è **≈ 0** (−0,005R: una scommessa a caso con stop simmetrico rende
zero, come deve) mentre il reale è **−0,405R** → l'entrata **distrugge ~0,4R rispetto alla moneta**;
è alpha negativo misurato, non assenza di alpha. (3) **Converge col fade**: nel 2026-07-17 invertire
la stessa entrata rendeva +0,35R. Due misure indipendenti dicono che a questo orizzonte, dopo il
ritracciamento, il prezzo **prosegue nella direzione del ritracciamento**.

**Contabilità: nessun trial consumato** — rianalisi descrittiva di un test già chiuso, nessuna regola
modificata, holdout non aperto. La famiglia NXT conserva il round 3, senza nulla su cui spenderlo.

**Scope onesto.** Non è coperta la variante a scala di sessione su M5 (es. minimo della sessione di
Londra). Ma spostarsi lì sarebbe **shopping di timeframe** ([§4](docs/STRATEGY_LIFECYCLE.md)),
costerebbe l'ultimo round, e il modo di morte è già misurato su due scale indipendenti (NXT H1;
estremi di periodo su H4/D1/W1 nella ricerca livelli). **Non falsificata l'uscita a coda aperta in
sé**: è falsificato il suo accoppiamento con questa entrata.

**Lezione metodologica riusabile.** Per una geometria a stop stretto e holding lungo, le metriche di
escursione in unità di R sono **gonfiate per costruzione**: vanno sempre lette contro un baseline
risk-matched a entrata casuale, mai contro una soglia assoluta.

---

## 2026-08-09 — Griglia a numero tondo .80/.20 sul Nasdaq: **NULL**. Famiglia CLOSED al primo trial.

**Decisione.** Prima ipotesi estratta dal mandato "insight da YouTube" (fonte: *Okala 80/20*, canale
Chart Fanatics). Pre-registrata in
[docs/ROUND_NUMBER_GRID_PREREGISTRATION.md](docs/ROUND_NUMBER_GRID_PREREGISTRATION.md), eseguita da
[`analysis/round_grid/test_80_20.py`](analysis/round_grid/test_80_20.py). **Esito: NULL** →
famiglia **CLOSED**, nessuna rifinitura.

**Cosa è stato testato.** Solo il **primitivo oggettivo**, non la strategia: la strategia non è
testabile (entrate *fork/H/cross-section/repair* sono **descrizioni visive**, non regole; grafico
d'ingresso a **200 secondi**, non ricostruibile da M5 e senza M1 in repo). Ipotesi isolata: i prezzi
con finale **.80/.20** (`P mod 100 ∈ {20,80}`) reagiscono più di una griglia **identica per geometria
ma sfasata**.

**Perché il null era il giusto null.** Con griglia fissa il *random distance-matched* dell'engine
originale non è applicabile — la distanza determina la posizione, quindi un livello "alla stessa
distanza" sarebbe lo stesso prezzo. Baseline usata: **sfasamento di fase**, $\{20+\delta, 80+\delta\}
\bmod 100$, che preserva esattamente la spaziatura 60/40 e cambia solo la fase.

**Risultato** (NAS100 M5, 949.241 barre 2012-2026, TRAIN 70%, `classify()` della ricerca livelli con
costanti invariate, block-bootstrap sui giorni):

| | reale | random sfasato | differenza | CI 95% |
|---|---|---|---|---|
| **POOL** | **27,5%** | **27,5%** | **+0,08 pt** | **[−0,56, +0,74]** |
| SUPPORT | 29,2% | 28,5% | +0,70 pt | [−0,19, +1,65] |
| RESISTANCE | 25,9% | 26,5% | −0,54 pt | [−1,48, +0,36] |

n = **28.745 touch reali** su **2.903 giorni**. Il CI è largo ±0,65 punti percentuali: avremmo
rilevato un effetto di ~1 punto. **Non è un null per mancanza di potenza — è un null stretto.**

**L'holdout NON è stato aperto** (TRAIN negativo → si chiude prima), quindi il 30% finale della serie
resta **sigillato** per ipotesi future. È il meccanismo di
[STRATEGY_LIFECYCLE §2](docs/STRATEGY_LIFECYCLE.md) che fa il suo lavoro.

**Correzione a una mia stima a priori.** Avevo calcolato che i livelli .80/.20 coprono il ~40% del
territorio di prezzo, deducendone scarsa selettività. Vero **rispetto allo stop di Okala** (10 punti),
ma il test usa la tolleranza pre-registrata di **0,10 ATR**, molto più stretta: la distanza mediana dal
livello più vicino è **4,92 ATR** e solo l'**1,4%** dei punti orari è già "al livello". La critica vale
per l'uso operativo, non per il test.

**Cosa resta della fonte** (l'uso primario previsto dal mandato — il layer operativo, non le regole):
*spec drift* come modo di morte dominante di un sistema discrezionale (*"è facile prendere entrate che
**quasi** rientrano nel modello"*), overtrading auto-identificato, rischio fisso per trade con size
variabile, non rincorrere le entrate mancate — quest'ultima **converge indipendentemente** col nostro
gate anti-ritardo sui segnali mentore. **Rifiutato**: *"più contratti quando sei caldo"* — anti-Kelly,
alza la varianza proprio quando la stima dell'edge è più gonfiata dalla fortuna recente.

**Statistiche dichiarate scartate**, come da mandato: 70% win a 1,5:1 implica **+0,75R per trade**;
con "multiple entries per day" e rischio 0,25% sono **>+140% l'anno sostenuto**. Fallisce il BS-test
di [04 §8](fondamenti_tecnici/04_quant_metodologia/principles.md). Quarta occorrenza dopo NXT,
VELTRIX e il playbook Chart Fanatics.

**Budget**: trial **1 di 3** della famiglia, e **1 delle 2-3 pre-registrazioni esterne del trimestre**.

---

## 2026-08-07 — Segnali mentore XAUUSD: **CONFERMATO fuori campione**. Primo OOS pre-registrato superato.

**Decisione.** L'edge direzionale del mentore **regge OOS**. È il **primo verdetto positivo su un
test pre-registrato** in questo workspace. Pre-registrazione:
[docs/MENTOR_SIGNALS_OOS_PREREGISTRATION.md](docs/MENTOR_SIGNALS_OOS_PREREGISTRATION.md) (scritta e
committata **prima** dell'esecuzione, commit `21df57b`). Motore:
[`analysis/mentor_signals/oos_validation.py`](analysis/mentor_signals/oos_validation.py).

**Finestra**: 131 segnali completi dal 15/06 al 07/08/2026 — **mai replayati** dall'audit dell'8
luglio, che si fermava al 12/06 per copertura prezzi. 121 eseguiti (fill entro 6h dall'entry).
Serie M5 estesa col feed MT5 e validata sulla sovrapposizione (8.063 barre, corr 1.000000, offset
mediano +$0.060 sottratto).

**Esito (soglie fissate prima):**
| Metrica | OOS | Audit luglio |
|---|---|---|
| Win-rate simmetrica mentore | **63,0%** | 67-72% |
| Win-rate side casuale | 35,0% | 32% |
| **Differenza appaiata** | **+0.277** · BCa95 **[+0.193, +0.353]** | — |
| **E[R] TP1 dopo costi** | **+0.194** · BCa95 **[+0.079, +0.289]** | +0.20/+0.32 |
| TP1 hit | 81,8% | ~85% |
| Stabilità mensile | 57,1% / 65,2% / 66,7% | 60-77% |

Entrambe le condizioni pre-registrate soddisfatte (lower bound della differenza > 0; E[R] > 0) →
**CONFERMATO**.

**BUG TROVATO E CORRETTO — allineamento orario.** Il sanity-check di riconciliazione, imposto dalla
pre-registrazione, è scattato. Test di shift sui timestamp (criterio **indipendente dagli esiti**:
minimizzare lo scarto mediano |entry dichiarato − prezzo al timestamp|): −1h → $16.34; **0h → $10.53**;
**+1h → $3.16 (minimo)**; +2h → $7.15. I timestamp Telegram sono **UTC+01:00**, la serie prezzi è in
**ora server broker (~UTC+2)**: serve **+1h**. Su stop da ~$10 uno scarto di $10.53 non è
trascurabile. Correzione di **bug**, non ritaratura → non conta come trial
([STRATEGY_LIFECYCLE §3](docs/STRATEGY_LIFECYCLE.md)). **Il verdetto regge in entrambi gli
allineamenti** (senza fix: 69,0% e E[R] +0.243); i numeri corretti sono più conservativi.

⚠️ **Conseguenza sull'audit di luglio**: usava lo stesso confronto naive → i suoi numeri (67-72%,
E[R] +0.20/+0.32) sono probabilmente **leggermente ottimistici**. Il valore realistico è quello OOS:
**~63% e E[R] ~+0.19**. Da ri-eseguire con il fix per allineare il record.

**Cosa NON autorizza.** (1) **Non** è un test di esecuzione: il forward reale del copier (2-8 giugno)
ha rifiutato **5 segnali su 12** perché il prezzo si era mosso oltre 20 pip — questo misura l'edge del
**segnale**, non quello **catturabile**. (2) **Non** cambia il divieto prop sui segnali di terzi
([PROP_FIRM_CRITERIA.md §4](docs/PROP_FIRM_CRITERIA.md)): resta capitale proprio. (3) Restano key-man
risk, un solo asset, un solo regime, e **survivorship confermata allo ~0,2%** (1 segnale cancellato
dal canale tra i due export).

---

## 2026-08-07 — Prop: copy-trading CHIUSO definitivamente + criteri nostri + consistency rule misurata

**1. Copy trading di segnali terzi: CASO CHIUSO.** Sesta e ultima verifica (catalogo
`propfirmtrader.com`, 18 firm, via browser dell'utente): **nessuna firm permette la copia esterna**.
La distinzione universale è **interno vs esterno** — copiare la *propria* strategia su *propri*
account è ammesso quasi ovunque, seguire segnali di terzi è vietato **anche in funded**, dove anzi è
più severo perché i programmi funded richiedono decisioni di trading indipendenti.

**Il divieto è strutturale, non commerciale**: decine di account che aprono la stessa posizione nello
stesso minuto sono il rischio concentrato che il modello prop esiste per evitare. Non è una policy
che cambia da firm a firm per marketing. → **L'edge mentore va su capitale proprio, o non va.**
Riapertura solo con evidenza esterna nuova ([docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md) §7).

*Nota metodologica*: `propfirmtrader.com` espone i regolamenti per **1 firm su 18** → **non
utilizzabile a livello di rulebook**, buono solo per censire il perimetro. Conferma la regola: si
lavora sui **regolamenti primari**. L'unico frammento recuperato (Alpha Capital, *"Group hedging or
prohibited copy trading"*) sta nella sezione **Trading Activity & Risk Review legata alle richieste
di payout** → conferma che l'enforcement scatta al **payout review**, non all'apertura.

**2. Criteri nostri prima delle firm** → [docs/PROP_FIRM_CRITERIA.md](docs/PROP_FIRM_CRITERIA.md).
Otto eliminatori derivati da cosa tradiamo davvero. I due che nessun comparatore espone e che ci
ucciderebbero in silenzio: **(a) daily drawdown su balance, NON su equity flottante** — `nxt_fade`
tiene posizioni fino a **20 giorni di borsa** su **6 strumenti in parallelo**, quindi un flottante
negativo (che poi gira a TP) farebbe scattare la violazione; **(b) holding overnight e weekend
consentito** — `nxt_fade` è **swing, non intraday**: le firm che obbligano a chiudere il venerdì lo
rendono ineseguibile. Nel ranking il **profit split è ultimo**, il **rischio di controparte** primo.

**3. Consistency rule: MISURATA, non stimata** — motore
[`analysis/nxt/consistency.py`](analysis/nxt/consistency.py) (riproduce esattamente i numeri
pre-registrati: E[R] +0.354, win 31.3%, n=10.280). Quota del giorno migliore sul profitto della
finestra, sole finestre in utile: **14 giorni → mediana 57,2%, sfora il 40% nel 74,7% dei casi**;
30 giorni → 41,9%; 60 giorni → **15,7%**.

**Alpha Capital (payout il 14 e il 28, regola 40% best-day): SQUALIFICATA** per questa strategia —
violeremmo 3 payout su 4, e sfora già il caso mediano.

**Mitigazione trovata**: allungando la finestra la violazione crolla (75%→42%→16%) → se la regola si
calcola **dall'ultimo payout** e l'accumulo è libero, richiedere il payout ogni ~60 giorni la rende
gestibile. Nuova domanda da porre a ogni firm: *dall'ultimo payout o dall'intera storia? Payout
obbligatorio a scadenza o accumulo libero?*

**Il risultato dura più della strategia**: non dipende dall'avere edge, dipende dalla **forma** della
distribuzione (payoff 1:3, trade sparsi). **Payoff 1:3 + payout bi-settimanale + consistency 40% =
incompatibili** per qualunque strategia di questa forma, anche futura. È un vincolo di
**progettazione**.

---

## 2026-08-07 — Pilastro investing OPERATIVO: Trade Republic + VWCE, 100 €/mese da fine settembre

**Decisione.** Il PAC passa da pianificato a **esecutivo**. Piano completo in
[docs/INVESTING_PILLAR_PLAN.md §0](docs/INVESTING_PILLAR_PLAN.md). **Broker: Trade Republic.
Strumento: VWCE** (`IE00BK5BQT80`, Vanguard FTSE All-World UCITS **Acc**, TER 0,22%, Irlanda),
verificato presente nel piano di accumulo dell'app. **Rata 100 €/mese**, data fissa, partenza **fine
settembre 2026**. **Nessun ribilancio** (uno strumento, 100% azionario, fase 1).

**Input personali (categoria A, chiusi):** 21 anni · rata 100 €/mese (l'utente aveva calcolato 150
sostenibili e sceglie 100 per garantire di non saltare mai) · obiettivo = capitale massimo per
smettere di lavorare quando vuole, **nessuna data d'uso** → orizzonte indefinito → **fase 1, 100%
azionario** · buffer e spese mensili **fuori perimetro** (li gestisce l'utente).

**Il vincolo strutturale che governa tutto: è un serbatoio, non un flusso.** Le entrate sono 2-3
stipendi estivi che coprono ~10 mesi (fino alla laurea, target 2 anni). Il PAC è un **prelievo a rate
da un serbatoio** → contromisura: a fine settembre si **vincolano €1.200** separati dai soldi di
spesa, e il PAC è garantito per l'anno a prescindere.

**Selezione broker (deep research 2026-08-04/07, 5 candidati).** Discriminante = **regime fiscale**,
non costo. **Esclusi per regime dichiarativo**: **Revolut** (ETF restano dichiarativi anche con IBAN
IT → quadro RT+RW ogni anno) e **IBKR** (nessuna stabile organizzazione in Italia → RT+RW+IVAFE; un
commercialista per il solo RW costerebbe >10% dei versamenti annui a questa scala). **Escluso per
frazionario**: **Directa** (arrotonda per difetto → a 100 €/mese alcuni mesi comprerebbe zero quote;
sarebbe ottimo a 500 €/mese). **Alternativa valida**: **Fineco** (Replay gratis under-30, ma il
vantaggio scade a 30 anni). **IBKR è rimandato, non escluso**: da rivalutare a portafoglio grande o
quando esisterà già un commercialista per il lato trading.

**Correzioni rispetto alla prima ricerca** (verifica utente su fonti ufficiali, 2026-08-07): il tasso
sulla liquidità è **2% ordinario** (BCE-linked, accredito mensile, **senza tetto** per IBAN IT), non
3% — il 3% è una **promo per nuovi clienti** fino a 50k. Il "niente RW/IVAFE" **non è dichiarato in
modo generale** nella documentazione ufficiale: il regime amministrato si applica **dopo la
migrazione alla succursale italiana**, non per data di apertura → verificare sulla certificazione
fiscale annuale. **Custodia e trasferimento titoli in uscita: NON PUBBLICATI** nel listino.

**Interessi sul vincolo: non sono una leva.** Saldo medio ~€600 → ~**€9/anno netti** al 2%
(~€13 con promo 3%), cioè lo 0,75% dei versamenti annui, e in termini **reali** circa a pareggio o
leggermente negativo. Non giustificano un aumento della rata: servono a pagare pochissimo
un'**opzione di liquidità** che nella situazione dell'utente ha valore vero.

**⚠️ La laurea NON è un trigger di aumento della rata**: il reddito sale ma salgono anche le spese
(vita da solo). Trigger corretto = **6-12 mesi dopo che la nuova struttura di spesa si è
stabilizzata**, su surplus verificato. Revisione **una volta l'anno a settembre**, agganciata al
ciclo di reddito, non all'anno solare.

---

## 2026-08-04 — Rituale di aggiornamento: dopo OGNI verdetto si allinea il repo

**Decisione.** Ogni verdetto (GO / LEAD / NO-GO / CLOSED / INSUFFICIENT DATA) chiude con
l'aggiornamento di **DECISIONS.md + memoria di lavoro + documenti impattati**, nella stessa
sessione. Non è un'attività opzionale di fine progetto: è parte del verdetto.

**Razionale.** Il buco trovato oggi lo dimostra: il **NO-GO NXT del 2026-07-17** e il lead fade
esistevano in memoria, in `strategie_candidate/` e in `_INTAKE.md`, ma **non in questo file** — cioè
non erano visibili a una sessione pulita che sfoglia il repo. Un decision log con dei buchi produce
esattamente ciò che esiste per impedire: riproporre cose già chiuse.

---

## 2026-08-04 — Ciclo di vita delle strategie: loop di ricerca formalizzato + criteri di bocciatura

**Decisione.** Adottato il loop `ricerca → formulazione → [G1] pre-registrazione → backtest (train) →
rifinitura (train) → walk-forward (train) → [G2] holdout sigillato → verdetto`, con criteri di kill
espliciti. Documento: [docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md).

**Razionale.** Un loop di miglioramento su dataset storico fisso è una **macchina per falsi
positivi** se non ha contabilità dei tentativi, dati sigillati e criteri di morte dichiarati prima.
Tre meccanismi rendono il loop non-tossico: (1) **contatore trial persistente** attraverso le
iterazioni (il DSR si applica al cumulato); (2) **holdout sigillato**, apribile **una volta per
famiglia** — se il budget si esaurisce prima, la famiglia muore senza averlo mai aperto;
(3) test operativo anti-p-hacking: *"avresti fatto questa modifica se il backtest fosse stato
positivo?"*.

**Criteri di kill.** Sei **kill duri** (difetto metodologico · non batte il random matched ·
fallimento di breadth · muore sui costi · instabilità parametrica · razionale economico falsificato)
e i **kill di budget**: **max 3 round di rifinitura per famiglia**, budget trial esaurito, e la
**regola di futilità DSR** (se il miglior risultato osservato è sotto la soglia di significatività
per il numero cumulato di trial, iterare è matematicamente inutile → kill immediato).
**Riapertura di una famiglia CLOSED solo con evidenza esterna nuova**, mai con un ritocco.

**Costo dimostrato:** la ricerca livelli è arrivata a **384 trial su 3 round** prima di chiudere il
libro; con un budget dichiarato in partenza sarebbe morta a v2.

---

## 2026-08-04 — Forward test FADE: pre-registrato a DUE STADI (50 boccia, 200 conferma)

**Decisione.** Il forward del fade — **già in corso da ~2026-07-24 senza pre-registrazione** — è
regolato da [docs/NXT_FADE_FORWARD_PREREGISTRATION.md](docs/NXT_FADE_FORWARD_PREREGISTRATION.md).
**Stadio 1 · N=50**: se E[R] ≤ 0 o win < 25% → **KILL** senza estensione; altrimenti prosegue.
**Nessun GO dichiarabile a 50, in nessun caso.** **Stadio 2 · N=200**: GO solo se il **lower bound
BCa 95%** su E[R] è > 0. Backstop 2026-10-31 e 2027-03-31; vale il primo evento.

**Razionale.** Il quant reviewer impone un *pavimento di sufficienza* (`n<50` → INSUFFICIENT DATA)
ma **non è una regola di stop**: è un gate a valle e non può sapere quante volte hai guardato prima
di sottoporgli i dati. L'asimmetria "negativo → raccogliamo ancora / positivo → chiudiamo" è
l'optional stopping, e il DSR penalizza le **varianti**, non le **sbirciate**.
Inoltre **N=50 è sottodimensionato per confermare**: con SD ~1,8R per trade l'errore standard su 50
trade è ~0,26R, quindi un E[R] vero di +0,35R darebbe un CI 95% **che attraversa lo zero** — per una
conferma a potenza 80% servono ~200-220 trade. Da qui i due stadi, entrambi fissati **prima** dei
dati. Il fade è **trial #2 di 3** della famiglia NXT e **non ha diritto a rifinitura** (è già nato
come rifinitura).

---

## 2026-08-04 — Prop firm: la traccia segnali-mentore NON è finanziabile su capitale prop

**Decisione.** L'assunto della roadmap *"prop anticipata dai segnali"* (2026-05-30) è **superato**.
Le prop non vietano solo l'automazione: vietano il **trading basato su segnali di terzi**. Verificato
su quattro firm indipendenti — FTMO, FundedNext, The5ers e Alpha Capital Group — che consentono la
copia **solo tra account di proprietà** e classificano il signal-following da canali Telegram come
*Group Trading* proibito. Se l'edge mentore va operato, va operato su **capitale proprio**.

**Perché morde davvero.** L'enforcement scatta al **payout review**, non all'apertura: si tradano
mesi e i profitti vengono negati quando si chiedono. Il rilevamento è per **pattern identici tra
account** — cioè esattamente la firma di più follower dello stesso mentore.

**Corollario.** La traccia **EA** resta compatibile (FTMO/FundedNext/The5ers/Alpha permettono EA su
MT5; vietati HFT, latency arbitrage, copy di terzi), ma oggi **non abbiamo nulla di finanziabile**:
ORB è NO-GO e il fade è un LEAD in forward. Scelta della prop **rimandata**, a valle di un GO.
Fattori da tenere presenti quando si riapre: **ESMA/MiFID II** in movimento sulle prop che si
rivolgono all'UE, avviso **CONSOB** del luglio 2024, 80-100 firm chiuse nel 2024 → il **rischio di
controparte è il criterio dominante**, non lo split. Alpha Capital: EA solo MT5 **con consegna del
sorgente `.mq5`** e **consistency rule del 40% best-day** — quest'ultima è testabile sulla
distribuzione del P&L giornaliero delle nostre strategie.

---

## 2026-08-04 — Fonti esterne: si raccolgono le regole, si scartano le statistiche dichiarate

**Decisione.** I canali/video di terzi entrano da [`_INTAKE.md`](fondamenti_tecnici/_INTAKE.md) e
alimentano **solo la fase RICERCA**. Due vincoli: (1) **mai importare le statistiche dichiarate nel
prior**; (2) **budget di max 2-3 pre-registrazioni per trimestre** da fonti esterne.

**Razionale.** Il track record dei claim esterni misurati da noi o da terzi: NXT ex-soci 60-70%
dichiarato → **13,3%**; bot VELTRIX 80-90% → **~53%**; ricerca livelli → **NULL** su 384 trial;
playbook Chart Fanatics 90% → **~20%** (test indipendente di terzi). Il collo di bottiglia non è mai
stata la fornitura di idee — è la **capacità di validazione**: ogni ipotesi in più alza
meccanicamente la soglia DSR per tutte le altre.

**Fonte valutata (2026-08-04):** *Chart Fanatics* / *Words of Rizdom* (Riz Iqbal) — stesso
ecosistema, monetizzato via Chart Academy e affiliazione con **Apex Trader Funding**; il metodo di
verifica dei trader non è pubblicato. **Uso approvato**: layer **operativo e di rischio** (pre-mortem
[04 §9](fondamenti_tecnici/04_quant_metodologia/principles.md)) + raccolta regole con filtro
d'ingresso (strumenti che tradiamo, regole codificabili senza discrezionalità, timeframe coperti dai
nostri dati).

---

## 2026-07-17 — NXT (Fibonacci/Elliott, ex-soci): continuazione NO-GO. Il FADE resta un LEAD.

> ⚠️ **Numero corretto dall'audit A5 del 2026-09-18** (la decisione **non** cambia). Il −0,44R qui sotto e' stato prodotto col **fill fantasma**: rimisurato coi soli fill ottenibili vale **−0,118R** BCa95 [−0,161 ; −0,076], e la breadth e' **0/6 strumenti** e **2/15 anni** positivi, non 14/14. Il difetto valeva **+0,326R**, tre quarti dell'effetto dichiarato. Vedi [voce 18/09 (5)](#) e [EARLY_STAGE_AUDIT_REPORT.md](docs/EARLY_STAGE_AUDIT_REPORT.md).


> *Voce ricostruita il 2026-08-04: la decisione era tracciata in memoria, in
> [`strategie_candidate/nxt_fib_trend_pullback.md`](fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md)
> e in `_INTAKE.md`, ma mancava da questo log.*

**Decisione.** La strategia **NXT** degli ex-soci (continuazione: entry al ritracciamento 0.5,
SL 0.786, target 1:3) è **NO-GO**. Test **pre-registrato** su 6 asset H1 (EURUSD, GBPUSD, USDJPY,
XAUUSD, US100, US500), ~14 anni, ~10.000 setup — motori
[`analysis/nxt/backtest.py`](analysis/nxt/backtest.py) e [`closure.py`](analysis/nxt/closure.py).

**Esito.** Win rate **13,3%** contro il 60-70% dichiarato; **E[R] = −0,44R**; negativa in **14/14
anni** e **6/6 strumenti**; l'holdout conferma; le varianti wide-stop non salvano. È un **kill duro
per fallimento di breadth** — nessun set di parametri ripara un effetto che non esiste.

**Sottoprodotto.** Il **lato opposto** (FADE / mean-reversion: stessa entrata, posizione invertita,
R = 28,6% della gamba, TP 3R, BE a +2R) è **+0,35R** base e **+0,24R** a 3× i costi, positivo in
14/14 anni e 6/6 strumenti. **Ma è un'ipotesi data-derived** — nata invertendo una strategia che
perdeva, sugli stessi dati. → **LEAD**, non edge: richiede pre-registrazione nuova e forward OOS
indipendente. Spec eseguibile:
[`fade_mr_walkforward_socio.md`](fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md);
EA [`mql5/nxt_fade.mq5`](mql5/nxt_fade.mq5). Forward pre-registrato il 2026-08-04 (voce sopra).

---

## 2026-07-16 — Opening-Range Breakout (scalping single-asset, idea utente+socio): NO-GO su 14.5y.

> ⚠️ **Ridimensionato dall'audit A5 del 2026-09-18.** Il NO-GO vale per **SPX500** (TRAIN '12-'19: −0,267 BCa95 [−0,391 ; −0,121], esclude lo zero). Su **NAS100 ogni intervallo contiene lo zero** e arriva fino a +0,078 / +0,203, con MDE **0,135R**: la casella e' **vuota, non chiusa**. La frase *"anche il filone scalping single-asset e' null"* generalizza da **uno strumento su due**. ⚠️ Non autorizza a riaprire: l'holdout della famiglia e' gia' speso.


Primo test del filone **scalping intraday single-asset**. ORB dell'apertura cash USA (09:30 ET) + retest,
US100/US500 M5, 1:2, pre-registrato ([docs/OPENING_RANGE_PREREGISTRATION.md](docs/OPENING_RANGE_PREREGISTRATION.md)),
motore [analysis/opening_range/](analysis/opening_range/). Verdetto: [docs/reviews/opening-range-2026-07-16.md](docs/reviews/opening-range-2026-07-16.md).

**Lezione del campione:** sul broker (1.4y, 2025-26) sembrava debole-positivo (E[R]+0.073, entrambi lati+),
ma su **Dukascopy 14.5y (2012-2026, tutti i regimi)** — richiesta utente di allungare lo storico — è
**NEGATIVO**: NAS100 E[R] −0.056 (BCa CI [−0.11, 0.00]), SPX500 −0.137 (CI [−0.19,−0.08]). Per-anno quasi
tutti rossi; positivi solo 2021/2026 = outlier di regime. Il +0.073 recente era **fortuna di regime**.
Entrambi i lati negativi. Il segno si ribalta tra broker e Dukascopy sul 2025 marginale = firma di edge
**inesistente** (E[R]≈0 → domina il rumore di feed). Filtro news (v2) improbabile che ribalti −0.1R base.

**Decisione: NO-GO.** Estendere lo storico ha **corretto un falso positivo** (valore del multi-regime).
Anche il filone scalping single-asset, testato bene, è null → coerente col resto (niente edge meccanico
own robusto). Dati Dukascopy M5 14.5y NAS100/SPX500 e motore ORB **riusabili** per varianti pre-registrate
future. Confermati i due binari: reddito=mentore manuale, ricchezza=passivo.

**Iterazioni (utente+socio), stesso verdetto:** (1) **filtro news** = peggiora (breakout serve vol; giorni
calmi = chop). (2) **filtro volatilità ADX** = leva GIUSTA (E[R] sale monotòno con ADX) ma tetto ~zero su
NAS, negativo su SPX. (3) **v2 completa** (SL su OR+10, RR 1:3, BE a 2R, expiry 12:00 ET, ADX): **NO-GO** —
l'**holdout** è decisivo: 2012-2019 negativo su entrambi (NAS −0.08, SPX −0.27), positivo solo nel recente
2020-2026 (non-significativo) → **non-stazionaria/regime-dipendente**, non edge persistente (stesso inganno
del campione 1.4y). Chiuso il filone ORB. `backtest_v2.py` riusabile.

**Infra nuova:** `dukascopy-python` per storico M5 lungo e gratuito su indici (2012+); backtester ORB
tz-safe (UTC/EET → US-open) + ADX + holdout. Utile per qualunque futuro test intraday su indici.

---

## 2026-07-08 — Stagionalità TOM: NO-GO. Chiusa la ricerca di edge sistematici own → pivot al passivo.

Terzo e **ultimo** edge sistematico. Test pre-registrato ([docs/SEASONALITY_PREREGISTRATION.md](docs/SEASONALITY_PREREGISTRATION.md)),
motore [strategies/seasonality/backtest.py](strategies/seasonality/backtest.py). Verdetto:
[docs/reviews/seasonality-tom-2026-07-08.md](docs/reviews/seasonality-tom-2026-07-08.md).

**Esito: NO-GO.** La finestra Turn-of-Month **non batte finestre di giorni casuali** (pooled +3.47 bps/g,
**p=0.238**); effetto **assente/negativo sugli indici** (US500 −1.0%, US100 −2.6%/anno) → anomalia
decaduta. Strategia long-TOM Sharpe −0.28 (BCa lower −0.69, DSR 0.008 n.s., MC p=0.48, OOS −0.21); il
buy&hold (+0.40) la batte. I positivi (ETH +118%/anno) = rumore small-sample.

**BILANCIO del pivot post-livelli (patto con l'utente attivato):** livelli null (384) · TSMOM NO-GO
(=beta, B&H batte, short perde) · mean-reversion NO-GO · router momentum+MR **refutato** (beta-trap) ·
stagionalità NO-GO. **Nessun edge sistematico *own* robusto** su questo universo/epoca/accesso retail.
L'**unico edge reale** è il **mentore** (discrezionale, manuale, external-dependent). Ciò che è robusto e
automatizzabile è **raccogliere beta** (long diversificato vol-managed) = il **pilastro passivo**.

**Decisione:** si **chiude la ricerca di edge sistematici own** (si smette l'edge-hunting a treadmill).
Due binari: **reddito = mentore manuale** (quando l'utente può), **ricchezza = pilastro passivo**
(automatizzabile, robusto). **Prossimo lavoro di più alto valore = costruire bene il pilastro passivo**
("strutturato e protetto"), in sospeso in attesa degli input personali utente (INVESTING_PILLAR_PLAN.md).
La macchina rigorosa (`core/quant_metrics` + backtester riusabili) resta per opportunità future.

---

## 2026-07-08 — Mean-reversion vol (secondo edge): NO-GO. Ma emerge la complementarità momentum⟂reversione.

Secondo edge del pivot (dopo TSMOM NO-GO). Test **pre-registrato** ([docs/MEANREV_PREREGISTRATION.md](docs/MEANREV_PREREGISTRATION.md)),
motore [strategies/meanrev/backtest.py](strategies/meanrev/backtest.py) (riusa la struttura TSMOM),
16 asset D1 2003-2026, z-score N=10 Z=1. Verdetto: [docs/reviews/meanrev-portfolio-2026-07-08.md](docs/reviews/meanrev-portfolio-2026-07-08.md).

**Esito: NO-GO.** Primario Sharpe **−0.21**, BCa lower −0.63, DSR 0.011 n.s., MC p=0.50, PBO 0.80,
White's RC p=0.94, walk-forward OOS −0.02. Tutte le varianti ≤ 0. Coerente col decay documentato.

**Rivelazione (il lead più forte finora):** Sharpe standalone MR **positivo sui RANGER** (EURGBP.r +0.56,
USDCAD +0.32, cross FX, indici) e **negativo sui TRENDER** (XAU −0.76, BTC −0.38) → **specchio esatto di
TSMOM** (XAU +1.44, US100 +1.19, cross FX negativi). Momentum e reversione, **deboli da soli**, sono
**anti-correlati per carattere dell'asset**. → Ipotesi (da PRE-REGISTRARE, non rivendicare): **sistema
combinato momentum+reversione / router trendiness** look-ahead-safe (efficiency ratio/Hurst su dati
passati, MAI gli Sharpe in-sample) validato OOS. È la materializzazione della tesi "portafoglio ortogonale".

**Decisione:** kill-switch → archiviare MR standalone. **Bivio (scelta utente):** (a) il combinato
momentum+reversione (lead forte, thesis-aligned) o (b) prossimo backlog (stagionalità/calendario).

---

## 2026-07-08 — Segnali mentore XAUUSD: edge direzionale REALE (primo positivo). → forward paper-validation.

Track A del pivot (priorità-1 utente). Parser + replay dei suoi segnali sul prezzo oro REALE (M5,
Gen-Giu 2026): **non un backtest disegnato, ma l'audit del suo track record live**. Codice
[analysis/mentor_signals/](analysis/mentor_signals/); verdetto [docs/reviews/mentor-signals-2026-07-08.md](docs/reviews/mentor-signals-2026-07-08.md).

**Riconciliazione**: i suoi entry stanno nei range intraday dell'oro reale (range 2026 mentore 3964-5553
vs reale 3999-5415) → è XAUUSD vero. Il mio flag "4670 vs 4155" era errore di allineamento (segnale di
metà 2026, oro in discesa) — CHIUSO.

**Esito (477 segnali replayati, dopo costo):** win-rate simmetrica **67-72%** vs **32%** del side casuale
(stessa geometria/tempi) → la sua direzione è giusta ~2/3 (non è drift dell'oro). Exit TP1 **E[R] +0.20/
+0.32**; TP1-hit reale ~85% (il suo claim "~100%" è ottimista). **Robusto al ritardo di copia manuale**
(E[R] +0.32→+0.12 da 0 a 60 min) e **stabile su tutti i 6 mesi** (60-77%). 5 angoli indipendenti concordi.

**Caveat vincolanti:** è una **COPIA** (key-man risk, non generatore nostro); 6 mesi/1 asset/1 regime
(oro in discesa); esecuzione idealizzata; survivorship non escludibile del tutto (ma baseline 32% +
"Sl hit"/"Running loss" nel canale remano contro). **Le prop vietano l'auto** → è la traccia **manuale**
(utilizzabile col telefono, ORA non disponibile), NON il milestone "1 mese demo non supervisionato".

**Decisione:** primo edge che **merita di proseguire**. → **forward paper-validation live** (~4-6 sett.,
out-of-sample vero, con esecuzione reale) via il parser; se tiene, è l'edge da operare **a mano** sulle
prop. In parallelo la traccia "sistema nostro" continua col prossimo edge del backlog. Nessuna promozione
a capitale senza forward.

---

## 2026-07-08 — TSMOM multi-asset (primo edge del pivot): NO-GO pulito. Kill-switch → mean-reversion vol.

> ⚠️ **Declassato dall'audit A5 del 2026-09-18 da "refutato" a NON MISURATO.** Con 23 anni l'effetto minimo rilevabile e' **Sharpe 0,59**, mentre l'atteso a priori citato da questa stessa voce e' **0,3-0,5**: per vedere 0,4 servivano **53 anni**. L'intervallo osservato [−0,18 ; +0,59] **contiene per intero** la fascia attesa. Il test **non ha escluso** l'effetto: ha fallito nel dimostrarlo. Resta chiuso (la casella non e' riempibile), ma **smette di valere come prova** nel bilancio *"niente edge meccanico own robusto"*.


Primo edge dopo la chiusura livelli. Test **pre-registrato** ([docs/TSMOM_PREREGISTRATION.md](docs/TSMOM_PREREGISTRATION.md)),
motore di portafoglio [strategies/tsmom/backtest.py](strategies/tsmom/backtest.py) sulle **serie di
rendimenti** (non le sintesi MT5 del tentativo 2026-05), 16 asset D1 2003-2026, spec canonica MOP
(sign 252g, vol-target 60g, media portafoglio, mensile, costi, look-ahead-safe). Verdetto completo:
[docs/reviews/tsmom-portfolio-2026-07-08.md](docs/reviews/tsmom-portfolio-2026-07-08.md).

**Esito: NO-GO.** Primario (252,mensile) Sharpe **+0.21**, ma **BCa CI [−0.18,+0.59]** (lower≤0),
**DSR 0.33 n.s.**, MC-perm **p=0.51**, **PBO 0.58**, White's RC **p=0.53**, walk-forward OOS +0.12
(degrado 51%). 5 test indipendenti concordi: **edge non distinguibile dal caso**. Overlay prop: maxDD
−40% → non avviabile.

**Novità vs 2026-05-29:** il multi-asset ha **risolto i difetti** del vecchio NO-GO (mono-asset/mono-anno):
breadth 12/16, top asset 16%, 13/23 anni positivi. Il problema non è più il campione — l'edge è
**semplicemente troppo debole** (~0.2) in questo universo USD-pesante / epoca decaduta post-2009
(atteso a priori: Baltas-Kosowski, SG Trend 0.3-0.5). Nessun curve-fit: verdetto per BCa+DSR+PBO+MC+WRC.

**Ipotesi (NON risultato):** trend concentrato negli asset che trendano (XAU +1.44, US100 +1.19, US500
+1.13, BTC +0.63) vs cross FX negativi (USDCHF −0.27, EURGBP.r −0.69). Un TSMOM "trending-universe"
*potrebbe* reggere, ma è **post-hoc** → va pre-registrato come nuovo trial e validato OOS, non rivendicato.

**Decisione:** kill-switch pre-registrato → **archiviare TSMOM canonico**, passare al prossimo edge del
backlog ortogonale (**mean-reversion vol non-level**), salvo scelta utente di pre-registrare prima la
variante trending-universe. La **macchina di validazione** (`core/quant_metrics` + backtester portafoglio)
è l'asset riusabile per gli edge successivi.

---

## 2026-07-07 (v3) — Livelli HTF fatti bene: confermato NULL. Libro CHIUSO davvero (384 trial).

Dopo l'audit delle tolleranze (la `0.10·ATR` era una costante ereditata/tarata su XAU-H1, applicata a
sproposito anche alle zone; i materiali dicono che i livelli forti stanno sugli HTF, che OB/S-D sono
**zone** con larghezza intrinseca e regola del **50% MT**, e che la struttura è **ubiqua**), abbiamo
rifatto il test **come si deve** (addendum pre-registrato). Motore `analysis/level_research/htf.py`:
- detection/misura su **H4, D1, W1** (H4 resample da H1, W1 da D1); **tolleranza scalata all'ATR del TF**
  (0.20 linea; le zone usano la **larghezza vera** + break = body-close oltre il 50% MT);
- **random distance-matched E structure-free** (rifiutato se cade su qualsiasi struttura vera — il punto
  che chiedeva l'utente); **freshness** naked/tested stratificata. FVG e Monthly esclusi (decisione utente).

**Esito (5 concetti × 3 TF × 16 asset = 240 trial): 0 sopravvissuti.** Pooled reale ≤ random su ogni TF
(spesso **negativo**: swing W1 CI[−2.4,−0.7], D1[−2.0,−1.3], H4[−1.5,−0.8]; prev H/L, round, EQH/EQL
idem; OB il "meno peggio" ma CI che tocca 0, breadth 2/16). **7 celle "battono" su 240, attese ~12 per
caso** → sotto il rumore. **Freshness piatta** (naked ≈ tested, entrambi ≤ random) → smentisce anche la
tesi "fresh≫tested" dei materiali. Con il random *structure-free* i livelli reagiscono spesso **meno del
vuoto** → coerente con "i livelli sono dove il prezzo rompe/consuma liquidità, non dove rimbalza".

**Robustezza tolleranza:** il null tiene a **0.10·ATR** (v1, H1) **e** a **0.20·ATR** (v3, H4/D1/W1) →
non è un artefatto della soglia. **Totale ricerca livelli: v1(96)+v2(48)+v3(240) = 384 trial
pre-registrati, 0 edge.** "Il prezzo reagisce ai livelli come zona" è **falsificato a fondo, su ogni
timeframe e con la metodologia dei nostri stessi materiali.** Libro chiuso senza rimpianti. **Pivot** a
strategie **non** level-based (razionale economico/peer-reviewed) — da decidere con l'utente.

---

## 2026-07-07 — Ricerca livelli v2 (volume): 0/3 concetti. Libro CHIUSO (144 trial, 0 edge).

Testata l'ultima famiglia rimasta (concetti **volume**, tick-proxy), stesso protocollo pre-registrato
([addendum](docs/LEVEL_RESEARCH_PREREGISTRATION.md)): POC/VAH/VAL, VWAP, anchored VWAP × 16 asset.
**Nessuno batte il random distance-matched** — breadth 0/16 ciascuno, pooled reale≈random (POC 30.1
vs 30.5 CI[−0.8,+0.1]; VWAP 30.6 vs 30.5 CI[−0.7,+1.0]; AVWAP 29.7 vs 29.7 CI[−0.5,+0.4]). **0 celle
"battono" su 48** (attese per caso ~2.4). Caveat dichiarato: volume = tick-proxy su tutti gli asset.

**Conclusione (regola pre-registrata).** v1 (6 OHLC) + v2 (3 volume) = **9 concetti × 16 asset = 144
trial, 0 sopravvissuti.** La premessa "il prezzo reagisce ai livelli come zona" è **falsificata in modo
ampio e a prova di p-hacking**. **Libro livelli-come-zona-di-reazione CHIUSO. Pivot.** Unico angolo mai
testato (e volutamente non aperto: alto rischio DoF/overfit) = livelli come *filtro condizionale* dentro
un contesto direzionale/sessione — NON è "reazione al livello", è un'altra ipotesi. Motore
`analysis/level_research/` resta riusabile per qualsiasi nuovo concetto (basta dichiararlo nuovo trial).

---

## 2026-07-06 — Ricerca livelli v1: NESSUN concetto batte il random (0/6). Pivot.

**Contesto.** Dopo il NO-GO del conf=2 (sotto), abbiamo rifondato la domanda: *quali criteri trovano
livelli dove il mercato reagisce davvero?* Test **pre-registrato**
([docs/LEVEL_RESEARCH_PREREGISTRATION.md](docs/LEVEL_RESEARCH_PREREGISTRATION.md)), motore walk-forward
look-ahead-safe ([analysis/level_research/](analysis/level_research/)), **6 concetti OHLC-puri** ×
**16 asset** (FX/metalli/crypto/indici, feed demo4 validato), metrica = **%REACTION|touch reale vs
random distance-matched**, CI block-bootstrap sui giorni, breadth, DSR sui 96 trial, holdout 70/30.

**Esito (TRAIN, breadth = asset che battono / testati):**
| concetto | breadth | pooled %REACT reale vs random | CI95 diff | esito |
|---|---|---|---|---|
| swing S/R | 1/16 | 29.0% vs 29.8% | [−1.1, −0.6] | peggio del random |
| PDH/PDL | 0/16 | 28.8% vs 30.5% | [−2.4, −1.2] | **peggio** (rotti più del caso) |
| order block | 3/16 | 30.0% vs 29.6% | [+0.0, +0.9] | pool>0 ma breadth<50%, ~0.4pt |
| FVG | 0/16 | 29.6% vs 29.8% | [−0.5, +0.2] | nullo |
| round number | 0/16 | 29.4% vs 30.1% | [−1.1, −0.3] | peggio del random |
| EQH/EQL | 0/16 | ~nullo | — | nullo |

**DSR/molteplicità:** 4 celle "battono" su 96; falsi attesi per caso a CI95 = 0.05·96 ≈ **4.8** →
osservati ≤ attesi = **rumore**. La %REACTION è ~29-30% ovunque, **identica** tra livello "vero" e
punto arbitrario alla stessa distanza.

**Decisione (regola pre-registrata attivata).** Nessun concetto sopravvive → a questa risoluzione
**i livelli non sono zone di reazione**: la posizione "strutturale" non aggiunge nulla oltre la
distanza. Generalizza il conf=2 su 16 asset × 6 concetti. **Non forziamo edge dove non c'è → Pivot.**

**Scope onesto (NON falsificato):** (a) concetti **volume** (POC/VWAP/TPO), rimandati a v2 (proxy su
FX); (b) livelli come **filtro condizionale** in un contesto direzionale/sessione (non zona di reazione
unconditional); (c) altri timeframe/orizzonti. Unici spiragli prima di chiudere il libro "livelli".

---

## 2026-07-05 — Level Analyzer conf=2 (fade): **NO-GO forward** (i livelli ≠ zone di reazione)

**Decisione.** Il fade sistematico dei livelli conf=2 (XAU+BTC) è **NO-GO**. Analisi con 3 agenti
Fable indipendenti (criteri di reazione dai materiali · audit fallacie · misura reazione-vs-random)
su 101 record forward (18-06 → 05-07-2026, 81 riconciliati).

**La prova decisiva = misura DIRETTA dei livelli** (indipendente dalla meccanica del trade): i
livelli conf=2 **non reagiscono più di livelli casuali** alla stessa distanza (BTC 18.5% vs 22.5%,
CI include 0; con baseline a 0.3–6 ATR reagiscono *meno* del caso); **~63% dei touch finisce in
break**. La classificazione livello→esito è forte (REACTION→67% win, BREAK→13% win): i livelli sono
in maggioranza cattivi. Coerente col trade E[R]=−0.37R (CI esclude 0).

**Il trade da solo NON basta a concludere (audit).** Il forward NON testava la strategia validata:
24/7 vs sessione 06–21 (61/101 fuori finestra), livelli "appena nati" ricalcolati sulla barra in
formazione (repaint → fade del momentum), XAU su **GC=F futures** (spec: spot), exact-touch vs fill
tollerante. Inoltre "conf=2" NON era 2 nature diverse (47/101 = stessa natura doppia; `cluster_confluence`
conta i membri) e il backtest "+0.15R" era esso stesso debole (CI iid su trade clusterizzati,
selezione post-hoc del bucket). → il −0.37 del trade è confondato, MA la misura diretta (C)
falsifica il **concetto** alla radice: non serve "fixare il protocollo e ri-fadare".

**Razionale.** N-esimo negativo custom (cfr. London Breakout, TSMOM, Stock Selector, sweep+reclaim,
regime gate). Il workflow ha fatto il suo lavoro: refutato strategia **e** la sua validazione debole,
prima dei soldi veri. Il Level Analyzer va **sospeso** (stop `run` sul server); il workflow
(capture→reconcile→gate + agenti) è l'asset riusabile che resta.

**Reverse/breakout anch'esso REFUTATO (check `breakout_check.py`, 13y/6y):** tradare la direzione
OPPOSTA alle zone conf=2 è **catastrofico** (XAU −0.78 / BTC −0.70 / EUR −0.77, win 11-16%), molto
PEGGIO del random → nessun edge inverso, le zone non sono neanche livelli di breakout. Chiude
"tradare questi livelli in qualunque direzione". NB tensione: nel **backtest** il fade batte il
random (+0.19 vs −0.16) ma NON regge **forward** (−0.37) → edge in-sample fragile/overfit + protocollo
forward rotto. C'è debole struttura mean-reversion in-sample (il reverse-catastrofico lo conferma),
troppo fragile per la meccanica grezza e diluita dal blob conf=2.

**Segnali deboli conservati (non azionabili, n piccolo):** natura **OB** sopra media (33% reaction,
n=21) e regime "transizione" (n=13); **FVG** (5% reaction, 90% break) e regime "range" (0/18) = rumore.
XAU inconcludente (futures + n=29). **Bug noti:** conteggio no_fill nel gate (fill reale ~83%), fill/exit
idealizzati (−0.37 = upper bound).

→ Analisi: [`analysis/trading-bot-eval/level_reaction_analysis.py`](analysis/trading-bot-eval/level_reaction_analysis.py) ·
spec [`LEVEL_ANALYZER_SPEC.md`](analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md) ·
workflow [`docs/TRADING_WORKFLOW_DESIGN.md`](docs/TRADING_WORKFLOW_DESIGN.md)

---

## 2026-06-14 — OctoBot (traccia crypto): **DORMIENTE**

**Decisione.** La traccia **OctoBot / crypto-automation** è messa in **stand-by (dormiente)**, non
archiviata: rispolverabile in futuro se si riapre esplicitamente un fronte crypto. **Emenda la priorità
del 2026-05-30** (sotto), dove OctoBot era #1.

**Razionale.** Dopo il pivot di giugno 2026 il lavoro reale è su **forex/XAUUSD via MT5** (signal copier
mentori, prop), **quant** (quant-review, metriche, backtest) e **investing passivo**. OctoBot è
**crypto-only** (esecuzione via ccxt, nessun MT5/forex) → non serve lo stack attuale. La priorità "#1
OctoBot" era anteriore a questo pivot. La review della repo forkata conferma: i pezzi che sembravano
combaciare (TelegramSignalEvaluator, modulo `signals/`) sono esempi banali / plumbing interno crypto, meno
adatti del nostro `signal_copier`.

**Condizione per riaprire.** Quando (a) si decide consapevolmente di aprire un fronte crypto-automation
**E** (b) c'è slack-time dopo milestone-1 forex. Allora OctoBot torna candidato come executor crypto.

→ Review: `github_repo_reviews/OctoBot.md` (memoria di lavoro) · Stage storico: [ROADMAP.md Stage 6](ROADMAP.md)

---

## 2026-06-14 — Terzo secchio (sleeve trend/managed-futures): **RIMANDATO a fase 2-3**

**Decisione.** Il pilastro investing resta a **due secchi** (buffer + All-World PAC) in fase di
accumulo. Lo *sleeve* trend-following / managed-futures — idea emersa dal materiale
volatility-drag / orthogonal-streams (QuantGuild) — **non si aggiunge ora**: è uno strumento di
**riduzione del drawdown**, quindi appartiene alla **fase 2-3** del glide-path (preservazione),
dove il piano già prevede una quota "difensiva". Quando ci si arriverà, va valutato come
**diversificatore del secchio difensivo accanto/al posto dei bond** (che nel 2022 hanno fallito la
diversificazione, correlazione salita coi tassi), **mai con leva**, **mai come "batti il mercato"**.

**Razionale.** (1) **Phase mismatch decisivo**: in accumulo il drawdown è un ALLEATO (il DCA compra
a sconto) → pagare carry negativo / CAGR inferiore per assicurarsi contro un non-rischio è sbagliato
ora (guardrail quant §3 del piano). (2) Il **principio** è solido (stream ortogonale R²≈0 → meno
drawdown → meno volatility drag → meglio geometrico; il trend-following fu orthogonale/positivo nel
2022 quando i bond fallirono), ma la **ricetta** commerciale (leva + hedge-leg "batte SPY") è un
singolo backtest in-sample non robusto. (3) **Praticità retail-IT**: gli strumenti canonici
(DBMF/KMLM) sono **US-domiciled** → estate tax + non-armonizzati + fisco complesso; opzioni UCITS
sottili, da verificare al momento. (4) La **base non è ancora costruita**: il piano a 2 secchi non
ha ancora i numeri (categoria A) → non aggiungere il layer più avanzato prima delle fondamenta.

**Condizione per riaprire.** Quando (a) il pilastro passivo è numericamente vivo **E** (b) si entra
in fase 2-3 del glide-path **E** (c) esiste un veicolo UCITS trend/managed-futures verificato (TER,
AUM, domicilio) → valutarlo come quota **modesta** del difensivo, misurandone il contributo reale a
drawdown/correlazione, **non** con leva.

**Corroborazione esterna (2026-06-14, review GitHub).** Il `ManagedFuturesAnalyzer` di FinceptTerminal
(impostazione standard CFA) classifica i managed futures come *"The Flawed"*: i benefici di crisis-alpha
**non giustificano** i costi (2&20), cita capacity constraints, e suggerisce **replica via ETF
trend-following low-cost o di saltare del tutto**. Converge con la nostra decisione (fee drag vs
crisis-alpha) e con la cautela sul singolo backtest levered-hedge. Da rileggere quando si riapre lo
sleeve in fase 2-3 → `github_repo_reviews/FinceptTerminal.md` (memoria di lavoro).

→ [docs/INVESTING_PILLAR_PLAN.md §3b](docs/INVESTING_PILLAR_PLAN.md) ·
teoria [fondamenti_tecnici/05_portfolio_rischio](fondamenti_tecnici/05_portfolio_rischio/principles.md) ·
caveat evidenza [fondamenti_tecnici/08_asset_allocation_passiva](fondamenti_tecnici/08_asset_allocation_passiva/principles.md)

---

## 2026-06-02 — Due tracce parallele + pivot Stock Selector → TAA risk-management

**Decisione.** Il lavoro procede su **due strade parallele**, non più in catena unica:
1. **Esecuzione/dati**: Telegram signal copier, OctoBot, Confluence automatica.
2. **Quant/investing**: parte dai **dati e dall'infrastruttura dello Stock Selector**.

Quando un fronte non ha lavoro attivo (solo raccolta dati), si avanza sull'altro. Questo
**emenda** la catena di priorità del 2026-05-30 (sotto): non un ordine rigido, ma due tracce
concorrenti. Vincolo invariato: **non promuovere nulla a capitale reale** finché la milestone-1
(mese demo positivo) non è raggiunta; il lavoro investing resta **validazione**, non operatività.

**Pivot Stock Selector.** Lo stock-picking cross-sezionale nell'SP500 è **falsificato**
(IC momentum ~0 a 12y, score fondamentale anti-predittivo — vedi review). Lo Stock Selector
pivota verso un **motore di asset-allocation tattica (TAA)** = gestione del rischio fattoriale
β<1 (timing dell'esposizione + dual-momentum cross-asset), **non** ricerca di alpha da selezione.
Layer 2-3 (selezione titoli) **congelati**; Layer 4 (multi-mercato) futuro.

**Correzione dati.** Per i backtest PIT survivorship-free i vendor sono **Sharadar SF1 / Norgate**,
**non Interactive Brokers** (che non fornisce titoli delistati → survivorship bias). IB resta
valido solo per l'esecuzione live. Acquisto dati rimandato finché il Layer 1 (gratis: ETF +
FRED) non supera il gate `/quant-review`.

→ Design + merge review a 5 agent: [docs/INVESTMENT_ALGO_DESIGN.md](docs/INVESTMENT_ALGO_DESIGN.md) ·
Review dati: [docs/reviews/stock_selector-2026-06-01.md](docs/reviews/stock_selector-2026-06-01.md)

---

## 2026-05-30 — Ordine di priorità del workspace

**Decisione.** Priorità in quest'ordine: **(1) OctoBot** → **(2) dati da Confluence + Telegram
signal copier** → **(3) prop firm** (anticipata dai segnali, se i dati reggono) → **(4) strategie
automatiche custom (IN FONDO)**.

**Razionale.** Concentrare l'energia su ciò che è già pronto a produrre dati/segnali invece
di disperdersi a costruire nuove strategie custom. Le strategie/agenti custom (incl. tutti i
*blueprint* in `fondamenti_tecnici/blueprints/`) restano backlog finché OctoBot e la raccolta
dati non sono completi. **Non riproporre dev custom finché OctoBot non è completo.**

---

## 2026-05-2x — Telegram Signal Copier: demo full-auto, prop rimandata

**Decisione.** Il copia-segnali (2 canali mentori → MT5) gira in **demo, full-auto**. La prop
sui segnali è **rimandata** (anticipabile se i dati demo reggono, vedi priorità sopra).

**Razionale + caveat.** Fase di test per validare parsing + risk gate prima di rischiare capitale.
Attenzione **compliance copy-trading** lato prop firm (alcune vietano la copia di segnali terzi).
Architettura: Telethon → parser → risk gate → MT5. I segnali mentori sono oggi **semiautomatici
in test** ma il target è la **piena automazione**.

→ Codice: [signal_copier/](signal_copier/) · Test: [tests/test_signal_copier.py](tests/test_signal_copier.py)

---

## 2026-05-30 — London Breakout: **NO-GO** (archiviata)

**Decisione.** London Open Breakout EA **archiviata**. Non si promuove a capitale reale.

**Razionale.** Quant review: su 686 trade (2020–2026) PBO alto, DSR non significativo, e l'edge
percepito dal regime gating era **look-ahead** (label calcolato sul close dello stesso giorno).
Il codice resta conservato in `mql5/` ma non è deployabile.

→ Review: [docs/reviews/london_breakout-2026-05-29.md](docs/reviews/london_breakout-2026-05-29.md) ·
Postmortem: [docs/reviews/london_breakout-postmortem-2026-05-30.md](docs/reviews/london_breakout-postmortem-2026-05-30.md)

---

## 2026-05-2x — Caveat look-ahead della regime timeline

**Decisione/Regola.** `data/regime_timeline_gbpusd.csv` ha il label calcolato sul **close del
giorno stesso** → usarlo **SOLO con lag 1 giorno** per strategie intraday, altrimenti si gonfia
l'edge. È stato il cap della quant-review di London Breakout.

**Razionale.** Evitare look-ahead bias (vedi [fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/)).

---

## 2026-05-29 — TSMOM USDJPY: **NO-GO / dati insufficienti**

**Decisione.** TSMOM single-asset (USDJPY D1) **non promosso**.

**Razionale.** 38 trade, DSR ≈ 0, l'edge dipendeva da 1 trade (regime 2021-22); sotto-campione
2024-26 negativo. Possibile rivalutazione solo in versione **multi-asset** con campione adeguato.

→ Review: [docs/reviews/tsmom_jpy-2026-05-29.md](docs/reviews/tsmom_jpy-2026-05-29.md) ·
[docs/reviews/tsmom-multiasset-2026-05-30.md](docs/reviews/tsmom-multiasset-2026-05-30.md)

---

## 2026-05-24 — Quant Reviewer come gate decisionale

**Decisione.** Le decisioni promuovi/scarta strategia passano da una **quant-review formale**
(`/quant-review`), non da impressioni. Pipeline: dati live → quant review → modifica codice.

**Razionale.** Dopo 2 settimane live (London: 2 trade; Confluence: 0 trade per attrito operativo)
serviva un metro statistico (PBO, DSR, walk-forward, MC permutation).

→ [agents/quant_reviewer.md](agents/quant_reviewer.md) · [core/quant_metrics.py](core/quant_metrics.py) ·
[docs/QUANT_REVIEW_PROTOCOL.md](docs/QUANT_REVIEW_PROTOCOL.md)

---

## 2026-05-24 — Confluence manuale → opportunistica

**Decisione.** La Confluence **manuale** (weekend planning + `levels.yaml`) è **opportunistica**:
nessun obbligo settimanale. L'energia è sull'**automazione** (`confluence_auto/` shadow run).

**Razionale.** L'attrito operativo del planning weekend produceva 0 trade. Meglio investire
sull'estrazione algoritmica dei livelli e raccogliere dati di confronto manuale vs algoritmico.

→ Concetti: [TRADING_PRINCIPLES.md](TRADING_PRINCIPLES.md) · [strategies/confluence_auto/](strategies/confluence_auto/)
(il vecchio `WEEKEND_CHECKLIST.md` — procedura manuale livelli→`levels.yaml`→VPS — è stato eliminato il 2026-06-14)

---

## 2026-05-05 — Pivot architetturale (ibrido Python/MQL5, 3 componenti)

**Decisione.** Architettura ibrida a **3 componenti indipendenti, 3 habitat, zero bridge**:
1. **Confluence Levels** (Python) — solo notifica — VPS Linux Hetzner.
2. **Expert Advisor MQL5** (es. London Breakout, archiviato) — esecuzione automatica — MetaQuotes VPS.
3. **Stock Selector** (Python) — tool offline — PC di casa.

**Razionale.** Disaccoppiare deployment e failure mode; niente VPS Windows/RDP; niente sync
Python↔MQL5. Sostituisce il piano monolitico pre-pivot.

→ Architettura: [docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md) ·
Operatività: [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md) ·
Doc storico pre-pivot: [docs/STAGE2_TESTING_PLAN.md](docs/STAGE2_TESTING_PLAN.md)

---

## Principio trasversale — Edge condizionato alla strategia

Nessuna fase di mercato è tradabile/non-tradabile **in assoluto**: l'edge è condizionato alla
strategia + regime. Il backtest da solo **non basta** — triangolare con razionale economico e
walk-forward. Vedi [fondamenti_tecnici/03_regimi_macro/](fondamenti_tecnici/03_regimi_macro/) e
[fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/).

---

## Principio trasversale — Mappa dei modelli (gestione dei conflitti tra teorie)

I mercati non sono scienza esatta: **non esiste l'equazione madre** che spiega/predice tutto.
Quando due fonti o teorie si contraddicono, il nostro compito **NON è eleggere un vincitore
universale** ("X è più giusto di Y"). Si registra **ogni modello con le sue CONDIZIONI di
validità** e si rende il conflitto **esplicito**, così la decisione operativa sceglie il modello
che calza il contesto. È l'estensione naturale del principio "edge condizionato" qui sopra.

**Model card minima** per ogni claim in conflitto:
`{ claim · fonte · condizioni (regime/asset/timeframe/assunzioni) · contraddice · stato (attivo/reference/parcheggiato) }`

**Esempi svolti** (i due conflitti già emersi nel materiale):
- *"Il backtest è inutile / è overfitting"* (Roan, Quant Guild) **vs** *"misura con DSR/PBO/
  walk-forward"* (López de Prado, nostro quant). **Non** è una contraddizione: vale separando
  *non curve-fittare una regola di timing* (vero) da *non misurare distribuzioni / non falsificare*
  (falso). Condizione: il backtest serve a **falsificare e misurare proprietà distributive**, non
  a *scoprire* la regola.
- *"Vendi il volatility risk premium"* (IV sovrastima RV in media) **vs** *"compra convexity /
  long-vol"* (mitiga il drag nei crash). Entrambe vere secondo **regime/timing**: vendi il premio
  in mercato normale, l'assicurazione paga nei tail.
- *"Il rischio forward non è misurabile con modelli e dati storici: vince la profondità
  qualitativa/esperienza"* (fonte: appunti 2026-08-04, blocco risk-mispricing) **vs** la nostra
  **pre-registrazione + gate statistici**. Si separa per **dominio**, non per merito:
  la fonte parla di **scommesse discrezionali concentrate** su singola entità ($n=1$, nessun
  campione disponibile, l'edge *è* la profondità informativa); noi facciamo **regole sistematiche
  ripetibili** su strumenti liquidi (il campione esiste, il fallimento dominante è l'overfitting).
  **Condizione operativa: il qualitativo genera ipotesi ed enumera direzioni di rischio — non
  valida mai.** Nessun ragionamento qualitativo promuove una strategia bocciata dai gate; nessun
  "aggiornamento bayesiano" sugli stessi dati già usati per il test. Il tassello **utile** della
  fonte (pre-mortem sulle direzioni principali di rischio) è distillato in
  [fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/) §9 — copre
  proprio ciò che il backtest non può interrogare (key-man, compliance, rottura tecnica).

- *"Genera 10.000 strategie e tieni le 25 che sopravvivono"* (ricerca di massa, StrategyQuant e
  affini) **vs** *"una ipotesi per volta, pre-registrata, con budget di trial"* (nostro
  [STRATEGY_LIFECYCLE](docs/STRATEGY_LIFECYCLE.md)). **Non si elegge un vincitore**: le due scuole
  pagano la **stessa** tassa di molteplicità in **posti diversi**. La ricerca di massa la paga in
  **deflazione** — con N grande il DSR alza la soglia al punto che serve un effetto molto forte per
  sopravvivere; la nostra la paga in **copertura**, perché esplorando poco possiamo semplicemente non
  incontrare mai l'edge. Nessuna delle due è gratis.
  **Condizione di validità**: la ricerca di massa è legittima **solo se** la molteplicità è
  effettivamente contabilizzata (DSR sul numero **vero** di candidati, PBO/CSCV su best-IS vs
  mediana-OOS) e l'holdout è aperto una volta sola. Senza quelle, "25 su 10.000" è indistinguibile
  dal rumore. **Nota autocritica**: il nostro repo ha talvolta letto "il data mining è male" come
  "non cercare". La formulazione corretta è **"cerca pure, ma deflaziona sul numero vero e non
  toccare l'holdout"** — e gli strumenti per farlo li abbiamo già in
  [`core/quant_metrics.py`](core/quant_metrics.py). Fonte del conflitto: Noel T./SQX, 2026-08-17.
- *"L'analisi tecnica non si può confutare: non puoi rigiocare lo stesso evento tecnico 10.000
  volte, e comunque non sono obbligato a usarla sempre"* (Quant Guild, #119, distillamento
  2026-09-17) **vs** i nostri **384 trial pre-registrati** che hanno chiuso la ricerca sui livelli
  ([[project_level_research_v1_null_2026_07_06]]). **Si separa per oggetto, non per merito.**
  L'argomento è **corretto** su un punto: un backtest meccanico falsifica **quella regola
  meccanica**, non l'abilità di chi la applica **selettivamente**; sono due ipotesi diverse.
  È **insufficiente** su un altro: da ciò non segue che l'abilità discrezionale sia
  **inosservabile** — è osservabile con il **track record prospettico pre-registrato** di quello
  specifico operatore, che è esattamente la strada già percorsa sui segnali del mentore
  ([[project_mentor_signals_edge_2026_07_08]]: direzione giusta 67-72% vs 32% casuale, stabile su
  6 mesi, robusta al ritardo). **Condizione operativa**: il NULL sui livelli **resta valido e non
  si riapre** (il suo bersaglio erano regole meccaniche); e **nessun** NULL meccanico va citato
  come prova contro un operatore discrezionale — per quello serve il suo track record prospettico.
- *"Non è la domanda se io possa generare alpha in modo consistente e statisticamente
  significativo"* (Quant Guild, #25, analogia del fuoricampo: *"devi solo essere in posizione di
  batterlo"*) **vs** `docs/STRATEGY_LIFECYCLE.md` + [[feedback_mass_search_vs_preregistration]].
  **Si separa per problema.** La fonte parla da **allocatore con mandato**: opera comunque, il suo
  problema è l'**esecuzione** e la sopravvivenza in posizione, e lì presidiare il processo (la
  "media battuta") è la mossa giusta. Noi abbiamo il problema opposto, la **selezione**: decidere
  **se accendere** una strategia. In una distribuzione a coda destra il singolo esito eccezionale
  è **esattamente** ciò che il rumore produce (~0,25% di falsi passaggi × 10.000 candidati ≈ 25
  "fuoricampo" dal nulla). **Condizione operativa**: per decidere se accendere, la significatività
  corretta per molteplicità **è** la domanda; il criterio "resta in posizione" vale **dopo**, sul
  capitale già allocato.
- *"Portfolio engineering con gamba di copertura e monetizzazione del drawdown: batte il
  portafoglio non coperto sul lungo periodo"* (Quant Guild, #47/#38/#29; e nella variante KMLM
  anche dagli appunti `Petrodollar ed ETF.txt`) **vs** il pilastro passivo deciso
  ([[project_stock_selector_eval_2026_06]], `docs/INVESTING_PILLAR_PLAN.md`).
  **CHIUSO il 2026-09-17** con una passata mirata di 7 video
  ([`copertura.md`](fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/quantguild/copertura.md), criteri
  dichiarati **prima** della lettura). Motivi: il costo della protezione non e' mai prezzato in 10
  video; la regola di monetizzazione e' **dichiaratamente non pubblicata** (sta in un corso a
  pagamento); l'unica dimostrazione numerica e' **sbagliata** (crescita geometrica dichiarata 0% con
  mu=15% e sigma=30%: sono +10,5%; per azzerarla servirebbe sigma=54,8%).
  🔧 **Condizione di pareggio ricavata da noi**, valida per **entrambe** le varianti: una gamba che
  costa `c` all'anno e porta la volatilita' da `sigma` a `k*sigma` si ripaga con la sola riduzione
  dell'erosione **solo se `sigma > sqrt(2c/(1-k^2))`** — con c=2,5% e k=0,5 serve **sigma > 25,8%**,
  mentre un azionario diversificato sta a 15-20% (erosione 1,1-2,0%/anno). **Il conto torna solo a
  volatilita' alta**, ed e' per questo che entrambe le fonti accoppiano la gamba alla **leva** senza
  trarne la conseguenza: non e' "aggiungi protezione al tuo ETF", e' un **pacchetto con leva**.
  **Cosa sopravvive, con condizione**: l'argomento della **perdita tripla** (lavoro + casa +
  portafoglio crollano insieme perche' condividono il fattore macro) non e' un argomento sul CAGR ma
  sulla correlazione col **capitale umano**. Condizione: *la gamba serve quando il capitale
  finanziario e' grande rispetto al capitale umano residuo* — **oggi per noi no** (capitale ~0,
  decenni di reddito, e il drawdown si ricompra con i versamenti del PAC); torna seria **a ridosso
  del decumulo**. **Stato: chiuso, non si riparcheggia.**
  **Regola generale che ne discende**: *piu' occorrenze della stessa affermazione dalla stessa fonte
  non sono conferme indipendenti*. Le conferme si contano per **fonte**, non per **occorrenza** —
  vale anche al contrario di come l'abbiamo usata in passato (le 4 conferme esterne del lead
  playground contano perche' erano **4 fonti diverse**).

Operativamente la mappa vive in due posti: il **registro di intake**
([fondamenti_tecnici/_INTAKE.md](fondamenti_tecnici/_INTAKE.md)) traccia stato e destinazione di
ogni fonte; le **condizioni di validità** stanno accanto al concetto nel file `fondamenti_tecnici/`
che lo ospita, con cross-link al claim opposto. Regola epistemica di base: §0 di
[agents/quant_reviewer.md](agents/quant_reviewer.md) (il gioco, non i giocatori).
