# prop-lab — istruzioni per Claude Code

Ambiente per trasformare un'**idea grezza = famiglia di strategie** (es. "mean reversion") in
strategie **meccaniche, testate e dimensionate per una prop**.

## Il flusso (sempre in quest'ordine)

| Fase | Cosa | Comando | Output in `results/<run>/` |
|---|---|---|---|
| 0 Famiglia | ricerca di TUTTE le varianti note → codice in `lab/strategies/<famiglia>.py` | skill `famiglia-strategie` | `research/families/<famiglia>/catalogo.md` |
| 1 Qualitativo | backtest IDEALE di ogni variante, **senza** spread/commissioni/swap | `python -m lab.cli stage1 --run …` | `stage1_famiglia.csv`, `stage1_qualitativo.csv` |
| 2 Costi | le sopravvissute con spread bid/ask, commissioni, slippage, swap | `stage2` | `stage2_costi.csv` |
| 3 Prop × rischio | ogni candidato × ogni regola prop × ogni profilo di rischio (statico, DD-lineare, scaglioni, …) | `stage3` | `stage3_prop.csv`, `stage3_rischio_pivot.csv` |
| 4 Conferma | periodo OOS mai visto + Deflated Sharpe + prop su OOS coi profili scelti in IS | `confirm` | `conferma_oos.csv`, `report.md` |

Tutto in una volta: `python -m lab.cli all --family <famiglia> --symbol XAUUSD --data data/XAUUSD_H1.csv`

## Regole non negoziabili
1. **Niente look-ahead**: segnale a chiusura barra i, ingresso all'open di i+1. Mai `shift(-1)`, `center=True`, livelli del giorno corrente usati prima che il giorno finisca.
2. **Ogni strategia ha uno stop** (`sl_dist > 0`): tutto è in R, il rischio lo decide la fase 3.
3. **L'OOS non si guarda** prima della fase 4. Non modificare parametri/griglie dopo aver visto l'OOS: se lo fai, crea un nuovo run e dichiaralo.
4. **Ogni tentativo è registrato** (`results/registry.sqlite`): il Deflated Sharpe usa quel conteggio. Non cancellare il registro per "migliorare" i numeri.
5. I costi (`config/symbols.yaml`) e le regole prop (`config/prop_rules.yaml`) sono **esempi**: prima di conclusioni operative vanno allineati al broker/prop reali dell'utente.
6. Dopo aver scritto o modificato una strategia → fai controllare il codice dall'agente `quant-reviewer`.
7. Per analizzare la fase 3 o proporre nuovi profili di rischio → agente `prop-risk-manager`.
8. **Nessun EV senza il benchmark a vantaggio zero** (`pass_zero`, `ev_zero`, `ev_vs_zero`; per un candidato
   vero `lab.prop.evaluate_ci`). La challenge e' un'opzione: anche chi non ha vantaggio ha EV positivo con
   rischio alto. `DA_OSSERVARE` = "non dimostrato" (esce anche su rumore puro).
9. Questa cartella vive anche dentro il repo `trad` (`prop-lab/`): ogni modifica va in `CHANGELOG.md`.
   In `trad` valgono in piu' le regole di `trad/CLAUDE.md` e `docs/STRATEGY_LIFECYCLE.md` (§4quater: verdetto
   solo sul binario a rischio fisso 1R, overlay dalla libreria dichiarata in `core/sizing.py`).

## Struttura
- `lab/data.py` loader CSV MT5 (orario server, usa la colonna `<SPREAD>` se presente)
- `lab/backtest.py` motore bar-by-bar in R (SL prima del TP nella stessa barra, gap oltre lo stop)
- `lab/metrics.py` metriche, plateau dei parametri, Deflated Sharpe
- `lab/strategies/` una famiglia per file (`base.py` = interfaccia)
- `lab/risk.py` modelli di rischio componibili · `lab/prop.py` simulatore challenge + funded
- `config/` soglie dei cancelli, simboli/costi, regole prop, profili di rischio
- `data/` CSV esportati da MT5 (`DEMO_*` = sintetici, solo per verificare che tutto giri)

## Stile
- Rispondi in italiano. Riporta sempre: n trade, expectancy in R, PF, max DD in R, quota dei costi, pass rate
  **accanto a pass_zero**, EV **accanto a ev_vs_zero**.
- Non presentare MAI un risultato su dati `DEMO_*` come se avesse valore di trading.
- Test del motore: `python tests/test_core.py`
