# Ciclo di vita di una strategia — loop di ricerca, gate e criteri di bocciatura

> **Il problema che questo documento risolve.** Un loop di miglioramento è la cosa giusta da fare in
> ingegneria: provi, misuri, correggi, riprovi. Ma su un **dataset storico fisso** lo stesso loop è
> una **macchina per generare falsi positivi**: ogni iterazione è un tentativo in più, e se scegli la
> variante migliore fra molte stai selezionando rumore. Il loop è utile solo se accompagnato da
> **contabilità dei tentativi**, **dati sigillati** e **criteri di morte dichiarati in anticipo**.
> Senza questi tre, "ricerca → backtest → rifinitura → ricerca" è p-hacking con più passaggi.

Riferimenti teorici: [04_quant_metodologia §2](../fondamenti_tecnici/04_quant_metodologia/principles.md)
(overfitting/data snooping, DSR, PBO), [§9](../fondamenti_tecnici/04_quant_metodologia/principles.md)
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

**Due differenze rispetto al loop intuitivo:**

1. **[G1] La pre-registrazione è un gate, non un passaggio.** Sta *fra* formulazione e backtest, e
   fissa **prima di guardare i dati**: ipotesi, metriche, soglie di verdetto, **budget di tentativi**
   e criteri di bocciatura. Se non è scritta prima, il test non è informativo — è una descrizione dei
   dati. Modello: i cinque `docs/*_PREREGISTRATION.md` già in repo.
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

| Azione | Conta come trial? |
|---|---|
| Correzione di un **bug**: il codice non implementava la regola pre-registrata | **No** — è la prima esecuzione valida del trial originale. Va documentata |
| Modellazione **più realistica** di costi/slippage/esecuzione | **No** — può solo peggiorare il risultato, non è ricerca di conferma |
| Cambio di **parametro** dopo aver visto l'esito | **Sì**, uno per variante |
| Cambio di **asset o timeframe** dopo aver visto l'esito | **Sì**, uno per combinazione |
| Aggiunta di un **filtro** | **Sì** — ed è il più pericoloso (vedi §4) |
| **Nuova ipotesi** con razionale economico indipendente | **Sì**, ma apre una **nuova pre-registrazione** |

> **Regola di futilità (stop matematico).** Dato il numero cumulato di trial, esiste uno Sharpe
> minimo sotto il quale il DSR non può essere significativo. Se il **migliore** risultato osservato
> su tutte le varianti è sotto quella soglia, continuare a iterare è **matematicamente inutile**:
> serviresti un effetto più grande di qualunque cosa tu abbia mai visto. → **kill immediato**.

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

## 5. Tassonomia dei verdetti

| Verdetto | Significato | Cosa succede |
|---|---|---|
| **GO** | Edge sopravvive a train + walk-forward + holdout + costi | Promozione a capitale, con pre-mortem ([04 §9](../fondamenti_tecnici/04_quant_metodologia/principles.md)) |
| **LEAD** | Risultato positivo ma **data-derived** o senza OOS indipendente | **Non promuovibile.** Richiede **nuova** pre-registrazione + **forward OOS**. Stato attuale del *fade* NXT |
| **NO-GO** | Questa specifica non regge | La *specifica* muore. La *famiglia* sopravvive solo se ha budget residuo |
| **CLOSED** | L'intera direzione di ricerca è morta | Vedi §7 — non si riapre con un ritocco |
| **INSUFFICIENT DATA** | `n_trades < 50` | **Non è un verdetto.** Si continua a raccogliere **solo se la soglia era pre-dichiarata** |

---

## 6. Criteri di bocciatura

### 6a. Kill duri — nessun ramo di rifinitura disponibile

Questi non si aggiustano con un parametro. Quando scattano, la strategia (o la famiglia) muore.

1. **Difetto metodologico conclamato** — look-ahead, survivorship, finestre sovrapposte, dati
   contaminati. I risultati sono **nulli**, non "da correggere": vanno rifatti da zero e il vecchio
   numero non si cita più. *Precedente: London Breakout, edge da regime gating look-ahead.*
2. **Non batte il baseline random** matched (stessa geometria, stessi tempi, distance-matched).
   *Precedente: ricerca livelli, 384 trial, NULL su ogni timeframe.*
3. **Fallimento di breadth** — negativa sulla maggioranza degli asset **e** dei periodi testati.
   Nessun set di parametri ripara una cosa che non c'è. *Precedente: NXT, 14/14 anni e 6/6 asset
   negativi.*
4. **Muore sui costi realistici** — l'edge esiste lordo e sparisce con spread/slippage/commissioni.
5. **Instabilità parametrica** — piccole variazioni ribaltano l'esito. Già NO-GO in
   [04](../fondamenti_tecnici/04_quant_metodologia/principles.md).
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

Qualunque altra riapertura è il bias di conferma che si ripresenta col cappello. *Precedente
vincolante: la ricerca livelli è CHIUSA — non riproporre "testiamo i livelli".*

---

## 8. Cosa entra nel loop dall'esterno

Le fonti esterne (canali, video, materiale di terzi) entrano da
[`fondamenti_tecnici/_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md) e alimentano la fase **RICERCA**,
mai le fasi successive. Due vincoli:

- **Si raccolgono le regole, si scartano le statistiche dichiarate.** Un "90% win rate" non deve
  entrare nel prior. Storico del repo: 60-70% dichiarato → 13,3% misurato (NXT); 80-90% → ~53%
  (VELTRIX); 90% → ~20% (playbook Chart Fanatics, test di terzi).
- **Budget di ipotesi esterne dichiarato**: max **2-3 pre-registrazioni per trimestre** da fonti
  esterne. Un funnel aperto non produce più edge — produce più penalità DSR su quelli veri.

---

## 8bis. Dopo il capitale — ritiro, incubazione, riattivazione

> **Buco colmato il 2026-08-17.** Fino a qui il documento copre **nascita e morte prima del
> capitale**: il loop finisce al verdetto. Non diceva nulla su *cosa succede a una strategia già
> operativa che peggiora*. Serve adesso, non domani: il fade è in forward e il copier mentore va in
> live. Innesco esterno: fonte *Noel T.* ([`_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md)), che
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

**Cosa NON si fa.** Non si ritara la strategia durante l'incubazione — sarebbe rifinitura su dati
che includono il periodo negativo, cioè il p-hacking del §4 con il capitale già in gioco. Se serve
una modifica, è una **nuova specifica** e riparte dal gate [G1].

---

## 9. Collegamenti

- [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md) — come si misura (il *gate*, non la *regola di stop*).
- [`agents/quant_reviewer.md`](../agents/quant_reviewer.md) — il reviewer avversariale.
- [04_quant_metodologia](../fondamenti_tecnici/04_quant_metodologia/principles.md) — teoria dei bias, DSR/PBO, pre-mortem.
- [DECISIONS.md](../DECISIONS.md) — il registro dei verdetti effettivi.
- Pre-registrazioni esistenti: `TSMOM_`, `OPENING_RANGE_`, `MEANREV_`, `SEASONALITY_`, `LEVEL_RESEARCH_PREREGISTRATION.md`.
