"""Pipeline a cancelli:  famiglia -> 1 qualitativo -> 2 costi -> 3 prop x rischio -> 4 conferma OOS.

Ogni fase legge l'output della precedente dalla cartella del run (results/<run_id>/)
così puoi rilanciare una fase sola, cambiare soglie o profili di rischio senza rifare tutto.
"""
from __future__ import annotations

import hashlib
import json
import os
import pickle
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

import numpy as np
import pandas as pd
import yaml

from .backtest import run_backtest
from .data import load_mt5_csv, timeframe_label
from .metrics import trade_metrics, plateau_scores, expand_grid, deflated_sharpe
from .prop import trades_by_day, evaluate, zero_edge
from .risk import build_profiles
from .strategies.base import get_family

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cfg(name):
    # encoding esplicito: su Windows il default e' cp1252 e i "⚠️" dei commenti YAML fanno crashare la fase 2
    with open(os.path.join(ROOT, "config", name), encoding="utf-8") as f:
        return yaml.safe_load(f)


def vkey(strategy, params):
    return f"{strategy}|{json.dumps(params, sort_keys=True)}"


# ---------------------------------------------------------------- registro di TUTTI i tentativi
def registry():
    con = sqlite3.connect(os.path.join(ROOT, "results", "registry.sqlite"))
    con.execute("""CREATE TABLE IF NOT EXISTS trials(run_id TEXT, ts REAL, family TEXT, symbol TEXT, tf TEXT,
                   strategy TEXT, params TEXT, stage TEXT, n INT, expectancy REAL, pf REAL, sharpe_d REAL)""")
    return con


def log_trials(run, rows: pd.DataFrame, stage):
    con = registry()
    con.executemany("INSERT INTO trials VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", [
        (run["run_id"], time.time(), run["family"], run["symbol"], run["tf"], r["strategy"], r["params"], stage,
         int(r["n"]), float(r["expectancy"]) if pd.notna(r["expectancy"]) else None,
         float(r["pf"]) if pd.notna(r["pf"]) and np.isfinite(r["pf"]) else None,
         float(r["sharpe_d"]) if pd.notna(r["sharpe_d"]) else None) for _, r in rows.iterrows()])
    con.commit(); con.close()


def all_trial_sharpes(family, symbol, tf):
    con = registry()
    v = [x[0] for x in con.execute("SELECT sharpe_d FROM trials WHERE family=? AND symbol=? AND tf=? AND stage='stage1'",
                                   (family, symbol, tf)) if x[0] is not None]
    con.close()
    return np.array(v)


# ---------------------------------------------------------------- run
class Run:
    def __init__(self, run_dir):
        self.dir = run_dir
        with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as f:
            self.meta = json.load(f)
        self.df = load_mt5_csv(self.meta["data"])
        self.cut = pd.Timestamp(self.meta["cut_time"])
        self.days_is = pd.DatetimeIndex(sorted({d for d in self.df.index.normalize() if d < self.cut.normalize() and d.dayofweek < 5}))
        self.days_oos = pd.DatetimeIndex(sorted({d for d in self.df.index.normalize() if d >= self.cut.normalize() and d.dayofweek < 5}))

    def path(self, *p):
        return os.path.join(self.dir, *p)

    def save_trades(self, key, tag, trades):
        os.makedirs(self.path("trades"), exist_ok=True)
        fn = self.path("trades", f"{hashlib.md5(key.encode()).hexdigest()[:12]}_{tag}.pkl")
        with open(fn, "wb") as f:
            pickle.dump({"key": key, "trades": trades}, f)
        return fn

    def load_trades(self, fn):
        with open(fn, "rb") as f:
            return pickle.load(f)["trades"]


def new_run(family, symbol, data_path, run_id=None):
    df = load_mt5_csv(data_path)
    tf = timeframe_label(df)
    holdout = cfg("pipeline.yaml")["split"]["holdout_frac"]
    cut_time = df.index[int(len(df) * (1 - holdout))]
    run_id = run_id or f"{family}_{symbol}_{tf}_{time.strftime('%Y%m%d_%H%M%S')}"
    d = os.path.join(ROOT, "results", run_id)
    os.makedirs(d, exist_ok=True)
    meta = {"run_id": run_id, "family": family, "symbol": symbol, "tf": tf, "data": os.path.abspath(data_path),
            "cut_time": str(cut_time), "start": str(df.index[0]), "end": str(df.index[-1]), "bars": len(df)}
    with open(os.path.join(d, "run.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return d


_DF_CACHE: dict = {}


def _bt_variant(args):
    data_path, family, strat_name, params, costs, cut = args
    if data_path not in _DF_CACHE:          # un caricamento per processo worker
        _DF_CACHE[data_path] = load_mt5_csv(data_path)
    df = _DF_CACHE[data_path]
    strat = get_family(family)[strat_name]()
    sig = strat.signals(df, **params)
    tr = run_backtest(df, sig, costs)
    cut = pd.Timestamp(cut)
    return strat_name, params, tr[tr["entry_time"] < cut].reset_index(drop=True), tr[tr["entry_time"] >= cut].reset_index(drop=True)


def _workers():
    """PROPLAB_WORKERS=1 forza l'esecuzione seriale (utile su Windows e per il debug)."""
    try:
        return max(1, int(os.environ.get("PROPLAB_WORKERS", os.cpu_count() or 2)))
    except ValueError:
        return 1


def _map(fn, jobs, chunksize=1):
    """Map parallelo con ricaduta seriale. Su Windows il pool di processi puo' morire con
    'WinError 6 Handle non valido' (visto il 05/10 in fase 2 e in conferma): invece di perdere
    il run si ricalcola tutto in serie. Il risultato non cambia: ogni job e' deterministico."""
    jobs = list(jobs)
    if _workers() > 1 and len(jobs) > 1:
        try:
            with ProcessPoolExecutor(max_workers=_workers()) as ex:
                return list(ex.map(fn, jobs, chunksize=chunksize))
        except (OSError, BrokenProcessPool) as e:
            print(f"[pool] pool di processi fallito ({type(e).__name__}: {e}): ricalcolo in serie")
    return [fn(j) for j in jobs]


# ---------------------------------------------------------------- FASE 1: qualitativo (senza costi)
def stage1(run_dir):
    R = Run(run_dir); m = R.meta; th = cfg("pipeline.yaml")["stage1_qualitativo"]
    fam = get_family(m["family"])
    jobs = [(m["data"], m["family"], sn, p, None, m["cut_time"]) for sn, cls in fam.items() for p in expand_grid(cls.grid)]
    print(f"[fase1] {len(jobs)} varianti da {len(fam)} strategie, backtest IDEALE (no costi) su in-sample...")
    rows = []
    for sn, p, tr_is, _ in _map(_bt_variant, jobs, chunksize=4):
        met = trade_metrics(tr_is, R.days_is)
        rows.append({"strategy": sn, "params": json.dumps(p, sort_keys=True), **{f"p_{k}": v for k, v in p.items()}, **met})
    res = pd.DataFrame(rows)
    # plateau per strategia
    res["plateau_r"] = np.nan
    for sn, cls in fam.items():
        sub = res[res["strategy"] == sn]
        res.loc[sub.index, "plateau_r"] = plateau_scores(sub, {f"p_{k}": v for k, v in cls.grid.items()}).values
    res["pass"] = ((res["n"] >= th["min_trades"]) & (res["expectancy"] >= th["min_expectancy_r"]) &
                   (res["pf"] >= th["min_pf"]) & (res["plateau_r"] > th["min_plateau_r"]))
    res["score"] = res["tstat"] * np.clip(res["plateau_r"] / res["expectancy"].where(res["expectancy"] > 0), 0, 1)
    log_trials(m, res, "stage1")
    res.sort_values(["pass", "score"], ascending=False).to_csv(R.path("stage1_qualitativo.csv"), index=False)
    # riepilogo per strategia (la "famiglia" vista dall'alto)
    summ = res.groupby("strategy").agg(varianti=("n", "size"), pct_positive=("expectancy", lambda x: (x > 0).mean()),
                                       best_exp=("expectancy", "max"), median_exp=("expectancy", "median"),
                                       passano=("pass", "sum")).sort_values("median_exp", ascending=False)
    summ.to_csv(R.path("stage1_famiglia.csv"))
    print(summ.round(3).to_string())
    print(f"[fase1] passano {int(res['pass'].sum())}/{len(res)} varianti -> {R.path('stage1_qualitativo.csv')}")
    return res


# ---------------------------------------------------------------- FASE 2: costi reali
def stage2(run_dir):
    R = Run(run_dir); m = R.meta; th = cfg("pipeline.yaml")["stage2_costi"]
    th1 = cfg("pipeline.yaml")["stage1_qualitativo"]
    s1 = pd.read_csv(R.path("stage1_qualitativo.csv"))
    surv = s1[s1["pass"]].sort_values("score", ascending=False).groupby("strategy").head(th1["top_per_strategy"])
    costs = cfg("symbols.yaml").get(m["symbol"])
    if costs is None:
        raise KeyError(f"{m['symbol']} non presente in config/symbols.yaml")
    print(f"[fase2] {len(surv)} varianti con costi reali ({m['symbol']}: spread/commissione/slippage/swap)...")
    jobs = [(m["data"], m["family"], r["strategy"], json.loads(r["params"]), costs, m["cut_time"]) for _, r in surv.iterrows()]
    gross = {(r["strategy"], r["params"]): r for _, r in surv.iterrows()}
    rows = []
    for sn, p, tr_is, tr_oos in _map(_bt_variant, jobs):
        pk = json.dumps(p, sort_keys=True)
        met = trade_metrics(tr_is, R.days_is)
        g = gross[(sn, pk)]
        key = vkey(sn, p)
        f_is = R.save_trades(key, "is_net", tr_is)
        f_oos = R.save_trades(key, "oos_net", tr_oos)   # salvato ma NON valutato fino alla conferma
        cost_share = (g["expectancy"] - met["expectancy"]) / g["expectancy"] if g["expectancy"] > 0 else np.nan
        rows.append({"strategy": sn, "params": pk, "exp_gross": g["expectancy"], "plateau_r": g["plateau_r"],
                     "cost_share": cost_share, **met, "file_is": f_is, "file_oos": f_oos})
    res = pd.DataFrame(rows)
    if res.empty:
        print("[fase2] nessuna variante dalla fase 1."); res.to_csv(R.path("stage2_costi.csv"), index=False); return res
    res["pass"] = ((res["n"] >= th["min_trades"]) & (res["expectancy"] >= th["min_expectancy_r"]) &
                   (res["pf"] >= th["min_pf"]) & (res["cost_share"] <= th["max_cost_share"]))
    log_trials(m, res, "stage2")
    res = res.sort_values(["pass", "tstat"], ascending=False)
    res.to_csv(R.path("stage2_costi.csv"), index=False)
    cols = ["strategy", "params", "n", "exp_gross", "expectancy", "cost_share", "pf", "win_rate", "max_dd_r", "tstat", "pass"]
    print(res[cols].head(15).round(3).to_string(index=False))
    print(f"[fase2] passano {int(res['pass'].sum())}/{len(res)} -> {R.path('stage2_costi.csv')}")
    return res


# ---------------------------------------------------------------- FASE 3: prop x gestione del rischio
def _prop_job(a):
    day_trades, rules, rname, profile, sc, tag = a
    kw = dict(mode=sc["mode"], n_paths=sc["n_paths"], block=sc["block_days"], stride=sc.get("stride_days", 5))
    out = evaluate(day_trades, rules, profile, **kw)
    # stessi trade a vantaggio ZERO, stessi percorsi: l'EV che resta e' valore d'opzione della challenge
    z = evaluate(zero_edge(day_trades), rules, profile, **kw)
    return {"candidate": tag, "rules": rname, "risk_profile": profile["name"], **out,
            "pass_zero": z["pass_rate"], "ev_zero": z["ev_attempt"],
            "ev_vs_zero": out["ev_attempt"] - z["ev_attempt"]}


def stage3(run_dir, use_oos=False, only=None):
    R = Run(run_dir); sc = cfg("pipeline.yaml")["stage3_prop"]; top = cfg("pipeline.yaml")["stage2_costi"]["top_total"]
    s2 = pd.read_csv(R.path("stage2_costi.csv"))
    cand = s2[s2["pass"]].head(top) if only is None else s2[s2.apply(lambda r: vkey(r["strategy"], json.loads(r["params"])) in only, axis=1)]
    rules_all = cfg("prop_rules.yaml")
    profiles = build_profiles(cfg("risk_profiles.yaml"))
    days = R.days_oos if use_oos else R.days_is
    jobs = []
    for _, c in cand.iterrows():
        tr = R.load_trades(c["file_oos" if use_oos else "file_is"])
        dt = trades_by_day(tr, days)
        tag = vkey(c["strategy"], json.loads(c["params"]))
        for rn in sc["rules"]:
            for pf in profiles:
                jobs.append((dt, rules_all[rn], rn, pf, sc, tag))
    lab = "OOS" if use_oos else "IS"
    print(f"[fase3-{lab}] {len(cand)} candidati x {len(sc['rules'])} regole x {len(profiles)} profili rischio = {len(jobs)} combinazioni...")
    rows = _map(_prop_job, jobs, chunksize=8)
    # ordinati per la parte di EV dovuta al VANTAGGIO: l'EV grezzo premia il rischio alto anche a vantaggio zero
    res = pd.DataFrame(rows).sort_values(["ev_vs_zero", "pass_rate"], ascending=False)
    fn = R.path("stage3_prop_oos.csv" if use_oos else "stage3_prop.csv")
    res.to_csv(fn, index=False)
    best = res.sort_values("ev_vs_zero", ascending=False).groupby(["candidate", "rules"]).head(1)
    print(best[["candidate", "rules", "risk_profile", "pass_rate", "pass_zero", "fail_daily", "fail_max", "median_days",
                "ev_attempt", "ev_zero", "ev_vs_zero"]]
          .head(20).round(3).to_string(index=False))
    # confronto famiglie di rischio (media su candidati e regole)
    res["risk_family"] = res["risk_profile"].str.split("|").str[0]
    res["risk_pct"] = res["risk_profile"].str.split("|").str[1]
    sfx = "_oos" if use_oos else ""
    for metric, fn_m in [("pass_rate", "stage3_rischio_pivot"), ("fail_daily", "stage3_pivot_fail_daily"),
                         ("fail_max", "stage3_pivot_fail_max"), ("ev_attempt", "stage3_pivot_ev"),
                         ("ev_vs_zero", "stage3_pivot_ev_vs_zero")]:
        piv = res.pivot_table(index="risk_family", columns="risk_pct", values=metric, aggfunc="mean")
        piv = piv[sorted(piv.columns, key=lambda x: float(x.rstrip("%c")))]
        piv.to_csv(R.path(f"{fn_m}{sfx}.csv"))
        print(f"\n{metric} medio per modello di rischio x rischio base:\n" + piv.round(3).to_string())
    return res


# ---------------------------------------------------------------- FASE 4: conferma out-of-sample
def confirm(run_dir):
    R = Run(run_dir); m = R.meta; th = cfg("pipeline.yaml")["conferma_oos"]
    s2 = pd.read_csv(R.path("stage2_costi.csv")); s3 = pd.read_csv(R.path("stage3_prop.csv"))
    top = cfg("pipeline.yaml")["stage2_costi"]["top_total"]
    cand = s2[s2["pass"]].head(top)
    sr_trials = all_trial_sharpes(m["family"], m["symbol"], m["tf"])
    rows = []
    for _, c in cand.iterrows():
        key = vkey(c["strategy"], json.loads(c["params"]))
        oos = R.load_trades(c["file_oos"]); met_o = trade_metrics(oos, R.days_oos)
        dsr = deflated_sharpe(c["sharpe_d"], sr_trials, int(c["n_days"]), c["skew_d"], c["kurt_d"])
        rows.append({"candidate": key, "n_is": c["n"], "exp_is": c["expectancy"], "n_oos": met_o["n"],
                     "exp_oos": met_o["expectancy"], "pf_oos": met_o["pf"], "dd_oos_r": met_o["max_dd_r"],
                     "dsr_is": dsr, "trials": len(sr_trials)})
    res = pd.DataFrame(rows)
    res["verdetto"] = np.where((res["exp_oos"] > th["min_expectancy_r"]) & (res["dsr_is"] >= th["min_dsr"]), "PROMOSSA",
                       np.where(res["exp_oos"] > th["min_expectancy_r"], "DA_OSSERVARE", "SCARTATA"))
    res.to_csv(R.path("conferma_oos.csv"), index=False)
    print(res.round(3).to_string(index=False))
    # prop sul periodo OOS, solo per i profili migliori trovati in-sample (niente nuova ottimizzazione)
    best_prof = s3.sort_values("ev_vs_zero", ascending=False).groupby(["candidate", "rules"]).head(3)
    profiles = {p["name"]: p for p in build_profiles(cfg("risk_profiles.yaml"))}
    rules_all = cfg("prop_rules.yaml"); sc = cfg("pipeline.yaml")["stage3_prop"]
    jobs = []
    for _, b in best_prof.iterrows():
        c = cand[cand.apply(lambda r: vkey(r["strategy"], json.loads(r["params"])) == b["candidate"], axis=1)]
        if c.empty or b["risk_profile"] not in profiles:
            continue
        dt = trades_by_day(R.load_trades(c.iloc[0]["file_oos"]), R.days_oos)
        jobs.append((dt, rules_all[b["rules"]], b["rules"], profiles[b["risk_profile"]], sc, b["candidate"]))
    po = pd.DataFrame(_map(_prop_job, jobs))
    if not po.empty:
        po = po.merge(best_prof[["candidate", "rules", "risk_profile", "pass_rate", "ev_attempt", "ev_vs_zero"]]
                      .rename(columns={"pass_rate": "pass_rate_is", "ev_attempt": "ev_is", "ev_vs_zero": "ev_vs_zero_is"}),
                      on=["candidate", "rules", "risk_profile"])
        po.to_csv(R.path("conferma_prop_oos.csv"), index=False)
        print("\nProp su OOS (profili scelti in-sample):")
        print(po[["candidate", "rules", "risk_profile", "pass_rate_is", "pass_rate", "pass_zero", "ev_is", "ev_attempt",
                  "ev_vs_zero_is", "ev_vs_zero"]].round(3).to_string(index=False))
    write_report(R)
    return res


# ---------------------------------------------------------------- report
def write_report(R: Run):
    m = R.meta
    parts = [f"# Report {m['run_id']}", "",
             f"Simbolo **{m['symbol']}** {m['tf']} · dati {m['start']} → {m['end']} · IS fino a {m['cut_time']}", ""]
    def add(title, fn, cols=None, n=15):
        p = R.path(fn)
        if os.path.exists(p):
            d = pd.read_csv(p)
            if cols:
                d = d[[c for c in cols if c in d.columns]]
            try:
                tbl = d.head(n).round(3).to_markdown(index=False)
            except ImportError:
                tbl = "```\n" + d.head(n).round(3).to_string(index=False) + "\n```"
            parts.extend([f"## {title}", "", tbl, ""])
    add("Fase 1 · Famiglia (qualitativo, senza costi)", "stage1_famiglia.csv")
    add("Fase 2 · Con costi reali", "stage2_costi.csv", ["strategy", "params", "n", "exp_gross", "expectancy", "cost_share", "pf", "max_dd_r", "pass"])
    add("Fase 3 · Pass rate per modello di rischio (media)", "stage3_rischio_pivot.csv")
    add("Fase 3 · Fallimento per DAILY loss (media)", "stage3_pivot_fail_daily.csv")
    add("Fase 3 · Fallimento per MAX loss (media)", "stage3_pivot_fail_max.csv")
    add("Fase 3 · EV per tentativo (media, valuta conto)", "stage3_pivot_ev.csv")
    add("Fase 3 · EV dovuto al VANTAGGIO (EV meno lo stesso EV a vantaggio zero)", "stage3_pivot_ev_vs_zero.csv")
    add("Fase 3 · Migliori combinazioni prop (ordinate per ev_vs_zero)", "stage3_prop.csv",
        ["candidate", "rules", "risk_profile", "pass_rate", "pass_zero", "fail_daily", "fail_max", "median_days",
         "ev_attempt", "ev_zero", "ev_vs_zero"])
    add("Fase 4 · Conferma OOS", "conferma_oos.csv")
    add("Fase 4 · Prop su OOS (profili scelti in-sample, nessuna ri-ottimizzazione)", "conferma_prop_oos.csv",
        ["candidate", "rules", "risk_profile", "pass_rate_is", "pass_rate", "pass_zero", "fail_daily", "fail_max", "ev_is",
         "ev_attempt", "ev_vs_zero_is", "ev_vs_zero"])
    with open(R.path("report.md"), "w", encoding="utf-8") as f:   # "→" e "·" non esistono in cp1252
        f.write("\n".join(parts))
    print(f"[report] {R.path('report.md')}")
