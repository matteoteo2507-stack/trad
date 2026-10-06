---
name: pipeline-prop
description: Esegue e interpreta le fasi della pipeline prop-lab (qualitativo senza costi → costi reali → prop con regole e profili di rischio statici/decrescenti col drawdown → conferma OOS). Usala per lanciare/rilanciare una fase, confrontare gestioni del rischio, cambiare regole prop o leggere i risultati di un run.
---

# Skill: pipeline prop

## Comandi
```
python -m lab.cli all     --family F --symbol S --data data/S_TF.csv   # tutto
python -m lab.cli new     --family F --symbol S --data …               # crea run
python -m lab.cli stage1|stage2|stage3|confirm|report --run results/<run_id>
```
Ogni fase legge i file della precedente: per provare **nuovi profili di rischio o regole prop**
modifica `config/risk_profiles.yaml` / `config/prop_rules.yaml` e rilancia SOLO `stage3` (+ `confirm`).

## Come leggere i risultati
**Fase 1 (`stage1_famiglia.csv`, `stage1_qualitativo.csv`)** — vantaggio lordo.
`plateau_r` = media della variante e dei suoi vicini di griglia: se è molto più bassa dell'expectancy,
è un picco isolato → sospetto overfitting. `score` premia t-stat alto E plateau stabile.

**Fase 2 (`stage2_costi.csv`)** — `cost_share` = quota del vantaggio mangiata dai costi.
Sopra ~50% la strategia è fragile: basta uno spread un po' più largo per azzerarla. Prova
`spread_mult: 1.5` in `config/symbols.yaml` come stress test.

**Fase 3 (`stage3_prop.csv`, `stage3_rischio_pivot.csv`)** — la parte più importante.
- `pass_rate` (tutte le fasi), `fail_daily`, `fail_max`, `timeout`, `median_days`
- `ev_attempt` = payout attesi nel funded − fee (in valuta del conto). **Non si legge da solo**: `pass_zero` e
  `ev_zero` sono gli stessi numeri con i trade a vantaggio zero, e `ev_vs_zero` = `ev_attempt` − `ev_zero` e' la
  parte dovuta al vantaggio. I profili si scelgono su `ev_vs_zero` (06/10: a vantaggio zero EV ~+1.900)
- Il pivot mostra il pass rate medio per **modello di rischio × rischio base**:
  rischio troppo basso → timeout; troppo alto → fail_max/fail_daily. Cerca la zona dove il pass rate
  è alto e **stabile** fra rischi vicini, non il massimo puntuale.
- Confronta statico vs DD-lineare vs scaglioni: i modelli decrescenti dovrebbero ridurre `fail_max`
  a parità di rischio base; se riducono anche molto il pass rate (più timeout), il rischio base va alzato.

**Fase 4 (`conferma_oos.csv`, `conferma_prop_oos.csv`)**
- `exp_oos` > 0 e coerente con `exp_is` → il vantaggio regge
- `dsr_is` (Deflated Sharpe) corregge per il numero di varianti provate (`trials`): è severo apposta
- verdetto (dal 07/10): **PROMOSSA** (limite basso dell'intervallo OOS > 0, corretto per il numero di candidati; il DSR si riporta come diagnostica, non e' richiesto) · **NON_DIMOSTRATA** (l'intervallo contiene lo zero o il DSR non regge: **non va in demo**, e non si scrive "refutata": si riporta `mde_oos`) · **SCARTATA** (intervallo OOS tutto sotto zero). Il vecchio DA_OSSERVARE usciva anche su rumore puro, 5 random walk su 8

## Per l'utente
Riassumi sempre: quali strategie della famiglia sopravvivono a ogni cancello, quale gestione del rischio
massimizza pass rate/EV per ogni regola prop, cosa cambia fra IS e OOS, e i prossimi passi
(incubazione in demo, più dati, altri simboli). Per analisi approfondite del rischio usa l'agente `prop-risk-manager`.
Se i dati sono `DEMO_*`, dillo chiaramente: i numeri non significano nulla.
