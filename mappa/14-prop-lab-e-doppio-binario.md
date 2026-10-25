---
titolo: 14 · prop-lab e doppio binario del rischio
tipo: mappa
tags: [#public]
creato: 2026-10-06
compreso:
verificato_il:
metodo: spiegazione
---

# 14 · prop-lab e doppio binario del rischio

← [[00-panoramica-trad]] · componente 14 di 14

## Cosa fa

Risponde a due domande che `trad` prima non sapeva fare con un numero:

1. **Questa sequenza di trade, su questa challenge prop, quanto passa e quanto rende, e quanto di
   quel rendimento e' merito del vantaggio?** Il simulatore gioca migliaia di challenge complete (fase 1, fase 2,
   funded con payout) sotto le regole di una firm e un profilo di rischio, e le ripete con gli **stessi trade
   portati ad attesa zero**: la differenza (`ev_vs_zero`) e' la parte dovuta al vantaggio, il resto e' il valore
   d'opzione della challenge, che ha anche chi non ha nessun vantaggio.
2. **Una regola di gestione del rischio attiva aggiunge qualcosa, o sposta solo il rischio?** Ogni strategia si
   legge su due binari: **1R fisso** (l'unico su cui si da' il verdetto) e gli **overlay** di una libreria fissa
   (O1 cuscinetto, O2 guardia giornaliera, O3 serie di perdite, O4 avvicinamento al target).

| Pezzo | File | Ruolo |
|---|---|---|
| **Simulatore prop** | `prop-lab/lab/prop.py` (`evaluate`, `zero_edge`, `evaluate_ci`) | proprietario unico della logica delle challenge, condiviso col socio |
| **Modelli di rischio** | `prop-lab/lab/risk.py` (`RiskModel`) | i modificatori (dd_linear, daily_guard, loss_streak, target_coast, floor_cap, …) |
| **Ponte** | `core/prop_sim.py` | l'unico punto di `trad` che arriva a `prop-lab` (`sys.path` in coda) |
| **Doppio binario** | `core/sizing.py` (`LIBRERIA`, `confronta_overlay`, `confronta_overlay_prop`) | la libreria dichiarata e i due confronti |
| **La pipeline del socio** | `prop-lab/lab/pipeline.py`, `cli.py`, `strategies/` | famiglia → backtest ideale → costi → prop × rischio → conferma OOS |
| **Il cancello** | `prop-lab/lab/gate.py`, `prop-lab/config/gate.yaml` | su dati reali: niente test senza famiglia nel contatore e pre-registrazione APPROVATA; fuori campione aperto una volta (dal 08/10) |
| **Il controllo** | `prop-lab/lab/strategies/controllo_casuale.py` | ingressi casuali: collauda la pipeline su dati veri senza ipotesi |
| **La regola** | `docs/STRATEGY_LIFECYCLE.md` §4quater, `docs/QUANT_REVIEW_PROTOCOL.md` Step 5bis | quando e come si usa |

## Perché esiste

Il **04-05/10** il socio VELTRIX ha portato `prop-lab`, generato da un'AI nella sua sessione
(`prop-lab/docs/sessione_socio_veltrix_2026-10-04_05.md`). Valutandolo il 05/10 sono emerse due cose:

- il **motore** e' sano (nessun look-ahead; su un random walk a passi di un minuto l'attesa e' zero), e il
  **simulatore prop** e' il pezzo che a `trad` mancava: prima c'era solo la formula a due barriere
  (`core.verifiche.prob_obiettivo_prima_del_limite`), senza giornaliero, trailing, consistency e funded;
- ma un **EV positivo non distingue** vantaggio da rumore: a vantaggio zero il profilo guardia giornaliera al 3%
  passava ~30% delle due fasi con EV ~+1.900 per tentativo. E scegliere fra 35 profili quello con l'EV piu'
  alto premia il rischio alto, cioe' chi un vantaggio non ce l'ha.

Il **06/10** Matteo ha deciso: il materiale del socio entra in `trad` come nostro, in git, su due repo tenuti
allineati; e ogni test si legge su due binari, a prescindere dall'esito (DECISIONS 2026-10-06).

## Il principio, in una riga

guadagno = Σ E[size]·E[R] + Σ Cov(size, R). Se la size dipende solo dal passato e gli esiti sono indipendenti,
la covarianza e' zero: un overlay **non crea vantaggio**. Aiuta solo se gli esiti sono raggruppati
(**dipendenza**, si misura contro la stessa sequenza rimescolata) o se l'obiettivo e' a barriere (**struttura**,
si misura contro il vantaggio zero).

## Come si lancia

Su dati reali, dentro trad (dal 08/10): prima la famiglia nel contatore (`registro_prop_lab: true`,
`preregistrazione` APPROVATA), poi

```
cd prop-lab
python -m lab.cli all --family <famiglia di codice> --symbol XAUUSD --data ../analysis/trading-bot-eval/data/XAUUSD_H1.csv --famiglia <id del contatore>
python -m lab.cli confirm --run results/<run>      # APRE il fuori campione: una volta sola, su richiesta di Matteo
cd .. && python -m core.trial_ledger --check        # registro e contatore devono dire la stessa cosa
```

Per collaudare senza ipotesi: `--family controllo_casuale` (nessun `--famiglia` richiesto).

```
python -m pytest -q prop-lab/tests core/tests/test_sizing.py      # i test di questo componente
cd prop-lab && python tools/make_demo_data.py && python -m lab.cli all --family mean_reversion --symbol XAUUSD --data data/DEMO_XAUUSD_H1.csv
```

Da Python, dentro `trad`:

```python
from core.sizing import confronta_overlay, confronta_overlay_prop
tab, runs = confronta_overlay(R)                                  # capitale proprio
tab_prop = confronta_overlay_prop(day_trades, rules, base_pct=1.0)  # prop
```

Esempio completo su dati veri: `analysis/opening_range/doppio_binario.py`.

## Input → Output

- **Input:** una sequenza di R per trade (capitale proprio), oppure i trade per giorno con la loro MAE
  (`prop_sim.trades_by_day`) e un regolamento in `prop-lab/config/prop_rules.yaml` (prop).
- **Output:** una tabella per binario (1R e ogni overlay). Capitale proprio: attesa per unita' di rischio, maxDD,
  banda del rimescolato, `valore_dipendenza`, lettura. Prop: pass rate con intervallo, `pass_zero`, EV, `ev_zero`,
  `ev_vs_zero` con intervallo e probabilita' che sia positivo.

## Stato atteso

| Cosa | Valore atteso | Come si controlla | Chi |
|---|---|---|---|
| Registro di prop-lab e contatore | coerenti | `python -m core.trial_ledger --check` → exit 0 | Claude |
| Test del componente | tutti passati | `python -m pytest -q prop-lab/tests core/tests/test_sizing.py` (06/10: 11 + 8 passati) | Claude |
| Vantaggio zero, barriere ±10%, niente timeout | pass ≈ 0,5 | `test_vantaggio_zero_due_barriere_come_la_rovina_del_giocatore` | Claude |
| Libreria degli overlay | identica alla dichiarazione del §4quater | `test_libreria_dichiarata_non_cambia_di_nascosto` | Claude |
| Repo del socio allineato | ogni voce di `prop-lab/CHANGELOG.md` riportata anche lì | chiedere al socio | Matteo |
| Regole prop | due sezioni dichiarate nell'intestazione: modelli parametrici + regolamenti veri `citato_senza_url` (25/10); nessuna decisione con soldi finche' gli URL non sono verificati e il §3 di PROP_FIRM_CRITERIA non e' compilato | leggere l'intestazione di `prop_rules.yaml` (corretta il 25/10) | Matteo |

## Come si rompe

**Guasti trovati e riparati il 05-06/10:**
- *Su Windows non arrivava in fondo.* YAML letti in cp1252 (crash in fase 2) e pool di processi che moriva con
  `WinError 6`. Riparati in `lab/pipeline.py` (UTF-8 esplicito, `_map` con ricaduta seriale).
- *Il profilo "migliore" era quello piu' audace.* Ordinamento per `ev_attempt`; ora per `ev_vs_zero`.

**Riparati il 07/10 (Matteo: "condivido la correzione"):**
- *DA_OSSERVARE usciva su rumore puro* (5 serie nulle su 8 mandavano un candidato in demo). Ora il verdetto e'
  PROMOSSA / NON_DIMOSTRATA / SCARTATA, deciso dall'intervallo OOS corretto per i candidati; il DSR resta come
  diagnostica (`lab/metrics.py`: `mean_ci`, `verdetto_oos`). Controlli: 0 promosse su 9 random walk, 2 su 8 con
  la mean reversion iniettata debole, 8 su 8 con quella forte. Con DSR ≥ 0,95 obbligatorio (la prima versione
  del 07/10) non si promuoveva nemmeno quella forte: un gate irraggiungibile e' rotto quanto uno che fa passare
  il rumore.
- *I dati demo avevano il vantaggio dentro* (mean reversion non dichiarata e massimi/minimi staccati dal percorso).
  Ora sono due controlli costruiti su un percorso a passi di un minuto: `DEMO_NULL` e `DEMO_MR` (con `--forza`).
- *Regolamenti incompleti simulati con default.* `lab.prop.regole_mancanti` li rifiuta con l'elenco dei campi.

**Limite da sapere:** `ev_vs_zero` toglie il valore d'opzione della challenge, **non il caso**. Decide il verdetto
della conferma; per un candidato vero serve `evaluate_ci`.

**Ancora aperti:**
- Il motore riempie lo stop **esattamente al livello**: sui dati veri e' ottimista quanto lo slittamento degli
  stop sulle news.
- Il DD dentro la giornata e' stimato con la MAE del trade e un trade conta nel giorno in cui chiude: sottostima
  le violazioni giornaliere delle firm che contano il flottante (PROP_FIRM_CRITERIA §1.1).
- *Trade sovrapposti nel binario capitale proprio* (G2 del 08/10, candidato A). `confronta_overlay` legge una sequenza
  e fissa la size di ogni trade con l'esito del precedente: se due trade sono aperti insieme (due indici nello stesso
  episodio) il precedente non era ancora chiuso all'ingresso, e l'overlay vede il futuro. Su sequenze sintetiche senza
  dipendenza: falsi AGGIUNGE di O3 nel 36% invece del ~2,5%. Finche' non c'e' un controllo, il binario capitale proprio
  si legge solo su sequenze **senza sovrapposizioni** (una posizione alla volta).

**Sintomi da riconoscere:** un EV prop citato senza `ev_zero` accanto; un overlay che "salva" un 1R negativo;
un overlay nuovo aggiunto dopo aver visto il risultato; un AGGIUNGE letto come verdetto invece che come ipotesi
(con k overlay almeno un falso allarme arriva con probabilita' ~1 − 0,95^k).

## Dipende da / chi dipende da lui

- **Usa:** `core.verifiche.runs_test` (componente 6), i regolamenti di `docs/PROP_FIRM_CRITERIA.md` (5).
- **Lo applicano:** ogni review (QUANT_REVIEW_PROTOCOL Step 5bis) e ogni test futuro (componente 1).
- **Condiviso con:** il repo del socio VELTRIX, tramite `prop-lab/CHANGELOG.md`.

## Con parole mie

