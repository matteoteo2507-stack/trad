# skills/

Skill in formato `SKILL.md` da usare con Claude Code / Antigravity.

Ogni skill è una cartella con un file `SKILL.md` che contiene:
- frontmatter YAML con `name` e `description` (usate dal dispatcher per attivare la skill);
- istruzioni in markdown su come svolgere il compito.

## Skill disponibili

| Skill | Quando si attiva |
|---|---|
| `stock-selector/` | Quando si vuole eseguire o modificare la selezione azionaria SP500 basata sul sistema V6.0 |
| `strategy-designer/` | Quando si vuole progettare una nuova strategia partendo da un PDF di analisi tecnica o da un'idea |
| `backtest-runner/` | Quando si vuole testare una strategia su uno o più backtester e ottenere un report comparativo |
| `telegram-notifier/` | Quando si vuole inviare un segnale via Telegram o configurare il bot |

## Convenzione frontmatter

```yaml
---
name: nome-skill
description: Quando attivare questa skill (frase breve, comprensibile dal dispatcher).
---
```
