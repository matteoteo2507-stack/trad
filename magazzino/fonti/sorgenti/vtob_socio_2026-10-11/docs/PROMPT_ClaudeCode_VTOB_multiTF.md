# Progetto: backtest multi-timeframe della strategia "VTOB PRO" su XAUUSD

## Contesto
Ho un indicatore TradingView (Pine Script v6), `VTOB_Indicator_Pro.pine`. È una versione modificata del "Volume-Trend Order Block Engine [BigBeluga]". Funziona così:
- Disegna order block (OB) sui pivot, nella direzione di un Supertrend custom.
- Dà un punteggio di qualità a ogni OB e mostra solo quelli selezionati.
- Genera un segnale ("croce di retest") quando il prezzo torna sull'OB.

Su XAUUSD M15 (luglio 2022 – ottobre 2026) l'ho già testato con un motore Python. Trovi il motore in `motore_riferimento_vtob_bt.py` e i risultati più sotto. Ora voglio fare lo stesso lavoro, ma molto più a fondo, **su tutti i timeframe**, e trovare le migliori configurazioni operative per ciascuno.

**La strategia di base resta sempre la stessa: entrare sugli OB dell'indicatore.** Le cose da ottimizzare sono:
- la gestione del trade: stop, target, R:R, parziali, break-even, trailing;
- i parametri dell'indicatore: pivot, filtri, altezza della zona.

## File che ti do
- `VTOB_Indicator_Pro.pine`: l'indicatore. È la fonte di verità della logica.
- `motore_riferimento_vtob_bt.py`: il mio motore Python già funzionante su M15. Usalo come punto di partenza e come riferimento per validare. Puoi riscriverlo meglio, ma i risultati su M15 devono tornare.
- Export barre MT5, uno per timeframe: `XAUUSD_M1.csv`, `XAUUSD_M5.csv`, `XAUUSD_M15.csv`, `XAUUSD_M30.csv`, `XAUUSD_H1.csv`, `XAUUSD_H4.csv`, ecc. Usa quelli che trovi nella cartella.
  - Colonne: `time,open,high,low,close,tick_volume,spread,real_volume`
  - `time` è l'ora del server del broker, cioè UTC+3 d'estate e UTC+2 d'inverno. L'ora italiana è quella del server meno 1 ora.
  - `spread` è in punti: 1 punto = 0,01 $. Quindi spread 150 = 1,50 $.
  - I prezzi sono BID.

## FASE 1 — Replica esatta dell'indicatore (prima di qualsiasi ottimizzazione)
Replica in Python, candela per candela, la logica di `VTOB_Indicator_Pro.pine`, **senza lookahead**:
1. **Volatilità** `custom_atr = SMA(high - low, 50)`. **Supertrend custom** con mult 3.5, ricorsivo esattamente come nel Pine: `lower_band`/`upper_band` con ricorsione, `prevSuperTrend == prevUpperBand`, `market_trend`, `trend_stop`.
2. **Pivot** `ta.pivotlow(low, pivot_left, pivot_right)` / `ta.pivothigh`. Default: 7 a sinistra e 3 a destra. Il pivot è noto solo `pivot_right` candele dopo: **l'OB esiste solo dalla candela di conferma in poi.**
3. **OB long** (trend = 1 e pivot low): `top = min(open, close)` della candela pivot, `bottom = top - zona_h × custom_atr`, con default `zona_h = 1`. **OB short** speculare. Se si sovrappone all'OB attivo viene ignorato. C'è un solo OB attivo alla volta.
4. **Punteggio qualità**, calcolato alla candela di conferma. Ogni fattore attivo vale 1 punto.
   - (a) **Impulso:** massimo delle ultime N candele − top ≥ X × atr.
   - (b) **Età del trend:** candele dal cambio di trend ≥ 20.
   - (c) **Timeframe superiore:** close sopra/sotto la EMA200 del TF superiore, calcolata sulla candela HTF già chiusa (`[1]` + `lookahead_on`).
   - (d) **Distanza dalla linea di trend:** long `bottom − trend_stop ≥ dist × atr`.
   - (e) **Volume:** volume del pivot ≥ X × media delle 20 candele precedenti.

   Default: (b), (c) e (d) attivi, punteggio minimo 3 (tutti e tre obbligatori).
5. **Invalidazione:** OB long rotto se `high < bottom`, short se `low > top`. Dopo la rottura non dà più segnali.
6. **Croce di retest** long: `crossover(low, top)`, con OB attivo long, nessun nuovo pivot sulla candela, nessun cambio di trend sulla candela, a candela chiusa. Short speculare.

**Validazione obbligatoria su M15, prima di andare avanti.** Con la configurazione qui sotto devi riottenere circa i miei numeri (tolleranza ±5%):
- pivot 7/3, filtri b+c+d, ingresso alla croce, stop 6×atr, TP 1:3, BE a +1R (stop a ingresso + 0,1R), solo long, spread reale;
- risultato atteso: **199 trade, PF 2,03, +83 R, drawdown max 8,9 R**.

Se i numeri non tornano, trova il motivo prima di continuare. Poi controlla a mano 5-10 OB su date diverse rispetto a quello che disegna TradingView e scrivi nel report le differenze che trovi.

## FASE 2 — Simulatore di esecuzione (realistico e conservativo)
- **Ordini:** decisi a chiusura candela, eseguiti dalla candela successiva.
  - Croce: ingresso a mercato all'open della candela dopo.
  - Limit: attivo dalla candela dopo la conferma, eseguito se il prezzo tocca il livello. Se c'è un gap, esecuzione all'open.
- **Costi:** spread reale della candela di ingresso, più uno slippage configurabile (default 0,10 $ per lato). Commissione configurabile.
- **Candela ambigua:** se una stessa candela tocca sia SL che TP, **vince lo SL**. Sulla candela di ingresso con limit controlla solo lo SL.
- **Regole di posizione:** una posizione alla volta per configurazione e un solo trade per OB. Opzionale da testare: "rientro sullo stesso OB dopo uno stop".
- **Risultati** in R (multipli del rischio iniziale) e in $ per 1 oncia. Con il BE, il "win rate" va riportato separato in TP, BE, SL e parziali.
- **Velocità:** usa numba o una vettorizzazione dove possibile. Lo spazio dei parametri è grande e M1/M5 hanno milioni di candele. Calcola gli OB **una volta per set di parametri dell'indicatore** e riusali per tutte le varianti di gestione del trade. Usa multiprocessing.

## FASE 3 — Spazio delle varianti da testare (per ogni timeframe)
Ordine di lavoro: **prima la gestione del trade con l'indicatore di default, poi i parametri dell'indicatore** sulle 2-3 gestioni migliori. Non fare il prodotto cartesiano completo di tutto.

**Ingresso**
- croce di retest (a mercato);
- limit sul bordo dell'OB;
- limit al 25% e al 50% dentro la zona;
- limit con scadenza dopo N candele.

**Stop loss**
- X × atr, con X da 1 a 8;
- fisso in $ (5, 10, 15, 20, 30, 50) e in pips (1 pip XAUUSD = 0,10 $; riporta sempre anche i $);
- oltre il bordo opposto dell'OB + buffer di 0,5–3 × atr;
- sotto/sopra lo swing del pivot + buffer.

**Take profit**
- R:R 1 / 1,5 / 2 / 2,5 / 3 / 4 / 5;
- fisso in $ o pips;
- TP sul massimo/minimo di swing precedente;
- nessun TP con solo trailing.

**Parziali**
- es. 50% a 1R e resto a 3R, 33/33/33 a 1R, 2R e 3R, 50% a 1,5R e resto in trailing;
- dopo il primo parziale, stop a BE o meno.

**Break-even**
- trigger 0,5 / 0,75 / 1 / 1,5 / 2 R;
- offset 0 / 0,1 / 0,2 R.

**Trailing**
- ATR trailing (2–4 × atr) che parte dopo il BE o dopo il primo parziale;
- trailing sulla linea `trend_stop` del Supertrend;
- chandelier.

**Uscite a tempo / di contesto**
- time stop dopo N candele;
- uscita al cambio di trend;
- uscita a fine sessione / venerdì sera.

**Filtri operativi**
- direzione: long, short, entrambe;
- sessione oraria in ora italiana: tutte, 8–17, 9–22, 13–22;
- giorni della settimana.

**Parametri dell'indicatore** (dopo aver fissato la gestione)
- pivot sinistra 3–20 e destra 1–7;
- `zona_h` 0,5–2;
- soglie dei filtri (età del trend 10–40, dist 0–1 × atr);
- fattori attivi/spenti e punteggio minimo;
- **timeframe superiore adattato al TF del grafico**, per esempio: M1 → M15/H1, M5 → H1, M15 → H1/H4, H1 → H4/D1, H4 → D1/W1.

## FASE 4 — Anti-overfitting (la parte più importante)
- **Divisione dei dati:** primo 65% in-sample (IS) per scegliere, ultimo 35% out-of-sample (OOS) per verificare. **I parametri si scelgono SOLO sull'IS.** Aggiungi un walk-forward: finestre mobili, per esempio 12 mesi di ottimizzazione e 3 di test.
- **Scarta le configurazioni** con meno di 100 trade in totale o meno di 30 in OOS. Scarta anche quelle con PF OOS < 1,1 o con più di 1 anno negativo.
- **Robustezza:** una configurazione vale solo se anche i parametri vicini (±1 step) restano buoni, cioè se sta su un "plateau" e non su un picco isolato. Riporta l'indice di stabilità.
- **Monte Carlo:** rimescola l'ordine dei trade 1.000 volte e riporta il drawdown al 95° percentile e la serie di perdite consecutive più lunga.
- **Classifica** per R/maxDD in OOS e stabilità, **non** per il profitto IS. Riporta sempre quante configurazioni hai testato in totale, perché più ne testi più è facile trovarne una buona per caso.
- **Il trend dell'oro:** tieni presente che dal 2022 al 2026 l'oro è passato da 1.700 a 4.200, e questo favorisce i long. Riporta sempre anche i risultati long+short e separati.

## FASE 5 — Output
1. `risultati/<TF>_tutte.csv`: tutte le configurazioni testate, con le colonne trade, win/BE/loss %, PF, R totali, R medio, maxDD, R/DD, PF IS, PF OOS, anni positivi, anno peggiore, DD Monte Carlo 95%, stabilità.
2. `report.html` (o `.md`) **in italiano**:
   - per ogni TF, la **top 5** robusta con curva equity (IS e OOS evidenziati) e risultati per anno;
   - un confronto tra i timeframe;
   - la **configurazione consigliata** per ciascun TF e una **classifica finale** tra TF;
   - le differenze trovate rispetto a TradingView nella Fase 1.
3. `pine/VTOB_<TF>_<nome>.pine`: per ogni configurazione consigliata, una **strategy() Pine v6** che riproduce ESATTAMENTE le regole (ingresso, SL, TP, parziali con `strategy.exit` multipli, BE, trailing). Requisiti:
   - tutti i parametri come input;
   - nessun lookahead (`request.security` con `[1]` + `lookahead_on`);
   - `process_orders_on_close = false` e `calc_on_every_tick = false`;
   - commissione e slippage impostati.
4. `pine/VTOB_Indicator_Pro_<TF>.pine`: l'indicatore con i default della configurazione migliore per quel TF, con SL/TP/BE/parziali disegnati sul segnale e gli alert.
5. Un breve `LEGGIMI.md` che spiega come riprodurre tutto: comandi e versioni delle librerie.

## Regole generali
- Non modificare i file di dati originali. Se trovi buchi o candele anomale, segnalali e gestiscili.
- Prima di lanciare griglie enormi, stima i tempi e dimmelo. Procedi per gradi: prima M15 (validazione), poi H1 e M5, poi gli altri TF.
- Se trovi bug o ipotesi sbagliate nel mio motore o nel Pine, segnalali chiaramente.
- Scrivi codice pulito e commentato. Tieni il motore in un modulo separato dagli script di ricerca.
- Sii onesto sui risultati: se su un timeframe la strategia non funziona, scrivilo, senza forzare una configurazione "vincente".
