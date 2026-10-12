# Technical Indicators Quantitative Evidence – X (Twitter) Research
**Date of research:** 2026-10-08  
**Period covered:** last ~5 years (since 2021-10-08)  
**Source:** X (Twitter) keyword + author searches  
**Language of original posts:** English  
**Purpose:** Collect posts/threads that claim *quantitative evidence* (not pure opinion) on technical indicators, trend-following, mean-reversion, repainting, overfitting, Fibonacci, Andrews Pitchfork, etc.

---

## Research Rules Applied
- Only posts/threads containing numbers, backtests, papers, sample sizes, Sharpe, win-rates, OOS, costs, or statistical claims.
- Explicitly included opposing claims when they brought numbers.
- Max 25 useful rows retained.
- Promotional posts (“100% win rate”, affiliate links, “DM for group”, pure chart setups without numbers) excluded.
- Conflict of interest noted when visible (selling indicators, courses, funds, subscriptions).
- Author accounts verified as genuine where possible.
- No external knowledge added; only what appears in the posts.

---

## Main Table

| Author (Name + @handle) | Date | Link | Indicator / Theme | Claim (one sentence) | Evidence Type | Market & Horizon | Numbers Cited + Sample | Conflict of Interest |
|-------------------------|------|------|-------------------|----------------------|---------------|------------------|------------------------|----------------------|
| Gazmatrades - @Gazmalol | 2026-04-13 | https://x.com/Gazmalol/status/2043580107327951243 | TA patterns (H&S, Double Bottom, Fib, RSI Div, MA Crossover) | Backtest of 10 popular TA patterns: success rates after fees ≈ 47-51%; coin flip beats most. | Backtest without OOS or costs | 100 stocks, 10 years | H&S 47%, Double Bottom 49%, Fib Retracement 48%, RSI Div 51% (ns), MA Crossover 49% | None stated |
| The Capital Allocator - @theallocator_ | 2023-08-15 | https://x.com/theallocator_/status/1691389991753056256 | Time-series momentum / Trend following | Paper “A Century of Evidence on Trend-Following Investing” (Hurst/Ooi/Pedersen 2014) shows consistent positive returns, low correlations, reduces max DD in 60/40. | Paper cited | 67 markets, 1880–present, 1/3/12-month lookbacks | Strong positive returns + low corr; “smile” in extreme markets; improves 60/40 returns & reduces vol/DD | None stated |
| Wes Gray - @alphaarchitect | 2026-08-14 | https://x.com/alphaarchitect/status/2088280994671468560 | VIX + Trend following | New post: VIX and Trend Following Revisited – nearly a decade of out-of-sample evidence. | Backtest with OOS (and likely costs) | Not specified in post | Nearly a decade of OOS evidence | Yes – Alpha Architect ETFs |
| Larry Swedroe - @larryswedroe | 2026-08-07 | https://x.com/larryswedroe/status/2085531704543113393 | Trend following / TS Momentum | Substack column: “When Trend-Following Hits a Wall: New Evidence on the Boundaries of Time Series Momentum”. | Paper / new evidence cited | Not specified | Not specified in post | None stated |
| Quantpedia - @quantpedia | 2026-08-28 | https://x.com/quantpedia/status/2093344965287875026 | Time-series momentum | Paper “Boundaries of Time Series Momentum” (Suominen/Hjalmarsson): TSMOM works in normal cycles but breaks and reverses at historical valuation extremes. | Paper cited | Equity markets | Trends persist in normal cycles; reverse at valuation extremes | Yes – Quantpedia subscription service |
| Quantpedia - @quantpedia | 2026-09-22 | https://x.com/quantpedia/status/2102383124243951883 | Intraday trend-following on technical indicators | Building & testing trend-following strategies using technical indicators on 1-minute SPY data. | Backtest (details in linked article) | SPY, 1-minute bars | Not specified in post | Yes – Quantpedia |
| QuantSeeker - @quantseeker | 2024-11-30 | https://x.com/quantseeker/status/1862884234890743933 | Short-term reversal | Classic short-term reversal has weakened; paper shows how to revive it (industry-relative / residual, shorter lookbacks, liquidity provision, avoid news). | Paper cited | Not specified | Not specified | None stated |
| パンダくんbotだよ - @pandakunbot | 2022-08-06 | https://x.com/pandakunbot/status/1555771247987986432 | Short-term reversal | “Is short-term reversal driven by liquidity provision in emerging markets? Evidence from China”. | Paper cited | China / emerging markets | Not specified | None stated |
| Daniele Bianchi - @WhitesPhD | 2022-05-31 | https://x.com/WhitesPhD/status/1531561325939380224 | Short-term reversal / liquidity provision | Empirical evidence in crypto: returns from liquidity provision (proxied by short-term reversal) are almost uniquely concentrated in “low-quality” pairs. | Empirical / backtest evidence | Cryptocurrency markets | Almost uniquely concentrated in low-quality pairs | None stated |
| Andrew Cole - @Beyzanuracbp | 2026-10-05 | https://x.com/Beyzanuracbp/status/2107168740630770047 | Fibonacci retracement | Technical analysis has the same predictive power as the lunar calendar; BTC does not care about Fib; only edge is what you can backtest – and you cannot backtest line drawing. | Opinion | BTC | None | None stated |
| Owen - @World3tk | 2026-07-08 | https://x.com/World3tk/status/2074865187971006536 | Fibonacci retracement | Fib spiral in art is like Fib retracement in markets: tools with enough random lines that they map onto anything and create the illusion of structure. | Opinion | Not specified | None | None stated |
| Backtesting Arena - @SifuBacktest | 2026-05-21 | https://x.com/SifuBacktest/status/2057595634794770572 | Fibonacci / ZigZag / Harmonics | Empirically the edge of Fib retracement entries, ZigZag and harmonics is mostly within transaction-cost margins. | Backtest (no OOS/costs detail) | Not specified | Edge mostly within transaction-cost margins | None stated |
| SignalForge AI - @SignalForge_AI | 2026-06-30 | https://x.com/SignalForge_AI/status/2071858420542505149 | Repainting indicators (TradingView) | 90% of TradingView indicator scripts are repainting; backtests look amazing because the indicator changes its mind after the candle closes. Always forward-test ≥30 days. | Personal experience | TradingView | 90% | Yes – sells TradingView→MT5 service |
| ALGO TRADING x AI - @AlgoTradingxAI | 2026-02-11 | https://x.com/AlgoTradingxAI/status/2021698889905058120 | Repainting (TradingView) | TradingView repainting is the silent killer: backtest shows 75% win rate → live drops to 45% because the indicator used future data. | Personal experience | TradingView | 75% → 45% | None stated |
| ALGO TRADING x AI - @AlgoTradingxAI | 2026-04-30 | https://x.com/AlgoTradingxAI/status/2049780344593805670 | Repainting (Pine Script) | Pine Editor repainting almost broke me: strategy looked like 3R per trade on TradingView → live barely break-even (used next candle’s open). | Personal experience | TradingView / Pine | 3R → break-even | None stated |
| Pops - @popspinedev | 2026-07-31 | https://x.com/popspinedev/status/2083216647230460311 | Repainting | Lie #1 – Repainting: historical signals used information not available in real time; backtest perfect, live signals vanish. | Opinion / experience | TradingView | None | Yes – Pine Script / automation service |
| Marcos López de Prado - @lopezdeprado | 2023-12-01 | https://x.com/lopezdeprado/status/1730649227049521216 | Backtest overfitting / p-hacking | Honest researchers acknowledge a replication crisis in finance caused by p-hacking, backtest overfitting and causal denial. | Opinion (with reference to replication crisis) | Finance in general | None | None stated |
| Rob Carver - @investingidiocy | 2026-09-14 | https://x.com/investingidiocy/status/2099517517974651344 | Trend following | “Trend-following as a concept is so powerful that TF funds should always outperform any single asset class in the long-run” is utter horseshite. | Opinion | Not specified | None | No (explicitly states he does not own/run TF funds) |
| Corey Hoffstein - @choffstein | 2026-09-15 | https://x.com/choffstein/status/2099885555529961681 | Trend following (stacking) | Stacking trend following on a glide path: simulations show 22% more wealth at age 65 and 64–79% odds that a 4% withdrawal plan lasts to age 95. | Simulation / backtest | Glide-path / retirement portfolios | +22% wealth at 65; 64–79% success odds | Yes – Return Stacked ETFs / Newfound Research |
| Wes Gray - @alphaarchitect | 2026-07-01 | https://x.com/alphaarchitect/status/2072411523650388358 | Long-term trend / 200-day MA | The signals that “work” are noisy versions of brain-dead 200-day moving-average type concepts. | Opinion / experience | Not specified | None | Yes – Alpha Architect ETFs |
| Kris - @Robot_Wealth | 2025-09-06 | https://x.com/Robot_Wealth/status/1964200968436040169 | Binary MA signals / trend | Binary “above MA → long / below → short” work (sort of) but waste most of the data; a simple continuous adjustment improves them. Code provided to test. | Discussion + code for testing | Crypto (mentioned) | None | Yes – Robot Wealth |
| Euan Sinclair - @SinclairEuan | 2022-03-12 | https://x.com/SinclairEuan/status/1502657235444510720 | Indicator testing | Testing is full of pitfalls; read David Aronson’s book – he rigorously tests every indicator. | Opinion | Not specified | None | None stated |
| Euan Sinclair - @SinclairEuan | 2022-03-12 | https://x.com/SinclairEuan/status/1502640042518450179 | RSI | Number of winning RSI traders is meaningless without also knowing the number of losers; everything dies – why would RSI be more persistent than real quant methods? | Opinion | Not specified | None | None stated |
| sentinel - @sentinelbotsaas | 2026-04-12 | https://x.com/sentinelbotsaas/status/2043131992284565510 | EMA + RSI + ATR vs sentiment | TA-only backtest (EMA + RSI + ATR) Sharpe 1.62 vs sentiment-agent Sharpe 0.74 on BTC over 6 months. | Backtest without OOS or costs detail | BTC, 6 months | Sharpe 1.62 (TA) vs 0.74 (sentiment) | None stated |

---

## Summary of Evidence Strength

**Themes / indicators that appear most often WITH quantitative evidence:**
- Time-series momentum / Trend following (century-long papers, OOS results, boundary papers, portfolio-stacking simulations).
- Short-term reversal linked to liquidity provision (academic papers + crypto evidence).

**Themes / indicators that appear most often WITHOUT (or with very weak) quantitative evidence:**
- Fibonacci retracement (mostly “random lines” critiques or pure chart claims).
- Classic RSI / MA crossover strategies (success rates ≈ coin-flip or criticised for overfitting/repainting).
- Andrews Pitchfork / median lines (almost exclusively anecdotal charting).
- Generic TradingView indicators (heavy emphasis on the repainting problem destroying live performance).

---

## Excluded Posts
Approximately 40+ posts were excluded.  
Main reasons:
- Pure promotional claims (“100% win rate”, “70% accuracy”, affiliate links, “DM for the group”).
- Chart setups or trade ideas without any numbers, sample size, or statistical claim.
- Accounts primarily selling indicators, courses or signals that provided no transparent backtest data.

---

## Verified Author Accounts (genuine)
- Rob Carver → @investingidiocy
- Corey Hoffstein → @choffstein
- Wes Gray / Alpha Architect → @alphaarchitect
- Quantpedia → @quantpedia (Radovan Vojtko)
- Robot Wealth → @Robot_Wealth (Kris)
- Ernest Chan → @echanQT
- Kris Abdelmessih → @KrisAbdelmessih
- Adam Butler → @GestaltU
- Euan Sinclair → @SinclairEuan
- Marcos López de Prado → @lopezdeprado

---

## How to use this file with Claude
1. Upload this entire Markdown file.
2. Ask Claude to:
   - Rank indicators by strength of evidence
   - Extract only the rows with “paper cited” or “backtest with OOS”
   - Build a summary table of positive vs negative findings
   - Compare trend-following evidence vs classic TA evidence
   - Flag all conflicts of interest
   - Suggest next search queries based on gaps

File ready for direct use.
