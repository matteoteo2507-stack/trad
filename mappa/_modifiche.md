---
titolo: Registro modifiche di architettura
tipo: registro
---

# Registro modifiche di architettura

Ogni modifica di architettura fatta da Claude finisce qui nella stessa sessione, con stato
`da_rivedere`. Matteo le rivede nel rituale settimanale e le porta a `rivisto`.
Regola completa: [CLAUDE.md](../CLAUDE.md#mappa-e-protocollo-modifiche).

| Data | Cosa | Perché | Note/file toccati | Impatto | Stato |
|---|---|---|---|---|---|
| 2026-09-27 | Commit `bc2d987` del lavoro rimasto aperto dal 21/09 (voci A1/B3 in DECISIONS, `core/trial_ledger.py`, `data_checks.py`, `random_baseline.py` + test, doc TREND_*/B3_*) | Salvare il lavoro prima dello spostamento | 21 file, vedi commit | Nessuno sul comportamento: era già il codice in uso | da_rivedere |
| 2026-09-27 | Repo spostato da `Desktop\lavoro\trad` a `Obsidian\claude-brain\trad` | Vault centrale (piano 27/09) | intera cartella; backup in `Desktop\lavoro\_backup-2026-09-27` | Test invariati (166 passati, 2 saltati prima e dopo). Il vecchio percorso resta citato solo in report generati | da_rivedere |
| 2026-09-27 | Memoria automatica di Claude spostata in `claude-brain/memoria/trad` via `.claude/settings.json` (`autoMemoryDirectory`) | Col nuovo percorso la memoria sarebbe rimasta orfana; così è visibile in Obsidian e i ~60 wikilink verso di lei si risolvono | `.claude/settings.json` (nuovo) | Le sessioni aperte su `trad/` leggono e scrivono lì. Originale intatto in `~/.claude/projects/c--Users-mmbus-Desktop-lavoro-trad/memory` | da_rivedere |
| 2026-09-27 | Nuovo `CLAUDE.md`: ordine di lettura (stato canonico → DECISIONS più recente → metodo → trial ledger) e protocollo modifiche | Prima non esisteva: Claude si orientava senza regole scritte, da qui "mescola versioni" | `CLAUDE.md` | Cambia come Claude cerca numeri e stati | da_rivedere |
| 2026-09-27 | Percorso aggiornato nelle istruzioni di `README.md`, `docs/ARCHITECTURE_v2.md`, `docs/OPERATIONAL_GUIDE.md` | Puntavano ancora a `Desktop\lavoro\trad` | 3 doc | Solo documentazione | da_rivedere |
| 2026-09-27 | **Stato canonico nel frontmatter** delle 10 pre-registrazioni (`stato`, `aggiornato`, `decisione`, `metrica_corrente`, `nota`), ricostruito voce per voce da DECISIONS | Causa radice del "mescola versioni": `docs/README.md` diceva ancora **FADE ATTIVO** e **copier +0,194** dopo il KILL del 17/09 e la correzione del 18/09 | `docs/*_PREREGISTRATION.md` (solo frontmatter, corpo intatto) | D'ora in poi lo stato si legge **solo** lì. Stati: FADE KILL · copier IN AVVIO · mentore CONFERMATO (numeri 18/09) · playground LEAD fermo · TSMOM/ORB NO-GO declassati da A5 · MEANREV/TOM NO-GO · livelli e numeri tondi CLOSED | da_rivedere |
| 2026-09-27 | `docs/README.md`: la tabella delle pre-registrazioni non ripete più stati né numeri (solo "cosa testa") + aggiunta la playground, che mancava | Una tabella che copia gli stati invecchia in silenzio | `docs/README.md` | Per lo stato: frontmatter o cruscotto | da_rivedere |
| 2026-09-27 | Nuovo cruscotto `mappa/_cruscotto.base` (Obsidian Bases) sullo stato canonico | Rendere visibili gli stati dove Matteo guarda, anche da telefono | `mappa/_cruscotto.base` | Solo lettura | da_rivedere |
| 2026-09-27 | Marcatori **"⚠️ Superato"** (senza riscrivere la storia) sulle affermazioni al presente diventate false: FADE "+0,35R robusto" e "+0,31R", forward ORB "in corso", EA `nxt_fade` con atteso +0,35R | Erano le copie che Claude poteva pescare come attuali | `fondamenti_tecnici/_INTAKE.md` (righe 34, 132), `strategie_candidate/fade_mr_walkforward_socio.md` e `nxt_fib_trend_pullback.md` (+ `stato` nel frontmatter), `mql5/README.md` | Nessun numero storico cancellato. DECISIONS, review, report di salute e schede YouTube **non toccati**: sono storia datata, non stato | da_rivedere |
| 2026-09-27 | `aliases: [0X_nome]` nel frontmatter degli 8 moduli di `fondamenti_tecnici` | I ~66 wikilink tipo `[[04_quant_metodologia]]` puntavano a una cartella e in Obsidian non si risolvevano | `0X_*/principles.md`, `07_data_sources/reference.md` | Nessuna rinomina: i link relativi restano validi | da_rivedere |
| 2026-09-27 | `fondamenti_tecnici/README.md` elenca tutte e 3 le strategie candidate (prima solo 1) | Indice incompleto | `fondamenti_tecnici/README.md` | — | da_rivedere |

**Non toccato di proposito:** "384 trial" (25 occorrenze). È il conteggio **fisso** di una famiglia
chiusa, confermato dall'audit A5, e non può divergere. Il totale **corrente** dei trial si legge solo
da `python -m core.trial_ledger`. `analysis/trading-bot-eval/SIZING_SPEC.md` (XAU +0.194) riguarda la
valutazione di un bot di terzi, non i segnali del mentore: da verificare con Matteo, non corretto.
