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
