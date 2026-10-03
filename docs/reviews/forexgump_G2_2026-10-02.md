# Forex Gump — revisione G2 del quant-gatekeeper (2026-10-02)

Oggetto: esito dell'esecuzione unica del 02/10 ([referto](forexgump_esito_2026-10-02.md)) contro la
[pre-registrazione APPROVATA](../FOREXGUMP_LATENCY_PREREGISTRATION.md). Nessun file modificato, `esegui_test.py`
non rilanciato. Verifiche a mano solo su **prezzi contro entrate postate** (nessun esito calcolato), script nella
scratchpad della sessione.

Il verdetto non lo emette il guardiano: le proposte di testo in fondo sono **da confermare da Matteo**.

```
VERDETTO DEL GUARDIANO: PASSA CON RISERVE
```

## BLOCCANTI (0)

Nessuno. Il verdetto meccanico segue la tabella, lo Step 3bis e' riportato, il baseline appaiato e i controlli
ci sono, i CI sono a cluster, l'MDE sta accanto al verdetto, i kill sui dati non scattano.

## Risposte ai sette punti

### 1. Il verdetto meccanico segue il §6? Si', ed e' scritto con la forza del test

- Il codice applica la tabella alla lettera: `esegui_test.py:269-277`. LB_d = −0,082 ≤ 0 → caso 4
  (`FOREXGUMP_LATENCY_PREREGISTRATION.md:203`). E ed E_s non entrano nel caso 4, e il codice non li usa.
- L'etichetta usa l'MDE **pre-registrato** (`esegui_test.py:56`, 0,130R), con quello osservato accanto (0,109R):
  referto righe 32-34. "Refutato" non compare da nessuna parte.
- Riserva minore (R2): il §6 (riga 196) chiede CI **ed MDE** sia di d sia di E accanto al verdetto. L'MDE
  pre-registrato di E[R] (0,171R, riga 212) non e' stampato; c'e' solo quello osservato (0,132R, referto riga 17).
  Va aggiunto nel testo della voce DECISIONS, non serve rieseguire nulla.

### 2. Il CI di d esclude un vantaggio sopra ~+0,07R? Si', ma come descrittiva, e attenti alla scala

Cosa si puo' dire onestamente:
- **Scala.** d = (R_mentore − R_opposto)/2 (`replay.py:291`). Il CI [−0,082; +0,069] su d vale
  **[−0,164; +0,138]R** sul divario mentore − lato opposto. Chi legge "+0,07R" deve sapere che e' una mezza differenza.
- **Cosa esclude.** Con un CI percentile al 95% a due code, valori di d sopra +0,069 sono poco compatibili con i
  dati (2,5% a una coda) **sotto questa esecuzione** (L = 10 s, bracket ricentrato). E' una lettura del CI, **non**
  un test di equivalenza: nessun margine d'equivalenza e' stato pre-registrato (il §6, righe 214-215, dice solo
  "esclude effetti sopra l'MDE"). Quindi: "non dimostrato; il CI rende poco plausibile un vantaggio direzionale
  sopra ~0,07R di d" va bene come **frase accanto**, non come secondo verdetto.
- **Direzione dei bias.** I bias del §8.2-8.3 (cancellazioni, modifiche: righe 238-241) spingono d **verso
  l'alto**: il limite superiore e' quindi, se mai, conservativo.
- **Cosa d NON misura.** d misura l'informazione direzionale **dopo t + 10 s**. Non dice nulla sul mentore prima
  del messaggio (vedi punto 4: al messaggio il prezzo si e' gia' mosso a suo favore). "Il segnale copiato non porta
  direzione rilevabile" si'; "il mentore non ha abilita'" no (§9, riga 264).

### 3. "Copiato a L = 10 s il segnale perde": si', come affermazione separata e condizionata

E' legittima perche' il §6 (riga 196) pre-registra il CI di E accanto a ogni verdetto, e il CI e' tutto negativo:
**−0,342 [−0,431; −0,248]** base, **−0,636 [−0,713; −0,555]** sotto stress (referto righe 17-18). Condizioni da
scrivere accanto:
- **Cosa la produce.** La perdita e' il **costo**, non un'abilita' negativa: d ≈ 0, e il lato casuale a parita' di
  ora perde quasi lo stesso (−0,264 [−0,328; −0,196] contro −0,298 del mentore rifatto su M1, divario −0,040
  [−0,148; +0,075], referto righe 45-47). Spread Dukascopy 0,17-0,35R a trade con SL 2 $ (§8.7, righe 245-248).
- **E' robusta all'incertezza su d.** Anche al limite superiore di d (+0,069) il lato del mentore resterebbe
  sotto zero di circa 0,27R: non c'e' un d compatibile coi dati che paghi lo spread.
- **Bias del §8.** Cancellazioni e modifiche spingono **verso l'alto**: rispetto a quei bias l'E[R] negativo e'
  **conservativo** (il vero, se diverso, e' piu' basso). La convenzione pessimistica spinge verso il basso, ma conta
  poco: holding mediano 0,17 h (referto riga 58), quindi la maggior parte delle uscite si risolve sui tick della
  prima ora, dove pareggi intrabar non esistono; d ottimistica coincide (−0,006 contro −0,007).
- **Spread del broker** (§8.7): non e' quello di Dukascopy. Meta' spread da' −0,193 (descrittiva, riga 80); nei 4
  trade live il broker riempiva 0,09-0,12 $ meglio di Dukascopy
  ([gump_live_rr_qualitativo_2026-09-29.md](gump_live_rr_qualitativo_2026-09-29.md) righe 35-36). Solo a spread
  ~zero E tornerebbe ≈ d ≈ 0: **non positivo** in nessuno scenario di costo realistico.
- **Perimetro.** Vale per **questo** copier: bracket puro ricentrato, nessuna gestione (BE, scarichi), tutte le
  categorie, nessuna deduplica (§3-§4). Le configurazioni live 8-8 e 10-7 e la gestione "BE" del mentore non sono
  state testate, ne' in un senso ne' nell'altro.

Testo onesto: *"Copiato come lo esegue il copier (L = 10 s, bracket ricentrato), il segnale ha E[R] −0,342R
[−0,431; −0,248]: perde quanto costa transare, senza direzione rilevabile che lo compensi."*

### 4. Step 3bis: il 99,6% e' un fatto, non un artefatto di fuso o di dati

Verificato sul codice e sui prezzi (solo entrate contro prezzo, nessun esito):
- **Codice.** `replay.py:192`: scarto = fill − entrata (buy, fill all'ASK) o entrata − fill (sell, fill al BID),
  con fill = ASK/BID reali nel caso base (`replay.py:185-187`, slittamento 0, k = 1). Coincide con la definizione
  del §5 (righe 167-169). Denominatore = trade eseguiti, come pre-registrato (`esegui_test.py:262`; le etichette
  SL/TP/TIMEOUT/BE sono quelle di `core/resolve_trade.py:87`).
- **Fuso.** La conversione sta solo in `carica.py:24,31-33` e `verifica()` (`carica.py:50-63`) si ferma sotto il
  95%. Un'ora di errore la farebbe crollare sotto il 23% (§3.1). La verifica pero' guarda una finestra di 5 minuti:
  **non** vede scostamenti di secondi o minuti. Per quelli ho controllato a parte.
- **Tick contro M1.** 40 ore di tick a caso: indice `datetime64[ms, UTC]`, primo tick di ogni minuto = apertura
  M1, scarto mediano e massimo **0,00**. I tick non sono spostati.
- **Profilo dello scarto nel tempo** (400 segnali a caso, prezzo eseguibile contro entrata postata):

  | istante rispetto al messaggio | −600 s | −300 s | −120 s | −60 s | 0 s | +10 s |
  |---|---|---|---|---|---|---|
  | quota sfavorevole | 0,87 | 0,85 | 0,87 | 0,97 | **1,00** | 0,995 |
  | scarto mediano ($) | +2,45 | +1,36 | **+0,53** | +0,81 | **+1,65** | +1,69 |
  | quota oltre 1 $ | 0,75 | 0,58 | 0,30 | 0,41 | 0,76 | 0,75 |

  Il minimo sta a 1-2 minuti **prima** del messaggio, simmetrico per lato (buy +0,53, sell +0,53 a −120 s): il
  mentore entra su un estremo locale e posta 1-3 minuti dopo, a prezzo gia' mosso a suo favore. Coincide con il
  referto live dei 4 trade, che usa i fill MT5 e non l'export ("68 s / 186 s prima del messaggio",
  `gump_live_rr_qualitativo_2026-09-29.md` righe 35-41) e con la controprova del 28/09 (export 08:48:40 UTC,
  copier 08:48:46). La simmetria esclude anche una convenzione BID/ASK del prezzo postato.
- **Non e' solo spread.** Spread mediano a t + 10 s 0,40 $ contro scarto mediano 1,69 $; nel referto stesso la
  variante skip1 esegue solo **411 su 1.792** (riga 79): oltre tre quarti hanno uno scarto sopra 1 $ (0,5R).
- **Artefatto residuo possibile: le modifiche (D3, §8.3).** Se il mentore correggeva l'entrata verso un prezzo
  migliore dopo la pubblicazione, lo scarto storico e' gonfiato. Non tocca il primario (usa solo lato e distanze),
  e il live mostra lo stesso fenomeno su testi non modificati.

Interpretazione corretta: il prezzo postato **non e' mai ottenibile** da chi copia; il ritardo vale **+1,238R** sugli
stessi segnali (referto riga 28). L'E[R] al postato (+0,896) e' in gran parte il **vantaggio di partenza** (circa 0,8R
di scarto gia' maturato con un bracket −1R/+5R): non misura il mentore, e per il §5 (riga 171) non si cita mai. Se la
webapp del socio riempie al postato, il suo backtest positivo ha **esattamente** questa forma (§1, riga 72) — da
dire al condizionale, perche' il codice della webapp non l'abbiamo.

⚠️ Il **100% di trade in guadagno al messaggio** e' un campanello, non un merito: nessun trader e' in profitto in
tutte le entrate dopo due minuti. E' compatibile con un posting selettivo (si posta dopo la conferma) o con il prezzo
postato scelto sull'estremo. Non e' misurabile dal passato (§8.2-8.3); chi lo legge come "il mentore ha ragione,
e' il ritardo a rovinarlo" ricade nel bias M1 (confermato senza misura).

### 5. Controlli M1 contro M1 e riserva sull'holding: dichiarati correttamente

- M1 contro M1 come richiesto dalla G1 #3 (N2): braccio reale rifatto su sole M1 (`esegui_test.py:288-289`),
  controlli su M1 (`:290-292`), divario con CI a cluster (`:301-303`), versione su tick solo accanto (`:304-305`).
  Il passaggio da tick a M1 cambia E[R] di +0,044 (−0,342 → −0,298): il divario va letto **solo** sulla riga M1.
- Matching (`esegui_test.py:296-297`): lato esatto su tutte le coppie, rischio identico, hold dichiarato come esito
  confondato (mediana 0,17 h contro 0,23 h, +40%; referto righe 51-56). Corretto.
- Riserva R5 (interpretazione da aggiungere): l'holding piu' corto sugli istanti reali dice che i messaggi cadono in
  momenti **piu' volatili** della stessa ora a ±1-20 giorni (arrivano dopo un movimento, punto 4). Il controllo e'
  appaiato su ora e lato, **non** sulla volatilita'. Col bracket fisso in dollari questo cambia la velocita', non il
  segno atteso; il divario resta compatibile con zero. Non cambia il verdetto, va scritto.
- 14 controlli mancanti (5.308 contro 5.322 attesi) e righe a 5.352 prima del filtro: coerenti con il codice (il
  filtro per `msg_id` a `:295`), nessun problema.

### 6. Descrittive: cosa rischia di essere letto come un risultato, e cosa scrivere per impedirlo

Errore standard per trade di d, dal CI: ≈ 0,039 × √1.774 ≈ 1,64R. Ne seguono queste letture, da scrivere **nella
voce DECISIONS**, non solo qui:

| cella | numero (referto) | perche' non e' un risultato |
|---|---|---|
| post-cutoff 06-09/2026 | n 78, d +0,122, E −0,041 (riga 99) | SE di d ≈ 0,19 → **MDE ≈ 0,52R**: 0,6 errori standard. L'E[R] meno negativo e' **geometria**: da giugno 2026 lo SL e' 3 $ (79 segnali post-cutoff, tutti a ~3 $; prima ~2 $), quindi lo spread pesa un terzo in meno in R (§8.7, righe 253-256; §10 riga 276) |
| anni 2024 e 2026 | d +0,161 (n 339), +0,137 (n 208) | ~1,8 e ~1,2 errori standard, con il 2022 a −0,246 (~−2,5) dall'altra parte. Su ~20 celle descrittive una a |z| ≈ 2 per caso e' attesa. Breadth di d: 2 anni positivi su 6 |
| latenza 0 s | d +0,026 (riga 66) | 0,7 errori standard; il declino 0 → 60 s sta tutto dentro un errore standard |
| LIVE meno negativa | −0,156 contro −0,342 (riga 77) | **Non e' la stessa unita'**: r_unit = |fill − SL| (`replay.py:206`) ≈ 2 $ + scarto, quindi lo stesso costo in dollari pesa meno in R. Non e' un'esecuzione migliore |
| categorie (didattica +0,083, bonus +0,161 su n 13) | righe 93-98 | celle piccole e non indipendenti (un segnale puo' avere piu' categorie) |
| momentum | +0,017 [−0,121; +0,154] (riga 101) | due d ≈ 0 confrontati fra loro: dice "nessuno dei due ha direzione", non "il mentore equivale al momentum" |

Frase da scrivere: *"Le descrittive (latenza, varianti, anni, categorie, post-cutoff, momentum) sono 0 trial e
restano descrittive per sempre sui 1.792 (D1). Sceglierne una perche' e' positiva e' un trial nuovo, validabile
solo su un forward pre-registrato con la sua potenza (§5, righe 190-191)."*

### 7. Stato da registrare, condizioni per riaprire, demo del socio

- **Segue dalla pre-registrazione:** caso 4 → "la fonte non entra in pipeline" (riga 203). Trial 1 su budget 1,
  0 round di rifinitura ammessi (D1, riga 25): sui dati storici **non resta budget**. Per il LIFECYCLE §5 la
  specifica e' NO-GO e la famiglia senza budget residuo non sopravvive → lo stato coerente e' **CLOSED**, con
  verdetto **NON DIMOSTRATO (MDE 0,130R)**, non "refutato" ne' "falsificato". `gate_finale: "forward"` era la
  condizione per un LEAD: con questo esito non si attiva (il campo puo' restare, `--check` lo accetta: verificato,
  exit 0).
- **Riapertura (§7 LIFECYCLE):** solo con evidenza nuova che cambi **cosa vede chi copia**, non con piu' dati dello
  stesso tipo:
  1. il mentore pubblica **prima** di entrare (ordini pendenti o livelli con tempo per agire): e' un segnale diverso,
     quindi un'ipotesi nuova con pre-registrazione nuova;
  2. un canale o un feed che arriva all'istante d'ingresso del mentore (oggi non esiste);
  3. un confronto fra export (`analysis/mentor_signals/confronta_export.py`) che mostri cancellazioni o modifiche:
     questo pero' puo' solo **peggiorare** la stima, non riaprire.
  Ogni proposta deve portare la **potenza prima**: al ritmo di ~300 segnali l'anno, un forward con la stessa
  esecuzione ha MDE ≈ 0,32R dopo un anno, arriva a 0,13R dopo ~6 anni e a 0,07R (il limite superiore attuale) dopo
  ~20. Un forward di Gump "per vedere" e' futile per costruzione
  ([[feedback_potenza_prima_di_raccogliere]]). La variante LIMIT non e' una via: descrittiva, scelta dopo l'esito,
  e comunque −0,368 (riga 78).
- **Demo del socio:** e' sua e puo' continuare, ma per noi:
  - **non e' un forward test** (nessuna pre-registrazione) e non puo' validare nulla in tempi utili (vedi potenza);
  - il suo valore atteso, con questa esecuzione, e' **negativo per trade, dell'ordine dei costi** (−0,34R a spread
    Dukascopy): in denaro reale, o su una prop, no;
  - il prodotto utile e' di **misura**, a 0 trial: lo spread reale del broker e la latenza dai fill, e un secondo
    export per misurare cancellazioni e modifiche (D3). Il journal deve salvare l'id dei messaggi
    ([[feedback_export_non_e_track_record]]);
  - se la demo usa la gestione "BE" o i bracket 8-8 / 10-7, sta girando configurazioni **non testate** qui: il suo
    esito non conferma ne' smentisce questo test.

## RISERVE (6)

- **R1 [Step 3bis]** Il referto riporta la quota (99,6%) ma non la **grandezza** dello scarto: letta da sola sembra
  un effetto di spread. Grandezza misurata qui (punto 4): mediana +1,69 $ a t + 10 s, ~75% oltre 1 $. · Da scrivere
  nella voce DECISIONS.
- **R2 [verdetto]** Manca l'MDE pre-registrato di E[R] (0,171R) accanto al verdetto (§6, riga 196). · Formale.
- **R3 [convenzioni]** E[R] in convenzione ottimistica non riportato (solo d). · Impatto atteso piccolo (uscite
  quasi tutte sui tick); la distanza fra le convenzioni su E resta non misurata.
- **R4 [CI]** Numero di giornate (cluster) non stampato (`ci_cluster_giorno` lo calcola, `replay.py:306`, ma
  `_riga` non lo scrive). · Nessun impatto sul verdetto.
- **R5 [matching]** Holding +40% sugli istanti reali = volatilita' non appaiata (punto 5). · Non cambia il segno.
- **R6 [allineamento repo]** Frontmatter della pre-registrazione ancora `stato: APPROVATA`, `metrica_corrente:
  "nessuna: nessun esito calcolato"`; ledger `stato: QUARANTENA`, `verdetto: null`; nessuna voce DECISIONS
  dell'esito. · Da allineare **dopo** che Matteo dichiara il verdetto, nella stessa sessione
  ([[feedback_post_verdict_repo_sync]]).

## VERIFICATO E A POSTO (12)

Verdetto meccanico (`esegui_test.py:269-277`) · MDE pre-registrato nell'etichetta (`:56`, `:277-279`) · definizione
dello scarto e denominatore (`replay.py:192`, `esegui_test.py:262`) · costo del ritardo sugli stessi segnali
(`:260-261`) · kill sui dati sotto soglia (0,0% / 0,9% / 0,1%, referto righe 7-9) · fill 100% da tick · fuso unico
in `carica.py` con verifica · tick allineati alle M1 (40 ore, scarto 0) · scarto simmetrico per lato · controlli M1
contro M1 e `check_matching` · varianti solo sul lato del mentore (`esegui_appaiato` rifiuta le altre,
`replay.py:286-287`) · `python -m core.trial_ledger --check` exit 0.

## ESECUZIONE

- Fill non ottenibili: il primario e' a mercato a t + 10 s, ottenibile per costruzione dopo lo SKIP (0,9%). Prezzo
  postato gia' superato a t + L: **99,6% dei trade eseguiti** (1.774); scarto mediano +1,69 $ (campione di 400,
  misura del guardiano).
- Convenzione d'uscita: `PESSIMISTA` (pareggio SL, `gap_beyond_stop=True`), tick per 60 min poi M1; ottimistica
  solo su d.
- Variante riportata: ricentrata a mercato (primaria); postato solo come costo del ritardo, etichettato NON
  OTTENIBILE.

## CONTABILITA'

- Trial di questo test: 1 · cumulato famiglia: 1 · budget residuo sui dati storici: **0** (D1).
- Holdout famiglia: **aperto il 2026-10-02** (unica apertura; il ledger lo registra).
- Pre-registrazioni esterne 2026-Q4: **1 di 2-3** (`python -m core.trial_ledger`, 02/10).
- DSR: n_trial = 1; irrilevante per un esito negativo.

## DEBITO DI PROTOCOLLO

- Il controllo **tick contro M1** e il **profilo dello scarto rispetto al messaggio** li ho fatti a mano: nessuna
  primitiva in `core/data_checks.py` li copre. Il secondo e' il controllo che distingue "ritardo del copier" da
  "ritardo del messaggio" e vale per ogni canale di segnali (XAT compreso).
- CI a cluster per giornata implementato nel motore (`replay.py:295-306`), non in `core/` (debito gia' dichiarato
  nel §5).
- `--futilita` annualizza a 252 anche sui trade (debito gia' dichiarato nel §7).

---

## Testi proposti (da confermare da Matteo)

**Voce DECISIONS:**

> ## 2026-10-02 (esito) — Gump: **NON DIMOSTRATO (MDE 0,130R)** al primo e unico trial; famiglia **CLOSED**
>
> Esecuzione unica del 02/10 ([referto](docs/reviews/forexgump_esito_2026-10-02.md), G2
> [qui](docs/reviews/forexgump_G2_2026-10-02.md)). Caso 4 del §6: d = −0,007 [−0,082; +0,069], CI a cluster per
> giornata, n 1.774. MDE pre-registrato 0,130R su d, 0,171R su E[R]. **Non dimostrato non vuol dire refutato**:
> il CI rende poco plausibile un d sopra ~0,07R (un divario mentore − opposto sopra ~0,14R), sotto questa
> esecuzione.
> Accanto, pre-registrato nel §6: copiato a L = 10 s con bracket ricentrato, **E[R] −0,342R [−0,431; −0,248]**
> (stress −0,636). La perdita e' il costo di transare, non un'abilita' negativa: il lato casuale perde quasi lo
> stesso. Cancellazioni e modifiche (§8.2-8.3) spingerebbero verso l'alto: il numero e' conservativo rispetto a loro.
> Step 3bis: prezzo postato gia' superato al momento d'agire nel **99,6%** dei trade, scarto mediano ~1,7 $ (~0,8R),
> presente **gia' al messaggio** (il mentore posta 1-3 minuti dopo l'ingresso). Costo del ritardo +1,238R. Il
> backtest al prezzo postato non e' ottenibile e non si cita.
> Descrittive (latenza, varianti, anni, categorie, post-cutoff, momentum): 0 trial, descrittive **per sempre**. Il
> post-cutoff (n 78, d +0,122) ha MDE ≈ 0,52R e il suo E[R] meno negativo e' geometria (SL 3 $ da giugno). Sceglierne
> una e' un trial nuovo, solo su forward pre-registrato.
> **Riapertura** solo se cambia cosa vede chi copia (il mentore pubblica prima di entrare, o un feed all'istante
> d'ingresso), con la potenza prima: lo stesso forward servirebbe ~6 anni per un MDE di 0,13R.
> **Demo del socio:** non e' un nostro forward. Valore atteso negativo dell'ordine dei costi; si usa solo per
> misurare spread reale, latenza e un secondo export (D3), a 0 trial. Nessun capitale.

**Ledger (`forexgump_signals`):**

```json
"stato": "CLOSED",
"verdetto": "NON DIMOSTRATO (MDE 0,130R) al primo e unico trial (02/10): d -0,007 [-0,082; +0,069]; copiato a L=10 s E[R] -0,342 [-0,431; -0,248]",
"fonti": [ ...le attuali...,
  "docs/reviews/forexgump_esito_2026-10-02.md",
  "docs/reviews/forexgump_G2_2026-10-02.md",
  "DECISIONS.md 2026-10-02 (esito)" ]
```

Nella pre-registrazione: frontmatter `stato: CLOSED`, `metrica_corrente` con il verdetto e il link al referto, voce
nel §10.
