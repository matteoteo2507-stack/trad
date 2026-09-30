---
tipo: preregistrazione
stato: LEAD
aggiornato: 2026-09-21
decisione: "DECISIONS 2026-09-21 (2) — A1 held-out non finanziabile"
metrica_corrente: "gradiente rho +0,929 a durata appaiata, ma divario vs random −0,238 [−0,363; −0,098]"
nota: "Fermo: il punto 3 (held-out) non si apre; round trend 2 di 3. Condizioni di riapertura in TREND_A1_HELDOUT_POWER §7."
---
# Trend following: uscita a coda aperta × gradiente di liquidità — PRE-REGISTRAZIONE

> **Committata PRIMA di guardare qualunque risultato.** 2026-08-14. Fonte esterna:
> *Pavel Kichev* (gestore algoritmico istituzionale), registrata in
> [`fondamenti_tecnici/_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md). Spec, universo, finestre,
> varianti, metriche e criteri di kill sono fissati qui **a priori**. Dopo i numeri non si cambiano;
> un bug si documenta come *fix*; ogni variante extra è un trial in più nel DSR.
> Motori: [`analysis/trend/export_d1.py`](../analysis/trend/export_d1.py) (dati),
> `analysis/trend/backtest.py` (test). Riusa [`core/quant_metrics.py`](../core/quant_metrics.py).

---

## Le due domande (indipendenti, un solo esperimento)

**Q1 — l'uscita a coda aperta.** *Tenendo fissa l'entrata*, un'uscita che lascia correre (trailing
su media mobile, nessun target) batte le uscite che troncano (R fisso, uscita a tempo)?
È la domanda dell'utente, parcheggiata il 2026-08-14 dopo il KILL dell'accoppiamento con l'entrata
NXT ([DECISIONS.md](../DECISIONS.md)). Qui trova finalmente un veicolo dove l'uscita aperta è la
**regola nativa**, non un innesto su un'entrata già morta.

**Q2 — il "playground".** L'espettanza della *stessa* regola di trend è **ordinata secondo la
volatilità/illiquidità dell'asset**, come sostiene la fonte (forex = massima liquidità, edge minimo →
agricoli/crypto = minima liquidità, edge massimo)? Se vero, è una spiegazione **ex-ante** della
nostra serie di null — tutti prodotti su FX, indici e oro, cioè il campo più competuto che esista.

## Contesto onesto (aspettative a priori)

Il prior è **sfavorevole**. TSMOM canonico è **NO-GO** su questo tipo di universo (Sharpe +0,21,
DSR 0,33 n.s., PBO 0,58) e il Donchian è la sua cugina stretta: stessa famiglia economica
(persistenza del trend), **round 2 di 3**. La letteratura documenta trend following forte 1985-2009
e **decaduto dopo il 2009** (Baltas-Kosowski); SG Trend index ~0,3-0,5 di Sharpe. Aspettativa
realistica: **edge debole o nullo**. Ciò che rende comunque utile l'esperimento: (a) è l'unico
veicolo pulito per Q1; (b) la spec **non è inventata da noi**; (c) Q2 è falsificabile e, se falso,
**chiude definitivamente l'alibi "sbagliavamo campo"** — che altrimenti resterebbe disponibile per
sempre come scusa a ogni null futuro.

## Dati — feed omogeneo, e perché era obbligatorio

I CSV storici in `data/` **non sono utilizzabili per questo test**: mescolano finestre diverse
(major FX dal 2003, indici/metalli/crypto dal 2020) e feed diversi. In
[`strategies/tsmom/backtest.py:88`](../strategies/tsmom/backtest.py#L88) lo Sharpe standalone per
asset è calcolato con `.dropna()` **per asset**, cioè ognuno sulla propria finestra: il residuo
"il trend vive sui trender e muore sui cross FX" che ci portiamo dietro da luglio è quindi
**confondato col periodo campionario** — gli asset positivi sono esattamente quelli che partono nel
2020. Questa pre-registrazione nasce anche per disfare quel nodo.

→ Tutto riscaricato da **Dukascopy, D1, stessa granularità, stesso lato (BID)**, in
`analysis/trading-bot-eval/data/dukascopy_d1/` (il feed broker **non** viene toccato).

## Universo (dichiarato a priori, 8 gruppi)

Scelto per **coprire il gradiente** del claim, e per colmare il buco che la pre-registrazione TSMOM
aveva dichiarato ("USD-pesante, senza bond né commodities; espansione solo se il concetto mostra
vita"):

| gruppo | strumenti |
|---|---|
| `fx_major` | EURUSD GBPUSD USDJPY AUDUSD USDCAD NZDUSD USDCHF |
| `fx_cross` | EURJPY GBPJPY EURGBP |
| `index` | NAS100 SPX500 |
| `bond` | BUND UKGILT USTBOND |
| `metal` | XAUUSD XAGUSD COPPER XPT XPD |
| `energy` | BRENT WTI NATGAS |
| `agri` | COCOA COFFEE COTTON SOYBEAN SUGAR |
| `crypto` | BTCUSD ETHUSD |

L'appartenenza al gruppo è **dichiarata nel codice di estrazione**, scritto prima di ogni backtest.
Strumenti con copertura insufficiente vengono esclusi **per disponibilità**, mai per risultato, e
l'esclusione è registrata in `_coverage.csv`.

## Finestre (fissate dalla copertura, prima di qualunque backtest)

- **W1 "lunga"** = 2012-01-01 → fine dati, per gli strumenti con copertura ≥ 90% del periodo.
  **Primaria per Q1** (più dati per il confronto fra uscite).
- **W2 "comune"** = data di inizio dello strumento più tardivo → fine dati, **tutti** gli strumenti.
  **Primaria per Q2** (nessun confondimento fra gruppo e calendario).
- **W3 "stazionarietà"** = W1 spezzata in **pre-2020** e **post-2020**.

## Spec canonica (dalla fonte, fissa, nessun tuning)

- **Entrata**: rottura del **massimo a 100 giorni** → long; del **minimo a 100 giorni** → short.
  Segnale su dati **≤ t-1**, esecuzione all'apertura di t (look-ahead-safe). Una posizione per
  strumento alla volta.
- **Uscita primaria (E1, la tesi)**: chiusura sotto la **SMA a 10 giorni** (long) / sopra (short).
  **Nessun target, nessuno stop iniziale** — è la spec della fonte ed è la coda aperta pura.
- **Unità di rischio**: `R = ATR(20)` all'entrata, calcolato su dati ≤ t-1. Serve a rendere gli
  esiti **confrontabili fra uscite e fra asset**; non è uno stop.
- **Costi** (round-trip, bps di nozionale, dichiarati a priori): `fx_major` 2 · `fx_cross` 3 ·
  `index` 3 · `bond` 3 · `metal` 4 (XAU/XAG) e 8 (industriali) · `energy` 8 · `agri` 12 ·
  `crypto` 8. Convertiti in R. **Stress a 3× costi** riportato a fianco.

## Le quattro uscite messe testa a testa (sulle IDENTICHE entrate)

| | regola | cosa rappresenta |
|---|---|---|
| **E1** | trailing SMA10, nessuno stop | **la tesi dell'utente** — coda aperta pura (spec della fonte) |
| **E1b** | trailing SMA10 + stop iniziale a 1R | la variante dell'utente (*"lo SL c'è"*) |
| **E2** | stop 1R / target 3R | l'uscita che **tronca** — geometria NXT/ORB |
| **E3** | uscita a tempo dopo 20 giorni | tronca senza dipendere dal prezzo |

Baseline (non varianti di strategia, non entrano nel conteggio trial):
- **B-oracolo**: uscita al massimo dell'escursione favorevole = **soffitto invalicabile** di
  qualunque regola d'uscita.
- **B-random**: entrata a **istante casuale**, stesso strumento, stesso lato, stesso R, stesso anno,
  stessa uscita E1, 3 controlli per segnale reale. **È il baseline che ha ucciso l'idea precedente**
  ([reviews/nxt-exit-ceiling-2026-08-14.md](reviews/nxt-exit-ceiling-2026-08-14.md)) ed è
  obbligatorio qui.

## Conteggio dei trial

**4 uscite × 3 lookback di entrata {50, 100, 200} = `n_trials = 12`** per il DSR.
**Primario = (100, E1)**; i lookback 50 e 200 sono **robustezza**, riportati ma **non eleggibili al
verdetto**. Nessun tuning per-asset, nessuna scelta di parametro dopo aver visto i numeri.
Famiglia trend: **round 2 di 3** (round 1 = TSMOM canonico, NO-GO).
Budget fonti esterne: **2ª di 2-3 del trimestre** (la 1ª è stata la griglia .80/.20).

## Regole di decisione (scritte prima dei numeri)

### Q1 — la tesi della coda aperta

**Supportata** se **tutte**:
1. **E1 batte B-random** — differenza appaiata con **lower bound BCa 95% > 0**. *Se fallisce qui,
   l'entrata non vale nulla e il confronto fra uscite è privo di significato*: si riporta così e Q1
   resta senza risposta (non "risposta negativa").
2. **E1 batte E2 e E3** — entrambe le differenze appaiate con lower bound BCa 95% > 0.
3. **Breadth**: maggioranza degli **8 gruppi** e maggioranza degli **anni**.
4. **Sopravvive a 3× costi** mantenendo il segno.

**Refutata** se E1 non batte E2/E3 pur battendo il random: l'entrata ha valore ma **lasciar correre
non è il modo di raccoglierlo**.

### Q2 — il playground

Proxy operativo del claim, dichiarato: la fonte afferma *"liquidity inversely relates to volatility;
low liquidity markets have higher volatility, offering more directional moves"* → il proxy è la
**volatilità realizzata annualizzata** dell'asset, quantità **misurata**, non un giudizio nostro.

- **Primario**: Spearman fra **volatilità media di gruppo** ed **E[R] medio di gruppo**, su **n = 8
  gruppi**, con test di permutazione. **Supportato** se ρ > 0 con p < 0,05. *(Buco 46, 30/09: e' una correlazione **di rango fra gruppi** — volatilita' contro E[R] — non fra serie di rendimenti: frequenza e finestra non si applicano.)*
- **Secondario** (riportato, non decisivo): stessa correlazione sui singoli strumenti — soggetta a
  **pseudo-replicazione** (7 major FX si muovono insieme), quindi non usabile per il verdetto.

⚠️ **Potenza dichiarata**: con n = 8 serve ρ ≈ 0,74 per p < 0,05. Il test può **refutare la versione
forte** del claim, non un effetto debole. Un null va riportato come *"ordinamento forte non
rilevato"*, **mai** come "il claim è falso".

### W3 — stazionarietà (richiesta esplicita dell'utente)

Il confronto fra uscite e il segno di E[R] sono riportati **separatamente pre-2020 e post-2020**.
Regola di lettura fissata ora: **se il risultato esiste solo post-2020, non è un edge** — è
regime-dipendenza, e vale il precedente ORB v2, dove esattamente questo pattern ha prodotto il NO-GO
([DECISIONS.md](../DECISIONS.md) 2026-07-16) e ha aperto il forward tuttora in corso. È il terzo
incontro con lo stesso fenomeno (ORB, TSMOM per-asset, ora questo): l'obiettivo dichiarato è
**capirlo**, non aggirarlo.

## Kill-switch

**NO-GO immediato** se: E1 non batte B-random (kill duro n. 2), **oppure** breadth < 50% dei gruppi,
**oppure** l'edge sparisce a 3× costi, **oppure** esiste solo post-2020.
→ si archivia la famiglia trend (round 2 di 3 consumato) e **Q1 resta senza veicolo**: non si cerca
una terza entrata su cui innestare la coda aperta senza un razionale nuovo e indipendente.

## Impegni anti-overfitting (vincolanti)

1. Spec presa **dalla fonte**, non ottimizzata: 100 giorni e SMA10 sono i suoi numeri.
2. Universo e gruppi dichiarati **nel codice di estrazione**, prima di ogni backtest.
3. Look-ahead-safe: segnale, ATR e SMA su dati ≤ t-1; esecuzione all'apertura successiva.
4. DSR/PBO/White's RC sul **vero** numero di varianti (12), cumulato con la famiglia.
5. Verdetto per **lower bound + breadth + baseline random**, mai sul best-asset o sul best-gruppo.
6. Nessuna esclusione di strumenti dopo aver visto i risultati; le esclusioni per copertura sono
   registrate in `_coverage.csv`.
7. Se qualcosa sopravvive: **nessuna promozione senza forward OOS pre-registrato**.


---

## Decisioni prese sulla COPERTURA (prima di qualunque backtest)

Registrate qui perche' prese su **disponibilita' dei dati e mai su risultato**:

1. **Esclusi USTBOND (start 2018-12-18), XPT (2021-12-01), XPD (2022-02-15)**: senza questo taglio
   la finestra comune W2 si sarebbe compressa a **4,5 anni**. Con la regola "start <= 2018-01-01"
   W2 resta a **8,7 anni** e tutti gli 8 gruppi restano rappresentati.
2. **Barre di weekend fuse nella barra feriale successiva** per i non-crypto. Il D1 grezzo
   Dukascopy contiene sessioni parziali di sabato/domenica (EURUSD: 761 barre domenicali, range
   mediano 0,137% contro 0,65% dei feriali): tenerle diluisce l'ATR(20), gonfia ogni multiplo di R
   e riduce il "Donchian 100 giorni" a ~83 giorni reali. La crypto tratta davvero 7 giorni: non si
   fonde nulla.

## Esito

- **Q1 — coda aperta: NO-GO** (kill-switch: E1 non batte il baseline random in nessuno dei 3
  lookback; l'uscita a tempo batte il trail in tutti e tre).
- **Q2 — playground: SUPPORTATO** dalla regola pre-registrata (rho +0,857, p 0,0060; controllato
  +0,786, p 0,0135) ma declassato a **LEAD** per i caveat dichiarati nel verdetto.
- **Lacuna dichiarata**: questa pre-registrazione **non ha definito un holdout sigillato per Q2**.
  Il risultato non ha superato un gate G2 e non e' promuovibile senza una pre-registrazione propria.

Verdetto completo: [docs/reviews/trend-exit-playground-2026-08-14.md](reviews/trend-exit-playground-2026-08-14.md).
