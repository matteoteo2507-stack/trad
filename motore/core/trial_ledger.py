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
`decisioni/trial_ledger.json` e' il dato; questo modulo lo legge, lo **verifica** e calcola la
soglia di futilita'. Ogni voce cita le **fonti nel repo** da cui il numero e' stato
ricostruito: un numero senza fonte e' un numero inventato, e qui e' un errore bloccante.

Dove un conteggio storico **non e' ricostruibile** (ORB, London Breakout) il campo vale
`null` e lo dice, invece di mettere un numero plausibile. E' la differenza fra un
registro e una narrazione.

Uso
---
    python -m motore.core.trial_ledger              # stato + verifica
    python -m motore.core.trial_ledger --futilita 250   # soglia di futilita' a 250 osservazioni
    python -m motore.core.trial_ledger --check      # solo verifica, exit 1 se qualcosa non torna
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from math import sqrt
from typing import Optional

__all__ = ["load", "famiglia", "futility_sharpe", "verifica", "tabella", "MOTIVI_CHIUSURA", "GRANDEZZE",
           "NON_GRANDEZZE", "grandezze_condivise"]

ROOT = next(str(p) for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())
LEDGER = os.path.join(ROOT, "decisioni", "trial_ledger.json")

Z95 = 1.6448536269514722          # Phi^-1(0.95)
GAMMA = 0.5772156649              # Eulero-Mascheroni
# Perche' una famiglia e' chiusa (LIFECYCLE §5, DECISIONS 2026-11-04). None = le fonti non lo dicono.
MOTIVI_CHIUSURA = ("refutata", "potenza", "criterio", "metodo")
# Grandezze della DOMANDA PRIMARIA di una famiglia: lette dalle sue regole primarie e dal suo bersaglio; filtri e
# ingressi fissi vanno nelle note (LIFECYCLE §3; DECISIONS 2026-11-21 (2) e (3)). Le sei del modulo 10 §2, il tempo
# come condizionamento e la dipendenza fra i rendimenti contemporanei (I3).
GRANDEZZE = ("tendenza", "spostamento_media", "volatilita", "volume", "livelli", "candela", "tempo",
             "dipendenza_rendimenti", "segnale_esterno")
# Etichetta, non grandezza (DECISIONS 2026-11-21 (3)): la famiglia esegue la decisione di un terzo (segnali copiati).
# Non conta fra le grandezze condivise (due fonti diverse non sono la stessa famiglia) ed e' vietata per i binari
# `strumenti` e `hub`, perche' non diventi una via per sfuggire al controllo.
NON_GRANDEZZE = ("segnale_esterno",)
# Verso un'ALTRA famiglia esiste solo `parente` (famiglia distinta per bersaglio o meccanismo, con la fonte). Una
# riapertura non e' una parentela: per il §7a si fa sulla STESSA voce del contatore (trial sommati, quota del binario
# d'origine, un round, binario invariato), quindi `riapertura` verso un altro id e' un errore (G1 del 21/11, B1).
TIPI_PARENTELA = ("parente",)
# Le famiglie CLOSED alla data della regola (DECISIONS 2026-11-21 (3)): esenti dall'obbligo di parentela. Ogni altra
# famiglia, anche se poi si chiude, conserva l'obbligo (la relazione dichiarata non si perde alla chiusura).
ESENTI_PARENTELA = ("livelli", "nxt", "opening_range", "tsmom", "meanrev_vol", "seasonality_tom", "round_grid",
                    "trend_momentum", "meanrev_kichev", "mentor_signals", "london_breakout", "forexgump_signals",
                    "mr_indici_rsi2", "momentum_ultima_mezzora")


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
    # `utente_llm` (dal 2026-10-25, Matteo): idea di Matteo con il ragionamento scritto insieme a Claude.
    # Sul passato vale come proposta dall'LLM; e' indipendente solo su dati oltre il cutoff.
    if prov in ("llm", "utente_llm") and fine and fine <= cutoff:
        return ["%s ipotesi %s su dati che finiscono prima del cutoff %s: "
                "non e' una predizione indipendente, serve un forward OLTRE il cutoff"
                % (eti, "proposta da LLM" if prov == "llm" else "scritta con l'LLM (utente_llm)", cutoff)]
    return []


def _usate(dati: dict, binario: str) -> list:
    """Famiglie che hanno usato uno slot di pre-registrazione nel trimestre corrente, per binario.

    Due budget separati (decisione di Matteo, 2026-10-25): `strategie` (le pre-registrazioni da fonte
    esterna di sempre) e `hub` (ipotesi che arrivano dal vault, es. geopolitica; STRATEGY_LIFECYCLE §8).
    Il binario si legge dal campo `binario` della famiglia; assente = `strategie`. I trial di entrambi
    restano nello stesso contatore e nello stesso DSR: il budget separato regola il ritmo, non lo sconto.
    Il terzo binario, `strumenti` (dal 2026-11-11), non ha quota: qui non si conta mai."""
    q = dati.get("trimestre_corrente")
    return [f["id"] for f in dati["famiglie"]
            if f.get("prereg_esterna_trimestre") == q and f.get("binario", "strategie") == binario]


PROP_LAB_REGISTRO = os.path.join(ROOT, "motore/prop-lab/results/registry.sqlite")
TAG_ESENTI = {"sintetico", "controllo", "fuori_gate"}     # etichette di motore/prop-lab/lab/gate.py che non sono famiglie


def registro_prop_lab(path: str = PROP_LAB_REGISTRO) -> dict:
    """Eventi del registro di prop-lab per etichetta: {id: {"trial": n, "aperture": [(run_id, ts), ...]}}.

    `trial` = combinazioni distinte (strategia, parametri, simbolo, timeframe) provate in fase 1: rigirare la stessa
    variante sugli stessi dati non e' un tentativo nuovo, la stessa variante su un altro simbolo si' (§3).
    Il registro e' il diario degli eventi; il contatore resta la fonte dei numeri (08/10/2026)."""
    if not os.path.exists(path):
        return {}
    import sqlite3
    con = sqlite3.connect(path)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(trials)")}
        out: dict = {}
        if "ledger_id" in cols:
            q = ("SELECT ledger_id, COUNT(DISTINCT strategy || '|' || params || '|' || symbol || '|' || tf) "
                 "FROM trials WHERE stage='stage1' AND ledger_id IS NOT NULL GROUP BY ledger_id")
            for lid, n in con.execute(q):
                out.setdefault(lid, {"trial": 0, "aperture": []})["trial"] = n
        tabelle = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "aperture" in tabelle:
            for lid, run_id, ts in con.execute("SELECT ledger_id, run_id, ts FROM aperture"):
                out.setdefault(lid, {"trial": 0, "aperture": []})["aperture"].append((run_id, ts))
        return out
    finally:
        con.close()


def _verifica_prop_lab(dati: dict, reg: dict) -> list:
    """Il registro di prop-lab e il contatore dicono la stessa cosa? (08/10/2026)"""
    problemi = []
    ids = {f["id"]: f for f in dati["famiglie"]}
    for lid in reg:
        if lid not in TAG_ESENTI and lid not in ids:
            problemi.append("%-16s tentativi nel registro di prop-lab per una famiglia che il contatore non ha"
                            % lid[:16])
    lim = dati["budget"].get("holdout_aperture_per_famiglia", 1)
    for f in dati["famiglie"]:
        if not f.get("registro_prop_lab"):
            continue
        eti = "%-16s" % f["id"]
        r = reg.get(f["id"], {"trial": 0, "aperture": []})
        attesi = r["trial"] + int(f.get("trial_fuori_prop_lab", 0))
        if f.get("trial_cumulati") != attesi:
            problemi.append("%s trial_cumulati %s, ma il registro di prop-lab ne conta %d%s: aggiornare il contatore"
                            % (eti, f.get("trial_cumulati"), r["trial"],
                               " (+%d fuori prop-lab)" % f["trial_fuori_prop_lab"] if f.get("trial_fuori_prop_lab") else ""))
        if r["aperture"] and not f.get("holdout_aperto"):
            problemi.append("%s fuori campione aperto in prop-lab (run %s) ma holdout_aperto vuoto nel contatore"
                            % (eti, r["aperture"][0][0]))
        if len(r["aperture"]) > lim:
            problemi.append("%s fuori campione aperto %d volte in prop-lab (budget %d)" % (eti, len(r["aperture"]), lim))
    return problemi


def verifica(dati: Optional[dict] = None, registro: Optional[dict] = None) -> list:
    """Controlli di coerenza del registro. Lista vuota = tutto torna.
    `registro`: eventi di prop-lab (default: letti da `motore/prop-lab/results/registry.sqlite`)."""
    dati = dati or load()
    b = dati["budget"]
    problemi = _verifica_prop_lab(dati, registro_prop_lab() if registro is None else registro)

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
        gf = f.get("gate_finale")
        if gf is not None and gf != "forward":
            problemi.append("%s gate_finale '%s' sconosciuto (ammesso solo: forward)" % (eti, gf))
        # Un LEAD con l'holdout aperto e' legittimo solo se il gate finale dichiarato PRIMA e' il
        # forward (es. Gump, D1: il campione intero e' l'holdout). Senza il campo resta un errore.
        if f.get("stato") == "LEAD" and f.get("holdout_aperto") and gf != "forward":
            problemi.append("%s e' LEAD con holdout gia' aperto: il gate finale non c'e' piu' "
                            "(se e' un forward pre-registrato: gate_finale = \"forward\")" % eti)
        if f.get("stato") == "CLOSED":
            if "motivo_chiusura" not in f:
                problemi.append("%s CLOSED senza motivo_chiusura (ammessi: %s, o null se le fonti non "
                                "lo dicono)" % (eti, ", ".join(MOTIVI_CHIUSURA)))
            elif f["motivo_chiusura"] not in MOTIVI_CHIUSURA + (None,):
                problemi.append("%s motivo_chiusura '%s' sconosciuto" % (eti, f["motivo_chiusura"]))
        elif f.get("motivo_chiusura") is not None:
            problemi.append("%s ha un motivo_chiusura ma non e' CLOSED" % eti)
        gr = f.get("grandezze")
        if not gr:
            problemi.append("%s grandezze non dichiarate: senza, 'stessa grandezza = stessa famiglia' non si "
                            "controlla (ammesse: %s)" % (eti, ", ".join(GRANDEZZE)))
        else:
            ignote = [g for g in gr if g not in GRANDEZZE]
            if ignote:
                problemi.append("%s grandezza sconosciuta %s (ammesse: %s; una nuova si decide in DECISIONS)"
                                % (eti, ignote, ", ".join(GRANDEZZE)))
            if f.get("binario") in ("strumenti", "hub") and any(g in NON_GRANDEZZE for g in gr):
                problemi.append("%s binario %s con l'etichetta %s: e' riservata ai segnali copiati da terzi"
                                % (eti, f["binario"], "/".join(NON_GRANDEZZE)))
        problemi += _verifica_parentela(f, eti, dati)
        problemi += _contaminazione(f, eti, b.get("llm_knowledge_cutoff"))

    # quota di pre-registrazioni del trimestre: due budget separati (strategie esterne, hub)
    q = dati.get("trimestre_corrente")
    usate = _usate(dati, "strategie")
    if len(usate) > b["prereg_esterne_per_trimestre"]:
        problemi.append("prereg esterne %s: %d usate, budget %d - SFORATO (%s)"
                        % (q, len(usate), b["prereg_esterne_per_trimestre"],
                           ", ".join(usate)))
    hub = _usate(dati, "hub")
    if len(hub) > b.get("prereg_hub_per_trimestre", 1):
        problemi.append("prereg dall'hub %s: %d usate, budget %d - SFORATO (%s)"
                        % (q, len(hub), b.get("prereg_hub_per_trimestre", 1), ", ".join(hub)))
    for f in dati["famiglie"]:
        if f.get("binario", "strategie") not in BINARI:
            problemi.append("%-16s binario '%s' sconosciuto (ammessi: %s)" % (f["id"], f["binario"], ", ".join(BINARI)))
        elif f.get("binario") == "strumenti":
            problemi += _verifica_strumenti(f)
    return problemi


# Binari del contatore. `strumenti` (dal 2026-11-11, DECISIONS 2026-11-10/11): famiglie di strumenti di lettura del
# prezzo, senza quota trimestrale (vale solo il tetto dei round); regole in STRATEGY_LIFECYCLE §8ter.
BINARI = ("strategie", "hub", "strumenti")


def _verifica_strumenti(f: dict) -> list:
    """Una famiglia di strumenti divide il suo errore fra le sottofamiglie PRIMA di ogni test (LIFECYCLE §8ter, S2).

    Controlla: errore di famiglia dichiarato; ogni sottofamiglia con id, quota di errore e benchmark; somma delle
    quote <= errore di famiglia; trial della famiglia = somma dei trial confermativi ed esplorativi delle sottofamiglie
    (le varianti nate dopo un esito si contano anche se non danno verdetto, P2); data d'inizio dell'holdout fissata
    prima di aprirlo (H1)."""
    eti = "%-16s" % f["id"]
    out = []
    alfa = f.get("alfa_famiglia")
    if not isinstance(alfa, (int, float)) or not 0 < alfa < 1:
        out.append("%s strumenti: alfa_famiglia mancante o fuori da (0, 1)" % eti)
        alfa = None
    sotto = f.get("sottofamiglie") or []
    if not sotto:
        out.append("%s strumenti: nessuna sottofamiglia dichiarata (anche una sola va scritta)" % eti)
    somma_alfa, somma_trial = 0.0, 0
    for s in sotto:
        sid = s.get("id", "?")
        if not isinstance(s.get("alfa"), (int, float)) or s["alfa"] <= 0:
            out.append("%s sottofamiglia %s senza quota di errore (alfa)" % (eti, sid))
        else:
            somma_alfa += s["alfa"]
        if not s.get("benchmark"):
            out.append("%s sottofamiglia %s senza benchmark dichiarato prima (S4)" % (eti, sid))
        somma_trial += int(s.get("trial_cumulati") or 0) + int(s.get("varianti_esplorative") or 0)
    if alfa is not None and somma_alfa > alfa + 1e-12:
        out.append("%s strumenti: quote delle sottofamiglie %.4g > alfa di famiglia %.4g" % (eti, somma_alfa, alfa))
    tc = f.get("trial_cumulati")
    if sotto and tc is not None and tc != somma_trial:
        out.append("%s strumenti: trial_cumulati %s ma le sottofamiglie ne sommano %d (confermativi + esplorativi)"
                   % (eti, tc, somma_trial))
    if f.get("holdout_aperto") and not f.get("holdout_inizio"):
        out.append("%s strumenti: holdout aperto senza holdout_inizio dichiarato prima (H1)" % eti)
    return out


def _verifica_parentela(f: dict, eti: str, dati: dict) -> list:
    """Una famiglia che condivide una grandezza con un'altra dichiara la relazione (DECISIONS 2026-11-21 (3), LIFECYCLE
    §3 e §7a): voce `parentela` = [{"famiglia", "tipo": "parente", "fonte"}], con la fonte in DECISIONS o in una
    pre-registrazione. Senza, `--check` fallisce. Cosa controlla davvero: che la relazione sia dichiarata, verso una
    famiglia esistente e diversa che condivide almeno una grandezza, con una fonte che nomina DECISIONS o una
    pre-registrazione. NON puo' controllare che una riapertura sia fatta sulla stessa voce senza cambiare binario: non
    c'e' storia nel contatore (debito, DECISIONS 2026-11-21 (3)). Esenti le famiglie in ESENTI_PARENTELA."""
    out = []
    par = f.get("parentela")
    if par is None:
        par = []
    if not isinstance(par, list) or not all(isinstance(p, dict) for p in par):
        return ["%s parentela malformata: serve una lista di {famiglia, tipo, fonte}" % eti]
    ids = {x["id"] for x in dati["famiglie"]}
    gr_di = {x["id"]: {g for g in x.get("grandezze") or [] if g not in NON_GRANDEZZE} for x in dati["famiglie"]}
    mie = gr_di.get(f["id"], set())
    dichiarate = set()
    for p in par:
        altra = p.get("famiglia")
        if altra == f["id"]:
            out.append("%s parentela verso se stessa" % eti)
        elif altra not in ids:
            out.append("%s parentela con '%s': famiglia inesistente nel contatore" % (eti, altra))
        elif not (mie & gr_di[altra]):
            out.append("%s parentela con %s, che non condivide nessuna grandezza" % (eti, altra))
        if p.get("tipo") == "riapertura":
            out.append("%s 'riapertura' di %s da un'altra voce: per il sez.7a una riapertura si fa sulla STESSA voce "
                       "(trial sommati, quota del binario d'origine, un round, binario invariato)" % (eti, altra))
        elif p.get("tipo") not in TIPI_PARENTELA:
            out.append("%s parentela con %s: tipo '%s' (ammessi: %s)"
                       % (eti, altra, p.get("tipo"), ", ".join(TIPI_PARENTELA)))
        fonte = str(p.get("fonte") or "")
        if "DECISIONS" not in fonte and "PREREGISTRATION" not in fonte:
            out.append("%s parentela con %s: la fonte deve nominare DECISIONS o una pre-registrazione" % (eti, altra))
        dichiarate.add(altra)
    if f["id"] in ESENTI_PARENTELA:
        return out
    for g, fam in sorted(grandezze_condivise(dati).items()):
        if g not in mie:
            continue
        for altra in fam:
            if altra != f["id"] and altra not in dichiarate:
                out.append("%s condivide '%s' con %s senza parentela dichiarata: o e' una riapertura (sez.7a, sulla "
                           "voce di %s) o una famiglia parente con fonte in DECISIONS" % (eti, g, altra, altra))
                dichiarate.add(altra)
    return out


def grandezze_condivise(dati: dict) -> dict:
    """{grandezza: [id, ...]} per le grandezze dichiarate da piu' di una famiglia.

    Non e' un errore: le famiglie nate prima della regola del 2026-10-08 (3) restano come sono, e Matteo puo' tenerne
    due sulla stessa grandezza (DECISIONS 2026-11-21 (3): `tsmom` e `trend_momentum`). Serve a vedere, prima di aprire
    una famiglia, quali esistono gia' sulla stessa grandezza; una famiglia CLOSED riproposta come strumento resta una
    riapertura (LIFECYCLE §7a)."""
    per = {}
    for f in dati["famiglie"]:
        for g in dict.fromkeys(f.get("grandezze") or []):      # una grandezza ripetuta conta una volta
            if g in NON_GRANDEZZE:                              # i segnali copiati non sono una grandezza comune
                continue
            per.setdefault(g, []).append(f["id"])
    return {g: ids for g, ids in per.items() if len(ids) > 1}


def _stato_esterne(dati: dict) -> str:
    q = dati.get("trimestre_corrente")
    usate = _usate(dati, "strategie")
    hub = _usate(dati, "hub")
    b = dati["budget"]
    avviso = " <-- soglia di allarme raggiunta" \
        if len(usate) >= b["prereg_esterne_per_trimestre_soglia_allarme"] else ""
    return ("pre-registrazioni esterne %s: %d di %d-%d usate (%s)%s\n"
            "pre-registrazioni dall'hub %s: %d di %d usate (%s)"
            % (q, len(usate), b["prereg_esterne_per_trimestre_soglia_allarme"],
               b["prereg_esterne_per_trimestre"], ", ".join(usate) or "nessuna", avviso,
               q, len(hub), b.get("prereg_hub_per_trimestre", 1), ", ".join(hub) or "nessuna"))


def tabella(dati: Optional[dict] = None) -> str:
    dati = dati or load()
    righe = ["CONTATORE TRIAL PERSISTENTE - aggiornato %s   (STRATEGY_LIFECYCLE sez.3)"
             % dati["aggiornato"], "=" * 96,
             "%-16s %-8s %-8s %7s %7s %-12s %-6s %s"
             % ("famiglia", "stato", "motivo", "trial", "round", "holdout", "est.", "verdetto")]
    for f in sorted(dati["famiglie"], key=lambda x: (x["stato"] != "GO", x["stato"] != "LEAD", x["id"])):
        tc = f.get("trial_cumulati")
        tb = f.get("trial_budget")
        trial = "?" if tc is None else (str(tc) if tb is None else "%d/%d" % (tc, tb))
        rb = f.get("round_budget")
        rd = f.get("round_rifinitura")
        rnd = "-" if rd is None else (str(rd) if rb is None else "%d/%d" % (rd, rb))
        ho = f.get("holdout_aperto") or "sigillato"
        mot = (f.get("motivo_chiusura") or "?") if f["stato"] == "CLOSED" else "-"
        righe.append("%-16s %-8s %-8s %7s %7s %-12s %-6s %s"
                     % (f["id"][:16], f["stato"], mot, trial, rnd, ho[:12],
                        "si" if f.get("fonte_esterna") else "no",
                        (f.get("verdetto") or "")[:38]))
    strum = [f for f in dati["famiglie"] if f.get("binario") == "strumenti"]
    for f in strum:
        for s in f.get("sottofamiglie") or []:
            righe.append("  - %-14s alfa %-6s trial %s + %s esplorativi  benchmark: %s"
                         % (s.get("id", "?")[:14], s.get("alfa"), s.get("trial_cumulati", 0),
                            s.get("varianti_esplorative", 0), s.get("benchmark", "?")))
            if s.get("uscita_prima_dell_apertura"):
                righe.append("      USCITA prima dell'apertura, quota riservata: %s"
                             % s["uscita_prima_dell_apertura"][:90])
    righe.append("")
    righe.append(_stato_esterne(dati))
    righe.append("strumenti: nessuna quota trimestrale, solo il tetto dei round (LIFECYCLE sez.8ter); famiglie: %s"
                 % (", ".join(f["id"] for f in strum) or "nessuna"))
    cond = grandezze_condivise(dati)
    if cond:
        righe.append("grandezze con piu' famiglie (LIFECYCLE sez.3; prima di aprirne una, una riapertura e' sez.7a):")
        for g in sorted(cond):
            righe.append("  %-20s %s" % (g, ", ".join(cond[g])))
    nd = [f["id"] for f in dati["famiglie"]
          if f.get("provenienza_ipotesi") == "non_dichiarata"]
    if nd:
        righe.append("provenienza dell'ipotesi NON DICHIARATA: %s" % ", ".join(nd))
        righe.append("  -> non si puo' escludere la contaminazione da knowledge cutoff "
                     "(%s). Per una famiglia CHIUSA e' un'annotazione; per una da "
                     "riaprire e' un bloccante." % dati["budget"].get("llm_knowledge_cutoff"))
    senza = [f["id"] for f in dati["famiglie"] if f["stato"] == "CLOSED" and f.get("motivo_chiusura") is None]
    if senza:
        righe.append("motivo di chiusura NON RICOSTRUIBILE dalle fonti: %s" % ", ".join(senza))
        righe.append("  -> refutata o per potenza non si puo' dire: non vale come prova in nessuno dei due sensi.")
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
