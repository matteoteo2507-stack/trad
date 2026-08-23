# Blocco E — video pubblicati DOPO la chiusura del funnel

> Il funnel Chart Fanatics è stato dichiarato **chiuso il 2026-08-22** dopo 45 video.
> Il canale continua a pubblicare. Questo file raccoglie i video usciti **dopo** quella data.
>
> ⚠️ **Questione di processo, aperta e non risolta.** "Funnel chiuso" significava *non rileggiamo
> l'arretrato di altri canali*. Non era stata scritta una regola per i **video nuovi dello stesso
> canale**. Servono due decisioni: (a) li leggiamo tutti, a campione, o solo su segnalazione?
> (b) contano contro il tetto di **1 pre-registrazione** del funnel, che è già speso?
> Finché non è deciso, ogni video nuovo è **trattato come segnalazione**, non come intake corrente.

---

## E.1 — "Market Maker's Trading Strategy For Futures Prop Firms" (Freddy Siento) · 26.718 parole

`35cyqDz-ej8` · 149 minuti — **il video più lungo dell'intero canale**. Pubblicato il 2026-08-23.

**Chi è**: 20 anni in istituzionale, **market maker su outright e swap FX** per una banca
d'investimento a Londra (dichiara di aver coperto ordini fino a 1,5 mld di sterline); da ~3,5 anni
opera in proprio. Opera **NQ**, leggendo i livelli su **SPX/NDX**.

⚠️ **Conflitto d'interesse dichiarato in chiusura**: offre uno **sconto del 65%** sulla piattaforma
vendor (GEX-bot) che è indispensabile per applicare il metodo, pur precisando *"non lavoro per
loro"*. Più le sponsorizzazioni consuete (Apex, Ninja Trader, Hola Prime). Questo **non falsifica
il meccanismo** — ma colloca il video nella stessa categoria della demo StrategyQuant (Noel T.,
DECISIONS 2026-08-17): fonte con incentivo a far sembrare indispensabile uno strumento a pagamento.

---

### Il meccanismo — ed è il razionale economico più forte incontrato in 46 video

Questa è la parte che vale, e va separata nettamente dai numeri dichiarati.

1. Fondi pensione, dotazioni, fondi comuni **devono** coprire i portafogli — è un vincolo di
   mandato, non una scelta. Lo fanno con **opzioni su indici**.
2. Il **market maker** prende l'altro lato e **non può rifiutare**: il suo mestiere è fornire
   liquidità e incassare lo spread, non prendere posizione direzionale.
3. Per non fallire deve restare **delta-neutrale** → va sui **futures** (ES/NQ, la gamba più
   liquida) e compra/vende il sottostante.
4. Il prezzo si muove → il delta cambia (**gamma**) → deve **ricoprire ancora**. È
   **autoalimentante**: la sua copertura muove il prezzo, il movimento gli impone altra copertura.
5. Alle concentrazioni massime di gamma (**call wall / put wall**) la copertura da fare **si
   esaurisce**, e quando le posizioni si chiudono il flusso **si inverte** → il prezzo respinge.
6. Le **0DTE** (autorizzate dalla SEC nel 2021) hanno reso tutto questo violentissimo: dichiara che
   sono passate dal **21% al ~60-63%** del volume giornaliero. La sua analogia: prima il market
   maker copriva guidando a 80 km/h, oggi a 300 in Formula 1.

**Perché questo razionale è di categoria diversa da tutto il resto del funnel.** Non è psicologia,
non è "gli istituzionali cacciano i tuoi stop", non è un pattern grafico. È **meccanica di mercato
verificabile indipendentemente**: il delta-hedging esiste, è obbligatorio, ed è documentato nella
letteratura sulle opzioni. La fonte lo descrive **dal lato di chi lo eseguiva**.

⚠️ E dice esplicitamente la cosa che **coincide con il nostro NULL sui livelli** e con Cimbali
(C4.6): *"non gliene importa nulla dei retail, non gliene importa dei vostri stop, non gliene
importa della vostra liquidità — devono solo coprire il portafoglio"*. **Seconda voce con
esperienza di floor/market making a smentire lo stop-hunting.** Nel nostro registro questo è
coerente: i 384 trial dicono che i livelli non sono zone di reazione; qui un market maker dice
che il meccanismo che il retail immagina dietro quei livelli **non esiste**, e che quello vero è
un altro.

---

### I numeri dichiarati — e l'incoerenza interna che li affonda

| claim | valore |
|---|---|
| win rate | **75%** |
| stop | **30-50 tick** su NQ (~120-250 $) |
| movimenti citati | 384, 420, 478, 592, 800 tick (~2.000-4.000 $) |
| frequenza | **1-2 occasioni al giorno** |
| frequenza degli stop | *"prendo uno stop ogni due o tre settimane"* |

⚠️ **I due numeri di frequenza non possono essere veri insieme, e si controllano senza avere
alcun dato.**

Con **1-2 occasioni al giorno** e ~5 giorni operativi a settimana, "due o tre settimane fra uno
stop e l'altro" significa **da 10 a 30 trade vinti fra una perdita e l'altra** → win rate implicito
**90-97%**. Ma il claim dichiarato è **75%**, che a 1-2 trade al giorno significa una perdita
**ogni 2-4 giorni**, cioè circa **una a settimana** — non una ogni due-tre.

**I due numeri differiscono di un fattore 3-10.** Nello stesso video, a pochi minuti di distanza.

E il claim più aggressivo peggiora il problema: 75% di vittorie con rischio 30-50 tick e obiettivi
di 300-800 tick darebbe un'expectancy di **oltre +7R per trade**. Su ~350 occasioni l'anno sarebbe
il track record più straordinario mai documentato in finanza.

**Parziale riconciliazione, per onestà**: dichiara anche di portare rapidamente a break-even e di
uscire con più contratti scalati (*"prendo profitto su uno e lascio l'altro a break even"*), e i
tick citati sono i **movimenti del mercato**, non i suoi esiti medi. Quindi l'R:R **realizzato** è
certamente molto inferiore a quello potenziale. Ma questo è precisamente il punto: **pubblica il
potenziale e non il realizzato**, ed è il quinto claim del funnel che si comporta così.

Per protocollo: **le statistiche dichiarate restano in quarantena**. Il track record del funnel
diventa **5 claim alti su 5** privi dei numeri necessari a verificarli
(campione, periodo, baseline, taglia del rischio).

---

### Verdetto: **NON TESTABILE con i nostri dati — ma è il miglior REFERENCE del funnel**

**Perché non è testabile.** Servono dati che non abbiamo e che non sono a portata:

- **catena opzioni per strike** su SPX/NDX (open interest, gamma per strike);
- **superficie di volatilità implicita** in 3D (strike × scadenza × IV) e il suo *skew*;
- aggiornamento **intraday** — il dato pubblico CBOE è ritardato di 10-15 minuti, e lui stesso dice
  che quel ritardo rende il dato grezzo inutilizzabile;
- di fatto, un **abbonamento vendor** — il che rende il metodo, per noi, non un edge ma un costo
  ricorrente su un flusso che non possiamo verificare in modo indipendente.

E l'universo è indici azionari USA intraday: nella mappa di Kichev (D.1) è **la cella più
sovraffollata della griglia** — massima liquidità, timeframe minimo.

**Perché resta il miglior reference.** Tre cose che nessun altro video ha portato:

1. **Un meccanismo economico obbligato, non facoltativo.** Il market maker *deve* coprire. Nel
   nostro registro il "razionale economico assente" è un **kill duro** (`STRATEGY_LIFECYCLE §6a`):
   questo è l'unico caso del funnel in cui il razionale sarebbe passato quel gate a pieni voti.
2. **Una spiegazione di cosa siano davvero i low volume node** — la casella vuota B5 del backlog.
   Dice esplicitamente che i **picchi** di volatilità implicita corrispondono ai nodi ad **alto**
   volume e le **tasche** ai nodi a **basso** volume, e che il prezzo attraversa in fretta le
   seconde. ⚠️ Non cambia il verdetto su B5 — testeremmo comunque la versione amputata, senza il
   flusso — ma **fornisce il meccanismo** che a Carmine, Fabio e Yush mancava.
3. **Un calendario di eventi strutturali**, verificabile e pubblico: OPEX mensile (terzo venerdì),
   **triple witching** (marzo/giugno/settembre/dicembre), scadenza VIX (il mercoledì 30 giorni
   prima del terzo venerdì, che scade **alle 9:30**, cioè all'apertura), rollover trimestrale
   dell'hedge JP Morgan. Dichiara di **non operare** nei giorni di triple witching perché non ci
   sono 0DTE e quindi non ha edge.

---

### Il punto che tocca un nostro binario attivo

⚠️ **È la seconda fonte in due giorni a offrire un meccanismo per l'intraday sugli indici USA —
cioè esattamente il perimetro del nostro NO-GO ORB.**

| fonte | meccanismo proposto |
|---|---|
| Cimbali (C4.6) | flusso strutturale d'acquisto sugli indici + market maker obbligati a fornire liquidità |
| **Siento (qui)** | **copertura gamma obbligata delle 0DTE**, ~60% del volume, autoalimentante |

Il secondo è **più preciso e più falsificabile** del primo. E converge con un fatto che avevamo già
misurato e archiviato come anomalia: l'ORB era **negativo pre-2020** e il post-2020 (−0,208) non
batte il random in modo conclusivo. Le 0DTE sono state autorizzate **nel 2021**.

⚠️ **Questo NON riapre l'ORB, e va detto chiaramente perché.** È una coincidenza di date, non
un'evidenza: la stessa `feedback_backtest_long_history_falsification` avverte che *"funziona solo
post-2020"* è quasi sempre rumore più overfit al campione recente, e che un'ipotesi di
microstruttura **non è confermabile dal backtest che l'ha generata** — solo da un forward
pre-registrato. **Il forward ORB sta già girando ed è lo strumento giusto.**

**Cosa fare, a costo zero**: allegare **anche questo** razionale al forward ORB, accanto a quello
di Cimbali (voce C1 del backlog). Due meccanismi dichiarati *prima* dell'esito, invece di uno. Se
il forward risulta positivo sappiamo quali due ipotesi guardare; se negativo, ne abbiamo falsificate
due invece di zero.

---

### Riepilogo per il registro

| voce | esito |
|---|---|
| strategia | **NON TESTABILE** — servono catena opzioni + superficie IV intraday, e un vendor |
| razionale economico | **il più forte del funnel** — vincolo istituzionale obbligato, verificabile indipendentemente |
| statistiche dichiarate | **in quarantena**, con **incoerenza interna dimostrata** (75% vs "uno stop ogni 2-3 settimane") |
| effetto sul backlog | **nessun oggetto nuovo**; fornisce il **meccanismo** mancante a B5 (LVN) e un **secondo razionale** da allegare al forward ORB (C1) |
| pre-registrazioni aperte | **zero** |
