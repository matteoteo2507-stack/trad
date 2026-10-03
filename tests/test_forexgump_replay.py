"""Test del motore di replay di Forex Gump su prezzi SINTETICI (nessun segnale reale toccato)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis.forexgump import replay as rp


def _barre(t0, prezzi, spread=0.2):
    """M1 piatte: ogni barra ha O=H=L=C=prezzo (mid); bid/ask a +/- spread/2."""
    idx = pd.date_range(t0, periods=len(prezzi), freq="min")
    p = np.asarray(prezzi, float)
    mk = lambda x: pd.DataFrame({"open": x, "high": x, "low": x, "close": x}, index=idx)
    return mk(p - spread / 2), mk(p + spread / 2)


def _prezzi(t0, percorso, spread=0.2):
    b, a = _barre(t0, percorso, spread)
    return rp.Prezzi(m1_bid=b, m1_ask=a)


T0 = pd.Timestamp("2026-03-10 10:00")


def test_buy_entra_ask_esce_bid_e_prende_il_tp():
    # mid 100 per 5 minuti, poi sale a 112: TP a +10 dal fill
    percorso = [100.0] * 5 + [112.0] * 30
    pz = _prezzi(T0, percorso, spread=0.2)
    r = rp.esegui(pz, T0, True, dist_sl=2.0, dist_tp=10.0, entry_post=99.0)
    assert r["sorgente_fill"] == "m1" and r["fill"] == pytest.approx(100.1)      # ASK
    assert r["esito"] == "TP"
    assert r["r"] == pytest.approx(10.0 / 2.0 - rp.COMMISSIONE / 2.0)
    assert r["scarto_postato"] == pytest.approx(1.1)                              # gia' superato


def test_sell_esce_ask_e_prende_lo_stop():
    percorso = [100.0] * 3 + [103.0] * 10
    pz = _prezzi(T0, percorso, spread=0.2)
    r = rp.esegui(pz, T0, False, dist_sl=2.0, dist_tp=10.0)
    assert r["fill"] == pytest.approx(99.9)                                       # BID
    assert r["esito"] == "SL" and r["r"] < -1.0                                   # gap oltre lo stop


def test_spread_maggiore_dello_stop_salta_l_ordine():
    pz = _prezzi(T0, [100.0] * 30, spread=2.5)
    assert rp.esegui(pz, T0, True, dist_sl=2.0, dist_tp=10.0)["esito"] == "SKIP_SPREAD"


def test_timeout_a_24_ore_di_calendario():
    pz = _prezzi(T0, [100.0] * (60 * 30), spread=0.2)                            # 30 ore piatte
    r = rp.esegui(pz, T0, True, dist_sl=2.0, dist_tp=10.0)
    assert r["esito"] == "TIMEOUT"
    assert r["t_uscita"] - r["t_fill"] <= pd.Timedelta(hours=24)
    assert r["rollover"] == 1                                                     # attraversa le 22 UTC


def test_stress_peggiora():
    percorso = [100.0] * 5 + [112.0] * 30
    base = rp.esegui(_prezzi(T0, percorso), T0, True, 2.0, 10.0)
    st = rp.esegui(_prezzi(T0, percorso), T0, True, 2.0, 10.0, stress=True)
    assert st["r"] < base["r"]


def test_giornata_di_trading_parte_alle_22_utc():
    assert rp.giorno_trading(pd.Timestamp("2026-03-09 21:59")) == pd.Timestamp("2026-03-09")
    assert rp.giorno_trading(pd.Timestamp("2026-03-09 22:00")) == pd.Timestamp("2026-03-10")


def test_variante_live_usa_i_livelli_postati_e_il_rischio_vero():
    percorso = [101.0] * 5 + [110.5] * 30
    pz = _prezzi(T0, percorso, spread=0.2)
    r = rp.esegui(pz, T0, True, dist_sl=2.0, dist_tp=10.0, entry_post=100.0, variante="live")
    assert r["esito"] == "TP" and r["r_unit"] == pytest.approx(101.1 - 98.0)


def test_appaiato_su_random_walk_e_centrato_sullo_zero():
    rng = np.random.default_rng(3)
    d, giorni = [], []
    for i in range(300):
        t = T0 + pd.Timedelta(days=i)
        percorso = 100 + np.cumsum(rng.normal(0, 0.5, 600))
        pz = _prezzi(t, percorso, spread=0.1)
        x = rp.esegui_appaiato(pz, t, bool(rng.integers(0, 2)), 2.0, 10.0)
        if x["d"] is not None:
            d.append(x["d"]); giorni.append(rp.giorno_trading(t))
    ci = rp.ci_cluster_giorno(d, giorni, n_boot=2000)
    assert ci["low"] < 0 < ci["high"]


def test_variante_postato_riempie_al_prezzo_dichiarato():
    percorso = [101.0] * 5 + [110.5] * 30
    r = rp.esegui(_prezzi(T0, percorso), T0, True, 2.0, 10.0, entry_post=100.0, variante="postato")
    assert r["fill"] == 100.0 and r["esito"] == "TP"
    assert r["r"] == pytest.approx(10.0 / 2.0 - rp.COMMISSIONE / 2.0)


def test_meta_spread_migliora_il_fill():
    pz = _prezzi(T0, [100.0] * 40, spread=0.4)
    assert rp.esegui(pz, T0, True, 2.0, 10.0, k_spread=0.5)["fill"] == pytest.approx(100.1)


# ---- correzioni della G1 #2 (02/10) ---------------------------------------------------------

def test_appaiato_rifiuta_le_varianti_descrittive():
    # B1: con "postato"/"live" il lato opposto mandava in errore lo script a meta' corsa
    pz = _prezzi(T0, [100.0] * 40)
    with pytest.raises(ValueError):
        rp.esegui_appaiato(pz, T0, True, 2.0, 10.0, entry_post=100.0, variante="postato")


def test_fill_oltre_60_secondi_non_eseguito():
    # B2: stesso ritardo massimo per tick e M1; buco nei dati dopo t+L -> NON_ESEGUITO, contato
    b, a = _barre(T0 + pd.Timedelta(minutes=5), [100.0] * 30)
    r = rp.esegui(rp.Prezzi(m1_bid=b, m1_ask=a), T0, True, 2.0, 10.0)
    assert r["esito"] == "NON_ESEGUITO" and r["r"] is None


def _tick_provider(serie):
    def f(t0, t1):
        x = serie[(serie.index >= t0) & (serie.index < t1)]
        return x if len(x) else None
    return f


def test_crollo_dentro_la_finestra_tick_e_uno_stop():
    # B2: un crollo sotto lo SL nella prima ora deve uscire come SL (prima poteva diventare TIMEOUT)
    idx = pd.date_range(T0, periods=4000, freq="1s")
    mid = np.full(len(idx), 100.0)
    mid[600:900] = 97.0                                   # 10-15 minuti dopo: crollo di 3 $
    tk = pd.DataFrame({"bidPrice": mid - 0.1, "askPrice": mid + 0.1}, index=idx)
    b, a = _barre(T0, [100.0] * 60 * 30)
    r = rp.esegui(rp.Prezzi(m1_bid=b, m1_ask=a, tick=_tick_provider(tk)), T0, True, 2.0, 10.0)
    assert r["sorgente_fill"] == "tick" and r["esito"] == "SL"


def test_slittamento_d_uscita_sullo_stop_non_sul_tp():
    # R1: lo slittamento d'uscita e' un costo esplicito su ogni uscita non-TP
    pz_sl = _prezzi(T0, [100.0] * 3 + [97.0] * 10)
    base, st = (rp.esegui(pz_sl, T0, True, 2.0, 10.0, stress=s) for s in (False, True))
    assert st["esito"] == "SL" and st["r"] < base["r"] - rp.STRESS["slittamento"] / 2.0 + 1e-9
    pz_tp = _prezzi(T0, [100.0] * 5 + [113.0] * 30)
    tp_b, tp_s = (rp.esegui(pz_tp, T0, True, 2.0, 10.0, stress=s) for s in (False, True))
    assert tp_s["esito"] == "TP" and tp_b["esito"] == "TP"


# ---- correzioni della G1 #3 (02/10) ---------------------------------------------------------

def _tick_piatti(t0, n_sec, mid=100.0, spread=0.2, ritocchi=()):
    idx = pd.date_range(t0, periods=n_sec, freq="1s")
    m = np.full(n_sec, mid)
    for (a, b, v) in ritocchi:
        m[a:b] = v
    return pd.DataFrame({"bidPrice": m - spread / 2, "askPrice": m + spread / 2}, index=idx)


def test_limit_su_tick_eseguito_quando_il_prezzo_torna():
    # il prezzo torna all'entrata postata (ask <= 100) dopo 5 minuti, poi sale al TP
    tk = _tick_piatti(T0, 6000, mid=101.0, ritocchi=((300, 330, 99.85), (900, 6000, 111.0)))
    b, a = _barre(T0, [101.0] * 600)
    r = rp.esegui(rp.Prezzi(m1_bid=b, m1_ask=a, tick=_tick_provider(tk)), T0, True, 2.0, 10.0,
                  entry_post=100.0, variante="limit")
    assert r["fill"] == 100.0 and r["esito"] == "TP"


def test_limit_su_tick_non_eseguito_se_il_prezzo_non_torna():
    tk = _tick_piatti(T0, 6000, mid=102.0)
    b, a = _barre(T0, [102.0] * 600)
    r = rp.esegui(rp.Prezzi(m1_bid=b, m1_ask=a, tick=_tick_provider(tk)), T0, True, 2.0, 10.0,
                  entry_post=100.0, variante="limit")
    assert r["esito"] == "LIMIT_NON_ESEGUITO"


def test_giunzione_tick_m1_senza_buco():
    # crollo SOLO nei tick fra fine_tick (fill + 60 min) e il minuto intero successivo; M1 piatte.
    # Prima della correzione quei secondi non stavano ne' nei tick ne' nelle M1: lo stop spariva.
    fill_s = 10                                           # fill al tick di T0 + 10 s
    a_crollo = fill_s + 3600 + 20                         # 60 min e 20 s dopo il fill
    tk = _tick_piatti(T0, 4000, ritocchi=((a_crollo, a_crollo + 15, 97.0),))
    b, a = _barre(T0, [100.0] * 300)
    r = rp.esegui(rp.Prezzi(m1_bid=b, m1_ask=a, tick=_tick_provider(tk)), T0, True, 2.0, 10.0)
    assert r["sorgente_fill"] == "tick" and r["esito"] == "SL"
