---
tipo: analisi
stato: fuori dal nostro binario
aggiornato: 2026-10-09
fonte_dati: "codice Pine v6 in fondamenti_tecnici/_sorgenti/indicatore_ob_bigbeluga_2026-10-09.pine (copia integrale, licenza intatta)"
nota: "Matteo (09/10): sulla strategia con questo indicatore lavora il socio; noi non spendiamo trial. Se il socio torna con regole e operazioni registrate, si riparte dal §4 (si misura la persona)."
---
# Indicatore "Volume-Trend Order Block Engine" (BigBeluga): intake

> Portato dal socio il 09/10: non e' suo, l'ha trovato nella libreria pubblica di TradingView. E' il primo script
> smistato con le sei domande di [10_indicatori_tecnici §10](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md).
> Il codice e' stato **letto riga per riga**; nessun backtest, nessun dato, 0 trial.

> **Seguito (11/10):** il socio e' tornato con regole complete e un backtest, non con operazioni registrate. La lettura
> e' in [vtob_socio_intake_2026-10-11](vtob_socio_intake_2026-10-11.md).

## 1. Cosa fa (input → output)

Tre pezzi, piu' un segnale.

- **Filtro di tendenza** (un Supertrend modificato). La banda e' il punto medio della barra ± 3,5 volte la **media semplice
  dell'ampiezza** (massimo − minimo) delle ultime 50 barre: non e' l'ATR vero, quindi ignora i gap. La banda si muove solo
  nella direzione della tendenza, e la tendenza gira quando la chiusura la attraversa. Uscita: tendenza +1 o −1.
- **Zona** (chiamata "order block"). Quando si conferma un **minimo di swing** (piu' basso delle 7 barre prima e delle 7
  dopo) mentre la tendenza e' rialzista, la zona parte dal minimo fra apertura e chiusura di quella barra e scende di
  un'ampiezza media. In ribasso e' lo stesso, dai massimi. C'e' **una zona attiva alla volta**; una nuova nasce solo se non
  si sovrappone alla precedente, e la zona si cancella quando una barra intera la oltrepassa dal lato sbagliato.
- **"Buy %" / "Sell %"**. E' la quota di volume delle **barre verdi** (chiusura ≥ apertura) sul totale delle 8 barre che
  vanno dal minimo di swing alla sua conferma. **Non e' volume di acquisto**: e' il colore della candela pesato per il
  volume, che su CFD e forex e' volume di tick.
- **Segnale**: una croce di acquisto quando, **a barra chiusa**, il minimo della barra torna sopra il bordo alto della zona
  dopo esserci stato dentro o sotto, con "Buy %" ≥ 50%, escludendo la barra in cui si conferma un pivot e quella in cui
  gira la tendenza. Per la vendita e' lo stesso, specchiato.
- **Cosa non fa**: **niente stop, niente obiettivo, niente uscita**. E' un indicatore, non una strategia. Per testarlo
  dovremmo completare la regola noi, e ogni scelta sarebbe un grado di liberta' nostro.

## 2. Le sei domande

| domanda | risposta | esito |
|---|---|---|
| 1. Quale grandezza misura? | tre: **tendenza** (Supertrend), **livelli** (zona da un pivot), **volume** (approssimato dal colore delle candele). Il segnale e' "ritorno su un livello nella direzione della tendenza" | stessa grandezza di due famiglie gia' chiuse: `livelli` (l'order block come zona vera e' stato testato in v1 e v3, nessun vantaggio sul caso: DECISIONS 2026-07-06 e 2026-07-07 (v3)) e `nxt` (ritorno in tendenza su un livello dello swing: con fill ottenibili la continuazione **perde**, DECISIONS 2026-09-18 (5); famiglia KILL). Per la regola dell'08/10 **non e' una famiglia nuova** |
| 2. Ridisegna? | **il segnale no**: il pivot si usa solo dopo la conferma; nessun `request.security`, `varip` o `timenow`; i segnali richiedono `barstate.isconfirmed`. **Il disegno si'**: la zona parte dalla barra del minimo, 7 barre prima che si potesse conoscere | segnale causale, grafico ingannevole (§3) |
| 3. Prezzi veri? | si', su candele normali | da chiedere: su che tipo di grafico lo guarda (con Heikin Ashi i riempimenti sono falsi) |
| 4. Parametri scelti guardando il grafico? | sono i valori di default dell'autore (50; 3,5; 7; 50%) | da chiedere: li ha cambiati? Dopo aver guardato cosa? |
| 5. Chi paga? | nessuna risposta nel codice. La narrativa e' quella degli order block ("ordini istituzionali lasciati nella zona"), aneddotica ([[02_liquidita_orderflow]]) | **pattern**: nessuna classe |
| 6. Quante varianti provate? | sconosciuto | da chiedere: quanti indicatori ha scorso nella libreria prima di questo |

## 3. Tre illusioni nel codice (perche' sul grafico sembra funzionare)

1. **Ogni zona sembra rispettata appena nasce, per costruzione.** Il riquadro e' disegnato dalla barra del minimo di swing,
   e per definizione di pivot le 7 barre successive hanno tutte minimi piu' alti. Sul grafico storico ogni zona rialzista
   mostra subito 7 barre che "rimbalzano" sopra di lei: e' la definizione del pivot, non una reazione. Dal vivo la zona
   compare 7 barre dopo, quando quel tratto e' gia' passato. E' il "disegno nel passato" della documentazione di
   TradingView, e il tasso di base mancante del modulo 10 (§8.2, §8.5).
2. **"Buy %" probabilmente supera il 50% per costruzione.** Le 8 barre del calcolo sono il minimo e le 7 barre che, per
   definizione, non scendono sotto di lui: ci si aspetta che siano piu' spesso verdi. Se e' cosi', il filtro "Buy % ≥ 50%"
   e' quasi sempre vero e non filtra niente. ⚠️ **E' un'attesa, non una misura**: si conta a 0 trial (quota delle zone che
   passano il filtro), come insegna [[feedback_soglia_normalizzata_cancella_distinzione]].
3. **Senza volume il filtro passa sempre, in silenzio.** Se il simbolo su TradingView non ha volume, la quota vale 0,5 e
   la soglia di default (50%) e' soddisfatta. Da chiedere: quale simbolo e quale fornitore di dati.

Due note di codice, senza effetto con le impostazioni di default ma da sapere: il segnale di acquisto **non controlla che
la zona attiva sia rialzista** (con la cancellazione spenta puo' nascere su una zona ribassista oltrepassata), e una zona
rialzista **resta attiva anche dopo che la tendenza gira**, quindi un segnale di acquisto puo' arrivare in tendenza
ribassista.

## 4. Verdetto proposto: CHIUSO all'intake, 0 trial (decide Matteo)

- **Non e' una famiglia nuova**: misura grandezze di famiglie gia' chiuse (regola dell'08/10, DECISIONS 2026-10-08 (3)).
- **Non riapre niente**: per riaprire `livelli` o `nxt` serve evidenza esterna nuova (STRATEGY_LIFECYCLE §7), e non c'e'.
  La ricerca dell'08/10 non ha trovato studi ne' repository che confrontino zone da pivot con zone casuali.
- **Non ha un "chi paga"**: e' un pattern ([09_fonti_di_vantaggio](../../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md) §4).
- Le differenze dal nostro test (zona disegnata diversamente, filtro di tendenza, conferma del rimbalzo, filtro sul
  volume) sono **parametri e filtri dentro la stessa grandezza**: testarle sarebbe "ritocchiamo e riproviamo" sopra 384
  trial nulli.
- **Cosa lo riaprirebbe**: un risultato pubblicato, con campione, di zone da pivot nella direzione della tendenza contro
  zone casuali alla stessa distanza; oppure il **track record del socio**, se lo usa per operare (si misura la persona,
  non lo strumento).

## 5. Cosa chiedere al socio

- Lo usa per operare o lo sta solo guardando? Se opera: da quando, quante operazioni, dove le annota.
- Su che simbolo, timeframe, fornitore di dati e tipo di grafico.
- Ha cambiato le impostazioni? Quali, e dopo aver guardato cosa?
- Dove mette stop e obiettivo, visto che l'indicatore non li da'.
- Quanti altri indicatori ha provato prima di questo.

## 6. Licenza

Creative Commons **BY-NC-SA 4.0**: si puo' condividere e modificare citando l'autore, con la stessa licenza e **non per
scopi commerciali**. Il codice e' catturato in `_sorgenti/` con l'intestazione intatta, come la licenza richiede. Un port in
Python sarebbe un'opera derivata con la stessa licenza. Usarlo dentro un servizio a pagamento (per esempio un canale di
segnali a pagamento) rischia di essere uso commerciale: da verificare prima, se il socio ci pensa.

## Collegamenti

- [10_indicatori_tecnici](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md): §10 (smistamento), §8 (illusioni), §9 (lista).
- [BACKLOG_RICERCA §H](../BACKLOG_RICERCA.md): H4, stessa conclusione per la pitchfork.
- [LEVEL_RESEARCH_PREREGISTRATION](../LEVEL_RESEARCH_PREREGISTRATION.md), [STRATEGY_LIFECYCLE](../STRATEGY_LIFECYCLE.md) §3 e §7.
