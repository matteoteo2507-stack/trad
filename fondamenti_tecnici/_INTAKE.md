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
| `_sorgenti/Lost Decades PAC (video).txt` — decenni persi nel mercato azionario | video divulgativo | **distillato** | [[08_asset_allocation_passiva]] (sez. "Decenni persi") | RINFORZA il PAC passivo (All-World anti-home-bias, buffer, glide-path) + 2 tarature (real-return conservativi vs CAPE alto; allocazione "sopportabile"). La proposta market timing 200-MA = RIFIUTATA (regime-dependent + tasse IT 26%; survival-over-prediction [[05_portfolio_rischio]]). Il "lost decade" è statistica lump-sum, il DCA la riscrive |

## Baseline già distillato (storico)
Il corpus storico in [`_sorgenti/`](_sorgenti/) è già distillato nei moduli `01…08` e nei
`blueprints/` — mappa in [README.md](README.md). Questo registro traccia attivamente il **nuovo**
intake da qui in avanti.

## Collegamenti
- [DECISIONS.md](../DECISIONS.md) — dottrina "Mappa dei modelli" (regola dei conflitti).
- [README.md](README.md) — tassonomia della knowledge base (concetti / blueprints / candidate).
