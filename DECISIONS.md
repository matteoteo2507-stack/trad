# DECISIONS — Decisioni già prese (decision log)

> **Perché questo file esiste.** Per non riallucinare scelte già chiuse né ricostruire
> analisi già fatte. Prima di proporre "costruiamo X" o "riattiviamo Y", **controlla qui**.
> Le decisioni si cambiano **con dati nuovi**, non con sensazioni — e quando cambiano, si
> aggiorna questo file con una nuova voce (non si riscrive la storia).
>
> Formato: ogni voce = *data · decisione · razionale · link*. Ordine: dal più recente.
> Questo file rispecchia nel repo le decisioni che vivono anche nella memoria di lavoro
> (`~/.claude/projects/.../memory/`), così sono visibili sfogliando il workspace e su GitHub.

---

## 2026-07-08 — TSMOM multi-asset (primo edge del pivot): NO-GO pulito. Kill-switch → mean-reversion vol.

Primo edge dopo la chiusura livelli. Test **pre-registrato** ([docs/TSMOM_PREREGISTRATION.md](docs/TSMOM_PREREGISTRATION.md)),
motore di portafoglio [strategies/tsmom/backtest.py](strategies/tsmom/backtest.py) sulle **serie di
rendimenti** (non le sintesi MT5 del tentativo 2026-05), 16 asset D1 2003-2026, spec canonica MOP
(sign 252g, vol-target 60g, media portafoglio, mensile, costi, look-ahead-safe). Verdetto completo:
[docs/reviews/tsmom-portfolio-2026-07-08.md](docs/reviews/tsmom-portfolio-2026-07-08.md).

**Esito: NO-GO.** Primario (252,mensile) Sharpe **+0.21**, ma **BCa CI [−0.18,+0.59]** (lower≤0),
**DSR 0.33 n.s.**, MC-perm **p=0.51**, **PBO 0.58**, White's RC **p=0.53**, walk-forward OOS +0.12
(degrado 51%). 5 test indipendenti concordi: **edge non distinguibile dal caso**. Overlay prop: maxDD
−40% → non avviabile.

**Novità vs 2026-05-29:** il multi-asset ha **risolto i difetti** del vecchio NO-GO (mono-asset/mono-anno):
breadth 12/16, top asset 16%, 13/23 anni positivi. Il problema non è più il campione — l'edge è
**semplicemente troppo debole** (~0.2) in questo universo USD-pesante / epoca decaduta post-2009
(atteso a priori: Baltas-Kosowski, SG Trend 0.3-0.5). Nessun curve-fit: verdetto per BCa+DSR+PBO+MC+WRC.

**Ipotesi (NON risultato):** trend concentrato negli asset che trendano (XAU +1.44, US100 +1.19, US500
+1.13, BTC +0.63) vs cross FX negativi (USDCHF −0.27, EURGBP.r −0.69). Un TSMOM "trending-universe"
*potrebbe* reggere, ma è **post-hoc** → va pre-registrato come nuovo trial e validato OOS, non rivendicato.

**Decisione:** kill-switch pre-registrato → **archiviare TSMOM canonico**, passare al prossimo edge del
backlog ortogonale (**mean-reversion vol non-level**), salvo scelta utente di pre-registrare prima la
variante trending-universe. La **macchina di validazione** (`core/quant_metrics` + backtester portafoglio)
è l'asset riusabile per gli edge successivi.

---

## 2026-07-07 (v3) — Livelli HTF fatti bene: confermato NULL. Libro CHIUSO davvero (384 trial).

Dopo l'audit delle tolleranze (la `0.10·ATR` era una costante ereditata/tarata su XAU-H1, applicata a
sproposito anche alle zone; i materiali dicono che i livelli forti stanno sugli HTF, che OB/S-D sono
**zone** con larghezza intrinseca e regola del **50% MT**, e che la struttura è **ubiqua**), abbiamo
rifatto il test **come si deve** (addendum pre-registrato). Motore `analysis/level_research/htf.py`:
- detection/misura su **H4, D1, W1** (H4 resample da H1, W1 da D1); **tolleranza scalata all'ATR del TF**
  (0.20 linea; le zone usano la **larghezza vera** + break = body-close oltre il 50% MT);
- **random distance-matched E structure-free** (rifiutato se cade su qualsiasi struttura vera — il punto
  che chiedeva l'utente); **freshness** naked/tested stratificata. FVG e Monthly esclusi (decisione utente).

**Esito (5 concetti × 3 TF × 16 asset = 240 trial): 0 sopravvissuti.** Pooled reale ≤ random su ogni TF
(spesso **negativo**: swing W1 CI[−2.4,−0.7], D1[−2.0,−1.3], H4[−1.5,−0.8]; prev H/L, round, EQH/EQL
idem; OB il "meno peggio" ma CI che tocca 0, breadth 2/16). **7 celle "battono" su 240, attese ~12 per
caso** → sotto il rumore. **Freshness piatta** (naked ≈ tested, entrambi ≤ random) → smentisce anche la
tesi "fresh≫tested" dei materiali. Con il random *structure-free* i livelli reagiscono spesso **meno del
vuoto** → coerente con "i livelli sono dove il prezzo rompe/consuma liquidità, non dove rimbalza".

**Robustezza tolleranza:** il null tiene a **0.10·ATR** (v1, H1) **e** a **0.20·ATR** (v3, H4/D1/W1) →
non è un artefatto della soglia. **Totale ricerca livelli: v1(96)+v2(48)+v3(240) = 384 trial
pre-registrati, 0 edge.** "Il prezzo reagisce ai livelli come zona" è **falsificato a fondo, su ogni
timeframe e con la metodologia dei nostri stessi materiali.** Libro chiuso senza rimpianti. **Pivot** a
strategie **non** level-based (razionale economico/peer-reviewed) — da decidere con l'utente.

---

## 2026-07-07 — Ricerca livelli v2 (volume): 0/3 concetti. Libro CHIUSO (144 trial, 0 edge).

Testata l'ultima famiglia rimasta (concetti **volume**, tick-proxy), stesso protocollo pre-registrato
([addendum](docs/LEVEL_RESEARCH_PREREGISTRATION.md)): POC/VAH/VAL, VWAP, anchored VWAP × 16 asset.
**Nessuno batte il random distance-matched** — breadth 0/16 ciascuno, pooled reale≈random (POC 30.1
vs 30.5 CI[−0.8,+0.1]; VWAP 30.6 vs 30.5 CI[−0.7,+1.0]; AVWAP 29.7 vs 29.7 CI[−0.5,+0.4]). **0 celle
"battono" su 48** (attese per caso ~2.4). Caveat dichiarato: volume = tick-proxy su tutti gli asset.

**Conclusione (regola pre-registrata).** v1 (6 OHLC) + v2 (3 volume) = **9 concetti × 16 asset = 144
trial, 0 sopravvissuti.** La premessa "il prezzo reagisce ai livelli come zona" è **falsificata in modo
ampio e a prova di p-hacking**. **Libro livelli-come-zona-di-reazione CHIUSO. Pivot.** Unico angolo mai
testato (e volutamente non aperto: alto rischio DoF/overfit) = livelli come *filtro condizionale* dentro
un contesto direzionale/sessione — NON è "reazione al livello", è un'altra ipotesi. Motore
`analysis/level_research/` resta riusabile per qualsiasi nuovo concetto (basta dichiararlo nuovo trial).

---

## 2026-07-06 — Ricerca livelli v1: NESSUN concetto batte il random (0/6). Pivot.

**Contesto.** Dopo il NO-GO del conf=2 (sotto), abbiamo rifondato la domanda: *quali criteri trovano
livelli dove il mercato reagisce davvero?* Test **pre-registrato**
([docs/LEVEL_RESEARCH_PREREGISTRATION.md](docs/LEVEL_RESEARCH_PREREGISTRATION.md)), motore walk-forward
look-ahead-safe ([analysis/level_research/](analysis/level_research/)), **6 concetti OHLC-puri** ×
**16 asset** (FX/metalli/crypto/indici, feed demo4 validato), metrica = **%REACTION|touch reale vs
random distance-matched**, CI block-bootstrap sui giorni, breadth, DSR sui 96 trial, holdout 70/30.

**Esito (TRAIN, breadth = asset che battono / testati):**
| concetto | breadth | pooled %REACT reale vs random | CI95 diff | esito |
|---|---|---|---|---|
| swing S/R | 1/16 | 29.0% vs 29.8% | [−1.1, −0.6] | peggio del random |
| PDH/PDL | 0/16 | 28.8% vs 30.5% | [−2.4, −1.2] | **peggio** (rotti più del caso) |
| order block | 3/16 | 30.0% vs 29.6% | [+0.0, +0.9] | pool>0 ma breadth<50%, ~0.4pt |
| FVG | 0/16 | 29.6% vs 29.8% | [−0.5, +0.2] | nullo |
| round number | 0/16 | 29.4% vs 30.1% | [−1.1, −0.3] | peggio del random |
| EQH/EQL | 0/16 | ~nullo | — | nullo |

**DSR/molteplicità:** 4 celle "battono" su 96; falsi attesi per caso a CI95 = 0.05·96 ≈ **4.8** →
osservati ≤ attesi = **rumore**. La %REACTION è ~29-30% ovunque, **identica** tra livello "vero" e
punto arbitrario alla stessa distanza.

**Decisione (regola pre-registrata attivata).** Nessun concetto sopravvive → a questa risoluzione
**i livelli non sono zone di reazione**: la posizione "strutturale" non aggiunge nulla oltre la
distanza. Generalizza il conf=2 su 16 asset × 6 concetti. **Non forziamo edge dove non c'è → Pivot.**

**Scope onesto (NON falsificato):** (a) concetti **volume** (POC/VWAP/TPO), rimandati a v2 (proxy su
FX); (b) livelli come **filtro condizionale** in un contesto direzionale/sessione (non zona di reazione
unconditional); (c) altri timeframe/orizzonti. Unici spiragli prima di chiudere il libro "livelli".

---

## 2026-07-05 — Level Analyzer conf=2 (fade): **NO-GO forward** (i livelli ≠ zone di reazione)

**Decisione.** Il fade sistematico dei livelli conf=2 (XAU+BTC) è **NO-GO**. Analisi con 3 agenti
Fable indipendenti (criteri di reazione dai materiali · audit fallacie · misura reazione-vs-random)
su 101 record forward (18-06 → 05-07-2026, 81 riconciliati).

**La prova decisiva = misura DIRETTA dei livelli** (indipendente dalla meccanica del trade): i
livelli conf=2 **non reagiscono più di livelli casuali** alla stessa distanza (BTC 18.5% vs 22.5%,
CI include 0; con baseline a 0.3–6 ATR reagiscono *meno* del caso); **~63% dei touch finisce in
break**. La classificazione livello→esito è forte (REACTION→67% win, BREAK→13% win): i livelli sono
in maggioranza cattivi. Coerente col trade E[R]=−0.37R (CI esclude 0).

**Il trade da solo NON basta a concludere (audit).** Il forward NON testava la strategia validata:
24/7 vs sessione 06–21 (61/101 fuori finestra), livelli "appena nati" ricalcolati sulla barra in
formazione (repaint → fade del momentum), XAU su **GC=F futures** (spec: spot), exact-touch vs fill
tollerante. Inoltre "conf=2" NON era 2 nature diverse (47/101 = stessa natura doppia; `cluster_confluence`
conta i membri) e il backtest "+0.15R" era esso stesso debole (CI iid su trade clusterizzati,
selezione post-hoc del bucket). → il −0.37 del trade è confondato, MA la misura diretta (C)
falsifica il **concetto** alla radice: non serve "fixare il protocollo e ri-fadare".

**Razionale.** N-esimo negativo custom (cfr. London Breakout, TSMOM, Stock Selector, sweep+reclaim,
regime gate). Il workflow ha fatto il suo lavoro: refutato strategia **e** la sua validazione debole,
prima dei soldi veri. Il Level Analyzer va **sospeso** (stop `run` sul server); il workflow
(capture→reconcile→gate + agenti) è l'asset riusabile che resta.

**Reverse/breakout anch'esso REFUTATO (check `breakout_check.py`, 13y/6y):** tradare la direzione
OPPOSTA alle zone conf=2 è **catastrofico** (XAU −0.78 / BTC −0.70 / EUR −0.77, win 11-16%), molto
PEGGIO del random → nessun edge inverso, le zone non sono neanche livelli di breakout. Chiude
"tradare questi livelli in qualunque direzione". NB tensione: nel **backtest** il fade batte il
random (+0.19 vs −0.16) ma NON regge **forward** (−0.37) → edge in-sample fragile/overfit + protocollo
forward rotto. C'è debole struttura mean-reversion in-sample (il reverse-catastrofico lo conferma),
troppo fragile per la meccanica grezza e diluita dal blob conf=2.

**Segnali deboli conservati (non azionabili, n piccolo):** natura **OB** sopra media (33% reaction,
n=21) e regime "transizione" (n=13); **FVG** (5% reaction, 90% break) e regime "range" (0/18) = rumore.
XAU inconcludente (futures + n=29). **Bug noti:** conteggio no_fill nel gate (fill reale ~83%), fill/exit
idealizzati (−0.37 = upper bound).

→ Analisi: [`analysis/trading-bot-eval/level_reaction_analysis.py`](analysis/trading-bot-eval/level_reaction_analysis.py) ·
spec [`LEVEL_ANALYZER_SPEC.md`](analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md) ·
workflow [`docs/TRADING_WORKFLOW_DESIGN.md`](docs/TRADING_WORKFLOW_DESIGN.md)

---

## 2026-06-14 — OctoBot (traccia crypto): **DORMIENTE**

**Decisione.** La traccia **OctoBot / crypto-automation** è messa in **stand-by (dormiente)**, non
archiviata: rispolverabile in futuro se si riapre esplicitamente un fronte crypto. **Emenda la priorità
del 2026-05-30** (sotto), dove OctoBot era #1.

**Razionale.** Dopo il pivot di giugno 2026 il lavoro reale è su **forex/XAUUSD via MT5** (signal copier
mentori, prop), **quant** (quant-review, metriche, backtest) e **investing passivo**. OctoBot è
**crypto-only** (esecuzione via ccxt, nessun MT5/forex) → non serve lo stack attuale. La priorità "#1
OctoBot" era anteriore a questo pivot. La review della repo forkata conferma: i pezzi che sembravano
combaciare (TelegramSignalEvaluator, modulo `signals/`) sono esempi banali / plumbing interno crypto, meno
adatti del nostro `signal_copier`.

**Condizione per riaprire.** Quando (a) si decide consapevolmente di aprire un fronte crypto-automation
**E** (b) c'è slack-time dopo milestone-1 forex. Allora OctoBot torna candidato come executor crypto.

→ Review: `github_repo_reviews/OctoBot.md` (memoria di lavoro) · Stage storico: [ROADMAP.md Stage 6](ROADMAP.md)

---

## 2026-06-14 — Terzo secchio (sleeve trend/managed-futures): **RIMANDATO a fase 2-3**

**Decisione.** Il pilastro investing resta a **due secchi** (buffer + All-World PAC) in fase di
accumulo. Lo *sleeve* trend-following / managed-futures — idea emersa dal materiale
volatility-drag / orthogonal-streams (QuantGuild) — **non si aggiunge ora**: è uno strumento di
**riduzione del drawdown**, quindi appartiene alla **fase 2-3** del glide-path (preservazione),
dove il piano già prevede una quota "difensiva". Quando ci si arriverà, va valutato come
**diversificatore del secchio difensivo accanto/al posto dei bond** (che nel 2022 hanno fallito la
diversificazione, correlazione salita coi tassi), **mai con leva**, **mai come "batti il mercato"**.

**Razionale.** (1) **Phase mismatch decisivo**: in accumulo il drawdown è un ALLEATO (il DCA compra
a sconto) → pagare carry negativo / CAGR inferiore per assicurarsi contro un non-rischio è sbagliato
ora (guardrail quant §3 del piano). (2) Il **principio** è solido (stream ortogonale R²≈0 → meno
drawdown → meno volatility drag → meglio geometrico; il trend-following fu orthogonale/positivo nel
2022 quando i bond fallirono), ma la **ricetta** commerciale (leva + hedge-leg "batte SPY") è un
singolo backtest in-sample non robusto. (3) **Praticità retail-IT**: gli strumenti canonici
(DBMF/KMLM) sono **US-domiciled** → estate tax + non-armonizzati + fisco complesso; opzioni UCITS
sottili, da verificare al momento. (4) La **base non è ancora costruita**: il piano a 2 secchi non
ha ancora i numeri (categoria A) → non aggiungere il layer più avanzato prima delle fondamenta.

**Condizione per riaprire.** Quando (a) il pilastro passivo è numericamente vivo **E** (b) si entra
in fase 2-3 del glide-path **E** (c) esiste un veicolo UCITS trend/managed-futures verificato (TER,
AUM, domicilio) → valutarlo come quota **modesta** del difensivo, misurandone il contributo reale a
drawdown/correlazione, **non** con leva.

**Corroborazione esterna (2026-06-14, review GitHub).** Il `ManagedFuturesAnalyzer` di FinceptTerminal
(impostazione standard CFA) classifica i managed futures come *"The Flawed"*: i benefici di crisis-alpha
**non giustificano** i costi (2&20), cita capacity constraints, e suggerisce **replica via ETF
trend-following low-cost o di saltare del tutto**. Converge con la nostra decisione (fee drag vs
crisis-alpha) e con la cautela sul singolo backtest levered-hedge. Da rileggere quando si riapre lo
sleeve in fase 2-3 → `github_repo_reviews/FinceptTerminal.md` (memoria di lavoro).

→ [docs/INVESTING_PILLAR_PLAN.md §3b](docs/INVESTING_PILLAR_PLAN.md) ·
teoria [fondamenti_tecnici/05_portfolio_rischio](fondamenti_tecnici/05_portfolio_rischio/principles.md) ·
caveat evidenza [fondamenti_tecnici/08_asset_allocation_passiva](fondamenti_tecnici/08_asset_allocation_passiva/principles.md)

---

## 2026-06-02 — Due tracce parallele + pivot Stock Selector → TAA risk-management

**Decisione.** Il lavoro procede su **due strade parallele**, non più in catena unica:
1. **Esecuzione/dati**: Telegram signal copier, OctoBot, Confluence automatica.
2. **Quant/investing**: parte dai **dati e dall'infrastruttura dello Stock Selector**.

Quando un fronte non ha lavoro attivo (solo raccolta dati), si avanza sull'altro. Questo
**emenda** la catena di priorità del 2026-05-30 (sotto): non un ordine rigido, ma due tracce
concorrenti. Vincolo invariato: **non promuovere nulla a capitale reale** finché la milestone-1
(mese demo positivo) non è raggiunta; il lavoro investing resta **validazione**, non operatività.

**Pivot Stock Selector.** Lo stock-picking cross-sezionale nell'SP500 è **falsificato**
(IC momentum ~0 a 12y, score fondamentale anti-predittivo — vedi review). Lo Stock Selector
pivota verso un **motore di asset-allocation tattica (TAA)** = gestione del rischio fattoriale
β<1 (timing dell'esposizione + dual-momentum cross-asset), **non** ricerca di alpha da selezione.
Layer 2-3 (selezione titoli) **congelati**; Layer 4 (multi-mercato) futuro.

**Correzione dati.** Per i backtest PIT survivorship-free i vendor sono **Sharadar SF1 / Norgate**,
**non Interactive Brokers** (che non fornisce titoli delistati → survivorship bias). IB resta
valido solo per l'esecuzione live. Acquisto dati rimandato finché il Layer 1 (gratis: ETF +
FRED) non supera il gate `/quant-review`.

→ Design + merge review a 5 agent: [docs/INVESTMENT_ALGO_DESIGN.md](docs/INVESTMENT_ALGO_DESIGN.md) ·
Review dati: [docs/reviews/stock_selector-2026-06-01.md](docs/reviews/stock_selector-2026-06-01.md)

---

## 2026-05-30 — Ordine di priorità del workspace

**Decisione.** Priorità in quest'ordine: **(1) OctoBot** → **(2) dati da Confluence + Telegram
signal copier** → **(3) prop firm** (anticipata dai segnali, se i dati reggono) → **(4) strategie
automatiche custom (IN FONDO)**.

**Razionale.** Concentrare l'energia su ciò che è già pronto a produrre dati/segnali invece
di disperdersi a costruire nuove strategie custom. Le strategie/agenti custom (incl. tutti i
*blueprint* in `fondamenti_tecnici/blueprints/`) restano backlog finché OctoBot e la raccolta
dati non sono completi. **Non riproporre dev custom finché OctoBot non è completo.**

---

## 2026-05-2x — Telegram Signal Copier: demo full-auto, prop rimandata

**Decisione.** Il copia-segnali (2 canali mentori → MT5) gira in **demo, full-auto**. La prop
sui segnali è **rimandata** (anticipabile se i dati demo reggono, vedi priorità sopra).

**Razionale + caveat.** Fase di test per validare parsing + risk gate prima di rischiare capitale.
Attenzione **compliance copy-trading** lato prop firm (alcune vietano la copia di segnali terzi).
Architettura: Telethon → parser → risk gate → MT5. I segnali mentori sono oggi **semiautomatici
in test** ma il target è la **piena automazione**.

→ Codice: [signal_copier/](signal_copier/) · Test: [tests/test_signal_copier.py](tests/test_signal_copier.py)

---

## 2026-05-30 — London Breakout: **NO-GO** (archiviata)

**Decisione.** London Open Breakout EA **archiviata**. Non si promuove a capitale reale.

**Razionale.** Quant review: su 686 trade (2020–2026) PBO alto, DSR non significativo, e l'edge
percepito dal regime gating era **look-ahead** (label calcolato sul close dello stesso giorno).
Il codice resta conservato in `mql5/` ma non è deployabile.

→ Review: [docs/reviews/london_breakout-2026-05-29.md](docs/reviews/london_breakout-2026-05-29.md) ·
Postmortem: [docs/reviews/london_breakout-postmortem-2026-05-30.md](docs/reviews/london_breakout-postmortem-2026-05-30.md)

---

## 2026-05-2x — Caveat look-ahead della regime timeline

**Decisione/Regola.** `data/regime_timeline_gbpusd.csv` ha il label calcolato sul **close del
giorno stesso** → usarlo **SOLO con lag 1 giorno** per strategie intraday, altrimenti si gonfia
l'edge. È stato il cap della quant-review di London Breakout.

**Razionale.** Evitare look-ahead bias (vedi [fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/)).

---

## 2026-05-29 — TSMOM USDJPY: **NO-GO / dati insufficienti**

**Decisione.** TSMOM single-asset (USDJPY D1) **non promosso**.

**Razionale.** 38 trade, DSR ≈ 0, l'edge dipendeva da 1 trade (regime 2021-22); sotto-campione
2024-26 negativo. Possibile rivalutazione solo in versione **multi-asset** con campione adeguato.

→ Review: [docs/reviews/tsmom_jpy-2026-05-29.md](docs/reviews/tsmom_jpy-2026-05-29.md) ·
[docs/reviews/tsmom-multiasset-2026-05-30.md](docs/reviews/tsmom-multiasset-2026-05-30.md)

---

## 2026-05-24 — Quant Reviewer come gate decisionale

**Decisione.** Le decisioni promuovi/scarta strategia passano da una **quant-review formale**
(`/quant-review`), non da impressioni. Pipeline: dati live → quant review → modifica codice.

**Razionale.** Dopo 2 settimane live (London: 2 trade; Confluence: 0 trade per attrito operativo)
serviva un metro statistico (PBO, DSR, walk-forward, MC permutation).

→ [agents/quant_reviewer.md](agents/quant_reviewer.md) · [core/quant_metrics.py](core/quant_metrics.py) ·
[docs/QUANT_REVIEW_PROTOCOL.md](docs/QUANT_REVIEW_PROTOCOL.md)

---

## 2026-05-24 — Confluence manuale → opportunistica

**Decisione.** La Confluence **manuale** (weekend planning + `levels.yaml`) è **opportunistica**:
nessun obbligo settimanale. L'energia è sull'**automazione** (`confluence_auto/` shadow run).

**Razionale.** L'attrito operativo del planning weekend produceva 0 trade. Meglio investire
sull'estrazione algoritmica dei livelli e raccogliere dati di confronto manuale vs algoritmico.

→ Concetti: [TRADING_PRINCIPLES.md](TRADING_PRINCIPLES.md) · [strategies/confluence_auto/](strategies/confluence_auto/)
(il vecchio `WEEKEND_CHECKLIST.md` — procedura manuale livelli→`levels.yaml`→VPS — è stato eliminato il 2026-06-14)

---

## 2026-05-05 — Pivot architetturale (ibrido Python/MQL5, 3 componenti)

**Decisione.** Architettura ibrida a **3 componenti indipendenti, 3 habitat, zero bridge**:
1. **Confluence Levels** (Python) — solo notifica — VPS Linux Hetzner.
2. **Expert Advisor MQL5** (es. London Breakout, archiviato) — esecuzione automatica — MetaQuotes VPS.
3. **Stock Selector** (Python) — tool offline — PC di casa.

**Razionale.** Disaccoppiare deployment e failure mode; niente VPS Windows/RDP; niente sync
Python↔MQL5. Sostituisce il piano monolitico pre-pivot.

→ Architettura: [docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md) ·
Operatività: [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md) ·
Doc storico pre-pivot: [docs/STAGE2_TESTING_PLAN.md](docs/STAGE2_TESTING_PLAN.md)

---

## Principio trasversale — Edge condizionato alla strategia

Nessuna fase di mercato è tradabile/non-tradabile **in assoluto**: l'edge è condizionato alla
strategia + regime. Il backtest da solo **non basta** — triangolare con razionale economico e
walk-forward. Vedi [fondamenti_tecnici/03_regimi_macro/](fondamenti_tecnici/03_regimi_macro/) e
[fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/).

---

## Principio trasversale — Mappa dei modelli (gestione dei conflitti tra teorie)

I mercati non sono scienza esatta: **non esiste l'equazione madre** che spiega/predice tutto.
Quando due fonti o teorie si contraddicono, il nostro compito **NON è eleggere un vincitore
universale** ("X è più giusto di Y"). Si registra **ogni modello con le sue CONDIZIONI di
validità** e si rende il conflitto **esplicito**, così la decisione operativa sceglie il modello
che calza il contesto. È l'estensione naturale del principio "edge condizionato" qui sopra.

**Model card minima** per ogni claim in conflitto:
`{ claim · fonte · condizioni (regime/asset/timeframe/assunzioni) · contraddice · stato (attivo/reference/parcheggiato) }`

**Esempi svolti** (i due conflitti già emersi nel materiale):
- *"Il backtest è inutile / è overfitting"* (Roan, Quant Guild) **vs** *"misura con DSR/PBO/
  walk-forward"* (López de Prado, nostro quant). **Non** è una contraddizione: vale separando
  *non curve-fittare una regola di timing* (vero) da *non misurare distribuzioni / non falsificare*
  (falso). Condizione: il backtest serve a **falsificare e misurare proprietà distributive**, non
  a *scoprire* la regola.
- *"Vendi il volatility risk premium"* (IV sovrastima RV in media) **vs** *"compra convexity /
  long-vol"* (mitiga il drag nei crash). Entrambe vere secondo **regime/timing**: vendi il premio
  in mercato normale, l'assicurazione paga nei tail.

Operativamente la mappa vive in due posti: il **registro di intake**
([fondamenti_tecnici/_INTAKE.md](fondamenti_tecnici/_INTAKE.md)) traccia stato e destinazione di
ogni fonte; le **condizioni di validità** stanno accanto al concetto nel file `fondamenti_tecnici/`
che lo ospita, con cross-link al claim opposto. Regola epistemica di base: §0 di
[agents/quant_reviewer.md](agents/quant_reviewer.md) (il gioco, non i giocatori).
