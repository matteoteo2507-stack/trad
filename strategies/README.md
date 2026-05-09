# strategies/

Strategie meccaniche di trading. Una cartella per strategia.

**Trading meccanico**: niente LLM nel loop di decisione. Le regole sono completamente codificate
e deterministiche.

## Struttura di una strategia

```
strategies/<nome_strategia>/
├── strategy.py       # Classe che eredita da StrategyBase
├── config.yaml       # Parametri (size, soglie, timeframe)
└── README.md         # Cosa fa, ipotesi, riferimenti teorici
```

## Strategie pianificate

| Stage | Strategia | Mercato | Stato |
|---|---|---|---|
| 1 | `stock_selector` | SP500 (paper IBKR) | Pianificata (porting del notebook V6.0) |
| 2 | TBD — basata su confluence o candle structures | MT5 demo (forex) | Pianificata |
| 6 | TBD — quant crypto | Coinbase/Binance live | Pianificata |

## Come creare una nuova strategia

1. Copia `_template/` in `<nome_strategia>/`.
2. Compila il `README.md` (ipotesi, regole, fonte teorica).
3. Implementa `strategy.py`:
   - `should_enter(market_data) -> Optional[Signal]`
   - `should_exit(market_data, position) -> bool`
   - `get_required_data() -> DataRequirement`
4. Riempi `config.yaml` con i parametri numerici.
5. Test minimo in `tests/test_<nome_strategia>.py`.
6. Backtest via skill `backtest-runner`.
7. Validazione paper / demo.
8. Promozione a produzione (richiede commit dedicato + risk gate verificato).

Vedi `CONVENTIONS.md` (top level) per il dettaglio del pattern.
