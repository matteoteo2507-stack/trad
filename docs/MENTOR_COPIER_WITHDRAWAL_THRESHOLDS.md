# Soglie di ritiro del copier mentore — dichiarate **prima** del capitale

> **Documento vincolante.** Fissato il **2026-09-18**, con il copier **non ancora operativo**
> (il deploy su VPS del 2026-09-15 non era andato a buon fine). Questo e' il momento giusto: le
> soglie vanno dichiarate **prima** che entri il capitale, altrimenti si finisce per spegnere la
> strategia dopo un drawdown — cioe' al minimo — e riaccenderla dopo il recupero.
>
> Richiesto da [`STRATEGY_LIFECYCLE.md`](STRATEGY_LIFECYCLE.md) **§8bis**. Colma la voce **C3** del
> [backlog](BACKLOG_RICERCA.md).
>
> Motore: [`analysis/mentor_signals/withdrawal_thresholds.py`](../analysis/mentor_signals/withdrawal_thresholds.py).

---

## 1. Di cosa stiamo fissando le soglie

Il copia-segnali del mentore su **XAUUSD**, uscita a **TP1**, scenario pessimistico, costi inclusi
($0,30 round-trip). E' l'**unico binario del workspace con un verdetto positivo pre-registrato**
([`MENTOR_SIGNALS_OOS_PREREGISTRATION.md`](MENTOR_SIGNALS_OOS_PREREGISTRATION.md), 2026-08-07:
win-rate 63,0% contro 35,0% del lato casuale, E[R] **+0,194** BCa95 [+0,079 ; +0,289]).

**Profilo del rendimento**, su 477 trade in 101 giorni (2026-01-22 → 2026-06-12):

| | |
|---|---|
| E[R] | **+0,2025** |
| deviazione standard | 0,571 |
| vincenti | **82,6%** |
| payoff | **+0,46** contro **−1,03** |

⚠️ **Questo profilo e' il motivo per cui le soglie servono davvero.** Un win rate dell'82,6% con un
payoff di 1:0,45 significa che **l'equity sale quasi sempre e scende di colpo**: servono **2,2
vincite per recuperare una perdita**. Una serie sfortunata non "si vede arrivare", e la tentazione di
spegnere nel mezzo e' massima proprio quando statisticamente non andrebbe fatto.

---

## 2. Il problema che ha cambiato i numeri: **gli esiti non sono indipendenti**

Il Monte Carlo standard **rimescola i trade**, e cosi' facendo assume che siano indipendenti.
Qui non lo sono:

| diagnostica | valore | lettura |
|---|---|---|
| runs test sulla serie vinta/persa | **z = −3,37** | raggruppamento netto |
| autocorrelazione dei rendimenti, lag 1 | **+0,136** | |
| autocorrelazione, lag 10 | +0,085 | persiste a lungo |
| segnali al giorno | **4,7** (max 9) | stesso strumento, stessa sessione |

Il meccanismo e' ovvio a posteriori: **quando la lettura del mentore e' sbagliata, sbaglia per tutta
la sessione**. Le perdite arrivano in grappoli.

**Conseguenza sui numeri**: il rimescolamento distrugge proprio il raggruppamento che genera i
drawdown profondi.

| simulazione (95° percentile, 20.000 percorsi) | maxDD | serie negativa |
|---|---|---|
| **i.i.d.** — rimescola i singoli trade | **6,84 ± 0,06 R** | 4,88 ± 0,35 |
| **a blocchi** — ricampiona **giorni interi** | **12,15 ± 0,12 R** | 5,38 ± 0,52 |

> 🔧 **L'ipotesi di indipendenza valeva 5,31R, cioe' il 78% di drawdown in meno.** Con il metodo
> standard avremmo fissato la soglia a **6,8R** e ritirato il copier durante un drawdown che gli
> capita **normalmente una volta su venti**. E' il buco 29 del distillamento Quant Guild (test di
> indipendenza degli esiti), applicato — e da solo ha quasi raddoppiato la soglia.

Gli **errori standard** sono riportati perche' un percentile e' una stima: 12,15 ± 0,12 e' un numero,
"12,15" da solo non lo e' (buco 37 dello stesso distillamento).

---

## 3. Sensibilita': e se il vero E[R] fosse al limite inferiore?

L'intervallo OOS su E[R] e' [+0,079 ; +0,289]. Rifacendo la simulazione a blocchi con E[R] portato a
**+0,079**:

| | maxDD 95° | serie negativa 95° |
|---|---|---|
| E[R] = +0,203 (stima puntuale) | 12,15 ± 0,12 R | 5,38 |
| **E[R] = +0,079 (limite inferiore OOS)** | **20,11 ± 0,33 R** | 5,38 |

Cioe': **se il vantaggio reale e' nella parte bassa dell'intervallo, drawdown da 20R sono normali.**
La scelta della soglia deve dire esplicitamente cosa si accetta di sbagliare.

---

## 4. Le soglie — **dichiarate ora**

| soglia | valore | da dove viene |
|---|---|---|
| **DD di ritiro** | **12 R** | 95° percentile del maxDD, ricampionamento a blocchi |
| **Serie negativa di ritiro** | **6 perdite consecutive** | 95° percentile (5,38 ± 0,52), arrotondato in alto |
| **Finestra minima di valutazione** | **62 trade** (~13 giorni) | potenza 80%, α 0,05, per distinguere E[R] attuale da zero |

**Perche' 12R e non 20R.** La soglia non manda la strategia in pensione: la manda in **INCUBAZIONE**,
dove continua a girare in simulazione e a raccogliere dati. Un falso allarme costa **poco ed e'
reversibile**; una soglia troppo larga fa bruciare capitale vero mentre si aspetta. Si accetta
quindi che, **se il vero E[R] fosse +0,079, questa soglia scattera' piu' spesso del 5%** — e va bene
cosi', perche' la conseguenza e' guardare, non chiudere.

**Perche' una finestra minima.** Sotto i 62 trade non si valuta **affatto**: nemmeno per dire "sta
andando bene". Con 4,7 trade al giorno sono circa **13 giorni**, quindi il vincolo non e' oneroso.

⚠️ **Nota sulla potenza, che qui e' una buona notizia.** Distinguere un degrado di **0,05R**
richiederebbe **1.022 trade (~216 giorni)**: i degradi *piccoli* restano invisibili a lungo. Ma il
degrado che conta — **da +0,20 a zero** — si vede in **62 trade**. Contrasto col FADE, dove servivano
oltre 1.000 trade anche per la domanda grossa: qui la deviazione standard e' **0,571R** invece di
1,8R, ed e' questo che rende il binario governabile.

---

## 5. Macchina a stati e criterio di rientro — anch'esso dichiarato ora

```
   LIVE ──(DD > 12R  oppure  6 perdite consecutive)──► INCUBAZIONE
     │                                                      │
     │                                            (criterio di rientro)
     │                                                      ▼
     │                                                    LIVE
     │                                                      │
     │                                      (seconda uscita) ▼
     └──(razionale falsificato / difetto)──────────────► RITIRATA
```

- **INCUBAZIONE**: il copier continua a girare **in simulazione**, con le **stesse identiche regole**.
  Non si ritara nulla: ritarare su dati che includono il periodo negativo e' p-hacking col capitale
  gia' in gioco (§4 + §8bis).
- **Criterio di rientro, dichiarato ora**: si torna LIVE quando, **in simulazione**, la curva
  **recupera il picco precedente all'ingresso in incubazione** *e* sono stati accumulati almeno
  **62 trade** dall'ingresso. Entrambe le condizioni, non una.
- **Seconda uscita dalla distribuzione dopo un rientro → RITIRATA definitiva.** Due fallimenti
  indipendenti non sono sfortuna.
- **Ritiro immediato, senza incubazione**, se cade il razionale: key-man risk (il mentore smette,
  cambia stile o strumento), oppure un difetto metodologico conclamato nel nostro replay.

---

## 6. Limiti dichiarati

1. **Il campione e' in larga parte in campione.** I 477 trade coprono 2026-01-22 → 2026-06-12, cioe'
   il periodo da cui l'edge e' stato identificato; la validazione OOS (131 segnali) e' successiva ed
   e' su un export diverso. La sensibilita' del §3 e' il modo in cui questo e' stato parzialmente
   compensato, non una soluzione.
2. **Il replay non e' il copier.** Il replay assume il fill entro 6h dal prezzo di ingresso
   dichiarato; il copier reale avra' un ritardo proprio, e la **soglia anti-ritardo non e' ancora
   fissata** (voce **C5** del backlog, tuttora aperta). Se il ritardo reale degrada il fill, la
   distribuzione qui sopra e' ottimista.
3. **Un solo strumento, un solo mentore, cinque mesi.** Nessuna di queste soglie e' trasferibile a
   un'altra fonte di segnali.
4. Il rischio per trade con cui si converte R in percentuale di capitale **non e' fissato in questo
   documento**: con l'1% per trade, 12R valgono circa il 12% del capitale.

---

## 7. Registro

| data | evento |
|---|---|
| 2026-09-18 | documento creato **prima** del capitale, copier non ancora operativo. Soglie: DD 12R, serie 6, finestra 62 trade |
