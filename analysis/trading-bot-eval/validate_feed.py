"""VALIDAZIONE FEED (Fase 0) — i dati del broker demo sono usabili?

Due controlli, entrambi decisivi PRIMA di fidarci dei dati:

  A) GAP: per i simboli flaggati ⚠️ stampa le DATE reali dei buchi > 3 giorni.
     Se cadono su festivita' (fine anno, Thanksgiving, Pasqua) = benigni (mercato chiuso),
     non buchi di feed. Cosi' distinguiamo "storia bucata" da "calendario".

  B) FEED: confronta gli ultimi ~15 close giornalieri del broker vs un riferimento
     pubblico (yfinance) per FX/oro/BTC/ETH/indici. Deviazione piccola (pochi decimi di %)
     = stesso mercato, feed valido. Deviazione grande/sistematica = sintetico sbagliato
     (la lezione GC=F: $11-25 fuori). Le differenze attese vengono dal fuso dell'ora di
     chiusura del daily, non da un feed sbagliato.

Uso: python analysis/trading-bot-eval/validate_feed.py   (serve internet per yfinance)
"""
from __future__ import annotations

import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
DATA = "analysis/trading-bot-eval/data"

# simboli flaggati per il controllo gap
GAP_SYMS = ["EURUSD", "USDCHF", "XAUUSD", "XAGUSD", "BTCUSD", "US500", "US100"]

# broker_prefix -> lista di ticker yfinance candidati (primo che risponde vince)
REF = {
    "EURUSD": ["EURUSD=X"],
    "GBPUSD": ["GBPUSD=X"],
    "USDJPY": ["USDJPY=X"],
    "XAUUSD": ["XAUUSD=X", "GC=F"],   # oro spot; fallback futures (aspettati piccola base)
    "BTCUSD": ["BTC-USD"],
    "ETHUSD": ["ETH-USD"],
    "US500": ["^GSPC"],
    "US100": ["^NDX"],
}


def load_d1(prefix):
    df = pd.read_csv(f"{DATA}/{prefix}_D1.csv", parse_dates=["time"]).set_index("time")
    df.index = df.index.normalize()
    return df


def load_h1(prefix):
    return pd.read_csv(f"{DATA}/{prefix}_H1.csv", parse_dates=["time"]).set_index("time")


def gap_check():
    print("=" * 70)
    print("A) GAP > 3 GIORNI — sono festivita' o buchi di feed?")
    print("=" * 70)
    for sym in GAP_SYMS:
        try:
            df = load_h1(sym)
        except FileNotFoundError:
            print(f"\n{sym}: file mancante"); continue
        diffs = df.index.to_series().diff()
        gaps = diffs[diffs > pd.Timedelta(days=3)]
        print(f"\n{sym}  ({len(gaps)} buchi > 3g):")
        for t, d in gaps.items():
            prev = t - d
            print(f"   {prev.date()} -> {t.date()}   ({d.total_seconds()/3600:.0f}h, ~{d.days}g)")


def _last_common(broker, ref, n=15):
    """Ultime n date comuni; ritorna DataFrame con close broker vs ref e %dev."""
    j = pd.DataFrame({"broker": broker["close"], "ref": ref}).dropna()
    j = j.tail(n)
    j["dev_pct"] = (j["broker"] - j["ref"]) / j["ref"] * 100
    return j


def feed_check():
    import yfinance as yf
    print("\n" + "=" * 70)
    print("B) FEED broker vs riferimento pubblico (yfinance) — ultimi ~15 daily")
    print("=" * 70)
    summary = []
    for prefix, tickers in REF.items():
        try:
            bro = load_d1(prefix)
        except FileNotFoundError:
            print(f"\n{prefix}: file broker mancante"); continue
        ref_ser, used = None, None
        for tk in tickers:
            try:
                raw = yf.download(tk, period="60d", interval="1d",
                                  progress=False, auto_adjust=False)
                if raw is not None and len(raw) > 5:
                    s = raw["Close"]
                    if isinstance(s, pd.DataFrame):
                        s = s.iloc[:, 0]
                    s.index = pd.to_datetime(s.index).normalize()
                    ref_ser, used = s, tk
                    break
            except Exception as e:  # noqa: BLE001
                print(f"   ({prefix}: {tk} fallito: {e})")
        if ref_ser is None:
            print(f"\n{prefix}: nessun riferimento yfinance disponibile"); continue
        j = _last_common(bro, ref_ser, n=15)
        if j.empty:
            print(f"\n{prefix} vs {used}: nessuna data comune"); continue
        md = j["dev_pct"].abs().median()
        mx = j["dev_pct"].abs().max()
        me = j["dev_pct"].mean()
        note = "OK" if md < 0.35 else ("BASE futures?" if used.endswith("=F") else "⚠️ CONTROLLA")
        summary.append((prefix, used, md, mx, me, note))
        print(f"\n{prefix} vs {used}   (ultime {len(j)} date comuni)")
        print(f"   ultimo: broker={j['broker'].iloc[-1]:.5g}  ref={j['ref'].iloc[-1]:.5g}"
              f"  dev={j['dev_pct'].iloc[-1]:+.3f}%")
        print(f"   |dev| mediana={md:.3f}%  max={mx:.3f}%  bias medio={me:+.3f}%  -> {note}")

    print("\n" + "-" * 70)
    print(f"{'simbolo':9} {'ref':10} {'|dev|med%':>9} {'|dev|max%':>9} {'bias%':>8}  esito")
    for prefix, used, md, mx, me, note in summary:
        print(f"{prefix:9} {used:10} {md:9.3f} {mx:9.3f} {me:+8.3f}  {note}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass
    gap_check()
    feed_check()
    print("\nNOTE: FX/indici, piccola dev attesa dal fuso dell'ora di chiusura del daily.")
    print("Oro su GC=F = base spot-vs-futures (pochi $), non errore di feed.")


if __name__ == "__main__":
    main()
