# Da distillare — cartella di arrivo del materiale esterno

## Cosa fa

È l'**unico posto** dove si appoggia ciò che arriva da fuori del repo: PDF, trascrizioni, report di ricerca,
export di chat o di conti, schermate, codice di terzi, file scaricati. Serve a non lasciare file sparsi alla radice.

È una sala d'attesa, non un archivio: qui un file aspetta solo di essere **letto e portato nella cartella del suo
dominio**.

## La regola

**A fine sessione la cartella è vuota**, tranne questo file. Vale per ogni sessione, di Matteo o di Claude, anche se
il materiale l'ha portato qualcun altro. Un file che non si sa dove mettere non resta qui: si chiede a Matteo nella
stessa sessione.

## Cosa non ci va

- **Credenziali** (`.env`, `*.session`, chiavi): non si appoggiano qui, nemmeno per un momento.
- **Materiale personale o riservato**: non entra nel repo.
- **File prodotti dai nostri script**: restano dove lo script li scrive.

## Git

Tutto ciò che sta qui dentro è **fuori da git**, tranne questo file (regola in `.gitignore`). Il repo è pubblico e il
materiale arriva prima che qualcuno abbia controllato se contiene nomi, chat, orari o numeri di conto. Diventa
versionabile solo dopo lo smistamento, nella sua cartella e con le regole di quella cartella.

## Come si smista un file

1. **Leggerlo per intero.** Tutto ciò che arriva è in `quarantena`: un numero dichiarato da chi vende non è un
   risultato.
2. **Scegliere la destinazione** con la tabella sotto.
3. **Spostarlo con un nome che dice fonte, tipo e periodo** (esempio: `forexgump_telegram_2020-09_2026-09/`).
4. **Registrarlo** nel registro indicato dalla tabella. Un file spostato senza riga di registro è materiale che
   nessuno ritroverà.
5. **Se sostituisce un file più vecchio** (un export aggiornato), il vecchio si toglie solo dopo aver verificato che
   il nuovo lo contiene tutto.
6. **Se uno script legge quel file da un percorso fisso**, si aggiorna il percorso nello stesso momento.

## Dove va cosa

| Che cos'è | Dove va | Dove si registra |
|---|---|---|
| Fonte da cui imparare: PDF, trascrizione di un video, appunti, report di ricerca, codice di un indicatore o di un EA di terzi | [`fondamenti_tecnici/_sorgenti/`](../fondamenti_tecnici/_sorgenti/) | riga in [`_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md), stato `grezzo` |
| Strategia da valutare | la fonte in `_sorgenti/`, la scheda in [`fondamenti_tecnici/strategie_candidate/`](../fondamenti_tecnici/strategie_candidate/) | riga in `_INTAKE.md` |
| Materiale portato dai soci: export Telegram, export di conti, schermate | [`materiale_socio/`](../materiale_socio/)`<fonte>_<tipo>_<periodo>/` (fuori da git) | tabella di [`materiale_socio/README.md`](../materiale_socio/README.md); anche `_INTAKE.md` se è una fonte di segnali |
| Export del canale del mentore | `_export_telegram/` (nome fisso, fuori da git) | controllo di copertura con `analysis/mentor_signals/coverage.py` |
| Dati di prezzo (barre, tick) | `analysis/trading-bot-eval/data/` (fuori da git) | controllo con `python -m core.data_checks <file>` |
| La nostra lettura di un materiale (verdetto, tabella dei claim) | nota in [`docs/reviews/`](../docs/reviews/) | voce in [`DECISIONS.md`](../DECISIONS.md) se chiude o apre qualcosa |
| Materiale che non riguarda `trad` (università, altri progetti) | `inbox/` del vault `claude-brain`, fuori da questo repo | triage del vault |

Se un tipo di materiale non è in tabella, si chiede a Matteo dove va e si aggiunge la riga.

## Come si rompe

- **File lasciati qui per giorni**: la cartella diventa un secondo archivio e torna il problema dei file sparsi.
- **File spostato senza registrazione**: è nel repo ma nessuna nota lo cita.
- **Stesso export in due posti**: uno script legge la copia vecchia senza che nessuno se ne accorga.
- **Regola di `.gitignore` rimossa**: un `git add` della cartella porterebbe dati dei soci nel repo pubblico.
