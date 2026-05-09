# notifiers/

Canali di notifica verso l'utente. Telegram è il canale principale per le strategie semiautomatiche.

## Pattern

Tutte le implementazioni ereditano da `NotifierBase` (`base.py`). L'interfaccia minima:

| Metodo | Cosa fa |
|---|---|
| `send_signal(signal)` | Invia un signal di trading formattato |
| `send_message(text)` | Invia un messaggio di testo arbitrario (per status, errori, status check) |
| `send_exit_alert(symbol, reason)` | Invia alert di uscita anticipata |

## Implementazioni

- `telegram.py` → Stage 2.

## Configurazione

Vedi `.env.example` per `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.
Vedi anche la skill `skills/telegram-notifier/SKILL.md` per il flusso completo.
