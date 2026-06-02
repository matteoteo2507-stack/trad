---
titolo: "Blueprint — Skill Markov regime (osservabile + HMM opzionale)"
fonti:
  - "Markov regime skill for claude.txt (framework Roan / @RohOnChain, skill Claude Code di Lewis Jackson)"
tipo: blueprint
---

# Blueprint — Skill Markov regime (osservabile + HMM opzionale)

> **STATO: idea — NON committata.** Vedi [`../../DECISIONS.md`](../../DECISIONS.md) (priorità 2026-05-30: agenti/strategie custom per ultime). Nel repo c'è già [`../../core/regime.py`](../../core/regime.py) deterministico; questa skill sarebbe un'alternativa/estensione probabilistica, da valutare, non in piano.

> Distillato implementativo della skill `markov-hedge-fund-method`: un modulo Python che etichetta i regimi da rolling return, costruisce la matrice di transizione, risolve la stazionaria, fa forecast n-step e gira un walk-forward senza look-ahead — più un layer HMM opzionale e un indicatore PineScript per la visualizzazione live su TradingView. La teoria sottostante è in [[principles]] (`03_regimi_macro`).

## Concetti

### 1. Modulo `regime.py` (modello osservabile)

Funzioni-chiave (firme distillate fedelmente dalla fonte):

- **`label_regimes(close, window=20, threshold=0.02)`**
  Calcola il rolling return `close.pct_change(window)` ed etichetta:
  `> +threshold` → Bull (2), `< -threshold` → Bear (0), altrimenti → Sideways (1). Ritorna la serie di label (encoding intero `Bear=0, Sideways=1, Bull=2`).

- **`build_transition_matrix(labels)`**
  Stima MLE della matrice 3×3: conta le transizioni `arr[i] → arr[i+1]`, normalizza ogni riga a somma 1. Guardia anti divisione-per-zero sulle righe vuote (`row_sum == 0 → 1.0`).

- **`stationary_distribution(P)`**
  Autovettore sinistro di `P` con autovalore ≈ 1 (`np.linalg.eig(P.T)`, indice dell'autovalore più vicino a 1), preso in valore assoluto e normalizzato a somma 1.

- **`n_step_forecast(P, n)`**
  Chapman-Kolmogorov: `np.linalg.matrix_power(P, n)` = matrice di transizione a n passi.

- **`signal_from_matrix(P, current_state)`**
  `P[current_state, 2] - P[current_state, 0]` = `P(next=Bull) − P(next=Bear)`. Positivo → long, negativo → short.

- **`walk_forward_backtest(close, labels, min_train=252)`**
  A ogni `t` da `min_train` in poi: ri-stima `P` su `labels.iloc[:t]` (solo passato), deriva il segnale dallo stato corrente, posizione = `sign(signal)`, applica al rendimento del giorno `t+1`. Ritorna `{sharpe, max_drawdown, n_trades}`. Sharpe annualizzato `mean/std*sqrt(252)`; max drawdown da equity cumulata. **Nessun look-ahead, nessun tuning.**

Costanti: `STATES = ["Bear", "Sideways", "Bull"]` (indici 0,1,2).

### 2. Estensione HMM opzionale (`hmm_extension.py`)

Layer Hidden Markov che *inferisce* i regimi dai rendimenti grezzi senza etichettatura manuale.

- **`fit_hmm(returns, n_components=3, random_state=42)`** — import **lazy** di `hmmlearn` (se fallisce ritorna `(None, None)` → degrade pulito). `GaussianHMM(covariance_type="diag", n_iter=200)`, `.fit(X)` (Baum-Welch) + `.predict(X)` (Viterbi). Ordina gli stati per media dei rendimenti → Bear/Sideways/Bull.
- **Caveat della fonte**: Baum-Welch trova **massimi locali**; in produzione fittare con più `random_state` e tenere il miglior log-likelihood.
- **Graceful degrade**: `hmmlearn` può non compilare su Windows senza MS C++ Build Tools. In quel caso il layer HMM viene saltato e il modello osservabile funziona comunque (flag file `.hmm_available` = `true`/`false`).

### 3. Indicatore PineScript (TradingView)

Visualizzazione live on-chart dello stesso framework:

- Etichetta ogni barra Bull/Bear/Sideways da **log-return** sulla finestra (`math.log(close/close[lookback])`), default lookback 20 barre, soglie ±5% (configurabili e asimmetriche).
- Conta le transizioni in un array persistente `var` (idx `prev*3 + curr`), costruisce `P` per normalizzazione righe, e itera `M := M*P` ~50 volte per la **stazionaria** (qualsiasi riga della `M` convergente è la distribuzione long-run).
- Rende due tabelle d'angolo: **matrice di transizione** (diagonale evidenziata = persistence) e **long-run mix**, più ribbon di sfondo e label di cambio-regime *debounced* (`min_regime_hold` barre prima di marcare un flip, per evitare spam in zone choppy).
- Note tecniche della fonte: `matmul` 3×3 srotolato a mano (portabile su tutte le build v5; alternativa `matrix.*` commentata), tabelle create UNA volta con `var` (anti-flicker), heavy work gated su `barstate.islast`. Palette desaturata (Bull `#84BBA1`, Bear `#C57F86`, Sideways `#A4ABB7`).

### 4. Comando d'uso

Skill installata in `~/.claude/skills/markov-hedge-fund-method/`, ambiente pinnato Python 3.12 via `uv`. Esecuzione del modulo:

```
cd ~/.claude/skills/markov-hedge-fund-method
uv run python -m markov_hedge_fund_method.run --ticker SPY --years 10 --window 20
```

Flag: `--ticker` (default `SPY`), `--years` (default 10), `--window` (rolling-return in giorni di trading, default 20), `--threshold` (default 0.02), `--no-hmm` (salta l'HMM anche se presente). Dipendenze core: `yfinance`, `numpy`, `pandas`, `scikit-learn`; opzionale `hmmlearn`. Dati via yfinance (Yahoo Finance, free, no key). Output a ogni run: header ticker/date/righe, matrice 3×3 con diagonale di persistenza, distribuzione stazionaria, Sharpe walk-forward + max drawdown, ed eventuali rendimenti medi per regime HMM.

> **Nota di adattamento al repo (se mai si valutasse).** Questa skill è generica su ticker azionari/crypto via yfinance; il workspace lavora soprattutto su forex (EURUSD, XAUUSD, GBPUSD). La sorgente dati e i simboli andrebbero ripensati, e il rapporto con [`../../core/regime.py`](../../core/regime.py) chiarito (complementare, non sostitutivo — vedi [[principles]]). Resta comunque idea non committata: vedi [`../../DECISIONS.md`](../../DECISIONS.md).

## Collegamenti

- [[principles]] — teoria dei regimi Markov + macro timing (`03_regimi_macro/principles.md`).
- Classificatore deterministico già in repo: [`../../core/regime.py`](../../core/regime.py) (Wilder DMI/ADX/ATR), documentato in [`../../TRADING_PRINCIPLES.md`](../../TRADING_PRINCIPLES.md) §1.
- Caveat look-ahead da non ripetere: [`../../data/regime_timeline_gbpusd.csv`](../../data/regime_timeline_gbpusd.csv) e [`../../DECISIONS.md`](../../DECISIONS.md).
- Priorità di workspace (custom in fondo): [`../../DECISIONS.md`](../../DECISIONS.md).

## Fonti

- **"Markov regime skill for claude.txt"** — framework di Roan (@RohOnChain), confezionato come skill Claude Code (`markov-hedge-fund-method`) da Lewis Jackson. Parte implementativa: prompt one-shot d'installazione, modulo `regime.py` + `hmm_extension.py` + `run.py`, `pyproject.toml` (Python 3.12, uv), indicatore PineScript v5 per TradingView. I backtest sono storici, non forward-looking (disclaimer della fonte).
