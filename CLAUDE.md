# trad — istruzioni per Claude

Progetto di ricerca quant di Matteo. Repo git autonomo, annidato nel vault `claude-brain`
(le regole comuni stanno in `../CLAUDE.md` e valgono anche qui).

## Ordine di lettura quando serve uno stato o un numero

1. **Stato canonico** di una famiglia/strategia: frontmatter `stato` della sua pre-registrazione in
   `docs/*_PREREGISTRATION.md` (in migrazione — finché manca, vale il punto 2).
2. **`DECISIONS.md`**: registro cronologico. **La voce più recente vince** su tutto ciò che la precede,
   in qualunque file. Se un altro documento contraddice una voce più recente, è quel documento a
   essere vecchio: segnalalo, non mediare.
3. **Metodo**: `docs/STRATEGY_LIFECYCLE.md` (il loop e i criteri di bocciatura) e
   `docs/QUANT_REVIEW_PROTOCOL.md` (come si misura). Il revisore è `.claude/agents/quant-gatekeeper.md`.
4. **Conteggi di trial e budget**: `python -m core.trial_ledger`, mai numeri a memoria o copiati.

Non citare mai un risultato (R, win rate, N, p) senza la nota sorgente e la data della misura.
`_INTAKE.md`, `docs/README.md`, la memoria e il gatekeeper **non sono fonti** di numeri: puntano.

## Mappa e protocollo modifiche

`mappa/` è la mappa funzionale del sistema, scritta per Matteo (che deve capire tutto il sistema
anche a costo di rallentare). Ogni modifica di architettura — nuovo componente o modulo, regola o
gate, cambio di input/output, file spostato o rimosso, nuovo agente o skill — va, **nella stessa
sessione**:
- riflessa nelle note di `mappa/` coinvolte;
- registrata in `mappa/_modifiche.md` (data, cosa, perché, note toccate, impatto) con stato `da_rivedere`.

Correzioni che non cambiano cosa fa un componente (typo, refactor interno a parità di I/O) non
vanno registrate.

## Convenzioni

Codice: `CONVENTIONS.md`. Principi di trading: `TRADING_PRINCIPLES.md`. Concetti distillati:
`fondamenti_tecnici/` (8 moduli `0X_*/principles.md`). Intake da fonti esterne: `fondamenti_tecnici/_INTAKE.md`.
Credenziali (`.env`, `*.session`) non si leggono, non si stampano, non si spostano.
