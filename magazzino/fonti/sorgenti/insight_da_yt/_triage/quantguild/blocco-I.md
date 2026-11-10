# Blocco I — video singoli arrivati dopo la chiusura (dall'hub)

Il distillamento del canale resta **chiuso** (17/09, [`PIANO.md`](PIANO.md)): questo blocco non lo riapre. Raccoglie
i video che Matteo segnala uno per uno dall'inbox dell'hub, letti per intero dalla trascrizione in `_raw/`.
Legenda come in [`blocco-A.md`](blocco-A.md); in più ogni claim ha il suo **stato di conoscenza** (regola comune 4
del vault).

---

## I1 — Sports, Poker, and Why Quants are Bad Traders

`pNwcgLbfz-A` · 14 min · 2.389 parole · traccia generata, completezza ok (169 parole/min) · scaricato e letto il
2026-11-04 · arrivato dall'inbox dell'hub il 01/11, con la nota di Matteo *"Teorie"*.

### Che cos'è
Un *fireside chat*: un monologo senza lavagna, senza formule, **senza un numero e senza una regola**. Nessuna
statistica dichiarata da filtrare. La tesi: un quant diventa un cattivo trader quando crede che il backtest dica cosa
succederà. Assumere rischio è un'attività "a prestazione", come lo sport o il poker: l'edge è un valore atteso che si
vede solo su molte ripetizioni, si sopravvive con scommesse indipendenti e si corregge la rotta in corsa
("aggiornamento bayesiano").

### I claim

| # | Claim della fonte | Stato | Nel repo | Lettura |
|---|---|---|---|---|
| 1 | L'edge è il **valore atteso**: il singolo trade non dice nulla, conta la legge dei grandi numeri | `verificato` (definizione) | `doc`: A1, [`04`](../../../../04_quant_metodologia/principles.md) | Rinforzo, niente di nuovo |
| 2 | Al casinò l'edge del banco è fisso e positivo, quello del giocatore è il suo opposto (somma zero); chi continua a giocare perde tutto | `verificato` nel limite (gioco senza fine contro un banco con capitale illimitato) | `doc`: rovina del giocatore in [`SINTESI.md`](SINTESI.md) | Corretto qui, perché l'edge del giocatore è negativo. La battuta sul conteggio delle carte ("non stai contando") riguarda chi ascolta, non la possibilità: il conteggio è un edge documentato |
| 3 | Il backtest mostra come sarebbe andata **in quelle condizioni**, e *"non ha letteralmente alcuna rilevanza"* su ciò che succederà | prima metà `verificato`; seconda `falsificato` come affermazione generale | conflitto **già mappato**: [`_INTAKE.md`](../../../../_INTAKE.md) riga "volatility drag + orthogonal streams", mappa dei modelli in `DECISIONS.md` | La prima metà è la ragione per cui esistono holdout e forward OOS. La seconda si contraddice con il resto del video: chiede di scegliere scommesse a valore atteso positivo senza dire da dove venga la stima. **Stessa fonte, stesso conflitto: non è una conferma in più** |
| 4 | "Se la strategia non batte l'S&P 500, a che serve?" è un errore, perché il confronto si fa solo ex post | `verificabile`, coerente solo in parte | `doc`: [`05`](../../../../05_portfolio_rischio/principles.md) apertura (battere un benchmark ≠ alpha) | Vero che battere l'indice non è alpha. Ma la domanda non è un errore: è il **costo opportunità**, e per noi ha un nome preciso, il PAC. Il nostro protocollo confronta col random risk-matched e con `benchmark_metrics`, tutti e due fissati **prima**. Nessun cambiamento |
| 5 | Domande retoriche sulla volatilità: perché è "sempre" in contango, perché la backwardation è effimera, perché ritorna verso la media | `verificabile`; "sempre" è falso alla lettera (lo smentisce la sua stessa "backwardation effimera") | `doc`: VRP **parcheggiato** in `_INTAKE.md` (opzioni e vol fuori perimetro operativo) | Nessun numero, nessuna regola. Il perimetro resta quello; il filone VIX è chiuso a 0 trial dal 03/10 |
| 6 | Valore atteso positivo **non vuol dire** puntare tutto: serve un portafoglio di scommesse indipendenti per sopravvivere quando le perdite arrivano insieme; conta il CAGR, cioè la crescita geometrica | `verificato` (matematica) | `core` + `doc`: volatility drag e Kelly frazionario in `05`, `core/verifiche.py` | Rinforzo. È la stessa tesi delle note già distillate dallo stesso autore |
| 7 | **Demone di Shannon**: chi ribilancia bene mantiene un vantaggio; chi non ribilancia può finire a crescita geometrica nulla | formula `verificato` (derivazione); "dà un edge" `verificabile`, con condizioni | **assente come nome**: aggiunto a `05`, punto 5 del volatility drag | Vedi sotto. Rilevanza: reference per il PAC di fase 2, nessuna per il trading |
| 8 | **Aggiornamento in corsa**: se perdi il primo set, cambi strategia. Non sai se è stato il caso o un edge negativo: *"devi decidere al volo"* | conflitto, **già mappato** nella forma generale | `doc`: corollario sul Bayesian updating in `04` §9; regola di ritiro in [`STRATEGY_LIFECYCLE.md`](../../../../../docs/STRATEGY_LIFECYCLE.md) ("si giudica contro la distribuzione, non contro l'umore") | La fonte ammette di non saper distinguere il caso da un edge negativo. La nostra risposta a quella domanda c'è già: SPRT sul win rate e CUSUM sulla R media, **con gli errori dichiarati prima del capitale**. Cambiare le regole dopo aver visto le perdite è un trial ([[feedback_correggere_non_e_cercare]]). È la stessa separazione del conflitto (b) di `SINTESI.md`: allocatore discrezionale contro regole sistematiche. Nessun cambiamento |
| 9 | L'alpha è un'allocazione giusta guardando avanti, e si vede nel residuo di un modello fattoriale | `verificato` (definizione) | `doc`: alpha ortogonale in `05` | Rinforzo |
| 10 | "Il rendimento passato non predice il futuro": la squadra che ha vinto il Super Bowl potrebbe non rivincere | `non falsificabile` così com'è scritto | — | Uno slogan. La versione che si misura è il nostro forward OOS |

### Il demone di Shannon (punto 7), con le condizioni
Viene dalla formula del volatility drag che sta già in `05` ($R_G \approx \bar R - \sigma^2/2$). Applicata a un
portafoglio a pesi fissi $w_i$, ribilanciato a ogni periodo, la media aritmetica del portafoglio è la media pesata
delle medie, $\bar R_p = \sum_i w_i \bar R_i$, mentre la varianza $\sigma_p^2$ è più piccola della media pesata delle
varianze quando le componenti non sono perfettamente correlate. Ne segue:

$$R_{G,p} \approx \sum_i w_i R_{G,i} + \tfrac12\Big(\sum_i w_i \sigma_i^2 - \sigma_p^2\Big)$$

Il secondo termine è il **premio di ribilanciamento**: non è mai negativo, e cresce con la volatilità delle componenti
e con la distanza della loro correlazione da 1.

- **Cosa confronta**: la crescita del portafoglio con la **media pesata** delle crescite delle componenti, **non** con
  quella della componente migliore. Un portafoglio ribilanciato può crescere meno dell'asset migliore.
- **Quando regge**: rendimenti indipendenti da un periodo all'altro, componenti volatili e poco correlate, costi di
  ribilanciamento piccoli rispetto al premio.
- **Quando si rompe**: con correlazioni vicine a 1 (il premio sparisce), quando i costi e le tasse a ogni ribilancio
  superano il premio, e quando un asset ha una tendenza persistente, perché il ribilancio vende sistematicamente il
  vincitore.
- **Per noi**: il PAC di fase 1 è un solo strumento, quindi non c'è niente da ribilanciare
  ([`INVESTING_PILLAR_PLAN.md`](../../../../../docs/INVESTING_PILLAR_PLAN.md) §0). Nella fase 2 il ribilancio annuale
  o a bande produce questo premio come **sottoprodotto**: la ragione per ribilanciare resta il controllo del rischio,
  non il premio. Nessun numero dichiarato dalla fonte, nessuna misura nostra.

### Consuntivo
- **Strategie**: zero. **Trial**: zero. **Pre-registrazioni**: nessuna.
- **Buchi nuovi**: nessuno. L'unico termine che mancava (il demone di Shannon) è una conseguenza di una formula che
  avevamo già.
- **Conflitti nuovi**: nessuno. I punti 3 e 8 sono **nuove occorrenze, della stessa fonte**, di conflitti già mappati:
  per la regola sulle conferme contano zero.
- **Qualità della fonte**: lo stesso difetto già notato in `SINTESI.md`. Dice che il backtest non ha alcuna rilevanza,
  poi chiede di scegliere scommesse a valore atteso positivo e di affidarsi all'"esperienza", senza dire come si stimi
  quel valore atteso né come si distingua il caso dall'errore.
- **Per la nota "Teorie" di Matteo**: dal punto di vista teorico il video dà una cornice (edge come valore atteso,
  sopravvivenza prima della massimizzazione, crescita geometrica) che il repo ha già, con le formule. Non cambia
  nessuna decisione.
