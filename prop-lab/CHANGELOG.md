# Modifiche a prop-lab

`prop-lab` vive in **due repo**: quello del socio VELTRIX e `trad` (cartella `prop-lab/`). Li teniamo
allineati come se fossero uno solo, ma separati per protezione dagli errori (decisione di Matteo, 06/10/2026).
Ogni modifica fatta da una parte si scrive qui, cosi' l'altra parte la riporta.

## 2026-10-07 — fatte in trad (da riportare nel repo del socio)

**Verdetto della conferma OOS (`lab/pipeline.py`, `lab/metrics.py`).** Prima: `DA_OSSERVARE` = attesa OOS > 0
a prescindere dal DSR, e andava in demo; su 8 random walk senza vantaggio usciva in 5. Ora:
- **PROMOSSA** solo se il limite basso dell'intervallo OOS, corretto con Bonferroni per il numero di candidati,
  supera `min_expectancy_r`;
- **NON_DIMOSTRATA** altrimenti (non va in demo; accanto c'e' `mde_oos`, l'effetto minimo che il test poteva vedere);
- **SCARTATA** solo se l'intervallo OOS e' tutto sotto zero.
- Il **DSR non e' piu' richiesto** (`min_dsr: null`), resta come diagnostica. Con DSR >= 0,95 obbligatorio la
  pipeline non promuoveva nemmeno una mean reversion iniettata fortissima (OOS +0,85R, limite basso +0,68R, DSR 0,90).

Controlli (07/10, 204 varianti mean_reversion, 3 anni salvo dove detto):

| serie | promosse con la regola nuova | con DSR >= 0,95 obbligatorio | col vecchio DA_OSSERVARE |
|---|---|---|---|
| 9 random walk (nessun vantaggio) | **0** | 0 | almeno un candidato in demo in 5 su 8 |
| mean reversion iniettata, forza 1 (3 e 10 anni) | 2 su 8 | 0 | — |
| mean reversion iniettata, forza 5 e 15 | **8 su 8** | 0 | — |

**Dati demo (`tools/make_demo_data.py`).** Ora sono due controlli costruiti su un percorso a passi di un minuto
(massimi e minimi veri): `--mode null` (niente da trovare) e `--mode mr` (mean reversion dichiarata, `--forza`).
Prima c'era una sola serie con la mean reversion non dichiarata e massimi/minimi "a baffi" staccati dal percorso,
che regalavano attesa al target vicino. Con la stessa forza dichiarata la mean reversion vera e' debole
(autocorrelazione a 6 ore −0,023): il vantaggio forte dei vecchi demo veniva soprattutto dai baffi.
`docs/esempio_report_DEMO.md` sostituito da `esempio_report_DEMO_NULL.md` e `esempio_report_DEMO_MR.md`.

**Regolamenti (`lab/prop.py`, `config/prop_rules.yaml`).** `regole_mancanti()` elenca i campi mancanti o non
modellati ed `evaluate()` rifiuta di simulare un regolamento incompleto; un costo ignoto da' EV `nan`, non 0.
Aggiunte le voci reali di FTMO, FundedNext e The5ers raccolte da Comet (`stato: da_verificare`): simulabile solo
`ftmo_2step` (pass rate; costo mancante).

**Report.** Il verdetto del candidato accanto a ogni riga prop della conferma; nota che `ev_vs_zero` toglie il
valore d'opzione ma non il caso (sul random walk e' positivo al 100% fuori campione sui candidati usciti fortunati).

**Test:** 13 in `tests/test_core.py`.

## 2026-10-06 — fatte in trad (da riportare nel repo del socio)

**Correzioni (non cambiano nessun numero, verificato):**
- `lab/pipeline.py`: i file YAML e il report si leggono e scrivono in UTF-8. Su Windows il default era cp1252
  e la fase 2 crashava sul primo "⚠️" di `config/symbols.yaml`.
- `lab/pipeline.py`: il pool di processi ha una ricaduta seriale (`_map`). Su Windows moriva a intermittenza con
  `WinError 6 Handle non valido` in fase 2 o in conferma. `PROPLAB_WORKERS=1` forza la serie.
- Verifica: rigirata la pipeline intera sui dati demo, su Windows senza `PYTHONUTF8`. Gli EV della fase 3
  coincidevano al centesimo con `docs/esempio_report_DEMO.md` (rimosso il 07/10, resta nella storia di git) (4.013,60 / 3.470,76 / 2.935,82 / 2.620,86).

**Aggiunte al simulatore (`lab/prop.py`):**
- `zero_edge(day_trades)`: gli stessi trade con attesa zero. Perche': il 05/10 una strategia a vantaggio
  **zero** passava ~30% delle due fasi e aveva EV ~+1.900 per tentativo col profilo guardia giornaliera al 3%.
  La challenge e' un'opzione: un EV positivo da solo non prova niente.
- `evaluate_ci(...)`: pass rate ed EV con l'incertezza di stima (il campione stesso ricampionato) e
  `ev_vs_zero`, la parte di EV dovuta al vantaggio, con il suo intervallo.

**Cambi nella pipeline (cambiano la scelta dei profili, non i backtest):**
- Fase 3: ogni combinazione ha anche `pass_zero`, `ev_zero`, `ev_vs_zero`. Ordinamento e scelta dei profili
  migliori passano da `ev_attempt` a **`ev_vs_zero`**: l'EV grezzo premia il rischio alto anche a vantaggio zero.
- Nuovo pivot `stage3_pivot_ev_vs_zero.csv`; le stesse colonne nella conferma OOS e nel report.

**Test:** 4 nuovi in `tests/test_core.py`, tra cui il controllo che a vantaggio zero, con barriere simmetriche
+10%/−10% e niente timeout, la probabilita' di passare torni 0,5 (rovina del giocatore).

**Dati:** `data/*.csv` fuori da git; i `DEMO_*` si rigenerano identici con `tools/make_demo_data.py`.

**Da sapere, misurato il 05/10** (i primi due punti risolti il 07/10, vedi sopra):
- su 8 random walk senza alcun vantaggio la pipeline intera manda almeno un candidato a `DA_OSSERVARE` in 5 serie
  su 8 (0 `PROMOSSA`, DSR massimo 0,24). `DA_OSSERVARE` significa "non dimostrato", non "promettente";
- i dati `DEMO_*` contengono mean reversion iniettata dal generatore (`tools/make_demo_data.py`, righe 35-36):
  il "DA_OSSERVARE" del report demo e' per costruzione;
- con 204 varianti su ~2 anni di in-sample il DSR puo' diventare significativo solo con Sharpe annuo > 3.
