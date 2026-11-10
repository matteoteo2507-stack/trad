---
titolo: "Collaudo di prop-lab su dati reali con ingressi casuali"
tipo: referto
creato: 2026-10-08
stato: descrittivo
trial: 0
---

# Collaudo di prop-lab su dati reali

**Perche'.** Matteo (08/10): chiudere i punti bloccanti, provare la catena per scoprire altre dipendenze, poi
collaudare. Il collaudo prova **tutto insieme su dati di mercato veri** (loader, costi, giornate, simulatore prop,
verdetto, contatore) senza aprire il fuori campione di nessuna famiglia vera: usa la famiglia di **controllo**
`controllo_casuale` (`prop-lab/lab/strategies/controllo_casuale.py`), ingressi e direzione a caso, stessa geometria
di stop e target delle strategie vere. Non e' un'ipotesi: **0 trial**.

## 1. Cosa e' stato chiuso prima (08/10)

- **Contatore collegato.** `prop-lab` registra ogni variante e ogni apertura del fuori campione con l'id della
  famiglia del contatore (`results/registry.sqlite`); `core.trial_ledger --check` segnala trial diversi, aperture non
  registrate e famiglie sconosciute.
- **Cancello sui dati reali** (`prop-lab/lab/gate.py`, `config/gate.yaml`): senza famiglia nel contatore con
  `preregistrazione` in stato APPROVATA non parte; famiglie chiuse rifiutate; il fuori campione si apre una volta;
  `lab.cli all` su una famiglia vera si ferma prima della conferma.
- **Gatekeeper** (`.claude/agents/quant-gatekeeper.md`): checklist 8 (rischio e prop) e controllo del registro.

**Prova di catena** (copia isolata di trad, famiglia FINTA nel contatore copiato, dati sintetici rinominati come
reali per non guardare il mercato con una famiglia vera): rifiuti corretti senza famiglia, con famiglia chiusa, con
pre-registrazione in bozza; fasi 1-3 solo con pre-registrazione approvata; il contatore segnala i 204 trial e poi
l'apertura non registrata; seconda apertura rifiutata dal registro e dal contatore. **Dipendenze trovate e corrette:**
1. percorso dei dati in `run.json` con la barra Windows (non portabile);
2. percorsi **assoluti** dei file dei trade in `stage2_costi.csv` (non portabili e col nome utente, repo pubblico);
3. giorni contati solo lun-ven: con dati in UTC un trade chiuso di domenica spariva dalla simulazione prop e dallo
   Sharpe giornaliero (con i nostri file in orario server MT5 non succede, ma e' latente);
4. **nessuna variante sopravvissuta alla fase 1 → crash** della fase 3 su una tabella vuota. Ora la famiglia muore
   **senza aprire** il fuori campione (STRATEGY_LIFECYCLE §2): verificato, 0 aperture registrate.

**Dipendenze trovate e non corrette (annotate):** i costi in `config/symbols.yaml` sono valori d'esempio e mancano
US100/US500 (i nostri nomi degli indici): vanno presi dal broker reale prima di un test sugli indici. `EURUSD_H1.csv`
ha esattamente 90.000 righe da un orario qualunque (05/01/2012 17:00): probabile limite di barre dell'export MT5, da
verificare prima di un test vero su EURUSD.

## 2. Collaudo dichiarato PRIMA dell'esecuzione

- **Dati:** `analysis/trading-bot-eval/data/XAUUSD_H1.csv` (05/2020 → 07/2026) ed `EURUSD_H1.csv` (01/2012 → 07/2026),
  orario del server MT5 (settimana lun 00 → ven 23). Controlli `core.data_checks`: tempo crescente, nessun duplicato,
  barre per anno coerenti (~5.900 oro, ~6.200 EURUSD). Senza spread per barra: costi d'esempio di `symbols.yaml`.
- **Famiglia:** `controllo_casuale`, 36 varianti per simbolo (stop 1,5 / 2,5 ATR × target 1/2/3 R × frequenza 1% / 3%
  × 3 semi), pipeline completa (fasi 1-4) con le soglie in vigore, regole prop modello di `pipeline.yaml`.

**Esito positivo se, su entrambi i simboli:**
1. la pipeline arriva in fondo (fasi 1-4, report) senza errori;
2. **zero PROMOSSA**. Il falso positivo atteso e' ≤ 5% per run (Bonferroni sui candidati): se ne esce una, prima di
   dichiarare il fallimento si guarda se e' il 5% o una distorsione (attesa lorda per direzione, costi);
3. `core.trial_ledger --check` resta a exit 0 (il controllo non tocca nessuna famiglia);
4. nessun percorso assoluto nei file salvati dal run.

**Descrittivo, non decide:** quota di varianti con attesa lorda positiva (attesa vicina al 50%; la deriva del prezzo
si annulla a direzione casuale), costo per trade in R, e `ev_vs_zero` della fase 3 (sui candidati scelti in-sample
e' gonfiato dalla selezione: e' il motivo per cui non decide).

## 3. Risultati (eseguito il 08/10 dopo il commit `a1259bd`, gia' `1a32307`)

**ESITO POSITIVO: i quattro criteri dichiarati sono soddisfatti su entrambi i simboli.**

| criterio | XAUUSD | EURUSD |
|---|---|---|
| pipeline completa (fasi 1-4, report) | si' | si' |
| zero PROMOSSA | si' (2 NON_DIMOSTRATA) | si' (3 NON_DIMOSTRATA) |
| `core.trial_ledger --check` a exit 0 | si' | si' |
| nessun percorso assoluto nei file del run | si' | si' |

Il registro contiene i trial con etichetta `controllo` e le due aperture (`controllo`): nessuna famiglia toccata.

**Descrittivo:**

| | XAUUSD (36.212 barre, IS fino al 30/08/2024) | EURUSD (90.000 barre, IS fino al 02/03/2022) |
|---|---|---|
| fase 1: varianti con attesa lorda > 0 | 23 su 36 (64%), mediana +0,021R | 17 su 36 (47%), mediana −0,004R |
| fase 1: passano le soglie | 6 | 6 |
| fase 2: attesa lorda → netta (mediane) | +0,114 → +0,035R, costi 69% del lordo | +0,084 → +0,038R, costi 59% |
| conferma: attesa fuori campione dei candidati | −0,335 e −0,197R | −0,023, −0,009, +0,017R |

- **Le varianti non sono indipendenti.** Per seme: sull'oro il seme 1 ha 12 varianti positive su 12, il seme 3 3 su
  12; su EURUSD il seme 2 ha 12 su 12. Le 36 varianti sono **3 estrazioni indipendenti** per simbolo, e i
  sopravvissuti sono tutti dello stesso seme. "Il 64% delle varianti e' positivo" significa "2 semi su 3": e' la
  lettura "vantaggio diffuso" del funnel originale, e su un controllo casuale e' falsa per costruzione. Anche per
  questo il verdetto sta sull'intervallo fuori campione, non sulla quota di varianti positive.
- **Costi.** Con i costi d'esempio di `symbols.yaml` (non quelli del broker), a H1 con stop di 1,5-2,5 ATR il costo
  vale circa **0,05-0,08R per trade** (differenza fra attesa lorda e netta dei sopravvissuti). Un candidato vero a
  questo orizzonte ha bisogno di un vantaggio lordo ben sopra questa cifra.
- `ev_vs_zero` della fase 3 e' positivo nell'88% delle combinazioni su entrambi i simboli: e' la selezione in-sample
  (candidati scelti perche' positivi nell'IS), il motivo per cui non decide.

**L'infrastruttura e' chiusa per i test veri.** Restano annotati: costi reali del broker in `symbols.yaml` (e i nomi
US100/US500), e la lunghezza reale della storia EURUSD (90.000 righe = probabile limite dell'export).
