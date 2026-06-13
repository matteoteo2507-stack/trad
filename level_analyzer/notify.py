"""Notifica Telegram (opzionale) + formattazione messaggio. Nessun ordine, solo avviso."""
from __future__ import annotations

import os
from pathlib import Path


def _token(env_name: str = "TELEGRAM_BOT_TOKEN") -> str | None:
    tok = os.environ.get(env_name)
    if tok:
        return tok.strip()
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(env_name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def format_signal(sig: dict, asset: str, price: float, note: str = "") -> str:
    arrow = "🟢 LONG" if sig["side"] == "long" else "🔴 SHORT"
    msg = (f"{arrow}  {asset}  (zona conf=2)\n"
           f"Zona: {sig['zone']}  ({', '.join(sig['types'])})\n"
           f"Prezzo: {price}  (dist {sig['dist']} ≈ {sig['dist_atr']} ATR)\n"
           f"SL: {sig['sl']}   TP: {sig['tp']}   RR 1:{sig['rr']}\n"
           f"— Fase A: valuta e piazza a mano (pending/market). Non automatico.")
    if note:
        msg += f"\n⚠️ {note}"
    return msg


def send_telegram(chat_id: str, text: str, token_env: str = "TELEGRAM_BOT_TOKEN") -> bool:
    tok = _token(token_env)
    if not tok or not chat_id:
        return False
    import requests
    try:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                          json={"chat_id": chat_id, "text": text}, timeout=20)
        return r.status_code == 200
    except requests.RequestException:
        return False
