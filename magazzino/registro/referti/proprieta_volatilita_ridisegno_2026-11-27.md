---
titolo: "Volatilita', ridisegno: proprieta' e potenza (passo 2) — consultazione del gatekeeper e decisioni aperte"
data: 2026-11-27
tipo: referto
stato: quarantena
---

# Ridisegno di `volatilita` — passo 2, punto di partenza

Passo 2 della procedura del [LIFECYCLE §8ter](../../../motore/metodo/STRATEGY_LIFECYCLE.md), dopo il
[passo 1](grandezze_volatilita_ridisegno_2026-11-24.md) (DECISIONS 2026-11-24 (7)). **Stato: aperto. Le sette decisioni della tabella sotto sono prese il 27/11, tutte
sull'opzione piu' sicura ([DECISIONS 2026-11-27 (2)](../../../decisioni/DECISIONS.md)), con GEX a scadenza
2027-01-31; restano le scelte tecniche.** Qui c'e' l'esito della consultazione di metodo chiesta da Matteo al gatekeeper il 27/11 (sola lettura, 0
trial), per non perderlo fra una sessione e l'altra; il referto vero del passo 2 si scrive sopra questo, con le
decisioni.

## Tre buchi che nessuna regola copre (bloccanti alla G1 se restano aperti)

- **B-a. Il blocco sigillato come finestra di stima.** Un forward che parte a dicembre 2026 ha finestre mobili (EWMA,
  c_t su 1.000 giorni, ricalibrazione del VIX) quasi tutte dentro il blocco 2024-11-11 → 2026-11-10, "sigillato senza
  uso" (DECISIONS 2026-11-20 (2); `giorni.py` si ferma per costruzione). Un fattore ΣRV/ΣIV su quel blocco e' una
  statistica del premio sul periodo sigillato anche se non stampata. E' una **regola di protezione** (P6 del §8ter):
  decide Matteo in DECISIONS. Opzioni: (i) blocco ammesso **solo come ingresso di stima**, nessuna perdita, nessun
  fattore stampato, guardia nel codice (precedente: I3 legge il blocco dichiarandolo); (ii) finestre che ripartono
  dall'inizio del forward (riscaldamento perso, niente c_t a 1.000 giorni). Piu' sicura per il gatekeeper: (i).
- **B-b. La dispersione VIX contro EWMA costa trial.** In I3 la dispersione era fra benchmark e riferimento (0 trial);
  qui e' fra candidato e benchmark: C1 conta ogni variante di cui si calcolano le previsioni (varianti × orizzonti).
  Alternativa a 0 trial: dispersione proxy (EWMA contro persistenza o media), piu' grezza. Da decidere prima.
- **B-c. Controllo di dimensione.** Il differenziale QLIKE VIX-EWMA ha la stessa coda del premio, il nodo uscito il
  13/11 (dimensione 14,6-16,0% contro <= 2,5%). Prima di fissare quote e lunghezza: bootstrap a blocchi del
  differenziale di sviluppo riportato a media zero, lunghezza del forward, test pre-registrato, criterio <= 2 × quota.
  Esce solo la frequenza di rifiuto.

## Ordine dei lavori

(a) Scelte di disegno e misura nel referto, prima di ogni calcolo, con l'**elenco delle scelte rinviate** a dopo la
dispersione (lunghezza, semi); quote e B-a decise da Matteo prima della dispersione. (b) Commit di congelamento
(referto, codice, test sintetici, guardie; modello: commit (1) di I3). (c) Gatekeeper sul diff, poi la sola dispersione
HAC **sui dati di sviluppo** (G6; Newey-West max(h−1, 4) ritardi, origini comuni; con due varianti solo la massima delle
deviazioni) e il controllo di dimensione, con la stessa guardia. (d) Rapporto effetto/MDE prima del G9 positivo:
l'effetto di riferimento non dalla media del VIX, ma da un effetto minimo dichiarato o dai guadagni GARCH di sviluppo
gia' visti (0,054-0,081 sugli indici a h = 1). (e) Lunghezza e MDE ex ante, bozza di pre-registrazione, passate G1.
**L'approvazione e' la data d'inizio del forward** (e della regola dei dati futuri per i soci e per I3).

## Decisioni per Matteo, con l'opzione piu' sicura secondo il gatekeeper

| # | decisione | opzioni | piu' sicura | tipo |
|---|---|---|---|---|
| 1 | blocco sigillato come stima (B-a) | ammesso con guardia / finestre dal forward | ammesso con guardia | protezione (Matteo) |
| 2 | dispersione per la potenza (B-b) | differenziale vero, contato / proxy a 0 trial | differenziale vero, contato prima | Matteo |
| 3 | quote | (A) VIX 1,25 dal premio, GEX 1,25 dall'HMM, GARCH 2,5; (B) VIX 2,5, GEX 1,25; (C) solo VIX | (A) o (B), l'HMM rinuncia (potenza attesa 2,1%); il premio rinuncia salvo un test di dimensione gia' provato | budget (Matteo) |
| 4 | forma del VIX | grezzo (VIX²·k, k fissato ora) / ricalibrato (ΣRV/ΣIV, 1.000 giorni) / entrambi | entrambi nello SPA studentizzato, dichiarato come informato dal descrittivo del premio; a + b·IV sconsigliato | presa insieme, **non gratis** |
| 5 | orizzonti | 1 / 1 e 5 / 30 giorni di calendario | h = 1; h = 5 solo se la potenza regge; 30 sconsigliato | presa insieme |
| 6 | GEX | esce ora / condizionato | condizionato: disegno congelato, data d'attivazione, **scadenza**, quota che non passa al VIX se esce; permesso scritto chiesto da Matteo | Matteo |
| 7 | lunghezza del forward | due anni / altra fissata dopo dispersione e dimensione | due anni, MDE ex ante ed ex post, nessuna estensione | metodo (Matteo) |

Scelte tecniche da prendere insieme (P6): convenzione k, finestra di ricalibrazione, giorni senza VIX (origine esclusa e
contata, stesse origini per l'EWMA), ~~VIX_t delle 16:15 ET per v_{t+1}~~ (⚠️ superato: e' un look-ahead, D9 sotto), fine settimana nella conversione, trasformazione
del GEX in previsione QLIKE (per esempio c_t·EWMA_t·exp(β_t·1{GEX<0}), solo il segno; il livello e' una variante
contata), test, G9, chiavi d'uscita. Il GEX si misura contro l'EWMA, non contro EWMA+VIX (S4), e un esito si legge come
contenuto in piu', non come meccanismo.

## Scelte tecniche del passo 2 (seconda bozza del 27/11, prese insieme, P6)

Tutte prima di ogni calcolo su VIX o GEX. Costo di un cambio: gratis fino al commit di congelamento, salvo le scelte
**informate** segnate sotto; deviazione P5 dopo il commit; dopo dispersione, dimensione e G9 solo i cambi elencati in
"Scelte rinviate". **Revisione del gatekeeper sulla prima bozza (27/11): BLOCCA il congelamento** (4 bloccanti, 14
riserve, la direzione regge); questa seconda bozza le applica, salvo le decisioni di Matteo in fondo.

**Provenienza** (Checklist 5, R14): idea di Matteo da un'intervista, candidati raccomandati da Claude; il VIX come
previsore della volatilita' e' letteratura famosa: una conferma porta poca informazione nuova (come Carr-Wu al 13/11).
Il forward oltre il cutoff del modello rende il test non contaminabile.

**Classe**: nessuna (misura di rischio, modulo 10 §2). Il premio non resta come sottofamiglia (decisione 3).

**Bersaglio** (G1): v_{t+1} dell'SPX500 come nella pre-registrazione del 13/11 §3 (giorno XNYS che chiude con la barra
delle 15:55, cioe' alle 16:00; notte + quadrati di seduta da M5 Dukascopy; giorni esclusi al 90%), h = 1.

**Origini** (B1): comuni **dentro ogni nodo** (le varianti del nodo e l'EWMA), non fra nodi. Un'origine senza VIX esce
solo dal nodo VIX, una senza GEX solo dal nodo GEX; il GARCH usa tutte le origini valide per il bersaglio. Si contano per
nodo. **Finestre del forward**: VIX e GARCH 504 giorni di borsa dall'approvazione della pre-registrazione; GEX 504 giorni
dalla sua attivazione (aggiunta datata, entro il 2027-01-31). **La procedura grafica gira una volta, alla fine
dell'ultimo nodo**, con i p di tutti; nessun verdetto parziale prima.

**Perdita** (G2): QLIKE primaria, soglia minima 1e-100 (deviazione del 19/11); MSE descrittiva.

**Benchmark** (G3, S4): EWMA λ = 0,94 sui rendimenti r_t, riscalata con c_t sui 1.000 giorni (§3 del 13/11), per tutti
e tre i nodi. Riferimenti solo descrittivi: persistenza, media di lungo periodo, HAR. Si riporta c dell'SPX500 con la
direzione dell'effetto (R4).

**Nodo VIX** (quota 1,25%), due varianti nello SPA studentizzato (C2). s = l'origine del VIX secondo **D9**.
- **V1 grezzo**: f = VIX_s² / 252 (k = 1/252: VIX 20 da' 1,59 %² al giorno; nessuna correzione per il fine settimana).
  **Senza c_t** (decisione 4 e §3 del 13/11, "Premio e scala"). Svantaggio di costruzione dichiarato (R4): il premio
  sposta il livello del VIX, e un errore di livello del 40% vale circa 0,05 di QLIKE, l'ordine dell'MDE; c pesa invece
  circa 0,001 a ±5%. Vedi **D10** (V1 con c_t).
- **V2 ricalibrato**: f = κ_t · VIX_s² / 252, κ_t = Σ v_{u+1} / Σ VIX_{s(u)}²/252 sulle coppie della finestra di 1.000
  giorni con v_{u+1} gia' osservato all'origine (solo passato; con D9 (a), coppie (VIX_{u−1}, v_{u+1})).
- **Informata** (S6, P3) dalla forma del premio (asimmetria −8,74, curtosi 91,7, `esiti/descrittivo_premio.json`,
  commit `b0df760`): confermativa solo perche' il test e' forward.

**Nodo GEX** (quota 1,25%, condizionato: permesso scritto di SqueezeMetrics entro il 2027-01-31, decisione 6).
Fornitore: SqueezeMetrics, CSV pubblico `date,price,dix,gex`; DIX esclusa. Una variante (R5):
f = EWMA_t × m_t(segno_{t−1}) / m̄_t, con m_t(s) = Σ v_{u+1} / Σ EWMA_u sulle coppie (v_{u+1}, EWMA_u, segno_{u−1}) della
finestra di 1.000 giorni con quel segno, m̄_t lo stesso rapporto su tutte le coppie; c si semplifica e non si usa (niente
finestre annidate). Segno = 1{GEX < 0}, GEX = 0 positivo. **Ritardo t−1 obbligatorio** finche' l'ora di pubblicazione
non e' documentata (vincolo 3 del 24/11). Minimo **50 giorni** di ciascun segno nella finestra, altrimenti m/m̄ = 1 (la
variante coincide con l'EWMA) e si conta. Con segno non informativo m/m̄ → 1: il nullo contiene il benchmark. Un esito
si legge come contenuto in piu' rispetto all'EWMA, non come prova del meccanismo. **Una sola variante con lo SPA**
invece del DM-HLN della lettera di G4: deviazione dichiarata, per uniformita' fra nodi.

**Nodo GARCH** (quota 2,5%): GARCH(1,1), GJR, EGARCH come il 13/11, contro l'EWMA. Strumenti: **D8**. Le scelte (a) e
(b) sono informate dallo sviluppo (il GARCH vince sugli indici, perde su metalli ed FX): S6, P1, dichiarato.

**Test** (G4): per nodo un'ipotesi, SPA studentizzato (`spa_studentizzato`) delle varianti contro l'EWMA, bootstrap
stazionario con blocco √T, ripetizioni e semi del 13/11 (100.000 per seme, 4 semi, regola dell'intervallo intero sotto
la soglia corrente); procedura grafica sui nodi attivi (VIX 1,25%, GEX 1,25%, GARCH 2,5%), riciclo in parti uguali dopo
un rifiuto. Un nodo uscito prima dell'inizio si toglie e la sua quota resta riservata per il round 2.

**Controllo di dimensione** (B-c, B4), per nodo, prima del forward, sui differenziali di sviluppo SPX500 riportati a
media zero: bootstrap stazionario esterno con blocco medio **21 e 63 giorni** (devono passare entrambi, come il 13/11),
lunghezza 504 giorni, **2.000 repliche**, SPA studentizzato dentro ogni replica con **10.000 ripetizioni**, regola del
**p puntuale** (b+1)/(B+1) sotto la quota iniziale del nodo (come i positivi del 19/11; differenza dalla regola del
forward dichiarata: il p puntuale e' meno severo dell'intervallo, quindi il controllo e' prudente), semi
**20261201-20261203** (uno per nodo). Passa se rifiuta in <= 2 × quota. Si riporta accanto, come informazione, la
frequenza al livello massimo raggiungibile col riciclo (5%) (R12). **Conseguenza scritta ora**: un nodo che fallisce
esce prima del forward, quota riservata al round 2.

**Dispersione per la potenza** (decisione 2): sd Newey-West (4 ritardi) del differenziale QLIKE di ogni variante
contro l'EWMA sullo sviluppo SPX500 2015-2024, origini comuni nel nodo; per nodo solo la **massima**. Funzione nuova
(R8): non si riusa `mde_coppie` di `potenza.py`, che sceglie la variante con la media. Guardia: nessuna media, nessun
segno.

**Effetto di riferimento per l'MDE** (R7): **0,05 di QLIKE**, unico e uguale per i tre nodi (circa il 40% di errore di
livello), dichiarato come informato dai guadagni GARCH gia' visti; il guadagno GARCH dell'SPX500 a h = 1 solo come
contesto.

**G9** (B4), su processi noti, criterio **80%** per i positivi e **<= 2 × quota** per i negativi, 200 repliche, seme
20261204; **conseguenza**: un positivo che fallisce fa uscire il nodo prima del forward (come §7.7 del 13/11), quota
riservata al round 2.
- GARCH: processi e rumore di `neg_garch` e `pos_garch` (IGARCH λ 0,94; GJR del 13/11), σ del rumore dell'SPX500 da
  `esiti/sviluppo.json` (gia' visto).
- VIX: varianza vera GJR; positivo: VIX simulato = varianza vera del giorno dopo × exp(σ_V ε − σ_V²/2), σ_V = 0,5
  fissato ora; negativo: VIX simulato = varianza EWMA × lo stesso rumore (il candidato e' strettamente peggiore: trova
  guasti, **non** prova il confine del nullo, che prova la dimensione, R11).
- GEX: processo a due regimi di varianza (rapporto 1,5, persistenza 0,95) con il segno simulato uguale al regime nel
  positivo e indipendente nel negativo.
- Rapporto effetto/MDE scritto prima delle corse, come il 19/11.

**Controllo positivo sui dati reali** (R10, QUANT_REVIEW_PROTOCOL): l'analogo del §7.6 del 13/11, variante iniettata
tarata sullo sviluppo SPX500 (`tara_w` di `potenza.py`) con guadagno pari all'MDE ex ante: deve rifiutare nel forward
simulato; criterio 80%, conseguenza come il G9.

**Guardie del codice** (B3): (1) flag `SOLO_STIMA`, distinto da `HOLDOUT_APERTO` (che resta legato al passo 8 del
13/11), che consente di leggere il blocco 2024-11-11 → inizio del forward solo per le finestre di stima e **rifiuta
l'uscita** di perdite, di κ, c, m e di ogni aggregato con finestra nel blocco; test sintetico che provi il rifiuto.
Residuo dichiarato: dalle previsioni del forward salvate si puo' risalire a κ_t delle prime origini. (2) Dispersione,
dimensione e G9 escono solo con chiavi ammesse (deviazioni, frequenze, conteggi). (3) Dati del forward (R13): istantanee
datate per SPX500 M5, VIX e GEX, ciascuna con sha256 e data di scarico; vale la prima istantanea che contiene un giorno;
confronto sui giorni in comune; un giorno mancante resta mancante (origine esclusa e contata); un cambio di fornitore e'
una deviazione P5.

**Contabilita'** (B2): una serie (modello × strumento × orizzonte) si conta **una volta, al primo calcolo**. VIX 2 e GEX 1
alla dispersione; GARCH 0 (le serie SPX500 a h = 1 sono gia' fra le 54); il forward non aggiunge trial. Nel contatore,
al congelamento: sottofamiglie `vix` e `gex` con quota, provenienza e parentela del GEX (D0 del 24/11), round 0 → 1 alla
pre-registrazione, poi `--check`. Debito: il LIFECYCLE §8ter C1 non dice quando una serie si conta.

**Scelte rinviate a dopo dispersione, dimensione e G9** (P6 (3)): solo le ripetizioni dello SPA del forward (dalla
soglia) e l'uscita dei nodi che falliscono. Tutto il resto e' fissato qui.

### Decisioni per Matteo

- **D8 — strumenti del nodo GARCH.** (a) **solo SPX500** (3 serie gia' contate); (b) gli indici come domanda unica; (c)
  il nodo GARCH rinuncia e la quota resta riservata. *Raccomandata (a).*
- **D9 — orario del VIX.** Il VIX di chiusura e' fissato alle **16:15 New York** (13:15 nelle sedute ridotte), il giorno
  dell'SPX500 chiude alle **16:00**: i 15 minuti stanno in v_{t+1}, usare il VIX di t e' un **look-ahead** (confermato
  dal gatekeeper, che corregge la sua regola delle 17:00; fonte Cboe da citare nella pre-registrazione). Opzioni:
  (a) **VIX del giorno prima**: nessun look-ahead, il nodo misura "il VIX di ieri" contro l'EWMA di oggi, costo
  d'informazione ignoto (misurarlo costerebbe trial); (b) registrazione alle 15:55: scartata, le quote gratuite sono
  ritardate di 15 minuti e sviluppo, κ e dimensione sarebbero su un'altra variabile; (c) **VIX intraday acquistato**:
  l'unica che tiene sviluppo, κ e forward sullo stesso orario senza ritardo, serve un preventivo; (d) spostare il taglio
  del giorno alle 16:15: scartata, cambia il bersaglio del 13/11 e le serie GARCH non sarebbero piu' fra le 126.
  *Raccomandata (a) come default*, (c) solo se il preventivo e' basso (coi payout, regola del 07/11).
- **D10 — V1 con c_t** (R4, informata). (a) V1 senza c_t come deciso (svantaggio di costruzione dichiarato); (b)
  V1 = c_t · VIX²/252. La differenza e' piccola (circa 0,001 di QLIKE): *raccomandata (a)*, non cambiare la decisione 4.
- **D11 — quando si calcola la dispersione del GEX** (R6). (a) Subito, con lo scaricamento unico; (b) **solo se arriva
  il permesso**: senza permesso il nodo esce e il trial sarebbe speso a vuoto. *Raccomandata (b).*

## Scadenze e debito

- ✅ Il descrittivo del premio (asimmetria e curtosi, 13/11) e' ora versionato: `descrittivo_premio.py` (commit
  `b0df760`), esito `esiti/descrittivo_premio.json` (n 2358, −8,74, 91,7: coincide col 13/11), 27/11, 0 trial.
- Debito di protocollo: nessuna regola sul blocco sigillato come finestra di stima; C1 non dice che una dispersione fra
  candidato e benchmark conta trial.
