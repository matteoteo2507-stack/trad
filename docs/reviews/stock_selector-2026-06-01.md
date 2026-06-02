# Quant Review — Stock Selector V6.0 (dati live raccolti) — 2026-06-01

> Analisi del primo mese di pick reali (5 cross-sezioni: 30-12-2025, 10/17/24/31-05-2026).
> Codice: [strategies/stock_selector/](../../strategies/stock_selector/).
> Dati grezzi: [stoxs picks/](../../stoxs%20picks/). Script: [analysis/](../../strategies/stock_selector/analysis/).
> Output riproducibile: `python -m strategies.stock_selector.analysis.build_dataset && python -m strategies.stock_selector.analysis.analyze`

## Sommario in 5 righe

Selettore cross-sectional SP500: assegna a ogni titolo uno **score fondamentale** (0-6:
D/E, P/E, EPS, MOL, profit margin, ROE>rf), un flag **macro-match** (`SI`/`NO` secondo
scenario derivato da tasso + liquidità: *Difensivo* a dic, *Quality* a maggio) e uno stato
**RRG** (momentum relativo vs benchmark). Buy-list = `score≥4 AND match=SI`. Ipotesi
operativa: ogni lunedì compra 100$ equal-weight di ogni titolo selezionato, **nessuna
regola di uscita**. Frequenza: settimanale, ~90-120 titoli per run (≈ closet-indexing).

## Gradi di libertà

N parametri ≈ **14** calibrati su dati (soglie D/E 0.5/1.0, MOL 0.20/0.10, profit 0.08,
high_rate_threshold 3.0, rs_window 50, momentum_lookback 10, min_history 100, filtri
scenario de_max/beta/roe ×3) + 2 fissati a priori (score≥4, require_match). N varianti
realmente testate fuori campione = **0** (questi sono i primi dati live; il notebook V6.0
implica ≥6 iterazioni "V1→V6" non documentate → per DSR assumere N≥100).

## Verdict

**RAFFINA — con sample insufficiente per qualunque conclusione di edge (né positiva né negativa).**

Motivazione: su 4 coorti utilizzabili la buy-list ha **sottoperformato** il benchmark
equal-weight (RSP) in **tutte e quattro**, e i due segnali differenzianti (score, macro-match)
sono risultati **anti-predittivi** (IC ≤ 0, long-short SI−NO negativo). MA: (a) il campione è
statisticamente nullo, (b) tutta la finestra è **un solo regime risk-on** — esattamente quello
in cui un selettore *difensivo/quality* è progettato per restare indietro. Non possiamo né
promuovere né condannare l'algoritmo; possiamo solo **generare ipotesi di miglioramento**.

## Edge probability

| Metrica | Valore | Note |
|---|---|---|
| PBO (CSCV) | **non calcolabile** | servono ≥16 sotto-periodi di una serie di return continua; abbiamo 4 snapshot |
| DSR | **non calcolabile** | < 50 osservazioni temporali indipendenti |
| Walk-forward OOS | **n/a** | 1 regime, nessun out-of-sample di regime opposto |
| IC score→ret (to-now) | **−0.05 / −0.11 / −0.12 / +0.01** (per data) | media ≈ **−0.07**, segno *sbagliato* |
| IC RRG→ret (4w) | **+0.02 / +0.09 / +0.05 / +0.01** | media ≈ **+0.04**, segno *giusto* ma debole |
| Long-short SI−NO (to-now) | **−6.2% / −1.8% / −2.1% / +0.0%** | il filtro macro ha scelto i *lagging* |
| Alpha buy-list vs RSP (to-now) | **−5.6% / −1.4% / −1.7% / −1.0%** | negativo in 4/4 coorti |

I p-value < 0.05 di alcune celle IC **non vanno creduti**: le osservazioni cross-sezionali
sono fortemente correlate (≈300-500 titoli SP500 nello stesso giorno → N efficace ≪ N
nominale). Senza clustering per data l'inferenza è gonfiata (López de Prado 2018, cap. 7).

### Il fatto centrale, in chiaro

In un regime **risk-on** (RSP +9.7% in 5 mesi dalla coorte di dicembre), hanno corso di più i
titoli che il selettore **scarta**: i bucket di score più basso ("junk") e i `NO` macro hanno
battuto i `SI` quality. Esempi (coorte 30-12, to-now): `NO` +10.2% vs `SI` +3.9%; bucket
score 0-2.5 in media a doppia cifra (rally del junk), score 4-6 a singola cifra. È il
**comportamento da manuale del fattore quality che sottoperforma in un rally di bassa qualità**
— non necessariamente un bug dell'algoritmo.

L'unico componente con segno "giusto" è l'**RRG (momentum relativo)**: gli stati LEADING/
WEAKENING (titoli con RS alto) hanno battuto IMPROVING/LAGGING in più coorti — ma l'RRG
**non entra** nella buy-list, è solo informativo.

## Top 3 rischi

1. **Regime-selection bias nella valutazione stessa** — l'intera finestra dic-2025→giu-2026 è
   un singolo regime risk-on. Concludere "il selettore non funziona" replicherebbe l'errore
   simmetrico del "backtest solo bull market" ([agents/quant_reviewer.md §2](../../agents/quant_reviewer.md)).
   Un selettore difensivo va giudicato sul **downside protection in risk-off**, che qui è
   **non osservato**. → vedi [[feedback_strategy_conditional_edge]].

2. **Mismatch orizzonte segnale / orizzonte holding** — lo score è un segnale *value/quality*
   a orizzonte pluri-mensile/annuale, misurato qui su forward-return di 1-5 settimane su tape
   guidato dal momentum. Segnali fondamentali e momentum hanno IC con **segni opposti** a
   queste frequenze (Asness-Moskowitz-Pedersen, "Value and Momentum Everywhere", JF 2013).
   Misurare un segnale lento con una regola d'uscita inesistente confonde la diagnosi.

3. **Closet-indexing → nessun edge misurabile possibile** — comprare equal-weight ~90-120
   titoli su 500 produce un portafoglio quasi indistinguibile da RSP (tracking error minimo),
   per cui anche un edge reale sarebbe sommerso. Con N efficace così alto, lo *active share* è
   troppo basso perché il segnale emerga (Cremers-Petajisto RFS 2009).

## Conclusioni operative per lo Stage 2 (miglioramento algoritmo)

Ipotesi da testare — **in ordine di leva attesa**, non ancora validate:

1. **Lo scenario macro è la leva dominante e a dicembre era sbagliato.** Derivare lo scenario
   da 2 input (tasso > 3% + bool liquidità) è troppo grezzo: ha chiamato *Difensivo* all'inizio
   di un rally. Il workspace ha già [core/regime.py](../../core/regime.py) (direzione×volatilità
   da prezzo) — agganciarlo al posto/oltre la regola tassi. → [[reference_regime_timeline_lookahead]]
   (attenzione al lag, niente same-day label).

2. **Aggiungere un gate di momentum (RRG) alla buy-list.** È l'unico segnale con segno corretto
   nei dati. Ipotesi: `buy = score≥4 AND match=SI AND RRG∈{LEADING,IMPROVING}`. Da verificare se
   alza l'alpha o solo la varianza.

3. **Concentrare.** Passare da "tutti i SI" a top-N (es. 15-25) per score combinato, per creare
   active share misurabile. Senza concentrazione l'edge non sarà mai distinguibile dal rumore.

4. **Definire una regola di uscita basata su prezzo** (non solo il diff sui pick), p.es. uscita
   su RRG→LAGGING o stop su drawdown relativo. Oggi il "return" non è nemmeno ben definito.

5. **Misurare lo score sull'orizzonte giusto.** Se è un segnale value a 6-12 mesi, valutarlo a
   quell'orizzonte; non aspettarsi IC positivo a 1 settimana.

## Test mancanti prima di qualunque promozione

- [ ] Raccogliere ≥6-12 mesi di cross-sezioni settimanali che **includano un episodio risk-off**
      (l'unico contesto in cui la tesi difensiva è falsificabile).
- [ ] IC con **clustering per data** + bootstrap a blocchi per t-stat onesti (N efficace).
- [ ] A/B della buy-list **con vs senza gate RRG** e **concentrata vs full**, su backtest
      storico SP500 multi-anno (non solo i 4 snapshot live), con costi e survivorship handling.
- [ ] Walk-forward dello scenario macro: lo switch *Difensivo→Quality* ha valore predittivo o
      è rumore? Test su storia tassi/liquidità lunga.

## Note operative

- **Non promuovere a live / non aumentare size** sulla base di questi dati: il segnale è
  insufficiente in entrambe le direzioni.
- **Non concludere "il selettore è rotto"**: l'underperformance osservata è coerente con un
  selettore quality in un rally di bassa qualità; la sua funzione (protezione) non è stata
  ancora testata.
- Dati mancanti: 6 ticker senza prezzi forward (DAY, FI, IPG, K, MMC, WBA — rinominati/delisted),
  esclusi; impatto trascurabile sulle medie ma è una micro-fonte di survivorship.

---

# Addendum Step 2 — Backtest storico PIT (2014-2026) — 2026-06-01

Obiettivo dichiarato dall'utente: **outperformare l'indice nei rally E restare a netto
positivo mentre l'indice cala** (profilo asimmetrico). Il backtest serve a verificare con
evidenza multi-regime se l'architettura attuale può raggiungerlo. Script:
[backtest.py](../../strategies/stock_selector/analysis/backtest.py). 148 cross-sezioni
mensili, 501 titoli. **Survivorship: costituenti attuali (bias noto, gonfia le CAGR
long-only — conta solo il differenziale).** Lo score fondamentale non è incluso (no PIT DB).

## Risultato 1 — Il segnale RRG/momentum NON ha edge cross-sezionale (12 anni)

| Segnale | mean IC | t-stat | %>0 |
|---|---|---|---|
| rs_ratio (RRG) | −0.0017 | **−0.14** | 51% |
| rs_momentum (RRG) | −0.0012 | −0.10 | 51% |
| mom_12_1 (classico) | +0.0022 | +0.14 | 53% |

Quadrante RRG, forward 1M: LEADING +1.36%, IMPROVING +1.63%, WEAKENING +1.46%, LAGGING
+1.33% → spread LEADING−LAGGING **+0.03%/mese, t=+0.14**. Long-short Q5−Q1 di momentum:
**+0.7% CAGR, Sharpe 0.12**. **Nessun edge.** Il "RRG sembrava il segnale buono" dei dati
live era rumore di 4 osservazioni. Coerente con momentum debole/assente nel large-cap SP500
(universo efficiente; Asness-Moskowitz-Pedersen JF 2013). → ribalta l'**ipotesi H2** dello
Step 1: aggiungere un gate RRG **non è supportato dai dati**.

## Risultato 2 — Il regime ^GSPC non riscatta il momentum

IC del momentum per regime: tutti vicini a zero e incoerenti; i pochi valori "grandi"
(Bull Volatile +0.034) sono su N=5 mesi = irrilevanti. **Nessun regime in cui il momentum
cross-sezionale funziona robustamente.** → l'**ipotesi H1** (timing dello scenario per
accendere il momentum) non trova base: non c'è momentum da accendere.

## Risultato 3 — Il tilt difensivo (low-vol) e l'obiettivo asimmetrico

Proxy price-based del tilt difensivo (quintile a volatilità più bassa, = ciò che lo scenario
*Difensivo* cerca con beta<1):

| | up-capture (rally) | down-capture (cali) | Sharpe | maxDD |
|---|---|---|---|---|
| Low-vol | **69%** | **52%** | 0.94 | −16% |
| RSP (indice EW) | 100% | 100% | 0.78 | −24% |

- **Protegge** (cade ~metà dell'indice nei mesi negativi) → migliore Sharpe e maxDD (anomalia
  low-vol, Baker-Bradley-Wurgler 2011; Frazzini-Pedersen BAB 2014).
- **MA lagga nei rally** (partecipa solo al 69%) → *è esattamente l'underperformance osservata
  nei dati live di Step 1*. Non un bug: è la natura del tilt difensivo.
- **NON resta positivo nei cali**: solo nel **27%** dei mesi negativi dell'indice il low-vol
  chiude positivo. Negli altri 73% scende, solo meno.

## La conclusione che conta per l'obiettivo dell'utente

**I due obiettivi sono in tensione strutturale e non ottenibili da un tilt statico long-only.**
La frontiera della letteratura low-vol è chiara: alto up-capture *e* basso down-capture insieme
non si ottengono selezionando azioni — un tilt difensivo compra protezione *vendendo* rally
(up-capture < 100%); un tilt aggressivo fa l'opposto. E **nessun** portafoglio azionario
long-only resta positivo in un vero bear market (2020 −34%, 2022 −25%): cade solo meno.

→ Il profilo asimmetrico desiderato (su nei rally, **netto positivo** nei cali) richiede una
**leva di timing dell'esposizione** (risk-on/risk-off verso cash/difensivo), **non** una
migliore selezione cross-sezionale dentro l'SP500. È qui che [core/regime.py](../../core/regime.py)
ha valore: come **interruttore di esposizione di mercato** sull'indice, non come filtro titoli.
La selezione titoli dentro l'SP500 contribuisce poco alpha dimostrabile (universo efficiente).

## Implicazioni riviste per il codice (da discutere, non ancora implementate)

1. **Spostare l'asse da "quali titoli" a "quanto mercato".** Layer di market-timing su ^GSPC
   (regime → % allocazione azionaria vs cash) è la sola leva con evidenza per l'asimmetria.
2. **Abbandonare il gate RRG** come selettore cross-sezionale (IC nullo a 12y).
3. **Lo score fondamentale resta non validato** (serve PIT DB per testarlo onestamente).
4. **Se si vuole alpha di selezione**, serve un **universo più ampio** (mid/small cap) dove
   i fattori hanno dispersione — non l'SP500. → [[project_stock_selector_global_future]].
5. **Survivorship + PIT constituents** vanno risolti prima di qualunque numero "da live".

## Test mancanti (aggiornati)

- [ ] Backtest del layer regime-as-exposure-switch su ^GSPC: up/down-capture del portafoglio
      *timed* vs buy&hold, con costi di turnover, su 2008/2020/2022.
- [ ] Ripetere IC con **costituenti point-in-time** (eliminare survivorship) per confermare il
      null del momentum.
- [ ] Quantificare il drag del turnover settimanale dell'attuale rebalance.

## Riferimenti (addendum)

- Baker, Bradley, Wurgler — *Benchmarks as Limits to Arbitrage (low-vol anomaly)*. FAJ 2011.
- Frazzini, Pedersen — *Betting Against Beta*. JFE 111(1), 2014.

## Riferimenti

- Asness, Moskowitz, Pedersen — *Value and Momentum Everywhere*. JF 68(3), 2013.
- Cremers, Petajisto — *How Active Is Your Fund Manager? (Active Share)*. RFS 22(9), 2009.
- López de Prado — *Advances in Financial ML*, cap. 7 (cross-sectional dependence). 2018.
- Harvey, Liu, Zhu — *…and the Cross-Section of Expected Returns*. RFS 29(1), 2016.
