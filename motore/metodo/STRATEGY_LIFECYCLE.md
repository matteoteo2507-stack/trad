# Ciclo di vita di una strategia — loop di ricerca, gate e criteri di bocciatura

> **Il problema che questo documento risolve.** Un loop di miglioramento è la cosa giusta da fare in
> ingegneria: provi, misuri, correggi, riprovi. Ma su un **dataset storico fisso** lo stesso loop è
> una **macchina per generare falsi positivi**: ogni iterazione è un tentativo in più, e se scegli la
> variante migliore fra molte stai selezionando rumore. Il loop è utile solo se accompagnato da
> **contabilità dei tentativi**, **dati sigillati** e **criteri di morte dichiarati in anticipo**.
> Senza questi tre, "ricerca → backtest → rifinitura → ricerca" è p-hacking con più passaggi.

Riferimenti teorici: [04_quant_metodologia §2](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md)
(overfitting/data snooping, DSR, PBO), [§9](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md)
(pre-mortem). Protocollo di misura: [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md).

---

## 1. Il loop, nella sequenza corretta

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
                    ▼                                              │
   RICERCA ──► FORMULAZIONE ──► [G1] PRE-REGISTRAZIONE ──► BACKTEST (solo TRAIN)
   (razionale     (ipotesi          (ipotesi, metriche,        │
    economico)     falsificabile)    soglie, N trial,          │
                                     criteri di kill)          ▼
                                                          RIFINITURA (solo TRAIN,
                                                          consuma budget trial)
                                                               │
                                                               ▼
                                                       WALK-FORWARD (solo TRAIN)
                                                               │
                                                               ▼
                                                   [G2] HOLDOUT SIGILLATO
                                                     (si apre UNA volta)
                                                               │
                                                               ▼
                                                           VERDETTO
                    ┌──────────────┬───────────────┬───────────┴────┐
                    ▼              ▼               ▼                ▼
                   GO            LEAD           NO-GO            CLOSED
              (capitale)   (nuova prereg   (questa spec        (famiglia
                            + forward OOS)   muore, famiglia     morta —
                                             vive se ha budget)  vedi §7)
```

**La fase RICERCA ha un metodo** (dal 2026-10-03): prima di cercare candidati si risponde a *chi paga,
perche' accetta, perche' non e' gia' arbitraggiato*, e si sceglie la **classe** di vantaggio (premio, flusso
forzato, errore comportamentale, informazione, velocita'). Le nove domande, nell'ordine, stanno in
[`09_fonti_di_vantaggio`](../../magazzino/fondamenti_tecnici/09_fonti_di_vantaggio/principles.md) §4 (bozza in
quarantena, da confermare con le fonti del suo §6). Un candidato senza classe e' un pattern, non un'ipotesi.

**Due differenze rispetto al loop intuitivo:**

1. **[G1] La pre-registrazione è un gate, non un passaggio.** Sta *fra* formulazione e backtest, e
   fissa **prima di guardare i dati**: ipotesi, metriche, soglie di verdetto, **budget di tentativi**
   e criteri di bocciatura. Se non è scritta prima, il test non è informativo — è una descrizione dei
   dati. Modello: i `*_PREREGISTRATION.md` in `magazzino/registro/documenti/`.
2. **La rifinitura sta *dentro* il TRAIN, mai prima dell'holdout.** Rifinire guardando risultati che
   includono i dati di validazione brucia la validazione. Il walk-forward *non* protegge da questo: i
   suoi segmenti "out-of-sample" li hai già visti se hai tarato sul full-sample.

---

## 2. Disciplina dei dati — la risorsa scarsa

Lo split si fa **all'inizio**, una volta, e non si tocca più:

| Segmento | Quota | Uso | Rinnovabile? |
|---|---|---|---|
| **TRAIN** | ~70% | Tutta l'iterazione: backtest, rifinitura, walk-forward | No, ma riutilizzabile (a costo DSR) |
| **HOLDOUT sigillato** | ~30% | **Una sola apertura per famiglia di ipotesi** | **No — una volta aperto è bruciato** |
| **FORWARD OOS** | il futuro | Validazione vera, post-verdetto | **Sì — l'unica fonte rinnovabile** |

**Regole non negoziabili:**

- L'holdout si apre **una volta per famiglia**, non per variante. Se la famiglia esaurisce il budget
  sul train senza un candidato, **muore senza aver mai aperto l'holdout**.
- Se guardi l'holdout e poi rifinisci, l'holdout **è diventato train**. Non c'è modo di tornare
  indietro: va dichiarato nel report e la famiglia perde il suo gate finale.
- Il **forward OOS è l'unico test davvero pulito** che possiamo generare a volontà — ma costa tempo
  reale. Per questo contaminarlo (optional stopping, cambi di regola in corsa) è l'errore più caro
  che possiamo fare.

---

## 3. Contabilità dei tentativi — cosa conta come "trial"

Il **Deflated Sharpe Ratio** penalizza il numero di tentativi ([`deflated_sharpe_ratio`](../core/quant_metrics.py)).
Perché funzioni, il contatore deve **persistere attraverso le iterazioni del loop**, non azzerarsi a
ogni giro. Si dichiara nella pre-registrazione e si aggiorna nel report.

> ✅ **Dal 2026-09-19 il contatore esiste davvero**: dato in [`decisioni/trial_ledger.json`](../../decisioni/trial_ledger.json),
> letto e verificato da [`motore/core/trial_ledger.py`](../core/trial_ledger.py).
> `python -m motore.core.trial_ledger` stampa lo stato di ogni famiglia (trial cumulati, round
> spesi, holdout, quota di pre-registrazioni esterne del trimestre) e `--check` esce con
> **exit 1** se un budget e' sforato o se una voce non cita le sue fonti nel repo.
> ⚠️ Tre famiglie storiche hanno il conteggio a `null` perche' **non e' ricostruibile**:
> non si inventa un numero, si applica la raccomandazione Bailey-LdP (100 × N_params) e
> lo si dichiara.

> **Test passati da `prop-lab`** (dal 2026-10-08): ogni variante e ogni apertura del fuori campione finiscono nel
> registro di `prop-lab` con l'id della famiglia; su dati reali la pipeline non parte senza una famiglia nel
> contatore con pre-registrazione APPROVATA, e `--check` segnala ogni differenza fra registro e contatore
> (`motore/prop-lab/lab/gate.py`, `core.trial_ledger.registro_prop_lab`). Il registro e' il diario, il contatore la fonte.

| Azione | Conta come trial? |
|---|---|
| Correzione di un **bug**: il codice non implementava la regola pre-registrata | **No** — è la prima esecuzione valida del trial originale. Va documentata |
| Modellazione **più realistica** di costi/slippage/esecuzione | **No** — può solo peggiorare il risultato, non è ricerca di conferma |
| Cambio di **parametro** dopo aver visto l'esito | **Sì**, uno per variante |
| Cambio di **asset o timeframe** dopo aver visto l'esito | **Sì**, uno per combinazione |
| Passaggio a un **indicatore diverso che misura la stessa grandezza** (RSI → Stocastico, media mobile → Donchian; le grandezze in [10_indicatori_tecnici §2](../../magazzino/fondamenti_tecnici/10_indicatori_tecnici/principles.md)) | **Sì**, ed e' un trial **della stessa famiglia**: non ne apre una nuova (dal 2026-10-08, DECISIONS 2026-10-08 (3)). Un **meccanismo economico** diverso resta una nuova ipotesi (ultima riga della tabella), con parentela dichiarata e senza usare come holdout i dati della famiglia simile (primo caso: DECISIONS 2026-10-09) |
| Un'ipotesi nuova tratta dalla **stessa teoria** di una famiglia esistente (es. un altro evento previsto dallo stesso modello geopolitico) | **Sì**, ed e' un trial **della stessa famiglia** (dal 2026-10-25, DECISIONS 2026-10-25 (8)): stessa teoria = stessa famiglia, come stessa grandezza = stessa famiglia. Una teoria con un **meccanismo diverso** apre una famiglia nuova |
| Aggiunta di un **filtro** | **Sì** — ed è il più pericoloso (vedi §4) |
| **Nuova ipotesi** con razionale economico indipendente | **Sì**, ma apre una **nuova pre-registrazione** |

> **Come si legge "stessa grandezza"** (dal 2026-11-21, DECISIONS 2026-11-21 e 2026-11-21 (2)). Due letture, da fare
> entrambe prima di aprire una famiglia:
> - **ingresso**: cosa legge l'indicatore dal prezzo (le sei grandezze del
>   [modulo 10 §2](../../magazzino/fondamenti_tecnici/10_indicatori_tecnici/principles.md), il tempo, la dipendenza fra
>   i rendimenti contemporanei, con le esclusioni scritte nel modulo 10 §2); e' la lettura della regola dell'08/10;
> - **bersaglio**: cosa prevede lo strumento. Stesso bersaglio con un'altra perdita = variante della stessa famiglia
>   (per la direzione, "lo stato Bull persiste" e "il segno passato guadagna" prevedono entrambi il rendimento futuro);
>   bersaglio diverso = grandezza diversa (la volatilita' prevista come varianza, contro le strategie che la usavano per
>   un rendimento).
>
> Se le due letture concordano si applica l'esito; se divergono **decide Matteo** in DECISIONS (primo caso: la forza
> dell'ADX, rimasta tendenza il 21/11).
>
> **Nel contatore** (DECISIONS 2026-11-21 (3)). Ogni famiglia dichiara nel campo `grandezze` le grandezze della sua
> **domanda primaria**: quelle lette dalle regole primarie e dal bersaglio; filtri e ingressi fissi vanno nelle note.
> Una famiglia che condivide una grandezza con un'altra o e' una **riapertura** di quella, e allora si fa sulla **stessa
> voce** del contatore (§7a: trial sommati, quota del binario d'origine, un round, binario invariato), o e' una famiglia
> **parente** (distinta per bersaglio o per meccanismo) e lo dichiara nel campo `parentela` (tipo `parente`) con la
> fonte in DECISIONS o in una pre-registrazione: senza, `--check` fallisce, e `riapertura` verso un'altra voce e' un
> errore. Esenti le 14 famiglie CLOSED al 21/11 (`ESENTI_PARENTELA` nel codice); una famiglia nuova che poi si chiude
> conserva l'obbligo. Il codice non vede la storia: che una riapertura non cambi binario lo controlla il gatekeeper.
> `segnale_esterno` (segnali
> copiati da terzi) e' un'**etichetta**, non una grandezza: non conta fra le grandezze condivise ed e' vietata ai binari
> `strumenti` e `hub`.
>
> **Grandezze composte.** Quando il bersaglio e' prodotto di due grandezze (covarianza = correlazione × volatilita' ×
> volatilita'), un confronto appartiene alla famiglia della parte che cambia: se tutte le previsioni confrontate,
> benchmark compreso, usano **lo stesso ingresso fisso** per una parte e differiscono solo nell'altra, e' un trial della
> famiglia dell'altra; se differiscono in entrambe, **conta in tutte e due e procede** nella famiglia che lo
> pre-registra (Matteo, 21/11), anche se l'altra e' CLOSED o in ridisegno. Restano i vincoli sui dati dell'altra
> famiglia (il suo holdout, i dati futuri di un ridisegno, il §7a sulla storia gia' vista). L'ingresso fisso si dichiara
> prima di ogni dato e non e' una variante (primo caso: I3, volatilita' EWMA 0,94 come ingresso fisso, DECISIONS
> 2026-11-21 (2)).

> **Regola di futilità (stop matematico).** Dato il numero cumulato di trial, esiste uno Sharpe
> minimo sotto il quale il DSR non può essere significativo. Se il **migliore** risultato osservato
> su tutte le varianti è sotto quella soglia, continuare a iterare è **matematicamente inutile**:
> serviresti un effetto più grande di qualunque cosa tu abbia mai visto. → **kill immediato**.
>
> Ora è un numero: `futility_sharpe(n_trial, n_obs)` in [`motore/core/trial_ledger.py`](../core/trial_ledger.py),
> o `python -m motore.core.trial_ledger --futilita <n_obs>`. Su **250 osservazioni** servono Sharpe
> **1,65** con 1 trial, **3,12** con 8, **4,64** con i 384 della ricerca livelli — cioè a quel punto
> del libro nessun risultato raggiungibile avrebbe potuto essere significativo. È un **pavimento
> gaussiano**: con skew negativo o code grasse la soglia sale.

---

## 4. Rifinitura legittima vs p-hacking

Il ramo "ritocca e riparti" è quello che uccide i progetti di ricerca seri. La linea è netta:

**Legittima** — la modifica è motivata da un **razionale formulato senza guardare quali trade hanno
perso**:
- Il razionale economico prevede una condizione che non avevamo implementato.
- L'esecuzione modellata era irrealistica (in senso peggiorativo).
- Bug conclamato.

**P-hacking** — la modifica è motivata **dall'esito**:
- *"20 periodi non funziona, provo 30"* → ricerca di parametri post-hoc.
- *"Non va su EURUSD, provo GBPUSD"* → shopping di asset.
- *"Funziona solo dal 2020, restringo il campione"* → vedi
  [[feedback_backtest_long_history_falsification]]: quasi sempre rumore, non rottura di microstruttura.
- *"Aggiungo un filtro che toglie i trade perdenti"* → il più seducente e il più fatale: stai
  descrivendo il passato, non modellandolo.

**Test operativo**: *avresti fatto questa modifica se il backtest fosse stato positivo?* Se la
risposta è no, è p-hacking — conta come trial e va dichiarata.

---

### 4bis. Una componente aggiunta si testa per ABLAZIONE (buco Quant Guild 11, dal 2026-10-02)

Un filtro, una condizione di regime o un'uscita alternativa aggiunti a una regola **non** si valutano come
strategie nuove. Il formato e' l'**ablazione pre-registrata**: la **stessa** regola **con e senza** la
componente, sugli **stessi** dati, ciascuna contro lo **stesso** baseline. La metrica e' la differenza
appaiata fra le due versioni sugli stessi segnali (precedente: B7, uscita a 1R contro TP1, differenza
-0,0001). E' anche la risposta operativa a *"l'analisi tecnica non si puo' smentire"*: si smentisce una
componente alla volta.

**Le condizioni che la fonte stessa prevede** (dal 2026-11-04, DECISIONS 2026-11-04, proposta 1 del 12/10): se la
fonte dice in anticipo che la regola vale *solo* in certe condizioni (un regime, una sessione, una classe di
strumenti), quelle condizioni si pre-registrano **come varianti dichiarate prima**, accanto alla regola nuda. Ogni
variante **conta come un trial** della famiglia ed entra nel DSR con tutte le altre. Una condizione che la fonte non
nomina resta un filtro (§3, §4): non diventa una variante perche' "ci stava".

### 4ter. Si sceglie il parametro POSITIVO OVUNQUE, non quello ottimo da qualche parte (buco 40)

Quando una regola ha un parametro, il criterio di scelta dichiarato nella pre-registrazione e' **"positivo in
tutti i sottoperiodi e gruppi"**, non "massimo nel campione": la politica ottima di un regime ha spesso EV
**negativo** in un altro (Quant Guild, G2: Sharpe 3,01 in addestramento, crollo fuori). La robustezza si
verifica con `core.verifiche.test_perturbazione` (buco 33): se muovere gli input del 10% sposta l'uscita
oltre la soglia dichiarata, il risultato vive sul punto, non sulla regola.

### 4quater. La gestione del rischio si legge su DUE BINARI (dal 2026-10-06)

Decisione di Matteo del 06/10, dopo la sessione col socio VELTRIX (DECISIONS 2026-10-06). Ogni test o
backtest di una strategia riporta, **a prescindere dall'esito**:

1. **binario 1R**: rischio fisso per trade. E' l'**unico** su cui si da' il verdetto sul vantaggio.
2. **binari di overlay**: la stessa sequenza di trade sotto ogni overlay della **libreria dichiarata**
   in [`motore/core/sizing.py`](../core/sizing.py) (`LIBRERIA`), fissa per tutto il repo e non scelta per strategia:

| overlay | cosa fa | obiettivo | perche' puo' servire | quando danneggia |
|---|---|---|---|---|
| **O1 cuscinetto** | rischio proporzionale alla distanza dal limite di perdita (min 0,25×) | proprio, prop | un limite duro lo giustifica anche con esiti indipendenti | costa crescita; con rischio base basso, timeout |
| **O2 guardia giornaliera** | stop alla giornata a meta' del limite giornaliero o dopo 3 trade; mai un trade che possa sforare | prop | la perdita giornaliera chiude il conto | taglia il vantaggio se e' concentrato in pochi trade del giorno |
| **O3 serie di perdite** | dimezza dopo 2 perdite di fila, fino a 0,25× | proprio, prop | solo se le perdite arrivano raggruppate | esiti indipendenti (recupero lento) o alternati (toglie valore) |
| **O4 avvicinamento al target** | dimezza oltre l'80% della strada verso l'obiettivo di fase | prop | obiettivo a barriera | inutile su capitale proprio |

**Il principio** (perche' il verdetto sta solo sul binario 1R): guadagno = Σ E[size]·E[R] + Σ Cov(size, R).
Una size decisa solo dal passato non ha covarianza con un esito indipendente: un overlay **non crea
vantaggio**, sposta il rischio nel tempo e cambia il percorso. Ha valore vero solo in due casi, che si
misurano separatamente:

- **valore di dipendenza** (capitale proprio): gli esiti sono raggruppati. Si misura con
  `confronta_overlay`, contro la **stessa sequenza rimescolata**, che azzera la covarianza. Banda al 95%:
  con esiti indipendenti ogni overlay da' un falso allarme con probabilita' 5% (misurato il 06/10 su 200
  sequenze: 7,0% e 5,5%). **E' un'ipotesi sul processo, non un risultato**: si conferma solo in forward.
- **valore di struttura** (prop): l'obiettivo e' a barriere, quindi la size ottima dipende dallo stato
  anche con esiti indipendenti. Ma vale anche per chi non ha vantaggio: si misura con
  `confronta_overlay_prop`, che riporta per ogni binario il benchmark a **vantaggio zero** e `ev_vs_zero`
  con l'incertezza di stima. Si legge `ev_vs_zero`, non l'EV grezzo. ⚠️ `ev_vs_zero` toglie il valore
  d'opzione, **non il caso**: su un random walk i candidati usciti positivi per fortuna hanno `ev_vs_zero`
  fuori campione positivo al 100% (07/10). Senza il suo intervallo (`evaluate_ci`) non si cita.

**Regole:**
- Un overlay **non salva un NO-GO e non promuove niente**. Un overlay che trasforma un 1R negativo in
  positivo e' un campanello: o dipendenza (da confermare) o un difetto.
- Aggiungere un overlay alla libreria dopo aver visto un risultato e' un **tentativo** (§3); `confronta_*`
  rifiuta i nomi fuori libreria.
- **Non sono overlay** il vol targeting, i filtri di regime e la size per "convinzione": usano informazione
  di mercato ex ante, possono avere covarianza con l'esito, quindi cambiano il segnale. Sono filtri (§4) e
  si testano per ablazione (§4bis).
- **Il rischio base si sceglie sull'intervallo, non sul picco.** Il rischio fisso che massimizza il pass
  rate di una challenge dipende dal vantaggio **e dal limite di tempo**. Misurato il 07/10 sulle regole FTMO
  2 fasi (10%+5%, daily 5%, max 10% statico, payoff 1:1), con un orizzonte di un anno perche' FTMO non pone
  limiti: l'ottimo e' ~3% con E = −0,10R, 1-2% con E = 0, **1% con +0,10 (77%) e con +0,20 (97%)**. Con un
  orizzonte di 120 giorni lo stesso calcolo metteva l'ottimo a 2% anche con vantaggio positivo: era il limite di
  tempo a spingere verso il rischio alto (il numero del 06/10, scritto qui fino al 07/10, dipendeva da quello).
  Senza limite di tempo e con un vantaggio vero vince il rischio basso; il gioco audace conviene solo a chi un
  vantaggio non ce l'ha (Dubins-Savage, da confermare). Quindi: l'**orizzonte della simulazione si sceglie sulla
  firm**, e l'ottimo puntuale su un campione premia il rumore. Si sceglie il rischio che resta buono su tutto
  l'intervallo dell'E[R].
- Scegliere fra 1R e gli overlay per operare e' una **selezione fra al massimo 5**: si dichiara, con il
  criterio "positivo ovunque" (§4ter).
- Vale **da qui in avanti**. Una famiglia CLOSED non si riapre con un overlay (§7). Il caso delle famiglie
  chiuse vicine a zero e' in [doppio_binario_closed_2026-10-06](../../magazzino/registro/referti/doppio_binario_closed_2026-10-06.md).

## 5. Tassonomia dei verdetti

| Verdetto | Significato | Cosa succede |
|---|---|---|
| **GO** | Edge sopravvive a train + walk-forward + holdout + costi | Promozione a capitale, con pre-mortem ([04 §9](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md)) |
| **LEAD** | Risultato positivo ma **data-derived** o senza OOS indipendente | **Non promuovibile.** Richiede **nuova** pre-registrazione + **forward OOS**. Stato attuale del *fade* NXT. Se l'holdout e' gia' aperto per costruzione (campione intero come holdout, es. Gump D1), il ledger lo ammette solo con `gate_finale: "forward"` dichiarato **prima** dell'esito (DECISIONS 2026-10-02) |
| **NO-GO** | Questa specifica non regge | La *specifica* muore. La *famiglia* sopravvive solo se ha budget residuo |
| **NON DIMOSTRATO** | Il test non rifiuta il nullo **e** non aveva la forza per vedere l'effetto plausibile (MDE sopra l'effetto atteso) | Si scrive **sempre con l'MDE** accanto. Non e' "refutato": la casella resta vuota, non chiusa. Puo' chiudere una famiglia, con motivo `potenza` (dal 2026-11-04) |
| **CLOSED** | L'intera direzione di ricerca è morta | Vedi §7 — non si riapre con un ritocco |
| **INSUFFICIENT DATA** | `n_trades < 50` | **Non è un verdetto.** Si continua a raccogliere **solo se la soglia era pre-dichiarata** |

**Verdetto di un test e stato di una famiglia sono due cose** (dal 2026-11-04, debito E7). NO-GO, NON DIMOSTRATO e
NULL sono l'esito di un test; CLOSED e' lo stato della famiglia. Quando una famiglia chiude, il contatore registra
**perche'** nel campo `motivo_chiusura` di [`trial_ledger.json`](../../decisioni/trial_ledger.json), controllato da
`motore/core/trial_ledger.py`:

| motivo | significato | vale come prova che l'effetto non c'e'? |
|---|---|---|
| `refutata` | il test aveva la forza per vedere l'effetto atteso e lo ha escluso | **si'** |
| `potenza` | NON DIMOSTRATO: l'MDE supera l'effetto plausibile | **no** |
| `criterio` | chiusa su un criterio dichiarato prima, senza test | no |
| `metodo` | difetto di metodo o di dati: i numeri non valgono | no |
| `null` | le fonti non permettono di dirlo | no: non si inventa |

---

## 6. Criteri di bocciatura

### 6a. Kill duri — nessun ramo di rifinitura disponibile

Questi non si aggiustano con un parametro. Quando scattano, la strategia (o la famiglia) muore.

1. **Difetto metodologico conclamato** — look-ahead **di informazione** (survivorship, finestre
   sovrapposte, dati contaminati) *oppure* look-ahead **di prezzo** (fill non ottenibile: si transa
   a un livello disponibile solo *prima* di poter agire). I risultati sono **nulli**, non "da
   correggere": vanno rifatti da zero e il vecchio numero non si cita più. *Precedenti: London
   Breakout, edge da regime gating look-ahead · FADE NXT, **+0,409 → −0,250** togliendo il 46,1%
   di fill fantasma → KILL della famiglia (2026-09-17).* ⚠️ Il difetto **non ha un segno**: lo
   stesso fantasma aveva reso il NO-GO della continuazione NXT troppo severo (−0,44R contro
   −0,118R onesto). Gate di verifica: [QUANT_REVIEW_PROTOCOL.md Step 3bis](QUANT_REVIEW_PROTOCOL.md).
2. **Non batte il baseline random** matched (stessa geometria, stessi tempi, distance-matched).
   *Precedente: ricerca livelli, 384 trial, NULL su ogni timeframe.*
3. **Fallimento di breadth** — negativa sulla maggioranza degli asset **e** dei periodi testati.
   Nessun set di parametri ripara una cosa che non c'è. *Precedente: NXT, 14/14 anni e 6/6 asset
   negativi.*
4. **Muore sui costi realistici** — l'edge esiste lordo e sparisce con spread/slippage/commissioni.
5. **Instabilità parametrica** — piccole variazioni ribaltano l'esito. Già NO-GO in
   [04](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md).
6. **Razionale economico falsificato** — non è il numero a fallire, è il *perché*. Se "i livelli sono
   zone di reazione" è falso, muore la **famiglia**, non la singola implementazione.

### 6b. Kill di budget — l'anti-loop-infinito

Servono a impedire che un progetto diventi uno zombie. Si dichiarano nella pre-registrazione.

- **Massimo 3 round di rifinitura** per famiglia di ipotesi. Al quarto giro senza un candidato:
  **kill**. Se dopo tre tentativi motivati non emerge nulla, il problema è l'ipotesi, non la taratura.
- **Budget di trial esaurito** → kill (e il DSR usa il conteggio **cumulato**, non quello dell'ultimo
  giro).
- **Regola di futilità DSR** (§3) → kill immediato, indipendentemente dal budget residuo.
- **Budget di tempo**: se una famiglia occupa più di una finestra di ricerca dichiarata senza
  arrivare a un gate, si sospende e si passa al backlog.

> **Lezione dal nostro registro.** La ricerca livelli è arrivata a **384 trial** su tre round (v1
> OHLC, v2 volume, v3 HTF) prima di chiudere il libro. Con un budget dichiarato in partenza sarebbe
> morta a v2, risparmiando un round intero. È esattamente il costo che questa sezione esiste per
> evitare.

---

## 7. Riapertura di una famiglia CLOSED

Una famiglia chiusa **non si riapre con un ritocco, un parametro nuovo o "riproviamo con più dati"**.
Si riapre **solo** con **evidenza esterna nuova**:

- una fonte dati nuova che prima non avevamo (non gli stessi dati riorganizzati);
- una classe di strumenti realmente diversa;
- un risultato pubblicato e verificabile che contraddice il nostro null.

Un indicatore diverso che misura la **stessa grandezza** non e' evidenza esterna nuova: appartiene alla stessa famiglia
(§3, dal 2026-10-08). Lo stesso vale per un'altra ipotesi tratta dalla **stessa teoria** (§3, dal 2026-10-25).

⚠️ **Eccezione decisa da Matteo il 2026-11-21, da rivedere al rituale**: un confronto di **grandezze composte** che
cambia entrambe le parti conta anche nella famiglia CLOSED e procede nella famiglia che lo pre-registra, senza §7 (§3,
"Grandezze composte"; restano i vincoli sui dati della famiglia chiusa). Non e' una riapertura: dove si registra quel
trial, se consuma un round della famiglia chiusa e quale conteggio usa il DSR non sono ancora scritti e si decidono a
mano (DECISIONS 2026-11-21 (3)).

Qualunque altra riapertura è il bias di conferma che si ripresenta col cappello. *Precedente
vincolante: la ricerca livelli è CHIUSA — non riproporre "testiamo i livelli".*

### 7a. Come si contabilizza una riapertura (dal 2026-11-04, debito E7)

Quando il §7 e' soddisfatto, la riapertura:
- e' una **pre-registrazione nuova nella stessa famiglia**, non una famiglia nuova;
- **somma** i suoi trial a quelli gia' spesi: il contatore non riparte da zero, e il DSR usa il cumulato;
- **consuma una quota** del trimestre, quella del suo binario (strategie o hub);
- **non puo' validarsi sui dati che hanno generato l'idea**: i dati gia' guardati restano dati di scoperta.
- **non cambia binario** (Matteo, 21/11): una famiglia CLOSED del binario strategie o hub riproposta come
  **strumento** (§8ter) resta la stessa famiglia e una riapertura. Servono il §7 e la quota del binario d'origine, e si
  consuma un round; il binario `strumenti`, che non ha quota, non e' una via d'ingresso per le famiglie chiuse
  (DECISIONS 2026-11-21 (2)). Cosa controlla il codice (§3, DECISIONS 2026-11-21 (3)): vieta la riapertura da un'altra
  voce; per le 14 famiglie CLOSED al 21/11 controlla che il binario resti `strategie` e che i trial non scendano sotto
  quelli di allora. Per le famiglie successive il binario invariato lo controlla il gatekeeper sul diff del contatore.

### 7b. Forward di una famiglia CLOSED (dal 2026-11-04)

Registrare in avanti una famiglia chiusa **e' ammesso senza il §7**, a quattro condizioni: la regola e' **identica**
a quella testata, la soglia di verdetto, l'inizio e il numero di osservazioni sono **dichiarati prima**, non c'e'
capitale, e il registro e' salvato in git man mano. Costa **0 trial**: non si cerca niente, si misura la stessa cosa
su dati nuovi. Era gia' la condizione di riapertura scritta caso per caso per il mentore (DECISIONS 2026-10-25 (6))
e per il VTOB (2026-10-13 (5)): da qui vale per tutte.

### 7c. Un'ipotesi nata da un descrittivo (dal 2026-11-04, proposta 2 del 12/10)

Un'ipotesi suggerita dai descrittivi di un test (l'"annata buona", un terzile, una sessione) ha **una sola** prova di
conferma, e **solo su dati forward**, cioe' nati dopo la data della sua pre-registrazione. Un holdout "mai aperto"
non basta: che nessuno l'abbia letto non si puo' verificare (referto H1, 12/10, §7). La prova si fa come un forward
del §7b, ma la regola **non** e' quella gia' testata: e' un trial della stessa famiglia e segue la contabilita' del
§7a (trial sommati, quota del binario). Fallita la conferma, l'ipotesi si cancella.

Finche' i dati forward non bastano, l'ipotesi sta **parcheggiata** in
[`BACKLOG_RICERCA.md`](../../decisioni/BACKLOG_RICERCA.md), sezione "Ipotesi nate da un descrittivo", con famiglia, stato
`quarantena` e data `scade` (la sezione nasce con la prima voce). Senza parcheggio tornerebbe fra qualche mese come
idea nuova.

---

## 8. Cosa entra nel loop dall'esterno

Le fonti esterne (canali, video, materiale di terzi) entrano da
[`decisioni/_INTAKE.md`](../../decisioni/_INTAKE.md) e alimentano la fase **RICERCA**,
mai le fasi successive. Due vincoli:

- **Si raccolgono le regole, si scartano le statistiche dichiarate.** Un "90% win rate" non deve
  entrare nel prior. Storico del repo: 60-70% dichiarato → 13,3% misurato (NXT); 80-90% → ~53%
  (VELTRIX); 90% → ~20% (playbook Chart Fanatics, test di terzi).
- **Budget di ipotesi esterne dichiarato**: max **2-3 pre-registrazioni per trimestre** da fonti
  esterne. Un funnel aperto non produce più edge — produce più penalità DSR su quelli veri.
- **Provenienza dell'ipotesi dichiarata** — rischio nuovo, non previsto dalla prima stesura di
  questo documento. Il knowledge cutoff del modello che assiste la ricerca è **maggio 2026**:
  un'ipotesi **proposta dall'LLM** su dati **precedenti** a quella data **non è una predizione
  indipendente**, può essere memorizzazione. Vale solo se arriva da (a) una **fonte esterna umana**
  datata e citabile, (b) un **razionale economico** che non richiede di conoscere l'esito, o (c) un
  **forward oltre il cutoff**. Si registra nel campo `provenienza_ipotesi` di
  [`decisioni/trial_ledger.json`](../../decisioni/trial_ledger.json), e `python -m motore.core.trial_ledger` segnala chi non
  l'ha dichiarata. Evidenza esterna: *Profit Mirage* (arXiv 2510.07920) — spostando la finestra di
  test oltre il cutoff, **quasi tutti** gli agenti LLM pubblicati **non battono un baseline
  random**. ⚠️ Corollario che va nella direzione opposta a quella che verrebbe da pensare: questo
  **rafforza** il valore del forward OOS, che resta l'unica validazione non contaminabile.

### Ingresso dall'hub (dal 2026-10-25)

> Lato ricevente del ponte con il vault `claude-brain` (lato hub: `../CLAUDE.md`, "Lavorare su `trad` dall'hub").
> Fissato con il gatekeeper il 25/10 su richiesta di Matteo; da rivedere nel rituale
> ([`decisioni/mappa/_modifiche.md`](../../decisioni/mappa/_modifiche.md)). Prima prova: l'idea "insider pesati con la geopolitica",
> [intake del 25/10](../../magazzino/registro/referti/idee_matteo_hub_intake_2026-10-25.md).

Un'idea che nasce nell'hub (appunti di Matteo, studio, geopolitica) arriva in [`decisioni/Da distillare/`](../../decisioni/Da%20distillare/README.md)
come ogni altro materiale. Diventa un'**ipotesi** di `trad` solo con questa scheda. Si legge in ordine e **ci si ferma
al primo campo che manca**.

**1. Sei campi del ponte** (la griglia del modulo 09 non li copre):

| Campo | Cosa contiene | Si respinge se |
|---|---|---|
| **P1 · Fonte unica** | link alla nota dell'hub da cui nasce l'idea, data, chi l'ha avuta; la scheda richiama la nota, non la copia | manca il link |
| **P2 · Provenienza** | (a) chi ha avuto l'idea; (b) chi ha scritto razionale e specifica: Matteo, Claude in una sessione sull'hub, una fonte umana datata e citata; la finestra dei dati del test rispetto al cutoff; se il tema e' "famoso e discusso" | provenienza non dichiarata (vale come il caso peggiore, [QUANT_REVIEW_PROTOCOL](QUANT_REVIEW_PROTOCOL.md), "Provenienza"); razionale scritto dall'LLM su dati anteriori al cutoff senza un forward previsto (vincolo sopra) |
| **P3 · Controllo contro il repo** | famiglia esistente? stessa grandezza di una famiglia del contatore? riga delle "chiuse in partenza" di [BACKLOG §H](../../decisioni/BACKLOG_RICERCA.md)? | ripropone una famiglia CLOSED senza evidenza del §7; stessa grandezza presentata come famiglia nuova (§3); cade fra le chiuse in partenza senza che sia scattata la loro condizione "si riapre se" |
| **P4 · Dati gia' guardati** | grafici, episodi, "l'ho visto succedere" visti nell'hub; "nessuno" e' una risposta valida | il campo manca. Dati gia' visti non fanno da holdout: un'idea nata da quei dati arriva al massimo a LEAD (§5) |
| **P5 · Misura fatta nell'hub** | solo se l'idea viene da un registro (es. le previsioni): cosa si e' misurato e su quante osservazioni, metrica e riferimento, intervallo, criterio scritto **prima** con il commit dell'hub che lo data, quante serie o categorie sono state misurate | criterio non datato prima della misura, o nessun riferimento: e' un descrittivo; statistiche di terzi al posto di una misura (vincolo sopra); per la geopolitica, misura assente |
| **P6 · Baseline previsto** | una riga: che cosa si randomizza | manca (G1 del gatekeeper, Checklist 1) |

**2. Le nove domande** del [modulo 09 §4](../../magazzino/fondamenti_tecnici/09_fonti_di_vantaggio/principles.md), cosi' come sono.
Respingono: classe assente (un candidato senza classe e' un pattern: riga in `_INTAKE.md`, niente pre-registrazione);
"chi paga" incompleto; accessibilita' fuori perimetro ("CFD retail, capitale piccolo, dati liberi", DECISIONS
2026-10-03 (4); allargato all'azionario il 2026-10-25 (3)) o dato a pagamento senza la regola di [BACKLOG §G](../../decisioni/BACKLOG_RICERCA.md); potenza fuori scala (si chiude
a 0 trial, come COT e carry il 03/10); "dove muore" senza un esito numerico. Il limite all'arbitraggio non respinge:
"nessuno l'ha visto" si annota come prior basso.

**3. Caso geopolitica** (registro delle previsioni, `../projects/geopolitica.md`). P5 porta:
- il registro **intero**, non filtrato; la data di emissione e' il commit sull'hub, e una riga modificata dopo
  l'emissione non vale;
- solo previsioni **risolte** con un riferimento dello stesso giorno;
- Brier proprio, Brier del riferimento e **differenza appaiata** per domanda, con bootstrap a cluster sull'evento, piu'
  la curva di calibrazione;
- il criterio dichiarato prima (es. il limite alto dell'intervallo di Brier proprio − riferimento sta sotto zero); se
  non passa, l'MDE accanto;
- quanti temi o categorie sono stati misurati: promuoverne uno solo e' una selezione multipla;
- domande con lo **stesso orizzonte** del test in `trad`;
- la mappa evento → asset (settore, direzione, orizzonte) scritta **prima** di guardare un rendimento: battere un
  mercato di previsione non vuol dire battere il mercato azionario, che puo' aver gia' prezzato;
- la potenza del test in `trad` calcolata all'ingresso: se e' fuori scala si chiude a 0 trial anche con una fase 1
  positiva.

Un numero minimo di previsioni **non e' fissato**: senza calcolo di potenza sarebbe inventato. La forma e'
MDE = 2,80 × sd(d) / √n_eff, dove d e' la differenza di Brier per domanda e n_eff conta come una sola le domande sullo
stesso evento. Il calcolo e' fra gli Aperti della nota dell'hub e aspetta la scelta del riferimento.

**4. Esiti e dove si registrano.** In ogni caso la voce si cancella dalla cassetta d'uscita dell'hub
(`../laboratorio/pending.md`). Le chiusure le dichiara Matteo.

| Esito | Quando | Dove |
|---|---|---|
| **Respinta** | un campo P manca o fa scattare il rigetto, o ci si ferma alle domande 1, 2, 6, 7 o 8 | `_INTAKE.md` ("chiuso all'intake, 0 trial", motivo, condizione di riapertura); nota in `magazzino/registro/referti/`; `DECISIONS.md` con la decisione di Matteo |
| **Parcheggiata** | condizione nota lato `trad`: dati, perimetro, budget | `_INTAKE.md` (`parcheggiato`) + riga del BACKLOG §D o §G con "si sblocca se" |
| **Rimandata all'hub** | cio' che manca vive nell'hub (es. la misura di fase 1) | resta nella nota dell'hub (fonte unica); in `trad` al piu' una riga di `_INTAKE.md` con il link |
| **Accettata** | passa scheda e griglia | `_INTAKE.md` (`distillato`) + riga del BACKLOG §B; famiglia e slot li decide Matteo in `DECISIONS.md`; il contatore la registra all'approvazione della pre-registrazione |

**5. Contabilita'.** Scheda, griglia e potenza sui numeri pubblicati costano **0 trial**, purche' non si guardino
rendimenti nostri del segnale (precedente: COT, 03/10). Il trial si spende all'approvazione della pre-registrazione
(§3). Il registro di Brier dell'hub non e' un trial di `trad`: non misura rendimenti. Un condizionamento venuto
dall'hub sopra un segnale esistente (es. un peso geopolitico) e' un **filtro**: un trial, testato per ablazione (§4bis).

**Decisioni di Matteo (25/10, DECISIONS 2026-10-25 (8)), prese dopo una simulazione del percorso geopolitica → `trad`:**
1. **Quota separata.** Le ipotesi dall'hub hanno un budget loro: **1 pre-registrazione a trimestre**, che non tocca le
   2-3 da fonte esterna delle strategie. La famiglia porta `binario: "hub"` nel contatore, e `python -m motore.core.trial_ledger`
   controlla le due quote separatamente. I trial di entrambi restano nello stesso contatore e nello stesso DSR: il budget
   separato regola il ritmo, non sconta la penalita' dei tentativi.
2. **Provenienza `utente_llm`**: un'idea di Matteo con il ragionamento scritto insieme a Claude vale come predizione
   indipendente solo su dati oltre il cutoff; sul passato e' trattata come proposta dall'LLM (il contatore la controlla).
3. **Fase 1 positiva = solo condizione necessaria.** Battere il riferimento apre la porta al test in `trad`, ma non entra
   nel giudizio del test: dice che si sa prevedere, non che l'asset non abbia gia' prezzato.
4. **Esclusioni geopolitiche (fase 2)**: famiglia nel contatore di `trad` (i trial si contano qui), decisione di cambiare
   il PAC dentro il pilastro investing, con commit separati.
5. **Le idee rimandate all'hub si tracciano anche in `_INTAKE.md`**, con una riga e il link: un'idea proposta piu' volte
   non deve essere ritrovata come nuova (World Monitor, 25/10).
6. **Stessa teoria = stessa famiglia** (§3).

**Cosa la simulazione ha mostrato, per chi prepara il primo test:** l'unita' d'inferenza e' l'**evento**, non il trade
(intervalli a cluster sull'evento, `motore/core/random_baseline.py`, `gap_ci`); il baseline e' lo stesso asset sullo stesso
orizzonte in date casuali; un backtest geopolitico sul passato e' un'illustrazione, non una prova; nessun capitale prima
di una fase 1 misurata, al piu' posizioni simulate registrate in avanti. Manca ancora un calcolatore di potenza per studi
su eventi: si scrive (0 trial) quando arriva la prima ipotesi.

---

## 8bis. Dopo il capitale — ritiro, incubazione, riattivazione

> **Buco colmato il 2026-08-17.** Fino a qui il documento copre **nascita e morte prima del
> capitale**: il loop finisce al verdetto. Non diceva nulla su *cosa succede a una strategia già
> operativa che peggiora*. Serve adesso, non domani: il fade è in forward e il copier mentore va in
> live. Innesco esterno: fonte *Noel T.* ([`_INTAKE.md`](../../decisioni/_INTAKE.md)), che
> gestisce un parco di algoritmi con rotazione e incubazione.

**Il problema.** Spegnere una strategia perché "ultimamente perde" è **optional stopping applicato
al capitale**. La performance di qualunque edge reale è rumorosa: se il criterio è discrezionale, si
spegne sistematicamente dopo il drawdown — cioè **al minimo** — e si riaccende dopo il recupero.
È comprare caro e vendere a buon mercato sulle proprie strategie. La versione discrezionale della
fonte (*"se perde per qualche mese, riduci o spegni"*) ha esattamente questo difetto.

**La regola: si giudica contro la distribuzione, non contro l'umore.** Il backtest non fornisce solo
un E[R]: fornisce la **distribuzione attesa dei drawdown e delle serie negative**. Una strategia va
ritirata quando esce da quella distribuzione, non quando fa male.

Da dichiarare **nella pre-registrazione, prima del capitale**, insieme alle soglie di verdetto:

| Soglia | Come si fissa |
|---|---|
| **DD di ritiro** | percentile alto (es. 95°) del maxDD nella simulazione Monte Carlo del backtest. Sopra quello, la strategia è fuori distribuzione |
| **Serie negativa di ritiro** | percentile alto delle perdite consecutive attese |
| **Finestra minima** | numero di trade sotto il quale **non si valuta affatto** (stesso pavimento del §5: sotto, non è un verdetto) |

**Stati dopo il capitale**, con le transizioni consentite:

```
   LIVE ──(fuori distribuzione)──► INCUBAZIONE ──(criterio di rientro)──► LIVE
     │                                   │
     │                                   └──(secondo fallimento)──► RITIRATA (definitiva)
     └──(razionale economico falsificato / difetto metodologico)──► RITIRATA (subito)
```

- **INCUBAZIONE** = continua a girare in **simulazione**, con le stesse regole, e continua a
  raccogliere dati. Non è un cestino: è l'unico modo di distinguere "rotta" da "sfortunata".
- **Criterio di rientro dichiarato prima**, mai deciso guardando la curva. Una **seconda** uscita
  dalla distribuzione dopo un rientro = **RITIRATA definitiva**: due fallimenti indipendenti non
  sono sfortuna.
- Il ritiro per **razionale falsificato** o **difetto metodologico** (kill duri §6a n. 1 e n. 6)
  è **immediato e non passa dall'incubazione**: lì non c'è niente da incubare.

### Sorveglianza in codice (buchi Quant Guild 5, 22, 27, 28, 29, 41 — dal 2026-09-30)

Le soglie qui sopra erano **percentili**: dicono dove fermarsi, non **quando** il forward ha iniziato a
tradire il backtest. Da dichiarare nella stessa pre-registrazione, con le primitive di
[`motore/core/verifiche.py`](../core/verifiche.py):

| Cosa | Primitiva | Regola |
|---|---|---|
| **Finestra di misura del conto live** (buco 41) | — | data d'inizio, attività incluse e numero di trade della valutazione si scrivono **prima** di guardare. Lo stesso conto da' Sharpe **0,88 o 6,28** cambiando solo la data d'inizio (Quant Guild, G3). I trade gia' visti prima della dichiarazione **non entrano** |
| **Indipendenza degli esiti** (buco 29) | `runs_test` | prima di fissare serie negative e DD da un Monte Carlo che rimescola i trade. Se `z < 0` (esiti raggruppati) le soglie i.i.d. sono **ottimiste**: si usa il ricampionamento a blocchi (precedente: copier C3, z = −3,37) |
| **Serie negativa attesa** (buco 27) | `attesa_trade_prima_di_k_perdite`, `prob_serie_perdite` | il riferimento analitico accanto al percentile simulato. Con win rate 50%, 5 perdite di fila arrivano in media entro **62** operazioni: non sono un segnale |
| **Degrado del win rate** (buco 5) | `SPRTBernoulli(p0, p1)` | test sequenziale con errori dichiarati (α falso allarme, β degrado non visto), aggiornato trade per trade. p0 dal backtest, p1 = degrado che si vuole vedere |
| **Degrado del payoff** (buchi 5, 28) | `CUSUMInferiore(mu0, sigma0, k, h)` | sulla media di R, con le **innovazioni standardizzate** registrate: media ~0 e varianza ~1 se il modello regge |
| **Taratura delle soglie** (buco 22) | `test_eccedenze` | ogni soglia "peggior x%" si verifica contando le eccedenze realizzate contro quelle attese. Un limite superato molto piu' spesso del dichiarato **sottostima il rischio** |
| **DD e serie di ritiro con incertezza sui parametri** (buco 13, priorita' 2) | `rischio_percorsi(r, n_trade, incertezza_parametri=True, blocco=...)` | il Monte Carlo classico rimescola gli stessi trade come se l'E[R] stimato fosse quello vero; qui ogni percorso parte da un campione ricampionato, e le code si allargano quanto l'incertezza della stima |
| **Soglie come probabilita' di violazione** (buco 39, priorita' 2) | `probabilita_violazione(valori, soglia)` | si dichiara "questo DD di ritiro scatta per caso con probabilita' p ± se", non "e' il 95esimo percentile" |

⚠️ **I parametri di riferimento sono quelli FISSI della pre-registrazione, mai statistiche mobili
ristimate in corsa**: una banda mobile si ricentra dopo una rottura e **assorbe il degrado**, e dopo
qualche settimana il livello peggiore diventa "atteso" (Quant Guild, C4).

**Cosa NON si fa.** Non si ritara la strategia durante l'incubazione — sarebbe rifinitura su dati
che includono il periodo negativo, cioè il p-hacking del §4 con il capitale già in gioco. Se serve
una modifica, è una **nuova specifica** e riparte dal gate [G1].

---

## 8ter. Strumenti di lettura del prezzo — gate, holdout, varianti (dal 2026-11-11)

Uno **strumento** produce una lettura con una proprieta' misurabile e nessuna regola di trade
([04 §0](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md)): non ha un'attesa in R, quindi il
baseline casuale e il DSR non si applicano. Al loro posto valgono le regole sotto, adottate da Matteo l'11/11
(DECISIONS 2026-11-10 e 2026-11-11). Le fonti di ogni regola stanno nel
[referto del 10/11](../../magazzino/registro/referti/gate_strumenti_volatilita_2026-11-10.md); qui c'e' la versione in
vigore. Il resto del ciclo vale come per le strategie: pre-registrazione, contatore unico, tetto di **3 round** per
famiglia, **una** apertura dell'holdout, verdetto con l'MDE.

**Nel contatore**: binario `strumenti`, **nessuna quota trimestrale**. La famiglia dichiara `alfa_famiglia` e le
`sottofamiglie` (ognuna con `alfa`, `benchmark`, `trial_cumulati`, `varianti_esplorative`); `trial_cumulati` della
famiglia e' la somma di confermativi ed esplorativi; `holdout_inizio` si scrive prima di aprire. `--check` lo verifica.
Senza quota, il freno al numero di famiglie e' "stessa grandezza = stessa famiglia" (§3): si controlla **prima** di
aprirne una.

**Procedura per una famiglia di strumenti** (dal 2026-11-21; i primi casi sono I2 e I3 del backlog §I). Fra un passo
e l'altro decide Matteo; ogni passo finisce con un referto, una revisione del gatekeeper e un commit.
1. **Controllo delle grandezze** (§3, Checklist 10 punto 8), prima di qualunque dato: candidato per candidato, la
   grandezza per ingresso e per bersaglio, le famiglie esistenti, le misure gia' calcolate sulla stessa grandezza
   (dati gia' visti). Esito: famiglia nuova, trial di una famiglia esistente (se e' CLOSED, una **riapertura**: §7 e
   §7a), o fuori perimetro.
2. **Proprieta' e potenza**, prima di ogni dato: la **classe** si dichiara, e per una misura di rischio vale "nessuna"
   (come la volatilita', modulo 10 §2); "chi paga" e limite all'arbitraggio (modulo 09) si cercano solo per una
   sottofamiglia di **premio**. Poi bersaglio, perdita e benchmark (sotto, "Bersaglio diverso dalla varianza"), l'MDE
   coi dati in casa e i dati acquistabili che mancano (regola d'acquisto, backlog §G).
3. **Bozza di pre-registrazione** e passate G1 del gatekeeper, fino all'approvazione di Matteo. Nessun test prima.

**Bersaglio diverso dalla varianza** (dal 2026-11-21). G1-G3 sotto sono scritti per la volatilita'. Per una famiglia
con un altro bersaglio (per esempio la correlazione, I3), **Matteo decide al passo 2, prima della bozza**: la misura
realizzata del bersaglio, la perdita primaria e i benchmark. Restano fissi i principi di G1-G3: misura realizzata col
proxy meno rumoroso disponibile; perdita primaria che ordina i modelli come il bersaglio vero quando il proxy e'
rumoroso ma non distorto (per la varianza QLIKE e MSE, Patton 2011); benchmark semplici nominati prima, compreso uno
senza parametri stimati. Le regole scritte per la varianza si leggono cosi': **G6** e' l'MDE sul differenziale della
perdita primaria decisa al passo 2 (non della QLIKE); **G7** solo se lo strumento promette le code del suo bersaglio;
**G9** e' un controllo positivo e negativo su un processo simulato noto **per quel bersaglio**, dichiarato al passo 2
(non un GARCH contro un EWMA). G4, G5 (se la perdita lo consente), G8, holdout, conteggio, varianti e sottofamiglie
valgono senza cambiamenti.

**Ingresso fisso da un'altra famiglia** (Matteo, 21/11). Una famiglia A usa come ingresso fisso l'uscita di una
famiglia B (§3, grandezze composte). Se B e' in ridisegno su dati futuri (come `volatilita`, DECISIONS 2026-11-20 (2)),
la regola dei dati futuri per i soci vale anche per `trad`, con la stessa decorrenza e le stesse conseguenze:
- **decorrenza**: dal giorno della pre-registrazione del ridisegno di B fino alla fine del test che quella fissa;
- **cosa non si riporta**: in quel periodo A non riporta risultati **per modello** di B (le diagnostiche dell'ingresso
  fisso: calibrazione, residui, livello della varianza) calcolati sui **dati del test di B**;
- **prima della decorrenza**: le diagnostiche di B gia' calcolate da A su dati precedenti si dichiarano alla
  pre-registrazione del ridisegno, fra le informazioni gia' ricevute;
- **se succede lo stesso**: Matteo registra in DECISIONS quali strumenti e orizzonti di B tocca il risultato (non il
  numero), e quelle coppie escono dal test di B.
Chi legge un blocco sigillato di B lo dichiara prima di leggerlo.

**Gate statistico**
- **G1 Bersaglio**: la varianza all'orizzonte dichiarato, misurata con la varianza realizzata da barre a 5 minuti
  (indici, DAX, oro da M1, futures da M1); per l'FX da barre H1, dichiarata come misura piu' rumorosa. Sessione o
  giornata intera con la notte: si fissa nella pre-registrazione.
- **G2 Perdita**: primaria la **QLIKE** sulla varianza, secondaria la MSE sulla varianza; le altre solo descrittive.
  Nessun cambio di perdita dopo l'esito.
- **G3 Benchmark nominati prima**: EWMA (λ = 0,94); media di lungo periodo e persistenza come riferimenti di skill;
  GARCH(1,1) e HAR-RV come benchmark forti; una combinazione semplice fra i candidati. Sui dati intraday si toglie la
  stagionalita' oraria.
- **G4 Test**: un candidato, Diebold-Mariano con correzione HLN ed errori HAC (o Giacomini-White); piu' candidati,
  **SPA** (p-value `consistent`) contro il benchmark, **StepM** per sapere quali lo battono, **MCS** (statistica di
  range, livello dichiarato) per scegliere, preferendo il piu' semplice. Bootstrap stazionario, almeno 1.000
  ripetizioni (5.000 vicino alla soglia), seme fisso, blocco √T con una prova di sensibilita'. Libreria `arch`, ma
  SPA e StepM **studentizzati** con `spa_studentizzato` e `stepm_studentizzato` di `motore/core/verifiche.py`: in
  `arch` 8.0.0 il parametro `studentize` non cambia la statistica, e un modello rumoroso nasconde quello buono
  (verificato il 13/11 sul sorgente). Per piu' ipotesi con quote: `procedura_grafica_nodi`; p-value con `pvalue_spa`.
- **G5** Mincer-Zarnowitz solo come diagnostica, in livelli, con errori HAC; mai in logaritmi per un verdetto.
- **G6 Potenza prima**: l'MDE sul differenziale di QLIKE si stima sui dati di sviluppo prima di aprire l'holdout; un
  mancato rifiuto si scrive "non dimostrato, MDE = ...".
- **G7 Code**, solo se lo strumento le promette: Kupiec, Christoffersen e quantile dinamico al 95% e al 97,5% (99% solo
  descrittivo: con 250 giorni la potenza e' circa 0,24); PIT e Berkowitz; log score per i modelli a regimi.
- **G8 Piu' strumenti**: un test per strumento con correzione di Holm sui p-value dello SPA, oppure un universo unico
  modello × strumento con date allineate. Si dichiara quale.
- **G9 Controllo della pipeline**: su dati simulati con processo noto, il gate deve trovare un GARCH vero quando c'e' e
  non trovare nulla su un EWMA/IGARCH puro (controllo positivo e negativo).

**Holdout**
- **H1** Un blocco finale di calendario **comune a tutti gli strumenti**; per la volatilita' **due anni** (Matteo,
  11/11). La data d'inizio sta nella pre-registrazione di famiglia, scritta prima di qualunque test, dopo aver
  allineato le date di fine dei file. Uno strumento tenuto da parte e' solo una prova complementare.
- **H2** Sviluppo a origine mobile solo prima dell'holdout; almeno h giorni fra stima e bersaglio; nell'holdout i
  parametri si ristimano con la regola dichiarata, senza scelte nuove.
- **H3** Finestra di stima mobile di lunghezza fissa dichiarata, ristima settimanale, gaussiana QMLE; niente finestra
  crescente (rende il differenziale non stazionario e invalida GW e MCS).
- **H4** **Una sola apertura** per famiglia, in cui si testano insieme tutte le sottofamiglie pronte; le sottofamiglie
  pronte dopo usano dati forward successivi all'apertura, con l'errore rimasto.
- **H5** Dopo l'apertura nessuna scelta (finestra, perdita, distribuzione, numero di regimi). Piu' punti di divisione
  solo con la statistica min-p di Hansen-Timmermann, dichiarata prima: scegliere la divisione dopo porta il 5% al 15%.
- **H6** Si dichiara prima quali regimi contiene il blocco, per leggere bene un esito "calmo".

**Conteggio delle varianti**
- **C1** Ogni variante di cui si calcolano le previsioni entra nel contatore, anche se scartata a vista.
- **C2** Lo SPA e l'MCS di una sottofamiglia includono **tutte** le varianti pre-registrate, comprese le pessime.
- **C3** Finestra, distribuzione e frequenza di ristima sono varianti se scelte dopo aver visto le perdite.
- **C4** Una curva di specificazioni dichiarata prima, con un test congiunto come verdetto, conta come un test solo.
- **C5** Correggere un bug o un look-ahead non e' una variante (§3); cambiare un parametro dopo l'esito si'.

**Varianti nate dopo un esito**
- **P1** Sono **esplorative**: niente verdetto, niente holdout, niente errore di famiglia.
- **P2** Entrano comunque nel contatore (`varianti_esplorative`) e si riportano solo dentro la curva di tutte le
  varianti provate.
- **P3** Diventano confermative solo con una pre-registrazione nuova e **dati forward non visti**, con una quota
  d'errore fissata prima (per esempio α·6/(π²k²) alla k-esima).
- **P4** Le rifiniture dei round 2-3 si elencano, se possibile, nella pre-registrazione del round 1; quelle non
  elencate sono post-esito.
- **P5** Ogni deviazione dalla pre-registrazione va in una tabella con la giustificazione; una deviazione grande rende
  esplorativo l'intero test.
- **P6 Costo di un cambio** (Matteo, 21/11; DECISIONS 2026-11-21 (7)). Le scelte di **misura e di disegno** sono prese
  insieme da Matteo e Claude e sono rivedibili; il costo dipende da cosa si e' visto.
  (1) Prima del commit di congelamento, e se nessun dato o risultato gia' visto (elencato fra i "dati gia' visti")
  riguarda la scelta: **gratis**, con una voce in DECISIONS.
  (2) Dopo il commit, o dopo dati che non contengono perdite ne' differenziali (conteggi del controllo di struttura,
  testo delle fonti): **deviazione** nella tabella P5, con il motivo e la risposta scritta al test del §4 ("l'avrei
  fatta con qualunque esito?"). 0 trial se la risposta e' si'; non rende esplorativo il test.
  (3) Dopo perdite o differenziali sui dati reali, comprese le dispersioni e le simulazioni calibrate sui dati reali
  (G9): ammessi solo i cambi **elencati prima** come condizionati a quell'uscita; ogni altro cambio e' una **variante
  contata** (C1, C3) ed **esplorativa** (P1-P3): niente verdetto, niente holdout.
  (4) Dopo l'apertura dell'holdout: nessuna scelta (H5).
  **Regole di protezione** (holdout, sigilli, dati futuri, decorrenze, budget) e **verdetti** non sono scelte: cambiano
  solo con il §7 o con una decisione di metodo di Matteo che dichiari cosa ha visto.

**Sottofamiglie**
- **S1** La pre-registrazione di famiglia le elenca tutte. La teoria senza previsioni testate (per la volatilita':
  Black-Scholes, Heston, SABR) resta fuori dal contatore.
- **S2** Errore di famiglia fissato e diviso prima di ogni test, lungo un grafo con riciclo dopo un rifiuto. Volatilita':
  **5% a una coda = 2,5% GARCH + 1,25% HMM + 1,25% premio di volatilita'**, riciclo in parti uguali (Matteo, 11/11).
- **S3** Ogni sottofamiglia e' un'ipotesi sola ("almeno una variante batte il benchmark"), con lo SPA alla sua quota.
- **S4** I benchmark si fissano prima e non dipendono dagli esiti delle altre sottofamiglie. Volatilita': GARCH contro
  EWMA; HMM contro GJR o HAR dichiarato, sul contenuto **in piu'** della probabilita' **filtrata**; premio di
  volatilita': varianza realizzata sui 30 giorni di calendario successivi contro VIX², Newey-West con 21-30 ritardi o
  dati mensili non sovrapposti.
- **S5** HMM: solo probabilita' filtrate, parametri ristimati su finestra mobile, vincolo σ_basso < σ_alto, piu'
  partenze casuali.
- **S6** Una sottofamiglia proposta dopo aver visto i risultati di un'altra e' selezionata dai dati: si conta, e il
  suo test usa dati non visti.

**Cosa puo' dire il pacchetto ai soci.** "Previsione piu' accurata e calibrata" si'; "piu' profitto" no: la gestione
per volatilita' migliora code e drawdown ma lo Sharpe solo per azioni e credito (Harvey et al. 2018), e fuori campione
peggiora in 72 strategie su 103 (Cederburg et al. 2020). Il passaggio da strumento a strategia lo testano i soci.

---

## 9. Collegamenti

- [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md) — come si misura (il *gate*, non la *regola di stop*).
- [`.claude/agents/quant-gatekeeper.md`](../../.claude/agents/quant-gatekeeper.md) — il revisore: fa rispettare questo ciclo ai gate G1 e G2 (dal 2026-10-13 è l'unico).
- [04_quant_metodologia](../../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md) — teoria dei bias, DSR/PBO, pre-mortem.
- [DECISIONS.md](../../decisioni/DECISIONS.md) — il registro dei verdetti effettivi.
- Pre-registrazioni esistenti: `TSMOM_`, `OPENING_RANGE_`, `MEANREV_`, `SEASONALITY_`, `LEVEL_RESEARCH_PREREGISTRATION.md`.
