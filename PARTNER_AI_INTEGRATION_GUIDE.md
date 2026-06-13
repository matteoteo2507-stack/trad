# Guida per l'AI del socio — Level Analyzer & analisi del bot VELTRIX

> ## ⚠️⚠️ WARNING OBBLIGATORIO — LEGGERE PRIMA DI TOCCARE IL CODICE DEL BOT ⚠️⚠️
>
> **PRIMA di copiare, integrare o modificare QUALSIASI cosa nel repo del bot VELTRIX
> (`alphaflowgpt-crypto/trading-bot`), DEVI:**
> 1. produrre al socio (proprietario del bot) un **RIEPILOGO COMPLETO** di: cosa è stato
>    scoperto/aggiunto in questo repo, **come funziona ogni componente**, e cosa proponi di
>    integrare e perché;
> 2. ottenere la sua **APPROVAZIONE ESPLICITA**.
>
> **NON copiare/mergiare codice alla cieca.** Questo NON è una patch pronta: è una
> *valutazione del bot* + uno *strumento nuovo validato*. Integrazioni sbagliate o frettolose
> possono peggiorare il bot o introdurre bug. Procedi solo dopo il riepilogo e l'OK.

---

## 0. TL;DR
- È stato valutato il bot VELTRIX e costruito un **Level Analyzer** (analizzatore di livelli)
  con edge **validato e cost-survived** su XAUUSD e BTCUSD.
- **Scoperta chiave:** la *predizione direzionale* (bias di sessione/daily) del bot **non ha
  edge** (~50% out-of-sample, 3 verifiche indipendenti). Il valore reale è nei **livelli**:
  il fade su **zone di confluenza a esattamente 2 nature (`conf=2`)** ha edge significativo.
- Tutto è in **Python** (il bot è in JS): vedi §4 per le opzioni di integrazione.

## 1. ⚠️ Sicurezza urgente (indipendente dall'integrazione)
- **Chiave API Bybit + secret esposti nella git history del bot** (commit `f3f875b`, file
  `test_api.py`, poi cancellato ma **recuperabile**). → **Revocare/rigenerare la chiave su
  Bybit subito**, poi ripulire la history (`git filter-repo`/BFG + force-push).
- Dipendenze inutili che trascinano CVE: `node-telegram-bot-api` e `node-fetch` sono
  **dichiarate ma non usate** → rimuoverle + `npm audit fix`.
- **Cron daily registrato due volte** (`index.js` + `market-alert.js:152`) → **doppi post**.

## 2. Cosa è stato scoperto (perché conta)
- **Direzione = niente edge.** Bot as-is ~53% (gonfiato da look-ahead), logica pulita OOS ~50%,
  macro DXY+yields ~50%. L'80-90% non è raggiungibile da price-action/MTF. **Non costruire
  strategie sulla % direzionale.**
- **Look-ahead nel bot:** il bias gira sulla **candela ancora in formazione**
  (`marketBias.js:191`, manca `slice(0,-1)`) e su spot live (`:171`). I "4H" sono blocchi non
  allineati ai veri boundary UTC. L'oro usa `GC=F` **futures**, non XAUUSD spot → livelli
  PDH/PDL sbagliati di $11-25 vs spot.
- **Edge reale = livelli `conf=2`.** Validato su 13y XAU + 6y BTC, **al netto dei costi reali**:
  XAU ~+0.15÷+0.19 R/trade, BTC ~+0.09 R (recente +0.17 R). EUR escluso (edge mangiato dallo spread).
  Sorpresa: **più confluenza NON aiuta** — `conf=3+` (congestione) è negativo. Sweet spot = **2 nature**.

## 3. Cosa c'è in questo repo da integrare

| Componente | Path | Cosa fa |
|---|---|---|
| **Level Analyzer (Fase A)** | `level_analyzer/` | Genera zone `conf=2` con lato/SL/TP/RR e (opz.) notifica Telegram. **Non piazza ordini.** |
| **Port logica livelli** | `analysis/veltrix/levels_engine.py` | Port fedele in Python di `marketBias.js` (analyze_bias, get_key_levels, OB, FVG) + `cluster_confluence`. |
| **Spec + report validazione** | `analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md` | La spec operativa e tutti i numeri di validazione. **Leggi prima questo.** |
| **Harness di validazione** | `analysis/trading-bot-eval/*.py` | Riproducono ogni risultato (expectancy, CI, costi, cross-asset). |

### Come funziona il Level Analyzer (`level_analyzer/`)
- `detector.py` — pura: da OHLC (daily prec. + finestra H1) costruisce le nature (PDH/PDL,
  swing S/R, OB, FVG), le clusterizza in zone, tiene **solo `confluence == 2`**, ed emette
  `{side, zone, entry, SL=0.5·ATR(H1), TP=RR·SL, RR}`.
- `feed.py` — dati: offline (CSV) o live (MT5 spot).
- `notify.py` — messaggio Telegram (token da `.env`, opzionale).
- `__main__.py` — CLI: `preview` (offline), `scan [--notify]` (live), `run` (loop).
- Output operativo: notifica + `signals_log.csv` (log forward, gitignored).

## 4. Come integrare nel bot (opzioni) + cosa NON fare

**Il bot è Node.js, l'analyzer è Python.** Due strade:
1. **Servizio Python affiancato** (consigliato, basso rischio): far girare `level_analyzer`
   come processo separato che pubblica le zone `conf=2` (file/endpoint) che il bot legge.
   Non si tocca la logica del bot.
2. **Port in JS:** riscrivere la pipeline `conf=2` (detector → cluster → filtro 2 nature →
   fade/SL/TP) dentro il bot. Più lavoro, da testare contro l'harness Python come oracolo.

**NON fare:**
- ❌ Non prendere il **bias direzionale** del bot come predittore (no edge dimostrato).
- ❌ Non usare i livelli su **`GC=F` futures**: servono dati **spot** (broker).
- ❌ Non filtrare per "alta confluenza" (`conf=3+`): è negativo. **Solo `conf=2`.**
- ❌ Non promettere/aspettarsi 80-90%: il target realistico è **expectancy positiva**
  (~+0.10÷+0.20 R/trade netto), non un win-rate alto.

**DA correggere nel bot (dall'audit):** togliere la candela viva (`slice(0,-1)`), 4H allineato
ai veri boundary UTC, dedup del cron daily, rimuovere `node-fetch`/`node-telegram-bot-api`.

## 5. Spec sintetica (versione validata)
`Asset: XAUUSD + BTCUSD (EUR escluso) · zone conf=2 (escludi conf=1 e conf=3+) ·
fade (long supporto / short resistenza) · SL = 0.5·ATR(H1) · RR primario 1:1.5 (XAU regge 1:2).`
Fase operativa attuale = **A: notifica → l'umano piazza a mano**. Semi/full-auto solo DOPO aver
validato i guardrail (regime, filtri news/spread/SL, risk dinamico) sui trade reali.

## 6. Riproducibilità / dati
- I CSV OHLC **non sono in git** (rigenerabili). Per averli:
  - `python analysis/trading-bot-eval/export_mt5_spot.py` (spot da MT5, serve terminale connesso),
  - `python analysis/trading-bot-eval/fetch_ohlc.py` (fallback Yahoo).
- Validare/riprodurre i numeri: gli script in `analysis/trading-bot-eval/` (es.
  `expectancy_confluence.py XAU`, con `COST_PRICE=0.20` per il netto).
- Provare l'analyzer: `python -m level_analyzer preview`.

## 7. In una riga
Integra **i livelli `conf=2` su dati spot** (XAU/BTC) come fonte di setup con SL/TP/RR; **ignora**
la parte direzionale; **correggi** look-ahead/4H/data-source nel bot — **ma solo dopo aver fatto
il riepilogo al socio e averne avuto l'OK.**
