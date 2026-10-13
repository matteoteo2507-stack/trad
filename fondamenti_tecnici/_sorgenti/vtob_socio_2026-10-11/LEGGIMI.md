# Pacchetto VTOB — strategie order block su XAUUSD

Questo pacchetto contiene tutto il necessario per analizzare, testare e migliorare le strategie su un altro computer: specifiche, codice TradingView, EA MT5, motore di backtest Python, dati e risultati.

## In breve: il portafoglio
| | TF | Regole chiave | Trade | PF | Totale | DD max |
|---|---|---|---|---|---|---|
| A | M15 | pivot 7/3, EMA200 H1, trend ≥20 candele, **solo long**, SL 6×vol, TP 3R, BE 1R | 199 | 2,03 | +83 R | 8,9 R |
| B | H1 | pivot 10/3, EMA200 **D1**, trend ≥10, **long+short**, SL 3×vol, TP 4R, BE 1R | 109 | 2,56 | +70 R | 6,7 R |
| C | M30 | pivot 5/2, EMA200 **H4**, trend ≥20, **long+short**, SL 8×vol, TP 3R, BE 1R | 116 | 1,94 | +44 R | 4,3 R |
| D (opz.) | M5 | pivot 10/5, EMA200 H1, trend ≥20, solo long, SL 6×vol, TP 4R, BE 1R | 117* | 1,74 | +42 R | 8,0 R |

\*D è testata su maggio 2025 – ottobre 2026; A, B e C su luglio 2022 – ottobre 2026.

**A + B + C insieme, in 4 anni:**
- 424 trade, circa 1,9 a settimana; PF 2,14; +197 R; DD 13,7 R; **tutti gli anni positivi**.
- **Rischio 1% per trade:** mese medio +4,0%, mediano +2,1%, DD max 13,1%.
- **Rischio 0,5%:** mese medio +1,9%, DD max 6,7%.

Dettagli completi in `docs/PORTAFOGLIO_VTOB.md`.

## Contenuto
```
LEGGIMI.md                     questo file
docs/
  PORTAFOGLIO_VTOB.md          specifica e risultati delle 4 strategie, rendimenti mensili, impostazioni EA
  STRATEGIA_VTOB_Config1.md    specifica completa e formale delle regole (formule, OB, segnali, gestione trade)
  PROMPT_ClaudeCode_StrategiaMigliore.md  prompt per Claude Code: verifica su TradingView e ricerca di miglioramenti
  PROMPT_ClaudeCode_VTOB_multiTF.md       prompt per Claude Code: backtest multi-timeframe approfondito
pine/
  VTOB_Indicator_Pro.pine      indicatore PRO (OB selezionati a punteggio, SL/TP/BE disegnati, alert)
  VTOB_Strategy_Portafoglio.pine  strategy() TradingView con preset A/B/C/D
  VTOB_Strategy_Config1.pine   strategy() della sola strategia A
  VTOB_Indicator_NoDelete.pine indicatore originale senza la cancellazione degli OB rotti
mt5/
  VTOB_Config1_EA.mq5              Expert Advisor MT5, un solo file per tutte le strategie (cambiano le impostazioni)
python/
  vtob_bt.py                   motore v1: caricamento dati, indicatore (core), simulatore e statistiche
  vtob_v2.py                   motore v2: più OB attivi, BE, parziali, trailing, time stop
  strategie.py                 definizione delle 4 strategie e caricamento dati per timeframe
  run_portfolio.py             riproduce i risultati del portafoglio e salva trade e rendimenti mensili
  run_grid.py                  ricerca a griglia (11.520 varianti per timeframe)
  requirements.txt
data/
  XAUUSD_M15.csv               export MT5, 12/07/2022 – 09/10/2026 (100.000 candele)
  XAUUSD_M5.csv                export MT5, 09/05/2025 – 09/10/2026 (100.000 candele)
risultati/
  riepilogo_portafoglio_ABC_1pct.txt
  trade_<strategia>.csv        ogni trade: ingresso, uscita, direzione, risultato in R
  portafoglio_trade.csv / portafoglio_mensile.csv
  griglia_M5/M15/M30/H1.csv    tutte le 46.080 varianti testate con le statistiche
```

## Come usarlo

### Python (backtest e ricerca)
```bash
cd python
pip install -r requirements.txt
python run_portfolio.py                                    # A+B+C, rischio 1%
python run_portfolio.py --rischio 0.005                    # rischio 0,5%
python run_portfolio.py --strategie A_M15,B_H1,C_M30,D_M5 --da 2025-05-10
python run_grid.py H1                                      # rifà la ricerca su un timeframe
```
- **Cambiare una strategia:** modifica i parametri in `strategie.py`.
- **Provare un'idea nuova:** modifica `vtob_v2.py` (funzione `run2`).
- **Nuovi dati:** sostituisci i CSV in `data/` con un nuovo export MT5. Il formato è quello di MT5: colonne `time,open,high,low,close,tick_volume,spread,real_volume`, ora del server, spread in punti (1 punto = 0,01 $).
- **Più storico:** in MT5 imposta Strumenti → Opzioni → Grafici → "Barre massime nel grafico" = Illimitato, poi riesporta (per esempio M5 e M1 su più anni).

**Regole del simulatore**, da mantenere se lo modifichi:
- nessun lookahead: l'OB esiste solo dalla candela di conferma del pivot;
- segnale a candela chiusa, ingresso all'open successivo;
- EMA del timeframe superiore solo da candele già chiuse;
- se una candela tocca sia SL che TP, conta lo SL;
- spread reale della candela di ingresso.

**Leggere le griglie:**
- `PF_IS` / `R_IS` = primo periodo (fino a giugno 2025, oppure gennaio 2026 per M5);
- `PF_OOS` / `R_OOS` = periodo di verifica;
- `tr_wk` = trade a settimana;
- `RoDD` = R totali / drawdown.

Scegli sempre configurazioni buone **in entrambi i periodi** e con parametri vicini altrettanto buoni.

### TradingView
1. Pine Editor → incolla `pine/VTOB_Strategy_Portafoglio.pine` → Aggiungi al grafico.
2. Apri il grafico XAUUSD sul timeframe giusto e scegli il preset: A = M15, B = H1, C = M30, D = M5.
3. Leggi i risultati nello Strategy Tester. Saranno un po' diversi da quelli Python, perché il feed e lo spread di TradingView sono diversi da quelli del broker.
4. Per tradare a mano usa `VTOB_Indicator_Pro.pine`, con gli alert.

### MT5 (automatico)
Compila `mt5/VTOB_Config1_EA.mq5` in MetaEditor (F7) e mettilo su più grafici XAUUSD, ognuno con le sue impostazioni:

| Grafico | Magic | Pivot sx | Pivot dx | Trend da | TF EMA | Stop | Target | Pareggio | Long | Short |
|---|---|---|---|---|---|---|---|---|---|---|
| M15 (A) | 7303001 | 7 | 3 | 20 | H1 | 6 | 3 | 1 | ✔ | ✘ |
| H1 (B) | 7306001 | 10 | 3 | 10 | D1 | 3 | 4 | 1 | ✔ | ✔ |
| M30 (C) | 7330001 | 5 | 2 | 20 | H4 | 8 | 3 | 1 | ✔ | ✔ |
| M5 (D) | 7305001 | 10 | 5 | 20 | H1 | 6 | 4 | 1 | ✔ | ✘ |

Prima di andare live:
1. Strategy Tester MT5 ("ogni tick basato su tick reali") per ogni grafico;
2. 1-2 mesi in demo;
3. poi rischio 0,25–0,5% per trade.

L'EA e le strategy Pine non sono stati compilati: se danno errori, correggili con Claude partendo dal messaggio di errore.

### Con Claude Code
Apri la cartella del pacchetto in Claude Code e incolla `docs/PROMPT_ClaudeCode_StrategiaMigliore.md`. Trova già qui dentro dati, motori e risultati da cui partire.

## Avvertenze
- I risultati sono di backtest. Ho scelto la combinazione migliore tra 46.080 varianti testate, quindi dal vivo aspettati risultati più bassi: un PF intorno a 1,5 sarebbe già buono.
- I guadagni sono concentrati nelle fasi di forte trend dell'oro (2024–2025). Il 2026 finora è stato più debole.
- Con più strategie aperte insieme il rischio si somma: fino a 3–4 posizioni contemporanee.
- I risultati passati non garantiscono quelli futuri.
- Il codice dell'indicatore deriva da "Volume-Trend Order Block Engine" di BigBeluga, licenza CC BY-NC-SA 4.0: uso non commerciale, citando l'autore.
