# London Breakout — Resoconto, lezioni apprese e archiviazione — 2026-05-30

> Documento di chiusura. Decisione utente (2026-05-30): **archiviare** la strategia, **conservare** tutti i dati raccolti. Nessuna eliminazione.
> Basato su: [docs/reviews/london_breakout-2026-05-29.md](london_breakout-2026-05-29.md) (review formale) · codice [mql5/london_breakout.mq5](../../mql5/london_breakout.mq5) · dati [backtest_results/london_breakout/](../../backtest_results/london_breakout/).

## 1. Cosa è stato fatto

- Implementato breakout della sessione asiatica su GBPUSD M15 (stop OCO alle 07:00 UTC, SL al lato opposto, time-stop 16:00, filtri NFP/FOMC, sizing 1% fixed-fractional).
- Refactor con `InpExitMode` per testare 3 exit (A=FIXED_RR, B=PARTIAL_TRAIL, C=FULL_TRAIL).
- Backtest MT5 99% real-tick 2020–2026 (686 trade) + sotto-finestra 2025–2026 (139 trade).
- Quant review formale (PBO-surrogato, DSR, walk-forward, MC permutation, split per regime, haircut costi).

## 2. Verdetto e perché i principi non reggono

**Verdict: NO-GO incondizionato.** I principi sono stati valutati anche nelle condizioni più favorevoli; nessuna versione supera il breakeven al netto di costi e look-ahead:

| Ipotesi di rifinitura | Risultato (dati reali) | Esito |
|---|---|---|
| Baseline always-on (A) | Net −552, PF 0.98, Sharpe −0.10, **MC p=0.51** | Nessun edge |
| Solo lato long (la nota segnalava asimmetria) | +173, **PF 1.013** | Breakeven, negativo post-costi |
| Solo lato short | −725, PF 0.94 | È il ramo che sanguina |
| Gating "accendi su Volatile" (label same-day) | +1828, PF 1.21 | **Artefatto look-ahead** |
| Gating su regime **point-in-time** (label D−1) | +349, PF 1.04 → **negativo post −1 pip** | Non rescue |
| Esperimento exit A/B/C | B e C **mai prodotti** (file "partial trail" = duplicato di A) | Non valutabile |

La famiglia di edge (Osler, AER 2003: clustering di stop-order) è plausibilmente **decaduta** (McLean-Pontiff, JF 2016) e su GBPUSD London 2020–2026 non è presente al netto dei costi. Non c'è un parametro da girare che cambi il segno: il problema non è il tuning, è l'assenza di edge.

## 3. Lezioni apprese (da portare a TUTTE le strategie future)

1. **I label di regime devono essere point-in-time.** È la lezione più costosa: usare il regime calcolato sulla chiusura del giorno D per decidere un trade delle 07:00 di D gonfiava l'edge apparente di ~5× (+1828 → +349). Regola operativa registrata in [[reference_regime_timeline_lookahead]]: per strategie intraday usare sempre il regime di **D−1**.
2. **Verificare la provenienza dei backtest prima di analizzarli.** Due file "diversi" erano lo stesso run (hash diverso, deal identici). Check d'ora in poi: confrontare inputs-block + hash + un diff sui deal prima di trattarli come varianti.
3. **Trappola del sotto-campione favorevole.** Il read iniziale "positivo" (2025–2026: +413, PF 1.08) era una coda fortunata; il campione pieno 6 anni è negativo. Mai concludere da una finestra corta scelta a posteriori.
4. **Costi/slippage su stop-order non sono opzionali.** Con PF già < 1.0, −1 pip/trade porta a PF 0.92; gli stop in breakout slippano 2–5× spread (persona §3).
5. **L'asimmetria long/short era reale ma non sfruttabile.** Disabilitare il lato debole porta a breakeven, non a edge: rimuovere perdite non crea profitto.

## 4. Stato di archiviazione

- **Codice**: [mql5/london_breakout.mq5](../../mql5/london_breakout.mq5) — conservato, non più in sviluppo. NON deployare (neppure demo): gate quant non superato.
- **Dati**: [backtest_results/london_breakout/](../../backtest_results/london_breakout/) — conservati come evidenza storica.
- **Review + questo post-mortem**: restano in `docs/reviews/` come motivazione tracciata della decisione.
- **`activation` rule / regime CSV**: NON modificare sulla base di questi numeri (erano look-ahead).

**Status: ARCHIVIATA.** Riapribile solo se emerge un razionale strutturale nuovo (es. filtro di liquidità point-in-time documentato) da validare da zero, non come tuning di questa.
