"""CLI Typer per la strategia Confluence Levels.

Esempi:
    python -m strategies.confluence_levels validate-levels
    python -m strategies.confluence_levels dry-run --symbol EURUSD --price 1.08600
    python -m strategies.confluence_levels run                        # default: yfinance
    python -m strategies.confluence_levels run --datasource mt5 --account DEMO1

Architettura post-pivot 2026-05-05:
    Confluence è SOLO NOTIFICA. Non piazza ordini. Il broker serve solo come fonte OHLC.
    Datasource default = yfinance (gratis, cloud-friendly, niente MT5 desktop).
    L'opzione `--datasource mt5` resta per chi vuole prezzi tick reali del broker su PC con MT5
    aperto, ma non è necessaria.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .strategy import ConfluenceLevelsStrategy

app = typer.Typer(add_completion=False, help="Confluence Levels Trader (solo notifica)")
console = Console()

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@app.command("validate-levels")
def validate_levels(
    levels_path: Path = typer.Option(
        None,
        "--levels",
        help="Path del file levels.yaml (default: dalla cartella strategia).",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Valida `levels.yaml` e stampa eventuali warning (scaduti, RR insufficiente)."""
    _setup_logging(verbose)
    strategy = ConfluenceLevelsStrategy(config_path=CONFIG_PATH)
    if levels_path is not None:
        strategy._levels_path = levels_path  # override esplicito per uso CLI

    levels_by_symbol = strategy.load_levels_now(force_reload=True)
    if not levels_by_symbol:
        console.print("[yellow]Nessun livello valido trovato.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Livelli validi")
    for col in ("Symbol", "ID", "Price", "Type", "Bias", "Confluence", "Valid Until", "TP"):
        table.add_column(col)
    for symbol, levels in levels_by_symbol.items():
        for lvl in levels:
            table.add_row(
                symbol,
                lvl.id,
                f"{lvl.price:.5f}",
                lvl.type,
                lvl.bias,
                ", ".join(lvl.confluence) or "-",
                lvl.valid_until.isoformat(),
                f"{lvl.tp_target_price:.5f}" if lvl.tp_target_price else "-",
            )
    console.print(table)


@app.command("dry-run")
def dry_run(
    symbol: str = typer.Option(..., "--symbol", "-s"),
    price: float = typer.Option(..., "--price", "-p"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Simula la valutazione dei livelli a un prezzo dato. Niente broker, niente Telegram."""
    _setup_logging(verbose)
    strategy = ConfluenceLevelsStrategy(config_path=CONFIG_PATH)
    evaluations = strategy.evaluate_symbol(symbol=symbol, current_price=price)

    if not evaluations:
        console.print(f"[yellow]Nessun livello configurato per {symbol}.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title=f"Dry-run {symbol} @ {price}")
    for col in ("Level", "Distance (pip)", "Passed", "Reason"):
        table.add_column(col)
    for ev in evaluations:
        table.add_row(
            ev.level.id,
            f"{ev.distance_pips:.1f}",
            "PASS" if ev.passed else "SKIP",
            ev.reason,
        )
    console.print(table)


@app.command("run")
def run(
    datasource: str = typer.Option(
        "yfinance",
        "--datasource",
        "-d",
        help="Fonte prezzi: 'yfinance' (default, cloud-friendly) o 'mt5' (richiede terminale MT5 aperto).",
    ),
    account: str = typer.Option(
        "DEMO1",
        "--account",
        help="Account MT5 da usare (solo se --datasource=mt5).",
    ),
    once: bool = typer.Option(
        False, "--once", help="Una sola passata invece del polling continuo."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Avvia il polling loop. Default: yfinance + Telegram, niente MT5 desktop."""
    _setup_logging(verbose)

    from dotenv import load_dotenv

    from core.risk_gate import load_risk_config
    from notifiers.telegram import TelegramNotifier

    from .runner import ConfluenceRunner

    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or ""
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or ""
    if not bot_token or not chat_id:
        raise typer.BadParameter("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti")

    broker = _build_broker(datasource=datasource, account=account)

    strategy = ConfluenceLevelsStrategy(config_path=CONFIG_PATH)
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
    risk_config = load_risk_config()

    broker.connect()
    try:
        notifier.send_message(
            f"🚀 Confluence runner avviato (datasource={datasource}, once={once})"
        )
        runner = ConfluenceRunner(
            strategy=strategy,
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
            notifier.send_message("🛑 Confluence runner fermato")
        except Exception:
            pass
        broker.disconnect()


def _build_broker(datasource: str, account: str):
    """Factory broker: yfinance (default) o mt5 (legacy, opzionale)."""
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


if __name__ == "__main__":
    app()
