"""Doppio binario della gestione del rischio (STRATEGY_LIFECYCLE §4quater, DECISIONS 2026-10-06).

Ogni test di una strategia si legge su due binari, **a prescindere dall'esito**:

1. **rischio fisso 1R**: l'unico su cui si da' il verdetto sul vantaggio;
2. gli **overlay della libreria qui sotto**, fissa e dichiarata una volta per tutto il repo (non per
   strategia). Un overlay aggiunto dopo aver visto un risultato e' un tentativo, e si conta.

Il principio che decide cosa un overlay puo' e non puo' fare:

    guadagno = somma E[size] * E[R]  +  somma Cov(size, R)

Una size decisa solo dal passato (serie di perdite, drawdown) ha covarianza **zero** con un esito
indipendente dal passato. Quindi un overlay **non crea vantaggio**: sposta il rischio nel tempo e cambia il
percorso. Aggiunge valore vero solo in due casi, che le due funzioni sotto misurano separatamente:

- **dipendenza** (capitale proprio): gli esiti sono raggruppati (regimi). Si misura confrontando l'overlay
  sulla sequenza reale con la **stessa sequenza rimescolata**, che azzera la covarianza
  (`confronta_overlay`). E' un'ipotesi sul processo: si conferma solo in forward.
- **struttura** (prop): l'obiettivo e' a barriere (+obiettivo prima di -limite), non lineare. Li' la size
  ottima dipende dallo stato anche con esiti indipendenti, ma lo stesso vale per chi **non ha vantaggio**:
  si confronta col benchmark a vantaggio zero e con l'incertezza di stima (`confronta_overlay_prop`).

Misure del 06/10 su sequenze simulate (illustrazioni, non mercato; scratchpad di sessione, ripetute nei test):
con esiti indipendenti nessun overlay esce dalla banda del rimescolato; con regimi il cuscinetto aggiunge
(+0,175 contro p95 +0,138) e dimezza il maxDD; con esiti alternati la riduzione dopo le perdite toglie
(+0,076 contro p5 +0,098).

Cosa NON e' un overlay: vol targeting, filtri di regime, size per "convinzione". Usano informazione di mercato
ex ante, possono avere covarianza con l'esito, quindi cambiano il segnale: sono filtri (LIFECYCLE §4, trial).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from core.prop_sim import AccountState, RiskModel, evaluate_ci
from core.verifiche import runs_test

# ---- la libreria dichiarata ------------------------------------------------------------------
# Valori identici agli insiemi omonimi di prop-lab/config/risk_profiles.yaml (05/10), ma FISSATI qui:
# se il socio cambia il suo YAML, la libreria di trad non cambia di nascosto (test_sizing lo verifica).
LIBRERIA = {
    "O1_cuscinetto": {
        "modifiers": [{"type": "dd_linear", "min_mult": 0.25}],
        "obiettivi": ("proprio", "prop"),
        "razionale": "rischio proporzionale alla distanza dal limite di perdita (Grossman-Zhou 1993, CPPI; "
                     "da confermare): giustificato da un limite duro anche con esiti indipendenti",
        "quando_danneggia": "costa crescita; con rischio base basso allunga i tempi (timeout in prop)",
    },
    "O2_guardia_giornaliera": {
        "modifiers": [{"type": "daily_guard", "stop_at": 0.5, "max_trades": 3},
                      {"type": "floor_cap", "frac": 0.9}],
        "obiettivi": ("prop",),
        "razionale": "la perdita giornaliera chiude il conto: stop alla giornata a meta' del limite, mai un "
                     "trade che possa sforare",
        "quando_danneggia": "se il vantaggio e' concentrato in pochi trade della giornata, li taglia",
    },
    "O3_serie_perdite": {
        "modifiers": [{"type": "loss_streak", "after": 2, "factor": 0.5, "min_mult": 0.25}],
        "obiettivi": ("proprio", "prop"),
        "razionale": "dimezza dopo 2 perdite di fila: ha senso solo se le perdite arrivano raggruppate",
        "quando_danneggia": "esiti indipendenti (recupero lento) o alternati (distrugge valore)",
    },
    "O4_avvicinamento_target": {
        "modifiers": [{"type": "target_coast", "near": 0.8, "mult": 0.5}],
        "obiettivi": ("prop",),
        "razionale": "vicino all'obiettivo della fase il guadagno marginale vale meno del rischio di bruciarla",
        "quando_danneggia": "inutile senza un obiettivo a barriera",
    },
}

_INF = float("inf")


def profilo(nome: str, base_pct: float) -> dict:
    """Profilo nel formato di `prop-lab` (`RiskModel`): '1R' = rischio fisso, altrimenti un overlay."""
    mods = [] if nome == "1R" else [dict(m) for m in LIBRERIA[nome]["modifiers"]]
    return {"name": f"{nome}|{base_pct}%", "base": {"type": "fixed_pct", "pct": base_pct, "of": "initial"},
            "modifiers": mods}


def _controlla(nomi, obiettivo):
    for n in nomi:
        if n not in LIBRERIA:
            raise KeyError(f"{n} non e' nella libreria dichiarata: aggiungerlo e' un tentativo (LIFECYCLE §4quater)")
        if obiettivo not in LIBRERIA[n]["obiettivi"]:
            raise ValueError(f"{n} non si applica all'obiettivo '{obiettivo}'")


# ---- binario capitale proprio: valore di dipendenza --------------------------------------------

def moltiplicatori(r, nome: str, limite_r: float = 10.0, trailing: bool = True) -> np.ndarray:
    """Size (in R della size base) che l'overlay assegna a ogni trade della sequenza `r`, in ordine.

    Conto lineare in unita' di R: la size base e' 1, il limite di perdita e' `limite_r` R sotto il picco
    (`trailing=True`, come un DD di ritiro) o sotto il capitale iniziale. Il conto non si ferma al limite:
    serve a misurare l'overlay, non a simulare il ritiro.
    """
    r = np.asarray(r, dtype=float)
    if nome == "1R":
        return np.ones(r.size)
    model = RiskModel(profilo(nome, 1.0))
    ini = 100.0
    bal = peak = ini
    ls = ws = 0
    out = np.empty(r.size)
    for t, x in enumerate(r):
        floor = (peak if trailing else ini) - limite_r
        st = AccountState(ini, bal, peak, bal, 0.0, 0, ls, ws, _INF, -_INF, floor, _INF, limite_r)
        m = model.risk_amount(st)
        out[t] = m
        bal += m * x
        peak = max(peak, bal)
        if m > 0:
            ls, ws = (0, ws + 1) if x > 0 else (ls + 1, 0)
    return out


def _metriche(r, m):
    pnl = m * r
    eq = np.concatenate([[0.0], np.cumsum(pnl)])
    dd = float((np.maximum.accumulate(eq) - eq).max())
    tot = float(m.sum())
    return {"e_per_unita": float(pnl.sum() / tot) if tot > 0 else float("nan"),
            "totale_r": float(pnl.sum()), "max_dd_r": dd, "size_media": float(m.mean())}


def _rimescola(r, blocco, rng):
    if blocco <= 1:
        return rng.permutation(r)
    nb = int(math.ceil(r.size / blocco))
    pezzi = [r[i * blocco:(i + 1) * blocco] for i in range(nb)]
    return np.concatenate([pezzi[i] for i in rng.permutation(nb)])


def confronta_overlay(r, overlay=("O1_cuscinetto", "O3_serie_perdite"), limite_r: float = 10.0,
                      trailing: bool = True, n_perm: int = 300, blocco: int = 1, seed: int = 42,
                      conf: float = 0.95):
    """Binario 1R contro gli overlay, sulla sequenza reale e su `n_perm` rimescolamenti della stessa.

    `valore_dipendenza` = attesa per unita' di rischio sulla sequenza reale meno la media sui rimescolati.
    E' fuori dal caso solo se cade fuori dalla banda centrale `conf` dei rimescolati. Con esiti
    indipendenti la sequenza reale e' scambiabile con le sue permutazioni, quindi ogni overlay da' un
    **falso allarme con probabilita' 1 - conf** (verificato il 06/10: 7,0% e 5,5% su 200 sequenze
    indipendenti con conf = 0,95), e con k overlay almeno uno lo da' con ~1 - conf^k. Per questo la
    lettura AGGIUNGE/TOGLIE e' un'ipotesi da confermare in forward, mai un verdetto.
    `percentile_reale` usa il rango medio (i pareggi contano a meta'). `blocco` > 1 rimescola a blocchi
    contigui (conserva la dipendenza corta, misura solo quella lunga).
    Restituisce (tabella, runs_test sugli esiti).
    """
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    _controlla(overlay, "proprio")
    rng = np.random.default_rng(seed)
    perm = [_rimescola(r, blocco, rng) for _ in range(n_perm)]
    righe = []
    for nome in ("1R",) + tuple(overlay):
        reale = _metriche(r, moltiplicatori(r, nome, limite_r, trailing))
        sim = [_metriche(x, moltiplicatori(x, nome, limite_r, trailing)) for x in perm]
        e = np.array([s["e_per_unita"] for s in sim])
        d = np.array([s["max_dd_r"] for s in sim])
        x0 = reale["e_per_unita"]
        sotto, pari = float((e < x0 - 1e-12).sum()), float((np.abs(e - x0) <= 1e-12).sum())
        riga = {"binario": nome, **reale, "e_rimescolato": float(e.mean()),
                "e_lo": float(np.percentile(e, (1 - conf) / 2 * 100)),
                "e_hi": float(np.percentile(e, (1 + conf) / 2 * 100)),
                "valore_dipendenza": x0 - float(e.mean()),
                "percentile_reale": (sotto + 0.5 * pari + 0.5) / (len(e) + 1) * 100,
                "max_dd_mediano_rimescolato": float(np.median(d))}
        if nome == "1R":
            riga["lettura"] = "verdetto sul vantaggio"
        elif x0 > riga["e_hi"]:
            riga["lettura"] = "AGGIUNGE per dipendenza (ipotesi: si conferma in forward)"
        elif x0 < riga["e_lo"]:
            riga["lettura"] = "TOGLIE per dipendenza"
        else:
            riga["lettura"] = "nessun valore di dipendenza"
        righe.append(riga)
    return pd.DataFrame(righe), runs_test(r > 0)


# ---- binario prop: valore di struttura, contro il vantaggio zero --------------------------------

def confronta_overlay_prop(day_trades, rules: dict, base_pct: float,
                           overlay=("O1_cuscinetto", "O2_guardia_giornaliera", "O3_serie_perdite",
                                    "O4_avvicinamento_target"),
                           n_paths: int = 200, n_outer: int = 100, block: int = 5, seed: int = 7,
                           conf: float = 0.90) -> pd.DataFrame:
    """Per 1R e per ogni overlay, allo stesso rischio base: pass rate ed EV con l'incertezza di stima,
    lo stesso calcolo a vantaggio zero e `ev_vs_zero` (la parte di EV dovuta al vantaggio).

    Un overlay e' utile in prop se alza `ev_vs_zero` rispetto a 1R con un intervallo che lo regge, non se
    alza l'EV grezzo: quello sale anche a chi non ha vantaggio. Il rischio base si sceglie fra quelli che
    restano buoni su tutto l'intervallo dell'attesa (la tabella del 06/10: piu' il vantaggio e' scarso, piu'
    l'ottimo si sposta verso il rischio alto, quindi l'ottimo puntuale su un campione premia il rumore).
    `day_trades`: lista per giorno di (R, MAE in R), come `prop_sim.trades_by_day`.
    """
    _controlla(overlay, "prop")
    righe = []
    for nome in ("1R",) + tuple(overlay):
        o = evaluate_ci(day_trades, rules, profilo(nome, base_pct), n_paths=n_paths, block=block,
                        seed=seed, n_outer=n_outer, conf=conf)
        righe.append({"binario": nome, "base_pct": base_pct,
                      "pass_rate": o["pass_rate"], "pass_lo": o["pass_ci"][0], "pass_hi": o["pass_ci"][1],
                      "pass_zero": o["pass_zero"],
                      "ev": o["ev_attempt"], "ev_zero": o["ev_zero"],
                      "ev_vs_zero": o["ev_vs_zero"], "ev_vs_zero_lo": o["ev_vs_zero_ci"][0],
                      "ev_vs_zero_hi": o["ev_vs_zero_ci"][1], "p_ev_vs_zero_pos": o["p_ev_vs_zero_pos"]})
    return pd.DataFrame(righe)
