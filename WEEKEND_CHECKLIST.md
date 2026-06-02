# Weekend Checklist

> **Aggiornamento 2026-05-24** (post settimana 2): Confluence è ora una strategia
> **opportunistica**. Questa procedura va eseguita **solo quando decidi di tradare
> Confluence la settimana entrante**. Se la settimana non è tradabile (impegni, mancanza
> di setup chiari, regime Sideways Volatile), salta la checklist senza colpa — TSMOM e
> London Breakout girano comunque in automatico e raccolgono dati per il Quant Reviewer
> (Stage 2.6 della [ROADMAP](ROADMAP.md)).

Procedura operativa da eseguire **quando si decide di tradare Confluence la settimana
entrante**, prima dell'apertura dei mercati (Asia lunedì 00:00 Roma). Ordine cronologico —
esegui dall'alto verso il basso. Ogni passo è atomico: niente "lo faccio dopo".

Riferimento concettuale: [`TRADING_PRINCIPLES.md`](TRADING_PRINCIPLES.md). Se in dubbio su una scelta,
torna a quel file — non interpretare al volo.

Tempo stimato totale: **2–3 ore** ben fatte. Non sotto le 90 minuti.

---

## Fase 0 — Setup ambiente (5 minuti)

1. Apri TradingView in browser (account loggato).
2. Apri MT5 sul PC (non per tradare, solo per consultare il calendario news interno se serve).
3. Apri questo file (`WEEKEND_CHECKLIST.md`) e tienilo affiancato al chart.
4. Apri un blocco note vuoto chiamato `journal_settimana_<YYYY-MM-DD>.md` nella cartella
   `journals/` del progetto (se non esiste la cartella, creala). Servirà per annotare tutto.

---

## Fase 1 — Diagnosi del regime di mercato (30 secondi)

> **Cambio 2026-05-25**: la regola empirica HH/HL ("conta le candele direzionali")
> è stata rimossa perché generava dati sporchi. La diagnosi è ora **completamente
> automatizzata** via Wilder DMI/ADX/ATR. Logica in
> [`core/regime.py`](core/regime.py); dettagli in [`TRADING_PRINCIPLES.md §1`](TRADING_PRINCIPLES.md).

1. Da terminale nella root del progetto, esegui:

   ```bash
   python -m core.regime --symbols EURUSD=X,XAUUSD=X --journal
   ```

   Output esempio:

   ```
   ## Regime corrente 2026-05-25
   - EURUSD: Bull Quiet  | ATR=0.00521 (SMA50=0.00614)  ADX=27.4  +DI=24.1 -DI=15.2  → proceed
   - XAUUSD: Sideways Volatile | ATR=42.10 (SMA50=31.05)  ADX=18.7  +DI=19.0 -DI=18.4  → stay_out
   ```

2. Copia il blocco markdown nel journal `journal_settimana_<YYYY-MM-DD>.md`.

3. **Decisione operativa immediata** (codificata in `core/regime.py`, coerente
   con [`TRADING_PRINCIPLES.md §1`](TRADING_PRINCIPLES.md)):
   - Action `stay_out` (Sideways Volatile) → niente trade direzionali questa settimana
     o size dimezzata se proprio devi.
   - Action `proceed` → procedi.

4. (Opzionale) Per usare un CSV custom invece di yfinance (es. export MT5):

   ```bash
   python -m core.regime --csv data/eurusd_d1.csv --label EURUSD --journal
   ```

5. (Opzionale) Apri TradingView per **verifica visiva** di coerenza — non per
   sovrascrivere la diagnosi automatica. Se vedi una macro-divergenza fra
   quello che leggi e l'output del comando, **annotala nel journal come
   "anomalia da indagare"** e portala al `/quant-review`. Non auto-correggere
   il regime.

---

## Fase 2 — Analisi top-down dei livelli (60–90 minuti, il grosso del lavoro)

Da fare **per ogni simbolo**, in questo ordine di timeframe (alto → basso).

### 2.1 — Monthly (5 minuti)

1. Chart Monthly del simbolo.
2. Identifica i livelli S/R orizzontali storici visibili: massimi e minimi importanti, livelli psicologici
   (es. 1.20 su EURUSD, 5000 su XAU). Disegna max 5 linee orizzontali.
3. Annotale nel journal con prezzo e tipo:
   ```
   ## Monthly EURUSD
   - 1.20000 — resistance psicologica (testata 3 volte nel 2024-2025)
   - 1.08500 — supporto storico
   ```

### 2.2 — Weekly (15 minuti)

1. Chart Weekly.
2. Identifica:
   - Supporti/resistenze orizzontali delle ultime 26 settimane (~6 mesi).
   - Zone di supply/demand (rettangoli, non linee): dove c'è stato un rapido movimento dopo un periodo
     di consolidamento, quel consolidamento È la zona.
   - Direzione del trend Weekly (HH+HL, LH+LL, sideways).
3. Per ogni zona S/D identificata, **conta quante volte è stata testata dopo la creazione**:
   - 0 test → `fresh` (massima priorità)
   - 1 test → `tested_1`
   - 2–3 test → `tested_2plus` (uso solo con conferma forte)
   - 4+ test → `esaurita` (non la uso come entry, eventualmente come target di breakout)
4. Annota tutto nel journal sotto `## Weekly <simbolo>`.

### 2.3 — Daily (20 minuti)

1. Chart Daily.
2. Identifica livelli S/R **interni alla settimana entrante** (entro ±3% dal prezzo corrente).
3. Per ognuno, conta i touch storici (vedi §2 di `TRADING_PRINCIPLES.md`):
   - 1–2 touch con rejection netta → forte
   - 3 touch → a rischio rottura
   - 4+ touch → esaurito
4. Identifica zone S/D Daily fresh.
5. Annota tutto nel journal sotto `## Daily <simbolo>`.

### 2.4 — H4 (15 minuti) e H1 (5 minuti)

1. Chart H4 → ripeti §2.3 per livelli H4 (timeframe operativo principale per Confluence).
2. Chart H1 → solo se serve raffinare un livello H4 (es. per identificare il punto esatto di un'area
   S/D ampia).
3. Annota nel journal sotto `## H4 <simbolo>` e `## H1 <simbolo>` (se usato).

---

## Fase 3 — Tracciamento Fibonacci (15 minuti per simbolo)

1. Sul Daily, identifica l'ultimo **swing direzionale chiaro** (da swing low a swing high se in uptrend,
   viceversa in downtrend).
2. Traccia lo strumento Fibonacci retracement da swing low → swing high (uptrend) o swing high →
   swing low (downtrend).
3. Annota nel journal i livelli `0.236`, `0.382`, `0.5`, `0.618`, `0.786` con il prezzo corrispondente.
4. **Cerca confluenza**: ogni livello Fib che coincide entro **±10 pip (forex)** o **±50 pip (XAU)** con
   un livello S/R o S/D già identificato → è confluenza forte, segnalo nel journal con un `[CONFLUENZA]`.

---

## Fase 4 — [BOZZA] Analisi POC / Volume Profile (15 minuti per simbolo)

> Sezione **bozza**: usala manualmente per qualche settimana, poi formalizziamo. Non aggiungere ancora
> marker POC in `levels.yaml` se non sei sicuro — meglio averli nel journal come nota.

1. Chart Daily del simbolo.
2. Aggiungi indicatore TradingView: **"Volume Profile Fixed Range"** (gratuito anche su piano free).
3. Imposta il range temporale:
   - **POC mensile**: ultimi 30 giorni di calendario.
   - **POC settimanale**: ultima settimana di trading (lunedì → venerdì precedente).
4. Annota nel journal:
   ```
   ## POC <simbolo>
   - POC monthly: <prezzo>
   - POC weekly: <prezzo>
   - VAH monthly: <prezzo>  (Value Area High)
   - VAL monthly: <prezzo>  (Value Area Low)
   ```
5. **Cerca confluenza POC con i livelli identificati nelle fasi 2–3**:
   - Se un tuo livello S/R o S/D coincide entro ±10 pip (forex) o ±50 pip (XAU) con un POC → annotalo
     come `[POC_aligned]` nel journal.
   - Questi livelli hanno **alta priorità** nella settimana.
6. **Per XAUUSD**: ripeti l'analisi Volume Profile su `GC1!` (gold futures CME, volume reale), perché
   il tick volume di XAUUSD spot è solo un proxy. Confronta i due POC: se coincidono entro $5, il
   livello è confermato. Se divergono di più, fida del POC su `GC1!`.

---

## Fase 5 — Identificazione setup operativi (20 minuti)

Per ogni livello identificato nelle fasi precedenti, decidi se è un **setup tradabile** applicando
i 3 criteri di `TRADING_PRINCIPLES.md` §5:

1. **Livello valido**: type definito + confluenza ≥ 2 elementi di natura diversa.
2. **Bias coerente col regime** (fase 1).
3. **RR ≥ 1:3 al primo target strutturale**.

Per ogni setup che supera tutti e 3 i criteri:

1. Definisci entry price (= prezzo del livello).
2. Definisci SL price (livello ± buffer; per EURUSD 5–10 pip, per XAU $3–5).
3. Definisci TP price = **primo livello strutturale** raggiungibile in giornata, nella direzione del bias.
4. Calcola RR:
   ```
   RR = |TP - entry| / |entry - SL|
   ```
   Se RR < 3 → setup **incerto** (size dimezzata o skip).
5. Annota tutto nel journal sotto `## Setup <simbolo>`:
   ```
   - id: EURUSD-2026W21-S1
     entry: 1.16500
     sl: 1.16400
     tp: 1.17000
     RR: 5.0
     classification: VALIDO
     confluence: SR_D1, Fib_618, POC_weekly
     freshness: fresh
   ```

---

## Fase 6 — Compilazione `levels.yaml` (20 minuti)

1. Apri il file [`strategies/confluence_levels/levels.yaml`](strategies/confluence_levels/levels.yaml).
2. **Cancella i livelli scaduti** (`valid_until` < oggi) o mantienili commentati se vuoi storico.
3. Per ogni setup valido identificato nella fase 5, aggiungi una voce. Sintassi esatta (vedi anche
   la legenda in cima al file):
   ```yaml
   - id: "EURUSD-2026W21-S1"
     price: 1.16500
     type: support
     confluence: [SR_D1, Fib_618, POC_weekly]
     bias: long
     valid_until: 2026-05-24       # domenica successiva
     tp_target_price: 1.17000
     # sl_buffer_pips: 7           # opzionale, override del default
   ```
4. Regole di compilazione (da `TRADING_PRINCIPLES.md` e legenda `levels.yaml`):
   - `id` univoco, formato `<SYM>-<YYYY>W<NN>-<TIPO><N>`.
   - `price` in formato decimale (5 decimali per forex, 2 per XAU, **niente virgolette**).
   - `type` ∈ {`support`, `resistance`, `demand_zone`, `supply_zone`, `fib_retracement`,
     `fib_extension`, `vwap`, `key_level`}.
   - `confluence` lista con ≥ 2 elementi di natura diversa.
   - `bias` ∈ {`long`, `short`}.
   - `valid_until` data YYYY-MM-DD = domenica successiva (o oltre per livelli D1+).
   - `tp_target_price` OBBLIGATORIO (il runner SCARTA il livello senza TP).
   - `sl_buffer_pips` opzionale (override per livello del default in `config.yaml`).
   - Per `demand_zone` / `supply_zone`: `price` = bordo **prossimale** (alto per
     demand, basso per supply). Annota il bordo distale in un commento `##` sulla
     riga sopra la voce — non viene letto dal runner, serve a te per ricordartelo
     in editing. Vedi legenda di [`levels.yaml`](strategies/confluence_levels/levels.yaml).

---

## Fase 7 — Validazione locale (2 minuti)

1. Apri terminale nella cartella del progetto.
2. Esegui:
   ```bash
   python -m strategies.confluence_levels validate-levels
   ```
3. **Output atteso**: tabella con tutti i livelli validi. Errori bloccanti → torna a Fase 6 e correggi.
   Warning su confluenza < 2 elementi → valuta se aggiungere un altro marker, oppure accetta il warning
   se sei sicuro.

---

## Fase 8 — Sync sul VPS Hetzner (3 minuti)

1. Da PowerShell:
   ```powershell
   cd c:\Users\mmbus\Desktop\lavoro\trad
   scp strategies\confluence_levels\levels.yaml matteo@204.168.249.76:~/trad/strategies/confluence_levels/levels.yaml
   ```
2. Il runner sul VPS rilegge il file entro 60 secondi. **NO restart necessario.**
3. Verifica (opzionale, se vuoi avere conferma visiva):
   ```powershell
   ssh matteo@204.168.249.76 "sudo journalctl -u confluence -n 5 --no-pager"
   ```
   Dovresti vedere il `[heartbeat]` con i nuovi `nearest=` corrispondenti ai livelli appena caricati.

---

## Fase 9 — Calendario news (10 minuti)

1. Vai su https://www.forexfactory.com/calendar o equivalente.
2. Filtra per i **5 giorni della settimana entrante**.
3. Filtra impatto: solo **High** (rosso).
4. Annota nel journal sotto `## News settimana`:
   ```
   - lun 09:30: GBP CPI (impatto: GBP, indiretto su EUR)
   - mer 14:30: USD FOMC minutes
   - gio 14:30: USD jobless claims
   ```
5. Per ogni evento high impact USD, marca i livelli operativi più vicini all'orario news come **NO TRADE**
   nei 30 minuti prima e 30 dopo (già gestito dal filtro `news_block_minutes` nel runner Confluence, ma
   è buona pratica saperlo manualmente).

---

## Fase 10 — Quick check operativo finale (5 minuti)

Spunta mentalmente:

- [ ] Regime corrente identificato e annotato per ogni simbolo.
- [ ] Setup VALIDI (≥1:3) elencati nel journal con entry/SL/TP/confluence.
- [ ] Setup INCERTI annotati come riferimento ma non in `levels.yaml`.
- [ ] `levels.yaml` aggiornato e validato (Fase 7 senza errori bloccanti).
- [ ] `levels.yaml` sincronizzato sul VPS (Fase 8).
- [ ] News high impact della settimana annotate.
- [ ] [BOZZA] POC weekly e monthly annotati nel journal per ogni simbolo.

---

## Fase 11 — Prepara il journal della settimana entrante (5 minuti)

> **Cambio 2026-05-18**: i **Trade eseguiti** non si registrano più nel markdown
> settimanale, ma nel database Notion `Trading Journal` — accessibile da mobile,
> da compilare *quando il trade viene preso*. Schema in
> [`journals/NOTION_JOURNAL_SCHEMA.md`](journals/NOTION_JOURNAL_SCHEMA.md), guida
> di creazione in [`journals/NOTION_SETUP_GUIDE.md`](journals/NOTION_SETUP_GUIDE.md).
>
> Il markdown settimanale resta per: Trade NON eseguiti, osservazioni di mercato,
> auto-valutazione fine settimana.

Lascia aperto nel journal `journal_settimana_<YYYY-MM-DD>.md` la sezione:

```markdown
## Trade NON eseguiti (compila durante la settimana)

| # | Giorno | Simbolo | Setup ID | Motivo skip | Cosa è successo dopo |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

## Osservazioni di mercato
- Lunedì:
- Martedì:
- Mercoledì:
- Giovedì:
- Venerdì:

## Auto-valutazione fine settimana
- Trade forzati: <numero>
- Trade saltati per disciplina: <numero>
- Deviazioni dai principi (con motivo):
- Da migliorare la prossima settimana:
```

Compilare il journal **alla fine di ogni giornata di trading**, non a memoria a fine
settimana. Per i trade eseguiti, apri l'app Notion sul telefono o il database su
desktop e crea una nuova entry — vedi guida operativa nel file
[`journals/NOTION_SETUP_GUIDE.md`](journals/NOTION_SETUP_GUIDE.md) §Workflow di
compilazione.
