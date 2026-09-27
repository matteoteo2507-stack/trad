---
tipo: preregistrazione
stato: NO-GO
aggiornato: 2026-09-18
decisione: "DECISIONS 2026-09-18 (5) — audit A5"
metrica_corrente: "SPX500 TRAIN −0,267 [−0,391; −0,121]; NAS100 MDE 0,135R"
nota: "Audit A5: MISTO — SPX500 refutato, NAS100 mai misurato con potenza sufficiente. Forward ORB spento il 27/08."
---
# Opening-Range Breakout + Retest (US100 M5) — PRE-REGISTRAZIONE

> **Committata PRIMA dei risultati.** 2026-07-08. Primo test del filone **scalping single-asset intraday**
> (idea utente + socio). Le **regole core** sono fissate qui a priori: dopo i numeri non si toccano. La
> **validazione** sale a gradini: **v1 grezza** (capire il potenziale) → v2 piena se promette. Riusa
> `core/quant_metrics.py`. Asset: **US100** (Nasdaq 100 CFD); validazione OOS su **US500**.

## Idea e razionale
Breakout dell'**opening range** dell'**apertura del cash USA** (09:30 ET) con **entry sul retest**.
Razionale microstrutturale reale: l'asta di apertura inietta volatilità e order flow; la rottura del
range di apertura, poi ri-testata, può dare continuazione. Meccanica, **un solo trade/giorno**, pochi
parametri, 1:2 fisso, niente BE → **bassa superficie di overfitting** (lo spirito giusto).

## Timeframe, sessione, fuso
- **M5** (candele 5 minuti), asset **US100**.
- **Opening range (OR)**: **09:30–10:00 ET** (= 15:30–16:00 Roma) = **6 candele M5**. Si segnano
  **ORH** (massimo assoluto) e **ORL** (minimo assoluto) di quelle 6 candele.
- **Ancora = apertura USA 09:30 ET** (non l'ora di Roma fissa): conversione DST-correct via
  timezone `America/New_York` (i timestamp broker sono in ora server; allineamento gestito e
  **verificato empiricamente** nel codice via profilo di volatilità intraday).
- Il **pending scade alle 16:00 ET (22:00 Roma)** = chiusura cash USA; se non riempito → nessun trade.

## Regole (lato SELL; il BUY è lo specchio esatto)
1. **Dalle 10:00 ET**: si attende il **primo** break di ORH o ORL. **Break = candela M5 che CHIUDE oltre
   il livello** (chiusura < ORL per il sell; chiusura > ORH per il buy). Il **primo** break decide il lato;
   l'altro scenario si **ignora** (un solo trade).
2. Sia **C0** la candela che ha rotto ORL. Si fissa **L = low(C0)** e **SLref = high(C0)**.
3. Si attende che **L** venga rotto, candela per candela (dalle successive a C0):
   - se una candela **CHIUDE < L** → **BREAK confermato** (stop attesa);
   - se una candela **passa ma non rompe** (`low < L` ma `close ≥ L`, cioè wick sotto senza chiusura) →
     **si aggiorna** `L = low(candela)` e si continua ad attendere;
   - altrimenti si continua.
4. Al break confermato: si piazza **SELL LIMIT (retest) al livello L rotto**.
   - **SL** = `SLref + BUFFER`, con **BUFFER = 6 punti** (indice).  *(6 "pips" utente = 6 punti US100; da
     verificare col tick del broker sui dati esportati.)*
   - **Rischio** = `SL − L`. **TP** = `L − 2·Rischio` (**1:2 fisso**).
5. **Fill**: il SELL LIMIT si riempie se una candela successiva ha `high ≥ L` (retest) entro le 16:00 ET;
   altrimenti scade (nessun trade).
6. In posizione: **niente BE**, si tiene fino a **TP o SL** (nessun time-stop). Si riporta la durata
   tipica dell'hold (per capire se resta intraday o va overnight).

*(BUY: OR-break = chiusura > ORH; C0 = candela che rompe ORH; H = high(C0), SLref = low(C0); si attende
chiusura > H, con update `H = high` sui wick-sopra-senza-chiusura; BUY LIMIT a H; SL = SLref − BUFFER;
TP = H + 2·(H − SL).)*

## Costi e realismo (dentro dal primo minuto)
- **Spread/slippage** US100: applicato a entry e uscita (stima da dati; default ~1.5 punti round-trip,
  ri-tarabile dal tick reale). **Ambiguità intrabar**: se una candela M5 tocca sia TP sia SL, si
  riportano **due scenari** — pessimistico (SL prima) e ottimistico (TP prima) → bound onesti.
- Look-ahead-safe: OR e break usano **candele chiuse**; il fill e la risoluzione TP/SL su candele
  successive.

## Validazione a gradini
- **v1 (GREZZA, questo giro):** niente filtro news; costi onesti; look-ahead-safe. Metriche: n trade,
  win-rate, **E[R]** (dopo costi, bound pess/opt), profit factor, equity, **per-anno**, durata hold,
  distribuzione R. Split **train/test temporale** per un primo out-of-sample. Scopo: **capire se c'è
  potenziale**, non emettere GO.
- **v2 (se promette):** **guardrail news** (esclusione giorni FOMC/CPI/NFP, lista pre-registrata);
  **DSR** (conteggio onesto dei trial); **purged/embargoed CV** (`cpcv_splits`); **US500 OOS** (stessa
  regola, stessa apertura USA); **forward** paper. Solo allora un verdetto GO/NO-GO.

## Criteri di potenziale (v1, a priori)
Si passa a v2 se, dopo costi (scenario **pessimistico**): **E[R] > 0** con **BCa lower-bound > 0** e
**maggioranza di anni positivi** e win-rate coerente col 1:2 (break-even ~33%). Altrimenti NO-GO grezzo.

## Anti-overfitting (vincolante, essendo single-asset)
Regole core, OR-window, BUFFER, TP, definizione di "rompere" = **fissati qui**. Nessun tuning post-hoc.
Antidoto alla mancanza di breadth: **US500 OOS + forward obbligatori** prima di credere a qualsiasi
risultato. Ogni parametro cambiato dopo i numeri = nuovo trial dichiarato nel DSR.
