# Pilastro Investing — Piano GREZZO (pre-studio) — 2026-06-02

> **Stato: BOZZA grezza, non esecutiva.** Scaturisce dal pivot dello Stock Selector
> ([DECISIONS.md 2026-06-02](../DECISIONS.md), [INVESTMENT_ALGO_DESIGN.md](INVESTMENT_ALGO_DESIGN.md)):
> niente algoritmo custom, niente selezione titoli, niente market-timing. Il pilastro investing
> diventa **due secchi passivi**. L'utente tornerà a costruire gli step esecutivi DOPO essersi
> informato sulle incognite elencate in §4. Qui c'è solo lo scheletro + i guardrail del quant.
>
> **▶ NEXT SESSION — START HERE.** Questo è il documento vivo del pilastro investing. Per produrre
> il piano NUMERICO concreto serve la **categoria A (input personali)** in §5c: chiedi all'utente
> età (e quando compie 30), orizzonte di decumulo, spese mensili, rata DCA sostenibile, target di
> capitale, equity floor finale, view sugli Emergenti, uso del buffer. Con quelli → allocazione
> iniziale, sizing buffer, tabella glide-path, step esecutivi (broker→PAC→ribilancio). Da chiudere
> con l'utente anche il bivio **DIY vs LifeStrategy all-in-one** (§5b). NON costruire esecuzione/
> codice prima di avere la categoria A.

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
