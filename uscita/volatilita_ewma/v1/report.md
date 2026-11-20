---
strumento: volatilita_ewma
versione: 1
tipo: prima consegna
data: 2026-11-20
fonte: trad, famiglia volatilita (DECISIONS 2026-11-20 e 2026-11-20 (2))
---

# volatilita_ewma v1 — previsione della varianza di domani e dei prossimi 5 giorni

**In breve.** Una previsione, fatta alla chiusura di oggi, di quanto si muovera' il prezzo domani e nei prossimi 5
giorni di borsa, con l'EWMA a λ = 0,94 (lo standard RiskMetrics). In piu', come **opzione esplorativa** per gli indici
azionari, un GJR-GARCH. **Nessuna delle due ha una proprieta' dimostrata fuori campione**: il test di `trad` non ha
avuto la potenza per dirlo (punto 1). L'EWMA esce perche' e' lo standard, e nei nostri dati nulla di piu' complesso
si e' dimostrato migliore. Nessuna promessa di profitto (punto 3).

---

## 1. Lo strumento e la proprieta' misurata

**Cosa produce.** Per ogni giorno di borsa t, con i soli prezzi fino alla chiusura di t:
- `h1`: la varianza prevista del rendimento di domani, in %² (radice quadrata = deviazione standard giornaliera in %);
- `h5`: la somma delle varianze previste dei prossimi 5 giorni (per l'EWMA vale sempre 5 × `h1`).

**La proprieta' che `trad` voleva misurare**: una perdita QLIKE (la misura standard dell'errore di una previsione di
varianza; piu' bassa = meglio) piu' bassa di un benchmark semplice, su un periodo mai visto (holdout, dal 2024-11-11).
I modelli candidati erano GARCH, GJR, EGARCH e quattro modelli a regimi (HMM), contro l'EWMA come benchmark.

**Esito: test non concluso, nessuna proprieta' dimostrata** ([DECISIONS 2026-11-20 e 2026-11-20 (2)](../../../decisioni/DECISIONS.md),
[pre-registrazione §11](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md)). Prima di aprire
l'holdout si e' verificato, su dati simulati con un vantaggio noto, se il test lo avrebbe riconosciuto: lo riconosceva
nel 18,9% dei casi per i GARCH e nel 2,0% per i regimi, contro l'80% richiesto (misura del 20/11/2026, commit
`5dcee68`). Un test che vede un vantaggio vero una volta su cinque non puo' dare un verdetto, quindi l'holdout **non e'
stato aperto** e resta sigillato. Non e' un verdetto sui modelli: con due anni di holdout e 18 domande per gruppo di
modelli, vantaggi di questa taglia non si vedono strumento per strumento.

**Perche' esce comunque l'EWMA.** (a) E' lo standard dichiarato prima di ogni misura come benchmark ([pre-registrazione
§4](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md)). (b) Ha un solo parametro, fissato dalla
letteratura e non stimato sui nostri dati, quindi non c'e' nulla da sovra-adattare, e gira con le sole chiusure
giornaliere. **Non** esce perche' sia la previsione migliore: nei dati di sviluppo (punto 2, 18 coppie strumento ×
orizzonte) e' la migliore in **1 coppia su 18** (EURUSD a h = 5). Batte la media di lungo periodo in 18 su 18 e la
persistenza ("domani come oggi") in 15 su 18; perde contro GJR, GARCH, la media delle tre varianti GARCH e la
combinazione GJR + regimi in 11 su 18, e contro l'HAR (che richiede dati a 5 minuti) in 10 su 18. Sono
**descrizioni**, non test.

**Perche' il GJR solo come opzione esplorativa.** Nei dati di sviluppo ha una perdita piu' bassa dell'EWMA su tutti e
5 gli indici azionari, a entrambi gli orizzonti (10 coppie su 10), e sul WTI a h = 1; piu' alta su oro, argento ed
euro. La scelta "GJR sugli indici" e' stata fatta **dopo** aver visto queste perdite, quindi quei dati non la
confermano. E il test non l'avrebbe vista: nel controllo positivo, con la volatilita' degli indici, riconosceva un
vantaggio simulato nel 9-23% dei casi per coppia (`esiti/pos_garch.json`, commit `5dcee68`); per la differenza
osservata sull'SPX500 a h = 1 (0,080, contro una differenza minima rilevabile di 0,151) la potenza stimata e' circa
il 17% (formula di `potenza.py` sui numeri di `esiti/sviluppo.json`, voce `mde`). La ragione teorica e' nota (sugli indici i ribassi alzano la volatilita' piu'
dei rialzi, e il GJR lo modella), ma resta un'ipotesi. Anche il GARCH semplice sta sotto l'EWMA nelle
stesse 11 coppie, con perdite molto vicine al GJR; sugli indici la previsione piu' bassa e' spesso la media delle tre
varianti GARCH (6 coppie su 10). Nel contatore la scelta e' annotata come selezione dopo l'esito: 10 serie gia'
contate, confermabile solo su dati non visti.

## 2. Su quali dati e' stato provato

| Voce | Valore |
|---|---|
| Strumenti | SPX500, NAS100, DOW, RUSSELL, DAX, XAUUSD, XAGUSD, WTI, EURUSD |
| Fonte | barre a 5 minuti Dukascopy (prezzi bid), non incluse nel pacchetto (licenze personali) |
| Periodo | 2015-01-02 → 2024-11-08 (RUSSELL dal 2018-08-09) |
| Prime previsioni | dopo 1.000 giorni di stima: dal 2018-11-05 (EURUSD) al 2018-12-20 (indici USA); RUSSELL dal 2022-07-29 ([`esiti/pacchetto_ewma_v1.json`](../../../magazzino/registro/codice/volatilita/esiti/pacchetto_ewma_v1.json)) |
| Bersaglio | varianza realizzata dalle barre a 5 minuti (piu' la notte per gli indici), [pre-registrazione §3](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md) |

Perdite QLIKE medie nei dati di sviluppo, a h = 1 (fonte:
[`esiti/sviluppo.json`](../../../magazzino/registro/codice/volatilita/esiti/sviluppo.json), corsa del 19/11/2026 sul
commit `86fcdae`, riepilogo rifatto sul `0d53ba1`). Si confrontano solo dentro una riga: il livello cambia da uno
strumento all'altro. L'ultima colonna dice quale delle 12 previsioni provate ha la perdita piu' bassa.

| Strumento | EWMA | GJR | HAR (dati a 5 min) | persistenza | media lungo periodo | la piu' bassa |
|---|---|---|---|---|---|---|
| SPX500 | 1,002 | 0,922 | 0,949 | 1,042 | 1,735 | media GARCH |
| NAS100 | 1,547 | 1,466 | 1,479 | 1,572 | 1,992 | media GARCH |
| DOW | 0,900 | 0,839 | 0,911 | 0,935 | 1,674 | media GARCH |
| RUSSELL | 1,606 | 1,598 | 1,602 | 1,684 | 1,786 | GJR |
| DAX | 1,053 | 1,000 | 1,014 | 1,163 | 1,501 | GJR |
| XAUUSD | 0,765 | 0,801 | 0,726 | 0,773 | 0,949 | HAR |
| XAGUSD | 2,172 | 2,234 | 2,133 | 2,166 | 2,492 | HAR |
| WTI | 2,830 | 2,802 | 2,937 | 2,728 | 4,148 | persistenza |
| EURUSD | −0,674 | −0,639 | −0,681 | 0,091 | −0,479 | HAR |

A h = 5 il GJR resta sotto l'EWMA sugli indici; sugli altri l'EWMA sta sotto il GJR, la persistenza batte l'EWMA solo
sul WTI, l'HAR su oro e argento, e l'EWMA e' la piu' bassa di tutte sull'EURUSD. Le differenze fra EWMA e GJR sono piccole rispetto al rumore: per l'SPX500 a h = 1 la
differenza minima che il test sull'holdout di due anni avrebbe visto all'80% era 0,15 (stesso file, voce `mde`);
quella osservata nello sviluppo e' 0,08.

**Questi dati non sono una conferma indipendente.** Chi rifa' il confronto sugli stessi strumenti fino al 2024-11-08
ritrova questi numeri, non una prova nuova.

**Regola sui dati futuri.** `trad` ridisegnera' il test con meno ipotesi (per esempio il GJR sugli indici) e lo fara'
su **dati futuri**, raccolti dopo la sua pre-registrazione ([DECISIONS 2026-11-20 (2)](../../../decisioni/DECISIONS.md)).
Oggi la regola non vincola nulla: usare il pacchetto su qualunque dato, e riportare cio' che si trova, e' libero. Dal
giorno di quella pre-registrazione, che sara' scritto nella tabella Consegne di [uscita/README.md](../../README.md),
fino alla fine del test che la pre-registrazione fissa:
- non si riporta a `trad`, **in nessun canale** (repo, chat, voce), un risultato **per modello** calcolato su quei dati:
  perdite, confronti EWMA contro GJR o altri, impressioni del tipo "il GJR va meglio";
- un test di strategia costruito sullo strumento si registra nel contatore col **solo verdetto aggregato**, senza il
  confronto fra modelli;
- se un confronto arriva lo stesso, si registra in `DECISIONS.md` quali strumenti e orizzonti tocca (non il numero), e
  quelle coppie escono dal test sui dati futuri.

Un problema del codice si riporta sempre.

## 3. Limiti noti e quando non usarlo

- **Accuratezza non e' profitto.** Usare la volatilita' per dimensionare le posizioni migliora le code e i drawdown,
  ma lo Sharpe solo per azioni e credito (Harvey et al. 2018), e fuori campione peggiora in 72 strategie su 103
  (Cederburg et al. 2020). Il passaggio da strumento a strategia va testato, e **una regola costruita su questo
  strumento e' una strategia**: il suo test si registra nel contatore unico di `trad`.
- **L'EWMA reagisce in ritardo e non torna alla media.** Dopo uno shock alza la previsione e la tiene alta per
  settimane (meta' del peso se ne va in circa 11 giorni); la previsione a 5 giorni e' piatta (5 × domani), quindi dopo
  un picco sovrastima, in un periodo calmo sottostima. Il GJR invece torna verso la sua media di lungo periodo.
- **La scala dipende dal bersaglio.** Da soli prezzi di chiusura il pacchetto prevede la varianza da chiusura a
  chiusura. Se la si confronta con una varianza realizzata intraday, va riscalata con c_t (punto 4), altrimenti la
  QLIKE premia chi prevede piu' alto.
- **Dati.** Una riga per giorno di borsa, senza buchi lunghi e senza giorni ripetuti. I salti di rollover dei CFD su
  futures (nel WTI Dukascopy 16 salti nel 2015-2024) gonfiano la previsione per settimane: vanno tolti prima. Il
  pacchetto non conosce i calendari di borsa.
- **I giorni degli strumenti a 24 ore** (oro, argento, petrolio, euro): in `trad` il giorno va dalle 17:00 di New York
  alle 17:00 del giorno dopo, e il movimento del fine settimana e della pausa non entra. Una chiusura giornaliera del
  broker di solito ha un altro orario e include il fine settimana: le perdite della tabella non si trasferiscono a quei
  dati, e il lunedi' la previsione sottostima.
- **Altri strumenti o timeframe**: non provati. Su barre intraday la stagionalita' oraria va tolta prima.
- **GJR**: servono almeno 1.000 giorni di rendimenti; si ristima ogni 5 giorni (piu' lento dell'EWMA) e, se una stima
  non converge, riusa i parametri della precedente (colonna `gjr_ripiego`).

## 4. Come si usa

Requisiti: `numpy`, `pandas`; `arch` solo per il GJR; `pytest` per i test. Provato con Python 3.12, numpy 2.4.4,
pandas 3.0.2, arch 8.0.0.

**Da riga di comando**, con un CSV di chiusure giornaliere (colonne di default `time` e `close`):

```
python volatilita_ewma.py prezzi_giornalieri.csv
python volatilita_ewma.py prezzi_giornalieri.csv --gjr --uscita previsioni.csv
```

Stampa la previsione per domani e per i prossimi 5 giorni; con `--uscita` scrive tutte le righe: `r` (rendimento in
%), `ewma_h1`, `ewma_h5`, `ewma_vol_giorno_pct`, `ewma_vol_annua_pct` (radice di 252 × `h1`), e con `--gjr` anche
`gjr_h1`, `gjr_h5`, `gjr_ripiego`.

**Da Python:**

```python
import volatilita_ewma as V
r = V.rendimenti(df["close"])          # rendimenti log in %
p = V.previsioni_ewma(r)               # colonne h1, h5; NaN nei primi 100 giorni (minimo 75)
g = V.previsioni_gjr(r)                # esplorativo, solo indici azionari
```

**Leggere i numeri.** `h1` = 1,44 significa una deviazione standard prevista dell'1,2% per domani; con 252 giorni
l'anno, circa il 19% annuo. La riga t si usa **dopo la chiusura di t**: e' la previsione per t+1.

**Con una varianza realizzata intraday** `v` (somma dei quadrati dei rendimenti a 5 minuti, piu' la notte per gli
indici), sullo stesso calendario di `r`: `c = V.riscala(r, v)` e poi `previsione * c`. Per misurare, la previsione
della riga t va confrontata coi giorni **successivi**: `V.qlike(f, V.bersaglio(v, 1))` per `h1`,
`V.qlike(f, V.bersaglio(v, 5))` per `h5` (tolte le righe NaN: sono la fine dei dati e le finestre che toccano un giorno con `v` mancante). Confrontarla con `v` dello stesso giorno premia chi copia
oggi.

**Insieme ad altri strumenti.** Lo strumento dice *quanto* si muove il prezzo, non *dove*. Usi tipici da testare:
dimensione della posizione inversa alla deviazione standard prevista, ampiezza di stop e target in multipli di essa,
filtro sui giorni di volatilita' prevista estrema. Ognuno e' una strategia da testare (punto 3).

**Test:** `python -m pytest test_volatilita_ewma.py` (9 test: ricorsione, nessun dato futuro per EWMA e GJR,
uguaglianza con `arch`, riscalamento, QLIKE, bersaglio allineato, controlli degli input).

## 5. Versione e tipo

**v1, prima consegna** (20/11/2026). Il codice riproduce quello usato da `trad` nella corsa di sviluppo
(`magazzino/registro/codice/volatilita/modelli.py`): sui nove strumenti di sviluppo, 12.732 origini, lo scarto massimo
fra le previsioni del pacchetto e quelle di `trad` (prima di c_t) e' **0** per l'EWMA e per il GJR, a entrambi gli
orizzonti; il GJR ripiega sui parametri precedenti in 10 origini dell'EURUSD, come in `trad`
([`esiti/pacchetto_ewma_v1.json`](../../../magazzino/registro/codice/volatilita/esiti/pacchetto_ewma_v1.json), script
`verifica_pacchetto.py`, 20/11/2026, commit `00a36b8`; dopo, nel codice e' cambiata solo `bersaglio`, che non entra
nelle previsioni). Vale per i dati costruiti come in `trad` (punto 3, giorni a 24
ore).

**Il ciclo di ritorno** ([uscita/README.md](../../README.md)): al massimo 5 versioni. Una **correzione** (un bug,
un'applicazione sbagliata) e' gratis. Una **modifica fatta dopo aver visto i vostri esiti** (un altro λ, un altro
modello, un filtro) conta come trial, e i dati che l'hanno motivata non servono piu' a giudicarla. Ogni ritorno si
registra in `decisioni/DECISIONS.md`.
