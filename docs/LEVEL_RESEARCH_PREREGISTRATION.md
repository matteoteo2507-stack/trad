# Ricerca livelli — PRE-REGISTRAZIONE (anti-p-hacking)

> **Committata PRIMA di guardare i risultati.** 2026-07-06. Contratto scientifico: le definizioni,
> le soglie, l'universo, la metrica, il baseline e la **regola di decisione** qui sotto sono fissati
> *a priori*. Dopo aver visto i numeri **non si cambiano**. Se si scopre un bug, si documenta come
> *fix* (con commit) — non come nuova definizione. Ogni concetto/soglia aggiunto dopo = **nuovo trial**
> dichiarato, che entra nel conteggio DSR. Attua [LEVEL_RESEARCH_PLAN.md](LEVEL_RESEARCH_PLAN.md).

## Domanda (una sola)
Quando il prezzo tocca un livello generato da un concetto **C**, il mercato **REAGISCE** (rimbalzo/
rigetto misurabile) più spesso e più forte che a un punto **arbitrario alla stessa distanza**, e questo
vale su **molti asset**? Misuriamo la *qualità del livello* (reazione-vs-random), **non** un trade
(niente entry/SL/TP in v1).

## Universo (16 asset, fissato) — dati broker demo4 validati (Fase 0)
FX: EURUSD GBPUSD USDJPY AUDUSD USDCAD NZDUSD USDCHF EURJPY.r GBPJPY.r EURGBP.r ·
Metalli: XAUUSD XAGUSD · Crypto: BTCUSD ETHUSD · Indici: US500 US100.
Timeframe: **detection e misura su H1**; PDH/PDL da D1. Storia intera disponibile per asset.

## Concetti testati (v1 = 6, tutti OHLC-puri; volume rimandato a v2 come "proxy")
Una **sola** definizione per concetto, fissata qui:

| # | Concetto | Definizione operativa (a priori) | Side |
|---|---|---|---|
| 1 | **Swing S/R** | Pivot a 3 candele (`levels_engine.get_key_levels`): low < low dei 2 vicini = supporto; high > high dei 2 vicini = resistenza. Ultimi ≤4 per lato nella finestra. | sup/res |
| 2 | **PDH/PDL** | High/Low della D1 precedente. PDL=supporto, PDH=resistenza. | sup/res |
| 3 | **Order Block** | `levels_engine.detect_order_blocks` (ultima candela opposta prima di displacement che chiude oltre il suo estremo entro 2 barre). Livello = mid dell'OB. Bull→sup, Bear→res. | sup/res |
| 4 | **FVG** | `levels_engine.detect_fvg` (imbalance a 3 barre). Livello = mid del gap. Bull→sup, Bear→res. | sup/res |
| 5 | **Round number** | Livelli psicologici a passo fisso per asset (tabella sotto). Round più vicino sopra=res, sotto=sup. | sup/res |
| 6 | **EQH/EQL** | ≥2 pivot high (o low) entro 0.10·ATR = pool di liquidità; livello = media. EQH=res, EQL=sup. | sup/res |

**Passo round-number (fissato):** FX non-JPY = 0.0050; FX JPY (USDJPY/EURJPY/GBPJPY) = 0.50;
EURGBP = 0.0050; XAUUSD = 25; XAGUSD = 0.50; BTCUSD = 1000; ETHUSD = 100; US500 = 25; US100 = 100.

## Soglie e finestre (FISSE — ereditate dall'analisi Agent C, non ottimizzate)
- **ATR** = ATR(H1, 14) alla barra della decisione.
- **Tolleranza touch** = `0.10·ATR` (mercati sporchi: zone, non pip).
- **Finestra touch** = 24 barre H1 dopo il punto di decisione (il livello deve essere toccato entro).
- **Finestra reazione** = 4 barre H1 dopo il primo touch.
- **REACTION** = escursione netta (fav−avv) > 0 **E** favorevole ≥ 1.0·ATR, senza BREAK prima.
- Tassonomia completa: REACTION / TOUCH_NO_REACTION / BREAK / SWEEP_THEN_BREAK / NO_TEST /
  INSUFFICIENT (identica a `classify()` di `level_reaction_analysis.py`, look-ahead-safe).
- **Cadenza decisione** = ogni chiusura D1. **Finestra detection** = ultime 120 barre H1 chiuse
  (≈1 settimana) per swing/OB/FVG/EQH-EQL; PDH/PDL dalla D1 precedente; round dal prezzo.
- **Geometria valida**: supporti solo ≤ prezzo, resistenze solo ≥ prezzo; dedup entro 0.10·ATR
  per concetto/giorno; distanza `d = |livello−prezzo|/ATR > 0`.

## Baseline RANDOM (distance-matched) — il controllo che conta
Per **ogni** livello reale (concetto C, asset A, giorno D, side s, distanza d) genero **M=5** livelli
di controllo: distanza `d'` **campionata dalla distribuzione empirica delle distanze reali** di (C,A)
sullo stesso side, stesso giorno D e stesso prezzo P0(D). Prezzo random = `P0 − d'·ATR` (sup) o
`P0 + d'·ATR` (res); stessa `classify()`. Così il pool random ha **la stessa distribuzione di
distanza-al-touch, lo stesso timing e lo stesso drift** dei reali, ma su posizioni strutturalmente
arbitrarie. (Motivo: Agent C ha mostrato che il random naïve lontano è confondato dal timing del touch.)

## Metrica e verdetto (a priori)
Per ogni cella **(concetto × asset)**:
- **Primaria**: `%REACTION | touch` reale vs random. Differenza + **CI 95% block-bootstrap sui GIORNI**
  (cluster = giorno di decisione; `n_eff` = giorni distinti).
- **Secondaria**: escursione netta mediana (ATR) al primo touch, reale vs random, con CI.
- La cella **"batte il random"** se il CI della differenza `%REACTION` **esclude 0 dal lato positivo**.

**Verdetto per concetto = BREADTH:** frazione di asset su cui batte il random. Un concetto è
**sopravvissuto** se: batte il random su **≥ 50% degli asset** *e* l'effetto poolato è positivo col
CI che esclude 0. (Nessun verdetto sul "miglior asset": è cherry-picking.)

**Correzione molteplicità (DSR/PBO):** T = n_concetti × n_asset trial (v1: 6×16 = 96). Riporto il
numero atteso di "batte" falsi a CI 95% (`0.05·T ≈ 5`) contro gli osservati; un concetto che "vince"
solo su ~5 asset sparsi ≈ rumore. L'effetto poolato per concetto è il test robusto alla molteplicità.

**Holdout temporale:** ogni asset diviso in **TRAIN = 70% giorni più vecchi** / **TEST = 30% più
recenti**. La matrice gira su TRAIN; i concetti sopravvissuti su TRAIN vengono verificati **out-of-sample
su TEST**. Avanza solo chi sopravvive a **entrambi**.

## Regola di decisione (scritta prima dei numeri)
- **≥1 concetto** batte il random con breadth su TRAIN **e** tiene su TEST → sono i **criteri veri** di
  livello → si costruisce sopra lo strato-strategia (forward, Fase 4).
- **Nessun** concetto tiene → mercato efficiente a questa risoluzione → **pivot** (ortogonalità/passivo),
  senza forzare (la lezione conf=2: non inventare edge dove non c'è).

## Impegni anti-overfitting (vincolanti)
1. Nessun tuning di soglia per-asset; una definizione per concetto, fissata qui.
2. Niente concetti aggiunti dopo aver visto i risultati senza dichiararli nuovi trial (DSR aggiornato).
3. Random **distance-matched**; block-bootstrap **sui giorni**; holdout **+** forward per i sopravvissuti.
4. Verdetto per **breadth**, mai per miglior asset; volume marcato "proxy" e tenuto separato (v2).
5. Look-ahead-safe: detection solo su barre chiuse, misura solo su barre successive al punto decisione.

---

## ADDENDUM v2 — concetti VOLUME (2026-07-07, committato PRIMA dei risultati v2)

**Esito v1 (per contesto):** 0/6 concetti OHLC battono il random distance-matched (DECISIONS.md
2026-07-06). La v2 testa l'unica famiglia rimasta: i livelli **volume-based**. Tutto il resto del
protocollo (soglie touch 0.10·ATR, finestra 24, reazione 4, random distance-matched, block-bootstrap
sui giorni, breadth, holdout 70/30, geometria) è **identico alla v1**. Cambiano solo i detector.

**⚠️ Caveat dato (dichiarato a priori):** su TUTTI i 16 asset il "volume" è **tick-volume** (numero di
tick), non volume scambiato reale — proxy (corr. ~0.85-0.90 con volume vero su FX). L'intera v2 è
marcata **"proxy, confidenza inferiore"**; un eventuale segnale andrebbe riconfermato con volume reale.

**3 nuovi concetti (nuovi trial per il DSR), definizione fissa:**

| # | Concetto | Definizione operativa (a priori) | Side |
|---|---|---|---|
| 7 | **POC / VAH / VAL** | Volume profile sulle ultime 120 barre H1: bin di ampiezza **0.20·ATR**, volume di ogni barra distribuito uniformemente sul suo range [low,high]. **POC** = bin a volume max. **Value Area** = 70% del volume attorno al POC; **VAH/VAL** = estremi della VA. 3 livelli, tag `poc`. | posizione |
| 8 | **VWAP** | VWAP rolling sulle ultime 120 barre H1: `Σ(typ·vol)/Σvol`, typ=(H+L+C)/3. 1 livello, tag `vwap`. | posizione |
| 9 | **Anchored VWAP** | 2 AVWAP ancorate agli estremi della finestra (barra del max-high e barra del min-low), calcolate dall'ancora fino a "ora". Tag `avwap`. | posizione |

**Side**: livello ≤ prezzo → SUPPORT, > prezzo → RESISTANCE (poi filtro geometria come v1).
**Volume** = colonna `volume` dei CSV (= tick_volume dell'export MT5).

**Molteplicità aggiornata:** v2 = 3 concetti × 16 asset = **48 trial** (falsi attesi a CI95 ≈ 2.4).
Cumulativo dichiarato v1+v2 = 9 × 16 = **144 trial**. Verdetto v2 per **breadth ≥ 50% + pool CI>0**,
identico alla v1. Se anche il volume nulla → si chiude il libro "livelli come zona di reazione".
