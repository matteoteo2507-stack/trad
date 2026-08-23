# Forward FADE — health-check del 2026-08-24: il test gira, ma il campione è contaminato

> **Non è un verdetto sulla strategia.** È una diagnosi di **esecuzione**: nessuna di queste voci
> tocca la regola pre-registrata, quindi per
> [`STRATEGY_LIFECYCLE §3`](../STRATEGY_LIFECYCLE.md) **non consuma trial**. Ma tutte e quattro
> incidono su *quali* trade finiscono nel campione — cioè sulla cosa che il forward doveva
> proteggere.
>
> Origine: verifica dello stato reale dei binari attivi, dopo che il 23/08 si era scoperto che il
> **forward ORB non era mai stato implementato** pur essendo citato come "in corso".
> Strumento: [`analysis/ops/deployment_healthcheck.py`](../../analysis/ops/deployment_healthcheck.py) (40 giorni).

## Stato del conto

`7396683 @ FPMarkets-Demo` · equity **105.588 USD** · EA `nxt_fade` (magic 26071) avviato ~2026-07-24.

**Conteggio Stadio 1: N valido = 29 / 50** (2 esclusi perché fuori universo).
Breadth: **4 strumenti su 6** hanno trade chiusi.

| strumento | ordini storici | trade chiusi |
|---|---|---|
| XAUUSD.cyr | 25 | 12 |
| US100 | 36 | 7 |
| GBPUSD.r | 13 | 6 |
| USDJPY.r | 8 | 4 |
| EURUSD.r | **1** | 0 |
| US500 | **0** (+1 pendente) | 0 |

---

## I quattro difetti, in ordine di gravità per la validità del test

### 1. ⚠️ Ordini non inviati — 197 fallimenti fra il 2 e il 21 agosto

Il log Experts del VPS contiene 197 righe `[nxt_fade] <SIMBOLO> arm fallito, err=4756`
(`ERR_TRADE_SEND_FAILED`), distribuite su **12 giornate operative**:

| simbolo (come appare nel log) | fallimenti |
|---|---|
| USDJPY | 67 |
| EURUSD | 64 |
| GBPUSD | 41 |
| BTCUSD | 20 |
| XAUUSD.cyr | 5 |

**Il dettaglio che spiega tutto**: i primi tre compaiono nel log **senza il suffisso del broker**
(`nxt_fade (EURUSD,H1)`), mentre il conto negozia `EURUSD.r`, `GBPUSD.r`, `USDJPY.r`. I fallimenti
sono a cadenza **oraria esatta** (23:00, 00:00, 01:00, 02:00…), cioè **uno per barra H1**.

Confronto che rende la cosa concreta: **EURUSD ha 1 solo ordine storico e 64 tentativi falliti**.
USDJPY: 8 ordini contro 67 fallimenti.

⚠️ **È la recidiva del bug che ha generato questo stesso script**: nell'agosto precedente l'EA era
rimasto **tre settimane** agganciato a simboli non negoziabili, con grafici attivi e log che
scorreva, e **zero trade** — il segnale stava in ciò che mancava.

**Perché è il difetto peggiore**: il campione del forward non è un sottoinsieme casuale dei segnali
della strategia. Manca in modo **sistematico** la parte di segnali generata sulle istanze a nome
semplice, e quelle sono concentrate sui **major FX** — cioè, secondo il lead del playground, proprio
il gruppo con l'aspettativa peggiore. Il campione superstite è quindi **spostato verso gli strumenti
più volatili** (XAU, US100), che è la direzione che gonfia l'E[R].

⚠️ `err=4756` è generico. Il pattern (nome senza suffisso, cadenza oraria, esattamente i major)
indica un disallineamento di simbolo, ma **la causa esatta va letta nel log del terminale**, riga
`failed … [motivo]`, prima di scrivere la correzione.

### 2. ⚠️ Strumenti fuori dall'universo pre-registrato

| strumento | ordini |
|---|---|
| **BTCUSD** | 7 (2 trade chiusi) |
| **EURGBP.r** | 2 |

Nessuno dei due è nell'universo di [`NXT_FADE_FORWARD_PREREGISTRATION.md`](../NXT_FADE_FORWARD_PREREGISTRATION.md) §2.

⚠️ Questo **chiude la voce C2 del backlog** — che era formulata come *"decidere se reinserire BTCUSD
nel FADE live"*. **Non è una decisione aperta: sta già operando**, fuori universo, da settimane.
Lo script li esclude correttamente dal conteggio (N valido 29 anziché 31), ma finché l'EA resta
agganciato continuano a generare ordini e a consumare margine (vedi §3).

### 3. ⚠️ Dropout per margine — e non è casuale

**8 ordini non eseguiti su 92 (8,7%)**, di cui `BTCUSD ×3` e `US100 ×2` respinti con
`deleted [no money]`.

Il meccanismo, già annotato nello script: il rifiuto per margine **non colpisce a caso**. Colpisce i
setup con lo **stop più stretto**, perché a rischio costante uno stop stretto significa **volume
maggiore**, quindi margine maggiore. Sono anche i setup con il **miglior rapporto rischio/rendimento
potenziale**. Il campione perde in modo selettivo proprio quelli.

Aggravante: parte del margine è occupata da **strumenti fuori universo** (§2).

### 4. ⚠️ Rischio per trade fuori specifica

| posizione aperta | rischio | % equity | atteso |
|---|---|---|---|
| US100 | 264,98 | **0,25%** | ~0,25% ✓ |
| GBPUSD.r | 668,64 | **0,63%** | ~0,25% ✗ |

**2,5× il rischio previsto** su GBPUSD. Se il rischio per trade non è costante, i multipli di R
**non sono confrontabili fra loro** e l'E[R] aggregato diventa una media pesata con pesi non voluti.

---

## Cosa NON è cambiato

- **La regola pre-registrata è intatta.** Nessuno dei quattro punti è una modifica di strategia.
- **La regola di stop resta N e data** — mai il P&L cumulato
  ([`prereg §5`](../NXT_FADE_FORWARD_PREREGISTRATION.md)). Questo report **non guarda il P&L** ed è
  deliberato: guardarlo adesso sarebbe optional stopping.
- **Il confronto resta contro +0,31R**, non +0,354R (fill onesto, correzione del 14/08).

## Cosa va deciso

Le riparazioni sono correzioni di bug e **non consumano trial**. La domanda vera è **cosa fare dei
29 trade già raccolti**, e sono due opzioni con costi diversi:

| opzione | conseguenza |
|---|---|
| **ripara e prosegui**, tenendo i 29 | il campione resta contaminato per la sua prima metà; il verdetto Stadio 1 sarà su dati misti. **Va dichiarato nel report finale** |
| **ripara e azzera il contatore** | Stadio 1 riparte da 0 su un campione pulito. Costa ~30 trade e ~un mese, ma il verdetto diventa interpretabile |

⚠️ **La seconda è quella coerente col protocollo.** Il forward è l'**unica fonte di dati puliti
rinnovabile** che abbiamo ([`LIFECYCLE §2`](../STRATEGY_LIFECYCLE.md)): contaminarla è l'errore più
caro possibile, e tenersi 29 trade con selezione nota è esattamente contaminarla. Ma è una scelta
dell'utente, non mia.

## Debito che questo episodio conferma

Il health-check **esisteva già** e ha trovato tutto in dieci secondi — ma **nessuno lo eseguiva**.
Come per il forward ORB (mai implementato pur essendo citato come attivo), il problema non è la
mancanza dello strumento: è che **lo stato reale dei binari non è osservabile senza andarlo a
cercare a mano**. È il debito **E2** del backlog, e questo è il secondo caso in due giorni.

Minimo indispensabile: esecuzione **settimanale** del health-check con output datato e versionato,
così che N, breadth e anomalie abbiano una serie storica invece di essere una fotografia estemporanea.
