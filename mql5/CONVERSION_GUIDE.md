# Guida alla conversione Python -> MQL5 (EA MetaTrader 5)

Knowledge base operativa per portare i backtest Python del workspace
(`analysis/**/*.py`) in Expert Advisor MQL5 compilabili e *semanticamente
fedeli*. Usata dall'agente `mql5-converter` e come riferimento umano.

Regola d'oro: **un backtest e un EA che divergono sono un bug, non "il live e'
diverso".** Il cross-check nel Strategy Tester sullo stesso periodo deve
riprodurre win%/E[R] per anno; qualsiasi scostamento va spiegato prima di
considerare il port finito.

---

## 0. Convenzioni del workspace (NON reinventarle)

Estratte dagli EA esistenti (`orb_nasdaq.mq5`, `nxt_fade.mq5`,
`london_breakout.mq5`, `tsmom_jpy.mq5`). Ogni nuovo EA le rispetta.

- `#property strict` sempre. Header a blocco `//+---...` che documenta:
  logica, timezone, status (GO/NO-GO/LEAD), e istruzione di cross-check.
- Include: **preferisci EA AUTOCONTENUTI** -> `#include <Trade\Trade.mqh>` (standard)
  e nient'altro. Le funzioni condivise piccole (`TG_SendMessage`/`TG_UrlEncode`,
  singoli helper) vanno **inlinate** nel `.mq5`. NON dipendere da
  `<TradingSystemWorkspace/*.mqh>` a meno che non usi molte funzioni: quegli include
  virtuali si risolvono in modo fragile (sezione 1b) e sono la causa dell'errore
  "undeclared identifier". `london_breakout`/`tsmom_jpy` usano ancora gli include
  (storico); `nxt_fade`/`orb_nasdaq` sono autocontenuti (modello da seguire).
- **Registro magic number** (uno per strategia, mai riusarli):
  - `london_breakout` = 26050
  - `tsmom_jpy`        = 26060
  - `orb_nasdaq`       = 26052
  - `nxt_fade`         = 26071
  - nuovo EA -> scegli un numero libero (range 26050-26099) e aggiornalo qui.
- Input raggruppati con `input group "=== ... ==="`; ogni parametro
  "congelato" (pre-registrato) va marcato nel commento come CONGELATO.
- Sizing rischio-based via `ComputeVolume(risk_price)` (equity * pct / valore
  per unita' calcolato con TICK_VALUE/TICK_SIZE, arrotondato a VOLUME_STEP,
  clampato a VOLUME_MIN/MAX). `InpFallbackVolume` se i dati simbolo mancano.
- Prezzi normalizzati con `NormalizePrice()` (allineamento a TICK_SIZE, **non**
  al Point) — vedi sezione 4.
- Notifiche via `NotifyTelegram()` con prefissi `[START] [ORDER] [FILL] [BE]
  [SKIP] [EXPIRE] [HOLD] [STOP]`.
- **ASCII PURO** in tutto il sorgente, commenti inclusi (sezione 1).

---

## 1. Encoding: la causa n.1 dei fallimenti di compilazione

MetaEditor tratta i sorgenti come ANSI/UTF-8; caratteri non-ASCII (accenti
`e' a' o'`, virgolette curve `" "`, trattini lunghi, simboli, emoji) in un file
salvato UTF-8 senza BOM producono errori di compilazione o glifi corrotti.

Regole:
- **Solo ASCII 0x20-0x7E** in tutto il `.mq5` e `.mqh` (codice E commenti).
  - `perche'` non `perché`, `e'` non `è`, `pero'` non `però`.
  - virgolette dritte `"` `'`, trattino `-`, niente `->` unicode, niente emoji.
- Se devi generare stringhe runtime con caratteri speciali, costruiscile con
  `ShortToString`/codici, non come letterali nel sorgente.
- Verifica prima di consegnare: nessun byte > 0x7E nel file. Comando di check:
  `grep -nP '[^\x00-\x7E]' file.mq5` (deve restituire vuoto).
- **Anche gli `.mqh` inclusi vengono compilati col `.mq5`**: un emoji/accento in
  `telegram.mqh` o `helpers.mqh` rompe la compilazione dell'EA anche se l'EA e' ASCII.
  Fai il grep ASCII su OGNI file toccato, include compresi. (`telegram.mqh` e
  `helpers.mqh` sono stati bonificati ad ASCII il 2026-07-24.)

Fonti: [UTF-8 encoding in MetaEditor](https://www.mql5.com/en/forum/453883),
[Feature request UTF-8](https://www.mql5.com/en/forum/149488).

---

## 1b. Include-path fragility -> EA autocontenuti (errore "undeclared identifier")

Trappola scoperta portando `nxt_fade`/`orb_nasdaq` (2026-07-24). Sintomo:
compilazione che fallisce con **`undeclared identifier 'TG_SendMessage'`** (+ cascata
di "some operator expected" / "unexpected token" sulla riga della chiamata), pur
avendo il file ASCII.

Causa: `#include <TradingSystemWorkspace/telegram.mqh>` usa il **path virtuale**
degli Include e si risolve **diversamente a seconda di dove apri il file e a quale
terminale/data-folder e' agganciato MetaEditor**. Se il terminale attivo non ha
`MQL5/Include/TradingSystemWorkspace/telegram.mqh`, o ne ha una **copia vecchia**
priva della funzione, il simbolo risulta non dichiarato -> errore al primo uso. Con
piu' terminali installati (qui: due) e file aperti dal repo sul Desktop, e' quasi
garantito che prima o poi punti alla copia sbagliata.

Fix (adottato): **rendere l'EA autocontenuto**. Inlina nel `.mq5` le poche funzioni
che usi davvero (verifica con `grep -oE '\bTG_[A-Za-z]+|\bH_[A-Za-z]+' file.mq5`) e
**rimuovi gli include workspace**; tieni solo `<Trade\Trade.mqh>`. Cosi' l'EA compila
da qualsiasi cartella e qualsiasi terminale, senza dipendere dal path degli Include.
Regola: se usi <= 2-3 helper piccoli, inlinali; non introdurre un include workspace
solo per una funzione.

---

## 2. Differenze semantiche Python -> MQL5 (bug silenziosi)

Queste NON danno errore di compilazione: danno risultati diversi dal backtest.

| Python | MQL5 | Trappola |
|---|---|---|
| `a / b` (float sempre) | `int/int` = **divisione intera** | forza `(double)` se serve il decimale |
| liste 0..n-1 crescente nel tempo | timeseries indicizzate **dal piu' recente**: shift 0 = barra corrente in formazione, shift 1 = ultima **chiusa** | valuta i segnali su shift 1, mai shift 0 |
| `df.iloc[i]` allineato al tuo ordine | `CopyRates`/`CopyBuffer` dipendono da `ArraySetAsSeries` | imposta esplicitamente la direzione dell'array prima di leggerlo |
| indexing negativo `x[-1]` | non esiste | usa shift 1 o `ArraySize-1` |
| `datetime` pandas tz-aware | `datetime` = secondi epoch, **naive**; server, GMT e broker differiscono | vedi sezione 6 (timezone) |
| `for r in rows` su barre chiuse | `OnTick` gira ad ogni tick | gate con new-bar (sezione 3) |
| `nan`/`None` | non esistono; `CopyBuffer` puo' tornare < richiesto | controlla il valore di ritorno, esci se dati incompleti |
| `and/or` su valori | `&&`/`||` booleani | tipi rigidi |
| append dinamico | array dinamici: `ArrayResize`, `ArraySetAsSeries` | non su array statici/multidim |
| costanti globali | ogni funzione top-level ridichiarata; niente closure | passa stato via struct/globali |
| `pd.Series(tr).rolling(n).mean()` = **SMA** del TR | `iATR` usa **Wilder/SMMA**, non SMA | se il .py media il TR con `rolling().mean()`, ricalcola l'ATR come SMA a mano (non usare iATR); vedi sotto |

**ATR: SMA vs Wilder.** Trappola scoperta nel port di `nxt_fade` (2026-07-24).
Il `iATR` di MT5 e l'`H_ATR` del workspace usano lo smoothing di **Wilder (SMMA)**;
molti backtest Python (`analysis/nxt/backtest.py: atr()`) usano invece la **media
semplice** del True Range: `pd.Series(tr).rolling(14).mean()`. I due valori
divergono e, se l'ATR e' una **soglia** (es. filtro ampiezza gamba `rng >= 1*ATR`),
cambiano quali setup passano il filtro -> trade-set diverso, divergenza silenziosa
dal backtest. Fix: se il .py fa `rolling().mean()`, calcola l'ATR come SMA del TR
manualmente su `CopyRates` (TR[i] = max(H-L, |H-Cprev|, |L-Cprev|), media su n),
NON usare `iATR`. Su una finestra di barre contigue reali l'SMA coincide
esattamente col Python (il TR usa la chiusura precedente reale). Esempio:
`AtrSmaAt()` in `nxt_fade.mq5`.

Regola shift: **decidi sull'ultima barra CHIUSA (shift 1)**; entra sulla barra
corrente. Replica esattamente quale barra il Python usava per il segnale.

Fonti: [Indexing direction](https://www.mql5.com/en/docs/series/bufferdirection),
[ArraySetAsSeries](https://www.mql5.com/en/docs/array/arraysetasseries).

---

## 3. Struttura EA e new-bar

Pattern di riferimento (già usato in `orb_nasdaq.mq5`):

```cpp
datetime g_last_bar_time = 0;
void OnTick()
{
   ManageOpenPosition();                    // logica tick-level (fill/BE/stop)
   datetime cur = iTime(_Symbol, InpTimeframe, 0);
   if(cur != g_last_bar_time) { g_last_bar_time = cur; OnNewBar(); }  // 1x/barra
}
```

- Tutte le decisioni di segnale in `OnNewBar()`; solo gestione posizione (BE,
  trailing, max-hold, fill-detect) puo' stare a livello tick.
- Static/global per l'ultimo tempo barra; nel Strategy Tester multi-simbolo il
  static va isolato (una var per simbolo/tf).

Fonte: ["New Bar" event handler](https://www.mql5.com/en/articles/159).

---

## 4. Indicatori: handle + CopyBuffer

- Crea l'handle **una volta** in `OnInit`, controlla `INVALID_HANDLE` ->
  `INIT_FAILED`. **Mai** creare handle dentro `OnTick`/`OnNewBar`.
- Rilascia con `IndicatorRelease` in `OnDeinit`.
- Leggi con `CopyBuffer(handle, buf_idx, start_shift, count, arr)`; **controlla
  il ritorno > 0** prima di usare i valori. Segnale su shift 1 (barra chiusa).
- `H_ATR()` in helpers apre/rilascia l'handle ad ogni chiamata: comodo ma
  costoso in loop — per uso frequente tieni un handle persistente.

Fonte: [New Bar EA from indicator buffers](https://www.mql5.com/en/articles/23015).

---

## 5. Ordini: filling mode, stops level, retcode

Fonti principali di fallimenti runtime (non di compilazione).

### 5.1 Filling mode (errore 10030 TRADE_RETCODE_INVALID_FILL)
Non hard-codare FOK. `CTrade::SetTypeFillingBySymbol(_Symbol)` (già usato) sceglie
un mode valido. Se lavori manualmente, controlla
`SYMBOL_FILLING_MODE` e scegli FOK -> IOC -> RETURN in ordine di supporto. Non
mischiare le costanti `SYMBOL_FILLING_*` (check) con `ORDER_FILLING_*` (set).
Fonte: [Unsupported filling mode](https://www.mql5.com/en/forum/58514).

### 5.2 Stops level / freeze level (errore 10016 INVALID_STOPS)
- SL/TP devono distare almeno `SYMBOL_TRADE_STOPS_LEVEL * _Point` dal prezzo
  corrente (BUY: dal Bid; SELL: dall'Ask).
- `SYMBOL_TRADE_FREEZE_LEVEL`: entro questa distanza non puoi modificare/chiudere
  pending o posizioni. Controlla prima di `OrderModify`/`OrderDelete`.
- I pending LIMIT devono stare oltre stops-level dal prezzo (vedi il ramo
  market-fallback in `orb_nasdaq.Confirm()`).

### 5.3 Normalizzazione prezzo
- **Non** usare `NormalizeDouble` sul Point per allineare i prezzi: usa la
  TICK_SIZE (`NormalizePrice()` del workspace). Su indici/azioni Tick != Point.

### 5.4 Retcode
- Successo = `TRADE_RETCODE_DONE` (10009). Dopo ogni operazione CTrade controlla
  `ResultRetcode()`; logga `GetLastError()` sul fallimento. Non assumere fill.

Fonti: [Invalid stops fix](https://www.mql5.com/en/forum/348327),
[Common EA errors](https://alfatactix.com/academy/mql5-ea/common-mql5-ea-errors).

---

## 6. Timezone (fonte n.1 di divergenza dal backtest su strategie a orario)

- `TimeCurrent()` = ora **server broker**; `TimeGMT()` = GMT; il backtest Python
  ragiona spesso in ET o UTC. Non assumere che server == GMT.
- Se la strategia e' ancorata a un fuso (es. ORB 09:30 ET), replica il calcolo
  DST come in `orb_nasdaq.mq5` (`UsEastDst`, `NthSundayUtc`, offset server).
- Nel Strategy Tester `TimeGMT()` puo' comportarsi diversamente dal live:
  documentalo nell'header e verifica che la finestra catturi le barre giuste.

---

## 7. Strategy Tester: cross-check obbligatorio

Il port non e' "finito" finche' non riproduce il backtest.
1. Gira l'EA nel Tester su stesso simbolo/TF/periodo del `.py`.
2. Confronta win%, E[R], n. trade **per anno**. Divergenza = bug (spesso shift
   di barra, timezone, o costi diversi).
3. Verifica che i costi (spread/commissione) del Tester siano allineati alle
   assunzioni del backtest, altrimenti l'E[R] non e' comparabile.

---

## 8. Checklist finale prima di consegnare

- [ ] Solo ASCII (`grep -nP '[^\x00-\x7E]'` vuoto su .mq5 **e ogni .mqh incluso**).
- [ ] EA autocontenuto: solo `#include <Trade\Trade.mqh>`; helper piccoli inlinati,
      niente include `<TradingSystemWorkspace/*>` (sezione 1b).
- [ ] `#property strict`, header con logica + status + timezone + cross-check.
- [ ] Magic number nuovo e registrato (sezione 0).
- [ ] Handle indicatori in OnInit (check INVALID_HANDLE) + IndicatorRelease in OnDeinit.
- [ ] Segnali su barra chiusa (shift 1), gate new-bar in OnTick.
- [ ] Nessuna divisione intera involontaria; array con ArraySetAsSeries esplicito.
- [ ] Prezzi via NormalizePrice (tick-size); SL/TP oltre STOPS_LEVEL.
- [ ] Filling via SetTypeFillingBySymbol; retcode controllato dopo ogni ordine.
- [ ] Timezone replicata fedelmente se la strategia e' a orario.
- [ ] Sizing rischio-based con fallback; niente lotti hard-coded.
- [ ] Compila senza errori/warning in MetaEditor (sezione 9).
- [ ] Mappa di conversione Python->MQL5 documentata (quale riga .py -> quale blocco).
- [ ] Nota di cross-check Strategy Tester nell'header.

---

## 9. Compilazione da riga di comando (verifica)

Se MetaEditor e' installato, compila headless e leggi il log:

```
"C:\Program Files\MetaTrader 5\metaeditor64.exe" /compile:"<path>\file.mq5" /log:"<path>\file.log"
```

- Il path esatto di `metaeditor64.exe` varia (spesso sotto `C:\Program Files\`
  o la cartella del broker in `%APPDATA%`). Cerca l'eseguibile prima.
- Invocazione da Git Bash: **prefissa `MSYS_NO_PATHCONV=1`** o il path dopo
  `/compile:` viene mangiato dalla conversione path di MSYS e la compilazione non
  parte. L'`.ex5` prodotto (timestamp aggiornato) e' la conferma di successo;
  l'exit code puo' essere != 0 anche con 0 errori.
- Il log e' UTF-16; leggilo (`iconv -f UTF-16LE -t UTF-8`) e itera finche'
  `Result: 0 errors, 0 warnings`.
- Un EA **autocontenuto** (sezione 1b) compila da qualsiasi path. Se invece usi
  ancora include workspace, il `.mq5` deve stare in `MQL5/Experts/...` con gli
  Include in `MQL5/Include/TradingSystemWorkspace/` perche' risolvano.
