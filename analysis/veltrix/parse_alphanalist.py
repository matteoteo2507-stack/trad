"""Parser dell'export AlphaAnalist (VELTRIX) -> dataset strutturato pulito.

Punto 1 del piano: trasformare 1296 messaggi broadcast in record analizzabili,
così il punto 2 (calibrazione hit-rate del bias del bot) lavora su dati puliti.

Estrae, per ogni messaggio che porta una chiamata direzionale, una o più righe
(asset, bias, prezzo, lampadine TF, score, livelli). Gestisce le varianti di
template accumulate da aprile a giugno:
  - "Alert Daily"            (📊 ASSET — Alert Daily): bias = CONFLUENZA MTF
  - sessioni                 (🗽 NY / 🇬🇧 LONDON / 🌏 ASIA — ASSET): bias riga in alto
  - "DAILY CLOSE REPORT"     multi-asset (una riga per asset)
  - recap/buongiorno/preview/forex factory -> tipizzati, senza bias
Asset inclusi anche i dismessi (GBPUSD, SP500). Lampadine 🟢/🔴/🟡 -> +1/-1/0.

I prezzi: si tolgono le virgole delle migliaia (NASDAQ/BTC/SP500) e si parsa
float; nessun asset usa la virgola come decimale, quindi è sicuro.

Uso:
    python -m analysis.veltrix.parse_alphanalist
Output: analysis/veltrix/signals.csv , analysis/veltrix/signals.jsonl
"""

from __future__ import annotations

import csv
import glob
import json
import re
import sys
from pathlib import Path

ASSETS = ["XAUUSD", "EURUSD", "NASDAQ", "BTCUSD", "GBPUSD", "SP500"]
LIGHT = {"🟢": 1, "🔴": -1, "🟡": 0}
OUT = Path("analysis/veltrix")


def _num(s: str) -> float | None:
    s = s.strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _msg_type(t: str) -> str:
    h = t.strip().split("\n", 1)[0].upper()
    if "ALERT DAILY" in h:
        return "alert_daily"
    if "CLOSE REPORT" in h:
        return "close_report"
    if "DAILY RECAP" in h or "RECAP" in h or "BUONANOTTE" in h:
        return "recap"
    if "PREVIEW" in h:
        return "preview"
    if "BUONGIORNO" in h:
        return "buongiorno"
    if "FOREX FACTORY" in h:
        return "forex_factory"
    if "ASIA SESSION" in h:
        return "asia_session"
    if "LONDON" in h:
        return "london_session"
    if "NY SESSION" in h or "NEW YORK" in h:
        return "ny_session"
    return "other"


def _asset_in(s: str) -> str | None:
    up = s.upper()
    for a in ASSETS:
        if a in up:
            return a
    # SP500 a volte come "SP 500" o "SP#"
    if re.search(r"\bSP\s?500\b", up):
        return "SP500"
    return None


def _lights(t: str) -> tuple[int | None, int | None, int | None]:
    def find(*pats):
        for p in pats:
            m = re.search(p, t)
            if m:
                return LIGHT.get(m.group(1))
        return None
    d = find(r"Daily\s*:\s*([🟢🔴🟡])", r"\bD\s*:\s*([🟢🔴🟡])")
    h4 = find(r"4H\s*:\s*([🟢🔴🟡])")
    h1 = find(r"1H\s*:\s*([🟢🔴🟡])")
    return d, h4, h1


def _bias_norm(raw: str) -> tuple[str, bool]:
    raw = raw.upper()
    forte = "FORTE" in raw
    if "LONG" in raw:
        return "long", forte
    if "SHORT" in raw:
        return "short", forte
    if "NEUTR" in raw:
        return "neutral", False
    return "", False


def _levels(t: str) -> list[dict]:
    """Estrae livelli: righe con R:/S:/Resistenza/Supporto/PDH/PDL + prezzo + tag."""
    out = []
    for line in t.split("\n"):
        m = re.search(r"([🟢🔴⚪])[^\d]*?([\d][\d.,]*)\s*(.*)$", line)
        if not m:
            continue
        # filtro: deve sembrare una riga di livello (R/S/resistenza/supporto/PD/OB/FVG/swing)
        if not re.search(r"R:|S:|Resistenz|Supporto|PDH|PDL|PDC|OB|FVG|Swing|Max Ieri|Min Ieri",
                         line, re.IGNORECASE):
            continue
        price = _num(m.group(2))
        if price is None:
            continue
        side = "R" if m.group(1) == "🔴" else ("S" if m.group(1) == "🟢" else "?")
        tag = re.sub(r"\s+", " ", m.group(3)).strip(" —-:")[:40]
        out.append({"side": side, "price": price, "tag": tag})
    return out


def _score(t: str) -> float | None:
    m = re.search(r"score\s*:\s*([+-]?\d+(?:\.\d+)?)", t, re.IGNORECASE)
    return float(m.group(1)) if m else None


def _price_single(t: str) -> float | None:
    for pat in (r"💰\s*([\d][\d.,]*)", r"Prezzo attuale:\s*([\d][\d.,]*)",
                r"[—|]\s*([\d][\d.,]*)\s*(?:\n|\()", r"\|\s*([\d][\d.,]*)"):
        m = re.search(pat, t)
        if m:
            v = _num(m.group(1))
            if v:
                return v
    return None


def parse_message(rec: dict) -> list[dict]:
    t = rec.get("text") or ""
    ts = rec.get("date")
    mid = rec.get("id")
    typ = _msg_type(t)
    base = {"id": mid, "ts_utc": ts, "type": typ}

    if typ == "close_report":
        # multi-asset: una riga per asset con bias + lights + prezzo + %day
        rows = []
        for line_blk in re.split(r"\n(?=[🟢🔴💥⚪🟡])", t):
            asset = _asset_in(line_blk.split("\n")[0])
            if not asset:
                continue
            mb = re.search(r"—\s*([A-Z ]*?(?:LONG|SHORT|NEUTR)[A-Z ]*)", line_blk.upper())
            bias, forte = _bias_norm(mb.group(1) if mb else "")
            d, h4, h1 = _lights(line_blk)
            mp = re.search(r"\|\s*([\d][\d.,]*)\s*([+-][\d.,]+)%", line_blk)
            price = _num(mp.group(1)) if mp else None
            daypct = _num(mp.group(2)) if mp else None
            if bias:
                rows.append({**base, "asset": asset, "bias": bias, "strength": forte,
                             "tf_d": d, "tf_4h": h4, "tf_1h": h1, "score": None,
                             "price": price, "day_pct": daypct, "levels": "[]"})
        return rows

    if typ in ("alert_daily", "ny_session", "london_session", "asia_session"):
        asset = _asset_in(t.split("\n", 1)[0]) or _asset_in(t)
        # bias: CONFLUENZA MTF: X  oppure  (emoji) LONG/SHORT/NEUTRO nelle prime righe
        mb = re.search(r"CONFLUENZA MTF\s*:?\s*([A-Z ]+)", t.upper())
        if not mb:
            mb = re.search(r"([🟢🔴⚪💥])\s*([A-Z]+(?:\s+FORTE)?)", t)
            biasraw = mb.group(2) if mb else ""
        else:
            biasraw = mb.group(1)
        bias, forte = _bias_norm(biasraw)
        d, h4, h1 = _lights(t)
        return [{**base, "asset": asset, "bias": bias, "strength": forte,
                 "tf_d": d, "tf_4h": h4, "tf_1h": h1, "score": _score(t),
                 "price": _price_single(t), "day_pct": None,
                 "levels": json.dumps(_levels(t), ensure_ascii=False)}]

    # tipi senza bias direzionale: riga minima (per contesto/conteggio)
    return [{**base, "asset": _asset_in(t), "bias": "", "strength": False,
             "tf_d": None, "tf_4h": None, "tf_1h": None, "score": None,
             "price": None, "day_pct": None, "levels": "[]"}]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    src = sorted(glob.glob("alphanalist_chat_*.jsonl"))
    if not src:
        raise SystemExit("Nessun file alphanalist_chat_*.jsonl nella root.")
    rows: list[dict] = []
    for line in open(src[0], encoding="utf-8"):
        rec = json.loads(line)
        if rec.get("sender") != "AlphaAnalist":
            continue
        rows.extend(parse_message(rec))

    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["id", "ts_utc", "type", "asset", "bias", "strength", "tf_d", "tf_4h",
            "tf_1h", "score", "price", "day_pct", "levels"]
    with open(OUT / "signals.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "signals.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Riepilogo di controllo
    from collections import Counter
    print(f"Righe totali: {len(rows)}  (da {src[0]})")
    print("Per tipo:", dict(Counter(r["type"] for r in rows)))
    directional = [r for r in rows if r["bias"]]
    print(f"\nRecord con bias direzionale: {len(directional)}")
    print("  per bias:", dict(Counter(r["bias"] for r in directional)))
    print("  per asset:", dict(Counter(r["asset"] for r in directional)))
    miss_price = sum(1 for r in directional if r["price"] is None)
    miss_tf = sum(1 for r in directional if r["tf_d"] is None)
    print(f"  senza prezzo: {miss_price}  | senza lampadine: {miss_tf}")
    print(f"\nOutput: {OUT/'signals.csv'} , {OUT/'signals.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
