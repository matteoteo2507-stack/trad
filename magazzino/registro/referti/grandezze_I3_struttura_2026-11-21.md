---
titolo: "I3 Struttura fra asset: controllo delle grandezze (passo 1)"
data: 2026-11-21
tipo: controllo
stato: quarantena
---

# I3 — controllo "stessa grandezza = stessa famiglia"

Passo 1 della famiglia I3 del [backlog §I](../../../decisioni/BACKLOG_RICERCA.md), prima di qualunque dato. Stesse regole
e stesso criterio del [controllo di I2](grandezze_I2_regimi_2026-11-20.md) (DECISIONS 2026-11-21): conta il
**bersaglio** che lo strumento prevede; stesso bersaglio con un'altra perdita = variante, bersaglio diverso = grandezza
diversa. Dal 21/11 entrano in I3 anche il beta dinamico fra due asset e i regimi di correlazione; la cointegrazione no
(famiglia nuova solo con un meccanismo scritto in DECISIONS). **Nessun dato letto, nessuna previsione: 0 trial.**

## La grandezza di I3

Le sei grandezze del [modulo 10 §2](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md) si leggono su un
prezzo solo. La struttura fra asset si legge solo su **piu' prezzi insieme**: e' la **dipendenza fra i rendimenti**
(correlazioni, e la loro scomposizione in fattori). Nessuna famiglia del contatore l'ha misurata come proprieta' di
uno strumento (verificato con `python -m motore.core.trial_ledger` il 21/11: nessun id fra asset).

**Il confine con `volatilita'`** (chiesto dal gatekeeper nel controllo di I2, riga 6a). Una covarianza e' correlazione
per due volatilita': σ_xy = ρ·σ_x·σ_y. La volatilita' di ogni asset (la diagonale) e' il bersaglio della famiglia
`volatilita`, in ridisegno su soli dati futuri (DECISIONS 2026-11-20 (2)). Proposta di confine:
- **il bersaglio di I3 e' la correlazione**, cioe' la dipendenza fra rendimenti gia' divisi per la loro volatilita';
- la volatilita' usata per dividerli e' un **ingresso fisso dichiarato prima** (per esempio l'EWMA 0,94 del pacchetto
  `volatilita_ewma` v1), mai una variante di I3 e mai confrontata dentro I3;
- un modello che prevede insieme varianze e correlazioni (DCC) entra in I3 **solo per la parte di correlazione**, con
  il primo stadio fissato come sopra; confrontare primi stadi diversi sarebbe un trial di `volatilita`.

**Persistenza meccanica.** Come in I2: una correlazione su finestra mobile condivide quasi tutta la finestra col giorno
dopo, quindi "la struttura di oggi somiglia a quella di domani" a un passo e' vera per costruzione. La stabilita' fuori
campione si legge solo su finestre non sovrapposte, o contro un nullo con la stessa sovrapposizione.

## Candidato per candidato

| # | candidato | bersaglio | grandezza | famiglia esistente | esito |
|---|---|---|---|---|---|
| 1 | **PCA sui rendimenti** | (a) quante direzioni indipendenti ha un paniere (spettro degli autovalori); (b) se i fattori stimati sul passato descrivono la dipendenza futura | correlazione | nessuna | **nuova**: e' il candidato di partenza di I3 |
| 2 | auto-encoder | come 1, con una scomposizione non lineare | correlazione (e dipendenza non lineare) | — | **variante di 1**, stessa famiglia. Il backlog la ammette solo se la PCA lascia struttura stabile non spiegata; ogni scelta di architettura e' un trial (C1, C3) |
| 3 | beta dinamico (Kalman sui rendimenti) | β = ρ·σ_y/σ_x fra due asset | correlazione × rapporto di volatilita' | — | **variante di I3** per la parte ρ; il rapporto σ_y/σ_x e' l'ingresso fisso del confine |
| 4 | regimi di correlazione (risk-on/risk-off, correlazioni che salgono nelle crisi) | correlazione futura condizionata allo stato | correlazione | — | **stessa famiglia**: e' la dinamica della grandezza 1 |
| 5 | modelli a fattori sul mercato (beta del CAPM, multi-fattore; [05](../../fondamenti_tecnici/05_portfolio_rischio/principles.md)) | esposizione a un fattore nominato | correlazione con un fattore dato | — | **stessa famiglia** per il beta; l'alpha (intercetta) e' un rendimento: strategia, ai soci |
| 6 | raggruppamento gerarchico, albero minimo, HRP | struttura della matrice di correlazione | correlazione | — | **varianti** di metodo della stessa famiglia |
| 7 | pulizia con matrici casuali (Marchenko-Pastur) | quali autovalori superano il rumore | correlazione | — | **metodo** dentro la famiglia (riferimento di rumore per 1a); non e' una famiglia |
| 8 | dipendenza nelle code (cadute congiunte, copule) | probabilita' di movimenti estremi insieme | dipendenza nelle code | — | **stessa famiglia** (dipendenza fra asset); le code del singolo asset restano di `volatilita` (G7) |
| 9 | dispersione fra asset (ampiezza dei rendimenti nella sezione trasversale) | dispersione di domani | circa σ²·(1 − ρ medio): volatilita' e correlazione insieme | `volatilita` per la parte σ² | **stessa famiglia** solo se il bersaglio e' scritto sulla parte di correlazione; altrimenti tocca `volatilita` |
| 10 | anticipo/ritardo fra asset (un mercato che anticipa un altro) | **rendimento futuro** di un asset dato il passato di un altro | direzione (primo momento), non dipendenza contemporanea | nessuna: le famiglie di tendenza usano il passato dello stesso asset | **fuori da I3**: e' una previsione di rendimento. Entra solo da `_INTAKE.md` con una fonte e una classe (modulo 09), non si genera qui. I canali di [03 §6](../../fondamenti_tecnici/03_regimi_macro/principles.md) sono dichiarati "meccanismi, non previsioni" |
| 11 | cointegrazione sui livelli | stazionarieta' di uno spread | spostamento dalla media di uno spread | — | **fuori da I3** (DECISIONS 2026-11-21, decisione 2) |

## Cosa esiste gia' sulla stessa grandezza

- **Il numero effettivo di strumenti indipendenti** del referto A1
  ([TREND_A1_HELDOUT_POWER](../documenti/TREND_A1_HELDOUT_POWER.md) §4 e §8): `n_eff = n/(1+(n−1)ρ)` con ρ medio
  misurato sui rendimenti D1 dal 2017-12-26 (crypto, indici, cross FX, energia, agricoli; azioni e futures nel §8). E'
  la domanda 1a di I3 in forma grezza, calcolata **dentro il campione** come conto di potenza, a 0 trial. Non e' una
  famiglia e non e' una validazione. Conseguenza: le correlazioni medie per classe su quella finestra sono **gia'
  viste**; la pre-registrazione di I3 deve elencarle fra le informazioni note e non puo' usarle come conferma.
- Il modulo 05 descrive la PCA come teoria (un esempio su 9 titoli: PC1 circa 27%), senza misura nostra.
- I dati D1 multi-asset sono stati usati da `tsmom` (fino al 2026-07-08) e `trend_momentum` (fino al 2026-08-14) per
  rendimenti di strategia, non per la correlazione. Per il criterio del bersaglio non sono una famiglia di I3; se e come
  contino come visti per l'holdout di I3 si decide nella pre-registrazione (H1, passo 3).

## Esito proposto (da confermare: gatekeeper, poi Matteo)

**I3 ha una grandezza nuova: la dipendenza fra i rendimenti (correlazione e fattori).** Una famiglia sola, con PCA,
auto-encoder, beta dinamico, regimi di correlazione, beta su fattori, raggruppamenti e dipendenza nelle code come
candidati o varianti al suo interno. Il confine con `volatilita'`: la volatilita' entra in I3 solo come ingresso fisso
dichiarato prima. Fuori da I3: l'anticipo fra asset (previsione di rendimento, solo da intake con fonte) e la
cointegrazione (decisione del 21/11).

Passo 2, dopo la conferma di Matteo: la classe (chi paga, limite all'arbitraggio, accessibilita'), poi la proprieta'
misurabile e il benchmark, poi la potenza coi dati in casa e i dati acquistabili (regola d'acquisto, backlog §G).

## Revisione del gatekeeper

*(da compilare con l'esito della revisione)*
