# A5 — Audit dei verdetti early-stage: **referto** (2026-09-18)

> Protocollo e criteri: [EARLY_STAGE_AUDIT_PROTOCOL.md](EARLY_STAGE_AUDIT_PROTOCOL.md), scritto e
> committato **prima** di aprire i motori. **0 trial spesi.**

---

## Il risultato in una riga

**Nessun verdetto era sbagliato. Due erano piu' forti di quanto sapessimo, due dicevano meno di
quello che gli abbiamo fatto dire.**

Il difetto sistematico non sta nei test: sta nel **passaggio dal test al verdetto**. Le review
tecniche sono oneste e scrivono *"non distinguibile dal caso"* e *"INSUFFICIENT DATA"*. In
`DECISIONS.md` e in memoria le stesse cose diventano *"NO-GO pulito"*, *"null"*, *"l'edge non
esiste"* — e **su quelle formulazioni compresse abbiamo poi costruito**.

| famiglia | esito | cosa cambia |
|---|---|---|
| **Livelli** (384 trial) | ✅ **CONFERMATO** — piu' solido di quanto dichiarato | niente da riaprire; il NULL e' **molto** ben misurato |
| **NXT continuazione** | ✅ **CONFERMATO**, ma **numero sbagliato** | il vero E[R] e' **−0,118**, non −0,444 |
| **ORB** | 🟡 **MISTO** | SPX500 genuinamente negativo · **NAS100 mai refutato** |
| **TSMOM** | ⚠️ **NON MISURATO** | il test non poteva vedere l'effetto che cercava |

---

## 1. Livelli — ✅ CONFERMATO, ed e' il verdetto piu' solido che abbiamo

Rieseguito il motore per intero ([output](health/a5_level_research_rerun_2026-09-18.txt)). Riproduce
esattamente: **4 celle "battono" su 96 testate, contro 4,8 attese per puro caso.**

Controllo di **potenza**, che nessuno aveva fatto:

| concetto | reale | random | CI sulla differenza |
|---|---|---|---|
| swing | 29,0% | 29,8% | [−1,1 ; −0,6] pp |
| pdh_pdl | 28,8% | 30,5% | [−2,4 ; −1,2] pp |
| ob | 30,0% | 29,6% | [+0,0 ; +0,9] pp |
| fvg | 29,6% | 29,8% | [−0,5 ; +0,2] pp |
| round | 29,4% | 30,1% | [−1,1 ; −0,3] pp |
| eqh_eql | 29,2% | 30,2% | [−1,3 ; −0,6] pp |

**Gli intervalli sono larghi meno di un punto percentuale su una base del 30%.** Un effetto reale
anche di soli 2 punti sarebbe stato visto senza difficolta'. Questo **non** e' un null da campione
scarso: e' un null misurato bene.

Verificati anche, leggendo il codice: detection su barre **chiuse** prima del punto di decisione
(`P0 = h1[di-1]["close"]`, finestra `h1[di-H1_WINDOW:di]`), misura forward da `di` in poi
(**nessun look-ahead**), baseline random **distance-matched** dallo stesso pool per
(concetto, lato), stessa `classify`, stesso ATR, holdout temporale 70/30, correzione per
molteplicita'.

📋 Due difetti minori, **ininfluenti**: l'output non stampa la finestra dei dati (oggi lo
esigeremmo); il pool delle distanze per il random e' costruito su tutto lo split invece che
causalmente — e va nella direzione che rende il confronto **piu' severo** per la strategia, non
piu' facile.

> **Conclusione**: il libro sui livelli resta chiuso, e adesso sappiamo **quanto** e' chiuso.

---

## 2. NXT continuazione — ✅ CONFERMATO, con un numero da correggere

Il verdetto del 2026-07-17 (**E[R] = −0,44R**, negativa in 14/14 anni e 6/6 strumenti) e' stato
prodotto con lo **stesso fill fantasma** che il 2026-08-27 ha invalidato il FADE.

⚠️ **E qui l'artefatto spingeva nel verso pericoloso.** Fade e continuazione entrano allo **stesso
livello**: il fade **vende**, la continuazione **compra**. Concedere il fill a un livello gia'
oltrepassato **regala** un prezzo migliore a chi vende e **impone** un prezzo peggiore a chi compra.
Lo stesso difetto che gonfiava il fade **deprimeva** la continuazione — cioe' poteva **aver prodotto
lui** il NO-GO.

Rimisurata con i soli fill ottenibili
([`continuation_obtainable.py`](../analysis/nxt/continuation_obtainable.py),
[output](health/a5_nxt_continuazione_2026-09-18.txt)):

| | n | E[R] | BCa95 |
|---|---|---|---|
| col fill fantasma (il verdetto del 17/07) | 10.218 | **−0,444** | [−0,470 ; −0,417] |
| **solo fill ottenibili** (riferimento) | 5.506 | **−0,118** | **[−0,161 ; −0,076]** |
| solo fill ottenibili (ottimista) | 5.506 | −0,056 | [−0,099 ; −0,011] |

**Il difetto valeva +0,326R**: tre quarti dell'effetto dichiarato erano artefatto.
**Ma il verdetto sopravvive**: l'intervallo esclude lo zero in **entrambe** le convenzioni,
**0 strumenti su 6** positivi, **2 anni su 15**.

🔧 **Il fatto che vale piu' del verdetto stesso.** Misurate onestamente, **entrambe le direzioni
dello stesso ingresso perdono**: fade **−0,250**, continuazione **−0,118**. Non e' un edge con il
segno sbagliato: e' **un livello che non contiene informazione**, piu' costi. E' la stessa cosa che
dicono i 384 trial sui livelli, trovata da una strada completamente diversa.

**Da correggere ovunque**: "−0,44R, negativa in 14/14 anni" → **"−0,118R, negativa in 13/15 anni"**.

---

## 3. ORB — 🟡 MISTO: un lato refutato, l'altro mai misurato

### L'ipotesi che avevo, e che era sbagliata

`backtest_v2.py` calcola **due** colonne, `R_pess` e `R_opt` (ordine assunto degli eventi dentro la
barra M5), ma il verdetto stampa **solo la pessimistica**. Su un NO-GO e' il verso pericoloso: la
convenzione pessimistica deprime, e poteva aver prodotto lei il verdetto — come il 18/09 la stessa
forbice valeva **0,82R** sul baseline del copier.

Misurata ([`audit_convenzioni.py`](../analysis/opening_range/audit_convenzioni.py),
[output](health/a5_orb_convenzioni_2026-09-18.txt)): **la forbice e' +0,001R.** Praticamente nulla,
su ogni scomposizione e su entrambi gli strumenti. **Ipotesi mia, refutata.** Il motivo e'
strutturale: con RR 1:3 e stop ampio rispetto alla barra M5, le barre ambigue sono rare.

📋 Trovato e corretto un difetto reale in codice morto: `R_opt` assegnava **0.0** a un timeout invece
di scartarlo. Mai usato nel verdetto, quindi ininfluente — ma ora quella colonna la usiamo.

### Quello che invece c'e' davvero: la potenza

| | n | E[R] | BCa95 | sd | **MDE** |
|---|---|---|---|---|---|
| **NAS100** ADX≥25 | 1.195 | −0,012 | [−0,100 ; **+0,078**] | 1,670 | **0,135** |
| NAS100 TRAIN '12-'19 | 621 | −0,076 | [−0,194 ; **+0,058**] | 1,651 | 0,185 |
| NAS100 TEST '20-'26 | 574 | +0,057 | [−0,073 ; **+0,203**] | 1,689 | 0,197 |
| **SPX500** ADX≥25 | 1.094 | −0,094 | [−0,192 ; +0,001] | 1,668 | 0,141 |
| **SPX500 TRAIN '12-'19** | 525 | **−0,267** | **[−0,391 ; −0,121]** | 1,575 | 0,192 |
| SPX500 TEST '20-'26 | 569 | +0,066 | [−0,072 ; +0,214] | 1,736 | 0,204 |

**SPX500 e' genuinamente negativo** sul campione lungo: l'intervallo esclude lo zero con margine.
Quel verdetto regge.

**NAS100 non e' mai stato refutato.** Ogni singolo intervallo **contiene lo zero** e arriva fino a
**+0,078** / **+0,203** — cioe' dentro territorio perfettamente tradabile. L'MDE dice la stessa cosa
dall'altro lato: il campione poteva vedere solo effetti da **0,135R in su**.

E il criterio pre-registrato era: *"si passa a v2 se E[R] > 0 con BCa lower-bound > 0"* — un criterio
che puo' produrre **solo** "dimostrato" o "non dimostrato". Un "non dimostrato" e' finito in
`DECISIONS.md` come **NO-GO**, cioe' come refutazione, e da li' come *"anche il filone scalping
single-asset, testato bene, e' null"* — generalizzando da uno strumento su due.

> **Correzione**: il NO-GO ORB vale per **SPX500**. Su **NAS100** la casella e' **vuota, non chiusa**.
> ⚠️ Questo **non** autorizza a rifarlo: l'holdout della famiglia e' **gia' stato aperto** (A3), e il
> protocollo dice che un "non misurato" non regala un trial.

---

## 4. TSMOM — ⚠️ NON MISURATO

Il verdetto del 2026-07-08: Sharpe **+0,21**, **BCa95 [−0,18 ; +0,59]**, lower bound ≤ 0 → NO-GO per
regola pre-registrata. La review **cita nella stessa pagina** l'aspettativa a priori dalla
letteratura (Baltas-Kosowski, SG Trend): **Sharpe 0,3-0,5**.

Nessuno ha messo insieme le due righe. Fatto ora
([`a5_potenza_tsmom.py`](../analysis/ops/a5_potenza_tsmom.py),
[output](health/a5_potenza_tsmom_2026-09-18.txt)), con `SE(SR) ≈ sqrt((1+SR²/2)/T)`:

| Sharpe cercato | anni necessari | ne avevamo 23? |
|---|---|---|
| 0,20 | 200 | no — **9×** |
| **0,30** | **91** | no — **4×** |
| **0,40** | **53** | no — **2,3×** |
| **0,50** | 35 | no — 1,5× |
| 0,80 | 16 | si' |

**Effetto minimo rilevabile con 23 anni: Sharpe 0,59.** L'intervallo osservato arriva a **+0,59** e
**contiene per intero la fascia attesa dalla letteratura**.

> **Il test non ha escluso l'effetto che cercava: ha fallito nel dimostrarlo.** Sono due cose
> diverse. E' la stessa forma del difetto che il 2026-09-17 ha smontato il "secondo test" del FADE
> (fuori scala di 40×): una giustificazione plausibile, mai tradotta in un numero.
>
> ⚠️ Anche qui: **non** autorizza a riaprire. Autorizza a **smettere di citarlo come prova** che il
> momentum non funziona su questo universo. La casella e' vuota, e per riempirla servirebbero dati
> che **non possiamo avere** — 53 anni non esistono su questo universo.

---

## 5. Famiglie minori — passata rapida

| famiglia | lettura |
|---|---|
| **TSMOM USDJPY** (05-29) | ✅ **la review aveva gia' ragione**: verdetto *"NO-GO / INSUFFICIENT DATA"*, e scrive *"strutturalmente incapace di dimostrare (o negare) l'edge"*, n=38, l'intero P&L in **un solo trade**. Nessuna correzione |
| **London Breakout** (05-29/30) | ✅ **rafforzato**: il NO-GO nasce **togliendo** un look-ahead (label di regime same-day: Volatile da +1828 a +349 con lag 1g). Un difetto che **gonfiava**, rimosso correttamente |
| **Stagionalita' TOM** | 🟡 stima puntuale **negativa** (−0,28) e baseline proprio (finestre casuali, p=0,24) → difendibile. Ma il CI arriva a +0,13 e l'MDE e' ~0,59: *"assente"* e' piu' forte del misurato |
| **Mean-reversion vol** | 🟡 stessa forma: Sharpe −0,21, CI [−0,63 ; +0,21], 8/24 anni positivi. Puntuale negativo, quindi difendibile come *"nessuna evidenza"*, non come *"refutato"* |

---

## 6. Cosa cambia operativamente

1. **Correggere il numero NXT**: −0,118R (13/15 anni), non −0,44R (14/14). In `DECISIONS.md`,
   backlog e memoria.
2. **Declassare due verdetti da "refutato" a "non misurato"**: TSMOM, e ORB **limitatamente a
   NAS100**. Restano chiusi, ma **smettono di valere come prova** nel bilancio *"niente edge
   meccanico own robusto"*, che e' la frase su cui poggia il pivot al passivo.
3. **Rafforzare il verdetto sui livelli**: e' misurato meglio di quanto sapessimo, e la
   continuazione NXT lo **corrobora da una strada indipendente** (entrambe le direzioni dello
   stesso livello perdono).
4. **Regola nuova, generale**: un verdetto va scritto con la **stessa forza** del test che lo
   produce. Se il criterio era *"dimostra che > 0"*, il fallimento si scrive **"non dimostrato"** e
   si accompagna con l'**MDE**. `STRATEGY_LIFECYCLE` chiede gia' di dichiarare prima cosa significhera'
   un mancato rifiuto: **non lo stavamo facendo**.

## 7. Contabilita'

**0 trial spesi.** Nessuna famiglia riaperta, nessun holdout toccato, nessun parametro cercato.
Due verdetti declassati **non** ricevono un trial nuovo: tornano allo stato precedente col budget
residuo di allora.
