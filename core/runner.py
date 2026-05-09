"""Orchestrator generico (post-pivot 2026-05-05).

Avvia una strategia Python registrata in `core.registry`. Attualmente
l'unica strategia Python operativa è `confluence_levels` — la London Breakout
è migrata a Expert Advisor MQL5 e gira sul terminale MT5, non più qui.

Esempio:
    python -m core.runner list
    python -m core.runner run --strategy confluence_levels
    python -m core.runner run --strategy confluence_levels --datasource mt5 --account DEMO1
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from core import registry

app = typer.Typer(add_completion=False, help="Trading System — orchestrator generico")
console = Console()


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@app.command("list")
def list_strategies() -> None:
    """Elenca le strategie Python registrate."""
    for name in registry.available():
        console.print(f"- {name}")


@app.command("run")
def run(
    strategy: str = typer.Option(..., "--strategy", "-s"),
    datasource: str = typer.Option(
        "yfinance",
        "--datasource",
        "-d",
        help="Fonte prezzi: 'yfinance' (default) o 'mt5'.",
    ),
    account: str = typer.Option(
        "DEMO1", "--account", help="Account MT5 (solo se --datasource=mt5)."
    ),
    once: bool = typer.Option(False, "--once"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        help="Path del config strategia. Default: strategies/<name>/config.yaml",
    ),
) -> None:
    """Avvia una strategia per nome (delega al suo runner specifico)."""
    _setup_logging(verbose)

    strategy_cls = registry.get_strategy_class(strategy)
    strategy_dir = Path("strategies") / strategy
    cfg_path = config_path or (strategy_dir / "config.yaml")
    if not cfg_path.exists():
        raise typer.BadParameter(f"Config non trovato: {cfg_path}")

    strategy_instance = strategy_cls(config_path=cfg_path)

    runner_factories = {
        "confluence_levels": _make_confluence_runner,
    }
    if strategy not in runner_factories:
        raise typer.BadParameter(
            f"Strategia '{strategy}' non ha un runner Python. "
            f"Le strategie automatiche girano come EA MQL5: vedi `mql5/`. "
            f"Strategie Python disponibili: {sorted(runner_factories.keys())}"
        )

    from dotenv import load_dotenv

    from core.risk_gate import load_risk_config
    from notifiers.telegram import TelegramNotifier

    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or ""
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or ""
    if not bot_token or not chat_id:
        raise typer.BadParameter("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti")

    broker = _build_broker(datasource=datasource, account=account)
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
    risk_config = load_risk_config()

    broker.connect()
    try:
        notifier.send_message(
            f"🚀 [{strategy}] runner avviato (datasource={datasource}, once={once})"
        )
        runner = runner_factories[strategy](
            strategy_instance=strategy_instance,
            broker=broker,
            notifier=notifier,
            risk_config=risk_config,
        )
        if once:
            runner.run_once()
        else:
            runner.run_forever()
    finally:
        try:
            notifier.send_message(f"🛑 [{strategy}] runner fermato")
        except Exception:
            pass
        broker.disconnect()


def _build_broker(datasource: str, account: str):
    """Factory broker condivisa col CLI di Confluence."""
    ds = datasource.strip().lower()
    if ds == "yfinance":
        from brokers.yfinance_data import YFinanceBroker

        return YFinanceBroker()

    if ds == "mt5":
        from brokers.mt5 import MT5Broker

        login = os.getenv(f"MT5_{account}_LOGIN")
        password = os.getenv(f"MT5_{account}_PASSWORD")
        server = os.getenv(f"MT5_{account}_SERVER")
        terminal_path = os.getenv(f"MT5_{account}_TERMINAL_PATH")
        if not (login and password and server):
            raise typer.BadParameter(f"Credenziali MT5_{account}_* mancanti in .env")
        return MT5Broker(
            login=int(login),
            password=password,
            server=server,
            terminal_path=terminal_path,
        )

    raise typer.BadParameter(
        f"--datasource '{datasource}' non valido. Valori ammessi: 'yfinance', 'mt5'."
    )


def _make_confluence_runner(strategy_instance, broker, notifier, risk_config):
    from strategies.confluence_levels.runner import ConfluenceRunner

    return ConfluenceRunner(
        strategy=strategy_instance,
        broker=broker,
        notifier=notifier,
        risk_config=risk_config,
    )


if __name__ == "__main__":
    app()
