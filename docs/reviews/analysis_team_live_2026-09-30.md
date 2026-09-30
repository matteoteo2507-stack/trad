---
tipo: analisi
stato: quarantena
aggiornato: 2026-09-30
fonte_dati: "export MT5 del conto demo del socio 5056226036 (MetaQuotes-Demo, 'XAU Analysis Lab'), 21-29/09/2026: materiale_socio/dati socio 2/"
nota: "Descrittivo, n = 22 segnali. Non e' un verdetto. Il setup non e' quello congelato in COPIER_EXECUTION_PREREGISTRATION §2: se questi dati contino per N=60 lo decide Matteo."
---
# Mentore XAU in live sul PC del socio: la prima settimana con gli esiti

> Il 28/09 il log del copier del socio non conteneva chiusure ([DECISIONS 2026-09-28](../../DECISIONS.md)).
> Il 29/09 il socio ha esportato tutto lo storico del conto demo con uno script di sola lettura
> ([export.py](../../materiale_socio/dati%20socio%202/export.py)). Questa nota dice cosa contiene, cosa
> se ne puo' dire con 22 segnali e cosa manca per dirne di piu'.
>
> Il canale e' **XAU/USD ANALYSIS TEAM** = il **mentore XAU**, lo stesso della
> [validazione OOS](../MENTOR_SIGNALS_OOS_PREREGISTRATION.md) e del
> [test di esecuzione del copier](../COPIER_EXECUTION_PREREGISTRATION.md). Non e' Gump.

## 1. I dati reggono

| Controllo | Esito |
|---|---|
| Completezza | 1 deposito (25.000 EUR, 20/09) + 66 aperture + 66 chiusure = 133 deal; 132 ordini, tutti eseguiti; 0 posizioni aperte, 0 pendenti |
| Struttura | **22 segnali × 3 gambe** da 0,01 lotti (`MultiAcct-L1/L2/L3`, magic 770001). Le 3 gambe di un segnale partono entro 1 s |
| Coerenza col log del 28/09 | 20 segnali fra il 21 e il 28/09 = i "20 segnali eseguiti" del log; il 29/09 ne aggiunge 2 |
| **Fuso del server** | **UTC+3**: il 100% dei 120 fill cade nel range M1 Dukascopy dello stesso lato (buy su ASK, sell su BID, ±0,30 $); con ogni altro offset da UTC−1 a UTC+6 si resta sotto il 9%. ⚠️ Non e' l'UTC+5 ricavato per i trade Gump ([review del 29/09](gump_live_rr_qualitativo_2026-09-29.md)): **il fuso va verificato per conto**, non ereditato |
| Rischio | 3 × 0,01 lotti × SL 10 $ = 30 $ a segnale, circa **0,1%** del conto (la pre-registrazione dice 1%). Non cambia nulla in R |

Periodo: 21/09 14:46 UTC → 29/09 13:37 UTC. Commissioni, swap e fee: zero su tutte le posizioni.

## 2. Come esegue il copier del socio

E' la logica del nostro `signal_copier` per questo canale (`entry_mode = "trigger"`), anche se il codice
e' suo (magic e commenti diversi dal repo):

1. Sul messaggio **"BUY/SELL NOW"** apre 3 gambe **a mercato** con un bracket **provvisorio** centrato sul
   fill: SL a 10 $, TP a 5/10/15 $ ([planner.py](../../signal_copier/planner.py), `build_market_plan`).
2. Al messaggio coi livelli **riconcilia**: riscrive SL e TP con quelli postati
   ([executor.py](../../signal_copier/executor.py), `on_reconcile`).
3. Dopo il TP1, SL a break-even (al prezzo di fill della gamba L1) sulle gambe rimaste.

Lo si vede dagli ordini: il bracket d'apertura e' sempre fill ±10 / 5 / 10 / 15, mentre i livelli di
chiusura sono i numeri tondi del mentore.

## 3. L'entrata postata si ricava dai livelli, e il fill e' 2,6 $ peggio

Sui 255 segnali del mentore da giugno 2026 ([signals.csv](../../analysis/mentor_signals/signals.csv),
fino al 18/09) la geometria e' fissa nel **97%** dei casi (TP a ±5/10/15 $, SL a ±10 $) e l'entrata e'
sempre un numero intero. Quindi, quando una gamba chiude su un livello riconciliato,
**entrata postata = livello ∓ la sua distanza**. Il calcolo e' possibile su 18 segnali su 22, e fra le
gambe dello stesso segnale non c'e' mai disaccordo.

| | Valore (18 segnali) |
|---|---|
| Scarto fill − entrata postata, lato sfavorevole | mediana **2,62 $** (media 2,63), da −0,50 a +5,79 |
| In R (SL postato 10 $) | mediana **0,26R** |
| Sfavorevoli / favorevoli | **17 / 1** |
| Oltre **20 pip** (2 $) sfavorevoli | **10 su 18** |

E' la stessa struttura di Gump (1,8-3,1 $ al messaggio): il copier entra dopo il mentore, e l'oro si e'
gia' mosso nella sua direzione. Il broker aggiunge 0,1-0,7 s tra richiesta ed esecuzione (`time_setup` →
`time_done`), quindi lo scarto non nasce nel broker. Senza gli orari dei messaggi non si puo' dividere fra
il ritardo del mentore (NOW postato dopo il suo ingresso) e quello del copier.

**Effetto sulla riconciliazione.** Quando il fill e' peggiore, il TP1 postato e' piu' vicino del
provvisorio: sulle 17 gambe L1 chiuse a TP la distanza dal fill scende da **5,00 $** (provvisorio) a una
mediana di **2,72 $** (riconciliato). In **3 casi** (24/09 14:35, 28/09 08:20, 29/09 05:44 UTC) il TP1
postato stava **gia' dalla parte sbagliata del fill** e la gamba e' "arrivata a TP" in perdita
(−0,01 / −0,74 / −0,79 $). In un quarto caso (22/09 08:58, SELL) il TP1 postato non era piazzabile e la
gamba e' rimasta sul provvisorio.

## 4. Il gate anti-ritardo C5 non e' attivo su questo canale

La C5 del 18/09 ([DECISIONS 2026-09-18 (4)](../../DECISIONS.md)) ha reso il gate da 20 pip
**asimmetrico** perche', sul replay storico, entrare a mercato senza gate rendeva **−0,184** e col gate
sul solo lato sfavorevole **+0,159** (293 segnali su 696). Il gate vive in `build_plan`. Il canale del
mentore pero' passa da `build_market_plan`, che lo **spegne per costruzione**
(`current_price=None → gate anti-ritardo OFF: siamo a mercato per definizione`), e la riconciliazione
non lo controlla. Al momento del NOW l'entrata postata non esiste ancora, quindi nessun gate sul prezzo
postato puo' agire prima dell'ingresso.

Quindi **nel nostro codice la C5 e' attiva solo sui canali in modalita' `signal`**, non su quello per cui
e' stata misurata. Il copier del socio si comporta allo stesso modo: 10 segnali su 18 sono entrati oltre
i 20 pip e nessuno e' stato chiuso alla riconciliazione. E' la stessa classe di errore di
[[regola-di-filtro-si-verifica-per-effetto]]: una regola "implementata" che non agisce sul percorso che
conta.

⚠️ C5 ha misurato un'esecuzione diversa da quella live: fill a mercato **dopo il messaggio coi livelli**
(il `ts` di `signals.csv` e' quello del messaggio strutturato), con il gate sull'entrata postata. Il
copier entra **prima**, sul NOW. Le due strade per riattivare il gate vanno decise, non scelte guardando
questi 22 esiti (§7).

## 5. Esiti — descrittivi

R di ogni gamba = (uscita − fill) / distanza dello SL d'apertura (10 $); R del segnale = media delle 3 gambe.

| | n | E[R] | dev. std. | MDE (2,8 × SE) |
|---|---|---|---|---|
| **Segnale** (3 gambe, BE dopo TP1) | 22 | **−0,055** | 0,62 | 0,37 |
| **Solo gamba L1** = uscita a TP1, la metrica della pre-registrazione | 22 | **−0,029** | 0,56 | 0,33 |

Netto del conto: **−30,92 EUR** (profit factor 0,79 sulle 66 gambe, dal riepilogo del socio).

Esiti per segnale: 4 tutte a TP, 2 con TP1 e TP2, 11 con solo TP1 (le altre due a BE), **5 stop pieni**.
BUY −0,007 (12), SELL −0,113 (10).

**Cosa se ne puo' dire: niente sull'edge.** L'E[R] storico a TP1 e' +0,127
([COPIER_EXECUTION_PREREGISTRATION](../COPIER_EXECUTION_PREREGISTRATION.md), frontmatter; misura del
18/09 su 629 trade). La distanza fra i due (0,16R) e' sotto l'MDE (0,33R), quindi con 22 segnali i dati
sono compatibili sia con zero sia col valore storico. Uno stop pieno in piu' o in meno sposta la media di
0,05R.

## 6. Due eventi da conoscere

**Il BE rifiutato del 24/09 e' il segnale 11** (BUY, 14:35 UTC, fill 4262,01, entrata postata 4257). Il
TP1 postato (4262) era sotto il fill, quindi L1 chiude "a TP" in pari. Il BE a 4262,01 non si puo'
piazzare perche' il prezzo e' gia' sotto. Sono i 78 rifiuti in 25 minuti del log del 28/09. L2 e L3
restano sullo SL provvisorio e chiudono a −1R ciascuna alle 15:01. Costo: **−0,67R**, piu' di meta' del
totale della settimana (−1,21R). Nel nostro `executor` il difetto e' stato corretto il 28/09 (livello
gia' oltrepassato → chiusura a mercato). Che lo sia anche nel copier del socio non lo sappiamo.

**4 stop pieni su 5 sono avvenuti sul bracket provvisorio** (23/09 10:59, 25/09 05:19, 08:26, 08:50
UTC): lo SL colpito e' fill ±10 esatto, non un livello del mentore. Almeno nel caso del 25/09 08:50 il
trade e' durato 78 minuti, quindi il messaggio coi livelli, che di solito arriva entro circa un minuto,
avrebbe dovuto riconciliarlo. Le cause possibili sono tre: il canale non ha postato i livelli, il parser
non li ha letti, oppure `on_reconcile` li ha scartati come "re-entry" (`plan.reconciled`). Se il fill
era 2-3 $ peggio dell'entrata, lo SL provvisorio stava 2-3 $ **piu' vicino** di quello del mentore:
lo stesso meccanismo di Gump, con lo stop che cade nel rumore. Senza i messaggi non si distingue.

## 7. Cosa decide Matteo

1. **Questi dati contano per N = 60?** Il setup congelato (§2 della pre-registrazione: conto 5054470558,
   magic 27050, rischio 1%, gate a 20 pip) **non** e' quello che gira. In particolare il gate non agisce
   (§4). Proposta: registrarli come **descrittivi pre-correzione** e far partire il conteggio N = 60 dalla
   correzione del gate, con conteggio **spezzato pre/post**. La data d'inizio si scrive prima di vedere
   altri esiti.
2. **Come riattivare il gate** (correzione d'esecuzione, 0 trial: e' la decisione del 18/09 applicata al
   percorso giusto):
   - **(a) entrare sul messaggio coi livelli**, non sul NOW, e passare da `build_plan` col gate. E'
     l'esecuzione che C5 ha misurato. Costa circa un minuto di ritardo in piu';
   - **(b) entrare sul NOW e alla riconciliazione chiudere a mercato** se lo scarto sfavorevole supera
     20 pip. Si paga spread e movimento sui trade chiusi, e C5 non l'ha misurata.

   Da scegliere per coerenza con la misura, non sui 22 esiti. La (a) e' l'unica gia' misurata.

## 8. Cosa manca (richieste)

- **Export Telegram del canale** dal 18/09 a oggi, nella cartella stabile `_export_telegram/` (un export
  nuovo **sostituisce** il vecchio). Da quello: orario del NOW e del messaggio coi livelli → latenza vera
  e divisione del ritardo fra mentore e copier; segnali postati e **non eseguiti**; le cause dei 4 stop sul
  provvisorio; il **replay sugli stessi segnali**, cioe' il controfattuale richiesto dal §5 della
  pre-registrazione.
- **Log del copier del socio** sullo stesso periodo: rifiuti, riconciliazioni fallite, BE.
- Dal socio: il suo copier ha la correzione del BE del 28/09? E la riconciliazione aggiorna anche lo SL?
  Sul segnale 11 la gamba L1 e' stata riconciliata ma lo SL di L2 e L3 no.

## Limiti

n = 22. L'entrata postata e' **ricostruita** dalla geometria (97% dei segnali storici), non letta dal
messaggio. Il TP1 riconciliato dei 5 stop pieni non si vede. Gli esiti sul bracket provvisorio non sono
i trade del mentore. Prezzi di confronto Dukascopy M1 (fino al 28/09 20:31 UTC).
