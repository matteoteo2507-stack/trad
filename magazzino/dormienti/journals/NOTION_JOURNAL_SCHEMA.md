# Notion Trading Journal — Schema

Contratto operativo del database Notion `Trading Journal`. **Se modifichi il database
su Notion (aggiungi/togli proprietà, rinomini, cambi opzioni dei Select), aggiorna
questo file di conseguenza.** È la fonte di verità per documentazione, futura
analytics Python e Claude via connector.

> Per istruzioni step-by-step su come creare il database, vedi
> [`NOTION_SETUP_GUIDE.md`](NOTION_SETUP_GUIDE.md).

---

## Nome database

`Trading Journal`

## Proprietà

### Identificazione

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Title` | Title | Formato libero, es. `EURUSD 2026-05-18 L #1`. ID umano. |
| `Data` | Date | Include time. Apertura del trade. |
| `Modalità` | Select | `Live` / `Demo` / `Backtest` |
| `Account` | Select | `IBKR Live`, `MT5 Demo`, `Backtest GBPUSD M15`, ... — estendibile |

### Strumento & direzione

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Simbolo` | Select | `EURUSD`, `XAUUSD`, `GBPUSD`, ... — estendibile |
| `Direzione` | Select | `Long` / `Short` |
| `Strategia/Setup` | Select | `Confluence S/D`, `London Breakout`, `Manuale PA`, ... |
| `Timeframe contesto` | Select | `D1` / `H4` / `H1` / `M15` |

### Esecuzione

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Entry price` | Number | 5 decimali forex / 2 decimali XAU |
| `Stop Loss` | Number | stessi decimali di Entry |
| `Take Profit` | Number | stessi decimali di Entry |
| `Exit price` | Number | riempito a chiusura; vuoto se Esito=Open |
| `Size (lotti)` | Number | lotti o frazione (es. 0.10) |
| `Rischio %` | Number, format Percent | % equity rischiata (calcolata su SL distance) |
| `Esito` | Select | `TP` / `SL` / `BE` / `Manuale` / `Time stop` / `Open` |
| `R realizzato` | Formula | vedi sotto |
| `Durata (min)` | Number | chiusura - apertura, in minuti |

### Contesto

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Setup ID` | Text | es. `EURUSD-2026W19-S1` — riferimento a `levels.yaml` / journal markdown |
| `Confluenze` | Multi-select | vocabolario di `levels.yaml`: `SR_D1`, `SR_H4`, `SD_D1`, `SD_H4`, `Fib_236`, `Fib_382`, `Fib_50`, `Fib_618`, `Fib_786`, `POC_weekly`, `POC_monthly`, `VAH_weekly`, `VAL_weekly`, `vwap_daily`, `round_number`, `DXY_aligned`, ... |
| `News rilevanti 2h prima` | Checkbox | per filtrare statistiche post-news |

### Qualitativi

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Emozione pre-trade` | Select | `Lucido` / `Neutro` / `FOMO` / `Paura` / `Revenge` / `N/A (backtest)` |
| `Deviazione dal piano` | Multi-select | `Nessuna` / `Entrata anticipata` / `SL spostato` / `Size aumentata` / `TP anticipato` / `Altro` |
| `Lezione appresa` | Text | UNA frase, end-of-day |

### Note operative

| Nome | Tipo | Opzioni / Note |
|---|---|---|
| `Note libere` | Text | osservazioni extra |

---

## Formula `R realizzato`

Da incollare come **Formula property** (sostituire `R realizzato` Number con
Formula se preferisci il calcolo automatico):

```
if(prop("Esito") == "Open",
   "",
   if(prop("Direzione") == "Long",
      (prop("Exit price") - prop("Entry price")) / (prop("Entry price") - prop("Stop Loss")),
      (prop("Entry price") - prop("Exit price")) / (prop("Stop Loss") - prop("Entry price"))
   )
)
```

Restituisce un numero (positivo = win, negativo = loss) in unità di R. Stringa vuota
se il trade è ancora aperto, per non confondere le statistiche.

---

## Viste

| Nome vista | Tipo | Filtro | Sort | Scopo |
|---|---|---|---|---|
| `All trades` | Table | nessuno | `Data` desc | Default, vista completa |
| `Aperti` | Table | `Esito = Open` | `Data` desc | Tracking real-time |
| `Live` | Table | `Modalità = Live` | `Data` desc | Statistiche reali |
| `Per setup` | Board | nessuno | — | Group by `Strategia/Setup` |
| `Deviazioni` | Table | `Deviazione dal piano` ≠ `Nessuna` (e non vuoto) | `Data` desc | Review settimanale comportamentale |

---

## Convenzioni di compilazione

- `Title`: formato `<SYMBOL> <YYYY-MM-DD> <L|S> #<N>`. Esempio: `XAUUSD 2026-05-19 S #2`.
- `Setup ID` vuoto se il trade è discrezionale fuori da un setup pianificato weekend.
- `Confluenze`: minimo 2 elementi di natura diversa (S/R + Fib, S/D + POC, ecc.).
  Stessa regola di `TRADING_PRINCIPLES.md` §5.
- Modalità `Backtest`: `Emozione pre-trade` = `N/A (backtest)`, `Deviazione dal piano`
  = `Nessuna`, `Lezione appresa` lasciata vuota (il backtest non insegna lezioni
  comportamentali).
- Modalità `Live` / `Demo`: tutti i campi qualitativi vanno compilati, anche solo
  per dire "Nessuna" / "Lucido". Lasciarli vuoti rompe l'analisi futura.

---

## Estensioni future (non implementate ora)

- `Screenshot pre-trade` / `Screenshot post-trade` (Files & media) — utile per
  rilettura visiva price action; aggiungere se senti il bisogno.
- `Qualità setup A/B/C` (Select) — grading prima dell'entrata, permette filtri
  statistici sui soli A-setup.
- `MAE` / `MFE` (Number) — max adverse/favorable excursion, utili per capire se
  esci troppo presto. Richiede dati da broker, non sempre disponibili.
- `Spread/commissioni` (Number) — necessario solo se vuoi calcolare net PnL preciso.

Quando aggiungi un campo, **aggiorna questo file** e la sezione "Estensioni future"
sposta il campo nella sezione attiva.
