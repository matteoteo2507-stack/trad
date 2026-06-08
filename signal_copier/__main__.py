"""CLI del signal copier.

Uso:
    # Dry-run sui messaggi di esempio (nessuna credenziale, nessun ordine):
    python -m signal_copier dryrun --channel xauusd_analysislab \
        --samples signal_copier/samples/xau_analysis_lab.txt

    # Live (richiede .env con TELEGRAM_API_ID/HASH e MT5_DEMO*_):
    python -m signal_copier live --mode live

Il dry-run è il percorso per validare il parsing prima del live.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

from .executor import Executor
from .journal import TradeJournal
from .models import EntryTrigger, ParsedSignal, SignalUpdate
from .parsers import get_parser
from .planner import build_market_plan, build_plan
from .reader import TelegramReader, iter_offline_messages

logger = logging.getLogger("signal_copier")

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _setup_logging() -> None:
    # Console Windows (cp1252) va in UnicodeEncodeError sulle emoji/frecce dei
    # messaggi: forziamo UTF-8 su stdout/stderr (no-op se già utf-8 o non supportato).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not root.handlers:
        stream_h = logging.StreamHandler()
        stream_h.setFormatter(fmt)
        root.addHandler(stream_h)
        # Log persistente su file (UTF-8): la console si perde, questo no. Serve a
        # ricostruire cosa è arrivato dai canali anche dopo (forensics + dataset).
        try:
            Path("logs").mkdir(exist_ok=True)
            file_h = logging.FileHandler("logs/signal_copier.log", encoding="utf-8")
            file_h.setFormatter(fmt)
            root.addHandler(file_h)
        except OSError as exc:
            root.warning("Impossibile aprire logs/signal_copier.log: %s", exc)


def _log_raw_message(channel_id: str, text: str, raw_log: Path) -> None:
    """Append-only del messaggio grezzo ricevuto (audit + dataset reverse-eng.)."""
    import json
    from datetime import datetime, timezone

    rec = {"ts": datetime.now(timezone.utc).isoformat(), "channel": channel_id, "text": text}
    try:
        with open(raw_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.warning("Scrittura messaggio grezzo fallita: %s", exc)


def _load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dispatch(parser: Any, executor: Executor, copier_cfg: dict, balance: float,
              text: str, broker: Any = None) -> None:
    """Parsa un messaggio e instrada il risultato all'executor.

    Flusso del canale: trigger "BUY/SELL NOW" → apri a mercato; messaggio coi
    livelli → riconcilia SL/TP sulle gambe aperte; TP/close → gestione.
    Logga OGNI messaggio e la sua classificazione, così in dry-run si vedono
    anche gli ignorati e si scoprono i falsi negativi del parser.
    """
    preview = " ".join(text.split())[:120]
    result = parser.parse(text)

    if isinstance(result, EntryTrigger):
        if broker is None:
            logger.info("Messaggio → TRIGGER %s %s (dry-run: nessuna esecuzione): %s",
                        result.symbol, result.side, preview)
            return
        # Policy "uno per simbolo" + flip su cambio bias (chiude il vecchio se opposto).
        if not executor.prepare_for_new_trade(result.symbol, result.direction):
            logger.info("Messaggio → TRIGGER %s %s IGNORATO (re-entry stesso bias): %s",
                        result.symbol, result.side, preview)
            return
        try:
            price = broker.get_price(result.symbol)
        except Exception as exc:
            logger.warning("get_price fallito, trigger %s %s saltato: %s",
                           result.symbol, result.side, exc)
            return
        logger.info("Messaggio → TRIGGER %s %s @mercato %.2f", result.symbol, result.side, price)
        plan = build_market_plan(result, price, balance, copier_cfg)
        executor.on_signal(plan)

    elif isinstance(result, ParsedSignal):
        if getattr(parser, "entry_mode", "trigger") == "signal":
            # Canale "signal": livelli tutto-in-uno → apri a mercato direttamente.
            if not executor.prepare_for_new_trade(result.symbol, result.direction):
                logger.info("Messaggio → SEGNALE %s %s IGNORATO (re-entry stesso bias): %s",
                            result.symbol, result.side, preview)
                return
            current_price = None
            if broker is not None:
                try:
                    current_price = broker.get_price(result.symbol)
                except Exception as exc:
                    logger.warning("get_price fallito, gate anti-ritardo off: %s", exc)
            logger.info("Messaggio → SEGNALE %s %s (apre a mercato): %s",
                        result.symbol, result.side, preview)
            plan = build_plan(result, balance, copier_cfg, current_price=current_price)
            executor.on_signal(plan)
        else:
            # Canale "trigger": i livelli riconciliano il trade già aperto dal "NOW".
            logger.info("Messaggio → LIVELLI (riconcilio): %s", preview)
            executor.on_reconcile(result)

    elif isinstance(result, SignalUpdate):
        logger.info("Messaggio → UPDATE[%s]: %s", result.kind, preview)
        executor.on_update(result)

    else:
        logger.info("Messaggio ignorato (nessun parse): %s", preview)


# ---------------------------------------------------------------------------
# Comando: dryrun
# ---------------------------------------------------------------------------


def cmd_dryrun(args: argparse.Namespace) -> int:
    config = _load_config()
    copier_cfg = config["copier"]

    parser = get_parser(args.channel)
    if parser is None:
        logger.error("Nessun parser registrato per channel_id=%s", args.channel)
        return 2

    balance = args.balance if args.balance else float(copier_cfg.get("account_balance_hint", 10000))
    # Dry-run su esempi offline: journal separato (dati di test, non reali).
    base = Path(config.get("journal_file", "logs/signal_copier_journal.jsonl"))
    journal = TradeJournal(base.with_name(base.stem + "_dryrun" + base.suffix))
    executor = Executor(mode="dry_run", config=copier_cfg, journal=journal)

    n = 0
    for text in iter_offline_messages(args.samples):
        n += 1
        _dispatch(parser, executor, copier_cfg, balance, text)
    logger.info("Dry-run completato: %d messaggi processati (balance=%.0f)", n, balance)
    return 0


# ---------------------------------------------------------------------------
# Comando: live
# ---------------------------------------------------------------------------


def cmd_live(args: argparse.Namespace) -> int:
    from dotenv import load_dotenv

    load_dotenv()
    config = _load_config()
    copier_cfg = config["copier"]
    mode = args.mode

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session = os.getenv("TELEGRAM_SESSION", "signal_copier")
    if not api_id or not api_hash:
        logger.error("TELEGRAM_API_ID / TELEGRAM_API_HASH mancanti in .env")
        return 2

    broker = None
    if mode == "live":
        broker = _build_broker(config["broker_account"], copier_cfg)
        broker.connect()

    # Canale reale (sia in dry_run che in live): journal principale.
    # Il campo `mode` di ogni record distingue ascolto-osservativo da esecuzione.
    journal = TradeJournal(config.get("journal_file", "logs/signal_copier_journal.jsonl"))
    executor = Executor(mode=mode, broker=broker, config=copier_cfg, journal=journal)

    raw_log = Path(config.get("raw_message_log", "logs/messages_received.jsonl"))
    raw_log.parent.mkdir(parents=True, exist_ok=True)

    def on_message(channel_id: str, text: str) -> None:
        # Prima di tutto: persisti il messaggio grezzo (anche se il parser lo ignora).
        _log_raw_message(channel_id, text, raw_log)
        parser = get_parser(channel_id)
        if parser is None:
            logger.warning("Messaggio da canale senza parser: %s", channel_id)
            return
        balance = float(copier_cfg.get("account_balance_hint", 10000))
        if broker is not None:
            try:
                balance = broker.get_info().equity
            except Exception as exc:
                logger.warning("get_info fallito, uso hint: %s", exc)
        _dispatch(parser, executor, copier_cfg, balance, text, broker=broker)

    # Gestione guidata dal broker (BE/trailing indipendenti dai messaggi): solo in live.
    on_tick = executor.poll_broker_management if mode == "live" else None
    poll_seconds = float(copier_cfg.get("manage", {}).get("poll_seconds", 20))

    reader = TelegramReader(
        api_id=int(api_id),
        api_hash=api_hash,
        session=session,
        channel_map=config["channels"],
        on_message=on_message,
        on_tick=on_tick,
        tick_interval=poll_seconds,
    )
    reader.run()
    return 0


def _build_broker(prefix: str, copier_cfg: dict) -> Any:
    """Costruisce un MT5Broker dalle env MT5_<prefix>_LOGIN/PASSWORD/SERVER."""
    from brokers.mt5 import MT5Broker

    login = os.getenv(f"{prefix}_LOGIN")
    password = os.getenv(f"{prefix}_PASSWORD")
    server = os.getenv(f"{prefix}_SERVER")
    if not (login and password and server):
        raise RuntimeError(f"Credenziali {prefix}_* mancanti in .env")
    return MT5Broker(login=int(login), password=password, server=server, magic=27050)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    _setup_logging()
    p = argparse.ArgumentParser(prog="signal_copier", description="Copia segnali Telegram → MT5")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("dryrun", help="Parsa messaggi di esempio senza eseguire")
    d.add_argument("--channel", required=True, help="channel_id del parser (es. xauusd_analysislab)")
    d.add_argument("--samples", required=True, help="file di messaggi di esempio")
    d.add_argument("--balance", type=float, default=0.0, help="balance per il sizing (override hint)")
    d.set_defaults(func=cmd_dryrun)

    live = sub.add_parser("live", help="Ascolta Telegram e (se --mode live) apre ordini")
    live.add_argument("--mode", choices=["dry_run", "live"], default="dry_run",
                      help="dry_run: ascolta e logga; live: apre su MT5")
    live.set_defaults(func=cmd_live)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
