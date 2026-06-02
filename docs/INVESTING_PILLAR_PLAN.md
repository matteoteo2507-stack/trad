# Pilastro Investing — Piano GREZZO (pre-studio) — 2026-06-02

> **Stato: BOZZA grezza, non esecutiva.** Scaturisce dal pivot dello Stock Selector
> ([DECISIONS.md 2026-06-02](../DECISIONS.md), [INVESTMENT_ALGO_DESIGN.md](INVESTMENT_ALGO_DESIGN.md)):
> niente algoritmo custom, niente selezione titoli, niente market-timing. Il pilastro investing
> diventa **due secchi passivi**. L'utente tornerà a costruire gli step esecutivi DOPO essersi
> informato sulle incognite elencate in §4. Qui c'è solo lo scheletro + i guardrail del quant.

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

## 5. Prossimi step (quando l'utente torna)
- [ ] Studiare le incognite §4 → distillare in `fondamenti_tecnici/08_asset_allocation_passiva/`.
- [ ] Fissare: target buffer (€), ETF All-World specifico, importo DCA, soglie glide path.
- [ ] Scrivere gli step esecutivi (apertura conto/broker, PAC automatico, regola di ribilancio).
- [ ] (Opzionale) aggiornare PROJECT.md: il pilastro investing = 2 secchi passivi, non lo Stock Selector.
