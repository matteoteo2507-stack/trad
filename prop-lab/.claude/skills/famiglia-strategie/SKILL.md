---
name: famiglia-strategie
description: Da un'idea grezza / famiglia di strategie (es. "mean reversion", "breakout", "trend following", "liquidity sweep") ricerca tutte le varianti note, le formalizza in regole meccaniche, le implementa in lab/strategies/<famiglia>.py con griglie di parametri e lancia il backtest qualitativo. Usala quando l'utente nomina una famiglia o un concetto di trading da esplorare.
---

# Skill: famiglia di strategie → varianti meccaniche testate

Input: nome della famiglia (+ opzionale: simbolo, timeframe, file dati). Se mancano simbolo/dati,
usa quelli in `data/` e chiedi solo se non c'è nessun CSV.

## 1. Ricerca (ampia, prima di scrivere codice)
Cerca TUTTE le varianti note della famiglia, con WebSearch/WebFetch su:
- GitHub (repo di strategie, librerie di indicatori, awesome-lists di trading)
- X/Twitter e blog di trader sistematici (thread su regole e risultati)
- letteratura classica (es. Connors, Chan, Davey, Kaufman, Carver) e paper SSRN/arXiv
- TradingView (script pubblici: solo per capire la regola, non copiare codice protetto)

Per ogni variante annota: nome, regola in parole, fonte/link, parametri, mercati/timeframe dove viene usata,
e se è **meccanizzabile**. Le parti discrezionali vanno o formalizzate (es. "candela di rifiuto" → close nel 30%
opposto del range) o scartate dichiarandolo.

Scrivi `research/families/<famiglia>/catalogo.md` con:
- tabella varianti (nome · regola · ingresso · stop · uscita · parametri · fonte)
- sezione "scartate / non meccanizzabili" con motivo
- sezione "ipotesi": PERCHÉ la famiglia dovrebbe funzionare e in quali regimi dovrebbe fallire

## 2. Implementazione
Crea/aggiorna `lab/strategies/<famiglia>.py` seguendo `lab/strategies/base.py` e l'esempio `mean_reversion.py`:
- una classe `@register` per variante, `family = "<famiglia>"`, `description` con la fonte
- `grid`: 2–4 valori per parametro, **ordinati**, valori "ragionevoli" e non ottimizzati; max ~40 varianti per strategia
- usa solo `lab/indicators.py` o calcoli causali (rolling/shift positivi)
- stop sempre presente; target fissato al segnale (`tp_level`/`tp_r`) o uscita a condizione (`exit_long/short`); `max_bars` come time stop
- orari di sessione = orario SERVER MT5 (rendili parametri)

## 3. Controlli prima di lanciare
1. `python -m lab.cli list` → la famiglia compare con il numero di varianti
2. smoke test: `python -c` che chiama `signals()` di ogni classe su `data/…csv` e verifica che ci siano segnali e `sl_dist>0`
3. invoca l'agente **quant-reviewer** sul file nuovo (look-ahead, stop, costi, coerenza con il catalogo). Correggi ciò che segnala.

## 4. Backtest qualitativo
```
python -m lab.cli new --family <famiglia> --symbol <SIMBOLO> --data <csv>
python -m lab.cli stage1 --run results/<run_id>
```
Presenta all'utente `stage1_famiglia.csv`: quali sotto-strategie della famiglia hanno un vantaggio lordo
**diffuso** (pct_positive, median_exp, plateau) e quali no. Un buon segnale è una strategia con molte varianti
positive, non un singolo picco.

Poi chiedi se proseguire con fase 2 (costi) → 3 (prop × rischio) → conferma, oppure usa la skill `pipeline-prop`.

## Regole
- Non aggiungere varianti "su misura" dopo aver visto i risultati senza dirlo: ogni giro entra nel registro e abbassa il Deflated Sharpe, ed è giusto così.
- Mai guardare l'out-of-sample in questa skill.
