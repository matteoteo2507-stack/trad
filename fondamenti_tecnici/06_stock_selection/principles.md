---
titolo: Stock Selection — Strategie, archetipi azienda e metodologie di screening
fonti:
  - _sorgenti/Stock conceps from defiantmentor.txt (parte STOCK SELECTION)
  - _sorgenti/Appunti estratti da pdf key concept.txt (metodologie di screening)
tipo: concetti
---

# Stock Selection — Strategie, archetipi azienda e metodologie di screening

> Selezionare azioni significa combinare **come** entrare (la strategia), **cosa** comprare (l'archetipo di azienda adatto al regime monetario) e **con quale filtro sistematico** restringere l'universo (le metodologie di screening). Questo file copre il lato *selezione*: le 4 strategie azionarie con i rispettivi caveat, gli archetipi A–D e la loro allocazione per quadrante Fed, le metriche di valutazione, la narrative / value-chain analysis, la disciplina di uscita e le metodologie quantitative di screening (CANSLIM, VCP, FTD/Distribution Days, score Druckenmiller, edge pipeline). La teoria macro/regime in sé è curata altrove ([[03_regimi_macro]]); qui si usa solo come input alla selezione.

## Concetti

### 1. Le 4 strategie azionarie (e i loro caveat)

Quattro approcci distinti osservati su peer che hanno costruito ricchezza, ognuno con un profilo rischio/skill diverso.

#### Scalping (technical, intraday)
Posizioni da secondi a ore. Quattro principi operativi:
1. **Solo azioni ad alto volume** — escludere futures, crypto e commodities. L'identità del titolo conta meno della liquidità/volatilità.
2. **Medie mobili 10 e 34 periodi** — incrocio 10>34 in trend up = buy; 10<34 in trend down = short. Segnali imperfetti, soggetti a falsi positivi e ritardo in alta volatilità.
3. **RSI come conferma momentum** — >75 ipercomprato (sell), <25 ipervenduto (buy); conferma gli incroci di media.
4. **Cap profitto e perdita all'1% per trade** — per limitare emotività e overexposure.

*Caveat*: pattern che falliscono in modo imprevedibile, controllo emotivo difficile, costi di brokeraggio elevati per l'alta frequenza. Adatto solo a chi ha talento e prontezza di esecuzione.

#### Narrative strategy (logica + value chain)
Investimento basato su catene logiche derivate da news/eventi (vedi sezione dedicata sotto). Richiede immaginazione, pensiero logico, pazienza e disciplina. Bassa frequenza di trading, orizzonte lungo.

*Caveat*: lunga attesa perché i profitti si materializzino; la "visione" può rivelarsi un sogno errato; i trend macro possono cambiare e richiedere di riaggiustare la narrativa.

#### FX trading (macro-driven, leverage)
Due metodi: (a) breve termine tecnico (stesse MA 10/34 + RSI adattati ai grafici FX, ETF per l'esposizione); (b) analisi di politica monetaria/fiscale — confrontare tassi e bilanci delle banche centrali di due paesi. **Tassi più alti + minore liquidità = valuta più forte**: long sulla valuta che restringe, short su quella che allenta. Prosperità economica via componenti GDP (C consumi, G spesa pubblica, I investimenti, X export netto), confrontando la propria view con il consensus (Bloomberg/Reuters).

*Caveat*: cambi di politica monetaria/fiscale inattesi, rischi geopolitici (es. guerra), difficoltà a prevedere GDP. Alto rischio, soprattutto con leva.

#### Commodities — **sconsigliata al retail**
Metalli, energia, agricoli; prezzi guidati da domanda/offerta, geopolitica, valute, eventi (disastri, guerre). **Esplicitamente sconsigliata**: caso reale di perdita totale di $100k su ETF WTI a leva nel 2020 (oil andò sotto zero il giorno dopo l'acquisto, perché gli ETF rappresentano *futures* e l'oversupply senza stoccaggio rese i contratti negativi). Eventi "one-off" imprevedibili rendono le commodities inadatte alla maggior parte degli investitori retail / medium-term, anche se abili nelle altre tre strategie.

### 2. Archetipi azienda A–D e allocazione per quadrante Fed

Profili di azienda definiti su quattro metriche (Revenue Growth / Earnings Growth / Forward P/E / Debt-to-EBITDA):

| Archetipo | Rev growth | EPS growth | Forward P/E | Debt/EBITDA | Sintesi |
|-----------|-----------|-----------|-------------|-------------|---------|
| **A** | 5% | 5% | 10x | 1x | Stabile, bassa crescita, debito minimo, valutazione bassa (difensiva) |
| **B** | 10% | 10% | 20x | 3x | Crescita e debito moderati, valutazione media |
| **C** | 20% | 10% | 25x | 5x | Alta crescita, alto debito, valutazione alta |
| **D** | >50% (80–100%) | Perdite | N/A | N/A (EBITDA negativo) | Crescita estrema, no earnings, molto leva, speculativa |

L'azienda ideale (rara) unisce la crescita di D alla valutazione/leva basse di A. **Confrontare sempre le metriche dentro lo stesso settore.**

**Allocazione per quadrante Fed** (tassi × liquidità di bilancio):

| Quadrante | Ambiente Fed | Approccio | Titolo preferito |
|-----------|-------------|-----------|-----------------|
| **Q1** (max liquidità) | Tassi bassi/in calo + QE (bilancio in espansione) | Molto aggressivo, fino al 100%+ (leva) | **D** — growth/speculativa, finanziamento a buon mercato |
| **Q2** | Tassi alti/in salita + bilancio in espansione | ≤50%, selettivo / osservare | **B** — equilibrio crescita/debito |
| **Q3** | Tassi bassi/in calo + bilancio in contrazione (QT) | ≤50%, selettivo / osservare | **C** — alta crescita beneficia dei tassi bassi, debito rifinanziabile |
| **Q4** (min liquidità) | Tassi alti/in salita + QT | <20% o stare a bordo campo | **A** — difensivo/cash, basso debito minimizza il rischio insolvenza |

Logica: bassa liquidità + tassi alti → favorire low-debt stabili o restare fuori; alta liquidità + tassi bassi → bet aggressivi su growth ad alta leva (finanziamento economico, forte domanda di crescita).

### 3. Metriche di valutazione

- **Forward P/E** — preferito al trailing P/E perché *forward-looking* (basato sugli earnings dell'anno prossimo). Coerenza con la crescita attesa dell'EPS.
- **WACC** (Weighted Average Cost of Capital, "whack") — tasso di sconto sui flussi futuri. Tassi bassi → WACC più basso → present value più alto a parità di earnings (es. valore = $100 / (1+r): r da 10% a 8% porta il PV da $90.9 a $92.6). È il canale per cui la politica Fed muove le valutazioni.
- **Debt/EBITDA** — leva e capacità di ripagare il debito con gli utili operativi; EBITDA usato come proxy del free cash flow operativo. Indica quanti anni di EBITDA servono per estinguere il debito — cruciale in ambiente di tassi/rifinanziamento.
- (Supporto) Revenue growth ed EPS growth come indicatori di crescita.

### 4. Narrative / value-chain analysis

Processo logico news → tesi → universo investibile:
1. **Headline** (es. "la domanda di ristorazione cala per l'inflazione").
2. **Estrai le assunzioni** (domanda ristoranti giù; inflazione presente).
3. **Catena di conseguenze** per ogni assunzione (ristoranti soffrono → fast food / hard discount beneficiano; inflazione → margini cambiano → fornitori di cibo più economico avvantaggiati).
4. **Restringi all'assunzione più plausibile** (es. catene fast food).
5. **Value chain** — identifica le aziende collegate (Burger King, McDonald's, Taco Bell, Domino's), verifica che siano quotate (anche via parent), seleziona su metriche (P/E, EV, cassa, debito, crescita). Poi **estendi a monte e a valle**: fornitori di ingredienti, packaging, design/costruzione → fino a ~10 candidati, decidendo concentrazione vs diversificazione in base alla convinzione.

**Esempio reale**: EV identificati come gamechanger nel 2017 (ipotesi 20–30% market share in 5 anni) → investimento pesante su **Tesla** → uscita dopo 4–5 anni → riallocazione su **battery recycling** (es. Glencore). Catena: tema EV → produttore → anello successivo della value chain (riciclo batterie).

### 5. Exit discipline

- Per i titoli tipo **D** in ambiente QE/tassi bassi, il timing di uscita è essenziale.
- **Uscire prontamente** ai primi segnali di **tassi in rialzo o fine del QE**, indipendentemente dall'hype mediatico o dal livello di profitto raggiunto.
- Target di profitto graduali (20%, 50%, 100%, 200%) sono tutti validi punti di uscita; ciò che conta è la **disciplina di vendere**.
- Orizzonte d'investimento intermedio (6 mesi – 2 anni); evitare il "fast money". La volatilità di breve è attesa, la ricerca diligente aumenta la probabilità.

### 6. Metodologie di screening (sistematiche)

#### CANSLIM (William O'Neil — 7 fattori)
Scoring su 7 componenti con Relative Strength multi-periodo. Implementato come screener su S&P 500 (FMP API richiesta; free tier sufficiente per ~35 titoli; scraping FINVIZ per dati istituzionali).

#### VCP — Volatility Contraction Pattern (Mark Minervini)
Screen di titoli in **Stage 2 uptrend** con contrazione progressiva della volatilità + calo del volume nella base + prossimità al pivot di breakout. Da usare solo con regime di mercato "green light" (cercare setup in un mercato rotto trova grafici che falliscono subito). Output collegabile a un breakout trade planner (pivot, stop, sizing, portfolio heat).

#### FTD / Distribution Days (IBD, metodologia O'Neil — risk tier)
- **Follow-Through Day (FTD)**: conferma del bottom di mercato. Un guadagno significativo dell'indice su **volume più alto**, al **giorno 4 o successivo** di un rally tentato = i compratori istituzionali stanno entrando.
- **Distribution Day Monitor**: conta i Distribution Days su QQQ e SPY. Tier di rischio: **0–3 NORMAL, 4–5 CAUTION, 6+ HIGH→SEVERE**. I giorni scadono dopo 25 sessioni o se l'indice sale del 5%+ dal close del Distribution Day.

#### Druckenmiller macro-to-micro score (8 input)
Integra 8 output upstream in un'unica **conviction score 0–100** (quanto essere aggressivi o difensivi). Gli 8 input: Market Breadth, Uptrend Analysis, Market Top probability, Macro Regime, FTD Detector, VCP Screener, Theme Detector, CANSLIM Screener. Calcolo locale.

#### Edge pipeline (candidate → synthesis → design → review → export)
Pipeline di ricerca dell'edge che formalizza le osservazioni di mercato *prima* di spendere tempo a backtestarle:
1. **Candidate** — genera/prioritizza ticket di ricerca da osservazioni End-Of-Day (candidate spec pronti per la pipeline).
2. **Synthesis** (concept synthesizer) — astrae più output detector in concetti d'edge riutilizzabili (tesi, segnali di invalidazione, playbook); evita di backtestare lo stesso edge in cinque modi.
3. **Design** (strategy designer) — converte i concetti in draft di strategia con entry/exit, data requirement, parametri, performance attese.
4. **Review** (strategy reviewer) — quality gate prima del backtest: plausibilità dell'edge, rischio di overfitting, dimensione del campione, realismo d'esecuzione, survivorship bias.
5. **Export** — orchestrato dall'edge pipeline orchestrator (sequenzia tutte le skill via subprocess).

> Nota trasversale: ogni ora spesa a raccogliere dati a mano o a fare calcoli ripetitivi è un'ora non spesa su strategia e decisioni — il lato screening va automatizzato.

## Collegamenti

- **Applicazione nel repo**: `../../strategies/stock_selector/` — lo Stock Selector V6.0 è **dove questi concetti si applicano** (scoring fondamentale + RRG + scenario macro). Vedi `../../strategies/stock_selector/strategy.py`, `scoring.py`, `config.yaml`.
- **Consensus layer**: `../../agents/consensus/` — 4 personas che riesaminano un ticker pre-screenato (Damodaran valuation, Buffett quality/moat, Burry contrarian/value, Taleb tail-risk).
- **Agente di selezione**: `../../agents/stock_selector.md`.
- [[03_regimi_macro]] — quadranti Fed, QE/QT, indicatori macro (input alla selezione; teoria curata lì, non duplicata qui).
- [[05_portfolio_rischio]] — sizing, portfolio heat, exit discipline a livello di portafoglio.
- [[07_data_sources]] — endpoint e provider dati che alimentano screening e scoring.
- Contesto progetto: lo Stock Selector è un progetto **dinamico** (oggi semiauto, automatizzabile), parallelo a PAC e worldmonitor — vedi `../../DECISIONS.md` e `../../PROJECT.md`.

## Fonti

- `_sorgenti/Stock conceps from defiantmentor.txt` — parte STOCK SELECTION: 4 strategie (scalping, narrative, FX, commodities), archetipi A–D, quadranti Fed lato selezione, narrative/value-chain, exit discipline.
- `_sorgenti/Appunti estratti da pdf key concept.txt` — metodologie di screening: CANSLIM, VCP, FTD/Distribution Days, Druckenmiller score, edge pipeline.
