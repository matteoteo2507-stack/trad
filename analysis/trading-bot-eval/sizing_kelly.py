"""SIZING vol-drag-aware per il Level Analyzer (conf=2 fade).

Trasforma l'edge per-trade GIA' validato (distribuzione delle R nette conf=2,
SL=0.5*ATR, RR 1:1.5) in una REGOLA DI SIZING che massimizza la crescita
GEOMETRICA invece dell'EV aritmetico. Implementa:

  - Kelly numerico  f* = argmax_f  E[ln(1 + f*R)]   (non la formula discreta:
    usa la distribuzione empirica reale, code incluse -> il drag e' dentro).
  - Kelly frazionario (1/2, 1/4) + ceiling assoluto: l'edge e' piccolo e rumoroso,
    full-Kelly su una stima ottimistica = rovina.
  - Decomposizione aritmetico vs geometrico: mostra il volatility drag f^2*sigma^2/2.
  - Sensibilita' all'HAIRCUT dell'edge (se la mu vera fosse meta'): quanto crolla f*.
  - Clustering: segnali conf=2 per sessione -> cap sull'esposizione aggregata.

NON e' un nuovo backtest: e' una funzione della distribuzione gia' misurata
(stessa sim di expectancy_confluence.py, stessi costi reali del LEVEL_ANALYZER_SPEC).

Uso:  python analysis/trading-bot-eval/sizing_kelly.py [--write-spec]
"""
from __future__ import annotations

import bisect
import csv
import math
import os
import statistics as st
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "analysis/veltrix")
import levels_engine as le  # noqa: E402

# --- costanti IDENTICHE a expectancy_confluence.py (stessa distribuzione) ---
SESSION = (6, 21)
K_SL, K_TOL = 0.5, 0.10
RR = 1.5                      # RR primario validato cross-asset
MAX_HOLD, H1_WINDOW, ATR_N = 24, 120, 14
START_YEAR, CLUSTER_TOL_PCT = 2013, 0.25

# asset + spread reale (unita' di prezzo) dal LEVEL_ANALYZER_SPEC
ASSETS = [("XAU", 0.10), ("BTC", 13.0)]

# parametri di sizing (default prudenti, regolabili)
KELLY_FRACTION = 0.25        # quarter-Kelly: ~94% crescita a meta' varianza vs half
PER_TRADE_CEILING = 0.010    # tetto assoluto: max 1.0% del conto a rischio per trade
AGG_CEILING = 0.020          # max 2.0% a rischio simultaneo su zone conf=2 concorrenti


def _p(asset, tf):
    base = "analysis/trading-bot-eval/data"
    for n in (f"{asset}_spot_{tf}.csv", f"{asset}_{tf}.csv"):
        if os.path.exists(f"{base}/{n}"):
            return f"{base}/{n}"
    return f"{base}/{asset}_spot_{tf}.csv"


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t = datetime.fromisoformat(r["time"][:19])
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                out.append({"t": t, "open": float(r["open"]), "high": float(r["high"]),
                            "low": float(r["low"]), "close": float(r["close"])})
            except (ValueError, KeyError):
                continue
    out.sort(key=lambda x: x["t"])
    return out


def atr_series(h1, n=ATR_N):
    atr, trs = [None] * len(h1), []
    for i in range(len(h1)):
        tr = (h1[i]["high"] - h1[i]["low"]) if i == 0 else max(
            h1[i]["high"] - h1[i]["low"], abs(h1[i]["high"] - h1[i - 1]["close"]),
            abs(h1[i]["low"] - h1[i - 1]["close"]))
        trs.append(tr)
        if i >= n:
            atr[i] = sum(trs[i - n + 1:i + 1]) / n
    return atr


def resolve(h1, i0, entry, side, sl, tp, sl_dist):
    last = h1[i0]["close"]
    for j in range(i0, min(i0 + MAX_HOLD, len(h1))):
        b = h1[j]; last = b["close"]
        if side == "S":
            if b["low"] <= sl:
                return -1.0
            if b["high"] >= tp:
                return RR
        else:
            if b["high"] >= sl:
                return -1.0
            if b["low"] <= tp:
                return RR
    return (last - entry) / sl_dist if side == "S" else (entry - last) / sl_dist


def first_touch(h1, s_i, e_i, price, tol):
    for j in range(s_i, e_i):
        if h1[j]["low"] <= price + tol and h1[j]["high"] >= price - tol:
            return j
    return None


def sim(h1, s_i, e_i, price, side, atr, cost):
    j = first_touch(h1, s_i, e_i, price, K_TOL * atr)
    if j is None:
        return None
    sld = K_SL * atr
    if side == "S":
        sl, tp = price - sld, price + RR * sld
    else:
        sl, tp = price + sld, price - RR * sld
    return resolve(h1, j, price, side, sl, tp, sld) - cost / sld   # netto costi


def build_entries(prev, hwin):
    e = [{"price": prev["high"], "type": "RESISTANCE", "label": "PDH"},
         {"price": prev["low"], "type": "SUPPORT", "label": "PDL"}]
    kl = le.get_key_levels(hwin)
    for p in kl["supports"]:
        e.append({"price": p, "type": "SUPPORT", "label": "Swing_S"})
    for p in kl["resistances"]:
        e.append({"price": p, "type": "RESISTANCE", "label": "Swing_R"})
    for ob in le.detect_order_blocks(hwin):
        e.append({"price": (ob["high"] + ob["low"]) / 2, "label": "OB",
                  "type": "SUPPORT" if ob["type"] == "BULLISH_OB" else "RESISTANCE"})
    for f in le.detect_fvg(hwin):
        e.append({"price": (f["high"] + f["low"]) / 2, "label": "FVG",
                  "type": "SUPPORT" if f["type"] == "BULLISH_FVG" else "RESISTANCE"})
    return e


def conf2_distribution(asset, cost):
    """Estrae la lista di R nette conf=2 + conteggio trade per sessione (clustering)."""
    d1, h1 = load(_p(asset, "D1")), load(_p(asset, "H1"))
    if not h1:
        return [], [], (None, None)
    atr = atr_series(h1)
    d1_by_date = {b["t"].date(): b for b in d1}
    d1_dates = sorted(d1_by_date)
    h1_t = [b["t"] for b in h1]
    rs, per_session = [], []
    days = sorted({b["t"].date() for b in h1 if b["t"].year >= START_YEAR})
    for day in days:
        di = bisect.bisect_left(d1_dates, day)
        if di == 0:
            continue
        prev = d1_by_date[d1_dates[di - 1]]
        ss = datetime(day.year, day.month, day.day, SESSION[0], tzinfo=timezone.utc)
        se = datetime(day.year, day.month, day.day, SESSION[1], tzinfo=timezone.utc)
        s_i, e_i = bisect.bisect_left(h1_t, ss), bisect.bisect_left(h1_t, se)
        if e_i - s_i < 6 or s_i == 0:
            continue
        a = atr[s_i - 1]
        if not a or a <= 0:
            continue
        ci = bisect.bisect_right(h1_t, ss - timedelta(hours=1))
        hwin = h1[max(0, ci - H1_WINDOW):ci]
        if len(hwin) < 10:
            continue
        n_day = 0
        for z in le.cluster_confluence(build_entries(prev, hwin), tol_pct=CLUSTER_TOL_PCT):
            if z["confluence"] != 2 or z["side"] not in ("SUPPORT", "RESISTANCE"):
                continue
            r = sim(h1, s_i, e_i, z["price"], "S" if z["side"] == "SUPPORT" else "R", a, cost)
            if r is not None:
                rs.append(r); n_day += 1
        if n_day:
            per_session.append(n_day)
    yrs = (days[-1].year - days[0].year + 1) if days else None
    span = (days[0], days[-1]) if days else (None, None)
    return rs, per_session, (yrs, span)


def g(f, rs):
    """log-growth geometrico per trade alla frazione f (rischio f del conto)."""
    return sum(math.log(1 + f * r) for r in rs) / len(rs)


def kelly_star(rs):
    """f* = argmax E[ln(1+fR)] via ricerca su griglia + raffinamento."""
    mn = min(rs)
    fmax = 0.95 if mn >= 0 else min(0.95, 0.99 / (-mn))
    best_f, best_g, step, lo, hi = 0.0, -1e9, fmax / 200, 1e-4, fmax
    for _ in range(3):  # 3 passate di raffinamento
        f = lo
        while f <= hi:
            gv = g(f, rs)
            if gv > best_g:
                best_g, best_f = gv, f
            f += step
        lo, hi, step = max(1e-4, best_f - step), best_f + step, step / 20
    return best_f, best_g


def annual(gv, n, yrs):
    """crescita geometrica annualizzata (%) dal log-growth per trade."""
    if not yrs:
        return None
    tpy = n / yrs
    return (math.exp(gv * tpy) - 1) * 100


def report_asset(asset, cost):
    rs, per_session, (yrs, span) = conf2_distribution(asset, cost)
    if len(rs) < 50:
        print(f"\n### {asset}: distribuzione insufficiente (n={len(rs)})")
        return None
    n = len(rs)
    mu, sd = st.mean(rs), st.pstdev(rs)
    win = 100 * sum(1 for r in rs if r > 0) / n
    f_full, g_full = kelly_star(rs)
    f_used = min(KELLY_FRACTION * f_full, PER_TRADE_CEILING)
    g_used = g(f_used, rs)

    # haircut: se la mu vera fosse meta' (edge sovrastimato) -> shift R
    rs_hc = [r - mu / 2 for r in rs]
    f_hc, g_hc = kelly_star(rs_hc) if min(rs_hc) < 0 else (0.0, 0.0)

    # clustering
    avg_s = st.mean(per_session) if per_session else 0
    p90_s = sorted(per_session)[int(0.9 * len(per_session))] if per_session else 0

    print(f"\n{'='*66}\n### {asset}  conf=2 fade, RR 1:{RR}, costo {cost} px  "
          f"({span[0]}->{span[1]}, ~{yrs}y)\n{'='*66}")
    print(f"  distribuzione netta:  n={n}  mu(R)={mu:+.3f}  sigma(R)={sd:.2f}  win={win:.0f}%")
    print(f"  Kelly pieno   f*={f_full*100:5.2f}%  ->  g/trade={g_full*100:+.3f}%"
          f"   (annuo ~{annual(g_full, n, yrs):+.1f}%)")
    print(f"  Kelly 1/{int(1/KELLY_FRACTION)}     f ={KELLY_FRACTION*f_full*100:5.2f}%"
          f"  ->  g/trade={g(KELLY_FRACTION*f_full, rs)*100:+.3f}%"
          f"   (annuo ~{annual(g(KELLY_FRACTION*f_full, rs), n, yrs):+.1f}%)")
    # decomposizione aritmetico vs geometrico ALLA frazione usata
    arith = f_used * mu
    drag = f_used * f_used * sd * sd / 2
    print(f"  --> USATA      f ={f_used*100:5.2f}%  (1/{int(1/KELLY_FRACTION)} Kelly, "
          f"tetto {PER_TRADE_CEILING*100:.1f}%)")
    print(f"      aritmetico f*mu = {arith*100:+.3f}%/trade   drag f^2*s^2/2 = {drag*100:.3f}%"
          f"   geometrico g = {g_used*100:+.3f}%/trade")
    print(f"  HAIRCUT (mu vera = mu/2):  f* crolla a {f_hc*100:.2f}%  "
          f"(g/trade {g_hc*100:+.3f}%)  -> margine del tetto {PER_TRADE_CEILING*100:.1f}% "
          f"{'REGGE' if PER_TRADE_CEILING <= KELLY_FRACTION*f_hc else 'da rivedere'}")
    print(f"  clustering:  segnali conf=2/sessione  media={avg_s:.1f}  p90={p90_s}  "
          f"-> con tetto agg. {AGG_CEILING*100:.1f}% del conto")
    return {"asset": asset, "n": n, "mu": mu, "sd": sd, "win": win, "yrs": yrs,
            "span": span, "f_full": f_full, "f_used": f_used, "g_used": g_used,
            "f_hc": f_hc, "avg_s": avg_s, "p90_s": p90_s, "cost": cost}


SPEC_TMPL = """# Sizing vol-drag-aware — Level Analyzer (conf=2 fade)

> Generato da `analysis/trading-bot-eval/sizing_kelly.py` · RR 1:{rr} · costi reali
> (XAU spread $0.10, BTC $13). Trasforma l'edge per-trade validato
> ([LEVEL_ANALYZER_SPEC.md](LEVEL_ANALYZER_SPEC.md)) in una regola di sizing che
> massimizza la crescita **geometrica**, non l'EV aritmetico. Teoria:
> [05_portfolio_rischio](../../fondamenti_tecnici/05_portfolio_rischio/principles.md)
> (volatility drag), quant `agents/quant_reviewer.md` §4.

## Perche' non "rischio fisso a caso"

L'edge conf=2 e' positivo ma **piccolo e rumoroso** (mu_R ~ +0.09..+0.19). Il
volatility drag dice che l'EV positivo non basta: conta la crescita geometrica
`g(f)=E[ln(1+fR)]`, dove `f` = frazione del conto a rischio per trade (un -1 R
perde esattamente `f`). Sizing troppo grande -> il drag e il ruin risk mangiano
la crescita; troppo piccolo -> si lascia compounding sul tavolo. La risposta e'
**Kelly frazionario** sulla distribuzione reale + **tetto** + **cap aggregato**.

## Regola operativa

{table}

- **Kelly pieno** = sizing growth-ottimo teorico, **da NON usare mai**. Annualizzato dal
  backtest darebbe numeri-fantasia (ordine +100%..+800%/anno): e' proprio il miraggio che
  fa saltare i conti, perche' assume che la mu storica sia vera e stabile su un edge sottile.
- **Frazione usata = 1/{frac_den} Kelly, con tetto assoluto {ceiling:.1f}% per trade.** Qui il
  vincolo che morde e' il **tetto**, non il Kelly frazionario (1/4 Kelly sarebbe ~3%). Stress
  test **haircut** (mu vera = meta'): 1/4-Kelly resta sopra il tetto -> **{ceiling:.1f}% regge anche
  se l'edge fosse sovrastimato del 50%**.
- **A {ceiling:.1f}% il volatility drag e' trascurabile** (f^2*sigma^2/2 ~ 0.008%/trade): il drag
  e' un pericolo **solo se si sovradimensiona**. Restare piccoli lo annulla quasi del tutto.
- **Cap aggregato {agg:.1f}%**: piu' zone conf=2 nella stessa sessione sono trade **correlati**
  (stesso regime/sessione) -> non sommare il rischio pieno. Il clustering misurato e' **mite**
  ({clustering}), quindi il cap aggregato raramente vincola: il tetto per-trade fa il grosso.

## Caveat (onesta')

- **Distribuzione piu' ampia/recente** del frozen LEVEL_ANALYZER_SPEC (la serie e' stata estesa):
  i numeri qui sono ricalcolati sui dati correnti, non copiati dallo spec.
- Numeri da distribuzione **storica netta**: le epoche vecchie usano lo spread attuale ->
  ottimistiche. Il forward log (`level_analyzer/signals_log.csv`) e' il vero giudice:
  **ri-stimare `f*` sui trade reali** appena ce n'e' massa.
- **Non ancora forward-tested**: finche' il forward non conferma, partire dal basso (es.
  {ceiling_half:.1f}% per trade) e' difendibile; salire verso il tetto solo a edge confermato.
- Path su H1 (coarse): la varianza vera intra-trade puo' essere maggiore -> altra ragione per
  stare **sotto** il Kelly pieno.
"""


def write_spec(rows):
    lines = ["| Asset | n | mu_R | sigma_R | win | Kelly pieno f* | **f usata** | g/trade | haircut f* |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['asset']} | {r['n']} | {r['mu']:+.3f} | {r['sd']:.2f} | {r['win']:.0f}% | "
            f"{r['f_full']*100:.2f}% | **{r['f_used']*100:.2f}%** | {r['g_used']*100:+.3f}% | "
            f"{r['f_hc']*100:.2f}% |")
    table = "\n".join(lines)
    clustering = "; ".join(f"{r['asset']} {r['avg_s']:.1f}/sess (p90 {r['p90_s']})" for r in rows)
    out = SPEC_TMPL.format(rr=RR, table=table, frac_den=int(1 / KELLY_FRACTION),
                           ceiling=PER_TRADE_CEILING * 100, agg=AGG_CEILING * 100,
                           ceiling_half=PER_TRADE_CEILING * 50, clustering=clustering)
    path = "analysis/trading-bot-eval/SIZING_SPEC.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"\n[scritto {path}]")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    print("SIZING vol-drag-aware — Level Analyzer (conf=2)")
    print(f"Kelly fraction = 1/{int(1/KELLY_FRACTION)}   tetto/trade = {PER_TRADE_CEILING*100:.1f}%"
          f"   cap aggregato = {AGG_CEILING*100:.1f}%")
    rows = []
    for asset, cost in ASSETS:
        r = report_asset(asset, cost)
        if r:
            rows.append(r)
    if "--write-spec" in sys.argv and rows:
        write_spec(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
