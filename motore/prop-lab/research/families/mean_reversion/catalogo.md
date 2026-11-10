# Famiglia: Mean Reversion — catalogo

**Ipotesi.** Dopo un movimento estremo rispetto a una media (o dopo una falsa rottura di un livello
dove c'è liquidità), il prezzo tende a tornare verso il valore "di equilibrio". Funziona meglio in regimi
laterali / di range e su strumenti con forte componente intraday (oro, indici in sessioni calme, FX nelle
ore asiatiche). **Fallisce** nei trend forti e durante news ad alto impatto (l'eccesso continua).

| Strategia (codice) | Ingresso | Stop | Uscita | Parametri | Ispirazione |
|---|---|---|---|---|---|
| `bb_fade` | chiusura fuori dalla Bollinger(n,k) | m×ATR | banda centrale / time stop | n, k, atr_sl, filtro trend | Bollinger, classico |
| `rsi_extreme` | RSI(2–5) < soglia (o > 100−soglia) | m×ATR | RSI torna a 50 | n, lo, atr_sl, trend | Connors "RSI(2)" |
| `zscore_revert` | z-score vs media(n) oltre ±z | m×ATR | z torna verso 0 / z_exit | n, z, z_exit, atr_sl | stat-arb su singolo strumento, E. Chan |
| `keltner_reversal` | barra prima fuori Keltner, barra attuale di inversione che rientra | oltre l'estremo + buffer ATR | EMA | n, mult, buf, trend | Keltner / "re-entry" |
| `pdh_pdl_sweep` | wick oltre massimo/minimo di ieri e chiusura dentro | oltre la wick + buffer | metà range di ieri o R fisso | buf, tp, finestra oraria | liquidity sweep / "turtle soup" (Raschke & Connors) |
| `asia_range_fade` | falsa rottura del range asiatico e rientro | oltre la wick + buffer | centro o lato opposto del range / R fisso | fine Asia, buf, tp, ultima ora | session range fade (FX/oro) |
| `consecutive_bars` | N chiusure consecutive nella stessa direzione | m×ATR | prima chiusura contraria | n_bars, atr_sl, trend | "N down days" Connors |

## Da aggiungere (candidati)
- VWAP fade intraday (serve il volume reale o il tick volume MT5 come proxy)
- Internal Bar Strength (IBS) < 0.2 su indici, timeframe giornaliero
- Mean reversion su spread/coppie correlate (EURUSD vs GBPUSD): serve un motore multi-simbolo
- Fade del gap d'apertura sugli indici (cash open)

## Scartate / non meccanizzabili
- "Zone di supply/demand" disegnate a mano → servirebbe una definizione oggettiva (es. base di N candele + impulso > k×ATR)
- Divergenze RSI "a occhio" → formalizzabili come pivot a confronto, da fare in una variante dedicata
