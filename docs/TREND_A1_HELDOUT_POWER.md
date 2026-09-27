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
