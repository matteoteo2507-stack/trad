# Ricerca livelli — Piano strategico operativo

> **Stato:** piano attivo · 2026-07-05 · scope = **solo trading, qualità dei livelli**.
> Nasce dalla chiusura del conf=2 fade ([DECISIONS.md 2026-07-05](../DECISIONS.md)): rifondare
> **quali criteri trovano livelli dove il mercato reagisce davvero**, con rigore, prima di
> ricostruire qualsiasi strategia.

## Context
Il fade conf=2 è NO-GO (forward −0.37R; misura diretta: i livelli non battono il random; reverse
catastrofico). La lezione: il "blob" conf=2 mescolava metà livelli fasulli e meccanica grezza.
Ora testiamo **ogni concetto di livello singolarmente**, misurando la **reazione-vs-random** (la
qualità del livello, scollegata dal trade), su **molti asset**, con protocollo scritto a priori.
La scelta è critica perché **condiziona i dati** su cui si baseranno le conclusioni.

## Scelte confermate (utente)
- **Universo ampio ~15-20 asset** — la breadth è l'antidoto all'overfitting.
- **Dati spot puliti da MT5** dove possibile (FX + oro come li esegue l'utente); crypto/indici da
  exchange/yfinance. Niente futures/composito silenzioso (la lezione GC=F).
- **Concetti volume-based inclusi (POC/VWAP/TPO)**, MA su FX/oro il volume è **tick-volume proxy**
  → risultati marcati "proxy, confidenza inferiore", non mescolati coi concetti OHLC puri.

## Parte 1 — Pitfall da presidiare
**Generazione concetti:** confirmation bias narrativo (testarli TUTTI, riportarli tutti) · una
definizione per concetto fissata a priori dai materiali (mai "shoppare" la definizione) · marcare i
requisiti-dato.
**Estrazione:** distillation drift (usare i *principles*, non il port del bot; annotare divergenze) ·
conflitti di modello (S/R rafforza vs S/D consuma → mappa dei modelli, stratificare per touch) ·
non meccanizzare il discrezionale.
**Esecuzione (dove muore tutto):**
1. **Multiple testing / cherry-picking** → pre-registrare tutto, matrice completa, DSR/PBO col vero
   numero di trial, verdetto per **breadth** (% di asset), non miglior asset.
2. **Tolleranza/zona = DoF (mercati sporchi)** → una tolleranza **ATR-relativa fissa**, uguale su
   tutti; la sensibilità è check di robustezza, non leva di tuning.
3. **Random baseline** → **distance-matched** (stessa distribuzione di distanza-al-touch dei reali);
   il random naïve è confondato (Agent C).
4. **Look-ahead / repaint** → livelli solo da **barre chiuse**, snapshot pre-decisione
   (`validate_levels.py` è look-ahead-safe).
5. **In-sample ≠ forward** → holdout temporale train/test + forward per i sopravvissuti.
6. **Clustering** → block-bootstrap sui giorni, `n_eff` = giorni distinti.
7. **Dati sporchi/inappropriati** → spot non futures, sorgente documentata per asset, tick-volume
   marcato proxy.
8. **Circolarità/leakage** → separare la finestra di *detection* del livello da quella di *misura*
   della reazione.
9. **"Reazione" ≠ "trade"** → v1 misura solo la qualità del livello, non entry/SL/TP.
10. **Universo/regime unico** → universo a priori, storia lunga multi-regime, stratificare per regime.

## Parte 2 — Catalogo dei concetti (dal repo)
| Famiglia | Concetto | Detector | Dato | Note |
|---|---|---|---|---|
| Price structure | Swing S/R (pivot 3 candele) | `levels_engine.get_key_levels`, `confluence_auto/sr.py` | OHLC | ✅ |
| | PDH/PDL/PDC (+ PWH/PWL) | `levels_engine` | OHLC | ✅ |
| | Round number / psicologici | da scrivere (banale) | prezzo | — |
| Liquidity/SMC | Order Block | `levels_engine.detect_order_blocks`, `sd.py` | OHLC | ✅ (miglior forward 33%) |
| | FVG / imbalance | `levels_engine.detect_fvg` | OHLC | ✅ (peggiore forward 5%) |
| | Supply/Demand (DBR/RBR/RBD/DBD) | `confluence_auto/sd.py` | OHLC | ✅ |
| | EQH/EQL (pool liquidità) | da scrivere (da 02) | OHLC | — |
| | Sweep + reclaim | `expectancy_sweep.py` (crudo) | OHLC | rifare pulito |
| | Breaker / mitigation | da scrivere (da 02) | OHLC | — |
| Volume | POC / VAH / VAL / HVN / LVN | `confluence_auto/detectors/poc.py` | volume | ⚠️ tick-proxy su FX |
| | Market Profile / TPO | da candidata `nyse_scalping` | volume/tempo | ⚠️ proxy |
| VWAP | VWAP / Anchored VWAP | da scrivere | volume | ⚠️ proxy |
| Derivati | Fibonacci retracement | da scrivere | OHLC | bassa priorità |
| | Session / opening range | da candidata NYSE | OHLC+orari | — |
| Meta | Confluenza (2+ a **nature distinte**) | `confluence_auto/confluence.py` | — | ri-testare corretto |

## Parte 3 — Orchestrazione (protocollo a priori)
Motore unico riusabile (base: `analysis/veltrix/validate_levels.py` reazione-vs-random look-ahead-safe
+ `analysis/trading-bot-eval/level_reaction_analysis.py` tassonomia). Per ogni **asset × concetto**:
rileva livelli (barre chiuse) → classifica ogni avvicinamento **REACTION / BREAK / NO_TEST /
SWEEP→BREAK** (criteri/soglie ATR-relative dell'Agent A, fissi) → confronta col **random
distance-matched**.
- **Pre-registrazione** (lista concetti + una definizione + soglie + universo + metrica) *prima* dei
  risultati.
- **Metrica**: %REACTION reale vs random + escursione netta mediana (ATR), **block-bootstrap CI sui
  giorni** + **DSR** sul numero di trial.
- **Verdetto per breadth**: su quanti asset il concetto batte il random (CI diff esclude 0).
- **Holdout** train/test per asset; **forward** per i sopravvissuti (la macchina già costruita).
- **Stratificazione** regime + touch-count (mappa dei modelli).
- **Output**: matrice **concetto × asset** ("batte il random? di quanto?") + verdetto di breadth.
  Se **nessun** concetto regge → mercato efficiente qui → pivot (ortogonalità/passivo). Se **uno-due**
  reggono → sono i criteri veri su cui costruire.

## Fasi di esecuzione
0. **Acquisizione dati (gating, azione utente):** export MT5 spot di ~15-20 simboli (H1+D1 **con
   tick_volume**) via `analysis/trading-bot-eval/export_mt5_spot.py` esteso; crypto/indici da
   exchange/yfinance. Simboli broker-specifici → lista configurabile.
1. **Detector v1**: riusare gli esistenti (swing/PD/OB/FVG/S-D/POC) + aggiungere i mancanti
   OHLC-puri (round number, EQH/EQL, sweep pulito, session).
2. **Motore reazione-vs-random** generalizzato multi-asset multi-concetto (estende
   `level_reaction_analysis.py`).
3. **Run della matrice** concetto × asset, con holdout + block-bootstrap + DSR.
4. **Forward-validazione** dei sopravvissuti sulla macchina live.

## Verifica
- Pre-registrazione committata *prima* di guardare i numeri (anti p-hacking).
- Ogni cella riporta n, `n_eff` (giorni), CI vs random distance-matched; verdetto per breadth.
- Concetti volume marcati "proxy"; niente mix futures/spot.
- Nessuna definizione/soglia cambiata dopo aver visto i risultati (o si documenta come nuovo trial).
