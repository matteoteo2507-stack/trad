# Dataset: ingressi di un signal provider XAUUSD (analisi in cieco)

Obiettivo dell'analisi: **scoprire il criterio d'ingresso** di questo trader a
partire dai suoi trade e dal contesto di prezzo. NON ci sono conclusioni qui: le
devi derivare tu dai dati.

## File

- `trades.csv` — 32 trade. Colonne:
  - `n` progressivo, `ts_utc` timestamp del segnale in **UTC** (ISO, suffisso Z),
  - `side` BUY/SELL, `entry` prezzo d'ingresso dichiarato, `sl` stop loss,
  - `tp1,tp2,tp3` take profit, `outcome` esito (ALL=tutti i TP, TP2, TP1, SL).
  - Nota struttura fissa: SL ~$10, TP a +$5/+$10/+$15 dall'entry. Asset XAUUSD
    (1 "pip" = $0.10). Strategia di scalping, 1-2 trade per sessione.

- `bars_D1.csv`, `bars_H1.csv`, `bars_M15.csv`, `bars_M5.csv` — OHLCV continui di
  XAUUSD. Indice `time` in **UTC** (stessa scala di `ts_utc`). Colonne:
  `open, high, low, close, volume` (volume = tick volume MT5).

## Allineamento temporale (verificato)

Le barre sono etichettate in UTC reale, **coerenti** con `ts_utc` dei trade. Per
ogni trade, una barra M5 con `time` ~ `ts_utc` (arrotondato a 5') contiene
l'ingresso. Quindi puoi incrociare direttamente trade e barre per timestamp.

## Regola tassativa: niente look-ahead

Per analizzare un ingresso usa **solo barre con `time <= ts_utc`** di quel trade
(anzi, scarta la barra in formazione che contiene l'ingresso, per non guardare il
futuro intrabar). Ogni feature/contesto va calcolato sui dati disponibili *prima*
dell'ingresso.
