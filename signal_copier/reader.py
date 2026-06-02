"""Reader dei messaggi: sorgente live (Telethon) e sorgente offline (file).

- `iter_offline_messages`: legge un file di esempi (messaggi separati da una riga
  di soli '='), per validare il parsing in dry-run senza credenziali Telegram.
- `TelegramReader`: si collega via Telethon (MTProto, account utente) e inoltra
  ogni nuovo messaggio dei canali configurati a una callback.

Telethon è importato pigramente: il modulo resta importabile (e testabile) anche
dove la libreria non è installata, come per `MetaTrader5`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Iterator

logger = logging.getLogger(__name__)

# Separatore tra messaggi distinti nel file di esempi.
_MSG_SEP = "==="


def iter_offline_messages(path: str | Path) -> Iterator[str]:
    """Itera i messaggi da un file di esempi.

    Formato: messaggi separati da una riga che inizia con '==='. I blocchi vuoti
    vengono saltati. Utile per il dry-run del parser sui messaggi reali.
    """
    text = Path(path).read_text(encoding="utf-8")
    block: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith(_MSG_SEP):
            msg = "\n".join(block).strip()
            if msg:
                yield msg
            block = []
        else:
            block.append(line)
    tail = "\n".join(block).strip()
    if tail:
        yield tail


def _import_telethon() -> Any:
    """Import pigro di Telethon con messaggio diagnostico se mancante."""
    try:
        from telethon import TelegramClient, events  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Pacchetto `telethon` non installato. Eseguire `poetry add telethon`."
        ) from exc
    return TelegramClient, events


class TelegramReader:
    """Legge i canali Telegram via account utente e inoltra i messaggi.

    `channel_map` mappa l'identificatore Telegram del canale (username senza @,
    es. "XAUUSD_AnalysisLab", o l'id numerico) al `channel_id` del parser.
    `on_message(channel_id, text)` viene chiamata per ogni nuovo messaggio.
    """

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session: str,
        channel_map: dict[str, str],
        on_message: Callable[[str, str], None],
    ):
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.session = session
        self.channel_map = channel_map
        self.on_message = on_message
        self._client: Any = None

    def run(self) -> None:
        """Avvia il client e resta in ascolto (bloccante) fino a disconnessione."""
        TelegramClient, events = _import_telethon()
        self._client = TelegramClient(self.session, self.api_id, self.api_hash)

        # Lista dei canali da osservare (chiavi della mappa).
        watched = list(self.channel_map.keys())

        @self._client.on(events.NewMessage(chats=watched))
        async def _handler(event: Any) -> None:  # noqa: ANN001
            text = event.message.message or ""
            channel_id = self._resolve_channel(event)
            if channel_id is None:
                return
            try:
                self.on_message(channel_id, text)
            except Exception as exc:  # non far cadere il client per un parse error
                logger.exception("on_message ha sollevato: %s", exc)

        logger.info("TelegramReader avviato su canali: %s", watched)
        with self._client:
            self._client.run_until_disconnected()

    def _resolve_channel(self, event: Any) -> str | None:
        """Risolve il `channel_id` del parser dal messaggio Telethon."""
        chat = event.chat
        username = getattr(chat, "username", None)
        if username and username in self.channel_map:
            return self.channel_map[username]
        chat_id = str(getattr(chat, "id", ""))
        return self.channel_map.get(chat_id)
