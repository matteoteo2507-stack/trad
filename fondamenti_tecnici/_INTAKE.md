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

## Baseline già distillato (storico)
Il corpus storico in [`_sorgenti/`](_sorgenti/) è già distillato nei moduli `01…08` e nei
`blueprints/` — mappa in [README.md](README.md). Questo registro traccia attivamente il **nuovo**
intake da qui in avanti.

## Collegamenti
- [DECISIONS.md](../DECISIONS.md) — dottrina "Mappa dei modelli" (regola dei conflitti).
- [README.md](README.md) — tassonomia della knowledge base (concetti / blueprints / candidate).
