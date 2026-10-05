"""A1, condizione di riapertura §7: il broker MT5 (FP Markets) ha gli strumenti che a Dukascopy mancano?

Il [referto del punto 2](../../docs/TREND_A1_HELDOUT_POWER.md) ha chiuso cosi': nel braccio ad
ALTA volatilita' ci sono **3,4** strumenti nuovi indipendenti, ne servono da **7,3** (effetto
osservato) a **29,3** (effetto dimezzato). La prima condizione di riapertura e' *"una fonte con
piu' classi ad alta volatilita' e storia lunga"* (riga G9 del backlog). Questo script fa lo
stesso inventario di `heldout_pool.py` sul feed del broker su cui opereremmo davvero.

Stesso metodo del referto, per restare confrontabile:
- finestra dal 2017-12-26, rendimenti log D1, volatilita' = sd * sqrt(252), soglia 20%;
- `n_eff = n / (1 + (n-1) * rho_medio)` dentro ogni classe, poi somma fra classi (GENEROSA);
- in piu', solo come indicatore: il rapporto di partecipazione degli autovalori
  `(sum lambda)^2 / sum lambda^2` = quante DIMENSIONI ha il pool. NON e' la numerosita'
  effettiva per la potenza: la varianza della media di un braccio dipende dalla formula sopra
  (con rho uniforme il rapporto da' ~9 dove la formula da' ~3). Corretto il 03/10.

Esclusi gli strumenti gia' usati nella scoperta (il feed Dukascopy D1 di `_coverage.csv`):
petrolio, gas, rame, platino, palladio, oro, argento, cacao, caffe', cotone, zucchero, BTC,
ETH, US500, US100.

Controlli sui dati PRIMA dei numeri: storia sufficiente (inizio entro il 2018-03-01) e
**split non rettificati** — un CFD azionario che non rettifica lo split mostra un rendimento
giornaliero di -50%/-75% che non e' mai avvenuto, gonfia la volatilita' e inventa un trend.

Costo: **0 trial** — nessuna regola, nessun parametro, nessun esito di strategia.

    python analysis/trend/heldout_pool_mt5.py --scarica     # terminale MT5 aperto; riprende
    python analysis/trend/heldout_pool_mt5.py               # solo l'inventario
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DIR = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "mt5_fp_d1")

T0 = pd.Timestamp("2017-12-26")         # stessa finestra W2 del referto
INIZIO_MAX = pd.Timestamp("2018-03-01")  # storia "piena": parte entro questa data
SOGLIA_VOL = 0.20
SPLIT = np.log(0.6)                      # un giorno sotto -40% su un CFD azionario e' sospetto

#: Fabbisogno per braccio da `power_two_groups.py` (referto §3).
FABBISOGNO = (("durata appaiata, effetto osservato", 7.3),
              ("durata fissa 20g, effetto osservato", 16.7),
              ("durata appaiata, effetto dimezzato", 29.3),
              ("durata fissa 20g, effetto dimezzato", 66.8))

IN_SAMPLE = {"BRENT", "WTI", "XBRUSD", "XTIUSD", "XNGUSD", "COCOA", "COFFEE", "COTTON",
             "SUGAR", "XCUUSD.r", "XPTUSD", "XPDUSD", "BTCUSD", "ETHUSD", "US500", "US100"}
CARTELLE = ("Commodities", "Soft Commodities", "Metals Raw", "Crypto Currency",
            "Equity CFD", "Indices", "Palladium", "Platinum")


def classe(path: str) -> str:
    top = path.split("\\")[0]
    return {"Soft Commodities": "agri", "Metals Raw": "metalli_ind",
            "Crypto Currency": "crypto", "Indices": "indici", "Commodities": "energia",
            "Equity CFD US": "azioni_US", "Equity CFD EU": "azioni_EU",
            "Equity CFD UK": "azioni_UK"}.get(top, top)


def scarica() -> int:
    import MetaTrader5 as mt5
    if not mt5.initialize():
        print("initialize() fallito:", mt5.last_error())
        return 1
    os.makedirs(DIR, exist_ok=True)
    righe = []
    for s in mt5.symbols_get():
        if not s.path.startswith(CARTELLE) or s.name in IN_SAMPLE:
            continue
        if s.name.startswith(("XAU", "XAG")):
            continue
        righe.append((s.name, classe(s.path), s.trade_mode))
        out = os.path.join(DIR, s.name + "_D1.csv")
        if os.path.exists(out):
            continue
        mt5.symbol_select(s.name, True)
        r = mt5.copy_rates_from_pos(s.name, mt5.TIMEFRAME_D1, 0, 5000)
        if r is None or len(r) == 0:
            continue
        d = pd.DataFrame(r)
        d["time"] = pd.to_datetime(d["time"], unit="s")
        d[["time", "open", "high", "low", "close", "tick_volume"]].to_csv(out, index=False)
    mt5.shutdown()
    pd.DataFrame(righe, columns=["sym", "classe", "trade_mode"]).to_csv(
        os.path.join(DIR, "_simboli.csv"), index=False)
    print("simboli candidati: %d, file presenti: %d"
          % (len(righe), sum(os.path.exists(os.path.join(DIR, r[0] + "_D1.csv")) for r in righe)))
    return 0


def n_eff(n, rho):
    if n <= 1 or not np.isfinite(rho):
        return float(n)
    return n / (1.0 + (n - 1) * max(rho, 0.0))


def partecipazione(R: pd.DataFrame) -> float:
    """Numero effettivo di dimensioni indipendenti: (sum l)^2 / sum l^2 sugli autovalori."""
    c = R.corr(min_periods=250).fillna(0.0).to_numpy().copy()
    np.fill_diagonal(c, 1.0)
    lam = np.clip(np.linalg.eigvalsh(c), 0, None)
    return float(lam.sum() ** 2 / (lam ** 2).sum())


def inventario() -> int:
    sim = pd.read_csv(os.path.join(DIR, "_simboli.csv"))
    print("=" * 92)
    print("A1 §7 - POOL HELD-OUT SUL BROKER MT5 (FP Markets): finestra %s+, soglia %.0f%%"
          % (T0.date(), 100 * SOGLIA_VOL))
    print("=" * 92)

    rend, info = {}, []
    for _, r in sim.iterrows():
        p = os.path.join(DIR, r.sym + "_D1.csv")
        if not os.path.exists(p):
            info.append((r.sym, r.classe, "manca", None, 0, np.nan, 0))
            continue
        d = pd.read_csv(p, parse_dates=["time"]).sort_values("time")
        inizio = d.time.iloc[0]
        x = np.log(d.close.where(d.close > 0)).diff()
        x.index = d.time
        x = x[x.index >= T0].dropna()
        split = int((x < SPLIT).sum()) if r.classe.startswith("azioni") else 0
        stato = "piena" if inizio <= INIZIO_MAX else "corta"
        vol = float(x.std(ddof=1) * np.sqrt(252)) if len(x) > 200 else np.nan
        info.append((r.sym, r.classe, stato, inizio, len(x), vol, split))
        if stato == "piena" and split == 0 and np.isfinite(vol):
            rend[r.sym] = x
    T = pd.DataFrame(info, columns=["sym", "classe", "stato", "inizio", "barre", "vol", "split"])

    print("\n--- 1. controlli sui dati, per classe")
    print("  %-12s %6s %6s %6s %8s %10s %14s" % ("classe", "totale", "manca", "corta",
                                                "piena", "con split", "inizio mediano"))
    for c, g in T.groupby("classe"):
        print("  %-12s %6d %6d %6d %8d %10d %14s"
              % (c, len(g), (g.stato == "manca").sum(), (g.stato == "corta").sum(),
                 (g.stato == "piena").sum(), (g.split > 0).sum(),
                 str(pd.to_datetime(g.inizio).median())[:10]))
    sp = T[T.split > 0].sort_values("split", ascending=False)
    if len(sp):
        print("  split sospetti (giorno < -40%%), esclusi: %s" % ", ".join(
            "%s(%d)" % (s, n) for s, n in zip(sp.sym.head(15), sp.split.head(15))))

    ok = T[T.sym.isin(rend)]
    alta = ok[ok.vol >= SOGLIA_VOL]
    print("\n--- 2. braccio ALTA volatilita' (storia piena, nessuno split): per classe")
    print("  %-12s %5s %9s %9s %8s %10s" % ("classe", "n", "vol med.", "rho medio",
                                           "n_eff", "vol min"))
    somma = 0.0
    for c, g in alta.groupby("classe"):
        R = pd.DataFrame({s: rend[s] for s in g.sym})
        cc = R.corr(min_periods=250).to_numpy()
        rho = float(np.nanmean(cc[np.triu_indices(len(g), 1)])) if len(g) > 1 else np.nan
        ne = n_eff(len(g), rho)
        somma += ne
        print("  %-12s %5d %8.1f%% %+9.3f %8.2f %9.1f%%"
              % (c, len(g), 100 * g.vol.median(), rho, ne, 100 * g.vol.min()))
    pr = partecipazione(pd.DataFrame({s: rend[s] for s in alta.sym})) if len(alta) > 1 else 0
    print("  somma per classe (GENEROSA, come il referto): %.1f" % somma)
    print("  dimensioni del pool (rapporto di partecipazione, NON e' n_eff per la potenza): %.1f"
          % pr)
    senza_az = alta[~alta.classe.str.startswith("azioni")]
    pr_na = (partecipazione(pd.DataFrame({s: rend[s] for s in senza_az.sym}))
             if len(senza_az) > 1 else float(len(senza_az)))
    print("  di cui SENZA azioni (solo commodity, crypto, indici): %.1f" % pr_na)

    bassa = ok[ok.vol < SOGLIA_VOL]
    print("\n  braccio bassa: %d strumenti nuovi con storia piena (non e' il vincolo: referto §5)"
          % len(bassa))

    print("\n--- 3. confronto col fabbisogno (referto §3) - Dukascopy ne aveva 3,4")
    print("  %-38s %8s %10s %10s" % ("scenario", "servono", "formula", "dimensioni"))
    for eti, serve in FABBISOGNO:
        def esito(x):
            if x <= 0:
                return "vuoto"
            return "OK" if x >= serve else "x%.1f" % (serve / x)
        print("  %-38s %8.1f %5.1f %-4s %5.1f %-4s"
              % (eti, serve, somma, esito(somma), pr, esito(pr)))
    return 0


DIR_DK = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1",
                      "_pool_azioni_us")


def azioni_dukascopy(scarica_dati: bool) -> int:
    """Il server FP Markets conserva poca storia (azioni da 2024-08, verificato il 03/10):
    la STORIA delle azioni USA si prende da Dukascopy (630 titoli, molti dal 2017-03), e si
    tengono solo quelli che FP Markets offre davvero, cioe' su cui si potrebbe operare."""
    sim = pd.read_csv(os.path.join(DIR, "_simboli.csv"))
    fp = sorted({s.split(".")[0].upper() for s in sim[sim.classe == "azioni_US"].sym})
    os.makedirs(DIR_DK, exist_ok=True)
    if scarica_dati:
        import datetime as dt
        from datetime import timezone
        import dukascopy_python as dk
        import dukascopy_python.instruments as ins
        for t in fp:
            out = os.path.join(DIR_DK, t + "_D1.csv")
            code = getattr(ins, "INSTRUMENT_US_%s_US_USD" % t, None)
            if os.path.exists(out) or code is None:
                continue
            try:
                d = dk.fetch(code, dk.INTERVAL_DAY_1, dk.OFFER_SIDE_BID,
                             dt.datetime(2012, 1, 1, tzinfo=timezone.utc),
                             dt.datetime.now(timezone.utc))
            except Exception as e:                       # rete: si riprende al prossimo giro
                print("  %-6s errore %s" % (t, type(e).__name__))
                continue
            if d is not None and len(d):
                d.to_csv(out)

    print("\n" + "=" * 92)
    print("4. AZIONI USA - storia Dukascopy, operabilita' FP Markets")
    print("=" * 92)
    rend, info = {}, []
    for t in fp:
        p = os.path.join(DIR_DK, t + "_D1.csv")
        if not os.path.exists(p):
            info.append((t, "assente su Dukascopy", np.nan, 0))
            continue
        d = pd.read_csv(p)
        tcol = next(c for c in d.columns if c.lower() in ("timestamp", "time", "date"))
        d["t"] = pd.to_datetime(d[tcol], utc=True, format="mixed").dt.tz_localize(None)
        d = d.sort_values("t")
        x = np.log(d.close.where(d.close > 0)).diff()
        x.index = d.t
        x = x[x.index >= T0].dropna()
        split = int((x < SPLIT).sum())
        if d.t.iloc[0] > INIZIO_MAX:
            info.append((t, "corta", np.nan, split))
            continue
        vol = float(x.std(ddof=1) * np.sqrt(252))
        info.append((t, "piena", vol, split))
        if split == 0:
            rend[t] = x
    T = pd.DataFrame(info, columns=["sym", "stato", "vol", "split"])
    print("  titoli FP Markets USA: %d | assenti su Dukascopy: %d | storia corta: %d | "
          "storia piena: %d (di cui con split sospetti, esclusi: %d)"
          % (len(T), (T.stato == "assente su Dukascopy").sum(), (T.stato == "corta").sum(),
             (T.stato == "piena").sum(), ((T.stato == "piena") & (T.split > 0)).sum()))
    ok = T[T.sym.isin(rend)]
    alta = ok[ok.vol >= SOGLIA_VOL]
    print("  sopra il %.0f%% di volatilita': %d su %d (vol mediana %.1f%%)"
          % (100 * SOGLIA_VOL, len(alta), len(ok), 100 * ok.vol.median()))
    if len(alta) < 2:
        return 0
    R = pd.DataFrame({s: rend[s] for s in alta.sym})
    cc = R.corr(min_periods=250).to_numpy()
    rho = float(np.nanmean(cc[np.triu_indices(len(alta), 1)]))
    ne = n_eff(len(alta), rho)
    pr = partecipazione(R)
    print("  rho medio %+.3f -> n_eff (formula del referto) %.1f | tetto teorico 1/rho = %.1f"
          % (rho, ne, 1 / rho if rho > 0 else np.inf))
    print("  dimensioni del pool (rapporto di partecipazione, NON e' n_eff per la potenza): %.1f" % pr)
    # con le crypto del referto (1,40), sommate come se fossero indipendenti: GENEROSO
    for eti, base in (("azioni da sole (formula)", ne), ("azioni + crypto 1,40 + agri/energia 2,0", ne + 3.4)):
        print("  %-42s %5.1f  ->  %s" % (eti, base, ", ".join(
            "%s %s" % (str(serve), "OK" if base >= serve else "x%.1f" % (serve / base))
            for _, serve in FABBISOGNO)))
    # per settore: la correlazione dentro il braccio non e' uniforme
    top = alta.sort_values("vol", ascending=False).head(12)
    print("  i piu' volatili: %s" % ", ".join("%s %.0f%%" % (s, 100 * v)
                                             for s, v in zip(top.sym, top.vol)))
    return 0


DIR_PST = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "pysystemtrade")
PST = "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/"

#: Futures continui di pysystemtrade (gratis, fermi al 2024) che NON sono gia' in-sample
#: (petrolio, gas USA, rame, oro, argento, platino, palladio, cacao, caffe' arabica, cotone,
#: zucchero 11, soia, BTC, ETH), ne' FX, bond, tassi o indici azionari. Un contratto per
#: sottostante: mini e micro duplicano lo stesso rischio. Raggruppati per classe economica.
FUTURES = {
    "metalli_ind": ["ALUMINIUM_LME", "NICKEL_LME", "ZINC_LME", "LEAD_LME", "TIN_LME",
                    "IRON", "STEEL"],
    "energia": ["GASOIL", "HEATOIL", "GASOILINE", "ETHANOL", "COAL", "EUA"],
    "cereali": ["CORN", "WHEAT", "REDWHEAT", "MILLWHEAT", "OAT", "RICE", "SOYMEAL",
                "SOYOIL", "CANOLA"],
    "soft": ["ROBUSTA", "OJ", "RUBBER", "LUMBER-new"],
    "zootecnia": ["LEANHOG", "LIVECOW", "FEEDCOW", "MILK", "CHEESE", "BUTTER", "WHEY"],
}


def futures_pysystemtrade(scarica_dati: bool) -> int:
    """La prima condizione §7 del referto, contata GRATIS prima di comprare Pinnacle/Norgate."""
    import urllib.request
    os.makedirs(DIR_PST, exist_ok=True)
    if scarica_dati:
        for nomi in FUTURES.values():
            for n in nomi:
                for tipo in ("adjusted_prices_csv", "multiple_prices_csv"):
                    out = os.path.join(DIR_PST, "%s__%s.csv" % (n, tipo.split("_")[0]))
                    if os.path.exists(out):
                        continue
                    try:
                        urllib.request.urlretrieve(PST + "%s/%s.csv" % (tipo, n), out)
                    except Exception as e:
                        print("  %-14s %s: %s" % (n, tipo, type(e).__name__))

    print("\n" + "=" * 92)
    print("5. FUTURES pysystemtrade (gratis, non in-sample) - la riga G9 contata prima di comprare")
    print("=" * 92)
    rend, righe = {}, []
    for classe_, nomi in FUTURES.items():
        for n in nomi:
            pa = os.path.join(DIR_PST, n + "__adjusted.csv")
            pm = os.path.join(DIR_PST, n + "__multiple.csv")
            if not (os.path.exists(pa) and os.path.exists(pm)):
                righe.append((n, classe_, "manca", None, None, np.nan))
                continue
            a = pd.read_csv(pa, parse_dates=["DATETIME"]).set_index("DATETIME")["price"]
            m = pd.read_csv(pm, parse_dates=["DATETIME"]).set_index("DATETIME")["PRICE"]
            a = a.groupby(a.index.normalize()).last()
            m = m.groupby(m.index.normalize()).last().reindex(a.index).ffill()
            r = (a.diff() / m.shift(1)).replace([np.inf, -np.inf], np.nan)
            r = r[r.index >= T0].dropna()
            inizio, fine = a.index.min(), a.index.max()
            if inizio > INIZIO_MAX or len(r) < 500:
                righe.append((n, classe_, "corta", inizio, fine, np.nan))
                continue
            vol = float(r.std(ddof=1) * np.sqrt(252))
            righe.append((n, classe_, "piena", inizio, fine, vol))
            rend[n] = r
    T = pd.DataFrame(righe, columns=["sym", "classe", "stato", "inizio", "fine", "vol"])
    print("  %-14s %-11s %6s %11s %11s %8s" % ("futures", "classe", "stato", "da", "a", "vol"))
    for _, x in T.iterrows():
        print("  %-14s %-11s %6s %11s %11s %7s"
              % (x.sym, x.classe, x.stato, str(x.inizio)[:10], str(x.fine)[:10],
                 "" if not np.isfinite(x.vol) else "%.0f%%" % (100 * x.vol)))
    alta = T[(T.stato == "piena") & (T.vol >= SOGLIA_VOL)]
    print("\n  braccio ALTA: %d futures sopra il %.0f%%" % (len(alta), 100 * SOGLIA_VOL))
    print("  %-12s %4s %10s %8s" % ("classe", "n", "rho medio", "n_eff"))
    somma = 0.0
    for c, g in alta.groupby("classe"):
        R = pd.DataFrame({s: rend[s] for s in g.sym})
        cc = R.corr(min_periods=250).to_numpy()
        rho = float(np.nanmean(cc[np.triu_indices(len(g), 1)])) if len(g) > 1 else np.nan
        ne = n_eff(len(g), rho)
        somma += ne
        print("  %-12s %4d %+10.3f %8.2f" % (c, len(g), rho, ne))
    R = pd.DataFrame({s: rend[s] for s in alta.sym})
    cc = R.corr(min_periods=250).to_numpy()
    rho_tot = float(np.nanmean(cc[np.triu_indices(len(alta), 1)]))
    ne_tot = n_eff(len(alta), rho_tot)
    print("  somma per classe (GENEROSA): %.1f | tutto insieme con rho medio %+.3f: %.1f"
          % (somma, rho_tot, ne_tot))
    for eti, base in (("futures da soli, tutto insieme", ne_tot),
                      ("futures (somma) + crypto 1,40 del referto", somma + 1.4)):
        print("  %-42s %5.1f  ->  %s" % (eti, base, ", ".join(
            "%s %s" % (serve, "OK" if base >= serve else "x%.1f" % (serve / base))
            for _, serve in FABBISOGNO)))
    print("  fine dati: %s (pysystemtrade non aggiorna il CSV pubblico: per un TEST serve il feed"
          " a pagamento)" % str(T.fine.dropna().max())[:10])
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scarica", action="store_true", help="scarica i D1 dal terminale MT5")
    ap.add_argument("--azioni", action="store_true",
                    help="azioni USA: storia da Dukascopy (con --scarica la scarica)")
    ap.add_argument("--futures", action="store_true",
                    help="futures pysystemtrade gratis (con --scarica li scarica)")
    a = ap.parse_args(argv)
    if a.futures:
        return futures_pysystemtrade(a.scarica)
    if a.scarica and not a.azioni:
        rc = scarica()
        if rc:
            return rc
    rc = inventario()
    if a.azioni:
        rc = azioni_dukascopy(a.scarica) or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
