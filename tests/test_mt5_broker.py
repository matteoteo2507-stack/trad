"""Test delle utility di bonifica request di MT5Broker (pure, niente terminale).

`MetaTrader5` è importato pigramente nei metodi, quindi MT5Broker è istanziabile
e queste helper sono testabili anche senza la libreria/terminale.
"""

from __future__ import annotations

import re

from types import SimpleNamespace

from brokers.mt5 import MT5Broker


def _broker() -> MT5Broker:
    return MT5Broker(login=1, password="x", server="y")


def test_safe_comment_solo_caratteri_ammessi():
    c = MT5Broker._safe_comment("xauusd_analysislab TP1 (NOW, tp provvisorio)")
    assert re.fullmatch(r"[A-Za-z0-9_-]+", c)  # niente spazi/parentesi/virgole
    assert len(c) <= 31
    assert c.startswith("xauusd_analysislab_TP1")


def test_safe_comment_vuoto():
    assert MT5Broker._safe_comment("") == ""
    assert MT5Broker._safe_comment("(),; ") == ""


def test_norm_volume_allinea_e_clampa():
    info = SimpleNamespace(volume_step=0.01, volume_min=0.01, volume_max=5.0)
    b = _broker()
    assert b._norm_volume(0.033, info) == 0.03      # allineato al passo
    assert b._norm_volume(0.0, info) == 0.01        # clamp al minimo
    assert b._norm_volume(10.0, info) == 5.0        # clamp al massimo


def test_normalize_request_prezzi_ai_digits_e_comment():
    info = SimpleNamespace(volume_step=0.01, volume_min=0.01, volume_max=5.0, digits=2)
    b = _broker()
    req = {"price": 4451.855, "sl": 4441.855, "tp": 4456.855,
           "volume": 0.033, "comment": "ch TP1 (NOW)"}
    b._normalize_request(req, info)
    # prezzi arrotondati ai digits (≤ 2 decimali), non più 3
    for k in ("price", "sl", "tp"):
        assert req[k] == round(req[k], 2)
    assert req["volume"] == 0.03
    assert re.fullmatch(r"[A-Za-z0-9_-]+", req["comment"])
