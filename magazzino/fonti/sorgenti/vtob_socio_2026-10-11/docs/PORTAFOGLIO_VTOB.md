# Portafoglio VTOB — XAUUSD multi-timeframe

Sono quattro strategie meccaniche, tutte basate sulle **stesse regole OB** di `STRATEGIA_VTOB_Config1.md` (volatilità, Supertrend custom, pivot, OB, filtri, croce di retest, ingresso all'open successivo, SL in volatilità, TP in R, pareggio a +1R con offset +0,1R, un trade per OB). Cambiano solo il **timeframe** e i **parametri**.

## Le 4 strategie
| | TF | Pivot sx/dx | EMA200 filtro | Trend da ≥ | Direzione | SL | TP | Pareggio | Magic EA |
|---|---|---|---|---|---|---|---|---|---|
| **A** | M15 | 7 / 3 | H1 | 20 candele | solo long | 6× vol | 3R | 1R | 7303001 |
| **B** | H1 | 10 / 3 | **D1** | 10 candele | long + short | 3× vol | 4R | 1R | 7306001 |
| **C** | M30 | 5 / 2 | **H4** | 20 candele | long + short | 8× vol | 3R | 1R | 7330001 |
| **D** (opzionale) | M5 | 10 / 5 | H1 | 20 candele | solo long | 6× vol | 4R | 1R | 7305001 |

In tutte: zona OB = 1× volatilità e distanza minima dalla linea di trend = 0.

## Risultati del backtest (spread reale del broker, senza lookahead)
Ho scelto i parametri tra **46.080 varianti testate** su M5/M15/M30/H1. Ogni configurazione scelta resta buona anche cambiando i parametri vicini ("plateau") ed è positiva sia nel periodo di scelta sia in quello di verifica.

| | Periodo | Trade | Trade/sett | PF | Totale | DD max | PF 1° periodo / 2° periodo |
|---|---|---|---|---|---|---|---|
| A M15 | lug 2022 – ott 2026 | 199 | 0,90 | 2,03 | +83 R | 8,9 R | 1,87 / 2,44 |
| B H1 | lug 2022 – ott 2026 | 109 | 0,49 | 2,56 | +70 R | 6,7 R | 2,44 / 2,86 |
| C M30 | lug 2022 – ott 2026 | 116 | 0,52 | 1,94 | +44 R | 4,3 R | 1,75 / 2,75 |
| D M5 | mag 2025 – ott 2026 | 117 | 1,58 | 1,74 | +42 R | 8,0 R | 1,72 / 1,82 |

### Portafoglio A + B + C (4 anni: luglio 2022 – ottobre 2026)
- **424 trade, circa 1,9 a settimana.** Nell'89% delle settimane c'è almeno un ingresso.
- **PF 2,14, +197 R, drawdown massimo 13,7 R.** Massimo 3 posizioni aperte insieme.
- R per anno: 2022 +22,8 · 2023 +16,5 · 2024 +46,0 · 2025 +94,0 · 2026 (fino a ottobre) +17,8. **Tutti positivi.**
- **Rischio 0,5% per trade:** +163% composto in 4 anni, **drawdown massimo 6,7%**, mese mediano +1,1%, mese peggiore −2,0%.
- **Rischio 1% per trade:** +572% composto, drawdown massimo 13,1%, mese mediano +2,1%, mese peggiore −3,9%.
- Mesi positivi: 35 su 52.
- Correlazione mensile tra le strategie: 0,42–0,51. Si muovono in parte insieme, quindi la diversificazione aiuta ma non è totale.

### Con anche D (M5), maggio 2025 – ottobre 2026
- **245 trade, circa 3,3 a settimana** (93% delle settimane con almeno un ingresso), **PF 2,10**, +114 R, DD 11 R.
- Con l'1% di rischio: +199% composto in 17 mesi, DD max 10,5%, mese mediano +2,5%, mese peggiore −5,2%.
- D è testata su soli 17 mesi: è la meno provata delle quattro.

## Rendimento mensile, A+B+C con rischio 1% per trade
| Anno | Gen | Feb | Mar | Apr | Mag | Giu | Lug | Ago | Set | Ott | Nov | Dic |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | | | | | | | 1,7 | −3,5 | 5,8 | 4,6 | 4,9 | 9,7 |
| 2023 | 6,7 | 0,6 | −0,5 | −2,5 | 0,1 | −3,9 | 2,1 | −1,2 | 3,0 | 9,5 | 3,1 | −1,0 |
| 2024 | −3,2 | 3,6 | 18,7 | 4,0 | 5,7 | −3,0 | 7,5 | 2,8 | 6,9 | 5,6 | 0,6 | −2,3 |
| 2025 | 2,6 | 8,0 | 15,4 | 17,7 | −3,0 | −2,0 | 0,9 | 0,8 | 32,9 | 13,7 | −2,0 | 16,1 |
| 2026 | 19,5 | −0,1 | 2,1 | −1,7 | −3,7 | 6,4 | −1,6 | 2,1 | −3,9 | 0,1 | | |

## Come metterlo in funzione (MT5)
Usa lo stesso EA `VTOB_Config1_EA.mq5` su più grafici XAUUSD, ognuno con le sue impostazioni:

| Grafico | Magic | Pivot sx | Pivot dx | Trend da | TF EMA | Stop | Target | Pareggio | Long | Short |
|---|---|---|---|---|---|---|---|---|---|---|
| M15 | 7303001 | 7 | 3 | 20 | H1 | 6 | 3 | 1 | ✔ | ✘ |
| H1 | 7306001 | 10 | 3 | 10 | D1 | 3 | 4 | 1 | ✔ | ✔ |
| M30 | 7330001 | 5 | 2 | 20 | H4 | 8 | 3 | 1 | ✔ | ✔ |
| M5 (opz.) | 7305001 | 10 | 5 | 20 | H1 | 6 | 4 | 1 | ✔ | ✘ |

Su TradingView usa `VTOB_Strategy_Portafoglio.pine` e scegli il preset A/B/C/D in base al timeframe del grafico.

## Rischi e avvertenze
- Le varianti testate sono molte. Anche se ho scelto solo quelle robuste, **dal vivo aspettati risultati inferiori**: per esempio un PF intorno a 1,5 invece di 2.
- I guadagni sono concentrati nelle fasi di forte trend dell'oro (2024–2025). Il 2026 finora è più debole: +17,8 R in 9 mesi.
- Con più strategie aperte insieme il rischio si somma: fino a 3 posizioni con A+B+C, fino a 4 con D.
- **Prima di andare live:**
  1. Strategy Tester MT5 ("ogni tick basato su tick reali") per ogni grafico;
  2. almeno 1-2 mesi in demo;
  3. poi rischio basso (0,25–0,5%).
