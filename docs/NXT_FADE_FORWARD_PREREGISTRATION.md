# Pre-registrazione — Forward test FADE mean-reversion (NXT A1)

> **Documento vincolante.** Fissato il **2026-08-04**, con il forward test **già in corso** (EA
> avviato ~2026-07-24). Scopo: bloccare la **regola di stop** e le **soglie di verdetto** prima che
> la dimensione campionaria diventi conosciuta, per impedire l'**optional stopping** — decidere
> quando fermarsi guardando come sta andando. Le regole di questo file **non si modificano** durante
> il test; qualunque modifica va datata, motivata e dichiarata nel report finale.
>
> Ciclo di riferimento: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md).
> Spec operativa immutabile: [fade_mr_walkforward_socio.md](../fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md).

---

## 1. Ipotesi sotto test

**H1**: la variante **FADE** (A1 mirror-fade 1:3) mantiene un'aspettativa positiva in R
**fuori campione**, su dati non usati per generarla.

**H0**: E[R] ≤ 0 — l'edge osservato nel backtest è un artefatto della derivazione dai dati.

**Perché serve.** Il fade è un'ipotesi **data-derived**: è nata invertendo la strategia di
continuazione che perdeva. Ha superato holdout interno e stress sui costi, ma quei test **girano
sugli stessi dati che l'hanno generata** e non possono validarla. Questo forward è l'unica evidenza
indipendente possibile. Stato attuale: **LEAD**, non edge ([STRATEGY_LIFECYCLE §5](STRATEGY_LIFECYCLE.md)).

## 2. Strategia — parametri congelati

Definizione operativa in `analysis/nxt/closure.py` (config **A1**), eseguita da
[`mql5/nxt_fade.mq5`](../mql5/nxt_fade.mq5). Parametri **immutabili** per tutta la durata del test:

| Parametro | Valore |
|---|---|
| Timeframe | H1 |
| Universo | EURUSD, GBPUSD, USDJPY, XAUUSD, US100, US500 |
| Swing | frattale a 5 barre per lato (`K=5`) |
| Filtro trend | HH+HL (uptrend) / LH+LL (downtrend) |
| Filtro dimensione gamba | ≥ 1× ATR(14) H1 |
| Direzione | **contro-trend** (uptrend → short, downtrend → long) |
| Entrata | ritracciamento **50%** della gamba |
| R (unità di rischio) | **28,6%** dell'ampiezza della gamba |
| Stop-loss | 1R dal lato del trend |
| Take-profit | **3R** (rapporto 1:3) |
| Break-even | stop a pareggio a **+2R** |
| Finestra di fill | 48 barre H1 dallo swing |
| Time-stop | ~20 giorni di borsa (`MAX_HOLD`) |
| Vincolo | un solo trade per gamba per strumento |

**Esecuzione**: EA su MT5 demo/VPS. Lo **storico MT5 è la raccolta dati** — nessun journaling
manuale, nessuna discrezionalità nel marcaggio degli swing.

## 3. Regola di stop — DUE STADI (pre-dichiarata)

> **Motivazione.** N=50 è sufficiente a **bocciare**, non a **confermare**. Con la distribuzione R
> attesa dal backtest (win ~31% a 1:3, break-even 25%), la deviazione standard per trade è
> nell'ordine di **~1,8R** → l'errore standard su 50 trade è **~0,26R**. Un E[R] vero di +0,35R
> produrrebbe un intervallo di confidenza al 95% che **attraversa lo zero**: anche se la strategia
> funzionasse esattamente come nel backtest, a 50 trade non potremmo dimostrarlo. Per una conferma
> a potenza 80% servono **~200-220 trade**. Da qui il disegno sequenziale a due soglie, entrambe
> fissate **ora**.
>
> *(La SD va ricalcolata esattamente sul trade log del backtest — `analysis/nxt/closure.py` — e il
> numero dello Stadio 2 aggiornato di conseguenza **prima** che il campione live vi arrivi.)*

### Stadio 1 — GATE DI BOCCIATURA · **N = 50 trade chiusi**

- Si valuta **una sola volta**, al raggiungimento del **50° trade chiuso** (aggregato sui 6 strumenti).
- **Backstop temporale: 2026-10-31.** Vale il primo evento che si verifica.

| Esito a N=50 | Decisione |
|---|---|
| **E[R] ≤ 0** (stima puntuale) | **KILL** — lead archiviato. Nessuna estensione, nessuna rifinitura |
| **Win rate < 25%** (sotto il break-even a 1:3) | **KILL** |
| **E[R] > 0** | **PROSEGUE** allo Stadio 2. Nessuna conclusione positiva dichiarabile qui |

### Stadio 2 — GATE DI CONFERMA · **N = 200 trade chiusi**

- Backstop temporale: **2027-03-31**.

| Esito a N=200 | Decisione |
|---|---|
| **BCa 95% lower bound su E[R] > 0** ([`bca_bootstrap_ci`](../core/quant_metrics.py)) | **GO** → valutazione per capitale, con pre-mortem obbligatorio |
| Altrimenti | **KILL** — il lead non regge, famiglia archiviata |

### Se il campione non arriva

- **N < 50 al 2026-10-31** → **una sola** estensione al **2027-01-31**. Se ancora < 50 → archiviato
  come **INSUFFICIENT DATA / irrisolto**. Nessuna ulteriore estensione.
- **N < 200 al 2027-03-31** → archiviato come **INSUFFICIENT DATA**, non come GO.

## 4. Impegni vincolanti (la parte che fa il lavoro)

1. **Non si prolunga se il verdetto è negativo.** Un E[R] ≤ 0 a N=50 chiude il lead. "Raccogliamo
   ancora un po'" è precisamente il bias che questo documento esiste per impedire.
2. **Non si guarda il P&L cumulato per decidere quando valutare.** La regola di stop è N e data, non
   l'aspetto della curva.
3. **Non si modificano i parametri in corsa.** Qualunque modifica **azzera il test** e ne apre uno
   nuovo, con nuovo N e nuova pre-registrazione — non prosegue quello vecchio.
4. **Nessuna rifinitura è disponibile su questo lead.** Il fade ha già consumato il suo ramo di
   ricerca: è nato *come* rifinitura di NXT. Un secondo ritocco sarebbe il secondo giro sugli stessi
   dati ([STRATEGY_LIFECYCLE §4](STRATEGY_LIFECYCLE.md)).
5. **Contatore trial**: il fade è **trial #2** della famiglia NXT (#1 = continuazione, NO-GO). Un
   eventuale terzo tentativo sarebbe l'ultimo prima del kill di budget (3 round).

## 5. Metriche da riportare nel verdetto

Obbligatorie, indipendentemente dall'esito:

- N trade chiusi, per strumento e aggregato · win rate · **E[R] con BCa 95% CI**
- Distribuzione degli esiti (TP / SL / break-even / time-stop) — il BE a +2R sposta massa a 0R e
  **abbassa** l'E[R] rispetto al modello a due esiti
- Breadth: E[R] per strumento (quanti dei 6 sono positivi)
- Confronto col backtest: **+0,31R** base / +0,24R a 3× costi, win ~31%
  (⚠️ **corretto il 2026-08-14**, era +0,35R: il backtest assumeva il fill dello stop *esattamente*
  al livello, ma il **12,7%** degli stop apre gia' oltre → fill vero −1,29R contro −0,75R assunto.
  Modellazione piu' realistica dell'esecuzione = **fix, non ritaratura**, non consuma trial
  ([STRATEGY_LIFECYCLE §3](STRATEGY_LIFECYCLE.md)). Motore `analysis/nxt/weekend.py`.
  **Il confronto forward va fatto contro +0,31R, non +0,35R.**)
- Slippage e spread **reali** vs modellati, **con il gap-attraverso-lo-stop separato**: e' la voce
  che vale −0,047R nel backtest ed e' per il **95%** un fenomeno **infrasettimanale**, non del weekend
- Trade saltati (setup validi non riempiti entro 48 barre) e motivo

## 6. Cosa NON è questo test

- **Non** è una validazione della famiglia NXT/Fibonacci: la continuazione è già **NO-GO** (win
  13,3%, E[R] −0,44R, 14/14 anni e 6/6 asset negativi).
- **Non** è un test su capitale reale: demo/micro, size sperimentale.
- **Non** produce un GO allo Stadio 1, in nessun caso.

## 7. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-04 | Creazione. N=50 (Stadio 1) e N=200 (Stadio 2), backstop e impegni fissati | Test già in corso da ~2026-07-24 senza pre-registrazione |
| 2026-08-12 | **Anomalia di deployment rilevata e corretta — vedi §9** | Il deployment non implementava l'universo pre-registrato |
| 2026-08-27 | **Pendenti orfani dopo un riavvio: strumento congelato — vedi §10** | La finestra di fill di 48 barre non sopravviveva al restart dell'EA (US500 spento 27 giorni) |

## 9. Anomalia di deployment (2026-08-12) — bug fix, NON modifica di spec

Alla terza settimana l'utente segnala l'assenza di trade sui cambi. Diagnosi sui log del VPS
(`hosting.6876289.experts` e `.terminal`, conto 7396683 @ FirstPrudentialMarkets-Demo):

**1. I tre cambi non hanno mai potuto operare.** L'EA *è* agganciato a EURUSD, GBPUSD, USDJPY — ma
ai simboli **senza suffisso**, che su questo broker esistono nell'albero e sono **disabilitati alla
negoziazione**. Il set tradabile è quello raw-spread con suffisso **`.r`**. Esito: **171 ordini
rifiutati con `[Trade disabled]`** (USDJPY 67, EURUSD 64, GBPUSD 40), loggati dall'EA come
`arm fallito, err=4756` (`ERR_TRADE_SEND_FAILED`, generico). Non è un difetto della strategia: la
logica genera i segnali correttamente, non riesce a inviarli. ⚠️ I 171 rifiuti **non** sono 171
segnali: l'EA non marca la gamba come armata quando l'invio fallisce, quindi ritenta a ogni barra.

**2. Uno strumento fuori universo.** `nxt_fade` era agganciato anche a **BTCUSD**, che non è nei sei
pre-registrati → **2 trade chiusi da escludere** dal conteggio e dal verdetto. Su BTCUSD si osservano
anche `No money` (x12) e **`Invalid stops` (x7)**: quest'ultimo è un modo di fallimento reale da
sorvegliare — se comparisse sui `.r` dopo il fix, sarebbe un problema di **geometria** (R = 28,6%
della gamba troppo stretto su un cambio a bassa volatilità), non di deployment.

**3. Pressione di margine.** Cinque ordini scartati con `[No money]` (BTCUSD x12 e US100 x2 nello
storico ordini). Il sizing risk-based con stop stretti genera volumi elevati; con **sei** strumenti in
parallelo il margine peggiora. **Mitigazione: ridurre il rischio per trade.** La **size NON è un
parametro pre-registrato** — §3 congela la geometria, e il verdetto è su **E[R]**, in multipli di R:
ridurre i lotti non altera alcuna statistica misurata.

**Qualificazione**: **bug fix**, non modifica di spec — il deployment non implementava l'universo
pre-registrato. Per [STRATEGY_LIFECYCLE §3](STRATEGY_LIFECYCLE.md) **non conta come trial** e non
azzera il test.

**Azioni**: (a) riagganciare l'EA a `EURUSD.r`, `GBPUSD.r`, `USDJPY.r`; (b) staccare **BTCUSD** e
**EURGBP.r** (entrambi fuori universo); (c) ridurre il rischio per trade a **0,25%**
(`InpRiskPerTradePct = 0.0025` — è una **frazione**, non una percentuale); (d) escludere i trade
fuori universo dal conteggio.

**Conteggio corretto al 2026-08-12** — `nxt_fade` = magic **26071**:

| Simbolo | Chiusi | |
|---|---|---|
| XAUUSD.cyr | 6 | in universo |
| US100 | 3 | in universo |
| BTCUSD | 2 | **escluso** (fuori universo) |
| US500 | 0 | agganciato, 1 pendente attivo, nessun fill |
| EURUSD.r / GBPUSD.r / USDJPY.r | 0 | mai potuti operare (`Trade disabled`) |

→ **N valido = 9/50**, breadth **2/6**.

> ⚠️ **Correzione di un mio errore di conteggio (2026-08-12).** In prima battuta avevo riportato
> N = 14 attribuendo i trade per **commento**. È sbagliato: il commento `nxt_fade` sopravvive solo
> sulla deal di **apertura**; la deal di **chiusura** porta un commento generato dal broker
> (`[tp 28292.80]`, `[sl 4409.82]`). Attribuendo per commento avevo incluso le chiusure di
> `orb_nasdaq` (magic 26052) dentro quelle di `nxt_fade`. **L'attribuzione corretta è per MAGIC**,
> che invece sopravvive su entrambe le deal. Verificato in
> [`analysis/ops/deployment_healthcheck.py`](../analysis/ops/deployment_healthcheck.py), che usa il
> magic e va usato come fonte del conteggio da qui in avanti.

> ⚠️ **CAVEAT DI COMPOSIZIONE — obbligatorio nel verdetto finale.** Le prime tre settimane del
> forward hanno operato su **2 strumenti su 6** (US100 e XAUUSD). Anche dopo il fix il campione non
> sarà un'estrazione omogenea dall'universo: la prima parte è sbilanciata su due strumenti, la
> seconda sarà mista. L'E[R] resta misurato per trade, ma il report finale **deve** includere il
> **breakdown per strumento** e dichiarare questa asimmetria.

---

## 10. Anomalia di deployment (2026-08-27) — un riavvio dell'EA **congela lo strumento**. Bug fix, NON modifica di spec

**Come è emersa.** L'utente ha cancellato a mano un pendente US500 fermo dal **2026-07-31** per
vedere se lo strumento si sbloccasse. Si è sbloccato: l'EA ha armato un nuovo ordine **tre minuti
dopo**, alle 14:00 del 27/08. Non era una stranezza dell'ordine — era il sintomo di un difetto.

**Il meccanismo, verificato nel sorgente.** La finestra di fill di **48 barre H1** (parametro
CONGELATO, §2) è calcolata in [`mql5/nxt_fade.mq5`](../mql5/nxt_fade.mq5) da `g_pending_swingend`,
variabile che **vive solo in RAM** e che `OnInit()` **non ripristinava**. Dopo ogni riavvio
dell'EA — ricompilazione, restart del terminale, **spostamento sul VPS Windows** — tornava a `0`:

1. `iBarShift(symbol, H1, 1970-01-01)` ritorna **−1**;
2. `-1 > 48` è **falso** → il pending orfano **non scade mai**;
3. subito dopo c'è `return;  // un solo setup attivo per volta` → **nessun nuovo setup viene più
   armato su quel simbolo**.

Un singolo ordine non riempito, dopo un riavvio, **spegne lo strumento in modo permanente e
silenzioso**. Nessun log di errore: l'EA sta facendo esattamente ciò che il codice gli dice.

**Impatto misurato.**

| strumento | congelato da | a | durata |
|---|---|---|---|
| **US500** | 2026-07-31 20:00 | 2026-08-27 13:57 (sblocco manuale) | **27 giorni** |
| **XAUUSD.cyr** | 2026-08-21 04:00 | tuttora al momento della scrittura | **6 giorni** |

→ **US500 non ha prodotto zero trade per assenza di segnali: era spento.** La riga *"US500:
agganciato, 1 pendente attivo, nessun fill"* del §9 descriveva questo difetto senza riconoscerlo.

**Cosa NON è toccato.** Il difetto **sottrae** trade, non ne aggiunge di spuri. Verifica sui
riempimenti realmente avvenuti (72 ordini riempiti in universo): attesa **mediana 0,0h**, solo
**3 oltre le 24h** di calendario e tutte spiegate dal weekend — le 48 sono **barre**, non ore.
Nessun fill è avvenuto su un segnale scaduto. **I valori di R raccolti restano validi; N valido
resta 36/50.**

**La correzione** (2026-08-27, `mql5/nxt_fade.mq5`):
- `OnInit()` ricostruisce `g_pending_swingend` dall'ordine vivo via `ORDER_TIME_SETUP` — proxy
  dello swing di fine con scarto **≤ 1-2 barre su 48**, e mai in difetto (il pending può vivere
  pochissimo in più, mai in meno);
- il test di scadenza tratta `age < 0` come **SCADUTO**, mai come *"tienilo per sempre"*.

Richiede **ricompilazione in MetaEditor + riattacco dell'EA**. Fino ad allora **XAUUSD resta
congelato**: il pendente del 21/08 va cancellato a mano, come è stato fatto per US500.

**Classificazione: BUG FIX.** Riporta l'esecuzione **dentro** la specifica congelata invece di
allontanarla — la spec dice 48 barre, il codice ne applicava infinite. Nessun parametro cambia,
nessun filtro aggiunto → **nessun trial consumato** ([`STRATEGY_LIFECYCLE §3`](STRATEGY_LIFECYCLE.md)).

> ⚠️ **Il caveat di composizione del §9 va letto più duro.** Questo difetto si attiva **quando
> interveniamo**: ogni manutenzione (riaggancio `.r` del 12-13/08, trasloco sul VPS) creava un
> orfano. La copertura del campione non è solo disomogenea — è **correlata al calendario delle
> nostre manutenzioni**. Il report finale deve dichiararlo insieme al breakdown per strumento.

---

## 11. TEST AZZERATO (2026-08-27) — l'EA non eseguiva la strategia congelata sul 40% dei trade

> ## 🛑 QUESTO FORWARD È CHIUSO. I 36 TRADE RACCOLTI CONTANO **ZERO**.
>
> Non è una sospensione né una riparazione in corsa. Lo Stadio 1 **non esiste più**.

### Il fatto

Su **17 ingressi su 43 in universo (40%)** l'EA è entrato **a mercato** invece che con un ordine
pendente, mantenendo SL/TP calcolati sull'entry **teorica** e il volume dimensionato sull'R
**inteso**. Risultato misurato sui trade reali:

| tipo di ordine | n | rischio reale / inteso | RR reale |
|---|---|---|---|
| `BUY_STOP` / `SELL_STOP` | 26 | 1,00× | 1:3 — conforme |
| `BUY` / `SELL` a mercato | 17 | **1,3× – 4,0×** | da 1:2,1 a **1:0,00** |

Esposizione aperta rilevata: **2,00% dell'equity** contro l'1,00% previsto.

### Perché azzera invece di riparare

Il §2 congela tre parametri: **SL 1R**, **TP 3R**, **R = 28,6% dell'ampiezza**. Il ramo a mercato di
[`mql5/nxt_fade.mq5`](../mql5/nxt_fade.mq5) li viola **tutti e tre contemporaneamente**. Non è un
difetto di contorno: su quel 40% dei trade **la strategia eseguita non è quella pre-registrata**.

Si applica il **§4.3** — *"qualunque modifica azzera il test e ne apre uno nuovo, con nuovo N e
nuova pre-registrazione"*. Il vincolo è **speculare e vale contro di noi**: riparare l'EA e
riprendere lo stesso contatore di Stadio 1 sarebbe **vietato dalla stessa clausola** che qui usiamo
per annullare.

### E comunque il numero di partenza non c'era

Indipendentemente dall'esecuzione, l'audit [`analysis/nxt/entry_fill_audit.py`](../analysis/nxt/entry_fill_audit.py)
ha mostrato che il **+0,31R non è mai stato misurato**: `closure.py` concedeva il fill al prezzo
`entry` anche sul **46,1%** dei setup in cui il mercato lo aveva già oltrepassato — un prezzo non
ottenibile. Con qualunque esecuzione realmente ottenibile l'E[R] sta fra **−0,32 e −0,03**, mai
vicino a +0,31. Vedi [`DECISIONS.md`](../DECISIONS.md), voce **2026-08-27 (2)**.

Un forward serve a validare fuori campione un numero misurato dentro campione. **Qui il numero
dentro campione non esisteva**, quindi non c'era nulla da validare.

### Conseguenze registrate

| | |
|---|---|
| N valido | **0** — i 36 trade non entrano in alcun verdetto |
| Stadio 1 / Stadio 2 | **decaduti**, insieme ai backstop 2026-10-31 e 2027-03-31 |
| trial consumati | **0** (integrità dell'esecuzione, `STRATEGY_LIFECYCLE §3`) |
| budget famiglia | invariato: **2 di 3**, holdout **già aperto** |
| nome | la famiglia è **FADE**; il rinominare **non** azzera il contatore (il fade è l'inversione della continuazione NXT sugli stessi dati) |

### ⚠️ Aggiornamento 2026-09-17 — le condizioni sono ancora aperte, e ora c'e' un numero

Verificato **nel sorgente** (`mql5/nxt_fade.mq5`, righe 432-451): l'EA **entra ancora a mercato**
quando il prezzo ha superato l'entry, con volume dimensionato sulla distanza teorica. La condizione 3
qui sotto e' **non soddisfatta**, come la 1 e la 2.

Aggiunto il calcolo che mancava, in [`FADE_LIVE_AUDIT_PROTOCOL.md`](FADE_LIVE_AUDIT_PROTOCOL.md):

- con **SD = 1,8R**, il campione live (~46 trade onesti) rileva solo effetti oltre **0,74R** — un win
  rate del 43,5% su una 1:3, che **nessuno ha mai proposto**;
- il confronto fra ramo pendente e ramo a mercato, che giustificava di lasciare l'EA rotto,
  richiederebbe **3.362 trade per ramo** (~12 anni): la giustificazione **non sopravvive**;
- il campione onesto non e' solo piccolo, e' **selezionato**: un ingresso a mercato occupa lo slot
  (una posizione per strumento) e blocca i setup successivi, e lo fa **quando il prezzo si e' mosso
  in fretta** — cioe' non a caso;
- per risolvere il FADE servirebbero **~11 mesi** (rilevare +0,31R) o **~3,6 anni** (KILL statistico).

**Condizione 5, aggiunta**: N va dichiarato **sulla base della potenza**, non scelto a occhio.

### ⚠️ Aggiornamento 2026-09-17 (2) — condizione 2 MISURATA: non e' soddisfatta, e non lo sara'

Condizione 1 **fatta**: primitiva unica [`core/resolve_trade.py`](../core/resolve_trade.py), con le
cinque convenzioni come parametri espliciti e l'equivalenza con le implementazioni storiche
**dimostrata** su migliaia di percorsi ([`core/tests/test_resolve_trade.py`](../core/tests/test_resolve_trade.py)).

Condizione 2 **misurata** con [`analysis/nxt/fade_obtainable.py`](../analysis/nxt/fade_obtainable.py),
su 10.218 setup in 14 anni e 6 asset:

| campione | n | E[R] | BCa 95% |
|---|---|---|---|
| **solo fill ottenibili (SKIP), convenzione di riferimento** | **5.506** | **−0,250** | **[−0,287 ; −0,210]** |
| solo fill ottenibili, convenzione ottimista | 5.506 | −0,186 | [−0,226 ; −0,146] |
| tutti i setup, col fill fantasma (per confronto) | 10.218 | **+0,409** | [+0,370 ; +0,443] |

Il **46,1%** dei setup ha il livello gia' oltrepassato — identico al valore dell'audit di agosto, che
e' anche una verifica incrociata della primitiva contro un numero gia' pubblicato.

> **La condizione 2 chiedeva un E[R] positivo sui fill ottenibili. Il valore e' −0,250 con
> l'intervallo di confidenza interamente negativo su 5.506 trade.** Non e' "non ancora dimostrato":
> e' **misurato negativo con precisione alta** (SE 0,020). E lo e' **sui dati da cui la strategia e'
> stata derivata**, cioe' nelle condizioni piu' favorevoli possibili.

L'intero segno positivo del lead veniva dai fill non ottenibili: **+0,409 con il fantasma, −0,250
senza**. Non e' un aggiustamento, e' un ribaltamento.

**Nota su un mio sospetto risultato infondato**: avevo segnalato che tre implementazioni su quattro
**scartavano** i trade in timeout (filtro sull'esito, non convenzione). E' vero come difetto, ma qui
e' **trascurabile**: 10 trade su 10.218 (0,1%), che spostano E[R] di 0,006R. Registrato come difetto
di metodo da non ripetere, non come causa di nulla.

**Conseguenza sulle condizioni della sez. 11**: la 2 non e' soddisfatta e non c'e' un percorso per
soddisfarla senza cambiare la strategia — cioe' senza spendere il trial #3 su una variante nuova.
Si applicano i **kill duri** di [`STRATEGY_LIFECYCLE`](STRATEGY_LIFECYCLE.md) §6a n. 1 (difetto
metodologico conclamato: i vecchi numeri sono nulli e rifatti da zero) e n. 3 (fallimento di
breadth). **Verdetto proposto all'utente: KILL della famiglia.** Non lo dichiaro io.

### Cosa serve prima che esista un forward nuovo

1. Una **primitiva unica** `resolve_trade()` in `core/`, con la convenzione sulla barra di fill e sul
   gap oltre lo stop come parametri espliciti — oggi la stessa logica è reimplementata **quattro
   volte con quattro convenzioni diverse**, ed è ciò che ha prodotto l'ambiguità +0,354 / +0,308 / +0,347.
2. Un backtest che modelli **solo fill ottenibili**, e il cui E[R] risultante sia positivo. Oggi non
   lo è per nessuna variante.
3. Un EA che **rifiuti** il setup quando non può ottenere l'entrata pre-registrata, invece di
   ripiegare su un ordine a mercato.
4. Una **pre-registrazione nuova**, con N nuovo. ⚠️ Scegliere quale variante portare avanti **dopo**
   averne visto l'esito costa **trial #3, l'ultimo del budget della famiglia**.
