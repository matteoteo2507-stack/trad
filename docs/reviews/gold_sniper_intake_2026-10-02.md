---
tipo: analisi
stato: chiuso
aggiornato: 2026-10-02
fonte_dati: "export Telegram del canale 'THE GOLD SNIPER' in goldsniper/ (1 file, 13/08/2026 → 02/10/2026); cartella eliminata dall'utente il 03/10 dopo la chiusura, i numeri restano in questa nota"
nota: "CHIUSO all'intake il 02/10 (decisione di Matteo), 0 trial. gold_5tp disattivato per sempre."
---
# Canale "THE GOLD SNIPER": intake

> Secondo canale portato dal socio il 02/10. Analizzato nel **testo**, con il parser live del nostro copier
> (`signal_copier/parsers/gold_5tp.py`), quindi letto esattamente come lo leggerebbe il copier.

## 1. È il canale `gold_5tp` che il nostro copier seguiva

Formato e refuso coincidono con il parser `gold_5tp` (canale `gfetyydh8959` in
[config.yaml](../../signal_copier/config.yaml)), compreso "READY FOR GOLD Sl**G**NAL" con la "l"
minuscola, presente anche nel nostro log live di giugno (`logs/messages_received.jsonl`). È **quasi
certamente lo stesso canale**: l'handle non compare nell'export. Il copier lo ha seguito in demo a giugno,
ed è disattivato dal 02/10 per un altro motivo (il test N = 60 prevede solo XAT).

## 2. Che cosa contiene

| | |
|---|---|
| Periodo | 13/08/2026 → 02/10/2026 (7 settimane: l'export parte da una data, non dall'inizio del canale) |
| Messaggi | 633, un solo autore |
| Segnali | **78** (51 BUY, 27 SELL); 7 con refusi che il parser legge male (es. TP a −41.797) |
| Geometria | `GOLD BUY 4410/4407 · TP¹ 4413 · TP² 4416 · TP³ 4419 · TP⁴ 4422 · SL 4400`: TP ogni **3 $**, SL a **10 $** → TP1 = **0,3R**, pareggio sopra il **77%** di vittorie |
| Esiti dichiarati dal canale | 54 "all hit", 12 fino al TP3, 8 fino al TP2, 4 senza esito. **Nessuno stop, mai** |
| Id mancanti dentro la finestra | **236 su 823 (28,7%)**: XAT ne ha il 16%, Ben il 3% |

## 3. Cosa vende

24 post di "recupero perdite" e gestione conti, con un contatto Telegram (handle omesso), in inglese e farsi. 5 chiedono
**i dati del conto**:

- *"Don't wory send me account details i recover your loss"*
- *"I will Recover Your All losses · Safe trading MT4-MT5 · If anyone Account Running in loss send to me…"*
- *"CPI News offer · Minimum Deposit 500$ Profit average 1200$"*
- *"Profit Share 50 50 · Safe your Account · Management Available"*

Chiedere le credenziali di un conto MT4/MT5 a chi sta perdendo è un furto di conti, non un servizio.

## 4. Raccomandazione

**Chiudere all'intake, 0 trial**, per le stesse ragioni di Ben
([ben_gold_trader_intake_2026-10-02.md](ben_gold_trader_intake_2026-10-02.md)), qui più gravi:

1. **Nessun razionale economico**: il canale guadagna da depositi e conti consegnati, non dai segnali.
2. **Track record impossibile da credere e con quasi un terzo dei messaggi spariti**: 78 segnali con stop a
   10 $ e nessuno stop ammesso in 7 settimane, con il 28,7% di id mancanti. È la forma della selezione
   misurata su XAT, solo più estrema.
3. **Campione corto**: 7 settimane non bastano per nessun test, anche se il campione fosse pulito.

**Conseguenza sul copier:** `gold_5tp` resta **disattivato per sempre**, non solo per il test N = 60. Il
parser può restare nel repo come codice.

⚠️ **Per il socio:** non inviare dati di conti, login o password, e non contattare l'account indicato in quei post.
