# Stagionalità / calendario (Turn-of-Month) — PRE-REGISTRAZIONE (anti-p-hacking)

> **Committata PRIMA dei risultati.** 2026-07-08. Terzo e **ultimo** edge sistematico del pivot (patto
> con l'utente: se nulla, si smette l'edge-hunting e si rafforza il pilastro passivo). Contratto: spec,
> universo, varianti, metrica, criteri e kill-switch fissati qui *a priori*; dopo i numeri non si cambiano.
> Riusa `core/quant_metrics.py` e la struttura `strategies/tsmom/backtest.py`.

## Domanda (una sola)
Esiste un effetto **Turn-of-Month** (i rendimenti si concentrano attorno al cambio di mese) **reale,
dopo costi, out-of-sample e su più asset** — cioè i rendimenti nella finestra di cambio-mese sono
**abnormalmente più alti** del resto del mese, non solo "positivi" (che sarebbe drift/beta)? Razionale:
**flussi strutturali di calendario** (rebalancing di fine mese, stipendi/pensioni, liquidità/pagamenti —
Ogden 1990; Etula-Rinne-Suominen-Vuolteenaho 2020 "Dash for Cash"). NON è geometria del grafico né beta:
è un effetto di *timing* legato al calendario. Documentato soprattutto sugli **indici azionari**.

## Universo (16 asset, D1) — feed demo4 validato
Stesso di TSMOM/MR. Si testa su **tutti**; l'atteso è che l'effetto (se c'è) sia sugli **indici**
(US500, US100) ed eventualmente sugli asset di rischio; verdetto per **breadth** onesto.

## Definizione (fissa)
- **Finestra TOM (primaria)**: un giorno è "TOM" se è **l'ultimo giorno di trading del suo mese**
  (rank-dal-fondo = 1) **oppure** tra i **primi 3 giorni di trading del suo mese** (rank-dall-inizio ≤ 3).
  Copre entrambi i lati di ogni confine di mese (≈ 4 giorni/mese ≈ 20% del tempo).
- **Metrica primaria (isola dal beta)**: per asset, **(media rendimento giornaliero TOM) − (media
  non-TOM)**, annualizzata. L'edge è la **differenza**, non il livello (long-sempre = beta).
- **Baseline giorni-casuali (il controllo che conta)**: si estraggono ripetutamente **lo stesso numero**
  di giorni a caso e si calcola la stessa differenza → distribuzione null → **p-value** dell'osservato.
  (Stessa filosofia del random distance-matched dei livelli.)
- **Strategia tradabile**: **long durante TOM, flat altrimenti**, vol-target per asset (σ_target 10%,
  vol 60g). Si confronta il suo Sharpe col **buy&hold** vol-normalizzato: se TOM (~20% del tempo) cattura
  una **frazione sproporzionata** del rendimento → concentrazione reale; se ~proporzionale → solo beta.
- **Look-ahead-safe**: il calendario è noto in anticipo; la posizione a close t guadagna il ritorno t+1.
- **Costi**: per turnover (entry/exit della finestra), stessi bps a priori (FX 2, XAU/XAG 4, indici 3,
  crypto 8).

## Varianti pre-registrate (per DSR/molteplicità) — "numero di trial"
Finestra ∈ { [−1,+3], [−1,+2], [0,+3], [−2,+3] } = **4 varianti**. Primaria = **[−1,+3]**.
`n_trials = 4` per il DSR.

## Metriche/validazione (via `core/quant_metrics.py`)
- **(TOM − nonTOM)** per asset + **pooled**, con **CI block-bootstrap sui MESI** + **p-value baseline
  giorni-casuali**.
- **Breadth**: quanti asset hanno (TOM−nonTOM) CI>0.
- Strategia long-TOM/flat: **BCa CI** sullo Sharpe, **DSR** (n_trials=4), **MC-permutation**,
  **walk-forward** (anchored 5y/1y), maxDD, per-anno; frazione del rendimento B&H catturata + time-in-market.

## Regola di decisione (a priori)
**GO** se la finestra primaria, dopo costi, soddisfa TUTTE: (1) (TOM−nonTOM) pooled CI>0 **e** p-value
baseline giorni-casuali < 0.05; (2) **breadth > 50%** degli asset (o, in subordine dichiarato, effetto
robusto su **entrambi** gli indici US500+US100 con CI>0 — ma allora è un edge **stretto**, non broad);
(3) la strategia long-TOM ha **BCa Sharpe lower > 0** e **DSR significant_95**; (4) maggioranza anni positivi.

**KILL-SWITCH (NO-GO)** se: (TOM−nonTOM) non batte i giorni casuali, **oppure** breadth < 50% e non
robusto sugli indici, **oppure** BCa lower ≤ 0, **oppure** DSR n.s. → **patto attivato**: si chiude la
ricerca di edge sistematici own; il reddito passa dal **mentore (manuale)**, e il lavoro si sposta sul
**pilastro passivo** (struttura + protezione). Nessun edge broad = mercato efficiente sul timing anche qui.

## Impegni anti-overfitting (vincolanti)
Varianti/finestre/costi fissati qui; nessun tuning per-asset; **differenza TOM−nonTOM** (non il livello,
per non spacciare beta per edge); baseline **giorni-casuali** matchato sul conteggio; block-bootstrap
sui mesi; DSR sul vero numero di varianti; verdetto per breadth/CI, mai best-asset; forward per l'eventuale
sopravvissuto.
