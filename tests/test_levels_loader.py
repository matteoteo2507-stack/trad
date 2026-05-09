"""Test di `levels_loader.load_levels`."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from strategies.confluence_levels.levels_loader import Level, load_levels


def _write_yaml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "levels.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def test_carica_livello_completo(tmp_path):
    p = _write_yaml(tmp_path, """
EURUSD:
  - id: "EURUSD-W19-S1"
    price: 1.0850
    type: support
    confluence: [SR_weekly, SD_H4, Fib_618]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.0950
""")
    levels = load_levels(p)
    assert "EURUSD" in levels
    assert len(levels["EURUSD"]) == 1
    lvl = levels["EURUSD"][0]
    assert isinstance(lvl, Level)
    assert lvl.id == "EURUSD-W19-S1"
    assert lvl.price == 1.0850
    assert lvl.bias == "long"
    assert lvl.tp_target_price == 1.0950


def test_scarta_livelli_scaduti(tmp_path):
    p = _write_yaml(tmp_path, """
EURUSD:
  - id: "old"
    price: 1.0850
    type: support
    confluence: [SR_weekly, Fib_618]
    bias: long
    valid_until: 2020-01-01
    tp_target_price: 1.0950
  - id: "new"
    price: 1.0900
    type: resistance
    confluence: [SR_weekly, Fib_786]
    bias: short
    valid_until: 2099-12-31
    tp_target_price: 1.0800
""")
    levels = load_levels(p, today=date(2026, 5, 2))
    assert len(levels["EURUSD"]) == 1
    assert levels["EURUSD"][0].id == "new"


def test_bias_invalido_solleva(tmp_path):
    p = _write_yaml(tmp_path, """
EURUSD:
  - id: "x"
    price: 1.0850
    type: support
    confluence: [SR_weekly, Fib_618]
    bias: maybe
    valid_until: 2099-12-31
""")
    with pytest.raises(ValueError, match="bias"):
        load_levels(p)


def test_campo_mancante_solleva(tmp_path):
    p = _write_yaml(tmp_path, """
EURUSD:
  - price: 1.0850
    type: support
    bias: long
""")
    with pytest.raises(ValueError, match="campi mancanti"):
        load_levels(p)


def test_id_auto_generato_se_mancante(tmp_path):
    p = _write_yaml(tmp_path, """
EURUSD:
  - price: 1.0850
    type: support
    confluence: [SR_weekly, Fib_618]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.0950
""")
    levels = load_levels(p)
    assert levels["EURUSD"][0].id.startswith("EURUSD-auto-")


def test_file_mancante_ritorna_dict_vuoto(tmp_path):
    levels = load_levels(tmp_path / "non_esiste.yaml")
    assert levels == {}


def test_confluenza_debole_solo_warning(tmp_path, caplog):
    """Confluenza singola non blocca: solo warning."""
    import logging

    p = _write_yaml(tmp_path, """
EURUSD:
  - id: "weak"
    price: 1.0850
    type: support
    confluence: [SR_weekly]
    bias: long
    valid_until: 2099-12-31
    tp_target_price: 1.0950
""")
    with caplog.at_level(logging.WARNING):
        levels = load_levels(p)
    assert len(levels["EURUSD"]) == 1
    assert any("confluenza debole" in rec.message for rec in caplog.records)
