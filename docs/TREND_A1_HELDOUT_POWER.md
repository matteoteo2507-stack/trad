# A1 punto 2 — quanti strumenti servono, e Dukascopy li ha?

> Eseguito il **2026-09-21**, dopo che il [diagnostico di durata](TREND_DURATION_DIAGNOSTIC.md)
> ha lasciato in piedi il gradiente (esito dichiarato prima: *"A1 sopravvive → si passa al
> punto 2"*).
>
> **Costo: 0 trial.** È un calcolo di **potenza** e un **inventario**, non un test dell'ipotesi:
> nessuna regola, nessun parametro, nessun verdetto su A1. Motori:
> [`analysis/trend/power_two_groups.py`](../analysis/trend/power_two_groups.py) e
> [`analysis/trend/heldout_pool.py`](../analysis/trend/heldout_pool.py).
>
> Esiste per la regola nata dal FADE: *una ragione plausibile e non quantificata tiene in piedi
> lavoro inutile per mesi*. Il "secondo test" del FADE era **fuori scala di 40x**, e nessuno lo
> aveva calcolato prima di iniziare.

---

## 1. Il disegno di cui si calcola la potenza

Quello del punto 3, come formulato: **confronto a due gruppi su strumenti mai visti.**

| | scelta | perché |
|---|---|---|
| **bracci** | ALTA vs BASSA volatilità realizzata, soglia **20%** annualizzata | la volatilità è un **input**, misurabile sui nuovi strumenti senza guardarne l'esito: è ciò che rende il disegno pre-registrabile |
| **metrica primaria** | differenza appaiata *reale − random* a **durata controllata** | è il grezzo `E[R]` che conteneva il canale meccanico (§6.2 del diagnostico). Due varianti: durata **appaiata** e durata **fissa 20g** |
| **unità di inferenza** | lo **strumento**, non il trade | è lo strumento che viene tenuto fuori, e i trade dentro uno strumento condividono la stessa serie |

## 2. Perché non si contano i trade

| metrica | ICC fra strumenti | cluster medio | design effect |
|---|---|---|---|
| durata appaiata | 0,0217 | 43 trade | **1,92** |
| durata fissa 20g | 0,0113 | 43 trade | **1,48** |

Un ICC di **0,01–0,02** sembra trascurabile e non lo è: con cluster da 43 trade, i **1.169** trade
raccolti valgono **791** trade indipendenti. Contare i trade dà numeri comodi e sbagliati —
246 e 588 per braccio — e sono riportati nel motore solo per mostrare di quanto ingannano.

## 3. L'effetto e la dispersione, misurati

Media per-strumento della differenza, 27 strumenti, finestra 2017-12-26 → oggi, 9 anni:

| metrica | braccio BASSA (14 str.) | braccio ALTA (13 str.) | **Δ** | sd fra strumenti |
|---|---|---|---|---|
| durata **appaiata** | −0,501 | +0,109 | **+0,610 R** | 0,417 |
| durata **fissa 20g** | −0,758 | −0,113 | **+0,645 R** | 0,666 |

Strumenti per braccio, α 0,05 bilaterale e potenza 80% — `n = 2·(z+z)²·(sd/Δ)²`, fattore 7,849:

| effetto ipotizzato | durata appaiata | durata fissa 20g |
|---|---|---|
| **osservato** (ottimistico) | **7,3** | **16,7** |
| **dimezzato** (winner's curse) | **29,3** | **66,8** |
| un terzo | 65,9 | 150,4 |

⚠️ L'effetto osservato è stato **scoperto su questi stessi dati**: usarlo come effetto atteso è la
definizione del winner's curse. La riga di pianificazione onesta è quella **dimezzata**.

## 4. Il pool libero: misurato, non assunto

Dukascopy espone **1.380 strumenti**, ma quasi tutti azioni singole ed ETF. Fuori dall'azionario
il pool ancora **libero** (mai usato nella scoperta) è: 58 cross FX, 20 indici, 19 crypto,
1 agricolo (OJUICE), 1 energia (DIESEL). Bond, FX major e metalli sono **esauriti**.

**Disponibilità verificata scaricando davvero** (18 candidati su 19; `XMRUSD` non ha dati):
cross FX e indici dal 2012, DIESEL e OJUICE dal 2017-12, ma le crypto libere partono tardi —
LTC 2018-09, XRP 2018-05, **BCH 2021-05**, **ADA 2021-09** — e **EOS finisce nel 2025-06**.

### Il conto che conta: quanti ne *valgono*

`n_eff = n / (1 + (n−1)·ρ)`, con ρ **misurato** sui rendimenti D1 nella stessa finestra:

| insieme | ρ medio misurato | ticker liberi | **n_eff dei liberi** |
|---|---|---|---|
| **crypto** | **+0,698** | 19 | **1,40** |
| **indici** | **+0,791** | 20 | **1,25** |
| cross FX | **+0,050** | 58 | **15,07** |
| energia | +0,443 | 1 | 1,00 |
| agricoli | +0,099 | 1 | 1,00 |

E la volatilità misurata dice dove finiscono davvero: **nessun cross FX raggiunge il 20%** (il più
volatile è USDZAR a 13,0%), e degli indici solo NAS100 — che è già in-sample. DAX 17,8%, N225
19,7%, DJIND 16,5% stanno **sotto** la soglia.

| braccio | capacità effettiva in strumenti nuovi indipendenti |
|---|---|
| **ALTA volatilità** | **3,4** — crypto 1,40 + agricoli 1,00 + energia 1,00 |
| BASSA volatilità | 16,3 — cross FX 15,07 + indici 1,25 |

⚠️ È una stima **generosa**: somma categorie diverse come se fossero indipendenti fra loro e
ignora la correlazione incrociata.

## 5. Verdetto: la condizione **non è rispettata**

| scenario | servono per braccio | ALTA ne ha | esito |
|---|---|---|---|
| durata appaiata, effetto **osservato** | 7,3 | 3,4 | **fuori scala 2,1×** |
| durata fissa 20g, effetto osservato | 16,7 | 3,4 | fuori scala 4,9× |
| durata appaiata, effetto **dimezzato** | 29,3 | 3,4 | fuori scala 8,6× |
| durata fissa 20g, effetto dimezzato | 66,8 | 3,4 | **fuori scala 19,6×** |

**Anche lo scenario più ottimistico fallisce**, e quello di pianificazione onesta fallisce di un
ordine di grandezza. Il braccio a bassa volatilità sarebbe capiente (16,3); è il braccio **alto**
a non esistere.

**La ragione non è il numero di ticker** — Dukascopy ne ha in abbondanza. È che **l'estremo alto
della volatilità è una sola classe di attivi**: le 19 crypto libere si muovono insieme
(ρ = +0,698) e portano **1,4 strumenti** di informazione indipendente. Un test costruito così non
misurerebbe *"alta volatilità contro bassa volatilità"*: misurerebbe **"crypto contro cross FX"**,
cioè una differenza di classe di attivi — e la crypto è esattamente l'unico gruppo positivo nel
campione di scoperta. Sarebbe circolare **per costruzione**, non per sbadataggine.

## 6. Cosa NON risolve il problema

Tre vie d'uscita che sembrano disponibili e non lo sono:

1. **Abbassare la soglia** per far entrare indici ed EM nel braccio alto: fa entrare strumenti
   meno volatili, quindi **riduce Δ** e alza il fabbisogno. Non c'è pasto gratis.
2. **Usare una regressione continua** invece di due bracci: è più efficiente di uno split, ma il
   limite resta il numero di punti **indipendenti** sull'asse della volatilità — e sopra il 20%
   ce ne sono ~3 nuovi. La regressione sarebbe dominata da quei tre.
3. **Allungare la finestra** all'indietro: la crypto non esiste prima del 2017, ed è proprio il
   braccio che manca.

## 7. Cosa riaprirebbe la strada

Condizioni scritte **ora**, perché la prossima volta la risposta sia pronta:

- una **fonte dati con più classi ad alta volatilità** e storia lunga (futures su commodity
  minori, singole azioni ad alta vol, volatilità implicita) — cioè un feed diverso, non gli
  stessi dati riorganizzati;
- un **effetto più grande** misurato su un disegno che non sia questo (non la stessa tabella
  rivista);
- il **forward**: raccogliere nel tempo su strumenti nuovi non consuma holdout ed è l'unica fonte
  rinnovabile — ma a **4,8 trade per strumento-anno**, arrivare a ~30 strumenti indipendenti per
  braccio è una questione di anni, non di mesi.

⚠️ **Quello che non è una condizione di riapertura**: scegliere la crypto perché è l'unica casella
positiva. Dopo aver visto la tabella del §6.3 del diagnostico, è **eleggere un vincitore dalla
mappa** — e costerebbe il terzo e ultimo round del ramo trend.

---

## 8. Addendum 2026-10-03 — la condizione §7 contata gratis, prima di comprare

Richiesta di Matteo (03/10): verificare la riga G9 sul broker MT5 e fare il conteggio gratuito.
Motore: [`analysis/trend/heldout_pool_mt5.py`](../analysis/trend/heldout_pool_mt5.py)
(`--scarica`, `--azioni`, `--futures`). **0 trial**: inventario, nessun esito di strategia.
Stessa finestra (dal 2017-12-26), stessa soglia (20%), stessa formula `n/(1+(n−1)ρ)`.

**(a) Il broker FP Markets non e' una fonte di storia.** 764 simboli, 599 candidati nuovi, ma il
server demo conserva poco: azioni dal 2024-08, crypto e cereali dal 2022-02, metalli industriali
dal 2023-09 (verificato con richiesta esplicita dal 2005 e M1 del 2015: assenti). **Zero**
strumenti con storia nella finestra. Il broker serve per operare, la storia va presa altrove.

**(b) Azioni USA offerte da FP Markets, storia Dukascopy.** 432 titoli: 149 assenti su Dukascopy,
83 con storia corta, 200 con storia piena, di cui 33 esclusi per salti < −40% in un giorno (split
non rettificati sospetti). Dei 167 restanti, **165 sopra il 20%** (vol mediana 32,9%), ma
**ρ medio +0,323 → n_eff 3,1**, che e' anche il tetto `1/ρ`: aggiungere titoli non serve, si
muovono col mercato.

**(c) Futures pysystemtrade non in-sample (gratis, fermi al 2024-03-28).** 33 candidati, 7 con
storia corta (metalli LME, EUA, gomma, legname). **20 sopra il 20%** in 5 classi (cereali,
energia, metalli, soft, zootecnia), **ρ medio +0,112 → n_eff 6,4 tutto insieme** (10,7 sommando
per classe, generoso).

| braccio ALTA, strumenti nuovi indipendenti | n_eff | 7,3 (oss.) | 16,7 | **29,3 (dimezzato)** | 66,8 |
|---|---|---|---|---|---|
| referto §4 (Dukascopy) | 3,4 | ×2,1 | ×4,9 | ×8,6 | ×19,6 |
| futures 6,4 + crypto 1,4 | 7,8 | **OK** | ×2,1 | **×3,8** | ×8,6 |
| + azioni 3,1 (somma, ignora la correlazione fra classi) | 10,9 | OK | ×1,5 | ×2,7 | ×6,1 |

**Lettura.** Il feed G9 **sposta** il problema ma **non lo risolve**: lo scenario ottimistico
(effetto osservato, cioe' col winner's curse dentro) diventa finanziabile, quello di
pianificazione onesta resta fuori scala di **~3×**. Tre limiti in piu':
1. **pysystemtrade si ferma al 2024-03**: per un test serve il feed a pagamento (Pinnacle/Norgate,
   riga G9); questo conteggio dice solo cosa comprerebbe.
2. **Operabilita'**: dei 20 futures, su FP Markets ci sono solo mais e grano (e soft gia'
   in-sample). Un A1 positivo direbbe che il gradiente esiste, non che lo possiamo operare.
3. Il rendimento dei prezzi e' un **proxy** della correlazione della metrica (reale − random),
   come nel §4: puo' sbagliare in entrambe le direzioni.

**Decisione aperta (di Matteo):** comprare il feed vale solo se si accetta di pre-registrare A1
punto 3 sullo scenario **ottimistico**, dichiarando prima che un nullo sarebbe "non dimostrato".

---

## 9. Addendum 2026-10-25 — la finestra cambia il fabbisogno, non la conclusione

Richiesta di Matteo (25/10): prima di comprare Pinnacle (99 $, [ricerca dati](reviews/ricerca_dati_2026-10-25.md)),
vedere se bastano i futures gratuiti, che finiscono il **2024-03-28** (ultima riga dei CSV, verificata il 25/10).
Motore: [`analysis/trend/a1_potenza_finestra.py`](../analysis/trend/a1_potenza_finestra.py). **0 trial**: varianza
dal campione di scoperta (gia' usato il 21/09), sugli strumenti nuovi solo prezzi.

**Il punto di metodo.** La dispersione fra strumenti del §3 (0,417) e' quasi tutta **rumore dei pochi trade**: la
differenza vera fra strumenti pesa lo **0,8%** della varianza per trade (0,6% a durata fissa). Con piu' anni per
strumento il rumore scende e servono meno strumenti; con meno anni ne servono di piu'. Il modello ricostruisce la
dispersione osservata (0,431 contro 0,417): la riga A ridà il §3 con un margine del 4% in eccesso (7,6 contro 7,3).

Strumenti per braccio (α 0,05, potenza 80%), 4,8 trade per strumento-anno; disponibilita' = futures pysystemtrade
non in-sample con storia piena nella finestra, braccio ALTA (≥ 20%), n_eff tutto insieme (somma per classe):

| finestra | anni | appaiata, osservato | appaiata, **dimezzato** | fissa 20g, osservato | fissa 20g, dimezzato | ALTA disponibile |
|---|---|---|---|---|---|---|
| A — scoperta, o Pinnacle fino a oggi | 9,0 | 7,6 | 30,4 | 17,3 | 69,3 | §8: 7,8-10,9 con crypto e azioni |
| B — gratis, dal 2017-12-26 | 6,3 | 10,1 | 40,5 | 23,3 | 93,3 | 6,4 (10,7); + crypto 1,4 e azioni 3,1 |
| C — gratis, dal 2010 | 14,2 | **5,5** | 22,1 | 12,3 | 49,3 | **5,9** (9,8) |
| D — gratis, dal 2000 | 24,2 | **4,0** | 16,1 | 8,8 | 35,0 | **4,2** (6,5) |
| E — gratis, dal 1990 | 34,2 | **3,4** | 13,6 | 7,3 | 29,1 | **4,0** (5,5) |
| limite, infiniti trade | — | 1,9 | **7,6** | 3,7 | 14,8 | — |

**Lettura.**
1. **Lo scenario ottimistico** (durata appaiata, effetto osservato) **e' finanziabile con i dati gratuiti**, allungando
   la finestra all'indietro (C, D, E), senza crypto ne' azioni. **Pinnacle non serve per questo scenario.**
2. **Lo scenario di pianificazione onesta resta fuori scala in ogni finestra**, gratuita o comprata: di 2,3-3,8 volte.
   Anche con infiniti trade servirebbero **7,6** strumenti indipendenti ad alta volatilita' per braccio, e quelli
   nuovi che esistono ne valgono 4-6. **Nessun acquisto di dati lo risolve**: il limite e' quanti strumenti volatili e
   indipendenti esistono, non quanti anni di storia hanno.
3. Il braccio BASSA nel motore conta solo le commodity (2-4 n_eff nelle finestre lunghe), ma pysystemtrade ha
   obbligazioni di paesi mai usati (BTP, OAT, JGB, Corea, Canada), cambi emergenti e futures settoriali: il braccio
   basso si riempie, **il collo di bottiglia resta quello alto**.

**Ipotesi del conto, da leggere col risultato.** (a) Effetto e componenti di varianza misurati nel 2017-2026 valgono
anche negli anni '90 e 2000: il trend following ha avuto decenni molto diversi, e una finestra lunga e' un'estrapolazione
nel tempo oltre che negli strumenti. (b) Il rendimento giornaliero e' un proxy della correlazione della metrica (§4).
(c) La soglia del 20% si misura sulla finestra del test: in finestre diverse cambiano gli strumenti nel braccio
(20 nella B, 10 nella E).

**Operabilita', invariata dal §8:** dei futures contati, sul broker attuale ci sono solo mais e grano. Un esito
positivo direbbe che il gradiente esiste, non che lo possiamo operare.

**Decisione aperta (Matteo), ora con un'alternativa gratuita:** (a) pre-registrare A1 punto 3 sullo scenario
**ottimistico**, su futures gratuiti in una finestra lunga, dichiarando prima che un nullo vale "non dimostrato" (MDE
accanto): costa l'ultimo round di `trend_momentum`; (b) dichiarare la famiglia chiusa per potenza sullo scenario onesto,
che nessun dato raggiunge. In entrambi i casi **non si compra niente** per A1.

✅ **Deciso il 25/10 (Matteo): strada (b).** Famiglia `trend_momentum` CLOSED per potenza, D4 compresa (DECISIONS
2026-10-25 (5)).
