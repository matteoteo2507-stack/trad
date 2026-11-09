# uscita — pacchetti per i soci

Quinta macro del repo (DECISIONS 2026-11-09). Qui sta cio' che `trad` **consegna** ai soci: uno strumento di lettura del
prezzo che l'analisi da quant ha trovato applicabile coi nostri mezzi. Cos'e' uno strumento e cosa lo distingue da una
strategia: [04_quant_metodologia §0](../fondamenti_tecnici/04_quant_metodologia/principles.md).

La cartella resta anche vuota finche' non esce il primo pacchetto, come `Da distillare/`.

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
- Una *correzione* e' gratis. Una *modifica dopo l'esito* conta come **trial** nel contatore unico, e i dati dei soci
  che l'hanno motivata non sono piu' indipendenti per giudicarla.
- Cio' che torna dai soci (esiti, problemi) si registra in `DECISIONS.md`.

## Cosa non esce mai

Dati grezzi (licenze personali, DECISIONS 2026-11-05), credenziali, nomi, chat, orari e numeri di conto (il repo e'
pubblico).

## Consegne

| Strumento | Versione | Data | Tipo | A chi (ruolo) | Ritorno |
|---|---|---|---|---|---|

Nessuna consegna al 09/11/2026.
