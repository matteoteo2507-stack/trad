---
titolo: "Doppio binario sulle famiglie CLOSED: c'e' un caso in cui darebbe un risultato diverso?"
tipo: referto
creato: 2026-10-06
stato: descrittivo
trial: 0
---

# Doppio binario sulle famiglie CLOSED

**Domanda di Matteo (06/10):** fra le famiglie etichettate CLOSED ce n'e' una per cui, per aritmetica, il
doppio binario (1R fisso + overlay, [STRATEGY_LIFECYCLE §4quater](../STRATEGY_LIFECYCLE.md)) potrebbe dare
un risultato diverso?

**Cosa NON puo' cambiare, per costruzione:** il verdetto. Sta sul binario 1R, che e' quello gia' misurato.
E una famiglia CLOSED non si riapre con un overlay (§7). La domanda vera e': c'e' una famiglia in cui un
overlay mostrerebbe **valore di dipendenza** (esiti raggruppati) abbastanza grande da cambiare il quadro?

## 1. L'aritmetica

Un overlay cambia l'attesa per unita' di rischio solo tramite Cov(size, R). Nel caso sintetico **piu'
favorevole** misurato il 06/10 (regimi 65%/45% di vincite, persistenza 0,97: perdite molto raggruppate) il
cuscinetto O1 aggiungeva circa **+0,05R** per unita'. Una famiglia con un 1R piu' negativo di cosi'
richiederebbe una dipendenza piu' forte di quel caso estremo.

| famiglia | da cosa viene il verdetto | 1R (fonte) | un overlay e' applicabile? | serve un guadagno di |
|---|---|---|---|---|
| livelli | tasso di reazione contro il random | — (384 trial, DECISIONS 2026-07-07) | no: non e' una sequenza di trade | — |
| london_breakout | difetto di look-ahead (kill duro 1) | risultati nulli | no: non c'e' un numero da migliorare | — |
| nxt (fade) | fill ottenibili | **−0,250** (DECISIONS 2026-09-17 (4)) | si' | ≥ 0,25R: fuori portata |
| nxt (continuazione) | fill ottenibili | **−0,118** [−0,161; −0,076] (2026-09-18 (5)) | si' | ≥ 0,12R: fuori portata |
| opening_range SPX500 | TRAIN 2012-19 | **−0,267** [−0,391; −0,121] (A5, 2026-09-18) | si' | ≥ 0,27R: fuori portata |
| **opening_range NAS100** | 14,5 anni | **−0,056** [−0,11; 0,00]; v2: ogni intervallo contiene lo zero, MDE 0,135 (A5) | si' | **~0,06R: dentro la portata del caso estremo** |
| round_grid | reazione contro griglia sfasata | +0,08 punti (2026-08-09) | no: non e' una sequenza di trade | — |
| seasonality_tom | finestre di posizione | Sharpe −0,28 (2026-07-08) | no: niente stop, niente R | — |
| meanrev_vol | portafoglio vol-scalato | Sharpe −0,21 (2026-07-08) | no: la size e' gia' una regola ex ante | — |
| tsmom | portafoglio vol-scalato | Sharpe +0,21 [−0,18; +0,59], **non misurato** (A5) | no: il problema e' la potenza (MDE 0,59), e una size variabile aggiunge varianza invece di toglierla | — |
| meanrev_kichev | misura descrittiva, nessun trade | — | no | — |
| forexgump | differenza appaiata mentore − opposto | d −0,007; copiato −0,342 (2026-10-05) | no: l'overlay agirebbe uguale sui due lati del confronto | — |

**Risposta aritmetica: un solo caso, ORB su NAS100.** E' l'unico verdetto che (a) viene da una sequenza di
trade con stop, (b) sta abbastanza vicino a zero da essere raggiungibile da una dipendenza forte, (c) ha un
motivo a priori per averla: A5 ha misurato che l'E[R] dell'ORB sale in modo monotono con l'ADX, e il regime
di volatilita' e' persistente, quindi gli esiti potrebbero arrivare raggruppati. ⚠️ Nota: usare l'ADX per
decidere la size **non** sarebbe un overlay (e' informazione ex ante: un filtro, §4); qui si misura solo se la
sequenza degli esiti, cosi' com'e', contiene dipendenza.

## 2. Misura dichiarata PRIMA dell'esecuzione

Script: [`analysis/opening_range/doppio_binario.py`](../../analysis/opening_range/doppio_binario.py), scritto e
committato prima di girare. **0 trial**: nessun parametro, asset o filtro scelto, l'holdout della famiglia e'
gia' speso, la famiglia resta CLOSED qualunque cosa esca.

- **Campione:** ORB v2 (`backtest_v2.run`), trade primari ADX ≥ 25, tutto il periodo, come la scomposizione di A5.
- **Primario:** NAS100, colonna `R_pess` (la convenzione del verdetto), rimescolamento a blocco 1, overlay O1 e
  O3, banda al 95% su 1.000 rimescolamenti. Due confronti: falso allarme ~10% sulla coppia.
- **Descrittivo** (non vale come risultato, comunque esca): `R_opt`, blocco 20, SPX500 come controllo, e il
  binario prop (`two_step_classic` di `prop-lab`, rischio base 1% e 2%, 60 ricampionamenti × 200 percorsi,
  MAE = 1R per tutti i trade, cioe' conservativa sul drawdown).

**Lettura scritta prima:**
- Primario **nessun valore di dipendenza** → la risposta aritmetica era l'unico dubbio e la misura lo chiude.
- Primario **AGGIUNGE** → nel backlog entra un'ipotesi nuova, *"gli esiti dell'ORB su NAS100 sono raggruppati"*,
  che si valuta solo con dati nuovi (forward o una pre-registrazione nuova). Non e' una riapertura.
- Primario **TOGLIE** → si annota, nessuna conseguenza.
- Binario prop: conta `ev_vs_zero` con il suo intervallo. Un EV positivo con `ev_vs_zero_lo` ≤ 0 si scrive
  *"EV dovuto al vantaggio non dimostrato"*.

## 3. Risultati (eseguito il 06/10 dopo il commit `7458b1c`, 6'31")

**Primario: NAS100, `R_pess`, blocco 1.** 1.195 trade primari, 20/01/2012 → 15/07/2026. 1R **−0,0125R**.
Runs test **z = −0,08** (p = 0,94): nessuna traccia di esiti raggruppati.

| binario | E per unita' di rischio | banda 95% del rimescolato | valore di dipendenza | maxDD (R) | maxDD mediano rimescolato | lettura |
|---|---|---|---|---|---|---|
| 1R | −0,0125 | — | — | 79,9 | 69,2 | verdetto |
| O1 cuscinetto | −0,0243 | [−0,0434; +0,0283] | −0,0072 | **25,1** | 22,8 | nessun valore di dipendenza |
| O3 serie di perdite | −0,0265 | [−0,0712; +0,0446] | −0,0125 | 48,9 | 48,2 | nessun valore di dipendenza |

**Lettura dichiarata: il dubbio aritmetico era l'unico, e la misura lo chiude.** Nessuna famiglia CLOSED
cambierebbe quadro con il doppio binario. ORB resta CLOSED; nessuna ipotesi nuova nel backlog.

Cosa si vede in piu', senza che cambi la risposta: il cuscinetto taglia il drawdown di due terzi (79,9R → 25,1R)
al costo di 0,012R per unita'. E' **struttura del rischio**, non vantaggio: lo stesso taglio c'e' sulla sequenza
rimescolata (22,8R).

**Descrittivi** (non valgono come risultato):
- `R_opt` e blocco 20: stessa lettura su NAS100.
- **SPX500, controllo:** esiti **raggruppati** (z = −2,21, p = 0,027). O3 ha +0,056 di valore di dipendenza a
  blocco 1 (percentile 96,6, appena dentro la banda), che sparisce a blocco 20 (−0,003): il raggruppamento e'
  corto, entro una ventina di trade. Anche cosi' O3 resta a **−0,039R** per unita': una dipendenza vera ma
  modesta non porta a zero un verdetto di −0,094R. E' esattamente la previsione del §1.
- **Binario prop** (`two_step_classic`, regole modello di `prop-lab`): la dimostrazione del perche' si legge
  `ev_vs_zero` e mai l'EV da solo.

| | rischio | EV per tentativo (range sui binari) | `ev_vs_zero` (range) | intervallo 90% di `ev_vs_zero` |
|---|---|---|---|---|
| SPX500 (1R −0,094, refutato) | 2% | **da +339 a +783 €** | da −898 a −1.475 € | **tutto sotto zero** in ogni binario (p > 0: 0,03-0,05) |
| NAS100 (1R −0,013) | 2% | da +400 a +1.105 € | da −166 a +5 € | contiene lo zero in ogni binario (p > 0: 0,42-0,50) |

  Una strategia refutata mostra un EV positivo in ogni binario perche' la challenge e' un'opzione; misurata
  contro il vantaggio zero **toglie** valore. Su NAS100 la scritta corretta e' *"EV dovuto al vantaggio non
  dimostrato"*.

**Limite di questa esecuzione:** 60 ricampionamenti × 200 percorsi. Con 200 percorsi anche la stima puntuale ha
rumore Monte Carlo (in una riga, SPX500 O3 al 2%, il punto cade appena fuori dal suo intervallo). Per un numero
da citare in una decisione servono almeno 500 percorsi.
