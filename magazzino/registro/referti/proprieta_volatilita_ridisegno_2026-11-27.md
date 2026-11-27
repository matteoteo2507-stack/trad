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
contata, stesse origini per l'EWMA), VIX_t delle 16:15 ET per v_{t+1}, fine settimana nella conversione, trasformazione
del GEX in previsione QLIKE (per esempio c_t·EWMA_t·exp(β_t·1{GEX<0}), solo il segno; il livello e' una variante
contata), test, G9, chiavi d'uscita. Il GEX si misura contro l'EWMA, non contro EWMA+VIX (S4), e un esito si legge come
contenuto in piu', non come meccanismo.

## Scelte tecniche del passo 2 (bozza del 27/11, prese insieme, P6)

Tutte prima di ogni calcolo su VIX o GEX. Costo di un cambio: gratis fino al commit di congelamento, salvo la forma del
VIX (informata, sotto); deviazione P5 dopo il commit; dopo la dispersione solo i cambi elencati in "Scelte rinviate".

**Classe**: nessuna (misura di rischio, modulo 10 §2). Il premio non resta come sottofamiglia (decisione 3).

**Bersaglio** (G1): v_{t+1} dell'SPX500 come nella pre-registrazione del 13/11 §3 (giorno XNYS, notte + quadrati di
seduta da M5 Dukascopy, giorni esclusi al 90%), h = 1. Stessi giorni, stesse origini per tutti i modelli: un'origine
senza VIX o senza GEX valido e' esclusa per tutti e si conta.

**Perdita** (G2): QLIKE primaria, con la soglia minima 1e-100 della deviazione del 19/11; MSE descrittiva.

**Benchmark** (G3, S4): EWMA λ = 0,94 sui rendimenti r_t, riscalata con c_t sui 1.000 giorni (§3 del 13/11), per tutte
e tre le sottofamiglie. Riferimenti solo descrittivi: persistenza, media di lungo periodo, HAR.

**Sottofamiglia VIX** (quota 1,25%), due varianti nello SPA studentizzato (C2):
- **V1 grezzo**: f = VIX_s² / 252 (VIX in punti percentuali annui; k = 1/252, varianza per giorno di borsa, senza
  correzione per il fine settimana). Nessun c_t: il VIX e' esterno e si confronta con v, come il premio.
- **V2 ricalibrato**: f = κ_t · VIX_s² / 252, κ_t = Σ v_{u+1} / Σ VIX_u²/252 sulle coppie della finestra di 1.000
  giorni con v_{u+1} gia' osservato all'origine (solo passato). Assorbe il livello, non il giorno della settimana.
- Dichiarata come **informata** dalla forma del premio (asimmetria −8,74, curtosi 91,7, `esiti/descrittivo_premio.json`,
  commit `b0df760`): S6 e P3, confermativa solo perche' il test e' forward.
- s = ultimo VIX noto prima della chiusura di riferimento: vedi **D9** sotto (problema di orario trovato il 27/11).

**Sottofamiglia GEX** (quota 1,25%, condizionata al permesso entro il 2027-01-31), una variante:
f = c_t·EWMA_t × m_t(segno)/m̄_t, con segno = 1{GEX_{t−1} < 0} (valore datato del giorno prima, ritardo di cautela;
GEX = 0 conta come positivo), m_t(s) = Σ v / Σ c·EWMA sui giorni della finestra di 1.000 con quel segno, m̄_t lo stesso
rapporto su tutti i giorni. Usa solo il segno; il livello sarebbe una variante contata. Un esito si legge come
contenuto in piu' rispetto all'EWMA, non come prova del meccanismo (il segno e' correlato alla volatilita' recente).
Le istantanee del forward: una al giorno, datata, sha256, confronto sui giorni in comune; se un valore passato cambia
fra due istantanee vale la prima istantanea che lo contiene. **Solo con permesso scritto**: istantanee quotidiane sono
un prelievo sistematico.

**Sottofamiglia GARCH** (quota 2,5%): GARCH(1,1), GJR, EGARCH come il 13/11, contro l'EWMA. Strumenti: vedi **D8**.

**Test** (G4): per ogni sottofamiglia un'ipotesi, SPA studentizzato (`spa_studentizzato`) delle sue varianti contro
l'EWMA (anche con una sola variante, per uniformita'), bootstrap stazionario con blocco √T, ripetizioni e semi come il
13/11; procedura grafica sui tre nodi (VIX 1,25%, GEX 1,25%, GARCH 2,5%), riciclo in parti uguali dopo un rifiuto. Se
il GEX esce prima dell'inizio, il suo nodo si toglie e la quota resta riservata.

**Controllo di dimensione** (B-c), per ogni nodo, prima del forward: bootstrap stazionario del differenziale di
sviluppo riportato a media zero, lunghezza = 504 giorni di borsa (due anni), il test pre-registrato del nodo, 2.000
repliche; passa se rifiuta in <= 2 × quota. **Conseguenza scritta ora**: un nodo che fallisce esce prima dell'inizio
del forward, con la quota riservata (come §7.7 del 13/11).

**Dispersione per la potenza** (decisione 2): deviazione Newey-West (4 ritardi) del differenziale QLIKE di ogni
variante contro l'EWMA sullo sviluppo SPX500 (2015-2024, origini comuni); per un nodo con piu' varianti si riporta solo
la massima. Guardia: nessuna media, nessun segno. **Trial**: VIX 2, GEX 1 (se la storia del GEX si scarica, una volta,
a mano); GARCH 0 (le sue serie di sviluppo SPX500 a h = 1 sono gia' fra le 126).

**Effetto di riferimento per l'MDE** (passo (d)): il guadagno GARCH di sviluppo sugli indici a h = 1, gia' visto
(0,054-0,081 di QLIKE, pre-registrazione §11, 19/11), e un effetto minimo d'interesse di 0,05 di QLIKE. Non la media
del VIX.

**G9**: positivo e negativo su processo noto. Negativo VIX: varianza vera da IGARCH (l'EWMA e' esatta), VIX simulato =
varianza vera EWMA × rumore lognormale; positivo VIX: VIX simulato = varianza vera GJR × rumore, con il rapporto
effetto/MDE scritto prima. Stesso schema per il GEX (segno simulato legato o no a un regime di varianza). Dettagli nel
commit di congelamento.

**Guardie del codice**: (1) il blocco sigillato si legge solo con un flag `SOLO_STIMA` che consente finestre di stima e
vieta ogni perdita con bersaglio dal 2024-11-11 in poi fino all'inizio del forward (decisione 1); (2) dispersione e
controllo di dimensione escono solo con chiavi ammesse (deviazioni, frequenze, conteggi); (3) hash di SPX500 M5, VIX,
GEX nel file versionato.

**Trial del forward** (C1): VIX 2 + GEX 1 + GARCH (3 × strumenti di D8) serie, contate quando si calcolano.

**Scelte rinviate a dopo la dispersione** (P6 (3)): solo il numero di ripetizioni dello SPA (dalla soglia) e, se un
controllo di dimensione fallisce, l'uscita del nodo. Lunghezza fissata: due anni (decisione 7).

### Due decisioni nuove per Matteo

- **D8 — strumenti del nodo GARCH.** (a) **solo SPX500** (3 serie; tutto il ridisegno su un solo strumento e un
  orizzonte, "meno ipotesi" al massimo); (b) gli indici come domanda unica (perdita media sugli indici, un'ipotesi; poca
  potenza in piu', gli indici sono molto correlati). *Raccomandata (a).*
- **D9 — orario del VIX (trovato il 27/11).** Il VIX di chiusura e' fissato alle **16:15 New York**, mentre il giorno
  dell'SPX500 chiude alle **16:00** (ultima barra 15:55). I 15 minuti dopo le 16:00 appartengono alla notte di v_{t+1}:
  usare il VIX di chiusura di t e' un **look-ahead** di 15 minuti. (La consultazione del gatekeeper parlava di 17:00:
  vale per gli strumenti a 24 ore, non per gli indici.) Opzioni: (a) **VIX del giorno prima** (s = t−1): nessun
  look-ahead, penalizza un po' il VIX, dichiarato; (b) VIX registrato da noi alle 15:55 ogni giorno del forward (serve
  un raccoglitore e la storia per κ resta quella delle 16:15, solo passato); (c) dati intraday del VIX acquistati.
  *Raccomandata (a)*: semplice, conservativa, il VIX e' molto persistente.

## Scadenze e debito

- ✅ Il descrittivo del premio (asimmetria e curtosi, 13/11) e' ora versionato: `descrittivo_premio.py` (commit
  `b0df760`), esito `esiti/descrittivo_premio.json` (n 2358, −8,74, 91,7: coincide col 13/11), 27/11, 0 trial.
- Debito di protocollo: nessuna regola sul blocco sigillato come finestra di stima; C1 non dice che una dispersione fra
  candidato e benchmark conta trial.
