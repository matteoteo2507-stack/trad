# DECISIONS — Decisioni già prese (decision log)

> **Perché questo file esiste.** Per non riallucinare scelte già chiuse né ricostruire
> analisi già fatte. Prima di proporre "costruiamo X" o "riattiviamo Y", **controlla qui**.
> Le decisioni si cambiano **con dati nuovi**, non con sensazioni — e quando cambiano, si
> aggiorna questo file con una nuova voce (non si riscrive la storia).
>
> Formato: ogni voce = *data · decisione · razionale · link*. Ordine: dal più recente.
> Questo file rispecchia nel repo le decisioni che vivono anche nella memoria di lavoro
> (`~/.claude/projects/.../memory/`), così sono visibili sfogliando il workspace e su GitHub.

---

## 2026-08-07 — Segnali mentore XAUUSD: **CONFERMATO fuori campione**. Primo OOS pre-registrato superato.

**Decisione.** L'edge direzionale del mentore **regge OOS**. È il **primo verdetto positivo su un
test pre-registrato** in questo workspace. Pre-registrazione:
[docs/MENTOR_SIGNALS_OOS_PREREGISTRATION.md](docs/MENTOR_SIGNALS_OOS_PREREGISTRATION.md) (scritta e
committata **prima** dell'esecuzione, commit `21df57b`). Motore:
[`analysis/mentor_signals/oos_validation.py`](analysis/mentor_signals/oos_validation.py).

**Finestra**: 131 segnali completi dal 15/06 al 07/08/2026 — **mai replayati** dall'audit dell'8
luglio, che si fermava al 12/06 per copertura prezzi. 121 eseguiti (fill entro 6h dall'entry).
Serie M5 estesa col feed MT5 e validata sulla sovrapposizione (8.063 barre, corr 1.000000, offset
mediano +$0.060 sottratto).

**Esito (soglie fissate prima):**
| Metrica | OOS | Audit luglio |
|---|---|---|
| Win-rate simmetrica mentore | **63,0%** | 67-72% |
| Win-rate side casuale | 35,0% | 32% |
| **Differenza appaiata** | **+0.277** · BCa95 **[+0.193, +0.353]** | — |
| **E[R] TP1 dopo costi** | **+0.194** · BCa95 **[+0.079, +0.289]** | +0.20/+0.32 |
| TP1 hit | 81,8% | ~85% |
| Stabilità mensile | 57,1% / 65,2% / 66,7% | 60-77% |

Entrambe le condizioni pre-registrate soddisfatte (lower bound della differenza > 0; E[R] > 0) →
**CONFERMATO**.

**BUG TROVATO E CORRETTO — allineamento orario.** Il sanity-check di riconciliazione, imposto dalla
pre-registrazione, è scattato. Test di shift sui timestamp (criterio **indipendente dagli esiti**:
minimizzare lo scarto mediano |entry dichiarato − prezzo al timestamp|): −1h → $16.34; **0h → $10.53**;
**+1h → $3.16 (minimo)**; +2h → $7.15. I timestamp Telegram sono **UTC+01:00**, la serie prezzi è in
**ora server broker (~UTC+2)**: serve **+1h**. Su stop da ~$10 uno scarto di $10.53 non è
trascurabile. Correzione di **bug**, non ritaratura → non conta come trial
([STRATEGY_LIFECYCLE §3](docs/STRATEGY_LIFECYCLE.md)). **Il verdetto regge in entrambi gli
allineamenti** (senza fix: 69,0% e E[R] +0.243); i numeri corretti sono più conservativi.

⚠️ **Conseguenza sull'audit di luglio**: usava lo stesso confronto naive → i suoi numeri (67-72%,
E[R] +0.20/+0.32) sono probabilmente **leggermente ottimistici**. Il valore realistico è quello OOS:
**~63% e E[R] ~+0.19**. Da ri-eseguire con il fix per allineare il record.

**Cosa NON autorizza.** (1) **Non** è un test di esecuzione: il forward reale del copier (2-8 giugno)
ha rifiutato **5 segnali su 12** perché il prezzo si era mosso oltre 20 pip — questo misura l'edge del
**segnale**, non quello **catturabile**. (2) **Non** cambia il divieto prop sui segnali di terzi
([PROP_FIRM_CRITERIA.md §4](docs/PROP_FIRM_CRITERIA.md)): resta capitale proprio. (3) Restano key-man
risk, un solo asset, un solo regime, e **survivorship confermata allo ~0,2%** (1 segnale cancellato
dal canale tra i due export).

---

## 2026-08-07 — Prop: copy-trading CHIUSO definitivamente + criteri nostri + consistency rule misurata

**1. Copy trading di segnali terzi: CASO CHIUSO.** Sesta e ultima verifica (catalogo
`propfirmtrader.com`, 18 firm, via browser dell'utente): **nessuna firm permette la copia esterna**.
La distinzione universale è **interno vs esterno** — copiare la *propria* strategia su *propri*
account è ammesso quasi ovunque, seguire segnali di terzi è vietato **anche in funded**, dove anzi è
più severo perché i programmi funded richiedono decisioni di trading indipendenti.

**Il divieto è strutturale, non commerciale**: decine di account che aprono la stessa posizione nello
stesso minuto sono il rischio concentrato che il modello prop esiste per evitare. Non è una policy
che cambia da firm a firm per marketing. → **L'edge mentore va su capitale proprio, o non va.**
Riapertura solo con evidenza esterna nuova ([docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md) §7).

*Nota metodologica*: `propfirmtrader.com` espone i regolamenti per **1 firm su 18** → **non
utilizzabile a livello di rulebook**, buono solo per censire il perimetro. Conferma la regola: si
lavora sui **regolamenti primari**. L'unico frammento recuperato (Alpha Capital, *"Group hedging or
prohibited copy trading"*) sta nella sezione **Trading Activity & Risk Review legata alle richieste
di payout** → conferma che l'enforcement scatta al **payout review**, non all'apertura.

**2. Criteri nostri prima delle firm** → [docs/PROP_FIRM_CRITERIA.md](docs/PROP_FIRM_CRITERIA.md).
Otto eliminatori derivati da cosa tradiamo davvero. I due che nessun comparatore espone e che ci
ucciderebbero in silenzio: **(a) daily drawdown su balance, NON su equity flottante** — `nxt_fade`
tiene posizioni fino a **20 giorni di borsa** su **6 strumenti in parallelo**, quindi un flottante
negativo (che poi gira a TP) farebbe scattare la violazione; **(b) holding overnight e weekend
consentito** — `nxt_fade` è **swing, non intraday**: le firm che obbligano a chiudere il venerdì lo
rendono ineseguibile. Nel ranking il **profit split è ultimo**, il **rischio di controparte** primo.

**3. Consistency rule: MISURATA, non stimata** — motore
[`analysis/nxt/consistency.py`](analysis/nxt/consistency.py) (riproduce esattamente i numeri
pre-registrati: E[R] +0.354, win 31.3%, n=10.280). Quota del giorno migliore sul profitto della
finestra, sole finestre in utile: **14 giorni → mediana 57,2%, sfora il 40% nel 74,7% dei casi**;
30 giorni → 41,9%; 60 giorni → **15,7%**.

**Alpha Capital (payout il 14 e il 28, regola 40% best-day): SQUALIFICATA** per questa strategia —
violeremmo 3 payout su 4, e sfora già il caso mediano.

**Mitigazione trovata**: allungando la finestra la violazione crolla (75%→42%→16%) → se la regola si
calcola **dall'ultimo payout** e l'accumulo è libero, richiedere il payout ogni ~60 giorni la rende
gestibile. Nuova domanda da porre a ogni firm: *dall'ultimo payout o dall'intera storia? Payout
obbligatorio a scadenza o accumulo libero?*

**Il risultato dura più della strategia**: non dipende dall'avere edge, dipende dalla **forma** della
distribuzione (payoff 1:3, trade sparsi). **Payoff 1:3 + payout bi-settimanale + consistency 40% =
incompatibili** per qualunque strategia di questa forma, anche futura. È un vincolo di
**progettazione**.

---

## 2026-08-07 — Pilastro investing OPERATIVO: Trade Republic + VWCE, 100 €/mese da fine settembre

**Decisione.** Il PAC passa da pianificato a **esecutivo**. Piano completo in
[docs/INVESTING_PILLAR_PLAN.md §0](docs/INVESTING_PILLAR_PLAN.md). **Broker: Trade Republic.
Strumento: VWCE** (`IE00BK5BQT80`, Vanguard FTSE All-World UCITS **Acc**, TER 0,22%, Irlanda),
verificato presente nel piano di accumulo dell'app. **Rata 100 €/mese**, data fissa, partenza **fine
settembre 2026**. **Nessun ribilancio** (uno strumento, 100% azionario, fase 1).

**Input personali (categoria A, chiusi):** 21 anni · rata 100 €/mese (l'utente aveva calcolato 150
sostenibili e sceglie 100 per garantire di non saltare mai) · obiettivo = capitale massimo per
smettere di lavorare quando vuole, **nessuna data d'uso** → orizzonte indefinito → **fase 1, 100%
azionario** · buffer e spese mensili **fuori perimetro** (li gestisce l'utente).

**Il vincolo strutturale che governa tutto: è un serbatoio, non un flusso.** Le entrate sono 2-3
stipendi estivi che coprono ~10 mesi (fino alla laurea, target 2 anni). Il PAC è un **prelievo a rate
da un serbatoio** → contromisura: a fine settembre si **vincolano €1.200** separati dai soldi di
spesa, e il PAC è garantito per l'anno a prescindere.

**Selezione broker (deep research 2026-08-04/07, 5 candidati).** Discriminante = **regime fiscale**,
non costo. **Esclusi per regime dichiarativo**: **Revolut** (ETF restano dichiarativi anche con IBAN
IT → quadro RT+RW ogni anno) e **IBKR** (nessuna stabile organizzazione in Italia → RT+RW+IVAFE; un
commercialista per il solo RW costerebbe >10% dei versamenti annui a questa scala). **Escluso per
frazionario**: **Directa** (arrotonda per difetto → a 100 €/mese alcuni mesi comprerebbe zero quote;
sarebbe ottimo a 500 €/mese). **Alternativa valida**: **Fineco** (Replay gratis under-30, ma il
vantaggio scade a 30 anni). **IBKR è rimandato, non escluso**: da rivalutare a portafoglio grande o
quando esisterà già un commercialista per il lato trading.

**Correzioni rispetto alla prima ricerca** (verifica utente su fonti ufficiali, 2026-08-07): il tasso
sulla liquidità è **2% ordinario** (BCE-linked, accredito mensile, **senza tetto** per IBAN IT), non
3% — il 3% è una **promo per nuovi clienti** fino a 50k. Il "niente RW/IVAFE" **non è dichiarato in
modo generale** nella documentazione ufficiale: il regime amministrato si applica **dopo la
migrazione alla succursale italiana**, non per data di apertura → verificare sulla certificazione
fiscale annuale. **Custodia e trasferimento titoli in uscita: NON PUBBLICATI** nel listino.

**Interessi sul vincolo: non sono una leva.** Saldo medio ~€600 → ~**€9/anno netti** al 2%
(~€13 con promo 3%), cioè lo 0,75% dei versamenti annui, e in termini **reali** circa a pareggio o
leggermente negativo. Non giustificano un aumento della rata: servono a pagare pochissimo
un'**opzione di liquidità** che nella situazione dell'utente ha valore vero.

**⚠️ La laurea NON è un trigger di aumento della rata**: il reddito sale ma salgono anche le spese
(vita da solo). Trigger corretto = **6-12 mesi dopo che la nuova struttura di spesa si è
stabilizzata**, su surplus verificato. Revisione **una volta l'anno a settembre**, agganciata al
ciclo di reddito, non all'anno solare.

---

## 2026-08-04 — Rituale di aggiornamento: dopo OGNI verdetto si allinea il repo

**Decisione.** Ogni verdetto (GO / LEAD / NO-GO / CLOSED / INSUFFICIENT DATA) chiude con
l'aggiornamento di **DECISIONS.md + memoria di lavoro + documenti impattati**, nella stessa
sessione. Non è un'attività opzionale di fine progetto: è parte del verdetto.

**Razionale.** Il buco trovato oggi lo dimostra: il **NO-GO NXT del 2026-07-17** e il lead fade
esistevano in memoria, in `strategie_candidate/` e in `_INTAKE.md`, ma **non in questo file** — cioè
non erano visibili a una sessione pulita che sfoglia il repo. Un decision log con dei buchi produce
esattamente ciò che esiste per impedire: riproporre cose già chiuse.

---

## 2026-08-04 — Ciclo di vita delle strategie: loop di ricerca formalizzato + criteri di bocciatura

**Decisione.** Adottato il loop `ricerca → formulazione → [G1] pre-registrazione → backtest (train) →
rifinitura (train) → walk-forward (train) → [G2] holdout sigillato → verdetto`, con criteri di kill
espliciti. Documento: [docs/STRATEGY_LIFECYCLE.md](docs/STRATEGY_LIFECYCLE.md).

**Razionale.** Un loop di miglioramento su dataset storico fisso è una **macchina per falsi
positivi** se non ha contabilità dei tentativi, dati sigillati e criteri di morte dichiarati prima.
Tre meccanismi rendono il loop non-tossico: (1) **contatore trial persistente** attraverso le
iterazioni (il DSR si applica al cumulato); (2) **holdout sigillato**, apribile **una volta per
famiglia** — se il budget si esaurisce prima, la famiglia muore senza averlo mai aperto;
(3) test operativo anti-p-hacking: *"avresti fatto questa modifica se il backtest fosse stato
positivo?"*.

**Criteri di kill.** Sei **kill duri** (difetto metodologico · non batte il random matched ·
fallimento di breadth · muore sui costi · instabilità parametrica · razionale economico falsificato)
e i **kill di budget**: **max 3 round di rifinitura per famiglia**, budget trial esaurito, e la
**regola di futilità DSR** (se il miglior risultato osservato è sotto la soglia di significatività
per il numero cumulato di trial, iterare è matematicamente inutile → kill immediato).
**Riapertura di una famiglia CLOSED solo con evidenza esterna nuova**, mai con un ritocco.

**Costo dimostrato:** la ricerca livelli è arrivata a **384 trial su 3 round** prima di chiudere il
libro; con un budget dichiarato in partenza sarebbe morta a v2.

---

## 2026-08-04 — Forward test FADE: pre-registrato a DUE STADI (50 boccia, 200 conferma)

**Decisione.** Il forward del fade — **già in corso da ~2026-07-24 senza pre-registrazione** — è
regolato da [docs/NXT_FADE_FORWARD_PREREGISTRATION.md](docs/NXT_FADE_FORWARD_PREREGISTRATION.md).
**Stadio 1 · N=50**: se E[R] ≤ 0 o win < 25% → **KILL** senza estensione; altrimenti prosegue.
**Nessun GO dichiarabile a 50, in nessun caso.** **Stadio 2 · N=200**: GO solo se il **lower bound
BCa 95%** su E[R] è > 0. Backstop 2026-10-31 e 2027-03-31; vale il primo evento.

**Razionale.** Il quant reviewer impone un *pavimento di sufficienza* (`n<50` → INSUFFICIENT DATA)
ma **non è una regola di stop**: è un gate a valle e non può sapere quante volte hai guardato prima
di sottoporgli i dati. L'asimmetria "negativo → raccogliamo ancora / positivo → chiudiamo" è
l'optional stopping, e il DSR penalizza le **varianti**, non le **sbirciate**.
Inoltre **N=50 è sottodimensionato per confermare**: con SD ~1,8R per trade l'errore standard su 50
trade è ~0,26R, quindi un E[R] vero di +0,35R darebbe un CI 95% **che attraversa lo zero** — per una
conferma a potenza 80% servono ~200-220 trade. Da qui i due stadi, entrambi fissati **prima** dei
dati. Il fade è **trial #2 di 3** della famiglia NXT e **non ha diritto a rifinitura** (è già nato
come rifinitura).

---

## 2026-08-04 — Prop firm: la traccia segnali-mentore NON è finanziabile su capitale prop

**Decisione.** L'assunto della roadmap *"prop anticipata dai segnali"* (2026-05-30) è **superato**.
Le prop non vietano solo l'automazione: vietano il **trading basato su segnali di terzi**. Verificato
su quattro firm indipendenti — FTMO, FundedNext, The5ers e Alpha Capital Group — che consentono la
copia **solo tra account di proprietà** e classificano il signal-following da canali Telegram come
*Group Trading* proibito. Se l'edge mentore va operato, va operato su **capitale proprio**.

**Perché morde davvero.** L'enforcement scatta al **payout review**, non all'apertura: si tradano
mesi e i profitti vengono negati quando si chiedono. Il rilevamento è per **pattern identici tra
account** — cioè esattamente la firma di più follower dello stesso mentore.

**Corollario.** La traccia **EA** resta compatibile (FTMO/FundedNext/The5ers/Alpha permettono EA su
MT5; vietati HFT, latency arbitrage, copy di terzi), ma oggi **non abbiamo nulla di finanziabile**:
ORB è NO-GO e il fade è un LEAD in forward. Scelta della prop **rimandata**, a valle di un GO.
Fattori da tenere presenti quando si riapre: **ESMA/MiFID II** in movimento sulle prop che si
rivolgono all'UE, avviso **CONSOB** del luglio 2024, 80-100 firm chiuse nel 2024 → il **rischio di
controparte è il criterio dominante**, non lo split. Alpha Capital: EA solo MT5 **con consegna del
sorgente `.mq5`** e **consistency rule del 40% best-day** — quest'ultima è testabile sulla
distribuzione del P&L giornaliero delle nostre strategie.

---

## 2026-08-04 — Fonti esterne: si raccolgono le regole, si scartano le statistiche dichiarate

**Decisione.** I canali/video di terzi entrano da [`_INTAKE.md`](fondamenti_tecnici/_INTAKE.md) e
alimentano **solo la fase RICERCA**. Due vincoli: (1) **mai importare le statistiche dichiarate nel
prior**; (2) **budget di max 2-3 pre-registrazioni per trimestre** da fonti esterne.

**Razionale.** Il track record dei claim esterni misurati da noi o da terzi: NXT ex-soci 60-70%
dichiarato → **13,3%**; bot VELTRIX 80-90% → **~53%**; ricerca livelli → **NULL** su 384 trial;
playbook Chart Fanatics 90% → **~20%** (test indipendente di terzi). Il collo di bottiglia non è mai
stata la fornitura di idee — è la **capacità di validazione**: ogni ipotesi in più alza
meccanicamente la soglia DSR per tutte le altre.

**Fonte valutata (2026-08-04):** *Chart Fanatics* / *Words of Rizdom* (Riz Iqbal) — stesso
ecosistema, monetizzato via Chart Academy e affiliazione con **Apex Trader Funding**; il metodo di
verifica dei trader non è pubblicato. **Uso approvato**: layer **operativo e di rischio** (pre-mortem
[04 §9](fondamenti_tecnici/04_quant_metodologia/principles.md)) + raccolta regole con filtro
d'ingresso (strumenti che tradiamo, regole codificabili senza discrezionalità, timeframe coperti dai
nostri dati).

---

## 2026-07-17 — NXT (Fibonacci/Elliott, ex-soci): continuazione NO-GO. Il FADE resta un LEAD.

> *Voce ricostruita il 2026-08-04: la decisione era tracciata in memoria, in
> [`strategie_candidate/nxt_fib_trend_pullback.md`](fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md)
> e in `_INTAKE.md`, ma mancava da questo log.*

**Decisione.** La strategia **NXT** degli ex-soci (continuazione: entry al ritracciamento 0.5,
SL 0.786, target 1:3) è **NO-GO**. Test **pre-registrato** su 6 asset H1 (EURUSD, GBPUSD, USDJPY,
XAUUSD, US100, US500), ~14 anni, ~10.000 setup — motori
[`analysis/nxt/backtest.py`](analysis/nxt/backtest.py) e [`closure.py`](analysis/nxt/closure.py).

**Esito.** Win rate **13,3%** contro il 60-70% dichiarato; **E[R] = −0,44R**; negativa in **14/14
anni** e **6/6 strumenti**; l'holdout conferma; le varianti wide-stop non salvano. È un **kill duro
per fallimento di breadth** — nessun set di parametri ripara un effetto che non esiste.

**Sottoprodotto.** Il **lato opposto** (FADE / mean-reversion: stessa entrata, posizione invertita,
R = 28,6% della gamba, TP 3R, BE a +2R) è **+0,35R** base e **+0,24R** a 3× i costi, positivo in
14/14 anni e 6/6 strumenti. **Ma è un'ipotesi data-derived** — nata invertendo una strategia che
perdeva, sugli stessi dati. → **LEAD**, non edge: richiede pre-registrazione nuova e forward OOS
indipendente. Spec eseguibile:
[`fade_mr_walkforward_socio.md`](fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md);
EA [`mql5/nxt_fade.mq5`](mql5/nxt_fade.mq5). Forward pre-registrato il 2026-08-04 (voce sopra).

---

## 2026-07-16 — Opening-Range Breakout (scalping single-asset, idea utente+socio): NO-GO su 14.5y.

Primo test del filone **scalping intraday single-asset**. ORB dell'apertura cash USA (09:30 ET) + retest,
US100/US500 M5, 1:2, pre-registrato ([docs/OPENING_RANGE_PREREGISTRATION.md](docs/OPENING_RANGE_PREREGISTRATION.md)),
motore [analysis/opening_range/](analysis/opening_range/). Verdetto: [docs/reviews/opening-range-2026-07-16.md](docs/reviews/opening-range-2026-07-16.md).

**Lezione del campione:** sul broker (1.4y, 2025-26) sembrava debole-positivo (E[R]+0.073, entrambi lati+),
ma su **Dukascopy 14.5y (2012-2026, tutti i regimi)** — richiesta utente di allungare lo storico — è
**NEGATIVO**: NAS100 E[R] −0.056 (BCa CI [−0.11, 0.00]), SPX500 −0.137 (CI [−0.19,−0.08]). Per-anno quasi
tutti rossi; positivi solo 2021/2026 = outlier di regime. Il +0.073 recente era **fortuna di regime**.
Entrambi i lati negativi. Il segno si ribalta tra broker e Dukascopy sul 2025 marginale = firma di edge
**inesistente** (E[R]≈0 → domina il rumore di feed). Filtro news (v2) improbabile che ribalti −0.1R base.

**Decisione: NO-GO.** Estendere lo storico ha **corretto un falso positivo** (valore del multi-regime).
Anche il filone scalping single-asset, testato bene, è null → coerente col resto (niente edge meccanico
own robusto). Dati Dukascopy M5 14.5y NAS100/SPX500 e motore ORB **riusabili** per varianti pre-registrate
future. Confermati i due binari: reddito=mentore manuale, ricchezza=passivo.

**Iterazioni (utente+socio), stesso verdetto:** (1) **filtro news** = peggiora (breakout serve vol; giorni
calmi = chop). (2) **filtro volatilità ADX** = leva GIUSTA (E[R] sale monotòno con ADX) ma tetto ~zero su
NAS, negativo su SPX. (3) **v2 completa** (SL su OR+10, RR 1:3, BE a 2R, expiry 12:00 ET, ADX): **NO-GO** —
l'**holdout** è decisivo: 2012-2019 negativo su entrambi (NAS −0.08, SPX −0.27), positivo solo nel recente
2020-2026 (non-significativo) → **non-stazionaria/regime-dipendente**, non edge persistente (stesso inganno
del campione 1.4y). Chiuso il filone ORB. `backtest_v2.py` riusabile.

**Infra nuova:** `dukascopy-python` per storico M5 lungo e gratuito su indici (2012+); backtester ORB
tz-safe (UTC/EET → US-open) + ADX + holdout. Utile per qualunque futuro test intraday su indici.

---

## 2026-07-08 — Stagionalità TOM: NO-GO. Chiusa la ricerca di edge sistematici own → pivot al passivo.

Terzo e **ultimo** edge sistematico. Test pre-registrato ([docs/SEASONALITY_PREREGISTRATION.md](docs/SEASONALITY_PREREGISTRATION.md)),
motore [strategies/seasonality/backtest.py](strategies/seasonality/backtest.py). Verdetto:
[docs/reviews/seasonality-tom-2026-07-08.md](docs/reviews/seasonality-tom-2026-07-08.md).

**Esito: NO-GO.** La finestra Turn-of-Month **non batte finestre di giorni casuali** (pooled +3.47 bps/g,
**p=0.238**); effetto **assente/negativo sugli indici** (US500 −1.0%, US100 −2.6%/anno) → anomalia
decaduta. Strategia long-TOM Sharpe −0.28 (BCa lower −0.69, DSR 0.008 n.s., MC p=0.48, OOS −0.21); il
buy&hold (+0.40) la batte. I positivi (ETH +118%/anno) = rumore small-sample.

**BILANCIO del pivot post-livelli (patto con l'utente attivato):** livelli null (384) · TSMOM NO-GO
(=beta, B&H batte, short perde) · mean-reversion NO-GO · router momentum+MR **refutato** (beta-trap) ·
stagionalità NO-GO. **Nessun edge sistematico *own* robusto** su questo universo/epoca/accesso retail.
L'**unico edge reale** è il **mentore** (discrezionale, manuale, external-dependent). Ciò che è robusto e
automatizzabile è **raccogliere beta** (long diversificato vol-managed) = il **pilastro passivo**.

**Decisione:** si **chiude la ricerca di edge sistematici own** (si smette l'edge-hunting a treadmill).
Due binari: **reddito = mentore manuale** (quando l'utente può), **ricchezza = pilastro passivo**
(automatizzabile, robusto). **Prossimo lavoro di più alto valore = costruire bene il pilastro passivo**
("strutturato e protetto"), in sospeso in attesa degli input personali utente (INVESTING_PILLAR_PLAN.md).
La macchina rigorosa (`core/quant_metrics` + backtester riusabili) resta per opportunità future.

---

## 2026-07-08 — Mean-reversion vol (secondo edge): NO-GO. Ma emerge la complementarità momentum⟂reversione.

Secondo edge del pivot (dopo TSMOM NO-GO). Test **pre-registrato** ([docs/MEANREV_PREREGISTRATION.md](docs/MEANREV_PREREGISTRATION.md)),
motore [strategies/meanrev/backtest.py](strategies/meanrev/backtest.py) (riusa la struttura TSMOM),
16 asset D1 2003-2026, z-score N=10 Z=1. Verdetto: [docs/reviews/meanrev-portfolio-2026-07-08.md](docs/reviews/meanrev-portfolio-2026-07-08.md).

**Esito: NO-GO.** Primario Sharpe **−0.21**, BCa lower −0.63, DSR 0.011 n.s., MC p=0.50, PBO 0.80,
White's RC p=0.94, walk-forward OOS −0.02. Tutte le varianti ≤ 0. Coerente col decay documentato.

**Rivelazione (il lead più forte finora):** Sharpe standalone MR **positivo sui RANGER** (EURGBP.r +0.56,
USDCAD +0.32, cross FX, indici) e **negativo sui TRENDER** (XAU −0.76, BTC −0.38) → **specchio esatto di
TSMOM** (XAU +1.44, US100 +1.19, cross FX negativi). Momentum e reversione, **deboli da soli**, sono
**anti-correlati per carattere dell'asset**. → Ipotesi (da PRE-REGISTRARE, non rivendicare): **sistema
combinato momentum+reversione / router trendiness** look-ahead-safe (efficiency ratio/Hurst su dati
passati, MAI gli Sharpe in-sample) validato OOS. È la materializzazione della tesi "portafoglio ortogonale".

**Decisione:** kill-switch → archiviare MR standalone. **Bivio (scelta utente):** (a) il combinato
momentum+reversione (lead forte, thesis-aligned) o (b) prossimo backlog (stagionalità/calendario).

---

## 2026-07-08 — Segnali mentore XAUUSD: edge direzionale REALE (primo positivo). → forward paper-validation.

Track A del pivot (priorità-1 utente). Parser + replay dei suoi segnali sul prezzo oro REALE (M5,
Gen-Giu 2026): **non un backtest disegnato, ma l'audit del suo track record live**. Codice
[analysis/mentor_signals/](analysis/mentor_signals/); verdetto [docs/reviews/mentor-signals-2026-07-08.md](docs/reviews/mentor-signals-2026-07-08.md).

**Riconciliazione**: i suoi entry stanno nei range intraday dell'oro reale (range 2026 mentore 3964-5553
vs reale 3999-5415) → è XAUUSD vero. Il mio flag "4670 vs 4155" era errore di allineamento (segnale di
metà 2026, oro in discesa) — CHIUSO.

**Esito (477 segnali replayati, dopo costo):** win-rate simmetrica **67-72%** vs **32%** del side casuale
(stessa geometria/tempi) → la sua direzione è giusta ~2/3 (non è drift dell'oro). Exit TP1 **E[R] +0.20/
+0.32**; TP1-hit reale ~85% (il suo claim "~100%" è ottimista). **Robusto al ritardo di copia manuale**
(E[R] +0.32→+0.12 da 0 a 60 min) e **stabile su tutti i 6 mesi** (60-77%). 5 angoli indipendenti concordi.

**Caveat vincolanti:** è una **COPIA** (key-man risk, non generatore nostro); 6 mesi/1 asset/1 regime
(oro in discesa); esecuzione idealizzata; survivorship non escludibile del tutto (ma baseline 32% +
"Sl hit"/"Running loss" nel canale remano contro). **Le prop vietano l'auto** → è la traccia **manuale**
(utilizzabile col telefono, ORA non disponibile), NON il milestone "1 mese demo non supervisionato".

**Decisione:** primo edge che **merita di proseguire**. → **forward paper-validation live** (~4-6 sett.,
out-of-sample vero, con esecuzione reale) via il parser; se tiene, è l'edge da operare **a mano** sulle
prop. In parallelo la traccia "sistema nostro" continua col prossimo edge del backlog. Nessuna promozione
a capitale senza forward.

---

## 2026-07-08 — TSMOM multi-asset (primo edge del pivot): NO-GO pulito. Kill-switch → mean-reversion vol.

Primo edge dopo la chiusura livelli. Test **pre-registrato** ([docs/TSMOM_PREREGISTRATION.md](docs/TSMOM_PREREGISTRATION.md)),
motore di portafoglio [strategies/tsmom/backtest.py](strategies/tsmom/backtest.py) sulle **serie di
rendimenti** (non le sintesi MT5 del tentativo 2026-05), 16 asset D1 2003-2026, spec canonica MOP
(sign 252g, vol-target 60g, media portafoglio, mensile, costi, look-ahead-safe). Verdetto completo:
[docs/reviews/tsmom-portfolio-2026-07-08.md](docs/reviews/tsmom-portfolio-2026-07-08.md).

**Esito: NO-GO.** Primario (252,mensile) Sharpe **+0.21**, ma **BCa CI [−0.18,+0.59]** (lower≤0),
**DSR 0.33 n.s.**, MC-perm **p=0.51**, **PBO 0.58**, White's RC **p=0.53**, walk-forward OOS +0.12
(degrado 51%). 5 test indipendenti concordi: **edge non distinguibile dal caso**. Overlay prop: maxDD
−40% → non avviabile.

**Novità vs 2026-05-29:** il multi-asset ha **risolto i difetti** del vecchio NO-GO (mono-asset/mono-anno):
breadth 12/16, top asset 16%, 13/23 anni positivi. Il problema non è più il campione — l'edge è
**semplicemente troppo debole** (~0.2) in questo universo USD-pesante / epoca decaduta post-2009
(atteso a priori: Baltas-Kosowski, SG Trend 0.3-0.5). Nessun curve-fit: verdetto per BCa+DSR+PBO+MC+WRC.

**Ipotesi (NON risultato):** trend concentrato negli asset che trendano (XAU +1.44, US100 +1.19, US500
+1.13, BTC +0.63) vs cross FX negativi (USDCHF −0.27, EURGBP.r −0.69). Un TSMOM "trending-universe"
*potrebbe* reggere, ma è **post-hoc** → va pre-registrato come nuovo trial e validato OOS, non rivendicato.

**Decisione:** kill-switch pre-registrato → **archiviare TSMOM canonico**, passare al prossimo edge del
backlog ortogonale (**mean-reversion vol non-level**), salvo scelta utente di pre-registrare prima la
variante trending-universe. La **macchina di validazione** (`core/quant_metrics` + backtester portafoglio)
è l'asset riusabile per gli edge successivi.

---

## 2026-07-07 (v3) — Livelli HTF fatti bene: confermato NULL. Libro CHIUSO davvero (384 trial).

Dopo l'audit delle tolleranze (la `0.10·ATR` era una costante ereditata/tarata su XAU-H1, applicata a
sproposito anche alle zone; i materiali dicono che i livelli forti stanno sugli HTF, che OB/S-D sono
**zone** con larghezza intrinseca e regola del **50% MT**, e che la struttura è **ubiqua**), abbiamo
rifatto il test **come si deve** (addendum pre-registrato). Motore `analysis/level_research/htf.py`:
- detection/misura su **H4, D1, W1** (H4 resample da H1, W1 da D1); **tolleranza scalata all'ATR del TF**
  (0.20 linea; le zone usano la **larghezza vera** + break = body-close oltre il 50% MT);
- **random distance-matched E structure-free** (rifiutato se cade su qualsiasi struttura vera — il punto
  che chiedeva l'utente); **freshness** naked/tested stratificata. FVG e Monthly esclusi (decisione utente).

**Esito (5 concetti × 3 TF × 16 asset = 240 trial): 0 sopravvissuti.** Pooled reale ≤ random su ogni TF
(spesso **negativo**: swing W1 CI[−2.4,−0.7], D1[−2.0,−1.3], H4[−1.5,−0.8]; prev H/L, round, EQH/EQL
idem; OB il "meno peggio" ma CI che tocca 0, breadth 2/16). **7 celle "battono" su 240, attese ~12 per
caso** → sotto il rumore. **Freshness piatta** (naked ≈ tested, entrambi ≤ random) → smentisce anche la
tesi "fresh≫tested" dei materiali. Con il random *structure-free* i livelli reagiscono spesso **meno del
vuoto** → coerente con "i livelli sono dove il prezzo rompe/consuma liquidità, non dove rimbalza".

**Robustezza tolleranza:** il null tiene a **0.10·ATR** (v1, H1) **e** a **0.20·ATR** (v3, H4/D1/W1) →
non è un artefatto della soglia. **Totale ricerca livelli: v1(96)+v2(48)+v3(240) = 384 trial
pre-registrati, 0 edge.** "Il prezzo reagisce ai livelli come zona" è **falsificato a fondo, su ogni
timeframe e con la metodologia dei nostri stessi materiali.** Libro chiuso senza rimpianti. **Pivot** a
strategie **non** level-based (razionale economico/peer-reviewed) — da decidere con l'utente.

---

## 2026-07-07 — Ricerca livelli v2 (volume): 0/3 concetti. Libro CHIUSO (144 trial, 0 edge).

Testata l'ultima famiglia rimasta (concetti **volume**, tick-proxy), stesso protocollo pre-registrato
([addendum](docs/LEVEL_RESEARCH_PREREGISTRATION.md)): POC/VAH/VAL, VWAP, anchored VWAP × 16 asset.
**Nessuno batte il random distance-matched** — breadth 0/16 ciascuno, pooled reale≈random (POC 30.1
vs 30.5 CI[−0.8,+0.1]; VWAP 30.6 vs 30.5 CI[−0.7,+1.0]; AVWAP 29.7 vs 29.7 CI[−0.5,+0.4]). **0 celle
"battono" su 48** (attese per caso ~2.4). Caveat dichiarato: volume = tick-proxy su tutti gli asset.

**Conclusione (regola pre-registrata).** v1 (6 OHLC) + v2 (3 volume) = **9 concetti × 16 asset = 144
trial, 0 sopravvissuti.** La premessa "il prezzo reagisce ai livelli come zona" è **falsificata in modo
ampio e a prova di p-hacking**. **Libro livelli-come-zona-di-reazione CHIUSO. Pivot.** Unico angolo mai
testato (e volutamente non aperto: alto rischio DoF/overfit) = livelli come *filtro condizionale* dentro
un contesto direzionale/sessione — NON è "reazione al livello", è un'altra ipotesi. Motore
`analysis/level_research/` resta riusabile per qualsiasi nuovo concetto (basta dichiararlo nuovo trial).

---

## 2026-07-06 — Ricerca livelli v1: NESSUN concetto batte il random (0/6). Pivot.

**Contesto.** Dopo il NO-GO del conf=2 (sotto), abbiamo rifondato la domanda: *quali criteri trovano
livelli dove il mercato reagisce davvero?* Test **pre-registrato**
([docs/LEVEL_RESEARCH_PREREGISTRATION.md](docs/LEVEL_RESEARCH_PREREGISTRATION.md)), motore walk-forward
look-ahead-safe ([analysis/level_research/](analysis/level_research/)), **6 concetti OHLC-puri** ×
**16 asset** (FX/metalli/crypto/indici, feed demo4 validato), metrica = **%REACTION|touch reale vs
random distance-matched**, CI block-bootstrap sui giorni, breadth, DSR sui 96 trial, holdout 70/30.

**Esito (TRAIN, breadth = asset che battono / testati):**
| concetto | breadth | pooled %REACT reale vs random | CI95 diff | esito |
|---|---|---|---|---|
| swing S/R | 1/16 | 29.0% vs 29.8% | [−1.1, −0.6] | peggio del random |
| PDH/PDL | 0/16 | 28.8% vs 30.5% | [−2.4, −1.2] | **peggio** (rotti più del caso) |
| order block | 3/16 | 30.0% vs 29.6% | [+0.0, +0.9] | pool>0 ma breadth<50%, ~0.4pt |
| FVG | 0/16 | 29.6% vs 29.8% | [−0.5, +0.2] | nullo |
| round number | 0/16 | 29.4% vs 30.1% | [−1.1, −0.3] | peggio del random |
| EQH/EQL | 0/16 | ~nullo | — | nullo |

**DSR/molteplicità:** 4 celle "battono" su 96; falsi attesi per caso a CI95 = 0.05·96 ≈ **4.8** →
osservati ≤ attesi = **rumore**. La %REACTION è ~29-30% ovunque, **identica** tra livello "vero" e
punto arbitrario alla stessa distanza.

**Decisione (regola pre-registrata attivata).** Nessun concetto sopravvive → a questa risoluzione
**i livelli non sono zone di reazione**: la posizione "strutturale" non aggiunge nulla oltre la
distanza. Generalizza il conf=2 su 16 asset × 6 concetti. **Non forziamo edge dove non c'è → Pivot.**

**Scope onesto (NON falsificato):** (a) concetti **volume** (POC/VWAP/TPO), rimandati a v2 (proxy su
FX); (b) livelli come **filtro condizionale** in un contesto direzionale/sessione (non zona di reazione
unconditional); (c) altri timeframe/orizzonti. Unici spiragli prima di chiudere il libro "livelli".

---

## 2026-07-05 — Level Analyzer conf=2 (fade): **NO-GO forward** (i livelli ≠ zone di reazione)

**Decisione.** Il fade sistematico dei livelli conf=2 (XAU+BTC) è **NO-GO**. Analisi con 3 agenti
Fable indipendenti (criteri di reazione dai materiali · audit fallacie · misura reazione-vs-random)
su 101 record forward (18-06 → 05-07-2026, 81 riconciliati).

**La prova decisiva = misura DIRETTA dei livelli** (indipendente dalla meccanica del trade): i
livelli conf=2 **non reagiscono più di livelli casuali** alla stessa distanza (BTC 18.5% vs 22.5%,
CI include 0; con baseline a 0.3–6 ATR reagiscono *meno* del caso); **~63% dei touch finisce in
break**. La classificazione livello→esito è forte (REACTION→67% win, BREAK→13% win): i livelli sono
in maggioranza cattivi. Coerente col trade E[R]=−0.37R (CI esclude 0).

**Il trade da solo NON basta a concludere (audit).** Il forward NON testava la strategia validata:
24/7 vs sessione 06–21 (61/101 fuori finestra), livelli "appena nati" ricalcolati sulla barra in
formazione (repaint → fade del momentum), XAU su **GC=F futures** (spec: spot), exact-touch vs fill
tollerante. Inoltre "conf=2" NON era 2 nature diverse (47/101 = stessa natura doppia; `cluster_confluence`
conta i membri) e il backtest "+0.15R" era esso stesso debole (CI iid su trade clusterizzati,
selezione post-hoc del bucket). → il −0.37 del trade è confondato, MA la misura diretta (C)
falsifica il **concetto** alla radice: non serve "fixare il protocollo e ri-fadare".

**Razionale.** N-esimo negativo custom (cfr. London Breakout, TSMOM, Stock Selector, sweep+reclaim,
regime gate). Il workflow ha fatto il suo lavoro: refutato strategia **e** la sua validazione debole,
prima dei soldi veri. Il Level Analyzer va **sospeso** (stop `run` sul server); il workflow
(capture→reconcile→gate + agenti) è l'asset riusabile che resta.

**Reverse/breakout anch'esso REFUTATO (check `breakout_check.py`, 13y/6y):** tradare la direzione
OPPOSTA alle zone conf=2 è **catastrofico** (XAU −0.78 / BTC −0.70 / EUR −0.77, win 11-16%), molto
PEGGIO del random → nessun edge inverso, le zone non sono neanche livelli di breakout. Chiude
"tradare questi livelli in qualunque direzione". NB tensione: nel **backtest** il fade batte il
random (+0.19 vs −0.16) ma NON regge **forward** (−0.37) → edge in-sample fragile/overfit + protocollo
forward rotto. C'è debole struttura mean-reversion in-sample (il reverse-catastrofico lo conferma),
troppo fragile per la meccanica grezza e diluita dal blob conf=2.

**Segnali deboli conservati (non azionabili, n piccolo):** natura **OB** sopra media (33% reaction,
n=21) e regime "transizione" (n=13); **FVG** (5% reaction, 90% break) e regime "range" (0/18) = rumore.
XAU inconcludente (futures + n=29). **Bug noti:** conteggio no_fill nel gate (fill reale ~83%), fill/exit
idealizzati (−0.37 = upper bound).

→ Analisi: [`analysis/trading-bot-eval/level_reaction_analysis.py`](analysis/trading-bot-eval/level_reaction_analysis.py) ·
spec [`LEVEL_ANALYZER_SPEC.md`](analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md) ·
workflow [`docs/TRADING_WORKFLOW_DESIGN.md`](docs/TRADING_WORKFLOW_DESIGN.md)

---

## 2026-06-14 — OctoBot (traccia crypto): **DORMIENTE**

**Decisione.** La traccia **OctoBot / crypto-automation** è messa in **stand-by (dormiente)**, non
archiviata: rispolverabile in futuro se si riapre esplicitamente un fronte crypto. **Emenda la priorità
del 2026-05-30** (sotto), dove OctoBot era #1.

**Razionale.** Dopo il pivot di giugno 2026 il lavoro reale è su **forex/XAUUSD via MT5** (signal copier
mentori, prop), **quant** (quant-review, metriche, backtest) e **investing passivo**. OctoBot è
**crypto-only** (esecuzione via ccxt, nessun MT5/forex) → non serve lo stack attuale. La priorità "#1
OctoBot" era anteriore a questo pivot. La review della repo forkata conferma: i pezzi che sembravano
combaciare (TelegramSignalEvaluator, modulo `signals/`) sono esempi banali / plumbing interno crypto, meno
adatti del nostro `signal_copier`.

**Condizione per riaprire.** Quando (a) si decide consapevolmente di aprire un fronte crypto-automation
**E** (b) c'è slack-time dopo milestone-1 forex. Allora OctoBot torna candidato come executor crypto.

→ Review: `github_repo_reviews/OctoBot.md` (memoria di lavoro) · Stage storico: [ROADMAP.md Stage 6](ROADMAP.md)

---

## 2026-06-14 — Terzo secchio (sleeve trend/managed-futures): **RIMANDATO a fase 2-3**

**Decisione.** Il pilastro investing resta a **due secchi** (buffer + All-World PAC) in fase di
accumulo. Lo *sleeve* trend-following / managed-futures — idea emersa dal materiale
volatility-drag / orthogonal-streams (QuantGuild) — **non si aggiunge ora**: è uno strumento di
**riduzione del drawdown**, quindi appartiene alla **fase 2-3** del glide-path (preservazione),
dove il piano già prevede una quota "difensiva". Quando ci si arriverà, va valutato come
**diversificatore del secchio difensivo accanto/al posto dei bond** (che nel 2022 hanno fallito la
diversificazione, correlazione salita coi tassi), **mai con leva**, **mai come "batti il mercato"**.

**Razionale.** (1) **Phase mismatch decisivo**: in accumulo il drawdown è un ALLEATO (il DCA compra
a sconto) → pagare carry negativo / CAGR inferiore per assicurarsi contro un non-rischio è sbagliato
ora (guardrail quant §3 del piano). (2) Il **principio** è solido (stream ortogonale R²≈0 → meno
drawdown → meno volatility drag → meglio geometrico; il trend-following fu orthogonale/positivo nel
2022 quando i bond fallirono), ma la **ricetta** commerciale (leva + hedge-leg "batte SPY") è un
singolo backtest in-sample non robusto. (3) **Praticità retail-IT**: gli strumenti canonici
(DBMF/KMLM) sono **US-domiciled** → estate tax + non-armonizzati + fisco complesso; opzioni UCITS
sottili, da verificare al momento. (4) La **base non è ancora costruita**: il piano a 2 secchi non
ha ancora i numeri (categoria A) → non aggiungere il layer più avanzato prima delle fondamenta.

**Condizione per riaprire.** Quando (a) il pilastro passivo è numericamente vivo **E** (b) si entra
in fase 2-3 del glide-path **E** (c) esiste un veicolo UCITS trend/managed-futures verificato (TER,
AUM, domicilio) → valutarlo come quota **modesta** del difensivo, misurandone il contributo reale a
drawdown/correlazione, **non** con leva.

**Corroborazione esterna (2026-06-14, review GitHub).** Il `ManagedFuturesAnalyzer` di FinceptTerminal
(impostazione standard CFA) classifica i managed futures come *"The Flawed"*: i benefici di crisis-alpha
**non giustificano** i costi (2&20), cita capacity constraints, e suggerisce **replica via ETF
trend-following low-cost o di saltare del tutto**. Converge con la nostra decisione (fee drag vs
crisis-alpha) e con la cautela sul singolo backtest levered-hedge. Da rileggere quando si riapre lo
sleeve in fase 2-3 → `github_repo_reviews/FinceptTerminal.md` (memoria di lavoro).

→ [docs/INVESTING_PILLAR_PLAN.md §3b](docs/INVESTING_PILLAR_PLAN.md) ·
teoria [fondamenti_tecnici/05_portfolio_rischio](fondamenti_tecnici/05_portfolio_rischio/principles.md) ·
caveat evidenza [fondamenti_tecnici/08_asset_allocation_passiva](fondamenti_tecnici/08_asset_allocation_passiva/principles.md)

---

## 2026-06-02 — Due tracce parallele + pivot Stock Selector → TAA risk-management

**Decisione.** Il lavoro procede su **due strade parallele**, non più in catena unica:
1. **Esecuzione/dati**: Telegram signal copier, OctoBot, Confluence automatica.
2. **Quant/investing**: parte dai **dati e dall'infrastruttura dello Stock Selector**.

Quando un fronte non ha lavoro attivo (solo raccolta dati), si avanza sull'altro. Questo
**emenda** la catena di priorità del 2026-05-30 (sotto): non un ordine rigido, ma due tracce
concorrenti. Vincolo invariato: **non promuovere nulla a capitale reale** finché la milestone-1
(mese demo positivo) non è raggiunta; il lavoro investing resta **validazione**, non operatività.

**Pivot Stock Selector.** Lo stock-picking cross-sezionale nell'SP500 è **falsificato**
(IC momentum ~0 a 12y, score fondamentale anti-predittivo — vedi review). Lo Stock Selector
pivota verso un **motore di asset-allocation tattica (TAA)** = gestione del rischio fattoriale
β<1 (timing dell'esposizione + dual-momentum cross-asset), **non** ricerca di alpha da selezione.
Layer 2-3 (selezione titoli) **congelati**; Layer 4 (multi-mercato) futuro.

**Correzione dati.** Per i backtest PIT survivorship-free i vendor sono **Sharadar SF1 / Norgate**,
**non Interactive Brokers** (che non fornisce titoli delistati → survivorship bias). IB resta
valido solo per l'esecuzione live. Acquisto dati rimandato finché il Layer 1 (gratis: ETF +
FRED) non supera il gate `/quant-review`.

→ Design + merge review a 5 agent: [docs/INVESTMENT_ALGO_DESIGN.md](docs/INVESTMENT_ALGO_DESIGN.md) ·
Review dati: [docs/reviews/stock_selector-2026-06-01.md](docs/reviews/stock_selector-2026-06-01.md)

---

## 2026-05-30 — Ordine di priorità del workspace

**Decisione.** Priorità in quest'ordine: **(1) OctoBot** → **(2) dati da Confluence + Telegram
signal copier** → **(3) prop firm** (anticipata dai segnali, se i dati reggono) → **(4) strategie
automatiche custom (IN FONDO)**.

**Razionale.** Concentrare l'energia su ciò che è già pronto a produrre dati/segnali invece
di disperdersi a costruire nuove strategie custom. Le strategie/agenti custom (incl. tutti i
*blueprint* in `fondamenti_tecnici/blueprints/`) restano backlog finché OctoBot e la raccolta
dati non sono completi. **Non riproporre dev custom finché OctoBot non è completo.**

---

## 2026-05-2x — Telegram Signal Copier: demo full-auto, prop rimandata

**Decisione.** Il copia-segnali (2 canali mentori → MT5) gira in **demo, full-auto**. La prop
sui segnali è **rimandata** (anticipabile se i dati demo reggono, vedi priorità sopra).

**Razionale + caveat.** Fase di test per validare parsing + risk gate prima di rischiare capitale.
Attenzione **compliance copy-trading** lato prop firm (alcune vietano la copia di segnali terzi).
Architettura: Telethon → parser → risk gate → MT5. I segnali mentori sono oggi **semiautomatici
in test** ma il target è la **piena automazione**.

→ Codice: [signal_copier/](signal_copier/) · Test: [tests/test_signal_copier.py](tests/test_signal_copier.py)

---

## 2026-05-30 — London Breakout: **NO-GO** (archiviata)

**Decisione.** London Open Breakout EA **archiviata**. Non si promuove a capitale reale.

**Razionale.** Quant review: su 686 trade (2020–2026) PBO alto, DSR non significativo, e l'edge
percepito dal regime gating era **look-ahead** (label calcolato sul close dello stesso giorno).
Il codice resta conservato in `mql5/` ma non è deployabile.

→ Review: [docs/reviews/london_breakout-2026-05-29.md](docs/reviews/london_breakout-2026-05-29.md) ·
Postmortem: [docs/reviews/london_breakout-postmortem-2026-05-30.md](docs/reviews/london_breakout-postmortem-2026-05-30.md)

---

## 2026-05-2x — Caveat look-ahead della regime timeline

**Decisione/Regola.** `data/regime_timeline_gbpusd.csv` ha il label calcolato sul **close del
giorno stesso** → usarlo **SOLO con lag 1 giorno** per strategie intraday, altrimenti si gonfia
l'edge. È stato il cap della quant-review di London Breakout.

**Razionale.** Evitare look-ahead bias (vedi [fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/)).

---

## 2026-05-29 — TSMOM USDJPY: **NO-GO / dati insufficienti**

**Decisione.** TSMOM single-asset (USDJPY D1) **non promosso**.

**Razionale.** 38 trade, DSR ≈ 0, l'edge dipendeva da 1 trade (regime 2021-22); sotto-campione
2024-26 negativo. Possibile rivalutazione solo in versione **multi-asset** con campione adeguato.

→ Review: [docs/reviews/tsmom_jpy-2026-05-29.md](docs/reviews/tsmom_jpy-2026-05-29.md) ·
[docs/reviews/tsmom-multiasset-2026-05-30.md](docs/reviews/tsmom-multiasset-2026-05-30.md)

---

## 2026-05-24 — Quant Reviewer come gate decisionale

**Decisione.** Le decisioni promuovi/scarta strategia passano da una **quant-review formale**
(`/quant-review`), non da impressioni. Pipeline: dati live → quant review → modifica codice.

**Razionale.** Dopo 2 settimane live (London: 2 trade; Confluence: 0 trade per attrito operativo)
serviva un metro statistico (PBO, DSR, walk-forward, MC permutation).

→ [agents/quant_reviewer.md](agents/quant_reviewer.md) · [core/quant_metrics.py](core/quant_metrics.py) ·
[docs/QUANT_REVIEW_PROTOCOL.md](docs/QUANT_REVIEW_PROTOCOL.md)

---

## 2026-05-24 — Confluence manuale → opportunistica

**Decisione.** La Confluence **manuale** (weekend planning + `levels.yaml`) è **opportunistica**:
nessun obbligo settimanale. L'energia è sull'**automazione** (`confluence_auto/` shadow run).

**Razionale.** L'attrito operativo del planning weekend produceva 0 trade. Meglio investire
sull'estrazione algoritmica dei livelli e raccogliere dati di confronto manuale vs algoritmico.

→ Concetti: [TRADING_PRINCIPLES.md](TRADING_PRINCIPLES.md) · [strategies/confluence_auto/](strategies/confluence_auto/)
(il vecchio `WEEKEND_CHECKLIST.md` — procedura manuale livelli→`levels.yaml`→VPS — è stato eliminato il 2026-06-14)

---

## 2026-05-05 — Pivot architetturale (ibrido Python/MQL5, 3 componenti)

**Decisione.** Architettura ibrida a **3 componenti indipendenti, 3 habitat, zero bridge**:
1. **Confluence Levels** (Python) — solo notifica — VPS Linux Hetzner.
2. **Expert Advisor MQL5** (es. London Breakout, archiviato) — esecuzione automatica — MetaQuotes VPS.
3. **Stock Selector** (Python) — tool offline — PC di casa.

**Razionale.** Disaccoppiare deployment e failure mode; niente VPS Windows/RDP; niente sync
Python↔MQL5. Sostituisce il piano monolitico pre-pivot.

→ Architettura: [docs/ARCHITECTURE_v2.md](docs/ARCHITECTURE_v2.md) ·
Operatività: [docs/OPERATIONAL_GUIDE.md](docs/OPERATIONAL_GUIDE.md) ·
Doc storico pre-pivot: [docs/STAGE2_TESTING_PLAN.md](docs/STAGE2_TESTING_PLAN.md)

---

## Principio trasversale — Edge condizionato alla strategia

Nessuna fase di mercato è tradabile/non-tradabile **in assoluto**: l'edge è condizionato alla
strategia + regime. Il backtest da solo **non basta** — triangolare con razionale economico e
walk-forward. Vedi [fondamenti_tecnici/03_regimi_macro/](fondamenti_tecnici/03_regimi_macro/) e
[fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/).

---

## Principio trasversale — Mappa dei modelli (gestione dei conflitti tra teorie)

I mercati non sono scienza esatta: **non esiste l'equazione madre** che spiega/predice tutto.
Quando due fonti o teorie si contraddicono, il nostro compito **NON è eleggere un vincitore
universale** ("X è più giusto di Y"). Si registra **ogni modello con le sue CONDIZIONI di
validità** e si rende il conflitto **esplicito**, così la decisione operativa sceglie il modello
che calza il contesto. È l'estensione naturale del principio "edge condizionato" qui sopra.

**Model card minima** per ogni claim in conflitto:
`{ claim · fonte · condizioni (regime/asset/timeframe/assunzioni) · contraddice · stato (attivo/reference/parcheggiato) }`

**Esempi svolti** (i due conflitti già emersi nel materiale):
- *"Il backtest è inutile / è overfitting"* (Roan, Quant Guild) **vs** *"misura con DSR/PBO/
  walk-forward"* (López de Prado, nostro quant). **Non** è una contraddizione: vale separando
  *non curve-fittare una regola di timing* (vero) da *non misurare distribuzioni / non falsificare*
  (falso). Condizione: il backtest serve a **falsificare e misurare proprietà distributive**, non
  a *scoprire* la regola.
- *"Vendi il volatility risk premium"* (IV sovrastima RV in media) **vs** *"compra convexity /
  long-vol"* (mitiga il drag nei crash). Entrambe vere secondo **regime/timing**: vendi il premio
  in mercato normale, l'assicurazione paga nei tail.
- *"Il rischio forward non è misurabile con modelli e dati storici: vince la profondità
  qualitativa/esperienza"* (fonte: appunti 2026-08-04, blocco risk-mispricing) **vs** la nostra
  **pre-registrazione + gate statistici**. Si separa per **dominio**, non per merito:
  la fonte parla di **scommesse discrezionali concentrate** su singola entità ($n=1$, nessun
  campione disponibile, l'edge *è* la profondità informativa); noi facciamo **regole sistematiche
  ripetibili** su strumenti liquidi (il campione esiste, il fallimento dominante è l'overfitting).
  **Condizione operativa: il qualitativo genera ipotesi ed enumera direzioni di rischio — non
  valida mai.** Nessun ragionamento qualitativo promuove una strategia bocciata dai gate; nessun
  "aggiornamento bayesiano" sugli stessi dati già usati per il test. Il tassello **utile** della
  fonte (pre-mortem sulle direzioni principali di rischio) è distillato in
  [fondamenti_tecnici/04_quant_metodologia/](fondamenti_tecnici/04_quant_metodologia/) §9 — copre
  proprio ciò che il backtest non può interrogare (key-man, compliance, rottura tecnica).

Operativamente la mappa vive in due posti: il **registro di intake**
([fondamenti_tecnici/_INTAKE.md](fondamenti_tecnici/_INTAKE.md)) traccia stato e destinazione di
ogni fonte; le **condizioni di validità** stanno accanto al concetto nel file `fondamenti_tecnici/`
che lo ospita, con cross-link al claim opposto. Regola epistemica di base: §0 di
[agents/quant_reviewer.md](agents/quant_reviewer.md) (il gioco, non i giocatori).
