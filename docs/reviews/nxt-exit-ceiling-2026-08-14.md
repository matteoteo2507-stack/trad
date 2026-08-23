# NXT — soffitto dell'uscita: **KILL**. La struttura d'entrata è peggio del random.

**Data**: 2026-08-14 · **Verdetto**: **NO-GO / kill duro n. 2 e n. 3**
**Pre-registrazione**: [NXT_EXIT_CEILING_ADDENDUM.md](../NXT_EXIT_CEILING_ADDENDUM.md) (scritta prima dell'esecuzione)
**Motore**: [`analysis/nxt/excursion.py`](../../analysis/nxt/excursion.py) · output `analysis/nxt/excursion_report.txt`

---

## Domanda

Idea dell'utente: stessa meccanica NXT (pivot confermato a *k* barre, ordine limite a distanza fissa
dall'estremo, stop sotto l'estremo) ma **senza TP**, tenendo aperto fino a un'uscita a coda aperta
(incrocio di medie mobili) — per catturare pochi trade a grande RR.

L'entrata è già implementata e pre-registrata; l'unico elemento nuovo è l'uscita. Quindi: **esiste una
qualunque uscita che riporti E[R] sopra zero, o la coda destra è troppo magra?** Si misura il
**soffitto** (MFE = limite superiore invalicabile di qualsiasi exit rule), non una regola specifica.

## Campione

10.290 setup riempiti, 6 asset H1, 2012-2026 (15 anni). Entrata primaria `entry_fib = 0.5`, stop
grezzo al 78.6%, **niente TP e niente break-even**, `MAX_HOLD` 20 giorni di borsa. Bound pessimistico
intrabar, costi per asset sottratti in R.

## Esito

### Le soglie dichiarate passano — e non contano niente

| | valore | soglia dichiarata | esito |
|---|---|---|---|
| **S1** E[R] oracolo (esce sempre al massimo) | **+1,709R** · CI95 [+1,610, +1,816] | > 0 | passa |
| **S2** E[MFE \| MFE ≥ 3R] | **+10,10R** | > 6,5R | passa |
| **S3** breadth su S1+S2 | 6/6 asset, 15/15 anni | maggioranza | passa |

**Le soglie erano mal calibrate e vanno dichiarate tali.** Il rischio per trade è
`0,286 × ampiezza della gamba`, con gamba ≥ 1 ATR(H1) → uno stop di ~0,3 ATR orari, tenuto fino a
20 giorni. Su quella scala il prezzo percorre meccanicamente decine di ATR: una MFE di 10R vale
~2,9 ATR(H1) in 20 giorni, cioè nulla di notevole. **S1 e S2 sono quasi garantite per costruzione
per qualunque geometria a stop stretto e holding lungo** — non hanno potere discriminante.
L'errore è di chi ha scritto l'addendum, non del test.

### Il baseline random ribalta il verdetto

Controllo aggiunto **dopo** aver visto S1-S3, e legittimo perché può solo **alzare** l'asticella
([STRATEGY_LIFECYCLE §3](../STRATEGY_LIFECYCLE.md), riga "modellazione più realistica"): per ogni
setup reale, 3 controlli con **stesso asset, stesso lato, stesso rischio in unità di prezzo, stesso
anno**, ma entrata a un **istante casuale**. Isola esattamente ciò che la struttura (pivot + gamba
impulsiva + ritracciamento al 50%) aggiunge rispetto a "stop stretto tenuto 20 giorni".

| | reale | random matched | differenza | CI95 cluster |
|---|---|---|---|---|
| **E[R] oracolo** | +1,709 | **+3,149** | **−1,440** | **[−1,569, −1,314]** |
| **R terminale** (tenere fino a stop/scadenza) | −0,405 | **−0,005** | **−0,399** | **[−0,493, −0,308]** |
| P(MFE ≥ 3R) | 16,24% | **24,72%** | −8,5 pt | — |
| E[MFE \| ≥ 3R] | +10,10 | +11,06 | −0,96 | — |
| stop-out | 95,4% | 92,7% | +2,7 pt | — |

**Breadth del confronto: 0/6 asset e 0/15 anni** in cui il reale batte il random. Ogni CI per asset
esclude lo zero dal lato sbagliato (da −1,15 su USDJPY a −1,66 su US100).

## Lettura

1. **Il soffitto della struttura è più basso del soffitto del caso.** Non "l'edge è debole": entrare
   sul ritracciamento al 50% di una gamba impulsiva è **peggio** che entrare a un istante a caso, con
   lo stesso stop e lo stesso lato. Kill duro **n. 2** (non batte il baseline random matched) —
   stesso modo di morte della ricerca livelli, dove PDH/PDL venivano rotti *più* del caso.
2. **Nessuna uscita può salvarla.** L'oracolo con preveggenza perfetta è il tetto di ogni exit rule
   possibile, medie mobili incluse. Se il tetto del reale sta 1,44R sotto il tetto del random, non
   esiste regola d'uscita che inverta l'ordine: si sta ottimizzando dentro uno spazio più povero di
   quello di partenza.
3. **Il random terminale è ≈ 0 (−0,005R), il reale è −0,405R.** Una scommessa a caso con stop
   simmetrico e scadenza rende zero al netto dei costi, come deve essere. La struttura d'entrata
   **distrugge ~0,4R** rispetto alla moneta. È alpha negativo misurato, non assenza di alpha.
4. **Converge con il fade.** Il NO-GO del 2026-07-17 aveva trovato che *invertire* la stessa entrata
   rendeva +0,35R. Due misure indipendenti dicono la stessa cosa: a questo orizzonte, dopo il
   ritracciamento il prezzo tende a **proseguire nella direzione del ritracciamento**, non a
   riprendere l'impulso.
5. **Kill duro n. 3** (breadth) in aggiunta: 0/6 e 0/15, senza una singola cella favorevole.

## Contabilità

**Nessun trial consumato**: rianalisi descrittiva di un test già concluso con verdetto NO-GO, nessuna
regola pre-registrata modificata, holdout non aperto. La famiglia NXT conserva formalmente il suo
round 3 — ma non c'è nulla su cui spenderlo in questa direzione.

## Cosa NON è stato falsificato

Il test copre H1 con pivot frattale k=5, entrata al 50%, 6 asset. **Non** copre la variante a scala
di sessione su M5 proposta dall'utente (esempio: minimo della sessione di Londra). Ma spostarsi lì
sarebbe **shopping di timeframe** ([§4](../STRATEGY_LIFECYCLE.md)) — modifica motivata dall'esito —
e costerebbe l'ultimo round della famiglia. Contro: il fallimento non è marginale (−1,44R sul
soffitto, 0/6, 0/15) e il meccanismo di morte è già stato misurato **due volte su scale diverse**
(NXT continuazione su H1; estremi di periodo su H4/D1/W1 nella ricerca livelli, null o negativi).

## Cosa resta in piedi dell'idea originale

L'uscita a coda aperta **non è stata falsificata in sé** — è stato falsificato l'accoppiamento con
questa entrata. Una tesi "lascia correre" ha ancora senso *sopra un'entrata che almeno pareggia il
random*. Ad oggi, in questo workspace, non ne esiste una: è precisamente ciò che i 384 trial sui
livelli e i tre NO-GO sistematici hanno stabilito.
