# config/

File YAML di configurazione del sistema. Tutto qui — niente valori magici nel codice.

## File

- `risk.yaml` — Parametri di rischio globali (max drawdown, max size per trade, ecc.).
- `markets.yaml` — Mercati abilitati per scopo, regole condizionate ai signal worldmonitor (Stage 5).

## Convenzione

I parametri sono letti dal codice via `pyyaml`. Le strategie hanno il proprio `config.yaml`
nella loro cartella; questi qui sono **globali**.
