---
titolo: Portfolio & Decomposizione del Rischio
fonti:
  - "_sorgenti/quantportfolio managernotes.txt"
tipo: concetti
---

# Portfolio & Decomposizione del Rischio

> Battere un benchmark NON equivale a generare alpha. L'alpha è il rendimento ortogonale al rischio di mercato; tutto il resto (incluso un +87% del settore tech contro un +49% dell'indice) può essere solo sovraesposizione a beta. La gestione di portafoglio consiste nel decomporre il rischio (idiosincratico, settoriale, di mercato), misurarlo con modelli quantitativi (CAPM, PCA, fattori) e targettizzare esposizioni fattoriali coerenti con gli obiettivi, monitorando esposizioni che sono per natura non-stazionarie.

## Concetti

### Alpha: rendimento ortogonale al rischio di mercato

Un errore diffuso è credere che sovraperformare un benchmark (S&P 500, NASDAQ) significhi generare alpha. Formalmente, **l'alpha è il rendimento che eccede ciò che ci si aspetterebbe dalla sola esposizione al rischio** — cioè rendimento **indipendente dai movimenti di mercato (ortogonale ai fattori di mercato)**.

Esempio: un portafoglio tech che rende 87% contro il 49% dell'indice NON ha generato alpha se quella sovraperformance deriva da sovraesposizione al beta di mercato (e infatti soffre drawdown più severi nei ribassi). Il vero alpha si genera con rendimenti indipendenti dalla direzione del mercato: trading intraday attivo, raccolta del premio di volatilità, o stock selection con effettiva skill.

### Tassonomia del rischio azionario

Tre componenti gerarchiche, distinte per diversificabilità:

1. **Rischio idiosincratico (firm-specific):** unico della singola azienda (scandali, gestione scadente, eventi straordinari). Esempio: UnitedHealth (UNH) con un -45% nel periodo di detenzione mentre il resto del settore healthcare era positivo. **Diversificabile** tenendo più titoli: un portafoglio di settore equipesato riduce drasticamente questo rischio mantenendo un rendimento medio positivo.
2. **Rischio settoriale/di industria:** eventi avversi che colpiscono un intero settore (es. regolamentazione sul tech) muovono insieme tutti i titoli del comparto. **Diversificabile** incrociando più settori.
3. **Rischio di mercato (sistematico):** ciò che resta dopo aver diversificato firm e settore. Colpisce tutti gli asset, legato a fattori macro. **NON diversificabile.**

Insight chiave: un singolo titolo espone interamente a tutti gli upside e downside idiosincratici — sconsigliato dalla teoria, dato il rendimento idiosincratico atteso mediamente negativo. Un portafoglio equipesato di 9 titoli (3 tech, 3 healthcare, 3 staples), una volta diversificati rischio firm e settore, traccia lo SPY con correlazione quasi perfetta.

### Beneficio e limiti della diversificazione

Covarianza e correlazione misurano le relazioni tra titoli:
- **Entro lo stesso settore:** correlazione positiva (influenze comuni di comparto).
- **Tra settori diversi:** correlazione vicina a zero in tempi normali (indipendenza).
- **In periodi di stress:** le correlazioni di tutti i titoli aumentano rapidamente, anche tra settori normalmente scorrelati — il beneficio della diversificazione collassa proprio quando servirebbe (es. shock tariffe inizio 2025).

### Non-stazionarietà delle correlazioni

Le serie storiche finanziarie sono **non-stazionarie**: le proprietà statistiche classiche (convergenza delle correlazioni empiriche, Legge dei Grandi Numeri, Teorema del Limite Centrale) non valgono sotto cambi di regime. Di conseguenza **le matrici di correlazione sono dinamiche e inaffidabili come predittori durante le crisi**. Stesso problema per i beta e per le esposizioni fattoriali: instabili nel tempo, richiedono monitoraggio e ribilanciamento continui.

### PCA / spectral decomposition

L'Analisi delle Componenti Principali (PCA) è una decomposizione spettrale che estrae **fattori ortogonali** dalla variazione dei rendimenti, ciascuno un fattore di rischio indipendente, comprimendo 9 titoli in pochi componenti.

| Componente Principale | Varianza spiegata | Varianza cumulata | Interpretazione |
|-----------------------|-------------------|-------------------|-----------------|
| PC1                   | ~27%              | ~27%              | Fattore di mercato |
| PC2 + PC3             | n.d.              | ~60%              | Rischio settoriale / variazione |
| PC5 o PC6             | n.d.              | ~90%              | Include rischio idiosincratico residuo |

I **loading sulla PC1 hanno segno uniforme** su tutti i titoli, confermandola come fattore di mercato. Le componenti successive differenziano i settori (tech, healthcare, staples) catturando il rischio settoriale. Il rischio idiosincratico resta in larga parte non spiegato da mercato e settore — particolarmente evidente per UNH, i cui rendimenti estremi sono di origine idiosincratica.

### CAPM (Capital Asset Pricing Model)

Metodo basato su regressione per quantificare l'esposizione al rischio di mercato:

$$E(R) = R_f + \beta\,(R_m - R_f)$$

Si regrediscono i rendimenti dell'asset/portafoglio contro l'**excess return di mercato** (rendimento di mercato meno tasso risk-free).

- Se i rendimenti sono interamente spiegati dall'excess return di mercato → **nessun alpha**: la performance è guidata dal mercato.
- Se la regressione ha un'**intercetta (alpha) statisticamente diversa da zero** → rendimento indipendente dall'esposizione al rischio di mercato = **vero alpha**, indicatore di skill nello stock picking o nel timing.

Sui portafogli compositi l'alpha risulta tipicamente non significativo (rendimenti spiegati dall'esposizione di mercato). L'**R²** varia per settore: il tech mostra R² più alto (più rendimento spiegato dal mercato) rispetto a healthcare e staples. Nel dataset il mercato spiega ~27% della varianza; il resto motiva le estensioni multi-fattore.

### Beta per settore e trade-off rischio/rendimento

| Settore           | Beta (esposizione al mercato) | Comportamento |
|-------------------|-------------------------------|---------------|
| Technology        | > 1 (sovraesposto)            | Rendimenti maggiori nei bull, drawdown più severi nei bear |
| Consumer Staples  | ~0.33                         | Minore esposizione, drawdown più contenuti |
| Healthcare        | ~0.25                         | Minore esposizione, drawdown più contenuti |

Trade-off centrale: rendimenti più alti tramite esposizione al beta vs. performance più liscia e drawdown ridotti tramite diversificazione settoriale (beta < 1). Un beta > 1 è "sovraesposto" e performa peggio nei mercati ribassisti nonostante i guadagni superiori nei rialzisti.

### Estensioni del CAPM

Poiché il solo beta di mercato spiega una frazione della varianza, si ricorre a modelli multi-fattore che catturano altri rischi prezzati e possibili fonti di alpha:
- **Fama-French a 3 fattori** e a **5 fattori**.
- **Carhart** (aggiunge il fattore **momentum**).
- Altri fattori citati: sentiment, momentum, size, value.

Tutti soffrono delle stesse sfide statistiche (loading non-stazionari).

### Metriche fondamentali correlate

- **WACC (costo medio ponderato del capitale):** un tasso di sconto `r` più basso → valutazioni più alte.
- **Debt/EBITDA:** misura della leva finanziaria.

### Costruzione di portafoglio goal-driven

L'obiettivo non è "battere il mercato" ma **targettizzare le esposizioni ai fattori di rischio prezzati** (mercato, settori, altri) coerenti con gli obiettivi di investimento, bilanciando crescita desiderata e rischio accettabile.

## Regole operative

- Non confondere sovraperformance con alpha: prima di attribuirti skill, regredisci i rendimenti sul mercato e verifica che l'**intercetta sia significativa**.
- Diversifica su firm e settore per neutralizzare il rischio diversificabile, ma **non aspettarti che la diversificazione tenga nelle crisi** (le correlazioni convergono a 1).
- Tratta beta ed esposizioni fattoriali come **grandezze dinamiche**: monitora e ribilancia, non assumerle stabili.
- Definisci obiettivi chiari di rischio/rendimento e costruisci targettizzando esposizioni fattoriali, non rincorrendo il benchmark.
- Un beta > 1 va messo in conto come drawdown più severi nei ribassi, non come "edge".

## Collegamenti

- Repo: [`../../strategies/stock_selector/`](../../strategies/stock_selector/) — lo scoring fondamentale + RRG applica questa logica di fattori e decomposizione del rischio.
- [[06_stock_selection]] — selezione titoli a valle della logica fattoriale.
- [[03_regimi_macro]] — il rischio di mercato (sistematico) dipende dal regime; correlazioni e beta cambiano con il regime.

## Fonti

- `_sorgenti/quantportfolio managernotes.txt` (~righe 1-152) — note da video "Quant Portfolio Manager" (materiali Quant Guild / quantguild.com). La parte successiva del file (gamma exposure / Argo) non è inclusa in questo documento.
