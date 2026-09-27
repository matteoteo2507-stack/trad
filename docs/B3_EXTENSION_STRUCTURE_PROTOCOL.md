# B3 — Condizione di struttura sull'estensione estrema: protocollo

> **Scritto PRIMA di misurare** (2026-09-21). Soglie, celle, direzione attesa e significato di un
> mancato rifiuto sono fissati qui e non si toccano dopo aver visto i numeri.
>
> **Costo dichiarato: 0 trial.** È una **misura descrittiva con una predizione pre-dichiarata**,
> non la ricerca di una regola: nessun parametro viene scelto guardando l'esito, nessuna cella
> viene promossa. ⚠️ Se una cella venisse poi trasformata in regola operativa, **quello sarebbe un
> trial** e aprirebbe una pre-registrazione nuova.

---

## 1. La convergenza da testare — e cosa NON è

Cinque fonti del funnel dicono *"l'estensione estrema si inverte"*. Non è quello l'oggetto: è
banale e non falsificabile come formulato. L'oggetto è **quale** estensione, e su questo due fonti
**indipendenti**, su mercati e stili diversi, si sono specificate a vicenda senza essersi parlate:

| condizione | Marius (C3.4, US Investing Championships +291%) | Kyle (C3.5, 7 M$ verificati) |
|---|---|---|
| estensione minima | 200 / 100 / 50% secondo market cap | 80-100% |
| durata | 2-4 candele, **mai il primo giorno** | **almeno 2 giorni verdi**, mai uno solo |
| **forma** | solo candele **enormi con ATR ampio**; scarta le *"formiche"* (tante candeline) | le candele devono **espandersi** salendo; se si contraggono è negativo |
| **volume** | **il più alto dell'anno** sul climax | **in espansione**; se cala, non opera |

Razionale economico identico nelle due: **affollamento completo** — volume enorme sul climax
significa che non resta nessuno da comprare. Non richiede market cap né order flow: richiede
**range delle candele** e **volume**, che abbiamo.

⚠️ Vincolo non negoziabile già scritto in sede di distillazione: le soglie assolute (200%, 100%,
80%) **non sono trasferibili** e vanno normalizzate sulla **volatilità** dello strumento. È la
lezione del KILL delle escursioni del 14/08 — una soglia assoluta senza riferimento non è una
soglia.

## 2. Il dato: metà della tesi poggia su una colonna che va verificata prima

La gamba **volume** richiede che la colonna `volume` sia volume. Sul feed Dukascopy D1 è
**tick volume** per l'FX e qualcosa di diverso per i CFD su materie prime, con scale
incomparabili (mediana 180.655 su EURUSD, **0,1** su COCOA, **1,1** su BTCUSD). Le scale in sé non
sono un problema — la misura è un **rapporto interno allo strumento**. Lo è invece il fatto che su
alcuni strumenti la serie non si comporta come un volume.

**Gate di usabilità del volume, dichiarato prima e applicato a ciascuno strumento:**

1. barre a volume **zero** < 5%;
2. `corr(volume, |rendimento log|)` **≥ 0,15** — un volume vero è sempre correlato positivamente
   con quanto il prezzo si muove; se non lo è, quella colonna non misura attività;
3. **mediana ≥ 10** — sotto, la serie è quantizzata su pochi livelli e un "volume in espansione"
   misura arrotondamento.

Strumenti che non passano: la gamba **volume** non viene misurata lì, e lo si dichiara. La gamba
**forma/range** resta misurabile su tutti.

## 3. Definizione dell'evento — tutto normalizzato, niente soglie assolute

Per ogni strumento e ogni barra `t`:

- **corsa (streak)**: la sequenza massimale di chiusure nella stessa direzione che finisce in `t`,
  di lunghezza `L`. Si richiede **`2 ≤ L ≤ 5`** — *mai il primo giorno*, entrambe le fonti, e non
  più di 5 per escludere l'accumulazione ordinata (*"10 giorni verdi con +30% non vale"*).
- **estensione**: `E = |C[t] − C[t−L]| / ATR20[t−L−1]`.
  L'ATR è preso **prima che la corsa inizi**: nessun look-ahead, e il denominatore non è gonfiato
  dalla corsa stessa. **Soglia primaria `E ≥ 3,0`**; robustezza a 2,0 e 4,0 **riportata ma non
  decisionale**.
- **forma**: `F = media(H−L sulle barre della corsa) / media(H−L sulle 10 barre precedenti)`.
  **Espansione** se `F ≥ 1,2`; **contrazione** se `F ≤ 1,0`.
- **volume**: `V = media(volume sulla corsa) / media(volume sulle 10 barre precedenti)`.
  **Espansione** se `V ≥ 1,2`; **contrazione** se `V ≤ 1,0`.

## 4. Cosa si misura

Il segnale è noto alla **chiusura di `t`** → la prima barra azionabile è `t+1`
([Step 3bis](QUANT_REVIEW_PROTOCOL.md)). Quindi:

- ingresso all'**apertura di `t+1`**, uscita all'**apertura di `t+1+h`**, con
  **`h ∈ {1, 2, 3, 5}`** dichiarati prima (le fonti danno una finestra di invalidazione di 2
  giorni / massimo 3 tentativi);
- rendimento espresso in unità di **ATR20 pre-corsa**, con **segno orientato alla corsa**:
  **positivo = continuazione**, **negativo = inversione**. È la direzione che le fonti predicono;
- **baseline random risk-matched** con [`core/random_baseline.py`](../core/random_baseline.py):
  stesso strumento, stesso anno, **stessa direzione**, **stesso orizzonte** — solo l'istante è
  casuale, `m = 3` controlli per evento. La durata è identica per costruzione, quindi il confonditore
  trovato su A1 il 21/09 **non si presenta qui**;
- metrica primaria = **differenza appaiata reale − media dei suoi controlli**, CI BCa a **cluster
  sull'evento**.

## 5. Le celle, e la predizione — questa è la parte falsificabile

Quattro celle, incrociando forma e volume, su eventi che hanno già superato `E ≥ 3,0`:

| | volume in espansione | volume in contrazione |
|---|---|---|
| **range in espansione** | **cella attesa: la più negativa** | intermedia |
| **range in contrazione** | intermedia | *"formiche"*: attesa neutra |

**H1** — nella cella (range espande **e** volume espande) la differenza contro random è
**negativa** (inversione) e il CI 95% **esclude lo zero**.

**H2** — quella cella è **più negativa delle altre tre**. È qui che sta il contenuto della
convergenza: le fonti non dicono *"l'estensione si inverte"*, dicono *"si inverte **questa**"*.
Se tutte e quattro le celle si comportano uguale, la condizione di struttura non porta
informazione, **anche se** l'estensione in sé dovesse invertire.

## 6. Cosa significherà un mancato rifiuto — dichiarato prima

Se nessuna cella si distingue dal random:

- **non** significa che le fonti sbagliano sul loro universo. Significa che la condizione **non è
  trasferibile** dall'azionario USA small/mid cap al nostro universo di CFD e FX, dove mancano i
  meccanismi che le due fonti citano (float ristretto, short squeeze, halt, locate);
- **non** è un kill di una famiglia: B3 non è una famiglia, è una casella descrittiva. Si chiude
  la casella e si scrive cosa servirebbe per riaprirla;
- si riporta l'**MDE**: l'effetto minimo che questo campione poteva rilevare. Un'assenza senza MDE
  non è un risultato ([audit A5](EARLY_STAGE_AUDIT_REPORT.md)).

## 7. Difese contro gli errori già commessi qui

| rischio | difesa |
|---|---|
| soglia assoluta che passa per costruzione (14/08) | tutto normalizzato su ATR, e **baseline random** obbligatorio |
| fill non ottenibile (Step 3bis) | ingresso all'apertura di `t+1`, mai alla chiusura di `t` |
| durata non appaiata (A1, 21/09) | orizzonti **fissi e identici** nei due bracci |
| CI finto su controlli non indipendenti | bootstrap **a cluster sull'evento** (`gap_ci`) |
| eleggere un vincitore dalla mappa (B1) | la cella attesa è **dichiarata qui sopra**, prima di guardare |
| molteplicità | 4 celle × 4 orizzonti = 16 combinazioni: la **primaria è una sola** (cella attesa, `h = 2`), le altre sono descrittive e vanno lette come tali |
| dato non verificato (18/09) | `core/data_checks.py` eseguito **prima**, gate volume del §2 |

## 8. Risultati — eseguito il 2026-09-21

Motore: [`analysis/extension/structure.py`](../analysis/extension/structure.py).
Finestra **2017-12-26 →**, 27 strumenti, **1.733 eventi** a `E ≥ 3,0 ATR`, 5.199 controlli.
Matching verificato: strumento, direzione e anno coincidono su **tutte** le coppie.

### 8.1 Il gate volume esclude proprio gli strumenti che servivano

**17 strumenti su 27 passano.** Non passano — e la gamba volume non viene misurata lì:

| strumento | perché |
|---|---|
| COCOA, COTTON, SUGAR, SOYBEAN | correlazione fra volume e rendimento assoluto: da **−0,03 a −0,00** |
| BTCUSD, ETHUSD | corr **0,02** e **0,05** |
| NATGAS | **20,6%** di barre a volume zero, corr 0,03 |
| BRENT, COPPER, UKGILT | corr 0,06–0,14 |

Su quelle serie il volume **non ha alcuna relazione con quanto il prezzo si muove**: è il
controllo minimo che un volume vero supera sempre. I gruppi coinvolti sono **agri, bond, crypto,
energy, metal** — cioè l'estremo ad alta volatilità, dove il fenomeno delle due fonti dovrebbe
manifestarsi. La gamba volume resta testabile solo su un sottoinsieme **dominato dall'FX**.

### 8.2 L'estensione estrema, da sola, non fa niente

Differenza appaiata *reale − random*, positivo = **continuazione**:

| orizzonte | n | reale | random | **differenza** | BCa95 | MDE |
|---|---|---|---|---|---|---|
| h=1 | 1.733 | −0,020 | +0,005 | −0,024 | [−0,074; +0,031] | 0,076 |
| **h=2 (primario)** | 1.733 | +0,034 | +0,023 | **+0,011** | [−0,061; +0,090] | **0,106** |
| h=3 | 1.733 | +0,053 | +0,047 | +0,005 | [−0,083; +0,106] | 0,135 |
| h=5 | 1.733 | +0,017 | +0,085 | −0,068 | [−0,180; +0,055] | 0,167 |

Nessun orizzonte si distingue dal random. Con **MDE 0,106R** all'orizzonte primario, un effetto
più grande di ~0,11R sarebbe stato visto: non c'è.

### 8.3 Il risultato vero: **le celle non esistono**, e non per mancanza di campione

| L (lunghezza corsa) | n | range **+** | range **−** | in mezzo |
|---|---|---|---|---|
| 2 | 236 | **97,0%** | 1,3% | 1,7% |
| 3 | 450 | **93,6%** | 1,3% | 5,1% |
| 4 | 534 | 80,9% | 5,2% | 13,9% |
| 5 | 513 | 59,5% | 9,9% | 30,6% |

Correlazione di rango fra estensione `E` e forma `F`: **+0,410**.

**È aritmetica, non un caso.** Un'estensione di 3 ATR in 2 barre richiede che ogni barra si muova
≥1,5 ATR; il range di una barra è almeno quanto il suo movimento, quindi `F ≥ ~1,5` **per
costruzione**. Una volta normalizzata la soglia sulla volatilità, *"estensione estrema"* e
*"candele grandi"* diventano **la stessa cosa**.

> La distinzione delle due fonti — *"non conta quanto è salito, conta se è salito in poche grandi
> candele"* — vive di soglie in **percentuale** applicate a strumenti con volatilità molto
> diversa. Lì un +200% può arrivare in venti candeline. Con una soglia normalizzata sull'ATR
> quel caso **sparisce**: le *"formiche"* sono l'1,3% degli eventi a L=2-3.
>
> Non è che non riusciamo a misurare la distinzione. È che **su un universo a volatilità
> normalizzata la distinzione non è una distinzione.**

### 8.4 La gamba volume, dove misurabile, non separa niente

| cella | n | differenza | BCa95 | MDE |
|---|---|---|---|---|
| **range+ / vol+** (la cella attesa) | 517 | **+0,007** | [−0,145; +0,168] | 0,221 |
| range+ / vol− | 126 | +0,011 | [−0,218; +0,224] | 0,323 |
| range− / vol+ | 3 | — | campione insufficiente | |
| range− / vol− | 27 | — | campione insufficiente | |

Le due celle misurabili danno **lo stesso numero**. Robustezza sulla soglia (riportata, non
decisionale): `E ≥ 2,0` → +0,041 [−0,053; +0,135]; `E ≥ 4,0` → +0,001 [−0,261; +0,268]. Monotona
verso lo zero al crescere della soglia, cioè il contrario di quanto prevede l'ipotesi.

### 8.5 Breadth: moneta, e il segno più forte è quello sbagliato

| gruppo | n | differenza |
|---|---|---|
| energy | 189 | −0,116 |
| fx_major | 384 | −0,050 |
| fx_cross | 180 | −0,036 |
| agri | 331 | −0,030 |
| metal | 186 | +0,035 |
| index | 133 | +0,065 |
| bond | 127 | +0,091 |
| **crypto** | 203 | **+0,248** |

**4 gruppi su 8** vanno nella direzione attesa (inversione). E il valore più grande in assoluto è
**crypto a +0,248**, cioè **continuazione** — il contrario della predizione, sullo strumento dove
il fenomeno dovrebbe essere più forte. Coerente con quanto già misurato in B1 il 17/09 (crypto
**continua**, non ritorna alla media), che è una terza strada indipendente sullo stesso segno.

### 8.6 Esito secondo §5, scritta prima

| | esito |
|---|---|
| **H1** la cella attesa è negativa col CI che esclude lo zero | **NO** — +0,007 [−0,145; +0,168] |
| **H2** la cella attesa è la più negativa delle quattro | **NON VALUTABILE** — solo 2 celle su 4 hanno campione, e non per caso (§8.3) |

**B3 si chiude. 0 trial spesi.**

Come impone §6, la formulazione precisa: le fonti **non sono state falsificate sul loro
universo**. Marius e Kyle operano small/mid cap USA con float ristretto, short squeeze, halt e
locate — meccanismi che sul nostro universo di CFD e FX **non esistono**. Quello che questo test
mostra è che la loro condizione **non è trasferibile**, e per una ragione strutturale e non
statistica: normalizzata sulla volatilità, la distinzione fra le forme **svanisce**.

### 8.7 Cosa servirebbe per riaprire la casella

- un universo dove **volatilità e dimensione della candela si separano davvero** — cioè azionario
  con normalizzazione su market cap, come fanno le fonti (è il [bucket D2](BACKLOG_RICERCA.md),
  bloccato per dati);
- **volume vero** (azioni o controvalore), non tick volume di CFD: il gate del §8.1 esclude oggi
  proprio i gruppi ad alta volatilità;
- ⚠️ **non** è condizione di riapertura inseguire il `+0,248` della crypto: è di segno opposto
  all'ipotesi, non è stato pre-registrato, ed è un solo gruppo su otto visto **dopo** la tabella.
