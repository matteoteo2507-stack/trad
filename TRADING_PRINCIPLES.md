# Trading Principles

Costituzione operativa: i concetti **non si cambiano**, le strategie di ingresso possono variare.
Distinzione di Matteo (post mentore): "tradare sui concetti vs tradare da strategia — noi siamo
una via di mezzo, i concetti devono essere fissi, le strategie possono adattarsi al regime".

Ogni voce qui sotto è una regola decisionale, non una nozione teorica.

---

## 1. Regimi di mercato (cosa stai tradando)

Il mercato è in uno di **6 stati** in ogni momento, dato da `direzione × volatilità`:

| Regime | Direzione | Volatilità | Strategia adatta |
|---|---|---|---|
| Bull Quiet | Up | Bassa | Trend-following su pullback (Confluence S/D long con-trend) |
| Bull Volatile | Up | Alta | Momentum / breakout, SL larghi |
| Bear Quiet | Down | Bassa | Speculare al Bull Quiet (short su pullback) |
| Bear Volatile | Down | Alta | Breakout short, attenzione ai gap |
| Sideways Quiet | Sideways | Bassa | Mean-reversion su S/R (Confluence ottimale) |
| Sideways Volatile | Sideways | Alta | **Stay out o size dimezzata** |

**Come identificare il regime (automatizzato, deterministico):**

Esegui `python -m core.regime --symbols EURUSD=X,XAUUSD=X --journal` e copia
l'output nel journal. La classificazione segue un albero deterministico basato
sul **DMI di Wilder (1978)**, senza più conteggi visuali HH/HL (rimossi nella
versione 2026-05-25 perché empirici e generavano dati sporchi):

1. **Direzione** (gated da ADX, vedi [`core/regime.py`](core/regime.py)):
   - `ADX(14) < 25` → **Sideways** (direzione ignorata, trend troppo debole).
   - `ADX(14) ≥ 25` AND `+DI(14) > -DI(14)` → **Bull**.
   - `ADX(14) ≥ 25` AND `-DI(14) > +DI(14)` → **Bear**.

2. **Volatilità**:
   - `ATR(14) > SMA(50)_ATR` → **Volatile**.
   - `ATR(14) ≤ SMA(50)_ATR` → **Quiet**.

3. **Note di lettura**:
   - `ADX > 40` = trend forte, attenzione al rischio di esaurimento (i +DI/-DI
     restano la direzione, ma è prudente valutare continuation vs reversal).
   - I `+DI` e `-DI` sono "sottoprodotti gratuiti" del calcolo ADX — usarli per
     la direzione invece di HH/HL elimina la discrezionalità senza aggiungere
     indicatori nuovi.

**Regola operativa**: il regime viene scritto in cima al `journal_settimana_*.md`
ogni domenica come output di `python -m core.regime`. Se `Sideways Volatile`,
**dimezza il size o stai fuori**. Niente eccezioni.

**Riferimenti**:
- Wilder J.W. (1978) — *New Concepts in Technical Trading Systems*, Trend Research.
  (DMI, +DI, -DI, ADX nella loro forma canonica).
- Estensione futura possibile: filtro di lungo termine `close vs SMA(200)` come
  conferma (Faber JWM 2007). Non incluso in v1 per evitare sovra-ingegnerizzazione
  prima del Quant Reviewer.

---

## 2. Importanza dei livelli S/R orizzontali

Un livello S/R **non vale uguale a un altro**. Due dimensioni:

**(a) Timeframe in cui è identificato** — più alto, più forte:
- Monthly > Weekly > Daily > H4 > H1 > M15
- Un livello Weekly che coincide con un livello H4 è confluenza tra TF.

**(b) Numero di test** — la letteratura è divisa, ma per noi vale questo:
- **1–2 touch con rejection netta**: livello forte, ancora "carico".
- **3 touch**: livello a rischio di rottura imminente. Non usarlo come entry primario.
- **4+ touch**: livello "esaurito", aspettati rottura. Usalo come livello-target di un breakout, non come entry.

**Regola operativa**: nel campo `confluence` di `levels.yaml`, segna sempre il timeframe del livello
(`SR_weekly`, `SR_D1`, `SR_H4`, `SR_H1`). Se hai contato i touch, annotali a parte nel weekend journal
ma non in `levels.yaml` (non lo legge il loader).

---

## 3. Zone di Supply / Demand — il concetto di freshness

Una zona S/D **perde potere ogni volta che il prezzo la visita**, perché gli ordini istituzionali
dentro la zona vengono "consumati":

| Stato | Probabilità di reazione |
|---|---|
| Fresh (mai testata) | Massima — ordini originali ancora presenti |
| Tested 1x | Alta ma in calo |
| Tested 2–3x | Media, in calo progressivo |
| Tested 4+ | Bassa, zona esaurita, probabile rottura |

**Distinzione importante con S/R** (vedi sezione 2): S/R è livello psicologico/strutturale che si
"rafforza per consenso"; S/D è livello di liquidità che si "consuma per esecuzione". Le due scuole
guardano cose diverse. Non confonderle.

**Regola operativa**: prediligi sempre zone S/D **fresh** o `tested_1`. Se nella tua analisi weekend
identifichi una S/D `tested_3+`, usala come **target di breakout**, non come entry.

---

## 4. Livelli di Fibonacci — significato delle zone

Misurati su un movimento direzionale chiaro (swing low → swing high in un trend up, viceversa).

| Zona | Comportamento atteso | Uso |
|---|---|---|
| 0 → 0.236 | Pausa/consolidamento, reazione lenta o assente | Non usare come entry |
| 0.236 → 0.382 | Continuo del trend, possibile reject aggressivo al **0.382** | Entry valido in trend forte |
| 0.382 → 0.5 | Continuo, rigetto lento al **0.5** | Entry valido in trend medio |
| 0.5 → 0.618 | Continuo con reversal aggressivo ad alta probabilità al **0.618** (Golden Ratio) | **Entry primario in retracement** |
| 0.618 → 0.786 | "Golden Zone" — area ad alta probabilità di reversal | Entry alternativo se 0.618 non ha tenuto |
| 0.786 → 1.0 | "Last resort": oltre il 0.786 il setup è probabilmente invalidato | NON entrare, aspetta nuova struttura |

**Note di realismo**:
- Le probabilità sopra sono **percezioni statistiche aneddotiche**, non studi peer-reviewed.
  Funzionano perché molti trader le osservano (self-fulfilling), non perché ci sia un edge dimostrato.
- 0.886 non è uno standard Fibonacci, è usato in armoniche (Gartley). Non lo usiamo.

**Regola operativa**: un livello Fibonacci **da solo non basta**. Va sempre in confluenza con almeno
un altro elemento di natura diversa (S/R, S/D, POC). Marker in `levels.yaml`: `Fib_236`, `Fib_382`,
`Fib_50`, `Fib_618`, `Fib_786`.

---

## 5. Criteri di ingresso — massimo 3, in ordine fisso

Verificare nell'ordine. Se uno fallisce, **scarta il setup**. No "ricuci dopo".

1. **Livello operativo valido**:
   - Type definito (S/R con TF specificato, S/D fresh o tested_1, Fib 0.618/0.786)
   - Confluenza ≥ 2 elementi di natura diversa (regola pratica della "natura diversa": SR_D1 + Fib_618 sì,
     SR_D1 + SR_D1 no)

2. **Bias coerente col regime corrente** (vedi sezione 1):
   - Mean-reversion su S/D → solo in Sideways Quiet o pullback in Bull/Bear Quiet con-trend
   - Breakout → solo in Bull/Bear Volatile o in uscita da Sideways Quiet
   - Sideways Volatile → niente trade

3. **Setup VALIDO vs INCERTO**:
   - **Valido**: dal punto di entrata, il primo livello strutturale ad alta probabilità di essere
     raggiunto in giornata permette **RR ≥ 1:3 senza forzare il TP** oltre quel primo livello.
   - **Incerto**: per arrivare a 1:3 devi puntare a un livello oltre il primo (target meno probabile
     in giornata). **Skip o size dimezzata.**

**Niente conferme di candele, niente conteggi di rifiuti, niente "aspetto la chiusura M15".**
Entrata con **ordine limit sul livello** o sull'ingresso pianificato dal piano weekend. L'ordine limit
toglie il "io ho voglia di entrare" — è disciplina meccanica, non psicologica.

**Regola di re-entry**: dopo uno stop, **NIENTE re-entry stesso giorno sullo stesso lato senza una
nuova invalidazione strutturale**. Lo stop = il setup era sbagliato o anticipato; ri-entrare subito
con un secondo ordine è bias di recupero, non analisi.

---

## 6. Disciplina del backtest a mano

Tre regole che vengono dall'osservazione di settimana 1 (3 trade manuali su 4 forzati):

1. **Replay a velocità controllata**: TradingView Bar Replay 1 barra alla volta. Mai velocità continua —
   sporca la price action, induce a forzare.
2. **Solo ordini limit anche in backtest**: piazza l'ordine *prima* che il prezzo arrivi, come faresti
   in live. Niente entrate "al market" perché "vedo che si gira".
3. **Stesso journal del live**: stesso formato setup/non-setup, stesso campo "valido/incerto", stesso
   campo "regime corrente". Senza identità di formato, i dati di backtest e live non si confrontano.

**Obiettivo backtest a mano**: raccogliere statistiche più velocemente del live (che fornisce 2–5 trade
a settimana). Target minimo: **+1h di backtest per settimana**, con almeno 5 setup analizzati.

---

## 7. Volume Profile / POC come strumento di conferma

Il Volume Profile mostra il volume scambiato **per livello di prezzo** (istogramma orizzontale), non
per tempo. Conferma matematica della percezione visiva di "dove c'è densità di ordini".

**Tre elementi (in ordine di importanza per noi):**

| Elemento | Cos'è | Uso |
|---|---|---|
| **POC** (Point of Control) | Livello con più volume scambiato nel periodo | Magnete del prezzo, S/R fortissimo |
| **VAH / VAL** | Estremi della Value Area (70% del volume) | Confini di "zona di valore" |
| **HVN / LVN** | High / Low Volume Nodes | HVN = S/D oggettiva, LVN = vacuum (target di breakout) |

**Uso operativo settimanale (manuale, su TradingView):**
- Per livelli **strutturali long-term**: VP su 3–6 mesi
- Per livelli **weekly operativi**: VP sull'ultimo mese
- Per livelli **intraday** (M15): VP della settimana precedente

**Regola di confluenza**: un livello S/R o S/D che coincide entro **10 pip (forex)** / **50 pip (XAU)**
con un POC weekly o monthly è di **alta priorità**. Marker: `POC_weekly`, `POC_monthly`.

**Limite onesto — tick volume vs volume reale**:
Il forex spot è OTC: TradingView mostra **tick volume** (numero di update di prezzo), proxy del volume
reale (correlazione ~0.85–0.90 coi futures CME). Per livelli importanti, conferma su:
- XAUUSD → `GC1!` (gold futures continuous, volume reale)
- EURUSD → `6E1!` (EUR futures CME, volume reale)

Per livelli intraday minori, il tick volume forex è sufficiente.

---

## Journaling

Il journaling è organizzato su **due fonti complementari**:

- **Markdown settimanale** in `journals/journal_settimana_<YYYY-MM-DD>.md` (gitignored):
  ospita il **planning weekend** (regime di mercato, livelli multi-TF, Fibonacci, POC,
  setup, news) e la **review settimanale** (Trade NON eseguiti, osservazioni di
  mercato, auto-valutazione). Compilato la domenica + ogni sera di trading.
- **Notion `Trading Journal`** (database unico Live + Demo + Backtest): ospita i
  **trade eseguiti**, una riga per trade, compilabile da mobile *quando il trade
  viene preso*. Schema in [`journals/NOTION_JOURNAL_SCHEMA.md`](journals/NOTION_JOURNAL_SCHEMA.md).

I due si collegano via `Setup ID` (es. `EURUSD-2026W19-S1`): il markdown lo
definisce in fase di planning, Notion lo riferisce in fase di esecuzione.

Registrare il trade *quando lo prendi*, non a fine giornata a memoria. Le emozioni
pre-trade e le deviazioni dal piano sono i KPI comportamentali più predittivi del
drawdown — saltarli vanifica il valore del journal.

---

## Cosa fare quando un trade va contro queste regole

Tre opzioni, **non** "rivedo la regola":

1. **Annotalo nel journal della settimana** come deviazione, con il motivo.
2. **Se la deviazione si ripete 3+ volte con risultati positivi**, valutiamo se la regola va aggiornata.
3. **Se la deviazione si ripete 3+ volte con risultati negativi**, la regola è giusta e tu stai
   sbagliando — stop, niente trade per 1 settimana di reset.

Le regole si aggiornano **con dati**, non con sensazioni.
