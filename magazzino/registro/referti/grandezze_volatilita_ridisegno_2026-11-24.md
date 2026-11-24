---
titolo: "Volatilita', ridisegno: controllo delle grandezze dei candidati nuovi (passo 1)"
data: 2026-11-24
tipo: controllo
stato: quarantena
---

# Ridisegno di `volatilita` — controllo "stessa grandezza = stessa famiglia"

Passo 1 della procedura del [LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md) per il ridisegno della
famiglia `volatilita` (DECISIONS 2026-11-20 (2): pre-registrazione nuova della stessa famiglia, round 0 → 1 di 3,
test su dati futuri successivi alla sua data). I candidati nuovi vengono da DECISIONS 2026-11-24 (3) (opzioni come
lente, [backlog §I1](../../../decisioni/BACKLOG_RICERCA.md)). Stesse regole dei controlli di
[I2](grandezze_I2_regimi_2026-11-20.md) e [I3](grandezze_I3_struttura_2026-11-21.md): grandezza per **ingresso** e per
**bersaglio**, teoria, famiglie esistenti, misure gia' calcolate. **Nessun dato letto, nessuna previsione: 0 trial.**

**Revisione del gatekeeper (24/11).** Prima passata: **BLOCCA**, un bloccante (B1, la regola della teoria non
applicata a B) e nove riserve, applicate nel testo; B1 chiuso dalla decisione di Matteo D0 (DECISIONS 2026-11-24 (7)).
Seconda passata: **PASSA CON RISERVE**, 0 bloccanti, sei riserve applicate (puntatore nel LIFECYCLE §3 e riga in
`decisioni/mappa/_modifiche.md`; direzione opposta della parentela; istantanee del GEX come condizione; fatti di c e
del GARCH precisati; esito di B dopo D0; divieto del backlog con la sua eccezione). **Passo 1 chiuso.**

## Provenienza (Checklist 5)

Idea di Matteo dopo un'intervista (una sola fonte, allineata con chi vende i livelli; scheda nell'hub,
`knowledge/sources/yt/words-of-rizdom-filliger-algoritmi-opzioni.md`); i due candidati sono **raccomandati da Claude**
(DECISIONS 2026-11-24 (3)). "La volatilita' implicita prevede la realizzata" e' un risultato noto in letteratura (claim
in quarantena). Sono proposti **dopo** aver visto le perdite di sviluppo della famiglia (sotto, "Dati gia' visti"): il
test su dati futuri toglie il rischio sul verdetto, ma la provenienza resta dichiarata.

## Perimetro

| # | candidato | in questo controllo |
|---|---|---|
| A | **volatilita' implicita come previsione** della varianza (VIX su SPX500; VXN su NAS100 e GVZ sull'oro come estensioni possibili) | si' |
| B | **segno (e livello) della gamma dei dealer** come informazione sulla varianza del giorno dopo (GEX SqueezeMetrics, solo S&P 500) | si' |
| C | nodi riservati: GARCH (2,5%), HMM (1,25%), premio di volatilita' (1,25%) ([pre-registrazione §11](../documenti/VOLATILITA_PREREGISTRATION.md), 13/11 e 20/11) | no: gia' della famiglia; quali restano ("meno ipotesi") si decide al passo 2 |

## A — volatilita' implicita

**Ingresso.** Il VIX e' fra gli indicatori della grandezza 3, **Volatilita'**, del
[modulo 10 §2](../../fondamenti_tecnici/10_indicatori_tecnici/principles.md) (riga della tabella: "ATR, deviazione
standard, larghezza delle Bollinger, Keltner, VIX"). *(Corretto dopo la revisione, R1: la prima versione diceva che non
era fra le sei grandezze.)*

**Bersaglio.** La varianza realizzata: il bersaglio di `volatilita` (G1). Ingresso e bersaglio concordano: A e' una
**sottofamiglia di `volatilita`**.

**Il legame col premio.** Il nodo del premio (pre-registrazione §3 e §5) usa **la stessa coppia**: IV_t = VIX_t² ×
30/365 contro la varianza realizzata dell'SPX500 nei 30 giorni di calendario dopo. Le proprieta' sono due:
- **premio**: E[IV − RV] > 0 (un livello);
- **previsione (A)**: QLIKE(IV) < QLIKE(EWMA) (un'accuratezza).
Non sono indipendenti: la QLIKE punisce una previsione distorta, e molto di piu' una previsione troppo bassa. Se A entra
nella sottofamiglia del premio, la quota dell'1,25% riservata a "un test adatto a questa coda" (DECISIONS 2026-11-13 (3))
cambia ipotesi: va scritto (R5).

**Dati gia' visti** (da elencare nella pre-registrazione):
1. `motore/data/cache/free/VIX_D1.csv` (CBOE, 1990 → 2026-11-12), hash in [`hash_dati.json`](../codice/volatilita/hash_dati.json).
2. **Premio giornaliero di sviluppo** dell'SPX500 (2.358 osservazioni), calcolato il 13/11. Nel codice versionato
   `dimensione_premio` (`controlli.py`) sottrae la media e restituisce solo frequenze di rifiuto e conteggi
   ([`esiti/dim_premio.json`](../codice/volatilita/esiti/dim_premio.json)). **Asimmetria −8,7 e curtosi in eccesso 92**
   (pre-registrazione §11) **non escono da codice versionato**: vengono da uno script lanciato a mano nella sessione
   `f47827df` del 13/11 (20:26 UTC; il transcript si cancella intorno al 13/12), che ha chiamato `premio_giornaliero()` con l'holdout chiuso e ha stampato solo "n 2358 asimmetria
   -8.74 curtosi in eccesso 91.7" e la prova del test su rumore gaussiano (0,0145 e 0,012). Ricostruito dal gatekeeper
   sui transcript, che Claude Code cancella dopo 30 giorni. **La media non risulta stampata** in nessun esito, referto,
   voce di DECISIONS o file di `uscita/`, ne' nei transcript cercati: verificato in modo forte, non certo (R2).
3. **Regola dell'1% sul VIX**, 03/10 ([ricerca_repo_2026-10-03](ricerca_repo_2026-10-03.md); DECISIONS 2026-10-03 (4)):
   VIX incrociato con SPX500 D1 dal 2012-01-18 al 2026-08-13, 35 eventi contati (19 al rialzo, 16 al ribasso) e
   deviazione standard giornaliera dell'SPX 1,03%. Il periodo **comprende il blocco oggi sigillato**: per la nota N3
   (DECISIONS 2026-11-20 (2)) si dichiara (R4a).
4. **Perdite di sviluppo** dell'EWMA e dei concorrenti su tutti e nove gli strumenti, SPX500 compreso
   ([`esiti/sviluppo.json`](../codice/volatilita/esiti/sviluppo.json), pre-registrazione §11): il GARCH batte l'EWMA
   sugli indici a h = 1 (0,054-0,081, indici in generale, non solo SPX500); c medio fra 0,955 (NAS100) e 1,265 (WTI),
   fra strumenti diversi; il pacchetto
   [`uscita/volatilita_ewma/v1`](../../../uscita/volatilita_ewma/v1/report.md) (GJR sugli indici); le diagnostiche
   dell'EWMA di I3 (R4b).
5. **Letteratura**: premio positivo in media sull'S&P 500 (claim in quarantena, referto del 10/11).
6. VXN e GVZ: **non in casa**, mai letti; i bersagli (NAS100 M5, XAU M1) sono gia' stati usati dalla famiglia.

**Esito.** Trial di `volatilita`, sottofamiglia nuova o estensione del premio (passo 2). Proposta dopo gli esiti delle
altre sottofamiglie: per S6 si conta e il suo test usa dati non visti, cioe' i dati futuri gia' imposti dal ridisegno.

## B — segno della gamma dei dealer

**Ingresso.** Una **stima** della gamma aggregata dei dealer sulle opzioni dell'S&P 500, costruita dal fornitore dagli
open interest per strike con un'**ipotesi sul segno** (white paper SqueezeMetrics, dicembre 2017: dealer lunghi di call
e corti di put). Non e' una delle sei grandezze e non e' la varianza implicita di A. **Grandezza nuova per ingresso.**

**Bersaglio.** La varianza realizzata dell'SPX500 del giorno dopo (o dei 5 giorni dopo): bersaglio di `volatilita`. Il
meccanismo dichiarato (coperture che smorzano con gamma positiva, amplificano con gamma negativa) e' un'affermazione
sulla varianza, non sulla direzione.

**Teoria: qui le regole divergono (bloccante B1 del gatekeeper).** Il LIFECYCLE §3 ha due righe:
- *stessa grandezza = stessa famiglia* (ingresso e bersaglio): porta B in **`volatilita`**;
- *stessa teoria = stessa famiglia* (DECISIONS 2026-10-25 (8)): B usa **lo stesso meccanismo** di
  `momentum_ultima_mezzora` (H1, CLOSED il 12/10: coperture di chi e' corto di gamma; backlog righe H1 e 175-177). Presa
  alla lettera, B sarebbe un trial di H1, cioe' una **riapertura** (§7, §7a: stessa voce del contatore, binario
  `strategie`, quota esterne del 2026-Q4 gia' piena).
Lo stesso vale per il caso ORB: in F1 "l'ORB funziona per via del gamma" e' scritto come condizione di riapertura di
`opening_range` (backlog §F). Il precedente (ADX, 21/11) dice che quando le letture divergono decide Matteo in
DECISIONS. Le opzioni sono in D0.

Argomento per la lettura del bersaglio, da pesare: la riga della teoria nasce per "un altro evento previsto dallo stesso
modello" (stessa proprieta', previsione diversa). H1 e B traggono dalla stessa teoria due proprieta' **diverse**: H1 il
segno del rendimento a fine giornata, B la varianza del giorno dopo. Un esito su H1 non dice niente su B, e viceversa.
Classificare B in `volatilita` non ricarica budget: la quota viene dalle riserve di una famiglia al 5% e il test usa
dati futuri.

**Dati gia' visti.** Nessun file scaricato. Il 24/11 un agente ha letto il CSV pubblico (`date,price,dix,gex`) fino al
2014-01-10 per verificarne l'esistenza, e ha riportato in sessione solo intestazione, prime righe e due valori (un GEX
negativo il 2011-06-07, uno a 0 il 2012-07-23): periodo di sviluppo, nessuna misura contro la varianza.

**Esito (D0 = a, 24/11).** Sottofamiglia nuova di `volatilita`, solo SPX500, S6 (si conta, test su dati non visti),
parentela `parente` verso `momentum_ultima_mezzora` e `opening_range` dichiarata a mano nella pre-registrazione e nel
campo `parentela`: `--check` non lo impone. Un esito del GEX **non** e' evidenza esterna per riaprire le due famiglie;
H1 o l'ORB condizionati al GEX sono una riapertura sul binario `strategie` (DECISIONS 2026-11-24 (7)). Ammesso ma
testabile solo con le istantanee del vincolo 4 (o un permesso scritto), da decidere al passo 2 prima della quota.

## Vincoli che il passo 2 deve fissare

1. **Quote** (R5). Le riserve sono legate per scritto al test forward **di ciascun nodo** (pre-registrazione §11, 20/11).
   Il passo 2 dice da quale nodo vengono le quote di A e B, e che quel nodo rinuncia in tutto o in parte al suo test.
2. **VIX nel giorno G1** (R7). Il VIX chiude alle 16:15 ET, prima delle 17:00 che chiudono il giorno: si usa per t+1.
   Da fissare: giorni con barra del CFD e senza VIX (festivi CBOE, mezze giornate); weekend quando si riporta la varianza
   a 30 giorni di calendario a 1 o 5 giorni di borsa; una scala con parametri si stima solo su finestra passata mobile,
   come c_t (pre-registrazione §3). **VIX grezzo o ricalibrato** non e' una scelta gratis: asimmetria e curtosi del premio
   (dato gia' visto 2) dicono gia' che il VIX sta di solito sopra la realizzata e sotto nei picchi, cioe' cio' che conta
   per la QLIKE. La scelta si dichiara come informata da quel descrittivo (R3).
3. **GEX: ora di disponibilita'.** Il GEX del giorno t usa open interest pubblicati a fine giornata; se l'ora non e'
   documentata, ritardo di un giorno.
4. **GEX: revisioni e licenza** (R6). Un CSV rifatto dal fornitore puo' ricalcolare i valori passati: scaricare una
   volta a fine periodo sarebbe look-ahead. Servono istantanee periodiche datate, con sha256 e data di scarico, e il
   confronto fra istantanee sui giorni in comune. I termini vietano il prelievo sistematico e non danno licenza: senza
   istantanee compatibili coi termini (o un permesso scritto), **B non ha dati futuri validi**. DIX esclusa (variante
   contata se usata dopo).
5. **Potenza senza vedere le perdite** (R8). L'MDE sul differenziale VIX contro EWMA chiede la sua deviazione standard,
   che sui dati di sviluppo e' un confronto vietato prima della dichiarazione dei candidati. Ordine, come in I3 (§8ter P6
   (3)): tutte le scelte in un commit, poi la sola dispersione HAC con una guardia che non stampi media e segno.
6. **Nessuna "fonte nuova mai vista"** (R8). La storia del GEX e del VIX (2011-2024, o il blocco sigillato) **non** vale
   come fonte nuova della regola del 20/11: i bersagli sono gia' visti (sviluppo) o sigillati. Il test e' solo forward.

## Fuori perimetro

- Livelli delle opzioni (call wall, put wall, volatility trigger) come segnali: DECISIONS 2026-11-24 (3).
- FX: nessun indice di volatilita' implicita in casa; non cercato.
- Black-Scholes, Heston, SABR: teoria senza previsioni testate (S1).

## Conseguenze della pre-registrazione, non di questo controllo

Alla **data** della pre-registrazione del ridisegno partono la regola dei dati futuri per i soci (DECISIONS 2026-11-20
(2)) e, per I3, gli obblighi del §8ter "Ingresso fisso da un'altra famiglia". Questo controllo non le fa partire.

## Decisioni per Matteo

**Prese il 24/11** ([DECISIONS 2026-11-24 (7)](../../../decisioni/DECISIONS.md)): **D0 = (a)**, **D1 si'**, **D2 solo
SPX500**. Le proposte restano sotto come erano.

- **D0 (bloccante B1).** Classificazione di B: (a) **sottofamiglia di `volatilita`**, la lettura del bersaglio
  prevale perche' H1 e B prevedono proprieta' diverse, parentela dichiarata (*raccomandata*); (b) riapertura di
  `momentum_ultima_mezzora` via §7, binario `strategie`, non prima del 2027-Q1 per la quota esterne piena; (c) B fuori dal
  ridisegno. Costo: gratis (nessun dato visto la riguarda).
- **D1.** A (e B, se D0 = a) come sottofamiglie di `volatilita`. *Raccomandata.* Gratis.
- **D2.** Strumenti di A: solo SPX500, oppure anche NAS100 (VXN) e oro (GVZ). *Raccomandato solo SPX500* (potenza).
  Gratis per P6 (1), ma proposta dopo le perdite di sviluppo (dato gia' visto 4): si dichiara.
- **D3** (passo 2): VIX grezzo o ricalibrato (informata, R3), orizzonti, A col premio o separata, quote e nodi che
  restano, ordine della stima di potenza.

## Debito di protocollo emerso

I descrittivi calcolati a mano su dati reali (asimmetria e curtosi del 13/11) non lasciano traccia versionata. Proposta
del gatekeeper: ogni numero sui dati reali citato in un documento esce da uno script versionato con un esito salvato. E
`--check` non vede la regola della teoria: la controlla solo il gatekeeper.
