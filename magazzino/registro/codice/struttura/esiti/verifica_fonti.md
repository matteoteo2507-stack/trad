# I3 — verifica delle fonti sul testo (27/11/2026)

Passo (2) del §10 del [referto del passo 2](../../../referti/proprieta_I3_struttura_2026-11-21.md), prima del download.
Testi letti per intero dai PDF pubblici (estrazione del testo, nessun riassunto di terzi), 0 trial, nessun dato:
- **LRV**: Laurent, Rombouts, Violante, "On Loss Functions and Ranking Forecasting Performances of Multivariate
  Volatility Models", CIRANO 2009s-45 (versione di lavoro dell'articolo del *Journal of Econometrics* 173, 2013, 1-10;
  la versione pubblicata e' a pagamento e non e' stata letta);
- **PS**: Patton, Sheppard, "Evaluating Volatility and Correlation Forecasts", Oxford-Man Institute WP OMI02/07
  (versione di lavoro del capitolo dello Handbook of Financial Time Series, 2009);
- **ES**: Engle, Sheppard, "Theoretical and Empirical Properties of Dynamic Conditional Correlation Multivariate
  GARCH", NBER WP 8554 (2001).
Le pagine sono quelle del PDF.

## (a) Stein e Frobenius conservano l'ordinamento? **Si', entrambe** — verificato

- LRV, tabella 1 (p. 10): "Frobenius distance ... consistent"; "Stein distance Tr[H⁻¹Σ] − log|H⁻¹Σ| − N ...
  consistent". Proposizione 1 (p. 12): una perdita con derivata seconda rispetto al bersaglio "finite and independent
  of H" e' consistente; subito dopo: "only LF, LS, LE and LWE satisfy Proposition 1".
- PS, eq. (50) (p. 24): la classe robusta multivariata contiene, per b = −2, "tr(H⁻¹Σ) − log|H⁻¹Σ| − K", e "nests both
  the multivariate QLIKE and multivariate MSE".
- In LRV sono **non consistenti**, fra le altre, la "Correlation distance" e la Frobenius proporzionale (tabella 1).

## (b) Quale non distorsione chiede il teorema? **Condizionata, giorno per giorno** — verificato

- LRV, definizione 2 (p. 9): il proxy e' "some conditionally unbiased proxy of Σt"; ipotesi A2.4 (p. 12):
  "ξt = (σ̂t − σt) is a vector martingale difference sequence".
- PS, definizione 0.1 (pp. 15-16): "an unbiased volatility proxy, E_{t−1}[Σ̂t] = Σt".

**Cosa vuol dire per I3.** L'ordinamento con Stein e' garantito rispetto a Σ_t := E_{t−1}[Σ̂_t], cioe' l'**attesa del
nostro stimatore** (Bartlett dei rendimenti standardizzati), che e' proprio il bersaglio dichiarato nel §3 (Epps residuo
compreso). Non e' garantito rispetto alla correlazione vera, e le previsioni H hanno diagonale 1 mentre Σ_t ha diagonale
1 solo **in media** (fattore di scala): nei giorni in cui l'EWMA sbaglia la volatilita' la Stein premia in parte le
correlazioni che si muovono con quell'errore. E' il limite gia' dichiarato nel §4, che **N1 misura** (con il passaggio
al bersaglio alternativo se rifiuta). La fonte non lo risolve e non lo smentisce: nessun cambio.

## (c) "QLIKE piu' potente" vale nel caso multivariato? **Non dimostrato dalle fonti**

- PS: le simulazioni di potenza dei test DMW (pp. 20-23, figure 3 e 4) usano un **processo univariato** (σ²_t, due
  previsioni h^A e h^B) e concludono "These results all point to QLIKE as the preferred choice" (p. 23). Le conclusioni
  (p. 30) estendono la frase alla "multivariate generalisation" con "our small simulations suggested", ma nel testo non
  c'e' una simulazione di potenza multivariata.
- LRV: nessun confronto di potenza fra Stein e Frobenius; dice solo che un proxy piu' rumoroso aumenta la variabilita'
  della perdita e puo' rendere "impossibile discriminare fra i modelli" (p. 35).

**Cosa vuol dire per I3.** La scelta di Stein (Matteo, 21/11) resta giustificata dalla **consistenza** (a), non dalla
potenza, che nel caso multivariato e' **non verificata** (stato: quarantena). Frobenius resta lettura secondaria. Nessun
cambio di perdita.

## (d) Matrici di correlazione

- LRV considera solo previsioni di matrici di **covarianza**; per le correlazioni suggerisce soltanto una distanza
  euclidea pesata sui soli elementi sotto la diagonale, che "does not satisfy Proposition 4" (osservazione 2, p. 19).
- PS, nota 9 (p. 8): il proxy di correlazione realizzata "is not generally unbiased since it is a non-linear function
  of unbiased estimators".

**Cosa vuol dire per I3.** Applicare Stein a previsioni di correlazione contro la covarianza **standardizzata** (§4) e'
una costruzione nostra, non presa dalle fonti: la consistenza vale perche' il bersaglio e' una matrice di covarianza (dei
rendimenti standardizzati) e H ne e' una previsione, con il limite di (b). La nota 9 di PS **conferma** il caveat di
Jensen del bersaglio alternativo (§4): la giustificazione richiesta li' **non e' nelle fonti lette**, quindi, se N1
rifiuta, il passaggio al bersaglio alternativo resta subordinato a trovarla, come scritto.

## (e) Previsione del DCC a piu' passi — verificato, con una differenza

- ES, sezione 7 (pp. 20-22): due approssimazioni. (1) Q in avanti: E_t[Q_{t+r}] = Σ_{i=0}^{r−2}(1 − α − β)Q̄(α + β)^i
  + (α + β)^{r−1} Q_{t+1}, poi normalizzata; e' la formula del §6 (che si riscrive Q̄ + (α + β)^{r−1}(Q_{t+1} − Q̄)).
  (2) R in avanti, con Q̄ ≈ R̄ ed E_t[Q_{t+1}] ≈ E_t[R_{t+1}]. Nel Monte Carlo bivariato del testo nessuna delle due ha
  un errore quadratico uniformemente minore (rapporto "extremely close to 1"), la (2) e' un po' meno distorta, e il
  testo conclude che "a logical choice ... would be the method that directly solves forward Rt".
- Q̄ e' "the unconditional covariance of the standardized residuals resulting from the first stage" (p. 6); stima in
  due passi con verosimiglianza gaussiana in cui compare "log(|Rt|) + ε′R⁻¹ε" (p. 6).

**Cosa vuol dire per I3.** La formula del §6 e' quella del testo (approssimazione (1)) ma **non** quella che il testo
preferisce. Il DCC entra solo come benchmark forte e controllo positivo, dopo il passo 3: quale delle due
approssimazioni usare e' una **scelta da fare insieme al passo 3**, gratis fino ad allora (nessun dato del DCC visto). Il
resto del §6 (Q̄ come media delle Σ, stima per quasi-verosimiglianza gaussiana, in due passi) coincide.

## In sintesi

| punto | esito | conseguenza |
|---|---|---|
| (a) Stein e Frobenius consistenti | verificato | nessun cambio |
| (b) non distorsione condizionata | verificato | limite del §4, gia' misurato da N1 |
| (c) Stein piu' potente nel multivariato | non dimostrato (solo simulazioni univariate) | Stein resta per la consistenza; potenza in quarantena |
| (d) correlazioni | fuori dalle fonti | costruzione nostra dichiarata; bersaglio alternativo ancora senza giustificazione |
| (e) previsione del DCC a piu' passi | verificato, il testo preferisce la (2) | scelta al passo 3 |

Nessun punto blocca il download: nessuna fonte smentisce una scelta gia' fissata per la potenza (perdita, bersaglio,
benchmark EWMA, costante).
