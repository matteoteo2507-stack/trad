# A1 / playground — diagnostico di DURATA

> **Protocollo scritto PRIMA di eseguire il diagnostico** (2026-09-21). Le soglie e i tre
> esiti possibili qui sotto non si toccano dopo aver visto i numeri.
>
> **Costo: 0 trial.** Non cambia regole, parametri, asset o filtri: verifica l'**integrità di
> un confronto già fatto**, che `STRATEGY_LIFECYCLE.md §3` classifica come modellazione più
> realistica dell'esecuzione. Stessa natura di `analysis/nxt/entry_fill_audit.py`.
> ⚠️ Se uno degli esiti portasse a **cambiare** la regola, quello sì costerebbe un trial —
> e sarebbe l'ultimo del ramo trend (round 2 di 3 già speso).

---

## 1. Da dove nasce

Il 2026-09-19, accendendo `check_matching` di [`core/random_baseline.py`](../core/random_baseline.py)
sul motore del playground, è emerso che il braccio reale e il braccio random **non stanno in
mercato per lo stesso tempo**: holding mediano **7 giorni contro 2** (−71%). Tutti gli altri assi
(asset, lato, anno, numerosità) risultano matchati.

Non è un difetto del baseline: con le stesse regole d'uscita la durata è un **esito**, non un
input. Ma significa che il confronto *reale vs random* è **in parte un confronto fra durate**, e
il controllo C1 di [`analysis/trend/q2_checks.py`](../analysis/trend/q2_checks.py) — quello che
doveva neutralizzare il canale meccanico — è costruito proprio su quella differenza.

## 2. Perché la durata può produrre il gradiente da sola

`E[R]` è misurato in unità di **ATR(20) all'ingresso**. Per un trade tenuto `h` barre:

```
E[R] ≈ h · (deriva per barra / ATR_ingresso)   +   (asimmetria dell'uscita)
```

Due canali, entrambi senza alcun edge della regola:

1. **Deriva × tempo.** Il braccio random eredita il **lato** dal trade reale. Su un asset con
   deriva positiva e breakout prevalentemente long, anche un'entrata casuale guadagna — e
   guadagna **in proporzione al tempo in cui resta dentro**. Gruppi tenuti più a lungo hanno
   `E[R]` più alto senza che la regola d'ingresso c'entri.
2. **Normalizzazione.** Se la volatilità realizzata durante l'holding supera l'ATR d'ingresso
   in modo sistematico più sugli asset volatili, ogni multiplo di R si gonfia lì di più.

Il sospetto è già corroborato **prima** di questo diagnostico: `q2_checks.py` mostra
**Spearman(vol, E[R] del braccio RANDOM) = +0,619 (p=0,062)**. Il gradiente esiste in parte
anche dove non c'è nessuna regola.

## 3. Cosa misuro — quattro passaggi

| | misura | serve a |
|---|---|---|
| **D0** | riprodurre il primario: `rho(vol, E[R] reale)` sugli 8 gruppi | se non riproduce +0,857 il codice nuovo è sbagliato, non il vecchio |
| **D1** | holding per gruppo, reale e random; `rho(vol, holding)` e `rho(holding, E[R])` | la durata è un candidato **almeno altrettanto buono** della volatilità? |
| **D2** | correlazione parziale fra `vol` e `E[R]` al netto di `holding` | il gradiente sopravvive al controllo, o è durata? |
| **D3** | **decisivo**: baseline random **a durata appaiata** — ogni controllo esce dopo **le stesse barre** del suo trade reale, stesso asset, lato, anno, rischio | è la stessa domanda del claim, ma con il tempo in mercato tolto di mezzo |

**D3 in dettaglio.** Per ogni trade reale `i` con holding `h_i`, i suoi `m = 3` controlli random
escono a `h_i` barre invece che sul proprio incrocio di SMA. Entrambi i bracci usano **la stessa
funzione di uscita**, perché la lezione di `excursion.py` (27/08) è che due simulatori diversi
mettono la loro differenza dentro il risultato. Il braccio reale viene ricalcolato con quella
funzione e **deve riprodurre `E1`**: se non lo fa, il diagnostico è rotto e si ferma lì.

## 4. La potenza, dichiarata prima

`n = 8` gruppi. Con Spearman a permutazione serve **|rho| ≈ 0,74** per p < 0,05. Ne segue una
regola di lettura che vale per tutti e tre gli esiti:

> Un `rho` che scende sotto 0,74 **non dimostra** che il gradiente non esiste. Dimostra che
> **questo test non lo vede**. Per chiudere A1 non basta l'assenza di prova nel braccio
> controllato: serve la **presenza** di una spiegazione meccanica nel braccio random.

È la lezione dell'audit A5: *"non dimostrato" non diventa "refutato"*.

## 5. I tre esiti, scritti prima

| esito | condizione numerica | cosa succede |
|---|---|---|
| **A1 CHIUSA** | `rho(vol, differenza a durata appaiata)` **non** significativo (< 0,74 o p ≥ 0,05) **E** `rho(vol, E[R] random a durata appaiata)` significativo (≥ 0,74, p < 0,05) | il gradiente è **nel mercato**, non nella regola. Non è una rifinitura: la spiegazione alternativa è meccanica e affermativa → famiglia chiusa, **senza spendere il terzo round** |
| **A1 SOPRAVVIVE** | `rho(vol, differenza a durata appaiata)` ≥ 0,74 con p < 0,05 | il gradiente resta dopo aver tolto il tempo in mercato → si passa al **punto 2** (quanti strumenti servono per l'MDE, e Dukascopy ce li ha?) |
| **NON CONCLUSIVO** | tutto il resto — in particolare se **entrambi** i rho scendono sotto soglia | si dichiara così, con l'MDE accanto. Non è un kill e non è una promozione: è un test senza potenza, e la decisione torna all'utente |

**Controllo di onestà obbligatorio**: quanti controlli random vengono **persi** perché mancano
barre per arrivare a `h_i`. Scartarli è un filtro sull'esito, non prudenza: se superano il 5% va
riportato accanto al risultato e il confronto va rifatto sui soli trade reali i cui controlli
sopravvivono tutti.

---

## 6. Risultati — eseguito il 2026-09-21

Motore: [`analysis/trend/duration_diagnostic.py`](../analysis/trend/duration_diagnostic.py).
Finestra W2 comune **2017-12-26 →**, **1.169** trade reali, **3.507** controlli, 8 gruppi.

### 6.0 Le verifiche preliminari passano

| controllo | esito |
|---|---|
| **D0** il primario riproduce | `rho(vol, E[R] reale) = +0,857  p=0,0060` — **identico** al pubblicato |
| **D0a** la funzione d'uscita comune riproduce `E1` | **99,8%** delle coppie. I 2 diversi (SPX500, SUGAR) sono trade **terminati a fine serie**, dove `simulate` esce alla chiusura e la funzione comune all'apertura. Effetto aggregato **−0,0016R** |
| controlli senza barre per arrivare a `h` | **0,43%** (soglia dichiarata 5%). Non vengono scartati: escono all'ultima chiusura disponibile |
| matching a durata appaiata | asset, lato, anno **e durata** coincidono su tutte le coppie: `scarto relativo max 0.00e+00` |

### 6.1 D1 — la durata spiega l'ordinamento **meglio** della volatilità

| gruppo | vol | holding reale | holding random | E[R] reale |
|---|---|---|---|---|
| fx_cross | 8,1% | 7,5 | 4,3 | −0,524 |
| bond | 8,2% | 8,6 | 5,3 | +0,166 |
| fx_major | 8,3% | 7,0 | 4,7 | −0,397 |
| index | 21,0% | 8,4 | 5,8 | −0,120 |
| metal | 25,5% | 9,4 | 4,8 | +0,464 |
| agri | 28,9% | 8,8 | 4,4 | +0,242 |
| energy | 51,2% | 9,1 | 5,0 | +0,396 |
| crypto | 63,5% | 9,8 | 4,7 | +1,099 |

| correlazione | rho | p |
|---|---|---|
| `vol → E[R] reale` (il primario) | **+0,857** | 0,0060 |
| `vol → holding` | **+0,810** | 0,0106 |
| **`holding → E[R] reale`** | **+0,976** | **0,0001** |
| `vol → E[R]` **al netto di** `holding` (parziale) | **+0,525** | 0,1164 — **non rilevato** |

**Sul solo braccio reale, la durata è un predittore migliore della volatilità** (+0,976 contro
+0,857), e al netto della durata la volatilità non aggiunge niente di rilevabile. ⚠️ Ma le due
sono a loro volta collineari (`vol → holding` = +0,810): **con n = 8 non sono separabili**, e la
parziale non-rilevata è anche un problema di potenza. Questa riga da sola non decide nulla — per
questo il protocollo aveva dichiarato D3 come test decisivo.

### 6.2 D3 / D3b — il gradiente sopravvive, il canale meccanico sparisce

Due controlli indipendenti sulla durata, e **concordano**:

| | durata **appaiata** (= quella del reale) | durata **fissa** (E3, 20 giorni) |
|---|---|---|
| `rho(vol, differenza)` | **+0,929** p=0,0009 | **+0,881** p=0,0041 |
| `rho(vol, E[R] del random)` | **+0,048** p=0,46 | +0,429 p=0,15 |

Prima del controllo, il braccio random mostrava da solo un gradiente di **+0,619** (p=0,062):
era la spiegazione meccanica da battere. **A durata controllata scende a +0,048.** Il gradiente
non è la normalizzazione in unità di ATR, e non è il tempo in mercato.

> **Esito secondo §5, scritta prima: A1 SOPRAVVIVE.** Il diagnostico non chiude la famiglia.

### 6.3 Ma il livello si ribalta: a parità di tempo in mercato, la regola **perde** dal random

È il risultato più importante, e non era la domanda che il diagnostico si poneva.

| confronto | reale | random | divario | BCa95 |
|---|---|---|---|---|
| **come oggi** (durata non appaiata) | +0,037 | +0,118 | **−0,081** | [−0,215 ; **+0,071**] — contiene lo zero |
| **durata appaiata** | +0,037 | +0,275 | **−0,238** | [−0,363 ; −0,098] |
| **durata fissa 20g** | +0,135 | +0,587 | **−0,451** | [−0,661 ; −0,219] |

Differenza per gruppo a **durata fissa**: positiva **solo su crypto** (+1,001). Negativa su tutti
gli altri sette, fino a **−1,012** su fx_major.

**Cosa vuol dire.** Il braccio random eredita il **lato** dal trade reale ed entra in un istante
casuale dello stesso anno. A parità di durata, quell'entrata casuale **batte il breakout
Donchian** — in aggregato e in 7 gruppi su 8. Il vantaggio che la regola sembrava avere era
**tempo in mercato**, non scelta del momento: il trail teneva aperte le posizioni più a lungo del
controllo, e in un mercato con deriva il tempo paga. Tolto quello, dell'entrata resta un costo.

⚠️ Questo **non** è "assenza di prova": i CI escludono lo zero da entrambi i lati del controllo.
È una misura positiva con segno sfavorevole.

### 6.4 I limiti di questo diagnostico, dichiarati

1. **La durata appaiata condiziona su un esito.** `rho(holding, E1)` sui singoli trade = **+0,836**:
   i trade che vanno bene restano aperti più a lungo, quindi il controllo appaiato riceve un
   orizzonte più lungo **proprio quando il reale ha funzionato**, e su un asset con deriva questo
   lo aiuta. È il motivo per cui D3 non va letto da solo. **D3b usa una durata decisa prima e
   uguale per tutti, non è esposta a questa obiezione, e dà lo stesso segno** — anzi più forte.
2. **n = 8 resta n = 8.** Tutte le correlazioni qui sopra hanno |rho| sopra la soglia di potenza
   (0,74), ma il campione di gruppi non è cambiato: restano 8 punti, con partenze scaglionate
   (bond dal 2016-17) e **nessun holdout sigillato**.
3. **Il lato è ereditato**, quindi il confronto misura *quando* entrare, non *se* essere long o
   short. Il controllo C2 di `q2_checks.py` resta valido: solo **3/8** gruppi sono positivi su
   entrambi i lati.

### 6.5 Conseguenza per il punto 3 (la decisione dell'utente)

Il diagnostico non ferma A1 — ma **cambia che cosa A1 afferma**. Non più *"più volatile = più
edge"*, bensì *"più volatile = l'entrata Donchian danneggia meno"*, con un solo gruppo sopra lo
zero a durata fissa. Una pre-registrazione a due gruppi su strumenti held-out dovrebbe quindi:

- misurare la **differenza contro random a durata controllata**, non `E[R]` grezzo (è il grezzo
  che conteneva il canale meccanico);
- dichiarare come ipotesi il **segno atteso di un divario negativo che si attenua**, non di un
  edge positivo, perché è quello che i dati attuali descrivono;
- o, in alternativa, cambiare oggetto e chiedersi se l'unica casella positiva (**crypto**) regga
  da sola — sapendo che sceglierla dopo aver visto questa tabella **è eleggere un vincitore dalla
  mappa**, e costerebbe il terzo e ultimo round del ramo trend.
