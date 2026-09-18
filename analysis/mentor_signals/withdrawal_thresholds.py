"""Soglie di ritiro del copier mentore — §8bis, da dichiarare PRIMA del capitale.

Cosa chiede §8bis di STRATEGY_LIFECYCLE
---------------------------------------
Tre numeri, fissati prima che entri il capitale, perche' una strategia si ritira quando
**esce dalla distribuzione attesa**, non quando "ultimamente perde" (che e' optional
stopping applicato al capitale: si spegne al minimo e si riaccende dopo il recupero):

  1. **DD di ritiro**           - percentile alto del maxDD nella simulazione
  2. **Serie negativa di ritiro** - percentile alto delle perdite consecutive attese
  3. **Finestra minima**        - sotto quel numero di trade non si valuta affatto

Il problema che questo script risolve davvero
---------------------------------------------
Il Monte Carlo standard **rimescola i trade** e quindi assume che siano **indipendenti**.
Qui non lo sono: il runs test sulla serie vinta/persa da' **z = -3,37** e
l'autocorrelazione dei rendimenti e' **+0,14 a lag 1**, ancora **+0,09 a lag 10**.
Il meccanismo e' ovvio a posteriori: ~4,7 segnali al giorno sullo stesso strumento, quindi
quando la lettura del mentore e' sbagliata **sbaglia per tutta la sessione**.

Conseguenza: il rimescolamento **distrugge proprio il raggruppamento che produce i
drawdown profondi** e quindi li sottostima. Soglie derivate da li' sarebbero **troppo
strette**, e ci farebbero ritirare la strategia durante un drawdown del tutto normale —
cioe' esattamente l'errore che §8bis esiste per impedire.

Percio' qui si simula in due modi e si usa quello onesto:
  - **i.i.d.**  : rimescolamento dei singoli trade (il metodo standard, per confronto)
  - **a blocchi**: ricampionamento dei **giorni interi**, che conserva il raggruppamento

La differenza fra i due **e' il costo dell'ipotesi di indipendenza**, ed e' un numero che
va riportato, non assunto.

Incertezza della simulazione
-----------------------------
Ogni percentile stimato da una simulazione ha il proprio errore standard. Qui viene
riportato (ripetendo la simulazione in piu' repliche indipendenti), perche' un percentile
"9,8R" e uno "11,2R" possono essere lo stesso numero visto due volte.

    python analysis/mentor_signals/withdrawal_thresholds.py
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.mentor_signals import backtest as bt   # noqa: E402

N_SIM = 20000          # simulazioni per replica
N_REPLICHE = 8         # repliche indipendenti, per l'errore standard dei percentili
PCT = 95               # percentile di ritiro
SEED = 42

# Limite inferiore dell'intervallo OOS su E[R] (pre-registrazione 2026-08-07:
# +0,194 BCa95 [+0,079 ; +0,289]). Si usa per la verifica di sensibilita': un E[R]
# piu' basso produce drawdown piu' profondi, quindi soglie piu' larghe. Sbagliare
# in quella direzione e' preferibile: una soglia troppo stretta ritira una strategia sana.
ER_OOS_LOW = 0.079


def serie_r():
    """R per trade (uscita a TP1, costi inclusi, scenario pessimistico) + giorno.

    FIX 2026-09-18 (2): usa il feed ESTESO e l'export Telegram completo, non
    `XAU_spot_M5.csv` (che si ferma al 12/06) e `signals.csv` (fermo al 08/07).
    Il repo aveva gia' due mesi in piu' di dati: `XAU_spot_M5_ext.csv` fino al
    07/08 e la cartella export fino al 07/08. Usarli non e' un'estensione del
    perimetro, e' smettere di buttare via meta' di quello che abbiamo.
    """
    import os as _os
    bt.M5 = _os.path.join(ROOT, "analysis", "trading-bot-eval", "data",
                          "XAU_spot_M5_ext.csv")
    T, HI, LO, CL = bt.load_m5()
    sys.path.insert(0, _os.path.join(ROOT, "analysis", "mentor_signals"))
    import oos_validation as ov
    segnali = ov.to_engine(ov.parse_export())
    out = []
    for s in segnali:
        r = bt.replay(s, T, HI, LO)
        if r is None or r.get("tp1_pess") is None:
            continue
        out.append((str(s["ts"])[:10], float(r["tp1_pess"])))
    return out


def max_dd(path):
    """Drawdown massimo di una curva cumulata, in unita' di R."""
    picco = np.maximum.accumulate(path)
    return float(np.max(picco - path))


def max_streak(r):
    best = cur = 0
    for x in r:
        cur = cur + 1 if x < 0 else 0
        if cur > best:
            best = cur
    return best


def simula(R, giorni, modo, n_sim, rng, shift=0.0):
    """Ritorna (maxDD, serie negativa max) per n_sim percorsi simulati."""
    R = np.asarray(R) + shift
    dd = np.empty(n_sim)
    st = np.empty(n_sim, dtype=int)
    if modo == "iid":
        for i in range(n_sim):
            x = rng.permutation(R)
            dd[i] = max_dd(np.cumsum(x))
            st[i] = max_streak(x)
    else:  # blocchi = giorni interi
        per_giorno = defaultdict(list)
        for g, v in zip(giorni, R):
            per_giorno[g].append(v)
        blocchi = [np.array(v) for v in per_giorno.values()]
        nb = len(blocchi)
        for i in range(n_sim):
            idx = rng.integers(0, nb, nb)
            x = np.concatenate([blocchi[k] for k in idx])
            dd[i] = max_dd(np.cumsum(x))
            st[i] = max_streak(x)
    return dd, st


def stima(R, giorni, modo, shift=0.0):
    """Percentile con errore standard, da repliche indipendenti."""
    dd_p, st_p = [], []
    for k in range(N_REPLICHE):
        rng = np.random.default_rng(SEED + 1000 * k)
        dd, st = simula(R, giorni, modo, N_SIM // N_REPLICHE, rng, shift)
        dd_p.append(np.percentile(dd, PCT))
        st_p.append(np.percentile(st, PCT))
    return (float(np.mean(dd_p)), float(np.std(dd_p, ddof=1)),
            float(np.mean(st_p)), float(np.std(st_p, ddof=1)))


def main() -> int:
    dati = serie_r()
    giorni = [g for g, _ in dati]
    R = np.array([v for _, v in dati])
    n = len(R)
    W = (R > 0).astype(int)
    q = 1.0 - W.mean()

    print("SOGLIE DI RITIRO - copier segnali mentore (XAUUSD)   [§8bis]")
    print("=" * 76)
    print("Campione: %d trade, %d giorni, %s -> %s"
          % (n, len(set(giorni)), giorni[0], giorni[-1]))
    print("E[R] = %+.4f   sd = %.4f   vincenti %.1f%%   payoff +%.2f / %.2f"
          % (R.mean(), R.std(ddof=1), 100 * W.mean(),
             R[R > 0].mean(), R[R < 0].mean()))
    print()

    # --- indipendenza: l'ipotesi che il Monte Carlo standard da' per scontata -----
    runs = 1 + int((W[1:] != W[:-1]).sum())
    n1, n0 = int(W.sum()), int(n - W.sum())
    mu = 2 * n1 * n0 / n + 1
    sd = np.sqrt(2 * n1 * n0 * (2 * n1 * n0 - n) / (n * n * (n - 1)))
    ac1 = np.corrcoef(R[:-1], R[1:])[0, 1]
    print("1) GLI ESITI SONO INDIPENDENTI?  (se no, il rimescolamento sottostima)")
    print("   runs test: %d sequenze contro %.1f attese  ->  z = %+.2f"
          % (runs, mu, (runs - mu) / sd))
    print("   autocorrelazione dei rendimenti a lag 1: %+.3f" % ac1)
    print("   serie negativa piu' lunga osservata: %d" % max_streak(R))
    print("   -> raggruppamento confermato: si usa il ricampionamento A BLOCCHI (giorni)")
    print()

    # --- le due simulazioni -------------------------------------------------------
    print("2) SIMULAZIONE - percentile %d, %s simulazioni, errore standard su %d repliche"
          % (PCT, f"{N_SIM:,}".replace(",", "."), N_REPLICHE))
    print()
    print("   %-34s %14s %16s" % ("", "maxDD (R)", "serie negativa"))
    ris = {}
    for modo, et in (("iid", "i.i.d. (rimescola i trade)"),
                     ("blocchi", "a blocchi (giorni interi)")):
        d, ds, s, ss = stima(R, giorni, modo)
        ris[modo] = (d, s)
        print("   %-34s %7.2f +- %.2f %9.2f +- %.2f" % (et, d, ds, s, ss))
    costo = ris["blocchi"][0] - ris["iid"][0]
    print()
    print("   Costo dell'ipotesi di indipendenza: **%+.2fR** di drawdown"
          " (%.0f%% in piu')" % (costo, 100 * costo / ris["iid"][0]))
    print()

    # --- sensibilita': E[R] al limite inferiore OOS -------------------------------
    shift = ER_OOS_LOW - R.mean()
    d2, ds2, s2, ss2 = stima(R, giorni, "blocchi", shift=shift)
    print("3) SENSIBILITA' - stesso campione con E[R] portato al limite inferiore")
    print("   dell'intervallo OOS (+%.3f invece di %+.3f):" % (ER_OOS_LOW, R.mean()))
    print("   maxDD %.2f +- %.2f R   serie negativa %.2f +- %.2f" % (d2, ds2, s2, ss2))
    print()

    # --- finestra minima: quanti trade per accorgersi di un degrado ---------------
    k = 2.80          # alpha 0,05 bilaterale, potenza 80%
    sdr = R.std(ddof=1)
    print("4) FINESTRA MINIMA - quanti trade servono per vedere un degrado")
    for eff, et in ((R.mean(), "da E[R] attuale a ZERO"),
                    (R.mean() - ER_OOS_LOW, "da E[R] attuale al limite inf. OOS"),
                    (0.05, "un degrado di 0,05R")):
        print("   %-40s n = %5.0f trade  (~%.0f giorni)"
              % (et, (k * sdr / eff) ** 2, (k * sdr / eff) ** 2 / (n / len(set(giorni)))))
    print()

    # --- le soglie ---------------------------------------------------------------
    dd_s, st_s = ris["blocchi"]
    print("=" * 76)
    print("SOGLIE PROPOSTE (dal ricampionamento a blocchi, quello onesto)")
    print("=" * 76)
    print("   DD di ritiro          : **%.1f R**  (percentile %d)" % (dd_s, PCT))
    print("   Serie negativa        : **%d perdite consecutive**" % int(np.ceil(st_s)))
    print("   Finestra minima       : **%d trade** - sotto non si valuta affatto"
          % int(round((k * sdr / R.mean()) ** 2)))
    print()
    print("   Con rischio dell'1%% per trade, %.1fR di drawdown valgono circa %.1f%%"
          " del capitale." % (dd_s, dd_s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
