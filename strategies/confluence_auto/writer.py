"""Serializzazione di `AutoLevel` → `levels_auto.yaml`.

Output compatibile con `confluence_levels/levels_loader.py`: stesso schema
(`id, price, type, confluence, bias, valid_until, tp_target_price`).
Per le S/D zones aggiunge un commento `##` sopra la voce con il bordo distale.

Convenzione adottata: il file è SOVRASCRITTO interamente a ogni run.
Lo storico viene gestito esternamente (commit git mensile, dataset confronto).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .detectors.confluence import AutoLevel


_HEADER = """# levels_auto.yaml — generato automaticamente da Confluence Auto.
#
# **NON EDITARE A MANO**: il file viene sovrascritto a ogni run di
# `python -m strategies.confluence_auto generate`.
#
# Per i livelli compilati manualmente, usa `levels.yaml`.
#
# Generato il: {timestamp}
# Detectors: S/R (swing pivots), S/D (base-impulse-base), POC (volume profile).
# Tutti gli ID hanno suffisso "-AUTO" per distinguibilità nel runner Telegram.
"""


def _format_price(price: float, decimals: int) -> str:
    return f"{price:.{decimals}f}"


def _decimals_for_symbol(symbol: str) -> int:
    # Convenzione progetto: 5 decimali forex, 2 decimali XAU.
    return 2 if symbol.upper().startswith("XAU") else 5


def write_levels_yaml(
    levels_by_symbol: dict[str, list[AutoLevel]],
    output_path: Path | str,
) -> None:
    """Scrive `levels_auto.yaml` nel formato letto da `levels_loader.load_levels`.

    Args:
        levels_by_symbol: dict simbolo → lista di AutoLevel.
        output_path: dove salvare il file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [_HEADER.format(timestamp=datetime.utcnow().isoformat(timespec="seconds"))]

    for symbol in sorted(levels_by_symbol.keys()):
        levels = levels_by_symbol[symbol]
        if not levels:
            continue
        decimals = _decimals_for_symbol(symbol)
        lines.append(f"\n{symbol}:")

        for L in levels:
            if L.distal_price is not None:
                lines.append(
                    f"  ## {L.id}: zona distale {_format_price(L.distal_price, decimals)}"
                )
            lines.append(f'  - id: "{L.id}"')
            lines.append(f"    price: {_format_price(L.price, decimals)}")
            lines.append(f"    type: {L.type}")
            conf = ", ".join(L.confluence)
            lines.append(f"    confluence: [{conf}]")
            lines.append(f"    bias: {L.bias}")
            lines.append(f"    valid_until: {L.valid_until.isoformat()}")
            if L.tp_target_price is not None:
                lines.append(f"    tp_target_price: {_format_price(L.tp_target_price, decimals)}")
            lines.append("")  # blank line tra livelli

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
