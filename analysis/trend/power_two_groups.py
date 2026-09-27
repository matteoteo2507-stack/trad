"""A1 punto 2: quanti strumenti servono per il confronto a due gruppi, e Dukascopy li ha?

NON e' un test dell'ipotesi. E' un calcolo di **potenza** fatto PRIMA di raccogliere, come
impone la regola nata dal FADE (il "secondo test" era fuori scala di 40x). Non consuma trial:
non cambia regole ne' parametri, e non produce un verdetto su A1.

La domanda. Il diagnostico di durata (docs/TREND_DURATION_DIAGNOSTIC.md) ha lasciato in piedi
il gradiente sulla DIFFERENZA contro random a durata controllata. Il passo successivo sarebbe
un confronto a **due gruppi** (alta vs bassa volatilita') su strumenti **mai visti**. Quanti
strumenti servono perche' quel test possa vincere, e quelli che servono esistono?

L'unita' di inferenza e' lo STRUMENTO, non il trade. E' lo strumento che viene tenuto fuori, e
i trade dentro uno strumento non sono indipendenti: condividono la serie. Riportare il numero
per-trade e' comodo e ottimistico, quindi qui compaiono entrambi e il confronto fra i due E' il
risultato.

    python analysis/trend/power_two_groups.py
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

from backtest import LOOKBACK, realized_vol, universe_from_coverage  # noqa: E402
from duration_diagnostic import run_all  # noqa: E402

Z_A = 1.959963985          # alpha 0,05 bilaterale
Z_B = 0.8416212336         # potenza 80%
FATT = (Z_A + Z_B) ** 2    # 7,849 -> la radice e' il 2,80 del promemoria
SOGLIA_VOL = 0.20          # split dichiarato: 20% di volatilita' annualizzata

# Cio' che la libreria dukascopy_python espone, per categoria non-azionaria, e cosa usiamo gia'.
POOL = {
    "fx_major":  (7, ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"]),
    "fx_cross":  (61, ["EURJPY", "GBPJPY", "EURGBP"]),
    "bond":      (3, ["BUND", "UKGILT", "USTBOND"]),
    "index":     (22, ["NAS100", "SPX500"]),          # AMERICA 7 + EUROPE 9 + ASIA 6
    "metal":     (5, ["XAUUSD", "XAGUSD", "COPPER", "XPT", "XPD"]),   # FX_METALS 2 + CMD_METALS 3
    "energy":    (4, ["BRENT", "WTI", "NATGAS"]),
    "agri":      (6, ["COCOA", "COFFEE", "COTTON", "SOYBEAN", "SUGAR"]),
    "crypto":    (21, ["BTCUSD", "ETHUSD"]),          # coppie *_USD distinte
}


def n_per_braccio(delta, sd, fattore=FATT):
    """Osservazioni per braccio per rilevare `delta` con alpha 0,05 e potenza 80%."""
    if not np.isfinite(delta) or delta == 0 or not np.isfinite(sd):
        return float("inf")
    return 2.0 * fattore * (sd / abs(delta)) ** 2


def icc_e_deff(y, gruppi):
    """ICC a una via e design effect. Con cluster grandi anche un ICC minuscolo pesa."""
    df = pd.DataFrame({"y": y, "g": gruppi}).dropna()
    k = df["g"].nunique()
    if k < 2:
        return float("nan"), float("nan"), float("nan")
    n = len(df)
    m = n / k
    medie = df.groupby("g")["y"].mean()
    conte = df.groupby("g")["y"].size()
    msb = float(((conte * (medie - df["y"].mean()) ** 2).sum()) / (k - 1))
    msw = float(df.groupby("g")["y"].apply(lambda v: ((v - v.mean()) ** 2).sum()).sum()
                / max(n - k, 1))
    m0 = (n - (conte ** 2).sum() / n) / (k - 1)
    icc = (msb - msw) / (msb + (m0 - 1) * msw) if (msb + (m0 - 1) * msw) > 0 else 0.0
    icc = max(icc, 0.0)
    return icc, 1.0 + (m - 1) * icc, m


def tabella(nome, per, col, anni):
    """Il conto, per una delle due convenzioni di durata."""
    lo = per[per["vol"] < SOGLIA_VOL]
    hi = per[per["vol"] >= SOGLIA_VOL]
    d_lo, d_hi = lo[col].mean(), hi[col].mean()
    delta = d_hi - d_lo
    sd_cl = np.sqrt((lo[col].var(ddof=1) + hi[col].var(ddof=1)) / 2.0)

    print("\n%s" % nome)
    print("  braccio BASSA vol (<%.0f%%): %d strumenti, media per-strumento %+.3f  sd %.3f"
          % (100 * SOGLIA_VOL, len(lo), d_lo, lo[col].std(ddof=1)))
    print("  braccio ALTA  vol (>=%.0f%%): %d strumenti, media per-strumento %+.3f  sd %.3f"
          % (100 * SOGLIA_VOL, len(hi), d_hi, hi[col].std(ddof=1)))
    print("  DELTA osservato = %+.3f R   sd fra strumenti (pooled) = %.3f" % (delta, sd_cl))

    print("  %-34s %10s %10s %10s" % ("effetto ipotizzato", "per braccio", "totale", "anni-str."))
    for eti, d in (("osservato (ottimistico)", delta),
                   ("dimezzato (winner's curse)", delta / 2.0),
                   ("un terzo", delta / 3.0)):
        n_str = n_per_braccio(d, sd_cl)
        tot = 2 * n_str
        print("  %-34s %10.1f %10.1f %10.0f"
              % ("%s  %+.3f R" % (eti, d), n_str, tot, tot * anni))
    return delta, sd_cl, lo, hi


def main() -> int:
    cov = universe_from_coverage()
    t0 = cov["start"].max()
    real, rand = run_all(cov, LOOKBACK, t0=t0)
    anni = (real["year"].max() - real["year"].min()) + 1

    # --- differenza appaiata per trade, nelle due convenzioni di durata ---
    m_app = rand.groupby("sigid")["E1_appaiato"].mean()
    m_e3 = rand.groupby("sigid")["E3"].mean()
    real = real.copy()
    real["y_app"] = real["E1"].to_numpy() - real["sigid"].map(m_app).to_numpy()
    real["y_e3"] = real["E3"].to_numpy() - real["sigid"].map(m_e3).to_numpy()

    per = []
    for sym, gg in real.groupby("sym"):
        g = gg["group"].iloc[0]
        per.append({"sym": sym, "group": g, "vol": realized_vol(sym, g, t0, None),
                    "y_app": gg["y_app"].mean(), "y_e3": gg["y_e3"].mean(),
                    "n": len(gg)})
    per = pd.DataFrame(per).dropna(subset=["vol"]).sort_values("vol")

    print("=" * 86)
    print("A1 PUNTO 2 - POTENZA del confronto a due gruppi su strumenti held-out")
    print("finestra di riferimento %s+  |  %d strumenti  |  %d trade  |  %d anni"
          % (t0.date(), len(per), len(real), anni))
    print("alpha 0,05 bilaterale, potenza 80 pct -> fattore (z+z)^2 = %.3f" % FATT)
    print("=" * 86)

    print("\n--- gli strumenti di oggi, e il loro contributo")
    print("  %-9s %-9s %7s %6s %9s %9s" % ("strumento", "gruppo", "vol", "trade",
                                           "y appaiata", "y fissa20"))
    for _, r in per.iterrows():
        print("  %-9s %-9s %6.1f%% %6d %+9.3f %+9.3f"
              % (r["sym"], r["group"], 100 * r["vol"], r["n"], r["y_app"], r["y_e3"]))

    tr_str = per["n"].sum() / len(per)
    print("\n  trade per strumento: %.0f in %d anni  ->  %.1f per strumento-anno"
          % (tr_str, anni, tr_str / anni))

    # --- clustering: quanto e' ottimistico contare i trade ---
    print("\n--- perche' NON si contano i trade")
    for eti, col in (("durata appaiata", "y_app"), ("durata fissa 20g", "y_e3")):
        icc, deff, m = icc_e_deff(real[col], real["sym"])
        print("  %-18s ICC fra strumenti = %.4f   cluster medio %.0f trade   "
              "design effect = %.2f" % (eti, icc, m, deff))
    deff_e3 = icc_e_deff(real["y_e3"], real["sym"])[1]
    print("  Un design effect di %.2f significa che i %d trade raccolti valgono quanto"
          % (deff_e3, len(real)))
    print("  %d trade indipendenti. Il conto per-trade piu' sotto e' riportato solo per"
          % int(len(real) / max(deff_e3, 1)))
    print("  mostrare di quanto inganna.")

    d1, s1, lo1, hi1 = tabella("--- A  metrica = differenza a DURATA APPAIATA",
                               per, "y_app", anni)
    d2, s2, lo2, hi2 = tabella("--- B  metrica = differenza a DURATA FISSA 20g (D3b, "
                               "indipendente dall'esito)", per, "y_e3", anni)

    print("\n--- per confronto, il conto INGANNEVOLE fatto sui trade")
    for eti, col, d in (("appaiata", "y_app", d1), ("fissa20", "y_e3", d2)):
        sd_t = real[col].std(ddof=1)
        print("  %-9s sd per-trade %.3f -> %.0f trade per braccio (ignorando il cluster)"
              % (eti, sd_t, n_per_braccio(d, sd_t)))

    # --- ridondanza: quanti strumenti INDIPENDENTI ci sono davvero in un gruppo ---
    print()
    print("=" * 86)
    print("RIDONDANZA: 19 altcoin non sono 19 strumenti")
    print("=" * 86)
    print("  Il conto di potenza qui sopra assume cluster indipendenti. Se gli strumenti di un")
    print("  braccio sono correlati fra loro, il numero che conta non e' quanti sono ma quanti")
    print("  ne valgono:  n_eff = n / (1 + (n-1) * rho_medio).")
    rend = {}
    for _, r in cov.iterrows():
        from backtest import load as _load
        d = _load(r["sym"], r["group"])
        d = d[d["time"] >= t0]
        if len(d) < 100:
            continue
        s_ = pd.Series(np.log(d["close"].to_numpy(float))).diff()
        s_.index = pd.DatetimeIndex(d["time"])
        rend[r["sym"]] = s_
    R = pd.DataFrame(rend).dropna(how="all")
    print()
    print("  %-9s %5s %9s %10s %12s" % ("gruppo", "n", "rho medio", "n_eff", "n_eff / n"))
    for g, gg in per.groupby("group"):
        syms = [x for x in gg["sym"] if x in R.columns]
        if len(syms) < 2:
            print("  %-9s %5d %9s %10s %12s" % (g, len(syms), "-", "-", "-"))
            continue
        c = R[syms].corr().to_numpy()
        iu = np.triu_indices(len(syms), 1)
        rho = float(np.nanmean(c[iu]))
        n = len(syms)
        neff = n / (1 + (n - 1) * max(rho, 0.0))
        print("  %-9s %5d %9.3f %10.2f %11.0f%%" % (g, n, rho, neff, 100 * neff / n))
    if "BTCUSD" in R.columns and "ETHUSD" in R.columns:
        rbe = float(R[["BTCUSD", "ETHUSD"]].corr().iloc[0, 1])
        for n_alt in (19, 21):
            neff = n_alt / (1 + (n_alt - 1) * rbe)
            print()
            print("  BTC-ETH rho = %.3f  ->  se le %d crypto libere fossero"
                  " correlate cosi'," % (rbe, n_alt))
            print("  varrebbero %.1f strumenti indipendenti, non %d." % (neff, n_alt))
            break

    # --- disponibilita' ---
    print("\n" + "=" * 86)
    print("DISPONIBILITA': cosa resta da pescare in Dukascopy (libreria dukascopy_python)")
    print("=" * 86)
    volg = per.groupby("group")["vol"].mean()
    print("  %-9s %7s %8s %6s %8s %s" % ("gruppo", "vol", "in libr.", "usati", "LIBERI",
                                         "lato"))
    lib_lo = lib_hi = 0
    for g, (tot, usati) in POOL.items():
        v = float(volg.get(g, np.nan))
        liberi = tot - len(usati)
        lato = "bassa" if (np.isfinite(v) and v < SOGLIA_VOL) else "ALTA"
        if lato == "bassa":
            lib_lo += liberi
        else:
            lib_hi += liberi
        print("  %-9s %6.1f%% %8d %6d %8d %s"
              % (g, 100 * v if np.isfinite(v) else float("nan"), tot, len(usati),
                 liberi, lato))
    print("\n  strumenti LIBERI lato bassa volatilita': %d" % lib_lo)
    print("  strumenti LIBERI lato alta  volatilita': %d   di cui crypto: %d"
          % (lib_hi, POOL["crypto"][0] - len(POOL["crypto"][1])))
    print("  -> fuori dalla crypto, il lato ALTA volatilita' ha solo %d strumenti nuovi"
          % (lib_hi - (POOL["crypto"][0] - len(POOL["crypto"][1]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
