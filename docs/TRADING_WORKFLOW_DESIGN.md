# Trading Workflow — Design (pilota Level Analyzer)

> **Stato:** design vivo · 2026-06-18 · scope = **solo trading** (il pilastro investing è
> finito+rimandato, avrà eventualmente un workflow separato — vedi
> [INVESTING_PILLAR_PLAN](INVESTING_PILLAR_PLAN.md)).
> Decisioni di architettura (confermate dall'utente): **agentico ma human-gated** · **pilota
> singolo = Level Analyzer** · **substrato ibrido** (Python nel repo + skill/agenti Claude Code).

## Context
Obiettivo ricorrente: **sistemi operativi e testabili che generano dati REALI** da cui ottimizzare.
Il backtest non è sufficiente né obbligatorio — è solo falsificazione/distribuzione; il **dato
forward reale è la prova primaria**. Rischio centrale dichiarato: **dati mal contestualizzati**
(es. trade) → modifiche a strategie che non migliorano precisione/performance. Già vissuto: regime
BTC che si ribalta train→test, discrezione del socio scambiata per edge del sistema, trade
clusterati trattati come iid, GC=F futures spacciati per spot.

**Legge del workflow (sintesi delle due esigenze):** l'ottimizzazione è **evidence-gated, lenta e
condizionata** — non si cambia una strategia finché i dati non sono *ricchi di contesto* **e**
*statisticamente sufficienti*. Il workflow serve a **resistere all'ottimizzazione finché non è
giustificata**, non a ottimizzare in fretta.

## Principi
1. **Contestualizzazione prima di tutto.** Ogni record porta il suo contesto *al momento della
   decisione*. È la spina dorsale; senza, nessuna analisi è onesta.
2. **Evidence-gated.** Nessuna modifica live senza superare il gate quant (CI, `n_eff`,
   stratificazione per regime) → [[fondamenti_tecnici/04_quant_metodologia]], `core/quant_metrics.py`.
3. **Mappa dei modelli.** Ogni conclusione è *condizionata* (regime/asset/assunzioni), mai un
   verdetto universale → [DECISIONS.md](../DECISIONS.md).
4. **Human-gated.** Go-live, ogni modifica a strategia/parametri, e la riconciliazione degli esiti
   passano da te. Gli agenti propongono e preparano; **tu approvi**.
5. **Backtest = falsificazione, non scoperta.** Il forward reale guida; il backtest scarta.

## Architettura — il loop pilota (chiuso)

```
Capture → Journal/reconcile → Analyze (gate) → [Scouting → candidati]
   → Experiment (pre-registrato, APPROVATO) → Risk-gate / go-live → Capture…
```

| Stadio | Cosa fa | Substrato | Gate |
|---|---|---|---|
| **Capture** | logga ogni segnale col contesto *al momento della decisione* + posto per la scelta umana e l'esito reale | **Python (repo)** — `level_analyzer/record.py` | — |
| **Journal/reconcile** | riempie decisione umana (taken/skipped/modified) ed esito reale netto costi | skill agente + tuo input | 🔒 esiti |
| **Analyze (gate)** | stratifica per regime/sessione; E[R]+CI, `n_eff`, **taken vs skipped**, vs baseline invariato → *stato dell'evidenza* (non una modifica) | **Python (repo)** — riusa `core/quant_metrics.py` | — |
| **Scouting** (bi-settimanale) | scouting web → `_INTAKE.md`, **max N candidati** | skill agente | 🔒 triage |
| **Experiment** | pre-registra ipotesi+metrica, misura forward vs baseline | Python + skill | 🔒 **approvi tu** |
| **Risk-gate / go-live** | ogni modifica a parametri/sizing live | — | 🔒 **approvi tu** |

I tre **human-gate** (🔒) sono il punto in cui resti nel loop: riconciliazione esiti · approvazione
di ogni esperimento/modifica · go-live. Coerente con Fase A e con la discrezione del socio.

## La spina dorsale — record contestualizzato
Oggi `signals_log.csv` ha ~12 campi scarni. La spina (`level_analyzer/trade_records.csv`, gitignored)
porta ogni record a:

- **identità/segnale:** `record_id, ts_utc, asset, instrument_basis (spot/futures), data_source,
  side, zone, confluence, types, price, dist_atr, sl, tp, rr, risk_pct, param_version`
- **contesto decisione (alla cattura):** `session, regime, adx_h1, atr_h1, vol_h1, spread_assumed`
- **decisione umana (riempita dopo):** `human_decision (taken|skipped|modified), human_note`
- **esito reale (riempito dopo, netto costi):** `real_entry, real_exit, real_cost, real_R, outcome`

> **Perché questi campi sono non-negoziabili.** Senza `human_decision` non separi **edge del
> sistema** da **edge della discrezione**. Senza `spread_assumed`/`real_cost` non separi **edge
> decaduto** da **costo aumentato**. Senza `regime`/`session` non eviti il confounding di regime.
> Senza `instrument_basis`/`param_version` ripeti l'errore spot-vs-futures e mescoli versioni.
> Il contesto *al momento della decisione* **non è recuperabile dopo**: ecco perché la spina è
> l'Incremento 1 e ha l'unico vero costo-di-ritardo.

## Build incrementale (testabile)
1. **Spina dati** ← *questo incremento*. Record contestualizzato in cattura + colonne per umano/esito.
2. **Report del gate.** Legge la spina → stato dell'evidenza (CI, `n_eff`, regime, taken-vs-skipped,
   vs baseline). Nessuna modifica, solo verdetto "abbastanza evidenza? per quale conclusione?".
3. **Registro esperimenti / change-control.** Pre-registrazione ipotesi+metrica; misura forward vs
   baseline invariato + baseline naive. Evita p-hacking sul proprio forward.
4. **Agente di scouting** (bi-settimanale) → `_INTAKE.md`, ingresso capato, poi gate.

## Substrato ibrido — chi fa cosa
- **Python nel repo** (riproducibile, versionato, dietro il gate): spina (`record.py`), analisi/gate
  (riusa `core/quant_metrics.py` + `level_analyzer/`), registro esperimenti.
- **Skill/agenti Claude Code**: scouting/research, assistente di riconciliazione (journal),
  reportistica. Template di riferimento (solo idee, non installati): `paperclip` (firm a 6 agenti),
  `ai-quant-workbench`, `skills` — vedi [[fondamenti_tecnici/blueprints/roan_quant_series_extract]].

## Scouting bi-settimanale (caveat)
Cadenza fissa **ma ingresso capato**: lo scouting può degenerare in caccia alla novità (il
fallimento opposto alla cattiva contestualizzazione). Ogni candidato entra da `_INTAKE.md`, si
guadagna il posto passando dal gate, e va a competere con il baseline — non si adotta perché "nuovo".

## Collegamenti
- [`fondamenti_tecnici/_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md) — porta del materiale (scouting).
- [DECISIONS.md](../DECISIONS.md) — dottrina "mappa dei modelli" (conflitti).
- [`analysis/trading-bot-eval/SIZING_SPEC.md`](../analysis/trading-bot-eval/SIZING_SPEC.md) — il sizing layer (stadio Sizing).
- [`analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md`](../analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md) — il sistema pilota.
- `core/quant_metrics.py` — il gate (DSR/PBO/Wilson/bootstrap/`n_eff`).

## Verifica
- **Incremento 1**: una passata `scan`/`run` scrive un record con TUTTI i campi di contesto popolati
  alla cattura; le colonne umano/esito esistono vuote; un secondo strumento può aggiornarle by
  `record_id`. Smoke test offline incluso.
- Il record distingue spot/futures e versione parametri → niente più mix silenziosi.
