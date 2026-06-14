# Sizing vol-drag-aware — Level Analyzer (conf=2 fade)

> Generato da `analysis/trading-bot-eval/sizing_kelly.py` · RR 1:1.5 · costi reali
> (XAU spread $0.10, BTC $13). Trasforma l'edge per-trade validato
> ([LEVEL_ANALYZER_SPEC.md](LEVEL_ANALYZER_SPEC.md)) in una regola di sizing che
> massimizza la crescita **geometrica**, non l'EV aritmetico. Teoria:
> [05_portfolio_rischio](../../fondamenti_tecnici/05_portfolio_rischio/principles.md)
> (volatility drag), quant `agents/quant_reviewer.md` §4.

## Perche' non "rischio fisso a caso"

L'edge conf=2 e' positivo ma **piccolo e rumoroso** (mu_R ~ +0.09..+0.19). Il
volatility drag dice che l'EV positivo non basta: conta la crescita geometrica
`g(f)=E[ln(1+fR)]`, dove `f` = frazione del conto a rischio per trade (un -1 R
perde esattamente `f`). Sizing troppo grande -> il drag e il ruin risk mangiano
la crescita; troppo piccolo -> si lascia compounding sul tavolo. La risposta e'
**Kelly frazionario** sulla distribuzione reale + **tetto** + **cap aggregato**.

## Regola operativa

| Asset | n | mu_R | sigma_R | win | Kelly pieno f* | **f usata** | g/trade | haircut f* |
|---|---|---|---|---|---|---|---|---|
| XAU | 898 | +0.194 | 1.25 | 50% | 12.73% | **1.00%** | +0.186% | 6.24% |
| BTC | 1419 | +0.187 | 1.25 | 51% | 12.05% | **1.00%** | +0.179% | 5.95% |

- **Kelly pieno** = sizing growth-ottimo teorico, **da NON usare mai**. Annualizzato dal
  backtest darebbe numeri-fantasia (ordine +100%..+800%/anno): e' proprio il miraggio che
  fa saltare i conti, perche' assume che la mu storica sia vera e stabile su un edge sottile.
- **Frazione usata = 1/4 Kelly, con tetto assoluto 1.0% per trade.** Qui il
  vincolo che morde e' il **tetto**, non il Kelly frazionario (1/4 Kelly sarebbe ~3%). Stress
  test **haircut** (mu vera = meta'): 1/4-Kelly resta sopra il tetto -> **1.0% regge anche
  se l'edge fosse sovrastimato del 50%**.
- **A 1.0% il volatility drag e' trascurabile** (f^2*sigma^2/2 ~ 0.008%/trade): il drag
  e' un pericolo **solo se si sovradimensiona**. Restare piccoli lo annulla quasi del tutto.
- **Cap aggregato 2.0%**: piu' zone conf=2 nella stessa sessione sono trade **correlati**
  (stesso regime/sessione) -> non sommare il rischio pieno. Il clustering misurato e' **mite**
  (XAU 1.1/sess (p90 1); BTC 1.5/sess (p90 2)), quindi il cap aggregato raramente vincola: il tetto per-trade fa il grosso.

## Caveat (onesta')

- **Distribuzione piu' ampia/recente** del frozen LEVEL_ANALYZER_SPEC (la serie e' stata estesa):
  i numeri qui sono ricalcolati sui dati correnti, non copiati dallo spec.
- Numeri da distribuzione **storica netta**: le epoche vecchie usano lo spread attuale ->
  ottimistiche. Il forward log (`level_analyzer/signals_log.csv`) e' il vero giudice:
  **ri-stimare `f*` sui trade reali** appena ce n'e' massa.
- **Non ancora forward-tested**: finche' il forward non conferma, partire dal basso (es.
  0.5% per trade) e' difendibile; salire verso il tetto solo a edge confermato.
- Path su H1 (coarse): la varianza vera intra-trade puo' essere maggiore -> altra ragione per
  stare **sotto** il Kelly pieno.
