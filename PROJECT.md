# PROJECT — obiettivo, ruoli, struttura

> **Aggiornato 2026-11-09** (reframing, [DECISIONS 2026-11-09](DECISIONS.md)). Le decisioni prese stanno in
> [DECISIONS.md](DECISIONS.md): la voce piu' recente vince su tutto, anche su questo file.

## Obiettivo (comune ai soci)

Portare alla **profittabilita'** sistemi di trading che operano **senza supervisione costante**, partendo da capitale
~0 e usando le **prop firm** come accesso al capitale; i guadagni vanno a un portafoglio di lungo periodo.

Il percorso, nell'ordine:

1. **Un sistema in profitto per almeno un mese su demo.**
2. **Prop firm**: superare una challenge low-cost col sistema validato
   ([criteri nostri](esercizio/prop/PROP_FIRM_CRITERIA.md)).
3. **Scalare con le prop**: reinvestire i guadagni in challenge nuove, su conti multipli e piu' grandi, fino a un conto
   da 100k.
4. **Allocare le entrate delle prop**:
   - **(a) portafoglio semi-passivo.** Il concetto resta, lo strumento e' da definire. Lo Stock Selector non e'
     applicabile (archiviato; lo score fondamentale e' una famiglia da testare, DECISIONS 2026-11-05);
   - **(b) PAC**: operativo dal 09/10/2026 ([piano](esercizio/pac/INVESTING_PILLAR_PLAN.md) §0);
   - **(c) dati**: fra i primi acquisti coi payout (DECISIONS 2026-11-07).

A che punto siamo: nessun sistema e' oggi candidato alla prop. Le 14 famiglie testate sono chiuse
(`python -m core.trial_ledger`); il PAC e' l'unica parte operativa.

## Ruoli

| Chi | Cosa fa |
|---|---|
| **I soci**, nei loro workspace (derivati in parte da questa infrastruttura) | test, backtest, walk-forward, riformulazione e test continui di strategie; parte della ricerca di strategie nuove |
| **`trad`** (Matteo) | i **fondamenti tecnici** su cui poggia la ricerca di edge, e la direzione della ricerca: strumenti di lettura del prezzo coerenti col mercato reale; l'analisi da quant di modelli trovati in fonti scelte (limiti, applicazioni, uso da solo o combinato); i **pacchetti** per i soci (report `.md` + file `.py`). Tiene il **metodo** (gatekeeper, contatore unico dei trial, `DECISIONS.md`) e il PAC |

**Strategia e strumento** sono definiti in [04_quant_metodologia §0](fondamenti_tecnici/04_quant_metodologia/principles.md).
In breve: uno strumento e' una lettura del prezzo con una proprieta' misurabile, senza regole di trade; una strategia
aggiunge ingresso, uscita e gestione del rischio, e produce trade.

**Il ciclo di uscita.** Uno strumento ha al massimo 5 versioni. Ognuna dichiara se e' una correzione (gratis) o una
modifica dopo i test dei soci (conta come trial). Nessun dato grezzo esce verso i soci.

## Vincoli

- **Tempo**: niente ore a grafico; il sistema fa lo scouting.
- **Capitale di partenza** ~0 €: la prop e' la via d'accesso.
- **Trading per regole codificate**: niente LLM nel ciclo di esecuzione. Gli agenti lavorano su ricerca, design e
  revisione.
- **Sicurezza**: mai live senza risk gate; `paper_mode` di default; tetti di drawdown in `config/risk.yaml`
  ([CONVENTIONS.md](CONVENTIONS.md)).
- **Metodo**: ogni test passa dal [ciclo di vita](docs/STRATEGY_LIFECYCLE.md) e dal gatekeeper; nessun numero senza
  nota sorgente e data.
- **Repo pubblico**: niente nomi, chat, orari o numeri di conto; i dati con licenza personale non entrano in git.

## Struttura

La macrostruttura segue l'ordine del processo: entra, si smista, si studia, si decide, si registra, esce o gira.

| Macro | Ruolo |
|---|---|
| `decisioni/` | centro decisionale: cosa e' stato deciso, cosa e' aperto, dove va cio' che entra |
| `motore/` | cio' che serve per lavorare: codice, test, dati, metodo |
| `magazzino/` | teoria, fonti grezze immutabili, registro degli studi (una cartella per famiglia) |
| `esercizio/` | cio' che gira con soldi veri o in demo |
| `uscita/` | pacchetti per i soci |

**La migrazione e' in corso**, una macro alla volta (DECISIONS 2026-11-09). Dove sta ogni cosa *oggi* lo dice il
[README](README.md); il catasto completo e' nella [mappa](mappa/00-panoramica-trad.md).

## Repo esterni di riferimento (audit del 2026-05-31)

La maggior parte sono fork di studio, non codice da integrare; l'integrazione segue le priorita' in `DECISIONS.md`.

| Repo | Ruolo |
|---|---|
| `OctoBot` | esecuzione crypto, **dormiente** dal 2026-06-14 |
| `worldmonitor` | dashboard macro e geopolitica; senza storico datato, non regge un backtest (DECISIONS 2026-10-25 (3)) |
| `claude-trading-skills` | catalogo di skill di trading, fonte di `fondamenti_tecnici/blueprints/` |
| `ai-hedge-fund`, `TradingAgents`, `dexter`, `paperclip-zero-human-trading-firm`, `AI_Stock_Trading` | pattern multi-agente e design di bot (studio) |
| `pybroker`, `Q-Fin`, `Kronos` | backtester, utility quantitative, modello di base su OHLCV (riferimento) |
| `QuantDinger`, `FinceptTerminal`, `Vibe-Trading` | piattaforme di riferimento (studio) |
| `tradingview-mcp` | valutato e rimandato: legge solo oggetti Pine |
| `second-brain`, `claudian` e tooling AI generico | riferimento |
