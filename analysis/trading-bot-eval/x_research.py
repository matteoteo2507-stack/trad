"""Bridge Grok/X (xAI Live Search) — estrae e sintetizza contenuti da X (Twitter).

Sostituisce lo stub `claude/agents/grok-x-researcher.md`: quello non era mai stato
attivato (tools vuoti, nessuna key). Questo script chiama xAI Grok con Live Search
su sorgente X e stampa una sintesi con citazioni.

Requisiti:
  - Aggiungi in .env (o come variabile d'ambiente):  XAI_API_KEY=...
    (Console: https://console.x.ai — pay-per-use, pochi cent per query.)
  - Opzionale: XAI_MODEL (default grok-4-latest), X_MAX_RESULTS (default 25).

Uso:
  python analysis/trading-bot-eval/x_research.py "la tua domanda di ricerca su X"
  # senza argomento usa la query di default sui livelli (POC/VWAP/liquidità/CVD).

In alternativa, come MCP registrato (se preferisci l'integrazione nativa Claude):
  claude mcp add grok --scope user --env "XAI_API_KEY=$XAI_API_KEY" -- npx -y grok-mcp
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

ENDPOINT = "https://api.x.ai/v1/chat/completions"

DEFAULT_QUERY = (
    "Sei un quant scettico. Cerca su X le pratiche dei trader SERI su livelli di "
    "prezzo intraday per XAUUSD, BTCUSD, EURUSD: volume profile (naked POC, HVN/LVN), "
    "anchored VWAP, liquidità (equal highs/lows, sweep), order flow (CVD/delta/absorption). "
    "Per ogni tecnica dimmi: (1) chi la usa con risultati credibili (account/thread + link), "
    "(2) come definiscono ENTRY/SL/TP e il BIAS al livello, (3) cosa è supportato da backtest "
    "vs hype, (4) errori comuni (look-ahead, sopravvivenza, drift scambiato per edge). "
    "Separa nettamente evidenza da marketing. Niente segnali, solo metodologia verificabile."
)


def load_key() -> str | None:
    key = os.environ.get("XAI_API_KEY")
    if key:
        return key.strip()
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("XAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    key = load_key()
    if not key:
        print("XAI_API_KEY mancante.\n"
              "  1) Crea una key su https://console.x.ai\n"
              "  2) Aggiungila in .env:  XAI_API_KEY=xai-...\n"
              "  3) Rilancia questo script (o registra l'MCP grok come da header).")
        return 2

    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    payload = {
        "model": os.environ.get("XAI_MODEL", "grok-4-latest"),
        "messages": [{"role": "user", "content": query}],
        "search_parameters": {
            "mode": "on",                       # forza la Live Search
            "sources": [{"type": "x"}],         # solo X/Twitter
            "max_search_results": int(os.environ.get("X_MAX_RESULTS", "25")),
            "return_citations": True,
        },
        "temperature": 0.2,
    }
    try:
        r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}",
                                             "Content-Type": "application/json"},
                          json=payload, timeout=120)
    except requests.RequestException as e:
        print("Errore di rete:", e)
        return 1
    if r.status_code != 200:
        print(f"xAI HTTP {r.status_code}: {r.text[:500]}")
        return 1
    data = r.json()
    msg = data["choices"][0]["message"]["content"]
    print("=" * 70)
    print("GROK / X — SINTESI")
    print("=" * 70)
    print(msg)
    cites = data.get("citations") or data["choices"][0].get("citations")
    if cites:
        print("\n--- CITAZIONI X ---")
        for c in cites:
            print("  ", c)
    usage = data.get("usage", {})
    if usage:
        print(f"\n[token: {usage}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
