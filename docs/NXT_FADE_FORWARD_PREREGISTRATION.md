# Pre-registrazione — Forward test FADE mean-reversion (NXT A1)

> **Documento vincolante.** Fissato il **2026-08-04**, con il forward test **già in corso** (EA
> avviato ~2026-07-24). Scopo: bloccare la **regola di stop** e le **soglie di verdetto** prima che
> la dimensione campionaria diventi conosciuta, per impedire l'**optional stopping** — decidere
> quando fermarsi guardando come sta andando. Le regole di questo file **non si modificano** durante
> il test; qualunque modifica va datata, motivata e dichiarata nel report finale.
>
> Ciclo di riferimento: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md).
> Spec operativa immutabile: [fade_mr_walkforward_socio.md](../fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md).

---

## 1. Ipotesi sotto test

**H1**: la variante **FADE** (A1 mirror-fade 1:3) mantiene un'aspettativa positiva in R
**fuori campione**, su dati non usati per generarla.

**H0**: E[R] ≤ 0 — l'edge osservato nel backtest è un artefatto della derivazione dai dati.

**Perché serve.** Il fade è un'ipotesi **data-derived**: è nata invertendo la strategia di
continuazione che perdeva. Ha superato holdout interno e stress sui costi, ma quei test **girano
sugli stessi dati che l'hanno generata** e non possono validarla. Questo forward è l'unica evidenza
indipendente possibile. Stato attuale: **LEAD**, non edge ([STRATEGY_LIFECYCLE §5](STRATEGY_LIFECYCLE.md)).

## 2. Strategia — parametri congelati

Definizione operativa in `analysis/nxt/closure.py` (config **A1**), eseguita da
[`mql5/nxt_fade.mq5`](../mql5/nxt_fade.mq5). Parametri **immutabili** per tutta la durata del test:

| Parametro | Valore |
|---|---|
| Timeframe | H1 |
| Universo | EURUSD, GBPUSD, USDJPY, XAUUSD, US100, US500 |
| Swing | frattale a 5 barre per lato (`K=5`) |
| Filtro trend | HH+HL (uptrend) / LH+LL (downtrend) |
| Filtro dimensione gamba | ≥ 1× ATR(14) H1 |
| Direzione | **contro-trend** (uptrend → short, downtrend → long) |
| Entrata | ritracciamento **50%** della gamba |
| R (unità di rischio) | **28,6%** dell'ampiezza della gamba |
| Stop-loss | 1R dal lato del trend |
| Take-profit | **3R** (rapporto 1:3) |
| Break-even | stop a pareggio a **+2R** |
| Finestra di fill | 48 barre H1 dallo swing |
| Time-stop | ~20 giorni di borsa (`MAX_HOLD`) |
| Vincolo | un solo trade per gamba per strumento |

**Esecuzione**: EA su MT5 demo/VPS. Lo **storico MT5 è la raccolta dati** — nessun journaling
manuale, nessuna discrezionalità nel marcaggio degli swing.

## 3. Regola di stop — DUE STADI (pre-dichiarata)

> **Motivazione.** N=50 è sufficiente a **bocciare**, non a **confermare**. Con la distribuzione R
> attesa dal backtest (win ~31% a 1:3, break-even 25%), la deviazione standard per trade è
> nell'ordine di **~1,8R** → l'errore standard su 50 trade è **~0,26R**. Un E[R] vero di +0,35R
> produrrebbe un intervallo di confidenza al 95% che **attraversa lo zero**: anche se la strategia
> funzionasse esattamente come nel backtest, a 50 trade non potremmo dimostrarlo. Per una conferma
> a potenza 80% servono **~200-220 trade**. Da qui il disegno sequenziale a due soglie, entrambe
> fissate **ora**.
>
> *(La SD va ricalcolata esattamente sul trade log del backtest — `analysis/nxt/closure.py` — e il
> numero dello Stadio 2 aggiornato di conseguenza **prima** che il campione live vi arrivi.)*

### Stadio 1 — GATE DI BOCCIATURA · **N = 50 trade chiusi**

- Si valuta **una sola volta**, al raggiungimento del **50° trade chiuso** (aggregato sui 6 strumenti).
- **Backstop temporale: 2026-10-31.** Vale il primo evento che si verifica.

| Esito a N=50 | Decisione |
|---|---|
| **E[R] ≤ 0** (stima puntuale) | **KILL** — lead archiviato. Nessuna estensione, nessuna rifinitura |
| **Win rate < 25%** (sotto il break-even a 1:3) | **KILL** |
| **E[R] > 0** | **PROSEGUE** allo Stadio 2. Nessuna conclusione positiva dichiarabile qui |

### Stadio 2 — GATE DI CONFERMA · **N = 200 trade chiusi**

- Backstop temporale: **2027-03-31**.

| Esito a N=200 | Decisione |
|---|---|
| **BCa 95% lower bound su E[R] > 0** ([`bca_bootstrap_ci`](../core/quant_metrics.py)) | **GO** → valutazione per capitale, con pre-mortem obbligatorio |
| Altrimenti | **KILL** — il lead non regge, famiglia archiviata |

### Se il campione non arriva

- **N < 50 al 2026-10-31** → **una sola** estensione al **2027-01-31**. Se ancora < 50 → archiviato
  come **INSUFFICIENT DATA / irrisolto**. Nessuna ulteriore estensione.
- **N < 200 al 2027-03-31** → archiviato come **INSUFFICIENT DATA**, non come GO.

## 4. Impegni vincolanti (la parte che fa il lavoro)

1. **Non si prolunga se il verdetto è negativo.** Un E[R] ≤ 0 a N=50 chiude il lead. "Raccogliamo
   ancora un po'" è precisamente il bias che questo documento esiste per impedire.
2. **Non si guarda il P&L cumulato per decidere quando valutare.** La regola di stop è N e data, non
   l'aspetto della curva.
3. **Non si modificano i parametri in corsa.** Qualunque modifica **azzera il test** e ne apre uno
   nuovo, con nuovo N e nuova pre-registrazione — non prosegue quello vecchio.
4. **Nessuna rifinitura è disponibile su questo lead.** Il fade ha già consumato il suo ramo di
   ricerca: è nato *come* rifinitura di NXT. Un secondo ritocco sarebbe il secondo giro sugli stessi
   dati ([STRATEGY_LIFECYCLE §4](STRATEGY_LIFECYCLE.md)).
5. **Contatore trial**: il fade è **trial #2** della famiglia NXT (#1 = continuazione, NO-GO). Un
   eventuale terzo tentativo sarebbe l'ultimo prima del kill di budget (3 round).

## 5. Metriche da riportare nel verdetto

Obbligatorie, indipendentemente dall'esito:

- N trade chiusi, per strumento e aggregato · win rate · **E[R] con BCa 95% CI**
- Distribuzione degli esiti (TP / SL / break-even / time-stop) — il BE a +2R sposta massa a 0R e
  **abbassa** l'E[R] rispetto al modello a due esiti
- Breadth: E[R] per strumento (quanti dei 6 sono positivi)
- Confronto col backtest: +0,35R base / +0,24R a 3× costi, win ~31%
- Slippage e spread **reali** vs modellati
- Trade saltati (setup validi non riempiti entro 48 barre) e motivo

## 6. Cosa NON è questo test

- **Non** è una validazione della famiglia NXT/Fibonacci: la continuazione è già **NO-GO** (win
  13,3%, E[R] −0,44R, 14/14 anni e 6/6 asset negativi).
- **Non** è un test su capitale reale: demo/micro, size sperimentale.
- **Non** produce un GO allo Stadio 1, in nessun caso.

## 7. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-04 | Creazione. N=50 (Stadio 1) e N=200 (Stadio 2), backstop e impegni fissati | Test già in corso da ~2026-07-24 senza pre-registrazione |
