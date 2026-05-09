"""CLI Typer per lo Stock Selector.

Esempio:
    python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .strategy import run_selection

app = typer.Typer(
    add_completion=False,
    help="Stock Selector V6.0 — selezione SP500 headless basata su scoring fondamentale + RRG.",
)
console = Console()


@app.command()
def main(
    risk_free: float = typer.Option(
        ...,
        "--risk-free",
        "-r",
        help="Tasso risk-free USA in percentuale (es. 4.2).",
    ),
    liquidity: str = typer.Option(
        ...,
        "--liquidity",
        "-l",
        help="Trend liquidità banche centrali: 'increasing' o 'decreasing'.",
    ),
    benchmark: str = typer.Option(
        "^GSPC",
        "--benchmark",
        "-b",
        help="Ticker benchmark per il calcolo RRG.",
    ),
    output_dir: Path = typer.Option(
        Path("."),
        "--output-dir",
        "-o",
        help="Cartella di output per gli Excel.",
    ),
    no_excel: bool = typer.Option(
        False,
        "--no-excel",
        help="Non salvare gli Excel, solo output strutturato a video.",
    ),
    tickers: Optional[str] = typer.Option(
        None,
        "--tickers",
        help="Lista ticker separati da virgola (override SP500). Utile per test rapidi.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Logging in DEBUG."),
) -> None:
    """Esegue la selezione e stampa le top picks a video."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    liquidity_norm = liquidity.strip().lower()
    if liquidity_norm not in {"increasing", "decreasing"}:
        raise typer.BadParameter("--liquidity deve essere 'increasing' o 'decreasing'.")
    is_increasing = liquidity_norm == "increasing"

    tickers_override = (
        [t.strip().upper() for t in tickers.split(",") if t.strip()] if tickers else None
    )

    result = run_selection(
        risk_free_rate=risk_free,
        is_liquidity_increasing=is_increasing,
        benchmark=benchmark,
        save_excel=not no_excel,
        output_dir=output_dir,
        tickers_override=tickers_override,
    )

    console.print(f"\n[bold]Scenario:[/bold] {result.scenario.value}")
    console.print(f"[bold]Benchmark:[/bold] {result.benchmark}")
    console.print(
        f"[bold]Top picks (score ≥ 5):[/bold] {len(result.top_picks)} su {len(result.full_analysis)}\n"
    )

    table = Table(title="Top Picks")
    for col in ("Ticker", "Settore", "Score", "RRG", "Macro Match", "P/E", "ROE"):
        table.add_column(col)
    for p in result.top_picks:
        table.add_row(
            p.ticker,
            p.sector,
            f"{p.score:.1f}",
            p.rrg.value,
            p.target_match,
            f"{p.pe:.2f}" if p.pe else "-",
            f"{p.roe:.2%}" if p.roe is not None else "-",
        )
    console.print(table)

    if result.excel_top_picks_path:
        console.print(f"\n[green]Excel salvato:[/green] {result.excel_top_picks_path}")
        console.print(f"[green]Excel salvato:[/green] {result.excel_full_analysis_path}")


if __name__ == "__main__":
    app()
