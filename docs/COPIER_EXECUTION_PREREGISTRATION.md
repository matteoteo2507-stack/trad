---
tipo: preregistrazione
stato: IN AVVIO
aggiornato: 2026-09-30
decisione: "DECISIONS 2026-09-18 (4) — correzione dell'ora applicata due volte"
metrica_corrente: "E[R] segnale a TP1 +0,1265 [+0,0756; +0,1736], 629 trade; gate asimmetrico 20 pip: +0,159 [+0,076; +0,239]"
nota: "In demo sul PC del socio dal 21/09, con un setup diverso dal §2 e senza il gate C5 attivo (il flusso NOW lo spegne): 22 segnali descrittivi in reviews/analysis_team_live_2026-09-30.md. Conteggio N=60 da decidere (§8). Il +0,194 nel corpo è superato."
---
# Pre-registrazione — Test di ESECUZIONE del copier (segnali mentore XAUUSD)

> **Vincolante, scritta il 2026-08-14 PRIMA di avviare il copier in modalità `live`.**
> Nessun trade è ancora stato eseguito su questo conto. Le soglie non si modificano dopo aver
> visto i numeri; ogni modifica va datata e dichiarata in §8.
>
> Ciclo: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md).
> Presupposto: [MENTOR_SIGNALS_OOS_PREREGISTRATION.md](MENTOR_SIGNALS_OOS_PREREGISTRATION.md) —
> l'edge del **segnale** è **CONFERMATO** fuori campione (63,0% direzione vs 35,0% random;
> E[R] **+0,194** dopo costi, BCa95 [+0,079, +0,289]).

---

## 1. La domanda — diversa da quella già risposta

L'OOS ha stabilito che **il segnale** ha valore. **Non** ha stabilito quanto ne arriva sul conto.

Nella settimana di test live di giugno il gate anti-ritardo ha **scartato 5 segnali su 12** perché il
prezzo si era già mosso oltre 20 pip. Se quel tasso è rappresentativo, oltre un terzo dei segnali non
viene mai eseguito — e i segnali scartati **non sono un campione casuale**: sono quelli che si sono
mossi più in fretta, cioè plausibilmente i migliori.

**H1**: l'edge sopravvive all'esecuzione reale — E[R] **catturato** > 0 dopo costi, slippage e
segnali persi.
**H0**: l'esecuzione erode l'edge fino ad annullarlo.

Grandezza descrittiva centrale: **capture ratio** = E[R] catturato / E[R] del segnale (+0,194).

## 2. Setup — congelato

| | |
|---|---|
| Conto | MetaQuotes-Demo **5054470558**, **HEDGING**, 100.000 EUR |
| Terminale | `C:\Program Files\MetaTrader 5\terminal64.exe` — **installazione separata** da quella FPM che ospita il forward degli EA |
| Canale | `XAUUSD_AnalysisLab` (parser `xauusd_analysislab`), entrata sul trigger "NOW" |
| Rischio | **1% per segnale**, splittato su **3 gambe** (una per TP) |
| Gate anti-ritardo | **20 pip** — **CONGELATO**, vedi §6 |
| Gestione | SL/TP armati sul broker all'apertura; BE dopo TP1; trailing a TP3→TP1; flatten su "Close" |
| Magic | 27050 (distinto da 26071 nxt_fade e 26052 orb_nasdaq) |

**Isolamento**: conto e terminale separati dal forward degli EA. Nessuna competizione di margine —
è la lezione del 12/08, dove il dropout per margine ha distorto un campione.

## 3. Regola di stop

**N = 60 trade ESEGUITI**, oppure **8 settimane** dall'avvio in `live` — vale il primo evento.

*Potenza, dichiarata onestamente*: con SD della R su uscita TP1 ≈ 0,58, a N=60 l'errore standard è
≈ **0,075R**. Quindi:
- **Ben stimati a N=60**: tasso di rifiuto (±12 punti percentuali), distribuzione dello slippage,
  latenza, capture ratio come stima puntuale. Sono le risposte descrittive che ci servono.
- **NON conclusivo a N=60**: la *significatività* di E[R] catturato. Per un lower bound > 0 servirebbe
  E[R] > ~0,147, cioè quasi il valore pieno del segnale. Da qui il disegno a due stadi.

## 4. Soglie — fissate ORA

### Stadio 1 · N = 60 eseguiti (o 8 settimane)

| Esito | Decisione |
|---|---|
| E[R] catturato **≤ 0** (stima puntuale) | **KILL** — l'esecuzione annulla l'edge. Traccia archiviata, nessuna rifinitura del gate |
| E[R] catturato **> 0** | **PROSEGUE** allo Stadio 2. **Nessuna promozione a capitale dichiarabile qui** |

### Stadio 2 · N = 120 eseguiti (o 16 settimane)

| Esito | Decisione |
|---|---|
| **BCa 95% lower bound su E[R] catturato > 0** | **VIABILE** su capitale proprio → decisione di sizing, separata e scoped |
| Altrimenti | **KILL** |

Se N < 30 alla scadenza → **INSUFFICIENT DATA**: il canale non produce abbastanza segnali per
sostenere la traccia, che è già di per sé un'informazione.

## 5. Metriche obbligatorie nel report

- **N**: segnali ricevuti · accettati · scartati (per motivo) · eseguiti · chiusi
- **Tasso di rifiuto** complessivo e per motivo (tardivo, oltre TP1, whitelist, SL incoerente)
- **E[R] catturato** con BCa 95% CI, uscita a TP1, e **capture ratio** vs +0,194
- **Slippage reale** all'ingresso: differenza tra prezzo del trigger e fill effettivo
- **Latenza**: tempo tra timestamp del messaggio e invio ordine
- Confronto con il replay teorico sugli **stessi** segnali del periodo (il controfattuale onesto)
- Ordini falliti per motivo — `[No money]`, `Invalid stops`, `Trade disabled` (lezione del 12/08)

## 6. La soglia anti-ritardo: NON si tocca durante il test

Il gate a 20 pip resta **congelato** per tutta la durata. Ritoccarlo guardando gli esiti sarebbe
p-hacking, e qui la tentazione è massima ("con 30 pip avremmo preso quei tre vincenti").

**Ma l'informazione si raccoglie lo stesso, gratis.** Dal 2026-08-14 `TradePlan.slip_pips` registra lo
scarto in pip come **numero**, su **ogni** segnale — accettati **e** scartati (commit `579ab08`).
A test chiuso si potrà ricostruire il controfattuale per qualunque soglia (15/25/30/40 pip) **senza
aver toccato nulla durante**.

⚠️ Quella ricostruzione **non è un verdetto**: è un'ipotesi *data-derived*, esattamente come il fade.
Se una soglia diversa sembrasse migliore, richiederebbe **nuova pre-registrazione e nuovo forward** —
non l'adozione immediata.

Nota tecnica ereditata dall'audit: la tolleranza al **ritardo in TEMPO** (l'edge regge fino a 60
minuti) **non** implica tolleranza allo **scarto in PREZZO**. Sono due grandezze diverse e non vanno
confuse quando si leggerà quel controfattuale.

## 7. Cosa questo test NON decide

- **Non** autorizza capitale reale: `live` qui significa **demo**. Il passaggio a capitale proprio è
  una decisione separata ed esplicita ([signal_copier/README.md](../signal_copier/README.md), red line 2).
- **Non** cambia nulla sul fronte prop: seguire segnali di terzi resta vietato a prescindere
  dall'esito ([PROP_FIRM_CRITERIA.md §4](PROP_FIRM_CRITERIA.md)).
- **Non** rimuove il **key-man risk**: il mentore può smettere, cambiare stile o cancellare segnali
  (cancellazione confermata a tasso ~0,2%).

## 8. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-14 | Creazione, prima dell'avvio in `live` | Conto demo hedging ricreato e verificato; copier pronto |
| 2026-09-30 | **Nessuna modifica alle soglie.** Primi esiti live (conto demo del socio 5056226036, 22 segnali 21-29/09) in [reviews/analysis_team_live_2026-09-30.md](reviews/analysis_team_live_2026-09-30.md): conto, magic, rischio e gate **diversi dal §2**; il gate a 20 pip non agisce sul flusso "NOW" (`build_market_plan` lo spegne). Se questi segnali contino per N = 60 e da quando far partire il conteggio: **decisione di Matteo, aperta** | Dati arrivati dal socio; il setup congelato non e' quello in esecuzione |
