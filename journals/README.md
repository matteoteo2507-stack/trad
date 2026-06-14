# `journals/` — overview

Cartella che raccoglie tutto ciò che riguarda il **journaling del trading**: planning
weekend, trade record, review, futura analytics.

## Contenuto

| File | Tracciato in git? | Scopo |
|---|---|---|
| `LEGENDA.md` | sì | Legenda della cartella + struttura dei journal markdown |
| `NOTION_JOURNAL_SCHEMA.md` | sì | Schema autoritativo del database Notion `Trading Journal` |
| `NOTION_SETUP_GUIDE.md` | sì | Guida step-by-step per creare il database Notion |
| `README.md` | sì | Questo file |
| `journal_settimana_*.md` | no (gitignored) | Journal markdown settimanali (planning weekend, trade non eseguiti, osservazioni, auto-valutazione) |

## Architettura del journaling (post 2026-05-18)

```
┌────────────────────────────────────────────────────────────┐
│  PLANNING WEEKEND (markdown locale, gitignored)            │
│  journal_settimana_YYYY-MM-DD.md                           │
│  - Regime di mercato                                       │
│  - Livelli Monthly/Weekly/Daily/H4/H1                      │
│  - Fibonacci, POC                                          │
│  - Setup operativi della settimana                         │
│  - News calendar                                           │
│  - Trade NON eseguiti (skip + cosa è successo dopo)        │
│  - Osservazioni mercato giornaliere                        │
│  - Auto-valutazione fine settimana                         │
└────────────────────────────────────────────────────────────┘
                          ↓ (i Setup ID diventano riferimento)
┌────────────────────────────────────────────────────────────┐
│  TRADE RECORD (Notion `Trading Journal`)                   │
│  Database unico per Live + Demo + Backtest                 │
│  - Una riga per trade                                      │
│  - Compilato quando il trade viene preso (pre)             │
│  - Completato a chiusura (post)                            │
│  - Accessibile da mobile/desktop                           │
│  - Schema in NOTION_JOURNAL_SCHEMA.md                      │
└────────────────────────────────────────────────────────────┘
                          ↓ (futuro)
┌────────────────────────────────────────────────────────────┐
│  ANALYTICS (Python, da pianificare dopo 1-2 mesi)          │
│  - R-multiple per setup / strumento / sessione             │
│  - Expectancy, win rate, drawdown                          │
│  - Pattern di deviazione dal piano                         │
│  - Equity curve                                            │
└────────────────────────────────────────────────────────────┘
```

## Perché due fonti (markdown + Notion)?

- **Markdown** = planning settimanale. È **per-settimana**, va bene la struttura
  documentale (sezioni). Non serve mobile, lo compili la domenica al PC. Resta
  gitignored perché contiene dati personali e dati di mercato volatili.
- **Notion** = trade record. È **per-trade**, una riga di database. Serve mobile
  perché il trade lo registri *quando lo prendi*. Tabella relazionale, filtrabile,
  taggabile, in futuro analizzabile via connector Claude.

I due si parlano via `Setup ID`: il markdown definisce `EURUSD-2026W19-S1` durante
il weekend, Notion lo riferisce quando esegui il trade.

## Riferimenti

- Principi operativi (incl. planning weekend): [`../TRADING_PRINCIPLES.md`](../TRADING_PRINCIPLES.md)
- Setup levels yaml: [`../strategies/confluence_levels/levels.yaml`](../strategies/confluence_levels/levels.yaml)
