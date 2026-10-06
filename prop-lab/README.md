# prop-lab

Dall'**idea grezza** (una famiglia di strategie) alla **prop**, con cancelli espliciti:

```
famiglia (es. mean reversion)
   │  skill famiglia-strategie: ricerca su GitHub/X/libri → catalogo → codice con griglie di parametri
   ▼
FASE 1  backtest IDEALE (no spread/commissioni/swap) di TUTTE le varianti  → c'è un vantaggio lordo diffuso?
   ▼
FASE 2  stesse varianti con costi reali (spread bid/ask da MT5, commissioni, slippage, swap)  → sopravvive ai costi?
   ▼
FASE 3  candidati × regole prop × profili di rischio (statico, DD-lineare, scaglioni, streak, guardia giornaliera, …)
        Monte Carlo di challenge complete + funded  → pass rate, cause di fallimento, giorni, EV per tentativo
   ▼
FASE 4  conferma sul periodo OUT-OF-SAMPLE mai visto + Deflated Sharpe  → PROMOSSA / DA_OSSERVARE / SCARTATA
```

## Avvio rapido
```bash
pip install pandas numpy scipy pyyaml tabulate
python tools/make_demo_data.py          # i CSV non sono in git: rigenera data/DEMO_XAUUSD_H1.csv (identico)
python tests/test_core.py && python tests/test_lookahead.py
python -m lab.cli list
python -m lab.cli all --family mean_reversion --symbol XAUUSD --data data/DEMO_XAUUSD_H1.csv
```
Poi apri la cartella con **Claude Code**: legge `CLAUDE.md`, ha le skill `famiglia-strategie` e `pipeline-prop`
e gli agenti `quant-reviewer` e `prop-risk-manager`. Esempi di richieste:
- "usa la skill famiglia-strategie per *breakout* su XAUUSD H1"
- "rilancia la fase 3 con rischio 2–4% e un profilo che dimezza dopo -3% dal picco"
- "chiedi al prop-risk-manager di analizzare l'ultimo run"

## I tuoi dati MT5
In MT5: *Visualizza → Simboli → Barre* (oppure Ctrl+U), scegli simbolo e timeframe, **Esporta barre**.
Salva in `data/XAUUSD_H1.csv`. Il file contiene `<SPREAD>` per barra: viene usato nei costi.
Più storia = meglio (almeno 3–5 anni su H1; per M5/M15 almeno 1–2 anni).

## Da configurare prima di fidarti dei numeri
- `config/symbols.yaml` → specifiche reali (point, contract size, commissioni, swap) del tuo broker/prop
- `config/prop_rules.yaml` → regole reali della tua prop (target, daily, max loss, trailing, consistency, fee)
- `config/pipeline.yaml` → soglie dei cancelli
- `config/risk_profiles.yaml` → gestioni del rischio da confrontare

## Come si legge un risultato prop (aggiunto in trad, 06/10/2026)
- **Mai l'EV da solo.** La challenge e' un'opzione: a vantaggio zero il profilo guardia giornaliera al 3% passava
  ~30% e aveva EV ~+1.900 per tentativo. Si legge `ev_vs_zero` (EV meno lo stesso EV a vantaggio zero), e per un
  candidato vero `lab.prop.evaluate_ci`, che aggiunge l'incertezza di stima.
- `DA_OSSERVARE` vuol dire "non dimostrato": su rumore puro esce in 5 serie su 8 (misura del 05/10).
- Su Windows: se il pool di processi da' problemi, `PROPLAB_WORKERS=1`.
- Cosa e' cambiato e perche': `CHANGELOG.md`. In `trad` la cartella e' raggiunta da `core/prop_sim.py`.

## Approssimazioni dichiarate
- motore bar-by-bar: se SL e TP sono nella stessa barra conta lo SL (conservativo); niente tick
- DD intraday nella prop stimato con la MAE del trade; una posizione alla volta per strategia
- i dati `DEMO_*` sono **sintetici**: servono solo a verificare che la pipeline giri

## Prossimi passi possibili
portafoglio di più strategie sullo stesso conto · motore multi-simbolo · filtro news ·
walk-forward ancorato con ri-ottimizzazione periodica · export della strategia promossa in EA MQL5 ·
collegamento al tuo sito con copier/dashboard MT5
