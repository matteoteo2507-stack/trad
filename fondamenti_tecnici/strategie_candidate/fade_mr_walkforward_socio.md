---
titolo: FADE mean-reversion — spec per walk-forward live (hand-off al socio)
fonti:
  - "analysis/nxt/closure.py (config A1)"
tipo: strategia_candidata
---

# FADE mean-reversion — regole per walk-forward live

> **Documento da consegnare al socio.** È la spec eseguibile della variante emersa dall'analisi di NXT. NON è una strategia dimostrata: è un **lead da validare in avanti** su mercato live/demo. Lo scopo di questo test è proprio capire se regge fuori campione. Regole **fisse**: non vanno modificate durante il test. Derivazione interna completa in [nxt_fib_trend_pullback.md](nxt_fib_trend_pullback.md) §4.

## In una riga

In un trend consolidato, quando il prezzo **ritraccia al 50%** della gamba impulsiva, si entra **CONTRO il trend** (fade / mean-reversion), scommettendo che il movimento si esaurisca e il ritracciamento si trasformi in inversione. Rischio piccolo e definito, obiettivo 1:3.

⚠️ È **deliberatamente contro-trend**: si shorta il pullback di un uptrend (e viceversa). Non è "compra il ritracciamento" — è l'opposto. Nasce dal fatto che la versione "continuazione" (comprare il pullback) su 14 anni e 6 mercati **perde** in modo netto; il lato opposto, invece, ha mostrato un edge.

## Universo e timeframe

- **Timeframe operativo: H1** (grafico a 1 ora).
- **Strumenti testati** (usare questi per confrontabilità): `EURUSD, GBPUSD, USDJPY, XAUUSD, US100 (Nasdaq), US500 (S&P)`.

## Passo 1 — Identificare la gamba impulsiva (con filtro di trend)

1. **Swing point** (metodo oggettivo, no discrezionalità): uno **swing high** è una candela il cui massimo è il più alto delle **5 candele precedenti e 5 successive** (quindi si "conferma" solo 5 candele dopo). Simmetrico per lo **swing low**.
2. **Gamba impulsiva** = ultimo movimento swing-low → swing-high (per un uptrend) o swing-high → swing-low (per un downtrend).
3. **Filtro di trend** (obbligatorio):
   - Uptrend valido: lo swing-high supera il precedente swing-high **E** lo swing-low di partenza supera il precedente swing-low (**Higher High + Higher Low**).
   - Downtrend valido: **Lower High + Lower Low**.
4. **Filtro dimensione**: l'ampiezza della gamba deve essere **≥ 1× ATR(14)** su H1. Gambe più piccole si scartano.

## Passo 2 — Il setup FADE

Traccia il ritracciamento di Fibonacci sulla gamba (0% = fine della gamba, 100% = origine).

- **Direzione**: uptrend → prepara uno **SHORT**; downtrend → prepara un **LONG**.
- **R (unità di rischio) = 28,6% dell'ampiezza della gamba** (in prezzo). Tutto è espresso in multipli di R.
- **Entrata**: quando il prezzo ritraccia fino al **50%** della gamba, entra nella direzione del fade.
- **Stop-loss**: **1R** dal lato del trend (per uno short: 1R **sopra** l'entrata ≈ livello **21,4%** di ritracciamento). Se il prezzo torna verso il massimo oltre quel punto, il movimento sta riprendendo → si esce.
- **Take-profit**: **3R** dal lato del fade (per uno short: 3R **sotto** l'entrata ≈ **135,8%** di estensione, cioè una vera inversione oltre l'origine della gamba). **Rapporto 1:3**.
- **Break-even**: appena il prezzo raggiunge **+2R** a favore, sposta lo stop a pareggio (entrata).
- **Validità del setup**: se il prezzo non raggiunge il 50% entro ~**48 candele H1** (~2 giorni di borsa) dalla formazione dello swing, si salta il trade.
- **Time-stop**: se dopo ~**20 giorni di borsa** non è arrivato né a TP né a SL/BE, chiudere a mercato.
- **Un solo trade per gamba per strumento.**

### Esempio numerico (short in uptrend)

Gamba da 100.00 (low) a 110.00 (high) → ampiezza = 10.00, R = 2,86.
- Entrata (50%): 105.00 → **SHORT**
- Stop (1R sopra): 107.86 (≈ 21,4% retrace)
- Target (3R sotto): 96.42 (≈ 135,8% ext)
- Break-even: sposta SL a 105.00 quando il prezzo tocca 99.28 (+2R)

## Cosa aspettarsi (dal backtest, sotto ipotesi PESSIMISTICHE dopo costi)

| Metrica | Valore backtest (14 anni, 6 mercati, ~10.000 setup) |
|---|---|
| Win rate @ 1:3 | ~**31%** (break-even a 1:3 = 25%) |
| E[R] per trade | **+0,35R** base; **+0,24R** anche a 3× i costi |
| Robustezza | positivo in **14/14 anni** e **6/6 strumenti**; regge l'holdout |

Se il live arriva **molto sotto** questi numeri (es. win < 25%, E[R] ≤ 0), il lead **non regge** e si archivia.

## Regole del test (importanti)

1. **Non modificare i parametri durante il test** (50% entrata, stop 1R, target 3R, BE 2R, swing a 5 barre, filtro 1 ATR). Cambiarli strada facendo invalida tutto (è "ottimizzazione col senno di poi").
2. **Size piccola / demo o micro**: è un esperimento di validazione, non un deployment.
3. **Registrare OGNI setup** (anche quelli saltati e i perdenti) con: strumento, data, direzione, entrata, esito in R. Serve per calcolare win rate ed E[R] reali e confrontarli col backtest.
4. **Coerenza nel marcare gli swing**: la parte più soggettiva è l'identificazione della gamba. Attenersi rigidamente alla regola delle 5 barre per non introdurre discrezionalità (è ciò che rende il test onesto).

## Status onesto (perché lo testiamo così)

Questa variante è stata **trovata analizzando i dati** (invertendo una strategia che perdeva). Ha superato l'holdout interno e lo stress sui costi, ma **non** una validazione indipendente in avanti — ed è esattamente ciò a cui serve questo walk-forward live. Finché non regge in forward reale, resta un'**ipotesi**, non un edge da capitalizzare. Nessuna promessa: solo un test pulito.
