# Materiale socio — indice unico

> Raccolta di tutto ciò che riguarda il **socio** (bot/canale **VELTRIX**, ex linkalphaflow/MG-Royal) e le **strategie degli ex-soci** (NXT/fade).
>
> **Regola di questa cartella.** Qui dentro sta solo il materiale *standalone*. Il resto è **intrecciato** con infrastruttura condivisa (data hub, `sys.path` hardcoded, link della knowledge base) e **NON è stato spostato per non rompere i path**: è solo **citato** sotto, con il percorso reale. Aggiornare questo indice quando si aggiunge/rimuove materiale del socio.

---

## 📥 Dati in questa cartella

Ogni cartella dice nel nome **che fonte è, che tipo di dato e che periodo copre**. I contenuti sono fuori
da git (`.gitignore`: `/materiale_socio/*/`): restano solo su questo disco.

| Cartella | Cosa contiene | Usata da | Stato |
|---|---|---|---|
| `forexgump_telegram_2020-09_2026-09/` | export Telegram di **Forex Gump GOLD VIP** (21 file, 18.688 messaggi, 09/09/2020 → 28/09/2026) | [`../analysis/forexgump/parse.py`](../analysis/forexgump/parse.py) → `signals.csv` | pre-registrazione [`FOREXGUMP_LATENCY_PREREGISTRATION.md`](../docs/FOREXGUMP_LATENCY_PREREGISTRATION.md) |
| `xat_conto_demo_socio_2026-09/` | export MT5 del conto demo del socio (numero omesso) su cui girava **XAT** (il mentore XAU), 22 segnali × 3 gambe, 21-29/09/2026, con lo script `export.py` del socio. ⚠️ Orari = server **UTC+3** | [`analysis_team_live_2026-09-30.md`](../docs/reviews/analysis_team_live_2026-09-30.md), [`xat_cancellazioni_2026-10-02.md`](../docs/reviews/xat_cancellazioni_2026-10-02.md) | dati descrittivi, fuori dal conteggio N = 60 |
| `veltrix_alphanalist_chat_2026-06-08/` | export della chat Telegram privata con il bot **VELTRIX** (AlphaAnalist), esportato l'08/06/2026 in quattro formati (md, jsonl, json, html) + il suo README | [`../analysis/veltrix/parse_alphanalist.py`](../analysis/veltrix/parse_alphanalist.py) → `signals.csv`; `validate_levels.py`, `xau_spot_levels.py` | valutazione del bot chiusa il 12/06 ([memoria e DECISIONS](../DECISIONS.md)); dati di lavoro del parser |
| `veltrix_webapp_conti_2026-09-28/` | export dalla webapp **VELTRIX** del 28/09/2026: due schermate del cruscotto (`dash1.jpg`, `dash2.jpg`) e `operazioni_conti_aggiuntivi.csv` (314 operazioni sui conti aggiuntivi) | nessuno script | citato in [`_INTAKE.md`](../fondamenti_tecnici/_INTAKE.md) (riga Forex Gump): il backtest della webapp **non e' un risultato** |

| `vtob_dati_risultati_2022-07_2026-10/` | pacchetto **VTOB** del socio (11/10/2026), la parte che non va in git: `data/` = barre XAUUSD del suo broker (M15 dal 12/07/2022, M5 dal 09/05/2025, fino al 09/10/2026, ora del server); `risultati/` = i suoi trade, il portafoglio e le quattro griglie. ⚠️ La colonna `spread` **cambia unita'** il 20/10/2025 (millesimi prima, centesimi dopo): per questo le barre restano qui e non nel data hub. I testi (specifiche, Pine, EA, Python) stanno in [`_sorgenti/vtob_socio_2026-10-11/`](../fondamenti_tecnici/_sorgenti/vtob_socio_2026-10-11/) | [`../analysis/vtob_intake/descrittivi.py`](../analysis/vtob_intake/descrittivi.py) | intake dell'11/10 in quarantena: [`vtob_socio_intake_2026-10-11.md`](../docs/reviews/vtob_socio_intake_2026-10-11.md) |
| `vtob_dati_risultati_usm30_2000-06_2026-10/` | secondo pacchetto **VTOB** del socio (datato 12/10/2026), la parte che non va in git: `dati/` = barre XAUUSD M15, M30 (dal 16/04/2018), H1 e H4 (intraday dal 13/07/2011), D1 e W1 (dal 2000), USTEC M30 (dal 06/07/2022), NAS100 D1 Dukascopy (dal 2016); `backtest/` = i 535 trade, statistiche, mensile, grafici; `mt5/` = EA compilato (`.ex5`, non eseguito da noi). ⚠️ `dati/XAUUSD_M15.csv` e' **identico byte per byte** a quello del primo pacchetto: resta doppio perche' ognuno dei due codici lo cerca nella sua cartella. Stessa avvertenza sull'unita' dello spread dell'oro. ⚠️ Le barre prima del 12/07/2022 **non si usano** per lanciare le regole del socio senza una pre-registrazione. Testi in [`_sorgenti/vtob_socio_2026-10-12/`](../fondamenti_tecnici/_sorgenti/vtob_socio_2026-10-12/) | [`../analysis/vtob_intake/secondo_pacchetto.py`](../analysis/vtob_intake/secondo_pacchetto.py) | chiuso all'intake il 13/10: [nota, §8](../docs/reviews/vtob_socio_intake_2026-10-11.md) |

**Spostate qui l'11/10** dalla radice del repo (`alphanalist_chat_*`, `28-09/`): stessi file, nessuna modifica al contenuto.

**Canali chiusi all'intake (02/10, 0 trial), cartelle eliminate:** "Ben, Gold Trader", "THE GOLD SNIPER" e
"ROYAL TRADING EMPIRE". I numeri e i motivi restano nelle note
[Ben](../docs/reviews/ben_gold_trader_intake_2026-10-02.md),
[Gold Sniper](../docs/reviews/gold_sniper_intake_2026-10-02.md) e
[Royal](../docs/reviews/royal_trading_empire_intake_2026-10-02.md), e nella voce di [DECISIONS](../DECISIONS.md)
del 02/10.

⚠️ **XAT** e **Gump** sono fonti di segnali seguite dal socio, non materiale *suo*. La distinzione in fondo
(socio ≠ mentori) vale per VELTRIX e NXT.

**Rimosso il 03/10:** `PARTNER_AI_INTEGRATION_GUIDE.md` (guida di giugno per l'AI del socio su VELTRIX):
superata, resta nella storia di git.

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

## 🧠 Memoria persistente *(fuori dal repo: `claude-brain/memoria/trad/`)*

- `project_partner_channel_linkalphaflow.md` — VELTRIX come Confluence di riferimento.
- `project_veltrix_bot_eval_2026_06_12.md` — valutazione bot (~53%, look-ahead, chiave esposta).
- `project_nxt_fib_nogo_2026_07_17.md` — NXT NO-GO + lead fade (walk-forward su demo/socio).

---

### Distinzione importante
**Socio** (bot/canale VELTRIX, ex-soci con NXT) ≠ **mentori** (segnali XAUUSD copiati via `signal_copier/`; XAT in revisione dal 02/10). Materiale diverso, non mescolare.
