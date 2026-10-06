---
titolo: Strategia manuale di Matteo (livelli + limit order, RR minimo 1:3)
fonti:
  - "file di Matteo, ritrovato e portato nel workspace il 2026-10-06 (data di scrittura non nota)"
tipo: strategia_candidata
stato: non testabile in backtest (discrezionale); componente meccanica gia' chiusa
aggiornato: 2026-10-06
---

# Strategia manuale di Matteo

> **Perche' e' qui.** Per averla nel workspace (Matteo, 06/10). Matteo stesso la ritiene non testabile.
> Sotto, il testo originale **senza modifiche**. Prima, cosa dicono gia' i verdetti del repo sulle sue parti.

## Cosa e' gia' stato misurato, pezzo per pezzo

| parte della strategia | stato nel repo | fonte |
|---|---|---|
| livelli S/R + S/D + Fibonacci in confluenza come zone dove il prezzo reagisce | **CLOSED**: 384 trial, nessun livello batte il random su nessun timeframe; riconfermato dall'audit A5 | DECISIONS 2026-07-06/07, 2026-09-18 (5) |
| confluenza a 2 criteri come filtro (Level Analyzer, conf=2) | **NO-GO** in forward: i livelli non sono zone di reazione | DECISIONS 2026-07-05 |
| Fibonacci come livello d'ingresso (NXT, ex-soci) | continuazione NO-GO (−0,118R), fade **KILL** | DECISIONS 2026-09-17 (4), 2026-09-18 (5) |
| "a RR 1:3 basta vincere il 25%" | aritmetica del pareggio, non una misura: e' la voce **M1** del registro dei bias | `global/registro-epistemico/matteo.md` |
| payoff 1:3 con payout ravvicinati in prop | incompatibile con una consistency del 40% (vincolo di forma, non di vantaggio) | DECISIONS 2026-08-07, PROP_FIRM_CRITERIA §1.5 |

**Cosa NON e' stato misurato:** le parti discrezionali, cioe' quali livelli scegli a occhio, il bias macro e la
conferma visiva su M15. Quelle non si misurano in backtest: si misurano **in forward**, come il mentore. Ogni
ordine annotato *prima* (livello, SL, TP, motivo), esiti registrati senza cancellazioni, soglia di valutazione
dichiarata prima di guardare (STRATEGY_LIFECYCLE §8bis). E' lo stesso metodo che vale per il track record del socio discrezionale.

**Se mai la si opera:** il doppio binario (§4quater) si applica anche qui. Verdetto sul rischio fisso 1R, e il
BE a +1R della regola 6 e' una regola d'uscita da misurare per ablazione (con e senza), non un overlay.

## Testo originale

```text
ANALISI WEEKLY (weekend, 45-60min)
├── TF Monthly/Weekly: identificare trend macro, livelli S/R major
├── Scendere a H4/H1: raffinare livelli, zone S/D, Fibonacci
├── Per ogni pair (EURUSD, XAUUSD):
│   └── Segnare 2-4 livelli chiave dove il prezzo potrebbe reagire
│       (confluenza S/R + S/D + Fibonacci = livello forte)
├── DXY: stessa analisi come contesto
├── Risultato: "mappa dei livelli" della settimana
└── Configurare alert su TradingView per ogni livello

AGGIORNAMENTO GIORNALIERO (10-15min, pre-sessione)
├── Controllare calendario news del giorno
├── Verificare: i livelli segnati sono ancora validi?
│   (il prezzo non li ha già attraversati/invalidati)
├── Aggiornare massimi/minimi giornalieri
└── Decisione: piazzare ordini / aggiornare ordini / no trade oggi
CONDIZIONI PER PIAZZARE UN LIMIT ORDER:

1. LIVELLO IDENTIFICATO nell'analisi (S/R, S/D, Fibonacci in confluenza)
2. DIREZIONE coerente con bias macro (trend W/D/H4)
3. TIPO ORDINE:
   - Buy Limit: piazzato SOTTO il prezzo attuale, su supporto/demand/Fibonacci
   - Sell Limit: piazzato SOPRA il prezzo attuale, su resistenza/supply/Fibonacci
4. STOP LOSS: fisso, strutturale
   - EURUSD: 15-30 pips sotto/sopra il livello
   - XAUUSD: basato su ATR, 80-150 pips (⚠ da rifinire con pratica)
5. TAKE PROFIT:
   - MINIMO R:R 1:3 (al prossimo livello strutturale)
   - Aggiustabile SOLO in aumento (se si identifica target più lontano)
   - MAI ridurre sotto 1:3
6. GESTIONE POST-ENTRATA:
   - A +1R (1:1): spostare SL a Break Even
   - Lasciar correre fino a TP
   - Nessun altro intervento

ORDINE PIAZZATO = set and forget (fino a BE trigger)

NON piazzare ordine se:
- News alto impatto previste entro 30min dal livello stimato di attivazione
- Livello ha già una confluenza debole (solo 1 criterio su 3: S/R, S/D, Fib)
- SL necessario > 30 pips (EU) o > 200 pips (XAU) → livello troppo largo
- RR < 1:3 anche al TP minimo
- Già 2 ordini attivi contemporaneamente sullo stesso pair
- Il livello è stato già testato e rigettato oggi (invalidato)
- Spread anomalo al momento del piazzamento
- Fuori sessione operativa (prima 9:00, dopo 18:00 Roma)

TRIGGER: alert TradingView ti notifica che il prezzo si avvicina a un livello
SE hai tempo di andare a grafico:
├── Scendi a M15
├── Aspetta conferma candela (engulfing, pinbar, chiusura forte)
├── Entrata manuale con conferma visiva
├── SL e TP come da regole standard
└── Vantaggio: entrata più precisa, SL potenzialmente più stretto → RR migliore
Supply,demand quantitativo, indicatori per identificare trend.
```
