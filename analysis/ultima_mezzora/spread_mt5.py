"""Spread dei CFD su indici nella finestra dell'ultima mezz'ora (backlog H1, passo 2). 0 trial.

Misura dai tick di MT5 (bid e ask) quanto costa entrare 30 minuti prima della chiusura e uscire alla
chiusura, e lo confronta col guadagno lordo pubblicato. NON calcola nessun rendimento: e' un controllo
di accessibilita' (STRATEGY_LIFECYCLE §3: costi ed esecuzione non sono trial).

Soglia dichiarata prima della misura (docs/BACKLOG_RICERCA.md §H, H1 passo 2, 08/10): se il costo per
operazione e' almeno META' del lordo stimato, H1 si chiude qui.

Fuso orario: i tempi di MT5 sono ora server senza fuso, e lo scarto del server FP Markets NON e' fisso
(docs/ULTIMA_MEZZORA_FATTIBILITA.md). Per ogni giorno lo si ricava da US500: fra due convenzioni
(server = Europe/Bucharest; server = New York + 7 ore) si tiene quella in cui non ci sono tick nella
pausa dei futures USA (17:15-17:45 ET) e ce ne sono fra le 16 e le 17 ET. Un giorno che nessuna
convenzione spiega viene escluso e contato. La convenzione del giorno vale per tutti i simboli.

Uso: python analysis/ultima_mezzora/spread_mt5.py [--giorni 180] [--simboli US500 US100 GER40 UK100 EURO50]
     (terminale MT5 aperto e connesso; nessuna credenziale letta dallo script)
"""
from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta, timezone

import pandas as pd

SERVER_TZ = "Europe/Bucharest"
ET = "America/New_York"
RIFERIMENTO = "US500"  # il simbolo su cui si legge la pausa dei futures USA
PAUSA = ((17, 15), (17, 45))
# Finestra per simbolo: fuso della borsa, entrata, uscita (Baltussen et al. 2021, Tab. 1).
FINESTRE = {
    "US500": (ET, (15, 30), (16, 0)),
    "US100": (ET, (15, 30), (16, 0)),
    "GER40": ("Europe/Berlin", (17, 0), (17, 30)),
    "EURO50": ("Europe/Berlin", (17, 0), (17, 30)),
    "UK100": ("Europe/London", (16, 0), (16, 30)),
}
# Lordo stimato per operazione di solo segno, in punti base: Baltussen et al. 2021, Tab. 6, futures azionari,
# 6,86% annuo / ~252 giorni (stima a spanne scritta nel backlog H1 l'08/10, prima della misura).
LORDO_PB = 2.7
SOGLIA_QUOTA = 0.5  # il costo non deve superare meta' del lordo
STANTIO_MAX = pd.Timedelta(seconds=60)  # una quotazione piu' vecchia di cosi' non vale
OUT = os.path.join(os.path.dirname(__file__), "..", "trading-bot-eval", "data")


def _a(giorno: date, hm: tuple[int, int], fuso: str = ET) -> pd.Timestamp:
    return pd.Timestamp(datetime(giorno.year, giorno.month, giorno.day, *hm)).tz_localize(fuso)


def _server_naive(ts: pd.Timestamp) -> datetime:
    """Ora server (convenzione Bucharest) come datetime UTC, il formato che chiede l'API di MT5."""
    s = ts.tz_convert(SERVER_TZ).tz_localize(None)
    return datetime(s.year, s.month, s.day, s.hour, s.minute, s.second, tzinfo=timezone.utc)


def _converti(naive: pd.DatetimeIndex, convenzione: str) -> pd.DatetimeIndex:
    """Converte l'ora server in ora di New York secondo una delle due convenzioni."""
    if convenzione == "bucharest":
        return naive.tz_localize(SERVER_TZ, ambiguous="NaT", nonexistent="NaT").tz_convert(ET)
    # server = New York + 7 ore (chiusura di New York a mezzanotte server)
    return (naive - pd.Timedelta(hours=7)).tz_localize(ET, ambiguous="NaT", nonexistent="NaT")


def scarica_tick(mt5, simbolo: str, da: pd.Timestamp, a: pd.Timestamp) -> pd.DataFrame | None:
    """Tick bid/ask fra due istanti, con un'ora di margine per lato (le convenzioni differiscono di un'ora)."""
    margine = pd.Timedelta(hours=1, minutes=30)
    r = mt5.copy_ticks_range(simbolo, _server_naive(da - margine), _server_naive(a + margine),
                             mt5.COPY_TICKS_INFO)
    if r is None or len(r) == 0:
        return None
    df = pd.DataFrame(r)[["time_msc", "bid", "ask"]]
    df = df[(df["bid"] > 0) & (df["ask"] >= df["bid"])]
    df.index = pd.to_datetime(df["time_msc"], unit="ms")
    return df[["bid", "ask"]]


def convenzione_del_giorno(mt5, giorno: date) -> str | None:
    """Convenzione oraria del server in quel giorno, letta dalla pausa dei futures su US500."""
    tick = scarica_tick(mt5, RIFERIMENTO, _a(giorno, (15, 30)), _a(giorno, (18, 0)))
    if tick is None:
        return None
    for conv in ("bucharest", "ny_piu_7"):
        idx = _converti(tick.index, conv)
        idx = idx[idx.notna()]
        nella_pausa = ((idx >= _a(giorno, PAUSA[0])) & (idx < _a(giorno, PAUSA[1]))).sum()
        dopo_chiusura = ((idx >= _a(giorno, (16, 0))) & (idx < _a(giorno, (17, 0)))).sum()
        if nella_pausa == 0 and dopo_chiusura > 0:
            return conv
    return None


def _quota(tick: pd.DataFrame, istante: pd.Timestamp) -> tuple[float, float] | None:
    """Ultima quotazione prima dell'istante, se non e' troppo vecchia: (spread, prezzo medio)."""
    prima = tick[tick.index <= istante]
    if prima.empty or istante - prima.index[-1] > STANTIO_MAX:
        return None
    bid, ask = prima.iloc[-1]["bid"], prima.iloc[-1]["ask"]
    return ask - bid, (ask + bid) / 2


def misura_giorno(mt5, simbolo: str, giorno: date, conv: str) -> dict:
    """Costo dell'operazione nella finestra del simbolo, con la convenzione oraria del giorno."""
    fuso, hm_in, hm_out = FINESTRE[simbolo]
    entrata, uscita = _a(giorno, hm_in, fuso), _a(giorno, hm_out, fuso)
    esito = {"giorno": giorno, "convenzione": conv}
    tick = scarica_tick(mt5, simbolo, entrata, uscita)
    if tick is None:
        esito["convenzione"] = "nessun_tick"
        return esito
    tick.index = _converti(tick.index, conv)
    tick = tick[tick.index.notna()]
    q_in, q_out = _quota(tick, entrata), _quota(tick, uscita)
    if q_in is None or q_out is None:
        esito["convenzione"] = conv + "_senza_quota"
        return esito
    (s_in, m_in), (s_out, m_out) = q_in, q_out
    esito.update(
        spread_in=s_in, spread_out=s_out, prezzo=m_in,
        # costo andata e ritorno rispetto al prezzo medio: meta' spread in entrata + meta' in uscita
        costo_pb=(s_in / m_in + s_out / m_out) / 2 * 1e4,
    )
    return esito


def riassumi(simbolo: str, esiti: list[dict], spread_ora: float | None) -> pd.DataFrame:
    """Stampa la distribuzione del costo e il confronto con la soglia; restituisce i giorni validi."""
    validi = [e for e in esiti if "costo_pb" in e]
    conv = pd.Series([e["convenzione"] for e in esiti]).value_counts(dropna=False)
    fuso, hm_in, hm_out = FINESTRE[simbolo]
    print(f"\n=== {simbolo}  finestra {hm_in[0]:02d}:{hm_in[1]:02d}-{hm_out[0]:02d}:{hm_out[1]:02d} {fuso} "
          f"(spread istantaneo adesso: {spread_ora})")
    print(f"giorni richiesti {len(esiti)} | esito per giorno: {conv.to_dict()}")
    if not validi:
        print("nessun giorno valido")
        return pd.DataFrame()
    df = pd.DataFrame(validi)
    c = df["costo_pb"]
    soglia = SOGLIA_QUOTA * LORDO_PB
    print(f"giorni validi {len(df)}: {df['giorno'].min()} -> {df['giorno'].max()}")
    print(f"spread in entrata (punti): mediana {df['spread_in'].median():.2f}  p90 {df['spread_in'].quantile(.9):.2f}")
    print(f"spread in uscita (punti): mediana {df['spread_out'].median():.2f}  p90 {df['spread_out'].quantile(.9):.2f}")
    print(f"costo per operazione (pb): mediana {c.median():.2f}  media {c.mean():.2f}  "
          f"p75 {c.quantile(.75):.2f}  p90 {c.quantile(.9):.2f}  max {c.max():.2f}")
    print(f"lordo stimato {LORDO_PB} pb -> soglia di chiusura {soglia:.2f} pb (meta') | costo mediano = "
          f"{c.median() / LORDO_PB:.0%} del lordo | giorni sopra soglia: {(c >= soglia).mean():.0%}")
    return df


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--giorni", type=int, default=180, help="giorni di calendario all'indietro")
    p.add_argument("--simboli", nargs="+", default=["US500", "US100"])
    args = p.parse_args()
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        print("MetaTrader5 non installato (serve il PC con MT5)")
        return 1
    if not mt5.initialize():
        print("MT5 initialize() fallito:", mt5.last_error())
        return 1
    try:
        oggi = date.today()
        giorni = [oggi - timedelta(days=k) for k in range(1, args.giorni + 1)]
        giorni = [g for g in giorni if g.weekday() < 5]
        mt5.symbol_select(RIFERIMENTO, True)
        convenzioni = {g: convenzione_del_giorno(mt5, g) for g in giorni}
        conta = pd.Series(list(convenzioni.values())).value_counts(dropna=False).to_dict()
        print(f"convenzione oraria del server per giorno (da {RIFERIMENTO}): {conta}")
        for simbolo in args.simboli:
            if simbolo not in FINESTRE:
                print(f"[SKIP] {simbolo}: finestra non dichiarata in FINESTRE")
                continue
            if not mt5.symbol_select(simbolo, True):
                print(f"[SKIP] {simbolo}: {mt5.last_error()}")
                continue
            info = mt5.symbol_info(simbolo)
            esiti = [{"giorno": g, "convenzione": "fuso_non_spiegato"} if convenzioni[g] is None
                     else misura_giorno(mt5, simbolo, g, convenzioni[g]) for g in giorni]
            df = riassumi(simbolo, esiti, None if info is None else info.spread * info.point)
            if not df.empty:
                df.to_csv(os.path.join(OUT, f"spread_ultima_mezzora_{simbolo}.csv"), index=False)
    finally:
        mt5.shutdown()
    print(f"\nDettaglio per giorno in {os.path.normpath(OUT)} (fuori da git).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
