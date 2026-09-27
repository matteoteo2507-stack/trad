"""Primitiva UNICA per il baseline random risk-matched.

Perche' esiste
--------------
E' il controllo che ha ribaltato piu' verdetti di qualunque altro in questo workspace —
e fino al 2026-09-19 era **reimplementato ad hoc in otto file**, con pool leggermente
diversi e nessun posto da cui riusarlo. Andava ricordato a mano ogni volta, e ogni volta
il matching andava riverificato a mano (`quant-gatekeeper.md`, Checklist 1).

Precedenti che esistono solo grazie a questo controllo:

* **14/08, escursioni** — tre soglie assolute passate **6/6 e 15/15**, garantite dalla
  costruzione (stop stretto + holding lungo gonfiano i multipli di R). Il random le ha
  ribaltate in **KILL**.
* **Ricerca livelli v1/v2/v3** — il random *structure-free* e' cio' che ha prodotto il
  **NULL su 384 trial**. Senza, sarebbero sembrati positivi.
* **ORB post-2020** — **−0,208** contro un random di **−0,323** [−0,487; −0,157]: il
  risultato "positivo dopo il 2020" non batte il caso.

Cosa fa questo modulo, e cosa NON fa
------------------------------------
Fa **l'estrazione e la verifica del matching**. Non simula: il cammino del trade lo
esegue il chiamante, con lo **stesso identico codice** che usa sul braccio reale —
tipicamente `core.resolve_trade`. E' una separazione voluta: se il baseline usasse un
simulatore proprio, la differenza misurata conterrebbe anche la differenza fra i due
simulatori. E' esattamente l'errore trovato il 27/08 in `excursion.py`, dove il braccio
reale camminava da `j = f` e il random da `k+1`: **l'asimmetria stava nel confronto, non
nel mercato**.

Le due famiglie di baseline in uso qui
--------------------------------------
1. **Istante d'ingresso casuale** (`BarSampler`) — stesso asset, stesso lato, stesso
   rischio in unita' di prezzo, stesse regole d'uscita; **solo il momento e' casuale**.
   Storico: `analysis/nxt/stops.py`, `analysis/nxt/excursion.py`,
   `analysis/nxt/excursion_recheck.py`, `analysis/trend/backtest.py`.
2. **Attributo casuale dal pool reale** (`PoolSampler`) — il livello random e' costruito
   campionando la **distanza** dal pool delle distanze reali dello stesso concetto/lato,
   cosi' che il confronto non diventi "vicino contro lontano".
   Storico: `analysis/level_research/engine.py`, `analysis/level_research/htf.py`.

La cosa che nessuno aveva scritto: l'holding NON si puo' matchare
-----------------------------------------------------------------
La checklist del guardiano elenca *"stessa durata di holding"* fra le dimensioni da
matchare. Preso alla lettera e' **impossibile**: con le stesse regole d'uscita la durata
e' un **esito**, non un input. Quello che si matcha davvero e' la **regola** (stesso
max-hold, stesso SL/TP in unita' di rischio); la durata **realizzata** va poi
**verificata**, ed e' quello che fa `check_matching`. Se le due distribuzioni di holding
divergono, il confronto e' confondato e il numero va letto con quella riserva — non
ignorato, ma nemmeno spacciato per pulito.

    from core.random_baseline import BarSampler, check_matching, gap_ci
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np

__all__ = [
    "MATCH_DIMENSIONS",
    "BarSampler",
    "PoolSampler",
    "MatchReport",
    "check_matching",
    "gap_ci",
]


#: Le dimensioni su cui un baseline deve essere matched, e perche'.
#: Tenute qui perche' codice e `quant-gatekeeper.md` Checklist 1 non divergano.
MATCH_DIMENSIONS = (
    ("asset", "la volatilita' di strumento e' la spiegazione alternativa piu' comune"),
    ("side", "il beta direzionale e' il trap piu' frequente del workspace"),
    ("risk", "altrimenti confronti size, non regole"),
    ("stratum", "anno/regime: altrimenti confronti periodi"),
    ("exit_rule", "stesso max-hold e stessa geometria SL/TP; la DURATA e' un esito, si verifica"),
    ("n_events", "m >= 3 controlli per evento reale, per ridurre la varianza del baseline"),
)

MIN_CONTROLS_PER_EVENT = 3


# ---------------------------------------------------------------------------
# 1. Istante d'ingresso casuale, stratificato
# ---------------------------------------------------------------------------
class BarSampler:
    """Estrae istanti d'ingresso casuali dallo **stesso strato** dell'evento reale.

    Lo strato e' quasi sempre l'anno: e' cio' che impedisce al baseline di confrontare
    periodi diversi invece che regole diverse.

    Args:
        strata: array lungo quanto le barre, con la chiave di strato di ogni barra
            (tipicamente `df["time"].dt.year.values`).
        rng: `np.random.Generator` gia' seminato. Passato dal chiamante perche' la
            riproducibilita' e' sua, non nostra.
        usable: maschera booleana opzionale sulle barre utilizzabili (warm-up di una
            media, finestra di validita' del feed, ...). Storico: `analysis/trend/backtest.py`
            la usa per escludere `lo_v` / `hi_v`.
        trim_tail: quante barre togliere dalla **coda del pool di strato**, perche' un
            controllo estratto a fine strato non avrebbe spazio per essere tenuto.
            Storico: `analysis/nxt/stops.py` usa `MAX_HOLD + 1`.
        min_pool: sotto questa dimensione del pool di strato non si estrae nulla.
            Storico: `stops.py` richiede `> MAX_HOLD + 2`.

    Nota sul determinismo: le estrazioni avvengono con `rng.choice(pool)`, una per
    controllo, **nell'ordine in cui il chiamante chiede gli eventi**. E' cio' che rende
    la primitiva bit-identica alle implementazioni storiche (vedi
    `core/tests/test_random_baseline.py`).
    """

    def __init__(self, strata: Sequence, rng: np.random.Generator,
                 usable: Optional[Sequence[bool]] = None,
                 trim_tail: int = 0, min_pool: int = 0) -> None:
        self._strata = np.asarray(strata)
        self._rng = rng
        self._trim_tail = int(trim_tail)
        self._min_pool = int(min_pool)
        idx = np.arange(len(self._strata))
        if usable is not None:
            mask = np.asarray(usable, dtype=bool)
            if len(mask) != len(self._strata):
                raise ValueError("usable deve essere lungo quanto strata")
            idx = idx[mask]
        self._pools: dict = {}
        for key in np.unique(self._strata[idx]) if len(idx) else []:
            self._pools[key] = idx[self._strata[idx] == key]

    def pool(self, stratum) -> np.ndarray:
        """Il pool effettivo dello strato, dopo `usable`, `min_pool` e `trim_tail`."""
        p = self._pools.get(stratum)
        if p is None or len(p) <= self._min_pool:
            return np.empty(0, dtype=int)
        if self._trim_tail > 0 and len(p) > self._trim_tail:
            p = p[:-self._trim_tail]
        return p

    def draw(self, stratum, m: int) -> list:
        """`m` indici di barra casuali dallo strato. Lista vuota se il pool non basta.

        ⚠️ Con reinserimento, come tutte le implementazioni storiche: su pool di
        migliaia di barre le collisioni sono rare e irrilevanti, ma il chiamante deve
        saperlo perche' significa che i controlli **non sono indipendenti al 100%**.
        Per questo `gap_ci` fa il bootstrap **a cluster sull'evento**.
        """
        p = self.pool(stratum)
        if len(p) == 0:
            return []
        return [int(self._rng.choice(p)) for _ in range(int(m))]


# ---------------------------------------------------------------------------
# 2. Attributo casuale campionato dal pool reale
# ---------------------------------------------------------------------------
class PoolSampler:
    """Campiona un **attributo** dal pool dei valori reali della stessa chiave.

    E' il baseline della ricerca livelli: il livello random non e' un prezzo qualunque,
    e' un prezzo posto a una **distanza estratta dalle distanze reali** dello stesso
    concetto e dello stesso lato. Senza questo matching il confronto diventa "livelli
    vicini contro livelli lontani", che e' una proprieta' della geometria, non
    dell'ipotesi.

        pool = PoolSampler(rng)
        for con, side, dist in livelli_reali:
            pool.add((con, side), dist)
        pool.freeze()
        d_random = pool.draw((con, side), 1)
    """

    def __init__(self, rng: np.random.Generator) -> None:
        self._rng = rng
        self._raw: dict = {}
        self._pools: Optional[dict] = None

    def add(self, key, value: float) -> None:
        if self._pools is not None:
            raise RuntimeError("pool gia' congelato: aggiungere valori dopo il freeze "
                               "significa campionare da un pool che dipende dall'ordine")
        self._raw.setdefault(key, []).append(float(value))

    def freeze(self) -> "PoolSampler":
        """Chiude la raccolta. Il pool deve essere **completo prima** della prima
        estrazione, altrimenti i primi eventi campionano da un pool piu' povero."""
        self._pools = {k: np.asarray(v, dtype=float) for k, v in self._raw.items()}
        return self

    def draw(self, key, m: int) -> list:
        if self._pools is None:
            raise RuntimeError("chiamare freeze() prima di draw()")
        p = self._pools.get(key)
        if p is None or len(p) == 0:
            return []
        return [float(self._rng.choice(p)) for _ in range(int(m))]


# ---------------------------------------------------------------------------
# 3. Verifica del matching — la parte che finora si faceva a mano
# ---------------------------------------------------------------------------
@dataclass
class MatchReport:
    """Esito della verifica. `ok` e' False se **anche una sola** dimensione e' rotta."""

    ok: bool = True
    righe: list = field(default_factory=list)
    rotte: list = field(default_factory=list)
    riserve: list = field(default_factory=list)

    def _add(self, stato: str, dim: str, testo: str) -> None:
        self.righe.append("  [%s] %-12s %s" % (stato, dim, testo))
        if stato == "ROTTO":
            self.ok = False
            self.rotte.append(dim)
        elif stato == "riserva":
            self.riserve.append(dim)

    def __str__(self) -> str:
        if not self.ok:
            stato = "ROTTO su " + ", ".join(self.rotte)
        elif self.riserve:
            stato = "a posto, CON RISERVA su " + ", ".join(self.riserve)
        else:
            stato = "a posto"
        return "\n".join(["MATCHING DEL BASELINE: " + stato] + self.righe)


def check_matching(real, rand, link: str,
                   exact: Sequence[str] = ("asset", "side"),
                   numeric: Sequence[str] = ("risk",),
                   observed: Sequence[str] = ("hold",),
                   tol: float = 0.02,
                   min_controls: int = MIN_CONTROLS_PER_EVENT) -> MatchReport:
    """Verifica che il baseline sia davvero matched, e lo dice in chiaro.

    Non e' un test statistico: e' un **controllo di costruzione**. Confronta ogni
    controllo con il proprio evento reale, non le due medie globali — una media
    globale puo' coincidere con eventi appaiati sbagliati.

    Args:
        real: DataFrame degli eventi reali. Deve contenere `link` e le colonne citate.
        rand: DataFrame dei controlli, con `link` che punta all'evento genitore.
        link: nome della colonna che lega controllo ed evento (es. `"sigid"`, `"legid"`).
        exact: dimensioni che devono coincidere **esattamente** per ogni coppia.
        numeric: dimensioni che devono coincidere entro `tol` (rischio, geometria).
        observed: dimensioni che **non si matchano per costruzione** — sono esiti.
            Vengono solo **riportate**: se divergono, il confronto e' confondato e va
            dichiarato. L'holding sta qui, non in `numeric`.
        tol: tolleranza relativa per `numeric`.
        min_controls: controlli per evento sotto i quali il baseline e' troppo rumoroso.

    Returns:
        `MatchReport`. Stampalo **accanto** al risultato, non in appendice.
    """
    import pandas as pd  # import locale: il modulo resta usabile senza pandas

    rep = MatchReport()
    if len(real) == 0 or len(rand) == 0:
        rep._add("ROTTO", "campione", "reale=%d controlli=%d" % (len(real), len(rand)))
        return rep

    real = pd.DataFrame(real)
    rand = pd.DataFrame(rand)
    for col in (link,):
        if col not in real.columns or col not in rand.columns:
            rep._add("ROTTO", "link", "colonna %r assente su reale o controlli" % col)
            return rep

    # --- numerosita' dei controlli per evento
    per_evento = rand.groupby(link).size()
    orfani = set(rand[link]) - set(real[link])
    if orfani:
        rep._add("ROTTO", "n_events",
                 "%d controlli non hanno un evento reale corrispondente" % len(orfani))
    scoperti = set(real[link]) - set(rand[link])
    med = float(per_evento.median()) if len(per_evento) else 0.0
    stato = "ok" if med >= min_controls and not scoperti else (
        "ROTTO" if med < min_controls else "riserva")
    rep._add(stato, "n_events",
             "%d eventi, %d controlli, mediana %.1f per evento%s"
             % (len(real), len(rand), med,
                "" if not scoperti else " - %d eventi SENZA controlli" % len(scoperti)))

    # --- dimensioni che devono coincidere esattamente
    idx = real.set_index(link)
    for dim in exact:
        if dim not in real.columns or dim not in rand.columns:
            rep._add("riserva", dim, "colonna assente: non verificabile")
            continue
        atteso = rand[link].map(idx[dim])
        diverse = int((atteso.to_numpy() != rand[dim].to_numpy()).sum())
        rep._add("ok" if diverse == 0 else "ROTTO", dim,
                 "coincide su tutte le coppie" if diverse == 0
                 else "%d controlli su %d hanno un valore DIVERSO dall'evento"
                      % (diverse, len(rand)))

    # --- dimensioni numeriche, entro tolleranza
    for dim in numeric:
        if dim not in real.columns or dim not in rand.columns:
            rep._add("riserva", dim, "colonna assente: non verificabile")
            continue
        atteso = rand[link].map(idx[dim]).to_numpy(dtype=float)
        ott = rand[dim].to_numpy(dtype=float)
        buoni = np.isfinite(atteso) & np.isfinite(ott) & (np.abs(atteso) > 0)
        if not buoni.any():
            rep._add("riserva", dim, "nessuna coppia confrontabile")
            continue
        rel = np.abs(ott[buoni] - atteso[buoni]) / np.abs(atteso[buoni])
        fuori = int((rel > tol).sum())
        rep._add("ok" if fuori == 0 else "ROTTO", dim,
                 "scarto relativo max %.2e (tol %.0f%%)" % (rel.max(), 100 * tol)
                 if fuori == 0 else
                 "%d controlli su %d oltre la tolleranza (max %.1f%%)"
                 % (fuori, buoni.sum(), 100 * rel.max()))

    # --- esiti: si riportano, non si matchano
    for dim in observed:
        if dim not in real.columns or dim not in rand.columns:
            continue
        a = real[dim].to_numpy(dtype=float)
        b = rand[dim].to_numpy(dtype=float)
        a, b = a[np.isfinite(a)], b[np.isfinite(b)]
        if len(a) == 0 or len(b) == 0:
            continue
        ma, mb = float(np.median(a)), float(np.median(b))
        scarto = abs(ma - mb) / max(abs(ma), 1e-12)
        stato = "ok" if scarto <= 0.25 else "riserva"
        rep._add(stato, dim,
                 "ESITO, non matchabile: mediana reale %.2f vs random %.2f (%+.0f%%)%s"
                 % (ma, mb, 100 * (mb - ma) / max(abs(ma), 1e-12),
                    "" if stato == "ok" else " <-- CONFONDATO, va dichiarato"))
    return rep


# ---------------------------------------------------------------------------
# 4. Il confronto
# ---------------------------------------------------------------------------
def gap_ci(real, rand, value: str, link: str, conf: float = 0.95,
           n_boot: int = 3000, seed: Optional[int] = 42,
           metric: Optional[Callable[[np.ndarray], float]] = None) -> dict:
    """Divario reale − random, con bootstrap **a cluster sull'evento**.

    Il cluster non e' un dettaglio: gli `m` controlli di uno stesso evento condividono
    strato, rischio e lato, quindi **non sono indipendenti**. Un CI i.i.d. su di loro e'
    finto e troppo stretto — lo stesso difetto che il guardiano segnala per i trade
    sovrapposti.

    Ogni evento contribuisce con `valore_reale − media_dei_suoi_controlli`: e' la forma
    appaiata, quella che toglie di mezzo la variabilita' fra eventi.

    Returns:
        dict con `gap`, `low`, `high`, `n_eventi`, `media_reale`, `media_random`.
    """
    import pandas as pd

    real = pd.DataFrame(real)
    rand = pd.DataFrame(rand)
    med_rand = rand.groupby(link)[value].mean()
    r = real.set_index(link)[value]
    comuni = r.index.intersection(med_rand.index)
    if len(comuni) < 10:
        return {"gap": float("nan"), "low": float("nan"), "high": float("nan"),
                "n_eventi": int(len(comuni)), "media_reale": float("nan"),
                "media_random": float("nan")}
    diff = (r.loc[comuni].to_numpy(float) - med_rand.loc[comuni].to_numpy(float))
    diff = diff[np.isfinite(diff)]

    from core import quant_metrics as qm

    if metric is None:
        metric = lambda v: float(np.mean(v))  # noqa: E731
    ci = qm.bca_bootstrap_ci(diff, metric=metric, conf=conf, n_boot=n_boot, seed=seed)
    return {"gap": float(np.mean(diff)), "low": ci["low"], "high": ci["high"],
            "n_eventi": int(len(diff)),
            "media_reale": float(r.loc[comuni].mean()),
            "media_random": float(med_rand.loc[comuni].mean())}
