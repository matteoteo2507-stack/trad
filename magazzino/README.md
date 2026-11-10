# magazzino — teoria, fonti, registro degli studi

Terza macro del repo in ordine di processo (DECISIONS 2026-11-09): qui sta cio' che si conserva. La teoria su cui
poggia la ricerca, le fonti da cui viene, e il registro di tutto cio' che e' stato studiato, chiuso o riaperto.

| Cartella | Cosa contiene | Regola |
|---|---|---|
| [`fondamenti_tecnici/`](fondamenti_tecnici/README.md) | la teoria: moduli `0X_*/principles.md`, `TRADING_PRINCIPLES.md`, `RIFERIMENTI.md`, `blueprints/`; la definizione di strategia e di strumento e' nel modulo 04 §0 | si corregge sul posto |
| `fonti/` | fonti grezze: `sorgenti/` (testi, trascrizioni, PDF) e `materiale_socio/` (dati e materiale dei soci, in gran parte fuori da git) | **immutabili**: si leggono, non si modificano |
| [`registro/`](registro/README.md) | `documenti/` (pre-registrazioni e documenti di studio, anche le strategie candidate storiche) e `referti/` (verdetti, intake, ricerche; `referti/audit/` per gli output degli audit) | per tipo, **non per stato** |
| `dormienti/` | cio' che non gira ma non e' ancora stato cancellato: documenti di architettura di maggio, journal, vecchi pick dello Stock Selector | si cancella quando Matteo lo giudica inutile (decisione del 10/11) |

## Perche' per tipo e non per famiglia (decisione di Claude, 10/11, su mandato di Matteo)

Lo studio e' l'unita' di lavoro, e non tutti gli studi sono famiglie del contatore: gli strumenti da consegnare ai
soci (es. il GARCH), gli intake di una fonte, le ricerche sui dati non hanno una famiglia. Una cartella per famiglia
lascerebbe fuori ogni caso nuovo; una per tipo li accoglie tutti. Per trovare tutto cio' che riguarda una famiglia o
uno strumento serve un **indice generato** dal contatore e dal frontmatter (da fare, `decisioni/README.md`), non una
gerarchia di cartelle. Lo stato vive nel frontmatter e nel contatore: un verdetto o una riapertura non spostano file.

## Cosa manca ancora

Il **codice** degli studi (`analysis/`, `strategies/{tsmom,meanrev,seasonality}/`) e quello dormiente
(`strategies/{confluence_*,stock_selector,_base,_template}/`, `level_analyzer/`, `backtesters/`) arrivano col passo del
motore: prima ogni script deve trovare la radice del repo senza contare le cartelle.
