# Momentum dell'ultima mezz'ora — revisione G2 del gatekeeper (2026-10-12)

Revisore: `.claude/agents/quant-gatekeeper.md`, dopo l'esecuzione unica del train. Esito rivisto:
[ultima_mezzora_train.txt](esiti/ultima_mezzora_train.txt) (12/10, commit `2b66e65`). Pre-registrazione:
[ULTIMA_MEZZORA_PREREGISTRATION.md](../ULTIMA_MEZZORA_PREREGISTRATION.md). Lettura rivista: DECISIONS 2026-10-12 (2).

Le misure fatte in questa revisione stanno in due script nuovi, lanciati il 12/10 sui soli dati del train:
[`verifiche_g2.py`](../../analysis/ultima_mezzora/verifiche_g2.py) e
[`descrittivo_anno_migliore.py`](../../analysis/ultima_mezzora/descrittivo_anno_migliore.py). Sono **descrittivi a
posteriori: non decidono, non sono un trial, non riaprono nulla**. Tutti e due riproducono prima i numeri dell'esito
e si fermano se non tornano. L'holdout non e' stato aperto ne' letto.

**Verdetto G2: PASSA CON RISERVE.** 0 bloccanti sul verdetto. L'etichetta **CLOSED** segue dalla regola del §6 e regge
ai controlli; non e' un NON DIMOSTRATO. Le riserve riguardano la **lettura** scritta in DECISIONS: una frase e'
smentita dall'esito stesso, una spiegazione non ha fonte, manca un punto, quattro frasi vanno precisate (§4). Il
verdetto sulla famiglia lo dichiara Matteo: qui c'e' l'evidenza.

## 1. Integrita' dell'esecuzione: a posto

- **Codice congelato.** Fra `2b66e65` (approvazione) e `272f0fb` (esito) cambia un solo file: l'esito. `git diff` e'
  vuoto su `analysis/ultima_mezzora`, pre-registrazione, contatore, `core/` e `tests/`. Dopo, in `8f0ca54`, la
  pre-registrazione cambia solo nel frontmatter e nel §10; regole, soglie e baseline (§2-§8) sono identici.
- **Contatore prima del lancio.** Al commit `2b66e65`: `trial_cumulati = 1`, `holdout_aperto = null`, pre-registrazione
  `stato: APPROVATA`. Lo script non parte senza queste tre cose.
- **Una esecuzione.** In `esiti/` c'e' un solo file della famiglia, senza la riga `RIPRESA`. Il segnaposto e' stato
  creato 11 secondi dopo il commit di approvazione, l'esito scritto 63 secondi piu' tardi e committato dopo altri 20.
  La cartella non ha piu' ricevuto file. Il file sul disco e' quello committato.
- **L'esito e' cio' che il codice congelato produce su questi dati.** Le impronte dei due file coincidono con quelle
  scritte nell'esito. Ricalcolati per import, con seme 42: divario −0,51 [−2,01; +0,99], MDE 2,15, effetto atteso 4,56,
  i sette divari annui, i tre terzili, i due strumenti, attesa netta, taglia fissa, runs test. Tornano tutti.
- **I dati sono letti bene** (un verdetto negativo non ha un controllo positivo sui dati reali; questo e' il
  sostituto). Gli stessi rendimenti calcolati da un secondo fornitore, i file MT5 FP Markets, su 345 e 353 sedute
  comuni (02/2025 → 07/2026): r_ROD correlato a 0,999 su entrambi gli indici; r_LH a 0,994 e 0,997 tolti i quattro
  giorni del 10-13/03/2025, in cui e' il file MT5 ad avere l'ora sbagliata
  ([FATTIBILITA](../ULTIMA_MEZZORA_FATTIBILITA.md), passo 3). I 7 test sulla lettura delle barre passano.

**Cosa non si puo' verificare, e lo dichiaro.**
1. Che le funzioni non siano mai state provate sui dati reali prima dell'approvazione. Le guardie proteggono il lancio
   dello script, non un import da una sessione Python. E la storia precedente non e' in git: codice e pre-registrazione
   entrano nel repo per la prima volta con il commit di approvazione, quindi le due passate G1 non si possono
   confrontare col testo approvato (§8, debito 1).
2. Che l'esecuzione sia stata una sola in senso stretto. Gli artefatti sono coerenti con una; non la dimostrano. Il
   rischio che la regola protegge e' scegliere fra piu' lanci: qui i semi sono fissi, un rilancio da' gli stessi numeri.
3. Per l'holdout: vedi §7.

## 2. Verdetto contro il §6: CLOSED

- **PASSA non scatta**, quindi la sua precedenza non conta: mancano tutte e cinque le condizioni. Limite basso del
  divario −2,01 (soglia +0,20); limite basso dell'attesa netta −2,43; netto a costi tripli −1,71; divario negativo su
  entrambi gli indici (−0,75 e −0,27); guardia a taglia fissa a −0,10 errori standard (soglia +1,645).
- **CLOSED scatta**: limite alto del divario +0,99 pb, sotto la meta' dell'effetto atteso, 2,28 pb.
- **Le unita' sono giuste.** L'effetto atteso e' la correlazione di riferimento (0,1725, media fuori campione di ES e
  NQ) per la media di |w| × |r_ROD/sigma| × deviazione mobile dell'ultima mezz'ora: 0,1725 × 26,4 = 4,56 pb a seduta
  sul portafoglio, come il divario. I fattori sono noti prima dell'esito di ogni giorno. Codice e §6 coincidono.
- **Quanto e' robusto.** La soglia sta a 3,6 errori standard dalla stima. Per diventare NON DIMOSTRATO la parte alta
  dell'intervallo dovrebbe essere piu' larga dell'**86%**. Misurato: su 10 semi il limite alto va da +0,92 a +1,03;
  con blocchi medi da 1 a 120 sedute va da +0,94 a +1,46. Sempre sotto 2,28, e sempre sotto la riga piu' bassa della
  tabella di esclusione (1,99).

## 3. I controlli della G2

| controllo | esito | nota |
|---|---|---|
| fill non ottenibili | 0 su 1.537 per indice, per costruzione | ordine a mercato alla prima barra dopo il segnale, uscita alla chiusura, nessun livello e nessuno stop. Scarto fra chiusura del segnale e apertura dell'entrata: mediana 0,46 e 0,14 pb, massimo 2,8 |
| baseline accanto al risultato | si' | la primaria **e'** il divario dal braccio casuale; taglia identica giorno per giorno, esposizione netta +0,072 contro +0,076, deriva tolta |
| intervalli a blocchi | si' | bootstrap stazionario sui giorni, sul portafoglio (i due indici non contano due volte) |
| MDE | 2,15 pb, accanto al verdetto | viene dall'errore standard a blocchi (0,77), che qui coincide con quello semplice (0,78). Con blocchi da 20 a 120 sedute l'errore standard sale fino a 0,92 e l'MDE fino a 2,59: sopra la meta' dell'effetto. L'esclusione regge lo stesso (§2); "MDE 2,15" vale col blocco pre-registrato |
| costi 3x | −1,71 pb | misurato qui anche l'intervallo: [−3,17; −0,23]. Costo medio pagato: 0,37 pb a seduta (1,11 a costi tripli) |
| ampiezza | 2 anni su 7 col divario positivo, 1 su 7 col netto; 0 indici su 2 | i due indici valgono uno strumento |
| p Monte Carlo | 0,774 [0,747; 0,800] su 1.000 | 0,05 e' fuori dall'intervallo; non decide |
| DSR e futilita' | 1 trial: DSR = PSR = 0,099; Sharpe per seduta −0,033 contro un pavimento di 0,042 | sotto il pavimento |
| doppio binario | O1 e O3: nessun valore di dipendenza (percentili 83,6 e 81,2) | sequenza giusta: una operazione al giorno, senza sovrapposizioni |

**Il runs test a p 0,052 non e' un problema per l'intervallo.** Tre motivi, misurati.
1. Riguarda un'altra serie: la sequenza vinto/perso della taglia fissa (z −1,94; autocorrelazione a un giorno +0,049).
   Sul segno del divario giornaliero, che e' la primaria, z −1,15 e p 0,25.
2. Il divario giornaliero non mostra dipendenza a breve: autocorrelazioni −0,031, −0,040, +0,053, −0,029 e +0,012 ai
   ritardi 1, 2, 3, 5 e 10, contro una banda del caso di ±0,050. Una sola tocca il bordo, e i segni si alternano.
3. L'intervallo non assume l'indipendenza, e non cambia quando la si assume: [−2,02; +0,99] con giorni indipendenti,
   [−2,01; +0,99] con il blocco pre-registrato.

L'etichetta "indipendenza non respinta" stampata dallo script e' una lettura a soglia di un numero che sta sulla
soglia: si legge come "raggruppamento debole, non distinguibile dal caso".

## 4. La lettura in DECISIONS 2026-10-12 (2), frase per frase

Sostenute dall'esito, senza modifiche: i numeri del paragrafo "Esito"; "nessuna condizione di PASSA e' soddisfatta";
i numeri noti riprodotti; fill; p; ampiezza; il 2,7% del sintetico (pre-registrazione §9); "non smentisce il paper sul
suo campione"; conseguenze; condizioni di riapertura (coerenti con LIFECYCLE §7).

**Da correggere.**

1. *"un divario sotto circa 1 pb a seduta non e' escluso. Ma a quel livello sta sotto i costi."* La prima meta' e'
   giusta (limite alto +0,99). **La seconda e' smentita dall'esito.** Il costo medio pagato e' 0,37 pb a seduta: 1 pb
   e' 2,7 volte tanto. E l'intervallo dell'attesa netta arriva a +0,50: un netto positivo ai costi del test non e'
   escluso. E' escluso solo a costi tripli. Testo proposto:
   > Non dice che l'effetto e' zero: un divario fino a circa +1 pb a seduta non e' escluso (limite alto +0,99). Ai
   > costi usati nel test, 0,37 pb a seduta in media, non starebbe sotto i costi: il limite alto dell'attesa netta e'
   > +0,50 pb. Un netto positivo e' escluso solo a costi tripli: −1,71 [−3,17; −0,23] (`verifiche_g2.py`, 12/10).

2. *"Decadimento dopo la pubblicazione, CFD al posto dei futures, barre a 5 minuti: il test non distingue fra queste
   tre spiegazioni."* Le **barre a 5 minuti** non sono fra le differenze dichiarate (pre-registrazione §3) e non c'e'
   un numero che le sostenga: segnale ed entrata cadono sul confine dei 30 minuti, che le barre a 5 minuti risolvono
   esattamente. **Mancano** invece due spiegazioni scritte prima del test: il cambio di regime dopo il 2021 (terza
   previsione della scheda H1 nel backlog, 08/10; pre-registrazione §9) e un difetto nostro (§8). Testo proposto:
   > Non smentisce il paper sul suo campione (futures, 1974-2020). Il test non distingue fra le spiegazioni:
   > decadimento dopo la pubblicazione; cambio di regime dopo il 2021 (opzioni a scadenza giornaliera, gia' scritto
   > nella scheda H1 del backlog); CFD lato denaro al posto dei futures; un difetto della nostra lettura dei dati, che
   > un solo stadio non puo' escludere (pre-registrazione §8). Sull'ultimo punto la G2 ha confrontato i rendimenti con
   > un secondo fornitore sul 2025-2026 e coincidono.

3. *"Il 2022 e' l'unico anno nettamente positivo [...] un parametro scelto sull'esito"*. "Nettamente" e'
   un'impressione: ora c'e' la misura (§5). E per LIFECYCLE §3 e' un filtro, non un parametro. Testo proposto:
   > **Il 2022** e' l'unico anno con un divario grande e positivo: +4,89 pb, cioe' +1,80 errori standard di
   > quell'anno (il 2023 e' a +0,14). E' un descrittivo guardato dopo, il migliore di sette. Sotto il nullo del test
   > l'anno migliore dei sette arriva a +4,89 pb nel 6,7% dei casi e a +1,80 errori standard nel 23,8%; fra le 12
   > celle di sottocampione dell'esito la migliore arriva a +1,80 nel 31,1% (`descrittivo_anno_migliore.py`, 12/10).
   > Non si distingue da cio' che il caso produce quando si guardano sette anni. Un filtro di regime scelto adesso
   > sarebbe un filtro scelto sull'esito (LIFECYCLE §3 e §4), su una famiglia chiusa.

**Da precisare.**

4. *"l'effetto pubblicato e la sua meta' sono esclusi su questi dati"*. Sostenuta, con tre precisazioni. E' una
   esclusione al 95%, non una dimostrazione. Cio' che e' escluso e' il divario che la **correlazione** pubblicata
   produrrebbe con questa posizione, tradotto con la formula del §6 (validata sul sintetico, dove l'effetto e' lineare
   e uguale ogni giorno). Contro l'altro numero della fonte, il rendimento della strategia di solo segno (Tab. 6:
   2,72 pb a seduta, [FATTIBILITA](../ULTIMA_MEZZORA_FATTIBILITA.md)), la taglia fissa esclude l'effetto pieno ma la
   meta' (1,36) **solo al margine**: limite alto +1,28. Non era la soglia pre-registrata e non cambia l'etichetta.
   > Il limite alto sta sotto: **con l'intervallo al 95% sono esclusi, su questi dati, il divario che la correlazione
   > pubblicata produrrebbe con questa posizione (formula del §6) e la sua meta'** (tutte le otto righe della tabella
   > di esclusione). Regge su 10 semi (limite alto da +0,92 a +1,03) e con blocchi da 1 a 120 sedute (al piu' +1,46).
   > Contro il rendimento pubblicato della strategia di solo segno (2,72 pb) la taglia fissa esclude l'effetto pieno;
   > la meta' solo al margine (+1,28 contro 1,36).

5. *"La scelta fra proporzionale e solo segno non ha cambiato l'esito."* L'esito dice solo che nessuna delle due
   passa. L'etichetta a taglia fissa non c'e', perche' la soglia in quelle unita' non era pre-registrata. Calcolata
   qui con la stessa formula: 3,69 pb, meta' 1,84; limite alto +1,28, quindi CLOSED anche li'.
   > Nemmeno il solo segno passa. Con la formula del §6 tradotta in taglia fissa (3,69 pb, meta' 1,84: calcolo della
   > G2, non pre-registrato) anche il verdetto a taglia fissa sarebbe stato CLOSED.

6. *"limite basso stabile su 10 semi"*. Vero, ma il CLOSED lo decide il limite **alto**, che l'esito non ripete sui
   semi. Aggiungere: *"il limite alto, che e' quello che decide, va da +0,92 a +1,03 (`verifiche_g2.py`)"*. Nello
   stesso punto: le sedute escluse sono 2 su 1.539 **per ciascun indice**.

7. *"l'effetto della grandezza pubblicata non c'e'"*. Con la forza del test: *"un effetto della grandezza pubblicata,
   o della sua meta', e' escluso al 95%"*.

**Da aggiungere.** I due controlli del meccanismo (pre-registrazione §7) non compaiono nella voce. Il §7 obbliga a
scriverli solo se vanno contro entrambi; qui uno va contro e uno a favore, e nessuno dei due si distingue da zero.
Vale la pena scriverlo, perche' e' l'altro posto in cui si puo' vedere "uno spiraglio":
> **I due controlli del meccanismo** (intervalli da `verifiche_g2.py`, 12/10). L'effetto non cresce col movimento:
> la stima va al contrario (solo segno lordo +1,02 pb nei giorni di movimento piccolo, −1,23 nei grandi; grande meno
> piccolo −2,25 [−5,08; +0,57]). L'inversione il giorno dopo ha il segno atteso (−3,59 pb [−8,75; +1,24]). Nessuno
> dei due si distingue da zero: il meccanismo non lascia impronte misurabili in questo campione.

Il paragrafo "Revisione" va aggiornato: la passata indipendente ora c'e', ed e' questa.

## 5. Il 2022, misurato

**Ammissibile**: usa solo il train, che e' aperto; non cambia regola, parametro, strumento o filtro; non sceglie
nulla per proseguire (LIFECYCLE §3). Corregge per la selezione un descrittivo che l'esito gia' stampa, quindi puo'
solo rendere la lettura piu' prudente.

**Come.** Nullo del test (§5 della pre-registrazione): la taglia di ogni giorno resta al suo posto, la direzione
viene da un altro giorno, con lo stesso spostamento circolare per i due indici. Ho usato **tutti i 1.497 spostamenti
ammessi** (da 20 a n−21 sedute), non un campione: non c'e' errore Monte Carlo. Seme 42 solo per ricostruire il
braccio casuale dell'esito. Volatilita' e taglia di ogni anno restano dove sono: sotto il nullo il 2022 resta l'anno
turbolento che era. Per ogni spostamento ricalcolo i sette divari annui e prendo il migliore. "In errori standard"
vuol dire: divario medio dell'anno diviso per (deviazione standard dei divari giornalieri di quell'anno / radice
delle sedute dell'anno).

Il 2022 reale: +4,89 pb su 251 sedute, deviazione giornaliera 43,1 pb (la piu' alta dei sette anni), errore standard
2,72, quindi **+1,80 errori standard**.

| domanda | quota sotto il nullo |
|---|---|
| **(a)** l'anno migliore dei sette ha un divario ≥ +4,89 pb | **6,7%** (99 su 1.497) |
| **(b)** l'anno migliore, in errori standard del suo anno, e' ≥ +1,80 | **23,8%** (355 su 1.497) |
| per confronto: il 2022 guardato da solo, come se fosse stato scelto prima | 2,3% in pb; 3,7% in errori standard |
| la cella migliore fra le 12 di sottocampione dell'esito e' ≥ +1,80 errori standard | **31,1%** (465 su 1.497) |
| anni positivi 2 o meno su 7 (il lato opposto) | 21,4% |

Sotto il nullo l'anno migliore vale in mediana +2,45 pb (95esimo percentile +5,37), cioe' +1,36 errori standard
(95esimo +2,42).

**Lettura.** In punti base un anno migliore cosi' capita una volta su quindici; messo sulla scala della sua
volatilita', una volta su quattro. La differenza fra i due numeri e' tutta nella volatilita' del 2022: solo gli anni
turbolenti possono produrre un numero cosi' grande in pb (sotto il nullo l'anno migliore in pb e' il 2020 o il 2022
nel 46% dei casi). Nessuno dei due numeri scende sotto il 5%, mentre il 2022 guardato da solo ci scende: e'
esattamente l'effetto della selezione. Il dubbio di Matteo e' fondato nei numeri: uno spiraglio cosi' il caso lo
lascia in un test su quattro guardando solo gli anni, e in quasi uno su tre guardando tutte le celle dell'esito.

**Quanti tagli contiene l'esito.** Oltre alla primaria, 19 posti in cui poteva comparire qualcosa: **12 celle di
sottocampione** (7 anni, 3 terzili di movimento, 2 strumenti) e **7 letture alternative** dell'intero campione
(taglia fissa, senza tetto, ablazione della taglia, inversione il giorno dopo, due overlay, runs test). Per gli anni
l'esito stampa due metriche, divario e netto. Le 12 celle, in errori standard: 2020 −0,81; 2021 −1,39; 2022 +1,80;
2023 +0,13; 2024 −0,90; 2025 −1,08; 2026 −0,59; movimento piccolo +1,26, medio +0,01, grande −0,98; SPX500 −1,02;
NAS100 −0,31. Nessuna supera 2 in valore assoluto; una cella estrema almeno quanto il 2022, in un verso o nell'altro,
esce nel 53,6% dei casi.

## 6. Un'ipotesi condizionale nata dai descrittivi ha un percorso? Oggi no

Cosa dice [STRATEGY_LIFECYCLE](../STRATEGY_LIFECYCLE.md):
- **§3**: una condizione aggiunta e' un filtro. Conta come trial **della stessa famiglia**, ed e' "il piu' pericoloso".
- **§4**: e' legittima solo se il razionale la prevedeva **senza guardare quali trade hanno perso**. Il test
  operativo ("l'avresti fatta se il backtest fosse stato positivo?") una condizione nata dall'anno migliore non lo passa.
- **§4bis**: il formato sarebbe l'ablazione pre-registrata, con e senza la condizione.
- Tutto questo vale per una famiglia **viva e con budget**. Qui il budget era 1 su 1, la pre-registrazione (§8) dice
  che ogni modifica dopo l'esito e' una pre-registrazione nuova, e la famiglia e' CLOSED.
- **§7**: una CLOSED riapre solo con evidenza esterna nuova. Un'ipotesi nata dai nostri descrittivi sono "gli stessi
  dati riorganizzati": non riapre. La regola "stessa grandezza = stessa famiglia" impedisce di farla passare per una
  famiglia nuova.
- **Il forward non e' un percorso previsto** per questo caso: nel documento segue un LEAD (§5) o il capitale (§8bis).
  Per una famiglia CLOSED non e' scritto che si possa registrare un forward senza passare dal §7.

**Costo**, se un giorno il §7 fosse soddisfatto: il §7 non lo dice. Per analogia col §3 e col contatore sarebbe una
pre-registrazione nuova, almeno 1 trial sul cumulato della famiglia (da 1 a 2), uno slot esterno del trimestre (il
2026-Q4 e' pieno), e il train 2020-2026 non potrebbe piu' validare una condizione suggerita dai suoi stessi descrittivi.

**Buchi del protocollo**, che segnalo senza colmare:
1. Il §7 dice **quando** una CLOSED riapre, non **come** si contabilizza: budget, contatore, slot, quali dati restano
   usabili, se un holdout mai aperto si eredita.
2. Non c'e' una regola sul **forward di una famiglia CLOSED**: se sia ammesso senza il §7, e quanto costi.
3. Le **previsioni del meccanismo scritte prima** (la scheda H1 ne aveva tre) sono entrate nel test come descrittivi
   senza soglia e senza incertezza. Il protocollo non dice quanto vale, dopo, una previsione dichiarata prima ma non
   pre-registrata come test.
4. Non c'e' un posto dove **parcheggiare** un'ipotesi nata da un descrittivo, con il suo stato e la sua scadenza. Senza,
   puo' tornare fra qualche mese come idea nuova.

## 7. Contabilita' e holdout

`python -m core.trial_ledger --check` (12/10): nessun problema. Famiglia CLOSED, 1 trial su 1, 0 round, holdout
`sigillato`, gate finale forward. Pre-registrazioni esterne del 2026-Q4: 3 di 2-3, quota piena. La famiglia non passa
da `prop-lab`.

**Holdout: risulta mai aperto**, per quanto si puo' verificare. `holdout_aperto` e' `null` in tutti e tre i commit;
non esiste un esito dell'holdout; lo script apre l'holdout solo con un train che dice PASSA, e il train dice CLOSED;
nel repo i tre file europei sono nominati solo dallo scaricamento, dai controlli meccanici dell'11/10 (letti: non
calcolano rendimenti) e dallo script del test. **Non si puo' verificare** che nessuno li abbia letti con codice non
salvato: i file sono fuori da git e nessun artefatto lo registra. In questa revisione non li ho aperti.

## 8. Debito di protocollo

1. **La storia prima dell'approvazione non e' in git.** Bozza, due passate G1 e correzioni entrano nel repo in un
   solo commit, quello di approvazione. Per il candidato A (08/10) la bozza era stata committata prima.
2. **La ripetizione sui semi copre il limite che non decide.** L'esito ripete il limite basso; un CLOSED dipende da
   quello alto. Va ripetuta la grandezza che decide ciascun verdetto possibile.
3. **I descrittivi escono senza incertezza**: anni, terzili, inversione sono stime puntuali, senza errore standard e
   senza una lettura che tenga conto di quante celle si guardano. E' cosi' che nasce "l'annata buona".
4. **Le guardie congelano meno di quello che il test usa**: `core/` e `tests/` non sono nell'elenco dei percorsi
   congelati; l'esito non riporta le versioni delle librerie (il calendario di borsa viene da un pacchetto esterno).
5. **Nessun controllo positivo sui dati reali per un verdetto negativo.** Il confronto col secondo fornitore copre
   solo il 2025-2026. Andrebbe chiesto alla G1 quando l'esito possibile e' un CLOSED.
6. **Tassonomia** (gia' segnalato l'08/10): il §5 di LIFECYCLE non ha NON DIMOSTRATO, e CLOSED indica sia l'etichetta
   di un test sia lo stato di una famiglia.
7. I quattro buchi del §6.

Nota pratica: i due script nuovi stanno in `analysis/ultima_mezzora/`, che e' un percorso congelato. Da ora
`esegui_test.py` rifiuta di lanciare qualunque stadio. E' coerente con una famiglia chiusa; una riapertura per §7
dovrebbe tenerne conto.
