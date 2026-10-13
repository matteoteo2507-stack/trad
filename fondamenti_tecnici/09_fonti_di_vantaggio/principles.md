---
aliases: [09_fonti_di_vantaggio]
titolo: "Fonti di vantaggio — come si costruisce un'ipotesi prima di testarla"
fonti:
  - "Bozza di Claude (03/10/2026), conoscenza propria: QUARANTENA finche' ogni voce non e' confermata da una fonte umana (piano in §6)"
  - "Fonti interne gia' distillate: Kichev (insight_da_yt, 14/08), SINTESI del funnel Chart Fanatics §3 e §6, blocco E.1 (Siento), DECISIONS 2026-10-03 (2)-(4)"
tipo: concetti
stato: quarantena
creato: 2026-10-03
---

# Fonti di vantaggio — come si costruisce un'ipotesi prima di testarla

> Il repo sa **verificare e bocciare** una strategia ([STRATEGY_LIFECYCLE](../../docs/STRATEGY_LIFECYCLE.md),
> [QUANT_REVIEW_PROTOCOL](../../docs/QUANT_REVIEW_PROTOCOL.md), [[04_quant_metodologia]], `core/`), ma fino al
> 03/10/2026 non diceva **come si arriva a un'ipotesi che valga la pena verificare**. La fase RICERCA del ciclo
> di vita era un riquadro con scritto "razionale economico". Il risultato: si cercava **per elenco** (video,
> canali, materiale del socio) e si passava ogni candidato alla macchina dei verdetti. Questo modulo rovescia
> l'ordine. Prima si chiede **da quale meccanismo puo' nascere un vantaggio, chi lo paga e perche'**; poi si
> cerca dove vederlo; solo alla fine si scrive una regola.

## 0. Stato di questo modulo — leggere prima

- E' la **bozza B** decisa con Matteo il 03/10: struttura scritta da Claude, da **confermare voce per voce**
  con le fonti del §6 (piano A). Finche' una voce non ha la sua fonte umana, resta `quarantena`.
- **Provenienza** ([STRATEGY_LIFECYCLE §8](../../docs/STRATEGY_LIFECYCLE.md)). Questa griglia serve a
  **orientare la ricerca di fonti**, non a generare ipotesi da testare. Un'ipotesi che io deduco dalla griglia
  su dati anteriori al mio cutoff **non e' una predizione indipendente**. Diventa ammissibile solo se arriva
  anche da (a) una fonte umana datata, o (b) un razionale che non richiede di conoscere l'esito, o (c) un
  forward.
- Gli esempi di letteratura citati sotto vengono dalla mia memoria e sono segnati **(da confermare)**.

## Concetti

### 1. La domanda madre: chi mi paga, e perche' continuera' a farlo?

Ogni vantaggio e' un **trasferimento**: qualcuno, dall'altra parte, accetta in media di perdere. Prima di
qualunque dato servono tre risposte:

1. **Chi c'e' dall'altra parte?** Una categoria concreta: chi si copre, un fondo con un mandato, un ETF che
   deve ribilanciare, un investitore che reagisce in ritardo, un market maker obbligato a coprirsi.
2. **Perche' accetta di perdere?** Ottiene qualcos'altro (un'assicurazione, liquidita' immediata, il rispetto
   di un vincolo) **oppure** sbaglia in modo sistematico.
3. **Perche' nessuno l'ha gia' eliminato?** Cioe' qual e' il **limite all'arbitraggio**: serve capitale, il
   rischio e' reale, la capacita' e' piccola, c'e' un vincolo istituzionale, o chi potrebbe arbitrarlo
   rischia la carriera.

**Se non si sa rispondere, non e' un'ipotesi: e' un pattern.** Il nostro storico lo conferma. Le famiglie
chiuse con piu' trial (livelli, Fibonacci, FADE/NXT, ORB) partivano tutte da un pattern grafico senza un
"chi paga". La SINTESI del funnel (§3) aveva gia' visto la stessa cosa dall'esterno: le fonti oneste sono
quelle che descrivono un **meccanismo economico**.

### 2. Le cinque classi

| # | classe | chi paga | perche' accetta | forma tipica del rendimento | come decade |
|---|---|---|---|---|---|
| 1 | **Premio per il rischio** | chi vuole scaricare un rischio (si copre, vuole liquidita', non sopporta i crolli) | compra un'**assicurazione**: non e' un errore | media positiva, **asimmetria negativa**, crolli rari e grandi | quando il rischio smette di esserci o il premio si affolla (il carry G10 dopo il 2008) |
| 2 | **Flusso forzato / vincolo** | chi **deve** comprare o vendere a prescindere dal prezzo (ribilanciamenti, roll, coperture obbligate, liquidazioni, fixing) | il vincolo e' istituzionale (prospetto, mandato, margine, regola) | piccolo, frequente, **ancorato al calendario o all'orario**, capacita' limitata | quando il flusso diventa prevedibile e troppi lo anticipano |
| 3 | **Errore comportamentale** | chi reagisce in modo sistematicamente sbagliato (in ritardo, in eccesso, per attenzione o disposizione) | non sa di sbagliare | dipende: il momentum ha code negative, la reversione e' piu' simmetrica | **dopo la pubblicazione** (McLean-Pontiff 2016, abstract letto l'08/10: [[10_indicatori_tecnici]] §3.4) e con l'automazione |
| 4 | **Informazione o analisi** | chi e' meno informato o elabora peggio | non lo sa o non puo' fare altrimenti | dipende dall'informazione | quando l'informazione diventa pubblica o economica |
| 5 | **Velocita' / microstruttura** | chi arriva dopo | non ha l'infrastruttura | molti piccoli guadagni | con la corsa tecnologica: vince chi e' piu' veloce |

**Lettura economica, utile a ogni ipotesi:**
- Le classi **1 e 2** non richiedono che qualcuno sbagli, quindi **sopravvivono meglio** alla pubblicazione.
- La classe **3** sopravvive solo se l'arbitraggio e' limitato.
- Le classi **4 e 5** sono gare: vince chi ha il dato o la velocita' migliore. Per un retail sono quasi
  sempre perse in partenza.

### 3. Dove abbiamo cercato finora: i nostri verdetti sulla griglia

| classe | cosa abbiamo testato o valutato | esito | accessibile al nostro perimetro? |
|---|---|---|---|
| **1 · premi** | premio azionario (PAC); copertura nei COT (03/10); carry FX (03/10); VRP (parcheggiato); oro notturno (proposto come premio, era classe 3: 03/10) | PAC operativo; COT e carry **chiusi** (potenza, premio sparito, operabilita'); VRP fuori perimetro | **poco**: i premi documentati sono gia' presi, fuori perimetro o spariti |
| **2 · flussi forzati** | **momentum dell'ultima mezz'ora** (coperture di gamma, Baltussen et al. 2021): primo e unico test della classe, 12/10. Prima: solo la traccia di Siento (funnel E.1), non testabile senza la catena delle opzioni | **CLOSED al train** su S&P 500 e Nasdaq dal 2020 (DECISIONS 2026-10-12 (2)); le altre direzioni del §5 **mai guardate** | **da capire**: alcuni flussi sono ancorati a orari e date che i nostri dati intraday vedono (§5) |
| **3 · comportamento** | livelli (384 trial), FADE/NXT, ORB, London breakout, TSMOM, mean reversion vol, stagionalita' TOM, griglia a numeri tondi, B1, B3, trend/playground, regola dell'1% sul VIX | **tutti chiusi**, tranne A1 (LEAD fermo per potenza) | si', ma e' la classe dove abbiamo **gia' speso quasi tutto** |
| **4 · informazione** | **segnali del mentore XAT e di Gump**: compriamo l'informazione o l'analisi di un terzo; PEAD (D3) per i dati | XAT in revisione (storico selezionato), Gump **CLOSED** (DECISIONS 2026-10-05); PEAD bloccato dai dati (G6 a pagamento) | **solo comprandola da terzi**, e misurandola col forward |
| **5 · velocita'** | order flow (D1); il copier e' il caso **inverso**: siamo noi quelli lenti, e paghiamo il ritardo (gate C5) | fuori portata | no |

**La lettura che conta.** Abbiamo speso quasi tutto il budget di ricerca nella classe 3, la piu' affollata e
la piu' esposta al decadimento dopo la pubblicazione. Nella classe 1 il perimetro ci blocca. **Nella classe 2 abbiamo
fatto un solo test** (12/10, chiuso); fine mese, fixing e scadenze restano da guardare. L'unico binario vivo con un passato positivo, il mentore, sta nella classe 4: non e'
un caso, e' la classe in cui un terzo puo' avere qualcosa che noi non abbiamo.

### 4. Le domande della fase RICERCA (prima del template e della pre-registrazione)

In quest'ordine. Ci si ferma alla prima risposta mancante.

1. **Classe.** In quale delle cinque cade? Se in nessuna, e' un pattern: stop.
2. **Chi paga e perche'.** Le tre risposte del §1, scritte in una frase ciascuna.
3. **Limite all'arbitraggio.** Perche' esiste ancora? Se la risposta e' "perche' nessuno l'ha visto", il
   prior e' basso.
4. **Dove si vede.** Il **meccanismo** sceglie strumento, orizzonte e dato, non il contrario. Un flusso di fine
   mese si vede attorno a fine mese; un premio di copertura si vede nel rendimento di roll dei futures, non in
   un CFD.
5. **Forma del rendimento.** Asimmetria, frequenza, crolli: decide la metrica. Su un premio con code negative
   lo Sharpe da solo inganna ([[04_quant_metodologia]], [[05_portfolio_rischio]]).
6. **Accessibilita'.** Strumento (CFD o futures), capitale minimo, costi, swap, broker. Su COT e carry e' la
   domanda che ha chiuso tutto: va fatta **prima**, non dopo.
7. **Potenza.** Quanti anni, eventi o strumenti indipendenti servono per vedere l'effetto atteso
   ([[feedback_potenza_prima_di_raccogliere]]). Va calcolata sullo **Sharpe pubblicato e su meta' di esso**.
8. **Dove muore.** Cosa falsificherebbe il **meccanismo**, non solo il pattern. Per esempio: se il flusso non
   c'e', anche il rendimento non deve esserci.
9. **Provenienza.** Da dove arriva l'ipotesi ([STRATEGY_LIFECYCLE §8](../../docs/STRATEGY_LIFECYCLE.md)).

Solo dopo: [template di strategia](../../strategies/_template/README.md) e pre-registrazione (G1).

### 5. Dove la griglia suggerisce di guardare — direzioni di lettura, non ipotesi

Servono a scegliere **cosa leggere** nelle fonti del §6, non cosa testare. Ognuna deve entrare da
[`_INTAKE.md`](../_INTAKE.md) con una fonte umana prima di diventare un'ipotesi.

- **Classe 2 nel nostro perimetro.** Flussi ancorati a un orario o a una data che i nostri dati vedono:
  - ribilanciamenti di fine mese o di fine trimestre dei fondi bilanciati (indici, obbligazionario);
  - fixing delle valute delle 16 di Londra (FX);
  - coperture di fine giornata degli ETF a leva e dei market maker (indici, ultima mezz'ora; momentum
    intraday: Gao-Han-Li-Zhou 2018 da confermare; Baltussen et al. 2021 abstract letto l'08/10, lega il
    momentum dell'ultima mezz'ora alle coperture di gamma dei market maker di opzioni e degli ETF a leva:
    [[10_indicatori_tecnici]] §2). **Testato e CLOSED il 12/10** (DECISIONS 2026-10-12 (2)): non riproporre;
  - scadenze delle opzioni sugli indici.

  ⚠️ Tutti cadono vicino al perimetro gia' chiuso dell'intraday sugli indici (ORB, London breakout), dove i
  costi hanno ucciso tutto: il punto 6 del §4 va fatto **per primo**.
- **Classe 4 senza comprare dati.** L'unica strada gia' aperta e' misurare **persone** (mentore, socio,
  canali) col forward. E' gia' il nostro binario principale: la griglia lo conferma, non lo cambia.

### 6. Piano A — le fonti con cui confermare questa bozza

| fonte | perche' | copre |
|---|---|---|
| Ilmanen, *Expected Returns* (2011) | catalogo dei premi con le loro condizioni e i loro crolli | classe 1 |
| Pedersen, *Efficiently Inefficient* (2015) | strategie dei fondi spiegate dal "chi paga", con interviste ai gestori | classi 1-3 |
| Harris, *Trading and Exchanges* (2003) | chi sta dall'altra parte di ogni scambio, tipi di trader e perche' guadagnano o perdono | classi 2, 4, 5 |
| McLean, Pontiff, *Journal of Finance* (2016) | quanto si riducono le anomalie dopo la pubblicazione | decadimento, classe 3 |
| Harvey, Liu, Zhu, *Review of Financial Studies* (2016) | quante "scoperte" sono rumore, con soglie di t piu' alte | fa da ponte con [[04_quant_metodologia]] |

Titoli e anni sono dalla mia memoria (**da confermare** all'acquisizione). Ogni fonte entra da `_INTAKE.md` con
il metodo di sempre: si raccolgono le regole e i meccanismi, si scartano le statistiche dichiarate senza
campione.

## Regole operative

- **Nessuna ricerca di candidati senza la griglia.** Prima di scorrere un elenco (video, canale, backlog,
  materiale di terzi) si scrive quale **classe** si sta cercando e perche'.
- **Un candidato senza classe e' un pattern.** Va a `_INTAKE.md` come segnalazione, non in pre-registrazione.
- **L'accessibilita' si verifica prima della potenza, e la potenza prima dei dati.** E' l'ordine che avrebbe
  chiuso COT e carry in un'ora invece che in mezza giornata.
- **La griglia orienta, non genera.** Un'ipotesi dedotta da qui da Claude deve comunque soddisfare la
  provenienza del §8 del ciclo di vita.

## Collegamenti

- [STRATEGY_LIFECYCLE §1](../../docs/STRATEGY_LIFECYCLE.md): questo modulo e' la fase RICERCA del loop; §8 per la provenienza.
- [[04_quant_metodologia]] (verifica), [[05_portfolio_rischio]] (premi, VRP, asimmetria), [[03_regimi_macro]] (canali macro).
- [[10_indicatori_tecnici]]: questa griglia applicata agli indicatori (quale grandezza misurano, chi paga). Le sue Fonti danno il livello di verifica di McLean-Pontiff 2016 e Baltussen et al. 2021 (abstract letto) e di Gao-Han-Li-Zhou 2018 (ancora solo sintesi del motore di ricerca).
- [Mappa del ciclo di vita](../../mappa/01-ciclo-di-vita-e-gate.md), passo 1.
- [Ricerca nel repo del 03/10](../../docs/reviews/ricerca_repo_2026-10-03.md): l'inventario che ha mostrato il buco.
- Kichev ([insight_da_yt](../_sorgenti/insight_da_yt/kichev_first_principles_+_yush_orderflow_2026-08-14.md) §3-4): concorrenza e decadimento, la fonte umana gia' in casa piu' vicina a questa griglia.

## Fonti

- **Bozza di Claude, 03/10/2026** — struttura, classi e domande: conoscenza propria, **quarantena**.
- **Fonti interne** gia' distillate e citate sopra: Kichev (14/08), SINTESI del funnel Chart Fanatics §3 e §6,
  blocco E.1 (Siento), DECISIONS 2026-10-03 (2), (3) e (4).
- **Da acquisire** (piano A, §6): Ilmanen, Pedersen, Harris, McLean-Pontiff, Harvey-Liu-Zhu.
