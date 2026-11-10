# A5 — Audit dei verdetti early-stage: **protocollo, scritto prima di guardare**

> Scritto e committato **prima** di aprire il codice dei motori. Serve a impedire che l'audit
> diventi una caccia selettiva ai difetti solo dove il risultato non ci era piaciuto.

---

## Perche' adesso

Il 2026-09-18 il binario del copier mentore ha prodotto **quattro** difetti in un giorno.
Nessuno era nel metodo, tutti nei **dati o nelle convenzioni**, e ognuno ha cambiato il verdetto:

1. timestamp indietro di 1h → look-ahead di prezzo;
2. uso dei **file corti** mentre nel repo c'erano quelli lunghi;
3. `parse.py` con nomi di file cablati che ignorava l'ultimo export;
4. la correzione del punto 1 applicata **due volte** → +2h, fill sistematicamente tardivi.

**Nessuno dei quattro e' stato trovato dal metodo.** Tre sono usciti da una domanda dell'utente
sulla copertura dei dati, uno da un controllo casuale mentre si cercava altro.

I verdetti early-stage — **livelli, NXT, ORB, TSMOM** e i minori — sono stati prodotti dalle
**stesse mani con le stesse abitudini**, mesi prima che esistessero `coverage.py`, `resolve_trade`
e la disciplina sul fill ottenibile. Sono la fondazione su cui rifiutiamo le idee nuove: se uno e'
sbagliato, stiamo usando un errore come filtro.

## L'asimmetria che governa tutto questo audit

Sono quasi tutti **NO-GO**. Questo cambia quale difetto e' pericoloso:

| difetto | effetto su un NO-GO | pericolo |
|---|---|---|
| gonfia il risultato (look-ahead, fill fantasma) | rende il NO-GO **piu' difficile** da dichiarare | **basso** — se nonostante il regalo non passa, il NO-GO regge a maggior ragione |
| deprime il risultato (fill tardivi, costi doppi, baseline regalato) | **produce** il NO-GO | **ALTO** — abbiamo buttato qualcosa di vivo |
| toglie potenza (n piccolo, sd alta, campione censurato) | produce un NO-GO **vuoto** | **ALTO e subdolo** — "non rifiutato" letto come "refutato" |

> 🔧 **La regola che ne discende**: qui si cercano prima di tutto i difetti che **peggiorano** il
> risultato e quelli che **tolgono potenza**. E' l'opposto dell'istinto, ed e' esattamente la
> lezione del quarto difetto di oggi: **un numero peggiore sembra prudenza e passa senza controlli.**

Un NO-GO falso e' **invisibile e definitivo**: nessuno lo scopre mai, perche' la strategia non
esiste piu' e non genera dati che lo contraddicano. E' l'unico errore del workspace che non si
autocorregge.

---

## La lista di controllo — 9 punti, applicati **uguali a tutti**

Per ogni famiglia si risponde **si' / no / non applicabile**, con il numero dove esiste.

| # | controllo | cosa lo fa fallire |
|---|---|---|
| **1** | **Potenza dichiarata** | Esiste un MDE calcolato (`2,80·σ/√n`)? Se l'effetto cercato e' **sotto** l'MDE, il verdetto e' *"non misurato"*, non *"refutato"* |
| **2** | **Copertura dei dati** | La finestra e' dichiarata nell'output? Il motore usa il file **lungo** o quello corto? Ci sono piu' file candidati? |
| **3** | **Allineamento temporale** | Prezzi e segnali/eventi sono sullo stesso orologio? La correzione e' applicata **una volta sola**? |
| **4** | **Fill ottenibile** | L'ingresso usa un prezzo disponibile **dopo** l'istante di decisione? Ritardi di conferma (K barre) inclusi? |
| **5** | **Baseline random risk-matched** | Esiste? E' calcolato con le **stesse** convenzioni, costi e campione della strategia? |
| **6** | **Convenzioni di risoluzione** | tie / gap oltre lo stop / priorita' BE / timeout: dichiarate? Il motore ha una `resolve` **propria** diversa dalle altre? |
| **7** | **Costi simmetrici** | Applicati a strategia **e** baseline nella stessa unita'? |
| **8** | **Censura del campione** | Occupazione (una posizione per strumento), filtri che tolgono osservazioni **non a caso**, sopravvivenza |
| **9** | **Il verdetto corrisponde al numero** | Cio' che e' scritto in DECISIONS e' quello che il codice ha prodotto? Soglie dichiarate **prima**? |

## Esiti possibili, definiti ora

| esito | significato | conseguenza |
|---|---|---|
| ✅ **CONFERMATO** | nessun difetto rilevante, o solo difetti che rendevano il test **piu' generoso** | il NO-GO resta, con piu' forza di prima |
| ⚠️ **NON MISURATO** | il test non aveva potenza per l'effetto cercato | il verdetto **non e' una refutazione**: la casella torna **vuota**, non chiusa. Non autorizza a rifarlo subito |
| 🔴 **DA RIFARE** | difetto che deprime il risultato o invalida il confronto | verdetto **annullato**. La famiglia torna allo stato **precedente al test**, ⚠️ **non** riceve un trial gratis |
| 📋 **DIFETTO INININFLUENTE** | difetto reale ma che non puo' aver cambiato il segno | si annota, il verdetto resta |

## Cosa **non** conta come difetto (dichiarato ora, per non barare dopo)

- **"Il risultato era vicino alla soglia"** — una soglia dichiarata prima si rispetta. Non e' un difetto.
- **"Con parametri diversi funzionava"** — e' ricerca di parametri, e costa un trial. Non e' un audit.
- **"Il campione era piccolo"** da solo — conta **solo** se tradotto in un MDE (punto 1).
- **"Oggi lo faremmo diversamente"** — se la differenza non cambia il segno, e' un 📋, non un 🔴.

## Contabilita' dei trial

L'audit e' **caccia ai bug: 0 trial** ([[feedback_correggere_non_e_cercare]]).
Se un verdetto viene annullato, la famiglia **non riceve un trial nuovo**: torna allo stato in cui
era prima, con il suo budget residuo di allora. Altrimenti "annullare un verdetto" diventerebbe un
modo per rigenerare tentativi.

## Perimetro

Quattro famiglie principali dichiarate in A5 — **livelli (384 trial), NXT/FADE, ORB, TSMOM** — piu'
le minori toccate di passaggio se emergono difetti della stessa forma: stagionalita' TOM,
mean-reversion vol, griglia a numero tondo, London Breakout.

**Ordine**: si parte da quella il cui NO-GO ha **chiuso piu' spazio di ricerca** — i livelli, che da
soli hanno consumato 384 trial e hanno chiuso un libro intero.
