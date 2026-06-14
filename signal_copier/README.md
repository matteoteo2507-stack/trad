# Signal Copier — copia segnali Telegram → MT5

Copia i segnali dei canali Telegram dei mentori e li esegue su MT5. Fase 1:
account **demo personale**, **full-auto** (caso d'uso chiave: segnali notturni
USA non copiabili a mano). La scelta della prop firm è rimandata.

## Pipeline

```
Telegram (Telethon) ─► parser per-canale ─► planner (sizing + gate) ─► executor (dry-run | MT5)
```

- **reader.py** — `TelegramReader` (Telethon, account utente) per il live;
  `iter_offline_messages` per il dry-run su file di esempi.
- **parsers/** — un parser deterministico per canale. Registry in `parsers/base.py`.
  Niente LLM nel percorso che apre ordini: una regex sbagliata si trova in test,
  un'allucinazione no.
- **planner.py** — gate copia-segnali (whitelist, coerenza SL/TP, anti-ritardo) +
  sizing: rischio totale del segnale splittato su N gambe (una per TP).
- **executor.py** — apre le gambe e applica gli update (TP1→break-even, close→flatten).

## Flusso del canale (entrata sul "NOW")

Il canale manda i messaggi in sequenza:
1. 🎫 sticker "get ready" → ignorato;
2. **"XAUUSD SELL/BUY NOW"** → il mentore entra a mercato: **apriamo a mercato qui**
   (trigger). SL = entry ± `entry.sl_distance`, TP provvisori da `entry.tp_offsets`;
3. messaggio con **entry/SL/TP** (~1 min dopo) → **riconciliazione**: sovrascriviamo
   gli SL/TP esatti sulle gambe già aperte (non riapre nulla);
4. **TP / Close** → gestione.

Perché sul "NOW" e non sul messaggio coi livelli: quest'ultimo arriva ~1 min dopo,
quando il prezzo si è già mosso (in live il 2026-06-02 abbiamo perso 2 segnali per
~30 pip di scarto, poi andati a TP). Entrando sul "NOW" copiamo il **timing** del
mentore senza rincorrere. Policy v1: **un trade per canale** (un secondo "NOW"
mentre uno è attivo viene ignorato). Parametri in [config.yaml](config.yaml) → `copier.entry`.

## Strategia di gestione (canale XAU/USD ANALYSIS TEAM)

Il segnale ha 3 TP. Apriamo **3 posizioni** (una per TP), stesso SL, ognuna ⅓ del
rischio. **TP e SL sono armati sul broker all'apertura**: così gli update Telegram
mancanti (il canale spesso omette il TP2) non rompono la gestione. Gli unici update
che usiamo davvero:
- `TP1 SUCCESSFUL` → sposta SL a break-even sulle gambe residue;
- `Close your trades` → chiude ciò che resta a mercato.

⚠️ **Richiede un account MT5 di tipo HEDGING.** Su account *netting* (default di
molti demo MetaQuotes) le 3 posizioni stesso-simbolo si nettano in una sola e i TP
indipendenti saltano. Crea il demo come hedging.

## Uso

```bash
# Dry-run sui messaggi di esempio (nessuna credenziale, nessun ordine):
python -m signal_copier dryrun --channel xauusd_analysislab \
    --samples signal_copier/samples/xau_analysis_lab.txt

# Live — ascolta soltanto e logga (utile per osservare il parsing dal vivo):
python -m signal_copier live --mode dry_run

# Live — apre ordini su MT5:
python -m signal_copier live --mode live
```

## Configurazione

- **`config.yaml`** — parametri non sensibili: canali, rischio, anti-ritardo, gestione.
- **`.env`** — segreti: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`,
  e le credenziali `MT5_DEMO1_*`. Vedi `.env.example`. Mai committare `.env`.

api_id/api_hash si ottengono da <https://my.telegram.org> → *API development tools*.

## Aggiungere un canale

1. Scrivi `parsers/<canale>.py` con una sottoclasse di `ChannelParser` che
   restituisce `ParsedSignal` / `SignalUpdate` / `None`, e chiama `register_parser`.
2. Importalo in `parsers/__init__.py`.
3. Aggiungi 5-10 messaggi reali in `samples/<canale>.txt` e un test in
   `tests/test_signal_copier.py`.
4. Mappa il canale in `config.yaml` (`channels:`).

## Stato

- ✅ **Fase 0** — scaffold + parser XAU + planner + dry-run + test (16 test verdi).
- ✅ **Fase 2 (codice)** — esecuzione MT5 multi-gamba con **gestione per-ticket**:
  `MT5Broker.get_positions / modify_position_by_ticket / close_position_by_ticket`,
  ticket catturato per gamba in `TradeLeg.ticket`, BE→break-even e flatten sulla
  singola gamba (una gamba col TP già scattato viene ignorata senza errore).
- ⏳ **Fase 1 (operativa)** — `.env` + `signal_copier.session` presenti: serve
  ascolto live in **dry-run** sul canale reale per validare il parser sui messaggi veri.
- ⏳ **Go-live** — creare/verificare il demo **hedging** e passare a `--mode live`.

## Percorso al live (checklist operativa)

1. **Demo HEDGING** — verifica che `MT5_DEMO1` in `.env` sia un conto **hedging**
   (non netting). In MT5: *Strumenti → tipo conto*; se netting, apri un nuovo demo
   MetaQuotes di tipo hedging e aggiorna `.env`.
2. **Dry-run live (≥ 3-5 giorni)** — `python -m signal_copier live --mode dry_run`.
   Osserva nel log che **ogni** messaggio del canale sia parsato correttamente
   (segnali, `TP1 SUCCESSFUL`, `Close your trades`). Annota i falsi negativi/positivi.
3. **Smoke test esecuzione** — con 1 segnale reale a basso rischio, `--mode live`,
   verifica: 3 gambe aperte (3 ticket distinti), SL/TP armati sul broker, BE su TP1,
   flatten su `Close`.
4. **Live full-auto** — `python -m signal_copier live --mode live` in background
   (tmux/servizio). Da qui parte la raccolta dati del mese.

## Red lines (sicurezza esecuzione automatica)

Regole non negoziabili per qualsiasi automazione che può piazzare ordini. Adattate dal pattern
di safety di un AI-trading platform (review GitHub QuantDinger), tarate sul nostro caso.

1. **Default = `dry_run`.** Nessun percorso apre ordini per default: `live` va passato esplicitamente
   ogni avvio (già imposto in [`executor.py`](executor.py), `mode ∈ {dry_run, live}`). Non aggiungere
   default che eseguano ordini.
2. **Capitale reale = decisione separata, mai implicita.** Oggi: **demo-only**. Il passaggio da demo a
   conto reale (e da segnali a prop) è una decisione esplicita e scoped — non una conseguenza automatica
   del "funziona in demo". Tenere un secondo gate (account demo vs reale verificato in `.env`) oltre al
   flag `--mode live` prima di rischiare capitale.
3. **Segreti mai nel repo.** `.env`, `*.session`, chiavi broker/Telegram restano **gitignored** (verificato
   2026-06-14: non tracciati). Precedente da non ripetere: chiave Bybit finita nella git history di VELTRIX.
   Mai loggare token/chiavi in chiaro.
4. **Audit di ogni evento, incluso il rifiuto.** Il journal append-only registra sia `signal_accepted` sia
   `signal_rejected` (col motivo) — mantenere questa simmetria: serve a tarare i gate e a ricostruire cosa
   è successo. Vedi [`journal.py`](journal.py).
5. **Niente bypass della review umana verso il reale.** Compliance copy-trading lato prop (alcune vietano la
   copia di segnali terzi): la piena automazione resta confinata alla demo finché la milestone-1 non è chiusa.

## Dati raccolti (auto-trade-log — niente Notion)

Il copier scrive **da solo** un journal append-only (`logs/signal_copier_journal.jsonl`,
configurabile via `journal_file`), una riga JSON per evento. Niente attrito manuale: i
dati arrivano dai **segnali stessi** + dal **risk management** applicato. Vedi
[`journal.py`](journal.py).

Eventi registrati:
- `signal_accepted` — segnale + gambe pianificate (entry/SL/TP, lotti) e **R/R pianificato
  per gamba** (reward al suo TP / rischio allo SL); in live anche i `ticket`.
- `signal_rejected` — segnale scartato dal planner + motivo (utile per tarare i gate).
- `levels_reconciled` / `levels_no_trade` — arrivo del messaggio coi livelli esatti (riconciliati sulle gambe, o ignorati se nessun trigger attivo).
- `update_tp_hit` / `update_all_tp` / `update_close_all` — eventi di gestione coi ticket.

Il dry-run su esempi offline scrive su `*_journal_dryrun.jsonl` (dati di test, separati).

Questo dataset basta per **ottimizzare il risk management** e alimentare `/quant-review`
(con ≥ 30-50 segnali). **Manca solo il PnL realizzato per gamba** (prezzi di fill): è una
riconciliazione opzionale dallo storico MT5 per `ticket`, da aggiungere se/quando servirà
la misura esatta in valuta. Vedi [DECISIONS.md](../DECISIONS.md) e [PROJECT.md](../PROJECT.md).
