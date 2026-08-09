# Pre-registrazione — I livelli a numero tondo .80/.20 sono zone di reazione? (Nasdaq)

> **Vincolante, scritta il 2026-08-09 PRIMA di qualunque esecuzione.** Nessun risultato è ancora
> stato calcolato. Le soglie non si modificano dopo aver visto i numeri.
>
> Ciclo: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md). Fonte dell'ipotesi:
> [`_sorgenti/insight_da_yt/okala_80-20_nasdaq_ChartFanatics.md`](../fondamenti_tecnici/_sorgenti/insight_da_yt/okala_80-20_nasdaq_ChartFanatics.md).

---

## 1. Cosa si testa — e cosa NON si testa

**Si testa il PRIMITIVO, non la strategia.** La strategia di Okala non è testabile da noi: le entrate
(*fork*, *H pattern*, *cross-section*, *repair*) sono **descrizioni visive**, non regole — due persone
marcherebbero setup diversi — e il grafico d'ingresso è a **200 secondi**, che non è ricostruibile dai
nostri M5 (200s non divide 300s) e per cui non abbiamo M1.

Resta un'affermazione **oggettiva e isolabile**, che è il vero punto di illuminazione del materiale:

**H1**: sul Nasdaq, i prezzi con finale **.80 e .20** (griglia fissa: livelli a `P mod 100 ∈ {20,80}`)
mostrano un tasso di **REACTION** superiore a quello di una griglia **identica per geometria ma
sfasata**.

**H0**: la fase della griglia è irrilevante — .80/.20 reagisce come qualunque altra coppia di livelli
con la stessa spaziatura.

**Perché non è una riapertura della famiglia CLOSED.** La [ricerca livelli](../DECISIONS.md) (384
trial, NULL) testava livelli **derivati dalla struttura** (OHLC, volume/POC, HTF, order block): "il
mercato ricorda questo prezzo". Qui il meccanismo proposto è **diverso**: una griglia aritmetica fissa
che non deriva da nulla, con razionale di **clustering degli ordini sui numeri tondi** — fenomeno
documentato nella microstruttura. Famiglia **nuova**, trial **#1 di 3**.
⚠️ **Prior dichiarato: negativo.** Il nostro studio trovò i livelli strutturali equivalenti a livelli
casuali; se una griglia arbitraria si comporta come una strutturale, la previsione naturale è NULL.

## 2. Il null giusto: stessa geometria, fase diversa

Con una griglia fissa non si può usare il *random distance-matched* dell'engine originale: a griglia
fissa la distanza determina la posizione, quindi un livello casuale "alla stessa distanza" sarebbe **lo
stesso prezzo**.

Baseline corretta: **sfasamento della griglia**. Per ogni estrazione random si sceglie un offset
$\delta$ uniforme e si usa la griglia $\{20+\delta,\ 80+\delta\} \bmod 100$. Preserva **esattamente**
la spaziatura reale (60/40 punti alternati) e cambia **solo la fase**. Se i numeri tondi contano, la
fase 0 deve battere le fasi casuali. $\delta$ è vincolato a stare ad almeno **10 punti** dalla griglia
reale per evitare sovrapposizioni.

## 3. Dati e parametri CONGELATI

| | |
|---|---|
| Serie | `NAS100_M5.csv` — **949.241 barre**, 2012-01-19 → 2026-07-16 |
| Split | **TRAIN 70% / HOLDOUT 30%** cronologico. L'holdout si apre **una sola volta**, e **solo** se il TRAIN è positivo |
| Metrica | **%REACTION per touch**, da `analysis/level_research/reaction.py::classify()` — **costanti invariate**: `TOL_ATR=0.10`, `TOUCH_WINDOW=24`, `N_REACT=4`, `REACT_FAV_ATR=1.0` |
| Punti di decisione | uno ogni **12 barre M5** (1 ora), per limitare la sovrapposizione |
| Lati | SUPPORT (livello sotto il prezzo) e RESISTANCE (sopra), classificati separatamente e poi poolati |
| Random | **M = 5** griglie sfasate per punto di decisione (come `M_RANDOM` originale) |
| CI | **block-bootstrap sui GIORNI** (`boot_rate_diff_ci`), che è il cluster reale |
| Seed | 42 |

Le costanti di `classify()` **non si toccano**: sono quelle pre-registrate della ricerca livelli e
riusarle identiche è ciò che rende i due studi confrontabili.

## 4. Soglie di verdetto — fissate ORA

Test **primario e unico decisivo**: differenza di %REACTION (reale − random) **poolata su entrambi i
lati**, su **TRAIN**.

| Esito TRAIN | Decisione |
|---|---|
| **Lower bound CI 95% della differenza > 0** | Si apre l'**HOLDOUT**, una volta. Conferma solo se anche lì il lower bound > 0 |
| **CI include lo zero, o lower bound ≤ 0** | **NULL** → famiglia **CLOSED**, nessuna rifinitura, nessun secondo giro |

**Secondari, riportati ma NON decisivi** (non possono ribaltare il verdetto primario): breakdown per
lato, per fascia oraria (apertura NY vs resto), e per anno. Servono a descrivere, non a decidere —
altrimenti sarebbero multiple testing mascherato.

## 5. Osservazione aritmetica da verificare nel test

Con livelli a `...20` e `...80`, la spaziatura è **60 e 40 punti alternati**. Con una tolleranza di
touch di 0.10 ATR, la **frazione di territorio di prezzo "vicino a un livello"** va misurata e
riportata: se è alta, il filtro non è selettivo e il livello fa poco lavoro a prescindere dal tasso di
reazione. È una metrica descrittiva obbligatoria del report.

## 6. Cosa un esito positivo NON darebbe

Nemmeno un CONFERMATO produce una strategia eseguibile: le entrate di Okala restano non specificate e
il timeframe d'ingresso non ricostruibile. Un esito positivo sarebbe un **mattone riutilizzabile**
(un filtro di livello oggettivo per strategie future su Nasdaq), non un sistema.

## 7. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-09 | Creazione, prima di qualunque esecuzione | Primo test dal mandato "insight da YouTube" |
