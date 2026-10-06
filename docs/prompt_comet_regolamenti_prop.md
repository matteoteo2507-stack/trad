---
titolo: Prompt per Comet — regolamenti delle prop firm
tipo: strumento
creato: 2026-10-07
---

# Prompt per Comet — regolamenti delle prop firm

Serve a compilare la griglia di [PROP_FIRM_CRITERIA §3](PROP_FIRM_CRITERIA.md) e le voci reali di
`prop-lab/config/prop_rules.yaml`. **Versione 2 (07/10)**: corregge tre difetti della prima, usata il 06/10
(§3bis): la domanda sulla perdita giornaliera mescolava due cose, i `null` non dicevano perche', e i campi 7-13
stavano solo nella tabella.

Regola d'uso: **una firm per volta** (su compiti lunghi i browser AI perdono precisione). propfirmtrader.com
serve a trovare il sito ufficiale e i programmi, non come fonte delle regole: il 07/08 mostrava il regolamento
completo di 1 firm su 18 (DECISIONS 2026-08-07).

## A. Prompt per una firm nuova

Firm ancora da fare: FXIFY, Goat Funded Trader, Atlas Funded, Blueberry Funded, Alpha Capital Group.

```text
Parti da propfirmtrader.com e trova la scheda della prop firm {FIRM}. Usala SOLO per trovare il sito ufficiale
e l'elenco dei programmi. Poi apri il sito ufficiale (help center, FAQ, Terms & Conditions, pagina del
programma) e prendi ogni dato da li'.

Programmi: valutazione standard a 2 fasi, a 1 fase (se esiste), variante "Swing" (se esiste), conto da 100.000.

Per OGNI campo riporta: valore | frase testuale copiata dalla pagina | URL esatto | data di oggi.
Se non hai il valore, al posto del valore scrivi UNO di questi codici, mai lasciare vuoto:
  NON_TROVATO      = cercato nelle pagine ufficiali consultate, non trovato
  NON_PUBBLICATO   = la firm dice che non lo pubblica, o rimanda al supporto
  NON_APPLICABILE  = il campo non esiste in questo programma
Non dedurre, non stimare, non usare pagine di affiliati, comparatori, recensioni o codici sconto. Se un dato
e' SOLO su propfirmtrader.com scrivi accanto FONTE_SECONDARIA.

CAMPI
1. Costo della valutazione per 100k, con la valuta; rimborsato? quando?
2. Fasi: per ciascuna obiettivo di profitto %, giorni minimi di trading, limite massimo di giorni.
3a. Perdita giornaliera: quanto vale in % e la PERCENTUALE E' CALCOLATA SU cosa? (saldo iniziale del conto /
    saldo di inizio giornata / equity di inizio giornata)
3b. Perdita giornaliera: DA QUALE LIVELLO SI MISURA la discesa? (saldo di inizio giornata / equity di inizio
    giornata / il maggiore dei due / saldo iniziale, cioe' una soglia fissa che non si sposta mai)
3c. Il P&L FLOTTANTE delle posizioni aperte conta per la perdita giornaliera? A che ora si azzera e in che fuso?
4. Perdita massima: %; statica dal saldo iniziale, trailing sul picco intraday dell'equity, trailing sul picco
   di fine giornata, o trailing che si ferma al saldo iniziale? Il flottante conta?
5. Consistency rule: esiste? percentuale? come si calcola? dall'ultimo payout, dall'apertura del conto o su
   tutta la storia? vale in valutazione, nel conto finanziato o in entrambi?
6. Conto finanziato: profit split; giorni prima del primo payout; frequenza; il payout e' obbligatorio a
   scadenza o il profitto puo' accumularsi?
7. Posizioni overnight e nel weekend consentite? in quali programmi?
8. News: cosa e' vietato (aprire, chiudere, modificare), finestra in minuti, strumenti, valutazione o solo
   finanziato? tagli ai profitti fatti durante le news?
9. Expert Advisor su MetaTrader 5: consentiti? serve il sorgente .mq5 o una pre-approvazione? stili vietati?
10. Leva su XAUUSD e su NAS100 (o US100), per programma.
11. Disponibile ai residenti in Italia? Qualcosa pubblicato su ESMA / MiFID II o clienti UE?
12. Piattaforme (MT5 si/no), broker o server.
13. Data dell'ultima modifica del regolamento, se indicata.

FORMATO DELLA RISPOSTA
A) Tabella: una riga per campo, una colonna per programma, con valore (o codice), citazione, URL, data.
B) Per ogni programma questo blocco, con i codici dove manca il valore:

{FIRM}_{PROGRAMMA}:
  account: 100000
  fee: ""                      # numero e valuta
  refund_fee: ""
  phases:
    - {target_pct: "", min_days: "", max_days: ""}
  daily_loss_pct: ""
  daily_pct_su: ""             # initial_balance | day_start_balance | day_start_equity
  daily_misurata_da: ""        # day_start_balance | day_start_equity | max_balance_equity | initial_fixed
  daily_flottante: ""          # si | no
  daily_reset: ""              # ora e fuso
  max_loss_pct: ""
  max_loss_type: ""            # static | trailing_intraday | trailing_eod | trailing_lock_initial
  consistency_pct: ""
  consistency_finestra: ""     # since_last_payout | account_lifetime | other: spiegare
  consistency_dove: ""         # valutazione | finanziato | entrambi
  funded: {split_pct: "", first_payout_days: "", payout_every_days: "", accumulo_libero: ""}
  weekend: ""
  news: ""
  ea_mt5: ""
  leva_xauusd: ""
  leva_nas100: ""
  italia: ""
  ultima_modifica: ""

C) I punti in cui il sito ufficiale e propfirmtrader.com dicono cose diverse.
```

## B. Prompt di completamento per FTMO, FundedNext, The5ers (fatti il 06/10)

```text
Per la prop firm {FIRM} ho gia' questi valori, raccolti oggi da te: [incolla il blocco YAML del 06/10].
Ora, SOLO sul sito ufficiale della firm:
1. Per ogni valore gia' presente, dammi la frase testuale copiata dalla pagina, l'URL esatto e la data.
   Se non la ritrovi, scrivi NON_RITROVATO accanto al valore.
2. Per ogni null, sostituiscilo con NON_TROVATO, NON_PUBBLICATO o NON_APPLICABILE, oppure con il valore se
   adesso lo trovi (con citazione e URL).
3. Rispondi a queste domande separate sulla perdita giornaliera, con citazione:
   3a. la percentuale e' calcolata sul saldo iniziale, sul saldo di inizio giornata o sull'equity di inizio giornata?
   3b. la discesa si misura dal saldo di inizio giornata, dall'equity di inizio giornata, dal maggiore dei due,
       o da una soglia fissa sotto il saldo iniziale?
   3c. a che ora si azzera e in che fuso?
4. Compila anche i campi 7-13 del prompt A (weekend, news, EA su MT5, leva XAUUSD/NAS100, Italia, piattaforme,
   ultima modifica), con citazione.
Formato: lo stesso blocco del prompt A, punto B, piu' la tabella delle citazioni.
```

Quando torna l'output: si aggiornano `prop_rules.yaml` (voci `stato: da_verificare` → `verificato` solo con le
citazioni) e la griglia del §3.
