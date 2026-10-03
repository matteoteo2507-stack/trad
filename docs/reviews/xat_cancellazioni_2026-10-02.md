---
tipo: analisi
stato: verificabile
aggiornato: 2026-10-02
fonte_dati: "export XAT in _export_telegram/ (al 02/10) contro due registri live indipendenti: conto demo del socio (22 segnali, 21-29/09) e journal del nostro copier (9 segnali XAT, 02-08/06)"
nota: "Fatto sui dati, non un verdetto sull'edge. Mette in discussione la base di ogni misura storica di XAT, compreso lo stato CONFERMATO. Decisioni aperte nel §5."
---
# XAT cancella i segnali andati male: l'export non è il track record

> Trovato il 02/10 mentre preparavo il test della variante del socio (bracket fisso 1:1 e 1:2 a 200 pip).
> **Nessun esito della variante è stato calcolato e il trial non è stato speso:** con questo difetto i dati
> storici non possono rispondere alla domanda (§4).

## 1. Il confronto

Ogni segnale eseguito dal vivo ha un orario certo. Lo si cerca nell'export Telegram (fuso Europe/Rome,
verificato oggi: 92,1% delle entrate postate nel range eseguibile dei 5 minuti precedenti, contro un
massimo del 62% con qualunque offset fisso).

**Conto demo del socio, 21-29/09** ([review del 30/09](analysis_team_live_2026-09-30.md)). La latenza
fra il NOW nell'export e il fill è **0-1 s** su tutti i segnali trovati, quindi l'abbinamento è certo.

| Segnale (UTC) | Esito della copia | Nell'export |
|---|---|---|
| 23/09 10:59 BUY | **stop pieno** | assente: buco di 4 id nei messaggi fra le 08:11 e le 14:11 (ora italiana) |
| 25/09 05:19 SELL | **stop pieno** | assente |
| 25/09 05:54 SELL | TP1 poi BE (+0,06R) | assente |
| 25/09 08:26 SELL | **stop pieno** | assente |
| 25/09 08:50 SELL | **stop pieno** | assente: i quattro del 25/09 cadono in un **buco di 13 id** fra le 04:51 e le 13:59 (ora italiana), senza nessun messaggio in mezzo |
| 22/09 05:01 BUY | TP1 poi BE | il NOW c'è, il messaggio coi livelli no (buco di 1 id subito dopo) |
| gli altri 16 | — | presenti, NOW e livelli |

**Journal del nostro copier, 02-08/06** (`logs/signal_copier_journal.jsonl`): 9 segnali XAT eseguiti o
scartati dal gate. **1 assente** dall'export: BUY del 03/06, NOW alle 13:30 UTC e livelli alle 13:31,
registrati dal journal (entrata **4449**, SL **4439**, TP1 **4454**). Nell'export al suo posto mancano gli
id **5514-5519**. Sui prezzi Dukascopy perde **anche sui livelli del mentore**, non solo sulla copia:
entrata toccata alle 13:31, SL alle 13:42, TP1 solo alle 14:10.

**Totale: 6 segnali assenti su 31 registrati dal vivo (19%; intervallo di Wilson al 95%: 9-36%). Di
questi, 5 hanno l'esito noto di uno stop pieno.** Dei 5 stop pieni della settimana del socio, 4 sono
spariti.

Il confronto fra due export successivi, previsto dal §6.1 della pre-registrazione OOS (tasso di
cancellazione 0,2%), **non poteva vederli**. Coglie solo i messaggi presenti nel primo export e assenti nel
secondo, mentre questi spariscono entro pochi giorni, prima di qualunque export.

**Controprova con l'export del 18/09** (ripristinato dall'utente in `_export_telegram_VECCHIO_2026-09-18/`,
confronto con [confronta_export.py](../../analysis/mentor_signals/confronta_export.py)):

- fra il 18/09 e il 02/10 sono spariti **solo 2 messaggi di spam** (0,05%) e nessun segnale. Nessun
  testo e' stato modificato e nessun id e' stato inserito a posteriori;
- gli id mancanti fino al 18/09 sono **identici** nei due export. Il segnale del 03/06 mancava gia' il 18/09.

Quindi i segnali spariscono **prima** che un export li possa vedere (quelli di fine settembre entro pochi
giorni), e dopo non si tocca piu' niente. Per questo il confronto fra export misura ~0% **per
costruzione**: e' lo stesso 0,2% della pre-registrazione OOS, e non dice niente sul tasso vero.

## 2. Quanto spazio c'è nella storia

Fra febbraio e settembre 2026 mancano **725 id** di messaggio contro 3.745 visibili (**16,2%**). Non sono
tutti segnali: il 18/09 sono stati cancellati anche messaggi di spam. Ma lo spazio per cancellazioni
sistematiche c'è in ogni mese, da 62 a 115 id al mese.

## 3. Cosa vuol dire per l'edge

L'E[R] a TP1 di riferimento, **+0,1265 su 629 trade** (DECISIONS 2026-09-18 (4)), è misurato **solo sui
segnali sopravvissuti**. Si può calcolare la quota di segnali cancellati che basterebbe ad azzerarlo, senza
nuovi esiti. Ipotesi: i cancellati sono stop pieni (−1,03R con i costi del motore), come 5 dei 6 osservati.

- Pareggio: **77 segnali cancellati**, cioè l'**11%** del totale.
- Stima dal vivo: **19%** (9-36%).

**Il segno dell'edge storico di XAT non è più determinato dai dati che abbiamo.** Alla stima puntuale
sarebbe negativo; al limite basso dell'intervallo resterebbe positivo. Due cautele:

- per 5 dei 6 l'esito è quello **della copia**, che entra in ritardo: sul bracket postato dal mentore
  qualcuno potrebbe essersi salvato. L'unico di cui conosciamo i livelli (03/06) perde anche sui suoi;
- 31 segnali sono pochi per la stima del tasso.

Il dato però è coerente: i cancellati sono quasi tutti perdenti. È la forma di selezione che gonfia un track
record, e nessuna quantità di dati in più dallo stesso export la cura ([[feedback_campione_selezionato_non_piccolo]]).

È anche una spiegazione **possibile** dei 4 stop pieni rimasti sul bracket provvisorio nella settimana del
socio: se il trade va male subito, il mentore forse non posta i livelli e cancella il NOW. Non è verificato.

## 4. Perché la variante del socio non si testa su questi dati

Il test confronterebbe la variante (20 $ di stop) e l'esecuzione attuale **sugli stessi segnali
sopravvissuti**. La selezione è fatta sull'esito del mentore con la sua geometria. Quindi gonfia l'E[R] di
**entrambi** i bracci, in misura diversa e non stimabile, e la condizione "E[R] della variante > 0" non si
può leggere. Spendere il trial ora produrrebbe un numero **plausibile e non interpretabile**. Lo stesso vale
per la misura storica del gate (b) su cui il DECISIONS del 02/10 voleva tarare i monitor prima del capitale.

## 5. Cosa resta valido e cosa si decide

**Resta valido, anzi diventa l'unica misura pulita: la demo live da lunedì 05/10.** Il copier esegue i
segnali prima che vengano cancellati, quindi il suo journal è il track record vero. Due condizioni:

1. **Registrare l'id Telegram di ogni messaggio ricevuto**, e se possibile gli eventi di cancellazione e di
   modifica. Oggi `logs/messages_received.jsonl` salva solo orario, canale e testo. Con l'id, ogni export
   futuro si confronta col journal e il tasso di cancellazione si misura, invece di stimarlo.
2. **Nessuna soglia del test dal vivo si tara sullo storico** finché il §3 non è risolto.

**Decisioni di Matteo:**
- **Stato di XAT**: `CONFERMATO` poggia su un campione selezionato. Le opzioni sono
  (a) declassarlo a `in revisione` finché la demo non lo rimisura, oppure (b) lasciarlo con l'avvertenza
  nel frontmatter. Raccomando la (a): un'evidenza nota per essere selezionata non conferma niente.
- **Variante del socio**: rimandarla a quando ci sarà un registro live abbastanza lungo, oppure farla
  girare in demo dal 05/10 in parallelo, come forward puro con la sua pre-registrazione. Un trial speso ora
  sullo storico non comprerebbe informazione.
- **Gump** (D3 "non misurabile"): lo è con lo stesso metodo. Basta confrontare i trade live del socio su
  Gump con il suo export.

## Limiti

31 segnali live in due finestre (giugno e fine settembre). L'esito dei cancellati è quello della copia
ritardata. L'abbinamento si fa per orario, con latenza di 0-1 s nei casi trovati. I buchi negli id non
dicono che cosa è stato cancellato.
