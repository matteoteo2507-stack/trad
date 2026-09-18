"""A5 - TSMOM: il test poteva vedere l'effetto che stava cercando?

Perche' esiste
--------------
Il 2026-07-08 il TSMOM canonico e' stato bocciato: Sharpe **+0,21** con
**BCa95 [-0,18 ; +0,59]**, lower bound <= 0 -> NO-GO per regola pre-registrata.
La stessa review dichiara pero' l'aspettativa **a priori** dalla letteratura
(Baltas-Kosowski, SG Trend): **Sharpe 0,3-0,5**.

Quelle due righe insieme sollevano una domanda che nessuno ha posto allora:
**con 23 anni di dati, un Sharpe di 0,3-0,5 era rilevabile?**

Se la risposta e' no, il verdetto non e' *"l'effetto non c'e'"* ma
*"non l'abbiamo misurato"* -- e sono due cose diverse, con conseguenze diverse
su cosa si puo' dire e su cosa si puo' riaprire.
E' la stessa forma del difetto che il 2026-09-17 ha smontato il "secondo test"
del FADE: una giustificazione plausibile, mai tradotta in un numero.

Come si calcola
---------------
Errore standard dello Sharpe annualizzato su T anni, rendimenti i.i.d.:

    SE(SR) ~ sqrt( (1 + SR^2 / 2) / T )

Effetto minimo rilevabile (alpha 0,05 bilaterale, potenza 80%): **MDE = 2,80 * SE**.
Anni necessari per rilevare un dato SR: **T = (2,80 / SR)^2 * (1 + SR^2/2)**.

L'approssimazione i.i.d. e' **generosa**: con autocorrelazione positiva (che il
trend-following ha per costruzione) l'errore standard vero e' piu' grande e gli
anni necessari aumentano. Quindi i numeri qui sotto sono un **limite inferiore**.

    python analysis/ops/a5_potenza_tsmom.py
"""
from __future__ import annotations

import numpy as np

K = 2.80          # alpha 0,05 bilaterale, potenza 80%
SR_OSS = 0.21     # Sharpe osservato, primario (252, mensile), dopo costi
T_ANNI = 23       # 2003-2026
CI_RIPORTATO = (-0.18, 0.59)


def se_sharpe(sr, t):
    return float(np.sqrt((1.0 + sr * sr / 2.0) / t))


def anni_per(sr):
    return float((K / sr) ** 2 * (1.0 + sr * sr / 2.0))


def main() -> int:
    se = se_sharpe(SR_OSS, T_ANNI)
    mde = K * se
    lo, hi = SR_OSS - 1.96 * se, SR_OSS + 1.96 * se

    print("A5 - POTENZA del test TSMOM (2026-07-08)")
    print("=" * 72)
    print("Osservato: Sharpe %+.2f su %d anni, BCa95 riportato [%+.2f ; %+.2f]"
          % (SR_OSS, T_ANNI, *CI_RIPORTATO))
    print("Controllo analitico: SE = %.3f -> CI95 [%+.2f ; %+.2f]  (coerente)"
          % (se, lo, hi))
    print()
    print("EFFETTO MINIMO RILEVABILE con %d anni: **Sharpe %.2f**" % (T_ANNI, mde))
    print()
    print("Quanto sarebbe servito per vedere l'effetto ATTESO A PRIORI:")
    print("  %-22s %10s   %s" % ("Sharpe cercato", "anni", "avevamo 23 anni?"))
    for sr in (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        t = anni_per(sr)
        print("  %-22.2f %10.0f   %s"
              % (sr, t, "SI" if t <= T_ANNI else "NO  (servivano %.0fx)" % (t / T_ANNI)))
    print()
    print("LETTURA")
    print("-" * 72)
    print("La letteratura citata dalla review stessa attende Sharpe 0,3-0,5.")
    print("Per rilevare 0,4 servono %.0f anni: ne avevamo %d, cioe' **%.1fx meno**."
          % (anni_per(0.4), T_ANNI, anni_per(0.4) / T_ANNI))
    print("L'intervallo osservato arriva a %+.2f: comprende per intero la fascia"
          % CI_RIPORTATO[1])
    print("attesa dalla letteratura. Il test **non ha escluso** l'effetto cercato:")
    print("ha fallito nel dimostrarlo, che non e' la stessa cosa.")
    print()
    print("Nota: l'approssimazione i.i.d. e' generosa. Con autocorrelazione positiva")
    print("gli anni necessari crescono ancora.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
