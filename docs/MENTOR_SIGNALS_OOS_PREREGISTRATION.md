---
tipo: preregistrazione
stato: CONFERMATO
aggiornato: 2026-09-18
decisione: "DECISIONS 2026-09-18 (4) — OOS rifatta sulla finestra estesa"
metrica_corrente: "differenza appaiata +0,274 [+0,209; +0,333]; E[R] +0,173 [+0,083; +0,244] su 218 segnali"
nota: "Verdetto del 07/08 confermato; i numeri originali (63,0% vs 35,0%, +0,194) sono superati."
---
# Pre-registrazione — Validazione OOS dei segnali mentore (XAUUSD)

> **Documento vincolante, scritto il 2026-08-07 PRIMA di eseguire il replay.** Nessun risultato è
> ancora stato calcolato sulla finestra oggetto del test. Le soglie qui sotto non si modificano dopo
> aver visto i numeri; qualunque modifica va datata e dichiarata nel §8.
>
> Ciclo: [STRATEGY_LIFECYCLE.md](STRATEGY_LIFECYCLE.md). Audit di riferimento:
> [reviews/mentor-signals-2026-07-08.md](reviews/mentor-signals-2026-07-08.md).

---

## 1. Perché questo test esiste

L'audit dell'8 luglio 2026 è stato **retrospettivo**: ha replayato i segnali del canale contro il
prezzo reale dell'oro su un periodo **già concluso e già osservato**. Ha dato il primo esito positivo
del workspace (direzione giusta ~2/3, robusta al ritardo, stabile su 6 mesi) — ma **nessuna
validazione indipendente in avanti è mai stata eseguita**.

L'export Telegram del 2026-08-07 rende disponibile una finestra che **non esisteva** quando l'audit è
stato fatto. È l'occasione di un OOS vero, a costo zero.

**H1**: l'edge direzionale del mentore persiste fuori campione.
**H0**: l'edge osservato nell'audit è artefatto di campione/periodo e non si ripete.

## 2. Dati

| | |
|---|---|
| **Segnali** | Export `Messaggi tg aggiornati 07-08/` — canale XAU/USD ANALYSIS TEAM, 3.239 messaggi, 10/01/2026 → 07/08/2026, **618 trigger** `BUY/SELL NOW` |
| **Finestra OOS** | Segnali con timestamp **> 2026-06-12 22:55** (fine della copertura prezzi dell'audit). ~147 trigger, 59 giorni |
| **Prezzi** | `analysis/trading-bot-eval/data/XAU_spot_M5_ext.csv` — serie originale dell'audit **estesa** con feed MT5 (`XAUUSD.cyr`, First Prudential Markets) dal 2026-06-13 al 2026-08-07 |

**Validazione della giunzione (eseguita prima della pre-registrazione, non dipende dagli esiti):**
8.063 barre M5 in comune tra le due fonti, **correlazione 1.000000**, differenza mediana **+$0.060**
(offset bid/mid del broker), σ $0.112, |max| $1.43. L'offset mediano è stato **sottratto** dal
segmento MT5 prima della giunzione. Su distanze di stop nell'ordine di $10 il residuo è trascurabile.

## 3. Parametri CONGELATI

Identici all'audit dell'8 luglio. **Nessuna ritaratura è ammessa in questo test.**

- Motore: `analysis/mentor_signals/parse.py` → `backtest.py`, invariati.
- Geometria: entry/SL/TP come pubblicati dal canale; exit su **TP1**.
- Costo: **$0.30** round-trip per operazione.
- Baseline: **side casuale** sulla stessa geometria e sugli stessi tempi (il confronto che rende il
  test informativo: misura la *direzione*, non il drift dell'oro).
- **Convenzione di fuso orario**: quella già implementata nel motore d'audit. I timestamp Telegram
  sono `UTC+01:00`. ⚠️ È la trappola che ha prodotto il falso allarme "4670 vs 4155" a luglio: il
  disallineamento va verificato con un sanity-check di riconciliazione (range dei prezzi dei segnali
  vs range reale del periodo) **prima** di leggere qualunque metrica.
- **Il gate anti-ritardo NON viene applicato**: qui si misura l'edge grezzo del segnale, come
  nell'audit. La soglia del gate è una domanda separata con una sua pre-registrazione (§7).

## 4. Regola di stop

**Valutazione unica**, su tutti i segnali della finestra §2. Nessuna estensione, nessuna
sottoselezione di periodo, nessuna esclusione di segnali se non per i criteri meccanici già nel
parser (segnale incompleto / non parsabile), che vanno **contati e riportati**.

## 5. Soglie di verdetto — fissate ORA

Confronto primario: **win-rate simmetrica del lato del mentore vs lato casuale**, sulla stessa
geometria. Riferimento audit: **67-72% vs 32%**; E[R] su TP1 **+0.20/+0.32**; TP1-hit reale ~85%.

| Esito | Condizione | Decisione |
|---|---|---|
| **CONFERMATO** | Lower bound BCa 95% della *differenza* (mentore − random) **> 0** **E** E[R] puntuale **> 0** dopo costi | L'edge regge OOS → si può discutere dove operarlo (capitale proprio) con una pre-registrazione di deployment |
| **DEGRADATO** | Direzione batte il random (lower bound > 0) **ma** E[R] ≤ 0 dopo costi | Edge direzionale reale ma **non tradabile con questa geometria** → non si opera; eventuale ridisegno = nuova ipotesi, nuova prereg |
| **FALSIFICATO** | Lower bound BCa 95% della differenza **≤ 0** | L'edge non si ripete OOS → traccia **archiviata**. Nessuna rifinitura |

Se i segnali replayabili risultassero **< 50**, l'esito è **INSUFFICIENT DATA** (soglia di protocollo)
e non si dichiara nulla in nessuna direzione.

## 6. Bias noti, dichiarati prima

1. **Cancellazione di segnali dal canale — CONFERMATA, non più ipotetica.** Confrontando l'export
   dell'08/07 con quello del 07/08: **1 segnale cancellato** (BUY del 07/07 06:25, entry 4130,
   TP 4135/4140/4145, SL 4120) e **0 modifiche** su 2.890 messaggi. Tasso di cancellazione osservato
   ~0,2%. Il delta è conservato in
   [`analysis/mentor_signals/deleted_signals/`](../analysis/mentor_signals/deleted_signals/).
   → L'audit indicava la survivorship come "non escludibile"; ora è **confermata a tasso basso**.
   Un tasso dello 0,2% non sposta le conclusioni, ma **va misurato di nuovo a ogni export**: se
   crescesse, il record del canale smetterebbe di essere una fonte affidabile.
2. **Esecuzione idealizzata**: il replay assume fill al livello pubblicato. Il forward reale del
   copier (2-8 giugno) mostra che **5 segnali su 12 furono rifiutati** perché il prezzo si era già
   mosso oltre 20 pip. Questo test **non** misura l'edge ottenibile in esecuzione — misura l'edge del
   segnale.
3. **Un solo asset, un solo regime**: XAUUSD, con l'oro in tendenza discendente nel periodo.
4. **Nessun controllo sul canale**: il mentore può cambiare stile, frequenza o smettere (key-man risk).

## 7. Cosa NON è questo test

- **Non** è un test di esecuzione (vedi §6.2) né una validazione del copier.
- **Non** produce alcuna autorizzazione a operare su **capitale prop**: il divieto di seguire segnali
  di terzi è indipendente dall'esito ([PROP_FIRM_CRITERIA.md §4](PROP_FIRM_CRITERIA.md)).
- **Non** è l'occasione per tarare il gate anti-ritardo. Quella domanda — *quale scarto in prezzo
  massimo preserva l'edge?* — richiede la sua pre-registrazione, perché è ottimizzazione di un
  parametro sui dati. Nota che l'audit ha misurato la tolleranza al **ritardo in tempo** (fino a
  60 min), che **non** implica tolleranza allo **scarto in prezzo**.

## 8. Registro delle modifiche

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-07 | Creazione, prima di qualunque esecuzione sulla finestra OOS | Export Telegram aggiornato rende disponibile una finestra mai replayata |
