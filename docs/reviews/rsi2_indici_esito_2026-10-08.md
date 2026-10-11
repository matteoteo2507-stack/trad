# RSI(2) sugli indici USA (candidato A) — esito del test pre-registrato (2026-10-08)

Pre-registrazione: [MR_INDICI_RSI2_PREREGISTRATION.md](../MR_INDICI_RSI2_PREREGISTRATION.md), approvata da Matteo il
08/10 e committata con trial e apertura **prima** dell'esecuzione (commit `13f7edd`; era `8b5f726` prima della riscrittura dell'11/10 che ha tolto dati sensibili dai commit locali; date e contenuto del test invariati). Esecuzione unica, semi fissi
(42/43). Output integrale: [esiti/mr_indici_rsi2_2026-10-08.txt](esiti/mr_indici_rsi2_2026-10-08.txt).
Revisione G2: [rsi2_indici_G2_2026-10-08.md](rsi2_indici_G2_2026-10-08.md) (CORREGGI la lettura, 0 bloccanti sul
verdetto). Tutti i numeri qui sotto vengono da quell'output, misurati il 08/10.

## 1. Verdetto

**NON DIMOSTRATO (MDE del divario 0,446%).** Famiglia `mr_indici_rsi2` **CLOSED per potenza, non refutata**, come
previsto dal §8 (CLOSED o NON DIMOSTRATO chiudono la famiglia, nessun round di rifinitura).

| esito (§6) | condizione | misurato | scatta? |
|---|---|---|---|
| NESSUN VERDETTO | dati o matching ROTTO, o > 5% di eventi senza controlli | dati a posto con riserva; matching a posto; 0 su 233 senza controlli | no |
| LEAD | limite basso attesa netta > 0 | +0,152 | si' |
| | limite basso del divario > B_NULL 0,09 | **−0,009** | **no** |
| | attesa netta con costi 3x > 0 | +0,263 | si' |
| | divario puntuale > 0 su entrambi gli indici | SPX +0,282, NAS +0,331 | si' |
| CLOSED (etichetta) | limite alto del divario < 0,50 | **0,615** | no |

Il primario: **divario reale − casuale a durata copiata, netto, +0,307% a trade, IC95 [−0,009; +0,615]**, 233 trade
in 142 episodi. L'esito regge all'errore dell'intervallo: per un LEAD l'intervallo avrebbe dovuto essere piu' stretto
del 31%, per un CLOSED del 37%; se il bootstrap per episodio e' ottimista, l'intervallo vero e' piu' largo e l'esito
non cambia (G2 §2).

## 2. Cosa il test poteva vedere

- Errore standard del divario **0,159%**. Il test aveva l'80% di probabilita' di vedere contro zero un eccesso di
  0,45%, circa il 50% con un eccesso di 0,31%. Per il LEAD (limite basso sopra B_NULL) l'80% si raggiungeva solo con un
  eccesso vero di **~0,54%**.
- La stima puntuale contiene la distorsione del nullo (+0,05/+0,06%, §6): corretta, l'eccesso stimato e'
  **~+0,24/+0,26%** a trade. Non e' "a un soffio dalla significativita'": la soglia era B_NULL, non zero.
- Cosa si puo' dire: un eccesso sul caso sopra ~0,62% a trade e' poco plausibile; uno fra 0 e ~0,6% resta aperto.

## 3. Le fonti pubblicate (tabella di esclusione, §6)

| fonte | pubblicato | nel loro metro (lordo assoluto [+0,258; +0,859]) | tradotto (divario lordo [−0,010; +0,615]) |
|---|---|---|---|
| Murtazin 2000-2026 | 0,51% | non escluso | 0,39% e 0,27% (crescita x1, x2): non escluso |
| Quantitativo 1999-2024 | 0,60% | non escluso | non traducibile |
| BacktestEverything 2000-2024 | 0,75% | non escluso | non traducibile |
| QuantifiedStrategies 1993-2026 (SMA200, uscita RSI > 80) | 0,95% | ESCLUSO, al margine | non traducibile |

- **Nessuna fonte e' confermata.** Il nostro lordo assoluto e' compatibile con tre fonti su quattro, ma il lordo
  assoluto contiene la crescita del mercato: confermarle richiede il divario, che non e' dimostrato.
- **QuantifiedStrategies: escluso al margine (0,09 punti) lo 0,95% di una variante con uscita piu' lunga.** Non e' una
  smentita di QuantifiedStrategies sulla regola testata. La loro uscita a RSI > 80 tiene piu' a lungo e incassa piu'
  crescita, i loro numeri sono su SPY (dividendi inclusi) e non e' detto se siano netti: tutto spinge verso
  l'esclusione, oltre alla direzione dichiarata nel §6 (periodo e costi). Correzione G2 §3b.

## 4. Numeri contro zero: non sono un vantaggio della regola

Attesa netta **+0,462% [+0,152; +0,764]**, lorda +0,561%; win rate 80% (SPX) e 78% (NAS); 11 anni positivi su 15;
Sharpe per trade 0,243 sopra il pavimento di futilita' 0,138; PSR sugli episodi 0,990; +0,105% per giorno in mercato.
**Tutti misurati contro zero**, quindi contengono la crescita degli indici: il casuale a durata copiata fa +0,155% a
trade e +0,035% per giorno. Nessuno si cita come vantaggio (voce **M1** del registro dei bias: "funziona" richiede la
misura contro il baseline, e quella misura e' il divario). Il rapporto per giorno (0,105 contro 0,035) e' lo stesso
divario in un'altra unita', senza intervallo: non e' evidenza in piu'.

## 5. Letture corrette dalla revisione G2

- **Runs test** (z −3,87, "esiti raggruppati"): gira sui **trade**, e 91 trade su 233 sono coppie SPX/NAS dello stesso
  episodio con esiti quasi uguali. Su 142 episodi **indipendenti** con coppie correlate a 0,8-0,9 lo z mediano e'
  −3,3/−4,1 (controllo negativo, coppie indipendenti: +0,03). Il test vede le coppie, **non** dice nulla sulla
  dipendenza fra episodi: non e' evidenza ne' contro ne' a favore del bootstrap per episodio.
- **Doppio binario, capitale proprio: non interpretabile.** `confronta_overlay` riceve i trade dei due indici in
  ordine di uscita e `moltiplicatori` (`core/sizing.py`) fissa la size di un trade con l'esito del precedente: per i
  trade sovrapposti il precedente era ancora aperto all'ingresso (**look-ahead di informazione** nell'overlay). Su
  sequenze sintetiche senza dipendenza sfruttabile e con la stessa struttura di episodi: falsi AGGIUNGE di O3 nel 36%,
  di O1 nel 27% (atteso ~2,5%). L'AGGIUNGE di O3 sui dati veri **non si cita, nemmeno come ipotesi per un forward**.
  Il difetto e' mio nella pre-registrazione e del gatekeeper nelle passate G1.
- **Doppio binario, prop FTMO: i numeri non si citano.** Il §7 prevedeva un pass rate vicino a zero ed e' uscito ~0,23:
  la simulazione non modella cio' che si pensava (rischio in unita' di ATR senza stop, MAE caricata solo nel giorno
  d'uscita, orizzonte di 250 giorni contro una firm senza limite di tempo, regole `citato_senza_url`).
- **Frequenza**: ~17 trade l'anno in totale (~8,5 per indice), ~10 episodi l'anno, su ~13,8 anni utili (SMA200 valida
  da fine 2012). La riga "~14 trade l'anno" stampata dallo script e' imprecisa; lo script approvato non si tocca.

## 6. Dati ed esecuzione

- File letti (non in git, data di modifica 14/08), SHA-256:
  - `analysis/trading-bot-eval/data/dukascopy_d1/SPX500_D1.csv`: `20c8417575f758e6adb1e4ec244f6ec7a7c360e3ecabdafb2248bac3ce952824`
  - `analysis/trading-bot-eval/data/dukascopy_d1/NAS100_D1.csv`: `f515dda2c0faed52d36ad73e75064d75b35915ae413f600753bb358710e62aeb`
- Riserva barre/anno (257-358): nei file ci sono barre del sabato (riempitivi a range 0 del 2012-2014) e della
  domenica sera; scartate, non tolgono giorni feriali (G2 §1).
- Fill non ottenibili 0 su 233 per costruzione (ingresso e uscita a mercato all'apertura successiva, nessuno stop).
- Contabilita': trial 1, cumulato 1 su budget 1, fuori campione aperto il 2026-10-08, quota esterne 2026-Q4 2 di 2-3.

## 7. Cosa servirebbe per riaprire

**Solo evidenza esterna nuova** (`STRATEGY_LIFECYCLE.md` §7), sempre con una nuova pre-registrazione: per esempio un
eccesso pubblicato e verificabile **contro un ingresso casuale a durata copiata**, su dati indipendenti da questi.
Un altro backtest contro zero non basta: misura la crescita del mercato.

**Il forward su questi due indici non e' una strada praticabile.** Con la stessa varianza e frequenza, MDE ≈ 0,446% ×
√(13,8 / anni): ~1,66% in 1 anno, ~0,96% in 3, ~0,74% in 5, ~0,53% in 10. Per un MDE pari agli effetti in gioco
servirebbero ~18 anni (0,39%, Murtazin tradotto) o ~29 (0,31%, la stima puntuale). Stima grossolana.

## 8. Debito di protocollo emerso (G2)

1. `confronta_overlay` accetta trade sovrapposti senza controllo: servono ingresso e uscita per trade, o un blocco.
2. Ne' il protocollo ne' la checklist del gatekeeper dicono su quale unita' gira il runs test: va fatto sull'unita'
   usata per l'intervallo (qui l'episodio).
3. La tassonomia del §5 di `STRATEGY_LIFECYCLE.md` non ha NON DIMOSTRATO, e il contatore non distingue CLOSED per
   potenza da CLOSED refutata: oggi due famiglie (Gump, questa) dipendono solo dal testo libero del verdetto.
4. I dati D1 non sono in git: gli hash stanno qui.
5. `check_matching` etichetta l'ATR al segnale come "ESITO" ma e' noto prima dell'ingresso: solo un'etichetta.
