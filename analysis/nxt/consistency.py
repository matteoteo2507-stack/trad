"""Consistency rule (best-day %) su nxt_fade — compatibilita' con le prop firm.

DOMANDA: molte prop impongono una "consistency rule" che limita quanta parte del profitto
puo' venire da un singolo giorno (es. il 40% best-day di Alpha Capital). Con un payoff 1:3
il P&L giornaliero e' a code grasse PER COSTRUZIONE: pochi giorni fanno il risultato.
Non si accetta ne' si rifiuta a occhio -> si misura sulla distribuzione reale.

METODO: si rigioca la config A1 (FADE, pre-registrata in closure.py) catturando anche la
BARRA DI USCITA, cosi' da poter aggregare le R per GIORNO DI CHIUSURA (e' quando il P&L
colpisce il conto). Poi, su finestre mobili di lunghezza pari ai periodi di payout tipici,
si calcola  best_day / profitto_totale  e si conta quante finestre sforerebbero la soglia.

ASSUNZIONI dichiarate:
  - rischio a frazione fissa per trade -> la R e' proporzionale al denaro (una R = un %).
  - tutti e 6 gli strumenti girano in parallelo sullo stesso conto (e' il caso reale).
  - si considerano solo le finestre con profitto NETTO POSITIVO: la consistency rule morde
    quando chiedi il payout, e il payout lo chiedi se sei in profitto.
  - risoluzione PESSIMISTICA (SL prima di TP se entrambi nella stessa barra), come da spec.

NB: come in closure.py, i trade che non si risolvono entro MAX_HOLD vengono scartati
(nessuna R realizzata). La spec leggibile prevede invece un time-stop a mercato: la
discrepanza e' ereditata dal motore pre-registrato e NON viene corretta qui.

Uso: python analysis/nxt/consistency.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import backtest as bt  # noqa: E402

BE_AT = 2.0
# soglie di consistency rule osservate sul mercato (Alpha Capital = 40%)
THRESHOLDS = (0.30, 0.40, 0.50)
# lunghezze finestra in giorni di calendario: bi-settimanale, mensile, bimestrale
WINDOWS = (14, 30, 60)


def sim_a1(leg, H, L, sym, cost_mult=1.0):
    """Config A1 (FADE mirror 1:3) — identica a closure.sim, ma ritorna anche exit_idx."""
    side, hi, lo, rng, b, cb = (leg["side"], leg["hi"], leg["lo"], leg["rng"],
                                leg["end_idx"], leg["conf"])
    buy_leg = (side == "BUY")

    entry = (hi - 0.5 * rng) if buy_leg else (lo + 0.5 * rng)
    pos_long = not buy_leg                      # FADE: posizione invertita
    risk = 0.286 * rng
    if risk <= 0:
        return None
    if pos_long:
        sl, tp = entry - risk, entry + 3.0 * risk
    else:
        sl, tp = entry + risk, entry - 3.0 * risk
    be = entry + BE_AT * risk if pos_long else entry - BE_AT * risk

    f = None
    for j in range(max(cb, b + 1), min(b + 1 + bt.FILL_WINDOW, len(H))):
        touched = (L[j] <= entry) if buy_leg else (H[j] >= entry)
        if touched:
            f = j
            break
    if f is None:
        return None

    be_on, sl_cur = False, sl
    for j in range(f, min(f + bt.MAX_HOLD, len(H))):
        if pos_long:
            if not be_on and H[j] >= be:
                be_on, sl_cur = True, entry
            hit_sl, hit_tp = L[j] <= sl_cur, H[j] >= tp
        else:
            if not be_on and L[j] <= be:
                be_on, sl_cur = True, entry
            hit_sl, hit_tp = H[j] >= sl_cur, L[j] <= tp
        if hit_sl:                              # PESSIMISTICO: SL vince i pareggi di barra
            r = (0.0 if be_on else -1.0)
            outcome = "BE" if be_on else "SL"
            break
        if hit_tp:
            r, outcome = 3.0, "TP"
            break
    else:
        return None                             # non risolto entro MAX_HOLD -> scartato

    cost_R = bt.SPREAD.get(sym, 0.0) * cost_mult / risk
    return {"asset": sym, "entry_idx": f, "exit_idx": j,
            "R": r - cost_R, "outcome": outcome}


def collect():
    rows = []
    for sym in bt.ASSETS:
        try:
            d = bt.load_h1(sym)
        except FileNotFoundError:
            continue
        H, L, C = d["high"].values, d["low"].values, d["close"].values
        times = d["time"].values
        A = bt.atr(H, L, C)
        for lg in bt.build_legs(bt.zigzag(H, L), A):
            t = sim_a1(lg, H, L, sym)
            if t is not None:
                t["exit_time"] = times[t["exit_idx"]]
                rows.append(t)
    return pd.DataFrame(rows)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    df = collect()
    if df.empty:
        print("Nessun trade: dati H1 mancanti?")
        return

    df["exit_date"] = pd.to_datetime(df["exit_time"]).dt.normalize()
    daily = df.groupby("exit_date")["R"].sum().sort_index()
    # calendario pieno: i giorni senza chiusure valgono 0
    full = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full, fill_value=0.0)

    print("=" * 84)
    print("CONSISTENCY RULE — nxt_fade (config A1 pre-registrata), pool 6 asset H1")
    print("=" * 84)
    print(f"Trade risolti      : {len(df)}")
    print(f"Periodo            : {daily.index.min().date()} -> {daily.index.max().date()}")
    print(f"E[R] per trade     : {df['R'].mean():+.3f}   win% (TP) = {100 * (df['outcome'] == 'TP').mean():.1f}")
    print(f"Esiti              : " + "  ".join(
        f"{k}={v}" for k, v in df["outcome"].value_counts().items()))
    act = daily[daily != 0.0]
    print(f"Giorni con chiusure: {len(act)} su {len(daily)} ({100 * len(act) / len(daily):.1f}%)")
    print(f"R giornaliera      : max={daily.max():+.2f}  min={daily.min():+.2f}  "
          f"media={daily.mean():+.4f}")

    print("\n" + "-" * 84)
    print("QUOTA DEL GIORNO MIGLIORE SUL PROFITTO DELLA FINESTRA")
    print("  (solo finestre con profitto netto POSITIVO — sono quelle in cui chiedi il payout)")
    print("-" * 84)
    print(f"{'finestra':>10} {'n fin.':>8} {'% in utile':>11} {'mediana':>9} {'media':>8} "
          + "  ".join(f"{'>' + str(int(t * 100)) + '%':>7}" for t in THRESHOLDS))

    for w in WINDOWS:
        tot = daily.rolling(w).sum()
        best = daily.rolling(w).max()
        ok = tot > 0
        share = (best[ok] / tot[ok]).clip(upper=1.0)
        n_all, n_pos = int(tot.notna().sum()), int(ok.sum())
        viol = [100 * float((share > t).mean()) for t in THRESHOLDS]
        print(f"{str(w) + ' giorni':>10} {n_all:>8} {100 * n_pos / n_all:>10.1f}% "
              f"{share.median():>8.1%} {share.mean():>7.1%} "
              + "  ".join(f"{v:>6.1f}%" for v in viol))

    print("\n" + "-" * 84)
    print("LETTURA")
    print("-" * 84)
    print("Le colonne '>N%' sono la percentuale di finestre in utile in cui il giorno migliore")
    print("supera la soglia: e' la frequenza con cui la consistency rule BLOCCHEREBBE il payout.")
    print("Con payoff 1:3 e trade sparsi, un singolo TP puo' da solo superare il profitto netto")
    print("della finestra -> quota vicina o pari al 100%.")


if __name__ == "__main__":
    main()
