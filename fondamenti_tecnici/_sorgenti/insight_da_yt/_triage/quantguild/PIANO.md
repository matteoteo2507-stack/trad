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

### Già distillati (9)

Gli appunti in `_sorgenti/` sono riassunti **senza ID video**: l'attribuzione è stata ricostruita per
contenuto il 2026-09-15. **#27 aggiunto in lettura** (blocco B, voce B5): i suoi appunti erano stati
scambiati per la coda del blocco "Comprehensive Guide to Investing".

| # | video | dove sono gli appunti | distillato in |
|---|---|---|---|
| 14 | Risk is always mispriced | `Appunti misti 2026-08-04.txt` righe 129-250 | `04_quant_metodologia` §9 (pre-mortem) |
| 27 | Math to Increase your Sharpe Ratios | `Nuove nozioni teoriche 2026-07-16.txt` righe 495-589 | `05_portfolio_rischio` (varianza a tre termini, indipendenza fisica) |
| 29 | The Ultimate Guide to Quant Portfolio Management | `quantportfolio managernotes.txt` righe 1-249 **+ `Nuove nozioni teoriche 2026-07-16.txt` righe 331-491** | `05_portfolio_rischio` (PCA, CAPM, beta), `08_asset_allocation_passiva` (EMH, verita' dure, metriche) |
| 31 | Modeling Tail Risk: A Quantitative Survival Guide | `Nuove nozioni teoriche 2026-07-16.txt` righe 223-330 | `05_portfolio_rischio` (tail risk) |
| 32 | Compound Annual Growth Rate (CAGR) for Quant Finance | `Nuove nozioni teoriche 2026-07-16.txt` righe 112-222 | `04_quant_metodologia` §8 |
| 41 | Volatility Risk Premium Explained | `NOZIONI AGGIUNTIVE.txt` righe 392-505 | `05_portfolio_rischio` (VRP) |
| 43 | No. You don't need to backtest a trading strategy. | `NOZIONI AGGIUNTIVE.txt` righe 1-175 | `05_portfolio_rischio` (orthogonal streams), mappa dei modelli |
| 44 | How to Derive Volatility Drag | `NOZIONI AGGIUNTIVE.txt` righe 181-391 | `05_portfolio_rischio` (volatility drag) |
| 76 | 3 Backtesting Pitfalls That Ruin Your Trading Strategy | `Quant backtest notes.txt` | `04_quant_metodologia` §1-4 |

✅ **Attribuito il 2026-09-17** (vedi [`blocco-H.md`](blocco-H.md)): il blocco *"Comprehensive Guide to Investing"* in
`Nuove nozioni teoriche 2026-07-16.txt` (righe **331-491**; le righe 495-589 sono #27) viene da **#29
`LX4Ugaxx9n0` - The Ultimate Guide to Quant Portfolio Management**, cioe' dallo **stesso video** gia' attribuito per
`quantportfolio managernotes.txt` righe 1-249: un solo video, **due serie di appunti in due file diversi**, che
coprono meta' video ciascuna. L'ipotesi "uno fra #24, #131, #162" era **sbagliata**: tutti e tre letti per intero,
zero marcatori. Il conteggio dei gia' distillati resta **9**.
Marcatori verificati su #29: *"15 years of academic and industrial experience"*, quattro *hard truths*, tabella
securities/non-securities, startup IA contro Microsoft, EMH nelle tre forme, controfattuali, orologi e arte come
mercati ortogonali.

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

**DISTILLAMENTO CHIUSO il 2026-09-17.** Gruppo 1 completo: 81/81 scaricati e **81/81 letti per intero**, piu' 2 video di
controllo (#29, #35) per l'attribuzione. Uscita finale: [`SINTESI.md`](SINTESI.md). Voce in `DECISIONS.md` (2026-09-17),
riga in `fondamenti_tecnici/_INTAKE.md`, memoria aggiornata a CHIUSO. **Non riaprire il canale**: il gruppo 2 resta solo
scaricato, il gruppo 3 escluso.

| blocco | scaricati | letti | file di triage |
|---|---|---|---|
| A | 14/14 | **14** | [`blocco-A.md`](blocco-A.md) ✅ |
| B | 24/24 | **24** | [`blocco-B.md`](blocco-B.md) ✅ lettura completa; buchi 5–13, mappa con 5 conflitti; righe di sintesi B23–B24 in aggiunta |
| C | 11/11 | **11** | [`blocco-C.md`](blocco-C.md) ✅ lettura completa; buchi 14–18; da chiudere righe di sintesi C10–C11 e sezione mappa; **C4, C8, C9 classificati male per titolo** (sviluppo personale / motivazionale); C7 in conflitto con il pilastro PAC (mappato, non riaperto) |
| D | 11/11 | **11** | [`blocco-D.md`](blocco-D.md) OK lettura completa; buchi 20-29; sintesi e buchi chiusi |
| E | 8/8 | **8** | [`blocco-E.md`](blocco-E.md) OK lettura completa; buchi 30-35; 2 conflitti in mappa |
| F | 4/4 | **4** | [`blocco-F.md`](blocco-F.md) OK lettura completa; buchi 36-39; nessun conflitto (blocco meno denso: il valore e' l'errore standard del MC, non le tecniche) |
| G | 6/6 | **6** | [`blocco-G.md`](blocco-G.md) OK lettura completa; buchi 40-45; 3 conflitti in mappa (analisi tecnica non confutabile; alpha "non serve significativo"; gamba di copertura, seconda occorrenza) |
| H | 3/3 (+2 di controllo) | **5** | [`blocco-H.md`](blocco-H.md) OK **attribuzione RISOLTA: e' #29 `LX4Ugaxx9n0`**, non uno dei tre candidati. Buchi 46-48 |
| altri video del canale | 3 scaricati fuori dal gruppo 1 | — | — |
| SINTESI | — | — | [`SINTESI.md`](SINTESI.md) **CHIUSA**: catalogo per 9 domini, 48 buchi in 4 fasce di priorita', 14 conflitti |
