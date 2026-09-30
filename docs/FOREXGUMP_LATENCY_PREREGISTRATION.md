---
tipo: preregistrazione
stato: BOZZA
aggiornato: 2026-09-28
decisione: "da scrivere in DECISIONS quando Matteo approva la bozza"
metrica_corrente: "nessuna: nessun esito calcolato"
nota: "G1 #1 del 28/09 = BLOCCA (5 punti): testo corretto; restano motore, tick e MDE sulla differenza (§0bis)."
---
# Pre-registrazione — Forex Gump GOLD VIP: il segnale copiato in ritardo vale ancora?

> **Bozza scritta il 2026-09-28 PRIMA di calcolare qualunque esito.** Finora sono stati calcolati
> solo **conteggi** (segnali per periodo e per lato, geometria dichiarata), la **potenza** e il
> **fuso** (sole entrate contro prezzo). Nessun E[R], nessun win rate, nessun confronto di esiti.
> Dopo l'approvazione le soglie non si toccano; ogni modifica va datata nel §10.
>
> Ciclo: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md) · review: [QUANT_REVIEW_PROTOCOL.md](QUANT_REVIEW_PROTOCOL.md)
> (Step 3bis) · modello: il lavoro C5 sul mentore XAU, [latency_gate.py](../analysis/mentor_signals/latency_gate.py).

---

## 0. Decisioni (di Matteo, prima dell'approvazione)

| # | Decisione | Testo proposto | Stato |
|---|---|---|---|
| **D1** | Split | **L'intero campione (1.792 segnali, 09/09/2020 → 28/09/2026) e' l'holdout della famiglia. Il TRAIN e' vuoto.** Si apre **una volta**, alla data dell'esecuzione, registrata in `trial_ledger.json` (`holdout_aperto`). Su questi dati sono ammessi **0 round di rifinitura**. Qualunque variante successiva (latenza, categoria, LIMIT/SKIP, geometria, anno) si valida **solo sul forward** dopo il 28/09/2026, conta come trial e ha una sua pre-registrazione: sui 1.792 resta **descrittiva per sempre**. L'esito positivo massimo e' **LEAD** (LIFECYCLE §5: nessun OOS indipendente); **GO** solo dal forward | proposta; accettabile per il gatekeeper (G1 #1). Precedente: `trend_momentum` senza holdout. Alternativa: audit < 2025-10-01 + holdout di 12 mesi, **MDE ~0,40R** (non potrebbe confermare un edge realistico) |
| **D2** | Trimestre | Il budget esterno e' **3 per trimestre** (allarme a 2), e conta la **data di approvazione**, non quella d'esecuzione. Due strade pulite: **approvare nel Q3** (3 di 3, trimestre pieno) oppure **approvare dal 01/10** (1 del Q4) | da decidere |
| **D3** | Messaggi modificati | Se l'export contiene la versione **finale** di messaggi modificati dopo la pubblicazione, il copier ha visto un testo diverso: look-ahead d'informazione. Da verificare **prima** dell'esecuzione: il socio sa se il mentore modifica i segnali? Nell'export compaiono segni di modifica? | da verificare (Matteo/socio) |

## 0bis. Stato del lavoro (dove siamo, cosa manca)

- ✅ Parser, prezzi M1 BID/ASK, fuso (98,9%), checklist dati — §3.
- ✅ G1 #1 (quant-gatekeeper, 28/09): **BLOCCA** su 5 punti; testo corretto in questa versione.
- ⏳ **Motore** `analysis/forexgump/replay.py`: tick, BID/ASK per lato, timeout a tempo, SKIP con
  spread ≥ SL, entrambi i lati allo stesso istante, CI a cluster per giorno (§4-§5).
- ⏳ **Export dei tick** nelle finestre dei segnali (§3).
- ⏳ **MDE sulla differenza appaiata**, calcolato su **istanti casuali** degli stessi anni e delle stesse
  ore, **senza** simulare gli istanti dei segnali (§6).
- ⏳ G1 #2, poi approvazione (D1-D3) e voce nel ledger, poi esecuzione **una volta**.

## 1. Perché questo test esiste

Il socio ha collegato Forex Gump a un copier e la sua webapp ne mostra un backtest positivo
(1.969 segnali, 2020-09 → 2026-09). La prima settimana live (4 segnali, 21-28/09/2026) ha mostrato
che **la copia entra in media 0,79R peggio del prezzo postato** (fill da 1,79 a 3,07 $ su uno stop
di 3 $). Il mentore scrive *"Ho venduto a X"*: al momento del post **e' gia' dentro**.

Se la webapp riempie al prezzo postato, il suo backtest ha lo stesso difetto che ha ucciso il FADE:
un fill **non ottenibile** ([[feedback_fill_ottenibile]]). Si puo' misurare sul passato, senza
aspettare dati live: ogni messaggio ha il suo orario, e il prezzo reale di quel momento esiste.

## 2. Ipotesi e perimetro

**H1 (primaria).** Copiando i segnali come fa il copier — ordine a mercato **L = 10 s** dopo il
messaggio, bracket ricentrato sul fill — il lato scelto dal mentore rende **piu' del lato opposto**
negli stessi istanti, **e** l'E[R] ottenibile resta **> 0** dopo spread e commissioni.
Non dimostrata se il limite inferiore del CI 95% della differenza appaiata e' ≤ 0.

**Perimetro — cosa e' davvero questo test.** Non e' un edge con un razionale proprio: e' la
**verifica di un claim di terzi** (il backtest della webapp) e la **misura del costo del ritardo**.
Per questo l'esito migliore possibile e' **LEAD**, mai un GO.

**Razionale economico — debole, dichiarato.** Un discrezionale con un track record lungo potrebbe
leggere la direzione di breve dell'oro meglio del caso: chi sta dall'altra parte, qui, non e'
identificato. I messaggi dicono che la maggior parte dei segnali sono **coperture** ("hedging", 947
su 1.899) attorno a una posizione lunga **mai postata**: per lui una copertura puo' avere senso anche
con valore atteso negativo da sola; per chi copia esiste solo il bracket. E il mentore usa **livelli**
("KL importante a 4313.50"), che nei nostri 384 trial non contenevano informazione
([LEVEL_RESEARCH_PREREGISTRATION.md](LEVEL_RESEARCH_PREREGISTRATION.md)). Prior basso.

## 3. Dati

| | |
|---|---|
| **Segnali** | Export Telegram `materiale_socio/dati socio1/` (21 file, 18.688 messaggi, 09/09/2020 → 28/09/2026) → [parse.py](../analysis/forexgump/parse.py) → `signals.csv`. **1.899 bracket**; 54 messaggi con XAU e TP scartati con motivo contato (32 senza prezzo d'entrata, 11 TP e 11 SL dalla parte sbagliata: refusi che un broker rifiuta) |
| **Universo** | Bracket **con SL, a mercato: 1.792** (978 sell, 814 buy). Esclusi 104 senza SL (il copier rifiuta ordini senza SL — log del 21/09) e 3 ordini stop pendenti. **Tutte le categorie incluse** (il copier le esegue tutte). **Nessuna deduplica**, come il copier: restano i 2 bracket identici ripetuti e i segnali ravvicinati (80 entro 5 min dal precedente, 635 entro 30). Nei messaggi con piu' TP vale il **primo** (`parse.py`) |
| **Prezzi** | Dukascopy XAU/USD **M1 BID e ASK**, 2020-09-01 → 2026-09-28 ([export_prices.py](../analysis/forexgump/export_prices.py)). **Tick** nella finestra [−10 min, +60 min] di ogni segnale: **export da fare** (§0bis). Se per un segnale mancano i tick, **fallback M1** (§4) e la quota si riporta |
| **Geometria dichiarata** | SL 2 $ (1.631 casi), 3 $ (117); TP 10 $ (1.677). Rapporto TP/SL mediano **5:1** |

### 3.1 Fuso orario — fissato, una volta sola

L'export etichetta **ogni** messaggio `UTC+01:00`, d'estate e d'inverno. **Eseguito il 2026-09-28**
([fuso.py](../analysis/forexgump/fuso.py), solo entrata contro prezzo): l'orologio e' **l'ora italiana
con l'ora legale** (Europe/Rome). Entrata postata dentro il range eseguibile di una finestra che va da
5 minuti prima al minuto del messaggio compreso: **99,1%** d'inverno a UTC+1, **98,8%** d'estate a
UTC+2; ogni altro offset sotto il 23%. Controprova: messaggio del 28/09 10:48:40 = 08:48:40 UTC,
apertura del copier 08:48:46 UTC (log del socio). Conversione **solo** in
[carica.py](../analysis/forexgump/carica.py), con `verifica()` che si ferma sotto il 95% (oggi 98,9%).
Il 98,9% risponde alla domanda "il prezzo postato era vero?", **non** a "era ancora ottenibile?"
(quella e' la diagnostica dello Step 3bis, §5).

Checklist dati: monotonia e duplicati ok su 2.153.636 barre per lato, ~354.000 barre/anno;
nessun segnale con la prima barra M1 oltre 10 min dal messaggio.

## 4. Esecuzione simulata (condizione di fill — G1.9)

| | Primaria | Motivo |
|---|---|---|
| **Istante azionabile** | messaggio + **L = 10 s** | Latenze osservate: 4, 6 s sul conto FTMO del socio (log in UTC) e 14, 5, 7, 4 s sui trade MT5 (server a UTC+5, ricavato confrontando i due log). 10 s sta fra la mediana e il massimo |
| **Fill** | primo tick **≥ t + L**: buy all'**ASK**, sell al **BID**. Fallback senza tick: apertura della prima barra M1 che inizia ≥ t + L, stesso lato | Spread reale, non un costo fisso |
| **Ordine non eseguibile** | se allo fill lo spread ≥ distanza SL (lo SL ricentrato cadrebbe oltre il prezzo d'uscita) → **SKIP**: il broker lo rifiuterebbe (invalid stops). Quota riportata sempre | 134 segnali (7,5%) cadono la domenica fra le 22 e le 23 UTC, alla riapertura, quando lo spread si allarga |
| **Bracket** | **ricentrato sul fill**: SL e TP alle distanze postate dal prezzo di fill. **Bracket puro**: niente BE, niente gambe multiple, i messaggi di gestione del mentore ("BE", "scarico") ignorati | E' cio' che fa il copier del socio **su Gump**: il 28/09 il bracket "come postato" chiude sullo SL originale (4147,89 = fill − 3 $) anche se il mentore aveva scritto "BE" alle 10:52. Le tre configurazioni live (come-postato, 8-8, 10-7) sono bracket paralleli, non gambe; la primaria e' **come-postato** |
| **Serie d'uscita** | buy → **BID** (high/low/close BID); sell → **ASK**. Alla primitiva si passano le serie del lato giusto | `core.resolve_trade` non conosce BID/ASK |
| **Uscita** | **tick** per i primi 60 min (niente pareggi); poi M1 con pareggio **pessimistico** (SL prima del TP) | L'ottimistico si riporta accanto: la distanza fra i due e' la misura dell'ignoranza ([[feedback_convenzioni_implicite]]) |
| **Timeout** | **24 h di calendario** dal fill, troncando le serie a t_fill + 24 h; chiusura a mercato marcata. Un trade del venerdi' attraversa il weekend e puo' chiudere sul gap del lunedi' | `max_hold` della primitiva conta barre: serve il taglio a tempo |
| **Primitiva** | `core.resolve_trade`, `FillConvention(fill_bar_can_resolve=True, tie="pess", gap_beyond_stop=True, on_timeout="mark")` | Una sola primitiva |
| **R** | (uscita − fill) / distanza SL postata, meno costi | Il copier dimensiona sulla distanza SL |

**Costi — base.** Spread dai dati BID/ASK + commissione **0,07 $/oncia** andata e ritorno.
**Swap**: non modellato nella base; si riporta la quota di trade che attraversano il rollover delle
22 UTC. **Stress**: spread **×1,5**, commissione **×3**, **0,10 $** di slittamento extra per lato,
swap **0,10 $/oncia per rollover** attraversato.

**Posizioni sovrapposte.** Ogni segnale e' un trade indipendente, anche se ne arriva un altro mentre
e' aperto. Il nostro `signal_copier` invece fa "uno per simbolo, flip sull'opposto": se un giorno si
usasse il nostro, **l'insieme dei trade cambierebbe** e il test andrebbe rifatto.

## 5. Baseline e metriche

- **Baseline appaiato**: a ogni istante si simulano **entrambi** i lati con la stessa esecuzione.
  Differenza appaiata d = R(lato del mentore) − media dei due lati = (R_mentore − R_opposto) / 2.
  ⚠️ **Non toglie il drift**: con 978 sell e 814 buy, il drift dell'oro entra pesato per lo
  sbilanciamento (a oro in rialzo, contro il mentore). Per questo si riportano sempre:
  - la **divisione per lato** (buy e sell separati);
  - un **controllo secondario, stesso lato a istante casuale**: `core.random_baseline.BarSampler`
    stratificato per anno, **3 controlli** per segnale, stesso simulatore. Separa il *quando* dal
    *da che parte*;
  - la **durata d'holding** dei bracci, con `check_matching(observed=("hold",))`: l'holding e' un
    esito, si verifica e si dichiara.
- **Primaria**: d e E[R] ottenibile, convenzione pessimistica, L = 10 s.
- **CI a cluster per giorno**: giorno = giornata di trading con rollover alle **22:00 UTC**, assegnata
  dall'istante di **fill**; un trade a cavallo resta nel giorno del fill. Bootstrap **percentile 95%**
  sugli indici dei giorni, **10.000** ricampionamenti, metrica = somma di R / numero di trade del
  ricampione. (La libreria non lo ha: `bca_bootstrap_ci` e' i.i.d., `gap_ci` fa il cluster per
  evento. Si implementa nel motore e si dichiara come debito.)
- **Diagnostica Step 3bis, riportata SEMPRE**: quota di segnali in cui il prezzo postato era **gia'
  superato in senso sfavorevole all'istante azionabile** — `ASK(t+L) > entrata` per un buy,
  `BID(t+L) < entrata` per un sell. Il braccio primario, a mercato, e' ottenibile per costruzione
  (dopo lo SKIP). Si riporta anche l'**E[R] al prezzo postato**, etichettato **NON OTTENIBILE**: serve
  solo a misurare **il costo del ritardo** (differenza col primario) e **non si cita mai come risultato**.

**Descrittive, dichiarate ora, senza verdetto** (0 trial finche' nessuna viene scelta):
- curva della latenza: 0 / 5 / 10 / 30 / 60 / 300 s;
- **LIVE**: livelli postati assoluti, `r_unit` = |fill − SL| (il rischio vero), salto se il fill e'
  gia' oltre lo SL;
- **LIMIT** al prezzo postato con attesa di **15 min** (buy riempito se l'ASK scende a ≤ entrata,
  bracket ai livelli postati; altrimenti nessun trade);
- **SKIP** se lo scostamento sfavorevole a t + L supera **1,0 $** (meta' dello SL tipico), a mercato
  per gli altri;
- per categoria, per anno, per lato;
- sotto-finestra **06/2026 → 09/2026**, successiva al cutoff del modello (non contaminabile);
- **spiegazione noiosa**: lato = segno del movimento nei **15 minuti** prima del messaggio, stessa
  esecuzione. Se riproduce d, il mentore non aggiunge informazione a un momentum banale;
- variante a **meta' spread** (ottimistica).

⚠️ **Scegliere dopo una di queste perche' "funziona" e' un trial nuovo**, validabile solo sul forward
([[feedback_mass_search_vs_preregistration]]).

## 6. Verdetti, potenza e kill — fissati ORA

LB_d = limite inferiore del CI 95% di d. E, E_s = E[R] puntuale base e sotto stress.
**La tabella copre tutti i casi**; a fianco di ogni verdetto si riportano CI ed MDE sia di d sia di E.

| Caso | Condizione | Verdetto | Decisione |
|---|---|---|---|
| 1 | LB_d > 0 **e** E > 0 **e** E_s > 0 | **LEAD** | Forward pre-registrato (demo). Nessun capitale |
| 2 | LB_d > 0 **e** E > 0 **e** E_s ≤ 0 | **LEAD FRAGILE** | Il margine sta dentro l'incertezza dei costi: forward solo dopo aver misurato lo **spread reale del broker** dai fill live. Nessun capitale |
| 3 | LB_d > 0 **e** E ≤ 0 | **DEGRADATO** | Direzione reale, **non copiabile** con questo ritardo e questo spread. Non si opera. Un'esecuzione diversa (es. LIMIT) si pre-registra e si valida **solo sul forward** |
| 4 | LB_d ≤ 0 | **NON DIMOSTRATO (MDE …)** | Nessuna informazione direzionale **rilevabile**: la fonte non entra in pipeline. Si scrive accanto l'MDE, **non** "refutato" ([[feedback_verdetto_con_la_forza_del_test]]) |

⚠️ **Calibrazione.** "E > 0" come soglia puntuale si supera per rumore circa una volta su due quando
l'E[R] vero e' zero. E' accettabile **solo** perche' i casi 1-2 portano al forward, non al capitale.

**Potenza.** Da ricalcolare **sulla differenza appaiata**, non su R (la deviazione standard di d
dipende dalla correlazione fra i lati, spesso stoppati entrambi): simulazione su **istanti casuali**
degli stessi anni e delle stesse ore del giorno, senza toccare gli istanti dei segnali. Riferimento
grezzo su R (esiti quasi binari +5R/−1R, sd 2,4-2,75R, fattore 2,80): ~0,17-0,18R su 1.792.
**Il valore da scrivere qui prima dell'approvazione: MDE_d = ___ (§0bis).**

**Cosa significa un mancato rifiuto, scritto prima:** esclude solo effetti sopra l'MDE; non dimostra
che l'edge sia zero.

**Kill** (senza rifinitura): nessun offset di fuso con minimo netto (superato: §3.1); **> 10%** dei
segnali senza prezzi nella finestra; **> 10%** di SKIP per spread ≥ SL (il copier non sarebbe
praticabile cosi' com'e': si riporta e si ferma).

## 7. Trial e contabilita'

| | |
|---|---|
| Famiglia | `forexgump_signals` (nuova) |
| Trial di questo test | **1** (la primaria). Descrittive: 0 finche' non vengono scelte |
| Round di rifinitura sui 1.792 | **0** (D1) |
| `provenienza_ipotesi` | `umana_esterna` — socio, 28/09/2026 (canale Forex Gump + backtest della webapp) |
| Pre-registrazione esterna | conta nel trimestre della **data di approvazione** (D2) |
| DSR | n_trial = 1. Futilita' per trade: ~1,645/√(n−1) ≈ **0,039R** di Sharpe per trade su 1.792 (il `--futilita` del ledger annualizza a 252 anche sui trade: debito dichiarato) |
| Ledger | voce in `docs/trial_ledger.json` con le fonti **prima** dell'esecuzione; `holdout_aperto` alla data dell'esecuzione |

## 8. Bias noti, dichiarati prima

1. **Abbiamo visto il backtest della webapp** (screenshot del 28/09): win rate per anno "come
   postati" e il confronto fra tre configurazioni. Per questo la configurazione e' fissata **dal
   copier live** (come-postato), non scelta fra le tre.
2. **Cancellazioni dal canale non misurabili**: c'e' un solo export. Direzione del bias: se il
   mentore cancellava i perdenti, d e' **gonfiata verso l'alto**. Lo risolve solo il forward.
3. **Messaggi modificati** — D3, non verificato. Stessa direzione: verso l'alto.
4. **Un solo asset**, e un oro quasi sempre al rialzo (2020-2026): vedi drift in §5.
5. **Key-man risk** e contenuti marcati "didattici / just for fun".
6. **Latenza da 6 trade**: per questo si riporta la curva intera.
7. **Lo spread e' quello di Dukascopy, non del broker del socio.** Mediana per anno (close ASK − BID,
   28/09): 0,33-0,39 $ nel 2020-2024, **0,58 $ nel 2025 e 0,69 $ nel 2026** — con SL 2 $ vale
   0,17-0,35R a trade. Il verdetto si legge sullo spread Dukascopy; stress a ×1,5, meta' spread
   descrittiva. Lo spread reale del broker va misurato dai fill live, non scelto.
   **Misurato il 29/09 (solo prezzi):** in punti base lo spread **scende** da 2,04 bps (2020) a 1,51
   (2026); l'aumento in dollari viene tutto dal prezzo (~1.890 → ~4.520). Profilo orario piatto
   (~1,7 bps) con picco **21-23 UTC** (~2,0; domenica alle 22 UTC 2,18), coerente con CME e Batten et
   al. 2017 ([ricerca 29/09](reviews/ricerca_X_dati_oro_2026-09-29.md)). ⚠️ **Conseguenza strutturale**:
   SL e TP del mentore sono fissi in dollari mentre il prezzo e' piu' che raddoppiato, quindi il costo
   dello spread **in R cresce meccanicamente** nel tempo anche a liquidita' invariata. La divisione per
   anno (§5) va letta tenendone conto: un peggioramento negli anni recenti puo' essere geometria, non
   perdita d'abilita' del mentore.
8. **Informazione fissata guardando i dati (non gli esiti)**: il fuso (calibrato sulle entrate),
   L = 10 s (da trade dentro il campione), il filtro dell'universo (dal log del copier), i 4 trade live.

## 9. Cosa NON e' questo test

- **Non** misura il mentore: misura il **suo segnale copiato**. La posizione lunga di fondo non e'
  postata e non entra.
- **Non** valida il copier del socio (codice non disponibile, repo `gold-desk-trading-suite` 404).
- **Non** e' l'occasione per scegliere latenza, categorie o geometria: ognuna e' un trial, sul forward.

## 10. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-09-28 | Bozza, prima di qualunque esito | Proposta del socio: studiare le entrate in ritardo sui dati storici invece di raccoglierli live |
| 2026-09-28 | §3.1 eseguito (fuso = Europe/Rome), checklist dati, bias dello spread | Preparazione dei dati: solo entrate e prezzi, nessun esito |
| 2026-09-29 | Nessuna modifica alle regole. I 4 trade live (gia' in §8.8) analizzati coi tick in [reviews/gump_live_rr_qualitativo_2026-09-29.md](reviews/gump_live_rr_qualitativo_2026-09-29.md): lo scarto c'e' gia' al messaggio (1,8-3,1 $), e da giugno 2026 lo SL e' 3 $ | Informazione vista da dichiarare, come richiede §8.8. Nessun segnale storico simulato |
| 2026-09-28 | Riscritta dopo **G1 #1 = BLOCCA** (quant-gatekeeper): D1 come holdout = 100%, D2 corretta (budget 3, data d'approvazione), D3 nuova; sezione trial; tabella dei verdetti esaustiva, "FALSIFICATO" → "NON DIMOSTRATO"; SKIP per spread ≥ SL, BID/ASK per lato, timeout a tempo, tick con fallback; bracket puro motivato dal live; diagnostica Step 3bis corretta; drift non rimosso + divisione per lato + stesso lato a istante casuale; CI a cluster per giorno definito; stress sullo spread e swap; descrittive LIMIT, SKIP, spiegazione noiosa, finestra post-cutoff; MDE da ricalcolare sulla differenza | Nessuna modifica guarda un esito: sono tutte convenzioni che la bozza lasciava implicite |
