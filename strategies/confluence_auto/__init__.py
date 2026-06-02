"""Confluence Auto — versione algoritmica di Confluence Levels.

Genera `levels_auto.yaml` con livelli S/R, S/D, POC ricavati matematicamente
da barre OHLC (D1, H4 principalmente). Gira in parallelo a Confluence manuale
come shadow run (vedi project memory `project_confluence_auto.md`).

Componenti:
- `data_source`     → fetch OHLC da MT5 (VPS) o yfinance (dev locale).
- `detectors.sr`    → swing pivots + clustering → support/resistance.
- `detectors.sd`    → base-impulse-base → demand_zone/supply_zone.
- `detectors.poc`   → Volume Profile rolling → POC/VAH/VAL/HVN/LVN.
- `detectors.confluence` → merge cross-detector + assegnazione marker.
- `writer`          → emette `levels_auto.yaml` compatibile col loader.

CLI: `python -m strategies.confluence_auto generate`.
"""
