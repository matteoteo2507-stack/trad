# strategies/ — Indice master

> **Nota sul nome.** La cartella resta `strategies/` (namespace Python importato da
> `core/runner`, `core/registry` e dai test). Concettualmente è l'area "strategie" del progetto.
> Questo file è l'**indice unico** di tutte le strategie e i componenti operativi, anche quelli
> che vivono fuori da `strategies/` (`mql5/`, `signal_copier/`).

I **sistemi** (semiautomatico → automatico) sono uno **spettro di maturità esecutiva**, non
etichette fisse: un sistema nasce semiauto (l'utente piazza) e gradua ad auto. Vedi
[PROJECT.md](../PROJECT.md). Prima di promuovere/scartare qualcosa, leggi [DECISIONS.md](../DECISIONS.md).

---

## Convenzione: una strategia = una cartella

```
strategies/<nome>/
├── strategy.py       # classe che eredita da StrategyBase (regole codificate, no LLM nel loop)
├── config.yaml       # parametri (size, soglie, timeframe) — niente valori magici nel codice
└── README.md         # vedi sotto: blocco metadati + cosa fa + ipotesi + riferimenti
```

Ogni `README.md` di strategia inizia con un **blocco metadati**:

```markdown
> **Sistema:** semiauto | auto | investing | candidata
> **Stato:** active | shadow | backlog | archived-NO-GO | stub
> **Habitat:** VPS Hetzner | MetaQuotes VPS | PC | demo MT5
> **Quant review:** <link a docs/reviews/...> oppure —
> **Fondamenti:** <link a fondamenti_tecnici/...>
```

Per creare una nuova strategia: copia [`_template/`](_template/), compila i 3 file, aggiungi il
test minimo in `tests/test_<nome>.py`, valida, poi promuovi (commit dedicato + risk gate). Dettaglio
del pattern in [CONVENTIONS.md](../CONVENTIONS.md).

---

## Mappa di tutte le strategie / componenti

### 1. Semiautomatico — *l'analisi arriva, l'utente piazza*

| Componente | Stato | Habitat | Quant review | Fondamenti |
|---|---|---|---|---|
| [confluence_levels/](confluence_levels/) | active (Fase A) | VPS Hetzner | — | [price action](../fondamenti_tecnici/01_price_action/), [liquidità](../fondamenti_tecnici/02_liquidita_orderflow/) |
| Analisi canali Telegram mentori | in test (→ auto) | mobile/PC | — | — |

### 2. Automatico — *segnali eseguiti direttamente*

| Componente | Stato | Habitat | Quant review | Fondamenti |
|---|---|---|---|---|
| [../signal_copier/](../signal_copier/) | demo full-auto | demo MT5 | — | — |
| [../mql5/](../mql5/) London Breakout | **archived-NO-GO** | MetaQuotes VPS | [review](../docs/reviews/london_breakout-2026-05-29.md) · [postmortem](../docs/reviews/london_breakout-postmortem-2026-05-30.md) | [regimi/macro](../fondamenti_tecnici/03_regimi_macro/) |
| [tsmom/](tsmom/) | **NO-GO** / stub | (Python) | [review](../docs/reviews/tsmom_jpy-2026-05-29.md) | [quant](../fondamenti_tecnici/04_quant_metodologia/) |
| [confluence_auto/](confluence_auto/) | shadow run | VPS Hetzner | — | [liquidità/POC](../fondamenti_tecnici/02_liquidita_orderflow/) |
| OctoBot (crypto) | **DORMIENTE** (stand-by 2026-06-14, rispolverabile) | esterno | — | [quant](../fondamenti_tecnici/04_quant_metodologia/) |

### 3. Manuale / Investing — *lungo termine, da entrate prop (parte conclusiva)*

| Componente | Stato | Note |
|---|---|---|
| PAC (piano di accumulo) | da definire | accumulo passivo lungo orizzonte |
| [stock_selector/](stock_selector/) | active (dinamico) | **non etichettato per regime** (oggi semiauto, automatizzabile); parallelo a PAC + worldmonitor |
| worldmonitor bridge | backlog | fonte sensoriale macro/geopolitica, convergenza finale |

### 4. Candidate — *distillate dai fondamenti, NON ancora costruite*

| Candidata | Fonte | Note |
|---|---|---|
| [NYSE Scalping](../fondamenti_tecnici/strategie_candidate/nyse_scalping.md) | fondamenti_tecnici | VWAP+TPO+OTF; da promuovere se prioritizzata |
| Backlog automatiche | [ARCHITECTURE_v2 §backlog](../docs/ARCHITECTURE_v2.md) | TSMOM multiasset, Donchian, DXY z-score, mean-reversion, KAMA+ATR |

> Le candidate e i [blueprints](../fondamenti_tecnici/blueprints/) restano in fondo alle priorità
> finché la raccolta dati non è completa ([DECISIONS.md](../DECISIONS.md)). NB: OctoBot **dormiente**
> dal 2026-06-14, non più gating per le custom.

---

## Riferimenti

- Fondamenti teorici: [fondamenti_tecnici/](../fondamenti_tecnici/)
- Costituzione operativa: [TRADING_PRINCIPLES.md](../TRADING_PRINCIPLES.md)
- Convenzioni codice: [CONVENTIONS.md](../CONVENTIONS.md)
- Quant review: [docs/QUANT_REVIEW_PROTOCOL.md](../docs/QUANT_REVIEW_PROTOCOL.md)
