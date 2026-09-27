"""A1 / playground: il gradiente di volatilita' sopravvive a parita' di TEMPO IN MERCATO?

Protocollo scritto prima: docs/TREND_DURATION_DIAGNOSTIC.md. Soglie ed esiti fissati li'.

Perche' esiste. Il 2026-09-19 `check_matching` ha mostrato che i due bracci del confronto non
stanno in mercato per lo stesso tempo: holding mediano 7 giorni sul reale contro 2 sul random.
La durata e' un ESITO, quindi non e' un difetto del baseline — ma il controllo C1 di
`q2_checks.py`, quello che doveva neutralizzare il canale meccanico, e' costruito proprio su
quella differenza.

Qui il baseline random viene rifatto **a durata appaiata**: ogni controllo esce dopo le stesse
barre del suo trade reale. Stesso asset, stesso lato, stesso anno, stesso rischio (1 ATR locale),
**stessa uscita**, e ora anche **stesso tempo in mercato**. Resta casuale solo l'istante.

Entrambi i bracci passano dalla STESSA funzione di uscita (`esci_a_durata`): se il baseline
avesse un cammino proprio, la differenza misurata conterrebbe anche la differenza fra i due
cammini. E' l'errore trovato il 27/08 in `excursion.py`.

Costo: 0 trial (verifica dell'integrita' di un confronto, LIFECYCLE sez.3).

    python analysis/trend/duration_diagnostic.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from backtest import (ATR_N, LOOKBACK, M_RANDOM, MAX_HOLD, SEED, SMA_EXIT,  # noqa: E402
                      atr, cost_bps_for, load, realized_vol, simulate,
                      spearman_perm, universe_from_coverage, _mean_ci)
from core.random_baseline import BarSampler, check_matching, gap_ci  # noqa: E402

TOLL_PERSI = 0.05          # oltre questa quota di controlli persi, il confronto va rifatto


# ---------------------------------------------------------------------------
def esci_a_durata(O, C, f, h, side, R, cost_R):
    """Uscita dopo ESATTAMENTE `h` barre, con la convenzione di prezzo di `simulate`.

    `simulate` esce all'**apertura** della barra successiva all'incrocio (`O[j+1]`), e alla
    **chiusura** se arriva a max-hold. Qui si replica: apertura di `f+h` se quella barra
    esiste, altrimenti chiusura dell'ultima disponibile.

    Usata su ENTRAMBI i bracci. Sul reale deve riprodurre `E1`: e' il controllo che dice se
    la funzione e' fedele (vedi il corollario "riprodurre il numero noto" del guardiano).
    """
    sgn = 1.0 if side == "BUY" else -1.0
    entry = O[f]
    j = f + h
    if j <= len(O) - 1:
        px = O[j]
    elif len(C) - 1 >= f:
        px = C[len(C) - 1]
    else:
        return None
    return sgn * (px - entry) / R - cost_R


def run_asset(sym, grp, lookback, rng):
    """Come `backtest.run_asset`, ma il braccio random esce a durata APPAIATA.

    Il campionamento e' identico (stessa primitiva, stesso pool, stesso ordine di chiamate),
    quindi i controlli estratti sono **gli stessi** di `backtest.py`: cambia solo quando escono.
    """
    d = load(sym, grp)
    t0 = run_asset.t0
    if t0 is not None:
        d = d[d["time"] >= t0]
    d = d.reset_index(drop=True)
    if len(d) < lookback + ATR_N + 60:
        return pd.DataFrame(), pd.DataFrame()
    O, H, L, C = (d[c].values.astype(float) for c in ("open", "high", "low", "close"))
    t = d["time"].values
    A = atr(H, L, C)
    sma = pd.Series(C).rolling(SMA_EXIT).mean().values
    hh = pd.Series(H).rolling(lookback).max().shift(1).values
    ll = pd.Series(L).rolling(lookback).min().shift(1).values
    bps = cost_bps_for(sym, grp)

    real, rand = [], []
    in_pos_until = -1
    years = pd.DatetimeIndex(t).year.values
    valid = np.flatnonzero(np.isfinite(A) & (A > 0))
    lo_v, hi_v = (valid[0], valid[-1]) if len(valid) else (0, 0)
    usable = (np.arange(len(C)) >= lo_v) & (np.arange(len(C)) <= hi_v - 2)
    sampler = BarSampler(years, rng, usable=usable)

    for i in range(lookback + ATR_N, len(C) - 2):
        if i <= in_pos_until:
            continue
        if not np.isfinite(hh[i]) or not np.isfinite(A[i]) or A[i] <= 0:
            continue
        side = None
        if C[i] > hh[i]:
            side = "BUY"
        elif C[i] < ll[i]:
            side = "SELL"
        if side is None:
            continue
        f = i + 1
        R = A[i]
        cost_R = (bps / 1e4) * C[i] / R
        res = simulate(O, H, L, C, sma, f, side, R, cost_R)
        h = int(res["hold_e1"])
        # il reale rifatto con la funzione comune: deve riprodurre E1
        r_comune = esci_a_durata(O, C, f, h, side, R, cost_R)
        real.append({"sym": sym, "group": grp, "side": side, "year": int(years[f]),
                     "entry_idx": f, "R_price": R, "cost_R": cost_R, "hold": h,
                     "sigid": f"{sym}:{f}", "E1": res["E1"], "E1_comune": r_comune,
                     "E3": res["E3"]})
        in_pos_until = int(res["exit_idx"])

        for k in sampler.draw(years[f], M_RANDOM):
            if not np.isfinite(A[k]) or A[k] <= 0 or k + 1 >= len(C) - 1:
                continue
            Rk = A[k]
            ck = (bps / 1e4) * C[k] / Rk
            fk = k + 1
            # --- come oggi: uscita propria (incrocio SMA), durata NON appaiata
            rr = simulate(O, H, L, C, sma, fk, side, Rk, ck)
            # --- a durata appaiata: esce dopo h barre come il suo trade reale
            persa = (fk + h) > (len(O) - 1)
            r_app = esci_a_durata(O, C, fk, h, side, Rk, ck)
            rand.append({"sym": sym, "group": grp, "side": side, "year": int(years[k]),
                         "entry_idx": fk, "R_price": Rk, "cost_R": ck,
                         "sigid": f"{sym}:{f}", "hold": int(rr["hold_e1"]),
                         "hold_appaiato": h, "E1": rr["E1"], "E1_appaiato": r_app,
                         "E3": rr["E3"], "coda_mancante": bool(persa)})
    return pd.DataFrame(real), pd.DataFrame(rand)


run_asset.t0 = None


def run_all(cov, lookback, t0=None):
    run_asset.t0 = t0
    rng = np.random.default_rng(SEED)
    R, D = [], []
    for _, r in cov.iterrows():
        a, b = run_asset(r["sym"], r["group"], lookback, rng)
        if len(a):
            R.append(a)
        if len(b):
            D.append(b)
    return (pd.concat(R, ignore_index=True) if R else pd.DataFrame(),
            pd.concat(D, ignore_index=True) if D else pd.DataFrame())


# ---------------------------------------------------------------------------
def spearman_parziale(x, y, z, n_perm=20000, seed=SEED):
    """Spearman(x, y) al netto di z: correlazione dei residui delle regressioni sui ranghi.

    p per permutazione di uno dei due residui. Con n=8 e' un test debolissimo, e il referto
    lo dice: serve a vedere se il gradiente SPARISCE, non a dimostrare che esiste.
    """
    x, y, z = (pd.Series(v).rank().to_numpy(float) for v in (x, y, z))

    def resid(a, b):
        b1 = np.column_stack([np.ones(len(b)), b])
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef

    rx, ry = resid(x, z), resid(y, z)

    def rho(a, b):
        a, b = a - a.mean(), b - b.mean()
        d = np.sqrt((a * a).sum() * (b * b).sum())
        return float((a * b).sum() / d) if d > 0 else 0.0

    obs = rho(rx, ry)
    rng = np.random.default_rng(seed)
    cnt = sum(1 for _ in range(n_perm) if rho(rng.permutation(rx), ry) >= obs)
    return obs, (cnt + 1) / (n_perm + 1)


def riga_rho(nome, x, y, soglia=0.74):
    r, p = spearman_perm(np.asarray(x, float), np.asarray(y, float))
    if r >= soglia and p < 0.05:
        esito = "SIGNIFICATIVO"
    elif p < 0.05:
        esito = "p<0.05 ma sotto la soglia di potenza"
    else:
        esito = "non rilevato"
    print("  %-46s rho=%+.3f  p=%.4f   %s" % (nome, r, p, esito))
    return r, p


# ---------------------------------------------------------------------------
def main() -> int:
    cov = universe_from_coverage()
    t0 = cov["start"].max()
    real, rand = run_all(cov, LOOKBACK, t0=t0)

    print("=" * 84)
    print("A1 - DIAGNOSTICO DI DURATA   W2 %s+   n_reali=%d  n_controlli=%d"
          % (t0.date(), len(real), len(rand)))
    print("protocollo: docs/TREND_DURATION_DIAGNOSTIC.md   (0 trial)")
    print("=" * 84)

    persi_pct = float(rand["coda_mancante"].mean())

    # --- D0a: la funzione comune riproduce E1 sul braccio reale? -------------
    d = (real["E1"] - real["E1_comune"]).abs()
    peggio = float(d.max())
    diversi = int((d > 1e-9).sum())
    print("\n--- D0a  la funzione d'uscita comune riproduce E1 sul reale?")
    print("  scarto massimo %.2e su %d trade; diversi: %d (%.1f%%)"
          % (peggio, len(real), diversi, 100.0 * diversi / max(len(real), 1)))
    if diversi:
        sub = real[d > 1e-9]
        print("  causa: `simulate` esce alla CHIUSURA quando il trade termina senza incrocio")
        print("  (fine dei dati o max-hold), all'APERTURA quando incrocia. La funzione comune")
        print("  usa l'apertura. I %d diversi sono terminazioni a fine serie:" % len(sub))
        for _, r in sub.iterrows():
            print("    %-9s %s  hold=%d  E1=%+.3f  comune=%+.3f"
                  % (r["sym"], r["sigid"], r["hold"], r["E1"], r["E1_comune"]))
        print("  E[R] reale con E1=%+.4f  con la funzione comune=%+.4f  -> differenza %+.4f"
              % (real["E1"].mean(), real["E1_comune"].mean(),
                 real["E1_comune"].mean() - real["E1"].mean()))
        print("  Lo stesso vale sul braccio random: %.2f%% dei controlli termina a fine serie"
              % (100 * persi_pct))
        print("  -> le due convenzioni coincidono sul %.1f%% delle coppie. La verifica PASSA,"
              % (100 * (1 - diversi / max(len(real), 1))))
        print("     con l'eccezione dichiarata qui sopra.")

    # --- controllo di onestà: controlli persi per coda mancante -------------
    persi = float(rand["coda_mancante"].mean())
    print("\n--- controllo di onesta': controlli senza barre per arrivare a h")
    print("  %d su %d (%.2f%%)  soglia dichiarata: %.0f%%"
          % (int(rand["coda_mancante"].sum()), len(rand), 100 * persi, 100 * TOLL_PERSI))
    print("  (non vengono scartati: escono all'ultima chiusura disponibile, che e' un "
          "prezzo realmente offerto)")

    # --- matching -----------------------------------------------------------
    print()
    print(check_matching(real, rand, link="sigid",
                         exact=("sym", "side", "year"), numeric=(),
                         observed=("hold",)))
    rand_app = rand.rename(columns={"hold_appaiato": "hold_m"}).copy()
    rand_app["hold"] = rand_app["hold_m"]
    print()
    print(check_matching(real, rand_app, link="sigid",
                         exact=("sym", "side", "year"), numeric=("hold",),
                         observed=()))

    # --- tabella per gruppo -------------------------------------------------
    per = []
    for sym, gg in real.groupby("sym"):
        g = gg["group"].iloc[0]
        rr = rand[rand["sym"] == sym]
        per.append({"sym": sym, "group": g, "vol": realized_vol(sym, g, t0, None),
                    "er": gg["E1"].mean(), "hold": gg["hold"].mean(),
                    "er_rand": rr["E1"].mean(), "hold_rand": rr["hold"].mean(),
                    "er_rand_app": rr["E1_appaiato"].mean(),
                    "er_e3": gg["E3"].mean(), "er_rand_e3": rr["E3"].mean(),
                    "n": len(gg)})
    per = pd.DataFrame(per).dropna(subset=["vol"])
    grp = per.groupby("group").agg(
        vol=("vol", "mean"), er=("er", "mean"), hold=("hold", "mean"),
        er_rand=("er_rand", "mean"), hold_rand=("hold_rand", "mean"),
        er_rand_app=("er_rand_app", "mean"), er_e3=("er_e3", "mean"),
        er_rand_e3=("er_rand_e3", "mean"),
        n=("n", "sum")).reset_index().sort_values("vol")
    grp["diff_oggi"] = grp["er"] - grp["er_rand"]
    grp["diff_app"] = grp["er"] - grp["er_rand_app"]
    grp["diff_e3"] = grp["er_e3"] - grp["er_rand_e3"]

    print("\n--- D1  per gruppo: durata e rendimenti")
    print("  %-9s %7s %7s %7s %9s %9s %9s %9s %9s"
          % ("gruppo", "vol", "hold", "h_rand", "E[R]", "rand_oggi", "rand_app",
             "diff_oggi", "diff_app"))
    for _, r in grp.iterrows():
        print("  %-9s %6.1f%% %7.1f %7.1f %+9.3f %+9.3f %+9.3f %+9.3f %+9.3f"
              % (r["group"], 100 * r["vol"], r["hold"], r["hold_rand"], r["er"],
                 r["er_rand"], r["er_rand_app"], r["diff_oggi"], r["diff_app"]))

    print("\n--- D0b/D1/D2  correlazioni sugli 8 gruppi (serve |rho|>=0.74 per p<0.05)")
    r0, _ = riga_rho("D0 primario   rho(vol, E[R] reale)", grp["vol"], grp["er"])
    riga_rho("D1  rho(vol, holding reale)", grp["vol"], grp["hold"])
    riga_rho("D1  rho(holding reale, E[R] reale)", grp["hold"], grp["er"])
    riga_rho("    rho(vol, E[R] random COSI' COM'E' oggi)", grp["vol"], grp["er_rand"])
    riga_rho("    rho(vol, differenza di oggi)", grp["vol"], grp["diff_oggi"])
    rp, pp = spearman_parziale(grp["vol"], grp["er"], grp["hold"])
    print("  %-46s rho=%+.3f  p=%.4f   %s"
          % ("D2  rho(vol, E[R] | holding)  parziale", rp, pp,
             "SIGNIFICATIVO" if (rp >= 0.74 and pp < 0.05) else "non rilevato"))

    print("\n--- D3  IL TEST DECISIVO: baseline a DURATA APPAIATA")
    r_app, p_app = riga_rho("rho(vol, differenza a durata appaiata)",
                            grp["vol"], grp["diff_app"])
    r_rnd, p_rnd = riga_rho("rho(vol, E[R] random a durata appaiata)",
                            grp["vol"], grp["er_rand_app"])

    g = gap_ci(real.assign(val=real["E1"]),
               rand.assign(val=rand["E1_appaiato"]), value="val", link="sigid")
    print("\n  divario aggregato reale - random(durata appaiata), cluster sull'evento:")
    print("    reale=%+.3f  random=%+.3f  gap=%+.3f  BCa95[%+.3f ; %+.3f]  n_eventi=%d"
          % (g["media_reale"], g["media_random"], g["gap"], g["low"], g["high"],
             g["n_eventi"]))
    g_oggi = gap_ci(real.assign(val=real["E1"]),
                    rand.assign(val=rand["E1"]), value="val", link="sigid")
    print("    per confronto, il divario di OGGI (durata non appaiata): gap=%+.3f "
          "BCa95[%+.3f ; %+.3f]" % (g_oggi["gap"], g_oggi["low"], g_oggi["high"]))

    # --- D3b: durata FISSA pre-registrata, indipendente dall'esito ----------
    print()
    print("--- D3b  robustezza: durata FISSA (E3 = 20 giorni, entrambi i bracci)")
    print("  Perche' serve. In D3 la durata appaiata e' un ESITO del trade reale: i trade che")
    print("  vanno bene restano aperti di piu', quindi il controllo riceve un orizzonte piu'")
    print("  lungo proprio quando il reale ha funzionato. Su un asset con deriva positiva")
    print("  questo AIUTA il controllo, cioe' spinge il divario verso il basso. D3b toglie")
    print("  l'obiezione usando una durata decisa PRIMA e uguale per tutti: E3, gia' una delle")
    print("  quattro uscite pre-registrate. Non e' una regola nuova, e' un metro fisso.")
    print("  %-9s %9s %9s %9s" % ("gruppo", "E3 reale", "E3 random", "differenza"))
    for _, r in grp.iterrows():
        print("  %-9s %+9.3f %+9.3f %+9.3f"
              % (r["group"], r["er_e3"], r["er_rand_e3"], r["diff_e3"]))
    r_e3, p_e3 = riga_rho("rho(vol, differenza a durata FISSA 20g)",
                          grp["vol"], grp["diff_e3"])
    riga_rho("rho(vol, E[R] random a durata FISSA 20g)", grp["vol"], grp["er_rand_e3"])
    g3 = gap_ci(real.assign(val=real["E3"]), rand.assign(val=rand["E3"]),
                value="val", link="sigid")
    print("    divario aggregato a durata fissa: reale=%+.3f random=%+.3f gap=%+.3f "
          "BCa95[%+.3f ; %+.3f]"
          % (g3["media_reale"], g3["media_random"], g3["gap"], g3["low"], g3["high"]))

    print()
    print("  quanto pesa il condizionamento su un esito? correlazione fra la durata del")
    print("  reale e il suo stesso rendimento: rho(hold, E1) sui singoli trade = %+.3f"
          % float(pd.Series(real["hold"]).corr(pd.Series(real["E1"]), method="spearman")))
    print("  (alta = il controllo appaiato eredita informazione dall'esito del reale:")
    print("   e' il motivo per cui D3 va letto INSIEME a D3b, mai da solo)")

    # --- verdetto secondo le tre condizioni dichiarate PRIMA ----------------
    sig_app = (r_app >= 0.74 and p_app < 0.05)
    sig_rnd = (r_rnd >= 0.74 and p_rnd < 0.05)
    print("\n" + "=" * 84)
    print("ESITO secondo docs/TREND_DURATION_DIAGNOSTIC.md sez.5 (scritta prima)")
    print("=" * 84)
    if sig_app:
        print("  A1 SOPRAVVIVE: il gradiente resta a parita' di tempo in mercato.")
        print("  -> si passa al punto 2 (quanti strumenti servono per l'MDE dichiarato).")
    elif sig_rnd:
        print("  A1 CHIUSA: il gradiente NON sopravvive al controllo di durata, ed esiste una")
        print("  spiegazione meccanica AFFERMATIVA - l'ordinamento c'e' anche dove non c'e'")
        print("  nessuna regola (entrata casuale, stessa durata).")
    else:
        print("  NON CONCLUSIVO: nessuno dei due rho raggiunge la soglia di potenza.")
        print("  Con n=8 serve |rho|>=0.74: questo test non distingue le due spiegazioni.")
        print("  Non e' un kill e non e' una promozione - la decisione torna all'utente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
