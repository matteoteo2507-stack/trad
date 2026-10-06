"""Modelli di gestione del rischio per le prop.

Un profilo = sizing di BASE + lista di MODIFICATORI moltiplicativi.
Il simulatore prop chiede, prima di ogni trade, quanto rischiare (in valuta),
passando lo stato del conto. Esempio YAML:

  - name: dd_lineare_1pct
    base: {type: fixed_pct, pct: 1.0, of: initial}
    modifiers:
      - {type: dd_linear, min_mult: 0.25}
      - {type: daily_guard, stop_at: 0.6, max_trades: 3}

Base:
  fixed_pct   pct% di 'balance' (composto) oppure 'initial' (importo fisso)
Modificatori:
  dd_linear     riduce il rischio in proporzione alla distanza rimasta dal limite di max loss
  dd_tiers      scaglioni: [[dd_pct, mult], ...] (dd dal picco, in % del conto iniziale)
  loss_streak   dopo `after` perdite di fila moltiplica per factor^k (min min_mult), reset al primo win
  win_boost     dopo una vincita moltiplica per `mult` (anti-martingala, max `cap`)
  daily_guard   smette di tradare oggi se la perdita giornaliera ha usato `stop_at` del limite
                o dopo `max_trades` trade; opzionale `stop_after_win` (chiude la giornata dopo un win)
  target_coast  vicino al target (oltre `near` della strada) rischia `mult` volte
  floor_cap     il rischio di un trade non supera `frac` della distanza dal limite più vicino (daily o max)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccountState:
    initial: float
    balance: float
    peak: float
    day_start: float
    day_pnl: float
    day_trades: int
    loss_streak: int
    win_streak: int
    target_balance: float     # obiettivo della fase (inf nel funded)
    floor_daily: float        # livello di equity che fa saltare il daily loss
    floor_max: float          # livello che fa saltare il max loss
    daily_limit_amt: float
    max_limit_amt: float


class RiskModel:
    def __init__(self, profile: dict):
        self.name = profile["name"]
        self.base = profile.get("base", {"type": "fixed_pct", "pct": 1.0, "of": "initial"})
        self.mods = profile.get("modifiers", [])
        self.floor_frac = next((m.get("frac", 0.9) for m in self.mods if m["type"] == "floor_cap"), None)

    def risk_amount(self, s: AccountState) -> float:
        b = self.base
        if b["type"] != "fixed_pct":
            raise ValueError(f"base sconosciuta: {b['type']}")
        ref = s.balance if b.get("of", "initial") == "balance" else s.initial
        risk = ref * b["pct"] / 100.0
        mult = 1.0
        for m in self.mods:
            t = m["type"]
            if t == "dd_linear":
                room = s.balance - s.floor_max
                mult *= max(m.get("min_mult", 0.25), min(1.0, room / s.max_limit_amt))
            elif t == "dd_tiers":
                dd_pct = (s.peak - s.balance) / s.initial * 100
                k = 1.0
                for thr, mm in sorted(m["tiers"]):
                    if dd_pct >= thr:
                        k = mm
                mult *= k
            elif t == "loss_streak":
                if s.loss_streak >= m.get("after", 2):
                    steps = s.loss_streak - m.get("after", 2) + 1
                    mult *= max(m.get("min_mult", 0.25), m.get("factor", 0.5) ** steps)
            elif t == "win_boost":
                if s.win_streak >= 1:
                    mult *= min(m.get("cap", 2.0), m.get("mult", 1.5) ** s.win_streak)
            elif t == "daily_guard":
                if s.day_trades >= m.get("max_trades", 99):
                    return 0.0
                if m.get("stop_after_win") and s.day_pnl > 0:
                    return 0.0
                if -s.day_pnl >= m.get("stop_at", 0.6) * s.daily_limit_amt:
                    return 0.0
            elif t == "target_coast":
                if s.target_balance != float("inf"):
                    prog = (s.balance - s.initial) / (s.target_balance - s.initial)
                    if prog >= m.get("near", 0.8):
                        mult *= m.get("mult", 0.5)
            elif t == "floor_cap":
                pass
            else:
                raise ValueError(f"modificatore sconosciuto: {t}")
        risk *= mult
        if self.floor_frac is not None:
            room = min(s.balance - s.floor_max, s.balance - s.floor_daily)
            risk = min(risk, self.floor_frac * room)
        return max(0.0, risk)


def build_profiles(cfg: dict) -> list[dict]:
    """Profili espliciti + griglia automatica base_pcts x modifier_sets."""
    out = list(cfg.get("profiles", []))
    g = cfg.get("grid")
    if g:
        for pct in g["base_pcts"]:
            for of in g.get("of", ["initial"]):
                for set_name, mods in g["modifier_sets"].items():
                    out.append({"name": f"{set_name}|{pct}%{'c' if of == 'balance' else ''}",
                                "base": {"type": "fixed_pct", "pct": pct, "of": of},
                                "modifiers": mods or []})
    return out
