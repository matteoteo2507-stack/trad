---
tipo: analisi
stato: "smistate all'intake, 0 trial; nessuna famiglia aperta o chiusa; priorita' fra i candidati da fissare (Matteo); aggiornata la sera del 25/10 (World Monitor, perimetro)"
aggiornato: 2026-10-25
fonte: "fondamenti_tecnici/_sorgenti/appunti_matteo_hub_2026-10-24/ (appunti di Matteo dall'inbox dell'hub del 24/10, con il controllo preliminare scritto dall'hub il 25/10)"
misure: "nessuna: ogni voce e' confrontata con DECISIONS.md, _INTAKE.md, BACKLOG_RICERCA.md e i moduli, letti il 25/10"
---
# Idee di Matteo dall'inbox dell'hub (24/10): smistamento

> Arrivate in `Da distillare/` il 25/10 dall'hub (`../CLAUDE.md`, "Lavorare su `trad` dall'hub"), con un controllo
> preliminare scritto dall'hub. Quel controllo e' un indizio, non un verdetto: qui ogni voce e' ricontrollata contro
> il repo. **0 trial**, nessuna variante provata, nessun dato toccato. **Le priorita' fra i candidati le fissa Matteo**;
> questa nota porta lo stato e le obiezioni.

## 1. Tre correzioni al controllo dell'hub

1. **Voce 3, "restano nuove le chiusure".** Non e' cosi'. La chiusura della seduta USA e' stata testata: H1, momentum
   dell'ultima mezz'ora, **CLOSED il 12/10** al train (DECISIONS 2026-10-12 (2)), e quella voce dice che *"non la
   riaprono un'altra finestra, il segnale della prima mezz'ora o un filtro di volatilita' sugli stessi indici"*.
   Mancavano anche l'apertura di Londra (London Breakout, **NO-GO** il 2026-05-30) e l'oro notturno (Blose et al.,
   **chiuso all'intake** il 03/10, meccanismo legato all'apertura; riga in `_INTAKE.md`).
2. **Voce 2, insider "testabile perche' i Form 4 sono gratuiti".** I Form 4 sono solo meta' del test: servono i prezzi
   delle **azioni singole USA senza survivorship**, che non abbiamo (BACKLOG §G, riga G6: Norgate 630 $/anno, letto il
   29/09; non comprato). E le azioni singole sono **fuori perimetro** per la tabella "chiuse in partenza" del BACKLOG §H.
   In piu' il repo ha gia' un blueprint con un agente sui Form 4 (`fondamenti_tecnici/blueprints/insider_constellation.md`,
   idea non committata; classificata il 03/10 in [ricerca_repo](ricerca_repo_2026-10-03.md) §3 come "equity USA +
   segnali da agenti").
3. **Voce 10, il quadrante di liquidita'.** Non e' nuovo: e' il **"framework Fed (defiantmentor)"** gia' distillato in
   [03_regimi_macro](../../fondamenti_tecnici/03_regimi_macro/principles.md) §2 e
   [06_stock_selection](../../fondamenti_tecnici/06_stock_selection/principles.md) §2. La tabella degli archetipi A-D
   dell'immagine coincide cella per cella (crescita dei ricavi 5/10/20/>50%, P/E 10/20/25x, debito/EBITDA 1/3/5x).
   Che il video sia della stessa fonte e' **dedotto** da questa coincidenza, non verificato: in ogni caso conta come
   **una** occorrenza, non come conferma ([[feedback_conferme_per_fonte]]). Unica differenza: l'immagine dice
   "Investment portion: 100%" nel quadrante A, i moduli "fino a 100%+ (leva)".

## 2. Voce per voce

| # | Idea (sintesi) | Cosa dice gia' il repo | Stato | Cosa servirebbe per andare avanti |
|---|---|---|---|---|
| 1 | Workspace quant "tipo Bloomberg": skill e agenti | — (infrastruttura) | **rinviata** per decisione di Matteo (25/10: fuori da questa sessione) | torna nella sezione `trad` della pending dell'hub, con la condizione "dopo la revisione delle voci `da_rivedere`" |
| 2a | Strategia su order flow (deepchart) | BACKLOG **D1**: servono tick + book, *"mai, realisticamente: il vantaggio e' di latenza"*; G7 | **bloccata** (D1). Che "deep chart.io" sia una piattaforma di grafici order flow e' una lettura di Claude, non verificata | nulla di nuovo: valgono le condizioni di D1 |
| 2b | Strategia sugli acquisti degli insider | correzione 2 sopra. Classe **3** del [modulo 09](../../fondamenti_tecnici/09_fonti_di_vantaggio/principles.md), reazione lenta al deposito: chi segue i Form 4 compra un'informazione gia' pubblica; la 4 e' dell'insider (correzione del gatekeeper, 25/10). Il segnale e' noto all'accettazione del deposito su EDGAR, non alla data della transazione. Letteratura nota a Claude (Lakonishok-Lee 2001; Cohen, Malloy, Pomorski 2012): **non letta, quarantena** | **quarantena, parcheggiata** (stessa condizione di D3, PEAD): nuova riga **D9** del backlog. Il perimetro si e' allargato all'azionario la sera stessa (DECISIONS 2026-10-25 (3)): resta bloccata dai dati | dati G6 + uno strumento per eseguire su azioni singole |
| 3 | Pattern all'apertura e alla chiusura delle sessioni, 15 anni, piu' asset | correzione 1 sopra; ORB **CLOSED** (F1, 27/08); stagionalita' TOM **NO-GO** (08/07) | **respinta nella forma attuale.** Cercare "se si trovano pattern" su asset × sessioni × finestre e' una ricerca per elenco: il modulo 09 chiede prima la classe e chi paga ([[feedback_prima_la_classe_poi_i_candidati]]), e ogni cella guardata e' un tentativo ([[feedback_mass_search_vs_preregistration]]) | un'ipotesi con classe e chi paga su un asset e una finestra mai usati. Attenzione: DAX, Euro Stoxx 50 e FTSE 100 in casa sono **sigillati** come holdout di H1, usarli e' una riapertura (DECISIONS 2026-10-12 (2)) |
| 4 | Strategia "sempre accesa" o accesa solo in certi periodi? | la risposta c'e': principio "Edge condizionato alla strategia" (DECISIONS, principi trasversali); una condizione di regime si testa **per ablazione pre-registrata** (LIFECYCLE §4bis) e si sceglie positiva ovunque (§4ter); i casi negativi: London Breakout (regime calcolato sullo stesso giorno = look-ahead) e il 2022 di H1 (*"un filtro di regime scelto adesso sarebbe scelto sull'esito"*); il caso aperto: il playground di A1 (`trend_momentum`, regime di volatilita', LEAD) | **gia' risposta**: on/off e' lecito se il regime e' definito **prima**, con dati disponibili al momento (ritardo di un giorno, [[reference_regime_timeline_lookahead]]) e testato con e senza | nessun lavoro nuovo. Se Matteo vuole una lettura, i punti sono quelli a sinistra |
| 5 | Divergenze fra coppie correlate | metodo gia' distillato (cointegrazione: [04_quant_metodologia](../../fondamenti_tecnici/04_quant_metodologia/principles.md) §11, buco 21); **mai testata** come strategia | **quarantena, candidato** | (a) griglia del modulo 09: classe (2-3, chi chiede liquidita' paga chi la fornisce?) e perche' il premio non e' gia' arbitrato, visto che la letteratura citata dall'hub (Gatev et al. 2006) lo da' in calo; (b) **famiglia**: lo spread fra due strumenti e' "spostamento dalla media" (regola 08/10) su un oggetto nuovo: famiglia nuova o parente di `mr_indici_rsi2`? Si decide alla G1 col gatekeeper; (c) se poggia su un risultato pubblicato e' una pre-registrazione **esterna**, e la quota del 2026-Q4 e' piena (3 di 2-3, `python -m core.trial_ledger`, 25/10) |
| 6 | Sfruttare le news con le previsioni ("world monitor") | il calendario macro e' *"il posto piu' pubblico e piu' affollato del mercato"* (DECISIONS 2026-08-22, porta D6); il filtro news peggiorava l'ORB (2026-07-16); le prop limitano il trading sulle news | **rimandata all'hub.** *World Monitor* (chiarito da Matteo il 25/10; era **gia' nel repo**: `data/README.md` lo prevedeva come sorgente "Stage 5", un ponte che leggesse i segnali correnti per filtrare le strategie, mai costruito, e Matteo l'aveva proposto piu' volte; il controllo dell'hub e il mio primo passaggio, che hanno cercato solo in `DECISIONS.md` e `_INTAKE.md`, non l'avevano trovato; fork di `koala73/worldmonitor` fra le sue repo GitHub, README letto il 25/10) e' una dashboard in tempo reale di notizie, conflitti, infrastrutture e mercati. **Non ha uno storico datato da cui fare un backtest**: il "historical playback" sono istantanee salvate nel browser da quando la si apre. Serve come pannello d'informazione per il registro delle previsioni, e integra **Polymarket**, candidato a fare da riferimento del registro (scelta aperta nell'hub). Il suo "market radar" (verdetto BUY/CASH da 7 segnali: yen, BTC contro QQQ, QQQ contro XLP, BTC sopra le medie, hashrate...) e' tendenza e regime, famiglie esistenti, senza nessuna misura pubblicata nel README: quarantena | in `trad` solo con la scheda d'ingresso ([STRATEGY_LIFECYCLE](../STRATEGY_LIFECYCLE.md) §8): serve una misura dal registro delle previsioni e, per un test sulle notizie, un archivio di notizie con data e ora |
| 7a | Azioni o ETF per cicli (cicliche) | stock picking cross-sezionale **falsificato** sull'S&P 500 (DECISIONS 2026-06-02, pivot Stock Selector → TAA; vedi la divergenza nel §4); pilastro investing = PAC passivo (DECISIONS 2026-08-07); market timing a 200 giorni **rifiutato** nel pilastro (riga "Lost Decades" di `_INTAKE.md`); orizzonte mensile fuori perimetro fino al 25/10 (BACKLOG §H; allargato all'azionario, DECISIONS 2026-10-25 (3)) | **quarantena, parcheggiata**: nessuna classe o chi paga dichiarati; pochi cicli osservabili | una classe e chi paga, e una decisione su dove vive: trading (`trad`) o studio macro (hub, "niente filosofia dentro `trad`") |
| 7b | Identificare le bolle | Quant Guild C10 (distillato il 17/09, `_triage/quantguild/blocco-C.md`): "bolla" e' un'etichetta a posteriori; il segnale non dice **quando**, quindi da solo non e' tradabile. BACKLOG H5: la tendenza si romperebbe agli estremi di valutazione (*Boundaries of TSMOM*, da acquisire), servono dati di valutazione → D | **parcheggiata**: lo studio storico delle bolle va nei domini dell'hub; in `trad` entra solo con una misura | un'ipotesi con una misura e un orizzonte (es. probabilita' di crollo dopo un rialzo estremo), dati di valutazione |
| 8 | Insider pesati con la mappa geopolitica | primo caso del ponte con l'hub | **bloccata**: dalla 2b (dati) e dal registro delle previsioni (fase 1 non partita) | **Prova della scheda d'ingresso** ([STRATEGY_LIFECYCLE](../STRATEGY_LIFECYCLE.md) §8, gatekeeper, 25/10): si ferma a **P5** (nessuna misura: il registro delle previsioni non ha ancora ne' riferimento ne' domande) e, per l'insider, alla **domanda 6** (accessibilita'). Esito: componente geopolitica **rimandata all'hub**, insider **parcheggiato** (D9). Anche quando le due condizioni cadranno, manca la domanda 2: nessuno ha scritto perche' il contesto geopolitico cambierebbe il contenuto di un acquisto, ne' chi paga l'interazione. Il test sarebbe un'ablazione: due trial |
| 9 | ADD (avanzanti − declinanti NYSE), "TREND Q", TMO, EMA, SAR | regola **stessa grandezza = stessa famiglia** (DECISIONS 2026-10-08 (3)): medie mobili e SAR sono `trend_momentum` (LEAD, round 3 conteso); TMO e' un oscillatore di momentum, quindi tendenza o spostamento dalla media, comunque una famiglia esistente | EMA, SAR, TMO: **chiuse in partenza** come famiglie nuove. TREND Q: **non falsificabile** finche' la formula non e' nota (indicatore proprietario). ADD: **quarantena** | ADD non e' fra le sei grandezze: e' una misura di partecipazione del mercato. Usata su un indice e' un filtro, quindi si testa per ablazione su una regola esistente (LIFECYCLE §4bis), non come strategia. Serve la serie storica NYSE (non in casa) e una regola a cui attaccarla |
| 10 | Quadrante di liquidita' (bilancio della banca centrale × tassi) | correzione 3 sopra; `docs/INVESTMENT_ALGO_DESIGN.md` §1: la liquidita' della Fed *"imposta il contesto, non e' un trigger preciso"*, da usare come contesto e scala del rischio | **gia' distillato**; nessun lavoro nuovo. La versione su azioni singole richiede fondamentali point-in-time (G6, non comprati); quella sull'esposizione all'indice ha pochi cambi di regime dal 2008 (obiezione dell'hub, corretta) ed e' market timing, gia' rifiutato nel pilastro investing | evidenza esterna con un campione; nel caso dell'investing, una decisione di Matteo che cambi il PAC passivo |

## 3. Cosa resta, per le priorita' di Matteo

- **Unico candidato che potrebbe arrivare a una G1 senza dati nuovi:** voce 5 (coppie). Costo: un trial e, se poggia sulla
  letteratura, uno slot esterno, libero non prima del 2027-Q1.
- **Bloccate dai dati** (il perimetro si e' allargato all'azionario, globale, la sera del 25/10: DECISIONS 2026-10-25 (3)): voci 2b e 8, insieme a D2 e D3.
- **Rimandata all'hub:** voce 6 (World Monitor e' una fonte d'informazione per il registro delle previsioni, non un dato storico).
- **Rinviate:** voce 1.
- Il resto e' gia' risposto o chiuso dalle regole esistenti.

## 4. Obiezioni

- **"Pattern da sfruttare" (voce 3) e "una strategia on/off" (voce 4)** sono le due forme in cui il repo ha gia' perso
  piu' tempo: la ricerca livelli (384 trial) e il regime gating del London Breakout. Non c'e' nulla di sbagliato nella
  domanda; e' la forma "cerchiamo e vediamo" che non regge.
- **Il quadrante (voce 10)** e' arrivato due volte da due video ed era gia' nei moduli: un'idea che sembra confermata
  perche' ricompare e' un caso di [[feedback_conferme_per_fonte]], non una prova.
- **Le voci 2b, 7 e 10** riguardano azioni singole o orizzonti mensili. La domanda a monte era il perimetro: Matteo l'ha
  allargato all'azionario la sera stessa (DECISIONS 2026-10-25 (3)). Ora le ferma lo stesso motivo per tutte: i dati azionari.
- **Divergenza da decidere, non da mediare** (trovata dal gatekeeper il 25/10). DECISIONS 2026-06-02 dice che lo score
  fondamentale dello Stock Selector e' *"anti-predittivo"*; la review su cui poggia
  ([stock_selector-2026-06-01](stock_selector-2026-06-01.md), "Implicazioni riviste per il codice", punto 3) dice che *"resta non validato
  (serve PIT DB per testarlo onestamente)"*. Per la regola del repo vale la voce piu' recente, cioe' DECISIONS; ma la
  differenza tocca ogni idea su azioni singole (voci 2b, 7a, 8, 10), quindi la segnalo a Matteo invece di sceglierne una.
