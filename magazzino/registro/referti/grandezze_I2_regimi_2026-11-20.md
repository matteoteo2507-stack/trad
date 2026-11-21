---
titolo: "I2 Regimi e stato latente: controllo delle grandezze (passo 1)"
data: 2026-11-20
tipo: controllo
stato: quarantena
---

# I2 — controllo "stessa grandezza = stessa famiglia"

Passo 1 della famiglia I2 del [backlog §I](../../../decisioni/BACKLOG_RICERCA.md), prima di qualunque dato.
Regola: [STRATEGY_LIFECYCLE §3](../../../motore/metodo/STRATEGY_LIFECYCLE.md) (indicatore diverso sulla stessa
grandezza = trial della stessa famiglia) e §8ter (senza quota, e' l'unico freno al numero di famiglie); Checklist 10
punto 8 del gatekeeper. Le grandezze sono le sei di
[10_indicatori_tecnici §2](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md) (regola di Matteo dell'08/10,
DECISIONS 2026-10-08 (3)). **Nessun dato letto, nessuna previsione calcolata: 0 trial.** Revisione del gatekeeper in
fondo: PASSA CON RISERVE, 0 bloccanti; le riserve sono applicate nel testo.

## Il criterio

**Due letture della regola.** Il §3 dice "misura la stessa grandezza", e la tabella del modulo 10 §2 classifica per
**ingresso** (cosa legge l'indicatore dal prezzo). La [pre-registrazione della volatilita'](../documenti/VOLATILITA_PREREGISTRATION.md)
§1 ha classificato per **bersaglio** (cosa prevede lo strumento): ha aperto una famiglia nuova perche' l'accuratezza di
una previsione di **varianza** e' un bersaglio diverso dai **rendimenti** delle famiglie di strategia che usavano la
volatilita' (`meanrev_vol`, gradiente di `trend_momentum`). Qui le due letture danno lo stesso esito ovunque tranne in
2b, che e' una domanda per Matteo (sotto).

**Bersaglio uguale con un'altra perdita = variante; bersaglio diverso = grandezza diversa.** Per la volatilita'
cambiava il bersaglio. Per la direzione no: "lo stato Bull persiste" e "il segno del rendimento passato guadagna" sono
due funzioni di perdita sullo stesso bersaglio, il rendimento futuro, come QLIKE e MSE lo sono per la varianza.
`tsmom` e `trend_momentum` hanno **posto** questa domanda senza la potenza per rispondere (`tsmom` declassato a NON
MISURATO, `trend_momentum` CLOSED per potenza): la grandezza e' comunque coperta da famiglie CLOSED.

**Persistenza meccanica.** Ogni etichetta costruita su una finestra mobile persiste a un passo per costruzione: il
rendimento a 20 giorni condivide 19 giorni con quello del giorno dopo, `ATR14` contro `SMA50(ATR14)` 49 barre su 50,
l'ADX e' un DX lisciato sopra DI lisciati (circa 2×14 barre, [`regime.py`](../../../motore/core/regime.py) righe 89-131).
La proprieta' del backlog I2 ("il regime di oggi prevede quello di domani") a un passo e' quindi **soddisfatta da un
processo senza contenuto**. Il contenuto oltre la meccanica si legge solo su passi non sovrapposti o contro un nullo
con la stessa sovrapposizione. Non cambia nessuna classificazione.

## Candidato per candidato

"Tendenza" sotto = `tsmom` + `trend_momentum`: una famiglia nella
[pre-registrazione trend](../documenti/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md) ("round 2 di 3, round 1 = TSMOM
canonico"), due id nel contatore; l'imputazione e' da decidere (vedi "Decisioni aperte", D3).

| # | candidato | cosa legge dal prezzo | bersaglio | grandezza | famiglia esistente |
|---|---|---|---|---|---|
| 1 | asse calmo/volatile di `regime.py` (`ATR14 > SMA50(ATR14)`) | ampiezza | varianza futura sopra o sotto la sua media: raggruppamento della volatilita' in forma binaria | 3 | **`volatilita`** (in ridisegno). La pre-registrazione §1: "non e' una famiglia: un esito dell'HMM non lo convalida" |
| 2a | asse direzionale, segno (`+DI` contro `-DI`) | segno del movimento recente | segno del movimento futuro | 1 | **tendenza** (CLOSED) |
| 2b | asse direzionale, forza (`ADX < 25` → Sideways) | quanto del range e' direzionale, senza segno | se domani il mercato tende o oscilla: l'autocorrelazione dei rendimenti che cambia nel tempo | per la lettera della regola 1; per il bersaglio, nessuna delle sei | **domanda a Matteo** (D1) |
| — | regime congiunto a 6 stati di `regime.py` | 1 × 3 | combinazione | 1 e 3 | tendenza e `volatilita`: nessuna grandezza nuova |
| 3 | catene di Markov su rendimenti a finestra mobile ([blueprint](../../fondamenti_tecnici/blueprints/markov_regime_skill.md)) | segno del rendimento a 20 giorni e banda Sideways ±2% | stato del passo successivo | 1 (segno) e 3 (la banda dipende dall'ampiezza) | tendenza e `volatilita`. Su finestre non sovrapposte e' la grandezza di `tsmom` con altri parametri (20/20 contro 252/21, perdita sull'accuratezza dello stato): per il §3 e' un **cambio di parametro**, cioe' un trial della tendenza |
| 4 | Kalman come livello del prezzo | media adattiva del prezzo | pendenza o scarto dal livello | 1 (pendenza), 2 (scarto) | tendenza (a regime il livello locale e' un EWMA; Levine-Pedersen 2016, modulo 10 §1); scarto: `meanrev_vol`, `meanrev_kichev`, `mr_indici_rsi2` (CLOSED) |
| 5 | canale di regressione | retta e fascia sul prezzo | pendenza, larghezza, posizione nel canale | 1, 3 (la dispersione dei residui dipende anche da finestra e autocorrelazione), 2 (z-score dalla retta) | DECISIONS 2026-11-10 lo assegna per intero alla tendenza; la divisione in tre e' un raffinamento e non cambia la conclusione: tutte coperte |
| 6a | Kalman hedge ratio, **beta dinamico sui rendimenti** | covarianza fra due serie | covarianza condizionale | secondo momento, struttura fra asset | nessuna famiglia; sul confine fra `volatilita` (il DCC e' il GARCH multivariato) e **I3**. Se va in I3, la G1 di I3 deve fissare il confine con `volatilita` |
| 6b | Kalman hedge ratio, **cointegrazione sui livelli** | combinazione di prezzi | stazionarieta' dello spread | per ingresso 2 (spostamento dalla media di uno spread), con un meccanismo di valore relativo | nessuna famiglia ha misurato spread fra asset. **Non** e' la covarianza della PCA: un'alta correlazione dei rendimenti non e' ne' necessaria ne' sufficiente. **Domanda a Matteo** (D2) |

**Altre idee di regime**

| candidato | grandezza | dove ricade |
|---|---|---|
| HMM sui rendimenti (blueprint §2) | 1 se gli stati si separano per media, 3 se per varianza | tendenza o `volatilita`. Che sui rendimenti giornalieri si separino soprattutto per varianza e' un claim in **quarantena**. ⚠️ Il blueprint usa `.predict(X)` (Viterbi sull'intero campione): e' lisciamento, vietato da S5 (§8ter); non usabile come strumento cosi' com'e' |
| VIX come previsione della varianza realizzata | 3 | `volatilita` (non il nodo del premio, che misura la media di IV − RV). Come filtro della direzione e' un trial della famiglia filtrata (precedente: H2 → `mr_indici_rsi2`) |
| efficiency ratio, esponente di Hurst, variance ratio | come 2b | segue D1. Il "router momentum + reversione" di luglio e' stato **proposto e dichiarato refutato senza un test** (nessun codice, pre-registrazione, referto o voce nel contatore; l'etichetta "beta-trap" compare solo nel bilancio di DECISIONS 2026-07-08): non vale come prova in nessuno dei due sensi. Precedente: DECISIONS 2026-10-08 (2) ha gia' superato uno scarto "beta-trap" senza test |
| sopra/sotto la media a 200 giorni (Faber) | 1 | tendenza |
| CUSUM, change point bayesiano | metodo, non grandezza: sulla media 1, sulla varianza 3 | tendenza o `volatilita` |
| salti, code, momenti superiori | 3 | `volatilita` (G7) |
| regimi di correlazione, dispersione fra asset | struttura fra asset | I3 |
| regimi di volume o attivita' | 4 | I4 (futures a 1 minuto con volume vero). Nessuna famiglia ha misurato la persistenza del volume: i livelli misuravano reazioni su zone di volume |
| regimi di liquidita' (spread, profondita') | microstruttura | I4 |
| regimi di orario | il tempo, fuori dalle sei | `momentum_ultima_mezzora` (CLOSED); per la volatilita' la stagionalita' oraria si toglie per regola (G3) |
| carry, base, struttura a termine | fuori dalle sei | fuori da I2; chiusi a 0 trial il 2026-10-03, senza famiglia |
| regimi macro: quadranti Fed, timing a 5 metriche, indicatori anticipatori ([03_regimi_macro](../../fondamenti_tecnici/03_regimi_macro/principles.md) §2-4) | fuori dalle sei (solo VIX > 30 e' una lettura del prezzo) | fuori dal perimetro di I2 (regimi letti dal prezzo); nessuna famiglia nel contatore, quindi uno strumento di regime macro sarebbe una **famiglia nuova** con la sua pre-registrazione. Due porte: il materiale del modulo 03 viene da una fonte esterna gia' distillata e passa da `_INTAKE.md` (LIFECYCLE §8); un'idea nata nell'hub passa dalla scheda d'ingresso ("Ingresso dall'hub") |

## Cosa sapevamo gia' di `regime.py`

- Uso misurato: il gating di `london_breakout` (maggio), invalidato da **look-ahead** (etichetta sulla chiusura dello
  stesso giorno, DECISIONS 2026-05-30); famiglia CLOSED per metodo. L'ADX come filtro e' stato speso anche come trial
  di `opening_range` (`magazzino/registro/codice/opening_range/backtest.py`).
- Il gating automatico per regime non e' mai stato costruito (DECISIONS 2026-11-09).
- La tabella "strategia adatta" di [TRADING_PRINCIPLES §1](../../fondamenti_tecnici/TRADING_PRINCIPLES.md) e la mappa
  `STRATEGY_REGIME_ACTIVATION` del codice sono **affermazioni senza misura**.
- La lettura di volatilita' che `regime.py` da' in forma binaria i soci la hanno gia', continua, nel pacchetto
  [`volatilita_ewma` v1](../../../uscita/volatilita_ewma/v1/report.md) (nessuna proprieta' dimostrata nemmeno li').

## Esito

**Dentro il perimetro di I2 (regimi letti dal prezzo) non resta nessuna grandezza nuova**, salvo che Matteo decida
diversamente su D1.
- **ATR (1)** → `volatilita`, in ridisegno. Se entra nel ridisegno, entra come serie contata nella sua
  pre-registrazione, su dati futuri; una fonte nuova mai vista si valuta come deviazione dichiarata da P3, col
  gatekeeper (DECISIONS 2026-11-20 (2)); il blocco dal 2024-11-11 resta escluso.
- **Direzione, Markov, Kalman livello, canale, media a 200 (2a, 3, 4, 5)** → tendenza e spostamento dalla media,
  CLOSED: riaprono solo con evidenza esterna (§7), non con un indicatore nuovo, e una riapertura non si valida sulla
  storia gia' vista (§7a): D1 multi-asset fino al 2026-08-14 per `trend_momentum`, fino al 2026-07-08 per `tsmom`.
  Usati come **filtro**, si imputano alla famiglia filtrata.
- **Kalman hedge ratio** → 6a verso I3 (con il confine verso `volatilita` da fissare), 6b da decidere (D2).
- **Regimi macro** → fuori da I2, famiglia nuova solo con una pre-registrazione; **volume e liquidita'** → I4.

Conseguenza per `regime.py`: resta "in uso senza misura" e non si misura in I2.

## Decisioni di Matteo (21/11)

**D1 = A** (la forza dell'ADX resta tendenza: I2 si chiude senza famiglia), **D2 = opzione 3** (cointegrazione: famiglia
nuova solo con un meccanismo indipendente scritto in DECISIONS), **D3 = due famiglie** (`tsmom` e `trend_momentum`
restano distinte; i round di `trend_momentum` restano 2 di 3 finche' non si decide altro). Registrate in
[DECISIONS 2026-11-21](../../../decisioni/DECISIONS.md). Le opzioni come erano poste:

## Decisioni poste

- **D1 — La forza della tendenza (2b) e' tendenza o una grandezza a se'?** Per la lettera della regola dell'08/10 e'
  tendenza: l'ADX e' nominato nella grandezza 1. La motivazione della regola pero' non la copre: Levine-Pedersen
  dimostra l'equivalenza fra filtri **lineari con segno** dei rendimenti passati, e l'ADX e' non lineare e senza segno
  (l'efficiency ratio e' circa |grandezza 1| / grandezza 3). Opzione A: resta nella tendenza (scelta prudente, nessuna
  famiglia nuova). Opzione B: si toglie l'ADX dalla grandezza 1 e "regime di autocorrelazione" diventa una grandezza
  nuova, cioe' una **modifica della regola dell'08/10** con una voce in DECISIONS; I2 avrebbe allora un candidato.
- **D2 — La cointegrazione (6b).** (1) dentro I3 per decisione di perimetro, sapendo che cambia la proprieta' di I3
  ("quante scommesse indipendenti"); (2) trial delle famiglie della grandezza 2 (CLOSED); (3) famiglia nuova solo con
  l'ultima riga del §3: meccanismo economico indipendente deciso in DECISIONS, parentela dichiarata, niente holdout sui
  dati delle famiglie parenti. Oggi il backlog I2 dice "e' un'altra grandezza".
- **D3 — `tsmom` e `trend_momentum`: una famiglia o due?** Non serve per chiudere I2, serve prima di qualunque trial di
  tendenza. Fino alla decisione l'unica imputazione difendibile e' sull'**unione**: trial sommati (Bailey-LdP,
  100 × N_params, per la parte non ricostruibile), holdout considerato aperto (il 2026-07-08, via `tsmom`), round 2 di 3
  consumati, dati fino al 2026-08-14 considerati visti. Lo stesso nodo c'e' nella grandezza 2 (`meanrev_vol`,
  `meanrev_kichev`, `mr_indici_rsi2`).

## Debito di protocollo emerso

**Corretto il 21/11** (DECISIONS 2026-11-21 (2)): 1 → campo `grandezze` del contatore; 2 → LIFECYCLE §7a (riapertura
come strumento: quota del binario d'origine, scelta di Matteo); 3 → modulo 10 §2 e §9; 4 → modulo 04 §7; 5 → nota nel
blueprint Markov.

1. Il contatore non ha un campo grandezza o parentela: `--check` non vede due id sulla stessa grandezza (D3).
2. Il §7a non dice cosa succede se una famiglia CLOSED del binario strategie viene riaperta come **strumento**, binario
   senza quota: e' una via per aggirare la quota, da regolare prima che serva.
3. Modulo 10 §2, riga 1: "famiglia trend ancora LEAD" e' superato da DECISIONS 2026-10-25 (5); §9: la motivazione
   Levine-Pedersen per l'ADX e' imprecisa (D1).
4. Modulo 04 §7: la persistenza da sovrapposizione e' meccanica, ma testabile contro un nullo con la stessa
   sovrapposizione; il testo e' troppo forte.
5. Blueprint Markov §2: HMM con Viterbi sull'intero campione; serve la nota "non usabile come strumento (S5)".

## Revisione del gatekeeper (2026-11-20)

**PASSA CON RISERVE**: 0 bloccanti, 13 riserve, tutte applicate in questo testo: criterio e doppia lettura (R1),
allineamento sul ridisegno (R2), persistenza meccanica per tutti gli assi (R3), Markov come cambio di parametro e banda
Sideways (R4), 2b come domanda a Matteo e filtro imputato alla famiglia filtrata (R5), `meanrev_kichev` e canale per
DECISIONS 2026-11-10 (R6), 6a/6b (R7), voci mancanti e VIX (R8), perimetro e due porte per il macro (R9), router (R10),
§7a sulla storia vista (R11), imputazione della tendenza (R12), commit prima dell'uso (R13). Il debito sopra viene
dalla stessa revisione.
