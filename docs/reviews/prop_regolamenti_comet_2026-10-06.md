---
titolo: "Regolamenti prop: secondo passaggio Comet (FTMO, FundedNext, The5ers)"
tipo: fonte
creato: 2026-10-07
fonte: "Comet (browser AI di Matteo), pagine ufficiali delle firm consultate il 2026-10-06; prompt in docs/prompt_comet_regolamenti_prop.md (B)"
stato: citato_senza_url
---

# Regolamenti prop: secondo passaggio Comet

> **Cos'e'.** L'output integrale di Comet, portato da Matteo il 07/10 (file "Exportcomet da integrare"), **senza
> modifiche** sotto la riga. E' la fonte delle voci `ftmo_*`, `fundednext_*`, `the5ers_*` di
> `prop-lab/config/prop_rules.yaml` e della griglia di [PROP_FIRM_CRITERIA §3](../PROP_FIRM_CRITERIA.md).
>
> **Come leggerlo (07/10):**
> - ogni valore ha una **frase citata** e il **nome della pagina**, ma **non l'URL**: la colonna "URL" contiene
>   nomi di pagina. Stato `citato_senza_url`: utilizzabile per orientarsi, non per una decisione con soldi;
> - **contraddizioni col primo passaggio del 06/10** (registrate, non risolte): FundedNext consistency 40% -> ora
>   DA_VERIFICARE; FundedNext Stellar 2-Step costo 549 -> ora NON_TROVATO; FTMO 1-Step "nessuna consistency" -> ora
>   **Best Day Rule 50%**;
> - **FundedNext, livello della perdita giornaliera**: "soglia fissa a 95.000" e' una **deduzione di Comet**, non una
>   citazione. La frase dice *"in a single day"*, che punta a un riferimento giornaliero; l'ora di reset e' NON_TROVATO;
> - **The5ers**: obiettivi, consistency e perdita massima vengono in parte dalla pagina promozionale "Summer Plan";
> - FTMO Standard funded: la frase citata sulle restrizioni non distingue **overnight** da **weekend**.

---

Nota: gli importi monetari sono calcolati applicando le percentuali ufficiali al capitale nominale. Quando la firm non pubblica esplicitamente il valore monetario per quella taglia, lo indico come CALCOLATO, non come dato testuale della pagina.

Legenda dei valori null
text
null_status:
  NON_TROVATO:
    meaning: "Il dato non è stato trovato nelle pagine ufficiali consultate."
  NON_PUBBLICATO:
    meaning: "Il dato è stato cercato nelle fonti pertinenti, ma la firm non pubblica quel dettaglio."
  NON_APPLICABILE:
    meaning: "Il campo non si applica a quel programma o a quella variante."
  DA_VERIFICARE:
    meaning: "Esiste una fonte ufficiale collegata, ma non è stato possibile verificare il testo completo o la versione applicabile."
Nel blocco YAML uso null, ma aggiungo sempre un campo null_reason.

FTMO
FTMO — regole comuni
FTMO mette a disposizione conti simulati da 10.000, 25.000, 50.000, 100.000 e 200.000 USD.

FTMO 2-Step
| Campo                      | 10k                                                                      | 25k               | 50k               | 100k              | Frase ufficiale                                                                                        | URL                             | Data       |
| -------------------------- | ------------------------------------------------------------------------ | ----------------- | ----------------- | ----------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------- | ---------- |
| Fase 1 target              | 10% = 1.000                                                              | 10% = 2.500       | 10% = 5.000       | 10% = 10.000      | “Profit Target 10%”                                                                                    | FTMO Trading Objectives         | 06/10/2026 |
| Fase 2 target              | 5% = 500                                                                 | 5% = 1.250        | 5% = 2.500        | 5% = 5.000        | “Profit Target 5% for the Verification”                                                                | FTMO Trading Objectives         | 06/10/2026 |
| Minimo giorni              | 4 per fase                                                               | 4 per fase        | 4 per fase        | 4 per fase        | “at least 4 Trading Days”                                                                              | FTMO Trading Objectives         | 06/10/2026 |
| Massimo giorni             | Illimitati                                                               | Illimitati        | Illimitati        | Illimitati        | “No time limit”                                                                                        | FTMO Trading Objectives         | 06/10/2026 |
| Daily loss %               | 5%                                                                       | 5%                | 5%                | 5%                | “Maximum Daily Loss Amount … is 5% of the Initial Simulated Capital”                                   | FTMO Trading Objectives         | 06/10/2026 |
| Daily loss importo         | 500                                                                      | 1.250             | 2.500             | 5.000             | Calcolo sulla percentuale ufficiale                                                                    | FTMO Trading Objectives         | 06/10/2026 |
| Base della percentuale     | Capitale iniziale                                                        | Capitale iniziale | Capitale iniziale | Capitale iniziale | “5% of the Initial Simulated Capital”                                                                  | FTMO Trading Objectives         | 06/10/2026 |
| Livello da cui si misura   | Saldo registrato alle 00:00 CE(S)T                                       | Uguale            | Uguale            | Uguale            | “account balance recorded at 00:00 CE(S)T”                                                             | FTMO Trading Objectives         | 06/10/2026 |
| P&L flottante incluso      | Sì                                                                       | Sì                | Sì                | Sì                | “Equity (i.e., Balance + Open Positions P/L ± Swaps – Commissions)”                                    | FTMO Trading Objectives         | 06/10/2026 |
| Reset                      | 00:00 CE(S)T                                                             | Uguale            | Uguale            | Uguale            | “recalculated daily at 00:00 CE(S)T”                                                                   | FTMO Trading Objectives         | 06/10/2026 |
| Maximum loss               | 10%                                                                      | 10%               | 10%               | 10%               | “The Maximum Loss rule establishes a static limit”                                                     | FTMO Trading Objectives         | 06/10/2026 |
| Maximum loss importo       | 1.000                                                                    | 2.500             | 5.000             | 10.000            | Calcolo sulla percentuale ufficiale                                                                    | FTMO Trading Objectives         | 06/10/2026 |
| Tipo maximum loss          | Statico                                                                  | Statico           | Statico           | Statico           | “static limit”                                                                                         | FTMO Trading Objectives         | 06/10/2026 |
| Consistency                | Non richiesta come regola separata del 2-Step                            | Uguale            | Uguale            | Uguale            | “Do you have any consistency rules?” — regole valutate tramite Trading Objectives                      | FTMO consistency FAQ            | 06/10/2026 |
| Overnight/weekend Standard | Consentiti in valutazione; vietati nel funded Standard                   | Uguale            | Uguale            | Uguale            | “these restrictions apply only once you start trading on an FTMO Account”                              | FTMO overnight FAQ              | 06/10/2026 |
| Overnight/weekend Swing    | Consentiti                                                               | Consentiti        | Consentiti        | Consentiti        | “Swing account type does not have any restrictions on holding positions overnight or over the weekend” | FTMO Swing FAQ                  | 06/10/2026 |
| News Standard              | Restrizioni solo funded                                                  | Uguale            | Uguale            | Uguale            | “Restrictions … apply only to the Standard account type”                                               | FTMO news FAQ                   | 06/10/2026 |
| Finestra news              | 2 minuti prima / 2 dopo                                                  | Uguale            | Uguale            | Uguale            | “starting 2 minutes before and ending 2 minutes after”                                                 | FTMO news FAQ                   | 06/10/2026 |
| News Swing                 | Consentite senza restrizioni specifiche                                  | Uguale            | Uguale            | Uguale            | “Swing account type have no restrictions on trading during news releases”                              | FTMO news FAQ                   | 06/10/2026 |
| Profit split funded        | 80%, potenzialmente 90%                                                  | Uguale            | Uguale            | Uguale            | “80% … increased to 90%”                                                                               | FTMO Reward Growth              | 06/10/2026 |
| Primo payout               | 14 giorni dal primo trade                                                | Uguale            | Uguale            | Uguale            | “after 14 days from your first trade”                                                                  | FTMO FAQ                        | 06/10/2026 |
| Accumulo profitto          | Sì nel 2-Step                                                            | Sì                | Sì                | Sì                | Rollover previsto nel 2-Step                                                                           | FTMO FAQ                        | 06/10/2026 |
| Rimborso fee               | Sì con primo Reward                                                      | Uguale            | Uguale            | Uguale            | “initial fee is refunded with the first Reward withdrawal”                                             | FTMO FAQ                        | 06/10/2026 |
| EA MT5                     | Consentiti se conformi                                                   | Uguale            | Uguale            | Uguale            | “Your trading style is up to you … provided … not forbidden practices”                                 | FTMO instruments/strategies FAQ | 06/10/2026 |
| Codice .mq5                | Non richiesto nella FAQ consultata                                       | Uguale            | Uguale            | Uguale            | NON PUBBLICATO                                                                                         | FTMO strategies FAQ             | 06/10/2026 |
| HFT/latency arbitrage      | Vietati se costituiscono pratica proibita                                | Uguale            | Uguale            | Uguale            | Riferimento alle “forbidden practices”                                                                 | FTMO strategies FAQ             | 06/10/2026 |
| Leva Standard              | Fino a 1:100, secondo specifiche conto                                   | Uguale            | Uguale            | Uguale            | Dato visualizzato nelle account specifications                                                         | FTMO account specifications     | 06/10/2026 |
| Leva Swing                 | Fino a 1:30, secondo specifiche conto                                    | Uguale            | Uguale            | Uguale            | Dato visualizzato nelle account specifications                                                         | FTMO account specifications     | 06/10/2026 |
| Leva XAUUSD                | Non separata nella pagina testuale                                       | Uguale            | Uguale            | Uguale            | NON PUBBLICATO come campo testuale per taglia                                                          | FTMO account specifications     | 06/10/2026 |
| Leva NAS100/US100          | Non separata nella pagina testuale                                       | Uguale            | Uguale            | Uguale            | NON PUBBLICATO come campo testuale per taglia                                                          | FTMO account specifications     | 06/10/2026 |
| MT5                        | Sì                                                                       | Sì                | Sì                | Sì                | FTMO fornisce accesso alla piattaforma MT5; server indicato nelle credenziali                          | FTMO MT5 login                  | 06/10/2026 |
| Broker                     | Non è un broker                                                          | Uguale            | Uguale            | Uguale            | “FTMO companies do not act as a broker”                                                                | FTMO MT5 login                  | 06/10/2026 |
| Italia                     | Ammessa, non inclusa nell’elenco delle restrizioni consultato            | Uguale            | Uguale            | Uguale            | “we accept clients globally” salvo eccezioni                                                           | FTMO eligibility                | 06/10/2026 |
| ESMA/MiFID II              | Nessuna applicabilità dichiarata come servizio finanziario regolamentato | Uguale            | Uguale            | Uguale            | FTMO descrive il servizio come simulazione e non broker                                                | FTMO legal relationship         | 06/10/2026 |
| Ultima modifica            | 30/09/2026 per le FAQ consultate                                         | Uguale            | Uguale            | Uguale            | Data mostrata dalla pagina                                                                             | URL sopra                       | 06/10/2026 |

FTMO 1-Step
| Campo              | 10k                                                                                  | 25k         | 50k         | 100k         | Frase ufficiale                                                       | URL                         | Data       |
| ------------------ | ------------------------------------------------------------------------------------ | ----------- | ----------- | ------------ | --------------------------------------------------------------------- | --------------------------- | ---------- |
| Target             | 10% = 1.000                                                                          | 10% = 2.500 | 10% = 5.000 | 10% = 10.000 | “Reach a 10% profit”                                                  | FTMO 1-Step                 | 06/10/2026 |
| Daily loss         | 3% = 300                                                                             | 3% = 750    | 3% = 1.500  | 3% = 3.000   | “Max Daily Loss 3%”                                                   | FTMO 1-Step                 | 06/10/2026 |
| Daily basis        | Capitale iniziale come base della percentuale; saldo di inizio giornata come livello | Uguale      | Uguale      | Uguale       | “account balance recorded at 00:00 CE(S)T” e 3% del capitale iniziale | FTMO Trading Objectives     | 06/10/2026 |
| Floating P&L       | Incluso                                                                              | Incluso     | Incluso     | Incluso      | “Balance + Open Positions P/L ± Swaps – Commissions”                  | FTMO Trading Objectives     | 06/10/2026 |
| Maximum loss       | Trailing EOD 10%                                                                     | Uguale      | Uguale      | Uguale       | “end-of-day trailing limit”                                           | FTMO Trading Objectives     | 06/10/2026 |
| Best Day Rule      | 50%                                                                                  | Uguale      | Uguale      | Uguale       | “Best Day … not … more than 50%”                                      | FTMO Trading Objectives     | 06/10/2026 |
| Overnight/weekend  | Swing non disponibile per 1-Step                                                     | Uguale      | Uguale      | Uguale       | “Swing account type is not offered for … 1-Step”                      | FTMO 1-Step                 | 06/10/2026 |
| News               | Standard: finestra 2+2 minuti nel funded; valutazione non soggetta                   | Uguale      | Uguale      | Uguale       | “restrictions … only to the Standard account type”                    | FTMO news FAQ               | 06/10/2026 |
| Profit split       | 90%                                                                                  | Uguale      | Uguale      | Uguale       | “90% of your simulated profits”                                       | FTMO 1-Step                 | 06/10/2026 |
| Primo payout       | 14 giorni                                                                            | Uguale      | Uguale      | Uguale       | “after 14 days from your first trade”                                 | FTMO FAQ                    | 06/10/2026 |
| Rimborso fee       | No                                                                                   | No          | No          | No           | “initial fee is not refunded”                                         | FTMO FAQ                    | 06/10/2026 |
| Accumulo profitto  | No                                                                                   | No          | No          | No           | Regola specifica 1-Step                                               | FTMO FAQ                    | 06/10/2026 |
| EA                 | Consentiti se conformi                                                               | Uguale      | Uguale      | Uguale       | “trading style is up to you” salvo pratiche vietate                   | FTMO strategies FAQ         | 06/10/2026 |
| Leva XAUUSD/NAS100 | Non separata nel testo                                                               | Uguale      | Uguale      | Uguale       | NON PUBBLICATO                                                        | FTMO account specifications | 06/10/2026 |
| Italia             | Ammessa salvo esclusioni generali                                                    | Uguale      | Uguale      | Uguale       | “we accept clients globally”                                          | FTMO eligibility            | 06/10/2026 |

FTMO_2-Step:
  description: "FTMO Challenge 2-Step, conto simulato"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: NON_TROVATO
  daily_loss_pct: 5
  daily_loss_base: initial_capital
  daily_loss_measurement_level: day_start_balance
  daily_basis: day_start_balance
  daily_includes_floating: true
  daily_reset: "00:00 CE(S)T"
  max_loss_pct: 10
  max_loss_type: static
  trailing_lock: null
  trailing_lock_null_reason: NON_APPLICABILE
  consistency_pct: null
  consistency_null_reason: NON_APPLICABILE
  phases:
    - {name: fase1, target_pct: 10, min_days: 4, max_days: null}
    - {name: fase2, target_pct: 5, min_days: 4, max_days: null}
  funded:
    split_pct: 80
    payout_every: "on demand from day 14"
    first_payout_days: 14
    refund_fee: true
    accumulo_libero: true
  overnight_weekend:
    standard_evaluation: true
    standard_funded: false
    swing: true
  news:
    evaluation: true
    standard_funded: restricted
    swing_funded: allowed
  ea_mt5: true
  source_code_required: null
  source_code_null_reason: NON_TROVATO
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  italy: true
  esma_mifid_statement: null
  esma_mifid_null_reason: NON_PUBBLICATO

FTMO_1-Step:
  description: "FTMO Challenge 1-Step"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: NON_TROVATO
  daily_loss_pct: 3
  daily_loss_base: initial_capital
  daily_loss_measurement_level: day_start_balance
  daily_basis: day_start_balance
  daily_includes_floating: true
  daily_reset: "00:00 CE(S)T"
  max_loss_pct: 10
  max_loss_type: trailing_eod
  trailing_lock: false
  consistency_pct: 50
  consistency_window: account_lifetime
  phases:
    - {name: fase1, target_pct: 10, min_days: null, max_days: null}
  funded:
    split_pct: 90
    payout_every: "on demand from day 14"
    first_payout_days: 14
    refund_fee: false
    accumulo_libero: false
  overnight_weekend:
    standard_evaluation: true
    standard_funded: false
    swing: false
  news:
    evaluation: true
    standard_funded: restricted
    swing_funded: NON_APPLICABILE
  ea_mt5: true
  source_code_required: null
  source_code_null_reason: NON_TROVATO
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  italy: true

FundedNext
Chiarimento fondamentale sul daily loss
Per FundedNext il precedente daily_basis: initial era ambiguo.

La formulazione ufficiale dice:

“Your account must not lose more than 5% of the initial balance in a single day.”

Quindi bisogna separare:

text
daily_loss:
  percentage_base: initial_balance
  measurement_level: initial_balance_minus_daily_limit
  daily_reset_reference: null
In altri termini, per un conto da 100.000 Stellar 2-Step:

base del 5%: saldo iniziale = 100.000;

limite monetario: 5.000;

livello di violazione: 95.000;

equity rilevante: comprende P&L aperto, swap e commissioni secondo la pagina generale;

non è corretto scrivere solo initial, perché quello non chiarisce da quale livello il simulatore misura l’equity.

FundedNext Stellar 2-Step
| Campo                      | 10k                                                                                | 25k             | 50k             | 100k            | Frase ufficiale                                                                                     | URL                             | Data       |
| -------------------------- | ---------------------------------------------------------------------------------- | --------------- | --------------- | --------------- | --------------------------------------------------------------------------------------------------- | ------------------------------- | ---------- |
| Fase 1 target              | 800                                                                                | 2.000           | 4.000           | 8.000           | “8% in Phase 1”                                                                                     | Stellar 2-Step target           | 06/10/2026 |
| Fase 2 target              | 500                                                                                | 1.250           | 2.500           | 5.000           | “5% in Phase 2”                                                                                     | Stellar 2-Step target           | 06/10/2026 |
| Minimo giorni              | 5 per fase                                                                         | 5               | 5               | 5               | “at least 5 different days”                                                                         | Stellar 2-Step rules            | 06/10/2026 |
| Massimo giorni             | Illimitato                                                                         | Illimitato      | Illimitato      | Illimitato      | “both with no time limit”                                                                           | Stellar 2-Step target           | 06/10/2026 |
| Daily loss %               | 5%                                                                                 | 5%              | 5%              | 5%              | “must not lose more than 5% of the initial balance in a single day”                                 | Stellar 2-Step rules            | 06/10/2026 |
| Base percentuale           | Saldo iniziale                                                                     | Saldo iniziale  | Saldo iniziale  | Saldo iniziale  | “5% of the initial balance”                                                                         | Stellar 2-Step rules            | 06/10/2026 |
| Livello misura             | 95% del saldo iniziale                                                             | 95%             | 95%             | 95%             | “must not lose more than 5%”                                                                        | Stellar 2-Step rules            | 06/10/2026 |
| Daily loss importo         | 500                                                                                | 1.250           | 2.500           | 5.000           | Calcolo sulla frase ufficiale                                                                       | FundedNext daily loss FAQ       | 06/10/2026 |
| Floating P&L               | Incluso                                                                            | Incluso         | Incluso         | Incluso         | “Includes realized and unrealized P&L, swap, and commission”                                        | FundedNext trading objectives   | 06/10/2026 |
| Maximum loss               | 10%                                                                                | 10%             | 10%             | 10%             | “account must not drop below 90% of its initial balance”                                            | Stellar 2-Step rules            | 06/10/2026 |
| Maximum loss importo       | 1.000                                                                              | 2.500           | 5.000           | 10.000          | Calcolo sulla frase ufficiale                                                                       | FundedNext daily loss FAQ       | 06/10/2026 |
| Tipo maximum loss          | Statico                                                                            | Statico         | Statico         | Statico         | “initial balance”                                                                                   | FundedNext trading objectives   | 06/10/2026 |
| News in challenge          | Consentito                                                                         | Consentito      | Consentito      | Consentito      | “allows traders to trade during news events in both the Challenge Phase and the FundedNext Account” | FundedNext news rules           | 06/10/2026 |
| News funded window         | 5 minuti prima / 5 dopo                                                            | Uguale          | Uguale          | Uguale          | “5 minutes before and 5 minutes after”                                                              | FundedNext news rules           | 06/10/2026 |
| News funded profit         | Conta solo il 40% del profitto                                                     | Uguale          | Uguale          | Uguale          | “40% of the profit … will be counted”                                                               | FundedNext news rules           | 06/10/2026 |
| News perdite               | Interamente a carico del trader                                                    | Uguale          | Uguale          | Uguale          | “Any losses … remain the trader’s responsibility”                                                   | FundedNext news rules           | 06/10/2026 |
| EA MT5 sotto 50k           | Consentito con fee/add-on                                                          | Consentito      | Non applicabile | Non applicabile | “accounts below $50,000”                                                                            | FundedNext EA rules             | 06/10/2026 |
| EA MT5 da 50k              | Non applicabile                                                                    | Non applicabile | Vietato         | Vietato         | “$50,000 and above must trade manually”                                                             | FundedNext EA rules             | 06/10/2026 |
| EA su cTrader/Match-Trader | Vietato                                                                            | Vietato         | Vietato         | Vietato         | “do not allow … automated trading”                                                                  | FundedNext EA rules             | 06/10/2026 |
| Codice .mq5                | Non richiesto nella fonte consultata                                               | Uguale          | Uguale          | Uguale          | NON PUBBLICATO                                                                                      | FundedNext EA rules             | 06/10/2026 |
| EA challenge-pass          | Vietato                                                                            | Vietato         | Vietato         | Vietato         | “EAs … designed specifically to pass Prop firm challenges are strictly prohibited”                  | FundedNext EA rules             | 06/10/2026 |
| MT5                        | Sì                                                                                 | Sì              | Sì              | Sì              | “MT4 and MT5”                                                                                       | FundedNext EA rules             | 06/10/2026 |
| Broker                     | Nessun broker terzo                                                                | Uguale          | Uguale          | Uguale          | “FundedNext is not a broker”                                                                        | FundedNext broker FAQ           | 06/10/2026 |
| Server/liquidity           | Infrastruttura interna e liquidity providers aggregati                             | Uguale          | Uguale          | Uguale          | “internal trading technology systems … top-tier liquidity providers”                                | FundedNext broker FAQ           | 06/10/2026 |
| Italia                     | Non inclusa nell’elenco dei paesi CFD vietati consultato                           | Uguale          | Uguale          | Uguale          | Elenco ufficiale delle restrizioni                                                                  | FundedNext country restrictions | 06/10/2026 |
| ESMA/MiFID II              | FundedNext dichiara di non essere soggetta al quadro usuale dei servizi finanziari | Uguale          | Uguale          | Uguale          | “does not manage client funds … usual regulatory requirements … do not apply”                       | FundedNext regulation FAQ       | 06/10/2026 |
| Leva XAUUSD                | Non pubblicata nella fonte consultata                                              | Uguale          | Uguale          | Uguale          | NON PUBBLICATO                                                                                      | FundedNext tradable assets      | 06/10/2026 |
| Leva NAS100                | Non pubblicata nella fonte consultata                                              | Uguale          | Uguale          | Uguale          | NON PUBBLICATO                                                                                      | FundedNext tradable assets      | 06/10/2026 |

FundedNext Stellar 1-Step
| Campo                      | 10k                                           | 25k               | 50k               | 100k               | Frase ufficiale                                                                       | URL                           | Data       |
| -------------------------- | --------------------------------------------- | ----------------- | ----------------- | ------------------ | ------------------------------------------------------------------------------------- | ----------------------------- | ---------- |
| Account disponibili/prezzo | 10k: da verificare nella tabella completa     | 25k: circa 219,99 | 50k: circa 329,99 | 100k: circa 569,99 | Tabella account e prezzi                                                              | Stellar 1-Step Account        | 06/10/2026 |
| Daily loss                 | 3%                                            | 3%                | 3%                | 3%                 | “Stellar 1-Step: 3% of initial balance”                                               | FundedNext trading objectives | 06/10/2026 |
| Daily loss importo         | 300                                           | 750               | 1.500             | 3.000              | Calcolo percentuale                                                                   | FundedNext trading objectives | 06/10/2026 |
| Maximum loss               | 6%                                            | 6%                | 6%                | 6%                 | “Stellar 1-Step: 6%”                                                                  | FundedNext trading objectives | 06/10/2026 |
| Maximum loss importo       | 600                                           | 1.500             | 3.000             | 6.000              | Calcolo percentuale                                                                   | FundedNext trading objectives | 06/10/2026 |
| EA                         | Consentito sotto 50k                          | Consentito        | Vietato           | Vietato            | “$50,000 and above … manually”                                                        | FundedNext EA rules           | 06/10/2026 |
| News                       | Challenge consentita; funded 40% profit share | Uguale            | Uguale            | Uguale             | “applies only to Stellar 1-Step, Stellar 2-Step and Stellar Lite FundedNext Accounts” | FundedNext news rules         | 06/10/2026 |
| Payout/split               | 80% iniziale; ciclo esatto da verificare      | Uguale            | Uguale            | Uguale             | Reward Share structure                                                                | FundedNext Reward Share       | 06/10/2026 |
| Leva XAUUSD/NAS100         | Non pubblicata                                | Non pubblicata    | Non pubblicata    | Non pubblicata     | NON PUBBLICATO                                                                        | FundedNext tradable assets    | 06/10/2026 |
| Italia                     | Ammessa salvo lista restrizioni               | Uguale            | Uguale            | Uguale             | Lista ufficiale paesi vietati                                                         | FundedNext restrictions       | 06/10/2026 |

FundedNext Stellar Lite
| Campo              | 10k                                           | 25k            | 50k            | 100k           | Frase ufficiale                                 | URL                   | Data       |
| ------------------ | --------------------------------------------- | -------------- | -------------- | -------------- | ----------------------------------------------- | --------------------- | ---------- |
| Fase 1             | 8% = 800                                      | 8% = 2.000     | 8% = 4.000     | 8% = 8.000     | “8% Profit Target”                              | Stellar Lite          | 06/10/2026 |
| Fase 2             | 4% = 400                                      | 4% = 1.000     | 4% = 2.000     | 4% = 4.000     | “4% Profit Target”                              | Stellar Lite          | 06/10/2026 |
| Daily loss         | 4%                                            | 4%             | 4%             | 4%             | “4% Daily Loss Limit”                           | Stellar Lite          | 06/10/2026 |
| Maximum loss       | 8%                                            | 8%             | 8%             | 8%             | “8% Maximum Loss”                               | Stellar Lite          | 06/10/2026 |
| EA                 | Consentito sotto 50k                          | Consentito     | Vietato        | Vietato        | Regola generale account size                    | FundedNext EA rules   | 06/10/2026 |
| News               | Challenge consentita; funded 40% profit share | Uguale         | Uguale         | Uguale         | “News Reward Share Rule applies … Stellar Lite” | FundedNext news rules | 06/10/2026 |
| Overnight/weekend  | NON TROVATO specifico per Stellar Lite        | Uguale         | Uguale         | Uguale         | NON TROVATO                                     | —                     | 06/10/2026 |
| Leva XAUUSD/NAS100 | NON PUBBLICATO                                | NON PUBBLICATO | NON PUBBLICATO | NON PUBBLICATO | NON PUBBLICATO                                  | —                     | 06/10/2026 |

FundedNext_Stellar_2-Step:
  description: "Stellar 2-Step CFD Challenge"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: NON_TROVATO
  daily_loss_pct: 5
  daily_loss_base: initial_balance
  daily_loss_measurement_level: "initial_balance - 5%"
  daily_basis: initial_balance
  daily_includes_floating: true
  daily_reset: null
  daily_reset_null_reason: NON_TROVATO
  max_loss_pct: 10
  max_loss_type: static
  trailing_lock: null
  trailing_lock_null_reason: NON_APPLICABILE
  consistency_pct: null
  consistency_null_reason: DA_VERIFICARE
  phases:
    - {name: fase1, target_pct: 8, min_days: 5, max_days: null}
    - {name: fase2, target_pct: 5, min_days: 5, max_days: null}
  funded:
    split_pct: 80
    payout_every: "initial 21-day cycle; exact recurring frequency depends on selected reward option"
    first_payout_days: 21
    refund_fee: null
    refund_fee_null_reason: DA_VERIFICARE
    accumulo_libero: null
    accumulo_libero_null_reason: NON_TROVATO
  overnight_weekend: null
  overnight_weekend_null_reason: NON_TROVATO
  news:
    challenge: allowed
    funded: "allowed; 40% of correlated high-impact-news profit counted"
    window_minutes_each_side: 5
  ea:
    below_50000: allowed_with_fee
    50000_and_above: prohibited
    source_code_required: null
    source_code_null_reason: NON_TROVATO
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  platforms: [MT4, MT5, cTrader, Match-Trader]
  broker: "No third-party broker; internal infrastructure"
  italy: true
  esma_mifid_statement: "FundedNext states ordinary financial-services regulations do not apply because it does not manage client funds or trade for the public."
  FundedNext_Stellar_1-Step:
  description: "Stellar 1-Step CFD Challenge"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: DA_VERIFICARE
  daily_loss_pct: 3
  daily_loss_base: initial_balance
  daily_loss_measurement_level: "initial_balance - 3%"
  daily_basis: initial_balance
  daily_includes_floating: true
  daily_reset: null
  daily_reset_null_reason: NON_TROVATO
  max_loss_pct: 6
  max_loss_type: static
  trailing_lock: null
  trailing_lock_null_reason: NON_APPLICABILE
  consistency_pct: null
  consistency_null_reason: DA_VERIFICARE
  phases:
    - {name: fase1, target_pct: null, min_days: 5, max_days: null}
  funded:
    split_pct: 80
    payout_every: null
    payout_every_null_reason: DA_VERIFICARE
    first_payout_days: null
    first_payout_days_null_reason: DA_VERIFICARE
    refund_fee: null
    refund_fee_null_reason: DA_VERIFICARE
    accumulo_libero: null
    accumulo_libero_null_reason: NON_TROVATO
  overnight_weekend: null
  overnight_weekend_null_reason: NON_TROVATO
  news:
    challenge: allowed
    funded: "allowed; 40% of correlated high-impact-news profit counted"
    window_minutes_each_side: 5
  ea:
    below_50000: allowed_with_fee
    50000_and_above: prohibited
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  italy: true

  FundedNext_Stellar_Lite:
  description: "Stellar Lite two-phase CFD Challenge"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: DA_VERIFICARE
  daily_loss_pct: 4
  daily_loss_base: initial_balance
  daily_loss_measurement_level: "initial_balance - 4%"
  daily_basis: initial_balance
  daily_includes_floating: true
  daily_reset: null
  daily_reset_null_reason: NON_TROVATO
  max_loss_pct: 8
  max_loss_type: static
  trailing_lock: null
  trailing_lock_null_reason: NON_APPLICABILE
  consistency_pct: null
  consistency_null_reason: DA_VERIFICARE
  phases:
    - {name: fase1, target_pct: 8, min_days: 5, max_days: null}
    - {name: fase2, target_pct: 4, min_days: 5, max_days: null}
  funded:
    split_pct: null
    split_pct_null_reason: DA_VERIFICARE
    payout_every: null
    first_payout_days: null
    refund_fee: null
    accumulo_libero: null
  overnight_weekend: null
  overnight_weekend_null_reason: NON_TROVATO
  news:
    challenge: allowed
    funded: "40% reward-share rule applies to correlated high-impact news profits"
  ea:
    below_50000: allowed_with_fee
    50000_and_above: prohibited
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  italy: true


## The5ers ##
Correzione del prezzo da 149 USD
Il valore 149 USD per il conto da 100k non è verificato come prezzo ordinario ufficiale del programma High Stakes. Deriva da una pagina promozionale “Summer Plan” che riportava:

“$149, on the 2-Step 10/5 tier.”

Quindi deve essere classificato così:

text
the5ers_149_price:
  value: 149
  status: PROMOZIONE_UFFICIALE
  valid_as_regular_price: false
  reason: "La fonte è una pagina promozionale, non la pagina tariffaria ordinaria del programma."
Nel report finale, per la fee standard di The5ers, il valore corretto è:

text
fee: null
fee_null_reason: NON_VERIFICATO_PREZZO_ORDINARIO
Non bisogna riportare 149 come prezzo generale del 100k.

The5ers High Stakes
| Campo             | 10k                                                | 25k        | 50k        | 100k       | Frase ufficiale                                                                  | URL                  | Data       |
| ----------------- | -------------------------------------------------- | ---------- | ---------- | ---------- | -------------------------------------------------------------------------------- | -------------------- | ---------- |
| Fase 1            | 8% o 10% secondo piano                             | Uguale     | Uguale     | Uguale     | La pagina mostra tier differenti 8/5 e 10/5                                      | High Stakes          | 06/10/2026 |
| Fase 2            | 5%                                                 | 5%         | 5%         | 5%         | “2-Step 10/5”                                                                    | Summer Plan          | 06/10/2026 |
| Daily loss        | 5%                                                 | 5%         | 5%         | 5%         | “Daily Loss 5%”                                                                  | High Stakes          | 06/10/2026 |
| Base percentuale  | Non separata chiaramente nel testo consultato      | Uguale     | Uguale     | Uguale     | NON PUBBLICATO                                                                   | High Stakes Help     | 06/10/2026 |
| Livello misura    | Non separato chiaramente                           | Uguale     | Uguale     | Uguale     | NON PUBBLICATO                                                                   | —                    | 06/10/2026 |
| P&L flottante     | Non verificato nel testo consultato                | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | —                    | 06/10/2026 |
| Maximum loss      | 10% secondo piano 10/5                             | 10%        | 10%        | 10%        | “wider 10% loss limit”                                                           | Summer Plan          | 06/10/2026 |
| Tipo maximum loss | Statico secondo piano documentato                  | Uguale     | Uguale     | Uguale     | “10% Static Maximum” in riepilogo ufficiale/secondario da verificare             | High Stakes          | 06/10/2026 |
| Overnight/weekend | Consentiti                                         | Consentiti | Consentiti | Consentiti | “Overnight and weekend actions are allowed”                                      | High Stakes          | 06/10/2026 |
| News              | Restrizioni High Stakes; automazione del controllo | Uguale     | Uguale     | Uguale     | “News Trading Automation High Stakes … trading doesn't occur around these hours” | Technology migration | 06/10/2026 |
| Finestra news     | Non recuperata nel testo consultato                | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | Technology migration | 06/10/2026 |
| EA MT5            | Non verificato per High Stakes                     | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | —                    | 06/10/2026 |
| Codice .mq5       | Non verificato                                     | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | —                    | 06/10/2026 |
| Leva generale     | 1:100                                              | 1:100      | 1:100      | 1:100      | “leverage is set to 1:100”                                                       | High Stakes leverage | 06/10/2026 |
| Leva XAUUSD       | Non separata per simbolo                           | Uguale     | Uguale     | Uguale     | NON PUBBLICATO                                                                   | High Stakes leverage | 06/10/2026 |
| Leva NAS100       | Non separata per simbolo                           | Uguale     | Uguale     | Uguale     | NON PUBBLICATO                                                                   | High Stakes leverage | 06/10/2026 |
| Profit split      | 80%, scalabile fino a 100%                         | Uguale     | Uguale     | Uguale     | “start with an 80% profit split … scale … to 100%”                               | Profit split Help    | 06/10/2026 |
| Primo payout      | 14 giorni dopo il funding                          | Uguale     | Uguale     | Uguale     | “payouts are available 14 days after funding”                                    | The5ers payout page  | 06/10/2026 |
| Frequenza payout  | Ogni due settimane                                 | Uguale     | Uguale     | Uguale     | “every two weeks thereafter”                                                     | The5ers payout page  | 06/10/2026 |
| Consistency       | 50% nel funded 2-Step secondo piano promozionale   | Uguale     | Uguale     | Uguale     | “50% consistency rule switches on once you are funded”                           | Summer Plan          | 06/10/2026 |
| MT5               | Sì                                                 | Sì         | Sì         | Sì         | “We use the MT5 platform from MetaQuotes”                                        | The5ers platform     | 06/10/2026 |
| Broker/server     | Non pubblicato nel testo consultato                | Uguale     | Uguale     | Uguale     | NON PUBBLICATO                                                                   | —                    | 06/10/2026 |
| Italia            | Non trovata pagina esplicita che nomini l’Italia   | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | —                    | 06/10/2026 |
| ESMA/MiFID II     | Non trovata dichiarazione specifica                | Uguale     | Uguale     | Uguale     | NON TROVATO                                                                      | —                    | 06/10/2026 |
| Fee standard 100k | NON VERIFICATA; 149 era promozione                 | —          | —          | —          | “$149, on the 2-Step 10/5 tier” = promo, non tariffa generale                    | Summer Plan          | 06/10/2026 |


| Campo               | Valore                         | Frase ufficiale                                                                       | URL                   | Data       |
| ------------------- | ------------------------------ | ------------------------------------------------------------------------------------- | --------------------- | ---------- |
| Struttura           | Instant funding / pro stages   | “The profit target, maximum loss, and daily pause remain the same for the pro stages” | Hyper Growth          | 06/10/2026 |
| Leva Forex          | 1:30                           | “Forex pairs- 1:30”                                                                   | Hyper Growth leverage | 06/10/2026 |
| Leva metalli/XAUUSD | 1:10                           | “Metals- 1:10”                                                                        | Hyper Growth leverage | 06/10/2026 |
| Leva indici/NAS100  | 1:7,5                          | “Indices- 1:7.5”                                                                      | Hyper Growth leverage | 06/10/2026 |
| Daily loss          | Non verificato per ogni taglia | NON TROVATO nella pagina completa consultata                                          | Hyper Growth          | 06/10/2026 |
| Maximum loss        | Non verificato per ogni taglia | NON TROVATO                                                                           | Hyper Growth          | 06/10/2026 |
| EA                  | Non verificato                 | NON TROVATO                                                                           | —                     | 06/10/2026 |
| News                | Non verificato                 | NON TROVATO                                                                           | —                     | 06/10/2026 |
| Fee 100k            | Non verificata                 | NON TROVATO                                                                           | —                     | 06/10/2026 |

The5ers_High_Stakes:
  description: "High Stakes 2-Step; piani 8/5 e 10/5 documentati"
  account_sizes: [10000, 25000, 50000, 100000]
  fee: null
  fee_null_reason: NON_VERIFICATO_PREZZO_ORDINARIO
  promotional_fee_100k: 149
  promotional_fee_status: "official_promotion_only"
  daily_loss_pct: 5
  daily_loss_base: null
  daily_loss_base_null_reason: NON_PUBBLICATO
  daily_loss_measurement_level: null
  daily_loss_measurement_level_null_reason: NON_PUBBLICATO
  daily_includes_floating: null
  daily_includes_floating_null_reason: NON_TROVATO
  max_loss_pct: 10
  max_loss_type: static
  trailing_lock: null
  trailing_lock_null_reason: NON_APPLICABILE
  consistency_pct: 50
  consistency_window: other
  consistency_window_note: "La pagina promozionale indica attivazione nel funded; il periodo esatto non è specificato."
  phases:
    - {name: fase1, target_pct: null, target_options: [8, 10], min_days: null, max_days: null}
    - {name: fase2, target_pct: 5, min_days: null, max_days: null}
  funded:
    split_pct: 80
    split_max_pct: 100
    payout_every: "every two weeks"
    first_payout_days: 14
    refund_fee: null
    refund_fee_null_reason: NON_TROVATO
    accumulo_libero: null
    accumulo_libero_null_reason: NON_TROVATO
  overnight_weekend: true
  news: restricted
  news_window_minutes: null
  news_window_null_reason: NON_TROVATO
  ea_mt5: null
  ea_mt5_null_reason: NON_TROVATO
  source_code_required: null
  source_code_null_reason: NON_TROVATO
  leverage_general: 100
  leverage_xauusd: null
  leverage_xauusd_null_reason: NON_PUBBLICATO
  leverage_nas100: null
  leverage_nas100_null_reason: NON_PUBBLICATO
  platforms: [MT5]
  broker_server: null
  broker_server_null_reason: NON_PUBBLICATO
  italy: null
  italy_null_reason: NON_TROVATO
  esma_mifid_statement: null
  esma_mifid_null_reason: NON_TROVATO

  The5ers_Hyper_Growth:
  description: "Hyper Growth instant/pro program"
  account_sizes: null
  account_sizes_null_reason: NON_TROVATO
  fee: null
  fee_null_reason: NON_TROVATO
  daily_loss_pct: null
  daily_loss_pct_null_reason: DA_VERIFICARE
  max_loss_pct: null
  max_loss_pct_null_reason: DA_VERIFICARE
  max_loss_type: null
  max_loss_type_null_reason: DA_VERIFICARE
  phases: []
  funded:
    split_pct: null
    split_pct_null_reason: DA_VERIFICARE
    payout_every: null
    first_payout_days: null
    refund_fee: null
    accumulo_libero: null
  overnight_weekend: null
  overnight_weekend_null_reason: NON_TROVATO
  news: null
  news_null_reason: NON_TROVATO
  ea_mt5: null
  ea_mt5_null_reason: NON_TROVATO
  leverage_xauusd: 10
  leverage_nas100: 7.5
  leverage_note: "The5ers publishes asset-group leverage: metals 1:10, indices 1:7.5."
  platforms: [MT5]
  italy: null
  italy_null_reason: NON_TROVATO


Tabella comparativa 10k, 25k, 50k, 100k
FTMO 2-Step
Account	Fase 1	Fase 2	Daily loss	Maximum loss
10k	1.000	500	500	1.000
25k	2.500	1.250	1.250	2.500
50k	5.000	2.500	2.500	5.000
100k	10.000	5.000	5.000	10.000
Percentuali ufficiali: 10%, 5%, daily loss 5%, maximum loss 10%.

FTMO 1-Step
Account	Target	Daily loss	Maximum loss
10k	1.000	300	1.000
25k	2.500	750	2.500
50k	5.000	1.500	5.000
100k	10.000	3.000	10.000
Target e daily loss provengono dalla pagina ufficiale 1-Step; il maximum loss è trailing EOD.

FundedNext Stellar 2-Step
Account	Fase 1 8%	Fase 2 5%	Daily loss 5%	Maximum loss 10%
10k	800	500	500	1.000
25k	2.000	1.250	1.250	2.500
50k	4.000	2.500	2.500	5.000
100k	8.000	5.000	5.000	10.000

FundedNext Stellar 1-Step
Account	Daily loss 3%	Maximum loss 6%
10k	300	600
25k	750	1.500
50k	1.500	3.000
100k	3.000	6.000

FundedNext Stellar Lite
Account	Fase 1 8%	Fase 2 4%	Daily loss 4%	Maximum loss 8%
10k	800	400	400	800
25k	2.000	1.000	1.000	2.000
50k	4.000	2.000	2.000	4.000
100k	8.000	4.000	4.000	8.000

The5ers High Stakes
Per The5ers il calcolo monetario seguente è valido solo come conversione delle percentuali pubblicate, non come conferma che ciascuna taglia abbia lo stesso piano tariffario:

Account	Piano 10/5 fase 1	Fase 2	Daily loss 5%	Maximum loss 10%
10k	1.000	500	500	1.000
25k	2.500	1.250	1.250	2.500
50k	5.000	2.500	2.500	5.000
100k	10.000	5.000	5.000	10.000
Fonte percentuale: piano ufficiale High Stakes 10/5 e daily loss 5%.

Differenze rilevanti per taglia
| Aspetto                     | 10k                                           | 25k                           | 50k                          | 100k                    |
| --------------------------- | --------------------------------------------- | ----------------------------- | ---------------------------- | ----------------------- |
| FTMO percentuali            | Uguali                                        | Uguali                        | Uguali                       | Uguali                  |
| FundedNext percentuali      | Dipendono dal programma                       | Dipendono dal programma       | Dipendono dal programma      | Dipendono dal programma |
| FundedNext EA MT5           | Possibile con fee se previsto                 | Possibile con fee se previsto | Vietato nei programmi citati | Vietato                 |
| News FundedNext             | Challenge consentita; funded 40% profit share | Uguale                        | Uguale                       | Uguale                  |
| The5ers leva High Stakes    | 1:100 programma                               | 1:100                         | 1:100                        | 1:100                   |
| The5ers Hyper Growth XAUUSD | 1:10                                          | 1:10                          | 1:10                         | 1:10                    |
| The5ers Hyper Growth NAS100 | 1:7,5                                         | 1:7,5                         | 1:7,5                        | 1:7,5                   |
| Payout monetario            | Più piccolo                                   | Più piccolo                   | Medio                        | Più grande              |
| Prezzo challenge            | Da verificare ufficialmente                   | Da verificare                 | Da verificare                | Da verificare           |

La soglia FundedNext più importante è quella di 50.000 USD: sotto 50k gli EA MT4/MT5 possono essere ammessi con costo aggiuntivo; da 50k in su il trading deve essere manuale.

Correzioni rispetto al report precedente
Daily loss FundedNext: non basta initial; ora è distinto tra:

base percentuale = saldo iniziale;

livello di misura = saldo iniziale meno il limite;

P&L flottante = incluso.

The5ers 149 USD: rimosso come prezzo standard; mantenuto solo come promozione ufficiale documentata.

EA FundedNext: corretto per dimensione:

sotto 50k: possibile su MT4/MT5;

50k e oltre: vietato.

News FundedNext: aggiunto:

5 minuti prima e dopo;

40% del profitto conteggiato;

perdite interamente a carico del trader;

regola sui funded account, non sulla challenge.

Broker: FTMO e FundedNext non si presentano come broker retail tradizionali; operano con infrastruttura simulata e liquidity provider.

Italia: FTMO e FundedNext non riportano l’Italia tra i paesi vietati nelle liste consultate; per The5ers non è stata trovata una conferma esplicita.

Null: ogni valore ora riporta una motivazione: NON_TROVATO, NON_PUBBLICATO, NON_APPLICABILE, DA_VERIFICARE oppure NON_VERIFICATO_PREZZO_ORDINARIO.
