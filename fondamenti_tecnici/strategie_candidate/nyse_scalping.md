---
titolo: NYSE Scalping (VWAP + TPO + OTF)
fonti:
  - "_sorgenti/NYSE Scalping Strategy_251011_114145.pdf"
tipo: strategia_candidata
---

# NYSE Scalping (VWAP + TPO + OTF)

> **STATO: candidata — NON costruita.** Spec pronta per essere promossa a strategies/<nome>/ (Python) o mql5/ (EA) SE prioritizzata. Oggi NON in piano: vedi ../../DECISIONS.md (strategie custom per ultime) e l'indice ../../strategies/README.md (sezione Candidate).

## Ipotesi di mercato

Strategia di **scalping intraday sulla sessione di New York** (fonte: Manuel Porcelluzzi). L'idea operativa è leggere l'intenzione del flusso istituzionale tramite **Volume Profile / TPO (Time Price Opportunity)** e **OTF (Order Time Frame)**, e usare il **VWAP della sessione NY** come trigger di esecuzione direzionale dopo l'apertura.

Concetti portanti:
- **Value (area di valore)**: porzione del profilo volumetrico compresa tra **VAH** (Value Area High) e **VAL** (Value Area Low). Il confronto del Value di oggi con quello del giorno precedente definisce il bias.
- **Forme distributive TPO** (lettura della forma del profilo della giornata):
  - **P profile = RIALZO** (uptrend).
  - **D profile = CONSOLIDAMENTO** (mercato in bilanciamento / range).
  - **b profile = RIBASSO** (downtrend).
  - **B profile = RIBASSO** (downtrend, distribuzione doppia/estesa).
- **OTF (Order Time Frame)**: time frame dominante dell'ordine/flusso; usato sul **Daily** come filtro di trend di fondo.
- **VWAP NY**: prezzo medio ponderato per volume della sessione di New York; la sua rottura su candela 1M è il segnale di ingresso.

Logica di confluenza: si opera quando **OTF Daily**, **bias TPO/STPO** (Value vs giorno precedente) e **rottura VWAP NY** puntano nella stessa direzione. Setup con filtri discordi = no trade (vedi risk).

## Indicatori & settaggi

Indicatori necessari (i settaggi precisi nel PDF sono mostrati a schermo per ciascuno; qui sono elencati gli indicatori e l'uso previsto):

- **"Lon & NY Open" by JonFibonacci** — apertura sessioni Londra/New York.
  - https://it.tradingview.com/script/b7XslGHJ-Lon-NY-Open/
- **Sessions [LuxAlgo] by LuxAlgo** — box delle sessioni.
  - https://it.tradingview.com/script/bkb6vZDz-Sessions-LuxAlgo/
- **OTF by Teoadams** — Order Time Frame.
  - https://it.tradingview.com/script/UF5GU16E-OTF/
- **Weekly Open Line by vanbumi** — riferimento weekly open (zona di interesse per il TP).
  - https://it.tradingview.com/script/DeNJA1Sq-Weekly-Open-Line/
- **TPO** (Time Price Opportunity) e **STPO** (Session TPO) — profilo distributivo e Value.
- **VWAP** della sessione NY.
- **Volume Profile** (supporto al concetto di Value / VAH-VAL / Single Print).
- **Price action (base)** — lettura candela su 1M per il trigger.

> NB: i settaggi numerici esatti dei singoli indicatori sono nelle slide "SETTING INDICATORI" della fonte (mostrati come screenshot); replicare da lì al momento della costruzione.

Time frame di lavoro (dalla checklist):
- **OTF → 1D**.
- **Value TPO Daily → m30**.
- **Value TPO New York → m1** (escludendo i weekend).
- **Trigger di entrata → m1** (rottura VWAP).

## Setup di entrata

Finestra operativa: **15:00–18:00 ora NY**, con **attesa di 15–30 minuti dopo l'apertura NY** prima di operare. Se c'è una news rilevante (es. alle 16:00), si opera **post news**.

Sequenza (checklist della fonte):
1. Vedere le **news** di giornata.
2. Definire l'**OTF** sul time frame **1D**.
3. Definire il **Value TPO Daily** sul time frame **m30**.
4. Definire il **Value TPO New York** sul time frame **m1** (escludere weekend).
5. **Attendere 15–30 min** dall'apertura di New York.
6. Aspettare la **rottura del VWAP NY** sul m1.
7. **Entry** sulla **chiusura della candela m1 che rompe il VWAP** (chiusura sopra VWAP → long; chiusura sotto VWAP → short), coerentemente con il bias di confluenza.

Bias direzionale dato dal Value (TPO e STPO si leggono allo stesso modo):
- **Rialzista**: i Value sono **superiori** rispetto a quelli del giorno precedente.
- **Ribassista**: i Value sono **inferiori** rispetto a quelli del giorno precedente.
- **Neutro**: i Value sono **interni** (compresi dentro) rispetto a quelli del giorno precedente → non direzionale.

## Setup di uscita & risk

**Stop Loss**: su **minimo / massimo precedente** (estremo della struttura prima del trigger).

**Take Profit**: **RR 1:3** oppure **zone di interesse** (Weekly Value / ATH / Single Print).

Gestione delle operazioni — **de-risking graduale** del trade:
- **Take Profit 1 → RR 1:2**.
- **Take Profit 2 → RR 1:3**.
- **Post 1:3**: lasciare una size correre in **trailing profit**.

Gestione fissa (alternativa):
- **Take Profit totale → RR 1:3**.
- Possibile **parziale a RR 1:2**.
- **Break Even a RR 1:1**.

Dimensionamento del rischio per qualità del setup (esempi della fonte):
- **Caso 1 — Setup +++** (tutti i filtri concordi): **risk 0,25%**.
- **Caso 2 — Setup -++** (un filtro non ottimale): **risk 0,1%**.
- **Caso 3 — no trade**: filtri discordi / giorno off.

## Filtri & off-days

**Filtri operativi** (devono concordare per il setup "+++"):
- **OTF Daily** (trend di fondo sul 1D).
- **TPO Value di giornata** (Daily, m30) vs giorno precedente.
- **TPO Value di New York** (m1).
- **Orari operativi 15:00–18:00 NY** + attesa 15–30 min post apertura; post news se c'è evento.

Quando i filtri sono **discordi** → **no trade** (vedi Caso 3).

**Off-days (NON operare)**:
- **New York chiusa**.
- **FED** — il **giorno prima** e il **giorno stesso** dell'evento.
- **Flash crash / eventi esogeni**.

## Come promuoverla

Quando/se prioritizzata (vedi ../../DECISIONS.md — le strategie custom sono in fondo alla pipeline):

1. **Copia lo scaffold** da ../../strategies/_template/ in `strategies/<nome>/` (proposta: `strategies/nyse_scalping/`).
2. Segui i pattern di nuova strategia in ../../CONVENTIONS.md (struttura `strategy.py`, `config.yaml`, `__main__.py`, README).
3. **Decidi il runtime**: Python (analisi/backtest weekend) oppure **EA MQL5** in `mql5/` se va eseguita live sul VPS MetaQuotes — coerente con il pivot ibrido Python/MQL5.
4. **Modella i componenti** come feature riproducibili senza gli indicatori TradingView proprietari: VWAP di sessione, Value Area (VAH/VAL) da Volume Profile, forma distributiva TPO/STPO, OTF Daily, finestra oraria NY.
5. **Codifica i filtri** (OTF Daily, Value vs giorno precedente, finestra 15:00–18:00 + delay 15–30 min, esclusione FED/holiday/eventi) e le regole di risk (SL su estremo precedente, scaling 1:2 / 1:3, trailing, break even 1:1, sizing 0,25% / 0,1%).
6. **Backtest con quant-review** (../../docs/QUANT_REVIEW_PROTOCOL.md): attenzione al **look-ahead** sui Value/TPO calcolati sul giorno stesso (usare il profilo del giorno **precedente** come riferimento, mai il close corrente).
7. **Walk-forward** e validazione prima di qualsiasi live; poi shadow run come da prassi (cfr. confluence_auto).

## Collegamenti

- [[02_liquidita_orderflow]] — TPO, Volume Profile e Market Profile sono trattati lì.
- ../../strategies/_template/ — scaffold da usare quando/se la si costruisce.
- ../../CONVENTIONS.md — pattern di una nuova strategia.
- ../../DECISIONS.md — priorità: strategie custom per ultime.
- ../../strategies/README.md — indice strategie, sezione Candidate.

## Fonti

- `_sorgenti/NYSE Scalping Strategy_251011_114145.pdf` — Manuel Porcelluzzi, "NYSE Scalping Strategy" (~33 pagine, italiano). Distillato fedele: concetti, indicatori, forme distributive TPO (P/D/b/B), filtri operativi, finestra oraria, checklist, regole di risk e off-days. Le slide "SETTING INDICATORI" e "ESEMPI DI TRADE" sono prevalentemente screenshot di chart da consultare nella fonte al momento della costruzione.
