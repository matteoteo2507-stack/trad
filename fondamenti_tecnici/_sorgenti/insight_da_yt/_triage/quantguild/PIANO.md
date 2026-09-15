# Distillamento Quant Guild (Roman Paolucci) — piano e punto di ripresa

> Avviato il **2026-09-15**, fermato prima della lettura per ripartire in una sessione nuova (il
> contesto era lungo). **Chi riprende il lavoro parte da qui.** Decisione di origine:
> [`DECISIONS.md`](../../../../../DECISIONS.md), voce 2026-09-15, *Decisione 3*.
>
> **Obiettivo dell'utente**: essere sicuri di avere tutti gli strumenti matematici necessari prima dei
> prossimi lavori, anche perché la distillazione di Chart Fanatics ha lasciato diverse porte aperte.
> **A distillazione finita va avvisato l'utente** (richiesta esplicita).

---

## Principio vincolante: cattura ampia

Non si cerca solo ciò che serve a quello che abbiamo: sarebbe superficiale, perché non sappiamo quali
strumenti serviranno. **Ogni strumento si cataloga con le sue condizioni**, anche senza un uso
immediato. La rilevanza **classifica, non esclude**. Resta valido il filtro sulle **statistiche
dichiarate** (si raccolgono le regole, si scartano i claim numerici non verificabili): quello riguarda
l'affidabilità di una fonte, non l'utilità di uno strumento.

---

## Perimetro

- Canale: <https://www.youtube.com/@QuantGuild> — **248 video + 2 live**, circa 109 ore.
  Elenco completo: [`analysis/intake/lists/quantguild_canale.txt`](../../../../../analysis/intake/lists/quantguild_canale.txt)
  (`num` = posizione nel tab Videos, 1 = più recente).

### Già distillati (8)

Gli appunti in `_sorgenti/` sono riassunti **senza ID video**: l'attribuzione è stata ricostruita per
contenuto il 2026-09-15.

| # | video | dove sono gli appunti | distillato in |
|---|---|---|---|
| 14 | Risk is always mispriced | `Appunti misti 2026-08-04.txt` righe 129-250 | `04_quant_metodologia` §9 (pre-mortem) |
| 29 | The Ultimate Guide to Quant Portfolio Management | `quantportfolio managernotes.txt` righe 1-249 | `05_portfolio_rischio` (PCA, CAPM, beta) |
| 31 | Modeling Tail Risk: A Quantitative Survival Guide | `Nuove nozioni teoriche 2026-07-16.txt` righe 223-330 | `05_portfolio_rischio` (tail risk) |
| 32 | Compound Annual Growth Rate (CAGR) for Quant Finance | `Nuove nozioni teoriche 2026-07-16.txt` righe 112-222 | `04_quant_metodologia` §8 |
| 41 | Volatility Risk Premium Explained | `NOZIONI AGGIUNTIVE.txt` righe 392-505 | `05_portfolio_rischio` (VRP) |
| 43 | No. You don't need to backtest a trading strategy. | `NOZIONI AGGIUNTIVE.txt` righe 1-175 | `05_portfolio_rischio` (orthogonal streams), mappa dei modelli |
| 44 | How to Derive Volatility Drag | `NOZIONI AGGIUNTIVE.txt` righe 181-391 | `05_portfolio_rischio` (volatility drag) |
| 76 | 3 Backtesting Pitfalls That Ruin Your Trading Strategy | `Quant backtest notes.txt` | `04_quant_metodologia` §1-4 |

⚠️ **Da attribuire**: il blocco *"Comprehensive Guide to Investing"* in
`Nuove nozioni teoriche 2026-07-16.txt` (righe 331-588) viene da uno fra **#24, #131, #162**. Le tre
trascrizioni sono in coda al gruppo 1 (blocco H): confrontarle e segnare quale.

Non sono Quant Guild, pur stando negli stessi file: il market update sui semiconduttori, la parte
"Argo process / gamma exposure" di `quantportfolio managernotes.txt`, lost decades, MMT, outlook
economico del 4/08.

### Gruppi

| gruppo | video | contenuto | cosa si fa |
|---|---|---|---|
| **1 — nucleo** | **81** | statistica e inferenza, edge e fortuna/abilità, validità del backtest, sizing e rovina, serie storiche e regimi, portafoglio, Monte Carlo, struttura di mercato | **si distilla**. Lista con blocchi e ordine: [`quantguild_gruppo1.txt`](../../../../../analysis/intake/lists/quantguild_gruppo1.txt) |
| **2 — calcolo stocastico e derivati** | ~45 | Itô, SDE, moti browniani (aritmetico, geometrico, frazionario), Black-Scholes e derivazioni, Bachelier, Heston/FFT, rough volatility e Markovian lifting, Volterra, Karhunen-Loève, variance swap, greche, superficie di volatilità, pricing risk-neutral, differenze finite, esotiche, deep hedging, path signatures, covered call, cash secured put | **scaricare, NON distillare ora** (decisione utente 2026-09-15) |
| **3 — programmazione** | ~40 | bot Interactive Brokers, dashboard, basi Python e C++, web app, NLP, reti neurali, sentiment ed emoji, sistemi in Java | leggere **per strumenti** (cattura ampia), non per il codice |
| **esclusi** | ~70 | carriera, vita personale, reaction, annunci | no. Eccezione da valutare con una lettura rapida: **#10** (TJR e il backtesting) e **#12** (Craig Percoco e la statistica), reaction con contenuto statistico |
| live | 2 | Q&A mentre costruisce un gioco; J.A.R.V.I.S. per portfolio management | esclusi |

La classificazione dei gruppi 2, 3 ed esclusi è fatta **per titolo**: chi la applica verifichi i casi
dubbi nell'elenco completo.

### Blocchi del gruppo 1, in ordine di lettura

| blocco | tema | video |
|---|---|---|
| **A** | statistica e inferenza (le fondamenta dei gate G1/G2) | 14 |
| **B** | edge, fortuna vs abilità, validità del backtest (il nostro protocollo) | 24 |
| **C** | sizing, rovina, ergodicità, dipendenza dal percorso | 11 |
| **D** | serie storiche, regimi, filtri, processi di punto | 11 |
| **E** | costruzione di portafoglio | 8 |
| **F** | simulazione Monte Carlo | 4 |
| **G** | struttura di mercato e cornice | 6 |
| **H** | da attribuire (vedi sopra) | 3 |

---

## Metodo

1. Ogni trascrizione **letta per intero**, un video alla volta, dalla **copia di lettura** in
   `_raw/_lettura/` — mai dalla grezza (vedi *Tecnica*).
2. Un file per blocco: `_triage/quantguild/blocco-<X>.md`, sul modello dei blocchi di Chart Fanatics
   ([`../blocco-C1.md`](../blocco-C1.md)): intestazione del blocco, poi una sezione per video con ID,
   durata e parole.
3. **La sezione di un video è un catalogo di strumenti**, non un verdetto su una strategia. Per ogni
   strumento:
   - definizione e formula;
   - domanda a cui risponde;
   - assunzioni;
   - limiti e modi in cui si rompe;
   - fonte (video, e minuto quando aiuta);
   - **stato nel repo**: implementato in `core/` · documentato in `fondamenti_tecnici/` · assente;
   - **rilevanza**: in uso · applicabile ora · futuro · reference;
   - conflitti con altre fonti, da registrare nella mappa dei modelli (condizioni di validità, nessun
     vincitore).
4. Alla fine: `_triage/quantguild/SINTESI.md` con il **catalogo consolidato per dominio**, lo stato
   del repo e la destinazione di ogni voce (`04_quant_metodologia`, `05_portfolio_rischio`,
   `03_regimi_macro` o una sezione nuova). Poi: aggiornare [`_INTAKE.md`](../../../../_INTAKE.md),
   voce in `DECISIONS.md`, memoria, commit e **avviso all'utente**.

---

## Inventario del repo al 2026-09-15 (per la colonna "stato")

- **`core/quant_metrics.py`**: `sharpe_ratio`, `probabilistic_sharpe_ratio`, `deflated_sharpe_ratio`,
  `pbo_cscv`, `cpcv_splits`, `walk_forward`, `mc_permutation_test`, `sortino_ratio`, `max_drawdown`,
  `calmar_ratio`, `ulcer_index`, `tail_metrics`, `omega_ratio`, `tail_ratio`, `benchmark_metrics`
  (alpha/beta), `whites_reality_check`, `bca_bootstrap_ci`, bootstrap stazionario.
  Altri moduli: `core/regime.py`, `core/risk_gate.py`.
- **`04_quant_metodologia/principles.md`** §1-9: look-ahead, overfitting/p-hacking, survivorship,
  walk-forward, costi, librerie di backtest, finestre sovrapposte, CAGR e Rule of 72, pre-mortem.
- **`05_portfolio_rischio/principles.md`**: alpha ortogonale, tassonomia del rischio, diversificazione,
  non-stazionarietà delle correlazioni, volatility drag, orthogonal return streams, VRP, tail risk,
  PCA, CAPM ed estensioni, beta per settore, costruzione goal-driven.
- **`03_regimi_macro/principles.md`**: catena di Markov a 3 stati, framework Fed, market timing a 5
  metriche, indicatori macro, canali di trasmissione.
- **Protocollo**: `docs/STRATEGY_LIFECYCLE.md`, `docs/QUANT_REVIEW_PROTOCOL.md`,
  `.claude/agents/quant-gatekeeper.md`.

---

## Tecnica: scaricamento e ripresa

- Download del gruppo 1 partito il 2026-09-15: **15/81 alle 22:15**. Potrebbe essersi fermato con la
  chiusura della sessione: **lo stato è salvato video per video** in `analysis/intake/_state.json`,
  chiave **`"Roman Paolucci - Videos"`**.
- **Prima di rilanciare**, verificare che non ne giri già uno: se l'ultimo `fetched` sotto quella
  chiave è di pochi minuti fa, è ancora attivo. Due download insieme raddoppiano il rischio di blocco
  IP (YouTube blocca dopo ~15 richieste ravvicinate).
- **Ripresa del gruppo 1**:
  `python analysis/intake/yt_fetch_list.py analysis/intake/lists/quantguild_gruppo1.txt`
- **Copie di lettura dei video già scaricati** (i primi 15 non le hanno):
  `python analysis/intake/yt_fetch_list.py analysis/intake/lists/quantguild_gruppo1.txt --solo-lettura`
- **Resto del canale** (gruppo 2, 3, esclusi: si scarica tutto, è testo): 
  `python analysis/intake/yt_fetch.py https://www.youtube.com/@QuantGuild/videos` — salta i video già
  presi perché usa la stessa chiave. Poi `--solo-lettura` con `quantguild_canale.txt`.
- ⚠️ **Non lanciare `yt_fetch.py` su un singolo URL video**: salva lo stato sotto il nome dell'uploader
  ("Roman Paolucci") e il giro sul canale riscaricherebbe tutto.

---

## Stato

Aggiornato automaticamente alla chiusura della sessione del 2026-09-15 (ultimo download: `2026-09-15T20:21:27+00:00` UTC). Rigenerare i conteggi leggendo `_state.json`.

| blocco | scaricati | letti | file di triage |
|---|---|---|---|
| A | 14/14 | 0 | — |
| B | 5/24 | 0 | — |
| C | 0/11 | 0 | — |
| D | 0/11 | 0 | — |
| E | 0/8 | 0 | — |
| F | 0/4 | 0 | — |
| G | 0/6 | 0 | — |
| H | 0/3 | 0 | — |
| altri video del canale | 3 scaricati fuori dal gruppo 1 | — | — |
| SINTESI | — | — | — |
