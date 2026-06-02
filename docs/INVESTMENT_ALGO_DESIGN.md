# Investment Algo — Design & Research (evoluzione dello Stock Selector) — 2026-06-02

> Sintesi di: inventario knowledge base + deep research (TAA/edge, vendor dati PIT, mercati
> mondiali) + prototipo Layer 1 (motore esposizione). Obiettivo dell'utente: **algoritmo di
> investimento che legge le condizioni di mercato → determina l'esposizione (rischio vs
> liquidità) → gestisce il capitale per battere l'SP500 con profilo asimmetrico (su nei rally,
> protetto nei cali)**, oggi US, in prospettiva multi-mercato.
> Prerequisito: vedi [stock_selector-2026-06-01.md](reviews/stock_selector-2026-06-01.md)
> (lo stock-picking cross-sezionale nell'SP500 non ha edge dimostrato; l'asimmetria viene dal
> timing dell'esposizione).

## 1. Cosa dice l'evidenza (deep research)

### Edge del market-timing dell'esposizione (TAA) — FONDATO, con caveat
- **Faber GTAA** (SMA 10 mesi → in asset/cash): riduce il max drawdown ~46%→<10%, rendimenti
  equity con volatilità da bond, Sharpe ~0.6, edge tenuto OOS 2006-2012. Il profilo asimmetrico
  **è ottenibile**.
- **Caveat (Hoffstein "Fragility", GEM 2016-17)**: la TAA trend-following **whipsaw-a e lagga
  nei bull choppy** (trade inutili, Sharpe peggiore di SPY in alcune fasi); fragile alla
  specifica (timing luck). → diversificare le regole/lookback, non single-point.
- **Liquidità Fed (QE/QT, net liquidity)**: relazione reale ma **"imposta il contesto, non è un
  trigger preciso"** — falling liquidity = headwind, non predice il crash. → usare come
  **risk-scaler/contesto**, NON come segnale di timing primario.

### Vendor dati PIT — CORREZIONE al piano "compro da IB"
- **Interactive Brokers NON fornisce dati dei titoli delistati → survivorship bias automatico.**
  IB va bene per esecuzione/live, **non** per dati di backtest.
- **Sharadar SF1** (via Nasdaq Data Link / QuantRocket): ~25 anni fondamentali **point-in-time**,
  titoli attivi+delistati, **costituenti S&P 500 storici dal 1957**. Il vendor giusto per i
  Layer 2-3 (selezione fondamentale survivorship-free).
- **Norgate Data**: prezzi survivorship-free + **costituenti storici indici** (S&P500/Russell/
  Nasdaq), integrazione Python. Forte per prezzi+constituents.
- (Pricing esatto da verificare sui siti; non fabbricato qui.)

### Mercati mondiali — NO a "tutti", SÌ a pochi blocchi liquidi
Risposta diretta alla domanda "ha senso monitorare tutti i mercati mondiali?": **No.**
- US ~50%+ del market cap globale; home bias tipico ~70%. Il beneficio di diversificazione
  esiste (Sharpe migliore) **ma satura in fretta** e **le correlazioni sono salite nel
  dopoguerra e convergono a 1 nelle crisi** (il beneficio sparisce proprio quando servirebbe —
  coerente con [05_portfolio_rischio](../fondamenti_tecnici/05_portfolio_rischio/principles.md)).
- Nessun paese è il migliore per >2 anni consecutivi → argomento PER avere *breadth*, ma
  ottenibile con **4-6 blocchi liquidi**, non con decine di mercati.
- **Raccomandazione**: concentrarsi su pochi blocchi a bassa correlazione e alta liquidità
  (es. **US, Developed ex-US/Europa, Giappone, Emerging/Cina**) via ETF indicizzati. Oltre
  ~6 blocchi: complessità, costi e carico-dati crescono senza diversificazione proporzionale.
  La leva che conta per l'asimmetria resta il **Layer 1 (timing esposizione)**, non l'ampiezza.

## 2. Prototipo Layer 1 — evidenza su dati gratuiti (2003-2026, 282 mesi)

Backtest del motore di esposizione (SPY total-return + FRED WALCL/DFF). Script:
[layer1_prototype.py](../strategies/stock_selector/analysis/layer1_prototype.py).

| Strategia | CAGR | vol | Sharpe | maxDD | up-cap | dn-cap | +mesi giù | alpha | a_t |
|---|---|---|---|---|---|---|---|---|---|
| Buy&Hold SPY | +11.6% | 14.5% | 0.71 | **−50.8%** | 100% | 100% | 0% | — | — |
| **Faber 10m-SMA** | +9.2% | 10.3% | **0.74** | **−21.7%** | 70% | 64% | 23% | +2.5% | +1.60 |
| Fed-quadrant (solo) | +6.8% | 10.8% | 0.50 | −50.8% | 62% | 63% | 4% | −1.4% | −1.35 |
| Faber AND Fed | +6.6% | 6.6% | 0.74 | **−10.0%** | 43% | 32% | 26% | +2.0% | +1.82 |

**Letture:**
1. **Il trend-timing (Faber) funziona come da letteratura**: dimezza il max drawdown
   (−51%→−22%), alza lo Sharpe, al **costo** di ~2.4% CAGR e del 30% di partecipazione ai rally
   (up-cap 70%). È la metà "protezione" dell'obiettivo, quantificata.
2. **Il Fed-quadrant da SOLO è un cattivo trigger** (Sharpe 0.50, maxDD non ridotto, alpha
   negativo) → **conferma la research**: la liquidità è *contesto, non timing*. Va combinata con
   il trend, non usata come innesco.
3. **Tensione confermata**: "Faber AND Fed" ha la protezione massima (maxDD −10%) ma up-cap 43%
   = lasci troppo rally sul tavolo. **Non puoi avere alta partecipazione E alta protezione da
   un tilt statico** (coerente con l'anomalia low-vol dello Step 1).
4. **"Netto positivo nei cali"**: il timing ti rende positivo nel 23-26% dei mesi negativi (vs
   0% buy&hold) — meglio, **ma non sempre**. Restare *sempre* positivi richiede la gamba cash +
   rf, che compensa solo in parte.
5. **alpha t ≈ 1.6-1.8**: suggestivo ma **non conclusivo** a 95% su 282 mesi (e questo è il
   caso più pulito, SPY price, survivorship-free). Onestà statistica: promettente, non provato.

## 3. Architettura raccomandata (4 layer)

| Layer | Funzione | Fondamento | Dati | Stato |
|---|---|---|---|---|
| **1. Esposizione** | regime+trend → % azionario vs cash | Faber/dual-momentum (edge OOS) + Fed come *risk-scaler* | FRED (gratis) + indici | **prototipato, regge** |
| **2. Archetipo/tilt** | tilt A/B/C/D per quadrante | [06](../fondamenti_tecnici/06_stock_selection/principles.md) | fondamentali PIT (Sharadar) | da progettare |
| **3. Selezione titoli** | screen quality, diversificato per settore | CANSLIM/VCP + [05](../fondamenti_tecnici/05_portfolio_rischio/principles.md) | PIT (Sharadar/Norgate) | da progettare |
| **4. Multi-mercato** | 4-6 blocchi liquidi via ETF | research §1 | indici/ETF globali | futuro |

**Principio guida (da [05](../fondamenti_tecnici/05_portfolio_rischio/principles.md)):** misurare
il successo come **alpha CAPM + up/down-capture**, non come return assoluto vs SP500 (battere
l'indice con più beta non è alpha). L'alpha vive nel Layer 1; i Layer 2-3 aggiungono selezione
*solo se* dimostrano IC>0 su dati PIT (oggi non dimostrato).

## 4. Sequenza operativa (spendi i dati al momento giusto)

1. **Ora, gratis**: irrobustire il Layer 1 (ensemble di lookback trend + Fed/credit come scaler;
   walk-forward; costi di turnover) — è dove vive l'asimmetria, validabile senza comprare dati.
2. **Quando il Layer 1 regge**: comprare **Sharadar/Norgate** (non IB) per testare i Layer 2-3
   (archetipi + screen) survivorship-free.
3. **Solo se i Layer 2-3 mostrano edge**: estendere al multi-mercato (Layer 4) sui blocchi liquidi.

## 5. Test mancanti prima di scrivere l'algoritmo definitivo

- [ ] Layer 1 ensemble (3/6/10/12m trend) + walk-forward + costi → alpha_t robusto?
- [ ] Fed/credit come *scaler continuo* (non quadranti secchi) sopra il trend.
- [ ] Sharadar/Norgate: pricing e accesso confermati prima dell'acquisto.
- [ ] Universo multi-mercato: 4-6 ETF, matrice di correlazione, beneficio marginale reale.

---

# Merge della review a 5 agent — 2026-06-02

Cinque lenti indipendenti (quant adversariale, practitioner TAA, portfolio/fattori, ingegnere/
dati, macro/regime) hanno valutato il design. **Convergenza forte** su 6 punti + contributi
distinti che migliorano il design. Sintesi operativa.

## Consenso (tutti o quasi)

1. **L'alpha_t=1.6 NON è significativo sotto multiple-testing.** 4-12 lookback impliciti + pesi
   quadrante scelti ex-post → DSR/PBO/White's Reality Check/walk-forward obbligatori. "Promettente,
   non provato" va preso alla lettera: **NO-GO a scrivere l'algoritmo**, RAFFINA il prototipo.
2. **Non è alpha: è β-timing di fattori noti e decaduti** (time-series momentum + low-vol/BAB).
   L'intercetta CAPM a β-costante è *spuria* su una strategia a β tempo-variante. Va misurata con
   **CAPM timing-aware** (Henriksson-Merton / Treynor-Mazuy) + **spanning multi-fattore**, non OLS.
   → Inquadrare il prodotto come **risk-management fattoriale (β<1)**, non come ricerca di alpha.
3. **Il Fed-quadrant è uno SCALER continuo, non un trigger.** I pesi secchi 0.2/0.5/1.0
   (`layer1_prototype.py:64-67`) sono arbitrari/overfit; da solo dà alpha negativo (confermato).
4. **Look-ahead FRED**: WALCL/DFF presi come serie *correnti revisionate* + `ffill` → micro
   look-ahead da lag di pubblicazione. Usare ALFRED vintage o lag esplicito di 1 release.
5. **Tagliare Layer 2-3-4 ora**: lo stock-picking è già falsificato (IC~0). Non comprare
   Sharadar/Norgate finché non esiste un'ipotesi di edge *non già smentita*. **Congelare**
   `strategy.py`/`scoring.py`, non riscriverli.
6. **L'obiettivo asimmetrico è irraggiungibile da un tilt statico long-only.** Il prototipo
   quantifica il trade-off, non realizza l'impossibile.

## Contributi distinti che MIGLIORANO il design

- **[TAA] Da on/off binario su un solo SPY → dual-momentum cross-asset (GEM).** Ruota
  SPY ↔ ex-US ↔ bond: l'asimmetria viene dalla rotazione equity-equity + momentum assoluto verso
  bond, con **up-capture più alto** che equity↔cash. *Potenzialmente rompe la "tensione"
  dichiarata*, perché la tensione nasce dallo schema statico/binario, non dal timing in sé.
  Aggiungere **ensemble di lookback (3/6/12m) + VOTO (non AND) + tranche di ribilancio sfalsate**
  (l'AND collassa up-cap a 43%; il voto no). È il rimedio alla timing-luck di Hoffstein.
- **[Fattori] Vol-targeting continuo** (w = σ_target/σ_realizzata, Harvey-Hoyle-Korgaonkar) al
  posto dei pesi quadrante. Diversificatori **crisi-robusti** (trend/long-vol/cash), non solo
  bond (falliscono nel 2022 quando le correlazioni convergono). Multi-mercato = riduzione di
  varianza, **mai contato come alpha**.
- **[Macro] Credit spread (HY OAS, FRED `BAMLH0A0HYM2`) + yield curve (`T10Y3M`)** sono i segnali
  macro *ortogonali al prezzo* (vera complementarità) e danno ~70% del valore macro — molto
  meglio del livello WALCL. **Markov è ridondante con Faber** (entrambi momentum di prezzo):
  tenerne UNO come timer, Markov solo come filtro anti-whipsaw (persistenza P[i,i]).
  `core/regime.py` (Wilder/intraday) **non appartiene** a un motore mensile.
- **[Quant] La protezione (maxDD/down-capture) è MECCANICA e affidabile; solo l'alpha è da
  provare.** Distinzione chiave: il prodotto "β<1 che taglia i drawdown" è reale già ora.
- **[Ingegnere] Conflitto di priorità da esplicitare** ([DECISIONS.md](DECISIONS.md): custom IN
  FONDO, OctoBot prima; investing = fase conclusiva, entrate prop oggi ~0). Questo lavoro è
  **validazione in slack-time, NON una promozione** e non deve sottrarre energia a OctoBot/
  Telegram copier. MVP riusa `core/regime.py` + `layer1_prototype.py` (~80% esiste).

## Design v2 mergiato — il Layer 1 da validare

Motore **mensile, su asset-class (ETF), non su titoli**:
- **Timer**: dual-momentum cross-asset (SPY/ex-US/bond) con **ensemble lookback votato** + tranche sfalsate.
- **Sizing**: **vol-targeting continuo** (non on/off, non quadranti).
- **Overlay macro**: risk-scaler continuo da **credit spread + yield curve** (non Fed-quadrant secco); Markov = anti-whipsaw.
- **Igiene dati**: FRED vintage/lag, cache, no ffill che guarda avanti.
- **Gate di validazione** (via `/quant-review`, gate già istituito): DSR(N reale) + PBO/CSCV +
  walk-forward anchored + White's RC + MC permutation a blocchi + Newey-West + CAPM timing-aware
  (HM/TM) + spanning fattoriale. **GO solo se l'alpha sopravvive a tutto questo.**

## Cosa NON fare (consenso)
Non scrivere l'algoritmo definitivo ora; non costruire Layer 2-3-4; non comprare dati PIT;
non usare Fed-quadrant come trigger; non promuovere nulla a operatività (rispetta le priorità).

---

# MVP Layer 1 v2 — risultati del backtest e VERDICT — 2026-06-02

Implementato il design v2 mergiato ([tactical_allocation.py](../strategies/stock_selector/analysis/tactical_allocation.py)):
dual-momentum cross-asset (SPY/EFA/EEM/TLT/GLD + AGG), ensemble lookback {3,6,12m} votato,
vol-targeting continuo, overlay macro (credit spread + curva, percentili espansivi), costi
turnover, segnali laggati. Universo 2004-11 → 2026-06 (260 mesi, include 2008/2020/2022).
Metriche con **alpha timing-aware** (Treynor-Mazuy + Henriksson-Merton), come richiesto.

| Strategia | CAGR | Sharpe | maxDD | up-cap | dn-cap | +mesi giù | α_TM | α_TM t | γ (timing) | turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| Buy&Hold SPY | +11.2% | 0.67 | −50.8% | 100% | 100% | 0% | — | — | — | — |
| 60/40 | +8.1% | 0.69 | −32.3% | 65% | 60% | 8% | +0.4% | 0.94 | −0.07 | — |
| **Faber SPY** | +9.0% | **0.71** | **−21.4%** | 70% | 63% | 23% | +2.5% | 1.27 | +0.02 | — |
| **GEM 12m** | +9.3% | 0.64 | −23.0% | **77%** | 73% | 9% | +1.2% | 0.63 | +0.06 | — |
| v2 noMacro | +7.0% | 0.52 | −38.8% | 54% | 47% | 29% | +3.2% | 1.75 | −1.26 | 4.2 |
| v2 FULL | +6.9% | 0.52 | −38.8% | 54% | 47% | 29% | +3.1% | 1.72 | −1.26 | 4.2 |

## Verdict — NO-GO al custom complesso; la frontiera è una regola SEMPLICE, senza alpha provato

1. **La complessità non si ripaga (anzi peggiora).** Il v2 multi-asset + vol-target + macro — la
   versione "migliorata" dai 5 agent — è la **peggiore**: Sharpe 0.52, maxDD −38.8% (peggio del
   Faber −21% e GEM −23%), **γ di timing NEGATIVO** (−1.26 = de-risk nei momenti sbagliati). La
   review aveva ragione a chiedere validazione: l'avrei "costruito" e sarebbe stato un downgrade.
   *Non lo tuno per farlo vincere: sarebbe esattamente il data-snooping che la review vieta.*
2. **NESSUNA variante ha alpha di timing significativo.** Tutti gli α_TM t e α_HM t < 2. I test
   corretti (Treynor-Mazuy/Henriksson-Merton) confermano la previsione dell'agent-fattori: l'α
   "alto" del v2 (+3.2%) è l'**intercetta spuria** di una strategia a β basso (γ negativo prova
   che NON è skill di timing). Nessuna skill dimostrata.
3. **Le regole più semplici vincono** (Faber, GEM): Sharpe ~marginalmente sopra 60/40, drawdown
   **dimezzato** vs buy&hold — ma protezione **meccanica** (β<1), non alpha.
4. **OOS debole**: v2 α_TM t passa da 1.83 (1ª metà) a 0.43 (2ª metà) → decadimento fuori campione.
5. **Overlay macro ≈ nullo** (FULL ≈ noMacro): terza conferma che il Fed/credit è contesto, non edge.

## Cosa significa per l'obiettivo dell'utente (onestà piena)

L'obiettivo "**outperformare l'SP500 nei rally E restare positivo nei cali**" è, sui dati,
**non raggiungibile** con un overlay di esposizione long-only:
- **Non si batte l'SP500**: tutte le strategie di timing hanno CAGR **inferiore** (6.9-9.3% vs
  11.2%) — ridurre esposizione in un bull secolare costa rendimento. Niente alpha.
- **Non si resta positivi nei cali**: miglior dn-capture ~63%, positivi solo ~23% dei mesi negativi.
- **Cosa È reale e ottenibile**: drawdown molto più piccolo (−21% vs −51%) e Sharpe leggermente
  migliore, al costo di ~2% CAGR/anno. È un profilo **"più liscio, non più ricco"** — un prodotto
  di *gestione del rischio*, non di sovraperformance.

→ Decisione tecnica: **non esiste evidenza per costruire un algoritmo di investimento custom che
batta l'SP500.** Se l'utente valuta i drawdown ridotti (es. in ottica leva/prop o tenuta
psicologica), la versione difendibile è una **regola semplice (Faber 10m o GEM)**, niente
multi-asset elaborato, niente Layer 2-4, niente acquisto dati PIT. Altrimenti, l'SP500 buy&hold
(o un 60/40) resta il benchmark difficile da battere — coerente con tutta l'evidenza raccolta.

## Fonti (research)
- Faber M. — *A Quantitative Approach to TAA*, SSRN 962461. mebfaber.com.
- Antonacci G. — *Dual Momentum / GEM*; Hoffstein C. (Newfound) — *Fragility Case Study: GEM*.
- Sharadar Fundamentals (sharadar.com / quantrocket.com); Norgate Data (norgatedata.com).
- Vista/Cambridge/Aberdeen — international diversification & rising correlations.
- Net liquidity / Fed balance sheet vs equities (macrofinalytic, CTSstock) — "backdrop non trigger".
