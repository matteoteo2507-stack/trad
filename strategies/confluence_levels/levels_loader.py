"""Carica e valida i livelli weekly compilati a mano dall'utente.

Il file `levels.yaml` è gitignored: contiene la "mappa dei livelli" che Matteo
prepara nel weekend (S/R + S/D + Fibonacci in confluenza). La strategia legge
questi livelli, NON li calcola.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


VALID_BIAS = {"long", "short"}
VALID_TYPES = {
    "support",
    "resistance",
    "demand_zone",
    "supply_zone",
    "fib_retracement",
    "fib_extension",
    "vwap",
    "key_level",
}


@dataclass
class Level:
    """Singolo livello operativo per una settimana."""

    id: str
    symbol: str
    price: float
    type: str
    confluence: list[str]
    bias: str  # "long" | "short"
    valid_until: date
    tp_target_price: Optional[float] = None
    sl_buffer_pips: Optional[float] = None  # override per livello, opzionale

    def is_expired(self, today: Optional[date] = None) -> bool:
        return self.valid_until < (today or date.today())


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_levels(
    path: Path | str | list[Path | str],
    today: Optional[date] = None,
) -> dict[str, list[Level]]:
    """Carica e valida uno o più file `levels.yaml`. Restituisce dict per simbolo.

    Args:
        path: singolo path OPPURE lista di path (merge per simbolo).
              Il caso lista serve all'integrazione con Confluence Auto, che
              genera un secondo file `levels_auto.yaml` da affiancare al
              manuale (vedi `strategies/confluence_auto/`). I file mancanti
              vengono saltati con warning (non bloccante).

    - Scarta livelli con `valid_until < today`.
    - Solleva `ValueError` su bias non valido.
    - Logga warning su confluenza < 2 elementi e su `tp_target_price` mancante.
    """
    today = today or date.today()
    paths: list[Path] = (
        [Path(p) for p in path] if isinstance(path, (list, tuple))
        else [Path(path)]
    )

    out: dict[str, list[Level]] = {}
    seen_ids: set[str] = set()
    for p in paths:
        if not p.exists():
            logger.warning("levels file mancante: %s", p)
            continue
        with open(p, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        if not isinstance(raw, dict):
            logger.warning("levels file %s vuoto o malformato — skip", p)
            continue
        for symbol, items in raw.items():
            if not isinstance(items, list):
                raise ValueError(
                    f"{p}:'{symbol}' deve essere una lista di livelli, non "
                    f"{type(items).__name__}"
                )
            for i, raw_level in enumerate(items):
                level = _parse_level(symbol, i, raw_level)
                if level.is_expired(today):
                    logger.info(
                        "livello scaduto ignorato: %s %s valid_until=%s",
                        level.symbol, level.id, level.valid_until,
                    )
                    continue
                if level.id in seen_ids:
                    logger.warning(
                        "ID duplicato fra file %s: %s — salto",
                        p.name, level.id,
                    )
                    continue
                seen_ids.add(level.id)
                _validate_level_warnings(level)
                out.setdefault(symbol, []).append(level)
    return out


def _parse_level(symbol: str, idx: int, raw: dict) -> Level:
    if not isinstance(raw, dict):
        raise ValueError(f"{symbol}[{idx}]: livello deve essere un dict")

    required = ("price", "type", "bias", "valid_until")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"{symbol}[{idx}]: campi mancanti {missing}")

    bias = str(raw["bias"]).lower()
    if bias not in VALID_BIAS:
        raise ValueError(
            f"{symbol}[{idx}]: bias='{bias}' non valido. Valori ammessi: {VALID_BIAS}"
        )

    valid_until = raw["valid_until"]
    if isinstance(valid_until, str):
        valid_until = datetime.strptime(valid_until, "%Y-%m-%d").date()
    elif isinstance(valid_until, datetime):
        valid_until = valid_until.date()
    elif not isinstance(valid_until, date):
        raise ValueError(
            f"{symbol}[{idx}]: valid_until deve essere date o YYYY-MM-DD"
        )

    level_id = str(raw.get("id") or f"{symbol}-auto-{idx}")
    confluence = list(raw.get("confluence") or [])

    return Level(
        id=level_id,
        symbol=symbol,
        price=float(raw["price"]),
        type=str(raw["type"]),
        confluence=confluence,
        bias=bias,
        valid_until=valid_until,
        tp_target_price=(
            float(raw["tp_target_price"]) if raw.get("tp_target_price") is not None else None
        ),
        sl_buffer_pips=(
            float(raw["sl_buffer_pips"]) if raw.get("sl_buffer_pips") is not None else None
        ),
    )


def _validate_level_warnings(level: Level) -> None:
    """Warning non-bloccanti che aiutano l'utente a tenere pulito `levels.yaml`."""
    if level.type not in VALID_TYPES:
        logger.warning(
            "%s %s: tipo '%s' non in lista standard (%s) — accettato comunque",
            level.symbol,
            level.id,
            level.type,
            sorted(VALID_TYPES),
        )
    if len(level.confluence) < 2:
        logger.warning(
            "%s %s: confluenza debole (%d elemento), atteso ≥2",
            level.symbol,
            level.id,
            len(level.confluence),
        )
    if level.tp_target_price is None:
        logger.warning(
            "%s %s: tp_target_price mancante — la strategia salterà questo livello",
            level.symbol,
            level.id,
        )
