# Notion Trading Journal — Setup Guide

Guida operativa per creare il database `Trading Journal` su Notion. Tempo stimato:
**15-20 minuti** la prima volta.

Lo schema autoritativo (proprietà, tipi, opzioni) è in
[`NOTION_JOURNAL_SCHEMA.md`](NOTION_JOURNAL_SCHEMA.md). Questa guida è la procedura
pratica per metterlo in piedi.

---

## Step 1 — Crea il database

1. Apri Notion (web o app).
2. Nella sidebar, crea una nuova pagina chiamata **`Trading`**. Sarà il workspace di
   trading; dentro ci metterai il journal e in futuro altre cose (analisi, idee).
3. Dentro la pagina `Trading`, digita `/database` e seleziona **`Database - Full page`**.
4. Rinomina il database in **`Trading Journal`**.

A questo punto hai un database vuoto con due colonne di default: `Name` (Title) e
`Tags`. Cancella `Tags`.

---

## Step 2 — Rinomina la proprietà Title

1. Click sulla colonna `Name` → `Edit property` → rinomina in **`Title`**.

---

## Step 3 — Aggiungi le proprietà nell'ordine

Per ogni proprietà sotto: click sul `+` a destra delle colonne → `New property` →
inserisci nome e tipo. Per i `Select` e `Multi-select` aggiungi anche le opzioni
dalla prima entry che crei (o pre-creandole nelle proprietà).

> Suggerimento: crea le proprietà nell'ordine dato, così la tabella resta leggibile.

### Identificazione

1. `Data` — Date — **Toggle "Include time" attivo**.
2. `Modalità` — Select — opzioni: `Live`, `Demo`, `Backtest`.
3. `Account` — Select — opzioni iniziali: `IBKR Live`, `MT5 Demo`, `Backtest GBPUSD M15`.
   Le aggiungi via via.

### Strumento & direzione

4. `Simbolo` — Select — opzioni iniziali: `EURUSD`, `XAUUSD`, `GBPUSD`. Estendibile.
5. `Direzione` — Select — opzioni: `Long`, `Short`.
6. `Strategia/Setup` — Select — opzioni iniziali: `Confluence S/D`, `London Breakout`,
   `Manuale PA`. Estendibile.
7. `Timeframe contesto` — Select — opzioni: `D1`, `H4`, `H1`, `M15`.

### Esecuzione

8. `Entry price` — Number — Number format: `Number` (precisione default).
9. `Stop Loss` — Number.
10. `Take Profit` — Number.
11. `Exit price` — Number.
12. `Size (lotti)` — Number.
13. `Rischio %` — Number — Number format: **`Percent`**.
14. `Esito` — Select — opzioni: `TP`, `SL`, `BE`, `Manuale`, `Time stop`, `Open`.
15. `R realizzato` — **Formula** (vedi Step 4 sotto).
16. `Durata (min)` — Number.

### Contesto

17. `Setup ID` — Text.
18. `Confluenze` — Multi-select — opzioni iniziali (incollabili una per riga
    durante la creazione): `SR_weekly`, `SR_D1`, `SR_H4`, `SR_H1`, `SD_D1`, `SD_H4`,
    `SD_H1`, `Fib_236`, `Fib_382`, `Fib_50`, `Fib_618`, `Fib_786`, `Fib_1272`,
    `Fib_1618`, `Fib_2618`, `POC_weekly`, `POC_monthly`, `VAH_weekly`, `VAL_weekly`,
    `HVN`, `LVN`, `vwap_daily`, `vwap_weekly`, `round_number`, `psychological`,
    `trendline`, `channel_upper`, `channel_lower`, `ath`, `atl`, `prior_day_high`,
    `prior_day_low`, `DXY_aligned`.
19. `News rilevanti 2h prima` — Checkbox.

### Qualitativi

20. `Emozione pre-trade` — Select — opzioni: `Lucido`, `Neutro`, `FOMO`, `Paura`,
    `Revenge`, `N/A (backtest)`.
21. `Deviazione dal piano` — Multi-select — opzioni: `Nessuna`, `Entrata anticipata`,
    `SL spostato`, `Size aumentata`, `TP anticipato`, `Altro`.
22. `Lezione appresa` — Text.

### Note

23. `Note libere` — Text.

---

## Step 4 — Aggiungi la formula `R realizzato`

Quando crei la proprietà `R realizzato`, selezione tipo **`Formula`** (non Number).
Poi nella formula incolla:

```
if(prop("Esito") == "Open",
   "",
   if(prop("Direzione") == "Long",
      (prop("Exit price") - prop("Entry price")) / (prop("Entry price") - prop("Stop Loss")),
      (prop("Entry price") - prop("Exit price")) / (prop("Stop Loss") - prop("Entry price"))
   )
)
```

Salva. Per i trade ancora aperti (`Esito = Open`) restituisce stringa vuota — utile
per non sporcare le statistiche.

---

## Step 5 — Crea le viste

In alto a sinistra del database, vicino al nome della vista corrente (`Table`),
click `+ Add view`.

### Vista 1 — `All trades` (rinomina la default)

- Tipo: `Table`
- Sort: `Data` descending
- Nessun filtro

### Vista 2 — `Aperti`

- Tipo: `Table`
- Filter: `Esito` = `Open`
- Sort: `Data` descending

### Vista 3 — `Live`

- Tipo: `Table`
- Filter: `Modalità` = `Live`
- Sort: `Data` descending

### Vista 4 — `Per setup`

- Tipo: `Board`
- Group by: `Strategia/Setup`
- Nessun filtro

### Vista 5 — `Deviazioni`

- Tipo: `Table`
- Filter: `Deviazione dal piano` `does not contain` `Nessuna` AND `Deviazione dal piano` `is not empty`
- Sort: `Data` descending

---

## Step 6 — Test con un trade fittizio

Crea una entry di prova per validare la formula e le opzioni:

- `Title`: `EURUSD 2026-05-18 L #TEST`
- `Data`: oggi
- `Modalità`: `Demo`
- `Account`: `MT5 Demo`
- `Simbolo`: `EURUSD`
- `Direzione`: `Long`
- `Strategia/Setup`: `Confluence S/D`
- `Timeframe contesto`: `H4`
- `Entry price`: 1.16500
- `Stop Loss`: 1.16400
- `Take Profit`: 1.17000
- `Exit price`: 1.16900
- `Size (lotti)`: 0.10
- `Rischio %`: 1
- `Esito`: `Manuale`
- `Durata (min)`: 240
- `Confluenze`: `SR_D1`, `Fib_618`
- `Emozione pre-trade`: `Lucido`
- `Deviazione dal piano`: `Nessuna`
- `Lezione appresa`: `Test entry per validare schema.`

Verifica che `R realizzato` mostri `4.0` (= (1.16900 - 1.16500) / (1.16500 - 1.16400) = 0.004 / 0.001 = 4).

Una volta verificato → **cancella la entry di test**.

---

## Step 7 — Pin alla sidebar

Click sui `...` accanto al nome del database → `Add to favorites` (o trascina nella
sidebar). Così lo apri in 1 click da mobile e desktop.

---

## Step 8 — Mobile

Installa l'app Notion su Android/iOS, login con lo stesso account. Il database
appare nei preferiti, compilabile via:
- Tap su `New` → si aprono i campi
- Per i Select, basta tap → scegli opzione

Tempo di compilazione pre-trade in piedi sul mobile: 1-2 min. Post-trade end-of-day
su desktop: 3-5 min. Totale 4-7 min per trade — in target.

---

## Step 9 — Connessione futura con Claude (rimandata)

Quando l'utente vorrà fare analisi quantitativa diretta:

1. In Notion: `Settings & members` → `Connections` → cerca `Claude` → connetti.
2. Da quel momento Claude (in conversazioni con MCP Notion attivo) può leggere il
   database direttamente e calcolare statistiche, segnalare pattern, ecc.
3. Permessi minimi: read-only sul database `Trading Journal`. Non serve write.

Pianificato dopo 1-2 mesi di dati compilati.

---

## Manutenzione

- Se aggiungi un nuovo `Simbolo`, `Account` o `Strategia/Setup`, fallo direttamente
  da Notion al volo: appare nel Select alla prima compilazione.
- Se aggiungi un nuovo marker di `Confluenze`, **aggiungilo anche in
  [`levels.yaml`](../strategies/confluence_levels/levels.yaml) sezione VOCABOLARIO**
  per coerenza tra setup planning e trade record.
- Se modifichi lo schema (rinomini, togli, aggiungi proprietà), aggiorna
  [`NOTION_JOURNAL_SCHEMA.md`](NOTION_JOURNAL_SCHEMA.md).
