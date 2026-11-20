---
tipo: referto
stato: "seconda passata (commit abb830e): PASSA CON NOTE, 0 bloccanti, 4 note; prima passata BLOCCA (4 bloccanti, 7 riserve), 20/11/2026"
aggiornato: 2026-11-20
oggetto: "uscita/volatilita_ewma/v1/ (report.md, volatilita_ewma.py, test_volatilita_ewma.py), non ancora committati, branch strumenti/volatilita su e0fa9f7"
misure: "nessun dato di prezzo caricato. Numeri ricalcolati da magazzino/registro/codice/volatilita/esiti/sviluppo.json (commit 0d53ba1), pos_garch.json e pos_hmm.json (commit 5dcee68); prove del codice su serie sintetiche; date delle prime previsioni dal calendario exchange_calendars 4.13.2"
---
# Revisione del pacchetto `volatilita_ewma` v1 prima della consegna ai soci

Fonti lette: [DECISIONS](../../../decisioni/DECISIONS.md) 2026-11-20, 2026-11-19 (2), 2026-11-19, 2026-11-09;
[pre-registrazione](../documenti/VOLATILITA_PREREGISTRATION.md) §4, §5, §7.7, §8, §11; [uscita/README](../../../uscita/README.md);
[STRATEGY_LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md); contatore (`python -m motore.core.trial_ledger`,
`--check` esce con 0). Righe citate: `report.md` e `volatilita_ewma.py` del pacchetto, nello stato del 20/11 ore 16:20.

```
VERDETTO DEL GUARDIANO: BLOCCA

BLOCCANTI (4)

  B1 [fonte delle decisioni] Le decisioni del 20/11 su cui poggia la consegna non stanno in DECISIONS.md.
     · report.md:6 e :29 citano "DECISIONS 2026-11-20"; quella voce (DECISIONS.md:14-26) dice ancora "Lo stato
       della famiglia e il seguito (test forward, disegno con meno ipotesi, pacchetto EWMA per i soci) li decide
       Matteo". Il contatore dice "stato della famiglia da decidere (Matteo)"; uscita/README.md: "Nessuna consegna
       al 09/11/2026", tabella Consegne vuota.
     · Perche' invalida: il pacchetto e la sua regola dell'holdout citano come fonte una voce che non contiene ne'
       la consegna ne' la regola. Un socio (o una sessione futura) che segue il link trova "da decidere". La regola
       dell'holdout, in particolare, vincola trad e i soci: se non e' in DECISIONS non esiste.
     · Riparazione: voce DECISIONS 2026-11-20 (2) con le decisioni (a)-(e), la regola dell'holdout completa (B3) e
       la contabilita' (sezione CONTABILITA'); riga nella tabella Consegne di uscita/README.md (strumento, v1, data,
       tipo, ruolo del destinatario); nota del contatore aggiornata ("in ridisegno"); poi il frontmatter del report
       punta a quella voce.

  B2 [contraddizione di metodo] "trad tiene quei dati non visti per un test futuro con meno ipotesi" (report.md:85)
     promette un uso dell'holdout che le regole in vigore non consentono.
     · STRATEGY_LIFECYCLE §8ter P1: le varianti nate dopo un esito sono "esplorative: niente verdetto, niente
       holdout"; P3: diventano confermative solo con "dati forward non visti"; H4: cio' che e' pronto dopo usa "dati
       forward successivi all'apertura". Pre-registrazione §7.7: un ridisegno dopo il passo 3 "conta trial (C1) ed e'
       post-esito"; un nodo uscito si testa "su dati forward successivi all'apertura"; §8: "Mai sull'holdout".
     · Un disegno "con meno ipotesi" scritto adesso nasce dopo la corsa di sviluppo e dopo i positivi: se sceglie,
       per esempio, GJR contro EWMA sugli indici, e' esattamente la selezione S6/P1 (report.md:43-46 lo ammette).
       Alla lettera, quel test non puo' usare l'holdout del 2024-11-11.
     · Perche' invalida: il report impegna i soci a una restrizione motivata da un uso che oggi e' vietato; e se il
       ridisegno usasse l'holdout senza una decisione esplicita, il suo verdetto violerebbe P1/P3.
     · Riparazione (decide Matteo, PRIMA della consegna): o (i) una voce DECISIONS che ammette un holdout sigillato e
       mai aperto come "dati non visti" per una pre-registrazione nuova della stessa famiglia, con l'argomento (il
       caricatore giorni.py non legge oltre il 2024-11-10; il contatore ha holdout_aperto = null), la quota d'errore
       (solo dalle quote riservate dei nodi usciti, §8: la famiglia resta al 5%) e il prezzo dichiarato (circa l'80%
       del blocco precede il cutoff del modello, pre-registrazione §4; gli eventi del blocco sono pubblici); oppure
       (ii) il report toglie la promessa e dice che il test futuro usera' dati forward. In entrambi i casi la
       restrizione ai soci resta utile: in (ii) protegge i dati dal 2026-11-11.

  B3 [protezione dell'holdout] La regola di report.md:85-88 non basta, anche dopo B2.
     Cosa manca:
     a. Ambito. Vieta di "riportare a trad confronti fra modelli (perdite medie)". Non copre: impressioni
        qualitative ("sugli indici il GJR ha tenuto meglio ad aprile 2025"), chat e messaggi a Matteo fuori dal repo,
        e soprattutto i test di STRATEGIA costruiti sullo strumento, che lo stesso report (righe 94-95, 140-142)
        chiede di registrare nel contatore di trad: un backtest di sizing con EWMA e con GJR sul 2025 e' un
        confronto fra modelli sull'holdout, misurato in R invece che in QLIKE. Chi scrive il ridisegno (Matteo, e
        Claude in sessione) non deve vederlo per modello.
     b. Violazione. Nessuna conseguenza scritta prima. Se la si decide dopo aver ricevuto il numero, e' una scelta
        post-esito come le altre.
     c. Chi registra e dove. Nessuno. Il ritorno dei soci passa da DECISIONS (report.md:157) e da
        decisioni/Da distillare/: proprio i due canali da cui un confronto sull'holdout entrerebbe in trad.
     d. Durata. "Finche' trad non avra' aperto l'holdout": se il ridisegno non arriva, vale per sempre.
     · Perche' invalida: l'unico valore del blocco sigillato e' che nessuno lo abbia guardato attraverso i modelli.
       Un confronto ricevuto prima della nuova pre-registrazione la contamina senza lasciare traccia, e il verdetto
       del ridisegno non sarebbe piu' su dati non visti.
     · Riparazione, nella voce DECISIONS di B1 e in una frase del report:
       - ambito: nessun risultato per modello (perdite, R, drawdown, impressioni) su dati dal 2024-11-11, verso
         trad o verso chi scrive il ridisegno, in qualunque canale; i test di strategia sul periodo si registrano nel
         contatore con il solo verdetto aggregato, senza scomposizione per modello di volatilita';
       - violazione, decisa ora: chi riceve il confronto lo registra in DECISIONS (data, ruolo, coppie modello ×
         strumento × orizzonte toccate, senza riportare il numero); quelle coppie non possono essere ipotesi
         confermative sull'holdout e passano ai dati forward (P3); la pre-registrazione del ridisegno elenca in un
         campo apposito tutte le informazioni sull'holdout gia' ricevute (come la P4 della scheda d'ingresso dall'hub,
         STRATEGY_LIFECYCLE §8);
       - chi registra: Matteo, che e' il punto di contatto coi soci; un materiale dei soci sulla volatilita' che
         arriva in Da distillare/ si controlla per questo prima di leggerlo;
       - durata: fino all'apertura dell'holdout o alla chiusura della famiglia, con una data di revisione.

  B4 [affermazione selettiva] La ragione (b) per l'EWMA (report.md:37-41) cita solo i confronti che l'EWMA vince.
     · Da esiti/sviluppo.json (commit 0d53ba1), su 12 previsioni e riferimenti: l'EWMA ha la QLIKE piu' bassa in
       1 coppia su 18 (EURUSD h5). La battono GARCH, GJR, media delle tre varianti GARCH e combinazione a 3 regimi
       in 11/18, l'HAR in 10/18, la combinazione a 2 regimi in 9/18, l'EGARCH in 8/18. L'HAR, riferimento
       pre-registrato, e' il migliore su XAUUSD e XAGUSD ai due orizzonti e su EURUSD a h1, cioe' proprio dove il
       report dice che il GJR perde; la tabella (righe 65-75) non ha la colonna HAR.
     · Anche la frase sul GJR (righe 43-45) omette il WTI a h1, dove il GJR batte l'EWMA (2,802 contro 2,830): sono
       11 coppie su 18, non "10 indici su 10, peggio altrove". Sugli indici la previsione migliore e' la media delle
       tre varianti GARCH in 6 coppie su 10; a h5 il GARCH semplice batte il GJR su SPX500, NAS100 e DOW.
     · Perche' invalida: il punto 1 del README e il §8ter chiedono di non dire piu' dell'evidenza. Ogni frase e' vera,
       ma la scelta delle colonne fa leggere al socio che l'EWMA regge contro le alternative, e i dati di sviluppo
       dicono il contrario. La ragione vera e sufficiente e' (a)+(c): standard dichiarato prima, zero parametri.
     · Riparazione: o si toglie (b) come ragione, o la si completa con una riga ("nello sviluppo l'EWMA e' la
       previsione migliore in 1 coppia su 18; l'HAR, che richiede la varianza intraday, la batte in 10") e si
       aggiunge il WTI h1 alla frase sul GJR.

RISERVE (7)

  R1 [numero col senso sbagliato] report.md:46-47: "il test aveva la potenza del 18,9% per vederla". Il 18,9% e'
     il rifiuto medio per coppia del controllo positivo su un processo GJR simulato, con i sigma di tutti e nove gli
     strumenti (pos_garch.json); sulle serie con il sigma degli indici era 9-23%. Per il vantaggio osservato nello
     sviluppo sull'SPX500 h1 (0,080) con l'MDE di 0,151, la potenza del test pre-registrato e' circa il 17%
     (calcolo di questa revisione: Φ(0,080/0,0395 − 2,99)). La conclusione regge, la frase va detta cosi'.
     Impatto: nessuno sul verdetto, solo sulla lettura.
  R2 [uso del codice] report.md:138 "Per misurare: V.qlike(f, v)" non dice l'allineamento: la riga t prevede t+1,
     quindi f[t] va con v[t+1] (e a h5 con la somma di v[t+1..t+5]). Senza lo spostamento la QLIKE premia chi pesa
     r_t² (persistenza, EWMA) e il confronto e' sbagliato. Va scritto anche nella docstring di qlike.
  R3 [strumenti a 24 ore] La tabella e la riproduzione (righe 149-152, solo SPX500) valgono per il r_t di trad:
     per oro, argento, petrolio ed euro il giorno va dalle 17:00 New York e il rendimento a cavallo della pausa e
     del fine settimana e' escluso (pre-registrazione §3). Un CSV di chiusure giornaliere di un broker ha un altro
     confine di giorno e include quel rendimento: le perdite della tabella non si trasferiscono. Il report (righe
     99-104) cita il rollover del WTI ma non il confine del giorno.
  R4 [verifica non conservata] "Scarto massimo 0 ... verifica del 20/11/2026 sul commit e0fa9f7" (righe 149-152)
     non ha uno script ne' un esito nel repo: non e' ripetibile. Qui non e' rifatta (nessun dato di prezzo). Fatto
     su serie sintetiche: l'EWMA del pacchetto e quello di trad (EWMAVariance di arch sul blocco di 1.000 giorni)
     coincidono con scarto relativo 0,0; il GJR del pacchetto ricalca modelli.py riga per riga (seme
     [20261113, t0, 1], partenze, regola di ripiego, fix e forecast sul blocco esteso). Conviene salvare lo script e
     l'esito in magazzino/registro/codice/volatilita/esiti/ col commit.
  R5 [gestione errori] (i) con meno di 101 righe la riga di comando stampa "nan" senza avviso (provato con 50
     righe sintetiche); (ii) `riscaldamento` e' un argomento pubblico: sotto 75 la riga t usa l'avvio, che contiene
     r[0..74], cioe' dati futuri per t < 75 (volatilita_ewma.py:39-58); va imposto >= 75 o scritto; (iii) qlike non
     controlla v, riscala non controlla la divisione per zero. Nel GJR i limiti di varianza di arch
     (variance_bounds) usano varianza e massimo del blocco esteso, fino a 4 giorni dopo l'origine: canale teorico
     che non scatta in pratica (il test del pacchetto e il passo 1 del §7 a tolleranza 1e-10 passano); lo si dichiara.
  R6 [versioni] report.md:111 "Python 3.11+": provato con Python 3.12, numpy 2.4.4, pandas 3.0.2, arch 8.0.0
     (pre-registrazione §2; numpy e pandas confermati qui). Scrivere le versioni provate, non un minimo non provato.
  R7 [stato della famiglia] Con la decisione (e), la pre-registrazione resta APPROVATA ma nessun nodo resta e
     l'holdout non si apre con questo testo (§7.7). Il frontmatter e la nota del contatore devono dirlo ("in
     ridisegno; nessuna apertura prevista da questa pre-registrazione"), perche' APPROVATA da sola fa credere a una
     sessione futura che il passo 8 sia ancora eseguibile.

VERIFICATO E A POSTO (16)
  - tabella QLIKE h1 (righe 65-75): 36 valori su 36 coincidono con sviluppo.json (commit 0d53ba1), grassetti sul minimo di riga
  - 18/18 sulla media di lungo periodo; 15/18 sulla persistenza (perde XAGUSD h1, WTI h1 e h5); GJR e GARCH sotto l'EWMA nelle stesse 11 coppie; frase su h5 (righe 77-78) corretta
  - MDE dell'SPX500 h1 = 0,1514 (variante migliore gjr, n_eff 496); differenza osservata 0,080
  - 18,9% (17,3-20,5%) e 2,0% da pos_garch.json e pos_hmm.json, commit 5dcee68, esito FALLISCE
  - date: sviluppo fino al 2024-11-08, RUSSELL dal 2018-08-09 (§11, punto 4); prime previsioni dal calendario: XNYS 2018-12-20, XETR 2018-12-10, RUSSELL 2022-07-29 (manca la fonte nel report: citare il calcolo)
  - 16 salti di rollover del WTI (pre-registrazione §3)
  - aritmetica: 0,94^100 = 0,2%; dimezzamento 11,2 giorni; h1 = 1,44 → 1,2% al giorno, 19,05% l'anno
  - EWMA: la riga t usa solo r[0..t] (con riscaldamento >= 75); uguale ad arch EWMAVariance
  - GJR: parametri stimati su r[t0-999..t0], filtro coi parametri congelati per t0..t0+4; nessun rendimento dopo t entra nella previsione di t (salvo R5)
  - unita': rendimenti log in %, varianze in %², annualizzazione √(252·h1), coerenti fra codice e report
  - 7 test verdi (rilanciati qui: 7 passed); riga di comando: ordine delle date, duplicati, prezzi mancanti gestiti (provato su CSV sintetici)
  - nessun dato grezzo, nome, chat, orario o numero di conto nei tre file; i prezzi restano fuori ("licenze personali")
  - nessuna promessa di profitto; "una regola costruita sullo strumento e' una strategia" e il rimando al contatore ci sono (§8ter)
  - "nessuna proprieta' dimostrata" e "GJR scelto dopo aver visto le perdite" dichiarati in testa (righe 13-15, 45-46)
  - i 5 punti di uscita/README presenti (proprieta' ed esito; dati e non-indipendenza; limiti; uso e comandi; versione)
  - holdout: holdout_aperto = null nel contatore; contatore --check senza problemi

ESECUZIONE
  - fill non ottenibili: non applicabile. Strumento (binario strumenti, §8ter), nessun ordine e nessuna regola di trade; baseline casuale in R e DSR non si applicano (Checklist 10)

CONTABILITA'
  - trial di questa consegna: 0. EWMA e' il benchmark (non contato in C1); le serie GJR sono gia' fra le 54 del nodo garch; la verifica di riproduzione ricalcola serie esistenti
  - GJR "sugli indici" come opzione esplorativa: e' una selezione fatta dopo l'esito (S6, P1). Non calcola serie nuove, quindi non aggiunge trial (contarle di nuovo raddoppierebbe le stesse 10 serie), ma P2 chiede che stia nel contatore: nota nella sottofamiglia garch ("selezione post-esito GJR × 5 indici × h1, h5, 10 serie gia' contate nei 54, 20/11; esplorativa: confermabile solo su dati non visti, P3") e la stessa frase in DECISIONS
  - cumulato famiglia: 126 (54 GARCH, 72 HMM, premio 0), invariato
  - il ridisegno: stessa grandezza = stessa famiglia (volatilita), pre-registrazione nuova, post-esito; conta ogni serie calcolata (C1); consuma un round (round_rifinitura 0 → 1 di 3); quota d'errore solo dalle quote riservate dei nodi usciti (2,5% + 1,25% + 1,25%), famiglia al 5% (§8)
  - holdout famiglia: sigillato (dal 2024-11-11, mai aperto); il suo uso per il ridisegno dipende da B2
  - budget pre-reg: binario strumenti, nessuna quota trimestrale
  - registro prop-lab coerente col contatore: si' (core.trial_ledger --check, uscita 0)

RISCHIO E PROP
  - non toccati dal pacchetto

DEBITO DI PROTOCOLLO
  - uscita/README non dice cosa fa un pacchetto quando la sua famiglia ha un holdout sigillato: la regola di B3 andrebbe li', valida per ogni pacchetto, non solo in questo report
  - nessuno script conserva la prova "pacchetto = codice di trad" (R4): per i prossimi pacchetti, un test di equivalenza versionato accanto al codice dello studio
```

## Note per chi corregge

- B1, B2 e B3 si chiudono con **una** voce DECISIONS (decisioni del 20/11 + scelta su B2 + regola dell'holdout) e
  con le due righe di report che la citano. B2 e' una scelta di Matteo: questa revisione non dice quale delle due.
- B4 si chiude in due righe del report.
- Dopo le correzioni basta una seconda passata sul solo report e sulla voce DECISIONS; il codice non va rivisto
  salvo R5 (ii).

## Seconda passata (20/11/2026, commit `abb830e`, branch `strumenti/volatilita`)

Solo sulle correzioni: commit `00a36b8` (codice, test, `verifica_pacchetto.py`) e `abb830e` (DECISIONS 2026-11-20 (2),
contatore, pre-registrazione §11, `uscita/README.md`, report, mappa). Nessun dato di prezzo caricato: lo scarto 0 si
legge da `esiti/pacchetto_ewma_v1.json`, non e' rifatto.

```
VERDETTO DEL GUARDIANO: PASSA CON NOTE

BLOCCANTI (0)

STATO DEI BLOCCANTI DELLA PRIMA PASSATA
  B1 chiuso. DECISIONS 2026-11-20 (2) contiene le decisioni (a)-(e), la regola, la contabilita' e la correzione di
     B2; riga nella tabella Consegne; nota e fonti del contatore aggiornate (--check: uscita 0); aggiunta datata nel
     §11 e metrica_corrente della pre-registrazione ("nessuna apertura prevista"); mappa e _modifiche (da_rivedere).
  B2 chiuso. Matteo sceglie i dati futuri, successivi alla pre-registrazione del ridisegno, come dicono §7.7, §8 e
     P3; il report non promette piu' l'holdout (report.md:93-94). Una fonte nuova acquistata e' una deviazione da P3
     da valutare ogni volta col gatekeeper: vedi N3.
  B3 chiuso. Report.md:93-103 e DECISIONS: ambito (ogni canale, comprese le impressioni), test di strategia col solo
     verdetto aggregato, violazione decisa prima (registro in DECISIONS delle coppie, non del numero; le coppie
     escono dal test), chi registra (Matteo), durata (dalla data della pre-registrazione alla fine del test),
     elenco di cio' che e' gia' stato ricevuto nella pre-registrazione. Spostare l'inizio alla data della
     pre-registrazione e' coerente con B2: prima di quella data i dati non sono dati del test.
  B4 chiuso. Report.md:37-44: l'EWMA non esce perche' e' la migliore (1 coppia su 18); confronti completi (11/18
     contro GJR, GARCH, media GARCH, comb3; 10/18 contro l'HAR); tabella con l'HAR e la colonna "la piu' bassa",
     9 righe su 9 coincidono con sviluppo.json; WTI h1 nella frase sul GJR (report.md:47).

STATO DELLE RISERVE DELLA PRIMA PASSATA
  R1 chiusa: 9-23% per coppia sui sigma degli indici (pos_garch.json, s0-s4) e circa 17% per l'SPX500 h1 (report.md:49-52).
  R2 chiusa: bersaglio(v, h) somma v[t+1..t+h], provato da test_bersaglio_allineato; uso corretto nel report.md:159-162.
  R3 chiusa: limite sui giorni a 24 ore (report.md:122-125) e "vale per i dati costruiti come in trad" (:178).
  R4 chiusa: verifica_pacchetto.py, esito sul commit 00a36b8: scarto relativo massimo 0,0 su 9 strumenti, EWMA e
     GJR, h1 e h5, 12.732 origini (somma ricontrollata); 10 ripieghi GJR sull'EURUSD = 2 blocchi non convergenti
     di sviluppo.json × 5 origini. Il codice del pacchetto non cambia fra 00a36b8 e abb830e (cambia solo il report):
     la verifica vale per il codice consegnato. Lo script legge i dati col caricatore giorni.py, fermo al 2024-11-10.
  R5 chiusa: riscaldamento < 75 e' un errore (volatilita_ewma.py:56-57); controlli su v in qlike e riscala; c_t NaN
     con denominatore 0; la riga di comando si ferma con <= 100 rendimenti; canale dei limiti di arch nel docstring.
  R6 chiusa: versioni provate (report.md:132-133, docstring).
  R7 chiusa: metrica_corrente e §11 della pre-registrazione, nota del contatore.

NOTE (4) — nessuna blocca la consegna
  N1 [fonte] report.md:6, frontmatter: "fonte: ... (DECISIONS 2026-11-20)". La voce che decide la consegna e' la
     2026-11-20 (2), come gia' a report.md:29 e :94.
  N2 [registro delle consegne] uscita/README.md:24-26 dice che la riga della tabella Consegne registra il commit
     da cui recuperare una versione cancellata, ma la tabella (:38-40) non ha la colonna del commit. Va aggiunta,
     col commit che arriva su main, prima che la v2 cancelli la v1.
  N3 [fonte nuova di dati] DECISIONS 2026-11-20 (2) ammette come deviazione da P3 "una fonte nuova di dati mai
     visti (strumenti o periodi mai toccati)". Il periodo 2024-11-11 → 2026-11-10 non e' mai stato toccato dalla
     pipeline: un feed acquistato su quel periodo (per esempio i futures CME) riaprirebbe da un'altra porta lo
     stesso blocco che la voce dichiara "sigillato senza uso", e sul quale la regola per i soci oggi non vale (i
     loro ritorni su quel periodo arrivano liberamente fino alla pre-registrazione). Alla prima valutazione di una
     fonte nuova va detto se quel periodo conta come "mai toccato"; se si', le informazioni ricevute nel frattempo
     sul periodo entrano nell'elenco della pre-registrazione, e la contaminazione da cutoff (circa l'80% del blocco
     precede il 2026-05-31, pre-registrazione §4) va dichiarata come nel §4.
  N4 [codice] bersaglio() usa una somma cumulata: un solo v mancante rende NaN tutte le righe successive, e
     "tolte le righe NaN" (report.md:161) le scarta senza avviso. qlike non tace (rifiuta i NaN), ma chi filtra
     prima perde dati senza saperlo. Basta una riga nel docstring o un controllo su v.

VERIFICATO E A POSTO (seconda passata)
  - tabella h1 con HAR e "la piu' bassa": 54 valori, 9 etichette, coincidono con sviluppo.json (commit 0d53ba1)
  - frase su h5 (report.md:85-86): persistenza solo sul WTI, HAR su oro e argento fra i non indici, EWMA la piu' bassa sull'EURUSD
  - prime origini nel report.md:65 = prima_origine di pacchetto_ewma_v1.json (EURUSD 2018-11-05, indici USA 2018-12-20, RUSSELL 2022-07-29)
  - 9 test verdi (rilanciati qui); contatore --check uscita 0; cumulato 126 invariato
  - nessun nome di socio, chat, orario, numero di conto o dato grezzo nei file del pacchetto e nel README d'uscita
  - "selezione post-esito GJR sugli indici, 10 serie gia' contate, 0 trial" coerente in DECISIONS, contatore, §11 e report

ESECUZIONE
  - non applicabile (binario strumenti, nessun ordine)

CONTABILITA'
  - trial della consegna: 0 · cumulato famiglia: 126 · round: 0 di 3 (il ridisegno portera' a 1)
  - holdout della famiglia: sigillato, senza uso (DECISIONS 2026-11-20 (2)); holdout_aperto = null
  - budget pre-registrazioni: binario strumenti, nessuna quota trimestrale
  - registro prop-lab coerente col contatore: si'
```
