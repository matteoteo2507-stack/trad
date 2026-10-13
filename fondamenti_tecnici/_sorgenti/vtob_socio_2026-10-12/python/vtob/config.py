"""Configurazioni leggibili delle strategie VTOB (indicatore + gestione del trade) e conversione per il motore.

Una configurazione è un dizionario con le chiavi KEYS. Le strategie del portafoglio sono in STRATEGIE.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from .indicatore import ParInd
from .motore import Serie
from .simulatore import cfg_vettore

SESSIONI = {"tutte": (0, 24), "8-17": (8, 17), "9-22": (9, 22), "13-22": (13, 22),
            "no10-13": [h for h in range(24) if h not in (10, 11, 12)]}          # ore italiane permesse
GIORNI = {"tutti": (0, 1, 2, 3, 4, 5, 6), "no_lun": (1, 2, 3, 4, 5, 6), "no_ven": (0, 1, 2, 3, 5, 6), "mar-gio": (1, 2, 3)}
PARZIALI = {"no": ((0, 0), (0, 0)), "50@1": ((0.5, 1.0), (0, 0)), "50@1.5": ((0.5, 1.5), (0, 0)),
            "50@2": ((0.5, 2.0), (0, 0)), "33x3": ((1 / 3, 1.0), (1 / 3, 2.0))}
IND_KEYS = ["tf", "pl", "pr", "zh", "fatt", "ms", "age", "dist", "imp", "vol", "htf"]
GEST_KEYS = ["dir", "entry", "efrac", "expiry", "sl", "slx", "tp", "tpx", "parz", "pbe", "bet", "beo", "trail", "trk",
             "trs", "time", "trx", "xf", "sess", "giorni", "reent"]
KEYS = IND_KEYS + GEST_KEYS
COSTI = dict(spread_mult=1.0, slippage=0.10, commissione=0.0)     # spread reale della candela + 0,10 $ per lato

_BASE = dict(zh=1.0, fatt="bcd", ms=3, dist=0.0, imp=1.0, vol=1.2, entry="croce", efrac=0.0, expiry=0, sl="atr",
             tp="rr", parz="no", pbe=False, bet=1.0, beo=0.1, trail="none", trk=3.0, trs="be", time=0, trx=False,
             xf="no", sess="tutte", giorni="tutti", reent=False)
# Il portafoglio del pacchetto (docs/PORTAFOGLIO_VTOB.md): stesse regole OB, cambiano TF e parametri
STRATEGIE = {
    "A": {**_BASE, "tf": "M15", "pl": 7, "pr": 3, "age": 20, "htf": "H1", "dir": "long", "slx": 6.0, "tpx": 3.0},
    "B": {**_BASE, "tf": "H1", "pl": 10, "pr": 3, "age": 10, "htf": "D1", "dir": "entrambe", "slx": 3.0, "tpx": 4.0},
    "C": {**_BASE, "tf": "M30", "pl": 5, "pr": 2, "age": 20, "htf": "H4", "dir": "entrambe", "slx": 8.0, "tpx": 3.0},
    "D": {**_BASE, "tf": "M5", "pl": 10, "pr": 5, "age": 20, "htf": "H1", "dir": "long", "slx": 6.0, "tpx": 4.0},
}


def normalizza(g: dict) -> dict:
    """I parametri che non hanno effetto prendono un valore fisso (niente doppioni con nomi diversi)."""
    g = dict(g)
    if g["entry"] == "croce":
        g["efrac"] = 0.0; g["expiry"] = 0
    if g["tp"] == "none":
        g["tpx"] = 0.0
    if g["bet"] == 0:
        g["beo"] = 0.0
    if g["parz"] == "no":
        g["pbe"] = False
    if g["trail"] in ("none", "st"):
        g["trk"] = 3.0 if g["trail"] == "none" else 0.0
    if g["trail"] == "none":
        g["trs"] = "be"
    if g["sess"] == "tutte" and g["xf"] == "sessione":
        g["xf"] = "venerdi"
    if "a" not in g["fatt"]:
        g["imp"] = 1.0
    if "b" not in g["fatt"]:
        g["age"] = 20
    if "d" not in g["fatt"]:
        g["dist"] = 0.0
    if "e" not in g["fatt"]:
        g["vol"] = 1.2
    for k in ("efrac", "slx", "tpx", "bet", "beo", "trk", "zh", "dist", "imp", "vol"):
        g[k] = float(g[k])
    for k in ("expiry", "time", "pl", "pr", "ms", "age"):
        g[k] = int(g[k])
    for k in ("pbe", "trx", "reent"):
        g[k] = bool(g[k])
    return g


def chiave(g: dict) -> tuple:
    return tuple(g[k] for k in KEYS)


def nome(g: dict) -> str:
    """Nome compatto: direzione, stop, target, parziale, BE, trailing, uscite, filtri."""
    s = [g["tf"], g["dir"][0].upper(), "croce" if g["entry"] == "croce" else f"lim{int(100 * g['efrac'])}",
         f"SL{g['slx']:g}" + ("" if g["sl"] == "atr" else g["sl"]),
         f"TP{g['tpx']:g}" if g["tp"] == "rr" else ("TPno" if g["tp"] == "none" else f"TP{g['tp']}{g['tpx']:g}")]
    if g["parz"] != "no":
        s.append(g["parz"] + ("be" if g["pbe"] else ""))
    s.append(f"BE{g['bet']:g}+{g['beo']:g}" if g["bet"] > 0 else "noBE")
    if g["trail"] != "none":
        s.append(f"TR{g['trail']}{g['trk']:g}{g['trs'][0]}")
    if g["time"]:
        s.append(f"T{g['time']}")
    if g["trx"]:
        s.append("Xtrend")
    if g["xf"] != "no":
        s.append("X" + g["xf"])
    if g["sess"] != "tutte":
        s.append("S" + g["sess"])
    if g["giorni"] != "tutti":
        s.append(g["giorni"])
    return "_".join(s)


def par_ind(g: dict) -> ParInd:
    f = g["fatt"]
    return ParInd(pivot_left=int(g["pl"]), pivot_right=int(g["pr"]), zona_h=float(g["zh"]), use_imp="a" in f,
                  imp_mult=float(g["imp"]), use_age="b" in f, min_age=int(g["age"]), use_htf="c" in f,
                  htf=g["htf"], use_dist="d" in f, dist_mult=float(g["dist"]), use_vol="e" in f,
                  vol_mult=float(g["vol"]), min_score=int(g["ms"]), htf_fonte="file")


def vettore(g: dict, costi: dict | None = None) -> np.ndarray:
    p1, p2 = PARZIALI[g["parz"]]
    return cfg_vettore(entry=g["entry"], entry_frac=g["efrac"], expiry=g["expiry"], sl=g["sl"], sl_x=g["slx"],
                       tp=g["tp"], tp_x=g["tpx"], p1=p1, p2=p2, parz_be=g["pbe"], be=(g["bet"], g["beo"]),
                       trail=g["trail"], trail_k=g["trk"], trail_start=g["trs"], time_stop=g["time"],
                       exit_trend=g["trx"], exit_forzata=g["xf"] != "no", direzione=g["dir"],
                       sess=SESSIONI[g["sess"]], giorni=GIORNI[g["giorni"]], rientro=g["reent"],
                       **(costi or COSTI))


def xflag(S: Serie, g: dict) -> np.ndarray:
    ses = SESSIONI[g["sess"]]
    if g["xf"] == "sessione" and isinstance(ses, tuple):
        return S.fine_sessione(*ses)
    return S.venerdi


__all__ = ["STRATEGIE", "KEYS", "IND_KEYS", "GEST_KEYS", "normalizza", "chiave", "nome", "par_ind", "vettore", "xflag",
           "SESSIONI", "GIORNI", "PARZIALI", "COSTI", "replace"]
