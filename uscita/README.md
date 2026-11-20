# uscita — pacchetti per i soci

Quinta macro del repo (DECISIONS 2026-11-09). Qui sta cio' che `trad` **consegna** ai soci: uno strumento di lettura del
prezzo che l'analisi da quant ha trovato applicabile coi nostri mezzi. Cos'e' uno strumento e cosa lo distingue da una
strategia: [04_quant_metodologia §0](../magazzino/fondamenti_tecnici/04_quant_metodologia/principles.md).

Il primo pacchetto e' uscito il 20/11/2026 (`volatilita_ewma/v1`).

## Com'e' fatto un pacchetto

Una cartella per strumento, una sottocartella per versione: `uscita/<strumento>/v<N>/`, con un `report.md` e i file
`.py` necessari (uno zip se serve spedirlo). Il `report.md` dichiara:

1. **lo strumento e la proprieta' misurata**, con l'esito e la nota sorgente (nessun numero senza fonte e data);
2. **su quali dati e' stato provato** (strumenti, periodo, fonte). I soci non possono usare quei dati come conferma
   indipendente dello strumento;
3. **limiti noti** e quando non usarlo;
4. **come si usa**, da solo o insieme ad altri strumenti, con i comandi per lanciarlo;
5. **versione e tipo**: *correzione* (bug, applicazione sbagliata) oppure *modifica dopo l'esito* dei test dei soci.

## Il ciclo di ritorno

- Al massimo **5 versioni** per strumento; alla quinta lo strumento si chiude o si riformula da capo.
- Una versione **resta in `uscita/` finche' e' quella in uso** dai soci, che la prendono da GitHub su `main`.
  Quando esce la successiva si cancella: git la conserva, e la colonna "Commit" della tabella Consegne registra
  l'ultimo commit di `main` che la contiene, da cui recuperarla (Matteo, 20/11; DECISIONS 2026-11-20 (2)).
- Una *correzione* e' gratis. Una *modifica dopo l'esito* conta come **trial** nel contatore unico, e i dati dei soci
  che l'hanno motivata non sono piu' indipendenti per giudicarla.
- Cio' che torna dai soci (esiti, problemi) si registra in `DECISIONS.md`.

## Cosa non esce mai

Dati grezzi (licenze personali, DECISIONS 2026-11-05), credenziali, nomi, chat, orari e numeri di conto (il repo e'
pubblico).

## Consegne

| Strumento | Versione | Data | Tipo | A chi (ruolo) | Ritorno | Commit (alla cancellazione) |
|---|---|---|---|---|---|---|
| [`volatilita_ewma`](volatilita_ewma/v1/report.md) | v1 | 2026-11-20 | prima consegna (0 trial) | tutti i soci | nessuno | in uso |

**Regola sui dati futuri della volatilita'** ([report v1](volatilita_ewma/v1/report.md), punto 2): **non attiva**.
Parte il giorno della pre-registrazione del ridisegno della famiglia, che si scrive qui.
