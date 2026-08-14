"""Login/rinnovo della sessione Telethon del copier — da lanciare A MANO.

Le sessioni Telegram vengono revocate per inattivita': se `is_user_authorized()`
torna False, va rifatto il login. Questo script fa SOLO quello, senza avviare il
copier: piu' semplice da diagnosticare se qualcosa va storto.

DOVE ARRIVA IL CODICE
  Se hai gia' un'altra sessione attiva (telefono, Telegram Desktop), Telegram
  NON manda un SMS: il codice arriva come MESSAGGIO dentro Telegram, dalla chat
  ufficiale "Telegram" (spunta blu). Solo se non hai altre sessioni attive
  ripiega sull'SMS.

Il numero va in formato internazionale: +39XXXXXXXXXX

Uso (in un terminale INTERATTIVO, non da script):
    python -m signal_copier.login
"""
from __future__ import annotations

import asyncio
import os
import sys


def _load_env(path: str = ".env") -> dict:
    env = {}
    if not os.path.exists(path):
        return env
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


async def _run() -> int:
    env = _load_env()
    api_id = os.getenv("TELEGRAM_API_ID") or env.get("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH") or env.get("TELEGRAM_API_HASH")
    session = os.getenv("TELEGRAM_SESSION") or env.get("TELEGRAM_SESSION", "signal_copier")
    if not (api_id and api_hash):
        print("TELEGRAM_API_ID / TELEGRAM_API_HASH mancanti in .env")
        return 1

    from telethon import TelegramClient

    client = TelegramClient(session, int(api_id), api_hash)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Sessione GIA' valida: {me.first_name} (@{me.username}) — niente da fare.")
        await client.disconnect()
        return 0

    print("Sessione non autorizzata: procedo col login.\n")
    print("  Il codice NON arriva per SMS se hai altre sessioni attive:")
    print("  cerca la chat 'Telegram' (spunta blu) dentro l'app.\n")
    phone = input("Numero in formato internazionale (+39...): ").strip()
    try:
        await client.send_code_request(phone)
    except Exception as exc:  # flood wait, numero non valido, ecc.
        print(f"\nInvio codice fallito: {exc}")
        print("Se e' un FloodWaitError, aspetta il tempo indicato e riprova.")
        await client.disconnect()
        return 1

    code = input("Codice ricevuto: ").strip()
    try:
        await client.sign_in(phone, code)
    except Exception as exc:
        # Verifica in due passaggi attiva -> serve la password
        if "password" in str(exc).lower() or "2fa" in str(exc).lower():
            import getpass
            pwd = getpass.getpass("Password di verifica in due passaggi: ")
            await client.sign_in(password=pwd)
        else:
            print(f"\nLogin fallito: {exc}")
            await client.disconnect()
            return 1

    me = await client.get_me()
    print(f"\nOK: sessione creata per {me.first_name} (@{me.username}).")
    print(f"File: {session}.session  —  NON committarlo (e' gia' gitignored).")

    # Verifica che il canale del mentore sia effettivamente visibile.
    trovati = []
    async for d in client.iter_dialogs(limit=300):
        uname = (getattr(d.entity, "username", "") or "")
        if "XAU" in uname.upper() or "XAU" in d.name.upper():
            trovati.append(f"{d.name} (@{uname or 'n/d'})")
    print("\nCanali XAU visibili da questo account:")
    for t in trovati or ["  nessuno — verifica di essere iscritto al canale"]:
        print(f"  {t}")

    await client.disconnect()
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
