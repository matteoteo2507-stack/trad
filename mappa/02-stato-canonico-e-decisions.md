---
titolo: 2 · Stato canonico e DECISIONS
tipo: mappa
tags: [#public]
creato: 2026-10-02
compreso: no
verificato_il:
metodo:
---

# 2 · Stato canonico e DECISIONS

← [[00-panoramica-trad]] · componente 2 di 14 · viene da [[01-ciclo-di-vita-e-gate]]

## Cosa fa

Risponde a due domande, ognuna con **una sola fonte**:

| Domanda | Fonte | Forma |
|---|---|---|
| **A che punto è** una famiglia o una strategia, oggi? | il **frontmatter** della sua pre-registrazione, `docs/*_PREREGISTRATION.md` | cinque campi: `stato`, `aggiornato`, `decisione`, `metrica_corrente`, `nota` |
| **Cosa abbiamo deciso, quando e perché?** | `DECISIONS.md` | registro cronologico, **la voce più recente in alto**; non si riscrive, si aggiunge una voce nuova |

Tutto il resto **punta** a queste due fonti e non le ripete:
- `docs/README.md` elenca le pre-registrazioni con "cosa testa", senza stati né numeri;
- `mappa/_cruscotto.base` mostra i frontmatter in una tabella di Obsidian, ed è una vista, non una copia;
- la memoria di Claude (`memoria/trad/MEMORY.md`) rimanda al frontmatter per stati e numeri;
- i report in `docs/reviews/` sono fotografie datate: valgono per quel giorno, e se una voce
  successiva di `DECISIONS.md` li supera, è la voce a vincere.

## Perché esiste

Il **27/09/2026** Claude "mescolava le versioni": rispondeva con il numero o lo stato sbagliato,
perché la stessa informazione stava in molti posti che invecchiavano a velocità diverse. Esempi
misurati quel giorno (`mappa/_modifiche.md`, voci del 27/09):
- `docs/README.md` diceva **FADE ATTIVO** dieci giorni dopo il KILL del 17/09;
- il copier era citato a **+0,194** in alcuni file e a **+0,127** in `DECISIONS.md` dopo la
  correzione del 18/09;
- `_INTAKE.md` descriveva il FADE come "+0,35R robusto".

La cura è stata strutturale: lo stato vive in un posto solo, gli altri file **linkano**.

## L'ordine di lettura (regola di `trad/CLAUDE.md`)

1. **Frontmatter** della pre-registrazione → lo stato di oggi.
2. **`DECISIONS.md`**, partendo dall'alto → la voce più recente **vince su tutto ciò che la
   precede**, in qualunque file. Se un documento contraddice una voce più recente, è quel documento
   a essere vecchio: si segnala, non si fa la media.
3. **Metodo** (`STRATEGY_LIFECYCLE`, `QUANT_REVIEW_PROTOCOL`) → come si è arrivati al numero.
4. **Contatori** → `python -m core.trial_ledger`, mai numeri a memoria.

## Come si aggiorna

Dopo **ogni** verdetto, anche un NO-GO, nella **stessa sessione** (memoria
`feedback_post_verdict_repo_sync`, nata dal NO-GO NXT del 17/07 che non era finito in `DECISIONS.md`):
1. una voce nuova in cima a `DECISIONS.md`: data, decisione, razionale, link;
2. i cinque campi del frontmatter della pre-registrazione, con `decisione` che punta a quella voce;
3. la memoria e i documenti toccati. Un documento **superato si cancella** (git conserva la storia), dopo
   aver portato i fatti ancora validi nella nota canonica. **Resta solo ciò che serve come storico**, e allora
   non si riscrive: si aggiunge un marcatore **"⚠️ Superato"** con il rimando alla fonte nuova (Matteo, 13/10:
   concilia questa regola con quella dell'hub del 09/10). Un componente che ne sostituisce un altro **aggiorna
   lo stesso file**, o ritira il vecchio nella stessa sessione: due file per lo stesso ruolo non convivono.

## Stato atteso

| Cosa | Valore atteso | Come si controlla | Chi |
|---|---|---|---|
| Campi del frontmatter | ogni `docs/*_PREREGISTRATION.md` ha `stato`, `aggiornato`, `decisione` | lettura del frontmatter (il 02/10: tutte e 11 li hanno) | Claude |
| Frontmatter non più vecchio delle decisioni | `aggiornato` ≥ data della voce più recente di `DECISIONS.md` che nomina la famiglia | confronto delle date (il 02/10: **trend non conforme**, vedi sotto; allineato il 13/10) | Claude |
| Nessuno stato copiato | nei documenti di stato corrente nessuna famiglia KILL, CLOSED o NO-GO descritta come attiva senza "⚠️ Superato" | healthcheck, controllo A.2 | Claude |
| `docs/README.md` | non contiene stati né numeri | lettura della tabella delle pre-registrazioni | Claude |

## Come si rompe

**Il meccanismo è sempre lo stesso:** un'informazione scritta in due posti, aggiornata in uno solo.
Non dà errori: chi legge il posto vecchio riceve una risposta plausibile e sbagliata.

**Casi reali:**
- *27/09:* FADE "ATTIVO" in `docs/README.md` dopo il KILL.
- *02/10:* `mql5/README.md` descriveva l'EA `nxt_fade` come "WALK-FORWARD LIVE (attivo)",
  sempre dopo il KILL del 17/09. Trovato costruendo il catasto, e corretto facendo puntare ogni EA
  alla sua pre-registrazione. Le sezioni degli EA lo descrivevano ancora al presente: marcatori aggiunti il 13/10.
- *02/10, riparato il 13/10:* il frontmatter di `docs/TREND_EXIT_PLAYGROUND_PREREGISTRATION.md` aveva
  `aggiornato: 2026-09-21`, mentre `DECISIONS.md` nominava la famiglia il **30/09** (round 3 a B2) e il
  **03/10** (B2 chiusa a 0 trial, round 3 conservato alla famiglia). Lo stato `LEAD` era giusto, ma la nota
  era più vecchia di due decisioni. È rimasta così 11 giorni, finché l'ha segnalata l'healthcheck dell'hub.

**Debolezze strutturali:**
- **Vocabolario degli stati non chiuso.** La tassonomia dei verdetti (`STRATEGY_LIFECYCLE.md` §5) è
  GO, LEAD, NO-GO, CLOSED; nei frontmatter compaiono anche KILL e IN REVISIONE (misura del 13/10; il 02/10 anche CONFERMATO, IN AVVIO e BOZZA). Non
  c'è un elenco dei valori ammessi, quindi un filtro del cruscotto su "LEAD o GO" non vedrebbe un
  CONFERMATO.
- **Un secondo campo `stato`** in `docs/trial_ledger.json`, per famiglia, che per i segnali mentore
  diceva `GO` mentre il frontmatter diceva `CONFERMATO` (02/10; il 13/10 coincidono, `IN REVISIONE`; vedi [[01-ciclo-di-vita-e-gate]]).
- **L'intestazione di `DECISIONS.md`** (righe 8-9) dice che il file rispecchia la memoria in
  `~/.claude/projects/.../memory/`. Dal 27/09 la memoria sta in `memoria/trad/` nel vault.

**Dove guardare quando una risposta non torna:** prima il frontmatter, poi le prime voci di
`DECISIONS.md`. Se dicono cose diverse, vince la voce di `DECISIONS.md` più recente, e il frontmatter
va aggiornato.

## Dipende da / chi dipende da lui

- **Lo scrive:** il ciclo di vita ([[01-ciclo-di-vita-e-gate]]), a ogni verdetto.
- **Lo legge:** Claude in ogni sessione (ordine di `trad/CLAUDE.md`); il cruscotto; il healthcheck
  dell'hub (controlli A.1–A.4); chi decide se dare capitale (componenti 3, 4, 5).

## Con parole mie

