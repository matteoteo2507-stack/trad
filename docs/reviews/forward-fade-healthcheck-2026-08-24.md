# Forward FADE — health-check: il fix del 12/08 ha funzionato

> ## ⚠️ CORREZIONE — questo documento è stato riscritto
>
> **La prima versione (commit `93d0f60`) era sbagliata nella sua tesi principale.** Sosteneva che il
> forward fosse *"contaminato"* da 197 ordini non inviati "fra il 2 e il 21 agosto", presentandoli
> come un problema **in corso** e come *"recidiva"* di un bug precedente.
>
> **Non è così.** Quei 197 errori sono **gli stessi** già diagnosticati e risolti nella
> [pre-registrazione §9 del 2026-08-12](../NXT_FADE_FORWARD_PREREGISTRATION.md) — gli identici
> conteggi per simbolo (USDJPY 67, EURUSD 64, GBPUSD 40/41). Restano nei file di log perché i log
> sono storici. **Il fix ha funzionato.**
>
> **Errore mio, di metodo**: ho letto un conteggio cumulato senza separarlo per data, e ho
> pubblicato un allarme al posto di una verifica. È lo stesso errore del caso ORB di due giorni
> prima — asserire uno stato senza controllarlo — commesso mentre lo stavo correggendo.
>
> Sotto, i dati verificati con finestra piena e separati pre/post fix.

---

## Metodo

Conteggio **autorevole per magic** (26071), non per commento — il commento `nxt_fade` sopravvive
solo sulla deal di apertura. Finestra **1 luglio 2026 → nessun taglio superiore**: la prima query
aveva usato `now + 1 giorno` come limite e **tagliava fuori i trade più recenti**, il che ha
prodotto una seconda lettura sbagliata ("EURUSD.r non opera").

⚠️ **Nota sull'orologio**: l'ora del server MT5 e quella locale della macchina indicano
**2026-08-27**. Il nome di questo file resta `2026-08-24` per non rompere i riferimenti già
committati.

---

## Lo stato reale, separato pre/post fix del 12-13 agosto

| simbolo | in universo | ordini pre / post | chiusi pre / post | lettura |
|---|---|---|---|---|
| **EURUSD.r** | ✓ | 0 / **6** | 0 / **3** | ✅ riparato |
| **GBPUSD.r** | ✓ | 0 / **14** | 0 / **7** | ✅ riparato |
| **USDJPY.r** | ✓ | 0 / **11** | 0 / **5** | ✅ riparato |
| **XAUUSD.cyr** | ✓ | 11 / 14 | 5 / 7 | ✅ ha sempre operato |
| **US100** | ✓ | 8 / 11 | 3 / 6 | ✅ ha sempre operato |
| **US500** | ✓ | 0 / 0 | 0 / 0 | ⚠️ pendente mai riempito |
| BTCUSD | ✗ | 7 / **0** | 2 / **0** | ✅ staccato correttamente |
| EURGBP.r | ✗ | 0 / **1** | 0 / **0** | ⚠️ 1 ordine residuo, nessun trade |

**Conteggio Stadio 1: N valido = 36 / 50** (trade chiusi in universo).
**Breadth: 5 strumenti su 6.**

---

## Le quattro voci di ieri, verificate una per una

| voce della prima versione | verità |
|---|---|
| *"197 ordini non inviati, contaminazione in corso"* | ❌ **falso**. **196 su 197 sono precedenti al 13/08**, cioè pre-fix. Dopo il fix: **un solo errore**, il 21/08 su `XAUUSD.cyr` — simbolo **in universo**, quindi non un problema di mappatura simboli |
| *"BTCUSD ed EURGBP operano fuori universo"* | ❌ **quasi del tutto falso**. BTCUSD: **0 ordini post-fix**, correttamente staccato. EURGBP.r: **1 ordine post-fix, 0 trade chiusi** → residuo reale ma senza effetto sul campione |
| *"dropout per margine non casuale"* | ❌ **falso come problema attuale**. I 3 rifiuti `[no money]` sono **tutti pre-fix e tutti su BTCUSD** — cioè causati dallo strumento fuori universo, ora staccato. **Post-fix: zero rifiuti per margine** |
| *"rischio 0,63% contro 0,25%"* | ⚠️ **osservazione reale ma superata**. Era una posizione aperta, ora chiusa; la riduzione del rischio a 0,25% era già l'**azione (c)** del piano del 12/08 |

**Il ragionamento che ne avevo tratto — "il campione è spostato verso gli strumenti più volatili,
cioè nella direzione che gonfia l'E[R]" — cade con le sue premesse.** Post-fix i tre cambi hanno
**15 trade chiusi su 36** (EURUSD 3, GBPUSD 7, USDJPY 5): sono rappresentati.

---

## Cosa resta davvero aperto

| # | voce | gravità |
|---|---|---|
| 1 | **US500 non ha mai riempito**: 0 ordini, 1 pendente attivo. Da capire se è normale (soglia di gamma raramente soddisfatta) o se è un secondo caso di simbolo/permessi | media — è 1 strumento su 6 della breadth |
| 2 | **EURGBP.r: 1 ordine post-fix**. L'azione (b) del 12/08 prevedeva di staccarlo. Nessun trade chiuso, quindi nessun effetto sul campione, ma va staccato | bassa |
| 3 | **1 errore `arm fallito` il 21/08 su XAUUSD.cyr**. Isolato, simbolo in universo. Da sorvegliare, non da diagnosticare adesso | bassa |
| 4 | **Caveat di composizione** (già in prereg §9): le prime tre settimane hanno operato su 2 strumenti su 6. Il report finale **deve** includere il breakdown per strumento | resta valido |

---

## Decisioni dell'utente registrate (2026-08-27)

1. **I 36 trade si tengono.** Non si azzera lo Stadio 1. Vanno **pesati per quello che mostrano** —
   cioè letti insieme al caveat di composizione, non come un campione omogeneo.
2. **I trade fuori universo non contano per il raggiungimento dei 50.** Già così: BTCUSD (2 chiusi)
   è escluso, e il conteggio autorevole è **36 in universo**.

Nessuna delle due tocca la regola pre-registrata → per
[`LIFECYCLE §3`](../STRATEGY_LIFECYCLE.md) **nessun trial consumato**.

---

## La lezione che resta valida

Il health-check **esisteva** e ha fatto il suo lavoro. Ciò che è mancato è che **nessuno lo
eseguiva**, e che quando l'ho eseguito ho letto un aggregato senza separarlo per data.

Da qui in avanti l'esecuzione è **settimanale e persistita** — `analysis/ops/weekly_healthcheck.py`
scrive un report datato in `docs/health/`, così N, breadth e anomalie hanno una **serie storica** e
la domanda *"è un problema nuovo o è il residuo di uno vecchio?"* si risponde confrontando due file
invece che rileggendo un log cumulato.
