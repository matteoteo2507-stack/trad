# TSMOM — Time Series Momentum

> **Sistema:** automatico · **Stato:** **NO-GO / stub** · **Habitat:** (Python)
> **Quant review:** [tsmom_jpy-2026-05-29](../../docs/reviews/tsmom_jpy-2026-05-29.md) → **NO-GO** (DSR≈0, dati insufficienti single-asset) · **Fondamenti:** [quant](../../fondamenti_tecnici/04_quant_metodologia/), [regimi/macro](../../fondamenti_tecnici/03_regimi_macro/)
> Indice: [strategies/README.md](../README.md) · Decisioni: [DECISIONS.md](../../DECISIONS.md). Rivalutabile solo multi-asset.

Strategia automatica D1 su USDJPY (e altri major). Replica della logica di
Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum" *Journal of Financial
Economics* 104(2), con sizing vol-target nel solco di Harvey-Hoyle-Korgaonkar
(JPM 2018).

## Logica

A ogni close D1:

1. `s_long = sign(close - close[lookback_long_bars])` (default 252 barre ≈ 1
   anno).
2. `s_fast = sign(EWMA(close, 20) - EWMA(close, 60))`.
3. `pos = s_long` se concorde con `s_fast`, altrimenti `0` (flat).
4. **Entry**: open della barra successiva quando `pos` cambia rispetto a
   `pos_prev`.
5. **Stop loss**: `entry ± 3 × ATR(20)` al momento del fill.
6. **Exit**: signal flip (`pos` cambia segno) → close al close della barra
   del flip. O SL hit.

## Sizing — vol-targeting

```
size_factor = vol_target_annual / realized_vol_60d_annual
            (capped a size_cap_mult, default 3.0)
risk_money = equity * account_risk_pct * size_factor
units      = risk_money / sl_distance
```

Coerente con Harvey, Hoyle, Korgaonkar (2018): il vol-targeting riduce il
tail risk e migliora lo Sharpe di +0.1-0.3 vs sizing costante.

## Edge atteso (paper)

- Sharpe annuo: **0.7-1.0** su singolo asset D1, 1.0-1.4 su portafoglio
  cross-asset.
- Frequenza: 4-8 trade/mese (signal flip).
- Max DD: 15-25%, time-under-water possibilmente lungo (mesi).
- **Decay post-2008 documentato**: applicare cautela sul sub-sample
  più recente (Baltas-Kosowski 2020).

## Uso

```bash
# Backtest 5 anni su USDJPY (yfinance)
python -m strategies.tsmom backtest --symbol USDJPY=X --years 5

# Backtest da CSV custom (export MT5)
python -m strategies.tsmom backtest --csv data/usdjpy_d1.csv --years 5

# Salva curve di equity
python -m strategies.tsmom backtest --years 8 --save-trades output/equity.csv
```

Output: Sharpe, Sortino, max DD, Calmar, skew/kurt, CVaR, **DSR** e
**MC permutation p-value** (vedi [core/quant_metrics.py](../../core/quant_metrics.py)).

## Quant review

Per la review formale (PBO via CSCV, walk-forward, White's Reality Check
su varianti), invoca la skill `/quant-review`:

```
/quant-review strategies/tsmom/
```

Il reviewer ti chiederà:
1. Backtest baseline (config attuale).
2. ≥ 3 varianti di parametri vicini per costruire la matrice CSCV.
3. Trade log live (se disponibili) per validazione OOS pura.

Verdict atteso a config default su 5 anni USDJPY: **RAFFINA** (Sharpe
verosimilmente sotto 0.7 per via di costi e regime FED 2024-2026), da
combinare con altri asset per portfolio TSMOM (Stage 3+).

## Configurazione

Vedi [config.yaml](config.yaml). Parametri rilevanti:

- `signal.lookback_long_bars` (252 default)
- `signal.ewma_fast` / `signal.ewma_slow` (20 / 60)
- `stop_loss.atr_period` / `atr_mult` (20 / 3.0)
- `sizing.vol_target_annual` (0.15)
- `costs.*` per realismo del backtest (popolare con spread broker reale)

## Roadmap

- **Stage 2.6**: backtest validato → deploy in `notify_only` su VPS Hetzner
  insieme al runner Confluence. Notifica Telegram a ogni signal flip.
- **Stage 3**: porting a backtester pluralistico (vectorbt + custom + ai-hedge-fund)
  per confronto cross-engine.
- **Futuro**: estensione multi-asset (USDJPY + EURUSD + GBPUSD + XAU) per
  portfolio TSMOM con vol-targeting al livello portafoglio.

## Riferimenti

- Moskowitz, Ooi, Pedersen (2012) — *Time Series Momentum*. JFE 104(2).
- Hurst, Ooi, Pedersen (2017) — *A Century of Evidence on Trend-Following
  Investing*. AQR.
- Harvey, Hoyle, Korgaonkar et al. (2018) — *The Impact of Volatility
  Targeting*. JPM.
- Baltas, Kosowski (2020) — *Demystifying Time-Series Momentum Strategies*.
