# MQL5 — Expert Advisor del workspace

Questa cartella contiene gli **Expert Advisor** scritti in MQL5 nativo per girare dentro il
terminale MetaTrader 5. Sostituiscono le strategie automatiche Python che dipendevano dalla
libreria `MetaTrader5` + MT5 desktop sullo stesso host.

**Perché MQL5 invece di Python**: vedi `C:/Users/mmbus/.claude/plans/adesso-abbiamo-le-basi-tingly-iverson.md`,
sezione "PIVOT ARCHITETTURALE". In sintesi:

- L'EA gira sul terminale ovunque sia installato (PC, MetaQuotes VPS).
- Su MetaQuotes VPS (~10$/mese) è **sempre online**, monitorabile dall'app mobile MT5.
- Niente IPC Python↔MT5, niente PC sempre acceso, niente VPS Windows.
- Strategy Tester nativo per backtest tick-reali è superiore a vectorbt/backtrader sul forex.

## Struttura

```
mql5/
├── london_breakout.mq5         # EA principale (Stage 2.5)
├── include/
│   ├── telegram.mqh            # Helper WebRequest per inviare messaggi Telegram
│   └── helpers.mqh             # Sessioni UTC, blackout NFP/FOMC, ATR, range Asia
└── README.md                   # questo file
```

## Setup terminale MT5 (una tantum)

### 1. Copia file nella cartella `MQL5/Experts/`

Apri il terminale MT5 → `File → Open Data Folder` → si apre Esplora Risorse → vai in `MQL5/`.

Crea (se non esiste) la sottocartella `Experts/TradingSystemWorkspace/` e copia:

```
MQL5/Experts/TradingSystemWorkspace/london_breakout.mq5
MQL5/Include/TradingSystemWorkspace/telegram.mqh
MQL5/Include/TradingSystemWorkspace/helpers.mqh
```

> Nota: aggiusta gli `#include` in `london_breakout.mq5` se cambi la struttura
> sottocartelle. Default: `#include "include/telegram.mqh"` (cartella relativa).

### 2. Compila in MetaEditor

`Tools → MetaQuotes Language Editor` (F4) → apri `london_breakout.mq5` → premi `F7` per
compilare. Il compile non deve produrre errori, eventuali warning in fondo sono ok.

### 3. Abilita WebRequest verso Telegram

`Tools → Options → Expert Advisors`:

- ☑️ `Allow algorithmic trading`
- ☑️ `Allow DLL imports`
- ☑️ `Allow WebRequest for listed URL`
- Aggiungi: `https://api.telegram.org`

Click `OK`.

### 4. Aggancia l'EA al grafico

Apri un grafico **GBPUSD M15**. Trascina l'EA `london_breakout` dalla `Navigator` → `Expert
Advisors` sul grafico.

Si apre il dialogo input. Imposta:

| Input | Valore consigliato | Note |
|---|---|---|
| `InpAsiaStartHourUtc` / Min | 0 / 0 | Sessione Asia: 00:00 UTC |
| `InpAsiaEndHourUtc` / Min | 7 / 0 | Piazzamento ordini: 07:00 UTC |
| `InpEntryWindowEndHourUtc` / Min | 10 / 0 | Cancella pendenti: 10:00 UTC |
| `InpTimeStopHourUtc` / Min | 16 / 0 | Chiusura posizioni: 16:00 UTC |
| `InpBreakoutBufferAtr` | 0.10 | Buffer breakout (frazione di ATR_D1) |
| `InpTpRMultiple` | 1.5 | TP = 1.5R |
| `InpMaxRangeToAtrRatio` | 1.5 | Skip se range > 1.5×ATR |
| `InpAtrPeriod` | 14 | Periodo ATR |
| `InpSkipNfp` | true | Skip primo venerdì del mese |
| `InpFomcBlackoutDatesCsv` | (default) | Aggiorna ogni anno con date FED ufficiali |
| `InpRiskPerTradePct` | 0.01 | 1% equity rischiata per trade |
| `InpFallbackVolume` | 0.10 | Lotti se sizing fallisce |
| `InpTelegramBotToken` | (dal `.env`) | Stesso bot del workspace |
| `InpTelegramChatId` | 1238922215 | Chat Matteo |
| `InpMagicNumber` | 26050 | Identificatore ordini propri |

Tab "Common": ☑️ `Allow algorithmic trading`, ☑️ `Allow live trading`. OK.

In alto a destra del grafico apparirà un faccino sorridente verde se l'EA è attivo.

## Backtest in Strategy Tester

`View → Strategy Tester` (Ctrl+R):

- Expert: `london_breakout`
- Symbol: `GBPUSD`
- Timeframe: `M15`
- Date: 6 mesi indietro a oggi
- Modeling: `Every tick based on real ticks`
- Forward: `No` (per primo backtest)
- Inputs: lascia i default

Premi `Start`. A fine test, controlla:

- Trade frequency 15-20/mese atteso.
- Win rate 45-55% atteso.
- Max drawdown < 10% del balance iniziale.
- Profit factor > 1.0.

Se i numeri sono fuori range, NON deployare in live. Verifica prima con tick model "Open prices
only" che la logica sia corretta, poi alza la qualità.

## Deploy su MetaQuotes VPS

Una volta validato in Strategy Tester e in demo locale per 1-2 settimane:

1. Da app mobile MT5 (o desktop): **Tools → Virtual Hosting** o tab "VPS" in basso.
2. Click `Subscribe` (10$/mese), seleziona regione vicina al broker.
3. Click `Migrate to virtual server`. Tutto lo stato del terminale (EA agganciati, settings,
   chart aperti) viene trasferito sul VPS MetaQuotes.
4. Da quel momento il PC di casa può restare spento. L'EA gira sul VPS.
5. Monitor da app mobile: stato VPS, posizioni aperte, equity, log EA.

## Aggiornare l'EA dopo modifiche

Dopo aver modificato `.mq5`:

1. F7 in MetaEditor per ricompilare.
2. Sul terminale: rimuovi l'EA dal grafico (clic destro → `Expert Advisors → Remove`) e
   ritrascinalo. Le modifiche entreranno in vigore.
3. Se l'EA gira su MetaQuotes VPS: `Migrate to virtual server` di nuovo per propagare.

## Troubleshooting

| Sintomo | Causa probabile | Soluzione |
|---|---|---|
| `WebRequest returned -1` nei log | URL non in whitelist | Aggiungi `https://api.telegram.org` in Options |
| Compile error "include not found" | Path `include/*.mqh` errato | Verifica struttura cartelle MQL5/Include |
| EA non piazza ordini | AutoTrading rosso o magic-conflict | Pulsante AutoTrading verde, magic_number unico |
| Nessuna candela M15 nel range Asia | Mercato chiuso (weekend, holiday) | Atteso. EA salta il giorno automaticamente. |
| Strategy Tester non trova tick reali | Tick history non scaricata | Tools → History Center → scarica GBPUSD M15+M1 ultimo anno |

## Riferimenti

- Doc ufficiale MQL5: `docs.mql5.com`
- WebRequest + Telegram: `mql5.com/en/articles/working-with-telegram` (Yashar Seyyedin, 2022)
- Standard Library `<Trade\Trade.mqh>`: `docs.mql5.com/standard_library/trade`
- Helper riutilizzabili: vedi `include/` di questa cartella, MIT-style.
