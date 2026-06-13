"""CLI Level Analyzer — Fase A (multi-asset: XAUUSD + BTCUSD).

  python -m level_analyzer preview          # offline sui CSV esportati (test/visione)
  python -m level_analyzer scan [--notify]  # live MT5 una passata (stampa, opz. notifica)
  python -m level_analyzer run               # loop live: notifica Telegram + log forward

Non piazza ordini: solo notifica. Tu decidi e piazzi a mano.
"""
from __future__ import annotations

import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import detector, feed, notify

CFG = {
    "atr_n": 14, "k_sl": 0.5, "rr": 1.5, "cluster_tol_pct": 0.25,
    "h1_window": 120, "proximity_atr": 0.25, "max_dist_atr": 8.0,
    "poll_seconds": 300, "telegram_chat_id": "",
    "log_path": "level_analyzer/signals_log.csv",
    "assets": [
        {"name": "XAUUSD", "mt5_symbol": "XAUUSD",
         "d1_csv": "analysis/trading-bot-eval/data/XAU_spot_D1.csv",
         "h1_csv": "analysis/trading-bot-eval/data/XAU_spot_H1.csv"},
        {"name": "BTCUSD", "mt5_symbol": "BTCUSD",
         "d1_csv": "analysis/trading-bot-eval/data/BTC_spot_D1.csv",
         "h1_csv": "analysis/trading-bot-eval/data/BTC_spot_H1.csv"},
    ],
}


def _load_cfg():
    p = Path(__file__).parent / "config.yaml"
    if not p.exists():
        return
    try:
        import yaml
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for k, v in data.items():
            CFG[k] = v
    except Exception:
        pass


def _signals(prev, win, price):
    return detector.conf2_signals(
        prev, win, price, k_sl=CFG["k_sl"], rr=CFG["rr"],
        cluster_tol_pct=CFG["cluster_tol_pct"], max_dist_atr=CFG["max_dist_atr"],
        atr_val=detector.atr(win, CFG["atr_n"]))


def _print(name, sigs, price):
    print(f"-- {name}  prezzo={price}" + (f"  ATR(H1)={sigs[0]['atr']}" if sigs else ""))
    if not sigs:
        print("   nessuna zona conf=2 entro la distanza."); return
    for s in sigs:
        print(f"   {s['side']:5}  zona {s['zone']:>10}  [{', '.join(s['types'])}]  "
              f"dist {s['dist_atr']:>4} ATR   SL {s['sl']}  TP {s['tp']}  RR 1:{s['rr']}")


def _log(asset, sig, price):
    p = Path(CFG["log_path"]); new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts_utc", "asset", "side", "zone", "sl", "tp", "rr",
                        "confluence", "types", "price", "dist_atr", "outcome"])
        w.writerow([datetime.now(timezone.utc).isoformat(), asset, sig["side"],
                    sig["zone"], sig["sl"], sig["tp"], sig["rr"], sig["confluence"],
                    "|".join(sig["types"]), round(price, 2), sig["dist_atr"], ""])


def cmd_preview():
    print(f"== PREVIEW offline (ultimo dato CSV) ==")
    for a in CFG["assets"]:
        try:
            prev, win, price = feed.load_offline(a["d1_csv"], a["h1_csv"], CFG["h1_window"])
            _print(a["name"], _signals(prev, win, price), round(price, 2))
        except Exception as e:
            print(f"-- {a['name']}: errore ({e})")


def cmd_scan(notify_on=False):
    print(f"== SCAN live  {datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z ==")
    for a in CFG["assets"]:
        try:
            prev, win, price = feed.fetch_mt5(a["mt5_symbol"], CFG["h1_window"])
        except Exception as e:
            print(f"-- {a['name']}: MT5 non disponibile ({e})"); continue
        sigs = _signals(prev, win, price)
        _print(a["name"], sigs, round(price, 2))
        if notify_on:
            for s in [x for x in sigs if x["dist_atr"] <= CFG["proximity_atr"]]:
                ok = notify.send_telegram(CFG["telegram_chat_id"],
                                          notify.format_signal(s, a["name"], round(price, 2)))
                _log(a["name"], s, price)
                print(f"   [alert {'inviato' if ok else 'solo-log'}] {s['side']} {s['zone']}")


def cmd_run():
    print(f"== RUN loop ogni {CFG['poll_seconds']}s (Ctrl+C per fermare) ==")
    seen = set()
    while True:
        day = datetime.now(timezone.utc).date()
        for a in CFG["assets"]:
            try:
                prev, win, price = feed.fetch_mt5(a["mt5_symbol"], CFG["h1_window"])
                for s in _signals(prev, win, price):
                    if s["dist_atr"] > CFG["proximity_atr"]:
                        continue
                    key = (day, a["name"], s["side"], s["zone"])
                    if key in seen:
                        continue
                    seen.add(key)
                    ok = notify.send_telegram(CFG["telegram_chat_id"],
                                              notify.format_signal(s, a["name"], round(price, 2)))
                    _log(a["name"], s, price)
                    print(f"{datetime.now(timezone.utc):%H:%M}Z {a['name']} alert "
                          f"{'OK' if ok else '(solo log)'}: {s['side']} {s['zone']}")
            except Exception as e:
                print(f"ciclo {a['name']} errore:", e)
        time.sleep(CFG["poll_seconds"])


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    _load_cfg()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "preview":
        cmd_preview()
    elif cmd == "scan":
        cmd_scan(notify_on=("--notify" in sys.argv))
    elif cmd == "run":
        cmd_run()
    else:
        print("comandi: preview | scan [--notify] | run")


if __name__ == "__main__":
    main()
