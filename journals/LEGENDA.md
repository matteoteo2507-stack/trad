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

Generata seguendo [`../WEEKEND_CHECKLIST.md`](../WEEKEND_CHECKLIST.md). Sezioni:

| Sezione | Quando si compila | Fase del checklist |
|---|---|---|
| `## Regime corrente` | Domenica | Fase 1 |
| `## Monthly / Weekly / Daily / H4 / H1 <simbolo>` | Domenica | Fase 2 |
| `## Fibonacci <simbolo>` | Domenica | Fase 3 |
| `## POC <simbolo>` (BOZZA) | Domenica | Fase 4 |
| `## Setup <simbolo>` | Domenica | Fase 5 |
| `## News settimana` | Domenica | Fase 9 |
| `## Trade NON eseguiti` | Ogni sera di trading | Fase 11 |
| `## Osservazioni di mercato` | Ogni sera di trading | Fase 11 |
| `## Auto-valutazione fine settimana` | Venerdì sera | Fase 11 |

> La sezione `## Trade eseguiti` **non c'è più** nel template markdown. I trade
> eseguiti vivono su Notion.

## File presenti nella cartella

- `README.md` — overview architetturale (tracciato).
- `LEGENDA.md` — questo file (tracciato).
- `NOTION_JOURNAL_SCHEMA.md` — schema database Notion (tracciato).
- `NOTION_SETUP_GUIDE.md` — guida creazione database Notion (tracciato).
- `journal_settimana_*.md` — journal markdown operativi (NON tracciati).
