"""Contatore trial PERSISTENTE — `STRATEGY_LIFECYCLE.md` §3.

Perche' esiste
--------------
Il Deflated Sharpe Ratio penalizza il numero di tentativi, e per funzionare il contatore
deve **persistere attraverso le iterazioni del loop**. Il ciclo di vita lo dichiarava
necessario dal 2026-08-04, ma **non esisteva nel codice**: andava ricostruito a mano
dalle pre-registrazioni ogni volta che serviva, cioe' proprio nel momento in cui si e'
meno disposti a essere severi con se stessi.

Il costo di non averlo, misurato: la voce DECISIONS del 2026-08-14 concludeva *"lasciar
correre il forward ORB"*. Era una **decisione**, non una descrizione — non e' mai stata
implementata, e per due settimane e' stata citata come se lo fosse. Non esisteva un
posto dove lo stato reale di un binario fosse registrato e verificabile.

Cosa c'e' dentro
----------------
`docs/trial_ledger.json` e' il dato; questo modulo lo legge, lo **verifica** e calcola la
soglia di futilita'. Ogni voce cita le **fonti nel repo** da cui il numero e' stato
ricostruito: un numero senza fonte e' un numero inventato, e qui e' un errore bloccante.

Dove un conteggio storico **non e' ricostruibile** (ORB, London Breakout) il campo vale
`null` e lo dice, invece di mettere un numero plausibile. E' la differenza fra un
registro e una narrazione.

Uso
---
    python -m core.trial_ledger              # stato + verifica
    python -m core.trial_ledger --futilita 250   # soglia di futilita' a 250 osservazioni
    python -m core.trial_ledger --check      # solo verifica, exit 1 se qualcosa non torna
"""
from __future__ import annotations

import json
import os
from math import sqrt
from typing import Optional

__all__ = ["load", "famiglia", "futility_sharpe", "verifica", "tabella"]

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LEDGER = os.path.join(ROOT, "docs", "trial_ledger.json")

Z95 = 1.6448536269514722          # Phi^-1(0.95)
GAMMA = 0.5772156649              # Eulero-Mascheroni


def load(path: str = LEDGER) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def famiglia(fid: str, dati: Optional[dict] = None) -> Optional[dict]:
    dati = dati or load()
    for f in dati["famiglie"]:
        if f["id"] == fid:
            return f
    return None


# ---------------------------------------------------------------------------
def _norm_inv(p: float) -> float:
    """Quantile normale standard (Acklam), sufficiente per la soglia di Bailey-LdP."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = sqrt(-2 * __import__("math").log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = sqrt(-2 * __import__("math").log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def futility_sharpe(n_trials: int, n_obs: int, periods_per_year: int = 252) -> float:
    """Sharpe annualizzato **minimo** sotto cui il DSR non puo' essere significativo.

    E' la *regola di futilita'* di `STRATEGY_LIFECYCLE.md` §3 resa un numero: se il
    **migliore** risultato che hai visto su tutte le varianti sta sotto questa soglia,
    continuare a iterare e' matematicamente inutile — ti servirebbe un effetto piu'
    grande di qualunque cosa tu abbia mai osservato. → kill immediato.

    Deriva dall'invertire il DSR sotto ipotesi gaussiana:

        SR_min = E[max SR | N trial nulli] + z_0.95 / sqrt(n_obs - 1)

    ⚠️ **E' un pavimento, non la soglia vera.** Con skew negativo o code grasse — cioe'
    sempre, nel trading — il requisito **sale**. Chi passa di poco questa soglia non ha
    passato niente.

    Args:
        n_trials: trial **cumulati** della famiglia, non di questo test.
        n_obs: numero di osservazioni (trade o periodi) su cui si misura lo Sharpe.
        periods_per_year: per l'annualizzazione.
    """
    if n_trials < 1 or n_obs < 3:
        return float("nan")
    if n_trials == 1:
        thr = 0.0
    else:
        z1 = _norm_inv(1.0 - 1.0 / n_trials)
        z2 = _norm_inv(1.0 - 1.0 / (n_trials * 2.718281828459045))
        thr = ((1.0 - GAMMA) * z1 + GAMMA * z2) / sqrt(n_obs)
    return (thr + Z95 / sqrt(n_obs - 1)) * sqrt(periods_per_year)


# ---------------------------------------------------------------------------
def _contaminazione(f: dict, eti: str, cutoff: Optional[str]) -> list:
    """Contaminazione da knowledge cutoff dell'LLM — checklist 5 del guardiano.

    Un'ipotesi **proposta da un LLM** su dati **precedenti** al suo cutoff non e' una
    predizione indipendente: puo' essere memorizzazione. Vale se arriva da (a) una fonte
    esterna umana datata e citabile, (b) un razionale economico che non richiede di
    conoscere l'esito, (c) un forward oltre il cutoff.

    Evidenza esterna: *Profit Mirage* (arXiv 2510.07920) — spostando la finestra oltre il
    cutoff, quasi tutti gli agenti LLM pubblicati non battono un baseline random.
    """
    if not cutoff:
        return []
    prov = f.get("provenienza_ipotesi")
    fine = f.get("finestra_dati_fine")
    if prov is None:
        return ["%s provenienza dell'ipotesi non registrata (campo assente)" % eti]
    if prov == "llm" and fine and fine <= cutoff:
        return ["%s ipotesi proposta da LLM su dati che finiscono prima del cutoff %s: "
                "non e' una predizione indipendente, serve un forward OLTRE il cutoff"
                % (eti, cutoff)]
    return []


def verifica(dati: Optional[dict] = None) -> list:
    """Controlli di coerenza del registro. Lista vuota = tutto torna."""
    dati = dati or load()
    b = dati["budget"]
    problemi = []

    for f in dati["famiglie"]:
        eti = "%-16s" % f["id"]
        if not f.get("fonti"):
            problemi.append("%s nessuna FONTE citata: il numero non e' verificabile" % eti)
        r = f.get("round_rifinitura")
        if r is not None and r > b["round_rifinitura_per_famiglia"]:
            problemi.append("%s round di rifinitura %d > budget %d (kill di budget sez.6b)"
                            % (eti, r, b["round_rifinitura_per_famiglia"]))
        tb = f.get("trial_budget")
        tc = f.get("trial_cumulati")
        if tb is not None and tc is not None and tc > tb:
            problemi.append("%s trial cumulati %d > budget dichiarato %d" % (eti, tc, tb))
        if f.get("stato") == "LEAD" and f.get("holdout_aperto"):
            problemi.append("%s e' LEAD con holdout gia' aperto: il gate finale non c'e' piu'"
                            % eti)
        problemi += _contaminazione(f, eti, b.get("llm_knowledge_cutoff"))

    # quota di pre-registrazioni esterne del trimestre
    q = dati.get("trimestre_corrente")
    usate = [f["id"] for f in dati["famiglie"]
             if f.get("prereg_esterna_trimestre") == q]
    if len(usate) > b["prereg_esterne_per_trimestre"]:
        problemi.append("prereg esterne %s: %d usate, budget %d - SFORATO (%s)"
                        % (q, len(usate), b["prereg_esterne_per_trimestre"],
                           ", ".join(usate)))
    return problemi


def _stato_esterne(dati: dict) -> str:
    q = dati.get("trimestre_corrente")
    usate = [f["id"] for f in dati["famiglie"]
             if f.get("prereg_esterna_trimestre") == q]
    b = dati["budget"]
    avviso = " <-- soglia di allarme raggiunta" \
        if len(usate) >= b["prereg_esterne_per_trimestre_soglia_allarme"] else ""
    return ("pre-registrazioni esterne %s: %d di %d-%d usate (%s)%s"
            % (q, len(usate), b["prereg_esterne_per_trimestre_soglia_allarme"],
               b["prereg_esterne_per_trimestre"], ", ".join(usate) or "nessuna", avviso))


def tabella(dati: Optional[dict] = None) -> str:
    dati = dati or load()
    righe = ["CONTATORE TRIAL PERSISTENTE - aggiornato %s   (STRATEGY_LIFECYCLE sez.3)"
             % dati["aggiornato"], "=" * 96,
             "%-16s %-8s %7s %7s %-12s %-6s %s"
             % ("famiglia", "stato", "trial", "round", "holdout", "est.", "verdetto")]
    for f in sorted(dati["famiglie"], key=lambda x: (x["stato"] != "GO", x["stato"] != "LEAD", x["id"])):
        tc = f.get("trial_cumulati")
        tb = f.get("trial_budget")
        trial = "?" if tc is None else (str(tc) if tb is None else "%d/%d" % (tc, tb))
        rb = f.get("round_budget")
        rd = f.get("round_rifinitura")
        rnd = "-" if rd is None else (str(rd) if rb is None else "%d/%d" % (rd, rb))
        ho = f.get("holdout_aperto") or "sigillato"
        righe.append("%-16s %-8s %7s %7s %-12s %-6s %s"
                     % (f["id"][:16], f["stato"], trial, rnd, ho[:12],
                        "si" if f.get("fonte_esterna") else "no",
                        (f.get("verdetto") or "")[:38]))
    righe.append("")
    righe.append(_stato_esterne(dati))
    nd = [f["id"] for f in dati["famiglie"]
          if f.get("provenienza_ipotesi") == "non_dichiarata"]
    if nd:
        righe.append("provenienza dell'ipotesi NON DICHIARATA: %s" % ", ".join(nd))
        righe.append("  -> non si puo' escludere la contaminazione da knowledge cutoff "
                     "(%s). Per una famiglia CHIUSA e' un'annotazione; per una da "
                     "riaprire e' un bloccante." % dati["budget"].get("llm_knowledge_cutoff"))
    non_ric = [f["id"] for f in dati["famiglie"] if f.get("trial_cumulati") is None]
    if non_ric:
        righe.append("trial NON RICOSTRUIBILI (mai scritti all'epoca): %s" % ", ".join(non_ric))
        righe.append("  -> non si inventa un numero: per il DSR di queste famiglie vale la "
                     "raccomandazione Bailey-LdP (100 x N_params).")
    return "\n".join(righe)


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    dati = load()
    solo_check = "--check" in argv
    if not solo_check:
        print(tabella(dati))
        print()

    if "--futilita" in argv:
        n_obs = int(argv[argv.index("--futilita") + 1])
        print("SOGLIA DI FUTILITA' a n_obs = %d (Sharpe annualizzato minimo)" % n_obs)
        print("-" * 60)
        for f in dati["famiglie"]:
            tc = f.get("trial_cumulati")
            if tc is None or tc < 1:
                continue
            print("  %-16s trial %-4d -> Sharpe > %.2f perche' il DSR possa essere sig."
                  % (f["id"], tc, futility_sharpe(tc, n_obs)))
        print("  (pavimento gaussiano: con skew negativo o code grasse la soglia SALE)")
        print()

    problemi = verifica(dati)
    if problemi:
        print("VERIFICA: %d PROBLEMI" % len(problemi))
        for p in problemi:
            print("  - %s" % p)
        return 1
    print("VERIFICA: nessun problema (budget, holdout, quota esterne, fonti citate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
