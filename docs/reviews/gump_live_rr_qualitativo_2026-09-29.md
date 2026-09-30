---
tipo: analisi
stato: quarantena
aggiornato: 2026-09-29
fonte_dati: "4 trade MT5 Gump del socio (21-28/09/2026, config come-postato) + tick Dukascopy + export Telegram"
nota: "Qualitativo, n = 4. Non e' un verdetto e non tocca la pre-registrazione: i 4 trade sono gia' dichiarati come informazione vista (§8.8)."
---
# Gump live: perche' il rapporto rischio/rendimento sembra lontano dal 1:5

> Domanda di Matteo e del socio (29/09): il rendimento live e' ridotto da un'**inefficienza del copier**
> o da una **struttura invalicabile dei segnali**? Risposta qualitativa sui 4 trade della prima settimana.
> La risposta quantitativa la da' la pre-registrazione
> ([FOREXGUMP_LATENCY_PREREGISTRATION.md](../FOREXGUMP_LATENCY_PREREGISTRATION.md)), sulle sue varianti
> descrittive (latenza, LIVE, LIMIT, SKIP).

## 1. Il 1:5 non e' la geometria di adesso

Dai 1.792 bracket dell'export (solo testo, nessun esito): SL mediano **2 $** e TP **10 $** (1:5) dal 2021
a **maggio 2026**; da **giugno 2026 SL 3 $** → **1:3,33**. Tutti i segnali della settimana live sono 1:3,33.
Le altre due configurazioni del copier del socio sono per costruzione **8-8 = 1:1** e **10-7 = 1:1,43**.

## 2. Il copier conserva il rapporto del singolo trade

Con il bracket ricentrato sul fill (come-postato) i due trade vinti hanno reso ~3,34 volte il rischio in
dollari (3,0-3,2 in euro: il conto e' in EUR) e i due persi −1. **Il rapporto per trade e' quello postato.**
Cio' che cambia e' **quali** trade arrivano al TP.

## 3. Da dove viene lo scarto d'ingresso

Scarto sfavorevole rispetto al prezzo postato, in dollari (prezzi Dukascopy tick; fill dal report MT5;
server MT5 a UTC+5, ricavato confrontando i due log del socio):

| Segnale | Ultimo istante in cui l'entrata postata era eseguibile | Al messaggio | Al fill (Dukascopy) | Fill MT5 | Broker vs Dukascopy | Spread al fill |
|---|---|---|---|---|---|---|
| 21/09 SELL 4373,80 | 68 s prima del messaggio | +2,77 | +3,20 | +3,07 | −0,12 | 0,57 |
| 23/09 SELL 4321,63 | 186 s prima | +1,82 | +1,88 | +1,79 | −0,09 | 0,48 |
| 28/09a BUY 4148,95 | 129 s prima | +2,45 | +2,11 | +1,94 | −0,17 | 0,57 |
| 28/09b BUY 4143,47 | 161 s prima | +3,07 | +2,90 | +2,72 | −0,19 | 0,58 |

- **Lo scarto c'e' gia' al messaggio.** Il mentore posta 1-3 minuti dopo l'ingresso, quando il prezzo si e'
  gia' mosso di 1,8-3,1 $ **a suo favore**.
- **La nostra parte e' piccola.** La latenza del copier (4-14 s) sposta il prezzo di ±0,4 $, in entrambe le
  direzioni. Il broker esegue 0,09-0,19 $ **meglio** di Dukascopy.
- **Lo spread** al fill e' 0,48-0,58 $: con SL 3 $ sono ~0,17R, pagati sempre.

## 4. Cosa succede dopo: lo stop ricentrato cade nel rumore

| Segnale | Bracket del mentore (livelli postati) | Bracket della copia (ricentrato) |
|---|---|---|
| 21/09 SELL | TP | TP |
| 23/09 SELL | TP | TP |
| 28/09a BUY | **SL** (08:52:15 UTC); il mentore dichiara "BE" perche' aveva gia' spostato lo stop all'entrata | SL dopo 3 min |
| 28/09b BUY | lo SL **non e' toccato per 3 centesimi**; TP dichiarato alle 09:51 UTC | **SL dopo 31 s** |

Il ricentramento sposta lo stop di 2-3 $ **verso il prezzo**, cioe' dentro l'escursione che lo stop del
mentore sopporta. E' la conseguenza diretta del punto 3, non di un difetto di esecuzione.

**I risultati dichiarati dal mentore includono la gestione** (stop all'entrata dopo +10 pip, chiusure
parziali: *"si puo' valutare una chiusura parziale…"*). Il copier esegue bracket puri, quindi **non puo'**
riprodurli.

## 5. Risposta qualitativa

**Struttura dei segnali, non inefficienza del copier.** Su questi 4 trade la parte migliorabile dal copier
(latenza, esecuzione del broker) vale quasi zero. Lo scarto nasce **prima** del messaggio: il mentore posta
dopo essere entrato e dopo che il prezzo si e' mosso. Nessun copier puo' recuperarlo; puo' solo scegliere
**come pagarlo**:

| Politica | Rapporto per trade | Cosa si sacrifica | Sui 4 trade |
|---|---|---|---|
| **Ricentrare** (oggi) | intatto (1:3,33) | lo stop cade nel rumore → meno TP | 2 TP, 2 SL |
| **Livelli postati, a mercato** | crolla (~1:1,1-1,7: rischio 4,8-6,1 $ contro 6,9-8,2 $ di premio) | quasi niente sul percorso: e' il trade del mentore | stessi esiti del mentore sul bracket |
| **Limite al prezzo postato** | intatto, ai livelli del mentore | i trade che scappano subito: **proprio i vincenti** (selezione avversa) | 21/09 e 23/09 mai riempiti (2 TP persi); 28/09a riempito → SL; 28/09b riempito → TP |
| **Saltare se lo scarto e' troppo grande** | intatto | frequenza | dipende dalla soglia |

Con 4 trade nessuna di queste si puo' preferire: e' esattamente cio' che le varianti descrittive della
pre-registrazione misurano su 1.792 segnali.

⚠️ **Ipotesi da non trascurare (non verificabile con 4 trade).** In tutti e 4 i casi il prezzo si era gia'
mosso **a favore** del mentore al momento del post. Se il mentore postasse piu' volentieri i trade partiti
bene, le entrate postate sarebbero **selezionate** su un movimento gia' avvenuto, e qualunque backtest al
prezzo postato (come quello della webapp) sarebbe gonfiato per costruzione. Lo misura la diagnostica dello
Step 3bis sulla distribuzione dello scarto al messaggio.

## 6. Cosa farebbe un copier "ideale" (per il socio)

1. **Registrare, non solo eseguire.** Per ogni segnale: istante di ricezione del messaggio, BID/ASK a quel
   momento, fill, spread, livelli postati e livelli effettivi. Con questi campi la tabella del §3 si produce
   da sola a ogni trade, e fra qualche settimana la risposta non e' piu' qualitativa.
2. **Tenere la latenza dov'e'**: non e' il collo di bottiglia.
3. **Confrontare in demo politiche di esecuzione, non geometrie.** Oggi le tre configurazioni (come-postato,
   8-8, 10-7) variano TP e SL, cioe' **parametri** presi dal backtest della webapp. Le domande che contano
   sono di esecuzione: ricentrato contro livelli postati contro limite. In demo le si puo' far girare in
   parallelo sugli stessi segnali.
4. **Decidere esplicitamente sulla gestione** (stop all'entrata dopo +X, parziali): oggi e' ignorata, e i
   risultati dichiarati dal mentore la contengono.

## Limiti

n = 4. Prezzi Dukascopy, non del broker (scarto misurato: 0,09-0,19 $). Il "momento del messaggio" e'
l'orario di invio su Telegram. Il mentore potrebbe essere entrato **prima** dell'ultimo istante indicato
nel §3, che e' solo un limite inferiore del suo ritardo.
