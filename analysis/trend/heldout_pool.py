"""A1 punto 2, seconda meta': gli strumenti che servono ESISTONO e sono INDIPENDENTI?

`power_two_groups.py` dice quanti strumenti servono per braccio. Questo dice quanti ce ne sono
davvero — e la risposta non e' il conteggio dei ticker, perche' strumenti correlati fra loro non
portano informazione separata:

    n_eff = n / (1 + (n - 1) * rho_medio)

Scarica un CAMPIONE del pool ancora libero, ne misura volatilita' realizzata e correlazione
reciproca, e confronta la capacita' effettiva dei due bracci con il fabbisogno. Le correlazioni
sono **misurate**, non assunte.

Non consuma trial: nessuna regola, nessun parametro, nessun esito. E' l'inventario che deve
precedere una pre-registrazione (regola nata dal FADE: il "secondo test" era fuori scala di 40x,
e nessuno lo aveva calcolato prima).

    python analysis/trend/heldout_pool.py
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from datetime import timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

DK = os.path.join(ROOT, "analysis", "trading-bot-eval", "data", "dukascopy_d1")
CACHE = os.path.join(DK, "_pool_candidati")
T0 = pd.Timestamp("2017-12-26")        # inizio della finestra comune W2
SOGLIA_VOL = 0.20

#: Campione del pool LIBERO, scelto per coprire i due bracci. I nomi vengono risolti a
#: runtime: se la libreria non espone un codice, lo strumento viene saltato e dichiarato.
CANDIDATI = [
    # --- lato ALTA volatilita': crypto (il grosso del pool libero) ---
    ("LTCUSD", "VCCY_LTC_USD"), ("XRPUSD", "VCCY_XRP_USD"), ("BCHUSD", "VCCY_BCH_USD"),
    ("ADAUSD", "VCCY_ADA_USD"), ("EOSUSD", "VCCY_EOS_USD"), ("XMRUSD", "VCCY_XMR_USD"),
    # --- lato ALTA volatilita': gli unici non-crypto rimasti ---
    ("OJUICE", "CMD_AGRICULTURAL_OJUICE_CMD_USX"), ("DIESEL", "CMD_ENERGY_DIESEL_CMD_USD"),
    # --- indici liberi: verifica se popolano davvero il braccio ALTA ---
    ("DAX", "IDX_EUROPE_E_DAAX"), ("N225", "IDX_ASIA_E_N225JAP"),
    ("DJIND", "IDX_AMERICA_E_D_J_IND"),
    # --- lato BASSA volatilita': cross FX, incluse le EM (le piu' volatili del gruppo) ---
    ("EURCHF", "FX_CROSSES_EUR_CHF"), ("AUDJPY", "FX_CROSSES_AUD_JPY"),
    ("EURAUD", "FX_CROSSES_EUR_AUD"), ("CADJPY", "FX_CROSSES_CAD_JPY"),
    ("USDNOK", "FX_CROSSES_USD_NOK"), ("USDZAR", "FX_CROSSES_USD_ZAR"),
    ("USDMXN", "FX_CROSSES_USD_MXN"), ("NZDCAD", "FX_CROSSES_NZD_CAD"),
]

#: Gia' nel feed: servono da ancoraggio per misurare la correlazione dentro ogni insieme.
ANCORE = ["BTCUSD", "ETHUSD", "EURJPY", "GBPJPY", "EURGBP", "SPX500", "NAS100",
          "BRENT", "WTI", "NATGAS", "COCOA", "COFFEE", "COTTON", "SOYBEAN", "SUGAR"]

#: Quanti ticker restano liberi per categoria (dalla libreria dukascopy_python).
LIBERI = {"crypto": 19, "index": 20, "fx_cross": 58, "agri": 1, "energy": 1,
          "fx_major": 0, "bond": 0, "metal": 0}


def scarica(nome, suffisso):
    """Scarica se manca, altrimenti usa la copia in cache. Ritorna il percorso o None."""
    out = os.path.join(CACHE, nome + "_D1.csv")
    if os.path.exists(out):
        return out
    try:
        import dukascopy_python as dk
        import dukascopy_python.instruments as ins
    except Exception as e:
        print("  libreria dukascopy_python non disponibile: %s" % e)
        return None
    code = getattr(ins, "INSTRUMENT_" + suffisso, None)
    if code is None:
        print("  %-8s codice non esposto dalla libreria" % nome)
        return None
    try:
        d = dk.fetch(code, dk.INTERVAL_DAY_1, dk.OFFER_SIDE_BID,
                     dt.datetime(2012, 1, 1, tzinfo=timezone.utc),
                     dt.datetime.now(timezone.utc))
    except Exception as e:
        print("  %-8s errore di rete: %s" % (nome, type(e).__name__))
        return None
    if d is None or len(d) == 0:
        print("  %-8s NESSUN DATO su Dukascopy" % nome)
        return None
    os.makedirs(CACHE, exist_ok=True)
    d.to_csv(out)
    return out


def rendimenti(percorso, col_tempo=None):
    d = pd.read_csv(percorso)
    if col_tempo is None:
        col_tempo = next(c for c in d.columns
                         if c.lower() in ("timestamp", "time", "date", "index"))
    t = pd.to_datetime(d[col_tempo], utc=True, format="mixed").dt.tz_localize(None)
    m = t >= T0
    return pd.Series(np.log(d.loc[m, "close"].to_numpy(float)),
                     index=pd.DatetimeIndex(t[m])).diff()


def n_eff(n, rho):
    if n <= 1 or not np.isfinite(rho):
        return float(n)
    return n / (1.0 + (n - 1) * max(rho, 0.0))


def rho_medio(serie: dict, syms):
    syms = [s for s in syms if s in serie]
    if len(syms) < 2:
        return float("nan"), len(syms)
    R = pd.DataFrame({s: serie[s] for s in syms}).dropna(how="all")
    c = R.corr().to_numpy()
    iu = np.triu_indices(len(syms), 1)
    return float(np.nanmean(c[iu])), len(syms)


def main() -> int:
    print("=" * 88)
    print("A1 PUNTO 2 (b) - il pool held-out esiste? e quanto e' INDIPENDENTE?")
    print("finestra di misura: %s+   soglia di braccio: vol >= %.0f%%"
          % (T0.date(), 100 * SOGLIA_VOL))
    print("=" * 88)

    serie, mancanti = {}, []
    print("\n--- disponibilita' effettiva su Dukascopy (scaricati o in cache)")
    for nome, suff in CANDIDATI:
        p = scarica(nome, suff)
        if p is None:
            mancanti.append(nome)
            continue
        serie[nome] = rendimenti(p)
    for sym in ANCORE:
        p = os.path.join(DK, sym + "_D1.csv")
        if os.path.exists(p):
            serie[sym] = rendimenti(p, col_tempo="time")

    nuovi = [n for n, _ in CANDIDATI if n in serie]
    print("  candidati verificati: %d su %d" % (len(nuovi), len(CANDIDATI)))
    if mancanti:
        print("  NON disponibili: %s" % ", ".join(mancanti))

    print("\n--- volatilita' annualizzata: chi finisce davvero nel braccio ALTA")
    print("  %-8s %9s %8s %8s  %s" % ("strum.", "vol ann.", "barre", "da", "braccio"))
    vols = {}
    for k in sorted(serie, key=lambda x: -float(np.nanstd(serie[x].to_numpy(), ddof=1))):
        s = serie[k].dropna()
        if len(s) < 200:
            continue
        v = float(s.std(ddof=1) * np.sqrt(252))
        vols[k] = v
        print("  %-8s %8.1f%% %8d %8s  %-5s%s"
              % (k, 100 * v, len(s), str(s.index.min())[:7],
                 "ALTA" if v >= SOGLIA_VOL else "bassa",
                 "   <- NUOVO" if k in nuovi else ""))

    print("\n--- correlazione MISURATA dentro ogni insieme (rendimenti D1)")
    insiemi = {
        "crypto": ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "BCHUSD", "ADAUSD", "EOSUSD"],
        "index": ["SPX500", "NAS100", "DAX", "N225", "DJIND"],
        "fx_cross": ["EURJPY", "GBPJPY", "EURGBP", "EURCHF", "AUDJPY", "EURAUD",
                     "CADJPY", "USDNOK", "USDZAR", "USDMXN", "NZDCAD"],
        "energy": ["BRENT", "WTI", "NATGAS", "DIESEL"],
        "agri": ["COCOA", "COFFEE", "COTTON", "SOYBEAN", "SUGAR", "OJUICE"],
    }
    print("  %-10s %4s %10s %8s %9s %10s" % ("insieme", "n misur.", "rho medio",
                                             "n_eff", "liberi", "n_eff liberi"))
    capacita = {}
    for g, syms in insiemi.items():
        r, n = rho_medio(serie, syms)
        ne = n_eff(n, r)
        lib = LIBERI.get(g, 0)
        # I vecchi strumenti sono IN-SAMPLE e non si possono riusare in un held-out:
        # la capacita' che conta e' quella dei soli LIBERI, in piedi da soli.
        ne_lib = n_eff(lib, r) if lib > 0 else 0.0
        capacita[g] = ne_lib
        print("  %-10s %4d %+10.3f %8.2f %8d %10.2f" % (g, n, r, ne, lib, ne_lib))

    print("\n--- capacita' EFFETTIVA dei due bracci (solo strumenti nuovi)")
    alta = capacita.get("crypto", 0) + capacita.get("agri", 0) + capacita.get("energy", 0)
    bassa = capacita.get("fx_cross", 0)
    idx_alta = sum(1 for k in ("DAX", "N225", "DJIND", "SPX500", "NAS100")
                   if vols.get(k, 0) >= SOGLIA_VOL)
    print("  braccio ALTA  vol: %.1f strumenti indipendenti nuovi" % alta)
    print("    (crypto %.2f + agri %.2f + energia %.2f)"
          % (capacita.get("crypto", 0), capacita.get("agri", 0), capacita.get("energy", 0)))
    print("    gli indici NON lo popolano: solo %d su 5 misurati sta sopra il %.0f%%"
          % (idx_alta, 100 * SOGLIA_VOL))
    bassa_tot = bassa + capacita.get("index", 0)
    print("  braccio BASSA vol: %.1f strumenti indipendenti nuovi "
          "(%.1f cross FX + %.1f indici)" % (bassa_tot, bassa, capacita.get("index", 0)))
    print()
    print("  Nota: si sommano categorie diverse come se fossero fra loro indipendenti,")
    print("  e si ignora la correlazione incrociata. E' una stima GENEROSA: la capacita'")
    print("  vera e' piu' bassa di cosi'.")

    print("\n--- confronto col fabbisogno di power_two_groups.py")
    print("  %-38s %9s %9s %s" % ("scenario", "servono", "ALTA ha", "esito"))
    for eti, serve in (("durata appaiata, effetto osservato", 7.3),
                       ("durata fissa 20g, effetto osservato", 16.7),
                       ("durata appaiata, effetto dimezzato", 29.3),
                       ("durata fissa 20g, effetto dimezzato", 66.8)):
        ok = "OK" if alta >= serve else "FUORI SCALA %.1fx" % (serve / max(alta, 1e-9))
        print("  %-38s %9.1f %9.1f %s" % (eti, serve, alta, ok))
    print("\n  Il vincolo NON e' il numero di ticker (Dukascopy ne ha a sufficienza):")
    print("  e' che l'estremo ALTO della volatilita' e' UNA classe di attivi sola.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
