---
tipo: preregistrazione
stato: APPROVATA
aggiornato: 2026-10-02
decisione: "DECISIONS 2026-10-02 (approvazione)"
metrica_corrente: "nessuna: nessun esito calcolato"
nota: "APPROVATA da Matteo il 02/10 (G1 #4 PASSA con riserve, sistemate). Voce nel ledger con gate_finale forward; procedura di ripresa confermata. Prossimo passo: esecuzione unica di esegui_test.py."
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
| **D1** | Split | **L'intero campione (1.792 segnali, 09/09/2020 → 28/09/2026) e' l'holdout della famiglia. Il TRAIN e' vuoto.** Si apre **una volta**, alla data dell'esecuzione, registrata in `trial_ledger.json` (`holdout_aperto`). Su questi dati sono ammessi **0 round di rifinitura**. Qualunque variante successiva (latenza, categoria, LIMIT/SKIP, geometria, anno) si valida **solo sul forward** dopo il 28/09/2026, conta come trial e ha una sua pre-registrazione: sui 1.792 resta **descrittiva per sempre**. L'esito positivo massimo e' **LEAD** (LIFECYCLE §5: nessun OOS indipendente); **GO** solo dal forward | ✅ **DECISA da Matteo il 2026-10-02** (DECISIONS 02/10) |
| **D2** | Trimestre | Il budget esterno e' **3 per trimestre** (allarme a 2), e conta la **data di approvazione**, non quella d'esecuzione. Due strade pulite: **approvare nel Q3** (3 di 3, trimestre pieno) oppure **approvare dal 01/10** (1 del Q4) | ✅ di fatto **Q4**: oggi e' il 02/10, lo slot va alla data d'approvazione (dopo la G1 #2) |
| **D3** | Messaggi modificati | Se l'export contiene la versione **finale** di messaggi modificati dopo la pubblicazione, il copier ha visto un testo diverso: look-ahead d'informazione. Da verificare **prima** dell'esecuzione: il socio sa se il mentore modifica i segnali? Nell'export compaiono segni di modifica? | ✅ **chiusa come NON MISURABILE** (02/10): non esiste un export piu' vecchio di Gump. Resta il bias §8.3, direzione verso l'alto; lo strumento per misurarlo esiste (`analysis/mentor_signals/confronta_export.py`) e si usera' sul **prossimo** export, per il forward |

## 0bis. Stato del lavoro (dove siamo, cosa manca)

- ✅ Parser, prezzi M1 BID/ASK, fuso (98,9%), checklist dati — §3.
- ✅ G1 #1 (quant-gatekeeper, 28/09): **BLOCCA** su 5 punti; testo corretto in questa versione.
- ✅ **Motore** [`replay.py`](../analysis/forexgump/replay.py) (02/10): fill al tick ≥ t+L (ripiego M1), BID/ASK
  per lato, SKIP con spread ≥ SL, bracket ricentrato, uscite su tick per 60 min poi M1, troncamento a 24 h di
  calendario, stress, swap per rollover, entrambi i lati, CI a cluster per giornata (22 UTC). Varianti
  `live`, `limit`, `skip1`, `postato` (NON OTTENIBILE), meta' spread. 17 test su prezzi sintetici
  (`tests/test_forexgump_replay.py`).
- ✅ **Tick** nelle finestre dei segnali [−10, +85 min]: [`export_tick.py`](../analysis/forexgump/export_tick.py),
  2.573 ore, **complete il 02/10** (0 fallite; 72 ore vuote, tutte chiusure di mercato con 0 barre M1). Un trade usa i tick solo se TUTTA la sua finestra e' in cache,
  altrimenti va interamente su M1 e la quota si riporta. La guardia richiede 0 ore mancanti e che ogni ora
  vuota sia una chiusura di mercato (0 barre M1).
- ✅ **MDE sulla differenza appaiata** su istanti casuali (§6): 0,130R a cluster.
- ✅ **Script d'esecuzione unica** [`esegui_test.py`](../analysis/forexgump/esegui_test.py) con **guardia**: non parte
  se questo frontmatter non dice `stato: APPROVATA` o se la famiglia non e' nel ledger (verificato: blocca).
- ✅ **G1 #2** (02/10): BLOCCA sul codice (3 punti) + 9 riserve; **tutto corretto lo stesso giorno**, +4 test
  di regressione (14 in totale), prova a secco dello script completo su 60 istanti spostati: arriva in fondo.
- ✅ **G1 #3** (02/10): B2, B3, R1-R3, R5-R9 chiusi; due bloccanti nuovi corretti lo stesso giorno — N1 (la
  prova a secco ora usa tick sintetici dalle M1 ed esercita il percorso tick: 100% dei fill su tick, LIMIT
  eseguito) e N2 (controlli confrontati M1 contro M1, braccio reale rifatto su M1; il tick solo accanto).
  +3 test (17). Riserve sistemate: finestra +85 min, non eseguiti nel kill, spostamenti distinti per
  giornata, costo del ritardo sugli stessi segnali, momentum escluso con barre vecchie, CI del divario,
  guardia sulle ore vuote, `assert` sostituito.
- ✅ **G1 #4** (02/10): PASSA con riserve, sistemate lo stesso giorno (flag `--ripresa`, testo del §3).
- ✅ **Approvata da Matteo il 02/10** (DECISIONS 2026-10-02, approvazione): `stato: APPROVATA`, voce
  `forexgump_signals` nel ledger con **`gate_finale: "forward"`**: un LEAD con l'holdout aperto e' previsto per
  costruzione da D1 e `trial_ledger --check` lo accetta solo con questo campo, dichiarato prima dell'esito.
- ⏳ **Esecuzione unica** di `esegui_test.py`.
- **Procedura se l'esecuzione unica si interrompe dopo l'apertura dell'holdout** (**confermata da Matteo il
  02/10**): il referto parziale resta agli atti; il difetto si corregge come
  correzione di esecuzione (0 trial, [[feedback_correggere_non_e_cercare]]) e si rilancia **una** volta, con la
  ripresa scritta in DECISIONS **prima** del rilancio; nessuna soglia, variante o universo cambia. Eseguibile:
  `esegui_test.py --ripresa AAAA-MM-GG` (accetta solo a holdout gia' aperto e con la voce in DECISIONS; non cancella
  l'apertura, referto separato `_ripresa`).

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
| **Prezzi** | Dukascopy XAU/USD **M1 BID e ASK**, 2020-09-01 → 2026-09-28 ([export_prices.py](../analysis/forexgump/export_prices.py)). **Tick** nella finestra [−10 min, +85 min] di ogni segnale: completi dal 02/10, stato nel §0bis. Se per un segnale mancano i tick, **fallback M1** (§4) e la quota si riporta |
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
| **Fill** | primo tick **≥ t + L**: buy all'**ASK**, sell al **BID**. Fallback senza tick: apertura della prima barra M1 che inizia ≥ t + L, stesso lato. **Ritardo massimo del fill: 60 s dopo t + L, uguale per tick e M1**; oltre, esito `NON_ESEGUITO`, contato. I tick si usano **solo se tutte le ore della finestra sono in cache**: altrimenti l'intero trade va su M1 (mai un buco in mezzo alla serie) | Spread reale, non un costo fisso (G1 #2, B2) |
| **Ordine non eseguibile** | se al fill lo spread **reale** ≥ distanza SL (deciso sullo spread reale anche sotto stress, cosi' base e stress hanno lo stesso campione) (lo SL ricentrato cadrebbe oltre il prezzo d'uscita) → **SKIP**: il broker lo rifiuterebbe (invalid stops). Quota riportata sempre | 134 segnali (7,5%) cadono la domenica fra le 22 e le 23 UTC, alla riapertura, quando lo spread si allarga |
| **Bracket** | **ricentrato sul fill**: SL e TP alle distanze postate dal prezzo di fill. **Bracket puro**: niente BE, niente gambe multiple, i messaggi di gestione del mentore ("BE", "scarico") ignorati | E' cio' che fa il copier del socio **su Gump**: il 28/09 il bracket "come postato" chiude sullo SL originale (4147,89 = fill − 3 $) anche se il mentore aveva scritto "BE" alle 10:52. Le tre configurazioni live (come-postato, 8-8, 10-7) sono bracket paralleli, non gambe; la primaria e' **come-postato** |
| **Serie d'uscita** | buy → **BID** (high/low/close BID); sell → **ASK**. Alla primitiva si passano le serie del lato giusto | `core.resolve_trade` non conosce BID/ASK |
| **Uscita** | **tick** dal fill fino all'inizio del primo minuto intero dopo 60 min (la serie M1 parte esattamente li', senza buchi); poi M1 con pareggio **pessimistico** (SL prima del TP) | L'ottimistico si riporta accanto: la distanza fra i due e' la misura dell'ignoranza ([[feedback_convenzioni_implicite]]). ⚠️ `OTTIMISTA` cambia **due** assi: pareggio a favore del TP **e** `gap_beyond_stop=False` (uscita allo stop anche su un'apertura oltre lo stop) (R7) |
| **Timeout** | **24 h di calendario** dal fill, troncando le serie a t_fill + 24 h; chiusura a mercato marcata. Fra la chiusura del venerdi' e la riapertura della domenica passano ~49 h: un trade del venerdi' **non** arriva al gap del lunedi', si chiude all'ultima barra prima della pausa (R5) | `max_hold` della primitiva conta barre: serve il taglio a tempo |
| **Primitiva** | `core.resolve_trade`, `FillConvention(fill_bar_can_resolve=True, tie="pess", gap_beyond_stop=True, on_timeout="mark")` | Una sola primitiva |
| **R** | (uscita − fill) / distanza SL postata, meno costi | Il copier dimensiona sulla distanza SL |

**Costi — base.** Spread dai dati BID/ASK + commissione **0,07 $/oncia** andata e ritorno.
**Swap**: non modellato nella base; si riporta la quota di trade che attraversano il rollover delle
22 UTC. **Stress**: spread **×1,5**, commissione **×3**, **0,10 $** di slittamento per lato — in entrata nel prezzo di fill,
in uscita come **costo esplicito su ogni uscita che non e' un TP** (un TP e' un limite: non slitta; spostare la serie
avrebbe spostato anche il trigger del TP, R1) —
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
  - un **controllo secondario, stesso lato a istante casuale**: **3 controlli** per segnale, ottenuti
    spostando in blocco ogni giornata di ±1-20 giorni (stessa ora del giorno, stesso raggruppamento per
    giornata; l'anno puo' cambiare a cavallo di capodanno; spostamenti **distinti** per giornata), con **CI a
    cluster per giornata**. Fuori dalle finestre dei segnali non ci sono tick: il confronto e' **M1 contro
    M1** (braccio reale rifatto su sole M1) con il CI del **divario** mentore − media dei suoi controlli; il
    braccio su tick si riporta solo accanto (G1 #3, N2). Separa il *quando* dal *da che parte*. Il matching si verifica con
    `check_matching(exact=("side",), numeric=("risk",), observed=("hold",))` (G1 #2, R4: prima il testo
    diceva `BarSampler` stratificato per anno, il codice spostava le giornate);
  - la **durata d'holding** dei **tre** bracci (mentore, lato opposto, controlli): e' un esito, si
    riporta e si dichiara.
- **Primaria**: d e E[R] ottenibile, convenzione pessimistica, L = 10 s.
- **CI a cluster per giorno**: giorno = giornata di trading con rollover alle **22:00 UTC**, assegnata
  dall'istante di **fill**; un trade a cavallo resta nel giorno del fill. Bootstrap **percentile 95%**
  sugli indici dei giorni, **10.000** ricampionamenti, metrica = somma di R / numero di trade del
  ricampione. (La libreria non lo ha: `bca_bootstrap_ci` e' i.i.d., `gap_ci` fa il cluster per
  evento. Si implementa nel motore e si dichiara come debito.)
- **Diagnostica Step 3bis, riportata SEMPRE** (denominatore: i trade **eseguiti**, esclusi SKIP e non eseguiti): quota di segnali in cui il prezzo postato era **gia'
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
- **spiegazione noiosa**: lato = segno del movimento del mid fra la barra M1 **chiusa** entro t − 15 min
  e quella **chiusa** entro il messaggio (nessuna barra che finisca dopo t: G1 #2, B3). Movimento nullo:
  nessun lato, escluso e contato. Barre vecchie dopo una pausa (la chiusa entro t piu' vecchia di 2 min):
  escluso e contato. Stessa esecuzione. **Criterio**: il mentore aggiunge informazione a un momentum banale
  solo se il CI a cluster di (d_mentore − d_momentum), sugli stessi istanti, ha limite inferiore **> 0**;
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
| 4 | LB_d ≤ 0 | **NON DIMOSTRATO (MDE 0,130R)** — l'MDE dell'etichetta e' quello **pre-registrato**; accanto si riporta anche quello dall'errore osservato | Nessuna informazione direzionale **rilevabile**: la fonte non entra in pipeline. Si scrive accanto l'MDE, **non** "refutato" ([[feedback_verdetto_con_la_forza_del_test]]) |

⚠️ **Calibrazione.** "E > 0" come soglia puntuale si supera per rumore circa una volta su due quando
l'E[R] vero e' zero. E' accettabile **solo** perche' i casi 1-2 portano al forward, non al capitale.

**Potenza.** Da ricalcolare **sulla differenza appaiata**, non su R (la deviazione standard di d
dipende dalla correlazione fra i lati, spesso stoppati entrambi): simulazione su **istanti casuali**
degli stessi anni e delle stesse ore del giorno, senza toccare gli istanti dei segnali. Riferimento
grezzo su R (esiti quasi binari +5R/−1R, sd 2,4-2,75R, fattore 2,80): ~0,17-0,18R su 1.792.
**Misurato il 2026-10-02** ([potenza.py](../analysis/forexgump/potenza.py), 1.783 istanti casuali su 445 giornate, giornate spostate in blocco: stessa geometria, stesse ore, stesso raggruppamento; nessun istante dei segnali simulato): **MDE_d = 0,130R** a cluster per giornata (0,102R contando gli eventi come indipendenti); **MDE di E[R] = 0,171R** a cluster (0,132R indipendenti). Il raggruppamento costa ~30% di potenza. SKIP per spread ≥ SL sugli istanti casuali: 0,5% (soglia di kill 10%).

**Cosa significa un mancato rifiuto, scritto prima:** esclude solo effetti sopra l'MDE; non dimostra
che l'edge sia zero.

**Kill** (senza rifinitura): nessun offset di fuso con minimo netto (superato: §3.1); **> 10%** dei
segnali senza prezzi nella finestra **o non eseguiti** (nessun prezzo entro 60 s da t + L); **> 10%** di SKIP per spread ≥ SL (il copier non sarebbe
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
3. **Messaggi modificati** — D3 **chiusa come non misurabile** (02/10: non esiste un export piu' vecchio). Bias
   non verificabile dal passato; direzione: verso l'alto.
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
   E il **livello del baseline casuale** stampato da `potenza.py` (02/10) su 1.783 istanti spostati: lato
   qualunque, esiti TP 242, SL 1.515, TIMEOUT 26, SKIP 9 (G1 #2, R8). Non e' il mentore, ma e' informazione vista.

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
| 2026-09-28 | Riscritta dopo **G1 #1 = BLOCCA** (quant-gatekeeper): D1 come holdout = 100%, D2 corretta (budget 3, data d'approvazione), D3 nuova; sezione trial; tabella dei verdetti esaustiva, "FALSIFICATO" → "NON DIMOSTRATO"; SKIP per spread ≥ SL, BID/ASK per lato, timeout a tempo, tick con fallback; bracket puro motivato dal live; diagnostica Step 3bis corretta; drift non rimosso + divisione per lato + stesso lato a istante casuale; CI a cluster per giorno definito; stress sullo spread e swap; descrittive LIMIT, SKIP, spiegazione noiosa, finestra post-cutoff; MDE da ricalcolare sulla differenza | Nessuna modifica guarda un esito: sono tutte convenzioni che la bozza lasciava implicite |
| 2026-09-29 | Nessuna modifica alle regole. I 4 trade live (gia' in §8.8) analizzati coi tick in [reviews/gump_live_rr_qualitativo_2026-09-29.md](reviews/gump_live_rr_qualitativo_2026-09-29.md): lo scarto c'e' gia' al messaggio (1,8-3,1 $), e da giugno 2026 lo SL e' 3 $ | Informazione vista da dichiarare, come richiede §8.8. Nessun segnale storico simulato |
| 2026-10-02 | §0: D1 decisa (valutazione unica), D2 nel Q4, D3 non misurabile | DECISIONS 2026-10-02 |
| 2026-10-02 | §6: MDE misurato su istanti casuali (0,130R su d, 0,171R su E[R], a cluster); motore, script con guardia | Richiesto dalla G1 #1; nessun istante dei segnali simulato |
| 2026-10-02 | G1 #2 = BLOCCA sul codice: corretti B1 (varianti solo sul lato del mentore, referto a pezzi, prova a secco), B2 (tick solo a finestra completa, fill entro 60 s, giunzione), B3 (momentum su barre chiuse, criterio dichiarato); R1-R9 nel testo (slittamento come costo, SKIP su spread reale, quota oltre il rollover, controllo secondario allineato, venerdi', MDE dell'etichetta, assi di OTTIMISTA, informazione vista, guardia contro la seconda esecuzione) | Nessuna modifica guarda un esito |
| 2026-10-02 | G1 #3: N1 (prova a secco sul percorso tick con tick sintetici) e N2 (controlli M1 contro M1) corretti; riserve chiuse; procedura in caso di interruzione proposta (§0bis) | Nessuna modifica guarda un esito |
| 2026-10-02 | APPROVATA da Matteo; procedura di ripresa confermata; ledger con `gate_finale: "forward"` | Decisione prima dell'esecuzione: nessun esito calcolato |