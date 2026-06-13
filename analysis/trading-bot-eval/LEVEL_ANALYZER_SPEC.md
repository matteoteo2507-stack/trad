# Level Analyzer — Spec & Report di validazione

> Versione finale validata · XAU spot · 2026-06-13
> Harness e dati: `analysis/trading-bot-eval/` · Port logica livelli: `analysis/veltrix/levels_engine.py`

## 1. Contesto e obiettivo

Si voleva uno strumento che evidenzi **livelli di prezzo operativi con un bias e un
RR misurati** (entry, SL, TP) — non un oracolo direzionale. Il punto di partenza era
il bot del socio (`alphaflowgpt-crypto/trading-bot`, motore VELTRIX). L'indagine ha
prima **escluso** la strada direzionale, poi **validato** quella dei livelli.

## 2. Il percorso (cosa è stato provato e con quali numeri)

| Fase | Test | Esito |
|---|---|---|
| Direzione | Bot as-is / logica pulita OOS / macro DXY+yields | **~50%, nessun edge** (3 angoli indipendenti) |
| Pivot livelli | Fade al primo touch, drift control, **13 anni** spot | **+0.10R, edge +0.25 vs random**, regime-stabile |
| Sweep+reclaim | Filtro contesto (H1, entry al reclaim) | **Bocciato** (−0.04R; impl. cruda, va testato su M5) |
| Confluenza | Cluster di nature → zone, bucket per grado | **conf=2 = sweet spot**; conf=3+ (congestione) = male |
| Cross-asset + CI | conf=2 isolato, CI bootstrap, XAU/BTC/EUR | **significativo 9/9 celle** (CI diff esclude 0) |
| Gate costi | Spread reale broker (XAU $0.10, EUR 1.1pip), 2× | **XAU sopravvive, EUR muore, BTC marginale** |

## 3. L'edge validato (netto costi)

Fade su **zone a confluenza esattamente = 2 nature** (2 livelli di natura diversa che
coincidono), SL = 0.5×ATR(H1), su 13 anni di XAU spot (n=898 trade conf=2):

| Asset | RR | E[R] netto | CI 95% | Edge vs random | Robustezza |
|---|---|---|---|---|---|
| **XAU** | 1:1.5 | **+0.15 R** | [+0.07, +0.24] | +0.39 (sig.) | 3 epoche OK; recente +0.19 |
| **XAU** | 1:2 | **+0.19 R** | [+0.09, +0.29] | +0.39 (sig.) | recente 2023-26 **+0.22** |
| **BTC** | 1:1.5 | **+0.09 R** | [+0.02, +0.16] | +0.40 (sig.) | **6y spot, spread reale $13; recente +0.17** |
| EUR | 1:1.5 | −0.23 R | [−0.35, −0.10] | +0.20 (sig.) | edge reale ma **mangiato dallo spread** |

**Conclusione:** l'edge `conf=2` è reale, significativo e **sopravvive ai costi reali su DUE
asset diversi**: **XAU** (~**+0.15÷+0.19 R** netti, 13y) e **BTC** (**+0.09 R** netto a RR1.5,
6y/2 regimi, spread reale $13, recente +0.17R). **EUR è fuori** (edge reale ma troppo sottile
vs spread). Generalizzazione forte (metallo + crypto, multi-regime, netto costi).

## 4. Spec del Level Analyzer (versione finale)

**Asset:** XAUUSD + BTCUSD (entrambi validati al netto dei costi reali; BTC via demo MT5
First Prudential Markets, spread $13). EURUSD escluso. **RR primario 1:1.5** (cross-asset il più
robusto netto; RR1:2 ok su XAU; RR1:3 muore su BTC).

**Pipeline:**
1. **Detect nature di livello** (su finestra H1 chiusa + daily precedente):
   PDH/PDL, swing S/R (`get_key_levels`), order block (`detect_order_blocks`),
   FVG (`detect_fvg`). [Già in `levels_engine.py`.]
2. **Cluster in zone** con `cluster_confluence(tol_pct≈0.25%)` → ogni zona ha
   `price`, `side` (SUPPORT/RESISTANCE), `confluence` (n. nature).
3. **Selezione:** tieni **solo zone con `confluence == 2`**. Scarta conf=1 (debole) e
   **conf=3+** (congestione, edge negativo).
4. **Trade per zona:** fade — long su SUPPORT, short su RESISTANCE.
   - Entry: al primo touch della zona.
   - **SL = 0.5 × ATR(H1,14)** oltre il livello.
   - **TP = RR × SL**, con **RR 1:1.5–2** (1:3 cala).
5. **Output:** `{zona, lato, entry, SL, TP, RR, score=confluence, contesto}`.

**Parametri chiave:** `cluster_tol=0.25%`, `K_SL=0.5×ATR`, `touch_tol=0.10×ATR`,
`RR∈{1.5,2}`, finestra H1 = ultime ~120 barre, sessione 06–21 UTC.

## 5. Caveat (onestà)

- **Edge sottile in assoluto** (+0.15-0.19R netti): è un edge da **disciplina + volume di
  trade**, non un colpo grosso. Va gestito con sizing rigoroso (rischio fisso per trade).
- **Spread storici:** il gate costi usa lo spread **attuale** ($0.10); nel 2013-2018 erano
  più larghi → il netto delle epoche vecchie è **ottimistico**. Il dato affidabile è il
  **regime recente (2023-2026): +0.19/+0.22R netti**.
- **Path su H1:** risoluzione coarse (conservativa, simmetrica reale/random). Una verifica
  su M5 affinerebbe le stime.
- **conf=2 n modesto** su BTC/EUR (455/384); XAU solido (898).
- **Non ancora forward-tested:** prima di soldi veri serve paper/forward su demo.

## 6. Prossimi passi

1. ✅ **BTC confermato** (demo4 FPM, spread $13, 6y spot): +0.09R netto RR1.5, recente +0.17R.
2. **Implementare l'analyzer live**: emette in tempo reale le zone `conf=2` con lato/SL/TP/RR
   (riusa i detector di `confluence_auto` + il filtro conf=2; dati **spot**, non futures).
3. **Forward/paper test** su demo (≥50 trade) prima di qualunque size reale.
4. Opzionale: test sweep+reclaim **fatto bene su M5** (entry su retest) come possibile
   amplificatore aggiuntivo.

## 7. Riproducibilità (file)

- `export_mt5_spot.py` — export spot XAU/EUR da MT5 (H1 2012+, D1 2004+).
- `fetch_ohlc.py` — fallback dati (Yahoo) per BTC e cross-check.
- `expectancy_levels_long.py` — baseline fade livello-nudo, 13 anni, drift control.
- `expectancy_confluence.py` — selezione per confluenza + CI bootstrap + gate costi (env `COST_PRICE`).
- `expectancy_sweep.py` — test sweep+reclaim (bocciato, conservato).
- `session_ci.py`, `reconstruct_baseline.py`, `macro_xau.py` — fase direzionale (archivio).
