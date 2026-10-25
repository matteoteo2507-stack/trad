---
titolo: 1 · Ciclo di vita e gate
tipo: mappa
tags: [#public]
creato: 2026-10-02
compreso: spiegato
verificato_il:
metodo: spiegazione
---

# 1 · Ciclo di vita e gate

← [[00-panoramica-trad]] · componente 1 di 14

## Cosa fa

È la **regola che decide quali idee ricevono capitale**, e soprattutto quali muoiono. Non trova
strategie: le **rifiuta** finché non hanno superato una sequenza di controlli fissati in anticipo.
Il gatekeeper la riassume con una frase di un quant esterno: *"l'edge non è il modello, è la
macchina di rifiuto attorno al modello"* (`.claude/agents/quant-gatekeeper.md`, righe 26-29).

È fatto di quattro pezzi:

| Pezzo | File | Ruolo |
|---|---|---|
| **La legge** | `docs/STRATEGY_LIFECYCLE.md` | il loop, cosa conta come tentativo, i verdetti possibili, quando si uccide |
| **La procedura di misura** | `docs/QUANT_REVIEW_PROTOCOL.md` | gli step di una review: gradi di libertà, fill ottenibili, metriche, costi, pre-mortem, verdetto |
| **Il guardiano** | `.claude/agents/quant-gatekeeper.md` | l'agente che controlla G1 e G2 e **blocca**; non decide il verdetto, che dichiara Matteo |
| **Il contatore** | `core/trial_ledger.py` + `docs/trial_ledger.json` | quanti tentativi ha speso ogni famiglia, e quale Sharpe servirebbe ancora. *Cos'è una famiglia*: un'ipotesi con il suo razionale; dal 08/10 due indicatori che misurano la **stessa grandezza** sono la stessa famiglia (`STRATEGY_LIFECYCLE.md` §3), così cambiare indicatore non ricarica il budget |

## Perché esiste

Un ciclo "provo, misuro, correggo, riprovo" è giusto in ingegneria, ma su un **dataset storico
fisso** diventa una macchina per produrre falsi positivi: ogni giro è un tentativo in più, e
scegliere la variante migliore tra molte significa selezionare rumore (`STRATEGY_LIFECYCLE.md`,
righe 3-8). Il documento nasce il **04/08/2026**, dopo mesi in cui il loop girava senza freni:

- la **ricerca livelli** è arrivata a 384 tentativi su tre round prima di essere chiusa; con un
  budget dichiarato sarebbe morta un round prima (§6b);
- il **FADE** ha retto due mesi su un edge che esisteva solo per un difetto di esecuzione, il
  *fill fantasma* (§6a.1, `QUANT_REVIEW_PROTOCOL.md` Step 3bis).

## Il loop in sei passi

1. **Ricerca e formulazione.** Un razionale economico (chi sta dall'altra parte, e perché continua
   a perdere) e un'ipotesi falsificabile. Le fonti esterne entrano solo da qui, passando da
   `fondamenti_tecnici/_INTAKE.md` (§8). **Dal 03/10 questo passo ha un metodo**:
   `fondamenti_tecnici/09_fonti_di_vantaggio/principles.md`. *Cosa fa*: prima di cercare candidati
   si sceglie la classe di vantaggio (premio, flusso forzato, errore comportamentale, informazione,
   velocità) e si risponde a nove domande in ordine (§4). *Input*: un'idea o una fonte. *Output*:
   un'ipotesi con classe, "chi paga", accessibilità e potenza già verificate, pronta per il
   template e la G1, oppure uno stop motivato. *Come si rompe*: se lo si salta si torna a cercare
   per elenco; e la griglia è una bozza di Claude in quarantena, da confermare con le fonti del suo §6.
   **Dal 08/10, per gli indicatori tecnici** (materiale TradingView incluso):
   `fondamenti_tecnici/10_indicatori_tecnici/principles.md`. *Cosa fa*: riconduce ogni indicatore a
   una di sei grandezze (tendenza, spostamento dalla media, volatilità, volume, livelli, forma della
   candela), ne eredita il verdetto della letteratura e dei nostri test, e lo smista con sei domande
   (§10: grandezza, ridisegno, prezzi veri, ancore scelte a occhio, chi paga, quante varianti).
   *Input*: un indicatore o uno script Pine. *Output*: tenere, cautela o scartare, con il motivo.
   *Come si rompe*: se si contano come candidati diversi due indicatori della stessa grandezza; ed è
   in quarantena, con molte fonti lette solo come sintesi del motore di ricerca.
   **Dal 25/10, per le idee che nascono nell'hub** (`claude-brain`: appunti di Matteo, studio, geopolitica):
   `docs/STRATEGY_LIFECYCLE.md` §8, "Ingresso dall'hub". *Cosa fa*: una scheda di sei campi (fonte unica nell'hub,
   provenienza, controllo contro il repo, dati gia' guardati, misura fatta nell'hub, baseline previsto) da compilare
   prima delle nove domande del modulo 09; ci si ferma al primo campo che manca. Per la geopolitica chiede la misura
   del registro delle previsioni (Brier contro un riferimento, registro intero, criterio scritto prima). *Input*: un
   file in `Da distillare/`. *Output*: respinta, parcheggiata, rimandata all'hub o accettata, ognuna col suo registro.
   *Come si rompe*: se un'idea dell'hub salta la scheda, i dati che Matteo ha gia' guardato nell'hub possono finire a
   fare da holdout; le ipotesi dall'hub hanno un budget loro di 1 pre-registrazione a trimestre (25/10), controllato dal
   contatore (`binario: "hub"`): se il campo manca, l'ipotesi finisce nella quota delle strategie. Il gatekeeper la controlla alla G1 (punto 10).
2. **[G1] Pre-registrazione**, *prima* di guardare i dati: ipotesi, metriche e soglie numeriche,
   baseline random, **budget di tentativi**, divisione dei dati, costi, criteri di morte,
   condizione di fill. Se manca anche una sola voce il gatekeeper blocca (gatekeeper, righe 77-98).
3. **Backtest e rifinitura solo sul TRAIN** (~70% dei dati). Ogni rifinitura spende tentativi.
4. **[G2] Holdout sigillato** (~30%): si apre **una volta per famiglia**, non per variante. Se lo
   guardi e poi rifinisci, è diventato train (§2).
5. **Verdetto**, dichiarato da Matteo: GO, LEAD, NO-GO, CLOSED, oppure "dati insufficienti", che non
   è un verdetto (§5).
6. **Dopo il verdetto.** Un LEAD richiede una nuova pre-registrazione e un **forward** sul futuro
   (se l'holdout era gia' tutto il campione, come per Gump, il contatore lo accetta solo con
   `gate_finale: "forward"` scritto prima dell'esito, `core/trial_ledger.py`, funzione `verifica`),
   l'unico dato davvero pulito e rinnovabile. Una strategia che ha già capitale si giudica contro
   la distribuzione dei suoi drawdown attesi, non contro l'umore (§8bis).

## Le regole che contano di più

- **Cosa costa un tentativo** (§3): correggere un bug o rendere l'esecuzione più realistica è
  **gratis**; cambiare parametro, asset o timeframe dopo aver visto l'esito, o aggiungere un filtro,
  **costa**. Il test operativo: *avresti fatto questa modifica se il risultato fosse stato positivo?*
  Se la risposta è no, è p-hacking (§4).
- **Fill ottenibile** (Step 3bis, bloccante): il prezzo a cui il backtest compra doveva essere
  ancora disponibile quando avremmo potuto agire. Senza la percentuale di fill non ottenibili
  **non c'è verdetto**, né positivo né negativo.
- **Baseline random** (gatekeeper, Checklist 1): ogni risultato si confronta con ingressi casuali
  a parità di asset, lato, rischio, periodo e regola d'uscita. *"Una soglia assoluta senza
  baseline non è una soglia."*
- **Kill duri** (§6a): difetto di metodo, non batte il random, negativo sulla maggior parte di
  asset e periodi, muore sui costi, instabile ai parametri, razionale falsificato. Nessun parametro
  li ripara.
- **Kill di budget** (§6b): massimo **3 round di rifinitura** per famiglia; budget di tentativi
  esaurito; **futilità** (sotto un certo Sharpe il risultato non potrà mai essere significativo,
  qualunque cosa si faccia).
- **Una famiglia chiusa non si riapre** con un ritocco o "più dati": solo con evidenza esterna
  nuova (§7).
- **Due binari per la gestione del rischio** (§4quater, dal 06/10): ogni test riporta il binario a
  **rischio fisso 1R**, l'unico su cui si dà il verdetto, e gli overlay della libreria fissa di
  `core/sizing.py`. Un overlay non salva un NO-GO; in prop si legge `ev_vs_zero`, mai l'EV da solo.
  Componente 14: [[14-prop-lab-e-doppio-binario]].
- **Quattro domande in più, non bloccanti** (gatekeeper, Checklist 9, dal 13/10): crescita geometrica e Kelly,
  Sharpe sopra 2 come campanello, regime, contributo al book. Vengono dal primo revisore, ritirato quel giorno;
  finiscono fra le riserve e non cambiano nessun gate.

## Come si lancia

```
python -m core.trial_ledger                  # stato di ogni famiglia + verifica
python -m core.trial_ledger --futilita 250   # Sharpe minimo per famiglia, a 250 osservazioni
python -m core.trial_ledger --check          # solo verifica: exit 1 se un budget è sforato
```

Il gatekeeper si chiama da una sessione Claude aperta su `trad/`, con il suo nome: *"usa il
quant-gatekeeper su …"*. Si usa tre volte: prima del backtest (G1), dopo averlo scritto, prima del
verdetto (G2). Il suo output ha sempre lo stesso formato: **PASSA / PASSA CON RISERVE / BLOCCA**,
con file e riga per ogni rilievo.

## Input → Output

- **Input:** un'idea con razionale, i dati, il codice dello studio in `analysis/<famiglia>/`. Un'idea dall'hub entra con la scheda del §8.
- **Output:** una pre-registrazione in `docs/`, un report in `docs/reviews/`, una voce in
  `DECISIONS.md`, lo stato nel frontmatter della pre-registrazione, una riga aggiornata in
  `docs/trial_ledger.json`.

## Stato atteso

| Cosa | Valore atteso | Come si controlla | Chi |
|---|---|---|---|
| Contatore coerente | nessun problema | `python -m core.trial_ledger --check` → exit 0 (il 02/10: exit 0) | Claude |
| Trimestre del contatore | uguale al trimestre di calendario | campo `trimestre_corrente` di `docs/trial_ledger.json` contro la data di oggi (il 02/10: **Q3 invece di Q4**) | Claude |
| Revisore indicato dai documenti di metodo | uno solo, ed è un agente che Claude Code carica | i riferimenti di `QUANT_REVIEW_PROTOCOL.md` e `STRATEGY_LIFECYCLE.md` §9 portano a `.claude/agents/` (il 02/10: **no**, portavano ad `agents/quant_reviewer.md`; il 13/10: **sì**, vecchio revisore ritirato) | Claude |
| Ogni famiglia con una pre-registrazione ha la sua riga nel contatore | sì | confronto tra `docs/*_PREREGISTRATION.md` e le voci del ledger | Claude |
| Ogni ipotesi arrivata dall'hub ha la scheda d'ingresso | sì | la nota di intake in `docs/reviews/` riporta P1-P6 o il punto in cui si e' fermata (il 25/10: prima prova, insider + geopolitica, fermata a P5 e alla domanda 6) | Claude |

## Come si rompe

**Guasti storici, già riparati:**
- *Contatore che non esiste.* Fino al 19/09 il conteggio dei tentativi andava ricostruito a mano,
  proprio quando si è meno severi con se stessi. Il 14/08 una decisione ("lasciar correre il
  forward ORB") è stata citata per due settimane come se fosse stata eseguita, e non lo era
  (`core/trial_ledger.py`, righe 11-14).
- *Soglie superabili senza edge.* Il 14/08 tre soglie assolute sono passate 6 su 6 e 15 su 15;
  solo il baseline random ha mostrato che erano garantite dalla costruzione (gatekeeper, righe 100-105).
- *Due revisori* (trovato il 02/10, riparato il 13/10). `QUANT_REVIEW_PROTOCOL.md` e `STRATEGY_LIFECYCLE.md` §9
  chiamavano revisore `agents/quant_reviewer.md`, da invocare con `skills/quant-review/`: cartelle alla radice che
  Claude Code **non carica** (carica solo `.claude/`). Chi seguiva il protocollo alla lettera cercava uno strumento
  che non parte. Ora quel file e la sua skill sono cancellati, i due documenti nominano il gatekeeper e le domande
  ancora valide del vecchio revisore sono la **Checklist 9** del gatekeeper, che non blocca. Lo stesso giorno, dopo
  aver verificato che nessuno strumento le carica e nessun codice le legge, sono state ritirate anche le altre voci
  di `agents/` e `skills/` alla radice (`DECISIONS.md` 2026-10-13 (4)).

**Guasti trovati scrivendo questa nota (02/10), non ancora riparati:**
- **Trimestre fermo.** `trimestre_corrente` è un campo scritto a mano: il 02/10 vale ancora
  `2026-Q3` e il comando segnala "soglia di allarme raggiunta" su un trimestre già chiuso. Incide
  sulla decisione D2 della pre-registrazione Gump (in quale trimestre conta).
- **Due campi di stato.** Il ledger ha un suo `stato` per famiglia (per i segnali mentore: `GO`),
  la pre-registrazione un altro (`CONFERMATO`). La regola di `trad/CLAUDE.md` dice che fa fede il
  frontmatter. Le due cose misurano livelli diversi, famiglia contro specifica, ma il vocabolario
  non coincide, e la seconda copia può divergere.

**Sintomi da riconoscere:** un "proviamo un'altra variante" senza che nessuno chieda quanti
tentativi restano; un risultato positivo senza baseline accanto; un verdetto senza la percentuale
di fill non ottenibili; una famiglia CLOSED che rientra "con più dati".

## Dipende da / chi dipende da lui

- **Usa:** le primitive di misura (componente 6: `core/quant_metrics.py`, `core/random_baseline.py`,
  `core/resolve_trade.py`, `core/data_checks.py`, `core/verifiche.py`) e il doppio binario con il
  simulatore prop (componente 14: `core/sizing.py`, `core/prop_sim.py` → `prop-lab/`).
- **Scrive in:** stato canonico e `DECISIONS.md` (componente 2).
- **Lo applicano:** ogni studio di `analysis/` (componenti 7 e 8), il copier e gli EA nella fase
  dopo il capitale (componenti 3 e 4).

## Con parole mie

