"""B2 (breakout Kichev) — PASSO 0: potenza PRIMA di spendere il round 3 di `trend_momentum`.

0 trial. Richiesto dal quant-gatekeeper (parere del 2026-09-29) e dalla decisione dell'utente del
2026-09-30 (DECISIONS): il round 3 va a B2, ma si spende solo se il test puo' vedere un effetto
economicamente rilevante. Se l'MDE supera l'effetto minimo economico (costo a 3x), B2 si chiude a 0
trial come "non testabile a potenza utile", non falsificata.

Cosa NON fa: non calcola ne' stampa alcuna media direzionale degli eventi. La varianza si stima con
quantita' **indipendenti dalla direzione**: il quadrato del movimento dopo il trigger (uguale per
long e short) e il quadrato del movimento su tutti i giorni (controlli casuali a lato casuale).
L'ipotesi testata — dopo un breakout il prezzo CONTINUA nella direzione della barra — resta non vista.

Specifica usata (scelte NOSTRE, la fonte da' solo esempi — da confermare nella pre-registrazione):
- trigger: range H-L della barra t >= 2 x media dei range delle 5 barre PRECEDENTI (t-5..t-1);
- direzione: segno di close_t - open_t;
- ingresso all'apertura di t+1 (ottenibile per costruzione), uscita all'apertura di t+1+X, nessuno stop;
- unita': ATR(20) a t; loader con fusione del weekend (`backtest.load`: senza, i trigger quasi raddoppiano).

Uso: python analysis/trend/b2_potenza.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from backtest import COST_BPS, METAL_IND, atr, load, universe_from_coverage  # noqa: E402
from core.verifiche import fattore_potenza  # noqa: E402

SOGLIA = 2.0
FINESTRA = 5
ORIZZONTI = (5, 2)          # X primario proposto = 5 (l'esempio della fonte); 2 descrittivo
M_CONTROLLI = 3             # controlli casuali per evento (come nei motori trend)
UNIVERSI = {
    "tutti i 30": None,
    "fonte (commodities + crypto)": {"metal", "metal_ind", "energy", "agri", "crypto"},
    "fonte senza crypto": {"metal", "metal_ind", "energy", "agri"},
}


def eventi_e_varianze(sym: str, grp: str, X: int) -> dict:
    d = load(sym, grp)
    if len(d) < 60:
        return {}
    O, H, L, C = (d[c].to_numpy(float) for c in ("open", "high", "low", "close"))
    A = atr(H, L, C)
    rng_ = H - L
    media5 = pd.Series(rng_).shift(1).rolling(FINESTRA).mean().to_numpy()
    n = len(d)
    t_ok = np.arange(n) + 1 + X < n                      # uscita disponibile
    valido = t_ok & np.isfinite(media5) & (media5 > 0) & (A > 0)
    trig = valido & (rng_ >= SOGLIA * media5)
    idx = np.arange(n)
    uscita = np.minimum(idx + 1 + X, n - 1)
    ingresso = np.minimum(idx + 1, n - 1)
    mov = (O[uscita] - O[ingresso]) / np.where(A > 0, A, np.nan)   # movimento in ATR, SENZA segno di lato
    grp_cost = "metal_ind" if sym in METAL_IND else grp
    costo3 = 3 * COST_BPS.get(grp_cost, 8) / 1e4 * O[ingresso] / np.where(A > 0, A, np.nan)
    return {
        "n_eventi": int(trig.sum()),
        "date_eventi": set(d["time"].dt.normalize()[trig]),
        "mov2_eventi": mov[trig] ** 2,                 # quadrato: identico per long e short
        "mov2_tutti": mov[valido] ** 2,                # controlli a lato casuale: E[Y]=0, Var=E[mov^2]
        "costo3_eventi": costo3[trig],
    }


def main() -> int:
    uni = universe_from_coverage()
    f = fattore_potenza()
    print("=" * 96)
    print("B2 breakout Kichev — POTENZA prima del round 3 (0 trial). Nessuna media direzionale calcolata.")
    print("=" * 96)
    for X in ORIZZONTI:
        per_sym = {r.sym: (r.group, eventi_e_varianze(r.sym, r.group, X)) for r in uni.itertuples()}
        print(f"\n--- uscita a X = {X} giorni {'(PRIMARIO proposto)' if X == 5 else '(descrittivo)'}")
        print(f"  {'universo':30s} {'strum.':>6s} {'eventi':>7s} {'date':>6s} {'sd_evento':>9s} "
              f"{'sd_ctrl':>8s} {'MDE indip.':>10s} {'MDE per data':>12s} {'costo 3x':>9s}")
        for nome, gruppi in UNIVERSI.items():
            sel = [v for s, (g, v) in per_sym.items() if v and (gruppi is None or g in gruppi)]
            n = sum(v["n_eventi"] for v in sel)
            date = set().union(*[v["date_eventi"] for v in sel]) if sel else set()
            m2e = np.concatenate([v["mov2_eventi"] for v in sel])
            m2c = np.concatenate([v["mov2_tutti"] for v in sel])
            c3 = np.concatenate([v["costo3_eventi"] for v in sel])
            var_d = np.nanmean(m2e) + np.nanmean(m2c) / M_CONTROLLI
            mde_i = f * np.sqrt(var_d / n)
            mde_c = f * np.sqrt(var_d / len(date))
            print(f"  {nome:30s} {len(sel):6d} {n:7d} {len(date):6d} {np.sqrt(np.nanmean(m2e)):9.3f} "
                  f"{np.sqrt(np.nanmean(m2c)):8.3f} {mde_i:10.3f} {mde_c:12.3f} {np.nanmedian(c3):9.3f}")
    print("\nLettura (scritta PRIMA di vedere qualunque esito):")
    print("  - MDE in ATR sulla differenza appaiata (evento - media di 3 controlli a lato casuale).")
    print("  - 'indip.' tratta gli eventi come indipendenti; 'per data' conta una sola osservazione per")
    print("    giorno con trigger (limite prudente: eventi dello stesso giorno fortemente correlati).")
    print("  - costo 3x = mediana, sugli eventi, di 3 x costo di andata e ritorno in unita' di ATR.")
    print("  - Regola del gatekeeper: se l'MDE del primario SUPERA il costo 3x, il round non si spende.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
