---
titolo: "I3 Struttura fra asset: controllo delle grandezze (passo 1)"
data: 2026-11-21
tipo: controllo
stato: quarantena
---

# I3 — controllo "stessa grandezza = stessa famiglia"

Passo 1 della famiglia I3 del [backlog §I](../../../decisioni/BACKLOG_RICERCA.md), prima di qualunque dato. Stesse regole
del [controllo di I2](grandezze_I2_regimi_2026-11-20.md) (DECISIONS 2026-11-21). Dal 21/11 entrano in I3 anche il beta
dinamico fra due asset e i regimi di correlazione; la cointegrazione no (famiglia nuova solo con un meccanismo scritto in
DECISIONS). **Nessun dato letto, nessuna previsione: 0 trial.** Revisione del gatekeeper in fondo: PASSA CON RISERVE,
0 bloccanti; le riserve sono applicate nel testo.

## Le due letture, e la grandezza di I3

La regola scritta (LIFECYCLE §3, modulo 10 §2) classifica per **ingresso** (cosa legge l'indicatore); il controllo di I2
ha usato anche il **bersaglio** (cosa prevede lo strumento). Qui le due letture **concordano**: le sei grandezze del
[modulo 10 §2](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md) si leggono su un prezzo solo, mentre la
struttura fra asset si legge solo su **piu' prezzi insieme** (prodotti incrociati di rendimenti). Il suo bersaglio e'
la **dipendenza fra i rendimenti**: correlazioni e la loro scomposizione in fattori.

Nessuna famiglia l'ha misurata come proprieta' di uno strumento. Il contatore lo conferma solo per nome (non ha un campo
grandezza, debito 1 di I2); la ricerca nei documenti fatta dal gatekeeper trova la correlazione solo come **uso**, mai
come proprieta' misurata (elenco in "Cosa esiste gia'").

## Il confine con `volatilita`

Una covarianza e' correlazione per due volatilita': σ_xy = ρ·σ_x·σ_y. La diagonale (la volatilita' di ogni asset) e' il
bersaglio della famiglia `volatilita`, in ridisegno su soli dati futuri (DECISIONS 2026-11-20 (2)).

**Regola del confine, una sola per tutte le righe.** Un confronto appartiene a I3 se tutte le previsioni confrontate,
benchmark compreso, usano **lo stesso ingresso di varianza fisso** e differiscono solo nella dipendenza. Se differiscono
nella parte di varianza e' un trial di `volatilita`; se differiscono in entrambe conta in tutte e due le famiglie. Con
questa regola una perdita sulla varianza di un portafoglio resta legittima in I3.

**L'ingresso fisso** (proposta, decisione di Matteo D2):
- **σ: EWMA con λ = 0,94**, come formula (non "il pacchetto validato", che non ha proprieta' dimostrate), scelto perche'
  e' lo standard dichiarato prima e non ha parametri stimati, **non** guardando gli esiti di `volatilita` (nello sviluppo
  il GJR batte l'EWMA su 10 coppie su 10 degli indici, [report del pacchetto](../../../uscita/volatilita_ewma/v1/report.md)
  §1: scegliere ora un primo stadio diverso sarebbe una selezione dopo l'esito presa da un'altra famiglia, S4 e S6);
- la **definizione del giorno** si fissa con l'ingresso (il pacchetto usa il giorno 17:00-17:00 di New York; le chiusure
  D1 del broker sono un'altra costruzione);
- la **distribuzione marginale** (necessaria a copule e DCC stimato per verosimiglianza) si fissa con σ: confrontare
  marginali diverse e' territorio di G7 di `volatilita`.

**Cosa I3 non riporta.** Le diagnostiche del primo stadio (media di z², Ljung-Box su z², curtosi, livello della varianza
di portafoglio) misurano la calibrazione dell'EWMA. Se la finestra di I3 tocca quella del ridisegno di `volatilita`,
I3 non le riporta, oppure le dichiara alla pre-registrazione del ridisegno fra le informazioni gia' ricevute. Se I3
legge il blocco sigillato 2024-11-11 → 2026-11-10, lo dichiara (nota N3, DECISIONS 2026-11-20 (2)): dopo, per
`volatilita`, non sarebbe piu' "mai toccato dalla pipeline".

**Stessa teoria?** Il DCC deriva dalla teoria GARCH, ma la regola del 2026-10-25 (8) ("stessa teoria = stessa
famiglia") riguarda un'altra ipotesi dalla stessa teoria; qui cambia la grandezza prevista, quindi vale la famiglia
nuova.

**Persistenza meccanica.** Una correlazione su finestra mobile condivide quasi tutta la finestra col giorno dopo: "la
struttura di oggi somiglia a quella di domani" a un passo e' vera per costruzione. La stabilita' fuori campione si legge
solo su finestre non sovrapposte, o contro un nullo con la stessa sovrapposizione.

**Chiusure non sincrone.** Su D1 mercati che chiudono a orari diversi (DAX alle 17:30 di Francoforte, indici USA alle
16:00 di New York, FX alle 17:00, crypto a 24 ore) spostano parte della dipendenza contemporanea sul ritardo di un
giorno. La correzione (somma dei termini a ritardo 0 e 1, o campionamento sincrono) e' una **correzione di misura dentro
I3**, non una previsione di rendimento; usare il termine ritardato per prevedere un rendimento e' la riga 10.

## Candidato per candidato

| # | candidato | bersaglio | esito |
|---|---|---|---|
| 1 | **PCA** | (a) quante direzioni indipendenti ha un paniere: autovalori della matrice di **correlazione** dei rendimenti divisi per l'ingresso fisso (una PCA sulla covarianza metterebbe la volatilita' negli autovalori); (b) se i fattori stimati sul passato descrivono la dipendenza futura | **nuova**: candidato di partenza di I3 |
| 2 | auto-encoder | come 1, scomposizione non lineare | **variante di 1**. La condizione del backlog ("solo se la PCA lascia struttura stabile non spiegata") la attiva dopo l'esito della PCA: o si elenca con la sua condizione nella pre-registrazione del round 1 (P4), o e' selezionata dai dati e si conta e si testa su dati non visti (S6, P3). Ogni scelta di architettura e' un trial (C1, C3) |
| 3 | beta dinamico (Kalman sui rendimenti) | β = ρ·σ_y/σ_x | **variante di I3 solo** se il filtro gira sui rendimenti standardizzati con l'ingresso fisso (allora β = ρ) o se la perdita e' scritta su ρ; altrimenti vale la regola del confine. Sui rendimenti grezzi il filtro stima β come stato unico e non separa ρ da σ_y/σ_x |
| 4 | regimi di correlazione (correlazioni che salgono nelle crisi) | correlazione futura condizionata allo stato | **stessa famiglia**; un condizionamento sullo stato di volatilita' e' un filtro imputato a I3 |
| 5 | beta su fattori (CAPM, multi-fattore, [05](../../fondamenti_tecnici/05_portfolio_rischio/principles.md)) | esposizione a un fattore nominato | **stessa famiglia** per il beta, con la stessa nota della riga 3; l'alpha (intercetta) e' un rendimento: strategia, ai soci |
| 6a | raggruppamento gerarchico, albero minimo | struttura della matrice di correlazione | **varianti** di metodo |
| 6b | HRP | **pesi di portafoglio**, valutati sulla varianza del portafoglio | allocazione: in I3 solo con la regola del confine (stessa varianza in ingresso, cambia solo la dipendenza); altrimenti e' una regola di gestione del rischio che testano i soci (04 §0, LIFECYCLE §4quater) |
| 7 | pulizia con matrici casuali (Marchenko-Pastur) | quali autovalori superano il rumore | **metodo** dentro la famiglia |
| 8 | dipendenza nelle code (cadute congiunte, copule) | probabilita' di estremi insieme | **stessa famiglia**, con la marginale fissata dall'ingresso; le code del singolo asset restano di `volatilita` (G7) |
| 9 | dispersione fra asset | dispersione dei rendimenti **standardizzati** = funzione di 1 − ρ medio | **stessa famiglia** in questa forma; sui rendimenti grezzi contiene σ² e tocca `volatilita` |
| 10 | anticipo/ritardo fra asset | **rendimento futuro** di un asset dato il passato di un altro | **fuori da I3**: previsione di rendimento, cioe' una strategia che testano i soci, nel contatore unico. Entra solo con una fonte da `_INTAKE.md` o dall'hub con la scheda d'ingresso (LIFECYCLE §8); quote al 21/11: esterne 2026-Q4 piena (3 di 2-3), hub 0 di 1. La correzione per le chiusure non sincrone resta dentro I3 (sopra) |
| 11 | cointegrazione sui livelli | stazionarieta' di uno spread | **fuori da I3** (DECISIONS 2026-11-21, decisione 2) |

**Altri candidati, solo come classificazione**

| candidato | bersaglio | dove ricade |
|---|---|---|
| reversione dei residui dopo la PCA (arbitraggio statistico) | rendimento di uno spread | spostamento dalla media, come la riga 11: **fuori da I3**. E' lo scivolamento piu' probabile da I3 a una strategia |
| ricadute di volatilita' fra asset (HAR multivariato, termini incrociati di un BEKK) | varianza | `volatilita`: solo nel ridisegno, come serie contata, su dati futuri |
| correlazione fra prezzo e volatilita' (indice contro VIX, effetto leva) | asimmetria della volatilita' | `volatilita` (e' cio' che modella il GJR) |
| correlazione implicita (indici del CBOE) come previsione della realizzata | correlazione | I3. Il suo **premio** (implicita meno realizzata) e' un'altra domanda, come `premio_vol` dentro `volatilita`; la dispersione sulle opzioni e' una strategia fuori perimetro. Solo classificazione, non un candidato da aprire |
| momentum fra asset (classifica per rendimento passato) | rendimento relativo | tendenza (CLOSED) o strategia: fuori da I3 |
| correlazione condizionata a variabili macro | correlazione | I3 per il bersaglio, anche se l'ingresso e' fuori dal prezzo (diverso dai regimi macro di I2, dove il bersaglio era il rendimento) |
| connettivita' alla Diebold-Yilmaz | si divide | ricaduta di rendimento → riga 10; di volatilita' → `volatilita`; parte contemporanea → I3 |
| volume e liquidita' che si muovono insieme fra asset | microstruttura | I4 |

## Cosa esiste gia' sulla stessa grandezza

**Misure gia' calcolate, quindi gia' viste** (vanno elencate nella pre-registrazione di I3 e non possono confermare
nulla sugli stessi insiemi e nelle stesse finestre):

| misura | insieme | finestra | dove |
|---|---|---|---|
| ρ medio per classe e `n_eff = n/(1+(n−1)ρ)` | pool libero Dukascopy (crypto, indici, cross FX, energia, agricoli) | dal 2017-12-26, calcolo del 21/09 | [TREND_A1_HELDOUT_POWER](../documenti/TREND_A1_HELDOUT_POWER.md) §4 |
| ρ medio: azioni USA +0,323, futures +0,112 | azioni offerte dal broker con storia Dukascopy; futures pysystemtrade | stessa finestra, calcolo del 03/10 | stesso referto §8 |
| ρ medio per classe e per braccio di volatilita' | futures pysystemtrade | dal 2010, dal 2000, dal 1990, fino al 2024-03-28; calcolo del 25/10 | stesso referto §9, `magazzino/registro/codice/trend/a1_potenza_finestra.py` |

La domanda 1a ("quante direzioni indipendenti") su quegli insiemi e in quelle finestre e' quindi un **descrittivo gia'
calcolato**, dentro il campione, come conto di potenza.

**Dati delle famiglie di tendenza.** `tsmom` (fino al 2026-07-08) e `trend_momentum` (fino al 2026-08-14) hanno usato i
D1 multi-asset per **rendimenti di strategia**, non per correlazioni; la pre-registrazione TSMOM ne parla solo in modo
qualitativo. Per il criterio di DECISIONS 2026-11-21 (3) i dati restano visti solo per la stessa grandezza: **per I3
non sono visti**, salvo le misure della tabella sopra. Al passo 3 resta solo la data d'inizio del blocco (H1).

**Conoscenza da memoria** (Checklist 5). "Le correlazioni salgono nelle crisi" (riga 4) e la correlazione positiva fra
azioni e obbligazioni nel 2022 sono fatti famosi, gia' nel modulo 05 e in DECISIONS 2026-06-14 senza misura nostra:
confermarli porta poca informazione nuova. Va annotato nella pre-registrazione.

**Usi della correlazione senza proprieta' misurata:**
- `correlazione_dichiarata` e `correlazione_in_drawdown` in `motore/core/verifiche.py` (righe 290 e 533): strumenti di
  verifica in uso, non una famiglia; il codice di I3 li **riusa**, non li riscrive;
- il ragionamento del PAC su azioni e obbligazioni (DECISIONS 2026-06-14) e i buchi 46 e 48 di Quant Guild
  (DECISIONS 2026-09-15);
- il modulo 05 come teoria (PCA su 9 titoli, PC1 circa 27%: numero della fonte, non nostro).

## Esito proposto

**I3 ha una grandezza nuova: la dipendenza fra i rendimenti (correlazione e fattori).** Una famiglia sola, con PCA,
auto-encoder, beta dinamico, regimi di correlazione, beta su fattori, raggruppamenti, dipendenza nelle code e dispersione
standardizzata come candidati o varianti. Confine con `volatilita` con la regola dell'ingresso fisso. Fuori da I3:
anticipo fra asset e momentum fra asset (rendimenti), reversione dei residui e cointegrazione (spread), ricadute di
volatilita' (`volatilita`).

## Decisioni per Matteo

- **D1 — Aprire I3** come famiglia del binario strumenti, sulla grandezza "dipendenza fra i rendimenti", con la regola
  del confine sopra.
- **D2 — Ingresso fisso**: EWMA λ = 0,94, definizione del giorno e distribuzione marginale fissate insieme, prima di ogni
  dato.
- **D3 — Il passo 2 per uno strumento di rischio.** La domanda "chi paga, limite all'arbitraggio" e' il punto 5 della
  definizione di **strategia** (04 §0). Per una misura di rischio non c'e' un chi paga: il modulo 10 §2 lo scrive per la
  volatilita' ("nessuna: e' una misura di rischio") e la pre-registrazione della volatilita' non ha una classe. Applicata
  alla lettera, la regola del modulo 09 ("un candidato senza classe e' un pattern") ucciderebbe I3 per un errore di
  procedura. Proposta: al passo 2 la classe si dichiara ("nessuna: misura di rischio") e si cerca solo per un'eventuale
  sottofamiglia di premio; il resto del passo 2 segue il §8ter (proprieta', bersaglio, perdita, benchmark, MDE).
- **Prima della bozza di pre-registrazione (passo 2):** §8ter G1-G3 e la Checklist 10 punti 1-2 sono scritti per la
  varianza (varianza realizzata, QLIKE, EWMA). Per un bersaglio di correlazione perdita e benchmark vanno **decisi da
  Matteo** al passo 2, non scoperti alla G1.

## Debito di protocollo emerso (non corretto qui)

1. §8ter G1-G3 non hanno un gate per un bersaglio diverso dalla varianza.
2. Il criterio del bersaglio non e' nel testo del LIFECYCLE §3 ne' del modulo 10 §2; se I3 si apre, al modulo 10 §2
   manca una riga "fra asset: dipendenza" fuori dalle sei.
3. Il contatore non ha un campo grandezza (debito 1 di I2, ancora aperto).
4. La procedura passo 1 / 2 / 3 per le famiglie di strumenti non e' scritta ne' nel backlog §I ne' nel §8ter.
5. Nessuna regola per una famiglia che usa come ingresso fisso l'uscita di un'altra famiglia in ridisegno, sugli stessi
   dati futuri; la regola dei dati futuri del 20/11 vincola i soci, non `trad`.
6. Nessuna regola per le grandezze composte (covarianza = volatilita' × correlazione): la regola del confine andrebbe
   scritta in §3 o in §8ter.

## Revisione del gatekeeper (2026-11-21)

**PASSA CON RISERVE**: 0 bloccanti, 11 riserve, tutte applicate: PCA sulla correlazione (R1); ingresso fisso senza
"per esempio", giorno, marginale, diagnostiche e blocco sigillato, regola unica del confine, nota sulla stessa teoria
(R2); beta solo su rendimenti standardizzati (R3); HRP separato (R4); auto-encoder come selezione dopo l'esito (R5);
anticipo fra asset con le due porte e le chiusure non sincrone (R6); misure A1 complete, dati della tendenza decisi ora,
conoscenza da memoria (R7); candidati mancanti (R8); doppia lettura (R9); passo 2 senza "chi paga" alla lettera e
perdita da decidere (R10); usi esistenti e limite della verifica col contatore (R11). Il debito sopra viene dalla
stessa revisione. Prima del passo 2 vanno chiuse R1, R2, R9 e R10: R1 e R9 nel testo, R2 e R10 con le decisioni D2 e D3.
