---
titolo: Registro di intake — materiale grezzo in entrata
tipo: indice
---

# Registro di intake (la porta lossless)

Ogni fonte grezza che entra nel workspace passa di qui **prima** di essere distillata o
parcheggiata. Scopo: **non perdere materiale utile** e rendere l'integrazione seriale,
riprendibile e verificabile. È anche l'**imbocco del loop di apprendimento** futuro:
`nuovo materiale → intake → triage → distilla / parcheggia`.

## Come si usa (procedura di triage)
1. **Cattura** la fonte grezza in [`_sorgenti/`](_sorgenti/) (lossless, sempre).
2. **Triage**: decidi lo stato — `grezzo` (da valutare) · `distillato` (integrato in un modulo
   `0X`/blueprint) · `parcheggiato` (reference/catalogo, approfondito on-demand).
3. **Distilla solo il necessario** (ciò che tocca i sistemi attivi). Il resto resta reference.
4. **Conflitti** → non eleggere un vincitore: applica la **mappa dei modelli**
   ([DECISIONS.md](../DECISIONS.md) → Principio trasversale) e annota la condizione nella colonna note.

Stati: `grezzo` · `distillato` · `parcheggiato`

## Backlog attivo

| Fonte (grezzo) | Origine | Stato | Destinazione | Note / conflitti |
|---|---|---|---|---|
| `_sorgenti/NOZIONI AGGIUNTIVE.txt` — volatility drag + orthogonal streams | Roman Paolucci / Quant Guild | **distillato** | [[05_portfolio_rischio]], `agents/quant_reviewer.md`, `skills/backtest-runner` | EV positivo ≠ crescita geometrica. Conflitto "backtest inutile vs misura": vedi mappa-modelli |
| `_sorgenti/NOZIONI AGGIUNTIVE.txt` — VRP (volatility risk premium) | Roman Paolucci / Quant Guild | **parcheggiato** | nota leggera in [[05_portfolio_rischio]] | Opzioni/vol = fuori scope operativo. Esempio cardine mappa-modelli (vendi premio vs compra convexity) |
| Prompt "Markov 2.0 — Hedge Fund Method" (FIX 1/2/3) | mentore (via Fable 5) | **distillato** (FIX 1) | [[04_quant_metodologia]], `quant_reviewer.md`, [blueprint markov](blueprints/markov_regime_skill.md) | FIX 1 (disjoint/stride) corregge un bug reale della 1.0. Skill NON installata (DECISIONS: custom in fondo) |
| Estratto Roan "Quant Series" + 18 repo `jackson-video-resources` | Roan (@RohOnChain) / Lewis Jackson | **parcheggiato** | [blueprint roan_quant_series_extract](blueprints/roan_quant_series_extract.md) | Reference/catalogo. 3 repo (`paperclip`, `ai-quant-workbench`, `skills`) = INPUT del piano workflow successivo. ≠ Quant Guild |
| `_sorgenti/Nuove nozioni teoriche 2026-07-16.txt` — tail risk + survival positioning; decomposizione varianza 2-asset | Quant Guild (stessa scuola Paolucci) | **distillato** (tasselli nuovi) | [[05_portfolio_rischio]] (tail risk regime-cond., $\mathrm{Var}$ 2-asset), [[04_quant_metodologia]] (walk-forward domain, CAGR BS-test) | Conflitto mappato: "walk-forward fallisce/predizione impossibile" NON contraddice il nostro WF → domìni diversi (persistenza edge ≠ timing tail). Vedi [[feedback_backtest_long_history_falsification]] |
| `_sorgenti/Nuove nozioni teoriche 2026-07-16.txt` — blocchi CAGR/EMH/CAPM/diversificazione | Quant Guild | **rinforzo** (già distillato) | — | ~80% del file duplica 04+05 (volatility drag, alpha ortogonale, CAPM/beta, correlazioni→1). Non ri-distillato per non gonfiare |
| `_sorgenti/Nuove nozioni teoriche 2026-07-16.txt` — blocco 1: market update semiconduttori (16-07-2026) | investitore hedge fund (video) | **parcheggiato** | lossless in `_sorgenti/` | Commentario **tattico/time-sensitive** (val. semi, war/Fed/Trump, CapEx). Conflitto mappato: vista discrezionale attiva ≠ pilastro investing **passivo** ([[08_asset_allocation_passiva]]) → NON deve contaminare il PAC/glide-path |
| `_sorgenti/NXT strategy Fibonacci Elliott (video ex-socio).txt` — strategia "NXT" degli ex-soci | ex-socio (video) | **distillato → NO-GO** (+ lead fade) | [strategie_candidate/nxt_fib_trend_pullback.md](strategie_candidate/nxt_fib_trend_pullback.md) | Continuazione NO-GO: win 13.3% (claim 60-70%), E[R]=−0.44R, 14/14 anni + 6/6 asset neg., holdout coerente; wide-stop non salva. **Sottoprodotto**: il FADE (mean-reversion) è +0.35R robusto ma è ipotesi data-derived → lead da RI-pre-registrare + forward OOS, NON un GO. Motori `analysis/nxt/{backtest,closure}.py`. Vedi [[project_nxt_fib_nogo_2026_07_17]] |
| `_sorgenti/Appunti misti 2026-08-04.txt` — blocco 1: lost decades | video divulgativo (stesso tema di "Lost Decades PAC") | **rinforzo** + 3 tasselli **distillati** | [[08_asset_allocation_passiva]] §Decenni persi p.6 e p.4, §Buffer | ~Tutto già distillato il 18/07 dall'altra fonte (3 periodi US, recupero asimmetrico, CAPE debole, timing MM200 già RIFIUTATO, DCA-a-saldo, All-World). NUOVI: **costo reale del cash** (16 paesi 1900-2011 — ⚠️ numeri **da verificare su DMS**: −4,1% come *mediana* secolare è implausibile, somiglia al valore **Italia**); **falsificazione indipendente timing CAPE 1958-2015** (non batte B&H *prima* di tasse, ~0,5%/anno di premio perso, Sharpe ~0,37 pari); **ancora di sizing buffer** (27% disoccupati >27 settimane → pavimento 6 mesi, da ri-verificare su Istat) |
| `_sorgenti/Appunti misti 2026-08-04.txt` — blocco 2: risk mispricing / breadth vs depth | divulgatore con lead magnet (corso + research note) | **distillato** (1 concetto) + **conflitto mappato** | [[04_quant_metodologia]] §9 (pre-mortem), [DECISIONS.md](../DECISIONS.md) §Mappa dei modelli | Tassello utile: **direzioni principali di rischio** = pre-mortem scritto prima del capitale, con esempio svolto sui segnali mentore (4 rischi su 5 sono NON-statistici: key-man, compliance, rottura parser, slippage). Colma un buco reale: 04/05 sono tutti ex-post. **CONFLITTO**: la tesi forte della fonte ("i modelli quantitativi non misurano il rischio forward, vince la profondità qualitativa") è una licenza a scavalcare un NO-GO pre-registrato → separata per **dominio** (scommessa discrezionale $n=1$ vs regole sistematiche ripetibili). Condizione: **il qualitativo genera ipotesi, non valida mai**. Bayesian updating solo su dati forward, mai sugli stessi del test |
| `_sorgenti/Appunti misti 2026-08-04.txt` — blocco 3: MMT / guerra Iran | video divulgativo (commentario politico) | **parcheggiato** | lossless in `_sorgenti/` | **Nessuna distillazione, per scelta.** (1) Zero aggancio operativo ai sistemi attivi (FX/oro intraday, PAC passivo); (2) l'MMT è una **scuola macro contesa**, non consenso — "il denaro segue le risorse" *validato da una guerra* è retorica, non evidenza; (3) time-sensitive/politico, stessa categoria del market update semiconduttori parcheggiato a luglio. L'unico residuo (spesa oltre le risorse → inflazione) è già coperto in [[03_regimi_macro]] |
| `_sorgenti/Appunti misti 2026-08-04.txt` — blocco 4: outlook macro 4-ago-2026 | video divulgativo (snapshot) | **parcheggiato** + 2 estratti **distillati** | [[03_regimi_macro]] §6 (canali cross-asset), [[08_asset_allocation_passiva]] §Buffer | Il grosso (CPI/Fed/labour/sentiment) è **fotografia datata** → obsoleta in settimane, e **non deve contaminare il pilastro passivo** (posizionamento, non predizione). Distillati solo i **meccanismi durevoli**: **yen carry trade** (unwind riflessivo → yield USA su + risk-off; precedente ago-2024, rilevante perché operiamo XAUUSD/NASDAQ intraday) e **chokepoint energetici** (Hormuz ~20% del greggio → gap overnight), entrambi come **event-risk, NON segnali**. **RIFIUTATI**: template **70-80% S&P 500 + 10-20% intl** (home bias USA importato = concentrazione geografica; la fonte **si auto-contraddice** col blocco 1 che invoca la diversificazione globale contro i decenni persi locali di Italia/Giappone), ~$200k in metalli (bilancio altrui), prodotti cash US (CD/FDIC → l'equivalente IT è conto deposito/FITD 100k, al netto del 26%). ⚠️ Il blocco riporta "GDP Q3 2026 **+5,0%**" accanto a Q2 1,5% e leading indicator negativo → probabile errore di trascrizione, **non riportato da nessuna parte** |
| `_sorgenti/Lost Decades PAC (video).txt` — decenni persi nel mercato azionario | video divulgativo | **distillato** | [[08_asset_allocation_passiva]] (sez. "Decenni persi") | RINFORZA il PAC passivo (All-World anti-home-bias, buffer, glide-path) + 2 tarature (real-return conservativi vs CAPE alto; allocazione "sopportabile"). La proposta market timing 200-MA = RIFIUTATA (regime-dependent + tasse IT 26%; survival-over-prediction [[05_portfolio_rischio]]). Il "lost decade" è statistica lump-sum, il DCA la riscrive |

## Fonti ricorrenti (mandato permanente)

| Fonte | Natura | Mandato | Vincoli |
|---|---|---|---|
| **Chart Fanatics** / **Words of Rizdom** (Riz Iqbal) — valutate 2026-08-04 | Stesso ecosistema, non fonti indipendenti. Monetizzate via **Chart Academy** (corsi) e **affiliazione Apex Trader Funding**. "Verified traders" affermato, **metodo di verifica non pubblicato** | **Uso primario**: layer **operativo e di rischio** (come dimensionano dopo una serie negativa, cosa li fa smettere, trade management) → alimenta il pre-mortem [[04_quant_metodologia]] §9. **Uso secondario**: raccolta regole → pipeline di pre-registrazione | **Si raccolgono le regole, si scartano le statistiche dichiarate** (track record dei claim: 60-70%→13,3% NXT; 80-90%→~53% VELTRIX; 90%→~20% playbook Chart Fanatics per test di terzi). **Filtro d'ingresso**: solo strumenti che tradiamo, regole codificabili senza discrezionalità, timeframe coperti dai nostri dati. **Budget: max 2-3 pre-registrazioni esterne per trimestre** (ogni ipotesi in più alza la soglia DSR per tutte) |

## Baseline già distillato (storico)
Il corpus storico in [`_sorgenti/`](_sorgenti/) è già distillato nei moduli `01…08` e nei
`blueprints/` — mappa in [README.md](README.md). Questo registro traccia attivamente il **nuovo**
intake da qui in avanti.

## Collegamenti
- [DECISIONS.md](../DECISIONS.md) — dottrina "Mappa dei modelli" (regola dei conflitti).
- [README.md](README.md) — tassonomia della knowledge base (concetti / blueprints / candidate).
