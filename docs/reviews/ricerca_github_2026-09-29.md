---
tipo: ricerca
stato: quarantena
aggiornato: 2026-09-29
nota: "Stelle, push e licenze letti il 2026-09-29 (API GitHub / PyPI). Nessun codice importato: le integrazioni che toccano i 48 buchi di Quant Guild aspettano la decisione di Matteo (DECISIONS 2026-09-17)."
---
# Ricerca GitHub GH1-GH4 (29/09/2026)

Specifica confermata da Matteo il 2026-09-29. Eseguita da un subagente in sola lettura, regola di arresto
a blocchi da 5. Escluse per categoria: strategie con backtest dichiarati, agenti LLM, bot crypto, e le 12
repo gia' valutate il 14/06 ([catalogo](../../../memoria/trad/reference_github_repos_review.md)).

## GH1 — Librerie statistiche

| Repo | Cosa useremmo | Verdetto |
|---|---|---|
| [bashtage/arch](https://github.com/bashtage/arch) (1.579★, push 2026-09-27, v8.0.0) | `StationaryBootstrap`, `CircularBlockBootstrap`, `optimal_block_length`; **SPA di Hansen** (migliora il White RC), `StepM`, `MCS` | **Da integrare come riferimento** per un test di equivalenza con `core/quant_metrics.py` (che ha gia' a mano stationary bootstrap, White RC, BCa). Cautela: dipende da pandas 2.3 (noi 3.0.2), provarla in un venv. Il commit 68e2f90 corregge il BCa **con metriche a piu' statistiche**: il nostro `bca_bootstrap_ci` accetta solo una metrica scalare → **non affetto** (verificato 29/09) |
| [statsmodels](https://github.com/statsmodels/statsmodels) (gia' installato) | `runstest_1samp` sulla sequenza vinto/perso; `acorr_ljungbox` sugli R | costo zero; e' il **buco 29** di Quant Guild → decisione di Matteo |
| [scipy](https://github.com/scipy/scipy) (gia' installato) | `binomtest(b, B).proportion_ci()` = intervallo del p-value Monte Carlo | una riga; e' il **buco 37** → decisione di Matteo |
| [online-ml/river](https://github.com/online-ml/river) | `PageHinkley`, `ADWIN`: drift online | da catalogare: soglie euristiche, niente errori α/β controllati, **non e' un SPRT** |
| [gostevehoward/confseq](https://github.com/gostevehoward/confseq), [jakorostami/expectation](https://github.com/jakorostami/expectation) | confidence sequences / e-values: il metodo giusto per sorvegliare un binario live | concetto da catalogare; librerie non installabili su Windows py3.12 (confseq) o giovani e GPL (expectation) |

**Non trovato:** una libreria matura per **SPRT/CUSUM online** su win rate e payoff con errori controllati,
e una per il **bootstrap a cluster** dei trade. Le strade oneste: SPRT Bernoulli scritto a mano (~15 righe,
con test) oppure ricampionare gli indici dei cluster con `arch.IIDBootstrap`.

## GH2 — Copier Telegram → MT5

| Repo | Cosa prendere (concetti, non codice) | Verdetto |
|---|---|---|
| [MooreSi/forex-gold](https://github.com/MooreSi/forex-gold) (AGPL-3.0, creato 2026-09-24) | `tca.py` separa `entry_drift_pts` (**costo di arrivare tardi**: quotazione contro prezzo della decisione) da `broker_slippage_pts` (fill contro quotazione), e scrive `None`, non 0, se manca il tick; 9 timestamp di latenza da "postato" a "ordinato"; l'EA adatta lo stop a `SYMBOL_TRADE_STOPS_LEVEL` | **il miglior confronto**; e' esattamente il registro consigliato al socio ([review Gump](gump_live_rr_qualitativo_2026-09-29.md) §6). Codice non riusabile (AGPL) |
| [scotthez/trader-copier](https://github.com/scotthez/trader-copier) | regola `stale` sull'eta' del segnale, `_age` registrata a ogni decisione, replay dagli export HTML | da catalogare. ⚠️ Stesso difetto del nostro BE silenzioso (corretto in `032f762`): il 10016 finisce solo in un log |
| [rjgrl/copy-trader](https://github.com/rjgrl/copy-trader) | schema di latenza a 3 punti | da catalogare. ⚠️ tratta un orario senza fuso come UTC: il nostro errore di fuso |
| altri 7 copier | — | scartati: niente latenza, niente gestione degli stop rifiutati |

## GH3 — Dati gratuiti

| Fonte | Uso | Verdetto |
|---|---|---|
| [dukascopy-node](https://github.com/Leo4815162342/dukascopy-node) `instrument-meta-data.json` (snapshot 2026-07-13) | **censimento**: 1.499 strumenti Dukascopy con la data d'inizio dell'M1 (es. Copper 2012-03, Natural Gas 2012-09; alcune commodity a "2000-01-01", data sospetta) | da integrare come censimento per la riga G9; le date vanno verificate sui dati |
| [pysystemtrade](https://github.com/pst-group/pysystemtrade) `data/futures/adjusted_prices_csv` | **252 futures continui aggiustati**, giornalieri, molti dagli anni '70, **fermi al 2024-03-28**; licenza dei dati non chiara (solo ricerca) | da catalogare: basta per **contare gratis** gli strumenti indipendenti ad alta volatilita' (G9) prima di comprare. Contiene duplicati mini/micro dello stesso sottostante |
| CFTC COT + [cot_reports](https://github.com/NDelventhal/cot_reports) | posizionamento settimanale | da catalogare (lib ferma al 2023; i file CFTC si scaricano direttamente) |
| VIX: [CBOE VIX_History.csv](https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv) (dal 1990) · FRED `VIXCLS` | G4 | da integrare quando serve: download diretto |
| Dollaro: FRED `DTWEXBGS` (dal 2006), `DTWEXM` (1973-2019, sospesa) | contesto intermarket | idem |
| yfinance `=F` | solo controllo incrociato (front-month non aggiustato) | da catalogare |
| Stooq | CSV dietro una sfida JavaScript: non si scarica da script | scartato |

## GH4 — Audit di track record dei canali

**Nessuno misura pubblicamente il ritardo di posting** (prezzo al momento del post contro l'entrata
dichiarata). Il piu' vicino: lo schema di cattura di
[Signal-Backtesting-Ai-with-Telegram](https://github.com/hallohallo2010-cmd/Signal-Backtesting-Ai-with-Telegram)
(una modifica crea una riga nuova con `edited_at`, una cancellazione e' timbrata) — utile per D3 della
pre-registrazione Gump; il suo backtest pero' usa **GC=F futures** via yfinance (il difetto futures/spot
gia' visto su VELTRIX). La letteratura sul social trading misura i rendimenti di chi segue, non il ritardo.

## Le tre cose di maggior valore

1. **arch** come riferimento per verificare le nostre funzioni scritte a mano, e lo **SPA di Hansen**.
2. La **scomposizione dello slippage** di forex-gold (`entry_drift` vs `broker_slippage`, `None` se manca la
   misura): e' il registro che serve al copier del socio per rispondere alla domanda sul rapporto live.
3. Il **censimento gratuito** degli strumenti (dukascopy-node + pysystemtrade): permette di contare gli
   strumenti indipendenti ad alta volatilita' **prima** di spendere per la riga G9.
