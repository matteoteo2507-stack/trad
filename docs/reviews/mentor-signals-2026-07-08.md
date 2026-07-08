# Segnali mentore (XAUUSD) — Audit su prezzo reale — 2026-07-08

> Track A del pivot. Parser [analysis/mentor_signals/parse.py](../../analysis/mentor_signals/parse.py)
> → replay [analysis/mentor_signals/backtest.py](../../analysis/mentor_signals/backtest.py) sul feed
> reale M5 (`XAU_spot_M5.csv`, 2026-01-21→2026-06-12). **Non è un backtest disegnato da noi**: è il
> suo **track record live** (segnali postati in tempo reale) verificato contro prezzo reale indipendente.

## Dati
552 segnali parsati (547 completi con SL+TP), 2026-01-21→2026-07-08, BUY 310/SELL 242, tutti XAUUSD.
**Riconciliazione confermata**: gli entry stanno dentro i range intraday dell'oro reale (es. 2026-01-22
mentore 4812-4831 vs reale 4772-4940; range 2026 mentore 3964-5553 vs reale 3999-5415). *Il "4670" che
avevo flaggato era un segnale di metà 2026, con l'oro in discesa da ~5400 a ~4150 — falso-flag chiuso.*
Coperti da M5 e replayati: **477** (fill entro 6h). Ultimo mese (Giu12-Lug8) non coperto da M5.

## Risultati (dopo costo $0.30; bound pess/opt = ordine intrabar non risolvibile su alcune barre)
| misura | Mentore (side reale) | Baseline side casuale |
|---|---|---|
| win-rate simmetrica (+1R prima di −1R) | **67.3% / 72.5%** | 31.9% / 41.2% |
| exit TP1, E[R] | **+0.203 / +0.321** | −0.455 / +0.390 |
| exit TP3, E[R] | +0.289 / +0.379 | −0.396 / +0.952 |
| TP1 hit% reale (vs suo claim ~100%) | **83-91%** | — |

**Robustezza al ritardo di copia manuale** (entry a mercato, SL/TP assoluti, exit TP1):
0min **+0.315** · 5min +0.292 · 15min +0.284 · 30min **+0.216** · 60min +0.120 → **positivo fino a 60'**.
**Stabilità mensile** (win-rate simmetrica pess): Gen 65% · Feb 61% · Mar 64% · Apr 77% · Mag 71% · Giu 70%
→ **tutti > 60%**, non un mese solo.

## Verdetto
**Edge direzionale reale sull'oro, robusto e baseline-controllato** — il PRIMO positivo del percorso.
La sua *direzione* è giusta ~2/3 delle volte (67% vs 32% del side casuale sulla stessa geometria/tempi →
non è "l'oro ha trendato"). Positività confermata da 5 angoli indipendenti + tolleranza al ritardo +
stabilità sui 6 mesi. Il suo claim "TP HIT ~100%" è in realtà ~85% (ottimismo lieve, edge vero sotto).

## Caveat onesti (vincolanti)
1. **È una COPIA, non un edge nostro**: dipende dal mentore che continua a postare e a essere bravo
   (key-man risk). Non è un generatore autonomo.
2. **6 mesi, 1 asset, 1 regime** (oro in discesa 5400→4150 in H1-2026): non visto in uptrend forte o
   chop; possibile regime-dipendenza. Ultime 4 settimane non replayate (dati M5).
3. **Esecuzione idealizzata**: feed M5 spot vs suo broker; spread/slippage reali oltre $0.30. Il test
   di ritardo mitiga ma non elimina.
4. **Survivorship**: non escludibile del tutto che segnali persi siano stati cancellati prima
   dell'export; ma il baseline casuale (32%) e la presenza di "Sl hit"/"Running loss" nel canale
   remano contro la curatela pura.
5. **Non è il milestone "1 mese demo NON supervisionato"**: le prop vietano l'auto → è il track
   **manuale** (utilizzabile col telefono, che ORA non hai). Vale per quella traccia, non per l'unsupervised.

## Azione raccomandata
**Forward paper-validation live**: usare il parser per ingerire i nuovi segnali man mano e registrarli
+ replay sul prezzo reale in avanti (out-of-sample vero) per ~4-6 settimane, misurando anche l'esecuzione
reale e il decadimento da ritardo. Se tiene → è l'edge da operare **manualmente** sulle prop quando avrai
il telefono. In parallelo, la traccia "sistema nostro" prosegue (prossimo edge del backlog).

### Riproducibilità
`python analysis/mentor_signals/parse.py && python analysis/mentor_signals/backtest.py` (dalla root).
