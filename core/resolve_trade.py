"""Primitiva UNICA per risolvere un trade su barre OHLC.

Perche' esiste
--------------
La stessa logica era reimplementata **quattro volte con quattro convenzioni diverse**
(`analysis/nxt/backtest.py`, `analysis/nxt/closure.py`, `analysis/nxt/entry_fill_audit.py`,
`analysis/opening_range/backtest_v2.py`). Le differenze non erano documentate e hanno
prodotto l'ambiguita' +0,354 / +0,308 / +0,347 sullo stesso lead, che nessuno sapeva
spiegare. Richiesta dalla pre-registrazione del FADE, sez. 11, condizione 1.

Qui le convenzioni diventano **parametri espliciti con un default dichiarato**, e ogni
chiamante deve sceglierle guardandole in faccia.

I cinque assi, e perche' contano
--------------------------------
1. `fill_bar_can_resolve` - la barra di riempimento puo' gia' chiudere il trade?
   Dire di si' e' ottimista sui TP veloci e pessimista sugli SL veloci, e non e'
   neutro: su un ingresso stop la barra di fill e' quella che si stava gia' muovendo.
2. `tie` - quando in una barra il prezzo tocca SL **e** TP, quale e' avvenuto prima?
   Dal solo OHLC non e' decidibile. `"pess"` assume SL, `"opt"` assume TP.
   La distanza fra i due e' la misura dell'ignoranza, non del risultato.
3. `gap_beyond_stop` - se la barra apre gia' oltre lo stop, si esce **all'apertura**
   (realistico) o allo stop (ottimistico)? Ignorarlo regala allo stop un prezzo che
   il mercato non offriva: e' lo stesso difetto del fill fantasma, sul lato uscita.
4. `be_priority` - il break-even si valuta prima o dopo SL/TP nella stessa barra?
   La famiglia NXT lo valuta **prima**, l'ORB **dopo**. In una barra che tocca BE e TP
   insieme la prima chiude a **0**, la seconda a **+3R**. Sullo stesso identico dato.
   Nessuna delle due e' "giusta": dall'OHLC non si sa in che ordine sia successo.
5. `on_timeout` - un trade che a max-hold non ha toccato ne' SL ne' TP:
   `"mark"` lo chiude al prezzo corrente (quello che fa l'EA), `"drop"` lo **scarta**.

   ⚠️ `"drop"` non e' una convenzione, e' un **filtro sull'esito**: toglie dal campione
   esattamente i trade che non sono andati da nessuna parte. Tre delle quattro
   implementazioni originali lo facevano, e il default qui e' `"mark"` per questo.
   Chi vuole `"drop"` deve scriverlo e giustificarlo.

Unita'
------
`r_unit` (l'R **inteso**, su cui e' stato dimensionato il volume) e' separato da
`risk = |fill - sl|` (quello **reale**). Coincidono solo se il fill e' avvenuto al
prezzo previsto. Il break-even si calcola sul rischio reale, il rendimento si
normalizza sull'R inteso: e' cosi' che un fill peggiore del previsto si vede nei numeri
invece di sparire.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

__all__ = ["FillConvention", "TradeResult", "resolve_trade", "PESSIMISTA", "OTTIMISTA"]


@dataclass(frozen=True)
class FillConvention:
    """Le cinque scelte che cambiano il risultato a parita' di dati."""

    fill_bar_can_resolve: bool = True
    tie: str = "pess"                 # "pess" | "opt"
    gap_beyond_stop: bool = True
    on_timeout: str = "mark"          # "mark" | "drop"
    be_priority: str = "first"        # "first" | "last": quando si valuta il break-even

    def __post_init__(self) -> None:
        if self.tie not in ("pess", "opt"):
            raise ValueError("tie deve essere 'pess' o 'opt', non %r" % (self.tie,))
        if self.on_timeout not in ("mark", "drop"):
            raise ValueError(
                "on_timeout deve essere 'mark' o 'drop', non %r" % (self.on_timeout,))
        if self.be_priority not in ("first", "last"):
            raise ValueError(
                "be_priority deve essere 'first' o 'last', non %r" % (self.be_priority,))


#: Convenzione di riferimento: la piu' sfavorevole su ogni asse ambiguo, ma **senza**
#: scartare i trade in timeout, perche' scartarli non e' prudenza, e' selezione.
PESSIMISTA = FillConvention(fill_bar_can_resolve=True, tie="pess",
                            gap_beyond_stop=True, on_timeout="mark")

#: Speculare, per bracketing. La distanza fra le due misura l'ambiguita' residua.
OTTIMISTA = FillConvention(fill_bar_can_resolve=True, tie="opt",
                           gap_beyond_stop=False, on_timeout="mark")


@dataclass(frozen=True)
class TradeResult:
    r: float                  # rendimento in unita' di R inteso, costi inclusi
    outcome: str              # "TP" | "SL" | "BE" | "TIMEOUT"
    bars_held: int
    be_hit: bool
    exit_price: float


def resolve_trade(
    O: Sequence[float],
    H: Sequence[float],
    L: Sequence[float],
    C: Sequence[float],
    f: int,
    *,
    fill: float,
    sl: float,
    tp: float,
    long: bool,
    r_unit: float,
    max_hold: int,
    be_at: Optional[float] = None,
    cost_R: float = 0.0,
    conv: FillConvention = PESSIMISTA,
) -> Optional[TradeResult]:
    """Risolve un trade dalla barra di fill `f` in poi.

    Ritorna None solo se il trade non e' risolvibile: dati insufficienti, rischio nullo,
    oppure timeout con `on_timeout="drop"`. In ogni altro caso ritorna un TradeResult.

    `be_at=None` disattiva il break-even; `be_at=2.0` sposta lo stop al prezzo di
    ingresso quando il prezzo ha percorso 2 volte il rischio reale a favore.
    """
    n = len(H)
    if not (0 <= f < n) or r_unit <= 0:
        return None
    risk = abs(fill - sl)
    if risk <= 0:
        return None

    sgn = 1.0 if long else -1.0
    be_level = None
    if be_at is not None:
        be_level = fill + be_at * risk if long else fill - be_at * risk

    be_on = False
    sl_cur = sl
    start = f if conv.fill_bar_can_resolve else f + 1
    end = min(f + max_hold, n)
    if start >= end:
        return None

    for j in range(start, end):
        reached_be = (be_level is not None and not be_on and
                      ((H[j] >= be_level) if long else (L[j] <= be_level)))

        # 1) break-even: PRIMA di SL/TP (famiglia NXT) oppure DOPO (ORB).
        #    Non e' un dettaglio: in una barra che tocca BE e TP insieme,
        #    "first" sposta lo stop a pareggio e puo' chiudere a 0, "last"
        #    chiude a TP. Sullo stesso dato, 0 contro +3R.
        if reached_be and conv.be_priority == "first":
            be_on, sl_cur = True, fill

        hit_sl = (L[j] <= sl_cur) if long else (H[j] >= sl_cur)
        hit_tp = (H[j] >= tp) if long else (L[j] <= tp)

        # 2) pareggio intrabar: indecidibile dall'OHLC, lo decide la convenzione
        if hit_sl and hit_tp:
            if conv.tie == "pess":
                hit_tp = False
            else:
                hit_sl = False

        if conv.be_priority == "last" and not hit_sl and not hit_tp and reached_be:
            be_on, sl_cur = True, fill

        if hit_sl:
            # 3) gap: se la barra APRE gia' oltre lo stop, si esce all'apertura.
            #    Sulla barra di fill no: la sua apertura precede l'ingresso.
            jumped = False
            if conv.gap_beyond_stop and j != f:
                jumped = (O[j] < sl_cur) if long else (O[j] > sl_cur)
            px = O[j] if jumped else sl_cur
            return TradeResult(
                r=sgn * (px - fill) / r_unit - cost_R,
                outcome="BE" if be_on else "SL",
                bars_held=j - f,
                be_hit=be_on,
                exit_price=px,
            )

        if hit_tp:
            return TradeResult(
                r=sgn * (tp - fill) / r_unit - cost_R,
                outcome="TP",
                bars_held=j - f,
                be_hit=be_on,
                exit_price=tp,
            )

    # 4) timeout
    if conv.on_timeout == "drop":
        return None
    px = C[end - 1]
    return TradeResult(
        r=sgn * (px - fill) / r_unit - cost_R,
        outcome="TIMEOUT",
        bars_held=end - 1 - f,
        be_hit=be_on,
        exit_price=px,
    )
