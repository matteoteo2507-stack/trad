# Materiale socio — indice unico

> Raccolta di tutto ciò che riguarda il **socio** (bot/canale **VELTRIX**, ex linkalphaflow/MG-Royal) e le **strategie degli ex-soci** (NXT/fade).
>
> **Regola di questa cartella.** Qui dentro sta solo il materiale *standalone*. Il resto è **intrecciato** con infrastruttura condivisa (data hub, `sys.path` hardcoded, link della knowledge base) e **NON è stato spostato per non rompere i path**: è solo **citato** sotto, con il percorso reale. Aggiornare questo indice quando si aggiunge/rimuove materiale del socio.

---

## 📁 Spostato qui (standalone)

- [PARTNER_AI_INTEGRATION_GUIDE.md](PARTNER_AI_INTEGRATION_GUIDE.md) — guida hand-off **per l'AI del socio**: valutazione del bot VELTRIX, Level Analyzer validato, warning di sicurezza (chiave Bybit esposta in git history), opzioni di integrazione. (Era in root; nessun link entrante → spostato.)

---

## 🤖 VELTRIX — motore/analisi del bot del socio *(resta in `analysis/veltrix/` — intrecciato)*

Cartella [`../analysis/veltrix/`](../analysis/veltrix/). **Non spostabile**: agganciata via `sys.path.insert("analysis/veltrix")` da 9 script in `trading-bot-eval/`, da [`../level_analyzer/detector.py`](../level_analyzer/detector.py) e letta da `session_ci.py`.
- `parse_alphanalist.py` — parser dei segnali del canale → `signals.csv` / `signals.jsonl` (dati grezzi del socio).
- `levels_engine.py` — port fedele dei detector del bot (swing S/R, OB, FVG…).
- `calibrate.py`, `calibrate_session.py` — calibrazione hit-rate per sessione.
- `validate_levels.py` — reazione-vs-random look-ahead-safe (base riusata anche da level_research).
- `xau_spot_levels.py` — livelli XAU spot.

## 🧪 Valutazione bot VELTRIX *(resta in `analysis/trading-bot-eval/` — data hub condiviso)*

Cartella [`../analysis/trading-bot-eval/`](../analysis/trading-bot-eval/). **Non spostabile**: `data/` è il **data hub** letto anche da `nxt/`, `level_research/`, `mentor_signals/`, `opening_range/`.
- `session_ci.py` — harness hit-rate per sessione (misurò ~53% vs 80-90% dichiarato).
- `level_reaction_analysis.py` + [`LEVEL_ANALYZER_SPEC.md`](../analysis/trading-bot-eval/LEVEL_ANALYZER_SPEC.md) — edge sui livelli `conf=2`.
- `expectancy_levels.py` / `_long.py` / `expectancy_sweep.py` / `expectancy_confluence.py` — expectancy per confluenza.
- `sizing_kelly.py` + `SIZING_SPEC.md`, `regime_gate.py`, `macro_xau.py`, `rebaseline.py`, `reconstruct_baseline.py`, `breakout_check.py`, `x_research.py`.
- `vendor-trading-bot/` — snapshot del repo bot del socio (riferimento).

## 🛠️ Level Analyzer *(resta in `../level_analyzer/` — riusa veltrix)*

[`../level_analyzer/`](../level_analyzer/) — strumento nato dalla valutazione VELTRIX; `detector.py` riusa `analysis/veltrix/levels_engine.py`.

## 📈 Strategie degli ex-soci — NXT / fade *(restano in `fondamenti_tecnici/` — link del registro intake)*

- [`../fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md`](../fondamenti_tecnici/strategie_candidate/nxt_fib_trend_pullback.md) — strategia **NXT** (Fib+Elliott): triage, pre-registrazione, verdetto **NO-GO** + chiusura (lead fade).
- [`../fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md`](../fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md) — **spec fade da consegnare al socio** per walk-forward live.
- [`../fondamenti_tecnici/_sorgenti/NXT strategy Fibonacci Elliott (video ex-socio).txt`](../fondamenti_tecnici/_sorgenti/) — fonte lossless del video dell'ex-socio.
- Motori: [`../analysis/nxt/backtest.py`](../analysis/nxt/backtest.py) + `closure.py` (leggono il data hub condiviso).
- Registro: [`../fondamenti_tecnici/_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md) (righe NXT).

## 🔗 Menzioni trasversali *(restano nei documenti globali — solo citate)*

- [`../DECISIONS.md`](../DECISIONS.md) — ORB "idea utente+socio" = NO-GO; il bot del socio è **discrezionale, fuori dal workflow quant**.
- [`../docs/TRADING_WORKFLOW_DESIGN.md`](../docs/TRADING_WORKFLOW_DESIGN.md) — "discrezione del socio scambiata per edge del sistema"; bot del socio fuori dal workflow.
- [`../docs/LEVEL_RESEARCH_PLAN.md`](../docs/LEVEL_RESEARCH_PLAN.md) — motore livelli basato su `analysis/veltrix/validate_levels.py`.
- [`../ROADMAP.md`](../ROADMAP.md) — OctoBot superato da Confluence Auto + VELTRIX.
- [`../signal_copier/README.md`](../signal_copier/README.md) — precedente da non ripetere: chiave Bybit nella git history di VELTRIX. ⚠️ **NB**: il signal_copier riguarda i **mentori**, non il socio — non confondere.

## 🧠 Memoria persistente *(fuori dal repo: `.claude/.../memory/`)*

- `project_partner_channel_linkalphaflow.md` — VELTRIX come Confluence di riferimento.
- `project_veltrix_bot_eval_2026_06_12.md` — valutazione bot (~53%, look-ahead, chiave esposta).
- `project_nxt_fib_nogo_2026_07_17.md` — NXT NO-GO + lead fade (walk-forward su demo/socio).

---

### Distinzione importante
**Socio** (bot/canale VELTRIX, ex-soci con NXT) ≠ **mentori** (segnali XAUUSD copiati via `signal_copier/`, primo edge reale del repo). Materiale diverso, non mescolare.
