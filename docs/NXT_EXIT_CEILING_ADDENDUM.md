# NXT — addendum: SOFFITTO DELL'USCITA (misura di escursione)

> **Scritto e committato PRIMA di eseguire la misura.** 2026-08-14. Addendum a
> [`fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md`](../fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md)
> e al NO-GO del 2026-07-17 ([DECISIONS.md](../DECISIONS.md)). Non è una nuova strategia:
> è una **rianalisi dei setup già eseguiti** che misura una quantità che il backtest originale
> non registrava. Motore: [`analysis/nxt/excursion.py`](../analysis/nxt/excursion.py).

## Da dove nasce

Idea dell'utente (2026-08-14): stessa meccanica NXT — pivot confermato a *k* barre, ordine limite
a distanza fissa dall'estremo, stop sotto l'estremo — ma **senza take-profit**, tenendo il trade
aperto fino a un'uscita a coda aperta (incrocio di medie mobili).

La meccanica di entrata è **identica** a quella già implementata in
[`analysis/nxt/backtest.py`](../analysis/nxt/backtest.py) (`zigzag` k=5 look-ahead-safe, entry
limite al 50% della gamba, SL al 78.6%). L'unico elemento nuovo è **l'uscita**.

## La domanda (una sola)

Esiste **una qualunque** regola di uscita a coda aperta che, tenendo fermi entrata e stop
pre-registrati, riporti E[R] sopra zero — oppure la coda destra è troppo magra perché il segno
possa cambiare, quale che sia l'uscita?

Si misura il **soffitto**, non una regola specifica. La MFE (massima escursione favorevole) è un
**limite superiore invalicabile** per qualunque exit rule: nessuna regola può incassare più di
quanto il prezzo si sia mosso a favore. Se il soffitto non basta, non serve costruire l'uscita a
medie mobili — e si risparmia l'ultimo round di rifinitura della famiglia.

## Cosa si misura

Per ogni setup **riempito** con l'entrata primaria (`entry_fib = 0.5`), dal fill in poi, **senza
TP e senza break-even**, si cammina in avanti fino a SL grezzo o `MAX_HOLD` e si registra:

- **MFE in R** — massima escursione favorevole / rischio;
- **MAE in R** — massima escursione avversa / rischio;
- **R terminale** — −1 allo stop, oppure `(close − entry)/rischio` a `MAX_HOLD`;
- durata, asset, anno.

Convenzione intrabar coerente con il motore originale: bound **pessimistico** (nella barra in cui
tocca lo stop, l'escursione favorevole di quella barra **non** si conta) come primario, bound
ottimistico riportato a fianco. Costi: stesso `SPREAD` per asset, sottratto in R.

## Soglie di lettura — DICHIARATE PRIMA DEI NUMERI

**S1 — soffitto dell'oracolo.** `E[R]_oracolo = media su tutti i setup di max(MFE, −1)`, al netto
dei costi: l'esito di un operatore con preveggenza perfetta che esce sempre al massimo.
→ **se ≤ 0: kill immediato.** Nessuna regola reale può battere l'oracolo; se nemmeno lui è in
utile, la famiglia è chiusa senza appello.

**S2 — soglia della tesi "lascia correre".** Tenendo il tasso di stop-out osservato, perché il
segno si ribalti i vincenti devono rendere in media **> 6,5R**:

$$0{,}133 \cdot W - 0{,}867 > 0 \implies W > 6{,}5R$$

Il tetto misurabile su *W* è `E[MFE | MFE ≥ 3R]`.
→ **se `E[MFE | MFE ≥ 3R]` < 6,5R: la tesi specifica è morta**, perché anche incassando l'intera
escursione di ogni vincente non si arriva a zero.

**S3 — breadth (kill duro n. 3).** Le due misure sopra vanno riportate **per asset (6) e per anno
(~14)**. Un soffitto positivo concentrato su un asset o un anno non è un soffitto: è un outlier.
Serve maggioranza di asset **e** di anni sopra soglia.

## Cosa NON si fa (vincoli anti-p-hacking)

1. **Non si scandaglia il multiplo d'uscita** cercando il migliore. Si guardano la distribuzione e
   le due soglie, punto. Scegliere *a posteriori* "si esce a 4,2R perché è il massimo della curva"
   è descrivere il passato.
2. **Non si usa il filtro sul rischio massimo per salvare il risultato.** L'utente ha indicato un
   vincolo operativo (si entra solo se la distanza entry→stop non supera *tot* pip). La MFE per
   quintile di rischio è riportata come **descrittivo**; usarla per selezionare il sottoinsieme che
   funziona sarebbe l'aggiunta di filtro di [STRATEGY_LIFECYCLE §4](STRATEGY_LIFECYCLE.md) — il
   p-hack più seducente e più fatale.
3. **Non si apre l'holdout.** La misura gira sull'intero campione perché è una **rianalisi
   descrittiva di un test già concluso con verdetto NO-GO**, non un nuovo gate: non c'è nulla da
   sigillare per una famiglia già bocciata. Se le soglie passano, la pre-registrazione nuova che ne
   seguirà dovrà avere **il proprio** holdout e il proprio forward OOS.

## Contabilità dei trial

Questa misura **non consuma trial**: non cambia nessuna regola pre-registrata e non può migliorare
il risultato del backtest originale — misura una quantità che quel backtest non registrava
([STRATEGY_LIFECYCLE §3](STRATEGY_LIFECYCLE.md), riga "modellazione più realistica").

Se S1, S2 e S3 passano tutte, la costruzione dell'uscita a medie mobili sarà il **round 3 di 3**
della famiglia NXT (dopo continuazione = NO-GO e fade = LEAD) — l'ultimo che le resta.
Se una qualunque fallisce: **kill**, e l'idea non arriva alla pre-registrazione.

---

## S4 — baseline random risk-matched (aggiunto in corsa, 2026-08-14)

**Aggiunto dopo aver visto S1-S3, e dichiarato come tale.** S1 e S2 sono passate, ma sono risultate
**mal calibrate**: con rischio = 0,286 × ampiezza gamba (≥ 1 ATR H1) e holding fino a 20 giorni, una
MFE a doppia cifra in R è quasi garantita per costruzione, per *qualunque* geometria a stop stretto.
Le soglie non avevano potere discriminante.

Il controllo che ce l'ha: per ogni setup reale, **3 controlli con stesso asset, stesso lato, stesso
rischio in unità di prezzo, stesso anno, ma entrata a istante casuale**. Isola ciò che la struttura
aggiunge rispetto al puro effetto "stop stretto tenuto a lungo".

Legittimo per [STRATEGY_LIFECYCLE §3](STRATEGY_LIFECYCLE.md): un baseline più severo **può solo
peggiorare** il risultato → non conta come trial. Regola dichiarata: **se il reale non batte il
random matched, kill duro n. 2**, indipendentemente da S1-S3.

## Esito

**KILL.** Reale −1,44R *sotto* il random sul soffitto (CI95 [−1,569, −1,314]), **0/6 asset e 0/15
anni** favorevoli. Verdetto completo:
[docs/reviews/nxt-exit-ceiling-2026-08-14.md](reviews/nxt-exit-ceiling-2026-08-14.md).
