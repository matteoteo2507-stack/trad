---
name: telegram-notifier
description: Inviare segnali di trading via Telegram o configurare il bot. Usare quando si vuole notificare un segnale semiautomatico, configurare il bot Telegram, modificare il template di messaggio, o testare la connessione.
---

# Skill — Telegram Notifier

Invia notifiche di trading all'utente via Telegram. Canale principale per le strategie
**semiautomatiche**: il sistema rileva un setup → invia il segnale → Matteo piazza l'ordine
manualmente (anche pending).

## Configurazione iniziale (una tantum)

1. Crea il bot tramite [@BotFather](https://t.me/BotFather) su Telegram. Ottieni il `BOT_TOKEN`.
2. Manda un messaggio qualsiasi al bot per attivare la chat.
3. Recupera il `CHAT_ID`:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
   Cerca `"chat":{"id": ...}` nella risposta.
4. Inserisci `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` nel file `.env` (vedi `.env.example`).

## Formato standard del messaggio (signal di trading)

```
🟢 BUY <SIMBOLO>
Strategia: <nome_strategia>
Timeframe: <tf>

📍 Entry: <prezzo_entry>
🛑 SL:    <prezzo_stop_loss>  (-<pip/%>)
🎯 TP:    <prezzo_take_profit>  (+<pip/%>)

💰 Size: <size_consigliata>
⏱  Validità: <durata_segnale_in_minuti>

Ratio R/R: <reward/risk>
Confidence: <0-100>%

[Riferimento al setup, link al grafico se disponibile]
```

Per `SELL` cambiare emoji (🔴) e direzione.

Per segnali di **uscita anticipata** (es. cambio di scenario macro che invalida la strategia):

```
⚠️ EXIT <SIMBOLO>
Strategia: <nome_strategia>
Motivo: <descrizione_breve>
Posizione da chiudere: <descrizione>
```

## Workflow di una notifica

1. La strategia genera un `Signal` (vedi `notifiers/base.py`).
2. Il signal passa attraverso il **risk gate** (`config/risk.yaml`):
   - se la size eccede la soglia → ridotta o segnale skippato;
   - se il drawdown corrente eccede il limite → tutti i segnali bloccati.
3. Il signal validato viene formattato e inviato.
4. Logging completo in `logs/telegram.log` con timestamp + esito invio.

## Comandi del bot (Stage 5+)

Quando Stage 5 sarà attivo, il bot dovrà rispondere ad alcuni comandi base:

- `/status` → stato del sistema, strategie attive, P&L corrente.
- `/disable <strategia>` → sospendere temporaneamente una strategia.
- `/enable <strategia>` → riattivarla.
- `/risk` → mostrare i parametri di rischio correnti.

Per Stage 2 questi non sono obbligatori — basta l'invio outbound.

## Vincoli

- Mai inviare credenziali, API key, o saldi assoluti del conto via Telegram.
- Rate limit: 30 messaggi/secondo verso Telegram, abbondantemente sotto la nostra esigenza.
- Se l'invio fallisce: retry 3 volte con backoff esponenziale, poi log errore + (opzionale) fallback su email.

## Riferimenti

- `notifiers/base.py` — interfaccia `NotifierBase`.
- `notifiers/telegram.py` — implementazione.
- `.env.example` — variabili `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Libreria: `python-telegram-bot` (in `pyproject.toml`).
- Stage 2 della roadmap.
