# decisioni — il centro decisionale

Prima macro del repo in ordine di processo (DECISIONS 2026-11-09): qui entra il materiale nuovo, qui si decide cosa
farne, e qui sta lo stato di tutto cio' che e' stato deciso.

| In ordine di processo | File | Cosa fa |
|---|---|---|
| 1. Ingresso | [`Da distillare/`](Da%20distillare/README.md) | la cartella d'arrivo del materiale esterno; si tiene il piu' possibile vuota |
| 2. Smistamento | [`_INTAKE.md`](_INTAKE.md) | la porta: ogni fonte nuova, il suo stato e dove e' finita |
| 3. Cosa resta da fare | [`BACKLOG_RICERCA.md`](BACKLOG_RICERCA.md) | strade di ricerca, dati mancanti (§G), debito di protocollo |
| 4. Il registro | [`DECISIONS.md`](DECISIONS.md) | ogni decisione, dalla piu' recente; **la voce piu' recente vince** su tutto |
| 5. Il contatore | [`trial_ledger.json`](trial_ledger.json) | famiglie, trial spesi, budget, motivo di chiusura. Si legge e si verifica con `python -m motore.core.trial_ledger` (`--check`), mai a mano |
| 6. La mappa | [`mappa/`](mappa/00-panoramica-trad.md) | cosa fa ogni componente, il cruscotto e il registro delle modifiche di architettura |

## Regole

- **Un file si colloca per tipo, non per stato.** Un verdetto o una riapertura non spostano file: lo stato vive nel
  frontmatter delle pre-registrazioni e nel contatore.
- **Da fare** (DECISIONS 2026-11-09): il campo `riapre_con` nel contatore, cioe' i dati o la condizione che
  riaprirebbero una famiglia chiusa, e un indice unico generato invece che scritto a mano.
- **Il gatekeeper** (`.claude/agents/quant-gatekeeper.md`) legge contatore e pre-registrazioni prima di ogni test e
  prima di ogni verdetto.
