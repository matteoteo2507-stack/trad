---
strumento: volatilita_ewma
versione: 1
tipo: prima consegna
data: 2026-11-20
fonte: trad, famiglia volatilita (DECISIONS 2026-11-20)
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

**Esito: test non concluso, nessuna proprieta' dimostrata** ([DECISIONS 2026-11-20](../../../decisioni/DECISIONS.md),
[pre-registrazione §11](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md)). Prima di aprire
l'holdout si e' verificato, su dati simulati con un vantaggio noto, se il test lo avrebbe riconosciuto: lo riconosceva
nel 18,9% dei casi per i GARCH e nel 2,0% per i regimi, contro l'80% richiesto (misura del 20/11/2026, commit
`5dcee68`). Un test che vede un vantaggio vero una volta su cinque non puo' dare un verdetto, quindi l'holdout **non e'
stato aperto** e resta sigillato. Non e' un verdetto sui modelli: con due anni di holdout e 18 domande per gruppo di
modelli, vantaggi di questa taglia non si vedono strumento per strumento.

**Perche' esce comunque l'EWMA.** (a) E' lo standard dichiarato prima di ogni misura come benchmark ([pre-registrazione
§4](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md)). (b) Nei dati di sviluppo (punto 2) ha una
perdita piu' bassa della media di lungo periodo in 18 coppie strumento × orizzonte su 18 e della persistenza ("domani
come oggi") in 15 su 18: e' una **descrizione**, non un test. (c) Ha un solo parametro, fissato dalla letteratura e non
stimato sui nostri dati, quindi non c'e' nulla da sovra-adattare.

**Perche' il GJR solo come opzione esplorativa.** Nei dati di sviluppo ha una perdita piu' bassa dell'EWMA su tutti e
5 gli indici azionari, a entrambi gli orizzonti (10 coppie su 10), e piu' alta su oro, argento ed euro. La scelta
"GJR sugli indici" e' stata fatta **dopo** aver visto queste perdite, quindi quei dati non la confermano, e il test
aveva la potenza del 18,9% per vederla. La ragione teorica e' nota (sugli indici i ribassi alzano la volatilita' piu'
dei rialzi, e il GJR lo modella), ma resta un'ipotesi. Anche il GARCH semplice sta sotto l'EWMA nelle
stesse coppie, con perdite molto vicine al GJR.

## 2. Su quali dati e' stato provato

| Voce | Valore |
|---|---|
| Strumenti | SPX500, NAS100, DOW, RUSSELL, DAX, XAUUSD, XAGUSD, WTI, EURUSD |
| Fonte | barre a 5 minuti Dukascopy (prezzi bid), non incluse nel pacchetto (licenze personali) |
| Periodo | 2015-01-02 → 2024-11-08 (RUSSELL dal 2018-08-09) |
| Prime previsioni | dopo 1.000 giorni di stima: novembre-dicembre 2018 (RUSSELL: 2022-07-29) |
| Bersaglio | varianza realizzata dalle barre a 5 minuti (piu' la notte per gli indici), [pre-registrazione §3](../../../magazzino/registro/documenti/VOLATILITA_PREREGISTRATION.md) |

Perdite QLIKE medie nei dati di sviluppo, a h = 1 (fonte:
[`esiti/sviluppo.json`](../../../magazzino/registro/codice/volatilita/esiti/sviluppo.json), corsa del 19/11/2026 sul
commit `86fcdae`, riepilogo rifatto sul `0d53ba1`). Si confrontano solo dentro una riga: il livello cambia da uno
strumento all'altro.

| Strumento | EWMA | GJR | persistenza | media lungo periodo |
|---|---|---|---|---|
| SPX500 | 1,002 | **0,922** | 1,042 | 1,735 |
| NAS100 | 1,547 | **1,466** | 1,572 | 1,992 |
| DOW | 0,900 | **0,839** | 0,935 | 1,674 |
| RUSSELL | 1,606 | **1,598** | 1,684 | 1,786 |
| DAX | 1,053 | **1,000** | 1,163 | 1,501 |
| XAUUSD | **0,765** | 0,801 | 0,773 | 0,949 |
| XAGUSD | 2,172 | 2,234 | **2,166** | 2,492 |
| WTI | 2,830 | 2,802 | **2,728** | 4,148 |
| EURUSD | **−0,674** | −0,639 | 0,091 | −0,479 |

A h = 5 l'ordine e' lo stesso sugli indici (GJR sotto l'EWMA); sugli altri l'EWMA sta sotto il GJR, e la persistenza
batte l'EWMA solo sul WTI. Le differenze fra EWMA e GJR sono piccole rispetto al rumore: per l'SPX500 a h = 1 la
differenza minima che il test sull'holdout di due anni avrebbe visto all'80% era 0,15 (stesso file, voce `mde`);
quella osservata nello sviluppo e' 0,08.

**Questi dati non sono una conferma indipendente.** Chi rifa' il confronto sugli stessi strumenti fino al 2024-11-08
ritrova questi numeri, non una prova nuova.

**Regola dell'holdout (dal 2024-11-11).** `trad` tiene quei dati non visti per un test futuro con meno ipotesi. Usare il
pacchetto su dati recenti, per lavorare, e' libero. Si chiede solo di **non riportare a `trad` confronti fra modelli**
(EWMA contro GJR, contro altri, perdite medie) calcolati su dati dal 2024-11-11 in poi, finche' `trad` non avra' aperto
l'holdout: un numero visto prima li renderebbe dati gia' visti. Un problema del codice si riporta sempre.

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
- **Altri strumenti o timeframe**: non provati. Su barre intraday la stagionalita' oraria va tolta prima.
- **GJR**: servono almeno 1.000 giorni di rendimenti; si ristima ogni 5 giorni (piu' lento dell'EWMA) e, se una stima
  non converge, riusa i parametri della precedente (colonna `gjr_ripiego`).

## 4. Come si usa

Requisiti: Python 3.11+, `numpy`, `pandas`; `arch` solo per il GJR (provato con la 8.0.0);
`pytest` per i test.

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
p = V.previsioni_ewma(r)               # colonne h1, h5; NaN nei primi 100 giorni
g = V.previsioni_gjr(r)                # esplorativo, solo indici azionari
```

**Leggere i numeri.** `h1` = 1,44 significa una deviazione standard prevista dell'1,2% per domani; con 252 giorni
l'anno, circa il 19% annuo. La riga t si usa **dopo la chiusura di t**: e' la previsione per t+1.

**Con una varianza realizzata intraday** `v` (somma dei quadrati dei rendimenti a 5 minuti, piu' la notte per gli
indici), sullo stesso calendario di `r`: `c = V.riscala(r, v)` e poi `previsione * c`. Per misurare: `V.qlike(f, v)`.

**Insieme ad altri strumenti.** Lo strumento dice *quanto* si muove il prezzo, non *dove*. Usi tipici da testare:
dimensione della posizione inversa alla deviazione standard prevista, ampiezza di stop e target in multipli di essa,
filtro sui giorni di volatilita' prevista estrema. Ognuno e' una strategia da testare (punto 3).

**Test:** `python -m pytest test_volatilita_ewma.py` (7 test: ricorsione, nessun dato futuro per EWMA e GJR,
uguaglianza con `arch`, riscalamento e QLIKE).

## 5. Versione e tipo

**v1, prima consegna** (20/11/2026). Il codice riproduce quello usato da `trad` nella corsa di sviluppo
(`magazzino/registro/codice/volatilita/modelli.py`): sull'SPX500 di sviluppo, 1.482 origini, lo scarto massimo fra le
previsioni del pacchetto e quelle di `trad` (prima di c_t) e' **0** per l'EWMA e per il GJR, a entrambi gli orizzonti
(verifica del 20/11/2026 sul commit `e0fa9f7`).

**Il ciclo di ritorno** ([uscita/README.md](../../README.md)): al massimo 5 versioni. Una **correzione** (un bug,
un'applicazione sbagliata) e' gratis. Una **modifica fatta dopo aver visto i vostri esiti** (un altro λ, un altro
modello, un filtro) conta come trial, e i dati che l'hanno motivata non servono piu' a giudicarla. Ogni ritorno si
registra in `decisioni/DECISIONS.md`.
