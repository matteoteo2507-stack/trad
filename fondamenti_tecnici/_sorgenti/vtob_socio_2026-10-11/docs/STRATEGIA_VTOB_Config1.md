# Strategia VTOB — Configurazione 1 (XAUUSD M15, Solo Long, 1:3, pareggio a 1R)

> **Istruzioni per Claude.** Questo documento è la specifica completa e vincolante di una strategia meccanica. Il tuo compito è renderla operativa: implementarla nel sistema che ti indico (bot, EA MT5, copier, script) oppure eseguirla seguendo le regole alla lettera.
>
> Non c'è margine discrezionale:
> - non aggiungere filtri, non saltare segnali validi, non spostare stop o target se non come scritto qui;
> - se una regola è ambigua o un dato manca, **fermati e chiedi**, invece di indovinare.
>
> File di riferimento allegati, se presenti:
> - `VTOB_Config1_EA.mq5`: implementazione MT5 di riferimento;
> - `VTOB_Strategy_Config1.pine`: strategy TradingView;
> - `motore_riferimento_vtob_bt.py`: motore di backtest Python.
>
> Se la tua implementazione diverge da questi file, sono i file ad avere ragione, salvo bug evidenti: in quel caso segnalalo.

---

## 1. Panoramica
- **Strumento:** XAUUSD (oro spot CFD), prezzi BID.
- **Timeframe operativo:** M15. Tutte le decisioni si prendono **solo alla chiusura di una candela M15**.
- **Idea:** comprare quando il prezzo torna a toccare un order block (OB) rialzista "di qualità" e riparte verso l'alto, nella direzione del trend.
- **Direzione:** solo long. Gli short sono disattivati di default, ma la logica speculare è descritta in fondo.
- **Frequenza attesa:** circa 4 trade al mese. Durata media circa 1 giorno, i trade vincenti circa 2 giorni. Le posizioni restano aperte anche di notte e nel weekend.

## 2. Parametri (valori fissi della Configurazione 1)
| Parametro | Valore |
|---|---|
| `ST_LEN` (periodo volatilità) | 50 |
| `ST_MULT` (moltiplicatore Supertrend) | 3.5 |
| `PIV_L` (candele a sinistra del pivot) | 7 |
| `PIV_R` (candele a destra / ritardo di conferma) | 3 |
| `ZONE_H` (altezza OB in volatilità) | 1.0 |
| `MIN_AGE` (età minima del trend, candele) | 20 |
| `DIST_MULT` (distanza minima OB dalla linea di trend, in volatilità) | 0.0 |
| `HTF` / `HTF_LEN` (EMA timeframe superiore) | H1 / 200 |
| `SL_MULT` (stop in volatilità) | 6.0 |
| `RR` (target in R) | 3.0 |
| `BE_R` (trigger pareggio in R) | 1.0 |
| `BE_OFF` (offset pareggio in R) | 0.1 |
| `RISK_PCT` (rischio per trade) | 0.5% del balance (modificabile solo dall'utente) |
| `MAX_SPREAD` | 1.00 $ |

## 3. Indicatori (calcolati su candele M15 chiuse, indice `i` = candela appena chiusa)
**3.1 Volatilità**
`vol[i] = media semplice di (high − low) delle ultime 50 candele, inclusa i`

**3.2 Supertrend custom** (ricorsivo, esattamente così):
```
src = (high[i] + low[i]) / 2
lb0 = src − 3.5·vol[i]        ub0 = src + 3.5·vol[i]
pLB = lb[i−1] (0 se non esiste)   pUB = ub[i−1] (0 se non esiste)
lb[i] = lb0 se (lb0 > pLB oppure close[i−1] < pLB), altrimenti pLB
ub[i] = ub0 se (ub0 < pUB oppure close[i−1] > pUB), altrimenti pUB
se vol[i−1] non esiste:            trend[i] = +1
altrimenti se tstop[i−1] == pUB:   trend[i] = +1 se close[i] > ub[i], altrimenti −1
altrimenti:                        trend[i] = −1 se close[i] < lb[i], altrimenti +1
tstop[i] = lb[i] se trend = +1, altrimenti ub[i]
cambio_trend[i] = (trend[i] ≠ trend[i−1])
età_trend[i] = candele trascorse dall'ultimo cambio_trend (0 sulla candela del cambio)
```
Prima di prendere segnali servono almeno **3.000 candele M15 di storico** per il riscaldamento. Con questo storico i risultati sono identici a quelli calcolati sullo storico completo.

**3.3 EMA del timeframe superiore**
EMA200 delle chiusure H1. Per la candela M15 `i` si usa il valore dell'**ultima candela H1 già chiusa**, cioè la H1 *precedente* a quella che contiene l'orario di apertura di `i`. Mai la H1 in formazione.

**3.4 Pivot low confermato alla candela i**
Con `p = i − 3`, c'è un pivot low se:
- `low[p] < low[k]` per tutte le k da p−7 a p−1 (minimo stretto a sinistra);
- `low[p] ≤ low[k]` per tutte le k da p+1 a i (a destra è ammessa la parità).

Il pivot è noto **solo alla chiusura di i**, non prima.

## 4. Order block (OB)
Esiste **un solo OB attivo alla volta**: `OB = {top, bottom, direzione, id}`.

**4.1 Creazione di un OB long** alla chiusura di `i`, se TUTTE queste condizioni sono vere:
1. `trend[i] = +1` e c'è un pivot low confermato in `i`;
2. `top = min(open[p], close[p])` e `bottom = top − 1.0·vol[i]`;
3. non si sovrappone all'OB attivo. "Sovrapposto" vuol dire che NON vale `(bottom > top_attivo oppure top < bottom_attivo)`. Se non c'è un OB attivo, la condizione è soddisfatta;
4. **filtro età trend:** `età_trend[i] ≥ 20`;
5. **filtro linea di trend:** `bottom − tstop[i] ≥ 0`, cioè tutto l'OB sta sopra la linea;
6. **filtro timeframe superiore:** `close[i] > EMA200_H1` (ultima H1 chiusa).

Se sono tutte vere, il nuovo OB sostituisce quello attivo. Come id si usa l'orario della candela pivot `p`. Se anche una sola è falsa, l'OB non esiste e quello attivo resta com'è.

**4.2 Invalidazione:** alla chiusura di `i`, dopo l'eventuale creazione, se `high[i] < bottom` l'OB long è **rotto** e non c'è più nessun OB attivo.

## 5. Segnale di ingresso (long)
Alla chiusura di `i` c'è un **segnale long** se TUTTE queste condizioni sono vere:
- l'OB attivo è long (valutato dopo i passi 4.1 e 4.2);
- `low[i] > top` e `low[i−1] ≤ top_alla_chiusura_di(i−1)`. È un crossover del low sopra il top: se alla chiusura di i−1 non c'era un OB attivo, niente segnale;
- non c'è un nuovo pivot low confermato in `i`;
- `cambio_trend[i]` è falso.

**Il segnale è valido solo se:**
- non c'è già una posizione aperta di questa strategia;
- l'id di questo OB non è già stato tradato (**un solo trade per OB**, anche dopo uno stop);
- lo spread attuale è ≤ 1,00 $.

## 6. Esecuzione e gestione del trade
1. **Ingresso:** BUY a mercato all'**apertura della candela M15 successiva** al segnale. Se l'ordine fallisce, non riprovare nelle candele dopo: il segnale decade.
2. **Distanza dello stop:** `D = 6.0 × vol[i]`, con `vol` della candela del segnale.
3. **Livelli** (sul prezzo BID al momento dell'ingresso, `B`):
   - `SL = B − D`;
   - `TP = B + 3·D`.
4. **Lotto:** `lotti = (balance × 0,5%) / ((D + spread) / tick_size × tick_value)`, arrotondato **per difetto** al passo lotto del broker. Se il risultato è sotto il lotto minimo, **salta il trade** e registralo nel log. Non alzare il lotto per arrivare al minimo.
5. **Pareggio:** a ogni chiusura di candela M15 dopo l'ingresso, compresa quella della candela di ingresso, se il **massimo** di una qualsiasi candela chiusa dall'ingresso è ≥ `B + 1.0·D`, sposta lo SL a `B + 0.1·D`. Lo fai **una volta sola** e non sposti altro.
   - Se al momento dello spostamento il prezzo è già sotto `B + 0.1·D`, chiudi a mercato.
6. **Uscita:** solo a SL, TP o SL di pareggio. Niente uscite manuali, niente trailing, niente parziali, niente chiusure a tempo. Le posizioni restano aperte nel weekend.

## 7. Regole speculari per gli short (DISATTIVATE in questa configurazione)
Si attivano solo se l'utente lo chiede esplicitamente.
- OB short su pivot high con `trend = −1`: `bottom = max(open[p], close[p])`, `top = bottom + vol`.
- Filtri: `età ≥ 20`, `tstop − top ≥ 0`, `close < EMA200_H1`.
- Rottura: `low > top`.
- Segnale: crossunder di `high` sotto `bottom`, senza nuovo pivot high e senza cambio trend.
- Ingresso: SELL con `SL = A + D`, `TP = A − 3D` (A = ASK).
- Pareggio: quando il minimo tocca `A − D`, stop a `A − 0.1D`.

## 8. Cosa NON fare
- Non usare candele non chiuse per OB, pivot, filtri o segnali.
- Non usare la EMA H1 della candela H1 in formazione.
- Non tradare due volte lo stesso OB. Non aprire più posizioni insieme.
- Non cambiare parametri, rischio o direzione senza l'ok esplicito dell'utente.
- Non spostare lo SL tranne che per il pareggio (una sola volta). Non chiudere in anticipo.

## 9. Log richiesto (per ogni candela con eventi)
Registra con l'orario della candela (server e ora italiana):
- OB creati: top, bottom, id;
- OB scartati, con il filtro che li ha scartati;
- OB rotti;
- segnali, con il motivo se sono stati ignorati (posizione aperta, OB già tradato, spread, lotto sotto il minimo);
- ordini inviati con prezzo, SL, TP, lotti ed esito;
- spostamenti a pareggio e chiusure con il risultato in $ e in R.

## 10. Risultati di riferimento e verifica
Backtest su XAUUSD M15 dal 12/07/2022 al 09/10/2026, con lo spread reale del broker:
- **199 trade, PF 2,03, +83 R, drawdown massimo 8,9 R, 5 anni positivi su 5** (il peggiore +6,3 R);
- esiti: 55 al target, 70 a pareggio, 74 a stop;
- serie peggiore: 5 perdite consecutive;
- stop mediano: circa 10 $ nel 2022, circa 64 $ nel 2026 (cresce con la volatilità).

**Test di accettazione per la tua implementazione:** sugli stessi dati devi riottenere questi numeri entro ±5%. Prima di andare live:
1. backtest;
2. almeno 2-4 settimane in **demo**, confrontando ogni segnale con l'indicatore/strategy su TradingView.

## 11. Rischi noti (da ricordare all'utente)
- Il "solo long" ha funzionato perché dal 2022 al 2026 l'oro è salito da circa 1.700 a circa 4.200 $. Se il trend di fondo si inverte, la configurazione va rivalutata (long+short: PF 1,62, +91 R, DD 13,9 R nello stesso periodo).
- Il vantaggio statistico esiste ma è moderato. I risultati passati non garantiscono quelli futuri.
- Con stop larghi e conti piccoli il lotto minimo può superare il rischio impostato: in quel caso il trade va saltato, non forzato.
