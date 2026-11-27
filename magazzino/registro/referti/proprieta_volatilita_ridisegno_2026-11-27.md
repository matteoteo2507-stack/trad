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

## Scadenze e debito

- Il descrittivo del premio (asimmetria e curtosi, 13/11) vive solo in un transcript che si cancella intorno al
  **13/12/2026**: va citato nella pre-registrazione prima, o ricalcolato da uno script versionato (stessi numeri gia'
  visti, 0 trial).
- Debito di protocollo: nessuna regola sul blocco sigillato come finestra di stima; C1 non dice che una dispersione fra
  candidato e benchmark conta trial.
