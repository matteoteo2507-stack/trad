# Passata mirata — la "gamba di copertura" (7 video del gruppo 2)

> **Scopo unico**: **qualificare o chiudere** l'unico claim aperto del canale che ci riguarda, parcheggiato **tre volte**
> senza mai essere deciso (E2 `#47`, G6 `#38`, `#29`) e oggi registrato in `08_asset_allocation_passiva` con la nota
> *"speculativo/promozionale, da verificare"*.
>
> **Non** è l'apertura del gruppo 2. Il gruppo 2 (~45 video su calcolo stocastico e derivati) resta **non distillato**
> per decisione dell'utente del 2026-09-15; qui si leggono **7 video scelti perché toccano il claim**, non perché
> completano il dominio.

## Il claim, enunciato con precisione (prima di leggere)

> *"Aggiungere a un'esposizione azionaria una **gamba di copertura**, rinunciando a parte del rialzo per limitare il
> drawdown, e **monetizzando** la copertura durante il drawdown per ricomprare più a buon mercato, produce un **CAGR di
> lungo periodo superiore** a quello del portafoglio non coperto."*

Vanno tenute separate due affermazioni che la fonte presenta insieme:

- **(A) — debole, non contesa**: la copertura riduce drawdown e volatilità. È aritmetica, e **si paga**. Nessuno la
  discute e non è questo il punto in sospeso.
- **(B) — forte, contesa**: la copertura migliora la **crescita geometrica**, cioè il premio pagato viene **più che
  recuperato** dalla minore erosione da volatilità più la monetizzazione. **È solo (B) che questa passata deve
  decidere.**

## Criteri dichiarati PRIMA della lettura

**QUALIFICA** — il claim passa da "promozionale, da verificare" a **"ipotesi con condizioni di validità"** nella mappa
dei modelli. Servono **tutte e tre**:

1. **Il costo è messo in conto**: da qualche parte compare quanto costa la protezione (in % annua del portafoglio, o
   come premio), non solo il payoff che produce.
2. **Esiste una condizione dichiarata** sotto cui regge **e una sotto cui non regge** — un claim che vale sempre non è
   un claim, è uno slogan.
3. **La regola di monetizzazione è specificata ex ante** (soglia, cadenza, quantità), non *"quando vedo paura sul
   mercato"*.

**CHIUDE** — il claim resta non approvato e si smette di riparcheggiarlo. Basta **una**:

1. Il costo della protezione **non viene mai prezzato** (si mostra il payoff senza il premio).
2. La regola di monetizzazione è **discrezionale** → è lo stesso interruttore acceso/spento non pre-registrato già
   rigettato in G2, applicato al capitale.
3. La fonte **si contraddice fra video senza dichiarare le condizioni** — e qui c'è un indizio forte già dal titolo:
   `#65` sostiene che **la copertura rovina tutto**, mentre `#47`, `#38` e `#29` sostengono il contrario.

**SOSPESO CON CONDIZIONE** — esito ammesso, e va dichiarato ora per non forzare un binario: se i video danno il
**meccanismo** in modo corretto ma **non i numeri**, il claim non si chiude né si qualifica; si riscrive la nota in `08`
dicendo **esattamente cosa mancherebbe** per deciderlo, così non si riapre una quarta volta a vuoto.

**Non conta come evidenza** (in continuità con tutto il distillamento): backtest in campione, simulazioni con parametri
non dichiarati, CAGR da percorsi auto-parametrizzati, qualunque numero accompagnato dalla vendita di un corso.

## Vincolo di portata, dichiarato ora

Qualunque sia l'esito, **non è una proposta operativa**: non abbiamo un broker opzioni, il PAC è su Trade Republic e la
fiscalità italiana tassa il 26% sul realizzato, il che penalizza per costruzione una gamba che si monetizza. L'uscita di
questa passata è **epistemica** — una voce nella mappa dei modelli e una nota riscritta in `08` — non un binario nuovo.

## I 7 video e perché ciascuno

| # | video | perché è qui |
|---|---|---|
| `#65` | The Math of "Burn the Boats": Why Hedging Ruins Everything | **il più importante**: è la contraddizione interna della fonte |
| `#16` | How to Protect your Stock Portfolio from Market Crashes | il "come si fa" del claim |
| `#42` | I want the market to crash | presumibilmente la tesi della **monetizzazione** |
| `#45` | Quant Portfolio Management and Volatility Drag | il **meccanismo** con cui la copertura dovrebbe vincere (meno erosione → più crescita geometrica) |
| `#50` | How to Trade the Cash Secured Put | struttura accessibile: **farsi pagare per comprare più in basso** = monetizzazione in forma concreta |
| `#62` | How to Trade the Covered Call | struttura accessibile: **cedere rialzo** = il lato "rinuncia" del claim |
| `#33` | How to Think About Stock Market Bubbles and Drawdowns | cornice sui drawdown |

Esclusi di proposito perché non toccano il claim: deep hedging (`#1`), variance swap (`#82`), le greche
(`#165`, `#167`, `#221`, `#236`), il corso completo sulle opzioni (`#58`). `#44` (derivazione dell'erosione da
volatilità) è **già distillato** fra i 9.

---


## Esito: **CLAIM CHIUSO** sul CAGR — e riscritto come claim condizionato sul bilancio familiare

Letti tutti e 7 i video (≈20.000 parole). Applicando i criteri dichiarati sopra: **CHIUDE**, per due dei tre motivi
previsti, più un terzo che non avevo previsto e che è il più solido.

### 1. Il costo non viene mai prezzato — in nessuno dei 7 video, né nei 3 già letti
Va dato atto alla fonte di **non nascondere l'obiezione**: il premio per il rischio di volatilità è citato
esplicitamente in `#16`, `#42` e `#45` (*"se l'assicurazione non fosse profittevole, chi diavolo la venderebbe?"*).
Ma la risposta è sempre **qualitativa**: *"si fa il giro dei preventivi come per l'assicurazione auto"*, e
*"le put molto fuori dal denaro a volte offrono convessità simile a quelle più vicine, a costo minore"* (`#16`, citando
le slide di un ETF di copertura di coda — la sigla nella trascrizione automatica è resa come "KO", probabilmente
storpiata).
**Nessun numero**: mai un costo annuo in % del portafoglio, mai un premio, mai un delta di CAGR misurato.
→ criterio 1 di QUALIFICA: **non soddisfatto**.

### 2. La regola di monetizzazione è **dichiaratamente non pubblicata**
Questo è decisivo, ed è la fonte stessa a dirlo. In `#42`:

> *"Ho queste bellissime note di ricerca quantitativa che ho scritto internamente… **l'insieme di regole vero e proprio
> per questa gamba di lunga convessità**, come monetizzare in modo efficace. Stavo pensando di pubblicarle. Non so bene
> cosa farne."*

E in `#16`: *"se non sai quali put comprare, quando rollare, come finanziarle, è esattamente quello che copro nel
corso."*
→ criterio CHIUDE n. 2, nella forma più netta possibile: **non è che la regola sia discrezionale, è che non c'è**
— o meglio, c'è e sta dietro il paywall. Un claim la cui parte operativa è deliberatamente non esposta **non è
valutabile**, e quindi non si valuta: si chiude.

### 3. 🔧 L'unica dimostrazione quantitativa ha i numeri sbagliati — **ricalcolato**
In `#45` c'è l'unico passaggio con numeri, ed è il perno di tutto l'argomento:

> *"Due strategie: una con **crescita geometrica 0%** su 10 anni, **rendimento medio 15%**, deviazione standard **30%**…
> l'altra è una gamba di copertura con crescita geometrica **−2,5%**. Le metti insieme e produci crescita geometrica
> positiva."*

Il primo numero non regge. Con $g \approx \mu - \sigma^2/2$:

| $\mu$ | $\sigma$ | crescita geometrica |
|---|---|---|
| 15% | **30%** (dichiarata) | **+10,5%** — non 0% |
| 15% | 40% (la sua stessa correzione a voce) | +7,0% |
| 15% | **54,8%** | 0% ← la volatilità che servirebbe davvero |

Lui stesso esita in diretta (*"30%, o era 40? dovrei riguardare la simulazione, vabbè"*). Ma non è un dettaglio:
**tutto l'argomento dipende dalla dimensione dell'erosione da recuperare.**

### 4. 🔧 La soglia di pareggio che la fonte non enuncia mai (e che decide la questione)
Se la gamba costa $c$ all'anno e porta la volatilità da $\sigma$ a $k\sigma$, il risparmio di erosione è
$(\sigma^2 - k^2\sigma^2)/2$. Si ripaga **solo se**:

$$\sigma > \sqrt{\frac{2c}{1-k^2}}$$

| costo annuo | la copertura porta la vol a | serve una volatilità di portafoglio superiore a |
|---|---|---|
| 1,0% | 50% | **16,3%** |
| 1,0% | 70% | 19,8% |
| **2,5%** (il suo esempio) | 50% | **25,8%** |
| 2,5% | 70% | 31,3% |
| 4,0% | 50% | 32,7% |

**L'erosione disponibile da recuperare, per un portafoglio azionario normale, è piccola**: a $\sigma$=18% vale
**1,62%/anno**, a 20% vale 2,00%/anno. Cioè: anche **azzerando del tutto** la volatilità di un portafoglio azionario
diversificato si recupererebbero ~1,6 punti l'anno — **meno** del 2,5% che costa la gamba nel suo stesso esempio.
La quadratura torna solo se la volatilità è molto alta.

### 5. 🔧 Il tassello che chiude il cerchio: **la gamba funziona solo in coppia con la leva**
E infatti in `#45` lo dice, di sfuggita e senza trarne la conseguenza:

> *"Puoi sovraperformare il compra-e-tieni… se introduci queste gambe di copertura **con un uso appropriato della
> leva**… perché se usi la leva senza uccidere il drago della volatilità, quell'effetto non lineare può farti saltare."*

**È il pezzo mancante.** La leva alza $\sigma$, la $\sigma$ alta rende l'erosione grande, l'erosione grande è ciò che
rende la copertura pagabile. Quindi il claim è coerente **solo come pacchetto azionario-con-leva + copertura** — che è
una proposta **diversa e molto più rischiosa** di "aggiungi una protezione al tuo ETF", che è invece il modo in cui
viene venduta in `#16`, `#38` e `#29`. La condizione di validità esiste, ma **non è mai dichiarata** e cambia
completamente il destinatario.

### 6. Una contraddizione verificabile con quanto avevamo già letto
In `#16`, mostrando il portafoglio coperto che ricompone in fretta dopo il crollo da dazi del 2025:
*"in effetti **assomiglia molto alla mia performance di trading dal vivo del 2025**."*
Ma il suo stesso P&L 2025, mostrato in `#133` (G3), è: 130k → **liquidato** → 70k proprio in quel periodo, poi risalita.
⚠️ **Caveat onesto**: in `#133` dichiara che quel P&L **esclude gli investimenti di lungo periodo**, quindi potrebbero
essere due libri diversi. Ma dice *"trading"*, e **non riconcilia mai le due affermazioni**.

### 7. La mia ipotesi su `#65` era sbagliata
Avevo scelto *"Why Hedging Ruins Everything"* aspettandomi la contraddizione interna della fonte. **Non lo è**: non
parla di copertura finanziaria, è un video motivazionale su battaglie, startup e relazioni ("brucia le navi").
Va comunque registrato per due ragioni:
- ⚠️ presenta come matematica un argomento **infalsificabile**: afferma che $P(\text{vittoria} \mid \text{hai le navi})
  \ll P(\text{vittoria} \mid \text{navi bruciate})$ disegnando due diagrammi di Venn, **senza un solo dato**, e
  ignorando la selezione (chi brucia le navi e affonda non fa video). È lo stesso difetto che il canale rimprovera ai
  guru.
- dichiara: *"investo il 100% del mio capitale nelle mie strategie… ho bruciato le navi, non mi copro"*. Sul **capitale
  umano** non si copre; sul **portafoglio** vende la copertura. Domini diversi, quindi non è una contraddizione formale
  — ma è la stessa persona che usa l'argomento opposto a seconda dell'oggetto.

### 8. `#50` e `#62`: meccanica corretta, **e vendono l'altro lato dello stesso premio**
Put cash-secured e covered call sono **tutorial di meccanica**, fatti bene, senza claim di performance e senza backtest.
Ma vanno notati per una cosa: insegnano a **incassare** lo stesso premio per il rischio di volatilità che la gamba di
copertura **paga**. Le due cose convivono solo con un modello che dica *quando* è caro e *quando* è a buon mercato —
cioè, di nuovo, la regola non pubblicata. Per noi sono comunque **non applicabili**: nessun broker opzioni, e la covered
call su un PAC taglia il rialzo (più il 26% sul realizzato).

### 9. `#33`: l'argomento migliore, e il suo limite
*"Non è come l'assicurazione auto: la macchina potresti non schiantarla mai. Una crisi di mercato nei prossimi 10-40
anni **ci sarà**"* — circa una per decennio, drawdown fra 20% e 80%, con il Giappone 1989-2024 come caso limite.
L'osservazione è **corretta e onesta**. Ma non porta dove vuole lui: **la quasi-certezza dell'evento è già dentro il
prezzo dell'opzione** — è esattamente ciò che rende il premio caro. La certezza del crollo giustifica il *volere*
protezione, non il fatto che sia *conveniente comprarla*. Per quello servirebbe un vantaggio di prezzo, cioè la regola
non pubblicata.

---

## Cosa sopravvive: la riformulazione che vale davvero

C'è **un** argomento, in `#42` e `#45`, che non dipende da nessun numero che la fonte non abbia dato, ed è forte:

> **La perdita tripla.** In una crisi perdi il lavoro, il valore della casa si dimezza e il portafoglio va in drawdown —
> **contemporaneamente**, perché sono tutti esposti allo stesso fattore macro. *"Ti serve liquidità esattamente quando
> serve a tutti gli altri."*

Questo **non è un argomento sul CAGR**, ed è per questo che sopravvive alla demolizione dei punti 1-5: il valore della
copertura sta nella **correlazione col capitale umano**, non nella crescita composta. E da qui esce la condizione di
validità che la fonte non enuncia mai:

> **La gamba di copertura ha senso quando il capitale finanziario è grande rispetto al capitale umano residuo.**

Che per noi risolve la questione senza bisogno di altri dati:

| | oggi (utente, 21 anni) | fra 25-30 anni |
|---|---|---|
| capitale finanziario | ~0 (PAC da 100 EUR/mese, a serbatoio) | il grosso del patrimonio |
| capitale umano residuo | **decenni di reddito** | quasi nullo |
| rapporto | ≈ 0 | alto |
| la copertura serve? | **no, e nemmeno un po'** | **è allora che la domanda diventa seria** |

Un drawdown del 40% oggi colpisce una cifra piccola e **si ricompra con i versamenti successivi** — che è esattamente
la monetizzazione, ottenuta gratis dal piano di accumulo invece che comprando put. Lo stesso drawdown a 50 anni, senza
reddito residuo per ricomprare, è un altro problema.

## Verdetto operativo

| | |
|---|---|
| **Claim (B) — "la gamba di copertura migliora il CAGR di lungo periodo"** | **CHIUSO**. Costo mai prezzato, regola di monetizzazione non pubblicata per scelta, unica dimostrazione numerica con numeri sbagliati, e soglia di pareggio che a volatilità azionaria normale **non si raggiunge**. Non si riparcheggia più. |
| **Claim (A) — "riduce drawdown e volatilità"** | vero e non conteso: è aritmetica, e **si paga**. |
| **Riformulazione (C) — "protegge contro la perdita tripla"** | **valida, con condizione**: vale quando il capitale finanziario è grande rispetto al capitale umano residuo. **Oggi non si applica**; da riprendere a ridosso della fase di decumulo, e comunque solo con un costo dichiarato. |
| **Corollario sulla leva** | se mai si valutasse (C), va valutata **come pacchetto con la leva**, perché è lì che il meccanismo funziona — non come "protezione aggiunta a un ETF". |

**Il gruppo 2 resta chiuso.** Questi 7 video non lo aprono: erano i soli che toccavano il claim, e il claim ora è deciso.
