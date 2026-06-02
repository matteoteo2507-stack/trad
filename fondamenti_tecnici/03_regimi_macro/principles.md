---
titolo: "Regimi di mercato (Markov) e timing macro"
fonti:
  - "Markov regime skill for claude.txt (framework Roan / @RohOnChain)"
  - "Stock conceps from defiantmentor.txt (solo parte macro: framework Fed, 5-metric timing, lettura dati macro)"
tipo: concetti
---

# Regimi di mercato (Markov) e timing macro

> Due lenti complementari per dire "dove siamo" nel ciclo. La prima è **probabilistica**: modella il mercato come una catena di Markov a 3 stati (Bull/Bear/Sideways) e ne misura la matrice di transizione, da cui ricava un segnale firmato e un forecast n-step. La seconda è **macro-discrezionale**: il framework Fed (tassi + bilancio) con 4 quadranti di allocazione, una checklist di timing a 5 metriche (empirica, ~80-85% nell'era post-2008 QE) e gli indicatori macro leading da monitorare. Entrambe NON sostituiscono il classificatore deterministico già in repo ([`../../core/regime.py`](../../core/regime.py), Wilder DMI/ADX/ATR): lo affiancano.

## Concetti

### 1. Catena di Markov a 3 stati (probabilistico)

**Idea di fondo.** Il prossimo stato del mercato dipende dallo stato corrente: i regimi *persistono*, non si invertono senza preavviso. La matrice di transizione è la "contabilità" di questa proprietà. Una desk quant guarda lo stesso grafico di un retail e vede questa matrice. (Distillato fedele dalla fonte; l'analogia con PageRank di Google e con il rating di un prestito — `current → 30 → 60 → 90 giorni`, non si salta — è retorica della fonte, non una dimostrazione formale.)

- **3 stati osservabili**: `Bull`, `Bear`, `Sideways`.
- **Label dei regimi** da *rolling return* a 20 giorni:
  - rolling return `> +2%` → **Bull**
  - rolling return `< -2%` → **Bear**
  - altrimenti → **Sideways**
  La soglia (`±2%`) e la finestra (`20gg`) sono parametri, non costanti universali.

- **Matrice di transizione 3×3 `P`**: stimata via **MLE counting** — si contano le transizioni osservate `stato_t → stato_{t+1}` e si normalizza ogni riga a somma 1 (matrice stocastica per righe). `P[i,j]` = probabilità di passare da `i` a `j`.

- **Persistence diagonal**: gli elementi diagonali `P[i,i]` misurano quanto spesso uno stato *resta* dove si trova. È la quantità "load-bearing" del modello: alto = regime persistente, basso = regime instabile. Gli off-diagonali sono la frequenza dei flip.

- **Distribuzione stazionaria `π`**: il mix di regimi nel lungo periodo. È l'autovettore sinistro di `P` associato all'autovalore 1 (`π P = π`), normalizzato a somma 1. Serve come *baseline / sanity check di tail-risk* prima di dimensionare: "in media storica quanto tempo il mercato passa in Bear?".

- **Forecast n-step (Chapman-Kolmogorov)**: la matrice a `n` passi è `P^n` (la potenza n-esima). Da `P^n` leggi la distribuzione di probabilità su dove sarà il mercato fra `n` giorni, dato lo stato attuale.

- **Segnale firmato** dato lo stato corrente `s`:
  `signal = P(next = Bull | s) − P(next = Bear | s)`
  Positivo → long, negativo → short, magnitudine → convinzione. La versione semplice prende solo il segno (`+1 / 0 / −1`) come posizione.

- **Walk-forward senza look-ahead**: a ogni giorno `t` la matrice viene ri-stimata SOLO sui dati esistenti prima di `t`, si deriva il segnale dallo stato corrente, si tiene la posizione un giorno e si misura il rendimento del giorno dopo. Si riportano Sharpe annualizzato e max drawdown. Questo è il dettaglio che separa un edge reale da un backtest gonfiato (la fonte lo chiama "YouTube backtest scam"). Nessun tuning.

> **Caveat look-ahead (cross-repo).** Lo stesso errore che il walk-forward evita qui è già documentato per la regime timeline del repo: `../../data/regime_timeline_gbpusd.csv` ha la label calcolata sul *close del giorno stesso* → usarla SOLO con lag di 1 giorno per strategie intraday, altrimenti si gonfia l'edge. Vedi [`../../DECISIONS.md`](../../DECISIONS.md).

### 2. Framework Fed (defiantmentor)

Due sole leve della Fed governano la liquidità di mercato:

1. **Tasso d'interesse** — basso → valutazioni più alte (WACC più basso → maggior valore attuale dei flussi futuri; capitale che migra da bond a azioni); alto → l'opposto.
2. **Bilancio** — **QE** (acquisto bond/MBS, inietta liquidità) vs **QT** (vende o lascia scadere, ritira liquidità).

Incrociando le due leve si ottiene una "scacchiera" di **4 quadranti**, ciascuno con una % di allocazione suggerita e un archetipo di azienda preferito (qui solo accennato — dettaglio degli archetipi A/B/C/D in `06_stock_selection`):

| Quadrante | Ambiente Fed | Allocazione | Archetipo preferito |
|---|---|---|---|
| Q1 (massima liquidità) | tassi bassi/in calo + QE | molto aggressivo, fino a 100%+ (leva) | D (iper-crescita, in perdita, alta leva) |
| Q2 | tassi alti/in salita + bilancio in aumento | ≤50%, selettivo/osservare | B (crescita e debito moderati) |
| Q3 | tassi bassi/in calo + bilancio in calo | ≤50%, selettivo/osservare | C (alta crescita, alto debito rifinanziabile a basso costo) |
| Q4 (minima liquidità) | tassi alti/in salita + QT | <20% o sidelines | A (basso debito, bassa valutazione, difensivo) |

Logica: liquidità bassa + tassi alti → si scoraggia il rischio (o aziende stabili a basso debito); liquidità alta + tassi bassi → si premia la crescita leveraged. **Caveat della fonte**: per gli archetipi D in fase QE il *timing di uscita* è critico — vendere ai primi segni di rialzo tassi / fine QE, a prescindere dall'hype.

### 3. Market timing a 5 metriche (empirico)

Checklist di entrata "macro-panico" della fonte. Quando **tutte e 5** si allineano, la fonte stima ~**80-85%** di probabilità storica di guadagno:

1. **VIX > 30** (paura elevata; calma tipica 15-20).
2. **Tasso Fed stabile o in calo** (non in traiettoria di rialzo).
3. **Deleveraging del margin debt FINRA** (debito a margine in calo; dato in ritardo di ~1 mese).
4. **Settore leader identificato** (tema che attira capitale istituzionale).
5. **Earnings beat del leader** (EPS/ricavi del settore guida battono il consenso anche durante il panico).

> **Empirico, non dimostrato.** La fonte è esplicita: l'80-85% è una stima storica valida nell'**era post-2008 di QE**, cioè *assume una Fed che interviene attivamente* (taglia tassi, inietta liquidità, evita credit freeze). Il restante 15-20% di fallimenti viene da rotture sistemiche dove le 5 metriche si allineano ma il mercato crolla comunque: dot-com 2000-01, scandali contabili 2002, GFC 2008 (bull trap), errore di comunicazione Fed 2022. Metriche di guardia aggiuntive citate: credit spread (junk vs Treasury), inflazione (CPI), fiducia nei bilanci contabili.

### 4. Indicatori macro leading

La Fed monitora 3 aree (lavoro, inflazione, attività economica). Tra gli ~10 indicatori, quelli **leading** (anticipatori) più utili al posizionamento:

- **Initial Jobless Claims** (settimanali) — anticipa il tasso di disoccupazione. Range normale ~250k-350k; >350k stress, <250k forza.
- **PPI** (Producer Price Index, mese su mese) — anticipa il CPI (inflazione vista dal lato produttori). Normale ~0%-0,2% m/m.
- **PMI** (ISM Manufacturing/Non-Manufacturing, Chicago PMI) — indici survey: 50 = neutro, >55 espansione, <50 contrazione. Il Chicago PMI anticipa l'ISM Manufacturing di 1-2 mesi.

Logica Fed generale: letture forti → policy contrattiva; letture deboli → policy espansiva. **Caveat della fonte**: nessun singolo dato determina meccanicamente la mossa Fed; i dati sono correlati e vanno letti insieme, ed eventi imprevisti (es. COVID) possono ribaltare l'interpretazione.

### 5. Markov vs classificatore deterministico del repo

Sono **complementari, non alternativi**:

| | `core/regime.py` (repo) | Markov (questa nota) |
|---|---|---|
| Natura | **deterministico** | **probabilistico** |
| Stati | 6 (`direzione × volatilità`) | 3 (`Bull/Bear/Sideways`) |
| Metodo | Wilder DMI/+DI/-DI/ADX + ATR | rolling return + matrice di transizione MLE |
| Output | etichetta secca del regime corrente | distribuzione di probabilità + segnale firmato + forecast n-step |

Il deterministico (descritto in [`../../TRADING_PRINCIPLES.md`](../../TRADING_PRINCIPLES.md) §1) risponde a "in quale stato siamo *ora*"; il Markov aggiunge "con quale probabilità ci spostiamo *dopo*". Il Markov in repo è un'idea non committata (vedi blueprint).

## Collegamenti

- [[markov_regime_skill]] — blueprint implementativo della skill Markov (modulo `regime.py`, HMM, PineScript). STATO: idea non committata.
- [[06_stock_selection]] — dettaglio archetipi azienda A/B/C/D per quadrante Fed (curato da altro agente).
- Classificatore deterministico in repo: [`../../core/regime.py`](../../core/regime.py), documentato in [`../../TRADING_PRINCIPLES.md`](../../TRADING_PRINCIPLES.md) §1.
- Caveat look-ahead della regime timeline: [`../../data/regime_timeline_gbpusd.csv`](../../data/regime_timeline_gbpusd.csv) e [`../../DECISIONS.md`](../../DECISIONS.md).
- Priorità di workspace (agenti/strategie custom in fondo): [`../../DECISIONS.md`](../../DECISIONS.md).

## Fonti

- **"Markov regime skill for claude.txt"** — framework di Roan (@RohOnChain), installato come skill Claude Code da Lewis Jackson. Parte teorica: catena di Markov osservabile a 3 stati, matrice di transizione MLE, distribuzione stazionaria, Chapman-Kolmogorov, walk-forward senza look-ahead.
- **"Stock conceps from defiantmentor.txt"** — solo la parte macro: framework Fed (2 leve, 4 quadranti), 5-metric market timing (empirico, era post-2008 QE), lettura degli indicatori macro leading (jobless claims, PPI, PMI). La parte di stock-selection è curata da un altro agente.
