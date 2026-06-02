# Confluence Auto — Shadow run algoritmico

> **Sistema:** automatico · **Stato:** shadow run · **Habitat:** VPS Hetzner
> **Quant review:** — (tuning futuro) · **Fondamenti:** [liquidità/order flow (POC, S/D)](../../fondamenti_tecnici/02_liquidita_orderflow/)
> Indice: [strategies/README.md](../README.md) · Decisioni: [DECISIONS.md](../../DECISIONS.md)

Versione **algoritmica** della strategia Confluence Levels. Gira **in parallelo**
a quella manuale (vedi [`../confluence_levels/`](../confluence_levels/)): non
la sostituisce.

Idea:
- La Confluence manuale è umano-centrica, costosa (2-3h weekend), e settimane
  senza tempo = settimane senza copertura.
- I concetti S/R, S/D, POC sono in larga misura **matematicamente ricavabili**.
- Far girare entrambe permette: (1) copertura settimanale garantita,
  (2) dataset di confronto manuale vs algoritmico → nel lungo periodo affina
  la lettura dei livelli (Quant Reviewer Stage 2.7).

I livelli **Fibonacci restano manuali**: lo swing dominante è scelta
contestuale difficile da automatizzare.

## Architettura

```
strategies/confluence_auto/
├── config.yaml             # parametri detector (ZigZag thresh, ATR mult, windows)
├── data_source.py          # fetch MT5 (VPS) + yfinance (dev) fallback
├── detectors/
│   ├── sr.py               # swing pivots + clustering → support/resistance
│   ├── sd.py               # base-impulse-base → demand_zone/supply_zone
│   ├── poc.py              # Volume Profile rolling → POC/VAH/VAL/HVN/LVN
│   └── confluence.py       # merge cross-detector + marker confluence
├── writer.py               # emette levels_auto.yaml (formato loader-compatibile)
└── __main__.py             # CLI: generate, preview
```

Output: `../confluence_levels/levels_auto.yaml` — letto **insieme** a
`levels.yaml` dal runner Confluence esistente. Tutti gli ID hanno suffisso
`-AUTO` per distinguibilità nelle notifiche Telegram e nel journal.

## Quick start

```bash
# Dry-run (stampa, non scrive)
python -m strategies.confluence_auto preview --source yfinance

# Genera levels_auto.yaml reale
python -m strategies.confluence_auto generate --source yfinance

# Sul VPS dopo aver installato MetaTrader5:
python -m strategies.confluence_auto generate         # source=mt5 da config
```

Validare i livelli (sia manuali che auto, in un colpo):

```bash
python -m strategies.confluence_levels validate-levels
```

## Calibrazione dei parametri

I valori in [`config.yaml`](config.yaml) sono "calibrati a occhio" sui regimi
forex/XAU tipici. **Non sono ottimizzati**. Il Quant Reviewer
([`../../agents/quant_reviewer.md`](../../agents/quant_reviewer.md)) li tunerà
via PBO + walk-forward quando ci saranno abbastanza dati di confronto
manuale vs auto.

Parametri chiave:

| Detector | Parametro | Default | Note |
|---|---|---|---|
| S/R | `zigzag_threshold_atr_mult.d1` | 1.5 | swing significativo se > 1.5 × ATR_D1 |
| S/R | `cluster_width_pips.EURUSD` | 12 | pivot entro 12 pip vengono fusi |
| S/D | `base_range_atr_mult` | 0.5 | base = barre con range < 0.5 × ATR |
| S/D | `impulse_atr_mult` | 1.5 | impulse confirmation se range > 1.5 × ATR |
| POC | `n_bins` | 100 | risoluzione del Volume Profile |
| Conf | `min_detectors` | 2 | min nature diverse per emettere il livello |

## Comportamento osservato in v1 (yfinance dev locale 2026-05-25)

Smoke test ha rivelato:
- **S/D detector ritorna 0 livelli** sulla maggior parte dei simboli con dati
  yfinance. Il parametro `base_range_atr_mult: 0.5` è troppo stretto: su
  forex/XAU D1 le candele tipiche hanno range > 0.5 × ATR. Rilassare a 0.7 o
  0.8 quando si pulisce.
- **POC su forex yfinance è basato sul time-in-price**, non sul volume reale
  (yfinance forex non espone volume). Su MT5 + tick_volume sarà più
  informativo. POC su XAU (`GC=F` futures CME) ha volume reale, OK.
- **S/R + confluenza cross-detector funzionano**: 8 livelli AUTO EURUSD, 4
  AUTO XAUUSD da yfinance.

## Deploy sul VPS Hetzner

### 1. Installa MetaTrader5 Python

Sul VPS (assumendo MT5 terminal già installato e configurato col tuo account
MetaQuotes Demo):

```bash
ssh matteo@204.168.249.76
cd ~/trad
source venv/bin/activate
pip install MetaTrader5
```

Test connessione:

```bash
python -c "import MetaTrader5 as mt5; print(mt5.initialize()); print(mt5.terminal_info())"
```

### 2. Sync codice

Dal locale. **Importante**: PowerShell interpreta `\` come escape, usa forward
slash (preferito) oppure quota il path con apici singoli.

```powershell
scp -r strategies/confluence_auto matteo@204.168.249.76:~/trad/strategies/
scp strategies/confluence_levels/levels_loader.py matteo@204.168.249.76:~/trad/strategies/confluence_levels/
scp strategies/confluence_levels/strategy.py matteo@204.168.249.76:~/trad/strategies/confluence_levels/
scp strategies/confluence_levels/config.yaml matteo@204.168.249.76:~/trad/strategies/confluence_levels/
```

### 3. Cron — rigenerazione settimanale domenica sera

Sul VPS:

```bash
crontab -e
```

Aggiungi:

```cron
# Confluence Auto — rigenera levels_auto.yaml ogni domenica 21:00 UTC
# Output va a ~/trad/strategies/confluence_levels/levels_auto.yaml
# Il runner Confluence rilegge il file entro 60s (no restart necessario).
0 21 * * 0 cd ~/trad && /home/matteo/trad/venv/bin/python -m strategies.confluence_auto generate >> /var/log/confluence_auto.log 2>&1
```

Verifica il log dopo la prima esecuzione:

```bash
tail -50 /var/log/confluence_auto.log
sudo journalctl -u confluence -n 20 --no-pager   # heartbeat con nuovi livelli AUTO
```

### 4. Notion `Trading Journal` — tagging

Quando un trade viene eseguito su segnale Telegram con ID `*-AUTO`, marcare:
- **Account**: `MT5 Demo — Confluence Auto`
- **Strategia/Setup**: `Confluence Auto`

Così il Quant Reviewer mensile (Stage 2.7) può fare il diff con `Confluence Manual`.

## Vincoli operativi

- **NON promuovere mai una decisione di trade a un livello AUTO** senza
  controllo visuale almeno per le prime 4 settimane di shadow run. Il design
  è "raccolta dati", non "trade automatico".
- **Sample size**: servono >= 50 trade su livelli AUTO prima di qualunque
  conclusione statistica del Quant Reviewer.
- **Double counting con manuale**: se un livello AUTO coincide con uno
  manuale (entro proximity window), il runner manda 2 notifiche distinte
  (una per ID). Nel Notion vai a confermare/scartare a mano per le prime
  settimane. Politica futura (Stage 2.7): prevale il manuale, oppure il
  Quant Reviewer decide chi sopprimere.

## Riferimenti

- Wilder J.W. (1978) — *New Concepts in Technical Trading Systems* (ATR).
- Murphy J. (1999) — *Technical Analysis of the Financial Markets* (S/R clustering).
- Sam Seiden (Online Trading Academy) — methodology base-impulse-base S/D.
- Steidlmayer P. (1982) — *Markets and Market Logic* (Market Profile / POC).
- Project memory: [`project_confluence_auto.md`](../../../.claude/projects/c--Users-mmbus-Desktop-lavoro-trad/memory/project_confluence_auto.md).
- Roadmap context: [`ROADMAP.md`](../../ROADMAP.md) Stage 2.6 punto 4.
