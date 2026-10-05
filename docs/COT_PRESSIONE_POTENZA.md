---
tipo: referto
stato: chiusa_non_testabile
aggiornato: 2026-10-03
decisione: "DECISIONS 2026-10-03 (3): strada A, chiusa a 0 trial (non testabile a potenza utile fuori campione, non operabile alla nostra scala; non falsificata)"
metrica_corrente: "MDE Sharpe fuori campione (dati liberi) 0,92-1,16 (dati liberi) contro Sharpe pubblicati 0,61 e ~0,79 lordo → sotto potenza in ogni scenario"
nota: "0 trial. Nessun rendimento calcolato sui nostri prezzi, nessun segnale COT guardato: solo aritmetica sui numeri pubblicati e conteggio delle date dei report"
---
# COT: il premio di copertura e' testabile a potenza utile? (passo 0, 0 trial)

> Nato dal brainstorming del 03/10 ([DECISIONS 2026-10-03 (2)](../DECISIONS.md)): *"premi per il rischio
> invece di tempismo"*. Tutte le regole di tempismo del repo sono cadute; l'unico vantaggio rimasto in A1
> era il tempo in mercato. Il premio di copertura e' il candidato della letteratura che risponde a
> quella domanda: chi si copre (produttori, consumatori) paga un premio a chi si prende il rischio.
>
> **Regola, la stessa di A1 punto 2 e di B2:** si confronta l'MDE con lo Sharpe **pubblicato**
> (scenario ottimistico, con dentro la maledizione del vincitore) e con **meta'** di quello (scenario
> onesto). Se l'MDE supera anche lo scenario ottimistico, il test non si apre: *"non testabile a potenza
> utile"*, **non falsificato**.

## 1. Le fonti e le grandezze (lette il 03/10, testo completo)

| fonte | disegno | campione | risultato |
|---|---|---|---|
| **Fan, Fernandez-Perez, Fuertes, Miffre**, *J. Futures Markets* 40(4), 2020 ([testo libero](https://openaccess.city.ac.uk/id/eprint/23283/)) | long-short sulla pressione speculativa (media delle posizioni a 52 settimane), ribilanciamento mensile | 10/1993-05/2018, 43 commodity (84 futures in tutto) | commodity: **+4,12% annuo, t 2,62, Sharpe 0,61** (Tab. 2). Gli autori notano che nella seconda meta' del campione il premio delle commodity si e' **gradualmente indebolito** (§3.2, Fig. 1) |
| **Kang, Rouwenhorst, Tang**, *J. Finance* 2020 ([versione 2017](https://www.carloalberto.org/wp-content/uploads/2018/11/Tale-of-two-premiums-JAN-2017.pdf)) | due premi di segno opposto: **liquidita'** (variazione settimanale delle posizioni, Q) e **assicurazione** (pressione media a 52 settimane) | 01/1994-11/2014, 26 commodity | la pressione **grezza non predice** (t −0,43); quella **media a 52 settimane si'** (t 3,35, regressioni Fama-MacBeth). Premio di liquidita' sui quintili di Q: 0,67% in 20 giorni, "circa 9% annuo" (Tab. 4) |
| Basu, Miffre, *J. Banking & Finance* 2013 | long-short su pressione di copertura | — | Sharpe superiori al long-only (solo abstract letto) |
| Bessembinder 1992; de Roon, Nijman, Veld 2000 | test della backwardation normale | 22 e 20 contratti | citati dalle fonti sopra, **non letti** |

⚠️ **La trappola del fill nel premio di liquidita'.** Il 9% annuo di Kang-Rouwenhorst-Tang include i
**giorni 1-4**, quando le posizioni del martedi' **non sono ancora pubbliche** (il report esce il venerdi'
sera): +0,21%, t 3,04, cioe' un terzo dei 67 punti base. La parte ottenibile parte dal giorno 5:
+0,30% nei giorni 5-10 (t 3,62) e +0,15% nei giorni 11-20 (t 1,23). E' lo stesso campanello del
fill fantasma ([Step 3bis](QUANT_REVIEW_PROTOCOL.md)): il numero di copertina non e' tutto incassabile.

## 2. Quanti anni ci sono davvero fuori campione

Il COT legacy (`data/cache/free/cot_legacy_fut.parquet`, scaricato il 03/10) ha **24 report l'anno**
dal 1986 al 1991, 31 nel 1992 e **52 dal 1993**. Prima del 1993 il disegno settimanale e' impossibile;
quello mensile si'.

I futures rettificati per il roll (pysystemtrade, gratis) si fermano al **2024-03-28**: il premio vive
nel rendimento di roll, quindi i CFD Dukascopy non servono.

| finestra fuori dal campione delle fonti | anni | disegno possibile |
|---|---|---|
| **dopo** Fan et al. (06/2018 → 03/2024, gratis) | **5,8** | mensile |
| dopo Fan et al., col feed a pagamento (G9) fino a 09/2026 | 8,3 | mensile |
| **prima** di Fan et al. (01/1987 → 09/1993: serve un anno di storia per la media a 52 settimane) | 6,7 | solo mensile ⚠️ probabilmente **gia' visto** da Bessembinder 1992 e de Roon 2000 (campioni non verificati) |
| dopo Kang et al. (12/2014 → 03/2024, gratis) | **9,3** | settimanale |
| dopo Kang et al., col feed a pagamento fino a 09/2026 | 11,8 | settimanale |

## 3. L'MDE

Il test e' sulla media del rendimento della strategia: t ≈ Sharpe annuo × √anni. Con alpha 5% e
potenza 80% serve t ≥ **2,80** ([[feedback_potenza_prima_di_raccogliere]]), quindi
**MDE (Sharpe) = 2,80 / √anni**. Lo Sharpe non dipende dalla volatilita' della strategia, quindi qui
bastano gli anni.

| disegno | Sharpe ottimistico (pubblicato) | onesto (meta') | anni disponibili | **MDE** | anni necessari (ottim. / onesto) | fuori scala |
|---|---|---|---|---|---|---|
| **mensile (Fan)**, solo dopo il 2018, gratis | 0,61 | 0,31 | 5,8 | **1,16** | 21 / 84 | **3,6× / 14,5×** |
| mensile, dopo il 2018, a pagamento | 0,61 | 0,31 | 8,3 | 0,97 | 21 / 84 | 2,5× / 10,2× |
| mensile, prima + dopo, a pagamento (generoso: conta anni forse gia' visti) | 0,61 | 0,31 | 15,0 | 0,72 | 21 / 84 | 1,4× / 5,6× |
| **settimanale (Kang), dal giorno 5**, gratis | ~0,79 lordo ¹ | ~0,40 | 9,3 | **0,92** | 12,6 / 49 | **1,4× / 5,3×** |
| settimanale, a pagamento | ~0,79 lordo ¹ | ~0,40 | 11,8 | 0,82 | 12,6 / 49 | 1,07× / 4,2× |

¹ **Stima mia, non pubblicata.** Viene dalla t 3,62 dei giorni 5-10 su ~20,8 anni (3,62/√20,8 ≈ 0,79).
E' la finestra **migliore** dopo la pubblicazione del report, ed e' **lorda**: il ribilanciamento
settimanale di 10 futures ha costi che il paper non sottrae. Lo scenario ottimistico qui e' piu'
ottimistico del solito.

## 4. Lettura

**Nessuna configurazione ha potenza, nemmeno nello scenario ottimistico con i dati a pagamento.** Il caso
meno lontano (settimanale, a pagamento, lordo) e' fuori scala di 1,07×. Ma e' lo Sharpe della sola
finestra migliore, senza costi, e col premio delle commodity che le fonti stesse vedono indebolirsi.
Nello scenario onesto servono **da 49 a 84 anni**.

Due limiti indipendenti dalla potenza:
1. **Operabilita' alla nostra scala.** Un long-short su 20-40 futures su commodity richiede un conto
   futures e un capitale nell'ordine delle centinaia di migliaia di dollari di nozionale: un contratto
   su una commodity agricola vale decine di migliaia di dollari (stima a spanne, **non verificata**).
   Su FP Markets ci sono solo mais, grano e le soft ([referto A1 §8](TREND_A1_HELDOUT_POWER.md)). Un GO
   direbbe che il premio esiste, non che possiamo incassarlo.
2. **Il sotto-campione della seconda meta'.** Fan et al. vedono il premio delle commodity indebolirsi
   dopo il ~2006. I nostri anni fuori campione stanno **tutti** dopo: lo scenario onesto non e'
   pessimismo, e' la lettura della fonte.

**Cosa dice sulla domanda del brainstorming.** *"Premi invece di tempismo"* era la domanda giusta, ma i
premi documentati e alla portata del retail sono gia' presi o fuori scala:
- il **premio azionario** lo incassa gia' il PAC;
- quello di **copertura** sulle commodity richiede un portafoglio di futures che non possiamo tenere ne' testare;
- il **VRP** richiede opzioni (parcheggiato, fuori perimetro).

E' un esito sul **perimetro**, non sul metodo.

## 5. Le strade — ✅ **decisa la A** (Matteo, 03/10)

- **A — chiudere a 0 trial** come *"non testabile a potenza utile fuori campione, e non operabile alla
  nostra scala"*. **Non falsificato.** Riapertura: un conto futures con capitale adeguato **e** un
  feed con almeno ~20 anni fuori dal campione delle fonti (cioe' un forward di molti anni), oppure una
  replica indipendente pubblicata dopo il 2018 con lo Sharpe ancora vicino a 0,6. *(raccomandata)*
- **B — replica nel campione** (1993-2018 sui futures pysystemtrade) come **verifica dei dati e del
  metodo**: dice se i nostri dati riproducono il paper, **non** se il premio c'e' oggi. Non e' un
  verdetto, e un esito positivo creerebbe pressione a "fare qualcosa" con un premio che non possiamo
  incassare. Sconsigliata.
- **C — forward**: raccogliere da oggi. Con 21-84 anni necessari non e' un'opzione reale.

Nessuno slot esterno del Q4 e' stato consumato, e nessuna famiglia aperta nel ledger.
