# Pilastro Investing — Piano OPERATIVO — agg. 2026-08-07

> **Stato: ESECUTIVO.** La categoria A (input personali) è stata chiusa il 2026-08-04/07 e il piano
> operativo è in **§0**. Il resto del documento resta come traccia del percorso: architettura (§1),
> glide-path (§2), guardrail del quant (§3), ricerca esecutiva (§5b). Origine: pivot dello Stock
> Selector ([DECISIONS.md 2026-06-02](../DECISIONS.md),
> [INVESTMENT_ALGO_DESIGN.md](INVESTMENT_ALGO_DESIGN.md)) — niente algoritmo custom, niente
> selezione titoli, niente market timing.

---

## §0 — PIANO OPERATIVO (attivo da fine settembre 2026)

### Input personali (categoria A — chiusi)

| Voce | Valore |
|---|---|
| Età | **21 anni** (finestra under-30 sui canoni broker fino al 2035) |
| Rata DCA | **100 €/mese** — l'utente aveva calcolato 150 sostenibili, sceglie 100 per garantire di non saltare mai |
| Obiettivo | **Capitale più alto possibile per smettere di lavorare quando vuole.** Nessuna data d'uso → orizzonte indefinito |
| Fase glide-path | **Fase 1 — accumulo**, 100% azionario |
| Buffer e spese mensili | **Fuori perimetro**: li gestisce l'utente. Pianifichiamo solo il Secchio B |

### Il modello di finanziamento: serbatoio, non flusso

Le entrate sono **2-3 stipendi estivi** che devono coprire ~10 mesi fino all'estate successiva
(situazione stabile fino alla laurea, target 2 anni). Il PAC **non è alimentato da un flusso
mensile: è un prelievo a rate da un serbatoio**. Il rischio non è "un mese guadagno meno" ma "a
marzo il serbatoio è basso e il PAC salta".

**Contromisura vincolante:** a fine settembre, quando il budget è pieno, si **vincolano
€1.200** (12 × 100) separati dai soldi di spesa. Da quel momento il PAC è garantito per l'anno a
prescindere da come va, e non dipende più dalla disciplina mese per mese.

### Il piano

| Voce | Decisione |
|---|---|
| **Broker** | **Trade Republic** — regime amministrato (post-migrazione succursale italiana), PAC senza commissioni, frazionario, canone €0 |
| **Strumento** | **VWCE** — Vanguard FTSE All-World UCITS ETF (USD) **Accumulating**, `IE00BK5BQT80`, TER 0,22%, domicilio Irlanda. **Verificato presente nel PAC dell'app** |
| **Rata** | **100 €/mese**, data fissa del mese, mai spostata |
| **Esecuzione** | XETRA, 09:00-17:30. Frazionario → i €100 entrano interi ogni mese |
| **Partenza** | **Fine settembre 2026** |
| **Ribilancio** | **Nessuno.** Un solo strumento, 100% azionario, fase 1: non c'è niente da ribilanciare |

### Regola dei top-up

I €50/mese di differenza tra i 100 scelti e i 150 sostenibili **non entrano nella rata ricorrente** —
si versano come **top-up discrezionali** quando il mese lo permette. Si ottiene la media da 150 senza
assumersi l'impegno da 150 (coerente con lump-sum > DCA sugli importi straordinari).

**Vincolo di costo:** l'ordine manuale costa **€1 di regolamento**. Un top-up da €50 pagherebbe il
2%. → **mai top-up manuali sotto ~€150**: si accumulano e si fa un ordine solo.

Gli **interessi sulla liquidità vincolata** (~€9/anno netti al 2% ordinario; ~€13 se si applica la
promo 3% per nuovi clienti) si versano come top-up di fine ciclo. **Non sono una leva**: sono lo
0,75% dei versamenti annui e in termini reali il parcheggio è circa a pareggio o leggermente
negativo. Il loro senso è pagare pochissimo per un'opzione di liquidità che ha valore vero.

### Revisione: una volta l'anno, a settembre

La revisione si aggancia al **ciclo di reddito** (settembre = nuovo budget), non all'anno solare.

**Si rivede:** la rata (sulla base del surplus **verificato**, non stimato), la tenuta del vincolo dei
€1.200, eventuali cambi nelle condizioni del broker.
**Non si rivede:** la scelta dell'ETF, l'allocazione, le prospettive di mercato.

**Trigger di aumento della rata** — solo per reddito, mai per performance di mercato, e
preferibilmente come **% del netto** così si auto-aggiorna. ⚠️ **La laurea NON è un trigger**: il
reddito sale ma salgono anche le spese (vita da solo). Il trigger corretto è **6-12 mesi dopo che la
nuova struttura di spesa si è stabilizzata**, quando esistono dati veri sul surplus.

### Cosa NON fare nei primi due anni

- Non cambiare ETF, non aggiungerne un secondo.
- Non fermare i versamenti in un ribasso — è esattamente quando il DCA sta lavorando ([08 §Decenni persi](../fondamenti_tecnici/08_asset_allocation_passiva/principles.md): in accumulo il drawdown è un alleato).
- Non guardare il saldo più della revisione annuale.
- Non spostare i soldi su "opportunità migliori".
- Non alzare la rata alla laurea (vedi sopra).

### Quando finisce la fase 1

Non per età, ma per **rapporto**: quando i versamenti annui scendono sotto il ~5-10% del saldo. A
rata costante servirebbero ~8-9 anni per arrivare a ~€12.000; con i versamenti in crescita
post-laurea arriverà prima. **Fino ad allora: fase 1, nessun bond, nessun glide-path attivo.**

### Verifiche residue prima dell'attivazione

- [ ] Conto effettivamente **migrato alla succursale italiana**: IBAN italiano, deposito italiano, certificazione fiscale italiana.
- [ ] Verificare se si applica la **promo 3%** per nuovi clienti e la sua data di scadenza (tasso ordinario: 2%, legato BCE, accredito mensile, senza tetto per IBAN IT).
- [ ] Verificare come viene applicata l'**imposta di bollo 0,2%/anno** sul dossier e che compaia nella certificazione fiscale.
- [ ] Schermata costi ex-ante e sede di esecuzione al primo ordine.

> ⚠️ **Commissione zero ≠ costo zero.** I costi reali del piano sono: **TER 0,22%**, **spread** in
> esecuzione, **bollo 0,2%/anno**. Nessuno dei tre si evita cambiando broker — il bollo è una tassa,
> non una tariffa.

---

## 1. Architettura: due secchi separati

### Secchio A — Cuscinetto di sicurezza (preservazione + liquidità)
- **Cosa**: cash / strumenti monetari / bond brevissimi (conto deposito, money market, T-bill o
  govt brevi). Stabile e liquido.
- **Quanto**: N mesi di spese (target da fissare sui TUOI numeri — da studente con spese basse,
  meglio un target in € assoluto). Tipico 3-12 mesi.
- **Fonte**: riempito **PRIMA** e dal capitale **stabile** (stipendio), non dai profitti trading.
  Una rete di sicurezza finanziata solo da una fonte rischiosa non è una rete.
- **Funzione vera**: ti permette di **non vendere il Secchio B nei crolli**. Non è un investimento.
- **Manutenzione**: ~zero.

### Secchio B — Accumulo crescita (il PAC)
- **Cosa**: 1 ETF azionario **globale All-World** (scelta fatta), accumulazione, TER basso, UCITS.
- **Come**: DCA automatico, importo fisso mensile, **indipendente dalla fonte** che lo alimenta.
- **Oggi**: ~100% azionario (decisione attuale: "oggi sono per sì", reggo i drawdown).
- **Ribilancio**: leggero (annuale o a soglia). Niente ottimizzazione.

## 2. Il glide path (lo scheletro del "tra qualche anno")

La tua tolleranza è volatile e cambierà: previsto. La riduzione dell'azionario va fatta **per
regole, a priori, per fase/età — MAI reattiva al mercato** (quello è market-timing mascherato,
già dimostrato non pagante).

| Fase | Situazione | Azionario | Difensivo (bond/cash) | Overlay timing |
|---|---|---|---|---|
| 1 — Accumulo (ORA) | giovane, versamenti >> saldo | 90-100% | 0-10% | No (DCA puro) |
| 2 — Crescita matura | saldo cresce, versamenti < ~5-10% del saldo | 70-80% | 20-30% | No |
| 3 — Preservazione | saldo grande, orizzonte d'uso vicino | 40-60% | 40-60% | *qui* si può valutare |

Numeri e strumenti esatti = da definire DOPO lo studio (§4).

## 3. Cosa propone il QUANT (guardrail)

- **Default = DCA puro su indice ampio.** È il benchmark che battere è dimostrato difficile
  (vedi [INVESTMENT_ALGO_DESIGN.md](INVESTMENT_ALGO_DESIGN.md)). Non reintrodurre
  selezione/timing nel Secchio B senza un edge **provato** — non c'è.
- **Glide path per regole, non reattivo.** Decidi le soglie a priori; non "sento che il mercato…".
- **Costi e fiscalità sono l'unico vero edge controllabile.** TER basso + pochi ribilanci battono
  qualsiasi furbizia tattica: 0.3% di TER risparmiato/anno, composto su decenni, vale più di
  ogni overlay.
- **Il buffer NON insegue rendimento.** Bond lunghi/high-yield nel buffer = rischio equity
  travestito (2022 docet: i bond lunghi −30%). La sua unica funzione è esistere ed essere liquido.
- **In accumulo il drawdown è un alleato** (compri a sconto col DCA): non assicurarti contro un
  non-rischio pagando CAGR. La protezione serve in fase 3, non ora.
- **Eccezione comportamentale**: se temi di mollare il piano in un −50%, meglio un 85/15
  *strutturale* tenuto con disciplina che un 100% azioni abbandonato nel panico. Insurance contro
  te stesso, non contro il mercato.

## 3b. Terzo secchio (sleeve trend/managed-futures) — DECISIONE: rimandato a fase 2-3

> Chiusura 2026-06-14 ([DECISIONS.md](../DECISIONS.md)). Idea emersa dal materiale
> volatility-drag / orthogonal-streams ([05_portfolio_rischio](../fondamenti_tecnici/05_portfolio_rischio/principles.md)):
> aggiungere uno *sleeve* trend-following / managed-futures (tipo DBMF/KMLM) come terzo secchio,
> orthogonale all'equity, per **ridurre il drawdown** → meno volatility drag → meglio il geometrico.

**Decisione: NON ora. Rimandato alla fase 2-3 del glide-path.** Il pilastro resta a 2 secchi in
accumulo. Perché:

1. **Phase mismatch (decisivo).** Lo sleeve serve a tagliare il drawdown, ma **in accumulo il
   drawdown è un alleato** (il DCA compra a sconto — §3). Pagare carry negativo / CAGR inferiore per
   assicurarsi contro un non-rischio è sbagliato *adesso*. La protezione serve in **fase 3**, dove il
   glide-path (§2) già introduce la quota "difensiva".
2. **Casa naturale = il secchio difensivo della fase 2-3, non un secchio nuovo.** Là dove oggi
   scrivi "bond/cash", il drag-insight **raffina** la scelta: una parte di quella quota difensiva
   può essere uno sleeve **trend/managed-futures** invece dei (o accanto ai) bond — perché i **bond
   lunghi hanno fallito la diversificazione nel 2022** (correlazione salita coi tassi, §3 e
   [08](../fondamenti_tecnici/08_asset_allocation_passiva/principles.md)), mentre il trend-following
   fu orthogonale/positivo. **Questo è l'unico contributo operativo utile dell'idea.**
3. **Principio valido, ricetta no.** Lo stream orthogonale (R²≈0 → meno DD → meno drag) è fondato;
   la versione commerciale "leva + hedge-leg che batte SPY" è un singolo backtest in-sample non
   robusto. Se mai adottato: quota **modesta**, **mai con leva**, **mai come "batti il mercato"**.
4. **Praticità retail-IT.** DBMF/KMLM sono **US-domiciled** → estate tax + non-armonizzati + fisco
   complesso. Opzioni **UCITS** trend/managed-futures sottili → da verificare al momento (TER, AUM,
   domicilio), non ora.
5. **Base non costruita.** Il piano a 2 secchi non ha ancora i numeri (categoria A, §5c) → non
   aggiungere il layer più avanzato prima delle fondamenta.

**Condizione per riaprire:** (a) pilastro passivo numericamente vivo **E** (b) ingresso in fase 2-3
**E** (c) veicolo UCITS verificato → allora valuta lo sleeve come **frazione del difensivo**,
misurandone il contributo reale a drawdown/correlazione. Fino ad allora: **chiuso, non in sospeso.**

## 4. Incognite da studiare PRIMA di costruire l'esecuzione

I "campi non ancora toccati" dichiarati dall'utente — oggi **assenti** dai materiali raccolti
(candidati a un nuovo modulo `fondamenti_tecnici/08_asset_allocation_passiva/`):

1. **Globale vs US vs Emergenti**: pesi di mercato, comportamento storico, perché un All-World
   include già gli EM (~10%) e i Developed ex-US; rischio cambio.
2. **Tipi di ETF**: accumulazione vs distribuzione; replica fisica vs sintetica; TER; **UCITS vs
   US-domiciled** (fiscalità IT, estate tax USA, modulo W-8BEN); dimensione/liquidità del fondo.
3. **Bond**: governativi vs corporate; duration (breve vs lunga); ruolo nel glide path; perché i
   bond lunghi hanno fallito la diversificazione nel 2022 (correlazione salita coi tassi).
4. **Fiscalità IT**: regime amministrato vs dichiarativo; tassazione capital gain/dividendi (26%,
   12.5% su titoli di Stato white-list); compensazione minus/plus; bollo.
5. **Dimensionamento**: buffer in mesi/€ sui tuoi numeri; soglie del glide path; importo DCA.

## 5b. Ricerca esecutiva — 3 deep-research (2026-06-02)

### Cosa è ora SOLIDO (evidenza, non più da discutere)
- **DCA vs lump-sum**: il lump-sum batte il DCA ~67% delle volte (Vanguard 2023), ma chi versa
  flussi da reddito **è DCA per costruzione** → non-problema. Decisione lump-sum rilevante SOLO
  su importi straordinari (bonus/eredità → investi subito).
- **Ribilancio**: annuale + bande ±5% = 99% del beneficio del ribilancio giornaliero a 1/10 dei
  costi (Vanguard 1926-2014). Per un accumulatore: **ribilancia coi NUOVI versamenti** sull'asset
  sottopesato → gratis, nessun evento fiscale.
- **Buffer emergenza**: 3-6 mesi di spese; **6-12 se reddito variabile/irregolare** (il tuo caso:
  stipendio estivo + prop). Fuori dal portafoglio investito.
- **Glide-path**: scritto a priori, mai reattivo. Riferimenti TDF: ~90% equity da giovane → 30-50%
  a 65 (Vanguard), declino ~1%/anno. Conta in DECUMULO, non in accumulo.
- **Sequence risk**: in accumulo il crash è un ALLEATO (compri a sconto) → conferma "DCA puro ora".

### Candidati concreti emersi (da verificare, non raccomandazioni)
| Categoria | Candidati | Note |
|---|---|---|
| Broker PAC IT (gratis + **regime amministrato**) | Trade Republic, Fineco, Directa | under-30 azzera canoni; Scalable = dichiarativo |
| ETF All-World UCITS Acc | VWCE (IE00BK5BQT80, 0,22%), FWRA (IE000716YHJ7, 0,15%), SWDA+EIMI | FTSE All-World include EM ~10-12%; MSCI World no |
| Sleeve bond (glide-path futuro) | IS3S (€ govt 3-5y), VGEA | duration BREVE preferita per stabilità |
| Buffer cash EUR | XEON (LU0290358497, ~12,9% tax eff.), BOT 6-12m (12,5%) | XEON se serve liquidità rapida; BOT se mai toccato |

### Bivio strutturale NUOVO (rilevante per "light-touch")
**DIY** (All-World + bond sleeve gestiti a mano nel glide-path) **vs all-in-one LifeStrategy**
(es. Vanguard LifeStrategy 80/60/40 UCITS, fa il mix azioni/bond internamente). Il secondo
elimina il lavoro manuale del glide-path → coerente col tuo vincolo light-touch, al costo di meno
controllo e TER leggermente più alto. **Da decidere.**

## 5c. BUCHI DI KNOWLEDGE — mappa consolidata

**A. Input personali (solo tu — sbloccano i numeri del piano):**
- [ ] Età oggi (e quando compi 30 → azzera canoni broker) · orizzonte/età target decumulo.
- [ ] Spese mensili essenziali (base per il sizing del buffer).
- [ ] Rata DCA mensile sostenibile · target di capitale finale.
- [ ] Equity floor desiderato a fine glide-path (30/40/50%) · velocità del declino.
- [ ] View su Emergenti (→ FTSE All-World vs MSCI World).
- [ ] Logica d'uso del buffer (mai toccato → BOT; liquidità rapida → XEON).

**B. Verifiche fattuali (da confermare prima di scegliere):**
- [ ] Scalable Capital: data effettiva regime amministrato IT (oggi non confermata).
- [ ] Importo minimo PAC Directa · lista ETF zero-commissioni Fineco attuale (include VWCE/SWDA?).
- [ ] Tracking difference reale FWRA (giovane, TER 0,15% ma poca storia) vs VWCE.
- [ ] Tassazione esatta ETF monetari (XEON) e dividendi reinvestiti in ETF Acc in regime amministrato.
- [ ] Bollo sotto soglia nei primi anni · tassi cash/deposito EUR attuali (post-tagli BCE) ·
      portabilità deposito + "zainetto" minusvalenze se cambio broker.

**C. Decisioni strutturali (forks di design):**
- [ ] DIY vs LifeStrategy (vedi §5b) · broker (condiziona ticker/piazza/costi/fisco).
- [ ] MSCI World vs FTSE All-World · strumento buffer · trigger+duration sleeve bond.
- [ ] Regola di revisione glide-path (per età annuale? per evento di vita?).

## 5. Prossimi step (quando l'utente torna)
- [x] Modulo KB creato: [08_asset_allocation_passiva](../fondamenti_tecnici/08_asset_allocation_passiva/principles.md)
      (distillato da "Petrodollar ed ETF.txt": tipi ETF, UCITS vs US, fiscalità IT, bond, globale/US/EM, debunk petrodollaro).
      Restano da approfondire: soglie numeriche del glide-path, scelta ETF/broker specifici, sizing sui propri numeri.
- [ ] Fissare: target buffer (€), ETF All-World specifico, importo DCA, soglie glide path.
- [ ] Scrivere gli step esecutivi (apertura conto/broker, PAC automatico, regola di ribilancio).
- [ ] (Opzionale) aggiornare PROJECT.md: il pilastro investing = 2 secchi passivi, non lo Stock Selector.
