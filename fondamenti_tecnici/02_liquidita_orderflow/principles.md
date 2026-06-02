---
titolo: Liquidità & Order Flow (Smart Money Concepts)
fonti: ["HOW TO MASTER LIQUIDITY - Soulz", "What Is Liquidity - CryptoSoulz", "THE ORDERFLOW - CryptoSoulz", "The Liquidity Edge"]
tipo: concetti
---

# Liquidità & Order Flow (Smart Money Concepts)

> Distillato della letteratura Smart Money Concepts (Soulz/CryptoSoulz) su dove si forma la liquidità, come gli istituzionali la cacciano e come leggerla con strumenti di order flow — base concettuale per le strategie di confluenza del repo.

## Concetti

### 1) Liquidità & struttura

**La regola d'oro: il prezzo si muove da liquidità a liquidità.**
Il prezzo non si muove a caso né per gli indicatori: si muove per *accedere alla liquidità*. La liquidità è il "carburante" del movimento. È il singolo concetto su cui ruota tutto il resto.

**Cos'è la liquidità.** Liquidità = ordini in attesa di essere riempiti. In pratica sono soprattutto **stop loss** che si addensano in posti prevedibili, perché i retail piazzano gli stop in modo prevedibile:
- oltre swing high/low (stop dei trader breakout e di chi è in posizione);
- ai numeri tondi psicologici (100.00, 1.2000);
- ai massimi/minimi temporali (giorno/settimana/mese precedente);
- agli equal highs/lows;
- dentro i range di consolidamento.

**Perché gli istituzionali ne hanno bisogno.** Chi deve comprare 10.000 contratti non può "market buy" (sposterebbe il prezzo e verrebbe front-runnato). Usa algoritmi per accumulare lentamente e **spinge il prezzo verso i cluster di stop** per crearsi la controparte: gli stop scattati diventano ordini a mercato che riempiono la sua posizione, poi il prezzo inverte. Da qui falsi breakout, stop hunt "ingiusti", livelli rispettati più volte, esplosioni dopo consolidamento.

**Players.** Retail (conti piccoli, pattern/indicatori, stop prevedibili → *forniscono* liquidità); istituzionali / smart money (banche, fondi, market maker — manipolano per accedere agli stop); whale / big players (exchange, fondi, banche centrali — creano i trend).

**BSL / SSL.**
| | Definizione | Cosa la crea | Quando viene cacciata |
|---|---|---|---|
| **BSL** (Buy-Side Liquidity) | Liquidità *sopra* il prezzo | Buy stop sopra gli swing high, stop degli short, breakout buyer | L'istituzione che vuole *vendere* spinge il prezzo SU per scattare questi buy stop |
| **SSL** (Sell-Side Liquidity) | Liquidità *sotto* il prezzo | Sell stop sotto gli swing low, stop dei long, breakout seller | L'istituzione che vuole *comprare* spinge il prezzo GIÙ per scattare questi sell stop |

**Liquidità interna vs esterna (+ priority rule).**
- **Interna**: dentro il range / tra swing strutturali; si forma in correzione; obiettivo intermedio, usata per aggiungere a posizione. *Priorità minore.*
- **Esterna**: oltre gli swing point, fuori dal range, ai livelli ovvi di breakout; magnete più forte.
- **Priority rule: External > Internal.** Se esistono entrambe, il prezzo cerca prima l'esterna (l'interna può venire presa lungo il cammino).

**Pool temporali.** PDH/PDL (prev. day, target intraday più comuni), PWH/PWL (prev. week, swing), PMH/PML (prev. month, livelli istituzionali/posizionali). Magneti per il prezzo.

**Equal Highs / Equal Lows (EQH/EQL).** 2–3+ swing allo stesso livello (entro pochi pip) → pool di liquidità "impilata". Si tradano in due modi: *fade* dopo lo sweep (entra in direzione opposta) o come *target* di un altro setup. I più potenti: gli sweep su EQH/EQL danno reversal esplosivi.

**Compression.** Sequenza di highs/lows che si stringe tra punti strutturali senza breakout; costruisce liquidità *su entrambi i lati* (molla caricata) → rottura accelerata. Durante: stai fuori o trada boundary-to-boundary; dopo la rottura: entra in direzione del break verso la liquidità opposta.

**Liquidity sweep / grab / raid** (sinonimi). Anatomia: (1) **Approach** — il prezzo si avvicina al livello; (2) **Sweep** — rompe brevemente (1–3 candele, spesso con wick) e scattano gli stop; (3) **Reversal** — inversione immediata con follow-through. Caratteristiche: rapido, netto, wick non body, inversione immediata senza consolidare oltre il livello. **Non è un breakout fallito: è manipolazione intenzionale.** Regola: la liquidità *non* è un segnale d'ingresso da sola — è un *target* e va combinata con struttura + entry model.

**Deviation (range trading)** *(aggiunta di "What Is Liquidity")*. Movimento oltre un boundary di range fatto apposta per rimuovere la liquidità esterna prima di rientrare. Principio: "deviation su un lato porta a deviation sull'altro". Distinzione chiave:
| | **Weak deviation (tradeable)** | **Strong deviation (evita)** |
|---|---|---|
| Volume | basso sulla spinta fuori | alto sul breakout |
| Reazione | rigetto immediato dentro il range | consolida fuori dal range |
| Divergenza | presente | assente |
| Esito | ritorno rapido al midpoint | follow-through, nuovo range fuori |
Gestione tipica: chiudi 80% dentro il range, lascia 20% runner per la deviation opposta.

**Market structure: MSS vs BOS** *(distinzione netta in "The Liquidity Edge")*. Uptrend = HH+HL; downtrend = LH+LL.
- **MSS (Market Structure Shift) = cambio di trend.** Rottura di uno swing strutturale nella direzione *opposta* al trend (in uptrend: chiude sotto l'ultimo minimo significativo). Segnala potenziale inversione.
- **BOS (Break of Structure) = continuazione.** Rottura di uno swing nella *stessa* direzione del trend (in uptrend: rompe i massimi recenti). Conferma che il trend è sano.
- Nota terminologica: il PDF base "Master Liquidity" usa "BOS" sui timeframe alti per il cambio trend e "Shift" sui timeframe bassi come segnale anticipato — *stesso concetto, etichette diverse*. In questa KB usiamo MSS=cambio trend, BOS=continuazione (convenzione "The Liquidity Edge"). Dopo un BOS serve **confirmation** (rottura dello swing della nuova struttura post-break) per ridurre i falsi segnali.

**Swing high/low — regola delle 3 candele.** Swing high = la candela centrale ha high più alto delle due adiacenti; swing low = low più basso delle due adiacenti. **Strong swing** (punti strutturali chiave: in uptrend i minimi, in downtrend i massimi — la loro rottura segnala cambio trend) vs **weak swing** (pivot minori dentro le correzioni, rumore).

**Fractality.** Gli stessi pattern si ripetono su tutti i timeframe: uno swing daily è fatto di tanti swing su 1H; un OB 4H può essere un intero range 15M. Si identifica la struttura su TF alto (D/4H) e si entra su TF basso (1H/15M). Vale per OB, FVG, order flow (vedi "nested").

**Premium / Discount (midpoint Fib 0.5).** Ogni range ha 3 zone: **Premium** (sopra 0.5, "caro", zona di distribuzione/vendita), **Discount** (sotto 0.5, "economico", zona di accumulo/acquisto), **Equilibrium** (0.5, fair value). Regola d'oro: *compra in Discount, vendi in Premium*. OTE (Optimal Trade Entry) = zona 0.62–0.79 (con midpoint 0.705) dove la smart money spesso entra dopo aver spazzato gli stop oltre 0.618–0.786. Nota: il **0.5 come midpoint** serve anche a validare un range (buon range = reazione netta al 0.5; range scadente = lo attraversa senza reagire → da scartare).

**Power of Three (PO3 / AMD)** *(esplicito in "Master the Art of Trading" cap. PO3; nel PDF liquidità è il ciclo MMXM)*. Tre fasi: **Accumulation** (laterale, le mani forti costruiscono posizione), **Manipulation** (spinta brusca fuori dal range per scattare stop/breakout falsi → fornisce liquidità), **Distribution** (vero movimento direzionale, i retail in trappola). È la versione "candela/range singolo" dello stesso ciclo dei **Market Maker Models** (vedi sotto).

**Market Maker Models (MMXM) & POI.** Ciclo completo di accumulo→markup→distribuzione→markdown→ritorno al consolidamento originale (MMBM = buy model, MMSM = sell model). Il punto d'ingresso a più alta probabilità è lo **SMR (Smart Money Reversal)**: sweep di liquidità → candela forte di inversione (Shift) → FVG creato → ritorno a testare l'FVG = entry. **POI (Point of Interest)** = zona dove entri (allineata al trend, in zona Premium/Discount corretta, con confluenza); **FTA (First Trouble Area)** = zona dove esci/prendi profitto (contro-trend). Flusso: POI → FTA → next POI. Gerarchia di priorità dei POI (PD Array Matrix): liquidità interna < mitigazione < FVG < Order Block < Breaker < Rejection block < liquidità esterna.

### 2) Order Block / FVG / displacement

**Fair Value Gap (FVG) / imbalance.** Pattern a 3 candele in cui la candela centrale (impulso) crea un gap tra candela 1 e candela 3 — il mercato è andato troppo veloce lasciando ordini non riempiti (vuoto che attira il prezzo per "ribilanciare"). Bullish FVG: gap tra high candela 1 e low candela 3. Bearish FVG: gap tra low candela 1 e high candela 3.
- **Tipi di fill (rebalancing):** *wick/IOFED* (parziale, <50% — reazione spesso più forte, R:R migliore), *0.5 (50%)* (midpoint, il "sweet spot" più affidabile), *full fill* (riempito con i body → FVG "consumato", può diventare *inversion* FVG).
- **Priorità FVG:** alta se in direzione dell'impulso, in Discount (uptrend) / Premium (downtrend), allineato al TF alto, con confluenza (OB, liquidità), dopo un BOS.
- **IFVG (Inverse FVG):** rileva imbalance anche con leggero overlap — più segnali, qualità mediamente inferiore (uso più scalping). Lo standard FVG (nessun overlap) è preferito.
- **BPR (Balance Price Range):** zona di *overlap tra un FVG bullish e uno bearish* → zona di equilibrio/S-R ad alta probabilità di reazione.

**Volume Imbalance (VI)** *(aggiunta "The Liquidity Edge")*. A differenza dell'FVG (gap, candele NON si sovrappongono), il VI ha candele che *si sovrappongono* ma con relazione open/close che rivela assorbimento (volume assorbito senza riflesso sul prezzo). Più raro, "footprint" istituzionale più pulito. FVG = imbalance di *prezzo*; VI = imbalance di *volume/assorbimento*. Combinati allo stesso livello = setup ad altissima probabilità.

**Displacement** *(aggiunta "The Liquidity Edge")*. Candela con body insolitamente grande rispetto alla media e wick piccoli (regola del 36%: ogni wick < 36% del body) = presenza istituzionale, inizio di un impulso/leg. Ogni displacement crea o è il centro di un FVG; gli FVG più affidabili hanno un displacement al centro. Displacement che rompe struttura + sweep precedente = segnale forte di cambio direzione.

**Order Block (OB).** Zona dove i grandi hanno piazzato ordini limite assorbendo liquidità opposta, prima di un'accelerazione netta.
- **Bullish OB** = ultima/e candela ribassista prima di un forte movimento su; **Bearish OB** = ultima/e candela rialzista prima di un forte movimento giù.
- **Componente critica: absorption** — la/le candela successiva engulfa il body dell'OB. Senza absorption non è un OB (può servire 1–3 candele).
- **Dove si formano:** durante liquidity removal (sweep), durante rebalancing di un FVG, testando OB precedenti (struttura "nested").
- **Livelli chiave:** Open (entry più comune), **MT/Mean Threshold = 50%** (validazione: se il prezzo chiude col body oltre il 50% l'OB si indebolisce — i *wick* oltre il 50% non contano), Wick (stop loss / ultima difesa). Marcatura: body-only (stop più stretti) o wick-incluso (più conservativo).
- **Contesto Premium/Discount:** in uptrend tradi bullish OB in Discount; in downtrend bearish OB in Premium. Evita OB nella zona sbagliata.

**Breaker Block (BB).** OB che viene rotto e cambia polarità (la posizione dell'istituzione fallisce → esce a breakeven o inverte). Es. bullish breaker: un bearish OB viene rotto al rialzo (BOS) e diventa supporto. Potente sui cambi di struttura, alta probabilità al primo retest.

**Rejection Block (RB).** OB caratterizzato da wick lungo (non body) formato durante uno sweep di liquidità; la zona di reazione è il wick stesso (con MT al 50% *del wick*).

**NWOG / NDOG** *(aggiunta "The Liquidity Edge")*. Gap di sessione che tendono a essere riempiti (mean reversion). **NWOG** (New Week Opening Gap) = range tra chiusura venerdì e apertura lunedì (per swing/weekly, può servire giorni). **NDOG** (New Day Opening Gap) = range tra chiusura giorno prec. e apertura giorno corrente (per intraday, spesso riempito in giornata). Entry tipico al midline 50% del gap.

**Killzones.** Finestre orarie ad alta attività istituzionale (volume e liquidità massimi, spread minimi, dove avvengono sweep/stop hunt): **London Open** (~07:00–10:00 GMT), **New York** (~07:00–09:00 EST), **Asian** (range, costruisce liquidità per Londra), **London Close** (mean reversion, overlap con NY). Massima liquidità nell'overlap **London + New York** (~08:00–12:00 EST). Sono guide di *timing*, non garanzie; da combinare con struttura/liquidità/OB/FVG.

### 3) Order flow tools (order book, volume/market profile, heatmap)

> Questi strumenti mostrano cosa accade *adesso* (order flow, liquidità, struttura) invece di indicatori laggard. Vanno usati per *confermare* setup, mai da soli.

**Order book (bid/ask, spread, depth, walls, spoofing).** *(da "THE ORDERFLOW")*
- **Bid** = prezzo più alto che un compratore paga; **Ask** = prezzo più basso che un venditore accetta; **Spread** = differenza (stretto = alta liquidità; largo = bassa).
- **Market depth**: quantità di ordini per livello (deep = liquidità forte; shallow = mosse volatili). **Balance**: più bid impilati = domanda; più ask = offerta.
- **Order wall**: grande cluster di ordini a un prezzo (buy wall sotto = supporto; sell wall sopra = resistenza); agisce da magnete, ma l'esito dipende da domanda/offerta reale.
- **Real vs fake liquidity (spoofing):** *real* = ordini che restano all'arrivo del prezzo, con reazione visibile (volume dots/assorbimento); *fake/spoofing* = ordini grossi che spariscono prima dell'esecuzione (illusione di S/R). Segnale di spoofing: il livello "non viene mai eseguito" e si sposta. Uso: insight di breve termine, cambia in secondi.

**Volume dots / bubbles** *(da "What Is Liquidity" e "THE ORDERFLOW")*. **Verde = acquisti aggressivi** (lift the ask); **rosso = vendite aggressive** (hit the bid); dot/bubble grandi = volume/attività istituzionale.

**Absorption & exhaustion** *(da "What Is Liquidity")*.
- **Absorption:** ordini aggressivi colpiscono un livello con forte liquidità resting ma il prezzo *non* lo rompe (qualcuno "mangia" tutto). Es. forte pressione di vendita (dots rossi) ma il prezzo non scende = buy orders che assorbono → si trada in direzione dell'assorbimento.
- **Exhaustion:** la spinta aggressiva esaurisce momentum (dots più piccoli, prezzo che non segue). Es. tanti dots verdi ma il prezzo non sale = compratori senza fiato → si trada contro la direzione esausta.

**Volume Profile** (volume *per livello di prezzo*). *(NB: il repo ne tratta già l'uso operativo — vedi §7 di TRADING_PRINCIPLES)*
- **POC / VPOC** (Point of Control): livello con più volume; prezzo "più equo", S/R forte, magnete.
- **Naked VPOC**: VPOC mai ri-testato → target ad alta probabilità (il prezzo tende a tornarci).
- **VAH / VAL / Value Area**: la Value Area contiene ~70% del volume (delimitata da VAH e VAL); dentro = prezzo accettato, fuori = ricerca di nuovo valore.
- **HVN** (High Volume Node): prezzo accettato, magnete, S/R, prezzo lento. **LVN** (Low Volume Node): prezzo rifiutato, "vuoto" attraversato in fretta — non metterci target. Trading: da HVN a HVN attraverso LVN.

**Market Profile / TPO / Initial Balance.** Organizza i dati per *tempo* (non volume): TPO = Time Price Opportunity (un blocco/lettera per ogni intervallo di tempo, tradizionalmente 30 min, a ogni prezzo toccato). POC qui = livello dove si è passato *più tempo*. **Initial Balance (IB):** range della prima ora di trading (prime due brackets da 30 min) — fissa il tono della sessione; estensioni oltre l'IB (ogni estensione ≈ 50% del range IB) sono significative come target. Profilo *bilanciato* (campana, POC al centro) = equilibrio, breakout imminente; profilo *sbilanciato* = market in discovery, bias direzionale. Single prints (TPO isolati a metà profilo) = mosse impulsive, spesso ri-testate o diventano boundary.
*Caveat metodologico (da "What Is Liquidity"):* la Value Area NON è statistica pura — usa il POC/VPOC (la *moda*) come centro, non la media; la larghezza è configurabile (default ~70%); varia tra piattaforme e data feed. Trattala come guida, non come regola rigida.

**Liquidation heatmap** (tooling crypto/leva). *(da "THE ORDERFLOW")* Traccia dove i trader a leva verranno liquidati forzatamente — zone-magnete (la cascata di liquidazioni accelera il movimento). **Long liquidation zones** sotto il prezzo (cascata ribassista se colpite); **short liquidation zones** sopra (squeeze rialzista). Cluster brillanti = alta concentrazione. È in pratica una visualizzazione di "trader pain" → dove cercare i target; da abbinare a order flow/volume.

**DOM Levels / Heatmap (ATAS).** *(da "Master Liquidity")* Mostra l'order book (limit buy/sell per livello) sul grafico: buy wall (supporto), sell wall (resistenza), liquidity void (zone scure, prezzo veloce), spoofing (wall che appaiono e spariscono). Permette di vedere in real-time la "caccia alla liquidità" descritta in teoria (push attraverso una zona debole verso un wall grande, poi reverse).

**Footprint charts.** Vanno un livello più in profondità del Volume Profile: mostrano *come* il volume è stato eseguito *dentro* ogni candela (buy che colpiscono l'ask vs sell che colpiscono il bid) → chi aveva il controllo a quel prezzo. Volume Profile = *dove* c'era attività; Footprint = *chi* aveva controllo; Market Profile = *quanto tempo* (accettazione/rifiuto).

#### Strumenti di terze parti citati (TOOLING — non nostri)
- **SCF Indicator / Kiyotaka.ai** (autore @SoulzBTC su community TradingView; piattaforma kiyotaka.ai): SCF Order Book Imbalance Indicator (barre verde/rosso = pressione compratori/venditori), oltre a Volume Profile, Liquidation Heatmap, Market Profile.
- **Smart Liquidity Indicator** (SoulzBTC x TaQuant, ~$49.99): detection automatica di MSS/BOS, liquidità (cluster 3+ swing, larghezza zona = ATR/Margin), OB, FVG/IFVG/BPR, Volume Imbalance, Displacement (regola 36%), NWOG/NDOG, Killzones, sweep detection, Fibonacci auto. Parametri: *Length* (sensibilità swing, default 5), *Margin* (default 4).
- **ATAS** (piattaforma a pagamento): Market Profile & TPO, Cumulative Delta (divergenza price vs delta), Big Trades (whale), DOM Levels/Heatmap, Market Replay.
- Altri citati in "What Is Liquidity": Bookmap, Sierra Chart, NinjaTrader, Jigsaw, MarketDelta, MotiveWave (order flow/volume profile). Libri di riferimento: Dalton "Mind Over Markets" / "Markets in Profile", Anna Coulling "Volume Price Analysis".

## Regole operative

1. **Pensa "da liquidità a liquidità".** Identifica cosa è stato appena spazzato (Point A) e quale liquidità è il prossimo target (Point B); trada il movimento tra i due. External > Internal quando coesistono.
2. **La liquidità non è un entry da sola.** Serve struttura + entry model (FVG, OB, SMR) + confluenza. Lo sweep va seguito da reversal/Shift prima di entrare.
3. **Allinea i timeframe (top-down).** Bias/POI sul TF alto (D/4H), entry preciso sul TF basso (1H/15M). Mai contro il TF alto. La conferma "scende" dall'alto verso il basso.
4. **Premium/Discount come filtro:** compra in Discount, vendi in Premium; foca su OB/FVG nella zona corretta; OTE 0.62–0.79 come sweet spot.
5. **Valida l'OB col 50% (MT):** chiusura body oltre il 50% = OB indebolito → scartalo. Stessa logica del 0.5 per validare i range e i fill FVG.
6. **MSS = prepara reversal, BOS = trada continuazione su pullback.** Non tradare MSS "alla cieca" senza confluenza.
7. **Deviation:** trada solo quelle *deboli* (basso volume, rigetto immediato, divergenza); evita quelle *forti*. Chiudi ~80% dentro il range, 20% runner.
8. **Order flow tools = conferma, non strategia.** Distingui liquidità reale (resta, reagisce, esegue) da fake/spoofing (sparisce). Non tradare dentro wall pesanti senza contesto. Sui naked VPOC/HVN aspettati reazione; attraverso gli LVN aspettati velocità (no target lì).
9. **Timing con le killzone** (London Open, NY, overlap) per gli ingressi a rischio più alto; le killzone sono guide, non garanzie.
10. **Stacking di probabilità.** I setup migliori hanno confluenza multipla (es. sweep + MSS + OB + FVG, o FVG + VI allo stesso livello, o POI + naked VPOC + Fib 0.618). Nessun segnale singolo basta.

> Nota su evidenza: gran parte di questi concetti è **aneddotica/qualitativa** (educazione SMC retail, non studi peer-reviewed) — la narrazione "istituzionale" è un modello mentale utile, non una verità dimostrata. I livelli Fibonacci e premium/discount funzionano in larga parte per *self-fulfilling* (cfr. realismo in TRADING_PRINCIPLES §4). Triangola sempre con backtest + razionale prima di accendere capitale.

## Collegamenti
- Fondamenti correlati: [[01_price_action]], [[03_regimi_macro]]
- Implementazioni nel repo: ../../strategies/confluence_levels/ (confluenza POC), ../../strategies/confluence_auto/ (detection S/D + POC algoritmica)
- Riferimenti operativi: ../../TRADING_PRINCIPLES.md (§3 S/D freshness, §7 Volume Profile/POC)
  - **§3 (S/D freshness)** copre già il "consumo" delle zone S/D per esecuzione (fresh > tested) — qui la letteratura SMC aggiunge il *meccanismo*: l'OB è una zona S/D, l'absorption la valida, il 50%/MT ne misura il decadimento, e l'OB rotto diventa Breaker (cambio di polarità). Rimanda al §3 per la regola operativa "prediligi fresh / usa tested_3+ come target".
  - **§7 (Volume Profile / POC)** copre già POC/naked VPOC/VAH-VAL/HVN-LVN come conferma — qui la letteratura aggiunge il *contesto order flow*: Market Profile/TPO/Initial Balance (tempo vs volume), Footprint, Cumulative Delta, e il caveat che la Value Area non è statistica pura. Non ricopiare i marker `POC_weekly`/`POC_monthly`: vedi §7.
- Decisioni rilevanti: ../../DECISIONS.md

## Fonti
File in `fondamenti_tecnici/_sorgenti/`:
- **HOW TO MASTER LIQUIDITY - Soulz** (`HOW TO MASTER LIQUIDITY - Soulz (1)_260519_142118.pdf`) — autore Soulz. Base istituzionale completa: market mechanics, struttura, liquidità, FVG, OB, Fibonacci/Premium-Discount, MTF, order flow (HRLR/LRLR), Market Maker Models, ATAS.
- **What Is Liquidity - CryptoSoulz** (`What Is Liquidity - CryptoSoulz_260519_142104.pdf`) — autore CryptoSoulz. Aggiunte: deviation (weak/strong), range trading, midpoint 0.5, order flow (HVN/LVN, VPOC/naked VPOC, heatmap, COB/SVP, absorption/exhaustion, real vs fake), Market Profile/TPO/IB, sessioni.
- **THE ORDERFLOW - CryptoSoulz** (`THE ORDERFLOW - CryptoSoulz (1)_260519_142044.pdf`) — autore CryptoSoulz. Aggiunte (tooling): order book (bid/ask/spread/depth/walls/spoofing), Volume Profile, Market Profile, Liquidation Heatmap, SCF Indicator/Kiyotaka.ai, Footprint vs Volume vs Market Profile.
- **The Liquidity Edge** (`The Liquidity Edge (2)_260519_142135.pdf`) — autore SoulzBTC. Aggiunte: MSS vs BOS, Volume Imbalance, Displacement (36%), IFVG/BPR, NWOG/NDOG, Killzones, sweep detection, detection indicator-based (Smart Liquidity Indicator).
- (riferimento secondario) **PDF - HOW TO MASTER THE ART OF TRADING - BY SOULZ** — cap. Power of Three (PO3 = Accumulation/Manipulation/Distribution) e Liquidation Levels.
