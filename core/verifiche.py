"""Verifiche di metodo: i buchi di PRIORITA' 1 del distillamento Quant Guild (DECISIONS 2026-09-30).

Una primitiva per ogni domanda che prima si rispondeva a mano, in copie sparse, o non si faceva.
Catalogo e fonti: `fondamenti_tecnici/_sorgenti/insight_da_yt/_triage/quantguild/SINTESI.md` §8.

| buco | domanda | primitiva |
|---|---|---|
| 2 | il test poteva vedere l'effetto? | `mde`, `n_richiesto` |
| 37 | "p = 0,048" e "p = 0,062" sono diversi? | `pvalue_mc`, `repliche_per_distinguere` |
| 29 | gli esiti sono indipendenti? | `runs_test` |
| 22 | una soglia "peggior x%" lo e' davvero? | `test_eccedenze` |
| 27 | quante operazioni prima di k perdite di fila, per puro caso? | `attesa_trade_prima_di_k_perdite`, `prob_serie_perdite` |
| 5 + 28 | il forward si sta degradando rispetto al backtest? | `SPRTBernoulli`, `CUSUMInferiore` |
| 46 | con che frequenza e finestra e' calcolata questa correlazione? | `correlazione_dichiarata` |

Regola comune ai monitor (buchi 5 e 28): i parametri di riferimento sono quelli **fissi** della
pre-registrazione, mai statistiche mobili ristimate in corsa. Una banda mobile si ricentra dopo una rottura
e **assorbe il degrado**: dopo qualche settimana il livello peggiore diventa "atteso" (blocco C, C4).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats


# ---- buco 2: potenza e dimensione campionaria --------------------------------------------------

def fattore_potenza(alpha: float = 0.05, potenza: float = 0.80) -> float:
    """z_{1-alpha/2} + z_{potenza}. Con alpha 0,05 e potenza 80% vale ~2,80."""
    return float(stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(potenza))


def mde(sd: float, n: float, alpha: float = 0.05, potenza: float = 0.80) -> float:
    """Effetto minimo rilevabile su una media: fattore * sd / sqrt(n).

    `n` e' il numero di osservazioni **indipendenti**: con esiti raggruppati (vedi `runs_test`) va
    passato un n efficace, non il conteggio grezzo, altrimenti l'MDE e' troppo stretto.
    Un verdetto negativo si scrive sempre con l'MDE accanto: "non dimostrato" non e' "refutato".
    """
    if n <= 0 or not np.isfinite(sd):
        return float("nan")
    return fattore_potenza(alpha, potenza) * sd / math.sqrt(n)


def n_richiesto(sd: float, effetto: float, alpha: float = 0.05, potenza: float = 0.80) -> int:
    """Osservazioni indipendenti per vedere `effetto`: n ~ (fattore * sd / effetto)^2.

    Es. (SINTESI, B22): con E = +0,04R e sd ~ 1R servono ~5.000 trade; con sd 2,7R, ~36.000.
    """
    if effetto <= 0:
        raise ValueError("effetto deve essere > 0")
    return int(math.ceil((fattore_potenza(alpha, potenza) * sd / effetto) ** 2))


# ---- buco 37: il p-value Monte Carlo ha un errore ---------------------------------------------

def pvalue_mc(superamenti: int, repliche: int, conf: float = 0.95) -> dict:
    """p-value di un test Monte Carlo/permutazione **con** il suo errore di stima.

    - `p` = (b + 1) / (B + 1) (Phipson & Smyth 2010): non vale mai 0, perche' l'osservato e' una delle
      permutazioni possibili. `p_grezzo` = b / B e' quello che i nostri motori riportavano.
    - `se` = sqrt(p (1 - p) / B): con B = 1.000 e p ~ 0,05 vale ~0,007, quindi "0,048" e "0,062" **non
      sono distinguibili** (SINTESI, F2).
    - `low`/`high`: intervallo esatto (Clopper-Pearson) su b / B.
    """
    b, B = int(superamenti), int(repliche)
    if B <= 0 or b < 0 or b > B:
        raise ValueError("serve 0 <= superamenti <= repliche, repliche > 0")
    p = (b + 1) / (B + 1)
    ic = stats.binomtest(b, B).proportion_ci(confidence_level=conf, method="exact")
    return {"p": p, "p_grezzo": b / B, "se": math.sqrt(p * (1 - p) / B),
            "low": float(ic.low), "high": float(ic.high), "repliche": B, "conf": conf}


def pvalue_distinguibile(res: dict, soglia: float = 0.05) -> bool:
    """True se la soglia sta fuori dall'intervallo del p-value: solo allora "sopra/sotto 0,05" ha senso."""
    return soglia < res["low"] or soglia > res["high"]


def repliche_per_distinguere(p: float, distanza: float, conf: float = 0.95) -> int:
    """Repliche perche' la semi-ampiezza dell'intervallo del p-value sia <= `distanza`."""
    z = stats.norm.ppf(1 - (1 - conf) / 2)
    return int(math.ceil(z * z * p * (1 - p) / distanza ** 2))


# ---- buco 29: indipendenza degli esiti --------------------------------------------------------

def runs_test(esiti) -> dict:
    """Test delle successioni (Wald-Wolfowitz) sulla sequenza vinto/perso.

    `z < 0`: **meno sequenze del caso** = esiti raggruppati (perdite che arrivano insieme). Allora ogni
    soglia calcolata come se gli esiti fossero indipendenti (serie negative, drawdown attesi, Monte Carlo
    che rimescola i trade) e' **ottimista** e va rivista al ribasso.

    Formula identica a quella scritta a mano in `analysis/mentor_signals/withdrawal_thresholds.py`
    (C3, 18/09): l'equivalenza e' in `core/tests/test_verifiche.py`.
    """
    w = np.asarray(esiti, dtype=bool)
    n = w.size
    n1 = int(w.sum())
    n0 = n - n1
    nan = {"n": n, "sequenze": float("nan"), "attese": float("nan"), "z": float("nan"),
           "p": float("nan"), "lettura": "non calcolabile (servono vinti e persi)"}
    if n < 2 or n1 == 0 or n0 == 0:
        return nan
    sequenze = 1 + int((w[1:] != w[:-1]).sum())
    mu = 2 * n1 * n0 / n + 1
    var = 2 * n1 * n0 * (2 * n1 * n0 - n) / (n * n * (n - 1))
    if var <= 0:
        return nan
    z = (sequenze - mu) / math.sqrt(var)
    p = float(2 * stats.norm.sf(abs(z)))
    if p >= 0.05:
        lettura = "indipendenza non respinta"
    elif z < 0:
        lettura = "esiti RAGGRUPPATI: le soglie i.i.d. sono ottimiste"
    else:
        lettura = "esiti ALTERNATI piu' del caso"
    return {"n": n, "sequenze": sequenze, "attese": mu, "z": z, "p": p, "lettura": lettura}


# ---- buco 22: backtest per eccedenze ----------------------------------------------------------

def test_eccedenze(violazioni, alpha: float, n: int | None = None) -> dict:
    """Una soglia dichiarata come "il peggior alpha" viene superata davvero con frequenza alpha?

    `violazioni`: array booleano (True = soglia superata) oppure un conteggio, con `n`.
    Test di Kupiec (proportion of failures, rapporto di verosimiglianza, chi quadro con 1 g.d.l.) e
    binomiale esatto. Si applica alle soglie di ritiro §8bis, al limite giornaliero del risk gate, ai
    percentili del Monte Carlo. Esempio del video (blocco D): VaR a varianza costante 40% di eccedenze
    contro 5% attese -> modello inservibile.
    """
    if n is None:
        v = np.asarray(violazioni, dtype=bool)
        x, n = int(v.sum()), int(v.size)
    else:
        x = int(violazioni)
    if n <= 0 or not 0 < alpha < 1 or not 0 <= x <= n:
        raise ValueError("argomenti non validi")
    pi = x / n

    def _ll(prob: float) -> float:
        a = (n - x) * math.log(1 - prob) if x < n else 0.0
        b = x * math.log(prob) if x > 0 else 0.0
        return a + b

    lr = -2 * (_ll(alpha) - (_ll(pi) if 0 < pi < 1 else 0.0))
    p_lr = float(stats.chi2.sf(max(lr, 0.0), 1))
    p_bin = float(stats.binomtest(x, n, alpha).pvalue)
    if p_bin >= 0.05:
        verdetto = "compatibile con la soglia dichiarata"
    elif pi > alpha:
        verdetto = "SOTTOSTIMA il rischio: troppe eccedenze"
    else:
        verdetto = "troppo prudente: meno eccedenze del dichiarato"
    return {"eccedenze": x, "n": n, "attese": alpha * n, "frazione": pi, "alpha": alpha,
            "lr": lr, "p_lr": p_lr, "p_binomiale": p_bin, "verdetto": verdetto}


# ---- buco 27: serie di perdite attese per puro caso -------------------------------------------

def attesa_trade_prima_di_k_perdite(q: float, k: int) -> float:
    """Numero atteso di operazioni prima di vedere k perdite di fila: sum_{i=1..k} q^(-i).

    q = probabilita' di perdita. Win rate 50%, k = 5 -> 62 operazioni: una serie di 5 perdite **non** e'
    un'anomalia. ⚠️ Assume esiti indipendenti: se `runs_test` dice "raggruppati", le serie arrivano
    **prima**, quindi questo numero e' un pavimento ottimista.
    """
    if not 0 < q < 1 or k < 1:
        raise ValueError("serve 0 < q < 1 e k >= 1")
    return float(sum(q ** -i for i in range(1, k + 1)))


def prob_serie_perdite(q: float, k: int, n: int) -> float:
    """P(almeno una serie di >= k perdite consecutive in n operazioni indipendenti). Esatta (ricorsione)."""
    if not 0 <= q <= 1 or k < 1 or n < 0:
        raise ValueError("argomenti non validi")
    # stato = lunghezza della serie in corso (0..k-1); massa assorbita = serie gia' avvenuta
    dist = np.zeros(k)
    dist[0] = 1.0
    assorbita = 0.0
    for _ in range(n):
        nuova = np.zeros(k)
        nuova[0] = dist.sum() * (1 - q)
        nuova[1:] = dist[:-1] * q
        assorbita += dist[-1] * q
        dist = nuova
    return float(assorbita)


# ---- buchi 5 + 28: sorveglianza del forward contro la distribuzione FISSA ---------------------

@dataclass
class SPRTBernoulli:
    """Test sequenziale di Wald sul win rate: H0 = win rate del backtest, H1 = win rate degradato.

    Si aggiorna trade per trade con errori controllati (alpha = falso allarme, beta = degrado non visto),
    invece di aspettare che il drawdown esca dalla distribuzione. `p0` e `p1` si scrivono nella
    pre-registrazione del forward e **non si ristimano in corsa**.

    Stato: "continua" | "degrado" (accetta H1: ritiro/indagine) | "in_linea" (accetta H0). Con
    `riparti_su_h0=True` (default, sorveglianza continua) dopo "in_linea" il test riparte da zero.
    """

    p0: float
    p1: float
    alpha: float = 0.05
    beta: float = 0.20
    riparti_su_h0: bool = True
    llr: float = 0.0
    n: int = 0
    storia: list = field(default_factory=list)

    def __post_init__(self):
        if not 0 < self.p1 < self.p0 < 1:
            raise ValueError("serve 0 < p1 < p0 < 1 (p1 = win rate degradato)")
        self.sup = math.log((1 - self.beta) / self.alpha)
        self.inf = math.log(self.beta / (1 - self.alpha))

    def aggiorna(self, vinto: bool) -> str:
        self.n += 1
        self.llr += (math.log(self.p1 / self.p0) if vinto
                     else math.log((1 - self.p1) / (1 - self.p0)))
        if self.llr >= self.sup:
            stato = "degrado"
        elif self.llr <= self.inf:
            stato = "in_linea"
            if self.riparti_su_h0:
                self.llr = 0.0
        else:
            stato = "continua"
        self.storia.append(stato)
        return stato


@dataclass
class CUSUMInferiore:
    """CUSUM unilaterale verso il basso sulla media di R per trade, tarato sul backtest.

    `mu0`, `sigma0`: media e deviazione di R **dichiarate** nella pre-registrazione (fisse).
    `k`: tolleranza in deviazioni (0,5 = si cerca uno spostamento di ~1 deviazione); `h`: soglia d'allarme.
    Ogni passo registra anche l'**innovazione standardizzata** (x - mu0) / sigma0 (buco 28): se il
    modello regge ha media ~0 e varianza ~1; una deriva sistematica dice che il forward sorprende il
    backtest prima che lo dica il drawdown.
    """

    mu0: float
    sigma0: float
    k: float = 0.5
    h: float = 5.0
    s: float = 0.0
    n: int = 0
    innovazioni: list = field(default_factory=list)

    def __post_init__(self):
        if not self.sigma0 > 0:
            raise ValueError("sigma0 deve essere > 0")

    def aggiorna(self, r: float) -> bool:
        """Aggiunge il risultato di un trade; True = allarme (spostamento verso il basso)."""
        self.n += 1
        z = (r - self.mu0) / self.sigma0
        self.innovazioni.append(z)
        self.s = max(0.0, self.s - z - self.k)
        return self.s > self.h

    def riepilogo_innovazioni(self) -> dict:
        z = np.asarray(self.innovazioni, dtype=float)
        if z.size < 2:
            return {"n": int(z.size), "media": float("nan"), "varianza": float("nan")}
        return {"n": int(z.size), "media": float(z.mean()), "varianza": float(z.var(ddof=1)),
                "se_media": float(1 / math.sqrt(z.size))}


# ---- buco 46: correlazioni con frequenza e finestra dichiarate --------------------------------

def correlazione_dichiarata(x: pd.Series, y: pd.Series, frequenza: str, finestra: int) -> dict:
    """Correlazione di due serie di rendimenti con **frequenza e finestra obbligatorie**.

    Una correlazione senza frequenza e finestra non e' un numero: JNJ/CMG valgono 0,01 annuale, 0,13
    mensile, 0,17 giornaliera **con punte a 0,73** (blocco H, H2) — e le punte cadono dove si subisce il
    drawdown. Riporta la correlazione sull'intero campione e la distribuzione di quella mobile.

    x, y: rendimenti semplici con DatetimeIndex. `frequenza`: alias pandas ("D", "W", "ME"...), i
    rendimenti si compongono dentro il periodo. `finestra`: numero di periodi della correlazione mobile.
    """
    df = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    agg = (1 + df).resample(frequenza).prod() - 1
    agg = agg[(agg != 0).any(axis=1)].dropna()
    n = len(agg)
    if n < max(3, finestra):
        raise ValueError(f"troppi pochi periodi ({n}) per la finestra {finestra}")
    mob = agg["x"].rolling(finestra).corr(agg["y"]).dropna()
    return {"frequenza": frequenza, "finestra": finestra, "periodi": n,
            "intero_campione": float(agg["x"].corr(agg["y"])),
            "mobile_min": float(mob.min()), "mobile_mediana": float(mob.median()),
            "mobile_max": float(mob.max())}


# =================================================================================================
# PRIORITA' 2 (2026-09-30): rendere dimensionabile cio' che oggi e' a soglia fissa
# =================================================================================================

# ---- buco 15: probabilita' di toccare un obiettivo prima di un limite -------------------------

def prob_obiettivo_prima_del_limite(mu: float, sigma: float, obiettivo: float, limite: float) -> float:
    """P(il capitale sale di `obiettivo` prima di scendere di `limite`), moto browniano con deriva.

    `mu`, `sigma`: media e deviazione del P&L **per operazione**, nelle stesse unita' di obiettivo e
    limite (es. % di capitale). Con theta = 2 mu / sigma^2:
        P = (1 - e^(theta * limite)) / (e^(-theta * obiettivo) - e^(theta * limite)),
    e con mu = 0, P = limite / (obiettivo + limite). Una challenge +8% / -10% **senza edge** si supera
    per caso nel 10/18 = ~56% dei casi (blocco C, C2): e' il numero contro cui leggere un "l'ho passata".
    """
    if obiettivo <= 0 or limite <= 0 or sigma <= 0:
        raise ValueError("obiettivo, limite e sigma devono essere > 0")
    theta = 2 * mu / sigma ** 2
    if abs(theta) < 1e-12:
        return limite / (obiettivo + limite)
    return float((1 - math.exp(theta * limite)) / (math.exp(-theta * obiettivo) - math.exp(theta * limite)))


def rovina_del_giocatore(p: float, passi_obiettivo: int, passi_limite: int) -> float:
    """Versione discreta: passi di +1 con probabilita' p e -1 con 1-p. P(+obiettivo prima di -limite)."""
    if not 0 < p < 1 or passi_obiettivo < 1 or passi_limite < 1:
        raise ValueError("argomenti non validi")
    i, N = passi_limite, passi_limite + passi_obiettivo
    if abs(p - 0.5) < 1e-12:
        return i / N
    r = (1 - p) / p
    return float((1 - r ** i) / (1 - r ** N))


# ---- buco 16: le proprieta' del Kelly frazionario ---------------------------------------------

def kelly_crescita(f: float, mu: float, sigma: float) -> float:
    """Crescita geometrica attesa g(f) = f mu - f^2 sigma^2 / 2 (la parabola del blocco C).

    Unifica volatility drag e Kelly: il massimo e' in f* = mu / sigma^2 (`kelly_ottimo`); oltre 2 f* la
    crescita diventa negativa anche con edge positivo.
    """
    return f * mu - 0.5 * f * f * sigma * sigma


def kelly_ottimo(mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma deve essere > 0")
    return mu / sigma ** 2


def kelly_frazionario(k: float) -> dict:
    """Cosa si compra puntando una frazione k del Kelly pieno (0 < k <= 1).

    - crescita: k (2 - k) di quella massima (meta' Kelly = 75% della crescita);
    - varianza della crescita: k^2 (meta' Kelly = 25%);
    - con Kelly pieno P(scendere mai alla frazione x del capitale) = x (meta' capitale: 50%); con la
      frazione k diventa x^(2/k - 1) (meta' Kelly: 12,5%).
    Il Kelly pieno e' ottimo solo con edge noto: con edge stimato l'errore e' asimmetrico (sovrastimare
    costa piu' che sottostimare), ed e' per questo che il reviewer lo tratta come red flag.
    """
    if not 0 < k <= 1:
        raise ValueError("serve 0 < k <= 1")
    return {"k": k, "crescita_relativa": k * (2 - k), "varianza_relativa": k * k,
            "prob_meta_capitale": 0.5 ** (2 / k - 1)}


# ---- buchi 13 + 39: Monte Carlo con incertezza sui parametri, soglie come probabilita' ---------

def rischio_percorsi(r, n_trade: int, n_sim: int = 5000, blocco: int = 1,
                     incertezza_parametri: bool = True, seed: int | None = 42) -> dict:
    """Distribuzione di max drawdown e serie negativa piu' lunga su `n_trade` operazioni future.

    `r`: R per operazione del campione (backtest o forward). Buco 13: il Monte Carlo classico rimescola
    gli **stessi** trade, come se l'E[R] stimato fosse quello vero. Con `incertezza_parametri=True`
    ogni simulazione **prima ricampiona il campione** (un E[R] plausibile diverso), poi genera il
    percorso da quello: le code si allargano quanto l'incertezza sulla stima. `blocco` > 1 ricampiona a
    blocchi contigui quando `runs_test` dice che gli esiti sono raggruppati.
    """
    x = np.asarray(r, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n < 5 or n_trade < 1 or blocco < 1:
        raise ValueError("campione troppo piccolo o parametri non validi")
    rng = np.random.default_rng(seed)
    dd = np.empty(n_sim)
    serie = np.empty(n_sim, dtype=int)
    for s in range(n_sim):
        base = x[rng.integers(0, n, n)] if incertezza_parametri else x
        n_bl = int(math.ceil(n_trade / blocco))
        inizi = rng.integers(0, max(1, n - blocco + 1), n_bl)
        percorso = np.concatenate([base[i:i + blocco] for i in inizi])[:n_trade]
        eq = np.concatenate([[0.0], np.cumsum(percorso)])
        dd[s] = float((np.maximum.accumulate(eq) - eq).max())
        c = m = 0
        for v in percorso:
            c = c + 1 if v < 0 else 0
            m = max(m, c)
        serie[s] = m
    return {"max_drawdown": dd, "serie_negativa": serie, "n_trade": n_trade, "n_sim": n_sim,
            "incertezza_parametri": incertezza_parametri, "blocco": blocco}


def probabilita_violazione(valori, soglia: float, conf: float = 0.95) -> dict:
    """Buco 39: una soglia di ritiro espressa come **probabilita'** che venga superata, con il suo errore.

    Ricetta della variabile indicatrice (blocco F, F1): si registra 1 se il percorso supera la soglia,
    0 altrimenti, e si fa la media. Da' "questo DD di ritiro ha il 5,2% +/- 0,3% di probabilita' di
    scattare per caso" invece di "e' il 95esimo percentile".
    """
    v = np.asarray(valori, dtype=float)
    k = int((v >= soglia).sum())
    ic = stats.binomtest(k, v.size).proportion_ci(confidence_level=conf, method="exact")
    p = k / v.size
    return {"soglia": soglia, "prob": p, "se": math.sqrt(p * (1 - p) / v.size),
            "low": float(ic.low), "high": float(ic.high), "n": int(v.size)}


# ---- buco 45: confronto fra alternative sul decile peggiore -----------------------------------

def confronto_decile_peggiore(esiti_a, esiti_b, q: float = 0.10) -> dict:
    """Confronta due alternative sulla media **e** sulla coda: la media del q peggiore dei percorsi.

    `esiti_a`, `esiti_b`: un esito per percorso simulato (es. rendimento finale o CAGR). Il blocco G
    (G6) mostra un caso in cui il segno del confronto **cambia** passando dalla media al 10% peggiore:
    chi decide su un capitale che non puo' ricominciare deve guardare anche la coda.
    """
    a = np.sort(np.asarray(esiti_a, dtype=float))
    b = np.sort(np.asarray(esiti_b, dtype=float))
    ka, kb = max(1, int(q * a.size)), max(1, int(q * b.size))
    media = float(a.mean() - b.mean())
    coda = float(a[:ka].mean() - b[:kb].mean())
    return {"q": q, "media_a": float(a.mean()), "media_b": float(b.mean()),
            "coda_a": float(a[:ka].mean()), "coda_b": float(b[:kb].mean()),
            "diff_media": media, "diff_coda": coda,
            "segno_cambia": bool(np.sign(media) != np.sign(coda) and media != 0 and coda != 0)}
