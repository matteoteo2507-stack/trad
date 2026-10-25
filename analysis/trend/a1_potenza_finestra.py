"""A1 punto 3: la potenza dipende dalla finestra? Conto sui futures GRATIS prima di comprare.

NON e' un test dell'ipotesi e non consuma trial (come `power_two_groups.py`, referto
docs/TREND_A1_HELDOUT_POWER.md). Usa solo:
  - i trade del campione di SCOPERTA (gia' usati il 21/09) per scomporre la dispersione fra
    strumenti in due parti: la differenza vera fra strumenti (sigma2_b) e il rumore dovuto ai
    pochi trade per strumento (sigma2_w / m);
  - i PREZZI dei futures pysystemtrade non in-sample (gia' scaricati il 03/10), per contare quanti
    strumenti indipendenti ci sono in ciascuna finestra. Nessuna regola gira sugli strumenti nuovi.

La domanda (Matteo, 25/10): i futures gratuiti finiscono il 2024-03-28. Una finestra piu' corta
da' meno trade per strumento, quindi piu' rumore; una finestra piu' lunga all'indietro ne da' di
piu'. Quanti strumenti servono in ciascun caso, e quanti ce ne sono?

Ipotesi del conto (dichiarate, vanno lette con il risultato):
  1. l'effetto (DELTA) e le due componenti di varianza misurati sul campione di scoperta valgono
     anche su strumenti e anni diversi;
  2. i trade per strumento crescono in proporzione agli anni (tasso misurato sul campione);
  3. per i futures conta solo il prezzo: il rendimento giornaliero e' un proxy della correlazione
     della metrica, come nel referto §4.

    python analysis/trend/a1_potenza_finestra.py
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
from power_two_groups import FATT, SOGLIA_VOL, n_per_braccio  # noqa: E402
from heldout_pool_mt5 import DIR_PST, FUTURES, n_eff  # noqa: E402

FINE_GRATIS = pd.Timestamp("2024-03-28")      # ultima riga dei CSV pysystemtrade (verificata il 25/10)
FINESTRE = (                                   # (etichetta, inizio, fine)
    ("A  scoperta / Pinnacle a oggi", None, None),
    ("B  gratis, stessa partenza", pd.Timestamp("2017-12-26"), FINE_GRATIS),
    ("C  gratis dal 2010", pd.Timestamp("2010-01-04"), FINE_GRATIS),
    ("D  gratis dal 2000", pd.Timestamp("2000-01-03"), FINE_GRATIS),
    ("E  gratis dal 1990", pd.Timestamp("1990-01-02"), FINE_GRATIS),
)
TOLLERANZA_INIZIO = pd.Timedelta(days=70)      # storia "piena": parte entro ~2 mesi dall'inizio


def componenti(per_trade: pd.DataFrame, col: str, braccio: pd.Series):
    """sigma2_b (fra strumenti, dentro il braccio) e sigma2_w (dentro lo strumento), ANOVA a una via
    calcolata separatamente nei due bracci e poi mediata: cosi' la differenza fra bracci (DELTA)
    non gonfia la varianza fra strumenti."""
    out = []
    for b in (False, True):
        df = per_trade[per_trade["sym"].map(braccio) == b][["sym", col]].dropna()
        k, n = df["sym"].nunique(), len(df)
        medie = df.groupby("sym")[col].mean()
        conte = df.groupby("sym")[col].size()
        msb = float((conte * (medie - df[col].mean()) ** 2).sum() / (k - 1))
        msw = float(df.groupby("sym")[col].apply(lambda v: ((v - v.mean()) ** 2).sum()).sum()
                    / (n - k))
        m0 = (n - (conte ** 2).sum() / n) / (k - 1)
        out.append((max((msb - msw) / m0, 0.0), msw, conte))
    s2b = float(np.mean([o[0] for o in out]))
    s2w = float(np.mean([o[1] for o in out]))
    conte = pd.concat([o[2] for o in out])
    return s2b, s2w, conte


def inventario_futures(inizio: pd.Timestamp, fine: pd.Timestamp):
    """Strumenti con storia piena nella finestra, per braccio, e quanti ne valgono (n_eff)."""
    rend, righe = {}, []
    for classe, nomi in FUTURES.items():
        for nome in nomi:
            pa = os.path.join(DIR_PST, nome + "__adjusted.csv")
            pm = os.path.join(DIR_PST, nome + "__multiple.csv")
            if not (os.path.exists(pa) and os.path.exists(pm)):
                continue
            a = pd.read_csv(pa, parse_dates=["DATETIME"]).set_index("DATETIME")["price"]
            m = pd.read_csv(pm, parse_dates=["DATETIME"]).set_index("DATETIME")["PRICE"]
            a = a.groupby(a.index.normalize()).last()
            m = m.groupby(m.index.normalize()).last().reindex(a.index).ffill()
            if a.index.min() > inizio + TOLLERANZA_INIZIO:
                continue
            r = (a.diff() / m.shift(1)).replace([np.inf, -np.inf], np.nan)
            r = r[(r.index >= inizio) & (r.index <= fine)].dropna()
            if len(r) < 500:
                continue
            vol = float(r.std(ddof=1) * np.sqrt(252))
            righe.append((nome, classe, vol))
            rend[nome] = r
    T = pd.DataFrame(righe, columns=["sym", "classe", "vol"])
    esito = {}
    for eti, sel in (("ALTA", T["vol"] >= SOGLIA_VOL), ("BASSA", T["vol"] < SOGLIA_VOL)):
        g = T[sel]
        if len(g) == 0:
            esito[eti] = (0, np.nan, 0.0, 0.0)
            continue
        if len(g) == 1:
            esito[eti] = (1, np.nan, 1.0, 1.0)
            continue
        R = pd.DataFrame({s: rend[s] for s in g["sym"]})
        cc = R.corr(min_periods=250).to_numpy()
        rho = float(np.nanmean(cc[np.triu_indices(len(g), 1)]))
        somma = 0.0
        for _, gc in g.groupby("classe"):
            if len(gc) == 1:
                somma += 1.0
                continue
            Rc = pd.DataFrame({s: rend[s] for s in gc["sym"]})
            c2 = Rc.corr(min_periods=250).to_numpy()
            somma += n_eff(len(gc), float(np.nanmean(c2[np.triu_indices(len(gc), 1)])))
        esito[eti] = (len(g), rho, n_eff(len(g), rho), somma)
    return esito


def main() -> int:
    cov = universe_from_coverage()
    t0 = cov["start"].max()
    real, rand = run_all(cov, LOOKBACK, t0=t0)

    m_app = rand.groupby("sigid")["E1_appaiato"].mean()
    m_e3 = rand.groupby("sigid")["E3"].mean()
    real = real.copy()
    real["y_app"] = real["E1"].to_numpy() - real["sigid"].map(m_app).to_numpy()
    real["y_e3"] = real["E3"].to_numpy() - real["sigid"].map(m_e3).to_numpy()

    vol = {s: realized_vol(s, gg["group"].iloc[0], t0, None) for s, gg in real.groupby("sym")}
    real = real[real["sym"].map(vol).notna()]
    braccio = pd.Series({s: v >= SOGLIA_VOL for s, v in vol.items() if v is not None and np.isfinite(v)})
    anni = (real["year"].max() - real["year"].min()) + 1
    tasso = len(real) / (real["sym"].nunique() * anni)     # trade per strumento-anno

    print("=" * 96)
    print("A1 punto 3 - POTENZA PER FINESTRA (0 trial: varianza dal campione di scoperta, prezzi dei futures)")
    print("campione di scoperta dal %s: %d strumenti, %d trade, %d anni -> %.1f trade per strumento-anno"
          % (str(t0)[:10], real["sym"].nunique(), len(real), anni, tasso))
    print("alpha 0,05 bilaterale, potenza 80%%, fattore %.3f" % FATT)
    print("=" * 96)

    metriche = {}
    for eti, col in (("durata appaiata", "y_app"), ("durata fissa 20g", "y_e3")):
        per = real.groupby("sym")[col].mean()
        lo, hi = per[~per.index.map(braccio)], per[per.index.map(braccio)]
        delta = hi.mean() - lo.mean()
        sd_oss = np.sqrt((lo.var(ddof=1) + hi.var(ddof=1)) / 2.0)
        s2b, s2w, conte = componenti(real, col, braccio)
        sd_mod = np.sqrt(s2b + s2w * float(np.mean(1.0 / conte)))
        metriche[eti] = (delta, s2b, s2w)
        print("\n%s: DELTA %+.3f R | sd fra strumenti osservata %.3f, ricostruita dal modello %.3f"
              % (eti, delta, sd_oss, sd_mod))
        print("  componenti: fra strumenti sigma_b %.3f | dentro lo strumento sigma_w %.3f "
              "(quota fra strumenti %.1f%%)" % (np.sqrt(s2b), np.sqrt(s2w), 100 * s2b / (s2b + s2w)))
        print("  limite con infiniti trade per strumento: servono %.1f strumenti per braccio "
              "(effetto osservato), %.1f (dimezzato)"
              % (n_per_braccio(delta, np.sqrt(s2b)), n_per_braccio(delta / 2, np.sqrt(s2b))))

    print("\n" + "-" * 96)
    print("FABBISOGNO (strumenti per braccio) e DISPONIBILITA' (futures non in-sample, n_eff) per finestra")
    print("-" * 96)
    print("%-30s %5s %5s | %7s %7s %7s %7s | %-24s %-14s"
          % ("finestra", "anni", "trade", "app.oss", "app.1/2", "fis.oss", "fis.1/2",
             "ALTA: n / rho / n_eff (somma)", "BASSA: n_eff"))
    for eti, inizio, fine in FINESTRE:
        if inizio is None:
            a = float(anni)
        else:
            a = (fine - inizio).days / 365.25
        m = tasso * a
        bis = []
        for _, (delta, s2b, s2w) in metriche.items():
            sd = np.sqrt(s2b + s2w / m)
            bis += [n_per_braccio(delta, sd), n_per_braccio(delta / 2, sd)]
        if inizio is None:
            disp, disp_b = "come il referto §4/§8", ""
        else:
            inv = inventario_futures(inizio, fine)
            n, rho, ne, somma = inv["ALTA"]
            disp = "%d / %s / %.1f (%.1f)" % (n, "-" if not np.isfinite(rho) else "%+.2f" % rho, ne, somma)
            disp_b = "%.1f (%.1f)" % (inv["BASSA"][2], inv["BASSA"][3])
        print("%-30s %5.1f %5.0f | %7.1f %7.1f %7.1f %7.1f | %-24s %-14s"
              % (eti, a, m, *bis, disp, disp_b))
    print("\nLettura: app./fis. = durata appaiata / fissa 20g; oss. = effetto osservato (ottimistico),"
          " 1/2 = dimezzato (pianificazione onesta).")
    print("Disponibilita': solo futures pysystemtrade non in-sample. Nella finestra B si possono aggiungere"
          " le crypto libere (1,4) e le azioni (3,1) del referto §8; prima del 2017 le crypto non esistono.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
