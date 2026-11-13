"""Esporta dal terminale MT5 aperto (FP Markets) le barre a 5 minuti del paniere della famiglia `volatilita`. 0 trial.

Secondo feed, non la serie di lavoro: MT5 ha solo ~17 mesi di M5 sugli indici (da giugno 2025, verificato l'11/11),
non copre l'holdout di due anni. Serve a confrontare la volatilita' del CFD del broker, quello che operano i soci,
con quella di Dukascopy e dei futures.

Orario: quello del server, **New York + 7 ore tutto l'anno** (verificato il 09/10,
`magazzino/registro/documenti/ULTIMA_MEZZORA_FATTIBILITA.md`); la colonna si chiama `ora_server` e non si converte qui:
la conversione ha un proprietario solo, il loader. Si collega al terminale gia' aperto: nessuna credenziale.
Stampa solo conteggi. Scrive `motore/data/prezzi/volatilita_mt5/<SIMBOLO>_M5.csv` (fuori da git).

Uso: python magazzino/registro/codice/volatilita/esporta_mt5.py
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import pandas as pd

ROOT = next(str(p) for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())
OUT = os.path.join(ROOT, "motore/data/prezzi/volatilita_mt5")
SIMBOLI = ["US500", "US100", "US30", "GER40", "XAUUSD.cyr", "XAGUSD.cyr", "XTIUSD", "EURUSD"]
PASSO = dt.timedelta(days=60)          # 60 giorni di M5 < 100.000 barre (limite del terminale)


def main() -> int:
    import MetaTrader5 as mt5  # type: ignore
    if not mt5.initialize():
        print("MT5 initialize() fallito:", mt5.last_error())
        return 1
    os.makedirs(OUT, exist_ok=True)
    try:
        fine = dt.datetime.now() + dt.timedelta(days=2)
        for s in SIMBOLI:
            if not mt5.symbol_select(s, True):
                print(f"{s}: simbolo non disponibile", mt5.last_error())
                continue
            pezzi, da = [], dt.datetime(2024, 1, 1)
            while da < fine:
                r = mt5.copy_rates_range(s, mt5.TIMEFRAME_M5, da, da + PASSO)
                if r is not None and len(r):
                    pezzi.append(pd.DataFrame(r))
                da += PASSO
            if not pezzi:
                print(f"{s}: nessuna barra")
                continue
            df = pd.concat(pezzi).drop_duplicates("time").sort_values("time")
            df["ora_server"] = pd.to_datetime(df["time"], unit="s")
            df = df[["ora_server", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]]
            percorso = os.path.join(OUT, f"{s.split('.')[0]}_M5.csv")
            tmp = percorso + ".tmp"
            df.to_csv(tmp, index=False)
            os.replace(tmp, percorso)
            print(f"{s}: {len(df)} barre, {df['ora_server'].iloc[0]} -> {df['ora_server'].iloc[-1]} (ora del server)")
    finally:
        mt5.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
