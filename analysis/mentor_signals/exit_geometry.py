"""B7 - Uscita a 1R contro uscita a TP1, confronto APPAIATO sullo stesso segnale.

Perche' esiste
--------------
Il 2026-09-18 avevo scritto che "il mentore e' bravo a chiamare la direzione ma la
geometria TP1/SL che pubblica la spreca", e che l'uscita a 1R avrebbe usato l'edge
invece di sprecarlo. Era un'ipotesi generata dai dati, messa a backlog come B7 con
un costo di 1 trial.

Due cose si sono rivelate sbagliate:

1. **La premessa era un errore di unita'.** Confrontavo il vantaggio appaiato
   (+0,294, una differenza di **win-rate**) con l'E[R] a TP1 (+0,127, un valore
   **in R**). In R il vantaggio sul lato casuale vale +0,597 a TP1 e +0,588 a 1R:
   identico. Nessuna delle due geometrie spreca niente rispetto all'altra.

2. **Il numero esisteva gia'.** La "win-rate simmetrica (+1R prima di -1R)" e'
   la metrica **primaria** della pre-registrazione di agosto -- ed **e'** l'uscita
   a 1R. Bastava convertirla in R invece di progettare un test nuovo.

Esito: TP1 +0,1247, 1R +0,1246, differenza appaiata -0,0001 [-0,0633 ; +0,0596].
Identiche, ma 1R ha +58% di deviazione standard a parita' di rendimento, quindi e'
**peggiore**. B7 chiusa, 0 trial spesi.

Il confronto e' APPAIATO (stesso segnale, stesso ingresso, stesso stop, cambia solo
il bersaglio): due campioni separati avrebbero un intervallo molto piu' largo e non
distinguerebbero una differenza piccola da una assente.

    python analysis/mentor_signals/exit_geometry.py
"""
import os, sys
import numpy as np

ROOT = os.path.abspath(".")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analysis", "mentor_signals"))
from coverage import verifica
from analysis.mentor_signals import backtest as bt
from core import quant_metrics as qm

T, HI, LO, CL, seg = verifica(silenzioso=True)
tp1, uno, mesi = [], [], []
for s in seg:
    r = bt.replay(s, T, HI, LO)
    if r is None or r.get("tp1_pess") is None or r.get("sym_pess") is None:
        continue
    risk = abs(s["entry"] - s["sl"])
    c = bt.COST_USD / risk
    tp1.append(float(r["tp1_pess"]))
    # sym_pess = True se +1R arriva prima di -1R (scenario pessimistico sui tie)
    uno.append((1.0 - c) if r["sym_pess"] else (-1.0 - c))
    mesi.append(str(s["ts"])[:7])

tp1 = np.array(tp1); uno = np.array(uno); d = uno - tp1
print("n = %d\n" % len(tp1))
for et, v in (("uscita a TP1 (attuale)", tp1), ("uscita a 1R", uno),
              ("DIFFERENZA appaiata (1R - TP1)", d)):
    ci = qm.bca_bootstrap_ci(v, np.mean, n_boot=10000, seed=42)
    print("  %-32s %+.4f  BCa95 [%+.4f ; %+.4f]   sd %.3f"
          % (et, v.mean(), ci["low"], ci["high"], v.std(ddof=1)))
print("\n  win-rate a 1R (simmetrica): %.1f%%   pareggio richiesto ~50%%" % (100*(uno>0).mean()))
print("  TP1 hit%%                  : %.1f%%   pareggio richiesto 69,1%%" % (100*(tp1>0).mean()))
print("\n  per mese (differenza 1R - TP1):")
mesi = np.array(mesi)
for m in sorted(set(mesi)):
    v = d[mesi == m]
    if len(v) >= 5:
        print("    %s  %+.3f  (n=%d)" % (m, v.mean(), len(v)))
