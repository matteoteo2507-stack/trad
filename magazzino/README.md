# magazzino — teoria, fonti, registro degli studi

Terza macro del repo in ordine di processo (DECISIONS 2026-11-09): qui sta cio' che si conserva. La teoria su cui
poggia la ricerca, le fonti da cui viene, e il registro di tutto cio' che e' stato studiato, chiuso o riaperto.

| Cartella | Cosa contiene | Regola |
|---|---|---|
| [`fondamenti_tecnici/`](fondamenti_tecnici/README.md) | la teoria: moduli `0X_*/principles.md`, `TRADING_PRINCIPLES.md`, `RIFERIMENTI.md`, `blueprints/`; la definizione di strategia e di strumento e' nel modulo 04 §0 | si corregge sul posto |
| `fonti/` | fonti grezze: `sorgenti/` (testi, trascrizioni, PDF) e `materiale_socio/` (dati e materiale dei soci, in gran parte fuori da git) | **immutabili**: si leggono, non si modificano |
| [`registro/`](registro/README.md) | `documenti/` (pre-registrazioni e documenti di studio, anche le strategie candidate storiche) e `referti/` (verdetti, intake, ricerche; `referti/audit/` per gli output degli audit), `codice/` (il codice di ogni studio) | per tipo, **non per stato** |
| `dormienti/` | cio' che non gira ma non e' ancora stato cancellato: documenti di architettura di maggio, journal, vecchi pick dello Stock Selector, e il codice fermo (strategie Confluence e Stock Selector, Level Analyzer, orchestratore) | si cancella quando Matteo lo giudica inutile (decisione del 10/11) |

## Perche' per tipo e non per famiglia (decisione di Claude, 10/11, su mandato di Matteo)

Lo studio e' l'unita' di lavoro, e non tutti gli studi sono famiglie del contatore: gli strumenti da consegnare ai
soci (es. il GARCH), gli intake di una fonte, le ricerche sui dati non hanno una famiglia. Una cartella per famiglia
lascerebbe fuori ogni caso nuovo; una per tipo li accoglie tutti. Per trovare tutto cio' che riguarda una famiglia o
uno strumento serve un **indice generato** dal contatore e dal frontmatter (da fare, `decisioni/README.md`), non una
gerarchia di cartelle. Lo stato vive nel frontmatter e nel contatore: un verdetto o una riapertura non spostano file.

## Il codice (dal 10/11, col passo del motore)

- **`registro/codice/`**: il codice degli studi, una sottocartella per studio (era `analysis/`, piu' `tsmom/`,
  `seasonality/` e il backtest di `meanrev/` che stavano in `strategies/`). Si importa come
  `magazzino.registro.codice.<studio>`. I dati di prezzo che usa **non** sono qui: stanno in `motore/data/prezzi/`.
- **`dormienti/`**: il codice che non gira: `strategies/` (Confluence, Stock Selector, template), `level_analyzer/`,
  `backtesters/`, `orchestratore/` (era `core/runner.py` e `core/registry.py`). I test di questo codice restano in
  `motore/tests/`, cosi' si vede subito se smette di funzionare.
- **`registro/codice/ultima_mezzora/` e' congelato** (studio H1, chiuso il 12/10): si riproduce dal commit del
  verdetto. Dal 10/11 vi sono cambiate solo le righe di import, perche' il suo test lo importa; la logica e i percorsi
  restano quelli del verdetto, quindi lanciato da qui si ferma al controllo del contatore.
