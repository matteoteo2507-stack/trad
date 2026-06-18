"""Spina dati del workflow — record di trade CONTESTUALIZZATO (Incremento 1).

Ogni segnale viene loggato col CONTESTO al momento della decisione (regime, sessione,
ATR/vol, spread assunto, base strumento spot/futures, versione parametri), piu' i campi
che umano/riconciliazione riempiranno DOPO: la decisione discrezionale (taken/skipped/
modified) e l'esito reale netto costi. Senza questi campi non si separa edge-del-sistema
da edge-della-discrezione, ne' edge-decaduto da costo-aumentato; e il contesto al momento
della decisione NON e' recuperabile dopo. Vedi docs/TRADING_WORKFLOW_DESIGN.md.

Logica pura, offline-testabile. Nessun ordine, nessuna rete.
"""
from __future__ import annotations

import csv
import math
import statistics as st
from datetime import datetime, timezone
from pathlib import Path

# schema della spina (ordine delle colonne nel CSV)
HEADER = [
    # identita' / segnale
    "record_id", "ts_utc", "asset", "instrument_basis", "data_source",
    "side", "zone", "confluence", "types", "price", "dist_atr",
    "sl", "tp", "rr", "risk_pct", "param_version",
    # contesto della decisione (popolato alla cattura)
    "session", "regime", "adx_h1", "atr_h1", "vol_h1", "spread_assumed",
    # decisione umana (riempita dopo — journal/reconcile)
    "human_decision", "human_note",
    # esito reale, netto costi (riempito dopo)
    "real_entry", "real_exit", "real_cost", "real_R", "outcome",
]


def session_of(dt: datetime) -> str:
    """Sessione FX dall'ora UTC (overlap Londra/NY prioritario)."""
    h = dt.hour
    if 12 <= h < 16:
        return "London/NY overlap"
    if 7 <= h < 12:
        return "London"
    if 16 <= h < 21:
        return "NY"
    if 0 <= h < 7:
        return "Tokyo"
    return "Off"


def adx_last(h1: list, n: int = 14):
    """ADX(Wilder) finale sulla finestra H1 (proxy di trend-strength). None se dati scarsi."""
    L = len(h1)
    if L < 2 * n + 2:
        return None
    tr, pdm, ndm = [0.0] * L, [0.0] * L, [0.0] * L
    for i in range(1, L):
        h, l, pc = h1[i]["high"], h1[i]["low"], h1[i - 1]["close"]
        up, dn = h - h1[i - 1]["high"], h1[i - 1]["low"] - l
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
        pdm[i] = up if (up > dn and up > 0) else 0.0
        ndm[i] = dn if (dn > up and dn > 0) else 0.0

    def wilder(x):
        s = [None] * L
        s[n] = sum(x[1:n + 1])
        for i in range(n + 1, L):
            s[i] = s[i - 1] - s[i - 1] / n + x[i]
        return s

    str_, spdm, sndm = wilder(tr), wilder(pdm), wilder(ndm)
    dx = [None] * L
    for i in range(n, L):
        if str_[i] and str_[i] > 0:
            pdi, ndi = 100 * spdm[i] / str_[i], 100 * sndm[i] / str_[i]
            den = pdi + ndi
            dx[i] = 100 * abs(pdi - ndi) / den if den > 0 else 0.0
    vals = [dx[i] for i in range(n + 1, 2 * n + 1) if dx[i] is not None]
    if len(vals) < n:
        return None
    adx = sum(vals) / n
    for i in range(2 * n + 1, L):
        if dx[i] is not None:
            adx = (adx * (n - 1) + dx[i]) / n
    return adx


def regime_from_adx(adx) -> str:
    """Etichetta regime da ADX (soglie Wilder standard). Proxy, non verita'."""
    if adx is None:
        return "n/d"
    if adx < 20:
        return "range"
    if adx < 25:
        return "transizione"
    return "trend"


def realized_vol(h1: list):
    """Volatilita' realizzata = stdev dei log-return dei close sulla finestra. None se scarsa."""
    cl = [b["close"] for b in h1 if b.get("close", 0) > 0]
    if len(cl) < 3:
        return None
    rets = [math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl)) if cl[i - 1] > 0]
    return st.pstdev(rets) if len(rets) >= 2 else None


def instrument_basis(yf_ticker: str | None, data_backend: str) -> str:
    """Base prezzo: spot reale (MT5), futures (GC=F), ~spot (BTC-USD)."""
    if data_backend == "mt5":
        return "spot"
    t = (yf_ticker or "").upper()
    if t.endswith("=F"):
        return "futures"
    return "spot~"


def build_record(asset_cfg: dict, sig: dict, price: float, h1_window: list, *,
                 data_backend: str, risk_pct, param_version: str,
                 ts: datetime | None = None) -> dict:
    """Costruisce il record contestualizzato (campi umano/esito vuoti alla cattura)."""
    ts = ts or datetime.now(timezone.utc)
    asset = asset_cfg.get("name", "?")
    adx = adx_last(h1_window)
    rec = {k: "" for k in HEADER}
    rec.update({
        "record_id": f"{ts.isoformat(timespec='seconds')}|{asset}|{sig['side']}|{sig['zone']}",
        "ts_utc": ts.isoformat(timespec="seconds"),
        "asset": asset,
        "instrument_basis": instrument_basis(asset_cfg.get("yf_ticker"), data_backend),
        "data_source": data_backend,
        "side": sig["side"], "zone": sig["zone"], "confluence": sig["confluence"],
        "types": "|".join(sig.get("types", [])), "price": round(price, 2),
        "dist_atr": sig["dist_atr"], "sl": sig["sl"], "tp": sig["tp"], "rr": sig["rr"],
        "risk_pct": risk_pct, "param_version": param_version,
        "session": session_of(ts), "regime": regime_from_adx(adx),
        "adx_h1": round(adx, 1) if adx is not None else "",
        "atr_h1": sig.get("atr", ""),
        "vol_h1": (lambda v: round(v, 5) if v is not None else "")(realized_vol(h1_window)),
        "spread_assumed": asset_cfg.get("spread_assumed", ""),
    })
    return rec


def append_record(path: str, rec: dict) -> None:
    """Append del record al CSV della spina (scrive l'header se il file e' nuovo)."""
    p = Path(path)
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow([rec.get(k, "") for k in HEADER])


def update_record(path: str, record_id: str, **fields) -> bool:
    """Riempie campi (es. human_decision, real_R, outcome) per record_id. Usato dal journal."""
    p = Path(path)
    if not p.exists():
        return False
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    hit = False
    for r in rows:
        if r.get("record_id") == record_id:
            for k, v in fields.items():
                if k in HEADER:
                    r[k] = v
            hit = True
    if hit:
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(rows)
    return hit
