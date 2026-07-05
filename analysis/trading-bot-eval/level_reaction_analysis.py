"""Level Reaction Analysis — i livelli conf=2 del Level Analyzer reagiscono piu' del caso?

Domanda: quando il prezzo tocca un livello registrato in level_analyzer/trade_records.csv,
il mercato REAGISCE (rimbalzo/rigetto) piu' spesso e piu' forte di quanto farebbe su un
livello CASUALE nello stesso contesto (stesso price path, stesso ATR, stesso lato)?

Metodo (adattato da analysis/veltrix/validate_levels.py, portato su H1 + tolleranze in ATR):
- Touch (support):    low <= zone + tol  AND  close >= zone - tol   (tol = 0.10 * atr_h1)
  Touch (resistance): high >= zone - tol AND  close <= zone + tol
- BREAK: un close H1 oltre il lato "sbagliato" (support: close < zone - tol; resistance
  speculare). Se il primo contatto chiude gia' oltre -> BREAK immediato.
- SWEEP_THEN_BREAK: penetrazione a wick + rientro (close recuperato) ma BREAK entro N barre.
- REACTION: nelle N=4 barre H1 dopo il primo touch, escursione_favorevole - escursione_avversa
  > 0 E favorevole >= 1.0 * atr_h1, senza BREAK prima.
- TOUCH_NO_REACTION: toccato, non rotto, ma reazione insufficiente (categoria residua).
- NO_TEST: mai toccato entro TOUCH_WINDOW barre H1.
- INSUFFICIENT: barre post-segnale non bastano per decidere (record troppo recente / gap dati).

Baseline random (drift control): per OGNI record reale, M=5 livelli casuali =
price -/+ uniform(0.3, 6) * atr_h1 (sotto il prezzo per i long/support, sopra per gli
short/resistance), stessi criteri, STESSO price path. Look-ahead-safe: si usano solo barre
con open >= ts_utc del record.

Uso:  python analysis/trading-bot-eval/level_reaction_analysis.py
NB: richiede rete (yfinance) e level_analyzer/trade_records.csv (gitignored, solo locale).
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from level_analyzer.feed import fetch_h1_ts  # noqa: E402  (riuso, non reinvento)

# ---- parametri (dichiarati a priori, non fittati) --------------------------
TOL_ATR = 0.10        # tolleranza touch in multipli di ATR H1 del record
N_REACT = 4           # barre H1 di osservazione dopo il primo touch
TOUCH_WINDOW = 24     # barre H1 entro cui il livello deve essere toccato (~= orizzonte
                      # di riconciliazione 24h del Level Analyzer)
M_RANDOM = 5          # livelli casuali per record
RAND_LO, RAND_HI = 0.3, 6.0   # distanza random dal prezzo, in ATR
SEED = 42
N_BOOT = 10_000
TICKER = {"XAUUSD": "GC=F", "BTCUSD": "BTC-USD"}

REACTION = "REACTION"
BREAK = "BREAK"
SWEEP = "SWEEP_THEN_BREAK"
WEAK = "TOUCH_NO_REACTION"
NO_TEST = "NO_TEST"
INSUFF = "INSUFFICIENT"


# ---------------------------------------------------------------------------
def classify(bars: list[dict], zone: float, side: str, atr: float) -> dict:
    """Classifica l'esito del livello sul price path post-segnale.

    bars: barre H1 con open-time >= ts del segnale, in ordine cronologico.
    side: 'long' (support) o 'short' (resistance).
    Ritorna: {cls, touch_idx, net_atr, fav_atr, rejection_wick, displacement}.
    """
    tol = TOL_ATR * atr
    sup = side == "long"
    res = {"cls": None, "touch_idx": None, "net_atr": None, "fav_atr": None,
           "rejection_wick": False, "displacement": False}

    # --- primo touch entro TOUCH_WINDOW ---
    touch_idx = None
    immediate_break = False
    for i, b in enumerate(bars[:TOUCH_WINDOW]):
        touched = (b["low"] <= zone + tol) if sup else (b["high"] >= zone - tol)
        if not touched:
            continue
        touch_idx = i
        closed_through = (b["close"] < zone - tol) if sup else (b["close"] > zone + tol)
        immediate_break = closed_through
        break

    if touch_idx is None:
        res["cls"] = NO_TEST if len(bars) >= TOUCH_WINDOW else INSUFF
        return res
    res["touch_idx"] = touch_idx

    tb = bars[touch_idx]
    rng_tb = tb["high"] - tb["low"]
    if rng_tb > 0:
        pos = (tb["close"] - tb["low"]) / rng_tb
        res["rejection_wick"] = (pos >= 2 / 3) if sup else (pos <= 1 / 3)

    win = bars[touch_idx + 1: touch_idx + 1 + N_REACT]

    # net excursion (in ATR) sulla finestra completa — metrica continua per il confronto
    if len(win) == N_REACT:
        hi = max(b["high"] for b in win)
        lo = min(b["low"] for b in win)
        fav = (hi - zone) if sup else (zone - lo)
        adv = (zone - lo) if sup else (hi - zone)
        res["net_atr"] = (fav - adv) / atr
        res["fav_atr"] = fav / atr

    if immediate_break:
        res["cls"] = BREAK
        return res

    # sweep: wick oltre il livello ma close recuperato (touch bar o barre successive)
    def is_sweep(b):
        return (b["low"] < zone - tol and b["close"] >= zone - tol) if sup else \
               (b["high"] > zone + tol and b["close"] <= zone + tol)

    swept = is_sweep(tb)
    for b in win:
        broke = (b["close"] < zone - tol) if sup else (b["close"] > zone + tol)
        if broke:
            res["cls"] = SWEEP if swept else BREAK
            return res
        swept = swept or is_sweep(b)

    if len(win) < N_REACT:
        res["cls"] = INSUFF
        return res

    # displacement nella direzione favorevole entro la finestra
    for b in win:
        rng = b["high"] - b["low"]
        body = b["close"] - b["open"]
        if rng >= 1.5 * atr and abs(body) >= 0.5 * rng and (body > 0) == sup:
            res["displacement"] = True
            break

    fav = res["fav_atr"]
    net = res["net_atr"]
    res["cls"] = REACTION if (net > 0 and fav >= 1.0) else WEAK
    return res


# ---------------------------------------------------------------------------
def bootstrap_diff(real_vals, rand_by_rec, stat, n_boot=N_BOOT, seed=SEED):
    """CI 95%% bootstrap della differenza stat(real) - stat(random), ricampionando i RECORD
    (cluster bootstrap: ogni record porta con se' i suoi M livelli random)."""
    rng = np.random.default_rng(seed)
    idx = np.arange(len(real_vals))
    diffs = []
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        rv = [real_vals[i] for i in s]
        cv = [v for i in s for v in rand_by_rec[i]]
        if not rv or not cv:
            continue
        diffs.append(stat(rv) - stat(cv))
    diffs = np.array(diffs)
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def rate(vals):
    return 100.0 * sum(vals) / len(vals) if vals else float("nan")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    df = pd.read_csv(ROOT / "level_analyzer" / "trade_records.csv")
    print(f"Record totali nel CSV: {len(df)}")

    # --- price path: 2 fetch totali, cache per ticker ---
    paths: dict[str, list[dict]] = {}
    for asset, tk in TICKER.items():
        try:
            paths[asset] = fetch_h1_ts(tk, days=30)
            print(f"  H1 {asset} ({tk}): {len(paths[asset])} barre "
                  f"{paths[asset][0]['t']:%Y-%m-%d %H:%M} -> {paths[asset][-1]['t']:%Y-%m-%d %H:%M}")
        except Exception as e:  # noqa: BLE001
            print(f"  H1 {asset} ({tk}): FETCH FALLITO ({e})")

    rng = np.random.default_rng(SEED)
    rows = []          # un dict per record analizzato
    skipped = Counter()  # (asset, motivo)

    for ridx, r in df.iterrows():
        asset = r["asset"]
        if asset not in paths:
            skipped[(asset, "no_feed")] += 1
            continue
        ts = datetime.fromisoformat(str(r["ts_utc"]))
        atr = float(r["atr_h1"])
        if not np.isfinite(atr) or atr <= 0:
            skipped[(asset, "atr_invalido")] += 1
            continue
        bars = [b for b in paths[asset] if b["t"] >= ts]
        if len(bars) < 3:
            skipped[(asset, "poche_barre_post")] += 1
            continue

        real = classify(bars, float(r["zone"]), r["side"], atr)
        if real["cls"] == INSUFF:
            skipped[(asset, "finestra_incompleta")] += 1
            continue

        rand_results = []
        rand_near = []          # sensibilita': random distance-matched ai livelli reali
        price = float(r["price"])
        sign = -1.0 if r["side"] == "long" else 1.0
        for _ in range(M_RANDOM):
            u = rng.uniform(RAND_LO, RAND_HI)
            rz = price + sign * u * atr
            rand_results.append(classify(bars, rz, r["side"], atr))
            un = rng.uniform(0.05, 0.30)   # come dist_atr tipico dei record reali
            rand_near.append(classify(bars, price + sign * un * atr, r["side"], atr))

        rows.append({
            "asset": asset, "side": r["side"], "regime": r["regime"],
            "types": str(r["types"]), "outcome": r["outcome"],
            "real_R": r["real_R"], "real": real, "rand": rand_results,
            "rand_near": rand_near,
        })

    # =====================================================================
    print("\n===== 1) SANITY =====")
    for asset in TICKER:
        n = sum(1 for x in rows if x["asset"] == asset)
        sk = sum(v for (a, _), v in skipped.items() if a == asset)
        print(f"  {asset}: analizzati={n}  scartati={sk}")
    for (a, why), v in sorted(skipped.items()):
        print(f"    scartati {a} per '{why}': {v}")

    print("\n===== 2) DISTRIBUZIONE ESITI (livelli reali) =====")
    order = [REACTION, WEAK, BREAK, SWEEP, NO_TEST]
    for asset in TICKER:
        sub = [x for x in rows if x["asset"] == asset]
        if not sub:
            continue
        c = Counter(x["real"]["cls"] for x in sub)
        n = len(sub)
        parts = "  ".join(f"{k}={c.get(k,0)} ({100*c.get(k,0)/n:.0f}%)" for k in order)
        print(f"  {asset} (n={n}): {parts}")
        rejw = [x["real"]["rejection_wick"] for x in sub if x["real"]["cls"] == REACTION]
        disp = [x["real"]["displacement"] for x in sub if x["real"]["cls"] == REACTION]
        if rejw:
            print(f"    qualificatori tra le REACTION: rejection_wick={rate(rejw):.0f}%  "
                  f"displacement={rate(disp):.0f}%")

    print("\n===== 3) REALE vs RANDOM (drift control) =====")
    tested_cls = {REACTION, WEAK, BREAK, SWEEP}
    for asset in TICKER:
        sub = [x for x in rows if x["asset"] == asset]
        if not sub:
            continue
        n = len(sub)
        print(f"\n  --- {asset} (n record={n}, random={n*M_RANDOM}) ---")

        # (a) tasso di touch (contesto: un livello random lontano spesso non viene testato)
        real_touch = [x["real"]["cls"] in tested_cls for x in sub]
        rand_touch = [[c["cls"] in tested_cls for c in x["rand"] if c["cls"] != INSUFF]
                      for x in sub]
        print(f"  touch entro {TOUCH_WINDOW}h: reale={rate(real_touch):.0f}%  "
              f"random={rate([v for g in rand_touch for v in g]):.0f}%")

        # (b) REACTION rate CONDIZIONATO al touch — il test principale
        real_r = [x["real"]["cls"] == REACTION for x in sub if x["real"]["cls"] in tested_cls]
        rand_r_by_rec, keep = [], []
        for x in sub:
            g = [c["cls"] == REACTION for c in x["rand"] if c["cls"] in tested_cls]
            if x["real"]["cls"] in tested_cls and g:
                keep.append(x["real"]["cls"] == REACTION)
                rand_r_by_rec.append(g)
        rr_real = rate(real_r)
        rr_rand = rate([v for g in rand_r_by_rec for v in g])
        print(f"  %REACTION | touch: reale={rr_real:.1f}% (n={len(real_r)})  "
              f"random={rr_rand:.1f}% (n={sum(len(g) for g in rand_r_by_rec)})")
        if len(keep) >= 5:
            lo, hi = bootstrap_diff(keep, rand_r_by_rec, rate)
            verdict = "PIU' del caso" if lo > 0 else ("MENO del caso" if hi < 0
                       else "NON distinguibile dal caso")
            print(f"    diff={rr_real-rr_rand:+.1f} pt  CI95%=[{lo:+.1f}, {hi:+.1f}]  -> {verdict}")

        # (c) magnitudo: escursione netta mediana (ATR) al primo touch
        real_m, rand_m_by_rec = [], []
        for x in sub:
            if x["real"]["net_atr"] is None:
                continue
            g = [c["net_atr"] for c in x["rand"] if c["net_atr"] is not None]
            if g:
                real_m.append(x["real"]["net_atr"])
                rand_m_by_rec.append(g)
        if real_m:
            med = float(np.median(real_m))
            medr = float(np.median([v for g in rand_m_by_rec for v in g]))
            print(f"  escursione netta mediana (ATR): reale={med:+.2f} (n={len(real_m)})  "
                  f"random={medr:+.2f}")
            if len(real_m) >= 5:
                lo, hi = bootstrap_diff(real_m, rand_m_by_rec,
                                        lambda v: float(np.median(v)))
                verdict = "PIU' del caso" if lo > 0 else ("MENO del caso" if hi < 0
                           else "NON distinguibile dal caso")
                print(f"    diff={med-medr:+.2f} ATR  CI95%=[{lo:+.2f}, {hi:+.2f}]  -> {verdict}")

    print("\n===== 3-bis) SENSIBILITA': random DISTANCE-MATCHED (u in [0.05, 0.30] ATR) =====")
    print("  (i random della sezione 3 stanno a 0.3-6 ATR: vengono toccati solo DOPO un big")
    print("   move, che favorisce meccanicamente il rimbalzo. Qui il random sta alla stessa")
    print("   distanza dei livelli reali: controllo di drift a parita' di timing.)")
    for asset in TICKER:
        sub = [x for x in rows if x["asset"] == asset]
        if not sub:
            continue
        real_r, rand_r_by_rec = [], []
        real_m, rand_m_by_rec = [], []
        for x in sub:
            g = [c["cls"] == REACTION for c in x["rand_near"] if c["cls"] in tested_cls]
            if x["real"]["cls"] in tested_cls and g:
                real_r.append(x["real"]["cls"] == REACTION)
                rand_r_by_rec.append(g)
            gm = [c["net_atr"] for c in x["rand_near"] if c["net_atr"] is not None]
            if x["real"]["net_atr"] is not None and gm:
                real_m.append(x["real"]["net_atr"])
                rand_m_by_rec.append(gm)
        if not real_r:
            continue
        rr_real = rate(real_r)
        rr_rand = rate([v for g in rand_r_by_rec for v in g])
        print(f"  {asset}: %REACTION|touch reale={rr_real:.1f}% vs random-near={rr_rand:.1f}%",
              end="")
        if len(real_r) >= 5:
            lo, hi = bootstrap_diff(real_r, rand_r_by_rec, rate)
            verdict = "PIU' del caso" if lo > 0 else ("MENO del caso" if hi < 0
                       else "NON distinguibile")
            print(f"  diff={rr_real-rr_rand:+.1f} pt CI95%=[{lo:+.1f},{hi:+.1f}] -> {verdict}")
        else:
            print()
        if real_m:
            med = float(np.median(real_m))
            medr = float(np.median([v for g in rand_m_by_rec for v in g]))
            lo, hi = bootstrap_diff(real_m, rand_m_by_rec, lambda v: float(np.median(v)))
            verdict = "PIU'" if lo > 0 else ("MENO" if hi < 0 else "NON dist.")
            print(f"          net mediano (ATR): reale={med:+.2f} vs random-near={medr:+.2f}"
                  f"  diff CI95%=[{lo:+.2f},{hi:+.2f}] -> {verdict}")

    print("\n===== 4) STRATIFICAZIONE =====")
    print("  --- per regime (solo livelli reali, condizionato al touch) ---")
    for reg in ("trend", "range", "transizione"):
        sub = [x for x in rows if x["regime"] == reg and x["real"]["cls"] in tested_cls]
        if not sub:
            continue
        rr = rate([x["real"]["cls"] == REACTION for x in sub])
        br = rate([x["real"]["cls"] in (BREAK, SWEEP) for x in sub])
        meds = [x["real"]["net_atr"] for x in sub if x["real"]["net_atr"] is not None]
        m = f"{np.median(meds):+.2f}" if meds else "n/a"
        print(f"  {reg:12} n={len(sub):3}  %REACTION={rr:5.1f}%  %BREAK+SWEEP={br:5.1f}%  "
              f"net mediano={m} ATR")

    print("  --- per natura del livello (componenti della colonna types; un record")
    print("      con due componenti conta in entrambe) ---")
    comp_map = defaultdict(list)
    for x in rows:
        if x["real"]["cls"] not in tested_cls:
            continue
        comps = set()
        for t in x["types"].split("|"):
            t = t.strip()
            if t.startswith("PD"):
                comps.add("PDH/PDL")
            elif t.startswith("OB"):
                comps.add("OB")
            elif t.startswith("FVG"):
                comps.add("FVG")
            elif t.startswith("Swing"):
                comps.add("Swing")
        for c in comps:
            comp_map[c].append(x)
    for c in ("Swing", "OB", "FVG", "PDH/PDL"):
        sub = comp_map.get(c, [])
        if not sub:
            continue
        rr = rate([x["real"]["cls"] == REACTION for x in sub])
        br = rate([x["real"]["cls"] in (BREAK, SWEEP) for x in sub])
        print(f"  {c:8} n={len(sub):3}  %REACTION={rr:5.1f}%  %BREAK+SWEEP={br:5.1f}%")

    print("\n===== 5) CROSS-CHECK classe-livello vs esito trade (real_R) =====")
    filled = [x for x in rows if x["outcome"] in ("win", "loss")]
    for cls in (REACTION, WEAK, BREAK, SWEEP, NO_TEST):
        sub = [x for x in filled if x["real"]["cls"] == cls]
        if not sub:
            print(f"  {cls:18} n=0")
            continue
        pos = rate([float(x["real_R"]) > 0 for x in sub])
        medR = float(np.median([float(x["real_R"]) for x in sub]))
        print(f"  {cls:18} n={len(sub):3}  %real_R>0={pos:5.1f}%  real_R mediano={medR:+.2f}")

    print("\n===== LIMITI (onesti) =====")
    print(f"  - Path H1 da yfinance ({TICKER}), non dal broker: gap weekend GC=F, possibili")
    print("    differenze di feed vs i prezzi con cui i record furono creati.")
    print("  - n piccolo su XAUUSD: i CI saranno larghi, verdetto per-asset fragile.")
    print("  - Volume/tick-proxy NON usato in questa v1 (nessun filtro di partecipazione).")
    print("  - Finestra touch 24 barre H1 e N=4 di reazione: scelte a priori, non ottimizzate.")
    print("  - I livelli random condividono il drift del path: e' proprio il controllo voluto,")
    print("    ma random vicini al prezzo vengono testati prima (bias di timing residuo).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
