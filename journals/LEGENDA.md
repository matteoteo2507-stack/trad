# `journals/` — legenda

Cartella che raccoglie planning settimanale, trade record e documentazione del
trading journal. Vedi [`README.md`](README.md) per la struttura completa.

> **Cambio architetturale 2026-05-18**: i **Trade eseguiti** non si registrano più
> nel markdown settimanale, ma nel database **Notion `Trading Journal`**. Schema in
> [`NOTION_JOURNAL_SCHEMA.md`](NOTION_JOURNAL_SCHEMA.md), setup in
> [`NOTION_SETUP_GUIDE.md`](NOTION_SETUP_GUIDE.md).

## Due fonti, due scopi

- **Markdown settimanale** (gitignored) — planning weekend + trade NON eseguiti +
  osservazioni di mercato + auto-valutazione settimanale. Per-settimana, su PC,
  domenica + ogni sera.
- **Notion `Trading Journal`** — record per-trade, accessibile da mobile e desktop.
  Compilato quando il trade viene preso (pre) e a chiusura (post). Live + Demo + Backtest.

I due si linkano via `Setup ID` (es. `EURUSD-2026W19-S1`).

## Markdown settimanale — naming

```
journal_settimana_<YYYY-MM-DD>.md
```

Dove `<YYYY-MM-DD>` è la **domenica di compilazione** (= primo giorno della settimana trading).
Esempio: `journal_settimana_2026-05-17.md` copre la settimana lun 18/05 → ven 22/05.

## Markdown settimanale — struttura

Concetti di riferimento in [`../TRADING_PRINCIPLES.md`](../TRADING_PRINCIPLES.md). Sezioni del markdown:

| Sezione | Quando si compila | Riferimento principi |
|---|---|---|
| `## Regime corrente` | Domenica (output `python -m core.regime`) | §1 Regimi |
| `## Monthly / Weekly / Daily / H4 / H1 <simbolo>` | Domenica | §2 S/R · §3 S/D freshness |
| `## Fibonacci <simbolo>` | Domenica | §4 Fibonacci |
| `## POC <simbolo>` | Domenica | §7 Volume Profile / POC |
| `## Setup <simbolo>` | Domenica | §5 Criteri di ingresso |
| `## News settimana` | Domenica | filtro news (runner) |
| `## Trade NON eseguiti` | Ogni sera di trading | §Journaling |
| `## Osservazioni di mercato` | Ogni sera di trading | §Journaling |
| `## Auto-valutazione fine settimana` | Venerdì sera | §Journaling |

> La sezione `## Trade eseguiti` **non c'è più** nel template markdown. I trade
> eseguiti vivono su Notion.

## File presenti nella cartella

- `README.md` — overview architetturale (tracciato).
- `LEGENDA.md` — questo file (tracciato).
- `NOTION_JOURNAL_SCHEMA.md` — schema database Notion (tracciato).
- `NOTION_SETUP_GUIDE.md` — guida creazione database Notion (tracciato).
- `journal_settimana_*.md` — journal markdown operativi (NON tracciati).
